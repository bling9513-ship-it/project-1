#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기술·트렌드 수집 & 분석 크롤러 (Infosec Archive)

수집 소스
  [논문·모델] Hugging Face Daily Papers : https://huggingface.co/api/daily_papers
  [논문·모델] arXiv (cs.AI / cs.CL / cs.CR) : http://export.arxiv.org/api/query
  [논문·모델] arXiv cs.CR AI보안 전용 쿼리 (프롬프트 인젝션·탈옥·에이전트 보안·딥페이크 등)
  [커뮤니티]  Hacker News (Algolia) 일반 AI + 보안 키워드 전용 검색
  [커뮤니티]  Hacker News Show HN (tags=show_hn) — AI/LLM/에이전트/CLI 개발자 툴
  [커뮤니티]  GeekNews : https://news.hada.io/rss/news
  [도구]      GitHub Search API — AI/LLM/에이전트/MCP/AI보안 오픈소스 저장소
  [보안 뉴스] The Hacker News · Dark Reading · Embrace the Red · Simon Willison RSS

카테고리 (5종)
  LLM·에이전트 / AI 보안·안전 / AI 툴·서비스 / 모델·논문 / 산업·트렌드

수집 균형
  보안 전용 수집분(track=security)과 도구 수집분(track=tool)에 최소 쿼터를 두고,
  나머지는 출처 라운드 로빈으로 채워 특정 카테고리가 비지 않도록 한다.

분석
  - EXAONE API (k-exaone_v2.5) 배치 4건, 호출 간 1.8초 대기, 429/5xx 지수 백오프(Retry-After 반영) 재시도
  - ai_tech_cache.json 캐싱 (성공한 분석만 캐시 → 재실행 시 API 호출 절감)
  - API 한도/오류 시 원문 기반 정제 폴백 (빈 항목 없음)

산출물
  - archive.db 의 ai_insights 테이블 UPSERT
  - ai_data.json (프론트엔드/외부 연동용)

보안: EXAONE_API_KEY / GITHUB_TOKEN 은 .env(로컬) 또는 환경변수에서만 읽으며, 로그/DB/JSON/Git 어디에도 기록하지 않는다.
"""
import os
import re
import json
import time
import html
import hashlib
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "ai_tech_cache.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")
AI_DATA_JSON = os.path.join(BASE_DIR, "ai_data.json")
RUN_ITEMS_FILE = os.path.join(BASE_DIR, "ai_run_items.json")
SEC_RUN_FILE = os.path.join(BASE_DIR, "ai_sec_run_items.json")
SEC_MANUAL_FILE = os.path.join(BASE_DIR, "ai_sec_manual.json")

KST = timezone(timedelta(hours=9))

# 'AI 보안 툴'을 맨 앞에 두어 GitHub AI 보안 오픈소스 도구만 따로 모아볼 수 있게 한다.
CATEGORIES = ["AI 보안 툴", "AI 보안·안전", "AI 툴·서비스", "LLM·에이전트", "모델·논문", "산업·트렌드"]
AI_SEC_TOOL_CAT = "AI 보안 툴"

# 옛 카테고리 → 새 카테고리 (캐시·DB 마이그레이션용)
CATEGORY_ALIASES = {
    "개발·오픈소스": "AI 툴·서비스",
    "개발 오픈소스": "AI 툴·서비스",
    "AI 툴·오픈소스": "AI 툴·서비스",
    "AI 툴": "AI 툴·서비스",
    "보안·안전": "AI 보안·안전",
    "AI보안": "AI 보안·안전",
    "AI 보안 도구": "AI 보안 툴",
    "AI 보안툴": "AI 보안 툴",
    "AI 보안 오픈소스": "AI 보안 툴",
}

SOURCES = ["Hugging Face", "arXiv", "Hacker News", "Show HN", "GitHub", "GeekNews",
           "The Hacker News", "Dark Reading", "Embrace the Red", "Simon Willison"]

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 수집 목표치 (중복 제거 후 최소 25건 이상 보장)
TARGET_TOTAL = 60
# 보안·도구 최소 쿼터 (수집 가능한 만큼만 채움)
SEC_TARGET = 14
TOOL_TARGET = 16

# ---------------------------------------------------------------------------
# 공통 유틸
# ---------------------------------------------------------------------------

def now_kst():
    return datetime.now(KST)


def fetch_bytes(url, timeout=25, tries=3, headers=None):
    """원자료 수집 공통 요청 (지수 백오프 3회 재시도)"""
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    last_err = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < tries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"요청 실패 {url}: {last_err}")


def clean_text(text, limit=None):
    if not text:
        return ""
    text = html.unescape(str(text))
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def norm_title(title):
    t = clean_text(title).lower()
    t = re.sub(r"[\W_]+", "", t, flags=re.UNICODE)
    return t


def norm_url(url):
    """URL 정규화: 앵커·추적 파라미터만 제거하고 id 등 식별 쿼리는 유지"""
    u = (url or "").strip().lower()
    u = re.sub(r"#.*$", "", u)
    u = re.sub(r"[?&](utm_[^&=]+|ref|fbclid|gclid)=[^&]*", "", u)
    u = re.sub(r"[?&]+", "?", u).rstrip("?&")
    return u.rstrip("/")


def item_key(src, title, url):
    base = norm_title(title) or (url or "")
    return hashlib.sha1(f"{src}|{base}".encode("utf-8")).hexdigest()[:16]


def parse_date(value):
    """다양한 표기의 날짜를 YYYY-MM-DD 로 정규화"""
    if not value:
        return ""
    v = str(value).strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", v)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


# ---------------------------------------------------------------------------
# 1) 수집기
# ---------------------------------------------------------------------------

AI_TITLE_PATTERNS = re.compile(
    r"(\bai\b|a\.i\.|llm|large language|gpt|claude|gemini|llama|mistral|qwen|deepseek|"
    r"transformer|diffusion|neural|machine learning|deep learning|agent|agentic|rag\b|"
    r"embedding|inference|fine-?tun|openai|anthropic|hugging ?face|multimodal|"
    r"prompt|model|chatbot|copilot|mcp\b|reasoning|benchmark)",
    re.I,
)

AI_KO_PATTERNS = re.compile(
    r"(인공지능|\bAI\b|에이전트|LLM|GPT|챗봇|모델|머신러닝|딥러닝|프롬프트|RAG|"
    r"보안|취약점|해킹|악성|공격|방어|오픈소스|추론|학습|데이터셋|파운데이션|"
    r"프라이버시|개인정보|유출|노출|침해|양자화|GPU|반도체|클라우드|거버넌스|규제)",
    re.I,
)

# HN 단순 장애 공지성 글 제외
HN_EXCLUDE = re.compile(r"(elevated (errors|latency)|status\.\w+\.(com|ai)|is down\b)", re.I)


def collect_huggingface(limit=16):
    out = []
    try:
        data = json.loads(fetch_bytes("https://huggingface.co/api/daily_papers", timeout=30).decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"  [HF] 수집 실패: {e}")
        return out

    for item in data[:limit]:
        p = item.get("paper") or {}
        pid = p.get("id") or ""
        title = clean_text(item.get("title") or p.get("title"))
        if not title:
            continue
        refs = p.get("ai_keywords") or []
        out.append({
            "source": "Hugging Face",
            "title_orig": title,
            "url": f"https://huggingface.co/papers/{pid}" if pid else "https://huggingface.co/papers",
            "summary_orig": clean_text(item.get("summary") or p.get("summary") or "", 1200),
            "published_at": parse_date(p.get("submittedOnDailyAt") or p.get("publishedAt") or item.get("publishedAt")),
            "score": int(p.get("upvotes") or 0),
            "source_hint": ", ".join(refs[:6]) if isinstance(refs, list) else "",
        })
    print(f"  [HF] {len(out)}건 수집")
    return out


ARXIV_ATOM = "{http://www.w3.org/2005/Atom}"


def collect_arxiv(categories=("cs.AI", "cs.CL", "cs.CR"), per_cat=6):
    out = []
    for cat in categories:
        time.sleep(3.2)  # arXiv API 예절 (요청 간 3초)
        url = ("http://export.arxiv.org/api/query?"
               + urllib.parse.urlencode({
                   "search_query": f"cat:{cat}",
                   "sortBy": "submittedDate",
                   "sortOrder": "descending",
                   "max_results": per_cat * 3,
               }))
        try:
            raw = fetch_bytes(url, timeout=30).decode("utf-8", errors="ignore")
            root = ET.fromstring(raw)
        except Exception as e:  # noqa: BLE001
            print(f"  [arXiv:{cat}] 수집 실패: {e}")
            continue

        added = 0
        for entry in root.findall(f"{ARXIV_ATOM}entry"):
            if added >= per_cat:
                break
            title = clean_text(entry.findtext(f"{ARXIV_ATOM}title"))
            summary = clean_text(entry.findtext(f"{ARXIV_ATOM}summary"), 1200)
            link = clean_text(entry.findtext(f"{ARXIV_ATOM}id"))
            published = parse_date(entry.findtext(f"{ARXIV_ATOM}published"))
            if not title or not link:
                continue
            # cs.CR 은 AI/보안 교차 주제만 (페이지 성격 유지)
            blob = f"{title} {summary}"
            if cat == "cs.CR" and not re.search(
                    r"(\bai\b|llm|language model|neural|machine learning|deep learning|agent|"
                    r"adversarial|prompt|model|attack|jailbreak|malware|privacy)", blob, re.I):
                continue
            out.append({
                "source": "arXiv",
                "title_orig": title,
                "url": link.replace("http://", "https://"),
                "summary_orig": summary,
                "published_at": published,
                "score": 0,
                "source_hint": cat,
            })
            added += 1
        print(f"  [arXiv:{cat}] {added}건 수집")
    return out


def collect_hackernews(queries=("AI", "LLM", "OpenAI", "AI agent"), per_query=15, days=7, min_points=25):
    import time as _t
    since = int(_t.time()) - days * 86400
    seen = {}
    for q in queries:
        url = ("https://hn.algolia.com/api/v1/search?"
               + urllib.parse.urlencode({
                   "query": q,
                   "tags": "story",
                   "numericFilters": f"created_at_i>{since},points>{min_points}",
                   "hitsPerPage": per_query,
               }))
        try:
            data = json.loads(fetch_bytes(url, timeout=25).decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  [HN:{q}] 수집 실패: {e}")
            continue
        for hit in data.get("hits", []):
            title = clean_text(hit.get("title"))
            oid = hit.get("objectID")
            if not title or not oid:
                continue
            if not AI_TITLE_PATTERNS.search(title) or HN_EXCLUDE.search(title):
                continue
            link = hit.get("url") or f"https://news.ycombinator.com/item?id={oid}"
            seen[oid] = {
                "source": "Hacker News",
                "title_orig": title,
                "url": link,
                "summary_orig": clean_text(hit.get("story_text") or "", 900),
                "published_at": parse_date(hit.get("created_at")),
                "score": int(hit.get("points") or 0),
                "source_hint": f"HN {hit.get('points')}점 · 댓글 {hit.get('num_comments') or 0}",
            }
    out = sorted(seen.values(), key=lambda x: -x["score"])[:14]
    print(f"  [HN] {len(out)}건 수집")
    return out


def collect_geeknews(limit=10):
    out = []
    try:
        raw = fetch_bytes("https://news.hada.io/rss/news", timeout=25).decode("utf-8", errors="ignore")
        root = ET.fromstring(raw)
    except Exception as e:  # noqa: BLE001
        print(f"  [GeekNews] 수집 실패: {e}")
        return out

    for entry in root.findall(f"{ARXIV_ATOM}entry"):
        if len(out) >= limit:
            break
        title = clean_text(entry.findtext(f"{ARXIV_ATOM}title"))
        summary = clean_text(entry.findtext(f"{ARXIV_ATOM}content"), 1200)
        link_el = entry.find(f"{ARXIV_ATOM}link")
        link = (link_el.get("href") if link_el is not None else entry.findtext(f"{ARXIV_ATOM}id")) or ""
        published = parse_date(entry.findtext(f"{ARXIV_ATOM}published") or entry.findtext(f"{ARXIV_ATOM}updated"))
        if not title or not link:
            continue
        if not AI_KO_PATTERNS.search(title):
            continue
        out.append({
            "source": "GeekNews",
            "title_orig": title,
            "url": link,
            "summary_orig": summary,
            "published_at": published,
            "score": 0,
            "source_hint": "GeekNews",
        })
    print(f"  [GeekNews] {len(out)}건 수집")
    return out


# ---------------------------------------------------------------------------
# 1-b) AI 보안·AI 툴 전용 수집
# ---------------------------------------------------------------------------

# AI 계열 신호 (제목·요약 어디든)
AI_TERMS = re.compile(
    r"(\bai\b|a\.i\.|\bllm\b|large language|gpt|claude|gemini|llama|qwen|mistral|deepseek|"
    r"agent|agentic|\bmcp\b|model|prompt|chatbot|copilot|openai|anthropic|hugging ?face|"
    r"machine learning|deep learning|neural|multimodal|\brag\b|embedding|inference|fine-?tun)",
    re.I,
)

# 보안·안전 신호 (뉴스·블로그 제목/요약 기준)
SEC_TERMS = re.compile(
    r"(security|안보|보안|vulnerab|취약|exploit|공격|attack|breach|유출|leak|jailbreak|탈옥|"
    r"prompt injection|프롬프트 인젝션|red.?team|malware|악성|phishing|피싱|threat|위협|"
    r"privacy|프라이버시|개인정보|\bcve\b|zero.?day|sandbox|exfiltrat|유출|adversarial|poison|"
    r"backdoor|백도어|supply chain|공급망|deepfake|딥페이크|safeguard|safety|안전|"
    r"cyber|hack|spy|espionage|ransomware|trojan|botnet|\brat\b|scam|harm|misuse|risk|"
    r"hijack|bypass|theft|steal|abuse|escap|injection|tamper|guardrail|alignment)",
    re.I,
)

# AI 핵심 신호 (논문 제목 기준 — 'model' 같은 일반어 제외)
AI_STRONG = re.compile(
    r"(\bai\b|a\.i\.|\bllm|large language|language model|gpt|chatgpt|claude|gemini|grok|llama|"
    r"qwen|mistral|deepseek|agent|agentic|\bmcp\b|prompt|chatbot|copilot|openai|anthropic|"
    r"deepfake|generative|machine learning|neural|multimodal|\brag\b|fine-?tun|distillation)",
    re.I,
)

# AI 보안 핵심 주제 (논문·뉴스의 본문 근거)
AI_SEC_TOPIC = re.compile(
    r"(prompt injection|jailbreak|backdoor|poison|adversarial|model (stealing|extraction|inversion)|"
    r"membership inference|deepfake|watermark|guardrail|alignment|red.?team|agent security|"
    r"tool.?use|\bmcp\b|data (leak|exfiltrat)|privacy|side.?channel|supply chain|"
    r"malicious (prompt|skill|extension|package)|promptware|ai (security|safety|risk)|llm (security|safety))",
    re.I,
)

# 툴·서비스 신호
TOOL_TERMS = re.compile(
    r"(open.?source|오픈소스|\bsdk\b|\bcli\b|library|라이브러리|framework|프레임워크|toolkit|"
    r"\btool\b|도구|\bapp\b|서비스|platform|플랫폼|extension|plugin|self.?host|\brepo\b|"
    r"\bapi\b|server|agent framework|workflow|\bapp\b)",
    re.I,
)

AWS_ATOM = "{http://www.w3.org/2005/Atom}"

# AI 보안 RSS 피드 (BleepingComputer는 Cloudflare 403 으로 제외)
#  - ai_in_title: 제목에 AI 신호를 요구 (범용 보안 매체 → 오탐 방지)
#  - require_sec: 보안 어휘 요구 (AI 보안 전문 블로그는 끌 수 있음)
SECURITY_FEEDS = [
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews",
     "limit": 8, "days": 30, "ai_in_title": True, "require_sec": True, "sec_in_title": True},
    {"name": "Dark Reading", "url": "https://www.darkreading.com/rss.xml",
     "limit": 7, "days": 30, "ai_in_title": True, "require_sec": True, "sec_in_title": False},
    {"name": "Embrace the Red", "url": "https://embracethered.com/blog/index.xml",
     "limit": 6, "days": 60, "ai_in_title": False, "require_sec": False, "sec_in_title": False},
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/",
     "limit": 5, "days": 21, "ai_in_title": True, "require_sec": True, "sec_in_title": True},
]

FEED_PROMO = re.compile(r"(webinar|sponsored|register (now|today)|white ?paper|threatsday|podcast|\[free\])", re.I)


def parse_feed_entries(raw):
    """RSS 2.0 / Atom 피드를 공통 형식으로 파싱"""
    from email.utils import parsedate_to_datetime
    root = ET.fromstring(raw)
    out = []
    for node in root.iter():
        if not (node.tag.endswith("item") or node.tag.endswith("entry")):
            continue
        title = ""
        link = ""
        summary = ""
        published = ""
        for child in list(node):
            tag = child.tag.split("}")[-1]
            if tag == "title" and not title:
                title = clean_text(child.text or "")
            elif tag == "link":
                href = child.get("href")
                if href and (child.get("rel") in (None, "alternate")) and not link:
                    link = href.strip()
                elif (not href) and (child.text or "").strip() and not link:
                    link = child.text.strip()
            elif tag in ("description", "summary", "content") and not summary:
                summary = clean_text(child.text or "")
            elif tag in ("pubDate", "published", "updated", "date") and not published:
                published = (child.text or "").strip()
        if not title or not link:
            continue
        date_str = ""
        if published:
            try:
                date_str = parsedate_to_datetime(published).astimezone(timezone.utc).strftime("%Y-%m-%d")
            except Exception:  # noqa: BLE001
                date_str = parse_date(published)
        out.append({"title": title, "url": link, "summary": summary, "published_at": date_str})
    return out


def _recent_enough(date_str, days):
    if not date_str:
        return True
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    return (now_kst().astimezone(timezone.utc) - d).days <= days


def collect_security_feeds():
    """AI 보안 전문 뉴스·블로그 RSS 에서 AI 보안 기사만 필터링 수집"""
    out = []
    for feed in SECURITY_FEEDS:
        name, url = feed["name"], feed["url"]
        try:
            raw = fetch_bytes(url, timeout=30).decode("utf-8", errors="ignore")
            entries = parse_feed_entries(raw)
        except Exception as e:  # noqa: BLE001
            print(f"  [{name}] 수집 실패: {type(e).__name__}: {e}")
            continue
        added = 0
        for en in entries:
            if added >= feed["limit"]:
                break
            title = en["title"]
            blob = f"{title} {en['summary']}"
            if FEED_PROMO.search(title):
                continue
            if not AI_STRONG.search(blob):
                continue
            if feed["ai_in_title"] and not AI_STRONG.search(title):
                continue
            if feed["require_sec"] and not SEC_TERMS.search(blob):
                continue
            if feed.get("sec_in_title") and not SEC_TERMS.search(title):
                continue
            if not _recent_enough(en["published_at"], feed["days"]):
                continue
            out.append({
                "source": name,
                "title_orig": title,
                "url": en["url"],
                "summary_orig": clean_text(en["summary"], 1200),
                "published_at": en["published_at"],
                "score": 0,
                "source_hint": name,
                "track": "security",
            })
            added += 1
        print(f"  [{name}] {added}건 수집 (AI 보안 필터)")
    return out


ARXIV_SEC_QUERIES = (
    'cat:cs.CR AND (all:"prompt injection" OR all:"LLM" OR all:"language model" OR all:"jailbreak")',
    'cat:cs.CR AND (all:"agent" OR all:"MCP" OR all:"tool call" OR all:"AI agent")',
    'cat:cs.CR AND (all:"deepfake" OR all:"watermark" OR all:"adversarial" OR all:"AI safety")',
)


def collect_arxiv_security(per_query=4):
    """arXiv cs.CR 에서 AI/LLM 보안 주제 논문만 집중 수집"""
    out = []
    seen = set()
    for i, sq in enumerate(ARXIV_SEC_QUERIES):
        if i:
            time.sleep(3.2)  # arXiv API 예절 (요청 간 3초)
        url = ("http://export.arxiv.org/api/query?"
               + urllib.parse.urlencode({
                   "search_query": sq,
                   "sortBy": "submittedDate",
                   "sortOrder": "descending",
                   "max_results": per_query * 4,
               }))
        try:
            raw = fetch_bytes(url, timeout=40).decode("utf-8", errors="ignore")
            root = ET.fromstring(raw)
        except Exception as e:  # noqa: BLE001
            print(f"  [arXiv:sec{i + 1}] 수집 실패: {e}")
            continue
        added = 0
        for entry in root.findall(f"{ARXIV_ATOM}entry"):
            if added >= per_query:
                break
            title = clean_text(entry.findtext(f"{ARXIV_ATOM}title"))
            summary = clean_text(entry.findtext(f"{ARXIV_ATOM}summary"), 1200)
            link = clean_text(entry.findtext(f"{ARXIV_ATOM}id"))
            if not title or not link or link in seen:
                continue
            blob = f"{title} {summary}"
            # 제목에 AI 신호가 있고, 제목·초록에 AI 보안 주제 또는 보안 어휘가 있을 때만
            if not AI_STRONG.search(title):
                continue
            if not (SEC_TERMS.search(title) or AI_SEC_TOPIC.search(blob)):
                continue
            seen.add(link)
            out.append({
                "source": "arXiv",
                "title_orig": title,
                "url": link.replace("http://", "https://"),
                "summary_orig": summary,
                "published_at": parse_date(entry.findtext(f"{ARXIV_ATOM}published")),
                "score": 0,
                "source_hint": "cs.CR · AI 보안",
                "track": "security",
            })
            added += 1
        print(f"  [arXiv:sec{i + 1}] {added}건 수집")
    return out


HN_SEC_QUERIES = ('"prompt injection"', '"AI security"', 'AI agent security',
                  'jailbreak LLM', 'deepfake', '"AI safety"', 'MCP server security')


def collect_hackernews_security(per_query=12, days=21, min_points=3):
    """Hacker News 보안 키워드 전용 검색 (AI 보안 담론)"""
    since = int(time.time()) - days * 86400
    seen = {}
    for q in HN_SEC_QUERIES:
        url = ("https://hn.algolia.com/api/v1/search?"
               + urllib.parse.urlencode({
                   "query": q,
                   "tags": "story",
                   "numericFilters": f"created_at_i>{since},points>{min_points}",
                   "hitsPerPage": per_query,
               }))
        try:
            data = json.loads(fetch_bytes(url, timeout=25).decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  [HN-sec:{q}] 수집 실패: {e}")
            continue
        for hit in data.get("hits", []):
            title = clean_text(hit.get("title"))
            oid = hit.get("objectID")
            if not title or not oid or oid in seen:
                continue
            if re.match(r"^(Show|Launch) HN\b", title):  # 도구·서비스 런칭은 보안 트랙에서 제외
                continue
            blob = f"{title} {hit.get('story_text') or ''}"
            if not AI_STRONG.search(title) or not SEC_TERMS.search(blob):
                continue
            if HN_EXCLUDE.search(title):
                continue
            link = hit.get("url") or f"https://news.ycombinator.com/item?id={oid}"
            seen[oid] = {
                "source": "Hacker News",
                "title_orig": title,
                "url": link,
                "summary_orig": clean_text(hit.get("story_text") or "", 900),
                "published_at": parse_date(hit.get("created_at")),
                "score": int(hit.get("points") or 0),
                "source_hint": f"HN {hit.get('points')}점 · 댓글 {hit.get('num_comments') or 0}",
                "track": "security",
            }
        time.sleep(0.4)
    out = sorted(seen.values(), key=lambda x: (-x["score"], x.get("published_at") or ""))[:10]
    print(f"  [HN-sec] {len(out)}건 수집")
    return out


SHOW_HN_QUERIES = ("AI", "LLM", "agent", "MCP", "coding agent", "local model", "RAG", "CLI AI")


def collect_show_hn(per_query=20, days=21, min_points=2):
    """Hacker News Show HN — 최신 AI/LLM/에이전트/개발자 툴 수집"""
    since = int(time.time()) - days * 86400
    seen = {}
    for q in SHOW_HN_QUERIES:
        url = ("https://hn.algolia.com/api/v1/search?"
               + urllib.parse.urlencode({
                   "query": q,
                   "tags": "show_hn",
                   "numericFilters": f"created_at_i>{since},points>{min_points}",
                   "hitsPerPage": per_query,
               }))
        try:
            data = json.loads(fetch_bytes(url, timeout=25).decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  [ShowHN:{q}] 수집 실패: {e}")
            continue
        for hit in data.get("hits", []):
            title = clean_text(hit.get("title"))
            oid = hit.get("objectID")
            if not title or not oid or oid in seen:
                continue
            blob = f"{title} {hit.get('story_text') or ''}"
            if not AI_TITLE_PATTERNS.search(title) or HN_EXCLUDE.search(title):
                continue
            link = hit.get("url") or f"https://news.ycombinator.com/item?id={oid}"
            seen[oid] = {
                "source": "Show HN",
                "title_orig": title,
                "url": link,
                "summary_orig": clean_text(hit.get("story_text") or "", 900),
                "published_at": parse_date(hit.get("created_at")),
                "score": int(hit.get("points") or 0),
                "source_hint": f"Show HN {hit.get('points')}점 · 댓글 {hit.get('num_comments') or 0}",
                "track": "tool",
            }
        time.sleep(0.4)
    # 같은 프로젝트가 여러 쿼리로 중복 등장하므로 점수·최신순 정렬 후 상한
    out = sorted(seen.values(), key=lambda x: (x.get("published_at") or "", -x["score"]), reverse=True)[:12]
    print(f"  [ShowHN] {len(out)}건 수집")
    return out


def get_github_token():
    """선택적 GitHub 토큰 (.env 또는 GITHUB_TOKEN 환경변수). 없으면 익명 호출(검색 10회/분).

    ※ GH_TOKEN 은 gh CLI 프록시용 값이라 API 호출에는 쓰지 않는다.
    """
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok.strip()
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GITHUB_TOKEN="):
                        return line.split("=", 1)[1].strip()
        except Exception:  # noqa: BLE001
            return None
    return None


GITHUB_QUERIES = (
    # (쿼리, 정렬 기준)
    ("topic:ai-security stars:>100", "stars"),
    ("prompt injection in:description stars:>50 pushed:>2026-06-01", "stars"),
    ("AI agent in:description stars:>1000 pushed:>2026-10-01", "updated"),
    ("topic:mcp stars:>300 pushed:>2026-10-15", "stars"),
)

# 면접·강의·치트시트 모음처럼 '도구'가 아닌 저장소 제외
GITHUB_DENY = re.compile(r"(面試|面试|interview|leetcode|cheat ?sheet|치트시트)", re.I)

GITHUB_RELEVANT = re.compile(
    r"(ai|llm|agent|mcp|model|prompt|copilot|rag|gpt|claude|inference|embedding|"
    r"security|vulnerab|jailbreak|firewall|scanner|red.?team|guardrail|sandbox|audit)",
    re.I,
)


def collect_github_tools(per_query=5, days=60):
    """GitHub Search API 로 AI/LLM/에이전트/MCP/AI보안 오픈소스 도구 수집"""
    token = get_github_token()
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    out = []
    seen = set()
    for i, (q, sort) in enumerate(GITHUB_QUERIES):
        if i:
            time.sleep(7 if not token else 2.5)  # 익명 검색 10회/분 한도 회피
        url = ("https://api.github.com/search/repositories?"
               + urllib.parse.urlencode({"q": q, "sort": sort, "order": "desc", "per_page": per_query * 3}))
        try:
            data = json.loads(fetch_bytes(url, timeout=30, headers=headers).decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if "Authorization" in headers:  # 토큰이 거부되면 익명으로 1회 재시도
                print(f"  [GitHub:{i + 1}] 토큰 인증 실패({e}) → 익명 요청으로 재시도")
                headers.pop("Authorization", None)
                token = None
                time.sleep(6)
                try:
                    data = json.loads(fetch_bytes(url, timeout=30, headers=headers).decode("utf-8"))
                except Exception as e2:  # noqa: BLE001
                    print(f"  [GitHub:{i + 1}] 수집 실패: {e2}")
                    continue
            else:
                print(f"  [GitHub:{i + 1}] 수집 실패: {e}")
                continue
        added = 0
        for repo in data.get("items", []):
            if added >= per_query:
                break
            full = repo.get("full_name") or ""
            desc = clean_text(repo.get("description") or "")
            if not full or full in seen or len(desc) < 12:
                continue
            if not GITHUB_RELEVANT.search(f"{full} {desc}") or GITHUB_DENY.search(desc):
                continue
            pushed = (repo.get("pushed_at") or "")[:10]
            if pushed and not _recent_enough(pushed, days):
                continue
            topics = repo.get("topics") or []
            stars = int(repo.get("stargazers_count") or 0)
            seen.add(full)
            extra = []
            if repo.get("language"):
                extra.append(f"언어 {repo['language']}")
            extra.append(f"★ {stars:,}")
            if topics:
                extra.append("토픽 " + ", ".join(topics[:6]))
            if repo.get("created_at"):
                extra.append(f"생성 {repo['created_at'][:10]}")
            out.append({
                "source": "GitHub",
                "title_orig": full,
                "url": repo.get("html_url") or f"https://github.com/{full}",
                "summary_orig": clean_text(f"{desc} ({' · '.join(extra)})", 1200),
                "published_at": pushed,
                "score": stars,
                "source_hint": f"GitHub ★{stars:,}",
                # AI 보안 주제 저장소는 보안 트랙으로 보내 AI 보안 카테고리에 갈 수 있게 한다
                "track": "security" if i < 2 else "tool",
            })
            added += 1
        print(f"  [GitHub:{i + 1}] {added}건 수집")
    return out


INTERLEAVE_ORDER = SOURCES

# ---------------------------------------------------------------------------
# AI 보안 오픈소스 툴 전용 수집 (레드팀·가드레일·프롬프트 인젝션·MCP/에이전트 보안)
#
#  · 일반 AI 툴 수집과 분리해 'AI 보안 툴' 카테고리로 모은다.
#  · 목록(awesome-*), 가이드·강의·치트시트, 취약 앱 실습장은 제외하고 실행 가능한 코드만 남긴다.
# ---------------------------------------------------------------------------

SEC_TOOL_QUERIES = (
    ("topic:llm-security stars:>150", "stars"),
    ("topic:ai-security stars:>150", "stars"),
    ("topic:prompt-injection stars:>30", "stars"),
    ("prompt injection detector in:description stars:>20", "stars"),
    ("llm guardrail in:description stars:>150", "stars"),
    ("topic:guardrails guardrail in:description stars:>150", "stars"),
    ("topic:ai-red-teaming stars:>100", "stars"),
    ("llm red team in:description stars:>100", "stars"),
    ("ai pentest in:description stars:>150", "stars"),
    ("topic:mcp-security stars:>100", "stars"),
    ("mcp security in:description stars:>100", "stars"),
    ("agent security in:description stars:>150", "stars"),
    ("llm vulnerability scanner in:description stars:>30", "stars"),
    ("ai firewall in:description stars:>30", "stars"),
    ("topic:llm-safety stars:>150", "stars"),
    ("jailbreak llm in:description stars:>80", "stars"),
)

# 도구가 아닌 저장소(목록·가이드·강의·취약 앱 실습장·프롬프트 모음) 제외
SEC_TOOL_DENY = re.compile(
    r"(awesome|curated|roadmap|tutorial|course|curriculum|cheat ?sheet|interview|leetcode|handbook|"
    r"collection of|knowledge base|everything for|arsenal|papers?\b|newsletter|weekly|digest|"
    r"deliberately vulnerable|vulnerable[-_ ]?(app|application|server|bank|lab)|playground|"
    r"system[ -]prompts?|beginner|syllabus|list of|\bbook\b|dataset|training|\bgame\b|"
    r"뉴스|논문|목록|가이드|강의|모음|레퍼런스|자료실|치트시트|로드맵|인터뷰|공부|강좌|다이제스트)",
    re.I,
)

# AI 보안을 직접 겨냥한 표현 (기존 DB 재분류는 이 신호를 반드시 요구한다)
SEC_TOOL_STRONG = re.compile(
    r"(prompt injection|프롬프트 인젝션|jailbreak|탈옥|guardrail|가드레일|red.?team|레드팀|"
    r"ai security|llm security|agent security|mcp security|ai firewall|agent firewall|"
    r"ai pentest|ai penetration|llm vulnerab|model scann|mlsecops|ai safety|ai 안전|"
    r"security (toolkit|scanner)|vulnerability scanner|ai 보안|llm 보안|에이전트 보안|mcp 보안|"
    r"ai 방화벽|침투 테스트|보안 스캐너|보안 검사 도구|"
    r"(codex|claude|llm|ai|agent)[- ]?(security|guard|safety)|unsafe|adversarial prompt)",
    re.I,
)

# AI 보안 저장소를 가리키는 GitHub 토픽
SEC_TOOL_TOPICS = {
    "ai-security", "ai-security-tools", "ai-security-audit", "llm-security", "llm-security-scanner",
    "security-scanners", "ai-penetration-testing", "ai-pentesting", "ai-red-teaming", "ai-red-team",
    "llm-red-teaming", "ai-cybersecurity", "agent-security", "agentic-ai-security", "agent-security-audit",
    "agent-runtime-security", "mcp-security", "prompt-injection", "prompt-injection-detection",
    "guardrails", "llm-guardrails", "llm-safety", "ai-safety", "redteam", "adversarial-ai", "ai-attacks",
}

# 보안 도구답게 이름이 잡힌 저장소 (Tier B 판별용)
SEC_TOOL_NAME = re.compile(
    r"(guard|scan|secur|shield|sentinel|defend|firewall|red.?team|pentest|jailbreak|"
    r"inject|audit|harden|defen[cs]e|armor|wall|sanitiz|observ)",
    re.I,
)

# 손으로 검증한 대표 AI 보안 툴 (쿼리 결과에서 놓치지 않게 우선 포함)
SEC_TOOL_SEED = {
    "promptfoo/promptfoo", "giskard-ai/giskard-oss", "protectai/llm-guard", "microsoft/pyrit",
    "nvidia/garak", "nvidia-nemo/guardrails", "confident-ai/deepteam", "msoedov/agentic_security",
    "tencent/ai-infra-guard", "usestrix/strix", "keygraphhq/shannon", "openai/codex-security",
    "snyk/agent-scan", "nvidia/skillspector", "superagent-ai/superagent", "stacklok/toolhive",
    "akto-api-security/akto", "archestra-ai/openappa", "nolabs-ai/nono", "hashgraph-online/hol-guard",
    "pipelab-org/pipelock",
}

# 토픽만 보고는 도구로 보기 어려운 저장소 (자동 판별 예외)
SEC_TOOL_BLOCK = {"kingcharleslzy-ai/dsh-purge"}

# 수집 단계 판별: AI 신호 + 보안 신호 + 코드 보유
SEC_TOOL_AI = re.compile(
    r"(\bai\b|a\.i\.|llm|large language|agent|agentic|\bmcp\b|prompt|model|gpt|claude|gemini|"
    r"\brag\b|inference|chatbot|copilot|guardrail|jailbreak|openai|anthropic|codex|\bgen ?ai\b|"
    r"에이전트|모델|프롬프트|챗봇|생성형|인공지능|머신러닝|코딩 에이전트)",
    re.I,
)
SEC_TOOL_SEC = re.compile(
    r"(security|보안|guardrail|firewall|scan|detect|red.?team|jailbreak|injection|safety|attack|"
    r"vulnerab|pentest|penetration|audit|protect|defen[cs]e|shiel|exfiltrat|traversal|leak|"
    r"malicious|threat|adversarial|poison|backdoor|safeguard|misuse|risk|sandbox|harden|"
    r"취약|침투|방어|탐지|스캔|보안|인젝션|탈옥|레드팀|공격|유출|격리|검사|모니터링)",
    re.I,
)


def is_ai_sec_tool_repo(name, desc, topics=(), language=None, size_kb=0, is_fork=False):
    """실제로 실행·활용 가능한 AI 보안 오픈소스 도구인지 판별 (전용 쿼리 수집용)

    검증 시드 > AI 보안 토픽 > (설명의 AI 보안 기능 + 이름의 보안 도구 신호) 순으로 인정한다.
    """
    blob = f"{name} {desc} {' '.join(topics or [])}"
    if SEC_TOOL_DENY.search(blob):
        return False
    if (name or "").lower() in SEC_TOOL_BLOCK:
        return False
    if is_fork or not language or (size_kb or 0) < 300:  # 코드가 거의 없는 저장소 제외
        return False
    if (name or "").lower() in SEC_TOOL_SEED:
        return True
    if {t.lower() for t in (topics or [])} & SEC_TOOL_TOPICS and SEC_TOOL_SEC.search(desc):
        return True
    return bool(SEC_TOOL_STRONG.search(desc) and SEC_TOOL_NAME.search(name))


def _github_search(q, sort, per_page, headers, tag="GitHub"):
    """GitHub Search API 호출 (토큰 거부 시 익명 재시도)"""
    url = ("https://api.github.com/search/repositories?"
           + urllib.parse.urlencode({"q": q, "sort": sort, "order": "desc", "per_page": per_page}))
    try:
        return json.loads(fetch_bytes(url, timeout=30, headers=headers).decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        if "Authorization" in headers:
            print(f"  [{tag}] 토큰 인증 실패({e}) → 익명 요청으로 재시도")
            headers.pop("Authorization", None)
            time.sleep(6)
            try:
                return json.loads(fetch_bytes(url, timeout=30, headers=headers).decode("utf-8"))
            except Exception as e2:  # noqa: BLE001
                print(f"  [{tag}] 수집 실패: {e2}")
                return {}
        print(f"  [{tag}] 수집 실패: {e}")
        return {}


def collect_ai_sec_tools(per_query=3, days=240, max_items=28):
    """AI 보안 오픈소스 툴 전용 수집 (GitHub Search API)"""
    headers = {"Accept": "application/vnd.github+json"}
    token = get_github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    candidates = {}
    for i, (q, sort) in enumerate(SEC_TOOL_QUERIES):
        if i:
            time.sleep(7 if "Authorization" not in headers else 2.5)
        data = _github_search(q, sort, per_query * 4, headers, tag=f"AI보안툴 {i + 1}/{len(SEC_TOOL_QUERIES)}")
        added = 0
        for repo in data.get("items", []):
            full = repo.get("full_name") or ""
            is_seed = full.lower() in SEC_TOOL_SEED
            if added >= per_query and not is_seed:
                continue
            desc = clean_text(repo.get("description") or "")
            topics = repo.get("topics") or []
            if not full or not desc:
                continue
            pushed = (repo.get("pushed_at") or "")[:10]
            if pushed and not _recent_enough(pushed, days):
                continue
            if not is_ai_sec_tool_repo(full, desc, topics, repo.get("language"),
                                      int(repo.get("size") or 0), bool(repo.get("fork"))):
                continue
            if full in candidates:
                continue
            stars = int(repo.get("stargazers_count") or 0)
            extra = [f"언어 {repo.get('language')}", f"★ {stars:,}"]
            if topics:
                extra.append("토픽 " + ", ".join(topics[:6]))
            if repo.get("created_at"):
                extra.append(f"생성 {repo['created_at'][:10]}")
            if repo.get("license") and repo["license"].get("spdx_id"):
                extra.append(f"라이선스 {repo['license']['spdx_id']}")
            candidates[full] = {
                "source": "GitHub",
                "item_key": item_key("GitHub", full, repo.get("html_url") or f"https://github.com/{full}"),
                "title_orig": full,
                "url": repo.get("html_url") or f"https://github.com/{full}",
                "summary_orig": clean_text(f"{desc} ({' · '.join(extra)})", 1200),
                "published_at": pushed,
                "score": stars,
                "source_hint": f"GitHub ★{stars:,} · AI 보안 도구",
                "track": "sec_tool",
                "sec_tool": True,
                "seed": is_seed,
            }
            added += 1
        print(f"  [AI보안툴 {i + 1}/{len(SEC_TOOL_QUERIES)}] {q} → {added}건")
    allc = list(candidates.values())
    seeded = sorted([c for c in allc if c.get("seed")], key=lambda x: -x["score"])
    rest = sorted([c for c in allc if not c.get("seed")], key=lambda x: -x["score"])
    picked = seeded + rest[:max(0, max_items - len(seeded))]
    out = sorted(picked, key=lambda x: -x["score"])
    print(f"  [AI보안툴] 후보 {len(allc)}건 중 {len(out)}건 채택 (검증 시드 {len(seeded)}건)")
    return out



def dedupe_and_mix(items, target=TARGET_TOTAL):
    """제목/URL 중복 제거 후, 보안·도구 최소 쿼터 + 출처 라운드 로빈으로 믹스"""
    seen_titles = set()
    seen_urls = set()
    uniq = []
    for it in items:
        t = norm_title(it["title_orig"])
        u = norm_url(it.get("url"))
        if not t or t in seen_titles or (u and u in seen_urls):
            continue
        seen_titles.add(t)
        if u:
            seen_urls.add(u)
        it["item_key"] = item_key(it["source"], it["title_orig"], it.get("url"))
        uniq.append(it)

    def latest_first(lst):
        return sorted(lst, key=lambda x: (x.get("published_at") or "", x.get("score") or 0), reverse=True)

    def pick_quota(pool, quota):
        """트랙 쿼터 안에서도 출처가 골고루 섞이도록 라운드 로빈 선택"""
        by_src = {}
        # GitHub은 pushed_at이 늘 오늘에 가까워 날짜 정렬이 의미가 없다 → 스타 우선
        gh = sorted([i for i in pool if i.get("source") == "GitHub"],
                    key=lambda x: (x.get("score") or 0, x.get("published_at") or ""), reverse=True)
        non_gh = latest_first([i for i in pool if i.get("source") != "GitHub"])
        for it in non_gh + gh:
            by_src.setdefault(it["source"], []).append(it)
        order = [s for s in INTERLEAVE_ORDER if s in by_src]
        chosen = []
        idx = 0
        while len(chosen) < quota and any(len(b) > idx for b in by_src.values()):
            for s in order:
                b = by_src[s]
                if len(b) > idx and len(chosen) < quota:
                    chosen.append(b[idx])
            idx += 1
        return chosen

    picked = []
    picked_keys = set()

    # 1) 보안·도구 쿼터 먼저 확보 (카테고리가 비지 않도록)
    for track, quota in (("security", SEC_TARGET), ("tool", TOOL_TARGET)):
        pool = [i for i in uniq if i.get("track") == track]
        chosen = pick_quota(pool, quota)
        for it in chosen:
            picked.append(it)
            picked_keys.add(it["item_key"])
        print(f"  · {track} 쿼터: {len(chosen)}건 확보 (후보 {len(pool)}건)")

    # 2) 나머지는 출처 라운드 로빈으로 채움
    buckets = {}
    for it in uniq:
        if it["item_key"] in picked_keys:
            continue
        buckets.setdefault(it["source"], []).append(it)
    for s in buckets:
        buckets[s] = latest_first(buckets[s])

    idx = 0
    while len(picked) < target and any(len(b) > idx for b in buckets.values()):
        for s in INTERLEAVE_ORDER:
            b = buckets.get(s, [])
            if len(b) > idx and len(picked) < target:
                picked.append(b[idx])
                picked_keys.add(b[idx]["item_key"])
        idx += 1

    # 3) 분석 배치가 한 출처에 몰리지 않도록 다시 출처 라운드 로빈으로 정렬
    per_src = {}
    for it in picked:
        per_src.setdefault(it["source"], []).append(it)
    mixed = []
    idx = 0
    while len(mixed) < len(picked):
        progressed = False
        for s in INTERLEAVE_ORDER:
            b = per_src.get(s, [])
            if len(b) > idx:
                mixed.append(b[idx])
                progressed = True
            if len(mixed) >= len(picked):
                break
        if not progressed:
            break
        idx += 1
    return mixed


# ---------------------------------------------------------------------------
# 2) EXAONE 분석
# ---------------------------------------------------------------------------

def get_api_key():
    key = os.environ.get("EXAONE_API_KEY")
    if key:
        return key.strip()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("EXAONE_API_KEY="):
                    return line.strip().split("=", 1)[1].strip()
    return None


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:  # noqa: BLE001
            return {}
    return {}


def save_cache(cache):
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CACHE_FILE)


SYSTEM_PROMPT = (
    "당신은 AI 기술 동향 분석가입니다. 제공된 AI 관련 논문·뉴스 원문을 읽고 한국어로 분석합니다. "
    "과장 없이 사실만 다루며, 반드시 지정된 JSON 배열만 출력합니다."
)


def build_prompt(chunk):
    lines = []
    for i, it in enumerate(chunk, 1):
        hint = it.get("source_hint") or ""
        if it.get("track") == "security":
            kind = "보안 수집"
        elif it.get("track") == "tool":
            kind = "도구 수집"
        else:
            kind = "일반"
        lines.append(
            f"[{i}] 출처: {it['source']} | 날짜: {it.get('published_at') or '미상'} | 유형: {kind} {hint}\n"
            f"제목: {it['title_orig']}\n"
            f"원문 요약: {(it.get('summary_orig') or '(원문 요약 없음)')[:650]}"
        )
    body = "\n\n".join(lines)
    return (
        f"다음 AI 관련 자료 {len(chunk)}건을 분석해 JSON 배열로만 답하세요. "
        "각 항목은 아래 키를 모두 포함해야 합니다.\n"
        "- id: 입력 번호(정수)\n"
        "- title_ko: 자연스러운 한국어 제목 (번역투 금지, 20~45자, 기술명·모델명·기관명·저장소명은 원문 표기 유지)\n"
        "- category: 다음 6개 중 정확히 1개\n"
        "    \"AI 보안 툴\" = 실제 실행해 쓸 수 있는 AI 보안 오픈소스 도구·스캐너·가드레일·프레임워크 (GitHub 저장소)\n"
        "    \"AI 보안·안전\" = AI/LLM 시스템의 공격·취특점·방어, 프롬프트 인젝션·탈옥, 에이전트 보안, 딥페이크, 모델 유출, AI 프라이버시·규제·안전\n"
        "    \"AI 툴·서비스\" = 개발자·실무자가 바로 쓰는 AI 도구·오픈소스 저장소·CLI·SDK·플랫폼·서비스 출시 (모델 성능 자체 연구는 모델·논문)\n"
        "    \"LLM·에이전트\" = LLM 활용 기법·에이전트 아키텍처·RAG·추론·프롬프트 설계\n"
        "    \"모델·논문\" = 새 모델·모델 구조·학습·양자화·벤치마크·데이터셋 연구\n"
        "    \"산업·트렌드\" = 시장·조직·정책·도입 사례·투자 동향\n"
        "- summary: 핵심 내용을 한국어 2~3문장으로 (무엇을 했고, 어떻게 했고, 결과가 무엇인지)\n"
        "  · AI 보안 툴 항목: ①핵심 기능(스캔·프록시·가드레일·샌드박스·레드팀 자동화 등) ②탐지·방어 대상(프롬프트 인젝션·탈옥·MCP 도구 오남용·에이전트 권한·모델 유출 등)을 summary에 반드시 포함\n"
        "  · AI 보안 항목: 어떤 공격·취특점인지, 무엇이 영향을 받았는지(제품·에이전트·데이터)를 summary에 반드시 포함\n"
        "  · AI 툴 항목: 이 도구가 어떤 문제를 푸는지(핵심 기능·지원 범위)를 summary에 반드시 포함\n"
        "- tech_insight: 기술적 포인트와 실무·보안 관점의 시사점 1~2문장\n"
        "  · AI 보안 툴 항목: 실무 활용 포인트(CI·배포 파이프라인 게이트, 런타임 프록시·게이트웨이, 에이전트 툴 호출 검증, 레드팀 자동화 중 해당되는 것)를 반드시 제시\n"
        "  · AI 보안 항목: 대응·완화 방안(패치·권한 최소화·입력 검증·모니터링·가드레일 중 해당되는 것)을 반드시 제시\n"
        "  · AI 툴 항목: 실무 활용법 + 보안 유의점(에이전트 권한, 데이터 노출, 공급망·설치 리스크 중 해당되는 것)\n"
        "  · GitHub 저장소 항목: 스타 수·언어·최근 업데이트를 참고해 성숙도와 도입 판단 포인트를 짚기\n"
        "- tags: 핵심 키워드 2~4개 (예: \"#RAG\", \"#에이전트\", \"#프롬프트인젝션\", \"#오픈소스도구\")\n"
        "- is_featured: 실무에 바로 영향이 있거나 주목할 기술이면 true, 아니면 false\n\n"
        f"{body}\n\n"
        "출력 형식(설명·코드블록 없이 JSON 배열만):\n"
        "[{\"id\":1,\"title_ko\":\"...\",\"category\":\"...\",\"summary\":\"...\","
        "\"tech_insight\":\"...\",\"tags\":[\"#...\",\"#...\"],\"is_featured\":true}]"
    )


def salvage_objects(text):
    """잘린/손상된 JSON에서도 완결된 객체만 건져내기"""
    decoder = json.JSONDecoder()
    objs = []
    i = 0
    n = len(text)
    while i < n:
        idx = text.find("{", i)
        if idx < 0:
            break
        try:
            obj, end = decoder.raw_decode(text[idx:])
            if isinstance(obj, dict):
                objs.append(obj)
            i = idx + end
        except Exception:  # noqa: BLE001
            i = idx + 1
    return objs


def parse_json_array(content, debug_tag=""):
    if not content:
        return None
    text = content.strip()
    if "```" in text:
        m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
        if m:
            text = m.group(1).strip()
    m = re.search(r"\[.*\]", text, re.S)
    candidate = m.group(0) if m else text
    try:
        data = json.loads(candidate)
        if isinstance(data, list):
            return data
    except Exception:  # noqa: BLE001
        pass
    try:
        data = json.loads(re.sub(r",\s*([\]}])", r"\1", candidate))
        if isinstance(data, list):
            return data
    except Exception:  # noqa: BLE001
        pass
    # 3차: 완결 객체 단위 복구
    objs = salvage_objects(candidate)
    if objs:
        print(f"  [API] JSON 부분 복구: {len(objs)}건")
        return objs
    if debug_tag:
        try:
            with open(os.path.join(BASE_DIR, f"ai_parse_fail_{debug_tag}.txt"), "w", encoding="utf-8") as f:
                f.write(content[:4000])
        except Exception:  # noqa: BLE001
            pass
    return None


def normalize_tags(raw):
    tags = []
    if isinstance(raw, str):
        raw = re.split(r"[,\s]+", raw)
    for t in (raw or []):
        t = str(t).strip()
        if not t:
            continue
        t = re.sub(r"\s+", "", t)
        if not t.startswith("#"):
            t = "#" + t
        if len(t) > 18:
            continue
        if t not in tags:
            tags.append(t)
    return tags[:4]


def normalize_analysis(res, item):
    cat = clean_text(res.get("category"))
    cat = CATEGORY_ALIASES.get(cat, cat)
    if cat not in CATEGORIES:
        for c in CATEGORIES:
            if c and c.replace("·", "") in cat.replace("·", ""):
                cat = c
                break
        else:
            cat = guess_category(item)
    analysis = {
        "title_ko": clean_text(res.get("title_ko")) or fallback_title(item),
        "category": cat,
        "summary": clean_text(res.get("summary")) or fallback_summary(item),
        "tech_insight": clean_text(res.get("tech_insight")) or fallback_insight(item),
        "tags": normalize_tags(res.get("tags")) or fallback_tags(item),
        "is_featured": bool(res.get("is_featured")),
        "analyzed_by": "exaone",
    }
    return analysis


def call_exaone(prompt, api_key, max_tokens=3200, timeout=200):
    payload = {
        "model": "k-exaone_v2.5",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "reasoning_effort": "low",
    }
    req = urllib.request.Request(
        "https://api.exaone.ai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


# --- 폴백 (원문 기반 정제) -------------------------------------------------

CATEGORY_RULES = [
    ("AI 보안·안전", r"(보안|안전|취약|공격|탈옥|jailbreak|adversarial|attack|safety|security|privacy|개인정보|malware|악성|프롬프트 인젝션|prompt injection|injection|red.?team|편향|bias|환각|hallucinat|유출|leak|exfiltrat|백도어|backdoor|딥페이크|deepfake)"),
    ("AI 툴·서비스", r"(오픈소스|open.?source|깃허브|github|sdk|cli|라이브러리|library|프레임워크|framework|도구|tool|toolkit|서비스|플랫폼|platform|plugin|extension|self.?host|저장소|repo)"),
    ("LLM·에이전트", r"(에이전트|agent|agentic|llm|대화|챗봇|챗gpt|gpt|claude|gemini|프롬프트|prompt|rag|mcp|tool.?use|reasoning|추론)"),
    ("모델·논문", r"(논문|paper|모델|model|transformer|diffusion|학습|training|벤치마크|benchmark|데이터셋|dataset|아키텍처|attention|파라미터|parameter)"),
]


def guess_category(item):
    """EXAONE 실패 시 원문 기반 카테고리 추정 (수집 트랙 우선)"""
    track = item.get("track")
    blob = f"{item.get('title_orig', '')} {item.get('summary_orig', '')} {item.get('source_hint', '')}"
    if track == "sec_tool":
        return AI_SEC_TOOL_CAT
    if track == "security" and SEC_TERMS.search(blob):
        return "AI 보안·안전"
    if track == "tool" and item.get("source") in ("GitHub", "Show HN"):
        return "AI 보안·안전" if SEC_TERMS.search(blob) else "AI 툴·서비스"
    for cat, pat in CATEGORY_RULES:
        if re.search(pat, blob, re.I):
            return cat
    if item.get("published_at", "") and item.get("source") in ("arXiv", "Hugging Face"):
        return "모델·논문"
    return "산업·트렌드"


def fallback_title(item):
    t = clean_text(item.get("title_orig"))
    t = re.sub(r"\s*\[[^\]]*\]\s*$", "", t)
    return t[:120]


def fallback_summary(item):
    s = clean_text(item.get("summary_orig"), 320)
    if len(s) < 40:
        hint = item.get("source_hint") or item.get("source")
        return f"{item['title_orig']} — {hint}에서 수집된 자료입니다. 상세 내용은 원문에서 확인할 수 있습니다."
    return s


def fallback_insight(item):
    cat = guess_category(item)
    src = item.get("source", "")
    mapping = {
        "AI 보안·안전": "공격 경로를 확인한 뒤 프롬프트·도구 권한, 입출력 검증, 탐지·모니터링을 함께 점검해야 함을 시사합니다.",
        "AI 보안 툴": "AI 시스템에 바로 붙여 쓸 수 있는 보안 도구로, 도입 시 탐지 범위·오탐률·유지보수 활도를 함께 확인해야 합니다.",
        "AI 툴·서비스": "실무에 바로 검토할 수 있는 도구로, 도입 시 에이전트 권한·데이터 노출·공급망 신뢰를 함께 확인해야 합니다.",
        "LLM·에이전트": "에이전트·LLM 활용 구조를 설계할 때 참고할 만한 구현 포인트를 담고 있습니다.",
        "모델·논문": "모델 구조·학습 방식의 변화로 실무 적용 가능성을 판단할 근거가 됩니다.",
        "산업·트렌드": "시장·조직 차원의 AI 활용 흐름을 판단하는 데 참고할 만합니다.",
    }
    return f"{mapping.get(cat, '')} ({src} 원문 기준 자동 정제)".strip()


def fallback_tags(item):
    blob = f"{item.get('title_orig','')} {item.get('summary_orig','')}".lower()
    table = [
        ("#에이전트", r"agent|에이전트"),
        ("#RAG", r"\brag\b|retrieval"),
        ("#AI보안", r"security|보안|attack|공격|jailbreak|취약"),
        ("#LLM", r"\bllm\b|large language"),
        ("#멀티모달", r"multimodal|멀티모달|vision|이미지"),
        ("#경량모델", r"distill|quantiz|경량|efficient|small model"),
        ("#추론", r"reasoning|추론|chain.?of.?thought"),
        ("#오픈소스", r"open.?source|오픈소스|github"),
        ("#파인튜닝", r"fine.?tun|파인튜닝|lora"),
        ("#벤치마크", r"benchmark|벤치마크|eval"),
        ("#인프라", r"inference|serving|gpu|인프라|배포"),
    ]
    tags = [tag for tag, pat in table if re.search(pat, blob)][:3]
    if not tags:
        tags = ["#" + (re.sub(r"[\s·]+", "", guess_category(item)) or "AI")]
    return tags


# ---------------------------------------------------------------------------
# 3) 브리핑 문장 (오늘의 AI 기술 동향)
# ---------------------------------------------------------------------------

def build_briefing_fallback(items, top_keywords, cat_counts):
    total = len(items)
    top_cat = max(cat_counts.items(), key=lambda x: x[1])[0] if cat_counts else "산업·트렌드"
    kw = ", ".join(k[0] for k in top_keywords[:3]) or "LLM"
    featured = sum(1 for i in items if i.get("is_featured"))
    sec = cat_counts.get("AI 보안·안전", 0)
    sectool = cat_counts.get(AI_SEC_TOOL_CAT, 0)
    tool = cat_counts.get("AI 툴·서비스", 0)
    sec_titles = [i.get("title_ko") or i["title_orig"] for i in items if i.get("category") == "AI 보안·안전"][:2]
    sectool_titles = [i["title_orig"] for i in items if i.get("category") == AI_SEC_TOOL_CAT][:2]
    tool_titles = [i.get("title_ko") or i["title_orig"] for i in items if i.get("category") == "AI 툴·서비스"][:2]
    parts = [f"오늘 수집된 AI 자료 {total}건 중 '{top_cat}' 비중이 가장 큽니다. 핵심 키워드는 {kw}이며, 주목할 기술 {featured}건이 포함되어 있습니다."]
    if sec_titles:
        parts.append(f"AI 보안·안전 {sec}건 중에서는 " + " / ".join(sec_titles) + " 등이 눈에 띕니다.")
    if sectool_titles:
        parts.append(f"바로 도입을 검토해 볼 AI 보안 오픈소스 툴 {sectool}건도 모았습니다(" + " / ".join(sectool_titles) + " 등).")
    if tool_titles:
        parts.append(f"AI 툴·서비스 {tool}건에서는 " + " / ".join(tool_titles) + " 등을 바로 검토해 볼 만합니다.")
    return " ".join(parts)


def _unwrap_briefing(raw):
    """모델이 JSON 배열/따옴표로 감싸 보낸 브리핑을 평문 한 덩어리로 정리"""
    t = (raw or "").strip()
    if not t:
        return ""
    # 1) JSON 문자열 배열이면 합치기
    candidate = t if t.startswith("[") else "[" + t + "]"
    try:
        arr = json.loads(candidate)
        if isinstance(arr, list) and arr and all(isinstance(x, str) for x in arr):
            return clean_text(" ".join(arr))
    except Exception:  # noqa: BLE001
        pass
    # 2) 따옴표 구분자 제거 후 남은 괄호/따옴표 벗기기
    t = re.sub(r'"\s*,\s*"', " ", t)
    t = re.sub(r"^[\[\{\"'\s]+", "", t)
    t = re.sub(r"[\]\}\"'\s]+$", "", t)
    return clean_text(t)


def build_briefing_exaone(items, api_key, top_keywords, cat_counts):
    # 보안·도구 항목이 목록 앞쪽에 오도록 정렬해 브리핑 반영률을 높임
    priority = [i for i in items if i.get("category") in (AI_SEC_TOOL_CAT, "AI 보안·안전", "AI 툴·서비스")]
    others = [i for i in items if i not in priority]
    sample = []
    for it in (priority[:16] + others[:14]):
        sample.append(f"- [{it['category']}] {it.get('title_ko') or it['title_orig']}")
    prompt = (
        "다음은 오늘 수집한 AI 기술·뉴스·논문 목록입니다. 이 목록만 근거로 "
        "오늘의 AI 기술 동향을 한국어 3~4문장으로 요약하세요. "
        "1문장: 가장 두드러진 흐름, 2문장: 오늘의 주요 AI 보안 쟁점(공격·유출·에이전트 리스크), "
        "3문장: 주목할 AI 툴·서비스와 어디에 쓸 수 있는지, 4문장(선택): 실무자가 당장 점검할 점. "
        "목록에 보안·도구 항목이 없으면 그 문장은 건너뛰고 3문장으로 마무리하세요. "
        "군더더기·인사말·머리말 없이 요약 본문만, JSON이나 따옴표 없이 평문으로 출력하세요.\n\n"
        + "\n".join(sample)
    )
    content = call_exaone(prompt, api_key, max_tokens=800, timeout=120)
    text = re.sub(r"^(요약|브리핑)\s*[:：]\s*", "", (content or "").strip())
    text = _unwrap_briefing(text)
    if len(text) < 40:
        raise RuntimeError("브리핑 응답이 너무 짧음")
    return text[:700]


def collect_all():
    print("[1/3] 소스 수집 시작")
    raw = []
    # AI 보안 전용 수집을 먼저 담아 중복 제거 시 보안 라벨을 우선 확보
    raw += collect_security_feeds()
    raw += collect_arxiv_security()
    raw += collect_hackernews_security()
    raw += collect_github_tools()
    raw += collect_show_hn()
    # 일반 AI 수집
    raw += collect_huggingface()
    raw += collect_arxiv()
    raw += collect_hackernews()
    raw += collect_geeknews(limit=14)
    items = dedupe_and_mix(raw)
    print(f"-> 중복 제거·출처 믹스 후 분석 대상 {len(items)}건")
    return items


def normalize_cache_categories(cache):
    """캐시에 남은 옛 카테고리(개발·오픈소스 등)를 새 5개 카테고리로 정규화"""
    changed = 0
    for v in cache.values():
        if not isinstance(v, dict):
            continue
        cat = v.get("category")
        new = CATEGORY_ALIASES.get(cat, cat)
        if new in CATEGORIES and new != cat:
            v["category"] = new
            changed += 1
    if changed:
        print(f"  [캐시] 카테고리 정규화 {changed}건 (개발·오픈소스 → AI 툴·서비스)")
    return cache


SEC_OVERRIDE_CATS = ("모델·논문", "산업·트렌드")


def enforce_track_categories(items):
    """보안·도구 전용 수집분이 모호한 카테고리로 빠졌을 때 수집 의도를 반영해 바로잡는다.

    (보안 피드에서 AI+보안 조건으로 걸러온 기사·논문이 '산업·트렌드'나 '모델·논문'으로
     분류되면 보안 카테고리가 비어 보이므로, 원문에 보안 어휘가 확인될 때만 되돌린다.)
    """
    fixed = 0
    for it in items:
        track = it.get("track")
        cat = it.get("category")
        if track == "security" and cat in SEC_OVERRIDE_CATS:
            blob = f"{it.get('title_orig', '')} {it.get('summary_orig', '')} {it.get('title_ko', '')} {it.get('summary', '')}"
            if SEC_TERMS.search(blob):
                it["category"] = "AI 보안·안전"
                fixed += 1
        elif track == "tool" and cat in SEC_OVERRIDE_CATS and it.get("source") in ("GitHub", "Show HN"):
            blob = f"{it.get('title_orig', '')} {it.get('summary_orig', '')} {it.get('summary', '')}"
            if TOOL_TERMS.search(blob) and not SEC_TERMS.search(blob):
                it["category"] = "AI 툴·서비스"
                fixed += 1
        elif (track == "sec_tool" or it.get("sec_tool")) and cat != AI_SEC_TOOL_CAT:
            it["category"] = AI_SEC_TOOL_CAT
            fixed += 1
    if fixed:
        print(f"  [분류 보정] 수집 트랙 기준 카테고리 보정 {fixed}건")
    return items


def analyze_items(items, batch_size=3, max_calls=30, deadline=None, finalize=True):
    """EXAONE 배치 분석 + 캐시 + 폴백. 반환: 분석 완료 items 리스트

    deadline: time.monotonic() 기준 중단 시각. 넘으면 남은 배치는 다음 실행으로 넘긴다.
    finalize: False 면 폴백·트랙 보정을 생략한다(부분 실행 저장용).
    """
    cache = normalize_cache_categories(load_cache())
    api_key = get_api_key()

    # 1) 캐시 적중분 먼저 채우기
    pending = []
    for it in items:
        c = cache.get(it["item_key"])
        if c and c.get("title_ko") and c.get("summary") and c.get("category"):
            it.update({
                "title_ko": c["title_ko"],
                "category": c["category"],
                "summary": c["summary"],
                "tech_insight": c.get("tech_insight", ""),
                "tags": normalize_tags(c.get("tags")),
                "is_featured": bool(c.get("is_featured")),
                "analyzed_by": "cache",
            })
        else:
            pending.append(it)

    print(f"[2/3] 분석: 캐시 적중 {len(items) - len(pending)}건 / 신규 {len(pending)}건 (API 키 {'있음' if api_key else '없음'})")

    if api_key and pending:
        calls = 0
        for start in range(0, min(len(pending), max_calls * batch_size), batch_size):
            if deadline and time.monotonic() > deadline:
                print("  [중단] 시간 예산 소진 → 다음 실행에서 이어서 진행")
                break
            chunk = pending[start:start + batch_size]
            if not chunk:
                break
            prompt = build_prompt(chunk)
            it_dbg = now_kst().strftime("%H%M%S")
            content = None
            MAX_ATTEMPT = 6
            _call_timeout = int(os.environ.get("AI_CALL_TIMEOUT") or 150)
            for attempt in range(MAX_ATTEMPT):
                try:
                    content = call_exaone(prompt, api_key, timeout=_call_timeout)
                    if not (content or "").strip():
                        raise RuntimeError("빈 응답")
                    break
                except urllib.error.HTTPError as e:
                    code = e.code
                    body = ""
                    try:
                        body = e.read().decode("utf-8", errors="ignore")[:160]
                    except Exception:  # noqa: BLE001
                        pass
                    print(f"  [API] HTTP {code} (시도 {attempt + 1}/{MAX_ATTEMPT}) {body}")
                    if code in (401, 403):
                        print("  [API] 키 인증 실패 → 폴백으로 전환")
                        api_key = None
                        break
                    if code == 429:
                        # 서버 동시요청 혼잡(일시적) — 짧은 백오프 후 재시도
                        retry_after = 0
                        try:
                            retry_after = int(e.headers.get("Retry-After") or 0)
                        except (TypeError, ValueError):
                            retry_after = 0
                        wait = max(retry_after, min(45, 4 * (2 ** attempt)))
                    elif code >= 500:
                        wait = min(40, 5 * (attempt + 1))
                    else:
                        wait = 2 * (attempt + 1)
                    if deadline and time.monotonic() + wait > deadline:
                        print("  [중단] 시간 예산 소진 → 재시도 없이 다음 실행으로")
                        break
                    if attempt < MAX_ATTEMPT - 1:
                        print(f"  [API] {wait}초 대기 후 재시도")
                        time.sleep(wait)
                except Exception as e:  # noqa: BLE001
                    print(f"  [API] 오류 {type(e).__name__}: {e} (시도 {attempt + 1}/{MAX_ATTEMPT})")
                    if attempt < MAX_ATTEMPT - 1:
                        time.sleep(3 * (attempt + 1))
            if not api_key:
                break
            if not content:
                print("  [API] 배치 실패 → 폴백 처리")
                continue

            results = parse_json_array(content, debug_tag=it_dbg)
            if not results:
                print("  [API] JSON 파싱 실패 → 폴백 처리")
                continue

            by_id = {}
            for r in results:
                if not isinstance(r, dict):
                    continue
                try:
                    by_id[int(r.get("id", 0))] = r
                except (TypeError, ValueError):
                    continue

            for i, it in enumerate(chunk, 1):
                res = by_id.get(i)
                if res:
                    analysis = normalize_analysis(res, it)
                else:
                    analysis = {
                        "title_ko": fallback_title(it),
                        "category": guess_category(it),
                        "summary": fallback_summary(it),
                        "tech_insight": fallback_insight(it),
                        "tags": fallback_tags(it),
                        "is_featured": False,
                        "analyzed_by": "fallback",
                    }
                it.update(analysis)
                if analysis["analyzed_by"] == "exaone":
                    cache[it["item_key"]] = {
                        "title_ko": analysis["title_ko"],
                        "category": analysis["category"],
                        "summary": analysis["summary"],
                        "tech_insight": analysis["tech_insight"],
                        "tags": analysis["tags"],
                        "is_featured": analysis["is_featured"],
                        "analyzed_at": now_kst().strftime("%Y-%m-%d %H:%M:%S"),
                    }
            save_cache(cache)
            calls += 1
            ok = sum(1 for it in chunk if it.get("analyzed_by") == "exaone")
            print(f"  [API] 배치 {calls} 완료: {ok}/{len(chunk)}건 분석 (누적 캐시 {len(cache)})")
            time.sleep(1.8)

    # 2) 남은 항목 폴백 정제 (빈 항목 없음 보장 — 최종 확정 시에만)
    if finalize:
        for it in items:
            if not it.get("title_ko"):
                it.update({
                    "title_ko": fallback_title(it),
                    "category": guess_category(it),
                    "summary": fallback_summary(it),
                    "tech_insight": fallback_insight(it),
                    "tags": fallback_tags(it),
                    "is_featured": False,
                    "analyzed_by": "fallback",
                })
            if not it.get("summary"):
                it["summary"] = fallback_summary(it)
            if not it.get("tech_insight"):
                it["tech_insight"] = fallback_insight(it)
            if not it.get("tags"):
                it["tags"] = fallback_tags(it)

        # 3) 수집 트랙 기준 카테고리 보정 (보안·도구 카테고리 공백 방지)
        enforce_track_categories(items)
        for it in items:
            if it["category"] not in CATEGORIES:
                it["category"] = guess_category(it)
    return items, cache


def compute_aggregates(items):
    cat_counts = {c: 0 for c in CATEGORIES}
    for it in items:
        cat_counts[it["category"]] = cat_counts.get(it["category"], 0) + 1

    tag_counter = {}
    for it in items:
        for t in {"#" + x.lstrip("#") for x in it.get("tags", [])}:
            tag_counter[t] = tag_counter.get(t, 0) + 1
    top_keywords = [[k, v] for k, v in sorted(tag_counter.items(), key=lambda x: (-x[1], len(x[0])))[:8]]

    source_counts = {s: 0 for s in SOURCES}
    for it in items:
        source_counts[it["source"]] = source_counts.get(it["source"], 0) + 1

    return cat_counts, top_keywords, source_counts


def save_ai_data(items, cat_counts, top_keywords, source_counts, briefing):
    payload = {
        "updated_at": now_kst().strftime("%Y-%m-%d %H:%M:%S KST"),
        "total": len(items),
        "briefing": briefing,
        "top_keywords": [{"keyword": k, "count": v} for k, v in top_keywords[:5]],
        "categories": cat_counts,
        "sources": source_counts,
        "items": [
            {
                "item_key": it["item_key"],
                "source": it["source"],
                "title_ko": it["title_ko"],
                "title_orig": it["title_orig"],
                "url": it["url"],
                "category": it["category"],
                "summary": it["summary"],
                "tech_insight": it["tech_insight"],
                "tags": it["tags"],
                "is_featured": bool(it["is_featured"]),
                "published_at": it.get("published_at", ""),
                "analyzed_by": it.get("analyzed_by", "fallback"),
            }
            for it in items
        ],
    }
    with open(AI_DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def sort_for_display(items):
    """주목할 기술 우선 + 최신순"""
    def key(it):
        return (0 if it.get("is_featured") else 1, _neg_date(it.get("published_at") or ""))
    return sorted(items, key=key)


def _neg_date(d):
    # 날짜 내림차순 정렬용: 문자열을 뒤집어 비교
    return "".join(chr(255 - ord(c)) for c in (d or "0000-00-00"))


def finalize_run(items):
    """분석이 끝난 items 로 브리핑·ai_data.json·DB 적재까지 마무리"""
    from db_manager import init_db, upsert_ai_insights, get_ai_insight_count

    t0 = time.time()
    init_db()
    items = sort_for_display(items)
    cat_counts, top_keywords, source_counts = compute_aggregates(items)
    if cat_counts.get("AI 보안·안전", 0) < 8:
        print(f"⚠ AI 보안·안전 카테고리가 {cat_counts.get('AI 보안·안전', 0)}건으로 목표(8건) 미만입니다.")
    if cat_counts.get(AI_SEC_TOOL_CAT, 0) < 12:
        print(f"⚠ {AI_SEC_TOOL_CAT} 카테고리가 {cat_counts.get(AI_SEC_TOOL_CAT, 0)}건으로 목표(12건) 미만입니다.")
    if cat_counts.get("AI 툴·서비스", 0) < 8:
        print(f"⚠ AI 툴·서비스 카테고리가 {cat_counts.get('AI 툴·서비스', 0)}건으로 목표(8건) 미만입니다.")
    briefing = build_briefing_fallback(items, top_keywords, cat_counts)
    _key = get_api_key()
    if _key:
        for _attempt in range(3):
            try:
                briefing = build_briefing_exaone(items, _key, top_keywords, cat_counts)
                break
            except Exception as _e:  # noqa: BLE001
                print(f"  [브리핑] 시도 {_attempt + 1}/3 실패 ({type(_e).__name__}) → 템플릿 유지")
                time.sleep(4 * (_attempt + 1))

    payload = save_ai_data(items, cat_counts, top_keywords, source_counts, briefing)

    upserted = upsert_ai_insights(items)
    print(f"[3/3] DB 적재 완료: {upserted}건 (테이블 누적 {get_ai_insight_count()}건)")

    exa = sum(1 for it in items if it.get("analyzed_by") == "exaone")
    fb = sum(1 for it in items if it.get("analyzed_by") == "fallback")
    print("\n=== AI 기술·트렌드 수집·분석 결과 ===")
    print(f"  총 수집: {len(items)}건 (EXAONE 분석 {exa}건 / 원문 정제 폴백 {fb}건)")
    print(f"  출처: " + ", ".join(f"{s} {c}건" for s, c in source_counts.items() if c))
    print(f"  카테고리: " + ", ".join(f"{c} {n}" for c, n in cat_counts.items()))
    sec_samples = [(i.get("title_ko") or i["title_orig"])[:34]
                   for i in items if i.get("category") == "AI 보안·안전"][:4]
    sectool_samples = [i["title_orig"] for i in items if i.get("category") == AI_SEC_TOOL_CAT][:6]
    tool_samples = [(i.get("title_ko") or i["title_orig"])[:34]
                    for i in items if i.get("category") == "AI 툴·서비스"][:4]
    print("  AI 보안 샘플: " + " | ".join(sec_samples))
    print("  AI 보안 툴: " + " | ".join(sectool_samples))
    print("  AI 툴 샘플: " + " | ".join(tool_samples))
    print(f"  Top 키워드: " + ", ".join(f"{k}({v})" for k, v in top_keywords[:5]))
    print(f"  브리핑: {briefing[:160]}")
    print(f"  소요 시간: {round(time.time() - t0, 1)}초")
    return payload


def save_run_items(items):
    tmp = RUN_ITEMS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    os.replace(tmp, RUN_ITEMS_FILE)


def load_run_items():
    with open(RUN_ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_only():
    """수집만 수행하고 ai_run_items.json 에 저장 (장시간 분석을 나눠 돌리기 위한 단계)"""
    items = collect_all()
    save_run_items(items)
    print(f"-> 수집 결과 저장: {os.path.basename(RUN_ITEMS_FILE)} ({len(items)}건)")
    return items


# ---------------------------------------------------------------------------
# AI 보안 툴 전용 수집·분석·적재 (--sec-tools)
# ---------------------------------------------------------------------------

def _looks_like_ai_sec_tool(title, text):
    """DB에 이미 있는 저장소를 'AI 보안 툴'로 판단 (저장된 요약 기준)"""
    blob = f"{title} {text}"
    if SEC_TOOL_DENY.search(blob):
        return False
    return bool(SEC_TOOL_STRONG.search(blob))


def retag_existing_sec_tools():
    """기존 DB의 GitHub 저장소 중 AI 보안 도구를 'AI 보안 툴' 카테고리로 옮긴다.

    (지난 수집분은 EXAONE이 'AI 보안·안전'이나 'AI 툴·서비스'로 분류했기 때문에,
     AI 보안 뉴스·논문과 도구가 섞여 있었다.)
    """
    from db_manager import get_ai_insights, upsert_ai_insights
    items = get_ai_insights()
    moved = []
    for it in items:
        if it.get("source") != "GitHub" or it.get("category") == AI_SEC_TOOL_CAT:
            continue
        blob = f"{it.get('title_orig', '')} {it.get('summary', '')} {it.get('tech_insight', '')}"
        if _looks_like_ai_sec_tool(it.get("title_orig", ""), blob):
            it["category"] = AI_SEC_TOOL_CAT
            it["published_at"] = it.get("published_at") or ""
            moved.append(it)
    if moved:
        upsert_ai_insights(moved)
    print(f"[AI보안툴] 기존 DB 저장소 재분류 {len(moved)}건: " + ", ".join(i["title_orig"] for i in moved))
    return moved


def load_manual_overrides():
    if not os.path.exists(SEC_MANUAL_FILE):
        return {}
    try:
        with open(SEC_MANUAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return {}


def apply_manual_overrides(items):
    """EXAONE 응답이 없어 폴백으로 남은 항목에 저장소 원문을 근거로 쓴 한국어 소개를 채운다.

    (EXAONE 이 429 등으로 계속 막힐 때 카드가 영문 설명 그대로 노출되는 것을 막기 위한 보충이며,
     EXAONE 분석이 성공한 항목은 건드리지 않는다.)
    """
    manual = load_manual_overrides()
    applied = 0
    for it in items:
        if it.get("analyzed_by") == "exaone":
            continue
        m = manual.get(it.get("title_orig"))
        if not m:
            continue
        it.update({
            "title_ko": m["title_ko"],
            "summary": m["summary"],
            "tech_insight": m["tech_insight"],
            "tags": m.get("tags") or it.get("tags") or [],
            "is_featured": bool(m.get("is_featured")),
            "analyzed_by": "manual",
        })
        applied += 1
    if applied:
        print(f"  [수동 정제] EXAONE 미응답 {applied}건에 검증된 한국어 소개 적용")
    return items


def run_sec_tools(budget=None):
    """AI 보안 오픈소스 툴만 전용 수집 → EXAONE 분석 → DB 적재 → 브리핑 갱신"""
    init_db_prep()
    print("=== [AI 보안 툴] 전용 수집 시작 ===")
    items = collect_ai_sec_tools()
    if not items:
        print("⚠ AI 보안 툴 수집 결과가 없습니다.")
        return None
    deadline = (time.monotonic() + budget) if budget and budget > 0 else None
    items, _cache = analyze_items(items, batch_size=3, max_calls=14, deadline=deadline, finalize=True)
    apply_manual_overrides(items)

    from db_manager import upsert_ai_insights
    upsert_ai_insights(items)
    retag_existing_sec_tools()

    exa = sum(1 for it in items if it.get("analyzed_by") == "exaone")
    print(f"\n=== AI 보안 툴 {len(items)}건 수집·분석 완료 (EXAONE {exa}건) ===")
    for it in sorted(items, key=lambda x: -(x.get("score") or 0)):
        print(f"  ★{(it.get('score') or 0):>6,}  {(it.get('title_ko') or '')[:40]:<42} {it['title_orig']}")

    # DB 전체 기준으로 브리핑·ai_data.json 재생성 (ai.html 빌드용 메타)
    try:
        refresh_briefing()
    except Exception as e:  # noqa: BLE001
        print(f"  [브리핑] 갱신 실패: {type(e).__name__}: {e}")
    return items


# --- AI 보안 툴 수집 → 분석 → 마무리 단계 분리 실행 (EXAONE 혼잡·시간 상한 대응) ---

def save_sec_items(items):
    tmp = SEC_RUN_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    os.replace(tmp, SEC_RUN_FILE)


def load_sec_items():
    with open(SEC_RUN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def sec_collect():
    items = collect_ai_sec_tools()
    save_sec_items(items)
    print(f"-> 수집본 저장: {os.path.basename(SEC_RUN_FILE)} ({len(items)}건)")
    return items


def sec_analyze(batch_budget=8, seconds=185):
    """수집본에 대해 EXAONE 분석을 제한 시간만큼 진행 (여러 번 나눠 실행)"""
    items = load_sec_items()
    items, _cache = analyze_items(items, batch_size=1, max_calls=10,
                                  deadline=time.monotonic() + seconds, finalize=False)
    save_sec_items(items)
    done = sum(1 for it in items if it.get("analyzed_by") == "exaone")
    cached = sum(1 for it in items if it.get("analyzed_by") == "cache")
    print(f"-> 분석 진행: EXAONE {done}건 / 캐시 {cached}건 / 전체 {len(items)}건")
    return done + cached, len(items)


def sec_finish(seconds=230):
    """남은 항목을 폴백으로 마감하고 DB 적재·재분류·브리핑 갱신까지 마무리"""
    items = load_sec_items()
    items, _cache = analyze_items(items, batch_size=3, max_calls=5,
                                  deadline=time.monotonic() + seconds, finalize=True)
    apply_manual_overrides(items)
    from db_manager import upsert_ai_insights
    upsert_ai_insights(items)
    retag_existing_sec_tools()
    exa = sum(1 for it in items if it.get("analyzed_by") == "exaone")
    print(f"\n=== AI 보안 툴 {len(items)}건 적재 완료 (EXAONE {exa}건 / 폴백 {len(items) - exa}건) ===")
    for it in sorted(items, key=lambda x: -(x.get("score") or 0)):
        print(f"  ★{(it.get('score') or 0):>6,}  {it.get('analyzed_by'):<7} {it['title_orig']}")
    try:
        refresh_briefing()
    except Exception as e:  # noqa: BLE001
        print(f"  [브리핑] 갱신 실패: {type(e).__name__}: {e}")
    return items


def analyze_partial(batch_budget=6, seconds=240, batch_size=1):
    """저장된 수집본에 대해 시간 예산만큼만 EXAONE 분석을 진행하고 다시 저장

    batch_size=1: EXAONE 혼잡 시에도 한 건씩 확실히 처리 (요청이 작아 성공률이 높다).
    """
    items = load_run_items()
    items, _cache = analyze_items(items, batch_size=batch_size, max_calls=batch_budget,
                                  deadline=time.monotonic() + seconds, finalize=False)
    save_run_items(items)
    done = sum(1 for it in items if it.get("title_ko"))
    print(f"-> 부분 분석 저장: {done}/{len(items)}건 완료")
    return done, len(items)


def finish_from_file():
    items = load_run_items()
    items, _cache = analyze_items(items, max_calls=8, deadline=time.monotonic() + 120, finalize=True)
    payload = finalize_run(items)
    return payload


def run():
    init_db_prep()
    items = collect_all()
    if len(items) < 25:
        print(f"⚠ 수집 건수가 {len(items)}건으로 목표(25건) 미만입니다.")
    # AI_RUN_TIME_BUDGET(초)을 두면 그 시간 안에서만 분석하고 나머지는 원문 정제로 마감한다.
    # (EXAONE 혼잡으로 일일 자동화가 길어질 때 상한을 두는 용도. 0/미설정이면 무제한)
    try:
        budget = int(os.environ.get("AI_RUN_TIME_BUDGET") or 0)
    except ValueError:
        budget = 0
    deadline = (time.monotonic() + budget) if budget > 0 else None
    items, _cache = analyze_items(items, deadline=deadline)
    payload = finalize_run(items)
    # 일일 실행이 다시 수집한 AI 보안 저장소가 보안·도구 카테고리로 되돌아가지 않도록 재분류
    try:
        retag_existing_sec_tools()
    except Exception as e:  # noqa: BLE001
        print(f"  [AI보안툴] 재분류 건너뜀: {type(e).__name__}: {e}")
    return payload


def init_db_prep():
    from db_manager import init_db
    init_db()



def refresh_briefing(retries=4):
    """DB에 이미 적재된 항목만으로 '오늘의 AI 기술 동향' 브리핑 문장을 다시 생성한다.
    (수집 시점에 EXAONE 혼잡으로 템플릿 폴백이 들어간 경우 재시도용)"""
    from db_manager import get_ai_insights
    items = get_ai_insights()
    if not items:
        print("-> ai_insights 가 비어 있어 브리핑을 생성할 수 없습니다.")
        return None
    cat_counts, top_keywords, source_counts = compute_aggregates(items)
    api_key = get_api_key()
    briefing = ""
    for attempt in range(retries):
        if not api_key:
            break
        try:
            briefing = build_briefing_exaone(items, api_key, top_keywords, cat_counts)
        except Exception as e:  # noqa: BLE001
            print(f"  [브리핑] 시도 {attempt + 1}/{retries} 오류 {type(e).__name__}")
            time.sleep(5 * (attempt + 1))
            continue
        # 템플릿 폴백 문구가 아니면 채택
        if briefing and not briefing.startswith("오늘 수집된 AI 자료"):
            break
        print(f"  [브리핑] 시도 {attempt + 1}/{retries} 실패 → 재시도 대기")
        time.sleep(5 * (attempt + 1))
    if not briefing:
        briefing = build_briefing_fallback(items, top_keywords, cat_counts)

    payload = save_ai_data(items, cat_counts, top_keywords, source_counts, briefing)
    print(f"-> 브리핑 갱신 완료 ({len(briefing)}자)")
    return payload


if __name__ == "__main__":
    import sys
    if "--briefing-only" in sys.argv:
        refresh_briefing()
    elif "--collect-only" in sys.argv:
        collect_only()
    elif "--analyze-batch" in sys.argv:
        analyze_partial()
    elif "--finish" in sys.argv:
        finish_from_file()
    elif "--sec-tools" in sys.argv:
        try:
            _b = int(os.environ.get("AI_RUN_TIME_BUDGET") or 0)
        except ValueError:
            _b = 0
        run_sec_tools(budget=_b)
    elif "--sec-collect" in sys.argv:
        init_db_prep()
        sec_collect()
    elif "--sec-analyze" in sys.argv:
        sec_analyze()
    elif "--sec-finish" in sys.argv:
        init_db_prep()
        sec_finish()
    else:
        run()

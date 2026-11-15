#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기술·트렌드 수집 & 분석 크롤러 (Infosec Archive)

수집 소스
  - Hugging Face Daily Papers  : https://huggingface.co/api/daily_papers
  - arXiv (cs.AI / cs.CL / cs.CR): http://export.arxiv.org/api/query
  - Hacker News (Algolia)      : https://hn.algolia.com/api/v1/search
  - GeekNews                   : https://news.hada.io/rss/news

분석
  - EXAONE API (k-exaone_v2.5) 배치 3~4건, 호출 간 1.5~2초 대기, 429/5xx 지수 백오프 재시도
  - ai_tech_cache.json 캐싱 (성공한 분석만 캐시 → 재실행 시 API 호출 절감)
  - API 한도/오류 시 원문 기반 정제 폴백 (빈 항목 없음)

산출물
  - archive.db 의 ai_insights 테이블 UPSERT
  - ai_data.json (프론트엔드/외부 연동용)

보안: EXAONE_API_KEY 는 .env(로컬) 또는 환경변수에서만 읽으며, 로그/DB/JSON/Git 어디에도 기록하지 않는다.
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

KST = timezone(timedelta(hours=9))

CATEGORIES = ["LLM·에이전트", "AI 보안·안전", "모델·논문", "개발·오픈소스", "산업·트렌드"]
SOURCES = ["Hugging Face", "arXiv", "Hacker News", "GeekNews"]

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 수집 목표치 (중복 제거 후 최소 25건 이상 보장)
TARGET_TOTAL = 40

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
        if not AI_KO_PATTERNS.search(f"{title} {summary}"):
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


INTERLEAVE_ORDER = ["Hugging Face", "arXiv", "Hacker News", "GeekNews"]


def dedupe_and_mix(items, target=TARGET_TOTAL):
    """출처별 소스가 골고루 섞이도록 라운드 로빈 + 제목/URL 중복 제거"""
    buckets = {s: [] for s in INTERLEAVE_ORDER}
    seen_titles = set()
    seen_urls = set()
    for it in items:
        t = norm_title(it["title_orig"])
        u = norm_url(it.get("url"))
        if not t or t in seen_titles or (u and u in seen_urls):
            continue
        seen_titles.add(t)
        if u:
            seen_urls.add(u)
        it["item_key"] = item_key(it["source"], it["title_orig"], it.get("url"))
        buckets.setdefault(it["source"], []).append(it)

    for s in buckets:
        buckets[s].sort(key=lambda x: (x.get("published_at") or "", x.get("score") or 0), reverse=True)

    mixed = []
    idx = 0
    while len(mixed) < target and any(len(b) > idx for b in buckets.values()):
        for s in INTERLEAVE_ORDER:
            b = buckets.get(s, [])
            if len(b) > idx and len(mixed) < target:
                mixed.append(b[idx])
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
        lines.append(
            f"[{i}] 출처: {it['source']} | 날짜: {it.get('published_at') or '미상'}\n"
            f"제목: {it['title_orig']}\n"
            f"원문 요약: {(it.get('summary_orig') or '(원문 요약 없음)')[:650]}"
        )
    body = "\n\n".join(lines)
    return (
        f"다음 AI 관련 자료 {len(chunk)}건을 분석해 JSON 배열로만 답하세요. "
        "각 항목은 아래 키를 모두 포함해야 합니다.\n"
        "- id: 입력 번호(정수)\n"
        "- title_ko: 자연스러운 한국어 제목 (번역투 금지, 20~45자, 기술명·모델명·기관명은 원문 표기 유지)\n"
        "- category: 다음 5개 중 정확히 1개 → \"LLM·에이전트\", \"AI 보안·안전\", \"모델·논문\", \"개발·오픈소스\", \"산업·트렌드\"\n"
        "- summary: 핵심 내용을 한국어 2~3문장으로 (무엇을 했고, 어떻게 했고, 결과가 무엇인지)\n"
        "- tech_insight: 기술적 포인트와 실무·보안 관점의 시사점 1~2문장 (개발자/보안 담당자가 무엇을 얻을 수 있는지)\n"
        "- tags: 핵심 키워드 2~4개 (예: \"#RAG\", \"#에이전트\", \"#AI보안\", \"#경량모델\")\n"
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
    ("AI 보안·안전", r"(보안|안전|취약|공격|탈옥|jailbreak|adversarial|attack|safety|security|privacy|개인정보|malware|악성|프롬프트 인젝션|injection|red.?team|편향|bias|환각|hallucinat)"),
    ("LLM·에이전트", r"(에이전트|agent|agentic|llm|대화|챗봇|챗gpt|gpt|claude|gemini|프롬프트|prompt|rag|mcp|tool.?use|reasoning|추론)"),
    ("모델·논문", r"(논문|paper|모델|model|transformer|diffusion|학습|training|벤치마크|benchmark|데이터셋|dataset|아키텍처|attention|파라미터|parameter)"),
    ("개발·오픈소스", r"(오픈소스|open.?source|깃허브|github|sdk|api|라이브러리|library|프레임워크|framework|배포|release|도구|tool|cli|cursor|ide)"),
]


def guess_category(item):
    blob = f"{item.get('title_orig','')} {item.get('summary_orig','')} {item.get('source_hint','')}"
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
        "AI 보안·안전": "AI 시스템 도입 시 공격 표면과 통제 지점을 함께 검토해야 함을 시사합니다.",
        "LLM·에이전트": "에이전트·LLM 활용 구조를 설계할 때 참고할 만한 구현 포인트를 담고 있습니다.",
        "모델·논문": "모델 구조·학습 방식의 변화로 실무 적용 가능성을 판단할 근거가 됩니다.",
        "개발·오픈소스": "개발 파이프라인에 바로 적용할 수 있는 도구·방식과 관련됩니다.",
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
    return (f"오늘 수집된 AI 자료 {total}건 중 '{top_cat}' 비중이 가장 큽니다. "
            f"핵심 키워드는 {kw}이며, 주목할 기술 {featured}건이 포함되어 있습니다. "
            f"Hugging Face·arXiv 논문과 Hacker News·GeekNews 실무 담론을 함께 비교해 보세요.")


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
    sample = []
    for it in items[:26]:
        sample.append(f"- [{it['category']}] {it.get('title_ko') or it['title_orig']}")
    prompt = (
        "다음은 오늘 수집한 AI 기술·뉴스·논문 목록입니다. 이 목록만 근거로 "
        "오늘의 AI 기술 동향을 한국어 3문장으로 요약하세요. "
        "1문장: 가장 두드러진 흐름, 2문장: 구체적 기술·모델·보안 이슈, 3문장: 실무자가 주목할 점. "
        "군더더기·인사말·머리말 없이 요약 본문만, JSON이나 따옴표 없이 평문으로 출력하세요.\n\n"
        + "\n".join(sample)
    )
    content = call_exaone(prompt, api_key, max_tokens=700, timeout=120)
    text = re.sub(r"^(요약|브리핑)\s*[:：]\s*", "", (content or "").strip())
    text = _unwrap_briefing(text)
    if len(text) < 40:
        raise RuntimeError("브리핑 응답이 너무 짧음")
    return text[:700]


def collect_all():
    print("[1/3] 소스 수집 시작")
    raw = []
    raw += collect_huggingface()
    raw += collect_arxiv()
    raw += collect_hackernews()
    raw += collect_geeknews()
    items = dedupe_and_mix(raw)
    print(f"-> 중복 제거·출처 믹스 후 분석 대상 {len(items)}건")
    return items


def analyze_items(items, batch_size=3, max_calls=16):
    """EXAONE 배치 분석 + 캐시 + 폴백. 반환: 분석 완료 items 리스트"""
    cache = load_cache()
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
            chunk = pending[start:start + batch_size]
            if not chunk:
                break
            prompt = build_prompt(chunk)
            it_dbg = now_kst().strftime("%H%M%S")
            content = None
            MAX_ATTEMPT = 6
            for attempt in range(MAX_ATTEMPT):
                try:
                    content = call_exaone(prompt, api_key, timeout=200)
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
                        wait = 3 + 3 * attempt
                    elif code >= 500:
                        wait = 5 * (attempt + 1)
                    else:
                        wait = 2 * (attempt + 1)
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

    # 2) 남은 항목 폴백 정제 (빈 항목 없음 보장)
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


def run():
    from db_manager import init_db, upsert_ai_insights, get_ai_insight_count

    t0 = time.time()
    init_db()
    items = collect_all()
    if len(items) < 25:
        print(f"⚠ 수집 건수가 {len(items)}건으로 목표(25건) 미만입니다.")

    items, cache = analyze_items(items)
    items = sort_for_display(items)
    cat_counts, top_keywords, source_counts = compute_aggregates(items)
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
    print(f"  Top 키워드: " + ", ".join(f"{k}({v})" for k, v in top_keywords[:5]))
    print(f"  소요 시간: {round(time.time() - t0, 1)}초")
    return payload



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
    else:
        run()

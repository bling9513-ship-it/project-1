#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cve_crawler.py — CVE 취약점 수집·분석 파이프라인

수집 소스
  1) CISA KEV  : https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
                 (실제 공격에 악용된 취약점, 최근 추가분 우선 25건)
  2) CIRCL CVE : https://cve.circl.lu/api/last/100 (최신 피드에서 CVE 식별자 항목)
  3) NVD       : https://services.nvd.nist.gov/rest/json/cves/2.0 (최근 공개 CVE, CVSS·CPE·CWE·참고 링크)
  4) FIRST EPSS: https://api.first.org/data/v1/epss (배치 100건 단위 악용 확률)
  5) GitHub    : https://api.github.com/search/repositories (공개 PoC 저장소, gh CLI 인증 사용)
  6) CISA 경보  : https://www.cisa.gov/cybersecurity-advisories/all.xml (최근 경보·권고에 언급된 CVE)
  7) 보안 뉴스  : The Hacker News · BleepingComputer · Dark Reading RSS 에 언급된 CVE
  8) 보안기업   : Microsoft MSRC(업데이트 가이드) · Qualys · Wiz · Sophos · Palo Alto Unit 42 ·
                 Google Cloud 위협 인텔리전스 RSS (2026-11-19 접근 확인)
  9) 국내 기관   : KISA 보호나라·KrCERT/CC 게시판(취약점 정보·보안공지, HTML) — RSS/JSON 없음
     → 6·7 에서만 확인된 CVE 는 NVD 단건 → CIRCL 상세 → 경보 메타데이터 순으로 보강해 수집 후보로 편입
     → 단서는 cve_alerts 테이블에 보관되어 cve.html 카드에 '긴급 권고'로 표시된다

분석
  EXAONE(k-exaone_v2.5)이 CVE별 한국어 제목·요약·영향·조치 방안을 생성한다.
  429/타임아웃 등으로 실패한 항목은 CISA 권고·제품·취약점 유형을 근거로 한국어 폴백 문구를
  生成해 영문 원문이 그대로 노출되지 않도록 한다.

보안
  EXAONE_API_KEY 는 .env(로컬) 또는 환경변수에서만 읽고, 로그·DB·JSON·HTML·git 어디에도 기록하지 않는다.
  분석 캐시(cve_cache.json)는 .gitignore 에 등록되어 있다.

실행
  python3 cve_crawler.py                 # 수집 + 분석 + DB 적재
  python3 cve_crawler.py --collect-only  # 수집만 (cve_run_items.json 보관)
  python3 cve_crawler.py --enrich         # KEV 등 CVSS·제품 미상 항목을 CIRCL 상세 레코드로 보강
  python3 cve_crawler.py --analyze --limit-ai 12  # 보관된 수집본을 제한 시간·건수만큼 분석
  python3 cve_crawler.py --finish         # 분석 결과를 DB에 적재
  python3 cve_crawler.py --ai-only        # DB에 적재된 항목 중 폴백 항목만 재분석
  python3 cve_crawler.py --curated-sync    # cve_curated.json 에만 있는 CVE 를 DB 에 적재
"""
import os
import re
import sys
import json
import time
import hashlib
import html
import urllib.parse
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timezone, timedelta
from net_guard import MAX_HTML_BYTES, read_limited

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
CACHE_FILE = os.path.join(BASE_DIR, "cve_cache.json")
RUN_ITEMS_FILE = os.path.join(BASE_DIR, "cve_run_items.json")
CURATED_FILE = os.path.join(BASE_DIR, "cve_curated.json")

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from db_manager import (init_db, upsert_cve_reports, get_cve_reports,  # noqa: E402
                          upsert_cve_alerts)

KST = timezone(timedelta(hours=9))
UA = "InfosecArchive-CVE/1.0 (+https://github.com/bling9513-ship-it/project-1)"

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
CIRCL_URL = "https://cve.circl.lu/api/last/{n}"
NVD_URL = ("https://services.nvd.nist.gov/rest/json/cves/2.0"
           "?pubStartDate={start}&pubEndDate={end}&resultsPerPage=2000")
EPSS_URL = "https://api.first.org/data/v1/epss?cve={ids}"
GH_SEARCH_URL = ("https://api.github.com/search/repositories"
                 "?q={q}+in:name,description&sort=stars&per_page=3")
NVD_CVE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"

# 경보·보안 뉴스에서 CVE 를 캐내는 소스 (NVD/CIRCL/KEV 반영보다 빠른 경우가 있다)
CISA_ADVISORY_FEED = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
NEWS_CVE_FEEDS = [
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews", "days": 7},
    {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/", "days": 7},
    {"name": "Dark Reading", "url": "https://www.darkreading.com/rss.xml", "days": 7},
]

# 해외 주요 보안기업 피드 (RSS, 2026-11-19 접근 확인)
#  rank: 2 = 벤더 보안 권고/업데이트(기관 공지급), 3 = 보안 블로그·뉴스
VENDOR_CVE_FEEDS = [
    {"name": "Microsoft MSRC", "url": "https://api.msrc.microsoft.com/update-guide/rss", "days": 10, "rank": 2, "cap": 400},
    {"name": "Qualys Blog", "url": "https://blog.qualys.com/feed", "days": 21, "rank": 3, "cap": 40},
    {"name": "Wiz Blog", "url": "https://www.wiz.io/feed/rss.xml", "days": 21, "rank": 3, "cap": 60},
    {"name": "Sophos News", "url": "https://news.sophos.com/feed/", "days": 21, "rank": 3, "cap": 40},
    {"name": "Palo Alto Unit 42", "url": "https://unit42.paloaltonetworks.com/feed/", "days": 21, "rank": 3, "cap": 40},
    {"name": "Google Cloud Threat Intelligence", "url": "https://cloudblog.withgoogle.com/topics/threat-intelligence/rss/", "days": 21, "rank": 3, "cap": 40},
    {"name": "Rapid7 Blog", "url": "https://www.rapid7.com/blog/rss/", "days": 21, "rank": 3, "cap": 40},
]

# 국내 기관: RSS/JSON 이 없어 공개 게시판 HTML 을 직접 읽는다(2026-11-19 확인).
#  · KISA 보호나라 & KrCERT/CC (boho.or.kr = krcert.or.kr 동일 사이트) 서버렌더링 게시판
#  · 취약점 정보(B0000302)는 제목이 'CVE-XXXX-XXXXX | 제품 취약점' 형식이라 CVE 단서로 바로 쓸 수 있다.
KR_INSTITUTION_BOARDS = [
    {"name": "KISA 취약점 정보", "url": "https://www.boho.or.kr/kr/bbs/list.do?menuNo=205023&bbsId=B0000302", "days": 120, "rank": 2},
    {"name": "KISA 보안공지", "url": "https://www.boho.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133", "days": 30, "rank": 3},
]

# 별칭으로 더 잘 검색되는 CVE (GitHub PoC 검색 보강)
POC_ALIASES = {
    "CVE-2026-123007": ["nginx2root"],
    "CVE-2026-123633": ["nginx2root"],
    "CVE-2026-123634": ["nginx2root"],
    "CVE-2026-121810": ["nginx2root"],
    "CVE-2026-113425": ["nginx2root"],
    "CVE-2026-114938": ["java4shell"],
}
CVE_ID_RE = re.compile(r"CVE-\d{4}-\d{4,7}")
ALERT_FEED_DAYS = 14        # CISA 피드에서 볼 최근 발행 범위(일)
NEWS_CVE_DAYS = 7           # 뉴스 RSS 에서 볼 최근 발행 범위(일)
ALERT_CANDIDATE_LIMIT = 10  # 경보·뉴스에서만 확인된 CVE 를 새로 수집할 최대 건수

KEV_LIMIT = 25          # KEV 최근 추가분
NVD_DAYS = 3            # NVD 최근 공개 범위(일)
NVD_LIMIT = 25          # NVD 신규 CVE 최대 건수
CIRCL_EXTRA_LIMIT = 10  # CIRCL 피드 보강 건수
POC_QUERY_LIMIT = 38    # GitHub PoC 조회 최대 CVE 수
AI_BATCH = int(os.environ.get("CVE_AI_BATCH", "4"))     # EXAONE 1회 호출당 CVE 수
AI_TIME_BUDGET = int(os.environ.get("CVE_AI_TIME_BUDGET", "1500"))

SEVERITY_KO = {"CRITICAL": "치명적", "HIGH": "높음", "MEDIUM": "보통", "LOW": "낮음", "UNKNOWN": "미평가"}


# ---------------------------------------------------------------------------
# 공통 유틸
# ---------------------------------------------------------------------------

def now_kst():
    return datetime.now(KST)


def now_str():
    return now_kst().strftime("%Y-%m-%d %H:%M:%S KST")


def parse_cache_time(value):
    """캐시 시각 파싱 — now_str()의 ' KST' 접미사가 붙은 값도 받아들인다.

    (strptime "%Y-%m-%d %H:%M:%S" 는 ' KST' 때문에 매번 ValueError 가 났고,
     그래서 12시간 PoC 캐시가 한 번도 재사용되지 못했다.)
    반환값은 KST 기준 naive datetime.
    """
    if not value:
        return None
    s = str(value).replace("KST", "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def clean(text, limit=None):
    s = "" if text is None else str(text)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if limit and len(s) > limit:
        s = s[:limit].rstrip() + "…"
    return s


def http_json(url, timeout=40, retries=2, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(read_limited(resp).decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(8 * (attempt + 1))
                continue
            raise
        except Exception as e:  # noqa: BLE001  (타임아웃·연결 오류)
            last_err = e
            if attempt < retries:
                time.sleep(5 * (attempt + 1))
                continue
            raise
    raise last_err


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("analysis", {})
                data.setdefault("poc", {})
                return data
        except Exception:  # noqa: BLE001
            pass
    return {"analysis": {}, "poc": {}}


def save_cache(cache):
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    os.replace(tmp, CACHE_FILE)


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


# ---------------------------------------------------------------------------
# 1) 수집
# ---------------------------------------------------------------------------

def classify_severity(score):
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "UNKNOWN"
    if s >= 9.0:
        return "CRITICAL"
    if s >= 7.0:
        return "HIGH"
    if s >= 4.0:
        return "MEDIUM"
    if s > 0:
        return "LOW"
    return "UNKNOWN"


def fetch_kev(limit=KEV_LIMIT):
    data = http_json(KEV_URL, timeout=60, retries=1)
    vulns = data.get("vulnerabilities", [])
    vulns.sort(key=lambda v: (v.get("dateAdded") or "", v.get("cveID") or ""), reverse=True)
    picked = []
    for v in vulns[:limit]:
        picked.append({
            "cve_id": v.get("cveID"),
            "source": "CISA KEV",
            "vendor": clean(v.get("vendorProject")),
            "product": clean(v.get("product")),
            "published_at": v.get("dateAdded") or "",
            "is_kev": True,
            "kev_date_added": v.get("dateAdded") or "",
            "kev_due_date": v.get("dueDate") or "",
            "kev_required_action": clean(v.get("requiredAction")),
            "kev_ransomware": clean(v.get("knownRansomwareCampaignUse")),
            "description_orig": clean(v.get("shortDescription")),
            "affected_products": [],
            "references": [],
            "cwe": [],
        })
    print(f"  [KEV] 최근 추가 {len(picked)}건 수집 (피드 전체 {data.get('count', len(vulns))}건)")
    return picked


def fetch_circl(max_cve=CIRCL_EXTRA_LIMIT, feed_size=100):
    """CIRCL 최신 피드에서 CVE 식별자를 가진 항목을 뽑는다 (에코시스템 권고는 aliases 의 CVE 사용)."""
    try:
        feed = http_json(CIRCL_URL.format(n=feed_size), timeout=45, retries=1)
    except Exception as e:  # noqa: BLE001
        print(f"  [CIRCL] 수집 실패: {e}")
        return []
    out, seen = [], set()
    for it in feed:
        cve_ids = []
        rid = str(it.get("id") or "")
        if rid.startswith("CVE-"):
            cve_ids.append(rid)
        for a in it.get("aliases") or []:
            if str(a).startswith("CVE-"):
                cve_ids.append(a)
        if not cve_ids:
            continue
        details = clean(it.get("details") or it.get("summary") or "")
        affected = []
        for aff in it.get("affected") or []:
            pkg = (aff or {}).get("package") or {}
            name = pkg.get("name")
            eco = pkg.get("ecosystem") or ""
            if name:
                affected.append(f"{eco}: {name}" if eco else name)
        refs = []
        for r in (it.get("references") or [])[:6]:
            url = r if isinstance(r, str) else (r or {}).get("url")
            if url:
                refs.append({"url": url, "title": ""})
        for cve_id in cve_ids:
            if cve_id in seen:
                continue
            seen.add(cve_id)
            pub = (it.get("published") or "")[:10]
            try:
                if pub and (now_kst().date() - datetime.strptime(pub, "%Y-%m-%d").date()).days > 45:
                    continue  # 최신 피드에 실린 오래된 CVE는 제외 (별도 공지용)
            except ValueError:
                pass
            out.append({
                "cve_id": cve_id,
                "source": "CIRCL CVE",
                "vendor": "",
                "product": (affected[0].split(": ")[-1] if affected else ""),
                "published_at": (it.get("published") or "")[:10],
                "is_kev": False,
                "description_orig": details,
                "affected_products": affected[:4],
                "references": refs,
                "cwe": [],
            })
            if len(out) >= max_cve:
                break
        if len(out) >= max_cve:
            break
    print(f"  [CIRCL] 최신 피드에서 CVE {len(out)}건 확보")
    return out


def parse_cpe(criteria):
    """cpe:2.3:a:vendor:product:version:... → (vendor, product, version)"""
    parts = (criteria or "").split(":")
    if len(parts) < 6:
        return None
    vendor, product, version = parts[3], parts[4], parts[5]
    if vendor in ("*", "-") and product in ("*", "-"):
        return None
    return (vendor, product, version)


def extract_product_from_desc(desc):
    """NVD 분석 전(CPE 없음) CVE 설명에서 제품명·영향 버전을 추출한다.
    예: 'A security flaw has been discovered in yangzongzhuan RuoYi up to 4.8.3.' → ('yangzongzhuan RuoYi', '4.8.3')
    """
    d = clean(desc)
    if not d:
        return "", ""
    patterns = [
        r"\bin ([A-Za-z][\w:.+\-/]*(?: [A-Za-z0-9_.+\-/]+){0,4}?) (?:up to|before|prior to|through) ([0-9][\w.\-]*)",
        r"^([A-Za-z][\w:.+\-]{1,40}) versions? (?:from [\w.\-]+ )?before ([\w.\-]+)",
        r"\b(?:in|for|of) ([A-Za-z][\w:.+\-/]*(?: [A-Za-z0-9_.+\-/]+){0,4}?) versions? ([0-9][\w.\-]*)",
        r"\bin ([A-Za-z][\w:.+\-/]*(?: [A-Za-z0-9_.+\-/]+){0,4}) version ([vV]?[0-9][\w.\-]*)",
    ]
    for pat in patterns:
        m = re.search(pat, d, re.I)
        if m:
            name, ver = _clean_product_name(m.group(1), m.group(2))
            if len(name) >= 2:
                return name, ver
    # 보조: "A vulnerability in X" / "X < 2.0 allows"
    m = re.search(r"\b(?:vulnerability|flaw|weakness|issue)\s+(?:has been\s+\w+\s+)?in ([A-Za-z][\w:.+\-/]*(?: [A-Za-z0-9_.+\-/]+){0,4})", d, re.I)
    if m:
        name, ver = _clean_product_name(m.group(1), "")
        return name, ver
    return "", ""


def _clean_product_name(name, ver):
    name = (name or "").strip(" .,'\"")
    name = re.split(r"\.\s", name)[0].strip(" .,'\"")
    name = re.sub(r"^(?:the|a|an)\s+", "", name, flags=re.I)
    if not ver:
        m = re.match(r"(.+?)\s+([vV]?[0-9][\w.\-]*)$", name)
        if m:
            name, ver = m.group(1), m.group(2)
    return name, (ver or "").strip(" .,'\"")


def parse_nvd_cve(cve):
    """NVD 응답의 cve 객체 하나를 파이프라인 레코드로 바꾼다 (fetch_nvd·단건 조회 공용)."""
    cve_id = cve.get("id")
    if not cve_id:
        return None
    desc = ""
    for d in cve.get("descriptions") or []:
        if d.get("lang") == "en":
            desc = clean(d.get("value"))
            break
    metrics = cve.get("metrics") or {}
    score, severity = None, "UNKNOWN"
    for key in ("cvssMetricV31", "cvssMetricV40", "cvssMetricV30", "cvssMetricV2"):
        for m in metrics.get(key) or []:
            cd = m.get("cvssData") or {}
            if cd.get("baseScore") is not None:
                score = float(cd["baseScore"])
                severity = (cd.get("baseSeverity") or m.get("baseSeverity") or "").upper() or classify_severity(score)
                break
        if score is not None:
            break
    cwe = []
    for w in cve.get("weaknesses") or []:
        for d in w.get("description") or []:
            v = d.get("value") or ""
            if v.startswith("CWE-") and v not in cwe:
                cwe.append(v)
    vendors, products = {}, []
    for conf in cve.get("configurations") or []:
        for node in conf.get("nodes") or []:
            for cm in node.get("cpeMatch") or []:
                if not cm.get("vulnerable", True):
                    continue
                parsed = parse_cpe(cm.get("criteria"))
                if not parsed:
                    continue
                vendor, product, version = parsed
                key = (vendor, product)
                vendors.setdefault(key, set())
                if version not in ("*", "-"):
                    vendors[key].add(version)
    for (vendor, product), versions in vendors.items():
        vs = sorted(versions)
        label = f"{vendor.title()} {product}"
        if vs:
            shown = ", ".join(vs[:3]) + (" 외" if len(vs) > 3 else "")
            label = f"{label} ({shown})"
        products.append(label)
    if not products:
        # NVD 신규 CVE는 CPE 분석 전(configurations=null)이므로 설명에서 제품·버전을 도출
        name, ver = extract_product_from_desc(desc)
        if name:
            products.append(f"{name} ({ver})" if ver else name)
    refs = []
    for r in (cve.get("references") or [])[:8]:
        url_r = r.get("url")
        if not url_r:
            continue
        tags = r.get("tags") or []
        title = ", ".join(tags[:2]) if tags else ""
        refs.append({"url": url_r, "title": title})
    first = products[0] if products else ""
    vendor = first.split(" ")[0] if first else ""
    return {
        "cve_id": cve_id,
        "source": "NVD",
        "vendor": vendor,
        "product": first,
        "published_at": (cve.get("published") or "")[:10],
        "cvss_score": score,
        "severity": severity,
        "is_kev": False,
        "description_orig": desc,
        "affected_products": products[:8],
        "references": refs,
        "cwe": cwe[:4],
    }


def fetch_nvd_cve(cve_id):
    """NVD 단건 조회 — 경보·기사에서만 확인된 CVE 의 상세를 채울 때 쓴다. 없으면 None."""
    try:
        data = http_json(NVD_CVE_URL.format(cve_id=urllib.parse.quote(cve_id)), timeout=45, retries=1)
    except Exception as e:  # noqa: BLE001
        print(f"  [NVD] {cve_id} 단건 조회 실패: {type(e).__name__}")
        return None
    vulns = data.get("vulnerabilities") or []
    if not vulns:
        return None
    return parse_nvd_cve((vulns[0] or {}).get("cve") or {})


def fetch_nvd(days=NVD_DAYS, limit=NVD_LIMIT):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    url = NVD_URL.format(
        start=start.strftime("%Y-%m-%dT%H:%M:%S.000"),
        end=end.strftime("%Y-%m-%dT%H:%M:%S.000"),
    )
    try:
        data = http_json(url, timeout=90, retries=2)
    except Exception as e:  # noqa: BLE001
        print(f"  [NVD] 수집 실패: {e}")
        return []
    records = []
    for wrap in data.get("vulnerabilities") or []:
        rec = parse_nvd_cve(wrap.get("cve") or {})
        if rec:
            records.append(rec)
    # 최신 공개 우선 + 고위험 우선 정렬 후 상한
    records.sort(key=lambda r: (r.get("severity") == "CRITICAL", r.get("cvss_score") or 0, r.get("published_at") or ""), reverse=True)
    picked = records[:limit]
    print(f"  [NVD] 최근 {days}일 공개 CVE {len(records)}건 중 {len(picked)}건 선별")
    return picked


# ---------------------------------------------------------------------------
# 1-b) 경보·보안 뉴스에서 CVE 캐내기
#   NVD·CIRCL 반영이 늦거나 CISA KEV 등재 전인 긴급 취약점은 피드만으로는 놓친다.
#   (2026-11-18 Java4Shell 사례: CISA 경보·보안 매체는 06:00 공개 직후 보도했지만
#    NVD 반영은 그 뒤였고 KEV 에는 아직 없어 수집 목록에 들어오지 못했다.)
# ---------------------------------------------------------------------------

def feed_date(value):
    """RSS pubDate(RFC822)·Atom(ISO8601) 문자열을 'YYYY-MM-DD' 로 바꾼다. 실패하면 ''."""
    from email.utils import parsedate_to_datetime
    raw = (value or "").strip()
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).astimezone(timezone.utc).strftime("%Y-%m-%d")
    except Exception:  # noqa: BLE001
        pass
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", raw)
    return m.group(0) if m else ""


def parse_feed_items(raw):
    """RSS 2.0·Atom 피드를 [{title, link, summary, published_at}] 로 파싱한다."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    out = []
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        title = link = summary = published = ""
        for child in list(node):
            ctag = child.tag.split("}")[-1]
            if ctag == "title" and not title:
                title = clean(child.text or "")
            elif ctag == "link":
                href = child.get("href")
                if href and child.get("rel") in (None, "alternate") and not link:
                    link = href.strip()
                elif not href and (child.text or "").strip() and not link:
                    link = child.text.strip()
            elif ctag in ("description", "summary", "content", "encoded") and not summary:
                summary = clean(child.text or "")
            elif ctag in ("pubDate", "published", "updated", "date") and not published:
                published = (child.text or "").strip()
        if title and link:
            out.append({"title": title, "link": link, "summary": summary, "published_at": feed_date(published)})
    return out


def _recent(date_str, days):
    if not date_str:
        return True
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except ValueError:
        return True
    return (now_kst().date() - d).days <= days


def cisa_source(url):
    """CISA 피드 항목 URL → (표시 이름, 우선순위). 낮을수록 먼저 수집한다."""
    u = url or ""
    if "/news-events/alerts/" in u:
        return "CISA Alert", 0
    if "/news-events/ics-advisories/" in u:
        return "CISA ICS Advisory", 2
    return "CISA Advisory", 1


def fetch_cisa_items(days=ALERT_FEED_DAYS):
    """CISA Cybersecurity Alerts/Advisories 피드의 최근 항목."""
    try:
        req = urllib.request.Request(CISA_ADVISORY_FEED, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = read_limited(resp, MAX_HTML_BYTES).decode("utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  [CISA] 경보 피드 수집 실패: {type(e).__name__}")
        return []
    items = []
    for it in parse_feed_items(raw):
        if not _recent(it["published_at"], days):
            continue
        source, rank = cisa_source(it["link"])
        it["source"] = source
        it["rank"] = rank
        items.append(it)
    if items:
        alerts = sum(1 for i in items if i["rank"] == 0)
        print(f"  [CISA] 최근 {days}일 피드 {len(items)}건 (경보 {alerts}건)")
    return items


def fetch_news_items(feed):
    """주요 보안 매체 RSS 의 최근 항목."""
    try:
        req = urllib.request.Request(feed["url"], headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml"})
        with urllib.request.urlopen(req, timeout=35) as resp:
            raw = read_limited(resp, MAX_HTML_BYTES).decode("utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  [{feed['name']}] 피드 수집 실패: {type(e).__name__}")
        return []
    items = [it for it in parse_feed_items(raw) if _recent(it["published_at"], feed.get("days", NEWS_CVE_DAYS))]
    for it in items:
        it["source"] = feed["name"]
        it["rank"] = 3
    return items


def fetch_vendor_items(feed):
    """보안기업 피드(RSS). 항목이 수천 건인 피드(MSRC 등)는 cap 으로 앞부분만 본다."""
    try:
        req = urllib.request.Request(feed["url"], headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = read_limited(resp, MAX_HTML_BYTES).decode("utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  [{feed['name']}] 피드 수집 실패: {type(e).__name__}")
        return []
    parsed = parse_feed_items(raw)
    cap = feed.get("cap")
    if cap:
        parsed = parsed[: int(cap)]
    items = [it for it in parsed if _recent(it["published_at"], feed.get("days", NEWS_CVE_DAYS))]
    for it in items:
        it["source"] = feed["name"]
        it["rank"] = feed.get("rank", 3)
    if items:
        print(f"  [{feed['name']}] 최근 {feed.get('days', NEWS_CVE_DAYS)}일 {len(items)}건")
    return items


def fetch_kr_board_items(board):
    """국내 기관 게시판(HTML 표)의 최근 글. 제목에 CVE ID 가 있으면 그대로 단서가 된다.

    KISA 보호나라 게시판은 서버렌더링 표(<td class="sbj"><a href="...view.do...">)로 내려온다.
    """
    try:
        req = urllib.request.Request(board["url"], headers={"User-Agent": UA, "Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=35) as resp:
            raw = read_limited(resp, MAX_HTML_BYTES).decode("utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        print(f"  [{board['name']}] 게시판 수집 실패: {type(e).__name__}")
        return []

    items = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S):
        m = re.search(r'href="([^"]*view\.do[^"]*)"[^>]*>(.*?)</a>', row, re.S)
        if not m:
            continue
        title = clean(html.unescape(re.sub(r"<[^>]+>", "", m.group(2))))
        if not title:
            continue
        href = html.unescape(m.group(1))
        link = urllib.parse.urljoin(board["url"], href)
        dm = re.search(r'(\d{4}-\d{2}-\d{2})', row)
        published = dm.group(1) if dm else ""
        if not _recent(published, board.get("days", NEWS_CVE_DAYS)):
            continue
        items.append({"title": title, "link": link, "summary": title,
                      "published_at": published, "source": board["name"], "rank": board.get("rank", 3)})
    if items:
        print(f"  [{board['name']}] 최근 {board.get('days', NEWS_CVE_DAYS)}일 {len(items)}건")
    return items


def collect_cve_clues():
    """경보·보안 뉴스·기관/기업 피드에서 '이 CVE 가 어디서 언급됐는가'를 모아 cve_id 별로 묶는다."""
    items = fetch_cisa_items()
    for feed in NEWS_CVE_FEEDS:
        items.extend(fetch_news_items(feed))
    for feed in VENDOR_CVE_FEEDS:
        items.extend(fetch_vendor_items(feed))
    for board in KR_INSTITUTION_BOARDS:
        items.extend(fetch_kr_board_items(board))
    clues = {}
    for it in items:
        blob = " ".join([it.get("title", ""), it.get("summary", "")])
        ids = list(dict.fromkeys(CVE_ID_RE.findall(blob)))
        for cve_id in ids:
            clues.setdefault(cve_id, []).append({
                "cve_id": cve_id,
                "source": it["source"],
                "title": it.get("title", ""),
                "url": it.get("link", ""),
                "published_at": it.get("published_at", ""),
                "summary": clean(it.get("summary", ""), 1200),
                "rank": it.get("rank", 3),
            })
    for cve_id, rows in clues.items():
        rows.sort(key=lambda r: (r["rank"], r["published_at"]), reverse=False)
        # rank 우선, 같은 rank 안에서는 최신 발행 우선
        rows.sort(key=lambda r: r["published_at"], reverse=True)
        rows.sort(key=lambda r: r["rank"])
    with_alert = sum(1 for rows in clues.values() if any(r["rank"] == 0 for r in rows))
    print(f"  [경보] CISA·보안 뉴스에서 CVE {len(clues)}건 확인 (CISA 경보 언급 {with_alert}건)")
    return clues


def clue_rows(clues):
    """cve_alerts 테이블에 적재할 평평한 단서 목록."""
    rows = []
    for cve_id, items in clues.items():
        for it in items:
            rows.append({
                "cve_id": cve_id,
                "source": it["source"],
                "title": it["title"],
                "url": it["url"],
                "published_at": it["published_at"],
                "summary": it["summary"],
            })
    return rows


def build_alert_records(clues, known_ids, limit=ALERT_CANDIDATE_LIMIT):
    """경보·기사에서만 확인된 CVE 를 수집 후보로 만든다.

    ① NVD 단건 조회 → ② CIRCL 상세 → ③ 경보·기사 메타데이터만으로 기본 레코드.
    (NVD·CIRCL 에 아직 없더라도 그날 바로 리포트에 세우기 위한 마지막 단계)
    """
    candidates = [(cid, rows) for cid, rows in clues.items() if cid not in known_ids]
    candidates.sort(key=lambda kv: (kv[1][0]["rank"], kv[1][0]["published_at"]), reverse=False)
    candidates = candidates[:limit]
    if not candidates:
        return []
    print(f"  [경보] NVD·KEV·CIRCL 에 없는 후보 CVE {len(candidates)}건 상세 보강 시도")
    out = []
    for cve_id, rows in candidates:
        rec = fetch_nvd_cve(cve_id)
        if not rec:
            detail = fetch_circl_detail(cve_id)
            if detail:
                rec = {
                    "cve_id": cve_id,
                    "source": "CIRCL CVE",
                    "vendor": detail.get("vendor", ""),
                    "product": detail.get("product", ""),
                    "published_at": rows[0]["published_at"],
                    "cvss_score": detail.get("cvss_score"),
                    "severity": detail.get("severity") or "UNKNOWN",
                    "is_kev": False,
                    "description_orig": detail.get("description_orig", ""),
                    "affected_products": detail.get("affected_products", []),
                    "references": detail.get("references", []),
                    "cwe": detail.get("cwe", []),
                }
        if not rec:
            top = rows[0]
            print(f"  [경보] {cve_id} — NVD·CIRCL 미등록, 기사·경보 메타데이터로 기본 레코드 생성 ({top['source']})")
            rec = {
                "cve_id": cve_id,
                "source": top["source"],
                "vendor": "",
                "product": "",
                "published_at": top["published_at"],
                "cvss_score": None,
                "severity": "UNKNOWN",
                "is_kev": False,
                "description_orig": top["summary"] or top["title"],
                "affected_products": [],
                "references": [],
                "cwe": [],
            }
        # 경보·기사 링크를 참고 자료에 남긴다 (중복 URL 은 한 번만)
        refs = list(rec.get("references") or [])
        seen = {r.get("url") for r in refs if isinstance(r, dict)}
        for it in rows[:3]:
            if it["url"] and it["url"] not in seen:
                refs.append({"url": it["url"], "title": it["title"]})
                seen.add(it["url"])
        rec["references"] = refs[:10]
        if not rec.get("published_at"):
            rec["published_at"] = rows[0]["published_at"]
        out.append(rec)
        time.sleep(0.4)
    return out


def fetch_epss(cve_ids):
    scores = {}
    ids = list(dict.fromkeys([c for c in cve_ids if c]))
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        url = EPSS_URL.format(ids=",".join(chunk))
        try:
            data = http_json(url, timeout=45, retries=1)
        except Exception as e:  # noqa: BLE001
            print(f"  [EPSS] 조회 실패({len(chunk)}건): {e}")
            continue
        for row in data.get("data") or []:
            try:
                scores[row["cve"]] = (float(row["epss"]), float(row.get("percentile") or 0))
            except (KeyError, TypeError, ValueError):
                continue
        time.sleep(0.6)
    print(f"  [EPSS] 악용 확률 {len(scores)}건 병합")
    return scores


def gh_available():
    try:
        r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=20)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def fetch_poc(cve_id, use_gh=True, aliases=None):
    """GitHub 공개 PoC 저장소 조회. gh CLI 인증(분당 30회) → 없으면 무인증(분당 10회).

    aliases: 취약점 별칭(예: 'nginx2root'). CVE ID 로 0건이면 별칭으로 한 번 더 찾는다.
    """
    out = _fetch_poc_query(cve_id, use_gh)
    if isinstance(out, list) and not out and aliases:
        for alias in aliases:
            alt = _fetch_poc_query(alias, use_gh)
            if isinstance(alt, list):
                out.extend(alt)
            if out:
                break
    return out


def _fetch_poc_query(query, use_gh=True):
    q = urllib.parse.quote(query)
    if use_gh:
        try:
            r = subprocess.run(
                ["gh", "api", f"search/repositories?q={cve_id}+in:name,description&sort=stars&per_page=3",
                 "--jq", "[.items[] | {name: .full_name, url: .html_url, stars: .stargazers_count, description: (.description // \"\"), updated: (.updated_at // \"\")}]"],
                capture_output=True, text=True, timeout=45)
            if r.returncode == 0:
                return json.loads(r.stdout or "[]")
            if "rate limit" in (r.stderr or "").lower():
                time.sleep(30)
            return None
        except Exception:  # noqa: BLE001
            return None
    try:
        data = http_json(GH_SEARCH_URL.format(q=q), timeout=45, retries=0)
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return "RATE_LIMIT"
        return None
    except Exception:  # noqa: BLE001
        return None
    out = []
    for it in (data.get("items") or [])[:3]:
        out.append({
            "name": it.get("full_name"),
            "url": it.get("html_url"),
            "stars": it.get("stargazers_count") or 0,
            "description": clean(it.get("description"), 160),
            "updated": (it.get("updated_at") or "")[:10],
        })
    return out


def collect_pocs(records, cache):
    """KEV 전체 + 고위험 비-KEV 순으로 PoC 조회 (12시간 캐시 재사용)

    원칙: 이번 실행에서 실제로 새로 조회해 링크를 얻지 못한 CVE 는
    기존 캐시(cve_cache.json)의 PoC 를 그대로 유지한다. 빈 배열로 덮어써서
    이미 확보한 공개 PoC 를 잃지 않게 하기 위함이다.
    """
    use_gh = gh_available()
    delay = 2.4 if use_gh else 7.0

    # 0) 조회 대상에서 빠지는 항목(POC_QUERY_LIMIT 밖)도 캐시 PoC 를 먼저 복원
    for rec in records:
        if rec.get("poc_links"):
            continue
        seeded = (cache["poc"].get(rec["cve_id"]) or {}).get("links") or []
        if seeded:
            rec["poc_links"] = list(seeded)

    ordered = sorted(records, key=lambda r: (not r.get("is_kev"), -(r.get("cvss_score") or 0), -(r.get("epss_score") or 0)))
    targets = ordered[:POC_QUERY_LIMIT]
    fetched = 0
    rate_limited = False
    now_naive = now_kst().replace(tzinfo=None)
    for rec in targets:
        cve_id = rec["cve_id"]
        cached = cache["poc"].get(cve_id)
        cached_links = (cached or {}).get("links") or []
        if cached and cached.get("fetched_at"):
            ts = parse_cache_time(cached["fetched_at"])
            if ts is not None and (now_naive - ts) < timedelta(hours=12):
                rec["poc_links"] = cached_links
                continue
        if rate_limited:
            rec["poc_links"] = rec.get("poc_links") or cached_links
            continue
        res = fetch_poc(cve_id, use_gh=use_gh, aliases=POC_ALIASES.get(cve_id))
        if res == "RATE_LIMIT" or res is None:
            # gh 실패 → 다음 항목부터는 딜레이를 늘려 재시도
            rec["poc_links"] = rec.get("poc_links") or cached_links
            time.sleep(10)
            res2 = fetch_poc(cve_id, use_gh=use_gh, aliases=POC_ALIASES.get(cve_id))
            if res2 in (None, "RATE_LIMIT"):
                rate_limited = True
                print(f"  [GitHub] {cve_id} 조회 실패 — 이후 조회는 캐시값으로 유지")
                continue
            res = res2
        if res:
            rec["poc_links"] = res
            cache["poc"][cve_id] = {"fetched_at": now_str(), "links": rec["poc_links"]}
            save_cache(cache)
            fetched += 1
        else:
            # 조회는 됐지만 0건 → 기존에 확보한 링크가 있으면 유지(캐시도 덮지 않는다)
            rec["poc_links"] = rec.get("poc_links") or cached_links
        time.sleep(delay)
    print(f"  [GitHub] PoC 조회 {fetched}건 완료 (대상 {len(targets)}건, {'gh 인증' if use_gh else '무인증'})")
    print(f"  [GitHub] PoC 보유 {sum(1 for r in records if r.get('poc_links'))}건 / 링크 {sum(len(r.get('poc_links') or []) for r in records)}개")


# ---------------------------------------------------------------------------
# 2) 한국어 폴백 (EXAONE 실패 대비)
# ---------------------------------------------------------------------------

VULN_TYPES = [
    ("원격 코드 실행", r"remote code execution|\brce\b|execute arbitrary code|arbitrary code execution"),
    ("명령어 주입", r"command injection|os command|shell command|command execution|inject[^.]{0,60}commands?"),
    ("SQL 주입", r"sql injection|\bsqli\b"),
    ("크로스사이트 스크립팅", r"cross[- ]site scripting|\bxss\b"),
    ("인증 우회", r"authentication bypass|auth(?:entication)? bypass|improper authentication|missing authentication|bypass authentication"),
    ("권한 상승", r"privilege escalation|elevation of privilege|escalate privileges"),
    ("경로 순회", r"path traversal|directory traversal|arbitrary file read"),
    ("역직렬화", r"deserializ|unsafe deserialization"),
    ("파일 업로드", r"unrestricted file upload|arbitrary file upload|malicious file upload"),
    ("정보 노출", r"information disclosure|sensitive information|exposure of|information leak|data leak"),
    ("서비스 거부", r"denial of service|\bDoS\b|resource exhaustion|infinite loop"),
    ("메모리 손상", r"buffer overflow|out[- ]of[- ]bounds|use[- ]after[- ]free|heap overflow|stack overflow|memory corruption|double free"),
    ("요청 위조", r"server[- ]side request forgery|\bSSRF\b|cross[- ]site request forgery|\bCSRF\b"),
    ("접근 제어 미흡", r"improper access control|authorization bypass|insecure direct object|missing authorization|permission"),
]

IMPACT_KO = {
    "원격 코드 실행": "공격자가 원격에서 임의 코드를 실행해 서버를 완전히 장악하고, 내부 데이터 유출·추가 침해의 발판으로 삼을 수 있습니다.",
    "명령어 주입": "조작된 입력으로 서버 명령을 실행할 수 있어 시스템 장악과 데이터 유출로 이어질 수 있습니다.",
    "SQL 주입": "데이터베이스 조회·변조·삭제가 가능해 계정 정보와 주요 데이터가 유출될 수 있습니다.",
    "크로스사이트 스크립팅": "로그인 사용자의 세션을 탈취하거나 악성 스크립트를 실행시켜 관리자 권한을 노릴 수 있습니다.",
    "인증 우회": "인증 없이 보호된 기능·관리 화면에 접근해 설정 변경과 데이터 조회가 가능합니다.",
    "권한 상승": "낮은 권한의 사용자가 관리자 수준 권한을 얻어 시스템 전반을 통제할 수 있습니다.",
    "경로 순회": "서버 파일 시스템의 중요 파일을 읽거나 조작해 설정·자격 증명이 노출될 수 있습니다.",
    "역직렬화": "신뢰할 수 없는 데이터가 역직렬화되면서 원격 코드 실행으로 이어질 수 있습니다.",
    "파일 업로드": "악성 파일 업로드를 통해 웹셸 실행이나 서버 장악이 가능합니다.",
    "정보 노출": "민감 정보가 외부에 노출되어 추가 공격의 단서가 되거나 개인정보 침해로 이어질 수 있습니다.",
    "서비스 거부": "반복 요청으로 서비스 응답이 멈추거나 지연되어 정상 사용자가 서비스를 이용하지 못합니다.",
    "메모리 손상": "메모리 오류를 악용해 서비스가 중단되거나 원격 코드 실행으로 이어질 수 있습니다.",
    "요청 위조": "서버가 내부 자원에 접근하도록 유도해 내부 서비스 정보 노출이나 요청 변조가 가능합니다.",
    "접근 제어 미흡": "권한 없는 사용자가 다른 사용자의 데이터나 관리 기능에 접근할 수 있습니다.",
}

TYPE_HINT = {
    "원격 코드 실행": "원격 코드 실행(RCE)",
    "명령어 주입": "명령어 주입",
    "SQL 주입": "SQL 주입",
    "크로스사이트 스크립팅": "XSS",
    "인증 우회": "인증 우회",
    "권한 상승": "권한 상승",
    "경로 순회": "경로 순회",
    "역직렬화": "역직렬화",
    "파일 업로드": "파일 업로드",
    "정보 노출": "정보 노출",
    "서비스 거부": "서비스 거부(DoS)",
    "메모리 손상": "메모리 손상",
    "요청 위조": "요청 위조",
    "접근 제어 미흡": "접근 제어 미흡",
}


def guess_vuln_type(rec):
    blob = " ".join([rec.get("description_orig", ""), rec.get("product", ""),
                     " ".join(rec.get("affected_products") or []), " ".join(rec.get("cwe") or [])])
    cwe_map = {"CWE-78": "명령어 주입", "CWE-77": "명령어 주입", "CWE-94": "원격 코드 실행",
               "CWE-787": "메모리 손상", "CWE-125": "메모리 손상", "CWE-416": "메모리 손상",
               "CWE-89": "SQL 주입", "CWE-79": "크로스사이트 스크립팅", "CWE-22": "경로 순회",
               "CWE-287": "인증 우회", "CWE-306": "인증 우회", "CWE-269": "권한 상승",
               "CWE-502": "역직렬화", "CWE-434": "파일 업로드", "CWE-200": "정보 노출",
               "CWE-918": "요청 위조", "CWE-352": "요청 위조", "CWE-862": "접근 제어 미흡",
               "CWE-863": "접근 제어 미흡", "CWE-284": "접근 제어 미흡"}
    for c in rec.get("cwe") or []:
        if c in cwe_map:
            return cwe_map[c]
    for label, pat in VULN_TYPES:
        if re.search(pat, blob, re.I):
            return label
    return "보안 취약점"


def product_label(rec):
    prod = clean(rec.get("product") or "")
    vendor = clean(rec.get("vendor") or "")
    if vendor.lower() in ("unknown", "n/a", "none"):
        vendor = ""
    prod = re.sub(r"^(?:unknown|n/a)\s+", "", prod, flags=re.I)
    if prod.lower() in ("multiple products", "multiple products and versions", "multiple", "various"):
        affected = rec.get("affected_products") or []
        if affected:
            first = re.split(r"\s*\(", affected[0])[0].strip()
            if first:
                return first
        return f"{vendor} 제품군" if vendor else "복수 제품"
    if prod and vendor:
        if vendor.lower() in prod.lower() or prod.lower() in vendor.lower():
            return prod
        return f"{vendor} {prod}"
    if prod:
        return prod
    if vendor:
        return vendor
    affected = rec.get("affected_products") or []
    return affected[0] if affected else "영향 제품"


def action_ko(action):
    a = (action or "").strip()
    if not a:
        return ""
    low = a.lower()
    if "discontinue use" in low and "mitigations" in low:
        return "벤더가 안내하는 완화 조치를 적용하고, 완화 조치가 없으면 해당 제품의 사용을 중단해야 합니다."
    if low.startswith("apply updates"):
        return "벤더가 제공하는 보안 업데이트를 가능한 한 빠르게 적용해야 합니다."
    if low.startswith("apply mitigations") or "mitigations" in low:
        return "벤더가 안내하는 완화 조치를 적용하고, 패치가 제공되면 최신 버전으로 업데이트해야 합니다."
    if "update" in low or "patch" in low:
        return "벤더의 보안 패치를 적용해야 합니다."
    return "벤더가 안내하는 조치를 확인해 적용해야 합니다."


def fallback_korean(rec, reason=""):
    """EXAONE 실패 시 제품·CVSS·CISA 권고·취약점 유형으로 한국어 문구를 구성한다."""
    vtype = guess_vuln_type(rec)
    label = clean(product_label(rec), 70)
    if label and label[0].islower() and len(label.split()[0]) <= 14:
        label = label[0].upper() + label[1:]
    sev = rec.get("severity") or "UNKNOWN"
    cvss = rec.get("cvss_score")
    epss = rec.get("epss_score")
    if vtype == "보안 취약점":
        title = f"{label} 보안 취약점".strip()
    else:
        title = f"{label} {TYPE_HINT.get(vtype, '취약점')} 취약점".strip()
    title = re.sub(r"\s+", " ", title)[:110]

    bits = []
    if rec.get("is_kev"):
        bits.append(f"{rec['cve_id']}는 CISA가 실제 공격 악용 정황을 확인해 KEV 목록에 등재한 {label}의 {TYPE_HINT.get(vtype, '보안')} 취약점입니다.")
    else:
        bits.append(f"{rec['cve_id']}는 {label}에서 확인된 {TYPE_HINT.get(vtype, '보안')} 취약점입니다.")
    if cvss is not None:
        bits.append(f"CVSS {cvss:g}점({SEVERITY_KO.get(sev, '미평가')})으로 평가됐습니다.")
    if epss is not None:
        pct = rec.get("epss_percentile")
        pct_txt = ""
        if pct is not None:
            top = max(1, round((1 - pct) * 100))
            pct_txt = f"(악용 위험 상위 {top}% 수준)"
        bits.append(f"향후 30일 내 악용될 확률(EPSS)은 {epss * 100:.1f}%{pct_txt}입니다.")
    if rec.get("kev_date_added"):
        bits.append(f"CISA는 {rec['kev_date_added']}에 이 취약점을 알려진 악용 목록에 추가했습니다.")
    summary_ko = " ".join(bits)

    impact = IMPACT_KO.get(vtype, "취약점이 악용되면 시스템 기밀성·무결성이 훼손될 수 있습니다.")
    if rec.get("is_kev"):
        impact += " 실제 악용 사례가 확인된 만큼 인터넷에 노출된 자산은 즉시 영향 여부를 확인해야 합니다."
    if rec.get("kev_ransomware") and rec["kev_ransomware"].lower().startswith("known"):
        impact += " 랜섬웨어 캠페인에서의 악용도 알려져 있습니다."

    steps = []
    act = action_ko(rec.get("kev_required_action"))
    if act:
        steps.append(act)
    # 수집 원문에 적힌 수정 버전 기준을 찾아 구체적으로 안내 (커밋 해시 등 버전이 아닌 값은 제외)
    fixed_list = []
    for p in rec.get("affected_products") or []:
        for m in re.finditer(r"<\s*([0-9][\w.\-]*)", p):
            v = m.group(1)
            if re.fullmatch(r"[0-9a-f]{12,}", v):
                continue
            if v not in fixed_list:
                fixed_list.append(v)
    if not fixed_list:
        m = re.search(r"(?:fixed|resolved|patched|corrected|addressed) (?:in|by) (?:version |v)?([0-9][\w.\-]*)", rec.get("description_orig", ""), re.I)
        if m:
            fixed_list.append(m.group(1))
    fixed = "·".join(fixed_list[:3])
    if fixed:
        steps.append(f"영향 범위는 {fixed} 미만 버전이며, 자산 목록과 대조해 {fixed} 이상 버전으로 업데이트하면 해결됩니다.")
    else:
        steps.append("영향받는 제품·버전을 자산 목록에서 확인하고, 벤더 보안 공지의 수정 버전으로 업데이트하세요.")
    if rec.get("kev_due_date"):
        steps.append(f"CISA는 {rec['kev_due_date']}까지 조치를 완료하도록 권고하고 있습니다.")
    steps.append("인터넷에 직접 노출된 서비스는 접근 제어·WAF 차단 등 임시 완화 조치를 함께 적용하고, 침해 흔적 점검을 병행하세요.")
    remediation_ko = " ".join(f"{chr(0x2460 + i)} {s}" for i, s in enumerate(steps[:4]))

    return {
        "title_ko": title,
        "summary_ko": summary_ko,
        "impact_ko": impact,
        "remediation_ko": remediation_ko,
        "analyzed_by": f"fallback:{reason}" if reason else "fallback",
    }


# ---------------------------------------------------------------------------
# 3) EXAONE 분석
# ---------------------------------------------------------------------------

AI_SYSTEM_PROMPT = (
    "당신은 정보보안 취약점 분석가입니다. CVE 정보를 읽고 실무자가 바로 참고할 수 있는 한국어 분석을 작성합니다. "
    "제공된 사실만 사용하고 추측하지 않으며, 반드시 지정된 JSON 배열만 출력합니다."
)


def build_ai_prompt(batch):
    lines = []
    for i, r in enumerate(batch, 1):
        kev = "KEV 실제 악용 등재"
        if r.get("kev_date_added"):
            kev += f" ({r['kev_date_added']}"
            if r.get("kev_due_date"):
                kev += f", 조치기한 {r['kev_due_date']}"
            kev += ")"
        epss = ""
        if r.get("epss_score") is not None:
            epss = f"{r['epss_score'] * 100:.1f}%"
            if r.get("epss_percentile"):
                epss += f" (상위 {round(r['epss_percentile'] * 100)}%)"
        prod = product_label(r)
        affected = "; ".join((r.get("affected_products") or [])[:4])
        lines.append(
            f"{i}) {r['cve_id']} | 제품: {prod}"
            + (f" | 영향 버전: {affected}" if affected else "")
            + f" | CVSS: {r.get('cvss_score') if r.get('cvss_score') is not None else '미평가'} ({r.get('severity') or 'UNKNOWN'})"
            + (f" | EPSS: {epss}" if epss else "")
            + f" | {'KEV: ' + kev if r.get('is_kev') else 'KEV: 미등재'}"
            + (f" | CISA 권고: {r['kev_required_action']}" if r.get("kev_required_action") else "")
            + (f" | CWE: {', '.join(r.get('cwe') or [])}" if r.get("cwe") else "")
            + f" | 설명: {clean(r.get('description_orig'), 900)}"
        )
    return (
        "다음 CVE 취약점들을 한국어로 분석해 JSON 배열로만 답하세요. 입력 개수와 같은 순서로 작성합니다.\n"
        "형식: [{\"cve_id\":\"CVE-...\",\"title_ko\":\"...\",\"summary_ko\":\"...\",\"impact_ko\":\"...\",\"remediation_ko\":\"...\"}]\n"
        "작성 규칙:\n"
        "- title_ko: 45자 이내. '제품명 + 취약점 유형' 형태 (예: \"PAN-OS GlobalProtect 명령어 주입 취약점\"). 영문 제품명은 그대로 둡니다.\n"
        "- summary_ko: 2~3문장, 200~330자. 무엇이 문제이고 어떤 조건에서 악용되는지.\n"
        "- impact_ko: 공격 성공 시 영향(데이터 유출, 권한 탈취, 서비스 중단 등) 1~2문장.\n"
        "- remediation_ko: 실무 조치 2~3개를 '① … ② …' 형태의 한 문단으로. CISA 권고가 있으면 우선 반영하고, 확인되지 않은 패치 버전은 추측하지 않습니다. 인터넷 노출 자산 우선 점검을 포함합니다.\n"
        "- 모든 문장은 한국어. 영문 고유명사·버전·CVE ID만 영문 유지. 과장·추측 금지.\n\n"
        "입력:\n" + "\n".join(lines)
    )


def call_exaone(prompt, api_key, max_tokens=2600, timeout=180):
    payload = {
        "model": "k-exaone_v2.5",
        "messages": [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
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
        data = json.loads(read_limited(resp).decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def parse_ai_json(text):
    if not text:
        return []
    t = text.strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    m = re.search(r"\[[\s\S]*\]", t)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def src_hash(rec):
    blob = "|".join([rec.get("cve_id", ""), rec.get("description_orig", ""), str(rec.get("cvss_score")),
                     str(rec.get("is_kev")), rec.get("kev_required_action", ""), product_label(rec)])
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def analyze_records(records, cache, ai_limit=None, budget=AI_TIME_BUDGET, patient=False):
    key = get_api_key()
    if not key:
        print("  [EXAONE] API 키 없음 — 한국어 폴백으로 구성")
        for r in records:
            r.update(fallback_korean(r, "nokey"))
        return

    todo = []
    for r in records:
        h = src_hash(r)
        cached = cache["analysis"].get(r["cve_id"])
        if cached and cached.get("hash") == h and cached.get("title_ko"):
            r.update({k: cached[k] for k in ("title_ko", "summary_ko", "impact_ko", "remediation_ko")})
            r["analyzed_by"] = cached.get("analyzed_by", "cache")
            continue
        r["_hash"] = h
        todo.append(r)

    if ai_limit:
        todo = todo[:int(ai_limit)]
        # 이번 실행에서 다루지 않는 항목은 기존 캐시/폴백 유지
        rest = [r for r in records if r not in todo and "_hash" in r]
        for r in rest:
            cached = cache["analysis"].get(r["cve_id"])
            if cached and cached.get("title_ko"):
                r.update({k: cached[k] for k in ("title_ko", "summary_ko", "impact_ko", "remediation_ko")})
                r["analyzed_by"] = cached.get("analyzed_by", "cache")
            else:
                r.update(fallback_korean(r, "pending"))

    print(f"  [EXAONE] 분석 대상 {len(todo)}건 (캐시 재사용 {len(records) - len(todo)}건)")
    started = time.time()
    done = 0
    consec_fail = 0
    for i in range(0, len(todo), AI_BATCH):
        if time.time() - started > budget:
            print(f"  [EXAONE] 시간 예산({budget}s) 초과 — 남은 {len(todo) - i}건은 폴백 처리")
            for r in todo[i:]:
                r.update(fallback_korean(r, "budget"))
            break
        batch = todo[i:i + AI_BATCH]
        prompt = build_ai_prompt(batch)
        # 배치가 클수록 출력이 길어져 2600 토큰에서 JSON이 잘리던 문제 → 건당 여유를 두고 상한을 올린다
        max_tokens = min(8192, 1400 * len(batch) + 600)
        content = None
        for attempt, wait in enumerate((0, 8, 20, 40)):
            if wait:
                time.sleep(wait)
            try:
                content = call_exaone(prompt, key, max_tokens=max_tokens)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504):
                    print(f"  [EXAONE] {e.code} — {wait or 15}s 후 재시도 ({len(batch)}건 배치)")
                    content = None
                    continue
                print(f"  [EXAONE] HTTP {e.code} — 폴백 전환")
                content = None
                break
            except Exception as e:  # noqa: BLE001
                print(f"  [EXAONE] 호출 실패({type(e).__name__}) — 재시도")
                content = None
                continue
        parsed = {str(x.get("cve_id")): x for x in parse_ai_json(content) if isinstance(x, dict)}
        batch_ok = 0
        for r in batch:
            got = parsed.get(r["cve_id"])
            ok = got and got.get("title_ko") and got.get("summary_ko") and got.get("remediation_ko")
            if ok:
                r["title_ko"] = clean(got.get("title_ko"), 90)
                r["summary_ko"] = clean(got.get("summary_ko"), 700)
                r["impact_ko"] = clean(got.get("impact_ko"), 500)
                r["remediation_ko"] = clean(got.get("remediation_ko"), 700)
                r["analyzed_by"] = "exaone"
                cache["analysis"][r["cve_id"]] = {
                    "hash": r["_hash"],
                    "title_ko": r["title_ko"],
                    "summary_ko": r["summary_ko"],
                    "impact_ko": r["impact_ko"],
                    "remediation_ko": r["remediation_ko"],
                    "analyzed_by": "exaone",
                    "analyzed_at": now_str(),
                }
                done += 1
                batch_ok += 1
            else:
                r.update(fallback_korean(r, "ai-fail"))
        save_cache(cache)
        print(f"  [EXAONE] {min(i + AI_BATCH, len(todo))}/{len(todo)} 처리 (성공 누적 {done}건)")
        # 연속 실패(혼잡)가 이어지면 남은 항목은 폴백으로 마감하고, 추후 --ai-only 로 재시도
        consec_fail = 0 if batch_ok else consec_fail + 1
        if consec_fail >= 2 and not patient:
            remain = todo[i + AI_BATCH:]
            if remain:
                print(f"  [EXAONE] 혼잡으로 연속 실패 — 남은 {len(remain)}건은 폴백 처리 (추후 --ai-only 재분석)")
                for r in remain:
                    r.update(fallback_korean(r, "busy"))
            break
        time.sleep(1.5)
    print(f"  [EXAONE] 최종 EXAONE 분석 {done}건 / 폴백 {len(todo) - done}건")


# ---------------------------------------------------------------------------
# 3-b) 사람이 검증한 한국어 분석 (cve_curated.json)
#   AI 분석·폴백보다 우선한다. 다음 날 자동 수집이 같은 CVE 를 다시 가져와도
#   (설명문·CVSS 가 바뀌어 캐시 해시가 달라져도) 검증된 문장이 되돌아가지 않게 한다.
# ---------------------------------------------------------------------------

def load_curated():
    if not os.path.exists(CURATED_FILE):
        return {}
    try:
        with open(CURATED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:  # noqa: BLE001
        print(f"  [수동] cve_curated.json 읽기 실패: {type(e).__name__}")
        return {}


def ensure_curated_reports():
    """cve_curated.json 에만 있고 DB 에는 아직 없는 CVE 를 적재한다.

    수동 검증 항목(예: 공개 당일 수집 전인 NGINX2Root 5종)을 자동 수집을 기다리지 않고
    바로 사이트에 올리기 위한 경로다. 이미 있는 CVE 는 건드리지 않는다(apply_curated 담당).
    """
    curated = load_curated()
    if not curated:
        return 0
    existing = {r.get("cve_id") for r in get_cve_reports()}
    new_records = []
    for cve_id, c in curated.items():
        if not isinstance(c, dict) or cve_id in existing:
            continue
        if not (c.get("title_ko") and c.get("summary_ko")):
            continue
        new_records.append({
            "cve_id": cve_id,
            "title_ko": c["title_ko"],
            "summary_ko": c["summary_ko"],
            "impact_ko": c.get("impact_ko", ""),
            "remediation_ko": c.get("remediation_ko", ""),
            "cvss_score": c.get("cvss_score"),
            "severity": c.get("severity", "UNKNOWN"),
            "epss_score": c.get("epss_score"),
            "epss_percentile": c.get("epss_percentile"),
            "is_kev": bool(c.get("is_kev")),
            "kev_date_added": c.get("kev_date_added", ""),
            "kev_due_date": c.get("kev_due_date", ""),
            "kev_required_action": c.get("kev_required_action", ""),
            "kev_ransomware": c.get("kev_ransomware", ""),
            "vendor": c.get("vendor", ""),
            "product": c.get("product", ""),
            "affected_products": c.get("affected_products", []),
            "poc_links": c.get("poc_links", []),
            "references": c.get("references", []),
            "cwe": c.get("cwe", []),
            "description_orig": c.get("description_orig", ""),
            "published_at": c.get("published_at", ""),
            "analyzed_by": "curated",
        })
    if not new_records:
        return 0
    count = upsert_cve_reports(new_records)
    print(f"  [수동] cve_curated.json 신규 {count}건 적재: {', '.join(r['cve_id'] for r in new_records)}")
    return count


def apply_curated(records):
    """원문 대조로 직접 작성한 분석을 최종값으로 적용한다."""
    curated = load_curated()
    if not curated:
        return 0
    applied = 0
    for r in records:
        c = curated.get(r.get("cve_id"))
        if not isinstance(c, dict):
            continue
        for k in ("title_ko", "summary_ko", "impact_ko", "remediation_ko"):
            if c.get(k):
                r[k] = c[k]
        if c.get("cvss_score") is not None:
            r["cvss_score"] = c["cvss_score"]
        if c.get("severity"):
            r["severity"] = c["severity"]
        for k in ("vendor", "product", "cwe", "affected_products"):
            if c.get(k):
                r[k] = c[k]
        if c.get("poc_links"):
            # 공개 PoC 목록은 GitHub 검색이 놓칠 때를 대비해 검증된 항목을 앞에 붙인다
            seen = set()
            pocs = []
            for poc in list(c["poc_links"]) + list(r.get("poc_links") or []):
                url = (poc or {}).get("url") if isinstance(poc, dict) else poc
                if not url or url in seen:
                    continue
                seen.add(url)
                pocs.append(poc if isinstance(poc, dict) else {"name": url, "url": url, "stars": 0})
            r["poc_links"] = pocs
            r["poc_count"] = len(pocs)
        if c.get("references"):
            seen = set()
            refs = []
            for ref in list(c["references"]) + list(r.get("references") or []):
                url = ref.get("url") if isinstance(ref, dict) else ref
                if not url or url in seen:
                    continue
                seen.add(url)
                refs.append(ref if isinstance(ref, dict) else {"url": ref, "title": ""})
            r["references"] = refs[:10]
        r["analyzed_by"] = "curated"
        applied += 1
    if applied:
        print(f"  [수동] 원문 대조로 검증한 한국어 분석 {applied}건 우선 적용")
    return applied


# ---------------------------------------------------------------------------
# 4) 메인
# ---------------------------------------------------------------------------

def merge_records(*groups):
    """수집 소스 그룹들을 CVE 기준으로 합친다. 앞 그룹(KEV)의 값이 우선하고 뒤 그룹은 빈 칸만 보강한다."""
    merged = {}
    order = []
    for group in groups:
        for r in group:
            cid = r["cve_id"]
            if cid in merged:
                cur = merged[cid]
                # KEV 정보가 우선, 나머지는 빈 필드만 보강
                for k, v in r.items():
                    if k in ("is_kev", "kev_date_added", "kev_due_date", "kev_required_action", "kev_ransomware"):
                        if v:
                            cur[k] = v
                    elif not cur.get(k) and v:
                        cur[k] = v
                    elif k == "affected_products" and v and len(v) > len(cur.get(k) or []):
                        cur[k] = v
                continue
            merged[cid] = dict(r)
            order.append(cid)
    return [merged[c] for c in order]


def fetch_circl_detail(cve_id):
    """CIRCL 개별 CVE 레코드(CVE 5.x)에서 CVSS·설명·제품·CWE·참고 링크를 보강한다.
    KEV 항목은 CVSS·제품 버전이 피드에 없어 이 보강이 필요하다."""
    try:
        d = http_json(f"https://cve.circl.lu/api/cve/{cve_id}", timeout=25, retries=1)
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(d, dict):
        return None
    cna = ((d.get("containers") or {}).get("cna") or {})
    out = {}

    metrics = cna.get("metrics") or []
    for m in metrics:
        for key in ("cvssV4_0", "cvssV3_1", "cvssV3_0", "cvssV2_0"):
            cd = m.get(key)
            if isinstance(cd, dict) and cd.get("baseScore") is not None:
                out["cvss_score"] = float(cd["baseScore"])
                out["severity"] = (cd.get("baseSeverity") or "").upper() or classify_severity(cd["baseScore"])
                break
        if out.get("cvss_score") is not None:
            break

    descs = cna.get("descriptions") or []
    for de in descs:
        if de.get("lang") == "en" and de.get("value"):
            out["description_orig"] = clean(de["value"])
            break

    prods, vendor, product = [], "", ""
    for aff in cna.get("affected") or []:
        v = clean(aff.get("vendor") or "")
        p = clean(aff.get("product") or "")
        if not p:
            continue
        if not product:
            vendor, product = v, p
        vers = []
        for ver in aff.get("versions") or []:
            if ver.get("lessThan"):
                vers.append("< " + str(ver["lessThan"]))
            elif ver.get("version") and str(ver["version"]) not in ("0", "*", "-", "N/A", "n/a"):
                vers.append(str(ver["version"]))
        v_disp = v if (not v or v[0].isupper()) else v[0].upper() + v[1:]
        if v_disp.lower() == p.lower() or p.lower().startswith(v_disp.lower() + " "):
            label = p
        else:
            label = f"{v_disp} {p}".strip()
        if vers:
            label += " (" + ", ".join(vers[:3]) + (" 외" if len(vers) > 3 else "") + ")"
        prods.append(label)
    if prods:
        out["affected_products"] = prods[:6]
        out["vendor"] = vendor
        out["product"] = product

    cwes = []
    for pt in cna.get("problemTypes") or []:
        for dsc in pt.get("descriptions") or []:
            cid = dsc.get("cweId") or ""
            if cid.startswith("CWE-") and cid not in cwes:
                cwes.append(cid)
    if cwes:
        out["cwe"] = cwes[:4]

    refs = []
    for r in cna.get("references") or []:
        if r.get("url"):
            refs.append({"url": r["url"], "title": ""})
    if refs:
        out["references"] = refs[:8]
    return out or None


def enrich_records(records):
    """CVSS·제품 정보를 CIRCL 개별 레코드(CNA 원문)로 보강한다.
    NVD 신규 CVE는 CPE 분석 전(configurations=null)이라 제품명이 설명문 추출값이므로,
    CNA의 affected(vendor·product)가 있으면 그것을 우선한다."""
    targets = records
    print(f"  [CIRCL] 상세 보강 대상 {len(targets)}건")
    filled = 0
    for r in targets:
        detail = fetch_circl_detail(r["cve_id"])
        if not detail:
            continue
        for k, v in detail.items():
            if k in ("affected_products", "references", "cwe"):
                if v and (k != "affected_products" or len(v) >= 1):
                    r[k] = v
            elif k in ("vendor", "product"):
                if v:
                    r[k] = v
            elif v and not r.get(k):
                r[k] = v
        for k in ("affected_products", "references", "cwe", "poc_links"):
            r.setdefault(k, [])
        filled += 1
        time.sleep(0.25)
    print(f"  [CIRCL] 상세 보강 {filled}건 완료")
    return records


def save_items(records):
    tmp = RUN_ITEMS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    os.replace(tmp, RUN_ITEMS_FILE)


def load_items():
    if not os.path.exists(RUN_ITEMS_FILE):
        return []
    try:
        with open(RUN_ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return []


def collect_all():
    """수집 단계 — KEV·NVD·CIRCL·EPSS·GitHub PoC 를 모아 cve_run_items.json 에 보관"""
    init_db()
    cache = load_cache()
    print("=== [CVE] 수집 시작 ===")
    kev = fetch_kev()
    nvd = fetch_nvd()
    circl = fetch_circl()
    records = merge_records(kev, nvd, circl)
    print(f"  [통합] 피드 기준 CVE {len(records)}건")

    # 경보·보안 뉴스에서만 확인된 CVE 를 후보로 편입 (NVD·CIRCL·KEV 반영 지연 대비)
    clues = collect_cve_clues()
    if clues:
        upsert_cve_alerts(clue_rows(clues))
    extra = build_alert_records(clues, {r["cve_id"] for r in records})
    if extra:
        records = merge_records(records, extra)
        print(f"  [통합] 경보·뉴스에서 추가된 CVE {len(extra)}건 반영")
    print(f"  [통합] 중복 제거 후 CVE {len(records)}건")

    epss = fetch_epss([r["cve_id"] for r in records])
    for r in records:
        if r["cve_id"] in epss:
            r["epss_score"], r["epss_percentile"] = epss[r["cve_id"]]
        if r.get("cvss_score") is not None and r.get("severity") in (None, "", "UNKNOWN"):
            r["severity"] = classify_severity(r["cvss_score"])
        r.setdefault("severity", "UNKNOWN")
    save_items(records)

    enrich_records(records)
    for r in records:
        if r.get("cvss_score") is not None:
            r["severity"] = classify_severity(r["cvss_score"]) if r.get("severity") in (None, "", "UNKNOWN") else r["severity"]
    save_items(records)

    collect_pocs(records, cache)
    save_cache(cache)
    save_items(records)
    return records


def finish(records=None):
    """미분석(폴백) 항목을 정리하고 DB에 적재"""
    records = records if records is not None else load_items()
    if not records:
        print("수집 결과가 없습니다. 먼저 수집을 실행하세요.")
        return 0
    for r in records:
        if not r.get("title_ko"):
            r.update(fallback_korean(r, "pending"))
        r.pop("_hash", None)
        r["updated_at"] = now_str()
    apply_curated(records)
    init_db()
    count = upsert_cve_reports(records)
    exa = sum(1 for r in records if r.get("analyzed_by") == "exaone")
    print(f"=== [CVE] {count}건 DB 적재 완료 (archive.db · cve_reports) ===")
    print(f"  - EXAONE 분석 {exa}건 / 한국어 폴백 {len(records) - exa}건")
    print(f"  - KEV {sum(1 for r in records if r.get('is_kev'))}건 / PoC 확보 {sum(1 for r in records if r.get('poc_links'))}건")
    return count


def run_collect():
    records = collect_all()
    cache = load_cache()
    analyze_records(records, cache)
    save_cache(cache)
    save_items(records)
    return finish(records)


def run_analyze(ai_limit=None, budget=AI_TIME_BUDGET):
    records = load_items()
    if not records:
        print("수집 결과가 없습니다. 먼저 수집을 실행하세요.")
        return 0
    cache = load_cache()
    analyze_records(records, cache, ai_limit=ai_limit, budget=budget, patient=True)
    save_cache(cache)
    save_items(records)
    print(f"=== [CVE] 분석 저장 완료 ({len(records)}건 중 EXAONE {sum(1 for r in records if r.get('analyzed_by') == 'exaone')}건) ===")
    return len(records)


def run_ai_only(ai_limit=None):
    init_db()
    cache = load_cache()
    records = get_cve_reports()
    if not records:
        print("DB에 CVE 리포트가 없습니다. 먼저 수집을 실행하세요.")
        return 0
    analyze_records(records, cache, ai_limit=ai_limit, patient=True)
    save_cache(cache)
    for r in records:
        r.pop("_hash", None)
        r["updated_at"] = now_str()
    apply_curated(records)
    count = upsert_cve_reports(records)
    exa = sum(1 for r in records if r.get("analyzed_by") == "exaone")
    print(f"=== [CVE] 재분석 완료 — EXAONE {exa}건 / 전체 {count}건 ===")
    return count


def main():
    args = sys.argv[1:]
    limit_ai = None
    if "--limit-ai" in args:
        try:
            limit_ai = int(args[args.index("--limit-ai") + 1])
        except (IndexError, ValueError):
            limit_ai = None
    budget = AI_TIME_BUDGET
    if "--budget" in args:
        try:
            budget = int(args[args.index("--budget") + 1])
        except (IndexError, ValueError):
            budget = AI_TIME_BUDGET

    if "--ai-only" in args:
        run_ai_only(limit_ai)
        return
    if "--curated-sync" in args:
        init_db()
        ensure_curated_reports()
        return
    if "--alerts" in args:
        # 경보·보안 뉴스에서 어떤 CVE 가 잡히는지 확인만 하고 DB 레코드는 건드리지 않는다
        init_db()
        clues = collect_cve_clues()
        if clues:
            print(f"  [경보] 단서 {upsert_cve_alerts(clue_rows(clues))}행 적재")
        for cid, rows in sorted(clues.items(), key=lambda kv: (kv[1][0]["rank"], kv[1][0]["published_at"])):
            print(f"  - {cid} [{rows[0]['source']}] {rows[0]['title'][:70]}")
        return
    if "--collect-only" in args:
        collect_all()
        return
    if "--analyze" in args:
        run_analyze(limit_ai, budget)
        return
    if "--enrich" in args:
        records = load_items()
        enrich_records(records)
        for r in records:
            if r.get("cvss_score") is not None and r.get("severity") in (None, "", "UNKNOWN"):
                r["severity"] = classify_severity(r["cvss_score"])
        save_items(records)
        return
    if "--finish" in args:
        finish()
        return
    run_collect()


if __name__ == "__main__":
    main()

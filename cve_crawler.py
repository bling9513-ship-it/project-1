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
"""
import os
import re
import sys
import json
import time
import hashlib
import urllib.parse
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
CACHE_FILE = os.path.join(BASE_DIR, "cve_cache.json")
RUN_ITEMS_FILE = os.path.join(BASE_DIR, "cve_run_items.json")

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from db_manager import init_db, upsert_cve_reports, get_cve_reports  # noqa: E402

KST = timezone(timedelta(hours=9))
UA = "InfosecArchive-CVE/1.0 (+https://github.com/bling9513-ship-it/project-1)"

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
CIRCL_URL = "https://cve.circl.lu/api/last/{n}"
NVD_URL = ("https://services.nvd.nist.gov/rest/json/cves/2.0"
           "?pubStartDate={start}&pubEndDate={end}&resultsPerPage=2000")
EPSS_URL = "https://api.first.org/data/v1/epss?cve={ids}"
GH_SEARCH_URL = ("https://api.github.com/search/repositories"
                 "?q={q}+in:name,description&sort=stars&per_page=3")

KEV_LIMIT = 25          # KEV 최근 추가분
NVD_DAYS = 3            # NVD 최근 공개 범위(일)
NVD_LIMIT = 25          # NVD 신규 CVE 최대 건수
CIRCL_EXTRA_LIMIT = 10  # CIRCL 피드 보강 건수
POC_QUERY_LIMIT = 38    # GitHub PoC 조회 최대 CVE 수
AI_BATCH = 4            # EXAONE 1회 호출당 CVE 수
AI_TIME_BUDGET = int(os.environ.get("CVE_AI_TIME_BUDGET", "1500"))

SEVERITY_KO = {"CRITICAL": "치명적", "HIGH": "높음", "MEDIUM": "보통", "LOW": "낮음", "UNKNOWN": "미평가"}


# ---------------------------------------------------------------------------
# 공통 유틸
# ---------------------------------------------------------------------------

def now_kst():
    return datetime.now(KST)


def now_str():
    return now_kst().strftime("%Y-%m-%d %H:%M:%S KST")


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
                return json.loads(resp.read().decode("utf-8"))
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
    raw = data.get("vulnerabilities", [])
    records = []
    for wrap in raw:
        cve = wrap.get("cve") or {}
        cve_id = cve.get("id")
        if not cve_id:
            continue
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
        records.append({
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
        })
    # 최신 공개 우선 + 고위험 우선 정렬 후 상한
    records.sort(key=lambda r: (r.get("severity") == "CRITICAL", r.get("cvss_score") or 0, r.get("published_at") or ""), reverse=True)
    picked = records[:limit]
    print(f"  [NVD] 최근 {days}일 공개 CVE {len(records)}건 중 {len(picked)}건 선별")
    return picked


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


def fetch_poc(cve_id, use_gh=True):
    """GitHub 공개 PoC 저장소 조회. gh CLI 인증(분당 30회) → 없으면 무인증(분당 10회)."""
    q = urllib.parse.quote(cve_id)
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
    """KEV 전체 + 고위험 비-KEV 순으로 PoC 조회 (12시간 캐시 재사용)"""
    use_gh = gh_available()
    delay = 2.4 if use_gh else 7.0
    ordered = sorted(records, key=lambda r: (not r.get("is_kev"), -(r.get("cvss_score") or 0), -(r.get("epss_score") or 0)))
    targets = ordered[:POC_QUERY_LIMIT]
    fetched = 0
    rate_limited = False
    for rec in targets:
        cve_id = rec["cve_id"]
        cached = cache["poc"].get(cve_id)
        if cached and cached.get("fetched_at"):
            try:
                age = now_kst() - datetime.strptime(cached["fetched_at"], "%Y-%m-%d %H:%M:%S")
                if age < timedelta(hours=12):
                    rec["poc_links"] = cached.get("links") or []
                    continue
            except ValueError:
                pass
        if rate_limited:
            rec["poc_links"] = rec.get("poc_links") or []
            continue
        res = fetch_poc(cve_id, use_gh=use_gh)
        if res == "RATE_LIMIT" or res is None:
            # gh 실패 → 다음 항목부터는 딜레이를 늘려 재시도
            rec["poc_links"] = rec.get("poc_links") or []
            time.sleep(10)
            res2 = fetch_poc(cve_id, use_gh=use_gh)
            if res2 in (None, "RATE_LIMIT"):
                rate_limited = True
                print(f"  [GitHub] {cve_id} 조회 실패 — 이후 조회는 캐시값으로 유지")
                continue
            res = res2
        rec["poc_links"] = res or []
        cache["poc"][cve_id] = {"fetched_at": now_str(), "links": rec["poc_links"]}
        save_cache(cache)
        fetched += 1
        time.sleep(delay)
    print(f"  [GitHub] PoC 조회 {fetched}건 완료 (대상 {len(targets)}건, {'gh 인증' if use_gh else '무인증'})")


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
    label = clean(product_label(rec), 60)
    sev = rec.get("severity") or "UNKNOWN"
    cvss = rec.get("cvss_score")
    epss = rec.get("epss_score")
    if vtype == "보안 취약점":
        title = f"{label} 보안 취약점".strip()
    else:
        title = f"{label} {TYPE_HINT.get(vtype, '취약점')} 취약점".strip()
    title = re.sub(r"\s+", " ", title)[:80]

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
    # 수집 원문에 적힌 수정 버전 기준을 찾아 구체적으로 안내
    fixed = ""
    for p in rec.get("affected_products") or []:
        m = re.search(r"<\s*([0-9][\w.\-]*)", p)
        if m:
            fixed = m.group(1)
            break
    if not fixed:
        m = re.search(r"(?:fixed|resolved|patched|corrected|addressed) (?:in|by) (?:version |v)?([0-9][\w.\-]*)", rec.get("description_orig", ""), re.I)
        if m:
            fixed = m.group(1)
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
        data = json.loads(resp.read().decode("utf-8"))
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
        content = None
        for attempt, wait in enumerate((0, 8, 20, 40)):
            if wait:
                time.sleep(wait)
            try:
                content = call_exaone(prompt, key)
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
# 4) 메인
# ---------------------------------------------------------------------------

def merge_records(kev, circl, nvd):
    merged = {}
    order = []
    for group in (kev, nvd, circl):
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
    """CVSS·제품 정보가 빈 항목(주로 KEV)을 CIRCL 개별 레코드로 보강"""
    targets = [r for r in records if r.get("cvss_score") is None or not r.get("affected_products")]
    print(f"  [CIRCL] 상세 보강 대상 {len(targets)}건")
    filled = 0
    for r in targets:
        detail = fetch_circl_detail(r["cve_id"])
        if not detail:
            continue
        for k, v in detail.items():
            if k in ("affected_products", "references", "cwe"):
                if v and (not r.get(k) or r.get("source") == "CISA KEV"):
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

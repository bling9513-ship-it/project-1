#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정보보안 채용공고 자동 수집 & 엄격한 직무 검증/태깅 크롤러
대상 플랫폼: 원티드 (Wanted), 점핏 (Jumpit), 사람인 (Saramin)
대상 핵심 분야: 정보보안, 정보보호, 취약점 진단, 모의해킹
"""

import urllib.request
import urllib.parse
import json
import re
import html
from datetime import datetime, timezone, timedelta, date

KEYWORDS = ["정보보안", "정보보호", "취약점 진단", "모의해킹"]

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
WANTED_HEADERS = {**HEADERS_BASE, "Referer": "https://www.wanted.co.kr/"}
JUMPIT_HEADERS = {**HEADERS_BASE, "Referer": "https://www.jumpit.co.kr/"}
SARAMIN_HEADERS = {**HEADERS_BASE, "Referer": "https://www.saramin.co.kr/"}

# 실제 정보보안 직무 식별을 위한 필수 키워드 패턴 (대소문자 무관)
SECURITY_PATTERNS = [
    r"보안", r"정보보호", r"개인정보", r"취약점", r"모의해킹", r"침해대응",
    r"\bcert\b", r"보안관제", r"악성코드", r"리버싱", r"\bciso\b", r"\bcpo\b",
    r"\bisms\b", r"security", r"infosec", r"secops", r"devsecops",
    r"pentest", r"penetration", r"cyber", r"vulnerab", r"red\s*team", r"blue\s*team",
    r"오펜시브"
]

# 비보안 직무 및 단순 물리/경비 직무 제외 패턴
EXCLUDE_PATTERNS = [
    r"경비", r"보안요원", r"물류센터\s*보안", r"시설\s*보안", r"주차\s*보안",
    r"출입\s*보안", r"보안\s*안내", r"특수경비", r"청원경찰",
    r"마케팅", r"디자이너", r"영업", r"\bmd\b", r"hvac", r"캐스팅"
]

def get_today_kst():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).date()

def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()

def is_security(title):
    """공고 제목(Title)을 기반으로 실제 정보보안 직무인지 엄격 검증"""
    t = clean_text(title).lower()
    if not any(re.search(p, t) for p in SECURITY_PATTERNS):
        return False
    if any(re.search(p, t) for p in EXCLUDE_PATTERNS):
        return False
    return True

def assign_keywords(title):
    """
    공고 제목 및 직무명을 분석하여 실제 수행 업무에 부합하는 카테고리만 정확히 태깅
    (검색 쿼리 기반 맹목적 태깅 배제)
    """
    t = clean_text(title).lower()
    tags = []
    
    # 1. 모의해킹 (Penetration Testing / Offensive)
    if any(k in t for k in ["모의해킹", "pentest", "penetration", "레드팀", "red team", "오펜시브", "offensive", "해킹"]):
        tags.append("모의해킹")
        
    # 2. 취약점 진단 (Vulnerability Assessment / Code Audit)
    if any(k in t for k in ["취약점", "진단", "보안성 검토", "보안성검토", "소스코드", "sast", "dast", "vulnerab"]):
        tags.append("취약점 진단")
        
    # 3. 정보보호 (Governance, Risk & Compliance, Privacy, ISMS)
    if any(k in t for k in ["정보보호", "개인정보", "isms", "cpo", "privacy", "관리체계", "grc", "컴플라이언스"]):
        tags.append("정보보호")
        
    # 4. 정보보안 (Infosec, Engineering, Operations, CERT, Cloud/Network Security)
    if any(k in t for k in ["정보보안", "보안", "security", "secops", "devsecops", "infosec", "침해대응", "cert", "관제", "악성코드", "리버싱", "cyber"]):
        tags.append("정보보안")
        
    if not tags:
        tags.append("정보보안")
    return tags

def normalize_key(company, title):
    """중복 제거를 위한 정규화 키 생성"""
    c = clean_text(company)
    c = re.sub(r"[\(주\)|㈜|주식회사|\s]", "", c).lower()
    
    t = clean_text(title)
    t = re.sub(r"\[.*?\]|\(.*?\)|<.*?>", "", t)
    t = re.sub(r"[\s\-_/|·]", "", t).lower()
    return f"{c}_{t[:12]}"

def parse_saramin_deadline(text, today_date):
    t = text.strip()
    if not t or "상시" in t:
        return "상시채용"
    if "채용시" in t:
        return "채용시 마감"
    if "오늘" in t:
        return "D-Day (오늘 마감)"
    if "내일" in t:
        return "D-1 (내일 마감)"
    
    m = re.search(r"(\d{1,2})/(\d{1,2})", t)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        year = today_date.year
        if month < today_date.month:
            year += 1
        target = date(year, month, day)
        diff = (target - today_date).days
        if diff < 0:
            return f"마감 ({t})"
        elif diff == 0:
            return f"D-Day ({t})"
        else:
            return f"D-{diff} ({t})"
    return t

def format_jumpit_deadline(p, today_date):
    if p.get("alwaysOpen"):
        return "상시채용"
    closed_at = p.get("closedAt")
    if not closed_at:
        return "상시채용"
    try:
        dt = datetime.fromisoformat(closed_at.replace("Z", "+00:00"))
        d_day = (dt.date() - today_date).days
        day_str = dt.strftime("%m/%d")
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        w = weekdays[dt.weekday()]
        if d_day < 0:
            return f"마감 (~{day_str})"
        elif d_day == 0:
            return f"D-Day (~{day_str} {w})"
        else:
            return f"D-{d_day} (~{day_str} {w})"
    except Exception:
        return "상시채용"

def fetch_jumpit(today_date):
    """점핏 (Jumpit) API 수집 + 직무 검증"""
    results = []
    seen_ids = set()
    queries = ["정보보안", "보안", "정보보호", "취약점", "모의해킹"]
    
    for q in queries:
        for page in [1, 2]:
            encoded = urllib.parse.quote(q)
            url = f"https://api.jumpit.co.kr/api/positions?keyword={encoded}&page={page}"
            try:
                req = urllib.request.Request(url, headers=JUMPIT_HEADERS)
                with urllib.request.urlopen(req, timeout=10) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    positions = data.get("result", {}).get("positions", [])
                    for p in positions:
                        jid = str(p.get("id"))
                        if jid in seen_ids:
                            continue
                        seen_ids.add(jid)
                        
                        title = clean_text(p.get("title", ""))
                        if not is_security(title):
                            continue
                            
                        comp = clean_text(p.get("companyName", ""))
                        deadline = format_jumpit_deadline(p, today_date)
                        results.append({
                            "platform": "점핏",
                            "company": comp,
                            "title": title,
                            "url": f"https://www.jumpit.co.kr/position/{jid}",
                            "location": clean_text(p.get("location", "")),
                            "deadline": deadline
                        })
            except Exception as e:
                pass
    return results

def fetch_wanted():
    """원티드 (Wanted) 공식 채용 API 수집 + 직무 검증"""
    results = []
    seen_ids = set()
    queries = ["정보보안", "보안", "정보보호", "취약점", "모의해킹"]
    
    for q in queries:
        encoded = urllib.parse.quote(q)
        url = f"https://www.wanted.co.kr/api/v4/jobs?query={encoded}&country=kr&years=-1&limit=50"
        try:
            req = urllib.request.Request(url, headers=WANTED_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode("utf-8"))
                for item in data.get("data", []):
                    jid = str(item.get("id"))
                    if jid in seen_ids:
                        continue
                    seen_ids.add(jid)
                    
                    pos = clean_text(item.get("position", ""))
                    if not is_security(pos):
                        continue
                        
                    comp = clean_text(item.get("company", {}).get("name", "") if isinstance(item.get("company"), dict) else item.get("company", ""))
                    results.append({
                        "platform": "원티드",
                        "company": comp,
                        "title": pos,
                        "url": f"https://www.wanted.co.kr/wd/{jid}",
                        "location": clean_text(item.get("address", {}).get("location", "")),
                        "deadline": "상시채용"
                    })
        except Exception as e:
            pass
    return results

def fetch_saramin(today_date):
    """사람인 (Saramin) 수집 + 직무 검증"""
    results = []
    seen_links = set()
    queries = ["정보보안", "정보보호", "취약점 진단", "모의해킹"]
    
    for q in queries:
        encoded = urllib.parse.quote(q)
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={encoded}&recruitPage=1"
        try:
            req = urllib.request.Request(url, headers=SARAMIN_HEADERS)
            with urllib.request.urlopen(req, timeout=15) as res:
                page = res.read().decode("utf-8", errors="ignore")
                pattern = r'<strong class="corp_name"[^>]*>.*?<a[^>]*>(.*?)</a>.*?<h2 class="job_tit"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>.*?<span>(.*?)</span>.*?<div class="job_date">\s*<span class="date">(.*?)</span>'
                for m in re.findall(pattern, page, re.DOTALL):
                    corp = clean_text(m[0])
                    link_part = html.unescape(m[1]).split("&searchType")[0]
                    link = ("https://www.saramin.co.kr" + link_part) if not link_part.startswith("http") else link_part
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    title = clean_text(m[2])
                    if not is_security(title):
                        continue
                        
                    raw_deadline = clean_text(m[3])
                    deadline = parse_saramin_deadline(raw_deadline, today_date)
                    results.append({
                        "platform": "사람인",
                        "company": corp,
                        "title": title,
                        "url": link,
                        "location": "",
                        "deadline": deadline
                    })
        except Exception as e:
            pass
    return results

def collect_all_jobs():
    today_date = get_today_kst()
    print("=== 정보보안 채용 정보 정밀 수집 시작 ===")
    
    wanted_jobs = fetch_wanted()
    jumpit_jobs = fetch_jumpit(today_date)
    saramin_jobs = fetch_saramin(today_date)
    
    print(f"-> 플랫폼별 검증 수집 결과: 원티드 {len(wanted_jobs)}건, 점핏 {len(jumpit_jobs)}건, 사람인 {len(saramin_jobs)}건")
    raw_jobs = wanted_jobs + jumpit_jobs + saramin_jobs
    print(f"-> 유효 보안 공고 총합: {len(raw_jobs)}건")
    
    # 중복 제거 및 직무 기반 정확한 카테고리 태깅
    deduped = {}
    for job in raw_jobs:
        if not job["company"] or not job["title"]:
            continue
            
        key = normalize_key(job["company"], job["title"])
        if key not in deduped:
            deduped[key] = {
                "company": job["company"],
                "title": job["title"],
                "url": job["url"],
                "platforms": [job["platform"]],
                "keywords": assign_keywords(job["title"]),
                "location": job["location"],
                "deadline": job.get("deadline", "상시채용")
            }
        else:
            if job["platform"] not in deduped[key]["platforms"]:
                deduped[key]["platforms"].append(job["platform"])
            if not deduped[key]["location"] and job["location"]:
                deduped[key]["location"] = job["location"]
            # 구체적인 D-day 일정이 있는 마감일을 '상시채용'보다 우선 반영
            curr_dl = deduped[key].get("deadline", "상시채용")
            new_dl = job.get("deadline", "상시채용")
            if "상시채용" in curr_dl and "상시채용" not in new_dl:
                deduped[key]["deadline"] = new_dl
                
    job_list = list(deduped.values())
    print(f"-> 중복 제거 후 최종 고유 공고: {len(job_list)}건")
    return job_list

def generate_html(jobs, update_time_str):
    """GitHub Pages 배포용 정적 웹 대시보드 (프로덕트급 미니멀 UI/UX)"""
    jobs_json_str = json.dumps(jobs, ensure_ascii=False)
    
    kw_counts = {}
    for kw in KEYWORDS:
        kw_counts[kw] = sum(1 for j in jobs if kw in j.get("keywords", []))
        
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SecJobs · 정보보안 포지션 큐레이션</title>
  <meta name="description" content="원티드, 점핏, 사람인의 보안 엔지니어 및 분석가 채용공고를 매일 아침 선별해 중복 없이 제공합니다.">
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
  <style>
    :root {{
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      
      --bg-page: #f8fafc;
      --bg-surface: #ffffff;
      --bg-subtle: #f1f5f9;
      --bg-muted: #e2e8f0;
      
      --border-subtle: #f1f5f9;
      --border-default: #e2e8f0;
      --border-strong: #cbd5e1;
      
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;
      
      --accent-primary: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;
      
      --tag-bg: #f8fafc;
      --tag-border: #e2e8f0;
      --tag-text: #475569;
      
      --wanted-bg: #eff6ff;
      --wanted-text: #2563eb;
      --wanted-border: #bfdbfe;
      
      --jumpit-bg: #ecfdf5;
      --jumpit-text: #059669;
      --jumpit-border: #a7f3d0;
      
      --saramin-bg: #fff7ed;
      --saramin-text: #d97706;
      --saramin-border: #fed7aa;
      
      --urgent-bg: #fef2f2;
      --urgent-text: #dc2626;
      --urgent-border: #fecaca;
      
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
    }}

    [data-theme="dark"] {{
      --bg-page: #09090b;
      --bg-surface: #18181b;
      --bg-subtle: #27272a;
      --bg-muted: #3f3f46;
      
      --border-subtle: #1f1f23;
      --border-default: #27272a;
      --border-strong: #3f3f46;
      
      --text-primary: #f4f4f5;
      --text-secondary: #a1a1aa;
      --text-muted: #71717a;
      
      --accent-primary: #3b82f6;
      --accent-hover: #60a5fa;
      --accent-subtle: rgba(59, 130, 246, 0.15);
      
      --tag-bg: #27272a;
      --tag-border: #3f3f46;
      --tag-text: #d4d4d8;
      
      --wanted-bg: rgba(37, 99, 235, 0.15);
      --wanted-text: #60a5fa;
      --wanted-border: rgba(37, 99, 235, 0.3);
      
      --jumpit-bg: rgba(16, 185, 129, 0.15);
      --jumpit-text: #34d399;
      --jumpit-border: rgba(16, 185, 129, 0.3);
      
      --saramin-bg: rgba(245, 158, 11, 0.15);
      --saramin-text: #fbbf24;
      --saramin-border: rgba(245, 158, 11, 0.3);
      
      --urgent-bg: rgba(239, 68, 68, 0.15);
      --urgent-text: #f87171;
      --urgent-border: rgba(239, 68, 68, 0.3);
      
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-page);
      color: var(--text-primary);
      line-height: 1.5;
      letter-spacing: -0.02em;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    /* Global Header */
    .navbar {{
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }}

    .nav-container {{
      max-width: 1140px;
      margin: 0 auto;
      padding: 0 20px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: inherit;
    }}

    .logo-mark {{
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: var(--accent-primary);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .brand-name {{
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
    }}

    .curation-pill {{
      font-size: 11px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 4px;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
    }}

    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .update-meta {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
    }}

    .live-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
    }}

    .icon-btn {{
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
      text-decoration: none;
    }}

    .icon-btn:hover {{
      background: var(--bg-subtle);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }}

    /* Main Container */
    .container {{
      max-width: 1140px;
      margin: 0 auto;
      padding: 32px 20px 80px;
    }}

    /* Hero Section */
    .hero {{
      margin-bottom: 28px;
    }}

    .hero-title {{
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      margin-bottom: 8px;
    }}

    .hero-desc {{
      font-size: 14.5px;
      color: var(--text-secondary);
      line-height: 1.6;
      margin-bottom: 16px;
    }}

    .hero-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .stat-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
    }}

    .stat-chip strong {{
      color: var(--text-primary);
      font-weight: 600;
    }}

    /* Control Panel (Toolbar) */
    .toolbar {{
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 24px;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    /* Search Input */
    .search-box {{
      position: relative;
      width: 100%;
    }}

    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }}

    .search-input {{
      width: 100%;
      padding: 11px 40px 11px 40px;
      font-family: inherit;
      font-size: 14px;
      color: var(--text-primary);
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}

    .search-input:focus {{
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 3px var(--accent-subtle);
    }}

    .clear-search-btn {{
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 14px;
      padding: 4px;
      display: none;
    }}

    .clear-search-btn:hover {{
      color: var(--text-primary);
    }}

    /* Keyword Segmented Tabs */
    .segmented-control {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
      -webkit-overflow-scrolling: touch;
    }}

    .segmented-control::-webkit-scrollbar {{
      display: none;
    }}

    .segment-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 8px;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 13.5px;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      user-select: none;
    }}

    .segment-btn:hover {{
      background: var(--bg-subtle);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }}

    .segment-btn.active {{
      background: var(--text-primary);
      color: var(--bg-surface);
      border-color: var(--text-primary);
      font-weight: 600;
    }}

    .segment-btn .count {{
      font-size: 11px;
      font-weight: 600;
      padding: 1px 6px;
      border-radius: 10px;
      background: rgba(148, 163, 184, 0.2);
    }}

    .segment-btn.active .count {{
      background: rgba(255, 255, 255, 0.25);
    }}

    /* Sub Filters & View Switcher */
    .sub-toolbar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding-top: 10px;
      border-top: 1px solid var(--border-subtle);
    }}

    .filter-group {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
    }}

    .filter-label {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      margin-right: 2px;
    }}

    .filter-pill {{
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .filter-pill:hover {{
      color: var(--text-primary);
      border-color: var(--border-strong);
    }}

    .filter-pill.active {{
      background: var(--accent-subtle);
      color: var(--accent-primary);
      border-color: var(--accent-primary);
      font-weight: 600;
    }}

    .filter-divider {{
      width: 1px;
      height: 14px;
      background: var(--border-default);
      margin: 0 4px;
    }}

    .view-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .sort-select {{
      padding: 5px 10px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 12px;
      font-weight: 500;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      cursor: pointer;
      outline: none;
    }}

    .sort-select:focus {{
      border-color: var(--accent-primary);
    }}

    .view-toggle {{
      display: inline-flex;
      border: 1px solid var(--border-default);
      border-radius: 6px;
      overflow: hidden;
    }}

    .view-toggle-btn {{
      padding: 5px 8px;
      background: var(--bg-page);
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }}

    .view-toggle-btn:hover {{
      color: var(--text-primary);
    }}

    .view-toggle-btn.active {{
      background: var(--bg-surface);
      color: var(--accent-primary);
      font-weight: 600;
    }}

    /* Feed Status Info */
    .feed-info {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 16px;
      padding: 0 2px;
    }}

    .feed-info strong {{
      color: var(--text-primary);
      font-weight: 600;
    }}

    /* Job Cards Grid View */
    .jobs-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
    }}

    @media (min-width: 640px) {{
      .jobs-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    @media (min-width: 1024px) {{
      .jobs-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
      }}
    }}

    .job-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      padding: 18px 20px;
      text-decoration: none;
      color: inherit;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: var(--card-shadow);
      transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
      cursor: pointer;
    }}

    .job-card:hover {{
      transform: translateY(-2px);
      border-color: var(--border-strong);
      box-shadow: var(--card-shadow-hover);
    }}

    .job-card:hover .job-title {{
      color: var(--accent-primary);
    }}

    .card-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 8px;
    }}

    .company-name {{
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .badges-row {{
      display: flex;
      align-items: center;
      gap: 5px;
      flex-shrink: 0;
    }}

    .badge-dl {{
      font-size: 11px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 4px;
      white-space: nowrap;
    }}

    .badge-dl-urgent {{
      background: var(--urgent-bg);
      color: var(--urgent-text);
      border: 1px solid var(--urgent-border);
    }}

    .badge-dl-normal {{
      background: var(--bg-subtle);
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
    }}

    .badge-dl-always {{
      background: var(--bg-page);
      color: var(--text-muted);
      border: 1px solid var(--border-subtle);
    }}

    .badge-platform {{
      font-size: 10.5px;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }}

    .badge-platform-원티드 {{
      background: var(--wanted-bg);
      color: var(--wanted-text);
      border: 1px solid var(--wanted-border);
    }}

    .badge-platform-점핏 {{
      background: var(--jumpit-bg);
      color: var(--jumpit-text);
      border: 1px solid var(--jumpit-border);
    }}

    .badge-platform-사람인 {{
      background: var(--saramin-bg);
      color: var(--saramin-text);
      border: 1px solid var(--saramin-border);
    }}

    .job-title {{
      font-size: 15.5px;
      font-weight: 600;
      line-height: 1.45;
      color: var(--text-primary);
      margin-bottom: 14px;
      word-break: keep-all;
      transition: color 0.15s ease;
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid var(--border-subtle);
    }}

    .tags-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }}

    .keyword-tag {{
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 4px;
      background: var(--tag-bg);
      border: 1px solid var(--tag-border);
      color: var(--tag-text);
    }}

    .outlink-indicator {{
      color: var(--text-muted);
      display: flex;
      align-items: center;
      transition: transform 0.15s ease, color 0.15s ease;
    }}

    .job-card:hover .outlink-indicator {{
      color: var(--accent-primary);
      transform: translate(2px, -2px);
    }}

    /* Compact List View */
    .jobs-list-compact {{
      display: flex;
      flex-direction: column;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--card-shadow);
    }}

    .list-row {{
      display: grid;
      grid-template-columns: 140px 1fr 110px 70px 30px;
      align-items: center;
      gap: 12px;
      padding: 13px 18px;
      border-bottom: 1px solid var(--border-subtle);
      text-decoration: none;
      color: inherit;
      transition: background-color 0.12s ease;
    }}

    .list-row:last-child {{
      border-bottom: none;
    }}

    .list-row:hover {{
      background: var(--bg-subtle);
    }}

    .list-row:hover .list-title {{
      color: var(--accent-primary);
    }}

    .list-company {{
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .list-title {{
      font-size: 14.5px;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      transition: color 0.12s ease;
    }}

    .list-deadline {{
      font-size: 11.5px;
      text-align: right;
    }}

    .list-platforms {{
      display: flex;
      gap: 4px;
    }}

    .list-outlink {{
      color: var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: flex-end;
    }}

    @media (max-width: 768px) {{
      .list-row {{
        grid-template-columns: 1fr auto;
        gap: 6px;
        padding: 12px 14px;
      }}
      .list-company {{
        font-size: 12px;
        grid-column: 1;
      }}
      .list-title {{
        font-size: 14px;
        grid-column: 1;
        white-space: normal;
      }}
      .list-deadline {{
        grid-column: 2;
        grid-row: 1;
      }}
      .list-platforms {{
        grid-column: 2;
        grid-row: 2;
      }}
      .list-outlink {{
        display: none;
      }}
    }}

    /* Empty State */
    .empty-state {{
      text-align: center;
      padding: 64px 20px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      color: var(--text-secondary);
    }}

    .empty-title {{
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 6px;
    }}

    .empty-desc {{
      font-size: 13.5px;
      color: var(--text-muted);
      margin-bottom: 16px;
    }}

    .reset-btn {{
      padding: 7px 16px;
      border-radius: 8px;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      cursor: pointer;
    }}

    .reset-btn:hover {{
      background: var(--bg-subtle);
    }}

    /* Footer */
    footer {{
      margin-top: 60px;
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.8;
    }}
  </style>
</head>
<body>

  <!-- Global Nav -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <div class="logo-mark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
        <span class="brand-name">SecJobs</span>
        <span class="curation-pill">큐레이션</span>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>{update_time_str} 기준</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        </button>
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="container">
    
    <!-- Hero Header -->
    <section class="hero">
      <h1 class="hero-title">정보보안 직무 채용 큐레이션</h1>
      <p class="hero-desc">원티드 · 점핏 · 사람인의 보안 포지션을 직무 검증을 거쳐 선별하고 중복 없이 정리합니다.</p>
      <div class="hero-stats">
        <span class="stat-chip">엄선된 보안 공고 <strong>{len(jobs)}건</strong></span>
        <span class="stat-chip">매일 <strong>06:30</strong> 자동 갱신</span>
        <span class="stat-chip">공고명 기반 정밀 직무 분류</span>
      </div>
    </section>

    <!-- Toolbar -->
    <section class="toolbar">
      <!-- Search Input -->
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="searchInput" class="search-input" placeholder="회사명, 포지션명, 기술 키워드로 검색 (예: 금융, 모의해킹, 신입)">
        <button id="clearSearch" class="clear-search-btn" aria-label="검색 지우기">✕</button>
      </div>

      <!-- Keyword Tabs -->
      <div class="segmented-control" id="keywordNav">
        <button class="segment-btn active" data-kw="all">전체 <span class="count">{len(jobs)}</span></button>
        <button class="segment-btn" data-kw="정보보안">정보보안 <span class="count">{kw_counts.get("정보보안", 0)}</span></button>
        <button class="segment-btn" data-kw="정보보호">정보보호 <span class="count">{kw_counts.get("정보보호", 0)}</span></button>
        <button class="segment-btn" data-kw="취약점 진단">취약점 진단 <span class="count">{kw_counts.get("취약점 진단", 0)}</span></button>
        <button class="segment-btn" data-kw="모의해킹">모의해킹 <span class="count">{kw_counts.get("모의해킹", 0)}</span></button>
      </div>

      <!-- Sub Filters & View Options -->
      <div class="sub-toolbar">
        <div class="filter-group">
          <span class="filter-label">플랫폼</span>
          <button class="filter-pill active" data-filter="platform" data-val="all">전체</button>
          <button class="filter-pill" data-filter="platform" data-val="원티드">원티드</button>
          <button class="filter-pill" data-filter="platform" data-val="점핏">점핏</button>
          <button class="filter-pill" data-filter="platform" data-val="사람인">사람인</button>
          
          <span class="filter-divider"></span>
          
          <span class="filter-label">마감</span>
          <button class="filter-pill active" data-filter="deadline" data-val="all">전체</button>
          <button class="filter-pill" data-filter="deadline" data-val="urgent">마감 임박</button>
          <button class="filter-pill" data-filter="deadline" data-val="always">상시</button>
        </div>

        <div class="view-actions">
          <select id="sortSelect" class="sort-select" aria-label="정렬">
            <option value="default">등록 순</option>
            <option value="deadline">마감 임박 순</option>
            <option value="company">회사명 순</option>
          </select>

          <div class="view-toggle">
            <button class="view-toggle-btn active" id="btnGrid" title="카드 그리드 뷰" aria-label="그리드 뷰">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
              </svg>
            </button>
            <button class="view-toggle-btn" id="btnList" title="컴팩트 리스트 뷰" aria-label="리스트 뷰">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Status Bar -->
    <div class="feed-info">
      <div>현재 <strong id="matchCount">{len(jobs)}</strong>개의 포지션 표시 중</div>
      <div id="filterSummary"></div>
    </div>

    <!-- Job Cards Container -->
    <div id="jobsContainer"></div>

    <!-- Footer -->
    <footer>
      <p>SecJobs · 비상업적 정보 큐레이션 서비스</p>
      <p>데이터는 매일 아침 06:30 KST 기준 자동 갱신됩니다.</p>
    </footer>
  </main>

  <script>
    const JOBS = {jobs_json_str};

    let selectedKeyword = 'all';
    let selectedPlatform = 'all';
    let selectedDeadline = 'all';
    let sortBy = 'default';
    let searchTerm = '';
    let currentView = 'grid';

    const jobsContainer = document.getElementById('jobsContainer');
    const matchCount = document.getElementById('matchCount');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');
    const sortSelect = document.getElementById('sortSelect');
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');

    // Theme Management
    function initTheme() {{
      const saved = localStorage.getItem('secjobs-theme');
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
        setTheme('dark');
      }} else {{
        setTheme('light');
      }}
    }}

    function setTheme(theme) {{
      if (theme === 'dark') {{
        document.documentElement.setAttribute('data-theme', 'dark');
        moonIcon.style.display = 'none';
        sunIcon.style.display = 'block';
        localStorage.setItem('secjobs-theme', 'dark');
      }} else {{
        document.documentElement.removeAttribute('data-theme');
        moonIcon.style.display = 'block';
        sunIcon.style.display = 'none';
        localStorage.setItem('secjobs-theme', 'light');
      }}
    }}

    themeToggle.addEventListener('click', () => {{
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      setTheme(isDark ? 'light' : 'dark');
    }});

    // Helper: Clean leading emojis from deadline
    function cleanDeadline(dl) {{
      if (!dl) return '상시채용';
      return dl.replace(/^[🚨⚡⏳\\s]+/, '').trim();
    }}

    function getDeadlineMeta(rawDl) {{
      const dl = cleanDeadline(rawDl);
      let badgeClass = 'badge-dl-normal';
      let isUrgent = false;
      let isAlways = false;
      let daysLeft = 999;

      if (dl.includes('D-Day') || dl.includes('D-1') || dl.includes('D-2') || dl.includes('D-3') || dl.includes('오늘') || dl.includes('내일')) {{
        badgeClass = 'badge-dl-urgent';
        isUrgent = true;
        const m = dl.match(/D-(\\d+)/);
        daysLeft = m ? parseInt(m[1]) : 0;
      }} else if (dl.includes('상시') || dl.includes('채용시')) {{
        badgeClass = 'badge-dl-always';
        isAlways = true;
        daysLeft = 500;
      }} else {{
        const m = dl.match(/D-(\\d+)/);
        if (m) daysLeft = parseInt(m[1]);
      }}

      return {{ label: dl, badgeClass, isUrgent, isAlways, daysLeft }};
    }}

    function escapeHtml(str) {{
      return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    function renderFeed() {{
      // 1. Filter
      let filtered = JOBS.filter(job => {{
        if (selectedKeyword !== 'all' && (!job.keywords || !job.keywords.includes(selectedKeyword))) {{
          return false;
        }}
        if (selectedPlatform !== 'all' && (!job.platforms || !job.platforms.includes(selectedPlatform))) {{
          return false;
        }}
        const dlMeta = getDeadlineMeta(job.deadline);
        if (selectedDeadline === 'urgent' && !dlMeta.isUrgent) return false;
        if (selectedDeadline === 'always' && !dlMeta.isAlways) return false;

        if (searchTerm) {{
          const term = searchTerm.toLowerCase();
          const matchCompany = (job.company || '').toLowerCase().includes(term);
          const matchTitle = (job.title || '').toLowerCase().includes(term);
          const matchKeywords = (job.keywords || []).some(k => k.toLowerCase().includes(term));
          if (!matchCompany && !matchTitle && !matchKeywords) return false;
        }}
        return true;
      }});

      // 2. Sort
      if (sortBy === 'deadline') {{
        filtered.sort((a, b) => {{
          const da = getDeadlineMeta(a.deadline).daysLeft;
          const db = getDeadlineMeta(b.deadline).daysLeft;
          return da - db;
        }});
      }} else if (sortBy === 'company') {{
        filtered.sort((a, b) => (a.company || '').localeCompare(b.company || '', 'ko'));
      }}

      matchCount.textContent = filtered.length;

      // 3. Render
      if (filtered.length === 0) {{
        jobsContainer.innerHTML = `
          <div class="empty-state">
            <div class="empty-title">일치하는 채용공고가 없습니다</div>
            <div class="empty-desc">검색어를 변경하거나 적용된 필터를 초기화해 보세요.</div>
            <button class="reset-btn" onclick="resetFilters()">필터 초기화</button>
          </div>
        `;
        return;
      }}

      if (currentView === 'grid') {{
        let html = '<div class="jobs-grid">';
        filtered.forEach(job => {{
          const dlMeta = getDeadlineMeta(job.deadline);
          const dlBadge = `<span class="badge-dl ${{dlMeta.badgeClass}}">${{escapeHtml(dlMeta.label)}}</span>`;
          const platformBadges = (job.platforms || []).map(p => 
            `<span class="badge-platform badge-platform-${{p}}">${{p}}</span>`
          ).join('');
          const tags = (job.keywords || []).map(k => 
            `<span class="keyword-tag">#${{k}}</span>`
          ).join('');

          html += `
            <a class="job-card" href="${{job.url}}" target="_blank" rel="noopener noreferrer">
              <div>
                <div class="card-top">
                  <span class="company-name" title="${{escapeHtml(job.company)}}">${{escapeHtml(job.company)}}</span>
                  <div class="badges-row">
                    ${{dlBadge}}
                    ${{platformBadges}}
                  </div>
                </div>
                <div class="job-title">${{escapeHtml(job.title)}}</div>
              </div>
              <div class="card-footer">
                <div class="tags-list">${{tags}}</div>
                <div class="outlink-indicator">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="7" y1="17" x2="17" y2="7"></line>
                    <polyline points="7 7 17 7 17 17"></polyline>
                  </svg>
                </div>
              </div>
            </a>
          `;
        }});
        html += '</div>';
        jobsContainer.innerHTML = html;
      }} else {{
        let html = '<div class="jobs-list-compact">';
        filtered.forEach(job => {{
          const dlMeta = getDeadlineMeta(job.deadline);
          const dlBadge = `<span class="badge-dl ${{dlMeta.badgeClass}}">${{escapeHtml(dlMeta.label)}}</span>`;
          const platformBadges = (job.platforms || []).map(p => 
            `<span class="badge-platform badge-platform-${{p}}">${{p}}</span>`
          ).join('');

          html += `
            <a class="list-row" href="${{job.url}}" target="_blank" rel="noopener noreferrer">
              <div class="list-company" title="${{escapeHtml(job.company)}}">${{escapeHtml(job.company)}}</div>
              <div class="list-title">${{escapeHtml(job.title)}}</div>
              <div class="list-deadline">${{dlBadge}}</div>
              <div class="list-platforms">${{platformBadges}}</div>
              <div class="list-outlink">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="7" y1="17" x2="17" y2="7"></line>
                  <polyline points="7 7 17 7 17 17"></polyline>
                </svg>
              </div>
            </a>
          `;
        }});
        html += '</div>';
        jobsContainer.innerHTML = html;
      }}
    }}

    function resetFilters() {{
      selectedKeyword = 'all';
      selectedPlatform = 'all';
      selectedDeadline = 'all';
      searchTerm = '';
      searchInput.value = '';
      clearSearchBtn.style.display = 'none';

      document.querySelectorAll('#keywordNav .segment-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-kw') === 'all'));
      document.querySelectorAll('.filter-pill[data-filter="platform"]').forEach(b => b.classList.toggle('active', b.getAttribute('data-val') === 'all'));
      document.querySelectorAll('.filter-pill[data-filter="deadline"]').forEach(b => b.classList.toggle('active', b.getAttribute('data-val') === 'all'));

      renderFeed();
    }}

    // Event Listeners
    document.querySelectorAll('#keywordNav .segment-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('#keywordNav .segment-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedKeyword = btn.getAttribute('data-kw');
        renderFeed();
      }});
    }});

    document.querySelectorAll('.filter-pill').forEach(pill => {{
      pill.addEventListener('click', () => {{
        const filterType = pill.getAttribute('data-filter');
        const val = pill.getAttribute('data-val');
        document.querySelectorAll(`.filter-pill[data-filter="${{filterType}}"]`).forEach(p => p.classList.remove('active'));
        pill.classList.add('active');

        if (filterType === 'platform') selectedPlatform = val;
        if (filterType === 'deadline') selectedDeadline = val;
        renderFeed();
      }});
    }});

    searchInput.addEventListener('input', e => {{
      searchTerm = e.target.value.trim();
      clearSearchBtn.style.display = searchTerm ? 'block' : 'none';
      renderFeed();
    }});

    clearSearchBtn.addEventListener('click', () => {{
      searchInput.value = '';
      searchTerm = '';
      clearSearchBtn.style.display = 'none';
      renderFeed();
      searchInput.focus();
    }});

    sortSelect.addEventListener('change', e => {{
      sortBy = e.target.value;
      renderFeed();
    }});

    document.getElementById('btnGrid').addEventListener('click', () => {{
      currentView = 'grid';
      document.getElementById('btnGrid').classList.add('active');
      document.getElementById('btnList').classList.remove('active');
      renderFeed();
    }});

    document.getElementById('btnList').addEventListener('click', () => {{
      currentView = 'list';
      document.getElementById('btnList').classList.add('active');
      document.getElementById('btnGrid').classList.remove('active');
      renderFeed();
    }});

    // Keyboard shortcut: '/' to focus search, 'Esc' to clear
    window.addEventListener('keydown', e => {{
      if (e.key === '/' && document.activeElement !== searchInput) {{
        e.preventDefault();
        searchInput.focus();
      }} else if (e.key === 'Escape' && document.activeElement === searchInput) {{
        searchInput.value = '';
        searchTerm = '';
        clearSearchBtn.style.display = 'none';
        renderFeed();
        searchInput.blur();
      }}
    }});

    // Initialize
    initTheme();
    renderFeed();
  </script>
</body>
</html>
"""
    return html_content

def generate_readme(jobs, update_time_str):
    """GitHub 저장소 메인에 노출될 마크다운"""
    keyword_jobs = {kw: [] for kw in KEYWORDS}
    for job in jobs:
        for kw in job.get("keywords", []):
            if kw in keyword_jobs:
                keyword_jobs[kw].append(job)

    lines = [
        "# SecJobs · 정보보안 직무 채용 피드",
        "",
        f"> **🌐 웹사이트 바로가기**: [https://bling9513-ship-it.github.io/project-1/](https://bling9513-ship-it.github.io/project-1/)",
        f"> **마지막 업데이트**: `{update_time_str}` (매일 06:30 KST 자동 수집)",
        f"> **엄선된 보안 공고**: 총 **{len(jobs)}**개 (직무 검증 및 중복 제거 완료)",
        "",
        "### 분야별 바로가기",
        "| 분야 | 등록 공고 | 바로가기 |",
        "| :--- | :---: | :--- |"
    ]

    for kw in KEYWORDS:
        count = len(keyword_jobs[kw])
        anchor = kw.replace(" ", "-")
        lines.append(f"| **{kw}** | **{count}개** | [목록 바로가기](#{anchor}-{count}건) |")

    lines.append("")
    lines.append("---")
    lines.append("")

    for kw in KEYWORDS:
        kw_list = keyword_jobs[kw]
        lines.append(f"## {kw} ({len(kw_list)}건)")
        lines.append("")
        if not kw_list:
            lines.append("_현재 등록된 공고가 없습니다._")
            lines.append("")
            continue

        lines.append("| 회사명 | 공고명 | 플랫폼 | 마감 일정 | 상세 분야 |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for job in kw_list:
            platforms_str = ", ".join(job["platforms"])
            keywords_str = ", ".join([f"`{k}`" for k in job["keywords"]])
            dl = job.get("deadline", "상시채용")
            title_escaped = job["title"].replace("|", "\\|")
            company_escaped = job["company"].replace("|", "\\|")
            lines.append(f"| **{company_escaped}** | [{title_escaped}]({job['url']}) | {platforms_str} | **{dl}** | {keywords_str} |")
        
        lines.append("")
        lines.append("[맨 위로 이동](#secjobs--정보보안-직무-채용-피드)")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def main():
    jobs = collect_all_jobs()
    
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    
    # 1. JSON 파일 저장
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print("-> 'jobs.json' 저장 완료")
    
    # 2. index.html 생성
    html_data = generate_html(jobs, now_kst)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_data)
    print("-> 'index.html' 생성 완료")
    
    # 3. README.md 생성
    readme_data = generate_readme(jobs, now_kst)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_data)
    print("-> 'README.md' 생성 완료")
    
    print("\n모든 산출물이 성공적으로 생성되었습니다!")

if __name__ == "__main__":
    main()

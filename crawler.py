#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정보보안 채용공고 자동 수집 & 엄격한 직무 검증/태깅 크롤러
대상 플랫폼: 원티드 (Wanted), 점핏 (Jumpit), 사람인 (Saramin), 리멤버 (Remember), 잡코리아 (JobKorea), 인크루트 (Incruit)
대상 핵심 분야: 정보보안, 정보보호, 취약점 진단, 모의해킹
"""

import os
import sys
import urllib.request
import urllib.parse
import json
import re
import html
from datetime import datetime, timezone, timedelta, date
from concurrent.futures import ThreadPoolExecutor

from html_guard import harden_html, safe_json_for_script, safe_url
import ui_shell
from net_guard import read_limited

KEYWORDS = ["정보보안", "정보보호", "취약점 진단", "모의해킹"]

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
WANTED_HEADERS = {**HEADERS_BASE, "Referer": "https://www.wanted.co.kr/"}
JUMPIT_HEADERS = {**HEADERS_BASE, "Referer": "https://www.jumpit.co.kr/"}
SARAMIN_HEADERS = {**HEADERS_BASE, "Referer": "https://www.saramin.co.kr/"}
REMEMBER_HEADERS = {
    **HEADERS_BASE,
    "Referer": "https://career.rememberapp.co.kr/",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
JOBKOREA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://m.jobkorea.co.kr/"
}
INCRUIT_HEADERS = {
    **HEADERS_BASE,
    "Referer": "https://job.incruit.com/"
}

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
    r"마케팅", r"디자이너", r"영업", r"\bmd\b", r"hvac", r"캐스팅",
    # 임원·수행 비서 등 보안 키워드가 회사명에만 걸린 비보안 직무
    # (예: "[강서] 정보보안 솔루션 기업 'W'사 임원비서")
    r"비서", r"수행\s*기사"
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

def count_urgent_jobs(jobs):
    """마감 임박 공고 수 — DB가 판정한 deadline_status(D_DAY/URGENT)를 우선한다.

    수집 당시의 상대 라벨('D-9 (~11/25(수))')만 보고 세면 오늘 기준 실제 남은 일수와
    어긋나 화면 칩(D-Day 마감 임박)과 DB 집계가 달라진다. deadline_status가 없는
    입력(외부 호출)만 라벨 기반 is_urgent_deadline으로 되돌린다.
    """
    count = 0
    for j in jobs:
        st = j.get("deadline_status")
        if st in ("D_DAY", "URGENT"):
            count += 1
        elif not st and is_urgent_deadline(j.get("deadline", "")):
            count += 1
    return count


def job_deadline_label(job):
    """표시용 마감 라벨 — 오늘 기준으로 보정된 deadline_label이 있으면 그것을 쓴다."""
    return job.get("deadline_label") or job.get("deadline", "상시채용")


def is_urgent_deadline(dl):
    """마감 임박 여부 판별 (D-Day, 오늘, 내일, D-1 ~ D-7, 날짜 없이 시각만 적힌 당일 마감)"""
    if not dl:
        return False
    if "D-Day" in dl or "오늘" in dl or "내일" in dl:
        return True
    m = re.search(r"D-(\d+)", dl)
    if m:
        return int(m.group(1)) <= 7
    # "16시 마감", "18:30 마감" 처럼 날짜 없이 시각만 적힌 당일 마감 표기
    if re.match(r"^\d\d?(?::\d\d)?\s*시?\s*마감$", dl.strip()):
        return True
    return False

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
    """짧은 제목 키(회사+제목12자). 같은 공고인지 '후보'를 좁히는 용도로만 쓴다.

    제목 앞 12자가 같아도 플랫폼 공고 ID가 다르면 서로 다른 공고이므로,
    이 키만으로 합치지 않는다(합치기 판정은 collect_all_jobs / db_manager 참고).
    회사 법인 표기((주)·㈜·주식회사 …)·괄호 별칭과 제목 앞머리 [태그] 차이는
    db_manager 의 중복 판정 키와 같은 규칙으로 없앤다(제목 속 괄호는 그대로).
    """
    from db_manager import normalize_key as _db_normalize_key
    return _db_normalize_key(clean_text(company), clean_text(title))


def job_external_identity(job):
    """플랫폼 + 공고 ID. 같은 값이면 같은 공고이므로 중복 제거의 최우선 기준이다."""
    platform = str(job.get("platform") or "").strip()
    ext = str(job.get("external_id") or "").strip()
    if not ext and platform:
        try:
            from db_manager import extract_external_id
            ext = extract_external_id(job.get("url", ""))
        except Exception:  # noqa: BLE001 - ID 추출 실패는 'ID 없음'과 같게 다룬다
            ext = ""
        job["external_id"] = ext
    return (platform, ext) if ext else None


def _merge_same_posting(target, job):
    """같은 공고를 한 목록에서 두 번 만났을 때(플랫폼 내 중복) 필드만 보강한다."""
    if job["platform"] not in target["platforms"]:
        target["platforms"].append(job["platform"])
    if not target["location"] and job["location"]:
        target["location"] = job["location"]
    curr_dl = target.get("deadline", "상시채용")
    new_dl = job.get("deadline", "상시채용")
    if ("상시" in curr_dl or "채용시" in curr_dl) and ("D-" in new_dl or "D-Day" in new_dl):
        target["deadline"] = new_dl

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
                    data = json.loads(read_limited(res).decode("utf-8"))
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
                            "external_id": jid,
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
                data = json.loads(read_limited(res).decode("utf-8"))
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
                        "external_id": jid,
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
                page = read_limited(res).decode("utf-8", errors="ignore")
                # 각 공고 단위(item_recruit)로 분할하여 회사명-공고명-마감일의 1:1 매칭 보장
                items = page.split('class="item_recruit"')[1:]
                for it in items:
                    tit_m = re.search(r'<h2 class="job_tit"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>.*?<span>(.*?)</span>', it, re.DOTALL)
                    corp_m = re.search(r'<strong class="corp_name"[^>]*>.*?<a[^>]*>(.*?)</a>', it, re.DOTALL)
                    date_m = re.search(r'<div class="job_date">\s*<span class="date">(.*?)</span>', it, re.DOTALL)
                    
                    if not tit_m or not corp_m:
                        continue
                        
                    corp = clean_text(corp_m.group(1))
                    title = clean_text(tit_m.group(2))
                    if not is_security(title):
                        continue
                        
                    link_part = html.unescape(tit_m.group(1)).split("&searchType")[0]
                    link = ("https://www.saramin.co.kr" + link_part) if not link_part.startswith("http") else link_part
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    raw_deadline = clean_text(date_m.group(1)) if date_m else "상시채용"
                    deadline = parse_saramin_deadline(raw_deadline, today_date)
                    results.append({
                        "platform": "사람인",
                        "external_id": (re.search(r"rec_idx=(\d+)", link).group(1) if re.search(r"rec_idx=(\d+)", link) else ""),
                        "company": corp,
                        "title": title,
                        "url": link,
                        "location": "",
                        "deadline": deadline
                    })
        except Exception as e:
            pass
    return results

def fetch_remember(today_date):
    """리멤버 (Remember) REST API 수집 + 직무 검증"""
    results = []
    seen_ids = set()
    queries = ["정보보안", "정보보호", "취약점 진단", "모의해킹"]
    url = "https://career-api.rememberapp.co.kr/job_postings/search"
    for q in queries:
        for page in [1, 2]:
            payload = json.dumps({"search": {"keywords": [q]}, "page": page, "per": 50}).encode("utf-8")
            try:
                req = urllib.request.Request(url, data=payload, headers=REMEMBER_HEADERS, method="POST")
                with urllib.request.urlopen(req, timeout=10) as res:
                    data = json.loads(read_limited(res).decode("utf-8"))
                    for it in data.get("data", []):
                        jid = str(it.get("id"))
                        if jid in seen_ids:
                            continue
                        seen_ids.add(jid)
                        title = clean_text(it.get("title", ""))
                        if not is_security(title):
                            continue
                        comp = clean_text((it.get("company") or {}).get("name") or (it.get("organization") or {}).get("name") or "")
                        deadline = "상시채용"
                        if it.get("explicit_due") and it.get("ends_at"):
                            try:
                                dt = datetime.fromisoformat(it.get("ends_at"))
                                diff = (dt.date() - today_date).days
                                day_str = dt.strftime("%m/%d")
                                w = ["월", "화", "수", "목", "금", "토", "일"][dt.weekday()]
                                if diff < 0:
                                    deadline = f"마감 (~{day_str})"
                                elif diff == 0:
                                    deadline = f"D-Day (~{day_str} {w})"
                                elif diff == 1:
                                    deadline = "D-1 (내일 마감)"
                                else:
                                    deadline = f"D-{diff} (~{day_str} {w})"
                            except Exception:
                                deadline = "상시채용"
                        results.append({
                            "platform": "리멤버",
                            "external_id": jid,
                            "company": comp,
                            "title": title,
                            "url": f"https://career.rememberapp.co.kr/job/posting/{jid}",
                            "location": "",
                            "deadline": deadline
                        })
            except Exception:
                pass
    return results

def fetch_jobkorea(today_date):
    """잡코리아 (JobKorea) 모바일 수집 + 직무 검증"""
    results = []
    seen_links = set()
    queries = ["정보보안", "정보보호", "취약점 진단", "모의해킹"]
    for q in queries:
        for page in [1, 2]:
            url = f"https://m.jobkorea.co.kr/Search/Adv?Keyword={urllib.parse.quote(q)}&Page_No={page}"
            try:
                req = urllib.request.Request(url, headers=JOBKOREA_HEADERS)
                with urllib.request.urlopen(req, timeout=10) as res:
                    html_text = read_limited(res).decode("utf-8", errors="ignore")
                    items = html_text.split('class="section-item bg-white')[1:]
                    for it in items:
                        link_m = re.search(r'href="(/Recruit/GI_Read/\d+)[^"]*"', it)
                        comp_m = re.search(r'class="item-corp_name"[^>]*>(.*?)</(?:span|div)>', it, re.DOTALL)
                        tit_m = re.search(r'class="item-title"[^>]*>(.*?)</(?:span|div)>', it, re.DOTALL)
                        dday_m = re.search(r'class="item-condition_dday"[^>]*>(.*?)</span>', it, re.DOTALL)
                        loc_m = re.search(r'class="item-condition_location"[^>]*>(.*?)</span>', it, re.DOTALL)
                        
                        if comp_m and tit_m and link_m:
                            title = clean_text(tit_m.group(1))
                            if not is_security(title):
                                continue
                            link = "https://www.jobkorea.co.kr" + link_m.group(1).split("?")[0]
                            if link in seen_links:
                                continue
                            seen_links.add(link)
                            comp = clean_text(comp_m.group(1))
                            raw_dday = clean_text(dday_m.group(1)) if dday_m else "상시채용"
                            if "오늘" in raw_dday or raw_dday == "D-Day":
                                deadline = "D-Day (오늘 마감)"
                            elif "내일" in raw_dday or raw_dday == "D-1":
                                deadline = "D-1 (내일 마감)"
                            elif "채용시" in raw_dday:
                                deadline = "채용시 마감"
                            elif "상시" in raw_dday:
                                deadline = "상시채용"
                            else:
                                deadline = raw_dday
                                
                            results.append({
                                "platform": "잡코리아",
                                "external_id": (re.search(r"/GI_Read/(\d+)", link).group(1) if re.search(r"/GI_Read/(\d+)", link) else ""),
                                "company": comp,
                                "title": title,
                                "url": link,
                                "location": clean_text(loc_m.group(1)) if loc_m else "",
                                "deadline": deadline
                            })
            except Exception:
                pass
    return results

def fetch_incruit(today_date):
    """인크루트 (Incruit) 수집 + 직무 검증"""
    results = []
    seen_links = set()
    queries = ["정보보안", "정보보호", "취약점 진단", "모의해킹"]
    for q in queries:
        for page in [1, 2]:
            url = f"https://job.incruit.com/jobdb_list/searchjob.asp?kw={urllib.parse.quote(q)}&page={page}"
            try:
                req = urllib.request.Request(url, headers=INCRUIT_HEADERS)
                with urllib.request.urlopen(req, timeout=10) as res:
                    html_text = read_limited(res).decode("euc-kr", errors="ignore")
                    items = html_text.split('class="cell_first"')[1:]
                    for it in items:
                        cp_m = re.search(r'class="cpname"[^>]*>(.*?)</a>', it)
                        tit_m = re.search(r'<div class="cell_mid">.*?<div class="cl_top">.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', it, re.DOTALL)
                        date_m = re.search(r'<div class="cell_last">.*?<div class="cl_btm"><span>(.*?)</span>', it, re.DOTALL)
                        loc_m = re.search(r'<div class="cl_md"><span>(.*?)</span>', it, re.DOTALL)
                        
                        if cp_m and tit_m:
                            title = clean_text(tit_m.group(2))
                            if not is_security(title):
                                continue
                            link = tit_m.group(1).split("&src=")[0].strip()
                            if link in seen_links:
                                continue
                            seen_links.add(link)
                            comp = clean_text(cp_m.group(1))
                            raw_dl = clean_text(date_m.group(1)) if date_m else ""
                            deadline = "상시채용"
                            if "상시" in raw_dl:
                                deadline = "상시채용"
                            elif "채용시" in raw_dl:
                                deadline = "채용시 마감"
                            elif "오늘" in raw_dl:
                                deadline = "D-Day (오늘 마감)"
                            elif "내일" in raw_dl:
                                deadline = "D-1 (내일 마감)"
                            else:
                                m = re.search(r'(\d{1,2})\.(\d{1,2})', raw_dl)
                                if m:
                                    month, day = int(m.group(1)), int(m.group(2))
                                    year = today_date.year
                                    if month < today_date.month:
                                        year += 1
                                    target = date(year, month, day)
                                    diff = (target - today_date).days
                                    w_match = re.search(r'\(([월화수목금토일])\)', raw_dl)
                                    w_str = f" {w_match.group(1)}" if w_match else ""
                                    if diff < 0:
                                        deadline = f"마감 (~{month:02d}/{day:02d}{w_str})"
                                    elif diff == 0:
                                        deadline = f"D-Day (~{month:02d}/{day:02d}{w_str})"
                                    elif diff == 1:
                                        deadline = "D-1 (내일 마감)"
                                    else:
                                        deadline = f"D-{diff} (~{month:02d}/{day:02d}{w_str})"
                                else:
                                    time_only = re.match(r'^(\d\d?(?::\d\d)?)\s*시?\s*마감$', raw_dl)
                                    if time_only:
                                        # 인크루트는 마감 당일이면 '16시 마감'처럼 시각만 표기한다.
                                        # 날짜가 없으면 매일 D-Day로 남으므로 수집일(오늘)과 시각을 함께 표기한다.
                                        ws = ["월", "화", "수", "목", "금", "토", "일"][today_date.weekday()]
                                        deadline = (f"D-Day (~{today_date.month:02d}/{today_date.day:02d} {ws}) "
                                                    f"{time_only.group(1)}시 마감")
                                    else:
                                        deadline = raw_dl if raw_dl else "상시채용"
                            
                            results.append({
                                "platform": "인크루트",
                                "external_id": (re.search(r"[?&]job=(\d+)", link).group(1) if re.search(r"[?&]job=(\d+)", link) else ""),
                                "company": comp,
                                "title": title,
                                "url": link,
                                "location": clean_text(loc_m.group(1)) if loc_m else "",
                                "deadline": deadline
                            })
            except Exception:
                pass
    return results

def collect_all_jobs():
    today_date = get_today_kst()
    print("=== 정보보안 채용 정보 정밀 수집 시작 (6대 플랫폼 병렬) ===")
    
    tasks = {
        "원티드": lambda: fetch_wanted(),
        "점핏": lambda: fetch_jumpit(today_date),
        "사람인": lambda: fetch_saramin(today_date),
        "리멤버": lambda: fetch_remember(today_date),
        "잡코리아": lambda: fetch_jobkorea(today_date),
        "인크루트": lambda: fetch_incruit(today_date),
    }
    
    platform_results = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fn): name for name, fn in tasks.items()}
        for future in futures:
            name = futures[future]
            try:
                platform_results[name] = future.result(timeout=40)
            except Exception as e:
                print(f"[수집 경고] {name} 수집 실패 또는 타임아웃: {e}")
                platform_results[name] = []
                
    wanted_jobs = platform_results.get("원티드", [])
    jumpit_jobs = platform_results.get("점핏", [])
    saramin_jobs = platform_results.get("사람인", [])
    remember_jobs = platform_results.get("리멤버", [])
    jobkorea_jobs = platform_results.get("잡코리아", [])
    incruit_jobs = platform_results.get("인크루트", [])
    
    print(f"-> 플랫폼별 검증 수집 결과: 원티드 {len(wanted_jobs)}건, 점핏 {len(jumpit_jobs)}건, 사람인 {len(saramin_jobs)}건, 리멤버 {len(remember_jobs)}건, 잡코리아 {len(jobkorea_jobs)}건, 인크루트 {len(incruit_jobs)}건")
    raw_jobs = wanted_jobs + jumpit_jobs + saramin_jobs + remember_jobs + jobkorea_jobs + incruit_jobs
    print(f"-> 유효 보안 공고 총합: {len(raw_jobs)}건")
    
    # 중복 제거 및 직무 기반 정확한 카테고리 태깅
    #  ① 최우선: 플랫폼 + 공고 ID가 같으면 같은 공고(한 목록 안에서 두 번 나온 경우만 합친다).
    #  ② 제목 12자만 같은 다른 공고는 절대 합치지 않는다(플랫폼 ID가 다르면 다른 공고).
    #  ③ 서로 다른 플랫폼에 '완전히 같은 제목'으로 교차 게시된 공고만 1건으로 합쳐 플랫폼 배지를 붙인다.
    deduped = {}
    order = []
    for job in raw_jobs:
        if not job["company"] or not job["title"]:
            continue

        identity = job_external_identity(job)
        if identity:
            key = ("pid",) + identity
        else:
            # ID를 못 얻은 공고는 같은 플랫폼 안에서만 같은 제목으로 합친다.
            key = ("title", normalize_key(job["company"], job["title"]), job["platform"])

        if key not in deduped:
            deduped[key] = {
                "company": job["company"],
                "title": job["title"],
                "url": job["url"],
                "platforms": [job["platform"]],
                "external_id": job.get("external_id", ""),
                "keywords": assign_keywords(job["title"]),
                "location": job["location"],
                "deadline": job.get("deadline", "상시채용"),
            }
            order.append(key)
        else:
            _merge_same_posting(deduped[key], job)

    # ③ 플랫폼 교차 게시 병합 — 짧은 제목 키 후보가 '플랫폼마다 정확히 1건'이고
    #    회사·전체 제목이 완전히 같으며 같은 플랫폼에 다른 공고 ID가 섞여 있지 않을 때만.
    from db_manager import job_title_fingerprint, dedup_company_key as _dedup_company_key
    groups = {}
    for key in order:
        entry = deduped[key]
        groups.setdefault(normalize_key(entry["company"], entry["title"]), []).append(key)

    merged_into = {}
    for _short_key, keys in groups.items():
        if len(keys) < 2:
            continue
        seen_platforms = set()
        titles = set()
        companies = set()
        ambiguous = False
        for key in keys:
            entry = deduped[key]
            platform = entry["platforms"][0]
            if platform in seen_platforms:
                # 같은 플랫폼의 서로 다른 공고 ID → 어느 쪽이 같은 공고인지 알 수 없다.
                ambiguous = True
                break
            seen_platforms.add(platform)
            titles.add(job_title_fingerprint(entry["title"]))
            companies.add(_dedup_company_key(entry["company"]))
        if ambiguous or len(titles) != 1 or len(companies) != 1:
            continue

        primary_key = keys[0]
        primary = deduped[primary_key]
        for key in keys[1:]:
            other = deduped[key]
            for platform in other["platforms"]:
                if platform not in primary["platforms"]:
                    primary["platforms"].append(platform)
            if not primary["location"] and other["location"]:
                primary["location"] = other["location"]
            curr_dl = primary.get("deadline", "상시채용")
            new_dl = other.get("deadline", "상시채용")
            if ("상시" in curr_dl or "채용시" in curr_dl) and ("D-" in new_dl or "D-Day" in new_dl):
                primary["deadline"] = new_dl
            merged_into[key] = primary_key

    def get_deadline_sort_key(item):
        dl = item.get("deadline", "상시채용")
        if not dl:
            return (3, 999)
        if "D-Day" in dl or "오늘" in dl:
            return (0, 0)
        if "내일" in dl:
            return (0, 1)
        m = re.search(r"D-(\d+)", dl)
        if m:
            return (0, int(m.group(1)))
        if "채용시" in dl:
            return (1, 500)
        if "상시" in dl:
            return (2, 800)
        return (3, 999)

    job_list = [deduped[key] for key in order if key not in merged_into]
    # 플랫폼 공고 ID + 제목 지문 기반 키: 같은 통합 URL을 쓰는 다른 공고도 분리된다.
    from db_manager import make_job_key
    for job in job_list:
        job["job_key"] = make_job_key(
            job["company"], job["title"], job["url"],
            platforms=job["platforms"], platform=job["platforms"][0],
            external_id=job.get("external_id", ""),
        )
    job_list.sort(key=get_deadline_sort_key)
    print(f"-> 중복 제거 및 마감 임박 순 정렬 후 최종 공고: {len(job_list)}건")
    return job_list

_WATCH_CSS = """
    /* ---- 관심 목록(상태·메모) · 저장 검색 ---- */
    .job-card { padding: 0; }
    .job-card-link {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      flex: 1 1 auto;
      min-width: 0;
      padding: 18px 20px 12px;
      text-decoration: none;
      color: inherit;
    }
    .job-card.is-watched { border-color: #bfdbfe; }
    .job-watch {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 0 14px 12px 14px;
      min-width: 0;
    }
    .watch-btn {
      flex: 0 0 auto;
      width: 30px;
      height: 30px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      border: 1px solid var(--border-default);
      border-radius: 8px;
      background: var(--bg-surface);
      color: var(--text-muted);
      cursor: pointer;
      transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease, transform 150ms ease;
    }
    .watch-btn svg { fill: none; }
    .watch-btn:hover { border-color: var(--border-strong); color: var(--text-secondary); }
    .watch-btn:active { transform: scale(0.94); }
    .watch-btn.is-on { color: var(--accent-primary); border-color: #bfdbfe; background: var(--accent-subtle); }
    .watch-btn.is-on svg { fill: currentColor; }
    .status-select {
      flex: 0 0 auto;
      max-width: 96px;
      padding: 5px 6px;
      border: 1px solid var(--border-default);
      border-radius: 8px;
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
    }
    .status-select.is-off { color: var(--text-muted); font-weight: 500; }
    .job-watch[data-status="지원예정"] .status-select { color: #1d4ed8; border-color: #bfdbfe; background: #eff6ff; }
    .job-watch[data-status="지원완료"] .status-select { color: #047857; border-color: #a7f3d0; background: #ecfdf5; }
    .job-watch[data-status="면접"] .status-select { color: #b45309; border-color: #fed7aa; background: #fff7ed; }
    .job-watch[data-status="보류"] .status-select { color: #475569; border-color: #e2e8f0; background: #f1f5f9; }
    .memo-input {
      flex: 1 1 auto;
      min-width: 0;
      padding: 6px 9px;
      border: 1px solid var(--border-default);
      border-radius: 8px;
      background: var(--bg-surface);
      color: var(--text-primary);
      font-family: inherit;
      font-size: 12px;
      line-height: 1.3;
    }
    .memo-input::placeholder { color: var(--text-muted); }
    .memo-input:focus { outline: none; border-color: var(--accent-primary); box-shadow: 0 0 0 3px var(--accent-subtle); }

    .list-item { border-bottom: 1px solid var(--border-subtle); }
    .list-item:last-child { border-bottom: none; }
    .list-item .list-row { border-bottom: 0; }
    .job-watch.is-list { justify-content: flex-end; padding: 0 18px 10px; }
    .job-watch.is-list .memo-input { flex: 0 1 320px; }

    .watch-archive {
      margin: 0 0 16px;
      padding: 14px 16px;
      border: 1px solid var(--border-default);
      border-radius: 12px;
      background: var(--bg-surface);
      box-shadow: var(--card-shadow);
    }
    .watch-archive[hidden] { display: none; }
    .watch-archive-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
    .watch-archive-title { font-size: 13.5px; font-weight: 700; letter-spacing: -0.01em; }
    .watch-archive-count { font-size: 11px; font-weight: 700; color: var(--text-secondary); background: var(--bg-subtle); border-radius: 6px; padding: 1px 6px; }
    .watch-archive-desc { flex-basis: 100%; font-size: 12px; color: var(--text-muted); margin-top: 4px; }
    .watch-arch-item { padding: 11px 0 6px; border-top: 1px solid var(--border-subtle); margin-top: 10px; }
    .watch-arch-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
    .watch-arch-meta { min-width: 0; }
    .watch-arch-company { display: block; font-size: 11.5px; font-weight: 600; color: var(--text-muted); }
    .watch-arch-title { display: block; font-size: 13.5px; font-weight: 600; color: var(--text-primary); line-height: 1.4; }
    .watch-arch-deadline { display: inline-block; margin-top: 3px; font-size: 11px; color: var(--text-muted); }
    .watch-arch-actions { display: flex; align-items: center; gap: 6px; flex: 0 0 auto; }
    .watch-arch-link, .watch-arch-remove {
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-secondary);
      text-decoration: none;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      border-radius: 7px;
      padding: 4px 8px;
      cursor: pointer;
    }
    .watch-arch-link:hover, .watch-arch-remove:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .watch-arch-remove { color: #b91c1c; }
    .job-watch.is-arch { padding: 0; }

    .save-search-btn {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--border-default);
      border-radius: 9px;
      background: var(--bg-page);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: border-color 150ms ease, color 150ms ease;
    }
    .save-search-btn:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .save-search-btn:active { transform: scale(0.99); }
    .saved-chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .saved-empty { font-size: 11.5px; color: var(--text-muted); }
    .saved-chip { display: inline-flex; align-items: center; border: 1px solid var(--border-default); border-radius: 999px; background: var(--bg-page); max-width: 100%; }
    .saved-chip-apply {
      border: 0;
      background: transparent;
      padding: 5px 4px 5px 10px;
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-primary);
      cursor: pointer;
      max-width: 168px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .saved-chip-del { border: 0; background: transparent; padding: 4px 8px 4px 2px; font-size: 13px; line-height: 1; color: var(--text-muted); cursor: pointer; }
    .saved-chip-del:hover { color: #b91c1c; }
    .filter-pill-count { margin-left: 4px; font-size: 10px; font-weight: 700; color: var(--accent-primary); }

    @media (max-width: 640px) {
      .job-card-link { padding: 14px 16px 10px; }
      .job-watch { flex-wrap: wrap; padding: 0 12px 10px 12px; }
      .memo-input { flex: 1 1 140px; }
      .status-select { max-width: 88px; }
      .watch-arch-top { flex-direction: column; gap: 6px; }
      .job-watch.is-list { justify-content: flex-start; padding: 0 14px 10px; }
      .job-watch.is-list .memo-input { flex: 1 1 140px; }
    }
    @media (prefers-reduced-motion: reduce) {
      .watch-btn, .save-search-btn { transition: none; }
    }
"""

_WATCH_JS = """
    // ===== 관심 목록(상태·한 줄 메모) + 저장 검색 =====
    // 저장 위치는 브라우저 localStorage 뿐이고, 서버로는 아무것도 보내지 않는다.
    // 사용자가 입력한 메모·검색어는 전부 textContent / input.value 로만 그려서
    // <img onerror=...> 같은 문자열이 마크업으로 해석되지 않게 한다.
    var WATCH_STORE_KEY = 'secjobs-watchlist-v1';
    var SAVED_SEARCH_KEY = 'secjobs-saved-searches-v1';
    var WATCH_STATUSES = ['관심', '지원예정', '지원완료', '면접', '보류'];
    var STAR_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true"><path d="M12 17.6l-5.7 3 1.1-6.4-4.6-4.5 6.4-.9L12 3l2.8 5.8 6.4.9-4.6 4.5 1.1 6.4z"></path></svg>';

    var watchlist = readStore(WATCH_STORE_KEY, sanitizeWatchStore);
    var savedSearches = readStore(SAVED_SEARCH_KEY, sanitizeSavedSearches);
    var jobByKey = {};

    function readStore(key, sanitize) {
      try {
        var raw = localStorage.getItem(key);
        return sanitize(raw ? JSON.parse(raw) : null);
      } catch (err) {
        return sanitize(null);
      }
    }

    function sanitizeWatchStore(parsed) {
      var clean = {};
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return clean;
      Object.keys(parsed).forEach(function (key) {
        var item = parsed[key];
        if (!item || typeof item !== 'object') return;
        if (typeof item.company !== 'string' || typeof item.title !== 'string') return;
        clean[String(key)] = {
          key: String(key),
          company: item.company,
          title: item.title,
          url: typeof item.url === 'string' ? item.url : '',
          platforms: Array.isArray(item.platforms) ? item.platforms.filter(function (p) { return typeof p === 'string'; }) : [],
          deadline: typeof item.deadline === 'string' ? item.deadline : '',
          status: WATCH_STATUSES.indexOf(item.status) >= 0 ? item.status : '관심',
          memo: typeof item.memo === 'string' ? item.memo.slice(0, 120) : '',
          watched_at: typeof item.watched_at === 'string' ? item.watched_at : '',
          updated_at: typeof item.updated_at === 'string' ? item.updated_at : ''
        };
      });
      return clean;
    }

    function sanitizeSavedSearches(parsed) {
      if (!Array.isArray(parsed)) return [];
      return parsed.filter(function (item) {
        return item && typeof item === 'object' && typeof item.label === 'string' && item.state && typeof item.state === 'object';
      }).slice(0, 8).map(function (item) {
        return {
          id: typeof item.id === 'string' ? item.id : ('ss' + Math.random().toString(36).slice(2, 8)),
          label: item.label.slice(0, 60),
          signature: typeof item.signature === 'string' ? item.signature : '',
          state: item.state,
          saved_at: typeof item.saved_at === 'string' ? item.saved_at : ''
        };
      });
    }

    function persistStore(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch (err) {
        // 저장 공간을 쓰지 못해도 화면 동작은 유지한다.
      }
    }

    function persistWatch() { persistStore(WATCH_STORE_KEY, watchlist); }
    function persistSavedSearches() { persistStore(SAVED_SEARCH_KEY, savedSearches); }

    function rememberJob(job) {
      if (!job || typeof job.job_key !== 'string' || !job.job_key) return null;
      var key = job.job_key;
      var now = new Date().toISOString();
      var entry = watchlist[key];
      if (!entry) {
        entry = watchlist[key] = {
          key: key,
          company: typeof job.company === 'string' ? job.company : '',
          title: typeof job.title === 'string' ? job.title : '',
          url: safeUrl(job.url),
          platforms: Array.isArray(job.platforms) ? job.platforms.filter(function (p) { return typeof p === 'string'; }).slice(0, 6) : [],
          deadline: typeof job.deadline_label === 'string' ? job.deadline_label : (typeof job.deadline === 'string' ? job.deadline : ''),
          status: '관심',
          memo: '',
          watched_at: now,
          updated_at: now
        };
      }
      persistWatch();
      return entry;
    }

    function updateWatchEntry(key, patch) {
      var job = jobByKey[key];
      var entry = watchlist[key] || (job ? rememberJob(job) : null);
      if (!entry) return null;
      Object.keys(patch || {}).forEach(function (field) {
        if (field === 'status') {
          if (WATCH_STATUSES.indexOf(patch.status) >= 0) entry.status = patch.status;
          return;
        }
        if (field === 'memo') {
          entry.memo = String(patch.memo == null ? '' : patch.memo).slice(0, 120);
          return;
        }
        entry[field] = patch[field];
      });
      entry.updated_at = new Date().toISOString();
      persistWatch();
      return entry;
    }

    function forgetJob(key) {
      if (!watchlist[key]) return;
      delete watchlist[key];
      persistWatch();
      refreshWatchSurface();
    }

    function toggleWatch(key) {
      if (watchlist[key]) forgetJob(key);
      else if (rememberJob(jobByKey[key])) refreshWatchSurface();
      renderFeed();
    }

    function setWatchStatus(key, status) {
      if (!updateWatchEntry(key, { status: status })) return;
      updateWatchCounts();
      syncWatchNode(key);
    }

    function setWatchMemo(key, memo) {
      if (!watchlist[key] && !String(memo || '').trim()) return;
      if (!updateWatchEntry(key, { memo: memo })) return;
      updateWatchCounts();
      syncWatchNode(key);
    }

    function updateWatchCounts() {
      var countEl = document.getElementById('watchFilterCount');
      if (countEl) countEl.textContent = String(Object.keys(watchlist).length);
      return Object.keys(watchlist).length;
    }

    function syncWatchNode(key) {
      var entry = watchlist[key] || null;
      var nodes = document.querySelectorAll('[data-watch-for]');
      for (var i = 0; i < nodes.length; i += 1) {
        var node = nodes[i];
        if (node.getAttribute('data-watch-for') !== key) continue;
        var star = node.querySelector('[data-watch-toggle]');
        if (star) {
          star.classList.toggle('is-on', !!entry);
          star.setAttribute('aria-pressed', entry ? 'true' : 'false');
          var label = entry ? '관심 해제' : '관심 등록';
          star.setAttribute('aria-label', label);
          star.setAttribute('title', label);
        }
        var select = node.querySelector('[data-watch-status]');
        var memoInput = node.querySelector('[data-watch-memo]');
        if (select) {
          select.classList.toggle('is-off', !entry);
          if (entry) select.value = entry.status;
        }
        if (memoInput && entry && memoInput.value !== entry.memo && document.activeElement !== memoInput) {
          memoInput.value = entry.memo;
        }
      }
      var cards = document.querySelectorAll('.job-card.is-watched, .job-card');
      for (var j = 0; j < cards.length; j += 1) {
        var card = cards[j];
        if (card.getAttribute('data-key') !== key) continue;
        card.classList.toggle('is-watched', !!entry);
      }
      var items = document.querySelectorAll('.job-watch[data-watch-for]');
      for (var k = 0; k < items.length; k += 1) {
        if (items[k].getAttribute('data-watch-for') === key) {
          items[k].setAttribute('data-status', entry ? entry.status : '관심');
        }
      }
    }

    function buildStatusSelect(key, status, off) {
      var select = document.createElement('select');
      select.className = 'status-select' + (off ? ' is-off' : '');
      select.setAttribute('data-watch-status', key);
      select.setAttribute('aria-label', '진행 상태');
      WATCH_STATUSES.forEach(function (label) {
        var option = document.createElement('option');
        option.value = label;
        option.textContent = label;
        select.appendChild(option);
      });
      select.value = WATCH_STATUSES.indexOf(status) >= 0 ? status : '관심';
      return select;
    }

    function buildMemoInput(key, memo, ariaLabel) {
      var input = document.createElement('input');
      input.type = 'text';
      input.className = 'memo-input';
      input.setAttribute('data-watch-memo', key);
      input.setAttribute('maxlength', '120');
      input.setAttribute('placeholder', '한 줄 메모');
      input.setAttribute('aria-label', ariaLabel || '한 줄 메모');
      input.value = typeof memo === 'string' ? memo : '';
      return input;
    }

    function buildJobWatch(job) {
      var key = job.job_key;
      var entry = watchlist[key] || null;
      var wrap = document.createElement('div');
      wrap.className = 'job-watch';
      wrap.setAttribute('data-watch-for', key);
      wrap.setAttribute('data-status', entry ? entry.status : '관심');

      var star = document.createElement('button');
      star.type = 'button';
      star.className = 'watch-btn' + (entry ? ' is-on' : '');
      star.setAttribute('data-watch-toggle', key);
      star.setAttribute('aria-pressed', entry ? 'true' : 'false');
      star.setAttribute('title', entry ? '관심 해제' : '관심 등록');
      star.setAttribute('aria-label', entry ? '관심 해제' : '관심 등록');
      star.innerHTML = STAR_SVG;
      wrap.appendChild(star);

      wrap.appendChild(buildStatusSelect(key, entry ? entry.status : '관심', !entry));
      wrap.appendChild(buildMemoInput(key, entry ? entry.memo : '', (job.company || '') + ' ' + (job.title || '') + ' 한 줄 메모'));
      return wrap;
    }

    function hydrateWatchSlots(root) {
      if (!root || !root.querySelectorAll) return;
      var slots = root.querySelectorAll('[data-watch-slot]');
      for (var i = 0; i < slots.length; i += 1) {
        var slot = slots[i];
        var card = slot.parentElement;
        while (card && !card.getAttribute('data-key')) card = card.parentElement;
        if (!card) continue;
        var key = card.getAttribute('data-key') || '';
        var job = jobByKey[key];
        if (!job) continue;
        var built = buildJobWatch(job);
        // 그리드/리스트 슬롯이 가진 클래스(예: is-list 여백)를 그대로 이어받는다.
        built.className = slot.className;
        slot.replaceWith(built);
      }
    }

    function buildArchiveItem(entry) {
      var item = document.createElement('div');
      item.className = 'watch-arch-item';
      item.setAttribute('data-watch-for', entry.key);

      var top = document.createElement('div');
      top.className = 'watch-arch-top';

      var meta = document.createElement('div');
      meta.className = 'watch-arch-meta';
      var company = document.createElement('span');
      company.className = 'watch-arch-company';
      company.textContent = entry.company || '회사명 없음';
      meta.appendChild(company);
      var title = document.createElement('span');
      title.className = 'watch-arch-title';
      title.textContent = entry.title || '제목 없음';
      meta.appendChild(title);
      if (entry.deadline) {
        var deadline = document.createElement('span');
        deadline.className = 'watch-arch-deadline';
        deadline.textContent = entry.deadline;
        meta.appendChild(deadline);
      }
      top.appendChild(meta);

      var actions = document.createElement('div');
      actions.className = 'watch-arch-actions';
      var link = document.createElement('a');
      link.className = 'watch-arch-link';
      link.href = safeUrl(entry.url);
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = '원문';
      actions.appendChild(link);
      var remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'watch-arch-remove';
      remove.setAttribute('data-watch-remove', entry.key);
      remove.setAttribute('aria-label', (entry.company || '') + ' ' + (entry.title || '') + ' 관심 목록에서 삭제');
      remove.textContent = '삭제';
      actions.appendChild(remove);
      top.appendChild(actions);
      item.appendChild(top);

      var controls = document.createElement('div');
      controls.className = 'job-watch is-arch';
      controls.setAttribute('data-status', entry.status);
      controls.appendChild(buildStatusSelect(entry.key, entry.status, false));
      controls.appendChild(buildMemoInput(entry.key, entry.memo, (entry.company || '') + ' ' + (entry.title || '') + ' 한 줄 메모'));
      item.appendChild(controls);
      return item;
    }

    function renderWatchArchive() {
      var section = document.getElementById('watchArchive');
      var list = document.getElementById('watchArchiveList');
      var countEl = document.getElementById('watchArchiveCount');
      if (!section || !list) return;
      var live = {};
      getLiveJobs().forEach(function (job) { if (job && job.job_key) live[job.job_key] = true; });
      var archived = Object.keys(watchlist)
        .filter(function (key) { return !live[key]; })
        .map(function (key) { return watchlist[key]; })
        .sort(function (a, b) { return String(b.updated_at || '').localeCompare(String(a.updated_at || '')); });
      list.replaceChildren();
      archived.forEach(function (entry) { list.appendChild(buildArchiveItem(entry)); });
      if (countEl) countEl.textContent = archived.length + '건';
      section.hidden = archived.length === 0;
    }

    function refreshWatchSurface() {
      updateWatchCounts();
      renderWatchArchive();
    }

    // ---- 저장 검색 ----
    function currentSearchState() {
      return {
        query: searchTerm,
        keyword: selectedKeyword,
        platform: selectedPlatform,
        deadline: selectedDeadline,
        sort: sortBy,
        watch: selectedWatch
      };
    }

    function searchLabel(state) {
      var parts = [];
      if (state.query) parts.push('"' + state.query + '"');
      if (state.keyword && state.keyword !== 'all') parts.push(state.keyword);
      if (state.platform && state.platform !== 'all') parts.push(state.platform);
      if (state.deadline === 'urgent') parts.push('마감임박');
      else if (state.deadline === 'always') parts.push('상시');
      if (state.watch === 'watch') parts.push('관심만');
      var label = parts.length ? parts.join(' · ') : '전체 조건';
      if (state.sort === 'company') label += ' · 회사명순';
      else if (state.sort === 'default') label += ' · 등록순';
      return label;
    }

    function saveCurrentSearch() {
      var state = currentSearchState();
      var signature = JSON.stringify(state);
      var duplicate = null;
      for (var i = 0; i < savedSearches.length; i += 1) {
        if (savedSearches[i].signature === signature) { duplicate = savedSearches[i]; break; }
      }
      if (duplicate) {
        duplicate.saved_at = new Date().toISOString();
        persistSavedSearches();
        renderSavedSearches();
        return;
      }
      savedSearches.unshift({
        id: 'ss' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5),
        label: searchLabel(state),
        signature: signature,
        state: state,
        saved_at: new Date().toISOString()
      });
      if (savedSearches.length > 8) savedSearches = savedSearches.slice(0, 8);
      persistSavedSearches();
      renderSavedSearches();
    }

    function removeSavedSearch(id) {
      savedSearches = savedSearches.filter(function (item) { return item.id !== id; });
      persistSavedSearches();
      renderSavedSearches();
    }

    function findSavedSearch(id) {
      for (var i = 0; i < savedSearches.length; i += 1) {
        if (savedSearches[i].id === id) return savedSearches[i];
      }
      return null;
    }

    function renderSavedSearches() {
      var box = document.getElementById('savedSearchList');
      if (!box) return;
      box.replaceChildren();
      if (!savedSearches.length) {
        var hint = document.createElement('p');
        hint.className = 'saved-empty';
        hint.textContent = '저장한 검색이 없습니다.';
        box.appendChild(hint);
        return;
      }
      savedSearches.forEach(function (item) {
        var chip = document.createElement('span');
        chip.className = 'saved-chip';
        var apply = document.createElement('button');
        apply.type = 'button';
        apply.className = 'saved-chip-apply';
        apply.setAttribute('data-saved-apply', item.id);
        apply.setAttribute('title', item.label + ' 조건으로 보기');
        apply.textContent = item.label;
        var del = document.createElement('button');
        del.type = 'button';
        del.className = 'saved-chip-del';
        del.setAttribute('data-saved-delete', item.id);
        del.setAttribute('aria-label', item.label + ' 저장 검색 삭제');
        del.textContent = '×';
        chip.appendChild(apply);
        chip.appendChild(del);
        box.appendChild(chip);
      });
    }

    function syncFilterButtons() {
      document.querySelectorAll('#keywordNav .segment-btn').forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-kw') === selectedKeyword);
      });
      document.querySelectorAll('.filter-pill').forEach(function (pill) {
        var type = pill.getAttribute('data-filter');
        var value = pill.getAttribute('data-val');
        if (type === 'platform') pill.classList.toggle('active', value === selectedPlatform);
        else if (type === 'deadline') pill.classList.toggle('active', value === selectedDeadline);
        else if (type === 'watch') pill.classList.toggle('active', value === selectedWatch);
      });
    }

    function applySearchState(state) {
      if (!state) return;
      searchTerm = typeof state.query === 'string' ? state.query : '';
      searchInput.value = searchTerm;
      clearSearchBtn.style.display = searchTerm ? 'block' : 'none';
      selectedKeyword = typeof state.keyword === 'string' ? state.keyword : 'all';
      selectedPlatform = typeof state.platform === 'string' ? state.platform : 'all';
      selectedDeadline = typeof state.deadline === 'string' ? state.deadline : 'all';
      selectedWatch = state.watch === 'watch' ? 'watch' : 'all';
      sortBy = typeof state.sort === 'string' ? state.sort : 'deadline';
      if (sortSelect) sortSelect.value = sortBy;
      if (sortSelectMobile) sortSelectMobile.value = sortBy;
      syncFilterButtons();
      renderFeed();
      if (filterRail && filterRail.classList.contains('is-open')) closeFilterSheet();
    }

    // ---- 이벤트 ----
    document.addEventListener('click', function (event) {
      var target = event.target;
      if (!target || !target.closest) return;
      var toggle = target.closest('[data-watch-toggle]');
      if (toggle) {
        event.preventDefault();
        toggleWatch(toggle.getAttribute('data-watch-toggle'));
        return;
      }
      var remove = target.closest('[data-watch-remove]');
      if (remove) {
        event.preventDefault();
        forgetJob(remove.getAttribute('data-watch-remove'));
        renderFeed();
        return;
      }
      var apply = target.closest('[data-saved-apply]');
      if (apply) {
        event.preventDefault();
        var saved = findSavedSearch(apply.getAttribute('data-saved-apply'));
        if (saved) applySearchState(saved.state);
        return;
      }
      var del = target.closest('[data-saved-delete]');
      if (del) {
        event.preventDefault();
        removeSavedSearch(del.getAttribute('data-saved-delete'));
      }
    });

    document.addEventListener('change', function (event) {
      var target = event.target;
      if (target && target.matches && target.matches('[data-watch-status]')) {
        setWatchStatus(target.getAttribute('data-watch-status'), target.value);
      }
    });

    document.addEventListener('input', function (event) {
      var target = event.target;
      if (target && target.matches && target.matches('[data-watch-memo]')) {
        setWatchMemo(target.getAttribute('data-watch-memo'), target.value);
      }
    });

    function initWatchFeatures() {
      for (var i = 0; i < JOBS.length; i += 1) {
        var job = JOBS[i];
        if (job && typeof job.job_key === 'string') jobByKey[job.job_key] = job;
      }
      var saveBtn = document.getElementById('saveSearchBtn');
      if (saveBtn) saveBtn.addEventListener('click', saveCurrentSearch);
      renderSavedSearches();
      updateWatchCounts();
      renderFeed();
    }

    initWatchFeatures();
"""

def generate_html(jobs, update_time_str):
    """GitHub Pages 배포용 정적 웹 대시보드 (프로덕트급 미니멀 UI/UX)"""
    # <script> 블록 안의 JSON 은 "</" 로 조기 종료되지 않게 중화하고, 외부 수집 URL 은 스킴을 검증해 심는다.
    _jobs_for_embed = []
    for _j in jobs:
        if isinstance(_j, dict):
            _c = dict(_j)
            _c["url"] = safe_url(_c.get("url"))
            _jobs_for_embed.append(_c)
    jobs_json_str = safe_json_for_script(json.dumps(_jobs_for_embed, ensure_ascii=False))
    
    kw_counts = {}
    for kw in KEYWORDS:
        kw_counts[kw] = sum(1 for j in jobs if kw in j.get("keywords", []))
        
    urgent_count = count_urgent_jobs(jobs)

    # 상단 KPI: 오늘 마감 / 이번 주 마감 / 오늘 새로 수집된 공고
    from db_manager import compute_remaining_days
    _today = datetime.now(timezone(timedelta(hours=9))).date()
    due_today = 0
    due_week = 0
    new_today = 0
    for _job in jobs:
        _days = compute_remaining_days(_job.get("deadline"), _today, _job.get("last_seen_at"))
        if _days is not None and _days >= 0:
            if _days == 0:
                due_today += 1
            if _days <= 7:
                due_week += 1
        if (_job.get("first_seen_at") or "")[:10] == _today.isoformat():
            new_today += 1

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 정보보안 포지션 아카이브</title>
  <meta name="description" content="원티드 · 점핏 · 사람인 · 리멤버 · 잡코리아 · 인크루트의 보안 포지션을 직무 검증을 거쳐 선별하고 중복 없이 아카이빙하는 정보공유 플랫폼입니다.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" integrity="sha384-SN6A48CJQjx946+DRb8wsoifC4a8ur9ZS6R+HCTgnBHOKCa6GLXAR3Qn8d1jztxg" crossorigin="anonymous" />
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

      --remember-bg: #f8fafc;
      --remember-text: #0f172a;
      --remember-border: #cbd5e1;

      --jobkorea-bg: #f0f9ff;
      --jobkorea-text: #0284c7;
      --jobkorea-border: #bae6fd;

      --incruit-bg: #fff1f2;
      --incruit-text: #e11d48;
      --incruit-border: #fecdd3;
      
      --urgent-bg: #fef2f2;
      --urgent-text: #dc2626;
      --urgent-border: #fecaca;
      
      --warning-bg: #fff7ed;
      --warning-text: #ea580c;
      --warning-border: #fed7aa;
      
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

      --remember-bg: rgba(148, 163, 184, 0.15);
      --remember-text: #e2e8f0;
      --remember-border: rgba(148, 163, 184, 0.3);

      --jobkorea-bg: rgba(2, 132, 199, 0.15);
      --jobkorea-text: #38bdf8;
      --jobkorea-border: rgba(2, 132, 199, 0.3);

      --incruit-bg: rgba(225, 29, 72, 0.15);
      --incruit-text: #fb7185;
      --incruit-border: rgba(225, 29, 72, 0.3);
      
      --warning-bg: rgba(234, 88, 12, 0.15);
      --warning-text: #fb923c;
      --warning-border: rgba(234, 88, 12, 0.3);
      
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
      max-width: 1360px;
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

    .brand-logo-img {{
      width: 28px;
      height: 28px;
      border-radius: 7px;
      object-fit: cover;
      display: block;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
      flex-shrink: 0;
    }}

    .brand-name {{
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
    }}

    .nav-tabs {{
      display: flex;
      gap: 5px;
      margin-left: 10px;
      flex: 1 1 auto;
      min-width: 0;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }}

    .nav-tabs::-webkit-scrollbar {{ display: none; }}

    .nav-tab-item {{
      padding: 5px 10px;
      border-radius: 18px;
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      color: var(--text-secondary);
      transition: all 0.15s ease;
      white-space: nowrap;
    }}

    .nav-tab-item:hover {{
      background: var(--bg-subtle);
      color: var(--text-primary);
    }}

    .nav-tab-item.active {{
      background: var(--accent-primary);
      color: #ffffff !important;
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
      flex-direction: column;
      gap: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--border-subtle);
    }}

    @media (min-width: 860px) {{
      .sub-toolbar {{
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
      }}
    }}

    .filter-controls-wrap {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px 18px;
    }}

    .filter-row {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .filter-label {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      margin-right: 2px;
      white-space: nowrap;
    }}

    .filter-pills-scroll {{
      display: flex;
      align-items: center;
      gap: 4px;
      overflow-x: auto;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
      padding-bottom: 2px;
    }}
    .filter-pills-scroll::-webkit-scrollbar {{ display: none; }}

    .filter-pill {{
      flex-shrink: 0;
      white-space: nowrap;
      padding: 5px 10px;
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
      min-width: 0;
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

    .badge-dl-warning {{
      background: var(--warning-bg);
      color: var(--warning-text);
      border: 1px solid var(--warning-border);
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

    .badge-platform-리멤버 {{
      background: var(--remember-bg);
      color: var(--remember-text);
      border: 1px solid var(--remember-border);
    }}

    .badge-platform-잡코리아 {{
      background: var(--jobkorea-bg);
      color: var(--jobkorea-text);
      border: 1px solid var(--jobkorea-border);
    }}

    .badge-platform-인크루트 {{
      background: var(--incruit-bg);
      color: var(--incruit-text);
      border: 1px solid var(--incruit-border);
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

    .job-summary {{
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.45;
      margin-top: -6px;
      margin-bottom: 12px;
      word-break: keep-all;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .ai-tag {{
      background: var(--bg-subtle);
      border-color: var(--border-default);
      color: var(--text-secondary);
      font-weight: 500;
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
      min-width: 0;
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
      gap: 5px;
      flex-shrink: 0;
      transition: transform 0.15s ease, color 0.15s ease;
    }}

    .outlink-host {{
      font-size: 11px;
      line-height: 1.2;
      max-width: 132px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
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
      grid-template-columns: 140px 1fr 110px 70px auto;
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

    .list-summary {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
      font-weight: 400;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
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
      gap: 5px;
      min-width: 0;
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

    /* Mobile Responsive Polish */
    @media (max-width: 640px) {{
      .nav-container {{
        padding: 0 12px;
        height: 54px;
        gap: 6px;
      }}
      .brand-name {{
        font-size: 15px;
      }}
      .brand-logo-img {{
        width: 24px;
        height: 24px;
      }}
      .nav-tabs {{
        margin-left: 6px;
        gap: 4px;
      }}
      .nav-tab-item {{
        padding: 4px 8px;
        font-size: 11.5px;
        border-radius: 14px;
      }}
      .update-meta {{
        display: none !important;
      }}
      .nav-actions a.icon-btn {{
        display: none;
      }}
      .container {{
        padding: 16px 12px 60px;
      }}
      .hero {{
        margin-bottom: 18px;
      }}
      .hero-title {{
        font-size: 21px;
      }}
      .hero-desc {{
        font-size: 13px;
        line-height: 1.5;
      }}
      .hero-stats {{
        gap: 6px;
      }}
      .stat-chip {{
        font-size: 11px;
        padding: 3px 8px;
      }}
      .toolbar {{
        padding: 12px;
        border-radius: 12px;
        gap: 10px;
      }}
      .search-input {{
        padding: 9px 34px 9px 36px;
        font-size: 13px;
      }}
      .segment-btn {{
        padding: 6px 10px;
        font-size: 12px;
      }}
      .sub-toolbar {{
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
      }}
      .filter-controls-wrap {{
        flex-direction: column;
        align-items: stretch;
        gap: 8px;
      }}
      .filter-row {{
        width: 100%;
      }}
      .view-actions {{
        width: 100%;
        justify-content: space-between;
      }}
      .sort-select {{
        flex: 1;
      }}
      .jobs-grid {{
        grid-template-columns: 1fr !important;
        gap: 12px;
      }}
      .job-card {{
        padding: 14px 16px;
      }}
      .job-title {{
        font-size: 14.5px;
        line-height: 1.45;
      }}
    }}

    /* 내비게이션 7탭 수용: 좁은 화면에서는 브랜드 텍스트 숨김 */
    @media (max-width: 560px) {{
      .brand-name {{
        display: none;
      }}
    }}

    @media (max-width: 430px) {{
      .nav-container {{
        padding: 0 10px;
        height: 52px;
        gap: 6px;
      }}
      .brand-logo-img {{
        width: 22px;
        height: 22px;
      }}
      .nav-tabs {{
        margin-left: 2px;
        gap: 2px;
      }}
      .nav-tab-item {{
        padding: 4px 6px;
        font-size: 10.5px;
        border-radius: 12px;
        letter-spacing: -0.03em;
      }}
      .nav-actions .icon-btn {{
        width: 30px;
        height: 30px;
      }}
    }}

    /* 내비게이션 8탭(피싱 레이더 추가) 대응: 넘침 없이 한 줄 유지 */
    @media (max-width: 1440px) {{
      .nav-container {{ max-width: 1360px; padding: 0 16px; }}
      .nav-tabs {{ gap: 4px; margin-left: 8px; }}
      .nav-tab-item {{ padding: 4px 8px; font-size: 11.5px; }}
    }}

    @media (max-width: 1024px) {{
      .nav-brand {{ min-width: 0; }}
      .nav-tabs {{ flex: 1 1 auto; min-width: 0; overflow-x: auto; white-space: nowrap; scrollbar-width: none; -ms-overflow-style: none; }}
      .nav-tabs::-webkit-scrollbar {{ display: none; }}
      .nav-tab-item {{ padding: 4px 7px; font-size: 11px; }}
    }}

    @media (max-width: 430px) {{
      .nav-container {{ padding: 0 8px; gap: 4px; }}
      .nav-tabs {{ margin-left: 2px; gap: 1px; }}
      .nav-tab-item {{ padding: 4px 5px; font-size: 10px; border-radius: 11px; letter-spacing: -0.045em; }}
      .nav-actions {{ gap: 4px; }}
      .nav-actions .icon-btn {{ width: 28px; height: 28px; }}
    }}

    /* ===== 채용공고 PC/모바일 분리 레이아웃 (1차 UI/UX 개편) ===== */
    .ia-overview {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 20px;
    }}
    .ia-overview-copy {{ min-width: 0; }}
    .ia-overview .hero-title {{ margin-bottom: 6px; }}
    .ia-overview .hero-desc {{ margin-bottom: 0; }}
    .ia-quick-link {{
      display: inline-flex; align-items: center; gap: 8px; margin-top: 12px;
      padding: 9px 12px; border: 1px solid var(--border-default); border-radius: 11px;
      background: var(--bg-surface); color: var(--text-primary); text-decoration: none;
      font-size: 12.5px; font-weight: 600; max-width: 100%;
      transition: background-color 150ms ease, border-color 150ms ease, transform 150ms ease;
    }}
    .ia-quick-link:hover {{ background: var(--bg-subtle); border-color: var(--border-strong); }}
    .ia-quick-link:active {{ transform: scale(0.99); }}
    .ia-quick-kicker {{ flex: 0 0 auto; font-weight: 700; color: var(--accent-primary); }}
    .ia-quick-text {{
      min-width: 0; color: var(--text-secondary);
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .ia-quick-link svg {{ width: 14px; height: 14px; color: var(--text-muted); flex: 0 0 auto; }}
    .ia-kpis {{ display: flex; gap: 8px; flex: 0 0 auto; }}
    .ia-kpi {{
      min-width: 98px;
      padding: 9px 12px 10px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      box-shadow: var(--card-shadow);
    }}
    .ia-kpi-label {{ display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 2px; white-space: nowrap; }}
    .ia-kpi-value {{ font-size: 19px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); font-variant-numeric: tabular-nums; }}
    .ia-kpi-unit {{ font-size: 11px; font-weight: 600; color: var(--text-muted); margin-left: 2px; }}
    .ia-kpi.is-urgent .ia-kpi-value {{ color: #dc2626; }}

    .ia-jobs-layout {{ display: grid; grid-template-columns: 278px minmax(0, 1fr); gap: 26px; align-items: start; }}
    .ia-results {{ min-width: 0; }}

    .ia-rail {{
      position: sticky;
      top: 76px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      max-height: calc(100vh - 96px);
      overflow-y: auto;
    }}
    .ia-rail-head {{ display: none; }}
    .ia-rail-section {{ display: flex; flex-direction: column; gap: 8px; }}
    .ia-rail-label {{ font-size: 11.5px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.01em; }}
    .ia-rail .search-input {{ padding: 9px 32px 9px 34px; font-size: 13px; }}
    .ia-rail .search-icon {{ left: 11px; }}
    .ia-rail .clear-search-btn {{ right: 8px; }}
    .ia-rail .segmented-control {{ flex-wrap: wrap; overflow: visible; gap: 4px; }}
    .ia-rail .segment-btn {{ padding: 6px 9px; font-size: 12px; border-radius: 8px; }}
    .ia-rail .segment-btn .count {{ font-size: 10px; padding: 1px 5px; }}
    .ia-rail .filter-pills-scroll {{ flex-wrap: wrap; overflow: visible; }}
    .ia-rail .filter-pill {{ padding: 5px 9px; font-size: 11.5px; }}
    .ia-rail .sort-select {{ width: 100%; }}
    .ia-rail .view-toggle {{ align-self: flex-start; }}
    .ia-rail-foot {{ display: none; }}

    .ia-mobile-controls {{ display: none; }}
    .ia-filter-btn {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 9px 12px;
      border-radius: 10px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      cursor: pointer;
      transition: transform 160ms cubic-bezier(0.2, 0.8, 0.2, 1), background-color 160ms;
    }}
    .ia-filter-btn:active {{ transform: scale(0.98); }}
    .ia-filter-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 9px;
      background: var(--accent-primary);
      color: #ffffff;
      font-size: 10.5px;
      font-weight: 700;
    }}
    .ia-filter-badge.is-zero {{ display: none; }}
    .ia-apply-btn {{
      width: 100%;
      padding: 12px;
      border: 0;
      border-radius: 11px;
      background: var(--accent-primary);
      color: #ffffff;
      font-family: inherit;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
    }}
    .ia-apply-btn:active {{ transform: scale(0.98); }}
    .ia-rail-backdrop {{ display: none; }}

    @media (min-width: 1024px) {{
      .container {{ max-width: 1300px; }}
    }}

    @media (max-width: 1023px) {{
      .ia-overview {{ flex-direction: column; align-items: stretch; gap: 12px; margin-bottom: 14px; }}
      .ia-overview .hero-desc {{ display: none; }}
      .ia-kpis {{ gap: 6px; overflow-x: auto; scrollbar-width: none; }}
      .ia-kpis::-webkit-scrollbar {{ display: none; }}
      .ia-kpi {{ flex: 1 1 0; min-width: 0; padding: 8px 10px; }}
      .ia-kpi-value {{ font-size: 16px; }}
      .ia-kpi-label {{ font-size: 10.5px; overflow: hidden; text-overflow: ellipsis; }}
      .ia-jobs-layout {{ grid-template-columns: minmax(0, 1fr); gap: 0; }}
      .ia-mobile-controls {{ display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }}
      .ia-mobile-controls .sort-select {{ flex: 1 1 auto; min-width: 0; }}
      .ia-rail {{
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        top: auto;
        z-index: 90;
        max-height: 86vh;
        overflow-y: auto;
        border-radius: 20px 20px 0 0;
        border-bottom: 0;
        padding: 8px 18px calc(22px + env(safe-area-inset-bottom));
        box-shadow: 0 -18px 40px -22px rgba(15, 23, 42, 0.4);
        transform: translateY(100%);
        visibility: hidden;
        transition: transform 240ms cubic-bezier(0.2, 0.8, 0.2, 1), visibility 0s linear 240ms;
      }}
      .ia-rail.is-open {{
        transform: translateY(0);
        visibility: visible;
        transition: transform 240ms cubic-bezier(0.2, 0.8, 0.2, 1), visibility 0s;
      }}
      .ia-rail-head {{ display: flex; align-items: center; justify-content: space-between; padding: 8px 0 4px; }}
      .ia-rail-head strong {{ font-size: 16px; font-weight: 700; letter-spacing: -0.03em; }}
      .ia-rail-close {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border: 1px solid var(--border-default);
        border-radius: 10px;
        background: var(--bg-page);
        color: var(--text-secondary);
        cursor: pointer;
      }}
      .ia-rail .segmented-control {{ flex-wrap: nowrap; overflow-x: auto; }}
      .ia-rail .segment-btn {{ flex: 0 0 auto; }}
      .ia-rail .filter-pills-scroll {{ flex-wrap: nowrap; overflow-x: auto; padding-bottom: 2px; }}
      .ia-rail .filter-pill {{ flex: 0 0 auto; }}
      .ia-rail .search-input {{ font-size: 14px; padding: 10px 36px 10px 36px; }}
      .ia-rail-foot {{ display: block; padding-top: 4px; }}
      .ia-rail-backdrop {{
        display: block;
        position: fixed;
        inset: 0;
        z-index: 89;
        background: rgba(15, 23, 42, 0.44);
        opacity: 0;
        transition: opacity 200ms cubic-bezier(0.2, 0.8, 0.2, 1);
      }}
      .ia-rail-backdrop.is-open {{ opacity: 1; }}
      .ia-rail-backdrop[hidden] {{ display: none; }}
      body.ia-filter-open {{ overflow: hidden; }}
      .feed-info {{ font-size: 12.5px; margin-bottom: 12px; }}
      /* 320px 폭에서 카드 상단 배지가 카드 밖으로 밀리지 않게 줄바꿈을 허용한다 */
      .card-top {{ flex-wrap: wrap; gap: 4px 8px; }}
      .company-name {{ min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
      .badges-row {{ flex-shrink: 1; flex-wrap: wrap; }}
      .ia-rail {{ overflow-x: hidden; }}
    }}

{_WATCH_CSS}
  </style>
</head>
<body>

  <!-- Global Nav -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand" style="display:flex;align-items:center;gap:12px;">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
        <div class="nav-tabs">
          <a href="index.html" class="nav-tab-item active">채용공고</a>
          <a href="study.html" class="nav-tab-item">시험 공부</a>
          <a href="ai.html" class="nav-tab-item">AI 트렌드</a>
          <a href="cve.html" class="nav-tab-item">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
          <a href="radar.html" class="nav-tab-item">피싱 레이더</a>
          <a href="pick.html" class="nav-tab-item">오늘 뭐 먹지</a>
          <a href="clue.html" class="nav-tab-item">3단서 추리</a>
          <a href="mission.html" class="nav-tab-item">퇴근길 미션</a>
          <a href="chart.html" class="nav-tab-item">차트 추리실</a>
        </div>
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

  <script>
    // 좁은 화면에서 현재 페이지 탭이 가려지지 않도록 탭 영역만 살짝 스크롤한다.
    (function () {{
      function keepActiveTabVisible() {{
        var box = document.querySelector('.nav-tabs');
        if (!box) return;
        var act = box.querySelector('.nav-tab-item.active');
        if (!act || box.scrollWidth <= box.clientWidth) return;
        var br = box.getBoundingClientRect();
        var ar = act.getBoundingClientRect();
        if (ar.right > br.right) box.scrollLeft += (ar.right - br.right) + 8;
        else if (ar.left < br.left) box.scrollLeft -= (br.left - ar.left) + 8;
      }}
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', keepActiveTabVisible);
      else keepActiveTabVisible();
      window.addEventListener('resize', keepActiveTabVisible);
    }})();
  </script>

  <!-- Main Content -->
  <main class="container">
    
    <!-- Summary / KPI -->
    <section class="ia-overview">
      <div class="ia-overview-copy">
        <h1 class="hero-title">정보보안 직무 & 포지션 아카이브</h1>
        <p class="hero-desc">원티드 · 점핏 · 사람인 · 리멤버 · 잡코리아 · 인크루트의 보안 포지션을 직무 검증을 거쳐 선별하고 중복 없이 아카이빙하는 정보공유 플랫폼입니다.</p>
        <a class="ia-quick-link" href="today.html">
          <span class="ia-quick-kicker">오늘 한 번에</span>
          <span class="ia-quick-text">마감 공고 · KEV · 복습 · 브리핑 · 날씨</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"></path></svg>
        </a>
      </div>
      <div class="ia-kpis">
        <div class="ia-kpi">
          <span class="ia-kpi-label">총 활성 공고</span>
          <strong class="ia-kpi-value" id="statActiveCount">{len(jobs)}</strong><span class="ia-kpi-unit">건</span>
        </div>
        <div class="ia-kpi is-urgent">
          <span class="ia-kpi-label">오늘 마감</span>
          <strong class="ia-kpi-value" id="statDueToday">{due_today}</strong><span class="ia-kpi-unit">건</span>
        </div>
        <div class="ia-kpi">
          <span class="ia-kpi-label">이번 주 마감</span>
          <strong class="ia-kpi-value" id="statDueWeek">{due_week}</strong><span class="ia-kpi-unit">건</span>
        </div>
        <div class="ia-kpi">
          <span class="ia-kpi-label">새 공고</span>
          <strong class="ia-kpi-value" id="statNewToday">{new_today}</strong><span class="ia-kpi-unit">건</span>
        </div>
      </div>
    </section>

    <div class="ia-jobs-layout">
      <!-- 필터: PC 좌측 고정 레일 / 모바일 바텀 시트 -->
      <aside class="ia-rail" id="filterRail" aria-label="공고 필터">
        <div class="ia-rail-head">
          <strong>필터</strong>
          <button type="button" class="ia-rail-close" id="filterCloseBtn" aria-label="필터 닫기">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg>
          </button>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">검색</p>
          <div class="search-box">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" id="searchInput" class="search-input" placeholder="회사명, 포지션명, 키워드 검색">
            <button id="clearSearch" class="clear-search-btn" aria-label="검색 지우기">✕</button>
          </div>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">키워드</p>
          <div class="segmented-control" id="keywordNav">
            <button class="segment-btn active" data-kw="all">전체 <span class="count">{len(jobs)}</span></button>
            <button class="segment-btn" data-kw="정보보안">정보보안 <span class="count">{kw_counts.get("정보보안", 0)}</span></button>
            <button class="segment-btn" data-kw="정보보호">정보보호 <span class="count">{kw_counts.get("정보보호", 0)}</span></button>
            <button class="segment-btn" data-kw="취약점 진단">취약점 진단 <span class="count">{kw_counts.get("취약점 진단", 0)}</span></button>
            <button class="segment-btn" data-kw="모의해킹">모의해킹 <span class="count">{kw_counts.get("모의해킹", 0)}</span></button>
          </div>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">플랫폼</p>
          <div class="filter-pills-scroll">
            <button class="filter-pill active" data-filter="platform" data-val="all">전체</button>
            <button class="filter-pill" data-filter="platform" data-val="원티드">원티드</button>
            <button class="filter-pill" data-filter="platform" data-val="점핏">점핏</button>
            <button class="filter-pill" data-filter="platform" data-val="사람인">사람인</button>
            <button class="filter-pill" data-filter="platform" data-val="리멤버">리멤버</button>
            <button class="filter-pill" data-filter="platform" data-val="잡코리아">잡코리아</button>
            <button class="filter-pill" data-filter="platform" data-val="인크루트">인크루트</button>
          </div>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">마감</p>
          <div class="filter-pills-scroll">
            <button class="filter-pill active" data-filter="deadline" data-val="all">전체</button>
            <button class="filter-pill" data-filter="deadline" data-val="urgent">마감 임박</button>
            <button class="filter-pill" data-filter="deadline" data-val="always">상시</button>
          </div>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">관심</p>
          <div class="filter-pills-scroll">
            <button class="filter-pill active" data-filter="watch" data-val="all">전체</button>
            <button class="filter-pill" data-filter="watch" data-val="watch">관심만<span class="filter-pill-count" id="watchFilterCount">0</span></button>
          </div>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">정렬</p>
          <select id="sortSelect" class="sort-select" aria-label="정렬">
            <option value="deadline" selected>마감 임박 순</option>
            <option value="default">등록 순</option>
            <option value="company">회사명 순</option>
          </select>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">저장 검색</p>
          <button type="button" class="save-search-btn" id="saveSearchBtn">현재 조건 저장</button>
          <div class="saved-chips" id="savedSearchList"></div>
        </div>

        <div class="ia-rail-section">
          <p class="ia-rail-label">보기</p>
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

        <div class="ia-rail-foot">
          <button type="button" class="ia-apply-btn" id="filterApplyBtn">결과 보기 <span id="filterApplyCount"></span></button>
        </div>
      </aside>

      <div class="ia-results">
        <div class="ia-mobile-controls">
          <select id="sortSelectMobile" class="sort-select" aria-label="정렬">
            <option value="deadline" selected>마감 임박 순</option>
            <option value="default">등록 순</option>
            <option value="company">회사명 순</option>
          </select>
          <button type="button" class="ia-filter-btn" id="filterOpenBtn" aria-expanded="false" aria-controls="filterRail">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M7 12h10M10 18h4"></path></svg>
            필터<span class="ia-filter-badge is-zero" id="filterBadge">0</span>
          </button>
        </div>

        <div class="feed-info">
          <div>현재 <strong id="matchCount">{len(jobs)}</strong>개의 포지션 표시 중</div>
          <div id="filterSummary"></div>
        </div>

        <section class="watch-archive" id="watchArchive" aria-label="보관된 관심 공고" hidden>
          <div class="watch-archive-head">
            <strong class="watch-archive-title">보관된 관심 공고</strong>
            <span class="watch-archive-count" id="watchArchiveCount">0건</span>
            <p class="watch-archive-desc">현재 목록에서 마감·제외된 공고입니다. 상태와 메모는 그대로 남아 있습니다.</p>
          </div>
          <div id="watchArchiveList"></div>
        </section>

        <div id="jobsContainer"></div>
      </div>
    </div>
    <div class="ia-rail-backdrop" id="filterBackdrop" hidden></div>

    <!-- Footer -->
    <footer>
      <p>Infosec Archive · 정보보안 포지션 & 커리어 정보공유 아카이브</p>
      <p>데이터는 매일 아침 08:00 KST 기준 자동 갱신됩니다.</p>
    </footer>
  </main>

  <script>
    const JOBS = {jobs_json_str};

    let selectedKeyword = 'all';
    let selectedPlatform = 'all';
    let selectedDeadline = 'all';
    let selectedWatch = 'all';
    let sortBy = 'deadline';
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

    // ---- 실시간 마감 판정 ----
    // 매일 08:00 정적 빌드 이후에도, 페이지를 연 '현재 KST 날짜·시각' 기준으로
    // 마감 시각이 지난 공고(예: 14시마감, ~11/17 18:00, 지난 날짜)를 목록에서 자동 제외한다.
    function getKstNow() {{
      const d = new Date();
      return new Date(d.getTime() + (d.getTimezoneOffset() * 60000) + (9 * 60 * 60 * 1000));
    }}

    function startOfDay(d) {{
      return new Date(d.getFullYear(), d.getMonth(), d.getDate());
    }}

    function dayDiff(from, to) {{
      return Math.round((startOfDay(to) - startOfDay(from)) / 86400000);
    }}

    function parseSeenDateC(seen) {{
      if (!seen) return null;
      const m = String(seen).match(/(\\d{{4}})-(\\d{{2}})-(\\d{{2}})/);
      if (!m) return null;
      return new Date(parseInt(m[1], 10), parseInt(m[2], 10) - 1, parseInt(m[3], 10));
    }}

    // 표기에 함께 적힌 날짜(MM/DD)를 Date로. 없거나 달력에 없으면 null.
    function parseExplicitDateC(dl, now) {{
      const m = dl.match(/(\\d{{1,2}})\\s*\\/\\s*(\\d{{1,2}})/);
      if (!m) return null;
      const month = parseInt(m[1], 10), day = parseInt(m[2], 10);
      if (month < 1 || month > 12 || day < 1 || day > 31) return null;
      let target = new Date(now.getFullYear(), month - 1, day);
      if (target.getMonth() !== month - 1 || target.getDate() !== day) return null;
      const gap = dayDiff(now, target);
      if (gap > 180) target = new Date(now.getFullYear() - 1, month - 1, day);
      else if (gap < -180) target = new Date(now.getFullYear() + 1, month - 1, day);
      return target;
    }}

    // 표기에 적힌 마감 시각(시, 분). 없으면 null.
    function parseDeadlineClockC(dl) {{
      let s = dl.replace(/\\d{{1,2}}\\s*\\/\\s*\\d{{1,2}}/g, ' ');
      s = s.replace(/\\d{{4}}\\s*[.\\-년]\\s*\\d{{1,2}}\\s*[.\\-월]\\s*\\d{{1,2}}\\s*일?/g, ' ');
      let m = s.match(/(\\d{{1,2}})\\s*시(?:\\s*(\\d{{1,2}})\\s*분)?/);
      if (m) return [parseInt(m[1], 10), m[2] ? parseInt(m[2], 10) : 0];
      m = s.match(/(\\d{{1,2}})\\s*:\\s*(\\d{{2}})/);
      if (m) return [parseInt(m[1], 10), parseInt(m[2], 10)];
      return null;
    }}

    function getDeadlineMeta(rawDl, lastSeen, labelText) {{
      const dl = cleanDeadline(rawDl);
      const now = getKstNow();
      const clock = parseDeadlineClockC(dl);
      const isTimeOnly = /^\\d\\d?(:\\d\\d)?\\s*시?\\s*마감$/.test(dl);
      const clockPassed = clock ? ((now.getHours() * 60 + now.getMinutes()) >= (clock[0] >= 24 ? 24 * 60 : clock[0] * 60 + clock[1])) : false;
      const seen = parseSeenDateC(lastSeen);
      const explicit = parseExplicitDateC(dl, now);

      let badgeClass = 'badge-dl-normal';
      let isUrgent = false;
      let isAlways = false;
      let daysLeft = 999;
      let expired = false;
      let hasDeadline = true;

      // 부분 문자열 매칭('D-1' in 'D-16')을 피해 D-(숫자)를 정규식으로 파싱한다.
      const dm = dl.match(/D-(\\d+)/);

      if (explicit) {{
        daysLeft = dayDiff(now, explicit);
        if (daysLeft < 0) expired = true;
        else if (daysLeft === 0 && clockPassed) expired = true;
      }} else if (dm) {{
        daysLeft = parseInt(dm[1], 10) - (seen ? dayDiff(seen, now) : 0);
        if (daysLeft < 0) expired = true;
        else if (daysLeft === 0 && clockPassed) expired = true;
      }} else if (dl.includes('D-Day') || dl.includes('오늘')) {{
        daysLeft = 0;
        if (seen && dayDiff(seen, now) > 0) expired = true;
        else if (clockPassed) expired = true;
      }} else if (dl.includes('내일')) {{
        daysLeft = seen ? (1 - dayDiff(seen, now)) : 1;
        if (daysLeft < 0) expired = true;
        else if (daysLeft === 0 && clockPassed) expired = true;
      }} else if (isTimeOnly) {{
        daysLeft = 0;
        if (seen && dayDiff(seen, now) > 0) expired = true;
        else if (clockPassed) expired = true;
      }} else if (dl.includes('상시') || dl.includes('채용시')) {{
        badgeClass = 'badge-dl-always';
        isAlways = true;
        daysLeft = 500;
        hasDeadline = false;
      }} else {{
        hasDeadline = false;
      }}

      if (hasDeadline && daysLeft <= 3 && daysLeft >= 0) {{
        badgeClass = 'badge-dl-urgent';
        isUrgent = true;
      }} else if (hasDeadline && daysLeft <= 7 && daysLeft >= 0) {{
        badgeClass = 'badge-dl-warning';
        isUrgent = true;
      }}

      // 표시 라벨은 빌드 시점에 오늘 기준으로 보정한 deadline_label을 우선한다.
      return {{ label: labelText || dl, badgeClass, isUrgent: isUrgent && !expired, isAlways, daysLeft, expired }};
    }}

    // 현재 시각 기준 살아 있는 공고 (마감된 공고 제외)
    function getLiveJobs() {{
      return JOBS.filter(job => !getDeadlineMeta(job.deadline, job.last_seen_at, job.deadline_label).expired);
    }}

    // 상단 통계·키워드 탭 카운트를 실시간 마감 반영값으로 갱신
    function updateLiveCounts(liveJobs) {{
      const live = liveJobs || getLiveJobs();
      const activeEl = document.getElementById('statActiveCount');
      // 단위('건')는 KPI 카드의 .ia-kpi-unit 스팬이 그리므로 숫자만 넣는다(건건 중복 방지).
      if (activeEl) activeEl.textContent = String(live.length);
      const dueTodayEl = document.getElementById('statDueToday');
      const dueWeekEl = document.getElementById('statDueWeek');
      if (dueTodayEl || dueWeekEl) {{
        let dueToday = 0;
        let dueWeek = 0;
        live.forEach(job => {{
          const meta = getDeadlineMeta(job.deadline, job.last_seen_at, job.deadline_label);
          if (meta.expired || meta.daysLeft === null || meta.daysLeft === undefined || meta.daysLeft < 0) return;
          if (meta.daysLeft === 0) dueToday += 1;
          if (meta.daysLeft <= 7) dueWeek += 1;
        }});
        if (dueTodayEl) dueTodayEl.textContent = dueToday;
        if (dueWeekEl) dueWeekEl.textContent = dueWeek;
      }}
      const kwCounts = {{}};
      live.forEach(job => (job.keywords || []).forEach(k => {{ kwCounts[k] = (kwCounts[k] || 0) + 1; }}));
      document.querySelectorAll('#keywordNav .segment-btn').forEach(btn => {{
        const kw = btn.getAttribute('data-kw');
        const countEl = btn.querySelector('.count');
        if (countEl) countEl.textContent = kw === 'all' ? live.length : (kwCounts[kw] || 0);
      }});
    }}

    function escapeHtml(str) {{
      return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    // 수집된 링크는 URL 파서로 검증해 http/https/mailto 만 통과시킨다
    // (javascript:, data:, vbscript:, 프로토콜 상대 //, 제어문자 삽입 차단).
    function safeUrl(u) {{
      const raw = String(u == null ? '' : u).trim();
      if (!raw || /[\\u0000-\\u001F\\u007F<>"'`\\\\]/.test(raw)) return '#';
      let parsed;
      try {{ parsed = new URL(raw); }} catch (e) {{ return '#'; }}
      const proto = parsed.protocol.toLowerCase();
      return (proto === 'http:' || proto === 'https:' || proto === 'mailto:') ? parsed.href : '#';
    }}

    // 외부 링크 카드 옆에 실제 이동 도메인을 표시해 피싱 링크를 눈으로 걸러낸다.
    function linkHost(u) {{
      let parsed;
      try {{ parsed = new URL(String(u == null ? '' : u).trim()); }} catch (e) {{ return ''; }}
      const proto = parsed.protocol.toLowerCase();
      if (proto === 'mailto:') {{
        const parts = String(parsed.pathname || '').split('@');
        return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
      }}
      if (proto !== 'http:' && proto !== 'https:') return '';
      return parsed.hostname.replace(/^www\\./, '').toLowerCase();
    }}

    function renderFeed() {{
      // 0. 상단 통계·탭 카운트를 현재 시각 기준 실시간 마감 반영값으로 먼저 갱신
      updateLiveCounts();
      updateFilterBadge();

      // 1. Filter
      let filtered = JOBS.filter(job => {{
        if (selectedKeyword !== 'all' && (!job.keywords || !job.keywords.includes(selectedKeyword))) {{
          return false;
        }}
        if (selectedPlatform !== 'all' && (!job.platforms || !job.platforms.includes(selectedPlatform))) {{
          return false;
        }}
        const dlMeta = getDeadlineMeta(job.deadline, job.last_seen_at, job.deadline_label);
        if (dlMeta.expired) return false;   // 현재 KST 시각 기준 이미 마감된 공고는 숨김
        if (selectedDeadline === 'urgent' && !dlMeta.isUrgent) return false;
        if (selectedDeadline === 'always' && !dlMeta.isAlways) return false;
        if (selectedWatch === 'watch' && !watchlist[job.job_key]) return false;

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
          const da = getDeadlineMeta(a.deadline, a.last_seen_at, a.deadline_label).daysLeft;
          const db = getDeadlineMeta(b.deadline, b.last_seen_at, b.deadline_label).daysLeft;
          return da - db;
        }});
      }} else if (sortBy === 'company') {{
        filtered.sort((a, b) => (a.company || '').localeCompare(b.company || '', 'ko'));
      }}

      matchCount.textContent = filtered.length;
      updateFilterBadge();

      // 3. Render
      if (filtered.length === 0) {{
        jobsContainer.innerHTML = `
          <div class="empty-state">
            <div class="empty-title">일치하는 채용공고가 없습니다</div>
            <div class="empty-desc">검색어를 변경하거나 적용된 필터를 초기화해 보세요.</div>
            <button class="reset-btn" data-action="reset-filters">필터 초기화</button>
          </div>
        `;
        return;
      }}

      if (currentView === 'grid') {{
        let html = '<div class="jobs-grid">';
        filtered.forEach(job => {{
          const dlMeta = getDeadlineMeta(job.deadline, job.last_seen_at, job.deadline_label);
          const dlBadge = `<span class="badge-dl ${{dlMeta.badgeClass}}">${{escapeHtml(dlMeta.label)}}</span>`;
          const platformBadges = (job.platforms || []).map(p => 
            `<span class="badge-platform badge-platform-${{escapeHtml(p)}}">${{escapeHtml(p)}}</span>`
          ).join('');
          const tags = (job.keywords || []).map(k => 
            `<span class="keyword-tag">#${{escapeHtml(k)}}</span>`
          ).join('');
          const aiTags = (job.tags || []).filter(t => !(job.keywords || []).includes(t.replace('#', ''))).map(t =>
            `<span class="keyword-tag ai-tag">${{escapeHtml(t)}}</span>`
          ).join('');
          const summaryHtml = job.summary ? `<div class="job-summary">${{escapeHtml(job.summary)}}</div>` : '';

          html += `
            <article class="job-card${{watchlist[job.job_key] ? ' is-watched' : ''}}" data-key="${{escapeHtml(job.job_key)}}" data-watch-for="${{escapeHtml(job.job_key)}}">
              <a class="job-card-link" href="${{safeUrl(job.url)}}" target="_blank" rel="noopener noreferrer">
              <div>
                <div class="card-top">
                  <span class="company-name" title="${{escapeHtml(job.company)}}">${{escapeHtml(job.company)}}</span>
                  <div class="badges-row">
                    ${{dlBadge}}
                    ${{platformBadges}}
                  </div>
                </div>
                <div class="job-title">${{escapeHtml(job.title)}}</div>
                ${{summaryHtml}}
              </div>
              <div class="card-footer">
                <div class="tags-list">${{tags}}${{aiTags}}</div>
                <div class="outlink-indicator" title="원문 열기: ${{escapeHtml(job.url)}}">
                  <span class="outlink-host">${{escapeHtml(linkHost(job.url))}}</span>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="7" y1="17" x2="17" y2="7"></line>
                    <polyline points="7 7 17 7 17 17"></polyline>
                  </svg>
                </div>
              </div>
              </a>
              <div class="job-watch" data-watch-slot></div>
            </article>
          `;
        }});
        html += '</div>';
        jobsContainer.innerHTML = html;
        hydrateWatchSlots(jobsContainer);
      }} else {{
        let html = '<div class="jobs-list-compact">';
        filtered.forEach(job => {{
          const dlMeta = getDeadlineMeta(job.deadline, job.last_seen_at, job.deadline_label);
          const dlBadge = `<span class="badge-dl ${{dlMeta.badgeClass}}">${{escapeHtml(dlMeta.label)}}</span>`;
          const platformBadges = (job.platforms || []).map(p => 
            `<span class="badge-platform badge-platform-${{escapeHtml(p)}}">${{escapeHtml(p)}}</span>`
          ).join('');

          const listSummaryHtml = job.summary ? `<div class="list-summary" title="${{escapeHtml(job.summary)}}">${{escapeHtml(job.summary)}}</div>` : '';

          html += `
            <div class="list-item" data-key="${{escapeHtml(job.job_key)}}" data-watch-for="${{escapeHtml(job.job_key)}}">
            <a class="list-row" href="${{safeUrl(job.url)}}" target="_blank" rel="noopener noreferrer">
              <div class="list-company" title="${{escapeHtml(job.company)}}">${{escapeHtml(job.company)}}</div>
              <div class="list-title">
                <div>${{escapeHtml(job.title)}}</div>
                ${{listSummaryHtml}}
              </div>
              <div class="list-deadline">${{dlBadge}}</div>
              <div class="list-platforms">${{platformBadges}}</div>
              <div class="list-outlink" title="원문 열기: ${{escapeHtml(job.url)}}">
                <span class="outlink-host">${{escapeHtml(linkHost(job.url))}}</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="7" y1="17" x2="17" y2="7"></line>
                  <polyline points="7 7 17 7 17 17"></polyline>
                </svg>
              </div>
            </a>
            <div class="job-watch is-list" data-watch-slot></div>
            </div>
          `;
        }});
        html += '</div>';
        jobsContainer.innerHTML = html;
        hydrateWatchSlots(jobsContainer);
      }}
      renderWatchArchive();
      updateWatchCounts();
    }}

    function resetFilters() {{
      selectedKeyword = 'all';
      selectedPlatform = 'all';
      selectedDeadline = 'all';
      selectedWatch = 'all';
      searchTerm = '';
      searchInput.value = '';
      clearSearchBtn.style.display = 'none';

      document.querySelectorAll('#keywordNav .segment-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-kw') === 'all'));
      document.querySelectorAll('.filter-pill[data-filter="platform"]').forEach(b => b.classList.toggle('active', b.getAttribute('data-val') === 'all'));
      document.querySelectorAll('.filter-pill[data-filter="deadline"]').forEach(b => b.classList.toggle('active', b.getAttribute('data-val') === 'all'));
      document.querySelectorAll('.filter-pill[data-filter="watch"]').forEach(b => b.classList.toggle('active', b.getAttribute('data-val') === 'all'));

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
        if (filterType === 'watch') selectedWatch = val;
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

    // Initialize (관심 목록·저장 검색 초기화 뒤에 첫 렌더가 실행된다)
    initTheme();

    // 결과 없음 화면의 '필터 초기화' 버튼은 매번 새로 그려지므로 문서 레벨 위임으로 받는다.
    // (CSP script-src 에서 'unsafe-inline' 을 쓰지 않아 인라인 onclick 을 사용할 수 없다)
    document.addEventListener('click', function (e) {{
      const el = (e.target && e.target.closest) ? e.target.closest('[data-action="reset-filters"]') : null;
      if (el) resetFilters();
    }});

    // 페이지를 오래 열어둔 경우에도 마감 시각이 지나면 목록에서 자동으로 ㅐ진다.
    let liveSignature = '';
    setInterval(() => {{
      const live = getLiveJobs();
      const signature = live.length + '|' + JOBS.length;
      if (signature !== liveSignature) {{
        liveSignature = signature;
        renderFeed();
      }}
    }}, 60000);

    // ---- 모바일 필터 시트 · 필터 배지 ----
    const filterRail = document.getElementById('filterRail');
    const filterBackdrop = document.getElementById('filterBackdrop');
    const filterOpenBtn = document.getElementById('filterOpenBtn');
    const filterCloseBtn = document.getElementById('filterCloseBtn');
    const filterApplyBtn = document.getElementById('filterApplyBtn');
    const sortSelectMobile = document.getElementById('sortSelectMobile');

    function activeFilterCount() {{
      let n = 0;
      if (selectedPlatform !== 'all') n += 1;
      if (selectedDeadline !== 'all') n += 1;
      if (selectedKeyword !== 'all') n += 1;
      if (selectedWatch === 'watch') n += 1;
      if (searchTerm) n += 1;
      return n;
    }}

    function updateFilterBadge() {{
      const badge = document.getElementById('filterBadge');
      if (badge) {{
        const n = activeFilterCount();
        badge.textContent = n;
        badge.classList.toggle('is-zero', n === 0);
      }}
      const applyCount = document.getElementById('filterApplyCount');
      if (applyCount) {{
        const el = document.getElementById('matchCount');
        applyCount.textContent = el ? '(' + el.textContent + ')' : '';
      }}
    }}

    function openFilterSheet() {{
      if (!filterRail || !filterBackdrop) return;
      filterBackdrop.hidden = false;
      document.body.classList.add('ia-filter-open');
      if (filterOpenBtn) filterOpenBtn.setAttribute('aria-expanded', 'true');
      window.requestAnimationFrame(function () {{
        window.requestAnimationFrame(function () {{
          filterRail.classList.add('is-open');
          filterBackdrop.classList.add('is-open');
          if (filterCloseBtn) filterCloseBtn.focus();
        }});
      }});
    }}

    function closeFilterSheet() {{
      if (!filterRail || !filterBackdrop) return;
      filterRail.classList.remove('is-open');
      filterBackdrop.classList.remove('is-open');
      document.body.classList.remove('ia-filter-open');
      if (filterOpenBtn) {{
        filterOpenBtn.setAttribute('aria-expanded', 'false');
        filterOpenBtn.focus();
      }}
      window.setTimeout(function () {{ filterBackdrop.hidden = true; }}, 220);
    }}

    if (filterOpenBtn) {{
      filterOpenBtn.addEventListener('click', function () {{
        if (filterRail && filterRail.classList.contains('is-open')) closeFilterSheet();
        else openFilterSheet();
      }});
    }}
    if (filterCloseBtn) filterCloseBtn.addEventListener('click', closeFilterSheet);
    if (filterApplyBtn) filterApplyBtn.addEventListener('click', closeFilterSheet);
    if (filterBackdrop) filterBackdrop.addEventListener('click', closeFilterSheet);

    if (sortSelectMobile) {{
      sortSelectMobile.addEventListener('change', function (event) {{
        sortSelect.value = event.target.value;
        sortBy = event.target.value;
        renderFeed();
      }});
      sortSelect.addEventListener('change', function (event) {{
        sortSelectMobile.value = event.target.value;
      }});
    }}

    window.addEventListener('keydown', function (event) {{
      if (event.key === 'Escape' && filterRail && filterRail.classList.contains('is-open')) {{
        closeFilterSheet();
      }}
    }});

{_WATCH_JS}
  </script>
</body>
</html>
"""
    import ui_shell

    return harden_html(ui_shell.apply(html_content, 'index'))

def generate_readme(jobs, update_time_str):
    """GitHub 저장소 메인에 노출될 마크다운"""
    keyword_jobs = {kw: [] for kw in KEYWORDS}
    for job in jobs:
        for kw in job.get("keywords", []):
            if kw in keyword_jobs:
                keyword_jobs[kw].append(job)

    urgent_count = count_urgent_jobs(jobs)

    lines = [
        "# 🛡️ Infosec Archive · 정보보안 포지션 아카이브",
        "",
        f"> **🌐 공식 아카이브 웹사이트**: [https://bling9513-ship-it.github.io/project-1/](https://bling9513-ship-it.github.io/project-1/)",
        f"> **마지막 업데이트**: `{update_time_str}` (매일 08:00 KST 자동 수집)",
        f"> **아카이빙된 보안 공고**: 총 **{len(jobs)}**개 (직무 검증 및 중복 제거 완료)",
        f"> **마감 임박 공고**: 총 **{urgent_count}**개 (D-Day 및 마감 기한 순 정렬)",
        "> **오늘 한 번에**: [today.html](https://bling9513-ship-it.github.io/project-1/today.html) (오늘 마감 · KEV · 복습 · AI 브리핑 · 날씨 · 게임)",
        "> **AI 기술·트렌드 브리핑**: [ai.html](https://bling9513-ship-it.github.io/project-1/ai.html) (Hugging Face · arXiv · Hacker News · GeekNews 수집·분석)",
        "> **CVE 취약점 리포트**: [cve.html](https://bling9513-ship-it.github.io/project-1/cve.html) (CISA KEV · NVD · EPSS · 공개 PoC · 한국어 조치 방안)",
        "> **시험 공부 허브**: [study.html](https://bling9513-ship-it.github.io/project-1/study.html) (CPPG · 정보보안기사 · ISMS-P)",
        "",
        "원티드, 점핏, 사람인, 리멤버, 잡코리아, 인크루트의 정보보안 포지션을 정밀 직무 필터링을 거쳐 선별하고 공유하는 정보 아카이브 레포지토리입니다.",
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
            dl = job_deadline_label(job)
            title_escaped = job["title"].replace("|", "\\|")
            company_escaped = job["company"].replace("|", "\\|")
            lines.append(f"| **{company_escaped}** | [{title_escaped}]({job['url']}) | {platforms_str} | **{dl}** | {keywords_str} |")
        
        lines.append("")
        lines.append("[맨 위로 이동](#️-infosec-archive--정보보안-포지션-아카이브)")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def sync_jobs_to_db(jobs, now_dt=None, db_path=None):
    """수집한 공고를 archive.db 에 반영하고 더 이상 보이지 않는 공고를 마감 처리한다.

    · 기존 행 연결은 platform+external_id 가 최우선이고, 짧은 제목 키는 후보가
      정확히 1건이고 외부 ID가 충돌하지 않을 때만 쓴다(crawler.main 과 같은 코드경로).
    · 테스트에서 archive.db 사본으로 같은 재수집을 돌려볼 수 있게 분리했다.
    """
    from db_manager import (get_connection, init_db, parse_deadline_status, make_job_key,
                            migrate_job_keys, mark_expired_jobs, build_job_identity_index,
                            resolve_existing_job_key, expire_platform_conflict_duplicates,
                            deduplicate_active_jobs, job_dedup_key, DB_PATH)
    db_path = db_path or DB_PATH
    kst = timezone(timedelta(hours=9))
    now_dt = now_dt or datetime.now(kst)
    now_kst = now_dt.strftime("%Y-%m-%d %H:%M:%S KST")
    today_date = now_dt.date()

    init_db(db_path)
    migrated = migrate_job_keys(db_path)
    if migrated:
        print(f"-> 기존 공고 키를 플랫폼 ID 기반 키로 정리: {migrated}건")
    conn = get_connection(db_path)
    cur = conn.cursor()

    # 1. 수집된 공고 DB UPSERT
    #   이미 저장된 공고는 platform+external_id를 최우선으로 찾아 그 행의 job_key를 이어받는다.
    #   짧은 제목 키는 '후보가 정확히 1건이고 외부 ID가 충돌하지 않을 때'만 쓰므로,
    #   제목 12자만 같은 다른 공고(플랫폼 ID가 다른 2건)가 1행으로 합쳐지거나 사라지지 않는다.
    cur.execute("SELECT id, job_key, company, title, url, platforms FROM jobs WHERE status = 'ACTIVE';")
    existing_rows = cur.fetchall()
    identity_index, title_index = build_job_identity_index(existing_rows)
    # 같은 공고를 플랫폼만 바꿔 다시 수집했을 때 기존 행의 플랫폼 배지를 잃지 않도록 보관
    platforms_by_key = {r["job_key"]: r["platforms"] for r in existing_rows}
    # 이번 수집에서 본 공고의 (회사·제목) 중복 판정 키 — 플랫폼이 새 공고 ID로 다시 올려도
    # 같은 공고가 '목록에서 사라졌다'고 잘못 마감 처리하지 않기 위해 쓴다.
    seen_dedup_keys = {job_dedup_key(j.get("company", ""), j.get("title", "")) for j in jobs}

    seen_keys = set()
    for job in jobs:
        platform = (job.get("platforms") or [""])[0]
        key = resolve_existing_job_key(
            job["company"], job["title"], platform, job.get("external_id", ""), job["url"],
            identity_index, title_index,
        )
        own_key = job.get("job_key") or make_job_key(
            job["company"], job["title"], job["url"],
            platforms=job.get("platforms", []), platform=platform,
            external_id=job.get("external_id", ""),
        )
        # 같은 실행에서 두 공고가 한 행으로 몰리면 먼저 쓴 공고가 덮이므로, 중복 키는 피한다.
        if not key or key in seen_keys:
            key = own_key
        job["job_key"] = key
        seen_keys.add(key)
        # 기존 행에 이어붙이는 경우 플랫폼 배지는 합집합으로 유지한다.
        previous_platforms = platforms_by_key.get(key)
        if previous_platforms:
            try:
                previous_platforms = json.loads(previous_platforms) if isinstance(previous_platforms, str) else previous_platforms
            except (TypeError, ValueError):
                previous_platforms = []
            merged_platforms = list(job.get("platforms", []) or [])
            for platform_name in previous_platforms or []:
                if platform_name not in merged_platforms:
                    merged_platforms.append(platform_name)
            job["platforms"] = merged_platforms
        raw_deadline = job.get("deadline", "상시채용")
        dl_status, status = parse_deadline_status(raw_deadline, today_date, now_kst, now_dt=now_dt)

        cur.execute("""
        INSERT INTO jobs (
            job_key, company, title, url, platforms, keywords,
            location, deadline, deadline_status, status,
            summary, tags, first_seen_at, last_seen_at,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_key) DO UPDATE SET
            platforms = excluded.platforms,
            keywords = excluded.keywords,
            location = CASE WHEN excluded.location != '' THEN excluded.location ELSE jobs.location END,
            deadline = excluded.deadline,
            deadline_status = excluded.deadline_status,
            status = excluded.status,
            summary = CASE WHEN excluded.summary != '' THEN excluded.summary ELSE jobs.summary END,
            tags = CASE WHEN excluded.tags != '[]' THEN excluded.tags ELSE jobs.tags END,
            last_seen_at = excluded.last_seen_at,
            updated_at = excluded.updated_at;
        """, (
            key, job["company"], job["title"], job["url"],
            json.dumps(job.get("platforms", []), ensure_ascii=False),
            json.dumps(job.get("keywords", []), ensure_ascii=False),
            job.get("location", ""), raw_deadline, dl_status, status,
            job.get("summary", ""), json.dumps(job.get("tags", []), ensure_ascii=False),
            now_kst, now_kst, now_kst, now_kst
        ))

    # 2. 마감일 지난 공고 및 플랫폼에서 삭제된 공고 EXPIRED 처리
    conn.commit()
    mark_expired_jobs(today_date, db_path=db_path, now_dt=now_dt)
    cur.execute("SELECT id, job_key, company, title, deadline FROM jobs WHERE status = 'ACTIVE';")
    active_rows = cur.fetchall()
    for r in active_rows:
        if r["job_key"] not in seen_keys:
            # 플랫폼이 새 공고 ID로 같은 공고를 다시 올린 경우: 이번 수집에서 같은 (회사·제목)을
            # 보았다면 아직 살아 있는 공고이므로 마감 처리하지 않는다(중복 병합이 대표 행으로 합친다).
            if job_dedup_key(r["company"], r["title"]) in seen_dedup_keys:
                continue
            dl_st, st = parse_deadline_status(r["deadline"], today_date, now_dt=now_dt)
            if st == "EXPIRED" or "D-" not in r["deadline"]:
                cur.execute("UPDATE jobs SET status = 'EXPIRED', deadline_status = 'EXPIRED', updated_at = ? WHERE id = ?;", (now_kst, r["id"]))

    conn.commit()

    # 2-b. 플랫폼별 마감 표기 불일치로 생긴 복제 행 정리 (예: 사람인 14시마감 ↔ 잡코리아 D-Day 오늘 마감)
    conflict_expired = expire_platform_conflict_duplicates(today_date, db_path=db_path, now_dt=now_dt)
    if conflict_expired:
        print(f"-> 플랫폼 마감 표기 불일치 복제 행 {conflict_expired}건 정리")
    conn.commit()
    conn.close()

    # 2-c. 같은 공고 중복 행 병합 — 회사 표기 차이((주)·㈜·괄호 별칭)·제목 앞머리 태그 차이와
    #      플랫폼 재등록(새 공고 ID)으로 쌓인 중복을 대표 1건으로 합치고 나머지는 EXPIRED 로 보관한다.
    dedup = deduplicate_active_jobs(db_path=db_path, today_date=today_date, now_dt=now_dt)
    if dedup["merged"]:
        print(f"-> 같은 공고 중복 병합: {dedup['merged']}건을 {dedup['groups']}개 대표 공고로 정리")
    return sorted(seen_keys)


def main():
    jobs = collect_all_jobs()
    
    # EXAONE AI 기반 직무 요약 및 정밀 태깅 배치 연동
    try:
        from ai_enricher import enrich_jobs_batch
        print("\n[AI 배치] 엑사원(EXAONE) API 연동 직무 요약 및 정밀 태깅 진행 중...")
        jobs = enrich_jobs_batch(jobs, max_calls=2, batch_size=4)
    except Exception as e:
        print(f"[AI 배치 경고] 엑사원 연동 중 오류 발생 (기본 크롤링 데이터로 계속 진행): {e}")
    
    kst = timezone(timedelta(hours=9))
    now_dt = datetime.now(kst)
    now_kst = now_dt.strftime("%Y-%m-%d %H:%M:%S KST")
    today_date = now_dt.date()

    # SQLite DB (archive.db) 저장 및 마감 정리 연동
    from db_manager import get_active_jobs, get_db_stats
    sync_jobs_to_db(jobs, now_dt=now_dt)
    
    
    # 3. DB에서 활성 공고 조회 (Single Source of Truth)
    active_jobs = get_active_jobs()
    stats = get_db_stats()
    print(f"\n[SQLite DB] 활성 공고: {stats['active_jobs']}건 | 마감 정리된 공고: {stats['expired_jobs']}건")
    
    # 4. JSON 파일 저장 (활성 공고 기준)
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(active_jobs, f, ensure_ascii=False, indent=2)
    print(f"-> 'jobs.json' 저장 완료 ({len(active_jobs)}건)")
    
    # 5. index.html 생성
    html_data = generate_html(active_jobs, now_kst)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_data)
    print("-> 'index.html' 생성 완료")
    
    # 6. README.md 생성
    readme_data = generate_readme(active_jobs, now_kst)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_data)
    print("-> 'README.md' 생성 완료")
    
    print("\n모든 산출물이 성공적으로 생성되었습니다!")

    # 7. (선택) AI 기술·트렌드 수집·분석 연동
    #    기본 채용공고 갱신에는 영향이 없고, `python3 crawler.py --with-ai` 또는 WITH_AI=1 일 때만 실행한다.
    #    (일일 자동화에서는 ai_news_crawler.py 를 별도로 호출해도 된다.)
    if os.environ.get("WITH_AI") == "1" or "--with-ai" in sys.argv:
        try:
            import ai_news_crawler
            from build_ai_html import build as build_ai
            print("\n[AI] 기술·트렌드 수집·분석 시작")
            ai_news_crawler.run()
            build_ai()
        except Exception as e:  # noqa: BLE001
            print(f"[AI] 수집·분석을 건너뜁니다: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()

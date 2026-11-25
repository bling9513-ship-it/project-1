#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""활성 공고 근무지(location) 백필.

크롤러가 사람인·인크루트·리멤버·점핏의 근무지를 읽지 못하던 시절에 쌓인 공고는
`jobs.location` 이 비어 있다. 이 스크립트는 각 공고의 원문 상세 페이지를 병렬로 조회해
근무지를 채우고, 이미 채워진 값도 `normalize_location()` 표기로 다시 정리한다.

  · 점핏     api.jumpit.co.kr/api/position/{id}          → location
  · 리멤버   career-api.rememberapp.co.kr/job_postings/{id} → normalized_address
  · 사람인   m.saramin.co.kr/job-search/view?rec_idx={id}  → '지역' 항목
  · 인크루트 job.incruit.com/jobdb_info/jobpost.asp?job={id} → '근무지역' 항목
  · 잡코리아 m.jobkorea.co.kr/Recruit/GI_Read/{id}         → JSON-LD streetAddress

실행: python3 backfill_locations.py            # 실제 반영
      python3 backfill_locations.py --dry-run  # 조회 결과만 확인
"""
import argparse
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crawler import (  # noqa: E402
    INCRUIT_HEADERS,
    JOBKOREA_HEADERS,
    JUMPIT_HEADERS,
    REMEMBER_HEADERS,
    SARAMIN_HEADERS,
    normalize_location,
)
from net_guard import read_limited  # noqa: E402

DB_PATH = os.path.join(BASE_DIR, "archive.db")
KST = timezone(timedelta(hours=9))
PLATFORM_BY_PREFIX = {
    "wanted": "원티드",
    "jumpit": "점핏",
    "saramin": "사람인",
    "remember": "리멤버",
    "jobkorea": "잡코리아",
    "incruit": "인크루트",
}


def _read(url, headers, enc="utf-8", timeout=20):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return read_limited(res).decode(enc, errors="ignore")


def _read_retry(url, headers, enc="utf-8"):
    for attempt in range(2):
        try:
            return _read(url, headers, enc)
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == 1:
                raise
    return ""


def location_jumpit(external_id, _url):
    payload = _read_retry(f"https://api.jumpit.co.kr/api/position/{external_id}", JUMPIT_HEADERS)
    import json
    detail = json.loads(payload).get("result") or {}
    return normalize_location(detail.get("location") or "")


def location_remember(external_id, _url):
    import json
    payload = _read_retry(f"https://career-api.rememberapp.co.kr/job_postings/{external_id}", REMEMBER_HEADERS)
    data = json.loads(payload).get("data") or {}
    na = data.get("normalized_address") if isinstance(data.get("normalized_address"), dict) else {}
    loc = normalize_location(" ".join([str(na.get("level1") or ""), str(na.get("level2") or "")]))
    if loc:
        return loc
    addresses = data.get("addresses") or []
    if addresses and isinstance(addresses[0], dict):
        a0 = addresses[0]
        return normalize_location(" ".join([str(a0.get("address_level1") or ""), str(a0.get("address_level2") or "")]))
    return ""


def location_saramin(external_id, _url):
    text = _read_retry(f"https://m.saramin.co.kr/job-search/view?rec_idx={external_id}", SARAMIN_HEADERS)
    m = re.search(r'<dt class="tit">지역</dt>\s*<dd class="desc">\s*<div class="crop_button">(.*?)</div>', text, re.S)
    if m:
        loc = normalize_location(m.group(1))
        if loc:
            return loc
    m = re.search(r'<address class="txt_address">\s*<span>(.*?)</span>', text, re.S)
    return normalize_location(m.group(1)) if m else ""


def location_incruit(external_id, _url):
    text = _read_retry(f"https://job.incruit.com/jobdb_info/jobpost.asp?job={external_id}", INCRUIT_HEADERS, "euc-kr")
    m = re.search(r'<em>근무지역</em>.*?<div class="txt">\s*<em>(.*?)</em>', text, re.S)
    return normalize_location(m.group(1)) if m else ""


def location_jobkorea(external_id, url):
    text = _read_retry(f"https://m.jobkorea.co.kr/Recruit/GI_Read/{external_id}", JOBKOREA_HEADERS)
    m = re.search(r'"jobLocation".{0,400}?"streetAddress"\s*:\s*"([^"]+)"', text, re.S)
    if m:
        loc = normalize_location(m.group(1))
        if loc:
            return loc
    return ""


DETAIL_FETCHERS = {
    "jumpit": location_jumpit,
    "remember": location_remember,
    "saramin": location_saramin,
    "incruit": location_incruit,
    "jobkorea": location_jobkorea,
}


def list_refresh(conn, dry_run, now):
    """각 플랫폼 목록을 다시 훑어 "(플랫폼, 공고 ID) → 근무지" 로 비어 있는 행을 채운다.

    상세 페이지에 근무지 항목이 없는 공고(자유 양식 공고)도 목록 카드에는 지역이 찍혀 있고,
    예전 크롤러가 목록 단계에서 근무지를 놓쳤던 공고를 한 번에 되살릴 수 있다.
    """
    from crawler import (fetch_wanted, fetch_jumpit, fetch_saramin, fetch_remember,
                         fetch_jobkorea, fetch_incruit, get_today_kst)
    today = get_today_kst()
    tasks = {
        "wanted": lambda: fetch_wanted(),
        "jumpit": lambda: fetch_jumpit(today),
        "saramin": lambda: fetch_saramin(today),
        "remember": lambda: fetch_remember(today),
        "jobkorea": lambda: fetch_jobkorea(today),
        "incruit": lambda: fetch_incruit(today),
    }
    lookup = {}
    for prefix, fn in tasks.items():
        try:
            rows = fn()
        except Exception as exc:
            print(f"  [목록 재수집 경고] {prefix}: {type(exc).__name__}", flush=True)
            continue
        for row in rows:
            loc = row.get("location") or ""
            jid = str(row.get("external_id") or "")
            if loc and jid:
                lookup[(prefix, jid)] = loc
        print(f"  [목록 재수집] {PLATFORM_BY_PREFIX.get(prefix, prefix)} {len(rows)}건 · 근무지 {sum(1 for r in rows if r.get('location'))}건", flush=True)

    filled = 0
    for row in load_rows(conn, only_empty=True):
        prefix = platform_of(row["job_key"])
        key = (prefix, external_id_of(row["job_key"]))
        loc = lookup.get(key)
        if not loc:
            continue
        filled += 1
        if not dry_run:
            conn.execute("UPDATE jobs SET location=?, updated_at=? WHERE job_key=?",
                         (loc, now, row["job_key"]))
    if not dry_run:
        conn.commit()
    print(f"-> 목록 재수집으로 보완: {filled}건", flush=True)
    return filled


def load_rows(conn, only_empty=True):
    sql = "SELECT job_key, url, location FROM jobs WHERE status='ACTIVE'"
    if only_empty:
        sql += " AND trim(coalesce(location,''))=''"
    return conn.execute(sql).fetchall()


def platform_of(job_key):
    return (job_key or "").split(":")[0]


def external_id_of(job_key):
    parts = (job_key or "").split(":")
    return parts[1] if len(parts) > 1 else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="DB에 쓰지 않고 조회 결과만 확인")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--db", default=DB_PATH)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")

    # 1) 이미 채워진 값 표기 정리 ('서울 강남구 외' → '서울 강남구', '세종전지역' → '세종')
    renormalized = 0
    for row in load_rows(conn, only_empty=False):
        current = row["location"] or ""
        cleaned = normalize_location(current)
        if cleaned and cleaned != current:
            renormalized += 1
            if not args.dry_run:
                conn.execute("UPDATE jobs SET location=?, updated_at=? WHERE job_key=?",
                             (cleaned, now, row["job_key"]))
    print(f"-> 기존 표기 정리: {renormalized}건", flush=True)

    # 2) 목록 재수집 — 목록 카드에 찍힌 지역으로 한 번에 보완
    list_refresh(conn, args.dry_run, now)

    # 3) 비어 있는 근무지 — 원문 상세 조회
    pending = load_rows(conn, only_empty=True)
    by_platform = Counter(platform_of(r["job_key"]) for r in pending)
    print(f"-> 근무지 없는 활성 공고 {len(pending)}건: "
          + ", ".join(f"{PLATFORM_BY_PREFIX.get(k, k)} {v}" for k, v in by_platform.most_common()), flush=True)

    def worker(row):
        platform = platform_of(row["job_key"])
        fetcher = DETAIL_FETCHERS.get(platform)
        if not fetcher:
            return row, "", "no-fetcher"
        try:
            return row, fetcher(external_id_of(row["job_key"]), row["url"]), "ok"
        except Exception as exc:  # 네트워크·파싱 예외는 건별로 격리한다
            return row, "", type(exc).__name__

    filled = defaultdict(int)
    failed = defaultdict(int)
    remaining = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        for row, loc, status in executor.map(worker, pending):
            platform = PLATFORM_BY_PREFIX.get(platform_of(row["job_key"]), platform_of(row["job_key"]))
            if loc:
                filled[platform] += 1
                if not args.dry_run:
                    conn.execute("UPDATE jobs SET location=?, updated_at=? WHERE job_key=?",
                                 (loc, now, row["job_key"]))
            else:
                failed[platform] += 1
                remaining.append({"job_key": row["job_key"], "platform": platform, "reason": status})

    if not args.dry_run:
        conn.commit()

    total_platform = Counter(PLATFORM_BY_PREFIX.get(platform_of(r["job_key"]), platform_of(r["job_key"]))
                             for r in pending)
    print("\n=== 플랫폼별 백필 결과 ===")
    for platform in sorted(total_platform, key=lambda p: -total_platform[p]):
        print(f"  {platform:6} 대상 {total_platform[platform]:4}건 · 채움 {filled[platform]:4}건 · 미확인 {failed[platform]:3}건")
    print(f"  합계   대상 {len(pending)}건 · 채움 {sum(filled.values())}건 · 미확인 {len(remaining)}건")

    active = conn.execute(
        "SELECT count(*) n, sum(case when trim(coalesce(location,''))<>'' then 1 else 0 end) f FROM jobs WHERE status='ACTIVE'"
    ).fetchone()
    print(f"-> 활성 공고 근무지 보유: {active['f']}/{active['n']}건")
    if remaining:
        print("-> 끝까지 비어 있는 공고(원문에 근무지 표기 없음 또는 상세 조회 실패):")
        for item in remaining[:15]:
            print(f"   · {item['platform']} {item['job_key']} ({item['reason']})")
        if len(remaining) > 15:
            print(f"   · …외 {len(remaining) - 15}건")
    if args.dry_run:
        print("(dry-run: DB에 반영하지 않았습니다)")
    conn.close()


if __name__ == "__main__":
    main()

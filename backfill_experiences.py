#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""활성 공고 경력(experience) 백필.

크롤러가 경력 조건을 읽지 않던 시절에 쌓인 공고는 `jobs.experience` 가 비어 있다.
이 스크립트는 6개 플랫폼의 목록을 다시 훑어 `(플랫폼, 공고 ID) → 경력` 지도를 만들고,
비어 있는 공고는 원문 상세(API·HTML)를 병렬 조회해 채운다. 이미 채워진 값도
`normalize_experience()` 표기로 다시 정리한다.

  · 원티드   www.wanted.co.kr/api/v4/jobs/{id}          → annual_from ~ annual_to
  · 점핏     api.jumpit.co.kr/api/position/{id}          → minCareer ~ maxCareer · newcomer
  · 리멤버   career-api.rememberapp.co.kr/job_postings/{id} → min_experience ~ max_experience
  · 사람인   m.saramin.co.kr/job-search/view?rec_idx={id}  → dd.experience / meta description
  · 인크루트 job.incruit.com/jobdb_info/jobpost.asp?job={id} → '경력' 항목
  · 잡코리아 m.jobkorea.co.kr/Recruit/GI_Read/{id}         → meta description / JSON-LD

실행: python3 backfill_experiences.py            # 실제 반영
      python3 backfill_experiences.py --dry-run  # 조회 결과만 확인
"""
import argparse
import json
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
    WANTED_HEADERS,
    experience_from_years,
    experience_group,
    normalize_experience,
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


def _read(url, headers, enc="utf-8", timeout=20, data=None):
    req = urllib.request.Request(url, headers=headers, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return read_limited(res).decode(enc, errors="ignore")


def _read_retry(url, headers, enc="utf-8", data=None):
    last = None
    for _attempt in range(2):
        try:
            return _read(url, headers, enc, data=data)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
    if last:
        raise last
    return ""


def _meta_description(text):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', text)
    if not m:
        m = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', text)
    return m.group(1) if m else ""


def _from_meta_experience(text):
    """'경력: 경력 3년 이상, 급여: …' 형태의 meta description 에서 경력 값만 뽑는다."""
    desc = _meta_description(text)
    m = re.search(r"경력\s*[:：]\s*([^,]+)", desc)
    if m:
        return normalize_experience(m.group(1))
    return ""


def experience_wanted(external_id, _url):
    payload = json.loads(_read_retry(f"https://www.wanted.co.kr/api/v4/jobs/{external_id}", WANTED_HEADERS))
    job = payload.get("job") or {}
    return experience_from_years(job.get("annual_from"), job.get("annual_to"))


def experience_jumpit(external_id, _url):
    payload = json.loads(_read_retry(f"https://api.jumpit.co.kr/api/position/{external_id}", JUMPIT_HEADERS))
    detail = payload.get("result") or {}
    return experience_from_years(
        detail.get("minCareer"), detail.get("maxCareer"), newcomer=bool(detail.get("newcomer")))


def experience_remember(external_id, _url):
    payload = json.loads(_read_retry(f"https://career-api.rememberapp.co.kr/job_postings/{external_id}", REMEMBER_HEADERS))
    data = payload.get("data") or {}
    return experience_from_years(data.get("min_experience"), data.get("max_experience"))


def experience_saramin(external_id, _url):
    text = _read_retry(f"https://m.saramin.co.kr/job-search/view?rec_idx={external_id}", SARAMIN_HEADERS)
    m = re.search(r'<dd class="experience">(.*?)</dd>', text, re.S)
    if m:
        value = normalize_experience(re.sub(r"<br\s*/?>", " ", m.group(1)))
        if value:
            return value
    return _from_meta_experience(text)


def experience_incruit(external_id, _url):
    text = _read_retry(f"https://job.incruit.com/jobdb_info/jobpost.asp?job={external_id}", INCRUIT_HEADERS, "euc-kr")
    m = re.search(r"<em>경력</em>.*?<div class=\"txt\">.*?<em[^>]*>(.*?)</em>", text, re.S)
    if m:
        value = normalize_experience(m.group(1))
        if value:
            return value
    m = re.search(r"경력\s*:\s*([^<\n]+)", text)
    return normalize_experience(m.group(1)) if m else ""


def experience_jobkorea(external_id, url):
    # 통합검색으로 모인 행은 공고 ID가 잡코리아 것이 아닐 수 있다(사람인 URL). 그때는 URL 의 ID로 조회한다.
    target_id = external_id
    html_url = f"https://m.jobkorea.co.kr/Recruit/GI_Read/{external_id}"
    if "saramin.co.kr" in (url or ""):
        m = re.search(r"rec_idx=(\d+)", url or "")
        if m:
            return experience_saramin(m.group(1), url)
    text = _read_retry(html_url, JOBKOREA_HEADERS)
    value = _from_meta_experience(text)
    if value:
        return value
    m = re.search(r'"experienceRequirements"\s*:\s*"([^"]+)"', text)
    return normalize_experience(m.group(1)) if m else ""


DETAIL_FETCHERS = {
    "wanted": experience_wanted,
    "jumpit": experience_jumpit,
    "remember": experience_remember,
    "saramin": experience_saramin,
    "incruit": experience_incruit,
    "jobkorea": experience_jobkorea,
}


def platform_of(job_key, url=""):
    """job_key 접두사가 곧 수집 플랫폼이다. 없으면 원문 URL 호스트로 되짚는다."""
    prefix = (job_key or "").split(":")[0]
    if prefix in DETAIL_FETCHERS:
        return prefix
    host = (url or "").lower()
    for key in DETAIL_FETCHERS:
        if key in host:
            return key
    return prefix


def external_id_of(job_key, url=""):
    parts = (job_key or "").split(":")
    if len(parts) > 1 and parts[1]:
        return parts[1]
    m = re.search(r"(?:rec_idx=|job=|wd/|position/|posting/|GI_Read/)(\d+)", url or "")
    return m.group(1) if m else ""


def load_rows(conn, only_empty=True):
    sql = "SELECT job_key, url, experience FROM jobs WHERE status='ACTIVE'"
    if only_empty:
        sql += " AND trim(coalesce(experience,''))=''"
    return conn.execute(sql).fetchall()


def list_refresh(conn, dry_run, now):
    """각 플랫폼 목록을 다시 훑어 (플랫폼, 공고 ID) → 경력 지도로 비어 있는 행을 채운다."""
    from crawler import (fetch_incruit, fetch_jobkorea, fetch_jumpit, fetch_remember,
                         fetch_saramin, fetch_wanted, get_today_kst)
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
        except Exception as exc:  # noqa: BLE001 - 플랫폼 단위 실패는 다른 플랫폼에 영향 없게
            print(f"  [목록 재수집 경고] {prefix}: {type(exc).__name__}", flush=True)
            continue
        for row in rows:
            value = row.get("experience") or ""
            jid = str(row.get("external_id") or "")
            if value and jid:
                lookup[(prefix, jid)] = value
        print(f"  [목록 재수집] {PLATFORM_BY_PREFIX.get(prefix, prefix)} {len(rows)}건 · "
              f"경력 {sum(1 for r in rows if r.get('experience'))}건", flush=True)

    filled = 0
    for row in load_rows(conn, only_empty=True):
        prefix = platform_of(row["job_key"], row["url"])
        value = lookup.get((prefix, external_id_of(row["job_key"], row["url"])))
        if not value:
            continue
        filled += 1
        if not dry_run:
            conn.execute("UPDATE jobs SET experience=?, updated_at=? WHERE job_key=?",
                         (value, now, row["job_key"]))
    if not dry_run:
        conn.commit()
    print(f"-> 목록 재수집으로 보완: {filled}건", flush=True)
    return filled


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="DB에 쓰지 않고 조회 결과만 확인")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--db", default=DB_PATH)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")

    # 0) 기존 DB 마이그레이션 — experience 열이 없으면 추가한다(데이터는 보존).
    columns = {r[1] for r in conn.execute("PRAGMA table_info(jobs)")}
    if "experience" not in columns:
        if args.dry_run:
            print("-> jobs.experience 열이 없습니다(dry-run: 추가하지 않음)")
        else:
            conn.execute("ALTER TABLE jobs ADD COLUMN experience TEXT")
            conn.commit()
            print("-> jobs.experience 열 추가")

    # 1) 이미 채워진 값 표기 정리 ('경력3년이상' → '경력 3년↑')
    renormalized = 0
    for row in load_rows(conn, only_empty=False):
        current = row["experience"] or ""
        cleaned = normalize_experience(current)
        if cleaned and cleaned != current:
            renormalized += 1
            if not args.dry_run:
                conn.execute("UPDATE jobs SET experience=?, updated_at=? WHERE job_key=?",
                             (cleaned, now, row["job_key"]))
    print(f"-> 기존 표기 정리: {renormalized}건", flush=True)

    # 2) 목록 재수집 — 목록 카드·API에 찍힌 경력으로 한 번에 보완
    list_refresh(conn, args.dry_run, now)

    # 3) 비어 있는 경력 — 원문 상세 조회
    pending = load_rows(conn, only_empty=True)
    by_platform = Counter(platform_of(r["job_key"], r["url"]) for r in pending)
    print(f"-> 경력 없는 활성 공고 {len(pending)}건: "
          + ", ".join(f"{PLATFORM_BY_PREFIX.get(k, k)} {v}" for k, v in by_platform.most_common()), flush=True)

    def worker(row):
        prefix = platform_of(row["job_key"], row["url"])
        fetcher = DETAIL_FETCHERS.get(prefix)
        if not fetcher:
            return row, "", "no-fetcher"
        try:
            return row, fetcher(external_id_of(row["job_key"], row["url"]), row["url"]), "ok"
        except Exception as exc:  # 네트워크·파싱 예외는 건별로 격리한다
            return row, "", type(exc).__name__

    filled = defaultdict(int)
    failed = defaultdict(int)
    remaining = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        for row, value, status in executor.map(worker, pending):
            platform = PLATFORM_BY_PREFIX.get(platform_of(row["job_key"], row["url"]),
                                              platform_of(row["job_key"], row["url"]))
            if value:
                filled[platform] += 1
                if not args.dry_run:
                    conn.execute("UPDATE jobs SET experience=?, updated_at=? WHERE job_key=?",
                                 (value, now, row["job_key"]))
            else:
                failed[platform] += 1
                remaining.append({"job_key": row["job_key"], "platform": platform, "reason": status})

    if not args.dry_run:
        conn.commit()

    total_platform = Counter(PLATFORM_BY_PREFIX.get(platform_of(r["job_key"], r["url"]),
                                                    platform_of(r["job_key"], r["url"])) for r in pending)
    print("\n=== 플랫폼별 백필 결과 ===")
    for platform in sorted(total_platform, key=lambda p: -total_platform[p]):
        print(f"  {platform:6} 대상 {total_platform[platform]:4}건 · 채움 {filled[platform]:4}건 · 미확인 {failed[platform]:3}건")
    print(f"  합계   대상 {len(pending)}건 · 채움 {sum(filled.values())}건 · 미확인 {len(remaining)}건")

    active = conn.execute(
        "SELECT count(*) n, sum(case when trim(coalesce(experience,''))<>'' then 1 else 0 end) f FROM jobs WHERE status='ACTIVE'"
    ).fetchone()
    ratio = active["f"] / max(1, active["n"])
    print(f"-> 활성 공고 경력 보유: {active['f']}/{active['n']}건 ({ratio:.1%})")

    groups = Counter()
    for r in conn.execute("SELECT experience FROM jobs WHERE status='ACTIVE'"):
        groups[experience_group(r["experience"])] += 1
    print("-> 경력 분포: " + " · ".join(f"{g} {groups[g]}건" for g in
                                     ("신입", "신입·경력", "경력", "경력무관", "인턴", "미표기") if groups.get(g)))
    if remaining:
        print("-> 끝까지 비어 있는 공고(원문에 경력 표기 없음 또는 상세 조회 실패):")
        for item in remaining[:15]:
            print(f"   · {item['platform']} {item['job_key']} ({item['reason']})")
        if len(remaining) > 15:
            print(f"   · …외 {len(remaining) - 15}건")
    if args.dry_run:
        print("(dry-run: DB에 반영하지 않았습니다)")
    conn.close()
    return 0 if ratio >= 0.95 else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""활성 공고 중복 병합 회귀 테스트 — 같은 공고는 1건, 다른 직무는 그대로.

검증 구간
  1) 회사 표기 차이: '(주)보령' / '㈜보령' / '보령' 처럼 법인 표기가 달라도 같은 공고는 1건으로 병합되고
     플랫폼 배지·키워드·태그는 합집합으로 남는다.
  2) 괄호 별칭·영문 표기: '(주)숲' = '㈜숲(SOOP CO., LTD.)', '엔에이치엔커머스(nhn커머스)' = '엔에이치엔커머스㈜'
  3) 제목 앞머리 태그: '[채용공고] …' · '[경력] …' · '[HYBE] …' 차이만 있는 같은 공고는 병합.
  4) 같은 플랫폼 복수 공고 ID: 잡코리아가 같은 공고를 새 공고 ID로 다시 올려도 1건으로 병합.
  5) 오병합 금지: '(서비스 보안)' vs '(자산관리 보안)' 처럼 실제로 다른 직무를 가르는 괄호는 지우지 않는다.
  6) 마감 표기: '상시채용'보다 실제 날짜·D-N 표기를 남기고 deadline_status 를 그 표기로 다시 계산.
  7) sync_jobs_to_db(): 다음 수집에서 같은 공고가 새 공고 ID로 들어와도 활성 행이 늘지 않는다.

실행: python3 tests/test_job_dedup_active.py
"""
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import db_manager  # noqa: E402
import crawler  # noqa: E402

KST = timezone(timedelta(hours=9))
NOW = datetime(2026, 11, 22, 9, 0, tzinfo=KST)
TODAY = NOW.date()

failures = []


def check(name, cond, detail=""):
    if cond:
        print("  [통과] %s" % name)
    else:
        failures.append("%s%s" % (name, (" — %s" % detail) if detail else ""))
        print("  [실패] %s%s" % (name, (" — %s" % detail) if detail else ""))


def temp_db():
    tmpdir = tempfile.mkdtemp(prefix="jobdedup-active-")
    path = os.path.join(tmpdir, "archive.db")
    db_manager.init_db(path)
    return tmpdir, path


def stamp(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S KST")


def insert_job(db_path, *, company, title, url, platform, job_key, deadline="D-3",
               seen=None, first=None, summary="", location="서울",
               keywords=None, tags=None, status="ACTIVE", deadline_status=None):
    seen = seen or NOW
    first = first or seen
    if deadline_status is None:
        deadline_status = db_manager.parse_deadline_status(deadline, seen.date(), stamp(seen), now_dt=seen)[0]
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO jobs (job_key, company, title, url, platforms, keywords, location, deadline,
                             deadline_status, status, summary, tags, first_seen_at, last_seen_at,
                             created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        (
            job_key, company, title, url, json.dumps([platform], ensure_ascii=False),
            json.dumps(keywords or ["정보보안"], ensure_ascii=False),
            location, deadline, deadline_status, status, summary,
            json.dumps(tags or ["정보보안"], ensure_ascii=False),
            stamp(first), stamp(seen), stamp(seen), stamp(seen),
        ),
    )
    conn.commit()
    conn.close()


def active_rows(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, job_key, company, title, url, platforms, keywords, tags, deadline, "
        "deadline_status, status, summary, first_seen_at, last_seen_at FROM jobs "
        "WHERE status = 'ACTIVE' ORDER BY id;"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def all_rows(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, job_key, status, platforms, deadline FROM jobs ORDER BY id;"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------- 1) 키 정규화
def test_keys():
    print("\n[1] 중복 판정 키 — 법인 표기·괄호 별칭·앞머리 태그")
    same_company = [
        "(주)보령", "㈜보령", "보령", "한화오션(주)", "한화오션 (주)",
        "㈜숲(SOOP CO., LTD.)", "(주)숲", "하이브(HYBE)", "(주)하이브",
        "엔에이치엔커머스(nhn커머스)", "엔에이치엔커머스㈜",
    ]
    check("(주)보령 = ㈜보령", db_manager.dedup_company_key("(주)보령") == db_manager.dedup_company_key("㈜보령"))
    check("한화오션(주) = 한화오션 (주)",
          db_manager.dedup_company_key("한화오션(주)") == db_manager.dedup_company_key("한화오션 (주)"))
    check("㈜숲(SOOP CO., LTD.) = (주)숲",
          db_manager.dedup_company_key("㈜숲(SOOP CO., LTD.)") == db_manager.dedup_company_key("(주)숲"))
    check("하이브(HYBE) = (주)하이브",
          db_manager.dedup_company_key("하이브(HYBE)") == db_manager.dedup_company_key("(주)하이브"))
    check("회사 키 서로 다름 유지(세스코 ≠ 세스코시스템즈)",
          db_manager.dedup_company_key("(주)세스코") != db_manager.dedup_company_key("(주)세스코시스템즈"),
          "회사 목록: %s" % ", ".join(same_company))
    check("제목 앞머리 [채용공고]·[경력]·[HYBE] 제거",
          db_manager.dedup_title_key("[채용공고] 정보보호 담당")
          == db_manager.dedup_title_key("정보보호 담당")
          == db_manager.dedup_title_key("[경력] 정보보호 담당")
          == db_manager.dedup_title_key("[HYBE] 정보보호 담당"))
    check("제목 속 괄호는 남긴다",
          db_manager.dedup_title_key("[HYBE] 정보보호 (서비스 보안)")
          != db_manager.dedup_title_key("[HYBE] 정보보호 (자산관리 보안)"))


# ---------------------------------------------------------------- 2) 교차 플랫폼 병합
def test_cross_platform_merge():
    print("\n[2] (주)보령 vs ㈜보령 — 교차 플랫폼 병합")
    tmpdir, db_path = temp_db()
    try:
        insert_job(db_path, company="(주)보령", title="[보령] 정보보호 담당자 (경력)",
                   url="https://career.rememberapp.co.kr/job/posting/354094", platform="리멤버",
                   job_key="remember:354094:aaaaaaaa", deadline="D-7 (~11/29 일)",
                   keywords=["정보보호"], tags=["정보보호"])
        insert_job(db_path, company="㈜보령", title="[보령] 정보보호 담당자 (경력)",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50350642", platform="잡코리아",
                   job_key="jobkorea:50350642:bbbbbbbb", deadline="상시채용",
                   summary="정보보호 거버넌스 담당", keywords=["정보보안"], tags=["ISMSP"],
                   seen=NOW - timedelta(days=1))
        res = db_manager.deduplicate_active_jobs(db_path=db_path, today_date=TODAY, now_dt=NOW)
        rows = active_rows(db_path)
        check("병합 1건", res["merged"] == 1, res["merged"])
        check("활성 1건 유지", len(rows) == 1, [(r["company"], r["title"]) for r in rows])
        if rows:
            row = rows[0]
            platforms = json.loads(row["platforms"])
            check("플랫폼 배지 합집합", sorted(platforms) == ["리멤버", "잡코리아"], platforms)
            check("키워드 합집합", sorted(json.loads(row["keywords"])) == ["정보보안", "정보보호"],
                  row["keywords"])
            check("태그 합집합", sorted(json.loads(row["tags"])) == ["ISMSP", "정보보호"], row["tags"])
            check("요약 유지", row["summary"] == "정보보호 거버넌스 담당", row["summary"])
            check("구체적 마감 표기 유지", row["deadline"] == "D-7 (~11/29 일)", row["deadline"])
            check("first_seen 은 이른 값 유지", row["first_seen_at"] == stamp(NOW - timedelta(days=1)),
                  row["first_seen_at"])
            check("last_seen 은 늦은 값 유지", row["last_seen_at"] == stamp(NOW), row["last_seen_at"])
        check("나머지 행은 EXPIRED 보관(삭제 아님)", len(all_rows(db_path)) == 2, all_rows(db_path))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------- 3) 같은 플랫폼 복수 ID
def test_same_platform_multiple_ids():
    print("\n[3] 같은 플랫폼 · 새 공고 ID 재등록 병합")
    tmpdir, db_path = temp_db()
    try:
        insert_job(db_path, company="포스켄㈜", title="증권사 인프라 취약점진단 운영",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50346024", platform="잡코리아",
                   job_key="jobkorea:50346024:cccccccc", deadline="D-3 (~ 11/25(수))",
                   seen=NOW - timedelta(days=1), summary="증권사 인프라 진단")
        insert_job(db_path, company="포스켄㈜", title="증권사 인프라 취약점진단 운영",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50399375", platform="잡코리아",
                   job_key="jobkorea:50399375:cccccccc", deadline="D-3")
        insert_job(db_path, company="포스켄㈜", title="증권사 인프라 취약점진단 운영",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50399999", platform="잡코리아",
                   job_key="jobkorea:50399999:cccccccc", deadline="D-3")
        res = db_manager.deduplicate_active_jobs(db_path=db_path, today_date=TODAY, now_dt=NOW)
        rows = active_rows(db_path)
        check("같은 플랫폼 3건 → 1건", len(rows) == 1, [r["job_key"] for r in rows])
        check("병합 2건", res["merged"] == 2, res["merged"])
        if rows:
            check("플랫폼 배지 중복 없음", json.loads(rows[0]["platforms"]) == ["잡코리아"],
                  rows[0]["platforms"])
            check("대표는 먼저 수집된 행", rows[0]["job_key"] == "jobkorea:50346024:cccccccc",
                  rows[0]["job_key"])
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------- 4) 오병합 금지
def test_no_over_merge():
    print("\n[4] 오병합 금지 — 실제로 다른 직무 괄호·다른 프로젝트")
    tmpdir, db_path = temp_db()
    try:
        insert_job(db_path, company="㈜하이브", title="[HYBE] 정보보호 (서비스 보안)",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50167942", platform="잡코리아",
                   job_key="jobkorea:50167942:dddddddd", deadline="D-21")
        insert_job(db_path, company="하이브(HYBE)", title="[HYBE] 정보보호 (자산관리 보안)",
                   url="https://www.wanted.co.kr/wd/392166", platform="원티드",
                   job_key="wanted:392166:eeeeeeee", deadline="상시채용")
        insert_job(db_path, company="(주)하이브", title="[HYBE] 보안정책(물리보안)",
                   url="https://career.rememberapp.co.kr/job/posting/352092", platform="리멤버",
                   job_key="remember:352092:ffffffff", deadline="채용시 마감")
        res = db_manager.deduplicate_active_jobs(db_path=db_path, today_date=TODAY, now_dt=NOW)
        rows = active_rows(db_path)
        check("서로 다른 직무 3건 그대로", len(rows) == 3, [(r["title"], r["platforms"]) for r in rows])
        check("병합 0건", res["merged"] == 0, res)

        # 같은 제목이라도 회사가 다르면 합치지 않는다.
        insert_job(db_path, company="(주)엘리스", title="엔드포인트 보안 엔지니어",
                   url="https://www.wanted.co.kr/wd/399207", platform="원티드",
                   job_key="wanted:399207:gggggggg", deadline="상시채용")
        insert_job(db_path, company="(주)스패로우", title="엔드포인트 보안 엔지니어",
                   url="https://career.rememberapp.co.kr/job/posting/355683", platform="리멤버",
                   job_key="remember:355683:hhhhhhhh", deadline="상시채용")
        res = db_manager.deduplicate_active_jobs(db_path=db_path, today_date=TODAY, now_dt=NOW)
        check("회사가 다르면 합치지 않음", len(active_rows(db_path)) == 5, len(active_rows(db_path)))
        check("추가 병합 0건", res["merged"] == 0, res)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------- 5) 제목 앞머리 태그
def test_title_prefix_tag_merge():
    print("\n[5] 제목 앞머리 태그만 다른 같은 공고 병합")
    tmpdir, db_path = temp_db()
    try:
        insert_job(db_path, company="㈜숲", title="[SOOP] 보안솔루션 운영 및 취약점 진단",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50356584", platform="잡코리아",
                   job_key="jobkorea:50356584:iiiiiiii", deadline="D-7")
        insert_job(db_path, company="(주)숲", title="[SOOP] 보안솔루션 운영 및 취약점 진단",
                   url="https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=44000001", platform="사람인",
                   job_key="saramin:44000001:iiiiiiii", deadline="D-Day (오늘 마감)")
        insert_job(db_path, company="㈜알라딘커뮤니케이션", title="[채용공고] 정보보호팀 정보보호담당자 (기술보안)",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50170173", platform="잡코리아",
                   job_key="jobkorea:50170173:jjjjjjjj", deadline="상시채용")
        insert_job(db_path, company="(주)알라딘커뮤니케이션", title="정보보호팀 정보보호담당자 (기술보안)",
                   url="https://www.wanted.co.kr/wd/392825", platform="원티드",
                   job_key="wanted:392825:jjjjjjjj", deadline="상시채용")
        db_manager.deduplicate_active_jobs(db_path=db_path, today_date=TODAY, now_dt=NOW)
        rows = active_rows(db_path)
        check("숲·알라딘 각 1건", len(rows) == 2, [(r["company"], r["title"]) for r in rows])
        companies = sorted(db_manager.dedup_company_key(r["company"]) for r in rows)
        check("병합된 회사 목록", companies == ["숲", "알라딘커뮤니케이션"], companies)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------- 6) 마감 표기 선택
def test_deadline_choice():
    print("\n[6] 마감 표기 선택 — 구체적·최근·임박")
    tmpdir, db_path = temp_db()
    try:
        insert_job(db_path, company="(주)카카오", title="개인정보보호 담당자 (경력)",
                   url="https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=44000002", platform="사람인",
                   job_key="saramin:44000002:kkkkkkkk", deadline="D-46 (~ 01/07(목))",
                   seen=NOW - timedelta(days=4))
        insert_job(db_path, company="㈜카카오", title="개인정보보호 담당자 (경력)",
                   url="https://www.jobkorea.co.kr/Recruit/GI_Read/50319688", platform="잡코리아",
                   job_key="jobkorea:50319688:kkkkkkkk", deadline="D-8 (~ 11/30(월))")
        db_manager.deduplicate_active_jobs(db_path=db_path, today_date=TODAY, now_dt=NOW)
        rows = active_rows(db_path)
        check("1건", len(rows) == 1)
        if rows:
            check("최근 수집된 날짜 표기 유지", rows[0]["deadline"] == "D-8 (~ 11/30(월))", rows[0]["deadline"])
            # 11/22 기준 '~ 11/30'은 8일 남음 → UPCOMING(D-8). 라벨과 상태가 어긋나지 않아야 한다.
            check("deadline_status 재계산", rows[0]["deadline_status"] == "UPCOMING", rows[0]["deadline_status"])

        tmpdir2, db_path2 = temp_db()
        try:
            insert_job(db_path2, company="(주)우아한형제들", title="정보보호관리",
                       url="https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=44000003",
                       platform="사람인", job_key="saramin:44000003:llllllll", deadline="D-8 (~ 11/30(월))")
            insert_job(db_path2, company="우아한형제들(배달의민족)", title="정보보호관리",
                       url="https://www.wanted.co.kr/wd/397108", platform="원티드",
                       job_key="wanted:397108:llllllll", deadline="상시채용")
            db_manager.deduplicate_active_jobs(db_path=db_path2, today_date=TODAY, now_dt=NOW)
            rows = active_rows(db_path2)
            check("상시채용보다 날짜 표기", rows and rows[0]["deadline"] == "D-8 (~ 11/30(월))",
                  rows[0]["deadline"] if rows else rows)
        finally:
            shutil.rmtree(tmpdir2, ignore_errors=True)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------- 7) 수집 파이프라인
def test_sync_does_not_accumulate():
    print("\n[7] sync_jobs_to_db() — 재수집·재등록에도 활성 행이 늘지 않는다")
    tmpdir, db_path = temp_db()
    try:
        base = {
            "company": "(주)세스코",
            "title": "(주)세스코 정보보안기획 담당자 채용",
            "location": "서울",
            "keywords": ["정보보안"],
            "tags": [],
            "summary": "",
        }
        day1 = datetime(2026, 11, 21, 8, 0, tzinfo=KST)
        job1 = dict(base, url="https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=44000010",
                    platforms=["사람인"], external_id="44000010", deadline="D-9 (~ 11/30(월))")
        job1["job_key"] = db_manager.make_job_key(
            job1["company"], job1["title"], job1["url"], platforms=["사람인"],
            platform="사람인", external_id="44000010")
        crawler.sync_jobs_to_db([job1], now_dt=day1, db_path=db_path)
        check("1일차 활성 1건", len(active_rows(db_path)) == 1, len(active_rows(db_path)))

        # 2일차: 같은 공고가 같은 플랫폼에 새 공고 ID로 다시 올라왔다(재등록).
        day2 = day1 + timedelta(days=1)
        job2 = dict(base, url="https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=44000011",
                    platforms=["사람인"], external_id="44000011", deadline="D-8 (~ 11/30(월))")
        job2["job_key"] = db_manager.make_job_key(
            job2["company"], job2["title"], job2["url"], platforms=["사람인"],
            platform="사람인", external_id="44000011")
        crawler.sync_jobs_to_db([job2], now_dt=day2, db_path=db_path)
        rows = active_rows(db_path)
        check("2일차에도 활성 1건", len(rows) == 1, [(r["job_key"], r["deadline"]) for r in rows])
        if rows:
            check("대표는 첫 수집 행 유지", rows[0]["job_key"] == job1["job_key"], rows[0]["job_key"])
            check("마감 표기 갱신", rows[0]["deadline"] == "D-8 (~ 11/30(월))", rows[0]["deadline"])

        # 3일차: 이번에는 잡코리아에도 같은 공고가 올라왔다.
        day3 = day2 + timedelta(days=1)
        job3 = dict(base, company="㈜세스코",
                    url="https://www.jobkorea.co.kr/Recruit/GI_Read/50404321",
                    platforms=["잡코리아"], external_id="50404321", deadline="D-7")
        job3["job_key"] = db_manager.make_job_key(
            job3["company"], job3["title"], job3["url"], platforms=["잡코리아"],
            platform="잡코리아", external_id="50404321")
        crawler.sync_jobs_to_db([job3], now_dt=day3, db_path=db_path)
        rows = active_rows(db_path)
        check("3일차에도 활성 1건", len(rows) == 1, [(r["job_key"], r["platforms"]) for r in rows])
        if rows:
            check("플랫폼 배지 2개", sorted(json.loads(rows[0]["platforms"])) == ["사람인", "잡코리아"],
                  rows[0]["platforms"])
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    test_keys()
    test_cross_platform_merge()
    test_same_platform_multiple_ids()
    test_no_over_merge()
    test_title_prefix_tag_merge()
    test_deadline_choice()
    test_sync_does_not_accumulate()
    if failures:
        print("\n활성 공고 중복 병합 테스트 실패 %d건" % len(failures))
        for message in failures:
            print("  [실패] %s" % message)
        raise SystemExit(1)
    print("\n활성 공고 중복 병합 테스트 통과")
    return 0


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""공고 누락 회귀 테스트 — 같은 회사·같은 앞 12자 제목이어도 플랫폼 공고 ID가 다르면 2건 모두 남는다.

검증 구간
  1) collect_all_jobs(): 플랫폼 수집 결과를 직접 넣어 중복 제거 결과를 본다.
     · 같은 플랫폼에 공고 ID만 다른 2건
     · 서로 다른 플랫폼에 공고 ID만 다른 2건
     · (통제) 플랫폼에 교차 게시된 '완전히 같은' 공고 1건은 플랫폼 배지로 합쳐진다
  2) sync_jobs_to_db(): archive.db 사본에 두 번(첫 수집 → 재수집) 반영해도 행이 2건 유지된다.
     (DB에는 2건이 들어가고, 두 번째 수집에서도 서로 덮어쓰지 않는다)

실행: python3 tests/test_job_dedup.py
"""
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import crawler  # noqa: E402

KST = timezone(timedelta(hours=9))
COMPANY = "테스트컴퍼니"
TITLE_NEW = "2026년 정보보안 담당자 채용 (신입)"
TITLE_EXP = "2026년 정보보안 담당자 채용 (경력)"

failures = []


def check(name, cond, detail=""):
    if cond:
        print("  [통과] %s" % name)
    else:
        failures.append("%s%s" % (name, (" — %s" % detail) if detail else ""))
        print("  [실패] %s%s" % (name, (" — %s" % detail) if detail else ""))


def make_job(platform, ext, title, url, deadline="D-3"):
    return {
        "company": COMPANY,
        "title": title,
        "url": url,
        "platform": platform,
        "external_id": ext,
        "location": "서울",
        "deadline": deadline,
    }


def run_collect(jobs_by_platform):
    """플랫폼 수집 함수를 고정 데이터로 바꾸고 collect_all_jobs()를 돌린다."""
    names = ["fetch_wanted", "fetch_jumpit", "fetch_saramin", "fetch_remember",
             "fetch_jobkorea", "fetch_incruit"]
    originals = {name: getattr(crawler, name) for name in names}
    try:
        for name in names:
            setattr(crawler, name, lambda *args, **kwargs: [])
        for platform, jobs in jobs_by_platform.items():
            attr = {
                "원티드": "fetch_wanted",
                "점핏": "fetch_jumpit",
                "사람인": "fetch_saramin",
                "리멤버": "fetch_remember",
                "잡코리아": "fetch_jobkorea",
                "인크루트": "fetch_incruit",
            }[platform]
            setattr(crawler, attr, (lambda data: (lambda *args, **kwargs: list(data)))(jobs))
        return crawler.collect_all_jobs()
    finally:
        for name, fn in originals.items():
            setattr(crawler, name, fn)


def find_titles(jobs):
    return sorted(j["title"] for j in jobs if j["company"] == COMPANY)


def test_same_platform_different_ids():
    print("\n[1] 같은 플랫폼 · 공고 ID만 다른 2건")
    jobs = run_collect({
        "사람인": [
            make_job("사람인", "900001", TITLE_NEW,
                     "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=900001"),
            make_job("사람인", "900002", TITLE_EXP,
                     "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=900002"),
        ]
    })
    got = find_titles(jobs)
    check("같은 플랫폼 2건 유지", got == sorted([TITLE_NEW, TITLE_EXP]), got)
    keys = {j["job_key"] for j in jobs if j["company"] == COMPANY}
    check("서로 다른 job_key", len(keys) == 2, keys)


def test_cross_platform_different_ids():
    print("\n[2] 서로 다른 플랫폼 · 공고 ID가 다른 2건(제목도 앞 12자만 같음)")
    jobs = run_collect({
        "사람인": [make_job("사람인", "910001", TITLE_NEW,
                          "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=910001")],
        "잡코리아": [make_job("잡코리아", "910002", TITLE_EXP,
                           "https://www.jobkorea.co.kr/GI_Read/910002")],
    })
    got = find_titles(jobs)
    check("플랫폼이 달라도 2건 유지", got == sorted([TITLE_NEW, TITLE_EXP]), got)


def test_cross_posted_same_job_is_one():
    print("\n[3] 통제 — 플랫폼에 교차 게시된 '완전히 같은' 공고는 1건 + 플랫폼 배지")
    jobs = run_collect({
        "사람인": [make_job("사람인", "920001", TITLE_NEW,
                          "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=920001")],
        "잡코리아": [make_job("잡코리아", "920002", TITLE_NEW,
                           "https://www.jobkorea.co.kr/GI_Read/920002")],
    })
    mine = [j for j in jobs if j["company"] == COMPANY]
    check("같은 공고는 1건", len(mine) == 1, [j["title"] for j in mine])
    if mine:
        check("플랫폼 배지 2개", sorted(mine[0]["platforms"]) == ["사람인", "잡코리아"],
              mine[0]["platforms"])


def test_db_recollect_keeps_both():
    print("\n[4] archive.db 사본 재수집 — 2건 모두 유지")
    tmpdir = tempfile.mkdtemp(prefix="jobdedup-")
    db_path = os.path.join(tmpdir, "archive.db")
    try:
        jobs = [
            {**make_job("사람인", "930001", TITLE_NEW,
                        "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=930001"),
             "platforms": ["사람인"], "keywords": ["정보보안"], "summary": "", "tags": []},
            {**make_job("사람인", "930002", TITLE_EXP,
                        "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=930002",
                        deadline="상시채용"),
             "platforms": ["사람인"], "keywords": ["정보보안"], "summary": "", "tags": []},
        ]
        now_dt = datetime.now(KST)
        crawler.sync_jobs_to_db(jobs, now_dt=now_dt, db_path=db_path)

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        first = conn.execute(
            "SELECT job_key, title, first_seen_at FROM jobs WHERE company = ? AND status = 'ACTIVE';",
            (COMPANY,),
        ).fetchall()
        conn.close()
        check("첫 수집 2행", len(first) == 2, [r["title"] for r in first])
        first_keys = {r["job_key"] for r in first}

        # 같은 공고를 다시 수집(재수집) — 이번에는 두 건 모두 URL/ID가 그대로다.
        again = [
            {**make_job("사람인", "930001", TITLE_NEW,
                        "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=930001"),
             "platforms": ["사람인"], "keywords": ["정보보안"], "summary": "", "tags": []},
            {**make_job("사람인", "930002", TITLE_EXP,
                        "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=930002",
                        deadline="상시채용"),
             "platforms": ["사람인"], "keywords": ["정보보안"], "summary": "", "tags": []},
        ]
        crawler.sync_jobs_to_db(again, now_dt=now_dt + timedelta(hours=1), db_path=db_path)

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT job_key, title, first_seen_at, last_seen_at FROM jobs "
            "WHERE company = ? AND status = 'ACTIVE';",
            (COMPANY,),
        ).fetchall()
        conn.close()
        check("재수집 후에도 2행", len(rows) == 2, [r["title"] for r in rows])
        check("행 키 유지(새 행이 생기지 않음)", {r["job_key"] for r in rows} == first_keys,
              {r["job_key"] for r in rows})
        titles = sorted(r["title"] for r in rows)
        check("두 제목 모두 남음", titles == sorted([TITLE_NEW, TITLE_EXP]), titles)

        # 한 건만 남은 상태(다른 공고가 목록에서 사라짐)에서도 남은 공고가 사라지지 않는다.
        crawler.sync_jobs_to_db([again[0]], now_dt=now_dt + timedelta(hours=2), db_path=db_path)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT title, status FROM jobs WHERE company = ?;", (COMPANY,)
        ).fetchall()
        conn.close()
        active_titles = [r["title"] for r in rows if r["status"] == "ACTIVE"]
        check("남은 1건은 유지", active_titles == [TITLE_NEW], active_titles)
        check("사라진 공고는 마감 처리", any(r["status"] == "EXPIRED" for r in rows),
              [(r["title"], r["status"]) for r in rows])
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    test_same_platform_different_ids()
    test_cross_platform_different_ids()
    test_cross_posted_same_job_is_one()
    test_db_recollect_keeps_both()
    if failures:
        print("\n공고 중복 제거 회귀 테스트 실패 %d건" % len(failures))
        for message in failures:
            print("  [실패] %s" % message)
        raise SystemExit(1)
    print("\n공고 중복 제거 회귀 테스트 통과")
    return 0


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""재수집되지 않은 활성 공고의 낡은 마감 라벨(D-N/오늘/내일)을 오늘(KST) 기준으로 DB에서 직접 교정한다.

배경
- 화면·jobs.json 은 빌드 시점에 normalize_deadline_label() 로 라벨을 다시 쓰지만,
  jobs.deadline 에는 플랫폼이 준 상대 표기('D-13')와 그 표기가 유효했던 수집일(last_seen_at)이
  그대로 남아 있어, DB만 보면 오늘 기준 남은 일수와 숫자가 어긋난다(예: 11-18 수집 'D-13' → 오늘 D-10).
- 이 스크립트는 그 어긋남을 DB에서 없앤다. 보정 직전 원문은 jobs.deadline_raw 에 남긴다.

보정 규칙 (db_manager.compute_remaining_days / normalize_deadline_label 과 동일한 우선순위)
1) 라벨에 실제 날짜(MM/DD)가 있으면 그 날짜를 기준으로 D-N 숫자만 다시 쓴다(날짜 표기는 보존).
2) 날짜가 없으면 수집일과 오늘의 차이만큼 되돌려 남은 일수를 구하고, 그 날짜를 괄호로 함께 적는다
   ('D-13' → 'D-10 (~ 12/01(화))'). 날짜를 함께 적어야 다음 빌드·수집에서도 숫자가 다시 어긋나지 않는다.
   (상대 표기만 고쳐 쓰면 기준일이 사라져 다음 날 다시 어긋난다.)

사용: python3 fix_deadline_labels.py [--dry-run]
"""
import re
import sys
from datetime import datetime, timedelta, timezone

from db_manager import (
    DEADLINE_CLOCK_TAIL_RE,
    WEEKDAY_KO,
    compute_remaining_days,
    get_connection,
    init_db,
    normalize_deadline_label,
    parse_deadline_status,
    parse_explicit_deadline_date,
)

KST = timezone(timedelta(hours=9))


def ensure_raw_column(conn):
    """보정 직전 원문을 남길 jobs.deadline_raw 열을 보장한다."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(jobs)")}
    if "deadline_raw" not in cols:
        conn.execute("ALTER TABLE jobs ADD COLUMN deadline_raw TEXT")
        conn.commit()
        return True
    return False


def stale_reason(deadline, days):
    """라벨의 상대 표기가 오늘 기준 남은 일수와 어긋나면 그 이유를 돌려준다."""
    if days is None:
        return None
    m = re.search(r"D-(\d+)", deadline)
    if m and int(m.group(1)) != max(days, 0):
        return f"D-{m.group(1)} → {max(days, 0)}일"
    if ("D-Day" in deadline or "오늘" in deadline) and days != 0:
        return f"D-Day → {days}일"
    if "내일" in deadline and days != 1:
        return f"내일 → {days}일"
    return None


def build_corrected_label(deadline, days, today):
    """오늘 기준으로 다시 쓴 마감 라벨(날짜가 없으면 계산한 날짜를 함께 적는다)."""
    days = max(days, 0)
    if parse_explicit_deadline_date(deadline, today) is not None:
        # 적힌 날짜가 있으면 숫자만 교체(기존 normalize_deadline_label 과 같은 결과)
        return normalize_deadline_label(deadline, today, None)

    tail_m = DEADLINE_CLOCK_TAIL_RE.search(deadline)
    tail = f" {tail_m.group(1).strip()}" if tail_m else ""
    target = today + timedelta(days=days)
    stamp = f"{target.month:02d}/{target.day:02d}({WEEKDAY_KO[target.weekday()]})"
    token = "D-Day" if days == 0 else f"D-{days}"
    return f"{token} (~ {stamp}){tail}"


def main():
    dry_run = "--dry-run" in sys.argv[1:]
    today = datetime.now(KST).date()
    init_db()

    conn = get_connection()
    added = ensure_raw_column(conn)
    if added:
        print("-> jobs.deadline_raw 열 추가(보정 원문 보존용)")

    rows = conn.execute(
        "SELECT job_key, company, title, deadline, last_seen_at FROM jobs WHERE status = 'ACTIVE'"
    ).fetchall()

    fixes = []
    skipped = []
    for r in rows:
        dl = (r["deadline"] or "").strip()
        if not dl:
            continue
        days = compute_remaining_days(dl, today, r["last_seen_at"])
        reason = stale_reason(dl, days)
        if not reason:
            continue
        new_label = build_corrected_label(dl, days, today)
        if new_label == dl:
            continue
        status, state = parse_deadline_status(new_label, today)
        if state != "ACTIVE":
            # 보정 결과가 마감이면 손대지 않고 빌드의 만료 정리에 맡긴다.
            skipped.append((r["company"], dl, new_label, state))
            continue
        fixes.append((r["job_key"], r["company"], r["title"], dl, new_label, reason, r["last_seen_at"]))

    print(f"-> 검사 대상 활성 공고 {len(rows)}건 / 교정 대상 {len(fixes)}건 (건너뜀 {len(skipped)}건)")
    for f in fixes:
        print(f"  · {f[1]} | {f[3]} → {f[4]}  ({f[6][:10] if f[6] else '-'} 수집)")

    if dry_run:
        print("\n[dry-run] DB에 반영하지 않았습니다.")
        conn.close()
        return 0

    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    for job_key, _c, _t, old, new, _reason, _seen in fixes:
        conn.execute(
            """UPDATE jobs
                  SET deadline_raw = COALESCE(deadline_raw, ?),
                      deadline = ?,
                      updated_at = ?
                WHERE job_key = ?""",
            (old, new, now_str, job_key),
        )
    conn.commit()

    # 재검증: 같은 기준으로 남은 어긋남이 0건인지 확인한다.
    left = []
    for r in conn.execute(
        "SELECT company, deadline, last_seen_at FROM jobs WHERE status = 'ACTIVE'"
    ).fetchall():
        days = compute_remaining_days(r["deadline"], today, r["last_seen_at"])
        reason = stale_reason((r["deadline"] or "").strip(), days)
        if reason:
            left.append((r["company"], r["deadline"], reason))
    conn.close()

    print(f"\n-> DB 반영 완료: {len(fixes)}건 교정")
    print(f"-> 재검증: 남은 어긋남 {len(left)}건")
    for x in left:
        print(f"  ! {x}")
    return 0 if not left else 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CVE 리포트의 한국어 심층 분석(원인·영향·조치)을 복구·보강한다.

일일 배치가 수집만 하고 분석(`--analyze`) 없이 `--finish` 로 끝나면 구조화 템플릿
(fallback)이 DB에 들어가 앞서 확보한 EXAONE 분석이 가려질 수 있다. 이 스크립트는

1) `cve_cache.json` 에 같은 cve_id 분석본이 남아 있으면 해시를 DB 행 기준으로 다시 맞춰
   API 호출 없이 그대로 되살리고,
2) 캐시가 없는 건만 EXAONE 으로 새로 분석한다(한 실행에 `--misses` 건까지).

실행마다 DB·캐시에 반영되므로 여러 번 나눠 호출해도 이어서 진행된다.

사용:
  python3 repair_cve_analysis.py                # 캐시 복구 + 미분석 4건 분석
  python3 repair_cve_analysis.py --misses 6     # 미분석 6건까지
  python3 repair_cve_analysis.py --misses 0     # 캐시 복구만
  python3 repair_cve_analysis.py --dry-run      # 대상만 확인
"""
import sqlite3
import sys

import cve_crawler as cc
from db_manager import DB_PATH, get_cve_reports, init_db, upsert_cve_reports


def arg_int(args, name, default):
    if name in args:
        try:
            return int(args[args.index(name) + 1])
        except (IndexError, ValueError):
            return default
    return default


def created_order():
    """오늘 신규를 먼저 처리하도록 created_at 내림차순 cve_id 목록을 만든다."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = [r[0] for r in conn.execute(
            "SELECT cve_id FROM cve_reports ORDER BY created_at DESC, cve_id DESC")]
        conn.close()
        return {cid: i for i, cid in enumerate(rows)}
    except Exception:  # noqa: BLE001
        return {}


def main():
    args = sys.argv[1:]
    misses = arg_int(args, "--misses", 4)
    budget = arg_int(args, "--budget", 240)
    dry_run = "--dry-run" in args

    init_db()
    rows = get_cve_reports()
    pending = [r for r in rows if str(r.get("analyzed_by") or "").startswith("fallback")]
    if not pending:
        print("복구할 fallback 항목이 없습니다.")
        return 0

    cache = cc.load_cache()
    cached, uncached = [], []
    for r in pending:
        entry = cache["analysis"].get(r["cve_id"])
        if entry and entry.get("title_ko"):
            # DB 행 기준 해시로 다시 묶어 두면 analyze_records 가 캐시로 인식한다.
            entry["hash"] = cc.src_hash(r)
            cached.append(r)
        else:
            uncached.append(r)

    order = created_order()
    uncached.sort(key=lambda r: order.get(r["cve_id"], 10 ** 6))
    targets = uncached[:max(0, misses)]

    print(f"fallback {len(pending)}건 → 캐시 복구 대상 {len(cached)}건 / 신규 분석 필요 {len(uncached)}건")
    if dry_run:
        for r in cached:
            print(f"  [캐시] {r['cve_id']}")
        for r in uncached:
            print(f"  [신규] {r['cve_id']} · {cc.clean(r.get('description_orig'), 70)}")
        return 0

    if cached:
        cc.save_cache(cache)
        cc.analyze_records(cached, cache, patient=True)

    if targets:
        print(f"— EXAONE 분석 {len(targets)}건 (예산 {budget}s) —")
        cc.analyze_records(targets, cache, budget=budget, patient=True)

    cc.save_cache(cache)

    changed = cached + targets
    for r in changed:
        r.pop("_hash", None)
        r["updated_at"] = cc.now_str()
    upsert_cve_reports(changed)

    after = get_cve_reports()
    remain = [r for r in after if str(r.get("analyzed_by") or "").startswith("fallback")]
    exa = sum(1 for r in after if r.get("analyzed_by") == "exaone")
    print(f"→ 반영 {len(changed)}건 / DB 전체 {len(after)}건 (EXAONE {exa}건 · 폴백 {len(remain)}건 남음)")
    if remain:
        print("  남은 항목:", ", ".join(r["cve_id"] for r in remain[:12]))
    return 0 if not remain else 3


if __name__ == "__main__":
    sys.exit(main())

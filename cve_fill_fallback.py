# -*- coding: utf-8 -*-
"""DB에 이미 적재된 CVE 중 EXAONE 폴백(영문 요약 템플릿) 항목만 골라 한국어 분석을 채운다.

- `cve_crawler.py --ai-only` 는 전체 레코드를 대상으로 해 오래 걸리므로, 폴백 항목만 추려 4건 단위로
  분석→DB 적재를 반복한다(중간에 끊겨도 처리분이 남는다).
- 우선순위: 제품명이 비어 있던 자리표시 항목 → 최근 공개(published_at) 순.
- 성공분은 cve_cache.json 에 적립되어 다음 실행에서 건너뛴다.

사용: CVE_AI_TIME_BUDGET=240 python3 cve_fill_fallback.py
"""
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import cve_crawler as cc  # noqa: E402
from db_manager import get_cve_reports, upsert_cve_reports  # noqa: E402

CHUNK = 4


def priority(rec):
    placeholder = 0 if not (rec.get("product") or "").strip() else 1
    published = rec.get("published_at") or ""
    # 최근 공개 우선(문자열 비교로 충분: YYYY-MM-DD)
    return (placeholder, tuple(-ord(ch) for ch in published) if published else ())


def main():
    cc.init_db()
    budget = int(os.environ.get("CVE_AI_TIME_BUDGET") or 240)
    started = time.time()
    records = [r for r in get_cve_reports() if (r.get("analyzed_by") or "").startswith("fallback")]
    if not records:
        print("폴백 항목이 없습니다.")
        return 0
    records.sort(key=lambda r: (priority(r)[0], r.get("published_at") or "", r.get("cve_id")))
    # 제품명 없는 항목 먼저, 그 다음 최신 공개 순
    records.sort(key=lambda r: (0 if "영향 제품" in (r.get("title_ko") or "") else 1,
                                0 if not (r.get("product") or "").strip() else 1,
                                -int((r.get("published_at") or "2020-01-01").replace("-", "")[:8] or 0)))
    print(f"-> 폴백 {len(records)}건 한국어 분석 시작 (예산 {budget}s, 제품 미상 "
          f"{sum(1 for r in records if not (r.get('product') or '').strip())}건)")

    cache = cc.load_cache()
    done_total = 0
    for start in range(0, len(records), CHUNK):
        if time.time() - started > budget:
            print(f"  [중단] 예산 소진 — 남은 {len(records) - start}건은 다음 실행으로")
            break
        chunk = records[start:start + CHUNK]
        cc.analyze_records(chunk, cache, ai_limit=None, budget=90, patient=True)
        cc.save_cache(cache)
        cc.apply_curated(chunk)
        for r in chunk:
            r.pop("_hash", None)
        upsert_cve_reports(chunk)
        done_total += sum(1 for r in chunk if r.get("analyzed_by") == "exaone")
        print(f"  [{min(start + CHUNK, len(records))}/{len(records)}] EXAONE 누적 {done_total}건")

    print(f"-> 이번 실행 EXAONE {done_total}건 반영")
    return 0


if __name__ == "__main__":
    sys.exit(main())

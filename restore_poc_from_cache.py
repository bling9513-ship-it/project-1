#!/usr/bin/env python3
"""cve_cache.json 의 PoC 캐시를 archive.db `cve_reports` 로 복구한다.

2026-11-18 회귀: POC_QUERY_LIMIT 밖 항목·GitHub 조회 실패 항목이
poc_count=0 / poc_links_json=[] 로 upsert 되면서 공개 PoC 21건이 1건으로 줄었다.
이 스크립트는 캐시에 남아 있는 링크를 DB 기존 값과 합집합(URL 기준 중복 제거)으로
병합해 되살린다. 다른 컬럼은 건드리지 않는다.

사용:
  python3 restore_poc_from_cache.py            # 미리보기
  python3 restore_poc_from_cache.py --apply    # 실제 반영
"""
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "archive.db")
CACHE_FILE = os.path.join(HERE, "cve_cache.json")


def load_cached_pocs():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    poc = data.get("poc") or {}
    return {cid: (v.get("links") or []) for cid, v in poc.items() if (v.get("links") or [])}


def key_of(link):
    return link.get("url") if isinstance(link, dict) else link


def main():
    apply = "--apply" in sys.argv
    cached = load_cached_pocs()
    if not cached:
        print("캐시에 PoC 링크가 없습니다.")
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = {r["cve_id"]: r for r in cur.execute(
        "SELECT cve_id, poc_count, poc_links_json FROM cve_reports")}

    changed = []
    missing = []
    for cve_id, links in sorted(cached.items()):
        row = rows.get(cve_id)
        if row is None:
            missing.append(cve_id)
            continue
        try:
            existing = json.loads(row["poc_links_json"]) if row["poc_links_json"] else []
        except (TypeError, ValueError):
            existing = []
        merged = list(existing)
        seen = {key_of(l) for l in merged}
        added = 0
        for link in links:
            k = key_of(link)
            if k and k not in seen:
                merged.append(link)
                seen.add(k)
                added += 1
        if added:
            changed.append((cve_id, row["poc_count"] or 0, len(merged), added))
            if apply:
                cur.execute(
                    "UPDATE cve_reports SET poc_count = ?, poc_links_json = ? WHERE cve_id = ?",
                    (len(merged), json.dumps(merged, ensure_ascii=False), cve_id),
                )

    if apply:
        conn.commit()

    print(f"{'[적용]' if apply else '[미리보기]'} 캐시 PoC {len(cached)}개 CVE / "
          f"복구 대상 {len(changed)}건 / DB에 없는 CVE {len(missing)}건")
    for cve_id, before, after, added in changed[:40]:
        print(f"  {cve_id}: {before} → {after} (+{added})")
    if missing:
        print("  DB에 없는 CVE: " + ", ".join(missing))
    if apply:
        n = cur.execute("SELECT COUNT(*) FROM cve_reports WHERE poc_count > 0").fetchone()[0]
        s = cur.execute("SELECT SUM(poc_count) FROM cve_reports").fetchone()[0] or 0
        print(f"  → PoC 보유 CVE {n}건 / 링크 {s}개")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

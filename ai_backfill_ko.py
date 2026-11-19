# -*- coding: utf-8 -*-
"""ai_insights 에서 한국어 제목이 없는(EXAONE 폴백으로 영문 원문이 노출되는) 항목을 보강한다.

- DB에 이미 적재된 항목을 대상으로 한다(재수집 없음).
- 원문 요약(summary_orig)은 ai_run_items.json → ai_tech_cache.json → 수집 URL 순으로 확보한다.
  (arXiv는 abstract 본문, 일반 페이지는 meta description을 쓴다.)
- EXAONE 1회 호출당 3건, 429/5xx는 짧은 백오프로 재시도한다.
- 성공분은 archive.db(ai_insights)와 ai_tech_cache.json 에 함께 반영한다.

사용: python3 ai_backfill_ko.py [--limit N] [--dry-run]
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

import ai_news_crawler as an
from db_manager import get_connection, init_db, upsert_ai_insights

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KO_RE = re.compile(r"[\uac00-\ud7a3]")
UA = "Mozilla/5.0 (compatible; infosec-archive/1.0)"


def has_korean(text):
    return bool(KO_RE.search(text or ""))


def fetch_source_text(url, timeout=20):
    """수집 URL에서 원문 요약에 쓸 짧은 텍스트를 가져온다. 실패하면 빈 문자열."""
    if not url:
        return ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        return ""

    m = re.search(r'<blockquote class="abstract[^>]*>(.*?)</blockquote>', raw, re.S)
    if m:
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        return re.sub(r"\s+", " ", text).strip()[:1200]

    for pat in (
        r'<meta[^>]+(?:name|property)=["\'](?:og:description|description)["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\'](?:og:description|description)["\']',
    ):
        m = re.search(pat, raw)
        if m:
            return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()[:1200]

    text = html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:1200]


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return {}


def collect_targets(limit=None):
    """한국어 제목이 없는 ai_insights 행을 (원문 요약 포함) 분석 입력 형태로 만든다."""
    run_items = load_json(os.path.join(BASE_DIR, "ai_run_items.json"))
    if isinstance(run_items, dict):
        run_items = []
    run_by_key = {it.get("item_key"): it for it in run_items if isinstance(it, dict)}

    init_db()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT item_key, source, title_orig, title_ko, url, category, summary, tech_insight,
               tags, is_featured, published_at, score, analyzed_by, collected_at
        FROM ai_insights
        ORDER BY id ASC
        """
    ).fetchall()
    conn.close()

    targets = []
    for r in rows:
        if has_korean(r["title_ko"]):
            continue
        item = {
            "item_key": r["item_key"],
            "source": r["source"],
            "title_orig": r["title_orig"],
            "published_at": r["published_at"] or "",
            "score": r["score"] or 0,
            "source_hint": "",
            "track": None,
            "category": r["category"],
            "_db": dict(r),
        }
        src = (run_by_key.get(r["item_key"]) or {}).get("summary_orig") or ""
        if not src:
            src = fetch_source_text(r["url"])
        if not src:
            src = r["title_orig"]
        item["summary_orig"] = src
        targets.append(item)

    if limit:
        targets = targets[: int(limit)]
    return targets


def analyze_chunk(chunk, api_key, max_attempt=6):
    """한 배치를 EXAONE으로 분석. 429/5xx는 백오프 재시도."""
    prompt = an.build_prompt(chunk)
    max_tokens = min(8192, 1500 * len(chunk) + 800)
    for attempt in range(max_attempt):
        try:
            content = an.call_exaone(prompt, api_key, max_tokens=max_tokens, timeout=180)
            if not (content or "").strip():
                raise RuntimeError("빈 응답")
            return an.parse_json_array(content) or []
        except urllib.error.HTTPError as e:
            code = e.code
            if code in (401, 403):
                print(f"  [API] HTTP {code} 키 인증 실패 → 중단")
                return None
            wait = min(45, 4 * (2 ** attempt)) if code == 429 else min(40, 5 * (attempt + 1))
            print(f"  [API] HTTP {code} (시도 {attempt + 1}/{max_attempt}) → {wait}초 후 재시도")
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001
            wait = 3 * (attempt + 1)
            print(f"  [API] {type(e).__name__}: {e} (시도 {attempt + 1}/{max_attempt}) → {wait}초 후 재시도")
            time.sleep(wait)
    return []


def main():
    args = sys.argv[1:]
    limit = None
    if "--limit" in args:
        try:
            limit = int(args[args.index("--limit") + 1])
        except (IndexError, ValueError):
            limit = None
    dry_run = "--dry-run" in args

    api_key = an.get_api_key()
    if not api_key and not dry_run:
        print("EXAONE_API_KEY 가 없습니다. .env 또는 환경변수를 확인하세요.")
        return 1

    targets = collect_targets(limit)
    print(f"-> 한국어 제목 없는 항목 {len(targets)}건 (원문 요약 확보 {sum(1 for t in targets if len(t['summary_orig']) > 80)}건)")
    if dry_run:
        for t in targets:
            print(f"  - [{t['source']}] {t['title_orig'][:70]} / 원문 {len(t['summary_orig'])}자")
        return 0

    tech_cache = load_json(an.CACHE_FILE) if isinstance(load_json(an.CACHE_FILE), dict) else {}
    done_items = []
    failed = []
    saved = 0

    BATCH = 3
    for start in range(0, len(targets), BATCH):
        chunk = targets[start:start + BATCH]
        results = analyze_chunk(chunk, api_key)
        if results is None:
            break
        by_id = {}
        for r in results:
            if isinstance(r, dict):
                try:
                    by_id[int(r.get("id", 0))] = r
                except (TypeError, ValueError):
                    continue
        for i, it in enumerate(chunk, 1):
            res = by_id.get(i)
            if not res:
                failed.append(it["title_orig"])
                continue
            a = an.normalize_analysis(res, it)
            if not has_korean(a.get("title_ko")):
                failed.append(it["title_orig"])
                continue
            row = dict(it["_db"])
            row.update({
                "title_ko": a["title_ko"],
                "category": a["category"],
                "summary": a["summary"],
                "tech_insight": a["tech_insight"],
                "tags": a["tags"],
                "is_featured": a["is_featured"],
                "analyzed_by": "exaone",
            })
            done_items.append(row)
            tech_cache[it["item_key"]] = {
                "title_ko": a["title_ko"],
                "category": a["category"],
                "summary": a["summary"],
                "tech_insight": a["tech_insight"],
                "tags": a["tags"],
                "is_featured": a["is_featured"],
            }
            print(f"  [{start + i}/{len(targets)}] {a['title_ko']}")

        # 배치마다 즉시 반영한다(오래 걸려 중단되어도 처리분은 남도록).
        if done_items:
            upsert_ai_insights(done_items)
            saved += len(done_items)
            done_items = []
            tmp = an.CACHE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(tech_cache, f, ensure_ascii=False, indent=2)
            os.replace(tmp, an.CACHE_FILE)
        time.sleep(1.5)
    print(f"\n-> 보강 완료 {saved}건 / 실패·미처리 {len(failed)}건")
    for t in failed:
        print(f"  ! {t[:90]}")
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())

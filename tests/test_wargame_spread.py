#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""워게임(wargame.html) 정적 4지선다 정답 위치 분산 검증.

- 정적 14문항의 정답이 A(0)에 몰리지 않고 0~3 에 고르게 퍼졌는지
- 회전 뒤에도 '정답 보기 텍스트'가 원본과 같은지(카드 HTML에서 직접 확인)
- 데일리 자동 출제(daily-*)는 건드리지 않았는지(DB 값과 비교)

실행: python3 tests/test_wargame_spread.py
"""
import html
import json
import os
import re
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from build_wargame_html import QUESTIONS  # noqa: E402

WARGAME_HTML = os.path.join(BASE_DIR, "wargame.html")
DB_PATH = os.path.join(BASE_DIR, "archive.db")
failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_payload():
    src = open(WARGAME_HTML, encoding="utf-8").read()
    marker = "const DATA = "
    start = src.index(marker) + len(marker)
    data, _ = json.JSONDecoder().raw_decode(src[start:])
    return src, data


def card_options(src, qid):
    m = re.search(r'<article class="q-card" id="q-%s".*?</article>' % re.escape(qid), src, re.S)
    if not m:
        return None
    options = {}
    for idx, text in re.findall(
            r'<button class="opt" type="button" data-idx="(\d)">'
            r'<span class="opt-key">[A-D]</span><span class="opt-text">(.*?)</span></button>',
            m.group(0), re.S):
        options[int(idx)] = html.unescape(text)
    return options


def main():
    src, payload = load_payload()
    static_ids = {q["id"] for q in QUESTIONS}
    source = {q["id"]: q for q in QUESTIONS}

    static = [item for item in payload if item["id"] in static_ids and item["type"] == "choice"]
    daily = [item for item in payload if str(item["id"]).startswith("daily-")]
    check("정적 4지선다 14문항", len(static) == 14, len(static))
    check("정적 문항은 모두 4지선다", all(item["type"] == "choice" for item in static))

    answers = [item["answer"] for item in static]
    counts = {i: answers.count(i) for i in range(4)}
    check("정답이 A(0)에 몰리지 않음", counts[0] < len(static), counts)
    check("정답 4곳 모두 사용", set(answers) == {0, 1, 2, 3}, counts)
    check("정답 위치 고른 분포(각 3문항 이상)", all(v >= 3 for v in counts.values()), counts)
    check("i % 4 순환", answers == [i % 4 for i in range(len(static))], answers)

    for item in static:
        qid = item["id"]
        idx = item["answer"]
        check("%s: 정답 위치 범위" % qid, 0 <= idx <= 3, idx)
        check("%s: sample 문자 일치" % qid, item["sample"] == "ABCD"[idx], item["sample"])
        options = card_options(src, qid)
        check("%s: 카드 보기 4개" % qid, options is not None and len(options) == 4)
        if not options:
            continue
        expected = source[qid]["choices"][source[qid]["answer"]]
        check("%s: 정답 보기 텍스트 유지" % qid, options.get(idx) == expected,
              "%r != %r" % (options.get(idx), expected))
        check("%s: 보기 문구 집합 유지" % qid,
              sorted(options.values()) == sorted(source[qid]["choices"]))

    # 데일리 문제는 회전 대상이 아니다(DB 값 그대로)
    if os.path.exists(DB_PATH) and daily:
        conn = sqlite3.connect(DB_PATH)
        try:
            for item in daily:
                row = conn.execute(
                    "SELECT answer_idx, choices_json FROM wargame_questions WHERE id = ?", (item["id"],)
                ).fetchone()
                if not row:
                    continue
                check("%s: 데일리 정답 위치 유지" % item["id"], row[0] == item["answer"],
                      "%s != %s" % (row[0], item["answer"]))
                choices = json.loads(row[1])
                check("%s: 데일리 정답 보기 텍스트 유지" % item["id"],
                      choices[row[0]] == choices[item["answer"]])
        finally:
            conn.close()

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("정적 4지선다 정답 분산 검증 통과: %s (총 %d문항 · 데일리 %d문항 유지)"
          % ("/".join(str(counts[i]) for i in range(4)), len(static), len(daily)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""90초 생활 추리(mystery90.html) 사건·화면 검증.

확인하는 것
  · 사건 데이터
      - 10건 이상 · ID 중복 없음 · 유형(order/pick) · 단계 4~5개 · 힌트/해설 있음
      - pick 유형은 보기 4개가 서로 다르고 정답 인덱스가 범위 안
  · 화면에 보여 줄 순서
      - display 가 정답 위치의 순열이고, 정답 순서와 똑같이 두지 않음
      - 같은 사건이면 항상 같은 순서(빌드 재현성)
      - pick 보기는 섞인 뒤 정답 인덱스가 정답 문구를 가리킴
  · 오늘의 사건
      - 날짜만으로 결정 · 14일 동안 14건이 모두 다른 사건
  · mystery90.html
      - data-page="mystery90" · 전체 메뉴 29페이지 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 사건 14건 임베드 · 제한 90초 · 스트릭 저장 키 · 가이드 재생 키 · 결과/힌트 요소

실행: python3 tests/test_mystery90_puzzles.py
"""
import json
import os
import re
import sys
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_mystery90_html as m9
from mystery90_data import CASES

HTML = os.path.join(BASE_DIR, "mystery90.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 29

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def check_data():
    print("== 사건 데이터 ==")
    check("사건 10건 이상", len(CASES) >= 10, len(CASES))
    ids = [case["id"] for case in CASES]
    check("ID 중복 없음", len(ids) == len(set(ids)))
    m9.validate()
    for case in CASES:
        steps = case["steps"]
        check("%s 단계 4~5" % case["id"], 4 <= len(steps) <= 5, len(steps))
        check("%s 힌트" % case["id"], bool(case["hint"]))
        check("%s 해설" % case["id"], bool(case["explain"]))
        for step in steps:
            check("%s 카드 그림" % case["id"], step["visual"] in m9.__dict__.get("VISUALS", []) or
                  step["visual"] in __import__("mystery90_data").VISUALS, step["visual"])
            check("%s 카드 문구" % case["id"], bool(step["text"]) and bool(step["tag"]))
        if case["type"] == "pick":
            check("%s 보기 4개" % case["id"], len(case["choices"]) == 4)
            check("%s 보기 중복 없음" % case["id"], len(set(case["choices"])) == 4)
            check("%s 정답 범위" % case["id"], 0 <= case["answer"] < 4)
            check("%s 질문" % case["id"], bool(case.get("question")))
    types = {case["type"] for case in CASES}
    check("두 유형 모두 있음", types == {"order", "pick"}, types)
    print("  사건 %d건 · 유형 %s" % (len(CASES), sorted(types)))


def check_shuffle():
    print("== 화면 순서 ==")
    for case in CASES:
        count = len(case["steps"])
        display = m9.shuffled_positions(case["id"], count)
        check("%s 순열" % case["id"], sorted(display) == list(range(count)), display)
        check("%s 정답 순서와 다름" % case["id"], display != list(range(count)), display)
        again = m9.shuffled_positions(case["id"], count)
        check("%s 재현성" % case["id"], display == again)
    pick = next(case for case in CASES if case["type"] == "pick")
    choices, answer = m9.shuffled_choices(pick["id"], pick["choices"], pick["answer"])
    check("pick 보기 수 유지", len(choices) == len(pick["choices"]))
    check("pick 정답 문구 유지", choices[answer] == pick["choices"][pick["answer"]],
          (choices[answer], pick["choices"][pick["answer"]]))
    check("pick 보기 순서 섞임", choices != list(pick["choices"]), choices)
    print("  순서·보기 섞기 확인")


def check_daily():
    print("== 오늘의 사건 ==")
    day = date(2026, 11, 24)
    first = m9.daily_case_id(day)
    check("같은 날 같은 사건", m9.daily_case_id(day) == first, first)
    days = [m9.daily_case_id(day + timedelta(days=offset)) for offset in range(14)]
    check("14일 모두 다른 사건", len(set(days)) == 14, len(set(days)))
    check("오늘 사건이 목록 안", first in {case["id"] for case in CASES}, first)
    print("  2026-11-24 → %s · 14일 순환" % first)


def check_html():
    print("== mystery90.html ==")
    html = read(HTML)
    check("data-page", 'data-page="mystery90"' in html)
    check("이모지 0", not EMOJI_RE.search(html), EMOJI_RE.findall(html)[:3])
    check("그라데이션 0", "linear-gradient" not in html and "radial-gradient" not in html)
    check("인라인 핸들러 0", not re.search(r'\son(click|load|change|input|submit|keydown)=', html, re.I))
    check("전체 메뉴 29페이지", html.count('class="ia-sheet-link') - html.count('class="ia-sheet-links"') == SHEET_PAGES,
          html.count('class="ia-sheet-link') - html.count('class="ia-sheet-links"'))
    check("제한 90초", '"limit":90' in html, "limit")
    check("스트릭 저장 키", m9.STORE_KEY in html)
    check("가이드 재생 키", m9.GUIDE_KEY in html)
    for element in ("m9Cards", "m9Tray", "m9Submit", "m9Hint", "m9Timer", "m9Result", "m9Share", "m9Start"):
        check("요소 %s" % element, 'id="%s"' % element in html)
    check("가이드 3단계", html.count('class="m9-frame"') == 3, html.count('class="m9-frame"'))
    check("reduced-motion 존중", "prefers-reduced-motion" in html)
    payload = json.loads(re.search(r'<script type="application/json" id="m9Data">(.*?)</script>', html, re.S).group(1))
    check("임베드 사건 수", len(payload["cases"]) == len(CASES), len(payload["cases"]))
    case = payload["cases"][0]
    check("임베드 순서", case["display"] == m9.shuffled_positions(case["id"], len(case["steps"])), case["display"])
    pick = next(item for item in payload["cases"] if item["type"] == "pick")
    check("임베드 pick 정답", pick["choices"][pick["answer"]] ==
          next(c["choices"][c["answer"]] for c in CASES if c["id"] == pick["id"]))
    check("오늘의 사건 표시", payload["daily"] == m9.daily_case_id(date(2026, 11, 24)) or
          payload["daily"] in {item["id"] for item in payload["cases"]}, payload["daily"])
    print("  페이지 확인 · 사건 %d건 임베드" % len(payload["cases"]))


def main():
    check_data()
    check_shuffle()
    check_daily()
    check_html()
    if failures:
        print("\n실패 %d건: %s" % (len(failures), failures))
        sys.exit(1)
    print("\n90초 생활 추리 검증 통과 (사건 %d건 · 전체 메뉴 %d페이지)" % (len(CASES), SHEET_PAGES))


if __name__ == "__main__":
    main()

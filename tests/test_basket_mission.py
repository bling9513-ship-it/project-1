#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘의 장바구니 리그(basket.html) 미션·채점 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · grocery_data.json 연동
      - 8품목 · 서울 소매가격 최신값 존재 · 카드에 실린 가격이 JSON 최신값과 같은지(가격 조작 금지)
  · 오늘의 미션
      - 날짜만으로 결정(같은 날 같은 미션) · 예산/최소 품목이 정의된 목록 안 · 조건 2개가 서로 다름
      - 60일치 미션이 모두 "달성 가능"한지(최고 조합이 A등급 이상)
  · 채점
      - 예산 정확도 점수 경계(1,000 / 2,000 / 4,000원)
      - 조건 미충족·최소 품목 미달 감점
      - 최고 조합이 실제로 가장 높은 점수인지(완전탐색 재검증)
  · basket.html
      - data-page="basket" · 26페이지 셸 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 8품목 카드 · 미니 바 · 스트릭 저장 키 · 결과 복사 · 임베드 JSON == grocery_data.json 가격

실행: python3 tests/test_basket_mission.py
"""
import itertools
import json
import os
import re
import sys
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_basket_html as bk
import ui_shell

HTML = os.path.join(BASE_DIR, "basket.html")
DATA = os.path.join(BASE_DIR, "grocery_data.json")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 31

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def check_data(data):
    print("== 데이터 ==")
    check("품목 8개", len(data["items"]) == 8, len(data["items"]))
    region = data["regionList"][0]
    check("첫 지역 서울", region["name"] == "서울", region["name"])
    for item in data["items"]:
        stats = item["byRegion"][region["id"]]
        check("%s 최신가" % item["name"], stats["latest"]["price"] > 0, stats["latest"]["price"])
        check("%s 분류" % item["name"], item["id"] in bk.CATEGORY, item["id"])
        check("%s 규격" % item["name"], bool(item["unit"]), item["unit"])
    check("출처 KAMIS", "kamis" in data["source"]["url"], data["source"]["url"])


def check_mission(data):
    print("== 미션 ==")
    day = date(2026, 11, 24)
    first = bk.mission_for(day)
    check("같은 날 같은 미션", bk.mission_for(day) == first)
    check("예산이 목록 안", first["budget"] in bk.BUDGETS, first["budget"])
    check("허용 오차 1,000원", first["tolerance"] == 1000, first["tolerance"])
    check("최소 품목 4~5", first["minItems"] in (4, 5), first["minItems"])
    check("조건 2개", len(first["conditions"]) == 2, len(first["conditions"]))
    check("조건 서로 다름", first["conditions"][0]["id"] != first["conditions"][1]["id"],
          [condition["id"] for condition in first["conditions"]])
    check("조건 문구 있음", all(condition["label"] for condition in first["conditions"]))
    days = [bk.mission_for(day + timedelta(days=offset)) for offset in range(14)]
    check("14일 안에 예산 다양", len({mission["budget"] for mission in days}) >= 5,
          sorted({mission["budget"] for mission in days}))
    check("14일 안에 조건 다양", len({tuple(c["id"] for c in mission["conditions"]) for mission in days}) >= 6,
          len({tuple(c["id"] for c in mission["conditions"]) for mission in days}))

    print("== 달성 가능성 (60일) ==")
    weak = []
    for offset in range(60):
        mission = bk.mission_for(day + timedelta(days=offset))
        best = bk.best_combination(mission, data)
        if best["grade"] not in ("S", "A"):
            weak.append((mission["date"], best["grade"], best["total"], mission["budget"]))
    check("60일 미션 모두 A 이상 달성 가능", not weak, weak[:3])


def check_grading(data):
    print("== 채점 ==")
    mission = {"date": "2026-11-24", "seed": 0, "budget": 23000, "tolerance": 1000, "minItems": 4,
               "conditions": [{"id": "fruit", "label": "과일 1가지 담기"},
                              {"id": "leaf", "label": "잎채소 1가지 이상 담기"}]}
    prices = {item["id"]: bk.price_of(data, item["id"]) for item in data["items"]}
    # 사과 1 + 시금치 1 + 양파 1 + 애호박 1 — 소매가격은 매일 갱신되므로 JSON 최신값에서 계산한다
    picks = {"apple": 1, "spinach": 1, "onion": 1, "zucchini": 1}
    total = sum(prices[key] * qty for key, qty in picks.items())
    latest = {item["id"]: item["byRegion"][data["regionList"][0]["id"]]["latest"]["price"]
              for item in data["items"]}
    check("합계 계산", total == sum(latest[key] for key in picks) and total > 0,
          (total, sum(latest[key] for key in picks)))
    result = bk.evaluate(picks, mission, data)
    check("합계 일치", result["total"] == total, result["total"])
    check("품목 수 4", result["count"] == 4, result["count"])
    check("오차 = 예산 차이", result["diff"] == abs(total - 23000), result["diff"])
    # 예산 점수는 오늘 시세에 따라 달라지므로 경계값 함수로 계산해 합산 규칙만 고정한다
    check("점수 = 예산 점수 + 조건 2개", result["points"] == bk.budget_points(result["diff"], 1000) + 40,
          (result["points"], bk.budget_points(result["diff"], 1000)))
    check("조건 모두 충족", all(c["met"] for c in result["checks"]), result["checks"])
    check("등급 = 점수 구간", result["grade"] == bk.grade_for(result["points"]), result["grade"])

    empty = bk.evaluate({}, mission, data)
    check("빈 장바구니 C등급", empty["grade"] == "C", empty)
    check("빈 장바구니 0점", empty["points"] == 0, empty["points"])
    check("빈 장바구니 품목 미달", empty["countOk"] is False)

    for diff, expected in [(0, 60), (1000, 60), (1001, 40), (2000, 40), (2001, 20), (4000, 20), (4001, 0)]:
        check("예산 점수 %d원 오차" % diff, bk.budget_points(diff, 1000) == expected,
              bk.budget_points(diff, 1000))

    # 최소 품목 미달 감점: 조건 2개 충족 + 예산 정확 + 2품목 → 100 - 20 = 80
    picks_two = {"apple": 1, "spinach": 1}
    total_two = prices["apple"] + prices["spinach"]
    near = {"date": "x", "seed": 0, "budget": total_two, "tolerance": 1000, "minItems": 4,
            "conditions": mission["conditions"]}
    result_two = bk.evaluate(picks_two, near, data)
    check("최소 품목 미달 감점", result_two["points"] == 80, result_two["points"])
    check("최소 품목 미달 표시", result_two["countOk"] is False)

    # 수량 3개까지 계산
    three = bk.evaluate({"apple": 3}, mission, data)
    check("수량 3개 합계", three["total"] == prices["apple"] * 3, three["total"])

    print("== 최고 조합 ==")
    best = bk.best_combination(mission, data)
    check("최고 조합 S", best["grade"] == "S", best)
    check("최고 조합 100점", best["points"] == 100, best["points"])
    check("최고 조합 예산 안", abs(best["total"] - mission["budget"]) <= mission["tolerance"],
          (best["total"], mission["budget"]))
    # 완전탐색 재검증 — 더 높은 점수가 없는지
    ids = [item["id"] for item in data["items"]]
    best_points = 0
    for combo in itertools.product(range(4), repeat=len(ids)):
        if not any(combo):
            continue
        points = bk.evaluate(dict(zip(ids, combo)), mission, data)["points"]
        best_points = max(best_points, points)
    check("완전탐색 최고점 일치", best_points == best["points"], (best_points, best["points"]))


def check_html(data):
    print("== HTML ==")
    src = open(HTML, encoding="utf-8").read()
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+[\"\s']on[a-z]+\s*=", src, re.I))
    check("data-page basket", 'data-page="basket"' in src)
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 basket.html", src.count('href="basket.html"') >= 2, src.count('href="basket.html"'))
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("unsafe-inline 미사용(script)", "script-src 'self' 'unsafe-inline'" not in src)
    check("스트릭 저장 키", "secjobs-basket-v1" in src)
    check("미니 바", 'id="bkMini"' in src)
    check("제출 버튼", 'id="bkSubmit"' in src)
    check("결과 복사", 'id="bkShare"' in src)
    check("등급 카드", 'id="bkGrade"' in src)
    check("등급 규칙 문구", "90점 이상 S" in src)
    check("KAMIS 출처 링크", src.count("kamis.or.kr") >= 8, src.count("kamis.or.kr"))
    check("장보기 타이밍 연결", 'href="grocery.html"' in src)
    check("PC 2단 레이아웃", "grid-template-columns: 330px" in src)
    check("모바일 1단", "@media (max-width: 900px)" in src)
    check("prefers-reduced-motion", "prefers-reduced-motion" in src)

    match = re.search(r'<script[^>]*id="bkData"[^>]*>(.*?)</script>', src, re.S)
    check("데이터 블록 1개", match is not None)
    if match:
        raw = match.group(1)
        check("스크립트 조기 종료 방지", "</" not in raw)
        embedded = json.loads(raw)
        region_id = embedded["region"]["id"]
        prices = {item["id"]: item["byRegion"][region_id]["latest"]["price"] for item in data["items"]}
        check("임베드 가격 == grocery_data.json",
              all(item["price"] == prices[item["id"]] for item in embedded["items"]),
              [(item["id"], item["price"], prices[item["id"]]) for item in embedded["items"]])
        check("임베드 8품목", len(embedded["items"]) == 8, len(embedded["items"]))
        check("임베드 미션 = 빌더 계산",
              embedded["mission"] == bk.mission_for(date.fromisoformat(embedded["mission"]["date"])),
              embedded["mission"])
        check("임베드 최고 조합 S", embedded["best"]["grade"] == "S", embedded["best"])
        check("임베드 규칙", embedded["rules"]["tolerance"] == 1000 and embedded["rules"]["budgetPoints"] == 60,
              embedded["rules"])
        check("공통 셸 페이지 등록", "basket" in ui_shell.PAGE_LABEL, ui_shell.PAGE_LABEL.get("basket"))


def main():
    data = load_json(DATA)
    check_data(data)
    check_mission(data)
    check_grading(data)
    check_html(data)
    print()
    if failures:
        print("실패 %d건" % len(failures))
        for name in failures:
            print("  - %s" % name)
        return 1
    mission = bk.mission_for(date(2026, 11, 24))
    print("장바구니 리그 검증 통과 (8품목 · 목표 %s원 · 조건 %d가지 · %d페이지 셸)"
          % (format(mission["budget"], ","), len(mission["conditions"]), SHEET_PAGES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

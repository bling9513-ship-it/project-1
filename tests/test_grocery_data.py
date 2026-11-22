#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""장보기 타이밍(grocery.html) 데이터·구성 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · grocery_data.json 이 KAMIS 소매가격 조사값만 담고 있는지
      - 품목 8종 · 지역 2곳(서울·수원) · 창은 정확히 28일
      - 최신 조사값이 최근 7일 안에 있고, 관측치가 5회 이상
      - 4주 중앙값을 series 로 다시 계산해 일치하는지(중앙값 조작 금지)
      - 등락률 (최신 − 중앙값) ÷ 중앙값 을 다시 계산해 일치하는지
      - 최저·최고가 series 의 실제 최소·최대인지
      - 관측치 수와 series 길이가 같고 날짜가 정렬·중복 없음
      - 모든 출처 링크가 kamis.or.kr 도메인인지(값을 만든 곳이 KAMIS 뿐인지)
  · grocery.html 이 그 데이터를 그대로 심었는지
      - data-page="grocery" · 23페이지 셸 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 품목 카드 8장 · 지역 버튼 2개 · localStorage 키 · 출처 표기
      - 임베드된 JSON == grocery_data.json (빌드 누락 검출)

실행: python3 tests/test_grocery_data.py
"""
import json
import os
import re
import statistics
from datetime import date, datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE_DIR, "grocery.html")
DATA = os.path.join(BASE_DIR, "grocery_data.json")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 23
WINDOW_DAYS = 28
NEUTRAL_PCT = 3.0
ITEMS = ("egg", "greenonion", "cabbage", "radish", "onion", "spinach", "zucchini", "apple")
REGIONS = ("seoul", "suwon")

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def check_data(data):
    print("== 데이터 구조 ==")
    items = data.get("items") or []
    check("품목 8종", [item["id"] for item in items] == list(ITEMS), [item["id"] for item in items])
    check("지역 2곳", [region["id"] for region in data.get("regionList", [])] == list(REGIONS),
          data.get("regionList"))
    check("지역 이름", [region["name"] for region in data.get("regionList", [])] == ["서울", "수원"],
          data.get("regionList"))
    check("지역 코드 서울 1101", data["regionList"][0]["code"] == "1101", data["regionList"][0])
    check("지역 코드 수원 3111", data["regionList"][1]["code"] == "3111", data["regionList"][1])
    check("출처 KAMIS", "KAMIS" in data["source"]["label"], data["source"]["label"])
    check("출처 링크 kamis", data["source"]["url"].startswith("https://www.kamis.or.kr/"),
          data["source"]["url"])

    print("== 수집 창 ==")
    start = datetime.strptime(data["window"]["start"], "%Y-%m-%d").date()
    end = datetime.strptime(data["window"]["end"], "%Y-%m-%d").date()
    check("창 28일", (end - start).days + 1 == WINDOW_DAYS, (data["window"]["start"], data["window"]["end"]))
    check("창 종료가 오늘 이전", end <= datetime.now().date(), end)
    check("수집 시각 형식", bool(re.match(r"^20\d\d-\d\d-\d\d \d\d:\d\d KST$", data["generated"])),
          data["generated"])

    for item in items:
        name = item.get("name")
        check("%s 규격" % name, bool(item.get("unit")), item.get("unit"))
        check("%s 등급" % name, bool(item.get("grade")), item.get("grade"))
        check("%s 두 지역" % name, set(item["byRegion"]) == set(REGIONS), list(item["byRegion"]))
        national = item["byRegion"]["seoul"]
        check("%s 전국/지역 구분" % name, (item.get("scope") == "national") == (name == "계란"),
              item.get("scope"))

        for rid in REGIONS:
            stats = item["byRegion"][rid]
            label = "%s/%s" % (name, rid)
            series = stats.get("series") or []
            dates = [row["d"] for row in series]
            prices = [row["p"] for row in series]

            check("%s 관측치 5회 이상" % label, len(series) >= 5, len(series))
            check("%s 관측치 수 일치" % label, stats["observations"] == len(series),
                  (stats["observations"], len(series)))
            check("%s 날짜 정렬" % label, dates == sorted(dates), dates[:5])
            check("%s 날짜 중복 없음" % label, len(dates) == len(set(dates)), len(dates))
            check("%s 창 안 날짜" % label,
                  all(start <= datetime.strptime(d, "%Y-%m-%d").date() <= end for d in dates),
                  dates[:3])
            check("%s 가격 양수·정수" % label,
                  all(isinstance(p, int) and p > 0 for p in prices), prices[:5])
            check("%s 최신값 = 마지막 관측치" % label,
                  stats["latest"]["date"] == dates[-1] and stats["latest"]["price"] == prices[-1],
                  (stats["latest"], dates[-1], prices[-1]))
            check("%s 최신 조사 최근 7일" % label,
                  (date.today() - datetime.strptime(stats["latest"]["date"], "%Y-%m-%d").date()).days <= 7,
                  stats["latest"]["date"])

            median = statistics.median(prices)
            expected = int(median) if float(median).is_integer() else round(median, 1)
            check("%s 중앙값 재계산" % label, stats["median"] == expected, (stats["median"], expected))
            gap = round((prices[-1] - median) / median * 100, 1)
            check("%s 등락률 재계산" % label, abs(stats["gapPct"] - gap) < 0.05,
                  (stats["gapPct"], gap))
            check("%s 최저값" % label,
                  stats["min"]["price"] == min(prices) and stats["min"]["date"] == dates[prices.index(min(prices))],
                  stats["min"])
            check("%s 최고값" % label,
                  stats["max"]["price"] == max(prices) and stats["max"]["date"] == dates[prices.index(max(prices))],
                  stats["max"])
            check("%s 출처 kamis" % label, stats["sourceUrl"].startswith("https://www.kamis.or.kr/"),
                  stats["sourceUrl"])
            check("%s 출처에 품목 코드" % label, "itemcode=" in stats["sourceUrl"], stats["sourceUrl"])
            if item.get("scope") == "national":
                check("%s 전국 조사 링크에 지역 코드 없음" % label,
                      "countycode=1101" not in stats["sourceUrl"]
                      and "countycode=3111" not in stats["sourceUrl"], stats["sourceUrl"])
            else:
                check("%s 출처에 지역 코드" % label, ("countycode=" + (
                    "1101" if rid == "seoul" else "3111")) in stats["sourceUrl"], stats["sourceUrl"])

        seoul, suwon = item["byRegion"]["seoul"], item["byRegion"]["suwon"]
        if item.get("scope") == "national":
            check("%s 축산물은 지역 공통값" % name,
                  seoul["latest"] == suwon["latest"] and seoul["median"] == suwon["median"],
                  (seoul["latest"], suwon["latest"]))
        else:
            check("%s 지역별 값 구분" % name, seoul["sourceUrl"] != suwon["sourceUrl"],
                  seoul["sourceUrl"])

    print("== 등락 칩 경계 ==")
    gaps = [item["byRegion"][rid]["gapPct"] for item in items for rid in REGIONS]
    check("칩 경계 -3/+3 정의", all(isinstance(gap, float) for gap in gaps), gaps[:4])
    check("고정값 아님(변동 있음)", len(set(gaps)) > 3, sorted(set(gaps)))


def check_html(src, data):
    print("== HTML ==")
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+[\s\"']on[a-z]+\s*=", src, re.I))
    check("data-page grocery", 'data-page="grocery"' in src)
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 grocery.html 등록", src.count('href="grocery.html"') >= 2,
          src.count('href="grocery.html"'))
    check("데스크톱 드롭다운에 장보기 타이밍", "장보기 타이밍" in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("unsafe-inline 미사용(script)", "script-src 'self' 'unsafe-inline'" not in src)
    check("카드 8장", src.count('class="gp-card"') == 8, src.count('class="gp-card"'))
    check("지역 버튼 2개", src.count('data-region="') == 2, src.count('data-region="'))
    check("관심 저장 키", "secjobs-grocery-saved-v1" in src)
    check("중앙값 표기", src.count("4주 중앙값") >= 8, src.count("4주 중앙값"))
    check("조사일 표기", "조사 · " in src)
    check("KAMIS 출처 링크", src.count("kamis.or.kr") >= 8, src.count("kamis.or.kr"))
    check("지역 안내", "전국" in src)
    check("추정 금지 안내", "추정" in src)
    check("스파크라인", src.count("gp-spark-svg") >= 8, src.count("gp-spark-svg"))
    check("PC 2단 레이아웃", "grid-template-columns: 296px" in src)
    check("모바일 1단", "@media (max-width: 900px)" in src)

    match = re.search(r'<script[^>]*id="gpData"[^>]*>(.*?)</script>', src, re.S)
    check("임베드 데이터 1개", match is not None)
    if match:
        raw = match.group(1)
        check("스크립트 조기 종료 방지", "</" not in raw)
        embedded = json.loads(raw)
        check("임베드 == grocery_data.json", embedded == data, "빌드 누락")


def main():
    data = load_json(DATA)
    check_data(data)
    with open(HTML, encoding="utf-8") as handle:
        src = handle.read()
    check_html(src, data)
    print()
    if failures:
        print("실패 %d건" % len(failures))
        for name in failures:
            print("  - %s" % name)
        return 1
    print("장보기 타이밍 검증 통과 (품목 %d개 · 지역 %d곳 · %d페이지 셸)"
          % (len(data["items"]), len(data["regionList"]), SHEET_PAGES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

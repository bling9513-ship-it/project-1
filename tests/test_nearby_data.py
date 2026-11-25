#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""우리 동네 지금 갈 곳(nearby.html) 데이터·화면 검증.

확인하는 것
  · 장소 데이터(nearby_data.json)
      - 자치구 8개 이상 · 장소 24곳 이상 · ID 중복 없음 · 자치구 목록에 속함
      - 분류·요금 표기 · 주소 · 공식 https 링크 · 체류 시간
      - 요일별 운영시간 7개 모두 있고, 열리는 날은 시작<종료 (24:00 은 1440분)
      - 자치구마다 2곳 이상 · 휴관 안내·확인일 표기
  · 대표 휴관 규칙
      - 서울도서관 월요일 휴관 · 서울숲 연중무휴 24시간 · 남산골 월요일 휴관
  · nearby.html
      - data-page="nearby" · 전체 메뉴 30페이지 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 자치구 칩(전체 + 9) · 남은 시간 3종 · 찜 저장 키 · 지도/공식 링크 · 데이터 기준일
      - 장소 30곳 임베드 · 무료/유료 배지 · 마감 임박 · 3분류 그리드

실행: python3 tests/test_nearby_data.py
"""
import json
import os
import re
import sys
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_nearby_html as nb

HTML = os.path.join(BASE_DIR, "nearby.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 30


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


failures = []


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def check_data():
    print("== 장소 데이터 ==")
    data = nb.load_data()
    places = data["places"]
    districts = data["districts"]
    check("자치구 8개 이상", len(districts) >= 8, len(districts))
    check("장소 24곳 이상", len(places) >= 24, len(places))
    check("자치구 중복 없음", len(districts) == len(set(districts)))
    ids = [place["id"] for place in places]
    check("장소 ID 중복 없음", len(ids) == len(set(ids)))
    for place in places:
        pid = place["id"]
        check("%s 이름" % pid, bool(place["name"]))
        check("%s 주소" % pid, "서울" in place["address"], place["address"])
        check("%s 분류" % pid, place["category"] in nb.CATEGORIES, place["category"])
        check("%s 요금" % pid, place["fee"] in ("무료", "유료"), place["fee"])
        check("%s 체류시간" % pid, place["duration"] >= 20, place["duration"])
        check("%s 공식 https" % pid, place["officialUrl"].startswith("https://"), place["officialUrl"])
        check("%s 휴관 안내" % pid, bool(place["closureNote"]))
        check("%s 확인일" % pid, bool(place["checkedOn"]))
        hours = place["hours"]
        check("%s 요일 7개" % pid, set(hours) == set(nb.DAYS), sorted(hours))
        open_days = 0
        for day in nb.DAYS:
            window = hours[day]
            if window is None:
                continue
            open_days += 1
            start, end = nb.parse_time(window[0]), nb.parse_time(window[1])
            check("%s %s 순서" % (pid, day), start < end, window)
        check("%s 여는 날 있음" % pid, open_days > 0, open_days)
    per_district = {name: sum(1 for place in places if place["district"] == name) for name in districts}
    for name, count in per_district.items():
        check("%s 장소 2곳 이상" % name, count >= 2, count)
    check("자료 기준일", bool(data["checkedOn"]) and bool(date.fromisoformat(data["checkedOn"])), data["checkedOn"])
    print("  자치구 %d · 장소 %d · %s" % (len(districts), len(places),
                                        ", ".join("%s %d" % (k, v) for k, v in per_district.items())))


def check_rules():
    print("== 휴관·운영 규칙 ==")
    data = nb.load_data()
    by_id = {place["id"]: place for place in data["places"]}
    library = by_id["seoul-library"]
    check("서울도서관 월 휴관", library["hours"]["mon"] is None, library["hours"]["mon"])
    check("서울도서관 화 21시", library["hours"]["tue"] == ["09:00", "21:00"], library["hours"]["tue"])
    forest = by_id["seoul-forest"]
    check("서울숲 24시간", all(forest["hours"][day] == ["00:00", "24:00"] for day in nb.DAYS))
    check("남산골 월 휴관", by_id["namsangol-hanok-village"]["hours"]["mon"] is None)
    check("국립중앙박물관 수 21시", by_id["national-museum-of-korea"]["hours"]["wed"] == ["09:30", "21:00"])
    check("24:00 파싱", nb.parse_time("24:00") == 1440)
    check("09:30 파싱", nb.parse_time("09:30") == 570)
    fees = {place["fee"] for place in data["places"]}
    check("무료·유료 모두 있음", fees == {"무료", "유료"}, fees)
    print("  월요일 휴관·24시간·야간 운영 규칙 확인")


def check_html():
    print("== nearby.html ==")
    html = read(HTML)
    payload = json.loads(re.search(r'<script type="application/json" id="nbData">(.*?)</script>', html, re.S).group(1))
    check("data-page", 'data-page="nearby"' in html)
    check("이모지 0", not EMOJI_RE.search(html), EMOJI_RE.findall(html)[:3])
    check("그라데이션 0", "linear-gradient" not in html and "radial-gradient" not in html)
    check("인라인 핸들러 0", not re.search(r'\son(click|load|change|input|submit|keydown)=', html, re.I))
    check("전체 메뉴 30페이지", html.count('class="ia-sheet-link') - html.count('class="ia-sheet-links"') == SHEET_PAGES,
          html.count('class="ia-sheet-link') - html.count('class="ia-sheet-links"'))
    check("임베드 장소 수", len(payload["places"]) == len(nb.load_data()["places"]), len(payload["places"]))
    chips = re.findall(r'class="nb-chip[^"]*" data-district="[^"]+"', html)
    check("자치구 칩 10개(전체+9)", len(chips) == len(payload["districts"]) + 1, len(chips))
    check("남은 시간 3종", all(('data-remain="%d"' % minutes) in html for minutes in (30, 60, 120)))
    check("찜 저장 키", nb.STORE_KEY in html)
    check("마감 임박 배지", "마감 임박" in html)
    check("무료/유료 배지", "is-free" in html and "is-paid" in html)
    check("지도 링크", "map.naver.com" in html)
    check("자료 기준일 표시", payload["checkedOn"] in html)
    check("3분류 그리드", all(('id="%s"' % grid) in html for grid in
                            ("nbOpenGrid", "nbShortGrid", "nbClosedGrid")))
    check("24시간 띠", "nb-band" in html and "nb-band-now" in html)
    check("공휴일 미반영 안내", "공휴일" in html and "반영하지 않" in html)
    check("지금 시각 표시", 'id="nbClock"' in html)
    print("  장소 %d곳 · 자치구 칩 %d · 남은 시간 3종" % (len(payload["places"]), len(payload["districts"]) + 1))


def main():
    check_data()
    check_rules()
    check_html()
    if failures:
        print("\n실패 %d건: %s" % (len(failures), failures))
        sys.exit(1)
    print("\n지금 갈 곳 검증 통과 (자치구 9 · 장소 %d곳 · 전체 메뉴 %d페이지)"
          % (len(nb.load_data()["places"]), SHEET_PAGES))


if __name__ == "__main__":
    main()

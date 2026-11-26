#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘의 지하철역(subway.html) 데이터·퍼즐 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · subway_data.json 이 서울 25개 구 역만 담았는지
      - 역 이름 중복 0 · 좌표가 서울 범위 안 · 자치구가 25개 구 중 하나
      - 노선 이름이 lines 목록에 있고 색상이 #RRGGBB 형식
      - deck 이 stations 의 순열인지(빠진 역·중복 없음)
      - 환승역(2개 이상 노선)이 70곳 이상인지 — 데이터가 납작해지지 않았는지
  · 퍼즐 규칙
      - 같은 날은 같은 역, 날짜만 다르면 다른 역
      - 306일 연속 정답이 모두 다르고, 306일 뒤 같은 역이 다시 나오는지
      - 글자 힌트(hit/near/miss) · 초성 추출 · 방향/거리 계산
  · subway.html 이 그 데이터를 그대로 심었는지
      - data-page="subway" · 26페이지 셸 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 노선 색 칩 · 초성 힌트 · 결과 그리드 · 3단계 가이드 · 스트릭 저장 키
      - 임베드된 JSON 의 오늘 정답 == 빌더가 계산한 정답(빌드 누락 검출)

실행: python3 tests/test_subway_data.py
"""
import json
import math
import os
import re
import sys
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_subway_html as sb
import ui_shell

HTML = os.path.join(BASE_DIR, "subway.html")
DATA = os.path.join(BASE_DIR, "subway_data.json")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 31
COLOR_RE = re.compile(r"^#[0-9A-F]{6}$")

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
    stations = data["stations"]
    names = [station["name"] for station in stations]
    check("역 300곳 이상", len(stations) >= 300, len(stations))
    check("역 이름 중복 없음", len(set(names)) == len(names), len(names) - len(set(names)))
    check("deck 이 stations 의 순열", sorted(data["deck"]) == sorted(names), len(data["deck"]))
    check("자치구 25개 구", all(station["area"] in sb.SEOUL_GU for station in stations),
          [station["name"] for station in stations if station["area"] not in sb.SEOUL_GU][:3])
    check("좌표 서울 범위", all(37.42 <= station["lat"] <= 37.72 and 126.75 <= station["lng"] <= 127.20
                                for station in stations),
          [(station["name"], station["lat"], station["lng"]) for station in stations
           if not (37.42 <= station["lat"] <= 37.72 and 126.75 <= station["lng"] <= 127.20)][:3])
    check("모든 역에 노선", all(station["lines"] for station in stations))
    known = {line["name"] for line in data["lines"]}
    check("노선 이름 정합", all(set(station["lines"]) <= known for station in stations),
          [station["name"] for station in stations if not set(station["lines"]) <= known][:3])
    check("노선 색 형식", all(COLOR_RE.match(line["color"]) for line in data["lines"]),
          [line for line in data["lines"] if not COLOR_RE.match(line["color"])][:2])
    check("노선 18종", len(data["lines"]) == 18, len(data["lines"]))
    multi = [station for station in stations if len(station["lines"]) >= 2]
    check("환승역 70곳 이상", len(multi) >= 70, len(multi))
    check("최다 환승역 5개 노선", max(len(station["lines"]) for station in stations) == 5,
          max(len(station["lines"]) for station in stations))
    kimpo = next((station for station in stations if station["name"] == "김포공항"), None)
    check("김포공항 5개 노선", kimpo and len(kimpo["lines"]) == 5, kimpo and kimpo["lines"])
    check("김포공항 노선 내용",
          kimpo and set(kimpo["lines"]) == {"5호선", "9호선", "공항철도", "김포골드라인", "서해선"},
          kimpo and kimpo["lines"])
    for name, area, lines in [
        ("강남", "강남구", {"2호선", "신분당선"}),
        ("왕십리", "성동구", {"2호선", "5호선", "경의중앙선", "수인분당선"}),
        ("서울역", "중구", {"1호선", "4호선", "공항철도"}),
        ("여의도", "영등포구", {"5호선", "9호선"}),
        ("사당", "동작구", {"2호선", "4호선"}),
        ("홍대입구", "마포구", {"2호선", "경의중앙선", "공항철도"}),
    ]:
        station = next((item for item in stations if item["name"] == name), None)
        check("%s 역 존재" % name, station is not None)
        if station:
            check("%s 자치구 %s" % (name, area), station["area"] == area, station["area"])
            check("%s 노선 %s" % (name, sorted(lines)), set(station["lines"]) == lines, station["lines"])
    check("확인일", data["checkedOn"] == "2026-11-24", data["checkedOn"])
    check("출처 3건", len(data["sources"]) >= 3, len(data["sources"]))
    check("출처 URL https", all(source["url"].startswith("https://") for source in data["sources"]),
          [source["url"] for source in data["sources"]])


def check_puzzle(data):
    print("== 퍼즐 규칙 ==")
    today = date(2026, 11, 24)
    check("같은 날 같은 정답", sb.answer_for(data, today) == sb.answer_for(data, today))
    check("다음 날 다른 정답", sb.answer_for(data, today) != sb.answer_for(data, today + timedelta(days=1)),
          (sb.answer_for(data, today), sb.answer_for(data, today + timedelta(days=1))))
    cycle = [sb.answer_for(data, today + timedelta(days=offset)) for offset in range(len(data["deck"]))]
    check("한 바퀴 %d일 모두 다른 역" % len(data["deck"]), len(set(cycle)) == len(cycle),
          len(cycle) - len(set(cycle)))
    check("한 바퀴 뒤 같은 역", sb.answer_for(data, today + timedelta(days=len(data["deck"]))) == cycle[0])

    print("== 힌트 계산 ==")
    check("초성 강남", sb.chosung("강남") == "ㄱㄴ", sb.chosung("강남"))
    check("초성 송파나루", sb.chosung("송파나루") == "ㅅㅍㄴㄹ", sb.chosung("송파나루"))
    check("초성 숫자 보존", sb.chosung("4.19민주묘지").startswith("4.19"), sb.chosung("4.19민주묘지"))
    check("글자 완전 일치", sb.syllable_state("강남", "강남") == ["hit", "hit"])
    check("글자 자리 바뀜 = near", sb.syllable_state("남강", "강남") == ["near", "near"],
          sb.syllable_state("남강", "강남"))
    check("글자 없음 = miss", sb.syllable_state("서울", "강남") == ["miss", "miss"],
          sb.syllable_state("서울", "강남"))
    check("한 글자만 맞음", sb.syllable_state("강변", "강남") == ["hit", "miss"],
          sb.syllable_state("강변", "강남"))

    gangnam = (37.4979, 127.0276)
    yeoksam = (37.5006, 127.0364)
    word, km = sb.bearing_words(gangnam[0], gangnam[1], yeoksam[0], yeoksam[1])
    check("강남→역삼 방향 동쪽", word in ("동", "북동"), word)
    check("강남→역삼 거리 0.5~1.5km", 0.5 <= km <= 1.5, round(km, 2))
    same_word, same_km = sb.bearing_words(gangnam[0], gangnam[1], gangnam[0], gangnam[1])
    check("같은 좌표 거리 0", same_km == 0, same_km)
    far_word, far_km = sb.bearing_words(37.56, 126.97, 37.65, 127.06)
    check("북쪽 방향", far_word in ("북", "북동"), far_word)
    check("거리 10km 이상", far_km > 10, round(far_km, 1))

    check("정답 1수 완벽", sb.grade([1], True) == "완벽")
    check("3수 이내 빠름", sb.grade([1, 2, 3], True) == "빠름")
    check("5수 정답", sb.grade([1, 2, 3, 4, 5], True) == "정답")
    check("실패 아쉬움", sb.grade([1, 2, 3, 4, 5, 6], False) == "아쉬움")


def check_html(data):
    print("== HTML ==")
    src = open(HTML, encoding="utf-8").read()
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+[\s\"']on[a-z]+\s*=", src, re.I))
    check("data-page subway", 'data-page="subway"' in src)
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 subway.html", src.count('href="subway.html"') >= 2, src.count('href="subway.html"'))
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("unsafe-inline 미사용(script)", "script-src 'self' 'unsafe-inline'" not in src)
    check("노선 색 2호선", "#00A84D" in src)
    check("노선 색 신분당선", "#D4003B" in src)
    check("초성 힌트 영역", 'id="swBlanks"' in src)
    check("결과 복사 영역", 'id="swShare"' in src)
    check("3단계 가이드", src.count('class="sw-step"') == 3, src.count('class="sw-step"'))
    check("다시 보기", 'id="swReplay"' in src)
    check("가이드 재생 문구", "재생" in src)
    check("스트릭 저장 키", "secjobs-subway-v1" in src)
    check("연습 모드", 'data-mode="practice"' in src)
    check("결과 그리드 문자", "■" in src and "▽" in src)
    check("prefers-reduced-motion", "prefers-reduced-motion" in src)
    check("PC 2단 레이아웃", "minmax(0, 1fr) 320px" in src)
    check("모바일 1단", "@media (max-width: 900px)" in src)
    check("스포일러 방지 문구", "스포일러" in src)

    match = re.search(r'<script[^>]*id="swData"[^>]*>(.*?)</script>', src, re.S)
    check("데이터 블록 1개", match is not None)
    if match:
        raw = match.group(1)
        check("스크립트 조기 종료 방지", "</" not in raw)
        embedded = json.loads(raw)
        check("임베드 역 수", len(embedded["stations"]) == len(data["stations"]),
              (len(embedded["stations"]), len(data["stations"])))
        check("임베드 == subway_data.json (역)",
              embedded["stations"] == data["stations"], "빌드 누락")
        check("임베드 == subway_data.json (노선)", embedded["lines"] == data["lines"], "빌드 누락")
        today = date.fromisoformat(embedded["meta"]["answerDate"])
        check("임베드 정답 == 빌더 계산", embedded["meta"]["answer"] == sb.answer_for(data, today),
              (embedded["meta"]["answer"], sb.answer_for(data, today)))
        answer_station = next(station for station in data["stations"] if station["name"] == embedded["meta"]["answer"])
        check("정답 노선 일치", embedded["meta"]["answerLines"] == answer_station["lines"],
              embedded["meta"]["answerLines"])
        check("정답 초성 일치", embedded["meta"]["answerChosung"] == sb.chosung(answer_station["name"]),
              embedded["meta"]["answerChosung"])
        check("최대 시도 6", embedded["meta"]["maxTries"] == 6, embedded["meta"]["maxTries"])
        check("공통 셸 페이지 등록", "subway" in ui_shell.PAGE_LABEL, ui_shell.PAGE_LABEL.get("subway"))


def main():
    data = load_json(DATA)
    check_data(data)
    check_puzzle(data)
    check_html(data)
    print()
    if failures:
        print("실패 %d건" % len(failures))
        for name in failures:
            print("  - %s" % name)
        return 1
    print("지하철역 퍼즐 검증 통과 (역 %d곳 · 노선 %d종 · %d페이지 셸)"
          % (len(data["stations"]), len(data["lines"]), SHEET_PAGES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

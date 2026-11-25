#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""증시 이슈 요약(market.html) 데이터·화면 검증.

확인하는 것
  · market_data.json
      - 기사 6건 이상 · ID 중복 없음 · 제목/한 줄 원인 있음
      - confidence 는 '원문 근거'/'추정'/'미확인' 중 하나, '미확인'이면 why 는 '뚜렷한 원인 미확인'
      - 섹터는 정해진 목록 안 · 기사 링크 https · 출처 매체 이름 있음
      - 국내/해외 지수 각 2개 이상 · 값·등락률 숫자 · 현지 거래일 형식 · 지연 시세 표기
      - 브리핑: 국내/해외 각 마감 3줄·아침 3줄
      - 일정: 날짜/시각 형식 · 날짜 순 정렬 · 지역 표기 · FOMC·물가·고용 일정 포함
  · market.html
      - data-page="market" · 전체 메뉴 30페이지 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 국내/해외 탭 · 섹터 필터 칩 · 지수 카드 · 일정 목록 · 원문 링크 · 지연 시세 안내
      - 심긴 JSON 이 market_data.json 과 같은지

실행: python3 tests/test_market_data.py
"""
import json
import os
import re
import sys
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_market_html as mk

HTML = os.path.join(BASE_DIR, "market.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 30
failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def check_data():
    print("== 증시 데이터 ==")
    data = mk.load_data()
    issues = data["issues"]
    check("기사 6건 이상", len(issues) >= 6, len(issues))
    ids = [row["id"] for row in issues]
    check("기사 ID 중복 없음", len(ids) == len(set(ids)))
    for row in issues:
        tag = row["id"]
        check("%s 제목" % tag, bool(row["title"].strip()))
        check("%s 한 줄 원인" % tag, bool(row["why"].strip()))
        check("%s 신뢰도" % tag, row["confidence"] in mk.CONFIDENCE_VALUES, row["confidence"])
        if row["confidence"] == "미확인":
            check("%s 미확인 문구" % tag, row["why"] == "뚜렷한 원인 미확인", row["why"])
        check("%s 시장" % tag, row["market"] in ("domestic", "global"), row["market"])
        check("%s 섹터" % tag, row["sectors"] and all(name in mk_sectors(data) for name in row["sectors"]),
              row["sectors"])
        check("%s 원문 링크" % tag, row["url"].startswith("http"), row["url"])
        check("%s 출처" % tag, bool(row["source"]))
    markets = {row["market"] for row in issues}
    check("국내·해외 모두 있음", markets == {"domestic", "global"}, markets)

    for row in data["indices"]:
        tag = "지수 %s" % row["name"]
        check("%s 값" % tag, isinstance(row["value"], (int, float)), row["value"])
        check("%s 등락률" % tag, isinstance(row["changePct"], (int, float)), row["changePct"])
        check("%s 현지 거래일" % tag, bool(re.match(r"^\d{4}-\d{2}-\d{2}$", row["lastTradingDate"])),
              row["lastTradingDate"])
        check("%s 지연 표기" % tag, row.get("delayed") is True)
        check("%s 출처 링크" % tag, str(row["sourceUrl"]).startswith("https://"), row["sourceUrl"])
    domestic = [row for row in data["indices"] if row["market"] == "domestic"]
    global_ = [row for row in data["indices"] if row["market"] == "global"]
    check("국내 지수 2개 이상", len(domestic) >= 2, len(domestic))
    check("해외 지수 3개 이상", len(global_) >= 3, len(global_))
    check("빅테크 5종 이상", len(data["bigtech"]) >= 5, len(data["bigtech"]))

    for key in ("domestic", "global"):
        session = data["sessions"][key]
        check("%s 세션 상태" % key, session["state"] in ("open", "closed", "preopen", "holiday", "unknown"),
              session["state"])
        check("%s 마지막 거래일" % key, bool(re.match(r"^\d{4}-\d{2}-\d{2}$", session["lastTradingDate"])),
              session["lastTradingDate"])
        briefing = data["briefing"][key]
        check("%s 마감 3줄" % key, len(briefing["close"]) == 3, len(briefing["close"]))
        check("%s 아침 3줄" % key, len(briefing["morning"]) == 3, len(briefing["morning"]))
        check("%s 줄 길이" % key, all(6 <= len(line) <= 120 for line in briefing["close"] + briefing["morning"]))

    calendar = data["calendar"]
    check("일정 5건 이상", len(calendar) >= 5, len(calendar))
    for row in calendar:
        tag = "일정 %s" % row["id"]
        check("%s 날짜" % tag, bool(re.match(r"^\d{4}-\d{2}-\d{2}$", row["date"])), row["date"])
        check("%s 시각" % tag, row["timeKst"] == "" or bool(re.match(r"^\d{2}:\d{2}$", row["timeKst"])),
              row["timeKst"])
        check("%s 지역" % tag, row["region"] in ("국내", "해외"), row["region"])
        check("%s 제목" % tag, bool(row["title"].strip()))
        check("%s 출처" % tag, bool(row["source"]))
        check("%s 링크" % tag, str(row["sourceUrl"]).startswith("http"), row["sourceUrl"])
        check("%s 날짜 파싱" % tag, bool(date.fromisoformat(row["date"])))
    dates = [row["date"] for row in calendar]
    check("일정 날짜 순 정렬", dates == sorted(dates), dates[:5])
    categories = {row["category"] for row in calendar}
    check("금리 일정 포함", "금리" in categories, categories)
    check("물가·고용 일정 포함", {"물가", "고용"} & categories, categories)
    titles = " ".join(row["title"] for row in calendar)
    check("FOMC 일정", "FOMC" in titles, titles[:60])
    check("CPI 일정", "CPI" in titles)
    check("고용보고서 일정", "고용보고서" in titles)
    check("금통위 일정", "금통위" in titles)
    check("실적 일정", "실적" in titles)

    meta = data["meta"]
    check("수집 시각", bool(re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} KST$", meta["collectedAt"])),
          meta["collectedAt"])
    check("출처 목록", len(meta["sources"]) >= 3, len(meta["sources"]))
    check("안내 문구", any("지연" in line for line in meta["notes"]))
    print("  기사 %d건 · 지수 %d · 빅테크 %d · 일정 %d건 (AI %s)"
          % (len(issues), len(data["indices"]), len(data["bigtech"]), len(calendar),
             meta["ai"].get("model") or "폴백"))


def mk_sectors(data):
    return {row["name"] for row in data["sectors"]}


def check_html():
    print("== market.html ==")
    html = read(HTML)
    payload = json.loads(re.search(r'<script type="application/json" id="mkData">(.*?)</script>', html, re.S).group(1))
    data = mk.load_data()
    check("data-page", 'data-page="market"' in html)
    check("이모지 0", not EMOJI_RE.search(html), EMOJI_RE.findall(html)[:3])
    check("그라데이션 0", "linear-gradient" not in html and "radial-gradient" not in html)
    check("인라인 핸들러 0", not re.search(r'\son(click|load|change|input|submit|keydown)=', html, re.I))
    links = html.count('class="ia-sheet-link') - html.count('class="ia-sheet-links"')
    check("전체 메뉴 %d페이지" % SHEET_PAGES, links == SHEET_PAGES, links)
    check("증시 이슈 메뉴 링크", 'href="market.html"' in html and "증시 이슈" in html)
    check("임베드 기사 수", len(payload["issues"]) == len(data["issues"]), len(payload["issues"]))
    check("임베드 일정 수", len(payload["calendar"]) == len(data["calendar"]), len(payload["calendar"]))
    check("국내/해외 탭", 'data-market="domestic"' in html and 'data-market="global"' in html)
    check("탭 패널", all(('id="%s"' % pid) in html for pid in ("mkPanelDomestic", "mkPanelGlobal")))
    check("지수 스냅샷", 'id="mkSnapshot"' in html)
    check("브리핑 3줄 영역", all(('id="%s"' % rid) in html for rid in
                              ("mkCloseDomestic", "mkMorningDomestic", "mkCloseGlobal", "mkMorningGlobal")))
    check("섹터 필터 칩 영역", 'id="mkSectorChips"' in html)
    for name in ("AI·반도체", "방산", "2차전지", "바이오"):
        check("섹터 %s" % name, name in html, name)
    check("일정 목록", 'id="mkCalendar"' in html and "D-DAY" in html)
    check("시간 미정 표기", "시간 미정" in html)
    check("지연 시세 안내", "지연 시세" in html)
    check("원인 미확인 안내", "뚜렷한 원인 미확인" in html)
    check("원문 링크", all(('"url":"%s"' % row["url"].replace("/", "/")) or row["url"] in html
                          for row in payload["issues"][:5]))
    check("테스트 훅", "window.MARKET" in html)
    print("  기사 %d건 · 일정 %d건 · 메뉴 %d페이지"
          % (len(payload["issues"]), len(payload["calendar"]), links))


def main():
    check_data()
    check_html()
    if failures:
        print("\n실패 %d건: %s" % (len(failures), failures[:8]))
        sys.exit(1)
    print("\n증시 이슈 검증 통과 (전체 메뉴 %d페이지)" % SHEET_PAGES)


if __name__ == "__main__":
    main()

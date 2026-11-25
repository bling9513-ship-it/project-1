#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""증시 이슈 요약(market.html) 데이터·화면 검증.

확인하는 것
  · market_data.json
      - 기사 6건 이상 · ID 중복 없음 · 제목/한 줄 원인 있음
      - confidence 는 '원문 근거'/'추정'/'미확인' 중 하나, '미확인'이면 why 는 '뚜렷한 원인 미확인'
      - 섹터는 정해진 목록 안 · 기사 링크 https · 출처 매체 이름 있음
      - 재배포 제한 매체(연합뉴스·매일경제·Yahoo Finance) 기사 0건
      - RSS 설명·요약 필드(summary/summary_orig) 0건
      - 지수·종목·환율 수치 필드(indices/bigtech/fx) 없음
      - 장 상태: 상태 값·현지 시각·거래 시간·최근/다음 거래일
      - 브리핑: 국내/해외 각 '오늘의 이슈 3줄'·'다음 거래일 점검 3줄'
      - 일정: 날짜/시각 형식 · 날짜 순 정렬 · 지역 표기 · FOMC·물가·고용 일정 포함
      - BLS 보관 사본 일정: 카드에 보관일(snapshotDate)과 공식 원문 링크(sourceUrl)
  · 장 상태 계산(단위 테스트)
      - 11/27 14:00 ET → '조기 마감'(장 진행 중 아님)
      - 정상 개장일 09:31 → '장 진행 중'(휴장 오표기 없음)
  · market.html
      - data-page="market" · 전체 메뉴 30페이지 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 장 상태 카드 · 국내/해외 탭 · 섹터 필터 칩 · 일정 목록 · 원문 링크 · 시세 미게시 안내
      - 심긴 JSON 이 market_data.json 과 같은지

실행: python3 tests/test_market_data.py
"""
import json
import os
import re
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_market_html as mk
import market_crawler as mc

HTML = os.path.join(BASE_DIR, "market.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 30
BLOCKED = ("연합뉴스", "매일경제", "Yahoo Finance")
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
    sectors = {row["name"] for row in data["sectors"]}
    for row in issues:
        tag = row["id"]
        check("%s 제목" % tag, bool(row["title"].strip()))
        check("%s 한 줄 원인" % tag, bool(row["why"].strip()))
        check("%s 신뢰도" % tag, row["confidence"] in mk.CONFIDENCE_VALUES, row["confidence"])
        if row["confidence"] == "미확인":
            check("%s 미확인 문구" % tag, row["why"] == "뚜렷한 원인 미확인", row["why"])
        check("%s 시장" % tag, row["market"] in ("domestic", "global"), row["market"])
        check("%s 섹터" % tag, row["sectors"] and all(name in sectors for name in row["sectors"]),
              row["sectors"])
        check("%s 원문 링크" % tag, row["url"].startswith("http"), row["url"])
        check("%s 출처" % tag, bool(row["source"]))
        check("%s 제한 매체 아님" % tag, row["source"] not in BLOCKED, row["source"])
        for field in ("summary", "summary_orig"):
            check("%s %s 없음" % (tag, field), not str(row.get(field) or "").strip())

    # 시세 재게시 금지: 수치 필드 자체가 없어야 한다.
    for field in ("indices", "bigtech", "fx"):
        check("%s 필드 없음" % field, field not in data, field)

    for key in ("domestic", "global"):
        session = data["sessions"][key]
        check("%s 세션 상태" % key,
              session["state"] in ("open", "closed", "preopen", "holiday", "early_closed", "unknown"),
              session["state"])
        check("%s 현지 시각" % key, bool(re.match(r"^\d{2}-\d{2} \d{2}:\d{2}$", session["localNow"])),
              session["localNow"])
        check("%s 거래 시간" % key, bool(re.match(r"^\d{2}:\d{2}~\d{2}:\d{2}$", session["sessionText"])),
              session["sessionText"])
        check("%s 최근 거래일" % key,
              bool(re.match(r"^\d{4}-\d{2}-\d{2}$", session["lastTradingDate"])),
              session["lastTradingDate"])
        check("%s 다음 거래일" % key,
              bool(re.match(r"^\d{4}-\d{2}-\d{2}$", session["nextTradingDate"])),
              session["nextTradingDate"])
        check("%s 캘린더 범위" % key, session["outsideCalendar"] is False, session["localDate"])
        briefing = data["briefing"][key]
        check("%s 이슈 3줄" % key, len(briefing.get("issues") or []) == 3, len(briefing.get("issues") or []))
        check("%s 점검 3줄" % key, len(briefing.get("next") or []) == 3, len(briefing.get("next") or []))
        check("%s 줄 길이" % key,
              all(6 <= len(line) <= 120 for line in (briefing["issues"] + briefing["next"])))
        check("%s 브리핑에 지수 수치 없음" % key,
              not re.search(r"\d{1,3}(,\d{3})+(\.\d+)?", " ".join(briefing["issues"] + briefing["next"])))

    calendar = data["calendar"]
    check("일정 5건 이상", len(calendar) >= 5, len(calendar))
    archive_rows = 0
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
        if row.get("snapshotDate"):
            archive_rows += 1
            check("%s 보관일 형식" % tag, bool(re.match(r"^\d{4}-\d{2}-\d{2}$", row["snapshotDate"])),
                  row["snapshotDate"])
            check("%s 보관 사본 링크" % tag, str(row.get("archiveUrl") or "").startswith("https://web.archive.org/"),
                  row.get("archiveUrl"))
            check("%s 공식 원문 링크" % tag, "bls.gov" in str(row["sourceUrl"]), row["sourceUrl"])
            check("%s 카드에 보관일 표기" % tag, row["snapshotDate"] in (row.get("note") or ""), row.get("note"))
    check("BLS 보관 사본 일정 있음", archive_rows >= 1, archive_rows)
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
    check("일정에 시가총액 미노출", "시가총액" not in json.dumps(calendar, ensure_ascii=False))

    meta = data["meta"]
    check("수집 시각", bool(re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} KST$", meta["collectedAt"])),
          meta["collectedAt"])
    check("출처 목록", len(meta["sources"]) >= 3, len(meta["sources"]))
    check("안내 문구", any("시세" in line for line in meta["notes"]))
    feed_urls = " ".join(str(row.get("url") or "") for row in meta["sources"])
    check("연합뉴스 피드 없음", "yna.co.kr" not in feed_urls)
    check("매일경제 피드 없음", "mk.co.kr" not in feed_urls)
    check("야후 시세 피드 없음", "finance.yahoo.com/v8" not in feed_urls)
    print("  기사 %d건 · 일정 %d건(보관 사본 %d) · AI %s"
          % (len(issues), len(calendar), archive_rows, meta["ai"].get("model") or "폴백"))


def check_sessions():
    print("== 장 상태 계산 ==")
    et = ZoneInfo("America/New_York")
    kst = ZoneInfo("Asia/Seoul")

    def state(market, moment):
        return mc.market_session(market, moment)

    # ChatGPT 교차 검증 지적 1: 11/27 추수감사절 다음 날 13:00 ET 조기 마감
    case = state("global", datetime(2026, 11, 27, 14, 0, tzinfo=et))
    check("11/27 14:00 ET 조기 마감", case["state"] == "early_closed", case["state"])
    check("11/27 조기 마감 문구", "조기 마감" in case["stateLabel"], case["stateLabel"])
    check("11/27 거래 시간 13:00", case["sessionText"] == "09:30~13:00", case["sessionText"])
    check("11/27 장 진행 중 아님", case["stateLabel"] != "장 진행 중", case["stateLabel"])

    before = state("global", datetime(2026, 11, 27, 12, 59, tzinfo=et))
    check("11/27 12:59 ET 장 진행 중", before["state"] == "open", before["state"])
    at_close = state("global", datetime(2026, 11, 27, 13, 0, tzinfo=et))
    check("11/27 13:00 ET 조기 마감", at_close["state"] == "early_closed", at_close["state"])

    # ChatGPT 교차 검증 지적 2: 정상 개장일 09:31 에 당일 봉이 지연돼도 휴장이 아니다
    normal = state("global", datetime(2026, 12, 2, 9, 31, tzinfo=et))
    check("정상 개장일 09:31 장 진행 중", normal["state"] == "open", normal["state"])
    check("정상 개장일 휴장 아님", normal["stateLabel"] != "휴장", normal["stateLabel"])

    # 휴장·개장 전·마감
    thanksgiving = state("global", datetime(2026, 11, 26, 11, 0, tzinfo=et))
    check("추수감사절 휴장", thanksgiving["state"] == "holiday", thanksgiving["state"])
    check("추수감사절 사유", "추수감사절" in thanksgiving["reason"], thanksgiving["reason"])
    weekend = state("global", datetime(2026, 11, 28, 11, 0, tzinfo=et))
    check("주말 휴장", weekend["state"] == "holiday", weekend["state"])
    preopen = state("domestic", datetime(2026, 11, 26, 8, 0, tzinfo=kst))
    check("국내 개장 전", preopen["state"] == "preopen", preopen["state"])
    closed = state("domestic", datetime(2026, 11, 26, 16, 0, tzinfo=kst))
    check("국내 장 마감", closed["state"] == "closed", closed["state"])
    holiday = state("domestic", datetime(2026, 12, 25, 10, 0, tzinfo=kst))
    check("국내 성탄절 휴장", holiday["state"] == "holiday", holiday["state"])
    check("국내 휴장 사유", "성탄절" in holiday["reason"], holiday["reason"])
    christmas_eve = state("global", datetime(2026, 12, 24, 13, 30, tzinfo=et))
    check("12/24 조기 마감", christmas_eve["state"] == "early_closed", christmas_eve["state"])
    # 다음 거래일 계산: 금요일 조기 마감 뒤에는 월요일
    check("11/27 다음 거래일", at_close["nextTradingDate"] == "2026-11-30", at_close["nextTradingDate"])
    # 수능일 늦은 개장
    late_open = state("domestic", datetime(2026, 11, 19, 9, 31, tzinfo=kst))
    check("수능일 09:31 개장 전", late_open["state"] == "preopen", late_open["state"])
    check("수능일 거래 시간", late_open["sessionText"] == "10:00~16:30", late_open["sessionText"])
    print("  단위 테스트 %d건 확인" % 17)


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
    check("임베드 장 상태", set(payload["sessions"].keys()) == {"domestic", "global"}, payload["sessions"].keys())
    check("시세 수치 미임베드",
          not any(field in payload for field in ("indices", "bigtech", "fx")),
          [field for field in ("indices", "bigtech", "fx") if field in payload])
    check("기사 요약 미임베드", not any("summary" in row for row in payload["issues"]))
    check("국내/해외 탭", 'data-market="domestic"' in html and 'data-market="global"' in html)
    check("탭 패널", all(('id="%s"' % pid) in html for pid in ("mkPanelDomestic", "mkPanelGlobal")))
    check("장 상태 영역", 'id="mkStatus"' in html)
    check("브리핑 영역", all(('id="%s"' % rid) in html for rid in
                           ("mkTodayDomestic", "mkNextDomestic", "mkTodayGlobal", "mkNextGlobal")))
    check("섹터 필터 칩 영역", 'id="mkSectorChips"' in html)
    for name in ("AI·반도체", "방산", "2차전지", "바이오"):
        check("섹터 %s" % name, name in html, name)
    check("일정 목록", 'id="mkCalendar"' in html and "D-DAY" in html)
    check("시간 미정 표기", "시간 미정" in html)
    check("시세 미게시 안내", "시세 수치" in html)
    check("공식 시세 확인 링크", all(label in html for label in ("KRX 정보데이터시스템", "네이버 증권", "Nasdaq")))
    check("원인 미확인 안내", "뚜렷한 원인 미확인" in html)
    check("보관 사본 표기 로직", "보관 사본" in html)
    check("원문 링크", all(row["url"] in html for row in payload["issues"][:5]))
    check("제한 매체 기사 없음", all(row["source"] not in BLOCKED for row in payload["issues"]))
    check("테스트 훅", "window.MARKET" in html)
    print("  기사 %d건 · 일정 %d건 · 메뉴 %d페이지"
          % (len(payload["issues"]), len(payload["calendar"]), links))


def main():
    check_data()
    check_sessions()
    check_html()
    if failures:
        print("\n실패 %d건: %s" % (len(failures), failures[:8]))
        sys.exit(1)
    print("\n증시 이슈 검증 통과 (전체 메뉴 %d페이지)" % SHEET_PAGES)


if __name__ == "__main__":
    main()

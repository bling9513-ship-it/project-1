#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실시간 월급·퇴근 미터(paymeter.html) 계산·구성 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · 급여 환산: 연봉·월급 → 시급(월 소정근로 209시간), 일급·오늘 번 돈 계산
  · 근무 시간: 점심 무급/유급, 야간 근무(퇴근 < 출근), 출근 전·점심·퇴근 후 경계
  · 영수증 문구에 오늘 날짜·출퇴근·금액이 들어가고, 남은 시간/마침 문구가 상태에 맞는지
  · paymeter.html 이 26페이지 공통 셸 · CSP · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0 을 지키는지
  · 화면에 심은 설정(급여 방식·금액·환산 기준 가격·저장 키)이 빌더 상수와 같은지

실행: python3 tests/test_paymeter_logic.py
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_paymeter_html as pm
import ui_shell

HTML = os.path.join(BASE_DIR, "paymeter.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 26
KST = timezone(timedelta(hours=9))

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def approx(left, right, tolerance=0.5):
    return abs(float(left) - float(right)) <= tolerance


def check_calc():
    print("== 급여 환산 ==")
    hourly = pm.hourly_wage("annual", 42000000)
    check("연봉 4,200만 시급 = 연봉÷12÷209", approx(hourly, 42000000 / 12 / 209), hourly)
    check("연봉 4,200만 시급 값", approx(hourly, 16746.4, 1), round(hourly, 1))
    check("월급 300만 시급", approx(pm.hourly_wage("monthly", 3000000), 3000000 / 209), pm.hourly_wage("monthly", 3000000))
    check("시급은 그대로", pm.hourly_wage("hourly", 12000) == 12000)
    check("금액 0이면 0", pm.hourly_wage("annual", 0) == 0)
    check("음수 금액은 0", pm.hourly_wage("monthly", -100) == 0)

    print("== 근무 시간 ==")
    check("9~18시 점심 60분 무급 = 480분", pm.work_minutes("09:00", "18:00", 60, False) == 480)
    check("9~18시 점심 60분 유급 = 540분", pm.work_minutes("09:00", "18:00", 60, True) == 540)
    check("점심 없음(0분) = 540분", pm.work_minutes("09:00", "18:00", 0, False) == 540)
    check("야간 22~06시 = 480분(점심 없음)", pm.work_minutes("22:00", "06:00", 0, False) == 480)
    check("야간 22~06시 점심 60분 무급 = 420분", pm.work_minutes("22:00", "06:00", 60, False) == 420)
    check("출근=퇴근은 야간(24시간) 처리", pm.shift_span("09:00", "09:00")[2] is True)

    print("== 지금까지 실근무 ==")
    def worked(hhmm, **kwargs):
        args = dict(start="09:00", end="18:00", lunch_start="12:00", lunch_min=60, lunch_paid=False)
        args.update(kwargs)
        hour, minute = [int(part) for part in hhmm.split(":")]
        return pm.worked_minutes(hour * 60 + minute, **args)

    check("08:00 출근 전 = 0분", worked("08:00") == 0)
    check("09:00 정각 = 0분", worked("09:00") == 0)
    check("10:30 = 90분", worked("10:30") == 90)
    check("12:00 점심 시작 = 180분", worked("12:00") == 180)
    check("12:30 점심 중 = 180분(멈춤)", worked("12:30") == 180)
    check("13:00 점심 끝 = 180분", worked("13:00") == 180)
    check("14:00 = 240분", worked("14:00") == 240)
    check("18:00 퇴근 = 480분", worked("18:00") == 480)
    check("20:00 퇴근 후 = 480분(고정)", worked("20:00") == 480)
    check("점심 유급이면 12:30 = 210분", worked("12:30", lunch_paid=True) == 210)
    check("야간 23:00 = 60분", worked("23:00", start="22:00", end="06:00", lunch_start="02:00", lunch_min=60) == 60)
    check("야간 01:00 = 180분", worked("01:00", start="22:00", end="06:00", lunch_start="02:00", lunch_min=60) == 180)
    check("야간 06:30 = 420분(고정)", worked("06:30", start="22:00", end="06:00", lunch_start="02:00", lunch_min=60) == 420)

    print("== 하루 총액 · 상태 ==")
    daily = pm.daily_pay("annual", 42000000, "09:00", "18:00", 60, False)
    check("하루 총액 = 시급 × 8시간", approx(daily, 16746.41 * 8, 2), round(daily))
    phase = lambda hhmm: pm.phase_at(int(hhmm[:2]) * 60 + int(hhmm[3:]), "09:00", "18:00", "12:00", 60)
    check("08:00 출근 전", phase("08:00") == "before")
    check("10:00 오전", phase("10:00") == "morning")
    check("12:30 점심", phase("12:30") == "lunch")
    check("14:00 오후", phase("14:00") == "afternoon")
    check("18:10 퇴근 후", phase("18:10") == "after")

    check("금액 표기 1,234,567", pm.fmt_won(1234567) == "1,234,567")
    check("시간 표기 8시간 0분", pm.fmt_duration(480) == "8시간 0분")
    check("시간 표기 45분", pm.fmt_duration(45) == "45분")


def check_receipt():
    print("== 영수증 ==")
    state = dict(pm.DEFAULT_STATE)
    noon = datetime(2026, 11, 24, 15, 0, tzinfo=KST)
    lines = pm.receipt_lines(state, noon)
    text = "\n".join(lines)
    check("날짜 포함", "2026-11-24" in text, lines[0])
    check("요일 표기", "(화)" in lines[0], lines[0])
    check("출퇴근 표기", "출근 09:00" in text and "퇴근 18:00" in text, lines[1])
    check("실근무 5시간 0분", "실근무 5시간 0분" in text, lines[2])
    check("지금까지 금액", "지금까지" in text and "원" in text, lines[3])
    check("남은 시간 안내", "퇴근까지" in text, lines[-1])
    after = pm.receipt_lines(state, datetime(2026, 11, 24, 19, 0, tzinfo=KST))
    check("퇴근 후 문구", "수고하셨습니다" in "\n".join(after), after[-1])
    check("퇴근 후 금액 = 하루 총액", pm.fmt_won(pm.daily_pay("annual", 42000000, "09:00", "18:00", 60, False)) in after[3],
          after[3])


def check_html():
    print("== HTML ==")
    with open(HTML, encoding="utf-8") as handle:
        src = handle.read()
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+[\s\"']on[a-z]+\s*=", src, re.I))
    check("data-page paymeter", 'data-page="paymeter"' in src)
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 paymeter.html", src.count('href="paymeter.html"') >= 2, src.count('href="paymeter.html"'))
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("unsafe-inline 미사용(script)", "script-src 'self' 'unsafe-inline'" not in src)
    check("월 소정근로 209시간 안내", "209시간" in src)
    check("저장 키", "secjobs-paymeter-v1" in src)
    check("영수증 복사 버튼", 'id="pmCopy"' in src)
    check("카드 이미지 버튼", 'id="pmCard"' in src)
    check("Canvas 사용", "createElement('canvas')" in src and "toBlob" in src)
    check("야간 근무 안내", "야간 근무" in src)
    check("환산 4종", src.count("pm-conv") >= 4, src.count("pm-conv"))
    check("prefers-reduced-motion", "prefers-reduced-motion" in src)
    check("PC 2단 레이아웃", "grid-template-columns: minmax(0, 1fr) 330px" in src)
    check("모바일 1단", "@media (max-width: 900px)" in src)

    match = re.search(r'<script[^>]*id="pmConfig"[^>]*>(.*?)</script>', src, re.S)
    check("설정 블록 1개", match is not None)
    if match:
        config = json.loads(match.group(1))
        check("월 소정근로 209", config["monthlyHours"] == pm.MONTHLY_HOURS, config["monthlyHours"])
        check("저장 키 일치", config["storeKey"] == "secjobs-paymeter-v1", config["storeKey"])
        check("환산 가격 일치",
              [(row["name"], row["price"]) for row in config["conversions"]] == pm.CONVERSIONS,
              config["conversions"])
        check("기본 상태 일치", config["defaults"] == pm.DEFAULT_STATE, config["defaults"])
        check("기본 연봉 4,200만", config["defaults"]["amount"] == 42000000)
        check("기본 근무 월~금", config["defaults"]["workdays"] == [1, 2, 3, 4, 5])
    check("공통 셸 페이지 등록", "paymeter" in ui_shell.PAGE_LABEL, ui_shell.PAGE_LABEL.get("paymeter"))


def main():
    check_calc()
    check_receipt()
    check_html()
    print()
    if failures:
        print("실패 %d건" % len(failures))
        for name in failures:
            print("  - %s" % name)
        return 1
    print("월급 미터 검증 통과 (연봉·월급·시급 환산 · 점심 무급/유급 · 야간 근무 · 26페이지 셸)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

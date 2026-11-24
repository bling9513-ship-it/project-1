#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실시간 월급·퇴근 미터(paymeter.html).

무엇을 하나
  · 급여 방식(연봉·월급·시급)과 근무 시간(출근·퇴근·점심)을 넣으면, 지금까지 번 돈을
    1초마다 올라가는 카운터로 보여 준다. 설정은 localStorage(`secjobs-paymeter-v1`)에 남는다.
  · 근무 진행률 바(점심시간 구간 표시) · 퇴근까지/점심까지 남은 시간 · 실근무 시간 · 하루 총액.
  · 오늘 번 돈을 아메리카노·국밥·치킨·영화 한 편으로 환산해 체감시킨다(기준 가격은 화면에 명시).
  · 출근 전 / 근무 중 / 점심시간 / 퇴근 후 / 비근무일(주말) 상태를 자연스럽게 바꿔 보여 준다.
  · 단톡방 공유용 '오늘의 근무 영수증' 텍스트 복사, 1080×1350 Canvas 카드 이미지 저장(모두 로컬 처리).

지키는 것
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 좌측 미터 + 우측 설정 레일 / 모바일(390px) 미터 먼저, 설정은 접어서 아래에
  · 급여 환산은 한국 노동 실무에서 쓰는 기준(월 소정근로 209시간, 주 5일)을 화면에 그대로 적는다.
    실제 급여와 다를 수 있으므로 '참고 계산'임을 분명히 한다.
"""
import json
import os
from datetime import datetime, timedelta, timezone

from html_guard import harden_html
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(BASE_DIR, "paymeter.html")
KST = timezone(timedelta(hours=9))

MONTHLY_HOURS = 209.0          # 주 40시간 · 주휴 포함 월 소정근로시간
DEFAULT_STATE = {
    "mode": "annual",          # annual | monthly | hourly
    "amount": 42000000,
    "start": "09:00",
    "end": "18:00",
    "lunchStart": "12:00",
    "lunchMin": 60,
    "lunchPaid": False,
    "workdays": [1, 2, 3, 4, 5],   # 0=일 … 6=토
}
CONVERSIONS = [
    ("아메리카노", 4500),
    ("국밥", 9500),
    ("치킨", 21000),
    ("영화 한 편", 15000),
]
WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"]


# ---------------------------------------------------------------------------
# 계산 (화면과 같은 규칙 — 테스트가 이 함수들을 직접 검증한다)
# ---------------------------------------------------------------------------
def to_minutes(hhmm):
    """'09:30' → 570분."""
    hour, minute = str(hhmm).split(":")
    hour, minute = int(hour), int(minute)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("시각 형식이 잘못되었습니다: %r" % hhmm)
    return hour * 60 + minute


def hourly_wage(mode, amount):
    """급여 방식별 시급 환산. 연봉 → 월급 ÷ 209, 월급 → ÷ 209."""
    amount = float(amount)
    if amount <= 0:
        return 0.0
    if mode == "hourly":
        return amount
    if mode == "monthly":
        return amount / MONTHLY_HOURS
    return amount / 12.0 / MONTHLY_HOURS


def shift_span(start, end):
    """출근·퇴근 시각 → (시작 분, 종료 분, 야간 여부). 퇴근이 출근보다 빠르면 다음 날 퇴근."""
    begin = to_minutes(start)
    finish = to_minutes(end)
    overnight = finish <= begin
    if overnight:
        finish += 24 * 60
    return begin, finish, overnight


def work_minutes(start, end, lunch_min, lunch_paid):
    """하루 실근무 분. 점심이 무급이면 점심 시간을 뺀다."""
    begin, finish, _ = shift_span(start, end)
    span = finish - begin
    return max(0, span - (0 if lunch_paid else int(lunch_min)))


def daily_pay(mode, amount, start, end, lunch_min, lunch_paid):
    """하루 실근무 기준 총액(원)."""
    return hourly_wage(mode, amount) * work_minutes(start, end, lunch_min, lunch_paid) / 60.0


def worked_minutes(now_min, start, end, lunch_start, lunch_min, lunch_paid):
    """근무일 기준 '지금까지' 실근무 분. 출근 전 0, 퇴근 후 하루 실근무."""
    begin, finish, overnight = shift_span(start, end)
    now = now_min
    if overnight and now < begin:
        now += 24 * 60
    now = min(max(now, begin), finish)
    elapsed = now - begin
    lunch_begin = to_minutes(lunch_start)
    if overnight and lunch_begin < begin:
        lunch_begin += 24 * 60
    lunch_end = lunch_begin + int(lunch_min)
    if not lunch_paid:
        overlap = max(0, min(now, lunch_end) - max(begin, lunch_begin))
        if now > lunch_end:
            overlap = int(lunch_min)
        elapsed -= overlap
    return max(0, elapsed)


def phase_at(now_min, start, end, lunch_start, lunch_min):
    """지금이 근무 흐름의 어디인지: before · morning · lunch · afternoon · after."""
    begin, finish, overnight = shift_span(start, end)
    now = now_min
    if overnight and now < begin:
        now += 24 * 60
    lunch_begin = to_minutes(lunch_start)
    if overnight and lunch_begin < begin:
        lunch_begin += 24 * 60
    lunch_end = lunch_begin + int(lunch_min)
    if now < begin:
        return "before"
    if now >= finish:
        return "after"
    if to_minutes(lunch_start) and lunch_min and lunch_begin <= now < lunch_end:
        return "lunch"
    return "morning" if now < lunch_begin else "afternoon"


def fmt_won(value):
    return "{:,}".format(int(round(value)))


def fmt_duration(minutes):
    minutes = int(max(0, round(minutes)))
    hours, mins = divmod(minutes, 60)
    if hours:
        return "%d시간 %d분" % (hours, mins)
    return "%d분" % mins


def receipt_lines(state, now_kst):
    """영수증 텍스트 (단톡방 복사용). now_kst 는 시간대가 붙은 datetime."""
    hourly = hourly_wage(state["mode"], state["amount"])
    worked = worked_minutes(now_kst.hour * 60 + now_kst.minute, state["start"], state["end"],
                            state["lunchStart"], state["lunchMin"], state["lunchPaid"])
    earned = hourly * worked / 60.0
    total_work = work_minutes(state["start"], state["end"], state["lunchMin"], state["lunchPaid"])
    phase = phase_at(now_kst.hour * 60 + now_kst.minute, state["start"], state["end"],
                     state["lunchStart"], state["lunchMin"])
    lunch_note = "점심 %d분%s" % (int(state["lunchMin"]),
                                 " (유급)" if state["lunchPaid"] else " (무급)")
    header = "오늘의 근무 영수증 · %s (%s)" % (now_kst.strftime("%Y-%m-%d"), WEEKDAYS[(now_kst.weekday() + 1) % 7])
    lines = [
        header,
        "출근 %s · 퇴근 %s · %s" % (state["start"], state["end"], lunch_note),
        "실근무 %s / %s" % (fmt_duration(worked), fmt_duration(total_work)),
        "지금까지 %s원 (하루 %s원)" % (fmt_won(earned), fmt_won(hourly * total_work / 60.0)),
        " · ".join("%s %s" % (name, ("%.1f" % (earned / price)).rstrip("0").rstrip("."))
                   for name, price in CONVERSIONS[:3]),
    ]
    if phase == "after":
        lines.append("오늘 근무 끝 · 수고하셨습니다")
    else:
        remain = max(0, shift_span(state["start"], state["end"])[1] - (now_kst.hour * 60 + now_kst.minute))
        lines.append("퇴근까지 %s 남음" % fmt_duration(remain))
    return lines


# ---------------------------------------------------------------------------
# 스타일 · 템플릿 · 스크립트
# ---------------------------------------------------------------------------
CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --bg-page: #f8fafc;  --bg-surface: #ffffff;  --bg-subtle: #f1f5f9;  --bg-muted: #e2e8f0;
      --border-subtle: #f1f5f9;  --border-default: #e2e8f0;  --border-strong: #cbd5e1;
      --text-primary: #0f172a;  --text-secondary: #475569;  --text-muted: #94a3b8;
      --accent-primary: #2563eb;  --accent-subtle: #eff6ff;
      --money: #0f766e;  --money-soft: #ecfdf5;  --money-border: #a7f3d0;
      --warn-bg: #fffbeb;  --warn-text: #b45309;  --warn-border: #fde68a;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --money: #5eead4;  --money-soft: rgba(16, 185, 129, 0.12);  --money-border: rgba(16, 185, 129, 0.32);
      --warn-bg: rgba(245, 158, 11, 0.14);  --warn-text: #fcd34d;  --warn-border: rgba(245, 158, 11, 0.34);
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body { font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease; }
    .pm-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .pm-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 96px; }
    .pm-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .pm-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 640px; word-break: keep-all; }
    .pm-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .pm-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px;
      font-size: 11.5px; color: var(--text-muted); }
    .pm-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }

    .pm-grid { display: grid; grid-template-columns: minmax(0, 1fr) 330px; gap: 16px; margin-top: 16px; align-items: start; }
    .pm-panel { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 18px; box-shadow: var(--card-shadow); }
    .pm-panel h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.01em; }

    .pm-meter { padding: 20px; }
    .pm-meter-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
    .pm-meter-head h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); }
    .pm-state { margin-top: 3px; font-size: 12.5px; color: var(--text-secondary); word-break: keep-all; }
    .pm-badge { flex: 0 0 auto; font-size: 11px; font-weight: 700; border-radius: 999px; padding: 4px 10px;
      background: var(--bg-subtle); color: var(--text-secondary); border: 1px solid var(--border-default); }
    .pm-badge.is-live { background: var(--money-soft); color: var(--money); border-color: var(--money-border); }
    .pm-badge.is-warn { background: var(--warn-bg); color: var(--warn-text); border-color: var(--warn-border); }

    .pm-amount { display: flex; align-items: baseline; gap: 5px; margin-top: 14px; }
    .pm-amount strong { font-size: 46px; font-weight: 800; letter-spacing: -0.05em; font-variant-numeric: tabular-nums;
      color: var(--text-primary); line-height: 1.05; }
    .pm-amount span { font-size: 17px; font-weight: 700; color: var(--text-secondary); }
    .pm-sub { margin-top: 6px; font-size: 12px; color: var(--text-muted); }

    .pm-progress { position: relative; height: 12px; margin-top: 16px; border-radius: 999px; overflow: hidden;
      background: var(--bg-subtle); border: 1px solid var(--border-default); }
    .pm-bar { display: block; height: 100%; width: 0%; background: var(--money); border-radius: 999px;
      transition: width .35s cubic-bezier(0.2, 0.8, 0.2, 1); }
    /* 점심시간 구간 — 바를 가리지 않도록 위아래를 잇는 점선 두 줄로만 표시한다(그라데이션 없음). */
    .pm-band { display: block; position: absolute; top: -2px; bottom: -2px; border-left: 1px dashed var(--border-strong);
      border-right: 1px dashed var(--border-strong); pointer-events: none; }
    .pm-legend { display: flex; flex-wrap: wrap; gap: 4px 10px; margin-top: 7px; font-size: 10.5px;
      color: var(--text-muted); }
    .pm-legend span { display: inline-flex; align-items: center; gap: 4px; }
    .pm-legend i { width: 8px; height: 8px; border-radius: 2px; display: inline-block; }
    .pm-legend i.pm-legend-band { background: transparent; border-left: 1px dashed var(--border-strong);
      border-right: 1px dashed var(--border-strong); width: 7px; border-radius: 0; }

    .pm-kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin-top: 16px;
      padding-top: 14px; border-top: 1px solid var(--border-subtle); }
    .pm-kpis span { display: block; font-size: 10.5px; color: var(--text-muted); }
    .pm-kpis b { display: block; margin-top: 2px; font-size: 15px; font-weight: 800; letter-spacing: -0.03em;
      font-variant-numeric: tabular-nums; }
    .pm-kpis b.is-live { color: var(--money); }

    .pm-convert { margin-top: 16px; }
    .pm-convert h3 { font-size: 11px; font-weight: 700; color: var(--text-muted); }
    .pm-convert-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 7px; margin-top: 7px; }
    .pm-conv { border: 1px solid var(--border-default); border-radius: 11px; padding: 8px 9px; background: var(--bg-subtle); }
    .pm-conv b { display: block; font-size: 14px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .pm-conv span { display: block; margin-top: 1px; font-size: 10px; color: var(--text-muted); }
    .pm-conv em { display: block; font-style: normal; font-size: 9.5px; color: var(--text-muted); margin-top: 1px; }

    .pm-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
    .pm-btn { border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      border-radius: 10px; padding: 9px 14px; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer;
      transition: background-color .15s ease, color .15s ease, border-color .15s ease; }
    .pm-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .pm-btn:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .pm-btn.pm-primary { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }
    .pm-btn.pm-primary:hover { opacity: .88; background: var(--text-primary); color: var(--bg-surface); }
    .pm-status { min-height: 16px; margin-top: 8px; font-size: 11px; font-weight: 600; color: var(--money); }

    .pm-rail { display: grid; gap: 12px; position: sticky; top: 76px; }
    .pm-setting-row { margin-top: 12px; }
    .pm-setting-row > label, .pm-setting-row > .pm-label { display: block; font-size: 11px; font-weight: 700;
      color: var(--text-secondary); margin-bottom: 5px; }
    .pm-seg { display: flex; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 11px; }
    .pm-seg button { flex: 1 1 0; border: 0; background: transparent; color: var(--text-secondary); cursor: pointer;
      font-family: inherit; font-size: 12px; font-weight: 700; padding: 7px 4px; border-radius: 8px; }
    .pm-seg button.is-on { background: var(--bg-surface); color: var(--text-primary); box-shadow: var(--card-shadow); }
    .pm-seg button:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .pm-input { width: 100%; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-primary);
      border-radius: 10px; padding: 9px 11px; font-family: inherit; font-size: 14px; font-weight: 700;
      font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
    .pm-input:focus { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .pm-input-hint { margin-top: 4px; font-size: 10.5px; color: var(--text-muted); }
    .pm-time-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
    .pm-time-grid label { display: block; font-size: 10.5px; color: var(--text-muted); margin-bottom: 3px; }
    .pm-days { display: flex; gap: 4px; }
    .pm-day { flex: 1 1 0; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 9px; padding: 7px 0; font-family: inherit; font-size: 11.5px;
      font-weight: 700; cursor: pointer; }
    .pm-day.is-on { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }
    .pm-day:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .pm-check { display: flex; align-items: center; gap: 7px; margin-top: 9px; font-size: 11.5px; color: var(--text-secondary); }
    .pm-check input { width: 15px; height: 15px; accent-color: var(--accent-primary); }
    .pm-reset { margin-top: 13px; width: 100%; }
    .pm-howto p { margin-top: 9px; font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .pm-howto b { color: var(--text-primary); }
    .pm-warn { margin-top: 10px; border-radius: 11px; padding: 9px 11px; background: var(--warn-bg);
      border: 1px solid var(--warn-border); color: var(--warn-text); font-size: 11px; line-height: 1.55; }

    .pm-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .pm-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; color: var(--text-primary); }
    .pm-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .pm-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .pm-notes li b { color: var(--text-primary); }
    .pm-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 900px) {
      .pm-wrap { padding: 14px 13px 88px; }
      .pm-hero h1 { font-size: 21px; }
      .pm-hero p { font-size: 12px; }
      .pm-grid { display: flex; flex-direction: column; gap: 10px; margin-top: 13px; }
      .pm-meter { order: 1; padding: 16px; }
      .pm-rail { order: 2; position: static; width: 100%; }
      .pm-amount strong { font-size: 38px; }
      .pm-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
      .pm-convert-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .pm-actions .pm-btn { flex: 1 1 44%; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
      .pm-bar { transition: none; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 실시간 월급·퇴근 미터</title>
  <meta name="description" content="연봉·월급·시급과 출퇴근 시간을 넣으면 지금까지 번 돈을 1초마다 계산합니다. 근무 진행률, 퇴근까지 남은 시간, 오늘의 근무 영수증 복사와 카드 이미지 저장까지 브라우저 안에서 처리합니다.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" integrity="sha384-SN6A48CJQjx946+DRb8wsoifC4a8ur9ZS6R+HCTgnBHOKCa6GLXAR3Qn8d1jztxg" crossorigin="anonymous" />
  <style>__CSS__</style>
  <script>
    (function () {
      try {
        var saved = localStorage.getItem('secjobs-theme');
        if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.setAttribute('data-theme', 'dark');
        }
      } catch (e) {}
    })();
  </script>
</head>
<body>

  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
      </div>
      <div class="nav-actions">
        <div class="update-meta"><span class="live-dot"></span><span>브라우저 안에서만 계산</span></div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="화면 테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
        </button>
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기" aria-label="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path></svg>
        </a>
      </div>
    </div>
  </header>

  <main class="pm-wrap">
    <section class="pm-hero">
      <span class="pm-pill">생활 · 실시간 월급 미터</span>
      <h1>지금 이 순간, 얼마 벌었을까</h1>
      <p>급여와 출퇴근 시간을 넣으면 오늘 번 돈이 1초마다 올라갑니다. 점심시간은 빼고 계산하고, 퇴근까지 남은 시간과 체감 환산까지 함께 보여 줍니다. 설정은 이 브라우저에만 저장됩니다.</p>
      <div class="pm-meta">
        <span id="pmMetaMode">연봉 기준</span>
        <span class="pm-dot"></span>
        <span>시급 환산 = 급여 ÷ 209시간</span>
        <span class="pm-dot"></span>
        <span>서버 전송 없음</span>
      </div>
    </section>

    <div class="pm-grid">
      <section class="pm-panel pm-meter" aria-labelledby="pmMeterTitle">
        <div class="pm-meter-head">
          <div>
            <h2 id="pmMeterTitle">오늘 번 돈</h2>
            <p class="pm-state" id="pmStateText">설정을 확인하는 중입니다</p>
          </div>
          <span class="pm-badge" id="pmBadge">계산 중</span>
        </div>

        <p class="pm-amount"><strong id="pmEarned">0</strong><span>원</span></p>
        <p class="pm-sub" id="pmSubLine">출근 전입니다.</p>

        <div class="pm-progress" role="img" aria-labelledby="pmProgressLabel">
          <span class="pm-bar" id="pmBar"></span>
          <span class="pm-band" id="pmBand"></span>
        </div>
        <p class="pm-sr" id="pmProgressLabel">근무 진행률</p>
        <div class="pm-legend">
          <span><i style="background:var(--money)"></i>근무한 시간 <b id="pmLegendRate">0%</b></span>
          <span><i class="pm-legend-band"></i>점심시간</span>
          <span><i style="background:var(--bg-subtle);border:1px solid var(--border-default)"></i>남은 시간</span>
        </div>

        <div class="pm-kpis">
          <div><span>지금까지 실근무</span><b id="pmWorked">0분</b></div>
          <div><span>남은 근무</span><b id="pmRemain">0분</b></div>
          <div><span>퇴근까지</span><b id="pmCountdown">0분</b></div>
          <div><span>하루 총액</span><b id="pmDaily">0원</b></div>
        </div>

        <div class="pm-convert">
          <h3>오늘 번 돈으로 바꾸면</h3>
          <div class="pm-convert-row" id="pmConvertRow"></div>
        </div>

        <div class="pm-actions">
          <button type="button" class="pm-btn pm-primary" id="pmCopy">영수증 복사</button>
          <button type="button" class="pm-btn" id="pmCard">카드 이미지 저장</button>
          <button type="button" class="pm-btn" id="pmReset">기본값으로</button>
        </div>
        <p class="pm-status" id="pmActionStatus" role="status" aria-live="polite"></p>
      </section>

      <aside class="pm-rail" aria-label="급여·근무 설정">
        <section class="pm-panel">
          <h2>급여·근무 설정</h2>

          <div class="pm-setting-row">
            <span class="pm-label" id="pmModeLabel">급여 방식</span>
            <div class="pm-seg" id="pmModeSeg" role="group" aria-labelledby="pmModeLabel">
              <button type="button" data-mode="annual" class="is-on" aria-pressed="true">연봉</button>
              <button type="button" data-mode="monthly" aria-pressed="false">월급</button>
              <button type="button" data-mode="hourly" aria-pressed="false">시급</button>
            </div>
          </div>

          <div class="pm-setting-row">
            <label for="pmAmount">금액</label>
            <input class="pm-input" id="pmAmount" type="text" inputmode="numeric" autocomplete="off" value="42,000,000">
            <p class="pm-input-hint" id="pmAmountHint">세전 연봉을 원 단위로 넣으세요.</p>
          </div>

          <div class="pm-setting-row">
            <span class="pm-label">근무 시간</span>
            <div class="pm-time-grid">
              <div><label for="pmStart">출근</label><input class="pm-input" id="pmStart" type="time" value="09:00"></div>
              <div><label for="pmEnd">퇴근</label><input class="pm-input" id="pmEnd" type="time" value="18:00"></div>
              <div><label for="pmLunchStart">점심 시작</label><input class="pm-input" id="pmLunchStart" type="time" value="12:00"></div>
              <div><label for="pmLunchMin">점심 길이(분)</label><input class="pm-input" id="pmLunchMin" type="number" min="0" max="240" step="10" value="60"></div>
            </div>
          </div>

          <label class="pm-check" for="pmLunchPaid">
            <input type="checkbox" id="pmLunchPaid">
            <span>점심시간도 급여에 포함(유급)</span>
          </label>

          <div class="pm-setting-row">
            <span class="pm-label">근무 요일</span>
            <div class="pm-days" id="pmDays" role="group" aria-label="근무 요일"></div>
          </div>

          <p class="pm-warn" id="pmWarn" hidden></p>
        </section>

        <section class="pm-panel pm-howto">
          <h2>계산 방식</h2>
          <p><b>월 소정근로 209시간</b>은 주 40시간 + 주휴 8시간을 한 달 평균으로 환산한 값입니다. 연봉·월급은 이 값으로 나눠 시급을 구합니다.</p>
          <p><b>오늘 번 돈</b> = 시급 × 지금까지 실근무 시간. 점심이 무급이면 그만큼 빼고 셉니다.</p>
          <p><b>퇴근이 출근보다 이른 경우</b>는 야간 근무로 보고 다음 날 퇴근으로 계산합니다.</p>
          <p><b>환산 금액</b>은 화면에 적힌 기준 가격으로 나눈 값입니다. 실제 지출과는 다릅니다.</p>
        </section>
      </aside>
    </div>

    <section class="pm-notes">
      <h2>알아 두실 점</h2>
      <ul>
        <li><b>참고 계산</b> — 세전 기준의 단순 환산입니다. 실제 급여는 수당·비과세·4대보험·소득세·연장근로 가산에 따라 달라집니다.</li>
        <li><b>저장 위치</b> — 급여·근무 시간 설정은 이 브라우저의 localStorage(`secjobs-paymeter-v1`)에만 남고 서버로 보내지 않습니다. 공용 기기에서는 '기본값으로'를 눌러 지우세요.</li>
        <li><b>영수증·카드</b> — 복사 문구와 카드 이미지는 브라우저에서 만들어집니다. 카드는 1080×1350 PNG로 저장됩니다.</li>
        <li><b>시각 기준</b> — 기기 시계를 그대로 씁니다. 시간대가 다른 곳에 있다면 기기 시간대를 먼저 확인하세요.</li>
      </ul>
    </section>
    <p class="pm-foot">급여·근무 시간은 브라우저 안에서만 계산합니다 · 화면의 환산 금액은 기준 가격으로 나눈 참고치입니다.</p>
  </main>

  <script type="application/json" id="pmConfig">__CONFIG_JSON__</script>
  <script>__JS__</script>
</body>
</html>
"""

JS = r"""
(function () {
  // ---------- 화면 테마 (공통 셸 헤더의 토글) ----------
  var themeBtn = document.getElementById('themeToggle');
  var moonIcon = document.getElementById('moonIcon');
  var sunIcon = document.getElementById('sunIcon');
  function applyTheme(dark, persist) {
    if (dark) document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    if (moonIcon) moonIcon.style.display = dark ? 'none' : 'block';
    if (sunIcon) sunIcon.style.display = dark ? 'block' : 'none';
    if (persist) {
      try { localStorage.setItem('secjobs-theme', dark ? 'dark' : 'light'); } catch (e) {}
    }
  }
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      applyTheme(document.documentElement.getAttribute('data-theme') !== 'dark', true);
    });
  }
  (function initTheme() {
    var saved = null;
    try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
    applyTheme(saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches), false);
  })();

  var CONFIG;
  try { CONFIG = JSON.parse(document.getElementById('pmConfig').textContent); } catch (e) { return; }

  var STORE_KEY = CONFIG.storeKey;
  var MONTHLY_HOURS = CONFIG.monthlyHours;
  var CONVERSIONS = CONFIG.conversions;
  var WEEKDAYS = CONFIG.weekdays;
  var DEFAULTS = CONFIG.defaults;

  var state = loadState();
  var els = {
    amount: document.getElementById('pmAmount'),
    amountHint: document.getElementById('pmAmountHint'),
    start: document.getElementById('pmStart'),
    end: document.getElementById('pmEnd'),
    lunchStart: document.getElementById('pmLunchStart'),
    lunchMin: document.getElementById('pmLunchMin'),
    lunchPaid: document.getElementById('pmLunchPaid'),
    days: document.getElementById('pmDays'),
    modeSeg: document.getElementById('pmModeSeg'),
    warn: document.getElementById('pmWarn'),
    earned: document.getElementById('pmEarned'),
    stateText: document.getElementById('pmStateText'),
    badge: document.getElementById('pmBadge'),
    subLine: document.getElementById('pmSubLine'),
    bar: document.getElementById('pmBar'),
    band: document.getElementById('pmBand'),
    legendRate: document.getElementById('pmLegendRate'),
    worked: document.getElementById('pmWorked'),
    remain: document.getElementById('pmRemain'),
    countdown: document.getElementById('pmCountdown'),
    daily: document.getElementById('pmDaily'),
    convertRow: document.getElementById('pmConvertRow'),
    metaMode: document.getElementById('pmMetaMode'),
    status: document.getElementById('pmActionStatus'),
    copy: document.getElementById('pmCopy'),
    card: document.getElementById('pmCard'),
    reset: document.getElementById('pmReset')
  };

  // ---------- 상태 저장 ----------
  function loadState() {
    var base = {
      mode: DEFAULTS.mode, amount: DEFAULTS.amount, start: DEFAULTS.start, end: DEFAULTS.end,
      lunchStart: DEFAULTS.lunchStart, lunchMin: DEFAULTS.lunchMin, lunchPaid: DEFAULTS.lunchPaid,
      workdays: DEFAULTS.workdays.slice()
    };
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); } catch (e) { raw = null; }
    if (!raw || typeof raw !== 'object') return base;
    if (raw.mode === 'annual' || raw.mode === 'monthly' || raw.mode === 'hourly') base.mode = raw.mode;
    if (typeof raw.amount === 'number' && raw.amount > 0 && raw.amount < 1e10) base.amount = Math.round(raw.amount);
    ['start', 'end', 'lunchStart'].forEach(function (key) {
      if (typeof raw[key] === 'string' && /^\d{2}:\d{2}$/.test(raw[key])) base[key] = raw[key];
    });
    if (typeof raw.lunchMin === 'number' && raw.lunchMin >= 0 && raw.lunchMin <= 240) base.lunchMin = Math.round(raw.lunchMin);
    if (typeof raw.lunchPaid === 'boolean') base.lunchPaid = raw.lunchPaid;
    if (Array.isArray(raw.workdays)) {
      var days = raw.workdays.filter(function (d) { return typeof d === 'number' && d >= 0 && d <= 6; });
      base.workdays = days.length ? days : DEFAULTS.workdays.slice();
    }
    return base;
  }

  function saveState() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  // ---------- 계산 (빌드 단계의 파이썬 함수와 같은 규칙) ----------
  function toMinutes(hhmm) {
    var parts = String(hhmm).split(':');
    return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
  }

  function hourlyWage() {
    var amount = Number(state.amount) || 0;
    if (amount <= 0) return 0;
    if (state.mode === 'hourly') return amount;
    if (state.mode === 'monthly') return amount / MONTHLY_HOURS;
    return amount / 12 / MONTHLY_HOURS;
  }

  function shiftSpan() {
    var begin = toMinutes(state.start);
    var finish = toMinutes(state.end);
    var overnight = finish <= begin;
    if (overnight) finish += 1440;
    return { begin: begin, finish: finish, overnight: overnight };
  }

  function totalWorkMinutes() {
    var span = shiftSpan();
    var lunch = state.lunchPaid ? 0 : Math.max(0, state.lunchMin | 0);
    return Math.max(0, span.finish - span.begin - lunch);
  }

  function workedMinutes(nowMin) {
    var span = shiftSpan();
    var now = nowMin;
    if (span.overnight && now < span.begin) now += 1440;
    now = Math.min(Math.max(now, span.begin), span.finish);
    var elapsed = now - span.begin;
    var lunchBegin = toMinutes(state.lunchStart);
    if (span.overnight && lunchBegin < span.begin) lunchBegin += 1440;
    var lunchEnd = lunchBegin + Math.max(0, state.lunchMin | 0);
    if (!state.lunchPaid) {
      var overlap = Math.max(0, Math.min(now, lunchEnd) - Math.max(span.begin, lunchBegin));
      if (now > lunchEnd) overlap = Math.max(0, state.lunchMin | 0);
      elapsed -= overlap;
    }
    return Math.max(0, elapsed);
  }

  function phaseAt(nowMin) {
    var span = shiftSpan();
    var now = nowMin;
    if (span.overnight && now < span.begin) now += 1440;
    var lunchBegin = toMinutes(state.lunchStart);
    if (span.overnight && lunchBegin < span.begin) lunchBegin += 1440;
    var lunchEnd = lunchBegin + Math.max(0, state.lunchMin | 0);
    if (now < span.begin) return 'before';
    if (now >= span.finish) return 'after';
    if ((state.lunchMin | 0) > 0 && lunchBegin <= now && now < lunchEnd) return 'lunch';
    return now < lunchBegin ? 'morning' : 'afternoon';
  }

  function fmtWon(value) { return Math.round(value).toLocaleString('ko-KR'); }

  function fmtDuration(minutes) {
    var total = Math.max(0, Math.round(minutes));
    var hours = Math.floor(total / 60);
    var mins = total % 60;
    return hours ? hours + '시간 ' + mins + '분' : mins + '분';
  }

  function fmtClock(minutes) {
    var total = Math.max(0, Math.round(minutes));
    var hours = Math.floor(total / 60);
    var mins = total % 60;
    if (hours) return hours + '시간 ' + mins + '분';
    return mins + '분';
  }

  function dayName(index) { return WEEKDAYS[index]; }

  function isWorkday(date) {
    return state.workdays.indexOf(date.getDay()) >= 0;
  }

  function nextWorkdayInfo(now) {
    for (var step = 1; step <= 7; step += 1) {
      var probe = new Date(now.getTime() + step * 86400000);
      if (isWorkday(probe)) {
        var startMin = toMinutes(state.start);
        var target = new Date(probe.getFullYear(), probe.getMonth(), probe.getDate(),
          Math.floor(startMin / 60), startMin % 60, 0, 0);
        return { date: probe, minutes: Math.max(0, (target - now) / 60000) };
      }
    }
    return null;
  }

  // ---------- 화면 ----------
  function renderDays() {
    els.days.innerHTML = '';
    WEEKDAYS.forEach(function (label, index) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'pm-day' + (state.workdays.indexOf(index) >= 0 ? ' is-on' : '');
      btn.textContent = label;
      btn.dataset.day = String(index);
      btn.setAttribute('aria-pressed', state.workdays.indexOf(index) >= 0 ? 'true' : 'false');
      btn.setAttribute('aria-label', label + '요일 근무' + (state.workdays.indexOf(index) >= 0 ? ' 포함' : ' 제외'));
      els.days.appendChild(btn);
    });
  }

  function renderModeSeg() {
    Array.prototype.forEach.call(els.modeSeg.querySelectorAll('button'), function (btn) {
      var on = btn.dataset.mode === state.mode;
      btn.classList.toggle('is-on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    els.metaMode.textContent = state.mode === 'annual' ? '연봉 기준'
      : state.mode === 'monthly' ? '월급 기준' : '시급 기준';
    els.amountHint.textContent = state.mode === 'annual' ? '세전 연봉을 원 단위로 넣으세요.'
      : state.mode === 'monthly' ? '세전 월급을 원 단위로 넣으세요.'
      : '세전 시급을 원 단위로 넣으세요.';
  }

  function renderConversions(earned) {
    els.convertRow.innerHTML = '';
    CONVERSIONS.forEach(function (item) {
      var count = item.price ? earned / item.price : 0;
      var cell = document.createElement('div');
      cell.className = 'pm-conv';
      var value = document.createElement('b');
      value.textContent = (count >= 100 ? Math.round(count) : Math.round(count * 10) / 10).toLocaleString('ko-KR') + '개';
      var name = document.createElement('span');
      name.textContent = item.name;
      var price = document.createElement('em');
      price.textContent = '기준 ' + fmtWon(item.price) + '원';
      cell.appendChild(value);
      cell.appendChild(name);
      cell.appendChild(price);
      els.convertRow.appendChild(cell);
    });
  }

  function validate() {
    var messages = [];
    var span = shiftSpan();
    if (span.finish - span.begin < 30) messages.push('근무 시간이 30분보다 짧습니다. 출근·퇴근 시각을 확인하세요.');
    if ((state.lunchMin | 0) >= span.finish - span.begin) messages.push('점심 시간이 근무 시간보다 깁니다. 점심 길이를 줄여 주세요.');
    if (Number(state.amount) <= 0) messages.push('금액을 0보다 크게 넣어 주세요.');
    if (messages.length) {
      els.warn.textContent = messages.join(' ');
      els.warn.hidden = false;
    } else {
      els.warn.hidden = true;
      els.warn.textContent = '';
    }
    return messages.length === 0;
  }

  function render(now) {
    var span = shiftSpan();
    var nowMin = now.getHours() * 60 + now.getMinutes() + now.getSeconds() / 60;
    var hourly = hourlyWage();
    var workTotal = totalWorkMinutes();
    var workday = isWorkday(now);
    // 비근무일에는 시계를 돌리지 않는다 — 오늘 번 돈은 0원.
    var workdone = workday ? workedMinutes(nowMin) : 0;
    var earned = hourly * workdone / 60;
    var phase = workday ? phaseAt(nowMin) : 'dayoff';
    var progress = workTotal > 0 ? Math.min(1, workdone / workTotal) : 0;

    els.earned.textContent = fmtWon(earned);
    els.bar.style.width = (progress * 100).toFixed(2) + '%';
    els.legendRate.textContent = Math.round(progress * 100) + '%';
    els.worked.textContent = fmtDuration(workdone);
    els.daily.textContent = fmtWon(hourly * workTotal / 60) + '원';
    els.remain.textContent = fmtDuration(Math.max(0, workTotal - workdone));

    // 점심시간 띠: 하루 근무 구간에서 점심이 차지하는 위치
    var spanLen = Math.max(1, span.finish - span.begin);
    var lunchBegin = toMinutes(state.lunchStart);
    if (span.overnight && lunchBegin < span.begin) lunchBegin += 1440;
    if ((state.lunchMin | 0) > 0 && lunchBegin >= span.begin && lunchBegin < span.finish) {
      var left = (lunchBegin - span.begin) / spanLen * 100;
      var width = Math.min(100 - left, (state.lunchMin | 0) / spanLen * 100);
      els.band.style.left = left.toFixed(2) + '%';
      els.band.style.width = Math.max(0, width).toFixed(2) + '%';
      els.band.hidden = false;
    } else {
      els.band.hidden = true;
    }

    renderConversions(earned);

    var badge = els.badge;
    badge.className = 'pm-badge';
    if (!workday) {
      badge.textContent = '비근무일';
      var next = nextWorkdayInfo(now);
      els.stateText.textContent = next
        ? dayName(next.date.getDay()) + '요일 ' + state.start + ' 출근까지 ' + fmtDuration(next.minutes)
        : '근무 요일이 하나도 없습니다. 근무 요일을 골라 주세요.';
      els.subLine.textContent = '오늘은 근무일이 아닙니다 · 하루 총액 ' + fmtWon(hourly * workTotal / 60) + '원 기준';
      els.countdown.textContent = next ? fmtDuration(next.minutes) : '—';
    } else if (phase === 'before') {
      badge.textContent = '출근 전';
      els.stateText.textContent = '출근까지 ' + fmtDuration(span.begin - nowMin);
      els.subLine.textContent = state.start + ' 출근 · ' + state.end + ' 퇴근 · 하루 ' + fmtWon(hourly * workTotal / 60) + '원';
      els.countdown.textContent = fmtDuration(span.begin - nowMin);
    } else if (phase === 'lunch') {
      badge.className = 'pm-badge is-warn';
      badge.textContent = state.lunchPaid ? '점심시간(유급)' : '점심시간';
      var lunchEndMin = lunchBegin + (state.lunchMin | 0);
      els.stateText.textContent = '점심시간 · ' + fmtDuration(lunchEndMin - nowMin) + ' 남음' +
        (state.lunchPaid ? ' · 유급이라 계속 올라갑니다' : ' · 무급이라 잠시 멈춥니다');
      els.subLine.textContent = '실근무 ' + fmtDuration(workdone) + ' / ' + fmtDuration(workTotal);
      els.countdown.textContent = fmtDuration(Math.max(0, span.finish - nowMin));
    } else if (phase === 'after') {
      badge.textContent = '퇴근 완료';
      els.stateText.textContent = '오늘 근무가 끝났습니다 · 하루 ' + fmtWon(hourly * workTotal / 60) + '원';
      els.subLine.textContent = '내일도 같은 시간이면 ' + state.start + ' 출근 · 영수증을 복사해 두세요';
      els.countdown.textContent = '0분';
    } else {
      badge.className = 'pm-badge is-live';
      badge.textContent = '근무 중';
      var lunchLeft = lunchBegin > nowMin ? '점심까지 ' + fmtDuration(lunchBegin - nowMin) + ' · ' : '';
      els.stateText.textContent = lunchLeft + (phase === 'morning' ? '오전 근무 중입니다' : '점심 지나 오후 근무 중입니다');
      els.subLine.textContent = '실근무 ' + fmtDuration(workdone) + ' / ' + fmtDuration(workTotal) +
        ' · 진행률 ' + Math.round(progress * 100) + '%';
      els.countdown.textContent = fmtDuration(Math.max(0, span.finish - nowMin));
    }
    els.countdown.classList.toggle('is-live', phase === 'morning' || phase === 'afternoon' || phase === 'lunch');
    return { earned: earned, worked: workdone, total: workTotal, phase: phase, hourly: hourly };
  }

  function tick() {
    var snapshot = render(new Date());
    return snapshot;
  }

  // ---------- 영수증 텍스트 ----------
  function receiptText(snapshot, now) {
    var lunchNote = '점심 ' + (state.lunchMin | 0) + '분' + (state.lunchPaid ? ' (유급)' : ' (무급)');
    var lines = [
      '오늘의 근무 영수증 · ' + now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate()) +
        ' (' + dayName(now.getDay()) + ')',
      '출근 ' + state.start + ' · 퇴근 ' + state.end + ' · ' + lunchNote,
      '실근무 ' + fmtDuration(snapshot.worked) + ' / ' + fmtDuration(snapshot.total),
      '지금까지 ' + fmtWon(snapshot.earned) + '원 (하루 ' + fmtWon(snapshot.hourly * snapshot.total / 60) + '원)',
      CONVERSIONS.slice(0, 3).map(function (item) {
        return item.name + ' ' + (Math.round(snapshot.earned / item.price * 10) / 10) + '개';
      }).join(' · ')
    ];
    if (snapshot.phase === 'after') lines.push('오늘 근무 끝 · 수고하셨습니다');
    else {
      var span = shiftSpan();
      var nowMin = now.getHours() * 60 + now.getMinutes();
      if (span.overnight && nowMin < span.begin) nowMin += 1440;
      lines.push('퇴근까지 ' + fmtDuration(Math.max(0, span.finish - nowMin)) + ' 남음');
    }
    lines.push('Infosec Archive 월급 미터');
    return lines.join('\n');
  }

  function pad(value) { return value < 10 ? '0' + value : String(value); }

  function copyText(text, statusEl) {
    function done(ok) {
      if (!statusEl) return;
      statusEl.textContent = ok ? '영수증을 복사했습니다. 단톡방에 붙여 넣으세요.' : '복사에 실패했습니다. 브라우저 권한을 확인해 주세요.';
      window.setTimeout(function () { if (statusEl.textContent) statusEl.textContent = ''; }, 4000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(text, done); });
      return;
    }
    fallback(text, done);
  }

  function fallback(text, done) {
    var area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', 'readonly');
    area.style.position = 'fixed';
    area.style.top = '-1000px';
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(area);
    done(ok);
  }

  // ---------- Canvas 카드 ----------
  function drawCard(snapshot, now) {
    var width = 1080, height = 1350;
    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    var ctx = canvas.getContext('2d');
    if (!ctx) return null;
    var ink = '#0f172a', sub = '#475569', mute = '#94a3b8', line = '#e2e8f0';
    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(60, 60, width - 120, height - 120);

    ctx.fillStyle = mute;
    ctx.font = '600 26px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillText('오늘의 근무 영수증', 110, 160);

    ctx.fillStyle = ink;
    ctx.font = '800 40px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillText(now.getFullYear() + '.' + pad(now.getMonth() + 1) + '.' + pad(now.getDate()) +
      ' (' + dayName(now.getDay()) + ')', 110, 215);

    ctx.fillStyle = mute;
    ctx.font = '600 24px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillText(state.start + ' 출근 · ' + state.end + ' 퇴근 · 점심 ' + (state.lunchMin | 0) + '분' +
      (state.lunchPaid ? ' 유급' : ' 무급'), 110, 265);

    ctx.fillStyle = mute;
    ctx.font = '600 26px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillText('지금까지 번 돈', 110, 380);

    ctx.fillStyle = ink;
    ctx.font = '800 124px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillText(fmtWon(snapshot.earned), 110, 505);
    var amountWidth = ctx.measureText(fmtWon(snapshot.earned)).width;
    ctx.font = '700 48px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillStyle = sub;
    ctx.fillText('원', 110 + amountWidth + 16, 505);

    // 진행 바
    var barY = 580, barW = width - 220;
    ctx.fillStyle = '#f1f5f9';
    ctx.fillRect(110, barY, barW, 26);
    var progress = snapshot.total > 0 ? Math.min(1, snapshot.worked / snapshot.total) : 0;
    ctx.fillStyle = '#0f766e';
    ctx.fillRect(110, barY, Math.max(6, Math.round(barW * progress)), 26);

    ctx.fillStyle = sub;
    ctx.font = '600 26px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillText('실근무 ' + fmtDuration(snapshot.worked) + ' / ' + fmtDuration(snapshot.total) +
      ' · ' + Math.round(progress * 100) + '%', 110, 655);

    // 구분선
    ctx.strokeStyle = line;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(110, 720);
    ctx.lineTo(width - 110, 720);
    ctx.stroke();

    var rows = [
      ['하루 총액', fmtWon(snapshot.hourly * snapshot.total / 60) + '원'],
      ['환산 시급', fmtWon(snapshot.hourly) + '원']
    ];
    CONVERSIONS.slice(0, 3).forEach(function (item) {
      rows.push([item.name, (Math.round(snapshot.earned / item.price * 10) / 10) + '개']);
    });
    rows.forEach(function (row, index) {
      var y = 790 + index * 92;
      ctx.fillStyle = mute;
      ctx.font = '600 28px "Pretendard", -apple-system, system-ui, sans-serif';
      ctx.fillText(row[0], 110, y);
      ctx.fillStyle = ink;
      ctx.font = '700 34px "Pretendard", -apple-system, system-ui, sans-serif';
      var valueWidth = ctx.measureText(row[1]).width;
      ctx.fillText(row[1], width - 110 - valueWidth, y);
    });

    ctx.fillStyle = mute;
    ctx.font = '600 24px "Pretendard", -apple-system, system-ui, sans-serif';
    ctx.fillText('Infosec Archive · 실시간 월급 미터', 110, height - 130);
    ctx.fillText('급여·근무 시간은 브라우저 안에서만 계산했습니다', 110, height - 95);
    return canvas;
  }

  function saveCard() {
    var now = new Date();
    var snapshot = render(now);
    var canvas = drawCard(snapshot, now);
    if (!canvas) {
      els.status.textContent = '이 브라우저에서는 카드 이미지를 만들 수 없습니다.';
      return;
    }
    function download(blob) {
      if (!blob) {
        els.status.textContent = '카드 이미지 생성에 실패했습니다.';
        return;
      }
      var url = URL.createObjectURL(blob);
      var link = document.createElement('a');
      link.href = url;
      link.download = 'paymeter-' + now.getFullYear() + pad(now.getMonth() + 1) + pad(now.getDate()) + '.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
      els.status.textContent = '카드 이미지를 저장했습니다.';
      window.setTimeout(function () { if (els.status.textContent) els.status.textContent = ''; }, 4000);
    }
    if (canvas.toBlob) canvas.toBlob(download, 'image/png');
    else els.status.textContent = '이 브라우저에서는 카드 이미지를 만들 수 없습니다.';
  }

  // ---------- 입력 처리 ----------
  function syncInputs() {
    els.amount.value = Number(state.amount).toLocaleString('ko-KR');
    els.start.value = state.start;
    els.end.value = state.end;
    els.lunchStart.value = state.lunchStart;
    els.lunchMin.value = String(state.lunchMin);
    els.lunchPaid.checked = !!state.lunchPaid;
    renderModeSeg();
    renderDays();
  }

  function commit() {
    saveState();
    validate();
    render(new Date());
  }

  els.modeSeg.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('button[data-mode]') : null;
    if (!btn) return;
    state.mode = btn.dataset.mode;
    renderModeSeg();
    commit();
  });

  els.amount.addEventListener('input', function () {
    var digits = els.amount.value.replace(/[^0-9]/g, '');
    var value = digits ? Math.min(99999999999, parseInt(digits, 10)) : 0;
    state.amount = value;
    els.amount.value = value ? value.toLocaleString('ko-KR') : '';
    saveState();
    validate();
    render(new Date());
  });

  els.amount.addEventListener('blur', function () {
    els.amount.value = Number(state.amount).toLocaleString('ko-KR');
  });

  [['start', els.start], ['end', els.end], ['lunchStart', els.lunchStart]].forEach(function (pair) {
    pair[1].addEventListener('change', function () {
      if (/^\d{2}:\d{2}$/.test(pair[1].value)) state[pair[0]] = pair[1].value;
      commit();
    });
  });

  els.lunchMin.addEventListener('change', function () {
    var value = parseInt(els.lunchMin.value, 10);
    if (isNaN(value)) value = DEFAULTS.lunchMin;
    state.lunchMin = Math.max(0, Math.min(240, value));
    els.lunchMin.value = String(state.lunchMin);
    commit();
  });

  els.lunchPaid.addEventListener('change', function () {
    state.lunchPaid = els.lunchPaid.checked;
    commit();
  });

  els.days.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('button[data-day]') : null;
    if (!btn) return;
    var day = parseInt(btn.dataset.day, 10);
    var index = state.workdays.indexOf(day);
    if (index >= 0) state.workdays.splice(index, 1);
    else state.workdays.push(day);
    state.workdays.sort(function (a, b) { return a - b; });
    renderDays();
    commit();
  });

  els.copy.addEventListener('click', function () {
    var now = new Date();
    copyText(receiptText(render(now), now), els.status);
  });

  els.card.addEventListener('click', saveCard);

  els.reset.addEventListener('click', function () {
    state = {
      mode: DEFAULTS.mode, amount: DEFAULTS.amount, start: DEFAULTS.start, end: DEFAULTS.end,
      lunchStart: DEFAULTS.lunchStart, lunchMin: DEFAULTS.lunchMin, lunchPaid: DEFAULTS.lunchPaid,
      workdays: DEFAULTS.workdays.slice()
    };
    syncInputs();
    commit();
    els.status.textContent = '기본값으로 되돌리고 저장한 설정을 지웠습니다.';
    window.setTimeout(function () { if (els.status.textContent) els.status.textContent = ''; }, 4000);
  });

  syncInputs();
  validate();
  render(new Date());
  window.setInterval(function () { render(new Date()); }, 1000);

  // 테스트·디버깅용 최소 노출 (계산 결과만 확인할 수 있게)
  window.PAYMETER = {
    state: state,
    snapshot: function () { return render(new Date()); },
    hourly: hourlyWage,
    worked: workedMinutes,
    total: totalWorkMinutes
  };
})();
"""


def build(out_path=None):
    config = {
        "storeKey": "secjobs-paymeter-v1",
        "monthlyHours": MONTHLY_HOURS,
        "conversions": [{"name": name, "price": price} for name, price in CONVERSIONS],
        "weekdays": WEEKDAYS,
        "defaults": DEFAULT_STATE,
    }
    payload = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__CONFIG_JSON__", payload)
            .replace("__JS__", JS))

    with open(out_path or OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "paymeter")))

    print("-> 'paymeter.html' 생성 완료 (월 소정근로 %d시간 기준 · 환산 %d종)"
          % (int(MONTHLY_HOURS), len(CONVERSIONS)))
    return {"conversions": len(CONVERSIONS), "monthlyHours": MONTHLY_HOURS}


if __name__ == "__main__":
    build()

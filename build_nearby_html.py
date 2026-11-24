#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""우리 동네 지금 갈 곳(nearby.html).

무엇을 하나
  · 서울 9개 자치구의 공공·생활 문화 공간 30곳(공공도서관·대형공원·무료 상설전시·생활문화센터·한강공원 등)을
    `nearby_data.json` 에서 읽는다. 주소·운영시간·정기휴무·요금·공식 안내 링크는 시설 공식 안내와
    대조한 값이며, 데이터 기준일(checkedOn)을 화면에 적는다.
  · 지금 시각(KST) · 자치구 · 남은 시간(30분/1시간/2시간+)으로 골라
      - 지금 들어갈 수 있는 곳(남은 시간이 운영 종료까지보다 짧은 곳)
      - 남은 시간이 모자란 곳
      - 오늘 문을 닫은 곳(휴관일·운영 종료·개장 전)
    으로 나눠 보여 준다. 마감 임박(60분 이내) 배지, 무료/유료 배지, 찜(localStorage)을 붙인다.
  · 하루 24시간 띠 위에 오늘의 운영 구간과 '지금' 표시를 그려 언제 닫는지 한눈에 보이게 한다.

지키는 것
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 필터 레일 + 3열 카드 / 모바일(390px) 가로 스크롤 필터 + 1열 카드
  · 없는 장소·시간을 만들지 않는다. 공휴일·임시휴관은 '반영되지 않음'을 화면에 밝힌다.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "nearby_data.json")
OUT_HTML = os.path.join(BASE_DIR, "nearby.html")
KST = timezone(timedelta(hours=9))
STORE_KEY = "secjobs-nearby-fav-v1"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_LABEL = {"mon": "월", "tue": "화", "wed": "수", "thu": "목", "fri": "금", "sat": "토", "sun": "일"}
CATEGORIES = ["도서관", "박물관", "미술관", "공원", "한강공원", "문화공간", "사찰", "왕릉"]
MIN_PLACES = 24
MIN_DISTRICTS = 8


def parse_time(text):
    if text == "24:00":
        return 24 * 60
    hour, minute = text.split(":")
    return int(hour) * 60 + int(minute)


def load_data(path=None):
    with open(path or DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)
    places = data.get("places") or []
    districts = data.get("districts") or []
    if len(districts) < MIN_DISTRICTS:
        raise SystemExit("자치구가 %d개입니다(%d개 이상 필요)." % (len(districts), MIN_DISTRICTS))
    if len(places) < MIN_PLACES:
        raise SystemExit("장소가 %d곳입니다(%d곳 이상 필요)." % (len(places), MIN_PLACES))
    seen = set()
    for place in places:
        pid = place.get("id")
        if not pid or pid in seen:
            raise SystemExit("장소 ID 가 없거나 중복입니다: %r" % pid)
        seen.add(pid)
        if place.get("district") not in districts:
            raise SystemExit("%s 자치구가 목록에 없습니다: %r" % (pid, place.get("district")))
        if place.get("category") not in CATEGORIES:
            raise SystemExit("%s 분류가 정의되지 않았습니다: %r" % (pid, place.get("category")))
        if not place.get("address") or not place.get("name"):
            raise SystemExit("%s 주소/이름이 비었습니다." % pid)
        if place.get("fee") not in ("무료", "유료"):
            raise SystemExit("%s 요금 표기가 잘못됐습니다: %r" % (pid, place.get("fee")))
        if not isinstance(place.get("duration"), int) or place["duration"] < 20:
            raise SystemExit("%s 체류 시간이 잘못됐습니다." % pid)
        url = place.get("officialUrl") or ""
        if not url.startswith("https://"):
            raise SystemExit("%s 공식 링크가 https 가 아닙니다: %s" % (pid, url))
        hours = place.get("hours") or {}
        if set(hours.keys()) != set(DAYS):
            raise SystemExit("%s 요일별 운영시간이 7개가 아닙니다." % pid)
        opened = 0
        for day in DAYS:
            window = hours[day]
            if window is None:
                continue
            if len(window) != 2:
                raise SystemExit("%s %s 운영시간 형식이 잘못됐습니다." % (pid, day))
            start, end = parse_time(window[0]), parse_time(window[1])
            if start >= end:
                raise SystemExit("%s %s 운영시간 순서가 잘못됐습니다." % (pid, day))
            opened += 1
        if opened == 0:
            raise SystemExit("%s 는 여는 날이 없습니다." % pid)
        if not place.get("closureNote"):
            raise SystemExit("%s 휴관 안내가 비었습니다." % pid)
    return data


def build_payload(data):
    places = []
    for place in data["places"]:
        places.append({
            "id": place["id"],
            "name": place["name"],
            "district": place["district"],
            "category": place["category"],
            "address": place["address"],
            "hours": {day: place["hours"][day] for day in DAYS},
            "closureNote": place["closureNote"],
            "fee": place["fee"],
            "feeNote": place.get("feeNote") or "",
            "duration": place["duration"],
            "note": place.get("note") or "",
            "officialUrl": place["officialUrl"],
            "mapUrl": "https://map.naver.com/p/search/" + quote(place["name"]),
            "checkedOn": place.get("checkedOn") or data["checkedOn"],
        })
    return {
        "places": places,
        "districts": data["districts"],
        "checkedOn": data["checkedOn"],
        "note": data["note"],
        "storeKey": STORE_KEY,
        "dayLabels": DAY_LABEL,
    }


def build(out_path=None, today=None):
    data = load_data()
    payload = build_payload(data)
    today = today or datetime.now(KST).date()

    district_html = '<button type="button" class="nb-chip is-on" data-district="all" aria-pressed="true">전체</button>'
    for district in payload["districts"]:
        count = sum(1 for place in payload["places"] if place["district"] == district)
        district_html += (
            '<button type="button" class="nb-chip" data-district="{name}" aria-pressed="false">'
            '{name}<span>{count}</span></button>'
        ).format(name=district, count=count)

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__TODAY__", today.isoformat())
            .replace("__CHECKED__", payload["checkedOn"])
            .replace("__COUNT__", str(len(payload["places"])))
            .replace("__DISTRICTS__", str(len(payload["districts"])))
            .replace("__DISTRICT_CHIPS__", district_html)
            .replace("__DATA_JSON__", safe_json_for_script(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":"))))
            .replace("__JS__", JS))

    with open(out_path or OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "nearby")))

    print("-> 'nearby.html' 생성 완료 (자치구 %d · 장소 %d곳 · 기준일 %s)"
          % (len(payload["districts"]), len(payload["places"]), payload["checkedOn"]))
    return {"districts": len(payload["districts"]), "places": len(payload["places"]),
            "checkedOn": payload["checkedOn"]}


CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --bg-page: #f8fafc;  --bg-surface: #ffffff;  --bg-subtle: #f1f5f9;  --bg-muted: #e2e8f0;
      --border-subtle: #f1f5f9;  --border-default: #e2e8f0;  --border-strong: #cbd5e1;
      --text-primary: #0f172a;  --text-secondary: #475569;  --text-muted: #94a3b8;
      --accent-primary: #2563eb;  --accent-subtle: #eff6ff;
      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;  --ok-ink: #0f766e;
      --warn-bg: #fffbeb;  --warn-text: #b45309;  --warn-border: #fde68a;
      --closed-bg: #f8fafc;  --closed-text: #64748b;  --closed-border: #e2e8f0;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --ok-bg: rgba(16, 185, 129, 0.14);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.34);  --ok-ink: #5eead4;
      --warn-bg: rgba(245, 158, 11, 0.14);  --warn-text: #fcd34d;  --warn-border: rgba(245, 158, 11, 0.34);
      --closed-bg: #141417;  --closed-text: #71717a;  --closed-border: #27272a;
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body { font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease; }
    .nb-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .nb-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 100px; }
    .nb-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .nb-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 680px; word-break: keep-all; }
    .nb-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .nb-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px;
      font-size: 11.5px; color: var(--text-muted); }
    .nb-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }
    .nb-clock { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 800;
      color: var(--text-primary); background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 999px; padding: 3px 10px 3px 8px; font-variant-numeric: tabular-nums; }
    .nb-clock::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: #10b981; }

    .nb-filters { margin-top: 16px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 14px 15px; box-shadow: var(--card-shadow); }
    .nb-filter-row { display: flex; align-items: center; gap: 10px; }
    .nb-filter-row + .nb-filter-row { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-subtle); }
    .nb-filter-label { flex: 0 0 auto; font-size: 10.5px; font-weight: 800; color: var(--text-muted);
      letter-spacing: 0.01em; width: 58px; }
    .nb-chips { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 2px; scrollbar-width: none; }
    .nb-chips::-webkit-scrollbar { display: none; }
    .nb-chip { flex: 0 0 auto; display: inline-flex; align-items: center; gap: 4px; border: 1px solid var(--border-default);
      background: var(--bg-page); color: var(--text-secondary); border-radius: 999px; padding: 6px 11px;
      font-family: inherit; font-size: 11.5px; font-weight: 700; cursor: pointer; white-space: nowrap;
      transition: border-color .15s ease, background-color .15s ease, color .15s ease, transform .15s ease; }
    .nb-chip:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .nb-chip:active { transform: scale(0.97); }
    .nb-chip:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .nb-chip span { font-size: 10px; font-weight: 700; color: var(--text-muted); }
    .nb-chip.is-on { border-color: var(--text-primary); background: var(--text-primary); color: var(--bg-surface); }
    .nb-chip.is-on span { color: var(--bg-surface); opacity: .7; }
    .nb-chip.is-ghost { border-style: dashed; }
    .nb-chip.is-fav-on { border-color: var(--accent-primary); background: var(--accent-subtle); color: var(--accent-primary); }

    .nb-summary { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 12px;
      font-size: 12px; color: var(--text-secondary); }
    .nb-summary b { font-weight: 800; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .nb-summary .nb-warn { color: var(--warn-text); font-weight: 700; }

    .nb-group { margin-top: 18px; }
    .nb-group-head { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; }
    .nb-group-head h2 { font-size: 15px; font-weight: 800; letter-spacing: -0.03em; }
    .nb-group-head .nb-count { font-size: 11.5px; font-weight: 700; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .nb-group-head p { margin-top: 2px; font-size: 11px; color: var(--text-muted); }
    .nb-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 9px; }
    .nb-grid.is-closed { grid-template-columns: repeat(4, minmax(0, 1fr)); }

    .nb-card { display: flex; flex-direction: column; gap: 7px; border: 1px solid var(--border-default);
      background: var(--bg-surface); border-radius: 15px; padding: 13px; box-shadow: var(--card-shadow);
      min-width: 0; transition: border-color .15s ease, transform .15s ease; }
    .nb-card:hover { border-color: var(--border-strong); }
    .nb-card.is-closed { background: var(--closed-bg); border-color: var(--closed-border); }
    .nb-card.is-closed .nb-name, .nb-card.is-closed .nb-addr { color: var(--closed-text); }
    .nb-card.is-closed .nb-name { color: var(--text-secondary); }
    .nb-card-top { display: flex; align-items: center; gap: 5px; }
    .nb-cat { font-size: 10px; font-weight: 800; color: var(--text-muted); border: 1px solid var(--border-default);
      border-radius: 999px; padding: 1px 7px; }
    .nb-fee { font-size: 10px; font-weight: 800; border-radius: 999px; padding: 1px 7px; }
    .nb-fee.is-free { color: var(--ok-text); background: var(--ok-bg); border: 1px solid var(--ok-border); }
    .nb-fee.is-paid { color: var(--warn-text); background: var(--warn-bg); border: 1px solid var(--warn-border); }
    .nb-urgent { font-size: 10px; font-weight: 800; color: var(--warn-text); background: var(--warn-bg);
      border: 1px solid var(--warn-border); border-radius: 999px; padding: 1px 7px; margin-left: auto; }
    .nb-fav { margin-left: auto; flex: 0 0 auto; width: 30px; height: 30px; border-radius: 9px; border: 1px solid var(--border-default);
      background: var(--bg-page); color: var(--text-muted); cursor: pointer; display: inline-flex;
      align-items: center; justify-content: center; transition: color .15s ease, border-color .15s ease, transform .15s ease; }
    .nb-fav svg { width: 15px; height: 15px; }
    .nb-fav:hover { color: var(--text-primary); border-color: var(--border-strong); }
    .nb-fav:active { transform: scale(0.94); }
    .nb-fav:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .nb-fav[aria-pressed="true"] { color: #e11d48; border-color: #fecdd3; background: #fff1f2; }
    [data-theme="dark"] .nb-fav[aria-pressed="true"] { color: #fb7185; border-color: rgba(251, 113, 133, .4); background: rgba(251, 113, 133, .12); }
    .nb-urgent + .nb-fav { margin-left: 0; }

    .nb-name { font-size: 14.5px; font-weight: 800; letter-spacing: -0.03em; word-break: keep-all; }
    .nb-addr { font-size: 10.5px; color: var(--text-muted); word-break: keep-all; }
    .nb-window { display: flex; align-items: baseline; gap: 6px; margin-top: 1px; }
    .nb-window b { font-size: 13px; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
    .nb-window span { font-size: 10.5px; font-weight: 700; color: var(--text-muted); }
    .nb-window span.is-left { color: var(--ok-ink); }
    .nb-window span.is-short { color: var(--warn-text); }
    .nb-band { position: relative; height: 7px; border-radius: 999px; background: var(--bg-subtle);
      border: 1px solid var(--border-default); overflow: hidden; }
    .nb-band-open { position: absolute; top: 0; bottom: 0; background: var(--text-secondary); opacity: .55; border-radius: 2px; }
    .nb-card.is-closed .nb-band-open { opacity: .25; }
    .nb-band-now { position: absolute; top: -2px; bottom: -2px; width: 2px; background: var(--accent-primary); }
    .nb-band-legend { display: flex; justify-content: space-between; font-size: 9px; color: var(--text-muted);
      font-variant-numeric: tabular-nums; margin-top: -3px; }
    .nb-closure { font-size: 10.5px; color: var(--text-secondary); word-break: keep-all; }
    .nb-closure b { font-weight: 700; color: var(--text-primary); }
    .nb-note { font-size: 10.5px; line-height: 1.5; color: var(--text-muted); word-break: keep-all; }
    .nb-card.is-closed .nb-note { color: var(--closed-text); }
    .nb-links { display: flex; gap: 6px; margin-top: auto; padding-top: 3px; }
    .nb-link { display: inline-flex; align-items: center; justify-content: center; gap: 3px; flex: 1 1 0;
      border: 1px solid var(--border-default); background: var(--bg-page); color: var(--text-secondary);
      border-radius: 8px; padding: 6px 4px; font-size: 10.5px; font-weight: 700; text-decoration: none;
      transition: background-color .15s ease, color .15s ease, border-color .15s ease; }
    .nb-link:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .nb-link:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .nb-link svg { width: 11px; height: 11px; }

    .nb-empty { margin-top: 8px; border: 1px dashed var(--border-strong); border-radius: 13px; padding: 18px;
      background: var(--bg-surface); font-size: 12px; color: var(--text-secondary); text-align: center; line-height: 1.6; }
    .nb-empty b { color: var(--text-primary); }
    .nb-group.is-hidden { display: none; }

    .nb-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .nb-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; }
    .nb-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .nb-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .nb-notes li b { color: var(--text-primary); }
    .nb-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 1000px) {
      .nb-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .nb-grid.is-closed { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 900px) {
      .nb-wrap { padding: 14px 13px 110px; }
      .nb-hero h1 { font-size: 21px; }
      .nb-hero p { font-size: 12px; }
      .nb-filters { padding: 12px; margin-top: 13px; }
      .nb-filter-row { display: block; }
      .nb-filter-row + .nb-filter-row { margin-top: 9px; padding-top: 9px; }
      .nb-filter-label { width: auto; display: block; margin-bottom: 6px; }
      .nb-summary { margin-top: 10px; font-size: 11.5px; }
      .nb-group { margin-top: 15px; }
      .nb-group-head h2 { font-size: 14.5px; }
      .nb-grid { grid-template-columns: minmax(0, 1fr); gap: 8px; }
      .nb-grid.is-closed { grid-template-columns: minmax(0, 1fr); }
    }
    @media (max-width: 380px) {
      .nb-card { padding: 11px; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 우리 동네 지금 갈 곳</title>
  <meta name="description" content="서울 9개 자치구의 공공도서관·대형공원·무료 상설전시·한강공원 30곳을 지금 시각(KST)과 남은 시간(30분·1시간·2시간)으로 골라 보여 줍니다. 운영시간·정기휴무·요금·공식 안내를 시설 공식 자료와 대조해 기준일과 함께 표시합니다.">
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
        <div class="update-meta"><span class="live-dot"></span><span>장소 __COUNT__곳 · 자료 확인 __CHECKED__</span></div>
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

  <main class="nb-wrap">
    <section class="nb-hero">
      <span class="nb-pill">생활 · 지금 갈 곳</span>
      <h1>지금 이 동네, 어디 갈까</h1>
      <p>서울 9개 자치구의 공공도서관·대형공원·무료 상설전시·한강공원 30곳입니다. 지금 시각과 남은 시간, 자치구를 고르면 지금 들어가 이용할 수 있는 곳만 남깁니다.</p>
      <div class="nb-meta">
        <span class="nb-clock" id="nbClock">--:-- KST</span>
        <span class="nb-dot"></span>
        <span>장소 __COUNT__곳 · 자치구 __DISTRICTS__개</span>
        <span class="nb-dot"></span>
        <span>자료 확인 __CHECKED__</span>
        <span class="nb-dot"></span>
        <span>공휴일·임시휴관은 반영하지 않음</span>
      </div>
    </section>

    <section class="nb-filters" aria-label="갈 곳 고르기">
      <div class="nb-filter-row">
        <span class="nb-filter-label">자치구</span>
        <div class="nb-chips" id="nbDistricts" role="group" aria-label="자치구 선택">__DISTRICT_CHIPS__</div>
      </div>
      <div class="nb-filter-row">
        <span class="nb-filter-label">남은 시간</span>
        <div class="nb-chips" id="nbRemain" role="group" aria-label="남은 시간 선택">
          <button type="button" class="nb-chip is-on" data-remain="30" aria-pressed="true">30분</button>
          <button type="button" class="nb-chip" data-remain="60" aria-pressed="false">1시간</button>
          <button type="button" class="nb-chip" data-remain="120" aria-pressed="false">2시간 이상</button>
        </div>
        <button type="button" class="nb-chip is-ghost" id="nbFavOnly" aria-pressed="false">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 21s-7-4.6-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.4-7 10-7 10z"></path></svg>
          찜한 곳만
        </button>
      </div>
      <div class="nb-summary" id="nbSummary" role="status" aria-live="polite"></div>
    </section>

    <section class="nb-group" id="nbOpenGroup" aria-labelledby="nbOpenTitle">
      <div class="nb-group-head">
        <div>
          <h2 id="nbOpenTitle">지금 들어갈 수 있어요</h2>
          <p>지금 문을 열었고, 남은 시간보다 늦게 닫습니다</p>
        </div>
        <span class="nb-count" id="nbOpenCount">0곳</span>
      </div>
      <div class="nb-grid" id="nbOpenGrid"></div>
      <p class="nb-empty" id="nbOpenEmpty" hidden></p>
    </section>

    <section class="nb-group" id="nbShortGroup" aria-labelledby="nbShortTitle">
      <div class="nb-group-head">
        <div>
          <h2 id="nbShortTitle">남은 시간이 모자라요</h2>
          <p>문은 열었지만 고른 시간 안에 닫습니다</p>
        </div>
        <span class="nb-count" id="nbShortCount">0곳</span>
      </div>
      <div class="nb-grid" id="nbShortGrid"></div>
      <p class="nb-empty" id="nbShortEmpty" hidden></p>
    </section>

    <section class="nb-group" id="nbClosedGroup" aria-labelledby="nbClosedTitle">
      <div class="nb-group-head">
        <div>
          <h2 id="nbClosedTitle">오늘은 문을 닫아요</h2>
          <p>휴관일이거나 오늘 운영이 끝났습니다</p>
        </div>
        <span class="nb-count" id="nbClosedCount">0곳</span>
      </div>
      <div class="nb-grid is-closed" id="nbClosedGrid"></div>
      <p class="nb-empty" id="nbClosedEmpty" hidden></p>
    </section>

    <section class="nb-notes">
      <h2>알아 두실 점</h2>
      <ul>
        <li><b>자료 기준일</b> — 주소·운영시간·정기휴무·요금은 2026-11-24에 시설 공식 안내(누리집·서울시 공공 안내)와 대조한 값입니다. 계절·전시 교체·공휴일로 달라질 수 있습니다.</li>
        <li><b>지금 시각</b> — 이 기기의 시계를 KST로 환산해 계산합니다. 공휴일·임시휴관·행사로 인한 단축 운영은 반영하지 않으니 전화나 공식 안내로 확인하세요.</li>
        <li><b>남은 시간</b> — '30분'을 고르면 지금부터 30분 뒤에도 문이 열려 있는 곳만 남깁니다. 종료 60분 전부터는 마감 임박 배지를 붙입니다.</li>
        <li><b>요금</b> — 무료 표시는 상설전·공원 입장 기준입니다. 특별전·주차·체험 프로그램은 따로 낼 수 있습니다.</li>
        <li><b>찜</b> — 찜한 곳은 이 브라우저(localStorage)에만 저장되며 서버로 보내지 않습니다.</li>
      </ul>
      <p class="nb-foot">각 시설의 공식 안내를 옮겨 적었고, 지금 시각과 남은 시간 계산만 이 페이지에서 합니다 · 방문 전 공식 안내를 한 번 더 확인하세요.</p>
    </section>
  </main>

  <script type="application/json" id="nbData">__DATA_JSON__</script>
  <script>__JS__</script>
</body>
</html>
"""

JS = r"""
(function () {
  'use strict';

  // ---------- 화면 테마 ----------
  var themeBtn = document.getElementById('themeToggle');
  var moonIcon = document.getElementById('moonIcon');
  var sunIcon = document.getElementById('sunIcon');
  function applyTheme(dark, persist) {
    if (dark) document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    if (moonIcon) moonIcon.style.display = dark ? 'none' : 'block';
    if (sunIcon) sunIcon.style.display = dark ? 'block' : 'none';
    if (persist) { try { localStorage.setItem('secjobs-theme', dark ? 'dark' : 'light'); } catch (e) {} }
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

  var DATA;
  try { DATA = JSON.parse(document.getElementById('nbData').textContent); } catch (e) { return; }
  var PLACES = DATA.places;
  var DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  var DAY_LABEL = { sun: '일', mon: '월', tue: '화', wed: '수', thu: '목', fri: '금', sat: '토' };
  var STORE_KEY = DATA.storeKey;

  var els = {
    clock: document.getElementById('nbClock'),
    districts: document.getElementById('nbDistricts'),
    remain: document.getElementById('nbRemain'),
    favOnly: document.getElementById('nbFavOnly'),
    summary: document.getElementById('nbSummary'),
    openGrid: document.getElementById('nbOpenGrid'),
    shortGrid: document.getElementById('nbShortGrid'),
    closedGrid: document.getElementById('nbClosedGrid'),
    openCount: document.getElementById('nbOpenCount'),
    shortCount: document.getElementById('nbShortCount'),
    closedCount: document.getElementById('nbClosedCount'),
    openEmpty: document.getElementById('nbOpenEmpty'),
    shortEmpty: document.getElementById('nbShortEmpty'),
    closedEmpty: document.getElementById('nbClosedEmpty'),
    openGroup: document.getElementById('nbOpenGroup'),
    shortGroup: document.getElementById('nbShortGroup'),
    closedGroup: document.getElementById('nbClosedGroup')
  };

  var filter = { district: 'all', remain: 30, favOnly: false };
  var favs = [];
  try {
    var raw = JSON.parse(localStorage.getItem(STORE_KEY) || '[]');
    if (Object.prototype.toString.call(raw) === '[object Array]') favs = raw.filter(function (id) { return typeof id === 'string'; });
  } catch (e) { favs = []; }
  function saveFavs() { try { localStorage.setItem(STORE_KEY, JSON.stringify(favs)); } catch (e) {} }

  // ---------- KST 시각 ----------
  function kstNow() {
    var now = new Date();
    return new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + 9 * 3600000);
  }
  function pad(v) { return v < 10 ? '0' + v : String(v); }
  function minutesOf(day) { return day.getHours() * 60 + day.getMinutes(); }
  function dayKey(day) { return DAYS[day.getDay()]; }
  function timeText(minutes) {
    if (minutes >= 1440) return '24:00';
    return pad(Math.floor(minutes / 60)) + ':' + pad(minutes % 60);
  }
  function parseTime(text) {
    if (text === '24:00') return 1440;
    var parts = text.split(':');
    return Number(parts[0]) * 60 + Number(parts[1]);
  }
  function spanText(minutes) {
    var m = Math.max(0, Math.round(minutes));
    if (m >= 60) {
      var h = Math.floor(m / 60);
      var rest = m % 60;
      return h + '시간' + (rest ? ' ' + rest + '분' : '');
    }
    return m + '분';
  }

  // ---------- 카드 ----------
  var HEART_PATH = 'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1L12 21l7.7-7.6 1.1-1a5.5 5.5 0 0 0 0-7.8z';
  var HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + HEART_PATH + '"></path></svg>';
  var HEART_FILL = '<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="' + HEART_PATH + '"></path></svg>';
  var EXTERNAL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-8 8"></path><path d="M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"></path></svg>';

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function statusOf(place, day) {
    var key = dayKey(day);
    var window = place.hours[key];
    var now = minutesOf(day);
    if (!window) {
      return { kind: 'closed', reason: '오늘 휴관', window: null };
    }
    var start = parseTime(window[0]);
    var end = parseTime(window[1]);
    if (now < start) {
      return { kind: 'closed', reason: timeText(start) + ' 개장', window: [start, end] };
    }
    if (now >= end) {
      return { kind: 'closed', reason: timeText(end) + ' 운영 종료', window: [start, end] };
    }
    // 00:00~24:00 은 하루 종일 여는 곳이라 자정을 '마감'으로 보지 않는다.
    var wholeDay = start === 0 && end === 24 * 60;
    return { kind: 'open', left: wholeDay ? 24 * 60 : end - now, window: [start, end], wholeDay: wholeDay };
  }

  function cardOf(place, status, day) {
    var card = el('article', 'nb-card' + (status.kind === 'open' ? '' : ' is-closed'));
    card.dataset.id = place.id;

    var top = el('div', 'nb-card-top');
    top.appendChild(el('span', 'nb-cat', place.category));
    top.appendChild(el('span', 'nb-fee ' + (place.fee === '무료' ? 'is-free' : 'is-paid'), place.fee));
    if (status.kind === 'open' && status.left <= 60) {
      top.appendChild(el('span', 'nb-urgent', '마감 임박'));
    }
    var fav = el('button', 'nb-fav');
    fav.type = 'button';
    fav.dataset.fav = place.id;
    fav.setAttribute('aria-pressed', favs.indexOf(place.id) >= 0 ? 'true' : 'false');
    fav.setAttribute('aria-label', place.name + ' 찜하기');
    fav.innerHTML = favs.indexOf(place.id) >= 0 ? HEART_FILL : HEART;
    top.appendChild(fav);
    card.appendChild(top);

    card.appendChild(el('h3', 'nb-name', place.name));
    card.appendChild(el('p', 'nb-addr', place.address));

    var windowLine = el('p', 'nb-window');
    if (status.kind === 'open') {
      windowLine.appendChild(el('b', '', timeText(status.window[0]) + '–' + timeText(status.window[1])));
      var left = el('span', 'is-left', status.wholeDay ? '24시간 개방' : spanText(status.left) + ' 남음');
      if (status.left <= 60) left.className = 'is-short';
      windowLine.appendChild(left);
    } else {
      windowLine.appendChild(el('b', '', status.reason));
      windowLine.appendChild(el('span', '', place.closureNote));
    }
    card.appendChild(windowLine);

    // 하루 24시간 띠 — 오늘 운영 구간과 지금 위치
    var band = el('div', 'nb-band');
    var span = status.window;
    var openBar = el('span', 'nb-band-open');
    var nowBar = el('span', 'nb-band-now');
    if (span) {
      openBar.style.left = (span[0] / 1440 * 100).toFixed(2) + '%';
      openBar.style.width = (Math.max(0, span[1] - span[0]) / 1440 * 100).toFixed(2) + '%';
    } else {
      openBar.style.left = '0%';
      openBar.style.width = '0%';
    }
    nowBar.style.left = (minutesOf(day) / 1440 * 100).toFixed(2) + '%';
    band.appendChild(openBar);
    band.appendChild(nowBar);
    card.appendChild(band);
    var legend = el('div', 'nb-band-legend');
    legend.appendChild(el('span', '', '00'));
    legend.appendChild(el('span', '', '12'));
    legend.appendChild(el('span', '', '24'));
    card.appendChild(legend);

    if (status.kind === 'open') {
      var closure = el('p', 'nb-closure');
      closure.appendChild(el('b', '', '휴관 '));
      closure.appendChild(document.createTextNode(place.closureNote));
      card.appendChild(closure);
    }
    if (place.note) card.appendChild(el('p', 'nb-note', place.note));

    var links = el('div', 'nb-links');
    var official = el('a', 'nb-link');
    official.href = place.officialUrl;
    official.target = '_blank';
    official.rel = 'noopener noreferrer';
    official.innerHTML = EXTERNAL;
    official.appendChild(document.createTextNode(' 공식 안내'));
    var map = el('a', 'nb-link');
    map.href = place.mapUrl;
    map.target = '_blank';
    map.rel = 'noopener noreferrer';
    map.innerHTML = EXTERNAL;
    map.appendChild(document.createTextNode(' 지도'));
    links.appendChild(official);
    links.appendChild(map);
    card.appendChild(links);
    return card;
  }

  // ---------- 렌더 ----------
  function matchesFilters(place) {
    if (filter.district !== 'all' && place.district !== filter.district) return false;
    if (filter.favOnly && favs.indexOf(place.id) < 0) return false;
    return true;
  }

  function render() {
    var day = kstNow();
    els.clock.textContent = timeText(minutesOf(day)) + ' ' + DAY_LABEL[dayKey(day)] + ' KST';

    var open = [];
    var short = [];
    var closed = [];
    PLACES.forEach(function (place) {
      if (!matchesFilters(place)) return;
      var status = statusOf(place, day);
      if (status.kind === 'open') {
        if (status.left >= filter.remain) open.push({ place: place, status: status });
        else short.push({ place: place, status: status });
      } else {
        closed.push({ place: place, status: status });
      }
    });
    open.sort(function (a, b) { return a.status.left - b.status.left; });
    short.sort(function (a, b) { return b.status.left - a.status.left; });
    closed.sort(function (a, b) { return a.place.name.localeCompare(b.place.name, 'ko'); });

    function fill(grid, empty, rows, emptyText) {
      grid.innerHTML = '';
      rows.forEach(function (row) {
        grid.appendChild(cardOf(row.place, row.status, day));
      });
      if (!rows.length) {
        empty.hidden = false;
        empty.innerHTML = emptyText;
      } else {
        empty.hidden = true;
      }
    }

    fill(els.openGrid, els.openEmpty, open,
      '<b>지금 이 조건에 맞는 곳이 없습니다.</b><br>남은 시간을 늘리거나 자치구를 바꿔 보세요.');
    fill(els.shortGrid, els.shortEmpty, short,
      '고른 시간 안에 닫는 곳이 없습니다. 남은 시간을 줄이면 더 보입니다.');
    fill(els.closedGrid, els.closedEmpty, closed,
      '조건에 맞는 휴관 장소가 없습니다.');

    els.openCount.textContent = open.length + '곳';
    els.shortCount.textContent = short.length + '곳';
    els.closedCount.textContent = closed.length + '곳';
    els.shortGroup.classList.toggle('is-hidden', short.length === 0 && filter.favOnly);
    els.closedGroup.classList.toggle('is-hidden', closed.length === 0 && filter.favOnly);

    var urgent = open.filter(function (row) { return row.status.left <= 60; }).length;
    els.summary.innerHTML = '';
    els.summary.appendChild(document.createTextNode('지금 갈 수 있는 곳 '));
    els.summary.appendChild(el('b', '', open.length + '곳'));
    els.summary.appendChild(document.createTextNode(' · 오늘 문 닫은 곳 '));
    els.summary.appendChild(el('b', '', closed.length + '곳'));
    if (urgent) {
      els.summary.appendChild(document.createTextNode(' · '));
      els.summary.appendChild(el('span', 'nb-warn', '마감 임박 ' + urgent + '곳'));
    }

    // 찜 상태를 카드에 반영
    Array.prototype.forEach.call(document.querySelectorAll('.nb-fav'), function (btn) {
      var id = btn.dataset.fav;
      var on = favs.indexOf(id) >= 0;
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.innerHTML = on ? HEART_FILL : HEART;
    });
  }

  // ---------- 이벤트 ----------
  els.districts.addEventListener('click', function (event) {
    var chip = event.target.closest ? event.target.closest('.nb-chip') : null;
    if (!chip) return;
    filter.district = chip.dataset.district;
    Array.prototype.forEach.call(els.districts.querySelectorAll('.nb-chip'), function (btn) {
      var on = btn === chip;
      btn.classList.toggle('is-on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    render();
  });

  els.remain.addEventListener('click', function (event) {
    var chip = event.target.closest ? event.target.closest('.nb-chip') : null;
    if (!chip) return;
    filter.remain = Number(chip.dataset.remain);
    Array.prototype.forEach.call(els.remain.querySelectorAll('.nb-chip'), function (btn) {
      var on = btn === chip;
      btn.classList.toggle('is-on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    render();
  });

  els.favOnly.addEventListener('click', function () {
    filter.favOnly = !filter.favOnly;
    els.favOnly.setAttribute('aria-pressed', filter.favOnly ? 'true' : 'false');
    els.favOnly.classList.toggle('is-fav-on', filter.favOnly);
    render();
  });

  document.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('.nb-fav') : null;
    if (!btn) return;
    var id = btn.dataset.fav;
    var at = favs.indexOf(id);
    if (at >= 0) favs.splice(at, 1);
    else favs.push(id);
    saveFavs();
    if (filter.favOnly) render();
    else {
      btn.setAttribute('aria-pressed', at >= 0 ? 'false' : 'true');
      btn.innerHTML = at >= 0 ? HEART : HEART_FILL;
    }
  });

  // 1분마다 다시 계산 — 날짜가 바뀌면 요일 운영시간도 함께 바뀐다.
  var lastDay = dayKey(kstNow());
  window.setInterval(function () {
    var now = kstNow();
    if (dayKey(now) !== lastDay) {
      lastDay = dayKey(now);
      render();
      return;
    }
    els.clock.textContent = timeText(minutesOf(now)) + ' ' + DAY_LABEL[dayKey(now)] + ' KST';
    render();
  }, 60000);
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) render();
  });

  render();

  // 테스트·디버깅용
  window.NEARBY = {
    data: DATA,
    filter: filter,
    favs: function () { return favs.slice(); },
    setDistrict: function (name) {
      var chip = els.districts.querySelector('[data-district="' + name + '"]');
      if (chip) chip.click();
    },
    setRemain: function (minutes) {
      var chip = els.remain.querySelector('[data-remain="' + minutes + '"]');
      if (chip) chip.click();
    },
    toggleFav: function (id) {
      var btn = document.querySelector('.nb-fav[data-fav="' + id + '"]');
      if (btn) btn.click();
    },
    statusAt: function (minutes, dayIndex) {
      // 지정한 시각(KST 분)과 요일로 상태를 계산한다(테스트·확인용).
      var fake = new Date(2026, 10, 22 + (dayIndex || 0), Math.floor(minutes / 60), minutes % 60);
      return PLACES.map(function (place) {
        return { id: place.id, name: place.name, status: statusOf(place, fake) };
      });
    },
    counts: function () {
      return {
        open: Number(els.openCount.textContent.replace(/[^0-9]/g, '')),
        short: Number(els.shortCount.textContent.replace(/[^0-9]/g, '')),
        closed: Number(els.closedCount.textContent.replace(/[^0-9]/g, '')),
        cards: document.querySelectorAll('.nb-grid .nb-card').length
      };
    }
  };
})();
"""


if __name__ == "__main__":
    build()

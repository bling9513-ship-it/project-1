#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""장보기 타이밍(grocery.html) — 8품목 소매가격 vs 4주 중앙값.

무엇을 보여 주나
  · aT KAMIS 공개 소매가격 조사값(grocery_data.json, grocery_crawler.py 수집)만 쓴다.
    추정·보정 없이 사이트에 적힌 값을 그대로 옮긴다.
  · 품목 카드: 오늘(최신) 조사값 · 조사일 · 규격 · 등급 · 4주(28일) 중앙값 · 중앙값 대비 등락률 칩
    (평소보다 N% 낮음 / 높음 / 비슷함) · 4주 최저·최고 · 조사값 추이 스파크라인 · 공식 출처 링크.
  · 지역 전환(서울 · 수원). 계란은 KAMIS 축산물 조사가 지역 구분 없이 전국 단일이라
    '전국' 표기를 달고 두 지역에서 같은 값을 보여 준다.
  · 관심 품목 저장(localStorage `secjobs-grocery-saved-v1`, 허용된 품목 id만 저장),
    카드 한 줄 텍스트 복사, 오늘 요약 한 줄 복사.
  · 필터(전체 · 관심 · 평소보다 낮음 · 높음)와 정렬(중앙값 대비 낮은 순 · 높은 순 · 이름순).

지키는 것
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 좌측 요약 레일 + 우측 2단 카드 / 모바일(390px) 1단 세로 배치
  · 수집값이 없으면 그리지 않는다 — 화면에 수치를 만들어 넣지 않는다.
"""
import json
import os
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "grocery_data.json")
OUT_HTML = os.path.join(BASE_DIR, "grocery.html")
KST = timezone(timedelta(hours=9))

NEUTRAL_PCT = 3.0      # 중앙값 대비 ±3% 안쪽은 '평소와 비슷'으로 본다
MIN_ITEMS = 6


# ---------------------------------------------------------------------------
# 데이터
# ---------------------------------------------------------------------------
def load_data():
    with open(DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)
    items = data.get("items") or []
    if len(items) < MIN_ITEMS:
        raise SystemExit("grocery_data.json 품목이 %d개뿐입니다(최소 %d개). grocery_crawler.py 를 먼저 실행하세요."
                         % (len(items), MIN_ITEMS))
    region_ids = [region["id"] for region in data["regionList"]]
    for item in items:
        if not item.get("unit"):
            raise SystemExit("%s 규격(단위)이 비었습니다" % item.get("name"))
        for rid in region_ids:
            stats = (item.get("byRegion") or {}).get(rid)
            if not stats:
                raise SystemExit("%s/%s 수집값이 없습니다" % (item.get("name"), rid))
            if not stats.get("series") or stats["latest"]["price"] <= 0 or stats["median"] <= 0:
                raise SystemExit("%s/%s 수치가 비정상입니다" % (item.get("name"), rid))
            if len(stats["series"]) != stats["observations"]:
                raise SystemExit("%s/%s 관측치 수와 추이 길이가 다릅니다" % (item.get("name"), rid))
    return data


def fmt(value):
    if isinstance(value, float) and not float(value).is_integer():
        return "{:,.1f}".format(value)
    return "{:,}".format(int(round(value)))


def short_date(iso):
    """2026-11-20 → 11.20"""
    return iso[5:7] + "." + iso[8:10]


def chip_of(gap):
    if gap <= -NEUTRAL_PCT:
        return {"kind": "low", "label": "평소보다 %d%% 낮음" % round(abs(gap))}
    if gap >= NEUTRAL_PCT:
        return {"kind": "high", "label": "평소보다 %d%% 높음" % round(abs(gap))}
    return {"kind": "same", "label": "평소와 비슷"}


def region_name(data, region_id):
    for region in data["regionList"]:
        if region["id"] == region_id:
            return region["name"]
    return region_id


def scope_label(item):
    return "전국" if item.get("scope") == "national" else None


def _clause(cheap, same, pricey):
    """'5개는 낮고, 2개는 비슷하며, 1개는 높습니다' 형태의 요약 절."""
    pairs = [
        (cheap, "개는 4주 중앙값보다 낮고", "개는 4주 중앙값보다 낮습니다"),
        (same, "개는 비슷하며", "개는 비슷합니다"),
        (pricey, "개는 높고", "개는 높습니다"),
    ]
    clauses = [(count, mid, end) for count, mid, end in pairs if count]
    if not clauses:
        return "값이 모였습니다"
    parts = []
    for index, (count, mid, end) in enumerate(clauses):
        last = index == len(clauses) - 1
        parts.append("%d%s" % (count, end if last else mid))
    return ", ".join(parts)


def summarize(data, region_id):
    """요약 레일 · 한 줄 문장에 쓰는 값. 모두 수집값에서 바로 계산한다."""
    cheap = same = pricey = 0
    latest_sum = median_sum = 0
    ranked = []
    latest_dates = []
    for item in data["items"]:
        stats = item["byRegion"][region_id]
        gap = stats["gapPct"]
        if gap <= -NEUTRAL_PCT:
            cheap += 1
        elif gap >= NEUTRAL_PCT:
            pricey += 1
        else:
            same += 1
        latest_sum += stats["latest"]["price"]
        median_sum += stats["median"]
        latest_dates.append(stats["latest"]["date"])
        ranked.append({"name": item["name"], "gap": gap, "price": stats["latest"]["price"],
                       "unit": item["unit"]})
    ranked.sort(key=lambda row: row["gap"])
    basket_pct = round((latest_sum - median_sum) / median_sum * 100, 1) if median_sum else 0.0
    lowest = ranked[0]
    highest = ranked[-1]
    sentence = "%d품목 중 %s." % (len(ranked), _clause(cheap, same, pricey))
    if lowest["gap"] <= -NEUTRAL_PCT:
        sentence += " 가장 많이 내린 품목은 %s(%d%%)." % (lowest["name"], round(abs(lowest["gap"])))
    if highest["gap"] >= NEUTRAL_PCT:
        sentence += " 가장 오른 품목은 %s(+%d%%)." % (highest["name"], round(highest["gap"]))
    return {
        "count": len(ranked),
        "cheap": cheap,
        "same": same,
        "pricey": pricey,
        "latestSum": latest_sum,
        "medianSum": median_sum,
        "basketPct": basket_pct,
        "sentence": sentence,
        "latestDate": max(latest_dates),
    }


# ---------------------------------------------------------------------------
# HTML 조각
# ---------------------------------------------------------------------------
def spark(series, median):
    """조사값 추이 — index 기반 x, 가격 y. 중앙값은 점선."""
    width, height, pad = 260, 44, 3
    prices = [row["p"] for row in series]
    lo, hi = min(prices + [median]), max(prices + [median])
    span = (hi - lo) or 1
    step = (width - pad * 2) / max(len(prices) - 1, 1)

    def xy(index, value):
        x = pad + index * step
        y = height - pad - (value - lo) / span * (height - pad * 2)
        return round(x, 1), round(y, 1)

    points = " ".join("%s,%s" % xy(i, v) for i, v in enumerate(prices))
    my = xy(0, median)[1]
    last_x, last_y = xy(len(prices) - 1, prices[-1])
    return (
        '<svg class="gp-spark-svg" viewBox="0 0 %d %d" width="100%%" height="%d" '
        'preserveAspectRatio="none" aria-hidden="true" focusable="false">'
        '<line x1="%s" y1="%s" x2="%s" y2="%s" class="gp-spark-median" stroke-dasharray="3 3"/>'
        '<polyline points="%s" class="gp-spark-line" fill="none"/>'
        '<circle cx="%s" cy="%s" r="2.6" class="gp-spark-dot"/>'
        "</svg>"
        % (width, height, height, pad, my, width - pad, my, points, last_x, last_y)
    )


def history_rows(series):
    rows = []
    for row in reversed(series):
        rows.append('<tr><td>%s</td><td>%s원</td></tr>' % (short_date(row["d"]), fmt(row["p"])))
    return "".join(rows)


def card_html(item, data, region_id):
    stats = item["byRegion"][region_id]
    gap = stats["gapPct"]
    chip = chip_of(gap)
    scope = scope_label(item)
    scope_text = scope if scope else region_name(data, region_id)
    unit = item["unit"]
    special = item.get("scope") == "national"
    return """
      <article class="gp-card" data-id="{id}" data-gap="{gap}" data-name="{name}" data-kind="{chip_kind}">
        <div class="gp-card-top">
          <div class="gp-card-title">
            <h3>{name}</h3>
            <span class="gp-scope{special}">{scope_text}</span>
          </div>
          <button type="button" class="gp-save" data-save="{id}" aria-pressed="false" aria-label="{name} 관심 품목으로 저장">
            <svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true" focusable="false"><path d="M12 3.6l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>
            <span>관심</span>
          </button>
        </div>
        <p class="gp-price"><strong>{price}</strong><span class="gp-won">원</span><em>/{unit}</em></p>
        <p class="gp-when">{date} 조사 · {kind} · {grade}</p>
        <p class="gp-chip-line"><span class="gp-chip is-{chip_kind}">{chip_label}</span></p>
        <div class="gp-spark" role="img" aria-label="{name} 최근 4주 조사값 추이">
          {spark}
          <span class="gp-spark-cap">최근 {n}회 조사 · 점선은 4주 중앙값</span>
        </div>
        <dl class="gp-stats">
          <div><dt>4주 중앙값</dt><dd>{median}원</dd></div>
          <div><dt>4주 최저</dt><dd>{lo}원<span class="gp-d">{lo_d}</span></dd></div>
          <div><dt>4주 최고</dt><dd>{hi}원<span class="gp-d">{hi_d}</span></dd></div>
        </dl>
        <div class="gp-actions">
          <button type="button" class="gp-copy" data-copy="{id}">한 줄 복사</button>
          <a class="gp-src" href="{url}" target="_blank" rel="noopener noreferrer">KAMIS 원문</a>
        </div>
        <details class="gp-hist">
          <summary>최근 조사값 {n}건 보기</summary>
          <table><caption class="gp-sr">{name} 조사일별 소매가격</caption>
            <thead><tr><th scope="col">조사일</th><th scope="col">가격</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </details>
        <p class="gp-copied" data-copied="{id}" role="status" aria-live="polite"></p>
      </article>""".format(
        id=item["id"], name=item["name"], gap="%.1f" % gap, chip_kind=chip["kind"],
        chip_label=chip["label"], scope_text=scope_text,
        special=" is-national" if special else "",
        price=fmt(stats["latest"]["price"]), unit=unit,
        date=short_date(stats["latest"]["date"]),
        kind=item.get("kind") or "-", grade=item.get("grade") or "-",
        spark=spark(stats["series"], stats["median"]),
        n=stats["observations"], median=fmt(stats["median"]),
        lo=fmt(stats["min"]["price"]), lo_d=short_date(stats["min"]["date"]),
        hi=fmt(stats["max"]["price"]), hi_d=short_date(stats["max"]["date"]),
        url=stats["sourceUrl"], rows=history_rows(stats["series"]),
    )


def cards_html(data, region_id):
    # 기본 정렬(중앙값 대비 낮은 순)과 같은 순서로 그려, JS 없이도 화면 순서가 같다.
    ordered = sorted(data["items"], key=lambda item: item["byRegion"][region_id]["gapPct"])
    return "".join(card_html(item, data, region_id) for item in ordered)


def region_buttons(data):
    parts = []
    for index, region in enumerate(data["regionList"]):
        active = " is-active" if index == 0 else ""
        selected = "true" if index == 0 else "false"
        parts.append(
            '<button type="button" class="gp-region%s" role="tab" id="gpRegion-%s" '
            'data-region="%s" aria-selected="%s" tabindex="%s">%s</button>'
            % (active, region["id"], region["id"], selected, "0" if index == 0 else "-1",
               region["name"])
        )
    return "".join(parts)


def sources_html(data):
    rows = [
        ('<li><a href="%s" target="_blank" rel="noopener noreferrer">%s</a>'
         '<span>간편가격정보 &gt; 소매가격 · 지역·품목·기간을 지정해 조회하는 원문 화면</span></li>'
         % (data["source"]["url"], data["source"]["label"])),
        ('<li><a href="%s" target="_blank" rel="noopener noreferrer">KAMIS 가격정보 조사요령</a>'
         '<span>조사대상 품목 · 조사방법 · 조사주기 및 지역 안내</span></li>'
         % data["source"]["howtoUrl"]),
    ]
    for item in data["items"]:
        url = item["byRegion"][data["regionList"][0]["id"]]["sourceUrl"]
        rows.append('<li><a href="%s" target="_blank" rel="noopener noreferrer">%s 조사값 원문</a>'
                    '<span>%s · %s · %s</span></li>'
                    % (url, item["name"], item.get("kind") or "-", item.get("grade") or "-",
                       item["unit"]))
    return "".join(rows)


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
      --low-bg: #ecfdf5;  --low-text: #047857;  --low-border: #a7f3d0;
      --high-bg: #fef2f2;  --high-text: #b91c1c;  --high-border: #fecaca;
      --same-bg: #f8fafc;  --same-text: #475569;  --same-border: #e2e8f0;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --low-bg: rgba(16, 185, 129, 0.12);  --low-text: #6ee7b7;  --low-border: rgba(16, 185, 129, 0.32);
      --high-bg: rgba(239, 68, 68, 0.12);  --high-text: #fca5a5;  --high-border: rgba(239, 68, 68, 0.32);
      --same-bg: rgba(148, 163, 184, 0.12);  --same-text: #cbd5e1;  --same-border: rgba(148, 163, 184, 0.28);
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body {
      font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease;
    }
    .gp-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .gp-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 96px; }
    .gp-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .gp-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 640px; word-break: keep-all; }
    .gp-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .gp-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; margin-top: 9px;
      font-size: 11.5px; color: var(--text-muted); }
    .gp-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }

    .gp-toolbar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 16px 0 14px; }
    .gp-regions { display: inline-flex; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 11px; }
    .gp-region { border: 0; background: transparent; border-radius: 8px; padding: 7px 18px; font-family: inherit;
      font-size: 13px; font-weight: 600; color: var(--text-secondary); cursor: pointer; }
    .gp-region.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: var(--card-shadow); }
    .gp-region:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .gp-toolbar-right { margin-left: auto; display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
    .gp-filters { display: inline-flex; gap: 4px; overflow-x: auto; scrollbar-width: none; }
    .gp-filters::-webkit-scrollbar { display: none; }
    .gp-filter { flex: 0 0 auto; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 999px; padding: 5px 11px; font-family: inherit;
      font-size: 11.5px; font-weight: 600; cursor: pointer; white-space: nowrap; }
    .gp-filter.is-active { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }
    .gp-filter:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .gp-sort { border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      border-radius: 9px; padding: 6px 9px; font-family: inherit; font-size: 11.5px; font-weight: 600; cursor: pointer; }

    .gp-main { display: grid; grid-template-columns: 296px minmax(0, 1fr); gap: 20px; align-items: start; }
    .gp-rail { position: sticky; top: 76px; display: grid; gap: 12px; }

    .gp-panel { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 16px; box-shadow: var(--card-shadow); }
    .gp-panel h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.01em; }
    .gp-tally { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 11px; }
    .gp-tally div { text-align: center; border-radius: 10px; padding: 8px 4px; border: 1px solid transparent; }
    .gp-tally b { display: block; font-size: 19px; font-weight: 800; letter-spacing: -0.03em; }
    .gp-tally span { font-size: 10.5px; font-weight: 600; }
    .gp-tally .is-low { background: var(--low-bg); border-color: var(--low-border); color: var(--low-text); }
    .gp-tally .is-same { background: var(--same-bg); border-color: var(--same-border); color: var(--same-text); }
    .gp-tally .is-high { background: var(--high-bg); border-color: var(--high-border); color: var(--high-text); }
    .gp-line { margin-top: 12px; font-size: 12.5px; line-height: 1.6; color: var(--text-secondary); word-break: keep-all; }
    .gp-basket { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-subtle); }
    .gp-basket-row { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; font-size: 12px;
      color: var(--text-secondary); }
    .gp-basket-row + .gp-basket-row { margin-top: 5px; }
    .gp-basket-row b { font-size: 14px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em; }
    .gp-basket-note { margin-top: 8px; font-size: 10.5px; color: var(--text-muted); line-height: 1.5; }
    .gp-copysum { width: 100%; margin-top: 12px; border: 1px solid var(--border-strong); background: var(--bg-surface);
      color: var(--text-primary); border-radius: 10px; padding: 9px; font-family: inherit; font-size: 12.5px;
      font-weight: 700; cursor: pointer; }
    .gp-copysum:hover { background: var(--bg-subtle); }
    .gp-copysum:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .gp-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .gp-card { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 15px; box-shadow: var(--card-shadow); display: flex; flex-direction: column; gap: 7px; }
    .gp-card.is-saved { border-color: var(--border-strong); }
    .gp-card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
    .gp-card-title { display: flex; align-items: center; gap: 6px; min-width: 0; }
    .gp-card-title h3 { font-size: 15.5px; font-weight: 800; letter-spacing: -0.03em; }
    .gp-scope { flex: 0 0 auto; font-size: 10px; font-weight: 700; color: var(--text-muted);
      border: 1px solid var(--border-default); border-radius: 5px; padding: 1px 5px; }
    .gp-scope.is-national { color: var(--accent-primary); border-color: var(--border-default); background: var(--accent-subtle); }
    .gp-save { flex: 0 0 auto; display: inline-flex; align-items: center; gap: 4px; border: 1px solid var(--border-default);
      background: var(--bg-surface); color: var(--text-muted); border-radius: 999px; padding: 3px 8px;
      font-family: inherit; font-size: 10.5px; font-weight: 700; cursor: pointer; }
    .gp-save[aria-pressed="true"] { color: var(--accent-primary); border-color: var(--border-default); background: var(--accent-subtle); }
    .gp-save[aria-pressed="true"] svg path { fill: currentColor; }
    .gp-save:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .gp-price { display: flex; align-items: baseline; gap: 3px; }
    .gp-price strong { font-size: 27px; font-weight: 800; letter-spacing: -0.045em; font-variant-numeric: tabular-nums; }
    .gp-won { font-size: 13px; font-weight: 700; color: var(--text-secondary); }
    .gp-price em { font-style: normal; font-size: 11.5px; font-weight: 600; color: var(--text-muted); margin-left: 3px; }
    .gp-when { font-size: 11px; color: var(--text-muted); }
    .gp-chip-line { margin-top: 1px; }
    .gp-chip { display: inline-block; font-size: 11.5px; font-weight: 700; border-radius: 7px; padding: 3px 8px; border: 1px solid transparent; }
    .gp-chip.is-low { background: var(--low-bg); color: var(--low-text); border-color: var(--low-border); }
    .gp-chip.is-high { background: var(--high-bg); color: var(--high-text); border-color: var(--high-border); }
    .gp-chip.is-same { background: var(--same-bg); color: var(--same-text); border-color: var(--same-border); }

    .gp-spark { margin-top: 3px; }
    .gp-spark-svg { display: block; width: 100%; height: 46px; }
    .gp-spark-line { stroke: var(--accent-primary); stroke-width: 1.6; stroke-linejoin: round; stroke-linecap: round; }
    .gp-spark-median { stroke: var(--text-muted); stroke-width: 1; opacity: .55; }
    .gp-spark-dot { fill: var(--accent-primary); }
    .gp-spark-cap { display: block; margin-top: 1px; font-size: 10px; color: var(--text-muted); }

    .gp-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; margin-top: 5px;
      padding-top: 9px; border-top: 1px solid var(--border-subtle); }
    .gp-stats dt { font-size: 10px; color: var(--text-muted); }
    .gp-stats dd { font-size: 12.5px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .gp-d { display: block; font-size: 9.5px; font-weight: 500; color: var(--text-muted); }
    .gp-actions { display: flex; align-items: center; gap: 8px; margin-top: 3px; }
    .gp-copy { border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      border-radius: 8px; padding: 5px 10px; font-family: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }
    .gp-copy:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .gp-copy:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .gp-src { margin-left: auto; font-size: 11px; font-weight: 600; color: var(--text-secondary);
      text-decoration: none; border-bottom: 1px solid var(--border-strong); padding-bottom: 1px; }
    .gp-src:hover { color: var(--accent-primary); border-color: var(--accent-primary); }
    .gp-copied { min-height: 15px; font-size: 10.5px; font-weight: 600; color: var(--low-text); }
    .gp-hist { margin-top: 1px; }
    .gp-hist summary { cursor: pointer; font-size: 11px; font-weight: 600; color: var(--text-secondary); }
    .gp-hist summary:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .gp-hist table { width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 11px; }
    .gp-hist th { text-align: left; font-weight: 700; color: var(--text-muted); padding: 3px 2px;
      border-bottom: 1px solid var(--border-default); }
    .gp-hist td { padding: 3px 2px; border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary);
      font-variant-numeric: tabular-nums; }
    .gp-empty { grid-column: 1 / -1; border: 1px dashed var(--border-strong); border-radius: 14px; padding: 22px;
      text-align: center; font-size: 12.5px; color: var(--text-secondary); }

    .gp-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .gp-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; }
    .gp-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .gp-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .gp-notes li b { color: var(--text-primary); }
    .gp-notes .gp-srcs { list-style: none; padding-left: 0; margin-top: 12px; padding-top: 11px;
      border-top: 1px solid var(--border-subtle); }
    .gp-notes .gp-srcs li { display: flex; flex-direction: column; gap: 1px; }
    .gp-notes .gp-srcs a { font-weight: 700; color: var(--accent-primary); text-decoration: none; font-size: 11.5px; }
    .gp-notes .gp-srcs span { font-size: 10.5px; color: var(--text-muted); }
    .gp-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 900px) {
      .gp-wrap { padding: 14px 13px 88px; }
      .gp-hero h1 { font-size: 21px; }
      .gp-hero p { font-size: 12px; }
      .gp-main { grid-template-columns: minmax(0, 1fr); gap: 12px; }
      .gp-rail { position: static; order: 2; }
      .gp-toolbar { margin: 13px 0 11px; gap: 7px; }
      .gp-toolbar-right { margin-left: 0; width: 100%; justify-content: space-between; }
      .gp-region { padding: 7px 15px; }
      .gp-grid { grid-template-columns: minmax(0, 1fr); gap: 10px; }
      .gp-card { padding: 14px; }
      .gp-price strong { font-size: 25px; }
      .gp-tally b { font-size: 17px; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 장보기 타이밍</title>
  <meta name="description" content="계란·대파·배추·무·양파·시금치·애호박·사과 8품목의 오늘 소매가격을 최근 4주 중앙값과 비교합니다. aT KAMIS 공식 소매가격 조사값만 사용하며, 서울·수원 지역을 골라 볼 수 있습니다.">
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
        <div class="update-meta"><span class="live-dot"></span><span>KAMIS 소매가격 __GENERATED__</span></div>
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

  <main class="gp-wrap">
    <section class="gp-hero">
      <span class="gp-pill">생활 · 장보기 타이밍</span>
      <h1>오늘 장볼 때, 평소보다 싼가?</h1>
      <p>aT KAMIS 공식 소매가격 조사값으로 8품목의 오늘 가격을 최근 4주 중앙값과 비교합니다. 조사일·규격·등급을 함께 적었으니 숫자만 보고 판단하지 마세요.</p>
      <div class="gp-meta">
        <span>조사 기간 __WINDOW__</span>
        <span class="gp-dot"></span>
        <span>수집 __GENERATED__</span>
        <span class="gp-dot"></span>
        <span>출처 aT KAMIS</span>
      </div>
    </section>

    <div class="gp-toolbar">
      <div class="gp-regions" role="tablist" aria-label="지역 선택">__REGION_BUTTONS__</div>
      <div class="gp-toolbar-right">
        <div class="gp-filters" role="group" aria-label="품목 필터">
          <button type="button" class="gp-filter is-active" data-filter="all" aria-pressed="true">전체</button>
          <button type="button" class="gp-filter" data-filter="saved" aria-pressed="false">관심</button>
          <button type="button" class="gp-filter" data-filter="low" aria-pressed="false">평소보다 낮음</button>
          <button type="button" class="gp-filter" data-filter="high" aria-pressed="false">높음</button>
        </div>
        <select class="gp-sort" id="gpSort" aria-label="정렬 기준">
          <option value="low">중앙값 대비 낮은 순</option>
          <option value="high">중앙값 대비 높은 순</option>
          <option value="name">품목 이름순</option>
        </select>
      </div>
    </div>

    <div class="gp-main">
      <aside class="gp-rail" aria-label="오늘 요약">
        <section class="gp-panel">
          <h2>오늘 요약 · <span id="gpSummaryRegion">__FIRST_REGION__</span></h2>
          <div class="gp-tally" id="gpTally">
            <div class="is-low"><b>__CHEAP__</b><span>평소보다 낮음</span></div>
            <div class="is-same"><b>__SAME__</b><span>평소와 비슷</span></div>
            <div class="is-high"><b>__PRICEY__</b><span>평소보다 높음</span></div>
          </div>
          <p class="gp-line" id="gpSentence">__SENTENCE__</p>
          <div class="gp-basket">
            <div class="gp-basket-row"><span>8품목 합계(최신 조사값)</span><b id="gpLatestSum">__LATEST_SUM__원</b></div>
            <div class="gp-basket-row"><span>같은 품목 4주 중앙값 합계</span><b id="gpMedianSum">__MEDIAN_SUM__원</b></div>
            <p class="gp-basket-note">품목마다 조사 규격(1kg·1포기·10구 등)이 달라 합계는 같은 규격 기준의 단순 합입니다. 장바구니 총액이 아니라 값의 방향을 보는 지표로만 쓰세요. 합계 등락 <b id="gpBasketPct">__BASKET_PCT__</b></p>
          </div>
          <button type="button" class="gp-copysum" id="gpCopySum">오늘 요약 한 줄 복사</button>
          <p class="gp-copied" id="gpCopySumState" role="status" aria-live="polite"></p>
        </section>
        <section class="gp-panel">
          <h2>읽는 법</h2>
          <p class="gp-line"><b>중앙값</b>은 최근 4주 동안 조사된 값들을 크기순으로 줄 세웠을 때 가운데 값입니다. 하루 튄 값에 흔들리지 않으려고 평균 대신 씁니다.</p>
          <p class="gp-line"><b>등락률</b>은 (최신 조사값 − 중앙값) ÷ 중앙값입니다. ±3% 안쪽은 '평소와 비슷', 그보다 낮으면 '낮음', 높으면 '높음'으로 표시합니다.</p>
        </section>
      </aside>

      <section aria-label="품목별 가격">
        <div class="gp-grid" id="gpGrid">__CARDS__</div>
      </section>
    </div>

    <section class="gp-notes">
      <h2>알아 두실 점</h2>
      <ul>
        <li><b>조사일</b> — KAMIS 소매가격은 주중에 조사되어 주말 값이 없습니다. 그래서 '오늘'은 최신 조사일 기준입니다. 축산물(계란)은 주말 포함 매일 조사됩니다.</li>
        <li><b>지역</b> — 서울·수원은 KAMIS 소매가격 조사 지역입니다. 계란은 KAMIS 축산물 조사가 지역 구분 없이 전국 단일이라 '전국' 표기를 달았고, 지역을 바꿔도 값이 같습니다.</li>
        <li><b>규격·등급</b> — 값은 카드에 적힌 규격(1kg·1포기·10구 등)과 등급(상품·일반란) 기준입니다. 매장의 포장 단위가 다르면 그대로 비교할 수 없습니다.</li>
        <li><b>조사값의 성격</b> — 대형마트와 전통시장에서 조사한 평균으로, 집 앞 마트의 실제 가격이나 할인가는 다를 수 있습니다. 값이 오르내린 방향을 보고 장보기 순서를 정하는 데 쓰세요.</li>
        <li><b>표시 원칙</b> — 화면의 모든 수치는 KAMIS 화면에 적힌 값을 그대로 옮긴 것이며, 빠진 값은 추정해 채우지 않습니다. 수집에 실패한 품목은 직전 수집값을 그대로 두고 표시합니다.</li>
      </ul>
      <ul class="gp-srcs">__SOURCES__</ul>
    </section>
    <p class="gp-foot">aT 한국농수산식품유통공사 KAMIS 공개 소매가격 조사값 · 화면 구성과 비교 계산만 이 페이지에서 합니다.</p>
  </main>

  <script type="application/json" id="gpData">__DATA_JSON__</script>
  <script>__JS__</script>
</body>
</html>
"""

JS = r"""
(function () {
  var NEUTRAL = 3;
  var SAVED_KEY = 'secjobs-grocery-saved-v1';
  var KNOWN_IDS = [];

  var data;
  try {
    data = JSON.parse(document.getElementById('gpData').textContent);
  } catch (e) { return; }

  var grid = document.getElementById('gpGrid');
  if (!grid) return;

  data.items.forEach(function (item) { KNOWN_IDS.push(item.id); });

  var state = {
    region: data.regionList[0].id,
    filter: 'all',
    sort: 'low',
    saved: loadSaved()
  };

  function loadSaved() {
    var kept = [];
    try {
      var raw = JSON.parse(localStorage.getItem(SAVED_KEY) || '[]');
      if (Array.isArray(raw)) {
        raw.forEach(function (id) {
          if (typeof id === 'string' && KNOWN_IDS.indexOf(id) >= 0 && kept.indexOf(id) < 0) kept.push(id);
        });
      }
    } catch (e) {}
    return kept;
  }

  function storeSaved() {
    try { localStorage.setItem(SAVED_KEY, JSON.stringify(state.saved)); } catch (e) {}
  }

  function fmt(value) {
    var n = Math.round(value * 10) / 10;
    var parts = String(n).split('.');
    var head = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return parts.length > 1 ? head + '.' + parts[1] : head;
  }

  function shortDate(iso) { return iso.slice(5, 7) + '.' + iso.slice(8, 10); }

  function regionName() {
    for (var i = 0; i < data.regionList.length; i++) {
      if (data.regionList[i].id === state.region) return data.regionList[i].name;
    }
    return state.region;
  }

  function statsOf(item) { return item.byRegion[state.region]; }

  function chipOf(gap) {
    if (gap <= -NEUTRAL) return { kind: 'low', label: '평소보다 ' + Math.round(Math.abs(gap)) + '% 낮음' };
    if (gap >= NEUTRAL) return { kind: 'high', label: '평소보다 ' + Math.round(Math.abs(gap)) + '% 높음' };
    return { kind: 'same', label: '평소와 비슷' };
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function svgEl(tag, attrs) {
    var node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.keys(attrs).forEach(function (key) { node.setAttribute(key, attrs[key]); });
    return node;
  }

  function spark(series, median) {
    var width = 260, height = 44, pad = 3;
    var prices = series.map(function (row) { return row.p; });
    var lo = Math.min.apply(null, prices.concat([median]));
    var hi = Math.max.apply(null, prices.concat([median]));
    var span = (hi - lo) || 1;
    var step = (width - pad * 2) / Math.max(prices.length - 1, 1);
    function y(value) { return Math.round((height - pad - (value - lo) / span * (height - pad * 2)) * 10) / 10; }

    var svg = svgEl('svg', {
      'class': 'gp-spark-svg', viewBox: '0 0 ' + width + ' ' + height, width: '100%',
      height: String(height), preserveAspectRatio: 'none', 'aria-hidden': 'true', focusable: 'false'
    });
    var medianLine = svgEl('line', {
      x1: String(pad), y1: String(y(median)), x2: String(width - pad), y2: String(y(median)),
      'class': 'gp-spark-median', 'stroke-dasharray': '3 3'
    });
    svg.appendChild(medianLine);
    var points = prices.map(function (value, index) {
      return Math.round((pad + index * step) * 10) / 10 + ',' + y(value);
    }).join(' ');
    svg.appendChild(svgEl('polyline', { points: points, 'class': 'gp-spark-line', fill: 'none' }));
    var dot = svgEl('circle', {
      cx: String(Math.round((pad + (prices.length - 1) * step) * 10) / 10),
      cy: String(y(prices[prices.length - 1])), r: '2.6', 'class': 'gp-spark-dot'
    });
    svg.appendChild(dot);
    return svg;
  }

  function buildCard(item) {
    var stats = statsOf(item);
    var chip = chipOf(stats.gapPct);
    var scopeText = item.scope === 'national' ? '전국' : regionName();

    var card = el('article', 'gp-card');
    card.dataset.id = item.id;
    card.dataset.gap = stats.gapPct.toFixed(1);
    card.dataset.name = item.name;
    card.dataset.kind = chip.kind;
    if (state.saved.indexOf(item.id) >= 0) card.classList.add('is-saved');

    var top = el('div', 'gp-card-top');
    var titleBox = el('div', 'gp-card-title');
    titleBox.appendChild(el('h3', '', item.name));
    var scope = el('span', 'gp-scope' + (item.scope === 'national' ? ' is-national' : ''), scopeText);
    titleBox.appendChild(scope);
    top.appendChild(titleBox);

    var saveBtn = el('button', 'gp-save');
    saveBtn.type = 'button';
    saveBtn.dataset.save = item.id;
    saveBtn.setAttribute('aria-pressed', state.saved.indexOf(item.id) >= 0 ? 'true' : 'false');
    saveBtn.setAttribute('aria-label', item.name + ' 관심 품목으로 저장');
    var star = svgEl('svg', { viewBox: '0 0 24 24', width: '13', height: '13', 'aria-hidden': 'true', focusable: 'false' });
    var path = svgEl('path', {
      d: 'M12 3.6l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z',
      fill: 'none', stroke: 'currentColor', 'stroke-width': '1.6', 'stroke-linejoin': 'round'
    });
    star.appendChild(path);
    saveBtn.appendChild(star);
    saveBtn.appendChild(el('span', '', '관심'));
    top.appendChild(saveBtn);
    card.appendChild(top);

    var price = el('p', 'gp-price');
    price.appendChild(el('strong', '', fmt(stats.latest.price)));
    price.appendChild(el('span', 'gp-won', '원'));
    price.appendChild(el('em', '', '/' + item.unit));
    card.appendChild(price);

    card.appendChild(el('p', 'gp-when', shortDate(stats.latest.date) + ' 조사 · ' +
      (item.kind || '-') + ' · ' + (item.grade || '-')));

    var chipLine = el('p', 'gp-chip-line');
    chipLine.appendChild(el('span', 'gp-chip is-' + chip.kind, chip.label));
    card.appendChild(chipLine);

    var sparkBox = el('div', 'gp-spark');
    sparkBox.setAttribute('role', 'img');
    sparkBox.setAttribute('aria-label', item.name + ' 최근 4주 조사값 추이');
    sparkBox.appendChild(spark(stats.series, stats.median));
    sparkBox.appendChild(el('span', 'gp-spark-cap', '최근 ' + stats.observations + '회 조사 · 점선은 4주 중앙값'));
    card.appendChild(sparkBox);

    var dl = el('dl', 'gp-stats');
    function stat(label, value, sub) {
      var wrap = el('div');
      wrap.appendChild(el('dt', '', label));
      var dd = el('dd', '', value);
      if (sub) dd.appendChild(el('span', 'gp-d', sub));
      wrap.appendChild(dd);
      dl.appendChild(wrap);
    }
    stat('4주 중앙값', fmt(stats.median) + '원');
    stat('4주 최저', fmt(stats.min.price) + '원', shortDate(stats.min.date));
    stat('4주 최고', fmt(stats.max.price) + '원', shortDate(stats.max.date));
    card.appendChild(dl);

    var actions = el('div', 'gp-actions');
    var copyBtn = el('button', 'gp-copy', '한 줄 복사');
    copyBtn.type = 'button';
    copyBtn.dataset.copy = item.id;
    actions.appendChild(copyBtn);
    var src = el('a', 'gp-src', 'KAMIS 원문');
    src.href = stats.sourceUrl;
    src.target = '_blank';
    src.rel = 'noopener noreferrer';
    actions.appendChild(src);
    card.appendChild(actions);

    var hist = el('details', 'gp-hist');
    hist.appendChild(el('summary', '', '최근 조사값 ' + stats.observations + '건 보기'));
    var table = el('table');
    var cap = el('caption', 'gp-sr', item.name + ' 조사일별 소매가격');
    table.appendChild(cap);
    var thead = el('thead');
    var hr = el('tr');
    var th1 = el('th', '', '조사일');
    th1.setAttribute('scope', 'col');
    var th2 = el('th', '', '가격');
    th2.setAttribute('scope', 'col');
    hr.appendChild(th1); hr.appendChild(th2);
    thead.appendChild(hr);
    table.appendChild(thead);
    var tbody = el('tbody');
    stats.series.slice().reverse().forEach(function (row) {
      var tr = el('tr');
      tr.appendChild(el('td', '', shortDate(row.d)));
      tr.appendChild(el('td', '', fmt(row.p) + '원'));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    hist.appendChild(table);
    card.appendChild(hist);

    var copied = el('p', 'gp-copied', '');
    copied.dataset.copied = item.id;
    copied.setAttribute('role', 'status');
    copied.setAttribute('aria-live', 'polite');
    card.appendChild(copied);
    return card;
  }

  function visibleItems() {
    var list = data.items.filter(function (item) {
      if (state.filter === 'saved') return state.saved.indexOf(item.id) >= 0;
      if (state.filter === 'low') return statsOf(item).gapPct <= -NEUTRAL;
      if (state.filter === 'high') return statsOf(item).gapPct >= NEUTRAL;
      return true;
    });
    if (state.sort === 'name') {
      list.sort(function (a, b) { return a.name.localeCompare(b.name, 'ko'); });
    } else if (state.sort === 'high') {
      list.sort(function (a, b) { return statsOf(b).gapPct - statsOf(a).gapPct; });
    } else {
      list.sort(function (a, b) { return statsOf(a).gapPct - statsOf(b).gapPct; });
    }
    return list;
  }

  function renderGrid() {
    var list = visibleItems();
    grid.textContent = '';
    if (!list.length) {
      grid.appendChild(el('p', 'gp-empty',
        state.filter === 'saved' ? '저장한 관심 품목이 없습니다. 카드의 관심 버튼을 눌러 담아 두세요.'
                                  : '이 조건에 맞는 품목이 없습니다.'));
      return;
    }
    list.forEach(function (item) { grid.appendChild(buildCard(item)); });
  }

  function summary() {
    var cheap = 0, same = 0, pricey = 0, latestSum = 0, medianSum = 0;
    var ranked = data.items.map(function (item) {
      var stats = statsOf(item);
      if (stats.gapPct <= -NEUTRAL) cheap += 1;
      else if (stats.gapPct >= NEUTRAL) pricey += 1;
      else same += 1;
      latestSum += stats.latest.price;
      medianSum += stats.median;
      return { name: item.name, gap: stats.gapPct };
    }).sort(function (a, b) { return a.gap - b.gap; });
    var pct = medianSum ? Math.round((latestSum - medianSum) / medianSum * 1000) / 10 : 0;
    var pairs = [
      [cheap, '개는 4주 중앙값보다 낮고', '개는 4주 중앙값보다 낮습니다'],
      [same, '개는 비슷하며', '개는 비슷합니다'],
      [pricey, '개는 높고', '개는 높습니다']
    ].filter(function (row) { return row[0] > 0; });
    var parts = pairs.map(function (row, index) {
      return row[0] + (index === pairs.length - 1 ? row[2] : row[1]);
    });
    var sentence = ranked.length + '품목 중 ' + (parts.join(', ') || '값이 모였습니다') + '.';
    if (ranked[0].gap <= -NEUTRAL) sentence += ' 가장 많이 내린 품목은 ' + ranked[0].name + '(' + Math.round(Math.abs(ranked[0].gap)) + '%).';
    if (ranked[ranked.length - 1].gap >= NEUTRAL) sentence += ' 가장 오른 품목은 ' + ranked[ranked.length - 1].name + '(+' + Math.round(ranked[ranked.length - 1].gap) + '%).';
    return { cheap: cheap, same: same, pricey: pricey, latestSum: latestSum, medianSum: medianSum,
             pct: pct, sentence: sentence, ranked: ranked };
  }

  function renderSummary() {
    var info = summary();
    var tally = document.getElementById('gpTally');
    if (!tally) return;
    var cells = tally.children;
    if (cells.length === 3) {
      cells[0].firstChild.textContent = String(info.cheap);
      cells[1].firstChild.textContent = String(info.same);
      cells[2].firstChild.textContent = String(info.pricey);
    }
    document.getElementById('gpSentence').textContent = info.sentence;
    document.getElementById('gpLatestSum').textContent = fmt(info.latestSum) + '원';
    document.getElementById('gpMedianSum').textContent = fmt(info.medianSum) + '원';
    document.getElementById('gpBasketPct').textContent =
      (info.pct > 0 ? '+' : '') + info.pct + '%';
    document.getElementById('gpSummaryRegion').textContent = regionName();
  }

  function renderRegionButtons() {
    var buttons = document.querySelectorAll('.gp-region');
    Array.prototype.forEach.call(buttons, function (button) {
      var active = button.dataset.region === state.region;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-selected', active ? 'true' : 'false');
      button.tabIndex = active ? 0 : -1;
    });
  }

  function oneLine(item) {
    var stats = statsOf(item);
    var chip = chipOf(stats.gapPct);
    return item.name + ' ' + item.unit + ' ' + fmt(stats.latest.price) + '원 (' +
      shortDate(stats.latest.date) + ' 조사, ' + regionName() + ') · 4주 중앙값 ' +
      fmt(stats.median) + '원 · ' + chip.label;
  }

  function summaryLine(info) {
    var bits = info.ranked.slice(0, 4).map(function (row) {
      var sign = row.gap > 0 ? '+' : '';
      return row.name + ' ' + sign + row.gap.toFixed(1) + '%';
    }).join(' · ');
    return '장보기 타이밍 ' + regionName() + ' · 중앙값 대비 ' + bits;
  }

  function copyText(text, target) {
    function done(ok) {
      if (target) target.textContent = ok ? '복사했습니다' : '복사가 막혀 있습니다. 길게 눌러 선택해 주세요.';
      if (ok) window.setTimeout(function () { if (target) target.textContent = ''; }, 2200);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(); });
      return;
    }
    fallback();
    function fallback() {
      try {
        var area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', 'readonly');
        area.style.position = 'fixed';
        area.style.top = '-1000px';
        document.body.appendChild(area);
        area.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(area);
        done(ok);
      } catch (e) { done(false); }
    }
  }

  function findItem(id) {
    for (var i = 0; i < data.items.length; i++) { if (data.items[i].id === id) return data.items[i]; }
    return null;
  }

  function toggleSaved(id) {
    if (KNOWN_IDS.indexOf(id) < 0) return;
    var index = state.saved.indexOf(id);
    if (index >= 0) state.saved.splice(index, 1); else state.saved.push(id);
    storeSaved();
    renderGrid();
    renderFilterButtons();
  }

  function renderFilterButtons() {
    Array.prototype.forEach.call(document.querySelectorAll('.gp-filter'), function (button) {
      if (button.dataset.filter === 'saved') {
        button.textContent = '관심' + (state.saved.length ? ' ' + state.saved.length : '');
      }
      var active = button.dataset.filter === state.filter;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }

  document.addEventListener('click', function (event) {
    var target = event.target;
    var regionBtn = target.closest ? target.closest('.gp-region') : null;
    if (regionBtn) {
      state.region = regionBtn.dataset.region;
      renderRegionButtons();
      renderGrid();
      renderSummary();
      return;
    }
    var filterBtn = target.closest ? target.closest('.gp-filter') : null;
    if (filterBtn) {
      state.filter = filterBtn.dataset.filter;
      renderFilterButtons();
      renderGrid();
      return;
    }
    var saveBtn = target.closest ? target.closest('[data-save]') : null;
    if (saveBtn) {
      toggleSaved(saveBtn.dataset.save);
      return;
    }
    var copyBtn = target.closest ? target.closest('[data-copy]') : null;
    if (copyBtn) {
      var item = findItem(copyBtn.dataset.copy);
      if (!item) return;
      var status = document.querySelector('[data-copied="' + copyBtn.dataset.copy + '"]');
      copyText(oneLine(item), status);
      return;
    }
  });

  document.addEventListener('keydown', function (event) {
    var buttons = document.querySelectorAll('.gp-region');
    if (!buttons.length) return;
    var current = document.activeElement;
    if (!current || !current.classList || !current.classList.contains('gp-region')) return;
    var index = Array.prototype.indexOf.call(buttons, current);
    var next = null;
    if (event.key === 'ArrowRight') next = buttons[(index + 1) % buttons.length];
    if (event.key === 'ArrowLeft') next = buttons[(index - 1 + buttons.length) % buttons.length];
    if (!next) return;
    event.preventDefault();
    next.focus();
    next.click();
  });

  var sort = document.getElementById('gpSort');
  if (sort) {
    sort.addEventListener('change', function () {
      state.sort = sort.value;
      renderGrid();
    });
  }

  var copySum = document.getElementById('gpCopySum');
  if (copySum) {
    copySum.addEventListener('click', function () {
      copyText(summaryLine(summary()), document.getElementById('gpCopySumState'));
    });
  }

  renderRegionButtons();
  renderFilterButtons();
  renderGrid();
  renderSummary();
})();
"""


def build():
    data = load_data()
    first_region = data["regionList"][0]["id"]
    info = summarize(data, first_region)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__GENERATED__", data["generated"])
            .replace("__WINDOW__", "%s ~ %s" % (data["window"]["start"], data["window"]["end"]))
            .replace("__REGION_BUTTONS__", region_buttons(data))
            .replace("__FIRST_REGION__", region_name(data, first_region))
            .replace("__CHEAP__", str(info["cheap"]))
            .replace("__SAME__", str(info["same"]))
            .replace("__PRICEY__", str(info["pricey"]))
            .replace("__SENTENCE__", info["sentence"])
            .replace("__LATEST_SUM__", fmt(info["latestSum"]))
            .replace("__MEDIAN_SUM__", fmt(info["medianSum"]))
            .replace("__BASKET_PCT__", ("+" if info["basketPct"] > 0 else "") + ("%s%%" % info["basketPct"]))
            .replace("__CARDS__", cards_html(data, first_region))
            .replace("__SOURCES__", sources_html(data))
            .replace("__DATA_JSON__", payload)
            .replace("__JS__", JS))

    with open(OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "grocery")))

    print("-> 'grocery.html' 생성 완료 (품목 %d개 · %s ~ %s 기준)"
          % (len(data["items"]), data["window"]["start"], data["window"]["end"]))
    return {
        "items": len(data["items"]),
        "regions": len(data["regionList"]),
        "generated": data["generated"],
        "window": data["window"],
    }


if __name__ == "__main__":
    build()

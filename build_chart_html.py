# -*- coding: utf-8 -*-
"""
차트 추리실 (chart.html) 빌더.

- 문제 데이터는 chart_data.json (Yahoo Finance 과거 일별·주별 시세를 잘라 둔 것) 하나뿐이다.
  차트에 그리는 시가·고가·저가·종가·거래량은 실제 과거 값이고, 가려진 구간의 정답도
  chart_fetch_data.py 가 실제 종가로 계산해 넣는다(빌드 단계에서 다시 검증한다).
- 처음에는 가격·거래량만 보이고, '단서 보기'를 누를 때마다 기술적 단서 3개가 차례로 열린다.
  정답을 고르면 가려져 있던 기간·종목·출처·해설이 함께 공개된다.
- 진행 기록은 localStorage(secjobs-chart-v1)에만 남는다.
"""
import json
import os
import statistics
from datetime import datetime, timezone, timedelta
from html import escape as esc

from html_guard import harden_html, safe_json_for_script

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "chart_data.json")
CHART_HTML = os.path.join(BASE_DIR, "chart.html")

CATEGORIES = [
    {"key": "domestic", "label": "국내 증시"},
    {"key": "bigtech", "label": "미국 빅테크"},
    {"key": "market", "label": "지수·원자재"},
    {"key": "event", "label": "금융 이벤트"},
]

FLOW_BANDS = {
    "surge": "10% 넘게 상승",
    "up": "2~10% 상승",
    "flat": "보합권(±2% 이내)",
    "down": "2~10% 하락",
    "plunge": "10% 넘게 하락",
}


# ---------------------------------------------------------------- 단서 생성
def _pct(a, b):
    return (a / b - 1.0) * 100.0 if b else 0.0


def _sma(values, n):
    window = values[-n:]
    return sum(window) / len(window)


def _fmt(value):
    if abs(value) >= 1000:
        return "{:,.0f}".format(value)
    if abs(value) >= 100:
        return "{:.1f}".format(value)
    return "{:.2f}".format(value)


def build_clues(bars, split_index, interval):
    """보이는 구간만으로 단서 3개를 만든다(가려진 값은 쓰지 않는다)."""
    visible = bars[: split_index + 1]
    closes = [b[4] for b in visible]
    vols = [b[5] for b in visible]
    last = closes[-1]
    ma20 = _sma(closes, 20)
    ma60 = _sma(closes, 60)

    # 1) 거래량(없으면 일간 등락)
    if any(v > 0 for v in vols):
        recent = sum(vols[-5:]) / 5.0
        base = sum(vols[-25:-5]) / max(1, len(vols[-25:-5]))
        ratio = recent / base if base else 1.0
        if ratio >= 1.25:
            vol_text = "최근 5봉 평균 거래량은 그 앞 20봉 평균의 %.1f배로 늘었습니다. 매수·매도 공방이 커진 자리입니다." % ratio
        elif ratio <= 0.8:
            vol_text = "최근 5봉 평균 거래량은 그 앞 20봉 평균의 %.1f배로 줄었습니다. 관망세가 짙어진 자리입니다." % ratio
        else:
            vol_text = "최근 5봉 평균 거래량은 그 앞 20봉 평균과 비슷한 수준(%.1f배)입니다." % ratio
    else:
        recent = [abs(_pct(closes[i], closes[i - 1])) for i in range(len(closes) - 5, len(closes))]
        base = [abs(_pct(closes[i], closes[i - 1])) for i in range(max(1, len(closes) - 25), len(closes) - 5)]
        if recent and base:
            vol_text = ("이 자산은 거래량이 공개되지 않아 아래 패널에 일간 등락률을 그렸습니다. "
                        "최근 5봉 평균 변동은 %.1f%%p로 그 앞 20봉(%.1f%%p)과 견줄 만합니다."
                        % (sum(recent) / len(recent), sum(base) / len(base)))
        else:
            vol_text = "이 자산은 거래량이 공개되지 않아 아래 패널에 일간 등락률을 그렸습니다."

    # 2) 추세(이동평균)
    gap20 = _pct(last, ma20)
    side = "위" if gap20 >= 0 else "아래"
    cross = "위" if ma20 >= ma60 else "아래"
    trend_text = ("현재가는 20봉 이동평균보다 %.1f%% %s에 있고, 20봉선은 60봉선 %s에 있습니다."
                  % (abs(gap20), side, cross))
    if abs(gap20) >= 8:
        trend_text += " 단기선에서 꽤 벌어진 자리라 되돌림이 나오기 쉬운 위치입니다."

    # 3) 변동성과 구간 내 위치
    rets = [_pct(closes[i], closes[i - 1]) for i in range(1, len(closes))]
    recent_vol = statistics.pstdev(rets[-20:]) if len(rets) >= 20 else statistics.pstdev(rets)
    base_vol = statistics.pstdev(rets[-40:-20]) if len(rets) >= 40 else recent_vol
    trend_word = "커졌" if recent_vol > base_vol * 1.1 else ("작아졌" if recent_vol < base_vol * 0.9 else "비슷해졌")
    window = visible[-60:]
    hi = max(b[2] for b in window)
    lo = min(b[3] for b in window)
    span_text = ("최근 20봉 일간 등락 표준편차는 %.1f%%로 그 앞 20봉(%.1f%%)보다 %s습니다. "
                 "현재가는 최근 60봉 최고가보다 %.0f%% 아래, 최저가보다 %.0f%% 위에 있습니다."
                 % (recent_vol, base_vol, trend_word,
                    abs(_pct(last, hi)), abs(_pct(last, lo)) if lo else 0))
    if interval == "1wk":
        span_text = "주봉 기준입니다. " + span_text.replace("일간 등락", "주간 등락")

    return [
        {"key": "volume", "label": "거래량", "text": vol_text},
        {"key": "trend", "label": "추세", "text": trend_text},
        {"key": "risk", "label": "변동성·위치", "text": span_text},
    ]


# ---------------------------------------------------------------- 데이터
def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    episodes = data["episodes"]
    for index, ep in enumerate(episodes):
        bars = ep["bars"]
        split = ep["split_index"]
        if not (0 < split < len(bars) - 1):
            raise SystemExit("[중단] %s: 가려진 구간이 없습니다" % ep["id"])
        ep["ordinal"] = index + 1
        ep["clues"] = build_clues(bars, split, ep["interval"])
        # 정답이 실제 데이터와 맞는지 빌드 때마다 다시 확인한다.
        seg = bars[split + 1:]
        ret = _pct(seg[-1][4], bars[split][4])
        ep["future_return"] = round(ret, 2)
        quiz = ep["quiz"]
        if len(quiz["choices"]) != 4 or not (0 <= quiz["answer"] < 4):
            raise SystemExit("[중단] %s: 보기가 4개가 아니거나 정답 위치가 잘못됐습니다" % ep["id"])
        if quiz["type"] == "next":
            label = quiz["choices"][quiz["answer"]]
            if FLOW_BANDS.get(quiz["band"]) != label:
                raise SystemExit("[중단] %s: 정답 라벨이 구간과 맞지 않습니다" % ep["id"])
            expect = "surge" if ret >= 10 else "up" if ret >= 2 else "down" if ret <= -10 else "plunge"
            if ret >= 10:
                expect = "surge"
            elif ret >= 2:
                expect = "up"
            elif ret > -2:
                expect = "flat"
            elif ret > -10:
                expect = "down"
            else:
                expect = "plunge"
            if expect != quiz["band"]:
                raise SystemExit("[중단] %s: 계산된 다음 구간 %.1f%% 와 정답(%s)이 어긋납니다"
                                 % (ep["id"], ret, quiz["band"]))
        elif quiz["type"] == "regime":
            if not quiz["choices"][quiz["answer"]]:
                raise SystemExit("[중단] %s: 정답 문구가 비었습니다" % ep["id"])
        else:
            raise SystemExit("[중단] %s: 알 수 없는 문제 유형 %s" % (ep["id"], quiz["type"]))
    return data


# ---------------------------------------------------------------- 조각 렌더
def render_arc_card(ep):
    cat = next(c for c in CATEGORIES if c["key"] == ep["category"])
    unknown = "다음 구간의 흐름은?" if ep["quiz"]["type"] == "next" else "이 직후에 벌어진 일은?"
    return (
        '        <button class="arc-card" type="button" data-id="%s" data-cat="%s" data-ordinal="%d">\n'
        '          <div class="arc-top"><span class="arc-no">#%02d · %s</span>'
        '<span class="arc-state" data-state></span></div>\n'
        '          <div class="arc-title">%s</div>\n'
        '          <div class="arc-foot"><span class="arc-bars">%d봉 · %s</span>'
        '<span class="arc-solved" data-solved></span></div>\n'
        '        </button>\n'
        % (esc(ep["id"]), esc(ep["category"]), ep["ordinal"], ep["ordinal"], esc(cat["label"]),
           esc(unknown), len(ep["bars"]), "주봉" if ep["interval"] == "1wk" else "일봉")
    )


def render_cat_chips(episodes):
    counts = {}
    for ep in episodes:
        counts[ep["category"]] = counts.get(ep["category"], 0) + 1
    parts = ['<button class="chip active" type="button" data-cat="all">전체 <em>%d</em></button>'
             % len(episodes)]
    for cat in CATEGORIES:
        parts.append('<button class="chip" type="button" data-cat="%s">%s <em>%d</em></button>'
                     % (esc(cat["key"]), esc(cat["label"]), counts.get(cat["key"], 0)))
    return "".join(parts)


# ---------------------------------------------------------------- CSS
CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;

      --bg-page: #f8fafc;
      --bg-surface: #ffffff;
      --bg-subtle: #f1f5f9;
      --bg-muted: #e2e8f0;

      --border-subtle: #f1f5f9;
      --border-default: #e2e8f0;
      --border-strong: #cbd5e1;

      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;

      --accent-primary: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;

      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --cat-domestic: #2563eb;
      --cat-bigtech: #7c3aed;
      --cat-market: #d97706;
      --cat-event: #dc2626;

      --up: #ef4444;
      --down: #2563eb;
      --ma20: #64748b;
      --ma60: #94a3b8;
      --grid: #eef2f7;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
    }

    [data-theme="dark"] {
      --bg-page: #09090b;
      --bg-surface: #18181b;
      --bg-subtle: #27272a;
      --bg-muted: #3f3f46;

      --border-subtle: #1f1f23;
      --border-default: #27272a;
      --border-strong: #3f3f46;

      --text-primary: #f4f4f5;
      --text-secondary: #a1a1aa;
      --text-muted: #71717a;

      --accent-primary: #3b82f6;
      --accent-hover: #60a5fa;
      --accent-subtle: rgba(59, 130, 246, 0.15);

      --ok-bg: rgba(16, 185, 129, 0.12);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.32);
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);

      --cat-domestic: #60a5fa;
      --cat-bigtech: #a78bfa;
      --cat-market: #fbbf24;
      --cat-event: #f87171;

      --up: #f87171;
      --down: #60a5fa;
      --ma20: #a1a1aa;
      --ma60: #71717a;
      --grid: #232327;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }

    html { scroll-behavior: smooth; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-page);
      color: var(--text-primary);
      line-height: 1.5;
      letter-spacing: -0.02em;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    a { color: inherit; }

    .navbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    .nav-container {
      max-width: 1360px;
      margin: 0 auto;
      padding: 0 20px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }

    .brand-logo-img {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      object-fit: cover;
      display: block;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
      flex-shrink: 0;
    }

    .brand-name {
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      white-space: nowrap;
    }

    .nav-tabs {
      display: flex;
      gap: 5px;
      margin-left: 10px;
      flex: 1 1 auto;
      min-width: 0;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }

    .nav-tabs::-webkit-scrollbar { display: none; }

    .nav-tab-item {
      padding: 5px 10px;
      border-radius: 18px;
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      color: var(--text-secondary);
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .nav-tab-item:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .nav-tab-item.active { background: var(--accent-primary); color: #ffffff !important; }

    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .update-meta {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
      white-space: nowrap;
    }

    .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      flex-shrink: 0;
    }

    .icon-btn {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
      text-decoration: none;
    }

    .icon-btn:hover {
      background: var(--bg-subtle);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }

    .container { max-width: 900px; margin: 0 auto; padding: 32px 20px 80px; }

    .hero { margin-bottom: 18px; }

    .hero-pill {
      display: inline-block;
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 9px;
      margin-bottom: 12px;
    }

    .hero-title { font-size: 26px; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 8px; }

    .hero-desc {
      font-size: 14.5px;
      color: var(--text-secondary);
      line-height: 1.65;
      margin-bottom: 14px;
      max-width: 760px;
    }

    .hero-stats { display: flex; flex-wrap: wrap; gap: 8px; }

    .stat-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .stat-chip strong { color: var(--text-primary); font-weight: 600; }

    .panel {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      margin-bottom: 14px;
      min-width: 0;
    }

    .player { padding: 20px; }

    .player-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .player-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0; }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: 999px;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .badge::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
      flex-shrink: 0;
    }

    .badge.cat-domestic::before { background: var(--cat-domestic); }
    .badge.cat-bigtech::before { background: var(--cat-bigtech); }
    .badge.cat-market::before { background: var(--cat-market); }
    .badge.cat-event::before { background: var(--cat-event); }

    .player-date { font-size: 12px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    .today-tag {
      font-size: 10.5px;
      font-weight: 600;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border-radius: 5px;
      padding: 2px 7px;
    }

    .dots { display: flex; align-items: center; gap: 5px; }

    .dots .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--bg-muted);
      display: block;
      transition: background-color 0.2s ease;
    }

    .dots .dot.on { background: var(--accent-primary); }

    .player-title { font-size: 19px; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 4px; }

    .player-sub { font-size: 12.5px; color: var(--text-muted); margin-bottom: 4px; }

    .chart-card {
      border: 1px solid var(--border-default);
      border-radius: 12px;
      background: var(--bg-surface);
      padding: 12px 12px 10px;
      margin: 14px 0 16px;
      min-width: 0;
    }

    .chart-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 6px;
      flex-wrap: wrap;
    }

    .chart-legend { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 11px; color: var(--text-muted); }

    .chart-legend .item { display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }

    .chart-legend .swatch { width: 12px; height: 3px; border-radius: 2px; display: inline-block; background: var(--text-muted); }

    .chart-legend .swatch.up { background: var(--up); }
    .chart-legend .swatch.down { background: var(--down); }
    .chart-legend .swatch.ma20 { background: var(--ma20); }
    .chart-legend .swatch.ma60 { background: var(--ma60); }

    .chart-wrap { position: relative; }

    .chart-wrap svg { width: 100%; height: auto; display: block; touch-action: pan-y; }

    .svg-grid { stroke: var(--grid); stroke-width: 1; }
    .svg-axis { fill: var(--text-muted); font-size: 10.5px; font-family: var(--font-sans); }
    .svg-future { fill: var(--bg-subtle); opacity: 0.55; }
    .svg-hidden-label { fill: var(--text-muted); font-size: 12px; font-weight: 600; font-family: var(--font-sans); }
    .svg-hidden-sub { fill: var(--text-muted); font-size: 10.5px; font-family: var(--font-sans); }
    .svg-divider { stroke: var(--border-strong); stroke-width: 1; stroke-dasharray: 3 3; }
    .candle-up { fill: var(--up); }
    .candle-down { fill: var(--down); }
    .wick-up { stroke: var(--up); stroke-width: 1; }
    .wick-down { stroke: var(--down); stroke-width: 1; }
    .is-future { opacity: 0.5; }
    .ma-line { fill: none; stroke-width: 1.6; }
    .ma-20 { stroke: var(--ma20); }
    .ma-60 { stroke: var(--ma60); stroke-dasharray: 4 3; }
    .ma-group { display: none; }
    .show-ma .ma-group { display: inline; }
    .vol-divider { stroke: var(--border-default); stroke-width: 1; }
    .bar-hit { fill: transparent; }
    .hover-line { stroke: var(--border-strong); stroke-width: 1; stroke-dasharray: 2 2; }

    .tooltip {
      position: absolute;
      z-index: 5;
      pointer-events: none;
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      border-radius: 8px;
      box-shadow: var(--card-shadow-hover);
      padding: 7px 9px;
      font-size: 11.5px;
      line-height: 1.55;
      color: var(--text-primary);
      white-space: nowrap;
      transform: translate(-50%, -100%);
      font-variant-numeric: tabular-nums;
    }

    .tooltip .tip-dim { color: var(--text-muted); }

    .axis-note { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

    .chart-empty { padding: 30px 0; text-align: center; font-size: 12.5px; color: var(--text-muted); }

    .clues { display: flex; flex-direction: column; gap: 8px; }

    .clue {
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 12px 14px;
      background: var(--bg-surface);
      min-width: 0;
    }

    .clue.open { background: var(--bg-page); }

    .clue.locked {
      border-style: dashed;
      background: transparent;
    }

    .clue-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 5px;
    }

    .clue-label {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.01em;
      color: var(--accent-primary);
    }

    .clue.locked .clue-label { color: var(--text-muted); }

    .clue-step { font-size: 10.5px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    .clue-text { font-size: 13.5px; line-height: 1.65; color: var(--text-primary); }

    .clue.locked .clue-text { color: var(--text-muted); font-size: 12.5px; }

    .clue-foot {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 12px;
      flex-wrap: wrap;
    }

    .btn {
      font-family: inherit;
      border-radius: 9px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: -0.02em;
      padding: 9px 16px;
      cursor: pointer;
      transition: all 0.15s ease;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-primary);
      white-space: nowrap;
    }

    .btn:hover { background: var(--bg-subtle); border-color: var(--border-strong); }

    .btn:disabled { opacity: 0.55; cursor: default; }

    .btn-line { border-color: var(--border-strong); }

    .btn-sm { padding: 6px 11px; font-size: 12px; border-radius: 8px; }

    .btn-primary {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #ffffff;
    }

    .btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }

    .btn-text {
      font-family: inherit;
      border: none;
      background: none;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      padding: 4px 2px;
      cursor: pointer;
      text-decoration: underline;
      text-underline-offset: 3px;
    }

    .btn-text:hover { color: var(--text-primary); }

    .clue-note { font-size: 11.5px; color: var(--text-muted); }

    .ask {
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
    }

    .ask-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 6px;
    }

    .ask-label { font-size: 11px; font-weight: 700; letter-spacing: 0.02em; color: var(--text-muted); }

    .ask-hint { font-size: 11.5px; color: var(--text-muted); }

    .ask-q { font-size: 15px; font-weight: 600; margin-bottom: 10px; }

    .options { display: flex; flex-direction: column; gap: 7px; }

    .opt {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      text-align: left;
      font-family: inherit;
      font-size: 13.5px;
      font-weight: 500;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 11px 13px;
      cursor: pointer;
      transition: all 0.15s ease;
      min-width: 0;
    }

    .opt:hover { border-color: var(--border-strong); background: var(--bg-subtle); }

    .opt:disabled { cursor: default; }

    .opt .key {
      flex: 0 0 20px;
      width: 20px;
      height: 20px;
      border-radius: 6px;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      font-size: 10.5px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .opt .body { min-width: 0; flex: 1 1 auto; }

    .opt.is-correct {
      border-color: var(--ok-border);
      background: var(--ok-bg);
      color: var(--ok-text);
    }

    .opt.is-correct .key { background: var(--ok-border); color: var(--ok-text); }

    .opt.is-wrong {
      border-color: var(--no-border);
      background: var(--no-bg);
      color: var(--no-text);
    }

    .opt.is-wrong .key { background: var(--no-border); color: var(--no-text); }

    .ask-foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-top: 10px;
      flex-wrap: wrap;
    }

    .ask-msg { font-size: 12px; color: var(--text-secondary); }
    .ask-msg.no { color: var(--no-text); }

    .result {
      margin-top: 16px;
      border: 1px solid var(--ok-border);
      background: var(--ok-bg);
      border-radius: 12px;
      padding: 15px 16px;
    }

    .result.gave-up { border-color: var(--border-strong); background: var(--bg-page); }

    .result-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }

    .result-badge {
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 5px;
      background: var(--ok-text);
      color: #ffffff;
    }

    .result.gave-up .result-badge { background: var(--text-muted); }

    .result-title { font-size: 14px; font-weight: 700; color: var(--ok-text); }

    .result.gave-up .result-title { color: var(--text-primary); }

    .reveal {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 14px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 12px 13px;
      margin-bottom: 12px;
    }

    .reveal .rv { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
    .reveal .rv-k { font-size: 10.5px; font-weight: 700; color: var(--text-muted); }
    .reveal .rv-v { font-size: 12.5px; color: var(--text-primary); word-break: break-word; }
    .reveal a { color: var(--accent-primary); text-decoration: underline; text-underline-offset: 2px; }

    .result-answer { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }

    .result-answer strong { color: var(--text-primary); font-size: 14px; }

    .result-explain { font-size: 13px; line-height: 1.65; color: var(--text-primary); margin-bottom: 12px; }

    .share {
      display: flex;
      align-items: center;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid var(--border-default);
      flex-wrap: wrap;
    }

    .share-preview {
      flex: 1 1 240px;
      min-width: 0;
      font-size: 11.5px;
      line-height: 1.55;
      color: var(--text-secondary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 8px;
      padding: 8px 10px;
      white-space: pre-line;
      word-break: break-word;
    }

    .share-note { font-size: 11px; color: var(--text-muted); margin-top: 8px; }

    .archive { padding: 18px 20px 20px; }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .panel-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; }

    .panel-title .bar {
      width: 3px;
      height: 14px;
      border-radius: 2px;
      background: var(--accent-primary);
      display: inline-block;
    }

    .panel-meta { font-size: 11.5px; color: var(--text-muted); }

    .chips { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 12px; }

    .chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: -0.02em;
      padding: 5px 11px;
      border-radius: 16px;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .chip:hover { border-color: var(--border-strong); color: var(--text-primary); }

    .chip.active { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }

    .chip em { font-style: normal; font-size: 10.5px; font-variant-numeric: tabular-nums; opacity: 0.62; }

    .arc-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }

    .arc-card {
      display: flex;
      flex-direction: column;
      gap: 6px;
      text-align: left;
      font-family: inherit;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 12px 13px;
      cursor: pointer;
      transition: all 0.15s ease;
      min-width: 0;
    }

    .arc-card:hover { border-color: var(--border-strong); box-shadow: var(--card-shadow-hover); }

    .arc-card.current { border-color: var(--accent-primary); }

    .arc-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }

    .arc-no { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    .arc-title {
      font-size: 13px;
      font-weight: 600;
      line-height: 1.45;
      color: var(--text-primary);
      word-break: keep-all;
    }

    .arc-foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; }

    .arc-bars { font-size: 10.5px; color: var(--text-muted); }

    .arc-state { font-size: 10.5px; color: var(--text-muted); }

    .arc-state.done { color: var(--ok-text); font-weight: 600; }

    .arc-solved { font-size: 10.5px; color: var(--text-muted); }
    .arc-solved.done { color: var(--ok-text); font-weight: 600; }

    .empty { font-size: 12.5px; color: var(--text-muted); padding: 10px 2px; }

    .footer {
      margin-top: 22px;
      padding-top: 16px;
      border-top: 1px solid var(--border-default);
      font-size: 11.5px;
      line-height: 1.7;
      color: var(--text-muted);
    }

    @media (max-width: 640px) {
      .nav-container { padding: 0 12px; height: 54px; gap: 6px; }
      .brand-logo-img { width: 24px; height: 24px; }
      .brand-name { font-size: 15px; }
      .nav-tabs { margin-left: 6px; gap: 4px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; border-radius: 14px; }
      .update-meta { display: none !important; }
      .nav-actions a.icon-btn { display: none; }
      .container { padding: 18px 12px 60px; }
      .hero-title { font-size: 21px; }
      .hero-desc { font-size: 13px; line-height: 1.6; }
      .hero-stats { gap: 6px; }
      .stat-chip { font-size: 11px; padding: 3px 8px; }
      .player { padding: 15px 14px; border-radius: 12px; }
      .player-title { font-size: 16.5px; }
      .chart-card { padding: 10px 8px 8px; }
      .chart-legend { font-size: 10px; gap: 8px; }
      .clue { padding: 11px 12px; }
      .clue-text { font-size: 12.8px; }
      .ask-q { font-size: 14px; }
      .opt { font-size: 12.8px; padding: 10px 11px; }
      .reveal { grid-template-columns: minmax(0, 1fr); }
      .share { flex-direction: column; align-items: stretch; }
      .share-preview { flex: 1 1 auto; }
      .share .btn-primary { width: 100%; }
      .archive { padding: 15px 14px 16px; border-radius: 12px; }
      .arc-grid { grid-template-columns: minmax(0, 1fr); }
      .arc-title { font-size: 12.5px; }
    }

    @media (max-width: 560px) {
      .brand-name { display: none; }
    }

    @media (max-width: 1440px) {
      .nav-container { max-width: 1360px; padding: 0 16px; }
      .nav-tabs { gap: 4px; margin-left: 8px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; }
    }

    @media (max-width: 1024px) {
      .nav-brand { min-width: 0; }
      .nav-tabs { flex: 1 1 auto; min-width: 0; overflow-x: auto; white-space: nowrap; scrollbar-width: none; -ms-overflow-style: none; }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 7px; font-size: 11px; }
    }

    @media (max-width: 430px) {
      .nav-container { padding: 0 8px; height: 52px; gap: 4px; }
      .brand-logo-img { width: 22px; height: 22px; }
      .nav-tabs {
        margin-left: 2px;
        gap: 1px;
        flex: 1 1 auto;
        min-width: 0;
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
      }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 5px; font-size: 10px; border-radius: 11px; letter-spacing: -0.045em; }
      .nav-actions { gap: 4px; }
      .nav-actions .icon-btn { width: 28px; height: 28px; }
    }
"""


# ---------------------------------------------------------------- HTML
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 차트 추리실</title>
  <meta name="description" content="날짜와 종목명을 가린 과거 차트 한 장을 보고, 가려진 다음 구간의 흐름이나 어떤 시장 국면이었는지 맞히는 4지선다 게임. 실제 과거 일별·주별 시세를 쓰고, 정답을 고르면 가려져 있던 기간·종목·출처와 해설이 공개됩니다.">
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

  <!-- Global Nav -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
        <div class="nav-tabs">
          <a href="index.html" class="nav-tab-item">채용공고</a>
          <a href="study.html" class="nav-tab-item">시험 공부</a>
          <a href="ai.html" class="nav-tab-item">AI 트렌드</a>
          <a href="cve.html" class="nav-tab-item">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
          <a href="radar.html" class="nav-tab-item">피싱 레이더</a>
          <a href="pick.html" class="nav-tab-item">오늘 뭐 먹지</a>
          <a href="clue.html" class="nav-tab-item">3단서 추리</a>
          <a href="mission.html" class="nav-tab-item">퇴근길 미션</a>
          <a href="chart.html" class="nav-tab-item active">차트 추리실</a>
        </div>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>매일 00:00 새 차트</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        </button>
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <script>
    // 좁은 화면에서 현재 페이지 탭이 가려지지 않도록 탭 영역만 살짝 스크롤한다.
    (function () {
      function keepActiveTabVisible() {
        var box = document.querySelector('.nav-tabs');
        if (!box) return;
        var act = box.querySelector('.nav-tab-item.active');
        if (!act || box.scrollWidth <= box.clientWidth) return;
        var br = box.getBoundingClientRect();
        var ar = act.getBoundingClientRect();
        if (ar.right > br.right) box.scrollLeft += (ar.right - br.right) + 8;
        else if (ar.left < br.left) box.scrollLeft -= (br.left - ar.left) + 8;
      }
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', keepActiveTabVisible);
      else keepActiveTabVisible();
      window.addEventListener('resize', keepActiveTabVisible);
    })();
  </script>

  <main class="container">

    <section class="hero">
      <span class="hero-pill">CHART MYSTERY</span>
      <h1 class="hero-title">차트 추리실</h1>
      <p class="hero-desc">날짜와 종목명을 가린 과거 차트 한 장을 보고, 가려진 다음 구간의 흐름이나 그 시점의 시장 국면을 맞히는 게임입니다. 가격과 거래량만으로 시작해 필요하면 이동평균·변동성 같은 기술적 단서를 열어 볼 수 있고, 정답을 고르면 실제 기간·종목·출처와 해설이 함께 공개됩니다. 모든 차트는 실제 과거 시세이고 실시간 시세나 투자 조언이 아닙니다.</p>
      <div class="hero-stats">
        <span class="stat-chip">문제 <strong>__TOTAL__</strong></span>
        <span class="stat-chip">오늘 <strong id="statToday">미도전</strong></span>
        <span class="stat-chip">연속 정답 <strong id="statStreak">0</strong></span>
        <span class="stat-chip">해결 <strong id="solvedStat">0 / __TOTAL__</strong></span>
        <span class="stat-chip">정답률 <strong id="rateStat">-</strong></span>
      </div>
    </section>

    <section class="panel player" id="playPanel" aria-label="차트 추리실 플레이어">
      <div class="player-top">
        <div class="player-meta">
          <span class="badge cat-domestic" id="pCat">분야</span>
          <span class="player-date" id="pFreq">일봉</span>
          <span class="today-tag" id="pToday" hidden>오늘의 차트</span>
        </div>
        <div class="dots" id="cDots" aria-label="연 단서 수">
          <i class="dot"></i><i class="dot"></i><i class="dot"></i>
        </div>
      </div>
      <h2 class="player-title" id="pTitle">차트를 불러오는 중입니다</h2>
      <p class="player-sub" id="pSub">날짜와 종목명은 정답을 확인할 때 공개됩니다.</p>

      <div class="chart-card">
        <div class="chart-toolbar">
          <div class="chart-legend" id="legend"></div>
          <button class="btn btn-line btn-sm" id="indicatorBtn" type="button" aria-pressed="false">보조 지표 보기</button>
        </div>
        <div class="chart-wrap">
          <svg id="chartSvg" viewBox="0 0 900 440" role="img" aria-label="가격과 거래량 차트"></svg>
          <div class="tooltip" id="chartTip" hidden></div>
        </div>
        <div class="axis-note" id="axisNote">세로축 가격은 정답 확인 뒤에 표시됩니다</div>
      </div>

      <div class="clues" id="clueList"></div>

      <div class="clue-foot">
        <button class="btn btn-line" id="nextClue" type="button">단서 보기</button>
        <span class="clue-note" id="clueNote">단서를 적게 열고 맞힐수록 기록이 좋아집니다</span>
      </div>

      <div class="ask">
        <div class="ask-head">
          <span class="ask-label">정답 고르기</span>
          <span class="ask-hint" id="triesText"></span>
        </div>
        <p class="ask-q" id="qText"></p>
        <div class="options" id="options"></div>
        <div class="ask-foot">
          <span class="ask-msg" id="askMsg"></span>
          <button class="btn-text" id="giveUp" type="button">정답 보기</button>
        </div>
      </div>

      <div class="result" id="resultBox" hidden>
        <div class="result-head">
          <span class="result-badge" id="resultBadge">정답</span>
          <span class="result-title" id="resultTitle">정답입니다</span>
        </div>
        <div class="reveal">
          <div class="rv"><span class="rv-k">실제 기간</span><span class="rv-v" id="revealPeriod"></span></div>
          <div class="rv"><span class="rv-k">종목·지수</span><span class="rv-v" id="revealName"></span></div>
          <div class="rv"><span class="rv-k">가려진 구간</span><span class="rv-v" id="revealFuture"></span></div>
          <div class="rv"><span class="rv-k">출처</span><span class="rv-v"><a id="revealSource" href="#" target="_blank" rel="noopener noreferrer"></a></span></div>
        </div>
        <p class="result-answer">정답 <strong id="resultAnswer"></strong></p>
        <p class="result-explain" id="resultExplain"></p>
        <div class="share">
          <div class="share-preview" id="sharePreview"></div>
          <button class="btn btn-primary" id="copyBtn" type="button">결과 복사</button>
        </div>
        <p class="share-note">결과 문구에는 정답과 종목명이 들어가지 않습니다. 링크에 이 차트 ID가 들어가, 받은 사람이 같은 차트를 바로 열 수 있습니다.</p>
      </div>
    </section>

    <section class="panel archive" id="archivePanel">
      <div class="panel-head">
        <div class="panel-title"><span class="bar"></span>차트 아카이브</div>
        <span class="panel-meta">분야를 골라 다시 풀 수 있습니다</span>
      </div>
      <div class="chips" id="catFilter">__CAT_CHIPS__</div>
      <div class="arc-grid" id="arcGrid">
__ARC_CARDS__      </div>
      <div class="empty" id="arcEmpty" hidden>이 분야의 차트가 아직 없습니다. 다른 분야를 골라 보세요.</div>
    </section>

    <footer class="footer">
      Infosec Archive · 차트 추리실<br>
      차트는 Yahoo Finance가 공개한 과거 일별·주별 시세(시가·고가·저가·종가·거래량)를 그대로 쓴 것이며, 주가는 액면분할·배당을 반영해 조정된 값입니다. 정답과 해설은 학습·오락용으로, 투자 판단의 근거로 쓰라고 만든 것이 아닙니다. 풀이 기록은 이 브라우저(localStorage)에만 저장되며 서버로 전송되지 않습니다.<br>
      __BUILT_AT__ 기준 · 매일 00:00 새 차트
    </footer>
  </main>

  <script>
    // ---- Theme (다른 페이지와 같은 secjobs-theme 동기화) ----
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');

    function setTheme(theme) {
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'block';
        try { localStorage.setItem('secjobs-theme', 'dark'); } catch (e) {}
      } else {
        document.documentElement.removeAttribute('data-theme');
        if (moonIcon) moonIcon.style.display = 'block';
        if (sunIcon) sunIcon.style.display = 'none';
        try { localStorage.setItem('secjobs-theme', 'light'); } catch (e) {}
      }
    }

    (function initTheme() {
      let saved = null;
      try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) setTheme('dark');
      else setTheme('light');
    })();

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    // ---- 데이터 ----
    const DATA = __DATA_JSON__;
    const CATS = __CATS_JSON__;
    const TODAY_ID = '__TODAY_ID__';
    const STORE_KEY = 'secjobs-chart-v1';
    const SITE = 'https://bling9513-ship-it.github.io/project-1/chart.html';

    const catLabel = {};
    CATS.forEach(c => { catLabel[c.key] = c.label; });
    const byId = {};
    DATA.forEach(p => { byId[p.id] = p; });

    const pCat = document.getElementById('pCat');
    const pFreq = document.getElementById('pFreq');
    const pToday = document.getElementById('pToday');
    const pTitle = document.getElementById('pTitle');
    const pSub = document.getElementById('pSub');
    const cDots = document.getElementById('cDots');
    const clueList = document.getElementById('clueList');
    const nextClue = document.getElementById('nextClue');
    const clueNote = document.getElementById('clueNote');
    const optionsBox = document.getElementById('options');
    const qText = document.getElementById('qText');
    const triesText = document.getElementById('triesText');
    const askMsg = document.getElementById('askMsg');
    const giveUp = document.getElementById('giveUp');
    const resultBox = document.getElementById('resultBox');
    const resultBadge = document.getElementById('resultBadge');
    const resultTitle = document.getElementById('resultTitle');
    const revealPeriod = document.getElementById('revealPeriod');
    const revealName = document.getElementById('revealName');
    const revealFuture = document.getElementById('revealFuture');
    const revealSource = document.getElementById('revealSource');
    const resultAnswer = document.getElementById('resultAnswer');
    const resultExplain = document.getElementById('resultExplain');
    const sharePreview = document.getElementById('sharePreview');
    const copyBtn = document.getElementById('copyBtn');
    const solvedStat = document.getElementById('solvedStat');
    const statStreak = document.getElementById('statStreak');
    const rateStat = document.getElementById('rateStat');
    const statToday = document.getElementById('statToday');
    const chartSvg = document.getElementById('chartSvg');
    const chartTip = document.getElementById('chartTip');
    const axisNote = document.getElementById('axisNote');
    const legend = document.getElementById('legend');
    const indicatorBtn = document.getElementById('indicatorBtn');
    const arcGrid = document.getElementById('arcGrid');
    const arcEmpty = document.getElementById('arcEmpty');
    const catFilter = document.getElementById('catFilter');

    // ---- 상태 ----
    let currentId = null;
    let openClues = 0;
    let answered = false;
    let gaveUp = false;
    let indicator = false;
    let showPrices = false;
    let hoverIndex = -1;

    // ---- 공유 링크 (?id=<차트 ID> · #<차트 ID> 해시도 받아 준다) ----
    function chartUrl(id) {
      return SITE + '?id=' + encodeURIComponent(id);
    }

    function chartIdFromUrl() {
      let q = null;
      try { q = new URLSearchParams(location.search).get('id'); } catch (e) { q = null; }
      if (q && byId[q]) return q;
      let h = String(location.hash || '').replace(/^#/, '');
      if (h) {
        try { h = decodeURIComponent(h); } catch (e) {}
        if (byId[h]) return h;
      }
      return null;
    }

    function syncUrl(id) {
      try {
        const next = '?id=' + encodeURIComponent(id);
        if (location.search !== next || location.hash) history.replaceState(null, '', next);
      } catch (e) {}
    }

    function escapeHtml(s) {
      return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // ---- 기록 ----
    function emptyRecord() {
      const r = {};
      DATA.forEach(p => { r[p.id] = { solved: false, revealed: false, clues: 0, gaveUp: false, pick: -1 }; });
      return r;
    }

    function loadStore() {
      const base = { records: emptyRecord(), streak: 0, lastDate: null };
      let raw = null;
      try { raw = localStorage.getItem(STORE_KEY); } catch (e) {}
      if (!raw) return base;
      let saved = null;
      try { saved = JSON.parse(raw); } catch (e) { return base; }
      if (saved && typeof saved === 'object' && saved.records && typeof saved.records === 'object') {
        Object.keys(base.records).forEach(id => {
          const s = saved.records[id];
          if (!s || typeof s !== 'object') return;
          base.records[id].solved = !!s.solved;
          base.records[id].revealed = !!s.revealed || !!s.solved || !!s.gaveUp;
          base.records[id].clues = Math.min(3, Math.max(0, Number(s.clues) || 0));
          base.records[id].gaveUp = !!s.gaveUp;
          base.records[id].pick = Number.isInteger(Number(s.pick)) && Number(s.pick) >= 0 && Number(s.pick) < 4 ? Number(s.pick) : -1;
        });
        base.streak = Math.max(0, Number(saved.streak) || 0);
        base.lastDate = typeof saved.lastDate === 'string' ? saved.lastDate : null;
      } else {
        Object.keys(base.records).forEach(id => {
          const s = saved ? saved[id] : null;
          if (!s || typeof s !== 'object') return;
          base.records[id].solved = !!s.solved;
          base.records[id].revealed = !!s.revealed || !!s.solved || !!s.gaveUp;
          base.records[id].clues = Math.min(3, Math.max(0, Number(s.clues) || 0));
          base.records[id].gaveUp = !!s.gaveUp;
          base.records[id].pick = Number.isInteger(Number(s.pick)) && Number(s.pick) >= 0 && Number(s.pick) < 4 ? Number(s.pick) : -1;
        });
      }
      return base;
    }

    let store = loadStore();

    function saveStore() {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); } catch (e) {}
    }

    function todayKst() {
      const now = new Date();
      const kst = new Date(now.getTime() + (now.getTimezoneOffset() + 540) * 60000);
      return kst.toISOString().slice(0, 10);
    }

    function solvedCount() {
      return DATA.filter(p => store.records[p.id].solved).length;
    }

    function triedCount() {
      return DATA.filter(p => {
        const r = store.records[p.id];
        return r.revealed || r.solved || r.gaveUp;
      }).length;
    }

    // ---- 표시 도우미 ----
    function pctText(v) {
      return (v >= 0 ? '+' : '') + v.toFixed(1) + '%';
    }

    function priceText(v) {
      if (Math.abs(v) >= 1000) return Math.round(v).toLocaleString('ko-KR');
      if (Math.abs(v) >= 100) return v.toFixed(1);
      return v.toFixed(2);
    }

    // ---- 차트 그리기 (순수 SVG · 외부 라이브러리 없음) ----
    const CHART = { W: 900, H: 440, padL: 16, padR: 62, top: 14, priceH: 268, volTop: 318, volH: 92 };

    function sma(values, n) {
      // 앞부분은 창이 덜 차도 그때까지의 평균으로 그린다(봉이 적은 구간에서도 선이 끊기지 않게).
      const out = new Array(values.length).fill(null);
      const buf = [];
      let sum = 0;
      for (let i = 0; i < values.length; i += 1) {
        buf.push(values[i]);
        sum += values[i];
        if (buf.length > n) sum -= buf.shift();
        out[i] = sum / buf.length;
      }
      return out;
    }

    function plottedCount(ep) {
      return showPrices ? ep.bars.length : ep.split_index + 1;
    }

    function bandValues(ep, shown) {
      let lo = Infinity;
      let hi = -Infinity;
      for (let i = 0; i < shown; i += 1) {
        lo = Math.min(lo, ep.bars[i][3]);
        hi = Math.max(hi, ep.bars[i][2]);
      }
      if (!isFinite(lo) || !isFinite(hi)) { lo = 0; hi = 1; }
      if (hi === lo) { hi += 1; lo -= 1; }
      const pad = (hi - lo) * 0.06;
      return { lo: lo - pad, hi: hi + pad };
    }

    function drawChart() {
      const ep = byId[currentId];
      if (!ep) return;
      const n = ep.bars.length;
      const si = ep.split_index;
      const shown = plottedCount(ep);
      const { W, padL, padR, top, priceH, volTop, volH } = CHART;
      const plotW = W - padL - padR;
      const bw = plotW / n;
      const x = i => padL + bw * (i + 0.5);
      const { lo, hi } = bandValues(ep, shown);
      const y = v => top + priceH * (hi - v) / (hi - lo);

      const hasVolume = ep.bars.some(b => b[5] > 0);
      let vmax = 1;
      for (let i = 0; i < shown; i += 1) {
        vmax = Math.max(vmax, hasVolume ? ep.bars[i][5] : Math.abs(ep.bars[i][4] - ep.bars[i - 1 >= 0 ? i - 1 : 0][4]));
      }

      const parts = [];
      parts.push('<defs><clipPath id="priceClip"><rect x="' + padL + '" y="' + top + '" width="' + plotW + '" height="' + priceH + '"></rect></clipPath></defs>');

      // 가려진 구간: 정답 전에는 빈 자리로 남기고, 정답 뒤에는 실제 봉을 그린다.
      if (si + 1 < n) {
        const fx = padL + bw * (si + 1);
        const fw = plotW - bw * (si + 1);
        parts.push('<rect class="svg-future" x="' + fx.toFixed(1) + '" y="' + top + '" width="' + fw.toFixed(1) + '" height="' + priceH + '"></rect>');
        parts.push('<rect class="svg-future" x="' + fx.toFixed(1) + '" y="' + volTop + '" width="' + fw.toFixed(1) + '" height="' + volH + '"></rect>');
        if (!showPrices) {
          parts.push('<text class="svg-hidden-label" x="' + (fx + fw / 2).toFixed(1) + '" y="' + (top + priceH / 2 - 4).toFixed(1) + '" text-anchor="middle">가려진 구간</text>');
          parts.push('<text class="svg-hidden-sub" x="' + (fx + fw / 2).toFixed(1) + '" y="' + (top + priceH / 2 + 14).toFixed(1) + '" text-anchor="middle">' + (n - si - 1) + '봉 · 정답 확인 시 공개</text>');
        }
      }

      // 가로 눈금선
      for (let k = 0; k <= 3; k += 1) {
        const value = hi - (hi - lo) * k / 3;
        const gy = y(value);
        parts.push('<line class="svg-grid" x1="' + padL + '" y1="' + gy.toFixed(1) + '" x2="' + (W - padR) + '" y2="' + gy.toFixed(1) + '"></line>');
        if (showPrices) {
          parts.push('<text class="svg-axis" x="' + (W - padR + 7) + '" y="' + (gy + 3.5).toFixed(1) + '">' + escapeHtml(priceText(value)) + '</text>');
        }
      }

      // 거래량(또는 등락률) 구분선
      parts.push('<line class="vol-divider" x1="' + padL + '" y1="' + volTop + '" x2="' + (W - padR) + '" y2="' + volTop + '"></line>');

      // 이동평균선 (단서를 열면 표시 · 과거 값만 쓴다)
      if (indicator) {
        const closes = ep.bars.map(b => b[4]);
        const ma20 = sma(closes, 20);
        const ma60 = sma(closes, 60);
        [['ma-20', ma20], ['ma-60', ma60]].forEach(([cls, series]) => {
          let d = '';
          for (let i = 0; i < shown; i += 1) {
            if (series[i] == null) continue;
            d += (d ? ' L' : 'M') + x(i).toFixed(1) + ' ' + y(series[i]).toFixed(1);
          }
          if (d) parts.push('<path class="ma-line ' + cls + ' ma-group" d="' + d + '"></path>');
        });
      }

      // 봉 + 거래량
      for (let i = 0; i < shown; i += 1) {
        const bar = ep.bars[i];
        const o = bar[1], hh = bar[2], ll = bar[3], c = bar[4], v = bar[5];
        const up = c >= o;
        const future = i > si;
        const cls = (up ? 'up' : 'down') + (future ? ' is-future' : '');
        const cxp = x(i).toFixed(1);
        const bodyTop = Math.min(y(o), y(c));
        const bodyH = Math.max(1.1, Math.abs(y(o) - y(c)));
        const bodyW = Math.max(1.4, bw * 0.62);
        parts.push('<line class="wick-' + (up ? 'up' : 'down') + (future ? ' is-future' : '') + '" x1="' + cxp + '" y1="' + y(hh).toFixed(1) + '" x2="' + cxp + '" y2="' + y(ll).toFixed(1) + '"></line>');
        parts.push('<rect class="candle-' + cls + '" x="' + (x(i) - bodyW / 2).toFixed(1) + '" y="' + bodyTop.toFixed(1) + '" width="' + bodyW.toFixed(1) + '" height="' + bodyH.toFixed(1) + '"></rect>');
        const value = hasVolume ? v : Math.abs(c - ep.bars[Math.max(0, i - 1)][4]);
        const vh = Math.max(0.7, volH * value / vmax);
        parts.push('<rect class="candle-' + cls + '" x="' + (x(i) - bodyW / 2).toFixed(1) + '" y="' + (volTop + volH - vh).toFixed(1) + '" width="' + bodyW.toFixed(1) + '" height="' + vh.toFixed(1) + '"></rect>');
      }

      // 가려진 구간 시작 표시
      if (si + 1 < n) {
        const dx = (padL + bw * (si + 1)).toFixed(1);
        parts.push('<line class="svg-divider" x1="' + dx + '" y1="' + top + '" x2="' + dx + '" y2="' + (volTop + volH) + '"></line>');
      }

      // 호버 세로선 + 봉별 히트 영역
      for (let i = 0; i < shown; i += 1) {
        parts.push('<rect class="bar-hit" data-i="' + i + '" x="' + (padL + bw * i).toFixed(1) + '" y="' + top + '" width="' + bw.toFixed(2) + '" height="' + (volTop + volH - top) + '"></rect>');
      }
      parts.push('<line class="hover-line" id="hoverLine" style="display:none" x1="0" y1="' + top + '" x2="0" y2="' + (volTop + volH) + '"></line>');

      chartSvg.innerHTML = parts.join('');
      chartSvg.setAttribute('class', indicator ? 'show-ma' : '');
      const axisKind = hasVolume ? '거래량' : '일간 등락률';
      chartSvg.setAttribute('aria-label', '익명 가격 차트 ' + shown + '봉, 아래 패널은 ' + axisKind);
      axisNote.textContent = (showPrices ? '세로축 가격이 공개되었습니다. ' : '세로축 가격은 정답 확인 뒤에 표시됩니다. ')
        + '아래 패널은 ' + axisKind + (hasVolume ? '이고, 봉 위에 포인터를 올리면 봉별 값이 보입니다.' : '입니다.');

      renderLegend(ep, hasVolume);
      placeHover(hoverIndex);
    }

    function placeHover(i) {
      const line = chartSvg.querySelector('#hoverLine');
      if (!line) return;
      const ep = byId[currentId];
      if (!ep || i < 0 || i >= plottedCount(ep)) { line.style.display = 'none'; return; }
      const bw = (CHART.W - CHART.padL - CHART.padR) / ep.bars.length;
      const px = (CHART.padL + bw * (i + 0.5)).toFixed(1);
      line.setAttribute('x1', px);
      line.setAttribute('x2', px);
      line.style.display = '';
    }

    function renderLegend(ep, hasVolume) {
      const items = ['<span class="item"><span class="swatch up"></span>상승</span>',
        '<span class="item"><span class="swatch down"></span>하락</span>'];
      if (indicator) {
        items.push('<span class="item"><span class="swatch ma20"></span>20봉선</span>');
        items.push('<span class="item"><span class="swatch ma60"></span>60봉선</span>');
      }
      items.push('<span class="item">' + (hasVolume ? '거래량' : '일간 등락률') + '</span>');
      legend.innerHTML = items.join('');
    }

    function showTip(i) {
      const ep = byId[currentId];
      if (!ep) return;
      const bar = ep.bars[i];
      const prev = ep.bars[Math.max(0, i - 1)][4];
      const chg = (bar[4] / prev - 1) * 100;
      const hasVolume = ep.bars.some(b => b[5] > 0);
      if (!hasVolume) {
        chartTip.innerHTML = '<div class="tip-dim">' + (i + 1) + '번째 봉</div><div>등락 ' + pctText(chg) + '</div>';
      } else {
        chartTip.innerHTML = '<div class="tip-dim">' + (i + 1) + '번째 봉</div><div>등락 ' + pctText(chg) + '</div>'
          + (showPrices
            ? '<div class="tip-dim">' + escapeHtml(bar[0]) + ' · 종가 ' + priceText(bar[4]) + '</div><div class="tip-dim">거래량 ' + Math.round(bar[5]).toLocaleString('ko-KR') + '</div>'
            : '<div class="tip-dim">종가·날짜는 공개 전입니다</div>');
      }
      chartTip.hidden = false;
      const rect = chartSvg.getBoundingClientRect();
      const bw = (CHART.W - CHART.padL - CHART.padR) / ep.bars.length;
      const px = (CHART.padL + bw * (i + 0.5)) / CHART.W * rect.width;
      chartTip.style.left = Math.max(40, Math.min(rect.width - 40, px)) + 'px';
      chartTip.style.top = Math.max(30, rect.height * (CHART.top + 40) / CHART.H) + 'px';
    }

    function hideTip() {
      chartTip.hidden = true;
    }

    // ---- 화면 렌더 ----
    function recordFor(id) {
      return store.records[id] || { solved: false, revealed: false, clues: 0, gaveUp: false, pick: -1 };
    }

    function refreshStats() {
      const solved = solvedCount();
      const tried = triedCount();
      solvedStat.textContent = solved + ' / ' + DATA.length;
      statStreak.textContent = String(store.streak || 0);
      rateStat.textContent = tried ? Math.round(solved / tried * 100) + '%' : '-';
      const today = byId[TODAY_ID];
      statToday.textContent = today && store.records[TODAY_ID].solved ? '해결' : '미도전';
      DATA.forEach(p => {
        const card = arcGrid.querySelector('.arc-card[data-id="' + p.id + '"]');
        if (!card) return;
        const r = store.records[p.id];
        const state = card.querySelector('[data-state]');
        const solvedMark = card.querySelector('[data-solved]');
        if (r.solved) {
          state.textContent = '해결';
          state.className = 'arc-state done';
          solvedMark.textContent = r.clues ? '단서 ' + r.clues + '개로 해결' : '해결';
          solvedMark.className = 'arc-solved done';
        } else if (r.gaveUp) {
          state.textContent = '정답 확인';
          state.className = 'arc-state';
          solvedMark.textContent = '';
          solvedMark.className = 'arc-solved';
        } else if (r.revealed) {
          state.textContent = '오답';
          state.className = 'arc-state';
          solvedMark.textContent = '정답 확인함';
          solvedMark.className = 'arc-solved';
        } else {
          state.textContent = '미도전';
          state.className = 'arc-state';
          solvedMark.textContent = '';
          solvedMark.className = 'arc-solved';
        }
        card.classList.toggle('current', p.id === currentId);
      });
    }

    function renderClues(ep) {
      clueList.innerHTML = ep.clues.map((clue, i) => {
        const open = i < openClues;
        return '<div class="clue ' + (open ? 'open' : 'locked') + '">'
          + '<div class="clue-head"><span class="clue-label">' + (open ? escapeHtml(clue.label) : '단서 ' + (i + 1)) + '</span>'
          + '<span class="clue-step">' + (open ? (i + 1) + ' / 3' : '닫힘') + '</span></div>'
          + '<div class="clue-text">' + (open ? escapeHtml(clue.text) : '단서를 열면 표시됩니다.') + '</div>'
          + '</div>';
      }).join('');
      cDots.querySelectorAll('.dot').forEach((dot, i) => {
        dot.classList.toggle('on', i < openClues);
      });
      nextClue.textContent = openClues >= ep.clues.length ? '단서 모두 열림' : '단서 ' + (openClues + 1) + '/' + ep.clues.length + ' 보기';
      nextClue.disabled = openClues >= ep.clues.length;
      clueNote.textContent = openClues >= 3 ? '단서를 모두 열었습니다. 정답을 골라 보세요.' : '단서를 적게 열고 맞힐수록 기록이 좋아집니다';
    }

    function renderOptions(ep, r) {
      const quiz = ep.quiz;
      const locked = answered || gaveUp;
      optionsBox.innerHTML = quiz.choices.map((choice, i) => {
        let cls = 'opt';
        if (locked) {
          if (i === quiz.answer) cls += ' is-correct';
          else if (r.pick === i) cls += ' is-wrong';
        }
        return '<button class="' + cls + '" type="button" data-idx="' + i + '"' + (locked ? ' disabled' : '') + '>'
          + '<span class="key">' + 'ABCD'[i] + '</span><span class="body">' + escapeHtml(choice) + '</span></button>';
      }).join('');
      qText.textContent = quiz.prompt;
      triesText.textContent = locked ? '정답을 확인했습니다' : (openClues ? '단서 ' + openClues + '개를 열었습니다' : '차트만 보고 골라 보세요');
    }

    function renderResult(ep, correct) {
      const quiz = ep.quiz;
      resultBox.hidden = false;
      resultBox.classList.toggle('gave-up', gaveUp);
      giveUp.hidden = true;
      resultBadge.textContent = gaveUp ? '정답 공개' : (correct ? '정답' : '아쉬움');
      if (gaveUp) resultTitle.textContent = '정답을 공개합니다';
      else if (correct) resultTitle.textContent = '정답입니다';
      else resultTitle.textContent = '다른 선택지가 정답이었습니다';
      revealPeriod.textContent = ep.period + ' (' + (ep.interval === '1wk' ? '주봉' : '일봉') + ')';
      revealName.textContent = ep.name;
      revealFuture.textContent = ep.bars[ep.split_index + 1][0] + ' ~ ' + ep.bars[ep.bars.length - 1][0]
        + ' · ' + (ep.bars.length - ep.split_index - 1) + '봉 · ' + pctText(ep.future_return);
      revealSource.textContent = ep.source;
      revealSource.href = ep.source_url;
      resultAnswer.textContent = quiz.choices[quiz.answer];
      resultExplain.textContent = ep.explanation;
      askMsg.textContent = gaveUp ? '정답을 봤으니 기록에는 해결로 남지 않습니다.' : (correct ? '' : '가려진 구간을 함께 열었습니다.');
      askMsg.className = 'ask-msg' + (correct || gaveUp ? '' : ' no');
      sharePreview.textContent = shareText(ep);
      refreshStats();
    }

    function shareText(ep) {
      const r = recordFor(ep.id);
      const solved = solvedCount();
      const rate = triedCount() ? Math.round(solved / triedCount() * 100) : 0;
      const line1 = '차트 추리실 #' + ep.ordinal + ' · ' + catLabel[ep.category];
      const line2 = '이름을 가린 과거 차트 한 장, 가려진 다음 구간을 맞혀 보세요.';
      const mine = r.solved ? '내 기록 ' + solved + '/' + DATA.length + ' · 정답률 ' + rate + '%' : '나는 ' + (r.gaveUp ? '정답을 확인했습니다' : '도전 중입니다');
      return line1 + '\\n' + line2 + '\\n' + mine + '\\n' + chartUrl(ep.id);
    }

    function resetStateFor(ep) {
      const r = recordFor(ep.id);
      openClues = Math.min(3, Math.max(0, r.clues || 0));
      answered = !!r.revealed || !!r.solved || !!r.gaveUp;
      gaveUp = !!r.gaveUp && !r.solved;
      showPrices = answered || gaveUp;
      indicator = openClues > 0;
      hoverIndex = -1;
    }

    function load(id, opts) {
      currentId = id;
      const ep = byId[id];
      resetStateFor(ep);
      pCat.textContent = catLabel[ep.category];
      pCat.className = 'badge cat-' + ep.category;
      pFreq.textContent = (ep.interval === '1wk' ? '주봉' : '일봉') + ' · ' + ep.bars.length + '봉';
      pToday.hidden = id !== TODAY_ID;
      pTitle.textContent = '블라인드 차트 #' + ep.ordinal;
      pSub.textContent = answered || gaveUp ? '정답 확인 완료 · 가려졌던 구간까지 표시됩니다' : '날짜와 종목명은 정답을 확인할 때 공개됩니다';
      resultBox.hidden = !(answered || gaveUp);
      drawChart();
      renderClues(ep);
      const rec = recordFor(id);
      renderOptions(ep, rec);
      if (answered || gaveUp) renderResult(ep, !!rec.solved);
      else {
        askMsg.textContent = '';
        askMsg.className = 'ask-msg';
      }
      giveUp.hidden = answered || gaveUp;
      indicatorBtn.textContent = indicator ? '보조 지표 숨기기' : '보조 지표 보기';
      indicatorBtn.setAttribute('aria-pressed', indicator ? 'true' : 'false');
      refreshStats();
      if (opts && opts.scroll) {
        const panel = document.getElementById('playPanel');
        if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    // ---- 상호작용 ----
    nextClue.addEventListener('click', () => {
      const ep = byId[currentId];
      if (openClues >= ep.clues.length) return;
      openClues += 1;
      if (!indicator) indicator = true;
      const r = recordFor(ep.id);
      r.clues = Math.max(r.clues, openClues);
      saveStore();
      renderClues(ep);
      drawChart();
      indicatorBtn.textContent = indicator ? '보조 지표 숨기기' : '보조 지표 보기';
      indicatorBtn.setAttribute('aria-pressed', indicator ? 'true' : 'false');
      triesText.textContent = '단서 ' + openClues + '개를 열었습니다';
      refreshStats();
    });

    indicatorBtn.addEventListener('click', () => {
      indicator = !indicator;
      indicatorBtn.textContent = indicator ? '보조 지표 숨기기' : '보조 지표 보기';
      indicatorBtn.setAttribute('aria-pressed', indicator ? 'true' : 'false');
      drawChart();
    });

    optionsBox.addEventListener('click', (event) => {
      const btn = event.target.closest('.opt');
      if (!btn || answered || gaveUp) return;
      const ep = byId[currentId];
      const pick = Number(btn.dataset.idx);
      const correct = pick === ep.quiz.answer;
      const r = recordFor(ep.id);
      answered = true;
      r.revealed = true;
      r.pick = pick;
      r.clues = Math.max(r.clues || 0, openClues);
      if (correct) {
        r.solved = true;
        store.streak = (store.streak || 0) + 1;
        store.lastDate = todayKst();
      } else {
        store.streak = 0;
      }
      saveStore();
      showPrices = true;
      drawChart();
      renderOptions(ep, r);
      renderResult(ep, correct);
      pSub.textContent = '정답 확인 완료 · 가려졌던 구간까지 표시됩니다';
    });

    giveUp.addEventListener('click', () => {
      const ep = byId[currentId];
      if (answered || gaveUp) return;
      gaveUp = true;
      answered = true;
      const r = recordFor(ep.id);
      r.gaveUp = true;
      r.revealed = true;
      r.clues = Math.max(r.clues || 0, openClues);
      saveStore();
      showPrices = true;
      drawChart();
      renderOptions(ep, r);
      renderResult(ep, false);
      pSub.textContent = '정답 확인 완료 · 가려졌던 구간까지 표시됩니다';
    });

    function copyText(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          copyBtn.textContent = '복사됨';
          setTimeout(() => { copyBtn.textContent = '결과 복사'; }, 1600);
        }).catch(() => fallbackCopy(text));
      } else {
        fallbackCopy(text);
      }
    }

    function fallbackCopy(text) {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(area);
      copyBtn.textContent = '복사됨';
      setTimeout(() => { copyBtn.textContent = '결과 복사'; }, 1600);
    }

    copyBtn.addEventListener('click', () => copyText(sharePreview.textContent));

    // 차트 호버/터치 → 봉별 값
    function indexFromEvent(event) {
      const ep = byId[currentId];
      if (!ep) return -1;
      const rect = chartSvg.getBoundingClientRect();
      const relX = (event.clientX - rect.left) / rect.width * CHART.W;
      const plotW = CHART.W - CHART.padL - CHART.padR;
      const frac = (relX - CHART.padL) / plotW;
      const idx = Math.floor(frac * ep.bars.length);
      const shown = plottedCount(ep);
      if (idx < 0 || idx >= shown) return -1;
      return idx;
    }

    function handlePointer(event) {
      const idx = indexFromEvent(event);
      if (idx < 0) {
        hoverIndex = -1;
        hideTip();
        placeHover(-1);
        return;
      }
      hoverIndex = idx;
      placeHover(idx);
      showTip(idx);
    }

    chartSvg.addEventListener('pointermove', handlePointer);
    chartSvg.addEventListener('pointerdown', handlePointer);

    chartSvg.addEventListener('pointerleave', () => {
      hoverIndex = -1;
      hideTip();
      placeHover(-1);
    });

    // 분야 필터
    catFilter.addEventListener('click', (event) => {
      const chip = event.target.closest('.chip');
      if (!chip) return;
      catFilter.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c === chip));
      const key = chip.dataset.cat;
      let visible = 0;
      arcGrid.querySelectorAll('.arc-card').forEach(card => {
        const show = key === 'all' || card.dataset.cat === key;
        card.hidden = !show;
        if (show) visible += 1;
      });
      arcEmpty.hidden = visible !== 0;
    });

    arcGrid.addEventListener('click', (event) => {
      const card = event.target.closest('.arc-card');
      if (!card) return;
      const id = card.dataset.id;
      if (!id || !byId[id]) return;
      syncUrl(id);
      load(id, { scroll: true });
    });

    // ---- 시작 ----
    (function start() {
      const linked = chartIdFromUrl();
      load(linked || TODAY_ID);
      if (linked) syncUrl(linked);
    })();
  </script>
</body>
</html>
"""


def build():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    built_at = now.strftime("%Y-%m-%d %H:%M KST")
    data = load_data()
    episodes = data["episodes"]
    if len(episodes) < 14:
        raise SystemExit("[중단] 차트가 14개 미만입니다: %d" % len(episodes))
    for ep in episodes:
        if not ep["source_url"].startswith("https://"):
            raise SystemExit("[중단] %s: 출처 링크가 https 가 아닙니다" % ep["id"])

    # 오늘의 차트: 날짜로 정해지는 순환(매일 00:00 KST에 다음 문제)
    epoch = datetime(2026, 1, 1, tzinfo=kst).date()
    today_index = (now.date() - epoch).days % len(episodes)
    today_id = episodes[today_index]["id"]

    data_json = safe_json_for_script(json.dumps(episodes, ensure_ascii=False, separators=(",", ":")))
    cats_json = safe_json_for_script(json.dumps(CATEGORIES, ensure_ascii=False, separators=(",", ":")))

    cards = "".join(render_arc_card(ep) for ep in episodes)

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__TOTAL__", str(len(episodes)))
    html = html.replace("__CAT_CHIPS__", render_cat_chips(episodes))
    html = html.replace("__ARC_CARDS__", cards)
    html = html.replace("__DATA_JSON__", data_json)
    html = html.replace("__CATS_JSON__", cats_json)
    html = html.replace("__TODAY_ID__", today_id)
    html = html.replace("__BUILT_AT__", esc(built_at))

    with open(CHART_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(html))

    print("-> 'chart.html' 생성 완료 (차트 %d개 · 오늘의 차트 %s · 오늘 #%d)"
          % (len(episodes), today_id, today_index + 1))
    for ep in episodes:
        print("   · #%02d %-9s %-12s %2d봉 %-4s 정답 %d/%d · 가려진 %2d봉 %+6.1f%%"
              % (ep["ordinal"], next(c["label"] for c in CATEGORIES if c["key"] == ep["category"]),
                 ep["name"], len(ep["bars"]), "주봉" if ep["interval"] == "1wk" else "일봉",
                 ep["quiz"]["answer"] + 1, len(ep["quiz"]["choices"]),
                 len(ep["bars"]) - ep["split_index"] - 1, ep["future_return"]))
    return len(episodes)


if __name__ == "__main__":
    build()

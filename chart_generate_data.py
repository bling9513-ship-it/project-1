# -*- coding: utf-8 -*-
"""차트 추리실(chart.html) 합성 OHLCV 생성기.

외부 시세(Yahoo Finance 등)를 쓰지 않는다. 16문항 모두 이 스크립트가 만든
'학습용 합성 시계열'이며 실제 종목·지수·시세가 아니다.

원칙
- 문항마다 정해 둔 차트 시나리오(추세·돌파·지지/저항·거래량)에 맞춰 시가·고가·저가·종가·거래량을 만든다.
- 난수는 문항 id 를 seed 로 쓰는 random.Random 이라 같은 코드면 언제나 같은 값이 나온다(재현 가능).
- 가려진 구간의 흐름(정답)은 사람이 적지 않고 만들어진 종가로 계산한다.
- 해설의 수치도 전부 만들어진 봉에서 계산해 넣는다(해설과 차트가 어긋나지 않는다).
- 날짜는 x축·호버용 합성 달력이다(주말 제외, 실제 거래일과 무관).

실행: python3 chart_generate_data.py
"""
import json
import math
import os
import random
import sys
from datetime import date, datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "chart_data.json")

CATEGORIES = [
    {"key": "trend", "label": "추세"},
    {"key": "breakout", "label": "돌파"},
    {"key": "level", "label": "지지·저항"},
    {"key": "volume", "label": "거래량"},
]

FLOW_BANDS = [
    ("surge", "10% 넘게 상승", lambda r: r >= 0.10),
    ("up", "2~10% 상승", lambda r: 0.02 <= r < 0.10),
    ("flat", "보합권(±2% 이내)", lambda r: -0.02 < r < 0.02),
    ("down", "2~10% 하락", lambda r: -0.10 < r <= -0.02),
    ("plunge", "10% 넘게 하락", lambda r: r <= -0.10),
]

NOTICE = "합성 학습 데이터 · 실제 시세 아님"

PATTERN_POOL = [
    "고점과 저점을 함께 높이는 상승 추세",
    "고점과 저점을 함께 낮추는 하락 추세",
    "박스권 상단을 거래량과 함께 돌파",
    "전고점을 넘었다가 되돌아온 가짜 돌파",
    "같은 가격대에서 두 번 반등한 지지선",
    "저항선에 막혀 되돌림",
    "거래량이 줄며 좁아지는 횡보",
    "거래량 폭증 뒤 급락(클라이맥스)",
    "거래량이 실리지 않은 완만한 반등",
    "이중바닥을 만든 뒤의 반등",
]

# 각 문항: legs = [(봉 수, 구간 등락률 %, 봉당 변동성, 거래량 배수), ...]
#   앞쪽 legs 가 보이는 구간, hidden_legs 가 가려진 구간이다.
SCENARIOS = [
    # ------------------------------------------------------------------ 추세
    {
        "id": "syn-trend-01", "category": "trend", "name": "순조로운 상승 추세",
        "interval": "1d", "anchor": "2019-04-01", "start_price": 12400.0, "base_volume": 860000,
        "legs": [(14, 3.6, 0.008, 1.00), (8, -2.2, 0.009, 0.90), (18, 7.4, 0.008, 1.05),
                 (7, -1.8, 0.009, 0.85), (7, 2.0, 0.008, 1.10)],
        "hidden_legs": [(20, 6.4, 0.009, 1.10)],
        "quiz": "next", "expect_band": "up",
        "lesson": "20봉선이 60봉선 위에서 함께 올라가고, 눌림 목의 저점이 앞 저점보다 높게 유지되는 동안은 추세를 따라가는 쪽이 유리합니다. 다만 단기선에서 멀리 벌어지면 되돌림이 나올 수 있어, 눌림 폭을 함께 봐야 합니다.",
    },
    {
        "id": "syn-trend-02", "category": "trend", "name": "상승 추세 지속 확인",
        "interval": "1d", "anchor": "2021-02-15", "start_price": 25800.0, "base_volume": 410000,
        "legs": [(12, 2.6, 0.008, 1.00), (6, -1.6, 0.008, 0.85), (14, 4.2, 0.008, 1.05),
                 (6, -1.3, 0.008, 0.90), (12, 3.0, 0.008, 1.10)],
        "hidden_legs": [(16, 4.2, 0.008, 1.05)],
        "quiz": "pattern", "pattern": PATTERN_POOL[0],
        "lesson": "고점과 저점이 함께 높아지는 구간에서는 고점 하나가 아니라 저점의 위치를 확인해야 합니다. 저점이 계속 올라오면 매수세가 가격을 받쳐 주고 있다는 뜻입니다.",
    },
    {
        "id": "syn-trend-03", "category": "trend", "name": "하락 추세 속 기술적 반등",
        "interval": "1d", "anchor": "2022-05-09", "start_price": 47800.0, "base_volume": 690000,
        "legs": [(16, -6.0, 0.011, 1.10), (10, -3.0, 0.010, 0.95), (14, -5.0, 0.012, 1.15),
                 (8, -1.0, 0.010, 0.90), (6, 1.6, 0.010, 1.00)],
        "hidden_legs": [(18, 12.8, 0.013, 1.35)],
        "quiz": "next", "expect_band": "surge",
        "lesson": "낙폭이 컸던 자산은 매도세가 한 번 쉬는 구간에서 짧고 강한 반등이 나오기 쉽습니다. 다만 20봉선이 60봉선 아래에 있어 추세 자체가 바뀌었다고 보기는 어렵습니다.",
    },
    {
        "id": "syn-trend-04", "category": "trend", "name": "추세 가속 뒤 과열",
        "interval": "1d", "anchor": "2020-06-01", "start_price": 8130.0, "base_volume": 1250000,
        "legs": [(18, 3.0, 0.008, 1.00), (12, 6.2, 0.009, 1.15), (14, 9.4, 0.012, 1.45),
                 (12, 5.2, 0.014, 1.60)],
        "hidden_legs": [(17, -8.5, 0.014, 1.30)],
        "quiz": "next", "expect_band": "down",
        "lesson": "상승 기울기가 갑자기 가팔라지고 거래량까지 늘면 막바지 국면일 수 있습니다. 20봉선에서 크게 벌어진 상태에서의 첫 하락은 되돌림이 아니라 추세 전환의 시작인 경우도 많습니다.",
    },
    # ------------------------------------------------------------------ 돌파
    {
        "id": "syn-break-01", "category": "breakout", "name": "박스권 상단 돌파",
        "interval": "1d", "anchor": "2023-02-06", "start_price": 10150.0, "base_volume": 540000,
        "legs": [(16, 1.0, 0.006, 0.95), (14, -1.0, 0.006, 0.85), (12, 1.2, 0.006, 0.90),
                 (7, -0.8, 0.005, 0.80), (5, 6.4, 0.010, 1.95)],
        "hidden_legs": [(16, 9.1, 0.011, 1.30)],
        "quiz": "pattern", "pattern": PATTERN_POOL[2],
        "lesson": "박스권에서는 위아래 경계가 저항과 지지 역할을 합니다. 상단을 종가로 넘어서면서 거래량이 늘면, 넘어선 가격대가 다시 지지로 바뀌는지가 다음 관전 포인트입니다.",
    },
    {
        "id": "syn-break-02", "category": "breakout", "name": "전고점 돌파 실패",
        "interval": "1d", "anchor": "2018-03-05", "start_price": 33200.0, "base_volume": 330000,
        "legs": [(16, 5.0, 0.009, 1.00), (8, -2.0, 0.009, 0.90), (14, 4.0, 0.009, 1.00),
                 (11, 11.0, 0.010, 1.45), (9, -7.4, 0.012, 1.20)],
        "hidden_legs": [(20, -14.5, 0.015, 1.50)],
        "quiz": "pattern", "pattern": PATTERN_POOL[3],
        "lesson": "전고점을 넘을 때 거래량이 따라오지 않거나, 넘은 뒤 며칠 안에 다시 아래로 돌아오면 돌파를 믿기 어렵습니다. 되돌아온 자리에서 지지가 확인되지 않으면 직전 매수세가 물린 상태로 남습니다.",
    },
    {
        "id": "syn-break-03", "category": "breakout", "name": "하락 채널 상단 돌파",
        "interval": "1d", "anchor": "2019-09-16", "start_price": 6740.0, "base_volume": 2100000,
        "legs": [(20, -8.0, 0.011, 1.05), (12, 4.2, 0.011, 1.00), (10, -3.0, 0.010, 0.90),
                 (13, 6.6, 0.012, 1.25)],
        "hidden_legs": [(20, 5.8, 0.011, 1.10)],
        "quiz": "next", "expect_band": "up",
        "lesson": "하락 채널의 윗선을 넘으면 그동안의 매도 압력이 약해졌다는 신호로 봅니다. 다만 60봉선이 아직 내려오고 있다면 반등의 폭을 크게 기대하기는 이릅니다.",
    },
    {
        "id": "syn-break-04", "category": "breakout", "name": "신고가 돌파 후 횡보",
        "interval": "1wk", "anchor": "2024-01-01", "start_price": 158000.0, "base_volume": 96000,
        "legs": [(14, 6.0, 0.020, 1.00), (6, -3.0, 0.018, 0.90), (12, 7.2, 0.020, 1.10),
                 (8, 1.0, 0.016, 0.85)],
        "hidden_legs": [(12, -0.6, 0.015, 0.80)],
        "quiz": "next", "expect_band": "flat",
        "lesson": "신고가를 갱신한 뒤 거래량이 줄며 좁게 움직이면, 오른 것을 소화하는 구간으로 볼 수 있습니다. 이때는 방향을 서두르기보다 다음 거래량 증가가 어느 쪽으로 나오는지를 봅니다.",
    },
    # -------------------------------------------------------------- 지지·저항
    {
        "id": "syn-level-01", "category": "level", "name": "지지선 두 번 반등",
        "interval": "1d", "anchor": "2021-08-02", "start_price": 18400.0, "base_volume": 720000,
        "legs": [(14, -8.2, 0.010, 1.10), (10, 6.2, 0.010, 1.05), (10, -5.6, 0.010, 1.00),
                 (8, 5.0, 0.010, 1.05), (9, 1.6, 0.009, 0.95)],
        "hidden_legs": [(16, 7.7, 0.011, 1.15)],
        "quiz": "pattern", "pattern": PATTERN_POOL[4],
        "lesson": "같은 가격대에서 두 번 반등했다면 그 아래에서 기다리던 매수세가 있다는 뜻입니다. 두 번째 반등 뒤 고점을 넘어서는지가 지지선의 힘을 확인하는 기준이 됩니다.",
    },
    {
        "id": "syn-level-02", "category": "level", "name": "저항선에 막혀 되돌림",
        "interval": "1d", "anchor": "2022-01-10", "start_price": 14200.0, "base_volume": 480000,
        "legs": [(16, 8.2, 0.009, 1.05), (9, -4.2, 0.009, 0.90), (14, 7.6, 0.009, 1.00),
                 (6, -4.6, 0.010, 1.05), (10, -2.0, 0.009, 0.90)],
        "hidden_legs": [(18, -6.2, 0.010, 1.10)],
        "quiz": "pattern", "pattern": PATTERN_POOL[5],
        "lesson": "같은 가격대에서 두 번 막혔다면 그 위에 매도 물량이 남아 있다고 봅니다. 두 번째 시도에서도 종가가 저항 아래로 밀리면 조정이 길어질 수 있습니다.",
    },
    {
        "id": "syn-level-03", "category": "level", "name": "지지선 이탈",
        "interval": "1d", "anchor": "2023-06-05", "start_price": 9650.0, "base_volume": 880000,
        "legs": [(12, 2.6, 0.009, 1.00), (10, -6.2, 0.010, 1.10), (10, 5.0, 0.010, 1.00),
                 (10, -5.6, 0.010, 1.05), (8, -0.6, 0.010, 1.15)],
        "hidden_legs": [(17, -11.9, 0.014, 1.50)],
        "quiz": "next", "expect_band": "plunge",
        "lesson": "지지선은 닿는 횟수가 많아질수록 약해집니다. 다시 올라오지 못하고 종가가 지지선 아래에 머물면, 그 가격대는 지지가 아니라 저항으로 바뀌게 됩니다.",
    },
    {
        "id": "syn-level-04", "category": "level", "name": "이중바닥 뒤 반등",
        "interval": "1d", "anchor": "2019-11-04", "start_price": 22600.0, "base_volume": 505000,
        "legs": [(18, -9.0, 0.011, 1.10), (10, 4.2, 0.010, 0.95), (12, -8.2, 0.011, 1.05),
                 (10, 5.4, 0.010, 1.10), (6, 2.2, 0.009, 1.05)],
        "hidden_legs": [(20, 13.6, 0.012, 1.30)],
        "quiz": "next", "expect_band": "surge",
        "lesson": "비슷한 가격대에서 두 번 바닥을 만들고 두 번째 바닥의 거래량이 줄었다면 매도 압력이 약해진 것으로 봅니다. 목선(중간 고점)을 넘어서면 이중바닥이 확인됩니다.",
    },
    # ----------------------------------------------------------------- 거래량
    {
        "id": "syn-vol-01", "category": "volume", "name": "거래량 폭증 뒤 급락",
        "interval": "1d", "anchor": "2021-11-15", "start_price": 7340.0, "base_volume": 1420000,
        "legs": [(18, 2.0, 0.008, 1.00), (14, 4.0, 0.008, 1.05), (10, 5.0, 0.009, 1.20),
                 (8, 7.4, 0.012, 2.20)],
        "hidden_legs": [(17, -9.8, 0.014, 1.40)],
        "quiz": "pattern", "pattern": PATTERN_POOL[7],
        "shocks": {49: {"ret": -0.035, "wick": 0.05, "vol": 3.0}},
        "lesson": "가격이 수직으로 오르는데 거래량이 폭발하면, 그 거래가 대부분 추격 매수일 수 있습니다. 긴 윗꼬리를 달고 종가가 밀리는 봉이 나오면 그 자리가 단기 정점이 된 사례가 많습니다.",
    },
    {
        "id": "syn-vol-02", "category": "volume", "name": "거래량 감소 속 횡보",
        "interval": "1wk", "anchor": "2020-02-03", "start_price": 42700.0, "base_volume": 260000,
        "legs": [(14, 1.2, 0.014, 1.00), (10, -1.2, 0.012, 0.80), (10, 0.6, 0.010, 0.60)],
        "hidden_legs": [(11, 0.9, 0.009, 0.55)],
        "quiz": "next", "expect_band": "flat",
        "lesson": "거래량이 줄며 폭이 좁아지는 구간은 매수·매도 모두 지친 상태입니다. 이때는 방향을 미리 정하기보다 거래량이 다시 늘어나는 쪽으로 움직임이 나오는 것을 기다립니다.",
    },
    {
        "id": "syn-vol-03", "category": "volume", "name": "거래량 동반 하락 추세",
        "interval": "1d", "anchor": "2022-09-05", "start_price": 31800.0, "base_volume": 640000,
        "legs": [(14, -2.2, 0.009, 1.00), (8, -1.6, 0.009, 1.05), (16, -4.2, 0.009, 1.25),
                 (14, -2.6, 0.010, 1.35)],
        "hidden_legs": [(17, -4.7, 0.010, 1.30)],
        "quiz": "next", "expect_band": "down",
        "lesson": "하락하는데 거래량이 늘어난다면 매도세가 적극적이라는 뜻입니다. 반등할 때 거래량이 줄고 하락할 때 늘어나는 흐름이 이어지면 추세는 아직 꺾이지 않은 것으로 봅니다.",
    },
    {
        "id": "syn-vol-04", "category": "volume", "name": "거래량 급증 돌파",
        "interval": "1d", "anchor": "2024-05-06", "start_price": 5320.0, "base_volume": 3150000,
        "legs": [(14, 1.2, 0.008, 0.80), (12, -1.6, 0.008, 0.75), (12, 2.0, 0.009, 0.90),
                 (16, 2.6, 0.010, 1.65)],
        "hidden_legs": [(17, 8.4, 0.011, 1.35)],
        "quiz": "next", "expect_band": "up",
        "lesson": "가격이 잘 움직이지 않던 구간을 지나 거래량이 배로 늘며 고점을 넘으면, 그동안 쌓인 매물을 소화한 것으로 볼 수 있습니다. 이후 눌림에서 거래량이 줄면 돌파가 유지될 가능성이 커집니다.",
    },
]


# ------------------------------------------------------------------ 시계열 생성
def _trading_days(anchor, count, interval):
    day = date.fromisoformat(anchor)
    out = []
    if interval == "1wk":
        while len(out) < count:
            out.append(day.isoformat())
            day += timedelta(days=7)
        return out
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day.isoformat())
        day += timedelta(days=1)
    return out


def _leg_multipliers(n, drift_pct, sigma, rng):
    """구간 n봉의 종가 배수 목록. 구간 끝값은 정확히 (1+drift) 배가 되게 보정한다."""
    if n <= 0:
        return []
    target = math.log1p(drift_pct / 100.0)
    mu = target / n
    acc = 0.0
    logs = []
    for _ in range(n):
        acc += mu + rng.gauss(0.0, sigma)
        logs.append(acc)
    correction = target - logs[-1]
    for i in range(n):
        logs[i] += correction * ((i + 1) / n)
    return [math.exp(value) for value in logs]


def build_bars(spec):
    rng = random.Random(spec["id"])
    dates = _trading_days(spec["anchor"], sum(leg[0] for leg in spec["legs"]) +
                          sum(leg[0] for leg in spec["hidden_legs"]), spec["interval"])
    closes, sigmas, vol_mults = [], [], []
    for leg in spec["legs"] + spec["hidden_legs"]:
        n, drift, sigma, vmult = leg
        base = closes[-1] if closes else spec["start_price"]
        for mult in _leg_multipliers(n, drift, sigma, rng):
            closes.append(base * mult)
            sigmas.append(sigma)
            vol_mults.append(vmult)
    for index, shock in (spec.get("shocks") or {}).items():
        closes[index] = closes[index - 1] * (1 + shock["ret"])

    bars = []
    prev_close = None
    for i, close in enumerate(closes):
        sigma = sigmas[i]
        open_price = close * (1 - rng.gauss(0.0, sigma * 0.25)) if prev_close is None else \
            prev_close * (1 + rng.gauss(0.0, sigma * 0.35))
        high = max(open_price, close) * (1 + abs(rng.gauss(0.0, sigma * 0.55)))
        low = min(open_price, close) * (1 - abs(rng.gauss(0.0, sigma * 0.55)))
        shock = (spec.get("shocks") or {}).get(i)
        if shock:
            if shock.get("wick"):
                high = max(high, max(open_price, close) * (1 + shock["wick"]))
            vol = spec["base_volume"] * vol_mults[i] * shock.get("vol", 1.0) * math.exp(rng.gauss(0.0, 0.16))
        else:
            vol = spec["base_volume"] * vol_mults[i] * math.exp(rng.gauss(0.0, 0.16))
        o, c = round(open_price, 2), round(close, 2)
        h, l = round(high, 2), round(low, 2)
        bars.append([dates[i], o, max(h, o, c), min(l, o, c), c, int(max(1000, vol))])
        prev_close = close
    return bars


# ------------------------------------------------------------------ 지표·패턴
def _sma(values, n):
    window = values[-n:]
    return sum(window) / len(window)


def _pivot_lows(lows, half=4):
    """±half 봉 안에서 가장 낮은 봉(저점 피벗)의 위치 목록."""
    out = []
    for i in range(len(lows)):
        lo, hi = max(0, i - half), min(len(lows), i + half + 1)
        if lows[i] == min(lows[lo:hi]):
            out.append(i)
    return out


def _double_bottom(lows):
    """서로 15봉 이상 떨어진 저점 피벗 두 곳 중 가장 낮은 두 곳."""
    pivots = sorted(_pivot_lows(lows), key=lambda i: lows[i])
    best = None
    for a in pivots:
        for b in pivots:
            if abs(a - b) < 15 or a > b:
                continue
            gap = abs(lows[a] - lows[b]) / min(lows[a], lows[b])
            if best is None or gap < best[2]:
                best = (lows[a], lows[b], gap, b - a)
    if best is None:
        low = min(lows)
        return low, low, 0.0, 0
    return best


def pattern_metrics(bars, split):
    visible = bars[: split + 1]
    highs = [b[2] for b in visible]
    lows = [b[3] for b in visible]
    closes = [b[4] for b in visible]
    volumes = [b[5] for b in visible]
    tail = min(20, len(visible))
    return {
        "last": closes[-1],
        "high": max(highs), "low": min(lows),
        "high_pos": highs.index(max(highs)),
        "high_recent_pos": len(highs) - 1 - max(range(len(highs)), key=lambda i: highs[i]),
        "ma20": _sma(closes, 20), "ma60": _sma(closes, min(60, len(closes))),
        "vol_ratio": (sum(volumes[-5:]) / 5.0) / max(1e-9, sum(volumes[-25:-5]) / max(1, len(volumes[-25:-5]))),
        "peak_vol_pos": len(volumes) - 1 - max(range(len(volumes)), key=lambda i: volumes[i]),
        "peak_vol_bar": volumes and visible[max(range(len(volumes)), key=lambda i: volumes[i])],
        "prior_high": max(highs[:-20]) if len(highs) > 20 else max(highs),
        "box_high": max(highs[:-5]) if len(highs) > 5 else max(highs),
        "low_a": _double_bottom(lows)[0],
        "low_b": _double_bottom(lows)[1],
        "low_gap": _double_bottom(lows)[2],
        "low_span": _double_bottom(lows)[3],
        "tail": tail,
    }


def verify_pattern(pattern, bars, split):
    """만들어진 봉이 그 패턴으로 읽히는지 확인한다(테스트도 같은 함수를 다시 돌린다)."""
    m = pattern_metrics(bars, split)
    if pattern == PATTERN_POOL[0]:      # 상승 추세
        assert m["last"] > m["ma20"] > m["ma60"], "상승 추세: 이동평균 배열이 어긋남"
        highs = [b[2] for b in bars[: split + 1]]
        lows = [b[3] for b in bars[: split + 1]]
        assert max(highs[-10:]) > max(highs[-30:-10]), "상승 추세: 고점이 높아지지 않음"
        assert min(lows[-10:]) > min(lows[-30:-10]), "상승 추세: 저점이 높아지지 않음"
    elif pattern == PATTERN_POOL[2]:    # 박스권 상단 돌파
        assert m["last"] > m["box_high"] * 1.01, "박스권 돌파: 종가가 박스 상단을 넘지 못함"
        assert m["vol_ratio"] >= 1.3, "박스권 돌파: 거래량이 늘지 않음"
    elif pattern == PATTERN_POOL[3]:    # 가짜 돌파
        assert m["high_recent_pos"] <= 10, "가짜 돌파: 고점이 최근이 아님"
        assert m["last"] < m["high"] * 0.97, "가짜 돌파: 고점에서 충분히 밀리지 않음"
        prior = m["prior_high"]
        closes = [b[4] for b in bars[: split + 1]]
        assert max(closes[-12:]) > prior, "가짜 돌파: 직전 고점을 넘은 종가가 없음"
    elif pattern == PATTERN_POOL[4]:    # 지지선 두 번 반등
        assert m["low_gap"] <= 0.025, "지지선: 두 저점이 다름"
        assert m["low_span"] >= 15, "지지선: 두 저점이 너무 가까움"
        assert m["last"] > max(m["low_a"], m["low_b"]) * 1.03, "지지선: 반등 폭이 부족함"
    elif pattern == PATTERN_POOL[5]:    # 저항선 되돌림
        assert m["high_recent_pos"] <= 14, "저항선: 고점이 최근이 아님"
        assert m["last"] < m["high"] * 0.96, "저항선: 저항에서 충분히 밀리지 않음"
        closes = [b[4] for b in bars[: split + 1]]
        assert max(closes) < m["high"], "저항선: 종가가 저항을 넘어섰음"
    elif pattern == PATTERN_POOL[7]:    # 클라이맥스
        assert m["peak_vol_pos"] <= 5, "클라이맥스: 최대 거래량 봉이 최근이 아님"
        bar = bars[split]
        assert bar[4] < bar[1] * 0.985, "클라이맥스: 마지막 봉이 음봉이 아님"
        assert m["vol_ratio"] >= 1.5, "클라이맥스: 거래량이 폭증하지 않음"
    else:
        raise AssertionError("검증 규칙이 없는 패턴: %s" % pattern)


def pattern_evidence(pattern, bars, split):
    m = pattern_metrics(bars, split)
    visible = bars[: split + 1]
    highs = [b[2] for b in visible]
    lows = [b[3] for b in visible]
    if pattern == PATTERN_POOL[0]:
        return ("보이는 구간은 20봉선(%s)이 60봉선(%s) 위에 있고, 최근 10봉의 고점(%s)과 저점(%s)은 "
                "그 앞 구간(고점 %s · 저점 %s)보다 높아진 모습입니다"
                % (_px(m["ma20"]), _px(m["ma60"]), _px(max(highs[-10:])), _px(min(lows[-10:])),
                   _px(max(highs[-30:-10])), _px(min(lows[-30:-10]))))
    if pattern == PATTERN_POOL[2]:
        return ("보이는 구간의 박스 상단(%s)을 마지막 5봉에서 종가가 %s까지 올라 넘어섰습니다. "
                "이때 거래량은 앞 20봉 평균의 %.1f배입니다" % (_px(m["box_high"]), _px(m["last"]), m["vol_ratio"]))
    if pattern == PATTERN_POOL[3]:
        return ("보이는 구간에서 종가가 직전 고점(%s)을 넘어섰지만, 마지막 종가는 %s까지 밀렸습니다. "
                "구간 최고가(%s)보다 %.1f%% 낮은 수준입니다"
                % (_px(m["prior_high"]), _px(m["last"]), _px(m["high"]), (1 - m["last"] / m["high"]) * 100))
    if pattern == PATTERN_POOL[4]:
        return ("보이는 구간에서 저점은 %s, %s 두 곳에서 같은 가격대를 지켰고, 마지막 종가는 %s입니다"
                % (_px(m["low_a"]), _px(m["low_b"]), _px(m["last"])))
    if pattern == PATTERN_POOL[5]:
        return ("보이는 구간에서 고점(%s) 부근에서 두 번 밀렸고, 마지막 종가는 %s까지 내려와 고점보다 %.1f%% 낮습니다"
                % (_px(m["high"]), _px(m["last"]), (1 - m["last"] / m["high"]) * 100))
    if pattern == PATTERN_POOL[7]:
        return ("마지막 봉은 거래량이 앞 20봉 평균의 %.1f배로 폭증한 가운데 시가 %s에서 %s까지 밀린 음봉이었습니다"
                % (m["vol_ratio"], _px(visible[-1][1]), _px(visible[-1][4])))
    raise AssertionError("설명 문구가 없는 패턴: %s" % pattern)


def _px(value):
    if abs(value) >= 1000:
        return "{:,.0f}".format(value)
    if abs(value) >= 100:
        return "{:.1f}".format(value)
    return "{:.2f}".format(value)


# ------------------------------------------------------------------ 데이터 조립
def band_for(ret):
    for key, label, test in FLOW_BANDS:
        if test(ret):
            return key, label
    raise ValueError("no band for %.4f" % ret)


def _shuffle(seq, seed):
    items = list(seq)
    for i in range(len(items) - 1, 0, -1):
        digest = hashlib_sha((seed + ":" + str(i)))
        j = digest % (i + 1)
        items[i], items[j] = items[j], items[i]
    return items


def hashlib_sha(text):
    import hashlib
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def build_explanation(spec, bars, split, pattern=None):
    hidden = bars[split + 1:]
    start_close = bars[split][4]
    end_close = hidden[-1][4]
    ret = (end_close / start_close - 1) * 100
    band_label = dict((k, l) for k, l, _ in FLOW_BANDS)[band_for(ret / 100)[0]]
    parts = []
    if pattern:
        parts.append(pattern_evidence(pattern, bars, split) + ".")
    if ret >= 2:
        move = "올라 %.1f%% 상승했습니다" % abs(ret)
    elif ret <= -2:
        move = "내려 %.1f%% 하락했습니다" % abs(ret)
    else:
        move = "제자리였습니다(%.1f%%)" % abs(ret)
    band_note = "" if pattern else " (정답 구간: %s)" % band_label
    parts.append("가려진 %d봉 동안 종가는 %s에서 %s까지 %s%s. 이 구간 고가는 %s, 저가는 %s입니다."
                 % (len(hidden), _px(start_close), _px(end_close), move, band_note,
                    _px(max(b[2] for b in hidden)), _px(min(b[3] for b in hidden))))
    m = pattern_metrics(bars, split)
    signal = []
    if not (pattern and "거래량" in pattern_evidence(pattern, bars, split)):
        if m["vol_ratio"] >= 1.25:
            signal.append("가려진 구간 직전 5봉 거래량은 앞 20봉 평균의 %.1f배로 늘어 있었습니다." % m["vol_ratio"])
        elif m["vol_ratio"] <= 0.8:
            signal.append("가려진 구간 직전 5봉 거래량은 앞 20봉 평균의 %.1f배로 줄어 있었습니다." % m["vol_ratio"])
    gap = (m["last"] / m["ma20"] - 1) * 100
    if gap >= 4:
        signal.append("직전 종가는 20봉선보다 %.1f%% 위에 있었습니다." % gap)
    elif gap <= -4:
        signal.append("직전 종가는 20봉선보다 %.1f%% 아래에 있었습니다." % abs(gap))
    parts.extend(signal)
    parts.append(spec["lesson"])
    return " ".join(parts)


def build_episode(spec, index):
    bars = build_bars(spec)
    split = sum(leg[0] for leg in spec["legs"]) - 1
    assert 0 < split < len(bars) - 1, "%s: 가려진 구간 없음" % spec["id"]
    start_close = bars[split][4]
    ret = (bars[-1][4] / start_close - 1)
    band_key, band_label = band_for(ret)
    if spec["quiz"] == "pattern":
        assert pattern_metrics(bars, split)["last"] == bars[split][4]
        verify_pattern(spec["pattern"], bars, split)
        correct = spec["pattern"]
        conflict = {PATTERN_POOL[3]: {PATTERN_POOL[2]}, PATTERN_POOL[2]: {PATTERN_POOL[3]},
                    PATTERN_POOL[4]: {PATTERN_POOL[9]}, PATTERN_POOL[9]: {PATTERN_POOL[4]}}.get(correct, set())
        decoys = _shuffle([p for p in PATTERN_POOL if p != correct and p not in conflict], spec["id"])[:3]
        prompt = "보이는 구간의 흐름을 가장 잘 설명한 것은?"
        quiz_extra = {"pattern": correct}
    else:
        assert band_key == spec["expect_band"], (
            "%s: 계산된 흐름 %s(%+.1f%%)가 기대 %s와 다름" % (spec["id"], band_key, ret * 100, spec["expect_band"]))
        correct = band_label
        decoys = _shuffle([l for k, l, _ in FLOW_BANDS if k != band_key], spec["id"])[:3]
        prompt = "가려진 마지막 구간(%d봉), 이어질 흐름은?" % (len(bars) - split - 1)
        quiz_extra = {"band": band_key}

    pos = index % 4
    choices = decoys[:]
    choices.insert(pos, correct)
    episode = {
        "id": spec["id"],
        "category": spec["category"],
        "code": "SYN-%02d" % (index + 1),
        "name": "SYN-%02d · %s" % (index + 1, spec["name"]),
        "synthetic": True,
        "interval": spec["interval"],
        "period": "%s ~ %s" % (bars[0][0], bars[-1][0]),
        "visible_until": bars[split][0],
        "split_index": split,
        "future_return": round(ret * 100, 2),
        "bars": bars,
        "pattern": spec.get("pattern"),
        "quiz": {"type": spec["quiz"], "prompt": prompt, "choices": choices, "answer": pos, **quiz_extra},
        "explanation": build_explanation(spec, bars, split, spec.get("pattern")),
        "data_note": NOTICE,
    }
    return episode


def build_dataset(write=True):
    episodes = [build_episode(spec, i) for i, spec in enumerate(SCENARIOS)]
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "synthetic": True,
        "notice": NOTICE,
        "generator": "chart_generate_data.py",
        "categories": CATEGORIES,
        "episodes": episodes,
    }
    if write:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        print("저장: %s (문제 %d개, %.1f KB)" % (DATA_PATH, len(episodes), os.path.getsize(DATA_PATH) / 1024))
    return payload


def main():
    payload = build_dataset()
    for ep in payload["episodes"]:
        hidden = len(ep["bars"]) - ep["split_index"] - 1
        print("%-14s %-4s %-22s %2d봉 (보임 %2d · 가림 %2d) %+6.1f%%  %-8s %s"
              % (ep["id"], "주봉" if ep["interval"] == "1wk" else "일봉", ep["name"],
                 len(ep["bars"]), ep["split_index"] + 1, hidden, ep["future_return"],
                 ep["quiz"]["type"], ep["quiz"]["choices"][ep["quiz"]["answer"]][:30]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

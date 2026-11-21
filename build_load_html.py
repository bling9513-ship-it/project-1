# -*- coding: utf-8 -*-
"""한 번 더 싣기(load.html) — 손수레 적재 푸시 유어 럭 게임 빌더.

규칙 요약
  · 손수레 적재 한도 100kg, 좌우 균형 허용 오차 28kg, 하루 5회차.
  · 상자는 이름·표기 무게 범위(예: 15~21kg)·점수를 보여 주고, 싣는 순간 실측 무게가
    확정된다. 다음 상자 후보의 표기 무게도 미리 보이므로 "한 번 더 실을지"를 확률로 판단한다.
  · 실측 무게가 한도를 넘으면 과적, 좌우 차가 허용 오차를 넘으면 전복 — 그 회차 점수는 0점,
    연속 배송 보너스도 초기화된다.
  · 배송 점수 = 상자 점수 합 × 균형 배율(최대 1.5배) × 연속 배송 배율(최대 1.5배).
  · 매일 KST 날짜로 같은 상자 순서(14일치 + 폴백)가 열려, 다른 선택으로 최고 점수를 겨룬다.
  · 기록은 localStorage(load_cart_stats_v1)에만 저장한다.
"""
import json
import os
import random
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "load_data.json")
LOAD_HTML = os.path.join(BASE_DIR, "load.html")
KST = timezone(timedelta(hours=9))

LIMIT = 100
TILT = 28
TRIPS = 5
DAILY_COUNT = 14

# (균형 비율 하한, 배율) — 위에서부터 처음 만족하는 구간을 쓴다.
TIERS = [(0.90, 1.5), (0.78, 1.25), (0.62, 1.0), (0.0, 0.75)]
STREAK_STEP = 0.1
STREAK_CAP = 5

# (이름, 기준 무게, 기준 점수)
CATALOG = [
    ("서류 상자", 9, 26), ("과일 상자", 14, 22), ("생수 팩", 22, 18), ("책 박스", 19, 24),
    ("공구함", 21, 20), ("이불 보따리", 12, 21), ("화분", 15, 25), ("주방용품", 17, 19),
    ("전자레인지", 23, 16), ("캠핑 의자", 11, 23), ("와인 상자", 16, 28), ("쌀 포대", 24, 15),
    ("라면 박스", 13, 17), ("신발 상자", 8, 20), ("전공서적", 20, 27), ("미니 냉장고", 24, 14),
    ("택배 소포", 10, 19), ("유리병 상자", 18, 29), ("악기 케이스", 21, 30), ("문구 세트", 7, 22),
]

SPREAD = {"easy": 2, "normal": 3, "hard": 4}
RATIOS = {
    "daily": (0.70, 0.82, 0.93),
    "beginner": (0.62, 0.75, 0.88),
    "mid": (0.68, 0.81, 0.92),
    "adv": (0.72, 0.84, 0.95),
}

DAILY_SPECS = [
    ("daily-01", "골목 배송", 0),
    ("daily-02", "시장길 배송", 1),
    ("daily-03", "이사 도움", 2),
    ("daily-04", "새벽 배송", 3),
    ("daily-05", "장보기 대행", 1),
    ("daily-06", "택배 폭탄", 2),
    ("daily-07", "마감 러시", 0),
    ("daily-08", "동네 순회", 3),
    ("daily-09", "비 오는 날", 1),
    ("daily-10", "한파 배송", 2),
    ("daily-11", "연휴 전 배송", 0),
    ("daily-12", "월말 정산", 3),
    ("daily-13", "첫 배송", 1),
    ("daily-14", "늦은 귀가", 2),
]

PRACTICE_SPECS = [
    ("p-b1", "연습 · 빈 손수레", "beginner", 0),
    ("p-b2", "연습 · 가벼운 짐", "beginner", 1),
    ("p-b3", "연습 · 두 상자", "beginner", 2),
    ("p-m1", "연습 · 시장길", "mid", 3),
    ("p-m2", "연습 · 쌓아 올리기", "mid", 4),
    ("p-m3", "연습 · 무거운 상자", "mid", 5),
    ("p-a1", "연습 · 마감 압박", "adv", 6),
    ("p-a2", "연습 · 균형의 한계", "adv", 7),
    ("p-a3", "연습 · 마지막 회차", "adv", 8),
]


def balance_mult(ratio):
    for minimum, mult in TIERS:
        if ratio >= minimum:
            return mult
    return TIERS[-1][1]


def streak_mult(streak):
    return round(1 + min(streak, STREAK_CAP) * STREAK_STEP, 2)


def trip_optimum(boxes):
    """실측 무게를 모두 아는 상태의 회차 최고 점수(배율 제외)."""
    best = 0.0
    n = len(boxes)

    def walk(index, left, right, score, count):
        nonlocal best
        if count > 0:
            total = left + right
            ratio = 1 - abs(left - right) / total
            best = max(best, score * balance_mult(ratio))
        if index >= n:
            return
        kg = boxes[index]["kg"]
        point = boxes[index]["score"]
        if left + kg + right <= LIMIT and abs(left + kg - right) <= TILT:
            walk(index + 1, left + kg, right, score + point, count + 1)
        if left + right + kg <= LIMIT and abs(left - right - kg) <= TILT:
            walk(index + 1, left, right + kg, score + point, count + 1)

    walk(0, 0, 0, 0, 0)
    return best


def make_trip(rng, spread, cid, trip_no):
    n = rng.choice([4, 5, 5, 6])
    picks = rng.sample(CATALOG, n)
    boxes = []
    for slot, (name, base_kg, base_score) in enumerate(picks, start=1):
        kg = max(8, min(24, base_kg + rng.randint(-2, 2)))
        score = base_score + rng.randint(-4, 4)
        if rng.random() < 0.18:            # 급한 소포: 가볍고 점수가 높다
            kg = max(8, kg - 4)
            score += 8
        lo = max(4, kg - rng.randint(1, spread))
        hi = min(TILT, kg + rng.randint(1, spread))
        if hi - lo < 2:
            hi = min(TILT, lo + 2)
        boxes.append({
            "id": "%s-t%d-b%d" % (cid, trip_no, slot),
            "name": name,
            "kg": kg,
            "lo": lo,
            "hi": hi,
            "score": score,
        })
    # 회차 상자를 모두 실을 수 없도록 총합을 한도 위로 올린다(푸시 유어 럭의 긴장).
    guard = 0
    while sum(box["kg"] for box in boxes) <= LIMIT + 4 and guard < 6:
        guard += 1
        name, base_kg, base_score = CATALOG[(rng.randrange(len(CATALOG)) + guard) % len(CATALOG)]
        kg = max(18, min(24, base_kg + 2))
        lo = max(4, kg - rng.randint(1, spread))
        hi = min(TILT, kg + rng.randint(1, spread))
        boxes.append({
            "id": "%s-t%d-b%d" % (cid, trip_no, len(boxes) + 1),
            "name": name,
            "kg": kg,
            "lo": lo,
            "hi": hi,
            "score": base_score,
        })
    rng.shuffle(boxes)
    for slot, box in enumerate(boxes, start=1):
        box["id"] = "%s-t%d-b%d" % (cid, trip_no, slot)
    return boxes


def make_challenge(cid, title, level, seed, spread):
    rng = random.Random(seed)
    batches = []
    trip_best = []
    raw_total = 0.0
    for trip_no in range(1, TRIPS + 1):
        for attempt in range(12):
            boxes = make_trip(rng, spread, cid, trip_no)
            raw = trip_optimum(boxes)
            if raw > 0:
                break
        else:
            raise RuntimeError("회차 최적해를 찾지 못했습니다: %s #%d" % (cid, trip_no))
        batches.append(boxes)
        trip_best.append(round(raw * streak_mult(trip_no - 1)))
        raw_total += raw * streak_mult(trip_no - 1)
    optimal = int(round(raw_total))
    r1, r2, r3 = RATIOS[level]
    goal = int(round(optimal * r1))
    stars = [goal, int(round(optimal * r2)), int(round(optimal * r3))]
    # 별 기준은 단조 증가해야 하고, 최고 별은 실측 정보 기준 최적해 이하여야 한다.
    for i in range(1, 3):
        if stars[i] <= stars[i - 1]:
            stars[i] = stars[i - 1] + max(1, int(round(optimal * 0.04)))
    stars[2] = min(stars[2], optimal)
    return {
        "id": cid,
        "title": title,
        "level": level,
        "seed": seed,
        "note": "표기 무게는 어림값입니다. 실측이 한도를 넘으면 그 회차는 0점입니다.",
        "goal": goal,
        "stars": stars,
        "optimal": optimal,
        "tripBest": trip_best,
        "limit": LIMIT,
        "tilt": TILT,
        "batches": batches,
    }


def build_data(now):
    daily = []
    for index, (cid, title, spread_index) in enumerate(DAILY_SPECS):
        spread = SPREAD["normal"] if spread_index % 2 == 0 else SPREAD["hard"]
        daily.append(make_challenge(cid, title, "daily", 7000000 + index * 7919 + 11, spread))
    practice = []
    for index, (cid, title, level, spread_index) in enumerate(PRACTICE_SPECS):
        spread = SPREAD["easy"] if level == "beginner" else (
            SPREAD["normal"] if level == "mid" else SPREAD["hard"])
        practice.append(make_challenge(cid, title, level, 9100000 + index * 6151 + 7, spread))
    fallback = make_challenge("fallback", "기본 배송", "daily", 20261121, SPREAD["normal"])
    return {
        "built_at": now.strftime("%Y-%m-%d %H:%M:%S KST"),
        "rules": {
            "limit": LIMIT,
            "tilt": TILT,
            "trips": TRIPS,
            "streakStep": STREAK_STEP,
            "streakCap": STREAK_CAP,
            "tiers": [{"min": minimum, "mult": mult} for minimum, mult in TIERS],
        },
        "levels": {"daily": "오늘", "beginner": "입문", "mid": "중급", "adv": "고급"},
        "daily": daily,
        "practice": practice,
        "fallback": fallback,
    }


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
      --warn-bg: #fffbeb; --warn-text: #b45309; --warn-border: #fde68a;
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
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
      --warn-bg: rgba(245, 158, 11, 0.12); --warn-text: #fcd34d; --warn-border: rgba(245, 158, 11, 0.32);
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }

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
    }
    .nav-container { max-width: 1360px; margin: 0 auto; padding: 0 20px; height: 60px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
    .brand-logo-img { width: 28px; height: 28px; border-radius: 7px; object-fit: cover; display: block; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15); flex-shrink: 0; }
    .brand-name { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; white-space: nowrap; }
    .update-meta { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); white-space: nowrap; }
    .live-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block; flex-shrink: 0; }
    .icon-btn { width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; cursor: pointer; text-decoration: none; }
    .icon-btn:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .load-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 72px; }

    .load-hero { margin-bottom: 13px; }
    .load-pill {
      display: inline-block;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 8px;
      margin-bottom: 8px;
    }
    .load-hero h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.035em; }
    .load-hero p { margin-top: 5px; font-size: 13px; color: var(--text-secondary); max-width: 680px; }

    .load-shell { display: grid; grid-template-columns: 324px minmax(0, 1fr); gap: 16px; align-items: start; }
    .load-rail { display: flex; flex-direction: column; gap: 12px; position: sticky; top: 76px; }

    .load-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 16px;
      padding: 13px 14px;
      box-shadow: var(--card-shadow);
      min-width: 0;
    }
    .load-card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 9px; }
    .load-card-head h2 { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; }
    .load-card-head span { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
    .load-foot { margin-top: 9px; font-size: 10px; line-height: 1.45; color: var(--text-muted); }

    .load-seg { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 11px; }
    .load-seg-btn {
      border: 0; background: transparent; border-radius: 8px; padding: 8px 4px;
      font-family: inherit; font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary); cursor: pointer; white-space: nowrap;
      transition: background-color 160ms ease, color 160ms ease;
    }
    .load-seg-btn:hover { color: var(--text-primary); }
    .load-seg-btn.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }

    .load-meter { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 10px; font-size: 11.5px; color: var(--text-secondary); }
    .load-meter strong { font-size: 16px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .load-meter span { white-space: nowrap; }

    .streak-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 8px; }
    .streak-chip {
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 10.5px; font-weight: 700; letter-spacing: -0.01em;
      color: var(--accent-primary); background: var(--accent-subtle);
      border: 1px solid var(--border-default); border-radius: 999px; padding: 3px 8px;
      font-variant-numeric: tabular-nums; white-space: nowrap;
    }
    .streak-chip.is-hot { color: var(--warn-text); background: var(--warn-bg); border-color: var(--warn-border); }
    .streak-best { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
    .load-status { margin-top: 9px; font-size: 10.5px; line-height: 1.5; color: var(--text-muted); min-height: 16px; }

    /* ----- 게임 방법(움직이는 3단계 데모) ----- */
    .guide-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .guide-head h2 { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; }
    .guide-toggle {
      border: 0; background: transparent; font-family: inherit; font-size: 11px; font-weight: 600;
      color: var(--accent-primary); cursor: pointer; padding: 4px 0 4px 8px; white-space: nowrap;
    }
    .guide-body { margin-top: 9px; }
    .gl-stage {
      position: relative; display: flex; align-items: flex-end; gap: 12px;
      padding: 13px 11px 10px; border: 1px solid var(--border-default); border-radius: 12px;
      background: var(--bg-page); min-height: 86px;
    }
    .gl-cart { position: relative; width: 74px; flex: 0 0 auto; }
    .gl-stack {
      position: relative; height: 40px; display: flex; flex-direction: column-reverse; gap: 2px;
      align-items: center; margin-bottom: 3px;
    }
    .gl-crate {
      width: 28px; height: 15px; border: 1px solid var(--border-strong); border-radius: 3px;
      background: var(--bg-subtle); color: var(--text-secondary);
      font-size: 7px; font-weight: 700; display: flex; align-items: center; justify-content: center;
    }
    .gl-box {
      position: absolute; left: 50%; margin-left: -15px; bottom: 21px; width: 30px; height: 17px;
      border: 1px solid var(--accent-primary); border-radius: 3px; background: var(--accent-subtle);
      color: var(--accent-primary); font-size: 7.5px; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      opacity: 0; animation: glDrop 9s ease-in-out infinite;
    }
    .gl-bed { display: block; position: relative; height: 7px; border-radius: 3px; background: var(--text-muted); }
    .gl-bed::before {
      content: ""; position: absolute; left: 4px; right: -9px; top: -13px; height: 13px;
      border-left: 2px solid var(--border-strong); border-top: 2px solid var(--border-strong);
      border-top-left-radius: 4px;
    }
    .gl-wheels { display: block; position: relative; height: 8px; }
    .gl-wheels span {
      position: absolute; top: 1px; width: 8px; height: 8px; border-radius: 50%;
      border: 2px solid var(--text-muted); background: var(--bg-surface);
    }
    .gl-wheels span:first-child { left: 10px; }
    .gl-wheels span:last-child { right: 10px; }
    .gl-meter { display: block; flex: 1 1 auto; min-width: 0; }
    .gl-meter-track {
      display: block; position: relative; height: 9px; border-radius: 999px; background: var(--bg-muted); overflow: hidden;
    }
    .gl-fill {
      position: absolute; left: 0; top: 0; bottom: 0; width: 0; border-radius: 999px;
      background: var(--ok-text); animation: glFill 9s ease-in-out infinite;
    }
    .gl-meter-marks { display: flex; justify-content: space-between; margin-top: 3px; font-size: 6.5px; color: var(--text-muted); }
    .gl-kg { display: block; }
    .gl-kg { margin-top: 4px; font-size: 9px; font-weight: 700; color: var(--text-secondary); font-variant-numeric: tabular-nums; opacity: 0; animation: glKg 9s ease-in-out infinite; }
    .gl-chips { display: flex; align-items: center; gap: 6px; margin-top: 8px; min-height: 22px; }
    .gl-ship {
      display: inline-flex; align-items: center; justify-content: center;
      padding: 3px 9px; border-radius: 7px; background: var(--accent-primary); color: #ffffff;
      font-size: 9.5px; font-weight: 700; opacity: 0; animation: glShip 9s ease-in-out infinite;
    }
    .gl-bonus { font-size: 11px; font-weight: 700; color: var(--ok-text); font-variant-numeric: tabular-nums; opacity: 0; animation: glBonus 9s ease-in-out infinite; }
    .gl-balance { margin-left: auto; display: inline-flex; align-items: center; gap: 4px; font-size: 8.5px; color: var(--text-muted); }
    .gl-balance b { color: var(--accent-primary); font-weight: 700; }
    .guide-caption { position: relative; height: 18px; margin-top: 8px; }
    .gc-step {
      position: absolute; left: 0; top: 0; display: inline-flex; align-items: center; gap: 5px;
      font-size: 10.5px; font-weight: 600; color: var(--text-secondary); opacity: 0; white-space: nowrap;
    }
    .gc-num {
      display: inline-flex; align-items: center; justify-content: center; width: 13px; height: 13px;
      border-radius: 50%; background: var(--bg-muted); color: var(--text-secondary);
      font-size: 8.5px; font-weight: 700; flex-shrink: 0;
    }
    .gc-3 .gc-num { background: var(--ok-text); color: #ffffff; }
    .gc-1 { animation: gc1 9s ease infinite; }
    .gc-2 { animation: gc2 9s ease infinite; }
    .gc-3 { animation: gc3 9s ease infinite; }
    .guide-note { margin-top: 6px; font-size: 10px; line-height: 1.5; color: var(--text-muted); }

    @keyframes glDrop {
      0%, 4% { opacity: 0; transform: translateY(-24px) rotate(-4deg); }
      7% { opacity: 1; transform: translateY(-24px) rotate(-4deg); }
      16% { opacity: 1; transform: translateY(0) rotate(0deg); }
      18% { transform: translateY(2px); }
      21%, 92% { opacity: 1; transform: translateY(0); }
      96%, 100% { opacity: 0; transform: translateY(0); }
    }
    @keyframes glFill {
      0%, 18% { width: 0; background: var(--ok-text); }
      34% { width: 48%; background: var(--ok-text); }
      50%, 62% { width: 72%; background: var(--warn-text); }
      92% { width: 72%; background: var(--warn-text); }
      96%, 100% { width: 0; background: var(--ok-text); }
    }
    @keyframes glKg {
      0%, 18% { opacity: 0; }
      26%, 92% { opacity: 1; }
      96%, 100% { opacity: 0; }
    }
    @keyframes glShip {
      0%, 56% { opacity: 0; transform: scale(0.86); }
      62% { opacity: 1; transform: scale(1.06); }
      66%, 92% { opacity: 1; transform: scale(1); }
      96%, 100% { opacity: 0; transform: scale(0.86); }
    }
    @keyframes glBonus {
      0%, 62% { opacity: 0; transform: translateY(4px); }
      68% { opacity: 1; transform: translateY(0); }
      80% { opacity: 1; transform: translateY(-4px); }
      90%, 100% { opacity: 0; transform: translateY(-8px); }
    }
    @keyframes gc1 {
      0%, 30% { opacity: 1; }
      36%, 100% { opacity: 0; }
    }
    @keyframes gc2 {
      0%, 34% { opacity: 0; }
      38%, 56% { opacity: 1; }
      62%, 100% { opacity: 0; }
    }
    @keyframes gc3 {
      0%, 58% { opacity: 0; }
      62%, 92% { opacity: 1; }
      96%, 100% { opacity: 0; }
    }

    /* ----- 목표 ----- */
    .goal-list { list-style: none; display: flex; flex-direction: column; gap: 6px; }
    .goal-row { display: flex; align-items: center; gap: 7px; font-size: 11.5px; color: var(--text-secondary); }
    .goal-row svg { width: 12px; height: 12px; flex-shrink: 0; fill: var(--bg-muted); stroke: none; }
    .goal-row.is-on svg { fill: var(--warn-text); }
    .goal-row.is-on { color: var(--text-primary); font-weight: 600; }
    .goal-label { flex: 1 1 auto; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .goal-row b { font-variant-numeric: tabular-nums; font-size: 11.5px; }
    .goal-bar { position: relative; height: 6px; margin-top: 9px; border-radius: 999px; background: var(--bg-muted); overflow: hidden; }
    .goal-bar span { position: absolute; left: 0; top: 0; bottom: 0; width: 0; border-radius: 999px; background: var(--accent-primary); transition: width 420ms ease; }

    /* ----- 기록 ----- */
    .record-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
    .record-grid dt { font-size: 10.5px; color: var(--text-muted); white-space: nowrap; }
    .record-grid dd { font-size: 14.5px; font-weight: 700; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .record-history { list-style: none; display: flex; flex-direction: column; gap: 5px; margin-top: 9px; }
    .record-history li { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 11px; color: var(--text-secondary); }
    .record-history li span:last-child { font-variant-numeric: tabular-nums; font-weight: 600; }
    .record-history li.is-empty { color: var(--text-muted); }

    /* ----- 보드(손수레) ----- */
    .load-main { min-width: 0; }
    .load-main-head { display: flex; align-items: baseline; gap: 9px; margin-bottom: 8px; }
    .load-main-title { font-size: 14px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap; }
    .load-main-sub { flex: 1 1 auto; min-width: 0; font-size: 11.5px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .load-reset { border: 0; background: transparent; font-family: inherit; font-size: 10.5px; font-weight: 600; color: var(--accent-primary); cursor: pointer; padding: 2px 0; white-space: nowrap; }
    .load-reset:hover { text-decoration: underline; }
    /* 진행 중인 판이 자정을 넘겼을 때만 뜨는 가벼운 안내 배지 */
    .day-badge { display: none; margin: 0 0 9px; padding: 6px 9px; border: 1px solid var(--border-default); border-radius: 10px; background: var(--bg-surface); font-size: 11px; line-height: 1.4; color: var(--text-secondary); }
    .day-badge:not([hidden]) { display: block; }

    .cart-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 18px;
      padding: 11px 13px 12px;
      box-shadow: var(--card-shadow);
      max-width: 600px;
      transition: border-color 220ms ease, box-shadow 220ms ease;
    }
    .cart-card.is-warn { border-color: var(--warn-border); }
    .cart-card.is-danger { border-color: var(--no-border); box-shadow: 0 0 0 3px var(--no-bg); }
    .cart-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 10.5px; color: var(--text-muted); }
    .cart-cap { font-size: 11.5px; color: var(--text-secondary); white-space: nowrap; }
    .cart-cap b { font-size: 16px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .cart-cap.is-warn b { color: var(--warn-text); }
    .cart-cap.is-danger b { color: var(--no-text); }

    .cart-stage { position: relative; padding: 8px 0 2px; }
    .cart-rig { position: relative; margin: 0 auto; max-width: 420px; transform-origin: 50% 88%; transition: transform 420ms cubic-bezier(0.2, 0.8, 0.2, 1); }
    .cart-deck {
      position: relative; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
      padding: 8px 9px 6px; border: 1px dashed var(--border-strong); border-bottom: 0;
      border-top-left-radius: 10px; border-top-right-radius: 10px; background: var(--bg-page);
    }
    .cart-deck::after {
      content: ""; position: absolute; left: 50%; top: 8px; bottom: 6px; width: 1px;
      background: var(--border-subtle);
    }
    .deck-col { display: flex; flex-direction: column; min-width: 0; }
    .deck-head {
      display: flex; align-items: baseline; justify-content: center; gap: 5px;
      font-size: 9.5px; color: var(--text-muted); margin-bottom: 5px; white-space: nowrap;
    }
    .deck-head b { font-size: 12px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .deck-head.is-heavy b { color: var(--warn-text); }
    .deck-head.is-over b { color: var(--no-text); }
    .crate-stack { display: flex; flex-direction: column-reverse; gap: 2px; height: 100px; min-width: 0; }
    .deck-empty {
      position: absolute; left: 0; right: 0; top: 56%; transform: translateY(-50%);
      text-align: center; font-size: 10px; color: var(--text-muted); pointer-events: none;
    }
    .crate {
      position: relative; flex: 1 1 0; min-height: 7px; max-height: 24px;
      border: 1px solid var(--border-strong); border-radius: 4px; background: var(--bg-surface);
      display: flex; align-items: center; justify-content: center;
      font-size: 8.5px; font-weight: 700; line-height: 1; color: var(--text-secondary);
      font-variant-numeric: tabular-nums; overflow: hidden; letter-spacing: -0.02em;
    }
    .crate.is-heavy { background: var(--bg-subtle); }
    .crate.is-light { background: var(--accent-subtle); border-color: var(--border-default); color: var(--accent-primary); }
    .crate.is-new { animation: crateDrop 340ms cubic-bezier(0.2, 0.9, 0.3, 1.2) both; }
    .crate.is-fallen { animation: crateFall 520ms ease-in both; }
    .cart-bed { height: 9px; border-radius: 0 0 4px 4px; background: var(--text-muted); }
    .cart-frame { position: relative; height: 17px; }
    .cart-frame span {
      position: absolute; top: 1px; width: 13px; height: 13px; border-radius: 50%;
      border: 2.5px solid var(--text-muted); background: var(--bg-surface);
    }
    .cart-frame span:first-child { left: 34px; }
    .cart-frame span:last-child { right: 34px; }
    .cart-rig.is-bounce { animation: cartBounce 300ms cubic-bezier(0.2, 0.9, 0.3, 1.1); }
    .cart-rig.is-shake { animation: cartShake 480ms ease-in-out; }

    .cart-meters { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
    .gauge-head, .tilt-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 10.5px; color: var(--text-muted); }
    .gauge-head b, .tilt-head b { font-size: 10.5px; font-weight: 700; letter-spacing: -0.01em; }
    .gauge-head b.is-safe { color: var(--ok-text); }
    .gauge-head b.is-warn { color: var(--warn-text); }
    .gauge-head b.is-danger { color: var(--no-text); }
    .gauge-head b.is-danger { animation: valuePulse 900ms ease-in-out infinite; }
    .gauge-track {
      position: relative; height: 10px; margin-top: 5px; border-radius: 999px;
      background: var(--bg-muted); overflow: hidden;
    }
    .gauge-track::after {
      content: ""; position: absolute; left: 70%; top: 0; bottom: 0; width: 1px; background: var(--bg-surface); opacity: 0.9;
    }
    .gauge-fill {
      position: absolute; left: 0; top: 0; bottom: 0; width: 0; border-radius: 999px;
      background: var(--ok-text); transition: width 420ms cubic-bezier(0.2, 0.8, 0.2, 1), background-color 300ms ease;
    }
    .gauge-fill.is-warn { background: var(--warn-text); }
    .gauge-fill.is-danger { background: var(--no-text); }
    .gauge-legend { display: flex; align-items: center; gap: 8px; margin-top: 5px; font-size: 9px; color: var(--text-muted); flex-wrap: wrap; }
    .gauge-legend span { display: inline-flex; align-items: center; gap: 3px; white-space: nowrap; }
    .gauge-legend i { width: 6px; height: 6px; border-radius: 2px; display: inline-block; }
    .lg-safe { background: var(--ok-text); }
    .lg-warn { background: var(--warn-text); }
    .lg-danger { background: var(--no-text); }

    .tilt-track { position: relative; height: 9px; margin-top: 5px; border-radius: 999px; background: var(--bg-muted); }
    .tilt-track::before {
      content: ""; position: absolute; left: 50%; top: -2px; bottom: -2px; width: 1px; background: var(--border-strong);
    }
    .tilt-zone { position: absolute; top: 0; bottom: 0; background: var(--warn-bg); opacity: 0.9; }
    .tilt-zone.left { left: 0; width: 25%; border-radius: 999px 0 0 999px; }
    .tilt-zone.right { right: 0; width: 25%; border-radius: 0 999px 999px 0; }
    .tilt-fill { position: absolute; top: 0; bottom: 0; width: 0; border-radius: 999px; background: var(--ok-text); transition: left 320ms ease, width 320ms ease, background-color 300ms ease; }
    .tilt-fill.is-warn { background: var(--warn-text); }
    .tilt-fill.is-danger { background: var(--no-text); }
    .tilt-note { margin-top: 4px; font-size: 9px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    /* ----- 상자 카드 ----- */
    .box-card {
      margin-top: 12px; max-width: 600px;
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 12px 13px; box-shadow: var(--card-shadow);
    }
    .box-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 10.5px; color: var(--text-muted); }
    .box-tag { display: inline-flex; align-items: center; gap: 5px; font-weight: 700; color: var(--text-secondary); }
    .box-tag::before { content: ""; width: 6px; height: 6px; border-radius: 2px; background: var(--accent-primary); }
    .box-body { display: flex; align-items: center; gap: 11px; margin-top: 8px; }
    .box-icon {
      width: 42px; height: 42px; flex: 0 0 auto; border-radius: 10px;
      border: 1px solid var(--border-default); background: var(--bg-page);
      display: flex; align-items: center; justify-content: center; color: var(--accent-primary);
    }
    .box-icon svg { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
    .box-info { min-width: 0; flex: 1 1 auto; }
    .box-name { font-size: 15px; font-weight: 700; letter-spacing: -0.03em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .box-stats { display: flex; align-items: center; gap: 6px; margin-top: 5px; flex-wrap: wrap; }
    .box-stat {
      display: inline-flex; align-items: baseline; gap: 3px;
      font-size: 10.5px; color: var(--text-muted); background: var(--bg-subtle);
      border-radius: 6px; padding: 2px 6px; white-space: nowrap;
    }
    .box-stat b { font-size: 12.5px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .box-stat.score b { color: var(--accent-primary); }

    .next-strip {
      display: flex; align-items: center; gap: 7px; margin-top: 9px; padding: 6px 8px;
      border: 1px dashed var(--border-strong); border-radius: 9px; background: var(--bg-page);
      font-size: 10.5px; color: var(--text-secondary); min-width: 0;
    }
    .next-tag { font-size: 9.5px; font-weight: 700; color: var(--text-muted); white-space: nowrap; }
    .next-name { font-weight: 700; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
    .next-kg, .next-score { font-variant-numeric: tabular-nums; white-space: nowrap; }
    .next-score { margin-left: auto; color: var(--accent-primary); font-weight: 700; }

    .box-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-top: 10px; }
    .side-btn {
      display: flex; align-items: center; justify-content: center; gap: 5px;
      padding: 11px 6px; border: 1px solid var(--border-default); border-radius: 11px;
      background: var(--bg-page); color: var(--text-primary);
      font-family: inherit; font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em;
      cursor: pointer; min-width: 0; white-space: nowrap;
      transition: background-color 160ms ease, border-color 160ms ease, transform 160ms ease;
    }
    .side-btn:hover { border-color: var(--border-strong); background: var(--bg-subtle); }
    .side-btn:active { transform: scale(0.985); }
    .side-btn .risk-tag {
      font-size: 9px; font-weight: 700; padding: 1px 4px; border-radius: 4px;
      background: var(--ok-bg); color: var(--ok-text); white-space: nowrap;
    }
    .side-btn .risk-tag.is-near { background: var(--warn-bg); color: var(--warn-text); }
    .side-btn .risk-tag.is-risk { background: var(--no-bg); color: var(--no-text); }
    .side-btn.is-risk { border-color: var(--no-border); }
    .side-btn:disabled, .ship-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

    .ship-btn {
      display: flex; align-items: center; justify-content: center; gap: 6px;
      width: 100%; margin-top: 7px; padding: 12px 8px;
      border: 0; border-radius: 11px; background: var(--accent-primary); color: #ffffff;
      font-family: inherit; font-size: 13.5px; font-weight: 700; letter-spacing: -0.02em;
      cursor: pointer; transition: background-color 160ms ease, transform 160ms ease;
    }
    .ship-btn:hover { background: var(--accent-hover); }
    .ship-btn:active { transform: scale(0.99); }
    .ship-btn span { font-size: 11.5px; font-weight: 700; opacity: 0.92; font-variant-numeric: tabular-nums; }
    .box-note { margin-top: 7px; font-size: 10px; line-height: 1.45; color: var(--text-muted); }

    /* ----- 회차 결과 ----- */
    .trip-panel {
      position: relative; margin-top: 12px; max-width: 600px;
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 14px; box-shadow: var(--card-shadow);
      animation: panelIn 260ms ease-out both;
    }
    .trip-panel.is-fail { border-color: var(--no-border); background: var(--no-bg); }
    .trip-badge {
      display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 6px;
      font-size: 10.5px; font-weight: 700;
      background: var(--ok-bg); color: var(--ok-text); border: 1px solid var(--ok-border);
    }
    .trip-panel.is-fail .trip-badge { background: var(--no-bg); color: var(--no-text); border-color: var(--no-border); }
    .trip-title { margin-top: 7px; font-size: 15px; font-weight: 700; letter-spacing: -0.03em; }
    .trip-score { display: flex; align-items: baseline; gap: 4px; margin-top: 4px; }
    .trip-score strong { font-size: 34px; font-weight: 700; letter-spacing: -0.045em; font-variant-numeric: tabular-nums; }
    .trip-score span { font-size: 13px; color: var(--text-muted); }
    .trip-panel.is-fail .trip-score strong { color: var(--no-text); }
    .trip-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; margin-top: 10px; }
    .trip-grid dt { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
    .trip-grid dd { font-size: 13px; font-weight: 700; font-variant-numeric: tabular-nums; }
    .trip-note { margin-top: 9px; font-size: 11px; line-height: 1.5; color: var(--text-secondary); }
    .load-primary {
      width: 100%; margin-top: 11px; padding: 11px 8px; border: 0; border-radius: 11px;
      background: var(--accent-primary); color: #ffffff; font-family: inherit;
      font-size: 13px; font-weight: 700; cursor: pointer;
    }
    .load-primary:hover { background: var(--accent-hover); }

    /* ----- 최종 결과 ----- */
    .result {
      position: relative; margin-top: 12px; max-width: 600px;
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 16px; box-shadow: var(--card-shadow);
      animation: panelIn 300ms ease-out both;
    }
    .result-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .result-badge {
      display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 6px;
      font-size: 10.5px; font-weight: 700; background: var(--accent-subtle); color: var(--accent-primary);
      border: 1px solid var(--border-default);
    }
    .result-title { margin-top: 8px; font-size: 16px; font-weight: 700; letter-spacing: -0.03em; }
    .result-score { display: flex; align-items: baseline; gap: 5px; margin-top: 4px; flex-wrap: wrap; }
    .result-score strong { font-size: 36px; font-weight: 700; letter-spacing: -0.045em; font-variant-numeric: tabular-nums; }
    .result-score .unit { font-size: 13px; color: var(--text-muted); }
    .result-best { margin-left: auto; font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .result-stars { display: flex; align-items: center; gap: 5px; margin-top: 7px; }
    .result-stars svg, .goal-row svg { width: 16px; height: 16px; }
    .result-stars svg { fill: var(--bg-muted); }
    .result-stars svg.is-on { fill: var(--warn-text); }
    .result-stars svg.is-pop { animation: starPop 380ms cubic-bezier(0.2, 0.9, 0.3, 1.3) both; }
    .result-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: 11px; }
    .result-grid dt { font-size: 10.5px; color: var(--text-muted); white-space: nowrap; }
    .result-grid dd { font-size: 14px; font-weight: 700; font-variant-numeric: tabular-nums; }
    .result-hint { margin-top: 10px; font-size: 11.5px; line-height: 1.5; color: var(--text-secondary); }
    .result-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-top: 11px; }
    .load-ghost {
      padding: 11px 8px; border: 1px solid var(--border-default); border-radius: 11px;
      background: var(--bg-page); color: var(--text-primary); font-family: inherit;
      font-size: 12.5px; font-weight: 600; cursor: pointer;
    }
    .load-ghost:hover { background: var(--bg-subtle); }

    /* ----- 연습 스테이지 ----- */
    .practice { margin-top: 14px; max-width: 600px; }
    .practice-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
    .practice-head h3 { font-size: 13px; font-weight: 700; letter-spacing: -0.02em; }
    .practice-head span { font-size: 10.5px; color: var(--text-muted); }
    .practice-list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
    .stage {
      display: flex; flex-direction: column; gap: 2px; min-width: 0;
      padding: 9px 10px; border: 1px solid var(--border-default); border-radius: 11px;
      background: var(--bg-surface); font-family: inherit; text-align: left; cursor: pointer;
      transition: border-color 160ms ease, background-color 160ms ease;
    }
    .stage:hover { border-color: var(--border-strong); }
    .stage.is-current { border-color: var(--accent-primary); background: var(--accent-subtle); }
    .stage-level { font-size: 9px; font-weight: 700; color: var(--text-muted); }
    .stage-title { font-size: 11.5px; font-weight: 700; letter-spacing: -0.02em; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .stage-best { font-size: 9.5px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .stage.is-current .stage-best { color: var(--accent-primary); font-weight: 600; }

    .bonus-pop {
      position: absolute; left: 50%; top: -4px; transform: translateX(-50%);
      font-size: 20px; font-weight: 700; color: var(--ok-text); font-variant-numeric: tabular-nums;
      pointer-events: none; opacity: 0;
    }
    .bonus-pop.is-on { animation: bonusPop 900ms ease-out both; }
    .result-burst { position: relative; width: 0; height: 0; }
    .result-burst span {
      position: absolute; left: 0; top: 0; width: 4px; height: 4px; border-radius: 50%;
      background: var(--warn-text); opacity: 0;
    }
    .result.is-new .result-burst span { animation: burst 620ms ease-out both; }
    .result.is-new .result-burst span:nth-child(2) { animation-delay: 40ms; }
    .result.is-new .result-burst span:nth-child(3) { animation-delay: 80ms; }
    .result.is-new .result-burst span:nth-child(4) { animation-delay: 120ms; }
    .result.is-new .result-burst span:nth-child(5) { animation-delay: 60ms; }
    .result.is-new .result-burst span:nth-child(6) { animation-delay: 100ms; }

    @keyframes crateDrop {
      0% { opacity: 0; transform: translateY(-26px) scale(1.08) rotate(-3deg); }
      60% { opacity: 1; transform: translateY(2px) scale(0.98) rotate(0deg); }
      100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes crateFall {
      0% { opacity: 1; transform: translateY(0) rotate(0deg); }
      100% { opacity: 0; transform: translateY(46px) rotate(-18deg); }
    }
    @keyframes cartBounce {
      0% { transform: translateY(0); }
      35% { transform: translateY(3px); }
      70% { transform: translateY(-1px); }
      100% { transform: translateY(0); }
    }
    @keyframes cartShake {
      0%, 100% { transform: translateX(0) rotate(0deg); }
      15% { transform: translateX(-5px) rotate(-1.6deg); }
      32% { transform: translateX(5px) rotate(1.6deg); }
      48% { transform: translateX(-4px) rotate(-1.2deg); }
      66% { transform: translateX(3px) rotate(0.8deg); }
      84% { transform: translateX(-2px) rotate(-0.4deg); }
    }
    @keyframes valuePulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.45; }
    }
    @keyframes panelIn {
      0% { opacity: 0; transform: translateY(8px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes starPop {
      0% { transform: scale(0.5); opacity: 0.4; }
      70% { transform: scale(1.18); opacity: 1; }
      100% { transform: scale(1); opacity: 1; }
    }
    @keyframes bonusPop {
      0% { opacity: 0; transform: translate(-50%, 6px) scale(0.9); }
      25% { opacity: 1; transform: translate(-50%, -6px) scale(1.06); }
      70% { opacity: 1; transform: translate(-50%, -18px) scale(1); }
      100% { opacity: 0; transform: translate(-50%, -32px) scale(0.98); }
    }
    @keyframes burst {
      0% { opacity: 0; transform: translate(0, 0) scale(0.6); }
      30% { opacity: 1; }
      100% { opacity: 0; transform: translate(var(--bx, 18px), var(--by, -14px)) scale(1); }
    }

    @media (max-width: 900px) {
      .load-shell { grid-template-columns: 290px minmax(0, 1fr); }
    }

    @media (max-width: 860px) {
      .load-wrap { padding: 14px 14px 72px; }
      .load-shell { display: flex; flex-direction: column; gap: 10px; align-items: stretch; }
      .load-rail, .load-main { display: contents; }
      .load-main-head { order: 1; }
      #statusCard { order: 2; }
      .cart-card { order: 3; }
      .box-card { order: 4; }
      #tripPanel, #resultBox { order: 5; }
      #guideCard { order: 6; }
      #goalCard { order: 7; }
      #recordCard { order: 8; }
      #practiceWrap { order: 9; }
      .load-card, .cart-card, .box-card, .trip-panel, .result, .practice { max-width: none; }
      .cart-card { padding: 10px 12px 11px; }
      .crate-stack { height: 74px; }
      .load-hero { margin-bottom: 10px; }
      .load-hero h1 { font-size: 20px; }
      .load-hero p { font-size: 11.5px; line-height: 1.45; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
      .box-note { display: none; }
      .gauge-legend { display: none; }
      .gauge-head, .tilt-head { font-size: 10px; }
      .cart-meters { gap: 10px; margin-top: 8px; }
      .load-status { margin-top: 7px; }
      .load-card-head { margin-bottom: 7px; }
      .load-main-head { margin-bottom: 5px; }
      .box-card { padding: 11px 12px; }
      .box-icon { width: 38px; height: 38px; }
      .box-body { margin-top: 7px; }
    }

    @media (max-width: 640px) {
      .load-hero p { display: none; }
      .load-hero { margin-bottom: 8px; }
      .load-pill { margin-bottom: 6px; padding: 2px 7px; }
      .load-hero h1 { font-size: 19px; }
      #statusCard .load-card-head { display: none; }
      .load-status { display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
      .load-main-head { margin-bottom: 5px; }
      .load-main-title { font-size: 13px; }
      .cart-stage { padding: 4px 0 1px; }
      .cart-deck { padding: 6px 8px 4px; }
      .crate-stack { height: 58px; }
      .cart-head { font-size: 10px; }
      .load-meter strong { font-size: 15px; }
      .next-strip { margin-top: 7px; padding: 5px 8px; }
      .load-wrap { padding-top: 10px; }
      .load-card { padding: 11px 12px; }
      .load-meter { margin-top: 8px; }
      .streak-row { margin-top: 6px; }
      .load-status { margin-top: 6px; }
      .cart-meters { margin-top: 6px; }
      .crate-stack { height: 54px; }
      .box-card { padding: 10px 11px; }
      .box-body { margin-top: 5px; }
      .next-strip { margin-top: 6px; }
      .box-actions { margin-top: 8px; }
      .ship-btn { margin-top: 6px; padding: 11px 8px; }
      .practice-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .box-name { font-size: 14px; }
    }

    @media (max-width: 380px) {
      .load-wrap { padding: 12px 10px 72px; }
      .load-card { padding: 11px 11px; }
      .side-btn { font-size: 11.5px; padding: 10px 4px; }
      .side-btn .risk-tag { font-size: 8px; padding: 1px 3px; }
      .trip-grid dd, .result-grid dd { font-size: 12.5px; }
    }

    @media (prefers-reduced-motion: reduce) {
      .gl-box { animation: none !important; opacity: 1 !important; transform: none !important; }
      .gl-fill { animation: none !important; width: 72% !important; background: var(--warn-text) !important; }
      .gl-kg { animation: none !important; opacity: 1 !important; }
      .gl-ship { animation: none !important; opacity: 1 !important; transform: none !important; }
      .gl-bonus { animation: none !important; opacity: 1 !important; transform: none !important; }
      .gc-1 { animation: none !important; opacity: 0 !important; }
      .gc-2 { animation: none !important; opacity: 0 !important; }
      .gc-3 { animation: none !important; opacity: 1 !important; }
      .crate.is-new, .crate.is-fallen { animation: none !important; }
      .cart-rig.is-bounce, .cart-rig.is-shake { animation: none !important; }
      .result.is-new .result-burst span { animation: none !important; }
      .result-stars svg.is-pop { animation: none !important; }
      .bonus-pop.is-on { animation: none !important; }
      .trip-panel, .result { animation: none !important; }
      .gauge-head b.is-danger { animation: none !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 한 번 더 싣기</title>
  <meta name="description" content="손수레 한도 100kg, 좌우 균형 28kg. 표기 무게만 보고 상자를 더 실을지 지금 배송할지 고르는 푸시 유어 럭 게임. 매일 KST 날짜로 같은 상자 순서가 열리고, 하루 5회차 점수와 최고 연속 배송을 겨룹니다.">
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
      </div>
      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>매일 KST 00:00 새 상자 순서</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="화면 테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
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
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기" aria-label="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <main class="load-wrap">
    <div class="load-hero">
      <span class="load-pill">일일 챌린지 · 하루 5회차</span>
      <h1>한 번 더 싣기</h1>
      <p>상자에는 표기 무게만 적혀 있습니다. 한도 100kg과 좌우 균형 28kg을 넘지 않게 실으면서, 더 실을지 지금 배송할지 고르세요. 넘치면 그 회차 점수가 사라집니다.</p>
    </div>

    <div class="load-shell">
      <aside class="load-rail" aria-label="게임 진행">
        <section class="load-card" id="statusCard">
          <div class="load-card-head">
            <h2>진행</h2>
            <span id="modeNote">오늘의 배송</span>
          </div>
          <div class="load-seg" role="group" aria-label="게임 모드">
            <button type="button" class="load-seg-btn is-active" id="modeDaily" data-mode="daily" aria-pressed="true">오늘의 챌린지</button>
            <button type="button" class="load-seg-btn" id="modePractice" data-mode="practice" aria-pressed="false">자유 연습</button>
          </div>
          <div class="load-meter">
            <span>회차 <strong id="tripValue">1</strong> / <span id="tripTotal">5</span></span>
            <span>누적 <strong id="totalValue">0</strong>점</span>
          </div>
          <div class="streak-row">
            <span class="streak-chip" id="streakChip">연속 0회 · ×1.0</span>
            <span class="streak-best" id="streakBest">최고 0회</span>
          </div>
          <p class="load-status" id="loadStatus" role="status" aria-live="polite">손수레가 도착했습니다. 표기 무게를 보고 첫 상자를 실어 보세요.</p>
        </section>

        <section class="load-card guide" id="guideCard" aria-labelledby="guideTitle">
          <div class="guide-head">
            <h2 id="guideTitle">게임 방법</h2>
            <button type="button" class="guide-toggle" id="guideToggle" aria-expanded="true" aria-controls="guideBody">접기</button>
          </div>
          <div class="guide-body" id="guideBody">
            <div class="gl-stage" aria-hidden="true">
              <span class="gl-cart">
                <span class="gl-stack"><span class="gl-crate">12</span></span>
                <span class="gl-box">18</span>
                <span class="gl-bed"></span>
                <span class="gl-wheels"><span></span><span></span></span>
              </span>
              <span class="gl-meter">
                <span class="gl-meter-track"><span class="gl-fill"></span></span>
                <span class="gl-meter-marks"><span>0</span><span>70</span><span>100kg</span></span>
                <span class="gl-kg">62kg 싣는 중</span>
              </span>
            </div>
            <div class="gl-chips" aria-hidden="true">
              <span class="gl-ship">지금 배송</span>
              <span class="gl-bonus">+38점</span>
              <span class="gl-balance">균형 <b>×1.25</b></span>
            </div>
            <div class="guide-caption" aria-hidden="true">
              <span class="gc-step gc-1"><span class="gc-num">1</span>상자를 왼쪽·오른쪽에 싣기</span>
              <span class="gc-step gc-2"><span class="gc-num">2</span>무게·균형 게이지가 차오름</span>
              <span class="gc-step gc-3"><span class="gc-num">3</span>지금 배송하면 점수 확정</span>
            </div>
            <p class="guide-note">표기 무게는 어림값입니다. 실측이 한도(100kg)나 균형(28kg)을 넘으면 그 회차는 0점. 다음 상자 표기를 보고 미리 판단하세요.</p>
          </div>
        </section>

        <section class="load-card" id="goalCard">
          <div class="load-card-head">
            <h2>목표</h2>
            <span id="goalNote">별 3단계</span>
          </div>
          <ul class="goal-list" id="goalList"></ul>
          <div class="goal-bar"><span id="goalFill"></span></div>
          <p class="load-foot" id="goalHint">균형이 좋을수록 배율이 오르고, 연속 배송이 쌓이면 더 커집니다.</p>
        </section>

        <section class="load-card" id="recordCard">
          <div class="load-card-head">
            <h2>기록</h2>
            <span id="recordDate">—</span>
          </div>
          <dl class="record-grid">
            <div><dt>오늘 최고</dt><dd id="recBest">—</dd></div>
            <div><dt>완주</dt><dd id="recPlays">0판</dd></div>
            <div><dt>최고 연속</dt><dd id="recStreak">0회</dd></div>
          </dl>
          <ul class="record-history" id="recHistory"></ul>
          <p class="load-foot">기록은 이 브라우저(localStorage)에만 저장됩니다. 서버로 보내지 않습니다.</p>
        </section>
      </aside>

      <section class="load-main" aria-label="손수레 적재">
        <div class="load-main-head">
          <h2 class="load-main-title" id="boardTitle">오늘의 배송</h2>
          <span class="load-main-sub" id="boardSub"></span>
          <button type="button" class="load-reset" id="resetBtn">처음부터</button>
        </div>
        <p class="day-badge" id="dayBadge" hidden>새 날짜 판이 열렸습니다 · 지금 판은 시작한 날 기록으로 마칩니다</p>

        <div class="cart-card" id="cartCard">
          <div class="cart-head">
            <span>손수레 적재량</span>
            <span class="cart-cap" id="cartCap"><b id="cartTotal">0</b> / 100kg</span>
          </div>
          <div class="cart-stage">
            <div class="cart-rig" id="cartRig">
              <div class="cart-deck">
                <div class="deck-col">
                  <span class="deck-head" id="headLeft"><span>왼쪽</span><span><b id="leftValue">0</b>kg</span></span>
                  <div class="crate-stack" id="stackLeft" aria-label="왼쪽 적재"></div>
                </div>
                <div class="deck-col">
                  <span class="deck-head" id="headRight"><span>오른쪽</span><span><b id="rightValue">0</b>kg</span></span>
                  <div class="crate-stack" id="stackRight" aria-label="오른쪽 적재"></div>
                </div>
                <p class="deck-empty" id="deckEmpty">상자를 실으면 여기에 쌓입니다</p>
              </div>
              <div class="cart-bed"></div>
              <div class="cart-frame"><span></span><span></span></div>
            </div>
          </div>
          <div class="cart-meters">
            <div class="gauge">
              <div class="gauge-head"><span>무게</span><b id="gaugeValue" class="is-safe">안전</b></div>
              <div class="gauge-track"><span class="gauge-fill" id="gaugeFill"></span></div>
              <div class="gauge-legend">
                <span><i class="lg-safe"></i>안전 0-70</span>
                <span><i class="lg-warn"></i>주의 70-90</span>
                <span><i class="lg-danger"></i>위험 90+</span>
              </div>
            </div>
            <div class="tilt">
              <div class="tilt-head"><span>좌우 균형</span><b id="tiltValue">균형</b></div>
              <div class="tilt-track">
                <span class="tilt-zone left"></span>
                <span class="tilt-zone right"></span>
                <span class="tilt-fill" id="tiltFill"></span>
              </div>
              <p class="tilt-note" id="tiltNote">허용 28kg</p>
            </div>
          </div>
        </div>

        <section class="box-card" id="boxCard" aria-labelledby="boxName">
          <div class="box-head">
            <span class="box-tag">현재 상자</span>
            <span id="boxCount">1 / 5</span>
          </div>
          <div class="box-body">
            <span class="box-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M3.5 8.2L12 4l8.5 4.2v7.6L12 20l-8.5-4.2z"></path><path d="M3.5 8.2L12 12.4l8.5-4.2M12 12.4V20"></path></svg>
            </span>
            <div class="box-info">
              <div class="box-name" id="boxName">상자를 기다리는 중</div>
              <div class="box-stats">
                <span class="box-stat">표기 <b id="boxKg">0~0</b>kg</span>
                <span class="box-stat score">점수 <b id="boxScore">0</b></span>
              </div>
            </div>
          </div>
          <div class="next-strip" id="nextCard">
            <span class="next-tag">다음 상자</span>
            <span class="next-name" id="nextName">—</span>
            <span class="next-kg" id="nextRange">—</span>
            <span class="next-score" id="nextScore">—</span>
          </div>
          <div class="box-actions">
            <button type="button" class="side-btn" id="loadLeft">왼쪽에 싣기<span class="risk-tag" id="riskLeft">안전</span></button>
            <button type="button" class="side-btn" id="loadRight">오른쪽에 싣기<span class="risk-tag" id="riskRight">안전</span></button>
          </div>
          <button type="button" class="ship-btn" id="shipBtn">지금 배송<span id="shipPreview">+0점</span></button>
          <p class="box-note" id="boxNote">표기 무게는 어림값입니다. 실측은 싣는 순간 정해집니다.</p>
        </section>

        <section class="trip-panel" id="tripPanel" hidden aria-labelledby="tripTitle">
          <span class="trip-badge" id="tripBadge">배송 완료</span>
          <h2 class="trip-title" id="tripTitle">1회차 배송 완료</h2>
          <div class="trip-score"><strong id="tripScore">0</strong><span>점</span><span class="bonus-pop" id="bonusPop">+0</span></div>
          <dl class="trip-grid">
            <div><dt>상자 점수</dt><dd id="tripSum">0</dd></div>
            <div><dt>균형 배율</dt><dd id="tripBal">×1.0</dd></div>
            <div><dt>연속 배율</dt><dd id="tripStreak">×1.0</dd></div>
          </dl>
          <p class="trip-note" id="tripNote"></p>
          <button type="button" class="load-primary" id="nextTripBtn">다음 회차</button>
        </section>

        <section class="result" id="resultBox" hidden aria-labelledby="resultTitle">
          <div class="result-head">
            <span class="result-badge" id="resultBadge">완주</span>
            <span class="result-burst" aria-hidden="true"><span style="--bx:20px;--by:-16px"></span><span style="--bx:14px;--by:14px"></span><span style="--bx:-18px;--by:-12px"></span><span style="--bx:-16px;--by:16px"></span><span style="--bx:26px;--by:2px"></span><span style="--bx:-26px;--by:4px"></span></span>
          </div>
          <h2 class="result-title" id="resultTitle">5회차 배송을 마쳤습니다</h2>
          <div class="result-score">
            <strong id="resultTotal">0</strong><span class="unit">점</span>
            <span class="result-best" id="resultBest">최고 0점</span>
          </div>
          <div class="result-stars" id="resultStars" aria-label="별점"></div>
          <dl class="result-grid">
            <div><dt>배송 성공</dt><dd id="resultDeliveries">0/5</dd></div>
            <div><dt>최고 연속</dt><dd id="resultStreak">0회</dd></div>
            <div><dt id="resultTodayLabel">오늘 최고</dt><dd id="resultToday">0점</dd></div>
          </dl>
          <p class="result-hint" id="resultHint"></p>
          <div class="result-actions">
            <button type="button" class="load-primary" id="retryBtn">다시 하기</button>
            <button type="button" class="load-ghost" id="practiceBtn">연습 모드</button>
          </div>
        </section>

        <section class="practice" id="practiceWrap" hidden aria-label="연습 스테이지">
          <div class="practice-head">
            <h3>연습 스테이지</h3>
            <span id="practiceNote">9판 · 자유 반복</span>
          </div>
          <div class="practice-list" id="practiceList"></div>
        </section>
      </section>
    </div>
  </main>

  <script type="application/json" id="loadData">__DATA_JSON__</script>

  <script>
  (function () {
    'use strict';

    /* ---------------------------------------------------------------- 데이터 */
    var dataEl = document.getElementById('loadData');
    var DATA = {};
    try { DATA = JSON.parse((dataEl && dataEl.textContent) || '{}'); } catch (e) { DATA = {}; }
    var RULES = DATA.rules || {};
    var LIMIT = RULES.limit || 100;
    var TILT = RULES.tilt || 28;
    var TRIPS = RULES.trips || 5;
    var STREAK_STEP = RULES.streakStep || 0.1;
    var STREAK_CAP = RULES.streakCap || 5;
    var TIERS = Array.isArray(RULES.tiers) && RULES.tiers.length ? RULES.tiers
      : [{ min: 0.9, mult: 1.5 }, { min: 0.78, mult: 1.25 }, { min: 0.62, mult: 1 }, { min: 0, mult: 0.75 }];
    var LEVELS = DATA.levels || { daily: '오늘', beginner: '입문', mid: '중급', adv: '고급' };
    var DAILY = Array.isArray(DATA.daily) ? DATA.daily : [];
    var PRACTICE = Array.isArray(DATA.practice) ? DATA.practice : [];
    var FALLBACK = DATA.fallback || null;

    var STORE_KEY = 'load_cart_stats_v1';
    var GUIDE_KEY = 'load_guide_seen_v1';
    var WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];
    var STAR_PATH = 'M12 3.4l2.6 5.4 5.9.8-4.3 4.1 1.1 5.9L12 16.8l-5.3 2.8 1.1-5.9-4.3-4.1 5.9-.8z';
    var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

    /* ---------------------------------------------------------------- DOM */
    var el = {};
    ['modeDaily', 'modePractice', 'modeNote', 'tripValue', 'tripTotal', 'totalValue', 'streakChip', 'streakBest', 'loadStatus',
     'guideCard', 'guideToggle', 'guideBody',
     'goalList', 'goalNote', 'goalFill', 'goalHint',
     'recBest', 'recPlays', 'recStreak', 'recordDate', 'recHistory',
     'boardTitle', 'boardSub', 'resetBtn', 'dayBadge', 'cartCard', 'cartCap', 'cartTotal', 'cartRig',
     'stackLeft', 'stackRight', 'headLeft', 'headRight', 'deckEmpty', 'leftValue', 'rightValue', 'tiltNote',
     'gaugeValue', 'gaugeFill', 'tiltValue', 'tiltFill',
     'boxCard', 'boxCount', 'boxName', 'boxKg', 'boxScore', 'nextCard', 'nextName', 'nextRange', 'nextScore',
     'loadLeft', 'loadRight', 'riskLeft', 'riskRight', 'shipBtn', 'shipPreview', 'boxNote',
     'tripPanel', 'tripBadge', 'tripTitle', 'tripScore', 'bonusPop', 'tripSum', 'tripBal', 'tripStreak', 'tripNote', 'nextTripBtn',
     'resultBox', 'resultBadge', 'resultTitle', 'resultTotal', 'resultBest', 'resultStars',
     'resultDeliveries', 'resultStreak', 'resultToday', 'resultTodayLabel', 'resultHint', 'retryBtn', 'practiceBtn',
     'practiceWrap', 'practiceNote', 'practiceList', 'themeToggle', 'moonIcon', 'sunIcon'
    ].forEach(function (id) { el[id] = document.getElementById(id); });

    /* ---------------------------------------------------------------- 상태 */
    var state = {
      mode: 'daily',
      challenge: null,
      practiceId: null,
      tripIndex: 0,
      boxIndex: 0,
      left: 0,
      right: 0,
      tripScoreSum: 0,
      tripBoxes: 0,
      total: 0,
      streak: 0,
      bestStreak: 0,
      deliveries: 0,
      overloads: 0,
      placed: { left: [], right: [] },
      tripDone: false,
      finished: false,
      store: null,
      dayKey: '',      /* 지금 판이 귀속된 날짜(판 시작일) */
      todayKey: ''     /* 지금 KST 날짜 */
    };

    /* ---------------------------------------------------------------- 유틸 */
    function pad2(n) { return (n < 10 ? '0' : '') + n; }

    function kstKey() {
      var t = new Date(Date.now() + 9 * 3600000);
      return t.getUTCFullYear() + '-' + pad2(t.getUTCMonth() + 1) + '-' + pad2(t.getUTCDate());
    }

    function dayOrdinal(key) {
      var p = String(key).split('-').map(Number);
      return Math.floor(Date.UTC(p[0], p[1] - 1, p[2]) / 86400000);
    }

    function dayLabel(key) {
      var p = String(key).split('-').map(Number);
      var d = new Date(Date.UTC(p[0], p[1] - 1, p[2]));
      return p[1] + '/' + p[2] + ' (' + WEEKDAYS[d.getUTCDay()] + ')';
    }

    function clamp(n, lo, hi) { return Math.max(lo, Math.min(hi, n)); }

    function starsOf(challenge, score) {
      var stars = (challenge && challenge.stars) || [0, 0, 0];
      var count = 0;
      for (var i = 0; i < stars.length; i += 1) if (score >= stars[i]) count += 1;
      return count;
    }

    function balanceInfo() {
      var total = state.left + state.right;
      if (total <= 0) return { ratio: 1, mult: 1 };
      var ratio = 1 - Math.abs(state.left - state.right) / total;
      var mult = TIERS[TIERS.length - 1].mult;
      for (var i = 0; i < TIERS.length; i += 1) {
        if (ratio >= TIERS[i].min) { mult = TIERS[i].mult; break; }
      }
      return { ratio: ratio, mult: mult };
    }

    function streakMult(n) {
      return Math.round((1 + Math.min(n, STREAK_CAP) * STREAK_STEP) * 100) / 100;
    }

    function previewScore() {
      if (!state.tripBoxes) return 0;
      return Math.round(state.tripScoreSum * balanceInfo().mult * streakMult(state.streak));
    }

    function readStore() {
      var raw = null;
      var parsed = null;
      try { raw = localStorage.getItem(STORE_KEY); } catch (e) { raw = null; }
      try { parsed = raw ? JSON.parse(raw) : null; } catch (e) { parsed = null; }
      var store = (parsed && typeof parsed === 'object') ? parsed : {};
      if (!store.days || typeof store.days !== 'object') store.days = {};
      if (!store.best || typeof store.best !== 'object') store.best = {};
      if (!store.totals || typeof store.totals !== 'object') store.totals = { plays: 0, deliveries: 0, overloads: 0 };
      if (!store.streak || typeof store.streak !== 'object') store.streak = { best: 0 };
      return store;
    }

    function writeStore() {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(state.store)); } catch (e) {}
    }

    function setStatus(text) { if (el.loadStatus) el.loadStatus.textContent = text; }

    /* 자정을 넘긴 판에서 띄우는 가벼운 안내 배지 */
    function showDayBadge(on) {
      if (!el.dayBadge) return;
      el.dayBadge.hidden = !on;
    }

    /* 새 일일판을 오늘 날짜로 시작한다. 이전 날짜 판은 이 함수로만 넘어간다. */
    function startDaily() {
      state.todayKey = kstKey();
      state.dayKey = state.todayKey;
      showDayBadge(false);
      loadChallenge(dailyChallenge(), 'daily');
    }

    /* 한 번이라도 실었거나 배송한, 아직 끝나지 않은 일일판인지 */
    function runInProgress() {
      if (state.mode !== 'daily' || state.finished) return false;
      return state.tripBoxes > 0 || state.deliveries > 0 || state.overloads > 0
        || state.tripIndex > 0 || state.tripScoreSum > 0
        || state.placed.left.length > 0 || state.placed.right.length > 0;
    }

    /* ---------------------------------------------------------------- 챌린지 */
    function dailyChallenge() {
      if (!DAILY.length) return FALLBACK;
      var index = dayOrdinal(state.dayKey) % DAILY.length;
      return DAILY[index] || FALLBACK;
    }

    function batch() {
      if (!state.challenge || !Array.isArray(state.challenge.batches)) return [];
      return state.challenge.batches[state.tripIndex] || [];
    }

    function currentBox() { return batch()[state.boxIndex] || null; }
    function nextBox() { return batch()[state.boxIndex + 1] || null; }

    function loadChallenge(challenge, mode, practiceId) {
      if (!challenge) return;
      state.mode = mode;
      state.challenge = challenge;
      state.practiceId = practiceId || null;
      state.tripIndex = 0;
      state.boxIndex = 0;
      state.left = 0;
      state.right = 0;
      state.tripScoreSum = 0;
      state.tripBoxes = 0;
      state.total = 0;
      state.streak = 0;
      state.bestStreak = 0;
      state.deliveries = 0;
      state.overloads = 0;
      state.placed = { left: [], right: [] };
      state.tripDone = false;
      state.finished = false;
      showDayBadge(false);
      el.tripPanel.hidden = true;
      el.resultBox.hidden = true;
      el.boxCard.hidden = false;
      el.resultBox.classList.remove('is-new');
      el.tripPanel.classList.remove('is-fail');
      setModeButtons();
      renderAll();
      setStatus(mode === 'practice'
        ? '연습 스테이지입니다. 기록은 최고 점수로만 남습니다.'
        : '오늘의 상자 순서입니다. 표기 무게를 보고 첫 상자를 실어 보세요.');
    }

    function setModeButtons() {
      var daily = state.mode === 'daily';
      el.modeDaily.classList.toggle('is-active', daily);
      el.modePractice.classList.toggle('is-active', !daily);
      el.modeDaily.setAttribute('aria-pressed', daily ? 'true' : 'false');
      el.modePractice.setAttribute('aria-pressed', daily ? 'false' : 'true');
      el.practiceWrap.hidden = daily;
    }

    function setMode(mode) {
      if (mode === 'practice') {
        var target = null;
        for (var i = 0; i < PRACTICE.length; i += 1) {
          if (PRACTICE[i].id === state.practiceId) target = PRACTICE[i];
        }
        if (!target) target = PRACTICE[0] || FALLBACK;
        state.mode = 'practice';
        state.practiceId = target ? target.id : null;
        loadChallenge(target, 'practice', state.practiceId);
        renderPractice();
        return;
      }
      state.mode = 'daily';
      state.practiceId = null;
      startDaily();
    }

    /* ---------------------------------------------------------------- 위험도 */
    function riskOf(side, box) {
      var kgLo = box.lo;
      var kgHi = box.hi;
      var l = state.left + (side === 'left' ? kgHi : 0);
      var r = state.right + (side === 'right' ? kgHi : 0);
      var worstOver = l + r > LIMIT;
      var worstTilt = Math.abs(l - r) > TILT;
      var l2 = state.left + (side === 'left' ? kgLo : 0);
      var r2 = state.right + (side === 'right' ? kgLo : 0);
      var bestOver = l2 + r2 > LIMIT;
      var bestTilt = Math.abs(l2 - r2) > TILT;
      if (worstOver || worstTilt) {
        if (bestOver || bestTilt) return { level: 'risk', text: '넘침' };
        return { level: 'risk', text: '위험' };
      }
      var total = l + r;
      var tilt = Math.abs(l - r);
      if (total >= LIMIT * 0.85 || tilt >= TILT * 0.8) return { level: 'near', text: '주의' };
      return { level: 'safe', text: '안전' };
    }

    /* ---------------------------------------------------------------- 렌더 */
    function reveal(node) {
      if (!node || node.hidden) return;
      var rect = node.getBoundingClientRect();
      var bar = document.querySelector('.ia-tabbar');
      var limit = bar && getComputedStyle(bar).display !== 'none'
        ? bar.getBoundingClientRect().top : window.innerHeight;
      if (rect.top >= 64 && rect.bottom <= limit - 8) return;
      try { node.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' }); }
      catch (e) { node.scrollIntoView(); }
    }

    function renderAll() {
      renderStatus();
      renderCart();
      renderBox();
      renderGoal();
      renderRecord();
      renderPractice();
    }

    function renderStatus() {
      var challenge = state.challenge;
      el.tripValue.textContent = String(Math.min(state.tripIndex + 1, TRIPS));
      el.tripTotal.textContent = String(TRIPS);
      el.totalValue.textContent = String(state.total);
      var mult = streakMult(state.streak);
      el.streakChip.textContent = '연속 ' + state.streak + '회 · ×' + mult.toFixed(1);
      el.streakChip.classList.toggle('is-hot', mult >= 1.3);
      el.streakBest.textContent = '최고 ' + (state.store ? state.store.streak.best || 0 : 0) + '회';
      el.modeNote.textContent = challenge
        ? (state.mode === 'practice' ? (LEVELS[challenge.level] || '연습') : '오늘의 배송')
        : '오늘의 배송';
      el.boardTitle.textContent = challenge ? challenge.title : '오늘의 배송';
      el.boardSub.textContent = challenge ? ('목표 ' + challenge.goal + '점 · ' + TRIPS + '회차') : '';
    }

    function renderStacks() {
      el.stackLeft.textContent = '';
      el.stackRight.textContent = '';
      function fill(stack, list) {
        list.forEach(function (box) {
          var crate = document.createElement('span');
          crate.className = 'crate' + (box.kg >= 18 ? ' is-heavy' : (box.kg <= 10 ? ' is-light' : ''));
          crate.textContent = String(box.kg);
          crate.setAttribute('title', box.name + ' · ' + box.kg + 'kg');
          stack.appendChild(crate);
        });
      }
      fill(el.stackLeft, state.placed.left);
      fill(el.stackRight, state.placed.right);
    }

    function renderCart() {
      var total = state.left + state.right;
      var ratio = clamp(total / LIMIT, 0, 1);
      el.cartTotal.textContent = String(total);
      el.cartCap.classList.toggle('is-warn', total >= LIMIT * 0.7 && total <= LIMIT * 0.9);
      el.cartCap.classList.toggle('is-danger', total > LIMIT * 0.9);
      el.leftValue.textContent = String(state.left);
      el.rightValue.textContent = String(state.right);
      var tilt = Math.abs(state.left - state.right);
      el.headLeft.classList.toggle('is-heavy', state.left > state.right && state.left > 0);
      el.headRight.classList.toggle('is-heavy', state.right > state.left && state.right > 0);
      el.headLeft.classList.toggle('is-over', state.left - state.right > TILT);
      el.headRight.classList.toggle('is-over', state.right - state.left > TILT);
      el.deckEmpty.hidden = (state.left + state.right) > 0;

      var fill = el.gaugeFill;
      fill.style.width = Math.round(ratio * 100) + '%';
      fill.classList.toggle('is-warn', total >= LIMIT * 0.7 && total <= LIMIT * 0.9);
      fill.classList.toggle('is-danger', total > LIMIT * 0.9);
      var level = total > LIMIT ? 'over' : (total > LIMIT * 0.9 ? 'danger' : (total >= LIMIT * 0.7 ? 'warn' : 'safe'));
      el.gaugeValue.textContent = level === 'over' ? '초과 ' + (total - LIMIT) + 'kg'
        : (level === 'danger' ? '위험' : (level === 'warn' ? '주의' : '안전'));
      el.gaugeValue.className = 'is-' + (level === 'over' ? 'danger' : level);
      el.cartCard.classList.toggle('is-warn', level === 'warn');
      el.cartCard.classList.toggle('is-danger', level === 'danger' || level === 'over');

      var pct = clamp(tilt / TILT, 0, 1);
      var width = Math.round(pct * 50);
      if (state.right >= state.left) {
        el.tiltFill.style.left = '50%';
      } else {
        el.tiltFill.style.left = (50 - width) + '%';
      }
      el.tiltFill.style.width = width + '%';
      el.tiltFill.classList.toggle('is-warn', pct >= 0.6 && pct < 0.85);
      el.tiltFill.classList.toggle('is-danger', pct >= 0.85);
      el.tiltValue.textContent = tilt > TILT ? '넘침' : (pct >= 0.85 ? '위험' : (pct >= 0.6 ? '기움' : '균형'));
      el.tiltNote.textContent = tilt > TILT ? ('허용 초과 ' + (tilt - TILT) + 'kg') : ('차이 ' + tilt + ' / 28kg');
      el.tiltValue.className = pct >= 0.85 ? 'is-danger' : (pct >= 0.6 ? 'is-warn' : '');

      if (total > 0) {
        var deg = clamp(((state.right - state.left) / Math.max(total, 1)) * 14, -5.5, 5.5);
        el.cartRig.style.transform = 'rotate(' + deg.toFixed(2) + 'deg)';
      } else {
        el.cartRig.style.transform = '';
      }
    }

    function riskOn(button, tag, side) {
      var box = currentBox();
      if (!box || state.tripDone || state.finished) {
        tag.textContent = '';
        tag.className = 'risk-tag';
        button.classList.remove('is-risk');
        return;
      }
      var risk = riskOf(side, box);
      tag.textContent = risk.text;
      tag.className = 'risk-tag' + (risk.level === 'safe' ? '' : (risk.level === 'near' ? ' is-near' : ' is-risk'));
      button.classList.toggle('is-risk', risk.level === 'risk');
    }

    function renderBox() {
      var box = currentBox();
      var list = batch();
      var disabled = state.tripDone || state.finished || !box;
      el.loadLeft.disabled = !!disabled;
      el.loadRight.disabled = !!disabled;
      el.shipBtn.disabled = state.tripDone || state.finished || !state.tripBoxes;
      el.boxCount.textContent = list.length
        ? (Math.min(state.boxIndex + 1, list.length) + ' / ' + list.length)
        : '0 / 0';
      if (box) {
        el.boxName.textContent = box.name;
        el.boxKg.textContent = box.lo + '~' + box.hi;
        el.boxScore.textContent = String(box.score);
      } else {
        el.boxName.textContent = list.length ? '회차 상자를 모두 확인했습니다' : '상자를 기다리는 중';
        el.boxKg.textContent = '—';
        el.boxScore.textContent = '—';
      }
      var next = nextBox();
      if (next) {
        el.nextName.textContent = next.name;
        el.nextRange.textContent = next.lo + '~' + next.hi + 'kg';
        el.nextScore.textContent = next.score + '점';
        el.nextCard.hidden = false;
      } else {
        el.nextName.textContent = list.length ? '이번 회차 마지막 상자' : '—';
        el.nextRange.textContent = '';
        el.nextScore.textContent = '';
        el.nextCard.hidden = false;
      }
      el.shipPreview.textContent = state.tripDone ? '회차 종료' : ('+' + previewScore() + '점');
      var info = balanceInfo();
      riskOn(el.loadLeft, el.riskLeft, 'left');
      riskOn(el.loadRight, el.riskRight, 'right');
      if (state.tripDone) {
        el.boxNote.textContent = '이번 회차가 끝났습니다. 아래 결과에서 다음 회차로 넘어가세요.';
      } else if (!box) {
        el.boxNote.textContent = '이번 회차 상자를 모두 실었습니다. 지금 배송하세요.';
      } else {
        var cap = LIMIT - (state.left + state.right);
        el.boxNote.textContent = '남은 무게 ' + cap + 'kg · 균형 여유 ' + (TILT - Math.abs(state.left - state.right)) + 'kg · 균형 배율 ×' + info.mult;
      }
    }

    function starSvg(on, pop) {
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', '0 0 24 24');
      svg.setAttribute('aria-hidden', 'true');
      if (on) svg.setAttribute('class', pop ? 'is-on is-pop' : 'is-on');
      var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', STAR_PATH);
      svg.appendChild(path);
      return svg;
    }

    function renderGoal() {
      var challenge = state.challenge;
      el.goalList.textContent = '';
      if (!challenge) return;
      var stars = challenge.stars || [];
      var labels = ['목표', '한 단계 위', '최고 기록'];
      for (var i = 0; i < stars.length; i += 1) {
        var row = document.createElement('li');
        row.className = 'goal-row' + (state.total >= stars[i] ? ' is-on' : '');
        row.appendChild(starSvg(state.total >= stars[i], false));
        var label = document.createElement('span');
        label.className = 'goal-label';
        label.textContent = labels[i] || ('별 ' + (i + 1));
        row.appendChild(label);
        var value = document.createElement('b');
        value.textContent = String(stars[i]);
        row.appendChild(value);
        el.goalList.appendChild(row);
      }
      var top = stars[stars.length - 1] || 1;
      el.goalFill.style.width = clamp(Math.round((state.total / top) * 100), 0, 100) + '%';
      el.goalNote.textContent = '내 점수 ' + state.total;
    }

    function renderRecord() {
      state.store = state.store || readStore();
      var day = state.store.days[state.todayKey] || null;
      el.recBest.textContent = day && day.best ? day.best + '점' : '—';
      el.recPlays.textContent = (day && day.plays ? day.plays : 0) + '판';
      el.recStreak.textContent = (state.store.streak.best || 0) + '회';
      el.recordDate.textContent = dayLabel(state.todayKey);
      el.recHistory.textContent = '';
      var keys = Object.keys(state.store.days).sort().reverse().slice(0, 3);
      if (!keys.length) {
        var empty = document.createElement('li');
        empty.className = 'is-empty';
        empty.textContent = '아직 완주 기록이 없습니다.';
        el.recHistory.appendChild(empty);
        return;
      }
      keys.forEach(function (key) {
        var row = document.createElement('li');
        var when = document.createElement('span');
        when.textContent = dayLabel(key);
        var value = document.createElement('span');
        value.textContent = (state.store.days[key].best || 0) + '점';
        row.appendChild(when);
        row.appendChild(value);
        el.recHistory.appendChild(row);
      });
    }

    function renderPractice() {
      el.practiceList.textContent = '';
      if (!PRACTICE.length) return;
      el.practiceNote.textContent = PRACTICE.length + '판 · 자유 반복';
      PRACTICE.forEach(function (challenge) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'stage' + (state.practiceId === challenge.id ? ' is-current' : '');
        button.setAttribute('data-pid', challenge.id);
        button.setAttribute('aria-pressed', state.practiceId === challenge.id ? 'true' : 'false');
        var level = document.createElement('span');
        level.className = 'stage-level';
        level.textContent = LEVELS[challenge.level] || '연습';
        var title = document.createElement('span');
        title.className = 'stage-title';
        title.textContent = challenge.title;
        var best = document.createElement('span');
        best.className = 'stage-best';
        var record = state.store && state.store.best ? state.store.best[challenge.id] : 0;
        best.textContent = (record ? '최고 ' + record + '점' : '목표 ' + challenge.goal + '점');
        button.appendChild(level);
        button.appendChild(title);
        button.appendChild(best);
        button.addEventListener('click', function () {
          state.mode = 'practice';
          state.practiceId = challenge.id;
          loadChallenge(challenge, 'practice', challenge.id);
          renderPractice();
        });
        el.practiceList.appendChild(button);
      });
    }

    /* ---------------------------------------------------------------- 상자 싣기 */
    function animateCrate(stack, box, fallen) {
      var crate = document.createElement('span');
      crate.className = 'crate' + (box.kg >= 18 ? ' is-heavy' : (box.kg <= 10 ? ' is-light' : ''))
        + (fallen ? ' is-fallen' : ' is-new');
      crate.textContent = String(box.kg);
      crate.setAttribute('title', box.name + ' · 실측 ' + box.kg + 'kg');
      stack.appendChild(crate);
      return crate;
    }

    function bounce() {
      el.cartRig.classList.remove('is-bounce');
      void el.cartRig.offsetWidth;
      el.cartRig.classList.add('is-bounce');
      if (reduceMotion) el.cartRig.classList.remove('is-bounce');
    }

    function shake() {
      el.cartRig.classList.remove('is-shake');
      void el.cartRig.offsetWidth;
      el.cartRig.classList.add('is-shake');
    }

    function loadSide(side) {
      if (state.tripDone || state.finished) return;
      var box = currentBox();
      if (!box) return;
      var kg = box.kg;
      state.left += side === 'left' ? kg : 0;
      state.right += side === 'right' ? kg : 0;
      state.tripScoreSum += box.score;
      state.tripBoxes += 1;
      state.boxIndex += 1;
      state.placed[side].push(box);

      var total = state.left + state.right;
      var failure = '';
      if (total > LIMIT) failure = 'over';
      else if (Math.abs(state.left - state.right) > TILT) failure = 'tilt';

      if (failure) {
        animateCrate(side === 'left' ? el.stackLeft : el.stackRight, box, true);
        state.overloads += 1;
        state.streak = 0;
        state.tripDone = true;
        renderCart();
        shake();
        showTrip(false, failure, box);
        renderStatus();
        renderBox();
        reveal(el.tripPanel);
        return;
      }

      animateCrate(side === 'left' ? el.stackLeft : el.stackRight, box, false);
      bounce();
      if (total > LIMIT * 0.9) shake();
      renderCart();
      renderStatus();
      renderBox();
      var cap = LIMIT - total;
      var via = side === 'left' ? '왼쪽' : '오른쪽';
      if (state.boxIndex >= batch().length) {
        setStatus(via + '에 ' + box.name + ' ' + kg + 'kg을 실었습니다. 이번 회차 마지막 상자입니다. 지금 배송하세요.');
      } else if (cap <= 12) {
        setStatus(via + '에 ' + box.name + ' ' + kg + 'kg을 실었습니다. 남은 무게 ' + cap + 'kg, 다음 상자는 넘칠 수 있습니다.');
      } else {
        setStatus(via + '에 ' + box.name + ' ' + kg + 'kg(실측)을 실었습니다. 남은 무게 ' + cap + 'kg.');
      }
    }

    /* ---------------------------------------------------------------- 배송 */
    function ship() {
      if (state.tripDone || state.finished || !state.tripBoxes) return;
      var info = balanceInfo();
      var mult = streakMult(state.streak);
      var gained = Math.round(state.tripScoreSum * info.mult * mult);
      state.total += gained;
      state.streak += 1;
      state.bestStreak = Math.max(state.bestStreak, state.streak);
      state.deliveries += 1;
      state.tripDone = true;
      showTrip(true, '', null, {
        gained: gained,
        sum: state.tripScoreSum,
        bal: info.mult,
        ratio: info.ratio,
        streak: mult
      });
      popBonus(gained);
      renderAll();
      setStatus('배송 완료. ' + gained + '점을 받았습니다. 연속 ' + state.streak + '회입니다.');
      reveal(el.tripPanel);
    }

    function countUp(node, target) {
      if (!node) return;
      if (reduceMotion) { node.textContent = String(target); return; }
      var start = performance.now();
      var duration = 520;
      function step(now) {
        var t = Math.min(1, (now - start) / duration);
        var eased = 1 - Math.pow(1 - t, 3);
        node.textContent = String(Math.round(target * eased));
        if (t < 1) window.requestAnimationFrame(step);
        else node.textContent = String(target);
      }
      node.textContent = '0';
      window.requestAnimationFrame(step);
    }

    function popBonus(points) {
      var pop = el.bonusPop;
      pop.textContent = '+' + points;
      pop.classList.remove('is-on');
      void pop.offsetWidth;
      pop.classList.add('is-on');
    }

    function showTrip(ok, reason, box, detail) {
      el.tripPanel.hidden = false;
      el.boxCard.hidden = true;
      el.tripPanel.classList.toggle('is-fail', !ok);
      var last = state.tripIndex >= TRIPS - 1;
      el.tripTitle.textContent = (state.tripIndex + 1) + '회차 ' + (ok ? '배송 완료' : '실패');
      if (ok) {
        el.tripBadge.textContent = '배송 완료';
        el.tripScore.setAttribute('data-value', String(detail.gained));
        countUp(el.tripScore, detail.gained);
        el.tripSum.textContent = String(detail.sum);
        el.tripBal.textContent = '×' + detail.bal.toFixed(2).replace(/0$/, '');
        el.tripStreak.textContent = '×' + detail.streak.toFixed(1);
        var cap = LIMIT - (state.left + state.right);
        var tilt = TILT - Math.abs(state.left - state.right);
        el.tripNote.textContent = '한도까지 ' + cap + 'kg, 균형 여유 ' + tilt + 'kg이 남아 있었습니다. '
          + (detail.bal >= 1.5 ? '좌우가 거의 같아 최고 균형 배율을 받았습니다.' : '균형을 더 맞췄다면 배율이 올라갑니다.');
      } else {
        el.tripBadge.textContent = reason === 'over' ? '과적' : '전복';
        el.tripScore.textContent = '0';
        el.tripScore.setAttribute('data-value', '0');
        el.tripSum.textContent = String(state.tripScoreSum);
        el.tripBal.textContent = '×0';
        el.tripStreak.textContent = '×0';
        var over = (state.left + state.right) - LIMIT;
        var tiltOver = Math.abs(state.left - state.right) - TILT;
        el.tripNote.textContent = reason === 'over'
          ? (box.name + ' 실측 ' + box.kg + 'kg을 실어 한도를 ' + over + 'kg 넘겼습니다. 이번 회차 점수와 연속 보너스가 사라졌습니다. 다음에는 표기 상한을 보고 배송하세요.')
          : (box.name + '을 실어 좌우 차가 ' + tiltOver + 'kg 넘었습니다. 한쪽으로 쏠리면 손수레가 전복됩니다. 무거운 상자는 가벼운 쪽에 실으세요.');
      }
      el.nextTripBtn.textContent = last ? '결과 보기' : '다음 회차';
    }

    function nextTrip() {
      el.tripPanel.hidden = true;
      el.boxCard.hidden = false;
      if (state.tripIndex >= TRIPS - 1) { finish(); return; }
      state.tripIndex += 1;
      state.boxIndex = 0;
      state.left = 0;
      state.right = 0;
      state.tripScoreSum = 0;
      state.tripBoxes = 0;
      state.placed = { left: [], right: [] };
      state.tripDone = false;
      renderStacks();
      renderAll();
      setStatus((state.tripIndex + 1) + '회차 손수레가 도착했습니다. 표기 무게를 확인하세요.');
      reveal(el.boxCard);
    }

    function finish() {
      state.finished = true;
      var challenge = state.challenge;
      var stars = starsOf(challenge, state.total);
      var isDaily = state.mode === 'daily';
      var record = state.store.best[challenge.id] || 0;
      var personalBest = state.total > record;
      if (personalBest) state.store.best[challenge.id] = state.total;
      var day = null;
      /* 연습판은 스테이지 최고 기록만 남긴다(연습 점수가 오늘의 최고점·완주·연속에 섞이지 않게).
         날짜별 통계는 시작일 기준 일일판에서만 쌓는다. */
      if (isDaily) {
        day = state.store.days[state.dayKey] || { best: 0, plays: 0, streak: 0, stars: 0, last: 0 };
        day.plays = (day.plays || 0) + 1;
        day.last = state.total;
        day.stars = Math.max(day.stars || 0, stars);
        day.best = Math.max(day.best || 0, state.total);
        day.streak = Math.max(day.streak || 0, state.bestStreak);
        state.store.days[state.dayKey] = day;
        state.store.totals.plays = (state.store.totals.plays || 0) + 1;
        state.store.totals.deliveries = (state.store.totals.deliveries || 0) + state.deliveries;
        state.store.totals.overloads = (state.store.totals.overloads || 0) + state.overloads;
        state.store.streak.best = Math.max(state.store.streak.best || 0, state.bestStreak);
      }
      writeStore();

      el.resultBox.hidden = false;
      el.boxCard.hidden = true;
      el.resultBox.classList.toggle('is-new', personalBest || (isDaily && !!day && state.total >= day.best));
      el.resultBadge.textContent = isDaily ? '완주' : '연습 완료';
      el.resultTitle.textContent = (personalBest ? '신기록입니다. ' : '') + TRIPS + '회차 배송을 마쳤습니다';
      el.resultTotal.setAttribute('data-value', String(state.total));
      countUp(el.resultTotal, state.total);
      el.resultBest.textContent = '최고 ' + Math.max(record, state.total) + '점';
      el.resultStars.textContent = '';
      for (var i = 0; i < 3; i += 1) el.resultStars.appendChild(starSvg(i < stars, i < stars));
      el.resultDeliveries.textContent = state.deliveries + '/' + TRIPS;
      el.resultStreak.textContent = state.bestStreak + '회';
      if (el.resultTodayLabel) {
        el.resultTodayLabel.textContent = isDaily
          ? (state.dayKey === state.todayKey ? '오늘 최고' : dayLabel(state.dayKey) + ' 최고')
          : '스테이지 최고';
      }
      el.resultToday.textContent = isDaily ? ((day && day.best) || 0) + '점' : Math.max(record, state.total) + '점';
      var top = challenge.stars[challenge.stars.length - 1] || 1;
      if (stars >= 3) {
        el.resultHint.textContent = '최고 별점입니다. 같은 상자 순서로 다른 선택을 시험해 더 높은 점수에 도전해 보세요.';
      } else if (state.overloads > 0) {
        el.resultHint.textContent = '과적 ' + state.overloads + '회로 회차 점수를 잃었습니다. 표기 상한까지 남은 무게를 계산해 보세요.';
      } else {
        el.resultHint.textContent = '최고 별점까지 ' + (top - state.total > 0 ? top - state.total : 0) + '점 남았습니다. 무게를 더 실을지 판단해 보세요.';
      }
      renderAll();
      setStatus('완주했습니다. 총 ' + state.total + '점 · 별 ' + stars + '개.');
      reveal(el.resultBox);
    }

    /* ---------------------------------------------------------------- 가이드·테마 */
    function setGuide(open) {
      el.guideBody.hidden = !open;
      el.guideToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      el.guideToggle.textContent = open ? '접기' : '게임 방법';
      if (!open) {
        try { localStorage.setItem(GUIDE_KEY, '1'); } catch (e) {}
      }
    }

    function initGuide() {
      var seen = null;
      try { seen = localStorage.getItem(GUIDE_KEY); } catch (e) { seen = null; }
      setGuide(!seen);
    }

    function initTheme() {
      var dark = document.documentElement.getAttribute('data-theme') === 'dark';
      if (el.sunIcon) el.sunIcon.style.display = dark ? 'block' : 'none';
      if (el.moonIcon) el.moonIcon.style.display = dark ? 'none' : 'block';
    }

    /* ---------------------------------------------------------------- 초기화 */
    state.todayKey = kstKey();
    state.store = readStore();
    initTheme();
    initGuide();
    startDaily();

    el.modeDaily.addEventListener('click', function () { setMode('daily'); });
    el.modePractice.addEventListener('click', function () { setMode('practice'); });
    el.loadLeft.addEventListener('click', function () { loadSide('left'); });
    el.loadRight.addEventListener('click', function () { loadSide('right'); });
    el.shipBtn.addEventListener('click', ship);
    el.nextTripBtn.addEventListener('click', nextTrip);
    el.retryBtn.addEventListener('click', function () {
      if (state.mode === 'practice') loadChallenge(state.challenge, 'practice', state.practiceId);
      else startDaily();
    });
    el.practiceBtn.addEventListener('click', function () { setMode('practice'); });
    el.resetBtn.addEventListener('click', function () {
      if (state.mode === 'practice') loadChallenge(state.challenge, 'practice', state.practiceId);
      else startDaily();
      setStatus('이번 판을 처음부터 다시 시작합니다. 기록은 그대로입니다.');
    });
    el.guideToggle.addEventListener('click', function () {
      setGuide(el.guideBody.hidden);
    });
    el.themeToggle.addEventListener('click', function () {
      var root = document.documentElement;
      var dark = root.getAttribute('data-theme') === 'dark';
      if (dark) root.removeAttribute('data-theme');
      else root.setAttribute('data-theme', 'dark');
      try { localStorage.setItem('secjobs-theme', dark ? 'light' : 'dark'); } catch (e) {}
      initTheme();
    });

    /* 자정이 지나면 새 상자 순서가 열린다(탭을 열어 둔 경우 포함).
       단, 이미 시작한 일일판은 시작일에 귀속해 그대로 마칠 수 있게 두고 배지만 띄운다. */
    function checkDay() {
      var key = kstKey();
      if (key === state.todayKey) return;
      state.todayKey = key;
      if (state.mode !== 'daily') {
        renderRecord();
        return;
      }
      if (state.finished || runInProgress()) {
        showDayBadge(true);
        renderRecord();
        setStatus(dayLabel(state.dayKey) + ' 판으로 시작했으니 이 판은 그날 기록으로 마칩니다. 새 날짜 판은 다음 시작(다시 하기 · 처음부터) 때 열립니다.');
        return;
      }
      state.dayKey = key;
      loadChallenge(dailyChallenge(), 'daily');
      showDayBadge(false);
      setStatus('날짜가 바뀌어 오늘의 새 상자 순서가 열렸습니다.');
    }
    window.setInterval(checkDay, 60000);
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) checkDay();
    });
  })();
  </script>
</body>
</html>
"""


def build():
    kst_now = datetime.now(KST)
    data = build_data(kst_now)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    html = HTML_TEMPLATE.replace("__CSS__", CSS).replace("__DATA_JSON__", payload)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with open(LOAD_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(ui_shell.apply(html, "load")))

    index = (kst_now.date() - datetime(1970, 1, 1).date()).days % DAILY_COUNT
    print("-> 'load_data.json' 저장 완료 (일일 %d판 · 연습 %d판 · 폴백 1판)"
          % (len(data["daily"]), len(data["practice"])))
    print("-> 'load.html' 생성 완료 (오늘 %s · %s · 목표 %d점)"
          % (kst_now.date().isoformat(), data["daily"][index]["title"], data["daily"][index]["goal"]))
    return {
        "daily": len(data["daily"]),
        "practice": len(data["practice"]),
        "today": data["daily"][index]["id"],
        "today_title": data["daily"][index]["title"],
        "goal": data["daily"][index]["goal"],
        "optimal": data["daily"][index]["optimal"],
    }


if __name__ == "__main__":
    build()

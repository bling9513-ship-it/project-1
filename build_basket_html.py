#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘의 장바구니 리그(basket.html).

무엇을 하나
  · grocery_data.json(aT KAMIS 서울 소매가격 실측값 8품목)을 그대로 읽어 쓴다. 가격을 만들지 않는다.
  · KST 날짜로 정해지는 오늘의 미션(목표 예산 ± 허용 오차 · 최소 품목 수 · 분류 조건 2가지)에 맞춰
    8품목의 수량(0~3)을 담고 제출하면, 예산 정확도(60점) + 조건 충족(각 20점)으로 점수를 매기고
    S/A/B/C 등급을 낸다.
  · 미션·등급 규칙은 파이썬(build)과 화면 JS가 같은 식으로 계산한다. 날짜만 같으면 두 곳의 결과가 같다
    (tests/test_basket_mission.py 가 두 식을 대조한다).
  · 연속 참여 스트릭·최고 등급 localStorage 저장(`secjobs-basket-v1`), 결과 한 줄 복사,
    제출 뒤에는 오늘 가능한 최고 조합(완전탐색)을 함께 보여 준다.

지키는 것
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 미션·판정 레일 + 품목 그리드 / 모바일(390px) 미션 → 게이지 → 품목 → 제출 순
  · 값은 서울 소매가격 조사값이고, 조사일·규격·등급을 카드에 함께 적는다.
"""
import itertools
import json
import os
from datetime import date, datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "grocery_data.json")
OUT_HTML = os.path.join(BASE_DIR, "basket.html")
KST = timezone(timedelta(hours=9))
EPOCH = date(1970, 1, 1)

MAX_QTY = 3
BUDGETS = [18000, 19000, 20000, 21000, 22000, 23000, 25000]
TOLERANCE = 1000
MIN_ITEMS_CHOICES = [4, 5]
BUDGET_POINTS = 60
CONDITION_POINTS = 20

# 품목 분류 — grocery_data.json 의 id 기준(값이 아니라 분류만 우리가 정한다)
CATEGORY = {
    "egg": "달걀",
    "greenonion": "잎채소",
    "spinach": "잎채소",
    "cabbage": "잎채소",
    "radish": "뿌리채소",
    "onion": "뿌리채소",
    "zucchini": "과채",
    "apple": "과일",
}

CONDITIONS = [
    ("leaf", "잎채소 1가지 이상 담기"),
    ("fruit", "과일 1가지 담기"),
    ("kinds3", "서로 다른 분류 3가지 이상 담기"),
    ("egg", "달걀 담기"),
    ("root", "뿌리채소 1가지 이상 담기"),
]


# ---------------------------------------------------------------------------
# 데이터
# ---------------------------------------------------------------------------
def load_data(path=None):
    with open(path or DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)
    items = data.get("items") or []
    if len(items) != 8:
        raise SystemExit("grocery_data.json 품목이 %d개입니다(8개 필요)." % len(items))
    region = data["regionList"][0]
    for item in items:
        stats = (item.get("byRegion") or {}).get(region["id"])
        if not stats or not stats.get("latest", {}).get("price"):
            raise SystemExit("%s/%s 수집값이 없습니다" % (item.get("name"), region["id"]))
        if item["id"] not in CATEGORY:
            raise SystemExit("%s 분류가 정의되지 않았습니다" % item.get("name"))
    return data


def price_of(data, item_id, region_id=None):
    region_id = region_id or data["regionList"][0]["id"]
    for item in data["items"]:
        if item["id"] == item_id:
            return item["byRegion"][region_id]["latest"]["price"]
    raise KeyError(item_id)


# ---------------------------------------------------------------------------
# 오늘의 미션 (날짜만으로 결정 — 화면 JS 와 같은 식)
# ---------------------------------------------------------------------------
def seed_for(day):
    return (day - EPOCH).days


def mission_for(day):
    seed = seed_for(day)
    budget = BUDGETS[seed % len(BUDGETS)]
    min_items = MIN_ITEMS_CHOICES[(seed // len(BUDGETS)) % len(MIN_ITEMS_CHOICES)]
    first = CONDITIONS[seed % len(CONDITIONS)]
    second_pool = [c for c in CONDITIONS if c[0] != first[0]]
    second = second_pool[(seed // len(CONDITIONS)) % len(second_pool)]
    return {
        "date": day.isoformat(),
        "seed": seed,
        "budget": budget,
        "tolerance": TOLERANCE,
        "minItems": min_items,
        "conditions": [
            {"id": first[0], "label": first[1]},
            {"id": second[0], "label": second[1]},
        ],
    }


def condition_met(condition_id, picks, items_by_id):
    """picks: {item_id: qty}. 분류 조건을 계산한다."""
    chosen = [items_by_id[item_id] for item_id, qty in picks.items() if qty > 0]
    if condition_id == "leaf":
        return any(CATEGORY[item["id"]] == "잎채소" for item in chosen)
    if condition_id == "fruit":
        return any(CATEGORY[item["id"]] == "과일" for item in chosen)
    if condition_id == "egg":
        return any(item["id"] == "egg" for item in chosen)
    if condition_id == "root":
        return any(CATEGORY[item["id"]] == "뿌리채소" for item in chosen)
    if condition_id == "kinds3":
        return len({CATEGORY[item["id"]] for item in chosen}) >= 3
    raise KeyError(condition_id)


def budget_points(diff, tolerance):
    if diff <= tolerance:
        return BUDGET_POINTS
    if diff <= tolerance * 2:
        return 40
    if diff <= tolerance * 4:
        return 20
    return 0


def grade_for(score):
    if score >= 90:
        return "S"
    if score >= 70:
        return "A"
    if score >= 50:
        return "B"
    return "C"


def evaluate(picks, mission, data):
    """채점 — 예산 정확도 + 조건 충족. 화면 JS 와 같은 규칙."""
    items_by_id = {item["id"]: item for item in data["items"]}
    total = sum(price_of(data, item_id) * qty for item_id, qty in picks.items() if qty)
    count = sum(1 for qty in picks.values() if qty > 0)
    diff = abs(total - mission["budget"])
    points = budget_points(diff, mission["tolerance"])
    checks = []
    for condition in mission["conditions"]:
        met = condition_met(condition["id"], picks, items_by_id)
        checks.append({"id": condition["id"], "label": condition["label"], "met": met})
        if met:
            points += CONDITION_POINTS
    count_ok = count >= mission["minItems"]
    if not count_ok:
        points = max(0, points - 20)
    return {
        "total": total,
        "count": count,
        "diff": diff,
        "points": points,
        "grade": grade_for(points),
        "countOk": count_ok,
        "checks": checks,
        "budgetOk": diff <= mission["tolerance"],
    }


def best_combination(mission, data):
    """오늘 미션에서 가능한 최고 조합(완전탐색). 같으면 예산에 더 가까운 쪽."""
    ids = [item["id"] for item in data["items"]]
    prices = {item["id"]: price_of(data, item["id"]) for item in data["items"]}
    best = None
    for combo in itertools.product(range(MAX_QTY + 1), repeat=len(ids)):
        if not any(combo):
            continue
        picks = dict(zip(ids, combo))
        result = evaluate(picks, mission, data)
        key = (result["points"], -result["diff"])
        if best is None or key > best[0]:
            best = (key, result, {k: v for k, v in picks.items() if v})
    if best is None:
        return None
    key, result, picks = best
    return {
        "picks": picks,
        "total": result["total"],
        "grade": result["grade"],
        "points": result["points"],
        "count": result["count"],
    }


def build(out_path=None, today=None):
    data = load_data()
    today = today or datetime.now(KST).date()
    region = data["regionList"][0]
    mission = mission_for(today)
    best = best_combination(mission, data)

    items = []
    for item in data["items"]:
        stats = item["byRegion"][region["id"]]
        items.append({
            "id": item["id"],
            "name": item["name"],
            "unit": item["unit"],
            "grade": item.get("grade") or "",
            "kind": item.get("kind") or "",
            "category": CATEGORY[item["id"]],
            "price": stats["latest"]["price"],
            "date": stats["latest"]["date"],
            "median": stats["median"],
            "gapPct": stats["gapPct"],
            "sourceUrl": stats["sourceUrl"],
            "stale": bool(stats.get("stale") or stats.get("inherited")),
        })

    payload = {
        "generated": data["generated"],
        "window": "%s ~ %s" % (data["window"]["start"], data["window"]["end"]),
        "region": {"id": region["id"], "name": region["name"]},
        "source": data["source"],
        "items": items,
        "mission": mission,
        "best": best,
        "rules": {
            "maxQty": MAX_QTY,
            "budgets": BUDGETS,
            "tolerance": TOLERANCE,
            "minItemsChoices": MIN_ITEMS_CHOICES,
            "budgetPoints": BUDGET_POINTS,
            "conditionPoints": CONDITION_POINTS,
            "conditions": [{"id": cid, "label": label} for cid, label in CONDITIONS],
        },
        "storeKey": "secjobs-basket-v1",
    }

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__GENERATED__", data["generated"])
            .replace("__WINDOW__", payload["window"])
            .replace("__MISSION_DATE__", mission["date"])
            .replace("__BUDGET__", "{:,}".format(mission["budget"]))
            .replace("__TOLERANCE__", "{:,}".format(mission["tolerance"]))
            .replace("__MINITEMS__", str(mission["minItems"]))
            .replace("__CONDITIONS__", "".join(
                '<li>%s</li>' % condition["label"] for condition in mission["conditions"]))
            .replace("__BEST__", best_text(best, items))
            .replace("__DATA_JSON__", safe_json_for_script(json.dumps(payload, ensure_ascii=False,
                                                                      separators=(",", ":"))))
            .replace("__JS__", JS))

    with open(out_path or OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "basket")))

    print("-> 'basket.html' 생성 완료 (%s 미션 · 예산 %s원 · 최고 %s등급 %s원)"
          % (mission["date"], format(mission["budget"], ","), best["grade"], format(best["total"], ",")))
    return {
        "items": len(items),
        "mission": mission,
        "best": best,
    }


def best_text(best, items):
    by_id = {item["id"]: item for item in items}
    parts = []
    for item_id, qty in best["picks"].items():
        name = by_id[item_id]["name"]
        parts.append(name if qty == 1 else "%s %d개" % (name, qty))
    return "%s · %s원 · %s등급 %d점" % (", ".join(parts), format(best["total"], ","), best["grade"], best["points"])


# ---------------------------------------------------------------------------
# 스타일
# ---------------------------------------------------------------------------
CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --bg-page: #f8fafc;  --bg-surface: #ffffff;  --bg-subtle: #f1f5f9;  --bg-muted: #e2e8f0;
      --border-subtle: #f1f5f9;  --border-default: #e2e8f0;  --border-strong: #cbd5e1;
      --text-primary: #0f172a;  --text-secondary: #475569;  --text-muted: #94a3b8;
      --accent-primary: #2563eb;  --accent-subtle: #eff6ff;
      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;  --ok-ink: #0f766e;
      --warn-bg: #fffbeb;  --warn-text: #b45309;  --warn-border: #fde68a;
      --miss-bg: #f8fafc;  --miss-text: #94a3b8;  --miss-border: #e2e8f0;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --ok-bg: rgba(16, 185, 129, 0.14);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.34);  --ok-ink: #5eead4;
      --warn-bg: rgba(245, 158, 11, 0.14);  --warn-text: #fcd34d;  --warn-border: rgba(245, 158, 11, 0.34);
      --miss-bg: #18181b;  --miss-text: #71717a;  --miss-border: #27272a;
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body { font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease; }
    .bk-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .bk-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 96px; }
    .bk-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .bk-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 640px; word-break: keep-all; }
    .bk-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .bk-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px;
      font-size: 11.5px; color: var(--text-muted); }
    .bk-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }

    .bk-main { display: grid; grid-template-columns: 330px minmax(0, 1fr); gap: 16px; margin-top: 16px; align-items: start; }
    .bk-main > * { min-width: 0; }
    .bk-panel { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 18px; box-shadow: var(--card-shadow); }
    .bk-panel h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); }

    .bk-rail { display: grid; gap: 12px; position: sticky; top: 76px; }
    .bk-mission-list { margin: 10px 0 0; display: grid; gap: 7px; }
    .bk-mission-row { display: flex; align-items: baseline; justify-content: space-between; gap: 10px;
      padding-bottom: 7px; border-bottom: 1px solid var(--border-subtle); }
    .bk-mission-row:last-child { border-bottom: 0; padding-bottom: 0; }
    .bk-mission-row span { font-size: 11px; color: var(--text-muted); }
    .bk-mission-row b { font-size: 14px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .bk-mission-conds { margin: 10px 0 0; padding-left: 0; list-style: none; display: grid; gap: 6px; }
    .bk-mission-conds li { position: relative; padding-left: 16px; font-size: 11.5px; font-weight: 600;
      color: var(--text-secondary); word-break: keep-all; }
    .bk-mission-conds li::before { content: ""; position: absolute; left: 2px; top: 6px; width: 6px; height: 6px;
      border-radius: 50%; background: var(--text-muted); }

    .bk-gauge-card { margin-top: 12px; }
    .bk-gauge-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
    .bk-total { font-size: 27px; font-weight: 800; letter-spacing: -0.04em; font-variant-numeric: tabular-nums; }
    .bk-total small { font-size: 12px; font-weight: 700; color: var(--text-muted); margin-left: 3px; }
    .bk-diff { font-size: 12px; font-weight: 800; font-variant-numeric: tabular-nums; }
    .bk-diff.is-ok { color: var(--ok-ink); }
    .bk-diff.is-over { color: var(--warn-text); }
    .bk-diff.is-under { color: var(--accent-primary); }
    .bk-gauge { position: relative; height: 14px; margin-top: 11px; border-radius: 999px; overflow: hidden;
      background: var(--bg-subtle); border: 1px solid var(--border-default); }
    .bk-band { position: absolute; top: -2px; bottom: -2px; border-left: 1px dashed var(--ok-ink);
      border-right: 1px dashed var(--ok-ink); background: transparent; opacity: .75; }
    .bk-fill { position: absolute; left: 0; top: 0; bottom: 0; background: var(--text-primary); opacity: .82;
      border-radius: 999px; transition: width .25s cubic-bezier(0.2, 0.8, 0.2, 1); }
    .bk-gauge-legend { display: flex; justify-content: space-between; margin-top: 5px; font-size: 10px; color: var(--text-muted); }
    .bk-count-line { display: flex; align-items: center; justify-content: space-between; margin-top: 11px;
      font-size: 11.5px; color: var(--text-secondary); }
    .bk-count-line b { font-size: 13px; font-weight: 800; color: var(--text-primary); }
    .bk-checks { margin-top: 10px; display: grid; gap: 6px; }
    .bk-check { display: flex; align-items: flex-start; gap: 7px; font-size: 11.5px; font-weight: 600;
      color: var(--text-secondary); }
    .bk-check i { flex: 0 0 auto; width: 15px; height: 15px; border-radius: 50%; border: 1.5px solid var(--border-strong);
      display: inline-flex; align-items: center; justify-content: center; margin-top: 1px; }
    .bk-check.is-on { color: var(--text-primary); }
    .bk-check.is-on i { background: var(--ok-ink); border-color: var(--ok-ink); }
    .bk-check.is-on i::after { content: ""; width: 7px; height: 4px; border-left: 1.6px solid #fff;
      border-bottom: 1.6px solid #fff; transform: rotate(-45deg) translate(1px, -1px); }
    .bk-submit { width: 100%; margin-top: 13px; border: 1px solid var(--text-primary); background: var(--text-primary);
      color: var(--bg-surface); border-radius: 12px; padding: 12px; font-family: inherit; font-size: 13.5px;
      font-weight: 800; cursor: pointer; }
    .bk-submit:hover { opacity: .9; }
    .bk-submit:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .bk-submit:disabled { opacity: .45; cursor: default; }
    .bk-ghost { width: 100%; margin-top: 7px; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 12px; padding: 10px; font-family: inherit; font-size: 12px;
      font-weight: 700; cursor: pointer; }
    .bk-ghost:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .bk-status { min-height: 16px; margin-top: 7px; font-size: 11px; font-weight: 600; color: var(--ok-ink); }

    /* ---------- 결과 ---------- */
    .bk-result { margin-top: 12px; border-radius: 14px; padding: 14px; border: 1px solid var(--border-default);
      background: var(--bg-surface); }
    .bk-result.grade-S { border-color: var(--ok-border); background: var(--ok-bg); }
    .bk-result.grade-A { border-color: var(--ok-border); background: var(--bg-subtle); }
    .bk-result.grade-B { border-color: var(--warn-border); background: var(--warn-bg); }
    .bk-result.grade-C { border-color: var(--miss-border); background: var(--miss-bg); }
    .bk-result-top { display: flex; align-items: center; gap: 9px; }
    .bk-grade { width: 42px; height: 42px; border-radius: 12px; display: inline-flex; align-items: center;
      justify-content: center; font-size: 22px; font-weight: 800; background: var(--text-primary); color: var(--bg-surface); }
    .bk-result.grade-S .bk-grade { background: var(--ok-ink); color: #fff; }
    .bk-result.grade-B .bk-grade { background: var(--warn-text); color: #fff; }
    .bk-result.grade-C .bk-grade { background: var(--text-muted); color: #fff; }
    .bk-result-top h3 { font-size: 15.5px; font-weight: 800; letter-spacing: -0.03em; }
    .bk-result-top p { font-size: 11.5px; color: var(--text-secondary); }
    .bk-result-body { margin-top: 10px; display: grid; gap: 4px; font-size: 12px; color: var(--text-secondary); }
    .bk-result-body b { color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .bk-share { margin-top: 10px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px;
      line-height: 1.55; white-space: pre-wrap; color: var(--text-secondary); background: var(--bg-subtle);
      border: 1px solid var(--border-default); border-radius: 10px; padding: 9px 10px; }
    .bk-best { margin-top: 10px; font-size: 11px; color: var(--text-muted); line-height: 1.55; }
    .bk-best b { color: var(--text-primary); }

    /* ---------- 품목 ---------- */
    .bk-shelf-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .bk-shelf-head h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; color: var(--text-primary); }
    .bk-shelf-head span { font-size: 11px; color: var(--text-muted); }
    .bk-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 11px; }
    .bk-item { border: 1px solid var(--border-default); border-radius: 14px; padding: 13px; background: var(--bg-surface);
      display: flex; flex-direction: column; gap: 7px; transition: border-color .15s ease, background-color .15s ease; }
    .bk-item.is-in { border-color: var(--text-primary); background: var(--bg-subtle); }
    .bk-item-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 6px; }
    .bk-item h3 { font-size: 14.5px; font-weight: 800; letter-spacing: -0.03em; }
    .bk-cat { font-size: 10px; font-weight: 700; color: var(--text-muted); border: 1px solid var(--border-default);
      border-radius: 999px; padding: 2px 7px; }
    .bk-price { font-size: 19px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .bk-price small { font-size: 11px; font-weight: 700; color: var(--text-muted); margin-left: 2px; }
    .bk-item-meta { font-size: 10.5px; color: var(--text-muted); }
    .bk-item-foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: auto; }
    .bk-chip { font-size: 10px; font-weight: 700; border-radius: 6px; padding: 2px 6px; background: var(--bg-subtle);
      color: var(--text-muted); }
    .bk-chip.is-low { background: var(--ok-bg); color: var(--ok-text); }
    .bk-chip.is-high { background: var(--warn-bg); color: var(--warn-text); }
    .bk-stepper { display: inline-flex; align-items: center; gap: 2px; border: 1px solid var(--border-default);
      border-radius: 10px; padding: 2px; background: var(--bg-surface); }
    .bk-step { width: 34px; height: 32px; border: 0; background: transparent; color: var(--text-secondary);
      border-radius: 8px; font-family: inherit; font-size: 16px; font-weight: 800; cursor: pointer; }
    .bk-step:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .bk-step:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .bk-step:disabled { opacity: .35; cursor: default; }
    .bk-qty { min-width: 22px; text-align: center; font-size: 13px; font-weight: 800; font-variant-numeric: tabular-nums; }
    .bk-qty.is-zero { color: var(--text-muted); }
    .bk-src { font-size: 10px; color: var(--text-muted); text-decoration: none; border-bottom: 1px solid var(--border-default); }
    .bk-src:hover { color: var(--accent-primary); }

    /* 모바일 전용 하단 미니 바 — 품목을 고르는 동안 합계와 제출을 계속 보여 준다. */
    .bk-mini { display: none; }
    @media (max-width: 900px) {
      .bk-mini {
        display: flex; align-items: center; gap: 10px; position: fixed; left: 10px; right: 10px;
        bottom: calc(var(--ia-tabbar-h, 64px) + 10px); z-index: 40; padding: 8px 8px 8px 13px;
        background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 14px;
        box-shadow: 0 8px 24px -12px rgba(15, 23, 42, 0.4);
      }
      .bk-mini-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; flex: 1 1 auto; }
      .bk-mini-info b { font-size: 16px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
      .bk-mini-info span { font-size: 10.5px; font-weight: 600; color: var(--text-muted); }
      .bk-mini-btn { flex: 0 0 auto; border: 1px solid var(--text-primary); background: var(--text-primary);
        color: var(--bg-surface); border-radius: 10px; padding: 10px 16px; font-family: inherit; font-size: 13px;
        font-weight: 800; cursor: pointer; }
      .bk-mini-btn:disabled { opacity: .45; cursor: default; }
    }

    .bk-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .bk-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; color: var(--text-primary); }
    .bk-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .bk-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .bk-notes li b { color: var(--text-primary); }
    .bk-notes .bk-srcs { list-style: none; padding-left: 0; margin-top: 12px; padding-top: 11px;
      border-top: 1px solid var(--border-subtle); }
    .bk-notes .bk-srcs li { display: flex; flex-direction: column; gap: 1px; }
    .bk-notes .bk-srcs a { font-weight: 700; color: var(--accent-primary); text-decoration: none; font-size: 11.5px; }
    .bk-notes .bk-srcs span { font-size: 10.5px; color: var(--text-muted); }
    .bk-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 900px) {
      .bk-wrap { padding: 14px 13px 150px; }
      .bk-hero h1 { font-size: 21px; }
      .bk-hero p { font-size: 12px; }
      .bk-main { display: flex; flex-direction: column; align-items: stretch; gap: 10px; margin-top: 13px; }
      .bk-rail { position: static; order: 1; }
      .bk-shelf { order: 2; }
      .bk-panel { padding: 14px; }
      .bk-total { font-size: 24px; }
      .bk-mission-row b { font-size: 13px; }
      .bk-mission-conds li { font-size: 11px; }
      .bk-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
      .bk-item { padding: 11px; }
      .bk-price { font-size: 17px; }
      .bk-step { width: 32px; height: 32px; }
      .bk-item-foot { flex-direction: column; align-items: stretch; gap: 6px; }
      .bk-chip { text-align: center; white-space: nowrap; font-size: 9.5px; }
      .bk-stepper { justify-content: space-between; }
      .bk-step { flex: 0 0 34px; width: 34px; height: 34px; }
      .bk-qty { flex: 1 1 auto; }
    }
    @media (max-width: 360px) {
      .bk-grid { grid-template-columns: minmax(0, 1fr); }
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
  <title>Infosec Archive · 오늘의 장바구니 리그</title>
  <meta name="description" content="aT KAMIS 서울 소매가격 8품목으로 오늘의 미션(목표 예산·최소 품목·분류 조건)에 맞는 장바구니를 담아 S/A/B/C 등급을 받는 데일리 게임. 조사일·규격·등급을 함께 표시합니다.">
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

  <main class="bk-wrap">
    <section class="bk-hero">
      <span class="bk-pill">생활 · 장바구니 리그</span>
      <h1>오늘 예산에 딱 맞게 담아라</h1>
      <p>aT KAMIS 서울 소매가격 8품목으로 오늘의 미션을 풉니다. 목표 예산과 허용 오차, 최소 품목 수, 분류 조건을 모두 만족하면 S등급입니다. 값은 조사일·규격과 함께 적혀 있습니다.</p>
      <div class="bk-meta">
        <span>서울 소매가격</span>
        <span class="bk-dot"></span>
        <span>조사 기간 __WINDOW__</span>
        <span class="bk-dot"></span>
        <span>수집 __GENERATED__</span>
      </div>
    </section>

    <div class="bk-main">
      <aside class="bk-rail" aria-label="오늘의 미션과 판정">
        <section class="bk-panel">
          <h2>오늘의 미션 · __MISSION_DATE__</h2>
          <div class="bk-mission-list">
            <div class="bk-mission-row"><span>목표 예산</span><b>__BUDGET__원</b></div>
            <div class="bk-mission-row"><span>허용 오차</span><b>± __TOLERANCE__원</b></div>
            <div class="bk-mission-row"><span>최소 품목</span><b>__MINITEMS__가지</b></div>
          </div>
          <ul class="bk-mission-conds">__CONDITIONS__</ul>

          <div class="bk-gauge-card">
            <div class="bk-gauge-head">
              <p class="bk-total" id="bkTotal">0<small>원</small></p>
              <p class="bk-diff" id="bkDiff">0원</p>
            </div>
            <div class="bk-gauge" role="img" aria-labelledby="bkGaugeLabel">
              <span class="bk-fill" id="bkFill"></span>
              <span class="bk-band" id="bkBand"></span>
            </div>
            <p class="bk-sr" id="bkGaugeLabel">목표 예산 대비 담은 금액</p>
            <div class="bk-gauge-legend"><span>0원</span><span id="bkGaugeGoal">목표 __BUDGET__원</span><span id="bkGaugeMax">최대</span></div>
            <div class="bk-count-line">
              <span>담은 품목 <b id="bkCount">0</b> / 최소 __MINITEMS__가지</span>
              <span id="bkScoreNow">예상 0점</span>
            </div>
            <div class="bk-checks" id="bkChecks"></div>
          </div>

          <button type="button" class="bk-submit" id="bkSubmit">장바구니 제출</button>
          <button type="button" class="bk-ghost" id="bkReset">담은 것 비우기</button>
          <p class="bk-status" id="bkStatus" role="status" aria-live="polite"></p>

          <div class="bk-result" id="bkResult" hidden>
            <div class="bk-result-top">
              <span class="bk-grade" id="bkGrade">S</span>
              <div>
                <h3 id="bkResultTitle">S등급</h3>
                <p id="bkResultSub">목표에 정확히 맞췄습니다</p>
              </div>
            </div>
            <div class="bk-result-body" id="bkResultBody"></div>
            <div class="bk-share" id="bkShare"></div>
            <p class="bk-best" id="bkBestLine">오늘 가능한 최고 조합: <b>__BEST__</b></p>
          </div>
        </section>
      </aside>

      <section class="bk-shelf" aria-labelledby="bkShelfTitle">
        <div class="bk-panel">
          <div class="bk-shelf-head">
            <h2 id="bkShelfTitle">오늘의 진열대 · 8품목</h2>
            <span>서울 소매가격 · 수량 0~3</span>
          </div>
          <div class="bk-grid" id="bkGrid"></div>
        </div>
      </section>
    </div>

    <div class="bk-mini" id="bkMini">
      <div class="bk-mini-info">
        <b id="bkMiniTotal">0원</b>
        <span id="bkMiniScore">담은 품목 0 · 예상 0점</span>
      </div>
      <button type="button" class="bk-mini-btn" id="bkMiniSubmit">제출</button>
    </div>

    <section class="bk-notes">
      <h2>알아 두실 점</h2>
      <ul>
        <li><b>가격의 성격</b> — aT KAMIS가 대형마트·전통시장에서 조사한 서울 소매가격 평균입니다. 집 앞 마트의 실제 가격·할인가는 다를 수 있습니다.</li>
        <li><b>규격</b> — 값은 카드에 적힌 규격(10구·1kg·1포기·1개·100g·10개) 기준입니다. 수량을 올리면 그 규격만큼 더 담는 것으로 계산합니다.</li>
        <li><b>조사일</b> — KAMIS 소매가격은 주중에 조사되어 주말 값이 없습니다. 카드의 조사일을 함께 보세요.</li>
        <li><b>등급 규칙</b> — 예산 정확도 60점(오차 1,000원 이내 60 · 2,000원 이내 40 · 4,000원 이내 20), 조건 충족 각 20점, 최소 품목 미달이면 20점 감점. 90점 이상 S, 70점 이상 A, 50점 이상 B, 그 아래 C입니다.</li>
        <li><b>미션</b> — 날짜로만 정해집니다. 같은 날은 모두 같은 미션이고, 다음 날 0시(KST)에 바뀝니다.</li>
      </ul>
      <ul class="bk-srcs">
        <li><a href="https://www.kamis.or.kr/" target="_blank" rel="noopener noreferrer">aT KAMIS — 농산물 유통정보</a><span>서울·수원 소매가격 조사값</span></li>
        <li><a href="grocery.html">장보기 타이밍</a><span>같은 조사값을 4주 중앙값과 비교해 보는 페이지</span></li>
      </ul>
    </section>
    <p class="bk-foot">가격은 aT KAMIS 조사값을 그대로 옮겼습니다 · 등급 계산과 화면 구성만 이 페이지에서 합니다.</p>
  </main>

  <script type="application/json" id="bkData">__DATA_JSON__</script>
  <script>__JS__</script>
</body>
</html>
"""

JS = r"""
(function () {
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
  try { DATA = JSON.parse(document.getElementById('bkData').textContent); } catch (e) { return; }

  var MISSION = DATA.mission;
  var RULES = DATA.rules;
  var STORE_KEY = DATA.storeKey;
  var ITEMS = DATA.items;
  var BY_ID = {};
  ITEMS.forEach(function (item) { BY_ID[item.id] = item; });
  var CATEGORY = {};
  ITEMS.forEach(function (item) { CATEGORY[item.id] = item.category; });
  var MAX_QTY = RULES.maxQty;

  // ---------- 날짜 (KST) ----------
  function pad(v) { return v < 10 ? '0' + v : String(v); }
  function kstDateString(now) {
    var shifted = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + 9 * 3600000);
    return shifted.getFullYear() + '-' + pad(shifted.getMonth() + 1) + '-' + pad(shifted.getDate());
  }
  function yesterdayOf(dateString) {
    var p = dateString.split('-');
    var d = new Date(Date.UTC(Number(p[0]), Number(p[1]) - 1, Number(p[2])));
    d.setUTCDate(d.getUTCDate() - 1);
    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  }

  // ---------- 오늘의 미션 (빌드와 같은 식) ----------
  function dayNumber(now) {
    var shifted = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + 9 * 3600000);
    return Math.floor(Date.UTC(shifted.getFullYear(), shifted.getMonth(), shifted.getDate()) / 86400000);
  }
  function missionOf(seed) {
    var budgetList = RULES.budgets;
    var minList = RULES.minItemsChoices;
    var conds = RULES.conditions;
    var budget = budgetList[seed % budgetList.length];
    var minItems = minList[Math.floor(seed / budgetList.length) % minList.length];
    var first = conds[seed % conds.length];
    var pool = conds.filter(function (c) { return c.id !== first.id; });
    var second = pool[Math.floor(seed / conds.length) % pool.length];
    return {
      date: kstDateString(new Date(seed * 86400000)),
      seed: seed,
      budget: budget,
      tolerance: RULES.tolerance,
      minItems: minItems,
      conditions: [{ id: first.id, label: first.label }, { id: second.id, label: second.label }]
    };
  }
  var todayString = kstDateString(new Date());
  var mission = MISSION;
  var missionFromBuild = mission.date === todayString;
  if (mission.date !== todayString) {
    // 빌드한 날짜와 오늘(KST)이 다르면 화면에서 같은 식으로 다시 계산한다.
    mission = missionOf(dayNumber(new Date()));
    mission.date = todayString;
  }

  // ---------- 채점 (빌드와 같은 규칙) ----------
  function budgetPoints(diff, tolerance) {
    if (diff <= tolerance) return RULES.budgetPoints;
    if (diff <= tolerance * 2) return 40;
    if (diff <= tolerance * 4) return 20;
    return 0;
  }
  function conditionMet(id, picks) {
    var chosen = Object.keys(picks).filter(function (key) { return picks[key] > 0; });
    function any(predicate) { return chosen.some(function (key) { return predicate(BY_ID[key]); }); }
    if (id === 'leaf') return any(function (item) { return item.category === '잎채소'; });
    if (id === 'fruit') return any(function (item) { return item.category === '과일'; });
    if (id === 'egg') return any(function (item) { return item.id === 'egg'; });
    if (id === 'root') return any(function (item) { return item.category === '뿌리채소'; });
    if (id === 'kinds3') {
      var kinds = {};
      chosen.forEach(function (key) { kinds[BY_ID[key].category] = true; });
      return Object.keys(kinds).length >= 3;
    }
    return false;
  }
  function gradeFor(points) {
    if (points >= 90) return 'S';
    if (points >= 70) return 'A';
    if (points >= 50) return 'B';
    return 'C';
  }
  function evaluate(picks) {
    var total = 0;
    var count = 0;
    Object.keys(picks).forEach(function (key) {
      var qty = picks[key] || 0;
      if (!qty) return;
      total += BY_ID[key].price * qty;
      count += 1;
    });
    var diff = Math.abs(total - mission.budget);
    var points = budgetPoints(diff, mission.tolerance);
    var checks = mission.conditions.map(function (condition) {
      var met = conditionMet(condition.id, picks);
      if (met) points += RULES.conditionPoints;
      return { id: condition.id, label: condition.label, met: met };
    });
    var countOk = count >= mission.minItems;
    if (!countOk) points = Math.max(0, points - 20);
    return {
      total: total, count: count, diff: diff, points: points, grade: gradeFor(points),
      countOk: countOk, checks: checks, budgetOk: diff <= mission.tolerance
    };
  }

  // ---------- 기록 ----------
  function loadRecord() {
    var empty = { streak: 0, bestGrade: '', plays: 0, lastDate: '', history: {} };
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); } catch (e) { raw = null; }
    if (!raw || typeof raw !== 'object') return empty;
    return {
      streak: Number(raw.streak) || 0,
      bestGrade: typeof raw.bestGrade === 'string' ? raw.bestGrade : '',
      plays: Number(raw.plays) || 0,
      lastDate: typeof raw.lastDate === 'string' ? raw.lastDate : '',
      history: raw.history && typeof raw.history === 'object' ? raw.history : {}
    };
  }
  var record = loadRecord();
  function saveRecord() { try { localStorage.setItem(STORE_KEY, JSON.stringify(record)); } catch (e) {} }

  var GRADE_ORDER = { '': 0, C: 1, B: 2, A: 3, S: 4 };
  function settle(result) {
    var today = kstDateString(new Date());
    if (record.history[today]) return false;
    record.history[today] = { grade: result.grade, total: result.total, points: result.points };
    record.plays += 1;
    record.streak = record.lastDate === yesterdayOf(today) ? record.streak + 1 : 1;
    record.lastDate = today;
    if (GRADE_ORDER[result.grade] > GRADE_ORDER[record.bestGrade]) record.bestGrade = result.grade;
    saveRecord();
    return true;
  }

  // ---------- 상태 ----------
  var picks = {};
  ITEMS.forEach(function (item) { picks[item.id] = 0; });
  var submitted = false;

  var els = {
    grid: document.getElementById('bkGrid'),
    total: document.getElementById('bkTotal'),
    diff: document.getElementById('bkDiff'),
    fill: document.getElementById('bkFill'),
    band: document.getElementById('bkBand'),
    gaugeMax: document.getElementById('bkGaugeMax'),
    count: document.getElementById('bkCount'),
    scoreNow: document.getElementById('bkScoreNow'),
    checks: document.getElementById('bkChecks'),
    submit: document.getElementById('bkSubmit'),
    reset: document.getElementById('bkReset'),
    status: document.getElementById('bkStatus'),
    result: document.getElementById('bkResult'),
    grade: document.getElementById('bkGrade'),
    resultTitle: document.getElementById('bkResultTitle'),
    resultSub: document.getElementById('bkResultSub'),
    resultBody: document.getElementById('bkResultBody'),
    share: document.getElementById('bkShare'),
    bestLine: document.getElementById('bkBestLine'),
    miniTotal: document.getElementById('bkMiniTotal'),
    miniScore: document.getElementById('bkMiniScore'),
    miniSubmit: document.getElementById('bkMiniSubmit')
  };

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }
  function won(value) { return Math.round(value).toLocaleString('ko-KR'); }

  function chipOf(gap) {
    if (gap <= -3) return { kind: 'low', label: '평소보다 ' + Math.round(Math.abs(gap)) + '% 낮음' };
    if (gap >= 3) return { kind: 'high', label: '평소보다 ' + Math.round(gap) + '% 높음' };
    return { kind: 'same', label: '평소와 비슷' };
  }

  function buildGrid() {
    els.grid.innerHTML = '';
    ITEMS.forEach(function (item) {
      var card = el('article', 'bk-item');
      card.dataset.id = item.id;
      var top = el('div', 'bk-item-top');
      var titleBox = el('div', '');
      titleBox.appendChild(el('h3', '', item.name));
      titleBox.appendChild(el('p', 'bk-item-meta', '/' + item.unit + (item.grade ? ' · ' + item.grade : '')));
      top.appendChild(titleBox);
      top.appendChild(el('span', 'bk-cat', item.category));
      card.appendChild(top);

      var price = el('p', 'bk-price', won(item.price));
      price.appendChild(el('small', '', '원'));
      card.appendChild(price);

      card.appendChild(el('p', 'bk-item-meta', item.date.replace(/-/g, '.') + ' 조사' + (item.stale ? ' · 이전 수집값' : '')));

      var foot = el('div', 'bk-item-foot');
      var chip = chipOf(item.gapPct);
      foot.appendChild(el('span', 'bk-chip' + (chip.kind === 'low' ? ' is-low' : chip.kind === 'high' ? ' is-high' : ''), chip.label));

      var stepper = el('div', 'bk-stepper');
      var minus = el('button', 'bk-step', '−');
      minus.type = 'button';
      minus.dataset.step = '-1';
      minus.dataset.id = item.id;
      minus.setAttribute('aria-label', item.name + ' 한 개 빼기');
      var value = el('span', 'bk-qty is-zero', '0');
      value.id = 'bkQty-' + item.id;
      value.setAttribute('aria-live', 'polite');
      var plus = el('button', 'bk-step', '+');
      plus.type = 'button';
      plus.dataset.step = '1';
      plus.dataset.id = item.id;
      plus.setAttribute('aria-label', item.name + ' 한 개 담기');
      stepper.appendChild(minus);
      stepper.appendChild(value);
      stepper.appendChild(plus);
      foot.appendChild(stepper);
      card.appendChild(foot);

      var src = el('a', 'bk-src', 'KAMIS 원문');
      src.href = item.sourceUrl;
      src.target = '_blank';
      src.rel = 'noopener noreferrer';
      card.appendChild(src);

      els.grid.appendChild(card);
    });
  }

  function renderChecks(result) {
    els.checks.innerHTML = '';
    mission.conditions.forEach(function (condition, index) {
      var check = el('div', 'bk-check' + (result.checks[index].met ? ' is-on' : ''));
      check.appendChild(el('i', ''));
      check.appendChild(el('span', '', condition.label));
      els.checks.appendChild(check);
    });
    var countCheck = el('div', 'bk-check' + (result.countOk ? ' is-on' : ''));
    countCheck.appendChild(el('i', ''));
    countCheck.appendChild(el('span', '', '최소 ' + mission.minItems + '가지 담기'));
    els.checks.appendChild(countCheck);
  }

  function render() {
    var result = evaluate(picks);
    els.total.innerHTML = '';
    els.total.appendChild(document.createTextNode(won(result.total)));
    els.total.appendChild(el('small', '', '원'));

    var diff = result.total - mission.budget;
    els.diff.textContent = (diff === 0 ? '0원 · 목표와 같음' : (diff > 0 ? '+' : '−') + won(Math.abs(diff)) + '원');
    els.diff.className = 'bk-diff' + (result.total === 0 ? '' : result.budgetOk ? ' is-ok' : diff > 0 ? ' is-over' : ' is-under');

    // 게이지: 목표의 2배를 최대로 본다
    var maxValue = Math.max(mission.budget * 2, result.total, mission.budget + mission.tolerance);
    els.fill.style.width = Math.min(100, result.total / maxValue * 100).toFixed(2) + '%';
    var bandStart = (mission.budget - mission.tolerance) / maxValue * 100;
    var bandWidth = (mission.tolerance * 2) / maxValue * 100;
    els.band.style.left = bandStart.toFixed(2) + '%';
    els.band.style.width = bandWidth.toFixed(2) + '%';
    els.gaugeMax.textContent = won(maxValue) + '원';

    els.count.textContent = String(result.count);
    els.scoreNow.textContent = '예상 ' + result.points + '점 · ' + result.grade + '등급';
    els.miniTotal.textContent = won(result.total) + '원';
    els.miniScore.textContent = '담은 품목 ' + result.count + ' · 예상 ' + result.points + '점 ' + result.grade + '등급';
    renderChecks(result);

    ITEMS.forEach(function (item) {
      var card = els.grid.querySelector('[data-id="' + item.id + '"]');
      var qty = picks[item.id];
      card.classList.toggle('is-in', qty > 0);
      var value = document.getElementById('bkQty-' + item.id);
      value.textContent = String(qty);
      value.classList.toggle('is-zero', qty === 0);
      card.querySelector('[data-step="-1"]').disabled = qty <= 0;
      card.querySelector('[data-step="1"]').disabled = qty >= MAX_QTY;
    });
    return result;
  }

  els.grid.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('button[data-step]') : null;
    if (!btn || submitted) return;
    var id = btn.dataset.id;
    var next = picks[id] + Number(btn.dataset.step);
    picks[id] = Math.max(0, Math.min(MAX_QTY, next));
    els.status.textContent = '';
    render();
  });

  function resultLine(result) {
    return '오늘의 장바구니 리그 · ' + kstDateString(new Date()) + '\n' +
      result.grade + '등급 · ' + won(result.total) + '원 (목표 ' + won(mission.budget) + '원 ±' + won(mission.tolerance) + ')\n' +
      result.count + '가지 · ' + result.points + '점 · 연속 ' + record.streak + '일';
  }

  function submitBasket() {
    if (submitted) return;
    var result = evaluate(picks);
    submitted = true;
    var isNewDay = settle(result);
    els.result.hidden = false;
    els.result.className = 'bk-result grade-' + result.grade;
    els.grade.textContent = result.grade;
    els.resultTitle.textContent = result.grade + '등급 · ' + result.points + '점';
    els.resultSub.textContent = result.budgetOk
      ? '목표 예산에 ' + (result.diff === 0 ? '정확히 맞췄습니다' : won(result.diff) + '원 차이로 들어왔습니다')
      : (result.total > mission.budget ? '예산을 ' + won(result.diff) + '원 넘겼습니다' : '예산보다 ' + won(result.diff) + '원 적게 담았습니다');
    els.resultBody.innerHTML = '';
    function row(label, value) {
      var p = el('p', '', label + ' ');
      p.appendChild(el('b', '', value));
      els.resultBody.appendChild(p);
    }
    row('합계', won(result.total) + '원 · ' + result.count + '가지');
    row('목표', won(mission.budget) + '원 ±' + won(mission.tolerance) + '원');
    mission.conditions.forEach(function (condition, index) {
      row(condition.label, result.checks[index].met ? '충족' : '미충족');
    });
    row('최소 품목', result.countOk ? '충족' : '미달');
    row('연속 참여', (isNewDay ? record.streak : Math.max(record.streak, 1)).toString() + '일 · 최고 ' + (record.bestGrade || '—'));
    els.share.textContent = resultLine(result);
    els.submit.disabled = true;
    els.status.textContent = '결과를 기록했습니다. 다시 담으면 같은 날 기록은 유지됩니다.';
    els.miniSubmit.disabled = true;
    copyText(resultLine(result));
  }

  els.submit.addEventListener('click', submitBasket);
  els.miniSubmit.addEventListener('click', submitBasket);

  els.reset.addEventListener('click', function () {
    ITEMS.forEach(function (item) { picks[item.id] = 0; });
    els.status.textContent = '';
    render();
  });

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(function () {});
    }
  }

  buildGrid();
  render();
  if (record.lastDate === kstDateString(new Date())) {
    els.status.textContent = '오늘 이미 참여했습니다. 최고 ' + (record.bestGrade || '—') + '등급 · 연속 ' + record.streak + '일.';
  }

  // 테스트·디버깅용
  window.BASKET = {
    data: DATA,
    mission: mission,
    missionFromBuild: missionFromBuild,
    picks: function () { return picks; },
    set: function (id, qty) { if (id in picks) { picks[id] = Math.max(0, Math.min(MAX_QTY, qty)); render(); } },
    evaluate: function () { return evaluate(picks); },
    submit: function () { els.submit.click(); },
    best: DATA.best
  };
})();
"""


if __name__ == "__main__":
    build()

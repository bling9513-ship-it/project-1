#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""90초 생활 추리(mystery90.html).

무엇을 하나
  · KST 날짜로 정해지는 오늘의 사건 1건 + 연습 사건 13건(`mystery90_data.py`).
  · 90초 카운트다운이 끝나기 전에 시각 단서 카드(영수증·택배함·출입기록·메모 모형)를 읽고
      - order 유형: 사건 타임라인 4~5단계를 시간 순서대로 배열
      - pick  유형: 단서를 근거로 원인/범인을 4지선다에서 선택
    해서 제출한다. 힌트는 남은 시간 10초를 깎고 사용 수를 기록한다.
  · 결과는 스포일러 없는 한 줄 복사 문구 + 연속 스트릭 localStorage(`secjobs-mystery90-v1`).
  · 3단계 움직이는 가이드(CSS)는 한 번만 자동 재생하고 `다시 보기` 로 다시 본다.
    `prefers-reduced-motion` 에서는 정지 화면으로 바로 보여 준다.

지키는 것
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 사건 레일 + 단서 보드 / 모바일(390px) 사건 → 타이머 → 단서 → 제출 순
  · 문제·정답은 빌드 시점에 섞어서 심고, 섞인 순서도 함께 심어 화면과 검증이 같은 값을 본다.
"""
import hashlib
import json
import os
import random
from datetime import date, datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell
from mystery90_data import CASES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(BASE_DIR, "mystery90.html")
KST = timezone(timedelta(hours=9))
EPOCH = date(1970, 1, 1)

LIMIT_SECONDS = 90
HINT_PENALTY_SECONDS = 10
STORE_KEY = "secjobs-mystery90-v1"
GUIDE_KEY = "mystery90_guide_seen_v1"
DAILY_POOL = 14


# ---------------------------------------------------------------------------
# 데이터 검증 · 섞기
# ---------------------------------------------------------------------------
def validate(cases=None):
    cases = cases if cases is not None else CASES
    if len(cases) < 10:
        raise SystemExit("사건이 %d건입니다(10건 이상 필요)." % len(cases))
    seen = set()
    for case in cases:
        cid = case.get("id")
        if not cid or cid in seen:
            raise SystemExit("사건 ID 가 없거나 중복입니다: %r" % cid)
        seen.add(cid)
        if case.get("type") not in ("order", "pick"):
            raise SystemExit("%s 유형이 잘못됐습니다: %r" % (cid, case.get("type")))
        steps = case.get("steps") or []
        if not 4 <= len(steps) <= 5:
            raise SystemExit("%s 단계가 %d개입니다(4~5개 필요)." % (cid, len(steps)))
        if len({step["text"] for step in steps}) != len(steps):
            raise SystemExit("%s 단계 문구가 중복됩니다." % cid)
        if not case.get("hint") or not case.get("explain"):
            raise SystemExit("%s 힌트/해설이 비었습니다." % cid)
        if case["type"] == "pick":
            choices = case.get("choices") or []
            if len(choices) != 4 or len(set(choices)) != 4:
                raise SystemExit("%s 선택지가 4개가 아닙니다." % cid)
            if not isinstance(case.get("answer"), int) or not 0 <= case["answer"] < 4:
                raise SystemExit("%s 정답 인덱스가 잘못됐습니다." % cid)
    return cases


def _rng(seed_text):
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def shuffled_positions(cid, count):
    """단계를 화면에 보여 줄 순서(정답 위치의 순열). 정답 순서와 겹치지 않게 한 번 돌린다."""
    order = list(range(count))
    rng = _rng("steps:" + cid)
    rng.shuffle(order)
    if order == list(range(count)) and count > 1:
        order = order[1:] + order[:1]
    return order


def shuffled_choices(cid, choices, answer):
    order = list(range(len(choices)))
    rng = _rng("choices:" + cid)
    rng.shuffle(order)
    if order == list(range(len(choices))) and len(choices) > 1:
        order = order[1:] + order[:1]
    return [choices[i] for i in order], order.index(answer)


def daily_case_id(day, cases=None):
    cases = cases if cases is not None else CASES
    pool = cases[:DAILY_POOL]
    return pool[(day - EPOCH).days % len(pool)]["id"]


def build_payload(day):
    cases = validate()
    payload = []
    for case in cases:
        display = shuffled_positions(case["id"], len(case["steps"]))
        item = {
            "id": case["id"],
            "title": case["title"],
            "type": case["type"],
            "where": case["where"],
            "level": case["level"],
            "brief": case["brief"],
            "hint": case["hint"],
            "explain": case["explain"],
            "steps": [
                {"tag": step["tag"], "visual": step["visual"], "text": step["text"]}
                for step in case["steps"]
            ],
            "display": display,
        }
        if case["type"] == "pick":
            choices, answer = shuffled_choices(case["id"], case["choices"], case["answer"])
            item["question"] = case["question"]
            item["choices"] = choices
            item["answer"] = answer
        payload.append(item)
    return {
        "cases": payload,
        "daily": daily_case_id(day),
        "date": day.isoformat(),
        "limit": LIMIT_SECONDS,
        "hintPenalty": HINT_PENALTY_SECONDS,
        "storeKey": STORE_KEY,
        "guideKey": GUIDE_KEY,
    }


def build(out_path=None, today=None):
    today = today or datetime.now(KST).date()
    payload = build_payload(today)
    daily = next(case for case in payload["cases"] if case["id"] == payload["daily"])
    practice = [case for case in payload["cases"] if case["id"] != payload["daily"]]

    practice_html = "".join(
        '<button type="button" class="m9-practice-item" data-case="{cid}">'
        '<span class="m9-practice-num">{num}</span>'
        '<span class="m9-practice-text"><b>{title}</b><span>{where} · {level}</span></span>'
        '<span class="m9-practice-type">{kind}</span></button>'.format(
            cid=case["id"],
            num="%02d" % (index + 1),
            title=case["title"],
            where=case["where"],
            level=case["level"],
            kind="순서" if case["type"] == "order" else "원인",
        )
        for index, case in enumerate(practice)
    )

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__TODAY__", payload["date"])
            .replace("__DAILY_TITLE__", daily["title"])
            .replace("__DAILY_WHERE__", daily["where"])
            .replace("__TOTAL__", str(len(payload["cases"])))
            .replace("__PRACTICE__", practice_html)
            .replace("__LIMIT__", str(LIMIT_SECONDS))
            .replace("__DATA_JSON__", safe_json_for_script(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":"))))
            .replace("__JS__", JS.replace("__GUIDE_KEY__", GUIDE_KEY)))

    with open(out_path or OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "mystery90")))

    print("-> 'mystery90.html' 생성 완료 (%s 오늘의 사건 %s · 사건 %d건 · 90초)"
          % (payload["date"], daily["id"], len(payload["cases"])))
    return {"cases": len(payload["cases"]), "daily": payload["daily"], "date": payload["date"]}


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
      --miss-bg: #fef2f2;  --miss-text: #b91c1c;  --miss-border: #fecaca;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --ok-bg: rgba(16, 185, 129, 0.14);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.34);  --ok-ink: #5eead4;
      --warn-bg: rgba(245, 158, 11, 0.14);  --warn-text: #fcd34d;  --warn-border: rgba(245, 158, 11, 0.34);
      --miss-bg: rgba(239, 68, 68, 0.14);  --miss-text: #fca5a5;  --miss-border: rgba(239, 68, 68, 0.32);
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body { font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease; }
    .m9-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .m9-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 96px; }
    .m9-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .m9-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 660px; word-break: keep-all; }
    .m9-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .m9-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px;
      font-size: 11.5px; color: var(--text-muted); }
    .m9-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }

    /* ---------- 움직이는 3단계 가이드 ---------- */
    .m9-guide { margin-top: 16px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 14px 16px; box-shadow: var(--card-shadow); }
    .m9-guide-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .m9-guide-head h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); }
    .m9-guide-replay { border: 1px solid var(--border-default); background: var(--bg-page); color: var(--text-secondary);
      border-radius: 9px; padding: 5px 10px; font-family: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }
    .m9-guide-replay:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .m9-guide-frames { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 11px; }
    .m9-frame { border: 1px solid var(--border-subtle); background: var(--bg-page); border-radius: 12px;
      padding: 10px; display: flex; flex-direction: column; gap: 6px; min-height: 128px; }
    .m9-frame-stage { position: relative; height: 62px; border-radius: 9px; background: var(--bg-subtle);
      overflow: hidden; display: flex; align-items: center; justify-content: center; gap: 6px; }
    .m9-frame-num { font-size: 10px; font-weight: 800; color: var(--text-muted); letter-spacing: 0; }
    .m9-frame p { font-size: 11.5px; font-weight: 700; color: var(--text-secondary); word-break: keep-all; }
    .m9-frame p span { display: block; font-size: 10.5px; font-weight: 500; color: var(--text-muted); margin-top: 2px; }
    .m9-chipmini { width: 30px; height: 20px; border-radius: 6px; background: var(--bg-surface);
      border: 1px solid var(--border-strong); }
    .m9-chipmini.f1 { height: 24px; }
    .m9-chipmini.f2 { opacity: .72; }
    .m9-chipmini.f3 { opacity: .45; }
    .m9-arg { position: absolute; left: 50%; bottom: 6px; width: 9px; height: 9px; margin-left: -5px;
      border-right: 2px solid var(--accent-primary); border-bottom: 2px solid var(--accent-primary);
      transform: rotate(45deg); }
    .m9-numcircle { position: absolute; left: 50%; top: 7px; width: 32px; height: 32px; margin-left: -16px;
      border-radius: 50%; border: 2px solid var(--accent-primary); display: flex; align-items: center;
      justify-content: center; font-size: 13px; font-weight: 800; color: var(--accent-primary); background: var(--bg-surface); }
    .m9-clockmini { position: absolute; left: 50%; top: 12px; width: 38px; height: 38px; margin-left: -19px;
      border-radius: 50%; border: 3px solid var(--border-strong); }
    .m9-clockmini::after { content: ""; position: absolute; left: 50%; top: 50%; width: 2px; height: 13px;
      background: var(--text-primary); transform-origin: bottom center; transform: translate(-1px, -100%) rotate(38deg); }

    /* 가이드 재생: 프레임이 차례로 켜지고 움직임이 멈춘 뒤 정지한다. */
    .m9-guide.is-playing .m9-frame { animation: m9-frame-in 520ms cubic-bezier(0.2, 0.8, 0.2, 1) both; }
    .m9-guide.is-playing .m9-frame:nth-child(1) { animation-delay: 80ms; }
    .m9-guide.is-playing .m9-frame:nth-child(2) { animation-delay: 980ms; }
    .m9-guide.is-playing .m9-frame:nth-child(3) { animation-delay: 1880ms; }
    .m9-guide.is-playing .m9-chipmini { animation: m9-chip-move 900ms cubic-bezier(0.2, 0.8, 0.2, 1) both; }
    .m9-guide.is-playing .m9-chipmini.f2 { animation-delay: 120ms; }
    .m9-guide.is-playing .m9-chipmini.f3 { animation-delay: 240ms; }
    .m9-guide.is-playing .m9-arg { animation: m9-arg-down 700ms cubic-bezier(0.2, 0.8, 0.2, 1) 900ms both; }
    .m9-guide.is-playing .m9-clockmini::after { animation: m9-hand 1600ms linear 1600ms both; }
    @keyframes m9-frame-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
    @keyframes m9-chip-move { from { transform: translateX(-10px); opacity: 0; } to { transform: none; opacity: 1; } }
    @keyframes m9-arg-down { from { transform: rotate(45deg) translate(-6px, -6px); opacity: 0; }
      to { transform: rotate(45deg); opacity: 1; } }
    @keyframes m9-hand { from { transform: translate(-1px, -100%) rotate(0deg); } to { transform: translate(-1px, -100%) rotate(300deg); } }

    /* ---------- 본문 배치 ---------- */
    .m9-main { display: grid; grid-template-columns: 310px minmax(0, 1fr); gap: 16px; margin-top: 16px; align-items: start; }
    .m9-main > * { min-width: 0; }
    .m9-panel { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 18px; box-shadow: var(--card-shadow); }
    .m9-panel h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); }
    .m9-rail { display: grid; gap: 12px; position: sticky; top: 76px; }
    .m9-today-title { margin-top: 8px; font-size: 16.5px; font-weight: 800; letter-spacing: -0.03em; }
    .m9-today-where { margin-top: 2px; font-size: 11.5px; color: var(--text-muted); }
    .m9-stats { margin-top: 12px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
    .m9-stat { border: 1px solid var(--border-subtle); border-radius: 11px; padding: 8px 9px; background: var(--bg-page); }
    .m9-stat span { display: block; font-size: 10px; font-weight: 700; color: var(--text-muted); }
    .m9-stat b { display: block; margin-top: 2px; font-size: 16px; font-weight: 800; letter-spacing: -0.03em;
      font-variant-numeric: tabular-nums; }
    .m9-practice { margin-top: 13px; display: grid; gap: 6px; max-height: 420px; overflow-y: auto; padding-right: 2px; }
    .m9-practice-item { display: flex; align-items: center; gap: 9px; width: 100%; text-align: left; border: 1px solid var(--border-default);
      background: var(--bg-page); border-radius: 11px; padding: 9px 10px; font-family: inherit; cursor: pointer;
      transition: border-color .15s ease, background-color .15s ease, transform .15s ease; }
    .m9-practice-item:hover { border-color: var(--border-strong); background: var(--bg-subtle); }
    .m9-practice-item:active { transform: scale(0.985); }
    .m9-practice-item:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .m9-practice-item.is-current { border-color: var(--accent-primary); background: var(--accent-subtle); }
    .m9-practice-num { flex: 0 0 auto; width: 22px; height: 22px; border-radius: 7px; background: var(--bg-muted);
      display: inline-flex; align-items: center; justify-content: center; font-size: 10.5px; font-weight: 800;
      color: var(--text-secondary); font-variant-numeric: tabular-nums; }
    .m9-practice-item.is-current .m9-practice-num { background: var(--accent-primary); color: #fff; }
    .m9-practice-text { display: flex; flex-direction: column; gap: 1px; min-width: 0; flex: 1 1 auto; }
    .m9-practice-text b { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .m9-practice-text span { font-size: 10.5px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .m9-practice-type { flex: 0 0 auto; font-size: 10px; font-weight: 700; color: var(--text-muted);
      border: 1px solid var(--border-default); border-radius: 999px; padding: 1px 7px; }

    /* ---------- 사건 카드 ---------- */
    .m9-game { display: grid; gap: 12px; }
    .m9-case-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
    .m9-case-tags { display: flex; flex-wrap: wrap; gap: 6px; font-size: 10.5px; color: var(--text-muted); }
    .m9-case-tags span { border: 1px solid var(--border-default); border-radius: 999px; padding: 1px 8px; font-weight: 700; }
    .m9-case-tags span.is-daily { border-color: var(--accent-primary); color: var(--accent-primary); background: var(--accent-subtle); }
    .m9-case-head h2 { margin-top: 8px; font-size: 20px; font-weight: 800; letter-spacing: -0.04em;
      color: var(--text-primary); }
    .m9-case-brief { margin-top: 5px; font-size: 12.5px; color: var(--text-secondary); word-break: keep-all; }

    .m9-timerbar { display: flex; align-items: center; gap: 12px; margin-top: 12px; padding: 11px 13px;
      border: 1px solid var(--border-default); border-radius: 14px; background: var(--bg-page); }
    .m9-clock { position: relative; width: 54px; height: 54px; flex: 0 0 auto; }
    .m9-clock svg { width: 54px; height: 54px; transform: rotate(-90deg); }
    .m9-clock circle { fill: none; stroke-width: 5; }
    .m9-clock .m9-ring-bg { stroke: var(--border-default); }
    .m9-clock .m9-ring-fg { stroke: var(--accent-primary); stroke-linecap: round;
      transition: stroke-dashoffset .18s linear, stroke .2s ease; }
    .m9-clock.is-low .m9-ring-fg { stroke: var(--miss-text); }
    .m9-clock-value { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
      font-size: 14px; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: -0.03em; }
    .m9-clock.is-low .m9-clock-value { color: var(--miss-text); }
    .m9-timer-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1 1 auto; }
    .m9-timer-text b { font-size: 13px; font-weight: 800; letter-spacing: -0.03em; }
    .m9-timer-text span { font-size: 11px; color: var(--text-muted); }
    .m9-timer-actions { display: flex; gap: 6px; flex: 0 0 auto; }
    .m9-btn { border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      border-radius: 10px; padding: 9px 13px; font-family: inherit; font-size: 12px; font-weight: 800; cursor: pointer;
      transition: background-color .15s ease, border-color .15s ease, transform .15s ease, opacity .15s ease; }
    .m9-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .m9-btn:active { transform: scale(0.98); }
    .m9-btn:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .m9-btn:disabled { opacity: .4; cursor: default; }
    .m9-btn.is-primary { border-color: var(--text-primary); background: var(--text-primary); color: var(--bg-surface); }
    .m9-btn.is-primary:hover { opacity: .9; }

    .m9-start { margin-top: 12px; }
    .m9-start .m9-btn { width: 100%; padding: 14px; font-size: 14px; }

    /* ---------- 단서 카드 ---------- */
    .m9-section-label { margin-top: 4px; font-size: 11px; font-weight: 700; color: var(--text-muted); }
    .m9-cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; margin-top: 7px; }
    .m9-card { position: relative; display: flex; flex-direction: column; gap: 7px; text-align: left;
      border: 1px solid var(--border-default); background: var(--bg-surface); border-radius: 13px; padding: 10px;
      font-family: inherit; color: var(--text-primary); cursor: pointer; min-height: 96px;
      transition: border-color .15s ease, background-color .15s ease, transform .15s ease, opacity .15s ease; }
    .m9-card:disabled { cursor: default; }
    .m9-card:hover:not(:disabled) { border-color: var(--border-strong); }
    .m9-card:active:not(:disabled) { transform: scale(0.99); }
    .m9-card:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .m9-card.is-picked { border-color: var(--text-primary); background: var(--bg-subtle); }
    .m9-card.is-locked { opacity: .55; }
    .m9-card.is-true { border-color: var(--ok-border); background: var(--ok-bg); }
    .m9-card.is-false { border-color: var(--miss-border); background: var(--miss-bg); }
    .m9-visual { height: 46px; border-radius: 9px; background: var(--bg-subtle); display: flex; align-items: center;
      justify-content: center; overflow: hidden; }
    .m9-visual svg { width: 100%; height: 100%; }
    .m9-card-tag { font-size: 10px; font-weight: 800; color: var(--text-muted); letter-spacing: 0; }
    .m9-card-text { font-size: 12px; font-weight: 600; line-height: 1.45; color: var(--text-secondary); word-break: keep-all; }
    .m9-card.is-picked .m9-card-text { color: var(--text-primary); }
    .m9-card-pickno { position: absolute; top: 8px; right: 8px; min-width: 20px; height: 20px; padding: 0 5px;
      border-radius: 999px; background: var(--text-primary); color: var(--bg-surface); font-size: 10.5px;
      font-weight: 800; display: inline-flex; align-items: center; justify-content: center; font-variant-numeric: tabular-nums; }

    /* 순서 트레이 */
    .m9-tray { margin-top: 9px; display: grid; gap: 6px; }
    .m9-slot { display: flex; align-items: center; gap: 8px; border: 1px dashed var(--border-strong);
      border-radius: 11px; padding: 9px 10px; min-height: 44px; background: var(--bg-page); }
    .m9-slot.is-filled { border-style: solid; border-color: var(--border-default); background: var(--bg-surface); }
    .m9-slot.is-ok { border-color: var(--ok-border); background: var(--ok-bg); }
    .m9-slot.is-ng { border-color: var(--miss-border); background: var(--miss-bg); }
    .m9-slot-no { flex: 0 0 auto; width: 22px; height: 22px; border-radius: 50%; border: 1px solid var(--border-strong);
      display: inline-flex; align-items: center; justify-content: center; font-size: 10.5px; font-weight: 800;
      color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .m9-slot.is-filled .m9-slot-no { border-color: var(--text-primary); color: var(--text-primary); }
    .m9-slot-text { font-size: 11.5px; color: var(--text-muted); flex: 1 1 auto; min-width: 0; }
    .m9-slot.is-filled .m9-slot-text { color: var(--text-primary); font-weight: 600; }
    .m9-slot-remove { flex: 0 0 auto; border: 0; background: transparent; color: var(--text-muted); font-family: inherit;
      font-size: 15px; font-weight: 800; cursor: pointer; padding: 2px 5px; border-radius: 6px; }
    .m9-slot-remove:hover { color: var(--text-primary); background: var(--bg-subtle); }

    /* 4지선다 */
    .m9-choices { margin-top: 9px; display: grid; gap: 7px; }
    .m9-choice { display: flex; align-items: flex-start; gap: 9px; width: 100%; text-align: left; border: 1px solid var(--border-default);
      background: var(--bg-surface); border-radius: 11px; padding: 11px 12px; font-family: inherit; font-size: 12.5px;
      font-weight: 600; color: var(--text-secondary); cursor: pointer; transition: border-color .15s ease, background-color .15s ease; }
    .m9-choice:hover:not(:disabled) { border-color: var(--border-strong); }
    .m9-choice:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .m9-choice.is-picked { border-color: var(--text-primary); color: var(--text-primary); background: var(--bg-subtle); }
    .m9-choice.is-true { border-color: var(--ok-border); background: var(--ok-bg); color: var(--ok-text); }
    .m9-choice.is-false { border-color: var(--miss-border); background: var(--miss-bg); color: var(--miss-text); }
    .m9-choice-no { flex: 0 0 auto; width: 20px; height: 20px; border-radius: 50%; background: var(--bg-muted);
      display: inline-flex; align-items: center; justify-content: center; font-size: 10.5px; font-weight: 800;
      color: var(--text-secondary); }
    .m9-choice.is-true .m9-choice-no { background: var(--ok-ink); color: #fff; }
    .m9-choice.is-false .m9-choice-no { background: var(--miss-text); color: #fff; }

    .m9-actions { display: flex; gap: 8px; margin-top: 12px; }
    .m9-actions .m9-btn { flex: 1 1 0; padding: 13px; font-size: 13.5px; }
    .m9-status { min-height: 16px; margin-top: 7px; font-size: 11px; font-weight: 600; color: var(--ok-ink); }

    /* ---------- 결과 ---------- */
    .m9-result { margin-top: 12px; border: 1px solid var(--border-default); border-radius: 15px; padding: 15px;
      background: var(--bg-surface); }
    .m9-result.is-correct { border-color: var(--ok-border); background: var(--ok-bg); }
    .m9-result.is-wrong { border-color: var(--miss-border); background: var(--miss-bg); }
    .m9-result-top { display: flex; align-items: center; gap: 10px; }
    .m9-badge { width: 44px; height: 44px; border-radius: 12px; display: inline-flex; align-items: center;
      justify-content: center; font-size: 12px; font-weight: 800; background: var(--text-primary); color: var(--bg-surface);
      letter-spacing: -0.02em; }
    .m9-result.is-correct .m9-badge { background: var(--ok-ink); color: #fff; }
    .m9-result.is-wrong .m9-badge { background: var(--miss-text); color: #fff; }
    .m9-result-top h3 { font-size: 15.5px; font-weight: 800; letter-spacing: -0.03em; }
    .m9-result-top p { font-size: 11.5px; color: var(--text-secondary); }
    .m9-result-stats { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
    .m9-result-stats span { font-size: 11px; font-weight: 700; color: var(--text-secondary); background: var(--bg-surface);
      border: 1px solid var(--border-default); border-radius: 999px; padding: 3px 9px; }
    .m9-share { margin-top: 10px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px;
      line-height: 1.55; white-space: pre-wrap; color: var(--text-secondary); background: var(--bg-subtle);
      border: 1px solid var(--border-default); border-radius: 10px; padding: 9px 10px; }
    .m9-explain { margin-top: 10px; font-size: 12px; line-height: 1.6; color: var(--text-secondary); word-break: keep-all; }
    .m9-explain b { color: var(--text-primary); }

    .m9-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .m9-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; color: var(--text-primary); }
    .m9-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .m9-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .m9-notes li b { color: var(--text-primary); }
    .m9-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 900px) {
      .m9-wrap { padding: 14px 13px 120px; }
      .m9-hero h1 { font-size: 21px; }
      .m9-hero p { font-size: 12px; }
      .m9-guide { padding: 12px; }
      .m9-guide-frames { gap: 6px; }
      .m9-frame { padding: 8px; min-height: 116px; }
      .m9-frame p { font-size: 10.5px; }
      .m9-frame p span { font-size: 9.5px; }
      .m9-main { display: flex; flex-direction: column; align-items: stretch; gap: 10px; margin-top: 12px; }
      .m9-rail { position: static; order: 2; }
      .m9-game { order: 1; }
      .m9-panel { padding: 14px; }
      .m9-case-head h2 { font-size: 18px; }
      .m9-practice { max-height: none; }
      .m9-cards { gap: 7px; }
      .m9-card { min-height: 92px; padding: 9px; }
      .m9-card-text { font-size: 11.5px; }
      .m9-timerbar { padding: 9px 11px; gap: 10px; }
      .m9-clock, .m9-clock svg { width: 46px; height: 46px; }
      .m9-clock-value { font-size: 12.5px; }
      .m9-timer-actions .m9-btn { padding: 8px 10px; font-size: 11px; }
    }
    @media (max-width: 430px) {
      .m9-timerbar { flex-wrap: wrap; }
      .m9-timer-text { flex: 1 1 calc(100% - 58px); }
      .m9-timer-actions { width: 100%; }
      .m9-timer-actions .m9-btn { flex: 1 1 0; }
      .m9-timer-text b { font-size: 12px; line-height: 1.35; }
    }
    @media (max-width: 380px) {
      .m9-cards { grid-template-columns: minmax(0, 1fr); }
      .m9-guide-frames { grid-template-columns: minmax(0, 1fr); }
      .m9-frame { min-height: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; animation-delay: 0ms !important; }
      .m9-guide.is-playing .m9-frame { opacity: 1; transform: none; }
      .m9-clock .m9-ring-fg { transition: none; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 90초 생활 추리</title>
  <meta name="description" content="영수증·택배함·출입기록·메모 모형 단서 카드를 읽고 90초 안에 사건 타임라인을 맞히거나 원인을 고르는 데일리 추리. 오늘의 사건 1건과 연습 13건, 남은 시간·힌트 기록과 연속 스트릭을 이 기기에 저장합니다.">
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
        <div class="update-meta"><span class="live-dot"></span><span>__TODAY__ · 사건 __TOTAL__건</span></div>
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

  <main class="m9-wrap">
    <section class="m9-hero">
      <span class="m9-pill">생활 · 90초 추리</span>
      <h1>90초 안에 사건의 순서를 세워라</h1>
      <p>영수증·택배함·출입기록·메모 모형으로 만든 단서 카드를 읽고, 사건 타임라인을 시간 순서대로 배열하거나 원인을 고릅니다. 힌트는 남은 시간 10초를 깎습니다.</p>
      <div class="m9-meta">
        <span>오늘의 사건 __DAILY_TITLE__ · __DAILY_WHERE__</span>
        <span class="m9-dot"></span>
        <span>사건 __TOTAL__건(오늘 1 + 연습)</span>
        <span class="m9-dot"></span>
        <span>제한 __LIMIT__초</span>
        <span class="m9-dot"></span>
        <span>기록은 이 기기에만 저장</span>
      </div>
    </section>

    <section class="m9-guide" id="m9Guide" aria-labelledby="m9GuideTitle">
      <div class="m9-guide-head">
        <h2 id="m9GuideTitle">이렇게 합니다 · 3단계</h2>
        <button type="button" class="m9-guide-replay" id="m9Replay">다시 보기</button>
      </div>
      <div class="m9-guide-frames">
        <div class="m9-frame">
          <div class="m9-frame-stage" aria-hidden="true">
            <span class="m9-chipmini f1"></span><span class="m9-chipmini f2"></span><span class="m9-chipmini f3"></span>
          </div>
          <p class="m9-frame-num">1</p>
          <p>단서 카드가 흩어져 있다<span>영수증·출입기록·메모를 한 장씩 읽는다</span></p>
        </div>
        <div class="m9-frame">
          <div class="m9-frame-stage" aria-hidden="true">
            <span class="m9-numcircle">1</span><span class="m9-arg"></span>
          </div>
          <p class="m9-frame-num">2</p>
          <p>시간 순서대로 탭한다<span>1번 칸부터 차례로 채우고, 다시 탭하면 뺀다</span></p>
        </div>
        <div class="m9-frame">
          <div class="m9-frame-stage" aria-hidden="true"><span class="m9-clockmini"></span></div>
          <p class="m9-frame-num">3</p>
          <p>90초 안에 제출<span>시간이 끝나면 자동으로 제출된다</span></p>
        </div>
      </div>
    </section>

    <div class="m9-main">
      <aside class="m9-rail" aria-label="오늘의 사건과 연습 목록">
        <section class="m9-panel">
          <h2>오늘의 사건 · __TODAY__</h2>
          <p class="m9-today-title">__DAILY_TITLE__</p>
          <p class="m9-today-where">__DAILY_WHERE__</p>
          <div class="m9-stats">
            <div class="m9-stat"><span>연속</span><b id="m9Streak">0일</b></div>
            <div class="m9-stat"><span>해결</span><b id="m9Solved">0</b></div>
            <div class="m9-stat"><span>최고</span><b id="m9Best">-</b></div>
          </div>
        </section>
        <section class="m9-panel">
          <h2>연습 사건 __TOTAL__건 중 오늘 제외</h2>
          <div class="m9-practice" id="m9Practice">__PRACTICE__</div>
        </section>
      </aside>

      <section class="m9-game" aria-labelledby="m9CaseTitle">
        <div class="m9-panel">
          <div class="m9-case-head">
            <div>
              <div class="m9-case-tags">
                <span class="is-daily" id="m9DailyTag">오늘의 사건</span>
                <span id="m9Where">__DAILY_WHERE__</span>
                <span id="m9Level">보통</span>
                <span id="m9Kind">순서</span>
              </div>
              <h2 id="m9CaseTitle">__DAILY_TITLE__</h2>
              <p class="m9-case-brief" id="m9Brief">사건 설명을 불러오는 중입니다.</p>
            </div>
          </div>

          <div class="m9-timerbar">
            <div class="m9-clock" id="m9Clock" role="img" aria-label="남은 시간 90초">
              <svg viewBox="0 0 54 54" aria-hidden="true">
                <circle class="m9-ring-bg" cx="27" cy="27" r="23"></circle>
                <circle class="m9-ring-fg" id="m9Ring" cx="27" cy="27" r="23" stroke-dasharray="144.5" stroke-dashoffset="0"></circle>
              </svg>
              <span class="m9-clock-value" id="m9Timer">90</span>
            </div>
            <div class="m9-timer-text">
              <b id="m9TimerTitle">시작을 누르면 90초가 흐릅니다</b>
              <span id="m9TimerSub">힌트 0개 · 제출 전</span>
            </div>
            <div class="m9-timer-actions">
              <button type="button" class="m9-btn" id="m9Hint">힌트</button>
              <button type="button" class="m9-btn" id="m9Restart">처음부터</button>
            </div>
          </div>

          <div class="m9-start" id="m9StartWrap">
            <button type="button" class="m9-btn is-primary" id="m9Start">90초 시작</button>
          </div>

          <p class="m9-section-label" id="m9CardsLabel">단서 카드 · 탭해서 순서대로 담기</p>
          <div class="m9-cards" id="m9Cards"></div>

          <div class="m9-tray" id="m9Tray" aria-label="사건 순서 배열"></div>
          <div class="m9-choices" id="m9Choices" hidden></div>

          <div class="m9-actions">
            <button type="button" class="m9-btn is-primary" id="m9Submit" disabled>제출</button>
          </div>
          <p class="m9-status" id="m9Status" role="status" aria-live="polite"></p>

          <div class="m9-result" id="m9Result" hidden>
            <div class="m9-result-top">
              <span class="m9-badge" id="m9Badge">정답</span>
              <div>
                <h3 id="m9ResultTitle">정답입니다</h3>
                <p id="m9ResultSub"></p>
              </div>
            </div>
            <div class="m9-result-stats" id="m9ResultStats"></div>
            <div class="m9-share" id="m9Share"></div>
            <p class="m9-explain" id="m9Explain"></p>
          </div>
        </div>
      </section>
    </div>

    <section class="m9-notes">
      <h2>알아 두실 점</h2>
      <ul>
        <li><b>문제의 성격</b> — 실제 사건이 아니라 생활에서 흔한 상황을 새로 지어 만든 추리 문제입니다. 인물·장소·번호는 모두 가상입니다.</li>
        <li><b>점수</b> — 정답이면 60점에 남은 시간 초의 절반(최대 45점)을 더하고, 힌트 하나마다 8점을 뺍니다. 틀리면 0점입니다.</li>
        <li><b>힌트</b> — 결정적 단서 한 줄을 보여 주는 대신 남은 시간 10초를 깎습니다.</li>
        <li><b>기록</b> — 오늘의 사건 결과와 연속 일수는 이 브라우저(localStorage)에만 저장됩니다. 서버로 보내지 않습니다.</li>
        <li><b>시각 단서 카드</b> — 영수증·택배함·출입기록·메모 모형은 이해를 돕기 위해 그린 그림이며 실제 서류와 다릅니다.</li>
      </ul>
      <p class="m9-foot">사건·정답·해설은 이 페이지에서만 쓰는 창작 문제입니다 · 기록은 기기를 바꾸면 이어지지 않습니다.</p>
    </section>
  </main>

  <script type="application/json" id="m9Data">__DATA_JSON__</script>
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

  // ---------- 가이드: 한 번만 자동 재생 ----------
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var guide = document.getElementById('m9Guide');
  var replay = document.getElementById('m9Replay');
  var guideTimer = null;
  function playGuide() {
    if (!guide) return;
    guide.classList.remove('is-playing');
    if (guideTimer) { window.clearTimeout(guideTimer); guideTimer = null; }
    if (reduceMotion) return;
    // 같은 프레임에서 클래스를 다시 붙이면 애니메이션이 재시작되지 않으므로 한 번 끊는다.
    void guide.offsetWidth;
    guide.classList.add('is-playing');
    guideTimer = window.setTimeout(function () {
      guide.classList.remove('is-playing');
      guideTimer = null;
    }, 3200);
  }
  var GUIDE_KEY = '__GUIDE_KEY__';
  var guideSeen = false;
  try { guideSeen = localStorage.getItem(GUIDE_KEY) === '1'; } catch (e) { guideSeen = false; }
  if (!guideSeen) {
    playGuide();
    try { localStorage.setItem(GUIDE_KEY, '1'); } catch (e) {}
  }
  if (replay) replay.addEventListener('click', playGuide);

  // ---------- 데이터 ----------
  var DATA;
  try { DATA = JSON.parse(document.getElementById('m9Data').textContent); } catch (e) { return; }
  var CASES = DATA.cases;
  var BY_ID = {};
  CASES.forEach(function (item) { BY_ID[item.id] = item; });
  var LIMIT = DATA.limit;
  var HINT_PENALTY = DATA.hintPenalty;
  var STORE_KEY = DATA.storeKey;

  // ---------- KST 날짜 ----------
  function pad(v) { return v < 10 ? '0' + v : String(v); }
  function kstParts(now) {
    var shifted = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + 9 * 3600000);
    return { y: shifted.getFullYear(), m: shifted.getMonth() + 1, d: shifted.getDate() };
  }
  function kstDateString(now) {
    var p = kstParts(now);
    return p.y + '-' + pad(p.m) + '-' + pad(p.d);
  }
  function yesterdayOf(dateString) {
    var p = dateString.split('-');
    var d = new Date(Date.UTC(Number(p[0]), Number(p[1]) - 1, Number(p[2])));
    d.setUTCDate(d.getUTCDate() - 1);
    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  }

  // ---------- 기록 ----------
  function loadRecord() {
    var empty = { streak: 0, lastDate: '', solved: 0, best: 0, history: {} };
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); } catch (e) { raw = null; }
    if (!raw || typeof raw !== 'object') return empty;
    return {
      streak: Number(raw.streak) || 0,
      lastDate: typeof raw.lastDate === 'string' ? raw.lastDate : '',
      solved: Number(raw.solved) || 0,
      best: Number(raw.best) || 0,
      history: raw.history && typeof raw.history === 'object' ? raw.history : {}
    };
  }
  var record = loadRecord();
  function saveRecord() { try { localStorage.setItem(STORE_KEY, JSON.stringify(record)); } catch (e) {} }
  function settle(caseId, result) {
    var today = kstDateString(new Date());
    var key = today + '|' + caseId;
    var firstToday = !record.history[today];
    if (!record.history[key] && record.solved < 9999) { record.solved += result.correct ? 1 : 0; }
    record.history[key] = { correct: result.correct, remaining: result.remaining, hints: result.hints };
    if (firstToday) {
      record.streak = record.lastDate === yesterdayOf(today) ? record.streak + 1 : 1;
      record.lastDate = today;
    }
    if (result.correct && result.points > record.best) record.best = result.points;
    saveRecord();
    return firstToday;
  }
  function renderStats() {
    var streak = document.getElementById('m9Streak');
    var solved = document.getElementById('m9Solved');
    var best = document.getElementById('m9Best');
    if (streak) streak.textContent = record.streak + '일';
    if (solved) solved.textContent = String(record.solved);
    if (best) best.textContent = record.best > 0 ? record.best + '점' : '-';
  }

  // ---------- 상태 ----------
  var state = {
    caseItem: null,
    isDaily: true,
    phase: 'idle',          // idle | playing | done
    entered: [],            // order: 화면 카드 인덱스를 고른 순서
    picked: -1,             // pick: 선택한 보기
    hints: 0,
    deadline: 0,
    startedAt: 0,
    remaining: LIMIT,
    timer: null,
    result: null
  };

  var els = {
    cards: document.getElementById('m9Cards'),
    cardsLabel: document.getElementById('m9CardsLabel'),
    tray: document.getElementById('m9Tray'),
    choices: document.getElementById('m9Choices'),
    submit: document.getElementById('m9Submit'),
    startWrap: document.getElementById('m9StartWrap'),
    start: document.getElementById('m9Start'),
    hint: document.getElementById('m9Hint'),
    restart: document.getElementById('m9Restart'),
    status: document.getElementById('m9Status'),
    timer: document.getElementById('m9Timer'),
    timerTitle: document.getElementById('m9TimerTitle'),
    timerSub: document.getElementById('m9TimerSub'),
    clock: document.getElementById('m9Clock'),
    ring: document.getElementById('m9Ring'),
    title: document.getElementById('m9CaseTitle'),
    brief: document.getElementById('m9Brief'),
    where: document.getElementById('m9Where'),
    level: document.getElementById('m9Level'),
    kind: document.getElementById('m9Kind'),
    dailyTag: document.getElementById('m9DailyTag'),
    result: document.getElementById('m9Result'),
    badge: document.getElementById('m9Badge'),
    resultTitle: document.getElementById('m9ResultTitle'),
    resultSub: document.getElementById('m9ResultSub'),
    resultStats: document.getElementById('m9ResultStats'),
    share: document.getElementById('m9Share'),
    explain: document.getElementById('m9Explain'),
    practice: document.getElementById('m9Practice')
  };

  var RING = 2 * Math.PI * 23;

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  // ---------- 시각 단서 카드 모형(SVG) ----------
  function visualSvg(kind) {
    var line = 'stroke="currentColor" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"';
    var box = '<rect x="6" y="6" width="60" height="34" rx="4" ' + line + ' opacity="0.55"></rect>';
    var body = '';
    if (kind === 'phone') {
      body = '<rect x="24" y="4" width="24" height="38" rx="4" ' + line + '></rect>' +
        '<rect x="28" y="9" width="16" height="22" rx="1.6" ' + line + ' opacity="0.7"></rect>' +
        '<path d="M32 35h8" ' + line + '></path>';
    } else if (kind === 'receipt' || kind === 'card') {
      body = '<path d="M26 5h20v36l-4-3-4 3-4-3-4 3-4-3z" ' + line + '></path>' +
        '<path d="M31 13h10M31 18h10M31 23h6" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'locker') {
      body = '<rect x="14" y="6" width="44" height="34" rx="3" ' + line + '></rect>' +
        '<path d="M26 6v34M38 6v34M50 6v34" ' + line + ' opacity="0.7"></path>' +
        '<circle cx="22" cy="23" r="1.6" fill="currentColor"></circle>' +
        '<circle cx="34" cy="23" r="1.6" fill="currentColor"></circle>';
    } else if (kind === 'door') {
      body = '<rect x="16" y="4" width="40" height="38" rx="3" ' + line + '></rect>' +
        '<path d="M22 8h16v12h-16z" ' + line + ' opacity="0.7"></path>' +
        '<circle cx="48" cy="24" r="2" fill="currentColor"></circle>';
    } else if (kind === 'memo') {
      body = '<path d="M20 5h32v34l-7-4H20z" ' + line + '></path>' +
        '<path d="M26 13h20M26 19h20M26 25h12" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'cctv') {
      body = '<rect x="10" y="18" width="26" height="13" rx="3" ' + line + '></rect>' +
        '<path d="M36 22l10-5v16l-10-5" ' + line + '></path>' +
        '<path d="M18 31v9M30 31v9" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'chat') {
      body = '<path d="M10 10h34a4 4 0 0 1 4 4v13a4 4 0 0 1-4 4H26l-9 7v-7h-3a4 4 0 0 1-4-4V14a4 4 0 0 1 4-4z" ' + line + '></path>' +
        '<path d="M17 18h24M17 24h16" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'clock') {
      body = '<circle cx="36" cy="23" r="17" ' + line + '></circle>' +
        '<path d="M36 13v10l7 5" ' + line + '></path>';
    } else if (kind === 'parcel') {
      body = '<path d="M36 6l22 10v18L36 44 14 34V16z" ' + line + '></path>' +
        '<path d="M14 16l22 10 22-10M36 26v18" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'laundry') {
      body = '<path d="M36 8a6 6 0 0 1 6 6h6l-4 22a6 6 0 0 1-6 5H30a6 6 0 0 1-6-5l-4-22h6a6 6 0 0 1 6-6z" ' + line + '></path>' +
        '<path d="M30 20c4 0 6 3 6 6s2 6 6 6" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'bike') {
      body = '<circle cx="22" cy="32" r="9" ' + line + '></circle>' +
        '<circle cx="52" cy="32" r="9" ' + line + '></circle>' +
        '<path d="M22 32l9-14h9l8 14M31 18h10" ' + line + '></path>';
    } else if (kind === 'book') {
      body = '<path d="M14 9h18a4 4 0 0 1 4 4v26H18a4 4 0 0 1-4-4z" ' + line + '></path>' +
        '<path d="M40 9h18v26H40" ' + line + ' opacity="0.7"></path>' +
        '<path d="M20 16h10M20 22h10" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'calendar') {
      body = '<rect x="16" y="9" width="40" height="32" rx="3" ' + line + '></rect>' +
        '<path d="M16 17h40M26 5v8M46 5v8" ' + line + '></path>' +
        '<rect x="24" y="24" width="8" height="7" ' + line + ' opacity="0.7"></rect>';
    } else if (kind === 'meter') {
      body = '<rect x="18" y="8" width="36" height="32" rx="4" ' + line + '></rect>' +
        '<circle cx="36" cy="23" r="9" ' + line + ' opacity="0.7"></circle>' +
        '<path d="M36 23l5-5M24 36h24" ' + line + ' opacity="0.7"></path>';
    } else if (kind === 'key') {
      body = '<circle cx="26" cy="20" r="9" ' + line + '></circle>' +
        '<path d="M32 26l14 14M40 34l5-5M45 39l4-4" ' + line + '></path>';
    } else {
      body = box + '<path d="M14 28h44" ' + line + ' opacity="0.7"></path>';
    }
    return '<svg viewBox="0 0 72 46" aria-hidden="true" style="color:var(--text-secondary)">' + body + '</svg>';
  }

  // ---------- 사건 그리기 ----------
  function setCase(caseItem, isDaily) {
    stopTimer();
    state.caseItem = caseItem;
    state.isDaily = isDaily;
    state.phase = 'idle';
    state.entered = [];
    state.picked = -1;
    state.hints = 0;
    state.remaining = LIMIT;
    state.result = null;

    els.title.textContent = caseItem.title;
    els.brief.textContent = caseItem.brief;
    els.where.textContent = caseItem.where;
    els.level.textContent = caseItem.level;
    els.kind.textContent = caseItem.type === 'order' ? '순서 배열' : '원인 선택';
    els.dailyTag.textContent = isDaily ? '오늘의 사건' : '연습 사건';
    els.dailyTag.className = isDaily ? 'is-daily' : '';
    els.result.hidden = true;
    els.status.textContent = '';
    els.startWrap.hidden = false;
    els.submit.disabled = true;
    els.hint.disabled = false;
    els.timerTitle.textContent = '시작을 누르면 ' + LIMIT + '초가 흐릅니다';
    els.timerSub.textContent = '힌트 0개 · 제출 전';
    els.cardsLabel.textContent = caseItem.type === 'order'
      ? '단서 카드 · 탭해서 순서대로 담기'
      : '단서 카드 · 읽고 아래에서 원인 선택';
    renderClock(LIMIT);
    renderCards();
    renderAnswerArea();
    renderStats();
    Array.prototype.forEach.call(els.practice.querySelectorAll('.m9-practice-item'), function (btn) {
      btn.classList.toggle('is-current', btn.dataset.case === caseItem.id);
    });
  }

  function renderClock(remaining) {
    var value = Math.max(0, remaining);
    els.timer.textContent = value >= 10 ? String(Math.ceil(value)) : value.toFixed(1);
    var ratio = Math.max(0, Math.min(1, value / LIMIT));
    els.ring.setAttribute('stroke-dashoffset', String((RING * (1 - ratio)).toFixed(2)));
    var low = value <= 20;
    els.clock.classList.toggle('is-low', low);
    els.clock.setAttribute('aria-label', '남은 시간 ' + Math.ceil(value) + '초');
  }

  function renderCards() {
    var caseItem = state.caseItem;
    els.cards.innerHTML = '';
    caseItem.display.forEach(function (stepIndex) {
      var step = caseItem.steps[stepIndex];
      var card = el('button', 'm9-card');
      card.type = 'button';
      card.dataset.index = String(stepIndex);
      var visual = el('div', 'm9-visual');
      visual.innerHTML = visualSvg(step.visual);
      card.appendChild(visual);
      card.appendChild(el('span', 'm9-card-tag', step.tag));
      card.appendChild(el('span', 'm9-card-text', step.text));
      var no = el('span', 'm9-card-pickno', '');
      no.hidden = true;
      card.appendChild(no);
      if (caseItem.type === 'order') {
        card.setAttribute('aria-pressed', 'false');
      }
      els.cards.appendChild(card);
    });
  }

  function renderAnswerArea() {
    var caseItem = state.caseItem;
    if (caseItem.type === 'order') {
      els.tray.hidden = false;
      els.choices.hidden = true;
      renderTray();
    } else {
      els.tray.hidden = true;
      els.choices.hidden = false;
      renderChoices();
    }
  }

  function renderTray() {
    var caseItem = state.caseItem;
    els.tray.innerHTML = '';
    for (var i = 0; i < caseItem.steps.length; i += 1) {
      var slot = el('div', 'm9-slot');
      slot.appendChild(el('span', 'm9-slot-no', String(i + 1)));
      var stepIndex = state.entered[i];
      var text = el('span', 'm9-slot-text', stepIndex === undefined ? '여기에 ' + (i + 1) + '번째 단서' : caseItem.steps[stepIndex].text);
      slot.appendChild(text);
      if (stepIndex !== undefined) {
        slot.classList.add('is-filled');
        if (state.phase === 'done') {
          var correctAt = caseItem.display[i];
          slot.classList.add(correctAt === stepIndex ? 'is-ok' : 'is-ng');
        }
        if (state.phase !== 'done') {
          var remove = el('button', 'm9-slot-remove', '×');
          remove.type = 'button';
          remove.dataset.remove = String(i);
          remove.setAttribute('aria-label', (i + 1) + '번째 단서 빼기');
          slot.appendChild(remove);
        }
      }
      els.tray.appendChild(slot);
    }
    els.submit.disabled = state.phase !== 'playing' || state.entered.length !== caseItem.steps.length;
  }

  function renderChoices() {
    var caseItem = state.caseItem;
    els.choices.innerHTML = '';
    caseItem.choices.forEach(function (text, index) {
      var btn = el('button', 'm9-choice');
      btn.type = 'button';
      btn.dataset.choice = String(index);
      btn.appendChild(el('span', 'm9-choice-no', String(index + 1)));
      btn.appendChild(el('span', '', text));
      if (state.picked === index) btn.classList.add('is-picked');
      if (state.phase === 'done') {
        if (index === caseItem.answer) btn.classList.add('is-true');
        else if (index === state.picked) btn.classList.add('is-false');
        btn.disabled = true;
      }
      els.choices.appendChild(btn);
    });
    els.submit.disabled = state.phase !== 'playing' || state.picked < 0;
  }

  function markCards() {
    var caseItem = state.caseItem;
    Array.prototype.forEach.call(els.cards.querySelectorAll('.m9-card'), function (card) {
      var stepIndex = Number(card.dataset.index);
      var no = card.querySelector('.m9-card-pickno');
      var pos = state.entered.indexOf(stepIndex);
      if (pos >= 0 && state.phase !== 'done') {
        card.classList.add('is-picked');
        no.hidden = false;
        no.textContent = String(pos + 1);
      } else if (pos >= 0) {
        card.classList.add('is-picked');
        no.hidden = false;
        no.textContent = String(pos + 1);
      } else {
        card.classList.remove('is-picked');
        no.hidden = true;
      }
      if (state.phase === 'done') {
        card.disabled = true;
        if (caseItem.type === 'order') {
          var correctPos = caseItem.display.indexOf(stepIndex);
          var placed = state.entered[correctPos];
          card.classList.add(placed === stepIndex ? 'is-true' : 'is-false');
        }
      } else if (state.phase === 'idle') {
        card.classList.add('is-locked');
      } else {
        card.classList.remove('is-locked');
      }
    });
  }

  // ---------- 타이머 ----------
  function stopTimer() {
    if (state.timer) { window.clearInterval(state.timer); state.timer = null; }
  }
  function tick() {
    if (state.phase !== 'playing') return;
    var now = Date.now();
    var remaining = Math.max(0, (state.deadline - now) / 1000);
    state.remaining = remaining;
    renderClock(remaining);
    if (remaining <= 0) {
      stopTimer();
      finish(true);
    }
  }
  function startTimer() {
    if (state.phase !== 'playing') return;
    stopTimer();
    tick();
    state.timer = window.setInterval(tick, 100);
  }

  function setPhasePlaying() {
    if (state.phase === 'done') return;
    state.phase = 'playing';
    state.startedAt = Date.now();
    state.deadline = state.startedAt + LIMIT * 1000;
    state.remaining = LIMIT;
    els.startWrap.hidden = true;
    els.timerTitle.textContent = '사건을 읽고 순서를 맞추세요';
    els.timerSub.textContent = '힌트 0개 · 제출 전';
    els.status.textContent = '';
    renderClock(LIMIT);
    markCards();
    renderAnswerArea();
    startTimer();
  }

  // ---------- 힌트 ----------
  function useHint() {
    if (state.phase !== 'playing') {
      els.status.textContent = '시작을 누른 뒤에 힌트를 쓸 수 있습니다.';
      return;
    }
    state.hints += 1;
    state.deadline -= HINT_PENALTY * 1000;
    var remaining = Math.max(0, (state.deadline - Date.now()) / 1000);
    state.remaining = remaining;
    renderClock(remaining);
    els.timerSub.textContent = '힌트 ' + state.hints + '개 · 남은 시간 ' + HINT_PENALTY + '초 차감';
    els.status.textContent = '힌트: ' + state.caseItem.hint;
    if (remaining <= 0) { stopTimer(); finish(true); }
  }

  // ---------- 제출 · 채점 ----------
  function currentCorrect() {
    var caseItem = state.caseItem;
    if (caseItem.type === 'pick') return state.picked === caseItem.answer;
    if (state.entered.length !== caseItem.steps.length) return false;
    for (var i = 0; i < caseItem.steps.length; i += 1) {
      if (state.entered[i] !== caseItem.display[i]) return false;
    }
    return true;
  }

  function scoreOf(correct, remaining, hints) {
    if (!correct) return 0;
    return Math.max(0, Math.round(60 + Math.min(45, remaining * 0.5) - hints * 8));
  }

  function resultLine(result) {
    return '90초 생활 추리 · ' + kstDateString(new Date()) + '\n' +
      '"' + state.caseItem.title + '" · ' + (result.correct ? '정답' : '아쉬움') + '\n' +
      '남은 시간 ' + Math.round(result.remaining) + '초 · 힌트 ' + result.hints + '개 · ' + result.points + '점\n' +
      '연속 ' + record.streak + '일 · 해결 ' + record.solved + '건';
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(function () {});
    }
  }

  function finish(timeout) {
    if (state.phase === 'done') return;
    var caseItem = state.caseItem;
    var correct = !timeout && currentCorrect();
    var remaining = timeout ? 0 : Math.max(0, (state.deadline - Date.now()) / 1000);
    state.remaining = remaining;
    state.phase = 'done';
    stopTimer();
    var result = {
      correct: correct,
      timeout: !!timeout,
      remaining: remaining,
      hints: state.hints,
      points: scoreOf(correct, remaining, state.hints)
    };
    state.result = result;
    settle(caseItem.id, result);
    renderStats();

    els.result.hidden = false;
    els.result.className = 'm9-result ' + (correct ? 'is-correct' : 'is-wrong');
    els.badge.textContent = correct ? '정답' : '아쉬움';
    els.resultTitle.textContent = correct ? '정답입니다 · ' + result.points + '점' : (timeout ? '시간이 끝났습니다' : '정답과 다릅니다');
    els.resultSub.textContent = correct
      ? '남은 ' + Math.round(remaining) + '초 · 힌트 ' + result.hints + '개로 해결했습니다.'
      : (caseItem.type === 'order' ? '아래 초록 칸이 정답 순서입니다. 해설을 읽고 연습으로 다시 해 보세요.'
        : '초록으로 표시된 보기가 정답입니다. 해설을 읽고 연습으로 다시 해 보세요.');
    els.resultStats.innerHTML = '';
    els.resultStats.appendChild(el('span', '', '남은 시간 ' + Math.round(remaining) + '초'));
    els.resultStats.appendChild(el('span', '', '힌트 ' + result.hints + '개'));
    els.resultStats.appendChild(el('span', '', '연속 ' + record.streak + '일'));
    els.share.textContent = resultLine(result);
    els.explain.textContent = '';
    var label = el('b', '', '해설 · ');
    els.explain.appendChild(label);
    els.explain.appendChild(document.createTextNode(caseItem.explain));

    renderClock(remaining);
    els.timerTitle.textContent = correct ? '해결했습니다' : '결과를 확인하세요';
    els.timerSub.textContent = '힌트 ' + result.hints + '개 · 제출 완료';
    els.submit.disabled = true;
    els.hint.disabled = true;
    els.status.textContent = '결과 문구를 복사했습니다. 같은 사건은 다시 풀어도 기록은 한 번만 남습니다.';
    markCards();
    renderAnswerArea();
    copyText(resultLine(result));
  }

  // ---------- 이벤트 ----------
  els.cards.addEventListener('click', function (event) {
    var card = event.target.closest ? event.target.closest('.m9-card') : null;
    if (!card || state.phase !== 'playing') return;
    var stepIndex = Number(card.dataset.index);
    if (state.caseItem.type !== 'order') return;
    var pos = state.entered.indexOf(stepIndex);
    if (pos >= 0) state.entered.splice(pos, 1);
    else state.entered.push(stepIndex);
    renderTray();
    markCards();
  });

  els.tray.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('.m9-slot-remove') : null;
    if (!btn || state.phase !== 'playing') return;
    state.entered.splice(Number(btn.dataset.remove), 1);
    renderTray();
    markCards();
  });

  els.choices.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('.m9-choice') : null;
    if (!btn || state.phase !== 'playing') return;
    state.picked = Number(btn.dataset.choice);
    renderChoices();
  });

  els.start.addEventListener('click', setPhasePlaying);
  els.hint.addEventListener('click', useHint);
  els.submit.addEventListener('click', function () {
    if (state.phase !== 'playing') return;
    finish(false);
  });
  els.restart.addEventListener('click', function () {
    setCase(state.caseItem, state.isDaily);
  });

  els.practice.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('.m9-practice-item') : null;
    if (!btn) return;
    var caseItem = BY_ID[btn.dataset.case];
    if (!caseItem) return;
    setCase(caseItem, false);
    if (window.innerWidth <= 900) {
      var target = document.getElementById('m9CaseTitle');
      if (target && target.scrollIntoView) target.scrollIntoView({ block: 'start', behavior: reduceMotion ? 'auto' : 'smooth' });
    }
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) return;
  });

  // ---------- 시작 ----------
  var dailyCase = BY_ID[DATA.daily] || CASES[0];
  var todayString = kstDateString(new Date());
  var dailyIsToday = DATA.date === todayString;
  var caseForNow = dailyCase;
  if (!dailyIsToday) {
    // 빌드한 날짜와 오늘(KST)이 다르면 날짜 시드로 다시 고른다.
    var epoch = Math.floor(Date.UTC(1970, 0, 1) / 86400000);
    var now = new Date();
    var p = kstParts(now);
    var dayNumber = Math.floor(Date.UTC(p.y, p.m - 1, p.d) / 86400000);
    var pool = CASES.slice(0, DATA.cases.length);
    caseForNow = pool[(dayNumber - epoch) % pool.length];
  }
  setCase(caseForNow, dailyIsToday);

  // 테스트·디버깅용
  window.MYSTERY90 = {
    data: DATA,
    state: state,
    case: function () { return state.caseItem; },
    start: function () { els.start.click(); },
    pickCard: function (stepIndex) {
      var card = els.cards.querySelector('[data-index="' + stepIndex + '"]');
      if (card) card.click();
    },
    answerOrder: function () {
      // 정답 순서로 담는다(테스트·연습용).
      state.entered = state.caseItem.display.slice();
      renderTray();
      markCards();
    },
    pickChoice: function (index) {
      var btn = els.choices.querySelector('[data-choice="' + index + '"]');
      if (btn) btn.click();
    },
    enter: function (list) {
      state.entered = (list || []).slice();
      renderTray();
      markCards();
    },
    submit: function () { els.submit.click(); },
    hint: function () { els.hint.click(); },
    finishNow: function () { finish(true); },
    result: function () { return state.result; }
  };
})();
"""


if __name__ == "__main__":
    build()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘의 지하철역 맞히기(subway.html).

무엇을 하나
  · subway_data.json(서울 25개 구 실제 지하철역 306곳 — 역명·자치구·좌표·노선)으로
    KST 날짜 시드 데일리 퍼즐을 낸다. 같은 날은 모두 같은 역, 306일 동안 같은 역이 다시 나오지 않는다.
  · 6회 안에 오늘의 역을 맞힌다. 추측할 때마다
      - 역명 글자: 같은 자리 글자(진한 칩) / 다른 자리에 있는 글자(옅은 칩) / 없는 글자
      - 노선: 추측한 역의 노선 칩을 정답 노선이면 노선 색으로 채워 표시 + 노선 수 비교
      - 환승: 연계 노선 수 비교(같음 · 많음 · 적음)
      - 권역: 자치구 일치 여부
      - 방향·거리: 정답이 이 역에서 어느 방향으로 몇 km 떨어졌는지(실제 좌표 계산)
      - 초성: 정답 역명의 초성을 보여 주고, 지금까지 맞힌 글자는 드러낸다
    를 한 줄에 모아 보여 준다.
  · 1회 자동 재생 후 멈추는 3단계 가이드(`다시 보기`), prefers-reduced-motion 에서는 정지 상태로 시작.
  · 연속 스트릭·최고 기록 localStorage 저장(`secjobs-subway-v1`), 스포일러 없는 결과 그리드 복사.

지키는 것
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 퍼즐 + 우측 기록 레일 / 모바일(390px) 입력·시도 기록이 첫 화면에 들어오게
  · 좌표·노선·자치구는 subway_data.json 값만 쓴다. 화면에서 만들어 넣는 값은 방향·거리·글자 비교뿐이고
    모두 실제 좌표·역명에서 계산한다.
"""
import json
import math
import os
from datetime import date, datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "subway_data.json")
OUT_HTML = os.path.join(BASE_DIR, "subway.html")
KST = timezone(timedelta(hours=9))

MAX_TRIES = 6
EPOCH = date(1970, 1, 1)
SEOUL_GU = set(
    "종로구 중구 용산구 성동구 광진구 동대문구 중랑구 성북구 강북구 도봉구 노원구 은평구 서대문구 마포구 "
    "양천구 강서구 구로구 금천구 영등포구 동작구 관악구 서초구 강남구 송파구 강동구".split()
)


# ---------------------------------------------------------------------------
# 데이터
# ---------------------------------------------------------------------------
def load_data(path=None):
    with open(path or DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)
    stations = data.get("stations") or []
    if len(stations) < 200:
        raise SystemExit("subway_data.json 역이 %d곳뿐입니다(최소 200곳)." % len(stations))
    names = [station["name"] for station in stations]
    if len(set(names)) != len(names):
        raise SystemExit("subway_data.json 에 같은 이름의 역이 있습니다")
    known = {line["name"] for line in data["lines"]}
    for station in stations:
        if station["area"] not in SEOUL_GU:
            raise SystemExit("%s 자치구가 서울 25개 구가 아닙니다: %r" % (station["name"], station["area"]))
        if not station["lines"] or any(line not in known for line in station["lines"]):
            raise SystemExit("%s 노선 정보가 잘못되었습니다: %r" % (station["name"], station["lines"]))
        if not (37.42 <= station["lat"] <= 37.72 and 126.75 <= station["lng"] <= 127.20):
            raise SystemExit("%s 좌표가 서울 범위를 벗어났습니다" % station["name"])
    deck = data.get("deck") or []
    if sorted(deck) != sorted(names):
        raise SystemExit("deck 과 stations 가 어긋났습니다")
    return data


# ---------------------------------------------------------------------------
# 퍼즐 (화면과 같은 규칙)
# ---------------------------------------------------------------------------
def day_index(day):
    """1970-01-01 부터 며칠째인지 — deck 순환 위치."""
    return (day - EPOCH).days


def answer_for(data, day):
    """그날의 정답 역 이름."""
    return data["deck"][day_index(day) % len(data["deck"])]


def bearing_words(lat1, lng1, lat2, lng2):
    """추측 → 정답 방향(8방위)과 거리(km). 실제 좌표에서 계산한다."""
    dlat = lat2 - lat1
    dlng = (lng2 - lng1) * math.cos(math.radians((lat1 + lat2) / 2))
    distance = math.hypot(dlat * 111.32, dlng * 111.32)
    angle = (math.degrees(math.atan2(dlng, dlat)) + 360) % 360
    words = ["북", "북동", "동", "남동", "남", "남서", "서", "북서"]
    return words[int((angle + 22.5) // 45) % 8], distance


def syllable_state(guess, answer):
    """역명 글자 비교 — 자리까지 맞으면 hit, 다른 자리에 있으면 near, 없으면 miss."""
    guess_chars = list(guess)
    answer_chars = list(answer)
    remaining = {}
    for index, char in enumerate(answer_chars):
        if index < len(guess_chars) and guess_chars[index] == char:
            continue
        remaining[char] = remaining.get(char, 0) + 1
    result = []
    for index, char in enumerate(guess_chars):
        if index < len(answer_chars) and char == answer_chars[index]:
            result.append("hit")
        elif remaining.get(char):
            remaining[char] -= 1
            result.append("near")
        else:
            result.append("miss")
    return result


CHOSUNG = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ",
        "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]


def chosung(text):
    """한글 초성 추출 — 자동완성 검색과 초성 힌트에 쓴다."""
    out = []
    for char in text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            out.append(CHOSUNG[(code - 0xAC00) // 588])
        else:
            out.append(char)
    return "".join(out)


def grade(attempts, solved):
    """결과 요약 — 공유 문구에 쓰는 등급."""
    if not solved:
        return "아쉬움"
    if len(attempts) == 1:
        return "완벽"
    if len(attempts) <= 3:
        return "빠름"
    return "정답"


def build(out_path=None, today=None):
    data = load_data()
    today = today or datetime.now(KST).date()
    answer = answer_for(data, today)
    answer_station = next(station for station in data["stations"] if station["name"] == answer)

    payload = dict(data)
    payload["meta"] = {
        "answer": answer,
        "answerDate": today.isoformat(),
        "maxTries": MAX_TRIES,
        "dayIndex": day_index(today),
        "answerLines": answer_station["lines"],
        "answerArea": answer_station["area"],
        "answerChosung": chosung(answer),
    }
    payload["build"] = {
        "pythonDayIndex": day_index(today),
        "answerIndex": day_index(today) % len(data["deck"]),
    }
    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__ANSWER__", answer)
            .replace("__CHECKED__", data["checkedOn"])
            .replace("__COUNT__", str(len(data["stations"])))
            .replace("__LINES__", str(len(data["lines"])))
            .replace("__DATA_JSON__", safe_json_for_script(json.dumps(payload, ensure_ascii=False,
                                                                      separators=(",", ":"))))
            .replace("__JS__", JS))

    with open(out_path or OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "subway")))

    print("-> 'subway.html' 생성 완료 (역 %d곳 · %s 정답 %s · 노선 %d종)"
          % (len(data["stations"]), today.isoformat(), answer, len(data["lines"])))
    return {"stations": len(data["stations"]), "answer": answer, "date": today.isoformat()}


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
      --hit-bg: #0f766e;  --hit-text: #ffffff;  --hit-soft: #ecfdf5;  --hit-border: #a7f3d0;  --hit-ink: #047857;
      --near-bg: #fffbeb;  --near-text: #b45309;  --near-border: #fde68a;
      --miss-bg: #f8fafc;  --miss-text: #94a3b8;  --miss-border: #e2e8f0;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --hit-bg: #0d9488;  --hit-text: #ffffff;  --hit-soft: rgba(16, 185, 129, 0.14);
      --hit-border: rgba(16, 185, 129, 0.34);  --hit-ink: #6ee7b7;
      --near-bg: rgba(245, 158, 11, 0.14);  --near-text: #fcd34d;  --near-border: rgba(245, 158, 11, 0.34);
      --miss-bg: #18181b;  --miss-text: #71717a;  --miss-border: #27272a;
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body { font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease; }
    .sw-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .sw-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 96px; }
    .sw-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .sw-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 640px; word-break: keep-all; }
    .sw-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .sw-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px;
      font-size: 11.5px; color: var(--text-muted); }
    .sw-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }

    .sw-main { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 16px; margin-top: 16px; align-items: start; }
    .sw-main > * { min-width: 0; }
    .sw-panel { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 18px; box-shadow: var(--card-shadow); }
    .sw-panel h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); }

    /* ---------- 입력 ---------- */
    .sw-play { padding: 18px; }
    .sw-play-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .sw-tries { display: flex; gap: 5px; }
    .sw-try-dot { width: 20px; height: 6px; border-radius: 3px; background: var(--bg-muted); }
    .sw-try-dot.is-used { background: var(--text-secondary); }
    .sw-try-dot.is-win { background: var(--hit-bg); }
    .sw-try-dot.is-lose { background: var(--near-text); }
    .sw-mode { display: inline-flex; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 10px; }
    .sw-mode button { border: 0; background: transparent; color: var(--text-secondary); cursor: pointer;
      font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 5px 10px; border-radius: 7px; }
    .sw-mode button.is-on { background: var(--bg-surface); color: var(--text-primary); box-shadow: var(--card-shadow); }
    .sw-mode button:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .sw-input-wrap { position: relative; margin-top: 13px; }
    .sw-input-row { display: flex; gap: 8px; }
    .sw-input { flex: 1 1 auto; min-width: 0; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-primary); border-radius: 12px; padding: 13px 14px; font-family: inherit; font-size: 16px;
      font-weight: 700; letter-spacing: -0.01em; }
    .sw-input::placeholder { color: var(--text-muted); font-weight: 600; }
    .sw-input:focus { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .sw-submit { flex: 0 0 auto; border: 1px solid var(--text-primary); background: var(--text-primary);
      color: var(--bg-surface); border-radius: 12px; padding: 0 18px; font-family: inherit; font-size: 13px;
      font-weight: 700; cursor: pointer; }
    .sw-submit:disabled { opacity: .4; cursor: default; }
    .sw-submit:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .sw-suggest { position: absolute; left: 0; right: 0; top: calc(100% + 5px); z-index: 20; background: var(--bg-surface);
      border: 1px solid var(--border-default); border-radius: 12px; box-shadow: 0 10px 24px -12px rgba(15, 23, 42, 0.28);
      overflow: hidden; max-height: 268px; overflow-y: auto; }
    .sw-suggest button { display: flex; align-items: center; gap: 8px; width: 100%; border: 0; background: transparent;
      color: var(--text-primary); text-align: left; padding: 9px 12px; font-family: inherit; font-size: 13.5px;
      font-weight: 700; cursor: pointer; }
    .sw-suggest button:hover, .sw-suggest button.is-active { background: var(--bg-subtle); }
    .sw-suggest button span { margin-left: auto; font-size: 10.5px; font-weight: 600; color: var(--text-muted); }
    .sw-suggest .sw-empty { padding: 11px 12px; font-size: 12px; color: var(--text-muted); }
    .sw-input-hint { margin-top: 7px; font-size: 11px; color: var(--text-muted); }

    /* ---------- 시도 기록 ---------- */
    .sw-head { display: grid; grid-template-columns: 96px minmax(0, 1.5fr) 56px 68px 62px minmax(80px, 1fr) 66px;
      gap: 6px; margin-top: 16px; padding: 0 2px; font-size: 10px; font-weight: 700; color: var(--text-muted); }
    .sw-head span { text-align: center; }
    .sw-head span:first-child { text-align: left; }
    .sw-rows { margin-top: 6px; display: grid; gap: 6px; }
    .sw-row { display: grid; grid-template-columns: 96px minmax(0, 1.5fr) 56px 68px 62px minmax(80px, 1fr) 66px;
      gap: 6px; align-items: stretch; }
    .sw-cell { display: flex; align-items: center; justify-content: center; min-height: 44px; border-radius: 10px;
      border: 1px solid var(--border-default); background: var(--bg-surface); font-size: 11.5px; font-weight: 700;
      color: var(--text-secondary); padding: 3px 4px; }
    .sw-cell.is-answer { border-color: var(--hit-border); background: var(--hit-soft); color: var(--hit-ink); }
    .sw-cell.is-hit { background: var(--hit-bg); border-color: var(--hit-bg); color: var(--hit-text); }
    .sw-cell.is-near { background: var(--near-bg); border-color: var(--near-border); color: var(--near-text); }
    .sw-cell.is-miss { background: var(--miss-bg); border-color: var(--miss-border); color: var(--miss-text); }
    .sw-name-cell { justify-content: flex-start; gap: 2px; padding: 3px 6px; font-size: 12.5px; flex-wrap: wrap; }
    .sw-char { display: inline-flex; align-items: center; justify-content: center; min-width: 17px; height: 23px;
      padding: 0 2px; border-radius: 5px; background: var(--bg-subtle); color: var(--text-secondary); }
    .sw-char.is-hit { background: var(--hit-bg); color: var(--hit-text); }
    .sw-char.is-near { background: var(--near-bg); color: var(--near-text); box-shadow: inset 0 0 0 1px var(--near-border); }
    .sw-chips { display: flex; flex-wrap: wrap; gap: 3px; justify-content: center; width: 100%; }
    .sw-chip { display: inline-flex; align-items: center; justify-content: center; min-width: 20px; height: 20px;
      padding: 0 5px; border-radius: 6px; font-size: 10.5px; font-weight: 800; background: var(--bg-subtle);
      color: var(--text-muted); border: 1px solid var(--border-default); }
    .sw-chip.is-on { color: #fff; border-color: transparent; }
    .sw-num { font-size: 15px; font-weight: 800; font-variant-numeric: tabular-nums; }
    .sw-arrow-up { color: var(--near-text); }
    .sw-arrow-down { color: var(--accent-primary); }
    .sw-dir { display: inline-flex; align-items: center; gap: 4px; font-size: 11.5px; font-weight: 700; }
    .sw-dir svg { width: 13px; height: 13px; }
    .sw-dir b { font-size: 11.5px; font-weight: 800; font-variant-numeric: tabular-nums; }
    .sw-empty-row { border: 1px dashed var(--border-strong); border-radius: 10px; min-height: 44px;
      display: flex; align-items: center; justify-content: center; font-size: 11.5px; color: var(--text-muted); }

    /* ---------- 초성 힌트 · 결과 ---------- */
    .sw-hint { margin-top: 16px; border: 1px solid var(--border-default); border-radius: 14px; padding: 12px 14px;
      background: var(--bg-subtle); }
    .sw-hint-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .sw-hint-head h3 { font-size: 11px; font-weight: 700; color: var(--text-muted); }
    .sw-hint-head span { font-size: 10.5px; color: var(--text-muted); }
    .sw-blanks { display: flex; gap: 5px; margin-top: 8px; flex-wrap: wrap; }
    .sw-blank { min-width: 30px; height: 34px; padding: 0 6px; border-radius: 8px; background: var(--bg-surface);
      border: 1px solid var(--border-default); display: inline-flex; align-items: center; justify-content: center;
      font-size: 13px; font-weight: 800; color: var(--text-muted); }
    .sw-blank.is-revealed { color: var(--text-primary); border-color: var(--border-strong); }
    .sw-blank.is-correct { background: var(--hit-soft); border-color: var(--hit-border); color: var(--hit-ink); }

    .sw-result { margin-top: 16px; border: 1px solid var(--border-default); border-radius: 14px; padding: 15px;
      background: var(--bg-surface); }
    .sw-result.is-win { border-color: var(--hit-border); background: var(--hit-soft); }
    .sw-result.is-lose { border-color: var(--near-border); background: var(--near-bg); }
    .sw-result-top { display: flex; align-items: center; gap: 8px; }
    .sw-result-badge { font-size: 11px; font-weight: 800; border-radius: 999px; padding: 3px 9px;
      background: var(--bg-surface); border: 1px solid var(--border-strong); color: var(--text-secondary); }
    .sw-result h3 { font-size: 17px; font-weight: 800; letter-spacing: -0.03em; }
    .sw-result p { margin-top: 6px; font-size: 12px; color: var(--text-secondary); word-break: keep-all; }
    .sw-answer-line { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
    .sw-result-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .sw-btn { border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      border-radius: 10px; padding: 8px 13px; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }
    .sw-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .sw-btn:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .sw-btn.sw-primary { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }
    .sw-status { min-height: 16px; margin-top: 8px; font-size: 11px; font-weight: 600; color: var(--hit-ink); }
    .sw-share { margin-top: 10px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px;
      line-height: 1.55; white-space: pre-wrap; color: var(--text-secondary); background: var(--bg-subtle);
      border: 1px solid var(--border-default); border-radius: 10px; padding: 10px 11px; }

    /* ---------- 가이드 ---------- */
    .sw-guide { margin-top: 12px; }
    .sw-guide-body { margin-top: 9px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
    .sw-step { border: 1px solid var(--border-default); border-radius: 12px; padding: 9px; background: var(--bg-subtle);
      transition: border-color .2s ease, background-color .2s ease, transform .2s ease; }
    .sw-step.is-on { border-color: var(--text-secondary); background: var(--bg-surface); transform: translateY(-2px); }
    .sw-step h4 { font-size: 10.5px; font-weight: 800; color: var(--text-secondary); }
    .sw-step p { margin-top: 4px; font-size: 10px; line-height: 1.45; color: var(--text-muted); word-break: keep-all; }
    .sw-stage { display: flex; align-items: center; justify-content: center; gap: 5px; height: 40px; margin-bottom: 4px; }
    .sw-g-chip { width: 15px; height: 15px; border-radius: 5px; background: var(--bg-muted);
      transition: background-color .35s ease, transform .35s ease; }
    .sw-step.is-on .sw-g-chip:nth-child(1) { background: #00A84D; transform: translateY(-2px); }
    .sw-step.is-on .sw-g-chip:nth-child(2) { background: #D4003B; transform: translateY(2px); }
    .sw-step.is-on .sw-g-chip:nth-child(3) { background: var(--bg-muted); }
    .sw-g-dir { width: 26px; height: 26px; color: var(--text-muted); transition: transform .5s cubic-bezier(0.2, 0.8, 0.2, 1), color .3s ease; }
    .sw-step.is-on .sw-g-dir { transform: rotate(45deg); color: var(--accent-primary); }
    .sw-g-tile { width: 22px; height: 26px; border-radius: 6px; background: var(--bg-muted); display: inline-flex;
      align-items: center; justify-content: center; font-size: 12px; font-weight: 800; color: transparent;
      transition: background-color .35s ease, color .35s ease; }
    .sw-step.is-on .sw-g-tile.is-hit { background: var(--hit-bg); color: #fff; }
    .sw-step.is-on .sw-g-tile.is-near { background: var(--near-bg); color: var(--near-text); box-shadow: inset 0 0 0 1px var(--near-border); }
    .sw-guide-foot { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
    .sw-guide-foot span { font-size: 10.5px; color: var(--text-muted); }
    .sw-replay { border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      border-radius: 8px; padding: 5px 10px; font-family: inherit; font-size: 11px; font-weight: 700; cursor: pointer; }
    .sw-replay:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    /* ---------- 레일 ---------- */
    .sw-rail { display: grid; gap: 12px; position: sticky; top: 76px; }
    .sw-stat { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 10px; }
    .sw-stat div { border: 1px solid var(--border-default); border-radius: 11px; padding: 9px 10px; background: var(--bg-subtle); }
    .sw-stat span { display: block; font-size: 10px; color: var(--text-muted); }
    .sw-stat b { display: block; margin-top: 2px; font-size: 18px; font-weight: 800; letter-spacing: -0.03em;
      font-variant-numeric: tabular-nums; white-space: nowrap; }
    .sw-stat b small { font-size: 11px; font-weight: 700; color: var(--text-muted); margin-left: 2px; }
    .sw-rail p { margin-top: 9px; font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .sw-rail p b { color: var(--text-primary); }
    .sw-practice { margin-top: 10px; width: 100%; }
    .sw-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .sw-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; color: var(--text-primary); }
    .sw-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .sw-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .sw-notes li b { color: var(--text-primary); }
    .sw-notes .sw-srcs { list-style: none; padding-left: 0; margin-top: 12px; padding-top: 11px;
      border-top: 1px solid var(--border-subtle); }
    .sw-notes .sw-srcs li { display: flex; flex-direction: column; gap: 1px; }
    .sw-notes .sw-srcs a { font-weight: 700; color: var(--accent-primary); text-decoration: none; font-size: 11.5px; }
    .sw-notes .sw-srcs span { font-size: 10.5px; color: var(--text-muted); }
    .sw-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 900px) {
      .sw-wrap { padding: 14px 13px 88px; }
      .sw-hero h1 { font-size: 21px; }
      .sw-hero p { font-size: 12px; }
      .sw-main { display: flex; flex-direction: column; align-items: stretch; gap: 10px; margin-top: 13px; }
      .sw-play { order: 1; padding: 14px; }
      .sw-rail { order: 2; position: static; width: 100%; }
      .sw-head { display: none; }
      .sw-row { min-width: 0; grid-template-columns: minmax(0, 1fr) 42px 50px 58px 44px;
        grid-template-areas: "name name name area csc" "lines lines num dir km"; gap: 5px; }
      .sw-row > .sw-cell:nth-child(1) { grid-area: name; }
      .sw-row > .sw-cell:nth-child(2) { grid-area: lines; }
      .sw-row > .sw-cell:nth-child(3) { grid-area: num; }
      .sw-row > .sw-cell:nth-child(4) { grid-area: area; }
      .sw-row > .sw-cell:nth-child(5) { grid-area: dir; }
      .sw-row > .sw-cell:nth-child(6) { grid-area: km; }
      .sw-row > .sw-cell:nth-child(7) { grid-area: csc; }
      .sw-name-cell { min-height: 38px; }
      .sw-input-row, .sw-input, .sw-suggest, .sw-hint, .sw-guide, .sw-rows { min-width: 0; max-width: 100%; }
      .sw-hero p, .sw-rail p, .sw-notes li { overflow-wrap: anywhere; }
      .sw-cell { min-height: 34px; font-size: 11px; }
      .sw-guide-body { grid-template-columns: minmax(0, 1fr); }
      .sw-step { display: flex; align-items: center; gap: 9px; }
      .sw-stage { height: 34px; margin-bottom: 0; }
      .sw-step > div:last-child { flex: 1 1 auto; }
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
  <title>Infosec Archive · 오늘의 지하철역</title>
  <meta name="description" content="서울 25개 구 실제 지하철역 __COUNT__곳 중 오늘의 역을 6회 안에 맞히는 데일리 퍼즐. 노선·환승·자치구·방향과 거리·초성 힌트를 한 줄씩 받아 좁혀 갑니다. 연습 모드와 연속 스트릭, 결과 복사가 있습니다.">
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
        <div class="update-meta"><span class="live-dot"></span><span>역 목록 확인 __CHECKED__</span></div>
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

  <main class="sw-wrap">
    <section class="sw-hero">
      <span class="sw-pill">게임 · 데일리 지하철역</span>
      <h1>오늘의 역은 어디일까</h1>
      <p>서울 25개 구 실제 지하철역 __COUNT__곳 중 오늘의 역을 6회 안에 맞힙니다. 노선·환승·자치구·방향과 거리·초성 힌트가 매번 좁혀 주니, 지하철을 자주 타는 사람에게 유리한 퍼즐입니다.</p>
      <div class="sw-meta">
        <span>서울 25개 구 · 역 __COUNT__곳</span>
        <span class="sw-dot"></span>
        <span>노선 __LINES__종</span>
        <span class="sw-dot"></span>
        <span>역 목록 확인 __CHECKED__</span>
      </div>
    </section>

    <div class="sw-main">
      <section class="sw-panel sw-play" aria-labelledby="swPlayTitle">
        <div class="sw-play-head">
          <div>
            <h2 id="swPlayTitle">오늘의 지하철역</h2>
          </div>
          <div class="sw-mode" role="group" aria-label="모드 선택">
            <button type="button" data-mode="daily" class="is-on" aria-pressed="true">오늘</button>
            <button type="button" data-mode="practice" aria-pressed="false">연습</button>
          </div>
        </div>

        <div class="sw-tries" id="swTries" role="img" aria-label="남은 시도"></div>

        <div class="sw-input-wrap">
          <div class="sw-input-row">
            <input class="sw-input" id="swInput" type="text" autocomplete="off" spellcheck="false"
                   placeholder="역 이름을 입력하세요 (예: 강남, ㄱㄴ)" aria-label="역 이름" aria-autocomplete="list"
                   aria-controls="swSuggest" aria-expanded="false" role="combobox">
            <button type="button" class="sw-submit" id="swSubmit">확인</button>
          </div>
          <div class="sw-suggest" id="swSuggest" role="listbox" aria-label="역 이름 제안" hidden></div>
          <p class="sw-input-hint" id="swHint">초성으로도 찾을 수 있습니다. 같은 역은 다시 넣을 수 없습니다.</p>
          <p class="sw-status" id="swInputStatus" role="status" aria-live="polite"></p>
        </div>

        <div class="sw-head" aria-hidden="true">
          <span>역명</span><span>노선</span><span>연계</span><span>자치구</span><span>방향</span><span>거리</span><span>초성</span>
        </div>
        <div class="sw-rows" id="swRows" role="list" aria-label="시도 기록"></div>

        <div class="sw-hint" id="swChosung">
          <div class="sw-hint-head">
            <h3>정답 초성</h3>
            <span id="swChosungNote">맞힌 글자는 드러납니다</span>
          </div>
          <div class="sw-blanks" id="swBlanks"></div>
        </div>

        <div class="sw-result" id="swResult" hidden>
          <div class="sw-result-top">
            <span class="sw-result-badge" id="swResultBadge">정답</span>
            <h3 id="swResultTitle">정답입니다</h3>
          </div>
          <p id="swResultText"></p>
          <div class="sw-answer-line" id="swAnswerLine"></div>
          <div class="sw-result-actions">
            <button type="button" class="sw-btn sw-primary" id="swCopy">결과 복사</button>
            <button type="button" class="sw-btn" id="swAgain">연습 한 판</button>
          </div>
          <p class="sw-status" id="swStatus" role="status" aria-live="polite"></p>
          <div class="sw-share" id="swShare"></div>
        </div>

        <section class="sw-guide" aria-labelledby="swGuideTitle">
          <div class="sw-hint-head">
            <h3 id="swGuideTitle">힌트 읽는 법 · 3단계</h3>
            <span id="swGuideNote">한 번 재생됩니다</span>
          </div>
          <div class="sw-guide-body" id="swGuideSteps">
            <div class="sw-step" data-step="1">
              <div class="sw-stage" aria-hidden="true">
                <span class="sw-g-chip"></span><span class="sw-g-chip"></span><span class="sw-g-chip"></span>
              </div>
              <div>
                <h4>1. 노선</h4>
                <p>추측한 역의 노선 칩이 정답 노선이면 그 노선 색으로 채워집니다.</p>
              </div>
            </div>
            <div class="sw-step" data-step="2">
              <div class="sw-stage" aria-hidden="true">
                <svg class="sw-g-dir" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V5"></path><path d="M6 11l6-6 6 6"></path></svg>
              </div>
              <div>
                <h4>2. 방향·거리</h4>
                <p>정답이 추측한 역에서 어느 방향으로 몇 km 떨어졌는지 화살표로 보여 줍니다.</p>
              </div>
            </div>
            <div class="sw-step" data-step="3">
              <div class="sw-stage" aria-hidden="true">
                <span class="sw-g-tile is-hit">강</span><span class="sw-g-tile is-near">남</span><span class="sw-g-tile">역</span>
              </div>
              <div>
                <h4>3. 초성·글자</h4>
                <p>정답 초성이 열리고, 자리까지 맞힌 글자는 진하게 표시됩니다.</p>
              </div>
            </div>
          </div>
          <div class="sw-guide-foot">
            <button type="button" class="sw-replay" id="swReplay">다시 보기</button>
            <span id="swGuideState">잠시 후 자동으로 재생됩니다</span>
          </div>
        </section>
      </section>

      <aside class="sw-rail" aria-label="기록과 안내">
        <section class="sw-panel">
          <h2>내 기록</h2>
          <div class="sw-stat">
            <div><span>연속 정답</span><b><span id="swStreak">0</span><small>일</small></b></div>
            <div><span>최고 기록</span><b><span id="swBest">0</span><small>일</small></b></div>
            <div><span>오늘 시도</span><b><span id="swTryCount">0</span><small>/6</small></b></div>
            <div><span>누적 정답</span><b><span id="swSolved">0</span><small>판</small></b></div>
          </div>
          <p id="swRecordNote">오늘 처음 열었습니다. 정답을 맞히면 연속 기록이 올라갑니다.</p>
          <button type="button" class="sw-btn sw-practice" id="swPracticeStart">연습 한 판 시작</button>
        </section>
        <section class="sw-panel">
          <h2>이렇게 풀면 빨라집니다</h2>
          <p><b>1수는 넓게</b> — 환승역을 넣으면 노선·연계·자치구를 한 번에 볼 수 있습니다.</p>
          <p><b>거리로 좁히기</b> — 방향과 km가 맞으면 그 방향에 있는 역만 남습니다.</p>
          <p><b>초성 확인</b> — 남은 후보가 몇 개 없을 때 초성과 글자 힌트가 결정적입니다.</p>
        </section>
      </aside>
    </div>

    <section class="sw-notes">
      <h2>알아 두실 점</h2>
      <ul>
        <li><b>범위</b> — 서울특별시 25개 구 안에 있는 역 __COUNT__곳이 정답 후보입니다. 경기·인천 역은 들어 있지 않습니다.</li>
        <li><b>매일 바뀌는 방식</b> — 역 목록을 섞은 순서를 날짜로 세어 하루에 한 곳씩 냅니다. __COUNT__일 동안 같은 역이 다시 나오지 않습니다.</li>
        <li><b>연계 노선 수</b> — 그 역에 들어오는 노선 수입니다. 1이면 단일 노선, 3이면 세 노선이 지나는 환승역입니다.</li>
        <li><b>방향·거리</b> — 두 역의 실제 위·경도로 계산한 직선 방향과 거리입니다. 지하철 이동 거리와는 다릅니다.</li>
        <li><b>역 목록의 성격</b> — 공개된 역 목록(CC0)과 위키데이터의 노선 정보를 대조해 정리했고, 확인일 __CHECKED__ 기준입니다. 노선이 바뀌면 목록도 함께 고칩니다.</li>
      </ul>
      <ul class="sw-srcs">
        <li><a href="https://www.wikidata.org/" target="_blank" rel="noopener noreferrer">위키데이터 — 서울 지하철역 위치·노선</a><span>역 좌표와 노선 정보 대조</span></li>
        <li><a href="https://gist.github.com/nemorize/ac5f39ff62b6bf82dc496d10c69b2b46" target="_blank" rel="noopener noreferrer">공개 지하철역 목록(CC0)</a><span>역명·자치구·좌표</span></li>
        <li><a href="https://www.seoulmetro.co.kr/kr/board.do?menuIdx=548" target="_blank" rel="noopener noreferrer">서울교통공사 노선 안내</a><span>노선명과 노선 색</span></li>
      </ul>
    </section>
    <p class="sw-foot">역·노선·좌표는 공개 자료를 대조해 정리했습니다 · 방향·거리는 실제 좌표에서 계산한 직선값입니다.</p>
  </main>

  <script type="application/json" id="swData">__DATA_JSON__</script>
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
  try { DATA = JSON.parse(document.getElementById('swData').textContent); } catch (e) { return; }

  var STORE_KEY = 'secjobs-subway-v1';
  var MAX_TRIES = DATA.meta.maxTries || 6;
  var BY_NAME = {};
  var LINE_COLOR = {};
  DATA.stations.forEach(function (station) { BY_NAME[station.name] = station; });
  DATA.lines.forEach(function (line) { LINE_COLOR[line.name] = line.color; });

  // ---------- 날짜 (KST 기준) ----------
  function kstParts(now) {
    var shifted = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + 9 * 3600000);
    return { y: shifted.getFullYear(), m: shifted.getMonth(), d: shifted.getDate(), date: shifted };
  }
  function kstDateString(now) {
    var part = kstParts(now);
    return part.y + '-' + pad(part.m + 1) + '-' + pad(part.d);
  }
  function pad(value) { return value < 10 ? '0' + value : String(value); }
  function dayNumber(now) {
    var part = kstParts(now);
    return Math.floor(Date.UTC(part.y, part.m, part.d) / 86400000);
  }
  function answerFor(now) {
    var index = ((dayNumber(now) % DATA.deck.length) + DATA.deck.length) % DATA.deck.length;
    return DATA.deck[index];
  }

  var today = kstDateString(new Date());
  var dailyAnswer = answerFor(new Date());
  var state = {
    mode: 'daily',
    answer: dailyAnswer,
    attempts: [],
    solved: false,
    practiceAnswer: null
  };

  // ---------- 초성 ----------
  var CHOSUNG = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ';
  function chosung(text) {
    var out = '';
    for (var i = 0; i < text.length; i += 1) {
      var code = text.charCodeAt(i);
      if (code >= 0xAC00 && code <= 0xD7A3) out += CHOSUNG[Math.floor((code - 0xAC00) / 588)];
      else out += text[i];
    }
    return out;
  }

  // ---------- 기록 ----------
  function loadRecord() {
    var empty = { streak: 0, best: 0, solved: 0, lastDate: '', lastResult: null, history: {} };
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); } catch (e) { raw = null; }
    if (!raw || typeof raw !== 'object') return empty;
    return {
      streak: Number(raw.streak) || 0,
      best: Number(raw.best) || 0,
      solved: Number(raw.solved) || 0,
      lastDate: typeof raw.lastDate === 'string' ? raw.lastDate : '',
      lastResult: raw.lastResult && typeof raw.lastResult === 'object' ? raw.lastResult : null,
      history: raw.history && typeof raw.history === 'object' ? raw.history : {}
    };
  }
  function saveRecord(record) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(record)); } catch (e) {}
  }
  var record = loadRecord();

  function yesterdayOf(dateString) {
    var parts = dateString.split('-');
    var d = new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
    d.setUTCDate(d.getUTCDate() - 1);
    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  }

  function settleDaily(win) {
    var todayString = kstDateString(new Date());
    if (record.history[todayString]) return;
    record.history[todayString] = { win: win, tries: state.attempts.length };
    if (win) {
      record.streak = record.lastDate === yesterdayOf(todayString) ? record.streak + 1 : 1;
      record.solved += 1;
      record.lastDate = todayString;
      if (record.streak > record.best) record.best = record.streak;
    } else {
      record.streak = 0;
    }
    record.lastResult = { date: todayString, win: win, tries: state.attempts.length };
    saveRecord(record);
    renderRecord();
  }

  function renderRecord() {
    document.getElementById('swStreak').textContent = String(record.streak);
    document.getElementById('swBest').textContent = String(record.best);
    document.getElementById('swSolved').textContent = String(record.solved);
    document.getElementById('swTryCount').textContent = String(state.attempts.length);
    var note = document.getElementById('swRecordNote');
    if (record.lastResult && record.lastResult.date === kstDateString(new Date())) {
      note.textContent = record.lastResult.win
        ? '오늘 ' + record.lastResult.tries + '수 만에 맞혔습니다. 연속 ' + record.streak + '일째입니다.'
        : '오늘은 아쉽게 놓쳤습니다. 연속 기록이 0으로 돌아갔습니다.';
    } else if (record.lastDate) {
      note.textContent = '마지막 정답 ' + record.lastDate + ' · 연속 ' + record.streak + '일 · 최고 ' + record.best + '일';
    } else {
      note.textContent = '오늘 처음 열었습니다. 정답을 맞히면 연속 기록이 올라갑니다.';
    }
  }

  // ---------- 계산 ----------
  function textOn(hex) {
    var value = String(hex || '#888888').replace('#', '');
    if (value.length === 3) value = value[0] + value[0] + value[1] + value[1] + value[2] + value[2];
    var r = parseInt(value.slice(0, 2), 16) / 255;
    var g = parseInt(value.slice(2, 4), 16) / 255;
    var b = parseInt(value.slice(4, 6), 16) / 255;
    function lin(c) { return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
    var lum = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
    return lum > 0.62 ? '#111827' : '#ffffff';
  }

  function directionOf(from, to) {
    var dlat = to.lat - from.lat;
    var dlng = (to.lng - from.lng) * Math.cos((from.lat + to.lat) / 2 * Math.PI / 180);
    var km = Math.sqrt(Math.pow(dlat * 111.32, 2) + Math.pow(dlng * 111.32, 2));
    var angle = (Math.atan2(dlng, dlat) * 180 / Math.PI + 360) % 360;
    var words = ['북', '북동', '동', '남동', '남', '남서', '서', '북서'];
    return { word: words[Math.floor((angle + 22.5) / 45) % 8], km: km, angle: angle };
  }

  function charStates(guess, answer) {
    var remaining = {};
    for (var i = 0; i < answer.length; i += 1) {
      if (i < guess.length && guess[i] === answer[i]) continue;
      remaining[answer[i]] = (remaining[answer[i]] || 0) + 1;
    }
    var out = [];
    for (var j = 0; j < guess.length; j += 1) {
      if (j < answer.length && guess[j] === answer[j]) out.push('hit');
      else if (remaining[guess[j]]) { remaining[guess[j]] -= 1; out.push('near'); }
      else out.push('miss');
    }
    return out;
  }

  function lineOverlap(guessLines, answerLines) {
    var hits = guessLines.filter(function (line) { return answerLines.indexOf(line) >= 0; });
    return { hits: hits, exact: hits.length === answerLines.length && guessLines.length === answerLines.length };
  }

  // ---------- 렌더 ----------
  var els = {
    input: document.getElementById('swInput'),
    submit: document.getElementById('swSubmit'),
    suggest: document.getElementById('swSuggest'),
    rows: document.getElementById('swRows'),
    tries: document.getElementById('swTries'),
    blanks: document.getElementById('swBlanks'),
    chosungNote: document.getElementById('swChosungNote'),
    result: document.getElementById('swResult'),
    resultBadge: document.getElementById('swResultBadge'),
    resultTitle: document.getElementById('swResultTitle'),
    resultText: document.getElementById('swResultText'),
    answerLine: document.getElementById('swAnswerLine'),
    status: document.getElementById('swStatus'),
    share: document.getElementById('swShare'),
    hint: document.getElementById('swHint'),
    inputStatus: document.getElementById('swInputStatus'),
    streak: document.getElementById('swStreak'),
    guide: document.getElementById('swGuideSteps')
  };

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function chip(lineName, on) {
    var node = el('span', 'sw-chip' + (on ? ' is-on' : ''), lineName.replace('호선', ''));
    if (on) {
      node.style.background = LINE_COLOR[lineName] || '#475569';
      node.style.color = textOn(LINE_COLOR[lineName]);
    }
    node.title = lineName + (on ? ' · 정답에 있는 노선' : ' · 정답에 없음');
    return node;
  }

  function arrowSvg(angle) {
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2.4');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M12 20V5');
    var head = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    head.setAttribute('d', 'M6 11l6-6 6 6');
    svg.appendChild(path);
    svg.appendChild(head);
    svg.style.transform = 'rotate(' + Math.round(angle) + 'deg)';
    return svg;
  }

  function renderTries() {
    els.tries.innerHTML = '';
    for (var i = 0; i < MAX_TRIES; i += 1) {
      var dot = el('span', 'sw-try-dot');
      if (state.attempts.length > i) {
        dot.classList.add('is-used');
        if (state.solved && i === state.attempts.length - 1) dot.classList.add('is-win');
        if (!state.solved && state.attempts.length >= MAX_TRIES) dot.classList.add('is-lose');
      }
      els.tries.appendChild(dot);
    }
    els.tries.setAttribute('aria-label', state.attempts.length + '회 시도 / 최대 ' + MAX_TRIES + '회');
  }

  function attemptRow(attempt) {
    var answer = BY_NAME[state.answer];
    var guess = attempt.station;
    var row = el('div', 'sw-row');
    row.setAttribute('role', 'listitem');
    row.dataset.name = guess.name;

    var nameCell = el('div', 'sw-cell sw-name-cell sw-name');
    var states = charStates(guess.name, answer.name);
    if (guess.name === answer.name) nameCell.classList.add('is-hit');
    else if (states.indexOf('near') >= 0) nameCell.classList.add('is-near');
    for (var i = 0; i < guess.name.length; i += 1) {
      var char = el('span', 'sw-char is-' + states[i], guess.name[i]);
      nameCell.appendChild(char);
    }
    row.appendChild(nameCell);

    var lineCell = el('div', 'sw-cell sw-lines');
    var chips = el('div', 'sw-chips');
    var overlap = lineOverlap(guess.lines, answer.lines);
    if (overlap.exact) lineCell.classList.add('is-hit');
    else if (overlap.hits.length) lineCell.classList.add('is-near');
    else lineCell.classList.add('is-miss');
    guess.lines.forEach(function (line) { chips.appendChild(chip(line, answer.lines.indexOf(line) >= 0)); });
    lineCell.appendChild(chips);
    row.appendChild(lineCell);

    var countCell = el('div', 'sw-cell sw-num');
    var diff = guess.lines.length - answer.lines.length;
    countCell.textContent = String(guess.lines.length);
    var mark = el('span', diff === 0 ? '' : diff > 0 ? 'sw-arrow-up' : 'sw-arrow-down',
      diff === 0 ? ' =' : diff > 0 ? ' ▲' : ' ▼');
    mark.style.fontSize = '10px';
    countCell.appendChild(mark);
    if (diff === 0) countCell.classList.add('is-hit');
    else countCell.classList.add('is-near');
    countCell.title = '연계 노선 ' + guess.lines.length + '개 · 정답은 ' + (diff === 0 ? '같음' : diff > 0 ? '더 적음' : '더 많음');
    row.appendChild(countCell);

    var areaCell = el('div', 'sw-cell', guess.area);
    if (guess.area === answer.area) areaCell.classList.add('is-hit');
    else areaCell.classList.add('is-miss');
    row.appendChild(areaCell);

    var dir = directionOf(guess, answer);
    var dirCell = el('div', 'sw-cell sw-dir');
    if (guess.name === answer.name) {
      dirCell.textContent = '정답';
      dirCell.classList.add('is-hit');
    } else {
      dirCell.appendChild(arrowSvg(dir.angle));
      dirCell.appendChild(el('span', '', dir.word));
      if (dir.km < 1.5) dirCell.classList.add('is-near');
    }
    row.appendChild(dirCell);

    var kmCell = el('div', 'sw-cell', guess.name === answer.name ? '0km' : (Math.round(dir.km * 10) / 10) + 'km');
    if (guess.name === answer.name) kmCell.classList.add('is-hit');
    else if (dir.km < 3) kmCell.classList.add('is-near');
    row.appendChild(kmCell);

    var chosungCell = el('div', 'sw-cell sw-chosung');
    var guessCho = chosung(guess.name);
    var answerCho = chosung(answer.name);
    var same = 0;
    for (var k = 0; k < Math.min(guessCho.length, answerCho.length); k += 1) {
      if (guessCho[k] === answerCho[k]) same += 1;
    }
    chosungCell.textContent = same + '/' + answerCho.length;
    if (same === answerCho.length && guess.name.length === answer.name.length) chosungCell.classList.add('is-hit');
    else if (same) chosungCell.classList.add('is-near');
    chosungCell.title = '초성 자리 일치 ' + same + '개 / 정답 ' + answerCho.length + '자';
    row.appendChild(chosungCell);
    return row;
  }

  function renderRows() {
    els.rows.innerHTML = '';
    if (!state.attempts.length) {
      var empty = el('div', 'sw-empty-row', '첫 역을 넣어 보세요. 노선·연계·자치구·방향·초성 힌트가 바로 나옵니다.');
      empty.setAttribute('role', 'listitem');
      els.rows.appendChild(empty);
      return;
    }
    state.attempts.forEach(function (attempt) { els.rows.appendChild(attemptRow(attempt)); });
  }

  function revealedChars() {
    var answer = BY_NAME[state.answer].name;
    var revealed = {};
    state.attempts.forEach(function (attempt) {
      charStates(attempt.station.name, answer).forEach(function (kind, index) {
        if (kind !== 'miss') revealed[index] = attempt.station.name[index];
      });
    });
    return revealed;
  }

  function renderChosung() {
    var answer = BY_NAME[state.answer].name;
    var answerCho = chosung(answer);
    var revealed = revealedChars();
    els.blanks.innerHTML = '';
    for (var i = 0; i < answerCho.length; i += 1) {
      var blank = el('span', 'sw-blank', revealed[i] ? answer[i] : answerCho[i]);
      if (revealed[i]) {
        blank.classList.add('is-revealed');
        if (revealed[i] === answer[i]) blank.classList.add('is-correct');
      }
      els.blanks.appendChild(blank);
    }
    els.chosungNote.textContent = '초성 ' + answerCho.length + '자 · 맞힌 글자는 드러납니다';
  }

  function renderResult() {
    var finished = state.solved || state.attempts.length >= MAX_TRIES;
    if (!finished) {
      els.result.hidden = true;
      return;
    }
    var answer = BY_NAME[state.answer];
    els.result.hidden = false;
    els.result.className = 'sw-result ' + (state.solved ? 'is-win' : 'is-lose');
    els.resultBadge.textContent = state.solved ? '정답' : '아쉬움';
    els.resultTitle.textContent = state.solved
      ? state.attempts.length + '수 만에 맞혔습니다'
      : '오늘의 역은 ' + answer.name + '역입니다';
    els.resultText.textContent = state.solved
      ? answer.name + '역 · ' + answer.lines.join(' · ') + ' · ' + answer.area
      : '내일 다시 도전해 보세요. 아래 정답 노선과 자치구를 기억해 두면 다음 판이 빨라집니다.';
    els.answerLine.innerHTML = '';
    answer.lines.forEach(function (line) { els.answerLine.appendChild(chip(line, true)); });
    els.answerLine.appendChild(el('span', 'sw-chip', answer.area));
    els.share.textContent = shareText();
    els.submit.disabled = true;
    els.input.disabled = true;
    els.input.placeholder = state.solved ? '오늘은 마쳤습니다' : '오늘 기회를 모두 썼습니다';
  }

  function shareText() {
    var lines = ['오늘의 지하철역 ' + kstDateString(new Date()) + (state.mode === 'practice' ? ' (연습)' : ''),
                 state.attempts.length + '/' + MAX_TRIES];
    var answer = BY_NAME[state.answer];
    state.attempts.forEach(function (attempt) {
      var guess = attempt.station;
      var states = charStates(guess.name, answer.name);
      var nameMark = guess.name === answer.name ? '■' : states.indexOf('near') >= 0 ? '▲' : '□';
      var overlap = lineOverlap(guess.lines, answer.lines);
      var lineMark = overlap.exact ? '■' : overlap.hits.length ? '▲' : '□';
      var diff = guess.lines.length - answer.lines.length;
      var countMark = diff === 0 ? '■' : diff > 0 ? '▲' : '▽';
      var areaMark = guess.area === answer.area ? '■' : '□';
      var km = directionOf(guess, answer).km;
      var dirMark = km < 1.5 ? '■' : km < 5 ? '▲' : '□';
      lines.push(nameMark + lineMark + countMark + areaMark + dirMark);
    });
    lines.push('http://bling9513-ship-it.github.io/project-1/subway.html');
    return lines.join('\n');
  }

  function renderAll() {
    renderTries();
    renderRows();
    renderChosung();
    renderResult();
    renderRecord();
  }

  // ---------- 입력 · 자동완성 ----------
  var suggestItems = [];
  var activeIndex = -1;

  function search(query) {
    var term = query.trim();
    if (!term) return [];
    var cho = chosung(term);
    var out = [];
    DATA.stations.forEach(function (station) {
      if (state.attempts.some(function (attempt) { return attempt.station.name === station.name; })) return;
      var nameCho = chosung(station.name);
      if (station.name.indexOf(term) === 0 || nameCho.indexOf(cho) === 0
          || station.name.indexOf(term) > 0 || nameCho.indexOf(cho) > 0) {
        out.push({ station: station, start: station.name.indexOf(term) === 0 || nameCho.indexOf(cho) === 0 });
      }
    });
    out.sort(function (a, b) {
      if (a.start !== b.start) return a.start ? -1 : 1;
      return a.station.name.length - b.station.name.length || a.station.name.localeCompare(b.station.name);
    });
    return out.slice(0, 8).map(function (row) { return row.station; });
  }

  function renderSuggest() {
    var term = els.input.value;
    var matches = search(term);
    suggestItems = matches;
    activeIndex = -1;
    els.suggest.innerHTML = '';
    if (!term.trim() || !matches.length || els.input.disabled) {
      if (term.trim() && !matches.length) {
        els.suggest.appendChild(el('div', 'sw-empty', '일치하는 역이 없습니다. 다른 이름이나 초성으로 찾아보세요.'));
        els.suggest.hidden = false;
        els.input.setAttribute('aria-expanded', 'true');
      } else {
        els.suggest.hidden = true;
        els.input.setAttribute('aria-expanded', 'false');
      }
      return;
    }
    matches.forEach(function (station, index) {
      var btn = el('button', '');
      btn.type = 'button';
      btn.setAttribute('role', 'option');
      btn.dataset.index = String(index);
      btn.dataset.name = station.name;
      btn.appendChild(el('span', '', station.name));
      btn.appendChild(el('span', '', station.lines.join(' · ') + ' · ' + station.area));
      btn.addEventListener('click', function () { choose(station.name); });
      els.suggest.appendChild(btn);
    });
    els.suggest.hidden = false;
    els.input.setAttribute('aria-expanded', 'true');
  }

  function highlight(index) {
    var buttons = els.suggest.querySelectorAll('button');
    activeIndex = index;
    Array.prototype.forEach.call(buttons, function (btn, i) {
      btn.classList.toggle('is-active', i === index);
    });
  }

  function choose(name) {
    els.input.value = name;
    els.suggest.hidden = true;
    els.input.setAttribute('aria-expanded', 'false');
    submitGuess();
  }

  function submitGuess() {
    if (state.solved || state.attempts.length >= MAX_TRIES) return;
    var name = els.input.value.trim();
    var station = BY_NAME[name];
    if (!station) {
      var matches = search(name);
      if (matches.length) { choose(matches[0].name); return; }
      els.inputStatus.textContent = '역 목록에 없는 이름입니다. 제안 목록에서 골라 주세요.';
      window.setTimeout(function () { if (els.inputStatus.textContent) els.inputStatus.textContent = ''; }, 3000);
      return;
    }
    if (state.attempts.some(function (attempt) { return attempt.station.name === station.name; })) {
      els.inputStatus.textContent = '이미 넣은 역입니다. 다른 역을 골라 주세요.';
      window.setTimeout(function () { if (els.inputStatus.textContent) els.inputStatus.textContent = ''; }, 3000);
      return;
    }
    state.attempts.push({ station: station });
    if (station.name === state.answer) {
      state.solved = true;
      if (state.mode === 'daily') settleDaily(true);
    } else if (state.attempts.length >= MAX_TRIES) {
      if (state.mode === 'daily') settleDaily(false);
    }
    els.input.value = '';
    els.suggest.hidden = true;
    els.inputStatus.textContent = '';
    renderAll();
    if (state.mode === 'practice' && (state.solved || state.attempts.length >= MAX_TRIES)) {
      els.status.textContent = state.solved ? '연습 판 정답입니다. 기록에는 반영하지 않습니다.' : '연습 판 정답은 ' + state.answer + '역이었습니다.';
    }
    if (!state.solved && state.attempts.length < MAX_TRIES) els.input.focus();
  }

  els.input.addEventListener('input', renderSuggest);
  els.input.addEventListener('focus', renderSuggest);
  els.input.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowDown' && suggestItems.length) {
      event.preventDefault();
      highlight(Math.min(suggestItems.length - 1, activeIndex + 1));
    } else if (event.key === 'ArrowUp' && suggestItems.length) {
      event.preventDefault();
      highlight(Math.max(0, activeIndex - 1));
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (!els.suggest.hidden && suggestItems.length) {
        choose(suggestItems[activeIndex >= 0 ? activeIndex : 0].name);
      } else {
        submitGuess();
      }
    } else if (event.key === 'Escape') {
      els.suggest.hidden = true;
      els.input.setAttribute('aria-expanded', 'false');
    }
  });
  els.submit.addEventListener('click', submitGuess);
  document.addEventListener('click', function (event) {
    if (!event.target.closest || !event.target.closest('.sw-input-wrap')) {
      els.suggest.hidden = true;
      els.input.setAttribute('aria-expanded', 'false');
    }
  });

  // ---------- 모드 ----------
  function startPractice() {
    var pool = DATA.stations.filter(function (station) { return station.name !== state.answer; });
    var pick = pool[Math.floor(Math.random() * pool.length)];
    state = { mode: 'practice', answer: pick.name, attempts: [], solved: false, practiceAnswer: pick.name };
    els.input.disabled = false;
    els.submit.disabled = false;
    els.input.value = '';
    els.input.placeholder = '연습 · 역 이름을 입력하세요';
    els.status.textContent = '';
    document.querySelectorAll('.sw-mode button').forEach(function (btn) {
      var on = btn.dataset.mode === 'practice';
      btn.classList.toggle('is-on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    renderAll();
    els.input.focus();
  }

  function startDaily() {
    state = { mode: 'daily', answer: dailyAnswer, attempts: [], solved: false, practiceAnswer: null };
    els.input.disabled = false;
    els.submit.disabled = false;
    els.input.value = '';
    els.input.placeholder = '역 이름을 입력하세요 (예: 강남, ㄱㄴ)';
    els.status.textContent = '';
    document.querySelectorAll('.sw-mode button').forEach(function (btn) {
      var on = btn.dataset.mode === 'daily';
      btn.classList.toggle('is-on', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    renderAll();
  }

  document.querySelectorAll('.sw-mode button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.dataset.mode === 'practice') startPractice();
      else startDaily();
    });
  });
  document.getElementById('swPracticeStart').addEventListener('click', startPractice);
  document.getElementById('swAgain').addEventListener('click', startPractice);

  // ---------- 복사 ----------
  function copyText(text) {
    function done(ok) {
      els.status.textContent = ok ? '결과를 복사했습니다. 스포일러 없는 그리드만 담았습니다.' : '복사에 실패했습니다. 브라우저 권한을 확인해 주세요.';
      window.setTimeout(function () { if (els.status.textContent) els.status.textContent = ''; }, 4000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallbackCopy(text, done); });
      return;
    }
    fallbackCopy(text, done);
  }
  function fallbackCopy(text, done) {
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
  document.getElementById('swCopy').addEventListener('click', function () { copyText(shareText()); });

  // ---------- 3단계 가이드 ----------
  var steps = Array.prototype.slice.call(els.guide.querySelectorAll('.sw-step'));
  var guideTimer = null;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var guideNote = document.getElementById('swGuideNote');
  var guideState = document.getElementById('swGuideState');

  function clearGuide() {
    steps.forEach(function (step) { step.classList.remove('is-on'); });
  }
  function playGuide() {
    if (guideTimer) { window.clearInterval(guideTimer); guideTimer = null; }
    clearGuide();
    if (reduceMotion) {
      steps.forEach(function (step) { step.classList.add('is-on'); });
      guideNote.textContent = '동작 줄이기 설정 · 정지 화면';
      guideState.textContent = '세 단계를 한 번에 보여 줍니다';
      return;
    }
    var index = 0;
    steps[0].classList.add('is-on');
    guideNote.textContent = '재생 중 1/3';
    guideState.textContent = '자동 재생이 끝나면 멈춥니다';
    guideTimer = window.setInterval(function () {
      index += 1;
      if (index >= steps.length) {
        window.clearInterval(guideTimer);
        guideTimer = null;
        guideNote.textContent = '재생 완료 · 멈춤';
        guideState.textContent = '다시 보려면 다시 보기를 누르세요';
        return;
      }
      clearGuide();
      steps[index].classList.add('is-on');
      guideNote.textContent = '재생 중 ' + (index + 1) + '/3';
    }, 1500);
  }
  document.getElementById('swReplay').addEventListener('click', playGuide);

  // ---------- 시작 ----------
  renderAll();
  if (reduceMotion) {
    playGuide();
  } else if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          observer.disconnect();
          playGuide();
        }
      });
    }, { threshold: 0.35 });
    observer.observe(els.guide);
  } else {
    playGuide();
  }

  // 테스트·디버깅용 (정답은 페이지 안에서 채점하므로 어차피 소스에 있다)
  window.SUBWAY_ANSWER = state.answer;
  window.SUBWAY = {
    data: DATA,
    state: function () { return state; },
    answer: function () { return state.answer; },
    guess: function (name) { els.input.value = name; submitGuess(); },
    share: shareText
  };
})();
"""


if __name__ == "__main__":
    build()

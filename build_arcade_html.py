# -*- coding: utf-8 -*-
"""아케이드(arcade.html) — 실시간 Canvas 벽돌깨기·지렁이 + 닉네임·티어 랭킹 빌더.

규칙 요약
  · 두 게임(벽돌깨기 / 지렁이) × 두 난이도(보통 / 어려움) = 점수판 4개를 완전히 분리한다.
  · 벽돌깨기: 60fps Canvas, 패들 마우스·터치 드래그·키보드, 콤보 점수, 스테이지 웨이브, 목숨 3.
  · 지렁이: 틱 기반 부드러운 이동, 먹이·보너스 먹이, 벽·몸·장애물 충돌, 스와이프·방향키 패드.
  · 점수 구간별 티어(브론즈~챌린저)와 다음 등급까지 남은 점수를 보여 준다.
  · 랭킹은 '이 기기 기록'(localStorage arcade_ranking_v1, verified:false)과 '기준 라이벌'(미리 세팅한
    AI 기준 기록)로 나눠 보여 준다. 기록은 100% textContent 로만 렌더링한다(닉네임 XSS 차단).
  · RankingStore 어댑터가 로컬 저장과 서버 검증 제출 훅을 분리한다 — 로컬 점수는 서버 검증 없이
    글로벌 기록으로 올리지 않는다(향후 2번 외부 DB 랭킹 확장 지점).
  · 게임 방법은 Canvas 프리뷰 애니메이션 1회 + '다시 보기'. 플레이를 가리거나 포커스를 뺏지 않는다.
"""
import json
import os
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "arcade_data.json")
ARCADE_HTML = os.path.join(BASE_DIR, "arcade.html")
KST = timezone(timedelta(hours=9))

# 티어 등급(낮은 점수 → 높은 점수). 화면 배지 색은 CSS 의 .tier-0 ~ .tier-5 가 맡는다.
TIERS = ["브론즈", "실버", "골드", "플래티넘", "다이아", "챌린저"]

# (게임, 난이도, 표시 이름, 티어 최소 점수 6단계, 기준 라이벌[(이름, 점수, 메모)])
BOARD_SPECS = [
    (
        "brick", "normal", "벽돌깨기 · 보통",
        [0, 800, 1800, 3200, 5200, 7600],
        [
            ("패들장인", 9400, "스테이지 9"),
            ("야간반사", 7700, "스테이지 8"),
            ("블루벽돌", 6150, "스테이지 7"),
            ("코랄러시", 4900, "스테이지 6"),
            ("집중근무", 3650, "스테이지 5"),
            ("첫출근러", 2480, "스테이지 4"),
        ],
    ),
    (
        "brick", "hard", "벽돌깨기 · 어려움",
        [0, 620, 1400, 2600, 4200, 6200],
        [
            ("강철패들", 7250, "스테이지 8"),
            ("심야당직", 5980, "스테이지 7"),
            ("속도광", 4600, "스테이지 6"),
            ("벽돌수집가", 3450, "스테이지 5"),
            ("늦은퇴근", 2520, "스테이지 4"),
            ("신입관제", 1740, "스테이지 3"),
        ],
    ),
    (
        "snake", "normal", "지렁이 · 보통",
        [0, 300, 620, 1000, 1450, 1950],
        [
            ("꼬리장인", 2130, "길이 46"),
            ("먹이사냥", 1720, "길이 39"),
            ("새벽순찰", 1310, "길이 31"),
            ("격자감각", 1010, "길이 26"),
            ("서행운전", 770, "길이 21"),
            ("첫뱀", 530, "길이 16"),
        ],
    ),
    (
        "snake", "hard", "지렁이 · 어려움",
        [0, 240, 500, 830, 1200, 1600],
        [
            ("독니", 1610, "길이 38"),
            ("급커브", 1290, "길이 32"),
            ("벽타기", 990, "길이 27"),
            ("좌회전", 760, "길이 22"),
            ("짧은꼬리", 570, "길이 18"),
            ("신입뱀", 390, "길이 14"),
        ],
    ),
]

GUIDE = {
    "brick": [
        "패들을 좌우로 움직여 공을 튕겨냅니다. 마우스·터치 드래그, ←/→ 키 모두 됩니다.",
        "벽돌을 연달아 깨면 콤보가 올라 점수가 커집니다. 공이 패들에 닿으면 콤보는 초기화됩니다.",
        "벽돌을 모두 깨면 다음 스테이지가 열립니다. 목숨은 3개, 공을 놓치면 하나 줄어듭니다.",
    ],
    "snake": [
        "먹이를 먹으면 몸이 길어지고 점수와 속도가 함께 오릅니다.",
        "스와이프 또는 화면 아래 방향키 패드, PC는 방향키·WASD로 방향을 바꿉니다.",
        "벽과 자기 몸, 어려움 난이도의 장애물에 부딪히면 끝납니다. 노란 보너스 먹이는 3배 점수입니다.",
    ],
}

CONFIG = {
    "brick": {
        "normal": {"speed": 320, "paddleW": 88, "rows": 5, "lives": 3},
        "hard": {"speed": 385, "paddleW": 72, "rows": 6, "lives": 3},
    },
    "snake": {
        "normal": {"tickMs": 150, "minTickMs": 85, "obstacles": False, "bonusEvery": 5},
        "hard": {"tickMs": 120, "minTickMs": 72, "obstacles": True, "bonusEvery": 4},
    },
}


def build_data(now):
    boards = []
    for game, difficulty, label, thresholds, rivals in BOARD_SPECS:
        tier_rows = []
        for index, minimum in enumerate(thresholds):
            tier_rows.append({"name": TIERS[index], "min": minimum})
        rival_rows = []
        for name, score, note in rivals:
            tier_name = TIERS[0]
            for index, minimum in enumerate(thresholds):
                if score >= minimum:
                    tier_name = TIERS[index]
            rival_rows.append({"name": name, "score": score, "tier": tier_name, "note": note})
        rival_rows.sort(key=lambda row: -row["score"])
        boards.append({
            "key": "%s:%s" % (game, difficulty),
            "game": game,
            "difficulty": difficulty,
            "label": label,
            "tiers": tier_rows,
            "rivals": rival_rows,
        })
    return {
        "built_at": now.strftime("%Y-%m-%d %H:%M:%S KST"),
        "tiers": TIERS,
        "boards": boards,
        "guide": GUIDE,
        "config": CONFIG,
        "ranking": {
            "storageKey": "arcade_ranking_v1",
            "maxRows": 10,
            "localOnly": True,
            "note": "이 기기 기록은 verified:false 로컬 기록입니다. 서버 검증 없이 글로벌 랭킹으로 올리지 않습니다.",
        },
    }


CSS = r"""
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

      --accent-primary: #3182f6;
      --accent-hover: #1f6fe5;
      --accent-subtle: #eff6ff;

      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;
      --warn-bg: #fffbeb; --warn-text: #b45309; --warn-border: #fde68a;
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --arc-navy: #0b1526;
      --arc-navy-soft: #13233c;
      --arc-coral: #ff6b6b;
      --arc-gold: #f6c343;

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

    .arc-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 72px; }

    .arc-hero { margin-bottom: 12px; }
    .arc-pill {
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
    .arc-hero h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.035em; }
    .arc-hero p { margin-top: 5px; font-size: 13px; color: var(--text-secondary); max-width: 700px; }

    .arc-toolbar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 12px; }
    .arc-seg { display: inline-flex; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 11px; min-width: 0; }
    .arc-seg-btn {
      border: 0; background: transparent; border-radius: 8px; padding: 8px 14px;
      font-family: inherit; font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary); cursor: pointer; white-space: nowrap;
      transition: background-color 160ms ease, color 160ms ease;
    }
    .arc-seg-btn:hover { color: var(--text-primary); }
    .arc-seg-btn.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }
    .arc-board-label { margin-left: auto; font-size: 11.5px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }

    .arc-shell { display: grid; grid-template-columns: 324px minmax(0, 1fr); gap: 16px; align-items: start; }
    .arc-main { grid-column: 2; grid-row: 1; min-width: 0; }
    .arc-rail { grid-column: 1; grid-row: 1; display: flex; flex-direction: column; gap: 12px; position: sticky; top: 76px; min-width: 0; }

    .arc-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 16px;
      padding: 13px 14px;
      box-shadow: var(--card-shadow);
      min-width: 0;
    }
    .arc-card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 9px; }
    .arc-card-head h2 { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; }
    .arc-card-head span { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }

    .arc-stage-card { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px; padding: 12px; box-shadow: var(--card-shadow); min-width: 0; }

    .arc-hud { display: flex; align-items: flex-end; flex-wrap: wrap; gap: 6px 16px; padding: 2px 4px 10px; }
    .arc-hud-item { display: inline-flex; flex-direction: column; gap: 1px; min-width: 44px; }
    .arc-hud-item span { font-size: 10.5px; font-weight: 600; color: var(--text-muted); }
    .arc-hud-item strong { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .arc-hud-aux { margin-left: auto; font-size: 11px; color: var(--text-secondary); font-variant-numeric: tabular-nums; text-align: right; }
    .arc-hud-actions { display: inline-flex; gap: 6px; }
    .arc-ghost-btn {
      border: 1px solid var(--border-default); background: var(--bg-page); color: var(--text-secondary);
      font-family: inherit; font-size: 11.5px; font-weight: 600; border-radius: 9px; padding: 7px 11px;
      cursor: pointer; white-space: nowrap;
      transition: background-color 160ms ease, color 160ms ease, border-color 160ms ease, transform 160ms ease;
    }
    .arc-ghost-btn:hover:not(:disabled) { color: var(--text-primary); border-color: var(--border-strong); }
    .arc-ghost-btn:active:not(:disabled) { transform: scale(0.97); }
    .arc-ghost-btn:disabled { opacity: 0.45; cursor: default; }

    .arc-stage { position: relative; max-width: 440px; margin: 0 auto; }
    .arc-canvas {
      display: block; width: 100%; aspect-ratio: 3 / 4; border-radius: 14px;
      background: var(--arc-navy); touch-action: none; cursor: crosshair;
    }

    .arc-overlay {
      position: absolute; inset: 0; display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 7px;
      padding: 20px; text-align: center; border-radius: 14px;
      background: rgba(8, 17, 34, 0.88); color: #eaf2ff;
      overflow-y: auto;
    }
    .arc-overlay h3 { font-size: 19px; font-weight: 700; letter-spacing: -0.03em; }
    .arc-overlay p { font-size: 12.5px; line-height: 1.55; color: #a9bcd8; max-width: 300px; }
    .arc-overlay-stats { font-size: 24px; font-weight: 700; letter-spacing: -0.03em; color: #ffffff; font-variant-numeric: tabular-nums; }
    .arc-overlay .arc-primary { margin-top: 4px; }
    .arc-primary {
      border: 0; border-radius: 11px; padding: 11px 20px;
      font-family: inherit; font-size: 13px; font-weight: 700; letter-spacing: -0.02em;
      background: var(--accent-primary); color: #ffffff; cursor: pointer;
      transition: background-color 160ms ease, transform 160ms ease;
    }
    .arc-primary:hover { background: var(--accent-hover); }
    .arc-primary:active { transform: scale(0.98); }

    .arc-status { min-height: 17px; padding: 8px 4px 0; font-size: 11px; line-height: 1.5; color: var(--text-muted); }

    /* ----- 방향키 패드(지렁이 · 모바일) ----- */
    .arc-dpad { display: none; grid-template-columns: repeat(3, 64px); grid-auto-rows: 50px; gap: 8px; justify-content: center; margin: 10px auto 0; }
    .arc-dpad-btn {
      display: flex; align-items: center; justify-content: center;
      border: 1px solid var(--border-default); background: var(--bg-subtle);
      border-radius: 14px; color: var(--text-primary); cursor: pointer;
      -webkit-tap-highlight-color: transparent; touch-action: manipulation;
      transition: background-color 140ms ease, transform 140ms ease;
    }
    .arc-dpad-btn:active { transform: scale(0.95); background: var(--bg-muted); }
    .arc-dpad-btn svg { width: 22px; height: 22px; }
    .arc-dpad-btn[data-dir="up"] { grid-column: 2; grid-row: 1; }
    .arc-dpad-btn[data-dir="left"] { grid-column: 1; grid-row: 2; }
    .arc-dpad-btn[data-dir="down"] { grid-column: 2; grid-row: 2; }
    .arc-dpad-btn[data-dir="right"] { grid-column: 3; grid-row: 2; }

    /* ----- 내 기록 · 티어 ----- */
    .arc-best-row { display: flex; align-items: baseline; gap: 8px; }
    .arc-best-row strong { font-size: 26px; font-weight: 700; letter-spacing: -0.035em; font-variant-numeric: tabular-nums; }
    .arc-best-row span { font-size: 11.5px; color: var(--text-muted); }
    .arc-tier-row { display: flex; align-items: center; gap: 8px; margin-top: 7px; }
    .arc-tier {
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 11px; font-weight: 700; letter-spacing: -0.01em;
      border-radius: 999px; padding: 3px 9px;
      border: 1px solid transparent;
    }
    .arc-tier[data-tier="0"] { background: #fdf6ec; color: #92643a; border-color: #f3ddc3; }
    .arc-tier[data-tier="1"] { background: #f1f5f9; color: #5b6b7f; border-color: #dde5ee; }
    .arc-tier[data-tier="2"] { background: #fffaeb; color: #a06a06; border-color: #f7e3a9; }
    .arc-tier[data-tier="3"] { background: #ecfeff; color: #0e7490; border-color: #bfeef6; }
    .arc-tier[data-tier="4"] { background: #eef2ff; color: #4338ca; border-color: #cdd5fb; }
    .arc-tier[data-tier="5"] { background: #fff1f2; color: #be123c; border-color: #fecdd3; }
    [data-theme="dark"] .arc-tier[data-tier="0"] { background: rgba(180, 130, 70, 0.16); color: #e7c39a; border-color: rgba(180, 130, 70, 0.34); }
    [data-theme="dark"] .arc-tier[data-tier="1"] { background: rgba(148, 163, 184, 0.16); color: #cbd5e1; border-color: rgba(148, 163, 184, 0.32); }
    [data-theme="dark"] .arc-tier[data-tier="2"] { background: rgba(246, 195, 67, 0.16); color: #f8d67f; border-color: rgba(246, 195, 67, 0.34); }
    [data-theme="dark"] .arc-tier[data-tier="3"] { background: rgba(56, 189, 248, 0.16); color: #8fe3fb; border-color: rgba(56, 189, 248, 0.32); }
    [data-theme="dark"] .arc-tier[data-tier="4"] { background: rgba(99, 102, 241, 0.2); color: #b6b9fb; border-color: rgba(99, 102, 241, 0.36); }
    [data-theme="dark"] .arc-tier[data-tier="5"] { background: rgba(255, 107, 107, 0.18); color: #ffb3b3; border-color: rgba(255, 107, 107, 0.36); }
    .arc-tier-next { font-size: 10.5px; line-height: 1.45; color: var(--text-muted); margin-top: 6px; }

    /* ----- 랭킹 ----- */
    .arc-rank-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 10px; }
    .arc-rank-tab {
      border: 0; background: transparent; border-radius: 8px; padding: 7px 4px;
      font-family: inherit; font-size: 11.5px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary); cursor: pointer; white-space: nowrap;
      transition: background-color 160ms ease, color 160ms ease;
    }
    .arc-rank-tab.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }
    .arc-rank-note { margin: 8px 0 6px; font-size: 10px; line-height: 1.5; color: var(--text-muted); }
    .arc-rank-list { list-style: none; display: flex; flex-direction: column; gap: 4px; }
    .arc-rank-row {
      display: flex; align-items: center; gap: 7px;
      padding: 7px 8px; border-radius: 9px; background: var(--bg-page);
      border: 1px solid var(--border-subtle); min-width: 0;
    }
    .arc-rank-row.is-top { border-color: var(--accent-primary); background: var(--accent-subtle); }
    .arc-rank-no { width: 16px; flex: 0 0 auto; font-size: 10.5px; font-weight: 700; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .arc-rank-name { flex: 1 1 auto; min-width: 0; font-size: 12px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .arc-rank-badge { flex: 0 0 auto; font-size: 9.5px; font-weight: 700; color: var(--text-muted); border: 1px solid var(--border-default); border-radius: 5px; padding: 1px 4px; }
    .arc-rank-tier { flex: 0 0 auto; font-size: 9.5px; font-weight: 600; color: var(--text-muted); }
    .arc-rank-score { flex: 0 0 auto; font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums; }
    .arc-rank-empty { padding: 12px 8px; text-align: center; font-size: 11px; color: var(--text-muted); border: 1px dashed var(--border-default); border-radius: 9px; list-style: none; }
    .arc-rank-foot { margin-top: 8px; font-size: 10px; line-height: 1.5; color: var(--text-muted); }

    /* ----- 닉네임 등록 ----- */
    .arc-nick {
      margin-top: 8px; padding: 10px 11px; width: 100%; max-width: 330px; text-align: left;
      border: 1px solid var(--border-default); border-radius: 12px;
      background: var(--bg-surface); color: var(--text-primary);
    }
    .arc-nick-head { display: flex; align-items: baseline; gap: 7px; flex-wrap: wrap; margin-bottom: 8px; }
    .arc-nick-head strong { font-size: 17px; font-weight: 700; font-variant-numeric: tabular-nums; }
    .arc-nick-head span { font-size: 11px; color: var(--text-muted); }
    .arc-nick label { display: block; font-size: 10.5px; font-weight: 600; color: var(--text-muted); margin-bottom: 5px; }
    .arc-nick-row { display: flex; gap: 6px; }
    .arc-nick input {
      flex: 1 1 auto; min-width: 0; padding: 9px 11px;
      border: 1px solid var(--border-default); border-radius: 9px;
      background: var(--bg-surface); color: var(--text-primary);
      font-family: inherit; font-size: 13px; letter-spacing: -0.01em;
    }
    .arc-nick input:focus { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .arc-nick .arc-primary { padding: 9px 14px; font-size: 12px; white-space: nowrap; }
    .arc-nick-note { margin-top: 7px; font-size: 10px; line-height: 1.5; color: var(--text-muted); }
    .arc-nick-note.arc-nick-error { color: var(--no-text); }

    /* ----- 게임 방법(Canvas 프리뷰) ----- */
    .arc-guide-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .arc-guide-head h2 { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; }
    .arc-guide-actions { display: inline-flex; gap: 6px; align-items: center; }
    .arc-guide-link {
      border: 0; background: transparent; font-family: inherit; font-size: 11px; font-weight: 600;
      color: var(--accent-primary); cursor: pointer; padding: 4px 0 4px 8px; white-space: nowrap;
    }
    .arc-guide-body { margin-top: 9px; }
    .arc-guide-frame { position: relative; max-width: 400px; border: 1px solid var(--border-default); border-radius: 12px; background: var(--arc-navy); padding: 6px; }
    .arc-guide-canvas { display: block; width: 100%; aspect-ratio: 15 / 8; border-radius: 8px; }
    .arc-guide-cap { margin-top: 7px; font-size: 10px; color: var(--text-muted); }
    .arc-steps { list-style: none; display: flex; flex-direction: column; gap: 7px; margin-top: 9px; }
    .arc-step { display: flex; gap: 8px; font-size: 11px; line-height: 1.5; color: var(--text-secondary); }
    .arc-step-num {
      flex: 0 0 auto; width: 18px; height: 18px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      background: var(--accent-subtle); color: var(--accent-primary);
      font-size: 10px; font-weight: 700; margin-top: 1px;
    }

    .arc-foot-note { margin-top: 12px; font-size: 10.5px; line-height: 1.55; color: var(--text-muted); }

    @media (max-width: 900px) {
      .arc-shell { grid-template-columns: minmax(0, 1fr); }
      .arc-main { grid-column: 1; grid-row: 1; }
      .arc-rail { grid-column: 1; grid-row: 2; position: static; }
      .arc-dpad { display: grid; }
    }

    @media (max-width: 480px) {
      .arc-wrap { padding: 12px 14px 72px; }
      .arc-hero { margin-bottom: 8px; }
      .arc-hero h1 { font-size: 20px; }
      .arc-hero p { margin-top: 4px; font-size: 12px; }
      .arc-toolbar { gap: 6px; margin-bottom: 8px; }
      .arc-seg-btn { padding: 7px 11px; font-size: 12px; }
      .arc-board-label { display: none; }
      .arc-stage-card { padding: 9px; }
      .arc-stage { max-width: min(100%, calc(46vh * 0.75)); }
      .arc-hud { gap: 2px 12px; padding-bottom: 8px; }
      .arc-hud-item strong { font-size: 15px; }
      .arc-hud-aux { width: 100%; margin-left: 0; text-align: left; }
      .arc-nick-row { flex-wrap: wrap; }
      .arc-nick .arc-primary { width: 100%; }
      .arc-dpad { grid-template-columns: repeat(3, 58px); grid-auto-rows: 48px; margin-top: 8px; }
      .arc-rank-row { gap: 5px; padding: 6px 7px; }
      .arc-overlay { padding: 10px; gap: 5px; }
      .arc-overlay h3 { font-size: 16px; }
      .arc-overlay p { font-size: 11.5px; line-height: 1.45; }
      .arc-overlay-stats { font-size: 21px; }
      .arc-nick { padding: 8px 9px; }
      .arc-nick label { margin-bottom: 3px; }
      .arc-nick-note { margin-top: 5px; }
    }

    @media (prefers-reduced-motion: reduce) {
      .arc-seg-btn, .arc-rank-tab, .arc-ghost-btn, .arc-primary, .arc-dpad-btn { transition: none !important; }
      .arc-primary:active, .arc-ghost-btn:active, .arc-dpad-btn:active { transform: none !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 아케이드</title>
  <meta name="description" content="실시간 Canvas 벽돌깨기와 지렁이. 점수 구간별 티어 등급과 게임·난이도별로 분리된 랭킹, 닉네임 기록 등록을 한 화면에서 겨룹니다.">
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
          <span>이 기기 랭킹 · 실시간 Canvas</span>
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

  <main class="arc-wrap">
    <div class="arc-hero">
      <span class="arc-pill">Canvas 아케이드</span>
      <h1>벽돌깨기 · 지렁이</h1>
      <p>벽돌을 깨고 먹이를 먹으며 점수를 쌓으세요. 게임과 난이도마다 점수판이 따로 열리고, 기록에는 닉네임과 티어 등급이 붙습니다.</p>
    </div>

    <div class="arc-toolbar">
      <div class="arc-seg" role="tablist" aria-label="게임 선택">
        <button type="button" class="arc-seg-btn is-active" id="gameBrick" role="tab" aria-selected="true">벽돌깨기</button>
        <button type="button" class="arc-seg-btn" id="gameSnake" role="tab" aria-selected="false">지렁이</button>
      </div>
      <div class="arc-seg" role="group" aria-label="난이도 선택">
        <button type="button" class="arc-seg-btn is-active" id="diffNormal" aria-pressed="true">보통</button>
        <button type="button" class="arc-seg-btn" id="diffHard" aria-pressed="false">어려움</button>
      </div>
      <span class="arc-board-label" id="boardLabel">벽돌깨기 · 보통</span>
    </div>

    <div class="arc-shell">
      <section class="arc-main" aria-label="게임 화면">
        <div class="arc-stage-card">
          <div class="arc-hud">
            <div class="arc-hud-item"><span>점수</span><strong id="hudScore">0</strong></div>
            <div class="arc-hud-item"><span>내 최고</span><strong id="hudBest">0</strong></div>
            <div class="arc-hud-item"><span id="hudLivesLabel">목숨</span><strong id="hudLives">3</strong></div>
            <span class="arc-hud-aux" id="hudAux">스테이지 1 · 콤보 0</span>
            <div class="arc-hud-actions">
              <button type="button" class="arc-ghost-btn" id="pauseBtn" disabled>일시정지</button>
              <button type="button" class="arc-ghost-btn" id="quitBtn" disabled>판 포기</button>
            </div>
          </div>

          <div class="arc-stage" id="stage" data-game="brick" data-difficulty="normal" data-board="brick:normal" data-phase="idle" data-dir="1,0">
            <canvas class="arc-canvas" id="gameCanvas" width="480" height="640" aria-label="게임 화면" role="img"></canvas>
            <div class="arc-overlay" id="overlay">
              <h3 id="overlayTitle">벽돌깨기</h3>
              <p id="overlayText">패들을 움직여 공을 튕겨내고 벽돌을 모두 깨세요.</p>
              <div class="arc-overlay-stats" id="overlayStats" hidden></div>
              <div class="arc-nick" id="nickPanel" hidden>
                <div class="arc-nick-head">
                  <strong id="nickScore">0</strong>
                  <span>점 · <span class="arc-tier" id="nickTier" data-tier="0">브론즈</span></span>
                </div>
                <label for="nickInput">닉네임 (1~12자)</label>
                <div class="arc-nick-row">
                  <input id="nickInput" type="text" maxlength="12" autocomplete="off" spellcheck="false" placeholder="예: 야간반사">
                  <button type="button" class="arc-primary" id="nickSave">기록 등록</button>
                </div>
                <p class="arc-nick-note" id="nickNote" role="status">이 기기에만 저장됩니다(검증 전 기록).</p>
              </div>
              <button type="button" class="arc-primary" id="overlayBtn">시작하기</button>
            </div>
          </div>

          <div class="arc-dpad" id="dpad" aria-label="방향키 패드">
            <button type="button" class="arc-dpad-btn" data-dir="up" aria-label="위로">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 15l7-7 7 7"></path></svg>
            </button>
            <button type="button" class="arc-dpad-btn" data-dir="left" aria-label="왼쪽으로">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"></path></svg>
            </button>
            <button type="button" class="arc-dpad-btn" data-dir="down" aria-label="아래로">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 9l7 7 7-7"></path></svg>
            </button>
            <button type="button" class="arc-dpad-btn" data-dir="right" aria-label="오른쪽으로">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"></path></svg>
            </button>
          </div>

          <p class="arc-status" id="arcStatus" role="status" aria-live="polite">시작하기를 누르면 게임이 시작됩니다.</p>
        </div>
      </section>

      <aside class="arc-rail" aria-label="기록과 안내">
        <section class="arc-card" aria-labelledby="bestTitle">
          <div class="arc-card-head"><h2 id="bestTitle">내 기록</h2><span id="bestBoard">벽돌깨기 · 보통</span></div>
          <div class="arc-best-row"><strong id="myBest">0</strong><span>점</span></div>
          <div class="arc-tier-row"><span class="arc-tier" id="tierBadge" data-tier="0">브론즈</span></div>
          <p class="arc-tier-next" id="tierNext">다음 등급 실버까지 800점</p>
        </section>

        <section class="arc-card" aria-labelledby="rankTitle">
          <div class="arc-card-head"><h2 id="rankTitle">랭킹</h2><span id="rankBoardLabel">벽돌깨기 · 보통</span></div>
          <div class="arc-rank-tabs" role="tablist" aria-label="랭킹 종류">
            <button type="button" class="arc-rank-tab is-active" id="rankLocal" role="tab" aria-selected="true">이 기기 기록</button>
            <button type="button" class="arc-rank-tab" id="rankRival" role="tab" aria-selected="false">기준 라이벌</button>
          </div>
          <p class="arc-rank-note" id="rankNote">내가 이 기기에서 등록한 기록입니다. 서버 검증 기록이 아닙니다.</p>
          <ol class="arc-rank-list" id="rankList"></ol>
          <p class="arc-rank-foot">기록은 닉네임과 함께 이 기기에만 남습니다(verified: false). 서버 랭킹은 별도 검증 경로로만 연결됩니다.</p>
        </section>

        <section class="arc-card" id="guideCard" aria-labelledby="guideTitle">
          <div class="arc-guide-head">
            <h2 id="guideTitle">게임 방법</h2>
            <div class="arc-guide-actions">
              <button type="button" class="arc-guide-link" id="guideReplay">다시 보기</button>
              <button type="button" class="arc-guide-link" id="guideToggle" aria-expanded="true" aria-controls="guideBody">접기</button>
            </div>
          </div>
          <div class="arc-guide-body" id="guideBody">
            <div class="arc-guide-frame">
              <canvas class="arc-guide-canvas" id="guideCanvas" width="300" height="160" aria-label="조작 방법 미리보기"></canvas>
            </div>
            <p class="arc-guide-cap" id="guideCaption">미리보기: 패들이 공을 받아 벽돌을 깨는 장면</p>
            <ol class="arc-steps" id="guideSteps">
              <li class="arc-step"><span class="arc-step-num">1</span><span class="arc-step-text">패들을 좌우로 움직여 공을 튕겨냅니다.</span></li>
              <li class="arc-step"><span class="arc-step-num">2</span><span class="arc-step-text">벽돌을 연달아 깨면 콤보 점수가 붙습니다.</span></li>
              <li class="arc-step"><span class="arc-step-num">3</span><span class="arc-step-text">벽돌을 모두 깨면 다음 스테이지가 열립니다.</span></li>
            </ol>
          </div>
        </section>
      </aside>
    </div>

    <p class="arc-foot-note">이 화면의 기록은 브라우저 저장소(arcade_ranking_v1)에만 남고 서버로 보내지 않습니다. 기기를 바꾸면 기록도 따로입니다.</p>
  </main>

  <script type="application/json" id="arcadeData">__DATA_JSON__</script>
  <script>
__JS__
  </script>
</body>
</html>
"""


ARCADE_JS = r"""
(function () {
  'use strict';

  var dataEl = document.getElementById('arcadeData');
  var DATA = {};
  try { DATA = JSON.parse((dataEl && dataEl.textContent) || '{}'); } catch (err) { DATA = {}; }

  var BOARDS = {};
  (Array.isArray(DATA.boards) ? DATA.boards : []).forEach(function (board) { BOARDS[board.key] = board; });
  var CONFIG = DATA.config || {};
  var GUIDE = DATA.guide || {};
  var VW = 480;
  var VH = 640;
  var REDUCE = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  var el = {};
  ['stage', 'gameCanvas', 'overlay', 'overlayTitle', 'overlayText', 'overlayStats', 'overlayBtn',
   'hudScore', 'hudBest', 'hudLivesLabel', 'hudLives', 'hudAux', 'pauseBtn', 'quitBtn',
   'gameBrick', 'gameSnake', 'diffNormal', 'diffHard', 'boardLabel', 'bestBoard',
   'myBest', 'tierBadge', 'tierNext', 'rankLocal', 'rankRival', 'rankList', 'rankNote', 'rankBoardLabel',
   'nickPanel', 'nickScore', 'nickTier', 'nickInput', 'nickSave', 'nickNote',
   'guideCard', 'guideCanvas', 'guideBody', 'guideToggle', 'guideReplay', 'guideSteps', 'guideCaption',
   'arcStatus', 'dpad', 'themeToggle', 'moonIcon', 'sunIcon'
  ].forEach(function (id) { el[id] = document.getElementById(id); });

  var canvas = el.gameCanvas;
  var ctx = canvas.getContext('2d');
  var view = { dpr: 1, scale: 1, ox: 0, oy: 0 };
  var state = { game: 'brick', difficulty: 'normal', phase: 'idle', score: 0, lastTs: 0 };
  var activeGame = null;
  var rankMode = 'local';
  var bestCache = {};
  var sheetEl = document.getElementById('iaSheet');

  /* ------------------------------------------------------------ 랭킹 저장소 어댑터 */
  /* RankingStore 는 '이 기기 기록'과 '서버 검증 랭킹'을 분리한다.
     로컬 점수는 사용자가 브라우저에서 조작할 수 있으므로, 서버 연동 시에도
     이 객체의 submitLocal 기록을 그대로 글로벌 기록으로 올리지 않는다.
     submitVerified 는 서버 검증(플레이 로그·서명 확인)을 거친 기록만 올리는 전용 훅이다. */
  var RankingStore = {
    KEY: 'arcade_ranking_v1',
    MAX_ROWS: 10,
    empty: function () { return { version: 1, boards: {} }; },
    load: function () {
      try {
        var raw = localStorage.getItem(this.KEY);
        if (!raw) return this.empty();
        var parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== 'object' || !parsed.boards || typeof parsed.boards !== 'object') return this.empty();
        if (!parsed.version) parsed.version = 1;
        return parsed;
      } catch (err) { return this.empty(); }
    },
    save: function (store) {
      try { localStorage.setItem(this.KEY, JSON.stringify(store)); return true; }
      catch (err) { return false; }
    },
    rows: function (store, key) {
      var list = (store && store.boards && Array.isArray(store.boards[key])) ? store.boards[key].slice() : [];
      list.sort(function (a, b) { return (b.score || 0) - (a.score || 0); });
      return list;
    },
    submitLocal: function (store, key, entry) {
      var record = {
        name: entry.name, score: entry.score, tier: entry.tier,
        game: entry.game, difficulty: entry.difficulty, at: entry.at, verified: false
      };
      var list = this.rows(store, key);
      var replaced = false;
      for (var i = 0; i < list.length; i += 1) {
        if (list[i].name === record.name) {
          if (record.score > list[i].score) list[i] = record;
          replaced = true;
          break;
        }
      }
      if (!replaced) list.push(record);
      list.sort(function (a, b) { return (b.score || 0) - (a.score || 0); });
      store.boards[key] = list.slice(0, this.MAX_ROWS);
      return this.save(store);
    },
    /* 서버(글로벌) 랭킹 제출 전용 훅 — 현재는 서버가 연결되어 있지 않아 아무것도 올리지 않는다. */
    submitVerified: function (key, entry) {
      return Promise.resolve({ ok: false, reason: 'server_not_connected', board: key, verified: false, entry: entry });
    }
  };

  var store = RankingStore.load();

  /* ------------------------------------------------------------ 공통 유틸 */
  function pad2(n) { return (n < 10 ? '0' : '') + n; }

  function formatScore(value) {
    var n = Math.round(Number(value) || 0);
    try { return n.toLocaleString('ko-KR'); }
    catch (err) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  }

  function boardKey() { return state.game + ':' + state.difficulty; }

  function board() { return BOARDS[boardKey()] || null; }

  function tierInfo(boardInfo, score) {
    var list = (boardInfo && Array.isArray(boardInfo.tiers) && boardInfo.tiers.length)
      ? boardInfo.tiers : [{ name: '브론즈', min: 0 }];
    var index = 0;
    for (var i = 0; i < list.length; i += 1) { if (score >= list[i].min) index = i; }
    var next = list[index + 1] || null;
    return {
      index: index,
      name: list[index].name,
      next: next ? { name: next.name, need: Math.max(0, next.min - score) } : null
    };
  }

  function bestScore() {
    var key = boardKey();
    if (typeof bestCache[key] === 'number') return bestCache[key];
    var rows = RankingStore.rows(store, key);
    var best = 0;
    for (var i = 0; i < rows.length; i += 1) { if ((rows[i].score || 0) > best) best = rows[i].score || 0; }
    bestCache[key] = best;
    return best;
  }

  function cleanNick(raw) {
    var text = String(raw == null ? '' : raw);
    text = text.replace(/[\u0000-\u001F\u007F-\u009F\u200B-\u200F\u2028\u2029]/g, '');
    text = text.replace(/\s+/g, ' ').trim();
    return text.slice(0, 12);
  }

  function setStatus(text) { if (el.arcStatus) el.arcStatus.textContent = text; }

  function roundRect(g, x, y, w, h, r) {
    var radius = Math.min(r, w / 2, h / 2);
    g.beginPath();
    g.moveTo(x + radius, y);
    g.lineTo(x + w - radius, y);
    g.quadraticCurveTo(x + w, y, x + w, y + radius);
    g.lineTo(x + w, y + h - radius);
    g.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
    g.lineTo(x + radius, y + h);
    g.quadraticCurveTo(x, y + h, x, y + h - radius);
    g.lineTo(x, y + radius);
    g.quadraticCurveTo(x, y, x + radius, y);
    g.closePath();
  }

  function addScore(amount) {
    state.score += amount;
    syncHud();
  }

  /* ------------------------------------------------------------ HUD · 기록 카드 */
  function syncHud() {
    el.hudScore.textContent = formatScore(state.score);
    el.hudBest.textContent = formatScore(bestScore());
    if (state.game === 'brick') {
      el.hudLivesLabel.textContent = '목숨';
      el.hudLives.textContent = String(Brick.lives);
      el.hudAux.textContent = '스테이지 ' + Brick.stage + ' · 콤보 ' + Brick.combo;
    } else {
      el.hudLivesLabel.textContent = '길이';
      el.hudLives.textContent = String(Snake.body.length);
      var speed = Snake.cfg ? (Snake.cfg.tick / Snake.tickMs) : 1;
      el.hudAux.textContent = '속도 ' + speed.toFixed(2) + '배' + (Snake.bonus ? ' · 보너스 먹이' : '');
    }
  }

  function updateRecordCard() {
    var info = board();
    var best = bestScore();
    el.myBest.textContent = formatScore(best);
    var tier = tierInfo(info, best);
    el.tierBadge.textContent = tier.name;
    el.tierBadge.setAttribute('data-tier', String(tier.index));
    if (tier.next) el.tierNext.textContent = '다음 등급 ' + tier.next.name + '까지 ' + formatScore(tier.next.need) + '점';
    else el.tierNext.textContent = '최고 등급입니다. 이 점수를 넘겨 보세요.';
  }

  function renderSegments() {
    var isBrick = state.game === 'brick';
    el.gameBrick.classList.toggle('is-active', isBrick);
    el.gameSnake.classList.toggle('is-active', !isBrick);
    el.gameBrick.setAttribute('aria-selected', isBrick ? 'true' : 'false');
    el.gameSnake.setAttribute('aria-selected', isBrick ? 'false' : 'true');
    var isNormal = state.difficulty === 'normal';
    el.diffNormal.classList.toggle('is-active', isNormal);
    el.diffHard.classList.toggle('is-active', !isNormal);
    el.diffNormal.setAttribute('aria-pressed', isNormal ? 'true' : 'false');
    el.diffHard.setAttribute('aria-pressed', isNormal ? 'false' : 'true');
    var info = board();
    var label = info ? info.label : boardKey();
    el.boardLabel.textContent = label;
    el.bestBoard.textContent = label;
    el.rankBoardLabel.textContent = label;
    el.stage.setAttribute('data-game', state.game);
    el.stage.setAttribute('data-difficulty', state.difficulty);
    el.stage.setAttribute('data-board', boardKey());
    el.overlayStats.hidden = true;
  }

  /* ------------------------------------------------------------ 랭킹 보드 */
  function makeRow(rank, row, kind) {
    var li = document.createElement('li');
    li.className = 'arc-rank-row' + (rank === 0 ? ' is-top' : '');
    li.setAttribute('data-verified', row.verified === false ? 'false' : (kind === 'rival' ? 'reference' : 'true'));
    var no = document.createElement('span');
    no.className = 'arc-rank-no';
    no.textContent = String(rank + 1);
    var name = document.createElement('span');
    name.className = 'arc-rank-name';
    name.textContent = String(row.name == null ? '' : row.name);
    var badge = document.createElement('span');
    badge.className = 'arc-rank-badge';
    badge.textContent = kind === 'rival' ? '기준' : '로컬';
    var tier = document.createElement('span');
    tier.className = 'arc-rank-tier';
    tier.textContent = row.tier || tierInfo(board(), row.score || 0).name;
    var score = document.createElement('span');
    score.className = 'arc-rank-score';
    score.textContent = formatScore(row.score || 0);
    li.appendChild(no);
    li.appendChild(name);
    li.appendChild(badge);
    li.appendChild(tier);
    li.appendChild(score);
    return li;
  }

  function renderRanks() {
    var isLocal = rankMode === 'local';
    el.rankLocal.classList.toggle('is-active', isLocal);
    el.rankRival.classList.toggle('is-active', !isLocal);
    el.rankLocal.setAttribute('aria-selected', isLocal ? 'true' : 'false');
    el.rankRival.setAttribute('aria-selected', isLocal ? 'false' : 'true');
    el.rankList.textContent = '';

    var rows = [];
    if (isLocal) {
      rows = RankingStore.rows(store, boardKey());
      el.rankNote.textContent = '내가 이 기기에서 등록한 기록입니다. 서버 검증 기록이 아닙니다(verified: false).';
    } else {
      var info = board();
      rows = (info && Array.isArray(info.rivals)) ? info.rivals.slice() : [];
      rows.sort(function (a, b) { return (b.score || 0) - (a.score || 0); });
      el.rankNote.textContent = '미리 세팅된 AI 기준 기록입니다. 실제 사용자 기록이 아니며, 이 점수를 넘으면 됩니다.';
    }

    if (!rows.length) {
      var empty = document.createElement('li');
      empty.className = 'arc-rank-empty';
      empty.textContent = isLocal ? '아직 등록된 기록이 없습니다. 게임이 끝나면 닉네임으로 남길 수 있습니다.' : '기준 기록이 없습니다.';
      el.rankList.appendChild(empty);
      return;
    }
    rows.forEach(function (row, index) {
      el.rankList.appendChild(makeRow(index, row, isLocal ? 'local' : 'rival'));
    });
  }

  /* ------------------------------------------------------------ 오버레이 · 흐름 */
  function showOverlay(title, text, buttonLabel, stats) {
    el.overlay.hidden = false;
    el.overlayTitle.textContent = title;
    el.overlayText.textContent = text || '';
    el.overlayBtn.textContent = buttonLabel;
    if (stats) {
      el.overlayStats.textContent = stats;
      el.overlayStats.hidden = false;
    } else {
      el.overlayStats.hidden = true;
    }
  }

  function hideOverlay() { el.overlay.hidden = true; }

  function setPhase(phase) {
    state.phase = phase;
    el.stage.setAttribute('data-phase', phase);
  }

  function resetBoard() {
    setPhase('idle');
    state.score = 0;
    state.lastTs = 0;
    bestCache = {};
    el.nickPanel.hidden = true;
    el.nickNote.classList.remove('arc-nick-error');
    el.pauseBtn.disabled = true;
    el.quitBtn.disabled = true;
    el.pauseBtn.textContent = '일시정지';
    activeGame = state.game === 'brick' ? Brick : Snake;
    activeGame.init(state.difficulty);
    renderSegments();
    renderGuideSteps(state.game);
    syncHud();
    updateRecordCard();
    renderRanks();
    showOverlay(state.game === 'brick' ? '벽돌깨기' : '지렁이',
      state.game === 'brick'
        ? '패들을 움직여 공을 튕겨내고 벽돌을 모두 깨세요.'
        : '먹이를 먹으며 벽과 몸을 피하세요. 방향키·스와이프로 움직입니다.',
      '시작하기');
    setStatus('시작하기를 누르면 게임이 시작됩니다.');
    el.stage.setAttribute('data-dir', '1,0');
  }

  function startRun() {
    if (state.phase === 'paused') { resumeRun(); return; }
    if (state.phase === 'over') { resetBoard(); }
    setPhase('playing');
    hideOverlay();
    el.pauseBtn.disabled = false;
    el.quitBtn.disabled = false;
    Guide.stop();
    if (state.game === 'brick') Brick.resetBall();
    else Snake.delay = 1.2;
    setStatus(state.game === 'brick'
      ? '시작. 좌우로 패들을 움직이세요. 공은 곧 발사됩니다.'
      : '시작. 방향키 · 스와이프 · 방향키 패드로 움직이세요.');
    syncHud();
    ensurePlayVisible();
  }

  /* 모바일에서 게임 화면과 방향키 패드가 하단 탭 바에 가리지 않도록 플레이 시작 시 한 번 맞춰 준다.
     포커스는 옮기지 않고, 이미 다 보이면 스크롤하지 않는다. */
  function ensurePlayVisible() {
    if (!window.matchMedia || !window.matchMedia('(max-width: 900px)').matches) return;
    var bar = document.querySelector('.ia-tabbar');
    var limit = (bar && getComputedStyle(bar).display !== 'none')
      ? bar.getBoundingClientRect().top : window.innerHeight;
    var target = (state.game === 'snake' && el.dpad) ? el.dpad : canvas;
    var box = target.getBoundingClientRect();
    if (box.height && box.bottom <= limit) return;
    // 고정 헤더(54px) 바로 아래에 게임 카드가 오도록 맞춰, 위쪽 내용이 어중간하게 잘려 보이지 않게 한다.
    var card = el.stage.closest ? el.stage.closest('.arc-stage-card') : null;
    var anchor = card || el.stage;
    var top = Math.max(0, window.scrollY + anchor.getBoundingClientRect().top - 54);
    try { window.scrollTo({ top: top, behavior: REDUCE ? 'auto' : 'smooth' }); }
    catch (err) { window.scrollTo(0, top); }
  }

  function togglePause() {
    if (state.phase === 'playing') {
      setPhase('paused');
      el.pauseBtn.textContent = '재개';
      showOverlay('일시정지', '잠시 멈췄습니다. 재개하면 이어서 진행합니다.', '재개하기');
      setStatus('일시정지.');
    } else if (state.phase === 'paused') {
      resumeRun();
    }
  }

  function resumeRun() {
    setPhase('playing');
    el.pauseBtn.textContent = '일시정지';
    hideOverlay();
    state.lastTs = 0;
    setStatus('이어서 진행합니다.');
  }

  function endRun(reason) {
    if (state.phase === 'over') return;
    var score = state.score;
    var info = board();
    var tier = tierInfo(info, score);
    setPhase('over');
    el.pauseBtn.disabled = true;
    el.quitBtn.disabled = true;
    el.pauseBtn.textContent = '일시정지';
    var best = bestScore();
    var isBest = score > 0 && score >= best;
    var detail = score > 0 ? (reason || '이번 판을 마쳤습니다.') : ((reason ? reason + ' ' : '') + '점수를 얻지 못했습니다.');
    showOverlay('기록 종료', detail, '다시 하기');
    if (score > 0) showNickPanel(score, tier, isBest);
    setStatus('기록 종료 · ' + formatScore(score) + '점 · ' + tier.name + '.');
    syncHud();
    renderRanks();
  }

  function showNickPanel(score, tier, isBest) {
    el.nickPanel.hidden = false;
    el.nickScore.textContent = formatScore(score);
    el.nickTier.textContent = tier.name;
    el.nickTier.setAttribute('data-tier', String(tier.index));
    el.nickNote.classList.remove('arc-nick-error');
    el.nickNote.textContent = (isBest ? '이 기기 최고 기록입니다. ' : '') + '닉네임을 남기면 이 기기 랭킹에 등록됩니다(검증 전 · verified: false).';
    el.nickSave.disabled = false;
    el.nickSave.textContent = '기록 등록';
    var last = '';
    try { last = localStorage.getItem('arcade_last_nick') || ''; } catch (err) { last = ''; }
    el.nickInput.value = last;
  }

  /* ------------------------------------------------------------ 티어 · 기록 등록 */
  el.nickSave.addEventListener('click', function () {
    var name = cleanNick(el.nickInput.value);
    if (!name) {
      el.nickNote.textContent = '닉네임은 1~12자로 입력하세요. 공백만으로는 등록할 수 없습니다.';
      el.nickNote.classList.add('arc-nick-error');
      el.nickInput.focus();
      return;
    }
    var info = board();
    var tier = tierInfo(info, state.score);
    var entry = {
      name: name, score: state.score, tier: tier.name,
      game: state.game, difficulty: state.difficulty, at: new Date().toISOString()
    };
    var ok = RankingStore.submitLocal(store, boardKey(), entry);
    store = RankingStore.load();
    bestCache = {};
    try { localStorage.setItem('arcade_last_nick', name); } catch (err) {}
    el.nickInput.value = name;
    RankingStore.submitVerified(boardKey(), entry);
    if (ok) {
      el.nickSave.disabled = true;
      el.nickSave.textContent = '등록됨';
      el.nickNote.textContent = '등록 완료 · 이 기기 랭킹에 남았습니다. 서버(글로벌) 랭킹은 검증된 기록만 받으므로 이 로컬 기록을 그대로 올리지 않습니다.';
      el.nickNote.classList.remove('arc-nick-error');
      setStatus('기록을 이 기기 랭킹에 등록했습니다.');
    } else {
      el.nickNote.textContent = '브라우저 저장 공간을 쓸 수 없어 등록하지 못했습니다.';
      el.nickNote.classList.add('arc-nick-error');
    }
    syncHud();
    updateRecordCard();
    renderRanks();
  });

  el.nickInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') { event.preventDefault(); el.nickSave.click(); }
  });

  /* ------------------------------------------------------------ 티어 · 세그먼트 */
  function updateTierBoard() {
    updateRecordCard();
  }

  /* ------------------------------------------------------------ 벽돌깨기 */
  function brickPalette(row) {
    var colors = ['#3182f6', '#4a90f8', '#64a0fb', '#7fb3fd', '#9cc6fe'];
    return colors[row % colors.length];
  }

  var Brick = {
    cfg: null,
    bricks: [],
    paddle: { x: VW / 2, y: VH - 34, w: 88, h: 12 },
    ball: { x: VW / 2, y: VH - 60, vx: 0, vy: 0, r: 7, stuck: true, serve: 0.7 },
    lives: 3, stage: 1, combo: 0, bestCombo: 0,
    keys: { left: false, right: false },
    flash: 0,
    init: function (difficulty) {
      var conf = (CONFIG.brick && CONFIG.brick[difficulty]) || {};
      this.cfg = {
        speed: conf.speed || 320, paddleW: conf.paddleW || 88,
        rows: conf.rows || 5, cols: 8, lives: conf.lives || 3
      };
      this.stage = 1;
      this.lives = this.cfg.lives;
      this.combo = 0;
      this.bestCombo = 0;
      this.flash = 0;
      this.paddle.w = this.cfg.paddleW;
      this.paddle.h = 12;
      this.paddle.y = VH - 34;
      this.paddle.x = VW / 2;
      this.buildStage();
      this.resetBall();
    },
    buildStage: function () {
      var rows = Math.min(this.cfg.rows + Math.floor((this.stage - 1) / 3), 8);
      var cols = this.cfg.cols;
      var pad = 8;
      var top = 66;
      var gap = 4;
      var bw = (VW - pad * 2 - (cols - 1) * gap) / cols;
      var bh = 18;
      this.bricks = [];
      for (var r = 0; r < rows; r += 1) {
        for (var c = 0; c < cols; c += 1) {
          var tough = (this.stage >= 2 && (r + c + this.stage) % 7 === 0) ? 2 : 1;
          this.bricks.push({
            x: pad + c * (bw + gap), y: top + r * (bh + gap),
            w: bw, h: bh, hp: tough, max: tough, row: r
          });
        }
      }
    },
    resetBall: function () {
      var half = this.paddle.w / 2;
      this.paddle.x = Math.max(half + 6, Math.min(VW - half - 6, this.paddle.x));
      this.ball.x = this.paddle.x;
      this.ball.y = this.paddle.y - 14;
      this.ball.vx = 0;
      this.ball.vy = 0;
      this.ball.stuck = true;
      this.ball.serve = 0.7;
      this.ball.r = 7;
      this.combo = 0;
    },
    aim: function (x) {
      var half = this.paddle.w / 2;
      this.paddle.x = Math.max(half + 6, Math.min(VW - half - 6, x));
    },
    launch: function () {
      if (!this.ball.stuck || state.phase !== 'playing') return;
      var speed = this.cfg.speed * (1 + (this.stage - 1) * 0.045);
      this.ball.vx = speed * 0.42;
      this.ball.vy = -speed * 0.91;
      this.ball.stuck = false;
    },
    update: function (dt) {
      if (this.keys.left || this.keys.right) {
        var step = 560 * dt;
        if (this.keys.left) this.aim(this.paddle.x - step);
        if (this.keys.right) this.aim(this.paddle.x + step);
      }
      var b = this.ball;
      if (b.stuck) {
        b.x = this.paddle.x;
        b.y = this.paddle.y - b.r - 6;
        if (state.phase === 'playing') {
          b.serve -= dt;
          if (b.serve <= 0) this.launch();
        }
        return;
      }
      var total = Math.sqrt(b.vx * b.vx + b.vy * b.vy) * dt;
      var steps = Math.max(1, Math.ceil(total / 6));
      var sdt = dt / steps;
      for (var s = 0; s < steps; s += 1) {
        if (!this.stepBall(sdt)) return;
      }
      if (this.flash > 0) this.flash = Math.max(0, this.flash - dt);
    },
    stepBall: function (dt) {
      var b = this.ball;
      var p = this.paddle;
      var prevX = b.x;
      var prevY = b.y;
      b.x += b.vx * dt;
      b.y += b.vy * dt;
      if (b.x - b.r < 6) { b.x = 6 + b.r; b.vx = Math.abs(b.vx); }
      if (b.x + b.r > VW - 6) { b.x = VW - 6 - b.r; b.vx = -Math.abs(b.vx); }
      if (b.y - b.r < 6) { b.y = 6 + b.r; b.vy = Math.abs(b.vy); }

      if (b.vy > 0 && b.y + b.r >= p.y && b.y - b.r <= p.y + p.h &&
          b.x >= p.x - p.w / 2 - 4 && b.x <= p.x + p.w / 2 + 4) {
        b.y = p.y - b.r;
        var offset = (b.x - p.x) / (p.w / 2);
        offset = Math.max(-1, Math.min(1, offset));
        var speed = Math.min(Math.sqrt(b.vx * b.vx + b.vy * b.vy) * 1.008, 640);
        var angle = offset * 1.02;
        b.vx = Math.sin(angle) * speed;
        b.vy = -Math.cos(angle) * speed;
        this.combo = 0;
        return true;
      }
      if (b.y - b.r > VH) { this.loseLife(); return false; }

      for (var i = 0; i < this.bricks.length; i += 1) {
        var br = this.bricks[i];
        if (!br.hp) continue;
        if (b.x + b.r < br.x || b.x - b.r > br.x + br.w || b.y + b.r < br.y || b.y - b.r > br.y + br.h) continue;
        var hitSide = (prevX + b.r <= br.x) || (prevX - b.r >= br.x + br.w) ||
          (Math.abs(b.vx) > Math.abs(b.vy) && Math.abs(prevY - b.y) < br.h);
        if (hitSide) b.vx = -b.vx;
        else b.vy = -b.vy;
        br.hp -= 1;
        this.combo += 1;
        this.bestCombo = Math.max(this.bestCombo, this.combo);
        var gain = 10 + Math.min(this.combo - 1, 9) * 3;
        if (br.max > 1) gain = Math.round(gain * 1.5);
        gain = Math.round(gain * (1 + (this.stage - 1) * 0.08));
        this.flash = 0.14;
        addScore(gain);
        break;
      }

      var left = 0;
      for (var k = 0; k < this.bricks.length; k += 1) { if (this.bricks[k].hp > 0) { left += 1; break; } }
      if (!left) this.clearStage();
      return true;
    },
    clearStage: function () {
      this.stage += 1;
      addScore(120 + this.stage * 30);
      this.buildStage();
      this.resetBall();
      setStatus('스테이지 ' + this.stage + ' 시작 · 공이 조금 더 빨라집니다.');
      syncHud();
    },
    loseLife: function () {
      this.lives -= 1;
      if (this.lives <= 0) { endRun('벽돌을 모두 깨지 못했습니다.'); return; }
      this.resetBall();
      setStatus('공을 놓쳤습니다. 목숨 ' + this.lives + '개 남았습니다.');
      syncHud();
    },
    render: function (g) {
      var i;
      for (i = 0; i < this.bricks.length; i += 1) {
        var br = this.bricks[i];
        if (!br.hp) continue;
        roundRect(g, br.x, br.y, br.w, br.h, 6);
        g.fillStyle = br.max > 1 ? (br.hp > 1 ? '#ff6b6b' : '#c24a5c') : brickPalette(br.row);
        g.fill();
        if (br.max > 1 && br.hp > 1) {
          g.fillStyle = 'rgba(255,255,255,0.28)';
          roundRect(g, br.x + 5, br.y + 5, br.w - 10, 2.5, 1.2);
          g.fill();
        }
      }
      var p = this.paddle;
      roundRect(g, p.x - p.w / 2, p.y, p.w, p.h, 6);
      g.fillStyle = '#e8f1ff';
      g.fill();
      roundRect(g, p.x - p.w / 2 + 6, p.y + p.h - 3.5, p.w - 12, 3, 1.5);
      g.fillStyle = '#3182f6';
      g.fill();
      var b = this.ball;
      g.beginPath();
      g.arc(b.x, b.y, b.r, 0, Math.PI * 2);
      g.fillStyle = '#ffffff';
      g.fill();
      g.font = '600 11px Pretendard, sans-serif';
      g.fillStyle = 'rgba(233,241,255,0.5)';
      g.fillText('STAGE ' + this.stage, 14, 26);
      g.fillText('COMBO ' + this.combo, VW - 86, 26);
    }
  };

  /* ------------------------------------------------------------ 지렁이 */
  var DIR_NAME = { '0,-1': 'up', '0,1': 'down', '-1,0': 'left', '1,0': 'right' };

  var Snake = {
    cfg: null, cols: 15, rows: 20, cell: 32,
    body: [], prev: [], dir: { x: 1, y: 0 }, queue: [],
    food: null, bonus: null, bonusLeft: 0, obstacles: [],
    acc: 0, tickMs: 150, eaten: 0, dirName: 'right',
    init: function (difficulty) {
      var conf = (CONFIG.snake && CONFIG.snake[difficulty]) || {};
      this.cfg = {
        tick: conf.tickMs || 150, minTick: conf.minTickMs || 85,
        obstacles: !!conf.obstacles, bonusEvery: conf.bonusEvery || 5
      };
      this.cell = 32;
      this.cols = Math.floor(VW / this.cell);
      this.rows = Math.floor(VH / this.cell);
      this.reset();
    },
    reset: function () {
      this.delay = 0;
      var cx = Math.floor(this.cols / 2);
      var cy = Math.floor(this.rows / 2);
      this.body = [
        { x: cx, y: cy }, { x: cx - 1, y: cy }, { x: cx - 2, y: cy }, { x: cx - 3, y: cy }
      ];
      this.prev = this.body.map(function (p) { return { x: p.x, y: p.y }; });
      this.dir = { x: 1, y: 0 };
      this.dirName = 'right';
      this.queue = [];
      this.acc = 0;
      this.tickMs = this.cfg.tick;
      this.eaten = 0;
      this.bonus = null;
      this.bonusLeft = 0;
      this.obstacles = [];
      this.food = { x: cx + 4, y: cy };
      el.stage.setAttribute('data-dir', '1,0');
    },
    queueDir: function (x, y) {
      var last = this.queue.length ? this.queue[this.queue.length - 1] : this.dir;
      if (x === -last.x && y === -last.y) return false;
      if (x === last.x && y === last.y) return false;
      if (this.queue.length >= 2) return false;
      this.queue.push({ x: x, y: y });
      el.stage.setAttribute('data-dir', x + ',' + y);
      this.dirName = DIR_NAME[x + ',' + y] || this.dirName;
      return true;
    },
    update: function (dt) {
      if (this.delay > 0) {
        this.delay -= dt;
        if (this.delay <= 0) setStatus('시작! 방향을 바꿔 벽을 피하세요.');
        return;
      }
      this.acc += dt * 1000;
      var guard = 0;
      while (this.acc >= this.tickMs && guard < 8) {
        this.acc -= this.tickMs;
        this.step();
        guard += 1;
      }
      if (this.bonusLeft > 0) {
        this.bonusLeft -= dt;
        if (this.bonusLeft <= 0) { this.bonus = null; this.bonusLeft = 0; }
      }
    },
    step: function () {
      this.prev = this.body.map(function (p) { return { x: p.x, y: p.y }; });
      if (this.queue.length) this.dir = this.queue.shift();
      var head = { x: this.body[0].x + this.dir.x, y: this.body[0].y + this.dir.y };
      if (head.x < 0 || head.x >= this.cols || head.y < 0 || head.y >= this.rows) { this.crash('벽에 부딪혔습니다.'); return; }
      for (var i = 0; i < this.body.length - 1; i += 1) {
        if (this.body[i].x === head.x && this.body[i].y === head.y) { this.crash('몸에 부딪혔습니다.'); return; }
      }
      for (var j = 0; j < this.obstacles.length; j += 1) {
        if (this.obstacles[j].x === head.x && this.obstacles[j].y === head.y) { this.crash('장애물에 부딪혔습니다.'); return; }
      }
      this.body.unshift(head);
      var ate = !!(this.food && head.x === this.food.x && head.y === this.food.y);
      var bonusAte = !!(this.bonus && head.x === this.bonus.x && head.y === this.bonus.y);
      if (bonusAte) { this.bonus = null; this.bonusLeft = 0; }
      if (ate || bonusAte) {
        this.eaten += 1;
        var base = bonusAte ? 30 : 10;
        var gain = base + Math.floor(this.body.length / 5) * 2 + (this.cfg.obstacles ? 2 : 0);
        addScore(gain);
        if (ate) this.spawnFood();
        if (!bonusAte && this.eaten % this.cfg.bonusEvery === 0) this.spawnBonus();
        this.tickMs = Math.max(this.cfg.minTick, this.cfg.tick - this.eaten * 3);
        if (this.cfg.obstacles && this.eaten % 4 === 0) this.spawnObstacle();
      } else {
        this.body.pop();
      }
      syncHud();
    },
    freeCell: function () {
      var occupied = {};
      var mark = function (p) { if (p) occupied[p.x + ',' + p.y] = 1; };
      this.body.forEach(mark);
      mark(this.food);
      mark(this.bonus);
      this.obstacles.forEach(mark);
      var free = [];
      for (var y = 0; y < this.rows; y += 1) {
        for (var x = 0; x < this.cols; x += 1) {
          if (!occupied[x + ',' + y]) free.push({ x: x, y: y });
        }
      }
      if (!free.length) return null;
      return free[Math.floor(Math.random() * free.length)];
    },
    spawnFood: function () { this.food = this.freeCell(); },
    spawnBonus: function () {
      var cell = this.freeCell();
      if (!cell) return;
      this.bonus = cell;
      this.bonusLeft = 7;
    },
    spawnObstacle: function () {
      for (var tries = 0; tries < 20; tries += 1) {
        var cell = this.freeCell();
        if (!cell) return;
        var dist = Math.abs(cell.x - this.body[0].x) + Math.abs(cell.y - this.body[0].y);
        if (dist >= 4) { this.obstacles.push(cell); return; }
      }
    },
    crash: function (reason) {
      endRun(reason);
    },
    render: function (g) {
      var cell = this.cell;
      var prog = Math.max(0, Math.min(1, this.acc / this.tickMs));
      g.strokeStyle = 'rgba(255,255,255,0.045)';
      g.lineWidth = 1;
      for (var gx = 1; gx < this.cols; gx += 1) {
        g.beginPath(); g.moveTo(gx * cell, 0); g.lineTo(gx * cell, VH); g.stroke();
      }
      for (var gy = 1; gy < this.rows; gy += 1) {
        g.beginPath(); g.moveTo(0, gy * cell); g.lineTo(VW, gy * cell); g.stroke();
      }
      for (var o = 0; o < this.obstacles.length; o += 1) {
        var ob = this.obstacles[o];
        roundRect(g, ob.x * cell + 3, ob.y * cell + 3, cell - 6, cell - 6, 6);
        g.fillStyle = 'rgba(148,163,184,0.55)';
        g.fill();
      }
      if (this.food) {
        var fx = this.food.x * cell + cell / 2;
        var fy = this.food.y * cell + cell / 2;
        g.beginPath(); g.arc(fx, fy, cell * 0.3, 0, Math.PI * 2);
        g.fillStyle = '#ff6b6b'; g.fill();
        g.beginPath(); g.arc(fx, fy, cell * 0.43, 0, Math.PI * 2);
        g.strokeStyle = 'rgba(255,107,107,0.38)'; g.lineWidth = 2; g.stroke();
      }
      if (this.bonus) {
        var bx = this.bonus.x * cell + cell / 2;
        var by = this.bonus.y * cell + cell / 2;
        g.save();
        g.translate(bx, by);
        g.rotate(Math.PI / 4);
        roundRect(g, -cell * 0.23, -cell * 0.23, cell * 0.46, cell * 0.46, 5);
        g.fillStyle = '#f6c343';
        g.fill();
        g.restore();
      }
      for (var i = this.body.length - 1; i >= 0; i -= 1) {
        var cur = this.body[i];
        var old = this.prev[i] || cur;
        var ix = (old.x + (cur.x - old.x) * prog) * cell;
        var iy = (old.y + (cur.y - old.y) * prog) * cell;
        var t = i / Math.max(1, this.body.length - 1);
        var r = Math.round(49 + t * 70);
        var gg = Math.round(130 + t * 46);
        g.fillStyle = i === 0 ? '#8fc1fe' : 'rgba(' + r + ',' + gg + ',246,' + (0.95 - t * 0.38).toFixed(2) + ')';
        roundRect(g, ix + 2, iy + 2, cell - 4, cell - 4, 8);
        g.fill();
      }
      var head = this.body[0];
      var headOld = this.prev[0] || head;
      var hx = (headOld.x + (head.x - headOld.x) * prog) * cell + cell / 2;
      var hy = (headOld.y + (head.y - headOld.y) * prog) * cell + cell / 2;
      g.fillStyle = '#0b1526';
      g.beginPath(); g.arc(hx - 4.5, hy - 4, 2.2, 0, Math.PI * 2); g.fill();
      g.beginPath(); g.arc(hx + 4.5, hy - 4, 2.2, 0, Math.PI * 2); g.fill();
    }
  };

  /* ------------------------------------------------------------ 캔버스 크기 · 렌더 루프 */
  function resizeCanvas() {
    var rect = canvas.getBoundingClientRect();
    var cssW = Math.max(1, Math.round(rect.width));
    var cssH = Math.max(1, Math.round(rect.height));
    var dpr = Math.min(window.devicePixelRatio || 1, 2.5);
    var pw = Math.round(cssW * dpr);
    var ph = Math.round(cssH * dpr);
    if (canvas.width !== pw) canvas.width = pw;
    if (canvas.height !== ph) canvas.height = ph;
    view.dpr = dpr;
    view.scale = Math.min(cssW / VW, cssH / VH);
    view.ox = (cssW - VW * view.scale) / 2;
    view.oy = (cssH - VH * view.scale) / 2;
  }

  function renderScene() {
    if (!view.scale) return;
    var cssW = canvas.width / view.dpr;
    var cssH = canvas.height / view.dpr;
    ctx.setTransform(view.dpr, 0, 0, view.dpr, 0, 0);
    ctx.clearRect(0, 0, cssW, cssH);
    ctx.save();
    ctx.translate(view.ox, view.oy);
    ctx.scale(view.scale, view.scale);
    ctx.beginPath();
    ctx.rect(0, 0, VW, VH);
    ctx.clip();
    ctx.fillStyle = '#0b1526';
    ctx.fillRect(0, 0, VW, VH);
    var grad = ctx.createLinearGradient(0, 0, 0, VH);
    grad.addColorStop(0, 'rgba(49,130,246,0.18)');
    grad.addColorStop(0.5, 'rgba(11,21,38,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, VW, VH);
    if (state.game === 'brick') Brick.render(ctx); else Snake.render(ctx);
    ctx.restore();
  }

  function loop(ts) {
    window.requestAnimationFrame(loop);
    if (!state.lastTs) state.lastTs = ts;
    var dt = (ts - state.lastTs) / 1000;
    state.lastTs = ts;
    if (!(dt > 0)) dt = 0;
    if (dt > 0.05) dt = 0.05;
    if (state.phase === 'playing') {
      if (state.game === 'brick') Brick.update(dt); else Snake.update(dt);
      syncHud();
    }
    if (!document.hidden) renderScene();
  }

  /* ------------------------------------------------------------ 조작 */
  function setDir(x, y) {
    if (state.game !== 'snake' || state.phase !== 'playing') {
      if (state.game === 'snake') setStatus('시작한 뒤에 방향을 바꿀 수 있습니다.');
      return;
    }
    Snake.queueDir(x, y);
  }

  function pointerX(event) {
    var rect = canvas.getBoundingClientRect();
    if (!view.scale) return VW / 2;
    return (event.clientX - rect.left - view.ox) / view.scale;
  }

  var swipeStart = null;

  canvas.addEventListener('pointerdown', function (event) {
    if (canvas.setPointerCapture) {
      try { canvas.setPointerCapture(event.pointerId); } catch (err) {}
    }
    if (state.game === 'brick') {
      Brick.aim(pointerX(event));
      if (state.phase === 'playing') Brick.launch();
      if (state.phase === 'idle') setStatus('시작하기를 누른 뒤 플레이할 수 있습니다.');
    } else {
      swipeStart = { x: event.clientX, y: event.clientY };
    }
  });

  canvas.addEventListener('pointermove', function (event) {
    if (state.game !== 'brick') return;
    Brick.aim(pointerX(event));
  });

  canvas.addEventListener('pointerup', function (event) {
    if (state.game === 'snake' && swipeStart) {
      var dx = event.clientX - swipeStart.x;
      var dy = event.clientY - swipeStart.y;
      if (Math.max(Math.abs(dx), Math.abs(dy)) >= 22) {
        if (Math.abs(dx) > Math.abs(dy)) setDir(dx > 0 ? 1 : -1, 0);
        else setDir(0, dy > 0 ? 1 : -1);
      }
      swipeStart = null;
    }
  });

  canvas.addEventListener('pointercancel', function () { swipeStart = null; });

  Array.prototype.forEach.call(document.querySelectorAll('.arc-dpad-btn'), function (btn) {
    btn.addEventListener('click', function () {
      var dir = btn.getAttribute('data-dir');
      if (dir === 'up') setDir(0, -1);
      else if (dir === 'down') setDir(0, 1);
      else if (dir === 'left') setDir(-1, 0);
      else if (dir === 'right') setDir(1, 0);
    });
  });

  document.addEventListener('keydown', function (event) {
    var target = event.target;
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) return;
    if (sheetEl && !sheetEl.hidden) return;
    var key = event.key;
    if (state.game === 'brick') {
      if (key === 'ArrowLeft' || key === 'a' || key === 'A') { Brick.keys.left = true; event.preventDefault(); }
      else if (key === 'ArrowRight' || key === 'd' || key === 'D') { Brick.keys.right = true; event.preventDefault(); }
    } else {
      if (key === 'ArrowUp' || key === 'w' || key === 'W') { setDir(0, -1); event.preventDefault(); }
      else if (key === 'ArrowDown' || key === 's' || key === 'S') { setDir(0, 1); event.preventDefault(); }
      else if (key === 'ArrowLeft' || key === 'a' || key === 'A') { setDir(-1, 0); event.preventDefault(); }
      else if (key === 'ArrowRight' || key === 'd' || key === 'D') { setDir(1, 0); event.preventDefault(); }
    }
    if (key === ' ' || key === 'Spacebar') {
      if (state.phase === 'idle' || state.phase === 'over') { event.preventDefault(); startRun(); }
      else if (state.phase === 'playing' && state.game === 'brick') { event.preventDefault(); Brick.launch(); }
      else if (state.phase === 'paused') { event.preventDefault(); resumeRun(); }
    }
    if (key === 'Escape' || key === 'p' || key === 'P') {
      if (state.phase === 'playing' || state.phase === 'paused') { event.preventDefault(); togglePause(); }
    }
  });

  document.addEventListener('keyup', function (event) {
    var key = event.key;
    if (key === 'ArrowLeft' || key === 'a' || key === 'A') Brick.keys.left = false;
    if (key === 'ArrowRight' || key === 'd' || key === 'D') Brick.keys.right = false;
  });

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
      if (state.phase === 'playing') {
        togglePause();
        setStatus('탭을 떠나 자동으로 일시정지했습니다.');
      }
      Brick.keys.left = false;
      Brick.keys.right = false;
    } else {
      state.lastTs = 0;
    }
  });

  /* ------------------------------------------------------------ 게임 방법 프리뷰 */
  function renderGuideSteps(game) {
    var steps = GUIDE[game] || [];
    el.guideSteps.textContent = '';
    for (var i = 0; i < steps.length; i += 1) {
      var li = document.createElement('li');
      li.className = 'arc-step';
      var num = document.createElement('span');
      num.className = 'arc-step-num';
      num.textContent = String(i + 1);
      var text = document.createElement('span');
      text.className = 'arc-step-text';
      text.textContent = steps[i];
      li.appendChild(num);
      li.appendChild(text);
      el.guideSteps.appendChild(li);
    }
    el.guideCaption.textContent = game === 'brick'
      ? '미리보기: 패들이 공을 받아 벽돌을 깨는 장면'
      : '미리보기: 지렁이가 먹이를 먹고 길어지는 장면';
  }

  var Guide = {
    gctx: el.guideCanvas ? el.guideCanvas.getContext('2d') : null,
    raf: null,
    running: false,
    t: 0,
    game: 'brick',
    autoClose: true,
    size: function () {
      var rect = el.guideCanvas.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = Math.max(1, Math.round(rect.width));
      var h = Math.max(1, Math.round(rect.height));
      if (el.guideCanvas.width !== Math.round(w * dpr)) {
        el.guideCanvas.width = Math.round(w * dpr);
        el.guideCanvas.height = Math.round(h * dpr);
      }
      return { w: w, h: h, dpr: dpr };
    },
    draw: function (p) {
      if (!this.gctx) return;
      var s = this.size();
      var g = this.gctx;
      g.setTransform(s.dpr, 0, 0, s.dpr, 0, 0);
      g.clearRect(0, 0, s.w, s.h);
      g.save();
      g.scale(s.w / 300, s.h / 160);
      g.fillStyle = '#0b1526';
      g.fillRect(0, 0, 300, 160);
      var i;
      if (this.game === 'brick') {
        var colors = ['#3182f6', '#4a90f8', '#64a0fb', '#ff6b6b', '#3182f6'];
        for (i = 0; i < 5; i += 1) {
          var blink = 0.55 + 0.45 * Math.abs(Math.sin((p * 2 + i * 0.18) * Math.PI));
          g.globalAlpha = blink;
          g.fillStyle = colors[i];
          roundRect(g, 22 + i * 53, 24, 46, 11, 4);
          g.fill();
        }
        g.globalAlpha = 1;
        var swing = Math.sin(p * Math.PI * 2);
        var padX = 150 + swing * 96;
        var ballX = 150 + Math.sin(p * Math.PI * 4) * 52;
        var ballY = 104 - Math.abs(Math.cos(p * Math.PI * 4)) * 54;
        roundRect(g, padX - 32, 126, 64, 8, 4);
        g.fillStyle = '#e8f1ff';
        g.fill();
        g.beginPath();
        g.arc(ballX, ballY, 5, 0, Math.PI * 2);
        g.fillStyle = '#ffffff';
        g.fill();
        g.font = '600 9px Pretendard, sans-serif';
        g.fillStyle = 'rgba(169,188,216,0.85)';
        g.fillText('드래그 · ←/→ 로 패들 이동', 92, 150);
      } else {
        var cell = 26;
        var ox = 47;
        var oy = 30;
        g.strokeStyle = 'rgba(255,255,255,0.06)';
        g.lineWidth = 1;
        for (i = 1; i < 8; i += 1) {
          g.beginPath(); g.moveTo(ox + i * cell, oy); g.lineTo(ox + i * cell, oy + cell * 4); g.stroke();
        }
        for (i = 1; i < 5; i += 1) {
          g.beginPath(); g.moveTo(ox, oy + i * cell); g.lineTo(ox + cell * 8, oy + i * cell); g.stroke();
        }
        var headIndex = 2 + Math.floor(p * 4);
        for (i = 0; i < 5; i += 1) {
          var hi = headIndex - i;
          if (hi < 0) continue;
          roundRect(g, ox + hi * cell + 2, oy + cell + 2, cell - 4, cell - 4, 6);
          g.fillStyle = i === 0 ? '#8fc1fe' : 'rgba(73,145,246,' + (0.9 - i * 0.12).toFixed(2) + ')';
          g.fill();
        }
        var fx = ox + 7 * cell + cell / 2;
        var fy = oy + cell + cell / 2;
        g.beginPath();
        g.arc(fx, fy, cell * 0.3, 0, Math.PI * 2);
        g.fillStyle = '#ff6b6b';
        g.fill();
        g.font = '600 9px Pretendard, sans-serif';
        g.fillStyle = 'rgba(169,188,216,0.85)';
        g.fillText('스와이프 · 방향키로 이동', 96, 148);
      }
      g.restore();
    },
    stop: function () {
      if (this.raf) { window.cancelAnimationFrame(this.raf); this.raf = null; }
      this.running = false;
    },
    start: function (game, autoClose) {
      this.game = game;
      this.autoClose = autoClose !== false;
      this.t = 0;
      this.stop();
      if (!this.gctx) return;
      if (REDUCE) { this.draw(0.8); return; }
      this.running = true;
      var self = this;
      var last = 0;
      function step(ts) {
        if (!self.running) return;
        if (!last) last = ts;
        var dt = Math.min(0.05, (ts - last) / 1000);
        last = ts;
        self.t += dt;
        var p = Math.min(1, self.t / 3.6);
        self.draw(p);
        if (self.t >= 4.2) {
          self.draw(1);
          self.running = false;
          self.raf = null;
          if (self.autoClose) onGuideDone();
          return;
        }
        self.raf = window.requestAnimationFrame(step);
      }
      this.raf = window.requestAnimationFrame(step);
    }
  };

  var guideAutoClosed = false;

  function onGuideDone() {
    if (guideAutoClosed) return;
    if (el.guideBody.hidden) return;
    guideAutoClosed = true;
    setGuide(false);
    setStatus('게임 방법 안내를 접었습니다. 다시 보기는 게임 방법 카드에 있습니다.');
  }

  function setGuide(open) {
    el.guideBody.hidden = !open;
    el.guideToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    el.guideToggle.textContent = open ? '접기' : '게임 방법';
    if (open) Guide.start(state.game, false);
    else {
      Guide.stop();
      try { localStorage.setItem('arcade_guide_seen_v1', '1'); } catch (err) {}
    }
  }

  el.guideToggle.addEventListener('click', function () { setGuide(el.guideBody.hidden); });
  el.guideReplay.addEventListener('click', function () {
    if (el.guideBody.hidden) setGuide(true);
    else Guide.start(state.game, false);
    setStatus('게임 방법 미리보기를 다시 재생합니다.');
  });

  /* ------------------------------------------------------------ 게임 · 난이도 전환 */
  function switchGame(game) {
    if (state.game === game) return;
    state.game = game;
    resetBoard();
    if (!el.guideBody.hidden) Guide.start(state.game, false);
  }

  function switchDifficulty(difficulty) {
    if (state.difficulty === difficulty) return;
    state.difficulty = difficulty;
    resetBoard();
  }

  el.gameBrick.addEventListener('click', function () { switchGame('brick'); });
  el.gameSnake.addEventListener('click', function () { switchGame('snake'); });
  el.diffNormal.addEventListener('click', function () { switchDifficulty('normal'); });
  el.diffHard.addEventListener('click', function () { switchDifficulty('hard'); });

  el.rankLocal.addEventListener('click', function () { rankMode = 'local'; renderRanks(); });
  el.rankRival.addEventListener('click', function () { rankMode = 'rival'; renderRanks(); });

  el.overlayBtn.addEventListener('click', function () {
    if (state.phase === 'paused') resumeRun();
    else if (state.phase === 'over') { resetBoard(); startRun(); }
    else startRun();
  });
  el.pauseBtn.addEventListener('click', function () { togglePause(); });
  el.quitBtn.addEventListener('click', function () {
    if (state.phase === 'playing' || state.phase === 'paused') endRun('판을 접었습니다.');
  });

  /* ------------------------------------------------------------ 테마 */
  function initTheme() {
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (el.moonIcon) el.moonIcon.style.display = dark ? 'none' : '';
    if (el.sunIcon) el.sunIcon.style.display = dark ? '' : 'none';
  }
  if (el.themeToggle) {
    el.themeToggle.addEventListener('click', function () {
      var root = document.documentElement;
      var dark = root.getAttribute('data-theme') === 'dark';
      if (dark) root.removeAttribute('data-theme');
      else root.setAttribute('data-theme', 'dark');
      try { localStorage.setItem('secjobs-theme', dark ? 'light' : 'dark'); } catch (err) {}
      initTheme();
    });
  }
  initTheme();

  /* ------------------------------------------------------------ 시작 */
  window.addEventListener('resize', resizeCanvas);
  if (window.ResizeObserver) new window.ResizeObserver(resizeCanvas).observe(canvas);
  resizeCanvas();
  resetBoard();
  requestAnimationFrame(function () { resizeCanvas(); renderScene(); });

  var guideSeen = false;
  try { guideSeen = localStorage.getItem('arcade_guide_seen_v1') === '1'; } catch (err) { guideSeen = false; }
  if (guideSeen) {
    el.guideBody.hidden = true;
    el.guideToggle.setAttribute('aria-expanded', 'false');
    el.guideToggle.textContent = '게임 방법';
  } else {
    Guide.start(state.game, true);
  }

  window.requestAnimationFrame(loop);
})();
"""


def build():
    kst_now = datetime.now(KST)
    data = build_data(kst_now)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    html = HTML_TEMPLATE.replace("__CSS__", CSS).replace("__JS__", ARCADE_JS).replace("__DATA_JSON__", payload)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with open(ARCADE_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(ui_shell.apply(html, "arcade")))

    print("-> 'arcade_data.json' 저장 완료 (점수판 %d개 · 기준 라이벌 %d명)"
          % (len(data["boards"]), sum(len(b["rivals"]) for b in data["boards"])))
    print("-> 'arcade.html' 생성 완료 (벽돌깨기 · 지렁이 · 보통/어려움)")
    return {
        "boards": len(data["boards"]),
        "rivals": sum(len(b["rivals"]) for b in data["boards"]),
        "tiers": len(TIERS),
    }


if __name__ == "__main__":
    build()

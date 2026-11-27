# -*- coding: utf-8 -*-
"""보안 취약점 점검 도구 백과사전(security-reference.html) 빌더.

데이터는 security_reference_data.json 하나만 고치면 된다(단일 소스).
8개 분야 × 22개 항목(기본 점검 6분야 12항목 · 오픈소스 점검 툴 7항목 · 진단 패턴·방어 검증 3항목)을
'점검 목적 → 도구·옵션 → 결과 판독 → 조치·재점검' 순서로 읽히게
정적 HTML 로 렌더링한다. 검색·분야 필터는 이미 렌더된 카드의 data 속성만 토글하므로
CSP(인라인 이벤트 핸들러 금지) 아래에서도 동작하고, JS 가 없어도 전체 문서를 읽을 수 있다.

- PC(>=1024px): 좌측 고정 레일(분야·항목 트리, #item-id 딥링크) + 우측 상세 문서
- 모바일(<1024px): 통합 검색 + 분야 필터 칩 + 상세 카드(가로 넘침 0)
- 도구 카드의 복사는 클립보드에만 쓰고, 명령을 실행하거나 외부로 요청하지 않는다.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from html import escape as esc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ui_shell
from html_guard import harden_html, safe_json_for_script

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "security_reference_data.json")
PAGE_PATH = os.path.join(BASE_DIR, "security-reference.html")

IMPACTS = ("로컬 파일 읽기", "네트워크 요청", "별도 변경 승인 필요")
IMPACT_CLASS = {
    "로컬 파일 읽기": "impact-read",
    "네트워크 요청": "impact-net",
    "별도 변경 승인 필요": "impact-change",
}
READING_KEYS = [
    ("normal", "정상 출력", "read-ok"),
    ("abnormal", "이상 징후", "read-no"),
    ("false_positive", "오탐 주의", "read-warn"),
    ("action", "조치", "read-act"),
    ("recheck", "재점검", "read-act"),
]


def esc_attr(value):
    return esc(str(value), quote=True)


def rich(text):
    """백틱으로 감싼 명령·옵션 조각을 인라인 코드로 렌더링한다."""
    parts = str(text).split("`")
    out = []
    for i, part in enumerate(parts):
        out.append('<code class="sr-code">%s</code>' % esc(part) if i % 2 else esc(part))
    return "".join(out)


def impact_pill(value):
    return '<span class="sr-pill %s">%s</span>' % (
        IMPACT_CLASS.get(value, "impact-read"), esc(value)
    )


EXPECTED_PER_CAT = {
    "asset": 2, "web": 2, "tls": 2, "packet": 2, "code": 2, "os": 2,
    "osscan": 7, "probe": 3,
}


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["categories"]) == 8, "분야는 8개여야 합니다."
    assert len(data["items"]) == 22, "항목은 22개여야 합니다."
    ids = [item["id"] for item in data["items"]]
    assert len(ids) == len(set(ids)), "항목 ID 가 중복됩니다."
    for cat in data["categories"]:
        count = sum(1 for item in data["items"] if item["category"] == cat["key"])
        assert count == EXPECTED_PER_CAT[cat["key"]], "%s 분야 항목 수: %d" % (cat["key"], count)
    for item in data["items"]:
        assert item["impact"] in IMPACTS, "알 수 없는 영향 등급: %s" % item["impact"]
        for cmd in item["commands"]:
            assert cmd["impact"] in IMPACTS, "알 수 없는 명령 영향 등급: %s" % cmd["impact"]
        for doc in item["docs"]:
            assert doc["url"].startswith("https://"), "공식 문서는 https 여야 합니다: %s" % doc["url"]
        if item.get("patterns"):
            assert item.get("mock") and item.get("block_log"), "%s: 판별 패턴에는 모의 응답·차단 로그가 필요합니다." % item["id"]
            for pat in item["patterns"]:
                assert pat.get("notation"), "%s: 판별 표기(notation)가 필요합니다." % item["id"]
                assert "payload" not in pat, "%s: 실행 문자열(payload)은 싣지 않습니다." % item["id"]
        else:
            assert item.get("sample"), "%s: 샘플 증적이 필요합니다." % item["id"]
    return data


CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --font-mono: "SFMono-Regular", ui-monospace, "JetBrains Mono", Menlo, Consolas, monospace;

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
      --warn-bg: #fffbeb; --warn-text: #b45309; --warn-border: #fde68a;

      --code-bg: #101828;
      --code-text: #e4e7ec;

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
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);
      --warn-bg: rgba(245, 158, 11, 0.12); --warn-text: #fcd34d; --warn-border: rgba(245, 158, 11, 0.35);

      --code-bg: #0b0f16;
      --code-text: #e4e7ec;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    html { scroll-behavior: smooth; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-page);
      color: var(--text-primary);
      line-height: 1.5;
      letter-spacing: -0.02em;
      word-break: keep-all;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    a { color: inherit; }

    [hidden] { display: none !important; }

    /* 공통 헤더 자리(ui_shell 이 교체한다) */
    .navbar { position: sticky; top: 0; z-index: 50; background: var(--bg-surface); border-bottom: 1px solid var(--border-default); }

    .container {
      max-width: 1360px;
      margin: 0 auto;
      padding: 26px 20px 76px;
    }

    :focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; border-radius: 6px; }

    /* ---------- 히어로 ---------- */
    .sr-eyebrow {
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.12em;
      color: var(--text-muted);
    }

    .sr-title {
      margin: 8px 0 10px;
      font-size: clamp(25px, 3.2vw, 36px);
      font-weight: 800;
      letter-spacing: -0.04em;
      line-height: 1.22;
    }

    .sr-lead {
      max-width: 940px;
      font-size: 14.5px;
      line-height: 1.72;
      color: var(--text-secondary);
    }

    .sr-stats { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }

    .sr-stat {
      display: inline-flex;
      align-items: baseline;
      gap: 6px;
      padding: 6px 12px;
      border: 1px solid var(--border-default);
      border-radius: 999px;
      background: var(--bg-surface);
      font-size: 12px;
      color: var(--text-secondary);
    }
    .sr-stat strong { font-size: 13px; font-weight: 700; color: var(--text-primary); }

    /* ---------- 읽는 순서 ---------- */
    .sr-flow { margin: 26px 0 16px; }
    .sr-flow ol {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      list-style: none;
    }
    .sr-flow li {
      display: flex;
      gap: 11px;
      padding: 14px 15px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
    }
    .sr-flow-no {
      flex: 0 0 auto;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      color: var(--accent-primary);
      padding-top: 2px;
    }
    .sr-flow h2 { font-size: 13.5px; font-weight: 700; letter-spacing: -0.02em; }
    .sr-flow p { margin-top: 3px; font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); }

    /* ---------- 범위 안내 ---------- */
    .sr-scope {
      padding: 16px 18px;
      border: 1px solid var(--border-default);
      border-radius: 16px;
      background: var(--bg-surface);
    }
    .sr-scope h2 { font-size: 13px; font-weight: 700; letter-spacing: -0.02em; }
    .sr-scope p { margin-top: 6px; font-size: 12.5px; line-height: 1.68; color: var(--text-secondary); }
    .sr-scope ul { margin: 10px 0 0; padding-left: 17px; }
    .sr-scope li { font-size: 12px; line-height: 1.75; color: var(--text-secondary); }
    .sr-scope li::marker { color: var(--text-muted); }

    /* ---------- 검색·필터(모바일) ---------- */
    .sr-toolbar {
      display: none;
      position: sticky;
      top: 60px;
      z-index: 40;
      margin: 18px -20px 0;
      padding: 10px 20px 12px;
      background: var(--bg-page);
      border-bottom: 1px solid var(--border-subtle);
    }

    .sr-search { position: relative; }
    .sr-search svg {
      position: absolute;
      left: 13px;
      top: 50%;
      width: 16px;
      height: 16px;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }
    .sr-search input {
      width: 100%;
      height: 42px;
      padding: 0 74px 0 38px;
      border: 1px solid var(--border-default);
      border-radius: 12px;
      background: var(--bg-surface);
      color: var(--text-primary);
      font-family: inherit;
      font-size: 13.5px;
      letter-spacing: -0.02em;
      -webkit-appearance: none;
      appearance: none;
    }
    .sr-search input::placeholder { color: var(--text-muted); }
    .sr-search input:focus { outline: none; border-color: var(--accent-primary); box-shadow: 0 0 0 3px var(--accent-subtle); }

    .sr-clear {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      padding: 5px 9px;
      border: 1px solid var(--border-default);
      border-radius: 8px;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
    }

    .sr-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }

    .sr-chip {
      flex: 0 0 auto;
      padding: 7px 12px;
      border: 1px solid var(--border-default);
      border-radius: 999px;
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: -0.02em;
      white-space: nowrap;
      cursor: pointer;
      transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease, transform 150ms ease;
    }
    .sr-chip:active { transform: scale(0.97); }
    .sr-chip.is-active {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #ffffff;
    }

    .sr-count { margin-top: 9px; font-size: 11.5px; color: var(--text-muted); }

    /* 검색·분야 필터가 걸리면 소개 블록을 접어 결과가 바로 보이게 한다. */
    body.sr-filtering .sr-flow,
    body.sr-filtering .sr-scope { display: none; }

    /* ---------- 레이아웃 ---------- */
    .sr-layout { display: block; margin-top: 22px; }

    .sr-rail {
      display: none;
      position: sticky;
      top: 78px;
      align-self: start;
      max-height: calc(100vh - 100px);
      overflow-y: auto;
      padding: 14px 12px;
      border: 1px solid var(--border-default);
      border-radius: 16px;
      background: var(--bg-surface);
      box-shadow: var(--card-shadow);
      scrollbar-width: thin;
    }

    .sr-rail-head {
      padding: 0 8px 8px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      color: var(--text-muted);
    }

    .sr-tree-cat {
      margin: 13px 8px 5px;
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
    }
    .sr-tree-group:first-child .sr-tree-cat { margin-top: 2px; }

    .sr-tree-link {
      display: flex;
      flex-direction: column;
      gap: 1px;
      padding: 7px 9px;
      border-radius: 9px;
      text-decoration: none;
      color: var(--text-secondary);
      transition: background-color 140ms ease, color 140ms ease;
    }
    .sr-tree-link:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .sr-tree-link.is-active { background: var(--accent-subtle); color: var(--accent-primary); }
    .sr-tree-name { font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.35; }
    .sr-tree-link.is-active .sr-tree-name { font-weight: 700; }
    .sr-tree-tool { font-size: 10.5px; color: var(--text-muted); }

    .sr-doc { min-width: 0; }

    .sr-empty {
      margin-bottom: 14px;
      padding: 14px 16px;
      border: 1px dashed var(--border-strong);
      border-radius: 12px;
      font-size: 13px;
      color: var(--text-secondary);
    }

    /* ---------- 분야 ---------- */
    .sr-cat { margin-bottom: 26px; }
    .sr-cat-head { margin: 4px 0 14px; }
    .sr-cat-kicker {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--text-muted);
    }
    .sr-cat-head h2 {
      margin-top: 3px;
      font-size: 21px;
      font-weight: 750;
      letter-spacing: -0.035em;
    }
    .sr-cat-head p { margin-top: 4px; font-size: 13px; color: var(--text-secondary); }

    /* ---------- 항목 카드 ---------- */
    .sr-item {
      margin-bottom: 16px;
      padding: 20px 22px 22px;
      border: 1px solid var(--border-default);
      border-radius: 18px;
      background: var(--bg-surface);
      box-shadow: var(--card-shadow);
      scroll-margin-top: 78px;
    }
    .sr-item:last-child { margin-bottom: 0; }

    .sr-item-kicker {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--text-muted);
    }
    .sr-item-kicker .sr-dot {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--accent-primary);
    }

    .sr-item-title {
      margin: 6px 0 4px;
      font-size: 19px;
      font-weight: 750;
      letter-spacing: -0.035em;
      line-height: 1.35;
    }
    .sr-item-title:focus { outline: none; }
    .sr-item-title:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 3px; border-radius: 6px; }

    .sr-item-summary { font-size: 13px; line-height: 1.65; color: var(--text-secondary); overflow-wrap: anywhere; }

    .sr-item-badges { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 12px; }

    .sr-tool {
      display: inline-flex;
      align-items: center;
      padding: 4px 9px;
      border: 1px solid var(--border-default);
      border-radius: 8px;
      background: var(--bg-subtle);
      font-family: var(--font-mono);
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-secondary);
    }

    .sr-pill {
      display: inline-flex;
      align-items: center;
      padding: 4px 9px;
      border: 1px solid transparent;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: -0.01em;
      white-space: nowrap;
    }
    .impact-read { background: var(--ok-bg); border-color: var(--ok-border); color: var(--ok-text); }
    .impact-net { background: var(--accent-subtle); border-color: var(--border-strong); color: var(--accent-primary); }
    .impact-change { background: var(--warn-bg); border-color: var(--warn-border); color: var(--warn-text); }

    .sr-copy-link {
      margin-left: auto;
      padding: 5px 10px;
      border: 1px solid var(--border-default);
      border-radius: 8px;
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 140ms ease, color 140ms ease, transform 140ms ease;
    }
    .sr-copy-link:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .sr-copy-link:active { transform: scale(0.97); }

    /* ---------- 고정 필드 ---------- */
    .sr-facts {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px 18px;
      margin-top: 16px;
      padding: 14px 16px;
      border: 1px solid var(--border-subtle);
      border-radius: 13px;
      background: var(--bg-page);
    }
    .sr-facts div { min-width: 0; }
    .sr-facts dt { font-size: 11px; font-weight: 700; letter-spacing: 0.02em; color: var(--text-muted); }
    .sr-facts dd { margin-top: 3px; font-size: 12.5px; line-height: 1.62; color: var(--text-secondary); overflow-wrap: anywhere; }
    .sr-facts dd .sr-pill { margin-right: 6px; }

    .sr-h {
      margin: 22px 0 10px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
      font-size: 12.5px;
      font-weight: 700;
      letter-spacing: 0.01em;
      color: var(--text-secondary);
    }

    /* ---------- 명령 ---------- */
    .sr-cmd {
      margin-bottom: 10px;
      border: 1px solid var(--border-default);
      border-radius: 12px;
      overflow: hidden;
    }
    .sr-cmd-head {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      padding: 8px 11px;
      background: var(--bg-subtle);
    }
    .sr-cmd-label { font-size: 11.5px; font-weight: 700; color: var(--text-secondary); }
    .sr-cmd-head .sr-pill { font-size: 10.5px; padding: 3px 7px; }
    .sr-cmd-copy {
      margin-left: auto;
      padding: 4px 10px;
      border: 1px solid var(--border-default);
      border-radius: 7px;
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 140ms ease, color 140ms ease, transform 140ms ease;
    }
    .sr-cmd-copy:hover { background: var(--bg-muted); color: var(--text-primary); }
    .sr-cmd-copy:active { transform: scale(0.96); }
    .sr-cmd-copy[data-state="done"] { border-color: var(--ok-border); background: var(--ok-bg); color: var(--ok-text); }

    .sr-cmd pre {
      margin: 0;
      padding: 12px 14px;
      background: var(--code-bg);
      color: var(--code-text);
      font-family: var(--font-mono);
      font-size: 12px;
      line-height: 1.62;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      tab-size: 4;
    }

    .sr-cmd-note { margin: 7px 2px 0; font-size: 11.5px; line-height: 1.66; color: var(--text-secondary); overflow-wrap: anywhere; }

    /* ---------- 옵션 표 ---------- */
    .sr-table-wrap { border: 1px solid var(--border-default); border-radius: 12px; overflow-x: auto; }
    .sr-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .sr-table th {
      padding: 9px 11px;
      background: var(--bg-subtle);
      border-bottom: 1px solid var(--border-default);
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      text-align: left;
      white-space: nowrap;
    }
    .sr-table td {
      padding: 9px 11px;
      border-top: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      line-height: 1.6;
      vertical-align: top;
    }
    .sr-table tr:first-child td { border-top: 0; }
    .sr-table td:first-child code { white-space: nowrap; }

    .sr-code {
      padding: 1px 5px;
      border: 1px solid var(--border-default);
      border-radius: 5px;
      background: var(--bg-subtle);
      font-family: var(--font-mono);
      font-size: 0.92em;
      color: var(--text-primary);
      overflow-wrap: anywhere;
    }
    /* 짧은 플래그가 줄 끝에서 쪼개지지 않게 한다(-rl → '-' + 'rl'). */
    .sr-facts .sr-code, .sr-cmd-note .sr-code { white-space: nowrap; }

    /* ---------- 판독 ---------- */
    .sr-read {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
    }
    .sr-read-block {
      padding: 12px 13px;
      border: 1px solid var(--border-default);
      border-left-width: 3px;
      border-radius: 11px;
      background: var(--bg-page);
    }
    .sr-read-block h5 { font-size: 11.5px; font-weight: 700; letter-spacing: 0.01em; }
    .sr-read-block ul { margin-top: 6px; padding-left: 15px; }
    .sr-read-block li { font-size: 12px; line-height: 1.68; color: var(--text-secondary); overflow-wrap: anywhere; }
    .sr-read-block li + li { margin-top: 4px; }
    .read-ok { border-left-color: var(--ok-border); }
    .read-ok h5 { color: var(--ok-text); }
    .read-no { border-left-color: var(--no-border); }
    .read-no h5 { color: var(--no-text); }
    .read-warn { border-left-color: var(--warn-border); }
    .read-warn h5 { color: var(--warn-text); }
    .read-act { border-left-color: var(--border-strong); }
    .read-act h5 { color: var(--accent-primary); }

    /* ---------- 샘플 ---------- */
    .sr-sample { margin: 0; border: 1px solid var(--border-default); border-radius: 12px; overflow: hidden; }
    .sr-sample figcaption {
      padding: 8px 12px;
      background: var(--bg-subtle);
      border-bottom: 1px solid var(--border-default);
      font-size: 11px;
      font-weight: 700;
      color: var(--text-secondary);
    }
    .sr-sample pre {
      margin: 0;
      padding: 12px 14px;
      background: var(--code-bg);
      color: var(--code-text);
      font-family: var(--font-mono);
      font-size: 11.5px;
      line-height: 1.7;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }
    .sr-sample-cap { margin-top: 8px; font-size: 11.5px; line-height: 1.66; color: var(--text-secondary); overflow-wrap: anywhere; }

    /* ---------- 판별 표기 · 모의 응답 ---------- */
    .sr-pattern-table td:first-child { min-width: 168px; }
    .sr-pat-cell { display: flex; flex-direction: column; gap: 5px; align-items: flex-start; }
    .sr-pat-name { font-size: 11.5px; font-weight: 700; color: var(--text-primary); }
    /* 비실행 표기: 복사·실행 대상이 아니라 무엇을 확인하는지 적은 설명문이다. */
    .sr-pat-notation { font-size: 11.5px; line-height: 1.6; color: var(--text-secondary); overflow-wrap: anywhere; }
    .sr-mock { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .sr-mock .sr-sample { min-width: 0; }
    .sr-mock .sr-sample pre { white-space: pre-wrap; overflow-wrap: anywhere; }
    .sr-mock-safe figcaption { color: var(--ok-text); }
    .sr-mock-vuln figcaption { color: var(--no-text); }
    .sr-blocklog pre { white-space: pre-wrap; overflow-wrap: anywhere; }
    .sr-sub { margin: 16px 2px 8px; font-size: 11.5px; font-weight: 700; color: var(--text-muted); }

    /* ---------- 문서·연결 ---------- */
    .sr-foot {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
    }
    .sr-foot h5 { font-size: 11px; font-weight: 700; letter-spacing: 0.04em; color: var(--text-muted); }
    .sr-foot ul { list-style: none; margin-top: 7px; display: flex; flex-wrap: wrap; gap: 6px; }
    .sr-foot a {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 5px 9px;
      border: 1px solid var(--border-default);
      border-radius: 8px;
      background: var(--bg-surface);
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-secondary);
      text-decoration: none;
      transition: background-color 140ms ease, color 140ms ease, border-color 140ms ease;
    }
    .sr-foot a:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .sr-foot a.sr-doc-link { color: var(--accent-primary); }
    .sr-foot .sr-link-kind { font-size: 10px; font-weight: 700; color: var(--text-muted); }

    /* ---------- 반응형 ---------- */
    @media (min-width: 1024px) {
      .sr-layout {
        display: grid;
        grid-template-columns: 264px minmax(0, 1fr);
        gap: 30px;
        align-items: start;
      }
      .sr-rail { display: block; }
    }

    @media (max-width: 1100px) {
      .sr-flow ol { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 1023px) {
      .sr-toolbar { display: block; }
      .sr-layout { margin-top: 18px; }
      .sr-item { scroll-margin-top: 186px; }
    }

    @media (max-width: 768px) {
      .container { padding: 20px 14px 84px; }
      .sr-toolbar { top: 54px; margin-left: -14px; margin-right: -14px; padding-left: 14px; padding-right: 14px; }
      .sr-title { font-size: 24px; }
      .sr-lead { font-size: 13.5px; }
      .sr-flow ol { grid-template-columns: 1fr; gap: 8px; }
      .sr-flow li { padding: 12px 13px; }
      /* 분야 칩 9개가 여러 줄로 늘어나 상단을 가리지 않도록 한 줄 가로 스크롤로 둔다. */
      .sr-chips { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 4px; scrollbar-width: none; }
      .sr-chips::-webkit-scrollbar { display: none; }
      .sr-chip { flex: 0 0 auto; }
      .sr-item { padding: 16px 15px 18px; border-radius: 15px; }
      .sr-item-title { font-size: 17.5px; }
      .sr-cat-head h2 { font-size: 19px; }
      .sr-facts { grid-template-columns: 1fr; gap: 10px; }
      .sr-read { grid-template-columns: 1fr; }
      .sr-mock { grid-template-columns: 1fr; }
      .sr-foot { grid-template-columns: 1fr; gap: 14px; }
      .sr-copy-link { margin-left: 0; }
      .sr-table { min-width: 480px; }
      /* 판별 패턴은 모바일에서 표 대신 카드처럼 쌓아 옆으로 스크롤하지 않게 한다. */
      .sr-pattern-table { min-width: 0; }
      .sr-pattern-table thead { display: none; }
      .sr-pattern-table, .sr-pattern-table tbody, .sr-pattern-table tr, .sr-pattern-table td { display: block; width: 100%; }
      .sr-pattern-table tr { padding: 11px 2px; border-top: 1px solid var(--border-subtle); }
      .sr-pattern-table tr:first-child { border-top: 0; }
      .sr-pattern-table td { padding: 3px 0; border: 0; }
      .sr-pattern-table td:first-child { min-width: 0; }
      .sr-pattern-table td[data-label]::before {
        content: attr(data-label);
        display: block;
        margin-bottom: 2px;
        font-size: 10.5px;
        font-weight: 700;
        color: var(--text-muted);
      }
    }

    @media (max-width: 380px) {
      .container { padding-left: 11px; padding-right: 11px; }
      .sr-toolbar { margin-left: -11px; margin-right: -11px; padding-left: 11px; padding-right: 11px; }
      .sr-item { padding: 14px 12px 16px; }
    }

    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
    }
"""

JS = r"""
    // ---- 테마(다른 페이지와 같은 secjobs-theme 키) ----
    (function initTheme() {
      const toggle = document.getElementById('themeToggle');
      const moon = document.getElementById('moonIcon');
      const sun = document.getElementById('sunIcon');
      function setTheme(dark) {
        if (dark) {
          document.documentElement.setAttribute('data-theme', 'dark');
          if (moon) moon.style.display = 'none';
          if (sun) sun.style.display = 'block';
        } else {
          document.documentElement.removeAttribute('data-theme');
          if (moon) moon.style.display = 'block';
          if (sun) sun.style.display = 'none';
        }
      }
      let saved = null;
      try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
      setTheme(saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches));
      if (toggle) {
        toggle.addEventListener('click', function () {
          const dark = document.documentElement.getAttribute('data-theme') === 'dark';
          setTheme(!dark);
          try { localStorage.setItem('secjobs-theme', dark ? 'light' : 'dark'); } catch (e) {}
        });
      }
    })();

    // ---- 검색 · 분야 필터 · 딥링크 · 복사 ----
    (function initReference() {
      const $ = function (id) { return document.getElementById(id); };
      const items = Array.prototype.slice.call(document.querySelectorAll('.sr-item'));
      const sections = Array.prototype.slice.call(document.querySelectorAll('.sr-cat'));
      const links = Array.prototype.slice.call(document.querySelectorAll('.sr-tree-link'));
      const search = $('srSearch');
      const clearBtn = $('srSearchClear');
      const chips = Array.prototype.slice.call(document.querySelectorAll('.sr-chip'));
      const count = $('srCount');
      const empty = $('srEmpty');
      const state = { q: '', cat: 'all' };

      const catLabel = { all: '전체' };
      chips.forEach(function (chip) {
        catLabel[chip.getAttribute('data-cat')] = chip.textContent.trim();
      });

      function setActive(id) {
        links.forEach(function (link) {
          const on = link.getAttribute('data-target') === id;
          link.classList.toggle('is-active', on);
          if (on) link.setAttribute('aria-current', 'true');
          else link.removeAttribute('aria-current');
        });
      }

      function applyCount(shown) {
        if (!count) return;
        count.textContent = shown + '개 항목' + (state.cat === 'all' ? '' : ' · ' + (catLabel[state.cat] || ''));
      }

      let wasFiltering = false;

      function applyFilter() {
        const q = state.q.trim().toLowerCase();
        const filtering = q.length > 0 || state.cat !== 'all';
        document.body.classList.toggle('sr-filtering', filtering);
        if (filtering && !wasFiltering) {
          const bar = $('srToolbar');
          if (bar && window.innerWidth < 1024) bar.scrollIntoView({ block: 'start', behavior: 'instant' });
        }
        wasFiltering = filtering;
        let shown = 0;
        items.forEach(function (el) {
          const catOk = state.cat === 'all' || el.getAttribute('data-cat') === state.cat;
          const text = el.getAttribute('data-search') || '';
          const qOk = !q || text.indexOf(q) !== -1;
          const show = catOk && qOk;
          el.hidden = !show;
          if (show) shown += 1;
        });
        sections.forEach(function (sec) {
          sec.hidden = !sec.querySelector('.sr-item:not([hidden])');
        });
        applyCount(shown);
        if (empty) empty.hidden = shown !== 0;
        if (clearBtn) clearBtn.hidden = state.q.length === 0;
      }

      function resetFilters() {
        state.q = '';
        state.cat = 'all';
        if (search) search.value = '';
        chips.forEach(function (chip) {
          const on = chip.getAttribute('data-cat') === 'all';
          chip.classList.toggle('is-active', on);
          chip.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        applyFilter();
      }

      let suppressSpyUntil = 0;

      function scrollToItem(el) {
        if (!el) return;
        // 이동 직후 스크롤 위치를 읽는 감시가 방금 고른 항목을 덮어쓰지 않게 잠시 멈춘다.
        suppressSpyUntil = Date.now() + 900;
        el.scrollIntoView({ block: 'start', behavior: 'instant' });
        const title = el.querySelector('.sr-item-title');
        if (title) {
          title.setAttribute('tabindex', '-1');
          try { title.focus({ preventScroll: true }); } catch (e) { title.focus(); }
        }
      }

      function openHash(hash, doScroll) {
        const id = String(hash || '').replace(/^#/, '');
        if (!id) return false;
        const el = document.getElementById(id);
        if (!el || !el.classList.contains('sr-item')) return false;
        if (el.hidden) resetFilters();
        setActive(id);
        if (doScroll) scrollToItem(el);
        return true;
      }

      if (search) {
        search.addEventListener('input', function () {
          state.q = search.value || '';
          applyFilter();
        });
        search.addEventListener('keydown', function (event) {
          if (event.key === 'Escape') {
            resetFilters();
            search.blur();
          }
        });
      }
      if (clearBtn) clearBtn.addEventListener('click', function () { resetFilters(); if (search) search.focus(); });

      chips.forEach(function (chip) {
        chip.addEventListener('click', function () {
          state.cat = chip.getAttribute('data-cat');
          chips.forEach(function (other) {
            const on = other === chip;
            other.classList.toggle('is-active', on);
            other.setAttribute('aria-pressed', on ? 'true' : 'false');
          });
          applyFilter();
        });
      });

      links.forEach(function (link) {
        link.addEventListener('click', function (event) {
          const id = link.getAttribute('data-target');
          if (!id) return;
          // 보조키 클릭(Ctrl/Cmd/Shift/Alt)과 가운데·오른쪽 버튼은 브라우저 기본 동작
          // (새 탭/새 창/새 창에서 열기)에 맡긴다. preventDefault 하면 새 탭이 열리지 않는다.
          if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
          event.preventDefault();
          if (history.pushState) history.pushState(null, '', '#' + id);
          else location.hash = '#' + id;
          openHash('#' + id, true);
        });
      });

      window.addEventListener('hashchange', function () { openHash(location.hash, true); });

      // 스크롤 위치에 따라 레일의 현재 항목을 표시한다(한 번에 하나만).
      let ticking = false;
      function syncActive() {
        ticking = false;
        if (window.innerWidth < 1024) return;
        // 모바일에서 걸어 둔 필터 상태로 넓은 화면에 들어오면 소개 블록을 되살린다.
        if (document.body.classList.contains('sr-filtering')) resetFilters();
        if (Date.now() < suppressSpyUntil) return;
        let currentId = null;
        for (let i = 0; i < items.length; i += 1) {
          if (items[i].hidden) continue;
          const top = items[i].getBoundingClientRect().top;
          if (top - 140 <= 0) currentId = items[i].id;
        }
        if (!currentId && items.length) currentId = items[0].id;
        if (currentId) setActive(currentId);
      }
      window.addEventListener('scroll', function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(syncActive);
      }, { passive: true });
      window.addEventListener('resize', syncActive);

      // 복사: 클립보드에만 쓰고 명령을 실행하지 않는다.
      function copyText(text) {
        if (navigator.clipboard && window.isSecureContext) {
          return navigator.clipboard.writeText(text);
        }
        return new Promise(function (resolve, reject) {
          try {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.setAttribute('readonly', '');
            ta.style.position = 'fixed';
            ta.style.top = '-1000px';
            document.body.appendChild(ta);
            ta.select();
            const ok = document.execCommand('copy');
            document.body.removeChild(ta);
            if (ok) resolve(); else reject(new Error('copy rejected'));
          } catch (error) { reject(error); }
        });
      }

      function markCopied(btn, ok) {
        const original = btn.getAttribute('data-label') || btn.textContent;
        btn.setAttribute('data-state', ok ? 'done' : 'fail');
        btn.textContent = ok ? '복사됨' : '직접 선택';
        window.clearTimeout(btn.__timer);
        btn.__timer = window.setTimeout(function () {
          btn.removeAttribute('data-state');
          btn.textContent = original;
        }, 1600);
      }

      document.addEventListener('click', function (event) {
        const target = event.target;
        if (!target || !target.closest) return;

        const cmdBtn = target.closest('[data-copy-cmd]');
        if (cmdBtn) {
          const pre = document.getElementById(cmdBtn.getAttribute('data-copy-cmd'));
          if (!pre) return;
          const text = pre.textContent;
          window.__srCopied = text;
          copyText(text).then(function () { markCopied(cmdBtn, true); }, function () {
            // 클립보드가 막힌 환경에서도 코드를 선택해 두어 바로 복사할 수 있게 한다.
            try {
              const range = document.createRange();
              range.selectNodeContents(pre);
              const sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(range);
            } catch (e) {}
            markCopied(cmdBtn, false);
          });
          return;
        }

        const linkBtn = target.closest('[data-copy-link]');
        if (linkBtn) {
          const id = linkBtn.getAttribute('data-copy-link');
          const url = location.origin + location.pathname + '#' + id;
          window.__srCopied = url;
          copyText(url).then(function () { markCopied(linkBtn, true); }, function () { markCopied(linkBtn, false); });
        }
      });

      applyFilter();
      if (!openHash(location.hash, true)) syncActive();
    })();
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 보안 취약점 점검 도구 백과사전</title>
  <meta name="description" content="점검 목적에서 도구 선택, 결과 판독, 조치와 재점검까지 한 흐름으로 읽는 보안 점검 도구 백과사전. 8개 분야 22개 항목의 대표 명령, 옵션별 영향, 오픈소스 점검 툴(nuclei·ffuf·sqlmap·nikto·subfinder·httpx·testssl.sh), 취약점별 판별 패턴과 모의 응답·차단 로그, 공식 문서 링크를 한 페이지에 정리했습니다.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
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
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>__BUILT_AT__ 기준</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="화면 테마 변경">
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
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기" aria-label="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <main class="container">

    <section class="sr-hero" aria-labelledby="srTitle">
      <span class="sr-eyebrow">SECURITY REFERENCE</span>
      <h1 class="sr-title" id="srTitle">__TITLE__</h1>
      <p class="sr-lead">__INTRO__</p>
      <div class="sr-stats">
        <span class="sr-stat">분야 <strong>__CAT_COUNT__</strong></span>
        <span class="sr-stat">항목 <strong>__ITEM_COUNT__</strong></span>
        <span class="sr-stat">대표 명령 <strong>__CMD_COUNT__</strong></span>
        <span class="sr-stat">실행 없이 복사만</span>
      </div>
    </section>

    <div class="sr-toolbar" id="srToolbar">
      <div class="sr-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
          <circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.4" y2="16.4"></line>
        </svg>
        <input type="search" id="srSearch" placeholder="도구·옵션·판별 표기 검색 (예: nuclei, openssl, HSTS, SSRF)" autocomplete="off" aria-label="도구·옵션·점검 목적 검색">
        <button type="button" class="sr-clear" id="srSearchClear" hidden>지우기</button>
      </div>
      <div class="sr-chips" role="group" aria-label="분야 필터">
        <button type="button" class="sr-chip is-active" data-cat="all" aria-pressed="true">전체</button>
__CHIPS__
      </div>
      <p class="sr-count" id="srCount" role="status" aria-live="polite">__ITEM_COUNT__개 항목</p>
    </div>

    <section class="sr-flow" aria-label="읽는 순서">
      <ol>
__FLOW__
      </ol>
    </section>

    <section class="sr-scope" aria-labelledby="srScopeTitle">
      <h2 id="srScopeTitle">__SCOPE_TITLE__</h2>
      <p>__SCOPE_BODY__</p>
      <ul>
__SCOPE_RULES__
      </ul>
    </section>


    <div class="sr-layout" id="srLayout">
      <aside class="sr-rail" aria-label="분야·항목 인덱스">
        <p class="sr-rail-head">인덱스</p>
        <nav class="sr-tree">
__RAIL__
        </nav>
      </aside>

      <div class="sr-doc">
        <p class="sr-empty" id="srEmpty" hidden>조건에 맞는 항목이 없습니다. 다른 도구명이나 옵션으로 찾아보세요.</p>
__SECTIONS__
      </div>
    </div>

  </main>

  <script type="application/json" id="srData">__DATA__</script>
  <script>__JS__</script>
</body>
</html>
"""


def build():
    data = load_data()
    kst = timezone(timedelta(hours=9))
    built_at = datetime.now(kst).strftime("%Y-%m-%d %H:%M KST")
    cats = {c["key"]: c for c in data["categories"]}
    items_by_cat = {key: [] for key in cats}
    for item in data["items"]:
        items_by_cat[item["category"]].append(item)

    flow_html = []
    for step in data["flow"]:
        flow_html.append(
            '        <li><span class="sr-flow-no">%s</span><div><h2>%s</h2><p>%s</p></div></li>'
            % (esc(step["step"]), esc(step["title"]), esc(step["desc"]))
        )

    chips = []
    for cat in data["categories"]:
        chips.append(
            '        <button type="button" class="sr-chip" data-cat="%s" aria-pressed="false">%s</button>'
            % (esc_attr(cat["key"]), esc(cat["label"]))
        )

    rail = []
    for ci, cat in enumerate(data["categories"], start=1):
        rail.append('          <div class="sr-tree-group">')
        rail.append('            <p class="sr-tree-cat">%s</p>' % esc(cat["label"]))
        for item in items_by_cat[cat["key"]]:
            rail.append(
                '            <a class="sr-tree-link" href="#%s" data-target="%s">'
                '<span class="sr-tree-name">%s</span>'
                '<span class="sr-tree-tool">%s</span></a>'
                % (esc_attr(item["id"]), esc_attr(item["id"]), esc(item["title"]), esc(item["tool"]))
            )
        rail.append("          </div>")

    cmd_total = 0
    sections = []
    index = 0
    for ci, cat in enumerate(data["categories"], start=1):
        sections.append('        <section class="sr-cat" id="cat-%s">' % esc_attr(cat["key"]))
        sections.append('          <header class="sr-cat-head">')
        sections.append('            <p class="sr-cat-kicker">분야 %02d</p>' % ci)
        sections.append('            <h2>%s</h2>' % esc(cat["label"]))
        sections.append('            <p>%s</p>' % esc(cat["desc"]))
        sections.append("          </header>")

        for item in items_by_cat[cat["key"]]:
            index += 1
            sections.append(render_item(item, index, cat["label"], items_by_cat, data))
        sections.append("        </section>")

    manifest = {
        "version": data["version"],
        "updated": data["updated"],
        "built_at": built_at,
        "total": len(data["items"]),
        "ids": [item["id"] for item in data["items"]],
        "categories": [
            {
                "key": cat["key"],
                "label": cat["label"],
                "items": [item["id"] for item in items_by_cat[cat["key"]]],
            }
            for cat in data["categories"]
        ],
    }
    cmd_total = sum(len(item["commands"]) for item in data["items"])

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__JS__", JS)
    html = html.replace("__TITLE__", esc(data["title"]))
    html = html.replace("__INTRO__", esc(data["intro"]))
    html = html.replace("__FLOW__", "\n".join(flow_html))
    html = html.replace("__SCOPE_TITLE__", esc(data["scope"]["title"]))
    html = html.replace("__SCOPE_BODY__", esc(data["scope"]["body"]))
    html = html.replace("__SCOPE_RULES__", "\n".join(
        "          <li>%s</li>" % esc(rule) for rule in data["scope"]["rules"]
    ))
    html = html.replace("__CHIPS__", "\n".join(chips))
    html = html.replace("__RAIL__", "\n".join(rail))
    html = html.replace("__SECTIONS__", "\n".join(sections))
    html = html.replace("__DATA__", safe_json_for_script(json.dumps(manifest, ensure_ascii=False)))
    html = html.replace("__CAT_COUNT__", str(len(data["categories"])))
    html = html.replace("__ITEM_COUNT__", str(len(data["items"])))
    html = html.replace("__CMD_COUNT__", str(cmd_total))
    html = html.replace("__BUILT_AT__", built_at)

    with open(PAGE_PATH, "w", encoding="utf-8") as f:
        f.write(harden_html(ui_shell.apply(html, "reference")))

    print("-> 'security-reference.html' 생성 완료 (분야 %d · 항목 %d · 대표 명령 %d)"
          % (len(data["categories"]), len(data["items"]), cmd_total))
    return {
        "categories": len(data["categories"]),
        "items": len(data["items"]),
        "commands": cmd_total,
        "builtAt": built_at,
    }


def render_item(item, index, cat_label, items_by_cat, data):
    out = []
    search_blob = " ".join([
        item["title"], item["tool"], item["summary"], item["purpose"], cat_label,
        " ".join(item.get("aliases") or []),
        " ".join(cmd["label"] + " " + cmd["cmd"] for cmd in item["commands"]),
        " ".join("%s %s" % (opt["flag"], opt["meaning"]) for opt in item.get("options") or []),
        " ".join("%s %s %s %s" % (p["name"], p.get("notation", ""), p["where"], p["principle"])
                  for p in item.get("patterns") or []),
        (item.get("mock") or {}).get("title", ""),
    ])
    search_blob = " ".join(search_blob.replace("`", " ").split()).lower()
    # 검색어 색인에는 꺾쇠·따옴표·앰퍼샌드를 남기지 않는다(태그처럼 보이는 문자열이 속성에 들어가지 않게).
    for ch in ("<", ">", '"', "&"):
        search_blob = search_blob.replace(ch, " ")

    out.append('          <article class="sr-item" id="%s" data-cat="%s" data-search="%s">'
               % (esc_attr(item["id"]), esc_attr(item["category"]), esc_attr(search_blob)))
    out.append('            <p class="sr-item-kicker"><span class="sr-dot"></span>%s · %02d</p>'
               % (esc(cat_label), index))
    out.append('            <h3 class="sr-item-title">%s</h3>' % esc(item["title"]))
    out.append('            <p class="sr-item-summary">%s</p>' % esc(item["summary"]))
    out.append('            <div class="sr-item-badges">')
    out.append('              <span class="sr-tool">%s</span>' % esc(item["tool"]))
    out.append("              " + impact_pill(item["impact"]))
    out.append('              <button type="button" class="sr-copy-link" data-copy-link="%s" data-label="링크 복사">링크 복사</button>'
               % esc_attr(item["id"]))
    out.append("            </div>")

    out.append('            <dl class="sr-facts">')
    out.append('              <div><dt>점검 목적</dt><dd>%s</dd></div>' % rich(item["purpose"]))
    out.append('              <div><dt>검증 기준 버전</dt><dd>%s</dd></div>' % rich(item["verified_version"]))
    out.append('              <div><dt>입력·대상</dt><dd>%s</dd></div>' % rich(item["input_type"]))
    out.append('              <div><dt>필요 권한</dt><dd>%s</dd></div>' % rich(item["privilege"]))
    out.append('              <div><dt>실행 영향 등급</dt><dd>%s %s</dd></div>'
               % (impact_pill(item["impact"]), rich(item["impact_note"])))
    out.append("            </dl>")

    if item.get("report"):
        out.append('            <h4 class="sr-h">보고서 필드</h4>')
        out.append('            <p class="sr-sub">%s</p>' % rich(item["report"]["format"]))
        out.append('            <div class="sr-table-wrap">')
        out.append('              <table class="sr-table">')
        out.append('                <thead><tr><th scope="col">필드</th><th scope="col">의미</th><th scope="col">판독 포인트</th></tr></thead>')
        out.append("                <tbody>")
        for field in item["report"]["fields"]:
            out.append('                  <tr><td><code class="sr-code">%s</code></td><td>%s</td><td>%s</td></tr>'
                       % (esc(field["name"]), rich(field["meaning"]), rich(field["note"])))
        out.append("                </tbody>")
        out.append("              </table>")
        out.append("            </div>")

    if item.get("patterns"):
        out.append('            <h4 class="sr-h">판별 표기 (비실행)</h4>')
        out.append('            <p class="sr-sub">실행할 문자열 대신 무엇을 확인하는지 적은 표기입니다. 복사·전송 없이, 저장된 모의 응답·차단 로그·테스트 결과 JSON과 대조해 판정합니다.</p>')
        out.append('            <div class="sr-table-wrap">')
        out.append('              <table class="sr-table sr-pattern-table">')
        out.append('                <thead><tr><th scope="col">확인 표기</th><th scope="col">위치 · 판별 원리</th><th scope="col">안전(차단) 신호</th><th scope="col">취약 신호</th></tr></thead>')
        out.append("                <tbody>")
        for pat in item["patterns"]:
            out.append('                  <tr><td><div class="sr-pat-cell">'
                       '<span class="sr-pat-name">%s</span>'
                       '<span class="sr-pat-notation">%s</span>'
                       '</div></td>'
                       '<td data-label="위치 · 판별 원리"><span class="sr-pat-name">%s</span><br>%s</td>'
                       '<td data-label="안전(차단) 신호">%s</td><td data-label="취약 신호">%s</td></tr>'
                       % (esc(pat["name"]), esc(pat["notation"]),
                          esc(pat["where"]), rich(pat["principle"]), rich(pat["safe"]), rich(pat["vulnerable"])))
        out.append("                </tbody>")
        out.append("              </table>")
        out.append("            </div>")

    out.append('            <h4 class="sr-h">%s</h4>' % ("확인 절차 (비실행)" if item.get("patterns") else "대표 명령어"))
    if item.get("patterns"):
        out.append('            <p class="sr-sub">아래 명령은 승인된 점검에서 이미 저장된 결과 JSON·로그를 읽기만 합니다. 대상을 향해 요청을 보내지 않습니다.</p>')
    for n, cmd in enumerate(item["commands"], start=1):
        pre_id = "%s-cmd-%d" % (item["id"], n)
        out.append('            <div class="sr-cmd">')
        out.append('              <div class="sr-cmd-head">')
        out.append('                <span class="sr-cmd-label">%s</span>' % esc(cmd["label"]))
        out.append("                " + impact_pill(cmd["impact"]))
        out.append('                <button type="button" class="sr-cmd-copy" data-copy-cmd="%s" data-label="복사">복사</button>'
                   % esc_attr(pre_id))
        out.append("              </div>")
        out.append('              <pre id="%s">%s</pre>' % (esc_attr(pre_id), esc(cmd["cmd"])))
        out.append("            </div>")
        if cmd.get("note"):
            out.append('            <p class="sr-cmd-note">%s</p>' % rich(cmd["note"]))

    if item.get("options"):
        out.append('            <h4 class="sr-h">옵션별 영향 해부</h4>')
        out.append('            <div class="sr-table-wrap">')
        out.append('              <table class="sr-table">')
        out.append('                <thead><tr><th scope="col">옵션</th><th scope="col">의미</th><th scope="col">부하·네트워크 / 파일 쓰기 / 민감정보 영향</th></tr></thead>')
        out.append("                <tbody>")
        for opt in item["options"]:
            out.append('                  <tr><td><code class="sr-code">%s</code></td><td>%s</td><td>%s</td></tr>'
                       % (esc(opt["flag"]), rich(opt["meaning"]), rich(opt["effect"])))
        out.append("                </tbody>")
        out.append("              </table>")
        out.append("            </div>")

    out.append('            <h4 class="sr-h">%s</h4>' % ("판정 기준 · 오탐 · 조치" if item.get("patterns") else "결과 판독"))
    out.append('            <div class="sr-read">')
    for key, label, cls in READING_KEYS:
        bullets = item["reading"].get(key) or []
        out.append('              <section class="sr-read-block %s">' % cls)
        out.append('                <h5>%s</h5>' % esc(label))
        out.append("                <ul>")
        for bullet in bullets:
            out.append("                  <li>%s</li>" % rich(bullet))
        out.append("                </ul>")
        out.append("              </section>")
    out.append("            </div>")

    if item.get("sample"):
        out.append('            <h4 class="sr-h">샘플 증적 (마스킹)</h4>')
        out.append('            <figure class="sr-sample">')
        out.append('              <figcaption>%s</figcaption>' % esc(item["sample"]["title"]))
        out.append('              <pre>%s</pre>' % esc(item["sample"]["text"]))
        out.append("            </figure>")
        out.append('            <p class="sr-sample-cap">%s</p>' % rich(item["sample"]["caption"]))

    if item.get("mock"):
        mock = item["mock"]
        out.append('            <h4 class="sr-h">모의 응답 대조</h4>')
        out.append('            <p class="sr-sub">%s</p>' % esc(mock["title"]))
        out.append('            <div class="sr-mock">')
        out.append('              <figure class="sr-sample sr-mock-safe">')
        out.append('                <figcaption>%s</figcaption>' % esc(mock["safe_label"]))
        out.append('                <pre>%s</pre>' % esc(mock["safe_text"]))
        out.append("              </figure>")
        out.append('              <figure class="sr-sample sr-mock-vuln">')
        out.append('                <figcaption>%s</figcaption>' % esc(mock["vuln_label"]))
        out.append('                <pre>%s</pre>' % esc(mock["vuln_text"]))
        out.append("              </figure>")
        out.append("            </div>")
        out.append('            <p class="sr-sample-cap">%s</p>' % rich(mock["caption"]))

    if item.get("block_log"):
        log = item["block_log"]
        out.append('            <h4 class="sr-h">차단 로그 예시</h4>')
        out.append('            <figure class="sr-sample sr-blocklog">')
        out.append('              <figcaption>%s</figcaption>' % esc(log["title"]))
        out.append('              <pre>%s</pre>' % esc(log["text"]))
        out.append("            </figure>")
        out.append('            <p class="sr-sample-cap">%s</p>' % rich(log["caption"]))

    out.append('            <div class="sr-foot">')
    out.append('              <div><h5>공식 문서</h5><ul>')
    for doc in item["docs"]:
        out.append('                <li><a class="sr-doc-link" href="%s" target="_blank" rel="noopener noreferrer">%s</a></li>'
                   % (esc_attr(doc["url"]), esc(doc["label"])))
    out.append("              </ul></div>")
    out.append('              <div><h5>이어 보기</h5><ul>')
    for cheat in item.get("cheats") or []:
        out.append('                <li><a href="tools.html#%s">치트시트 · %s</a></li>'
                   % (esc_attr(cheat["anchor"]), esc(cheat["title"])))
    for rel_id in item.get("related") or []:
        rel = next((x for x in data["items"] if x["id"] == rel_id), None)
        if rel:
            out.append('                <li><a href="#%s"><span class="sr-link-kind">항목</span>%s</a></li>'
                       % (esc_attr(rel_id), esc(rel["title"])))
    out.append('                <li><a href="tools.html"><span class="sr-link-kind">유틸</span>실무 유틸·치트시트 전체</a></li>')
    out.append("              </ul></div>")
    out.append("            </div>")

    out.append("          </article>")
    return "\n".join(out)


if __name__ == "__main__":
    build()

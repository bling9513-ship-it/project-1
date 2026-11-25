#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""국내·해외 증시 이슈 요약(market.html).

무엇을 하나
  · `market_data.json`(market_crawler.py 산출물)을 화면에 심는다. 브라우저는 그 JSON 만 읽는다.
  · 위에서부터
      1) 시장 장 상태 — 국내(KRX)·해외(NYSE·Nasdaq)의 개장·마감·휴장·조기 마감과 현지 시각,
         공식 시세 확인 링크(KRX 정보데이터시스템·네이버 증권·Nasdaq 등)
      2) 국내 / 해외 탭 — 오늘의 이슈 3줄 + 다음 거래일 점검 3줄
      3) 왜 움직였을까 — 기사별 한 줄 원인 카드 + 근거 신뢰도 + 섹터 + 원문 링크
      4) 돈 몰린 테마·섹터 — 섹터별 기사 묶음(누르면 위 카드가 걸러진다)
      5) 이번 주 시장 일정 — FOMC·CPI·고용·금통위·주요 실적을 KST D-Day 로
         (BLS 보관 사본에서 읽은 항목은 보관일과 bls.gov 원문 링크를 카드에 함께 적는다)
  · D-Day 는 화면에서 오늘 날짜(KST)로 다시 계산한다. 시간이 없는 일정은 '시간 미정'으로 적는다.

지키는 것
  · 지수·종목·환율 수치를 게시하지 않는다(Yahoo Finance 등 시세 재배포 금지). 원문 확인 링크만 둔다.
  · 기사는 제목·매체·시각·섹터·원문 링크만. RSS 설명·요약문은 싣지 않는다.
  · 연합뉴스·매일경제처럼 자동 수집·AI 활용을 제한하는 매체는 넣지 않는다(검증에서 막는다).
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 3열 카드 / 모바일(390px) 1열 — 가로 넘침 없음
  · 원인이 확인되지 않은 움직임은 '뚜렷한 원인 미확인'으로 그대로 보여 준다(추측으로 채우지 않음)
"""
import json
import os
from datetime import datetime

from html_guard import harden_html, safe_json_for_script, safe_url
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "market_data.json")
OUT_HTML = os.path.join(BASE_DIR, "market.html")

MIN_ISSUES = 6
CONFIDENCE_VALUES = ("원문 근거", "추정", "미확인")
SESSION_STATES = ("open", "closed", "preopen", "holiday", "early_closed", "unknown")
BLOCKED_SOURCES = ("연합뉴스", "매일경제", "Yahoo Finance")
BANNED_FIELDS = ("summary", "summary_orig")


def load_data(path=None):
    with open(path or DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)
    issues = data.get("issues") or []
    if len(issues) < MIN_ISSUES:
        raise SystemExit("기사가 %d건입니다(%d건 이상 필요)." % (len(issues), MIN_ISSUES))
    for issue in issues:
        if not safe_url(issue.get("url"), "").startswith("http"):
            raise SystemExit("기사 링크가 올바르지 않습니다: %r" % issue.get("id"))
        if issue.get("confidence") not in CONFIDENCE_VALUES:
            raise SystemExit("신뢰도 값이 올바르지 않습니다: %r" % issue.get("confidence"))
        if issue.get("source") in BLOCKED_SOURCES:
            raise SystemExit("재배포 제한 매체가 남아 있습니다: %r" % issue.get("source"))
        for field in BANNED_FIELDS:
            if str(issue.get(field) or "").strip():
                raise SystemExit("기사 %r 에 RSS 설명·요약이 남아 있습니다(%s)." % (issue.get("id"), field))
    if not data.get("calendar"):
        raise SystemExit("시장 일정이 없습니다.")
    sessions = data.get("sessions") or {}
    for market in ("domestic", "global"):
        if not sessions.get(market):
            raise SystemExit("장 상태가 없습니다: %s" % market)
        if sessions[market].get("state") not in SESSION_STATES:
            raise SystemExit("장 상태 값이 올바르지 않습니다: %r" % sessions[market].get("state"))
    return data


def build_payload(data):
    """화면이 쓰는 최소 필드만 남긴다(제목·매체·링크·장 상태)."""
    issues = []
    for issue in data["issues"]:
        issues.append({
            "id": issue["id"],
            "market": issue["market"],
            "title": issue["title"],
            "titleOriginal": issue.get("titleOriginal") or "",
            "why": issue["why"],
            "confidence": issue["confidence"],
            "sectors": issue.get("sectors") or ["매크로"],
            "source": issue["source"],
            "official": bool(issue.get("official")),
            "url": issue["url"],
            "publishedKst": issue.get("publishedKst") or "",
            "analyzedBy": issue.get("analyzedBy") or "fallback",
        })
    calendar = []
    for row in data["calendar"]:
        entry = {
            "id": row["id"],
            "date": row["date"],
            "timeKst": row.get("timeKst") or "",
            "title": row["title"],
            "category": row["category"],
            "region": row["region"],
            "note": row.get("note") or "",
            "source": row["source"],
            "sourceUrl": safe_url(row.get("sourceUrl"), ""),
            "localDate": row.get("localDate") or "",
        }
        if row.get("snapshotDate"):
            entry["snapshotDate"] = row["snapshotDate"]
        if row.get("archiveUrl"):
            entry["archiveUrl"] = safe_url(row["archiveUrl"], "")
        calendar.append(entry)
    return {
        "meta": data["meta"],
        "sessions": data["sessions"],
        "marketLinks": data.get("marketLinks") or {},
        "briefing": data["briefing"],
        "issues": issues,
        "sectors": data["sectors"],
        "calendar": calendar,
    }


def build(out_path=None, data=None):
    data = data or load_data()
    payload = build_payload(data)
    meta = payload["meta"]

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__JS__", JS)
            .replace("__COLLECTED__", meta["collectedAt"])
            .replace("__NEWS_COUNT__", str(len(payload["issues"])))
            .replace("__CAL_COUNT__", str(len(payload["calendar"])))
            .replace("__DATA_JSON__", safe_json_for_script(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")))))

    with open(out_path or OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "market")))

    print("-> 'market.html' 생성 완료 (기사 %d건 · 일정 %d건 · AI %s)"
          % (len(payload["issues"]), len(payload["calendar"]),
             "사용" if meta.get("ai", {}).get("used") else "폴백"))
    return {"issues": len(payload["issues"]),
            "calendar": len(payload["calendar"]),
            "sessions": "국내 %s · 해외 %s" % (payload["sessions"]["domestic"]["stateLabel"],
                                            payload["sessions"]["global"]["stateLabel"]),
            "ai": bool(meta.get("ai", {}).get("used")),
            "collectedAt": meta["collectedAt"]}


CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --bg-page: #f8fafc;  --bg-surface: #ffffff;  --bg-subtle: #f1f5f9;  --bg-muted: #e2e8f0;
      --border-subtle: #f1f5f9;  --border-default: #e2e8f0;  --border-strong: #cbd5e1;
      --text-primary: #0f172a;  --text-secondary: #475569;  --text-muted: #94a3b8;
      --accent-primary: #2563eb;  --accent-subtle: #eff6ff;
      --warn-bg: #fffbeb;  --warn-text: #b45309;  --warn-border: #fde68a;
      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --warn-bg: rgba(245, 158, 11, 0.14);  --warn-text: #fcd34d;  --warn-border: rgba(245, 158, 11, 0.34);
      --ok-bg: rgba(16, 185, 129, 0.14);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.34);
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body { font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease; }
    .mk-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .mk-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 100px; }
    .mk-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .mk-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 720px; word-break: keep-all; }
    .mk-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .mk-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px;
      font-size: 11.5px; color: var(--text-muted); }
    .mk-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }
    .mk-stamp { display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 700;
      color: var(--text-primary); background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 999px; padding: 3px 10px 3px 8px; font-variant-numeric: tabular-nums; }
    .mk-stamp::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: #10b981; }

    /* 시장 장 상태 */
    .mk-status { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 16px; }
    .mk-market { display: flex; flex-direction: column; gap: 10px; padding: 15px 16px; min-width: 0;
      background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      box-shadow: var(--card-shadow); }
    .mk-market-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .mk-market-head h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; }
    .mk-market-head .mk-badge { flex: 0 0 auto; }
    .mk-market-rows { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px 12px; }
    .mk-market-row { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
    .mk-market-row span { font-size: 10px; font-weight: 700; color: var(--text-muted); }
    .mk-market-row b { font-size: 12.5px; font-weight: 800; letter-spacing: -0.02em; color: var(--text-primary);
      font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .mk-market-note { font-size: 10.5px; color: var(--text-muted); word-break: keep-all; }
    .mk-links { display: flex; flex-wrap: wrap; gap: 5px; }
    .mk-link-chip { display: inline-flex; align-items: center; gap: 3px; font-size: 10.5px; font-weight: 700;
      color: var(--text-secondary); text-decoration: none; border: 1px solid var(--border-default);
      border-radius: 999px; padding: 3px 9px; background: var(--bg-page); transition: border-color .15s ease,
      color .15s ease, background-color .15s ease; }
    .mk-link-chip:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .mk-link-chip:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .mk-link-chip svg { width: 9px; height: 9px; }

    /* 탭 */
    .mk-tabs { display: flex; align-items: center; gap: 6px; margin-top: 18px; }
    .mk-tab { flex: 0 0 auto; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 999px; padding: 8px 16px; font-family: inherit;
      font-size: 13px; font-weight: 700; cursor: pointer; transition: background-color .15s ease, color .15s ease,
      border-color .15s ease, transform .15s ease; }
    .mk-tab:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .mk-tab:active { transform: scale(0.98); }
    .mk-tab:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .mk-tab[aria-selected="true"] { background: var(--text-primary); color: var(--bg-surface);
      border-color: var(--text-primary); }
    .mk-tab-note { margin-left: auto; font-size: 11px; color: var(--text-muted); }

    /* 브리핑 */
    .mk-panel { margin-top: 12px; }
    .mk-session { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 11.5px;
      color: var(--text-secondary); }
    .mk-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 10.5px; font-weight: 800;
      border-radius: 999px; padding: 2px 8px; border: 1px solid var(--border-default);
      background: var(--bg-subtle); color: var(--text-secondary); }
    .mk-badge.is-live { color: var(--ok-text); background: var(--ok-bg); border-color: var(--ok-border); }
    .mk-badge.is-warn { color: var(--warn-text); background: var(--warn-bg); border-color: var(--warn-border); }
    .mk-brief { display: grid; grid-template-columns: 1.1fr 1fr; gap: 10px; margin-top: 10px; }
    .mk-brief-card { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 14px 16px; box-shadow: var(--card-shadow); min-width: 0; }
    .mk-brief-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
    .mk-brief-head h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; }
    .mk-brief-head span { font-size: 10.5px; font-weight: 700; color: var(--text-muted); }
    .mk-brief-list { margin-top: 9px; display: grid; gap: 7px; }
    .mk-brief-line { display: grid; grid-template-columns: 16px minmax(0, 1fr); gap: 7px;
      font-size: 12.5px; line-height: 1.55; color: var(--text-primary); word-break: keep-all; }
    .mk-brief-num { font-size: 10.5px; font-weight: 800; color: var(--text-muted); padding-top: 2px; }

    /* 카드 목록 */
    .mk-section { margin-top: 20px; }
    .mk-section-head { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; }
    .mk-section-head h2 { font-size: 15.5px; font-weight: 800; letter-spacing: -0.03em; }
    .mk-section-head span { font-size: 11.5px; font-weight: 700; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .mk-section-head p { margin-top: 2px; font-size: 11px; color: var(--text-muted); }

    .mk-chips { display: flex; gap: 6px; overflow-x: auto; margin-top: 10px; padding-bottom: 2px; scrollbar-width: none; }
    .mk-chips::-webkit-scrollbar { display: none; }
    .mk-chip { flex: 0 0 auto; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 999px; padding: 5px 11px; font-family: inherit;
      font-size: 11.5px; font-weight: 700; cursor: pointer; white-space: nowrap;
      transition: border-color .15s ease, background-color .15s ease, color .15s ease, transform .15s ease; }
    .mk-chip span { font-size: 10px; color: var(--text-muted); margin-left: 3px; }
    .mk-chip:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .mk-chip:active { transform: scale(0.97); }
    .mk-chip:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .mk-chip[aria-pressed="true"] { background: var(--text-primary); border-color: var(--text-primary);
      color: var(--bg-surface); }
    .mk-chip[aria-pressed="true"] span { color: var(--bg-surface); opacity: .7; }

    .mk-issues { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 10px; }
    .mk-issue { display: flex; flex-direction: column; gap: 7px; background: var(--bg-surface);
      border: 1px solid var(--border-default); border-radius: 15px; padding: 13px 14px;
      box-shadow: var(--card-shadow); min-width: 0; transition: border-color .15s ease; }
    .mk-issue:hover { border-color: var(--border-strong); }
    .mk-issue-top { display: flex; flex-wrap: wrap; align-items: center; gap: 5px; }
    .mk-src { font-size: 10px; font-weight: 800; color: var(--text-secondary); border: 1px solid var(--border-default);
      border-radius: 999px; padding: 1px 7px; }
    .mk-src.is-official { color: var(--accent-primary); border-color: var(--accent-subtle); background: var(--accent-subtle); }
    .mk-conf { font-size: 10px; font-weight: 800; border-radius: 999px; padding: 1px 7px; }
    .mk-conf.is-strong { color: var(--ok-text); background: var(--ok-bg); border: 1px solid var(--ok-border); }
    .mk-conf.is-guess { color: var(--warn-text); background: var(--warn-bg); border: 1px solid var(--warn-border); }
    .mk-conf.is-none { color: var(--text-muted); background: var(--bg-subtle); border: 1px solid var(--border-default); }
    .mk-issue-time { margin-left: auto; font-size: 10px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .mk-issue h3 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.42; word-break: keep-all; }
    .mk-why { font-size: 12px; line-height: 1.55; color: var(--text-secondary); word-break: keep-all; }
    .mk-why b { font-weight: 800; color: var(--text-primary); }
    .mk-issue-foot { display: flex; align-items: center; gap: 6px; margin-top: auto; padding-top: 3px; }
    .mk-sector-tag { font-size: 10px; font-weight: 700; color: var(--accent-primary); background: var(--accent-subtle);
      border-radius: 6px; padding: 1px 6px; }
    .mk-link { display: inline-flex; align-items: center; gap: 3px; margin-left: auto; font-size: 10.5px;
      font-weight: 800; color: var(--text-secondary); text-decoration: none; border: 1px solid var(--border-default);
      border-radius: 8px; padding: 4px 8px; transition: background-color .15s ease, color .15s ease; }
    .mk-link:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .mk-link:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .mk-link svg { width: 10px; height: 10px; }
    .mk-empty { margin-top: 10px; border: 1px dashed var(--border-strong); border-radius: 13px; padding: 18px;
      background: var(--bg-surface); font-size: 12px; color: var(--text-secondary); text-align: center; line-height: 1.6; }
    .mk-empty b { color: var(--text-primary); }

    /* 섹터 */
    .mk-sectors { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-top: 10px; }
    .mk-sector { display: flex; flex-direction: column; gap: 6px; background: var(--bg-surface);
      border: 1px solid var(--border-default); border-radius: 15px; padding: 13px 14px; box-shadow: var(--card-shadow);
      min-width: 0; }
    .mk-sector.is-empty { background: var(--bg-subtle); border-style: dashed; box-shadow: none; }
    .mk-sector-head { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
    .mk-sector-head h3 { font-size: 12.5px; font-weight: 800; letter-spacing: -0.02em; }
    .mk-sector-count { font-size: 10.5px; font-weight: 800; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .mk-sector ul { list-style: none; display: grid; gap: 5px; }
    .mk-sector li { min-width: 0; }
    .mk-sector a { display: block; font-size: 11.5px; line-height: 1.45; color: var(--text-secondary);
      text-decoration: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .mk-sector a:hover { color: var(--accent-primary); text-decoration: underline; }
    .mk-sector-none { font-size: 11px; color: var(--text-muted); }

    /* 일정 */
    .mk-cal { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 10px; }
    .mk-cal-row { display: grid; grid-template-columns: 48px minmax(0, 1fr) auto; align-items: center; gap: 10px;
      background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 13px;
      padding: 11px 13px; box-shadow: var(--card-shadow); min-width: 0; }
    .mk-cal-row.is-today { border-color: var(--accent-primary); background: var(--accent-subtle); }
    .mk-dday { display: inline-flex; align-items: center; justify-content: center; height: 26px; border-radius: 8px;
      font-size: 11px; font-weight: 800; font-variant-numeric: tabular-nums; color: var(--text-secondary);
      background: var(--bg-subtle); border: 1px solid var(--border-default); }
    .mk-dday.is-today { background: var(--accent-primary); border-color: var(--accent-primary); color: #ffffff; }
    .mk-cal-body { min-width: 0; }
    .mk-cal-title { font-size: 12.5px; font-weight: 800; letter-spacing: -0.02em; white-space: nowrap;
      overflow: hidden; text-overflow: ellipsis; }
    .mk-cal-sub { font-size: 10.5px; color: var(--text-muted); white-space: nowrap; overflow: hidden;
      text-overflow: ellipsis; }
    .mk-cal-src { display: flex; flex-wrap: wrap; align-items: center; gap: 5px; margin-top: 3px;
      font-size: 10px; color: var(--text-muted); }
    .mk-cal-src a { color: var(--text-secondary); font-weight: 700; text-decoration: none;
      border-bottom: 1px solid var(--border-strong); }
    .mk-cal-src a:hover { color: var(--accent-primary); }
    .mk-cal-time { font-size: 11px; font-weight: 700; color: var(--text-secondary); font-variant-numeric: tabular-nums;
      text-align: right; white-space: nowrap; }
    .mk-cal-time.is-tbd { color: var(--text-muted); font-weight: 600; }

    /* 안내 */
    .mk-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .mk-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; }
    .mk-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .mk-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .mk-notes li b { color: var(--text-primary); }
    .mk-src-list { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
    .mk-src-item { display: inline-flex; align-items: center; gap: 5px; font-size: 10.5px; font-weight: 700;
      color: var(--text-secondary); border: 1px solid var(--border-default); border-radius: 999px; padding: 3px 9px;
      background: var(--bg-page); }
    .mk-src-item.is-fail { color: var(--warn-text); border-color: var(--warn-border); background: var(--warn-bg); }
    .mk-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 1080px) {
      .mk-issues { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .mk-sectors { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (max-width: 900px) {
      .mk-wrap { padding: 14px 13px 110px; }
      .mk-hero h1 { font-size: 21px; }
      .mk-hero p { font-size: 12px; }
      .mk-status { grid-template-columns: minmax(0, 1fr); gap: 8px; }
      .mk-market { padding: 13px 14px; }
      .mk-tabs { margin-top: 14px; }
      .mk-tab { padding: 7px 14px; font-size: 12.5px; }
      .mk-tab-note { display: none; }
      .mk-brief { grid-template-columns: minmax(0, 1fr); gap: 8px; }
      .mk-brief-card { padding: 13px 14px; }
      .mk-section { margin-top: 17px; }
      .mk-section-head h2 { font-size: 14.5px; }
      .mk-issues { grid-template-columns: minmax(0, 1fr); gap: 8px; }
      .mk-sectors { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
      .mk-cal { grid-template-columns: minmax(0, 1fr); gap: 7px; }
      .mk-cal-row { grid-template-columns: 44px minmax(0, 1fr) auto; padding: 10px 12px; gap: 8px; }
      .mk-cal-sub, .mk-cal-src { white-space: normal; }
    }
    @media (max-width: 380px) {
      .mk-sector { padding: 11px 12px; }
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
  <title>Infosec Archive · 증시 이슈 요약</title>
  <meta name="description" content="국내(KRX)·해외(NYSE·Nasdaq) 장 상태와 오늘의 증시 이슈를 3줄 브리핑, 한 줄 원인 카드, 섹터별 묶음, FOMC·CPI·고용·금통위·실적 일정(D-Day)으로 정리합니다. 시세 수치는 게시하지 않고 공식·원문 확인 링크만 안내합니다.">
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
        <div class="update-meta"><span class="live-dot"></span><span>기사 __NEWS_COUNT__건 · 일정 __CAL_COUNT__건</span></div>
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

  <main class="mk-wrap">
    <section class="mk-hero">
      <span class="mk-pill">증시 · 이슈 정리</span>
      <h1>오늘 시장, 왜 움직였나</h1>
      <p>장이 열렸는지부터 봅니다. 국내(KRX)·해외(NYSE·Nasdaq) 장 상태를 거래소 캘린더로 계산하고, 오늘의 이슈를 한 줄 원인과 원문 링크로 정리합니다. 지수·종목 수치는 싣지 않고 공식·원문에서 확인하도록 링크만 둡니다.</p>
      <div class="mk-meta">
        <span class="mk-stamp">수집 __COLLECTED__</span>
        <span class="mk-dot"></span>
        <span>기사 __NEWS_COUNT__건 · 일정 __CAL_COUNT__건</span>
        <span class="mk-dot"></span>
        <span>시세 수치 미게시 · 원문 링크 안내</span>
      </div>
    </section>

    <section class="mk-status" id="mkStatus" aria-label="시장 장 상태"></section>

    <div class="mk-tabs" role="tablist" aria-label="시장 선택">
      <button type="button" class="mk-tab" id="mkTabDomestic" role="tab" aria-selected="true"
              aria-controls="mkPanelDomestic" data-market="domestic">국내</button>
      <button type="button" class="mk-tab" id="mkTabGlobal" role="tab" aria-selected="false"
              aria-controls="mkPanelGlobal" data-market="global">해외</button>
      <span class="mk-tab-note" id="mkTabNote"></span>
    </div>

    <section class="mk-panel" id="mkPanelDomestic" role="tabpanel" aria-labelledby="mkTabDomestic">
      <div class="mk-session" id="mkSessionDomestic"></div>
      <div class="mk-brief">
        <article class="mk-brief-card">
          <div class="mk-brief-head"><h2>오늘의 이슈 3줄</h2><span id="mkIssueStampDomestic"></span></div>
          <div class="mk-brief-list" id="mkTodayDomestic"></div>
        </article>
        <article class="mk-brief-card">
          <div class="mk-brief-head"><h2>다음 거래일 점검</h2><span>장 상태 · 일정</span></div>
          <div class="mk-brief-list" id="mkNextDomestic"></div>
        </article>
      </div>
    </section>

    <section class="mk-panel" id="mkPanelGlobal" role="tabpanel" aria-labelledby="mkTabGlobal" hidden>
      <div class="mk-session" id="mkSessionGlobal"></div>
      <div class="mk-brief">
        <article class="mk-brief-card">
          <div class="mk-brief-head"><h2>오늘의 이슈 3줄</h2><span id="mkIssueStampGlobal"></span></div>
          <div class="mk-brief-list" id="mkTodayGlobal"></div>
        </article>
        <article class="mk-brief-card">
          <div class="mk-brief-head"><h2>다음 거래일 점검</h2><span>장 상태 · 일정</span></div>
          <div class="mk-brief-list" id="mkNextGlobal"></div>
        </article>
      </div>
    </section>

    <section class="mk-section" aria-labelledby="mkIssueTitle">
      <div class="mk-section-head">
        <div>
          <h2 id="mkIssueTitle">왜 움직였을까</h2>
          <p>기사 한 줄 원인 · 근거가 약하면 '뚜렷한 원인 미확인'으로 표시</p>
        </div>
        <span id="mkIssueCount"></span>
      </div>
      <div class="mk-chips" id="mkSectorChips" role="group" aria-label="섹터 필터"></div>
      <div class="mk-issues" id="mkIssues"></div>
      <p class="mk-empty" id="mkIssueEmpty" hidden></p>
    </section>

    <section class="mk-section" aria-labelledby="mkSectorTitle">
      <div class="mk-section-head">
        <div>
          <h2 id="mkSectorTitle">돈 몰린 테마·섹터</h2>
          <p>섹터를 누르면 위 카드가 그 섹터만 남깁니다</p>
        </div>
        <span id="mkSectorCount"></span>
      </div>
      <div class="mk-sectors" id="mkSectors"></div>
    </section>

    <section class="mk-section" aria-labelledby="mkCalTitle">
      <div class="mk-section-head">
        <div>
          <h2 id="mkCalTitle">이번 주 시장 일정</h2>
          <p>한국시간(KST) D-Day · FOMC·CPI·고용·금통위·주요 실적</p>
        </div>
        <span id="mkCalCount"></span>
      </div>
      <div class="mk-cal" id="mkCalendar"></div>
    </section>

    <section class="mk-notes">
      <h2>알아 두실 점</h2>
      <ul id="mkNotes"></ul>
      <div class="mk-src-list" id="mkSources" aria-label="수집 출처"></div>
      <p class="mk-foot">각 기사·지표의 저작권과 해석은 원문 매체·기관에 있습니다 · 시세 수치는 게시하지 않습니다.</p>
    </section>
  </main>

  <script type="application/json" id="mkData">__DATA_JSON__</script>
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
  try { DATA = JSON.parse(document.getElementById('mkData').textContent); } catch (e) { return; }
  var EXTERNAL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-8 8"></path><path d="M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"></path></svg>';

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }
  function pad(value) { return value < 10 ? '0' + value : String(value); }

  // ---------- KST 오늘 ----------
  function kstToday() {
    var now = new Date();
    var shifted = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + 9 * 3600000);
    return new Date(shifted.getFullYear(), shifted.getMonth(), shifted.getDate());
  }
  function parseDate(text) {
    var parts = String(text || '').split('-');
    if (parts.length !== 3) return null;
    return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
  }
  function dayDiff(a, b) { return Math.round((a.getTime() - b.getTime()) / 86400000); }

  // ---------- 시장 장 상태 ----------
  function stateClass(session) {
    var cls = 'mk-badge';
    if (session.state === 'open' || session.state === 'closed') cls += ' is-live';
    if (session.state === 'early_closed' || session.state === 'holiday' || session.state === 'unknown') cls += ' is-warn';
    return cls;
  }
  function marketRow(label, value) {
    var row = el('div', 'mk-market-row');
    row.appendChild(el('span', '', label));
    row.appendChild(el('b', '', value || '-'));
    return row;
  }
  var statusGrid = document.getElementById('mkStatus');
  ['domestic', 'global'].forEach(function (market) {
    var session = DATA.sessions[market];
    if (!session) return;
    var card = el('article', 'mk-market');
    var head = el('div', 'mk-market-head');
    var title = el('h2', '', (market === 'domestic' ? '국내 · ' : '해외 · ') + session.marketName);
    head.appendChild(title);
    head.appendChild(el('span', stateClass(session), session.stateLabel));
    card.appendChild(head);
    var rows = el('div', 'mk-market-rows');
    rows.appendChild(marketRow('현지 시각', session.localNow + ' ' + session.tzLabel));
    rows.appendChild(marketRow('거래 시간', session.sessionText));
    rows.appendChild(marketRow('최근 거래일', session.lastTradingLabel));
    rows.appendChild(marketRow('다음 거래일', session.nextTradingLabel));
    card.appendChild(rows);
    if (session.reason) card.appendChild(el('p', 'mk-market-note', '휴장·조기 마감 사유: ' + session.reason));
    if (session.outsideCalendar) {
      card.appendChild(el('p', 'mk-market-note', '거래소 캘린더 반영 범위 밖입니다. ' + session.calendarName + '에서 확인하세요.'));
    }
    var links = el('div', 'mk-links');
    (DATA.marketLinks[market] || []).forEach(function (link) {
      var a = el('a', 'mk-link-chip');
      a.href = link.url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.innerHTML = EXTERNAL;
      a.appendChild(document.createTextNode(' ' + link.label));
      links.appendChild(a);
    });
    card.appendChild(links);
    statusGrid.appendChild(card);
  });

  // ---------- 세션 줄 ----------
  function sessionLine(target, session) {
    target.innerHTML = '';
    if (!session) return;
    target.appendChild(el('span', stateClass(session), session.stateLabel));
    target.appendChild(el('span', '', '현지 ' + session.localNow + ' ' + session.tzLabel + ' · 거래 시간 ' + session.sessionText));
    target.appendChild(el('span', 'mk-dot'));
    target.appendChild(el('span', '', '최근 거래일 ' + (session.lastTradingLabel || '-')));
    target.appendChild(el('span', 'mk-dot'));
    target.appendChild(el('span', '', '갱신 ' + DATA.meta.collectedAt.replace(' KST', '') + ' KST'));
  }
  sessionLine(document.getElementById('mkSessionDomestic'), DATA.sessions.domestic);
  sessionLine(document.getElementById('mkSessionGlobal'), DATA.sessions.global);

  // ---------- 브리핑 ----------
  function fillLines(listId, lines) {
    var list = document.getElementById(listId);
    if (!list) return 0;
    list.innerHTML = '';
    (lines || []).forEach(function (line, index) {
      var row = el('div', 'mk-brief-line');
      row.appendChild(el('span', 'mk-brief-num', String(index + 1)));
      row.appendChild(el('span', '', line));
      list.appendChild(row);
    });
    if (!(lines || []).length) {
      var empty = el('div', 'mk-brief-line');
      empty.appendChild(el('span', 'mk-brief-num', '-'));
      empty.appendChild(el('span', '', '정리된 내용이 없습니다'));
      list.appendChild(empty);
    }
    return (lines || []).length;
  }
  ['domestic', 'global'].forEach(function (market) {
    var block = DATA.briefing[market] || {};
    var cap = market === 'domestic' ? 'Domestic' : 'Global';
    fillLines('mkToday' + cap, block.issues);
    fillLines('mkNext' + cap, block.next);
    var stamp = document.getElementById('mkIssueStamp' + cap);
    if (stamp) stamp.textContent = '제목 기준';
  });

  // ---------- 탭 ----------
  var state = { market: 'domestic', sector: 'all' };
  var tabs = [document.getElementById('mkTabDomestic'), document.getElementById('mkTabGlobal')];
  var panels = { domestic: document.getElementById('mkPanelDomestic'), global: document.getElementById('mkPanelGlobal') };

  function setMarket(market) {
    state.market = market;
    tabs.forEach(function (tab) {
      if (!tab) return;
      var on = tab.dataset.market === market;
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      if (panels[tab.dataset.market]) panels[tab.dataset.market].hidden = !on;
    });
  }
  tabs.forEach(function (tab) {
    if (!tab) return;
    tab.addEventListener('click', function () { setMarket(tab.dataset.market); });
  });

  var note = document.getElementById('mkTabNote');
  if (note) {
    note.textContent = '국내 ' + DATA.issues.filter(function (row) { return row.market === 'domestic'; }).length
      + '건 · 해외 ' + DATA.issues.filter(function (row) { return row.market === 'global'; }).length + '건';
  }

  // ---------- 섹터 필터 ----------
  var chips = document.getElementById('mkSectorChips');
  function sectorOptions() {
    var counts = {};
    DATA.issues.forEach(function (row) {
      (row.sectors || []).forEach(function (name) { counts[name] = (counts[name] || 0) + 1; });
    });
    var list = [{ name: 'all', count: DATA.issues.length }];
    DATA.sectors.forEach(function (row) {
      list.push({ name: row.name, count: counts[row.name] || 0 });
    });
    return list;
  }
  sectorOptions().forEach(function (option) {
    var chip = el('button', 'mk-chip', option.name === 'all' ? '전체' : option.name);
    chip.type = 'button';
    chip.dataset.sector = option.name;
    chip.setAttribute('aria-pressed', option.name === state.sector ? 'true' : 'false');
    if (option.name !== 'all') chip.appendChild(el('span', '', String(option.count)));
    chip.addEventListener('click', function () { setSector(option.name); });
    chips.appendChild(chip);
  });

  function setSector(name) {
    state.sector = name;
    Array.prototype.forEach.call(chips.querySelectorAll('.mk-chip'), function (chip) {
      chip.setAttribute('aria-pressed', chip.dataset.sector === name ? 'true' : 'false');
    });
    renderIssues();
  }

  // ---------- 원인 카드 ----------
  var issueGrid = document.getElementById('mkIssues');
  var issueEmpty = document.getElementById('mkIssueEmpty');
  var issueCount = document.getElementById('mkIssueCount');

  function confidenceText(value) {
    if (value === '원문 근거') return { cls: 'mk-conf is-strong', text: '원문 근거' };
    if (value === '추정') return { cls: 'mk-conf is-guess', text: '정황 추정' };
    return { cls: 'mk-conf is-none', text: '원인 미확인' };
  }

  function issueCard(row) {
    var card = el('article', 'mk-issue');
    card.dataset.market = row.market;
    card.dataset.sectors = (row.sectors || []).join('|');

    var top = el('div', 'mk-issue-top');
    top.appendChild(el('span', 'mk-src' + (row.official ? ' is-official' : ''), row.source));
    var conf = confidenceText(row.confidence);
    top.appendChild(el('span', conf.cls, conf.text));
    top.appendChild(el('span', 'mk-issue-time', row.publishedKst || ''));
    card.appendChild(top);

    card.appendChild(el('h3', '', row.title));

    var why = el('p', 'mk-why');
    if (row.confidence === '미확인') {
      why.appendChild(el('b', '', '뚜렷한 원인 미확인'));
      why.appendChild(document.createTextNode(' — 제목에서 원인을 확인하지 못했습니다'));
    } else {
      why.textContent = row.why;
    }
    card.appendChild(why);

    var foot = el('div', 'mk-issue-foot');
    (row.sectors || []).forEach(function (name) { foot.appendChild(el('span', 'mk-sector-tag', name)); });
    var link = el('a', 'mk-link');
    link.href = row.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.innerHTML = EXTERNAL;
    link.appendChild(document.createTextNode(' 원문'));
    link.setAttribute('aria-label', row.source + ' 원문 열기');
    foot.appendChild(link);
    card.appendChild(foot);
    return card;
  }

  function renderIssues() {
    var rows = DATA.issues.filter(function (row) {
      if (state.sector !== 'all' && (row.sectors || []).indexOf(state.sector) < 0) return false;
      return true;
    });
    issueGrid.innerHTML = '';
    rows.forEach(function (row) { issueGrid.appendChild(issueCard(row)); });
    issueCount.textContent = rows.length + '건';
    if (!rows.length) {
      issueEmpty.hidden = false;
      issueEmpty.innerHTML = '<b>이 조건의 기사가 없습니다.</b><br>다른 섹터를 골라 보세요.';
    } else {
      issueEmpty.hidden = true;
    }
  }

  // ---------- 섹터 판 ----------
  var sectorGrid = document.getElementById('mkSectors');
  var sectorCount = document.getElementById('mkSectorCount');
  (DATA.sectors || []).forEach(function (row) {
    var card = el('article', 'mk-sector' + (row.count ? '' : ' is-empty'));
    var head = el('div', 'mk-sector-head');
    var button = el('button', 'mk-chip', row.name);
    button.type = 'button';
    button.dataset.sector = row.name;
    button.addEventListener('click', function () {
      setSector(row.name);
      var target = document.getElementById('mkIssueTitle');
      if (target && target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    head.appendChild(button);
    head.appendChild(el('span', 'mk-sector-count', row.count + '건'));
    card.appendChild(head);
    if (row.count) {
      var list = el('ul');
      row.items.forEach(function (item) {
        var li = el('li');
        var link = el('a', '', item.title);
        link.href = item.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.title = item.source + ' · ' + item.title;
        li.appendChild(link);
        list.appendChild(li);
      });
      card.appendChild(list);
    } else {
      card.appendChild(el('p', 'mk-sector-none', '오늘 새 소재 없음'));
    }
    sectorGrid.appendChild(card);
  });
  var covered = (DATA.sectors || []).filter(function (row) { return row.count > 0; }).length;
  sectorCount.textContent = covered + ' / ' + (DATA.sectors || []).length + '섹터';

  // ---------- 일정(D-Day) ----------
  var calGrid = document.getElementById('mkCalendar');
  var calCount = document.getElementById('mkCalCount');
  var today = kstToday();
  function renderCalendar() {
    calGrid.innerHTML = '';
    DATA.calendar.forEach(function (row) {
      var date = parseDate(row.date);
      var diff = date ? dayDiff(date, kstToday()) : null;
      var wrap = el('article', 'mk-cal-row' + (diff === 0 ? ' is-today' : ''));
      var dday = el('span', 'mk-dday' + (diff === 0 ? ' is-today' : ''),
        diff === null ? '-' : (diff === 0 ? 'D-DAY' : 'D-' + diff));
      wrap.appendChild(dday);
      var body = el('div', 'mk-cal-body');
      body.appendChild(el('div', 'mk-cal-title', row.title));
      var sub = row.date.slice(5).replace('-', '/') + ' (' + row.region + ')';
      if (row.note) sub += ' · ' + row.note;
      body.appendChild(el('div', 'mk-cal-sub', sub));
      if (row.snapshotDate) {
        var src = el('div', 'mk-cal-src');
        src.appendChild(el('span', '', '보관 사본 ' + row.snapshotDate + ' 기준'));
        if (row.sourceUrl) {
          var official = el('a', '', 'bls.gov 원문');
          official.href = row.sourceUrl;
          official.target = '_blank';
          official.rel = 'noopener noreferrer';
          src.appendChild(official);
        }
        if (row.archiveUrl) {
          var archive = el('a', '', '보관 사본 열기');
          archive.href = row.archiveUrl;
          archive.target = '_blank';
          archive.rel = 'noopener noreferrer';
          src.appendChild(archive);
        }
        body.appendChild(src);
      }
      wrap.appendChild(body);
      wrap.appendChild(el('span', 'mk-cal-time' + (row.timeKst ? '' : ' is-tbd'), row.timeKst ? row.timeKst + ' KST' : '시간 미정'));
      calGrid.appendChild(wrap);
    });
    calCount.textContent = DATA.calendar.length + '건 · 기준 ' + today.getFullYear() + '.' + pad(today.getMonth() + 1) + '.' + pad(today.getDate());
  }
  renderCalendar();
  renderIssues();

  // ---------- 안내·출처 ----------
  var notes = document.getElementById('mkNotes');
  (DATA.meta.notes || []).forEach(function (line) {
    var li = document.createElement('li');
    li.textContent = line;
    notes.appendChild(li);
  });
  var sources = document.getElementById('mkSources');
  (DATA.meta.sources || []).forEach(function (row) {
    var item = el('span', 'mk-src-item' + (row.status === '실패' ? ' is-fail' : ''),
      row.name + ' · ' + row.status + ' ' + (row.count || 0) + '건');
    sources.appendChild(item);
  });

  // 테스트·확인용
  window.MARKET = {
    data: DATA,
    state: state,
    setMarket: setMarket,
    setSector: setSector,
    counts: function () {
      return {
        cards: document.querySelectorAll('#mkIssues .mk-issue').length,
        markets: document.querySelectorAll('#mkStatus .mk-market').length,
        sectors: document.querySelectorAll('#mkSectors .mk-sector').length,
        calendar: document.querySelectorAll('#mkCalendar .mk-cal-row').length,
        archived: document.querySelectorAll('#mkCalendar .mk-cal-src').length,
        dday: Array.prototype.map.call(document.querySelectorAll('#mkCalendar .mk-dday'), function (node) {
          return node.textContent.trim();
        }),
      };
    },
    sessionFor: function (market) { return DATA.sessions[market] || null; },
    ddayFor: function (isoDate) {
      var date = parseDate(isoDate);
      if (!date) return null;
      return dayDiff(date, kstToday());
    },
  };
})();
"""


if __name__ == "__main__":
    build()

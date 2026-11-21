#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_today_html.py — 오늘 한 번에 보는 얇은 데일리 허브(today.html)를 빌드한다.

상단 4카드
  1) 오늘 마감 공고   — archive.db 활성 공고 중 KST 오늘 마감
  2) KEV 우선 조치    — cve_data.json 의 KEV 중 조치 기한이 가까운/새로 등재된 항목
  3) 오늘 복습 큐     — 브라우저 localStorage(study_review_queue_v1 등)를 읽어 오늘 복습 수
  4) 오늘 AI 브리핑   — ai_data.json 의 오늘 브리핑 요약
하단 요약
  · 오늘 날씨·옷차림   — 빌드 시점 Apple Weather + 브라우저 Open-Meteo 실시간
  · 오늘의 게임       — 워게임·3단서 추리의 오늘 문제

상태는 '정상 · 데이터 없음 · 갱신 지연(26시간 초과) · 날씨 요청 실패'로 구분한다.
마감 기준은 모두 KST(Asia/Seoul)이며, 이모지 없이 다른 페이지와 같은 디자인 토큰을 쓴다.
"""
import json
import os
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script, safe_url
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TODAY_HTML = os.path.join(BASE_DIR, "today.html")
KST = timezone(timedelta(hours=9))
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
STALE_HOURS = 26


def _parse_stamp(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S KST", "%Y-%m-%d %H:%M KST",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=KST)
        except ValueError:
            continue
    return None


def _ms(value):
    dt = _parse_stamp(value)
    if dt is None:
        return None
    return int(dt.timestamp() * 1000)


def _age_hours(value, now):
    dt = _parse_stamp(value)
    if dt is None:
        return None
    return round((now - dt).total_seconds() / 3600, 1)


# ---------------------------------------------------------------- 1) 공고
def load_jobs(now):
    from db_manager import init_db, get_active_jobs
    init_db()
    jobs = get_active_jobs(today_date=now.date())
    today = [j for j in jobs if j.get("deadline_status") == "D_DAY"]
    week = [j for j in jobs if j.get("deadline_status") in ("D_DAY", "URGENT")]
    latest = max((j.get("last_seen_at") or "" for j in jobs), default="")
    items = []
    for job in today[:3]:
        items.append({
            "company": job.get("company") or "",
            "title": job.get("title") or "",
            "deadline": job.get("deadline_label") or job.get("deadline") or "",
            "url": safe_url(job.get("url"), "#"),
        })
    return {
        "count": len(today),
        "week": len(week),
        "total": len(jobs),
        "items": items,
        "updated": latest,
        "updated_ms": _ms(latest),
    }


# ---------------------------------------------------------------- 2) CVE
def load_cve(now):
    path = os.path.join(BASE_DIR, "cve_data.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {}
    items = data.get("items") or []
    meta = data.get("meta") or {}
    kev = [i for i in items if i.get("is_kev")]

    def due_key(item):
        value = (item.get("kev_due_date") or "")[:10]
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return now.date() + timedelta(days=3650)

    today = now.date()
    week_end = today + timedelta(days=7)
    urgent = [i for i in kev if today <= due_key(i) <= week_end]
    fresh = [i for i in kev if (i.get("kev_date_added") or "")[:10] >= str(today - timedelta(days=3))]
    focus = sorted(urgent, key=due_key)[:3]
    for item in sorted(fresh, key=lambda i: (i.get("kev_date_added") or ""), reverse=True):
        if len(focus) >= 3:
            break
        if item not in focus:
            focus.append(item)
    rows = []
    for item in focus:
        due = (item.get("kev_due_date") or "")[:10]
        label = ""
        if due:
            try:
                days = (datetime.strptime(due, "%Y-%m-%d").date() - today).days
                if days < 0:
                    label = "기한 %d일 경과" % abs(days)
                elif days == 0:
                    label = "오늘 기한"
                else:
                    label = "D-%d" % days
            except ValueError:
                label = ""
        rows.append({
            "cve_id": item.get("cve_id") or "",
            "title": item.get("title_ko") or "",
            "severity": (item.get("severity") or "").upper(),
            "due": label,
        })
    return {
        "kev": len(kev),
        "urgent": len(urgent),
        "fresh": len(fresh),
        "items": rows,
        "updated": meta.get("collected_at") or "",
        "updated_ms": _ms(meta.get("collected_at")),
    }


# ---------------------------------------------------------------- 3) AI
def load_ai(now):
    path = os.path.join(BASE_DIR, "ai_data.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {}
    items = data.get("items") or []
    featured = [i for i in items if i.get("is_featured")] or items
    top = [{
        "title": i.get("title_ko") or "",
        "category": i.get("category") or "",
        "url": safe_url(i.get("url"), "#"),
    } for i in featured[:2]]
    return {
        "briefing": data.get("briefing") or "",
        "total": data.get("total") or len(items),
        "items": top,
        "updated": data.get("updated_at") or "",
        "updated_ms": _ms(data.get("updated_at")),
    }


# ---------------------------------------------------------------- 4) 게임
def load_games(now):
    from db_manager import get_connection
    today_str = now.strftime("%Y-%m-%d")
    wargame = {}
    clue = {}
    try:
        conn = get_connection()
        row = conn.execute(
            "SELECT id, title, created_date FROM wargame_questions "
            "WHERE is_daily = 1 AND created_date = ? ORDER BY sort_order, id LIMIT 1;",
            (today_str,),
        ).fetchone()
        if row is None:
            row = conn.execute(
                "SELECT id, title, created_date FROM wargame_questions "
                "WHERE is_daily = 1 ORDER BY created_date DESC, sort_order, id LIMIT 1;"
            ).fetchone()
        if row is not None:
            wargame = {"title": row["title"] or "", "date": row["created_date"] or ""}
        row = conn.execute(
            "SELECT id, title, puzzle_date FROM clue_questions "
            "WHERE puzzle_date = ? ORDER BY is_daily DESC, id LIMIT 1;",
            (today_str,),
        ).fetchone()
        if row is None:
            row = conn.execute(
                "SELECT id, title, puzzle_date FROM clue_questions "
                "ORDER BY puzzle_date DESC, id LIMIT 1;"
            ).fetchone()
        if row is not None:
            clue = {"title": row["title"] or "", "date": row["puzzle_date"] or ""}
        conn.close()
    except Exception:  # noqa: BLE001 - 게임 카드가 없어도 나머지 허브는 그려야 한다
        pass
    return {"wargame": wargame, "clue": clue, "today": today_str}


# ---------------------------------------------------------------- 5) 날씨
def load_weather(now):
    try:
        from build_outfit_html import load_build_weather, band_for, BANDS
    except Exception:  # noqa: BLE001
        return {"ok": False, "bands": [], "updated": ""}
    try:
        wx = load_build_weather()
    except Exception:  # noqa: BLE001
        return {"ok": False, "bands": [], "updated": ""}
    band = band_for(wx.get("now_temp"))
    bands = [{
        "min": b["min"], "max": b["max"], "label": b["name"], "line": b["line"],
    } for b in BANDS]
    return {
        "ok": wx.get("now_temp") is not None,
        "source": wx.get("source") or "",
        "temp": wx.get("now_temp"),
        "feels": wx.get("now_feels"),
        "cond": wx.get("now_cond") or "",
        "low": wx.get("today_low"),
        "high": wx.get("today_high"),
        "pop": wx.get("today_pop"),
        "wind": wx.get("now_wind"),
        "line": band.get("line") or "",
        "band": band.get("name") or "",
        "updated": wx.get("updated") or now.strftime("%H:%M"),
        "bands": bands,
    }


def build():
    now = datetime.now(KST)
    today_str = now.strftime("%Y-%m-%d")
    date_label = "%d년 %d월 %d일 (%s)" % (now.year, now.month, now.day, WEEKDAYS[now.weekday()])
    built_at = now.strftime("%Y-%m-%d %H:%M KST")

    jobs = load_jobs(now)
    cve = load_cve(now)
    ai = load_ai(now)
    games = load_games(now)
    weather = load_weather(now)

    data = {
        "today": today_str,
        "build_date_kst": today_str,
        "date_label": date_label,
        "built_at": built_at,
        "built_ms": int(now.timestamp() * 1000),
        "stale_hours": STALE_HOURS,
        "jobs": jobs,
        "cve": cve,
        "ai": ai,
        "games": games,
        "weather": weather,
    }

    html = TEMPLATE
    html = html.replace("__DATE_LABEL__", date_label)
    html = html.replace("__BUILT_AT__", built_at)
    html = html.replace("__TODAY__", today_str)
    html = html.replace("__JOBS_COUNT__", str(jobs["count"]))
    html = html.replace("__JOBS_WEEK__", str(jobs["week"]))
    html = html.replace("__JOBS_TOTAL__", str(jobs["total"]))
    html = html.replace("__KEV_COUNT__", str(cve["kev"]))
    html = html.replace("__KEV_URGENT__", str(cve["urgent"]))
    html = html.replace("__AI_TOTAL__", str(ai["total"]))
    html = html.replace("__TODAY_DATA__", safe_json_for_script(json.dumps(data, ensure_ascii=False)))
    html = ui_shell.apply(html, "today")
    with open(TODAY_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(html))
    return {"jobs": jobs["count"], "kev": cve["kev"], "ai": ai["total"],
            "wargame": bool(games["wargame"]), "clue": bool(games["clue"]),
            "weather": weather.get("ok", False)}


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 오늘</title>
  <meta name="description" content="오늘 마감 공고, 이번 주 KEV 우선 조치, 오늘 복습할 문항, AI 브리핑, 서울 날씨와 옷차림, 오늘의 워게임·추리를 한 화면에서 확인하는 데일리 허브입니다.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
  <style>
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

      --warn-bg: #fffbeb;  --warn-text: #b45309;  --warn-border: #fde68a;
      --no-bg: #fef2f2;    --no-text: #b91c1c;    --no-border: #fecaca;
      --ok-bg: #ecfdf5;    --ok-text: #047857;    --ok-border: #a7f3d0;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
      --ease: cubic-bezier(0.2, 0.8, 0.2, 1);
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

      --warn-bg: rgba(245, 158, 11, 0.12); --warn-text: #fcd34d; --warn-border: rgba(245, 158, 11, 0.32);
      --no-bg: rgba(239, 68, 68, 0.12);    --no-text: #fca5a5;   --no-border: rgba(239, 68, 68, 0.32);
      --ok-bg: rgba(16, 185, 129, 0.12);   --ok-text: #6ee7b7;   --ok-border: rgba(16, 185, 129, 0.32);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
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
      transition: background-color 150ms ease, color 150ms ease;
    }

    a { color: inherit; }
    button { font-family: inherit; }

    .navbar {
      position: sticky; top: 0; z-index: 50;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
    }
    .nav-container {
      max-width: 1360px; margin: 0 auto; padding: 0 20px; height: 60px;
      display: flex; align-items: center; gap: 16px;
    }
    .nav-links { display: flex; align-items: center; gap: 6px; margin-left: auto; }
    .nav-links a {
      padding: 7px 11px; border-radius: 9px; font-size: 13.5px; font-weight: 600;
      color: var(--text-secondary); text-decoration: none;
      transition: background-color 150ms var(--ease), color 150ms var(--ease);
    }
    .nav-links a:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .container { max-width: 1360px; margin: 0 auto; padding: 26px 20px 48px; }

    /* ---- 히어로 ---- */
    .today-hero {
      display: flex; align-items: flex-end; justify-content: space-between;
      gap: 18px; flex-wrap: wrap; margin-bottom: 20px;
    }
    .hero-title {
      font-size: 27px; font-weight: 800; letter-spacing: -0.045em;
      color: var(--text-primary);
    }
    .hero-date {
      margin-top: 6px; font-size: 13.5px; font-weight: 600; color: var(--text-secondary);
    }
    .hero-note { font-size: 12.5px; color: var(--text-muted); margin-top: 4px; }
    .update-meta {
      display: inline-flex; align-items: center; gap: 7px;
      padding: 7px 12px; border: 1px solid var(--border-default); border-radius: 999px;
      background: var(--bg-surface); font-size: 12px; color: var(--text-secondary);
      white-space: nowrap;
    }
    .live-dot {
      width: 7px; height: 7px; border-radius: 50%; background: #10b981;
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.16);
    }
    /* 집계가 갱신 대기 중이면 초록 점 대신 경고색으로 바꾼다. */
    .update-meta.is-waiting .live-dot {
      background: #f59e0b; box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.18);
    }

    /* 자정을 넘겨 열었을 때: 마지막 집계일과 지금 날짜가 다르면 카드 위에 한 줄로 알린다. */
    .day-notice {
      margin: 0 0 14px; padding: 11px 14px;
      border: 1px solid var(--warn-border); background: var(--warn-bg); color: var(--warn-text);
      border-radius: 12px; font-size: 12.5px; line-height: 1.55;
    }
    .day-notice[hidden] { display: none; }

    /* ---- 카드 그리드 ---- */
    .day-grid {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px; margin-bottom: 14px;
    }
    .day-card {
      display: flex; flex-direction: column; gap: 10px;
      padding: 18px 20px 16px; min-width: 0;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 16px;
      box-shadow: var(--card-shadow);
      transition: transform 150ms var(--ease), box-shadow 150ms var(--ease), border-color 150ms var(--ease);
    }
    .day-card:hover { box-shadow: var(--card-shadow-hover); border-color: var(--border-strong); }
    .day-card-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .day-label {
      font-size: 12.5px; font-weight: 700; letter-spacing: 0.01em; color: var(--text-secondary);
    }
    .day-chip {
      flex: 0 0 auto; padding: 3px 8px; border-radius: 999px;
      font-size: 11px; font-weight: 700; letter-spacing: -0.01em;
      border: 1px solid var(--ok-border); background: var(--ok-bg); color: var(--ok-text);
      white-space: nowrap;
    }
    .day-chip[data-state="stale"] { border-color: var(--warn-border); background: var(--warn-bg); color: var(--warn-text); }
    .day-chip[data-state="none"] { border-color: var(--border-default); background: var(--bg-subtle); color: var(--text-muted); }
    .day-chip[data-state="error"] { border-color: var(--no-border); background: var(--no-bg); color: var(--no-text); }

    .day-value { display: flex; align-items: baseline; gap: 4px; }
    .day-value strong {
      font-size: 32px; font-weight: 800; letter-spacing: -0.05em; color: var(--text-primary);
      font-variant-numeric: tabular-nums; line-height: 1.1;
    }
    .day-value span { font-size: 13px; font-weight: 600; color: var(--text-muted); }
    .day-sub { font-size: 12.5px; color: var(--text-secondary); }
    .day-sub.is-muted { color: var(--text-muted); }

    .day-list { list-style: none; display: flex; flex-direction: column; gap: 6px; margin: 2px 0 0; }
    .day-list li {
      display: flex; align-items: flex-start; gap: 8px; min-width: 0;
      font-size: 12.5px; color: var(--text-secondary); line-height: 1.45;
    }
    .day-list .dot { flex: 0 0 auto; width: 4px; height: 4px; margin-top: 8px; border-radius: 50%; background: var(--border-strong); }
    .day-list .item { min-width: 0; overflow: hidden; }
    .day-list .item strong {
      display: block; font-weight: 600; color: var(--text-primary);
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .day-list .item span { display: block; color: var(--text-muted); font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    .day-empty { font-size: 12.5px; color: var(--text-muted); }

    /* AI 브리핑은 카드 높이를 맞추기 위해 4줄까지만 보여 주고, 전체는 ai.html 에서 읽는다. */
    #aiBrief {
      display: -webkit-box;
      -webkit-line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
      line-height: 1.6;
    }

    .day-more {
      margin-top: auto; padding-top: 8px;
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 12.5px; font-weight: 700; color: var(--accent-primary);
      text-decoration: none; align-self: flex-start;
      transition: color 150ms var(--ease), transform 150ms var(--ease);
    }
    .day-more:hover { color: var(--accent-hover); }
    .day-more:active { transform: translateX(2px); }
    .day-more svg { width: 14px; height: 14px; }

    /* ---- 하단 요약 2카드 ---- */
    .day-row {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;
    }
    .summary-card {
      display: flex; flex-direction: column; gap: 10px;
      padding: 18px 20px 16px; min-width: 0;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 16px;
      box-shadow: var(--card-shadow);
    }
    .wx-line { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .wx-temp { display: flex; align-items: baseline; gap: 3px; }
    .wx-temp strong { font-size: 26px; font-weight: 800; letter-spacing: -0.045em; font-variant-numeric: tabular-nums; }
    .wx-temp span { font-size: 12.5px; font-weight: 600; color: var(--text-muted); }
    .wx-cond { font-size: 13px; font-weight: 600; color: var(--text-secondary); }
    .wx-range { font-size: 12px; color: var(--text-muted); }
    .wx-outfit {
      padding: 10px 12px; border-radius: 10px;
      background: var(--bg-subtle); border: 1px solid var(--border-subtle);
      font-size: 12.5px; color: var(--text-secondary); line-height: 1.55;
    }
    .wx-outfit b { color: var(--text-primary); font-weight: 700; }

    .game-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
    .game-list li { min-width: 0; }
    .game-link {
      display: flex; align-items: center; justify-content: space-between; gap: 12px;
      padding: 10px 12px; border: 1px solid var(--border-default); border-radius: 11px;
      background: var(--bg-page); text-decoration: none; min-width: 0;
      transition: background-color 150ms var(--ease), border-color 150ms var(--ease), transform 150ms var(--ease);
    }
    .game-link:hover { background: var(--bg-subtle); border-color: var(--border-strong); }
    .game-link:active { transform: scale(0.99); }
    .game-link .gl-title {
      min-width: 0; font-size: 13px; font-weight: 600; color: var(--text-primary);
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .game-link .gl-kind { flex: 0 0 auto; font-size: 11px; font-weight: 700; color: var(--text-muted); }

    .foot {
      margin-top: 26px; padding-top: 16px; border-top: 1px solid var(--border-default);
      font-size: 11.5px; color: var(--text-muted); line-height: 1.7;
    }

    @media (max-width: 900px) {
      .day-grid, .day-row { grid-template-columns: minmax(0, 1fr); }
    }

    @media (max-width: 768px) {
      .container { padding: 18px 14px 28px; }
      .hero-title { font-size: 22px; }
      .hero-date { font-size: 12.5px; }
      .day-card, .summary-card { padding: 15px 15px 14px; border-radius: 14px; }
      .day-value strong { font-size: 28px; }
      .wx-temp strong { font-size: 24px; }
    }

    @media (max-width: 380px) {
      .container { padding: 14px 10px 24px; }
      .day-card, .summary-card { padding: 13px 12px; }
      .hero-title { font-size: 20px; }
      .day-label { font-size: 12px; }
      .wx-line { gap: 7px; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        transition-delay: 0ms !important;
        scroll-behavior: auto !important;
      }
    }
  </style>
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
      <a class="brand" href="index.html">Infosec Archive</a>
      <div class="update-meta"><span class="live-dot"></span><span>__BUILT_AT__ 기준 · 매일 08:00 갱신</span></div>
      <nav class="nav-links" aria-label="바로가기">
        <a href="index.html">채용공고</a>
        <a href="cve.html">CVE</a>
        <a href="study.html">시험 공부</a>
        <a href="ai.html">AI 트렌드</a>
      </nav>
    </div>
  </header>

  <main class="container">
    <section class="today-hero">
      <div>
        <h1 class="hero-title">오늘 한 번에 보기</h1>
        <p class="hero-date" id="todayDate">__DATE_LABEL__ · KST</p>
        <p class="hero-note">마감·취약점·복습·브리핑을 카드 하나씩만 확인하고, 자세한 내용은 각 페이지에서 봅니다.</p>
      </div>
      <span class="update-meta"><span class="live-dot"></span><span id="heroUpdated">__BUILT_AT__ 기준</span></span>
    </section>

    <p class="day-notice" id="dayNotice" role="status" hidden></p>

    <section class="day-grid" aria-label="오늘 핵심 4카드">
      <!-- 1. 오늘 마감 공고 -->
      <article class="day-card" data-card="jobs">
        <div class="day-card-head">
          <span class="day-label">오늘 마감 공고</span>
          <span class="day-chip" id="jobsState" data-state="ok">정상</span>
        </div>
        <p class="day-value"><strong id="jobsCount">__JOBS_COUNT__</strong><span id="jobsUnit">건</span></p>
        <p class="day-sub" id="jobsSub">이번 주 마감 __JOBS_WEEK__건 · 전체 활성 __JOBS_TOTAL__건</p>
        <ul class="day-list" id="jobsList"></ul>
        <p class="day-empty" id="jobsEmpty" hidden>오늘 마감으로 잡힌 공고가 없습니다.</p>
        <a class="day-more" href="index.html">채용공고 전체 보기
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"></path></svg>
        </a>
      </article>

      <!-- 2. KEV 우선 조치 -->
      <article class="day-card" data-card="cve">
        <div class="day-card-head">
          <span class="day-label">KEV 우선 조치</span>
          <span class="day-chip" id="cveState" data-state="ok">정상</span>
        </div>
        <p class="day-value"><strong id="cveCount">__KEV_COUNT__</strong><span>건 KEV</span></p>
        <p class="day-sub" id="cveSub">이번 주 조치 기한 __KEV_URGENT__건</p>
        <ul class="day-list" id="cveList"></ul>
        <p class="day-empty" id="cveEmpty" hidden>표시할 KEV 항목이 없습니다.</p>
        <a class="day-more" href="cve.html">CVE 리포트 열기
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"></path></svg>
        </a>
      </article>

      <!-- 3. 오늘 복습 큐 -->
      <article class="day-card" data-card="study">
        <div class="day-card-head">
          <span class="day-label">오늘 복습 큐</span>
          <span class="day-chip" id="studyState" data-state="none">이 브라우저</span>
        </div>
        <p class="day-value"><strong id="studyCount">0</strong><span>문항</span></p>
        <p class="day-sub" id="studySub">퀴즈에서 틀리거나 북마크한 문항이 자동으로 쌓입니다.</p>
        <ul class="day-list" id="studyList"></ul>
        <p class="day-empty" id="studyEmpty" hidden>오늘 복습할 문항이 없습니다.</p>
        <a class="day-more" href="study.html">시험 공부 허브 열기
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"></path></svg>
        </a>
      </article>

      <!-- 4. 오늘 AI 브리핑 -->
      <article class="day-card" data-card="ai">
        <div class="day-card-head">
          <span class="day-label">오늘 AI 브리핑</span>
          <span class="day-chip" id="aiState" data-state="ok">정상</span>
        </div>
        <p class="day-value"><strong id="aiCount">__AI_TOTAL__</strong><span>건 수집</span></p>
        <p class="day-sub" id="aiSub">오늘의 흐름 한 줄 요약</p>
        <p class="day-sub" id="aiBrief">브리핑을 불러오지 못했습니다.</p>
        <ul class="day-list" id="aiList"></ul>
        <a class="day-more" href="ai.html">AI 트렌드 전체 보기
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"></path></svg>
        </a>
      </article>
    </section>

    <section class="day-row" aria-label="오늘 요약">
      <!-- 날씨·옷차림 -->
      <article class="summary-card" data-card="weather">
        <div class="day-card-head">
          <span class="day-label">오늘 날씨·옷차림</span>
          <span class="day-chip" id="weatherState" data-state="ok">정상</span>
        </div>
        <div class="wx-line">
          <span class="wx-temp"><strong id="wxTemp">-</strong><span>°C</span></span>
          <span class="wx-cond" id="wxCond">-</span>
          <span class="wx-range" id="wxRange">서울</span>
        </div>
        <p class="wx-outfit" id="wxOutfit">옷차림 추천을 불러오는 중입니다.</p>
        <a class="day-more" href="outfit.html">옷차림 가이드 열기
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"></path></svg>
        </a>
      </article>

      <!-- 오늘의 게임 -->
      <article class="summary-card" data-card="games">
        <div class="day-card-head">
          <span class="day-label">오늘의 게임</span>
          <span class="day-chip" id="gameState" data-state="ok">정상</span>
        </div>
        <ul class="game-list" id="gameList"></ul>
        <p class="day-empty" id="gameEmpty" hidden>오늘 문제를 불러오지 못했습니다.</p>
      </article>
    </section>

    <p class="foot" id="todayFoot">
      __BUILT_AT__ 기준 · 마감 기준은 모두 KST(Asia/Seoul)입니다. 복습 큐는 이 브라우저(localStorage)에만 저장되며
      서버로 전송되지 않습니다. 날씨는 Apple Weather 기본값에 브라우저가 Open-Meteo 실시간 값을 덧입힙니다.
    </p>
  </main>

  <script>
    const TODAY = __TODAY_DATA__;
  </script>
  <script>
    (function () {
      'use strict';

      var DAY_MS = 86400000;
      var WEEKDAY = ['일', '월', '화', '수', '목', '금', '토'];

      function byId(id) { return document.getElementById(id); }

      function esc(text) { return String(text == null ? '' : text); }

      function two(n) { return (n < 10 ? '0' : '') + n; }

      // 브라우저 시계를 KST(UTC+9)로 옮겨 날짜만 뽑는다 — 기기 시간대와 상관없이 같은 값이 나온다.
      function kstDate(ms) {
        var d = new Date((ms == null ? Date.now() : ms) + 9 * 3600000);
        return d.getUTCFullYear() + '-' + two(d.getUTCMonth() + 1) + '-' + two(d.getUTCDate());
      }

      function shortDate(dateStr) {
        var parts = String(dateStr || '').split('-');
        if (parts.length !== 3) return '';
        return parseInt(parts[1], 10) + '/' + parseInt(parts[2], 10);
      }

      function longDate(dateStr) {
        var parts = String(dateStr || '').split('-');
        if (parts.length !== 3) return '';
        var y = parseInt(parts[0], 10);
        var m = parseInt(parts[1], 10);
        var d = parseInt(parts[2], 10);
        var wd = WEEKDAY[new Date(Date.UTC(y, m - 1, d)).getUTCDay()];
        return y + '년 ' + m + '월 ' + d + '일 (' + wd + ')';
      }

      // 일간 집계 기준일(빌드한 날)과 지금(KST) 날짜는 따로 본다.
      // 08:00 갱신 전에 자정을 넘기면 어제 집계가 오늘 값처럼 보이는 문제를 막는다.
      // 두 값은 refreshDayDependentUI()가 다시 계산하므로, 탭을 열어 둔 채 자정을 넘겨도
      // 새로고침 없이 날짜·기준일·갱신 대기 표시가 따라온다.
      var buildDateKst = TODAY.build_date_kst || TODAY.today || '';
      var buildLabel = shortDate(buildDateKst) || buildDateKst;
      var builtAtText = TODAY.built_at || '';
      var dayStale = false;
      var dayToday = kstDate();

      function setChip(id, state, label) {
        var el = byId(id);
        if (!el) return;
        el.setAttribute('data-state', state);
        el.textContent = label;
        el.setAttribute('aria-label', label);
      }

      // 집계 기준일이 지났으면 카운트 자체가 오늘 값이 아니라는 것을 칩에서 먼저 알린다.
      function markDated(chipId, updatedMs, hasData) {
        if (!hasData) {
          setChip(chipId, 'none', '데이터 없음');
          return;
        }
        if (dayStale) {
          setChip(chipId, 'stale', buildLabel + ' 기준 · 갱신 대기');
          return;
        }
        markFresh(chipId, updatedMs, hasData);
      }

      // 'D-Day (오늘 마감)' 처럼 빌드한 날 기준으로 쓰인 라벨을 기준일 라벨로 바꾼다.
      function retagDay(text, fromLabel, toLabel) {
        if (!dayStale) return text;
        return String(text == null ? '' : text).split(fromLabel).join(toLabel);
      }

      // 갱신 지연: 수집 시각이 26시간을 넘겼는지 본다(페이지를 며칠 뒤에 열어도 바로 드러나게).
      function markFresh(chipId, updatedMs, hasData) {
        if (!hasData) {
          setChip(chipId, 'none', '데이터 없음');
          return;
        }
        if (!updatedMs) {
          setChip(chipId, 'stale', '갱신 시각 없음');
          return;
        }
        var hours = (Date.now() - updatedMs) / 3600000;
        if (hours > (TODAY.stale_hours || 26)) {
          setChip(chipId, 'stale', Math.floor(hours) + '시간 전 갱신');
        } else {
          setChip(chipId, 'ok', '정상');
        }
      }

      function stamp(ms) {
        if (!ms) return '';
        var d = new Date(ms);
        function two(n) { return String(n).padStart(2, '0'); }
        return (d.getMonth() + 1) + '/' + d.getDate() + ' ' + two(d.getHours()) + ':' + two(d.getMinutes());
      }

      function addItem(listEl, titleText, subText) {
        var li = document.createElement('li');
        var dot = document.createElement('span');
        dot.className = 'dot';
        var box = document.createElement('span');
        box.className = 'item';
        var strong = document.createElement('strong');
        strong.textContent = titleText;
        box.appendChild(strong);
        if (subText) {
          var small = document.createElement('span');
          small.textContent = subText;
          box.appendChild(small);
        }
        li.appendChild(dot);
        li.appendChild(box);
        listEl.appendChild(li);
      }

      /* ---------- 1) 오늘 마감 공고 ---------- */
      function renderJobsCard() {
        var jobs = TODAY.jobs || {};
        var list = byId('jobsList');
        list.innerHTML = '';
        byId('jobsCount').textContent = String(jobs.count || 0);
        byId('jobsUnit').textContent = dayStale ? '건 · ' + buildLabel + ' 기준' : '건';
        var sub = '이번 주 마감 ' + (jobs.week || 0) + '건 · 전체 활성 ' + (jobs.total || 0) + '건';
        byId('jobsSub').textContent = dayStale
          ? buildLabel + ' 08:00 갱신 전 집계입니다 · ' + sub
          : sub;
        var items = jobs.items || [];
        items.forEach(function (job) {
          var deadline = retagDay(job.deadline, '오늘 마감', buildLabel + ' 마감');
          addItem(list, job.company, job.title + (deadline ? ' · ' + deadline : ''));
        });
        var empty = byId('jobsEmpty');
        empty.textContent = dayStale
          ? buildLabel + ' 마감으로 잡힌 공고가 없습니다.'
          : '오늘 마감으로 잡힌 공고가 없습니다.';
        empty.hidden = items.length > 0;
        markDated('jobsState', jobs.updated_ms, (jobs.total || 0) > 0);
      }

      /* ---------- 2) KEV 우선 조치 ---------- */
      function renderCveCard() {
        var cve = TODAY.cve || {};
        var list = byId('cveList');
        list.innerHTML = '';
        byId('cveCount').textContent = String(cve.kev || 0);
        var cveSub = '이번 주 조치 기한 ' + (cve.urgent || 0) + '건 · 새 등재 ' + (cve.fresh || 0) + '건';
        byId('cveSub').textContent = dayStale ? buildLabel + ' 기준 · ' + cveSub : cveSub;
        var items = cve.items || [];
        items.forEach(function (item) {
          var due = retagDay(item.due, '오늘 기한', buildLabel + ' 기한');
          addItem(list, item.cve_id + (item.severity ? ' · ' + item.severity : ''),
            item.title + (due ? ' · ' + due : ''));
        });
        byId('cveEmpty').hidden = items.length > 0;
        markDated('cveState', cve.updated_ms, (cve.kev || 0) > 0 || (cve.items || []).length > 0);
      }

      /* ---------- 3) 오늘 복습 큐 (이 브라우저) ---------- */
      function readJson(key, fallback) {
        try {
          var raw = localStorage.getItem(key);
          if (!raw) return fallback;
          var parsed = JSON.parse(raw);
          return (parsed && typeof parsed === 'object') ? parsed : fallback;
        } catch (e) { return fallback; }
      }

      function renderStudy() {
        var store = readJson('study_review_queue_v1', { items: {}, dismissed: {} });
        var items = store.items || {};
        var answers = readJson('study_user_answers_v4', {});
        var bookmarks = readJson('study_bookmarks_v1', {});
        var now = Date.now();
        var ids = Object.keys(items);
        var due = ids.filter(function (id) {
          var item = items[id] || {};
          return Number(item.next_review_at || 0) <= now;
        });
        var wrong = 0;
        var manual = 0;
        due.forEach(function (id) {
          if (items[id] && items[id].manual) manual += 1;
          else wrong += 1;
        });
        byId('studyCount').textContent = String(due.length);
        byId('studySub').textContent = '전체 큐 ' + ids.length + '문항 · 오답 ' + wrong + ' · 직접 담음 ' + manual;

        var list = byId('studyList');
        list.innerHTML = '';
        var nextMs = ids
          .map(function (id) { return Number((items[id] || {}).next_review_at || 0); })
          .filter(function (ms) { return ms > now; })
          .sort(function (a, b) { return a - b; })[0];
        if (due.length) {
          addItem(list, '지금 풀 수 있는 복습 ' + due.length + '문항', '시험 공부 허브의 오늘 복습에서 이어서 풀 수 있습니다.');
        } else if (nextMs) {
          addItem(list, '다음 복습 ' + stamp(nextMs), '오늘 복습할 문항은 모두 마쳤습니다.');
        } else if (ids.length) {
          addItem(list, '예정된 복습이 없습니다', '큐에 있는 문항은 모두 일정이 잡혀 있습니다.');
        }
        var answerCount = Object.keys(answers || {}).length;
        var bookmarkCount = Object.keys(bookmarks || {}).length;
        if (answerCount || bookmarkCount) {
          addItem(list, '퀴즈 기록 ' + answerCount + '문항 · 북마크 ' + bookmarkCount + '개', '이 브라우저에만 저장된 기록입니다.');
        }
        byId('studyEmpty').hidden = due.length > 0 || list.children.length > 0;
        setChip('studyState', due.length ? 'ok' : 'none', due.length ? '오늘 ' + due.length + '문항' : '이 브라우저');
      }
      renderStudy();

      /* ---------- 4) AI 브리핑 ---------- */
      function renderAiCard() {
        var ai = TODAY.ai || {};
        var list = byId('aiList');
        list.innerHTML = '';
        byId('aiCount').textContent = String(ai.total || 0);
        var brief = (ai.briefing || '').trim();
        byId('aiBrief').textContent = brief || '오늘 브리핑 요약이 아직 없습니다.';
        byId('aiSub').textContent = dayStale
          ? buildLabel + ' 브리핑 기준 · ' + '오늘의 흐름 한 줄 요약'
          : '오늘의 흐름 한 줄 요약';
        (ai.items || []).forEach(function (item) {
          addItem(list, item.title, item.category);
        });
        markDated('aiState', ai.updated_ms, (ai.total || 0) > 0);
      }

      /* ---------- 5) 날씨·옷차림 ---------- */
      function bandLine(temp) {
        var bands = (TODAY.weather && TODAY.weather.bands) || [];
        if (temp == null || !bands.length) return '';
        for (var i = 0; i < bands.length; i += 1) {
          if (temp >= bands[i].min && temp <= bands[i].max) return bands[i].line;
        }
        return bands[bands.length - 1].line;
      }

      function paintWeather(temp, feels, cond, low, high, pop, source) {
        byId('wxTemp').textContent = (temp == null) ? '-' : String(Math.round(temp));
        var parts = [];
        if (cond) parts.push(cond);
        if (feels != null && temp != null && Math.round(feels) !== Math.round(temp)) parts.push('체감 ' + Math.round(feels) + '°');
        byId('wxCond').textContent = parts.length ? parts.join(' · ') : '기온 확인 중';
        var range = [];
        if (low != null) range.push('최저 ' + Math.round(low) + '°');
        if (high != null) range.push('최고 ' + Math.round(high) + '°');
        if (pop != null) range.push('강수 ' + Math.round(pop) + '%');
        byId('wxRange').textContent = '서울 · ' + (range.length ? range.join(' · ') : '실시간');
        var line = bandLine(temp) || (TODAY.weather && TODAY.weather.line) || '';
        var band = (TODAY.weather && TODAY.weather.band) || '';
        byId('wxOutfit').innerHTML = '';
        if (line) {
          var b = document.createElement('b');
          b.textContent = band ? band + ' 구간 · ' : '';
          byId('wxOutfit').appendChild(b);
          byId('wxOutfit').appendChild(document.createTextNode(line));
        } else {
          byId('wxOutfit').textContent = '옷차림 추천을 불러오지 못했습니다.';
        }
        if (source === 'live') {
          setChip('weatherState', 'ok', '실시간');
        }
      }

      (function renderWeather() {
        var w = TODAY.weather || {};
        if (w.ok) {
          paintWeather(w.temp, w.feels, w.cond, w.low, w.high, w.pop, 'build');
          setChip('weatherState', 'ok', '빌드 ' + (w.updated || '') );
        } else {
          setChip('weatherState', 'error', '날씨 요청 실패');
          byId('wxOutfit').textContent = '날씨를 불러오지 못했습니다. 옷차림 가이드에서 직접 확인할 수 있습니다.';
        }

        if (!window.fetch) return;
        fetch('https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&timezone=Asia%2FSeoul&current=temperature_2m,apparent_temperature,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&forecast_days=1&wind_speed_unit=kmh')
          .then(function (res) {
            if (!res.ok) throw new Error('weather status ' + res.status);
            return res.json();
          })
          .then(function (payload) {
            var cur = (payload && payload.current) || {};
            var daily = (payload && payload.daily) || {};
            if (cur.temperature_2m == null) throw new Error('no temperature');
            var code = cur.weather_code;
            var cond = code == null ? '' : (code === 0 ? '맑음' : (code < 4 ? '구름 조금' : (code < 50 ? '흐림' : (code < 70 ? '비' : (code < 80 ? '눈' : '소나기')))));
            paintWeather(
              cur.temperature_2m, cur.apparent_temperature, cond,
              (daily.temperature_2m_min || [])[0], (daily.temperature_2m_max || [])[0],
              (daily.precipitation_probability_max || [])[0], 'live'
            );
          })
          .catch(function () {
            setChip('weatherState', 'error', '날씨 요청 실패');
          });
      })();

      /* ---------- 6) 오늘의 게임 ---------- */
      function renderGamesCard() {
        var games = TODAY.games || {};
        var list = byId('gameList');
        list.innerHTML = '';
        var entries = [];
        if (games.wargame && games.wargame.title) {
          entries.push({ kind: '워게임', title: games.wargame.title, href: 'wargame.html' });
        }
        if (games.clue && games.clue.title) {
          entries.push({ kind: '3단서 추리', title: games.clue.title, href: 'clue.html' });
        }
        entries.push({ kind: '퇴근길 미션', title: '오늘의 지도 한 판', href: 'mission.html' });
        entries.forEach(function (entry) {
          var li = document.createElement('li');
          var a = document.createElement('a');
          a.className = 'game-link';
          a.href = entry.href;
          var t = document.createElement('span');
          t.className = 'gl-title';
          t.textContent = entry.title;
          var k = document.createElement('span');
          k.className = 'gl-kind';
          k.textContent = entry.kind;
          a.appendChild(t);
          a.appendChild(k);
          li.appendChild(a);
          list.appendChild(li);
        });
        byId('gameEmpty').hidden = true;
        if (!(games.wargame && games.wargame.title) && !(games.clue && games.clue.title)) {
          setChip('gameState', 'none', '일부 없음');
        } else if (dayStale) {
          setChip('gameState', 'stale', buildLabel + ' 기준 · 갱신 대기');
        } else if ((games.wargame && games.wargame.date && games.wargame.date !== games.today)
          || (games.clue && games.clue.date && games.clue.date !== games.today)) {
          setChip('gameState', 'stale', '이전 문제');
        } else {
          setChip('gameState', 'ok', '정상');
        }
      }

      /* ---------- 집계 기준일 안내 (자정 경과 · 08:00 갱신 전) ---------- */
      function renderDayNotice() {
        // 히어로 날짜는 '지금(KST) 날짜'다. 자정을 넘기면 새로고침 없이 다음 날로 바뀐다.
        var heroDate = byId('todayDate');
        if (heroDate) heroDate.textContent = (longDate(dayToday) || dayToday) + ' · KST';
        var heroUpdated = byId('heroUpdated');
        if (heroUpdated) {
          heroUpdated.textContent = dayStale
            ? buildLabel + ' 기준 · 갱신 대기'
            : (builtAtText ? builtAtText + ' 기준' : '기준 시각 없음');
          var meta = heroUpdated.closest ? heroUpdated.closest('.update-meta') : null;
          if (meta) {
            if (dayStale) meta.classList.add('is-waiting');
            else meta.classList.remove('is-waiting');
          }
        }
        var notice = byId('dayNotice');
        if (!notice) return;
        if (!dayStale) {
          notice.textContent = '';
          notice.hidden = true;
          return;
        }
        var shownToday = longDate(dayToday) || dayToday;
        notice.textContent = shownToday + ' 화면을 열었지만 마지막 집계는 ' + buildLabel + ' 08:00입니다. '
          + '오늘 몫은 다음 갱신(08:00) 뒤에 채워지므로, 마감·KEV·AI 브리핑 카드는 '
          + buildLabel + ' 기준 · 갱신 대기 상태입니다.';
        notice.hidden = false;
      }

      // 날짜에 기대는 표시를 한 번에 다시 그린다.
      // 카드 내용은 매번 TODAY 원본 데이터에서 새로 만들기 때문에, 이미 '11/21 마감'으로
      // 바뀐 글자를 다시 바꾸는 일 없이 몇 번을 불러도 같은 결과(멱등)가 된다.
      function refreshDayDependentUI() {
        dayToday = kstDate();
        dayStale = !!buildDateKst && dayToday !== buildDateKst;
        renderJobsCard();
        renderCveCard();
        renderAiCard();
        renderGamesCard();
        renderDayNotice();
      }

      // 다음 KST 자정까지 남은 밀리초. 기기 시간대와 상관없이 UTC+9로만 계산한다.
      function msUntilKstMidnight() {
        var now = Date.now();
        var shifted = now + 9 * 3600000;
        var d = new Date(shifted);
        var next = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1, 0, 0, 0, 0);
        return next - shifted;
      }

      var midnightTimer = null;
      function scheduleMidnightTick() {
        if (midnightTimer) { clearTimeout(midnightTimer); midnightTimer = null; }
        var delay = msUntilKstMidnight();
        if (!isFinite(delay) || delay < 0) delay = 0;
        // 백그라운드 탭이 타이머를 조금 늦게 깨워도 자정 직후 값이 되도록 여유를 조금 둔다.
        midnightTimer = setTimeout(function () {
          midnightTimer = null;
          refreshDayDependentUI();
          scheduleMidnightTick();
        }, Math.min(delay + 300, 2147483000));
      }

      // 잠들었다 깨어난 탭(모바일 백그라운드·bfcache)은 자정 타이머가 밀렸을 수 있어 다시 계산한다.
      function refreshOnWake() {
        refreshDayDependentUI();
        scheduleMidnightTick();
      }

      document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') refreshOnWake();
      });
      window.addEventListener('focus', refreshOnWake);
      window.addEventListener('pageshow', refreshOnWake);
      // 타이머가 조용히 죽은 환경을 위한 보조 감지: 30초마다 날짜가 바뀌었는지만 본다.
      setInterval(function () {
        if (kstDate() !== dayToday) refreshOnWake();
      }, 30000);

      /* ---------- 날짜 의존 표시 첫 렌더 ---------- */
      refreshOnWake();

      /* ---------- 테마 ---------- */
      var themeToggle = byId('themeToggle');
      var moonIcon = byId('moonIcon');
      var sunIcon = byId('sunIcon');
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
        var saved = null;
        try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
        if (document.documentElement.getAttribute('data-theme') === 'dark'
          || saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          setTheme('dark');
        } else {
          setTheme('light');
        }
      })();
      if (themeToggle) {
        themeToggle.addEventListener('click', function () {
          setTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
        });
      }
    })();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    print(build())

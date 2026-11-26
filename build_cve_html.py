#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_cve_html.py — archive.db 의 cve_reports 테이블을 단일 소스로
CVE 취약점 리포트 페이지(cve.html)와 데이터 파일(cve_data.json)을 빌드한다.
(index.html / study.html / ai.html 과 동일한 secjobs-theme 디자인 시스템)
"""
import os
import re
import json
from datetime import datetime, timezone, timedelta

from db_manager import (init_db, get_cve_reports, get_cve_stats, get_cve_alerts,
                        normalize_cve_published_dates)
from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CVE_DATA_JSON = os.path.join(BASE_DIR, "cve_data.json")
CVE_HTML = os.path.join(BASE_DIR, "cve.html")
KST = timezone(timedelta(hours=9))

SEVERITY_KO = {"CRITICAL": "치명적", "HIGH": "높음", "MEDIUM": "보통", "LOW": "낮음", "UNKNOWN": "미평가"}


def esc(s):
    s = "" if s is None else str(s)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


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

      --tag-bg: #f8fafc;
      --tag-border: #e2e8f0;
      --tag-text: #475569;

      --sev-critical-bg: #fef2f2; --sev-critical-text: #b91c1c; --sev-critical-border: #fecaca;
      --sev-high-bg: #fff7ed;     --sev-high-text: #c2410c;     --sev-high-border: #fed7aa;
      --sev-medium-bg: #fffbeb;   --sev-medium-text: #a16207;   --sev-medium-border: #fde68a;
      --sev-low-bg: #f1f5f9;      --sev-low-text: #475569;      --sev-low-border: #e2e8f0;

      --kev-bg: #0f172a; --kev-text: #ffffff;
      --impact-bg: #f8fafc;
      --remed-bg: #f0f9ff;
      --remed-border: #bae6fd;

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

      --tag-bg: #27272a;
      --tag-border: #3f3f46;
      --tag-text: #d4d4d8;

      --sev-critical-bg: rgba(239, 68, 68, 0.16);  --sev-critical-text: #f87171; --sev-critical-border: rgba(239, 68, 68, 0.3);
      --sev-high-bg: rgba(234, 88, 12, 0.16);      --sev-high-text: #fb923c;     --sev-high-border: rgba(234, 88, 12, 0.3);
      --sev-medium-bg: rgba(234, 179, 8, 0.16);    --sev-medium-text: #facc15;   --sev-medium-border: rgba(234, 179, 8, 0.3);
      --sev-low-bg: rgba(148, 163, 184, 0.16);     --sev-low-text: #cbd5e1;      --sev-low-border: rgba(148, 163, 184, 0.3);

      --kev-bg: #f4f4f5; --kev-text: #18181b;
      --impact-bg: #1f1f23;
      --remed-bg: rgba(14, 116, 144, 0.12);
      --remed-border: rgba(56, 189, 248, 0.28);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

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

    /* Global Header (index.html / study.html / ai.html 과 동일) */
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
    }

    .nav-brand { display: flex; align-items: center; gap: 10px; }

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

    .nav-actions { display: flex; align-items: center; gap: 12px; }

    .update-meta {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
    }

    .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
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

    /* Layout */
    .container { max-width: 980px; margin: 0 auto; padding: 32px 20px 80px; }

    .hero { margin-bottom: 22px; }

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

    .hero-title {
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .hero-desc {
      font-size: 14.5px;
      color: var(--text-secondary);
      line-height: 1.65;
      margin-bottom: 16px;
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
    }

    .stat-chip strong { color: var(--text-primary); font-weight: 600; }

    /* 우선 조치 브리핑 */
    .briefing {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 18px;
      box-shadow: var(--card-shadow);
    }

    .briefing-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }

    .briefing-title {
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 7px;
    }

    .briefing-title .bar {
      width: 3px;
      height: 14px;
      border-radius: 2px;
      background: var(--accent-primary);
      display: inline-block;
    }

    .briefing-time { font-size: 11.5px; color: var(--text-muted); white-space: nowrap; }

    .briefing-text {
      font-size: 13.5px;
      line-height: 1.75;
      color: var(--text-secondary);
      margin-bottom: 14px;
    }

    .briefing-hint {
      font-size: 11px;
      color: var(--text-muted);
      margin: -6px 0 11px;
    }

    .priority-list { display: flex; flex-direction: column; gap: 8px; }

    .priority-row {
      display: flex;
      align-items: flex-start;
      gap: 9px;
      padding: 10px 12px;
      border-radius: 9px;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      font-size: 12.5px;
      line-height: 1.6;
      color: var(--text-secondary);
      min-width: 0;
    }

    /* 우선 조치 행은 실제 링크다 — 키보드 Tab/Enter 로 열 수 있고 카드로 이동한다. */
    a.priority-row {
      text-decoration: none;
      cursor: pointer;
      transition: background-color 0.15s ease, border-color 0.15s ease;
    }

    a.priority-row:hover {
      background: var(--bg-subtle);
      border-color: var(--border-strong);
    }

    a.priority-row:focus-visible {
      outline: 2px solid var(--accent-primary);
      outline-offset: 2px;
    }

    .priority-row .row-title {
      flex: 1 1 auto;
      min-width: 0;
      overflow-wrap: anywhere;
    }

    .priority-row .row-go {
      flex-shrink: 0;
      font-size: 14px;
      line-height: 1.4;
      color: var(--text-muted);
    }

    .priority-row .cve-mini {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
    }

    .priority-row .due {
      margin-left: auto;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--sev-high-text);
      white-space: nowrap;
    }

    .priority-row .due-over { color: var(--sev-critical-text); }
    .priority-row .due-today { color: var(--sev-high-text); }

    /* KEV · EPSS 지표 읽는 법 (접이식 안내) */
    .glossary { margin-bottom: 18px; }

    .glossary-box {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      box-shadow: var(--card-shadow);
    }

    .glossary-summary {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 11px 16px;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
      list-style: none;
      user-select: none;
      border-radius: 12px;
    }

    .glossary-summary::-webkit-details-marker { display: none; }

    .glossary-summary::before {
      content: "";
      width: 6px;
      height: 6px;
      border-right: 1.6px solid var(--text-muted);
      border-bottom: 1.6px solid var(--text-muted);
      transform: rotate(45deg);
      transition: transform 0.15s ease;
      flex-shrink: 0;
      margin-top: -2px;
    }

    .glossary-box[open] .glossary-summary::before {
      transform: rotate(225deg);
      margin-top: 2px;
    }

    .glossary-summary:focus-visible {
      outline: 2px solid var(--accent-primary);
      outline-offset: -2px;
    }

    .glossary-summary .glossary-hint {
      margin-left: auto;
      font-size: 11px;
      font-weight: 500;
      color: var(--text-muted);
    }

    .glossary-body {
      padding: 0 16px 15px;
      border-top: 1px solid var(--border-subtle);
    }

    .glossary-item { padding-top: 12px; }

    .glossary-term {
      font-size: 12.5px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
    }

    .glossary-term span {
      margin-left: 5px;
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0;
      color: var(--text-muted);
    }

    .glossary-body p {
      font-size: 12.5px;
      line-height: 1.7;
      color: var(--text-secondary);
    }

    .glossary-body b { color: var(--text-primary); font-weight: 600; }

    /* Toolbar */
    .toolbar {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .search-box { position: relative; display: flex; align-items: center; }

    .search-icon {
      position: absolute;
      left: 13px;
      color: var(--text-muted);
      pointer-events: none;
    }

    .search-input {
      width: 100%;
      padding: 10px 36px 10px 38px;
      border-radius: 9px;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      color: var(--text-primary);
      font-family: inherit;
      font-size: 13.5px;
      transition: all 0.15s ease;
    }

    .search-input::placeholder { color: var(--text-muted); }

    .search-input:focus {
      outline: none;
      border-color: var(--accent-primary);
      background: var(--bg-surface);
      box-shadow: 0 0 0 3px var(--accent-subtle);
    }

    .clear-search-btn {
      position: absolute;
      right: 10px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 13px;
      padding: 4px 6px;
      border-radius: 5px;
      display: none;
      line-height: 1;
    }

    .clear-search-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .clear-search-btn.visible { display: block; }

    .segmented-control {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }

    .segmented-control::-webkit-scrollbar { display: none; }

    .segment-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 8px;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      user-select: none;
    }

    .segment-btn:hover {
      background: var(--bg-subtle);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }

    .segment-btn.active {
      background: var(--text-primary);
      color: var(--bg-surface);
      border-color: var(--text-primary);
      font-weight: 600;
    }

    .segment-btn .count {
      font-size: 10.5px;
      font-weight: 600;
      padding: 1px 6px;
      border-radius: 10px;
      background: rgba(148, 163, 184, 0.2);
    }

    .segment-btn.active .count { background: rgba(255, 255, 255, 0.22); }

    /* Result meta */
    .result-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      row-gap: 4px;
      gap: 10px;
      font-size: 12.5px;
      color: var(--text-muted);
      margin-bottom: 12px;
      padding: 0 2px;
    }

    .result-meta strong { color: var(--text-primary); font-weight: 600; }

    .meta-tools { display: flex; align-items: center; gap: 8px; }

    .sort-select {
      font-family: inherit;
      font-size: 12.5px;
      color: var(--text-secondary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 8px;
      padding: 5px 8px;
      cursor: pointer;
    }

    .sort-select:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .reset-btn {
      border: none;
      background: transparent;
      color: var(--accent-primary);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      padding: 2px 4px;
    }

    /* CVE cards */
    .cve-list { display: flex; flex-direction: column; gap: 14px; }

    .cve-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 18px 18px 14px;
      box-shadow: var(--card-shadow);
      transition: box-shadow 0.18s ease, border-color 0.18s ease;
      min-width: 0;
      /* 우선 조치 행에서 이동할 때 sticky 내비게이션에 가리지 않도록 여백 확보 */
      scroll-margin-top: 80px;
    }

    .cve-card:hover { box-shadow: var(--card-shadow-hover); border-color: var(--border-strong); }

    /* 프로그램매틱 포커스(tabindex="-1")는 테두리 대신 하이라이트로 알린다 */
    .cve-card:focus { outline: none; }

    .cve-card.is-focused {
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 3px var(--accent-subtle), var(--card-shadow-hover);
    }

    .cve-top {
      display: flex;
      align-items: center;
      gap: 7px;
      flex-wrap: wrap;
      margin-bottom: 9px;
    }

    .cve-id {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12.5px;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: var(--text-primary);
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      border-radius: 5px;
      padding: 3px 7px;
      white-space: nowrap;
    }

    .sev-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 5px;
      border: 1px solid transparent;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }

    .sev-critical { background: var(--sev-critical-bg); color: var(--sev-critical-text); border-color: var(--sev-critical-border); }
    .sev-high { background: var(--sev-high-bg); color: var(--sev-high-text); border-color: var(--sev-high-border); }
    .sev-medium { background: var(--sev-medium-bg); color: var(--sev-medium-text); border-color: var(--sev-medium-border); }
    .sev-low, .sev-unknown { background: var(--sev-low-bg); color: var(--sev-low-text); border-color: var(--sev-low-border); }

    .badge-kev {
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 5px;
      background: var(--kev-bg);
      color: var(--kev-text);
      white-space: nowrap;
    }

    .badge-poc {
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 5px;
      background: var(--accent-subtle);
      color: var(--accent-primary);
      border: 1px solid var(--border-default);
      white-space: nowrap;
    }

    /* CISA 경보·보안 매체가 먼저 보도한 취약점 표시 */
    .badge-alert {
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 5px;
      background: var(--sev-critical-bg);
      color: var(--sev-critical-text);
      border: 1px solid var(--sev-critical-border);
      white-space: nowrap;
    }

    .badge-news {
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 5px;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
      white-space: nowrap;
    }

    .alert-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .alert-row a {
      color: var(--text-secondary);
      text-decoration: none;
      border-bottom: 1px solid var(--border-default);
      padding-bottom: 1px;
    }

    .alert-row a:hover { color: var(--text-primary); border-bottom-color: var(--text-primary); }

    .link-host {
      margin-left: 5px;
      font-size: 10.5px;
      font-weight: 500;
      color: var(--text-muted);
      letter-spacing: 0;
    }

    .link-host::before { content: "·"; margin-right: 4px; }

    .priority-row .due-alert {
      color: var(--sev-critical-text);
      border: 1px solid var(--sev-critical-border);
      background: var(--sev-critical-bg);
      border-radius: 5px;
      padding: 1px 6px;
    }

    .priority-row .due-fresh {
      color: var(--text-primary);
      border: 1px solid var(--border-strong);
      background: var(--bg-surface);
      border-radius: 5px;
      padding: 1px 6px;
    }

    .card-date {
      margin-left: auto;
      font-size: 11.5px;
      color: var(--text-muted);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }

    .cve-title {
      font-size: 16px;
      font-weight: 700;
      line-height: 1.45;
      letter-spacing: -0.025em;
      color: var(--text-primary);
      margin-bottom: 8px;
      overflow-wrap: anywhere;
    }

    .cve-metrics {
      display: flex;
      flex-wrap: wrap;
      gap: 6px 14px;
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 10px;
      font-variant-numeric: tabular-nums;
    }

    .cve-metrics b { color: var(--text-secondary); font-weight: 600; }

    .chip-row { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 12px; }

    .chip {
      font-size: 11px;
      font-weight: 500;
      color: var(--tag-text);
      background: var(--tag-bg);
      border: 1px solid var(--tag-border);
      border-radius: 5px;
      padding: 3px 7px;
      max-width: 100%;
      overflow-wrap: anywhere;
    }

    .cve-summary {
      font-size: 13.5px;
      line-height: 1.72;
      color: var(--text-secondary);
      margin-bottom: 12px;
      overflow-wrap: anywhere;
    }

    .detail-box {
      border-radius: 9px;
      padding: 11px 13px;
      margin-bottom: 10px;
    }

    .detail-box p {
      font-size: 12.5px;
      line-height: 1.7;
      color: var(--text-secondary);
      overflow-wrap: anywhere;
    }

    .box-label {
      display: block;
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.02em;
      color: var(--text-muted);
      margin-bottom: 5px;
    }

    .impact-box { background: var(--impact-bg); border: 1px solid var(--border-default); }

    .remed-box { background: var(--remed-bg); border: 1px solid var(--remed-border); }

    .poc-block {
      border-top: 1px solid var(--border-subtle);
      padding-top: 11px;
      margin-bottom: 4px;
    }

    .poc-item {
      display: flex;
      align-items: baseline;
      gap: 8px;
      font-size: 12.5px;
      line-height: 1.6;
      padding: 3px 0;
      min-width: 0;
    }

    .poc-item a {
      color: var(--accent-primary);
      text-decoration: none;
      font-weight: 600;
      overflow-wrap: anywhere;
      min-width: 0;
    }

    .poc-item a:hover { text-decoration: underline; }

    .poc-stars {
      flex-shrink: 0;
      font-size: 11px;
      color: var(--text-muted);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }

    .poc-desc {
      display: block;
      font-size: 11.5px;
      color: var(--text-muted);
      line-height: 1.55;
      overflow-wrap: anywhere;
    }

    .cve-foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
      border-top: 1px solid var(--border-subtle);
      margin-top: 11px;
      padding-top: 11px;
    }

    .ref-links { display: flex; flex-wrap: wrap; gap: 5px 10px; font-size: 11.5px; min-width: 0; }

    .ref-links a {
      color: var(--text-muted);
      text-decoration: none;
      border-bottom: 1px solid var(--border-default);
      padding-bottom: 1px;
      overflow-wrap: anywhere;
    }

    .ref-links a:hover { color: var(--accent-primary); border-color: var(--accent-primary); }

    .copy-btn {
      flex-shrink: 0;
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 7px;
      padding: 6px 11px;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .copy-btn:hover {
      color: var(--text-primary);
      background: var(--bg-subtle);
      border-color: var(--border-strong);
    }

    .copy-btn.copied {
      color: var(--accent-primary);
      border-color: var(--accent-primary);
      background: var(--accent-subtle);
    }

    /* ===== 저장(북마크) · 읽음(확인 완료) 표시 — 브라우저 localStorage 개인화 ===== */
    .card-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 11px;
    }

    .mark-btn {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 9px;
      border-radius: 7px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-muted);
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      line-height: 1.4;
      cursor: pointer;
      transition: color 150ms ease, border-color 150ms ease, background-color 150ms ease;
    }

    .mark-btn:hover { color: var(--text-primary); border-color: var(--border-strong); }
    .mark-btn.is-on { color: var(--accent-primary); border-color: var(--accent-primary); background: var(--accent-subtle); }
    .mark-btn svg { width: 12px; height: 12px; flex-shrink: 0; }
    .mark-btn:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .cve-card.is-saved { border-color: var(--accent-primary); }
    .cve-card.is-read .cve-title { color: var(--text-secondary); }
    .cve-card.is-read .cve-summary { color: var(--text-muted); }

    .read-badge {
      font-size: 10.5px;
      font-weight: 700;
      color: var(--text-muted);
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      padding: 3px 7px;
      border-radius: 5px;
      white-space: nowrap;
    }

    .collection-summary {
      font-size: 12px;
      color: var(--text-muted);
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }

    /* Empty state */
    .empty-state {
      display: none;
      text-align: center;
      padding: 60px 20px;
      color: var(--text-muted);
      font-size: 13.5px;
      background: var(--bg-surface);
      border: 1px dashed var(--border-strong);
      border-radius: 14px;
    }

    .empty-state.visible { display: block; }

    /* Toast */
    .toast {
      position: fixed;
      left: 50%;
      bottom: 26px;
      transform: translate(-50%, 12px);
      background: var(--text-primary);
      color: var(--bg-surface);
      font-size: 13px;
      font-weight: 600;
      padding: 10px 16px;
      border-radius: 9px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.18s ease, transform 0.18s ease;
      z-index: 100;
      max-width: calc(100vw - 32px);
    }

    .toast.show { opacity: 1; transform: translate(-50%, 0); }

    /* Footer */
    .footer {
      margin-top: 36px;
      padding-top: 18px;
      border-top: 1px solid var(--border-default);
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.8;
    }

    /* ===== 2차 UI/UX: PC 좌측 필터 레일 · 모바일 필터 바텀 시트 ===== */
    .cve-overview {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 20px;
    }
    .cve-overview-copy { min-width: 0; }
    .cve-overview .hero-pill { margin-bottom: 10px; }
    .cve-overview .hero-title { margin-bottom: 6px; }
    .cve-overview .hero-desc { margin-bottom: 0; }

    .cve-kpis { display: flex; gap: 8px; flex: 0 0 auto; }
    .cve-kpi {
      min-width: 104px;
      padding: 9px 12px 10px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      box-shadow: var(--card-shadow);
    }
    .cve-kpi-label { display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 2px; white-space: nowrap; }
    .cve-kpi-value { font-size: 19px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .cve-kpi-unit { font-size: 11px; font-weight: 600; color: var(--text-muted); margin-left: 2px; }
    .cve-kpi.is-urgent .cve-kpi-value { color: #dc2626; }

    .cve-layout {
      display: grid;
      grid-template-columns: 268px minmax(0, 1fr);
      gap: 24px;
      align-items: start;
    }
    .cve-main { min-width: 0; }

    .cve-rail {
      position: sticky;
      top: 76px;
      display: flex;
      flex-direction: column;
      gap: 15px;
      padding: 16px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      max-height: calc(100vh - 96px);
      overflow-y: auto;
    }
    .cve-rail-head { display: none; }
    .cve-rail-section { display: flex; flex-direction: column; gap: 8px; }
    .cve-rail-section[hidden] { display: none; }
    .cve-rail-label { font-size: 11.5px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.01em; }
    .cve-rail .segmented-control { flex-wrap: wrap; overflow: visible; gap: 4px; }
    .cve-rail .segment-btn { padding: 6px 9px; font-size: 12px; border-radius: 8px; }
    .cve-rail .segment-btn .count { font-size: 10px; padding: 1px 5px; }
    .cve-rail .filter-pills-scroll { flex-wrap: wrap; overflow: visible; }
    .cve-rail .filter-pill { padding: 5px 9px; font-size: 11.5px; }
    .filter-pills-scroll {
      display: flex;
      align-items: center;
      gap: 4px;
      overflow-x: auto;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
      padding-bottom: 2px;
    }
    .filter-pills-scroll::-webkit-scrollbar { display: none; }
    .filter-pill {
      flex-shrink: 0;
      white-space: nowrap;
      padding: 5px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 500;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      cursor: pointer;
      font-family: inherit;
      transition: background-color 160ms ease, border-color 160ms ease, color 160ms ease;
    }
    .filter-pill .count { margin-left: 4px; font-size: 10.5px; font-weight: 600; color: var(--text-muted); }
    .filter-pill:hover { color: var(--text-primary); border-color: var(--border-strong); }
    .filter-pill.active {
      background: var(--accent-subtle);
      border-color: var(--accent-primary);
      color: var(--accent-primary);
      font-weight: 600;
    }
    .filter-pill.active .count { color: var(--accent-primary); }
    .cve-rail .search-input { padding: 9px 32px 9px 34px; font-size: 13px; }
    .cve-rail .search-icon { left: 11px; }
    .cve-rail .clear-search-btn { right: 8px; }
    .cve-rail .sort-select { width: 100%; }
    .cve-rail-foot { display: flex; flex-direction: column; gap: 6px; padding-top: 2px; }

    .cve-apply-btn {
      display: none;
      align-items: center;
      justify-content: center;
      gap: 6px;
      width: 100%;
      padding: 12px;
      border: 0;
      border-radius: 11px;
      background: var(--accent-primary);
      color: #ffffff;
      font-family: inherit;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 160ms cubic-bezier(0.2, 0.8, 0.2, 1), background-color 160ms ease;
    }
    .cve-apply-btn:active { transform: scale(0.98); }
    .cve-reset-link {
      border: 0;
      border-radius: 8px;
      background: transparent;
      color: var(--text-muted);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      padding: 6px;
      cursor: pointer;
    }
    .cve-reset-link:hover { color: var(--text-primary); }

    .cve-mobile-controls { display: none; }
    .cve-mobile-search { flex: 1 1 auto; min-width: 0; }
    .cve-filter-btn {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      flex: 0 0 auto;
      padding: 9px 12px;
      border-radius: 10px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      cursor: pointer;
      transition: transform 160ms cubic-bezier(0.2, 0.8, 0.2, 1), background-color 160ms ease;
    }
    .cve-filter-btn:active { transform: scale(0.98); }
    .cve-filter-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 9px;
      background: var(--accent-primary);
      color: #ffffff;
      font-size: 10.5px;
      font-weight: 700;
    }
    .cve-filter-badge.is-zero { display: none; }
    .cve-backdrop { display: none; }
    .cve-rail-close { display: none; }
    .briefing-more { display: none; }

    @media (min-width: 1024px) {
      .container { max-width: 1300px; }
    }

    /* Mobile Responsive */
    @media (max-width: 640px) {
      .nav-container { padding: 0 12px; height: 54px; gap: 6px; }
      .brand-name { font-size: 15px; }
      .brand-logo-img { width: 24px; height: 24px; }
      .nav-tabs { margin-left: 6px; gap: 4px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; border-radius: 14px; }
      .update-meta { display: none !important; }
      .nav-actions a.icon-btn { display: none; }
      .container { padding: 16px 12px 60px; }
      .hero { margin-bottom: 16px; }
      .hero-title { font-size: 21px; }
      .hero-desc { font-size: 13px; line-height: 1.55; }
      .hero-stats { gap: 6px; }
      .stat-chip { font-size: 11px; padding: 3px 8px; }
      .briefing { padding: 16px; border-radius: 12px; margin-bottom: 14px; }
      .briefing-text { font-size: 12.5px; line-height: 1.7; }
      .briefing-hint { font-size: 10.5px; margin: -4px 0 9px; }
      .glossary { margin-bottom: 14px; }
      .glossary-summary { padding: 10px 13px; font-size: 12px; }
      .glossary-body { padding: 0 13px 13px; }
      .glossary-body p { font-size: 12px; line-height: 1.65; }
      .priority-row { font-size: 12px; flex-wrap: wrap; }
      .priority-row .due { margin-left: 0; }
      .priority-row .row-go { display: none; }
      .toolbar { padding: 12px; border-radius: 12px; gap: 10px; }
      .search-input { padding: 9px 34px 9px 36px; font-size: 13px; }
      .segment-btn { padding: 6px 10px; font-size: 12px; }
      .segmented-control { flex-wrap: wrap; overflow-x: visible; }
      .cve-list { gap: 12px; }
      .cve-card { padding: 15px 14px 12px; border-radius: 12px; }
      .cve-title { font-size: 15px; }
      .cve-summary { font-size: 13px; }
      .detail-box { padding: 10px 11px; }
      .detail-box p { font-size: 12px; }
      .card-date { margin-left: 0; }
      .cve-foot { align-items: flex-start; }
      .copy-btn { width: 100%; text-align: center; padding: 8px 11px; }
      .result-meta { flex-wrap: wrap; gap: 6px; }
      .meta-tools { gap: 6px; }
      .sort-select { font-size: 12px; padding: 4px 6px; }
    }

    @media (max-width: 560px) {
      .brand-name { display: none; }
    }

    @media (max-width: 430px) {
      .nav-container { padding: 0 10px; height: 52px; gap: 6px; }
      .brand-logo-img { width: 22px; height: 22px; }
      .nav-tabs { margin-left: 2px; gap: 2px; }
      .nav-tab-item { padding: 4px 6px; font-size: 10.5px; border-radius: 12px; letter-spacing: -0.03em; }
      .nav-actions .icon-btn { width: 30px; height: 30px; }
    }

    /* 내비게이션 8탭(피싱 레이더 추가) 대응: 넘침 없이 한 줄 유지 */
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
      .nav-container { padding: 0 8px; gap: 4px; }
      .nav-tabs { margin-left: 2px; gap: 1px; }
      .nav-tab-item { padding: 4px 5px; font-size: 10px; border-radius: 11px; letter-spacing: -0.045em; }
      .nav-actions { gap: 4px; }
      .nav-actions .icon-btn { width: 28px; height: 28px; }
    }

    /* ===== 2차 UI/UX: 태블릿·모바일 — 필터는 바텀 시트로, 첫 화면은 우선 조치·목록 ===== */
    @media (max-width: 1023px) {
      .cve-overview { flex-direction: column; align-items: stretch; gap: 12px; margin-bottom: 14px; }
      .cve-overview .hero-desc { display: none; }
      .cve-kpis { gap: 6px; overflow-x: auto; scrollbar-width: none; }
      .cve-kpis::-webkit-scrollbar { display: none; }
      .cve-kpi { flex: 1 1 0; min-width: 0; padding: 8px 10px; }
      .cve-kpi-value { font-size: 16px; }
      .cve-kpi-label { font-size: 10.5px; overflow: hidden; text-overflow: ellipsis; }

      .cve-layout { grid-template-columns: minmax(0, 1fr); gap: 0; }
      .cve-mobile-controls { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
      .cve-mobile-controls .sort-select { flex: 0 0 auto; max-width: 112px; }

      .cve-rail {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        top: auto;
        z-index: 90;
        max-height: 86vh;
        overflow-y: auto;
        border-radius: 20px 20px 0 0;
        border-bottom: 0;
        padding: 8px 18px calc(22px + env(safe-area-inset-bottom));
        box-shadow: 0 -18px 40px -22px rgba(15, 23, 42, 0.4);
        transform: translateY(100%);
        visibility: hidden;
        transition: transform 240ms cubic-bezier(0.2, 0.8, 0.2, 1), visibility 0s linear 240ms;
      }
      .cve-rail.is-open {
        transform: translateY(0);
        visibility: visible;
        transition: transform 240ms cubic-bezier(0.2, 0.8, 0.2, 1), visibility 0s;
      }
      .cve-rail-head { display: flex; align-items: center; justify-content: space-between; padding: 8px 0 4px; }
      .cve-rail-head strong { font-size: 16px; font-weight: 700; letter-spacing: -0.03em; }
      .cve-rail-close {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border: 1px solid var(--border-default);
        border-radius: 10px;
        background: var(--bg-page);
        color: var(--text-secondary);
        cursor: pointer;
      }
      .cve-rail-close svg { width: 16px; height: 16px; }
      .cve-rail .segmented-control { flex-wrap: nowrap; overflow-x: auto; }
      .cve-rail .segment-btn { flex: 0 0 auto; }
      .cve-rail .filter-pills-scroll { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 2px; }
      .cve-rail .filter-pill { flex: 0 0 auto; }
      .cve-rail .search-input { font-size: 14px; padding: 10px 36px 10px 36px; }
      .cve-rail-foot { display: flex; }
      .cve-apply-btn { display: inline-flex; }

      .cve-backdrop {
        display: block;
        position: fixed;
        inset: 0;
        z-index: 89;
        background: rgba(15, 23, 42, 0.44);
        opacity: 0;
        transition: opacity 200ms cubic-bezier(0.2, 0.8, 0.2, 1);
      }
      .cve-backdrop.is-open { opacity: 1; }
      .cve-backdrop[hidden] { display: none; }
      body.cve-filter-open { overflow: hidden; }

      /* 우선 조치 행: CVE ID 와 마감 배지를 한 줄에, 제목은 그 아래 전체 폭으로 */
      .priority-row { flex-wrap: wrap; gap: 4px 8px; }
      .priority-row .row-title { order: 3; flex: 1 1 100%; }
      .priority-row .due { order: 2; margin-left: auto; }
      .priority-row .row-go { display: none; }
      .briefing-text { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
      .briefing-text.is-expanded { display: block; -webkit-line-clamp: unset; overflow: visible; }
      .briefing-more {
        display: inline-flex;
        align-items: center;
        margin: -6px 0 10px;
        padding: 2px 0;
        border: 0;
        background: transparent;
        color: var(--accent-primary);
        font-family: inherit;
        font-size: 11.5px;
        font-weight: 600;
        cursor: pointer;
      }    }

    @media (max-width: 380px) {
      .briefing-head { flex-wrap: nowrap; gap: 8px; }
      .briefing-title { white-space: nowrap; }
      .briefing-time { display: none; }
    }
"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · CVE 취약점 리포트</title>
  <meta name="description" content="CISA KEV(실제 악용 취약점)·CIRCL·NVD 최신 CVE를 모아 CVSS·EPSS 위험도, 영향 제품, 한국어 원인 분석, 조치 방안, 공개 PoC 경로까지 한 화면에서 확인하는 취약점 리포트입니다.">
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
          <a href="cve.html" class="nav-tab-item active">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
          <a href="radar.html" class="nav-tab-item">피싱 레이더</a>
          <a href="pick.html" class="nav-tab-item">오늘 뭐 먹지</a>
          <a href="clue.html" class="nav-tab-item">3단서 추리</a>
          <a href="mission.html" class="nav-tab-item">퇴근길 미션</a>
          <a href="chart.html" class="nav-tab-item">차트 추리실</a>
        </div>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>__UPDATED_AT__ 기준</span>
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

    <!-- Overview · KPI -->
    <section class="cve-overview">
      <div class="cve-overview-copy">
        <span class="hero-pill">VULNERABILITY REPORT</span>
        <h1 class="hero-title">CVE 취약점 리포트</h1>
        <p class="hero-desc">CISA가 실제 공격 악용을 확인한 KEV 목록과 최신 CVE를 함께 모읍니다. CVSS·EPSS 위험도, 영향 제품, 한국어 원인 분석, 바로 적용할 수 있는 조치 방안, 공개 PoC 경로를 한 카드에서 확인하고 보고용 마크다운으로 복사할 수 있습니다.</p>
      </div>
      <div class="cve-kpis">
        <div class="cve-kpi">
          <span class="cve-kpi-label">전체 CVE</span>
          <strong class="cve-kpi-value">__TOTAL__</strong><span class="cve-kpi-unit">건</span>
        </div>
        <div class="cve-kpi is-urgent">
          <span class="cve-kpi-label">긴급 · KEV</span>
          <strong class="cve-kpi-value">__KEV__</strong><span class="cve-kpi-unit">건</span>
        </div>
        <div class="cve-kpi">
          <span class="cve-kpi-label">우선 조치</span>
          <strong class="cve-kpi-value">__PRIORITY_COUNT__</strong><span class="cve-kpi-unit">건</span>
        </div>
        <div class="cve-kpi">
          <span class="cve-kpi-label">공개 PoC</span>
          <strong class="cve-kpi-value">__POC__</strong><span class="cve-kpi-unit">건</span>
        </div>
      </div>
    </section>

    <div class="cve-layout">
      <!-- 필터: PC 좌측 고정 레일 / 모바일 바텀 시트 -->
      <aside class="cve-rail" id="cveRail" aria-label="CVE 필터">
        <div class="cve-rail-head">
          <strong>필터</strong>
          <button type="button" class="cve-rail-close" id="cveRailClose" aria-label="필터 닫기">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg>
          </button>
        </div>

        <div class="cve-rail-section" id="cveRailSearchSection">
          <p class="cve-rail-label">검색</p>
          <div class="search-box" id="cveSearchBox">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" id="searchInput" class="search-input" placeholder="CVE ID, 별칭, 제품명, 키워드 검색">
            <button id="clearSearch" class="clear-search-btn" aria-label="검색 지우기">✕</button>
          </div>
        </div>

        <div class="cve-rail-section">
          <p class="cve-rail-label">심각도</p>
          <div class="segmented-control" id="filterNav">
            <button class="segment-btn active" data-filter="all">전체 <span class="count">__TOTAL__</span></button>
            <button class="segment-btn" data-filter="critical">Critical <span class="count">__CRITICAL__</span></button>
            <button class="segment-btn" data-filter="high">High <span class="count">__HIGH__</span></button>
            <button class="segment-btn" data-filter="medium">Medium <span class="count">__MEDIUM__</span></button>
          </div>
        </div>

        <div class="cve-rail-section">
          <p class="cve-rail-label">악용 신호</p>
          <div class="segmented-control" id="signalNav">
            <button class="segment-btn" data-filter="kev">KEV 실제 악용 <span class="count">__KEV__</span></button>
            <button class="segment-btn" data-filter="poc">PoC 공개 <span class="count">__POC__</span></button>
            <button class="segment-btn" data-filter="alert">경보·보도 <span class="count">__ALERT__</span></button>
          </div>
        </div>

        <div class="cve-rail-section">
          <p class="cve-rail-label">내 목록</p>
          <div class="filter-pills-scroll" id="collectionNav">
            <button type="button" class="filter-pill" data-collection="saved" aria-pressed="false">저장한 항목만<span class="count" id="cveSavedCount">0</span></button>
            <button type="button" class="filter-pill" data-collection="unread" aria-pressed="false">안 읽은 항목만<span class="count" id="cveUnreadCount">0</span></button>
          </div>
        </div>

        <div class="cve-rail-section">
          <p class="cve-rail-label">출처</p>
          <div class="filter-pills-scroll" id="sourceNav">
            <button class="filter-pill active" data-src="all">전체</button>
            <button class="filter-pill" data-src="cisa">CISA <span class="count">__SRC_CISA__</span></button>
            <button class="filter-pill" data-src="kisa">KISA <span class="count">__SRC_KISA__</span></button>
            <button class="filter-pill" data-src="vendor">보안기업 <span class="count">__SRC_VENDOR__</span></button>
          </div>
        </div>

        <div class="cve-rail-section">
          <p class="cve-rail-label">정렬</p>
          <select class="sort-select" id="sortSelect" aria-label="정렬 기준">
            <option value="published" selected>최신 공개순</option>
            <option value="cvss">위험도 높은순</option>
            <option value="kev">KEV 실제 악용순</option>
          </select>
        </div>

        <div class="cve-rail-foot">
          <button type="button" class="cve-apply-btn" id="cveApplyBtn">결과 보기 <span id="cveApplyCount"></span></button>
          <button type="button" class="cve-reset-link" id="resetFilters">필터 초기화</button>
        </div>
      </aside>

      <section class="cve-main">
        <div class="cve-mobile-controls">
          <div class="cve-mobile-search" id="cveMobileSearchSlot"></div>
          <select class="sort-select" id="cveSortMobile" aria-label="정렬 기준">
            <option value="published" selected>최신 공개순</option>
            <option value="cvss">위험도 높은순</option>
            <option value="kev">KEV 실제 악용순</option>
          </select>
          <button type="button" class="cve-filter-btn" id="cveFilterOpenBtn" aria-expanded="false" aria-controls="cveRail">
            필터<span class="cve-filter-badge is-zero" id="cveFilterBadge">0</span>
          </button>
        </div>

        <!-- 우선 조치 -->
        <section class="briefing">
          <div class="briefing-head">
            <div class="briefing-title"><span class="bar"></span>이번 주 우선 조치</div>
            <span class="briefing-time">__COLLECTED_AT__ 수집</span>
          </div>
          <p class="briefing-text" id="briefingText">__BRIEFING__</p>
          <button type="button" class="briefing-more" id="briefingMore" aria-expanded="false" aria-controls="briefingText">요약 더 보기</button>
          <p class="briefing-hint">항목을 누르거나 Tab으로 옮겨 Enter를 누르면 해당 CVE 카드로 이동합니다.</p>
          <div class="priority-list">
            __PRIORITY_ROWS__
          </div>
        </section>

        <!-- KEV · EPSS 지표 안내 (접이식) -->
        <section class="glossary" aria-label="KEV·EPSS 지표 안내">
          <details class="glossary-box">
            <summary class="glossary-summary">KEV · EPSS 지표 읽는 법<span class="glossary-hint">점수 해석 기준</span></summary>
            <div class="glossary-body">
              <div class="glossary-item">
                <div class="glossary-term">CISA KEV<span>Known Exploited Vulnerabilities</span></div>
                <p>미국 CISA가 <b>실제 공격에 악용된 것이 확인된</b> 취약점 목록입니다. KEV 배지는 이론적인 위험이 아니라 이미 공격에 쓰이고 있다는 뜻입니다. 등재 항목의 조치 기한은 <b>CISA BOD 22-01에 따른 미국 연방 민간 행정부 기관 대상 의무 기한</b>이며, 일반 기업·기관에는 법적 의무가 아니라 패치 우선순위를 정할 때 참고하는 지표입니다. 노출된 자산이 있다면 그 기한을 목표 시점으로 삼아 패치·완화 조치를 서두르는 것이 좋습니다.</p>
              </div>
              <div class="glossary-item">
                <div class="glossary-term">EPSS<span>Exploit Prediction Scoring System · FIRST</span></div>
                <p>공개된 취약점이 <b>향후 30일 안에 실제로 악용될 확률</b>을 0~100%로 추정한 점수입니다(매일 갱신). 점수는 확률일 뿐이라 “몇 %부터 위험하다”는 공통 임계값은 없습니다. FIRST도 각 조직이 자산 중요도·인터넷 노출·위험 허용도에 맞춰 조치 기준을 정하도록 안내합니다. 아래 10% 이상·1% 미만 같은 구간은 운영 예시일 뿐 절대 기준이 아니므로, KEV·CVSS·인터넷 노출 여부와 함께 판단하세요. ‘악용 위험 상위 N%’는 같은 날 전체 CVE 중 이 항목의 추정 순위를 뜻합니다.</p>
              </div>
              <div class="glossary-item">
                <div class="glossary-term">CVSS<span>Common Vulnerability Scoring System</span></div>
                <p>취약점 자체의 심각도를 0~10으로 나타낸 점수입니다. 9.0 이상이 Critical(치명적), 7.0~8.9가 High(높음)입니다. 악용 여부(KEV)나 악용 확률(EPSS)과는 다른 축이므로 두 지표와 함께 읽습니다.</p>
              </div>
            </div>
          </details>
        </section>

        <div class="result-meta">
          <span class="result-count"><strong id="visibleCount">__TOTAL__</strong>건 표시 중 · 전체 __TOTAL__건</span>
          <span class="collection-summary" id="cveCollectionSummary">저장 0 · 안 읽음 __TOTAL__</span>
          <div class="meta-tools">
            <button class="reset-btn" id="resetFiltersMeta">필터 초기화</button>
          </div>
        </div>

        <section class="cve-list" id="cveList"></section>
        <div class="empty-state" id="emptyState">조건에 맞는 CVE가 없습니다. 다른 키워드나 필터로 다시 찾아보세요.</div>
      </section>
    </div>

    <div class="cve-backdrop" id="cveBackdrop" hidden></div>

    <div class="toast" id="toast">리포트를 클립보드에 복사했습니다.</div>

    <footer class="footer">
      Infosec Archive · CVE 취약점 리포트<br>
      수집 소스: CISA KEV · CISA 경보·권고 · KISA 보호나라 · MSRC · Google Cloud TI · Unit 42 · Qualys · Rapid7 · Sophos · Wiz · CIRCL CVE · NVD · FIRST EPSS · GitHub 공개 PoC · 보안 뉴스<br>
      요약·원인·조치 방안은 수집 원문을 바탕으로 AI가 한국어로 정리한 것이며, 실제 적용 전 벤더 공지와 원문을 함께 확인하세요.
    </footer>
  </main>

  <script>
    const CVE_ITEMS = __ITEMS_JSON__;
    const CVE_META = __META_JSON__;

    // ---- Theme (index.html / study.html / ai.html 과 동일한 secjobs-theme 동기화) ----
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');

    function setTheme(theme) {
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'block';
        localStorage.setItem('secjobs-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
        if (moonIcon) moonIcon.style.display = 'block';
        if (sunIcon) sunIcon.style.display = 'none';
        localStorage.setItem('secjobs-theme', 'light');
      }
    }

    (function initTheme() {
      const saved = localStorage.getItem('secjobs-theme');
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) setTheme('dark');
      else setTheme('light');
    })();

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    // ---- Helpers ----
    const SEV_KO = { CRITICAL: '치명적', HIGH: '높음', MEDIUM: '보통', LOW: '낮음', UNKNOWN: '미평가' };

    function escapeHtml(str) {
      return String(str == null ? '' : str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // 수집된 링크는 URL 파서로 검증해 http/https/mailto 만 통과시킨다
    // (javascript:, data:, vbscript:, 프로토콜 상대 //, 제어문자 삽입 차단).
    function safeUrl(u) {
      const raw = String(u == null ? '' : u).trim();
      if (!raw || /[\\u0000-\\u001F\\u007F<>"'`\\\\]/.test(raw)) return '#';
      let parsed;
      try { parsed = new URL(raw); } catch (e) { return '#'; }
      const proto = parsed.protocol.toLowerCase();
      return (proto === 'http:' || proto === 'https:' || proto === 'mailto:') ? parsed.href : '#';
    }

    // 외부 링크 카드 옆에 실제 이동 도메인을 표시해 피싱 링크를 눈으로 걸러낸다.
    function linkHost(u) {
      let parsed;
      try { parsed = new URL(String(u == null ? '' : u).trim()); } catch (e) { return ''; }
      const proto = parsed.protocol.toLowerCase();
      if (proto === 'mailto:') {
        const parts = String(parsed.pathname || '').split('@');
        return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
      }
      if (proto !== 'http:' && proto !== 'https:') return '';
      return parsed.hostname.replace(/^www\\./, '').toLowerCase();
    }

    // 링크 텍스트 옆에 실제 이동 도메인을 붙인다(피싱 도메인 육안 식별).
    function hostLabel(u) {
      const h = linkHost(u);
      return h ? '<span class="link-host">' + escapeHtml(h) + '</span>' : '';
    }

    function formatDate(d) {
      if (!d) return '';
      const parts = String(d).slice(0, 10).split('-');
      return parts.length === 3 ? parts.join('.') : String(d);
    }

    function sevClass(sev) {
      const s = String(sev || 'UNKNOWN').toLowerCase();
      return ['critical', 'high', 'medium', 'low'].includes(s) ? s : 'unknown';
    }

    function cvssText(it) {
      return (it.cvss_score == null) ? 'CVSS 미평가' : ('CVSS ' + Number(it.cvss_score).toFixed(1) + ' · ' + (SEV_KO[it.severity] || '미평가'));
    }

    function epssText(it) {
      if (it.epss_score == null) return '';
      let t = 'EPSS ' + (it.epss_score * 100).toFixed(1) + '%';
      if (it.epss_percentile != null) t += ' · 악용 위험 상위 ' + Math.max(1, Math.round((1 - it.epss_percentile) * 100)) + '%';
      return t;
    }

    // ---- State ----
    let activeFilter = 'all';
    let activeSource = 'all';
    let searchTerm = '';
    let onlySaved = false;
    let onlyUnread = false;

    // ===== 저장(북마크) · 읽음(확인 완료) 표시 =====
    // 저장 위치는 이 브라우저의 localStorage 뿐이고 서버로는 아무것도 보내지 않는다.
    // 저장한 CVE ID는 화면을 그릴 때 다시 마크업으로 해석되지 않고, 정해진 버튼 상태로만 쓴다.
    const SAVED_KEY = 'cve_saved_v1';
    const READ_KEY = 'cve_read_v1';
    const MARK_ID_RE = /^[A-Za-z0-9_.:-]{1,80}$/;
    const markStore = { saved: readMarkStore(SAVED_KEY), read: readMarkStore(READ_KEY) };

    function readMarkStore(key) {
      const clean = {};
      try {
        const raw = localStorage.getItem(key);
        const parsed = raw ? JSON.parse(raw) : null;
        if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return clean;
        Object.keys(parsed).forEach(function (id) {
          if (MARK_ID_RE.test(id)) clean[id] = 1;
        });
      } catch (e) {}
      return clean;
    }

    function persistMark(kind) {
      try {
        localStorage.setItem(kind === 'saved' ? SAVED_KEY : READ_KEY, JSON.stringify(markStore[kind]));
      } catch (e) {}
    }

    // ---- 재렌더 뒤 키보드 포커스 복원 ----
    // 저장·읽음 토글이 목록을 다시 그리면 포커스가 body 로 떨어져 키보드로 연속 조작할 수 없다.
    // 토글 직전의 CVE ID·동작 종류·목록 위치를 기억했다가 같은 위치의 같은 버튼으로 되돌린다.
    function markButtonFor(key, kind) {
      if (!key) return null;
      return list.querySelector('.cve-card[data-key="' + key + '"] [data-mark="' + kind + '"]');
    }

    function captureMarkFocus() {
      const active = document.activeElement;
      const btn = active && active.closest ? active.closest('[data-mark]') : null;
      if (!btn || !list.contains(btn)) return null;
      const card = btn.closest('.cve-card');
      const keys = sortItems(CVE_ITEMS.filter(matches)).map(function (it) { return it.cve_id; });
      const key = card ? card.getAttribute('data-key') : null;
      const index = key ? keys.indexOf(key) : -1;
      return {
        kind: btn.getAttribute('data-mark'),
        id: btn.getAttribute('data-id'),
        index: index >= 0 ? index : 0,
      };
    }

    function restoreMarkFocus(pending) {
      if (!pending) return;
      const keys = sortItems(CVE_ITEMS.filter(matches)).map(function (it) { return it.cve_id; });
      let target = keys.indexOf(pending.id) !== -1 ? markButtonFor(pending.id, pending.kind) : null;
      if (!target && keys.length) {
        // 카드가 필터로 빠졌으면 같은 자리(다음 카드)로, 마지막 카드였으면 이전 카드로 간다.
        const at = Math.min(pending.index, keys.length - 1);
        target = markButtonFor(keys[at], pending.kind) || markButtonFor(keys[keys.length - 1], pending.kind);
      }
      if (!target) {
        // 남은 카드가 0건이면 켜져 있는 필터 칩(모바일 시트처럼 숨김 상태면 보이는 '필터 초기화')으로 보낸다.
        focusFirstAvailable([
          document.querySelector('#collectionNav .filter-pill[aria-pressed="true"]'),
          document.getElementById('resetFilters'),
          document.getElementById('resetFiltersMeta'),
          document.getElementById('cveFilterOpenBtn'),
        ]);
        return;
      }
      target.focus({ preventScroll: true });
    }

    // 숨김(visibility:hidden · 시트 닫힘 · inert) 요소는 focus() 가 무시되므로,
    // 실제로 포커스가 옮겨간 첫 요소에서 멈춘다.
    function focusFirstAvailable(elements) {
      for (let i = 0; i < elements.length; i += 1) {
        const el = elements[i];
        if (!el) continue;
        el.focus({ preventScroll: true });
        if (document.activeElement === el) return el;
      }
      return null;
    }

    function toggleMark(kind, id) {
      if (!id || !MARK_ID_RE.test(id) || !markStore[kind]) return;
      const pending = captureMarkFocus();
      if (markStore[kind][id]) delete markStore[kind][id];
      else markStore[kind][id] = 1;
      persistMark(kind);
      render();
      restoreMarkFocus(pending);
    }

    function savedCount() {
      return CVE_ITEMS.filter(function (it) { return !!markStore.saved[it.cve_id]; }).length;
    }

    function unreadCount() {
      return CVE_ITEMS.filter(function (it) { return !markStore.read[it.cve_id]; }).length;
    }

    function updateMarkCounts() {
      const savedEl = document.getElementById('cveSavedCount');
      if (savedEl) savedEl.textContent = String(savedCount());
      const unreadEl = document.getElementById('cveUnreadCount');
      if (unreadEl) unreadEl.textContent = String(unreadCount());
      const summary = document.getElementById('cveCollectionSummary');
      if (summary) summary.textContent = '저장 ' + savedCount() + ' · 안 읽음 ' + unreadCount();
    }

    const MARK_ICONS = {
      saved: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6.5 4.5h11a1 1 0 0 1 1 1v14l-6.5-4.2-6.5 4.2v-14a1 1 0 0 1 1-1z"></path></svg>',
      read: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.5 12.5l4.5 4.5 10-10"></path></svg>'
    };

    // CISA·KISA·보안기업 피드로 출처를 묶는다(카드의 경보·보도 줄과 같은 기준).
    const VENDOR_SOURCES = ['Microsoft MSRC', 'Google Cloud Threat Intelligence', 'Palo Alto Unit 42',
      'Qualys Blog', 'Rapid7 Blog', 'Sophos News', 'Wiz Blog'];

    function sourceMatches(it, src) {
      if (src === 'all') return true;
      const alerts = it.alerts || [];
      if (src === 'cisa') return alerts.some(a => String(a.source || '').indexOf('CISA') === 0);
      if (src === 'kisa') return alerts.some(a => String(a.source || '').indexOf('KISA') === 0);
      if (src === 'vendor') return alerts.some(a => VENDOR_SOURCES.indexOf(a.source) !== -1);
      return true;
    }

    const list = document.getElementById('cveList');
    const emptyState = document.getElementById('emptyState');
    const visibleCount = document.getElementById('visibleCount');
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const clearSearchBtn = document.getElementById('clearSearch');
    const toast = document.getElementById('toast');
    let toastTimer = null;

    function matches(it) {
      if (onlySaved && !markStore.saved[it.cve_id]) return false;
      if (onlyUnread && markStore.read[it.cve_id]) return false;
      if (activeFilter === 'kev' && !it.is_kev) return false;
      if (activeFilter === 'poc' && !(it.poc_links && it.poc_links.length)) return false;
      if (activeFilter === 'alert' && !(it.alerts && it.alerts.length)) return false;
      if (activeFilter === 'critical' && it.severity !== 'CRITICAL') return false;
      if (activeFilter === 'high' && it.severity !== 'HIGH') return false;
      if (activeFilter === 'medium' && it.severity !== 'MEDIUM') return false;
      if (!sourceMatches(it, activeSource)) return false;
      if (searchTerm) {
        const hay = [it.cve_id, it.title_ko, it.summary_ko, it.impact_ko, it.remediation_ko,
                     it.vendor, it.product, (it.affected_products || []).join(' '),
                     (it.cwe || []).join(' '), (it.poc_links || []).map(p => p.name).join(' '),
                     (it.alerts || []).map(a => (a.title || '') + ' ' + (a.source || '')).join(' ')]
                    .join(' ').toLowerCase();
        if (!hay.includes(searchTerm)) return false;
      }
      return true;
    }

    function renderCard(it) {
      const sev = sevClass(it.severity);
      const top = [];
      top.push('<span class="cve-id">' + escapeHtml(it.cve_id) + '</span>');
      top.push('<span class="sev-badge sev-' + sev + '">' + escapeHtml(cvssText(it)) + '</span>');
      if (it.alerts && it.alerts.length) {
        const isCisaAlert = (it.alerts || []).some(a => (a.source || '').indexOf('CISA Alert') === 0);
        top.push(isCisaAlert
          ? '<span class="badge-alert">CISA 경보</span>'
          : '<span class="badge-news">경보·보도</span>');
      }
      if (it.is_kev) top.push('<span class="badge-kev" title="CISA가 실제 공격 악용을 확인한 취약점">KEV 실제 악용</span>');
      if (it.poc_links && it.poc_links.length) top.push('<span class="badge-poc">PoC ' + it.poc_links.length + '건</span>');
      if (it.published_at) top.push('<span class="card-date">' + escapeHtml(formatDate(it.published_at)) + ' 공개</span>');

      const metrics = [];
      const ep = epssText(it);
      if (ep) metrics.push('<span title="FIRST EPSS: 향후 30일 내 실제 악용될 확률 추정치"><b>' + escapeHtml(ep) + '</b></span>');
      if (it.kev_due_date) metrics.push('<span>조치 기한 <b>' + escapeHtml(formatDate(it.kev_due_date)) + '</b></span>');
      if (it.cwe && it.cwe.length) metrics.push('<span>' + escapeHtml(it.cwe.join(' · ')) + '</span>');

      const alertRow = (it.alerts && it.alerts.length)
        ? '<div class="alert-row"><span>경보·보도</span>' + (it.alerts || []).slice(0, 3).map(a =>
            '<a href="' + safeUrl(a.url) + '" target="_blank" rel="noopener noreferrer" title="원문: ' + escapeHtml(a.url) + '">' +
            escapeHtml(a.source || '원문') + (a.published_at ? ' ' + escapeHtml(formatDate(a.published_at)) : '') + hostLabel(a.url) + '</a>'
          ).join('') + '</div>'
        : '';

      const chips = (it.affected_products || []).slice(0, 4)
        .map(p => '<span class="chip">' + escapeHtml(p) + '</span>').join('');

      const pocs = (it.poc_links || []).map(p => {
        const label = escapeHtml(p.name || p.url);
        return '<div class="poc-item"><a href="' + safeUrl(p.url) + '" target="_blank" rel="noopener noreferrer" title="원문: ' + escapeHtml(p.url) + '">' + label + hostLabel(p.url) + '</a>'
          + '<span class="poc-stars">스타 ' + (p.stars || 0) + '</span></div>'
          + (p.description ? '<span class="poc-desc">' + escapeHtml(p.description) + '</span>' : '');
      }).join('');

      const refs = (it.references || []).slice(0, 3).map(r => {
        const url = typeof r === 'string' ? r : (r && r.url);
        if (!url) return '';
        const host = linkHost(url) || '원문';
        return '<a href="' + safeUrl(url) + '" target="_blank" rel="noopener noreferrer" title="원문: ' + escapeHtml(url) + '">' + escapeHtml(host) + '</a>';
      }).join('');

      const markKey = escapeHtml(it.cve_id);
      const isSaved = !!markStore.saved[it.cve_id];
      const isRead = !!markStore.read[it.cve_id];
      const actions = '<div class="card-actions">'
        + '<button type="button" class="mark-btn ' + (isSaved ? 'is-on' : '') + '" data-mark="saved" data-id="' + markKey + '" aria-pressed="' + (isSaved ? 'true' : 'false') + '" title="' + (isSaved ? '저장 해제' : '저장') + '">' + MARK_ICONS.saved + (isSaved ? '저장됨' : '저장') + '</button>'
        + '<button type="button" class="mark-btn ' + (isRead ? 'is-on' : '') + '" data-mark="read" data-id="' + markKey + '" aria-pressed="' + (isRead ? 'true' : 'false') + '" title="' + (isRead ? '읽음 취소' : '읽음 표시') + '">' + MARK_ICONS.read + (isRead ? '읽음' : '읽음 표시') + '</button>'
        + '</div>';

      return '<article class="cve-card' + (isSaved ? ' is-saved' : '') + (isRead ? ' is-read' : '') + '" id="cve-' + escapeHtml(it.cve_id) + '" data-key="' + markKey + '" tabindex="-1">'
        + '<div class="cve-top">' + top.join('') + (isRead ? '<span class="read-badge">읽음</span>' : '') + '</div>'
        + '<h2 class="cve-title">' + escapeHtml(it.title_ko) + '</h2>'
        + (metrics.length ? '<div class="cve-metrics">' + metrics.join('') + '</div>' : '')
        + alertRow
        + (chips ? '<div class="chip-row">' + chips + '</div>' : '')
        + '<p class="cve-summary">' + escapeHtml(it.summary_ko) + '</p>'
        + (it.impact_ko ? '<div class="detail-box impact-box"><span class="box-label">원인 및 영향 범위</span><p>' + escapeHtml(it.impact_ko) + '</p></div>' : '')
        + (it.remediation_ko ? '<div class="detail-box remed-box"><span class="box-label">조치 방안</span><p>' + escapeHtml(it.remediation_ko) + '</p></div>' : '')
        + (pocs ? '<div class="poc-block"><span class="box-label">공개 PoC 경로</span>' + pocs + '</div>' : '')
        + actions
        + '<div class="cve-foot">'
        +   '<div class="ref-links">' + (refs || '<a href="https://nvd.nist.gov/vuln/detail/' + escapeHtml(it.cve_id) + '" target="_blank" rel="noopener noreferrer">NVD 상세</a>') + '</div>'
        +   '<button class="copy-btn" data-cve="' + escapeHtml(it.cve_id) + '">리포트 복사</button>'
        + '</div>'
        + '</article>';
    }

    // ---- 정렬 (기본: 최신 공개순) ----
    let currentSort = 'published';

    function pubStamp(it) {
      const s = (it.published_at || '').replace(/[^0-9]/g, '');
      return s ? parseInt(s, 10) : 0;
    }

    function sortItems(arr) {
      const copy = arr.slice();
      if (currentSort === 'cvss') {
        copy.sort((a, b) => ((b.cvss_score || 0) - (a.cvss_score || 0))
          || (pubStamp(b) - pubStamp(a))
          || ((b.is_kev ? 1 : 0) - (a.is_kev ? 1 : 0)));
      } else if (currentSort === 'kev') {
        copy.sort((a, b) => ((b.is_kev ? 1 : 0) - (a.is_kev ? 1 : 0))
          || (pubStamp(b) - pubStamp(a))
          || ((b.cvss_score || 0) - (a.cvss_score || 0)));
      } else {
        // 기본값은 서버가 정한 순서(최근 공개일 → 경보·KEV → 위험도)를 그대로 살린다.
        // 배열 정렬은 안정 정렬이므로 공개일만 비교해도 같은 날짜 안의 보조 순서가 유지된다.
        copy.sort((a, b) => (pubStamp(b) - pubStamp(a)));
      }
      return copy;
    }

    function render() {
      const visible = sortItems(CVE_ITEMS.filter(matches));
      list.innerHTML = visible.map(renderCard).join('');
      visibleCount.textContent = visible.length;
      emptyState.classList.toggle('visible', visible.length === 0);
      updateFilterBadge();
      updateMarkCounts();
    }

    // 카드의 저장·읽음 버튼 (목록을 다시 그리므로 이벤트는 위임으로 받는다)
    list.addEventListener('click', (ev) => {
      const markBtn = ev.target.closest('[data-mark]');
      if (!markBtn) return;
      ev.preventDefault();
      toggleMark(markBtn.getAttribute('data-mark'), markBtn.getAttribute('data-id'));
    });

    // ---- 우선 조치 행 → 해당 CVE 카드로 이동 ----
    let jumpTimer = null;

    function resetFiltersForJump() {
      searchInput.value = '';
      searchTerm = '';
      clearSearchBtn.classList.remove('visible');
      activeFilter = 'all';
      activeSource = 'all';
      onlySaved = false;
      onlyUnread = false;
      document.querySelectorAll('.segment-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-filter') === 'all');
      });
      document.querySelectorAll('#sourceNav .filter-pill').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-src') === 'all');
      });
      document.querySelectorAll('#collectionNav .filter-pill').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      render();
    }

    // 검색어·필터로 카드가 숨겨져 있어도 조건을 풀고 다시 그린 뒤
    // 정확히 그 카드로 스크롤하고 포커스를 옮긴다.
    function jumpToCard(cid) {
      const id = String(cid == null ? '' : cid).trim();
      if (!id) return;
      if (railOpen || (rail && rail.classList.contains('is-open'))) closeRailSheet();
      resetFiltersForJump();
      const card = document.getElementById('cve-' + id);
      if (!card) {
        showToast('해당 CVE 카드를 찾지 못했습니다.');
        return;
      }
      card.focus({ preventScroll: true });
      card.scrollIntoView({ behavior: 'smooth', block: 'start' });
      card.classList.add('is-focused');
      clearTimeout(jumpTimer);
      jumpTimer = setTimeout(() => card.classList.remove('is-focused'), 2400);
      try { history.replaceState(null, '', '#cve-' + encodeURIComponent(id)); } catch (e) {}
    }

    // ---- Markdown report ----
    function buildMarkdown(it) {
      const L = [];
      L.push('# ' + it.cve_id + ' — ' + it.title_ko);
      L.push('');
      L.push('- CVSS: ' + (it.cvss_score == null ? '미평가' : Number(it.cvss_score).toFixed(1) + ' (' + (SEV_KO[it.severity] || '미평가') + ')'));
      const ep = epssText(it);
      if (ep) L.push('- ' + ep);
      if (it.is_kev) {
        let k = '- CISA KEV: 실제 악용 확인';
        if (it.kev_date_added) k += ' (등재 ' + formatDate(it.kev_date_added);
        if (it.kev_due_date) k += (it.kev_date_added ? ', ' : ' (') + '조치 기한 ' + formatDate(it.kev_due_date);
        if (it.kev_date_added) k += ')';
        L.push(k);
      }
      if (it.affected_products && it.affected_products.length) L.push('- 영향 제품: ' + it.affected_products.join(' / '));
      if (it.cwe && it.cwe.length) L.push('- CWE: ' + it.cwe.join(', '));
      if (it.published_at) L.push('- 공개일: ' + formatDate(it.published_at));
      L.push('');
      L.push('## 개요');
      L.push(it.summary_ko || '-');
      if (it.impact_ko) { L.push(''); L.push('## 원인 및 영향 범위'); L.push(it.impact_ko); }
      if (it.remediation_ko) { L.push(''); L.push('## 조치 방안'); L.push(it.remediation_ko); }
      if (it.poc_links && it.poc_links.length) {
        L.push(''); L.push('## 공개 PoC');
        it.poc_links.forEach(p => L.push('- [' + (p.name || p.url) + '](' + p.url + ') — 스타 ' + (p.stars || 0)));
      }
      L.push(''); L.push('## 참고 링크');
      L.push('- NVD: https://nvd.nist.gov/vuln/detail/' + it.cve_id);
      (it.references || []).slice(0, 4).forEach(r => {
        const url = typeof r === 'string' ? r : (r && r.url);
        if (url && url.indexOf('https://nvd.nist.gov/vuln/detail/' + it.cve_id) === -1) L.push('- ' + url);
      });
      L.push('');
      L.push('> 출처: Infosec Archive CVE 리포트 (' + CVE_META.collected_at + ' 수집)');
      return L.join('\\n');
    }

    function showToast(msg) {
      toast.textContent = msg;
      toast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
    }

    function fallbackCopy(text) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.top = '-1000px';
      document.body.appendChild(ta);
      ta.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      return ok;
    }

    list.addEventListener('click', (ev) => {
      const btn = ev.target.closest('.copy-btn');
      if (!btn) return;
      const it = CVE_ITEMS.find(x => x.cve_id === btn.getAttribute('data-cve'));
      if (!it) return;
      const md = buildMarkdown(it);
      const done = () => {
        btn.classList.add('copied');
        btn.textContent = '복사 완료';
        showToast('리포트를 클립보드에 복사했습니다.');
        setTimeout(() => { btn.classList.remove('copied'); btn.textContent = '리포트 복사'; }, 2200);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(md).then(done).catch(() => {
          if (fallbackCopy(md)) done();
          else showToast('복사에 실패했습니다. 다시 시도해 주세요.');
        });
      } else if (fallbackCopy(md)) {
        done();
      } else {
        showToast('복사에 실패했습니다. 다시 시도해 주세요.');
      }
    });

    // ---- 우선 조치 행 링크 (이벤트 위임: 인라인 on* 금지 규칙 준수) ----
    const priorityList = document.querySelector('.priority-list');
    if (priorityList) {
      priorityList.addEventListener('click', (ev) => {
        const row = ev.target.closest('a.priority-row');
        if (!row) return;
        ev.preventDefault();
        jumpToCard(row.getAttribute('data-cve'));
      });
    }

    // ---- Filters (레일·시트 공통 이벤트 위임) ----
    const rail = document.getElementById('cveRail');
    if (rail) {
      rail.addEventListener('click', (ev) => {
        const segBtn = ev.target.closest('.segment-btn');
        if (segBtn) {
          document.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
          segBtn.classList.add('active');
          activeFilter = segBtn.getAttribute('data-filter');
          render();
          return;
        }
        const colBtn = ev.target.closest('#collectionNav .filter-pill');
        if (colBtn) {
          const kind = colBtn.getAttribute('data-collection');
          const on = kind === 'saved' ? !onlySaved : !onlyUnread;
          if (kind === 'saved') onlySaved = on;
          else if (kind === 'unread') onlyUnread = on;
          colBtn.classList.toggle('active', on);
          colBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
          render();
          return;
        }
        const srcBtn = ev.target.closest('#sourceNav .filter-pill');
        if (srcBtn) {
          document.querySelectorAll('#sourceNav .filter-pill').forEach(b => b.classList.remove('active'));
          srcBtn.classList.add('active');
          activeSource = srcBtn.getAttribute('data-src');
          render();
        }
      });
    }

    searchInput.addEventListener('input', () => {
      searchTerm = searchInput.value.trim().toLowerCase();
      clearSearchBtn.classList.toggle('visible', !!searchTerm);
      render();
    });

    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      searchTerm = '';
      clearSearchBtn.classList.remove('visible');
      render();
      searchInput.focus();
    });

    function resetAllFilters() {
      searchInput.value = '';
      searchTerm = '';
      clearSearchBtn.classList.remove('visible');
      activeFilter = 'all';
      activeSource = 'all';
      onlySaved = false;
      onlyUnread = false;
      currentSort = 'published';
      sortSelect.value = 'published';
      if (cveSortMobile) cveSortMobile.value = 'published';
      document.querySelectorAll('.segment-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-filter') === 'all'));
      document.querySelectorAll('#sourceNav .filter-pill').forEach(b => b.classList.toggle('active', b.getAttribute('data-src') === 'all'));
      document.querySelectorAll('#collectionNav .filter-pill').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      render();
    }

    document.getElementById('resetFilters').addEventListener('click', resetAllFilters);
    const resetFiltersMeta = document.getElementById('resetFiltersMeta');
    if (resetFiltersMeta) resetFiltersMeta.addEventListener('click', resetAllFilters);

    sortSelect.addEventListener('change', () => {
      currentSort = sortSelect.value;
      if (cveSortMobile) cveSortMobile.value = currentSort;
      render();
    });

    // ---- 모바일 필터 시트 · 적용 개수 배지 ----
    const cveSortMobile = document.getElementById('cveSortMobile');
    const railCloseBtn = document.getElementById('cveRailClose');
    const filterOpenBtn = document.getElementById('cveFilterOpenBtn');
    const backdrop = document.getElementById('cveBackdrop');
    const applyBtn = document.getElementById('cveApplyBtn');
    let railOpenRaf = null;   // is-open 을 붙이려고 예약한 프레임(열기→같은 프레임 닫기 경합 차단)
    let railOpen = false;

    function activeFilterCount() {
      let n = 0;
      if (activeFilter !== 'all') n += 1;
      if (activeSource !== 'all') n += 1;
      if (onlySaved) n += 1;
      if (onlyUnread) n += 1;
      if (searchTerm) n += 1;
      return n;
    }

    function updateFilterBadge() {
      const badge = document.getElementById('cveFilterBadge');
      if (badge) {
        const n = activeFilterCount();
        badge.textContent = n;
        badge.classList.toggle('is-zero', n === 0);
      }
      const applyCount = document.getElementById('cveApplyCount');
      if (applyCount) {
        const el = document.getElementById('visibleCount');
        applyCount.textContent = el ? '(' + el.textContent + ')' : '';
      }
    }

    function cancelRailFrame() {
      if (railOpenRaf !== null) {
        window.cancelAnimationFrame(railOpenRaf);
        railOpenRaf = null;
      }
    }

    function openRailSheet() {
      if (!rail || !backdrop) return;
      railOpen = true;
      backdrop.hidden = false;
      document.body.classList.add('cve-filter-open');
      if (filterOpenBtn) filterOpenBtn.setAttribute('aria-expanded', 'true');
      cancelRailFrame();
      railOpenRaf = window.requestAnimationFrame(function () {
        railOpenRaf = window.requestAnimationFrame(function () {
          railOpenRaf = null;
          if (!railOpen) return;
          rail.classList.add('is-open');
          backdrop.classList.add('is-open');
          if (railCloseBtn) railCloseBtn.focus();
        });
      });
    }

    function closeRailSheet() {
      if (!rail || !backdrop) return;
      railOpen = false;
      cancelRailFrame();
      rail.classList.remove('is-open');
      backdrop.classList.remove('is-open');
      document.body.classList.remove('cve-filter-open');
      if (filterOpenBtn) {
        filterOpenBtn.setAttribute('aria-expanded', 'false');
        filterOpenBtn.focus();
      }
      window.setTimeout(function () { backdrop.hidden = true; }, 220);
    }

    if (filterOpenBtn) {
      filterOpenBtn.addEventListener('click', function () {
        if (railOpen || (rail && rail.classList.contains('is-open'))) closeRailSheet();
        else openRailSheet();
      });
    }
    if (railCloseBtn) railCloseBtn.addEventListener('click', closeRailSheet);
    if (applyBtn) applyBtn.addEventListener('click', closeRailSheet);
    if (backdrop) backdrop.addEventListener('click', closeRailSheet);

    if (cveSortMobile) {
      cveSortMobile.addEventListener('change', function () {
        sortSelect.value = cveSortMobile.value;
        currentSort = cveSortMobile.value;
        render();
      });
    }

    window.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && (railOpen || (rail && rail.classList.contains('is-open')))) closeRailSheet();
    });

    // 검색창은 PC에서는 좌측 레일, 모바일에서는 목록 상단에 놓인다(같은 입력 요소를 옮긴다).
    const searchBox = document.getElementById('cveSearchBox');
    const railSearchSection = document.getElementById('cveRailSearchSection');

    function mountSearch() {
      if (!searchBox || !railSearchSection) return;
      const mobile = window.innerWidth < 1024;
      const slot = document.getElementById(mobile ? 'cveMobileSearchSlot' : 'cveRailSearchSection');
      if (slot && searchBox.parentNode !== slot) slot.appendChild(searchBox);
      railSearchSection.hidden = mobile;
    }

    mountSearch();

    let mountTimer = null;
    window.addEventListener('resize', function () {
      window.clearTimeout(mountTimer);
      mountTimer = window.setTimeout(function () {
        mountSearch();
        if (window.innerWidth >= 1024 && rail && rail.classList.contains('is-open')) closeRailSheet();
      }, 120);
    });

    // 모바일에서 긴 우선 조치 요약은 4줄까지만 보이고 펼쳐 볼 수 있다.
    const briefingMore = document.getElementById('briefingMore');
    const briefingText = document.getElementById('briefingText');
    if (briefingMore && briefingText) {
      briefingMore.addEventListener('click', function () {
        const expanded = briefingText.classList.toggle('is-expanded');
        briefingMore.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        briefingMore.textContent = expanded ? '요약 접기' : '요약 더 보기';
      });
    }

    render();

    // 공유된 #cve-... 링크로 들어온 경우에도 카드가 그려진 뒤 해당 카드로 이동한다.
    (function openHashTargetOnLoad() {
      const raw = String(location.hash || '').replace(/^#/, '');
      if (raw.indexOf('cve-') !== 0) return;
      let cid = raw.slice(4);
      try { cid = decodeURIComponent(cid); } catch (e) {}
      setTimeout(() => jumpToCard(cid), 80);
    })();
  </script>
</body>
</html>
"""


# 경보·보도 소스 라벨 — '이번 주 우선 조치' 배지에 그대로 쓰인다
ALERT_SOURCE_LABELS = {
    "CISA Alert": "CISA 경보",
    "CISA ICS Advisory": "CISA ICS 권고",
    "KISA 취약점 정보": "KISA 경보",
}
# 보안기업·연구조직 피드 (KISA·CISA 경보와 함께 '신규 고위험' 판정 근거로 쓴다)
VENDOR_ALERT_SOURCES = {
    "Microsoft MSRC",
    "Google Cloud Threat Intelligence",
    "Palo Alto Unit 42",
    "Qualys Blog",
    "Rapid7 Blog",
    "Sophos News",
    "Wiz Blog",
}
ALERT_WEIGHTS = {"CISA Alert": 15, "KISA 취약점 정보": 12, "CISA ICS Advisory": 6}
VENDOR_SOURCE_LABELS = {
    "Microsoft MSRC": "MSRC",
    "Google Cloud Threat Intelligence": "Google Cloud TI",
    "Palo Alto Unit 42": "Unit 42",
    "Qualys Blog": "Qualys",
    "Rapid7 Blog": "Rapid7",
    "Sophos News": "Sophos",
    "Wiz Blog": "Wiz",
}


def build_briefing(items):
    """'이번 주 우선 조치' 요약 문장과 행(최대 7건)을 만든다.

    행 선정 순서
      ① 오늘~7일 내 마감 KEV — 마감일 → CVSS 순 (이번 주 마감이 먼저)
      ② CISA 경보·KISA·주요 보안기업이 포착한 KEV 미등재 고위험 취약점
         (CVSS ≥ 9.0 또는 공개 PoC ≥ 2, 최근 보도 가중)
      ③ 최근 기한 경과 KEV — 가장 최근 것 1건
    같은 CVE가 두 번 나오지 않도록 seen 집합으로 막는다.
    """
    if not items:
        return ("아직 수집된 CVE가 없습니다. cve_crawler.py 실행 후 다시 빌드하세요.", [])

    MAX_ROWS = 7
    today = datetime.now(KST).date()
    week_end = today + timedelta(days=6 - today.weekday())  # 이번 주 일요일

    def due_date(i):
        try:
            return datetime.strptime((i.get("kev_due_date") or "")[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    def cvss(i):
        try:
            return float(i.get("cvss_score") or 0)
        except (TypeError, ValueError):
            return 0.0

    def poc_n(i):
        try:
            n = int(i.get("poc_count") or 0)
        except (TypeError, ValueError):
            n = 0
        return max(n, len(i.get("poc_links") or []))

    def alert_sources(i):
        return [(a.get("source") or "").strip() for a in (i.get("alerts") or [])]

    def md(d):
        return f"{d.month}/{d.day}"

    kev_items = [i for i in items if i.get("is_kev")]
    poc_items = [i for i in items if i.get("poc_links")]
    crit = sum(1 for i in items if i.get("severity") == "CRITICAL")
    high = sum(1 for i in items if i.get("severity") == "HIGH")

    dated = [i for i in kev_items if due_date(i)]
    overdue = sorted([i for i in dated if due_date(i) < today],
                     key=lambda i: (due_date(i), -cvss(i)), reverse=True)
    this_week = sorted([i for i in dated if today <= due_date(i) <= week_end],
                       key=lambda i: (due_date(i), -cvss(i), i["cve_id"]))
    within7 = sorted([i for i in dated if today <= due_date(i) <= today + timedelta(days=7)],
                     key=lambda i: (due_date(i), -cvss(i), i["cve_id"]))

    def is_fresh_high_risk(i):
        """KEV 등재 전이지만 경보·보안기업 피드가 먼저 잡은 고위험 취약점."""
        if i.get("is_kev"):
            return False
        srcs = set(alert_sources(i))
        if not (srcs & (set(ALERT_SOURCE_LABELS) | VENDOR_ALERT_SOURCES)):
            return False
        return cvss(i) >= 9.0 or poc_n(i) >= 2

    def fresh_score(i):
        """독립 보도처 수 · PoC 수 · CVSS · 발표 최신성 · 경보 등급을 합산한 우선순위."""
        srcs = set(alert_sources(i))
        score = 7.0 * len(srcs)                       # 여러 곳이 독립적으로 다룰수록 파급이 크다
        score += 3 * poc_n(i) + 2 * cvss(i)
        score += sum(ALERT_WEIGHTS.get(s, 0) for s in srcs)
        latest = max([(a.get("published_at") or "") for a in (i.get("alerts") or [])] or [""])
        try:
            age = (today - datetime.strptime(latest[:10], "%Y-%m-%d").date()).days
        except ValueError:
            age = 30
        score += 8 if age <= 2 else (4 if age <= 7 else 0)
        return score

    fresh = sorted([i for i in items if is_fresh_high_risk(i)],
                   key=lambda i: (-fresh_score(i), i["cve_id"]))

    def deadline_badge(i):
        d = due_date(i)
        if not d:
            return esc("KEV 등재"), "due"
        delta = (d - today).days
        if delta < 0:
            return esc(f"기한 경과 {-delta}일 ({d.isoformat()})"), "due due-over"
        if delta == 0:
            return esc(f"오늘 마감 ({d.isoformat()})"), "due due-today"
        return esc(f"D-{delta} ({d.isoformat()})"), "due"

    def fresh_badge(i):
        srcs = alert_sources(i)
        tag = next((ALERT_SOURCE_LABELS[s] for s in srcs if s in ALERT_SOURCE_LABELS), "")
        stats = []
        if cvss(i) >= 9.0:
            stats.append(f"CVSS {cvss(i):.1f}")
        if poc_n(i):
            stats.append(f"PoC {poc_n(i)}건")
        parts = ([tag] if tag else []) + stats
        if len(parts) > 2:  # 배지가 길어지면 CVSS 를 덜어낸다 (경보 · PoC 우선)
            parts = [tag] + [p for p in stats if p.startswith("PoC")]
        if not parts:
            vendors = [VENDOR_SOURCE_LABELS[s] for s in srcs if s in VENDOR_SOURCE_LABELS]
            parts = [vendors[0] if vendors else "보도"]
        return esc(" · ".join(parts)), ("due due-alert" if tag else "due due-fresh")

    rows = []
    seen = set()

    def add_row(it, badge, cls):
        cid = it["cve_id"]
        if cid in seen:  # 같은 CVE 중복 행 차단
            return False
        seen.add(cid)
        title = re.sub(r"\s*\(?\s*" + re.escape(cid) + r"\s*\)?\s*$", "", it.get("title_ko", "")).strip()
        rows.append(
            f'<a class="priority-row" href="#cve-{esc(cid)}" data-cve="{esc(cid)}"'
            f' aria-label="{esc(cid)} 카드로 이동">'
            f'<span class="cve-mini">{esc(cid)}</span>'
            f'<span class="row-title">{esc(title)}</span>'
            f'<span class="{cls}">{badge}</span>'
            '<span class="row-go" aria-hidden="true">›</span>'
            "</a>"
        )
        return True

    # ① 이번 주 마감 KEV → ② 신규 고위험 → ③ 최근 기한 경과 KEV 순으로 채운다
    picks = ([("kev", i) for i in within7[:4]]
             + [("fresh", i) for i in fresh[:3]]
             + [("over", i) for i in overdue[:1]])
    while len(picks) > MAX_ROWS:  # 예산 초과 시 신규 고위험 꼬리부터 줄인다
        idx = max((n for n, (kind, _) in enumerate(picks) if kind == "fresh"), default=len(picks) - 1)
        picks.pop(idx)
    for kind, it in picks:
        if kind == "fresh":
            badge, cls = fresh_badge(it)
        else:
            badge, cls = deadline_badge(it)
        add_row(it, badge, cls)
    # 자리가 남으면 다음 순번으로 채운다 (이번 주 마감 → 신규 고위험 → 경과)
    for it in within7[4:] + fresh[3:] + overdue[1:]:
        if len(rows) >= MAX_ROWS:
            break
        badge, cls = deadline_badge(it) if it.get("is_kev") else fresh_badge(it)
        add_row(it, badge, cls)
    if not rows:
        for it in kev_items[:3]:
            add_row(it, deadline_badge(it)[0], deadline_badge(it)[1])
    if not rows:
        rows.append('<div class="priority-row"><span>현재 KEV 등재 항목이 없습니다. 아래 목록에서 위험도가 높은 항목부터 확인하세요.</span></div>')

    parts = []
    if kev_items:
        parts.append(f"최근 수집된 CVE {len(items)}건 중 {len(kev_items)}건이 CISA KEV에 등재된 실제 악용 취약점입니다.")
    else:
        parts.append(f"최근 수집된 CVE {len(items)}건 가운데 CISA KEV 등재 항목은 아직 없습니다.")

    if within7:
        nearest_day = due_date(within7[0])
        nearest = [i for i in within7 if due_date(i) == nearest_day]
        ids = ", ".join(i["cve_id"] for i in nearest)
        parts.append(
            f"이번 주({md(week_end)}까지) 마감 KEV는 {len(this_week)}건,"
            f" 7일 내({md(today + timedelta(days=7))}까지)로는 {len(within7)}건이며,"
            f" 가장 급한 {md(nearest_day)} 마감 {len(nearest)}건({ids})은 오늘 안에 패치 적용 여부를 확인해야 합니다."
        )
    elif kev_items:
        parts.append("이번 주 마감으로 잡힌 KEV는 없습니다. 아래 목록에서 위험도가 높은 항목부터 확인하세요.")

    if overdue:
        latest = overdue[0]
        parts.append(
            f"기한이 지난 KEV도 {len(overdue)}건(가장 최근 {latest['kev_due_date']} 마감 {latest['cve_id']}) 있습니다."
        )

    if fresh:
        top_fresh = fresh[:2]
        top_srcs = [s for i in top_fresh for s in alert_sources(i)]
        vendors = []
        for s in top_srcs:
            lbl = VENDOR_SOURCE_LABELS.get(s)
            if lbl and lbl not in vendors:
                vendors.append(lbl)
        who = []
        if "CISA Alert" in top_srcs:
            who.append("CISA 경보")
        if any(s.startswith("KISA") for s in top_srcs):
            who.append("KISA 취약점 정보")
        if vendors:
            who.append("보안기업(" + "·".join(vendors[:3]) + (" 등" if len(vendors) > 3 else "") + ")")
        desc = []
        for i in top_fresh:
            alias = (i.get("title_ko") or "").split(" — ")[0].strip()
            stats = [x for x in (f"CVSS {cvss(i):.1f}" if cvss(i) else "",
                                 f"PoC {poc_n(i)}건" if poc_n(i) else "") if x]
            desc.append(f"{alias}({i['cve_id']}{', ' + ' · '.join(stats) if stats else ''})")
        parts.append(
            f"KEV 등재 전 고위험 취약점도 {'·'.join(who) or '보안 매체'}에서 집중 보도됐습니다 — "
            + ", ".join(desc)
            + ". 해당 제품을 운영 중이라면 노출 여부와 벤더 패치를 먼저 확인하세요."
        )

    if crit or high or poc_items:
        parts.append(f"CVSS 기준 Critical {crit}건, High {high}건이며, 공개 PoC가 확인된 항목은 {len(poc_items)}건입니다.")

    return " ".join(parts), rows


def attach_alerts(items, days=30):
    """CISA 경보·보안 매체 단서를 항목에 붙이고, 목록은 **최근 공개일 순**으로 정렬한다.

    (요청: '최근 공개 날짜가 가장 상단'. 같은 날짜 안에서만 CISA Alert > Advisory > 일반 순을
     보조 기준으로 쓰고, 그 다음 위험도(CVSS) → 원래 순서를 따른다.)
    """
    alerts_map = get_cve_alerts(days=days)
    for it in items:
        rows = alerts_map.get(it.get("cve_id")) or []
        if rows:
            it["alerts"] = rows
    alert_ids = {cid for cid, rows in alerts_map.items() if rows}

    def pub_key(it):
        """최신 공개일을 내림차순으로 만들기 위한 음수 스탬프(값이 클수록 앞)."""
        raw = (it.get("published_at") or "").replace("-", "")
        try:
            return int(raw)
        except ValueError:
            return 0

    def alert_key(it):
        if it.get("cve_id") not in alert_ids or not it.get("alerts"):
            return 2
        is_alert = any((a.get("source") or "").startswith("CISA Alert") for a in it["alerts"])
        return 0 if is_alert else 1

    def rank(pair):
        idx, it = pair
        return (-pub_key(it), alert_key(it), -(it.get("cvss_score") or 0), idx)

    return [it for _, it in sorted(enumerate(items), key=rank)]


def build():
    init_db()
    fixed, still_empty = normalize_cve_published_dates()
    if fixed:
        print(f"  [CVE] 공개일 {fixed}건 ISO(YYYY-MM-DD) 정규화")
    if still_empty:
        print(f"  [CVE] 공개일 미확인 {len(still_empty)}건 (목록 맨 아래로 정렬): {', '.join(still_empty[:6])}")
    items = attach_alerts(get_cve_reports())
    stats = get_cve_stats()
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    updated_at = now.strftime("%Y-%m-%d %H:%M KST")

    briefing, rows = build_briefing(items)
    collected = ""
    if items:
        collected = max((i.get("updated_at") or "") for i in items) or updated_at

    # 2차 UI: 레일·KPI에 쓰는 파생 지표(심각도 Medium, 경보·보도, 우선 조치 행 수, 출처별 건수)
    medium = sum(1 for i in items if (i.get("severity") or "").upper() == "MEDIUM")
    alert_count = sum(1 for i in items if i.get("alerts"))
    priority_count = sum(1 for row in rows if "data-cve=" in row)

    def _has_source(it, prefix):
        return any(str(a.get("source") or "").startswith(prefix) for a in (it.get("alerts") or []))

    src_cisa = sum(1 for i in items if _has_source(i, "CISA"))
    src_kisa = sum(1 for i in items if _has_source(i, "KISA"))
    src_vendor = sum(
        1 for i in items
        if any((a.get("source") or "") in VENDOR_ALERT_SOURCES for a in (i.get("alerts") or []))
    )

    meta = {
        "total": stats["total"],
        "critical": stats["critical"],
        "high": stats["high"],
        "kev": stats["kev"],
        "poc": stats["poc"],
        "collected_at": collected,
        "built_at": updated_at,
        "sources": [
            "CISA KEV", "CISA 경보", "CISA ICS 권고", "CIRCL CVE", "NVD", "FIRST EPSS",
            "GitHub 공개 PoC", "KISA 보호나라", "MSRC", "Google Cloud TI", "Sophos",
            "Qualys", "Wiz", "Unit 42", "Rapid7", "보안 뉴스",
        ],
    }

    with open(CVE_DATA_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "items": items}, f, ensure_ascii=False, indent=2)

    # 화면에는 한국어 정리본만 싣는다 (영문 원문·CISA 원문 권고는 데이터 파일에만 보관)
    ui_items = []
    for it in items:
        ui = dict(it)
        ui.pop("description_orig", None)
        ui.pop("kev_required_action", None)
        ui_items.append(ui)

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__ITEMS_JSON__", safe_json_for_script(json.dumps(ui_items, ensure_ascii=False)))
    html = html.replace("__META_JSON__", safe_json_for_script(json.dumps(meta, ensure_ascii=False)))
    html = html.replace("__UPDATED_AT__", esc(updated_at))
    html = html.replace("__COLLECTED_AT__", esc(collected or updated_at))
    html = html.replace("__BRIEFING__", esc(briefing))
    html = html.replace("__PRIORITY_ROWS__", "\n        ".join(rows))
    html = html.replace("__TOTAL__", str(stats["total"]))
    html = html.replace("__CRITICAL__", str(stats["critical"]))
    html = html.replace("__HIGH__", str(stats["high"]))
    html = html.replace("__KEV__", str(stats["kev"]))
    html = html.replace("__POC__", str(stats["poc"]))
    html = html.replace("__MEDIUM__", str(medium))
    html = html.replace("__ALERT__", str(alert_count))
    html = html.replace("__PRIORITY_COUNT__", str(priority_count))
    html = html.replace("__SRC_CISA__", str(src_cisa))
    html = html.replace("__SRC_KISA__", str(src_kisa))
    html = html.replace("__SRC_VENDOR__", str(src_vendor))

    with open(CVE_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(ui_shell.apply(html, 'cve')))

    print(f"-> 'cve.html' · 'cve_data.json' 생성 완료 (CVE {len(items)}건, KEV {stats['kev']}건, PoC {stats['poc']}건)")
    return len(items)


if __name__ == "__main__":
    build()

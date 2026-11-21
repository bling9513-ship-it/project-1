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
      max-width: 1140px;
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
      gap: 6px;
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
      padding: 5px 12px;
      border-radius: 18px;
      font-size: 12.5px;
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

    <!-- Hero -->
    <section class="hero">
      <span class="hero-pill">VULNERABILITY REPORT</span>
      <h1 class="hero-title">CVE 취약점 리포트</h1>
      <p class="hero-desc">CISA가 실제 공격 악용을 확인한 KEV 목록과 최신 CVE를 함께 모읍니다. CVSS·EPSS 위험도, 영향 제품과 버전, 한국어 원인 분석, 바로 적용할 수 있는 조치 방안, 공개 PoC 경로를 한 카드에서 확인하고 보고용 마크다운으로 복사할 수 있습니다.</p>
      <div class="hero-stats">
        <span class="stat-chip">수집 CVE <strong>__TOTAL__건</strong></span>
        <span class="stat-chip">Critical <strong>__CRITICAL__건</strong></span>
        <span class="stat-chip">High <strong>__HIGH__건</strong></span>
        <span class="stat-chip">CISA KEV <strong>__KEV__건</strong></span>
        <span class="stat-chip">공개 PoC <strong>__POC__건</strong></span>
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

    <!-- 우선 조치 -->
    <section class="briefing">
      <div class="briefing-head">
        <div class="briefing-title"><span class="bar"></span>이번 주 우선 조치</div>
        <span class="briefing-time">__COLLECTED_AT__ 수집</span>
      </div>
      <p class="briefing-text">__BRIEFING__</p>
      <p class="briefing-hint">항목을 누르거나 Tab으로 옮겨 Enter를 누르면 해당 CVE 카드로 이동합니다.</p>
      <div class="priority-list">
        __PRIORITY_ROWS__
      </div>
    </section>

    <!-- Toolbar -->
    <section class="toolbar">
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="searchInput" class="search-input" placeholder="CVE ID, 별칭, 제품명, 키워드로 검색 (예: Java4Shell, CVE-2026-114938, PAN-OS)">
        <button id="clearSearch" class="clear-search-btn" aria-label="검색 지우기">✕</button>
      </div>

      <div class="segmented-control" id="filterNav">
        <button class="segment-btn active" data-filter="all">전체 <span class="count">__TOTAL__</span></button>
        <button class="segment-btn" data-filter="kev">KEV 실제 악용 <span class="count">__KEV__</span></button>
        <button class="segment-btn" data-filter="poc">PoC 공개 <span class="count">__POC__</span></button>
        <button class="segment-btn" data-filter="critical">Critical <span class="count">__CRITICAL__</span></button>
        <button class="segment-btn" data-filter="high">High <span class="count">__HIGH__</span></button>
      </div>
    </section>

    <div class="result-meta">
      <span class="result-count"><strong id="visibleCount">__TOTAL__</strong>건 표시 중 · 전체 __TOTAL__건</span>
      <div class="meta-tools">
        <select class="sort-select" id="sortSelect" aria-label="정렬 기준">
          <option value="published" selected>최신 공개순</option>
          <option value="cvss">위험도 높은순</option>
          <option value="kev">KEV 실제 악용순</option>
        </select>
        <button class="reset-btn" id="resetFilters">필터 초기화</button>
      </div>
    </div>

    <section class="cve-list" id="cveList"></section>
    <div class="empty-state" id="emptyState">조건에 맞는 CVE가 없습니다. 다른 키워드나 필터로 다시 찾아보세요.</div>

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
    let searchTerm = '';

    const list = document.getElementById('cveList');
    const emptyState = document.getElementById('emptyState');
    const visibleCount = document.getElementById('visibleCount');
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const clearSearchBtn = document.getElementById('clearSearch');
    const toast = document.getElementById('toast');
    let toastTimer = null;

    function matches(it) {
      if (activeFilter === 'kev' && !it.is_kev) return false;
      if (activeFilter === 'poc' && !(it.poc_links && it.poc_links.length)) return false;
      if (activeFilter === 'critical' && it.severity !== 'CRITICAL') return false;
      if (activeFilter === 'high' && it.severity !== 'HIGH') return false;
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
          + '<span class="poc-stars">★ ' + (p.stars || 0) + '</span></div>'
          + (p.description ? '<span class="poc-desc">' + escapeHtml(p.description) + '</span>' : '');
      }).join('');

      const refs = (it.references || []).slice(0, 3).map(r => {
        const url = typeof r === 'string' ? r : (r && r.url);
        if (!url) return '';
        const host = linkHost(url) || '원문';
        return '<a href="' + safeUrl(url) + '" target="_blank" rel="noopener noreferrer" title="원문: ' + escapeHtml(url) + '">' + escapeHtml(host) + '</a>';
      }).join('');

      return '<article class="cve-card" id="cve-' + escapeHtml(it.cve_id) + '" tabindex="-1">'
        + '<div class="cve-top">' + top.join('') + '</div>'
        + '<h2 class="cve-title">' + escapeHtml(it.title_ko) + '</h2>'
        + (metrics.length ? '<div class="cve-metrics">' + metrics.join('') + '</div>' : '')
        + alertRow
        + (chips ? '<div class="chip-row">' + chips + '</div>' : '')
        + '<p class="cve-summary">' + escapeHtml(it.summary_ko) + '</p>'
        + (it.impact_ko ? '<div class="detail-box impact-box"><span class="box-label">원인 및 영향 범위</span><p>' + escapeHtml(it.impact_ko) + '</p></div>' : '')
        + (it.remediation_ko ? '<div class="detail-box remed-box"><span class="box-label">조치 방안</span><p>' + escapeHtml(it.remediation_ko) + '</p></div>' : '')
        + (pocs ? '<div class="poc-block"><span class="box-label">공개 PoC 경로</span>' + pocs + '</div>' : '')
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
    }

    // ---- 우선 조치 행 → 해당 CVE 카드로 이동 ----
    let jumpTimer = null;

    function resetFiltersForJump() {
      searchInput.value = '';
      searchTerm = '';
      clearSearchBtn.classList.remove('visible');
      activeFilter = 'all';
      document.querySelectorAll('.segment-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-filter') === 'all');
      });
      render();
    }

    // 검색어·필터로 카드가 숨겨져 있어도 조건을 풀고 다시 그린 뒤
    // 정확히 그 카드로 스크롤하고 포커스를 옮긴다.
    function jumpToCard(cid) {
      const id = String(cid == null ? '' : cid).trim();
      if (!id) return;
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
        it.poc_links.forEach(p => L.push('- [' + (p.name || p.url) + '](' + p.url + ') — ★' + (p.stars || 0)));
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

    // ---- Filters ----
    document.getElementById('filterNav').addEventListener('click', (ev) => {
      const btn = ev.target.closest('.segment-btn');
      if (!btn) return;
      document.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.getAttribute('data-filter');
      render();
    });

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

    document.getElementById('resetFilters').addEventListener('click', () => {
      searchInput.value = '';
      searchTerm = '';
      clearSearchBtn.classList.remove('visible');
      activeFilter = 'all';
      currentSort = 'published';
      sortSelect.value = 'published';
      document.querySelectorAll('.segment-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-filter') === 'all'));
      render();
    });

    sortSelect.addEventListener('change', () => {
      currentSort = sortSelect.value;
      render();
    });

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

    with open(CVE_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(html))

    print(f"-> 'cve.html' · 'cve_data.json' 생성 완료 (CVE {len(items)}건, KEV {stats['kev']}건, PoC {stats['poc']}건)")
    return len(items)


if __name__ == "__main__":
    build()

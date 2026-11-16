#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_cve_html.py — archive.db 의 cve_reports 테이블을 단일 소스로
CVE 취약점 리포트 페이지(cve.html)와 데이터 파일(cve_data.json)을 빌드한다.
(index.html / study.html / ai.html 과 동일한 secjobs-theme 디자인 시스템)
"""
import os
import json
from datetime import datetime, timezone, timedelta

from db_manager import init_db, get_cve_reports, get_cve_stats

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

    .nav-tabs { display: flex; gap: 6px; margin-left: 10px; }

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
    }

    .cve-card:hover { box-shadow: var(--card-shadow-hover); border-color: var(--border-strong); }

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
      .nav-container { padding: 0 12px; height: 54px; }
      .brand-name { font-size: 15px; }
      .brand-logo-img { width: 24px; height: 24px; }
      .nav-tabs { margin-left: 6px; gap: 4px; }
      .nav-tab-item { padding: 4px 9px; font-size: 11.5px; border-radius: 14px; }
      .update-meta { display: none !important; }
      .container { padding: 16px 12px 60px; }
      .hero { margin-bottom: 16px; }
      .hero-title { font-size: 21px; }
      .hero-desc { font-size: 13px; line-height: 1.55; }
      .hero-stats { gap: 6px; }
      .stat-chip { font-size: 11px; padding: 3px 8px; }
      .briefing { padding: 16px; border-radius: 12px; margin-bottom: 14px; }
      .briefing-text { font-size: 12.5px; line-height: 1.7; }
      .priority-row { font-size: 12px; flex-wrap: wrap; }
      .priority-row .due { margin-left: 0; }
      .toolbar { padding: 12px; border-radius: 12px; gap: 10px; }
      .search-input { padding: 9px 34px 9px 36px; font-size: 13px; }
      .segment-btn { padding: 6px 10px; font-size: 12px; }
      .cve-list { gap: 12px; }
      .cve-card { padding: 15px 14px 12px; border-radius: 12px; }
      .cve-title { font-size: 15px; }
      .cve-summary { font-size: 13px; }
      .detail-box { padding: 10px 11px; }
      .detail-box p { font-size: 12px; }
      .card-date { margin-left: 0; }
      .cve-foot { align-items: flex-start; }
      .copy-btn { width: 100%; text-align: center; padding: 8px 11px; }
    }

    @media (max-width: 480px) {
      .brand-name { display: none; }
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
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
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

    <!-- 우선 조치 -->
    <section class="briefing">
      <div class="briefing-head">
        <div class="briefing-title"><span class="bar"></span>이번 주 우선 조치</div>
        <span class="briefing-time">__COLLECTED_AT__ 수집</span>
      </div>
      <p class="briefing-text">__BRIEFING__</p>
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
        <input type="text" id="searchInput" class="search-input" placeholder="CVE ID, 제품명, 키워드로 검색 (예: CVE-2026, PAN-OS, 원격 코드 실행)">
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
      <span><strong id="visibleCount">__TOTAL__</strong>건 표시 중 · 전체 __TOTAL__건</span>
      <button class="reset-btn" id="resetFilters">필터 초기화</button>
    </div>

    <section class="cve-list" id="cveList"></section>
    <div class="empty-state" id="emptyState">조건에 맞는 CVE가 없습니다. 다른 키워드나 필터로 다시 찾아보세요.</div>

    <div class="toast" id="toast">리포트를 클립보드에 복사했습니다.</div>

    <footer class="footer">
      Infosec Archive · CVE 취약점 리포트<br>
      수집 소스: CISA KEV · CIRCL CVE · NVD · FIRST EPSS · GitHub 공개 PoC<br>
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
                     (it.cwe || []).join(' '), (it.poc_links || []).map(p => p.name).join(' ')]
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
      if (it.is_kev) top.push('<span class="badge-kev">KEV 실제 악용</span>');
      if (it.poc_links && it.poc_links.length) top.push('<span class="badge-poc">PoC ' + it.poc_links.length + '건</span>');
      if (it.published_at) top.push('<span class="card-date">' + escapeHtml(formatDate(it.published_at)) + ' 공개</span>');

      const metrics = [];
      const ep = epssText(it);
      if (ep) metrics.push('<span><b>' + escapeHtml(ep) + '</b></span>');
      if (it.kev_due_date) metrics.push('<span>조치 기한 <b>' + escapeHtml(formatDate(it.kev_due_date)) + '</b></span>');
      if (it.cwe && it.cwe.length) metrics.push('<span>' + escapeHtml(it.cwe.join(' · ')) + '</span>');

      const chips = (it.affected_products || []).slice(0, 4)
        .map(p => '<span class="chip">' + escapeHtml(p) + '</span>').join('');

      const pocs = (it.poc_links || []).map(p => {
        const label = escapeHtml(p.name || p.url);
        return '<div class="poc-item"><a href="' + escapeHtml(p.url) + '" target="_blank" rel="noopener noreferrer">' + label + '</a>'
          + '<span class="poc-stars">★ ' + (p.stars || 0) + '</span></div>'
          + (p.description ? '<span class="poc-desc">' + escapeHtml(p.description) + '</span>' : '');
      }).join('');

      const refs = (it.references || []).slice(0, 3).map(r => {
        const url = typeof r === 'string' ? r : (r && r.url);
        if (!url) return '';
        let host = url;
        try { host = new URL(url).hostname.replace(/^www\\./, ''); } catch (e) {}
        return '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(host) + '</a>';
      }).join('');

      return '<article class="cve-card">'
        + '<div class="cve-top">' + top.join('') + '</div>'
        + '<h2 class="cve-title">' + escapeHtml(it.title_ko) + '</h2>'
        + (metrics.length ? '<div class="cve-metrics">' + metrics.join('') + '</div>' : '')
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

    function render() {
      const visible = CVE_ITEMS.filter(matches);
      list.innerHTML = visible.map(renderCard).join('');
      visibleCount.textContent = visible.length;
      emptyState.classList.toggle('visible', visible.length === 0);
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
      document.querySelectorAll('.segment-btn').forEach(b => b.classList.toggle('active', b.getAttribute('data-filter') === 'all'));
      render();
    });

    render();
  </script>
</body>
</html>
"""


def build_briefing(items):
    kev_items = [i for i in items if i.get("is_kev")]
    poc_items = [i for i in items if i.get("poc_links")]
    crit = sum(1 for i in items if i.get("severity") == "CRITICAL")
    high = sum(1 for i in items if i.get("severity") == "HIGH")
    today = datetime.now(KST).date()

    def due_date(i):
        try:
            return datetime.strptime((i.get("kev_due_date") or "")[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    dated = [i for i in kev_items if due_date(i)]
    dated.sort(key=due_date)
    overdue = [i for i in dated if due_date(i) < today]
    imminent = [i for i in dated if due_date(i) >= today]

    if not items:
        return ("아직 수집된 CVE가 없습니다. cve_crawler.py 실행 후 다시 빌드하세요.", [])

    parts = [f"최근 수집된 CVE {len(items)}건 중 {len(kev_items)}건이 CISA KEV에 등재된 실제 악용 취약점입니다."]
    if crit or high:
        parts.append(f"CVSS 기준 Critical {crit}건, High {high}건이며, 공개 PoC가 확인된 항목은 {len(poc_items)}건입니다.")
    if overdue:
        parts.append(f"CISA 조치 기한이 이미 지난 KEV 항목이 {len(overdue)}건 있습니다. 해당 제품을 운영 중이라면 패치 적용 여부를 먼저 확인하세요.")
    if imminent:
        parts.append(f"기한이 남은 항목 중 가장 임박한 것은 {imminent[0]['kev_due_date']}까지입니다.")
    elif not overdue and kev_items:
        parts.append("KEV 등재 항목은 패치 적용 여부를 우선 확인하세요.")
    briefing = " ".join(parts)

    rows = []
    # 기한 경과 → 임박 순으로 최대 4건 노출
    for it in (overdue[-2:] + imminent)[:4]:
        d = due_date(it)
        if d < today:
            tag = f"기한 경과 {(today - d).days}일"
            cls = "due due-over"
        elif d == today:
            tag = "오늘 마감"
            cls = "due due-today"
        else:
            tag = f"D-{(d - today).days}"
            cls = "due"
        rows.append(
            '<div class="priority-row">'
            f'<span class="cve-mini">{esc(it["cve_id"])}</span>'
            f'<span>{esc(it.get("title_ko", ""))}</span>'
            f'<span class="{cls}">{tag} ({esc(it["kev_due_date"])})</span>'
            "</div>"
        )
    if not rows:
        for it in kev_items[:3]:
            rows.append(
                '<div class="priority-row">'
                f'<span class="cve-mini">{esc(it["cve_id"])}</span>'
                f'<span>{esc(it.get("title_ko", ""))}</span>'
                "</div>"
            )
    if not rows:
        rows.append('<div class="priority-row"><span>현재 KEV 등재 항목이 없습니다. 아래 목록에서 위험도가 높은 항목부터 확인하세요.</span></div>')
    return briefing, rows


def build():
    init_db()
    items = get_cve_reports()
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
        "sources": ["CISA KEV", "CIRCL CVE", "NVD", "FIRST EPSS", "GitHub"],
    }

    with open(CVE_DATA_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "items": items}, f, ensure_ascii=False, indent=2)

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__ITEMS_JSON__", json.dumps(items, ensure_ascii=False))
    html = html.replace("__META_JSON__", json.dumps(meta, ensure_ascii=False))
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
        f.write(html)

    print(f"-> 'cve.html' · 'cve_data.json' 생성 완료 (CVE {len(items)}건, KEV {stats['kev']}건, PoC {stats['poc']}건)")
    return len(items)


if __name__ == "__main__":
    build()

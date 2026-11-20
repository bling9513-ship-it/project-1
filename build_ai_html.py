#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai.html 생성기 — SQLite archive.db 의 ai_insights 테이블을 단일 소스로
AI 기술·트렌드 브리핑 페이지를 빌드한다. (index.html / study.html 과 동일 디자인 시스템)
"""
import os
import re
import json
from datetime import datetime, timezone, timedelta

from db_manager import init_db, get_ai_insights, get_ai_insight_count

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DATA_JSON = os.path.join(BASE_DIR, "ai_data.json")
AI_HTML = os.path.join(BASE_DIR, "ai.html")
KST = timezone(timedelta(hours=9))

CATEGORIES = ["AI 보안 툴", "AI 보안·안전", "AI 툴·서비스", "LLM·에이전트", "모델·논문", "산업·트렌드"]
SOURCES = ["Hugging Face", "arXiv", "Hacker News", "Show HN", "GitHub", "GeekNews",
           "The Hacker News", "Dark Reading", "Embrace the Red", "Simon Willison"]

CAT_CLASS = {
    "AI 보안 툴": "cat-sectool",
    "AI 보안·안전": "cat-sec",
    "AI 툴·서비스": "cat-tool",
    "LLM·에이전트": "cat-llm",
    "모델·논문": "cat-paper",
    "산업·트렌드": "cat-trend",
}


def esc(s):
    s = "" if s is None else str(s)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def load_meta():
    if os.path.exists(AI_DATA_JSON):
        try:
            with open(AI_DATA_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:  # noqa: BLE001
            pass
    return {}


def compute_stats(items):
    cat_counts = {c: 0 for c in CATEGORIES}
    for it in items:
        cat_counts[it["category"]] = cat_counts.get(it["category"], 0) + 1
    src_counts = {s: 0 for s in SOURCES}
    for it in items:
        src_counts[it["source"]] = src_counts.get(it["source"], 0) + 1

    tag_counter = {}
    for it in items:
        for t in {("#" + x.lstrip("#")) for x in it.get("tags", [])}:
            tag_counter[t] = tag_counter.get(t, 0) + 1
    top_keywords = sorted(tag_counter.items(), key=lambda x: (-x[1], len(x[0])))[:5]
    return cat_counts, src_counts, top_keywords


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

      --cat-llm-bg: #eff6ff;   --cat-llm-text: #2563eb;   --cat-llm-border: #bfdbfe;
      --cat-sec-bg: #fef2f2;   --cat-sec-text: #dc2626;   --cat-sec-border: #fecaca;
      --cat-sectool-bg: #eef2ff; --cat-sectool-text: #4338ca; --cat-sectool-border: #c7d2fe;
      --cat-paper-bg: #f5f3ff; --cat-paper-text: #7c3aed; --cat-paper-border: #ddd6fe;
      --cat-tool-bg: #ecfdf5;  --cat-tool-text: #047857;  --cat-tool-border: #a7f3d0;
      --cat-trend-bg: #fff7ed; --cat-trend-text: #c2410c; --cat-trend-border: #fed7aa;

      --insight-bg: #f8fafc;
      --insight-border: #cbd5e1;

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

      --cat-llm-bg: rgba(37, 99, 235, 0.16);    --cat-llm-text: #60a5fa;   --cat-llm-border: rgba(37, 99, 235, 0.3);
      --cat-sec-bg: rgba(239, 68, 68, 0.16);    --cat-sec-text: #f87171;   --cat-sec-border: rgba(239, 68, 68, 0.3);
      --cat-sectool-bg: rgba(79, 70, 229, 0.18); --cat-sectool-text: #a5b4fc; --cat-sectool-border: rgba(79, 70, 229, 0.32);
      --cat-paper-bg: rgba(124, 58, 237, 0.16);--cat-paper-text: #a78bfa; --cat-paper-border: rgba(124, 58, 237, 0.3);
      --cat-tool-bg: rgba(16, 185, 129, 0.16);  --cat-tool-text: #34d399;  --cat-tool-border: rgba(16, 185, 129, 0.3);
      --cat-trend-bg: rgba(234, 88, 12, 0.16); --cat-trend-text: #fb923c; --cat-trend-border: rgba(234, 88, 12, 0.3);

      --insight-bg: #1f1f23;
      --insight-border: #3f3f46;

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

    /* Global Header (index.html / study.html 과 동일) */
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
    .container { max-width: 1140px; margin: 0 auto; padding: 32px 20px 80px; }

    .hero { margin-bottom: 24px; }

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
      line-height: 1.6;
      margin-bottom: 16px;
      max-width: 760px;
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

    /* Briefing */
    .briefing {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 20px;
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
      font-size: 14px;
      line-height: 1.75;
      color: var(--text-secondary);
      margin-bottom: 18px;
    }

    .briefing-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
    }

    @media (min-width: 820px) {
      .briefing-grid { grid-template-columns: 1.05fr 1fr; gap: 32px; }
    }

    .block-label {
      font-size: 11.5px;
      font-weight: 700;
      letter-spacing: 0.02em;
      color: var(--text-muted);
      margin-bottom: 10px;
      text-transform: uppercase;
    }

    .kw-list { display: flex; flex-wrap: wrap; gap: 6px; }

    .kw-chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 12.5px;
      font-weight: 500;
      color: var(--text-primary);
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 5px 9px;
    }

    .kw-chip .kw-count {
      font-size: 10.5px;
      font-weight: 700;
      color: var(--text-muted);
    }

    .dist-row {
      display: grid;
      grid-template-columns: 92px 1fr 30px;
      align-items: center;
      gap: 10px;
      margin-bottom: 7px;
    }

    .dist-name { font-size: 12px; color: var(--text-secondary); white-space: nowrap; }

    .dist-track {
      display: block;
      height: 6px;
      border-radius: 3px;
      background: var(--bg-subtle);
      overflow: hidden;
    }

    .dist-bar {
      display: block;
      height: 6px;
      border-radius: 3px;
      background: var(--accent-primary);
    }

    .dist-count { font-size: 11.5px; font-weight: 600; color: var(--text-muted); text-align: right; }

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

    .sub-toolbar {
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding-top: 12px;
      border-top: 1px solid var(--border-subtle);
    }

    .filter-row { display: flex; align-items: center; gap: 6px; min-width: 0; }

    /* 출처 필터는 스크롤되고, 정렬 필터는 좁아져도 항상 보이게 고정 */
    .filter-row-sort { flex: 0 0 auto; }

    .filter-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      white-space: nowrap;
    }

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
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: inherit;
    }

    .filter-pill:hover { color: var(--text-primary); border-color: var(--border-strong); }

    .filter-pill.active {
      background: var(--accent-subtle);
      border-color: var(--accent-primary);
      color: var(--accent-primary);
      font-weight: 600;
    }

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

    /* Cards */
    .ai-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
    }

    @media (min-width: 900px) {
      .ai-grid { grid-template-columns: repeat(2, 1fr); }
    }

    .ai-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 18px 18px 16px;
      box-shadow: var(--card-shadow);
      transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
      display: flex;
      flex-direction: column;
    }

    .ai-card:hover {
      box-shadow: var(--card-shadow-hover);
      border-color: var(--border-strong);
    }

    .card-top {
      display: flex;
      align-items: center;
      gap: 7px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }

    .cat-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 5px;
      border: 1px solid transparent;
      white-space: nowrap;
    }

    .cat-llm { background: var(--cat-llm-bg); color: var(--cat-llm-text); border-color: var(--cat-llm-border); }
    .cat-sectool { background: var(--cat-sectool-bg); color: var(--cat-sectool-text); border-color: var(--cat-sectool-border); }
    .cat-sec { background: var(--cat-sec-bg); color: var(--cat-sec-text); border-color: var(--cat-sec-border); }
    .cat-paper { background: var(--cat-paper-bg); color: var(--cat-paper-text); border-color: var(--cat-paper-border); }
    .cat-tool { background: var(--cat-tool-bg); color: var(--cat-tool-text); border-color: var(--cat-tool-border); }
    .cat-trend { background: var(--cat-trend-bg); color: var(--cat-trend-text); border-color: var(--cat-trend-border); }

    .star-badge {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-secondary);
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      padding: 3px 7px;
      border-radius: 5px;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }

    .src-badge {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      padding: 3px 7px;
      border-radius: 5px;
      white-space: nowrap;
    }

    .featured-badge {
      font-size: 10.5px;
      font-weight: 700;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      padding: 3px 7px;
      border-radius: 5px;
      white-space: nowrap;
    }

    .card-date {
      margin-left: auto;
      font-size: 11.5px;
      color: var(--text-muted);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }

    .ai-title {
      font-size: 16px;
      font-weight: 700;
      line-height: 1.45;
      letter-spacing: -0.025em;
      color: var(--text-primary);
      margin-bottom: 4px;
    }

    .ai-title a { text-decoration: none; color: inherit; }

    .ai-title a:hover { color: var(--accent-primary); }

    .ai-title-orig {
      font-size: 11.5px;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 10px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .ai-summary {
      font-size: 13.5px;
      line-height: 1.7;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }

    .insight-box {
      background: var(--insight-bg);
      border: 1px solid var(--border-default);
      border-left: 3px solid var(--insight-border);
      border-radius: 8px;
      padding: 11px 13px;
      margin-bottom: 13px;
    }

    .insight-label {
      display: block;
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.02em;
      color: var(--text-muted);
      margin-bottom: 5px;
    }

    .insight-box p {
      font-size: 12.5px;
      line-height: 1.65;
      color: var(--text-secondary);
    }

    .card-bottom {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 10px;
      margin-top: auto;
      flex-wrap: wrap;
    }

    .tag-list { display: flex; flex-wrap: wrap; gap: 5px; min-width: 0; }

    .tag-chip {
      font-size: 11px;
      font-weight: 500;
      color: var(--tag-text);
      background: var(--tag-bg);
      border: 1px solid var(--tag-border);
      border-radius: 5px;
      padding: 3px 7px;
      white-space: nowrap;
    }

    .source-link {
      font-size: 12px;
      font-weight: 600;
      color: var(--accent-primary);
      text-decoration: none;
      white-space: nowrap;
      padding: 3px 2px;
    }

    .source-link:hover { color: var(--accent-hover); text-decoration: underline; }

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
      .briefing-text { font-size: 13px; line-height: 1.7; }
      .briefing-grid { gap: 16px; }
      .dist-row { grid-template-columns: 84px 1fr 26px; gap: 8px; }
      .toolbar { padding: 12px; border-radius: 12px; gap: 10px; }
      .search-input { padding: 9px 34px 9px 36px; font-size: 13px; }
      .segment-btn { padding: 6px 10px; font-size: 12px; }
      .ai-grid { gap: 12px; }
      .ai-card { padding: 15px 14px 14px; border-radius: 12px; }
      .ai-title { font-size: 15px; }
      .ai-summary { font-size: 13px; }
      .insight-box { padding: 10px 11px; }
      .insight-box p { font-size: 12px; }
      .kw-chip { font-size: 12px; padding: 4px 8px; }
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
  <title>Infosec Archive · AI 기술·트렌드 브리핑</title>
  <meta name="description" content="AI 보안 소식과 AI 툴·오픈소스까지 한 번에 — arXiv·Hugging Face 논문, 보안 전문 매체(The Hacker News·Dark Reading·Embrace the Red), GitHub 트렌딩 저장소, Hacker News·Show HN·GeekNews를 매일 수집해 한국어로 분석·요약한 AI 기술 브리핑입니다.">
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
          <a href="ai.html" class="nav-tab-item active">AI 트렌드</a>
          <a href="cve.html" class="nav-tab-item">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
          <a href="radar.html" class="nav-tab-item">피싱 레이더</a>
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
      <span class="hero-pill">DAILY AI BRIEFING</span>
      <h1 class="hero-title">AI 기술·트렌드 브리핑</h1>
      <p class="hero-desc">AI 보안과 AI 툴까지 함께 모읍니다. arXiv·Hugging Face의 최신 논문, The Hacker News·Dark Reading·Embrace the Red의 AI 보안 소식, GitHub에서 주목받는 AI/LLM/에이전트/MCP 오픈소스 도구, Hacker News·Show HN·GeekNews의 실무 담론을 매일 수집해 한국어 요약과 기술·보안 시사점으로 정리합니다.</p>
      <div class="hero-stats">
        <span class="stat-chip">수집·분석 <strong>__TOTAL__건</strong></span>
        <span class="stat-chip">주목할 기술 <strong>__FEATURED__건</strong></span>
        <span class="stat-chip">출처 <strong>__ACTIVE_SOURCES__곳</strong></span>
        <span class="stat-chip">매일 <strong>08:00</strong> 자동 갱신</span>
      </div>
    </section>

    <!-- Today's Briefing -->
    <section class="briefing">
      <div class="briefing-head">
        <div class="briefing-title"><span class="bar"></span>오늘의 AI 기술 동향</div>
        <span class="briefing-time">__UPDATED_AT__ 기준</span>
      </div>
      <p class="briefing-text">__BRIEFING__</p>

      <div class="briefing-grid">
        <div>
          <div class="block-label">핵심 기술 키워드 Top 5</div>
          <div class="kw-list">
            __KEYWORD_CHIPS__
          </div>
        </div>
        <div>
          <div class="block-label">카테고리 분포</div>
          <div class="dist-list">
            __DIST_ROWS__
          </div>
        </div>
      </div>
    </section>

    <!-- Toolbar -->
    <section class="toolbar">
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="searchInput" class="search-input" placeholder="제목, 요약, 키워드로 검색 (예: 프롬프트 인젝션, 에이전트 보안, MCP, 오픈소스 툴)">
        <button id="clearSearch" class="clear-search-btn" aria-label="검색 지우기">✕</button>
      </div>

      <div class="segmented-control" id="categoryNav">
        <button class="segment-btn active" data-cat="all">전체 <span class="count">__TOTAL__</span></button>
        <button class="segment-btn" data-cat="featured">주목할 기술 <span class="count">__FEATURED__</span></button>
        __CATEGORY_BUTTONS__
      </div>

      <div class="sub-toolbar">
        <div class="filter-row">
          <span class="filter-label">출처</span>
          <div class="filter-pills-scroll" id="sourceNav">
            <button class="filter-pill active" data-src="all">전체</button>
            __SOURCE_PILLS__
          </div>
        </div>
        <div class="filter-row filter-row-sort">
          <span class="filter-label">정렬</span>
          <div class="filter-pills-scroll" id="sortNav">
            <button class="filter-pill active" data-sort="featured">주목할 기술 우선</button>
            <button class="filter-pill" data-sort="latest">최신순</button>
          </div>
        </div>
      </div>
    </section>

    <div class="result-meta">
      <span><strong id="visibleCount">__TOTAL__</strong>건 표시 중 · 전체 __TOTAL__건</span>
      <button class="reset-btn" id="resetFilters">필터 초기화</button>
    </div>

    <section class="ai-grid" id="aiGrid"></section>
    <div class="empty-state" id="emptyState">조건에 맞는 자료가 없습니다. 다른 키워드나 필터로 다시 찾아보세요.</div>

    <footer class="footer">
      Infosec Archive · AI 기술·트렌드 브리핑<br>
      수집 출처: Hugging Face Daily Papers · arXiv(cs.AI·cs.CL·cs.CR) · GitHub · Hacker News · Show HN · GeekNews · The Hacker News · Dark Reading · Embrace the Red<br>
      모든 요약·분석은 원문을 바탕으로 AI가 한국어로 정리한 것이며, 정확한 내용은 원문 링크에서 확인하세요.
    </footer>
  </main>

  <script>
    const AI_ITEMS = __ITEMS_JSON__;
    const AI_META = __META_JSON__;

    const CAT_CLASS = __CAT_CLASS_JSON__;

    // ---- Theme (index.html / study.html 과 동일한 secjobs-theme 동기화) ----
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');

    function initTheme() {
      const saved = localStorage.getItem('secjobs-theme');
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        setTheme('dark');
      } else {
        setTheme('light');
      }
    }

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

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    // ---- State ----
    let activeCat = 'all';
    let activeSrc = 'all';
    let activeSort = 'featured';
    let searchTerm = '';

    const grid = document.getElementById('aiGrid');
    const emptyState = document.getElementById('emptyState');
    const visibleCount = document.getElementById('visibleCount');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');

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

    function matches(item) {
      if (activeCat === 'featured' && !item.is_featured) return false;
      if (activeCat !== 'all' && activeCat !== 'featured' && item.category !== activeCat) return false;
      if (activeSrc !== 'all' && item.source !== activeSrc) return false;
      if (searchTerm) {
        const q = searchTerm.toLowerCase();
        const hay = [item.title_ko, item.title_orig, item.summary, item.tech_insight,
                     item.category, item.source, (item.tags || []).join(' ')].join(' ').toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    }

    function sorted(list) {
      const arr = list.slice();
      if (activeSort === 'latest') {
        arr.sort((a, b) => String(b.published_at || '').localeCompare(String(a.published_at || '')));
      } else {
        arr.sort((a, b) => {
          if (a.is_featured !== b.is_featured) return a.is_featured ? -1 : 1;
          const d = String(b.published_at || '').localeCompare(String(a.published_at || ''));
          if (d !== 0) return d;
          return (b.score || 0) - (a.score || 0);
        });
      }
      return arr;
    }

    function cardHtml(item) {
      const catCls = CAT_CLASS[item.category] || 'cat-trend';
      const tags = (item.tags || []).map(t => `<span class="tag-chip">${escapeHtml(t)}</span>`).join('');
      const featured = item.is_featured ? '<span class="featured-badge">주목</span>' : '';
      const star = (item.source === 'GitHub' && item.score > 0)
        ? `<span class="star-badge">스타 ${item.score >= 1000 ? (item.score / 1000).toFixed(1).replace(/\\.0$/, '') + 'k' : item.score}</span>` : '';
      const orig = item.title_orig && item.title_orig !== item.title_ko
        ? `<p class="ai-title-orig">${escapeHtml(item.title_orig)}</p>` : '';
      return `
        <article class="ai-card">
          <div class="card-top">
            <span class="cat-badge ${catCls}">${escapeHtml(item.category)}</span>
            <span class="src-badge">${escapeHtml(item.source)}</span>
            ${star}
            ${featured}
            <span class="card-date">${formatDate(item.published_at)}</span>
          </div>
          <h3 class="ai-title"><a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title_ko)}</a></h3>
          ${orig}
          <p class="ai-summary">${escapeHtml(item.summary)}</p>
          <div class="insight-box">
            <span class="insight-label">기술 포인트 &amp; 시사점</span>
            <p>${escapeHtml(item.tech_insight)}</p>
          </div>
          <div class="card-bottom">
            <div class="tag-list">${tags}</div>
            <a class="source-link" href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">원문 보기 →</a>
          </div>
        </article>`;
    }

    function render() {
      const list = sorted(AI_ITEMS.filter(matches));
      grid.innerHTML = list.map(cardHtml).join('');
      visibleCount.textContent = list.length;
      emptyState.classList.toggle('visible', list.length === 0);
      clearSearchBtn.classList.toggle('visible', searchTerm.length > 0);
    }

    // Category segments
    document.querySelectorAll('#categoryNav .segment-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#categoryNav .segment-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeCat = btn.dataset.cat;
        render();
      });
    });

    // Source pills
    document.querySelectorAll('#sourceNav .filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#sourceNav .filter-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeSrc = btn.dataset.src;
        render();
      });
    });

    // Sort pills
    document.querySelectorAll('#sortNav .filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#sortNav .filter-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeSort = btn.dataset.sort;
        render();
      });
    });

    // Search
    let debounce = null;
    searchInput.addEventListener('input', (e) => {
      const val = e.target.value;
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        searchTerm = val.trim();
        render();
      }, 120);
    });

    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      searchTerm = '';
      render();
      searchInput.focus();
    });

    document.getElementById('resetFilters').addEventListener('click', () => {
      activeCat = 'all';
      activeSrc = 'all';
      activeSort = 'featured';
      searchTerm = '';
      searchInput.value = '';
      document.querySelectorAll('#categoryNav .segment-btn').forEach(b => b.classList.toggle('active', b.dataset.cat === 'all'));
      document.querySelectorAll('#sourceNav .filter-pill').forEach(b => b.classList.toggle('active', b.dataset.src === 'all'));
      document.querySelectorAll('#sortNav .filter-pill').forEach(b => b.classList.toggle('active', b.dataset.sort === 'featured'));
      render();
    });

    initTheme();
    render();
  </script>
</body>
</html>
"""


# 페이지에 노출할 최대 건수 (매일 누적되는 DB 전체를 그대로 그리면 페이지가 계속 무거워지므로 상한을 둔다)
DISPLAY_LIMIT = 150


def cap_featured(items, ratio=0.28, minimum=10, maximum=24):
    """'주목할 기술'이 페이지 절반을 넘지 않도록 최신순으로 상한을 둔다.

    (EXAONE가 배치마다 is_featured 를 넉넉하게 주기 때문에 그대로 두면 필터가 무의미해진다.)
    """
    featured = [it for it in items if it.get("is_featured")]
    limit = max(minimum, min(maximum, round(len(items) * ratio)))
    if len(featured) <= limit:
        return items
    featured.sort(key=lambda it: (it.get("published_at") or "", it.get("score") or 0), reverse=True)
    keep = {it["item_key"] for it in featured[:limit]}
    for it in items:
        if it.get("is_featured") and it["item_key"] not in keep:
            it["is_featured"] = False
    return items


def build():
    init_db()
    items = cap_featured(get_ai_insights(limit=DISPLAY_LIMIT))

    meta = load_meta()
    cells = meta.get("top_keywords") or []
    if not cells:
        _, _, cells_t = compute_stats(items)
        cells = [{"keyword": k, "count": v} for k, v in cells_t]

    cat_counts, src_counts, _ = compute_stats(items)
    total = len(items)
    featured = sum(1 for it in items if it.get("is_featured"))
    active_sources = sum(1 for v in src_counts.values() if v)

    updated_at = meta.get("updated_at") or datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")

    briefing = meta.get("briefing") or ""
    if not briefing:
        top = " ".join(c.get("keyword", "") for c in cells[:3]) if cells else ""
        briefing = (f"오늘 수집된 AI 자료 {total}건을 분석했습니다. 핵심 키워드는 {top}이며, "
                    f"주목할 기술 {featured}건을 포함합니다. 각 카드의 기술 포인트 & 시사점에서 실무 적용 지점을 확인하세요.")
    else:
        # 수집 시점 브리핑의 '주목할 기술 N건'은 캡 적용 전 숫자라 상단 지표(실제 노출 수)와 어긋난다.
        # 페이지에 그리는 값에 맞춰 문장 안의 수치를 교정한다.
        briefing = re.sub(r"주목할 기술\s*\d+\s*건", f"주목할 기술 {featured}건", briefing)

    # 키워드 칩
    kw_html = "".join(
        f'<span class="kw-chip">{esc(c.get("keyword", ""))}<span class="kw-count">{c.get("count", 0)}</span></span>'
        for c in cells[:5]
    ) or '<span class="kw-chip">수집 대기</span>'

    # 카테고리 분포
    max_count = max(cat_counts.values()) if cat_counts and max(cat_counts.values()) > 0 else 1
    dist_html = ""
    for cat in CATEGORIES:
        n = cat_counts.get(cat, 0)
        pct = max(4, round(n / max_count * 100)) if n else 3
        dist_html += (
            f'<div class="dist-row"><span class="dist-name">{esc(cat)}</span>'
            f'<span class="dist-track"><span class="dist-bar" style="width:{pct}%"></span></span>'
            f'<span class="dist-count">{n}</span></div>'
        )

    # 카테고리 세그먼트 버튼
    cat_btns = "".join(
        f'<button class="segment-btn" data-cat="{esc(c)}">{esc(c)} <span class="count">{cat_counts.get(c, 0)}</span></button>'
        for c in CATEGORIES
    )

    # 출처 필터
    src_pills = "".join(
        f'<button class="filter-pill" data-src="{esc(s)}">{esc(s)} {src_counts.get(s, 0)}</button>'
        for s in SOURCES if src_counts.get(s, 0)
    )

    def display_title(it):
        # 'Show HN:' 같은 수집 접두어는 출처 배지로 이미 드러나므로 제목에서 걷어낸다
        return re.sub(r"^(Show|Launch|Ask) HN\s*:\s*", "", it["title_ko"] or "").strip()

    payload_items = [
        {
            "item_key": it["item_key"],
            "source": it["source"],
            "title_ko": display_title(it),
            "title_orig": it["title_orig"],
            "url": it["url"],
            "category": it["category"],
            "summary": it["summary"],
            "tech_insight": it["tech_insight"],
            "tags": it.get("tags", []),
            "is_featured": bool(it.get("is_featured")),
            "published_at": it.get("published_at", ""),
            "score": it.get("score", 0),
        }
        for it in items
    ]

    meta_payload = {
        "updated_at": updated_at,
        "total": total,
        "featured": featured,
        "briefing": briefing,
        "categories": cat_counts,
        "sources": src_counts,
        "top_keywords": cells[:5],
    }

    html_out = (HTML_TEMPLATE
                .replace("__CSS__", CSS)
                .replace("__TOTAL__", str(total))
                .replace("__FEATURED__", str(featured))
                .replace("__ACTIVE_SOURCES__", str(active_sources))
                .replace("__UPDATED_AT__", esc(updated_at))
                .replace("__BRIEFING__", esc(briefing))
                .replace("__KEYWORD_CHIPS__", kw_html)
                .replace("__DIST_ROWS__", dist_html)
                .replace("__CATEGORY_BUTTONS__", cat_btns)
                .replace("__SOURCE_PILLS__", src_pills)
                .replace("__ITEMS_JSON__", json.dumps(payload_items, ensure_ascii=False).replace("</", "<\\/"))
                .replace("__META_JSON__", json.dumps(meta_payload, ensure_ascii=False).replace("</", "<\\/"))
                .replace("__CAT_CLASS_JSON__", json.dumps(CAT_CLASS, ensure_ascii=False)))

    with open(AI_HTML, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"-> 'ai.html' 생성 완료 ({total}건, 주목할 기술 {featured}건)")
    return total


if __name__ == "__main__":
    build()

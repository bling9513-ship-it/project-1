#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_study_html.py:
보안 채용공고 메인 웹사이트(index.html)와 100% 동일한 디자인 시스템,
컬러 팔레트, 폰트 자간, 헤더/내비게이션, 카드 섀도우를 공유하는
'시험 공부' 통합 허브 HTML 생성 스크립트
"""

import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'cppg_questions.json')
js_path = os.path.join(base_dir, 'cppg_questions.js')
out_path = os.path.join(base_dir, 'study.html')

with open(json_path, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Write cppg_questions.js with safe escaping
safe_json = json.dumps(questions, ensure_ascii=False).replace('</script>', '<\\/script>')
with open(js_path, 'w', encoding='utf-8') as f:
    f.write('window.ALL_QUESTIONS = ' + safe_json + ';\n')

html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>시험 공부 &amp; 맞춤 AI 스터디 허브 | Infosec Archive</title>
  <meta name="description" content="CPPG 실전 300제, 정보보안기사(필기·실기), ISMS-P 인증심사원 기출 퀴즈와 전 과목 핵심 요약노트 및 파일/URL 맞춤 분석 학습 허브입니다.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
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
      
      --success-bg: #ecfdf5;
      --success-text: #059669;
      --success-border: #a7f3d0;
      
      --urgent-bg: #fef2f2;
      --urgent-text: #dc2626;
      --urgent-border: #fecaca;
      
      --warning-bg: #fff7ed;
      --warning-text: #ea580c;
      --warning-border: #fed7aa;
      
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
      
      --success-bg: rgba(16, 185, 129, 0.15);
      --success-text: #34d399;
      --success-border: rgba(16, 185, 129, 0.3);
      
      --urgent-bg: rgba(239, 68, 68, 0.15);
      --urgent-text: #f87171;
      --urgent-border: rgba(239, 68, 68, 0.3);
      
      --warning-bg: rgba(234, 88, 12, 0.15);
      --warning-text: #fb923c;
      --warning-border: rgba(234, 88, 12, 0.3);
      
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

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

    /* Global Header (index.html과 100% 동일) */
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

    .nav-brand {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: inherit;
    }

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
    }

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

    .nav-tab-item:hover {
      background: var(--bg-subtle);
      color: var(--text-primary);
    }

    .nav-tab-item.active {
      background: var(--accent-primary);
      color: #ffffff !important;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

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
    }

    .icon-btn:hover {
      background: var(--bg-subtle);
      color: var(--text-primary);
    }

    /* Main Container */
    .main-wrap {
      max-width: 1140px;
      margin: 0 auto;
      padding: 28px 20px 80px;
    }

    /* Hero Section */
    .hero {
      margin-bottom: 24px;
      text-align: center;
    }

    .hero-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      background: var(--accent-subtle);
      color: var(--accent-primary);
      font-size: 12px;
      font-weight: 600;
      border-radius: 20px;
      margin-bottom: 10px;
      border: 1px solid rgba(37, 99, 235, 0.2);
    }

    .hero-title {
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.03em;
      margin-bottom: 6px;
      color: var(--text-primary);
    }

    .hero-desc {
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.5;
    }

    /* Category Bar Section */
    .category-section {
      margin-bottom: 20px;
    }

    .category-label {
      font-size: 11.5px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .category-bar {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 4px;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
    }
    .category-bar::-webkit-scrollbar { display: none; }

    .cat-chip {
      padding: 7px 14px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      box-shadow: var(--card-shadow);
    }

    .cat-chip:hover {
      border-color: var(--border-strong);
      color: var(--text-primary);
    }

    .cat-chip.active {
      background: var(--text-primary);
      color: var(--bg-surface) !important;
      border-color: var(--text-primary);
    }

    .cat-chip.add-chip {
      background: var(--bg-subtle);
      border-style: dashed;
      color: var(--accent-primary);
    }
    .cat-chip.add-chip:hover {
      border-color: var(--accent-primary);
      background: var(--accent-subtle);
    }

    /* Add Resource Panel */
    .add-resource-panel {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
      box-shadow: var(--card-shadow);
      display: none;
    }
    .add-resource-panel.show { display: block; }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border-default);
    }

    .panel-title {
      font-size: 15px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .panel-close {
      background: none;
      border: none;
      font-size: 18px;
      color: var(--text-muted);
      cursor: pointer;
      padding: 4px;
    }
    .panel-close:hover { color: var(--text-primary); }

    .form-group { margin-bottom: 16px; }
    .form-label { display: block; font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
    .form-input {
      width: 100%;
      padding: 9px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      color: var(--text-primary);
      font-size: 13.5px;
      outline: none;
      transition: border-color 0.15s ease;
    }
    .form-input:focus { border-color: var(--accent-primary); }

    .source-type-selector { display: flex; gap: 8px; margin-bottom: 12px; }
    .source-type-btn {
      flex: 1;
      padding: 8px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }
    .source-type-btn.active {
      border-color: var(--accent-primary);
      background: var(--accent-subtle);
      color: var(--accent-primary);
    }

    .drop-zone {
      border: 2px dashed var(--border-strong);
      border-radius: 10px;
      padding: 24px;
      text-align: center;
      cursor: pointer;
      background: var(--bg-page);
      transition: all 0.15s;
    }
    .drop-zone:hover { border-color: var(--accent-primary); background: var(--accent-subtle); }
    .drop-icon { font-size: 28px; margin-bottom: 8px; color: var(--text-muted); }
    .drop-text { font-size: 13px; font-weight: 600; color: var(--text-primary); }
    .drop-hint { font-size: 11.5px; color: var(--text-muted); margin-top: 4px; }

    .panel-options { display: flex; flex-direction: column; gap: 8px; }
    .option-check { display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: var(--text-secondary); cursor: pointer; }
    .option-check input { accent-color: var(--accent-primary); }

    .submit-btn {
      width: 100%;
      padding: 10px;
      border-radius: 8px;
      background: var(--accent-primary);
      color: #ffffff;
      border: none;
      font-size: 13.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.15s;
    }
    .submit-btn:hover { background: var(--accent-hover); }

    /* Top Stats Grid */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 20px;
    }

    .stat-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      padding: 14px 16px;
      box-shadow: var(--card-shadow);
      transition: all 0.15s ease;
    }

    .stat-label {
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 4px;
    }

    .stat-val {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text-primary);
    }
    .stat-val.accent { color: var(--accent-primary); }

    /* Mode Segmented Control Bar */
    .mode-nav-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 16px;
      background: var(--bg-subtle);
      padding: 4px;
      border-radius: 12px;
      border: 1px solid var(--border-default);
    }

    .mode-btn {
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .mode-btn:hover { color: var(--text-primary); }

    .mode-btn.active {
      background: var(--bg-surface);
      color: var(--text-primary);
      box-shadow: var(--card-shadow);
    }

    /* Controls Bar */
    .controls-bar {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 20px;
    }

    .exam-btn-group {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 8px;
    }

    .exam-btn {
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease;
      box-shadow: var(--card-shadow);
    }

    .exam-btn:hover { border-color: var(--border-strong); color: var(--text-primary); }

    .exam-btn.active {
      border-color: var(--accent-primary);
      background: var(--accent-subtle);
      color: var(--accent-primary);
    }

    .filter-and-tools {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    .subj-chips-scroll {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
      padding-bottom: 2px;
    }
    .subj-chips-scroll::-webkit-scrollbar { display: none; }

    .filter-pill {
      padding: 5px 12px;
      border-radius: 16px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }

    .filter-pill:hover { border-color: var(--border-strong); color: var(--text-primary); }

    .filter-pill.active {
      background: var(--text-primary);
      color: var(--bg-surface);
      border-color: var(--text-primary);
    }

    .tools-wrap {
      display: flex;
      gap: 6px;
    }

    .tool-btn {
      padding: 5px 10px;
      border-radius: 6px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }

    .tool-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .tool-btn.active { background: var(--urgent-bg); color: var(--urgent-text); border-color: var(--urgent-border); }

    /* Question Cards */
    .questions-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .q-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      padding: 20px;
      box-shadow: var(--card-shadow);
      transition: border-color 0.15s ease;
    }

    .q-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
    }

    .q-badge {
      font-size: 11px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 4px;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
    }

    .q-num {
      font-size: 12px;
      font-weight: 700;
      color: var(--accent-primary);
      margin-left: auto;
    }

    .q-prompt {
      font-size: 15px;
      font-weight: 700;
      line-height: 1.6;
      color: var(--text-primary);
      margin-bottom: 16px;
      white-space: pre-wrap;
    }

    .choices-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .choice-row {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      color: var(--text-primary);
      cursor: pointer;
      font-size: 13.5px;
      line-height: 1.5;
      transition: all 0.15s ease;
    }

    .choice-row:hover {
      border-color: var(--accent-primary);
      background: var(--accent-subtle);
    }

    .choice-circle {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
      color: var(--text-secondary);
      flex-shrink: 0;
      margin-top: 1px;
    }

    .choice-text { flex: 1; }

    /* Answer States */
    .choice-row.correct {
      border-color: #10b981 !important;
      background: var(--success-bg) !important;
      color: var(--success-text) !important;
      font-weight: 600;
    }
    .choice-row.correct .choice-circle {
      background: #10b981;
      border-color: #10b981;
      color: #ffffff;
    }

    .choice-row.wrong {
      border-color: #ef4444 !important;
      background: var(--urgent-bg) !important;
      color: var(--urgent-text) !important;
    }
    .choice-row.wrong .choice-circle {
      background: #ef4444;
      border-color: #ef4444;
      color: #ffffff;
    }

    /* Explanation Box */
    .exp-box {
      margin-top: 14px;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      font-size: 12.5px;
      line-height: 1.6;
      display: none;
    }
    .exp-box.show { display: block; }
    .exp-header { font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
    .exp-header.correct { color: #10b981; }
    .exp-header.wrong { color: #ef4444; }

    /* Summary Note Cards */
    .summary-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .summary-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      padding: 20px;
      box-shadow: var(--card-shadow);
    }

    .summary-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-default);
    }

    .summary-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .summary-badge {
      font-size: 11px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 4px;
      background: var(--accent-subtle);
      color: var(--accent-primary);
      border: 1px solid rgba(37, 99, 235, 0.2);
    }

    .summary-topic {
      margin-bottom: 14px;
    }
    .summary-topic:last-child { margin-bottom: 0; }

    .summary-topic-title {
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 6px;
    }

    .summary-topic ul {
      list-style: none;
      padding-left: 0;
      display: flex;
      flex-direction: column;
      gap: 5px;
    }

    .summary-topic li {
      font-size: 12.5px;
      color: var(--text-secondary);
      line-height: 1.6;
      padding-left: 12px;
      position: relative;
    }
    .summary-topic li::before {
      content: "•";
      position: absolute;
      left: 0;
      color: var(--accent-primary);
    }

    /* Custom AI Banner */
    .custom-section { display: none; }
    .custom-hero-banner {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
      box-shadow: var(--card-shadow);
    }
    .custom-hero-title { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
    .custom-hero-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }

    .custom-guide-card {
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 20px;
      display: flex;
      gap: 12px;
      align-items: flex-start;
    }
    .custom-guide-icon { font-size: 20px; line-height: 1; }
    .custom-guide-title { font-size: 13.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
    .custom-guide-text { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }

    /* Footer */
    footer {
      margin-top: 60px;
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.8;
    }

    /* Responsive & Mobile Polish */
    .btn-text-mobile { display: none; }
    .btn-text-full { display: inline; }

    @media (max-width: 640px) {
      .nav-container {
        padding: 0 12px;
        height: 54px;
      }
      .brand-name {
        font-size: 15px;
      }
      .brand-logo-img {
        width: 24px;
        height: 24px;
      }
      .nav-tabs {
        margin-left: 6px;
        gap: 4px;
      }
      .nav-tab-item {
        padding: 4px 9px;
        font-size: 11.5px;
        border-radius: 14px;
      }
      .update-meta {
        display: none !important;
      }
      .main-wrap {
        padding: 16px 12px 60px;
      }
      .hero {
        margin-bottom: 16px;
      }
      .hero-title {
        font-size: 20px;
        letter-spacing: -0.03em;
      }
      .hero-desc {
        font-size: 12.5px;
        line-height: 1.5;
      }
      .stats-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
      }
      .stat-card {
        padding: 10px 12px;
      }
      .stat-label {
        font-size: 11px;
        white-space: nowrap;
      }
      .stat-val {
        font-size: 18px;
      }
      .mode-nav-grid {
        gap: 4px;
        padding: 3px;
      }
      .mode-btn {
        padding: 7px 4px;
        font-size: 11.5px;
        gap: 4px;
      }
      .btn-text-full {
        display: none !important;
      }
      .btn-text-mobile {
        display: inline !important;
      }
      .exam-btn-group {
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
      }
      .exam-btn {
        padding: 7px 6px;
        font-size: 12px;
      }
      .q-card {
        padding: 16px 14px;
      }
      .q-prompt {
        font-size: 14px;
        line-height: 1.55;
      }
      .choice-row {
        padding: 9px 10px;
        font-size: 13px;
      }
      .choice-circle {
        width: 20px;
        height: 20px;
        font-size: 11px;
        margin-top: 1px;
      }
    }
  </style>
</head>
<body>

  <!-- Global Nav (index.html과 100% 동일 구조) -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
        <div class="nav-tabs">
          <a href="index.html" class="nav-tab-item">보안 채용공고</a>
          <a href="study.html" class="nav-tab-item active">시험 공부</a>
        </div>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>스터디 허브</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 전환" aria-label="화면 테마 전환">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
          <svg id="sunIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
        </button>
      </div>
    </div>
  </header>

  <div class="main-wrap">
    <!-- Hero -->
    <div class="hero">
      <div class="hero-pill">자격증 시험 대비 · 핵심 문제 풀이</div>
      <h1 class="hero-title" id="pageMainTitle">CPPG 실전 300제 &amp; 전 과목 핵심 노트</h1>
      <p class="hero-desc" id="pageMainDesc">실전 모의고사 1·2·3회 300문항 즉시 채점, 187p 전 과목 핵심 요약 및 파일/URL 맞춤 분석</p>
    </div>

    <!-- Exam Category Selector -->
    <div class="category-section">
      <div class="category-label">
        <span>시험 종목 / 학습 카테고리</span>
        <span id="activeExamBadge" style="color:var(--accent-primary);font-weight:600;">개인정보관리사 (CPPG)</span>
      </div>
      <div class="category-bar" id="categoryBar">
        <button class="cat-chip active" data-cat="cppg">개인정보관리사 (CPPG)</button>
        <button class="cat-chip" data-cat="infosec_written">정보보안기사 (필기)</button>
        <button class="cat-chip" data-cat="infosec_practical">정보보안기사 (실기)</button>
        <button class="cat-chip" data-cat="ismsp_auditor">ISMS-P 인증심사원</button>
        <button class="cat-chip" data-cat="custom">맞춤 분석 (파일·URL)</button>
        <button class="cat-chip add-chip" id="btnAddResource" data-cat="add_new">+ 새 자료 등록</button>
      </div>
    </div>

    <!-- Add Resource Panel -->
    <div class="add-resource-panel" id="addResourcePanel">
      <div class="panel-header">
        <div class="panel-title">
          <span>새 학습자료 분석 &amp; 카테고리 등록</span>
        </div>
        <button class="panel-close" id="btnCloseAddPanel" title="닫기">&times;</button>
      </div>
      <div class="panel-form">
        <div class="form-group">
          <label class="form-label">시험명 또는 카테고리 제목</label>
          <input type="text" class="form-input" id="newCategoryTitle" placeholder="예: 개인정보보호법 2026 개정특강, AWS SAA, 네트워크관리사">
        </div>
        
        <div class="form-group">
          <label class="form-label">학습 자료 유형</label>
          <div class="source-type-selector">
            <button type="button" class="source-type-btn active" id="btnSourceFile" onclick="setSourceType('file')">문서 파일 (PDF / TXT / MD)</button>
            <button type="button" class="source-type-btn" id="btnSourceUrl" onclick="setSourceType('url')">웹 링크 (URL)</button>
          </div>
        </div>

        <div class="form-group" id="fileInputGroup">
          <label class="form-label">문서 파일 첨부</label>
          <input type="file" id="studyFileInput" accept=".pdf,.txt,.md,.json" style="display:none;" onchange="handleFileSelect(event)">
          <div class="drop-zone" id="dropZone" onclick="document.getElementById('studyFileInput').click()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:8px;color:var(--text-muted);"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            <div class="drop-text" id="dropFileName">클릭하여 PDF, TXT, MD 파일 선택 또는 드래그 앤 드롭</div>
            <div class="drop-hint">CPPG 요약본, 기출 해설서, 기술 표준 문서를 지원합니다</div>
          </div>
        </div>

        <div class="form-group" id="urlInputGroup" style="display:none;">
          <label class="form-label">웹 페이지 URL 링크</label>
          <input type="url" class="form-input" id="studyUrlInput" placeholder="https://law.go.kr/... 또는 기술 공식 문서 링크">
        </div>

        <div class="form-group">
          <label class="form-label">엑사원 AI 분석 옵션</label>
          <div class="panel-options">
            <label class="option-check"><input type="checkbox" id="chkSummary" checked> 핵심 3줄 서머리 &amp; 중요 개념 추출</label>
            <label class="option-check"><input type="checkbox" id="chkQuiz" checked> 실전 5지선다 문제 세트 자동 출제</label>
            <label class="option-check"><input type="checkbox" id="chkTraps" checked> 시험 빈출 함정 포인트 정리</label>
          </div>
        </div>

        <button type="button" class="submit-btn" id="btnRequestAnalysis" onclick="requestAnalysis()">
          <span>AI 분석 &amp; 카테고리 퀴즈 생성</span>
        </button>
      </div>
    </div>

    <!-- Top Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">현재 회차 문항</div>
        <div class="stat-val" id="topTotal">100</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">푼 문제</div>
        <div class="stat-val" id="topSolved">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">정답 수</div>
        <div class="stat-val accent" id="topCorrect">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">정답률 / 합격진단</div>
        <div class="stat-val" id="topRate">0%</div>
      </div>
    </div>

    <!-- Mode Selector -->
    <div class="mode-nav-grid" id="modeNavGrid">
      <button class="mode-btn active" data-mode="quiz" id="modeQuizBtn">
        <span class="btn-text-full" id="modeQuizLabel">실전 모의고사 (300제)</span>
        <span class="btn-text-mobile" id="modeQuizLabelMobile">실전 300제</span>
      </button>
      <button class="mode-btn" data-mode="summary" id="modeSummaryBtn">
        <span class="btn-text-full" id="modeSummaryLabel">전 과목 핵심 요약노트</span>
        <span class="btn-text-mobile" id="modeSummaryLabelMobile">핵심 요약집</span>
      </button>
      <button class="mode-btn" data-mode="custom" id="modeCustomBtn">
        <span class="btn-text-full" id="modeCustomLabel">맞춤 AI 분석 &amp; 퀴즈</span>
        <span class="btn-text-mobile" id="modeCustomLabelMobile">맞춤 AI</span>
      </button>
    </div>

    <!-- Controls Bar -->
    <div class="controls-bar" id="controlsBar">
      <div class="exam-btn-group" id="examBtnGroup">
        <!-- Rendered dynamically -->
      </div>
      <div class="filter-and-tools">
        <div class="subj-chips-scroll" id="subjPills">
          <!-- Rendered dynamically -->
        </div>
        <div class="tools-wrap">
          <button class="tool-btn" id="btnWrongOnly">오답만 보기</button>
          <button class="tool-btn" id="btnReset">풀이 초기화</button>
        </div>
      </div>
    </div>

    <!-- QUIZ VIEW -->
    <div class="questions-list" id="questionsList">
      <!-- Questions rendered dynamically -->
    </div>

    <!-- SUMMARY VIEW -->
    <div class="summary-section" id="summarySection">
      <!-- Dynamic summary cards loaded here -->
    </div>

    <!-- CUSTOM AI ANALYSIS VIEW -->
    <div class="custom-section" id="customSection">
      <div class="custom-hero-banner">
        <div class="custom-hero-title">
          <span>LG 엑사원(EXAONE) 심층 분석 &amp; 맞춤 출제</span>
        </div>
        <div class="custom-hero-desc">
          수험서 핵심 단원과 법령·기술 문서를 엑사원 모델(k-exaone_v2.5)이 분석하여 핵심 요약, 시험 빈출 함정 포인트, 그리고 법적 근거가 완비된 실전 5지선다 문제를 맞춤 생성했습니다.
        </div>
      </div>

      <div class="custom-guide-card">
        <div class="custom-guide-icon">💡</div>
        <div>
          <div class="custom-guide-title">새로운 시험 파일이나 웹 URL을 분석하고 싶으신가요?</div>
          <div class="custom-guide-text">
            상단 <strong>[➕ 새 학습자료 등록]</strong>을 누르시거나 피클 채팅창에 PDF 수험서, 웹 링크를 전달해 주시면 즉시 엑사원 AI가 이 화면에 새로운 시험 카테고리로 퀴즈를 탑재해 드립니다.
          </div>
        </div>
      </div>

      <div id="customUnitsList"></div>
    </div>

    <!-- Footer -->
    <footer>
      <p>Infosec Archive · 자격증 &amp; 시험 공부 허브</p>
      <p>개인정보관리사(CPPG) · 정보보안기사(필기/실기) · ISMS-P 인증심사원 · 엑사원 AI 맞춤 분석</p>
    </footer>

  </div>

  <script src="cppg_questions.js"></script>
  <script src="infosec_exam_data.js"></script>
  <script src="custom_study.js"></script>
  <script>
    // Theme Engine (index.html과 100% 동일한 secjobs-theme 동기화)
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
    initTheme();

    // Data Normalization Helper
    function normalizeQuestion(q) {
      if (!q) return null;
      return {
        id: q.id,
        exam: typeof q.exam === 'number' ? q.exam : 1,
        exam_name: q.exam_name || (q.exam ? `${q.exam}회 모의고사` : '모의고사'),
        subject_id: typeof q.subject_id === 'number' ? q.subject_id : 1,
        subject_name: q.subject || q.subject_name || '',
        question: q.prompt || q.question || '',
        options: q.choices || q.options || [],
        answer: typeof q.answer === 'number' ? q.answer : 1,
        explanation: q.explanation || ''
      };
    }

    // Global State
    let currentCategory = 'cppg'; // cppg | infosec_written | infosec_practical | ismsp_auditor | custom
    let currentMode = 'quiz'; // quiz | summary | custom
    let currentExam = 1;
    let currentSubj = 0;
    let wrongOnly = false;
    let userAnswers = {};

    try {
      const saved = localStorage.getItem('study_user_answers_v4');
      if (saved) userAnswers = JSON.parse(saved);
    } catch(e) {}

    function saveUserAnswers() {
      try {
        localStorage.setItem('study_user_answers_v4', JSON.stringify(userAnswers));
      } catch(e) {}
    }

    // Category Definitions
    const CATEGORIES = {
      cppg: {
        title: "개인정보관리사 (CPPG)",
        mainTitle: "CPPG 실전 300제 & 전 과목 핵심 노트",
        mainDesc: "실전 모의고사 1·2·3회 300문항 즉시 채점, 187p 전 과목 핵심 요약 및 파일/URL AI 맞춤 분석",
        quizLabel: "실전 모의고사 (300제)",
        quizLabelShort: "실전 300제",
        exams: [
          { id: 1, full: "1회 실전 모의고사 (100문항)", short: "1회 (100제)" },
          { id: 2, full: "2회 실전 모의고사 (100문항)", short: "2회 (100제)" },
          { id: 3, full: "3회 실전 모의고사 (100문항)", short: "3회 (100제)" },
          { id: 0, full: "전체 300제 집중 풀이", short: "전체 300제" }
        ],
        subjects: [
          { id: 0, name: "전체" },
          { id: 1, name: "1과목: 이해" },
          { id: 2, name: "2과목: 제도" },
          { id: 3, name: "3과목: 라이프사이클" },
          { id: 4, name: "4과목: 보호조치" },
          { id: 5, name: "5과목: 관리체계" }
        ]
      },
      infosec_written: {
        title: "정보보안기사 (필기)",
        mainTitle: "2026 이기적 정보보안기사 필기 100제 & 이론서 심층 요약",
        mainDesc: "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1회 실전(50제) · 2회 고난도 기출(50제) 총 100문항 및 1권 이론서 전 과목 요약집",
        quizLabel: "필기 모의고사 (100제)",
        quizLabelShort: "필기 100제",
        exams: [
          { id: 1, full: "1회 필기 실전 모의고사 (50문항)", short: "1회 (50제)" },
          { id: 2, full: "2회 필기 고난도 기출 (50문항)", short: "2회 (50제)" },
          { id: 0, full: "전체 100제 필기 집중 풀이", short: "전체 100제" }
        ],
        subjects: [
          { id: 0, name: "전체" },
          { id: 1, name: "1과목: 시스템" },
          { id: 2, name: "2과목: 네트워크" },
          { id: 3, name: "3과목: 애플리케이션" },
          { id: 4, name: "4과목: 정보보안 일반" },
          { id: 5, name: "5과목: 보안관리/법규" }
        ]
      },
      infosec_practical: {
        title: "정보보안기사 (실기)",
        mainTitle: "2026 이기적 정보보안기사 실기 50제 & 실무 가이드",
        mainDesc: "2026 이기적 올인원 실기 편제 기준 1회 단답형 족보(25제) · 2회 서술·실무형 침해사고 분석(25제) 총 50문항 및 실무 요약",
        quizLabel: "실기 실전 문제 (50제)",
        quizLabelShort: "실기 50제",
        exams: [
          { id: 1, full: "1회 단답형 핵심 족보 (25문항)", short: "1회 단답형 (25제)" },
          { id: 2, full: "2회 서술·실무형 분석 (25문항)", short: "2회 서술실무 (25제)" },
          { id: 0, full: "전체 50제 실기 집중 풀이", short: "전체 50제" }
        ],
        subjects: [
          { id: 0, name: "전체" },
          { id: 1, name: "1영역: 단답형" },
          { id: 2, name: "2영역: 시스템/네트워크" },
          { id: 3, name: "3영역: 시큐어코딩" },
          { id: 4, name: "4영역: 서술형/관리" }
        ]
      },
      ismsp_auditor: {
        title: "ISMS-P 인증심사원",
        mainTitle: "ISMS-P 인증심사원 실전 결함판정 퀴즈 & 102개 기준 결함사례",
        mainDesc: "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 실전 결함판정 시나리오 퀴즈(총 15문항) 및 기준별 결함 체크리스트",
        quizLabel: "인증기준 실전 퀴즈",
        quizLabelShort: "인증 퀴즈",
        exams: [
          { id: 1, full: "1회 실전 결함판정 모의고사 (15문항)", short: "1회 (15제)" },
          { id: 0, full: "전체 102개 기준 결함 풀이", short: "전체 풀이" }
        ],
        subjects: [
          { id: 0, name: "전체" },
          { id: 1, name: "1영역: 관리체계" },
          { id: 2, name: "2영역: 보호대책" },
          { id: 3, name: "3영역: 개인정보" }
        ]
      },
      custom: {
        title: "맞춤 분석 (파일·URL)",
        mainTitle: "파일·웹 URL AI 맞춤 분석 & 출제 세트",
        mainDesc: "LG 엑사원(EXAONE) AI로 분석한 핵심 요약 및 맞춤형 5지선다 실전 퀴즈",
        quizLabel: "맞춤 퀴즈 풀기",
        quizLabelShort: "맞춤 퀴즈",
        exams: [
          { id: 1, full: "엑사원 맞춤 분석 퀴즈", short: "맞춤 퀴즈" },
          { id: 0, full: "전체 맞춤 문제 풀이", short: "전체 풀이" }
        ],
        subjects: [
          { id: 0, name: "전체" }
        ]
      }
    };

    // DOM Elements
    const pageMainTitle = document.getElementById('pageMainTitle');
    const pageMainDesc = document.getElementById('pageMainDesc');
    const activeExamBadge = document.getElementById('activeExamBadge');
    const categoryBar = document.getElementById('categoryBar');
    const addResourcePanel = document.getElementById('addResourcePanel');
    const btnAddResource = document.getElementById('btnAddResource');
    const btnCloseAddPanel = document.getElementById('btnCloseAddPanel');

    const modeNavGrid = document.getElementById('modeNavGrid');
    const modeQuizBtn = document.getElementById('modeQuizBtn');
    const modeSummaryBtn = document.getElementById('modeSummaryBtn');
    const modeCustomBtn = document.getElementById('modeCustomBtn');
    const modeQuizLabel = document.getElementById('modeQuizLabel');
    const modeQuizLabelMobile = document.getElementById('modeQuizLabelMobile');

    const controlsBar = document.getElementById('controlsBar');
    const examBtnGroup = document.getElementById('examBtnGroup');
    const subjPills = document.getElementById('subjPills');
    const questionsList = document.getElementById('questionsList');
    const summarySection = document.getElementById('summarySection');
    const customSection = document.getElementById('customSection');

    // Add Resource Panel Toggle
    btnAddResource.addEventListener('click', (e) => {
      e.stopPropagation();
      addResourcePanel.classList.toggle('show');
      if (addResourcePanel.classList.contains('show')) {
        addResourcePanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
    btnCloseAddPanel.addEventListener('click', () => {
      addResourcePanel.classList.remove('show');
    });

    // Category Switching
    categoryBar.querySelectorAll('.cat-chip:not(.add-chip)').forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.getAttribute('data-cat');
        switchCategory(cat);
      });
    });

    function switchCategory(cat) {
      if (!CATEGORIES[cat]) return;
      currentCategory = cat;
      currentExam = 1;
      currentSubj = 0;

      // Update Active Category Chip
      categoryBar.querySelectorAll('.cat-chip:not(.add-chip)').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-cat') === cat);
      });

      const conf = CATEGORIES[cat];
      pageMainTitle.textContent = conf.mainTitle;
      pageMainDesc.textContent = conf.mainDesc;
      activeExamBadge.textContent = conf.title;

      // Update Mode Labels
      if (modeQuizLabel) modeQuizLabel.textContent = conf.quizLabel;
      if (modeQuizLabelMobile) modeQuizLabelMobile.textContent = conf.quizLabelShort;

      renderControls();
      updateStats();

      if (cat === 'custom') {
        switchMode('custom');
      } else {
        if (currentMode === 'custom') currentMode = 'quiz';
        switchMode(currentMode);
      }
    }

    function renderControls() {
      const conf = CATEGORIES[currentCategory];
      
      // 1. Exam buttons
      examBtnGroup.innerHTML = '';
      conf.exams.forEach(ex => {
        const btn = document.createElement('button');
        btn.className = `exam-btn ${currentExam === ex.id ? 'active' : ''}`;
        btn.innerHTML = `<span class="btn-text-full">${ex.full}</span><span class="btn-text-mobile">${ex.short}</span>`;
        btn.addEventListener('click', () => {
          currentExam = ex.id;
          renderControls();
          updateStats();
          renderQuestions();
        });
        examBtnGroup.appendChild(btn);
      });

      // 2. Subject Pills
      subjPills.innerHTML = '';
      conf.subjects.forEach(sub => {
        const pill = document.createElement('button');
        pill.className = `filter-pill ${currentSubj === sub.id ? 'active' : ''}`;
        pill.textContent = sub.name;
        pill.addEventListener('click', () => {
          currentSubj = sub.id;
          renderControls();
          renderQuestions();
        });
        subjPills.appendChild(pill);
      });
    }

    // Mode Switching
    modeNavGrid.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-mode');
        switchMode(mode);
      });
    });

    function switchMode(mode) {
      currentMode = mode;
      modeNavGrid.querySelectorAll('.mode-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-mode') === mode);
      });

      if (mode === 'quiz') {
        controlsBar.style.display = 'flex';
        questionsList.style.display = 'flex';
        summarySection.style.display = 'none';
        customSection.style.display = 'none';
        renderQuestions();
      } else if (mode === 'summary') {
        controlsBar.style.display = 'none';
        questionsList.style.display = 'none';
        summarySection.style.display = 'flex';
        customSection.style.display = 'none';
        renderSummaries();
      } else if (mode === 'custom') {
        controlsBar.style.display = 'none';
        questionsList.style.display = 'none';
        summarySection.style.display = 'none';
        customSection.style.display = 'block';
        renderCustomUnits();
      }
    }

    function getQuestionsForCurrentCategory() {
      let raw = [];
      if (currentCategory === 'cppg') {
        raw = window.ALL_QUESTIONS || [];
      } else if (currentCategory === 'infosec_written') {
        raw = (window.INFOSEC_WRITTEN_DATA && window.INFOSEC_WRITTEN_DATA.questions) || [];
      } else if (currentCategory === 'infosec_practical') {
        raw = (window.INFOSEC_PRACTICAL_DATA && window.INFOSEC_PRACTICAL_DATA.questions) || [];
      } else if (currentCategory === 'ismsp_auditor') {
        raw = (window.ISMSP_AUDITOR_DATA && window.ISMSP_AUDITOR_DATA.questions) || [];
      } else if (currentCategory === 'custom') {
        const customUnits = (window.CUSTOM_STUDY_DATA && window.CUSTOM_STUDY_DATA.units) || [];
        const flat = [];
        customUnits.forEach((u, uIdx) => {
          (u.practice_questions || []).forEach(q => {
            flat.push({
              id: q.id || `custom_${uIdx}_${q.q_index}`,
              exam: 1,
              exam_name: u.unit_title,
              subject_id: uIdx + 1,
              subject_name: u.unit_title,
              prompt: q.question,
              choices: q.options,
              answer: q.answer,
              explanation: q.explanation
            });
          });
        });
        raw = flat;
      }
      return raw.map(normalizeQuestion).filter(Boolean);
    }

    function getFilteredQuestions() {
      const all = getQuestionsForCurrentCategory();
      return all.filter(q => {
        const matchExam = currentExam === 0 || q.exam === currentExam;
        const matchSubj = currentSubj === 0 || q.subject_id === currentSubj;
        return matchExam && matchSubj;
      });
    }

    function updateStats() {
      const all = getQuestionsForCurrentCategory();
      const examQuestions = all.filter(q => currentExam === 0 || q.exam === currentExam);
      const totalCount = examQuestions.length;
      
      let solved = 0;
      let correct = 0;
      examQuestions.forEach(q => {
        if (userAnswers[q.id]) {
          solved++;
          if (userAnswers[q.id].isCorrect) correct++;
        }
      });

      const acc = solved > 0 ? Math.round((correct / solved) * 100) : 0;
      document.getElementById('topTotal').textContent = totalCount;
      document.getElementById('topSolved').textContent = solved;
      document.getElementById('topCorrect').textContent = correct;
      
      let rateText = acc + '%';
      if (totalCount >= 20 && solved >= 15) {
        rateText += acc >= 60 ? ' (합격권)' : ' (보강필요)';
      }
      document.getElementById('topRate').textContent = rateText;
    }

    const circles = ['①', '②', '③', '④', '⑤'];

    function renderQuestions() {
      let list = getFilteredQuestions();
      if (wrongOnly) {
        list = list.filter(q => userAnswers[q.id] && !userAnswers[q.id].isCorrect);
      }

      questionsList.innerHTML = '';
      if (list.length === 0) {
        questionsList.innerHTML = `
          <div style="text-align:center; padding: 48px 16px; color: var(--text-muted); background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 12px;">
            <div style="font-size:24px; margin-bottom:8px;">🔍</div>
            <div style="font-size:14px; font-weight:600;">조건에 해당하는 문제가 없습니다.</div>
            <div style="font-size:12px; margin-top:4px;">오답만 보기 필터나 과목 선택을 변경해 보세요.</div>
          </div>
        `;
        return;
      }

      list.forEach((q, idx) => {
        const uAns = userAnswers[q.id];
        const card = document.createElement('div');
        card.className = 'q-card';

        let choicesHtml = '';
        (q.options || []).forEach((optText, cIdx) => {
          const choiceNum = cIdx + 1;
          let extraClass = '';
          if (uAns) {
            if (choiceNum === q.answer) {
              extraClass = 'correct';
            } else if (uAns.selected === choiceNum && !uAns.isCorrect) {
              extraClass = 'wrong';
            }
          }

          choicesHtml += `
            <div class="choice-row ${extraClass}" onclick="handleSelectChoice('${q.id}', ${choiceNum})">
              <div class="choice-circle">${circles[cIdx] || (cIdx+1)}</div>
              <div class="choice-text">${escapeHtml(optText)}</div>
            </div>
          `;
        });

        let expShowClass = uAns ? 'show' : '';
        let isCorrect = uAns && uAns.isCorrect;
        let expHeaderClass = isCorrect ? 'correct' : 'wrong';
        let expHeaderText = isCorrect ? '✅ 정답입니다!' : '❌ 오답입니다';

        card.innerHTML = `
          <div class="q-meta">
            <span class="q-badge">${escapeHtml(q.exam_name || '')}</span>
            <span class="q-badge">${escapeHtml(q.subject_name || '')}</span>
            <span class="q-num">Q${idx + 1}</span>
          </div>
          <div class="q-prompt">${escapeHtml(q.question)}</div>
          <div class="choices-list">${choicesHtml}</div>
          <div class="exp-box ${expShowClass}" id="exp_${q.id}">
            <div class="exp-header ${expHeaderClass}">
              <span>정답: ${circles[q.answer - 1] || q.answer}</span>
              <span>${expHeaderText}</span>
            </div>
            <div>${escapeHtml(q.explanation)}</div>
          </div>
        `;

        questionsList.appendChild(card);
      });
    }

    window.handleSelectChoice = function(qid, choiceNum) {
      if (userAnswers[qid]) return; // 풀이 고정

      const all = getQuestionsForCurrentCategory();
      const q = all.find(item => item.id === qid);
      if (!q) return;

      const isCorrect = (choiceNum === q.answer);
      userAnswers[qid] = {
        selected: choiceNum,
        isCorrect: isCorrect,
        timestamp: Date.now()
      };
      saveUserAnswers();
      updateStats();
      renderQuestions();
    };

    function renderSummaries() {
      summarySection.innerHTML = '';
      
      if (currentCategory === 'cppg') {
        summarySection.innerHTML = `
          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">1과목. 개인정보보호의 이해 (배점: 10점)</div>
              <div class="summary-badge">핵심 요약</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 개인정보의 정의 및 판단 기준</div>
              <ul>
                <li><strong>개인정보:</strong> 살아있는 개인에 관한 정보로서 성명, 주민번호, 영상 등을 통해 특정 개인을 알아볼 수 있는 정보.</li>
                <li><strong>결합 식별 가능 정보:</strong> 해당 정보만으로는 알 수 없으나 다른 정보와 쉽게 결합하여 알아볼 수 있는 정보. 결합 시 '시간·비용·노력' 등 합리적 가능성을 종합 판단.</li>
                <li><strong>가명정보:</strong> 추가 정보 없이는 특정 개인을 알아볼 수 없도록 처리(가명처리)한 정보 (통계작성, 과학적 연구, 공익적 기록보존 목적 활용 가능).</li>
                <li><strong>익명정보:</strong> 다른 정보를 사용하여도 더 이상 개인을 알아볼 수 없는 정보로, 법 적용 대상에서 제외.</li>
              </ul>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 개인정보 보호 원칙 및 헌법상 권리</div>
              <ul>
                <li><strong>자기결정권:</strong> 헌법상 기본권으로서 자신에 관한 정보를 통제하고 결정할 권리.</li>
                <li><strong>최소 처리의 원칙:</strong> 처리 목적에 필요한 최소한의 범위에서 적법하고 정당하게 처리.</li>
                <li><strong>목적 외 이용 금지:</strong> 수집 목적의 범위를 초과하여 처리하거나 제3자에게 제공 금지.</li>
              </ul>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">2과목. 개인정보보호 제도 (배점: 20점)</div>
              <div class="summary-badge">핵심 요약</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 법체계 및 거버넌스</div>
              <ul>
                <li><strong>개인정보 보호위원회:</strong> 국무총리 소속 중앙행정기관으로 독립성 보장, 위원장 1인, 부위원장 1인 포함 총 9인으로 구성.</li>
                <li><strong>CPO(개인정보보호책임자) 지정:</strong> 개인정보 처리를 총괄하는 책임자 지정 의무. 정당한 이유 없이 불이익 처우 금지.</li>
                <li><strong>유출 통지 및 신고:</strong> 유출 인지 시 지체 없이 72시간 이내 정보주체에게 통지. 1천명 이상 유출 시 보호위/KISA에 즉시 신고.</li>
              </ul>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">3과목. 개인정보 라이프사이클 (배점: 25점)</div>
              <div class="summary-badge">핵심 요약</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 수집·이용·제공·파기 단계별 의무</div>
              <ul>
                <li><strong>동의 시 고지 필수 4대 사항:</strong> ① 수집·이용 목적, ② 수집 항목, ③ 보유 및 이용 기간, ④ 동의 거부권 및 불이익 내용.</li>
                <li><strong>민감정보 및 고유식별정보:</strong> 사상, 신념, 건강, 유전정보, 성생활 / 주민번호, 여권번호, 운전면허번호, 외국인등록번호는 원칙적 처리 금지(별도 동의 또는 법령 구체적 근거 시만 허용).</li>
                <li><strong>제3자 제공 vs 업무 위탁:</strong> 제3자 제공은 받는 자의 이익(별도 동의 필수), 위탁은 위탁자의 이익(계약서 문서화, 관리·감독, 수탁사 교육).</li>
                <li><strong>파기 기준:</strong> 목적 달성 시 복구 불가능한 영구 삭제(5일 이내). 법령상 보존 시 다른 개인정보와 분리 보관.</li>
              </ul>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">4과목 &amp; 5과목. 보호조치 및 관리체계 (배점: 45점)</div>
              <div class="summary-badge">핵심 요약</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 안전성 확보조치 기준 (고시)</div>
              <ul>
                <li><strong>접속기록 보관 및 점검:</strong> 최소 1년 이상 보관(5만명 이상 민감/고유식별정보 처리 시 2년). 월 1회 이상 점검.</li>
                <li><strong>암호화 의무:</strong> 고유식별정보, 비밀번호(일방향), 바이오정보. 저장 시 및 네트워크 전송 시 필수 암호화.</li>
                <li><strong>접근통제 및 비밀번호:</strong> 3종 8자리 또는 2종 10자리, 초기 비밀번호 변경 강제.</li>
                <li><strong>ISMS-P 인증기준:</strong> 관리체계 수립(16개), 보호대책 요구사항(64개), 개인정보 처리단계(22개) 총 102개 기준.</li>
              </ul>
            </div>
          </div>
        `;
      } else if (currentCategory === 'infosec_written') {
        const summaries = (window.INFOSEC_WRITTEN_DATA && window.INFOSEC_WRITTEN_DATA.summaries) || [];
        summaries.forEach(s => {
          let topicsHtml = '';
          s.topics.forEach(t => {
            let pts = '';
            t.points.forEach(p => { pts += `<li>${escapeHtml(p)}</li>`; });
            topicsHtml += `
              <div class="summary-topic">
                <div class="summary-topic-title">• ${escapeHtml(t.name)}</div>
                <ul>${pts}</ul>
              </div>
            `;
          });
          summarySection.innerHTML += `
            <div class="summary-card">
              <div class="summary-header">
                <div class="summary-title">${escapeHtml(s.title)}</div>
                <div class="summary-badge">필기 핵심요약</div>
              </div>
              ${topicsHtml}
            </div>
          `;
        });
      } else if (currentCategory === 'infosec_practical') {
        const summaries = (window.INFOSEC_PRACTICAL_DATA && window.INFOSEC_PRACTICAL_DATA.summaries) || [];
        summaries.forEach(s => {
          let topicsHtml = '';
          s.topics.forEach(t => {
            let pts = '';
            t.points.forEach(p => { pts += `<li>${escapeHtml(p)}</li>`; });
            topicsHtml += `
              <div class="summary-topic">
                <div class="summary-topic-title">• ${escapeHtml(t.name)}</div>
                <ul>${pts}</ul>
              </div>
            `;
          });
          summarySection.innerHTML += `
            <div class="summary-card">
              <div class="summary-header">
                <div class="summary-title">${escapeHtml(s.title)}</div>
                <div class="summary-badge">실기 실무족보</div>
              </div>
              ${topicsHtml}
            </div>
          `;
        });
      } else if (currentCategory === 'ismsp_auditor') {
        const summaries = (window.ISMSP_AUDITOR_DATA && window.ISMSP_AUDITOR_DATA.summaries) || [];
        summaries.forEach(s => {
          let topicsHtml = '';
          s.topics.forEach(t => {
            let pts = '';
            t.points.forEach(p => { pts += `<li>${escapeHtml(p)}</li>`; });
            topicsHtml += `
              <div class="summary-topic">
                <div class="summary-topic-title">• ${escapeHtml(t.name)}</div>
                <ul>${pts}</ul>
              </div>
            `;
          });
          summarySection.innerHTML += `
            <div class="summary-card">
              <div class="summary-header">
                <div class="summary-title">${escapeHtml(s.title)}</div>
                <div class="summary-badge">102개 기준 요약</div>
              </div>
              ${topicsHtml}
            </div>
          `;
        });
      }
    }

    function renderCustomUnits() {
      const container = document.getElementById('customUnitsList');
      container.innerHTML = '';
      const data = window.CUSTOM_STUDY_DATA;
      if (!data || !data.units || data.units.length === 0) {
        container.innerHTML = `
          <div style="text-align:center; padding: 40px; color:var(--text-muted); background:var(--bg-surface); border:1px solid var(--border-default); border-radius:12px;">
            등록된 맞춤 분석 단원이 없습니다. 상단 [➕ 새 학습자료 등록]을 이용해 보세요.
          </div>
        `;
        return;
      }

      data.units.forEach(u => {
        let keyConceptsHtml = '';
        (u.key_concepts || []).forEach(c => {
          keyConceptsHtml += `
            <div style="margin-bottom:8px;">
              <strong style="color:var(--text-primary); font-size:13px;">${escapeHtml(c.term)}:</strong>
              <span style="color:var(--text-secondary); font-size:12.5px;">${escapeHtml(c.desc)}</span>
            </div>
          `;
        });

        let trapsHtml = '';
        (u.exam_traps || []).forEach(tr => {
          trapsHtml += `<li style="font-size:12.5px; color:var(--text-secondary); line-height:1.6; margin-bottom:4px;">• ${escapeHtml(tr)}</li>`;
        });

        container.innerHTML += `
          <div class="summary-card" style="margin-bottom:16px;">
            <div class="summary-header">
              <div class="summary-title">${escapeHtml(u.unit_title)}</div>
              <div class="summary-badge">엑사원 AI 분석</div>
            </div>
            <div style="background:var(--accent-subtle); border-left:3px solid var(--accent-primary); padding:10px 12px; border-radius:4px; font-size:12.5px; line-height:1.6; margin-bottom:14px; color:var(--text-primary);">
              <strong>핵심 요약:</strong> ${escapeHtml(u.ai_summary)}
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 중요 개념 정리</div>
              <div style="padding-left:4px;">${keyConceptsHtml}</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 시험 빈출 함정 포인트</div>
              <ul style="list-style:none; padding-left:0;">${trapsHtml}</ul>
            </div>
          </div>
        `;
      });
    }

    // Tools
    const btnWrongOnly = document.getElementById('btnWrongOnly');
    btnWrongOnly.addEventListener('click', () => {
      wrongOnly = !wrongOnly;
      btnWrongOnly.classList.toggle('active', wrongOnly);
      btnWrongOnly.textContent = wrongOnly ? '전체 보기' : '오답만 보기';
      renderQuestions();
    });

    const btnReset = document.getElementById('btnReset');
    btnReset.addEventListener('click', () => {
      if (confirm('현재 시험의 풀이 기록을 모두 초기화하시겠습니까?')) {
        const qList = getQuestionsForCurrentCategory();
        qList.forEach(q => { delete userAnswers[q.id]; });
        saveUserAnswers();
        updateStats();
        renderQuestions();
      }
    });

    // Helper functions
    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    // Panel File/URL Helper
    window.setSourceType = function(type) {
      const btnFile = document.getElementById('btnSourceFile');
      const btnUrl = document.getElementById('btnSourceUrl');
      const grpFile = document.getElementById('fileInputGroup');
      const grpUrl = document.getElementById('urlInputGroup');
      if (type === 'file') {
        btnFile.classList.add('active');
        btnUrl.classList.remove('active');
        grpFile.style.display = 'block';
        grpUrl.style.display = 'none';
      } else {
        btnFile.classList.remove('active');
        btnUrl.classList.add('active');
        grpFile.style.display = 'none';
        grpUrl.style.display = 'block';
      }
    };

    window.handleFileSelect = function(e) {
      const file = e.target.files[0];
      if (file) {
        document.getElementById('dropFileName').textContent = `선택된 파일: ${file.name} (${Math.round(file.size/1024)} KB)`;
        if (!document.getElementById('newCategoryTitle').value) {
          document.getElementById('newCategoryTitle').value = file.name.replace(/\\.[^/.]+$/, "");
        }
      }
    };

    window.requestAnalysis = function() {
      const title = document.getElementById('newCategoryTitle').value.trim();
      const url = document.getElementById('studyUrlInput').value.trim();
      const fileInput = document.getElementById('studyFileInput');
      const hasFile = fileInput.files && fileInput.files.length > 0;
      
      if (!title) {
        alert('시험명 또는 카테고리 제목을 입력해 주세요.');
        return;
      }
      if (!hasFile && !url) {
        alert('분석할 문서 파일(PDF/TXT/MD)을 첨부하거나 웹 URL 링크를 입력해 주세요.');
        return;
      }

      alert(`[분석 요청 접수]\\n카테고리: ${title}\\n\\n피클 비서가 엑사원 AI를 가동하여 핵심 요약과 실전 퀴즈를 생성합니다.\\n채팅창에서도 즉시 확인하실 수 있습니다!`);
      addResourcePanel.classList.remove('show');
    };

    // Initial Load
    switchCategory('cppg');
  </script>
</body>
</html>
"""

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Successfully regenerated study.html with normalized questions and robust rendering!")

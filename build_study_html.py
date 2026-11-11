#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_study_html.py:
CPPG 300제, 정보보안기사, ISMS-P 및 파일·URL 맞춤 분석을 아우르는
'시험 공부' 통합 허브 HTML 생성 스크립트
"""

import json
import re
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'cppg_questions.json')
js_path = os.path.join(base_dir, 'cppg_questions.js')
custom_js_path = os.path.join(base_dir, 'custom_study.js')
infosec_js_path = os.path.join(base_dir, 'infosec_exam_data.js')
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
  <title>시험 공부 & 맞춤 AI 스터디 허브 | Infosec Archive</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <link rel="icon" type="image/png" href="logo.png">
  <style>
    :root {
      --bg-primary: #ffffff;
      --bg-secondary: #f8fafc;
      --bg-card: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;
      --border-color: #e2e8f0;
      --accent: #2563eb;
      --accent-soft: #eff6ff;
      --accent-hover: #1d4ed8;
      --success: #16a34a;
      --success-soft: #f0fdf4;
      --danger: #dc2626;
      --danger-soft: #fef2f2;
      --chip-bg: #f1f5f9;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.07);
    }
    [data-theme="dark"] {
      --bg-primary: #0b0f19;
      --bg-secondary: #111827;
      --bg-card: #161f30;
      --text-primary: #f8fafc;
      --text-secondary: #cbd5e1;
      --text-muted: #64748b;
      --border-color: #1e293b;
      --accent: #3b82f6;
      --accent-soft: rgba(59, 130, 246, 0.12);
      --accent-hover: #60a5fa;
      --success: #22c55e;
      --success-soft: rgba(34, 197, 94, 0.12);
      --danger: #ef4444;
      --danger-soft: rgba(239, 68, 68, 0.12);
      --chip-bg: #1e293b;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Pretendard', -apple-system, sans-serif; }
    body { background-color: var(--bg-primary); color: var(--text-primary); line-height: 1.6; min-height: 100vh; }
    
    .navbar { position: sticky; top: 0; z-index: 50; background: var(--bg-primary); border-bottom: 1px solid var(--border-color); backdrop-filter: blur(8px); }
    .nav-container { max-width: 1100px; margin: 0 auto; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; }
    .nav-left { display: flex; align-items: center; gap: 16px; }
    .nav-brand { display: flex; align-items: center; gap: 10px; text-decoration: none; color: var(--text-primary); }
    .brand-logo-img { width: 32px; height: 32px; border-radius: 8px; }
    .brand-name { font-weight: 700; font-size: 17px; }
    .nav-tabs { display: flex; gap: 6px; }
    .nav-tab-item { padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; text-decoration: none; color: var(--text-secondary); transition: all 0.2s; }
    .nav-tab-item:hover { background: var(--chip-bg); color: var(--text-primary); }
    .nav-tab-item.active { background: var(--accent); color: #ffffff !important; }
    .nav-right { display: flex; align-items: center; gap: 10px; }
    .theme-btn { background: none; border: 1px solid var(--border-color); border-radius: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: var(--text-secondary); cursor: pointer; }
    
    .main-wrap { max-width: 1000px; margin: 0 auto; padding: 28px 20px 80px; }
    .hero { margin-bottom: 20px; text-align: center; }
    .hero-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: var(--accent-soft); color: var(--accent); font-size: 12px; font-weight: 600; border-radius: 20px; margin-bottom: 10px; }
    .hero-title { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 6px; }
    .hero-desc { font-size: 14px; color: var(--text-secondary); }

    /* Category Bar */
    .category-section { margin-bottom: 20px; }
    .category-label { font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
    .category-bar { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
    .category-bar::-webkit-scrollbar { display: none; }
    .cat-chip { flex-shrink: 0; padding: 8px 16px; border-radius: 22px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-secondary); font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s ease; display: inline-flex; align-items: center; gap: 6px; user-select: none; }
    .cat-chip:hover { border-color: var(--accent); color: var(--accent); }
    .cat-chip.active { background: var(--accent); color: #ffffff; border-color: var(--accent); box-shadow: 0 2px 6px rgba(37,99,235,0.25); }
    .cat-chip.add-chip { border-style: dashed; background: var(--chip-bg); }
    .cat-chip.add-chip:hover { border-color: var(--accent); }

    /* Add Resource Panel */
    .add-resource-panel { display: none; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 22px; margin-bottom: 24px; box-shadow: var(--shadow-sm); animation: fadeIn 0.2s ease; }
    .add-resource-panel.open { display: block; }
    .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
    .panel-title { font-size: 16px; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 8px; }
    .panel-close { background: none; border: none; font-size: 18px; color: var(--text-muted); cursor: pointer; padding: 4px; }
    .panel-form { display: flex; flex-direction: column; gap: 14px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-label { font-size: 13px; font-weight: 600; color: var(--text-primary); }
    .form-input { padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-primary); color: var(--text-primary); font-size: 13px; outline: none; }
    .form-input:focus { border-color: var(--accent); }
    
    .source-type-selector { display: flex; gap: 8px; }
    .source-type-btn { flex: 1; padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--chip-bg); color: var(--text-secondary); font-size: 12.5px; font-weight: 600; cursor: pointer; text-align: center; }
    .source-type-btn.active { background: var(--accent-soft); color: var(--accent); border-color: var(--accent); }
    
    .drop-zone { border: 2px dashed var(--border-color); border-radius: 10px; padding: 24px; text-align: center; cursor: pointer; transition: all 0.15s; background: var(--bg-secondary); }
    .drop-zone:hover { border-color: var(--accent); background: var(--accent-soft); }
    .drop-icon { font-size: 28px; margin-bottom: 6px; }
    .drop-text { font-size: 13px; color: var(--text-secondary); font-weight: 500; }
    .drop-hint { font-size: 11.5px; color: var(--text-muted); margin-top: 4px; }
    
    .panel-options { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 4px; }
    .option-check { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); cursor: pointer; }
    .submit-btn { padding: 11px 16px; border-radius: 8px; border: none; background: var(--accent); color: #ffffff; font-size: 13.5px; font-weight: 700; cursor: pointer; transition: background 0.15s; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 6px; }
    .submit-btn:hover { background: var(--accent-hover); }
    .panel-quick-guide { margin-top: 14px; padding: 12px 14px; border-radius: 8px; background: var(--accent-soft); border-left: 3px solid var(--accent); font-size: 12.5px; color: var(--accent); line-height: 1.5; }

    /* Stats Grid */
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
    .stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; text-align: center; }
    .stat-label { font-size: 12px; color: var(--text-muted); font-weight: 500; margin-bottom: 4px; }
    .stat-val { font-size: 22px; font-weight: 800; color: var(--text-primary); }
    .stat-val.accent { color: var(--accent); }

    /* Mode Tabs */
    .mode-tabs {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
      max-width: 680px;
      margin: 0 auto 20px;
      background: var(--chip-bg);
      padding: 4px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
    }
    .mode-btn {
      padding: 9px 8px;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      white-space: nowrap;
      user-select: none;
    }
    .mode-btn:hover { color: var(--text-primary); }
    .mode-btn.active {
      background: var(--bg-card);
      color: var(--text-primary);
      box-shadow: var(--shadow-sm);
      font-weight: 700;
    }
    .mode-label-short { display: none; }
    .mode-label-full { display: inline; }

    /* Exam Tabs */
    .exam-tabs {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-bottom: 16px;
    }
    .exam-tab {
      padding: 9px 8px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-secondary);
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      text-align: center;
      white-space: nowrap;
      user-select: none;
    }
    .exam-tab:hover {
      border-color: var(--accent);
      color: var(--accent);
    }
    .exam-tab.active {
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
      box-shadow: 0 2px 4px rgba(37,99,235,0.2);
    }
    .exam-label-short { display: none; }
    .exam-label-full { display: inline; }

    /* Controls Bar */
    .controls-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 20px;
    }
    .subj-filters {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 4px;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      flex: 1;
    }
    .subj-filters::-webkit-scrollbar { display: none; }
    .subj-chip {
      flex-shrink: 0;
      padding: 6px 12px;
      border-radius: 16px;
      border: 1px solid var(--border-color);
      background: var(--chip-bg);
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
      white-space: nowrap;
    }
    .subj-chip.active {
      background: var(--accent-soft);
      color: var(--accent);
      border-color: var(--accent);
      font-weight: 700;
    }

    .tools-wrap { display: flex; gap: 6px; flex-shrink: 0; }
    .tool-btn {
      padding: 6px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
    }
    .tool-btn:hover { color: var(--text-primary); border-color: var(--border-strong); }
    .tool-btn.active { background: var(--danger-soft); color: var(--danger); border-color: var(--danger); }

    /* Questions List */
    .questions-list { display: flex; flex-direction: column; gap: 16px; }
    .q-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; box-shadow: var(--shadow-sm); }
    .q-meta { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
    .q-badge-wrap { display: flex; gap: 6px; }
    .q-exam-badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: var(--chip-bg); color: var(--text-secondary); font-weight: 600; }
    .q-subj-badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: var(--accent-soft); color: var(--accent); font-weight: 600; }
    .q-index { font-size: 13px; font-weight: 700; color: var(--text-muted); }

    .q-prompt { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 16px; line-height: 1.6; }
    .q-choices { display: flex; flex-direction: column; gap: 8px; }
    .choice-row {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 12px 14px;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      background: var(--bg-secondary);
      cursor: pointer;
      transition: all 0.15s;
      font-size: 13.5px;
      line-height: 1.5;
      word-break: keep-all;
      overflow-wrap: break-word;
    }
    .choice-row:hover:not(.disabled) { border-color: var(--accent); background: var(--accent-soft); }
    .choice-circle {
      flex-shrink: 0;
      width: 22px;
      height: 22px;
      margin-top: 1px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11.5px;
      font-weight: 700;
      background: var(--chip-bg);
      color: var(--text-secondary);
    }
    
    .choice-row.correct { border-color: var(--success); background: var(--success-soft); color: var(--success); font-weight: 600; }
    .choice-row.correct .choice-circle { background: var(--success); color: #fff; }
    .choice-row.wrong { border-color: var(--danger); background: var(--danger-soft); color: var(--danger); }
    .choice-row.wrong .choice-circle { background: var(--danger); color: #fff; }
    .choice-row.disabled { cursor: default; }

    .exp-panel { margin-top: 12px; padding: 14px; border-radius: 8px; background: var(--chip-bg); font-size: 13px; line-height: 1.5; }
    .exp-title { font-weight: 700; color: var(--accent); margin-bottom: 4px; }
    .exp-body { color: var(--text-secondary); white-space: pre-wrap; }

    /* Summary section */
    .summary-section { display: none; flex-direction: column; gap: 20px; }
    .summary-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; box-shadow: var(--shadow-sm); }
    .summary-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 16px; }
    .summary-title { font-size: 18px; font-weight: 700; color: var(--text-primary); }
    .summary-badge { font-size: 12px; padding: 3px 10px; border-radius: 12px; background: var(--accent-soft); color: var(--accent); font-weight: 600; }
    .summary-topic { margin-bottom: 16px; }
    .summary-topic-title { font-size: 14.5px; font-weight: 700; color: var(--accent); margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
    .summary-topic ul { list-style: none; padding-left: 0; }
    .summary-topic li { font-size: 13.5px; color: var(--text-secondary); margin-bottom: 6px; line-height: 1.5; padding-left: 14px; position: relative; }
    .summary-topic li::before { content: "•"; position: absolute; left: 0; color: var(--accent); font-weight: bold; }
    .summary-topic table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 12.5px; }
    .summary-topic th, .summary-topic td { border: 1px solid var(--border-color); padding: 8px 10px; text-align: left; }
    .summary-topic th { background: var(--chip-bg); font-weight: 600; color: var(--text-primary); }

    /* Custom AI Analysis Tab */
    .custom-section { display: none; flex-direction: column; gap: 20px; }
    .custom-hero-banner { background: linear-gradient(135deg, rgba(37,99,235,0.08) 0%, rgba(99,102,241,0.08) 100%); border: 1px solid rgba(37,99,235,0.2); border-radius: 12px; padding: 20px; margin-bottom: 8px; }
    .custom-hero-title { font-size: 17px; font-weight: 800; color: var(--accent); margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
    .custom-hero-desc { font-size: 13.5px; color: var(--text-secondary); line-height: 1.55; }
    .custom-guide-card { background: var(--bg-card); border: 1px dashed var(--accent); border-radius: 12px; padding: 18px 20px; display: flex; align-items: flex-start; gap: 14px; margin-bottom: 12px; }
    .custom-guide-icon { font-size: 24px; flex-shrink: 0; }
    .custom-guide-title { font-size: 14.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
    .custom-guide-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
    .custom-unit-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 22px; box-shadow: var(--shadow-sm); }
    .custom-unit-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
    .custom-unit-title { font-size: 17px; font-weight: 800; color: var(--text-primary); margin-bottom: 4px; }
    .custom-unit-meta { font-size: 12px; color: var(--text-muted); }
    .custom-takeaways { background: var(--bg-secondary); border-left: 3px solid var(--accent); border-radius: 0 8px 8px 0; padding: 12px 14px; margin-bottom: 14px; }
    .custom-takeaways-title { font-size: 12.5px; font-weight: 700; color: var(--accent); margin-bottom: 6px; }
    .custom-takeaways li { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; list-style: none; position: relative; padding-left: 12px; }
    .custom-takeaways li::before { content: "-"; position: absolute; left: 0; color: var(--accent); font-weight: bold; }
    .custom-terms-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px; margin-bottom: 16px; }
    .custom-term-card { background: var(--chip-bg); border-radius: 8px; padding: 10px 12px; font-size: 12.5px; }
    .custom-term-name { font-weight: 700; color: var(--text-primary); margin-bottom: 3px; }
    .custom-term-desc { color: var(--text-secondary); line-height: 1.45; }
    .custom-traps { background: var(--danger-soft); border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; }
    .custom-traps-title { font-size: 12px; font-weight: 700; color: var(--danger); margin-bottom: 4px; }
    .custom-traps li { font-size: 12.5px; color: var(--text-secondary); list-style: none; margin-bottom: 3px; }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

    @media (max-width: 640px) {
      .nav-container { padding: 8px 12px; }
      .nav-left { gap: 8px; }
      .brand-name { font-size: 14px; }
      .brand-logo-img { width: 24px; height: 24px; }
      .nav-tabs { gap: 4px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; }
      .theme-btn { width: 30px; height: 30px; font-size: 11px; }

      .main-wrap { padding: 16px 12px 60px; }
      .hero { margin-bottom: 14px; }
      .hero-pill { font-size: 11px; padding: 3px 10px; margin-bottom: 6px; }
      .hero-title { font-size: 19px; }
      .hero-desc { font-size: 12.5px; }

      .category-section { margin-bottom: 16px; }
      .cat-chip { padding: 7px 13px; font-size: 12px; }

      .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 16px; }
      .stat-card { padding: 10px 6px; }
      .stat-val { font-size: 18px; }

      .mode-tabs { gap: 3px; padding: 3px; margin-bottom: 16px; }
      .mode-btn { padding: 8px 4px; font-size: 12px; gap: 4px; }
      .mode-label-full { display: none; }
      .mode-label-short { display: inline; }

      .exam-tabs { grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 12px; }
      .exam-tab { padding: 8px 6px; font-size: 12px; }
      .exam-label-full { display: none; }
      .exam-label-short { display: inline; }

      .controls-bar { flex-direction: column; align-items: stretch; gap: 8px; margin-bottom: 14px; }
      .subj-filters { padding-bottom: 2px; }
      .subj-chip { padding: 5px 10px; font-size: 11.5px; }
      .tools-wrap { justify-content: flex-end; gap: 6px; }
      .tool-btn { padding: 5px 10px; font-size: 11px; }

      .q-card { padding: 16px 12px; }
      .q-prompt { font-size: 14px; margin-bottom: 12px; }
      .choice-row { padding: 9px 10px; font-size: 12.5px; gap: 8px; }
      .choice-circle { width: 20px; height: 20px; font-size: 11px; }
    }
  </style>
</head>
<body>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-left">
        <a href="index.html" class="nav-brand">
          <img src="logo.png" alt="Infosec Archive" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
        <div class="nav-tabs">
          <a href="index.html" class="nav-tab-item">보안 채용공고</a>
          <a href="study.html" class="nav-tab-item active">시험 공부</a>
        </div>
      </div>
      <div class="nav-right">
        <button class="theme-btn" id="btnTheme" title="테마 전환">🌓</button>
      </div>
    </div>
  </nav>

  <div class="main-wrap">
    <div class="hero">
      <div class="hero-pill">📚 IT·보안 자격증 & 시험 공부 허브</div>
      <h1 class="hero-title" id="pageMainTitle">시험 공부 & 맞춤 AI 스터디 허브</h1>
      <p class="hero-desc" id="pageMainDesc">자격증별 실전 기출·모의고사 즉시 채점, 핵심 요약노트 및 파일/URL 맞춤 분석</p>
    </div>

    <!-- Exam Category Selector -->
    <div class="category-section">
      <div class="category-label">
        <span>시험 종목 / 학습 카테고리</span>
        <span id="activeExamBadge" style="color:var(--accent);">📜 개인정보관리사(CPPG)</span>
      </div>
      <div class="category-bar" id="categoryBar">
        <button class="cat-chip active" data-cat="cppg">📜 개인정보관리사 (CPPG)</button>
        <button class="cat-chip" data-cat="infosec_written">🛡️ 정보보안기사 (필기)</button>
        <button class="cat-chip" data-cat="infosec_practical">⚔️ 정보보안기사 (실기)</button>
        <button class="cat-chip" data-cat="ismsp_auditor">🔒 ISMS-P 인증심사원</button>
        <button class="cat-chip" data-cat="custom">🔬 파일·URL 맞춤 분석</button>
        <button class="cat-chip add-chip" id="btnAddResource" data-cat="add_new">➕ 새 학습자료 등록</button>
      </div>
    </div>

    <!-- Add Resource Panel (파일 및 URL 첨부하여 카테고리 생성) -->
    <div class="add-resource-panel" id="addResourcePanel">
      <div class="panel-header">
        <div class="panel-title">
          <span>📥</span>
          <span>새 학습자료(파일/URL) 분석 &amp; 새 카테고리 등록</span>
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
            <button type="button" class="source-type-btn active" id="btnSourceFile" onclick="setSourceType('file')">📄 문서 파일 (PDF / TXT / MD)</button>
            <button type="button" class="source-type-btn" id="btnSourceUrl" onclick="setSourceType('url')">🔗 웹 링크 (URL)</button>
          </div>
        </div>

        <div class="form-group" id="fileInputGroup">
          <label class="form-label">문서 파일 첨부</label>
          <input type="file" id="studyFileInput" accept=".pdf,.txt,.md,.json" style="display:none;" onchange="handleFileSelect(event)">
          <div class="drop-zone" id="dropZone" onclick="document.getElementById('studyFileInput').click()">
            <div class="drop-icon">📁</div>
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
          <span>🚀</span>
          <span>엑사원 AI 분석 &amp; 카테고리 퀴즈 생성</span>
        </button>

        <div class="panel-quick-guide">
          <strong>💡 피클 비서 연동 안내:</strong><br>
          피클 채팅창에 직접 PDF 수험서나 공부할 웹 URL 링크를 첨부해 주시면, 엑사원 AI가 전체 텍스트를 정밀 파싱하여 이 화면 상단 카테고리에 새 시험 탭으로 자동 생성하고 배포해 드립니다!
        </div>
      </div>
    </div>

    <!-- Stats -->
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
        <div class="stat-val accent" id="topRate">0%</div>
      </div>
    </div>

    <!-- Mode Tabs: 실전 퀴즈 / 요약노트 / 맞춤 AI -->
    <div class="mode-tabs">
      <button class="mode-btn active" id="btnModeQuiz" onclick="switchMode('quiz')">
        <span class="mode-icon">📝</span>
        <span class="mode-label-full" id="lblModeQuiz">실전 모의고사 (300제)</span>
        <span class="mode-label-short" id="lblModeQuizShort">실전 300제</span>
      </button>
      <button class="mode-btn" id="btnModeSummary" onclick="switchMode('summary')">
        <span class="mode-icon">📖</span>
        <span class="mode-label-full">전 과목 핵심 요약노트</span>
        <span class="mode-label-short">핵심노트</span>
      </button>
      <button class="mode-btn" id="btnModeCustom" onclick="switchMode('custom')">
        <span class="mode-icon">🔬</span>
        <span class="mode-label-full">맞춤 AI 분석 &amp; 퀴즈</span>
        <span class="mode-label-short">맞춤 AI</span>
      </button>
    </div>

    <!-- QUIZ VIEW -->
    <div id="quizSection">
      <!-- Exam Selector -->
      <div class="exam-tabs" id="examTabsContainer">
        <button class="exam-tab active" data-exam="1">
          <span class="exam-label-full">1회 실전 모의고사 (100문항)</span>
          <span class="exam-label-short">1회 (100제)</span>
        </button>
        <button class="exam-tab" data-exam="2">
          <span class="exam-label-full">2회 실전 모의고사 (100문항)</span>
          <span class="exam-label-short">2회 (100제)</span>
        </button>
        <button class="exam-tab" data-exam="3">
          <span class="exam-label-full">3회 실전 모의고사 (100문항)</span>
          <span class="exam-label-short">3회 (100제)</span>
        </button>
        <button class="exam-tab" data-exam="0">
          <span class="exam-label-full">전체 300제 집중 풀이</span>
          <span class="exam-label-short">전체 300제</span>
        </button>
      </div>

      <!-- Controls & Filter -->
      <div class="controls-bar">
        <div class="subj-filters" id="subjFiltersContainer">
          <div class="subj-chip active" data-subj="0">전체</div>
          <div class="subj-chip" data-subj="1">1과목: 이해</div>
          <div class="subj-chip" data-subj="2">2과목: 제도</div>
          <div class="subj-chip" data-subj="3">3과목: 라이프사이클</div>
          <div class="subj-chip" data-subj="4">4과목: 보호조치</div>
          <div class="subj-chip" data-subj="5">5과목: 관리체계</div>
        </div>
        <div class="tools-wrap">
          <button class="tool-btn" id="btnWrongOnly">오답만 보기</button>
          <button class="tool-btn" id="btnReset">풀이 초기화</button>
        </div>
      </div>

      <!-- Questions Container -->
      <div class="questions-list" id="questionsContainer"></div>
    </div>

    <!-- SUMMARY VIEW -->
    <div class="summary-section" id="summarySection">
      <!-- Dynamic summary cards loaded here -->
    </div>

    <!-- CUSTOM AI ANALYSIS VIEW -->
    <div class="custom-section" id="customSection">
      <div class="custom-hero-banner">
        <div class="custom-hero-title">
          <span>🔬</span>
          <span>LG 엑사원(EXAONE) AI 심층 분석 &amp; 맞춤 출제</span>
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

  </div>

  <script src="cppg_questions.js"></script>
  <script src="infosec_exam_data.js"></script>
  <script src="custom_study.js"></script>
  <script>
    // Theme
    const btnTheme = document.getElementById('btnTheme');
    const root = document.documentElement;
    let isDark = localStorage.getItem('theme') === 'dark';
    function applyTheme() {
      root.setAttribute('data-theme', isDark ? 'dark' : 'light');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
    applyTheme();
    btnTheme.addEventListener('click', () => {
      isDark = !isDark;
      applyTheme();
    });

    // Global State
    let currentCategory = 'cppg'; // cppg | infosec_engineer | ismsp_auditor | custom
    let currentMode = 'quiz'; // quiz | summary | custom
    let currentExam = 1;
    let currentSubj = 0;
    let wrongOnly = false;
    let userAnswers = {};

    try {
      const saved = localStorage.getItem('study_user_answers_v3');
      if (saved) userAnswers = JSON.parse(saved);
    } catch(e) {}

    function saveUserAnswers() {
      try {
        localStorage.setItem('study_user_answers_v3', JSON.stringify(userAnswers));
      } catch(e) {}
    }

    // Category Definitions
    const CATEGORIES = {
      cppg: {
        title: "📜 개인정보관리사(CPPG)",
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
        title: "🛡️ 정보보안기사(필기)",
        mainTitle: "정보보안기사 필기 기출 모의고사 & 5대 과목 핵심요약",
        mainDesc: "시스템·네트워크·애플리케이션·정보보안일반·법규 5대 전 과목 핵심 기출 모의고사(총 50문항) 및 상세 해설",
        quizLabel: "필기 모의고사",
        quizLabelShort: "필기 퀴즈",
        exams: [
          { id: 1, full: "1회 필기 실전 모의고사 (25문항)", short: "1회 (25제)" },
          { id: 2, full: "2회 필기 고난도 모의고사 (25문항)", short: "2회 (25제)" },
          { id: 0, full: "전체 50제 필기 집중 풀이", short: "전체 50제" }
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
        title: "⚔️ 정보보안기사(실기)",
        mainTitle: "정보보안기사 실기 단답형·서술형 족보 & 실무 가이드",
        mainDesc: "단답형 핵심 명령어 · 시스템/네트워크 실무 설정 · 시큐어코딩 진단 · 법규 서술형 모범 답안 (총 30문항)",
        quizLabel: "실기 실전 문제",
        quizLabelShort: "실기 문제",
        exams: [
          { id: 1, full: "1회 단답형 핵심 족보 (15문항)", short: "1회 단답형" },
          { id: 2, full: "2회 서술·실무형 분석 (15문항)", short: "2회 서술실무" },
          { id: 0, full: "전체 30제 실기 집중 풀이", short: "전체 30제" }
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
        title: "🔒 ISMS-P 인증심사원",
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
        title: "🔬 맞춤 분석 (파일·URL)",
        mainTitle: "파일·웹 URL AI 맞춤 분석 & 출제 세트",
        mainDesc: "첨부 문서와 웹 문서를 엑사원 AI로 분석한 핵심 서머리와 실전 모의고사",
        quizLabel: "맞춤 퀴즈 풀이",
        quizLabelShort: "맞춤 퀴즈",
        exams: [
          { id: 1, full: "맞춤 분석 1차 세트", short: "1차 세트" },
          { id: 0, full: "전체 맞춤 퀴즈 풀이", short: "전체 풀이" }
        ],
        subjects: [
          { id: 0, name: "전체" },
          { id: 1, name: "PIA 영향평가" },
          { id: 2, name: "72h 유출통지" },
          { id: 3, name: "안전성확보조치" }
        ]
      }
    };

    // Category Tabs Click
    const categoryBar = document.getElementById('categoryBar');
    const catChips = categoryBar.querySelectorAll('.cat-chip');
    const activeExamBadge = document.getElementById('activeExamBadge');
    const addResourcePanel = document.getElementById('addResourcePanel');

    catChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const catKey = chip.getAttribute('data-cat');
        if (catKey === 'add_new') {
          addResourcePanel.classList.toggle('open');
          if (addResourcePanel.classList.contains('open')) {
            addResourcePanel.scrollIntoView({ behavior: 'smooth' });
          }
          return;
        }

        catChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentCategory = catKey;
        activeExamBadge.textContent = CATEGORIES[catKey].title;
        currentExam = 1;
        currentSubj = 0;
        wrongOnly = false;
        
        // Hide panel if open
        addResourcePanel.classList.remove('open');

        updateCategoryUI();
      });
    });

    document.getElementById('btnCloseAddPanel').addEventListener('click', () => {
      addResourcePanel.classList.remove('open');
    });

    function setSourceType(type) {
      document.getElementById('btnSourceFile').classList.toggle('active', type === 'file');
      document.getElementById('btnSourceUrl').classList.toggle('active', type === 'url');
      document.getElementById('fileInputGroup').style.display = type === 'file' ? 'flex' : 'none';
      document.getElementById('urlInputGroup').style.display = type === 'url' ? 'flex' : 'none';
    }

    function handleFileSelect(e) {
      const file = e.target.files[0];
      if (file) {
        document.getElementById('dropFileName').textContent = `선택된 파일: ${file.name} (${Math.round(file.size / 1024)} KB)`;
        if (!document.getElementById('newCategoryTitle').value) {
          document.getElementById('newCategoryTitle').value = file.name.replace(/\\.[^/.]+$/, "");
        }
      }
    }

    function requestAnalysis() {
      const title = document.getElementById('newCategoryTitle').value.trim() || '새 맞춤 학습자료';
      alert(`[분석 요청 접수]\\n\\n'${title}' 자료의 AI 분석 요청이 접수되었습니다!\\n피클 채팅창에 해당 파일이나 웹 URL을 공유해 주시면 엑사원 AI가 실전 문제와 요약노트로 추출하여 이 화면 상단에 새 카테고리로 정식 배포해 드립니다.`);
      addResourcePanel.classList.remove('open');
    }

    function updateCategoryUI() {
      const catConfig = CATEGORIES[currentCategory];
      document.getElementById('pageMainTitle').textContent = catConfig.mainTitle;
      document.getElementById('pageMainDesc').textContent = catConfig.mainDesc;
      document.getElementById('lblModeQuiz').textContent = catConfig.quizLabel;
      document.getElementById('lblModeQuizShort').textContent = catConfig.quizLabelShort;

      // Render Exam Tabs
      const examContainer = document.getElementById('examTabsContainer');
      examContainer.innerHTML = '';
      catConfig.exams.forEach((ex, idx) => {
        const btn = document.createElement('button');
        btn.className = 'exam-tab' + (ex.id === currentExam ? ' active' : '');
        btn.setAttribute('data-exam', ex.id);
        btn.innerHTML = `<span class="exam-label-full">${ex.full}</span><span class="exam-label-short">${ex.short}</span>`;
        btn.addEventListener('click', () => {
          examContainer.querySelectorAll('.exam-tab').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentExam = ex.id;
          updateStats();
          renderQuestions();
        });
        examContainer.appendChild(btn);
      });

      // Render Subj Chips
      const subjContainer = document.getElementById('subjFiltersContainer');
      subjContainer.innerHTML = '';
      catConfig.subjects.forEach(sub => {
        const chip = document.createElement('div');
        chip.className = 'subj-chip' + (sub.id === currentSubj ? ' active' : '');
        chip.setAttribute('data-subj', sub.id);
        chip.textContent = sub.name;
        chip.addEventListener('click', () => {
          subjContainer.querySelectorAll('.subj-chip').forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
          currentSubj = sub.id;
          renderQuestions();
        });
        subjContainer.appendChild(chip);
      });

      // Render Summary View
      renderCategorySummary();

      updateStats();
      renderQuestions();
    }

    function getQuestionsForCurrentCategory() {
      if (currentCategory === 'cppg') {
        return window.ALL_QUESTIONS || [];
      } else if (currentCategory === 'infosec_written') {
        return (window.INFOSEC_WRITTEN_DATA && window.INFOSEC_WRITTEN_DATA.questions) || [];
      } else if (currentCategory === 'infosec_practical') {
        return (window.INFOSEC_PRACTICAL_DATA && window.INFOSEC_PRACTICAL_DATA.questions) || [];
      } else if (currentCategory === 'ismsp_auditor') {
        return (window.ISMSP_AUDITOR_DATA && window.ISMSP_AUDITOR_DATA.questions) || [];
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
              question: q.question,
              options: q.options,
              answer: q.answer,
              explanation: q.explanation
            });
          });
        });
        return flat;
      }
      return [];
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
      const container = document.getElementById('questionsContainer');
      container.innerHTML = '';
      const list = getFilteredQuestions();

      let displayedCount = 0;
      list.forEach((q, idx) => {
        const ans = userAnswers[q.id];
        if (wrongOnly && (!ans || ans.isCorrect)) return;

        displayedCount++;
        const card = document.createElement('div');
        card.className = 'q-card';
        card.id = 'q_' + q.id;

        const isAnswered = !!ans;
        const userChoice = ans ? ans.choice : null;
        const isCorrect = ans ? ans.isCorrect : false;

        let choicesHtml = '';
        (q.options || []).forEach((opt, oIdx) => {
          const choiceNum = oIdx + 1;
          let rowClass = 'choice-row';
          if (isAnswered) {
            rowClass += ' disabled';
            if (choiceNum === q.answer) {
              rowClass += ' correct';
            } else if (choiceNum === userChoice && !isCorrect) {
              rowClass += ' wrong';
            }
          }
          choicesHtml += `
            <div class="${rowClass}" data-qid="${q.id}" data-choice="${choiceNum}">
              <div class="choice-circle">${circles[oIdx] || choiceNum}</div>
              <div class="choice-text">${escapeHtml(opt)}</div>
            </div>
          `;
        });

        let expHtml = '';
        if (isAnswered) {
          expHtml = `
            <div class="exp-panel">
              <div class="exp-title">정답: ${circles[q.answer - 1] || q.answer} ${isCorrect ? '✅ 정답입니다!' : '❌ 오답입니다'}</div>
              <div class="exp-body">${escapeHtml(q.explanation || '해설이 준비되어 있습니다.')}</div>
            </div>
          `;
        }

        card.innerHTML = `
          <div class="q-meta">
            <div class="q-badge-wrap">
              <span class="q-exam-badge">${escapeHtml(q.exam_name || (q.exam + '회 모의고사'))}</span>
              <span class="q-subj-badge">${escapeHtml(q.subject_name || (q.subject_id + '과목'))}</span>
            </div>
            <div class="q-index">Q${idx + 1}</div>
          </div>
          <div class="q-prompt">${escapeHtml(q.question)}</div>
          <div class="q-choices">${choicesHtml}</div>
          ${expHtml}
        `;

        card.querySelectorAll('.choice-row').forEach(row => {
          row.addEventListener('click', () => {
            if (userAnswers[q.id]) return;
            const chosen = parseInt(row.getAttribute('data-choice'), 10);
            const correct = chosen === q.answer;
            userAnswers[q.id] = { choice: chosen, isCorrect: correct };
            saveUserAnswers();
            updateStats();
            renderQuestions();
          });
        });

        container.appendChild(card);
      });

      if (displayedCount === 0) {
        container.innerHTML = `
          <div style="text-align:center; padding: 40px 20px; color: var(--text-muted); font-size: 14px;">
            ${wrongOnly ? '오답으로 체크된 문항이 없습니다. 🎉' : '선택한 조건에 해당하는 문항이 없습니다.'}
          </div>
        `;
      }
    }

    function renderCategorySummary() {
      const summaryContainer = document.getElementById('summarySection');
      summaryContainer.innerHTML = '';

      if (currentCategory === 'cppg') {
        summaryContainer.innerHTML = `
          <!-- 1과목 -->
          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">1과목. 개인정보보호의 이해</div>
              <div class="summary-badge">출제 10문항 (배점 10점)</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 개인정보의 법적 정의 및 식별가능성 판단 기준</div>
              <ul>
                <li><strong>정의 3요소:</strong> ① 살아있는 개인에 관한 정보, ② 성명·주민번호·영상 등을 통해 특정 개인을 알아볼 수 있는 정보, ③ 해당 정보만으로는 알 수 없더라도 다른 정보와 쉽게 결합하여 알아볼 수 있는 정보.</li>
                <li><strong>정보주체 범위:</strong> 원칙적으로 생존하는 자연인에 한정. 법인·단체·사망자·사물 정보는 개인정보가 아님.</li>
                <li><strong>가명정보 vs 익명정보:</strong> 가명정보는 통계작성, 과학적 연구 등 목적으로 동의 없이 처리 가능하나 재식별 행위는 절대 금지. 익명정보는 개인정보 보호법 적용 전면 배제.</li>
              </ul>
            </div>
          </div>
          <!-- 2과목 -->
          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">2과목. 개인정보보호 제도</div>
              <div class="summary-badge">출제 20문항 (배점 20점)</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• CPO(개인정보 보호책임자) 의무 및 자격요건</div>
              <ul>
                <li><strong>역할:</strong> 개인정보 보호 계획 수립·시행, 처리실태 조사 및 개선 권고, 불만처리 및 피해구제, 파일 등록·관리 등 총괄.</li>
                <li><strong>배상책임:</strong> 손해액의 최대 5배까지 징벌적 손해배상 청구 가능. 보험/공제 가입 의무(매출 10억 이상 or 이용자 1만명 이상).</li>
              </ul>
            </div>
          </div>
          <!-- 3과목 -->
          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">3과목. 개인정보 라이프사이클 관리</div>
              <div class="summary-badge">출제 25문항 (배점 25점)</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 수집·이용·제공·위탁·파기 전 과정</div>
              <ul>
                <li><strong>필수 동의 4대 고지사항:</strong> ① 수집·이용 목적, ② 수집 항목, ③ 보유 및 이용 기간, ④ 동의 거부권 및 거부 시 불이익.</li>
                <li><strong>제3자 제공 vs 위탁:</strong> 제3자 제공은 제공받는 자의 이익을 위한 것이며 별도 동의 필수. 위탁은 위탁자의 업무 목적 달성을 위한 것이며 동의 대신 처리방침 공개 가능.</li>
                <li><strong>파기 원칙:</strong> 목적 달성 시 지체 없이 5일 이내 파기. 영구 삭제(소각, 디가우징, 덮어쓰기).</li>
              </ul>
            </div>
          </div>
          <!-- 4과목 -->
          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">4과목. 개인정보의 보호조치</div>
              <div class="summary-badge">출제 30문항 (배점 30점 - 최다)</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• 기술적·관리적·물리적 안전성 확보조치 기준</div>
              <ul>
                <li><strong>접속기록 관리:</strong> 최소 1년 보관 (5만명 이상 민감/고유식별정보 처리 시스템은 2년 보관), 월 1회 이상 점검.</li>
                <li><strong>암호화 의무:</strong> 비밀번호는 일방향 암호화(SHA-256 이상 + Salt), 고유식별정보 및 바이오정보는 양방향 암호화(AES-256 등).</li>
              </ul>
            </div>
          </div>
          <!-- 5과목 -->
          <div class="summary-card">
            <div class="summary-header">
              <div class="summary-title">5과목. 개인정보 관리체계</div>
              <div class="summary-badge">출제 15문항 (배점 15점)</div>
            </div>
            <div class="summary-topic">
              <div class="summary-topic-title">• ISMS-P 및 PIA(영향평가) 관리체계</div>
              <ul>
                <li><strong>ISMS-P 인증기준:</strong> 관리체계 수립 및 운영(16개), 보호대책 요구사항(64개), 개인정보 처리단계별 요구사항(22개) 총 102개 기준.</li>
                <li><strong>PIA 의무기관:</strong> 5만명 이상 민감정보/고유식별정보 구축, 50만명 이상 연계·연동 공공시스템 운용 시 사전 영향평가 의무.</li>
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
          summaryContainer.innerHTML += `
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
          summaryContainer.innerHTML += `
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
          summaryContainer.innerHTML += `
            <div class="summary-card">
              <div class="summary-header">
                <div class="summary-title">${escapeHtml(s.title)}</div>
                <div class="summary-badge">인증기준 요약</div>
              </div>
              ${topicsHtml}
            </div>
          `;
        });
      }
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

    function switchMode(mode) {
      currentMode = mode;
      document.getElementById('btnModeQuiz').classList.toggle('active', mode === 'quiz');
      document.getElementById('btnModeSummary').classList.toggle('active', mode === 'summary');
      document.getElementById('btnModeCustom').classList.toggle('active', mode === 'custom');

      document.getElementById('quizSection').style.display = mode === 'quiz' ? 'block' : 'none';
      document.getElementById('summarySection').style.display = mode === 'summary' ? 'flex' : 'none';
      document.getElementById('customSection').style.display = mode === 'custom' ? 'flex' : 'none';

      if (mode === 'custom') {
        renderCustomUnits();
      }
    }

    function renderCustomUnits() {
      const container = document.getElementById('customUnitsList');
      container.innerHTML = '';
      const customData = window.CUSTOM_STUDY_DATA;
      if (!customData || !customData.units) {
        container.innerHTML = '<div style="color:var(--text-muted); text-align:center; padding:30px;">맞춤 분석 데이터가 아직 없습니다.</div>';
        return;
      }

      customData.units.forEach((u, uIdx) => {
        const card = document.createElement('div');
        card.className = 'custom-unit-card';
        card.style.marginBottom = '20px';

        let takeawaysHtml = '';
        (u.key_takeaways || []).forEach(pt => {
          takeawaysHtml += `<li>${escapeHtml(pt)}</li>`;
        });

        let termsHtml = '';
        (u.core_concepts || []).forEach(tc => {
          termsHtml += `
            <div class="custom-term-card">
              <div class="custom-term-name">${escapeHtml(tc.term)}</div>
              <div class="custom-term-desc">${escapeHtml(tc.definition)}</div>
            </div>
          `;
        });

        let trapsHtml = '';
        (u.exam_traps || []).forEach(tr => {
          trapsHtml += `<li>⚠️ ${escapeHtml(tr)}</li>`;
        });

        card.innerHTML = `
          <div class="custom-unit-header">
            <div>
              <div class="custom-unit-title">${escapeHtml(u.unit_title)}</div>
              <div class="custom-unit-meta">문서 출처: ${escapeHtml(u.source_material)}</div>
            </div>
            <div class="summary-badge">${escapeHtml(u.ai_model || 'k-exaone_v2.5')}</div>
          </div>

          <div class="custom-takeaways">
            <div class="custom-takeaways-title">📌 핵심 요약 &amp; 결론</div>
            <ul>${takeawaysHtml}</ul>
          </div>

          <div style="font-size:13px; font-weight:700; margin-bottom:8px; color:var(--text-primary);">💡 필수 개념 정리</div>
          <div class="custom-terms-grid">${termsHtml}</div>

          <div class="custom-traps">
            <div class="custom-traps-title">🚨 시험 빈출 함정 포인트</div>
            <ul>${trapsHtml}</ul>
          </div>
        `;

        container.appendChild(card);
      });
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    // Initialize
    updateCategoryUI();
  </script>
</body>
</html>
"""

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated study.html with Multi-Exam Category Support & Resource Upload Panel!")

import json, re, os

json_path = 'cppg_questions.json' if os.path.exists('cppg_questions.json') else 'downloads/infosec-job-crawler/cppg_questions.json'
js_path = 'cppg_questions.js' if os.path.exists('cppg_questions.json') else 'downloads/infosec-job-crawler/cppg_questions.js'
out_path = 'study.html' if os.path.exists('cppg_questions.json') else 'downloads/infosec-job-crawler/study.html'

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
  <title>CPPG 실전 300제 & 전 과목 핵심 요약 | Infosec Archive</title>
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
    .nav-tab-item.active { background: var(--accent); color: #ffffff; }
    .nav-right { display: flex; align-items: center; gap: 10px; }
    .theme-btn { background: none; border: 1px solid var(--border-color); border-radius: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: var(--text-secondary); cursor: pointer; }
    
    .main-wrap { max-width: 1000px; margin: 0 auto; padding: 32px 20px 80px; }
    .hero { margin-bottom: 24px; text-align: center; }
    .hero-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: var(--accent-soft); color: var(--accent); font-size: 12px; font-weight: 600; border-radius: 20px; margin-bottom: 12px; }
    .hero-title { font-size: 28px; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px; }
    .hero-sub { font-size: 15px; color: var(--text-secondary); }
    
    /* Stats & OMR */
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 20px; }
    .stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px; text-align: center; box-shadow: var(--shadow-sm); }
    .stat-label { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
    .stat-val { font-size: 18px; font-weight: 700; color: var(--text-primary); }

    /* View Switcher */
    .view-switcher { display: flex; justify-content: center; gap: 8px; margin: 28px 0 20px; }
    .view-btn { padding: 10px 24px; border-radius: 24px; border: 1px solid var(--border-color); background: var(--bg-card); font-size: 14px; font-weight: 600; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; }
    .view-btn.active { background: var(--text-primary); color: var(--bg-primary); border-color: var(--text-primary); }

    /* Exam Selector */
    .exam-bar { display: flex; gap: 8px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; }
    .exam-btn { padding: 8px 18px; border-radius: 20px; border: 1px solid var(--border-color); background: var(--bg-secondary); font-size: 13.5px; font-weight: 600; color: var(--text-secondary); cursor: pointer; transition: all 0.15s; }
    .exam-btn.active { background: var(--accent); color: #ffffff; border-color: var(--accent); }

    /* Quiz Filters */
    .filter-bar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; align-items: center; justify-content: space-between; }
    .subj-filters { display: flex; flex-wrap: wrap; gap: 6px; }
    .subj-chip { padding: 6px 14px; border-radius: 20px; background: var(--chip-bg); border: 1px solid var(--border-color); font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all 0.15s; }
    .subj-chip.active { background: var(--accent); color: #ffffff; border-color: var(--accent); font-weight: 600; }
    .quiz-tools { display: flex; gap: 8px; }
    .tool-btn { padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); font-size: 12px; font-weight: 600; color: var(--text-secondary); cursor: pointer; }
    .tool-btn.active { background: var(--danger-soft); color: var(--danger); border-color: var(--danger); }

    /* Question Cards */
    .questions-container { display: flex; flex-direction: column; gap: 20px; }
    .q-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 22px; box-shadow: var(--shadow-sm); transition: border-color 0.2s; }
    .q-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .q-badge-wrap { display: flex; align-items: center; gap: 8px; }
    .q-exam-badge { font-size: 11.5px; font-weight: 700; color: var(--text-secondary); background: var(--chip-bg); padding: 3px 8px; border-radius: 6px; }
    .q-subj-badge { font-size: 11.5px; font-weight: 600; color: var(--accent); background: var(--accent-soft); padding: 3px 10px; border-radius: 12px; }
    .q-index { font-size: 14px; font-weight: 700; color: var(--text-muted); }
    .q-prompt { font-size: 16px; font-weight: 600; line-height: 1.55; margin-bottom: 18px; word-break: keep-all; white-space: pre-line; }
    .choices-list { display: flex; flex-direction: column; gap: 10px; }
    .choice-row { display: flex; align-items: flex-start; gap: 12px; padding: 12px 16px; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-secondary); cursor: pointer; transition: all 0.15s; font-size: 14px; line-height: 1.5; }
    .choice-row:hover:not(.disabled) { border-color: var(--accent); background: var(--accent-soft); }
    .choice-circle { width: 22px; height: 22px; border-radius: 50%; border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; background: var(--bg-card); color: var(--text-secondary); }
    
    .choice-row.correct { background: var(--success-soft) !important; border-color: var(--success) !important; color: var(--success) !important; font-weight: 600; }
    .choice-row.correct .choice-circle { background: var(--success); color: #ffffff; border-color: var(--success); }
    .choice-row.wrong { background: var(--danger-soft) !important; border-color: var(--danger) !important; color: var(--danger) !important; }
    .choice-row.wrong .choice-circle { background: var(--danger); color: #ffffff; border-color: var(--danger); }

    .exp-panel { display: none; margin-top: 16px; padding: 16px; border-radius: 10px; background: var(--chip-bg); border-left: 4px solid var(--accent); }
    .exp-title { font-size: 12px; font-weight: 700; color: var(--accent); margin-bottom: 6px; text-transform: uppercase; }
    .exp-body { font-size: 13.5px; color: var(--text-secondary); line-height: 1.6; word-break: keep-all; white-space: pre-line; }

    /* Summary Section */
    .summary-section { display: none; }
    .subj-summary-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 24px; margin-bottom: 24px; box-shadow: var(--shadow-sm); }
    .summary-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 14px; margin-bottom: 18px; }
    .summary-title { font-size: 18px; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 8px; }
    .summary-weight { font-size: 12px; font-weight: 600; color: var(--accent); background: var(--accent-soft); padding: 3px 10px; border-radius: 12px; }
    .summary-topic { margin-bottom: 20px; }
    .summary-topic-title { font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
    .summary-topic-title::before { content: '•'; color: var(--accent); font-weight: 900; }
    .summary-list { list-style: none; display: flex; flex-direction: column; gap: 8px; padding-left: 14px; }
    .summary-list li { font-size: 14px; color: var(--text-secondary); line-height: 1.55; position: relative; }
    .summary-list li::before { content: '-'; position: absolute; left: -12px; color: var(--text-muted); }
    .summary-table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px; }
    .summary-table th, .summary-table td { border: 1px solid var(--border-color); padding: 8px 12px; text-align: left; }
    .summary-table th { background: var(--chip-bg); font-weight: 600; }

    @media (max-width: 640px) {
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
      .exam-bar { flex-direction: column; }
      .exam-btn { text-align: center; }
    }
  </style>
</head>
<body>
  <!-- Header Navbar -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-left">
        <a href="index.html" class="nav-brand">
          <img src="logo.png" alt="Infosec Archive" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
        <nav class="nav-tabs">
          <a href="index.html" class="nav-tab-item">보안 채용공고</a>
          <a href="study.html" class="nav-tab-item active">CPPG 스터디</a>
        </nav>
      </div>
      <div class="nav-right">
        <button class="theme-btn" id="themeToggle" aria-label="테마 전환">🌓</button>
      </div>
    </div>
  </header>

  <main class="main-wrap">
    <!-- Hero Header -->
    <div class="hero">
      <div class="hero-pill">📚 개인정보관리사(CPPG) 실전 수험 허브</div>
      <h1 class="hero-title">CPPG 실전 300제 & 전 과목 핵심 노트</h1>
      <p class="hero-sub">실전 모의고사 1·2·3회 300문항 즉시 채점 및 187p 기본서 5개 과목 정밀 요약</p>

      <!-- Stats Grid -->
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
          <div class="stat-val" id="topCorrect">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">정답률 / 합격진단</div>
          <div class="stat-val" id="topAccuracy">0%</div>
        </div>
      </div>
    </div>

    <!-- Mode Switcher -->
    <div class="view-switcher">
      <button class="view-btn active" id="btnQuizView">📝 실전 모의고사 (300제)</button>
      <button class="view-btn" id="btnSummaryView">📖 전 과목 핵심 개념 요약노트</button>
    </div>

    <!-- Quiz Section -->
    <section id="quizSection">
      <!-- Exam Selector -->
      <div class="exam-bar">
        <button class="exam-btn active" data-exam="1">1회 실전 모의고사 (100문항)</button>
        <button class="exam-btn" data-exam="2">2회 실전 모의고사 (100문항)</button>
        <button class="exam-btn" data-exam="3">3회 실전 모의고사 (100문항)</button>
        <button class="exam-btn" data-exam="0">전체 300제 집중 풀이</button>
      </div>

      <!-- Filters & Tools -->
      <div class="filter-bar">
        <div class="subj-filters">
          <div class="subj-chip active" data-subj="0">전체</div>
          <div class="subj-chip" data-subj="1">1과목: 이해</div>
          <div class="subj-chip" data-subj="2">2과목: 제도</div>
          <div class="subj-chip" data-subj="3">3과목: 라이프사이클</div>
          <div class="subj-chip" data-subj="4">4과목: 보호조치</div>
          <div class="subj-chip" data-subj="5">5과목: 관리체계</div>
        </div>
        <div class="quiz-tools">
          <button class="tool-btn" id="btnWrongOnly">오답만 보기</button>
          <button class="tool-btn" id="btnReset">풀이 초기화</button>
        </div>
      </div>

      <div class="questions-container" id="questionsContainer"></div>
    </section>

    <!-- Summary Section -->
    <section id="summarySection" class="summary-section">
      <!-- 1과목 -->
      <div class="subj-summary-card">
        <div class="summary-header">
          <div class="summary-title">1과목. 개인정보보호의 이해</div>
          <div class="summary-weight">출제 10문항 (배점 10점)</div>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">개인정보의 법적 정의 및 식별가능성 판단 기준</div>
          <ul class="summary-list">
            <li><strong>정의 3요소:</strong> ① 살아있는 개인에 관한 정보, ② 성명·주민번호·영상 등을 통해 특정 개인을 알아볼 수 있는 정보, ③ 해당 정보만으로는 알 수 없더라도 다른 정보와 쉽게 결합하여 알아볼 수 있는 정보.</li>
            <li><strong>정보주체 범위:</strong> 원칙적으로 생존하는 자연인에 한정. 법인·단체·사망자·사물 정보는 개인정보가 아님 (단, 사망자 정보가 유족과의 관계를 증명하여 유족의 사생활을 침해하는 경우 유족의 개인정보로 인정).</li>
            <li><strong>쉽게 결합(식별가능성):</strong> 결합 대상 정보의 입수 가능성, 결합에 소요되는 시간·비용·기술적 노력을 합리적으로 고려하여 판단.</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">가명정보 vs 익명정보의 법적 지위</div>
          <ul class="summary-list">
            <li><strong>가명정보:</strong> 추가 정보의 사용·결합 없이는 특정 개인을 식별할 수 없도록 처리한 정보. 개인정보 보호법의 적용을 받으나 통계작성, 과학적 연구, 공익적 기록보존 목적으로 정보주체 동의 없이 처리 가능. 특정 개인을 식별하기 위한 재식별 행위는 절대 금지(위반 시 5년 이하 징역 또는 5천만원 이하 벌금, 전체 매출액 3% 이하 과징금).</li>
            <li><strong>익명정보:</strong> 시간·비용·기술 등을 합리적으로 고려할 때 다른 정보를 사용하여도 더 이상 개인을 식별할 수 없는 정보. 개인정보 보호법의 적용을 전면 배제.</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">프라이버시 권리와 개인정보 유형</div>
          <ul class="summary-list">
            <li><strong>프라이버시 권리:</strong> '홀로 있을 권리'에서 출발하여 현대 사회에서는 '자신에 관한 정보를 언제, 누구에게, 어느 범위까지 공개하고 이용되도록 할 것인지 스스로 결정할 수 있는 권리(개인정보 자기결정권)'로 발전.</li>
            <li><strong>유형 분류:</strong> 인적 정보(성명, 주민번호, 주소), 신체적 정보(얼굴, 지문, 홍채, DNA), 정신적 정보(사상, 신념, 종교), 사회적 정보(학력, 직업, 경력, 상벌), 재산적 정보(금융계좌, 소득, 부동산, 신용등급), 통신·위치 정보(통화내역, 로그기록, GPS 위치 등).</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">OECD 8대 원칙 & EU GDPR 핵심 비교</div>
          <ul class="summary-list">
            <li><strong>OECD 8원칙:</strong> 수집제한의 원칙, 정보정확성의 원칙, 목적명확화의 원칙, 이용제한의 원칙, 안전보호의 원칙, 공개의 원칙, 개인참가의 원칙, 책임의 원칙.</li>
            <li><strong>EU GDPR 주요 특징:</strong>
              <table class="summary-table">
                <tr><th>구분</th><th>주요 내용</th></tr>
                <tr><td>역외 적용</td><td>EU 역내 사업장이 없더라도 EU 거주자에게 재화·서비스를 제공하거나 행동을 모니터링하는 경우 적용</td></tr>
                <tr><td>DPO 지정 의무</td><td>공공기관, 핵심 활동이 대규모 정기적 모니터링이거나 대규모 민감정보를 처리하는 기업에 DPO 지정 의무화</td></tr>
                <tr><td>유출 통지</td><td>개인정보 유출 인지 후 지체 없이 72시간 이내에 감독기구(DPA)에 통지</td></tr>
                <tr><td>과징금</td><td>심각한 위반 시 전 세계 연간 매출액의 4% 또는 2,000만 유로 중 높은 금액 부과</td></tr>
              </table>
            </li>
            <li><strong>미국 법제:</strong> 일반법 중심이 아닌 산업 분야별 개별법 체계(HIPAA, GLBA, COPPA 등) 및 주 단위 법률(캘리포니아 CCPA/CPRA) 중심 규율.</li>
          </ul>
        </div>
      </div>

      <!-- 2과목 -->
      <div class="subj-summary-card">
        <div class="summary-header">
          <div class="summary-title">2과목. 개인정보보호 제도</div>
          <div class="summary-weight">출제 20문항 (배점 20점)</div>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">법령 체계와 규제 일원화</div>
          <ul class="summary-list">
            <li><strong>일반법-특별법 체계:</strong> 개인정보 보호법은 공공과 민간을 포괄하는 일반법. 신용정보법(금융분야 개인신용정보), 위치정보법(개인위치정보), 의료법 등 특별법이 우선 적용되고 미규정 사항은 개인정보 보호법 적용.</li>
            <li><strong>규제 일원화:</strong> 정보통신망법의 개인정보 보호 관련 조항이 개인정보 보호법으로 전면 통합 이관되어 온·오프라인 사업자 규제가 완전히 일원화됨.</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">개인정보 수집·이용 요건 및 최소수집 원칙</div>
          <ul class="summary-list">
            <li><strong>적법 수집 근거(제15조):</strong> ① 정보주체의 동의, ② 법률에 특별한 규정 또는 법령상 의무 준수, ③ 공공기관의 소관 업무 수행, ④ 계약의 체결 및 이행, ⑤ 정보주체 또는 제3자의 급박한 생명·신체·재산의 이익, ⑥ 개인정보처리자의 정당한 이익 달성(명백히 정보주체의 권리보다 우선하는 경우).</li>
            <li><strong>필수 동의 vs 선택 동의 분리:</strong> 필수 항목과 선택 항목을 명확히 구분하여 각각 동의를 받아야 하며, 선택 항목 동의를 거부한다는 이유로 서비스 제공을 거부할 수 없음(위반 시 3천만원 이하 과태료).</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">개인정보 처리 위탁 vs 제3자 제공 핵심 비교</div>
          <table class="summary-table">
            <tr><th>구분</th><th>제3자 제공 (제17조)</th><th>개인정보 처리 위탁 (제26조)</th></tr>
            <tr><td>처리 목적</td><td>제공받는 제3자의 고유 업무 목적</td><td>위탁자의 업무 처리 목적 (위탁자 이익)</td></tr>
            <tr><td>동의 요건</td><td>원칙적으로 정보주체의 개별 동의 필수</td><td>정보주체 동의 불요 (처리방침 공개 또는 통지)</td></tr>
            <tr><td>법적 책임</td><td>제공받은 자가 독립된 처리자로서 법적 책임</td><td>위탁자가 수탁자에 대한 관리·감독 및 손해배상 책임</td></tr>
            <tr><td>문서 계약</td><td>제공 계약서 체결 권장</td><td>필수 사항(위탁업무 목적, 기술적 조치, 재위탁 제한 등) 서면 계약 의무</td></tr>
          </table>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">민감정보 및 고유식별정보의 처리 제한</div>
          <ul class="summary-list">
            <li><strong>민감정보:</strong> 사상·신념, 노동조합·정당의 가입·탈퇴, 정치적 견해, 건강, 성생활, 유전정보, 범죄경력자료, 생체인식정보(개인식별 목적), 인종·민족 정보. 일반 개인정보와 별도로 분리하여 동의를 받아야 함.</li>
            <li><strong>고유식별정보:</strong> 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호. 일반 개인정보와 별도 분리 동의 필수.</li>
            <li><strong>주민등록번호 원칙적 처리 금지:</strong> 동의가 있더라도 처리 불가! 법률·대통령령·국회규칙·대법원규칙 등 명시적 법령 근거가 있거나 급박한 생명·신체·재산의 이익을 위한 경우에만 예외적 허용. 대체수단(아이핀, 휴대폰인증 등) 의무 제공.</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">영상정보처리기기 설치·운영 규제</div>
          <ul class="summary-list">
            <li><strong>고정형 영상처리기기(CCTV):</strong> 공개된 장소 설치 원칙적 금지. 범죄 예방, 시설 안전, 화재 예방, 교통 단속 등 법정 목적에 한해 설치 가능. 안내판 5대 필수 항목: 설치 목적 및 장소, 촬영 범위 및 시간, 관리책임자 성명 및 연락처. 녹음 기능 사용 및 임의 조작은 절대 금지(3년 이하 징역 또는 3천만원 이하 벌금).</li>
            <li><strong>이동형 영상처리기기(드론, 자율주행차, 바디캠):</strong> 업무 목적으로 공개된 장소에서 이동형 기기로 촬영 시 불빛, 소리, 안내판 등으로 촬영 사실을 정보주체가 쉽게 알 수 있도록 표시해야 함.</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">개인정보 보호책임자(CPO) & 국외 이전</div>
          <ul class="summary-list">
            <li><strong>CPO 지정 요건:</strong> 공공기관(중앙부처 고위공무원, 시·도 3급, 시·군·구 4급), 민간기업(사업주, 대표자, 임원 또는 개인정보 처리 부서의 장). CPO의 독립적 업무 수행 보장 및 불이익 처우 금지.</li>
            <li><strong>국외 이전 요건:</strong> ① 정보주체 별도 동의, ② 계약 체결·이행을 위한 처리위탁·보관, ③ 개인정보보호 인증(ISMS-P 등), ④ 보호위원회가 동등 수준으로 인정한 국가/국제기구. 위반 시 보호위원회가 국외이전 중지명령 부과 가능.</li>
          </ul>
        </div>
      </div>

      <!-- 3과목 -->
      <div class="subj-summary-card">
        <div class="summary-header">
          <div class="summary-title">3과목. 개인정보 라이프사이클 관리</div>
          <div class="summary-weight">출제 25문항 (배점 25점)</div>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">수집·이용·파기 라이프사이클 관리</div>
          <ul class="summary-list">
            <li><strong>간접수집 출처 통지:</strong> 정보주체 이외로부터 수집한 경우 정보주체의 요구가 있거나, 5만명 이상 민감/고유식별정보 처리자 또는 100만명 이상 정보 처리자는 3개월 이내에 출처, 처리 목적, 처리정지 요구권을 서면 등으로 통지해야 함.</li>
            <li><strong>이용·제공 내역 정기 통지:</strong> 100만명 이상 정보주체 또는 5만명 이상 민감/고유식별정보 처리자는 연 1회 이상 개인정보 이용·제공 내역을 정보주체에게 통지해야 함.</li>
            <li><strong>파기 기한 및 방법:</strong> 보유기간 경과 또는 처리 목적 달성 시 지체 없이 5일 이내 파기. 전자적 파일은 영구삭제(복구 불가능 기술), 인쇄물은 분쇄 또는 소각. 다른 법령에 따라 보존해야 하는 경우 다른 개인정보와 별도 분리 저장·관리.</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">개인정보 유출 사고 대응 체계</div>
          <ul class="summary-list">
            <li><strong>정보주체 통지:</strong> 유출 사실을 알게 된 때부터 지체 없이 72시간 이내에 유출 항목, 시점 및 경위, 피해 최소화 조치, 처리자 대응 및 구제절차, 담당부서 연락처를 서면·이메일·문자 등으로 개별 통지. (연락처를 모르는 경우 홈페이지 30일 이상 게시 갈음 가능).</li>
            <li><strong>감독기구 신고:</strong> 1,000명 이상의 정보주체에 관한 개인정보가 유출된 경우 지체 없이 72시간 이내에 개인정보 보호위원회 또는 한국인터넷진흥원(KISA)에 신고 의무.</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">정보주체의 권리 및 권리구제 제도</div>
          <ul class="summary-list">
            <li><strong>정보주체의 6대 권리:</strong> 열람 요구권, 정정·삭제 요구권(열람 거친 후 행사), 처리정지 요구권, 동의철회권, 개인정보 전송요구권(마이데이터), 자동화된 결정에 대한 거부·설명요구권.</li>
            <li><strong>손해배상 제도:</strong> 입증책임 전환(처리자가 고의·과실 없음을 입증해야 함), 법정손해배상(300만원 이하 범위에서 배상 청구), 징벌적 손해배상(고의 또는 중대한 과실로 유출된 경우 실제 손해액의 최대 5배까지 배상책임). 손해배상책임 보장을 위한 보험·공제 가입 의무.</li>
            <li><strong>과징금 부과 체계:</strong> 위반행위 시 전체 매출액의 3% 이하 과징금 부과 (단, 처리자가 위반행위와 관련 없는 매출액임을 입증한 경우 해당 금액 제외 후 산정).</li>
          </ul>
        </div>
      </div>

      <!-- 4과목 -->
      <div class="subj-summary-card">
        <div class="summary-header">
          <div class="summary-title">4과목. 개인정보의 보호조치</div>
          <div class="summary-weight">출제 30문항 (배점 30점)</div>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">안전성 확보조치 기준 (보호위원회 고시) 핵심</div>
          <ul class="summary-list">
            <li><strong>내부관리계획 수립:</strong> CPO 지정, 취급자 역할 및 교육, 접근 권한 관리, 암호화, 접속기록 보관, 모의훈련 등 필수 사항을 반영하여 매년 수립·시행.</li>
            <li><strong>접근 권한 관리:</strong> 업무 수행에 필요한 최소한의 범위로 업무 담당자별 차등 부여. 인사이동 발생 시 지체 없이(5일 이내) 변경 또는 말소. 권한 부여·변경·말소 내역은 최소 3년 이상 보관.</li>
            <li><strong>접근 통제 & 망분리:</strong> 침입차단시스템(방화벽) 및 침입탐지시스템 운영. 외부 접속 시 안전한 가상사설망(VPN) 및 2차 인증(OTP) 적용. 10만명 이상 정보주체 또는 100만명 이상 정보 처리자는 인터넷망 차단조치(망분리) 의무.</li>
            <li><strong>암호화 의무 대상:</strong>
              <table class="summary-table">
                <tr><th>구분</th><th>암호화 대상 항목</th><th>암호화 방식</th></tr>
                <tr><td>전송 구간</td><td>모든 개인정보 및 인증정보</td><td>SSL/TLS, HTTPS, IPSec 등 보안 프로토콜</td></tr>
                <tr><td>저장 구간</td><td>고유식별정보, 바이오정보</td><td>안전한 암호 알고리즘(AES, ARIA, SEED 등)</td></tr>
                <tr><td>비밀번호</td><td>로그인 비밀번호</td><td>일방향(단방향) 암호화 (SHA-256 등 솔트 적용, 복호화 불가)</td></tr>
              </table>
            </li>
            <li><strong>접속기록 보관 및 점검:</strong> 접속기록(계정, 접속일시, 접속지IP, 수행업무, 정보주체 식별정보)을 기본 1년 이상 보관. 단, 5만명 이상 정보주체 또는 민감정보/고유식별정보 처리시스템은 2년 이상 보관! 월 1회 이상 정기적으로 점검(다운로드, 대량조회, 비정상 접속 분석).</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">정보통신망법 광고성 정보 전송 제한 규제</div>
          <ul class="summary-list">
            <li><strong>사전 동의 원칙(Opt-in):</strong> 영리 목적 광고성 정보 전송 시 정보주체의 명시적인 사전 수신 동의 필수.</li>
            <li><strong>야간 전송 제한:</strong> 오후 9시부터 다음 날 오전 8시까지 광고성 정보를 전송하려는 경우 별도의 사전 동의를 받아야 함.</li>
            <li><strong>필수 표기 사항:</strong> 제목 첫머리에 (광고) 표시, 전송자 명칭 및 연락처, 무료 수신거부 방법(080 무료전화 등). 수신거부 비용을 수신자에게 전가하는 것은 불법.</li>
          </ul>
        </div>
      </div>

      <!-- 5과목 -->
      <div class="subj-summary-card">
        <div class="summary-header">
          <div class="summary-title">5과목. 개인정보 관리체계</div>
          <div class="summary-weight">출제 15문항 (배점 15점)</div>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">ISMS-P 인증 제도 체계</div>
          <ul class="summary-list">
            <li><strong>공동 운영 부처:</strong> 과학기술정보통신부 + 개인정보보호위원회 공동 운영, 한국인터넷진흥원(KISA) 총괄 관리.</li>
            <li><strong>인증기준 구성 (총 102개 항목):</strong>
              <table class="summary-table">
                <tr><th>영역</th><th>기준 수</th><th>주요 내용</th></tr>
                <tr><td>1. 관리체계 수립 및 운영</td><td>16개</td><td>경영진 참여, 위험 관리, 정책 수립, 범위 설정, 사후 관리</td></tr>
                <tr><td>2. 보호대책 요구사항</td><td>64개</td><td>정책·조직·자산, 인적보안, 외부자보안, 접근통제, 암호화, 운영보안 등</td></tr>
                <tr><td>3. 개인정보 처리단계별 요구사항</td><td>22개</td><td>수집 시 보호, 보유 및 이용 시 보호, 제공 시 보호, 파기, 권리보호</td></tr>
              </table>
            </li>
            <li><strong>인증 유효기간:</strong> 최초 인증 3년. 매년 1회 이상 사후심사를 받아야 하며, 유효기간 만료 전 갱신심사 신청.</li>
            <li><strong>인증심사원 등급:</strong> 심사원보 → 심사원(자격 취득 후 심사 4회 20일 이상 참가) → 선임심사원 → 특급심사원. 자격 유효기간 3년(보수교육 필수 이수).</li>
          </ul>
        </div>
        <div class="summary-topic">
          <div class="summary-topic-title">개인정보 영향평가 (PIA: Privacy Impact Assessment)</div>
          <ul class="summary-list">
            <li><strong>제도 목적:</strong> 공공기관이 대규모 개인정보파일을 구축·운용·변경할 때 사전에 프라이버시 침해 위험성을 분석하고 개선책을 도출하는 제도.</li>
            <li><strong>공공기관 의무 평가 대상 기준:</strong>
              <table class="summary-table">
                <tr><th>구분</th><th>의무 평가 기준</th></tr>
                <tr><td>민감정보 / 고유식별정보</td><td>5만명 이상의 정보주체에 관한 정보를 처리하는 파일 구축·운용·변경 시</td></tr>
                <tr><td>연계·결합 파일</td><td>50만명 이상의 정보주체에 관한 정보를 다른 파일과 연계·결합하는 경우</td></tr>
                <tr><td>일반 대규모 개인정보파일</td><td>100만명 이상의 정보주체에 관한 개인정보파일을 구축·운용·변경하는 경우</td></tr>
              </table>
            </li>
            <li><strong>PIA 수행 3단계 절차:</strong> 사전준비 단계(사업계획 분석, 평가팀 구성) → 영향평가 수행 단계(위험도 분석, 보호조치 점검) → 결과보고 및 이행관리 단계(영향평가서 작성, 보호위원회 제출 및 개선사항 이행).</li>
          </ul>
        </div>
      </div>
    </section>
  </main>

  <script src="cppg_questions.js"></script>
  <script>
    let currentExam = 1; // 1, 2, 3, 0(all)
    let currentSubj = 0; // 0(all), 1..5
    let wrongOnly = false;
    let userAnswers = {}; // key: q.id

    // Load saved answers from localStorage
    try {
      const saved = localStorage.getItem('cppg_user_answers_v2');
      if (saved) userAnswers = JSON.parse(saved);
    } catch (e) {}

    // Theme Toggle
    const themeBtn = document.getElementById('themeToggle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && prefersDark)) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
    themeBtn.addEventListener('click', () => {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
      localStorage.setItem('theme', isDark ? 'light' : 'dark');
    });

    // View Switcher (Quiz vs Summary)
    const btnQuizView = document.getElementById('btnQuizView');
    const btnSummaryView = document.getElementById('btnSummaryView');
    const quizSection = document.getElementById('quizSection');
    const summarySection = document.getElementById('summarySection');

    btnQuizView.addEventListener('click', () => {
      btnQuizView.classList.add('active');
      btnSummaryView.classList.remove('active');
      quizSection.style.display = 'block';
      summarySection.style.display = 'none';
    });

    btnSummaryView.addEventListener('click', () => {
      btnSummaryView.classList.add('active');
      btnQuizView.classList.remove('active');
      summarySection.style.display = 'block';
      quizSection.style.display = 'none';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Exam buttons
    const examBtns = document.querySelectorAll('.exam-btn');
    examBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        examBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentExam = parseInt(btn.getAttribute('data-exam'), 10);
        updateStats();
        renderQuestions();
      });
    });

    // Subject chips
    const subjChips = document.querySelectorAll('.subj-chip');
    subjChips.forEach(chip => {
      chip.addEventListener('click', () => {
        subjChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentSubj = parseInt(chip.getAttribute('data-subj'), 10);
        renderQuestions();
      });
    });

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
      if (confirm('현재 풀이 기록을 모두 초기화하시겠습니까?')) {
        userAnswers = {};
        try { localStorage.removeItem('cppg_user_answers_v2'); } catch(e) {}
        updateStats();
        renderQuestions();
      }
    });

    function getFilteredQuestions() {
      const all = window.ALL_QUESTIONS || [];
      return all.filter(q => {
        const matchExam = currentExam === 0 || q.exam === currentExam;
        const matchSubj = currentSubj === 0 || q.subject_id === currentSubj;
        return matchExam && matchSubj;
      });
    }

    function updateStats() {
      const all = window.ALL_QUESTIONS || [];
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

      let passText = acc + '%';
      if (solved >= 40) {
        if (acc >= 60) {
          passText += ' (합격권 👍)';
        } else {
          passText += ' (보완필요 ⚠️)';
        }
      }
      document.getElementById('topAccuracy').textContent = passText;
    }

    function renderQuestions() {
      const container = document.getElementById('questionsContainer');
      container.innerHTML = '';

      const filtered = getFilteredQuestions();
      const circles = ['①', '②', '③', '④', '⑤'];

      filtered.forEach(q => {
        const ans = userAnswers[q.id];
        if (wrongOnly) {
          if (!ans || ans.isCorrect) return;
        }

        const card = document.createElement('div');
        card.className = 'q-card';

        let choicesHtml = '';
        q.choices.forEach((choiceText, idx) => {
          const choiceNum = idx + 1;
          let rowClass = 'choice-row';
          if (ans) {
            rowClass += ' disabled';
            if (choiceNum === q.answer) {
              rowClass += ' correct';
            } else if (choiceNum === ans.selected) {
              rowClass += ' wrong';
            }
          }

          choicesHtml += `
            <div class="${rowClass}" onclick="handleAnswer('${q.id}', ${choiceNum})">
              <div class="choice-circle">${circles[idx]}</div>
              <div>${escapeHtml(choiceText)}</div>
            </div>
          `;
        });

        const expDisplay = ans ? 'block' : 'none';

        card.innerHTML = `
          <div class="q-meta">
            <div class="q-badge-wrap">
              <span class="q-exam-badge">${q.exam}회 모의고사</span>
              <span class="q-subj-badge">${q.subject}</span>
            </div>
            <span class="q-index">Q${q.number}</span>
          </div>
          <div class="q-prompt">${escapeHtml(q.prompt)}</div>
          <div class="choices-list">${choicesHtml}</div>
          <div class="exp-panel" id="exp_${q.id}" style="display: ${expDisplay}">
            <div class="exp-title">정답: ${circles[q.answer - 1]}</div>
            <div class="exp-body">${escapeHtml(q.explanation || '해설 준비 중')}</div>
          </div>
        `;

        container.appendChild(card);
      });

      if (container.children.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--text-muted);">조건에 일치하는 문제가 없습니다.</div>';
      }
    }

    window.handleAnswer = function(qId, choiceNum) {
      if (userAnswers[qId]) return;
      const all = window.ALL_QUESTIONS || [];
      const q = all.find(item => item.id === qId);
      if (!q) return;

      const isCorrect = (choiceNum === q.answer);
      userAnswers[qId] = {
        selected: choiceNum,
        isCorrect: isCorrect
      };

      try {
        localStorage.setItem('cppg_user_answers_v2', JSON.stringify(userAnswers));
      } catch(e) {}

      updateStats();
      renderQuestions();
    };

    function escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    // Init
    updateStats();
    renderQuestions();
  </script>
</body>
</html>
"""

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Successfully generated cppg_questions.js and study.html!')

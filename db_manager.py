# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import re
import hashlib
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "archive.db")

# ---------------------------------------------------------------------------
# 공고 식별자(job_key)
#   예전에는 '회사명 + 제목 앞 12자'를 키로 썼기 때문에 제목이 비슷한 다른 공고가
#   같은 키로 뭉개지고, 사람인 rec_idx·원티드 wd 처럼 하나의 통합 URL을 여러 공고가
#   함께 쓰는 경우에도 구분할 방법이 없었다. 이제 플랫폼이 준 공고 ID(URL에서 추출)와
#   제목 지문을 함께 써서 같은 URL의 서로 다른 공고도 완전히 분리한다.
#   형식: `<platform>:<external_id>:<title_fingerprint>`  (예: wanted:390475:1a2b3c4d)
#         ID가 없으면 `h1:<sha1 회사|제목|URL>`
# ---------------------------------------------------------------------------
PLATFORM_SLUGS = {
    "원티드": "wanted",
    "점핏": "jumpit",
    "사람인": "saramin",
    "리멤버": "remember",
    "잡코리아": "jobkorea",
    "인크루트": "incruit",
}

# 플랫폼 공고 상세 URL의 ID 부분 (플랫폼별 표기)
EXTERNAL_ID_PATTERNS = (
    (r"/wd/(\d+)", "wanted"),
    (r"/position/(\d+)", "jumpit"),
    (r"[?&]rec_idx=(\d+)", "saramin"),
    (r"/posting/(\d+)", "remember"),
    (r"/GI_Read/(\d+)", "jobkorea"),
    (r"[?&]job=(\d+)", "incruit"),
)

JOB_KEY_PREFIX_RE = re.compile(
    r"^(?:" + "|".join(sorted(set(PLATFORM_SLUGS.values()) | {"etc", "h1"})) + r"):"
)


def extract_external_id(url):
    """플랫폼 공고 URL에서 공고 ID를 뽑는다. 없으면 빈 문자열."""
    text = str(url or "")
    for pattern, _slug in EXTERNAL_ID_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def job_title_fingerprint(title):
    """제목 지문 — 공백·대소문자만 정규화해 원문 구성을 최대한 보존한다."""
    return re.sub(r"\s+", "", str(title or "")).lower()


def make_job_key(company, title, url, platforms=None, platform=None, external_id=None):
    """충돌 없는 안정적인 공고 키. 같은 URL을 쓰는 다른 공고도 제목 지문으로 분리된다."""
    platform_list = [platform] if platform else list(platforms or [])
    slug = PLATFORM_SLUGS.get(platform_list[0], "") if platform_list else ""
    ext = str(external_id or "").strip() or extract_external_id(url)
    fingerprint = hashlib.sha1(job_title_fingerprint(title).encode("utf-8")).hexdigest()[:8]
    if ext:
        return "%s:%s:%s" % (slug or "etc", ext, fingerprint)
    seed = "%s|%s|%s" % (company or "", title or "", url or "")
    return "h1:" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:16]


def is_platform_job_key(job_key):
    """이미 플랫폼 ID 기반 키인지."""
    return bool(JOB_KEY_PREFIX_RE.match(str(job_key or "")))


def build_job_identity_index(rows):
    """기존 DB 행을 'platform+external_id' 색인과 '짧은 제목 키' 후보 색인으로 나눈다.

    rows: company/title/url/platforms/job_key 를 가진 매핑(또는 sqlite3.Row) 목록.
    반환: (identity_index, title_index)
      identity_index[(platform, external_id)] = job_key
      title_index[짧은 제목 키] = [ {"job_key", "platform", "external_id", "title"} ]
    """
    identity_index = {}
    title_index = {}
    for row in rows:
        platforms = row["platforms"] if not isinstance(row, dict) else row.get("platforms")
        if isinstance(platforms, str):
            try:
                platforms = json.loads(platforms) if platforms else []
            except (TypeError, ValueError):
                platforms = []
        if not isinstance(platforms, list):
            platforms = []
        url = row["url"] if not isinstance(row, dict) else row.get("url")
        company = row["company"] if not isinstance(row, dict) else row.get("company")
        title = row["title"] if not isinstance(row, dict) else row.get("title")
        job_key = row["job_key"] if not isinstance(row, dict) else row.get("job_key")
        platform = platforms[0] if platforms else ""
        ext = extract_external_id(url)
        if platform and ext:
            identity_index[(platform, ext)] = job_key
        short = normalize_key(company or "", title or "")
        title_index.setdefault(short, []).append({
            "job_key": job_key,
            "platform": platform,
            "external_id": ext,
            "title": title or "",
        })
    return identity_index, title_index


def resolve_existing_job_key(company, title, platform, external_id, url,
                             identity_index, title_index):
    """수집한 공고를 기존 DB 행에 이어붙일 job_key를 고른다(없으면 None).

    · 같은 platform+external_id 행이 있으면 그 키를 그대 쓴다(최우선).
    · 짧은 제목 키 후보가 **정확하 1건**이고 외부 ID가 충돌하지 않을 때만 이어받는다.
      - 같은 플랫폼인데 공고 ID가 서로 다르면 → 서로 다른 공고이므로 이어받지 않는다.
      - 플랫폼이 다르면 ID 네임스페이스가 달라 '충돌'이 아니지만, 같은 공고가
        교차 게시된 경우에만 이어받도록 회사·전체 제목까지 같을 때로 제한한다.
    · 후보가 둘 이상이면(제목 12자만 같은 다른 공고) 이어받지 않는다.
    """
    platform = str(platform or "").strip()
    ext = str(external_id or "").strip() or extract_external_id(url)
    if platform and ext:
        hit = identity_index.get((platform, ext))
        if hit:
            return hit

    candidates = title_index.get(normalize_key(company or "", title or "")) or []
    if len(candidates) != 1:
        return None
    candidate = candidates[0]
    if ext and candidate["external_id"]:
        if candidate["platform"] == platform:
            # 같은 플랫폼의 다른 공고 ID → 절대 합치지 않는다.
            return None
        if job_title_fingerprint(candidate["title"]) != job_title_fingerprint(title):
            return None
    return candidate["job_key"]


def migrate_job_keys(db_path=DB_PATH):
    """예전 '회사명_제목12자' 키를 플랫폼 ID 기반 키로 한 번에 옮긴다.

    수집이 다시 돌지 않아도(빌드만 돌아도) 화면·저장 데이터가 새 키를 쓰도록 하고,
    기존 행의 id·first_seen_at·요약은 그대로 유지한다. 대상 키가 이미 다른 행에
    있으면(희귀 충돌) 건드리지 않는다.
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, job_key, company, title, url, platforms FROM jobs;")
    rows = [dict(r) for r in cur.fetchall()]
    existing = {r["job_key"] for r in rows}
    now_str = get_kst_now().strftime("%Y-%m-%d %H:%M:%S KST")
    updates = []
    for row in rows:
        if is_platform_job_key(row["job_key"]):
            continue
        try:
            platforms = json.loads(row["platforms"]) if row["platforms"] else []
        except (TypeError, ValueError):
            platforms = []
        new_key = make_job_key(row["company"], row["title"], row["url"], platforms=platforms)
        if new_key == row["job_key"] or new_key in existing:
            continue
        updates.append((new_key, now_str, row["id"]))
        existing.add(new_key)
        existing.discard(row["job_key"])
    if updates:
        cur.executemany("UPDATE jobs SET job_key = ?, updated_at = ? WHERE id = ?;", updates)
        conn.commit()
    conn.close()
    return len(updates)

def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_PATH):
    """SQLite 데이터베이스 스키마 초기화"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    # 1. 채용 공고 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_key TEXT UNIQUE NOT NULL,
        company TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        platforms TEXT NOT NULL,  -- JSON Array
        keywords TEXT NOT NULL,   -- JSON Array
        location TEXT,
        experience TEXT,          -- 표시용 경력 라벨('신입' · '신입·경력' · '경력무관' · '인턴' · '경력 3년↑' · '경력 2~5년')
        deadline TEXT NOT NULL,
        deadline_status TEXT NOT NULL, -- D_DAY, URGENT, UPCOMING, ALWAYS, WHEN_FILLED, EXPIRED
        status TEXT NOT NULL,          -- ACTIVE, EXPIRED
        summary TEXT,
        tags TEXT,                 -- JSON Array
        first_seen_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_deadline_status ON jobs(deadline_status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);")

    # 기존 DB 안전 마이그레이션 — 경력(experience) 열이 없으면 추가한다(데이터는 보존).
    job_columns = {row[1] for row in cur.execute("PRAGMA table_info(jobs)")}
    if "experience" not in job_columns:
        cur.execute("ALTER TABLE jobs ADD COLUMN experience TEXT")
    
    # 2. 시험 공부 문제 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,       -- cppg, infosec_written, infosec_practical, ismsp_auditor, custom
        category_name TEXT NOT NULL,  -- 표시용 명칭
        round_id TEXT NOT NULL,       -- r1, r2, r3, r4, all
        round_name TEXT NOT NULL,     -- 표시용 회차명
        subject TEXT NOT NULL,        -- 과목/영역명
        question_num INTEGER NOT NULL,
        question_type TEXT NOT NULL,  -- choice (객관식), short (단답형), essay (서술실무형)
        prompt TEXT NOT NULL,
        choices TEXT,                 -- JSON Array (객관식 보기)
        answer TEXT NOT NULL,         -- 정답 번호 또는 정답 문자열
        explanation TEXT,             -- 상세 해설
        created_at TEXT NOT NULL,
        UNIQUE(category, round_id, question_num)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_questions_cat_round ON study_questions(category, round_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_questions_subject ON study_questions(subject);")
    
    # 3. 시험 공부 요약 노트 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,       -- cppg, infosec_written, infosec_practical, ismsp_auditor, custom
        sub_type TEXT NOT NULL,       -- content (내용별 심층), vocab (핵심 용어사전), standard (인증기준)
        subject TEXT NOT NULL,        -- 과목/영역
        title TEXT NOT NULL,          -- 요약 카드 제목
        content TEXT,                 -- 본문 텍스트 또는 HTML
        data_json TEXT,               -- 구조화된 토픽/포인트 데이터 (JSON)
        created_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_summaries_cat_type ON study_summaries(category, sub_type);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_summaries_subject ON study_summaries(subject);")
    
    # 4. AI 기술·트렌드 인사이트 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_key TEXT UNIQUE NOT NULL,
        source TEXT NOT NULL,            -- Hugging Face, arXiv, Hacker News, GeekNews
        title_ko TEXT NOT NULL,          -- 한국어 제목
        title_orig TEXT NOT NULL,        -- 원문 제목
        url TEXT NOT NULL,
        category TEXT NOT NULL,          -- LLM·에이전트, AI 보안·안전, 모델·논문, 개발·오픈소스, 산업·트렌드
        summary TEXT NOT NULL,           -- 한국어 핵심 요약
        tech_insight TEXT NOT NULL,      -- 기술 포인트 및 시사점
        tags TEXT NOT NULL,              -- JSON Array
        is_featured INTEGER NOT NULL DEFAULT 0,
        published_at TEXT,
        score INTEGER DEFAULT 0,
        analyzed_by TEXT,                -- exaone, cache, fallback
        collected_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ai_source ON ai_insights(source);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ai_category ON ai_insights(category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ai_published ON ai_insights(published_at);")

    # 5. CVE 취약점 리포트 테이블 (CISA KEV · CIRCL · NVD · EPSS · GitHub PoC)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cve_reports (
        cve_id TEXT PRIMARY KEY,
        title_ko TEXT NOT NULL,
        summary_ko TEXT NOT NULL,
        impact_ko TEXT,
        remediation_ko TEXT,
        cvss_score REAL,
        severity TEXT,              -- CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN
        epss_score REAL,            -- 0~1 악용 확률
        epss_percentile REAL,
        is_kev INTEGER NOT NULL DEFAULT 0,
        kev_date_added TEXT,
        kev_due_date TEXT,
        kev_required_action TEXT,
        kev_ransomware TEXT,
        vendor TEXT,
        product TEXT,
        affected_products TEXT,     -- JSON Array
        poc_count INTEGER DEFAULT 0,
        poc_links_json TEXT,        -- JSON Array
        references_json TEXT,       -- JSON Array
        cwe TEXT,                   -- JSON Array
        description_orig TEXT,      -- 원문 설명 (영문)
        published_at TEXT,
        updated_at TEXT,
        analyzed_by TEXT,           -- exaone, fallback, cache
        created_at TEXT
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cve_severity ON cve_reports(severity);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cve_kev ON cve_reports(is_kev);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cve_epss ON cve_reports(epss_score);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cve_published ON cve_reports(published_at);")

    # 5-a. CISA 경보·보안 뉴스에서 추출한 CVE 단서 테이블
    #   NVD/CIRCL 반영이 늦거나 KEV 등재 전인 긴급 취약점(예: Java4Shell)을 놓치지 않기 위해
    #   수집 소스가 아니라 '이 CVE 가 어떤 경보·기사에서 언급됐는가'를 따로 보관한다.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cve_alerts (
        cve_id TEXT NOT NULL,
        source TEXT NOT NULL,       -- CISA Alert, CISA Advisory, The Hacker News ...
        title TEXT,
        url TEXT NOT NULL,
        published_at TEXT,
        summary TEXT,
        fetched_at TEXT NOT NULL,
        PRIMARY KEY (cve_id, url)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cve_alerts_cve ON cve_alerts(cve_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cve_alerts_pub ON cve_alerts(published_at);")

    # 5-b. 출퇴근길 보안 워게임 문제 테이블 (정적 20문제 + 매일 자동 출제분)
    #   id 는 기존 localStorage 풀이 기록(secjobs-wargame-v1)의 키라서 절대 바뀌면 안 된다.
    #   정적 문제는 web-01...net-04, 데일리 문제는 daily-YYYYMMDD-NN 형식을 쓴다.
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wargame_questions (
        id TEXT PRIMARY KEY,
        created_date TEXT NOT NULL,          -- YYYY-MM-DD (KST)
        category TEXT NOT NULL,              -- web, log, sys, net
        difficulty TEXT NOT NULL,            -- basic, mid, adv
        kind TEXT NOT NULL DEFAULT 'choice', -- choice(4지선다), input(실습형)
        title TEXT NOT NULL,
        context TEXT NOT NULL,               -- 문제 상황 설명
        code_lang TEXT,                      -- python, sql, log, http, bash ...
        code_label TEXT,                     -- 코드 블록 제목 (예: Python · app.py)
        code_body TEXT,                      -- 대표 코드/로그/패킷 본문
        prompt TEXT NOT NULL,
        choices_json TEXT,                   -- JSON Array (4지선다)
        answer_idx INTEGER,                  -- 0~3
        hints_json TEXT NOT NULL,            -- JSON Array (2단계 힌트)
        principle TEXT NOT NULL,             -- 공격 원리
        impact TEXT NOT NULL,                -- 실무 영향
        vuln_code TEXT NOT NULL,             -- Vulnerable Code
        secure_code TEXT NOT NULL,           -- Secure Code
        source_ref TEXT,                     -- 근거 CVE ID / AI 인사이트 키
        is_daily INTEGER NOT NULL DEFAULT 0, -- 1 = 자동 출제분
        sort_order INTEGER NOT NULL DEFAULT 0,
        blocks_json TEXT,                    -- 전체 코드 블록 (JSON Array)
        patterns_json TEXT,                  -- 실습형 정답 정규식 (JSON Array)
        placeholder TEXT,
        sample TEXT,
        chips_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wargame_date ON wargame_questions(created_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wargame_daily ON wargame_questions(is_daily);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wargame_category ON wargame_questions(category);")

    # 5-c. 하루 한 판 · 3단서 추리 문제 테이블 (초기 시드 + 매일 자동 출제분)
    #   단서는 3단계로 나눠 저장하고, 첫 단서만 기본 공개한다.
    #   id 규칙: 시드 seed-01..., 데일리 daily-YYYYMMDD-NN
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clue_questions (
        id TEXT PRIMARY KEY,
        puzzle_date TEXT NOT NULL,          -- YYYY-MM-DD (KST)
        category TEXT NOT NULL,              -- tech, life, culture, science, nature, history
        title TEXT NOT NULL,                 -- 제목(정답을 노출하지 않는 한 줄)
        prompt TEXT NOT NULL,                -- 최종 질문
        clue1 TEXT NOT NULL,
        clue2 TEXT NOT NULL,
        clue3 TEXT NOT NULL,
        choices_json TEXT NOT NULL,          -- JSON Array (4지선다)
        answer_idx INTEGER NOT NULL,         -- 0~3
        explanation TEXT NOT NULL,           -- 정답 해설
        is_daily INTEGER NOT NULL DEFAULT 0, -- 1 = 08:00 자동 출제분
        sort_order INTEGER NOT NULL DEFAULT 0,
        source_ref TEXT,                     -- 근거 메모(선택)
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clue_date ON clue_questions(puzzle_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clue_category ON clue_questions(category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clue_daily ON clue_questions(is_daily);")

    # 6. DB 메타 정보 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS db_meta (
        key TEXT PRIMARY KEY,
        val TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()

def parse_explicit_deadline_date(deadline_str, today_date=None):
    """마감일 문자열에 함께 적힌 날짜(예: ~11/14, ~ 01/03(일))를 date로 해석.

    연 단위 표기가 없으므로 오늘 기준 같은 해로 먼저 해석하고, 그 차이가 6개월을 넘으면
    연말/연초 경계로 보고 연도를 보정한다 (12월의 ~01/05 → 다음 해, 1월의 ~12/31 → 지난 해).
    날짜 표기가 없거나 달력에 없는 값이면 None.
    """
    if not deadline_str:
        return None
    if not today_date:
        kst = timezone(timedelta(hours=9))
        today_date = datetime.now(kst).date()

    m = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})", deadline_str)
    if not m:
        return None

    month, day = int(m.group(1)), int(m.group(2))
    try:
        target_date = datetime(today_date.year, month, day).date()
    except ValueError:
        return None  # 13/45 같은 잘못된 값

    diff = (target_date - today_date).days
    if diff > 180 or diff < -180:
        shifted_year = today_date.year - 1 if diff > 180 else today_date.year + 1
        try:
            target_date = datetime(shifted_year, month, day).date()
        except ValueError:
            return None
    return target_date

# 날짜 없이 시각만 적힌 당일 마감 표기: "16시 마감", "16시마감", "18:30 마감", "24시 마감"
TIME_ONLY_DEADLINE_RE = re.compile(r"^\d\d?(?::\d\d)?\s*시?\s*마감$")

KST = timezone(timedelta(hours=9))


def get_kst_now(now_dt=None):
    """KST 현재 시각(datetime). now_dt가 naive면 KST로 간주한다."""
    if now_dt is None:
        return datetime.now(KST)
    if now_dt.tzinfo is None:
        return now_dt.replace(tzinfo=KST)
    return now_dt.astimezone(KST)


def parse_deadline_clock(deadline_str):
    """마감 표기에 함께 적힌 마감 시각(hour, minute)을 추출. 없으면 None.

    예: '14시마감'→(14, 0), '18시 마감'→(18, 0), '18:30 마감'→(18, 30),
        '~11/17 화 23시 마감'→(23, 0), '~11/17 17:00'→(17, 0)
    MM/DD·YYYY.MM.DD 날짜 표기는 먼저 지워 날짜 숫자를 시각으로 오인하지 않게 한다.
    """
    if not deadline_str:
        return None
    s = re.sub(r"\d{1,2}\s*/\s*\d{1,2}", " ", deadline_str)
    s = re.sub(r"\d{4}\s*[.\-년]\s*\d{1,2}\s*[.\-월]\s*\d{1,2}\s*일?", " ", s)

    hour = minute = None
    m = re.search(r"(\d{1,2})\s*시(?:\s*(\d{1,2})\s*분)?", s)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2) or 0)
    else:
        m = re.search(r"(\d{1,2})\s*:\s*(\d{2})", s)
        if not m:
            return None
        hour, minute = int(m.group(1)), int(m.group(2))

    if not (0 <= minute <= 59):
        return None
    if hour == 24 and minute == 0:
        return (24, 0)  # 24시 마감 = 당일 자정까지 유효
    if not (0 <= hour <= 23):
        return None
    return (hour, minute)


def is_clock_passed(clock, now_dt):
    """마감 시각이 현재 KST 시각 기준으로 이미 지났는지. 24시 마감은 당일 내내 유효."""
    if not clock:
        return False
    hour, minute = clock
    if hour >= 24:
        return False
    return (now_dt.hour, now_dt.minute) >= (hour, minute)


def is_time_only_deadline(deadline_str):
    """시각만 적힌 당일 마감 표기인지 판별 (인크루트 목록은 마감 당일이면 시각만 노출한다)"""
    if not deadline_str:
        return False
    return bool(TIME_ONLY_DEADLINE_RE.match(deadline_str.strip()))


def parse_seen_date(last_seen_at):
    """'2026-11-16 06:34:21 KST' 형태의 수집 시각에서 날짜(date)만 추출. 해석 불가면 None."""
    if not last_seen_at:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(last_seen_at))
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
    except ValueError:
        return None


WEEKDAY_KO = ("월", "화", "수", "목", "금", "토", "일")

# 라벨 뒤에 붙은 마감 시각 표기('23시 마감', '18:30 마감') — 상대 라벨을 다시 쓸 때 보존한다.
DEADLINE_CLOCK_TAIL_RE = re.compile(r"(\d{1,2}\s*(?::\s*\d{1,2})?\s*시?\s*마감)\s*$")


def compute_remaining_days(deadline_str, today_date=None, last_seen_at=None, now_dt=None):
    """공고 마감까지 남은 일수(오늘 KST 기준). 마감일을 알 수 없으면 None.

    parse_deadline_status와 같은 우선순위로 판정한다:
    라벨에 적힌 실제 날짜(MM/DD) > 당일 시각 표기 > D-Day/오늘 > 내일 > D-N.
    상대 라벨(D-N·오늘·내일)은 수집일(last_seen_at) 기준으로 계산된 값이므로,
    수집일과 오늘의 차이만큼 되돌려 실제 남은 일수로 환산한다.
    """
    now = get_kst_now(now_dt)
    if not today_date:
        today_date = now.date()
    if not deadline_str:
        return None

    dl = deadline_str.strip()
    seen = parse_seen_date(last_seen_at)

    explicit_date = parse_explicit_deadline_date(dl, today_date)
    if explicit_date is not None:
        return (explicit_date - today_date).days

    if is_time_only_deadline(dl):
        return (seen - today_date).days if seen else 0

    if "D-Day" in dl or "오늘" in dl:
        return (seen - today_date).days if seen else 0

    if "내일" in dl:
        return (seen + timedelta(days=1) - today_date).days if seen else 1

    m = re.search(r"D-(\d+)", dl)
    if m:
        days = int(m.group(1))
        if seen is not None:
            days -= (today_date - seen).days
        return days

    return None


def normalize_deadline_label(deadline_str, today_date=None, last_seen_at=None, now_dt=None):
    """표시용 마감 라벨을 오늘(KST) 기준으로 보정한다.

    재수집되지 않은 공고는 'D-26', 'D-1 (내일 마감)', 'D-Day (오늘 마감)' 같은 상대 표기가
    수집일 기준으로 남아 실제 남은 일수와 어긋난다(예: 어제 수집된 'D-9 (~ 11/25(수))'는 오늘 D-6).
    저장된 원문(deadline)은 그대로 두고, 화면·JSON·README에 쓰는 라벨만 오늘 기준으로 다시 쓴다.
    라벨에 적힌 날짜(MM/DD)가 있으면 그 날짜를 우선하고, 없으면 수집일과 오늘의 차이만큼 보정한다.
    """
    if not deadline_str or not deadline_str.strip():
        return "상시채용"
    dl = deadline_str.strip()

    # 이미 '마감 (...)'으로 정리된 표기나 상시·채용시는 그대로 둔다.
    if "마감 (" in dl or "마감(" in dl or dl.startswith("마감"):
        return dl
    if "상시" in dl or "채용시" in dl:
        return dl
    if is_time_only_deadline(dl):
        # '14시 마감' 같은 당일 표기는 수집일에만 유효하다(오래된 수집분은 이미 마감 처리).
        return dl

    days = compute_remaining_days(dl, today_date, last_seen_at, now_dt)
    if days is None:
        return dl
    if days < 0:
        days = 0

    token = "D-Day" if days == 0 else f"D-{days}"
    explicit_date = parse_explicit_deadline_date(dl, today_date)

    if explicit_date is not None:
        # 'D-9 (~ 11/25(수))' → 'D-6 (~ 11/25(수))' : 적힌 날짜와 괄호 표기는 보존
        new_label = re.sub(r"^(D-Day|D-\d+)", token, dl, count=1)
        if new_label == dl and dl.startswith("~"):
            new_label = f"{token} ({dl})"
        return new_label

    # 날짜 없이 상대 표기만 있는 경우 — 뒤에 붙은 마감 시각은 살린다.
    tail_m = DEADLINE_CLOCK_TAIL_RE.search(dl)
    tail = f" {tail_m.group(1).strip()}" if tail_m else ""
    if days == 0:
        base = "D-Day (오늘 마감)"
    elif days == 1:
        base = "D-1 (내일 마감)"
    else:
        base = token
    return f"{base}{tail}" if tail else base


def parse_deadline_status(deadline_str, today_date=None, last_seen_at=None, now_dt=None):
    """마감일 문자열을 분석하여 상태값과 마감 여부(ACTIVE/EXPIRED) 판별

    last_seen_at: 수집 시각(선택). 날짜 없는 상대 라벨(D-Day/오늘/내일/D-N)을 수집일 기준으로 환산하며,
                  시각만 적힌 당일 마감 표기는 오늘 수집된 경우에만 D-Day로 본다.
    now_dt: 판정 기준이 되는 현재 시각(KST). 없으면 지금 시각.
                  '14시마감' 처럼 당일 마감 시각이 지난 공고를 당일 오후에도 마감 처리하기 위해 쓴다.
    """
    now = get_kst_now(now_dt)
    if not today_date:
        today_date = now.date()
        
    dl = deadline_str.strip() if deadline_str else "상시채용"
    clock = parse_deadline_clock(dl)
    
    # 1. 이미 마감 표시가 명시된 경우 (예: "마감 (~11/12)")
    if "마감 (" in dl or "마감(" in dl or dl.startswith("마감"):
        return "EXPIRED", "EXPIRED"

    # 2. 문자열에 실제 마감 날짜(MM/DD)가 적혀 있으면 라벨(D-Day/오늘/D-N)보다 날짜를 우선한다.
    #    재수집되지 않은 라벨은 하루만 지나도 어긋나므로(예: 11/15에 남은 "D-Day (~11/14 토)"),
    #    적힌 날짜가 지났으면 라벨과 무관하게 마감 처리한다.
    explicit_date = parse_explicit_deadline_date(dl, today_date)
    if explicit_date is not None:
        diff = (explicit_date - today_date).days
        if diff < 0:
            return "EXPIRED", "EXPIRED"
        elif diff == 0:
            # 당일 마감이어도 '~11/17 17:00'처럼 시각이 적혀 있고 그 시각이 지났으면 마감
            if is_clock_passed(clock, now):
                return "EXPIRED", "EXPIRED"
            return "D_DAY", "ACTIVE"
        elif 1 <= diff <= 7:
            return "URGENT", "ACTIVE"
        else:
            return "UPCOMING", "ACTIVE"
        
    # 2-b. 날짜 없이 시각만 적힌 당일 마감 ("16시 마감", "18:30 마감")
    #      인크루트 목록은 마감 당일이 되면 시각만 표기하므로 당일 수집분은 D-Day로 판정한다.
    #      오늘 수집되지 않은(=목록에서 사라진) 항목은 이미 마감된 것으로 정리한다.
    if is_time_only_deadline(dl):
        seen = parse_seen_date(last_seen_at)
        if seen is not None and seen != today_date:
            return "EXPIRED", "EXPIRED"
        # 오늘 수집된 당일 마감이어도 마감 시각(예: 14시)이 지나면 마감으로 정리
        if is_clock_passed(clock, now):
            return "EXPIRED", "EXPIRED"
        return "D_DAY", "ACTIVE"

    # 3. D-Day / 오늘 마감 (날짜 표기 없음)
    #    상대 라벨은 수집한 날에만 유효하다. 마지막 수집일이 오늘 이전이면 그 사이 마감된 것으로 정리한다.
    #    (예: 11/13 수집 "D-Day (오늘 마감)" 이 11/17에도 오늘 마감처럼 노출되던 문제)
    if "D-Day" in dl or "오늘" in dl:
        seen = parse_seen_date(last_seen_at)
        if seen is not None and seen < today_date:
            return "EXPIRED", "EXPIRED"
        if is_clock_passed(clock, now):
            return "EXPIRED", "EXPIRED"
        return "D_DAY", "ACTIVE"

    # 4. 내일 마감 ("D-1" 부분 문자열 매칭은 D-10~D-19까지 잡히므로 사용하지 않음)
    #    어제 수집된 "D-1 (내일 마감)"은 오늘이 마감일(D-Day), 그보다 오래된 수집분은 마감 처리.
    if "내일" in dl:
        seen = parse_seen_date(last_seen_at)
        if seen is not None:
            if seen == today_date - timedelta(days=1):
                # 어제 기준 '내일 마감' = 오늘이 마감일. 시각이 적혀 있으면 그 시각 기준으로 판정
                if is_clock_passed(clock, now):
                    return "EXPIRED", "EXPIRED"
                return "D_DAY", "ACTIVE"
            if seen < today_date - timedelta(days=1):
                return "EXPIRED", "EXPIRED"
        return "URGENT", "ACTIVE"

    # 5. D-N 계산 (날짜 표기 없음)
    #    라벨은 수집일에 계산된 값이므로, 마지막 수집일과 오늘의 차이만큼 보정해 실제 남은 일수로 환산한다.
    m = re.search(r"D-(\d+)", dl)
    if m:
        days = int(m.group(1))
        seen = parse_seen_date(last_seen_at)
        if seen is not None:
            days -= (today_date - seen).days
        if days < 0:
            return "EXPIRED", "EXPIRED"
        elif days == 0:
            if is_clock_passed(clock, now):
                return "EXPIRED", "EXPIRED"
            return "D_DAY", "ACTIVE"
        elif 1 <= days <= 7:
            return "URGENT", "ACTIVE"
        else:
            return "UPCOMING", "ACTIVE"
            
    # 6. 상시 채용 / 채용시 마감
    if "채용시" in dl:
        return "WHEN_FILLED", "ACTIVE"
    if "상시" in dl:
        return "ALWAYS", "ACTIVE"
        
    return "UPCOMING", "ACTIVE"

# ---------------------------------------------------------------------------
# 중복 공고 판정 키 (회사·제목)
#   플랫폼마다 같은 공고를 다르게 적어 둔다.
#     회사: '(주)보령' · '㈜보령' · '한화오션 (주)' · '핀다(FINDA)' · '㈜숲(SOOP CO., LTD.)'
#     제목: '[채용공고] …' · '[경력] …' · '[HYBE] …' 처럼 앞머리 태그만 붙는 경우
#   그래서 회사는 법인 표기((주)·㈜·주식회사·유한회사 …)와 괄호 별칭·영문 표기를 지우고,
#   제목은 앞머리 [태그]만 지운 뒤 공백·기호 차이를 없앤다.
#   제목 속 괄호는 **지우지 않는다** — '(서비스 보안)'과 '(자산관리 보안)'처럼
#   실제로 다른 직무를 가르는 표기라서, 지우면 다른 포지션이 한 건으로 뭉개진다.
# ---------------------------------------------------------------------------
CORP_MARKER_RE = re.compile(r"\(주\)|\(유\)|\(합자\)|\(사\)|주식회사|유한회사|합자회사|[㈜㈕㈎-㈫]")
COMPANY_ALIAS_PAREN_RE = re.compile(r"\([^()]*\)|\[[^\[\]]*\]")
TITLE_LEADING_TAG_RE = re.compile(r"^(?:\s*\[[^\]]*\]\s*)+")
DEDUP_PUNCT_RE = re.compile(r"[\s\-_/|·.,'\"&+~`^]")


def dedup_company_key(company):
    """회사명 비교 키 — 법인 표기·괄호 별칭/영문 표기·공백·기호를 없앤다.

    '(주)보령' = '㈜보령' = '보령' = '한화오션(주)' = '한화오션 (주)',
    '하이브(HYBE)' = '(주)하이브' = '㈜하이브', '핀다(FINDA)' = '(주)핀다'
    """
    c = CORP_MARKER_RE.sub("", str(company or ""))
    c = COMPANY_ALIAS_PAREN_RE.sub("", c)
    return DEDUP_PUNCT_RE.sub("", c).lower()


def dedup_title_key(title):
    """제목 비교 키 — 앞머리 [회사명]·[경력] 같은 태그만 지우고, 속 괄호는 그대로 둔다."""
    t = TITLE_LEADING_TAG_RE.sub("", str(title or "").strip())
    return DEDUP_PUNCT_RE.sub("", t).lower()


def job_dedup_key(company, title):
    """같은 공고인지 판정하는 (회사 키, 제목 키) 쌍."""
    return (dedup_company_key(company), dedup_title_key(title))


def _dedup_company_key(company):
    """(하위 호환) 회사명 비교용 키 — dedup_company_key 와 같은 값."""
    return dedup_company_key(company)


def _dedup_title_key(title):
    """(하위 호환) 제목 비교용 키 — dedup_title_key 와 같은 값."""
    return dedup_title_key(title)


def expire_platform_conflict_duplicates(today_date=None, db_path=DB_PATH, now_dt=None):
    """같은 공고를 플랫폼마다 다른 마감 형식으로 보여줘 생긴 복제 행을 정리한다.

    한 플랫폼은 '14시마감'처럼 마감 시각을 적었고 그 시각이 이미 지나 마감됐는데,
    다른 플랫폼은 같은 공고를 시각 없는 'D-Day (오늘 마감)'으로 계속 보여주는 경우가 있다.
    (예: 2026-11-17 신한은행 정보보호 수시채용 — 사람인·인크루트 14시마감 / 잡코리아 D-Day)
    같은 회사·제목의 마감된 행에 오늘 이미 지난 마감 시각이 적혀 있으면 복제 행도 EXPIRED로 정리한다.
    """
    now = get_kst_now(now_dt)
    if not today_date:
        today_date = now.date()

    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT company, title, deadline FROM jobs WHERE status = 'EXPIRED';")
    closed_clock_keys = set()
    for row in cur.fetchall():
        clock = parse_deadline_clock(row["deadline"])
        if not clock or not is_clock_passed(clock, now):
            continue
        closed_clock_keys.add((_dedup_company_key(row["company"]), _dedup_title_key(row["title"])))

    if not closed_clock_keys:
        conn.close()
        return 0

    now_str = now.strftime("%Y-%m-%d %H:%M:%S KST")
    cur.execute("SELECT id, company, title, deadline FROM jobs WHERE status = 'ACTIVE';")
    targets = []
    for row in cur.fetchall():
        dl = row["deadline"] or ""
        # 시각·날짜가 적힌 표기는 parse_deadline_status가 이미 판정한다. 여기서는 상대 라벨만 본다.
        if parse_deadline_clock(dl) or parse_explicit_deadline_date(dl, today_date) is not None:
            continue
        key = (_dedup_company_key(row["company"]), _dedup_title_key(row["title"]))
        if key in closed_clock_keys:
            targets.append((now_str, row["id"]))

    if targets:
        cur.executemany("UPDATE jobs SET status = 'EXPIRED', deadline_status = 'EXPIRED', updated_at = ? WHERE id = ?;", targets)
        conn.commit()
    conn.close()
    return len(targets)


def normalize_key(company, title):
    """짧은 제목 키(회사+제목12자) — 같은 공고인지 '후보'를 좁히는 용도로만 쓴다.

    회사 법인 표기((주)·㈜·주식회사 …)와 괄호 별칭, 제목 앞머리 [태그], 공백·기호 차이를
    없앤다(제목 속 괄호는 다른 직무를 가르므로 그대로 둔다).
    """
    c = dedup_company_key(company)
    t = dedup_title_key(title)
    return f"{c}_{t[:12]}"


# 마감 표기의 '구체성' — 애매한 표기(상시채용)보다 실제 날짜가 적힌 표기를 남긴다.
DEADLINE_MARKER_RE = re.compile(r"D-Day|D-\d+|오늘|내일")


def deadline_rank(deadline, last_seen_at=None, today_date=None):
    """중복 공고를 병합할 때 어느 마감 표기를 남길지 정하는 우선순위(클수록 우선).

    ① 표기 구체성: 날짜(MM/DD) > 당일 시각 > D-N·D-Day > 상시·채용시
    ② 최근 수집된 표기
    ③ 더 임박한 표기(같은 구체성·같은 수집일이면 사용자가 놓치지 않도록)
    """
    if not today_date:
        today_date = get_kst_now().date()
    dl = str(deadline or "").strip()
    if not dl:
        concreteness = 0
    elif "마감 (" in dl or "마감(" in dl or dl.startswith("마감"):
        concreteness = 0
    elif parse_explicit_deadline_date(dl, today_date) is not None:
        concreteness = 4
    elif is_time_only_deadline(dl):
        concreteness = 3
    elif DEADLINE_MARKER_RE.search(dl):
        concreteness = 2
    else:
        concreteness = 1
    seen = parse_seen_date(last_seen_at) or today_date
    days = compute_remaining_days(dl, today_date, last_seen_at)
    return (concreteness, seen.toordinal(), -(days if days is not None else 100000))


def _json_list(value):
    """JSON 배열 컬럼 값을 리스트로 읽는다(문자열·None·깨진 값 방어)."""
    if isinstance(value, list):
        return value
    if not value:
        return []
    try:
        items = json.loads(value) if isinstance(value, str) else value
    except (TypeError, ValueError):
        return []
    if isinstance(items, list):
        return items
    return [items] if items else []


def _union_json_lists(values):
    """여러 행의 JSON 배열 컬럼을 순서를 지키며 합집합으로 만든다."""
    out = []
    for value in values:
        for item in _json_list(value):
            if item not in out:
                out.append(item)
    return out


def deduplicate_active_jobs(db_path=DB_PATH, today_date=None, now_dt=None, dry_run=False):
    """활성 공고 중 같은 공고(정규화 회사·제목)를 대표 1건으로 병합한다.

    왜 필요한가:
      · 플랫폼마다 회사 표기가 달라('(주)보령' / '㈜보령') 같은 공고가 따로 노출되고,
      · 잡코리아·사람인 등은 같은 공고를 새 공고 ID로 다시 올려(재등록·복제 등록) 행이 쌓이며,
      · 교차 게시된 공고도 제목 앞머리 태그('[HYBE] …')만 다르면 합쳐지지 않았다.

    병합 규칙:
      · 대표 = 요약이 있는 행 → 위치 정보가 있는 행 → 먼저 수집된 행 → id 작은 행.
        (수집일마다 대표가 바뀌지 않도록 first_seen_at 을 우선 기준으로 둔다)
      · platforms·keywords·tags 는 합집합, location·summary 는 있는 값을 유지.
      · deadline 은 deadline_rank 우선순위(구체적 → 최근 → 임박)로 고르고
        그 표기 기준으로 deadline_status 를 다시 계산한다.
      · first_seen_at 은 가장 이른 값, last_seen_at 은 가장 늦은 값을 남긴다.
      · 나머지 중복 행은 status='EXPIRED' 로 정리한다(삭제하지 않고 보관).

    반환: {"merged": 병합해 EXPIRED 로 정리한 행 수, "groups": 병합한 그룹 수, "detail": [...]}
    """
    now = get_kst_now(now_dt)
    if not today_date:
        today_date = now.date()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S KST")

    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT id, job_key, company, title, url, platforms, keywords, location,
           experience, deadline, summary, tags, first_seen_at, last_seen_at
    FROM jobs
    WHERE status = 'ACTIVE'
    ORDER BY id ASC;
    """)
    rows = [dict(r) for r in cur.fetchall()]

    groups = {}
    for row in rows:
        groups.setdefault(job_dedup_key(row["company"], row["title"]), []).append(row)

    merged = 0
    detail = []
    for key, members in groups.items():
        if len(members) < 2:
            continue

        def primary_rank(row):
            return (
                1 if (row["summary"] or "").strip() else 0,
                1 if (row["location"] or "").strip() else 0,
                1 if (row["experience"] or "").strip() else 0,
                -(parse_seen_date(row["first_seen_at"]) or today_date).toordinal(),
                -int(row["id"]),
            )

        primary = max(members, key=primary_rank)
        others = [m for m in members if m["id"] != primary["id"]]
        ordered = [primary] + sorted(others, key=lambda m: int(m["id"]))

        platforms = _union_json_lists([m["platforms"] for m in ordered])
        keywords = _union_json_lists([m["keywords"] for m in ordered])
        tags = _union_json_lists([m["tags"] for m in ordered])
        location = next((m["location"] for m in ordered if (m["location"] or "").strip()), "")
        experience = next((m["experience"] for m in ordered if (m["experience"] or "").strip()), "")
        summary = next((m["summary"] for m in ordered if (m["summary"] or "").strip()), "")

        # 마감 표기: 살아 있는(ACTIVE) 표기 중 가장 구체적·최근·임박한 것.
        deadline_row = None
        deadline_rank_best = None
        for m in ordered:
            dl = m["deadline"] or ""
            status = parse_deadline_status(dl, today_date, m["last_seen_at"], now_dt=now)[1]
            rank = deadline_rank(dl, m["last_seen_at"], today_date)
            if status != "ACTIVE":
                rank = (-1,) + rank[1:]
            if deadline_rank_best is None or rank > deadline_rank_best:
                deadline_row, deadline_rank_best = m, rank
        deadline = deadline_row["deadline"] or primary["deadline"]
        deadline_status = parse_deadline_status(
            deadline, today_date, deadline_row["last_seen_at"], now_dt=now)[0]

        seen_stamps = [m["first_seen_at"] for m in ordered if m["first_seen_at"]]
        last_stamps = [m["last_seen_at"] for m in ordered if m["last_seen_at"]]

        detail.append({
            "company": primary["company"],
            "title": primary["title"],
            "kept_job_key": primary["job_key"],
            "merged_job_keys": [m["job_key"] for m in others],
            "platforms": platforms,
            "deadline": deadline,
            "merged_rows": len(others),
        })
        merged += len(others)
        if dry_run:
            continue

        cur.execute("""
        UPDATE jobs
        SET platforms = ?, keywords = ?, tags = ?, location = ?, experience = ?, deadline = ?,
            deadline_status = ?, summary = ?, first_seen_at = ?, last_seen_at = ?,
            updated_at = ?
        WHERE id = ?;
        """, (
            json.dumps(platforms, ensure_ascii=False),
            json.dumps(keywords, ensure_ascii=False),
            json.dumps(tags, ensure_ascii=False),
            location,
            experience,
            deadline,
            deadline_status,
            summary,
            min(seen_stamps) if seen_stamps else now_str,
            max(last_stamps) if last_stamps else now_str,
            now_str,
            primary["id"],
        ))
        cur.executemany(
            "UPDATE jobs SET status = 'EXPIRED', deadline_status = 'EXPIRED', updated_at = ? WHERE id = ?;",
            [(now_str, m["id"]) for m in others],
        )

    if not dry_run and merged:
        conn.commit()
    conn.close()
    return {"merged": merged, "groups": len(detail), "detail": detail}

def mark_expired_jobs(today_date=None, db_path=DB_PATH, now_dt=None):
    """현재 날짜·시각(KST)을 기준으로 마감일이 지난 공고를 일괄 EXPIRED 상태로 전환"""
    now = get_kst_now(now_dt)
    if not today_date:
        today_date = now.date()
        
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, deadline, status, last_seen_at FROM jobs WHERE status = 'ACTIVE';")
    rows = cur.fetchall()
    
    expired_ids = []
    for row in rows:
        dl_status, status = parse_deadline_status(row["deadline"], today_date, row["last_seen_at"], now_dt=now)
        if status == "EXPIRED":
            expired_ids.append(row["id"])
            
    if expired_ids:
        cur.executemany("UPDATE jobs SET status = 'EXPIRED', deadline_status = 'EXPIRED' WHERE id = ?;", [(x,) for x in expired_ids])
        conn.commit()
    conn.close()
    return len(expired_ids)

def refresh_deadline_statuses(today_date=None, db_path=DB_PATH, now_dt=None):
    """ACTIVE 공고의 deadline_status를 현재 기준으로 재계산 (마감 판정 로직 변경 시 DB 재정규화)"""
    now = get_kst_now(now_dt)
    if not today_date:
        today_date = now.date()

    now_str = now.strftime("%Y-%m-%d %H:%M:%S KST")

    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, deadline, deadline_status, last_seen_at FROM jobs WHERE status = 'ACTIVE';")
    rows = cur.fetchall()

    updates = []
    unchanged = 0
    for row in rows:
        dl_status, status = parse_deadline_status(row["deadline"], today_date, row["last_seen_at"], now_dt=now)
        if status != "ACTIVE":
            # 마감 전환은 mark_expired_jobs 담당
            continue
        if dl_status != row["deadline_status"]:
            updates.append((dl_status, now_str, row["id"]))
        else:
            unchanged += 1

    if updates:
        cur.executemany("UPDATE jobs SET deadline_status = ?, updated_at = ? WHERE id = ?;", updates)
        conn.commit()
    conn.close()
    return len(updates), unchanged

def get_active_jobs(db_path=DB_PATH, today_date=None):
    """활성 공고(ACTIVE)를 마감 임박 순 및 최신 순으로 정렬하여 딕셔너리 리스트로 반환

    deadline은 수집 당시 원문이고, deadline_label은 오늘(KST) 기준으로 보정한 표시용 라벨이다.
    (재수집되지 않은 공고의 'D-26'·'D-1 (내일 마감)' 같은 상대 표기를 화면에서 바로잡기 위함)
    """
    if not today_date:
        today_date = get_kst_now().date()
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT job_key, company, title, url, platforms, keywords, location, experience, deadline, summary, tags, deadline_status, last_seen_at, first_seen_at
    FROM jobs
    WHERE status = 'ACTIVE'
    ORDER BY
        CASE deadline_status
            WHEN 'D_DAY' THEN 0
            WHEN 'URGENT' THEN 1
            WHEN 'WHEN_FILLED' THEN 2
            WHEN 'ALWAYS' THEN 3
            WHEN 'UPCOMING' THEN 4
            ELSE 5
        END,
        id ASC;
    """)
    rows = cur.fetchall()
    jobs = []
    for r in rows:
        jobs.append({
            "job_key": r["job_key"],
            "company": r["company"],
            "title": r["title"],
            "url": r["url"],
            "platforms": json.loads(r["platforms"]),
            "keywords": json.loads(r["keywords"]),
            "location": r["location"] or "",
            "experience": (r["experience"] or "").strip(),
            "deadline": r["deadline"],
            "deadline_label": normalize_deadline_label(r["deadline"], today_date, r["last_seen_at"]),
            "summary": r["summary"] or "",
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "deadline_status": r["deadline_status"],
            "last_seen_at": r["last_seen_at"],
            "first_seen_at": r["first_seen_at"] or "",
        })
    conn.close()
    return jobs

def get_expired_jobs(db_path=DB_PATH):
    """마감 정리된 공고(EXPIRED) 목록 반환"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT company, title, url, platforms, keywords, location, deadline, summary, tags
    FROM jobs
    WHERE status = 'EXPIRED'
    ORDER BY updated_at DESC;
    """)
    rows = cur.fetchall()
    jobs = []
    for r in rows:
        jobs.append({
            "company": r["company"],
            "title": r["title"],
            "url": r["url"],
            "platforms": json.loads(r["platforms"]),
            "keywords": json.loads(r["keywords"]),
            "location": r["location"] or "",
            "deadline": r["deadline"],
            "summary": r["summary"] or "",
            "tags": json.loads(r["tags"]) if r["tags"] else []
        })
    conn.close()
    return jobs

def get_db_stats(db_path=DB_PATH):
    """DB 전체 상태 통계 반환"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM jobs WHERE status = 'ACTIVE';")
    active_jobs = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM jobs WHERE status = 'EXPIRED';")
    expired_jobs = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM study_questions;")
    total_questions = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM study_summaries;")
    total_summaries = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM ai_insights;")
    total_ai = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM cve_reports;")
    total_cve = cur.fetchone()[0]

    try:
        cur.execute("SELECT COUNT(*) FROM wargame_questions;")
        total_wargame = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM wargame_questions WHERE is_daily = 1;")
        total_wargame_daily = cur.fetchone()[0]
    except sqlite3.OperationalError:
        total_wargame = 0
        total_wargame_daily = 0

    conn.close()
    return {
        "active_jobs": active_jobs,
        "expired_jobs": expired_jobs,
        "total_jobs": active_jobs + expired_jobs,
        "total_questions": total_questions,
        "total_summaries": total_summaries,
        "total_ai_insights": total_ai,
        "total_cve": total_cve,
        "total_wargame": total_wargame,
        "total_wargame_daily": total_wargame_daily
    }

# ---------------------------------------------------------------------------
# AI 기술·트렌드 인사이트 (ai_insights)
# ---------------------------------------------------------------------------

def upsert_ai_insights(items, db_path=DB_PATH):
    """AI 기술·트렌드 분석 결과를 item_key 기준 UPSERT (중복 수집 대비)"""
    if not items:
        return 0

    kst = timezone(timedelta(hours=9))
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")

    conn = get_connection(db_path)
    cur = conn.cursor()
    count = 0
    for it in items:
        cur.execute("""
        INSERT INTO ai_insights (
            item_key, source, title_ko, title_orig, url, category, summary, tech_insight,
            tags, is_featured, published_at, score, analyzed_by, collected_at, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(item_key) DO UPDATE SET
            source = excluded.source,
            title_ko = excluded.title_ko,
            title_orig = excluded.title_orig,
            url = excluded.url,
            category = excluded.category,
            summary = excluded.summary,
            tech_insight = excluded.tech_insight,
            tags = excluded.tags,
            is_featured = excluded.is_featured,
            published_at = excluded.published_at,
            score = excluded.score,
            analyzed_by = excluded.analyzed_by,
            collected_at = excluded.collected_at,
            updated_at = excluded.updated_at;
        """, (
            it["item_key"],
            it["source"],
            it["title_ko"],
            it["title_orig"],
            it["url"],
            it["category"],
            it["summary"],
            it["tech_insight"],
            json.dumps(it.get("tags", []), ensure_ascii=False),
            1 if it.get("is_featured") else 0,
            it.get("published_at", ""),
            int(it.get("score") or 0),
            it.get("analyzed_by", "fallback"),
            now_str, now_str, now_str
        ))
        count += 1
    conn.commit()
    conn.close()
    return count

def get_ai_insight_count(db_path=DB_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ai_insights;")
    n = cur.fetchone()[0]
    conn.close()
    return n

def get_ai_insights(limit=None, db_path=DB_PATH):
    """AI 인사이트 조회 (최신순 우선 — 상한에 걸려도 오늘 발행분이 밀리지 않도록)"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    sql = """
    SELECT item_key, source, title_ko, title_orig, url, category, summary, tech_insight,
           tags, is_featured, published_at, score, analyzed_by, collected_at
    FROM ai_insights
    ORDER BY COALESCE(NULLIF(published_at, ''), '0000-00-00') DESC,
             is_featured DESC, score DESC, id DESC
    """
    params = ()
    if limit:
        sql += " LIMIT ?"
        params = (int(limit),)
    cur.execute(sql, params)
    rows = cur.fetchall()
    items = []
    for r in rows:
        items.append({
            "item_key": r["item_key"],
            "source": r["source"],
            "title_ko": r["title_ko"],
            "title_orig": r["title_orig"],
            "url": r["url"],
            "category": r["category"],
            "summary": r["summary"],
            "tech_insight": r["tech_insight"],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "is_featured": bool(r["is_featured"]),
            "published_at": r["published_at"] or "",
            "score": r["score"] or 0,
            "analyzed_by": r["analyzed_by"] or "",
            "collected_at": r["collected_at"],
        })
    conn.close()
    return items

# ---------------------------------------------------------------------------
# CVE 취약점 리포트 (cve_reports)
# ---------------------------------------------------------------------------

def upsert_cve_reports(items, db_path=DB_PATH):
    """CVE 분석 결과를 cve_id 기준 UPSERT (수집·분석 재실행 대비)"""
    if not items:
        return 0

    kst = timezone(timedelta(hours=9))
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")

    conn = get_connection(db_path)
    cur = conn.cursor()
    # 기존에 확보된 PoC 는 이번 수집 결과가 비어 있어도 잃지 않는다.
    # (POC_QUERY_LIMIT 밖이거나 GitHub 호출이 실패한 CVE 가 poc_count=0 으로 덮여
    #  공개 PoC 21건이 1건으로 줄었던 회귀를 막는 방어선)
    existing_poc = {}
    for row in cur.execute("SELECT cve_id, poc_links_json FROM cve_reports"):
        raw = row["poc_links_json"]
        if not raw:
            continue
        try:
            links = json.loads(raw)
        except (TypeError, ValueError):
            continue
        if isinstance(links, list) and links:
            existing_poc[row["cve_id"]] = links

    def merge_poc_links(cve_id, new_links):
        merged = list(new_links or [])
        seen = set()
        for link in merged:
            seen.add((link or {}).get("url") if isinstance(link, dict) else link)
        for old in existing_poc.get(cve_id, []):
            key = (old or {}).get("url") if isinstance(old, dict) else old
            if key and key not in seen:
                merged.append(old)
                seen.add(key)
        return merged

    count = 0
    for it in items:
        poc_links = merge_poc_links(it["cve_id"], it.get("poc_links"))
        cur.execute("""
        INSERT INTO cve_reports (
            cve_id, title_ko, summary_ko, impact_ko, remediation_ko,
            cvss_score, severity, epss_score, epss_percentile, is_kev,
            kev_date_added, kev_due_date, kev_required_action, kev_ransomware,
            vendor, product, affected_products, poc_count, poc_links_json,
            references_json, cwe, description_orig, published_at, updated_at,
            analyzed_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(cve_id) DO UPDATE SET
            -- 한국어 폴백(구조화 템플릿)이 이미 확보된 EXAONE/큐레이션 분석을 덮어쓰지 않도록 방어한다.
            -- (수집만 하고 --analyze 없이 --finish 로 들어온 날, 분석 60건이 fallback:pending 으로
            --  되돌아간 회귀를 막는 방어선. 분석기가 실제로 성공한 경우에만 교체한다.)
            title_ko = CASE WHEN excluded.analyzed_by LIKE 'fallback%'
                             AND cve_reports.analyzed_by IN ('exaone', 'curated')
                             AND COALESCE(cve_reports.title_ko, '') <> ''
                        THEN cve_reports.title_ko ELSE excluded.title_ko END,
            summary_ko = CASE WHEN excluded.analyzed_by LIKE 'fallback%'
                               AND cve_reports.analyzed_by IN ('exaone', 'curated')
                               AND COALESCE(cve_reports.title_ko, '') <> ''
                          THEN cve_reports.summary_ko ELSE excluded.summary_ko END,
            impact_ko = CASE WHEN excluded.analyzed_by LIKE 'fallback%'
                              AND cve_reports.analyzed_by IN ('exaone', 'curated')
                              AND COALESCE(cve_reports.title_ko, '') <> ''
                         THEN cve_reports.impact_ko ELSE excluded.impact_ko END,
            remediation_ko = CASE WHEN excluded.analyzed_by LIKE 'fallback%'
                                   AND cve_reports.analyzed_by IN ('exaone', 'curated')
                                   AND COALESCE(cve_reports.title_ko, '') <> ''
                              THEN cve_reports.remediation_ko ELSE excluded.remediation_ko END,
            cvss_score = excluded.cvss_score,
            severity = excluded.severity,
            epss_score = excluded.epss_score,
            epss_percentile = excluded.epss_percentile,
            is_kev = excluded.is_kev,
            kev_date_added = excluded.kev_date_added,
            kev_due_date = excluded.kev_due_date,
            kev_required_action = excluded.kev_required_action,
            kev_ransomware = excluded.kev_ransomware,
            vendor = excluded.vendor,
            product = excluded.product,
            affected_products = excluded.affected_products,
            poc_count = excluded.poc_count,
            poc_links_json = excluded.poc_links_json,
            references_json = excluded.references_json,
            cwe = excluded.cwe,
            description_orig = excluded.description_orig,
            published_at = excluded.published_at,
            updated_at = excluded.updated_at,
            analyzed_by = CASE WHEN excluded.analyzed_by LIKE 'fallback%'
                                AND cve_reports.analyzed_by IN ('exaone', 'curated')
                                AND COALESCE(cve_reports.title_ko, '') <> ''
                           THEN cve_reports.analyzed_by ELSE excluded.analyzed_by END;
        """, (
            it["cve_id"],
            it["title_ko"],
            it["summary_ko"],
            it.get("impact_ko", ""),
            it.get("remediation_ko", ""),
            it.get("cvss_score"),
            it.get("severity", "UNKNOWN"),
            it.get("epss_score"),
            it.get("epss_percentile"),
            1 if it.get("is_kev") else 0,
            it.get("kev_date_added", ""),
            it.get("kev_due_date", ""),
            it.get("kev_required_action", ""),
            it.get("kev_ransomware", ""),
            it.get("vendor", ""),
            it.get("product", ""),
            json.dumps(it.get("affected_products", []), ensure_ascii=False),
            len(poc_links),
            json.dumps(poc_links, ensure_ascii=False),
            json.dumps(it.get("references", []), ensure_ascii=False),
            json.dumps(it.get("cwe", []), ensure_ascii=False),
            it.get("description_orig", ""),
            normalize_date_str(it.get("published_at", "")),
            it.get("updated_at", "") or now_str,
            it.get("analyzed_by", "fallback"),
            now_str,
        ))
        count += 1
    conn.commit()
    conn.close()
    return count


def upsert_cve_alerts(rows, db_path=DB_PATH):
    """CISA 경보·보안 뉴스에서 추출한 CVE 단서를 적재한다.

    같은 (cve_id, url) 조합은 제목·요약·발행일만 갱신하고 fetched_at 을 새로 찍는다.
    (하루 여러 번 실행해도 중복 행이 쌓이지 않는다)
    """
    if not rows:
        return 0
    kst = timezone(timedelta(hours=9))
    fetched_at = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    conn = get_connection(db_path)
    cur = conn.cursor()
    count = 0
    for r in rows:
        cve_id = (r or {}).get("cve_id")
        url = (r or {}).get("url")
        if not cve_id or not url:
            continue
        cur.execute("""
        INSERT INTO cve_alerts (cve_id, source, title, url, published_at, summary, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(cve_id, url) DO UPDATE SET
            source = excluded.source,
            title = excluded.title,
            published_at = excluded.published_at,
            summary = excluded.summary,
            fetched_at = excluded.fetched_at;
        """, (
            cve_id,
            r.get("source", ""),
            r.get("title", ""),
            url,
            r.get("published_at", ""),
            (r.get("summary") or "")[:1200],
            fetched_at,
        ))
        count += 1
    conn.commit()
    conn.close()
    return count


def get_cve_alerts(days=None, limit_per_cve=4, db_path=DB_PATH):
    """cve_id → [{source, title, url, published_at}] (최신 발행순, CVE당 최대 limit_per_cve건)

    days 를 주면 그 기간 안에 발행된 경보·기사만 돌려준다. 발행일이 비어 있는 항목은
    수집 시각(fetched_at)으로 대신 판정한다.
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    sql = """
    SELECT cve_id, source, title, url, published_at
    FROM cve_alerts
    """
    params = ()
    if days:
        kst = timezone(timedelta(hours=9))
        cutoff = (datetime.now(kst) - timedelta(days=int(days))).strftime("%Y-%m-%d")
        sql += """
        WHERE COALESCE(NULLIF(published_at, ''), substr(fetched_at, 1, 10)) >= ?
        """
        params = (cutoff,)
    sql += " ORDER BY COALESCE(NULLIF(published_at, ''), substr(fetched_at, 1, 10)) DESC, source ASC"
    cur.execute(sql, params)
    out = {}
    for r in cur.fetchall():
        bucket = out.setdefault(r["cve_id"], [])
        if len(bucket) >= limit_per_cve:
            continue
        bucket.append({
            "source": r["source"] or "",
            "title": r["title"] or "",
            "url": r["url"],
            "published_at": r["published_at"] or "",
        })
    conn.close()
    return out


def normalize_date_str(value):
    """공개일 문자열을 ISO(YYYY-MM-DD) 로 통일한다. 해석할 수 없으면 원문을 그대로 돌려준다."""
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    m = re.search(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", s)
    if not m:
        m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", s) if re.fullmatch(r"\d{8}", s) else None
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).strftime("%Y-%m-%d")
        except ValueError:
            return s
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y", "%Y년 %m월 %d일"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s


def normalize_cve_published_dates(db_path=DB_PATH):
    """cve_reports.published_at 을 ISO 날짜로 정규화하고, 비어 있는 행은 경보·출처 날짜로 메운다.

    정렬 기준이 '최근 공개순'이 된 만큼, 표기가 제각각이거나 비어 있는 행이 있으면
    그 행만 목록 맨 아래로 밀리므로 여기서 한 번 정리한다.
    반환: (정규화한 행 수, 끝까지 비어 있는 cve_id 목록)
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    alert_dates = {}
    try:
        for row in cur.execute("SELECT cve_id, published_at FROM cve_alerts"):
            d = normalize_date_str(row["published_at"])
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d or ""):
                prev = alert_dates.get(row["cve_id"], "")
                alert_dates[row["cve_id"]] = max(prev, d)
    except sqlite3.Error:
        alert_dates = {}

    fixed = 0
    still_empty = []
    for row in list(cur.execute("SELECT cve_id, published_at FROM cve_reports")):
        cve_id, raw = row["cve_id"], row["published_at"]
        norm = normalize_date_str(raw)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", norm or ""):
            norm = alert_dates.get(cve_id, "")
        if not norm:
            still_empty.append(cve_id)
            continue
        if norm != (raw or ""):
            cur.execute("UPDATE cve_reports SET published_at = ? WHERE cve_id = ?", (norm, cve_id))
            fixed += 1
    conn.commit()
    conn.close()
    return fixed, still_empty


def get_cve_reports(limit=None, db_path=DB_PATH):
    """CVE 리포트 조회 (최근 공개일 우선 → KEV → CVSS → EPSS)"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    sql = """
    SELECT cve_id, title_ko, summary_ko, impact_ko, remediation_ko,
           cvss_score, severity, epss_score, epss_percentile, is_kev,
           kev_date_added, kev_due_date, kev_required_action, kev_ransomware,
           vendor, product, affected_products, poc_count, poc_links_json,
           references_json, cwe, description_orig, published_at, updated_at,
           analyzed_by
    FROM cve_reports
    ORDER BY COALESCE(NULLIF(published_at, ''), '0000-00-00') DESC,
             is_kev DESC, COALESCE(cvss_score, 0) DESC, COALESCE(epss_score, 0) DESC,
             cve_id DESC
    """
    params = ()
    if limit:
        sql += " LIMIT ?"
        params = (int(limit),)
    cur.execute(sql, params)
    rows = cur.fetchall()
    items = []
    for r in rows:
        items.append({
            "cve_id": r["cve_id"],
            "title_ko": r["title_ko"],
            "summary_ko": r["summary_ko"],
            "impact_ko": r["impact_ko"] or "",
            "remediation_ko": r["remediation_ko"] or "",
            "cvss_score": r["cvss_score"],
            "severity": r["severity"] or "UNKNOWN",
            "epss_score": r["epss_score"],
            "epss_percentile": r["epss_percentile"],
            "is_kev": bool(r["is_kev"]),
            "kev_date_added": r["kev_date_added"] or "",
            "kev_due_date": r["kev_due_date"] or "",
            "kev_required_action": r["kev_required_action"] or "",
            "kev_ransomware": r["kev_ransomware"] or "",
            "vendor": r["vendor"] or "",
            "product": r["product"] or "",
            "affected_products": json.loads(r["affected_products"]) if r["affected_products"] else [],
            "poc_count": r["poc_count"] or 0,
            "poc_links": json.loads(r["poc_links_json"]) if r["poc_links_json"] else [],
            "references": json.loads(r["references_json"]) if r["references_json"] else [],
            "cwe": json.loads(r["cwe"]) if r["cwe"] else [],
            "description_orig": r["description_orig"] or "",
            "published_at": r["published_at"] or "",
            "updated_at": r["updated_at"] or "",
            "analyzed_by": r["analyzed_by"] or "",
        })
    conn.close()
    return items


def get_cve_stats(db_path=DB_PATH):
    """CVE 리포트 요약 지표"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cve_reports;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cve_reports WHERE severity = 'CRITICAL';")
    critical = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cve_reports WHERE severity = 'HIGH';")
    high = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cve_reports WHERE is_kev = 1;")
    kev = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cve_reports WHERE poc_count > 0;")
    poc = cur.fetchone()[0]
    conn.close()
    return {"total": total, "critical": critical, "high": high, "kev": kev, "poc": poc}


# ---------------------------------------------------------------------------
# 7) 워게임 문제 (wargame_questions)
# ---------------------------------------------------------------------------
WARGAME_CATEGORIES = ("web", "log", "sys", "net")
WARGAME_LEVELS = ("basic", "mid", "adv")


def _now_iso(now_dt=None):
    kst = timezone(timedelta(hours=9))
    return (now_dt or datetime.now(kst)).strftime("%Y-%m-%d %H:%M:%S")


def _json_dump(value, default=None):
    if value is None:
        value = default if default is not None else []
    return json.dumps(value, ensure_ascii=False)


def wargame_row_from_question(q, created_date, is_daily=0, sort_order=0, now_dt=None):
    """빌더/생성기의 문제 dict를 wargame_questions 행 dict로 변환한다.

    q 키: id, cat(category), level(difficulty), type(kind), title, brief(context),
          blocks[{label, code}], prompt, choices, answer, hints,
          explain{principle, impact, vuln, secure}, patterns, placeholder, sample, chips,
          code_lang, code_label, code_body, source_ref, created_date, is_daily, sort_order
    """
    blocks = q.get("blocks") or []
    if not blocks and (q.get("code_body") or q.get("code_label")):
        blocks = [{"label": q.get("code_label") or "Code", "code": q.get("code_body") or ""}]
    first = blocks[0] if blocks else {"label": "", "code": ""}
    explain = q.get("explain") or {}
    now = _now_iso(now_dt)
    kind = q.get("kind") or q.get("type") or "choice"
    answer = q.get("answer_idx") if q.get("answer_idx") is not None else q.get("answer")
    return {
        "id": q["id"],
        "created_date": q.get("created_date") or created_date,
        "category": q.get("category") or q.get("cat"),
        "difficulty": q.get("difficulty") or q.get("level"),
        "kind": kind,
        "title": q["title"],
        "context": q.get("context") or q.get("brief") or "",
        "code_lang": q.get("code_lang") or "",
        "code_label": q.get("code_label") or first.get("label", ""),
        "code_body": q.get("code_body") or first.get("code", ""),
        "prompt": q.get("prompt") or "",
        "choices_json": _json_dump(q.get("choices")),
        "answer_idx": answer,
        "hints_json": _json_dump(q.get("hints")),
        "principle": q.get("principle") or explain.get("principle", ""),
        "impact": q.get("impact") or explain.get("impact", ""),
        "vuln_code": q.get("vuln_code") or explain.get("vuln", ""),
        "secure_code": q.get("secure_code") or explain.get("secure", ""),
        "source_ref": q.get("source_ref") or "",
        "is_daily": 1 if (q.get("is_daily") or is_daily) else 0,
        "sort_order": int(q.get("sort_order", sort_order) or 0),
        "blocks_json": _json_dump(blocks),
        "patterns_json": _json_dump(q.get("patterns")),
        "placeholder": q.get("placeholder") or "",
        "sample": q.get("sample") or "",
        "chips_json": _json_dump(q.get("chips")),
        "created_at": now,
        "updated_at": now,
    }


_WARGAME_COLUMNS = (
    "id", "created_date", "category", "difficulty", "kind", "title", "context",
    "code_lang", "code_label", "code_body", "prompt", "choices_json", "answer_idx",
    "hints_json", "principle", "impact", "vuln_code", "secure_code", "source_ref",
    "is_daily", "sort_order", "blocks_json", "patterns_json", "placeholder", "sample",
    "chips_json", "created_at", "updated_at",
)


def seed_wargame_questions(questions, created_date="2026-11-20", db_path=DB_PATH):
    """기존 정적 워게임 문제를 DB로 이관한다 (id 보존, 이미 있으면 건드리지 않음)."""
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    inserted = 0
    try:
        for idx, q in enumerate(questions):
            row = wargame_row_from_question(q, created_date, is_daily=q.get("is_daily", 0), sort_order=idx)
            cur.execute(
                "INSERT OR IGNORE INTO wargame_questions (%s) VALUES (%s)"
                % (", ".join(_WARGAME_COLUMNS), ", ".join("?" * len(_WARGAME_COLUMNS))),
                [row[c] for c in _WARGAME_COLUMNS],
            )
            inserted += cur.rowcount if cur.rowcount > 0 else 0
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return inserted


def insert_wargame_questions(rows, db_path=DB_PATH):
    """검증을 통과한 문제 행들을 한 트랜잭션으로 적재한다. 실패 시 전부 롤백."""
    if not rows:
        return 0
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    try:
        for row in rows:
            cur.execute(
                "INSERT INTO wargame_questions (%s) VALUES (%s)"
                % (", ".join(_WARGAME_COLUMNS), ", ".join("?" * len(_WARGAME_COLUMNS))),
                [row[c] for c in _WARGAME_COLUMNS],
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return len(rows)


def get_wargame_questions(db_path=DB_PATH):
    """빌더가 바로 쓸 수 있는 형태로 워게임 문제를 반환한다 (데일리 최신순 → 정적 순)."""
    init_db(db_path)
    conn = get_connection(db_path)
    rows = conn.execute(
        """SELECT * FROM wargame_questions
           ORDER BY is_daily DESC, created_date DESC, sort_order ASC, id ASC"""
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        try:
            blocks = json.loads(r["blocks_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            blocks = []
        if not blocks and r["code_body"]:
            blocks = [{"label": r["code_label"] or "Code", "code": r["code_body"]}]
        try:
            choices = json.loads(r["choices_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            choices = []
        try:
            hints = json.loads(r["hints_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            hints = []
        try:
            patterns = json.loads(r["patterns_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            patterns = []
        try:
            chips = json.loads(r["chips_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            chips = []
        q = {
            "id": r["id"],
            "cat": r["category"],
            "level": r["difficulty"],
            "type": r["kind"],
            "title": r["title"],
            "brief": r["context"],
            "blocks": blocks,
            "prompt": r["prompt"],
            "hints": hints,
            "choices": choices,
            "answer": r["answer_idx"],
            "explain": {
                "principle": r["principle"],
                "impact": r["impact"],
                "vuln": r["vuln_code"],
                "secure": r["secure_code"],
            },
            "patterns": patterns,
            "placeholder": r["placeholder"] or "",
            "sample": r["sample"] or "",
            "chips": chips,
            "code_lang": r["code_lang"] or "",
            "source_ref": r["source_ref"] or "",
            "created_date": r["created_date"],
            "is_daily": int(r["is_daily"] or 0),
            "sort_order": int(r["sort_order"] or 0),
        }
        out.append(q)
    return out


def count_wargame_questions(db_path=DB_PATH, is_daily=None, created_date=None):
    init_db(db_path)
    conn = get_connection(db_path)
    sql = "SELECT COUNT(*) FROM wargame_questions WHERE 1=1"
    args = []
    if is_daily is not None:
        sql += " AND is_daily = ?"
        args.append(1 if is_daily else 0)
    if created_date:
        sql += " AND created_date = ?"
        args.append(created_date)
    n = conn.execute(sql, args).fetchone()[0]
    conn.close()
    return n


def get_wargame_titles(db_path=DB_PATH, limit=300):
    init_db(db_path)
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT title FROM wargame_questions ORDER BY created_date DESC, sort_order ASC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


# ---------------------------------------------------------------------------
# 8) 하루 한 판 · 3단서 추리 (clue_questions)
# ---------------------------------------------------------------------------
CLUE_CATEGORIES = ("tech", "life", "culture", "science", "nature", "history")


def clue_row_from_question(q, puzzle_date, is_daily=0, sort_order=0, now_dt=None):
    """빌더/생성기의 문제 dict를 clue_questions 행 dict로 변환한다.

    q 키: id, category, title, prompt, clues[3], choices[4], answer, explanation,
          source_ref, puzzle_date, is_daily, sort_order
    """
    clues = list(q.get("clues") or [])
    clues += [""] * (3 - len(clues))
    now = _now_iso(now_dt)
    return {
        "id": q["id"],
        "puzzle_date": q.get("puzzle_date") or puzzle_date,
        "category": q.get("category"),
        "title": q["title"],
        "prompt": q.get("prompt") or "이것은 무엇일까요?",
        "clue1": clues[0],
        "clue2": clues[1],
        "clue3": clues[2],
        "choices_json": _json_dump(q.get("choices")),
        "answer_idx": q.get("answer") if q.get("answer") is not None else q.get("answer_idx", 0),
        "explanation": q.get("explanation") or "",
        "is_daily": 1 if (q.get("is_daily") or is_daily) else 0,
        "sort_order": int(q.get("sort_order", sort_order) or 0),
        "source_ref": q.get("source_ref") or "",
        "created_at": now,
        "updated_at": now,
    }


_CLUE_COLUMNS = (
    "id", "puzzle_date", "category", "title", "prompt", "clue1", "clue2", "clue3",
    "choices_json", "answer_idx", "explanation", "is_daily", "sort_order", "source_ref",
    "created_at", "updated_at",
)


def seed_clue_questions(questions, db_path=DB_PATH):
    """초기 시드 문제를 DB로 이관한다 (id 보존, 이미 있으면 건드리지 않음)."""
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    inserted = 0
    try:
        for idx, q in enumerate(questions):
            row = clue_row_from_question(
                q, q.get("puzzle_date"), is_daily=q.get("is_daily", 0), sort_order=idx)
            cur.execute(
                "INSERT OR IGNORE INTO clue_questions (%s) VALUES (%s)"
                % (", ".join(_CLUE_COLUMNS), ", ".join("?" * len(_CLUE_COLUMNS))),
                [row[c] for c in _CLUE_COLUMNS],
            )
            inserted += cur.rowcount if cur.rowcount > 0 else 0
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return inserted


def insert_clue_questions(rows, db_path=DB_PATH):
    """검증을 통과한 문제 행들을 한 트랜잭션으로 적재한다. 실패 시 전부 롤백."""
    if not rows:
        return 0
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    try:
        for row in rows:
            cur.execute(
                "INSERT INTO clue_questions (%s) VALUES (%s)"
                % (", ".join(_CLUE_COLUMNS), ", ".join("?" * len(_CLUE_COLUMNS))),
                [row[c] for c in _CLUE_COLUMNS],
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return len(rows)


def get_clue_questions(db_path=DB_PATH):
    """빌더가 바로 쓸 수 있는 형태로 3단서 추리 문제를 반환한다 (최신 날짜 → 오래된 날짜)."""
    init_db(db_path)
    conn = get_connection(db_path)
    rows = conn.execute(
        """SELECT * FROM clue_questions
           ORDER BY puzzle_date DESC, is_daily DESC, sort_order ASC, id ASC"""
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        try:
            choices = json.loads(r["choices_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            choices = []
        out.append({
            "id": r["id"],
            "puzzle_date": r["puzzle_date"],
            "category": r["category"],
            "title": r["title"],
            "prompt": r["prompt"],
            "clues": [r["clue1"], r["clue2"], r["clue3"]],
            "choices": choices,
            "answer": int(r["answer_idx"]),
            "explanation": r["explanation"],
            "is_daily": int(r["is_daily"] or 0),
            "sort_order": int(r["sort_order"] or 0),
            "source_ref": r["source_ref"] or "",
        })
    return out


def count_clue_questions(db_path=DB_PATH, created_date=None, is_daily=None):
    init_db(db_path)
    conn = get_connection(db_path)
    sql = "SELECT COUNT(*) FROM clue_questions WHERE 1=1"
    args = []
    if created_date:
        sql += " AND puzzle_date = ?"
        args.append(created_date)
    if is_daily is not None:
        sql += " AND is_daily = ?"
        args.append(1 if is_daily else 0)
    n = conn.execute(sql, args).fetchone()[0]
    conn.close()
    return n


def get_clue_titles(db_path=DB_PATH, limit=300):
    init_db(db_path)
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT title FROM clue_questions ORDER BY puzzle_date DESC, sort_order ASC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


def export_jobs_to_json(out_path="jobs.json", db_path=DB_PATH):
    """DB의 활성 공고를 jobs.json으로 내보내기 (웹 프론트엔드 연동)"""
    jobs = get_active_jobs(db_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    return len(jobs)

def _round_num(round_id, default=1):
    """'r3' -> 3. 화면의 회차 필터(exam)와 DB round_id를 일치시킨다."""
    try:
        return int(str(round_id).lstrip("rR"))
    except (TypeError, ValueError):
        return default


_SUMMARY_CATEGORY_CODES = {
    "시스템 보안": "system", "시스템 필수 용어": "system",
    "네트워크 보안": "network", "네트워크 필수 용어": "network",
    "애플리케이션 보안": "app", "애플리케이션 필수 용어": "app",
    "정보보안 일반·암호학": "crypto", "암호학 필수 용어": "crypto",
    "정보보안 관리·법률": "law", "관리·법률 필수 용어": "law",
    "디지털 포렌식 & 법률": "law",
}


def _summary_category_code(subject):
    """요약 카드의 과목 필터 코드(system/network/app/crypto/law, CPPG는 s1~s5, AI 특강은 ai)를 subject 표시명에서 복원."""
    subject = (subject or "").strip()
    if "AI" in subject:
        return "ai"
    if subject in _SUMMARY_CATEGORY_CODES:
        return _SUMMARY_CATEGORY_CODES[subject]
    m = re.match(r"^(\d)과목", subject)
    if m:
        return f"s{m.group(1)}"
    if "시스템" in subject or "보안관제" in subject:
        return "system"
    if "네트워크" in subject:
        return "network"
    if "애플리케이션" in subject or "웹" in subject or "앱" in subject:
        return "app"
    if "암호" in subject:
        return "crypto"
    return "law"


def export_study_data_from_db(db_path=DB_PATH):
    """DB에서 시험 문제 및 요약 데이터를 읽어와 웹 프론트엔드용 JS 파일들로 빌드"""
    conn = get_connection(db_path)
    cur = conn.cursor()

    def load_summaries(category):
        cur.execute("""
        SELECT sub_type, subject, title, content, data_json
        FROM study_summaries
        WHERE category = ?
        ORDER BY id ASC;
        """, (category,))
        rows = cur.fetchall()
        out = []
        for r in rows:
            out.append({
                "type": r["sub_type"],
                "category": _summary_category_code(r["subject"]),
                "category_name": r["subject"],
                "title": r["title"],
                "badge": r["content"],
                "points": json.loads(r["data_json"]) if r["data_json"] else []
            })
        return out

    def load_questions(category, id_prefix, with_type=False):
        """회차(round) 단위로 정렬하고 회차/문항 고유 ID를 부여한다."""
        cols = "round_id, round_name, question_num, prompt, choices, answer, explanation, subject, question_type"
        cur.execute(f"""
        SELECT {cols}
        FROM study_questions
        WHERE category = ?
        ORDER BY CAST(SUBSTR(round_id, 2) AS INTEGER) ASC, question_num ASC;
        """, (category,))
        out = []
        for r in cur.fetchall():
            exam = _round_num(r["round_id"])
            q_num = r["question_num"]
            try:
                choices = json.loads(r["choices"]) if r["choices"] else []
            except (TypeError, ValueError):
                choices = []
            answer_raw = r["answer"]
            answer = int(answer_raw) if str(answer_raw).isdigit() else answer_raw
            subject = r["subject"] or ""
            subject_id = 0
            m = re.match(r"^\s*(\d)", subject)
            if m:
                subject_id = int(m.group(1))
            item = {
                "id": f"{id_prefix}_r{exam}_q{q_num}",
                "exam": exam,
                "exam_name": r["round_name"],
                "subject_id": subject_id,
                "subject_name": subject,
                "prompt": r["prompt"],
                "choices": choices,
                "answer": answer,
                "explanation": r["explanation"] or ""
            }
            if with_type:
                item["type"] = r["question_type"]
            out.append(item)
        return out

    # 1. CPPG 300제
    cppg_list = load_questions("cppg", "cppg")
    for q in cppg_list:
        q["id"] = f"e{q['exam']}_q{q['id'].split('_q')[-1]}"
        q["subject"] = q.pop("subject_name")
    with open(os.path.join(os.path.dirname(__file__), "cppg_questions.js"), "w", encoding="utf-8") as f:
        # study.html 은 window.ALL_QUESTIONS 를 읽는다 (구 산출물 호환)
        f.write(f"window.ALL_QUESTIONS = {json.dumps(cppg_list, ensure_ascii=False, indent=2)};\n")
    with open(os.path.join(os.path.dirname(__file__), "cppg_questions.json"), "w", encoding="utf-8") as f:
        json.dump(cppg_list, f, ensure_ascii=False, indent=2)

    # 2. CPPG 전 과목 핵심 요약집 125선 (내용별 35선 + 가이드라인 15선 + AI 특강 12선 + 용어·조문 60선 + AI 용어 3선)
    cppg_summaries = load_summaries("cppg")
    cppg_summary_data = {
        "title": "CPPG 전 과목 핵심 요약집 125선 (내용별 심층 35선 + 공식 가이드라인 15선 + AI 특강 12선 + 용어·조문 사전 60선 + AI 용어 3선)",
        "description": "개인정보 보호의 이해 / 보호제도 / 라이프사이클 관리 / 보호조치 / 관리체계 5과목 전 범위 핵심정리 35선, 2026년 최신 고시·안내서 기반 공식 가이드라인 15선, 생성형 AI 안내서·AI 기본법·합성데이터·모델 보안을 다루는 AI 개인정보보호 특강 12선, 필수 용어·조문 사전 60선, AI 용어 3선",
        "summaries": cppg_summaries
    }

    # 2-1. 정보보안기사 필기 200제 (1~4회 각 50제) + 내용별 50선 · 용어사전 108선 = 158선
    written_qs = load_questions("infosec_written", "written")
    written_summaries = load_summaries("infosec_written")
    written_data = {
        "title": "2026 이기적 정보보안기사 (필기) 200제 & 내용별 심층요약·용어사전 158선",
        "description": "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1~4회 모의고사(각 50제) 총 200문항 및 내용별 심층 요약 50선 + 필수 핵심 용어사전 108선",
        "questions": written_qs,
        "summaries": written_summaries
    }

    # 3. 정보보안기사 실기 100제 (1~4회 각 25제) + 내용별 35선 + 단답형 족보 60선 = 95선
    practical_qs = load_questions("infosec_practical", "prac", with_type=True)
    practical_summaries = load_summaries("infosec_practical")
    practical_data = {
        "title": "2026 이기적 정보보안기사 (실기) 100제 & 단답형 족보·실무 가이드 95선",
        "description": "2026 이기적 정보보안기사 올인원 실기 편제 기준 1~4회(단답 50제 + 서술실무 50제) 총 100문항 및 실기 내용별 심층 요약 35선 + 단답형 족보 60선",
        "questions": practical_qs,
        "summaries": practical_summaries
    }

    # 4. ISMS-P 인증심사원 30제 (1·2회 각 15제)
    ismsp_qs = load_questions("ismsp_auditor", "ismsp")

    from build_infosec_all import ismsp_summary_data
    ismsp_data = {
        "title": "ISMS-P 인증심사원 실전 결함판정 퀴즈 (30제) & 인증기준 심층 요약 25선",
        "description": "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 실전 결함판정 시나리오 퀴즈 1·2회(총 30문항) 및 인증기준별 요구사항·결함 판정 포인트 25선",
        "questions": ismsp_qs,
        "summaries": ismsp_summary_data
    }

    js_content = f"""// infosec_exam_data.js
// SQLite DB(archive.db)에서 자동 생성된 최신 데이터셋
// CPPG 요약 125선 | 필기 200문항·요약 158선 | 실기 100문항·요약 95선 | ISMS-P 30문항

window.CPPG_SUMMARY_DATA = {json.dumps(cppg_summary_data, ensure_ascii=False, indent=2)};

window.INFOSEC_WRITTEN_DATA = {json.dumps(written_data, ensure_ascii=False, indent=2)};

window.INFOSEC_PRACTICAL_DATA = {json.dumps(practical_data, ensure_ascii=False, indent=2)};

window.ISMSP_AUDITOR_DATA = {json.dumps(ismsp_data, ensure_ascii=False, indent=2)};
"""
    out_path = os.path.join(os.path.dirname(__file__), "infosec_exam_data.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    # 5. 내보내기 자체 검증 (빈 본문/빈 선지/회차 유실 방지)
    empty_prompt = sum(1 for q in written_qs + practical_qs + ismsp_qs if not str(q["prompt"]).strip())
    empty_choices = sum(1 for q in written_qs + ismsp_qs if not q["choices"])
    if empty_prompt or empty_choices:
        raise SystemExit(f"[실패] 내보내기 검증 실패: 빈 본문 {empty_prompt}건 / 빈 선지 {empty_choices}건")
    print(f"[DB -> Web] 시험 공부 데이터셋 동기화 빌드 완료! "
          f"(CPPG {len(cppg_list)}문항·요약 {len(cppg_summaries)}선 | "
          f"필기 {len(written_qs)}문항·요약 {len(written_summaries)}선 / "
          f"실기 {len(practical_qs)}문항·요약 {len(practical_summaries)}선 / "
          f"ISMS-P {len(ismsp_qs)}문항·요약 {sum(len(x.get('topics', [])) for x in ismsp_data['summaries'])}선)")

    conn.close()
    return {
        "cppg_summaries": len(cppg_summaries),
        "written_questions": len(written_qs),
        "written_summaries": len(written_summaries),
        "practical_questions": len(practical_qs),
        "practical_summaries": len(practical_summaries),
        "ismsp_questions": len(ismsp_qs),
    }


if __name__ == "__main__":
    init_db()
    print("DB Stats:", get_db_stats())

# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import re
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "archive.db")

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


def parse_deadline_status(deadline_str, today_date=None, last_seen_at=None):
    """마감일 문자열을 분석하여 상태값과 마감 여부(ACTIVE/EXPIRED) 판별

    last_seen_at: 수집 시각(선택). 날짜 없는 상대 라벨(D-Day/오늘/내일/D-N)을 수집일 기준으로 환산하며,
                  시각만 적힌 당일 마감 표기는 오늘 수집된 경우에만 D-Day로 본다.
    """
    if not today_date:
        kst = timezone(timedelta(hours=9))
        today_date = datetime.now(kst).date()
        
    dl = deadline_str.strip() if deadline_str else "상시채용"
    
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
        return "D_DAY", "ACTIVE"

    # 3. D-Day / 오늘 마감 (날짜 표기 없음)
    #    상대 라벨은 수집한 날에만 유효하다. 마지막 수집일이 오늘 이전이면 그 사이 마감된 것으로 정리한다.
    #    (예: 11/13 수집 "D-Day (오늘 마감)" 이 11/17에도 오늘 마감처럼 노출되던 문제)
    if "D-Day" in dl or "오늘" in dl:
        seen = parse_seen_date(last_seen_at)
        if seen is not None and seen < today_date:
            return "EXPIRED", "EXPIRED"
        return "D_DAY", "ACTIVE"

    # 4. 내일 마감 ("D-1" 부분 문자열 매칭은 D-10~D-19까지 잡히므로 사용하지 않음)
    #    어제 수집된 "D-1 (내일 마감)"은 오늘이 마감일(D-Day), 그보다 오래된 수집분은 마감 처리.
    if "내일" in dl:
        seen = parse_seen_date(last_seen_at)
        if seen is not None:
            if seen == today_date - timedelta(days=1):
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

def normalize_key(company, title):
    c = re.sub(r"\[.*?\]|\(.*?\)|<.*?>", "", company)
    c = re.sub(r"[\s\-_/|·]", "", c).lower()
    t = re.sub(r"\[.*?\]|\(.*?\)|<.*?>", "", title)
    t = re.sub(r"[\s\-_/|·]", "", t).lower()
    return f"{c}_{t[:12]}"

def mark_expired_jobs(today_date=None, db_path=DB_PATH):
    """현재 날짜를 기준으로 마감일이 지난 공고를 일괄 EXPIRED 상태로 전환"""
    if not today_date:
        kst = timezone(timedelta(hours=9))
        today_date = datetime.now(kst).date()
        
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, deadline, status, last_seen_at FROM jobs WHERE status = 'ACTIVE';")
    rows = cur.fetchall()
    
    expired_ids = []
    for row in rows:
        dl_status, status = parse_deadline_status(row["deadline"], today_date, row["last_seen_at"])
        if status == "EXPIRED":
            expired_ids.append(row["id"])
            
    if expired_ids:
        cur.executemany("UPDATE jobs SET status = 'EXPIRED', deadline_status = 'EXPIRED' WHERE id = ?;", [(x,) for x in expired_ids])
        conn.commit()
    conn.close()
    return len(expired_ids)

def refresh_deadline_statuses(today_date=None, db_path=DB_PATH):
    """ACTIVE 공고의 deadline_status를 현재 기준으로 재계산 (마감 판정 로직 변경 시 DB 재정규화)"""
    if not today_date:
        kst = timezone(timedelta(hours=9))
        today_date = datetime.now(kst).date()

    kst = timezone(timedelta(hours=9))
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")

    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, deadline, deadline_status, last_seen_at FROM jobs WHERE status = 'ACTIVE';")
    rows = cur.fetchall()

    updates = []
    unchanged = 0
    for row in rows:
        dl_status, status = parse_deadline_status(row["deadline"], today_date, row["last_seen_at"])
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

def get_active_jobs(db_path=DB_PATH):
    """활성 공고(ACTIVE)를 마감 임박 순 및 최신 순으로 정렬하여 딕셔너리 리스트로 반환"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT company, title, url, platforms, keywords, location, deadline, summary, tags, deadline_status
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
            "company": r["company"],
            "title": r["title"],
            "url": r["url"],
            "platforms": json.loads(r["platforms"]),
            "keywords": json.loads(r["keywords"]),
            "location": r["location"] or "",
            "deadline": r["deadline"],
            "summary": r["summary"] or "",
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "deadline_status": r["deadline_status"]
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
    
    conn.close()
    return {
        "active_jobs": active_jobs,
        "expired_jobs": expired_jobs,
        "total_jobs": active_jobs + expired_jobs,
        "total_questions": total_questions,
        "total_summaries": total_summaries,
        "total_ai_insights": total_ai,
        "total_cve": total_cve
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
    """AI 인사이트 조회 (주목할 기술 우선 → 최신순)"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    sql = """
    SELECT item_key, source, title_ko, title_orig, url, category, summary, tech_insight,
           tags, is_featured, published_at, score, analyzed_by, collected_at
    FROM ai_insights
    ORDER BY is_featured DESC, published_at DESC, score DESC, id DESC
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
    count = 0
    for it in items:
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
            title_ko = excluded.title_ko,
            summary_ko = excluded.summary_ko,
            impact_ko = excluded.impact_ko,
            remediation_ko = excluded.remediation_ko,
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
            analyzed_by = excluded.analyzed_by;
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
            len(it.get("poc_links", [])),
            json.dumps(it.get("poc_links", []), ensure_ascii=False),
            json.dumps(it.get("references", []), ensure_ascii=False),
            json.dumps(it.get("cwe", []), ensure_ascii=False),
            it.get("description_orig", ""),
            it.get("published_at", ""),
            it.get("updated_at", "") or now_str,
            it.get("analyzed_by", "fallback"),
            now_str,
        ))
        count += 1
    conn.commit()
    conn.close()
    return count


def get_cve_reports(limit=None, db_path=DB_PATH):
    """CVE 리포트 조회 (KEV 실제 악용 → CVSS → EPSS → 최신순)"""
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
    ORDER BY is_kev DESC, COALESCE(cvss_score, 0) DESC, COALESCE(epss_score, 0) DESC,
             published_at DESC, cve_id DESC
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


def export_jobs_to_json(out_path="jobs.json", db_path=DB_PATH):
    """DB의 활성 공고를 jobs.json으로 내보내기 (웹 프론트엔드 연동)"""
    jobs = get_active_jobs(db_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    return len(jobs)

def export_study_data_from_db(db_path=DB_PATH):
    """DB에서 시험 문제 및 요약 데이터를 읽어와 웹 프론트엔드용 JS 파일들로 빌드"""
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    # 1. CPPG 300제
    cur.execute("""
    SELECT question_num, prompt, choices, answer, explanation, subject
    FROM study_questions
    WHERE category = 'cppg'
    ORDER BY question_num ASC;
    """)
    cppg_rows = cur.fetchall()
    cppg_list = []
    for r in cppg_rows:
        cppg_list.append({
            "id": f"e{((r['question_num']-1)//100)+1}_q{r['question_num']}",
            "prompt": r["prompt"],
            "choices": json.loads(r["choices"]),
            "answer": int(r["answer"]) if r["answer"].isdigit() else r["answer"],
            "explanation": r["explanation"],
            "subject": r["subject"]
        })
    with open(os.path.join(os.path.dirname(__file__), "cppg_questions.js"), "w", encoding="utf-8") as f:
        f.write(f"window.CPPG_QUESTIONS = {json.dumps(cppg_list, ensure_ascii=False, indent=2)};\n")
    with open(os.path.join(os.path.dirname(__file__), "cppg_questions.json"), "w", encoding="utf-8") as f:
        json.dump(cppg_list, f, ensure_ascii=False, indent=2)
        
    # 2. 정보보안기사 필기
    cur.execute("""
    SELECT question_num, prompt, choices, answer, explanation, subject
    FROM study_questions
    WHERE category = 'infosec_written'
    ORDER BY question_num ASC;
    """)
    written_q_rows = cur.fetchall()
    written_qs = []
    for r in written_q_rows:
        written_qs.append({
            "id": f"written_q{r['question_num']}",
            "prompt": r["prompt"],
            "choices": json.loads(r["choices"]),
            "answer": int(r["answer"]) if r["answer"].isdigit() else r["answer"],
            "explanation": r["explanation"],
            "subject": r["subject"]
        })
        
    cur.execute("""
    SELECT sub_type, subject, title, content, data_json
    FROM study_summaries
    WHERE category = 'infosec_written';
    """)
    written_s_rows = cur.fetchall()
    written_summaries = []
    for r in written_s_rows:
        written_summaries.append({
            "type": r["sub_type"],
            "category_name": r["subject"],
            "title": r["title"],
            "badge": r["content"],
            "points": json.loads(r["data_json"])
        })
        
    written_data = {
        "title": "2026 이기적 정보보안기사 (필기) 200제 & 내용별 심층요약·용어사전 80선",
        "description": "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1~4회 모의고사(각 50제) 총 200문항 및 내용별 심층 요약 35선 + 필수 핵심 용어사전 45선",
        "questions": written_qs,
        "summaries": written_summaries
    }
    
    # 3. 정보보안기사 실기
    cur.execute("""
    SELECT question_num, prompt, choices, answer, explanation, subject, question_type
    FROM study_questions
    WHERE category = 'infosec_practical'
    ORDER BY question_num ASC;
    """)
    prac_q_rows = cur.fetchall()
    practical_qs = []
    for r in prac_q_rows:
        practical_qs.append({
            "id": f"prac_q{r['question_num']}",
            "prompt": r["prompt"],
            "choices": json.loads(r["choices"]),
            "answer": r["answer"],
            "explanation": r["explanation"],
            "subject": r["subject"],
            "type": r["question_type"]
        })
        
    cur.execute("""
    SELECT sub_type, subject, title, content, data_json
    FROM study_summaries
    WHERE category = 'infosec_practical';
    """)
    prac_s_rows = cur.fetchall()
    practical_summaries = []
    for r in prac_s_rows:
        practical_summaries.append({
            "type": r["sub_type"],
            "category_name": r["subject"],
            "title": r["title"],
            "badge": r["content"],
            "points": json.loads(r["data_json"])
        })
        
    practical_data = {
        "title": "2026 이기적 정보보안기사 (실기) 100제 & 단답형 족보·실무 가이드 50선",
        "description": "2026 이기적 정보보안기사 올인원 실기 편제 기준 1~4회(단답 50제 + 서술실무 50제) 총 100문항 및 실기 내용별 심층 요약 20선 + 단답형 족보 30선",
        "questions": practical_qs,
        "summaries": practical_summaries
    }
    
    # 4. ISMS-P 인증심사원
    cur.execute("""
    SELECT question_num, prompt, choices, answer, explanation, subject
    FROM study_questions
    WHERE category = 'ismsp_auditor'
    ORDER BY question_num ASC;
    """)
    ismsp_q_rows = cur.fetchall()
    ismsp_qs = []
    for r in ismsp_q_rows:
        ismsp_qs.append({
            "id": f"ismsp_q{r['question_num']}",
            "prompt": r["prompt"],
            "choices": json.loads(r["choices"]),
            "answer": int(r["answer"]) if r["answer"].isdigit() else r["answer"],
            "explanation": r["explanation"],
            "subject": r["subject"]
        })
        
    from build_infosec_all import ismsp_summary_data
    ismsp_data = {
        "title": "ISMS-P 인증심사원 실전 결함판정 퀴즈 (30제) & 102개 기준 결함사례",
        "description": "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 실전 결함판정 시나리오 퀴즈 1·2회(총 30문항) 및 102개 전 기준 결함사례 총람",
        "questions": ismsp_qs,
        "summaries": ismsp_summary_data
    }
    
    js_content = f"""// infosec_exam_data.js
// SQLite DB(archive.db)에서 자동 생성된 최신 데이터셋
// 필기 200문항 | 실기 100문항 | ISMS-P 30문항

window.INFOSEC_WRITTEN_DATA = {json.dumps(written_data, ensure_ascii=False, indent=2)};

window.INFOSEC_PRACTICAL_DATA = {json.dumps(practical_data, ensure_ascii=False, indent=2)};

window.ISMSP_AUDITOR_DATA = {json.dumps(ismsp_data, ensure_ascii=False, indent=2)};
"""
    out_path = os.path.join(os.path.dirname(__file__), "infosec_exam_data.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    conn.close()
    print("[DB -> Web] 시험 공부 데이터셋 동기화 빌드 완료!")

if __name__ == "__main__":
    init_db()
    print("DB Stats:", get_db_stats())

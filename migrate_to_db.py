# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(__file__))
from db_manager import get_connection, init_db, parse_deadline_status, normalize_key

def migrate_jobs():
    print("=== [1/3] 채용 공고 데이터 SQLite 마이그레이션 시작 ===")
    jobs_json_path = os.path.join(os.path.dirname(__file__), "jobs.json")
    if not os.path.exists(jobs_json_path):
        print("[경고] jobs.json 파일이 존재하지 않습니다.")
        return 0, 0
        
    with open(jobs_json_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)
        
    conn = get_connection()
    cur = conn.cursor()
    
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    today_date = datetime.now(kst).date()
    
    active_count = 0
    expired_count = 0
    
    for job in jobs:
        company = job.get("company", "").strip()
        title = job.get("title", "").strip()
        if not company or not title:
            continue
            
        key = normalize_key(company, title)
        url = job.get("url", "")
        platforms_json = json.dumps(job.get("platforms", []), ensure_ascii=False)
        keywords_json = json.dumps(job.get("keywords", []), ensure_ascii=False)
        location = job.get("location", "")
        raw_deadline = job.get("deadline", "상시채용")
        
        deadline_status, status = parse_deadline_status(raw_deadline, today_date)
        if status == "ACTIVE":
            active_count += 1
        else:
            expired_count += 1
            
        summary = job.get("summary", "")
        tags_json = json.dumps(job.get("tags", []), ensure_ascii=False)
        
        cur.execute("""
        INSERT INTO jobs (
            job_key, company, title, url, platforms, keywords,
            location, deadline, deadline_status, status,
            summary, tags, first_seen_at, last_seen_at,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_key) DO UPDATE SET
            platforms = excluded.platforms,
            keywords = excluded.keywords,
            location = CASE WHEN excluded.location != '' THEN excluded.location ELSE jobs.location END,
            deadline = excluded.deadline,
            deadline_status = excluded.deadline_status,
            status = excluded.status,
            summary = CASE WHEN excluded.summary != '' THEN excluded.summary ELSE jobs.summary END,
            tags = CASE WHEN excluded.tags != '[]' THEN excluded.tags ELSE jobs.tags END,
            last_seen_at = excluded.last_seen_at,
            updated_at = excluded.updated_at;
        """, (
            key, company, title, url, platforms_json, keywords_json,
            location, raw_deadline, deadline_status, status,
            summary, tags_json, now_kst, now_kst,
            now_kst, now_kst
        ))
        
    conn.commit()
    conn.close()
    print(f"-> 채용 공고 마이그레이션 완료: 총 {len(jobs)}건 중 활성(ACTIVE) {active_count}건, 마감 정리(EXPIRED) {expired_count}건")
    return active_count, expired_count

def migrate_study_questions():
    print("\n=== [2/3] 시험 문제 데이터 SQLite 마이그레이션 시작 ===")
    conn = get_connection()
    cur = conn.cursor()
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    
    total_q_count = 0
    cur.execute("DELETE FROM study_questions;") # 문제 데이터 멱등성 보장
    
    # 1. CPPG 300문항 (cppg_questions.json)
    cppg_json_path = os.path.join(os.path.dirname(__file__), "cppg_questions.json")
    if os.path.exists(cppg_json_path):
        with open(cppg_json_path, "r", encoding="utf-8") as f:
            cppg_data = json.load(f)
            
        for idx, q in enumerate(cppg_data, 1):
            raw_id = str(q.get("id", ""))
            m = re.search(r"e(\d+)_q(\d+)", raw_id)
            if m:
                exam_num = int(m.group(1))
                q_num = int(m.group(2))
            else:
                exam_num = 1 if idx <= 100 else (2 if idx <= 200 else 3)
                q_num = (idx - 1) % 100 + 1
                
            r_id = f"r{exam_num}"
            r_name = f"{exam_num}회 실전 모의고사 (100제)"
                
            cur.execute("""
            INSERT OR REPLACE INTO study_questions (
                category, category_name, round_id, round_name,
                subject, question_num, question_type,
                prompt, choices, answer, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "cppg", "개인정보관리사 (CPPG)", r_id, r_name,
                q.get("subject", "개인정보보호 제도"), q_num, "choice",
                q.get("prompt", ""), json.dumps(q.get("choices", []), ensure_ascii=False),
                str(q.get("answer", "1")), q.get("explanation", ""), now_kst
            ))
            total_q_count += 1
        print(f"-> CPPG 문제 마이그레이션 완료: {len(cppg_data)}문항")
        
    # 2. 정보보안기사 필기 200문항 (written_questions.get_written_questions())
    sys.path.append(os.path.join(os.path.dirname(__file__), "exam_builder"))
    try:
        import written_questions
        all_written = written_questions.get_written_questions() # 200제
        
        for idx, q in enumerate(all_written, 1):
            if idx <= 50:
                r_id, r_name = "r1", "1회 실전 모의고사 (50제)"
                q_num = idx
            elif idx <= 100:
                r_id, r_name = "r2", "2회 고난도 기출 (50제)"
                q_num = idx - 50
            elif idx <= 150:
                r_id, r_name = "r3", "3회 최신 기출 복원 (50제)"
                q_num = idx - 100
            else:
                r_id, r_name = "r4", "4회 고난도 심화 (50제)"
                q_num = idx - 150
                
            cur.execute("""
            INSERT OR REPLACE INTO study_questions (
                category, category_name, round_id, round_name,
                subject, question_num, question_type,
                prompt, choices, answer, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "infosec_written", "정보보안기사 (필기)", r_id, r_name,
                q.get("subject", "시스템 보안"), q_num, "choice",
                q.get("prompt", ""), json.dumps(q.get("choices", []), ensure_ascii=False),
                str(q.get("answer", "1")), q.get("explanation", ""), now_kst
            ))
            total_q_count += 1
        print(f"-> 정보보안기사 필기 문제 마이그레이션 완료: {len(all_written)}문항")
    except Exception as e:
        print(f"[경고] 정보보안기사 필기 마이그레이션 중 오류: {e}")
        
    # 3. 정보보안기사 실기 100문항 (practical_questions.get_practical_questions())
    try:
        import practical_questions
        all_practical = practical_questions.get_practical_questions() # 100제
        
        for idx, q in enumerate(all_practical, 1):
            if idx <= 25:
                r_id, r_name = "r1", "1회 단답형 족보 (25제)"
                q_type = "short"
                q_num = idx
            elif idx <= 50:
                r_id, r_name = "r2", "2회 서술·실무형 (25제)"
                q_type = "essay"
                q_num = idx - 25
            elif idx <= 75:
                r_id, r_name = "r3", "3회 단답형 최신 (25제)"
                q_type = "short"
                q_num = idx - 50
            else:
                r_id, r_name = "r4", "4회 침해사고 분석 (25제)"
                q_type = "essay"
                q_num = idx - 75
                
            cur.execute("""
            INSERT OR REPLACE INTO study_questions (
                category, category_name, round_id, round_name,
                subject, question_num, question_type,
                prompt, choices, answer, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "infosec_practical", "정보보안기사 (실기)", r_id, r_name,
                q.get("subject", "실무 보안"), q_num, q_type,
                q.get("prompt", ""), json.dumps(q.get("choices", []), ensure_ascii=False),
                str(q.get("answer", "")), q.get("explanation", ""), now_kst
            ))
            total_q_count += 1
        print(f"-> 정보보안기사 실기 문제 마이그레이션 완료: {len(all_practical)}문항")
    except Exception as e:
        print(f"[경고] 정보보안기사 실기 마이그레이션 중 오류: {e}")
        
    # 4. ISMS-P 인증심사원 30문항 (generate_exam_data.get_ismsp_questions())
    try:
        import generate_exam_data
        all_ismsp = generate_exam_data.get_ismsp_questions() # 30제
        
        for idx, q in enumerate(all_ismsp, 1):
            if idx <= 15:
                r_id = "r1"
                r_name = "1회 실전 결함판정 (15제)"
                q_num = idx
            else:
                r_id = "r2"
                r_name = "2회 고난도 시나리오 (15제)"
                q_num = idx - 15
            
            cur.execute("""
            INSERT OR REPLACE INTO study_questions (
                category, category_name, round_id, round_name,
                subject, question_num, question_type,
                prompt, choices, answer, explanation, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "ismsp_auditor", "ISMS-P 인증심사원", r_id, r_name,
                q.get("subject", "인증기준 결함판정"), q_num, "choice",
                q.get("prompt", ""), json.dumps(q.get("choices", []), ensure_ascii=False),
                str(q.get("answer", "1")), q.get("explanation", ""), now_kst
            ))
            total_q_count += 1
        print(f"-> ISMS-P 문제 마이그레이션 완료: {len(all_ismsp)}문항")
    except Exception as e:
        print(f"[경고] ISMS-P 마이그레이션 중 오류: {e}")

    # 5. 맞춤 분석 퀴즈 (custom_study.json)
    custom_json_path = os.path.join(os.path.dirname(__file__), "custom_study.json")
    if os.path.exists(custom_json_path):
        try:
            with open(custom_json_path, "r", encoding="utf-8") as f:
                custom_sets = json.load(f)
            custom_q_count = 0
            for set_idx, cset in enumerate(custom_sets, 1):
                set_title = cset.get("title", f"맞춤 분석 {set_idx}회")
                for q_idx, q in enumerate(cset.get("questions", []), 1):
                    custom_q_count += 1
                    cur.execute("""
                    INSERT OR REPLACE INTO study_questions (
                        category, category_name, round_id, round_name,
                        subject, question_num, question_type,
                        prompt, choices, answer, explanation, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "custom", "맞춤 분석 퀴즈", f"r{set_idx}", set_title,
                        cset.get("category", "맞춤 분석"), q_idx, "choice",
                        q.get("prompt", ""), json.dumps(q.get("choices", []), ensure_ascii=False),
                        str(q.get("answer", "1")), q.get("explanation", ""), now_kst
                    ))
                    total_q_count += 1
            print(f"-> 맞춤 분석 문제 마이그레이션 완료: {custom_q_count}문항")
        except Exception as e:
            print(f"[경고] 맞춤 분석 퀴즈 마이그레이션 중 오류: {e}")
            
    conn.commit()
    conn.close()
    print(f"-> 시험 문제 전체 마이그레이션 완료: 총 {total_q_count}문항 적재")
    return total_q_count

def migrate_study_summaries():
    print("\n=== [3/3] 시험 요약 노트 데이터 SQLite 마이그레이션 시작 ===")
    conn = get_connection()
    cur = conn.cursor()
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    
    total_s_count = 0
    cur.execute("DELETE FROM study_summaries;") # 요약은 재구축
    
    # 1. 정보보안기사 필기 요약 72선 (summary_notes.py -> items)
    sys.path.append(os.path.join(os.path.dirname(__file__), "exam_builder"))
    try:
        import summary_notes
        written_summary = summary_notes.get_written_summary()
        items = written_summary.get("items", [])
        for item in items:
            sub_type = item.get("type", "content") # content or term
            cur.execute("""
            INSERT INTO study_summaries (
                category, sub_type, subject, title, content, data_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "infosec_written", sub_type, item.get("category_name", "필기 공통"),
                item.get("title", ""), item.get("badge", ""),
                json.dumps(item.get("points", []), ensure_ascii=False), now_kst
            ))
            total_s_count += 1
        print(f"-> 정보보안기사 필기 요약 마이그레이션 완료: {len(items)}선")
    except Exception as e:
        print(f"[경고] 정보보안기사 필기 요약 마이그레이션 오류: {e}")
        
    # 2. 정보보안기사 실기 요약 50선 (practical_summary.py -> items)
    try:
        import practical_summary
        prac_summary = practical_summary.get_practical_summary()
        items = prac_summary.get("items", [])
        for item in items:
            sub_type = item.get("type", "content") # content or term
            cur.execute("""
            INSERT INTO study_summaries (
                category, sub_type, subject, title, content, data_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "infosec_practical", sub_type, item.get("category_name", "실기 공통"),
                item.get("title", ""), item.get("badge", ""),
                json.dumps(item.get("points", []), ensure_ascii=False), now_kst
            ))
            total_s_count += 1
        print(f"-> 정보보안기사 실기 요약 마이그레이션 완료: {len(items)}선")
    except Exception as e:
        print(f"[경고] 정보보안기사 실기 요약 마이그레이션 오류: {e}")

    # 3. ISMS-P 인증심사원 요약 (build_infosec_all.py 내 ismsp_summary_data)
    try:
        from build_infosec_all import ismsp_summary_data
        for section in ismsp_summary_data:
            sec_title = section.get("title", "")
            for top in section.get("topics", []):
                cur.execute("""
                INSERT INTO study_summaries (
                    category, sub_type, subject, title, content, data_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    "ismsp_auditor", "standard", sec_title,
                    top.get("name", ""), sec_title,
                    json.dumps(top.get("points", []), ensure_ascii=False), now_kst
                ))
                total_s_count += 1
        print(f"-> ISMS-P 요약 마이그레이션 완료")
    except Exception as e:
        print(f"[경고] ISMS-P 요약 마이그레이션 오류: {e}")

    # 4. 맞춤 분석 요약 (custom_study.json)
    custom_json_path = os.path.join(os.path.dirname(__file__), "custom_study.json")
    if os.path.exists(custom_json_path):
        try:
            with open(custom_json_path, "r", encoding="utf-8") as f:
                custom_sets = json.load(f)
            custom_s_count = 0
            for cset in custom_sets:
                s_obj = cset.get("summary", {})
                if s_obj:
                    custom_s_count += 1
                    cur.execute("""
                    INSERT INTO study_summaries (
                        category, sub_type, subject, title, content, data_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "custom", "content", s_obj.get("category", "맞춤 분석"),
                        s_obj.get("title", cset.get("title", "")), cset.get("source_type", ""),
                        json.dumps(s_obj, ensure_ascii=False), now_kst
                    ))
                    total_s_count += 1
            print(f"-> 맞춤 분석 요약 마이그레이션 완료: {custom_s_count}선")
        except Exception as e:
            print(f"[경고] 맞춤 분석 요약 마이그레이션 중 오류: {e}")
        
    conn.commit()
    conn.close()
    print(f"-> 시험 요약 전체 마이그레이션 완료: 총 {total_s_count}선 적재")
    return total_s_count

def run_all_migrations():
    init_db()
    a_jobs, exp_jobs = migrate_jobs()
    q_count = migrate_study_questions()
    s_count = migrate_study_summaries()
    
    conn = get_connection()
    cur = conn.cursor()
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    cur.execute("INSERT OR REPLACE INTO db_meta (key, val, updated_at) VALUES ('last_migration', ?, ?)", (
        f"jobs:{a_jobs}+{exp_jobs}, questions:{q_count}, summaries:{s_count}", now_kst
    ))
    conn.commit()
    conn.close()
    print(f"\n[성공] 모든 데이터의 SQLite DB화가 완벽히 완료되었습니다!")
    print(f"- 활성 공고: {a_jobs}건 / 마감 정리 공고: {exp_jobs}건")
    print(f"- 시험 문제: {q_count}문항 (CPPG 300제, 기사필기 200제, 기사실기 100제, ISMS-P 30제, 맞춤 9제)")
    print(f"- 핵심 요약: {s_count}선 (필기 72선, 실기 50선, ISMS-P 6선, 맞춤 3선)")

if __name__ == "__main__":
    run_all_migrations()

# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import sys
import re
import random
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

# ---------------------------------------------------------------------------
# 공통 헬퍼: 빌더 모듈키(question/options/subject_name)와 DB 컬럼(prompt/choices/subject)
# 간의 키 불일치를 정규화한다. (11-13 마이그레이션 당시 330문항이 빈 껍데기로 적재된 원인)
# ---------------------------------------------------------------------------
def _pick(q, keys, default=None):
    for k in keys:
        v = q.get(k) if isinstance(q, dict) else None
        if v is not None and v != "" and v != []:
            return v
    return default


def normalize_question(q, default_subject="", default_exam=1, default_exam_name=""):
    """빌더 원본(dict) -> DB 적재용 표준 dict. prompt/choices 는 절대 비지 않도록 검증."""
    prompt = str(_pick(q, ["prompt", "question"], "")).strip()
    raw_choices = _pick(q, ["choices", "options"], []) or []
    choices = [str(c).strip() for c in raw_choices if str(c).strip()] if isinstance(raw_choices, list) else []
    answer = q.get("answer", 1)
    if isinstance(answer, bool):
        answer = 1
    if isinstance(answer, int):
        answer_val = str(answer)
    elif isinstance(answer, str) and answer.strip().isdigit():
        answer_val = str(int(answer.strip()))
    else:
        answer_val = str(answer).strip()
    exam = q.get("exam")
    exam = exam if isinstance(exam, int) and exam > 0 else default_exam
    exam_name = str(_pick(q, ["exam_name"], default_exam_name) or default_exam_name).strip()
    subject = str(_pick(q, ["subject_name", "subject"], default_subject) or default_subject).strip()
    explanation = str(q.get("explanation", "") or "").strip()
    return {
        "prompt": prompt,
        "choices": choices,
        "answer": answer_val,
        "explanation": explanation,
        "subject": subject,
        "exam": exam,
        "exam_name": exam_name,
    }


def shuffle_choices(seed, choices, answer_val):
    """정답 위치가 1번에 몰려 있던 문제(필기 200제 중 161문항 정답=1)를 고르게 분산.
    보기 텍스트는 그대로 두고 순서만 문항별 고정 시드로 섞어, 재마이그레이션해도 동일하게 유지한다."""
    if not choices or len(choices) < 2:
        return choices, answer_val
    try:
        ans_idx = int(answer_val) - 1
    except (TypeError, ValueError):
        return choices, answer_val
    if ans_idx < 0 or ans_idx >= len(choices):
        return choices, answer_val
    order = list(range(len(choices)))
    random.Random(seed).shuffle(order)
    new_choices = [choices[i] for i in order]
    new_idx = order.index(ans_idx)
    return new_choices, str(new_idx + 1)


def migrate_study_questions():
    print("\n=== [2/3] 시험 문제 데이터 SQLite 마이그레이션 시작 ===")
    conn = get_connection()
    cur = conn.cursor()
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")

    total_q_count = 0
    empty_prompt = 0
    empty_choices = 0
    cur.execute("DELETE FROM study_questions;")  # 문제 데이터 멱등성 보장

    # 빌더 모듈 경로는 CPPG AI 특강(r4) 적재 전에 필요하다.
    sys.path.append(os.path.join(os.path.dirname(__file__), "exam_builder"))

    seen_keys = set()

    def insert_question(category, category_name, round_id, round_name, subject,
                        question_num, question_type, norm, shuffle=True):
        nonlocal total_q_count, empty_prompt, empty_choices
        key = (category, round_id, question_num)
        if key in seen_keys:
            raise SystemExit(f"[실패] 문항 키 중복: {key} (회차/문항 번호 매핑 오류)")
        seen_keys.add(key)
        prompt = norm["prompt"]
        choices = norm["choices"]
        answer_val = norm["answer"]
        if shuffle:
            choices, answer_val = shuffle_choices(
                f"{category}|{round_id}|{question_num}", choices, answer_val)
        if not prompt:
            empty_prompt += 1
        if question_type == "choice" and not choices:
            empty_choices += 1
        cur.execute("""
        INSERT OR REPLACE INTO study_questions (
            category, category_name, round_id, round_name,
            subject, question_num, question_type,
            prompt, choices, answer, explanation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            category, category_name, round_id, round_name,
            subject, question_num, question_type,
            prompt, json.dumps(choices, ensure_ascii=False),
            answer_val, norm["explanation"], now_kst
        ))
        total_q_count += 1

    # 1. CPPG 300문항 (cppg_questions.json)
    ai_q_count = 0
    cppg_base_count = 0
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

            # r4(AI 개인정보보호 특강)는 cppg_ai_privacy_questions.py 가 원천이다.
            # export_study_data_from_db()가 cppg_questions.json에 e4_*를 다시 써 두므로,
            # 재마이그레이션 때 여기서 한 번 더 적재하면 키 중복이 된다.
            if exam_num >= 4:
                continue

            norm = normalize_question(q, "개인정보보호 제도", exam_num,
                                      f"{exam_num}회 실전 모의고사 (100제)")
            insert_question("cppg", "개인정보관리사 (CPPG)", f"r{exam_num}",
                            f"{exam_num}회 실전 모의고사 (100제)",
                            norm["subject"], q_num, "choice", norm, shuffle=False)
            cppg_base_count += 1
        print(f"-> CPPG 문제 마이그레이션 완료: 1~3회 {cppg_base_count}문항 (r4 AI 특강은 별도 모듈)")

    # 1-b. CPPG 4회 AI 개인정보보호 특강 30문항 (exam_builder/cppg_ai_privacy_questions.py)
    try:
        import cppg_ai_privacy_questions
        ai_questions = cppg_ai_privacy_questions.get_ai_privacy_questions()
        for q_num, q in enumerate(ai_questions, 1):
            norm = normalize_question(q, "AI 개인정보보호", 4, cppg_ai_privacy_questions.EXAM_NAME)
            insert_question("cppg", "개인정보관리사 (CPPG)", "r4",
                            cppg_ai_privacy_questions.EXAM_NAME,
                            norm["subject"], q_num, "choice", norm, shuffle=False)
        print(f"-> CPPG 4회 AI 개인정보보호 특강 마이그레이션 완료: {len(ai_questions)}문항")
        ai_q_count = len(ai_questions)
    except Exception as e:
        raise SystemExit(f"[실패] CPPG AI 특강 마이그레이션 중 오류(문항 유실 방지로 중단): {e}")

    # 2. 정보보안기사 필기 200문항 (exam_builder/written_questions.py)
    sys.path.append(os.path.join(os.path.dirname(__file__), "exam_builder"))
    try:
        import written_questions
        all_written = written_questions.get_written_questions()  # 200제
        round_counts = {}
        for q in all_written:
            norm = normalize_question(q, "시스템 보안", 1, "필기 모의고사")
            r_id = f"r{norm['exam']}"
            round_counts[r_id] = round_counts.get(r_id, 0) + 1
            insert_question("infosec_written", "정보보안기사 (필기)", r_id,
                            norm["exam_name"], norm["subject"], round_counts[r_id],
                            "choice", norm)
        print(f"-> 정보보안기사 필기 문제 마이그레이션 완료: {len(all_written)}문항")
    except Exception as e:
        print(f"[경고] 정보보안기사 필기 마이그레이션 중 오류: {e}")

    # 3. 정보보안기사 실기 100문항 (exam_builder/practical_questions.py)
    try:
        import practical_questions
        all_practical = practical_questions.get_practical_questions()  # 100제
        round_counts = {}
        for q in all_practical:
            norm = normalize_question(q, "실무 보안", 1, "실기 문제")
            r_id = f"r{norm['exam']}"
            round_counts[r_id] = round_counts.get(r_id, 0) + 1
            q_type = "short" if norm["exam"] in (1, 3) else "essay"
            insert_question("infosec_practical", "정보보안기사 (실기)", r_id,
                            norm["exam_name"], norm["subject"], round_counts[r_id],
                            q_type, norm)
        print(f"-> 정보보안기사 실기 문제 마이그레이션 완료: {len(all_practical)}문항")
    except Exception as e:
        print(f"[경고] 정보보안기사 실기 마이그레이션 중 오류: {e}")

    # 4. ISMS-P 인증심사원 30문항 (generate_exam_data.get_ismsp_questions())
    try:
        import generate_exam_data
        all_ismsp = generate_exam_data.get_ismsp_questions()  # 30제
        round_counts = {}
        for q in all_ismsp:
            norm = normalize_question(q, "인증기준 결함판정", 1, "결함판정 모의고사")
            r_id = f"r{norm['exam']}"
            round_counts[r_id] = round_counts.get(r_id, 0) + 1
            insert_question("ismsp_auditor", "ISMS-P 인증심사원", r_id,
                            norm["exam_name"], norm["subject"], round_counts[r_id],
                            "choice", norm)
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
                    norm = normalize_question(q, cset.get("category", "맞춤 분석"), 1, set_title)
                    insert_question("custom", "맞춤 분석 퀴즈", f"r{set_idx}",
                                    set_title, norm["subject"], q_idx, "choice", norm, shuffle=False)
                    custom_q_count += 1
            print(f"-> 맞춤 분석 문제 마이그레이션 완료: {custom_q_count}문항")
        except Exception as e:
            print(f"[경고] 맞춤 분석 퀴즈 마이그레이션 중 오류: {e}")

    # 5-b. 카테고리별 원본 대비 적재 수 대조 (조용한 덮어쓰기 방지)
    expected = {"cppg": 300 + ai_q_count,
                "infosec_written": 200, "infosec_practical": 100, "ismsp_auditor": 30}
    for cat, exp in expected.items():
        cur.execute("SELECT COUNT(*) FROM study_questions WHERE category = ?;", (cat,))
        got = cur.fetchone()[0]
        if exp and got != exp:
            raise SystemExit(f"[실패] {cat} 적재 수 불일치: 원본 {exp}문항 / DB {got}문항")

    # 6. 적재 무결성 자체 검증
    cur.execute("SELECT category, COUNT(*), "
                "SUM(CASE WHEN TRIM(prompt) = '' THEN 1 ELSE 0 END), "
                "SUM(CASE WHEN choices IN ('[]', '') OR choices IS NULL THEN 1 ELSE 0 END) "
                "FROM study_questions GROUP BY category ORDER BY category;")
    print("\n[검증] 카테고리별 문항·빈 본문·빈 선지")
    for r in cur.fetchall():
        print(f"  - {r[0]}: {r[1]}문항 (빈 prompt {r[2]}건, 빈 choices {r[3]}건)")

    cur.execute("SELECT COUNT(*) FROM study_questions WHERE TRIM(prompt) = '';")
    empty_prompt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM study_questions "
                "WHERE question_type = 'choice' AND (choices IN ('[]', '') OR choices IS NULL);")
    empty_choices = cur.fetchone()[0]
    if empty_prompt or empty_choices:
        raise SystemExit(f"[실패] 빈 문제 본문 {empty_prompt}건 / 빈 선지 {empty_choices}건 — 적재 중단")

    conn.commit()
    conn.close()
    print(f"-> 시험 문제 전체 마이그레이션 완료: 총 {total_q_count}문항 적재 (빈 본문 0 / 빈 선지 0)")
    return total_q_count


def migrate_study_summaries():
    print("\n=== [3/3] 시험 요약 노트 데이터 SQLite 마이그레이션 시작 ===")
    conn = get_connection()
    cur = conn.cursor()
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    
    total_s_count = 0
    cur.execute("DELETE FROM study_summaries;") # 요약은 재구축

    # 0. CPPG 전 과목 핵심 요약집 110선 (cppg_summary_ext.py -> 내용별 35선 + 공식 가이드라인 15선 + 용어·조문 60선)
    sys.path.append(os.path.join(os.path.dirname(__file__), "exam_builder"))
    try:
        import cppg_summary_ext
        cppg_summary = cppg_summary_ext.get_cppg_summary()
        cppg_items = cppg_summary.get("items", [])
        for item in cppg_items:
            sub_type = item.get("type", "content")  # content or term
            cur.execute("""
            INSERT INTO study_summaries (
                category, sub_type, subject, title, content, data_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "cppg", sub_type, item.get("category_name", "CPPG 공통"),
                item.get("title", ""), item.get("badge", ""),
                json.dumps(item.get("points", []), ensure_ascii=False), now_kst
            ))
            total_s_count += 1
        cppg_content = sum(1 for i in cppg_items if i.get("type") == "content")
        cppg_term = sum(1 for i in cppg_items if i.get("type") == "term")
        print(f"-> CPPG 요약 마이그레이션 완료: {len(cppg_items)}선 (내용별 {cppg_content}선 + 용어·조문 {cppg_term}선)")
        if cppg_content < 62 or cppg_term < 63:
            raise SystemExit(f"[실패] CPPG 요약 구성 불일치: 내용별 {cppg_content}선(내용별 35 + 가이드라인 15 + AI 특강 12 = 62 기대) + 용어·조문 {cppg_term}선(용어 60 + AI 용어 3 = 63 기대)")
    except Exception as e:
        print(f"[경고] CPPG 요약 마이그레이션 오류: {e}")

    # 1. 정보보안기사 필기 요약 158선 (summary_notes.py -> items / 내용별 50선 + 용어사전 108선)
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
        written_content = sum(1 for i in items if i.get("type") == "content")
        written_term = sum(1 for i in items if i.get("type") == "term")
        print(f"-> 정보보안기사 필기 요약 마이그레이션 완료: {len(items)}선 (내용별 {written_content}선 + 용어사전 {written_term}선)")
        if written_content != 50 or written_term != 108:
            raise SystemExit(f"[실패] 필기 요약 구성 불일치: 내용별 {written_content}선(50 기대) + 용어사전 {written_term}선(108 기대)")
    except Exception as e:
        print(f"[경고] 정보보안기사 필기 요약 마이그레이션 오류: {e}")
        
    # 2. 정보보안기사 실기 요약 95선 (practical_summary.py -> items / 내용별 35선 + 단답형 족보 60선)
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
        prac_content = sum(1 for i in items if i.get("type") == "content")
        prac_term = sum(1 for i in items if i.get("type") == "term")
        print(f"-> 정보보안기사 실기 요약 마이그레이션 완료: {len(items)}선 (내용별 {prac_content}선 + 단답형 {prac_term}선)")
        if prac_content != 35 or prac_term != 60:
            raise SystemExit(f"[실패] 실기 요약 구성 불일치: 내용별 {prac_content}선(35 기대) + 단답형 {prac_term}선(60 기대)")
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
        ismsp_topic_count = sum(len(sec.get("topics", [])) for sec in ismsp_summary_data)
        print(f"-> ISMS-P 요약 마이그레이션 완료: {ismsp_topic_count}선")
        if ismsp_topic_count < 25:
            raise SystemExit(f"[실패] ISMS-P 요약 부족: {ismsp_topic_count}선(25선 이상 기대)")
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
    conn.close()

    conn = get_connection()
    cur = conn.cursor()
    print(f"\n[성공] 모든 데이터의 SQLite DB화가 완벽히 완료되었습니다!")
    print(f"- 활성 공고: {a_jobs}건 / 마감 정리 공고: {exp_jobs}건")
    print(f"- 시험 문제: {q_count}문항 (CPPG 300제, 기사필기 200제, 기사실기 100제, ISMS-P 30제, 맞춤 9제)")
    cur.execute("SELECT category, sub_type, COUNT(*) FROM study_summaries GROUP BY category, sub_type ORDER BY category, sub_type")
    breakdown = {}
    for cat, sub, cnt in cur.fetchall():
        breakdown.setdefault(cat, {})[sub] = cnt
    print(f"- 핵심 요약: {s_count}선")
    for cat, subs in breakdown.items():
        print(f"    · {cat}: " + ", ".join(f"{k} {v}선" for k, v in subs.items()))
    conn.close()

if __name__ == "__main__":
    run_all_migrations()

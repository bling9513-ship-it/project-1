# -*- coding: utf-8 -*-
"""
SQLite DB(archive.db)를 Single Source of Truth로 하여
채용 공고 대시보드(index.html, jobs.json) 및 시험 공부 허브(study.html, infosec_exam_data.js)를
일괄 생성하고 동기화하는 마스터 빌드 스크립트.
"""
import os
import sys
import json
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(__file__))
from db_manager import get_connection, init_db, mark_expired_jobs, refresh_deadline_statuses, get_active_jobs, get_db_stats, export_study_data_from_db
from crawler import generate_html, generate_readme

def build_all():
    print("=== [Infosec Archive] SQLite DB 기반 전체 산출물 빌드 시작 ===")
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    today_date = datetime.now(kst).date()
    
    init_db()
    
    # 1. 마감일 지난 공고 정리 (EXPIRED 전환)
    expired_count = mark_expired_jobs(today_date)
    stats = get_db_stats()
    print(f"-> 마감 공고 정리 완료: 오늘 기준 {expired_count}건 추가 정리 (누적 마감 보관: {stats['expired_jobs']}건)")

    # 1-b. 활성 공고 deadline_status 재정규화 (D-10~D-19 부분 문자열 매칭 오분류 교정)
    refreshed, unchanged = refresh_deadline_statuses(today_date)
    print(f"-> 마감 상태 재계산: {refreshed}건 갱신, {unchanged}건 유지")
    
    # 2. 활성 공고 조회 및 jobs.json 생성
    active_jobs = get_active_jobs()
    jobs_json_path = os.path.join(os.path.dirname(__file__), "jobs.json")
    with open(jobs_json_path, "w", encoding="utf-8") as f:
        json.dump(active_jobs, f, ensure_ascii=False, indent=2)
    print(f"-> 'jobs.json' 저장 완료 (활성 공고 {len(active_jobs)}건)")
    
    # 3. index.html 생성
    index_html_path = os.path.join(os.path.dirname(__file__), "index.html")
    html_data = generate_html(active_jobs, now_kst)
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html_data)
    print("-> 'index.html' 생성 완료")
    
    # 4. README.md 생성
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    readme_data = generate_readme(active_jobs, now_kst)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_data)
    print("-> 'README.md' 생성 완료")
    
    # 5. 시험 공부 DB 데이터셋 내보내기 (infosec_exam_data.js, cppg_questions.js)
    export_study_data_from_db()
    
    # 6. study.html 재생성
    import subprocess
    subprocess.run(["python3", "build_study_html.py"], cwd=os.path.dirname(__file__), check=True)
    
    print(f"\n[빌드 완결] SQLite DB 기반 전체 동기화 성공!")
    print(f"📊 최종 상태:")
    print(f"  - 활성 보안 공고: {stats['active_jobs']}건 (마감 보관 {stats['expired_jobs']}건)")
    print(f"  - 시험 문제 총합: {stats['total_questions']}문항")
    print(f"  - 핵심 요약 총합: {stats['total_summaries']}선")

if __name__ == "__main__":
    build_all()

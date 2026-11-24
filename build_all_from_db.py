# -*- coding: utf-8 -*-
"""
SQLite DB(archive.db)를 Single Source of Truth로 하여
채용 공고 대시보드(index.html, jobs.json), 시험 공부 허브(study.html, infosec_exam_data.js),
AI 기술·트렌드 브리핑(ai.html, ai_data.json), CVE 취약점 리포트(cve.html, cve_data.json),
옷차림 가이드(outfit.html), 출퇴근길 보안 워게임(wargame.html), 보안 실무 유틸·치트시트(tools.html),
피싱·스미싱 판별 레이더(radar.html), 오늘 뭐 먹지·날씨 맞춤 추천(pick.html),
하루 한 판 · 3단서 추리(clue.html), 퇴근길 미션(mission.html), 차트 추리실(chart.html),
퇴근 전 60초 관제실(ops.html), 막차 자리 배치(seat.html), 한 번 더 싣기(load.html),
실시간 Canvas 아케이드(arcade.html), 한글 한 칸 변신(hangul.html), 오늘의 카드(cards.html), 세탁 라벨 읽기(wash.html),
재질 표시·분리배출(recycle.html), 식품 라벨·영양성분표 읽기(food.html), 장보기 타이밍(grocery.html),
실시간 월급·퇴근 미터(paymeter.html), 오늘의 지하철역 맞히기(subway.html), 오늘의 장바구니 리그(basket.html)을
일괄 생성하고 동기화하는 마스터 빌드 스크립트.

※ AI 자료 수집·분석은 ai_news_crawler.py 가, CVE 수집·분석은 cve_crawler.py 가 담당한다(별도 실행).
   이 스크립트는 DB에 적재된 ai_insights / cve_reports 를 각 HTML로 빌드하는 역할만 한다.
"""
import os
import sys
import json
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(__file__))
from db_manager import get_connection, init_db, mark_expired_jobs, refresh_deadline_statuses, get_active_jobs, get_db_stats, export_study_data_from_db, expire_platform_conflict_duplicates, deduplicate_active_jobs, migrate_job_keys
from crawler import generate_html, generate_readme

def build_all():
    print("=== [Infosec Archive] SQLite DB 기반 전체 산출물 빌드 시작 ===")
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    today_date = datetime.now(kst).date()
    
    init_db()
    # 0. 예전 '회사명_제목12자' 키 → 플랫폼 공고 ID 기반 키로 정리 (관심 목록 식별자)
    migrated_keys = migrate_job_keys()
    if migrated_keys:
        print(f"-> 공고 키 마이그레이션: {migrated_keys}건을 플랫폼 ID 기반 키로 전환")
    
    # 1. 마감일 지난 공고 정리 (EXPIRED 전환)
    expired_count = mark_expired_jobs(today_date)
    # 1-a. 플랫폼별 마감 표기 불일치 복제 행 정리 (예: 14시마감 ↔ D-Day 오늘 마감)
    conflict_count = expire_platform_conflict_duplicates(today_date)
    # 1-a-2. 같은 공고 중복 행 병합 — 회사 표기 차이((주)·㈜·괄호 별칭)·제목 앞머리 태그·플랫폼 재등록
    dedup = deduplicate_active_jobs(today_date=today_date)
    if dedup["merged"]:
        print(f"-> 같은 공고 중복 병합: {dedup['merged']}건을 {dedup['groups']}개 대표 공고로 정리")
    stats = get_db_stats()
    print(f"-> 마감 공고 정리 완료: 오늘 기준 {expired_count}건 추가 정리, 플랫폼 표기 불일치 복제 {conflict_count}건 정리 (누적 마감 보관: {stats['expired_jobs']}건)")

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

    # 7. ai.html 재생성 (archive.db 의 ai_insights 테이블 기반)
    from build_ai_html import build as build_ai
    ai_total = build_ai()

    # 8. cve.html 재생성 (archive.db 의 cve_reports 테이블 기반)
    from build_cve_html import build as build_cve
    cve_total = build_cve()

    # 9. outfit.html 재생성 (서울 날씨 기본값 + 기온 구간별 옷차림 가이드)
    from build_outfit_html import build as build_outfit
    outfit_total = build_outfit()

    # 10. wargame.html 재생성 (출퇴근길 보안 워게임: 정적 카드 + 브라우저 채점·기록)
    from build_wargame_html import build as build_wargame
    wargame_total = build_wargame()

    # 11. tools.html 재생성 (보안 실무 유틸 5종 + 명령어 치트시트 · 100% 브라우저 로컬 처리)
    from build_tools_html import build as build_tools
    tool_total, cmd_total = build_tools()

    # 12. radar.html 재생성 (피싱·스미싱 판별 퀴즈 + 의심 신호 검사기 + 트렌드·긴급 대응)
    from build_radar_html import build as build_radar
    radar_total = build_radar()

    # 13. pick.html 재생성 (서울 날씨 연동 메뉴 룰렛 + 주말·퇴근 후 나들이 코스)
    from build_pick_html import build as build_pick
    pick_total = build_pick()

    # 14. clue.html 재생성 (하루 한 판 · 3단서 추리: 오늘의 문제 + 지난 문제 아카이브)
    from build_clue_html import build as build_clue
    clue_total = build_clue()

    # 15. mission.html 재생성 (퇴근길 미션: 오늘의 지도 + 연습 스테이지 · BFS 검증)
    from build_mission_html import build as build_mission
    daily_total, practice_total = build_mission()

    # 16. chart.html 재생성 (차트 추리실: 과거 시세 블라인드 차트 + 단서 3단계 + 정답 공개)
    from build_chart_html import build as build_chart
    chart_total = build_chart()

    # 17. today.html 재생성 (얇은 데일리 허브: 오늘 마감 · KEV · 복습 큐 · AI 브리핑 · 날씨 · 게임)
    from build_today_html import build as build_today
    today_total = build_today()

    # 18. ops.html 재생성 (퇴근 전 60초 관제실: 60초 실전 + 연습 모드 · KST 날짜 시드 일일 경보 6건)
    from build_ops_html import build as build_ops
    ops_total = build_ops()

    # 19. seat.html 재생성 (막차 자리 배치: 4×4 좌석 퍼즐 · KST 날짜 시드 일일 + 연습 12판 · 해답 검증)
    from build_seat_html import build as build_seat
    seat_total = build_seat()

    # 20. load.html 재생성 (한 번 더 싣기: 손수레 100kg·균형 28kg 푸시 유어 럭 · KST 날짜 시드 일일 14일치 + 연습 9판)
    from build_load_html import build as build_load
    load_total = build_load()

    # 21. arcade.html 재생성 (실시간 Canvas 벽돌깨기·지렁이 · 티어 · 이 기기/기준 라이벌 랭킹)
    from build_arcade_html import build as build_arcade
    arcade_total = build_arcade()

    # 22. hangul.html 재생성 (한글 한 칸 변신: 단어 사다리 퍼즐 · 일일 14판 + 연습 12판 · par BFS 검증)
    from build_hangul_html import build as build_hangul
    hangul_total = build_hangul()

    # 23. cards.html 재생성 (오늘의 카드: 컨디션 키워드 · 1분 디지털 생활 · KST 날짜 테마 순환)
    from build_cards_html import build as build_cards
    cards_total = build_cards()

    # 24. wash.html 재생성 (세탁 라벨 읽기: KS K 0021 취급표시기호 도감 + 라벨 읽기 퀴즈 6벌)
    from build_wash_html import build as build_wash
    wash_total = build_wash()

    # 25. recycle.html 재생성 (재질 표시·분리배출 도식: 마크 9종 + 품목 7종 퀴즈)
    from build_recycle_html import build as build_recycle
    recycle_total = build_recycle()

    # 26. food.html 재생성 (식품 라벨·영양성분표 도식: 영양정보 9항목 + 표시사항 + 라벨 퀴즈 7문항)
    from build_food_html import build as build_food
    food_total = build_food()

    # 27. grocery.html 재생성 (장보기 타이밍: KAMIS 소매가격 8품목 · 4주 중앙값 대비 등락)
    from build_grocery_html import build as build_grocery
    grocery_total = build_grocery()

    # 28. paymeter.html 재생성 (실시간 월급·퇴근 미터: 급여·출퇴근 설정 → 오늘 번 돈 · 영수증 · 카드)
    from build_paymeter_html import build as build_paymeter
    paymeter_total = build_paymeter()

    # 29. subway.html 재생성 (오늘의 지하철역: 서울 25개 구 역 306곳 · KST 날짜 시드 데일리 + 연습)
    from build_subway_html import build as build_subway
    subway_total = build_subway()

    # 30. basket.html 재생성 (오늘의 장바구니 리그: KAMIS 8품목 · 날짜 시드 미션 · S/A/B/C 등급)
    from build_basket_html import build as build_basket
    basket_total = build_basket()

    print(f"\n[빌드 완결] SQLite DB 기반 전체 동기화 성공!")
    print(f"📊 최종 상태:")
    print(f"  - 활성 보안 공고: {stats['active_jobs']}건 (마감 보관 {stats['expired_jobs']}건)")
    print(f"  - 시험 문제 총합: {stats['total_questions']}문항")
    print(f"  - 핵심 요약 총합: {stats['total_summaries']}선")
    print(f"  - AI 기술·트렌드 인사이트: {ai_total}건")
    print(f"  - CVE 취약점 리포트: {cve_total}건")
    print(f"  - 옷차림 코디: {outfit_total}개 (기온 구간 8단계)")
    print(f"  - 보안 워게임 문제: {wargame_total}개 (카테고리 4종)")
    print(f"  - 보안 실무 유틸: {tool_total}종 · 치트시트 명령어 {cmd_total}개")
    print(f"  - 피싱·스미싱 판별: {radar_total}문항 (정상 안내 4문항 · 트렌드 6종 · 긴급 대응 5단계)")
    print(f"  - 오늘 뭐 먹지: 메뉴 {pick_total}종 · 나들이 코스 16곳 (날씨 모드 3종 + 자동)")
    print(f"  - 하루 한 판 3단서 추리: 문제 {clue_total}개 (단서 3단계 · 4지선다 · 분야 6종)")
    print(f"  - 퇴근길 미션: 오늘의 지도 {daily_total}개 풀 · 연습 {practice_total}개 (최단 경로 BFS 검증)")
    print(f"  - 차트 추리실: 과거 차트 {chart_total}개 (단서 3단계 · 4지선다 · 18페이지 내비게이션)")
    print(f"  - 퇴근 전 60초 관제실: 경보 {ops_total}건 풀 · 오늘 6건 (실전 60초 + 연습 · 18페이지)")
    print(f"  - 막차 자리 배치: 일일 {seat_total['daily']}판 · 연습 {seat_total['practice']}판 (오늘 {seat_total['today']} · 기준 이동 수 검증)")
    print(f"  - 한 번 더 싣기: 일일 {load_total['daily']}일치 · 연습 {load_total['practice']}판 (오늘 {load_total['today']} · 목표 {load_total['goal']}점 · 최적 {load_total['optimal']}점)")
    print(f"  - 아케이드: 점수판 {arcade_total['boards']}개(게임×난이도) · 기준 라이벌 {arcade_total['rivals']}명 · 티어 {arcade_total['tiers']}단계")
    print(f"  - 한글 한 칸 변신: 단어 {hangul_total['words']}개 · 일일 {hangul_total['daily']}판 · 연습 {hangul_total['practice']}판 (오늘 {hangul_total['today']} · {hangul_total['today_start']}→{hangul_total['today_goal']} · 최소 {hangul_total['today_par']}수)")
    print(f"  - 오늘의 카드: 카드 {cards_total['cards']}장 · 덱 {cards_total['decks']}개 · 오늘 {cards_total['today']}")
    print(f"  - 세탁 라벨 읽기: 기호 {wash_total['symbols']}개 · 옷 {wash_total['quizzes']}벌 (기준 {wash_total['checkedOn']} 확인)")
    print(f"  - 재질 표시·분리배출: 마크 {recycle_total['marks']}종 · 품목 {recycle_total['quizzes']}개 (확인 {recycle_total['checkedOn']})")
    print(f"  - 식품 라벨·영양성분표: 영양성분 {food_total['nutrients']}행 · 항목 {food_total['items']}개 · 퀴즈 {food_total['quizzes']}문항 (확인 {food_total['checkedOn']})")
    print(f"  - 장보기 타이밍: 품목 {grocery_total['items']}개 · 지역 {grocery_total['regions']}곳 "
          f"({grocery_total['window']['start']} ~ {grocery_total['window']['end']} 기준 · 수집 {grocery_total['generated']})")
    print(f"  - 월급 미터: 환산 {paymeter_total['conversions']}종 (월 소정근로 {int(paymeter_total['monthlyHours'])}시간 기준)")
    print(f"  - 지하철역: 역 {subway_total['stations']}곳 · 오늘({subway_total['date']}) 정답 {subway_total['answer']}")
    print(f"  - 장바구니 리그: 품목 {basket_total['items']}개 · 목표 {basket_total['mission']['budget']:,}원 "
          f"±{basket_total['mission']['tolerance']:,}원 · 최고 {basket_total['best']['grade']}등급")
    print(f"  - 오늘 허브: 마감 {today_total['jobs']}건 · KEV {today_total['kev']}건 · AI {today_total['ai']}건 "
          f"(날씨 {'정상' if today_total['weather'] else '실패'} · 게임 {'정상' if today_total['wargame'] or today_total['clue'] else '없음'})")

if __name__ == "__main__":
    build_all()

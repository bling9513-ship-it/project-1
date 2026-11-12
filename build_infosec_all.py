# -*- coding: utf-8 -*-
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "exam_builder"))
import written_questions
import practical_questions
import summary_notes
import practical_summary
import generate_exam_data

written_qs = written_questions.get_written_questions()
practical_qs = practical_questions.get_practical_questions()
ismsp_qs = generate_exam_data.get_ismsp_questions()

written_summary = summary_notes.get_written_summary()
practical_summary_data = practical_summary.get_practical_summary()

ismsp_summary_data = [
    {
        "title": "1영역. 관리체계 수립 및 운영 (16개 기준 핵심)",
        "topics": [
            {
                "name": "1.1 기반 마련 및 1.2 위험 관리",
                "points": [
                    "1.1.1 경영진의 참여: 최고경영진의 보안위원회 주재 실적, 보안 예산 및 인력 배정 결재 증적 필수.",
                    "1.1.2 최고책임자의 지정: CISO/CPO 정식 임명. 망법상 CISO 겸직 제한(대기업 CISO의 CIO/개발본부장 겸직 금지) 준수.",
                    "1.1.4 범위 설정: 인증 대상 서비스 관련 시스템, 인프라, 네트워크, 개발망, 개인정보 흐름도 전수 식별.",
                    "1.2.2 위험 평가: 최고경영진 승인 하에 DOA(수용 가능한 위험 수준) 설정 및 초과 위험 대책 수립 필수."
                ]
            },
            {
                "name": "1.3 운영·점검 및 1.4 개선",
                "points": [
                    "1.4.1 법적 요구사항: 개정 법령(개인정보보호법, 망법 등) 준수 여부 연 1회 이상 정기 검토.",
                    "1.4.2 관리체계 점검: 연 1회 이상 독립된 내부감사를 수행하고 발견 결함을 경영진에 공식 보고."
                ]
            }
        ]
    },
    {
        "title": "2영역. 보호대책 요구사항 (64개 기준 핵심)",
        "topics": [
            {
                "name": "인적·물리보안 및 접근통제 (2.1 ~ 2.6)",
                "points": [
                    "2.2.3 퇴직 및 직무변경: 퇴직자 계정 및 모든 접근 권한은 당일 즉시 회수 및 비활성화 조치.",
                    "2.4.1 출입통제: 전산실/통제구역 출입기록은 최소 1년(또는 3년) 이상 보관 및 주기적 점검.",
                    "2.5.4 비밀번호 관리: 3종 8자리 또는 2종 10자리, 초기 패스워드 변경 강제 및 분기 1회 변경 유도.",
                    "2.6.2 개발망/운영망 분리: 개발망과 운영망 물리적/논리적 분리, 운영 DB 직접 접근 통제."
                ]
            },
            {
                "name": "접속기록, 암호화 및 운영보안 (2.6 ~ 2.11)",
                "points": [
                    "2.6.7 접속기록 보관: 최소 1년(5만명 이상 고유식별정보 처리 시 2년) 보관, 월 1회 이상 이상징후 점검.",
                    "2.7.1 암호정책: 고유식별정보, 비밀번호(일방향), 바이오정보 저장 시 암호화 적용.",
                    "2.8.5 시험 데이터 보안: 개발/테스트 시 실제 운영 개인정보 사용 금지(가명·익명 처리 데이터 사용).",
                    "2.9.3 백업 및 복구: 주기적 백업 수행 및 연 1회 이상 실제 복구 모의훈련 실시 증적 확보."
                ]
            }
        ]
    },
    {
        "title": "3영역. 개인정보 처리단계별 요구사항 (22개 기준 핵심)",
        "topics": [
            {
                "name": "수집·이용 및 제공·위탁 (3.1 ~ 3.3)",
                "points": [
                    "3.1.2 수집 제한: 필수항목과 선택항목을 엄격히 구분, 선택항목 미동의를 이유로 기본 서비스 제공 거부 금지.",
                    "3.2.1 현황 관리: 개인정보 처리방침과 실제 시스템 수집·이용 항목 간 100% 일치성 유지.",
                    "3.3.1 제3자 제공: 정보주체의 별도 동의 필수 (목적, 받는 자, 항목, 보유기간).",
                    "3.3.2 업무 위탁: 계약서에 법정 필수사항 명시 및 연 1회 이상 수탁사 처리 실태 관리·감독 점검 실시."
                ]
            },
            {
                "name": "파기 및 정보주체 권리보장 (3.4 ~ 3.5)",
                "points": [
                    "3.4.1 개인정보 파기: 보유기간 경과 또는 처리 목적 달성 시 지체 없이(5일 이내) 복구 불가능하게 영구 파기.",
                    "3.4.1 분리보관: 타 법령에 따라 보존해야 하는 경우 운영 DB에서 물리적/논리적으로 분리된 별도 저장소에 보관.",
                    "3.5.1 권리 보장: 정보주체의 열람, 정정, 삭제, 처리정지 요구에 대해 10일 이내에 조치 결과 통지."
                ]
            }
        ]
    }
]

written_data = {
    "title": "2026 이기적 정보보안기사 (필기) 100제 & 5대 과목 심층 요약집",
    "description": "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1회 실전 모의고사(50제), 2회 고난도 기출 모의고사(50제) 총 100문항 및 1권 이론서 전 과목 핵심 요약노트",
    "questions": written_qs,
    "summary": written_summary
}

practical_data = {
    "title": "2026 이기적 정보보안기사 (실기) 50제 & 실무 가이드",
    "description": "2026 이기적 정보보안기사 필기+실기 올인원 실기 편제 기준 1회 단답형 핵심 족보(25제), 2회 서술·실무형 침해사고 분석(25제) 총 50문항 및 실무 요약",
    "questions": practical_qs,
    "summary": practical_summary_data
}

ismsp_data = {
    "title": "ISMS-P 인증심사원 실전 결함판정 퀴즈 & 102개 기준 결함사례",
    "description": "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 실전 결함판정 시나리오 퀴즈(총 15문항) 및 102개 전 기준 결함사례 총람",
    "questions": ismsp_qs,
    "summary": {
        "title": "ISMS-P 102개 인증기준별 핵심 점검 포인트 및 결함도출 총람",
        "sections": ismsp_summary_data
    }
}

js_content = f"""// infosec_exam_data.js
// 2026 이기적 정보보안기사 필기+실기 올인원(영진닷컴) 및 ISMS-P 인증심사원 완전판 데이터셋
// 필기 100문항 (1회 50제 + 2회 50제) | 실기 50문항 (단답 25제 + 서술실무 25제) | ISMS-P 15문항

window.INFOSEC_WRITTEN_DATA = {json.dumps(written_data, ensure_ascii=False, indent=2)};

window.INFOSEC_PRACTICAL_DATA = {json.dumps(practical_data, ensure_ascii=False, indent=2)};

window.ISMSP_AUDITOR_DATA = {json.dumps(ismsp_data, ensure_ascii=False, indent=2)};
"""

with open("downloads/infosec-job-crawler/infosec_exam_data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Successfully generated infosec_exam_data.js!")
print(f"- Written questions: {len(written_qs)}")
print(f"- Practical questions: {len(practical_qs)}")
print(f"- ISMS-P questions: {len(ismsp_qs)}")

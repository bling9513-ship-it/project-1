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

from ismsp_summary_ext import get_ismsp_summary_data
ismsp_summary_data = get_ismsp_summary_data()

written_data = {
    "title": "2026 이기적 정보보안기사 (필기) 200제 & 내용별 심층요약·용어사전 158선",
    "description": "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1~4회 모의고사(각 50제) 총 200문항 및 내용별 심층 요약 50선 + 필수 핵심 용어사전 108선",
    "questions": written_qs,
    "summaries": written_summary.get("items", written_summary.get("sections", []))
}

practical_data = {
    "title": "2026 이기적 정보보안기사 (실기) 100제 & 단답형 족보·실무 가이드 95선",
    "description": "2026 이기적 정보보안기사 올인원 실기 편제 기준 1~4회(단답 50제 + 서술실무 50제) 총 100문항 및 실기 내용별 심층 요약 35선 + 단답형 족보 60선",
    "questions": practical_qs,
    "summaries": practical_summary_data.get("items", practical_summary_data.get("sections", []))
}

ismsp_data = {
    "title": "ISMS-P 인증심사원 실전 결함판정 퀴즈 (30제) & 인증기준 심층 요약 25선",
    "description": "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 결함판정 시나리오 퀴즈 1·2회(총 30문항) 및 인증기준별 요구사항·결함 판정 포인트 25선",
    "questions": ismsp_qs,
    "summaries": ismsp_summary_data
}

def _write_legacy_dataset():
    """과거 빌더 직접 출력 경로 (archive.db 파이프라인 도입 후에는 수동 실행 시에만 사용)."""
    js_content = f"""// infosec_exam_data.js
    // 2026 이기적 정보보안기사 필기+실기 올인원(영진닷컴) 및 ISMS-P 인증심사원 완전판 데이터셋
    // 필기 200문항 (1~4회 각 50제) | 실기 100문항 (단답 50제 + 서술실무 50제) | ISMS-P 30문항 (1·2회 각 15제)

    window.INFOSEC_WRITTEN_DATA = {json.dumps(written_data, ensure_ascii=False, indent=2)};

    window.INFOSEC_PRACTICAL_DATA = {json.dumps(practical_data, ensure_ascii=False, indent=2)};

    window.ISMSP_AUDITOR_DATA = {json.dumps(ismsp_data, ensure_ascii=False, indent=2)};
    """

    out_path = os.path.join(os.path.dirname(__file__), "infosec_exam_data.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"Successfully generated infosec_exam_data.js!")
    print(f"- Written questions: {len(written_qs)}")
    print(f"- Practical questions: {len(practical_qs)}")
    print(f"- ISMS-P questions: {len(ismsp_qs)}")


if __name__ == "__main__":
    _write_legacy_dataset()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
study_analyzer.py: 파일(PDF, TXT, MD) 및 URL 분석을 통한
핵심 요약 정리 및 실전 5지선다 문제 자동 출제 엔진 (LG EXAONE API 연동)
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.error

ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')
CUSTOM_STUDY_FILE = os.path.join(os.path.dirname(__file__), 'custom_study.json')
CUSTOM_STUDY_JS = os.path.join(os.path.dirname(__file__), 'custom_study.js')

def get_api_key():
    key = os.environ.get('EXAONE_API_KEY')
    if key:
        return key.strip()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('EXAONE_API_KEY='):
                    return line.strip().split('=', 1)[1].strip()
    return None

def extract_text_from_pdf(pdf_path, max_pages=15, start_page=1):
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        total = len(reader.pages)
        end = min(total, start_page + max_pages - 1)
        pages_text = []
        for p in range(start_page - 1, end):
            t = reader.pages[p].extract_text() or ''
            # Remove watermarks if any
            t = re.sub(r'sbs6128@naver\.com', '', t)
            pages_text.append(t)
        return "\n".join(pages_text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_text_from_url(url):
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Strip scripts, styles, tags
            html = re.sub(r'<script.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style.*?</style>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:6000] # limit length for prompt
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""

def call_exaone(prompt, system_prompt=None, max_tokens=2500, temperature=0.2):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("EXAONE API key not found in .env")
    
    if not system_prompt:
        system_prompt = "당신은 국가공인 정보보안 및 개인정보보호 전문 수석 연구원입니다. 주어진 지침에 따라 정확하고 실무적인 분석과 문제를 생성합니다."
        
    payload = {
        'model': 'k-exaone_v2.5',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': max_tokens,
        'temperature': temperature,
        'reasoning_effort': 'low'
    }
    
    req = urllib.request.Request(
        'https://api.exaone.ai/v1/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    )
    
    with urllib.request.urlopen(req, timeout=120) as resp:
        res_data = json.loads(resp.read().decode('utf-8'))
        content = res_data['choices'][0]['message']['content'].strip()
        return content

def analyze_and_generate_quiz(text, source_title="보안 학습 자료", source_type="문서"):
    """
    텍스트를 분석하여 1) 핵심 요약 노트, 2) 실전 5지선다 문제 세트 도출
    """
    print(f"Analyzing text ({len(text)} chars) for '{source_title}'...")
    
    # 1. 핵심 요약 생성
    summary_prompt = f"""다음 제공된 정보보안/개인정보보호 학습 텍스트를 정밀 분석하여 핵심 요약 노트를 작성해줘.
반드시 아래 JSON 포맷으로만 답변해줘.

[텍스트 내용]:
{text[:4500]}

[출력 JSON 포맷]:
{{
  "title": "{source_title}",
  "category": "핵심 분야 (예: 법령제도, 라이프사이클, 기술적보호조치, 관리체계 등)",
  "core_takeaways": [
    "핵심 요약 포인트 1 (구체적 기준이나 의무 포함)",
    "핵심 요약 포인트 2",
    "핵심 요약 포인트 3"
  ],
  "key_concepts": [
    {{"term": "핵심 용어/기준 1", "desc": "상세 정의 및 실무 유의점"}},
    {{"term": "핵심 용어/기준 2", "desc": "상세 정의 및 실무 유의점"}},
    {{"term": "핵심 용어/기준 3", "desc": "상세 정의 및 실무 유의점"}}
  ],
  "exam_points": [
    "시험 빈출 함정 포인트 1",
    "시험 빈출 함정 포인트 2"
  ]
}}"""

    summary_raw = call_exaone(summary_prompt, max_tokens=1500)
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', summary_raw, re.DOTALL)
    if match:
        summary_raw = match.group(1)
    else:
        m2 = re.search(r'(\{.*\})', summary_raw, re.DOTALL)
        if m2:
            summary_raw = m2.group(1)
            
    try:
        summary_data = json.loads(summary_raw)
    except Exception as e:
        print(f"Summary JSON parse error: {e}, using fallback")
        summary_data = {
            "title": source_title,
            "category": "보안 일반",
            "core_takeaways": ["핵심 내용 분석 완료"],
            "key_concepts": [],
            "exam_points": []
        }

    # 2. 실전 5지선다 문제 생성 (3문항)
    time.sleep(1.5) # Rate limit gap
    quiz_prompt = f"""다음 학습 텍스트 내용을 바탕으로 실제 국가공인 개인정보관리사(CPPG) 또는 정보보안기사 수준의 정밀한 5지선다 객관식 문제 3문항을 출제해줘.
보기는 반드시 ①, ②, ③, ④, ⑤ 5개여야 하며, 정답과 상세 법령/기술 해설을 포함해야 해.
반드시 아래 순수 JSON 배열 포맷으로만 답변해줘.

[텍스트 내용]:
{text[:4500]}

[출력 JSON 포맷]:
[
  {{
    "id": 1,
    "prompt": "다음 중 ...에 관한 설명으로 가장 옳지 않은 것은?",
    "choices": [
      "① ...",
      "② ...",
      "③ ...",
      "④ ...",
      "⑤ ..."
    ],
    "answer": 3,
    "explanation": "해설: ③번이 옳지 않은 이유와 정확한 법령 조항/기술 근거 설명."
  }}
]"""

    quiz_raw = call_exaone(quiz_prompt, max_tokens=2000)
    match_q = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', quiz_raw, re.DOTALL)
    if match_q:
        quiz_raw = match_q.group(1)
    else:
        m2 = re.search(r'(\[.*\])', quiz_raw, re.DOTALL)
        if m2:
            quiz_raw = m2.group(1)
            
    try:
        quiz_questions = json.loads(quiz_raw)
    except Exception as e:
        print(f"Quiz JSON parse error: {e}, fallback")
        quiz_questions = []

    result_item = {
        "id": f"study_{int(time.time())}",
        "title": summary_data.get("title", source_title),
        "source_type": source_type,
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "summary": summary_data,
        "questions": quiz_questions
    }
    
    return result_item

def save_custom_study(item):
    data = []
    if os.path.exists(CUSTOM_STUDY_FILE):
        try:
            with open(CUSTOM_STUDY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = []
            
    data.insert(0, item) # Newest first
    with open(CUSTOM_STUDY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    safe_js = json.dumps(data, ensure_ascii=False).replace('</script>', '<\\/script>')
    with open(CUSTOM_STUDY_JS, 'w', encoding='utf-8') as f:
        f.write('window.CUSTOM_STUDIES = ' + safe_js + ';\n')
        
    print(f"Saved custom study item '{item['title']}' to {CUSTOM_STUDY_FILE} and {CUSTOM_STUDY_JS}")

if __name__ == '__main__':
    print("Testing study_analyzer with EXAONE API...")
    # Sample test text from basic concepts (PIA & Technical Safeguards)
    test_text = """
    개인정보 영향평가(PIA: Privacy Impact Assessment)는 공공기관이 구축·운용하는 대규모 개인정보파일로 인해 정보주체의 프라이버시 침해 위험이 큰 경우,
    사전에 위험 요인을 체계적으로 분석하고 적절한 개선 대책을 마련하기 위한 법적 평가 제도이다.
    개인정보 보호법 제33조에 따라 공공기관의 장은 5만 명 이상의 정보주체에 관한 민감정보 또는 고유식별정보 처리가 수반되는 경우,
    다른 파일과의 연계를 통해 50만 명 이상의 정보주체에 관한 개인정보를 처리하게 되는 경우,
    그리고 100만 명 이상의 정보주체에 관한 개인정보파일을 구축·운용·변경하려는 경우 의무적으로 영향평가를 수행하여야 한다.
    영향평가 수행기관은 개인정보보호위원회가 지정하며, 수행 인력은 전문 인력과 일반 인력으로 구성된다.
    평가 완료 후 공공기관은 영향평가서를 작성하여 1년 이내에 보호위원회에 제출하고 도출된 개선사항을 충실히 이행해야 한다.
    """
    
    item = analyze_and_generate_quiz(test_text, source_title="개인정보 영향평가(PIA) 핵심 실무 및 출제 기준", source_type="개념서 발췌")
    save_custom_study(item)
    print("Test run completed successfully!")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
출퇴근길 보안 워게임 — 매일 자동 출제기.

archive.db 의 최근 cve_reports(신규 CVE·KEV·PoC)와 ai_insights(AI 보안·툴 이슈)를
소재로 EXAONE(k-exaone_v2.5)이 실전 시나리오 4지선다 문제를 만든다.

- 하루 1회만 생성: KST 오늘 날짜(created_date)에 is_daily=1 문제가 이미 있으면 건너뛴다.
- 기본 2문제: `python3 wargame_generator.py --daily 2`
- 저장 위치: archive.db 의 wargame_questions (빌더가 읽어 wargame.html 상단에 배치)
- EXAONE_API_KEY 는 로컬 .env 또는 환경변수에서만 읽는다. 키·프롬프트 원문은 로그·DB·git에 남기지 않는다.
- JSON 파싱 실패, 선택지 4개 아님, answer_idx 범위 밖, 이모지, 빈 필드, 중복 제목 등
  검증을 하나라도 통과하지 못한 문제는 DB에 넣지 않는다(전부 검증 후 단일 트랜잭션 적재).
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

sys.path.append(BASE_DIR)
from db_manager import (  # noqa: E402
    DB_PATH, WARGAME_CATEGORIES, WARGAME_LEVELS,
    count_wargame_questions, get_connection, get_wargame_titles,
    init_db, insert_wargame_questions, wargame_row_from_question,
)

KST = timezone(timedelta(hours=9))
MODEL = "k-exaone_v2.5"
API_URL = "https://api.exaone.ai/v1/chat/completions"

CATEGORY_KO = {
    "web": "웹 해킹(인젝션·인증·세션·파일 업로드·SSRF 등)",
    "log": "로그·침해 분석(웹/시스템 로그에서 침해 흔적 추적)",
    "sys": "시스템·권한 상승(리눅스/윈도 권한·설정·스케줄러·컨테이너)",
    "net": "네트워크·패킷(패킷/프로토콜 분석·TLS·DNS·프록시)",
}
LEVEL_KO = {"basic": "입문", "mid": "중급", "adv": "심화"}

# 이모지·변형 선택자·ZWJ (텍스트에 남으면 안 됨)
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U0001F1E6-\U0001F1FF\U00002600-\U000027BF"
    "\U00002B00-\U00002BFF\uFE0F\u200D\u20E3]"
)
HANGUL_RE = re.compile(r"[가-힣]")
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME)\b|Lorem ipsum|\bN/A\b", re.I)
HTML_TAG_RE = re.compile(r"<\s*(script|iframe|img|style|svg)\b", re.I)
FENCE_RE = re.compile(r"```")


def kst_now():
    return datetime.now(KST)


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# EXAONE
# ---------------------------------------------------------------------------
def get_api_key():
    key = os.environ.get("EXAONE_API_KEY")
    if key and key.strip():
        return key.strip()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("EXAONE_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return None


class ApiError(Exception):
    def __init__(self, code, message=""):
        super().__init__(f"HTTP {code} {message}".strip())
        self.code = code


def call_exaone(system_prompt, user_prompt, api_key, max_tokens=4200, timeout=180, temperature=0.6):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "reasoning_effort": "low",
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, str(e.reason or "")) from e
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# 소재 수집
# ---------------------------------------------------------------------------
def clean(text, limit):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text[:limit]


def load_sources(days=21, cve_limit=10, ai_limit=6):
    """최근 CVE(KEV·고위험 우선)와 AI 보안 인사이트를 프롬프트용 소재로 만든다."""
    init_db()
    since = (kst_now() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = get_connection()
    cves = conn.execute(
        """
        SELECT cve_id, title_ko, summary_ko, impact_ko, severity, cvss_score, is_kev,
               vendor, product, poc_count, published_at, cwe
        FROM cve_reports
        WHERE COALESCE(published_at, '') >= ?
        ORDER BY is_kev DESC,
                 CASE severity WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 ELSE 2 END,
                 COALESCE(cvss_score, 0) DESC,
                 COALESCE(published_at, '') DESC
        LIMIT ?
        """,
        (since, cve_limit),
    ).fetchall()

    ais = conn.execute(
        """
        SELECT item_key, title_ko, category, summary, tech_insight, tags, published_at
        FROM ai_insights
        WHERE COALESCE(published_at, '') >= ?
          AND (category LIKE '%보안%' OR tags LIKE '%보안%' OR tags LIKE '%security%')
        ORDER BY COALESCE(published_at, '') DESC
        LIMIT ?
        """,
        (since, ai_limit),
    ).fetchall()
    conn.close()

    sources = []
    for r in cves:
        lines = "- CVE: %s | %s" % (r["cve_id"], clean(r["title_ko"], 90))
        facts = []
        if r["vendor"] or r["product"]:
            facts.append("%s %s" % (r["vendor"] or "", r["product"] or ""))
        if r["cvss_score"] is not None:
            facts.append("CVSS %s %s" % (r["cvss_score"], r["severity"] or ""))
        if r["is_kev"]:
            facts.append("CISA KEV 실제 악용 등재")
        if r["poc_count"]:
            facts.append("공개 PoC %d건" % r["poc_count"])
        if facts:
            lines += " | " + " · ".join(x.strip() for x in facts if x.strip())
        lines += "\n  요약: " + clean(r["summary_ko"], 300)
        if r["impact_ko"]:
            lines += "\n  영향: " + clean(r["impact_ko"], 160)
        sources.append({"ref": r["cve_id"], "kind": "cve", "text": lines})
    for r in ais:
        lines = "- AI: %s | %s | %s" % (r["item_key"], clean(r["title_ko"], 90), clean(r["category"], 30))
        if r["published_at"]:
            lines += " | " + clean(r["published_at"], 10)
        lines += "\n  요약: " + clean(r["summary"], 260)
        if r["tech_insight"]:
            lines += "\n  포인트: " + clean(r["tech_insight"], 180)
        sources.append({"ref": r["item_key"], "kind": "ai", "text": lines})
    return sources


# ---------------------------------------------------------------------------
# 프롬프트
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "당신은 한국 정보보안 실무 교육 콘텐츠를 만드는 보안 강사입니다. "
    "실제 침해 사고·CVE·AI 보안 이슈를 학습용 시나리오로 각색해, 출퇴근길에 3분 안에 풀 수 있는 "
    "4지선다 워게임 문제를 만듭니다. 방어와 원리를 가르치는 것이 목적이며, 실제 시스템을 공격하는 "
    "그대로 쓸 수 있는 무기화된 공격 도구나 대량 공격 절차는 쓰지 않습니다. "
    "반드시 지정된 JSON 배열만 출력하고, 설명 문장이나 코드 펜스는 붙이지 않습니다."
)


def build_prompt(sources, wanted, existing_titles, used_cats=(), used_levels=()):
    lines = [s["text"] for s in sources]
    ref_ids = ", ".join(s["ref"] for s in sources)
    avoid = "; ".join(existing_titles[:40])
    diversity = ""
    if used_cats:
        diversity += ("- 이미 출제한 category: %s. 이번 문제는 그와 다른 category를 고르세요.\n"
                      % ", ".join(sorted(set(used_cats))))
    if used_levels:
        diversity += ("- 이미 출제한 difficulty: %s. 이번 문제는 다른 난이도를 고르세요.\n"
                      % ", ".join(sorted(set(used_levels))))
    return (
        f"아래 최신 보안 소재를 참고해 한국어 워게임 문제 {wanted}개를 JSON 배열로만 출력하세요.\n\n"
        "[소재]\n"
        + "\n".join(lines)
        + "\n\n[출제 조건]\n"
        f"1) 서로 다른 소재를 쓰고, 두 문제의 category는 가능하면 다르게 합니다. "
        f"category는 {', '.join(WARGAME_CATEGORIES)} 중 하나입니다.\n"
        f"2) difficulty는 {', '.join(WARGAME_LEVELS)} 중 하나이며, 두 문제의 난이도를 다르게 합니다.\n"
        + diversity +
        "3) 코드/로그/패킷 스니펫을 반드시 하나 이상 넣습니다. 실제 제품의 취약한 설정이나 코드 흐름을 "
        "재현하되, 학습 목적의 최소 예시로 각색하세요.\n"
        "4) 4지선다 보기는 정답 1개 + 그럴듯한 오답 3개. 오답은 흔한 착각을 자극해야 하며, "
        "정답 위치(answer_idx)는 0~3 중 하나이고 문제마다 다르게 합니다.\n"
        "5) hints는 정확히 2단계: 1단계는 관찰 포인트(어디를 볼지), 2단계는 풀이 방향(정답 개념). "
        "정답 문구를 그대로 노출하지 않습니다.\n"
        "6) principle은 공격 원리, impact는 실무 영향, vuln_code는 취약한 코드, secure_code는 "
        "같은 기능을 안전하게 고친 코드입니다. vuln_code와 secure_code는 반드시 다르고 실제로 동작 가능한 형태로 씁니다.\n"
        "7) source_ref에는 근거 소재의 ID(CVE 번호 또는 AI 항목 키)를 그대로 적습니다. "
        f"허용 값: {ref_ids}\n"
        "8) 모든 텍스트는 한국어. 영문 제품명·CVE ID·코드만 영문 유지. 이모지·마크다운·이모티콘 금지. "
        "제목은 12~40자, 상황 설명(context)은 40~220자, 보기 하나는 10~90자로 짧고 선명하게.\n"
        "9) 문장은 자연스러운 실무 한국어로 씁니다. '판단하라', '분석하라', '서술하라' 같은 딱딱한 명령형은 쓰지 말고 "
        "'~하세요' 또는 '~은 무엇인가?' 형태의 의문문으로 끝냅니다. '~라는 보고가 있다' 같은 모호한 인용 대신 "
        "소재의 제품·취약점 유형을 구체적으로 녹입니다.\n"
        "10) 보기는 주어와 서술어가 분명한 자연스러운 한국어 한 문장으로 씁니다. 자기 자신을 순환적으로 설명하는 "
        "문장(예: '인증이 허용된 부적절한 인증')이나 의미가 중복되는 표현을 쓰지 않습니다.\n"
        "10) vuln_code/secure_code는 code_lang과 같은 언어로 씁니다(예: code_lang이 http면 HTTP 요청/응답 예시, "
        "log면 로그/설정, python이면 Python). 설명과 예시가 서로 어긋나지 않게 합니다.\n"
        "11) 이미 있는 문제와 겹치지 않게 새 각도로 냅니다. 기존 제목(피할 것): " + (avoid or "없음") + "\n\n"
        "[출력 JSON 스키마]\n"
        "[{\n"
        '  "category": "web|log|sys|net",\n'
        '  "difficulty": "basic|mid|adv",\n'
        '  "title": "문제 제목",\n'
        '  "context": "문제 상황 설명",\n'
        '  "code_lang": "python|sql|javascript|php|java|bash|nginx|log|http|json|yaml 중 하나",\n'
        '  "code_label": "Python · 파일명 또는 Log · Apache access.log 같은 라벨",\n'
        '  "code_body": "코드/로그/패킷 본문 (줄바꿈은 \\n)",\n'
        '  "prompt": "무엇을 판단하거나 입력할지 묻는 한 문장",\n'
        '  "choices": ["보기1", "보기2", "보기3", "보기4"],\n'
        '  "answer_idx": 0,\n'
        '  "hints": ["1단계 힌트", "2단계 힌트"],\n'
        '  "principle": "공격 원리 3~4문장",\n'
        '  "impact": "실무 영향 1~2문장",\n'
        '  "vuln_code": "취약한 코드",\n'
        '  "secure_code": "안전하게 고친 코드",\n'
        '  "source_ref": "근거 소재 ID"\n'
        "}]\n"
        "JSON 배열만 출력하세요."
    )


# ---------------------------------------------------------------------------
# 검증
# ---------------------------------------------------------------------------
def parse_json_array(text):
    """EXAONE 응답에서 JSON 배열을 꺼낸다. 배열이 아닌 단일 객체도 1개 배열로 받아 준다."""
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    start = t.find("[")
    end = t.rfind("]")
    if start != -1 and end > start:
        try:
            data = json.loads(t[start:end + 1])
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    # 배열이 잘렸거나 단일 객체로 온 경우: 객체 단위로 건져 본다
    objs = []
    depth = 0
    buf = []
    in_str = False
    escape = False
    for ch in t:
        if in_str:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            buf.append(ch)
        elif ch == "{":
            depth += 1
            buf.append(ch)
        elif ch == "}":
            depth -= 1
            buf.append(ch)
            if depth == 0:
                chunk = "".join(buf).strip()
                buf = []
                try:
                    obj = json.loads(chunk)
                    if isinstance(obj, dict) and "title" in obj:
                        objs.append(obj)
                except json.JSONDecodeError:
                    pass
        elif depth > 0:
            buf.append(ch)
    return objs or None


def _text_errors(field, value, min_len, max_len, need_korean=True):
    errs = []
    if not isinstance(value, str):
        return ["%s: 문자열 아님" % field]
    v = value.strip()
    if len(v) < min_len:
        errs.append("%s: 너무 짧음(%d자)" % (field, len(v)))
    if len(v) > max_len:
        errs.append("%s: 너무 김(%d자 > %d)" % (field, len(v), max_len))
    if EMOJI_RE.search(v):
        errs.append("%s: 이모지 포함" % field)
    if PLACEHOLDER_RE.search(v):
        errs.append("%s: 자리표시자 의심" % field)
    if HTML_TAG_RE.search(v):
        errs.append("%s: HTML 태그 포함" % field)
    if need_korean and len(HANGUL_RE.findall(v)) < max(4, len(v) // 20):
        errs.append("%s: 한국어 비중 낮음" % field)
    return errs


def _code_errors(field, value, min_len=10, max_len=1500):
    errs = []
    if not isinstance(value, str):
        return ["%s: 문자열 아님" % field]
    v = value.strip()
    if len(v) < min_len:
        errs.append("%s: 너무 짧음(%d자)" % (field, len(v)))
    if len(v) > max_len:
        errs.append("%s: 너무 김(%d자 > %d)" % (field, len(v), max_len))
    if FENCE_RE.search(v):
        errs.append("%s: 코드 펜스 포함" % field)
    if EMOJI_RE.search(v):
        errs.append("%s: 이모지 포함" % field)
    if PLACEHOLDER_RE.search(v):
        errs.append("%s: 자리표시자 의심" % field)
    return errs


def _norm_title(s):
    return re.sub(r"[^0-9A-Za-z가-힣]", "", str(s or "")).lower()


def _similar(a, b):
    """제목 토큰 자카드 유사도 (중복 출제 방지)."""
    ta = set(re.findall(r"[가-힣A-Za-z0-9]+", str(a or "")))
    tb = set(re.findall(r"[가-힣A-Za-z0-9]+", str(b or "")))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _strip_hint_step(h):
    """힌트 앞의 '1단계:' '2단계 -' 같은 머리말은 화면에서 순서를 따로 보여 주므로 걷어낸다."""
    return re.sub(r"^\s*(?:[12]\s*단계|\(?[12]\)|[12]\))\s*[:：\-–]\s*", "", str(h or "")).strip()


def validate_question(raw, allowed_refs, existing_titles, today_str):
    """한 문제를 검증하고 정규화된 dict를 돌려준다. 실패 시 (None, errors)."""
    errs = []
    if not isinstance(raw, dict):
        return None, ["문제가 객체가 아님"]

    category = str(raw.get("category", "")).strip().lower()
    difficulty = str(raw.get("difficulty", "")).strip().lower()
    if category not in WARGAME_CATEGORIES:
        errs.append("category: 허용되지 않은 값(%r)" % category)
    if difficulty not in WARGAME_LEVELS:
        errs.append("difficulty: 허용되지 않은 값(%r)" % difficulty)

    errs += _text_errors("title", raw.get("title"), 8, 60)
    errs += _text_errors("context", raw.get("context"), 25, 320)
    errs += _text_errors("prompt", raw.get("prompt"), 8, 160)
    errs += _text_errors("code_label", raw.get("code_label"), 3, 60, need_korean=False)
    errs += _code_errors("code_body", raw.get("code_body"), 20, 1500)
    errs += _text_errors("principle", raw.get("principle"), 60, 700)
    errs += _text_errors("impact", raw.get("impact"), 20, 400)
    errs += _code_errors("vuln_code", raw.get("vuln_code"), 10, 800)
    errs += _code_errors("secure_code", raw.get("secure_code"), 10, 800)

    vuln = str(raw.get("vuln_code", "")).strip()
    secure = str(raw.get("secure_code", "")).strip()
    if vuln and secure and vuln == secure:
        errs.append("vuln_code와 secure_code가 동일")

    choices = raw.get("choices")
    if not isinstance(choices, list) or len(choices) != 4:
        errs.append("choices: 4개가 아님")
        choices = []
    else:
        seen = set()
        for i, c in enumerate(choices):
            errs += _text_errors("choices[%d]" % i, c, 5, 140, need_korean=True)
            key = _norm_title(c)
            if key in seen:
                errs.append("choices[%d]: 보기 중복" % i)
            seen.add(key)

    answer = raw.get("answer_idx")
    if isinstance(answer, bool) or not isinstance(answer, int):
        errs.append("answer_idx: 정수가 아님(%r)" % (answer,))
    elif not (0 <= answer <= 3):
        errs.append("answer_idx: 범위 밖(%r)" % (answer,))
    elif choices and answer >= len(choices):
        errs.append("answer_idx: 보기 수보다 큼")

    hints = raw.get("hints")
    if not isinstance(hints, list) or len(hints) != 2:
        errs.append("hints: 2단계가 아님")
        hints = hints if isinstance(hints, list) else []
    for i, h in enumerate(hints):
        errs += _text_errors("hints[%d]" % i, h, 10, 260)

    source_ref = str(raw.get("source_ref", "")).strip()
    if allowed_refs and source_ref not in allowed_refs:
        # 모델이 ID를 살짝 변형하는 경우를 위해 느슨하게 한 번 더 확인
        matched = next((r for r in allowed_refs if r.lower() in source_ref.lower() or source_ref.lower() in r.lower()), None)
        if matched:
            source_ref = matched
        else:
            errs.append("source_ref: 허용 소재 ID 아님(%r)" % source_ref)

    title = str(raw.get("title", "")).strip()
    ntitle = _norm_title(title)
    for old in existing_titles:
        if ntitle and ntitle == _norm_title(old):
            errs.append("title: 기존 문제와 동일(%r)" % title)
            break
        if ntitle and _similar(title, old) >= 0.72:
            errs.append("title: 기존 문제와 유사(%r)" % title)
            break

    if errs:
        return None, errs

    q = {
        "category": category,
        "difficulty": difficulty,
        "title": re.sub(r"\s+", " ", title),
        "context": re.sub(r"\s+", " ", raw["context"]).strip(),
        "code_lang": str(raw.get("code_lang", "")).strip()[:30],
        "code_label": re.sub(r"\s+", " ", raw["code_label"]).strip(),
        "code_body": raw["code_body"].strip(),
        "prompt": re.sub(r"\s+", " ", raw["prompt"]).strip(),
        "choices": [str(c).strip() for c in choices],
        "answer": answer,
        "hints": [_strip_hint_step(h) for h in hints],
        "principle": re.sub(r"\s+", " ", raw["principle"]).strip(),
        "impact": re.sub(r"\s+", " ", raw["impact"]).strip(),
        "vuln_code": raw["vuln_code"].strip(),
        "secure_code": raw["secure_code"].strip(),
        "source_ref": source_ref,
        "created_date": today_str,
        "is_daily": 1,
    }
    return q, []


def rotate_answer(q, new_idx):
    """정답 위치를 바꾸되 보기 내용은 그대로 유지한다."""
    old = q["answer"]
    if new_idx == old:
        return q
    shift = (old - new_idx) % 4
    q["choices"] = q["choices"][-shift:] + q["choices"][:-shift]
    q["answer"] = new_idx
    return q


def balance_answers(questions):
    """생성된 문제들의 정답 위치가 한쪽으로 몰리지 않게 회전한다."""
    used = set()
    for i, q in enumerate(questions):
        if q["answer"] not in used:
            used.add(q["answer"])
            continue
        for candidate in range(4):
            if candidate not in used:
                rotate_answer(q, candidate)
                used.add(candidate)
                break
    return questions


def to_row(q, idx, day_compact):
    q = dict(q)
    q["id"] = q["id"] if q.get("id") else "daily-%s-%02d" % (day_compact, idx + 1)
    q["blocks"] = [{"label": q["code_label"], "code": q["code_body"]}]
    q["explain"] = {
        "principle": q["principle"],
        "impact": q["impact"],
        "vuln": q["vuln_code"],
        "secure": q["secure_code"],
    }
    q["type"] = "choice"
    q["sort_order"] = idx
    return wargame_row_from_question(q, q["created_date"], is_daily=1, sort_order=idx)


def _existing_ids(prefix):
    conn = get_connection()
    rows = conn.execute("SELECT id FROM wargame_questions WHERE id LIKE ?", (prefix + "%",)).fetchall()
    conn.close()
    return {r[0] for r in rows}


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------
def generate(wanted, date_str, force=False, dry_run=False, max_attempts=0):
    today = kst_now()
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            log("[오류] --date 형식은 YYYY-MM-DD 입니다.")
            return 1
    else:
        date_str = today.strftime("%Y-%m-%d")
    day_compact = date_str.replace("-", "")

    if not force:
        existing_today = count_wargame_questions(is_daily=1, created_date=date_str)
        if existing_today:
            log("[건너뜀] %s 데일리 문제가 이미 %d개 있습니다 (하루 1회 출제). 필요하면 --force." % (date_str, existing_today))
            return 0

    api_key = get_api_key()
    if not api_key:
        log("[오류] EXAONE_API_KEY 가 .env 또는 환경변수에 없습니다. 출제를 중단합니다(DB 변경 없음).")
        return 1

    sources = load_sources()
    if not sources:
        log("[오류] 최근 cve_reports·ai_insights 소재가 없어 출제를 중단합니다(DB 변경 없음).")
        return 1
    allowed_refs = [s["ref"] for s in sources]
    log("[소재] 최근 CVE·AI 보안 소재 %d건 (허용 source_ref %d개)" % (len(sources), len(allowed_refs)))

    # EXAONE은 추론 토큰을 많이 쓴다. 한 번에 문제 1개씩 요청하고(잘림 방지),
    # 실패한 만큼만 다시 요청한다.
    existing_titles = get_wargame_titles()
    max_attempts = max_attempts or wanted * 2  # 08:00 배치 시간 안에 끝나도록 여유 있게 제한
    accepted = []
    errors_seen = []
    attempt = 0

    while len(accepted) < wanted and attempt < max_attempts:
        attempt += 1
        prompt = build_prompt(sources, 1, existing_titles + [q["title"] for q in accepted],
                              used_cats=[q["category"] for q in accepted],
                              used_levels=[q["difficulty"] for q in accepted])
        log("[EXAONE] 시도 %d/%d — 문제 1개 요청 (통과 %d/%d)"
            % (attempt, max_attempts, len(accepted), wanted))
        try:
            content = call_exaone(SYSTEM_PROMPT, prompt, api_key, max_tokens=8192, timeout=240,
                                  temperature=min(0.85, 0.6 + 0.05 * (attempt - 1)))
        except ApiError as e:
            log("  [EXAONE] HTTP %s — %s" % (e.code, "혼잡, 잠시 대기 후 재시도" if e.code in (429, 500, 502, 503, 504) else "요청 거부"))
            time.sleep(8 if e.code == 429 else 4)
            continue
        except Exception as e:  # 타임아웃·연결 실패
            log("  [EXAONE] 호출 실패(%s) — 재시도" % type(e).__name__)
            time.sleep(4)
            continue

        items = parse_json_array(content)
        if items is None:
            log("  [검증] JSON 배열 파싱 실패 — 이 응답은 버립니다. (응답 %d자, 끝: %r)"
                % (len(content or ""), (content or "")[-80:]))
            errors_seen.append("JSON 파싱 실패")
            continue

        for raw in items:
            if len(accepted) >= wanted:
                break
            q, errs = validate_question(raw, allowed_refs, existing_titles + [x["title"] for x in accepted], date_str)
            if q is None:
                log("  [검증] 탈락: %s" % "; ".join(errs[:4]))
                errors_seen.extend(errs)
                continue
            accepted.append(q)
            log("  [검증] 통과: [%s/%s] %s" % (q["category"], q["difficulty"], q["title"]))

    if len(accepted) < wanted:
        log("[경고] 요청 %d개 중 %d개만 검증을 통과했습니다." % (wanted, len(accepted)))
    if not accepted:
        log("[중단] 검증을 통과한 문제가 없어 DB에 아무것도 쓰지 않습니다.")
        return 1

    accepted = balance_answers(accepted)
    taken = _existing_ids("daily-%s-" % day_compact)
    rows = []
    seq = 1
    for q in accepted:
        while "daily-%s-%02d" % (day_compact, seq) in taken:
            seq += 1
        id_ = "daily-%s-%02d" % (day_compact, seq)
        taken.add(id_)
        q["id"] = id_
        rows.append(to_row(q, seq - 1, day_compact))
        seq += 1

    if dry_run:
        log("[드라이런] DB에 쓰지 않습니다. 검증 통과 문제 %d개:" % len(rows))
        for q in accepted:
            log(json.dumps(q, ensure_ascii=False, indent=1))
        return 0

    n = insert_wargame_questions(rows)
    log("[완료] %s 데일리 워게임 %d문제를 archive.db(wargame_questions)에 저장했습니다." % (date_str, n))
    for q in accepted:
        log("  - %s | %s | %s | 정답 %s | 근거 %s"
            % (q["id"], CATEGORY_KO.get(q["category"], q["category"]),
               q["title"], "ABCD"[q["answer"]], q["source_ref"] or "-"))
    return 0


def main():
    ap = argparse.ArgumentParser(description="출퇴근길 보안 워게임 데일리 자동 출제기")
    ap.add_argument("--daily", type=int, default=2, help="오늘 생성할 문제 수 (기본 2)")
    ap.add_argument("--date", default="", help="생성 날짜(YYYY-MM-DD, 기본 오늘 KST)")
    ap.add_argument("--force", action="store_true", help="오늘 문제가 이미 있어도 추가 생성")
    ap.add_argument("--dry-run", action="store_true", help="검증까지만 하고 DB에 쓰지 않음")
    args = ap.parse_args()

    if args.daily < 1 or args.daily > 4:
        log("[오류] --daily 는 1~4 사이여야 합니다.")
        return 1
    return generate(args.daily, args.date.strip(), force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())

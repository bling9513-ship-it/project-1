#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
하루 한 판 · 3단서 추리 — 매일 자동 출제기.

요일별 분야(월 기술·화 생활·수 문화·목 과학·금 자연·토 역사·일 자유)로
EXAONE(k-exaone_v2.5)이 1분 안에 풀리는 3단서 추리 문제 1개를 만든다.

- 하루 1회만 생성: KST 오늘 날짜(puzzle_date) 문제가 이미 있으면 건너뛴다.
- 저장 위치: archive.db 의 clue_questions (빌더가 읽어 clue.html '오늘의 문제'로 배치)
- EXAONE_API_KEY 는 로컬 .env 또는 환경변수에서만 읽는다. 키·프롬프트 원문은 로그·DB·git에 남기지 않는다.
- 형식 검증(단서 3개·보기 4개·정답 범위·이모지·빈 필드·중복 제목·정답 단어 노출)을
  하나라도 통과하지 못한 문제는 DB에 넣지 않는다.
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
from net_guard import read_limited

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

sys.path.append(BASE_DIR)
from db_manager import (  # noqa: E402
    CLUE_CATEGORIES, clue_row_from_question, count_clue_questions, get_clue_titles,
    insert_clue_questions, get_connection,
)

KST = timezone(timedelta(hours=9))
MODEL = "k-exaone_v2.5"
API_URL = "https://api.exaone.ai/v1/chat/completions"

CATEGORY_KO = {
    "tech": "기술(발명·인터넷·기기·소프트웨어)",
    "life": "생활(음식·집·습관·사물)",
    "culture": "문화(예술·언어·대중문화·풍속)",
    "science": "과학(물리·화학·천문·수학)",
    "nature": "자연(동물·식물·지구·기후)",
    "history": "역사(사건·인물·유물)",
}

# 월~일 (KST weekday(): 월=0)
WEEKDAY_CATEGORY = {0: "tech", 1: "life", 2: "culture", 3: "science", 4: "nature", 5: "history", 6: "tech"}

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


def call_exaone(system_prompt, user_prompt, api_key, max_tokens=3000, timeout=180, temperature=0.7):
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
            data = json.loads(read_limited(resp).decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, str(e.reason or "")) from e
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# 프롬프트
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "당신은 한국어로 짧은 상식 추리 문제를 만드는 퀴즈 작가입니다. "
    "널리 확인된 사실만 소재로 삼아, 단서 세 개로 정답을 좁혀 가는 1분짜리 4지선다 문제를 만듭니다. "
    "불확실한 연도·수치·최신 통계는 쓰지 않습니다. "
    "반드시 지정된 JSON 객체 하나만 출력하고, 설명 문장이나 코드 펜스는 붙이지 않습니다."
)


def _recent_titles(limit=40):
    try:
        return get_clue_titles(limit=limit)
    except Exception:
        return []


def build_prompt(category, date_str, existing_titles):
    avoid = "; ".join(existing_titles[:30])
    return (
        "아래 조건에 맞는 3단서 추리 문제 1개를 JSON 객체로만 출력하세요.\n\n"
        "[조건]\n"
        "1) 분야: %s. 이 분야 안에서 한국 사람이 흥미를 느낄 만한 소재를 고르세요(보안에 국한하지 않습니다).\n"
        "2) 정답은 사람·사물·동물·현상·발명품·장소·개념 중 하나로, 보기에서 한 단어~두 단어로 표현됩니다. "
        "정답은 널리 알려진 사실로 확인 가능해야 하며, 최근 몇 달 안에 바뀔 수 있는 값(주가·순위·수상자)은 피합니다.\n"
        "3) 단서 3개는 점점 구체적으로 좁혀야 합니다.\n"
        "   - 단서1: 넓은 범주와 배경만 (정답을 바로 알 수 없게)\n"
        "   - 단서2: 결정적인 특징 하나 (조금만 아는 사람은 여기서 맞힐 수 있게)\n"
        "   - 단서3: 정답 직전까지 좁히되 정답 단어 자체는 쓰지 않음\n"
        "   각 단서는 40~150자, 서로 다른 정보를 담고, 같은 문장을 반복하지 않습니다.\n"
        "4) 정답 단어(또는 그 핵심 명사)는 title·prompt·clue1·clue2·clue3 어디에도 등장하면 안 됩니다.\n"
        "5) title은 12~34자로, 정답을 노출하지 않는 궁금증 유발형 한 줄입니다(예: '달력이 맞추지 못한 여섯 시간').\n"
        "6) prompt는 정답을 묻는 자연스러운 한 문장입니다(예: '이 동물은 무엇일까요?').\n"
        "7) choices는 4개: 정답 1개 + 같은 범주에서 헷갈릴 만한 오답 3개. 보기마다 2~20자, 서로 중복되지 않게.\n"
        "8) answer에는 choices 중 정답 보기를 글자 그대로 복사해 넣습니다. answer_idx는 그 보기의 위치(0~3)이며 "
        "answer와 반드시 일치해야 합니다. 정답을 0번에 고정하지 마세요.\n"
        "9) explanation은 2~3문장, 왜 그 답인지 근거를 담아 40~260자로 씁니다.\n"
        "10) source_ref에는 근거가 되는 자료의 성격을 짧게 적습니다(예: '3M 공식 연혁', '국립국어원 자료'). "
        "확실한 출처가 없으면 빈 문자열로 둡니다.\n"
        "11) 모든 텍스트는 한국어. 고유명사·단위만 영문 유지. 이모지·마크다운·따옴표 장식·줄바꿈은 쓰지 않습니다.\n"
        "12) 이미 있는 문제와 소재가 겹치지 않게 새 각도로 냅니다. 기존 제목(피할 것): "
        + (avoid or "없음")
        + "\n\n[출력 JSON]\n"
        "{\n"
        '  "category": "' + category + '",\n'
        '  "title": "제목",\n'
        '  "prompt": "질문",\n'
        '  "clues": ["단서1", "단서2", "단서3"],\n'
        '  "choices": ["보기1", "보기2", "보기3", "보기4"],\n'
        '  "answer": "정답 보기",\n'
        '  "answer_idx": 0,\n'
        '  "explanation": "해설",\n'
        '  "source_ref": "근거 자료"\n'
        "}\n"
        "JSON 객체만 출력하세요."
    )


# ---------------------------------------------------------------------------
# 검증
# ---------------------------------------------------------------------------
def parse_json_object(text):
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        obj = json.loads(t[start:end + 1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


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
    if FENCE_RE.search(v):
        errs.append("%s: 코드 펜스 포함" % field)
    if need_korean and len(HANGUL_RE.findall(v)) < max(4, len(v) // 20):
        errs.append("%s: 한국어 비중 낮음" % field)
    return errs


def _norm(s):
    return re.sub(r"[^0-9A-Za-z가-힣]", "", str(s or "")).lower()


def _answer_leak(answer, texts):
    """정답 단어가 제목·질문·단서에 그대로 노출되었는지 확인한다."""
    core = _norm(answer)
    if not core:
        return True
    # '밀레니엄 버그(Y2K)' 같은 표기는 괄호 앞부분을 핵심어로 본다
    head = re.split(r"[(（]", str(answer))[0]
    keys = {core, _norm(head)}
    for t in texts:
        n = _norm(t)
        for k in keys:
            if k and len(k) >= 2 and k in n:
                return True
    return False


def normalize_category(value, fallback):
    """모델이 분야를 한글 라벨이나 다른 표기로 돌려줘도 요청한 분야로 맞춘다."""
    v = str(value or "").strip().lower()
    if v in CLUE_CATEGORIES:
        return v
    for key, label in CATEGORY_KO.items():
        short = label.split("(")[0]
        if v and (short in v or v in short):
            return key
    return fallback


def validate_question(raw, today_str, category, existing_titles):
    errs = []
    if not isinstance(raw, dict):
        return None, ["문제가 객체가 아님"]

    got_cat = normalize_category(raw.get("category"), category)

    errs += _text_errors("title", raw.get("title"), 8, 44)
    errs += _text_errors("prompt", raw.get("prompt"), 8, 80)
    errs += _text_errors("explanation", raw.get("explanation"), 30, 320)

    clues = raw.get("clues")
    if not isinstance(clues, list) or len(clues) != 3:
        errs.append("clues: 3개가 아님")
        clues = clues if isinstance(clues, list) else []
    else:
        seen = set()
        for i, c in enumerate(clues):
            errs += _text_errors("clues[%d]" % i, c, 20, 170)
            key = _norm(c)
            if key in seen:
                errs.append("clues[%d]: 중복" % i)
            seen.add(key)

    choices = raw.get("choices")
    if not isinstance(choices, list) or len(choices) != 4:
        errs.append("choices: 4개가 아님")
        choices = []
    else:
        seen = set()
        for i, c in enumerate(choices):
            errs += _text_errors("choices[%d]" % i, c, 2, 24, need_korean=False)
            key = _norm(c)
            if key in seen:
                errs.append("choices[%d]: 보기 중복" % i)
            seen.add(key)

    answer = raw.get("answer_idx")
    if isinstance(answer, bool) or not isinstance(answer, int):
        answer = 0
    elif not (0 <= answer <= 3):
        answer = 0

    # 정답 위치는 모델의 answer_idx 대신 '정답 보기 문장'에서 직접 계산한다(위치 오기 방지).
    answer_text = str(raw.get("answer") or raw.get("answer_text") or "").strip()
    if choices and answer_text:
        target = _norm(answer_text)
        match = next((i for i, c in enumerate(choices) if _norm(c) == target), None)
        if match is None:
            match = next((i for i, c in enumerate(choices)
                          if target and (_norm(c) in target or target in _norm(c))), None)
        if match is None:
            errs.append("answer: 보기에서 찾을 수 없음(%r)" % answer_text)
        else:
            answer = match
    elif choices:
        # answer 문장이 없는 응답은 index 만으로 판단한다(해설 일치 확인으로 보완).
        if answer >= len(choices):
            errs.append("answer_idx: 보기 수보다 큼")

    if choices and answer < len(choices):
        texts = [raw.get("title", ""), raw.get("prompt", "")] + list(clues)
        if _answer_leak(choices[answer], texts):
            errs.append("정답 단어가 제목·질문·단서에 노출됨(%r)" % choices[answer])

    # 해설이 가리키는 보기와 answer_idx가 어긋나는 경우를 잡는다.
    # (모델이 1부터 세거나 정답 위치를 잘못 적는 일이 있어, 해설에 유일하게 등장하는 보기로 교정한다.)
    explanation = str(raw.get("explanation", ""))
    if choices and not answer_text:
        expl_n = _norm(explanation)
        hits = [i for i, c in enumerate(choices) if _norm(c) and _norm(c) in expl_n]
        if answer < len(choices) and _norm(choices[answer]) not in expl_n:
            if len(hits) == 1:
                answer = hits[0]
            else:
                errs.append("answer_idx: 해설과 정답 불일치")

    title = str(raw.get("title", "")).strip()
    ntitle = _norm(title)
    for old in existing_titles:
        if ntitle and ntitle == _norm(old):
            errs.append("title: 기존 문제와 동일(%r)" % title)
            break

    if errs:
        return None, errs

    return {
        "category": got_cat,
        "title": re.sub(r"\s+", " ", title),
        "prompt": re.sub(r"\s+", " ", raw["prompt"]).strip(),
        "clues": [re.sub(r"\s+", " ", c).strip() for c in clues],
        "choices": [re.sub(r"\s+", " ", str(c)).strip() for c in choices],
        "answer": answer,
        "explanation": re.sub(r"\s+", " ", raw["explanation"]).strip(),
        "source_ref": str(raw.get("source_ref") or "").strip()[:80],
        "puzzle_date": today_str,
        "is_daily": 1,
    }, []


def rotate_answer(q, new_idx):
    old = q["answer"]
    if new_idx == old:
        return q
    shift = (new_idx - old) % 4
    q["choices"] = q["choices"][-shift:] + q["choices"][:-shift]
    q["answer"] = new_idx
    return q


def spread_answer(q, date_str):
    """정답 위치가 날짜에 따라 흩어지도록 날짜 기반으로 회전한다(0에 몰리는 것 방지)."""
    target = sum(int(x) for x in date_str.replace("-", "")) % 4
    return rotate_answer(q, target)


def to_row(q, date_str, seq):
    q = dict(q)
    q["id"] = q.get("id") or "daily-%s-%02d" % (date_str.replace("-", ""), seq)
    q["sort_order"] = seq - 1
    return clue_row_from_question(q, date_str, is_daily=1, sort_order=seq - 1)


def _existing_ids(prefix):
    conn = get_connection()
    rows = conn.execute("SELECT id FROM clue_questions WHERE id LIKE ?", (prefix + "%",)).fetchall()
    conn.close()
    return {r[0] for r in rows}


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------
def generate(date_str, force=False, dry_run=False, max_attempts=4, category=None):
    if date_str:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            log("[오류] --date 형식은 YYYY-MM-DD 입니다.")
            return 1
    else:
        date_str = kst_now().strftime("%Y-%m-%d")

    if not force:
        existing_today = count_clue_questions(created_date=date_str)
        if existing_today:
            log("[건너뜀] %s 문제가 이미 %d개 있습니다 (하루 1회 출제). 필요하면 --force." % (date_str, existing_today))
            return 0

    day = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    cat = category or WEEKDAY_CATEGORY[day]
    if cat not in CLUE_CATEGORIES:
        log("[오류] --category 는 %s 중 하나입니다." % ", ".join(CLUE_CATEGORIES))
        return 1

    api_key = get_api_key()
    if not api_key:
        log("[오류] EXAONE_API_KEY 가 .env 또는 환경변수에 없습니다. 출제를 중단합니다(DB 변경 없음).")
        return 1

    existing_titles = _recent_titles()
    accepted = None
    attempt = 0
    while accepted is None and attempt < max_attempts:
        attempt += 1
        prompt = build_prompt(cat, date_str, existing_titles)
        log("[EXAONE] 시도 %d/%d — %s 문제 1개 요청" % (attempt, max_attempts, CATEGORY_KO.get(cat, cat)))
        try:
            content = call_exaone(SYSTEM_PROMPT, prompt, api_key, max_tokens=6000, timeout=200,
                                  temperature=min(0.9, 0.65 + 0.06 * (attempt - 1)))
        except ApiError as e:
            log("  [EXAONE] HTTP %s — %s" % (e.code, "혼잡, 잠시 대기 후 재시도" if e.code in (429, 500, 502, 503, 504) else "요청 거부"))
            time.sleep(8 if e.code == 429 else 4)
            continue
        except Exception as e:
            log("  [EXAONE] 호출 실패(%s) — 재시도" % type(e).__name__)
            time.sleep(4)
            continue

        raw = parse_json_object(content)
        if raw is None:
            log("  [검증] JSON 객체 파싱 실패 — 이 응답은 버립니다. (응답 %d자)" % len(content or ""))
            continue
        q, errs = validate_question(raw, date_str, cat, existing_titles)
        if q is None:
            log("  [검증] 탈락: %s" % "; ".join(errs[:4]))
            continue
        accepted = q
        log("  [검증] 통과: [%s] %s" % (q["category"], q["title"]))

    if accepted is None:
        log("[중단] 검증을 통과한 문제가 없어 DB에 아무것도 쓰지 않습니다.")
        return 1

    accepted = spread_answer(accepted, date_str)
    taken = _existing_ids("daily-%s-" % date_str.replace("-", ""))
    seq = 1
    while "daily-%s-%02d" % (date_str.replace("-", ""), seq) in taken:
        seq += 1
    accepted["id"] = "daily-%s-%02d" % (date_str.replace("-", ""), seq)
    row = to_row(accepted, date_str, seq)

    if dry_run:
        log("[드라이런] DB에 쓰지 않습니다. 검증 통과 문제:")
        log(json.dumps(accepted, ensure_ascii=False, indent=1))
        return 0

    n = insert_clue_questions([row])
    log("[완료] %s 3단서 추리 문제 %d개를 archive.db(clue_questions)에 저장했습니다." % (date_str, n))
    log("  - %s | %s | %s | 정답 %s" % (accepted["id"], CATEGORY_KO.get(accepted["category"]), accepted["title"],
                                        "ABCD"[accepted["answer"]]))
    return 0


def main():
    ap = argparse.ArgumentParser(description="하루 한 판 · 3단서 추리 데일리 자동 출제기")
    ap.add_argument("--daily", type=int, default=1, help="오늘 생성할 문제 수 (1만 지원)")
    ap.add_argument("--date", default="", help="생성 날짜(YYYY-MM-DD, 기본 오늘 KST)")
    ap.add_argument("--force", action="store_true", help="오늘 문제가 이미 있어도 추가 생성")
    ap.add_argument("--dry-run", action="store_true", help="검증까지만 하고 DB에 쓰지 않음")
    ap.add_argument("--category", default="", help="분야 강제 지정(%s)" % ", ".join(CLUE_CATEGORIES))
    args = ap.parse_args()

    if args.daily < 1:
        log("[오류] --daily 는 1 이상이어야 합니다.")
        return 1
    if args.daily > 1:
        log("[안내] 하루 한 판이므로 1개만 생성합니다.")
    return generate(args.date.strip(), force=args.force, dry_run=args.dry_run,
                    category=(args.category.strip().lower() or None))


if __name__ == "__main__":
    sys.exit(main())

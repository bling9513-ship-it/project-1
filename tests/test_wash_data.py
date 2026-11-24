#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""세탁 라벨 읽기(wash.html) 데이터·구성 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · 기호 사전: 카테고리 4종(물세탁·표백·건조·다림질·드라이)에 대표 기호가 모두 있는지
    (물세탁 30℃·약·손세탁·금지, 표백 염소/산소·금지, 건조 옷걸이/그늘/기계건조 금지,
     다림질 120℃·금지, 드라이 석유계·금지)
  · 기준 판본: KS K 0021:2024(2024-12-31 개정) · ISO 3758:2023 대조 표기
  · 다림질 점 1개 = 최대 120℃, 손세탁은 30℃·40℃(KS) / 상온 20~30℃(무숫자 국제 기호)
  · 모든 기호에 인라인 SVG(48×48 뷰박스) · 이름 · 한 줄 뜻 · 주의할 점이 있는지
  · 금지 기호에는 X 선, 약한 세탁에는 밑줄, 물 온도 기호에는 숫자가 그려졌는지
  · 퀴즈 6벌: 옷 이름·소재·기호 조합·4지선다·정답 인덱스(0~3)·근거 기호(라벨 기호 안)
  · 이모지 0 · 그라데이션 0 · 입력 필드 0 · 인라인 이벤트 핸들러 0
  · 공통 셸 21페이지 등록 · 하단 탭 바 · 출처(국가기술표준원 KS K 0021:2024) · ISO 3758:2023 대조 · 확인일 표기
  · wash_data.json 과 wash.html 에 심긴 데이터가 일치하는지

실행: python3 tests/test_wash_data.py
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WASH_HTML = os.path.join(BASE_DIR, "wash.html")
WASH_JSON = os.path.join(BASE_DIR, "wash_data.json")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 26
CHECKED_ON = "2026-11-22"
CATEGORIES = ("물세탁", "표백", "건조", "다림질·드라이")
REQUIRED_SYMBOLS = (
    "wash-30", "wash-30-weak", "wash-hand", "wash-no",
    "bleach-any", "bleach-oxygen", "bleach-no",
    "dry-hanger", "dry-shade", "dry-flat", "dry-machine-no",
    "iron-low", "iron-no",
    "clean-p", "clean-f", "clean-no",
)
GARMENT_WORDS = ("울 니트", "바람막이", "셔츠", "패딩", "데님", "캐시미어")

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_html():
    with open(WASH_HTML, encoding="utf-8") as handle:
        src = handle.read()
    match = re.search(r'<script[^>]*id="washData"[^>]*>(.*?)</script>', src, re.S)
    if not match:
        raise SystemExit("wash.html 에서 세탁 데이터 블록을 찾지 못했습니다.")
    return src, json.loads(match.group(1))


def check_standard(data):
    std = data.get("standard") or {}
    check("표준 번호", std.get("code") == "KS K 0021:2024", std.get("code"))
    check("표준 기관", std.get("org") == "국가기술표준원", std.get("org"))
    check("표준 제목", "섬유 제품의 취급" in (std.get("title") or ""), std.get("title"))
    check("표준 판본", "2024-12-31" in (std.get("edition") or ""), std.get("edition"))
    check("표준 판본 고시번호", "2024-0699" in (std.get("edition") or ""), std.get("edition"))
    check("국제 표준 판본", std.get("intl") == "ISO 3758:2023", std.get("intl"))
    check("국제 표준 대조 문구", "ISO 3758:2023" in (std.get("intlNote") or ""), std.get("intlNote"))
    check("표준 원문 링크", (std.get("url") or "").startswith("https://"), std.get("url"))
    check("확인일", data.get("checkedOn") == CHECKED_ON, data.get("checkedOn"))
    check("카테고리 4종", tuple(data.get("categories") or ()) == CATEGORIES, data.get("categories"))


def check_symbols(data):
    symbols = data.get("symbols") or []
    by_id = {item.get("id"): item for item in symbols}
    check("기호 15개 이상", len(symbols) >= 15, len(symbols))
    check("기호 ID 고유", len(by_id) == len(symbols))
    check("기호 ID 누락 없음", all(by_id.get(sid) for sid in REQUIRED_SYMBOLS),
          [sid for sid in REQUIRED_SYMBOLS if not by_id.get(sid)])
    cats = {item.get("cat") for item in symbols}
    check("카테고리 값", cats == set(CATEGORIES), sorted(cats))

    for item in symbols:
        sid = item.get("id")
        check("%s 이름" % sid, bool(item.get("name")), item.get("name"))
        check("%s 한 줄 뜻" % sid, len(item.get("meaning") or "") >= 12, item.get("meaning"))
        check("%s 주의" % sid, len(item.get("caution") or "") >= 12, item.get("caution"))
        svg = item.get("svg") or ""
        check("%s 인라인 SVG" % sid, svg.startswith("<svg") and 'viewBox="0 0 48 48"' in svg, svg[:40])

    # 물 온도 기호: 숫자 표기 / 약한 세탁: 밑줄 / 금지: X 선
    check("30℃ 숫자", ">30<" in by_id["wash-30"]["svg"], by_id["wash-30"]["svg"][-80:])
    check("40℃ 숫자", ">40<" in by_id["wash-40"]["svg"] if "wash-40" in by_id else True)
    check("약한 세탁 밑줄", "M13.5 41.6h21" in by_id["wash-30-weak"]["svg"], by_id["wash-30-weak"]["svg"][-90:])
    check("약한 세탁 숫자 유지", ">30<" in by_id["wash-30-weak"]["svg"])
    for sid in ("wash-no", "bleach-no", "dry-machine-no", "iron-no", "clean-no"):
        check("%s 금지 X" % sid, "l37 37" in by_id[sid]["svg"], by_id[sid]["svg"][-90:])
    check("손세탁 손 그림", "M19.4 32.8" in by_id["wash-hand"]["svg"], by_id["wash-hand"]["svg"][-120:])
    check("산소계 사선", "stroke-width=\"1.6\"" in by_id["bleach-oxygen"]["svg"])

    # 다림질 점 1개: KS K 0021:2024 · ISO 3758:2023 은 최대 120℃ (110℃ 아님)
    iron = by_id["iron-low"]
    check("다림질 120℃ 이름", "120℃" in iron["name"], iron["name"])
    check("다림질 120℃ 뜻", "120℃" in iron["meaning"], iron["meaning"])
    check("다림질 이름에 110℃ 없음", "110℃" not in iron["name"], iron["name"])
    check("다림질 뜻에 110℃ 단정 없음", "110℃ 이하" not in iron["meaning"], iron["meaning"])
    check("다림질 옛 판본 안내", "110℃" in iron["caution"], iron["caution"])

    # 손세탁: KS K 0021:2024 는 30℃·40℃ 로 나뉘고, 숫자 없는 국제 기호는 상온(20~30℃)
    hand = by_id["wash-hand"]
    check("손세탁 이름에 세탁기 금지", "세탁기" in hand["name"], hand["name"])
    check("손세탁 KS 30℃·40℃ 안내", "30℃" in hand["caution"] and "40℃" in hand["caution"], hand["caution"])
    check("손세탁 상온 안내", "상온" in hand["caution"] and "20~30℃" in hand["caution"], hand["caution"])
    check("손세탁 ISO 판본 표기", "ISO 3758:2023" in hand["caution"], hand["caution"])
    check("염소계·산소계 빈 세모", "l37 37" not in by_id["bleach-any"]["svg"]
          and 'stroke-width="1.6"' not in by_id["bleach-any"]["svg"])

    # 산소계·드라이 글자 표기
    check("드라이 P", ">P<" in by_id["clean-p"]["svg"], by_id["clean-p"]["svg"][-80:])
    check("드라이 F(석유계)", ">F<" in by_id["clean-f"]["svg"], by_id["clean-f"]["svg"][-80:])


def check_quizzes(data):
    quizzes = data.get("quizzes") or []
    by_id = {item.get("id"): item for item in data.get("symbols") or []}
    check("퀴즈 5벌 이상", len(quizzes) >= 5, len(quizzes))
    check("퀴즈 ID 고유", len({q.get("id") for q in quizzes}) == len(quizzes))
    garments = " ".join(q.get("garment") or "" for q in quizzes)
    for word in GARMENT_WORDS:
        check("옷 종류 %s" % word, word in garments, garments)
    for quiz in quizzes:
        qid = quiz.get("id")
        check("%s 소재" % qid, bool(quiz.get("material")), quiz.get("material"))
        check("%s 질문" % qid, "어떻게 세탁" in (quiz.get("question") or ""), quiz.get("question"))
        options = quiz.get("options") or []
        check("%s 보기 4개" % qid, len(options) == 4, len(options))
        check("%s 보기 중복 없음" % qid, len(set(options)) == len(options))
        check("%s 보기 길이" % qid, all(len(text) >= 10 for text in options), [len(t) for t in options])
        answer = quiz.get("answer")
        check("%s 정답 인덱스" % qid, isinstance(answer, int) and 0 <= answer < len(options), answer)
        symbols = quiz.get("symbols") or []
        check("%s 라벨 기호 3개 이상" % qid, len(symbols) >= 3, symbols)
        check("%s 라벨 기호 존재" % qid, all(sid in by_id for sid in symbols), symbols)
        check("%s 기호 중복 없음" % qid, len(set(symbols)) == len(symbols), symbols)
        evidence = quiz.get("evidence") or []
        check("%s 근거 기호" % qid, bool(evidence) and set(evidence) <= set(symbols), evidence)
        check("%s 해설" % qid, len(quiz.get("explain") or "") >= 20, quiz.get("explain"))

    # 세탁법이 서로 다른 성격의 옷으로 구성됐는지(같은 라벨 반복 금지)
    labels = [tuple(q.get("symbols") or []) for q in quizzes]
    check("라벨 조합 서로 다름", len(set(labels)) == len(labels), labels)

    # 판본 정정이 퀴즈 보기·해설에도 반영됐는지
    shirt = next((q for q in quizzes if q.get("id") == "white-shirt"), {})
    shirt_answer = (shirt.get("options") or [""])[shirt.get("answer") or 0]
    check("흰 셔츠 정답 120℃", "120℃" in shirt_answer, shirt_answer)
    check("흰 셔츠 해설 120℃", "120℃" in (shirt.get("explain") or ""), shirt.get("explain"))
    knit = next((q for q in quizzes if q.get("id") == "wool-knit"), {})
    knit_answer = (knit.get("options") or [""])[knit.get("answer") or 0]
    check("울 니트 정답 상온 손세탁", "상온" in knit_answer and "20~30℃" in knit_answer, knit_answer)


def check_html(src, data):
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("입력 필드 없음", "<input" not in src.lower() and "<textarea" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+[\s\"']on[a-z]+\s*=", src, re.I))
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 wash.html 등록", src.count('href="wash.html"') >= 2, src.count('href="wash.html"'))
    check("현재 페이지 표시", 'data-page="wash"' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("데스크톱 드롭다운에 세탁 라벨", "세탁 라벨 읽기" in src)
    check("모바일 전체 메뉴에 세탁 라벨", "세탁 라벨" in src)

    check("기호 도감 탭", 'id="wsTabGuide"' in src and "기호 도감" in src)
    check("라벨 읽기 퀴즈 탭", 'id="wsTabQuiz"' in src and "라벨 읽기 퀴즈" in src)
    chips = re.findall(r'<button[^>]*class="ws-chip[ "]', src)
    check("카테고리 칩 5개", len(chips) == 5, len(chips))
    rows = re.findall(r'class="ws-row" data-cat="([^"]+)" data-row="([^"]+)"', src)
    check("라벨 줄 5개", len(rows) == 5, rows)
    check("라벨 줄 이름", [name for _cat, name in rows] == ["물세탁", "표백", "다림질", "드라이", "건조"], rows)
    cats = {cat for cat, _name in rows}
    check("다림질·드라이 줄이 한 카테고리", cats == set(CATEGORIES), sorted(cats))
    check("기호 버튼 %d개" % len(data["symbols"]), src.count('class="ws-sym"') == len(data["symbols"]), src.count('class="ws-sym"'))
    check("기호 버튼 aria-pressed", 'class="ws-sym" data-sym="wash-30" aria-pressed="false"' in src)
    check("기호 버튼 aria-label", 'aria-label="30℃ 이하 일반 세탁"' in src)
    check("설명 카드 즉시 노출", 'id="wsDesc"' in src and 'aria-live="polite"' in src and "30℃ 이하 일반 세탁" in src)
    check("주의 표기", "주의" in src and 'id="wsDescCaution"' in src)
    check("퀴즈 진행 표시", 'id="wsQuizProgress"' in src and "1 / 6" in src)
    check("퀴즈 옵션 컨테이너", 'id="wsOptions"' in src)
    check("근거 기호 표시", "근거 기호" in src and "is-evidence" in src)
    check("감속 모션 대응", "prefers-reduced-motion" in src)
    check("다크 테마 변수", '[data-theme="dark"]' in src)
    check("출처 링크", "standard.go.kr" in src and "KS K 0021:2024" in src)
    check("출처에 개정 판본", "2024-12-31" in src and "2024-0699" in src)
    check("출처에 ISO 3758:2023", "ISO 3758:2023" in src)
    check("확인일 표기", CHECKED_ON in src)
    check("110℃ 오표기 없음", "110℃ 이하 다림질" not in src)
    check("출처 링크 새 창 보호", re.search(r'href="https://www\.standard\.go\.kr[^"]*"[^>]*rel="noopener noreferrer"', src) is not None)

    # 심긴 데이터와 JSON 일치
    embedded = json.loads(re.search(r'<script[^>]*id="washData"[^>]*>(.*?)</script>', src, re.S).group(1))
    check("HTML ↔ wash_data.json 기호 일치", embedded.get("symbols") == data.get("symbols"))
    check("HTML ↔ wash_data.json 퀴즈 일치", embedded.get("quizzes") == data.get("quizzes"))
    check("HTML ↔ wash_data.json 기준 일치", embedded.get("standard") == data.get("standard"))


def main():
    with open(WASH_JSON, encoding="utf-8") as handle:
        data = json.load(handle)
    src, embedded = load_html()
    check("JSON 빌드 시각", bool(data.get("generated")), data.get("generated"))
    check("HTML 데이터 블록 = JSON", embedded == data)

    print("== 기준 · 기호 ==")
    check_standard(data)
    check_symbols(data)
    print("== 라벨 읽기 퀴즈 ==")
    check_quizzes(data)
    print("== 표기 · 통합 ==")
    check_html(src, data)

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("\n세탁 라벨 읽기 검증 통과 (기호 %d개 · 옷 %d벌 · %d페이지 셸)"
          % (len(data["symbols"]), len(data["quizzes"]), SHEET_PAGES))


if __name__ == "__main__":
    main()

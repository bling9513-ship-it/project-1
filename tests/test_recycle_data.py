#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""재질 표시·분리배출(recycle.html) 데이터·구성 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · 마크 사전: 계열 4종에 표시 도안이 모두 있는지
    (무색페트·플라스틱·비닐류 / 종이·일반팩·멸균팩 / 캔류·유리 / 도포·첩합)
  · 플라스틱 표시재질이 PET·HDPE·LDPE·PP·PS·OTHER 이고, 2021년 개정으로 빠진 PVC 를
    표시재질로 다시 넣지 않았는지(대신 안내 문구로 설명하는지)
  · 무색페트(라벨 제거·압착·뚜껑 닫기), 종량제 예외(영수증 감열지·칫솔·깨진 유리),
    깨진 유리의 지자체별 차이(서울 소량 종량제·다량 특수규격마대 / 부평구 전용 PP마대),
    고철과 캔의 구분, 도포·첩합(재질 분리 불가 → 종량제) 설명이 들어 있는지
  · 모든 마크에 인라인 SVG(48×48 뷰박스) · 표시문자 · 이름 · 뜻 · 배출 원칙 · 주의
  · 퀴즈 7종: 품목·표시 조합·4지선다·정답 인덱스(0~3)·근거 마크(라벨 안)·해설,
    정답 인덱스가 한 곳에 몰리지 않았는지
  · 이모지 0 · 그라데이션 0 · 입력 필드 0 · 인라인 이벤트 핸들러 0
  · 공통 셸 21페이지 등록 · 하단 탭 바 · 출처(법령 2건·분리배출 누리집·공단 도안)·
    확인일(2026-11-22) · 지자체별 차이 안내 표기
  · recycle_data.json 과 recycle.html 에 심긴 데이터가 일치하는지

실행: python3 tests/test_recycle_data.py
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECYCLE_HTML = os.path.join(BASE_DIR, "recycle.html")
RECYCLE_JSON = os.path.join(BASE_DIR, "recycle_data.json")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 23
CHECKED_ON = "2026-11-22"
GROUPS = ("플라스틱·비닐", "종이·종이팩", "금속·유리", "복합")
REQUIRED_MARKS = (
    "pet-clear", "plastic", "vinyl",
    "paper", "soft-pack", "sterile-pack",
    "can", "glass", "composite",
)
ITEM_WORDS = ("페트병", "우유팩", "봉지", "영수증", "유리컵", "칫솔", "캔")

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_html():
    with open(RECYCLE_HTML, encoding="utf-8") as handle:
        src = handle.read()
    match = re.search(r'<script[^>]*id="recycleData"[^>]*>(.*?)</script>', src, re.S)
    if not match:
        raise SystemExit("recycle.html 에서 분리배출 데이터 블록을 찾지 못했습니다.")
    return src, json.loads(match.group(1))


def check_sources(data):
    check("확인일", data.get("checkedOn") == CHECKED_ON, data.get("checkedOn"))
    check("마크 계열 4종", tuple(data.get("groups") or ()) == GROUPS, data.get("groups"))
    sources = data.get("sources") or []
    check("출처 4건", len(sources) == 4, len(sources))
    urls = [item.get("url") or "" for item in sources]
    check("법령 원문 2건", sum(1 for url in urls if "law.go.kr" in url) == 2, urls)
    check("분리배출 누리집", any("wasteguide.or.kr" in url for url in urls), urls)
    check("한국환경공단 도안", any("budamgum.or.kr" in url for url in urls), urls)
    check("출처 https", all(url.startswith("https://") for url in urls), urls)
    check("출처 설명", all(len(item.get("detail") or "") >= 8 for item in sources),
          [item.get("detail") for item in sources])


def check_marks(data):
    marks = data.get("marks") or []
    by_id = {item.get("id"): item for item in marks}
    check("마크 9종 이상", len(marks) >= 9, len(marks))
    check("마크 ID 고유", len(by_id) == len(marks))
    check("필수 마크", all(sid in by_id for sid in REQUIRED_MARKS),
          [sid for sid in REQUIRED_MARKS if sid not in by_id])
    check("계열 값", {item.get("group") for item in marks} == set(GROUPS),
          sorted({item.get("group") for item in marks}))
    check("계열마다 마크", all(any(m.get("group") == g for m in marks) for g in GROUPS), GROUPS)

    for item in marks:
        mid = item.get("id")
        check("%s 이름" % mid, bool(item.get("name")), item.get("name"))
        check("%s 표시문자" % mid, len(item.get("inner") or "") <= 4, item.get("inner"))
        check("%s 한 줄 뜻" % mid, len(item.get("meaning") or "") >= 10, item.get("meaning"))
        check("%s 배출 원칙" % mid, len(item.get("rule") or "") >= 15, item.get("rule"))
        check("%s 주의" % mid, len(item.get("caution") or "") >= 15, item.get("caution"))
        svg = item.get("svg") or ""
        check("%s 인라인 SVG" % mid, svg.startswith("<svg") and 'viewBox="0 0 48 48"' in svg, svg[:40])
        check("%s 화살표 3개" % mid, svg.count('fill="currentColor" stroke="none"') >= 3, svg.count("<path"))
        check("%s 색" % mid, item.get("color") in
              {"yellow", "blue", "purple", "black", "green", "teal", "gray", "orange", "red"},
              item.get("color"))

    # 플라스틱 표시재질: PET·HDPE·LDPE·PP·PS·OTHER / PVC 는 2021년 개정으로 삭제
    plastic = by_id.get("plastic") or {}
    material = plastic.get("material") or ""
    for code in ("PET", "HDPE", "LDPE", "PP", "PS", "OTHER"):
        check("플라스틱 표시재질 %s" % code, code in material, material)
    check("플라스틱 표시재질에 PVC 없음", "PVC" not in material, material)
    check("PVC 삭제 안내", "PVC" in (plastic.get("caution") or "")
          or "PVC" in (plastic.get("meaning") or ""), plastic.get("caution"))

    # 무색페트: 라벨 제거 → 압착 → 뚜껑 닫기, 화장품 병 예외
    pet = by_id.get("pet-clear") or {}
    check("무색페트 대상", "먹는샘물" in (pet.get("meaning") or ""), pet.get("meaning"))
    check("무색페트 라벨 제거", "라벨" in (pet.get("rule") or ""), pet.get("rule"))
    check("무색페트 압착", "압착" in (pet.get("rule") or ""), pet.get("rule"))
    check("무색페트 뚜껑", "뚜껑" in (pet.get("rule") or ""), pet.get("rule"))
    check("무색페트 화장품 예외", "화장품" in (pet.get("caution") or ""), pet.get("caution"))

    # 캔류: 철·알루미늄, 고철 구분
    can = by_id.get("can") or {}
    check("캔류 표시재질 철", "철" in (can.get("material") or ""), can.get("material"))
    check("캔류 표시재질 알루미늄", "알루미늄" in (can.get("material") or ""), can.get("material"))
    check("캔류 고철 구분", "고철" in (can.get("caution") or ""), can.get("caution"))

    # 종이: 영수증 감열지·코팅 전단지 종량제 예외
    paper = by_id.get("paper") or {}
    check("종이 영수증 예외", "영수증" in (paper.get("caution") or ""), paper.get("caution"))
    check("종이 감열지", "감열지" in (paper.get("caution") or ""), paper.get("caution"))
    check("종이 종량제", "종량제" in (paper.get("caution") or ""), paper.get("caution"))

    # 유리: 깨진 유리 종량제 예외 · 지자체별 차이(서울 특수규격마대 / 부평구 PP마대)
    glass = by_id.get("glass") or {}
    check("유리 깨짐 예외", "깨진" in (glass.get("caution") or ""), glass.get("caution"))
    check("유리 수거함 제외", "유리병 수거함에서" in (glass.get("caution") or ""), glass.get("caution"))
    check("유리 종량제", "종량제" in (glass.get("caution") or ""), glass.get("caution"))
    check("유리 특수규격마대", "특수규격마대" in (glass.get("caution") or ""), glass.get("caution"))
    check("유리 지자체 안내", "지자체" in (glass.get("caution") or ""), glass.get("caution"))
    check("유리 전용 PP마대", "PP마대" in (glass.get("caution") or ""), glass.get("caution"))
    check("유리 대형폐기물", "대형폐기물" in (glass.get("caution") or ""), glass.get("caution"))
    check("유리 보증금 반납", "보증금" in (glass.get("rule") or ""), glass.get("rule"))

    # 종이팩: 일반팩(합성수지) / 멸균팩(알루미늄박)
    soft = by_id.get("soft-pack") or {}
    sterile = by_id.get("sterile-pack") or {}
    check("일반팩 우유", "우유" in (soft.get("meaning") or ""), soft.get("meaning"))
    check("일반팩 합성수지", "합성수지" in (soft.get("meaning") or ""), soft.get("meaning"))
    check("멸균팩 알루미늄", "알루미늄" in (sterile.get("meaning") or ""), sterile.get("meaning"))
    check("종이팩 전용수거함", "전용수거함" in (soft.get("rule") or ""), soft.get("rule"))

    # 비닐류: 필름 두께 기준
    vinyl = by_id.get("vinyl") or {}
    check("비닐류 두께 기준", "0.25mm" in (vinyl.get("caution") or ""), vinyl.get("caution"))
    check("비닐류 투명 봉투", "투명" in (vinyl.get("rule") or ""), vinyl.get("rule"))

    # 도포·첩합: 사선 표시 + 종량제
    comp = by_id.get("composite") or {}
    check("도포·첩합 사선", "M7 5.6L41 42.4" in (comp.get("svg") or ""), (comp.get("svg") or "")[-90:])
    check("도포·첩합 종량제", "종량제" in (comp.get("rule") or ""), comp.get("rule"))
    check("도포·첩합 10% 기준", "10%" in (comp.get("caution") or ""), comp.get("caution"))


def check_quizzes(data):
    quizzes = data.get("quizzes") or []
    by_id = {item.get("id"): item for item in data.get("marks") or []}
    check("퀴즈 6종 이상", len(quizzes) >= 6, len(quizzes))
    check("퀴즈 ID 고유", len({q.get("id") for q in quizzes}) == len(quizzes))
    items = " ".join(q.get("item") or "" for q in quizzes)
    for word in ITEM_WORDS:
        check("품목 %s" % word, word in items, items)

    for quiz in quizzes:
        qid = quiz.get("id")
        check("%s 부제" % qid, bool(quiz.get("meta")), quiz.get("meta"))
        check("%s 질문" % qid, "어떻게" in (quiz.get("question") or ""), quiz.get("question"))
        options = quiz.get("options") or []
        check("%s 보기 4개" % qid, len(options) == 4, len(options))
        check("%s 보기 중복 없음" % qid, len(set(options)) == len(options))
        check("%s 보기 길이" % qid, all(len(text) >= 12 for text in options), [len(t) for t in options])
        answer = quiz.get("answer")
        check("%s 정답 인덱스" % qid, isinstance(answer, int) and 0 <= answer < len(options), answer)
        symbols = quiz.get("symbols") or []
        check("%s 표시 1개 이상" % qid, len(symbols) >= 1, symbols)
        check("%s 표시 ID 고유" % qid, len({s.get("id") for s in symbols}) == len(symbols),
              [s.get("id") for s in symbols])
        for sym in symbols:
            check("%s 표시 마크 존재" % qid, sym.get("mark") in by_id, sym.get("mark"))
            check("%s 표시 문자" % qid, bool(sym.get("inner")), sym)
            check("%s 표시 위치" % qid, bool(sym.get("caption")), sym)
            check("%s 표시 SVG" % qid, "<svg" in (sym.get("svg") or ""), (sym.get("svg") or "")[:40])
        evidence = quiz.get("evidence") or []
        check("%s 근거 마크" % qid, bool(evidence) and set(evidence) <= {s.get("id") for s in symbols},
              evidence)
        check("%s 해설" % qid, len(quiz.get("explain") or "") >= 40, quiz.get("explain"))

    # 정답 인덱스가 한 자리에 몰리지 않았는지
    answers = [q.get("answer") for q in quizzes]
    check("정답 인덱스 분산", set(answers) == {0, 1, 2, 3}, answers)

    # 근거가 되는 사실이 보기에도 드러나는지
    milk = next((q for q in quizzes if q.get("id") == "milk-soy"), {})
    milk_answer = (milk.get("options") or [""])[milk.get("answer") or 0]
    check("우유팩·두유팩 정답", "전용수거함" in milk_answer, milk_answer)
    check("우유팩·두유팩 따로", "따로" in milk_answer, milk_answer)
    receipt = next((q for q in quizzes if q.get("id") == "receipt-flyer"), {})
    receipt_answer = (receipt.get("options") or [""])[receipt.get("answer") or 0]
    check("영수증 정답 종량제", "종량제" in receipt_answer, receipt_answer)
    brush = next((q for q in quizzes if q.get("id") == "toothbrush-tube"), {})
    brush_answer = (brush.get("options") or [""])[brush.get("answer") or 0]
    check("칫솔 정답 종량제", "칫솔은 종량제" in brush_answer, brush_answer)
    broken = next((q for q in quizzes if q.get("id") == "broken-glass"), {})
    broken_answer = (broken.get("options") or [""])[broken.get("answer") or 0]
    check("깨진 유리 정답 수거함 제외", "유리병 수거함에서" in broken_answer, broken_answer)
    check("깨진 유리 정답 지자체 안내", "지자체" in broken_answer, broken_answer)
    check("깨진 유리 정답 맥주병 반납", "보증금" in broken_answer, broken_answer)
    broken_explain = broken.get("explain") or ""
    check("깨진 유리 해설 서울 소량 종량제", "서울시" in broken_explain and "신문지" in broken_explain, broken_explain)
    check("깨진 유리 해설 부평구 PP마대", "부평구" in broken_explain and "PP마대" in broken_explain, broken_explain)
    check("깨진 유리 해설 다량 특수규격마대", "다량은 특수규격마대" in broken_explain, broken_explain)
    # 깨진 유리컵은 지자체에 따라 종량제로도 가므로, '깨진 유리컵은 종량제'만으로 정답이 되면 안 된다
    check("깨진 유리 보기 종량제 단정 없음",
          all(not ("깨진 유리컵은" in opt and "종량제" in opt and "맥주병" not in opt)
              for i, opt in enumerate(broken.get("options") or []) if i != (broken.get("answer") or 0)),
          broken.get("options"))
    can = next((q for q in quizzes if q.get("id") == "can-pot"), {})
    can_answer = (can.get("options") or [""])[can.get("answer") or 0]
    check("캔·냄비 정답 고철", "고철" in can_answer, can_answer)


def check_html(src, data):
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("입력 필드 없음", "<input" not in src.lower() and "<textarea" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+[\s\"']on[a-z]+\s*=", src, re.I))
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 recycle.html 등록", src.count('href="recycle.html"') >= 2, src.count('href="recycle.html"'))
    check("현재 페이지 표시", 'data-page="recycle"' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("데스크톱 드롭다운에 분리배출", "분리배출 읽기" in src)
    check("모바일 헤더 이름", 'class="ia-current"' in src and "분리배출" in src)

    check("재질 도감 탭", 'id="rcTabGuide"' in src and "재질 도감" in src)
    check("분리배출 퀴즈 탭", 'id="rcTabQuiz"' in src and "분리배출 퀴즈" in src)
    chips = re.findall(r'<button[^>]*class="rc-chip[ \"]', src)
    check("계열 칩 5개", len(chips) == 5, len(chips))
    rows = re.findall(r'class="rc-row" data-group="([^"]+)"', src)
    check("마크 줄 4개", len(rows) == 4, rows)
    check("마크 줄 계열", rows == list(GROUPS), rows)
    check("마크 버튼 %d개" % len(data["marks"]), src.count('class="rc-mark"') == len(data["marks"]),
          src.count('class="rc-mark"'))
    check("마크 버튼 aria-pressed", 'class="rc-mark" data-mark="pet-clear" aria-pressed="false"' in src)
    check("마크 버튼 aria-label", 'aria-label="무색페트 (무색 PET병)"' in src)
    check("설명 카드 즉시 노출", 'id="rcDesc"' in src and 'aria-live="polite"' in src and "무색페트" in src)
    check("배출 원칙·주의 표기", "배출" in src and "주의" in src and 'id="rcDescRule"' in src)
    check("마크와 배출 구분 카드", src.count('class="rc-split-card"') == 2, src.count('class="rc-split-card"'))
    check("지자체 조례 안내", "지자체" in src and "조례" in src)
    check("재질 문자 6개", src.count('class="rc-resin-chip"') == len(data["resins"]),
          src.count('class="rc-resin-chip"'))
    check("PVC 삭제 안내", "PVC는 2021년 개정" in src)
    check("퀴즈 진행 표시", 'id="rcQuizProgress"' in src and "1 / 7" in src)
    check("퀴즈 옵션 컨테이너", 'id="rcOptions"' in src)
    check("근거 마크 표시", "근거 마크" in src and "is-evidence" in src)
    check("감속 모션 대응", "prefers-reduced-motion" in src)
    check("다크 테마 변수", '[data-theme="dark"]' in src)
    check("출처 링크", "law.go.kr" in src and "wasteguide.or.kr" in src and "budamgum.or.kr" in src)
    check("출처에 기후에너지환경부", "기후에너지환경부" in src)
    check("출처에 지침 판본", "제2026-189호" in src and "제18호" in src)
    check("확인일 표기", CHECKED_ON in src)
    check("지자체별 차이 문구", "지자체별 수거 기준이 다를 수 있어요" in src)
    check("시행 예정 개정 안내", "2027-01-01" in src)
    check("출처 링크 새 창 보호",
          re.search(r'href="https://www\.law\.go\.kr[^"]*"[^>]*rel="noopener noreferrer"', src) is not None)

    embedded = json.loads(re.search(r'<script[^>]*id="recycleData"[^>]*>(.*?)</script>', src, re.S).group(1))
    check("HTML ↔ JSON 마크 일치", embedded.get("marks") == data.get("marks"))
    check("HTML ↔ JSON 퀴즈 일치", embedded.get("quizzes") == data.get("quizzes"))
    check("HTML ↔ JSON 출처 일치", embedded.get("sources") == data.get("sources"))
    check("HTML ↔ JSON 재질 문자 일치", embedded.get("resins") == data.get("resins"))


def main():
    with open(RECYCLE_JSON, encoding="utf-8") as handle:
        data = json.load(handle)
    src, embedded = load_html()
    check("JSON 빌드 시각", bool(data.get("generated")), data.get("generated"))
    check("HTML 데이터 블록 = JSON", embedded == data)

    print("== 출처 · 마크 ==")
    check_sources(data)
    check_marks(data)
    print("== 분리배출 퀴즈 ==")
    check_quizzes(data)
    print("== 표기 · 통합 ==")
    check_html(src, data)

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("\n재질 표시·분리배출 검증 통과 (마크 %d종 · 품목 %d개 · %d페이지 셸)"
          % (len(data["marks"]), len(data["quizzes"]), SHEET_PAGES))


if __name__ == "__main__":
    main()

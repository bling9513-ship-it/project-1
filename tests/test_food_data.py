#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""식품 라벨·영양성분표 읽기(food.html) 데이터·구성 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · 영양정보 9항목(열량·나트륨·탄수화물·당류·지방·트랜스지방·포화지방·콜레스테롤·단백질)과
    '총 내용량 300g(750kcal) · 100g당' 기준. 100g당 값 × 3 = 총 내용량 값이고,
    %는 1일 영양성분 기준치(나트륨 2,000mg · 탄수화물 324g · 당류 100g · 지방 54g ·
    포화지방 15g · 콜레스테롤 300mg · 단백질 55g)로 다시 계산해 맞춘다.
    트랜스지방만은 100g당 '0g'이 0.2g 미만 문턱 표시라서 totalText('표시값만으로 계산 불가')를
    쓰고 총 내용량 수치를 두지 않는다(3배 환산 대상에서 뺀다).
  · 열량은 4·4·9 계산(탄수화물 32g·단백질 8g·지방 10g → 250kcal)과 맞는지,
    열량·트랜스지방에는 % 기준치를 적지 않았는지, 트랜스지방은 0g(0.2g 미만) 표기인지.
  · 항목 13개(영양성분 8 · 소비기한·보관 2 · 원재료·알레르기 3)의 뜻·함정·확인 요령과
    근거 문구(1회 섭취참고량 3배, 소비기한 2023-01-01·유통기한, 냉장 0~10℃·개봉,
    원재료명 많이 사용한 순서·2% 미만, 알레르기 19개 항목·굴·전복·홍합·혼입 가능성,
    트랜스지방 100g 기준·0.2g/0.5g·총량 계산 불가).
  · 퀴즈 7문항: 앞부분 두 문제가 '100g당 → 봉지 전체 환산'과 '소비기한 옆 보관방법'인지,
    4지선다·정답 인덱스 분산·근거 라벨 구역(발췌 안)·해설. 트랜스지방 문항은 100g 기준과
    '한 봉지 전체가 0g은 아니다'를 고른다.
  · 이모지 0 · 그라데이션 0 · 입력 필드 0 · 인라인 이벤트 핸들러 0.
  · 공통 셸 26페이지 등록 · 하단 탭 바 · 100g당/총 내용량 전환 버튼 · 출처 6건(제2025-60호 +
    제2026-37호 전문 대조) · 확인일(2026-11-22).
  · food_data.json 과 food.html 에 심긴 데이터가 일치하는지.

실행: python3 tests/test_food_data.py
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOOD_HTML = os.path.join(BASE_DIR, "food.html")
FOOD_JSON = os.path.join(BASE_DIR, "food_data.json")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 31
CHECKED_ON = "2026-11-22"
CATEGORIES = ("전체", "영양성분", "소비기한·보관", "원재료·알레르기")
BASELINE = {"sodium": 2000, "carbs": 324, "sugar": 100, "fat": 54,
            "satfat": 15, "cholesterol": 300, "protein": 55}
REQUIRED_ITEMS = (
    "serving", "calorie", "sodium", "carbs", "sugar", "fat", "transfat",
    "cholesterol", "expiry", "storage", "type", "ingredients", "allergen",
)
NUTRIENT_NAMES = ("열량", "나트륨", "탄수화물", "당류", "지방",
                  "트랜스지방", "포화지방", "콜레스테롤", "단백질")

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_html():
    with open(FOOD_HTML, encoding="utf-8") as handle:
        src = handle.read()
    match = re.search(r'<script[^>]*id="foodData"[^>]*>(.*?)</script>', src, re.S)
    if not match:
        raise SystemExit("food.html 에서 식품 라벨 데이터 블록을 찾지 못했습니다.")
    return src, json.loads(match.group(1))


def number(text):
    match = re.match(r"^([\d.]+)", str(text).replace(",", ""))
    return float(match.group(1)) if match else None


def percent(text):
    match = re.match(r"^(\d+)%$", str(text))
    return int(match.group(1)) if match else None


def check_sources(data):
    check("확인일", data.get("checkedOn") == CHECKED_ON, data.get("checkedOn"))
    check("카테고리 4종", tuple(data.get("categories") or ()) == CATEGORIES, data.get("categories"))
    sources = data.get("sources") or []
    check("출처 6건", len(sources) == 6, len(sources))
    urls = [item.get("url") or "" for item in sources]
    check("출처 https", all(url.startswith("https://") for url in urls), urls)
    check("식약처 고시 출처", any("mfds.go.kr" in url for url in urls), urls)
    check("법령 별표 출처", any("law.go.kr" in url for url in urls), urls)
    check("식품안전나라 소비기한 출처", any("foodsafetykorea.go.kr" in url for url in urls), urls)
    check("소비기한 Q&A 출처", any("korea.kr" in url for url in urls), urls)
    check("출처 설명", all(len(item.get("detail") or "") >= 10 for item in sources),
          [item.get("detail") for item in sources])
    details = " ".join(item.get("detail") or "" for item in sources)
    check("출처에 고시 판본", "제2025-60호" in details, details[:80])
    check("출처에 1일 기준치", "2,000mg" in details and "324g" in details, details[:80])
    check("출처에 계도기간", "23.1.1" in details, details[:80])
    # 제2026-37호 전문(m_211 seq=14968)을 직접 대조한 출처가 실려야 한다.
    notice = next((item for item in sources if "제2026-37호" in (item.get("detail") or "")), None)
    check("제2026-37호 출처", notice is not None,
          [item.get("label") for item in sources])
    if notice:
        check("제2026-37호 출처 주소", "m_211" in (notice.get("url") or "")
              and "seq=14968" in (notice.get("url") or ""), notice.get("url"))
        detail = notice.get("detail") or ""
        check("제2026-37호 시행일", "2028-01-01" in detail, detail)
        check("제2026-37호 고시일", "2026-05-12" in detail, detail)
        check("제2026-37호 개정 범위", "영양성분" in detail and "개정 없음" in detail, detail)


def check_product(data):
    product = data.get("product") or {}
    check("제품 총 내용량", product.get("total") == "300g", product.get("total"))
    check("제품 총 열량", product.get("totalKcal") == "750kcal", product.get("totalKcal"))
    check("제품 식품유형", product.get("type") == "과자", product.get("type"))
    check("제품 1회 섭취참고량", product.get("serving") == "30g", product.get("serving"))
    check("제품 소비기한", "2026.12.15" in (product.get("expiry") or ""), product.get("expiry"))
    check("제품 보관방법 냉장", "냉장보관(0~10℃)" in (product.get("storage") or ""), product.get("storage"))
    check("제품 보관방법 개봉 후", "개봉 후 밀봉" in (product.get("storage") or ""), product.get("storage"))
    check("제품 원재료명", "밀가루(밀)" in (product.get("ingredients") or ""), product.get("ingredients"))
    check("제품 알레르기 3종", product.get("allergens") == ["우유", "대두", "밀"], product.get("allergens"))


def check_nutrients(data):
    nutrients = data.get("nutrients") or []
    check("영양성분 9행", len(nutrients) == 9, len(nutrients))
    check("영양성분 이름", tuple(item.get("name") for item in nutrients) == NUTRIENT_NAMES,
          [item.get("name") for item in nutrients])
    check("첫 행이 열량", nutrients[0].get("name") == "열량", nutrients[0].get("name"))

    for nutrient in nutrients:
        name = nutrient.get("name")
        per100 = number(nutrient.get("per100"))
        total = number(nutrient.get("total"))
        total_text = nutrient.get("totalText")
        check("%s 100g당 함량" % name, per100 is not None, nutrient.get("per100"))
        if per100 is None:
            continue
        if total_text:
            check("%s 총량 환산 불가" % name,
                  name == "트랜스지방" and total_text == "표시값만으로 계산 불가", (name, total_text))
            check("%s 총 내용량 수치 없음" % name, nutrient.get("total") is None, nutrient.get("total"))
        else:
            check("%s 총 내용량 함량" % name, total is not None, nutrient.get("total"))
            if total is None:
                continue
            check("%s 3배 환산" % name, abs(per100 * 3 - total) < 1e-6,
                  (nutrient.get("per100"), nutrient.get("total")))
        baseline = BASELINE.get(nutrient.get("key") or "")
        if baseline:
            pairs = [("pct100", per100)]
            if total is not None:
                pairs.append(("pctTotal", total))
            for field, value in pairs:
                expect = int((value / baseline * 100) + 0.5)
                check("%s %s 계산" % (name, field), percent(nutrient.get(field)) == expect,
                      (nutrient.get(field), expect))
        if name in ("열량", "트랜스지방"):
            check("%s %% 없음" % name,
                  percent(nutrient.get("pct100")) is None and percent(nutrient.get("pctTotal")) is None)
        if name == "트랜스지방":
            check("트랜스지방 100g당 0g", nutrient.get("per100") == "0g", nutrient.get("per100"))

    by_value = {item.get("name"): item for item in nutrients}
    check("열량 250kcal", by_value["열량"].get("per100") == "250kcal", by_value["열량"])
    check("열량 4·4·9", abs(4 * 32 + 4 * 8 + 9 * 10 - 250) < 1e-9)
    check("나트륨 450mg(23%)", by_value["나트륨"].get("per100") == "450mg"
          and by_value["나트륨"].get("pct100") == "23%", by_value["나트륨"])
    check("나트륨 총 1,350mg(68%)", by_value["나트륨"].get("total") == "1,350mg"
          and by_value["나트륨"].get("pctTotal") == "68%", by_value["나트륨"])
    check("탄수화물 32g(10%)", by_value["탄수화물"].get("per100") == "32g"
          and by_value["탄수화물"].get("pct100") == "10%", by_value["탄수화물"])
    check("당류 18g(18%)", by_value["당류"].get("per100") == "18g"
          and by_value["당류"].get("pct100") == "18%", by_value["당류"])
    check("지방 10g(19%)", by_value["지방"].get("per100") == "10g"
          and by_value["지방"].get("pct100") == "19%", by_value["지방"])
    check("포화지방 5g(33%)", by_value["포화지방"].get("per100") == "5g"
          and by_value["포화지방"].get("pct100") == "33%", by_value["포화지방"])
    check("포화지방 총 100%", by_value["포화지방"].get("pctTotal") == "100%", by_value["포화지방"])
    check("단백질 8g(15%)", by_value["단백질"].get("per100") == "8g"
          and by_value["단백질"].get("pct100") == "15%", by_value["단백질"])
    check("당류가 탄수화물보다 큰 %", percent(by_value["당류"].get("pct100"))
          > percent(by_value["탄수화물"].get("pct100")))
    check("총 내용량당 묶음", [(n.get("id"), n.get("key")) for n in nutrients].count(("fat", "fat")) == 1
          and [(n.get("id"), n.get("key")) for n in nutrients].count(("fat", "satfat")) == 1,
          [(n.get("id"), n.get("key")) for n in nutrients])


def check_items(data):
    items = data.get("items") or []
    by_id = {item.get("id"): item for item in items}
    check("항목 10개 이상", len(items) >= 10, len(items))
    check("항목 ID 고유", len(by_id) == len(items))
    check("필수 항목", all(i in by_id for i in REQUIRED_ITEMS),
          [i for i in REQUIRED_ITEMS if i not in by_id])
    check("카테고리 값", {item.get("cat") for item in items} == set(CATEGORIES[1:]),
          sorted({item.get("cat") for item in items}))
    check("카테고리마다 항목", all(any(i.get("cat") == c for i in items) for c in CATEGORIES[1:]))
    for item in items:
        iid = item.get("id")
        for field in ("short", "title", "value"):
            check("%s %s" % (iid, field), bool(item.get(field)), item.get(field))
        for field in ("meaning", "trap", "check"):
            check("%s %s 길이" % (iid, field), len(item.get(field) or "") >= 30,
                  len(item.get(field) or ""))

    serving = by_id["serving"]
    check("총 내용량·100g당 규칙", "1회 섭취참고량의 3배" in serving["meaning"], serving["meaning"][:60])
    check("총 내용량 1포장 원칙", "총 내용량(1포장)당" in serving["meaning"], serving["meaning"][:60])
    check("100g당 오해 함정", "100g당" in serving["trap"], serving["trap"][:40])

    calorie = by_id["calorie"]
    check("열량 % 없음 설명", "기준치" in calorie["meaning"] and "%" in calorie["meaning"], calorie["meaning"][:50])
    check("열량 4·4·9 설명", "9kcal" in calorie["trap"], calorie["trap"][:50])

    sodium = by_id["sodium"]
    check("나트륨 기준치 2,000mg", "2,000mg" in sodium["meaning"], sodium["meaning"][:60])
    check("나트륨 봉지 환산", "1,350mg" in sodium["meaning"], sodium["meaning"][:60])
    check("나트륨 0 표시 5mg", "5mg 미만" in sodium["meaning"], sodium["meaning"][:60])

    carbs = by_id["carbs"]
    check("탄수화물 324g", "324g" in carbs["meaning"], carbs["meaning"][:60])
    check("탄수화물·당류 구분", "당류" in carbs["meaning"], carbs["meaning"][:60])

    sugar = by_id["sugar"]
    check("당류 100g", "100g" in sugar["meaning"], sugar["meaning"][:60])
    check("당류 정의", "단당류" in sugar["meaning"] and "이당류" in sugar["meaning"], sugar["meaning"][:60])

    fat = by_id["fat"]
    check("지방 54g·포화 15g", "54g" in fat["meaning"] and "15g" in fat["meaning"], fat["meaning"][:60])
    check("포화지방 0.5g 0표시", "0.5g" in fat["trap"], fat["trap"][:60])

    transfat = by_id["transfat"]
    check("트랜스지방 0.2g 기준", "0.2g" in transfat["meaning"], transfat["meaning"][:60])
    check("트랜스지방 0.5g 미만", "0.5g 미만" in transfat["meaning"], transfat["meaning"][:60])
    check("트랜스지방 식용유지 예외", "식용유지" in transfat["meaning"], transfat["meaning"][:60])
    check("경화유 확인", "경화유" in transfat["check"], transfat["check"][:60])
    # 100g 기준과 '표시값만으로 총량을 계산할 수 없다'는 주의가 설명에 있어야 한다.
    check("트랜스지방 100g 기준", "100g 기준" in transfat["meaning"], transfat["meaning"][:80])
    check("트랜스지방 1회 섭취참고량 기준", "1회 섭취참고량당" in transfat["meaning"],
          transfat["meaning"][:80])
    check("트랜스지방 총량 계산 불가", "표시값만으로는 총량을 계산할 수 없" in transfat["meaning"],
          transfat["meaning"][-90:])
    check("트랜스지방 3배 오해", "3배" in transfat["trap"] and "0.6g" in transfat["trap"],
          transfat["trap"][:90])
    check("트랜스지방 값 100g당 표기", "100g" in transfat["value"], transfat["value"])

    chol = by_id["cholesterol"]
    check("콜레스테롤 300mg", "300mg" in chol["meaning"], chol["meaning"][:60])
    check("단백질 55g", "55g" in chol["meaning"], chol["meaning"][:60])

    expiry = by_id["expiry"]
    check("소비기한 정의", "보관방법을 지킬 경우" in expiry["meaning"], expiry["meaning"][:60])
    check("유통기한 비교", "유통기한" in expiry["meaning"], expiry["meaning"][:60])
    check("소비기한 2023-01-01", "2023-01-01" in expiry["meaning"], expiry["meaning"][:60])
    check("유통기한 60~70%", "60~70" in expiry["meaning"], expiry["meaning"][:60])
    check("우유류 2031-01-01", "2031-01-01" in expiry["trap"], expiry["trap"][:60])

    storage = by_id["storage"]
    check("보관방법 온도", "0~10℃" in storage["meaning"], storage["meaning"][:60])
    check("냉동 -18℃", "-18℃" in storage["meaning"], storage["meaning"][:60])
    check("개봉 후 안내", "개봉" in storage["trap"], storage["trap"][:60])
    check("보관방법 의무 근거", "보관방법을 적어야" in storage["meaning"], storage["meaning"][:60])

    food_type = by_id["type"]
    check("식품유형 정의", "분류 단위" in food_type["meaning"], food_type["meaning"][:60])
    check("식품유형 표시면", "정보표시면" in food_type["trap"], food_type["trap"][:60])

    ingredients = by_id["ingredients"]
    check("원재료명 순서", "많이 사용한 순서" in ingredients["meaning"], ingredients["meaning"][:60])
    check("원재료명 2% 예외", "2%" in ingredients["meaning"], ingredients["meaning"][:60])
    check("복합원재료 표시", "복합원재료" in ingredients["meaning"], ingredients["meaning"][:60])

    allergen = by_id["allergen"]
    check("알레르기 별도 표시란", "별도" in allergen["meaning"] and "표시란" in allergen["meaning"],
          allergen["meaning"][:60])
    check("알레르기 함유량 무관", "함유량과 관계없이" in allergen["meaning"], allergen["meaning"][:60])
    check("알레르기 19개 항목", "19개" in allergen["meaning"], allergen["meaning"][:60])
    check("알레르기 22종", "22종" in allergen["meaning"], allergen["meaning"][:60])
    check("조개류 굴·전복·홍합", "굴·전복·홍합" in allergen["meaning"], allergen["meaning"][:60])
    check("혼입 가능성 구분", "혼입 가능성" in allergen["trap"], allergen["trap"][:60])
    check("아몬드 대상 아님", "아몬드" in allergen["trap"], allergen["trap"][:60])


def check_quizzes(data):
    quizzes = data.get("quizzes") or []
    ids = [item.get("id") for item in data.get("items") or []]
    check("퀴즈 6문항 이상", len(quizzes) >= 6, len(quizzes))
    check("퀴즈 ID 고유", len({q.get("id") for q in quizzes}) == len(quizzes))
    check("첫 문제 100g당 환산", quizzes[0].get("id") == "bag-300g", quizzes[0].get("id"))
    check("둘째 문제 보관방법", quizzes[1].get("id") == "cold-storage", quizzes[1].get("id"))

    for quiz in quizzes:
        qid = quiz.get("id")
        check("%s 부제" % qid, bool(quiz.get("meta")), quiz.get("meta"))
        options = quiz.get("options") or []
        check("%s 보기 4개" % qid, len(options) == 4, len(options))
        check("%s 보기 중복 없음" % qid, len(set(options)) == len(options))
        check("%s 보기 길이" % qid, all(len(text) >= 12 for text in options), [len(t) for t in options])
        answer = quiz.get("answer")
        check("%s 정답 인덱스" % qid, isinstance(answer, int) and 0 <= answer < 4, answer)
        excerpt = quiz.get("excerpt") or []
        check("%s 라벨 발췌" % qid, 1 <= len(excerpt) <= 4, len(excerpt))
        zones = {line.get("zone") for line in excerpt}
        check("%s 발췌 구역" % qid, zones <= set(ids), zones)
        for line in excerpt:
            check("%s 발췌 줄" % qid, bool(line.get("key")) and bool(line.get("val")), line)
        evidence = quiz.get("evidence") or []
        check("%s 근거 구역" % qid, bool(evidence) and set(evidence) <= zones, (evidence, zones))
        check("%s 해설" % qid, len(quiz.get("explain") or "") >= 60, len(quiz.get("explain") or ""))

    answers = [q.get("answer") for q in quizzes]
    check("정답 인덱스 분산", set(answers) == {0, 1, 2, 3}, answers)

    bag = quizzes[0]
    bag_answer = bag["options"][bag["answer"]]
    check("환산 정답 750kcal", "750kcal" in bag_answer, bag_answer)
    check("환산 정답 당류 54g", "54g" in bag_answer, bag_answer)
    check("환산 근거 총 내용량", "serving" in bag["evidence"], bag["evidence"])
    check("환산 근거 당류", "sugar" in bag["evidence"], bag["evidence"])
    check("환산 해설 3배", "3배" in bag["explain"], bag["explain"][:40])
    for index, option in enumerate(bag["options"]):
        if index != bag["answer"]:
            check("환산 오답 %d 는 환산값 아님" % index, "750kcal" not in option or "54g" not in option, option)

    cold = quizzes[1]
    cold_answer = cold["options"][cold["answer"]]
    check("보관 정답 상온", "상온" in cold_answer, cold_answer)
    check("보관 정답 개봉", "개봉" in cold_answer, cold_answer)
    check("보관 정답 빨리", "빨리" in cold_answer, cold_answer)
    check("보관 근거", "storage" in cold["evidence"], cold["evidence"])
    check("보관 해설 보관방법", "보관방법" in cold["explain"], cold["explain"][:40])

    items_text = " ".join(q.get("item") or "" for q in quizzes)
    for word in ("300g", "냉장보관", "유통기한", "원재료명", "알레르기", "트랜스지방", "나트륨"):
        check("퀴즈 소재 %s" % word, word in items_text, items_text)

    # 트랜스지방 문항: 100g 기준과 '한 봉지 전체가 0g은 아니다'를 고른다.
    tf = next((q for q in quizzes if q.get("id") == "trans-fat-zero"), None)
    check("트랜스지방 문항", tf is not None, [q.get("id") for q in quizzes])
    if tf:
        tf_answer = tf["options"][tf["answer"]]
        check("트랜스지방 정답 100g", "100g" in tf_answer, tf_answer)
        check("트랜스지방 정답 0.2g", "0.2g 미만" in tf_answer, tf_answer)
        check("트랜스지방 정답 봉지 전체 아님", "한 봉지 전체가 0g" in tf_answer, tf_answer)
        check("트랜스지방 발췌 100g당", any(line.get("val") == "100g당" for line in tf["excerpt"]),
              [line.get("val") for line in tf["excerpt"]])
        check("트랜스지방 해설 100g 기준", "100g 기준" in tf["explain"], tf["explain"][:60])
        check("트랜스지방 해설 계산 불가", "계산할 수 없" in tf["explain"], tf["explain"][-80:])


def check_html(src, data):
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("입력 필드 없음", "<input" not in src.lower() and "<textarea" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+[\s\"']on[a-z]+\s*=", src, re.I))
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 food.html 등록", src.count('href="food.html"') >= 2, src.count('href="food.html"'))
    check("현재 페이지 표시", 'data-page="food"' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("데스크톱 드롭다운에 식품 라벨", "식품 라벨 읽기" in src)
    check("모바일 헤더 이름", 'class="ia-current"' in src and "식품 라벨" in src)

    check("라벨 도감 탭", 'id="fnTabGuide"' in src and "라벨 도감" in src)
    check("식품 라벨 퀴즈 탭", 'id="fnTabQuiz"' in src and "식품 라벨 퀴즈" in src)
    cats = re.findall(r'<button[^>]*class="fn-cat[ \"]', src)
    check("카테고리 칩 4개", len(cats) == 4, len(cats))
    for name in CATEGORIES:
        check("카테고리 %s" % name, 'data-cat="%s"' % name in src, name)
    check("영양성분 행 9개", src.count('class="fn-nrow') == 9, src.count('class="fn-nrow'))
    check("표시사항 5개", src.count('<button type="button" class="fn-field') == 5,
          src.count('<button type="button" class="fn-field'))
    check("라벨 구역 15개", len(re.findall(r'id="fnPack"[\s\S]*?</div>\s*</div>', src)) > 0)
    zones = re.findall(r'data-zone="([a-z]+)" data-item="[a-z]+"', src)
    check("라벨 구역 수", len(zones) == 15, len(zones))
    check("100g당 버튼", 'id="fnBasis100"' in src and 'data-basis="100"' in src)
    check("총 내용량 버튼", 'id="fnBasisTotal"' in src and 'data-basis="total"' in src)
    check("기준 머리글", 'id="fnColBasis"' in src)
    # 트랜스지방은 총 내용량 보기로 전환하면 0g 대신 '표시값만으로 계산 불가'가 나와야 한다.
    check("트랜스지방 총량 계산 불가 표기", 'data-vtotal="표시값만으로 계산 불가"' in src)
    tf_row = re.search(r'data-item="transfat"[^>]*>.*?</button>', src, re.S)
    check("트랜스지방 행 존재", tf_row is not None)
    if tf_row:
        check("트랜스지방 행 100g당 0g", 'data-v100="0g"' in tf_row.group(0), tf_row.group(0)[:120])
        check("트랜스지방 행 총량 0g 아님", 'data-vtotal="0g"' not in tf_row.group(0), tf_row.group(0)[:120])
        check("트랜스지방 행 계산 불가 문구", "표시값만으로 계산 불가" in tf_row.group(0),
              tf_row.group(0)[:120])
    check("총량 계산 불가 안내", "환산할 수 없어" in src)
    check("총 내용량 300g 표기", "300g" in src and "750kcal" in src)
    check("소비기한 표기", "2026.12.15까지" in src)
    check("보관방법 표기", "냉장보관(0~10℃)" in src)
    check("원재료명 표기", "밀가루(밀), 버터(우유)" in src)
    check("알레르기 표기", "우유, 대두, 밀 함유" in src)
    check("설명 카드 즉시 노출", 'id="fnDesc"' in src and 'aria-live="polite"' in src)
    check("뜻·함정·확인 표기", "뜻" in src and "함정" in src and "확인" in src)
    check("항목 이동 버튼", 'id="fnPrev"' in src and 'id="fnNext"' in src)
    check("1일 기준치 카드", "1일 영양성분 기준치" in src and "2,000mg" in src)
    check("퀴즈 진행 표시", 'id="fnQuizProgress"' in src and "1 / 7" in src)
    check("퀴즈 보기 컨테이너", 'id="fnOptions"' in src)
    check("근거 라벨 구역 표시", "근거 라벨 구역" in src and "is-evidence" in src)
    check("감속 모션 대응", "prefers-reduced-motion" in src)
    check("다크 테마 변수", '[data-theme="dark"]' in src)
    check("출처 링크", "mfds.go.kr" in src and "law.go.kr" in src and "foodsafetykorea.go.kr" in src)
    source_links = re.findall(r'<a href="https://[^"]+" target="_blank" rel="noopener noreferrer">', src)
    check("출처 링크 6건", len(source_links) >= 6, len(source_links))
    check("확인일 표기", CHECKED_ON in src and src.count(CHECKED_ON) >= 3, src.count(CHECKED_ON))
    check("소비기한 시행일 안내", "2023-01-01" in src)
    check("우유류 유예 안내", "2031-01-01" in src)
    check("고시 판본 안내", "제2025-60호" in src and "제2026-37호" in src)
    # 제2026-37호 대조 결과: 개정 네 가지·시행일 2028-01-01·영양성분 조항 개정 없음
    check("제2026-37호 시행일 안내", "2028-01-01" in src)
    check("제2026-37호 개정 내역", "탈카페인" in src and "말티톨" in src)
    check("제2026-37호 영양성분 개정 없음", "영양성분·트랜스지방 표시 조항은 바뀌지 않았" in src)
    check("별지 1 트랜스지방 조항 인용", "별지 1 1. 아. 2) 나) (4) (다)" in src, src.count("별지 1 1. 아."))
    check("알레르기 22종 안내", "22종" in src)
    check("예시 라벨 안내", "가상" in src and "예시" in src)
    check("출처 링크 새 창 보호",
          re.search(r'href="https://www\.mfds\.go\.kr[^"]*"[^>]*rel="noopener noreferrer"', src) is not None)

    embedded = json.loads(re.search(r'<script[^>]*id="foodData"[^>]*>(.*?)</script>', src, re.S).group(1))
    check("HTML ↔ JSON 항목 일치", embedded.get("items") == data.get("items"))
    check("HTML ↔ JSON 퀴즈 일치", embedded.get("quizzes") == data.get("quizzes"))
    check("HTML ↔ JSON 출처 일치", embedded.get("sources") == data.get("sources"))
    check("HTML ↔ JSON 영양성분 일치", embedded.get("nutrients") == data.get("nutrients"))
    check("HTML ↔ JSON 기준치 일치", embedded.get("baseline") == data.get("baseline"))


def main():
    with open(FOOD_JSON, encoding="utf-8") as handle:
        data = json.load(handle)
    src, embedded = load_html()
    check("JSON 빌드 시각", bool(data.get("generated")), data.get("generated"))
    check("HTML 데이터 블록 = JSON", embedded == data)

    print("== 출처 · 제품 ==")
    check_sources(data)
    check_product(data)
    print("== 영양정보 ==")
    check_nutrients(data)
    print("== 라벨 항목 ==")
    check_items(data)
    print("== 식품 라벨 퀴즈 ==")
    check_quizzes(data)
    print("== 표기 · 통합 ==")
    check_html(src, data)

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("\n식품 라벨·영양성분표 검증 통과 (항목 %d개 · 퀴즈 %d문항 · %d페이지 셸)"
          % (len(data["items"]), len(data["quizzes"]), SHEET_PAGES))


if __name__ == "__main__":
    main()

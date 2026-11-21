# -*- coding: utf-8 -*-
"""식품 라벨·영양성분표 읽기(food.html) — 한 장 생활 도식 빌더.

구성
  · 가상 식품 포장 라벨(HTML/CSS 도식): 영양정보 표 영역과 표시사항 영역을 한 장에 배치한다.
    - 영양정보: 총 내용량 300g(750kcal) · 100g당 250kcal · 나트륨 450mg(23%) · 탄수화물 32g(10%) ·
      당류 18g(18%) · 지방 10g(19%) · 트랜스지방 0g · 포화지방 5g(33%) · 콜레스테롤 15mg(5%) ·
      단백질 8g(15%). 「식품등의 표시기준」 별지 1 의 의무 표시 9항목을 모두 채웠다.
    - 표시사항: 소비기한 · 보관방법 · 식품유형 · 원재료명 · 알레르기 유발물질.
  · 라벨의 각 구역을 누르면(키보드 Tab + Enter 포함) 설명 카드에 뜻 · 실수하기 쉬운 함정 ·
    확인 요령이 즉시 열린다. 카테고리 칩(전체 | 영양성분 | 소비기한·보관 | 원재료·알레르기)으로
    항목을 좁힌다.
  · '100g당 ↔ 총 내용량 300g' 전환 버튼으로 같은 표의 수치가 3배로 뛰는 것을 한눈에 본다
    (입력 필드 없이 버튼 토글만 쓴다).
  · 식품 라벨 퀴즈 7문항: 100g당 수치의 포장 전체 환산, 소비기한 옆 보관방법, 소비기한과
    유통기한의 차이, 원재료명 표기 순서, 알레르기 표시 위치, 트랜스지방 0g 표기 기준,
    1일 영양성분 기준치(%) 해석. 답을 고르면 근거가 된 라벨 구역이 라벨 발췌에서 강조되고
    해설 · 최종 점수 · 다시 풀기가 나온다.
  · 이모지 0 · 그라데이션 0 · 입력 필드 0. 라벨은 실제 제품 포장이 아니라 표시기준에 맞춰
    만든 예시이며, 수치는 계산 예시다.
"""
import json
import math
import os
import re
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "food_data.json")
FOOD_HTML = os.path.join(BASE_DIR, "food.html")
KST = timezone(timedelta(hours=9))
CHECKED_ON = "2026-11-22"

SOURCES = [
    {
        "label": "식품의약품안전처 「식품등의 표시기준」",
        "detail": "식약처 고시 제2025-60호 · 2025-08-29 시행 · 별지 1 표시사항별 세부표시기준",
        "url": "https://www.mfds.go.kr/brd/m_207/view.do?seq=15093",
    },
    {
        "label": "「식품 등의 표시·광고에 관한 법률 시행규칙」 별표 5",
        "detail": "1일 영양성분 기준치 · 2022-11-28 개정 (나트륨 2,000mg · 탄수화물 324g · 당류 100g · 지방 54g · 포화지방 15g · 단백질 55g)",
        "url": "https://www.law.go.kr/LSW/flDownload.do?bylClsCd=110201&flSeq=147344939",
    },
    {
        "label": "식품안전나라 「소비기한 표시제를, 알아보아요」",
        "detail": "식약처 식품안전나라 · 소비기한 표시제 소비자 안내",
        "url": "https://www.foodsafetykorea.go.kr/portal/board/boardDetail.do?bbs_no=bbs001&menu_no=3120&ntctxt_no=1093173",
    },
    {
        "label": "식약처 「Q&A로 알아보는 소비기한 표시제」",
        "detail": "2023-01-30 · 계도기간('23.1.1~12.31) · 개봉 후 섭취 안내 · 냉장 보관 우유류 2031-01-01 적용",
        "url": "https://www.korea.kr/news/policyNewsView.do?newsId=148911057",
    },
    {
        "label": "식약처 카드뉴스 「2023년 달라지는 식의약 정책」",
        "detail": "냉장 0~10℃ · 냉동 -18℃ 이하 · 실온 1~35℃ 보관온도 안내",
        "url": "https://www.mfds.go.kr/brd/m_580/view.do?seq=81",
    },
]

CATEGORIES = ["전체", "영양성분", "소비기한·보관", "원재료·알레르기"]

# 1일 영양성분 기준치(별표 5) — % 검산에 쓴다.
BASELINE = {
    "sodium": 2000,
    "carbs": 324,
    "sugar": 100,
    "fat": 54,
    "satfat": 15,
    "cholesterol": 300,
    "protein": 55,
}

# 화면에 보여 줄 1일 영양성분 기준치(별표 5) — 검산용 BASELINE 과 같은 값이다.
BASELINE_ROWS = [
    ("sodium", "나트륨", "2,000mg"),
    ("carbs", "탄수화물", "324g"),
    ("sugar", "당류", "100g"),
    ("fat", "지방", "54g"),
    ("satfat", "포화지방", "15g"),
    ("cholesterol", "콜레스테롤", "300mg"),
    ("protein", "단백질", "55g"),
]

# 가상 제품 — 과자(1회 섭취참고량 30g → 3배 90g). 300g은 100g도, 90g도 넘어 100g당 표시가 가능하다.
PRODUCT = {
    "name": "버터크림 샌드위치 쿠키",
    "maker": "(주)가상제과 · 가상시 가상로 12",
    "type": "과자",
    "total": "300g",
    "totalKcal": "750kcal",
    "serving": "30g",
    "expiry": "2026.12.15까지",
    "storage": "냉장보관(0~10℃), 개봉 후 밀봉",
    "ingredients": "밀가루(밀), 버터(우유), 설탕, 대두유, 전분, 정제소금, 향료",
    "allergens": ["우유", "대두", "밀"],
}

# 열량은 4×32 + 4×8 + 9×10 = 250kcal 로 계산이 맞는다.
NUTRIENTS = [
    {"id": "calorie", "key": "calorie", "name": "열량", "per100": "250kcal", "total": "750kcal", "pct100": "–", "pctTotal": "–"},
    {"id": "sodium", "key": "sodium", "name": "나트륨", "per100": "450mg", "total": "1,350mg", "pct100": "23%", "pctTotal": "68%"},
    {"id": "carbs", "key": "carbs", "name": "탄수화물", "per100": "32g", "total": "96g", "pct100": "10%", "pctTotal": "30%"},
    {"id": "sugar", "key": "sugar", "name": "당류", "per100": "18g", "total": "54g", "pct100": "18%", "pctTotal": "54%", "sub": True},
    {"id": "fat", "key": "fat", "name": "지방", "per100": "10g", "total": "30g", "pct100": "19%", "pctTotal": "56%"},
    {"id": "transfat", "key": "transfat", "name": "트랜스지방", "per100": "0g", "total": "0g", "pct100": "–", "pctTotal": "–", "sub": True},
    {"id": "fat", "key": "satfat", "name": "포화지방", "per100": "5g", "total": "15g", "pct100": "33%", "pctTotal": "100%", "sub": True},
    {"id": "cholesterol", "key": "cholesterol", "name": "콜레스테롤", "per100": "15mg", "total": "45mg", "pct100": "5%", "pctTotal": "15%"},
    {"id": "cholesterol", "key": "protein", "name": "단백질", "per100": "8g", "total": "24g", "pct100": "15%", "pctTotal": "44%"},
]

# 영양성분 표 밖의 구역(총 내용량 줄 + 표시사항) — 항목 사전의 id 와 1:1 로 맞는다
EXTRA_ZONES = ["serving", "expiry", "storage", "type", "ingredients", "allergen"]

# 항목 사전 — id · 카테고리 · 짧은 이름 · 카드 제목 · 라벨에 적힌 값 · 뜻 · 함정 · 확인 요령
ITEMS = [
    {
        "id": "serving",
        "cat": "영양성분",
        "short": "총 내용량·100g당",
        "title": "총 내용량과 100g당, 무엇을 기준으로 적었나",
        "value": "총 내용량 300g (750kcal) · 100g당",
        "meaning": "영양성분은 원칙적으로 총 내용량(1포장)당 값으로 적어요. 다만 총 내용량이 100g을 넘고 "
                   "1회 섭취참고량의 3배를 넘는 제품은 100g당으로 적을 수 있어요. 이 라벨은 300g 과자"
                   "(1회 섭취참고량 30g, 3배는 90g)라서 100g당으로 적었고, 봉지 전체 열량 750kcal를 "
                   "내용량 옆 괄호에 함께 적었어요.",
        "trap": "표 머리에 적힌 '100g당'을 놓치고 250kcal를 한 봉지 열량으로 읽는 것이 가장 흔한 실수예요. "
                "한 봉지는 3배인 750kcal예요. 1회 섭취참고량(30g)도 내가 실제로 먹는 양이 아니라 표시를 "
                "계산하는 기준값이에요.",
        "check": "라벨 맨 윗줄의 '총 내용량 ○○g (○○kcal)'와 표 머리의 '100g당·1회 제공량당·총 내용량당' 중 "
                 "무엇인지 먼저 확인하고, 먹을 양이 몇 배인지 곱해 보세요.",
    },
    {
        "id": "calorie",
        "cat": "영양성분",
        "short": "열량",
        "title": "열량 250kcal, 옆에 %가 없는 이유",
        "value": "열량 250kcal (100g당)",
        "meaning": "열량은 킬로칼로리(kcal)로 적고, 5kcal 단위까지 반올림해도 돼요. 1일 영양성분 기준치가 "
                   "정해져 있지 않아 기준치 대비 비율(%)은 적지 않아요. 트랜스지방도 %를 적지 않는 항목이에요.",
        "trap": "열량 옆 % 칸이 비어 있는 것을 표시 누락으로 오해하기 쉬워요. 또 열량은 탄수화물 4kcal·"
                "단백질 4kcal·지방 9kcal로 계산하므로, 지방이 많은 제품은 양이 적어도 열량이 커요. "
                "5kcal 미만이면 '0'으로 적을 수 있어요.",
        "check": "kcal는 100g당인지 봉지 전체인지부터 보고, 2,000kcal를 하루 기준으로 잡아 비중을 가늠하세요. "
                 "%는 2,000kcal가 아니라 영양성분별 1일 기준치에 대한 비율이에요.",
    },
    {
        "id": "sodium",
        "cat": "영양성분",
        "short": "나트륨",
        "title": "나트륨 450mg (23%)",
        "value": "나트륨 450mg · 1일 기준치의 23%",
        "meaning": "1일 영양성분 기준치 나트륨 2,000mg의 23%예요. 100g당 450mg이므로 한 봉지 300g을 다 먹으면 "
                   "1,350mg, 기준치의 68%가 돼요. 나트륨은 120mg 이하는 5mg 단위, 120mg을 넘으면 10mg 단위로 "
                   "적고, 5mg 미만이면 '0'으로 적을 수 있어요.",
        "trap": "'23%'를 한 봉지 기준으로 읽으면 실제 섭취량의 3분의 1만 계산하게 돼요. 나트륨 '0mg' 표시도 "
                "5mg 미만이라는 뜻이라 완전 무첨가는 아니에요.",
        "check": "국물·소스·양념을 다 먹는지, 한 번에 몇 봉지인지로 다시 계산하세요. 하루 2,000mg을 넘기 "
                 "쉬운 제품은 국물형·가공육이 많아요.",
    },
    {
        "id": "carbs",
        "cat": "영양성분",
        "short": "탄수화물",
        "title": "탄수화물 32g (10%)과 그 아래 당류",
        "value": "탄수화물 32g · 1일 기준치의 10%",
        "meaning": "탄수화물은 당류를 포함한 값이에요. 그래서 탄수화물 아래에 당류를 한 줄 더 적어요. "
                   "기준치는 324g이고 32g은 그 10%예요. 1g 단위로 적고, 0.5g 미만이면 '0', 1g 미만이면 "
                   "'1g 미만'으로 적을 수 있어요.",
        "trap": "탄수화물이 많다고 당류도 많은 것은 아니고, 반대로 당류 %가 탄수화물 %보다 클 수 있어요. "
                "이 라벨도 탄수화물 10%인데 당류는 18%예요. 기준치가 324g과 100g으로 다르기 때문이에요.",
        "check": "탄수화물 총량과 그 안의 당류를 나눠 보고, 식이섬유가 함께 표시돼 있으면 그만큼 빼고 "
                 "생각하세요. 식이섬유는 의무 표시 항목이 아니에요.",
    },
    {
        "id": "sugar",
        "cat": "영양성분",
        "short": "당류",
        "title": "당류 18g (18%)",
        "value": "당류 18g · 1일 기준치의 18%",
        "meaning": "당류는 모든 단당류와 이당류를 더한 값이에요. 기준치 100g의 18%이고, 100g당 18g이므로 "
                   "한 봉지 300g이면 54g, 기준치의 54%가 돼요.",
        "trap": "당류는 '첨가당'만 세는 값이 아니라 제품에 들어 있는 단당류·이당류 전체예요. 과일 농축액이나 "
                "꿀처럼 이름이 다른 원료도 당류에 들어가요. 한 봉지를 다 먹으면 하루 기준의 절반을 넘어요.",
        "check": "음료는 100ml당으로 적는 경우가 많아 한 병(500ml 등)과 헷갈리기 쉬워요. 병 전체 용량을 "
                 "곱해 보고, 당류 0g은 0.5g 미만일 때 붙는 표시임을 기억하세요.",
    },
    {
        "id": "fat",
        "cat": "영양성분",
        "short": "지방·포화지방",
        "title": "지방 10g (19%)과 포화지방 5g (33%)",
        "value": "지방 10g(19%) · 포화지방 5g(33%)",
        "meaning": "지방 아래에 트랜스지방과 포화지방을 나눠 적어요. 지방 기준치는 54g, 포화지방은 15g이에요. "
                   "100g당 포화지방 5g은 기준치의 33%이고, 한 봉지 300g을 다 먹으면 15g으로 기준치의 100%가 돼요.",
        "trap": "지방 %만 보고 넘기면 포화지방 %를 놓쳐요. 포화지방은 기준치가 15g으로 작아서 조금만 먹어도 "
                "%가 크게 올라가요. 지방과 포화지방 모두 0.5g 미만이면 '0'으로 적을 수 있어요.",
        "check": "지방 총량 다음 줄의 포화지방·트랜스지방을 함께 보고, 한 봉지로 환산해 기준치의 몇 %인지 "
                 "확인하세요.",
    },
    {
        "id": "transfat",
        "cat": "영양성분",
        "short": "트랜스지방",
        "title": "트랜스지방 0g, 정말 하나도 없을까",
        "value": "트랜스지방 0g",
        "meaning": "트랜스지방은 0.5g 미만이면 '0.5g 미만', 0.2g 미만이면 '0'으로 적을 수 있어요. 식용유지류는 "
                   "100g당 2g 미만일 때 '0'으로 적을 수 있어요. 그래서 '0g'은 '아주 적어서 0으로 적었다'는 "
                   "뜻이지 무함유를 뜻하지 않아요.",
        "trap": "'0g'을 믿고 여러 봉지 먹으면 0.2g 미만씩 쌓여요. 그리고 트랜스지방은 % 기준치를 적지 않는 "
                "항목이라 옆 칸이 비어 있는 게 정상이에요.",
        "check": "'0g'과 '0.5g 미만'을 구분해 읽고, 부분경화유·경화유가 원재료명에 있는지 함께 확인하세요. "
                 "원재료명에 경화유가 있는데 트랜스지방 0g이면 표시 단위를 의심해 볼 수 있어요.",
    },
    {
        "id": "cholesterol",
        "cat": "영양성분",
        "short": "콜레스테롤·단백질",
        "title": "콜레스테롤 15mg (5%) · 단백질 8g (15%)",
        "value": "콜레스테롤 15mg(5%) · 단백질 8g(15%)",
        "meaning": "콜레스테롤 기준치는 300mg, 단백질은 55g이에요. 15mg은 5%, 8g은 15%로 반올림해 적어요. "
                   "콜레스테롤은 5mg 미만이면 '5mg 미만', 2mg 미만이면 '0'으로 적고, 단백질은 0.5g 미만이면 "
                   "'0'으로 적을 수 있어요.",
        "trap": "콜레스테롤 0mg이어도 포화지방·트랜스지방은 따로 봐야 해요. 단백질 %는 하루 기준 대비 비율일 "
                "뿐 '고단백'이라는 뜻이 아니고, 그 판단은 강조표시 기준을 따로 봐야 해요.",
        "check": "콜레스테롤·단백질은 지방 줄 다음에 이어지니, 같은 제품 두 개를 비교할 때는 100g당으로 "
                 "맞춰 놓고 보세요.",
    },
    {
        "id": "expiry",
        "cat": "소비기한·보관",
        "short": "소비기한",
        "title": "소비기한과 유통기한은 무엇이 다른가",
        "value": "소비기한 2026.12.15까지",
        "meaning": "소비기한은 '표시된 보관방법을 지킬 경우' 먹어도 안전에 이상이 없는 기한이에요. 유통기한은 "
                   "판매할 수 있는 기한(영업자 중심)이었어요. 2023-01-01부터 유통기한 대신 소비기한을 적고, "
                   "품질안전한계기간의 80~90%로 잡아 유통기한(60~70%)보다 길어요.",
        "trap": "소비기한이 지나도 '조금은 괜찮다'가 아니에요. 기한이 지난 제품은 먹지 않는 것이 기준이에요. "
                "반대로 소비기한이 남아 있어도 보관방법을 어기면 기한의 전제가 깨져요. 우유류(냉장 보관)는 "
                "2031-01-01부터 적용돼서 한동안 두 표시가 섞여 있어요.",
        "check": "'까지' 날짜와 바로 옆 보관방법을 한 묶음으로 읽으세요. 제조일로부터 ○○일로 적힌 제품은 "
                 "제조일을 함께 확인해야 해요.",
    },
    {
        "id": "storage",
        "cat": "소비기한·보관",
        "short": "보관방법",
        "title": "보관방법이 소비기한의 조건이다",
        "value": "보관방법 냉장보관(0~10℃), 개봉 후 밀봉",
        "meaning": "보관·취급에 특별한 조건이 필요한 제품은 소비기한과 함께 보관방법을 적어야 해요. 냉장은 "
                   "0~10℃, 냉동은 -18℃ 이하, 실온은 1~35℃가 기준이에요. 이 라벨은 냉장보관 제품이라 "
                   "소비기한 2026.12.15은 냉장고 안에서만 유효해요.",
        "trap": "소비기한만 보고 상온에 두면 기한의 전제가 깨져요. 개봉한 뒤에는 소비기한도 유통기한도 "
                "안전을 보장하지 않아요(식약처 안내). '개봉 후 밀봉'처럼 개봉 뒤 조건도 함께 지켜야 해요.",
        "check": "장보는 길·집에 오는 시간까지 포함해 온도를 지킬 수 있는지 보고, 개봉 후에는 냉장고에 "
                 "밀봉해 두고 가능한 한 빨리 먹으세요.",
    },
    {
        "id": "type",
        "cat": "원재료·알레르기",
        "short": "식품유형",
        "title": "식품유형 과자, 왜 필요한가",
        "value": "식품유형 과자",
        "meaning": "식품유형은 「식품의 기준 및 규격」의 가장 작은 분류 단위예요. 같은 쿠키라도 과자·빵류·"
                   "즉석식품류 중 무엇인지에 따라 적용되는 기준과 영양표시 의무가 달라져요. 과자류는 영양성분 "
                   "표시 대상이고 그중 추잉껌만 제외예요.",
        "trap": "제품명만 보고 유형을 짐작하면 안 돼요. 유형은 제품명이 아니라 정보표시면에 따로 적혀요. "
                "이름이 비슷한 '쿠키'라도 유형이 다르면 기준이 달라요.",
        "check": "유형을 확인하면 어떤 기준이 적용되는지, 영양표시 의무가 있는 제품인지가 보여요. "
                 "유형과 함께 영업소 명칭·소재지, 품목보고번호도 정보표시면에 있어요.",
    },
    {
        "id": "ingredients",
        "cat": "원재료·알레르기",
        "short": "원재료명",
        "title": "원재료명은 많이 쓴 순서, 단 예외가 있다",
        "value": "밀가루(밀), 버터(우유), 설탕, 대두유, 전분, 정제소금, 향료",
        "meaning": "원재료명은 모든 원재료를 많이 사용한 순서로 적어요. 다만 중량비율이 2% 미만인 나머지 "
                   "원재료는 그 뒤에 순서와 상관없이 적을 수 있어요. 복합원재료는 이름 뒤 괄호에 많이 쓴 "
                   "순서로 적어요. 여기서 '버터(우유)'의 괄호는 버터를 만든 원료가 우유라는 표시예요.",
        "trap": "첫 원재료가 가장 많다는 것만 맞고, 뒤로 갈수록 함량 순서가 아닐 수 있어요. 괄호 안 원료가 "
                "알레르기 표시를 대신하지도 않아요. 원재료명이 짧다고 성분이 적은 것도 아니고, 향료처럼 "
                "묶어 적는 항목도 있어요.",
        "check": "앞쪽 세 개로 단맛·짠맛의 무게를 가늠하고, 괄호 안 복합원재료까지 읽으세요. 알레르기가 "
                 "있다면 원재료명보다 알레르기 표시란을 먼저 보세요.",
    },
    {
        "id": "allergen",
        "cat": "원재료·알레르기",
        "short": "알레르기 표시",
        "title": "알레르기 유발물질은 따로 모아 적는다",
        "value": "알레르기 유발물질 우유, 대두, 밀 함유",
        "meaning": "알레르기 유발물질을 원재료로 썼으면 원재료명 표시란 근처에 바탕색과 구분되는 별도 "
                   "표시란을 만들고, 함유량과 관계없이 대상 물질을 모두 적어야 해요. 대상은 알류·우유·메밀·"
                   "땅콩·대두·밀·고등어·게·새우·돼지고기·복숭아·토마토·아황산류·호두·닭고기·쇠고기·오징어·"
                   "조개류(굴·전복·홍합)·잣 19개 항목이고, 조개류를 나눠 세면 22종이에요.",
        "trap": "'우유, 대두, 밀 함유'만 확인하고 끝내면 안 돼요. '○○ 혼입 가능성'은 원료로 넣은 것이 아니라 "
                "같은 설비에서 섞일 수 있다는 뜻이고, 아몬드처럼 대상이 아닌 견과류는 표시 의무가 없어요. "
                "복합원재료 안에 든 물질도 표시 대상이에요.",
        "check": "알레르기가 있으면 원재료명보다 표시란을 먼저 보고, 그다음 '혼입 가능성' 문구를 확인하세요. "
                 "표시란과 문구가 모두 없어도 교차접촉 가능성이 없다는 뜻은 아니에요.",
    },
]

ITEM_BY_ID = {item["id"]: item for item in ITEMS}


def _ex(key, val, zone):
    return {"key": key, "val": val, "zone": zone}


def _quiz(qid, item, meta, excerpt, options, answer, evidence, explain):
    return {
        "id": qid,
        "item": item,
        "meta": meta,
        "excerpt": excerpt,
        "options": options,
        "answer": answer,
        "evidence": evidence,
        "explain": explain,
    }


QUIZZES = [
    _quiz(
        "bag-300g", "300g 과자 한 봉지",
        "100g당 열량 250kcal · 당류 18g · 나트륨 450mg",
        [
            _ex("총 내용량", "300g (750kcal)", "serving"),
            _ex("표 머리", "100g당", "serving"),
            _ex("나트륨", "450mg (23%)", "sodium"),
            _ex("당류", "18g (18%)", "sugar"),
        ],
        [
            "열량 250kcal, 당류 18g — 라벨에 적힌 값을 그대로 먹게 된다.",
            "열량 750kcal, 당류 54g — 100g당 값의 3배다.",
            "열량 750kcal, 당류 18g — 열량만 3배가 된다.",
            "열량 500kcal, 당류 36g — 100g당 값의 2배다.",
        ],
        1, ["serving", "sugar"],
        "300g은 100g의 3배예요. 열량 750kcal, 당류 54g(기준치의 54%), 나트륨 1,350mg(68%), 포화지방 15g(100%)이 "
        "한 봉지 값이에요. 라벨에 적힌 수치가 100g당인지 봉지 전체인지 먼저 확인하는 습관이 핵심이에요.",
    ),
    _quiz(
        "cold-storage", "냉장보관 과자",
        "소비기한 2026.12.15까지 · 보관방법 냉장보관(0~10℃), 개봉 후 밀봉",
        [
            _ex("소비기한", "2026.12.15까지", "expiry"),
            _ex("보관방법", "냉장보관(0~10℃), 개봉 후 밀봉", "storage"),
        ],
        [
            "소비기한이 남았으니 상온에 둬도 괜찮다.",
            "한 번 개봉했어도 소비기한까지는 그대로 먹을 수 있다.",
            "소비기한은 보관방법을 지킬 때의 기한이므로, 상온에 두었거나 개봉했다면 빨리 먹거나 버린다.",
            "소비기한이 지나야 문제가 되니 냉장고에 다시 넣어 두면 된다.",
        ],
        2, ["storage", "expiry"],
        "소비기한은 '표시된 보관방법을 준수할 경우' 안전하게 먹을 수 있는 기한이에요. 냉장보관(0~10℃) 제품을 "
        "상온에 두면 기한의 전제가 깨지고, 개봉한 식품은 소비기한도 유통기한도 안전을 보장할 수 없어요"
        "(식약처 안내). 기한이 지난 제품은 먹지 않는 것이 기준이에요.",
    ),
    _quiz(
        "expiry-vs-sellby", "소비기한과 유통기한",
        "2023-01-01부터 유통기한 대신 소비기한",
        [
            _ex("소비기한", "2026.12.15까지", "expiry"),
            _ex("제도", "소비기한 표시제 2023-01-01 시행", "expiry"),
        ],
        [
            "유통기한은 소비자가 안전하게 먹을 수 있는 기한이고, 소비기한은 판매할 수 있는 기한이다.",
            "소비기한은 보관방법을 지킬 때 안전하게 먹을 수 있는 기한으로, 판매 허용 기한이던 유통기한보다 길게 잡는다.",
            "2023년 이후에도 유통기한과 소비기한을 나란히 함께 적는 것이 원칙이다.",
            "소비기한이 지난 제품도 며칠은 먹을 수 있으니 조금 지나도 괜찮다.",
        ],
        1, ["expiry"],
        "유통기한은 제조일부터 소비자에게 판매가 허용되는 기한(영업자 중심)이었고, 소비기한은 보관방법을 "
        "지킬 경우 안전하게 섭취할 수 있는 기한(소비자 중심)이에요. 품질안전한계기간의 60~70%였던 유통기한과 "
        "달리 소비기한은 80~90%로 잡아 더 길어요. 두 표시를 나란히 적는 것은 소비자 혼동 우려로 권장하지 "
        "않고, 기한이 지난 제품은 먹지 않아요.",
    ),
    _quiz(
        "ingredient-order", "원재료명 표기",
        "밀가루(밀), 버터(우유), 설탕, 대두유, 전분, 정제소금, 향료",
        [_ex("원재료명", "밀가루(밀), 버터(우유), 설탕, 대두유, 전분, 정제소금, 향료", "ingredients")],
        [
            "원재료명은 함량이 가장 많은 3개만 적으면 된다.",
            "원재료명은 가나다순으로 적는다.",
            "원재료명의 첫 번째는 언제나 물이다.",
            "모든 원재료를 많이 사용한 순서로 적되, 중량비율 2% 미만인 원재료는 뒤에 순서와 상관없이 적을 수 있다.",
        ],
        3, ["ingredients"],
        "원재료명은 모든 원재료를 많이 사용한 순서로 적고, 중량비율 2% 미만인 나머지 원재료는 그 뒤에 함량 "
        "순서와 상관없이 적을 수 있어요. 복합원재료는 이름 뒤 괄호에 많이 쓴 순서로 적어요. 그래서 앞쪽 "
        "원재료로 단맛·짠맛의 무게를 가늠하고, 뒤쪽은 참고로 읽는 것이 정확해요.",
    ),
    _quiz(
        "allergen-zone", "알레르기 유발물질 표시",
        "원재료명 근처 별도 표시란 · 우유, 대두, 밀 함유",
        [
            _ex("알레르기 유발물질", "우유, 대두, 밀 함유", "allergen"),
            _ex("원재료명", "밀가루(밀), 버터(우유), 설탕, 대두유, 전분, 정제소금, 향료", "ingredients"),
        ],
        [
            "알레르기 유발물질은 원재료명 안에 섞여 있으니 원재료명만 읽으면 된다.",
            "함유량이 아주 적으면 표시하지 않아도 된다.",
            "원재료명 근처 별도 표시란에 함유량과 관계없이 대상 물질을 모두 적어야 한다.",
            "'○○ 혼입 가능성'은 그 원료를 넣었다는 뜻이다.",
        ],
        2, ["allergen", "ingredients"],
        "알레르기 유발물질을 원재료로 썼으면 원재료명 표시란 근처에 바탕색과 구분되는 별도 표시란을 만들고, "
        "함유량과 관계없이 대상 물질을 모두 적어요. 반대로 '○○ 혼입 가능성'은 원료로 넣지 않았지만 같은 "
        "설비에서 섞일 수 있다는 안내예요. 알레르기가 있다면 표시란을 먼저 보고, 그다음 교차접촉 문구를 "
        "확인하세요.",
    ),
    _quiz(
        "trans-fat-zero", "트랜스지방 0g",
        "지방 10g(19%) · 포화지방 5g(33%) · 트랜스지방 0g",
        [
            _ex("지방", "10g (19%)", "fat"),
            _ex("포화지방", "5g (33%)", "fat"),
            _ex("트랜스지방", "0g", "transfat"),
        ],
        [
            "0g이므로 트랜스지방이 전혀 없다.",
            "0g이면 1일 영양성분 기준치의 0%라고 적어야 한다.",
            "0.2g 미만이면 0으로 적을 수 있어, 아주 적은 양은 들어 있을 수 있다.",
            "트랜스지방은 어떤 경우에도 0으로 적을 수 없다.",
        ],
        2, ["transfat", "fat"],
        "트랜스지방은 0.5g 미만이면 '0.5g 미만', 0.2g 미만이면 '0'으로 적을 수 있어요(식용유지류는 100g당 2g "
        "미만). 그래서 '0g'은 무함유가 아니라 표시 문턱 아래라는 뜻이고, 여러 봉지 먹으면 조금씩 쌓여요. "
        "트랜스지방은 % 기준치를 적지 않는 항목이라 옆 칸이 비어 있는 것이 정상이에요.",
    ),
    _quiz(
        "percent-basis", "나트륨 450mg (23%)",
        "표 머리 100g당 · 나트륨 450mg(23%)",
        [
            _ex("표 머리", "100g당", "serving"),
            _ex("나트륨", "450mg (23%)", "sodium"),
        ],
        [
            "1일 나트륨 기준치의 23%를 이 제품 100g이 채운다는 뜻이고, 한 봉지면 68%가 된다.",
            "나트륨 450mg 가운데 23%만 몸에 흡수된다는 뜻이다.",
            "열량 2,000kcal에 대한 나트륨 비율이다.",
            "한 봉지 전체를 기준으로 23%라는 뜻이다.",
        ],
        0, ["sodium", "serving"],
        "%는 각 영양성분의 1일 영양성분 기준치에 대한 비율이고, 표에 적힌 함량(100g당)을 기준으로 반올림해 "
        "정수로 적어요. 나트륨 기준치는 2,000mg이라 450mg은 23%이고, 한 봉지 300g이면 1,350mg으로 68%가 돼요. "
        "열량과 트랜스지방은 기준치가 없어 %를 적지 않아요.",
    ),
]


def _num(text):
    """'1,350mg' → 1350.0, '0g' → 0.0, '–' → None."""
    match = re.match(r"^([\d.]+)", str(text).replace(",", ""))
    return float(match.group(1)) if match else None


def _pct(text):
    match = re.match(r"^(\d+)%$", str(text))
    return int(match.group(1)) if match else None


def build_data(now=None):
    kst_now = now or datetime.now(KST)
    ids = [item["id"] for item in ITEMS]
    if len(ids) != len(set(ids)):
        raise ValueError("항목 ID 가 중복됩니다")
    if {item["cat"] for item in ITEMS} != set(CATEGORIES[1:]):
        raise ValueError("항목 카테고리가 CATEGORIES 와 어긋납니다")
    zone_ids = {nutrient["id"] for nutrient in NUTRIENTS} | set(EXTRA_ZONES)
    if zone_ids != set(ids):
        raise ValueError("라벨 구역과 항목이 1:1 로 맞지 않습니다: %s" % sorted(zone_ids ^ set(ids)))
    for item in ITEMS:
        for field in ("short", "title", "value", "meaning", "trap", "check"):
            if not item.get(field):
                raise ValueError("항목 %s 의 %s 가 비었습니다" % (item["id"], field))
        for field in ("meaning", "trap", "check"):
            if len(item[field]) < 30:
                raise ValueError("항목 %s 의 %s 가 너무 짧습니다" % (item["id"], field))

    # 영양성분 검산: 총 내용량 = 3 × 100g당, % = 함량 ÷ 기준치(반올림), 열량 = 4·4·9
    ratio = _num(PRODUCT["total"]) / 100.0
    if abs(ratio - 3.0) > 1e-9:
        raise ValueError("예시 제품의 100g당 대비 배율이 3배가 아닙니다")
    for nutrient in NUTRIENTS:
        per100, total = _num(nutrient["per100"]), _num(nutrient["total"])
        if per100 is None or total is None:
            raise ValueError("%s 함량을 읽지 못했습니다" % nutrient["name"])
        if abs(per100 * ratio - total) > 1e-6:
            raise ValueError("%s 총 내용량 값이 3배가 아닙니다: %s → %s"
                             % (nutrient["name"], nutrient["per100"], nutrient["total"]))
        baseline = BASELINE.get(nutrient.get("key") or nutrient["id"])
        if baseline:
            for value, label in ((per100, "pct100"), (total, "pctTotal")):
                expect = int(math.floor(value / baseline * 100 + 0.5))
                got = _pct(nutrient[label])
                if got is not None and got != expect:
                    raise ValueError("%s %s 가 %s%% 가 아니라 %s 입니다"
                                     % (nutrient["name"], label, expect, got))
        if nutrient.get("key") in ("calorie", "transfat"):
            if _pct(nutrient["pct100"]) is not None or _pct(nutrient["pctTotal"]) is not None:
                raise ValueError("%s 는 %% 기준치를 적지 않습니다" % nutrient["name"])
    kcal = 4 * 32 + 4 * 8 + 9 * 10
    if _num(NUTRIENTS[0]["per100"]) != kcal:
        raise ValueError("열량 계산(4·4·9)이 맞지 않습니다")

    quiz_ids = [quiz["id"] for quiz in QUIZZES]
    if len(quiz_ids) != len(set(quiz_ids)):
        raise ValueError("퀴즈 ID 가 중복됩니다")
    if len(QUIZZES) < 6:
        raise ValueError("퀴즈는 6문항 이상이어야 합니다")
    if quiz_ids[:2] != ["bag-300g", "cold-storage"]:
        raise ValueError("100g당 환산·보관방법 문제가 앞부분에 와야 합니다")
    for quiz in QUIZZES:
        if len(quiz["options"]) != 4:
            raise ValueError("%s 보기가 4개가 아닙니다" % quiz["id"])
        if len(set(quiz["options"])) != 4:
            raise ValueError("%s 보기가 중복됩니다" % quiz["id"])
        if not 0 <= quiz["answer"] < 4:
            raise ValueError("%s 정답 인덱스가 범위를 벗어났습니다" % quiz["id"])
        if not quiz["evidence"] or not set(quiz["evidence"]) <= set(ids):
            raise ValueError("%s 근거 항목이 항목 사전에 없습니다" % quiz["id"])
        if not quiz["excerpt"]:
            raise ValueError("%s 라벨 발췌가 없습니다" % quiz["id"])
        for line in quiz["excerpt"]:
            if line["zone"] not in set(ids):
                raise ValueError("%s 발췌 구역 %s 가 없습니다" % (quiz["id"], line["zone"]))
        if set(quiz["evidence"]) - {line["zone"] for line in quiz["excerpt"]}:
            raise ValueError("%s 근거 구역이 발췌에 없습니다" % quiz["id"])
        if len(quiz["explain"]) < 60:
            raise ValueError("%s 해설이 너무 짧습니다" % quiz["id"])

    return {
        "generated": kst_now.strftime("%Y-%m-%d %H:%M KST"),
        "checkedOn": CHECKED_ON,
        "sources": SOURCES,
        "categories": CATEGORIES,
        "product": PRODUCT,
        "nutrients": NUTRIENTS,
        "items": ITEMS,
        "quizzes": QUIZZES,
        "baseline": BASELINE,
    }


# ---------------------------------------------------------------------------
# HTML 조각
# ---------------------------------------------------------------------------
def _nutri_rows():
    parts = []
    for nutrient in NUTRIENTS:
        zone = nutrient["id"]
        cls = "fn-nrow" + (" is-sub" if nutrient.get("sub") else "")
        parts.append(
            '<button type="button" class="%s" data-zone="%s" data-item="%s" aria-pressed="false" '
            'aria-label="%s 설명 보기">'
            '<span class="fn-nname">%s</span>'
            '<span class="fn-nval" data-v100="%s" data-vtotal="%s">%s</span>'
            '<span class="fn-npct" data-p100="%s" data-ptotal="%s">%s</span>'
            '</button>'
            % (cls, zone, zone, nutrient["name"], nutrient["name"],
               nutrient["per100"], nutrient["total"], nutrient["per100"],
               nutrient["pct100"], nutrient["pctTotal"], nutrient["pct100"])
        )
    return "".join(parts)


def _field(key, value, zone, extra=""):
    return (
        '<button type="button" class="fn-field%s" data-zone="%s" data-item="%s" aria-pressed="false" '
        'aria-label="%s 설명 보기">'
        '<span class="fn-field-key">%s</span><span class="fn-field-val">%s</span></button>'
        % (extra, zone, zone, key, key, value)
    )


def _fields():
    product = PRODUCT
    return "".join([
        _field("소비기한", product["expiry"], "expiry"),
        _field("보관방법", product["storage"], "storage"),
        _field("식품유형", product["type"], "type"),
        _field("원재료명", product["ingredients"], "ingredients", " fn-field-block"),
        _field("알레르기 유발물질", ", ".join(product["allergens"]) + " 함유", "allergen", " fn-field-al"),
    ])


def _cat_chips():
    parts = []
    for index, name in enumerate(CATEGORIES):
        active = " is-active" if index == 0 else ""
        parts.append(
            '<button type="button" class="fn-cat%s" data-cat="%s" aria-pressed="%s">%s</button>'
            % (active, name, "true" if index == 0 else "false", name)
        )
    return "".join(parts)


def _baseline_rows():
    parts = []
    for key, name, value in BASELINE_ROWS:
        if str(BASELINE[key]) not in value.replace(",", ""):
            raise ValueError("기준치 표시가 BASELINE 과 어긋납니다: %s" % name)
        parts.append('<li><span>%s</span><b>%s</b></li>' % (name, value))
    return "".join(parts)


def _sources_html():
    parts = []
    for source in SOURCES:
        parts.append(
            '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a> (%s)'
            % (source["url"], source["label"], source["detail"])
        )
    return " · ".join(parts)


CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;

      --bg-page: #f8fafc;
      --bg-surface: #ffffff;
      --bg-subtle: #f1f5f9;
      --bg-muted: #e2e8f0;

      --border-subtle: #f1f5f9;
      --border-default: #e2e8f0;
      --border-strong: #cbd5e1;

      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;

      --accent-primary: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;

      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --paper: #fffdf7;
      --ink: #1f2937;
    }

    [data-theme="dark"] {
      --bg-page: #09090b;
      --bg-surface: #18181b;
      --bg-subtle: #27272a;
      --bg-muted: #3f3f46;

      --border-subtle: #1f1f23;
      --border-default: #27272a;
      --border-strong: #3f3f46;

      --text-primary: #f4f4f5;
      --text-secondary: #a1a1aa;
      --text-muted: #71717a;

      --accent-primary: #3b82f6;
      --accent-hover: #60a5fa;
      --accent-subtle: rgba(59, 130, 246, 0.15);

      --ok-bg: rgba(16, 185, 129, 0.12);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.32);
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --paper: #1c1c1f;
      --ink: #e4e4e7;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-page);
      color: var(--text-primary);
      line-height: 1.5;
      letter-spacing: -0.02em;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    a { color: inherit; }

    .navbar { position: sticky; top: 0; z-index: 50; background: var(--bg-surface); border-bottom: 1px solid var(--border-default); }
    .nav-container { max-width: 1360px; margin: 0 auto; padding: 0 20px; height: 60px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
    .brand-logo-img { width: 28px; height: 28px; border-radius: 7px; object-fit: cover; display: block; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15); flex-shrink: 0; }
    .brand-name { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; white-space: nowrap; }
    .update-meta { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); white-space: nowrap; }
    .live-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block; flex-shrink: 0; }
    .icon-btn { width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; cursor: pointer; text-decoration: none; }
    .icon-btn:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .fn-wrap { max-width: 980px; margin: 0 auto; padding: 14px 14px 88px; }

    .fn-hero h1 { font-size: 19.5px; font-weight: 800; letter-spacing: -0.045em; margin-top: 5px; }
    .fn-hero p { margin-top: 3px; font-size: 11.5px; color: var(--text-secondary); word-break: keep-all; }
    .fn-pill {
      display: inline-block; font-size: 10.5px; font-weight: 700;
      color: var(--accent-primary); background: var(--accent-subtle);
      border: 1px solid var(--border-default); border-radius: 6px; padding: 2px 7px;
    }
    .fn-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 3px 6px; margin-top: 4px; font-size: 10px; color: var(--text-muted); }
    .fn-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); }

    .fn-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 11px; margin: 9px 0 8px; }
    .fn-tab {
      border: 0; background: transparent; border-radius: 8px; padding: 7px 4px;
      font-family: inherit; font-size: 12.5px; font-weight: 600; color: var(--text-secondary);
      cursor: pointer; transition: background-color 160ms ease, color 160ms ease;
    }
    .fn-tab:hover { color: var(--text-primary); }
    .fn-tab.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }
    .fn-tab:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .fn-cats { display: flex; gap: 5px; overflow-x: auto; padding: 1px 0 7px; scrollbar-width: none; }
    .fn-cats::-webkit-scrollbar { display: none; }
    .fn-cat {
      flex: 0 0 auto; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 999px; padding: 4px 10px;
      font-family: inherit; font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap;
      transition: background-color 140ms ease, color 140ms ease, border-color 140ms ease;
    }
    .fn-cat:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .fn-cat.is-active { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }
    .fn-cat:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .fn-guide { display: grid; gap: 9px; align-items: start; }
    .fn-side { display: grid; gap: 9px; align-content: start; min-width: 0; }

    /* ----- 가상 포장 라벨 ----- */
    .fn-pack {
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 14px; padding: 9px 9px 10px; box-shadow: var(--card-shadow); min-width: 0;
    }
    .fn-pack-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; padding-bottom: 7px; border-bottom: 1px solid var(--border-subtle); }
    .fn-pack-title { font-size: 9.5px; font-weight: 700; letter-spacing: 0.08em; color: var(--text-secondary); }
    .fn-pack-note { font-size: 9px; color: var(--text-muted); white-space: nowrap; }
    .fn-pack-name { display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 6px; padding: 6px 1px 7px; }
    .fn-pack-name strong { font-size: 13px; font-weight: 800; letter-spacing: -0.035em; }
    .fn-pack-name span { font-size: 9px; color: var(--text-muted); }

    .fn-sheet {
      background: var(--paper); border: 1px solid var(--ink);
      border-radius: 4px; padding: 8px 8px 7px; color: var(--ink);
    }
    .fn-sheet-head { padding-bottom: 6px; border-bottom: 1.5px solid var(--ink); }
    .fn-nutri-title { font-size: 12.5px; font-weight: 800; letter-spacing: 0.02em; }
    .fn-nutri-total { display: flex; align-items: baseline; gap: 4px; flex-wrap: wrap; margin-top: 1px; font-size: 10px; font-weight: 600; }
    .fn-nutri-total b { font-weight: 800; }
    .fn-total {
      display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px; width: 100%;
      margin-top: 2px; padding: 2px 3px; border: 0; border-radius: 5px; background: transparent;
      color: var(--ink); font-family: inherit; font-size: 10px; font-weight: 600; text-align: left; cursor: pointer;
    }
    .fn-total b { font-weight: 800; }
    .fn-total:hover { background: rgba(37, 99, 235, 0.07); }
    .fn-total.is-active, .fn-total.is-evidence { background: var(--accent-subtle); box-shadow: inset 2px 0 0 var(--accent-primary); color: var(--accent-primary); }
    .fn-total.is-dim { opacity: 0.42; cursor: default; }
    .fn-total:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: -2px; }
    .fn-switch { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; margin-top: 6px; padding: 2px; background: rgba(15, 23, 42, 0.06); border-radius: 7px; }
    [data-theme="dark"] .fn-switch { background: rgba(255, 255, 255, 0.08); }
    .fn-switch-btn {
      border: 0; border-radius: 6px; background: transparent; padding: 4px 2px;
      font-family: inherit; font-size: 10px; font-weight: 700; color: var(--text-muted); cursor: pointer;
      white-space: nowrap; transition: background-color 140ms ease, color 140ms ease;
    }
    .fn-switch-btn.is-active { background: var(--bg-surface); color: var(--ink); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.12); }
    .fn-switch-btn:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .fn-nutri { display: grid; margin-top: 3px; }
    .fn-nhead { display: grid; grid-template-columns: minmax(0, 1fr) 64px 40px; gap: 2px; padding: 3px 5px; font-size: 8.5px; font-weight: 700; color: var(--text-muted); border-bottom: 1px solid rgba(15, 23, 42, 0.22); }
    .fn-nhead span:last-child, .fn-npct { text-align: right; }
    .fn-nrow {
      display: grid; grid-template-columns: minmax(0, 1fr) 64px 40px; gap: 2px;
      align-items: center; width: 100%; padding: 4px;
      border: 0; border-bottom: 1px dashed rgba(15, 23, 42, 0.16); border-radius: 0;
      background: transparent; color: var(--ink); font-family: inherit; font-size: 10.5px;
      text-align: left; cursor: pointer;
    }
    .fn-nrow:last-child { border-bottom: 0; }
    .fn-nrow:hover { background: rgba(37, 99, 235, 0.07); }
    .fn-nrow.is-sub .fn-nname { padding-left: 8px; color: var(--text-secondary); }
    .fn-nname { font-weight: 600; }
    .fn-nval { font-weight: 700; font-variant-numeric: tabular-nums; }
    .fn-npct { font-weight: 700; font-variant-numeric: tabular-nums; color: var(--text-secondary); }
    .fn-nrow.is-active, .fn-nrow.is-evidence {
      background: var(--accent-subtle); box-shadow: inset 2px 0 0 var(--accent-primary);
    }
    .fn-nrow.is-active .fn-nname, .fn-nrow.is-evidence .fn-nname,
    .fn-nrow.is-active .fn-npct, .fn-nrow.is-evidence .fn-npct { color: var(--accent-primary); }
    .fn-nrow.is-dim { opacity: 0.42; cursor: default; }
    .fn-nrow:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: -2px; }
    .fn-sheet-foot { margin-top: 5px; font-size: 9px; line-height: 1.45; color: var(--text-muted); }

    .fn-fields { display: grid; gap: 0; margin-top: 7px; padding-top: 5px; border-top: 1.5px solid var(--ink); }
    .fn-field {
      display: grid; grid-template-columns: 62px minmax(0, 1fr); gap: 5px; align-items: start;
      width: 100%; padding: 4px 3px; border: 0; border-bottom: 1px dashed rgba(15, 23, 42, 0.16); border-radius: 0;
      background: transparent; color: var(--ink); font-family: inherit;
      font-size: 10px; text-align: left; cursor: pointer;
    }
    .fn-field:last-child { border-bottom: 0; }
    .fn-field:hover { background: rgba(37, 99, 235, 0.07); }
    .fn-field-key { font-weight: 700; color: var(--text-secondary); }
    .fn-field-val { font-weight: 600; word-break: keep-all; }
    .fn-field-al { background: rgba(180, 83, 9, 0.09); outline: 1px solid rgba(180, 83, 9, 0.22); outline-offset: -1px; }
    .fn-field-al .fn-field-key { color: #b45309; }
    [data-theme="dark"] .fn-field-al { background: rgba(245, 158, 11, 0.14); outline-color: rgba(245, 158, 11, 0.34); }
    [data-theme="dark"] .fn-field-al .fn-field-key { color: #fcd34d; }
    .fn-field.is-active, .fn-field.is-evidence {
      border-color: var(--accent-primary); background: var(--accent-subtle);
      box-shadow: inset 2px 0 0 var(--accent-primary);
    }
    .fn-field.is-active .fn-field-key, .fn-field.is-evidence .fn-field-key { color: var(--accent-primary); }
    .fn-field.is-dim { opacity: 0.42; cursor: default; }
    .fn-field:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: -2px; }

    /* ----- 설명 카드 ----- */
    .fn-desc {
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 14px; padding: 10px 11px; box-shadow: var(--card-shadow); min-width: 0;
    }
    .fn-desc-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .fn-desc-cat { font-size: 9.5px; font-weight: 700; color: var(--accent-primary); }
    .fn-desc-count { font-size: 9.5px; font-weight: 600; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .fn-desc-count b { color: var(--text-secondary); }
    .fn-desc-title { margin-top: 2px; font-size: 14px; font-weight: 800; letter-spacing: -0.035em; word-break: keep-all; }
    .fn-desc-value { margin-top: 2px; font-size: 10.5px; font-weight: 600; color: var(--text-muted); word-break: keep-all; }
    .fn-rows { display: grid; gap: 5px; margin-top: 7px; }
    .fn-line { display: flex; align-items: flex-start; gap: 5px; font-size: 10.5px; line-height: 1.5; color: var(--text-secondary); word-break: keep-all; }
    .fn-tag { flex: 0 0 auto; font-size: 9px; font-weight: 700; border-radius: 4px; padding: 0 4px; line-height: 1.5; }
    .fn-tag-mean { color: var(--accent-primary); background: var(--accent-subtle); border: 1px solid var(--border-default); }
    .fn-tag-trap { color: #b45309; background: #fffbeb; border: 1px solid #fde68a; }
    .fn-tag-check { color: var(--ok-text); background: var(--ok-bg); border: 1px solid var(--ok-border); }
    [data-theme="dark"] .fn-tag-trap { color: #fcd34d; background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.32); }
    .fn-nav { display: flex; gap: 6px; margin-top: 8px; }
    .fn-ghost {
      flex: 1; min-height: 32px; padding: 0 8px; border-radius: 9px;
      border: 1px solid var(--border-default); background: var(--bg-page); color: var(--text-secondary);
      font-family: inherit; font-size: 11px; font-weight: 600; cursor: pointer;
    }
    .fn-ghost:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .fn-ghost:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .fn-note { margin-top: 8px; padding: 8px 10px; border-radius: 10px; background: var(--bg-subtle); font-size: 10px; line-height: 1.55; color: var(--text-secondary); word-break: keep-all; }

    /* ----- 1일 영양성분 기준치 ----- */
    .fn-base { padding: 10px 11px; border: 1px solid var(--border-default); border-radius: 12px; background: var(--bg-surface); box-shadow: var(--card-shadow); }
    .fn-base-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
    .fn-base-head h2 { font-size: 12px; font-weight: 800; letter-spacing: -0.03em; }
    .fn-base-head span { font-size: 9.5px; color: var(--text-muted); white-space: nowrap; }
    .fn-base-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2px 10px; margin-top: 6px; list-style: none; }
    .fn-base-list li { display: flex; align-items: baseline; justify-content: space-between; gap: 6px; padding: 2px 0; border-bottom: 1px dashed var(--border-default); font-size: 10px; }
    .fn-base-list span { color: var(--text-secondary); }
    .fn-base-list b { font-weight: 700; font-variant-numeric: tabular-nums; }
    .fn-base-note { margin-top: 6px; font-size: 9.5px; line-height: 1.5; color: var(--text-muted); word-break: keep-all; }
    .fn-paren { white-space: nowrap; }
    .fn-foot { margin-top: 9px; font-size: 9.5px; line-height: 1.6; color: var(--text-muted); word-break: keep-all; }
    .fn-foot a { color: var(--text-secondary); text-decoration: underline; text-underline-offset: 2px; }

    /* ----- 퀴즈 ----- */
    .fn-quiz-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 0 2px 7px; font-size: 11px; color: var(--text-muted); }
    .fn-quiz-head strong { color: var(--text-secondary); font-weight: 700; font-variant-numeric: tabular-nums; }
    .fn-q { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 14px; padding: 11px; box-shadow: var(--card-shadow); }
    .fn-q-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
    .fn-q-head h2 { font-size: 14.5px; font-weight: 800; letter-spacing: -0.04em; }
    .fn-q-head span { font-size: 9.5px; color: var(--text-muted); text-align: right; max-width: 54%; word-break: keep-all; }
    .fn-excerpt { display: grid; gap: 3px; margin-top: 7px; padding: 6px; background: var(--paper); border: 1px solid var(--ink); border-radius: 4px; }
    .fn-ex { display: grid; grid-template-columns: 62px minmax(0, 1fr); gap: 5px; padding: 3px 5px; border-radius: 4px; font-size: 10px; color: var(--ink); }
    .fn-ex-key { font-weight: 700; color: var(--text-secondary); }
    .fn-ex-val { font-weight: 600; word-break: keep-all; }
    .fn-ex.is-evidence { background: var(--accent-subtle); box-shadow: inset 2px 0 0 var(--accent-primary); }
    .fn-ex.is-evidence .fn-ex-key, .fn-ex.is-evidence .fn-ex-val { color: var(--accent-primary); }
    .fn-ghint { margin-top: 6px; font-size: 10px; line-height: 1.45; color: var(--text-muted); }
    .fn-question { margin: 9px 1px 7px; font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; word-break: keep-all; }
    .fn-quiz-grid { display: grid; gap: 9px; align-items: start; }
    .fn-qmain { min-width: 0; }
    .fn-options { display: grid; gap: 5px; }
    .fn-opt {
      display: flex; align-items: flex-start; gap: 8px; width: 100%; text-align: left;
      padding: 8px 9px; border: 1px solid var(--border-default); border-radius: 10px;
      background: var(--bg-surface); color: var(--text-primary); font-family: inherit;
      font-size: 11.5px; line-height: 1.45; letter-spacing: -0.02em; cursor: pointer;
      word-break: keep-all; transition: background-color 140ms ease, border-color 140ms ease;
    }
    .fn-opt:hover:not(:disabled) { background: var(--bg-subtle); }
    .fn-opt:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .fn-opt-num { flex: 0 0 auto; width: 17px; height: 17px; border-radius: 50%; background: var(--bg-subtle); color: var(--text-secondary); font-size: 9.5px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; }
    .fn-opt.is-correct { background: var(--ok-bg); border-color: var(--ok-border); color: var(--ok-text); }
    .fn-opt.is-correct .fn-opt-num { background: var(--ok-border); color: var(--ok-bg); }
    .fn-opt.is-wrong { background: var(--no-bg); border-color: var(--no-border); color: var(--no-text); }
    .fn-opt.is-wrong .fn-opt-num { background: var(--no-border); color: var(--no-bg); }
    .fn-opt.is-muted { opacity: 0.5; }
    .fn-opt:disabled { cursor: default; }

    .fn-result { margin-top: 8px; padding: 9px 10px; border-radius: 10px; border: 1px solid var(--ok-border); background: var(--ok-bg); }
    .fn-result.is-no { border-color: var(--no-border); background: var(--no-bg); }
    .fn-result h3 { font-size: 12px; font-weight: 800; color: var(--ok-text); }
    .fn-result.is-no h3 { color: var(--no-text); }
    .fn-result p { margin-top: 3px; font-size: 10.5px; line-height: 1.55; color: var(--text-secondary); word-break: keep-all; }
    .fn-result b { color: var(--text-primary); font-weight: 700; }
    .fn-ev { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin-top: 6px; }
    .fn-ev-tag { font-size: 9px; font-weight: 700; color: var(--text-muted); }
    .fn-ev-item { font-size: 9.5px; font-weight: 600; padding: 1px 6px; border-radius: 999px; border: 1px solid var(--accent-primary); color: var(--accent-primary); }

    .fn-actions { display: flex; gap: 6px; margin-top: 8px; }
    .fn-primary { flex: 1; min-height: 40px; border: 0; border-radius: 10px; background: var(--accent-primary); color: #ffffff; font-family: inherit; font-size: 12px; font-weight: 700; cursor: pointer; transition: background-color 140ms ease; }
    .fn-primary:hover:not(:disabled) { background: var(--accent-hover); }
    .fn-primary:disabled { background: var(--bg-muted); color: var(--text-muted); cursor: default; }
    .fn-primary:focus-visible { outline: 2px solid var(--accent-hover); outline-offset: 2px; }

    .fn-summary { margin-top: 8px; padding: 14px 12px; border: 1px solid var(--border-default); border-radius: 12px; background: var(--bg-surface); text-align: center; box-shadow: var(--card-shadow); }
    .fn-summary h2 { font-size: 14.5px; font-weight: 800; letter-spacing: -0.035em; }
    .fn-summary p { margin-top: 3px; font-size: 11px; color: var(--text-secondary); word-break: keep-all; }
    .fn-summary-score { font-size: 25px; font-weight: 800; letter-spacing: -0.04em; margin-top: 6px; font-variant-numeric: tabular-nums; }
    .fn-summary-score span { font-size: 12px; color: var(--text-muted); font-weight: 700; margin-left: 3px; }

    @media (min-width: 900px) {
      .fn-wrap { padding: 22px 22px 96px; }
      .fn-hero h1 { font-size: 23px; }
      .fn-hero p { font-size: 12.5px; }
      .fn-tabs { max-width: 360px; }
      .fn-guide { grid-template-columns: minmax(0, 1.02fr) minmax(0, 1fr); gap: 12px; align-content: start; }
      .fn-pack { padding: 12px 13px 13px; }
      .fn-side { gap: 12px; }
      .fn-sheet { padding: 12px 12px 10px; }
      .fn-nutri-title { font-size: 14px; }
      .fn-nutri-total { font-size: 11px; }
      .fn-nhead, .fn-nrow { grid-template-columns: minmax(0, 1fr) 78px 46px; }
      .fn-nrow { font-size: 11.5px; padding: 5px 5px; }
      .fn-field { font-size: 10.5px; grid-template-columns: 70px minmax(0, 1fr); }
      .fn-desc-title { font-size: 15.5px; }
      .fn-line { font-size: 11px; }
      .fn-quiz-grid { grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); gap: 13px; }
      .fn-question { margin-top: 0; }
    }

    @media (max-width: 430px) {
      .fn-wrap { padding: 12px 11px 84px; }
      .fn-hero h1 { font-size: 18px; }
      .fn-hero p { font-size: 11px; }
      .fn-pack { padding: 8px 8px 9px; }
      .fn-nhead, .fn-nrow { grid-template-columns: minmax(0, 1fr) 58px 36px; }
      .fn-nrow { font-size: 10px; padding: 3px; }
      .fn-field { grid-template-columns: 56px minmax(0, 1fr); font-size: 9.5px; }
      .fn-ex { grid-template-columns: 56px minmax(0, 1fr); font-size: 9.5px; }
      .fn-desc-title { font-size: 13.5px; }
      .fn-opt { font-size: 11px; padding: 7px 8px; }
      .fn-q-head h2 { font-size: 14px; }
    }

    @media (max-width: 340px) {
      .fn-nhead, .fn-nrow { grid-template-columns: minmax(0, 1fr) 52px 32px; }
      .fn-nrow { font-size: 9.5px; }
      .fn-field { grid-template-columns: 50px minmax(0, 1fr); font-size: 9px; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 식품 라벨·영양성분표 읽기</title>
  <meta name="description" content="가상 식품 포장 라벨을 눌러 영양성분표의 총 내용량과 100g당 기준, 소비기한과 보관방법, 원재료명·알레르기 표시를 한 장으로 익히는 생활 도식. 식약처 「식품등의 표시기준」(고시 제2025-60호)과 「식품 등의 표시·광고에 관한 법률 시행규칙」 별표 5 기준, 2026-11-22 확인.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" integrity="sha384-SN6A48CJQjx946+DRb8wsoifC4a8ur9ZS6R+HCTgnBHOKCa6GLXAR3Qn8d1jztxg" crossorigin="anonymous" />
  <style>__CSS__</style>
  <script>
    (function () {
      try {
        var saved = localStorage.getItem('secjobs-theme');
        if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.setAttribute('data-theme', 'dark');
        }
      } catch (e) {}
    })();
  </script>
</head>
<body>

  <!-- Global Nav -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
      </div>
      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>식품 표시기준 확인 2026-11-22</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="화면 테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        </button>
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기" aria-label="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <main class="fn-wrap">
    <section class="fn-hero">
      <span class="fn-pill">생활 도식 · 식품 라벨</span>
      <h1>식품 라벨, 한 장으로 읽기</h1>
      <p>포장 라벨의 구역을 누르면 뜻과 함정, 확인 요령이 열립니다. 100g당 수치를 봉지 전체로 바꿔 보고 마지막엔 라벨 퀴즈로 확인하세요.</p>
      <div class="fn-meta">
        <span>식약처 「식품등의 표시기준」</span>
        <span class="fn-sep"></span>
        <span>확인 2026-11-22</span>
      </div>
    </section>

    <div class="fn-tabs" role="tablist" aria-label="보기 전환">
      <button type="button" class="fn-tab is-active" id="fnTabGuide" role="tab" aria-selected="true" aria-controls="fnPanelGuide" data-tab="guide">라벨 도감</button>
      <button type="button" class="fn-tab" id="fnTabQuiz" role="tab" aria-selected="false" aria-controls="fnPanelQuiz" data-tab="quiz" tabindex="-1">식품 라벨 퀴즈</button>
    </div>

    <section id="fnPanelGuide" role="tabpanel" aria-labelledby="fnTabGuide">
      <div class="fn-cats" role="group" aria-label="항목 분류">
        __CAT_CHIPS__
      </div>

      <div class="fn-guide">
        <div class="fn-pack" id="fnPack" aria-label="가상 식품 포장 라벨">
          <div class="fn-pack-head">
            <span class="fn-pack-title">PRODUCT LABEL · 표시사항 예시</span>
            <span class="fn-pack-note">가상 라벨 · 눌러서 뜻 보기</span>
          </div>
          <div class="fn-pack-name">
            <strong>__PRODUCT_NAME__</strong>
            <span>__PRODUCT_MAKER__</span>
          </div>

          <div class="fn-sheet">
            <div class="fn-sheet-head">
              <div class="fn-nutri-title">영양정보</div>
              <button type="button" class="fn-total" data-zone="serving" data-item="serving" aria-pressed="false" aria-label="총 내용량 설명 보기">
                <span>총 내용량</span><b>__PRODUCT_TOTAL__</b><span class="fn-paren">(__PRODUCT_KCAL__)</span>
              </button>
              <div class="fn-switch" role="group" aria-label="표시 기준 바꾸기">
                <button type="button" class="fn-switch-btn is-active" id="fnBasis100" data-basis="100" aria-pressed="true">100g당</button>
                <button type="button" class="fn-switch-btn" id="fnBasisTotal" data-basis="total" aria-pressed="false">총 내용량 300g</button>
              </div>
            </div>
            <div class="fn-nutri" role="group" aria-label="영양성분 표">
              <div class="fn-nhead" aria-hidden="true">
                <span>영양성분</span><span id="fnColBasis">100g당</span><span>%기준치</span>
              </div>
              __NUTRI_ROWS__
            </div>
            <p class="fn-sheet-foot" id="fnBasisNote">한 봉지 300g은 100g의 3배예요. 버튼을 누르면 봉지 전체 값으로 바뀝니다.</p>

            <div class="fn-fields" id="fnFields">
              __FIELDS__
            </div>
          </div>
        </div>

        <div class="fn-side">
          <div class="fn-desc" id="fnDesc" aria-live="polite">
          <div class="fn-desc-head">
            <span class="fn-desc-cat" id="fnDescCat">__FIRST_CAT__</span>
            <span class="fn-desc-count"><b id="fnDescNum">1</b> / <span id="fnDescTotal">__ITEM_TOTAL__</span></span>
          </div>
          <h2 class="fn-desc-title" id="fnDescTitle">__FIRST_TITLE__</h2>
          <p class="fn-desc-value" id="fnDescValue">__FIRST_VALUE__</p>
          <div class="fn-rows">
            <p class="fn-line"><span class="fn-tag fn-tag-mean">뜻</span><span id="fnDescMean">__FIRST_MEAN__</span></p>
            <p class="fn-line"><span class="fn-tag fn-tag-trap">함정</span><span id="fnDescTrap">__FIRST_TRAP__</span></p>
            <p class="fn-line"><span class="fn-tag fn-tag-check">확인</span><span id="fnDescCheck">__FIRST_CHECK__</span></p>
          </div>
          <div class="fn-nav">
            <button type="button" class="fn-ghost" id="fnPrev">이전 항목</button>
            <button type="button" class="fn-ghost" id="fnNext">다음 항목</button>
          </div>
        </div>

        <section class="fn-base" aria-label="1일 영양성분 기준치">
          <div class="fn-base-head">
            <h2>1일 영양성분 기준치</h2>
            <span>하루 2,000kcal 기준</span>
          </div>
          <ul class="fn-base-list">
            __BASELINE__
          </ul>
          <p class="fn-base-note">표의 %는 이 기준치에 대한 비율이에요. 열량과 트랜스지방은 기준치가 없어 %를 적지 않고, 1일 영양성분 기준치는 내 하루 필요량과 다를 수 있어요.</p>
        </section>
        </div>
      </div>

      <p class="fn-foot">
        출처: __SOURCES__ · 확인일 2026-11-22.
        <br>이 라벨은 실제 제품 포장이 아니라 표시기준에 맞춰 만든 예시입니다. 수치는 계산 예시이며 특정 제품의 영양성분이 아닙니다.
        <br>소비기한 표시제는 2023-01-01 시행, 냉장 보관 우유류는 2031-01-01부터 적용됩니다. 표시기준은 고시 제2025-60호(2025-08-29 시행)를 따랐고, 제2026-37호(2026-05-12 발령)는 2028-01-01 시행 예정입니다.
        <br>알레르기 표시 대상은 19개 항목(조개류의 굴·전복·홍합을 따로 세면 22종)이고, 함유량과 관계없이 원재료로 쓴 모든 대상 물질을 적어야 합니다.
      </p>
    </section>

    <section id="fnPanelQuiz" role="tabpanel" aria-labelledby="fnTabQuiz" hidden>
      <div class="fn-quiz-head">
        <span id="fnQuizProgress">1 / 7</span>
        <span>정답 <strong id="fnQuizScore">0</strong></span>
      </div>
      <div id="fnQuizBody">
        <div class="fn-quiz-grid">
          <article class="fn-q">
            <div class="fn-q-head">
              <h2 id="fnItemName"></h2>
              <span id="fnItemMeta"></span>
            </div>
            <div class="fn-excerpt" id="fnQuizLabel" aria-label="이 문제의 라벨 발췌"></div>
            <p class="fn-ghint">라벨 발췌를 읽고 답을 골라 보세요. 답을 고르면 근거가 된 구역이 파랗게 표시됩니다.</p>
          </article>
          <div class="fn-qmain">
            <p class="fn-question" id="fnQuestion"></p>
            <div class="fn-options" id="fnOptions" role="group" aria-label="보기"></div>
            <div class="fn-result" id="fnResult" hidden></div>
            <div class="fn-actions">
              <button type="button" class="fn-primary" id="fnQuizNext" disabled>다음 문제</button>
            </div>
          </div>
        </div>
      </div>
      <div class="fn-summary" id="fnSummary" hidden>
        <h2>일곱 문제를 모두 봤어요</h2>
        <p>정답의 근거가 된 라벨 구역은 발췌에서 파랗게 표시됐어요. 라벨 도감에서 다시 확인해 보세요.</p>
        <div class="fn-summary-score"><b id="fnSummaryNum">0</b><span id="fnSummaryTotal">/ 7</span></div>
        <div class="fn-actions">
          <button type="button" class="fn-primary" id="fnRestart">다시 풀기</button>
          <button type="button" class="fn-ghost" id="fnBackGuide">라벨 도감으로</button>
        </div>
      </div>
    </section>
  </main>

  <script type="application/json" id="foodData">__DATA_JSON__</script>
  <script>
const FOOD = JSON.parse(document.getElementById('foodData').textContent);
__JS__
  </script>
</body>
</html>
"""

JS = r"""
(function () {
  // ---------- 화면 테마 (공통 셸 헤더의 토글) ----------
  const themeBtn = document.getElementById('themeToggle');
  const moonIcon = document.getElementById('moonIcon');
  const sunIcon = document.getElementById('sunIcon');
  function applyTheme(dark, persist) {
    if (dark) document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    if (moonIcon) moonIcon.style.display = dark ? 'none' : 'block';
    if (sunIcon) sunIcon.style.display = dark ? 'block' : 'none';
    if (persist) {
      try { localStorage.setItem('secjobs-theme', dark ? 'dark' : 'light'); } catch (e) {}
    }
  }
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      applyTheme(document.documentElement.getAttribute('data-theme') !== 'dark', true);
    });
  }
  (function initTheme() {
    let saved = null;
    try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
    applyTheme(saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches), false);
  })();

  const ITEMS = FOOD.items;
  const ITEM_MAP = {};
  ITEMS.forEach(function (item, index) { ITEM_MAP[item.id] = index; });
  const QUIZ = FOOD.quizzes;
  const TOTAL = QUIZ.length;
  const PRODUCT = FOOD.product;

  // ---------- 탭 ----------
  const tabs = Array.from(document.querySelectorAll('.fn-tab'));
  const panels = {
    guide: document.getElementById('fnPanelGuide'),
    quiz: document.getElementById('fnPanelQuiz'),
  };
  function selectTab(key, focus) {
    tabs.forEach(function (tab) {
      const on = tab.getAttribute('data-tab') === key;
      tab.classList.toggle('is-active', on);
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.setAttribute('tabindex', on ? '0' : '-1');
      if (on && focus) tab.focus();
    });
    Object.keys(panels).forEach(function (name) {
      panels[name].hidden = name !== key;
    });
  }
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () { selectTab(tab.getAttribute('data-tab')); });
    tab.addEventListener('keydown', function (event) {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      selectTab(tab.getAttribute('data-tab') === 'guide' ? 'quiz' : 'guide', true);
    });
  });

  // ---------- 100g당 / 총 내용량 전환 ----------
  const basisBtns = Array.from(document.querySelectorAll('.fn-switch-btn'));
  const colBasis = document.getElementById('fnColBasis');
  const basisNote = document.getElementById('fnBasisNote');
  function applyBasis(basis) {
    const isTotal = basis === 'total';
    Array.from(document.querySelectorAll('[data-v100]')).forEach(function (el) {
      el.textContent = isTotal ? el.getAttribute('data-vtotal') : el.getAttribute('data-v100');
    });
    Array.from(document.querySelectorAll('[data-p100]')).forEach(function (el) {
      el.textContent = isTotal ? el.getAttribute('data-ptotal') : el.getAttribute('data-p100');
    });
    basisBtns.forEach(function (btn) {
      const on = btn.getAttribute('data-basis') === basis;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if (colBasis) colBasis.textContent = isTotal ? '총 내용량당' : '100g당';
    if (basisNote) {
      basisNote.textContent = isTotal
        ? '한 봉지 ' + PRODUCT.total + '를 다 먹으면 이 값이에요. 100g당으로 되돌려 비교해 보세요.'
        : '한 봉지 ' + PRODUCT.total + '은 100g의 3배예요. 버튼을 누르면 봉지 전체 값으로 바뀝니다.';
    }
  }
  basisBtns.forEach(function (btn) {
    btn.addEventListener('click', function () { applyBasis(btn.getAttribute('data-basis')); });
  });

  // ---------- 라벨 도감 ----------
  const zones = Array.from(document.querySelectorAll('#fnPack [data-zone]'));
  const catChips = Array.from(document.querySelectorAll('.fn-cat'));
  const desc = {
    cat: document.getElementById('fnDescCat'),
    num: document.getElementById('fnDescNum'),
    total: document.getElementById('fnDescTotal'),
    title: document.getElementById('fnDescTitle'),
    value: document.getElementById('fnDescValue'),
    mean: document.getElementById('fnDescMean'),
    trap: document.getElementById('fnDescTrap'),
    check: document.getElementById('fnDescCheck'),
  };
  const prevBtn = document.getElementById('fnPrev');
  const nextBtn = document.getElementById('fnNext');
  let category = '전체';
  let current = 0;

  function visibleIndexes() {
    const list = [];
    ITEMS.forEach(function (item, index) {
      if (category === '전체' || item.cat === category) list.push(index);
    });
    return list;
  }

  function markZones(itemId) {
    zones.forEach(function (zone) {
      zone.classList.toggle('is-active', zone.getAttribute('data-zone') === itemId);
      zone.setAttribute('aria-pressed', zone.getAttribute('data-zone') === itemId ? 'true' : 'false');
    });
  }

  function showItem(index) {
    const item = ITEMS[index];
    if (!item) return;
    current = index;
    desc.cat.textContent = item.cat;
    desc.num.textContent = String(index + 1);
    desc.title.textContent = item.title;
    desc.value.textContent = item.value;
    desc.mean.textContent = item.meaning;
    desc.trap.textContent = item.trap;
    desc.check.textContent = item.check;
    markZones(item.id);
    const visible = visibleIndexes();
    const pos = visible.indexOf(index);
    prevBtn.disabled = pos <= 0;
    nextBtn.disabled = pos === -1 || pos >= visible.length - 1;
  }

  function applyCategory(name) {
    category = name;
    catChips.forEach(function (chip) {
      const on = chip.getAttribute('data-cat') === name;
      chip.classList.toggle('is-active', on);
      chip.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    zones.forEach(function (zone) {
      const item = ITEMS[ITEM_MAP[zone.getAttribute('data-zone')]];
      const show = name === '전체' || (item && item.cat === name);
      zone.classList.toggle('is-dim', !show);
      if (zone.tagName === 'BUTTON') zone.disabled = !show;
    });
    const visible = visibleIndexes();
    if (visible.length && visible.indexOf(current) === -1) showItem(visible[0]);
    else showItem(current);
  }

  zones.forEach(function (zone) {
    zone.addEventListener('click', function () {
      if (zone.disabled) return;
      const index = ITEM_MAP[zone.getAttribute('data-zone')];
      if (index !== undefined) showItem(index);
    });
  });
  catChips.forEach(function (chip) {
    chip.addEventListener('click', function () { applyCategory(chip.getAttribute('data-cat')); });
  });
  prevBtn.addEventListener('click', function () {
    const visible = visibleIndexes();
    const pos = visible.indexOf(current);
    if (pos > 0) showItem(visible[pos - 1]);
  });
  nextBtn.addEventListener('click', function () {
    const visible = visibleIndexes();
    const pos = visible.indexOf(current);
    if (pos >= 0 && pos < visible.length - 1) showItem(visible[pos + 1]);
  });

  // ---------- 식품 라벨 퀴즈 ----------
  const els = {
    progress: document.getElementById('fnQuizProgress'),
    score: document.getElementById('fnQuizScore'),
    body: document.getElementById('fnQuizBody'),
    name: document.getElementById('fnItemName'),
    meta: document.getElementById('fnItemMeta'),
    label: document.getElementById('fnQuizLabel'),
    question: document.getElementById('fnQuestion'),
    options: document.getElementById('fnOptions'),
    result: document.getElementById('fnResult'),
    next: document.getElementById('fnQuizNext'),
    summary: document.getElementById('fnSummary'),
    summaryNum: document.getElementById('fnSummaryNum'),
    summaryTotal: document.getElementById('fnSummaryTotal'),
    restart: document.getElementById('fnRestart'),
    back: document.getElementById('fnBackGuide'),
  };
  let index = 0;
  let answered = false;
  let correctCount = 0;

  function itemName(id) {
    const item = ITEMS[ITEM_MAP[id]];
    return item ? item.short : id;
  }

  function renderQuiz() {
    const quiz = QUIZ[index];
    answered = false;
    els.body.hidden = false;
    els.summary.hidden = true;
    els.progress.textContent = (index + 1) + ' / ' + TOTAL;
    els.score.textContent = String(correctCount);
    els.name.textContent = quiz.item;
    els.meta.textContent = quiz.meta;
    els.label.innerHTML = quiz.excerpt.map(function (line) {
      return '<span class="fn-ex" data-zone="' + line.zone + '">'
        + '<span class="fn-ex-key">' + line.key + '</span>'
        + '<span class="fn-ex-val">' + line.val + '</span></span>';
    }).join('');
    els.label.setAttribute('aria-label', quiz.item + ' 라벨 발췌: '
      + quiz.excerpt.map(function (line) { return line.key + ' ' + line.val; }).join(', '));
    els.question.textContent = quiz.question;
    els.options.innerHTML = quiz.options.map(function (text, idx) {
      return '<button type="button" class="fn-opt" data-idx="' + idx + '">'
        + '<span class="fn-opt-num">' + (idx + 1) + '</span>'
        + '<span class="fn-opt-text">' + text + '</span></button>';
    }).join('');
    els.result.hidden = true;
    els.result.className = 'fn-result';
    els.result.innerHTML = '';
    els.next.disabled = true;
    els.next.textContent = index === TOTAL - 1 ? '결과 보기' : '다음 문제';
  }

  function markEvidence(quiz) {
    Array.from(els.label.querySelectorAll('.fn-ex')).forEach(function (node) {
      node.classList.toggle('is-evidence', quiz.evidence.indexOf(node.getAttribute('data-zone')) >= 0);
    });
  }

  function showResult(quiz, ok) {
    els.result.className = 'fn-result' + (ok ? '' : ' is-no');
    els.result.innerHTML = ''
      + '<h3>' + (ok ? '정답이에요' : '라벨을 다시 보세요') + '</h3>'
      + '<p>' + quiz.explain + '</p>'
      + (ok ? '' : '<p>맞는 답: <b>' + quiz.options[quiz.answer] + '</b></p>')
      + '<div class="fn-ev"><span class="fn-ev-tag">근거 라벨 구역</span>'
      + quiz.evidence.map(function (id) {
        return '<span class="fn-ev-item">' + itemName(id) + '</span>';
      }).join('')
      + '</div>';
    els.result.hidden = false;
    markEvidence(quiz);
    els.next.disabled = false;
  }

  els.options.addEventListener('click', function (event) {
    const btn = event.target.closest('.fn-opt');
    if (!btn || answered) return;
    const quiz = QUIZ[index];
    const picked = Number(btn.getAttribute('data-idx'));
    const ok = picked === quiz.answer;
    answered = true;
    if (ok) correctCount += 1;
    els.score.textContent = String(correctCount);
    Array.from(els.options.querySelectorAll('.fn-opt')).forEach(function (node) {
      const idx = Number(node.getAttribute('data-idx'));
      node.disabled = true;
      if (idx === quiz.answer) node.classList.add('is-correct');
      else if (idx === picked) node.classList.add('is-wrong');
      else node.classList.add('is-muted');
    });
    showResult(quiz, ok);
  });

  els.next.addEventListener('click', function () {
    if (index === TOTAL - 1) {
      els.body.hidden = true;
      els.summary.hidden = false;
      els.summaryNum.textContent = String(correctCount);
      els.summaryTotal.textContent = '/ ' + TOTAL;
      els.progress.textContent = TOTAL + ' / ' + TOTAL;
      return;
    }
    index += 1;
    renderQuiz();
  });

  els.restart.addEventListener('click', function () {
    index = 0;
    correctCount = 0;
    renderQuiz();
  });

  els.back.addEventListener('click', function () {
    selectTab('guide', true);
  });

  // 초기 상태
  applyBasis('100');
  applyCategory('전체');
  showItem(0);
  renderQuiz();
  selectTab('guide');
})();
"""


def build():
    kst_now = datetime.now(KST)
    data = build_data(kst_now)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    first = ITEMS[0]

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__CAT_CHIPS__", _cat_chips())
            .replace("__NUTRI_ROWS__", _nutri_rows())
            .replace("__FIELDS__", _fields())
            .replace("__PRODUCT_NAME__", PRODUCT["name"])
            .replace("__PRODUCT_MAKER__", PRODUCT["maker"])
            .replace("__PRODUCT_TOTAL__", PRODUCT["total"])
            .replace("__PRODUCT_KCAL__", PRODUCT["totalKcal"])
            .replace("__ITEM_TOTAL__", str(len(ITEMS)))
            .replace("__FIRST_CAT__", first["cat"])
            .replace("__FIRST_TITLE__", first["title"])
            .replace("__FIRST_VALUE__", first["value"])
            .replace("__FIRST_MEAN__", first["meaning"])
            .replace("__FIRST_TRAP__", first["trap"])
            .replace("__FIRST_CHECK__", first["check"])
            .replace("__SOURCES__", _sources_html())
            .replace("__BASELINE__", _baseline_rows())
            .replace("__DATA_JSON__", payload)
            .replace("__JS__", JS))

    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(FOOD_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "food")))

    print("-> 'food_data.json' 저장 완료 (항목 %d개 · 퀴즈 %d문항)" % (len(ITEMS), len(QUIZZES)))
    print("-> 'food.html' 생성 완료 (확인일 %s)" % CHECKED_ON)
    return {
        "items": len(ITEMS),
        "quizzes": len(QUIZZES),
        "nutrients": len(NUTRIENTS),
        "checkedOn": CHECKED_ON,
    }


if __name__ == "__main__":
    build()

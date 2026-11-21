#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pick_html.py — '오늘 뭐 먹지' 날씨 맞춤 메뉴 룰렛 + 서울 나들이 코스(pick.html)를 빌드한다.

- 빌드 시점에 weather CLI(Apple Weather)로 서울 오늘/내일 기온·체감·강수·바람을 읽어 기본값으로 심는다.
- 브라우저에서는 Open-Meteo(무료·키 불필요)로 실시간 값을 받아 배너·추천 모드·추천 이유를 갱신한다.
- 룰렛 상태(즐겨찾기·최근 뽑은 기록)는 브라우저 localStorage('secjobs-pick-v1')에만 남는다.
- index.html / study.html / ai.html / cve.html / outfit.html 과 동일한 secjobs-theme 디자인 시스템(이모지 미사용, 라인 SVG만 사용).
"""
import os
import json
import subprocess
import urllib.request
from datetime import datetime, timezone, timedelta

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICK_HTML = os.path.join(BASE_DIR, "pick.html")
KST = timezone(timedelta(hours=9))
WEATHER_COORDS = "37.5665, 126.9780"

# ---------------------------------------------------------------- 메뉴 데이터
# (id, 이름, 카테고리, 예상 가격대, 한 줄 설명, 스타일, 상황, 동행, 날씨 궁합, 곁들임 추천)
STYLES = [
    ("all", "전체"),
    ("gukmul", "든든한 국물"),
    ("light", "깔끔·가벼움"),
    ("spicy", "매콤·스트레스 해소"),
    ("noodle", "면·분식"),
    ("western", "양식·아시안"),
]

SITUATIONS = [("all", "전체"), ("lunch", "점심"), ("dinner", "저녁·야식"), ("cafe", "카페·간식")]
COMPANIONS = [("all", "전체"), ("solo", "혼밥"), ("group", "여럿이")]

MENU_ROWS = [
    ("kimchi-jjigae", "김치찌개", "찌개·국물", "9,000~11,000원", "묵은지와 돼지고기를 푹 끓인 국물에 공깃밥", ["gukmul", "spicy"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "계란말이 한 접시"),
    ("doenjang-jjigae", "된장찌개", "찌개·국물", "8,500~10,000원", "구수한 된장에 두부·애호박·감자를 넣은 국물", ["gukmul", "light"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "공깃밥 한 공기 더"),
    ("sundae-gukbap", "순대국밥", "국밥", "10,000~12,000원", "진한 사골 육수에 순대와 머릿고기", ["gukmul"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "새우젓·깍두기"),
    ("dwaeji-gukbap", "돼지국밥", "국밥", "10,000~12,000원", "돼지 사골을 오래 끓여 낸 뽀얀 국물", ["gukmul"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "부추·다대기 듬뿍"),
    ("seolleongtang", "설렁탕", "국밥", "12,000~14,000원", "하얀 사골 국물에 수육과 소면", ["gukmul", "light"], ["lunch", "dinner"], ["solo", "group"], ["cold"], "소면 사리"),
    ("samgyetang", "삼계탕", "보양식", "16,000~19,000원", "닭 한 마리에 인삼·대추·찹쌀을 넣고 고아 낸 국물", ["gukmul"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "찹쌀죽 사리"),
    ("gamjatang", "감자탕", "국물·탕", "11,000~14,000원", "등뼈와 우거지가 진하게 우러난 매콤한 국물", ["gukmul", "spicy"], ["dinner"], ["group"], ["cold", "rain"], "볶음밥 마무리"),
    ("sundubu", "순두부찌개", "찌개·국물", "9,000~11,000원", "부드러운 순두부에 계란을 풀어 넣은 얼큰한 국물", ["gukmul", "spicy"], ["lunch", "dinner"], ["solo"], ["cold", "rain"], "계란 하나 추가"),
    ("galbitang", "갈비탕", "국물·탕", "13,000~16,000원", "소갈비를 오래 끓여 낸 맑은 국물", ["gukmul"], ["lunch", "dinner"], ["solo", "group"], ["cold"], "깍두기·당면 사리"),
    ("budae-jjigae", "부대찌개", "국물·탕", "10,000~13,000원", "햄·소시지·라면 사리를 넣고 끓인 얼큰한 전골", ["gukmul", "spicy"], ["dinner"], ["group"], ["cold", "rain"], "라면 사리 추가"),
    ("nakgopsae", "낙곱새", "국물·탕", "15,000~20,000원", "낙지·곱창·새우를 매콤한 국물에 끓인 전골", ["gukmul", "spicy"], ["dinner"], ["group"], ["cold", "rain"], "볶음밥 마무리"),
    ("kalguksu", "칼국수", "면·분식", "8,000~10,000원", "손칼국수에 바지락과 애호박을 넣은 국물", ["noodle", "gukmul"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "왕만두 한 판"),
    ("janchi-guksu", "잔치국수", "면·분식", "7,000~9,000원", "멸치 육수에 소면을 말아 낸 가벼운 한 그릇", ["noodle", "light"], ["lunch"], ["solo"], ["rain", "warm"], "김가루·고춧가루"),
    ("udon", "우동", "면·분식", "8,000~10,000원", "굵은 면과 다시 국물의 담백함", ["noodle", "light"], ["lunch", "dinner"], ["solo"], ["cold", "rain"], "새우튀김"),
    ("jjamppong", "짬뽕", "면·분식", "9,000~12,000원", "불맛 나는 해물 국물에 면을 넣은", ["noodle", "spicy"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "군만두"),
    ("jjajang", "짜장면", "면·분식", "7,000~9,000원", "춘장을 볶아 만든 소스에 면", ["noodle"], ["lunch", "dinner"], ["solo", "group"], ["rain", "warm"], "군만두·탕수육"),
    ("naengmyeon", "물냉면", "면·분식", "11,000~14,000원", "살얼음 육수에 메밀면과 편육", ["noodle", "light"], ["lunch", "dinner"], ["solo", "group"], ["warm"], "수육 한 접시"),
    ("makguksu", "막국수", "면·분식", "11,000~13,000원", "새콤한 동치미 육수에 메밀면", ["noodle", "light"], ["lunch"], ["solo"], ["warm"], "보쌈 수육"),
    ("kongguksu", "콩국수", "면·분식", "11,000~13,000원", "고소한 콩물에 소면을 말아 낸", ["noodle", "light"], ["lunch"], ["solo"], ["warm"], "겉절이 김치"),
    ("jjolmyeon", "쫄면", "면·분식", "8,000~10,000원", "새콤매콤한 양념에 쫄깃한 면", ["noodle", "spicy"], ["lunch"], ["solo", "group"], ["warm"], "김밥 한 줄"),
    ("ramyeon", "라면", "면·분식", "4,000~6,000원", "야식의 기본, 계란과 파를 올린 라면", ["noodle", "spicy"], ["dinner"], ["solo"], ["cold", "rain"], "계란·치즈 추가"),
    ("tteokbokki", "떡볶이", "면·분식", "6,000~9,000원", "매콤한 고추장 양념에 밀떡과 어묵", ["spicy"], ["lunch", "cafe"], ["solo", "group"], ["rain", "warm"], "튀김·순대"),
    ("gimbap", "김밥", "면·분식", "4,000~6,000원", "여러 재료를 말아 넣은 한 줄", ["light"], ["lunch", "cafe"], ["solo"], ["warm", "rain"], "라면·떡볶이"),
    ("kimchijeon", "김치전", "분식·전", "9,000~12,000원", "잘 익은 김치를 부쳐 낸 바삭한 전", ["noodle", "spicy"], ["dinner"], ["group"], ["rain", "cold"], "막걸리 한 사발"),
    ("haemul-pajeon", "해물파전", "분식·전", "13,000~16,000원", "쪽파와 해물을 넣고 넓게 부친 전", ["noodle"], ["dinner"], ["group"], ["rain", "cold"], "막걸리·동동주"),
    ("jeyuk", "제육볶음", "한식·밥", "10,000~12,000원", "매콤한 고추장 양념에 돼지고기와 양파", ["spicy"], ["lunch", "dinner"], ["solo", "group"], ["cold"], "된장찌개·계란찜"),
    ("bibimbap", "비빔밥", "한식·밥", "10,000~13,000원", "나물과 고추장을 비벼 먹는 한 그릇", ["light"], ["lunch"], ["solo"], ["warm"], "계란후라이"),
    ("kimchi-bokkeumbap", "김치볶음밥", "한식·밥", "8,000~10,000원", "김치와 밥을 센 불에 볶아 낸", ["spicy"], ["lunch", "dinner"], ["solo"], ["rain", "warm"], "계란후라이·치즈"),
    ("bossam", "보쌈정식", "한식·밥", "13,000~16,000원", "수육과 겉절이, 국물 한 그릇이 함께 나오는", ["gukmul"], ["dinner"], ["group"], ["cold"], "막국수"),
    ("ssambap", "쌈밥정식", "한식·밥", "13,000~16,000원", "쌈채소와 제철 나물 반찬이 가득한", ["light"], ["lunch"], ["solo", "group"], ["warm"], "된장찌개"),
    ("saengseon-gui", "생선구이 정식", "한식·밥", "13,000~16,000원", "고등어·갈치를 노릇하게 구워 낸 백반", ["light"], ["lunch"], ["solo"], ["cold"], "미역국"),
    ("hoedeopbap", "회덮밥", "한식·밥", "13,000~17,000원", "신선한 회와 채소를 밥 위에 올린", ["light"], ["lunch"], ["solo"], ["warm"], "미소시루"),
    ("donkatsu", "돈가스", "양식", "11,000~14,000원", "두툼한 등심을 바삭하게 튀긴", ["western"], ["lunch", "dinner"], ["solo", "group"], ["rain"], "우동·냉모밀"),
    ("omurice", "오므라이스", "양식", "10,000~13,000원", "볶음밥을 달걀로 감싸 데미글라스 소스를 두른", ["western"], ["lunch"], ["solo"], ["rain", "warm"], "샐러드"),
    ("pasta", "파스타", "양식", "13,000~18,000원", "알리오 올리오부터 크림까지 고를 수 있는", ["western"], ["lunch", "dinner"], ["solo", "group"], ["rain", "warm"], "갈릭 브레드"),
    ("risotto", "리조또", "양식", "14,000~18,000원", "쌀을 쫀득하게 익혀 낸 크림 리조또", ["western", "light"], ["lunch", "dinner"], ["solo"], ["rain"], "수프·샐러드 세트"),
    ("burger", "수제버거", "양식", "9,000~13,000원", "더블 패티와 체다 치즈를 올린 버거", ["western"], ["lunch", "dinner"], ["solo"], ["rain"], "감자튀김·콜라"),
    ("sandwich", "샌드위치", "양식", "8,000~12,000원", "치킨·에그를 채운 샌드위치", ["western", "light"], ["lunch", "cafe"], ["solo"], ["warm", "rain"], "수프"),
    ("brunch", "브런치 플레이트", "양식", "13,000~18,000원", "스크램블·소시지·샐러드를 한 접시에", ["western", "light"], ["cafe"], ["solo", "group"], ["warm", "rain"], "아메리카노"),
    ("steak", "등심 스테이크", "양식", "25,000~35,000원", "미디엄으로 구운 등심과 감자퓨레", ["western"], ["dinner"], ["solo", "group"], ["cold"], "레드와인 한 잔"),
    ("taco", "타코", "양식", "11,000~15,000원", "또르띠야에 고기·살사·아보카도를 채운", ["western"], ["lunch", "dinner"], ["solo", "group"], ["warm"], "구아카몰·나초"),
    ("curry", "카레", "아시안", "10,000~13,000원", "향신료를 진하게 볶아 낸 커리", ["western"], ["lunch", "dinner"], ["solo"], ["rain", "warm"], "난·라이스 추가"),
    ("pho", "쌀국수", "아시안", "10,000~13,000원", "소고기 육수에 라이스누들과 고수", ["noodle"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain", "warm"], "짜조·분짜"),
    ("ramen", "라멘", "아시안", "10,000~13,000원", "진한 돈코츠 육수에 차슈와 반숙란", ["noodle"], ["lunch", "dinner"], ["solo"], ["cold", "rain"], "반숙란 추가"),
    ("gyudon", "규동", "아시안", "9,000~11,000원", "달큰한 소고기와 양파를 올린 덮밥", ["light"], ["lunch", "dinner"], ["solo"], ["rain", "warm"], "온천란"),
    ("katsudon", "카츠동", "아시안", "11,000~13,000원", "바삭한 돈가스에 달걀을 얹은 덮밥", ["western"], ["lunch"], ["solo"], ["rain", "warm"], "미소시루"),
    ("padthai", "팟타이", "아시안", "12,000~15,000원", "새콤달콤하게 볶아 낸 쌀국수", ["noodle", "western"], ["lunch", "dinner"], ["solo"], ["warm"], "쏨땀"),
    ("kebab", "케밥", "아시안", "9,000~12,000원", "꼬치 고기와 채소를 납작빵에 말아 낸", ["western"], ["dinner"], ["solo"], ["warm"], "감자튀김"),
    ("malatang", "마라탕", "아시안", "8,000~13,000원", "재료를 골라 담는 얼얼한 사골 국물", ["spicy", "gukmul"], ["lunch", "dinner"], ["solo", "group"], ["cold", "rain"], "꿔바로우 소"),
    ("malaxiangguo", "마라샹궈", "아시안", "13,000~18,000원", "매콤한 향신료에 재료를 볶아 낸", ["spicy"], ["dinner"], ["group"], ["cold", "rain"], "마라탕 국물"),
    ("yangkkochi", "양꼬치", "아시안", "12,000~16,000원", "큐민 향을 입혀 구운 양고기 꼬치", ["western", "spicy"], ["dinner"], ["group"], ["cold", "rain"], "마라탕 사리"),
    ("samgyeopsal", "삼겹살", "고기·구이", "15,000~20,000원", "숯불에 구워 먹는 삼겹살, 된장찌개와 냉면 곁들임", [], ["dinner"], ["group"], ["cold", "rain"], "냉면·된장찌개"),
    ("dakgalbi", "닭갈비", "고기·구이", "12,000~15,000원", "철판에 볶아 내는 매콤한 닭고기", ["spicy"], ["dinner"], ["group"], ["cold", "rain"], "볶음밥 마무리"),
    ("gopchang", "곱창", "고기·구이", "18,000~25,000원", "고소하게 구운 곱창과 소주 한 잔", [], ["dinner"], ["group"], ["cold", "rain"], "볶음밥"),
    ("chicken", "치킨", "야식·안주", "20,000~25,000원", "바삭한 후라이드에 양념 반반", [], ["dinner"], ["group"], ["rain"], "치즈볼·감자튀김"),
    ("dakbal", "닭발", "야식·안주", "13,000~16,000원", "매운 양념에 볶아 낸 닭발", ["spicy"], ["dinner"], ["group"], ["cold", "rain"], "주먹밥·계란찜"),
    ("oden-tang", "오뎅탕", "야식·안주", "12,000~16,000원", "꼬치 어묵과 무를 넣은 술안주 국물", ["gukmul"], ["dinner"], ["group"], ["cold", "rain"], "어묵 꼬치 추가"),
    ("croissant", "크루아상", "카페·간식", "4,500~7,000원", "겹겹이 구운 버터 페이스트리", ["light"], ["cafe"], ["solo"], ["warm", "rain"], "아메리카노"),
    ("cake", "케이크", "카페·간식", "7,000~10,000원", "당 충전이 필요한 조각 케이크", ["light"], ["cafe"], ["solo", "group"], ["warm", "rain"], "라떼"),
    ("bungeoppang", "붕어빵", "카페·간식", "2,000~4,000원", "겨울 길거리 간식, 팥이 가득한", ["light"], ["cafe"], ["solo"], ["cold"], "호떡"),
    ("hotteok", "호떡", "카페·간식", "2,000~3,000원", "씨앗과 흑설탕이 든 따끈한 호떡", ["light"], ["cafe"], ["solo"], ["cold"], "어묵 국물"),
    ("eomuk", "어묵", "카페·간식", "3,000~5,000원", "길거리 어묵과 뜨끈한 국물", ["gukmul", "light"], ["cafe"], ["solo"], ["cold", "rain"], "떡볶이"),
    ("churros", "츄러스", "카페·간식", "5,000~7,000원", "따끈하게 튀겨 낸 츄러스와 초코 소스", ["light"], ["cafe"], ["solo", "group"], ["cold", "rain"], "핫초코"),
    ("bingsu", "빙수", "카페·간식", "8,000~14,000원", "우유 얼음에 과일을 올린 여름 디저트", ["light"], ["cafe"], ["solo", "group"], ["warm"], "아메리카노"),
    ("toast", "길거리 토스트", "카페·간식", "4,000~6,000원", "계란과 채소를 넣고 철판에 구운 토스트", ["light"], ["cafe"], ["solo"], ["warm", "rain"], "커피"),
    ("poke", "포케", "샐러드·가벼움", "12,000~16,000원", "연어·아보카도·채소를 올린 덮밥", ["light"], ["lunch"], ["solo"], ["warm"], "미소시루"),
    ("salad", "샐러드 볼", "샐러드·가벼움", "9,000~13,000원", "닭가슴살과 채소를 담은 샐러드", ["light"], ["lunch", "cafe"], ["solo"], ["warm"], "통밀 브레드"),
]

MENUS = [
    {
        "id": r[0], "name": r[1], "cat": r[2], "price": r[3], "desc": r[4],
        "styles": r[5], "sit": r[6], "comp": r[7], "wx": r[8], "side": r[9],
    }
    for r in MENU_ROWS
]

# ---------------------------------------------------------------- 나들이 코스
COURSE_CATS = [
    ("all", "전체"),
    ("indoor", "실내 아지트"),
    ("walk", "산책·야경"),
    ("culture", "전시·서점"),
    ("drive", "근교·드라이브"),
]

COURSES = [
    {
        "id": "daelim-changgo", "name": "대림창고", "area": "성수동", "cat": "indoor", "kind": "카페·전시",
        "time": "2~3시간", "when": "비 오는 주말 낮 12시 이후", "fit": ["rain", "cold"],
        "point": "1960년대 정수장을 고친 붉은 벽돌 공간. 카페와 소품숍, 전시가 한 동에 모여 비가 와도 동선이 짧습니다.",
    },
    {
        "id": "ssamziegil", "name": "쌈지길", "area": "인사동", "cat": "indoor", "kind": "공방·소품",
        "time": "1~2시간", "when": "토요일 오후 2~5시", "fit": ["rain", "cold"],
        "point": "나선형으로 이어진 공방 골목. 실내 가게가 이어져 짧은 비나 한파에 무난하고, 인사동 찻집과 묶기 좋습니다.",
    },
    {
        "id": "nmk", "name": "국립중앙박물관", "area": "용산", "cat": "indoor", "kind": "박물관",
        "time": "2~3시간", "when": "일요일 오전 10시 개관 직후", "fit": ["rain", "cold"],
        "point": "상설전시는 무료에 실내 동선이 길어 한파·폭우에 가장 안전한 선택. 4호선·경의중앙선 이촌역에서 도보로 닿습니다.",
    },
    {
        "id": "onion-anguk", "name": "어니언 안국", "area": "안국", "cat": "indoor", "kind": "카페",
        "time": "1시간", "when": "평일 오전 11시 이전", "fit": ["rain", "cold"],
        "point": "한옥을 고친 카페. 창가 자리와 오픈 샌드위치가 알려져 주말엔 대기가 길어 평일 오전이 편합니다.",
    },
    {
        "id": "namsan", "name": "N서울타워·남산순환로", "area": "용산·중구", "cat": "walk", "kind": "야경 산책",
        "time": "2시간", "when": "해 지기 30분 전 17시 무렵", "fit": ["warm"],
        "point": "케이블카 대신 순환로를 걸어 올라가면 서울 야경이 트입니다. 겨울 밤엔 바람이 강해 한 겹 더 챙기세요.",
    },
    {
        "id": "naksan", "name": "낙산공원 성곽길", "area": "종로", "cat": "walk", "kind": "야경 산책",
        "time": "1~1.5시간", "when": "금요일 저녁 19~21시", "fit": ["warm"],
        "point": "한양도성 성곽을 따라 걸으면 동대문 쪽 야경이 한눈에 들어옵니다. 오르막이 짧아 퇴근 후에도 부담이 적습니다.",
    },
    {
        "id": "seoul-forest", "name": "서울숲", "area": "성동", "cat": "walk", "kind": "공원 산책",
        "time": "1.5~2시간", "when": "토요일 오전 10~12시", "fit": ["warm"],
        "point": "사슴 우리와 은행나무길이 이어집니다. 11월 말엔 낙엽이 남아 있어 사진 찍기 좋고, 성수동 카페로 이어지기 편합니다.",
    },
    {
        "id": "mangwon", "name": "망원한강공원", "area": "마포", "cat": "walk", "kind": "노을·산책",
        "time": "1.5시간", "when": "일몰 30분 전", "fit": ["warm"],
        "point": "망원시장에서 먹거리를 사 들고 한강으로. 노을과 야경을 한 번에 보기 좋은 자리입니다.",
    },
    {
        "id": "mmca-seoul", "name": "국립현대미술관 서울", "area": "삼청동", "cat": "culture", "kind": "전시",
        "time": "2시간", "when": "평일 오후 3시 이후", "fit": ["rain", "cold"],
        "point": "관람 후 삼청동 카페로 이어지기 좋습니다. 수요일·토요일 야간 개장을 노리면 저녁까지 붙일 수 있습니다.",
    },
    {
        "id": "byeolmadang", "name": "별마당 도서관", "area": "강남 코엑스몰", "cat": "culture", "kind": "서점·실내",
        "time": "1~2시간", "when": "평일 저녁 8시 이후", "fit": ["rain", "cold"],
        "point": "13m 높이 서가가 열린 공간. 무료로 앉아 책을 볼 수 있어 비 오는 날 시간을 보내기 좋습니다.",
    },
    {
        "id": "kyobo", "name": "교보문고 광화문점", "area": "광화문", "cat": "culture", "kind": "서점",
        "time": "1~2시간", "when": "주말 오전 10시 개점 직후", "fit": ["rain", "cold"],
        "point": "국내 최대 규모 서점. 광화문 광장 산책과 묶으면 반나절 코스가 됩니다.",
    },
    {
        "id": "seoul-craft", "name": "서울공예박물관", "area": "안국", "cat": "culture", "kind": "전시·실내",
        "time": "1.5시간", "when": "비 오는 주말 낮", "fit": ["rain", "cold"],
        "point": "무료 관람에 어린이박물관과 야외 정원까지 있습니다. 안국·북촌 산책과 함께 돌기 좋습니다.",
    },
    {
        "id": "dumulmeori", "name": "두물머리", "area": "양평", "cat": "drive", "kind": "근교 드라이브",
        "time": "반나절(왕복 2시간 포함)", "when": "토요일 오전 9시 출발", "fit": ["warm"],
        "point": "북한강과 남한강이 만나는 지점. 아침 물안개 사진으로 알려져 이른 시간에 도착하는 편이 좋습니다.",
    },
    {
        "id": "heyri", "name": "헤이리 예술마을", "area": "파주", "cat": "drive", "kind": "근교 드라이브",
        "time": "반나절", "when": "일요일 오전 11시", "fit": ["warm"],
        "point": "갤러리·카페·소품숍이 모인 예술마을. 차로 1시간 거리라 반나절 코스로 적당합니다.",
    },
    {
        "id": "songdo", "name": "송도 센트럴파크", "area": "인천", "cat": "drive", "kind": "근교 드라이브",
        "time": "3~4시간", "when": "맑은 주말 오후", "fit": ["warm"],
        "point": "호수 둘레 산책로와 트라이볼 야경. 차로 50분 거리라 서울에서 가까운 바다 기분을 냅니다.",
    },
    {
        "id": "paldang", "name": "팔당 북한강 카페거리", "area": "남양주", "cat": "drive", "kind": "근교 드라이브",
        "time": "3시간", "when": "토요일 오후 3시", "fit": ["warm"],
        "point": "북한강을 따라 이어지는 카페들. 창가 자리에서 강을 보며 쉬기 좋습니다.",
    },
]

# ---------------------------------------------------------------- 추천 모드
MODES = {
    "cold": {
        "label": "추운 날", "head": "추운 날엔 따뜻한 국물", "tone": "cold",
        "line": "찬 바람이 부는 날, 속을 데우는 한 그릇이 답입니다.",
        "tpls": [
            "체감 {feels}까지 내려간 날, {name}처럼 속을 데우는 메뉴가 잘 맞습니다. {desc}.",
            "바람이 차가운 날엔 몸이 먼저 따뜻한 걸 찾습니다. {desc}, 국물 한 술이면 충분합니다.",
            "해가 짧아진 저녁, {name} 한 그릇으로 체온을 올리기 좋은 날입니다.",
        ],
    },
    "rain": {
        "label": "비 오는 날", "head": "비 오는 날엔 전·면 요리", "tone": "rain",
        "line": "비 오는 날엔 지글지글 부치는 전이나 뜨끈한 면이 잘 어울립니다.",
        "tpls": [
            "비가 오는 날엔 지글지글 부치는 전이나 뜨끈한 면이 잘 어울립니다. {desc}.",
            "우산 쓰고 다녀온 날은 몸이 으슬으슬합니다. {name}처럼 따뜻한 메뉴로 기분을 올리세요.",
            "빗소리 들리는 날, {desc}에 곁들임 하나면 실내에서도 든든합니다.",
        ],
    },
    "warm": {
        "label": "맑은·더운 날", "head": "맑은·더운 날엔 가볍고 시원하게", "tone": "warm",
        "line": "햇볕이 강한 날엔 기름진 메뉴보다 산뜻한 쪽이 좋습니다.",
        "tpls": [
            "맑고 더운 날엔 기름진 메뉴보다 가볍고 산뜻한 쪽이 잘 맞습니다. {desc}.",
            "햇볕이 강해 입맛이 떨어지는 날, {name}처럼 가벼운 한 그릇이 좋습니다.",
            "더운 날엔 뜨거운 국물보다 시원한 면·샐러드로 가볍게. {desc}.",
        ],
    },
    "mild": {
        "label": "선선한 날", "head": "선선한 날엔 고르게 잘 맞습니다", "tone": "mild",
        "line": "기온이 무난한 날이라 국물도 가벼운 메뉴도 모두 잘 맞습니다.",
        "tpls": [
            "기온이 무난한 날엔 취향대로 고르면 됩니다. {desc}.",
            "선선한 날이라 뜨거운 메뉴도 부담이 없습니다. {name}에 곁들임 하나 어떨까요.",
            "오늘 같은 날은 {desc} 쪽이 무난합니다.",
        ],
    },
}

CONDITION_KO = {
    "Clear": "맑음", "Mostly Clear": "대체로 맑음", "Partly Cloudy": "구름 조금",
    "Mostly Cloudy": "구름 많음", "Cloudy": "흐림", "Overcast": "흐림",
    "Rain": "비", "Drizzle": "이슬비", "Heavy Rain": "강한 비",
    "Snow": "눈", "Flurries": "눈발", "Fog": "안개", "Haze": "연무",
    "Windy": "바람", "Thunderstorms": "천둥번개", "Blizzard": "눈보라",
}

# ---------------------------------------------------------------- 아이콘 (단색 라인 SVG)
ICONS = {
    "sun": '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"/>',
    "cloud": '<path d="M7 18h10a4 4 0 0 0 .5-8 6 6 0 0 0-11.4 1.5A3.5 3.5 0 0 0 7 18z"/>',
    "cloudsun": '<circle cx="8" cy="8" r="2.6"/><path d="M8 3v1.4M8 11.6V13M3 8h1.4M11.6 8H13M4.4 4.4l1 1M10.6 10.6l1 1M11.6 4.4l-1 1"/><path d="M9 19h9a3.6 3.6 0 0 0 .4-7.2A5.4 5.4 0 0 0 8.6 13 3.2 3.2 0 0 0 9 19z"/>',
    "rain": '<path d="M7 15.5h10a3.8 3.8 0 0 0 .4-7.6A5.6 5.6 0 0 0 6.6 9.4 3.3 3.3 0 0 0 7 15.5z"/><path d="M8.5 18.5l-1 2M12 18.5l-1 2M15.5 18.5l-1 2"/>',
    "snow": '<path d="M7 15h10a3.8 3.8 0 0 0 .4-7.6A5.6 5.6 0 0 0 6.6 9 3.3 3.3 0 0 0 7 15z"/><path d="M8 19h.01M12 19h.01M16 19h.01M10 21.5h.01M14 21.5h.01"/>',
    "wind": '<path d="M3 8h10a3 3 0 1 0-3-3"/><path d="M3 12h14a3 3 0 1 1-3 3"/><path d="M3 16h7"/>',
    "bowl": '<path d="M4 11h16a8 8 0 0 1-8 8 8 8 0 0 1-8-8z"/><path d="M9 8c0-1.2 1-1.6 1-2.6M13 8c0-1.2 1-1.6 1-2.6"/>',
    "pin": '<path d="M12 21s6.5-5.5 6.5-10.5A6.5 6.5 0 0 0 5.5 10.5C5.5 15.5 12 21 12 21z"/><circle cx="12" cy="10.5" r="2.4"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 1.8"/>',
    "route": '<circle cx="6" cy="6" r="2.4"/><circle cx="18" cy="18" r="2.4"/><path d="M8.4 6h5.1a3.5 3.5 0 0 1 0 7H9.5a2.5 2.5 0 0 0 0 5h6.1"/>',
    "star": '<path d="M12 3.6l2.6 5.3 5.8.9-4.2 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8L3.6 9.8l5.8-.9z"/>',
    "shuffle": '<path d="M17 4l3 3-3 3"/><path d="M20 7H8.5a4.5 4.5 0 0 0 0 9H12"/><path d="M17 14l3 3-3 3"/><path d="M20 17h-4"/>',
}


def icon(name, size=14):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>'
            % (size, size, ICONS.get(name, "")))


def esc(v):
    return (str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


# ---------------------------------------------------------------- 빌드 시점 날씨
def _weather_cli(date_str=None):
    cmd = ["weather", WEATHER_COORDS]
    if date_str:
        cmd += ["--date", date_str]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    if res.returncode != 0 or not res.stdout.strip():
        raise RuntimeError((res.stderr or "weather CLI 실패").strip()[:200])
    return json.loads(res.stdout)["data"]


OPEN_METEO_URL = ("https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780"
                  "&timezone=Asia%2FSeoul&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m"
                  "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code"
                  "&forecast_days=2&wind_speed_unit=kmh")

OM_CODE = {
    0: "Clear", 1: "Mostly Clear", 2: "Partly Cloudy", 3: "Cloudy", 45: "Fog", 48: "Fog",
    51: "Drizzle", 53: "Drizzle", 55: "Drizzle", 56: "Drizzle", 57: "Drizzle",
    61: "Rain", 63: "Rain", 65: "Heavy Rain", 66: "Rain", 67: "Rain",
    71: "Snow", 73: "Snow", 75: "Snow", 77: "Flurries",
    80: "Rain", 81: "Rain", 82: "Heavy Rain", 85: "Snow", 86: "Snow",
    95: "Thunderstorms", 96: "Thunderstorms", 99: "Thunderstorms",
}


def _open_meteo_fallback():
    """weather CLI를 못 쓸 때의 빌드 시점 두 번째 경로(Open-Meteo)."""
    req = urllib.request.Request(OPEN_METEO_URL, headers={"User-Agent": "infosec-archive-build/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        d = json.loads(resp.read().decode("utf-8"))
    cur = d.get("current", {})
    daily = d.get("daily", {})
    days = []
    for i in range(len(daily.get("time", [])[:2])):
        code = daily.get("weather_code", [None, None])[i]
        days.append({
            "date": daily["time"][i],
            "low_c": round(daily["temperature_2m_min"][i]),
            "high_c": round(daily["temperature_2m_max"][i]),
            "precipitation_chance": round(daily.get("precipitation_probability_max", [0, 0])[i] or 0),
            "condition": OM_CODE.get(code, "Cloudy"),
        })
    return {
        "now": {
            "time": cur.get("time", ""),
            "condition": OM_CODE.get(cur.get("weather_code"), "Cloudy"),
            "temperature_c": round(cur.get("temperature_2m")),
            "feels_like_c": round(cur.get("apparent_temperature")),
            "wind_kmh": round(cur.get("wind_speed_10m") or 0),
        },
        "days": days,
    }


def load_build_weather():
    """서울 오늘/내일 날씨를 실제 값으로 확보한다. 폴백 문구를 쓰지 않기 위해 실패하면 None을 돌려준다."""
    source = "apple"
    try:
        today = _weather_cli()
        days = list(today.get("days", [])[:2])
        if len(days) < 2 and days:
            try:
                nxt = _weather_cli(date_str=days[0]["date"])
                more = [d for d in nxt.get("days", []) if d["date"] != days[0]["date"]]
                days = days + more[:1]
            except Exception:
                pass
        data = {"now": today.get("now", {}), "days": days}
    except Exception as exc:
        print(f"   (weather CLI 실패 → Open-Meteo 시도: {exc})")
        try:
            data, source = _open_meteo_fallback(), "open-meteo"
        except Exception as exc2:
            print(f"   ! 날씨 확보 실패: {exc2}")
            return None

    now = data.get("now", {}) or {}
    days = data.get("days", []) or []
    d0 = days[0] if days else {}
    d1 = days[1] if len(days) > 1 else {}

    def cond(c):
        return CONDITION_KO.get(c, c or "")

    return {
        "source": source,
        "updated": (now.get("time", "") or "")[-5:] or datetime.now(KST).strftime("%H:%M"),
        "now_temp": now.get("temperature_c"),
        "now_feels": now.get("feels_like_c"),
        "now_cond": cond(now.get("condition")),
        "now_wind": now.get("wind_kmh"),
        "today_date": d0.get("date", ""),
        "today_low": d0.get("low_c"),
        "today_high": d0.get("high_c"),
        "today_pop": d0.get("precipitation_chance"),
        "today_cond": cond(d0.get("condition")),
        "tomorrow_date": d1.get("date", ""),
        "tomorrow_low": d1.get("low_c"),
        "tomorrow_high": d1.get("high_c"),
        "tomorrow_pop": d1.get("precipitation_chance"),
        "tomorrow_cond": cond(d1.get("condition")),
    }


def mode_for_wx(wx):
    cond = (wx.get("now_cond") or "") + (wx.get("today_cond") or "")
    pop = wx.get("today_pop")
    pop = pop if isinstance(pop, int) else 0
    if any(k in cond for k in ("비", "소나기", "눈", "이슬비")) or pop >= 50:
        return "rain"
    feels = wx.get("now_feels")
    if not isinstance(feels, int):
        feels = wx.get("now_temp")
    if isinstance(feels, int) and feels <= 5:
        return "cold"
    temp = wx.get("now_temp")
    if isinstance(temp, int) and temp >= 26:
        return "warm"
    return "mild"


def weather_icon_name(cond, pop=None):
    cond = cond or ""
    if "눈" in cond:
        return "snow"
    if "비" in cond or "이슬비" in cond or "소나기" in cond or "천둥" in cond:
        return "rain"
    if (pop or 0) >= 50:
        return "rain"
    if "맑" in cond and "구름" not in cond:
        return "sun"
    if "구름 조금" in cond:
        return "cloudsun"
    return "cloud"


# ---------------------------------------------------------------- CSS
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

      --cold-bg: #eff6ff;  --cold-text: #1d4ed8;  --cold-border: #bfdbfe;
      --warm-bg: #fff7ed;  --warm-text: #c2410c;  --warm-border: #fed7aa;
      --rain-bg: #eef2ff;  --rain-text: #4338ca;  --rain-border: #c7d2fe;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
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

      --cold-bg: rgba(59, 130, 246, 0.14);  --cold-text: #93c5fd;  --cold-border: rgba(59, 130, 246, 0.3);
      --warm-bg: rgba(234, 88, 12, 0.14);   --warm-text: #fb923c;  --warm-border: rgba(234, 88, 12, 0.3);
      --rain-bg: rgba(99, 102, 241, 0.16);  --rain-text: #a5b4fc;  --rain-border: rgba(99, 102, 241, 0.32);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    html { scroll-behavior: smooth; }

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

    /* Global Header (index.html / study.html / outfit.html 과 동일) */
    .navbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    .nav-container {
      max-width: 1360px;
      margin: 0 auto;
      padding: 0 20px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }

    .brand-logo-img {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      object-fit: cover;
      display: block;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
      flex-shrink: 0;
    }

    .brand-name {
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      white-space: nowrap;
    }

    .nav-tabs {
      display: flex;
      gap: 5px;
      margin-left: 10px;
      flex: 1 1 auto;
      min-width: 0;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }

    .nav-tabs::-webkit-scrollbar { display: none; }

    .nav-tab-item {
      padding: 5px 10px;
      border-radius: 18px;
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      color: var(--text-secondary);
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .nav-tab-item:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .nav-tab-item.active { background: var(--accent-primary); color: #ffffff !important; }

    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .update-meta {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
      white-space: nowrap;
    }

    .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      flex-shrink: 0;
    }

    .icon-btn {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
      text-decoration: none;
    }

    .icon-btn:hover {
      background: var(--bg-subtle);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }

    /* Layout */
    .container { max-width: 980px; margin: 0 auto; padding: 32px 20px 80px; }

    .hero { margin-bottom: 20px; }

    .hero-pill {
      display: inline-block;
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 9px;
      margin-bottom: 12px;
    }

    .hero-title {
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .hero-desc {
      font-size: 14.5px;
      color: var(--text-secondary);
      line-height: 1.65;
      margin-bottom: 14px;
      max-width: 720px;
    }

    .hero-stats { display: flex; flex-wrap: wrap; gap: 8px; }

    .stat-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .stat-chip strong { color: var(--text-primary); font-weight: 600; }

    /* 공통 패널 */
    .panel {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      margin-bottom: 16px;
      overflow: hidden;
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 15px 18px 0;
    }

    .panel-title {
      font-size: 14.5px;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 7px;
      min-width: 0;
    }

    .panel-title .bar {
      width: 3px;
      height: 14px;
      border-radius: 2px;
      background: var(--accent-primary);
      display: inline-block;
      flex-shrink: 0;
    }

    .panel-meta {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11.5px;
      color: var(--text-muted);
      white-space: nowrap;
      flex-shrink: 0;
    }

    .panel-body { padding: 14px 18px 16px; }

    /* 날씨 + 추천 모드 */
    .wx-body {
      display: grid;
      grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
      gap: 14px;
      padding: 14px 18px 16px;
    }

    .wx-now {
      border: 1px solid var(--border-default);
      border-radius: 11px;
      background: var(--bg-page);
      padding: 13px 14px;
      min-width: 0;
    }

    .wx-now-main { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }

    .wx-icon {
      width: 34px;
      height: 34px;
      border-radius: 9px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .wx-temp {
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.04em;
      line-height: 1.1;
      font-variant-numeric: tabular-nums;
    }

    .wx-cond { font-size: 12px; color: var(--text-secondary); margin-top: 1px; }

    .wx-facts {
      display: flex;
      flex-wrap: wrap;
      gap: 4px 12px;
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .wx-facts strong { color: var(--text-primary); font-weight: 600; font-variant-numeric: tabular-nums; }

    .wx-rec { min-width: 0; display: flex; flex-direction: column; }

    .rec-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }

    .rec-label { font-size: 11px; font-weight: 600; color: var(--text-muted); letter-spacing: 0.04em; }

    .mode-title {
      font-size: 14px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      margin-bottom: 4px;
    }

    .rec-text {
      font-size: 13px;
      line-height: 1.65;
      color: var(--text-secondary);
      margin-bottom: 10px;
    }

    .mode-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; }

    .mode-note { font-size: 11px; color: var(--text-muted); margin-top: 8px; }

    /* 배지·칩 */
    .badge {
      display: inline-block;
      font-size: 11.5px;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: 6px;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
      white-space: nowrap;
    }

    .tone-cold { background: var(--cold-bg); color: var(--cold-text); border-color: var(--cold-border); }
    .tone-warm { background: var(--warm-bg); color: var(--warm-text); border-color: var(--warm-border); }
    .tone-rain { background: var(--rain-bg); color: var(--rain-text); border-color: var(--rain-border); }
    .tone-mild { background: var(--bg-subtle); color: var(--text-secondary); border-color: var(--border-default); }

    .chip, .seg-tab {
      font-family: inherit;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: -0.01em;
      padding: 6px 10px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.13s ease;
      white-space: nowrap;
    }

    .chip:hover, .seg-tab:hover { border-color: var(--border-strong); color: var(--text-primary); }

    .chip.active, .seg-tab.active {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #ffffff;
      font-weight: 600;
    }

    /* 필터 */
    .control-row { padding: 12px 0; border-top: 1px solid var(--border-subtle); }
    .control-row:first-child { padding-top: 0; border-top: none; }
    .control-row:last-child { padding-bottom: 0; }

    .control-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 9px;
    }

    .control-label {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.06em;
      color: var(--text-muted);
    }

    .chips { display: flex; flex-wrap: wrap; gap: 6px; }

    /* 룰렛 */
    .slot {
      border: 1px solid var(--border-default);
      border-radius: 12px;
      background: var(--bg-page);
      padding: 18px;
      margin: 14px 0 12px;
      min-height: 168px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: border-color 0.15s ease, background-color 0.15s ease;
    }

    .slot.has-pick { display: block; background: var(--bg-surface); border-color: var(--border-strong); }
    .slot.rolling .pick-name { opacity: 0.55; }

    .slot-hint { text-align: center; color: var(--text-muted); }
    .slot-hint svg { margin-bottom: 8px; opacity: 0.7; }
    .slot-hint p { font-size: 13px; line-height: 1.6; }

    .pick-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }

    .pick-name {
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.035em;
      line-height: 1.25;
      word-break: keep-all;
      overflow-wrap: anywhere;
    }

    .pick-price {
      font-size: 12.5px;
      color: var(--text-secondary);
      font-variant-numeric: tabular-nums;
      margin-top: 3px;
    }

    .pick-tags { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0 12px; }

    .pick-block {
      padding: 10px 0;
      border-top: 1px solid var(--border-subtle);
    }

    .pick-label {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 4px;
    }

    .pick-text {
      font-size: 13px;
      line-height: 1.7;
      color: var(--text-primary);
      overflow-wrap: anywhere;
    }

    .pick-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 4px 12px;
      font-size: 11.5px;
      color: var(--text-muted);
      padding-top: 8px;
    }

    .pick-meta strong { color: var(--text-secondary); font-weight: 600; }

    .pick-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }

    .btn {
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: -0.01em;
      padding: 10px 18px;
      border-radius: 9px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-primary);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: all 0.13s ease;
    }

    .btn:hover { border-color: var(--border-strong); background: var(--bg-subtle); }

    .btn-primary {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #ffffff;
    }

    .btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); color: #ffffff; }

    .btn:disabled { opacity: 0.55; cursor: default; }

    .slot-note {
      font-size: 11.5px;
      color: var(--text-muted);
      margin-left: auto;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .link-btn {
      font-family: inherit;
      font-size: 11.5px;
      color: var(--text-secondary);
      background: none;
      border: none;
      cursor: pointer;
      text-decoration: underline;
      text-underline-offset: 2px;
      padding: 0;
    }

    .link-btn:hover { color: var(--text-primary); }

    .star-btn {
      width: 30px;
      height: 30px;
      flex-shrink: 0;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-muted);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.13s ease;
    }

    .star-btn:hover { color: var(--accent-primary); border-color: var(--border-strong); }
    .star-btn[aria-pressed="true"] { color: var(--accent-primary); background: var(--accent-subtle); border-color: var(--accent-primary); }
    .star-btn[aria-pressed="true"] svg { fill: currentColor; }

    /* 즐겨찾기·최근 기록 */
    .split { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 16px; }

    .list { display: flex; flex-direction: column; gap: 2px; }

    .list-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 0;
      border-top: 1px solid var(--border-subtle);
      min-width: 0;
    }

    .list-item:first-child { border-top: none; padding-top: 2px; }

    .li-main { min-width: 0; flex: 1; }

    .li-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .li-meta { font-size: 11px; color: var(--text-muted); overflow-wrap: anywhere; }

    .li-empty { font-size: 12.5px; color: var(--text-muted); line-height: 1.65; padding: 8px 0 4px; }

    /* 메뉴 풀 */
    .menu-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 8px;
    }

    .menu-card {
      border: 1px solid var(--border-default);
      border-radius: 10px;
      background: var(--bg-surface);
      padding: 10px 11px;
      min-width: 0;
      cursor: pointer;
      transition: border-color 0.13s ease, background-color 0.13s ease;
    }

    .menu-card:hover { border-color: var(--border-strong); background: var(--bg-page); }

    .menu-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; }

    .menu-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      overflow-wrap: anywhere;
      min-width: 0;
    }

    .menu-card .star-btn { width: 24px; height: 24px; border-color: transparent; background: transparent; }
    .menu-card .star-btn:hover { background: var(--bg-subtle); }
    .menu-card .star-btn[aria-pressed="true"] { background: transparent; border-color: transparent; }

    .menu-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 2px 8px;
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 3px;
    }

    .menu-price { font-variant-numeric: tabular-nums; }

    /* 나들이 코스 */
    .course-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 10px;
    }

    .course-card {
      border: 1px solid var(--border-default);
      border-radius: 11px;
      background: var(--bg-surface);
      padding: 13px 14px 14px;
      min-width: 0;
    }

    .course-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; flex-wrap: wrap; }

    .course-name {
      font-size: 14.5px;
      font-weight: 700;
      letter-spacing: -0.02em;
      overflow-wrap: anywhere;
    }

    .course-area {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 11.5px;
      color: var(--text-muted);
      margin: 5px 0 9px;
    }

    .course-area svg { flex-shrink: 0; }

    .course-rows { display: flex; flex-direction: column; gap: 4px; margin-bottom: 9px; }

    .course-row {
      display: grid;
      grid-template-columns: 72px minmax(0, 1fr);
      gap: 8px;
      font-size: 11.5px;
      line-height: 1.55;
    }

    .course-row .k { color: var(--text-muted); }
    .course-row .v { color: var(--text-secondary); overflow-wrap: anywhere; }

    .course-point {
      font-size: 12px;
      line-height: 1.65;
      color: var(--text-secondary);
      padding-top: 9px;
      border-top: 1px solid var(--border-subtle);
      overflow-wrap: anywhere;
    }

    .result-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-size: 12px;
      color: var(--text-muted);
      margin: 0 2px 10px;
    }

    .result-meta strong { color: var(--text-primary); font-weight: 600; }

    .empty-state {
      display: none;
      font-size: 12.5px;
      color: var(--text-muted);
      text-align: center;
      padding: 22px 10px;
    }

    .empty-state.show { display: block; }

    [hidden] { display: none !important; }

    .footer {
      margin-top: 36px;
      padding-top: 18px;
      border-top: 1px solid var(--border-default);
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.8;
    }

    .footer a { color: var(--text-muted); text-decoration: none; border-bottom: 1px dotted var(--border-strong); }
    .footer a:hover { color: var(--text-secondary); }

    /* Mobile */
    @media (max-width: 760px) {
      .wx-body { grid-template-columns: minmax(0, 1fr); }
      .split { grid-template-columns: minmax(0, 1fr); }
      .course-grid { grid-template-columns: minmax(0, 1fr); }
    }

    @media (max-width: 640px) {
      .nav-container { padding: 0 12px; height: 54px; gap: 6px; }
      .brand-logo-img { width: 24px; height: 24px; }
      .brand-name { font-size: 15px; }
      .nav-tabs { margin-left: 6px; gap: 4px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; border-radius: 14px; }
      .update-meta { display: none !important; }
      .nav-actions a.icon-btn { display: none; }
      .container { padding: 18px 12px 60px; }
      .hero-title { font-size: 21px; }
      .hero-desc { font-size: 13px; line-height: 1.6; }
      .hero-stats { gap: 6px; }
      .stat-chip { font-size: 11px; padding: 3px 8px; }
      .panel-head { padding: 13px 14px 0; }
      .panel-title { font-size: 13.5px; }
      .panel-body { padding: 12px 14px 14px; }
      .wx-body { gap: 12px; padding: 12px 14px 14px; }
      .wx-temp { font-size: 24px; }
      .slot { padding: 15px; min-height: 150px; }
      .pick-name { font-size: 20px; }
      .pick-text { font-size: 12.5px; }
      .btn { font-size: 12.5px; padding: 9px 14px; }
      .slot-note { margin-left: 0; flex: 1 1 100%; }
      .menu-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
      .course-row { grid-template-columns: 66px minmax(0, 1fr); }
      .footer { font-size: 11.5px; }
    }

    @media (max-width: 560px) {
      .brand-name { display: none; }
    }

    @media (max-width: 430px) {
      .nav-container { padding: 0 8px; gap: 4px; }
      .nav-tabs { margin-left: 2px; gap: 1px; }
      .nav-tab-item { padding: 4px 5px; font-size: 10px; border-radius: 11px; letter-spacing: -0.045em; }
      .nav-actions { gap: 4px; }
      .nav-actions .icon-btn { width: 28px; height: 28px; }
    }

    /* 내비게이션 9탭 대응: 넘침 없이 한 줄 유지, 좁은 화면은 탭 영역만 가로 스크롤 */
    @media (max-width: 1440px) {
      .nav-container { max-width: 1360px; padding: 0 16px; }
      .nav-tabs { gap: 4px; margin-left: 8px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; }
    }

    @media (max-width: 1024px) {
      .nav-brand { min-width: 0; }
      .nav-tabs { flex: 1 1 auto; min-width: 0; overflow-x: auto; white-space: nowrap; scrollbar-width: none; -ms-overflow-style: none; }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 7px; font-size: 11px; }
    }
"""


# ---------------------------------------------------------------- HTML 조각
def menu_card(m):
    styles = ",".join(m["styles"])
    return (
        '<article class="menu-card" data-id="%s" data-styles="%s" data-sit="%s" data-comp="%s" data-wx="%s">'
        '<div class="menu-top"><span class="menu-name">%s</span>'
        '<button class="star-btn" type="button" data-fav="%s" aria-pressed="false" aria-label="%s 즐겨찾기" title="즐겨찾기">%s</button>'
        '</div>'
        '<div class="menu-meta"><span>%s</span><span class="menu-price">%s</span></div>'
        '</article>'
        % (esc(m["id"]), esc(styles), esc(",".join(m["sit"])), esc(",".join(m["comp"])), esc(",".join(m["wx"])),
           esc(m["name"]), esc(m["id"]), esc(m["name"]), icon("star", 13),
           esc(m["cat"]), esc(m["price"]))
    )


def course_card(c, mode):
    tone = MODES[mode]["tone"]
    fit_label = {"rain": "비 오는 날 실내", "cold": "추운 날 실내", "warm": "맑은 날 야외", "mild": "무난한 날"}[mode]
    if mode in c["fit"]:
        fit = '<span class="badge tone-%s">%s</span>' % (tone, esc(fit_label))
    else:
        fit = '<span class="badge" hidden>%s</span>' % esc(fit_label)
    return (
        '<article class="course-card" data-cat="%s" data-fit="%s">'
        '<div class="course-top"><h3 class="course-name">%s</h3>%s</div>'
        '<div class="course-area">%s<span>%s · %s</span></div>'
        '<div class="course-rows">'
        '<div class="course-row"><span class="k">소요 시간</span><span class="v">%s</span></div>'
        '<div class="course-row"><span class="k">추천 타이밍</span><span class="v">%s</span></div>'
        '</div>'
        '<p class="course-point">%s</p>'
        '</article>'
        % (esc(c["cat"]), esc(",".join(c["fit"])), esc(c["name"]), fit,
           icon("pin", 12), esc(c["area"]), esc(c["kind"]),
           esc(c["time"]), esc(c["when"]), esc(c["point"]))
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 오늘 뭐 먹지</title>
  <meta name="description" content="서울 오늘 날씨에 맞춰 점심·저녁 메뉴를 랜덤 룰렛으로 뽑아 주는 페이지. 추운 날 국물, 비 오는 날 전·면처럼 날씨별 추천 모드와 예상 가격대, 곁들임, 주말 나들이 코스까지 한 곳에 정리했습니다.">
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

  <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
    <symbol id="w-sun" viewBox="0 0 24 24">__SYM_SUN__</symbol>
    <symbol id="w-cloud" viewBox="0 0 24 24">__SYM_CLOUD__</symbol>
    <symbol id="w-cloudsun" viewBox="0 0 24 24">__SYM_CLOUDSUN__</symbol>
    <symbol id="w-rain" viewBox="0 0 24 24">__SYM_RAIN__</symbol>
    <symbol id="w-snow" viewBox="0 0 24 24">__SYM_SNOW__</symbol>
    <symbol id="w-wind" viewBox="0 0 24 24">__SYM_WIND__</symbol>
  </svg>

  <!-- Global Nav -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
        <div class="nav-tabs">
          <a href="index.html" class="nav-tab-item">채용공고</a>
          <a href="study.html" class="nav-tab-item">시험 공부</a>
          <a href="ai.html" class="nav-tab-item">AI 트렌드</a>
          <a href="cve.html" class="nav-tab-item">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
          <a href="radar.html" class="nav-tab-item">피싱 레이더</a>
          <a href="pick.html" class="nav-tab-item active">오늘 뭐 먹지</a>
          <a href="clue.html" class="nav-tab-item">3단서 추리</a>
          <a href="mission.html" class="nav-tab-item">퇴근길 미션</a>
          <a href="chart.html" class="nav-tab-item">차트 추리실</a>
        </div>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>서울 기준</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <script>
    // 좁은 화면에서 현재 페이지 탭이 가려지지 않도록 탭 영역만 살짝 스크롤한다.
    (function () {
      function keepActiveTabVisible() {
        var box = document.querySelector('.nav-tabs');
        if (!box) return;
        var act = box.querySelector('.nav-tab-item.active');
        if (!act || box.scrollWidth <= box.clientWidth) return;
        var br = box.getBoundingClientRect();
        var ar = act.getBoundingClientRect();
        if (ar.right > br.right) box.scrollLeft += (ar.right - br.right) + 8;
        else if (ar.left < br.left) box.scrollLeft -= (br.left - ar.left) + 8;
      }
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', keepActiveTabVisible);
      else keepActiveTabVisible();
      window.addEventListener('resize', keepActiveTabVisible);
    })();
  </script>

  <main class="container">

    <!-- Hero -->
    <section class="hero">
      <span class="hero-pill">DAILY PICK</span>
      <h1 class="hero-title">오늘 뭐 먹지</h1>
      <p class="hero-desc">서울 날씨를 읽고 오늘 입맛에 맞는 메뉴를 골라 드립니다. 추운 날엔 국물, 비 오는 날엔 전·면처럼 추천 모드가 자동으로 바뀌고, 조건을 좁혀 룰렛으로 한 가지를 뽑을 수 있습니다. 주말·퇴근 후 나들이 코스도 함께 정리했습니다.</p>
      <div class="hero-stats">
        <span class="stat-chip">메뉴 <strong>__MENU_COUNT__종</strong></span>
        <span class="stat-chip">나들이 <strong>__COURSE_COUNT__곳</strong></span>
        <span class="stat-chip">추천 모드 <strong>3종 + 자동</strong></span>
        <span class="stat-chip">기록 <strong>이 브라우저에만</strong></span>
      </div>
    </section>

    <!-- 날씨 + 추천 모드 -->
    <section class="panel" id="wxCard">
      <div class="panel-head">
        <div class="panel-title"><span class="bar"></span>오늘 서울 날씨와 추천 모드</div>
        <span class="panel-meta"><span class="live-dot"></span><span id="wxUpdated">__WX_UPDATED__</span></span>
      </div>
      <div class="wx-body">
        <div class="wx-now">
          <div class="wx-now-main">
            <span class="wx-icon" id="wxNowIcon">__NOW_ICON__</span>
            <div>
              <div class="wx-temp" id="wxNowTemp">__NOW_TEMP__</div>
              <div class="wx-cond" id="wxNowCond">__NOW_COND__</div>
            </div>
          </div>
          <div class="wx-facts">
            <span>체감 <strong id="wxNowFeels">__NOW_FEELS__</strong></span>
            <span>최저 <strong id="wxLow">__TODAY_LOW__</strong></span>
            <span>최고 <strong id="wxHigh">__TODAY_HIGH__</strong></span>
            <span>강수 <strong id="wxPop">__TODAY_POP__</strong></span>
            <span>바람 <strong id="wxWind">__TODAY_WIND__</strong></span>
          </div>
        </div>
        <div class="wx-rec">
          <div class="rec-head">
            <span class="badge tone-__MODE_TONE__" id="modeBadge">__MODE_BADGE__</span>
            <span class="rec-label">오늘의 추천 모드</span>
          </div>
          <div class="mode-title" id="modeTitle">__MODE_HEAD__</div>
          <p class="rec-text" id="modeLine">__MODE_LINE__</p>
          <div class="mode-chips" id="modeChips">
            <button class="chip active" type="button" data-mode="auto" aria-pressed="true">오늘 날씨</button>
            <button class="chip" type="button" data-mode="cold" aria-pressed="false">추운 날</button>
            <button class="chip" type="button" data-mode="rain" aria-pressed="false">비 오는 날</button>
            <button class="chip" type="button" data-mode="warm" aria-pressed="false">맑은·더운 날</button>
          </div>
          <div class="mode-note" id="modeNote">__MODE_NOTE__</div>
        </div>
      </div>
    </section>

    <!-- 룰렛 -->
    <section class="panel" id="roulette">
      <div class="panel-head">
        <div class="panel-title"><span class="bar"></span>오늘 뭐 먹지 룰렛</div>
        <span class="panel-meta">후보 <strong id="candCount">__CAND_COUNT__</strong>개</span>
      </div>
      <div class="panel-body">
        <div class="control-row">
          <div class="control-head"><span class="control-label">상황</span></div>
          <div class="chips" id="sitChips">__SIT_CHIPS__</div>
        </div>
        <div class="control-row">
          <div class="control-head"><span class="control-label">동행</span></div>
          <div class="chips" id="compChips">__COMP_CHIPS__</div>
        </div>
        <div class="control-row">
          <div class="control-head"><span class="control-label">스타일</span></div>
          <div class="chips" id="styleChips">__STYLE_CHIPS__</div>
        </div>

        <div class="slot" id="slotCard">
          <div class="slot-hint" id="slotHint">
            __HINT_ICON__
            <p id="slotHintText">조건을 고르고 <strong>메뉴 뽑기</strong>를 눌러 보세요.<br>날씨 모드에 맞는 후보 중에서 한 가지를 골라 드립니다.</p>
          </div>
          <div class="slot-body" id="slotBody" hidden>
            <div class="pick-head">
              <div style="min-width:0;">
                <div class="pick-name" id="pickName"></div>
                <div class="pick-price" id="pickPrice"></div>
              </div>
              <button class="star-btn" id="pickStar" type="button" aria-pressed="false" aria-label="뽑은 메뉴 즐겨찾기" title="즐겨찾기">__PICK_STAR_ICON__</button>
            </div>
            <div class="pick-tags">
              <span class="badge" id="pickCat"></span>
              <span class="badge" id="pickModeBadge"></span>
            </div>
            <div class="pick-block">
              <div class="pick-label">오늘 날씨 추천 이유</div>
              <p class="pick-text" id="pickReason"></p>
            </div>
            <div class="pick-block">
              <div class="pick-label">곁들임 추천</div>
              <p class="pick-text" id="pickSide"></p>
            </div>
            <div class="pick-meta" id="pickMeta"></div>
          </div>
        </div>

        <div class="pick-actions">
          <button class="btn btn-primary" id="drawBtn" type="button">__DRAW_ICON__<span id="drawLabel">메뉴 뽑기</span></button>
          <button class="btn" id="excludeBtn" type="button" hidden>제외하고 뽑기</button>
          <span class="slot-note" id="pickNote"></span>
        </div>
      </div>
    </section>

    <!-- 즐겨찾기 · 최근 기록 -->
    <div class="split">
      <section class="panel">
        <div class="panel-head">
          <div class="panel-title"><span class="bar"></span>즐겨찾기</div>
          <span class="panel-meta"><strong id="favCount">0</strong>개</span>
        </div>
        <div class="panel-body">
          <div class="list" id="favList"></div>
        </div>
      </section>
      <section class="panel">
        <div class="panel-head">
          <div class="panel-title"><span class="bar"></span>최근 뽑은 기록</div>
          <span class="panel-meta">최대 10개</span>
        </div>
        <div class="panel-body">
          <div class="list" id="recentList"></div>
        </div>
      </section>
    </div>

    <!-- 메뉴 풀 -->
    <section class="panel" id="menuPool">
      <div class="panel-head">
        <div class="panel-title"><span class="bar"></span>메뉴 풀</div>
        <span class="panel-meta"><strong id="menuCount">__MENU_COUNT__</strong>종 · 위 필터가 함께 적용됩니다</span>
      </div>
      <div class="panel-body">
        <div class="menu-grid" id="menuGrid">
          __MENU_CARDS__
        </div>
        <div class="empty-state" id="menuEmpty">선택한 조건에 맞는 메뉴가 없습니다. 필터를 넓혀 보세요.</div>
      </div>
    </section>

    <!-- 나들이 코스 -->
    <section class="panel" id="outingPanel">
      <div class="panel-head">
        <div class="panel-title"><span class="bar"></span>주말·퇴근 후 서울 나들이</div>
        <span class="panel-meta"><strong id="courseCount">__COURSE_COUNT__</strong>곳</span>
      </div>
      <div class="panel-body">
        <div class="control-row" style="padding-top:0;border-top:none;">
          <div class="control-head"><span class="control-label">코스 유형</span></div>
          <div class="chips" id="courseChips">__COURSE_CHIPS__</div>
        </div>
        <div class="result-meta" style="margin-top:12px;">
          <span id="courseMeta">__COURSE_META__</span>
        </div>
        <div class="course-grid" id="courseGrid">
          __COURSE_CARDS__
        </div>
        <div class="empty-state" id="courseEmpty">선택한 유형의 코스가 없습니다.</div>
      </div>
    </section>

    <footer class="footer">
      Infosec Archive · 오늘 뭐 먹지 · 날씨 맞춤 메뉴 추천<br>
      오늘 날씨 기본값은 빌드 시점 Apple Weather, 방문 시 Open-Meteo 실시간 예보로 갱신됩니다.<br>
      예상 가격대는 서울 기준 대략치이며 실제 가격과 다를 수 있습니다. 즐겨찾기·뽑기 기록은 이 브라우저에만 저장됩니다.<br>
      최종 갱신 __BUILT_AT__
    </footer>
  </main>

  <script>
    const MENUS = __MENUS_JSON__;
    const COURSES = __COURSES_JSON__;
    const MODES = __MODES_JSON__;
    const WX_BUILD = __WX_JSON__;
    const STORE_KEY = 'secjobs-pick-v1';
    const RECENT_MAX = 10;

    // ---- Theme (다른 페이지와 동일한 secjobs-theme 동기화) ----
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');

    function setTheme(theme) {
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'block';
        try { localStorage.setItem('secjobs-theme', 'dark'); } catch (e) {}
      } else {
        document.documentElement.removeAttribute('data-theme');
        if (moonIcon) moonIcon.style.display = 'block';
        if (sunIcon) sunIcon.style.display = 'none';
        try { localStorage.setItem('secjobs-theme', 'light'); } catch (e) {}
      }
    }

    (function initTheme() {
      let saved = null;
      try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) setTheme('dark');
      else setTheme('light');
    })();

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    // ---- 저장소 (즐겨찾기 · 최근 뽑은 기록) ----
    function loadStore() {
      let raw = null;
      try { raw = localStorage.getItem(STORE_KEY); } catch (e) {}
      const empty = { fav: [], recent: [] };
      if (!raw) return empty;
      try {
        const d = JSON.parse(raw);
        if (!d || typeof d !== 'object') return empty;
        const fav = Array.isArray(d.fav) ? d.fav.filter(id => typeof id === 'string') : [];
        const recent = Array.isArray(d.recent)
          ? d.recent.filter(r => r && typeof r.id === 'string').slice(0, RECENT_MAX)
          : [];
        return { fav: fav, recent: recent };
      } catch (e) {
        return empty;
      }
    }

    const store = loadStore();

    function saveStore() {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); } catch (e) {}
    }

    // ---- 날씨 ----
    const COND_BY_CODE = {
      0: '맑음', 1: '대체로 맑음', 2: '구름 조금', 3: '흐림', 45: '안개', 48: '안개',
      51: '이슬비', 53: '이슬비', 55: '이슬비', 56: '이슬비', 57: '이슬비',
      61: '비', 63: '비', 65: '강한 비', 66: '비', 67: '비',
      71: '눈', 73: '눈', 75: '눈', 77: '눈발',
      80: '소나기', 81: '소나기', 82: '강한 비', 85: '눈', 86: '눈',
      95: '천둥번개', 96: '천둥번개', 99: '천둥번개'
    };

    function iconNameFor(cond, pop) {
      const c = cond || '';
      if (c.indexOf('눈') !== -1) return 'snow';
      if (c.indexOf('비') !== -1 || c.indexOf('이슬비') !== -1 || c.indexOf('소나기') !== -1 || c.indexOf('천둥') !== -1) return 'rain';
      if ((pop || 0) >= 50) return 'rain';
      if (c.indexOf('맑') !== -1 && c.indexOf('구름') === -1) return 'sun';
      if (c.indexOf('구름 조금') !== -1) return 'cloudsun';
      return 'cloud';
    }

    function setWxIcon(el, name) {
      if (!el) return;
      el.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><use href="#w-' + name + '"></use></svg>';
    }

    function fmtTemp(v) {
      return (typeof v === 'number' && isFinite(v)) ? (Math.round(v) + '°') : '—';
    }

    const state = {
      sit: 'all', comp: 'all', style: 'all',
      mode: 'auto',                   // auto | cold | rain | warm
      wx: {
        temp: WX_BUILD.now_temp, feels: WX_BUILD.now_feels, cond: WX_BUILD.now_cond,
        low: WX_BUILD.today_low, high: WX_BUILD.today_high, pop: WX_BUILD.today_pop,
        wind: WX_BUILD.now_wind, updated_text: WX_BUILD.updated + ' 기준',
        tomorrow_cond: WX_BUILD.tomorrow_cond, tomorrow_low: WX_BUILD.tomorrow_low, tomorrow_high: WX_BUILD.tomorrow_high
      },
      pick: null, excluded: [], rolling: false, courseCat: 'all', live: false
    };

    function modeFromWx(wx) {
      const cond = (wx.cond || '');
      const pop = (typeof wx.pop === 'number') ? wx.pop : 0;
      if (cond.indexOf('비') !== -1 || cond.indexOf('소나기') !== -1 || cond.indexOf('눈') !== -1 || cond.indexOf('이슬비') !== -1 || pop >= 50) return 'rain';
      const feels = (typeof wx.feels === 'number') ? wx.feels : wx.temp;
      if (typeof feels === 'number' && feels <= 5) return 'cold';
      if (typeof wx.temp === 'number' && wx.temp >= 26) return 'warm';
      return 'mild';
    }

    function effMode() {
      return state.mode === 'auto' ? modeFromWx(state.wx) : state.mode;
    }

    function wxContext() {
      const parts = [];
      if (typeof state.wx.feels === 'number') parts.push('체감 ' + fmtTemp(state.wx.feels));
      if (state.wx.cond) parts.push(state.wx.cond);
      if (typeof state.wx.low === 'number' && typeof state.wx.high === 'number') parts.push('최저 ' + fmtTemp(state.wx.low) + ' / 최고 ' + fmtTemp(state.wx.high));
      if (typeof state.wx.pop === 'number' && state.wx.pop > 0) parts.push('강수 ' + state.wx.pop + '%');
      return parts.join(' · ');
    }

    const wxEls = {
      temp: document.getElementById('wxNowTemp'),
      cond: document.getElementById('wxNowCond'),
      feels: document.getElementById('wxNowFeels'),
      low: document.getElementById('wxLow'),
      high: document.getElementById('wxHigh'),
      pop: document.getElementById('wxPop'),
      wind: document.getElementById('wxWind'),
      updated: document.getElementById('wxUpdated'),
      icon: document.getElementById('wxNowIcon'),
      badge: document.getElementById('modeBadge'),
      title: document.getElementById('modeTitle'),
      line: document.getElementById('modeLine'),
      note: document.getElementById('modeNote')
    };

    function paintWeather() {
      const wx = state.wx;
      if (wxEls.temp) wxEls.temp.textContent = fmtTemp(wx.temp);
      if (wxEls.cond) wxEls.cond.textContent = wx.cond || '—';
      if (wxEls.feels) wxEls.feels.textContent = fmtTemp(wx.feels);
      if (wxEls.low) wxEls.low.textContent = fmtTemp(wx.low);
      if (wxEls.high) wxEls.high.textContent = fmtTemp(wx.high);
      if (wxEls.pop) wxEls.pop.textContent = (typeof wx.pop === 'number') ? wx.pop + '%' : '—';
      if (wxEls.wind) wxEls.wind.textContent = (typeof wx.wind === 'number') ? wx.wind + 'km/h' : '—';
      if (wxEls.updated) wxEls.updated.textContent = wx.updated_text || (WX_BUILD.updated + ' 기준');
      setWxIcon(wxEls.icon, iconNameFor(wx.cond, wx.pop));
      paintMode();
    }

    function paintMode() {
      const key = effMode();
      const m = MODES[key] || MODES.mild;
      document.querySelectorAll('#modeChips .chip').forEach(chip => {
        chip.classList.toggle('active', chip.dataset.mode === state.mode);
        chip.setAttribute('aria-pressed', chip.dataset.mode === state.mode ? 'true' : 'false');
      });
      if (wxEls.badge) {
        wxEls.badge.className = 'badge tone-' + m.tone;
        wxEls.badge.textContent = (state.mode === 'auto' ? '오늘 날씨 · ' : '') + m.label;
      }
      if (wxEls.title) wxEls.title.textContent = m.head;
      if (wxEls.line) wxEls.line.textContent = m.line;
      if (wxEls.note) {
        let note = wxContext() || '';
        if (state.wx.tomorrow_cond) {
          note += (note ? ' · ' : '') + '내일 ' + state.wx.tomorrow_cond;
        }
        if (state.mode !== 'auto') note += ' · 직접 고른 모드';
        wxEls.note.textContent = note;
      }
    }

    // ---- 메뉴 룰렛 ----
    const slotCard = document.getElementById('slotCard');
    const slotHint = document.getElementById('slotHint');
    const slotBody = document.getElementById('slotBody');
    const pickName = document.getElementById('pickName');
    const pickPrice = document.getElementById('pickPrice');
    const pickCat = document.getElementById('pickCat');
    const pickModeBadge = document.getElementById('pickModeBadge');
    const pickReason = document.getElementById('pickReason');
    const pickSide = document.getElementById('pickSide');
    const pickMeta = document.getElementById('pickMeta');
    const pickStar = document.getElementById('pickStar');
    const drawBtn = document.getElementById('drawBtn');
    const drawLabel = document.getElementById('drawLabel');
    const excludeBtn = document.getElementById('excludeBtn');
    const pickNote = document.getElementById('pickNote');
    const candCount = document.getElementById('candCount');
    const menuGrid = document.getElementById('menuGrid');
    const menuCount = document.getElementById('menuCount');
    const menuEmpty = document.getElementById('menuEmpty');
    const menuCards = Array.from(document.querySelectorAll('.menu-card'));

    function matchesFilters(m) {
      const sitOk = state.sit === 'all' || m.sit.indexOf(state.sit) !== -1;
      const compOk = state.comp === 'all' || m.comp.indexOf(state.comp) !== -1;
      const styleOk = state.style === 'all' || m.styles.indexOf(state.style) !== -1;
      return sitOk && compOk && styleOk;
    }

    function wxAffinity(m) {
      const mode = effMode();
      if (mode === 'mild') return true;
      return m.wx.indexOf(mode) !== -1;
    }

    function candidatePool() {
      const filtered = MENUS.filter(matchesFilters);
      const withWx = filtered.filter(wxAffinity);
      return withWx.length ? withWx : filtered;
    }

    function candidates() {
      const pool = candidatePool();
      const live = pool.filter(m => state.excluded.indexOf(m.id) === -1);
      return live.length ? live : [];
    }

    function reasonFor(m) {
      const mode = effMode();
      const conf = MODES[mode] || MODES.mild;
      let seed = 0;
      for (let i = 0; i < m.id.length; i++) seed = (seed * 31 + m.id.charCodeAt(i)) % 9973;
      const tpl = conf.tpls[seed % conf.tpls.length];
      const feels = (typeof state.wx.feels === 'number') ? fmtTemp(state.wx.feels) : '오늘';
      return tpl.replace('{name}', m.name).replace('{desc}', m.desc).replace('{feels}', feels);
    }

    function paintPick(m) {
      pickName.textContent = m.name;
      pickPrice.textContent = m.price;
      pickCat.textContent = m.cat;
      pickModeBadge.textContent = (MODES[effMode()] || MODES.mild).label + ' 추천';
      pickModeBadge.className = 'badge tone-' + (MODES[effMode()] || MODES.mild).tone;
      pickReason.textContent = reasonFor(m);
      pickSide.textContent = m.side;
      pickMeta.innerHTML = '<span>후보 <strong>' + candidates().length + '</strong>개 중</span>'
        + '<span>' + wxContext() + '</span>';
      pickStar.setAttribute('aria-pressed', store.fav.indexOf(m.id) !== -1 ? 'true' : 'false');
    }

    function commitPick(m, record) {
      state.pick = m;
      slotCard.classList.add('has-pick');
      slotCard.classList.remove('rolling');
      slotHint.hidden = true;
      slotBody.hidden = false;
      paintPick(m);
      drawLabel.textContent = '다시 뽑기';
      excludeBtn.hidden = false;
      if (record !== false) {
        const now = new Date();
        const hh = ('0' + now.getHours()).slice(-2);
        const mm = ('0' + now.getMinutes()).slice(-2);
        store.recent = store.recent.filter(r => r.id !== m.id);
        store.recent.unshift({ id: m.id, mode: effMode(), at: hh + ':' + mm });
        store.recent = store.recent.slice(0, RECENT_MAX);
        saveStore();
        renderRecent();
      }
      renderNote();
    }

    function renderNote() {
      if (!pickNote) return;
      if (!state.excluded.length) {
        pickNote.innerHTML = '<span>뽑은 메뉴는 이 브라우저에만 기록됩니다</span>';
        return;
      }
      pickNote.innerHTML = '<span>제외 ' + state.excluded.length + '개</span>'
        + '<button class="link-btn" type="button" id="resetExcluded">제외 초기화</button>';
      const btn = document.getElementById('resetExcluded');
      if (btn) {
        btn.addEventListener('click', () => {
          state.excluded = [];
          renderNote();
          renderCandidatesCount();
        });
      }
    }

    function emptySlot(text) {
      slotCard.classList.remove('has-pick');
      slotCard.classList.remove('rolling');
      slotHint.hidden = false;
      slotBody.hidden = true;
      const t = document.getElementById('slotHintText');
      if (t) t.innerHTML = text;
    }

    function draw(animate) {
      if (state.rolling) return;
      const list = candidates();
      if (!list.length) {
        emptySlot('이 조건에서는 뽑을 메뉴가 없습니다.<br>제외 목록을 초기화하거나 필터를 넓혀 보세요.');
        return;
      }
      const pick = list[Math.floor(Math.random() * list.length)];
      if (!animate) {
        commitPick(pick);
        return;
      }
      state.rolling = true;
      drawBtn.disabled = true;
      excludeBtn.disabled = true;
      slotCard.classList.add('has-pick');
      slotCard.classList.add('rolling');
      slotHint.hidden = true;
      slotBody.hidden = false;
      let ticks = 0;
      const total = 16;
      const timer = setInterval(() => {
        const r = list[Math.floor(Math.random() * list.length)];
        pickName.textContent = r.name;
        pickPrice.textContent = '—';
        pickCat.textContent = r.cat;
        ticks++;
        if (ticks >= total) {
          clearInterval(timer);
          state.rolling = false;
          drawBtn.disabled = false;
          excludeBtn.disabled = false;
          slotCard.classList.remove('rolling');
          commitPick(pick);
        }
      }, 55);
    }

    drawBtn.addEventListener('click', () => draw(true));

    excludeBtn.addEventListener('click', () => {
      if (!state.pick) return;
      if (state.excluded.indexOf(state.pick.id) === -1) state.excluded.push(state.pick.id);
      draw(true);
    });

    pickStar.addEventListener('click', () => {
      if (!state.pick) return;
      toggleFav(state.pick.id);
      paintPick(state.pick);
    });

    // ---- 필터 ----
    function bindChips(containerId, key, attr, onChange) {
      const box = document.getElementById(containerId);
      if (!box) return;
      box.addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-' + attr + ']');
        if (!btn) return;
        state[key] = btn.dataset[attr];
        box.querySelectorAll('button').forEach(b => { b.classList.toggle('active', b === btn); b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        if (onChange) onChange();
      });
    }

    bindChips('sitChips', 'sit', 'sit', () => { applyMenuFilter(); renderCandidatesCount(); });
    bindChips('compChips', 'comp', 'comp', () => { applyMenuFilter(); renderCandidatesCount(); });
    bindChips('styleChips', 'style', 'style', () => { applyMenuFilter(); renderCandidatesCount(); });

    document.getElementById('modeChips').addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-mode]');
      if (!btn) return;
      state.mode = btn.dataset.mode;
      state.excluded = [];
      paintMode();
      renderCandidatesCount();
      renderNote();
      sortCourses();
      applyCourseFilter();
      if (state.pick) paintPick(state.pick);
    });

    function applyMenuFilter() {
      if (!menuCards.length) return;
      let shown = 0;
      menuCards.forEach(card => {
        const m = MENUS.filter(x => x.id === card.dataset.id)[0];
        const ok = m ? matchesFilters(m) : false;
        card.hidden = !ok;
        if (ok) shown++;
      });
      if (menuCount) menuCount.textContent = shown;
      if (menuEmpty) menuEmpty.classList.toggle('show', shown === 0);
    }

    function renderCandidatesCount() {
      if (!candCount) return;
      const pool = candidatePool().length;
      const live = candidates().length;
      candCount.textContent = live;
      candCount.title = '필터와 날씨 모드에 맞는 후보 ' + pool + '개 중 제외 ' + (pool - live) + '개';
      if (state.pick) {
        pickMeta.innerHTML = '<span>후보 <strong>' + live + '</strong>개 중</span>'
          + '<span>' + wxContext() + '</span>';
      }
    }

    // ---- 즐겨찾기 · 최근 기록 ----
    const favList = document.getElementById('favList');
    const recentList = document.getElementById('recentList');
    const favCount = document.getElementById('favCount');

    function menuById(id) {
      return MENUS.filter(m => m.id === id)[0] || null;
    }

    // localStorage 값이 조작돼도 마크업이 깨지지 않도록 목록 렌더링은 항상 이스케이프한다.
    function escHtml(s) {
      return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
      });
    }

    function toggleFav(id) {
      const i = store.fav.indexOf(id);
      if (i === -1) store.fav.push(id);
      else store.fav.splice(i, 1);
      saveStore();
      renderFav();
      syncStars();
    }


    function syncStars() {
      if (menuGrid) {
        menuGrid.querySelectorAll('.star-btn').forEach(btn => {
          btn.setAttribute('aria-pressed', store.fav.indexOf(btn.dataset.fav) !== -1 ? 'true' : 'false');
        });
      }
      if (state.pick && pickStar) {
        pickStar.setAttribute('aria-pressed', store.fav.indexOf(state.pick.id) !== -1 ? 'true' : 'false');
      }
    }

    function renderFav() {
      if (!favList) return;
      const items = store.fav.map(menuById).filter(Boolean);
      favCount.textContent = items.length;
      if (!items.length) {
        favList.innerHTML = '<p class="li-empty">마음에 드는 메뉴의 별을 누르면 여기에 모입니다.</p>';
        return;
      }
      favList.innerHTML = items.map(m =>
        '<div class="list-item"><div class="li-main"><div class="li-name">' + escHtml(m.name) + '</div>'
        + '<div class="li-meta">' + escHtml(m.cat) + ' · ' + escHtml(m.price) + '</div></div>'
        + '<button class="star-btn" type="button" data-unfav="' + escHtml(m.id) + '" aria-pressed="true" aria-label="' + escHtml(m.name) + ' 즐겨찾기 해제" title="즐겨찾기 해제">'
        + '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + __STAR_PATH__ + '</svg>'
        + '</button></div>'
      ).join('');
    }

    function renderRecent() {
      if (!recentList) return;
      const items = store.recent.map(r => ({ r: r, m: menuById(r.id) })).filter(x => x.m);
      if (!items.length) {
        recentList.innerHTML = '<p class="li-empty">룰렛으로 뽑은 메뉴가 시간과 함께 쌓입니다.</p>';
        return;
      }
      recentList.innerHTML = items.map(x =>
        '<div class="list-item"><div class="li-main"><div class="li-name">' + escHtml(x.m.name) + '</div>'
        + '<div class="li-meta">' + escHtml(x.r.at) + ' · ' + escHtml((MODES[x.r.mode] || MODES.mild).label) + ' 모드</div></div></div>'
      ).join('');
    }

    if (favList) {
      favList.addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-unfav]');
        if (!btn) return;
        toggleFav(btn.dataset.unfav);
      });
    }

    if (menuGrid) {
      menuGrid.addEventListener('click', (e) => {
        const star = e.target.closest('button[data-fav]');
        if (star) {
          e.stopPropagation();
          toggleFav(star.dataset.fav);
          return;
        }
        const card = e.target.closest('.menu-card');
        if (!card) return;
        const m = menuById(card.dataset.id);
        if (m) {
          commitPick(m, false);
          document.getElementById('roulette').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }

    // ---- 나들이 코스 ----
    const courseGrid = document.getElementById('courseGrid');
    const courseCards = Array.from(document.querySelectorAll('.course-card'));
    const courseCount = document.getElementById('courseCount');
    const courseEmpty = document.getElementById('courseEmpty');
    const courseChips = document.getElementById('courseChips');
    const courseMeta = document.getElementById('courseMeta');

    function fitLabelFor(mode) {
      return { rain: '비 오는 날 실내', cold: '추운 날 실내', warm: '맑은 날 야외', mild: '무난한 날' }[mode] || '추천';
    }

    function applyCourseFilter() {
      if (!courseCards.length) return;
      let shown = 0;
      courseCards.forEach(card => {
        const ok = state.courseCat === 'all' || card.dataset.cat === state.courseCat;
        card.hidden = !ok;
        if (ok) shown++;
      });
      if (courseCount) courseCount.textContent = shown;
      if (courseEmpty) courseEmpty.classList.toggle('show', shown === 0);
      if (courseMeta) {
        const mode = effMode();
        courseMeta.innerHTML = '<strong>' + (MODES[mode] || MODES.mild).label + '</strong> 기준으로 '
          + (state.courseCat === 'all' ? '날씨에 맞는 코스를 위로' : '해당 유형만') + ' 보여 줍니다';
      }
    }

    function sortCourses() {
      if (!courseGrid) return;
      const mode = effMode();
      const sorted = courseCards.slice().sort((a, b) => {
        const af = (a.dataset.fit || '').split(',').indexOf(mode) !== -1 ? 0 : 1;
        const bf = (b.dataset.fit || '').split(',').indexOf(mode) !== -1 ? 0 : 1;
        return af - bf;
      });
      sorted.forEach(card => {
        const badge = card.querySelector('.course-top .badge');
        if (badge) {
          const fit = (card.dataset.fit || '').split(',');
          if (fit.indexOf(mode) !== -1) {
            badge.textContent = fitLabelFor(mode);
            badge.className = 'badge tone-' + (MODES[mode] || MODES.mild).tone;
            badge.hidden = false;
          } else {
            badge.hidden = true;
          }
        }
        courseGrid.appendChild(card);
      });
    }

    if (courseChips) {
      courseChips.addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-cat]');
        if (!btn) return;
        state.courseCat = btn.dataset.cat;
        courseChips.querySelectorAll('button').forEach(b => { b.classList.toggle('active', b === btn); b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        applyCourseFilter();
      });
    }

    // ---- 초기화 ----
    paintWeather();
    applyMenuFilter();
    renderCandidatesCount();
    renderFav();
    renderRecent();
    syncStars();
    renderNote();
    sortCourses();
    applyCourseFilter();

    // Open-Meteo: 현재 기온·체감·최저/최고·강수확률·바람
    fetch('https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&timezone=Asia%2FSeoul&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code&forecast_days=2&wind_speed_unit=kmh')
      .then(r => { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
      .then(d => {
        if (!d || !d.current || !d.daily) throw new Error('empty');
        state.wx = {
          temp: Math.round(d.current.temperature_2m),
          feels: Math.round(d.current.apparent_temperature),
          cond: COND_BY_CODE[d.current.weather_code] || '흐림',
          wind: Math.round(d.current.wind_speed_10m || 0),
          low: Math.round(d.daily.temperature_2m_min[0]),
          high: Math.round(d.daily.temperature_2m_max[0]),
          pop: Math.round(d.daily.precipitation_probability_max[0] || 0),
          tomorrow_cond: COND_BY_CODE[d.daily.weather_code[1]] || '',
          tomorrow_low: Math.round(d.daily.temperature_2m_min[1]),
          tomorrow_high: Math.round(d.daily.temperature_2m_max[1]),
          updated_text: '실시간 ' + ((d.current.time || '').slice(11, 16)) + ' 기준'
        };
        state.live = true;
        paintWeather();
        renderCandidatesCount();
        sortCourses();
        applyCourseFilter();
        if (state.pick) paintPick(state.pick);
      })
      .catch(() => {
        // 실시간 조회가 막혀도 빌드 시점 실측값을 그대로 유지한다.
        if (wxEls.updated) wxEls.updated.textContent = '빌드 시점 ' + (WX_BUILD.updated || '') + ' 기준';
      });
  </script>
</body>
</html>
"""


def build():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    built_at = now.strftime("%Y-%m-%d %H:%M KST")

    wx = load_build_weather()
    if wx is None:
        print("-> 'pick.html' 생성 건너뜀 (서울 날씨를 확보하지 못해 기존 파일을 유지합니다)")
        return 0

    mode = mode_for_wx(wx)

    sit_chips = "".join(
        '<button class="chip%s" type="button" data-sit="%s" aria-pressed="%s">%s</button>'
        % (" active" if key == "all" else "", key, "true" if key == "all" else "false", esc(label))
        for key, label in SITUATIONS
    )
    comp_chips = "".join(
        '<button class="chip%s" type="button" data-comp="%s" aria-pressed="%s">%s</button>'
        % (" active" if key == "all" else "", key, "true" if key == "all" else "false", esc(label))
        for key, label in COMPANIONS
    )
    style_chips = "".join(
        '<button class="chip%s" type="button" data-style="%s" aria-pressed="%s">%s</button>'
        % (" active" if key == "all" else "", key, "true" if key == "all" else "false", esc(label))
        for key, label in STYLES
    )
    course_chips = "".join(
        '<button class="chip%s" type="button" data-cat="%s" aria-pressed="%s">%s</button>'
        % (" active" if key == "all" else "", key, "true" if key == "all" else "false", esc(label))
        for key, label in COURSE_CATS
    )

    def tt(v):
        return "—" if not isinstance(v, int) else ("%d°" % v)

    wx_updated = "빌드 시점 %s 기준" % wx.get("updated", "")
    mode_note = " · ".join(x for x in [
        ("체감 " + tt(wx.get("now_feels"))) if isinstance(wx.get("now_feels"), int) else "",
        wx.get("now_cond") or "",
        ("최저 " + tt(wx.get("today_low")) + " / 최고 " + tt(wx.get("today_high")))
        if isinstance(wx.get("today_low"), int) and isinstance(wx.get("today_high"), int) else "",
        ("내일 " + wx["tomorrow_cond"]) if wx.get("tomorrow_cond") else "",
    ] if x)

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__MENU_COUNT__", str(len(MENUS)))
    html = html.replace("__COURSE_COUNT__", str(len(COURSES)))
    html = html.replace("__WX_UPDATED__", esc(wx_updated))
    html = html.replace("__NOW_ICON__", icon(weather_icon_name(wx.get("now_cond"), wx.get("today_pop")), 18))
    html = html.replace("__NOW_TEMP__", tt(wx.get("now_temp")))
    html = html.replace("__NOW_COND__", esc(wx.get("now_cond") or "—"))
    html = html.replace("__NOW_FEELS__", tt(wx.get("now_feels")))
    html = html.replace("__TODAY_LOW__", tt(wx.get("today_low")))
    html = html.replace("__TODAY_HIGH__", tt(wx.get("today_high")))
    html = html.replace("__TODAY_POP__", ("%d%%" % wx["today_pop"]) if isinstance(wx.get("today_pop"), int) else "—")
    html = html.replace("__TODAY_WIND__", ("%dkm/h" % wx["now_wind"]) if isinstance(wx.get("now_wind"), int) else "—")
    html = html.replace("__MODE_TONE__", MODES[mode]["tone"])
    html = html.replace("__MODE_BADGE__", esc("오늘 날씨 · " + MODES[mode]["label"]))
    html = html.replace("__MODE_HEAD__", esc(MODES[mode]["head"]))
    html = html.replace("__MODE_LINE__", esc(MODES[mode]["line"]))
    html = html.replace("__MODE_NOTE__", esc(mode_note))
    html = html.replace("__SIT_CHIPS__", sit_chips)
    html = html.replace("__COMP_CHIPS__", comp_chips)
    html = html.replace("__STYLE_CHIPS__", style_chips)
    html = html.replace("__COURSE_CHIPS__", course_chips)
    html = html.replace("__MENU_CARDS__", "\n          ".join(menu_card(m) for m in MENUS))
    html = html.replace("__COURSE_CARDS__", "\n          ".join(course_card(c, mode) for c in COURSES))
    html = html.replace("__COURSE_META__", esc("%s 기준으로 날씨에 맞는 코스를 위로 보여 줍니다" % MODES[mode]["label"]))
    html = html.replace("__HINT_ICON__", icon("bowl", 26))
    html = html.replace("__PICK_STAR_ICON__", icon("star", 14))
    html = html.replace("__DRAW_ICON__", icon("shuffle", 14))
    html = html.replace("__STAR_PATH__", "'" + ICONS["star"].replace("'", "\\'") + "'")
    html = html.replace("__BUILT_AT__", esc(built_at))
    html = html.replace("__MENUS_JSON__", safe_json_for_script(json.dumps(MENUS, ensure_ascii=False)))
    html = html.replace("__COURSES_JSON__", safe_json_for_script(json.dumps(COURSES, ensure_ascii=False)))
    html = html.replace("__MODES_JSON__", safe_json_for_script(json.dumps(MODES, ensure_ascii=False)))
    html = html.replace("__WX_JSON__", safe_json_for_script(json.dumps(wx, ensure_ascii=False)))
    initial_pool = [m for m in MENUS if mode == "mild" or mode in m["wx"]]
    html = html.replace("__CAND_COUNT__", str(len(initial_pool)))

    # SVG 심볼
    for name in ["sun", "cloud", "cloudsun", "rain", "snow", "wind"]:
        html = html.replace("__SYM_%s__" % name.upper(), ICONS[name])

    with open(PICK_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(ui_shell.apply(html, 'pick')))

    print("-> 'pick.html' 생성 완료 (메뉴 %d종 · 나들이 %d곳, 서울 %s %s, %s~%s, 모드 %s)"
          % (len(MENUS), len(COURSES), tt(wx.get("now_temp")), wx.get("now_cond"),
             tt(wx.get("today_low")), tt(wx.get("today_high")), MODES[mode]["label"]))
    return len(MENUS)


if __name__ == "__main__":
    build()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘의 카드(cards.html) 데이터·구성 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · 덱 2개(컨디션 키워드·1분 디지털 생활) · 덱마다 테마 4개 · 테마마다 카드 정확히 3장
  · 카드 ID 고유, 모든 카드에 그림 키·헤드라인·요약·실천 한 가지가 있는지
  · 컨디션(건강) 카드 전부에 공신력 있는 기관명·페이지 주제·확인일(2026-11-22) 표기
  · 이모지 0 · 그라데이션 0 · 입력 필드(input/textarea) 0 · 인라인 이벤트 핸들러 0
  · KST 날짜 기준 4개 테마가 하루씩 순환하는지(연속 4일이면 네 테마 전부)
  · cards_data.json 과 cards.html 에 심긴 데이터가 일치하는지

실행: python3 tests/test_cards_data.py
"""
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_HTML = os.path.join(BASE_DIR, "cards.html")
CARDS_JSON = os.path.join(BASE_DIR, "cards_data.json")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 19
CHECKED_ON = "2026-11-22"
DECK_IDS = ("condition", "digital")
CREDIBLE_ORGS = ("질병관리청", "국민건강보험공단", "서울아산병원", "대한안과학회",
                 "보건복지부", "개인정보보호위원회", "방송미디어통신위원회", "Google")

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_html():
    with open(CARDS_HTML, encoding="utf-8") as handle:
        src = handle.read()
    match = re.search(r'<script[^>]*id="cardsData"[^>]*>(.*?)</script>', src, re.S)
    if not match:
        raise SystemExit("cards.html 에서 카드 데이터 블록을 찾지 못했습니다.")
    return src, json.loads(match.group(1))


def check_structure(data):
    decks = data.get("decks")
    check("덱 목록", isinstance(decks, list) and len(decks) == 2, len(decks) if isinstance(decks, list) else decks)
    if not isinstance(decks, list):
        return
    check("덱 ID", [d.get("id") for d in decks] == list(DECK_IDS), [d.get("id") for d in decks])
    seen_ids = set()
    for deck in decks:
        themes = deck.get("themes") or []
        check("%s 테마 4개" % deck.get("id"), len(themes) == 4, len(themes))
        check("%s 오늘 테마 지정" % deck.get("id"),
              deck.get("todayTheme") in [t.get("id") for t in themes], deck.get("todayTheme"))
        for theme in themes:
            cards = theme.get("cards") or []
            check("%s/%s 카드 3장" % (deck.get("id"), theme.get("id")), len(cards) == 3, len(cards))
            for card in cards:
                cid = card.get("id") or ""
                check("카드 ID 고유", cid not in seen_ids, cid)
                seen_ids.add(cid)
                check("%s 카드 ID 접두" % deck.get("id"), cid.startswith("cond-" if deck.get("id") == "condition" else "dig-"), cid)
                for field in ("headline", "summary", "action", "art"):
                    check("%s %s 있음" % (cid, field), bool((card.get(field) or "").strip()), field)
                check("%s 헤드라인 길이" % cid, 3 <= len(card.get("headline") or "") <= 24, len(card.get("headline") or ""))
                check("%s 요약 길이" % cid, 10 <= len(card.get("summary") or "") <= 130, len(card.get("summary") or ""))
                check("%s 실천 길이" % cid, 3 <= len(card.get("action") or "") <= 34, len(card.get("action") or ""))
    check("카드 총 24장", len(seen_ids) == 24, len(seen_ids))


def check_health_sources(data):
    for deck in data.get("decks") or []:
        if deck.get("id") != "condition":
            continue
        for theme in deck.get("themes") or []:
            for card in theme.get("cards") or []:
                source = card.get("source") or {}
                org = (source.get("org") or "").strip()
                topic = (source.get("topic") or "").strip()
                checked = (source.get("checked") or "").strip()
                check("%s 건강 카드 출처 기관" % card.get("id"), any(x in org for x in CREDIBLE_ORGS), org)
                check("%s 건강 카드 출처 주제" % card.get("id"), len(topic) >= 2, topic)
                check("%s 건강 카드 확인일" % card.get("id"), checked == CHECKED_ON, checked)


def check_html(src, data):
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("입력 필드 없음", "<input" not in src.lower() and "<textarea" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", src, re.I))
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 cards.html 등록", src.count('href="cards.html"') >= 2, src.count('href="cards.html"'))
    check("현재 페이지 표시", 'data-page="cards"' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("저장 키", "daily_cards_saved_v1" in src)
    check("실천 체크 키", "daily_cards_done_v1" in src)
    check("화이트리스트 필터", "BY_ID[id]" in src)
    arts = {c["art"] for deck in data["decks"] for t in deck["themes"] for c in t["cards"]}
    for key in sorted(arts):
        check("그림 %s 포함" % key, ('"%s":' % key) in src, key)


def check_rotation():
    sys.path.insert(0, BASE_DIR)
    from build_cards_html import build_data
    kst = timezone(timedelta(hours=9))
    seen = {deck: set() for deck in DECK_IDS}
    for offset in range(4):
        day = datetime(2026, 11, 22, 9, 0, tzinfo=kst) + timedelta(days=offset)
        data = build_data(day)
        for deck in data["decks"]:
            seen[deck["id"]].add(deck["todayTheme"])
        for deck in data["decks"]:
            check("%s 테마 순환 일치" % deck["id"], deck["todayTheme"] == deck["themes"][(day.date() - date(1970, 1, 1)).days % 4]["id"])
    for deck, themes in seen.items():
        check("%s 4테마 순환" % deck, themes == {"sleep", "eyes", "neck", "winter"} or themes == {"permission", "notify", "wifi", "backup"}, themes)


def check_json_alignment(data):
    with open(CARDS_JSON, encoding="utf-8") as handle:
        saved = json.load(handle)
    check("cards_data.json = cards.html 데이터", saved.get("decks") == data.get("decks"))


def main():
    src, data = load_html()
    check("빌드 시각", bool(re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2} KST$", data.get("generated", ""))), data.get("generated"))
    check_structure(data)
    check_health_sources(data)
    check_html(src, data)
    check_rotation()
    check_json_alignment(data)
    if failures:
        print("\n실패 %d건" % len(failures))
        return 1
    print("오늘의 카드 데이터 검증 통과 (카드 24장 · 덱 2개 · 테마 8개 · 19페이지 셸)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

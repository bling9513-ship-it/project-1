#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""오늘의 카드(cards.html) 데이터·구성 검증.

빌더와 독립된 판정기로 다음을 확인한다.
  · 덱 2개(컨디션 키워드·1분 디지털 생활) · 덱마다 테마 4개 · 테마마다 카드 정확히 3장
  · 카드 ID 고유, 모든 카드에 그림 키·헤드라인·요약·실천 한 가지가 있는지
  · 컨디션(건강) 카드 전부에 공신력 있는 기관명·페이지 주제·확인일(2026-11-22) 표기
  · 출처가 있는 카드(건강 12장 + 디지털 9장) 전부에 https 원문 링크(source.url) · 허용 호스트
  · cond-winter-2/3 는 확인된 질병관리청 원문(cntnts_sn=2047/2048) · cond-winter-1 은 개인차 반영 문구
  · cond-winter-1 은 질병관리청 「탈수」 원문(cntnts_sn=6551)에 없는 섭취 주기('한 시간에 한 잔씩')를 쓰지 않는다
  · dig-wifi-2 는 '자물쇠' 대신 연결 경고·도메인 확인 문구(그림 키 wifi-warn)
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
SHEET_PAGES = 23
CHECKED_ON = "2026-11-22"
DECK_IDS = ("condition", "digital")
CREDIBLE_ORGS = ("질병관리청", "국민건강보험공단", "서울아산병원", "대한안과학회", "미국안과학회",
                 "보건복지부", "국립정신건강센터", "개인정보보호위원회", "방송미디어통신위원회", "Google")
SOURCE_URL_HOSTS = ("health.kdca.go.kr", "www.mentalhealth.go.kr", "www.aao.org",
                    "www.ophthalmology.org", "www.amc.seoul.kr", "www.kmcc.go.kr",
                    "m.blog.naver.com", "support.google.com")
SOURCE_CARDS = 21          # 건강 12장 + 출처가 있는 디지털 9장
KDCA_WINTER_URLS = ("cntnts_sn=2047", "cntnts_sn=2048")

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


def all_cards(data):
    for deck in data.get("decks") or []:
        for theme in deck.get("themes") or []:
            for card in theme.get("cards") or []:
                yield card


def source_url(card):
    return ((card.get("source") or {}).get("url") or "").strip()


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
                check("%s 건강 카드 원문 링크" % card.get("id"), source_url(card).startswith("https://"), source_url(card))


def check_source_urls(data):
    seen = 0
    for card in all_cards(data):
        source = card.get("source")
        if not source:
            continue
        seen += 1
        url = source_url(card)
        cid = card.get("id")
        check("%s 원문 링크 https" % cid, url.startswith("https://"), url)
        check("%s 원문 링크 공백 없음" % cid, " " not in url and "\n" not in url, url)
        host = re.sub(r"^https://([^/?#]+).*$", r"\1", url)
        check("%s 원문 링크 허용 호스트" % cid, host in SOURCE_URL_HOSTS, host)
        check("%s 원문 링크 스킴 변조 없음" % cid, url.lower().startswith("https://") and "javascript" not in url.lower(), url)
    check("출처 있는 카드 %d장" % SOURCE_CARDS, seen == SOURCE_CARDS, seen)
    bare = [c["id"] for c in all_cards(data) if not c.get("source")]
    check("출처 없는 카드는 생활 팁 3장", sorted(bare) == ["dig-notify-1", "dig-notify-2", "dig-notify-3"], bare)


def check_fact_fixes(data):
    by_id = {c["id"]: c for c in all_cards(data)}

    # 겨울 습도·환기는 확인된 질병관리청 원문(대설 2047 · 한파 2048)에 연결한다.
    for cid in ("cond-winter-2", "cond-winter-3"):
        url = source_url(by_id[cid])
        check("%s 확인된 KDCA 원문" % cid, any(t in url for t in KDCA_WINTER_URLS), url)
        check("%s KDCA 기관명" % cid, "질병관리청" in (by_id[cid]["source"].get("org") or ""), by_id[cid]["source"].get("org"))

    # 환기: 원문에 있는 수치(하루 3번 · 10~30분)를 유지한다.
    vent = by_id["cond-winter-3"]
    check("cond-winter-3 환기 횟수 유지", "세 번" in vent["summary"] or "3번" in vent["summary"], vent["summary"])
    check("cond-winter-3 환기 시간 유지", "10~30분" in vent["summary"], vent["summary"])

    # 수분: '1.5~2L면 충분' 단정 대신 개인차를 먼저 말한다.
    water = by_id["cond-winter-1"]
    check("cond-winter-1 단정 문구 없음", "1.5~2L면 충분" not in water["summary"], water["summary"])
    check("cond-winter-1 개인차 반영", "달라" in water["summary"], water["summary"])
    check("cond-winter-1 개인차 요인",
          any(x in water["summary"] for x in ("활동량", "환경", "건강 상태")), water["summary"])
    check("cond-winter-1 원문 링크", "cntnts_sn=6551" in source_url(water), source_url(water))
    # 원문에 없는 섭취 주기('한 시간에 한 잔씩' · '한 시간마다')는 카드 어디에도 남기지 않는다.
    for field in ("headline", "summary", "action"):
        check("cond-winter-1 %s 미확인 주기 없음" % field,
              "한 시간" not in (water.get(field) or "") and "한 잔씩" not in (water.get(field) or ""),
              water.get(field))
    check("cond-winter-1 원문 수치 유지", "1.5~2L" in water["summary"], water["summary"])
    check("cond-winter-1 갈증 전 섭취 안내", "갈증" in water["summary"], water["summary"])

    # 공용 와이파이: 브라우저 자물쇠 대신 연결 경고·도메인 확인.
    wifi = by_id["dig-wifi-2"]
    for field in ("headline", "summary", "action"):
        check("dig-wifi-2 %s 자물쇠 없음" % field, "자물쇠" not in (wifi.get(field) or ""), wifi.get(field))
    check("dig-wifi-2 경고 문구", "안전하지 않음" in wifi["summary"], wifi["summary"])
    check("dig-wifi-2 도메인 확인 문구", "주소" in wifi["summary"], wifi["summary"])
    check("dig-wifi-2 그림 키", wifi["art"] == "wifi-warn", wifi["art"])


def check_html(src, data):
    check("이모지 0개", not EMOJI_RE.search(src))
    check("그라데이션 0개", "gradient" not in src.lower())
    check("입력 필드 없음", "<input" not in src.lower() and "<textarea" not in src.lower())
    check("인라인 이벤트 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", src, re.I))
    # 그림 라벨에도 원문에 없는 섭취 주기를 남기지 않는다.('한 잔씩'/'한 시간마다')
    check("수분 그림 라벨 미확인 주기 없음", "한 잔씩" not in src and "한 시간마다" not in src,
          src[src.find("winter-water"):src.find("winter-humid")][-400:])
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 cards.html 등록", src.count('href="cards.html"') >= 2, src.count('href="cards.html"'))
    check("현재 페이지 표시", 'data-page="cards"' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("저장 키", "daily_cards_saved_v1" in src)
    check("실천 체크 키", "daily_cards_done_v1" in src)
    check("화이트리스트 필터", "BY_ID[id]" in src)
    check("원문 링크 클래스", "cd-source-link" in src)
    check("원문 링크 새 창 보호", "noopener noreferrer" in src)
    check("전체 카드 칩", 'data-deck="all"' in src and "전체 카드" in src)
    check("전체 카드 목록", 'id="cdAllList"' in src and "cd-allrow" in src)
    check("자물쇠 표현 제거", "자물쇠" not in src and "wifi-lock" not in src)
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
    check_source_urls(data)
    check_fact_fixes(data)
    check_html(src, data)
    check_rotation()
    check_json_alignment(data)
    if failures:
        print("\n실패 %d건" % len(failures))
        return 1
    print("오늘의 카드 데이터 검증 통과 (카드 24장 · 덱 2개 · 테마 8개 · 23페이지 셸)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

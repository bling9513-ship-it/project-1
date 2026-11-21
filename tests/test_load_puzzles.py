#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""한 번 더 싣기(load.html) 데이터 검증.

페이지에 심긴 상자 시퀀스를 읽어, 빌더와 독립된 규칙 판정기로
'표기 무게 범위 안에 실측이 있는지' · '한도/균형을 넘지 않는 최고 점수' ·
'별 기준이 실현 가능한지'를 전수 확인한다.

실행: python3 tests/test_load_puzzles.py
"""
import datetime
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOAD_HTML = os.path.join(BASE_DIR, "load.html")
EMOJI_RE = re.compile("[\\U0001F000-\\U0001FAFF\\u2600-\\u27BF\\uFE0F\\u2B00-\\u2BFF]")
LIMIT = 100
TILT = 28
TRIPS = 5
TIERS = [(0.90, 1.5), (0.78, 1.25), (0.62, 1.0), (0.0, 0.75)]

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_data():
    src = open(LOAD_HTML, encoding="utf-8").read()
    match = re.search(r'<script[^>]*id="loadData"[^>]*>(.*?)</script>', src, re.S)
    if not match:
        raise SystemExit("load.html 에서 상자 데이터 블록을 찾지 못했습니다.")
    return src, json.loads(match.group(1))


def balance_mult(ratio):
    for minimum, mult in TIERS:
        if ratio >= minimum:
            return mult
    return TIERS[-1][1]


def streak_mult(streak):
    return round(1 + min(streak, 5) * 0.1, 2)


def best_trip(boxes):
    """실측 무게를 다 아는 상태의 회차 최고 점수(배율 제외)."""
    best = 0.0
    n = len(boxes)

    def walk(index, left, right, score, count):
        nonlocal best
        if count > 0:
            total = left + right
            best = max(best, score * balance_mult(1 - abs(left - right) / total))
        if index >= n:
            return
        kg = boxes[index]["kg"]
        point = boxes[index]["score"]
        if left + kg + right <= LIMIT and abs(left + kg - right) <= TILT:
            walk(index + 1, left + kg, right, score + point, count + 1)
        if left + right + kg <= LIMIT and abs(left - right - kg) <= TILT:
            walk(index + 1, left, right + kg, score + point, count + 1)

    walk(0, 0, 0, 0, 0)
    return best


def first_load_is_safe(box):
    """첫 상자는 어떤 실측이어도 한도·균형을 넘지 않아야 한다(최소 1개는 실을 수 있음)."""
    return box["hi"] <= LIMIT and box["hi"] <= TILT


def validate(challenge, group):
    cid = challenge["id"]
    label = "%s %s" % (group, cid)
    check("%s 제목" % label, bool(str(challenge.get("title") or "").strip()), challenge.get("title"))
    check("%s 회차 수" % label, len(challenge["batches"]) == TRIPS, len(challenge["batches"]))
    check("%s 한도" % label, challenge["limit"] == LIMIT, challenge["limit"])
    check("%s 균형 허용" % label, challenge["tilt"] == TILT, challenge["tilt"])

    total_best = 0.0
    seen = set()
    for trip_index, boxes in enumerate(challenge["batches"], start=1):
        where = "%s %d회차" % (label, trip_index)
        check("%s 상자 4~8개" % where, 4 <= len(boxes) <= 8, len(boxes))
        for box in boxes:
            check("%s 상자 id 중복 없음" % where, box["id"] not in seen, box["id"])
            seen.add(box["id"])
            check("%s %s 이름" % (where, box["id"]), bool(str(box.get("name") or "").strip()), box.get("name"))
            check("%s %s 표기 범위" % (where, box["id"]), box["lo"] <= box["kg"] <= box["hi"],
                  "%s/%s/%s" % (box["lo"], box["kg"], box["hi"]))
            check("%s %s 표기 폭 2~9kg" % (where, box["id"]), 2 <= box["hi"] - box["lo"] <= 9,
                  box["hi"] - box["lo"])
            check("%s %s 무게 8~28kg" % (where, box["id"]), 8 <= box["kg"] <= 28, box["kg"])
            check("%s %s 점수 5~60" % (where, box["id"]), 5 <= box["score"] <= 60, box["score"])
        check("%s 첫 상자 안전" % where, first_load_is_safe(boxes[0]), boxes[0])
        check("%s 전부 실을 수 없음" % where, sum(box["kg"] for box in boxes) > LIMIT,
              sum(box["kg"] for box in boxes))
        score = best_trip(boxes)
        check("%s 해답 존재" % where, score > 0, score)
        check("%s 회차 최고 점수 기록" % where,
              abs(challenge["tripBest"][trip_index - 1] - round(score * streak_mult(trip_index - 1))) <= 1,
              "%s vs %s" % (challenge["tripBest"][trip_index - 1], round(score * streak_mult(trip_index - 1))))
        total_best += score * streak_mult(trip_index - 1)

    optimal = int(round(total_best))
    check("%s 최적해 표기" % label, abs(challenge["optimal"] - optimal) <= 1,
          "%s vs %s" % (challenge["optimal"], optimal))
    stars = challenge["stars"]
    check("%s 별 3단계" % label, len(stars) == 3, stars)
    check("%s 별 단조 증가" % label, stars[0] < stars[1] < stars[2], stars)
    check("%s 1별 목표 양수" % label, stars[0] > 0, stars)
    check("%s 3별 실현 가능" % label, stars[2] <= optimal, "%s > %s" % (stars[2], optimal))
    check("%s 목표 = 1별" % label, challenge["goal"] == stars[0], "%s/%s" % (challenge["goal"], stars[0]))
    check("%s 1별 난이도" % label, stars[0] <= round(optimal * 0.8), "%s/%s" % (stars[0], optimal))
    check("%s 안내 문구" % label, bool(str(challenge.get("note") or "").strip()))


def main():
    if not os.path.exists(LOAD_HTML):
        raise SystemExit("load.html 이 없습니다. build_load_html.py 를 먼저 실행하세요.")
    src, data = load_data()

    rules = data["rules"]
    check("공통 한도", rules["limit"] == LIMIT, rules["limit"])
    check("공통 균형", rules["tilt"] == TILT, rules["tilt"])
    check("공통 회차", rules["trips"] == TRIPS, rules["trips"])
    check("균형 배율 단계", [tuple((t["min"], t["mult"])) for t in rules["tiers"]] == TIERS, rules["tiers"])

    daily = data["daily"]
    practice = data["practice"]
    print("== 일일 챌린지 ==")
    check("일일 14일치", len(daily) == 14, len(daily))
    check("일일 id 중복 없음", len({c["id"] for c in daily}) == len(daily))
    check("일일 제목 중복 없음", len({c["title"] for c in daily}) == len(daily))
    for challenge in daily:
        validate(challenge, "일일")
    signatures = {json.dumps([box["id"] for trip in c["batches"] for box in trip]) for c in daily}
    check("일일 14일 모두 다른 순서", len(signatures) == len(daily), len(signatures))

    base = datetime.date(2026, 1, 1)
    ordinals = {(base + datetime.timedelta(days=i)).toordinal() - 719163 for i in range(len(daily))}
    check("날짜 순환으로 14일 전체 도달", {value % len(daily) for value in ordinals} == set(range(len(daily))))

    print("== 폴백 ==")
    fallback = data.get("fallback")
    check("폴백 존재", isinstance(fallback, dict), type(fallback).__name__)
    if isinstance(fallback, dict):
        validate(fallback, "폴백")
        check("폴백 id", fallback["id"] == "fallback", fallback["id"])
        check("폴백은 일일 풀에 없음", fallback["id"] not in {c["id"] for c in daily})

    print("== 연습 스테이지 ==")
    check("연습 9판", len(practice) == 9, len(practice))
    check("연습 id 중복 없음", len({c["id"] for c in practice}) == len(practice))
    levels = [c["level"] for c in practice]
    check("난이도 3단계", set(levels) == {"beginner", "mid", "adv"}, sorted(set(levels)))
    for level in ("beginner", "mid", "adv"):
        check("%s 3판" % level, levels.count(level) == 3, levels.count(level))
    for challenge in practice:
        validate(challenge, "연습")

    print("== 표기 · 통합 ==")
    check("이모지 없음", not EMOJI_RE.search(src))
    check("그라데이션 없음", "gradient" not in src.lower())
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 22개", sheet_links == 22, sheet_links)
    check("내비게이션에 load.html 등록", src.count('href="load.html"') >= 2, src.count('href="load.html"'))
    check("게임 하단 탭이 게임 목록 시트로 열림", 'id="iaGameBtn"' in src and 'data-sheet-target="iaSheetGroupGame"' in src)
    check("미니게임 소제목", 'ia-sheet-sub">미니게임' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("인라인 on* 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", src, re.I))
    check("localStorage 키", "load_cart_stats_v1" in src)
    check("가이드 저장 키", "load_demo_seen_v1" in src)
    check("게임 방법 3단계", src.count('class="gg-step" data-step') == 3, src.count('class="gg-step" data-step'))
    check("무게 게이지", 'id="gaugeFill"' in src and 'id="tiltFill"' in src)
    check("상자 싣기 버튼", 'id="loadLeft"' in src and 'id="loadRight"' in src)
    check("배송 버튼", 'id="shipBtn"' in src)
    check("다음 상자 미리보기", 'id="nextCard"' in src and 'id="nextRange"' in src)
    check("위험 표시", 'id="riskLeft"' in src and 'id="riskRight"' in src)

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("\n모든 데이터 검증 통과: 일일 %d일치 · 연습 %d판 · 폴백 1판 "
          "(표기 범위 안 실측 · 한도/균형 최적해 · 별 기준 실현 가능)" % (len(daily), len(practice)))


if __name__ == "__main__":
    main()

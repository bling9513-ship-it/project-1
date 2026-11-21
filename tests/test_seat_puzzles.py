#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""막차 자리 배치(seat.html) 퍼즐 검증.

페이지에 실린 좌석·승객·정답 데이터를 읽어, 독립 구현한 규칙 판정기와
이동 계획기로 '해답이 실제로 par 수 이내에 도달 가능한지'를 전수 확인한다.
빌더 내부 함수를 재사용하지 않으므로 데이터 자체를 검증한다.

실행: python3 tests/test_seat_puzzles.py
"""
import datetime
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAT_HTML = os.path.join(BASE_DIR, "seat.html")
EMOJI_RE = re.compile("[\\U0001F000-\\U0001FAFF\\u2600-\\u27BF\\uFE0F\\u2B00-\\u2BFF]")
ROWS = 4
COLS = 4
SEAT_COUNT = ROWS * COLS

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_data():
    src = open(SEAT_HTML, encoding="utf-8").read()
    match = re.search(r'<script[^>]*id="seatData"[^>]*>(.*?)</script>', src, re.S)
    if not match:
        raise SystemExit("seat.html 에서 좌석 데이터 블록을 찾지 못했습니다.")
    return src, json.loads(match.group(1))


def has_tag(seat, tag):
    return tag in seat["tags"]


def contiguous(seats):
    rows = {s // COLS for s in seats}
    if len(rows) != 1:
        return False
    cols = sorted(s % COLS for s in seats)
    return cols[-1] - cols[0] == len(cols) - 1


def solved(arr, passengers, groups, seats):
    seat_of = {}
    for i, pid in enumerate(arr):
        if pid:
            seat_of[pid] = i
    for p in passengers:
        if p["id"] not in seat_of:
            return False
        for tag in p["conds"]:
            if not has_tag(seats[seat_of[p["id"]]], tag):
                return False
    for group in groups:
        placed = [seat_of.get(m) for m in group]
        if any(s is None for s in placed):
            return False
        if not contiguous(placed):
            return False
    return True


def plan(start, solution):
    """게임과 같은 규칙(대기 승객 탭 → 좌석 탭 / 앉은 승객 탭 → 좌석 탭)으로 이동 계획을 만든다."""
    seats = list(start)
    target = {pid: i for i, pid in enumerate(solution) if pid}
    steps = []
    guard = 0
    while seats != solution and guard < 40:
        guard += 1
        moved = False
        waiting = [pid for pid in target if pid not in seats]
        for pid in waiting:
            seat = target[pid]
            if seats[seat] is None:
                steps.append(("wait", pid))
                steps.append(("seat", seat))
                seats[seat] = pid
                moved = True
                break
        if moved:
            continue
        for i, pid in enumerate(seats):
            if not pid:
                continue
            seat = target[pid]
            if seat != i and seats[seat] is None:
                steps.append(("seat", i))
                steps.append(("seat", seat))
                seats[seat] = pid
                seats[i] = None
                moved = True
                break
        if moved:
            continue
        for i, pid in enumerate(seats):
            if not pid:
                continue
            j = target[pid]
            other = seats[j]
            if other and i != j and target.get(other) == i:
                steps.append(("seat", i))
                steps.append(("seat", j))
                seats[i], seats[j] = seats[j], seats[i]
                moved = True
                break
        if moved:
            continue
        for i, pid in enumerate(seats):
            if not pid:
                continue
            j = target[pid]
            if j != i and seats[j] is not None:
                steps.append(("seat", i))
                steps.append(("seat", j))
                seats[i], seats[j] = seats[j], seats[i]
                moved = True
                break
        if not moved:
            break
    return steps, seats


def validate(puzzle, seats, tags, group_label):
    pid = puzzle["id"]
    label = "%s %s" % (group_label, pid)
    passengers = puzzle["passengers"]
    groups = puzzle.get("groups") or []
    start = puzzle["start"]
    solution = puzzle["solution"]
    ids = [p["id"] for p in passengers]

    check("%s 인원 4~9명" % label, 4 <= len(passengers) <= 9, len(passengers))
    check("%s 승객 id 중복 없음" % label, len(set(ids)) == len(ids))
    check("%s 이름 채움" % label, all(p.get("name") and p.get("short") for p in passengers))
    for p in passengers:
        check("%s %s 조건 태그" % (label, p["id"]),
              all(c in tags for c in p["conds"]), p["conds"])
        check("%s %s 조건 2개 이하" % (label, p["id"]), len(p["conds"]) <= 2)
    for group in groups:
        check("%s 일행 2~3명" % label, 2 <= len(group) <= 3, group)
        check("%s 일행 구성원 존재" % label, set(group) <= set(ids), group)
        for member in group:
            member_info = next((p for p in passengers if p["id"] == member), {})
            check("%s 일행 표시" % label, member_info.get("together") is True, member)

    check("%s 좌석 16칸" % label, len(start) == SEAT_COUNT and len(solution) == SEAT_COUNT)
    check("%s 시작 배치 중복 없음" % label,
          len([x for x in start if x]) == len({x for x in start if x}))
    check("%s 정답 배치 중복 없음" % label,
          len([x for x in solution if x]) == len({x for x in solution if x}))
    check("%s 정답에 전원 배치" % label, {x for x in solution if x} == set(ids))
    check("%s 시작은 승객 일부만 배치" % label, {x for x in start if x} <= set(ids))
    check("%s 대기 승객 1명 이상" % label, len([x for x in start if x]) < len(ids))

    check("%s 정답이 조건 충족" % label, solved(solution, passengers, groups, seats))
    check("%s 시작은 미완성" % label, not solved(start, passengers, groups, seats))

    par = puzzle["par"]
    check("%s par 1~3" % label, isinstance(par, int) and 1 <= par <= 3, par)
    steps, final = plan(start, solution)
    moves = len(steps) // 2
    check("%s 탭 계획이 정답 도달" % label, final == solution)
    check("%s par 이내 해답 존재" % label, moves <= par, "%d수 > %d수" % (moves, par))
    check("%s par 가 계획과 일치" % label, moves == par, "%d수 != %d수" % (moves, par))
    check("%s 안내 문구" % label, bool(str(puzzle.get("note") or "").strip()))
    check("%s 제목" % label, bool(str(puzzle.get("title") or "").strip()))


def main():
    if not os.path.exists(SEAT_HTML):
        raise SystemExit("seat.html 이 없습니다. build_seat_html.py 를 먼저 실행하세요.")
    src, data = load_data()

    seats = data["seats"]
    tags = [t["key"] for t in data["tags"]]
    check("좌석 16칸", len(seats) == SEAT_COUNT, len(seats))
    check("좌석 라벨 중복 없음", len({s["label"] for s in seats}) == len(seats))
    for tag, expected in (("window", 8), ("aisle", 8), ("door", 8), ("quiet", 8), ("senior", 4)):
        count = len([s for s in seats if tag in s["tags"]])
        check("%s 좌석 %d칸" % (tag, expected), count == expected, count)
    check("출입문 1·4행", all("door" in s["tags"] for s in seats if s["row"] in (1, 4)))
    check("조용한 칸 2·3행", all("quiet" in s["tags"] for s in seats if s["row"] in (2, 3)))
    check("노약자석 4칸", len([s for s in seats if "senior" in s["tags"]]) == 4)

    daily = data["daily"]
    practice = data["practice"]
    print("== 오늘의 막차 풀 ==")
    check("일일 14~21판", 14 <= len(daily) <= 21, len(daily))
    check("일일 id 중복 없음", len({p["id"] for p in daily}) == len(daily))
    for puzzle in daily:
        validate(puzzle, seats, tags, "일일")

    signatures = {(tuple(p["start"]), tuple(p["solution"])) for p in daily}
    check("일일 퍼즐 모두 다름", len(signatures) == len(daily), "%d/%d" % (len(signatures), len(daily)))

    base = datetime.date(2026, 1, 1)
    seen = {(base + datetime.timedelta(days=i)).toordinal() - 719163 for i in range(len(daily))}
    check("날짜 순환으로 전체 풀 도달", {value % len(daily) for value in seen} == set(range(len(daily))))

    print("== 연습 스테이지 ==")
    check("연습 10~15판", 10 <= len(practice) <= 15, len(practice))
    check("연습 id 중복 없음", len({p["id"] for p in practice}) == len(practice))
    levels = [p["level"] for p in practice]
    check("난이도 3단계", set(levels) == {"beginner", "mid", "adv"}, sorted(set(levels)))
    for level in ("beginner", "mid", "adv"):
        check("%s 3판 이상" % level, levels.count(level) >= 3, levels.count(level))
    for puzzle in practice:
        validate(puzzle, seats, tags, "연습")

    print("== 표기 ==")
    check("이모지 없음", not EMOJI_RE.search(src))
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 17개", sheet_links == 17, sheet_links)
    check("내비게이션에 seat.html 등록", 'href="seat.html"' in src)
    check("게임 소제목 챌린지·미니게임", 'ia-sheet-sub">챌린지' in src and 'ia-sheet-sub">미니게임' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1)
    check("인라인 on* 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", src, re.I))
    check("localStorage 키", "seat_puzzle_stats_v1" in src)

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("\n모든 퍼즐 검증 통과: 일일 %d판 · 연습 %d판 (정답 조건 충족 · par 이내 이동 계획 확인)"
          % (len(daily), len(practice)))


if __name__ == "__main__":
    main()

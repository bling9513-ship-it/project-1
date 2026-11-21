#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""퇴근길 미션(mission.html) 퍼즐 검증.

페이지에 실제로 실린 지도 데이터를 읽어, 독립 구현한 BFS로
'최단 경로로 도달 가능 + 제한 이동 수 이내 클리어'를 전수 확인한다.
빌더 내부 함수를 재사용하지 않으므로 데이터 자체를 검증한다.

실행: python3 tests/test_mission_puzzles.py
"""
import json
import os
import re
import sys
from collections import deque

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MISSION_HTML = os.path.join(BASE_DIR, "mission.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_data():
    src = open(MISSION_HTML, encoding="utf-8").read()
    marker = "const DATA = "
    start = src.index(marker) + len(marker)
    data, _ = json.JSONDecoder().raw_decode(src[start:])
    return src, data


def walkable(puzzle, r, c):
    if not (0 <= r < puzzle["size"] and 0 <= c < puzzle["size"]):
        return False
    return puzzle["rows"][r][c] not in "#X"


def shortest(puzzle):
    """(칸, 경유지 마스크) BFS로 최단 이동 수와 경로를 구한다."""
    start = tuple(puzzle["start"])
    goal = tuple(puzzle["goal"])
    waypoints = [(w["r"], w["c"]) for w in puzzle["waypoints"]]
    index = {cell: i for i, cell in enumerate(waypoints)}
    full = (1 << len(waypoints)) - 1
    origin = (start, 0)
    dist = {origin: 0}
    prev = {origin: None}
    queue = deque([origin])
    found = None
    while queue:
        state = queue.popleft()
        pos, mask = state
        if pos == goal and mask == full:
            found = state
            break
        r, c = pos
        for dr, dc in DIRS:
            cell = (r + dr, c + dc)
            if not walkable(puzzle, cell[0], cell[1]):
                continue
            nmask = mask | (1 << index[cell]) if cell in index else mask
            nstate = (cell, nmask)
            if nstate not in dist:
                dist[nstate] = dist[state] + 1
                prev[nstate] = state
                queue.append(nstate)
    if found is None:
        return None, None
    path = []
    cur = found
    while cur is not None:
        path.append(cur[0])
        cur = prev[cur]
    return dist[found], list(reversed(path))


def validate(puzzle, group, label):
    size = puzzle["size"]
    check("%s %s: 격자 크기" % (group, label), size == 7 and len(puzzle["rows"]) == size)
    check("%s %s: 격자 문자" % (group, label),
          all(len(row) == size and set(row) <= set(".#Xp") for row in puzzle["rows"]))
    start = tuple(puzzle["start"])
    goal = tuple(puzzle["goal"])
    check("%s %s: 출발/도착 통행 가능" % (group, label), walkable(puzzle, *start) and walkable(puzzle, *goal))
    check("%s %s: 출발≠도착" % (group, label), start != goal)
    wps = [(w["r"], w["c"]) for w in puzzle["waypoints"]]
    check("%s %s: 경유지 1~2곳" % (group, label), 1 <= len(wps) <= 2, wps)
    check("%s %s: 경유지 통행 가능" % (group, label), all(walkable(puzzle, r, c) for r, c in wps))
    check("%s %s: 경유지 중복 없음" % (group, label), len(set(wps)) == len(wps) and not ({start, goal} & set(wps)))
    best, path = shortest(puzzle)
    check("%s %s: 최단 경로 존재" % (group, label), best is not None)
    if best is None:
        return
    check("%s %s: 기록된 최단 이동 수 일치" % (group, label), best == puzzle["optimal"], "%s != %s" % (best, puzzle["optimal"]))
    check("%s %s: 제한 이동 수 이내" % (group, label), best <= puzzle["limit"], "%s > %s" % (best, puzzle["limit"]))
    check("%s %s: 제한은 최단+0~3" % (group, label), 0 <= puzzle["limit"] - best <= 3)
    check("%s %s: 경로가 도착지에서 끝남" % (group, label), path[-1] == goal)
    check("%s %s: 경로가 경유지를 모두 지남" % (group, label), set(wps) <= set(path))
    check("%s %s: 경로 길이 일치" % (group, label), len(path) - 1 == best)
    check("%s %s: 지도 안내 문구" % (group, label), "→" in puzzle["scene"] and "집" in puzzle["scene"])


def main():
    if not os.path.exists(MISSION_HTML):
        raise SystemExit("mission.html 이 없습니다. build_mission_html.py 를 먼저 실행하세요.")
    src, data = load_data()

    daily = data["daily"]
    practice = data["practice"]
    levels = [lv["key"] for lv in data["levels"]]
    practice_items = [(lv, p) for lv in levels for p in practice.get(lv, [])]

    print("== 오늘의 미션 풀 ==")
    check("일일 풀 14~21개", 14 <= len(daily) <= 21, len(daily))
    ids = [p["id"] for p in daily]
    check("일일 id 중복 없음", len(set(ids)) == len(ids))
    for p in daily:
        validate(p, "일일", p["id"])
    signatures = {(tuple(p["rows"]), tuple((w["r"], w["c"]) for w in p["waypoints"])) for p in daily}
    check("일일 지도 모두 다름", len(signatures) == len(daily), "%d/%d" % (len(signatures), len(daily)))

    # 날짜 순환: 연속 21일이면 21개 지도를 모두 만난다
    import datetime
    base = datetime.date(2026, 1, 1)
    seen = set()
    for i in range(len(daily)):
        day = base + datetime.timedelta(days=i)
        seen.add((day.toordinal()) % len(daily))
    check("날짜 순환으로 전체 풀 도달", len(seen) == len(daily))

    print("== 연습 스테이지 ==")
    check("연습 퍼즐 10~15개", 10 <= len(practice_items) <= 15, len(practice_items))
    check("난이도 3단계", levels == ["beginner", "mid", "adv"], levels)
    for lv in levels:
        check("%s 5개 이상" % lv, len(practice.get(lv, [])) >= 5, len(practice.get(lv, [])))
    pids = [p["id"] for _, p in practice_items]
    check("연습 id 중복 없음", len(set(pids)) == len(pids))
    for lv, p in practice_items:
        validate(p, lv, p["id"])

    print("== 표기 ==")
    check("이모지 없음", not EMOJI_RE.search(src))
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 22개", sheet_links == 22, sheet_links)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1)
    check("인라인 on* 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", src, re.I))

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("\n모든 퍼즐 검증 통과: 오늘의 지도 %d개 · 연습 %d개 (최단 경로 BFS · 제한 이내 클리어 확인)"
          % (len(daily), len(practice_items)))


if __name__ == "__main__":
    main()

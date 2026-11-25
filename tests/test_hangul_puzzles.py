#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""한글 한 칸 변신(hangul.html) 데이터 검증.

페이지에 심긴 사전·퍼즐 데이터를 읽어, 빌더와 독립된 판정기로
'두 음절 한글 단어인지' · '한 음절만 바뀌는 이동만 있는지' ·
'모든 판의 par 가 실제 최단 거리인지' · '최단 경로의 모든 단어가 사전에 있는지'를
전수 확인한다.

실행: python3 tests/test_hangul_puzzles.py
"""
import json
import os
import re
import sys
from collections import deque

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANGUL_HTML = os.path.join(BASE_DIR, "hangul.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 30

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def load_data():
    src = open(HANGUL_HTML, encoding="utf-8").read()
    match = re.search(r'<script[^>]*id="hangulData"[^>]*>(.*?)</script>', src, re.S)
    if not match:
        raise SystemExit("hangul.html 에서 퍼즐 데이터 블록을 찾지 못했습니다.")
    return src, json.loads(match.group(1))


def is_two_syllable_word(word):
    if not isinstance(word, str) or len(word) != 2:
        return False
    return all(0xAC00 <= ord(ch) <= 0xD7A3 for ch in word)


def one_syllable_apart(left, right):
    if len(left) != len(right):
        return False
    return sum(1 for a, b in zip(left, right) if a != b) == 1


def build_graph(words):
    graph = {word: set() for word in words}
    for index in range(2):
        buckets = {}
        for word in words:
            buckets.setdefault(word[index], []).append(word)
        for group in buckets.values():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    if one_syllable_apart(group[i], group[j]):
                        graph[group[i]].add(group[j])
                        graph[group[j]].add(group[i])
    return graph


def shortest_path(graph, start, goal):
    if start == goal:
        return [start]
    seen = {start: 0}
    previous = {}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in sorted(graph[current]):
            if nxt in seen:
                continue
            seen[nxt] = seen[current] + 1
            previous[nxt] = current
            if nxt == goal:
                path = [goal]
                while path[-1] != start:
                    path.append(previous[path[-1]])
                return path[::-1]
            queue.append(nxt)
    return None


def main():
    src, data = load_data()

    print("== 사전 ==")
    words = data.get("words") or []
    check("사전 존재", len(words) >= 400, len(words))
    check("사전 중복 없음", len(set(words)) == len(words), len(words) - len(set(words)))
    bad = [word for word in words if not is_two_syllable_word(word)]
    check("모든 단어가 두 음절 한글", not bad, bad[:5])
    graph = build_graph(words)
    isolated = [word for word in words if not graph[word]]
    check("연결된 단어 우세", len(isolated) < len(words) * 0.2,
          "%d/%d 고립" % (len(isolated), len(words)))

    # 글자 모드 팔레트가 사전의 모든 음절을 덮는지 (덮지 못하면 풀 수 없는 판이 생긴다)
    groups = data.get("syllableGroups") or {}
    flat = [syllable for group in groups.values() for syllable in group]
    used = {ch for word in words for ch in word}
    check("글자 팔레트가 사전 음절 전체를 덮음", used <= set(flat), sorted(used - set(flat))[:8])
    check("글자 팔레트 중복 없음", len(flat) == len(set(flat)), len(flat) - len(set(flat)))

    daily = data.get("daily") or []
    practice = data.get("practice") or []
    print("== 퍼즐 ==")
    check("일일 14판", len(daily) == 14, len(daily))
    check("연습 12판", len(practice) == 12, len(practice))
    check("id 중복 없음", len({p["id"] for p in daily + practice}) == len(daily) + len(practice))
    pairs = [(p["start"], p["goal"]) for p in daily + practice]
    check("시작·목표 쌍 중복 없음", len(set(pairs)) == len(pairs), len(pairs) - len(set(pairs)))

    levels = {}
    for puzzle in practice:
        levels[puzzle["level"]] = levels.get(puzzle["level"], 0) + 1
    check("연습 난이도 3단계", set(levels) == {"입문", "중급", "고급"}, sorted(levels))
    for level in ("입문", "중급", "고급"):
        check("%s 4판" % level, levels.get(level) == 4, levels.get(level))

    for puzzle in daily + practice:
        label = puzzle["id"]
        start, goal = puzzle["start"], puzzle["goal"]
        check("%s 시작·목표 사전 수록" % label, start in graph and goal in graph, "%s %s" % (start, goal))
        if start not in graph or goal not in graph:
            continue
        check("%s 시작≠목표" % label, start != goal)
        path = shortest_path(graph, start, goal)
        check("%s 경로 존재" % label, path is not None)
        if not path:
            continue
        check("%s par 일치" % label, puzzle["par"] == len(path) - 1,
              "데이터 %s vs 계산 %s" % (puzzle["par"], len(path) - 1))
        check("%s par 2수 이상" % label, puzzle["par"] >= 2, puzzle["par"])
        check("%s 라이벌 기록 양수" % label, puzzle["rivalMs"] > 0, puzzle["rivalMs"])
        steps_ok = all(one_syllable_apart(a, b) for a, b in zip(path, path[1:]))
        check("%s 경로가 한 음절 이동" % label, steps_ok, path)
        check("%s 경로 단어 모두 사전 수록" % label, all(word in graph for word in path), path)

    # 일일 14판이 날짜 순환으로 모두 열리는지
    check("일일 제목 모두 있음", all(p.get("title") for p in daily))
    check("연습 제목 모두 있음", all(p.get("title") for p in practice))
    check("par 분포 2~7", {p["par"] for p in daily + practice} <= {2, 3, 4, 5, 6, 7},
          sorted({p["par"] for p in daily + practice}))

    print("== 표기 · 통합 ==")
    check("이모지 없음", not EMOJI_RE.search(src))
    check("그라데이션 없음", "gradient" not in src.lower())
    check("공통 셸 하단 탭 바", src.count('class="ia-tabbar"') == 1, src.count('class="ia-tabbar"'))
    sheet_links = src.count('class="ia-sheet-link') - src.count('class="ia-sheet-links"')
    check("전체 메뉴 %d개" % SHEET_PAGES, sheet_links == SHEET_PAGES, sheet_links)
    check("내비게이션에 hangul.html 등록", src.count('href="hangul.html"') >= 2, src.count('href="hangul.html"'))
    check("게임 하단 탭이 게임 목록 시트로 열림", 'id="iaGameBtn"' in src and 'data-sheet-target="iaSheetGroupGame"' in src)
    check("미니게임 소제목", 'ia-sheet-sub">미니게임' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("인라인 on* 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", src, re.I))
    check("localStorage 키", "hangul_ladder_stats_v1" in src)
    check("가이드 저장 키", "hangul_guide_seen_v1" in src)
    check("일일·연습 기록 분리", '"daily"' in src and '"practice"' in src and "puzzles" in src and "days" in src)
    check("자정 귀속 dayKey", "dayKey" in src and 'id="dayBadge"' in src)
    check("가이드 3단계", src.count('data-step="') == 3, src.count('data-step="'))
    check("가이드 다시 보기", 'id="guideReplay"' in src and "다시 보기" in src)
    check("감속 모션 대응", "prefers-reduced-motion" in src)
    check("자모 칸 선택", 'hg-part-jamo' in src and 'data-part' in src)
    check("글자 선택 팔레트", 'id="letterChoRow"' in src and 'id="letterGrid"' in src)
    check("별 3개 게이지", 'id="starGauge"' in src)
    check("연속 클리어 배지", 'id="streakChip"' in src)
    check("라이벌 기록 표시", 'id="rivalValue"' in src)
    check("타임 어택 타이머", 'id="timerValue"' in src)
    check("힌트 · 되돌리기 버튼", 'id="hintBtn"' in src and 'id="undoBtn"' in src)
    check("퍼펙트 배지", 'id="resultPerfect"' in src)
    check("연습 목록", 'id="practiceList"' in src)
    check("모드 분리 버튼", 'id="modeDaily"' in src and 'id="modePractice"' in src)

    if failures:
        print("\n실패 %d건" % len(failures))
        raise SystemExit(1)
    print("\n모든 데이터 검증 통과: 단어 %d개 · 일일 %d판 · 연습 %d판 "
          "(par 전수 BFS 검증 · 최단 경로 사전 확인 · 글자 팔레트 완전성)"
          % (len(words), len(daily), len(practice)))


if __name__ == "__main__":
    main()

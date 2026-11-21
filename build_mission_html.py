# -*- coding: utf-8 -*-
"""
퇴근길 미션 (mission.html) 빌더.

1분 경로 퍼즐: 회사에서 출발해 경유지(편의점·카페·서점 등)를 들른 뒤 집에 도착한다.
- 격자 지도(7×7)는 빌드 시점에 고정 시드로 생성하고, 모든 퍼즐은 BFS 최단 경로로
  '제한 이동 수 이내 클리어 가능'을 코드로 검증한 것만 싣는다(검증 실패 시 빌드 중단).
- 오늘의 미션: 21개 검증 풀을 날짜(YYYY-MM-DD) 기준으로 순환 → 같은 날 모든 사용자가 같은 지도.
- 연습 스테이지: 초급·중급·고급 각 5개(총 15개) 검증 퍼즐.
- 기록은 브라우저 localStorage(secjobs-mission-v1)에만 저장하고, 공유 문구에는 경로·지도를 넣지 않는다.
"""
import json
import os
import random
from collections import deque
from datetime import datetime, timezone, timedelta
from html import escape as esc

from html_guard import harden_html, safe_json_for_script

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MISSION_HTML = os.path.join(BASE_DIR, "mission.html")

GRID_SIZE = 7
DAILY_COUNT = 21
SEED_BASE = 20261121

# 이동 가능 방향 (위, 아래, 왼쪽, 오른쪽)
DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))

# 경유 미션 소재 (퇴근길에 들르는 동네 가게)
# (상호, 미션 문구)
MISSIONS = [
    ("편의점", "우유 사기"),
    ("카페", "원두 받기"),
    ("서점", "예약 도서 찾기"),
    ("우체국", "등기 부치기"),
    ("약국", "상비약 사기"),
    ("세탁소", "맡긴 옷 찾기"),
    ("문구점", "노트 사기"),
]

LEVELS = [
    {"key": "beginner", "label": "초급", "min_optimal": 6, "max_optimal": 9, "slack": 3, "waypoints": (1, 2)},
    {"key": "mid", "label": "중급", "min_optimal": 10, "max_optimal": 13, "slack": 2, "waypoints": (1, 2)},
    {"key": "adv", "label": "고급", "min_optimal": 14, "max_optimal": 18, "slack": 1, "waypoints": (2, 2)},
]

PRACTICE_PER_LEVEL = 5
DAILY_OPTIMAL = (10, 16)


# ---------------------------------------------------------------- 지도 유틸
def _neighbors(pos, open_cells):
    r, c = pos
    for dr, dc in DIRS:
        nxt = (r + dr, c + dc)
        if nxt in open_cells:
            yield nxt


def bfs_distances(start, open_cells):
    """start 에서 이동 가능한 칸까지의 최단 거리."""
    dist = {start: 0}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for nxt in _neighbors(cur, open_cells):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
    return dist


def shortest_route(start, goal, waypoints, open_cells):
    """경유지를 모두 들른 뒤 goal 에 도착하는 최단 이동 수(없으면 None).

    상태 = (현재 칸, 들른 경유지 비트마스크). 경유 순서를 바꿔 보는 것까지 BFS 가 함께 탐색한다.
    """
    index = {w: i for i, w in enumerate(waypoints)}
    full = (1 << len(waypoints)) - 1
    origin = (start, 0)
    dist = {origin: 0}
    queue = deque([origin])
    while queue:
        pos, mask = queue.popleft()
        step = dist[(pos, mask)]
        if pos == goal and mask == full:
            return step
        for nxt in _neighbors(pos, open_cells):
            nmask = mask | (1 << index[nxt]) if nxt in index else mask
            state = (nxt, nmask)
            if state not in dist:
                dist[state] = step + 1
                queue.append(state)
    return None


def optimal_path(start, goal, waypoints, open_cells):
    """최단 경로를 실제 칸 목록으로 돌려준다(검증·테스트용)."""
    index = {w: i for i, w in enumerate(waypoints)}
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
        for nxt in _neighbors(pos, open_cells):
            nmask = mask | (1 << index[nxt]) if nxt in index else mask
            nstate = (nxt, nmask)
            if nstate not in dist:
                dist[nstate] = dist[state] + 1
                prev[nstate] = state
                queue.append(nstate)
    if found is None:
        return None
    path = []
    cur = found
    while cur is not None:
        path.append(cur[0])
        cur = prev[cur]
    return list(reversed(path))


# ---------------------------------------------------------------- 퍼즐 생성
def _grid_layout(mode, size):
    """도시 블록 지도: 짝수(또는 홀수) 행·열이 도로, 나머지 칸은 건물."""
    cells = set()
    for r in range(size):
        for c in range(size):
            on_even = (r % 2 == 0 or c % 2 == 0)
            if (mode == "even" and on_even) or (mode == "odd" and not on_even):
                cells.add((r, c))
    return cells


def generate_puzzle(seed, level_key, min_optimal, max_optimal, slack, waypoint_choices):
    """검증된 퍼즐 1개를 만든다. 조건을 만족하는 배치를 못 찾으면 None."""
    rng = random.Random(seed)
    size = GRID_SIZE
    for _ in range(20000):
        mode = "even" if rng.random() < 0.6 else "odd"
        open_cells = _grid_layout(mode, size)
        buildings = {(r, c) for r in range(size) for c in range(size)} - open_cells
        parks = set()
        if buildings:
            for cell in rng.sample(sorted(buildings), min(len(buildings), rng.randint(1, 2))):
                parks.add(cell)
                open_cells.add(cell)

        ring = [cell for cell in sorted(open_cells)
                if cell[0] in (0, size - 1) or cell[1] in (0, size - 1)]
        if len(ring) < 4:
            continue
        start, goal = rng.sample(ring, 2)
        first = bfs_distances(start, open_cells)
        if first.get(goal, 0) < 5:
            continue

        # 공사 구간: 경로를 비켜 가게 만드는 통행 불가 칸
        blocked = set()
        road = [cell for cell in sorted(open_cells) if cell not in (start, goal)]
        if len(road) >= 4:
            for cell in rng.sample(road, rng.randint(2, 3)):
                blocked.add(cell)
                open_cells.discard(cell)
        if start not in open_cells or goal not in open_cells:
            continue

        from_start = bfs_distances(start, open_cells)
        from_goal = bfs_distances(goal, open_cells)
        if goal not in from_start:
            continue

        candidates = [cell for cell in sorted(open_cells)
                      if cell not in (start, goal) and cell not in parks
                      and cell not in ring
                      and from_start.get(cell, 0) >= 2
                      and from_goal.get(cell, 0) >= 2]
        count = rng.choice(waypoint_choices)
        if len(candidates) < count:
            continue
        waypoints = sorted(rng.sample(candidates, count))
        best = shortest_route(start, goal, waypoints, open_cells)
        if best is None or not (min_optimal <= best <= max_optimal):
            continue

        missions = rng.sample(MISSIONS, count)
        return {
            "size": size,
            "mode": mode,
            "start": list(start),
            "goal": list(goal),
            "open": sorted(open_cells),
            "parks": sorted(parks),
            "blocked": sorted(blocked),
            "waypoints": [{"cell": list(cell), "label": missions[i][0], "task": missions[i][1]}
                          for i, cell in enumerate(waypoints)],
            "optimal": best,
            "limit": best + slack,
            "level": level_key,
        }
    return None


def _require(puzzle, label):
    """퍼즐이 실제로 클리어 가능한지(최단 경로 · 제한 이내) 다시 확인한다."""
    if puzzle is None:
        raise SystemExit("[중단] %s 퍼즐 생성 실패" % label)
    start = tuple(puzzle["start"])
    goal = tuple(puzzle["goal"])
    open_cells = {tuple(cell) for cell in puzzle["open"]}
    waypoints = [tuple(w["cell"]) for w in puzzle["waypoints"]]
    for cell in [start, goal] + waypoints:
        if cell not in open_cells:
            raise SystemExit("[중단] %s: 경유지가 통행 불가 칸에 놓였습니다 %r" % (label, cell))
    best = shortest_route(start, goal, waypoints, open_cells)
    if best is None:
        raise SystemExit("[중단] %s: 도달 불가능한 퍼즐" % label)
    if best > puzzle["limit"]:
        raise SystemExit("[중단] %s: 최단 %d수 > 제한 %d수" % (label, best, puzzle["limit"]))
    path = optimal_path(start, goal, waypoints, open_cells)
    if path is None or len(path) - 1 != best:
        raise SystemExit("[중단] %s: 최단 경로 재구성 불일치" % label)
    visited = {cell for cell in path if cell in waypoints}
    if len(visited) != len(waypoints) or path[-1] != goal:
        raise SystemExit("[중단] %s: 경로가 경유지·도착지를 만족하지 않습니다" % label)
    return best


def build_puzzles():
    daily = []
    for i in range(DAILY_COUNT):
        puzzle = generate_puzzle(SEED_BASE + i * 7919, "daily", DAILY_OPTIMAL[0], DAILY_OPTIMAL[1], 2, (1, 2))
        _require(puzzle, "오늘의 미션 %d" % (i + 1))
        puzzle["id"] = "daily-%02d" % (i + 1)
        daily.append(puzzle)

    practice = {}
    for spec in LEVELS:
        items = []
        for j in range(PRACTICE_PER_LEVEL):
            seed = SEED_BASE + 100000 + LEVELS.index(spec) * 1000 + j * 131
            puzzle = generate_puzzle(seed, spec["key"], spec["min_optimal"], spec["max_optimal"],
                                     spec["slack"], spec["waypoints"])
            _require(puzzle, "%s %d" % (spec["label"], j + 1))
            puzzle["id"] = "%s-%02d" % (spec["key"], j + 1)
            puzzle["level_label"] = spec["label"]
            items.append(puzzle)
        practice[spec["key"]] = items
    return daily, practice


def grid_rows(puzzle):
    """퍼즐을 문자 격자로 직렬화한다 (# 건물, X 공사, p 공원, . 도로)."""
    size = puzzle["size"]
    open_cells = {tuple(cell) for cell in puzzle["open"]}
    parks = {tuple(cell) for cell in puzzle["parks"]}
    blocked = {tuple(cell) for cell in puzzle["blocked"]}
    rows = []
    for r in range(size):
        row = []
        for c in range(size):
            cell = (r, c)
            if cell in blocked:
                row.append("X")
            elif cell in parks:
                row.append("p")
            elif cell in open_cells:
                row.append(".")
            else:
                row.append("#")
        rows.append("".join(row))
    return rows


def scene_line(puzzle):
    """지도 아래에 쓰는 한 줄 설명(무엇을 들르고 어디로 가는지)."""
    stops = ["%s · %s" % (w["label"], w["task"]) for w in puzzle["waypoints"]]
    return " → ".join(["회사"] + stops + ["집"])


def serializable(puzzle):
    return {
        "id": puzzle["id"],
        "size": puzzle["size"],
        "rows": grid_rows(puzzle),
        "start": puzzle["start"],
        "goal": puzzle["goal"],
        "waypoints": [{"r": w["cell"][0], "c": w["cell"][1], "label": w["label"], "task": w["task"]}
                      for w in sorted(puzzle["waypoints"], key=lambda w: (w["cell"][0], w["cell"][1]))],
        "limit": puzzle["limit"],
        "optimal": puzzle["optimal"],
        "scene": scene_line(puzzle),
        "level": puzzle["level"],
        "levelLabel": puzzle.get("level_label", "오늘"),
    }


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

      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04);

      --road-bg: #ffffff;
      --road-line: #e8edf3;
      --block-bg: #e2e8f0;
      --cons-bg: #fef3c7;
      --cons-line: #d97706;
      --park-bg: #ecfdf5;
      --park-line: #a7f3d0;
      --trail-bg: #f2f7ff;
      --trail-line: #e2ebfb;
      --player-dot: #2563eb;
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
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);

      --road-bg: #1f1f23;
      --road-line: #2a2a30;
      --block-bg: #35353b;
      --cons-bg: rgba(217, 119, 6, 0.16);
      --cons-line: rgba(217, 119, 6, 0.55);
      --park-bg: rgba(16, 185, 129, 0.12);
      --park-line: rgba(16, 185, 129, 0.3);
      --trail-bg: rgba(59, 130, 246, 0.10);
      --trail-line: rgba(59, 130, 246, 0.22);
      --player-dot: #60a5fa;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }

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

    .container { max-width: 940px; margin: 0 auto; padding: 32px 20px 80px; }

    .hero { margin-bottom: 18px; }

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

    .hero-title { font-size: 26px; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 8px; }

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

    .panel {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      padding: 20px;
      margin-bottom: 16px;
    }

    .game-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 6px;
    }

    .game-kicker {
      font-size: 11.5px;
      font-weight: 600;
      color: var(--accent-primary);
      letter-spacing: 0.02em;
      margin-bottom: 4px;
    }

    .game-title { font-size: 19px; font-weight: 700; letter-spacing: -0.03em; }

    .game-tags { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; flex-shrink: 0; }

    .tag {
      font-size: 11.5px;
      font-weight: 600;
      color: var(--text-secondary);
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 8px;
      white-space: nowrap;
    }

    .tag-mode { color: var(--accent-primary); background: var(--accent-subtle); border-color: var(--border-default); }

    .game-scene {
      font-size: 13.5px;
      color: var(--text-secondary);
      margin-bottom: 16px;
    }

    .board-wrap {
      display: grid;
      grid-template-columns: minmax(0, 440px) minmax(0, 1fr);
      gap: 20px;
      align-items: start;
    }

    .board-col { min-width: 0; }

    .board {
      --n: 7;
      display: grid;
      grid-template-columns: repeat(var(--n), minmax(0, 1fr));
      gap: 4px;
      width: 100%;
      padding: 10px;
      border-radius: 14px;
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      touch-action: manipulation;
      outline: none;
    }

    .board:focus-visible { box-shadow: 0 0 0 2px var(--accent-primary); }

    .cell {
      position: relative;
      aspect-ratio: 1 / 1;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 0.12s ease, border-color 0.12s ease;
    }

    .cell.road { background: var(--road-bg); border: 1px solid var(--road-line); }
    .cell.block { background: var(--block-bg); border: 1px solid transparent; border-radius: 5px; }
    .cell.park { background: var(--park-bg); border: 1px solid var(--park-line); }
    .cell.cons {
      background:
        repeating-linear-gradient(45deg, transparent 0 4px, rgba(217, 119, 6, 0.22) 4px 6px),
        var(--cons-bg);
      border: 1px solid var(--cons-line);
    }

    .cell.via::after {
      content: '';
      position: absolute;
      width: 20%;
      height: 20%;
      border-radius: 50%;
      background: var(--accent-primary);
      opacity: 0.45;
    }
    .cell.current { box-shadow: inset 0 0 0 2px var(--accent-primary); }
    .cell.bump { animation: bump 0.24s ease; }

    @keyframes bump {
      0%, 100% { transform: translateX(0); }
      35% { transform: translateX(-2px); }
      70% { transform: translateX(2px); }
    }

    .mk {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: clamp(8px, 2vw, 10.5px);
      font-weight: 700;
      letter-spacing: -0.04em;
      pointer-events: none;
    }

    .mk-start span,
    .mk-goal span {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 74%;
      height: 74%;
      border-radius: 5px;
      font-size: clamp(8px, 1.9vw, 10px);
    }

    .mk-start span { background: var(--text-primary); color: var(--bg-surface); }
    .mk-goal span { background: var(--bg-surface); color: var(--accent-primary); border: 1.5px solid var(--accent-primary); }

    .mk-wp span {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 62%;
      height: 62%;
      border-radius: 50%;
      background: var(--accent-subtle);
      color: var(--accent-primary);
      border: 1.5px solid var(--accent-primary);
      font-size: clamp(8px, 1.9vw, 10px);
    }

    .mk-wp.done span { background: var(--accent-primary); color: #ffffff; }

    .cell.current .mk-start span { opacity: 0; }

    .ply {
      width: 58%;
      height: 58%;
      border-radius: 50%;
      background: var(--player-dot);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18);
      pointer-events: none;
      z-index: 2;
    }

    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 10px;
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .legend span { display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }

    .lg {
      width: 11px;
      height: 11px;
      border-radius: 3px;
      display: inline-block;
      border: 1px solid var(--border-default);
    }

    .lg-start { background: var(--text-primary); border-color: var(--text-primary); }
    .lg-goal { background: var(--bg-surface); border-color: var(--accent-primary); border-width: 2px; }
    .lg-wp { border-radius: 50%; border-color: var(--accent-primary); background: var(--accent-subtle); }
    .lg-cons { background: var(--cons-bg); border-color: var(--cons-line); }
    .lg-block { background: var(--block-bg); border-color: transparent; }

    .keys {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px dashed var(--border-default);
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .keys span { display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; }

    kbd {
      font-family: inherit;
      font-size: 10.5px;
      font-weight: 600;
      color: var(--text-secondary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-bottom-width: 2px;
      border-radius: 5px;
      padding: 1px 5px;
      line-height: 1.4;
    }

    .board-side { display: flex; flex-direction: column; gap: 14px; min-width: 0; }

    .mlist { list-style: none; display: flex; flex-direction: column; gap: 8px; }

    .mitem {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 9px 11px;
      border: 1px solid var(--border-default);
      border-radius: 9px;
      background: var(--bg-surface);
    }

    .mnum {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
      flex-shrink: 0;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
    }

    .mitem.is-done .mnum { background: var(--accent-primary); color: #ffffff; border-color: var(--accent-primary); }

    .mbody { display: flex; flex-direction: column; min-width: 0; }
    .mbody strong { font-size: 13.5px; font-weight: 600; }
    .mbody span { font-size: 11.5px; color: var(--text-muted); }

    .mstate { margin-left: auto; font-size: 11.5px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }
    .mitem.is-done .mstate { color: var(--accent-primary); }

    .meters { display: flex; flex-direction: column; gap: 6px; }

    .meter-row { display: flex; align-items: center; justify-content: space-between; font-size: 12.5px; color: var(--text-secondary); }
    .meter-row strong { color: var(--text-primary); font-weight: 700; font-variant-numeric: tabular-nums; }

    .bar { height: 5px; border-radius: 999px; background: var(--bg-subtle); overflow: hidden; }
    .bar i { display: block; height: 100%; width: 0; border-radius: 999px; background: var(--accent-primary); transition: width 0.18s ease; }
    .bar.is-full i { background: #d97706; }

    .pad {
      display: grid;
      grid-template-columns: repeat(3, 42px);
      grid-template-rows: repeat(3, 42px);
      gap: 6px;
      justify-content: start;
    }

    .pad-btn {
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      border-radius: 9px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.12s ease;
      padding: 0;
    }

    .pad-btn:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .pad-btn:active { transform: scale(0.96); }
    .pad-btn[data-dir="up"] { grid-area: 1 / 2; }
    .pad-btn[data-dir="left"] { grid-area: 2 / 1; }
    .pad-btn[data-dir="right"] { grid-area: 2 / 3; }
    .pad-btn[data-dir="down"] { grid-area: 3 / 2; }

    .pad-hub {
      grid-area: 2 / 2;
      border-radius: 50%;
      background: var(--bg-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 9.5px;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0;
    }

    .game-actions { display: flex; gap: 8px; }

    .btn {
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      border-radius: 9px;
      padding: 8px 13px;
      cursor: pointer;
      transition: all 0.15s ease;
      border: 1px solid transparent;
      letter-spacing: -0.02em;
    }

    .btn-line { background: var(--bg-surface); border-color: var(--border-default); color: var(--text-secondary); }
    .btn-line:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .btn-line:disabled { opacity: 0.45; cursor: default; }

    .btn-primary { background: var(--accent-primary); color: #ffffff; border-color: var(--accent-primary); }
    .btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }

    .game-msg { font-size: 12px; color: var(--text-muted); min-height: 18px; }

    .result {
      margin-top: 16px;
      padding: 16px;
      border-radius: 12px;
      border: 1px solid var(--ok-border);
      background: var(--ok-bg);
    }

    .result-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }

    .result-badge {
      font-size: 11.5px;
      font-weight: 700;
      color: var(--ok-text);
      border: 1px solid var(--ok-border);
      background: var(--bg-surface);
      border-radius: 6px;
      padding: 2px 7px;
    }

    .result-title { font-size: 14.5px; font-weight: 700; color: var(--text-primary); }

    .result-facts { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }

    .fact {
      display: inline-flex;
      flex-direction: column;
      gap: 1px;
      padding: 6px 10px;
      border-radius: 8px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      min-width: 72px;
    }

    .fact small { font-size: 10.5px; color: var(--text-muted); }
    .fact strong { font-size: 13px; font-weight: 700; font-variant-numeric: tabular-nums; }

    .share { display: flex; gap: 10px; align-items: stretch; }

    .share-preview {
      flex: 1 1 auto;
      min-width: 0;
      font-family: "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
      font-size: 11.5px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-all;
      color: var(--text-secondary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 9px;
      padding: 10px 11px;
    }

    .share-note { font-size: 11px; color: var(--text-muted); margin-top: 8px; }

    .practice-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .panel-title { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; }

    .panel-title .bar-mark { width: 3px; height: 14px; border-radius: 2px; background: var(--accent-primary); display: inline-block; }

    .panel-meta { font-size: 12px; color: var(--text-muted); }

    .seg { display: inline-flex; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 9px; }

    .seg-btn {
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-secondary);
      background: transparent;
      border: none;
      border-radius: 7px;
      padding: 6px 13px;
      cursor: pointer;
      transition: all 0.15s ease;
      letter-spacing: -0.02em;
    }

    .seg-btn.active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06); }

    .chips { display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 8px; margin-top: 12px; }

    .stage {
      font-family: inherit;
      text-align: left;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      border-radius: 9px;
      padding: 9px 10px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }

    .stage:hover { border-color: var(--border-strong); background: var(--bg-subtle); }
    .stage.active { border-color: var(--accent-primary); box-shadow: inset 0 0 0 1px var(--accent-primary); }
    .stage-label { font-size: 12.5px; font-weight: 700; color: var(--text-primary); }
    .stage-meta { font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 4px; }
    .stage.cleared .stage-meta { color: var(--ok-text); }

    .check { width: 11px; height: 11px; flex-shrink: 0; }

    .practice-note { font-size: 11.5px; color: var(--text-muted); margin-top: 10px; }

    .footer {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--border-default);
      font-size: 11.5px;
      line-height: 1.7;
      color: var(--text-muted);
    }

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

    @media (max-width: 820px) {
      .board-wrap { grid-template-columns: minmax(0, 1fr); }
      .board { max-width: 460px; margin: 0 auto; }
      .board-side { max-width: 460px; margin: 0 auto; width: 100%; }
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
      .panel { padding: 15px 14px; border-radius: 12px; }
      .game-title { font-size: 17px; }
      .game-scene { font-size: 12.5px; margin-bottom: 12px; }
      .board { padding: 8px; gap: 3px; border-radius: 12px; }
      .board-wrap { gap: 14px; }
      .pad { grid-template-columns: repeat(3, 40px); grid-template-rows: repeat(3, 40px); }
      .share { flex-direction: column; align-items: stretch; }
      .share .btn-primary { width: 100%; }
      .chips { grid-template-columns: repeat(auto-fill, minmax(88px, 1fr)); }
      .keys { display: none; }
    }

    @media (max-width: 430px) {
      .nav-container { padding: 0 8px; height: 52px; gap: 4px; }
      .brand-logo-img { width: 22px; height: 22px; }
      .nav-tabs {
        margin-left: 2px;
        gap: 1px;
        flex: 1 1 auto;
        min-width: 0;
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
      }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 5px; font-size: 10px; border-radius: 11px; letter-spacing: -0.045em; }
      .nav-actions { gap: 4px; }
      .nav-actions .icon-btn { width: 28px; height: 28px; }
      .game-tags { gap: 4px; }
      .tag { font-size: 10.5px; padding: 2px 6px; }
    }

    @media (max-width: 380px) {
      .brand-name { display: none; }
    }
"""

NAV_TABS = """
          <a href="index.html" class="nav-tab-item">채용공고</a>
          <a href="study.html" class="nav-tab-item">시험 공부</a>
          <a href="ai.html" class="nav-tab-item">AI 트렌드</a>
          <a href="cve.html" class="nav-tab-item">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
          <a href="radar.html" class="nav-tab-item">피싱 레이더</a>
          <a href="pick.html" class="nav-tab-item">오늘 뭐 먹지</a>
          <a href="clue.html" class="nav-tab-item">3단서 추리</a>
          <a href="mission.html" class="nav-tab-item active">퇴근길 미션</a>
"""


# ---------------------------------------------------------------- HTML
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 퇴근길 미션</title>
  <meta name="description" content="회사에서 출발해 편의점·카페 같은 경유지를 들르고 제한 이동 수 안에 집에 도착하는 1분 경로 퍼즐. 매일 같은 지도로 열리는 오늘의 미션과 초급·중급·고급 연습 스테이지, 최고 기록과 연속 클리어를 제공합니다.">
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
        <div class="nav-tabs">__NAV_TABS__        </div>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>매일 00:00 새 지도</span>
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

    // ---- Theme (다른 페이지와 같은 secjobs-theme 동기화) ----
    (function () {
      var themeToggle = document.getElementById('themeToggle');
      var moonIcon = document.getElementById('moonIcon');
      var sunIcon = document.getElementById('sunIcon');

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

      var saved = null;
      try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) setTheme('dark');
      else setTheme('light');

      if (themeToggle) {
        themeToggle.addEventListener('click', function () {
          var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
          setTheme(isDark ? 'light' : 'dark');
        });
      }
    })();
  </script>

  <main class="container">

    <section class="hero">
      <span class="hero-pill">COMMUTE ROUTE</span>
      <h1 class="hero-title">퇴근길 미션</h1>
      <p class="hero-desc">회사에서 출발해 경유지를 모두 들른 뒤 제한된 이동 수 안에 집에 도착하는 1분 경로 퍼즐입니다. 방향키·WASD 또는 화면의 방향 버튼과 인접한 칸을 눌러 움직이고, 막히면 되돌려 다시 짜면 됩니다. 오늘의 지도는 날짜마다 모두에게 같고, 연습 스테이지는 언제든 다시 풀 수 있습니다.</p>
      <div class="hero-stats">
        <span class="stat-chip">오늘 <strong id="statToday">미도전</strong></span>
        <span class="stat-chip">연속 <strong id="statStreak">0일</strong></span>
        <span class="stat-chip">최고 기록 <strong id="statBest">-</strong></span>
        <span class="stat-chip">연습 <strong id="statPractice">0 / 15</strong></span>
      </div>
    </section>

    <section class="panel game" aria-label="퇴근길 미션 퍼즐">
      <div class="game-head">
        <div>
          <div class="game-kicker" id="gameKicker">오늘의 미션</div>
          <h2 class="game-title" id="gameTitle">지도를 불러오는 중입니다</h2>
        </div>
        <div class="game-tags">
          <button type="button" class="link-btn" id="backDaily" hidden>오늘의 미션으로</button>
          <span class="tag" id="tagSize">7 × 7</span>
          <span class="tag" id="tagLimit">제한 14수</span>
          <span class="tag tag-mode" id="tagMode">일일</span>
        </div>
      </div>
      <p class="game-scene" id="gameScene"></p>

      <div class="board-wrap">
        <div class="board-col">
          <div class="board" id="board" role="grid" tabindex="0" aria-label="경로 지도"></div>
          <div class="legend">
            <span><i class="lg lg-start"></i>회사(출발)</span>
            <span><i class="lg lg-goal"></i>집(도착)</span>
            <span><i class="lg lg-wp"></i>경유지</span>
            <span><i class="lg lg-cons"></i>공사 구간</span>
            <span><i class="lg lg-block"></i>건물</span>
          </div>
          <div class="keys">
            <span><kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd> 이동</span>
            <span><kbd>Z</kbd> 되돌리기</span>
            <span><kbd>R</kbd> 다시 시작</span>
            <span>인접한 칸을 눌러도 이동합니다</span>
          </div>
        </div>

        <div class="board-side">
          <ol class="mlist" id="missionList"></ol>

          <div class="meters">
            <div class="meter-row"><span>이동</span><strong id="moveText">0 / 14</strong></div>
            <div class="bar" id="moveBarWrap"><i id="moveBar"></i></div>
            <div class="meter-row"><span>시간</span><strong id="timeText">00:00</strong></div>
          </div>

          <div class="pad" id="pad" aria-label="방향 버튼">
            <button type="button" class="pad-btn" data-dir="up" aria-label="위로 이동">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"></path><path d="M5 12l7-7 7 7"></path></svg>
            </button>
            <button type="button" class="pad-btn" data-dir="left" aria-label="왼쪽으로 이동">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"></path><path d="M12 19l-7-7 7-7"></path></svg>
            </button>
            <span class="pad-hub">이동</span>
            <button type="button" class="pad-btn" data-dir="right" aria-label="오른쪽으로 이동">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
            </button>
            <button type="button" class="pad-btn" data-dir="down" aria-label="아래로 이동">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"></path><path d="M19 12l-7 7-7-7"></path></svg>
            </button>
          </div>

          <div class="game-actions">
            <button type="button" class="btn btn-line" id="undoBtn">되돌리기</button>
            <button type="button" class="btn btn-line" id="resetBtn">다시 시작</button>
          </div>
          <p class="game-msg" id="gameMsg" role="status" aria-live="polite"></p>
        </div>
      </div>

      <div class="result" id="resultBox" hidden>
        <div class="result-head">
          <span class="result-badge" id="resultBadge">도착</span>
          <span class="result-title" id="resultTitle"></span>
        </div>
        <div class="result-facts">
          <span class="fact"><small>이동</small><strong id="rMoves">-</strong></span>
          <span class="fact"><small>시간</small><strong id="rTime">-</strong></span>
          <span class="fact"><small>최소 이동</small><strong id="rOpt">-</strong></span>
        </div>
        <div class="share">
          <div class="share-preview" id="sharePreview"></div>
          <button type="button" class="btn btn-primary" id="copyBtn">결과 복사</button>
        </div>
        <p class="share-note">결과 문구에는 지도와 경로가 들어가지 않습니다. 기록은 이 브라우저에만 저장됩니다.</p>
      </div>
    </section>

    <section class="panel practice" id="practicePanel" aria-label="연습 스테이지">
      <div class="practice-head">
        <div class="panel-title"><span class="bar-mark"></span>연습 스테이지</div>
        <span class="panel-meta">난이도를 골라 다시 풀 수 있습니다</span>
      </div>
      <div class="seg" id="levelSeg"></div>
      <div class="chips" id="stageChips"></div>
      <p class="practice-note" id="practiceNote">모든 스테이지는 최단 경로로 도달할 수 있고, 제한 이동 수 안에 클리어할 수 있도록 검증했습니다.</p>
    </section>

    <footer class="footer">
      Infosec Archive · 퇴근길 미션<br>
      지도는 날짜를 시드로 고른 검증된 퍼즐이며, 모든 스테이지는 BFS 최단 경로로 클리어 가능함을 빌드 단계에서 확인합니다. 플레이 기록은 이 브라우저(localStorage)에만 저장되며 서버로 전송되지 않습니다.<br>
      __BUILT_AT__ 기준 · 매일 00:00 새 지도
    </footer>
  </main>

  <script>
    const DATA = __DATA_JSON__;

    (function () {
      'use strict';

      const STORE_KEY = 'secjobs-mission-v1';
      const SITE = 'https://bling9513-ship-it.github.io/project-1/mission.html';
      const LEVELS = DATA.levels;
      const DIR_VECTORS = { up: [-1, 0], down: [1, 0], left: [0, -1], right: [0, 1] };

      const $ = function (id) { return document.getElementById(id); };
      const board = $('board');
      const missionList = $('missionList');
      const moveText = $('moveText');
      const moveBar = $('moveBar');
      const moveBarWrap = $('moveBarWrap');
      const timeText = $('timeText');
      const gameMsg = $('gameMsg');
      const gameKicker = $('gameKicker');
      const gameTitle = $('gameTitle');
      const gameScene = $('gameScene');
      const tagSize = $('tagSize');
      const tagLimit = $('tagLimit');
      const tagMode = $('tagMode');
      const backDaily = $('backDaily');
      const resultBox = $('resultBox');
      const resultTitle = $('resultTitle');
      const rMoves = $('rMoves');
      const rTime = $('rTime');
      const rOpt = $('rOpt');
      const sharePreview = $('sharePreview');
      const copyBtn = $('copyBtn');
      const levelSeg = $('levelSeg');
      const stageChips = $('stageChips');

      function pad2(n) { return (n < 10 ? '0' : '') + n; }
      function isoOf(d) { return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate()); }
      function dayNumber(iso) {
        const p = iso.split('-').map(Number);
        return Math.floor(Date.UTC(p[0], p[1] - 1, p[2]) / 86400000);
      }
      function fmtTime(seconds) {
        const s = Math.max(0, Math.round(seconds));
        return pad2(Math.floor(s / 60)) + ':' + pad2(s % 60);
      }
      function esc(text) {
        return String(text == null ? '' : text)
          .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
      }

      // ---- 기록 (localStorage 전용) ----
      function loadStore() {
        const out = { daily: {}, practice: {} };
        let raw = null;
        try { raw = localStorage.getItem(STORE_KEY); } catch (e) {}
        if (!raw) return out;
        let saved = null;
        try { saved = JSON.parse(raw); } catch (e) { return out; }
        if (!saved || typeof saved !== 'object') return out;
        const read = function (src, dest) {
          if (!src || typeof src !== 'object') return;
          Object.keys(src).forEach(function (key) {
            const r = src[key];
            if (!r || typeof r !== 'object') return;
            const moves = Number(r.moves);
            const seconds = Number(r.seconds);
            if (!isFinite(moves) || moves <= 0 || moves > 200) return;
            dest[key] = {
              moves: Math.round(moves),
              seconds: isFinite(seconds) && seconds >= 0 ? Math.min(3600, Math.round(seconds)) : 0,
              limit: Number(r.limit) || 0,
              optimal: Number(r.optimal) || 0
            };
          });
        };
        read(saved.daily, out.daily);
        read(saved.practice, out.practice);
        return out;
      }

      const STORE = loadStore();
      function saveStore() {
        try {
          localStorage.setItem(STORE_KEY, JSON.stringify({ version: 1, daily: STORE.daily, practice: STORE.practice }));
        } catch (e) {}
      }

      const TODAY = isoOf(new Date());
      const DAILY_INDEX = ((dayNumber(TODAY) % DATA.daily.length) + DATA.daily.length) % DATA.daily.length;

      function streakCount() {
        let count = 0;
        const cursor = new Date();
        cursor.setHours(12, 0, 0, 0);
        if (!STORE.daily[isoOf(cursor)]) cursor.setDate(cursor.getDate() - 1);
        for (let i = 0; i < 400; i += 1) {
          if (!STORE.daily[isoOf(cursor)]) break;
          count += 1;
          cursor.setDate(cursor.getDate() - 1);
        }
        return count;
      }

      // ---- 상태 ----
      let mode = 'daily';
      let practiceLevel = LEVELS[0].key;
      let practiceSlot = 0;
      let puz = null;
      let game = null;
      let cellEls = [];
      let plyEl = null;
      let ticker = null;

      function prepare(raw) {
        return {
          id: raw.id,
          size: raw.size,
          rows: raw.rows,
          start: raw.start.slice(),
          goal: raw.goal.slice(),
          waypoints: raw.waypoints.map(function (w) { return { r: w.r, c: w.c, label: w.label, task: w.task }; }),
          limit: raw.limit,
          optimal: raw.optimal,
          scene: raw.scene,
          level: raw.level,
          levelLabel: raw.levelLabel
        };
      }

      function cellAt(r, c) {
        if (r < 0 || c < 0 || r >= puz.size || c >= puz.size) return '#';
        return puz.rows[r][c];
      }
      function walkable(r, c) {
        const ch = cellAt(r, c);
        return ch !== '#' && ch !== 'X';
      }
      function pathHas(r, c) {
        for (let i = 0; i < game.path.length; i += 1) {
          if (game.path[i][0] === r && game.path[i][1] === c) return true;
        }
        return false;
      }
      function allVisited() {
        return puz.waypoints.every(function (w) { return pathHas(w.r, w.c); });
      }
      function elapsedSeconds() {
        if (game.startedAt) return game.elapsed + (Date.now() - game.startedAt) / 1000;
        return game.elapsed;
      }

      function flash(text) { gameMsg.textContent = text; }

      // ---- 렌더 ----
      function renderBoard() {
        board.innerHTML = '';
        board.style.setProperty('--n', puz.size);
        board.setAttribute('aria-label', '경로 지도 ' + puz.size + ' × ' + puz.size + ', 방향키나 인접한 칸을 눌러 이동');
        cellEls = [];
        for (let r = 0; r < puz.size; r += 1) {
          for (let c = 0; c < puz.size; c += 1) {
            const ch = puz.rows[r][c];
            const el = document.createElement('div');
            const kind = ch === '#' ? 'block' : ch === 'X' ? 'cons' : ch === 'p' ? 'park' : 'road';
            el.className = 'cell ' + kind;
            el.dataset.r = String(r);
            el.dataset.c = String(c);
            el.setAttribute('role', 'gridcell');
            const kindLabel = kind === 'block' ? '건물' : kind === 'cons' ? '공사 구간' : kind === 'park' ? '공원' : '길';
            el.setAttribute('aria-label', (r + 1) + '행 ' + (c + 1) + '열 ' + kindLabel);
            if (r === puz.start[0] && c === puz.start[1]) {
              el.insertAdjacentHTML('beforeend', '<span class="mk mk-start"><span>출</span></span>');
            } else if (r === puz.goal[0] && c === puz.goal[1]) {
              el.insertAdjacentHTML('beforeend', '<span class="mk mk-goal"><span>집</span></span>');
            }
            puz.waypoints.forEach(function (w, i) {
              if (w.r === r && w.c === c) {
                el.insertAdjacentHTML('beforeend',
                  '<span class="mk mk-wp" data-wp="' + i + '"><span>' + (i + 1) + '</span></span>');
              }
            });
            cellEls.push(el);
            board.appendChild(el);
          }
        }
      }

      function renderMissions() {
        const parts = [];
        parts.push('<li class="mitem is-start"><span class="mnum">출</span><div class="mbody"><strong>회사</strong><span>여기서 출발</span></div><span class="mstate">시작</span></li>');
        puz.waypoints.forEach(function (w, i) {
          parts.push('<li class="mitem" data-wp="' + i + '"><span class="mnum">' + (i + 1) + '</span>' +
            '<div class="mbody"><strong>' + esc(w.label) + '</strong><span>' + esc(w.task) + '</span></div>' +
            '<span class="mstate">대기</span></li>');
        });
        parts.push('<li class="mitem" data-goal="1"><span class="mnum">집</span><div class="mbody"><strong>집</strong><span>도착하면 완료</span></div><span class="mstate">대기</span></li>');
        missionList.innerHTML = parts.join('');
      }

      function paint() {
        for (let i = 0; i < cellEls.length; i += 1) cellEls[i].classList.remove('via', 'current');
        game.path.forEach(function (cell) {
          cellEls[cell[0] * puz.size + cell[1]].classList.add('via');
        });
        const current = cellEls[game.pos[0] * puz.size + game.pos[1]];
        current.classList.add('current');
        current.appendChild(plyEl);

        puz.waypoints.forEach(function (w, i) {
          const done = pathHas(w.r, w.c);
          const marker = board.querySelector('.mk-wp[data-wp="' + i + '"]');
          if (marker) marker.classList.toggle('done', done);
          const item = missionList.querySelector('.mitem[data-wp="' + i + '"]');
          if (item) {
            item.classList.toggle('is-done', done);
            const state = item.querySelector('.mstate');
            if (state) state.textContent = done ? '완료' : '대기';
          }
        });
        const goalItem = missionList.querySelector('.mitem[data-goal="1"]');
        if (goalItem) {
          const arrived = game.pos[0] === puz.goal[0] && game.pos[1] === puz.goal[1] && allVisited();
          goalItem.classList.toggle('is-done', arrived);
          const state = goalItem.querySelector('.mstate');
          if (state) state.textContent = arrived ? '완료' : '대기';
        }
        board.setAttribute('aria-label', '경로 지도 ' + puz.size + ' × ' + puz.size +
          ', 현재 ' + (game.pos[0] + 1) + '행 ' + (game.pos[1] + 1) + '열');
      }

      function updateMeters() {
        moveText.textContent = game.moves + ' / ' + puz.limit;
        const ratio = Math.min(1, game.moves / puz.limit);
        moveBar.style.width = (ratio * 100).toFixed(1) + '%';
        moveBarWrap.classList.toggle('is-full', game.moves >= puz.limit);
        timeText.textContent = fmtTime(elapsedSeconds());
        $('undoBtn').disabled = game.status === 'won' || game.path.length <= 1;
      }

      function renderStats() {
        const today = STORE.daily[TODAY];
        $('statToday').textContent = today ? ('클리어 · ' + today.moves + '수') : '미도전';
        $('statStreak').textContent = streakCount() + '일';
        const moves = Object.keys(STORE.daily).map(function (k) { return STORE.daily[k].moves; });
        $('statBest').textContent = moves.length ? Math.min.apply(null, moves) + '수' : '-';
        $('statPractice').textContent = Object.keys(STORE.practice).length + ' / ' + DATA.practiceCount;
      }

      function checkSvg() {
        return '<svg class="check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"></path></svg>';
      }

      function renderChips() {
        const list = DATA.practice[practiceLevel] || [];
        stageChips.innerHTML = list.map(function (p, i) {
          const rec = STORE.practice[p.id];
          const active = (mode === 'practice' && puz && puz.id === p.id);
          const meta = rec ? ('최소 ' + rec.moves + '수 · ' + fmtTime(rec.seconds)) : ('제한 ' + p.limit + '수');
          return '<button type="button" class="stage' + (rec ? ' cleared' : '') + (active ? ' active' : '') + '" data-slot="' + i + '">' +
            '<span class="stage-label">' + (i + 1) + '번 ' + (rec ? checkSvg() : '') + '</span>' +
            '<span class="stage-meta">' + meta + '</span></button>';
        }).join('');
      }

      function renderLevels() {
        levelSeg.innerHTML = LEVELS.map(function (l) {
          const active = l.key === practiceLevel;
          return '<button type="button" class="seg-btn' + (active ? ' active' : '') + '" data-level="' + l.key + '">' + esc(l.label) + '</button>';
        }).join('');
      }

      // ---- 게임 진행 ----
      function stopTicker() {
        if (ticker) { clearInterval(ticker); ticker = null; }
      }
      function startTicker() {
        if (ticker) return;
        ticker = setInterval(function () {
          if (game && game.startedAt) timeText.textContent = fmtTime(elapsedSeconds());
        }, 500);
      }
      function freezeTimer() {
        game.elapsed = elapsedSeconds();
        game.startedAt = 0;
        stopTicker();
      }

      function startPuzzle(raw, context) {
        mode = context.mode;
        if (context.level) practiceLevel = context.level;
        if (typeof context.slot === 'number') practiceSlot = context.slot;
        puz = prepare(raw);
        stopTicker();
        game = {
          pos: puz.start.slice(),
          path: [puz.start.slice()],
          moves: 0,
          status: 'playing',
          startedAt: 0,
          elapsed: 0
        };
        if (!plyEl) {
          plyEl = document.createElement('span');
          plyEl.className = 'ply';
          plyEl.setAttribute('aria-hidden', 'true');
        }

        if (mode === 'daily') {
          gameKicker.textContent = '오늘의 미션';
          gameTitle.textContent = Number(TODAY.slice(5, 7)) + '월 ' + Number(TODAY.slice(8, 10)) + '일 퇴근길';
          tagMode.textContent = '일일';
          backDaily.hidden = true;
        } else {
          gameKicker.textContent = '연습 스테이지';
          gameTitle.textContent = puz.levelLabel + ' ' + (practiceSlot + 1) + '번';
          tagMode.textContent = '연습';
          backDaily.hidden = false;
        }
        gameScene.textContent = puz.scene;
        tagSize.textContent = puz.size + ' × ' + puz.size;
        tagLimit.textContent = '제한 ' + puz.limit + '수';

        resultBox.hidden = true;
        copyBtn.textContent = '결과 복사';
        flash('출발 준비가 끝났습니다. 경유지를 모두 들르고 집에 도착하세요.');

        renderBoard();
        renderMissions();
        paint();
        updateMeters();
        renderLevels();
        renderChips();
      }

      function loadDaily() {
        startPuzzle(DATA.daily[DAILY_INDEX], { mode: 'daily' });
      }

      function loadPractice(level, slot) {
        const list = DATA.practice[level] || [];
        if (!list[slot]) return;
        startPuzzle(list[slot], { mode: 'practice', level: level, slot: slot });
        renderLevels();
      }

      function resetPuzzle() {
        const contextName = gameTitle.textContent;
        startPuzzle(mode === 'daily' ? DATA.daily[DAILY_INDEX] : DATA.practice[practiceLevel][practiceSlot], {
          mode: mode, level: practiceLevel, slot: practiceSlot
        });
        flash(contextName + ' · 처음 위치로 돌아왔습니다.');
      }

      function step(dr, dc) {
        if (!game) return;
        if (game.status === 'won') return;
        if (game.status === 'limit') {
          flash('이동 수를 모두 썼습니다. 되돌리기로 한 수를 되돌려 보세요.');
          return;
        }
        const nr = game.pos[0] + dr;
        const nc = game.pos[1] + dc;
        if (nr < 0 || nc < 0 || nr >= puz.size || nc >= puz.size) return;
        const ch = cellAt(nr, nc);
        if (ch === '#' || ch === 'X') {
          const el = cellEls[nr * puz.size + nc];
          el.classList.remove('bump');
          void el.offsetWidth;
          el.classList.add('bump');
          flash(ch === 'X' ? '공사 구간입니다. 돌아가야 합니다.' : '건물입니다. 길로만 다닐 수 있습니다.');
          return;
        }
        if (game.moves >= puz.limit) return;
        if (!game.startedAt) {
          game.startedAt = Date.now();
          startTicker();
        }
        game.path.push([nr, nc]);
        game.pos = [nr, nc];
        game.moves += 1;
        paint();
        updateMeters();
        checkEnd();
      }

      function undo() {
        if (!game || game.status === 'won') return;
        if (game.path.length <= 1) {
          flash('되돌릴 이동이 없습니다.');
          return;
        }
        game.path.pop();
        game.pos = game.path[game.path.length - 1].slice();
        game.moves = Math.max(0, game.moves - 1);
        game.status = 'playing';
        paint();
        updateMeters();
        flash('한 수 되돌렸습니다.');
      }

      function checkEnd() {
        const atGoal = game.pos[0] === puz.goal[0] && game.pos[1] === puz.goal[1];
        const missing = puz.waypoints.filter(function (w) { return !pathHas(w.r, w.c); });
        if (atGoal && missing.length === 0) {
          finish();
          return;
        }
        if (atGoal && missing.length) {
          flash('경유지 ' + missing.length + '곳을 아직 들르지 않았습니다.');
        }
        if (game.moves >= puz.limit) {
          game.status = 'limit';
          freezeTimer();
          updateMeters();
          flash('이동 수를 모두 썼습니다. 되돌리기로 한 수를 되돌리거나 다시 시작하세요.');
          if (!atGoal) resultBox.hidden = true;
        }
      }

      function recordClear(seconds) {
        const entry = {
          moves: game.moves,
          seconds: Math.round(seconds),
          limit: puz.limit,
          optimal: puz.optimal
        };
        let improved = false;
        if (mode === 'daily') {
          const prev = STORE.daily[TODAY];
          if (!prev || entry.moves < prev.moves || (entry.moves === prev.moves && entry.seconds < prev.seconds)) {
            improved = !!prev;
            STORE.daily[TODAY] = entry;
          }
        } else {
          const prev = STORE.practice[puz.id];
          if (!prev || entry.moves < prev.moves || (entry.moves === prev.moves && entry.seconds < prev.seconds)) {
            improved = !!prev;
            STORE.practice[puz.id] = entry;
          }
        }
        saveStore();
        renderStats();
        renderChips();
        return improved;
      }

      function shareText(seconds) {
        const visited = puz.waypoints.filter(function (w) { return pathHas(w.r, w.c); }).length;
        const head = mode === 'daily'
          ? '퇴근길 미션 ' + TODAY
          : '퇴근길 미션 연습 · ' + puz.levelLabel + ' ' + (practiceSlot + 1) + '번';
        const lines = [head,
          '경유 ' + visited + '/' + puz.waypoints.length + ' · 이동 ' + game.moves + '/' + puz.limit +
          ' · ' + fmtTime(seconds) + ' · 최소 ' + puz.optimal + '수'];
        if (mode === 'daily') {
          const streak = streakCount();
          if (streak > 0) lines.push('연속 ' + streak + '일');
        }
        lines.push(SITE);
        return lines.join('\\n');
      }

      function finish() {
        game.status = 'won';
        freezeTimer();
        const seconds = game.elapsed;
        const improved = recordClear(seconds);
        paint();
        updateMeters();

        resultTitle.textContent = game.moves === puz.optimal
          ? '최단 경로로 도착했습니다'
          : (game.moves <= puz.optimal + 1 ? '한 수 차이로 도착했습니다' : '무사히 도착했습니다');
        rMoves.textContent = game.moves + ' / ' + puz.limit + '수';
        rTime.textContent = fmtTime(seconds);
        rOpt.textContent = puz.optimal + '수';
        sharePreview.textContent = shareText(seconds);
        copyBtn.textContent = '결과 복사';
        resultBox.hidden = false;
        flash(improved ? '이전 기록보다 좋은 기록입니다. 이 브라우저에 저장했습니다.' : '기록을 이 브라우저에 저장했습니다.');
      }

      function copyResult() {
        const text = sharePreview.textContent;
        const done = function (ok) {
          copyBtn.textContent = ok ? '복사됨' : '복사 실패';
          setTimeout(function () { copyBtn.textContent = '결과 복사'; }, 1800);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallbackCopy(text)); });
        } else {
          done(fallbackCopy(text));
        }
      }

      function fallbackCopy(text) {
        try {
          const area = document.createElement('textarea');
          area.value = text;
          area.setAttribute('readonly', 'readonly');
          area.style.position = 'fixed';
          area.style.top = '-1000px';
          document.body.appendChild(area);
          area.select();
          const ok = document.execCommand('copy');
          document.body.removeChild(area);
          return ok;
        } catch (e) {
          return false;
        }
      }

      // ---- 입력 ----
      board.addEventListener('click', function (ev) {
        const cell = ev.target.closest ? ev.target.closest('.cell') : null;
        if (!cell || !game) return;
        const r = Number(cell.dataset.r);
        const c = Number(cell.dataset.c);
        const dr = r - game.pos[0];
        const dc = c - game.pos[1];
        if (Math.abs(dr) + Math.abs(dc) !== 1) {
          flash('한 칸 옆으로만 이동할 수 있습니다.');
          return;
        }
        step(dr, dc);
      });

      $('pad').addEventListener('click', function (ev) {
        const btn = ev.target.closest ? ev.target.closest('.pad-btn') : null;
        if (!btn) return;
        const vec = DIR_VECTORS[btn.dataset.dir];
        if (vec) step(vec[0], vec[1]);
      });

      $('undoBtn').addEventListener('click', undo);
      $('resetBtn').addEventListener('click', resetPuzzle);
      copyBtn.addEventListener('click', copyResult);
      backDaily.addEventListener('click', loadDaily);

      levelSeg.addEventListener('click', function (ev) {
        const btn = ev.target.closest ? ev.target.closest('.seg-btn') : null;
        if (!btn) return;
        practiceLevel = btn.dataset.level;
        renderLevels();
        renderChips();
        practiceNote.textContent = btn.textContent + ' 스테이지 5개입니다. 번호를 눌러 바로 시작하세요.';
      });

      stageChips.addEventListener('click', function (ev) {
        const btn = ev.target.closest ? ev.target.closest('.stage') : null;
        if (!btn) return;
        loadPractice(practiceLevel, Number(btn.dataset.slot));
      });

      document.addEventListener('keydown', function (ev) {
        if (ev.altKey || ev.ctrlKey || ev.metaKey) return;
        const tag = (ev.target && ev.target.tagName) || '';
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
        const key = ev.key;
        if (key === 'ArrowUp' || key === 'w' || key === 'W') { ev.preventDefault(); step(-1, 0); }
        else if (key === 'ArrowDown' || key === 's' || key === 'S') { ev.preventDefault(); step(1, 0); }
        else if (key === 'ArrowLeft' || key === 'a' || key === 'A') { ev.preventDefault(); step(0, -1); }
        else if (key === 'ArrowRight' || key === 'd' || key === 'D') { ev.preventDefault(); step(0, 1); }
        else if (key === 'z' || key === 'Z') { ev.preventDefault(); undo(); }
        else if (key === 'r' || key === 'R') { ev.preventDefault(); resetPuzzle(); }
      });

      // ---- 시작 ----
      const practiceNote = $('practiceNote');
      renderLevels();
      renderStats();
      loadDaily();
      renderChips();
    })();
  </script>
</body>
</html>
"""


def build():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    built_at = now.strftime("%Y-%m-%d %H:%M KST")

    daily, practice = build_puzzles()
    practice_count = sum(len(v) for v in practice.values())
    if not (10 <= practice_count <= 15):
        raise SystemExit("[중단] 연습 퍼즐 수가 10~15개를 벗어났습니다: %d" % practice_count)

    payload = {
        "daily": [serializable(p) for p in daily],
        "practice": {k: [serializable(p) for p in v] for k, v in practice.items()},
        "levels": [{"key": l["key"], "label": l["label"]} for l in LEVELS],
        "practiceCount": practice_count,
    }
    data_json = safe_json_for_script(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__NAV_TABS__", NAV_TABS)
    html = html.replace("__DATA_JSON__", data_json.replace("</", "<\\/"))
    html = html.replace("__BUILT_AT__", esc(built_at))

    with open(MISSION_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(html))

    print("-> 'mission.html' 생성 완료 (오늘의 지도 %d개 풀 · 연습 %d개 · 최단/제한 BFS 검증 완료)"
          % (len(daily), practice_count))
    for spec in LEVELS:
        items = practice[spec["key"]]
        print("   · %s %d개: 최단 %s · 제한 %s"
              % (spec["label"], len(items),
                 "/".join(str(p["optimal"]) for p in items),
                 "/".join(str(p["limit"]) for p in items)))
    return len(daily), practice_count


if __name__ == "__main__":
    build()

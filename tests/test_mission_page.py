"""mission.html 실제 동작 검증 (Python Playwright).

- 390px·1280px에서 페이지 가로 넘침 0, 상단 탭과 우측 버튼이 겹치지 않는지 확인
- 페이지에 실린 지도 데이터로 최단 경로를 계산해 방향키로 실제 클리어
- 되돌리기·다시 시작·연습 스테이지 전환·결과 복사·테마 전환 확인
- 콘솔 오류 0

실행: python3 tests/test_mission_page.py
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import socket
import time
from collections import deque

from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.environ.get("CHROMIUM_EXECUTABLE") or os.path.expanduser(
    "~/.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell")

KEY = {(-1, 0): "ArrowUp", (1, 0): "ArrowDown", (0, -1): "ArrowLeft", (0, 1): "ArrowRight"}


def free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def route(puzzle):
    """지도 데이터만 보고 최단 경로(칸 목록)를 계산한다."""
    size = puzzle["size"]
    rows = puzzle["rows"]
    start = tuple(puzzle["start"])
    goal = tuple(puzzle["goal"])
    wps = [(w["r"], w["c"]) for w in puzzle["waypoints"]]
    index = {cell: i for i, cell in enumerate(wps)}
    full = (1 << len(wps)) - 1

    def open_cell(r, c):
        return 0 <= r < size and 0 <= c < size and rows[r][c] not in "#X"

    origin = (start, 0)
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
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if not open_cell(nr, nc):
                continue
            nmask = mask | (1 << index[(nr, nc)]) if (nr, nc) in index else mask
            nstate = ((nr, nc), nmask)
            if nstate not in prev:
                prev[nstate] = state
                queue.append(nstate)
    assert found is not None, "퍼즐을 풀 수 없습니다: %s" % puzzle["id"]
    path = []
    cur = found
    while cur is not None:
        path.append(cur[0])
        cur = prev[cur]
    return list(reversed(path))


async def read_puzzle(page):
    return await page.evaluate("""() => {
      const el = document.querySelector('#gameTitle');
      return {title: el ? el.textContent : ''};
    }""")


async def current_puzzle(page):
    return await page.evaluate("""() => {
      const rows = [];
      const cells = Array.from(document.querySelectorAll('#board .cell'));
      const n = Math.round(Math.sqrt(cells.length));
      for (let r = 0; r < n; r += 1) {
        let line = '';
        for (let c = 0; c < n; c += 1) {
          const el = cells[r * n + c];
          line += el.classList.contains('road') || el.classList.contains('park') ? '.'
            : el.classList.contains('cons') ? 'X' : '#';
        }
        rows.push(line);
      }
      const waypoints = Array.from(document.querySelectorAll('#board .mk-wp')).map((el) => {
        const cell = el.closest('.cell');
        return {r: Number(cell.dataset.r), c: Number(cell.dataset.c)};
      });
      const startEl = document.querySelector('#board .mk-start').closest('.cell');
      const goalEl = document.querySelector('#board .mk-goal').closest('.cell');
      return {
        size: n, rows: rows, waypoints: waypoints,
        start: [Number(startEl.dataset.r), Number(startEl.dataset.c)],
        goal: [Number(goalEl.dataset.r), Number(goalEl.dataset.c)],
      };
    }""")


async def play_to_win(page, puzzle):
    path = route(puzzle)
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        await page.keyboard.press(KEY[(r2 - r1, c2 - c1)])
    await page.wait_for_selector("#resultBox:not([hidden])", timeout=5000)
    return len(path) - 1


async def check_width(browser, base, width):
    context = await browser.new_context(viewport={"width": width, "height": 900},
                                        permissions=["clipboard-read", "clipboard-write"])
    page = await context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append("pageerror: %s" % e))
    page.on("console", lambda m: errors.append("console: %s" % m.text) if m.type == "error" else None)
    await page.goto(base + "/mission.html", wait_until="load")
    await page.wait_for_selector("#board .cell")

    layout = await page.evaluate("""() => {
      const de = document.documentElement;
      const visible = (el) => {
        if (!el) return false;
        const cs = getComputedStyle(el);
        const box = el.getBoundingClientRect();
        return cs.display !== 'none' && cs.visibility !== 'hidden' && box.width > 0;
      };
      const board = document.querySelector('#board').getBoundingClientRect();
      return {
        overflow: de.scrollWidth - de.clientWidth,
        menu: visible(document.querySelector('.ia-menu')),
        tabbar: visible(document.querySelector('.ia-tabbar')),
        current: (document.querySelector('.ia-current') || {}).textContent || '',
        activeNav: !!document.querySelector('.ia-menu-link.is-active, .ia-menu-btn.is-active'),
        sheetLinks: document.querySelectorAll('#iaSheet .ia-sheet-link').length,
        boardRight: Math.round(board.right),
        boardBottom: Math.round(board.bottom),
        tabbarTop: Math.round(document.querySelector('.ia-tabbar').getBoundingClientRect().top),
        bodyRight: Math.round(de.getBoundingClientRect().right),
      };
    }""")
    assert layout["overflow"] == 0, "%dpx 가로 넘침 %dpx" % (width, layout["overflow"])
    assert layout["sheetLinks"] == 12, "전체 메뉴가 12개가 아닙니다: %s" % layout["sheetLinks"]
    if width <= 768:
        assert layout["tabbar"] and not layout["menu"], "%dpx 모바일 내비 구성이 다릅니다" % width
        assert layout["current"].strip() == "퇴근길 미션", "%dpx 현재 페이지 표시: %s" % (width, layout["current"])
        assert layout["boardBottom"] <= layout["tabbarTop"], "%dpx 지도가 하단 탭 바에 가립니다" % width
    else:
        assert layout["menu"] and not layout["tabbar"], "%dpx PC 내비 구성이 다릅니다" % width
        assert layout["activeNav"], "%dpx 현재 메뉴가 활성 표시되지 않았습니다" % width
    assert layout["boardRight"] <= layout["bodyRight"], "%dpx 에서 지도가 화면을 넘칩니다" % width

    # 1) 실제 클리어
    puzzle = await current_puzzle(page)
    optimal = await page.evaluate("""() => Number(document.getElementById('moveText').textContent.split('/')[1])""")
    limit = optimal
    title = (await read_puzzle(page))["title"]
    moves = await play_to_win(page, puzzle)
    assert moves <= limit, "최단 경로가 제한을 넘습니다: %d > %d" % (moves, limit)
    info = await page.evaluate("""() => ({
      result: document.getElementById('resultBox').hidden,
      move: document.getElementById('moveText').textContent.trim(),
      share: document.getElementById('sharePreview').textContent,
      title: document.getElementById('resultTitle').textContent,
      done: document.querySelectorAll('#missionList .mitem.is-done').length,
    })""")
    assert info["result"] is False, "클리어 후 결과 상자가 열리지 않았습니다"
    assert info["move"].startswith("%d /" % moves), "이동 수 표시가 어긋납니다: %s" % info["move"]
    assert info["done"] == len(puzzle["waypoints"]) + 1, "미션 완료 표시가 어긋납니다"
    assert title in info["share"] or "퇴근길 미션" in info["share"], "공유 문구 제목 누락"
    assert "Arrow" not in info["share"] and "→" not in info["share"], "공유 문구에 경로가 들어갔습니다"
    assert "ⓐ" not in info["share"]

    # 2) 결과 복사
    await page.click("#copyBtn")
    await page.wait_for_timeout(300)
    clip = await page.evaluate("""async () => {
      try { return await navigator.clipboard.readText(); } catch (e) { return null; }
    }""")
    button_text = (await page.inner_text("#copyBtn")).strip()
    assert button_text in ("복사됨", "결과 복사"), "복사 버튼 상태가 이상합니다: %s" % button_text
    if clip is not None:
        assert "퇴근길 미션" in clip, "클립보드에 결과 문구가 들어가지 않았습니다"

    # 3) 다시 시작 → 결과 닫힘, 이동 0
    await page.click("#resetBtn")
    reset_state = await page.evaluate("""() => ({
      hidden: document.getElementById('resultBox').hidden,
      move: document.getElementById('moveText').textContent.trim(),
    })""")
    assert reset_state["hidden"] is True, "다시 시작 후 결과 상자가 닫히지 않았습니다"
    assert reset_state["move"].startswith("0 /"), "다시 시작 후 이동 수가 0이 아닙니다: %s" % reset_state["move"]

    # 4) 이동 1회 후 되돌리기
    puzzle = await current_puzzle(page)
    path = route(puzzle)
    (r1, c1), (r2, c2) = path[0], path[1]
    await page.keyboard.press(KEY[(r2 - r1, c2 - c1)])
    moved = await page.evaluate("""() => document.getElementById('moveText').textContent.trim()""")
    assert moved.startswith("1 /"), "이동이 반영되지 않았습니다: %s" % moved
    await page.click("#undoBtn")
    undone = await page.evaluate("""() => document.getElementById('moveText').textContent.trim()""")
    assert undone.startswith("0 /"), "되돌리기가 동작하지 않았습니다: %s" % undone

    # 5) 연습 스테이지 전환
    await page.click(".seg-btn[data-level='adv']")
    await page.click("#stageChips .stage[data-slot='2']")
    practice = await page.evaluate("""() => ({
      kicker: document.getElementById('gameKicker').textContent,
      title: document.getElementById('gameTitle').textContent,
      back: document.getElementById('backDaily').hidden,
      move: document.getElementById('moveText').textContent.trim(),
      active: document.querySelectorAll('#stageChips .stage.active').length,
    })""")
    assert practice["kicker"] == "연습 스테이지", practice
    assert "고급 3번" in practice["title"], practice
    assert practice["back"] is False, "연습 모드에서 돌아가기 버튼이 숨겨져 있습니다"
    assert practice["move"].startswith("0 /"), practice
    assert practice["active"] == 1, "선택한 스테이지 표시가 없습니다"

    # 6) 연습 스테이지도 클리어 가능한지 확인
    puzzle = await current_puzzle(page)
    limit = int((await page.evaluate("""() => document.getElementById('moveText').textContent""")).split("/")[1])
    moves = await play_to_win(page, puzzle)
    assert moves <= limit, "연습 최단 경로가 제한을 넘습니다: %d > %d" % (moves, limit)

    # 7) 오늘의 미션으로 복귀
    await page.click("#backDaily")
    back = await page.evaluate("""() => ({
      kicker: document.getElementById('gameKicker').textContent,
      title: document.getElementById('gameTitle').textContent,
    })""")
    assert back["kicker"] == "오늘의 미션", back

    # 8) 테마 전환
    before = await page.get_attribute("html", "data-theme")
    await page.click("#themeToggle")
    after = await page.get_attribute("html", "data-theme")
    assert before != after, "테마가 바뀌지 않았습니다"

    # 9) 인접하지 않은 칸 탭 → 이동하지 않음
    await page.click("#resetBtn")
    before_move = await page.evaluate("""() => document.getElementById('moveText').textContent.trim()""")
    await page.click("#board .cell:nth-child(25)")
    after_move = await page.evaluate("""() => document.getElementById('moveText').textContent.trim()""")
    assert before_move == after_move, "멀리 떨어진 칸을 눌렀는데 이동했습니다"

    assert errors == [], "%dpx 브라우저 오류: %s" % (width, errors)
    await context.close()
    print("mission %dpx 통과 (최단 %d수 · 제한 %d수 · 메뉴 %d개)" % (width, moves, limit, layout["sheetLinks"]))


async def main():
    port = free_port()
    server = subprocess.Popen([sys.executable, "-u", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                              cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(executable_path=CHROME)
            for width in (390, 1280):
                await check_width(browser, "http://127.0.0.1:%d" % port, width)
            await browser.close()
    finally:
        server.terminate()


if __name__ == "__main__":
    asyncio.run(main())

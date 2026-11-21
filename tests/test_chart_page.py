"""chart.html 실제 동작 검증 (Python Playwright).

- 390px·1280px: 가로 넘침 0, 상단 12탭과 우측 버튼이 겹치지 않음, 현재 탭 표시
- 단서 보기 → 이동평균선 표시 → 정답 선택 → 실제 기간·종목·출처 공개
- 새로고침해도 공개 상태·기록 유지, ?id= 공유 링크로 다른 차트 열기
- 오답·정답 보기(포기) 흐름, 콘솔 오류 0

실행: python3 tests/test_chart_page.py
"""
import asyncio
import os
import socket
import subprocess
import sys
import time

from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.environ.get("CHROMIUM_EXECUTABLE") or os.path.expanduser(
    "~/.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell")


def free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


async def read_state(page):
    return await page.evaluate("""() => {
      const ep = byId[currentId];
      return {
        id: currentId,
        total: DATA.length,
        solved: document.getElementById('solvedStat').textContent.trim(),
        rate: document.getElementById('rateStat').textContent.trim(),
        streak: document.getElementById('statStreak').textContent.trim(),
        open: document.querySelectorAll('#clueList .clue.open').length,
        dots: document.querySelectorAll('#cDots .dot.on').length,
        nextLabel: document.getElementById('nextClue').textContent.trim(),
        futureBars: document.querySelectorAll('#chartSvg .candle-up.is-future, #chartSvg .candle-down.is-future').length,
        maGroupOn: document.getElementById('chartSvg').classList.contains('show-ma'),
        maLine: document.querySelectorAll('#chartSvg .ma-line').length,
        axisNote: document.getElementById('axisNote').textContent,
        resultHidden: document.getElementById('resultBox').hidden,
        badge: document.getElementById('resultBadge').textContent.trim(),
        title: document.getElementById('resultTitle').textContent.trim(),
        period: document.getElementById('revealPeriod').textContent.trim(),
        name: document.getElementById('revealName').textContent.trim(),
        future: document.getElementById('revealFuture').textContent.trim(),
        source: document.getElementById('revealSource').textContent.trim(),
        href: document.getElementById('revealSource').getAttribute('href'),
        answer: ep.quiz.answer,
        answerText: ep.quiz.choices[ep.quiz.answer],
        share: document.getElementById('sharePreview').textContent,
        todayHidden: document.getElementById('pToday').hidden,
        locked: document.querySelectorAll('#options .opt:disabled').length,
        wrongMarks: document.querySelectorAll('#options .opt.is-wrong').length,
        correctMarks: document.querySelectorAll('#options .opt.is-correct').length,
      };
    }""")


async def check_width(browser, base, width):
    context = await browser.new_context(viewport={"width": width, "height": 900},
                                        permissions=["clipboard-read", "clipboard-write"])
    page = await context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append("pageerror: %s" % e))
    page.on("console", lambda m: errors.append("console: %s" % m.text) if m.type == "error" else None)
    await page.goto(base + "/chart.html", wait_until="load")
    await page.wait_for_function("() => typeof currentId !== 'undefined' && !!currentId", timeout=5000)

    layout = await page.evaluate("""() => {
      const de = document.documentElement;
      const visible = (el) => {
        if (!el) return false;
        const cs = getComputedStyle(el);
        const box = el.getBoundingClientRect();
        return cs.display !== 'none' && cs.visibility !== 'hidden' && box.width > 0;
      };
      const svg = document.getElementById('chartSvg').getBoundingClientRect();
      return {
        overflow: de.scrollWidth - de.clientWidth,
        menu: visible(document.querySelector('.ia-menu')),
        tabbar: visible(document.querySelector('.ia-tabbar')),
        current: (document.querySelector('.ia-current') || {}).textContent || '',
        activeNav: !!document.querySelector('.ia-menu-link.is-active, .ia-menu-btn.is-active'),
        sheetLinks: document.querySelectorAll('#iaSheet .ia-sheet-link').length,
        svgRight: Math.round(svg.right), bodyRight: Math.round(de.getBoundingClientRect().right),
        svgHeight: Math.round(svg.height),
      };
    }""")
    assert layout["overflow"] == 0, "%dpx 가로 넘침 %dpx" % (width, layout["overflow"])
    assert layout["sheetLinks"] == 12, "%dpx 전체 메뉴가 12개가 아닙니다: %s" % (width, layout["sheetLinks"])
    if width <= 768:
        assert layout["tabbar"] and not layout["menu"], "%dpx 모바일 내비 구성이 다릅니다" % width
        assert layout["current"].strip() == "차트 추리실", "%dpx 현재 페이지 표시: %s" % (width, layout["current"])
    else:
        assert layout["menu"] and not layout["tabbar"], "%dpx PC 내비 구성이 다릅니다" % width
        assert layout["activeNav"], "%dpx 현재 메뉴가 활성 표시되지 않았습니다" % width
    assert layout["svgRight"] <= layout["bodyRight"], "%dpx 차트가 화면을 넘습니다" % width

    start = await read_state(page)
    assert start["total"] >= 14, "차트가 14개 미만입니다"
    assert start["open"] == 0 and start["dots"] == 0, "처음에는 단서가 닫혀 있어야 합니다"
    assert start["futureBars"] == 0, "정답 전에 가려진 구간이 그려졌습니다"
    assert start["maLine"] == 0, "정답 전에 이동평균선이 그려졌습니다"
    assert start["resultHidden"] is True
    assert "가격은 정답 확인 뒤" in start["axisNote"], start["axisNote"]
    assert start["todayHidden"] is False, "기본으로 오늘의 차트가 열려야 합니다"

    # 단서 1 → 이동평균선 표시
    await page.click("#nextClue")
    await page.wait_for_function("() => document.querySelectorAll('#clueList .clue.open').length === 1")
    one = await read_state(page)
    assert one["dots"] == 1, "단서 점 표시가 어긋납니다"
    assert one["maLine"] == 2 and one["maGroupOn"], "단서를 열면 이동평균선이 보여야 합니다"
    assert "2/3" in one["nextLabel"], one["nextLabel"]

    await page.click("#nextClue")
    await page.click("#nextClue")
    await page.wait_for_function("() => document.querySelectorAll('#clueList .clue.open').length === 3")
    three = await read_state(page)
    assert three["nextLabel"] == "단서 모두 열림" and three["dots"] == 3, three["nextLabel"]

    # 정답 선택 → 기간·종목·출처 공개
    await page.click('#options .opt[data-idx="%d"]' % start["answer"])
    await page.locator("#resultBox:not([hidden])").wait_for(timeout=5000)
    won = await read_state(page)
    assert won["badge"] == "정답" and won["title"] == "정답입니다", (won["badge"], won["title"])
    assert won["name"] and won["period"] and won["future"], "공개 정보 누락"
    assert won["href"].startswith("https://"), "출처 링크가 없습니다"
    assert won["source"] in ("Yahoo Finance 일별 시세", "Yahoo Finance 주별 시세") or won["source"].startswith("Yahoo Finance")
    assert won["futureBars"] > 0, "정답 후 가려진 구간이 보이지 않습니다"
    assert won["correctMarks"] == 1 and won["locked"] == 4, "정답 표시·선택 잠금"
    assert won["solved"] == "1 / %d" % won["total"], won["solved"]
    assert won["streak"] == "1", won["streak"]
    assert "가격이 공개되었습니다" in won["axisNote"], won["axisNote"]
    assert "/chart.html?id=" + won["id"] in won["share"], "공유 링크에 차트 ID 누락"
    assert won["answerText"] not in won["share"] and won["name"] not in won["share"], "공유 문구가 정답을 흘립니다"

    # 새로고침 → 공개 상태·기록 유지
    await page.reload(wait_until="load")
    await page.wait_for_function("() => typeof currentId !== 'undefined' && !!currentId", timeout=5000)
    again = await read_state(page)
    assert again["id"] == won["id"], "새로고침 후 다른 차트가 열렸습니다"
    assert again["resultHidden"] is False and again["badge"] == "정답", "공개 상태가 유지되지 않았습니다"
    assert again["open"] == 3 and again["futureBars"] > 0, "단서·가려진 구간이 유지되지 않았습니다"
    assert again["solved"] == "1 / %d" % again["total"], "해결 기록이 사라졌습니다"

    # 오답 흐름: 다른 차트를 ?id= 로 열어 일부러 틀린 답 선택
    other = await page.evaluate("""() => {
      const card = Array.from(document.querySelectorAll('#arcGrid .arc-card')).find(c => c.dataset.id !== currentId);
      return card.dataset.id;
    }""")
    await page.goto(base + "/chart.html?id=" + other, wait_until="load")
    await page.wait_for_function("(id) => typeof currentId !== 'undefined' && currentId === id", arg=other)
    fresh = await read_state(page)
    assert fresh["id"] == other and fresh["resultHidden"] is True
    wrong = (fresh["answer"] + 1) % 4
    await page.click('#options .opt[data-idx="%d"]' % wrong)
    await page.locator("#resultBox:not([hidden])").wait_for(timeout=5000)
    lost = await read_state(page)
    assert lost["badge"] == "아쉬움", lost["badge"]
    assert lost["wrongMarks"] == 1 and lost["correctMarks"] == 1, "오답·정답 표시"
    assert lost["solved"] == "1 / %d" % lost["total"], "오답인데 해결 수가 늘었습니다"
    assert lost["streak"] == "0", "오답인데 연속 정답이 남아 있습니다"
    assert lost["name"] and lost["futureBars"] > 0, "오답 뒤에도 공개되어야 합니다"

    # 정답 보기(포기): 해결 수는 그대로, 기록에는 '정답 확인'
    third = await page.evaluate("""() => {
      const card = Array.from(document.querySelectorAll('#arcGrid .arc-card'))
        .find(c => !store.records[c.dataset.id].revealed);
      return card ? card.dataset.id : null;
    }""")
    assert third, "포기를 시험할 미도전 차트가 없습니다"
    await page.goto(base + "/chart.html?id=" + third, wait_until="load")
    await page.wait_for_function("(id) => typeof currentId !== 'undefined' && currentId === id", arg=third)
    await page.click("#giveUp")
    await page.locator("#resultBox:not([hidden])").wait_for(timeout=5000)
    gave = await read_state(page)
    assert gave["badge"] == "정답 공개", gave["badge"]
    assert gave["solved"] == "1 / %d" % gave["total"], "포기인데 해결 수가 늘었습니다"
    assert gave["futureBars"] > 0 and gave["name"], "포기 뒤 공개 누락"

    # 아카이브 카드 → 그 차트로 전환 + ?id 갱신
    await page.click("#arcGrid .arc-card[data-id='%s']" % start["id"])
    await page.wait_for_function("(id) => currentId === id", arg=start["id"])
    assert "?id=" + start["id"] in page.url, "아카이브 이동 후 URL 이 갱신되지 않았습니다"

    # 분야 필터
    await page.click("#catFilter .chip[data-cat='domestic']")
    visible = await page.evaluate("""() => Array.from(document.querySelectorAll('#arcGrid .arc-card')).filter(c => !c.hidden).length""")
    assert visible == 4, "분야 필터 결과가 %d개입니다" % visible
    await page.click("#catFilter .chip[data-cat='bigtech']")
    visible = await page.evaluate("""() => Array.from(document.querySelectorAll('#arcGrid .arc-card')).filter(c => !c.hidden).length""")
    assert visible == 4, "분야 필터 결과가 %d개입니다" % visible

    # 테마 전환
    before = await page.get_attribute("html", "data-theme")
    await page.click("#themeToggle")
    after = await page.get_attribute("html", "data-theme")
    assert before != after, "테마가 바뀌지 않았습니다"

    assert errors == [], "%dpx 브라우저 오류: %s" % (width, errors)
    await context.close()
    print("chart %dpx 통과 (메뉴 %d개 · 차트 %d개 · 공개 %s · 가려진 %s)"
          % (width, layout["sheetLinks"], start["total"], won["name"], won["future"]))


async def main():
    port = free_port()
    server = subprocess.Popen([sys.executable, "-u", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                              cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
            try:
                for width in (390, 1280):
                    await check_width(browser, "http://127.0.0.1:%d" % port, width)
            finally:
                await browser.close()
    finally:
        server.terminate()


if __name__ == "__main__":
    asyncio.run(main())

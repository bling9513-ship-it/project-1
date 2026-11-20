#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'이번 주 우선 조치' 행 → CVE 카드 이동 회귀 테스트 (Playwright/Chromium).

확인 항목 (390px · 1280px)
  1) 검색어로 대상 카드를 숨긴 상태에서 키보드 Tab + Enter 로 행을 활성화하면
     검색어·필터가 초기화되고, 대상 카드로 스크롤되며 document.activeElement 가 그 카드가 된다.
  2) 필터(Critical 등)로 숨긴 상태에서 마우스 클릭으로 행을 눌러도 같은 동작을 한다.
  3) 이동 중 CSP 위반·콘솔 오류가 없다.

사용법: python3 tests/cve_priority_nav.py
(저장소의 다른 테스트는 node 기반이지만, 이 검증은 로컬 환경에 node 없이도 돌도록 파이썬으로 작성)
"""
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [(390, 900), (1280, 900)]


def wait_ready(page):
    page.wait_for_function("() => document.querySelectorAll('#cveList .cve-card').length > 0")


def pick_row(page, index=0):
    return page.evaluate(
        """(i) => {
            const rows = Array.from(document.querySelectorAll('.priority-list a.priority-row'));
            if (!rows[i]) return null;
            const cid = rows[i].getAttribute('data-cve');
            const it = (window.CVE_ITEMS || []).find(x => x.cve_id === cid);
            return { cid, severity: it ? it.severity : null, index: i, href: rows[i].getAttribute('href') };
        }""",
        index,
    )


def assert_jumped(page, cid, label):
    page.wait_for_function(
        """(cid) => {
            const el = document.getElementById('cve-' + cid);
            return !!el && document.activeElement === el;
        }""",
        arg=cid,
        timeout=5000,
    )
    page.wait_for_function(
        """(cid) => {
            const el = document.getElementById('cve-' + cid);
            const r = el.getBoundingClientRect();
            return r.top >= 0 && r.top < 220;
        }""",
        arg=cid,
        timeout=5000,
    )
    state = page.evaluate(
        """(cid) => {
            const el = document.getElementById('cve-' + cid);
            return {
                activeId: document.activeElement ? document.activeElement.id : null,
                focused: el.classList.contains('is-focused'),
                scrollY: Math.round(window.scrollY),
                term: document.getElementById('searchInput').value,
                visible: document.getElementById('visibleCount').textContent,
                cards: document.querySelectorAll('#cveList .cve-card').length,
                activeFilter: (document.querySelector('.segment-btn.active') || {}).dataset?.filter || null,
            };
        }""",
        arg=cid,
    )
    assert state["activeId"] == "cve-" + cid, f"{label}: activeElement={state['activeId']}"
    assert state["focused"] is True, f"{label}: is-focused 하이라이트 없음"
    assert state["term"] == "", f"{label}: 검색어가 초기화되지 않음({state['term']})"
    assert state["activeFilter"] == "all", f"{label}: 필터가 초기화되지 않음({state['activeFilter']})"
    assert int(state["visible"]) == state["cards"] > 1, f"{label}: 목록이 전체로 복원되지 않음({state})"
    print(f"  {label}: activeElement=cve-{cid}, scrollY={state['scrollY']}, visible={state['visible']}")


def run_width(browser, base, width, height):
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text)
            if m.type == "error" and not m.text.startswith("Failed to load resource:") else None)
    page.add_init_script(
        """window.navCsp = []; window.addEventListener('securitypolicyviolation', e => window.navCsp.push(e.effectiveDirective));"""
    )
    page.goto(f"{base}/cve.html", wait_until="load")
    wait_ready(page)

    print(f"[{width}px]")

    # 1) 검색어로 대상 카드를 숨긴 뒤 키보드 Tab + Enter
    row = pick_row(page, 0)
    assert row and row["href"] == "#cve-" + row["cid"], f"priority row link/href 없음: {row}"
    page.fill("#searchInput", "zzzz-no-such-cve")
    page.wait_for_function("() => document.querySelectorAll('#cveList .cve-card').length === 0")
    assert page.locator(f"#cve-{row['cid']}").count() == 0, "검색으로 숨겨지지 않음"

    page.evaluate("() => document.activeElement.blur()")
    for _ in range(60):
        active = page.evaluate(
            "() => document.activeElement && document.activeElement.classList.contains('priority-row')")
        if active:
            break
        page.keyboard.press("Tab")
        time.sleep(0.01)
    else:
        raise AssertionError("Tab 으로 우선 조치 행에 도달하지 못함")
    focused_row = page.evaluate(
        "() => document.activeElement.getAttribute('data-cve')")
    assert focused_row == row["cid"], f"Tab 포커스 대상이 다름({focused_row})"
    page.keyboard.press("Enter")
    assert_jumped(page, row["cid"], "키보드 Tab+Enter (검색 숨김)")

    # 2) 필터로 대상 카드를 숨긴 뒤 마우스 클릭
    page.goto(f"{base}/cve.html", wait_until="load")
    wait_ready(page)
    row2 = None
    for idx in range(7):
        cand = pick_row(page, idx)
        if not cand:
            continue
        hide_filter = "high" if cand["severity"] == "CRITICAL" else "critical"
        page.click(f'.segment-btn[data-filter="{hide_filter}"]')
        if page.locator(f"#cve-{cand['cid']}").count() == 0:
            row2 = cand
            break
    assert row2, "필터로 숨길 수 있는 대상 행을 찾지 못함"
    page.click(f'.priority-row[data-cve="{row2["cid"]}"]')
    assert_jumped(page, row2["cid"], "마우스 클릭 (필터 숨김)")

    csp = page.evaluate("() => window.navCsp")
    assert csp == [], f"CSP 위반: {csp}"
    assert errors == [], f"브라우저 오류: {errors}"
    print(f"  CSP·콘솔 오류 없음")
    context.close()


def main():
    probe = subprocess.run(
        [sys.executable, "-c",
         "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1]);s.close()"],
        capture_output=True, text=True, check=True)
    port = probe.stdout.strip()
    server = subprocess.Popen(
        [sys.executable, "-u", "-m", "http.server", port, "--bind", "127.0.0.1"],
        cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        time.sleep(0.6)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for width, height in TARGETS:
                run_width(browser, base, width, height)
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
    print("CVE 우선 조치 카드 이동 테스트 통과 (390px · 1280px).")


if __name__ == "__main__":
    main()

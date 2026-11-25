#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""자취방 입주 점검 카드(movein.html) 데이터·화면 검증.

확인하는 것
  · 점검 항목
      - 5구역(현관·거실/방·주방·욕실·베란다/외부) · 25항목 이상 · ID 중복 없음
      - 항목마다 제목과 '확인 방법' 문구가 있음
      - 수압·배수·결로·창문·계량기 5가지 핵심 확인 그림이 모두 항목에 연결됨
  · movein.html
      - data-page="movein" · 전체 메뉴 30페이지 · 이모지 0 · 그라데이션 0 · 인라인 핸들러 0
      - 항목 30개 · 상태 버튼 3종 × 항목 수 · 메모 입력 · 진행률 요소
      - localStorage 키 · Canvas 리포트 함수 · 텍스트/PNG 버튼 · 2단계 초기화
      - 하자 요약 목록과 모바일 하단 바

실행: python3 tests/test_movein_report.py
"""
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import build_movein_html as mv

HTML = os.path.join(BASE_DIR, "movein.html")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
SHEET_PAGES = 30

failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def check_data():
    print("== 점검 항목 ==")
    sections = mv.SECTIONS
    check("구역 5개", len(sections) == 5, len(sections))
    names = [section["name"] for section in sections]
    check("구역 이름", names == ["현관", "거실·방", "주방", "욕실", "베란다·외부"], names)
    total = sum(len(section["items"]) for section in sections)
    check("항목 25개 이상", total >= 25, total)
    ids = [item["id"] for section in sections for item in section["items"]]
    check("항목 ID 중복 없음", len(ids) == len(set(ids)), len(ids))
    keys = set()
    for section in sections:
        for item in section["items"]:
            check("%s 제목" % item["id"], bool(item["title"]))
            check("%s 확인 방법" % item["id"], len(item["how"]) >= 8, item["how"])
            if item.get("key"):
                keys.add(item["key"])
    check("핵심 그림 5종 연결", keys == set(mv.GUIDE_SVG), sorted(keys))
    check("상태 3종", [key for key, _label in mv.STATES] == ["ok", "issue", "na"], mv.STATES)
    mv.validate()
    print("  구역 %d · 항목 %d · 그림 %d" % (len(sections), total, len(mv.GUIDE_SVG)))


def check_html():
    print("== movein.html ==")
    html = read(HTML)
    payload = mv.payload_for()
    check("data-page", 'data-page="movein"' in html)
    check("이모지 0", not EMOJI_RE.search(html), EMOJI_RE.findall(html)[:3])
    check("그라데이션 0", "linear-gradient" not in html and "radial-gradient" not in html)
    check("인라인 핸들러 0", not re.search(r'\son(click|load|change|input|submit|keydown)=', html, re.I))
    check("전체 메뉴 30페이지", html.count('class="ia-sheet-link') - html.count('class="ia-sheet-links"') == SHEET_PAGES,
          html.count('class="ia-sheet-link') - html.count('class="ia-sheet-links"'))
    items = html.count('class="mv-item"')
    check("항목 카드 %d개" % payload["total"], items == payload["total"], items)
    check("상태 버튼 3×항목", html.count('class="mv-seg-btn"') == payload["total"] * 3,
          html.count('class="mv-seg-btn"'))
    check("문구 3종", all(('data-state="%s"' % key) in html for key, _label in mv.STATES))
    check("메모 입력", 'class="mv-note"' in html and 'maxlength="120"' in html)
    check("진행률", 'id="mvPercent"' in html and 'id="mvBarFill"' in html)
    check("하자 요약", 'id="mvIssueList"' in html and 'id="mvIssueBadge"' in html)
    check("localStorage 키", mv.STORE_KEY in html)
    check("Canvas 리포트", 'createElement(\'canvas\')' in html and 'toDataURL' in html)
    check("PNG 다운로드 이름", "link.download" in html and "입주점검_" in html)
    check("텍스트 복사", 'id="mvCopy"' in html and "navigator.clipboard" in html)
    check("2단계 초기화", "resetArmed" in html and "한 번 더 누르면" in html)
    check("모바일 하단 바", 'id="mvMobileBar"' in html and 'id="mvMobilePng"' in html)
    check("구역 5개 렌더", html.count('class="mv-section"') == 5, html.count('class="mv-section"'))
    check("주소·점검일 입력", 'id="mvAddress"' in html and 'id="mvDate"' in html)
    print("  항목 %d · 상태 버튼 %d · 구역 5" % (items, payload["total"] * 3))


def main():
    check_data()
    check_html()
    if failures:
        print("\n실패 %d건: %s" % (len(failures), failures))
        sys.exit(1)
    print("\n입주 점검 카드 검증 통과 (%d항목 · 전체 메뉴 %d페이지)" % (mv.payload_for()["total"], SHEET_PAGES))


if __name__ == "__main__":
    main()

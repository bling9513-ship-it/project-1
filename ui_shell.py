# -*- coding: utf-8 -*-
"""Infosec Archive 공통 UI 셸(내비게이션·모바일 하단 탭 바·전체 메뉴 시트).

31개 페이지 빌더가 각자 복사해 두던 상단 내비게이션을 한 곳에서 만든다.
빌더는 페이지 HTML 을 완성한 뒤 `apply(html, page_key)` 를 한 번 통과시키고,
그 결과를 `harden_html()` 에 넘긴다(CSP 해시는 harden 단계에서 다시 계산된다).

- 데스크톱(>768px): 브랜드 + 대표 5개 진입점(채용공고·시험 공부 + 3개 드롭다운)
- 모바일(<=768px): 간결한 헤더(로고·현재 페이지·테마) + 하단 고정 5탭 바 + 전체 메뉴 시트
- 게임 메뉴는 '챌린지 / 미니게임' 소제목으로 묶는다(데스크톱 드롭다운·모바일 시트 공통).
- 시트: 카테고리별 27개 페이지, 딤 클릭·닫기 버튼·Escape 로 닫기, 포커스 이동/복귀,
  배경 스크롤 잠금, 슬라이드 업. `prefers-reduced-motion` 에서는 모두 즉시 전환.
- 모바일 `게임` 탭은 wargame.html 로 이동하지 않고 시트의 게임 목록으로 스크롤·포커스한다.
"""
import re

import monetization

# key, 파일, 표시 이름, 짧은 이름(모바일 헤더)
PAGES = [
    ("today", "today.html", "오늘", "오늘"),
    ("market", "market.html", "증시 이슈", "증시 이슈"),
    ("index", "index.html", "채용공고", "채용공고"),
    ("study", "study.html", "시험 공부", "시험 공부"),
    ("ai", "ai.html", "AI 트렌드", "AI 트렌드"),
    ("cve", "cve.html", "CVE 리포트", "CVE 리포트"),
    ("tools", "tools.html", "실무 유틸", "실무 유틸"),
    ("reference", "security-reference.html", "점검 백과사전", "점검 백과"),
    ("radar", "radar.html", "피싱 레이더", "피싱 레이더"),
    ("outfit", "outfit.html", "옷차림", "옷차림"),
    ("pick", "pick.html", "오늘 뭐 먹지", "오늘 뭐 먹지"),
    ("wargame", "wargame.html", "워게임", "워게임"),
    ("clue", "clue.html", "3단서 추리", "3단서 추리"),
    ("mission", "mission.html", "퇴근길 미션", "퇴근길 미션"),
    ("chart", "chart.html", "차트 추리실", "차트 추리실"),
    ("ops", "ops.html", "60초 관제실", "60초 관제실"),
    ("seat", "seat.html", "막차 자리 배치", "막차 자리 배치"),
    ("load", "load.html", "한 번 더 싣기", "한 번 더 싣기"),
    ("arcade", "arcade.html", "아케이드", "아케이드"),
    ("hangul", "hangul.html", "한글 한 칸", "한 칸 변신"),
    ("cards", "cards.html", "오늘의 카드", "오늘의 카드"),
    ("wash", "wash.html", "세탁 라벨 읽기", "세탁 라벨"),
    ("recycle", "recycle.html", "분리배출 읽기", "분리배출"),
    ("food", "food.html", "식품 라벨 읽기", "식품 라벨"),
    ("grocery", "grocery.html", "장보기 타이밍", "장보기"),
    ("paymeter", "paymeter.html", "월급 미터", "월급 미터"),
    ("subway", "subway.html", "지하철역 맞히기", "지하철역"),
    ("basket", "basket.html", "장바구니 리그", "장바구니"),
    ("mystery90", "mystery90.html", "90초 추리", "90초 추리"),
    ("movein", "movein.html", "입주 점검", "입주 점검"),
    ("nearby", "nearby.html", "지금 갈 곳", "지금 갈 곳"),
]

PAGE_FILE = {key: file for key, file, _label, _short in PAGES}
PAGE_LABEL = {key: label for key, _file, label, _short in PAGES}
PAGE_SHORT = {key: short for key, _file, _label, short in PAGES}

# 게임 메뉴의 소제목 묶음 — 데스크톱 드롭다운과 모바일 시트 모두 '챌린지 / 미니게임' 으로 통일한다.
GAME_GROUPS = [
    ("챌린지", ["wargame", "clue", "mystery90", "mission", "chart", "subway"]),
    ("미니게임", ["arcade", "ops", "seat", "load", "hangul"]),
]

# 모바일 시트에서 바로 열어 줄 묶음(하단 `게임` 탭) — 시트 안 그룹 제목에 id 를 붙인다.
SHEET_GROUP_IDS = {"게임": "iaSheetGroupGame"}
GAME_TAB_TARGET = SHEET_GROUP_IDS["게임"]

# 데일리·생활 묶음 — 셸 그룹과 데스크톱 드롭다운이 같은 목록을 쓴다.
DAILY_KEYS = ["outfit", "pick", "grocery", "basket", "paymeter", "movein", "nearby", "cards", "wash", "recycle", "food"]

# (그룹 이름, 항목 목록) — 항목은 페이지 키(str) 또는 (소제목, 페이지 키 목록).
# 데스크톱 드롭다운과 모바일 시트가 같은 분류를 쓴다.
GROUPS = [
    ("보안·채용", ["index", "study"]),
    ("브리핑·유틸", ["today", "market", "ai", "cve", "tools", "reference", "radar"]),
    ("데일리·생활", DAILY_KEYS),
    ("게임", GAME_GROUPS),
]

# 데스크톱 내비게이션의 드롭다운 그룹(대표 메뉴 3개)
DESKTOP_DROPDOWNS = [
    ("브리핑·트렌드", ["today", "market", "ai", "cve", "tools", "reference", "radar"]),
    ("데일리·생활", DAILY_KEYS),
    ("게임", GAME_GROUPS),
]

# 모바일 하단 탭 바 — (키, 라벨, 기본 링크, 이 탭이 활성인 페이지 키 목록, 아이콘 키)
MOBILE_TABS = [
    ("jobs", "채용", "index.html", ["index"], "briefcase"),
    ("study", "학습", "study.html", ["study"], "book"),
    ("brief", "브리핑", "today.html", ["today", "market", "ai", "cve", "tools", "reference", "radar"], "chart"),
    # href 가 None 이면 이동 대신 전체 시트의 게임 목록을 열어 준다.
    ("game", "게임", None, ["wargame", "clue", "mystery90", "mission", "chart", "subway", "ops", "seat", "load", "arcade", "hangul"], "game"),
]

ICONS = {
    "briefcase": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="3" y="7" width="18" height="13" rx="2.5"></rect>'
        '<path d="M8.5 7V5.6A1.6 1.6 0 0 1 10.1 4h3.8a1.6 1.6 0 0 1 1.6 1.6V7"></path>'
        '<path d="M3 12.5h18"></path></svg>'
    ),
    "book": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M4 5.5A2 2 0 0 1 6 4h5v16H6a2 2 0 0 1-2-1.5z"></path>'
        '<path d="M20 5.5A2 2 0 0 0 18 4h-5v16h5a2 2 0 0 0 2-1.5z"></path></svg>'
    ),
    "chart": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M4 19V5"></path><path d="M4 19h16"></path>'
        '<path d="M7.5 15.5l3.5-4 3 2.4L19 8"></path></svg>'
    ),
    "game": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="3" y="7.5" width="18" height="10" rx="4"></rect>'
        '<path d="M8 11v2.6M6.7 12.3h2.6"></path>'
        '<circle cx="16" cy="11.6" r="0.9" fill="currentColor" stroke="none"></circle>'
        '<circle cx="17.8" cy="13.4" r="0.9" fill="currentColor" stroke="none"></circle></svg>'
    ),
    "grid": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="4" y="4" width="6.5" height="6.5" rx="1.6"></rect>'
        '<rect x="13.5" y="4" width="6.5" height="6.5" rx="1.6"></rect>'
        '<rect x="4" y="13.5" width="6.5" height="6.5" rx="1.6"></rect>'
        '<rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.6"></rect></svg>'
    ),
}

_CHEVRON = (
    '<svg class="ia-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M6 9l6 6 6-6"></path></svg>'
)
_MOON = (
    '<svg id="moonIcon" width="17" height="17" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>'
)
_SUN = (
    '<svg id="sunIcon" style="display:none" width="17" height="17" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4.4"></circle>'
    '<path d="M12 2.4v2.2M12 19.4v2.2M4.2 4.2l1.6 1.6M18.2 18.2l1.6 1.6M2.4 12h2.2M19.4 12h2.2'
    'M4.2 19.8l1.6-1.6M18.2 5.8l1.6-1.6"></path></svg>'
)
_GITHUB = (
    '<svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 '
    '2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605'
    '-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 '
    '1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338'
    '-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098'
    '-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337'
    '1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 '
    '2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 '
    '2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path></svg>'
)
_CLOSE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg>'
)


def _flatten_keys(items):
    """항목 목록(페이지 키 / (소제목, 키 목록)) 을 페이지 키 목록으로 평탄화한다."""
    keys = []
    for item in items:
        if isinstance(item, str):
            keys.append(item)
        else:
            keys.extend(item[1])
    return keys


def _has_subgroups(items):
    return any(not isinstance(item, str) for item in items)


def _is_dropdown(key):
    for _title, items in DESKTOP_DROPDOWNS:
        if key in _flatten_keys(items):
            return True
    return False


def _desktop_menu(current):
    parts = ['<nav class="ia-menu" aria-label="주요 메뉴">']
    # 대표 메뉴: 채용공고 / 시험 공부
    for key in ("index", "study"):
        active = " is-active" if current == key else ""
        cur = ' aria-current="page"' if current == key else ""
        parts.append(
            '<a class="ia-menu-link{active}" href="{file}"{cur}>{label}</a>'.format(
                active=active, file=PAGE_FILE[key], cur=cur, label=PAGE_LABEL[key]
            )
        )
    for title, items in DESKTOP_DROPDOWNS:
        keys = _flatten_keys(items)
        group_active = " is-active" if current in keys else ""
        expanded = "true" if current in keys else "false"
        parts.append('<div class="ia-menu-group">')
        parts.append(
            '<button type="button" class="ia-menu-btn{active}" aria-expanded="{exp}" '
            'aria-haspopup="true">{title}{chevron}</button>'.format(
                active=group_active, exp=expanded, title=title, chevron=_CHEVRON
            )
        )
        parts.append('<div class="ia-drop" role="menu">')

        def _drop_link(key):
            cur = ' aria-current="page"' if current == key else ""
            cls = "ia-drop-link is-current" if current == key else "ia-drop-link"
            return (
                '<a class="{cls}" role="menuitem" href="{file}"{cur}>{label}</a>'.format(
                    cls=cls, file=PAGE_FILE[key], cur=cur, label=PAGE_LABEL[key]
                )
            )

        if not _has_subgroups(items):
            for key in items:
                parts.append(_drop_link(key))
        else:
            first_sub = True
            for item in items:
                if isinstance(item, str):
                    parts.append(_drop_link(item))
                    continue
                sub_title, sub_keys = item
                if not first_sub:
                    parts.append('<div class="ia-drop-sep" aria-hidden="true"></div>')
                first_sub = False
                parts.append('<p class="ia-drop-label">{title}</p>'.format(title=sub_title))
                for key in sub_keys:
                    parts.append(_drop_link(key))
        parts.append("</div></div>")
    parts.append("</nav>")
    return "".join(parts)


def _mobile_tabs(current):
    tabbed = set()
    for _key, _label, _href, pages, _icon in MOBILE_TABS:
        tabbed.update(pages)
    # 탭이 없는 페이지(옷차림·오늘 뭐 먹지)는 '전체' 메뉴 안에 있으므로 전체를 활성으로 표시한다.
    all_active = " is-active" if current not in tabbed else ""
    parts = ['<nav class="ia-tabbar" aria-label="빠른 이동">']
    for tab_key, label, href, pages, icon in MOBILE_TABS:
        active = " is-active" if current in pages else ""
        cur = ' aria-current="page"' if current in pages else ""
        if href is None:
            parts.append(
                '<button type="button" class="ia-tab{active}" id="iaGameBtn" '
                'aria-haspopup="dialog" aria-controls="iaSheet" aria-expanded="false" '
                'data-sheet-target="{target}">'
                '<span class="ia-tab-icon">{icon}</span><span class="ia-tab-label">{label}</span>'
                '</button>'.format(
                    active=active, icon=ICONS[icon], label=label, target=GAME_TAB_TARGET
                )
            )
            continue
        parts.append(
            '<a class="ia-tab{active}" href="{href}"{cur}>'
            '<span class="ia-tab-icon">{icon}</span><span class="ia-tab-label">{label}</span></a>'.format(
                active=active, href=href, cur=cur, icon=ICONS[icon], label=label
            )
        )
    parts.append(
        '<button type="button" class="ia-tab{active}" id="iaAllBtn" aria-expanded="false" '
        'aria-controls="iaSheet"><span class="ia-tab-icon">{icon}</span>'
        '<span class="ia-tab-label">전체</span></button>'.format(
            active=all_active, icon=ICONS["grid"]
        )
    )
    parts.append("</nav>")
    return "".join(parts)


def _sheet(current):
    parts = [
        '<div class="ia-sheet-backdrop" id="iaSheetBackdrop" hidden></div>',
        '<section class="ia-sheet" id="iaSheet" role="dialog" aria-modal="true" '
        'aria-labelledby="iaSheetTitle" hidden>',
        '<div class="ia-sheet-head"><h2 class="ia-sheet-title" id="iaSheetTitle">전체 메뉴</h2>',
        '<button type="button" class="ia-sheet-close" id="iaSheetClose" '
        'aria-label="전체 메뉴 닫기">' + _CLOSE + "</button></div>",
        '<div class="ia-sheet-body">',
    ]
    def _sheet_link(key):
        cls = "ia-sheet-link"
        cur = ' aria-current="page"' if current == key else ""
        if current == key:
            cls += " is-current"
        return (
            '<a class="{cls}" href="{file}"{cur}><span>{label}</span>'
            '<span class="ia-sheet-file">{file}</span></a>'.format(
                cls=cls, file=PAGE_FILE[key], cur=cur, label=PAGE_LABEL[key]
            )
        )

    for title, items in GROUPS:
        group_id = SHEET_GROUP_IDS.get(title)
        if group_id:
            parts.append('<p class="ia-sheet-group" id="{gid}" tabindex="-1">{title}</p>'.format(
                gid=group_id, title=title
            ))
        else:
            parts.append('<p class="ia-sheet-group">{title}</p>'.format(title=title))
        if not _has_subgroups(items):
            parts.append('<div class="ia-sheet-links">')
            for key in items:
                parts.append(_sheet_link(key))
            parts.append("</div>")
            continue
        leading = [item for item in items if isinstance(item, str)]
        if leading:
            parts.append('<div class="ia-sheet-links">')
            for key in leading:
                parts.append(_sheet_link(key))
            parts.append("</div>")
        for item in items:
            if isinstance(item, str):
                continue
            sub_title, sub_keys = item
            parts.append('<p class="ia-sheet-sub">{title}</p>'.format(title=sub_title))
            parts.append('<div class="ia-sheet-links">')
            for key in sub_keys:
                parts.append(_sheet_link(key))
            parts.append("</div>")
    parts.append("</div></section>")
    return "".join(parts)


def render_header(current, meta_text=""):
    """페이지 상단 헤더(데스크톱 메뉴 + 모바일 헤더) HTML."""
    return (
        '<header class="ia-header">'
        '<div class="ia-header-inner">'
        '<a class="ia-brand" href="index.html" aria-label="Infosec Archive 홈">'
        '<img src="logo.png" alt="Infosec Archive 로고" class="ia-brand-img">'
        '<span class="ia-brand-name">Infosec Archive</span></a>'
        '<span class="ia-current">{short}</span>'.format(short=PAGE_SHORT.get(current, ""))
        + _desktop_menu(current)
        + '<div class="ia-actions">'
        '<span class="ia-meta">{meta}</span>'
        '<button type="button" class="ia-icon-btn" id="themeToggle" title="화면 테마 변경" '
        'aria-label="화면 테마 변경">'.format(meta=meta_text) + _MOON + _SUN + "</button>"
        '<a class="ia-icon-link" href="https://github.com/bling9513-ship-it/project-1" '
        'target="_blank" rel="noopener noreferrer" aria-label="GitHub 저장소 바로가기" '
        'title="GitHub 저장소 바로가기">' + _GITHUB + "</a>"
        "</div></div></header>"
    )


NAV_CSS = """
  /* ===== Infosec Archive 공통 셸 (ui_shell.py) ===== */
  :root {
    --ia-header-h: 60px;
    --ia-tabbar-h: 64px;
    --ia-ease: cubic-bezier(0.2, 0.8, 0.2, 1);
    --ia-press: 160ms cubic-bezier(0.2, 0.8, 0.2, 1);
  }

  .ia-header {
    position: sticky;
    top: 0;
    z-index: 60;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-default);
    -webkit-backdrop-filter: saturate(180%) blur(12px);
    backdrop-filter: saturate(180%) blur(12px);
  }

  .ia-header-inner {
    max-width: 1360px;
    margin: 0 auto;
    padding: 0 20px;
    height: var(--ia-header-h);
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .ia-brand {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    text-decoration: none;
    color: inherit;
    flex: 0 0 auto;
    border-radius: 10px;
    transition: transform var(--ia-press), opacity var(--ia-press);
  }
  .ia-brand:active { transform: scale(0.98); opacity: 0.86; }

  .ia-brand-img {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    object-fit: cover;
    display: block;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.16);
    flex-shrink: 0;
  }

  .ia-brand-name {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.035em;
    color: var(--text-primary);
    white-space: nowrap;
  }

  .ia-current { display: none; }

  .ia-menu {
    display: flex;
    align-items: center;
    gap: 2px;
    margin-left: 6px;
    flex: 1 1 auto;
    min-width: 0;
  }

  .ia-menu-link,
  .ia-menu-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 8px 12px;
    border: 0;
    border-radius: 10px;
    background: transparent;
    font-family: inherit;
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--text-secondary);
    text-decoration: none;
    cursor: pointer;
    white-space: nowrap;
    transition: background-color var(--ia-press), color var(--ia-press), transform var(--ia-press);
  }

  .ia-menu-link:hover,
  .ia-menu-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
  .ia-menu-link:active,
  .ia-menu-btn:active { transform: scale(0.98); }

  .ia-menu-link.is-active,
  .ia-menu-btn.is-active {
    color: var(--text-primary);
    background: var(--bg-subtle);
  }

  .ia-chevron {
    width: 14px;
    height: 14px;
    color: var(--text-muted);
    transition: transform var(--ia-press);
  }
  .ia-menu-group.is-open .ia-chevron { transform: rotate(180deg); }

  .ia-menu-group { position: relative; }

  .ia-drop {
    position: absolute;
    top: calc(100% + 6px);
    left: 0;
    min-width: 214px;
    padding: 6px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: 14px;
    box-shadow: 0 18px 38px -18px rgba(15, 23, 42, 0.28), 0 2px 8px rgba(15, 23, 42, 0.06);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-4px);
    transition: opacity 150ms var(--ia-ease), transform 150ms var(--ia-ease), visibility 150ms;
    z-index: 65;
  }
  .ia-menu-group.is-open .ia-drop { opacity: 1; visibility: visible; transform: none; }

  .ia-drop-link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 9px 11px;
    border-radius: 9px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    text-decoration: none;
    transition: background-color 140ms var(--ia-ease), color 140ms var(--ia-ease);
  }
  .ia-drop-link:hover { background: var(--bg-subtle); color: var(--text-primary); }
  .ia-drop-link.is-current { color: var(--accent-primary); font-weight: 600; background: var(--accent-subtle); }

  .ia-drop-label {
    margin: 7px 9px 3px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--text-muted);
  }
  .ia-drop-label:first-child { margin-top: 2px; }
  .ia-drop-sep { height: 1px; margin: 6px 6px; background: var(--border-subtle); }

  .ia-actions { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; margin-left: auto; }

  .ia-meta {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-muted);
    white-space: nowrap;
  }
  .ia-meta::before {
    content: "";
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
  }

  .ia-icon-btn,
  .ia-icon-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    border-radius: 10px;
    border: 1px solid var(--border-default);
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
    text-decoration: none;
    transition: background-color var(--ia-press), color var(--ia-press), transform var(--ia-press);
  }
  .ia-icon-btn:hover,
  .ia-icon-link:hover { background: var(--bg-subtle); color: var(--text-primary); }
  .ia-icon-btn:active,
  .ia-icon-link:active { transform: scale(0.94); }

  /* ----- 모바일 하단 탭 바 ----- */
  .ia-tabbar { display: none; }

  .ia-tab {
    flex: 1 1 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    padding: 8px 2px 6px;
    border: 0;
    background: transparent;
    font-family: inherit;
    color: var(--text-muted);
    text-decoration: none;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
    transition: color var(--ia-press), transform var(--ia-press);
  }
  .ia-tab:active { transform: scale(0.96); }
  .ia-tab-icon { display: inline-flex; width: 22px; height: 22px; }
  .ia-tab-icon svg { width: 22px; height: 22px; }
  .ia-tab-label { font-size: 10.5px; font-weight: 600; letter-spacing: -0.02em; }
  .ia-tab.is-active { color: var(--accent-primary); }
  .ia-tab.is-active .ia-tab-label { font-weight: 700; }

  /* ----- 전체 메뉴 바텀 시트 ----- */
  .ia-sheet-backdrop,
  .ia-sheet { display: none; }

  .ia-sheet-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.44);
    opacity: 0;
    transition: opacity 200ms var(--ia-ease);
    z-index: 88;
  }
  .ia-sheet-backdrop.is-open { opacity: 1; }

  .ia-sheet {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 90;
    background: var(--bg-surface);
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    box-shadow: 0 -18px 40px -22px rgba(15, 23, 42, 0.4);
    max-height: 84vh;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    padding: 8px 18px calc(26px + env(safe-area-inset-bottom));
    transform: translateY(100%);
    transition: transform 240ms var(--ia-ease);
  }
  .ia-sheet.is-open { transform: translateY(0); }

  .ia-sheet-head {
    position: sticky;
    top: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 10px 0 8px;
    background: var(--bg-surface);
  }
  .ia-sheet-title { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); }
  .ia-sheet-close {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    border: 1px solid var(--border-default);
    background: var(--bg-page);
    color: var(--text-secondary);
    cursor: pointer;
    transition: background-color var(--ia-press), transform var(--ia-press);
  }
  .ia-sheet-close svg { width: 18px; height: 18px; }
  .ia-sheet-close:active { transform: scale(0.94); }

  .ia-sheet-body { padding-bottom: 6px; }
  .ia-sheet-group {
    margin: 14px 0 7px;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--text-muted);
  }
  .ia-sheet-links {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 7px;
  }
  .ia-sheet-link {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 11px 12px;
    border: 1px solid var(--border-default);
    border-radius: 12px;
    background: var(--bg-page);
    color: var(--text-primary);
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: -0.02em;
    text-decoration: none;
    min-width: 0;
    transition: transform var(--ia-press), border-color var(--ia-press), background-color var(--ia-press);
  }
  .ia-sheet-link:active { transform: scale(0.98); }
  .ia-sheet-link.is-current { border-color: var(--accent-primary); background: var(--accent-subtle); }
  .ia-sheet-file { font-size: 10.5px; font-weight: 500; color: var(--text-muted); }
  .ia-sheet-sub {
    margin: 9px 0 5px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--text-muted);
  }

  body.ia-sheet-open { overflow: hidden; }

  /* ----- 프레스 피드백(공통) ----- */
  .job-card,
  .arc-card,
  .opt,
  .stage,
  .chip,
  .btn,
  .filter-pill,
  .segment-btn,
  .pad-btn {
    transition: transform var(--ia-press), box-shadow var(--ia-press), border-color var(--ia-press),
      background-color var(--ia-press), color var(--ia-press);
  }
  .job-card:active,
  .arc-card:active,
  .opt:active,
  .stage:active,
  .chip:active,
  .btn:active,
  .filter-pill:active,
  .segment-btn:active,
  .pad-btn:active { transform: scale(0.98); }

  /* 태블릿 폭(769~1100px)에서는 안내 문구·GitHub 버튼을 접어 메뉴가 겹치지 않게 한다. */
  @media (max-width: 1100px) {
    .ia-header-inner { gap: 10px; padding: 0 16px; }
    .ia-meta { display: none; }
    .ia-menu-link,
    .ia-menu-btn { padding: 7px 9px; font-size: 13px; }
  }

  @media (max-width: 900px) {
    .ia-icon-link { display: none; }
    .ia-brand-name { font-size: 16px; }
    .ia-menu-link,
    .ia-menu-btn { padding: 7px 7px; font-size: 12.5px; }
    .ia-chevron { width: 12px; height: 12px; }
  }

  @media (max-width: 768px) {
    .ia-header-inner { height: 54px; padding: 0 14px; gap: 8px; }
    .ia-brand-img { width: 25px; height: 25px; border-radius: 7px; }
    .ia-brand-name { display: none; }
    .ia-current {
      display: block;
      min-width: 0;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ia-menu { display: none; }
    .ia-actions { margin-left: auto; gap: 8px; }
    .ia-meta,
    .ia-icon-link { display: none; }
    .ia-icon-btn { width: 34px; height: 34px; }

    .ia-tabbar {
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      align-items: stretch;
      height: calc(var(--ia-tabbar-h) + env(safe-area-inset-bottom));
      padding: 0 4px env(safe-area-inset-bottom);
      background: var(--bg-surface);
      border-top: 1px solid var(--border-default);
      box-shadow: 0 -1px 0 rgba(15, 23, 42, 0.02);
      z-index: 80;
    }

    .ia-sheet-backdrop,
    .ia-sheet { display: block; }
    .ia-sheet-backdrop[hidden],
    .ia-sheet[hidden] { display: none; }

    body { padding-bottom: calc(var(--ia-tabbar-h) + 16px + env(safe-area-inset-bottom)); }
  }

  @media (max-width: 380px) {
    .ia-header-inner { padding: 0 10px; }
    .ia-current { font-size: 14px; }
    .ia-sheet { padding-left: 14px; padding-right: 14px; }
    .ia-sheet-links { gap: 6px; }
    .ia-sheet-link { padding: 10px; font-size: 12.5px; }
  }

  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      transition-delay: 0ms !important;
      scroll-behavior: auto !important;
    }
    .ia-brand:active,
    .ia-menu-link:active,
    .ia-menu-btn:active,
    .ia-icon-btn:active,
    .ia-icon-link:active,
    .ia-tab:active,
    .ia-sheet-close:active,
    .ia-sheet-link:active,
    .job-card:active,
    .arc-card:active,
    .opt:active,
    .stage:active,
    .chip:active,
    .btn:active,
    .filter-pill:active,
    .segment-btn:active,
    .pad-btn:active { transform: none !important; }
    .ia-drop,
    .ia-sheet { transform: none !important; }
    .ia-chevron { transition: none !important; }
  }
"""

NAV_JS = """
(function () {
  'use strict';

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 데스크톱 드롭다운 ---------- */
  var groups = Array.prototype.slice.call(document.querySelectorAll('.ia-menu-group'));

  function closeGroup(group) {
    if (!group) return;
    group.classList.remove('is-open');
    var btn = group.querySelector('.ia-menu-btn');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }

  function closeAllGroups(except) {
    groups.forEach(function (group) {
      if (group !== except) closeGroup(group);
    });
  }

  groups.forEach(function (group) {
    var btn = group.querySelector('.ia-menu-btn');
    if (!btn) return;

    btn.addEventListener('click', function (event) {
      event.stopPropagation();
      // 마우스 호버로 이미 열린 메뉴를 같은 클릭으로 닫아 버리지 않는다.
      if (group.getAttribute('data-hover-open') === '1' && event.detail > 0) {
        group.removeAttribute('data-hover-open');
        return;
      }
      var willOpen = !group.classList.contains('is-open');
      closeAllGroups(group);
      group.classList.toggle('is-open', willOpen);
      btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      if (willOpen) {
        var first = group.querySelector('.ia-drop-link');
        if (first && document.activeElement === btn) first.focus();
      }
    });

    group.addEventListener('mouseenter', function () {
      if (window.innerWidth > 768 && window.matchMedia('(hover: hover)').matches) {
        closeAllGroups(group);
        group.classList.add('is-open');
        group.setAttribute('data-hover-open', '1');
        btn.setAttribute('aria-expanded', 'true');
      }
    });

    group.addEventListener('mouseleave', function () {
      if (window.innerWidth > 768) {
        closeGroup(group);
        group.removeAttribute('data-hover-open');
      }
    });

    group.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && group.classList.contains('is-open')) {
        closeGroup(group);
        btn.focus();
      }
    });
  });

  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target || !target.closest || !target.closest('.ia-menu-group')) closeAllGroups(null);
  });

  /* ---------- 모바일 전체 메뉴 시트 ---------- */
  var sheet = document.getElementById('iaSheet');
  var backdrop = document.getElementById('iaSheetBackdrop');
  var allBtn = document.getElementById('iaAllBtn');
  var gameBtn = document.getElementById('iaGameBtn');
  var sheetClose = document.getElementById('iaSheetClose');
  var lastOpener = null;
  var hideTimer = null;
  var openRaf = null;   // is-open 을 붙이려고 예약한 프레임(열기→같은 프레임 닫기 경합 차단)
  var isOpen = false;   // 실제 열림 상태 플래그(예약된 콜백이 이 값을 다시 확인한다)

  function sheetItems() {
    if (!sheet) return [];
    return Array.prototype.slice.call(sheet.querySelectorAll('a[href], button:not([disabled])'));
  }

  function cancelOpenFrame() {
    if (openRaf !== null) {
      window.cancelAnimationFrame(openRaf);
      openRaf = null;
    }
  }

  // 시트 안 특정 그룹(예: 게임 목록)을 시트 상단으로 스크롤하고 그 제목에 포커스를 준다.
  function focusSheetTarget(targetId) {
    var target = document.getElementById(targetId);
    if (!target) return;
    var sheetBox = sheet.getBoundingClientRect();
    var box = target.getBoundingClientRect();
    sheet.scrollTop = Math.max(0, sheet.scrollTop + (box.top - sheetBox.top) - 10);
    if (target.focus) {
      try { target.focus({ preventScroll: true }); } catch (err) { target.focus(); }
    }
  }

  function openSheet(opener, targetId) {
    if (!sheet || !backdrop || !allBtn) return;
    if (hideTimer) { window.clearTimeout(hideTimer); hideTimer = null; }
    lastOpener = opener || allBtn;
    isOpen = true;
    sheet.hidden = false;
    backdrop.hidden = false;
    document.body.classList.add('ia-sheet-open');
    allBtn.setAttribute('aria-expanded', 'true');
    if (gameBtn) gameBtn.setAttribute('aria-expanded', 'true');
    cancelOpenFrame();
    if (reduceMotion) {
      sheet.classList.add('is-open');
      backdrop.classList.add('is-open');
    } else {
      openRaf = window.requestAnimationFrame(function () {
        openRaf = window.requestAnimationFrame(function () {
          openRaf = null;
          // 예약된 프레임 사이에 닫혔다면(isOpen=false) 다시 열지 않는다.
          if (!isOpen) return;
          sheet.classList.add('is-open');
          backdrop.classList.add('is-open');
        });
      });
    }
    if (targetId) {
      focusSheetTarget(targetId);
    } else if (sheetClose) {
      sheetClose.focus();
    }
  }

  function closeSheet() {
    if (!sheet || !backdrop || !allBtn || sheet.hidden) return;
    isOpen = false;
    cancelOpenFrame();
    sheet.classList.remove('is-open');
    backdrop.classList.remove('is-open');
    document.body.classList.remove('ia-sheet-open');
    allBtn.setAttribute('aria-expanded', 'false');
    if (gameBtn) gameBtn.setAttribute('aria-expanded', 'false');
    hideTimer = window.setTimeout(function () {
      sheet.hidden = true;
      backdrop.hidden = true;
      hideTimer = null;
    }, reduceMotion ? 0 : 240);
    if (lastOpener && lastOpener.focus) lastOpener.focus();
    else allBtn.focus();
  }

  if (allBtn) {
    allBtn.addEventListener('click', function () {
      if (sheet && !sheet.hidden) closeSheet();
      else openSheet(allBtn);
    });
  }

  if (gameBtn) {
    gameBtn.addEventListener('click', function () {
      if (sheet && !sheet.hidden) {
        focusSheetTarget(gameBtn.getAttribute('data-sheet-target'));
        return;
      }
      openSheet(gameBtn, gameBtn.getAttribute('data-sheet-target'));
    });
  }
  if (sheetClose) sheetClose.addEventListener('click', closeSheet);
  if (backdrop) backdrop.addEventListener('click', closeSheet);

  document.addEventListener('keydown', function (event) {
    if (!sheet || sheet.hidden) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      closeSheet();
      return;
    }
    if (event.key === 'Tab') {
      var items = sheetItems();
      if (!items.length) return;
      var first = items[0];
      var last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 768) {
      closeAllGroups(null);
      if (sheet && !sheet.hidden) closeSheet();
    }
  });
})();
"""


def apply(html, current):
    """완성된 페이지 HTML 에 공통 셸을 씌운다(헤더 교체 + CSS/JS/시트 주입)."""
    meta_match = re.search(
        r'<div class="update-meta">\s*<span class="live-dot"></span>\s*<span>(.*?)</span>',
        html,
        re.S,
    )
    meta_text = (meta_match.group(1).strip() if meta_match else "")
    if "{" in meta_text or "__" in meta_text:
        meta_text = ""
    if not meta_text:
        meta_text = PAGE_LABEL.get(current, "")

    header = render_header(current, meta_text)
    html, count = re.subn(
        r'<header\s+class="navbar">.*?</header>', header, html, count=1, flags=re.S
    )
    if count != 1:
        raise ValueError("공통 헤더를 찾지 못했습니다: " + str(current))

    style_tag = '<style id="ia-shell-style">' + NAV_CSS + "</style>"
    if "</head>" in html:
        html = html.replace("</head>", style_tag + "\n</head>", 1)
    else:
        raise ValueError("</head> 를 찾지 못했습니다: " + str(current))

    # 후원 링크: 설정에 허용된 URL 이 있을 때만, 운영자가 직접 쓴 페이지의 공통 푸터에 붙인다.
    # (민간 채용공고·KAMIS 가격 등 제3자 데이터 페이지는 SUPPORT_FOOTER_PAGES 에서 제외)
    support = (monetization.support_footer_html()
               if monetization.support_enabled_for(current) else "")
    if support:
        html = html.replace(
            "</head>",
            '<style id="ia-monetization-style">' + monetization.SUPPORT_CSS + "</style>\n</head>",
            1,
        )

    tail = (
        support
        + _mobile_tabs(current)
        + _sheet(current)
        + '<script id="ia-shell-script">'
        + NAV_JS
        + "</script>\n</body>"
    )
    if "</body>" in html:
        html = html.replace("</body>", tail, 1)
    else:
        raise ValueError("</body> 를 찾지 못했습니다: " + str(current))

    html = re.sub(r"<body(\s[^>]*)?>", lambda m: "<body" + (m.group(1) or "") + ' data-page="%s">' % current, html, count=1)
    return html

# -*- coding: utf-8 -*-
"""제휴·후원 링크(정적) — 설정 파일 읽기 · URL 검증 · HTML 조각.

이 사이트는 GitHub Pages 정적 호스팅이고 `html_guard.py` 의 CSP 를 그대로 쓴다.
그래서 수익화도 서버·추적 스크립트 없이 '링크'만 둔다.

- 설정: `monetization_config.json` (빌드 시 읽는 공개 메타데이터, 비밀값 없음)
  · `studyAffiliate` — 시험 공부 허브 학습 자료 하단의 제휴 카드 1곳
  · `supportLink`    — 운영자가 직접 쓴 페이지의 공통 푸터 후원 링크 1곳
  · `url` 이 빈 문자열이면 화면에 아무것도 그리지 않는다(초기 배포 상태 = 완전 숨김).
- 배치 제한: `index.html`(민간 채용공고)·`grocery.html`(KAMIS 가격)·`ai`/`cve` 등
  제3자 데이터를 그대로 보여 주는 페이지에는 제휴·후원 요소를 넣지 않는다.
- 보안: 허용 호스트의 HTTPS URL 만 통과시키고(그 외는 조용히 무시),
  활성 링크에는 `rel="sponsored noopener noreferrer"` 와 `target="_blank"` 를 붙인다.
- 표시: 제휴 카드에는 공정위 고지(수수료 수령 가능)를 함께 렌더링한다.
  고지문은 `DEFAULT_DISCLOSURE` 로 고정이며, 설정의 `disclosure` 문자열로 덮어쓸 수 없다
  (수수료 관계를 숨기는 문구가 나가지 않도록). 일반 설명은 `description` 만 쓴다.
"""
import html
import json
import os
import re
from urllib.parse import urlsplit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "monetization_config.json")
CONFIG_ENV = "MONETIZATION_CONFIG"

DEFAULT_DISCLOSURE = "이 링크를 통해 구매하면 운영자가 수수료를 받을 수 있습니다"

# 제휴·후원 링크로 허용하는 호스트(정확히 일치 또는 그 하위 도메인만).
ALLOWED_HOSTS = (
    "link.coupang.com",
    "coupa.ng",
    "www.yes24.com",
    "www.kyobobook.co.kr",
    "www.aladin.co.kr",
    "buymeacoffee.com",
    "qr.kakaopay.com",
    "toss.me",
    "github.com",
)

# 후원 링크를 공통 푸터에 노출하는 페이지 — 운영자가 직접 쓴 학습·도구 페이지만.
# 제3자 데이터 페이지(index·grocery·ai·cve·outfit·pick·food·seat·load·chart·radar·today)는 제외한다.
SUPPORT_FOOTER_PAGES = frozenset({"study", "tools"})

_TEXT_LIMIT = 120          # 제목·설명·버튼 라벨 길이 상한(레이아웃 보호)
_URL_LIMIT = 500
_BAD_URL_CHARS = re.compile(r"[\s<>\"'`\\]")
_TAG_RE = re.compile(r"<[^>]*>")

AFFILIATE_CSS = """
  /* ===== 제휴 카드 (monetization.py) — 학습 자료 하단 1곳 ===== */
  .ia-aff { margin: 26px 0 4px; padding: 14px 16px; background: var(--bg-surface, #fff);
    border: 1px solid var(--border-default, #e2e8f0); border-radius: 14px; }
  .ia-aff-disclosure { font-size: 10.5px; line-height: 1.5; color: var(--text-muted, #94a3b8); }
  .ia-aff-row { display: flex; align-items: center; justify-content: space-between; gap: 12px;
    margin-top: 9px; }
  .ia-aff-text { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
  .ia-aff-title { font-size: 13px; font-weight: 700; letter-spacing: -0.02em;
    color: var(--text-primary, #0f172a); }
  .ia-aff-desc { font-size: 11.5px; line-height: 1.5; color: var(--text-secondary, #475569);
    word-break: keep-all; }
  .ia-aff-btn { flex: 0 0 auto; display: inline-flex; align-items: center; height: 32px; padding: 0 14px;
    border-radius: 9px; background: var(--text-primary, #0f172a); color: var(--bg-surface, #fff);
    font-size: 12px; font-weight: 700; text-decoration: none; transition: opacity .16s ease; }
  .ia-aff-btn:hover { opacity: .86; }
  .ia-aff-btn:focus-visible { outline: 2px solid var(--accent-primary, #2563eb); outline-offset: 2px; }
  .ia-support { display: flex; flex-wrap: wrap; align-items: center; justify-content: center;
    gap: 7px; margin: 22px 0 4px; font-size: 11.5px; color: var(--text-muted, #94a3b8); }
  .ia-support a { color: var(--text-secondary, #475569); font-weight: 600; text-decoration: none;
    border-bottom: 1px solid var(--border-strong, #cbd5e1); padding-bottom: 1px; }
  .ia-support a:hover { color: var(--text-primary, #0f172a); }
  .ia-support a:focus-visible { outline: 2px solid var(--accent-primary, #2563eb); outline-offset: 2px; }
  @media (max-width: 480px) {
    .ia-aff { padding: 13px 13px; }
    .ia-aff-row { flex-direction: column; align-items: stretch; gap: 10px; }
    .ia-aff-btn { justify-content: center; height: 36px; }
  }
"""

SUPPORT_CSS = AFFILIATE_CSS


# ---------------------------------------------------------------------------
# 검증 · 설정
# ---------------------------------------------------------------------------
def validate_url(url):
    """허용 호스트의 HTTPS URL 만 통과시킨다. 그 외(http·javascript·미허용 호스트·자격증명)는 ''. """
    if not isinstance(url, str):
        return ""
    raw = url.strip()
    if not raw or len(raw) > _URL_LIMIT or _BAD_URL_CHARS.search(raw):
        return ""
    try:
        parts = urlsplit(raw)
        port = parts.port
    except ValueError:
        return ""
    if parts.scheme.lower() != "https":
        return ""
    if parts.username or parts.password:
        return ""
    if port not in (None, 443):
        return ""
    host = (parts.hostname or "").lower()
    if not host:
        return ""
    if not any(host == base or host.endswith("." + base) for base in ALLOWED_HOSTS):
        return ""
    return parts.geturl()


def _text(value, fallback="", limit=_TEXT_LIMIT):
    """링크에 실을 문구를 한 줄 텍스트로 정리한다(태그·제어문자 제거)."""
    if not isinstance(value, str):
        return fallback
    cleaned = _TAG_RE.sub("", value)
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return fallback
    return cleaned[:limit]


def _entry(raw, defaults):
    raw = raw if isinstance(raw, dict) else {}
    entry = dict(defaults)
    for key in defaults:
        if key == "url":
            entry["url"] = validate_url(raw.get("url"))
        else:
            entry[key] = _text(raw.get(key), defaults[key])
    return entry


def normalize_config(raw):
    """설정 dict 를 화면에 쓸 형태로 정리한다(모르는 키는 버리고 URL 은 검증한다)."""
    raw = raw if isinstance(raw, dict) else {}
    affiliate = _entry(raw.get("studyAffiliate"), {
        "title": "수험서 구매",
        "description": "",
        "buttonLabel": "수험서 보기",
        "url": "",
        "disclosure": DEFAULT_DISCLOSURE,
    })
    # 공정위 고지문은 설정으로 바꿀 수 없다 — 어떤 문자열이 들어와도 고정값을 쓴다.
    affiliate["disclosure"] = DEFAULT_DISCLOSURE
    return {
        "version": raw.get("version") if isinstance(raw.get("version"), int) else 1,
        "studyAffiliate": affiliate,
        "supportLink": _entry(raw.get("supportLink"), {
            "title": "이 사이트 돕기",
            "description": "",
            "buttonLabel": "후원하기",
            "url": "",
            "kind": "후원",
            "disclosure": "",
        }),
    }


def load_config(path=None):
    """설정 파일을 읽는다. 파일이 없거나 깨졌으면 '꺼진' 기본값을 쓴다."""
    path = path or os.environ.get(CONFIG_ENV) or CONFIG_PATH
    try:
        with open(path, encoding="utf-8") as handle:
            raw = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        raw = {}
    return normalize_config(raw)


# ---------------------------------------------------------------------------
# HTML 조각
# ---------------------------------------------------------------------------
def _link(url, label, kind):
    return ('<a class="ia-aff-btn" data-monetization-link="%s" href="%s" target="_blank" '
            'rel="sponsored noopener noreferrer">%s</a>'
            % (kind, html.escape(url, quote=True), html.escape(label)))


def affiliate_html(config=None):
    """시험 공부 허브 하단의 제휴 카드. url 이 없으면 빈 문자열(아무것도 그리지 않음)."""
    entry = (config or load_config())["studyAffiliate"]
    url = validate_url(entry.get("url"))
    if not url:
        return ""
    # 설정의 disclosure 로 덮어쓰지 않는다: 수수료 고지문은 항상 DEFAULT_DISCLOSURE.
    disclosure = DEFAULT_DISCLOSURE
    description = entry.get("description") or ""
    desc_html = ('<span class="ia-aff-desc">%s</span>' % html.escape(description)) if description else ""
    return (
        '<section class="ia-aff" data-monetization="affiliate" aria-label="%s">'
        '<p class="ia-aff-disclosure" data-monetization-disclosure>%s</p>'
        '<div class="ia-aff-row">'
        '<div class="ia-aff-text"><span class="ia-aff-title">%s</span>%s</div>'
        '%s'
        '</div></section>'
        % (html.escape(entry.get("title")), html.escape(disclosure),
           html.escape(entry.get("title")), desc_html,
           _link(url, entry.get("buttonLabel"), "affiliate"))
    )


def support_footer_html(config=None):
    """공통 푸터의 후원 링크. url 이 없으면 빈 문자열."""
    entry = (config or load_config())["supportLink"]
    url = validate_url(entry.get("url"))
    if not url:
        return ""
    kind = entry.get("kind") or "후원"
    return (
        '<footer class="ia-support" data-monetization="support">'
        '<span>%s</span>'
        '<a data-monetization-link="support" href="%s" target="_blank" '
        'rel="sponsored noopener noreferrer">%s</a>'
        '</footer>'
        % (html.escape(kind), html.escape(url, quote=True), html.escape(entry.get("buttonLabel")))
    )


def support_enabled_for(page):
    """이 페이지의 공통 푸터에 후원 링크를 붙일 수 있는지(배치 제한)."""
    return page in SUPPORT_FOOTER_PAGES

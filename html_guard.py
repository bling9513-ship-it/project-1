# -*- coding: utf-8 -*-
"""
정적 페이지 공통 보안 하드닝 유틸.

- CSP 메타 태그 주입 (meta 태그만으로도 object-src/base-uri/form-action 을 잠글 수 있다)
  · script-src 는 'self' + 페이지 내 인라인 <script> 본문의 SHA-256 해시만 허용한다.
    ('unsafe-inline' 미사용 → 인라인 이벤트 핸들러(onclick 등)와 javascript: URL 이 원천 차단됨)
- target="_blank" 앵커에 rel="noopener noreferrer" 강제
- 외부에서 수집한 URL 을 href 에 넣기 전 http/https/mailto 스킴 화이트리스트 검증
- <script> 안에 JSON 을 심을 때 "</" 가 스크립트를 조기 종료시키지 않도록 이스케이프
- 외부 CDN 리소스(<link rel="stylesheet">)에 SRI(integrity=sha384-…) + crossorigin="anonymous" 강제
"""
import base64
import hashlib
import re

# ---------------------------------------------------------------------------
# 외부 CDN 서브리소스 무결성(SRI)
#   jsDelivr 는 버전 태그가 고정된 경로(@v1.3.9)에 `cache-control: immutable` 로 응답하므로
#   바이트가 바뀌지 않는다. 실제 응답 본문으로 계산한 sha384 값을 고정해 두고,
#   빌드 산출물의 링크 태그를 이 값으로 정규화한다(해시 드리프트를 빌드 단계에서 차단).
#   ※ 버전을 올릴 때는 아래 URL·해시를 함께 갱신할 것.
# ---------------------------------------------------------------------------
PRETENDARD_CSS_URL = (
    "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css"
)
PRETENDARD_CSS_SRI = "sha384-SN6A48CJQjx946+DRb8wsoifC4a8ur9ZS6R+HCTgnBHOKCa6GLXAR3Qn8d1jztxg"

# 외부 스타일시트 URL → SRI 해시. 여기에 없는 외부 URL 은 integrity 없이 두고 건드리지 않는다.
SRI_STYLESHEETS = {
    PRETENDARD_CSS_URL: PRETENDARD_CSS_SRI,
}

# 인라인 스크립트가 하나도 없을 때의 기본값(해시 없이 'self' 만 허용).
CSP_VALUE = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "font-src 'self' data: https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "connect-src 'self' https://api.open-meteo.com; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)

_CHARSET_RE = re.compile(r'<meta\s+charset=["\']?[^"\'>\s]+["\']?\s*/?>', re.I)
_ANCHOR_BLANK_RE = re.compile(r'<a\b[^>]*?target\s*=\s*("_blank"|\'_blank\')[^>]*>', re.I)
_REL_RE = re.compile(r'rel\s*=\s*("([^"]*)"|\'([^\']*)\')', re.I)
_SAFE_SCHEME_RE = re.compile(r'^(?:https?:|mailto:)', re.I)
_BAD_CHARS_RE = re.compile(r'[\s<>"\'`\\]')

# <script ...> ... </script> 스캔. 브라우저와 동일하게 "먼저 열린 태그의 본문은
# 첫 </script> 에서 끝난다"는 규칙으로 순차 소비하므로, 스크립트 본문 문자열 안에
# 들어 있는 "<script" 예제 텍스트(예: XSS 학습 데이터)를 실제 태그로 오인하지 않는다.
_SCRIPT_OPEN_RE = re.compile(r'<script\b([^>]*)>', re.I)
_SCRIPT_CLOSE_RE = re.compile(r'</script\s*>', re.I)
_ATTR_RE = re.compile(r'([^\s=/>]+)\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)')
_CSP_META_RE = re.compile(
    r'<meta\b[^>]*http-equiv\s*=\s*["\']?Content-Security-Policy["\']?[^>]*>', re.I
)
_CSP_CONTENT_RE = re.compile(r'content\s*=\s*("[^"]*"|\'[^\']*\')', re.I)
_LINK_TAG_RE = re.compile(r'<link\b[^>]*>', re.I)


# 브라우저가 실행하는 스크립트 타입만 해시를 계산한다.
# application/json, text/template, importmap 등은 실행되지 않으므로 CSP 검사 대상이 아니다.
_EXECUTABLE_TYPES = {
    "",
    "text/javascript",
    "application/javascript",
    "application/x-javascript",
    "text/ecmascript",
    "application/ecmascript",
    "text/jscript",
    "module",
}


def safe_url(url, fallback="#"):
    """외부 수집 URL 을 href 로 쓰기 전 스킴 화이트리스트 검증."""
    if url is None:
        return fallback
    u = str(url).strip()
    if not u or _BAD_CHARS_RE.search(u):
        return fallback
    if not _SAFE_SCHEME_RE.match(u):
        return fallback
    return u


def safe_json_for_script(obj_json_str):
    """json.dumps 결과에서 스크립트 조기 종료 시퀀스를 중화한다."""
    return str(obj_json_str).replace("</", "<\\/")


def _fix_rel(match):
    tag = match.group(0)
    rel_m = _REL_RE.search(tag)
    if rel_m:
        raw = rel_m.group(2) if rel_m.group(2) is not None else rel_m.group(3)
        tokens = [t for t in raw.split() if t]
        lower = {t.lower() for t in tokens}
        for need in ("noopener", "noreferrer"):
            if need not in lower:
                tokens.append(need)
        new = 'rel="%s"' % " ".join(tokens)
        return tag[:rel_m.start()] + new + tag[rel_m.end():]
    return tag[:-1].rstrip() + ' rel="noopener noreferrer">'


def _parse_attrs(attr_text):
    attrs = {}
    for m in _ATTR_RE.finditer(attr_text or ""):
        name = m.group(1).lower()
        raw = m.group(2)
        if raw[:1] in ("'", '"'):
            raw = raw[1:-1]
        attrs[name] = raw
    return attrs


def iter_scripts(html):
    """(attrs dict, 본문 텍스트) 를 문서 등장 순서대로 돌려준다."""
    pos = 0
    while True:
        m = _SCRIPT_OPEN_RE.search(html, pos)
        if not m:
            return
        close = _SCRIPT_CLOSE_RE.search(html, m.end())
        if not close:
            return
        yield _parse_attrs(m.group(1)), html[m.end():close.start()]
        pos = close.end()


def inline_script_hashes(html):
    """실행되는 인라인 <script> 본문의 CSP source expression('sha256-...') 목록."""
    hashes = []
    seen = set()
    for attrs, body in iter_scripts(html):
        if "src" in attrs:
            continue  # 외부 스크립트는 'self' 로 허용되고, 인라인 본문은 무시된다
        if attrs.get("type", "").strip().lower() not in _EXECUTABLE_TYPES:
            continue  # JSON/템플릿 등 데이터 블록은 실행되지 않는다
        if not body:
            continue
        digest = hashlib.sha256(body.encode("utf-8")).digest()
        expr = "'sha256-%s'" % base64.b64encode(digest).decode("ascii")
        if expr not in seen:
            seen.add(expr)
            hashes.append(expr)
    return hashes


def build_csp(hashes):
    """인라인 스크립트 해시를 script-src 에 등록한 CSP 문자열."""
    script_src = "'self'" + ("".join(" " + h for h in hashes) if hashes else "")
    return CSP_VALUE.replace("script-src 'self'", "script-src " + script_src, 1)


def _strip_attr(tag, name):
    """태그 문자열에서 name 속성(값 유무 무관)을 제거한다."""
    return re.sub(
        r'\s+%s(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+))?' % re.escape(name),
        "", tag, flags=re.I,
    )


def _add_attr(tag, name, value):
    """태그 문자열에 name="value" 속성을 덧붙인다(닫는 괄호 앞)."""
    trimmed = tag.rstrip()
    closed = trimmed.endswith("/>")
    head = trimmed[:-2].rstrip() if closed else trimmed[:-1].rstrip()
    closing = " />" if closed else ">"
    return '%s %s="%s"%s' % (head, name, value, closing)


def _fix_external_link_sri(match):
    """<link rel="stylesheet"> 가 등록된 외부 CDN URL 이면 integrity/crossorigin 을 정규화한다."""
    tag = match.group(0)
    attrs = _parse_attrs(tag[len("<link"):])
    rel = (attrs.get("rel") or "").lower().split()
    href = (attrs.get("href") or "").strip()
    if "stylesheet" not in rel:
        return tag
    sri = SRI_STYLESHEETS.get(href)
    if not sri:
        return tag
    # crossorigin 이 없거나 값이 다르면 SRI 검증이 통과하지 못하므로 항상 익명 CORS 로 고정한다.
    fixed = _strip_attr(_strip_attr(tag, "integrity"), "crossorigin")
    fixed = _add_attr(fixed, "integrity", sri)
    fixed = _add_attr(fixed, "crossorigin", "anonymous")
    return fixed


def harden_html(html):
    """생성된 HTML 문자열에 CSP·rel·SRI 보강을 적용해 돌려준다."""
    if not html:
        return html
    html = _LINK_TAG_RE.sub(_fix_external_link_sri, html)
    html = _ANCHOR_BLANK_RE.sub(_fix_rel, html)

    # 해시는 최종 HTML 의 스크립트 본문 바이트로 계산해야 한다(다른 변형을 모두 마친 뒤).
    csp = build_csp(inline_script_hashes(html))
    meta = '<meta http-equiv="Content-Security-Policy" content="%s">' % csp

    existing = _CSP_META_RE.search(html)
    if existing:
        # 이미 CSP 가 있으면 script-src 를 포함해 새 정책으로 교체한다(중복 메타 방지 · 멱등).
        html = html[:existing.start()] + meta + html[existing.end():]
        return html

    m = _CHARSET_RE.search(html)
    if m:
        html = html[:m.end()] + "\n  " + meta + html[m.end():]
    elif "<head>" in html:
        html = html.replace("<head>", "<head>\n  " + meta, 1)
    return html

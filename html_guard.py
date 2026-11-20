# -*- coding: utf-8 -*-
"""
정적 페이지 공통 보안 하드닝 유틸.

- CSP 메타 태그 주입 (meta 태그만으로도 object-src/base-uri/form-action 을 잠글 수 있다)
- target="_blank" 앵커에 rel="noopener noreferrer" 강제
- 외부에서 수집한 URL 을 href 에 넣기 전 http/https/mailto 스킴 화이트리스트 검증
- <script> 안에 JSON 을 심을 때 "</" 가 스크립트를 조기 종료시키지 않도록 이스케이프
"""
import re

# 인라인 스크립트/스타일과 Pretendard CDN, Open-Meteo 런타임 조회만 허용한다.
CSP_VALUE = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "font-src 'self' data: https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "connect-src 'self' https://api.open-meteo.com; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)
CSP_META = '<meta http-equiv="Content-Security-Policy" content="%s">' % CSP_VALUE

_CHARSET_RE = re.compile(r'<meta\s+charset=["\']?[^"\'>\s]+["\']?\s*/?>', re.I)
_ANCHOR_BLANK_RE = re.compile(r'<a\b[^>]*?target\s*=\s*("_blank"|\'_blank\')[^>]*>', re.I)
_REL_RE = re.compile(r'rel\s*=\s*("([^"]*)"|\'([^\']*)\')', re.I)
_SAFE_SCHEME_RE = re.compile(r'^(?:https?:|mailto:)', re.I)
_BAD_CHARS_RE = re.compile(r'[\s<>"\'`\\]')


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


def harden_html(html):
    """생성된 HTML 문자열에 CSP·rel 보강을 적용해 돌려준다."""
    if not html:
        return html
    html = _ANCHOR_BLANK_RE.sub(_fix_rel, html)
    if "Content-Security-Policy" not in html:
        m = _CHARSET_RE.search(html)
        if m:
            html = html[:m.end()] + "\n  " + CSP_META + html[m.end():]
        elif "<head>" in html:
            html = html.replace("<head>", "<head>\n  " + CSP_META, 1)
    return html

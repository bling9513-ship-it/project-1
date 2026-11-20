# -*- coding: utf-8 -*-
"""
크롤러 공통 네트워크 가드.

외부 RSS/JSON/HTML 을 받을 때 응답 크기를 상한선까지만 읽어
비정상적으로 큰 응답(메모리 소진·빌드 지연)을 방어한다.
"""
import urllib.request

# JSON/RSS 응답은 보통 수백 KB~수 MB. 8MB 를 넘는 응답은 비정상으로 본다.
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
# HTML 목록 페이지 상한
MAX_HTML_BYTES = 12 * 1024 * 1024


def read_limited(resp, max_bytes=MAX_RESPONSE_BYTES):
    """Content-Length 가 상한을 넘으면 즉시 중단하고, 그 외에는 상한까지만 읽는다."""
    try:
        declared = resp.headers.get("Content-Length")
        if declared and declared.isdigit() and int(declared) > max_bytes:
            raise ValueError("response too large: %s bytes > %s" % (declared, max_bytes))
    except AttributeError:
        pass
    data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("response too large: over %s bytes" % max_bytes)
    return data


def open_http(url, headers=None, timeout=20):
    """http/https URL 만 허용하는 공통 오프너."""
    if not isinstance(url, str) or not url.lower().startswith(("http://", "https://")):
        raise ValueError("unsupported url scheme: %r" % (url,))
    req = urllib.request.Request(url, headers=headers or {})
    return urllib.request.urlopen(req, timeout=timeout)

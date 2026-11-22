#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""제휴·후원 인프라(monetization.py) 검증.

확인하는 것
  · 기본 설정(URL 빈 문자열)에서는 제휴·후원 DOM 이 전혀 만들어지지 않는다(완전 숨김).
  · URL 검증기: 허용 호스트의 HTTPS 만 통과, http·javascript:·미허용 호스트·자격증명·비표준 포트는 거절.
  · 유효한 설정을 넣으면 공정위 고지와 rel="sponsored noopener noreferrer"·target="_blank" 가 함께 나온다.
  · 설정 문구는 HTML 이스케이프되어 스크립트가 끼어들 수 없다(인라인 이벤트·그라데이션·이모지 없음).
  · 배치 제한: 제휴 카드는 study.html 학습 자료 하단 1곳, 후원은 공통 푸터(study·tools)에만.
    index·grocery 등 제3자 데이터 페이지에는 어떤 설정에서도 들어가지 않는다.
  · 미리보기 빌드(임시 설정)에서도 CSP 메타는 그대로 1개이고 unsafe-inline(script) 이 없다.

실행: python3 tests/test_monetization.py
"""
import os
import re
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import monetization  # noqa: E402
import make_preview_pages  # noqa: E402

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
failures = []


def check(name, cond, detail=""):
    if not cond:
        failures.append(name)
        print("  [실패] %s %s" % (name, detail))


SAMPLE = {
    "version": 1,
    "studyAffiliate": {
        "title": "수험서 구매",
        "description": "정보보안기사 수험서",
        "buttonLabel": "수험서 보기",
        "url": "https://www.yes24.com/Product/Goods/123456",
        "disclosure": "이 링크를 통해 구매하면 운영자가 수수료를 받을 수 있습니다",
    },
    "supportLink": {
        "title": "이 사이트 돕기",
        "description": "후원 안내",
        "buttonLabel": "후원하기",
        "url": "https://buymeacoffee.com/infosec-archive",
        "kind": "후원",
    },
}


def check_url_validator():
    print("== URL 검증 ==")
    good = [
        "https://link.coupang.com/a/abc123",
        "https://coupa.ng/bXyZ",
        "https://www.yes24.com/Product/Goods/123456",
        "https://www.kyobobook.co.kr/product/detailViewKor.laf?barcode=97911",
        "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=1",
        "https://buymeacoffee.com/infosec-archive",
        "https://qr.kakaopay.com/2819302",
        "https://toss.me/infosec",
        "https://github.com/sponsors/bling9513-ship-it",
    ]
    for url in good:
        check("허용 %s" % url, monetization.validate_url(url) == url, monetization.validate_url(url))
    bad = [
        "http://www.yes24.com/Product/Goods/1",          # http
        "javascript:alert(1)",                           # 스크립트 스킴
        "JavaScript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "https://evil.example.com/a",                    # 미허용 호스트
        "https://www.yes24.com.evil.example.com/a",       # 접미사 위장
        "https://user:pw@www.yes24.com/a",                # 자격증명
        "https://www.yes24.com:8443/a",                   # 비표준 포트
        "//www.yes24.com/a",                              # 프로토콜 상대
        "https://www.yes24.com/a b",                      # 공백
        "https://www.yes24.com/<script>",
        "",
        "   ",
        None,
    ]
    for url in bad:
        check("거절 %r" % (url,), monetization.validate_url(url) == "", monetization.validate_url(url))


def check_default_off():
    print("== 기본값(꺼짐) ==")
    config = monetization.load_config()
    check("기본 제휴 URL 빔", config["studyAffiliate"]["url"] == "", config["studyAffiliate"]["url"])
    check("기본 후원 URL 빔", config["supportLink"]["url"] == "", config["supportLink"]["url"])
    check("기본 제휴 DOM 없음", monetization.affiliate_html(config) == "",
          monetization.affiliate_html(config))
    check("기본 후원 DOM 없음", monetization.support_footer_html(config) == "",
          monetization.support_footer_html(config))
    check("설정 파일 없음 → 꺼짐", monetization.affiliate_html(
        monetization.load_config(os.path.join(tempfile.gettempdir(), "no-such-config.json"))) == "")
    for name in ("study", "tools", "index", "grocery", "ai", "cve"):
        path = os.path.join(BASE_DIR, name + ".html")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as handle:
            src = handle.read()
        check("%s.html 수익화 DOM 없음(기본)" % name, "data-monetization" not in src,
              src.count("data-monetization"))


def check_placement():
    print("== 배치 제한 ==")
    check("study 후원 허용", monetization.support_enabled_for("study"))
    check("tools 후원 허용", monetization.support_enabled_for("tools"))
    for page in ("index", "grocery", "ai", "cve", "outfit", "pick", "food", "today"):
        check("%s 후원 제외" % page, not monetization.support_enabled_for(page))


def check_rendered():
    print("== 유효 설정 렌더링 ==")
    config = monetization.normalize_config(SAMPLE)
    affiliate = monetization.affiliate_html(config)
    support = monetization.support_footer_html(config)
    check("제휴 카드 생성", bool(affiliate), affiliate[:60])
    check("후원 링크 생성", bool(support), support[:60])
    disclosure = config["studyAffiliate"]["disclosure"]
    check("고지 문구", disclosure in affiliate, disclosure)
    check("rel sponsored", 'rel="sponsored noopener noreferrer"' in affiliate, affiliate)
    check("target _blank", 'target="_blank"' in affiliate, affiliate)
    check("제휴 버튼 라벨", "수험서 보기" in affiliate, affiliate)
    check("후원 rel sponsored", 'rel="sponsored noopener noreferrer"' in support, support)
    check("후원 종류 표기", "후원" in support, support)
    check("이모지 없음", not EMOJI_RE.search(affiliate + support))
    check("그라데이션 없음", "gradient" not in (affiliate + support).lower())
    check("인라인 핸들러 없음", not re.search(r"<[^>]+[\s\"']on[a-z]+\s*=", affiliate + support, re.I))

    broken = monetization.normalize_config({
        "studyAffiliate": {"url": "http://www.yes24.com/Product/Goods/1"},
        "supportLink": {"url": "javascript:alert(1)"},
    })
    check("http 제휴 무시", monetization.affiliate_html(broken) == "")
    check("javascript 후원 무시", monetization.support_footer_html(broken) == "")

    evil = monetization.normalize_config({
        "studyAffiliate": dict(SAMPLE["studyAffiliate"], title="<script>alert(1)</script>",
                              description="<img src=x onerror=alert(1)>"),
    })
    html_out = monetization.affiliate_html(evil)
    check("설정 문구 이스케이프", "<script>" not in html_out and "onerror=" not in html_out, html_out[:120])


def check_preview_build():
    print("== 미리보기 빌드(임시 설정) ==")
    workdir = tempfile.mkdtemp(prefix="monetization-")
    out_html = os.path.join(workdir, "study-preview.html")
    out_config = os.path.join(workdir, "config.json")
    make_preview_pages.build_study_preview(out_html=out_html, out_config=out_config)
    with open(out_html, encoding="utf-8") as handle:
        src = handle.read()
    check("제휴 카드 1곳", src.count('data-monetization="affiliate"') == 1,
          src.count('data-monetization="affiliate"'))
    check("후원 링크 1곳", src.count('data-monetization="support"') == 1,
          src.count('data-monetization="support"'))
    check("제휴 고지 렌더링", SAMPLE["studyAffiliate"]["disclosure"] in src)
    check("제휴 rel", 'rel="sponsored noopener noreferrer"' in src)
    check("CSP 메타 1개", src.count("Content-Security-Policy") == 1, src.count("Content-Security-Policy"))
    check("unsafe-inline 미사용(script)", "script-src 'self' 'unsafe-inline'" not in src)
    check("제휴 카드가 푸터 위", src.find('data-monetization="affiliate"') < src.find("<footer>"),
          (src.find('data-monetization="affiliate"'), src.find("<footer>")))
    check("제휴 스타일 1개", src.count("ia-affiliate-style") == 1, src.count("ia-affiliate-style"))


def main():
    check_default_off()
    check_url_validator()
    check_placement()
    check_rendered()
    check_preview_build()
    print()
    if failures:
        print("실패 %d건" % len(failures))
        for name in failures:
            print("  - %s" % name)
        return 1
    print("제휴·후원 인프라 검증 통과 (기본 숨김 · URL 화이트리스트 · sponsored rel · 배치 제한)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""보안 취약점 점검 도구 백과사전(security-reference.html) 데이터·페이지 검증.

빌더와 독립된 규칙으로 다음을 확인한다.
  1) 데이터(security_reference_data.json)
     - 6개 분야 × 2개 항목 = 12개, ID 중복 없음, 필수 필드 누락 없음
     - 실행 영향 등급 3종(로컬 파일 읽기 / 네트워크 요청 / 별도 변경 승인 필요)만 사용
     - 공식 문서는 https 링크이고 형식이 유효함
     - 샘플 증적에 실제 사설·공인 IP, 실제 도메인, 시크릿 패턴이 없음(문서용 대역·이름만)
  2) 페이지(security-reference.html)
     - 항목 12개 · 레일 링크 12개 · 명령 복사 버튼 수 = 명령 수
     - 페이지에 심긴 목록(id·분야)이 JSON 과 일치
     - 이모지 0 · 'gradient' 0 · 인라인 on* 핸들러 0 · http:// 문서 링크 0
  3) tools.html 상호 연결
     - 데이터의 치트시트 앵커가 tools.html 에 실제로 있고, 그 카드가 같은 항목 ID로 되돌아옴

실행: python3 tests/test_security_reference.py
"""
import ipaddress
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "security_reference_data.json")
PAGE_PATH = os.path.join(BASE_DIR, "security-reference.html")
TOOLS_PATH = os.path.join(BASE_DIR, "tools.html")

IMPACTS = {"로컬 파일 읽기", "네트워크 요청", "별도 변경 승인 필요"}
REQUIRED = ("id", "category", "tool", "title", "summary", "purpose", "verified_version",
            "input_type", "privilege", "impact", "impact_note", "commands", "options",
            "reading", "sample", "docs")
READING_KEYS = ("normal", "abnormal", "false_positive", "action", "recheck")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
IPV4_RE = re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b")
DOMAIN_RE = re.compile(r"\b(?:[a-z0-9][a-z0-9-]*\.)+([a-z]{2,})\b", re.I)
DOC_NETS = [ipaddress.ip_network("192.0.2.0/24"), ipaddress.ip_network("198.51.100.0/24"),
            ipaddress.ip_network("203.0.113.0/24"), ipaddress.ip_network("127.0.0.0/8")]
# 샘플 증적에 실제 도메인이 섞이지 않았는지 보는 기준.
#   - 2글자 국가 코드(.kr·.jp·.io …)와 널리 쓰이는 공인 TLD 가 붙은 이름은 실제 도메인으로 본다.
#   - fixture.test(RFC 2606)와 예제 파일 확장자(.pcap·.crt …), 코드 식별자(tls.handshake.type)는 통과.
# 소스 파일 확장자로 쓰인 2글자 토큰(items.py, README.md)은 도메인으로 보지 않는다.
FILE_EXT_2 = {"py", "md", "sh", "db", "js", "ts", "go", "rs"}
PUBLIC_TLDS = {"com", "net", "org", "info", "biz", "edu", "gov", "mil", "int", "io", "co",
               "dev", "app", "cloud", "ai", "me", "tv", "xyz", "top", "tech", "online",
               "site", "store", "shop", "news", "live", "link", "pro", "plus", "one"}
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS 액세스 키"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "GitHub 토큰"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub PAT"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack 토큰"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "API 시크릿 키"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "개인키"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "JWT"),
    (re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+"), "평문 비밀번호"),
]

failures = []
checks = 0


def check(name, cond, detail=""):
    global checks
    checks += 1
    if not cond:
        failures.append("%s%s" % (name, (" — %s" % detail) if detail else ""))
    return bool(cond)


def sample_text(item):
    return "\n".join([item["sample"]["text"], item["sample"].get("caption", "")])


def main():
    if not os.path.exists(DATA_PATH):
        raise SystemExit("security_reference_data.json 이 없습니다.")
    data = json.load(open(DATA_PATH, encoding="utf-8"))
    items = data["items"]
    cats = data["categories"]
    html = open(PAGE_PATH, encoding="utf-8").read()
    tools = open(TOOLS_PATH, encoding="utf-8").read()

    print("== 데이터 ==")
    check("분야 6개", len(cats) == 6, len(cats))
    check("항목 12개", len(items) == 12, len(items))
    ids = [item.get("id") for item in items]
    check("ID 중복 없음", len(ids) == len(set(ids)), [x for x in ids if ids.count(x) > 1])

    cat_keys = [c["key"] for c in cats]
    counts = {key: sum(1 for item in items if item.get("category") == key) for key in cat_keys}
    check("분야별 2개", all(v == 2 for v in counts.values()), counts)
    check("분야 키 일치", {item.get("category") for item in items} == set(cat_keys),
          sorted({item.get("category") for item in items} - set(cat_keys)))

    for item in items:
        name = item.get("id", "?")
        missing = [field for field in REQUIRED if not item.get(field)]
        check("%s 필수 필드" % name, not missing, missing)
        check("%s 영향 등급" % name, item.get("impact") in IMPACTS, item.get("impact"))
        check("%s 명령 5개 이상" % name, len(item.get("commands") or []) >= 5, len(item.get("commands") or []))
        check("%s 옵션 7개 이상" % name, len(item.get("options") or []) >= 7, len(item.get("options") or []))
        for cmd in item.get("commands") or []:
            check("%s 명령 영향 등급" % name, cmd.get("impact") in IMPACTS, cmd.get("impact"))
            check("%s 명령 본문" % name, bool(cmd.get("cmd", "").strip()))
        for opt in item.get("options") or []:
            check("%s 옵션 필드" % name, all(opt.get(k) for k in ("flag", "meaning", "effect")))
        for key in READING_KEYS:
            check("%s 판독 %s" % (name, key), len(item["reading"].get(key) or []) >= 2,
                  len(item["reading"].get(key) or []))
        check("%s 공식 문서 2건 이상" % name, len(item.get("docs") or []) >= 2, len(item.get("docs") or []))
        for doc in item.get("docs") or []:
            url = doc.get("url", "")
            check("%s 문서 https" % name, url.startswith("https://"), url)
            check("%s 문서 형식" % name, bool(re.match(r"^https://[a-z0-9.-]+\.[a-z]{2,}(/[^\s]*)?$", url)), url)

    print("== 샘플 증적 위생 ==")
    for item in items:
        name = item["id"]
        text = sample_text(item)
        bad_ip = []
        for raw in IPV4_RE.findall(text):
            try:
                addr = ipaddress.ip_address(raw)
            except ValueError:
                bad_ip.append(raw)
                continue
            if not any(addr in net for net in DOC_NETS):
                bad_ip.append(raw)
        check("%s 샘플 IP" % name, not bad_ip, bad_ip)

        bad_domains = []
        for match in DOMAIN_RE.finditer(text):
            tld = match.group(1).lower()
            if tld in PUBLIC_TLDS or (len(tld) == 2 and tld.isalpha() and tld not in FILE_EXT_2):
                bad_domains.append(match.group(0))
        check("%s 샘플 도메인" % name, not bad_domains, bad_domains[:3])

        for pattern, label in SECRET_PATTERNS:
            hit = pattern.search(text)
            check("%s 샘플 %s 없음" % (name, label), not hit, hit.group(0)[:24] if hit else "")

    print("== 페이지 ==")
    articles = re.findall(r'<article class="sr-item" id="([^"]+)"', html)
    check("페이지 항목 12개", len(articles) == 12, len(articles))
    check("페이지 ID = 데이터 ID", articles == ids, [x for x in articles if x not in ids])
    rail_targets = re.findall(r'class="sr-tree-link" href="#([^"]+)"', html)
    check("레일 링크 12개", len(rail_targets) == 12, len(rail_targets))
    check("레일 = 항목 ID", rail_targets == ids, [x for x in rail_targets if x not in ids])

    cmd_count = sum(len(item["commands"]) for item in items)
    check("복사 버튼 = 명령 수", html.count('class="sr-cmd-copy"') == cmd_count,
          "%d vs %d" % (html.count('class="sr-cmd-copy"'), cmd_count))
    check("명령 블록 = 명령 수", len(re.findall(r'<pre id="[^"]+-cmd-\d+">', html)) == cmd_count)
    check("항목별 링크 복사 버튼", html.count('class="sr-copy-link"') == 12,
          html.count('class="sr-copy-link"'))
    check("이모지 0개", not EMOJI_RE.search(html))
    check("그라데이션 없음", "gradient" not in html.lower())
    check("인라인 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", html, re.I))
    check("http:// 문서 링크 없음", not re.search(r'href="http://', html))
    check("검색 입력 1개", html.count('id="srSearch"') == 1)
    chip_count = len(re.findall(r'<button[^>]*class="sr-chip[ "]', html))
    check("분야 칩 7개(전체 포함)", chip_count == 7, chip_count)

    embedded = re.search(r'<script type="application/json" id="srData">(.*?)</script>', html, re.S)
    if check("페이지 데이터 블록", embedded is not None):
        manifest = json.loads(embedded.group(1).replace("<\\/", "</"))
        check("페이지 데이터 항목 수", manifest.get("total") == 12, manifest.get("total"))
        check("페이지 데이터 ID", manifest.get("ids") == ids)
        check("페이지 데이터 분야", [c["key"] for c in manifest.get("categories", [])] == cat_keys)
        check("페이지 데이터 분야별 항목",
              all([c["items"] for c in manifest["categories"] if c["key"] == cat["key"]]
                  == [[i["id"] for i in items if i["category"] == cat["key"]]] for cat in cats))

    print("== tools.html 상호 연결 ==")
    for item in items:
        for cheat in item.get("cheats") or []:
            anchor = cheat["anchor"]
            check("%s %s 카드 존재" % (item["id"], anchor), 'id="%s"' % anchor in tools)
            block = re.search(r'<article class="cheat-card" id="%s".*?</article>' % re.escape(anchor), tools, re.S)
            if check("%s %s 카드 본문" % (item["id"], anchor), block is not None):
                check("%s %s 역링크" % (item["id"], anchor),
                      "security-reference.html#%s" % item["id"] in block.group(0))
    ref_links = re.findall(r'class="cheat-ref" href="security-reference.html#([^"]+)"', tools)
    check("tools 측 백과사전 링크 11개", len(ref_links) == 11, len(ref_links))
    check("tools 링크 ID 유효", all(link in ids for link in ref_links),
          [link for link in ref_links if link not in ids])
    check("백과사전 측 치트시트 링크", len(re.findall(r'href="tools\.html#cheat-\d+"', html)) == 11,
          len(re.findall(r'href="tools\.html#cheat-\d+"', html)))

    if failures:
        print("\n검사 실패 %d건 (검사 %d항목)" % (len(failures), checks))
        for message in failures:
            print("  [실패] %s" % message)
        return 1
    print("점검 백과사전 검사 통과: %d항목" % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())

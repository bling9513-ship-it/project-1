#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""보안 취약점 점검 도구 백과사전(security-reference.html) 데이터·페이지 검증.

빌더와 독립된 규칙으로 다음을 확인한다.
  1) 데이터(security_reference_data.json)
     - 8개 분야 22개 항목(기본 6분야 12 · 오픈소스 점검 툴 7 · 진단 패턴 3), ID 중복 없음
     - 도구 항목: 필수 필드·명령 5개 이상·옵션 7개 이상·보고서 필드
     - 진단 패턴 항목: 판별 패턴 5개 이상·모의 응답·차단 로그·조치·재점검
     - 실행 영향 등급 3종만 사용, 공식 문서는 https 공식 호스트
     - 샘플·패턴·모의 응답에 실제 사설·공인 IP, 실제 도메인, 시크릿 패턴이 없음
  2) 페이지(security-reference.html)
     - 항목·레일 링크 22개, 복사 버튼 = 명령 + 패턴 수
     - 합성 문자열(<script>alert(1)</script> · {{7*7}})이 원문 태그가 아니라 텍스트로만 존재
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
import urllib.parse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "security_reference_data.json")
PAGE_PATH = os.path.join(BASE_DIR, "security-reference.html")
TOOLS_PATH = os.path.join(BASE_DIR, "tools.html")

IMPACTS = {"로컬 파일 읽기", "네트워크 요청", "별도 변경 승인 필요"}
EXPECTED_PER_CAT = {"asset": 2, "web": 2, "tls": 2, "packet": 2, "code": 2, "os": 2,
                    "osscan": 7, "probe": 3}
REQUIRED_TOOL = ("id", "category", "tool", "title", "summary", "purpose", "verified_version",
                 "input_type", "privilege", "impact", "impact_note", "commands", "options",
                 "reading", "sample", "docs")
REQUIRED_PROBE = ("id", "category", "tool", "title", "summary", "purpose", "verified_version",
                  "input_type", "privilege", "impact", "impact_note", "commands", "patterns",
                  "mock", "block_log", "reading", "docs")
PATTERN_FIELDS = ("name", "payload", "where", "principle", "safe", "vulnerable")
READING_KEYS = ("normal", "abnormal", "false_positive", "action", "recheck")
# 공식 HTTPS 문서 호스트만 허용한다(임의 블로그·미러 차단).
DOC_HOSTS = {
    "bind9.readthedocs.io", "cheatsheetseries.owasp.org", "cirt.net", "cisofy.com", "curl.se",
    "datatracker.ietf.org", "developer.mozilla.org", "docs.openssl.org",
    "docs.projectdiscovery.io", "github.com", "kubescape.io", "learn.microsoft.com", "nmap.org",
    "owasp.org", "semgrep.dev", "testssl.sh", "trivy.dev", "www.gnu.org", "www.tcpdump.org",
    "www.wireshark.org",
}
OSSCAN_IDS = ("oss-nuclei", "oss-ffuf", "oss-sqlmap", "oss-nikto", "oss-subfinder",
              "oss-httpx", "oss-testssl")
PROBE_IDS = ("probe-input-validation", "probe-server-request", "probe-file-access")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]")
IPV4_RE = re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b")
DOMAIN_RE = re.compile(r"\b(?:[a-z0-9][a-z0-9-]*\.)+([a-z]{2,})\b", re.I)
DOC_NETS = [ipaddress.ip_network("192.0.2.0/24"), ipaddress.ip_network("198.51.100.0/24"),
            ipaddress.ip_network("203.0.113.0/24"), ipaddress.ip_network("127.0.0.0/8"),
            # 링크로컬 메타데이터 주소는 SSRF 차단 확인용으로만 등장한다(자격증명 경로 없음).
            ipaddress.ip_network("169.254.0.0/16")]
# 샘플·패턴에 실제 도메인이 섞이지 않았는지 보는 기준.
#   - 2글자 국가 코드(.kr·.jp·.io …)와 널리 쓰이는 공인 TLD 가 붙은 이름은 실제 도메인으로 본다.
#   - fixture.test·evil.test(RFC 2606), 예제 파일 확장자(.pcap·.crt …), 코드 식별자(tls.handshake.type)는 통과.
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


def evidence_text(item):
    """샘플·패턴·모의 응답·차단 로그를 하나로 모아 위생 검사에 쓴다."""
    parts = []
    if item.get("sample"):
        parts += [item["sample"]["text"], item["sample"].get("caption", "")]
    for pat in item.get("patterns") or []:
        parts += [pat["payload"], pat["where"], pat["principle"], pat["safe"], pat["vulnerable"]]
    if item.get("mock"):
        parts += [item["mock"]["safe_text"], item["mock"]["vuln_text"]]
    if item.get("block_log"):
        parts += [item["block_log"]["text"]]
    return "\n".join(parts)


def main():
    if not os.path.exists(DATA_PATH):
        raise SystemExit("security_reference_data.json 이 없습니다.")
    data = json.load(open(DATA_PATH, encoding="utf-8"))
    items = data["items"]
    cats = data["categories"]
    html = open(PAGE_PATH, encoding="utf-8").read()
    tools = open(TOOLS_PATH, encoding="utf-8").read()

    print("== 데이터 ==")
    check("분야 8개", len(cats) == 8, len(cats))
    check("항목 22개", len(items) == 22, len(items))
    ids = [item.get("id") for item in items]
    check("ID 중복 없음", len(ids) == len(set(ids)), [x for x in ids if ids.count(x) > 1])

    cat_keys = [c["key"] for c in cats]
    counts = {key: sum(1 for item in items if item.get("category") == key) for key in cat_keys}
    check("분야별 항목 수", counts == EXPECTED_PER_CAT, counts)
    check("분야 키 일치", {item.get("category") for item in items} == set(cat_keys),
          sorted({item.get("category") for item in items} - set(cat_keys)))
    check("오픈소스 점검 툴 7종", [i for i in ids if i in OSSCAN_IDS] == list(OSSCAN_IDS),
          [i for i in OSSCAN_IDS if i not in ids])
    check("진단 패턴 3종", [i for i in ids if i in PROBE_IDS] == list(PROBE_IDS),
          [i for i in PROBE_IDS if i not in ids])

    for item in items:
        name = item.get("id", "?")
        probe = name in PROBE_IDS
        required = REQUIRED_PROBE if probe else REQUIRED_TOOL
        missing = [field for field in required if not item.get(field)]
        check("%s 필수 필드" % name, not missing, missing)
        check("%s 영향 등급" % name, item.get("impact") in IMPACTS, item.get("impact"))
        check("%s 명령 3개 이상" % name, len(item.get("commands") or []) >= 3,
              len(item.get("commands") or []))
        for cmd in item.get("commands") or []:
            check("%s 명령 영향 등급" % name, cmd.get("impact") in IMPACTS, cmd.get("impact"))
            check("%s 명령 본문" % name, bool(cmd.get("cmd", "").strip()))
        for key in READING_KEYS:
            check("%s 판독 %s" % (name, key), len(item["reading"].get(key) or []) >= 2,
                  len(item["reading"].get(key) or []))
        check("%s 공식 문서 2건 이상" % name, len(item.get("docs") or []) >= 2, len(item.get("docs") or []))
        for doc in item.get("docs") or []:
            url = doc.get("url", "")
            host = urllib.parse.urlparse(url).netloc
            check("%s 문서 https" % name, url.startswith("https://"), url)
            check("%s 문서 형식" % name, bool(re.match(r"^https://[a-z0-9.-]+\.[a-z]{2,}(/[^\s]*)?$", url)), url)
            check("%s 문서 공식 호스트" % name, host in DOC_HOSTS, host)

        if probe:
            patterns = item.get("patterns") or []
            check("%s 판별 패턴 5개 이상" % name, len(patterns) >= 5, len(patterns))
            for pat in patterns:
                check("%s 패턴 필드" % name, all(pat.get(k) for k in PATTERN_FIELDS),
                      [k for k in PATTERN_FIELDS if not pat.get(k)])
            check("%s 모의 응답 쌍" % name,
                  bool(item["mock"].get("safe_text")) and bool(item["mock"].get("vuln_text")))
            check("%s 모의 응답 라벨" % name,
                  bool(item["mock"].get("safe_label")) and bool(item["mock"].get("vuln_label")))
            check("%s 차단 로그" % name, bool(item["block_log"].get("text", "").strip()))
            check("%s 조치 2건 이상" % name, len(item["reading"].get("action") or []) >= 2)
            check("%s 재점검 2건 이상" % name, len(item["reading"].get("recheck") or []) >= 2)
        else:
            check("%s 명령 5개 이상" % name, len(item.get("commands") or []) >= 5,
                  len(item.get("commands") or []))
            check("%s 옵션 7개 이상" % name, len(item.get("options") or []) >= 7,
                  len(item.get("options") or []))
            for opt in item.get("options") or []:
                check("%s 옵션 필드" % name, all(opt.get(k) for k in ("flag", "meaning", "effect")))
        if item.get("category") == "osscan":
            report = item.get("report") or {}
            check("%s 보고서 형식" % name, bool(report.get("format")))
            check("%s 보고서 필드 3개 이상" % name, len(report.get("fields") or []) >= 3,
                  len(report.get("fields") or []))
            for field in report.get("fields") or []:
                check("%s 보고서 필드명" % name, all(field.get(k) for k in ("name", "meaning", "note")))

    print("== 샘플·패턴 위생 ==")
    for item in items:
        name = item["id"]
        text = evidence_text(item)
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
    check("페이지 항목 22개", len(articles) == 22, len(articles))
    check("페이지 ID = 데이터 ID", articles == ids, [x for x in articles if x not in ids])
    rail_targets = re.findall(r'class="sr-tree-link" href="#([^"]+)"', html)
    check("레일 링크 22개", len(rail_targets) == 22, len(rail_targets))
    check("레일 = 항목 ID", rail_targets == ids, [x for x in rail_targets if x not in ids])

    cmd_count = sum(len(item["commands"]) for item in items)
    pat_count = sum(len(item.get("patterns") or []) for item in items)
    check("복사 버튼 = 명령 + 패턴", html.count('class="sr-cmd-copy"') == cmd_count + pat_count,
          "%d vs %d" % (html.count('class="sr-cmd-copy"'), cmd_count + pat_count))
    check("명령 블록 = 명령 수", len(re.findall(r'<pre id="[^"]+-cmd-\d+">', html)) == cmd_count)
    check("항목별 링크 복사 버튼", html.count('class="sr-copy-link"') == 22,
          html.count('class="sr-copy-link"'))
    check("이모지 0개", not EMOJI_RE.search(html))
    check("그라데이션 없음", "gradient" not in html.lower())
    check("인라인 핸들러 없음", not re.search(r"<[^>]+\son[a-z]+=", html, re.I))
    check("http:// 문서 링크 없음", not re.search(r'href="http://', html))
    check("검색 입력 1개", html.count('id="srSearch"') == 1)
    chip_count = len(re.findall(r'<button[^>]*class="sr-chip[ "]', html))
    check("분야 칩 9개(전체 포함)", chip_count == len(cats) + 1, chip_count)
    check("새 분야 이름 표시", "오픈소스 점검 툴" in html and "진단 패턴·방어 검증" in html)
    check("모의 응답·차단 로그 절", "모의 응답 대조" in html and "차단 로그 예시" in html)

    print("== 합성 문자열 (텍스트로만) ==")
    # 원문 태그가 그대로 들어가면 실제 <script> 요소가 생긴다.
    check("<script> 원문 태그 없음", "<script>alert(1)</script>" not in html)
    check("<script> 이스케이프 존재", "&lt;script&gt;alert(1)&lt;/script&gt;" in html)
    check("속성 탈출 패턴 이스케이프", "&quot; autofocus onfocus=&quot;alert(1)" in html
          or "&quot; autofocus onfocus=&quot;alert(1)" in html.replace("&#x27;", "'"))
    check("SSTI 패턴 텍스트", "{{7*7}}" in html)
    check("SSTI 결과값 미노출", "Template: 49" in html)  # 모의 응답(취약 예시) 안에서만
    for item in items:
        for pat in item.get("patterns") or []:
            if "<" not in pat["payload"]:
                continue
            check("%s 패턴 원문 태그 없음" % item["id"], pat["payload"] not in html, pat["payload"])
    check("패턴 복사 대상 코드 ID", len(re.findall(r'<code class="sr-code" id="[^"]+-pat-\d+">', html)) == pat_count,
          len(re.findall(r'<code class="sr-code" id="[^"]+-pat-\d+">', html)))
    check("패턴 복사 버튼 대상 일치",
          len(re.findall(r'data-copy-cmd="([^"]+-pat-\d+)"', html)) == pat_count)
    check("다중 속성/앰퍼샌드 이스케이프", "&amp;" in html and "&lt;" in html and "&gt;" in html)

    embedded = re.search(r'<script type="application/json" id="srData">(.*?)</script>', html, re.S)
    if check("페이지 데이터 블록", embedded is not None):
        manifest = json.loads(embedded.group(1).replace("<\\/", "</"))
        check("페이지 데이터 항목 수", manifest.get("total") == 22, manifest.get("total"))
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

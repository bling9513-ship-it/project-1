# -*- coding: utf-8 -*-
"""
출퇴근길 보안 워게임 (wargame.html) 빌더.

문제의 원본은 SQLite DB(archive.db)의 wargame_questions 테이블이다.
- 정적 20문제(web/log/sys/net × 4~6)는 아래 QUESTIONS를 최초 1회 DB로 이관해 id를 그대로 보존한다.
- 매일 08:00 wargame_generator.py 가 EXAONE으로 새 문제를 2개씩 추가하면 is_daily=1 로 쌓이고,
  빌드는 데일리 최신 문제를 맨 위에 배치하며 '오늘의 문제'/'YYYY-MM-DD 추가' 배지를 붙인다.

브라우저에서는 즉시 채점·해설·진행 기록(localStorage, 키 secjobs-wargame-v1)이 동작한다.
채용공고(index)·시험 공부(study)·AI 트렌드(ai)·CVE 리포트(cve)·옷차림(outfit)과 같은
secjobs-theme 라이트/다크 테마와 7탭 내비게이션을 공유한다.
"""
import json
import os
from datetime import datetime, timezone, timedelta
from html import escape as esc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WARGAME_HTML = os.path.join(BASE_DIR, "wargame.html")

# 정적 20문제가 처음 만들어진 날 (DB created_date 기본값)
STATIC_CREATED_DATE = "2026-11-20"

CATS = [
    {"key": "web", "label": "웹 해킹"},
    {"key": "log", "label": "로그·침해 분석"},
    {"key": "sys", "label": "시스템·권한 상승"},
    {"key": "net", "label": "네트워크·패킷"},
]

LEVELS = [
    {"key": "basic", "label": "입문"},
    {"key": "mid", "label": "중급"},
    {"key": "adv", "label": "심화"},
]


QUESTIONS = [
    # ------------------------------------------------------------------ 웹 해킹
    {
        "id": "web-01", "cat": "web", "level": "basic", "type": "choice",
        "title": "검색어가 그대로 쿼리 문자열이 된 재고 조회",
        "brief": "상품 재고 조회 API는 검색어를 SQL 문자열에 이어 붙여 실행합니다.",
        "blocks": [
            {"label": "Python · inventory.py",
             "code": '@app.get("/stock")\ndef stock():\n'
                     '    q = request.args.get("q", "")\n'
                     '    sql = "SELECT name, stock FROM items WHERE name LIKE \'%" + q + "%\'"\n'
                     '    return db.execute(sql).fetchall()'},
        ],
        "prompt": "이 코드에서 가장 먼저 고쳐야 할 취약점은?",
        "hints": ["사용자 입력이 SQL 문장 안에서 '값'으로만 쓰이는지, 아니면 문법 일부가 될 수 있는지 보세요.", "문자열 결합(+) 대신 ? 자리표시자와 파라미터 튜플로 쿼리를 먼저 고정하는 것이 정답입니다."],
        "choices": [
            "SQL Injection — 입력값이 문자열 결합으로 쿼리 구조 자체를 바꿀 수 있다",
            "XSS — 사용자 입력이 브라우저 화면에 그대로 출력된다",
            "CSRF — 상태를 바꾸는 요청에 토큰 검증이 없다",
            "경로 탐색 — 파일 경로를 입력으로 받아 상위 디렉터리에 접근할 수 있다",
        ],
        "answer": 0,
        "explain": {
            "principle": "LIKE '%...%' 안에 `' OR 1=1--` 같은 값이 들어가면 문자열 리터럴이 닫히고 조건이 새로 붙습니다. 쿼리와 데이터가 하나의 문자열로 합쳐지기 때문에 DB는 입력을 '값'이 아니라 'SQL 문법'으로 해석합니다.",
            "impact": "인증 우회, 전 테이블 덤프, UNION 기반 정보 유출, DB 권한에 따라 파일 읽기·쓰기까지 이어집니다. 쿼리를 먼저 고정하고 입력을 바인딩하면 입력은 항상 값으로만 취급됩니다.",
            "vuln": 'sql = "SELECT name, stock FROM items WHERE name LIKE \'%" + q + "%\'"\ndb.execute(sql)',
            "secure": 'sql = "SELECT name, stock FROM items WHERE name LIKE ?"\ndb.execute(sql, ("%" + q + "%",))',
        },
    },
    {
        "id": "web-02", "cat": "web", "level": "basic", "type": "input",
        "title": "비밀번호를 몰라도 통과하는 로그인",
        "brief": "로그인 API는 이메일과 비밀번호를 아래 쿼리에 그대로 이어 붙입니다. 비밀번호는 모르지만 첫 번째 계정으로 로그인해 볼 수 있습니다.",
        "blocks": [
            {"label": "SQL · 실제로 실행되는 쿼리",
             "code": "SELECT id, role FROM users\n"
                     "WHERE email = '<이메일 입력>' AND password = '<비밀번호 입력>';"},
        ],
        "prompt": "이메일 입력창에 넣을 페이로드를 완성하세요. 앞의 문자열을 닫고, 조건을 항상 참으로 만든 뒤, 뒤쪽 비밀번호 조건을 주석으로 지웁니다.",
        "patterns": [r"^(?:['\"]* *or +['\"]*1['\"]* *= *['\"]*1(?: *(?:--|#|/[*]).*)?|[A-Za-z0-9._@+-]+['\"] *(?:--|#|/[*]).*)$"],
        "placeholder": "완성한 페이로드 입력",
        "sample": "' OR 1=1-- ",
        "chips": ["'", " OR 1=1", "-- ", "#"],
        "hints": [
            "비밀번호 조건 자체를 없애면 됩니다. SQL 주석은 `--`(뒤에 공백) 또는 `#`입니다.",
            "이메일에 `'`를 넣어 문자열을 닫고 `OR 1=1`로 항상 참인 조건을 붙인 뒤 `--`로 나머지 `AND password = ...`를 지웁니다. 정답 예시는 `' OR 1=1-- ` 입니다.",
        ],
        "explain": {
            "principle": "`'`로 email 문자열을 닫고 `OR 1=1`로 조건을 항상 참으로 만든 뒤 `--`로 뒤의 `AND password = ...`를 주석 처리하면, DB는 조건에 맞는 첫 번째 행을 반환합니다. 비밀번호 비교는 아예 실행되지 않습니다.",
            "impact": "계정 탈취와 권한 상승. 로그인 실패 횟수 제한만으로는 막을 수 없고, 파라미터 바인딩과 비밀번호 해시 검증이 근본 대책입니다.",
            "vuln": 'sql = f"SELECT id, role FROM users WHERE email = \'{email}\' AND password = \'{pw}\'"\nrow = db.execute(sql).fetchone()',
            "secure": 'cur.execute("SELECT id, pw_hash, role FROM users WHERE email = %s", (email,))\n'
                      'row = cur.fetchone()\n'
                      'if not row or not check_password(pw, row["pw_hash"]):\n'
                      '    abort(401)',
        },
    },
    {
        "id": "web-03", "cat": "web", "level": "mid", "type": "choice",
        "title": "송장 번호만 바꿔도 열리는 다른 사람의 청구서",
        "brief": "로그인한 사용자는 자기 송장만 볼 수 있어야 합니다. 아래 API는 토큰은 검증하지만 송장의 주인은 확인하지 않습니다.",
        "blocks": [
            {"label": "HTTP · 정상 요청",
             "code": "GET /api/invoices/10428 HTTP/1.1\n"
                     "Host: billing.example.com\n"
                     "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
            {"label": "Python · invoices.py",
             "code": '@app.get("/api/invoices/<int:invoice_id>")\n'
                     "@login_required\n"
                     "def invoice(invoice_id):\n"
                     '    row = db.one("SELECT * FROM invoices WHERE id = ?", (invoice_id,))\n'
                     "    return jsonify(row)"},
        ],
        "prompt": "10428을 10429로 바꿔 요청하면 무슨 일이 일어나며, 올바른 수정은?",
        "hints": ["인증(로그인 여부)과 인가(이 객체를 볼 권한)를 구분해 보세요. 이 코드는 어느 쪽이 빠졌나요?", "WHERE 절에 id만 있는 것이 문제입니다. AND user_id = ? 로 소유자를 함께 묶어야 합니다."],
        "choices": [
            "다른 사용자의 송장이 그대로 반환되는 IDOR — 조회 조건에 소유자(user_id)를 함께 묶는다",
            "서명 검증이 없어 토큰을 위조할 수 있는 취약점 — JWT 알고리즘을 고정한다",
            "요청 수 제한이 없어 무차별 대입이 가능한 취약점 — 레이트리밋을 건다",
            "HTTPS가 아니어서 평문이 노출되는 취약점 — TLS를 강제한다",
        ],
        "answer": 0,
        "explain": {
            "principle": "객체를 가리키는 식별자를 사용자가 바꿀 수 있는데 서버가 '이 객체가 이 사용자 것인지'를 확인하지 않으면 IDOR입니다. 인증(로그인했는가)은 통과하지만 인가(이 객체를 볼 권한이 있는가)가 빠진 상태입니다.",
            "impact": "순차 증가하는 번호만 바꿔 전 사용자의 청구서·개인정보·계약서를 열람합니다. 응답 크기나 오류 코드 차이만으로도 객체 존재 여부가 새어 나갑니다.",
            "vuln": 'row = db.one("SELECT * FROM invoices WHERE id = ?", (invoice_id,))\nreturn jsonify(row)',
            "secure": 'row = db.one("SELECT * FROM invoices WHERE id = ? AND user_id = ?",\n'
                      '            (invoice_id, current_user.id))\n'
                      "if row is None:\n"
                      "    abort(404)",
        },
    },
    {
        "id": "web-04", "cat": "web", "level": "mid", "type": "choice",
        "title": "이미지 주소로 내부 메타데이터를 부른 썸네일 API",
        "brief": "프로필 이미지 URL을 받아 서버가 대신 내려받는 기능입니다. 한 사용자가 사내 전용 주소를 넣었고, 응답에 자격증명이 담겨 돌아왔습니다.",
        "blocks": [
            {"label": "Python · thumbnail.py",
             "code": 'url = request.json["image_url"]\n'
                     "r = requests.get(url, timeout=5, allow_redirects=True)\n"
                     'return Response(r.content, mimetype=r.headers.get("Content-Type"))'},
            {"label": "요청 기록",
             "code": 'POST /api/thumbnail  {"image_url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/app-role"}\n'
                     "200 OK  content-type: text/plain\n"
                     '{"AccessKeyId": "ASIA...", "SecretAccessKey": "...", "Token": "..."}'},
        ],
        "prompt": "이 요청이 성공한 이유와 가장 정확한 대응은?",
        "hints": ["이미지 URL을 가져오는 주체가 사용자 브라우저인지 서버인지 확인해 보세요.", "169.254.169.254는 클라우드 메타데이터 주소입니다. 서버가 내부 주소로 대신 요청하는 SSRF입니다."],
        "choices": [
            "SSRF — 서버가 내부 주소로 요청을 대신 보내 클라우드 자격증명이 노출된다. 허용 호스트 목록과 사설·링크로컬 대역 차단이 필요하다",
            "XXE — XML 외부 엔티티로 서버 파일을 읽은 것이다. XML 파서 설정을 바꾼다",
            "오픈 리다이렉트 — 302 응답으로 사용자를 다른 사이트로 보낸 것이다. redirect_uri를 검증한다",
            "CSRF — 사용자 브라우저가 요청을 위조한 것이다. SameSite 쿠키를 설정한다",
        ],
        "answer": 0,
        "explain": {
            "principle": "이미지 URL을 받아 서버가 대신 요청하면 그 요청은 사용자 PC가 아니라 서버의 네트워크 위치에서 나갑니다. 169.254.169.254는 클라우드 메타데이터 서비스로, IAM 임시 자격증명이 그대로 반환됩니다. localhost, 10.0.0.0/8, 192.168.0.0/16, DNS 리바인딩도 같은 부류입니다.",
            "impact": "클라우드 자격증명 탈취로 계정 전체가 넘어가고, 내부망 포트 스캔과 관리자 페이지 접근으로 이어집니다. URL은 파싱 후 IP 기준으로 검사하고, 리다이렉트를 따라가지 않으며, 응답 본문을 그대로 돌려주지 않아야 합니다.",
            "vuln": 'r = requests.get(request.json["image_url"], timeout=5, allow_redirects=True)\nreturn Response(r.content)',
            "secure": 'host = urlparse(user_url).hostname\n'
                      "ip = ipaddress.ip_address(socket.gethostbyname(host))\n"
                      "if host not in ALLOWED_HOSTS or ip.is_private or ip.is_loopback or ip.is_link_local:\n"
                      "    abort(400)\n"
                      "r = requests.get(user_url, timeout=5, allow_redirects=False)",
        },
    },
    {
        "id": "web-05", "cat": "web", "level": "mid", "type": "input",
        "title": "인코딩된 슬래시로 빠져나간 다운로드 경로",
        "brief": "첨부파일 다운로드 API가 파일명을 검증 없이 경로에 붙입니다. 아래 요청이 200으로 응답하며 파일 내용이 돌아왔습니다.",
        "blocks": [
            {"label": "HTTP · 요청",
             "code": "GET /download?file=..%2f..%2f..%2fetc%2fpasswd HTTP/1.1\nHost: board.example.com"},
            {"label": "Python · files.py",
             "code": 'name = request.args["file"]\n'
                     'return send_file(os.path.join("/var/www/uploads", name))'},
        ],
        "prompt": "file 값을 디코딩했을 때 실제로 열린 경로를 입력하세요. (%2f는 /, %2e는 .입니다)",
        "patterns": [r"^(?:[.][.]/)+etc/passwd$"],
        "placeholder": "열린 경로 입력",
        "sample": "../../../etc/passwd",
        "chips": ["../", "..%2f", "/etc/passwd"],
        "hints": [
            "URL에서 %2f는 /, %2e는 .입니다. 퍼센트 인코딩을 먼저 되돌려 보세요.",
            "/var/www/uploads에서 위로 세 번 올라가면 /이고 그 뒤에 etc/passwd가 붙습니다. 답은 `../../../etc/passwd`입니다.",
        ],
        "explain": {
            "principle": "%2f로 인코딩한 슬래시는 단순 필터를 통과한 뒤 WAS에서 디코딩되어 경로 구분자로 동작합니다. `..`는 상위 디렉터리를 뜻하므로 업로드 폴더 밖의 파일을 읽을 수 있습니다. 이중 인코딩(%252e), 유니코드, `....//` 같은 우회도 함께 나옵니다.",
            "impact": "설정 파일·DB 계정·SSH 키·소스코드가 유출됩니다. 읽기에서 그치지 않고 업로드 기능과 결합하면 웹쉘 배치로 이어집니다.",
            "vuln": 'return send_file(os.path.join("/var/www/uploads", request.args["file"]))',
            "secure": 'base = os.path.realpath("/var/www/uploads")\n'
                      'path = os.path.realpath(os.path.join(base, name))\n'
                      "if not path.startswith(base + os.sep) or not os.path.isfile(path):\n"
                      "    abort(404)\n"
                      "send_file(path)",
        },
    },
    {
        "id": "web-06", "cat": "web", "level": "adv", "type": "choice",
        "title": "alg를 none으로 바꾼 관리자 토큰",
        "brief": "API 게이트웨이가 JWT 헤더의 alg 값을 그대로 사용해 검증합니다. 아래 토큰은 서명이 비어 있는데도 통과했습니다.",
        "blocks": [
            {"label": "디코딩된 토큰",
             "code": 'header    = {"alg": "none", "typ": "JWT"}\n'
                     'payload   = {"sub": "user1", "role": "admin", "exp": 1799999999}\n'
                     'signature = ""      # 비어 있음'},
            {"label": "Python · auth.py",
             "code": "header = jwt.get_unverified_header(token)\n"
                     'alg = header["alg"]\n'
                     "claims = jwt.decode(token, KEY, algorithms=[alg])"},
        ],
        "prompt": "이 토큰이 통과할 수 있는 이유로 가장 정확한 것은?",
        "hints": ["JWT는 헤더에 서명 알고리즘(alg)을 담습니다. 서버가 헤더 값을 그대로 믿으면 무엇이 가능해질까요?", "alg: none과 빈 서명을 허용하면 서명 검증 없이 통과합니다. 허용 알고리즘을 코드에 고정해야 합니다."],
        "choices": [
            "서명 없는 alg: none을 서버가 허용해, 페이로드만 바꿔도 서명 검증 없이 통과한다",
            "HS256 키 길이가 짧아 브루트포스로 서명을 맞출 수 있다",
            "exp가 미래 시각이라 만료 검증이 생략된다",
            "Base64url은 암호화라서 페이로드를 바꿀 수 없다",
        ],
        "answer": 0,
        "explain": {
            "principle": "JWT는 헤더에 서명 알고리즘을 담습니다. 서버가 그 값을 신뢰하면 공격자가 alg를 none으로 바꾸고 서명을 비우는 것만으로 통과합니다. RS256 공개키를 HS256 비밀키로 오인하는 알고리즘 혼동(RS→HS)도 같은 뿌리입니다.",
            "impact": "role을 admin으로 바꾼 토큰을 스스로 만들어 관리자 권한을 얻습니다. 허용 알고리즘을 서버에 고정하고, alg: none을 거부하고, kid·jku를 외부 입력으로 신뢰하지 않아야 합니다. 세션 무효화를 위해 jti와 짧은 exp도 함께 씁니다.",
            "vuln": 'alg = jwt.get_unverified_header(token)["alg"]\nclaims = jwt.decode(token, KEY, algorithms=[alg])',
            "secure": 'claims = jwt.decode(token, PUBLIC_KEY,\n'
                      '                    algorithms=["RS256"],\n'
                      '                    options={"require": ["exp", "sub"]})',
        },
    },

    # ------------------------------------------------------------- 로그·침해 분석
    {
        "id": "log-01", "cat": "log", "level": "basic", "type": "choice",
        "title": "새벽 3시, 같은 IP가 반복한 인코딩 요청",
        "brief": "웹 서버 액세스 로그에서 한 외부 IP가 새벽에 남긴 기록입니다.",
        "blocks": [
            {"label": "Apache access.log",
             "code": '203.0.113.45 - - [20/Nov/2026:03:11:02 +0900] "GET /product.php?id=1%27%20OR%201=1-- HTTP/1.1" 200 5123 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"\n'
                     '203.0.113.45 - - [20/Nov/2026:03:11:04 +0900] "GET /product.php?id=1%20AND%20SLEEP(5) HTTP/1.1" 200 39012 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'},
        ],
        "prompt": "이 요청들이 보여 주는 공격은?",
        "hints": ["쿼리 문자열의 %27, %20을 먼저 디코딩해 보세요. 그리고 응답 크기가 왜 달라졌는지 보세요.", "1' OR 1=1-- 는 참 조건과 주석, SLEEP(5)는 시간 기반 블라인드 SQLi 신호입니다."],
        "choices": [
            "SQL Injection — 인코딩된 따옴표와 OR 1=1, SLEEP(5)로 조건과 응답 시간을 조작하는 시도",
            "XSS — 스크립트 태그를 심어 쿠키를 탈취하려는 시도",
            "디렉터리 리스팅 — 없는 경로를 반복 탐색한 기록",
            "정상 트래픽 — 응답이 200이고 크기도 일정하다",
        ],
        "answer": 0,
        "explain": {
            "principle": "%27은 따옴표, %20은 공백입니다. 디코딩하면 `id=1' OR 1=1--`가 되어 참 조건과 주석으로 쿼리를 바꾸고, `AND SLEEP(5)`는 응답 지연으로 참·거짓을 구분하는 블라인드 SQLi 기법입니다. 응답 크기가 5123에서 39012로 달라진 것도 결과 집합이 바뀌었다는 신호입니다.",
            "impact": "도구 없이 브라우저로도 실행할 수 있는 공격입니다. WAF 로그만 보지 말고 파라미터 바인딩 여부와 같은 IP의 다른 경로 호출, 성공 여부(응답 크기·시간)를 함께 확인해야 합니다.",
            "vuln": "$id = $_GET['id'];\n$sql = \"SELECT * FROM products WHERE id = $id\";",
            "secure": '$stmt = $pdo->prepare("SELECT * FROM products WHERE id = ?");\n$stmt->execute([$_GET[\'id\']]);',
        },
    },
    {
        "id": "log-02", "cat": "log", "level": "mid", "type": "input",
        "title": "검색 로그에 남은 인코딩된 스크립트",
        "brief": "검색 API 로그에 인코딩된 요청이 남았습니다. 직후 같은 클라이언트가 마이페이지를 열었습니다.",
        "blocks": [
            {"label": "Apache access.log",
             "code": '198.51.100.23 - - [20/Nov/2026:03:22:41 +0900] "GET /search?q=%3Cscript%3Ealert(document.cookie)%3C%2Fscript%3E HTTP/1.1" 200 812 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"\n'
                     '198.51.100.23 - - [20/Nov/2026:03:22:45 +0900] "GET /mypage HTTP/1.1" 200 1902 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"'},
        ],
        "prompt": "q 파라미터를 URL 디코딩한 값을 그대로 입력하세요.",
        "patterns": [r"^<script>alert[(]document[.]cookie[)][ ]*<[/]script>$"],
        "placeholder": "디코딩한 값 입력",
        "sample": "<script>alert(document.cookie)</script>",
        "chips": ["<script>", "</script>", "alert(document.cookie)"],
        "hints": [
            "%3C는 <, %3E는 >, %2F는 /입니다.",
            "디코딩하면 `<script>alert(document.cookie)</script>`가 됩니다. 검색어가 결과 화면에 그대로 되비춰지는 반사형 XSS입니다.",
        ],
        "explain": {
            "principle": "퍼센트 인코딩은 전송 형식일 뿐입니다. WAS가 디코딩한 값을 출력에 그대로 넣으면 브라우저가 스크립트로 실행합니다. 검색어가 '검색어: ...' 형태로 되비춰지는 화면은 반사형 XSS의 전형입니다.",
            "impact": "세션 쿠키 탈취, 관리자 화면에서의 권한 있는 동작 실행, 피싱 링크 위장. 출력 인코딩과 CSP, HttpOnly 쿠키를 함께 적용합니다.",
            "vuln": "echo \"<p>검색어: \" . $_GET['q'] . \"</p>\";",
            "secure": "echo \"<p>검색어: \" . htmlspecialchars($_GET['q'], ENT_QUOTES, 'UTF-8') . \"</p>\";",
        },
    },
    {
        "id": "log-03", "cat": "log", "level": "mid", "type": "choice",
        "title": "실패 40초 뒤에 남은 Accepted password",
        "brief": "운영 서버 auth.log의 같은 IP 기록입니다.",
        "blocks": [
            {"label": "auth.log",
             "code": "Nov 20 02:58:11 web01 sshd[2211]: Failed password for invalid user admin from 45.155.205.233 port 51234 ssh2\n"
                     "Nov 20 02:58:12 web01 sshd[2213]: Failed password for invalid user root from 45.155.205.233 port 51240 ssh2\n"
                     "Nov 20 02:58:14 web01 sshd[2216]: Failed password for invalid user test from 45.155.205.233 port 51251 ssh2\n"
                     "Nov 20 02:58:19 web01 sshd[2221]: Failed password for deploy from 45.155.205.233 port 51266 ssh2\n"
                     "Nov 20 02:58:26 web01 sshd[2229]: Failed password for deploy from 45.155.205.233 port 51274 ssh2\n"
                     "Nov 20 02:58:41 web01 sshd[2402]: Accepted password for deploy from 45.155.205.233 port 51402 ssh2\n"
                     "Nov 20 02:58:41 web01 sshd[2402]: pam_unix(sshd:session): session opened for user deploy by (uid=0)"},
        ],
        "prompt": "가장 먼저 내려야 할 판단은?",
        "hints": ["실패 줄만 보지 말고, 마지막 두 줄에서 상태가 바뀐 지점을 찾으세요.", "Accepted password for deploy 가 같은 IP에서 나왔습니다. 실패 직후 성공은 침해로 다룹니다."],
        "choices": [
            "무차별 대입 끝에 deploy 계정 로그인에 성공했다 — 세션 종료·비밀번호 교체·키 전환·해당 IP 차단이 필요하다",
            "실패만 반복된 단순 오타이므로 조치가 필요 없다",
            "sshd 버전이 노출된 것뿐이라 배너만 숨기면 된다",
            "invalid user는 시스템에 없는 계정이라 위험이 없다",
        ],
        "answer": 0,
        "explain": {
            "principle": "여러 계정명을 빠르게 시도하는 invalid user 반복은 사전 대입입니다. 같은 IP에서 Accepted password가 나왔다면 그 시점 이후는 사고로 다뤄야 합니다. 성공 로그인 이후의 명령 이력, 새 계정 생성, authorized_keys 변경, 외부 전송을 함께 확인합니다.",
            "impact": "서버 장악, 내부 이동, 랜섬웨어 배포의 시작점입니다. 키 기반 인증만 허용하고 비밀번호 인증을 끄며, fail2ban과 인터넷 노출 최소화를 적용합니다.",
            "vuln": "# /etc/ssh/sshd_config\nPasswordAuthentication yes\nPermitRootLogin yes",
            "secure": "# /etc/ssh/sshd_config\nPasswordAuthentication no\nPermitRootLogin no\nMaxAuthTries 3",
        },
    },
    {
        "id": "log-04", "cat": "log", "level": "adv", "type": "choice",
        "title": "업로드 8초 뒤에 실행된 data 디렉터리의 PHP",
        "brief": "게시판 서버에서 같은 IP가 남긴 세 줄입니다.",
        "blocks": [
            {"label": "Apache access.log",
             "code": '10.0.4.12 - - [20/Nov/2026:04:02:11 +0900] "POST /bbs/file_upload.php HTTP/1.1" 200 421 "-" "Mozilla/5.0"\n'
                     '10.0.4.12 - - [20/Nov/2026:04:02:19 +0900] "GET /bbs/data/6f1c.php?c=id;uname+-a HTTP/1.1" 200 1294 "-" "Mozilla/5.0"\n'
                     '10.0.4.12 - - [20/Nov/2026:04:03:02 +0900] "GET /bbs/data/6f1c.php?c=cat+/etc/passwd HTTP/1.1" 200 3311 "-" "Mozilla/5.0"'},
        ],
        "prompt": "세 줄이 함께 보여 주는 침해 단계로 가장 정확한 것은?",
        "hints": ["세 줄의 순서(업로드 → 실행 → 파일 읽기)와 c 파라미터를 눈여겨보세요.", "업로드 경로의 php 파일이 OS 명령을 실행하고 결과를 돌려준 흐름입니다. 웹쉘입니다."],
        "choices": [
            "업로드로 웹쉘을 적재하고 c 파라미터로 명령을 실행했다 — 업로드 확장자·실행 권한 검증과 해당 파일 격리가 필요하다",
            "정상적인 파일 다운로드와 게시판 조회이다",
            "SQL Injection으로 DB를 덤프한 뒤 게시물을 읽었다",
            "백업 스크립트가 주기적으로 실행된 기록이다",
        ],
        "answer": 0,
        "explain": {
            "principle": "업로드 직후 업로드 경로의 PHP 파일에 c 파라미터로 OS 명령(id, uname -a, cat /etc/passwd)을 넘기고 응답 본문에 결과가 돌아온 흐름입니다. 웹 루트에 실행 가능한 확장자로 저장된 것이 근본 원인입니다.",
            "impact": "웹 서버 권한의 원격 명령 실행에서 내부 정찰과 권한 상승으로 이어집니다. 업로드는 웹 루트 밖에 저장하고 확장자·MIME·매직바이트를 검증하며 업로드 경로의 스크립트 실행을 막아야 합니다. 이미 적재된 파일은 삭제 전에 해시와 사본을 보존합니다.",
            "vuln": 'move_uploaded_file($_FILES["f"]["tmp_name"], "/var/www/bbs/data/" . $_FILES["f"]["name"]);',
            "secure": '$name = bin2hex(random_bytes(16)) . ".bin";\n'
                      'move_uploaded_file($_FILES["f"]["tmp_name"], "/var/uploads/" . $name);\n'
                      "# /var/uploads 는 웹 루트 밖 + location 에서 php 실행 차단",
        },
    },
    {
        "id": "log-05", "cat": "log", "level": "adv", "type": "input",
        "title": "403이 급증한 IP의 User-Agent",
        "brief": "같은 시간대 403·500이 급증한 IP의 요청입니다. 모두 같은 User-Agent를 달고 있습니다.",
        "blocks": [
            {"label": "Nginx access.log",
             "code": '45.9.148.12 - - [20/Nov/2026:03:44:02 +0900] "GET /admin/ HTTP/1.1" 403 162 "-" "sqlmap/1.8.2#stable (https://sqlmap.org)"\n'
                     '45.9.148.12 - - [20/Nov/2026:03:44:05 +0900] "GET /api/users?id=1 HTTP/1.1" 500 1294 "-" "sqlmap/1.8.2#stable (https://sqlmap.org)"\n'
                     '45.9.148.12 - - [20/Nov/2026:03:44:11 +0900] "GET /.git/config HTTP/1.1" 403 162 "-" "sqlmap/1.8.2#stable (https://sqlmap.org)"'},
        ],
        "prompt": "User-Agent에 드러난 자동화 도구 이름을 입력하세요. (소문자)",
        "patterns": [r"^sqlmap$", r"^sqlmap/[0-9.]+$"],
        "placeholder": "도구 이름 입력",
        "sample": "sqlmap",
        "chips": ["sqlmap", "nmap", "nikto"],
        "hints": [
            "User-Agent 마지막 부분을 보세요. 브라우저가 아닌 도구 이름이 그대로 적혀 있습니다.",
            "`sqlmap`입니다. 다만 UA는 위조할 수 있으므로 차단 근거로만 쓰고, 요청 패턴·속도·경로 분포를 함께 봐야 합니다.",
        ],
        "explain": {
            "principle": "정상 브라우저 UA는 Mozilla/5.0 ... 형태입니다. 도구 UA가 그대로 남는 경우도 있지만 공격자는 UA를 바꿀 수 있으므로 UA 차단은 보조 수단입니다. 짧은 시간에 403·404·500이 섞이고 /.git/config, /admin 같은 경로를 훑는 패턴이 더 신뢰할 만한 신호입니다.",
            "impact": "자동 스캔 단계에서 취약점이 확인되면 곧 집중 공격이 옵니다. WAF 룰과 레이트리밋, 노출 경로 제거(.git, 백업 파일, 관리자 경로)를 함께 적용합니다.",
            "vuln": "location / { try_files $uri $uri/ =404; }   # /.git/config 를 그대로 서빙",
            "secure": "location ~ /\\.(git|env) { deny all; }\nlimit_req zone=api burst=20 nodelay;",
        },
    },

    # --------------------------------------------------------- 시스템·권한 상승
    {
        "id": "sys-01", "cat": "sys", "level": "basic", "type": "choice",
        "title": "비밀번호 없이 모든 명령을 허용한 sudo 설정",
        "brief": "신규 서버의 sudo 설정을 점검합니다.",
        "blocks": [
            {"label": "/etc/sudoers.d/deploy",
             "code": "deploy ALL=(ALL) NOPASSWD: ALL"},
            {"label": "deploy 계정에서 확인",
             "code": "deploy@web01:~$ sudo -l\n"
                     "User deploy may run the following commands on web01:\n"
                     "    (ALL : ALL) NOPASSWD: ALL"},
        ],
        "prompt": "이 설정의 위험으로 가장 정확한 것은?",
        "hints": ["(ALL:ALL)과 NOPASSWD: 가 각각 무엇을 허용하는지 나눠서 읽어 보세요.", "모든 명령을 비밀번호 없이 root로 실행할 수 있다는 뜻입니다. 계정 하나가 뚫리면 서버 전체가 넘어갑니다."],
        "choices": [
            "비밀번호 없이 root 권한 전체를 얻을 수 있다 — 계정 하나가 뚫리면 곧 서버 전체가 넘어간다",
            "sudo 로그가 남지 않아 감사만 불가능해진다",
            "deploy가 다른 사용자의 홈 디렉터리만 읽을 수 있다",
            "sudo 버전이 낮아 명령 별칭이 무시된다",
        ],
        "answer": 0,
        "explain": {
            "principle": "(ALL:ALL) NOPASSWD: ALL은 모든 사용자·그룹 권한으로 모든 명령을 비밀번호 없이 실행한다는 뜻입니다. 웹쉘, SSH 키 유출, 애플리케이션 취약점으로 deploy 권한만 얻어도 sudo su - 한 줄로 root가 됩니다.",
            "impact": "권한 상승 경로가 즉시 열립니다. 필요한 명령만 화이트리스트로 허용하고, 허용한 명령도 인자를 우회할 수 있는지(예: 편집기를 여는 명령) 확인해야 합니다.",
            "vuln": "deploy ALL=(ALL) NOPASSWD: ALL",
            "secure": "deploy ALL=(root) NOPASSWD: /bin/systemctl restart app, /usr/bin/journalctl -u app",
        },
    },
    {
        "id": "sys-02", "cat": "sys", "level": "mid", "type": "input",
        "title": "SUID 목록에 섞여 있던 기본값 아닌 바이너리",
        "brief": "서버에서 SUID가 설정된 root 소유 파일을 모두 찾았습니다. 원래 SUID가 아니어야 할 바이너리가 하나 있습니다.",
        "blocks": [
            {"label": "find / -perm -4000 -type f -ls",
             "code": "-rwsr-xr-x 1 root root 68208 Nov 10 09:12 /usr/bin/passwd\n"
                     "-rwsr-xr-x 1 root root 31328 Nov 10 09:12 /usr/bin/su\n"
                     "-rwsr-xr-x 1 root root 39112 Nov 10 09:12 /usr/bin/find\n"
                     "-rwsr-xr-x 1 root root 31032 Nov 10 09:12 /usr/bin/newgrp"},
        ],
        "prompt": "공격자가 -exec로 임의 명령을 root 권한으로 실행할 수 있는 파일 이름만 입력하세요.",
        "patterns": [r"^find$", r"^/usr/bin/find$"],
        "placeholder": "파일 이름 입력",
        "sample": "find",
        "chips": ["passwd", "su", "find", "newgrp"],
        "hints": [
            "세 개는 원래 SUID가 정상인 기본 바이너리입니다. 하나는 원래 SUID가 아니어야 합니다.",
            "find는 -exec로 명령을 실행합니다. root SUID로 걸리면 `find / -exec /bin/sh -p`로 root 셸을 얻습니다. 정답은 find입니다.",
        ],
        "explain": {
            "principle": "SUID가 붙은 실행 파일은 실행한 사용자 대신 파일 소유자(root) 권한으로 동작합니다. find는 -exec로 임의 명령을 실행하는 기능이 있어 SUID root로 설정되면 그 자체가 권한 상승 도구가 됩니다. vim, tar, nmap, cp도 같은 이유로 위험합니다.",
            "impact": "로컬 사용자에서 root로 올라섭니다. find / -perm -4000을 주기적으로 돌려 기본값과 비교하고, 다른 항목은 chmod u-s로 제거한 뒤 필요 여부를 확인합니다.",
            "vuln": "chmod u+s /usr/bin/find     # 원래 SUID가 아니어야 할 바이너리",
            "secure": "find / -xdev -perm -4000 -type f -ls | sort   # 주기 점검·기본값 대조\nchmod u-s /usr/bin/find",
        },
    },
    {
        "id": "sys-03", "cat": "sys", "level": "mid", "type": "choice",
        "title": "매분 root가 실행하는 쓰기 가능한 스크립트",
        "brief": "root의 cron이 매분 실행하는 백업 스크립트의 권한을 확인했습니다.",
        "blocks": [
            {"label": "crontab -l (root)",
             "code": "* * * * * /opt/backup/run_backup.sh >> /var/log/backup.log 2>&1"},
            {"label": "권한",
             "code": "$ ls -l /opt/backup/run_backup.sh\n"
                     "-rwxrwxrwx 1 root root 214 Nov 20 04:10 /opt/backup/run_backup.sh\n"
                     "$ ls -ld /opt/backup\n"
                     "drwxrwxr-x 2 root dev 4096 Nov 20 04:10 /opt/backup"},
        ],
        "prompt": "이 설정이 허용하는 권한 상승 경로는?",
        "hints": ["root가 실행하는 파일에 다른 사용자가 쓸 수 있는 권한이 있는지 보세요. 파일과 디렉터리 둘 다요.", "777 스크립트와 그룹 쓰기 가능 디렉터리 조합은 다음 실행에서 root 권한 코드 실행으로 이어집니다."],
        "choices": [
            "dev 그룹 구성원이 스크립트를 고쳐 root 권한으로 임의 코드를 실행할 수 있다",
            "cron 로그가 무한히 커져 디스크가 가득 찬다",
            "백업이 매분 실행되어 성능만 저하된다",
            "root만 실행하므로 위험이 없다",
        ],
        "answer": 0,
        "explain": {
            "principle": "root cron이 실행하는 파일에 다른 사용자가 쓸 수 있는 권한(777)이 있거나, 디렉터리가 775여서 파일을 바꿔치기할 수 있으면 다음 실행에서 root로 코드가 돌아갑니다. cron은 상대 경로와 환경변수도 함께 위험 요소입니다.",
            "impact": "로컬 그룹 사용자에서 root로 올라섭니다. root 소유 파일은 755, 실행 디렉터리는 700으로 두고 쓰기 권한을 분리합니다.",
            "vuln": "chmod 777 /opt/backup/run_backup.sh\nchgrp dev /opt/backup && chmod 775 /opt/backup",
            "secure": "chown root:root /opt/backup/run_backup.sh && chmod 755 /opt/backup/run_backup.sh\nchown root:root /opt/backup && chmod 700 /opt/backup",
        },
    },
    {
        "id": "sys-04", "cat": "sys", "level": "adv", "type": "choice",
        "title": "PATH 맨 앞에 놓인 사용자 홈 디렉터리",
        "brief": "root cron이 실행하는 야간 백업 스크립트입니다. 스크립트가 PATH를 직접 지정합니다.",
        "blocks": [
            {"label": "/opt/backup/nightly.sh (root cron)",
             "code": "#!/bin/sh\n"
                     "PATH=/home/deploy/bin:/usr/local/bin:/usr/bin:/bin\n"
                     "cd /var/backups\n"
                     "tar czf db-$(date +%F).tgz /var/lib/mysql"},
            {"label": "디렉터리 권한",
             "code": "$ ls -ld /home/deploy/bin\n"
                     "drwxrwxr-x 2 deploy deploy 4096 Nov 20 04:20 /home/deploy/bin"},
        ],
        "prompt": "deploy 계정으로 이 서버의 root 권한을 얻는 가장 직접적인 방법은?",
        "hints": ["스크립트가 tar를 이름만으로 부르면 셸은 어디서 찾을까요? PATH 순서를 보세요.", "PATH 맨 앞이 deploy 소유 디렉터리입니다. 같은 이름의 파일을 심으면 root cron이 그것을 실행합니다."],
        "choices": [
            "/home/deploy/bin/tar에 악성 스크립트를 만들면 root cron이 그것을 먼저 실행한다 (PATH 하이재킹)",
            "/var/backups에 심볼릭 링크를 걸어 백업 파일을 읽는다",
            "cron 로그에서 root 비밀번호를 찾아낸다",
            "tar 버전의 취약점을 스캔해 원격에서 공격한다",
        ],
        "answer": 0,
        "explain": {
            "principle": "스크립트가 tar를 이름만으로 부르면 셸은 PATH 순서대로 찾습니다. PATH 맨 앞이 사용자가 쓸 수 있는 디렉터리면 같은 이름의 파일이 먼저 실행됩니다. $(date +%F) 같은 명령 치환도 같은 규칙을 따릅니다.",
            "impact": "root 권한 실행입니다. root 스크립트에서는 PATH를 고정하고 모든 명령을 절대 경로로 쓰며 사용자 홈을 PATH에 넣지 않습니다. sudo가 -p로 기존 환경을 물려받는 설정도 함께 점검합니다.",
            "vuln": "PATH=/home/deploy/bin:/usr/local/bin:/usr/bin:/bin\ntar czf db.tgz /var/lib/mysql",
            "secure": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
                      "/usr/bin/tar -czf /var/backups/db.tgz /var/lib/mysql",
        },
    },
    {
        "id": "sys-05", "cat": "sys", "level": "basic", "type": "choice",
        "title": "오류 화면에 그대로 찍힌 키와 DB 비밀번호",
        "brief": "결제 API가 예외를 만나 사용자 화면에 아래 내용을 출력했습니다.",
        "blocks": [
            {"label": "브라우저에 표시된 500 오류",
             "code": "Traceback (most recent call last):\n"
                     '  File "/app/pay.py", line 88, in charge\n'
                     "KeyError: 'amount'\n"
                     "DEBUG=True\n"
                     "DB_URL=postgres://pay_app:Passw0rd!23@10.0.4.21:5432/pay\n"
                     "EXAONE_API_KEY=exaone_sk_9f2...c41\n"
                     "AWS_SECRET_ACCESS_KEY=wJalr..."},
        ],
        "prompt": "이 화면이 실제로 만드는 가장 큰 위험은?",
        "hints": ["화면에 무엇이 찍혔는지 하나씩 보세요. 오류 위치보다 민감한 값이 있나요?", "DB 접속 문자열과 클라우드 키가 그대로 노출됩니다. 디버그 모드를 끄고 자격증명을 교체해야 합니다."],
        "choices": [
            "DB·클라우드 자격증명 노출로 서버 권한과 데이터가 그대로 넘어간다 — 디버그 모드를 끄고 비밀값을 분리한 뒤 즉시 교체한다",
            "오류 위치가 드러나 코드 구조를 알 수 있다 정도다",
            "API 키는 무료라서 큰 문제가 아니다",
            "HTTPS라서 화면 내용은 외부에 노출되지 않는다",
        ],
        "answer": 0,
        "explain": {
            "principle": "디버그 오류 화면은 스택 트레이스와 환경변수를 함께 출력합니다. 키와 DB 비밀번호가 화면에 나오면 로그·스크린샷·프록시 캐시에 남고, 노출된 값으로 바로 접속을 시도할 수 있습니다. HTTPS는 전송 구간만 보호하며 서버가 그리는 화면 내용은 막지 못합니다.",
            "impact": "DB 직접 접속, 클라우드 리소스 탈취, 외부 API 과금입니다. 노출된 자격증명은 이미 유출된 것으로 보고 교체·감사하며, 사용자에게는 요청 ID만 보여 주고 상세는 서버 로그에 남깁니다.",
            "vuln": 'app.config["DEBUG"] = True\napp.config["PROPAGATE_EXCEPTIONS"] = True',
            "secure": 'app.config["DEBUG"] = False\n'
                      '@app.errorhandler(500)\n'
                      'def on_500(e):\n'
                      '    rid = uuid.uuid4().hex\n'
                      '    log.exception("internal error rid=%s", rid)\n'
                      '    return jsonify({"error": "요청을 처리하지 못했습니다", "rid": rid}), 500',
        },
    },

    # ------------------------------------------------------------ 네트워크·패킷
    {
        "id": "net-01", "cat": "net", "level": "basic", "type": "choice",
        "title": "22, 23, 25번 포트로 이어진 SYN과 RST",
        "brief": "한 외부 IP가 40초 동안 남긴 패킷 요약입니다.",
        "blocks": [
            {"label": "tcpdump 요약",
             "code": "04:11:02.118 IP 203.0.113.77.54812 > 10.0.4.21.22: Flags [S], seq 0, win 64240, length 0\n"
                     "04:11:02.121 IP 10.0.4.21.22 > 203.0.113.77.54812: Flags [R.], seq 0, ack 1, length 0\n"
                     "04:11:02.140 IP 203.0.113.77.54813 > 10.0.4.21.23: Flags [S], seq 0, win 64240, length 0\n"
                     "04:11:02.143 IP 10.0.4.21.23 > 203.0.113.77.54813: Flags [R.], seq 0, ack 1, length 0\n"
                     "04:11:02.162 IP 203.0.113.77.54814 > 10.0.4.21.25: Flags [S], seq 0, win 64240, length 0\n"
                     "04:11:02.165 IP 10.0.4.21.25 > 203.0.113.77.54814: Flags [R.], seq 0, ack 1, length 0"},
        ],
        "prompt": "이 트래픽의 성격은?",
        "hints": ["목적지 포트가 어떻게 움직이는지, SYN에 대한 응답이 ACK인지 RST인지 보세요.", "닫힌 포트는 RST로 응답합니다. 여러 포트를 훑는 SYN은 포트 스캔입니다."],
        "choices": [
            "포트 스캔 — 여러 포트에 SYN만 보내고 RST 응답으로 열린 포트를 가려내는 정찰",
            "정상적인 SMTP 메일 발송",
            "SYN Flood — 다량의 SYN으로 서버 자원을 고갈시키는 공격",
            "DNS 질의 폭주",
        ],
        "answer": 0,
        "explain": {
            "principle": "SYN만 보내고 핸드셰이크를 완성하지 않으며 목적지 포트가 22, 23, 25로 연속 이동합니다. RST 응답은 닫힌 포트를 뜻하고, SYN/ACK 또는 무응답으로 열린 포트를 구분합니다. 같은 출발지가 짧은 시간에 여러 포트를 훑으면 스캔입니다.",
            "impact": "열린 포트 목록이 다음 공격의 지도가 됩니다. 기본 차단 정책과 불필요 포트 제거, 스캔 탐지 룰로 대응하고 스캔 이후 같은 IP의 연결 시도를 함께 추적합니다.",
            "vuln": "# 인터넷에 그대로 노출된 관리 포트\n-A INPUT -p tcp --dport 22 -j ACCEPT\n-A INPUT -p tcp --dport 3306 -j ACCEPT",
            "secure": "-A INPUT -p tcp --dport 22 -s 10.0.0.0/8 -j ACCEPT\n-A INPUT -p tcp --dport 22 -j DROP\n# 3306 은 외부 노출 금지 (로컬·VPN 전용)",
        },
    },
    {
        "id": "net-02", "cat": "net", "level": "mid", "type": "input",
        "title": "끝없이 바뀌는 서브도메인, 변하지 않는 목적지",
        "brief": "내부 DNS 로그에서 같은 도메인으로 비정상적으로 많은 TXT·A 질의가 나갑니다.",
        "blocks": [
            {"label": "query.log",
             "code": "04:22:01 query: aGVsbG8td29ybGQ.exfil.example.com TXT\n"
                     "04:22:02 query: c2VjcmV0LWtleQ.exfil.example.com TXT\n"
                     "04:22:03 query: MQoyMDI2LTExLTIw.exfil.example.com TXT\n"
                     "04:22:04 query: dXNlcjpQYXNzdzByZA.exfil.example.com A\n"
                     "04:22:05 query: L2V0Yy9wYXNzd2Q.exfil.example.com A"},
        ],
        "prompt": "데이터가 실려 나가는 도메인을 입력하세요. (바뀌지 않는 부분만)",
        "patterns": [r"^exfil[.]example[.]com[.]?$"],
        "placeholder": "도메인 입력",
        "sample": "exfil.example.com",
        "chips": ["exfil.example.com", "example.com", "TXT"],
        "hints": [
            "질의마다 바뀌는 앞부분은 Base64로 인코딩된 데이터처럼 보입니다. 변하지 않는 부분이 터널의 목적지입니다.",
            "답은 `exfil.example.com`입니다. 서브도메인에 인코딩한 데이터를 실어 DNS 질의로 외부에 내보내는 DNS 터널링입니다.",
        ],
        "explain": {
            "principle": "DNS는 거의 모든 네트워크에서 허용되므로 서브도메인 문자열에 데이터를 나눠 담아 질의하면 방화벽을 통과해 유출과 명령 제어가 가능합니다. Base64·hex로 보이는 앞부분, 높은 질의량, 긴 서브도메인, TXT 질의 집중이 특징입니다.",
            "impact": "데이터 유출과 원격 제어입니다. 내부 리졸버에서 임의 외부 도메인 질의를 차단하고, 질의 길이·응답 크기·빈도 기반 탐지를 붙이며, 해당 호스트의 프로세스를 확인합니다.",
            "vuln": "# 내부 호스트가 임의 외부 도메인으로 직접 질의\nnameserver 8.8.8.8",
            "secure": "# 내부 리졸버만 사용하고 허용 도메인 외 질의는 차단·기록\nnameserver 10.0.0.53\n# 리졸버에서 RPZ·허용목록 + 긴 서브도메인·TXT 과다 질의 탐지",
        },
    },
    {
        "id": "net-03", "cat": "net", "level": "mid", "type": "choice",
        "title": "127.0.0.1을 적어 넣어 통과한 관리자 페이지",
        "brief": "관리자 페이지가 요청 헤더를 보고 내부 접속인지 판단합니다.",
        "blocks": [
            {"label": "HTTP · 외부에서 보낸 요청",
             "code": "GET /admin/users HTTP/1.1\n"
                     "Host: ops.example.com\n"
                     "X-Forwarded-For: 127.0.0.1\n"
                     "Cookie: session=..."},
            {"label": "Nginx",
             "code": "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"},
            {"label": "Python · admin.py",
             "code": 'if request.headers.get("X-Forwarded-For", "").startswith("127."):\n'
                     "    return admin_page()      # 내부 요청으로 판단"},
        ],
        "prompt": "이 구성의 결함은?",
        "hints": ["이 헤더는 누가 만들 수 있나요? 프록시가 덧붙이는 값과 클라이언트가 보낸 값을 구분해 보세요.", "$proxy_add_x_forwarded_for 는 클라이언트 값을 앞에 남깁니다. 그래서 127.0.0.1 위조가 통과합니다."],
        "choices": [
            "클라이언트가 보낸 X-Forwarded-For를 그대로 신뢰해, 외부에서 내부 요청인 것처럼 위장할 수 있다",
            "관리자 페이지가 HTTPS가 아니라 세션이 노출된다",
            "쿠키에 SameSite가 없어 CSRF가 가능하다",
            "Nginx가 헤더를 추가하면 요청이 두 번 전송된다",
        ],
        "answer": 0,
        "explain": {
            "principle": "$proxy_add_x_forwarded_for는 기존 헤더 뒤에 클라이언트 IP를 덧붙입니다. 클라이언트가 X-Forwarded-For: 127.0.0.1을 보내면 그 값이 앞부분에 남고, 애플리케이션이 첫 값이나 startswith로 판단하면 위조가 통과합니다. 직전 프록시에서 헤더를 덮어쓰고 신뢰 경계 기준으로 실제 접속 IP를 판단해야 합니다.",
            "impact": "IP 기반 접근 제어가 우회되어 관리자 기능이 노출됩니다. 접근 제어는 애플리케이션이 아니라 네트워크·프록시 계층에서 하고, 감사 로그에는 신뢰한 IP를 남깁니다.",
            "vuln": "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
                    'if request.headers.get("X-Forwarded-For", "").startswith("127."): allow()',
            "secure": "proxy_set_header X-Forwarded-For $remote_addr;   # 클라이언트 값 무시\n"
                      "ip = request.access_route[-1]                    # 신뢰 프록시 기준 실제 IP\n"
                      "if ip in ADMIN_ALLOWLIST: allow()",
        },
    },
    {
        "id": "net-04", "cat": "net", "level": "adv", "type": "choice",
        "title": "verify=False로 열어 둔 결제 채널",
        "brief": "사내 결제 연동 코드입니다. HTTPS 주소를 쓰지만 인증서 검증을 끕니다.",
        "blocks": [
            {"label": "Python · pg_client.py",
             "code": "import requests, urllib3\n"
                     "urllib3.disable_warnings()\n"
                     "\n"
                     'resp = requests.post(\n'
                     '    "https://pg.partner.example/v1/charge",\n'
                     "    json=payload,\n"
                     "    verify=False,\n"
                     "    timeout=5,\n"
                     ")"},
        ],
        "prompt": "이 코드의 실질적 위험은?",
        "hints": ["HTTPS를 쓴다는 것과 상대 서버를 검증한다는 것은 다릅니다. verify=False 가 무엇을 끄는지 보세요.", "인증서 검증을 끄면 중간자가 위조 인증서로 통신을 가로챌 수 있습니다. CA 번들을 지정해 검증을 유지해야 합니다."],
        "choices": [
            "인증서 검증이 없어 중간자가 위조 인증서로 결제 요청과 응답을 가로채고 변조할 수 있다",
            "TLS 핸드셰이크가 느려져 성능만 떨어진다",
            "요청 본문이 압축되지 않아 대역폭이 늘어난다",
            "인증서가 만료되면 요청이 실패한다",
        ],
        "answer": 0,
        "explain": {
            "principle": "verify=False는 인증서 체인·호스트명·만료 검증을 모두 끕니다. HTTPS라는 이름은 남지만 상대가 진짜 그 서버인지 확인하지 않으므로 같은 네트워크의 공격자가 프록시를 세워 요청과 응답을 읽고 바꿀 수 있습니다. 사내 CA를 쓰더라도 검증을 끄는 대신 CA 번들을 지정해야 합니다.",
            "impact": "결제 금액·계좌·개인정보 변조와 세션 탈취입니다. CA 번들로 검증을 유지하고 인증서 피닝과 TLS 최소 버전 1.2 이상을 함께 적용합니다.",
            "vuln": "requests.post(url, json=payload, verify=False, timeout=5)",
            "secure": 'requests.post(url, json=payload,\n'
                      '              verify="/etc/ssl/certs/partner-ca.pem", timeout=5)',
        },
    },
]


# ---------------------------------------------------------------- 렌더 도우미
def _code_block(block):
    return ('<div class="code-block">'
            '<div class="code-head"><span class="code-label">%s</span>'
            '<span class="code-scroll-hint">옆으로 넘겨 보기</span></div>'
            '<div class="code-body"><pre>%s</pre></div>'
            '</div>' % (esc(block["label"]), esc(block["code"])))


def _daily_badges(q, today_str):
    """데일리 자동 출제 문제에만 붙는 배지 (오늘의 문제 / YYYY-MM-DD 추가)."""
    if not q.get("is_daily"):
        return ""
    created = q.get("created_date") or ""
    out = []
    if created == today_str:
        out.append('<span class="q-badge q-badge-today">오늘의 문제</span>')
    if created:
        out.append('<span class="q-badge q-badge-date">%s 추가</span>' % esc(created))
    return "".join(out)


def _render_static(q, no=1, today_str=""):
    """서버 측에서 미리 그려 두는 카드 골격(문제·코드·보기). 채점은 JS가 한다."""
    cat = next(c["label"] for c in CATS if c["key"] == q["cat"])
    lv = next(l["label"] for l in LEVELS if l["key"] == q["level"])
    blocks = "".join(_code_block(b) for b in q.get("blocks", []))
    if q["type"] == "choice":
        body = "".join(
            '<button class="opt" type="button" data-idx="%d">'
            '<span class="opt-key">%s</span><span class="opt-text">%s</span>'
            '</button>' % (i, "ABCD"[i], esc(text))
            for i, text in enumerate(q["choices"])
        )
        body = '<div class="options">%s</div>' % body
        type_label = "4지선다"
    else:
        chips = "".join(
            '<button class="chip chip-input" type="button" data-chip="%s">%s</button>'
            % (esc(c), esc(c)) for c in q.get("chips", [])
        )
        body = ('<form class="answer-form" autocomplete="off">'
                '<input class="answer-input" type="text" name="answer" placeholder="%s" '
                'autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" '
                'enterkeyhint="done" aria-label="정답 입력">'
                '<button class="btn-primary" type="submit">확인</button>'
                '</form>'
                '<div class="quick-chips">%s</div>') % (esc(q.get("placeholder", "정답 입력")), chips)
        type_label = "실습형"
    return (
        '<article class="q-card" id="q-%(id)s" data-id="%(id)s" data-cat="%(cat)s" '
        'data-level="%(level)s" data-type="%(type)s">'
        '<div class="q-top">'
        '<span class="q-no">%(no)s</span>'
        '<span class="q-cat cat-%(cat)s">%(catlabel)s</span>'
        '<span class="lv lv-%(level)s">%(lv)s</span>'
        '<span class="q-type">%(typelabel)s</span>'
        '%(badge)s'
        '<span class="q-state" hidden>해결</span>'
        '</div>'
        '<h2 class="q-title">%(title)s</h2>'
        '<p class="q-brief">%(brief)s</p>'
        '<div class="q-blocks">%(blocks)s</div>'
        '<p class="q-prompt">%(prompt)s</p>'
        '<div class="q-body">%(body)s</div>'
        '<div class="q-foot">'
        '<button class="btn-ghost" type="button" data-act="hint">힌트 보기</button>'
        '<button class="btn-ghost btn-reveal" type="button" data-act="reveal" hidden>정답 보기</button>'
        '<span class="q-tries" hidden></span>'
        '</div>'
        '<div class="hint-box" hidden><div class="hint-label">힌트</div><ol class="hint-list"></ol></div>'
        '<div class="q-feedback" hidden></div>'
        '<div class="q-explain" hidden>'
        '<div class="explain-head">해설 · 공격 원리와 대응</div>'
        '<div class="explain-grid">'
        '<div class="explain-col"><h4>공격 원리</h4><p>%(principle)s</p></div>'
        '<div class="explain-col"><h4>실무 영향</h4><p>%(impact)s</p></div>'
        '</div>'
        '<div class="code-compare">'
        '<div class="cmp cmp-vuln"><div class="cmp-head">Vulnerable Code</div>'
        '<div class="code-body"><pre>%(vuln)s</pre></div></div>'
        '<div class="cmp cmp-secure"><div class="cmp-head">Secure Code</div>'
        '<div class="code-body"><pre>%(secure)s</pre></div></div>'
        '</div>'
        '</div>'
        '</article>'
    ) % {
        "id": esc(q["id"]), "cat": q["cat"], "level": q["level"], "type": q["type"],
        "no": "%02d" % no,
        "badge": _daily_badges(q, today_str),
        "catlabel": esc(cat), "lv": esc(lv), "typelabel": type_label,
        "title": esc(q["title"]), "brief": esc(q["brief"]), "blocks": blocks,
        "prompt": esc(q["prompt"]), "body": body,
        "hints": ["HTTPS를 쓴다는 것과 상대 서버를 검증한다는 것은 다릅니다. verify=False 가 무엇을 끄는지 보세요.", "인증서 검증을 끄면 중간자가 위조 인증서로 통신을 가로챌 수 있습니다. CA 번들을 지정해 검증을 유지해야 합니다."],
        "principle": esc(q["explain"]["principle"]), "impact": esc(q["explain"]["impact"]),
        "vuln": esc(q["explain"]["vuln"]), "secure": esc(q["explain"]["secure"]),
    }


# ---------------------------------------------------------------- CSS
CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --font-mono: "SFMono-Regular", ui-monospace, "JetBrains Mono", Menlo, Consolas, monospace;

      --bg-page: #f8fafc;
      --bg-surface: #ffffff;
      --bg-subtle: #f1f5f9;
      --bg-muted: #e2e8f0;

      --border-subtle: #f1f5f9;
      --border-default: #e2e8f0;
      --border-strong: #cbd5e1;

      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;

      --accent-primary: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;

      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --code-bg: #101828;
      --code-head: #1d2939;
      --code-text: #e4e7ec;
      --code-muted: #98a2b3;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
    }

    [data-theme="dark"] {
      --bg-page: #09090b;
      --bg-surface: #18181b;
      --bg-subtle: #27272a;
      --bg-muted: #3f3f46;

      --border-subtle: #1f1f23;
      --border-default: #27272a;
      --border-strong: #3f3f46;

      --text-primary: #f4f4f5;
      --text-secondary: #a1a1aa;
      --text-muted: #71717a;

      --accent-primary: #3b82f6;
      --accent-hover: #60a5fa;
      --accent-subtle: rgba(59, 130, 246, 0.15);

      --ok-bg: rgba(16, 185, 129, 0.12);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.32);
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);

      --code-bg: #0b0f16;
      --code-head: #151b25;
      --code-text: #e4e7ec;
      --code-muted: #98a2b3;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    html { scroll-behavior: smooth; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-page);
      color: var(--text-primary);
      line-height: 1.5;
      letter-spacing: -0.02em;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    a { color: inherit; }

    /* Global Header (index.html / study.html / ai.html / cve.html / outfit.html 과 동일) */
    .navbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    .nav-container {
      max-width: 1140px;
      margin: 0 auto;
      padding: 0 20px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }

    .brand-logo-img {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      object-fit: cover;
      display: block;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
      flex-shrink: 0;
    }

    .brand-name {
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      white-space: nowrap;
    }

    .nav-tabs { display: flex; gap: 6px; margin-left: 10px; }

    .nav-tab-item {
      padding: 5px 12px;
      border-radius: 18px;
      font-size: 12.5px;
      font-weight: 600;
      text-decoration: none;
      color: var(--text-secondary);
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .nav-tab-item:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .nav-tab-item.active { background: var(--accent-primary); color: #ffffff !important; }

    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .update-meta {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
      white-space: nowrap;
    }

    .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      flex-shrink: 0;
    }

    .icon-btn {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
      text-decoration: none;
    }

    .icon-btn:hover {
      background: var(--bg-subtle);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }

    /* Layout */
    .container { max-width: 860px; margin: 0 auto; padding: 32px 20px 80px; }

    .hero { margin-bottom: 18px; }

    .hero-pill {
      display: inline-block;
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 9px;
      margin-bottom: 12px;
    }

    .hero-title {
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.03em;
      margin-bottom: 8px;
    }

    .hero-desc {
      font-size: 14.5px;
      color: var(--text-secondary);
      line-height: 1.65;
      margin-bottom: 14px;
      max-width: 720px;
    }

    .hero-stats { display: flex; flex-wrap: wrap; gap: 8px; }

    .stat-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .stat-chip strong { color: var(--text-primary); font-weight: 600; }

    /* 진행 현황 */
    .summary {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      padding: 16px 18px;
      margin-bottom: 14px;
      display: grid;
      grid-template-columns: minmax(0, auto) minmax(0, 1fr);
      gap: 18px;
      align-items: center;
    }

    .sum-main { min-width: 0; }

    .sum-num {
      display: flex;
      align-items: baseline;
      gap: 4px;
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.04em;
    }

    .sum-num strong { font-size: 30px; font-weight: 700; line-height: 1.1; }

    .sum-num span { font-size: 14px; color: var(--text-muted); font-weight: 600; }

    .sum-label { font-size: 11.5px; color: var(--text-muted); margin-top: 2px; }

    .sum-bar {
      height: 5px;
      border-radius: 3px;
      background: var(--bg-muted);
      overflow: hidden;
      margin-top: 8px;
    }

    .sum-bar > i {
      display: block;
      height: 100%;
      width: 0%;
      border-radius: 3px;
      background: var(--accent-primary);
      transition: width 0.3s ease;
    }

    .sum-side { min-width: 0; }

    .sum-rows {
      display: flex;
      align-items: baseline;
      gap: 14px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }

    .sum-row { font-size: 12px; color: var(--text-muted); }
    .sum-row strong { color: var(--text-primary); font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }

    .cat-progress { display: flex; flex-wrap: wrap; gap: 6px; }

    .cat-bar {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 8px;
      background: var(--bg-page);
      white-space: nowrap;
    }

    .cat-bar b { font-weight: 600; color: var(--text-primary); font-variant-numeric: tabular-nums; }

    .cat-bar i {
      display: block;
      width: 26px;
      height: 3px;
      border-radius: 2px;
      background: var(--bg-muted);
      overflow: hidden;
    }

    .cat-bar i > s { display: block; height: 100%; width: 0%; background: var(--accent-primary); text-decoration: none; }

    /* 필터 */
    .controls {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      padding: 15px 18px;
      margin-bottom: 18px;
    }

    .filter-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 9px; }
    .filter-row:last-of-type { margin-bottom: 0; }

    .filter-label {
      flex: 0 0 46px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--text-muted);
      padding-top: 6px;
    }

    .chips { display: flex; flex-wrap: wrap; gap: 5px; min-width: 0; }

    .chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: -0.02em;
      padding: 5px 11px;
      border-radius: 16px;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .chip:hover { border-color: var(--border-strong); color: var(--text-primary); }

    .chip.active {
      background: var(--text-primary);
      border-color: var(--text-primary);
      color: var(--bg-surface);
    }

    .chip em {
      font-style: normal;
      font-size: 10.5px;
      font-variant-numeric: tabular-nums;
      opacity: 0.62;
    }

    .controls-foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-top: 12px;
      padding-top: 11px;
      border-top: 1px solid var(--border-subtle);
      flex-wrap: wrap;
    }

    .visible-count { font-size: 11.5px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    .foot-btns { display: flex; gap: 6px; }

    .btn-ghost {
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 11.5px;
      font-weight: 600;
      padding: 5px 11px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .btn-ghost:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }

    /* 문제 카드 */
    .q-list { display: flex; flex-direction: column; gap: 12px; }

    .q-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      padding: 18px;
      min-width: 0;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .q-card:hover { box-shadow: var(--card-shadow-hover); }

    .q-card.is-solved { border-color: var(--ok-border); }

    .q-card.is-revealed { border-color: var(--border-strong); }

    .q-top {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
      margin-bottom: 9px;
    }

    .q-no {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      font-variant-numeric: tabular-nums;
      letter-spacing: 0;
      min-width: 18px;
    }

    .q-cat, .lv, .q-type, .q-state {
      font-size: 10.5px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 5px;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .q-cat.cat-web { color: #1d4ed8; border-color: #bfdbfe; background: #eff6ff; }
    .q-cat.cat-log { color: #b45309; border-color: #fde68a; background: #fffbeb; }
    .q-cat.cat-sys { color: #7e22ce; border-color: #e9d5ff; background: #faf5ff; }
    .q-cat.cat-net { color: #0f766e; border-color: #99f6e4; background: #f0fdfa; }

    [data-theme="dark"] .q-cat.cat-web { color: #93c5fd; border-color: rgba(59,130,246,0.35); background: rgba(59,130,246,0.12); }
    [data-theme="dark"] .q-cat.cat-log { color: #fcd34d; border-color: rgba(245,158,11,0.35); background: rgba(245,158,11,0.12); }
    [data-theme="dark"] .q-cat.cat-sys { color: #d8b4fe; border-color: rgba(168,85,247,0.35); background: rgba(168,85,247,0.12); }
    [data-theme="dark"] .q-cat.cat-net { color: #5eead4; border-color: rgba(20,184,166,0.35); background: rgba(20,184,166,0.12); }

    .lv-basic { color: var(--text-secondary); }
    .lv-mid { color: #b45309; border-color: #fde68a; background: #fffbeb; }
    .lv-adv { color: #b91c1c; border-color: #fecaca; background: #fef2f2; }

    [data-theme="dark"] .lv-mid { color: #fcd34d; border-color: rgba(245,158,11,0.35); background: rgba(245,158,11,0.12); }
    [data-theme="dark"] .lv-adv { color: #fca5a5; border-color: rgba(239,68,68,0.35); background: rgba(239,68,68,0.12); }

    .q-state {
      margin-left: auto;
      color: var(--ok-text);
      border-color: var(--ok-border);
      background: var(--ok-bg);
    }

    .q-badge {
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 5px;
      white-space: nowrap;
      letter-spacing: -0.01em;
      font-variant-numeric: tabular-nums;
    }

    .q-badge-today {
      color: #0f766e;
      border: 1px solid #99f6e4;
      background: #f0fdfa;
    }

    .q-badge-date {
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
      background: var(--bg-subtle);
    }

    [data-theme="dark"] .q-badge-today {
      color: #5eead4;
      border-color: rgba(20, 184, 166, 0.4);
      background: rgba(20, 184, 166, 0.12);
    }

    [data-theme="dark"] .q-badge-date {
      color: #cbd5e1;
      border-color: var(--border-default);
      background: var(--bg-subtle);
    }

    .q-title {
      font-size: 16.5px;
      font-weight: 700;
      letter-spacing: -0.03em;
      line-height: 1.4;
      margin-bottom: 5px;
    }

    .q-brief {
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.7;
      margin-bottom: 12px;
    }

    .q-blocks { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }

    /* 코드 뷰어 (블록 내부만 가로 스크롤) */
    .code-block {
      background: var(--code-bg);
      border-radius: 10px;
      overflow: hidden;
      min-width: 0;
    }

    .code-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 7px 12px;
      background: var(--code-head);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .code-label {
      font-family: var(--font-mono);
      font-size: 10.5px;
      color: var(--code-muted);
      letter-spacing: 0;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .code-scroll-hint {
      font-size: 9.5px;
      color: var(--code-muted);
      opacity: 0.55;
      flex-shrink: 0;
    }

    .code-body {
      overflow-x: auto;
      overflow-y: hidden;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: thin;
      max-width: 100%;
      min-width: 0;
    }

    .code-body::-webkit-scrollbar { height: 5px; }
    .code-body::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.18); border-radius: 3px; }

    .code-body pre {
      margin: 0;
      padding: 11px 12px;
      font-family: var(--font-mono);
      font-size: 11.8px;
      line-height: 1.68;
      color: var(--code-text);
      white-space: pre;
      tab-size: 2;
      letter-spacing: 0;
    }

    .q-prompt {
      font-size: 13.5px;
      font-weight: 600;
      line-height: 1.65;
      color: var(--text-primary);
      margin-bottom: 10px;
      padding-left: 10px;
      border-left: 2px solid var(--accent-primary);
    }

    .options { display: flex; flex-direction: column; gap: 6px; }

    .opt {
      display: flex;
      align-items: flex-start;
      gap: 9px;
      width: 100%;
      text-align: left;
      font-family: inherit;
      font-size: 13px;
      line-height: 1.6;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 10px 12px;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .opt:hover { border-color: var(--border-strong); background: var(--bg-surface); }

    .opt-key {
      flex-shrink: 0;
      width: 19px;
      height: 19px;
      border-radius: 5px;
      background: var(--bg-muted);
      color: var(--text-secondary);
      font-size: 10.5px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-top: 1px;
    }

    .opt-text { min-width: 0; }

    .opt.is-wrong {
      border-color: var(--no-border);
      background: var(--no-bg);
      color: var(--no-text);
    }

    .opt.is-wrong .opt-key { background: var(--no-border); color: var(--no-text); }

    .opt.is-correct {
      border-color: var(--ok-border);
      background: var(--ok-bg);
      color: var(--ok-text);
      font-weight: 600;
    }

    .opt.is-correct .opt-key { background: var(--ok-border); color: var(--ok-text); }

    .opt:disabled { cursor: default; }
    .opt:disabled:hover { border-color: var(--border-default); }

    /* 실습형 입력 */
    .answer-form { display: flex; gap: 7px; align-items: stretch; }

    .answer-input {
      flex: 1 1 auto;
      min-width: 0;
      font-family: var(--font-mono);
      font-size: 13px;
      letter-spacing: 0;
      color: var(--text-primary);
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 10px 12px;
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .answer-input::placeholder { color: var(--text-muted); font-family: var(--font-sans); }

    .answer-input:focus {
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 3px var(--accent-subtle);
    }

    .answer-input:disabled { color: var(--ok-text); border-color: var(--ok-border); background: var(--ok-bg); }

    .btn-primary {
      flex: 0 0 auto;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: #ffffff;
      background: var(--accent-primary);
      border: 1px solid var(--accent-primary);
      border-radius: 10px;
      padding: 10px 16px;
      cursor: pointer;
      transition: background-color 0.15s ease;
    }

    .btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
    .btn-primary:disabled { background: var(--bg-muted); border-color: var(--bg-muted); color: var(--text-muted); cursor: default; }

    .quick-chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }

    .chip-input {
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: 0;
      padding: 3px 9px;
      border-radius: 6px;
      background: var(--bg-page);
      color: var(--text-secondary);
    }

    .q-foot {
      display: flex;
      align-items: center;
      gap: 7px;
      flex-wrap: wrap;
      margin-top: 12px;
    }

    .q-tries { font-size: 11px; color: var(--text-muted); margin-left: auto; font-variant-numeric: tabular-nums; }

    .hint-box {
      margin-top: 10px;
      background: var(--bg-page);
      border: 1px dashed var(--border-strong);
      border-radius: 10px;
      padding: 11px 13px;
    }

    .hint-label {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      margin-bottom: 5px;
    }

    .hint-list { list-style: none; display: flex; flex-direction: column; gap: 5px; }

    .hint-list li {
      position: relative;
      font-size: 12px;
      line-height: 1.65;
      color: var(--text-secondary);
      padding-left: 12px;
    }

    .hint-list li::before {
      content: "";
      position: absolute;
      left: 0;
      top: 8px;
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: var(--text-muted);
    }

    .q-feedback {
      margin-top: 10px;
      font-size: 12.5px;
      font-weight: 600;
      line-height: 1.6;
      border-radius: 9px;
      padding: 9px 12px;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      color: var(--text-secondary);
    }

    .q-feedback.ok { color: var(--ok-text); background: var(--ok-bg); border-color: var(--ok-border); }
    .q-feedback.no { color: var(--no-text); background: var(--no-bg); border-color: var(--no-border); }

    /* 해설 */
    .q-explain {
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--border-default);
    }

    .explain-head {
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.01em;
      color: var(--text-primary);
      margin-bottom: 9px;
    }

    .explain-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 10px;
      margin-bottom: 12px;
    }

    .explain-col {
      background: var(--bg-page);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 11px 12px;
      min-width: 0;
    }

    .explain-col h4 {
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--text-muted);
      margin-bottom: 5px;
    }

    .explain-col p {
      font-size: 12.3px;
      line-height: 1.72;
      color: var(--text-secondary);
    }

    .code-compare {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 8px;
    }

    .cmp {
      border-radius: 10px;
      overflow: hidden;
      background: var(--code-bg);
      border: 1px solid var(--border-default);
      min-width: 0;
    }

    .cmp-vuln { border-color: rgba(239, 68, 68, 0.45); }
    .cmp-secure { border-color: rgba(16, 185, 129, 0.45); }

    .cmp-head {
      font-family: var(--font-mono);
      font-size: 10px;
      letter-spacing: 0.02em;
      padding: 6px 11px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .cmp-vuln .cmp-head { color: #fca5a5; background: rgba(239, 68, 68, 0.12); }
    .cmp-secure .cmp-head { color: #6ee7b7; background: rgba(16, 185, 129, 0.12); }

    .cmp pre {
      margin: 0;
      padding: 10px 11px;
      font-family: var(--font-mono);
      font-size: 11.3px;
      line-height: 1.65;
      color: var(--code-text);
      white-space: pre;
      tab-size: 2;
      letter-spacing: 0;
    }

    .empty-state {
      display: none;
      text-align: center;
      padding: 40px 16px;
      font-size: 13px;
      color: var(--text-muted);
      background: var(--bg-surface);
      border: 1px dashed var(--border-strong);
      border-radius: 12px;
    }

    .empty-state.show { display: block; }

    .footer {
      margin-top: 30px;
      padding-top: 16px;
      border-top: 1px solid var(--border-default);
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.8;
    }

    /* Mobile */
    @media (max-width: 640px) {
      .nav-container { padding: 0 12px; height: 54px; gap: 6px; }
      .brand-logo-img { width: 24px; height: 24px; }
      .brand-name { font-size: 15px; }
      .nav-tabs { margin-left: 6px; gap: 4px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; border-radius: 14px; }
      .update-meta { display: none !important; }
      .nav-actions a.icon-btn { display: none; }
      .container { padding: 18px 12px 60px; }
      .hero-title { font-size: 21px; }
      .hero-desc { font-size: 13px; line-height: 1.6; }
      .hero-stats { gap: 6px; }
      .stat-chip { font-size: 11px; padding: 3px 8px; }
      .summary { grid-template-columns: minmax(0, 1fr); gap: 12px; padding: 14px; }
      .sum-num strong { font-size: 26px; }
      .controls { padding: 13px 14px; border-radius: 12px; }
      .filter-row { gap: 8px; }
      .filter-label { flex: 0 0 40px; font-size: 10.5px; padding-top: 7px; }
      .chip { font-size: 11.5px; padding: 5px 9px; }
      .q-card { padding: 15px 14px; border-radius: 12px; }
      .q-title { font-size: 15.5px; }
      .q-brief { font-size: 12.5px; }
      .q-top { gap: 5px; }
      .q-badge { font-size: 9.8px; padding: 2px 6px; }
      .code-body pre { font-size: 11.2px; padding: 10px; }
      .q-prompt { font-size: 13px; }
      .opt { font-size: 12.5px; padding: 9px 11px; }
      .answer-form { flex-direction: column; }
      .btn-primary { width: 100%; padding: 11px 16px; }
      .explain-grid { grid-template-columns: minmax(0, 1fr); gap: 8px; }
      .code-compare { grid-template-columns: minmax(0, 1fr); gap: 8px; }
      .cmp pre { font-size: 11px; }
    }

    /* 내비게이션 7탭 수용: 좁은 화면에서는 브랜드 텍스트 숨김 */
    @media (max-width: 560px) {
      .brand-name { display: none; }
    }

    /* 내비게이션 7탭 대응: 탭 영역만 가로 스크롤, 테마 토글은 고정 */
    @media (max-width: 640px) {
      .nav-brand { min-width: 0; }
      .nav-tabs { flex: 1 1 auto; min-width: 0; overflow-x: auto; white-space: nowrap; scrollbar-width: none; -ms-overflow-style: none; }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 7px; font-size: 11px; }
    }

    @media (max-width: 430px) {
      .nav-container { padding: 0 8px; height: 52px; gap: 4px; }
      .brand-logo-img { width: 22px; height: 22px; }
      .nav-tabs {
        margin-left: 2px;
        gap: 1px;
        flex: 1 1 auto;
        min-width: 0;
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
      }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 5px; font-size: 10px; border-radius: 11px; letter-spacing: -0.045em; }
      .nav-actions { gap: 4px; }
      .nav-actions .icon-btn { width: 28px; height: 28px; }
      .filter-row { flex-direction: column; gap: 6px; margin-bottom: 12px; }
      .filter-label { flex: none; padding-top: 0; font-size: 10.5px; }
    }
"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 출퇴근길 보안 워게임</title>
  <meta name="description" content="웹 해킹, 로그·침해 분석, 시스템·권한 상승, 네트워크·패킷 4개 카테고리 20문제를 3분 안에 푸는 실전 보안 워게임. 즉시 채점과 취약 코드·시큐어 코드 비교 해설, 브라우저에 저장되는 진행 기록.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
  <style>__CSS__
    [hidden] { display: none !important; }
  </style>
  <script>
    (function () {
      try {
        var saved = localStorage.getItem('secjobs-theme');
        if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.setAttribute('data-theme', 'dark');
        }
      } catch (e) {}
    })();
  </script>
</head>
<body>

  <!-- Global Nav -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
        <div class="nav-tabs">
          <a href="index.html" class="nav-tab-item">채용공고</a>
          <a href="study.html" class="nav-tab-item">시험 공부</a>
          <a href="ai.html" class="nav-tab-item">AI 트렌드</a>
          <a href="cve.html" class="nav-tab-item">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item active">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
        </div>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>기록은 이 브라우저에</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        </button>
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <script>
    // 좁은 화면에서 현재 페이지 탭이 가려지지 않도록 탭 영역만 살짝 스크롤한다.
    (function () {
      function keepActiveTabVisible() {
        var box = document.querySelector('.nav-tabs');
        if (!box) return;
        var act = box.querySelector('.nav-tab-item.active');
        if (!act || box.scrollWidth <= box.clientWidth) return;
        var br = box.getBoundingClientRect();
        var ar = act.getBoundingClientRect();
        if (ar.right > br.right) box.scrollLeft += (ar.right - br.right) + 8;
        else if (ar.left < br.left) box.scrollLeft -= (br.left - ar.left) + 8;
      }
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', keepActiveTabVisible);
      else keepActiveTabVisible();
      window.addEventListener('resize', keepActiveTabVisible);
    })();
  </script>

  <main class="container">

    <section class="hero">
      <span class="hero-pill">SECURITY DRILL</span>
      <h1 class="hero-title">출퇴근길 보안 워게임</h1>
      <p class="hero-desc">현업에서 마주치는 결함을 짧은 코드·서버 로그·패킷으로 재구성했습니다. 한 문제 3분, 지하철에서 한 손으로 풀고 바로 채점받으세요. 정답을 확인하면 공격 원리와 실무 영향, 그리고 취약 코드와 시큐어 코드를 나란히 보여 줍니다. 매일 아침 08:00에 최신 CVE·보안 이슈를 소재로 새 문제 2개가 추가됩니다.</p>
      <div class="hero-stats">
        <span class="stat-chip">문제 <strong>__TOTAL__</strong></span>
        <span class="stat-chip">카테고리 <strong>4</strong></span>
        <span class="stat-chip">실습형 <strong>__INPUT_COUNT__</strong></span>
        __TODAY_CHIP__
        <span class="stat-chip">기록 <strong>localStorage</strong></span>
      </div>
    </section>

    <section class="summary" aria-label="진행 현황">
      <div class="sum-main">
        <div class="sum-num"><strong id="solvedNum">0</strong><span>/ __TOTAL__</span></div>
        <div class="sum-label">해결한 문제</div>
        <div class="sum-bar"><i id="solvedBar"></i></div>
      </div>
      <div class="sum-side">
        <div class="sum-rows">
          <span class="sum-row">정답률 <strong id="accNum">—</strong></span>
          <span class="sum-row">제출 <strong id="tryNum">0</strong>회</span>
          <span class="sum-row">실습형 <strong id="inputNum">0</strong> / __INPUT_COUNT__</span>
        </div>
        <div class="cat-progress" id="catProgress"></div>
      </div>
    </section>

    <section class="controls" aria-label="문제 필터">
      <div class="filter-row">
        <div class="filter-label">카테고리</div>
        <div class="chips" id="catFilter"></div>
      </div>
      <div class="filter-row">
        <div class="filter-label">난이도</div>
        <div class="chips" id="levelFilter"></div>
      </div>
      <div class="filter-row">
        <div class="filter-label">상태</div>
        <div class="chips" id="statusFilter"></div>
      </div>
      <div class="controls-foot">
        <span class="visible-count" id="visibleCount">__TOTAL__문제</span>
        <div class="foot-btns">
          <button class="btn-ghost" type="button" id="resetFilters">필터 초기화</button>
          <button class="btn-ghost" type="button" id="resetProgress">기록 초기화</button>
        </div>
      </div>
    </section>

    <div class="q-list" id="qList">
__CARDS__
    </div>

    <div class="empty-state" id="emptyState">조건에 맞는 문제가 없습니다. 필터를 초기화해 보세요.</div>

    <footer class="footer">
      Infosec Archive · 출퇴근길 보안 워게임<br>
      시나리오는 실제 취약점 유형을 학습용으로 각색한 것입니다. 진행 기록은 이 브라우저(localStorage)에만 저장되며 서버로 전송되지 않습니다.<br>
      __BUILT_AT__ 기준
    </footer>
  </main>

  <script>
    // ---- Theme (index.html / study.html / ai.html / cve.html / outfit.html 과 동일한 secjobs-theme 동기화) ----
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');

    function setTheme(theme) {
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'block';
        localStorage.setItem('secjobs-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
        if (moonIcon) moonIcon.style.display = 'block';
        if (sunIcon) sunIcon.style.display = 'none';
        localStorage.setItem('secjobs-theme', 'light');
      }
    }

    (function initTheme() {
      const saved = localStorage.getItem('secjobs-theme');
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) setTheme('dark');
      else setTheme('light');
    })();

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    // ---- 데이터 ----
    const DATA = __DATA_JSON__;
    const CATS = __CATS_JSON__;
    const LEVELS = __LEVELS_JSON__;
    const STORE_KEY = 'secjobs-wargame-v1';

    const catLabel = {};
    CATS.forEach(c => { catLabel[c.key] = c.label; });
    const levelLabel = {};
    LEVELS.forEach(l => { levelLabel[l.key] = l.label; });

    // ---- 진행 기록 ----
    function emptyRecord() {
      const r = {};
      DATA.forEach(q => { r[q.id] = { solved: false, attempts: 0, correct: 0, revealed: false }; });
      return r;
    }

    function loadRecord() {
      const base = emptyRecord();
      try {
        const raw = localStorage.getItem(STORE_KEY);
        if (!raw) return base;
        const saved = JSON.parse(raw);
        Object.keys(base).forEach(id => {
          if (saved && saved[id] && typeof saved[id] === 'object') {
            base[id].solved = !!saved[id].solved;
            base[id].attempts = Number(saved[id].attempts) || 0;
            base[id].correct = Number(saved[id].correct) || 0;
            base[id].revealed = !!saved[id].revealed;
          }
        });
      } catch (e) {}
      return base;
    }

    function saveRecord() {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(RECORD)); } catch (e) {}
    }

    let RECORD = loadRecord();
    const filters = { cat: 'all', level: 'all', status: 'all' };

    // ---- 필터 UI ----
    const catFilter = document.getElementById('catFilter');
    const levelFilter = document.getElementById('levelFilter');
    const statusFilter = document.getElementById('statusFilter');
    const qList = document.getElementById('qList');
    const emptyState = document.getElementById('emptyState');

    function catSolved(key) {
      return DATA.filter(q => q.cat === key && RECORD[q.id].solved).length;
    }

    function buildFilterChips() {
      const catItems = [{ key: 'all', label: '전체' }].concat(CATS);
      catFilter.innerHTML = catItems.map(c => {
        const total = c.key === 'all' ? DATA.length : DATA.filter(q => q.cat === c.key).length;
        const done = c.key === 'all'
          ? DATA.filter(q => RECORD[q.id].solved).length
          : catSolved(c.key);
        return '<button class="chip' + (filters.cat === c.key ? ' active' : '') + '" type="button" data-group="cat" data-value="' + c.key + '">'
          + c.label + ' <em>' + done + '/' + total + '</em></button>';
      }).join('');

      const lvItems = [{ key: 'all', label: '전체' }].concat(LEVELS);
      levelFilter.innerHTML = lvItems.map(l => {
        const total = l.key === 'all' ? DATA.length : DATA.filter(q => q.level === l.key).length;
        const done = l.key === 'all'
          ? DATA.filter(q => RECORD[q.id].solved).length
          : DATA.filter(q => q.level === l.key && RECORD[q.id].solved).length;
        return '<button class="chip' + (filters.level === l.key ? ' active' : '') + '" type="button" data-group="level" data-value="' + l.key + '">'
          + l.label + ' <em>' + done + '/' + total + '</em></button>';
      }).join('');

      const stItems = [
        { key: 'all', label: '전체', n: DATA.length },
        { key: 'todo', label: '미해결', n: DATA.filter(q => !RECORD[q.id].solved).length },
        { key: 'done', label: '해결', n: DATA.filter(q => RECORD[q.id].solved).length }
      ];
      statusFilter.innerHTML = stItems.map(s =>
        '<button class="chip' + (filters.status === s.key ? ' active' : '') + '" type="button" data-group="status" data-value="' + s.key + '">'
        + s.label + ' <em>' + s.n + '</em></button>'
      ).join('');
    }

    function bindFilterClicks() {
      [catFilter, levelFilter, statusFilter].forEach(function (box) {
        box.addEventListener('click', function (ev) {
          const btn = ev.target.closest('.chip');
          if (!btn) return;
          filters[btn.dataset.group] = btn.dataset.value;
          buildFilterChips();
          applyFilters();
        });
      });
    }

    // ---- 요약 ----
    function renderSummary() {
      const solved = DATA.filter(q => RECORD[q.id].solved).length;
      const attempts = DATA.reduce((a, q) => a + RECORD[q.id].attempts, 0);
      const correct = DATA.reduce((a, q) => a + RECORD[q.id].correct, 0);
      const inputSolved = DATA.filter(q => q.type === 'input' && RECORD[q.id].solved).length;

      document.getElementById('solvedNum').textContent = solved;
      document.getElementById('solvedBar').style.width = (DATA.length ? (solved / DATA.length) * 100 : 0) + '%';
      document.getElementById('accNum').textContent = attempts ? Math.round((correct / attempts) * 100) + '%' : '—';
      document.getElementById('tryNum').textContent = attempts;
      const inputNum = document.getElementById('inputNum');
      if (inputNum) inputNum.textContent = inputSolved;

      document.getElementById('catProgress').innerHTML = CATS.map(function (c) {
        const total = DATA.filter(q => q.cat === c.key).length;
        const done = catSolved(c.key);
        const pct = total ? (done / total) * 100 : 0;
        return '<span class="cat-bar">' + c.label + ' <b>' + done + '/' + total + '</b><i><s style="width:' + pct + '%"></s></i></span>';
      }).join('');
    }

    // ---- 카드 채점 ----
    function cardOf(id) { return document.getElementById('q-' + id); }

    function showExplain(card) {
      const box = card.querySelector('.q-explain');
      if (box) box.hidden = false;
    }

    function markSolved(card, rec) {
      card.classList.add('is-solved');
      const state = card.querySelector('.q-state');
      if (state) state.hidden = false;
      const input = card.querySelector('.answer-input');
      if (input) input.disabled = true;
      const submit = card.querySelector('.btn-primary');
      if (submit) submit.disabled = true;
      const reveal = card.querySelector('.btn-reveal');
      if (reveal) reveal.hidden = true;
      showExplain(card);
    }

    function feedback(card, text, kind) {
      const box = card.querySelector('.q-feedback');
      box.hidden = false;
      box.className = 'q-feedback' + (kind ? ' ' + kind : '');
      box.textContent = text;
    }

    function triesText(rec) {
      return rec.solved ? '정답 · 제출 ' + rec.attempts + '회' : (rec.attempts ? '제출 ' + rec.attempts + '회' : '');
    }

    function updateTries(card, rec) {
      const el = card.querySelector('.q-tries');
      const text = triesText(rec);
      el.textContent = text;
      el.hidden = !text;
      const reveal = card.querySelector('.btn-reveal');
      if (reveal) reveal.hidden = rec.solved || rec.revealed || rec.attempts < 2;
    }

    function normalizeInput(s) {
      return String(s || '').trim().replace(/\\s+/g, ' ');
    }

    function matchesPattern(q, value) {
      const v = normalizeInput(value);
      if (!v) return false;
      const patterns = q.patterns || [];
      for (let i = 0; i < patterns.length; i++) {
        try {
          if (new RegExp(patterns[i], 'i').test(v)) return true;
        } catch (e) {}
      }
      return false;
    }

    function initCard(q) {
      const card = cardOf(q.id);
      const rec = RECORD[q.id];

      if (q.type === 'choice') {
        const opts = Array.from(card.querySelectorAll('.opt'));
        opts.forEach(function (btn) {
          btn.addEventListener('click', function () {
            if (rec.solved) return;
            const picked = Number(btn.dataset.idx);
            rec.attempts += 1;
            if (picked === q.answer) {
              rec.correct += 1;
              rec.solved = true;
              opts.forEach(function (o) {
                o.disabled = true;
                if (Number(o.dataset.idx) === q.answer) o.classList.add('is-correct');
                else o.classList.remove('is-wrong');
              });
              feedback(card, '정답입니다. 아래에서 공격 원리와 취약·시큐어 코드를 비교해 보세요.', 'ok');
              markSolved(card, rec);
            } else {
              btn.classList.add('is-wrong');
              btn.disabled = true;
              feedback(card, '오답입니다. 제시된 코드와 로그의 흐름을 다시 대조해 보세요.', 'no');
            }
            updateTries(card, rec);
            saveRecord();
            renderSummary();
            buildFilterChips();
          });
        });
      } else {
        const form = card.querySelector('.answer-form');
        const input = card.querySelector('.answer-input');
        form.addEventListener('submit', function (ev) {
          ev.preventDefault();
          if (rec.solved) return;
          const value = input.value;
          if (!normalizeInput(value)) { input.focus(); return; }
          rec.attempts += 1;
          if (matchesPattern(q, value)) {
            rec.correct += 1;
            rec.solved = true;
            feedback(card, '정답입니다. 입력값이 그대로 공격에 쓰입니다. 아래 해설에서 대응 코드를 확인하세요.', 'ok');
            markSolved(card, rec);
          } else {
            feedback(card, rec.attempts >= 2
              ? '아직 정답이 아닙니다. 힌트 2단계를 열거나 아래 정답 보기를 사용할 수 있습니다.'
              : '아직 정답이 아닙니다. 형식(따옴표·주석·경로 구분자)을 힌트에서 확인해 보세요.', 'no');
          }
          updateTries(card, rec);
          saveRecord();
          renderSummary();
          buildFilterChips();
        });

        const quick = card.querySelector('.quick-chips');
        if (quick) {
          quick.addEventListener('click', function (ev) {
            const chip = ev.target.closest('.chip-input');
            if (!chip || rec.solved) return;
            input.value = input.value + chip.dataset.chip;
            input.focus();
            try { input.setSelectionRange(input.value.length, input.value.length); } catch (e) {}
          });
        }
      }

      const hintBtn = card.querySelector('[data-act="hint"]');
      const hintBox = card.querySelector('.hint-box');
      const hintList = hintBox.querySelector('.hint-list');

      function paintHints(step) {
        hintList.textContent = '';
        q.hints.slice(0, step).forEach(function (h) {
          const li = document.createElement('li');
          li.textContent = h;
          hintList.appendChild(li);
        });
        hintBox.hidden = step === 0;
        hintBtn.textContent = step === 0
          ? '힌트 보기'
          : (step < q.hints.length ? '힌트 한 단계 더' : '힌트 접기');
      }

      card.dataset.hintStep = '0';
      hintBtn.addEventListener('click', function () {
        const step = Number(card.dataset.hintStep) || 0;
        const next = step >= q.hints.length ? 0 : step + 1;
        card.dataset.hintStep = String(next);
        paintHints(next);
      });

      const reveal = card.querySelector('[data-act="reveal"]');
      if (reveal) {
        reveal.addEventListener('click', function () {
          rec.revealed = true;
          card.classList.add('is-revealed');
          if (q.type === 'input') {
            const input = card.querySelector('.answer-input');
            if (input && !input.disabled) input.value = q.sample || '';
          } else {
            Array.from(card.querySelectorAll('.opt')).forEach(function (o) {
              o.disabled = true;
              if (Number(o.dataset.idx) === q.answer) o.classList.add('is-correct');
            });
          }
          feedback(card, '정답을 확인했습니다. 이 문제는 해결로 기록되지 않습니다.', '');
          showExplain(card);
          reveal.hidden = true;
          saveRecord();
        });
      }

      // 저장된 상태 복원
      if (rec.solved) {
        if (q.type === 'choice') {
          Array.from(card.querySelectorAll('.opt')).forEach(function (o) {
            o.disabled = true;
            if (Number(o.dataset.idx) === q.answer) o.classList.add('is-correct');
          });
        }
        feedback(card, '해결한 문제입니다. 해설은 아래에 그대로 남겨 두었습니다.', 'ok');
        markSolved(card, rec);
      } else if (rec.revealed) {
        card.classList.add('is-revealed');
        showExplain(card);
      }
      updateTries(card, rec);
    }

    // ---- 필터 적용 ----
    function matchesFilters(q) {
      if (filters.cat !== 'all' && q.cat !== filters.cat) return false;
      if (filters.level !== 'all' && q.level !== filters.level) return false;
      if (filters.status === 'todo' && RECORD[q.id].solved) return false;
      if (filters.status === 'done' && !RECORD[q.id].solved) return false;
      return true;
    }

    function applyFilters() {
      let shown = 0;
      DATA.forEach(function (q) {
        const card = cardOf(q.id);
        if (!card) return;
        const ok = matchesFilters(q);
        card.hidden = !ok;
        if (ok) shown += 1;
      });
      emptyState.classList.toggle('show', shown === 0);
      document.getElementById('visibleCount').textContent = shown + '문제 표시 / 전체 ' + DATA.length;
    }

    // ---- 초기화 ----
    document.getElementById('resetFilters').addEventListener('click', function () {
      filters.cat = 'all';
      filters.level = 'all';
      filters.status = 'all';
      buildFilterChips();
      applyFilters();
    });

    document.getElementById('resetProgress').addEventListener('click', function () {
      if (!window.confirm('이 브라우저에 저장된 진행 기록을 모두 지울까요? 되돌릴 수 없습니다.')) return;
      RECORD = emptyRecord();
      saveRecord();
      DATA.forEach(function (q) {
        const card = cardOf(q.id);
        if (!card) return;
        card.classList.remove('is-solved', 'is-revealed');
        const state = card.querySelector('.q-state');
        if (state) state.hidden = true;
        const fb = card.querySelector('.q-feedback');
        if (fb) { fb.hidden = true; fb.textContent = ''; fb.className = 'q-feedback'; }
        const ex = card.querySelector('.q-explain');
        if (ex) ex.hidden = true;
        const input = card.querySelector('.answer-input');
        if (input) { input.disabled = false; input.value = ''; }
        const submit = card.querySelector('.btn-primary');
        if (submit) submit.disabled = false;
        Array.from(card.querySelectorAll('.opt')).forEach(function (o) {
          o.disabled = false;
          o.classList.remove('is-wrong', 'is-correct');
        });
        const hintBtn = card.querySelector('[data-act="hint"]');
        const hintBox = card.querySelector('.hint-box');
        if (hintBox) { hintBox.hidden = true; hintBox.querySelector('.hint-list').textContent = ''; }
        if (hintBtn) hintBtn.textContent = '힌트 보기';
        card.dataset.hintStep = '0';
        updateTries(card, RECORD[q.id]);
      });
      renderSummary();
      buildFilterChips();
      applyFilters();
    });

    // ---- 시작 ----
    buildFilterChips();
    bindFilterClicks();
    DATA.forEach(initCard);
    renderSummary();
    applyFilters();
  </script>
</body>
</html>
"""


def seed_db(verbose=True):
    """정적 20문제를 archive.db(wargame_questions)로 이관한다 (id 보존, 재실행 안전)."""
    from db_manager import seed_wargame_questions, count_wargame_questions
    before = count_wargame_questions()
    inserted = seed_wargame_questions(QUESTIONS, created_date=STATIC_CREATED_DATE)
    after = count_wargame_questions()
    if verbose:
        print("-> wargame_questions 이관: %d개 추가 (전체 %d개)" % (inserted, after))
    return before, inserted, after


def load_questions(verbose=True):
    """DB의 wargame_questions를 읽는다. 테이블이 비었으면 정적 문제를 이관하고, DB 장애 시 내장 문제로 대체한다."""
    try:
        from db_manager import get_wargame_questions, count_wargame_questions
        if count_wargame_questions(is_daily=0) == 0:
            seed_db(verbose=verbose)
        qs = get_wargame_questions()
        if qs:
            return qs
    except Exception as e:  # DB 손상·권한 문제 시에도 페이지는 떠야 한다
        if verbose:
            print("  [경고] DB에서 워게임 문제를 읽지 못해 내장 문제로 빌드합니다: %s: %s"
                  % (type(e).__name__, e))
    fallback = []
    for i, q in enumerate(QUESTIONS):
        item = dict(q)
        item.setdefault("created_date", STATIC_CREATED_DATE)
        item["is_daily"] = 0
        item["sort_order"] = i
        fallback.append(item)
    return fallback


def sort_questions(qs):
    """데일리 최신순 → 그 아래 정적 문제 순. 새로 추가된 문제가 맨 위에 오게 한다."""
    daily = [q for q in qs if q.get("is_daily")]
    static = [q for q in qs if not q.get("is_daily")]
    daily.sort(key=lambda q: (q.get("created_date") or "", q.get("sort_order") or 0, q.get("id") or ""), reverse=True)
    static.sort(key=lambda q: (q.get("sort_order") or 0, q.get("id") or ""))
    return daily + static


def build():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    built_at = now.strftime("%Y-%m-%d %H:%M KST")
    today_str = now.strftime("%Y-%m-%d")

    questions = sort_questions(load_questions())

    payload = []
    for q in questions:
        item = {
            "id": q["id"], "cat": q["cat"], "level": q["level"], "type": q["type"],
            "patterns": q.get("patterns", []),
            "hints": q.get("hints", []),
        }
        if q["type"] == "choice":
            item["answer"] = q["answer"]
            item["sample"] = "ABCD"[q["answer"]]
        else:
            # 정답 보기용 예시 (입력창에 채워 준다)
            item["sample"] = q.get("sample", q.get("placeholder", ""))
        payload.append(item)

    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    cats_json = json.dumps(CATS, ensure_ascii=False, separators=(",", ":"))
    levels_json = json.dumps(LEVELS, ensure_ascii=False, separators=(",", ":"))

    cards = "\n".join(
        "      " + _render_static(q, no=i + 1, today_str=today_str).replace("\n", "\n      ")
        for i, q in enumerate(questions)
    )
    input_count = len([q for q in questions if q["type"] == "input"])
    today_count = len([q for q in questions if q.get("is_daily") and q.get("created_date") == today_str])
    daily_count = len([q for q in questions if q.get("is_daily")])
    today_chip = (('<span class="stat-chip">오늘 추가 <strong>%d</strong></span>' % today_count)
                  if today_count else "")

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__CARDS__", cards)
    html = html.replace("__DATA_JSON__", data_json.replace("</", "<\\/"))
    html = html.replace("__CATS_JSON__", cats_json.replace("</", "<\\/"))
    html = html.replace("__LEVELS_JSON__", levels_json.replace("</", "<\\/"))
    html = html.replace("__TODAY_CHIP__", today_chip)
    html = html.replace("__TOTAL__", str(len(questions)))
    html = html.replace("__INPUT_COUNT__", str(input_count))
    html = html.replace("__BUILT_AT__", esc(built_at))

    with open(WARGAME_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    cats_count = {}
    for q in questions:
        cats_count[q["cat"]] = cats_count.get(q["cat"], 0) + 1
    print("-> 'wargame.html' 생성 완료 (문제 %d개 · 실습형 %d개 · 데일리 %d개(오늘 %d개) · 카테고리 %s)"
          % (len(questions), input_count, daily_count, today_count,
             ", ".join("%s %d" % (c["label"], cats_count.get(c["key"], 0)) for c in CATS)))
    return len(questions)


if __name__ == "__main__":
    import sys
    if "--migrate" in sys.argv:
        seed_db()
    if "--migrate-only" not in sys.argv:
        build()

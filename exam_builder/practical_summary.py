# -*- coding: utf-8 -*-
"""
practical_summary.py
2026 이기적 정보보안기사 필기+실기 올인원 실기 편제 기준
- 실기 내용별 심층 요약 20선
- 실기 필수 단답형 핵심 용어사전 30선
총 50개 실기 전용 모듈
"""

def get_practical_summary():
    items = []

    # ==========================================
    # [내용별 핵심정리 20선]
    # ==========================================
    items.append({
        "id": "prac_content_01", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "리눅스 침해사고 분석 및 점검 필수 명령어 10선", "badge": "실기 단답·실무",
        "points": [
            "<code>find / -perm -4000 -type f</code>: SetUID가 설정된 파일을 전수 검색하여 권한 상승 백도어 식별.",
            "<code>netstat -antp</code>: 활성 소켓, 포트 번호(숫자 n), 프로토콜, PID 및 실행 프로그램 이름(p) 확인.",
            "<code>find / -mtime -1</code>: 최근 24시간 이내에 내용이 수정된 파일 검색 (악성코드 침투 시점 추적).",
            "<code>chattr +i [파일]</code>: root 권한자라 할지라도 파일 삭제, 수정, 이름 변경을 원천 잠금(Immutable).",
            "<code>lastlog</code>: /var/log/lastlog 파일을 읽어 시스템 내 모든 계정의 최근 로그인 시간과 IP 확인.",
            "<code>sha256sum [파일]</code>: 무결성 검증을 위한 SHA-256 해시값 생성 및 Tripwire DB 대조.",
            "<code>crontab -l -u [계정]</code>: /var/spool/cron 디렉토리의 사용자별 주기적 자동 실행 백도어 점검.",
            "<code>ps -ef | grep [의심프로세스]</code> 및 <code>ls -l /proc/[PID]/exe</code>: 숨겨진 프로세스의 실제 실행 파일 경로 확인.",
            "<code>tcpdump -i eth0 -nn 'port 80 and host 192.168.1.100'</code>: 특정 포트와 호스트 간 실시간 원시 패킷 덤프.",
            "<code>icacls (윈도우)</code>: NTFS 접근 제어 목록(ACL) 확인 및 수정 (Linux의 chmod/chown 대응)."
        ]
    })

    items.append({
        "id": "prac_content_02", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "서버 및 네트워크 주요 보안 설정 파라미터 족보", "badge": "실기 단답·실무",
        "points": [
            "<code>umask 027</code>: 파일 생성 기본 권한 640(-rw-r-----), 디렉토리 750(drwxr-x---) 강제 설정.",
            "<code>/etc/ssh/sshd_config</code>: <code>PermitRootLogin no</code> (root 직접 접속 차단), <code>PasswordAuthentication no</code> (공개키 인증 강제).",
            "<code>httpd.conf (Apache)</code>: <code>Options -Indexes</code> (디렉토리 리스팅 제거), <code>ServerTokens Prod</code> (상세 버전 은닉).",
            "<code>nginx.conf (Nginx)</code>: <code>server_tokens off;</code>, <code>add_header X-Frame-Options DENY;</code> (클릭재킹 방지).",
            "<code>/etc/hosts.allow & hosts.deny</code>: TCP Wrapper 접근 제어. allow 파일이 우선 적용된 후 deny 파일 적용.",
            "<code>/etc/login.defs</code>: <code>PASS_MAX_DAYS 90</code>, <code>PASS_MIN_DAYS 1</code>, <code>PASS_WARN_AGE 7</code> 패스워드 만료 주기.",
            "<code>/etc/sudoers</code>: 특정 계정에 패스워드 없이 root 권한을 부여하는 취약 설정(NOPASSWD: ALL) 점검 및 제거."
        ]
    })

    items.append({
        "id": "prac_content_03", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "웹 침해사고 로그 분석(SQLi·Path Traversal) 및 Snort 룰 작성", "badge": "실기 서술·실무",
        "points": [
            "<strong>Union-Based SQLi 로그:</strong> <code>GET /view.php?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users--%20 HTTP/1.1</code> -> 공백 인코딩(%20), UNION SELECT 키워드, information_schema 조회 식별.",
            "<strong>Path Traversal 로그:</strong> <code>GET /down.jsp?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1</code> -> %2e%2e%2f(상위 경로 ../) 디코딩 및 시스템 기밀 파일(/etc/passwd) 탈취 패턴 분석.",
            "<strong>WebShell 업로드 탐지 Snort 룰 작성 표준:</strong>",
            "<code>alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell JSP Upload\"; content:\"multipart/form-data\"; content:\".jsp\"; nocase; sid:1000001;)</code>",
            "<code>alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell Execution - cmd.jsp\"; content:\"cmd.jsp\"; nocase; content:\"cmd=\"; distance:0; sid:1000002;)</code>"
        ]
    })

    items.append({
        "id": "prac_content_04", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "SW 개발보안(시큐어코딩) 47개 보안약점 핵심 가이드", "badge": "실기 서술·실무",
        "points": [
            "<strong>1. SQL Injection:</strong> 반드시 파라미터 바인딩을 지원하는 PreparedStatement 사용. (취약: <code>Statement.executeQuery(\"...'\" + id + \"'\")</code>).",
            "<strong>2. XSS (크로스사이트 스크립팅):</strong> HTML Entity 치환(&lt;, &gt;, &amp;, &quot;) 라이브러리 사용 및 JSTL <code>&lt;c:out escapeXml=\"true\"&gt;</code> 적용.",
            "<strong>3. 파일 업로드 보안 3대 수칙:</strong> 화이트리스트 확장자 검증, UUID 파일명 난수화 변경 저장, 업로드 디렉토리 실행 권한(No-Exec) 박탈.",
            "<strong>4. 파일 다운로드 보안:</strong> 경로 조작 문자('../') 제거 및 <code>getCanonicalPath()</code>로 다운로드 루트 범위 검증.",
            "<strong>5. 취약한 난수 생성:</strong> 예측 가능한 <code>java.util.Random</code> 대신 암호학적으로 안전한 <code>java.security.SecureRandom</code> 클래스 사용.",
            "<strong>6. 패스워드 암호화 저장:</strong> 고속 해시(MD5/SHA) 단독 사용 금지, <code>PBKDF2 / bcrypt / Argon2</code> 기반 솔트 및 키 스트레칭 필수 적용."
        ]
    })

    items.append({
        "id": "prac_content_05", "type": "content", "category": "law", "category_name": "디지털 포렌식 & 법률",
        "title": "디지털 포렌식 5대 원칙 및 휘발성 데이터 수집 순서", "badge": "실기 서술·실무",
        "points": [
            "<strong>디지털 포렌식 5대 기본 원칙:</strong>",
            "1. <code>정당성의 원칙</code>: 적법 절차에 따라 영장 또는 동의 하에 수집.",
            "2. <code>재현성의 원칙</code>: 동일 조건에서 동일한 분석 도구 적용 시 동일한 결과 도출.",
            "3. <code>신속성의 원칙</code>: 휘발성 데이터 소실 전 신속하게 증거 확보.",
            "4. <code>연계보관성의 원칙 (Chain of Custody)</code>: 수집, 이송, 보관, 분석, 법정 제출 전 과정의 담당자 및 상태가 연속적으로 문서화 증명.",
            "5. <code>무결성의 원칙</code>: 수집 당시의 해시값(SHA-256)과 법정 제출 시 해시값이 100% 일치해야 함.",
            "<strong>휘발성 데이터 수집 순서 (Order of Volatility):</strong>",
            "1. CPU 레지스터 및 캐시 메모리 -> 2. 물리적 RAM 메모리 -> 3. 활성 네트워크 연결 및 소켓 상태 -> 4. 임시 파일 및 스왑 공간 -> 5. 하드디스크 비휘발성 파일시스템 -> 6. 원격 백업 미디어."
        ]
    })

    items.append({
        "id": "prac_content_06", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "리눅스 iptables 방화벽 패킷 필터링 문법 및 체인 구조", "badge": "실기 단답·실무",
        "points": [
            "<strong>3대 기본 테이블:</strong> filter (기본 패킷 필터링), nat (IP/포트 주소 변환), mangle (특수 패킷 변조).",
            "<strong>filter 테이블 3대 기본 체인:</strong> <code>INPUT</code> (로컬 호스트로 들어오는 패킷), <code>FORWARD</code> (호스트를 통과하는 패킷), <code>OUTPUT</code> (로컬에서 나가는 패킷).",
            "<strong>핵심 옵션:</strong> <code>-A</code> (체인 끝에 추가), <code>-I</code> (지정 위치에 삽입), <code>-D</code> (규칙 삭제), <code>-p</code> (프로토콜), <code>-s</code> (출발지 IP), <code>-d</code> (목적지 IP), <code>--sport/--dport</code> (포트), <code>-j</code> (타겟 동작).",
            "<strong>주요 타겟(-j):</strong> <code>ACCEPT</code> (허용), <code>DROP</code> (무응답 폐기), <code>REJECT</code> (거부 메시지 회신 후 폐기), <code>LOG</code> (syslog에 기록 후 다음 룰 진행)."
        ]
    })

    items.append({
        "id": "prac_content_07", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "윈도우 보안 감사 정책 및 핵심 이벤트 ID 총람", "badge": "실기 단답형",
        "points": [
            "<code>4624</code>: 계정 로그온 성공 (Logon Type: 2-대화형 콘솔, 3-네트워크 공유, 10-원격데스크톱 RDP).",
            "<code>4625</code>: 계정 로그온 실패 (무차별 대입 공격 및 패스워드 스프레이 탐지).",
            "<code>4672</code>: 관리자 특권(Special Privileges)이 새 세션에 할당됨.",
            "<code>4720</code>: 새 사용자 계정이 생성됨 (침해 후 지속성 계정 생성 감시).",
            "<code>4726</code>: 사용자 계정이 삭제됨.",
            "<code>1102</code>: 윈도우 보안 감사 로그가 지워짐(Clear Log) - 침해사고 강력한 은폐 지표."
        ]
    })

    items.append({
        "id": "prac_content_08", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "L4 DoS 공격 유형별 패킷 패턴 분석 및 대응책", "badge": "실기 서술·실무",
        "points": [
            "<strong>SYN Flooding:</strong> 미완결 TCP 3-Way Handshake로 Backlog 큐 고갈 -> SYN Cookie 활성화(<code>sysctl -w net.ipv4.tcp_syncookies=1</code>).",
            "<strong>Land Attack:</strong> 출발지 IP/Port와 목적지 IP/Port가 동일 -> 출발지와 목적지가 동일한 패킷 즉시 차단 룰 적용.",
            "<strong>Smurf Attack:</strong> 피해자 IP로 위조된 ICMP Echo Request를 서브넷 브로드캐스트로 전송 -> 라우터에서 Directed Broadcast 차단(<code>no ip directed-broadcast</code>).",
            "<strong>TearDrop:</strong> IP Fragment Offset 중첩 조작 -> 최신 OS 패치 및 방화벽에서 단편화 패킷 재조합 검증."
        ]
    })

    items.append({
        "id": "prac_content_09", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "웹 브라우저 보안 헤더(HSTS, CSP, X-Frame-Options) 완벽 설정", "badge": "실기 실무",
        "points": [
            "<strong>HSTS (Strict-Transport-Security):</strong> <code>Strict-Transport-Security: max-age=31536000; includeSubDomains; preload</code> -> 1년간 무조건 HTTPS 강제.",
            "<strong>CSP (Content-Security-Policy):</strong> <code>default-src 'self'; script-src 'self' https://trusted.cdn.com; object-src 'none';</code> -> 비인가 스크립트 실행 차단.",
            "<strong>X-Frame-Options:</strong> <code>DENY</code> (어디서도 frame 불가) 또는 <code>SAMEORIGIN</code> -> 클릭재킹 UI Redressing 방어.",
            "<strong>X-Content-Type-Options:</strong> <code>nosniff</code> -> MIME 타입 스니핑 방지.",
            "<strong>Referrer-Policy:</strong> <code>strict-origin-when-cross-origin</code> -> 민감한 URL 쿼리 파라미터 외부 유출 방지."
        ]
    })

    items.append({
        "id": "prac_content_10", "type": "content", "category": "law", "category_name": "디지털 포렌식 & 법률",
        "title": "개인정보 안전성 확보조치 접속기록 점검 및 이상징후 기준", "badge": "실기 서술·실무",
        "points": [
            "<strong>접속기록 법정 항목 5가지:</strong> 1) 사용자 계정, 2) 접속일시, 3) 접속자 IP 주소, 4) 수행 업무(열람·수정·삭제 등), 5) 정보주체 식별정보.",
            "<strong>보관 기간:</strong> 기본 최소 1년 이상 (5만 명 이상 또는 고유식별정보·민감정보 처리 시 최소 2년 이상).",
            "<strong>월 1회 점검 필수 이상징후 시나리오:</strong>",
            "- 단시간 내 대량 개인정보 다운로드 또는 조회 (임계치 초과)",
            "- 근무 시간 외(심야·휴일) 비정상 원격 접속 및 데이터 열람",
            "- 관리자 계정의 비인가 접속지(해외 IP, 공용망)에서의 로그인 시도",
            "- 퇴직자 계정이나 장기 미사용 계정의 활성화 및 데이터 접근"
        ]
    })

    items.append({
        "id": "prac_content_11", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "WebShell 업로드 방어 및 업로드 디렉토리 실행권한 제거", "badge": "실기 실무",
        "points": [
            "<strong>웹서버 실행권한 박탈:</strong> Apache 가상호스트 디렉토리 설정에서 <code>php_admin_flag engine off</code> (PHP 실행 중지) 또는 <code>Options -ExecCGI</code> 적용.",
            "<strong>Nginx 설정:</strong> <code>location ~* ^/upload/.*\\.(php|jsp|asp|sh)$ { deny all; }</code> 구문으로 업로드 경로 내 스크립트 직접 호출 전면 차단.",
            "<strong>저장소 분리:</strong> 웹 루트 디렉토리 외부(NAS 또는 S3 객체 스토리지)에 저장하고 파일명을 UUID 난수로 변경 저장."
        ]
    })

    items.append({
        "id": "prac_content_12", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "리눅스 PAM 패스워드 복잡도 및 임계치 잠금 설정 족보", "badge": "실기 단답형",
        "points": [
            "<code>pam_pwquality.so</code>: <code>minlen=8 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1</code> -> 최소 8자, 숫자/대문자/소문자/특수문자 각 1자 이상 강제.",
            "<code>pam_faillock.so (또는 pam_tally2)</code>: <code>deny=5 unlock_time=600 even_deny_root</code> -> 5회 연속 인증 실패 시 계정 10분간(600초) 잠금.",
            "<strong>잠금 확인 및 해제:</strong> <code>faillock --user [계정]</code> 확인, <code>faillock --user [계정] --reset</code> 잠금 해제."
        ]
    })

    items.append({
        "id": "prac_content_13", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "DNS 캐시 포이즈닝 원리와 DNSSEC 서명 레코드 족보", "badge": "실기 단답·실무",
        "points": [
            "<strong>공격 원리:</strong> 비권한 캐시 DNS 서버에 질의를 보낸 후 권한 서버 응답 전에 무작위 Transaction ID(16비트)와 소스 포트를 대량 스푸핑 전송하여 조작된 IP를 캐싱시킴.",
            "<strong>DNSSEC 4대 핵심 레코드:</strong>",
            "- <code>RRSIG</code>: DNS 리소스 레코드 세트(RRset)에 대한 암호학적 디지털 전자서명 레코드.",
            "- <code>DNSKEY</code>: RRSIG 서명을 검증하기 위한 공인 공개키 레코드 (KSK: 키 서명 키, ZSK: 존 서명 키).",
            "- <code>DS (Delegation Signer)</code>: 상위 존(TLD)에 등록된 하위 존 KSK의 SHA 해시값으로 신뢰의 사슬(Chain of Trust) 형성.",
            "- <code>NSEC / NSEC3</code>: 존재하지 않는 도메인 질의(NXDOMAIN)에 대한 부존재 증명 레코드."
        ]
    })

    items.append({
        "id": "prac_content_14", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "윈도우 BitLocker 드라이브 암호화 및 TPM 부팅 무결성", "badge": "실기 실무",
        "points": [
            "<strong>BitLocker 작동 원리:</strong> 볼륨 전체를 AES-128/256으로 암호화하는 전체 디스크 암호화(FDE) 기술.",
            "<strong>TPM (Trusted Platform Module):</strong> 메인보드의 보안 칩에 키(VMK)를 저장하고 PCR(Platform Configuration Register) 레지스터로 부팅 펌웨어 무결성을 측정.",
            "부팅 시 펌웨어나 부트 로더가 변조되었을 경우 TPM이 복호화 키를 릴리즈하지 않아 BitLocker 복구 키 입력을 요구함."
        ]
    })

    items.append({
        "id": "prac_content_15", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "데이터베이스 암호화 3대 방식(API, Plug-in, TDE) 장단점", "badge": "실기 서술·실무",
        "points": [
            "<strong>API 방식:</strong> 애플리케이션 소스에서 암호화 API 호출 -> DB 서버 부하 없음, 애플리케이션 소스코드 수정 필요.",
            "<strong>Plug-in 방식:</strong> DBMS 내부에 플러그인(함수, 트리거)으로 설치 -> 애플리케이션 수정 최소화, DB 서버 연산 부하 증가.",
            "<strong>TDE (투명한 데이터 암호화) 방식:</strong> DBMS 커널 엔진이 파일/블록 단위로 자동 암·복호화 -> 소스코드 및 쿼리 수정 0%, 인덱스 검색 지원."
        ]
    })

    items.append({
        "id": "prac_content_16", "type": "content", "category": "law", "category_name": "디지털 포렌식 & 법률",
        "title": "KISA 표준 사이버 침해사고 대응 7단계 절차", "badge": "실기 서술·실무",
        "points": [
            "<strong>1단계 사고 전 준비:</strong> 보안 정책 수립, 관제 로그 수집 인프라 및 대응팀(CERT) 구성.",
            "<strong>2단계 사고 탐지:</strong> 침입탐지시스템(IDS/IPS), EDR, 방화벽 로그 분석을 통한 이상 징후 포착.",
            "<strong>3단계 초기 대응:</strong> 사고 통지, 침해 시스템 식별, 네트워크 물리적 격리(케이블 분리).",
            "<strong>4단계 대응 전략 수립:</strong> 사고 피해 규모 산정, 침해 원인 초기 진단, 법적 대응 여부 결정.",
            "<strong>5단계 사고 조사 및 분석:</strong> 휘발성 메모리 덤프, 디스크 이미징, 타임라인 분석, C2 IP 추적.",
            "<strong>6단계 복구 및 해결:</strong> 취약점 패치, 백도어 악성코드 제거, 무결성이 검증된 백업 데이터 복원.",
            "<strong>7단계 사후 검토 및 보고서 작성:</strong> 침해 원인 보고서 작성, 경영진 보고, 재발 방지 대책 수립."
        ]
    })

    items.append({
        "id": "prac_content_17", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "리눅스 메모리 상주 악성코드 복구 및 프로세스 역추적", "badge": "실기 실무",
        "points": [
            "공격자가 <code>rm -f /tmp/backdoor.sh</code>로 원본을 지우고 프로세스를 백그라운드로 실행한 경우:",
            "1. <code>ps -ef | grep backdoor</code> 또는 <code>lsof +L1</code>(Unlinked 오픈 파일 검색)로 PID 확인.",
            "2. <code>ls -l /proc/[PID]/exe</code> 확인 시 <code>(deleted)</code> 표시 확인.",
            "3. <code>cp /proc/[PID]/exe /tmp/recovered_malware</code> 명령어로 메모리에 매핑된 원본 바이너리 즉시 덤프 및 복구.",
            "4. <code>sha256sum /tmp/recovered_malware</code>로 해시값 산출 후 VirusTotal 분석."
        ]
    })

    items.append({
        "id": "prac_content_18", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "SSL/TLS 중간자 공격(MITM) 및 SSL Stripping 방어", "badge": "실기 단답·실무",
        "points": [
            "<strong>SSL Stripping 공격:</strong> 클라이언트와 서버 간의 HTTPS 연결을 가로채어 클라이언트에게는 일반 HTTP로 다운그레이드 통신하게 만드는 공격.",
            "<strong>방어 대책:</strong>",
            "- <code>HSTS (Strict-Transport-Security)</code> 헤더를 브라우저에 등록하여 클라이언트가 애초에 HTTP 접속을 시도하지 못하게 차단.",
            "- <code>HSTS Preload</code> 리스트에 도메인을 정식 등록하여 최초 접속(First-Visit) 시에도 무조건 HTTPS 강제.",
            "- 클라이언트 인증서 기반의 <code>mTLS (상호 TLS 인증)</code> 도입."
        ]
    })

    items.append({
        "id": "prac_content_19", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "Cross-Site Scripting (XSS) 3대 유형 및 다계층 방어", "badge": "실기 서술·실무",
        "points": [
            "<strong>Stored XSS:</strong> 악성 스크립트가 게시판 DB에 저장되어 불특정 다수 방문자에게 지속적 피해 발생 (가장 위험).",
            "<strong>Reflected XSS:</strong> 검색어 URL 파라미터 등에 악성 스크립트가 포함되어 서버 응답 페이지로 즉시 반사되는 공격.",
            "<strong>DOM-based XSS:</strong> 서버로 전송되지 않고 브라우저 클라이언트 JS(innerHTML, document.write)에서 DOM 조작 시 발생.",
            "<strong>방어:</strong> 출력 시 HTML Entity 인코딩, 세션 쿠키 <code>HttpOnly</code> 플래그 강제, <code>CSP (Content-Security-Policy)</code> 적용."
        ]
    })

    items.append({
        "id": "prac_content_20", "type": "content", "category": "law", "category_name": "디지털 포렌식 & 법률",
        "title": "클라우드 침해사고 대응 및 IAM 최소 권한 가이드라인", "badge": "실기 서술·실무",
        "points": [
            "<strong>Root 계정 보안:</strong> 일상 업무 사용 전면 금지, 하드웨어 보안 키(YubiKey 등) 기반 MFA 의무화.",
            "<strong>임시 자격증명:</strong> 영구적인 IAM User Access Key 발급을 금지하고 AssumeRole(STS 임시 토큰) 사용.",
            "<strong>최소 권한 정책:</strong> AdministratorAccess 및 Action: \"*\" 부여를 금지하고, 리소스 ARN별로 최소 권한 할당.",
            "<strong>클라우드 감사 로그:</strong> CloudTrail(API 호출 감사) 및 VPC Flow Logs(네트워크 흐름) 다중 리전 활성화 및 위·변조 방지 S3 보관."
        ]
    })

    # ==========================================
    # [필수 단답형 핵심 용어사전 30선]
    # ==========================================
    practical_terms = [
        ("find (-perm -4000)", "시스템", "SetUID가 설정된 실행 바이너리를 전수 검색하여 권한 상승 취약점을 탐지하는 리눅스 명령어."),
        ("netstat (-antp)", "시스템", "활성 TCP/UDP 네트워크 소켓, 수신 포트, PID 및 프로세스명을 조회하는 핵심 포트 점검 명령어."),
        ("umask (027)", "시스템", "신규 파일 생성 시 640(-rw-r-----), 디렉토리 생성 시 750(drwxr-x---) 권한을 강제 부여하는 마스크값."),
        ("chattr (+i / -i)", "시스템", "root 사용자라도 파일을 삭제, 수정, 이름 변경할 수 없도록 속성을 불변(Immutable) 상태로 잠그는 명령어."),
        ("lastlog (/var/log/lastlog)", "시스템", "시스템 내 모든 사용자의 최근 로그인 일시와 출발지 IP를 확인하는 바이너리 로그 조회 명령어."),
        ("tcpdump", "네트워크", "네트워크 인터페이스(eth0 등)를 통과하는 패킷의 헤더와 페이로드를 실시간 캡처 및 필터링하는 도구."),
        ("icacls", "시스템", "윈도우 NTFS 파일 시스템에서 파일 및 폴더의 접근 제어 목록(ACL) 권한을 명령줄에서 확인·수정하는 도구."),
        ("distance (Snort)", "네트워크", "직전 content 패턴 매칭 끝 지점으로부터 다음 패턴을 탐색할 상대적 시작 거리를 바이트 단위로 지정하는 Snort 옵션."),
        ("within (Snort)", "네트워크", "distance 지점부터 최대 몇 바이트 범위 안에서 다음 패턴을 찾아야 하는지 탐색 범위를 한정하는 Snort 옵션."),
        ("iptables REJECT", "네트워크", "접속 패킷을 차단할 때 송신자에게 ICMP unreachable 또는 TCP RST 거부 응답을 명시적으로 회신하는 타겟."),
        ("PreparedStatement", "웹/앱", "SQL 쿼리를 사전 컴파일하고 입력값을 파라미터로 안전하게 바인딩하여 SQL Injection을 원천 차단하는 인터페이스."),
        ("SameSite=Lax", "웹/앱", "타 사이트에서의 안전한 GET 최상위 링크 이동만 허용하고, 외부 POST 등 비인가 요청에서 쿠키 전송을 막는 CSRF 방어 속성."),
        ("Strict-Transport-Security (HSTS)", "웹/앱", "웹 브라우저가 평문 HTTP 연결을 일절 시도하지 않고 오직 HTTPS로만 통신하도록 강제하는 보안 헤더."),
        ("Content-Security-Policy (CSP)", "웹/앱", "브라우저에서 실행 가능한 스크립트, 스타일, 이미지 등의 신뢰 출처를 지정하여 XSS 공격을 방어하는 보안 헤더."),
        ("Volatility", "포렌식", "물리 RAM 메모리 덤프 파일을 파싱하여 프로세스 트리, 네트워크 소켓, 셸코드 등을 역공학 분석하는 메모리 포렌식 도구."),
        ("SBOM", "보안관리", "소프트웨어 공급망 보안을 위해 오픈소스 라이브러리, 패키지 버전, 의존성 관계를 기계 판독 가능하게 작성한 소프트웨어 자재 명세서."),
        ("SOAR", "보안관제", "보안 솔루션 경보를 통합하고 사전 정의된 플레이북(Playbook)에 따라 침해 대응 프로세스를 자동 오케스트레이션하는 관제 기술."),
        ("EDR", "시스템", "단말기(엔드포인트)의 프로세스 생성, 파일 변경, 네트워크 연결 행위를 실시간 모니터링하여 침해를 탐지·격리하는 솔루션."),
        ("SPAN (Port Mirroring)", "네트워크", "스위치 포트나 VLAN의 패킷을 네트워크 분석 장비(IDS, Wireshark)가 연결된 특정 모니터링 포트로 복제하는 기능."),
        ("MITRE ATT&CK", "보안관리", "실제 사이버 공격자의 공격 전술(Tactics), 기술(Techniques), 절차(Procedures)를 매트릭스로 집대성한 지식 프레임워크."),
        ("Perfect Forward Secrecy (PFS)", "암호학", "서버의 장기 개인키가 유출되더라도 일회성 임시 세션키 폐기를 통해 과거 암호화 통신의 복호화를 방지하는 암호학적 특성."),
        ("auditctl", "시스템", "리눅스 커널 감사 서브시스템(auditd)에 특정 시스템 콜이나 중요 파일(/etc/passwd) 감시 규칙을 실시간 등록하는 도구."),
        ("fail2ban", "시스템", "SSH 등에서 일정 횟수 이상 인증 실패 로그가 기록되면 방화벽(iptables)에 차단 룰을 동적으로 생성하여 무차별 대입을 막는 도구."),
        ("SecureRandom", "웹/앱", "선형 합동(LCG) 대신 암호학적으로 안전한 난수를 생성하여 예측 불가능한 세션 ID 및 솔트(Salt)를 발급하는 자바 클래스."),
        ("Chain of Custody (연계보관성)", "포렌식", "디지털 증거가 압수된 순간부터 법정 제출 시까지 취급자, 보관 장소, 일시를 연속적으로 기록 증명하는 포렌식 기본 원칙."),
        ("Open Redirect", "웹/앱", "사용자 입력 URL을 검증 없이 HTTP 302 리다이렉트 대상으로 사용하여 악성 피싱 사이트로 연결시키는 웹 취약점."),
        ("Tripwire", "시스템", "시스템 바이너리 및 설정 파일의 기준 해시값(SHA-256)을 저장해 두고 변경 여부를 감시하여 악성 변조를 탐지하는 HIDS 도구."),
        ("Order of Volatility", "포렌식", "디지털 증거 수집 시 휘발성이 높은 순서(레지스터/캐시 -> RAM -> 네트워크 연결 -> 디스크)대로 수집해야 한다는 원칙."),
        ("CISO 겸직금지", "법률", "자산 5조 원 이상 또는 자산 5천억 이상 ISMS 의무 대상 기업의 CISO는 정보기술(CIO) 등 타 임원 직무를 겸직할 수 없도록 한 규정."),
        ("Zero Trust (Never Trust, Always Verify)", "보안관리", "내부망이라 할지라도 결코 신뢰하지 않고 모든 사용자, 기기, 세션에 대해 지속적인 인증과 최소 권한을 부여하는 보안 철학.")
    ]

    for idx, (term, cat, desc) in enumerate(practical_terms, start=1):
        items.append({
            "id": f"prac_term_{idx:02d}",
            "type": "term",
            "category": "system" if cat == "시스템" else ("network" if cat == "네트워크" else ("app" if cat == "웹/앱" else ("law" if cat in ("법률", "포렌식") else "general"))),
            "category_name": f"실기 단답형 용어 ({cat})",
            "title": f"[실기 단답] {term}",
            "term": term,
            "badge": "단답형 족보",
            "points": [desc]
        })

    return {
        "title": "2026 이기적 정보보안기사 실기 핵심 실무 가이드 & 단답형 족보 (총 50선)",
        "items": items
    }

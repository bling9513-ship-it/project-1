# -*- coding: utf-8 -*-
"""
practical_summary.py
2026 이기적 정보보안기사 필기+실기 올인원 실기 편제 기준
- 실기 단답형 핵심 명령어·설정 족보 (내용별 및 용어별)
- 실무형 침해사고 분석 & SW 개발보안(시큐어코딩) 47개 핵심
"""

def get_practical_summary():
    items = []

    # 단답형 핵심 족보 (내용별)
    items.append({
        "id": "prac_content_01",
        "type": "content",
        "category": "system",
        "category_name": "실기 단답형",
        "title": "리눅스/유닉스 침해사고 분석 및 점검 필수 명령어 10선",
        "badge": "단답형 핵심족보",
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
        "id": "prac_content_02",
        "type": "content",
        "category": "system",
        "category_name": "실기 단답형",
        "title": "서버 및 네트워크 주요 보안 설정 파라미터 족보",
        "badge": "단답형 핵심족보",
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
        "id": "prac_content_03",
        "type": "content",
        "category": "app",
        "category_name": "실기 서술·실무",
        "title": "웹 침해사고 로그 분석(SQLi·Path Traversal) 및 Snort 룰 작성",
        "badge": "실무 침해사고 분석",
        "points": [
            "<strong>Union-Based SQLi 로그:</strong> <code>GET /view.php?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users--%20 HTTP/1.1</code> -> 공백 인코딩(%20), UNION SELECT 키워드, information_schema 조회 식별.",
            "<strong>Path Traversal 로그:</strong> <code>GET /down.jsp?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1</code> -> %2e%2e%2f(상위 경로 ../) 디코딩 및 시스템 기밀 파일(/etc/passwd) 탈취 패턴 분석.",
            "<strong>WebShell 업로드 탐지 Snort 룰 작성 표준:</strong>",
            "<code>alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell JSP Upload\"; content:\"multipart/form-data\"; content:\".jsp\"; nocase; sid:1000001;)</code>",
            "<code>alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell Execution - cmd.jsp\"; content:\"cmd.jsp\"; nocase; content:\"cmd=\"; distance:0; sid:1000002;)</code>"
        ]
    })

    items.append({
        "id": "prac_content_04",
        "type": "content",
        "category": "app",
        "category_name": "실기 서술·실무",
        "title": "SW 개발보안(시큐어코딩) 47개 보안약점 핵심 가이드",
        "badge": "시큐어코딩 가이드",
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
        "id": "prac_content_05",
        "type": "content",
        "category": "law",
        "category_name": "실기 서술·실무",
        "title": "디지털 포렌식 5대 원칙 및 휘발성 데이터 수집 순서",
        "badge": "포렌식 & 침해대응",
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

    return {
        "title": "2026 이기적 정보보안기사 실기 핵심 실무 가이드 & 단답형 족보",
        "items": items
    }

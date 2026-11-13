# -*- coding: utf-8 -*-
"""
practical_questions.py
이기적 2026 정보보안기사 필기+실기 올인원 실기 편제 기준
- 1회 단답형 핵심 족보 (25문항: 명령어, 도구, 알고리즘, 프로토콜, 법률 핵심)
- 2회 서술·실무형 침해사고 분석 (25문항: Apache/Nginx 로그, Snort 룰, iptables, 시큐어코딩, 시스템 진단)
총 50문항
"""

def get_practical_questions():
    q = []

    # ==========================================
    # [1회] 실기 단답형 핵심 족보 (25문항)
    # ==========================================
    q.append({
        "id": "IP1_Q1", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스 환경에서 일반 파일 기본 권한 666, 디렉토리 기본 권한 777일 때, 파일은 640(-rw-r-----), 디렉토리는 750(drwxr-x---)으로 생성되도록 지정하는 umask 값은 무엇인가?",
        "options": ["022", "027", "077", "037"],
        "answer": 2, "explanation": "디렉토리(777 - 027 = 750), 파일(666 - 027 = 640, 실행비트 미부여)을 만족하는 보안 표준 umask 값은 027입니다."
    })
    q.append({
        "id": "IP1_Q2", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 아파치(Apache) 웹 서버에서 디렉토리 인덱싱(디렉토리 내 파일 목록 전체 노출) 취약점을 차단하기 위해 httpd.conf 설정 파일의 Options 지시자에서 반드시 제거해야 하거나 앞에 '-'를 붙여야 하는 옵션 명칭은?",
        "options": ["Indexes", "FollowSymLinks", "Includes", "ExecCGI"],
        "answer": 1, "explanation": "Options -Indexes 또는 Indexes 옵션을 제거해야 디렉토리 목록 노출(Directory Listing)을 방지할 수 있습니다."
    })
    q.append({
        "id": "IP1_Q3", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스 시스템에서 현재 활성화된 네트워크 연결 상태, 열린 포트 번호, 그리고 해당 포트를 사용 중인 프로세스 ID(PID)와 프로그램 이름을 숫자로 확인하기 위한 netstat 명령어 옵션 조합은?",
        "options": ["netstat -antp", "netstat -r", "netstat -i", "netstat -s"],
        "answer": 1, "explanation": "-a(모든 소켓), -n(IP/포트 숫자로 표시), -t(TCP), -p(프로세스 ID/이름 표시) 옵션인 'netstat -antp'가 침해사고 분석의 기본 명령어입니다."
    })
    q.append({
        "id": "IP1_Q4", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 최근 24시간 이내에 수정(Modify)된 파일을 전체 루트 디렉토리(/)부터 검색하기 위한 find 명령어의 올바른 옵션은?",
        "options": ["find / -mtime -1", "find / -atime +1", "find / -ctime 1", "find / -perm 777"],
        "answer": 1, "explanation": "-mtime -1은 수정된 지 1일(24시간) 이내인 파일을 의미합니다. (+1: 24시간 이전, 1: 정확히 24~48시간 사이)"
    })
    q.append({
        "id": "IP1_Q5", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] TCP Wrapper 접근 제어 파일(/etc/hosts.allow, /etc/hosts.deny)에서 동일한 IP나 대역이 양쪽 파일 모두에 정의되어 있을 때 적용되는 우선순위 규칙은?",
        "options": [
            "/etc/hosts.allow 파일이 먼저 적용되어 허용된다.",
            "/etc/hosts.deny 파일이 먼저 적용되어 차단된다.",
            "나중에 수정된 파일이 우선한다.",
            "동일하게 충돌 시 무조건 차단된다."
        ],
        "answer": 1, "explanation": "TCP Wrapper는 /etc/hosts.allow를 먼저 확인하고 일치하면 즉시 허용하며, 없을 때 hosts.deny를 확인합니다. 둘 다 없으면 기본 허용됩니다."
    })
    q.append({
        "id": "IP1_Q6", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스 iptables 방화벽에서 외부에서 서버의 22번(SSH) 포트로 들어오는 특정 IP(192.168.1.100)의 모든 TCP 접속 패킷을 폐기(차단)하고 로그를 남기지 않기 위한 명령어로 올바른 것은?",
        "options": [
            "iptables -A INPUT -p tcp -s 192.168.1.100 --dport 22 -j DROP",
            "iptables -D INPUT -p tcp -s 192.168.1.100 --sport 22 -j REJECT",
            "iptables -I OUTPUT -p tcp -d 192.168.1.100 --dport 22 -j ACCEPT",
            "iptables -A FORWARD -p tcp -s 192.168.1.100 -j DROP"
        ],
        "answer": 1, "explanation": "-A INPUT(인바운드 체인 추가), -p tcp(프로토콜), -s(출발지 IP), --dport 22(목적지 포트), -j DROP(폐기)이 정확한 문법입니다."
    })
    q.append({
        "id": "IP1_Q7", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] Snort IDS 규칙에서 패킷 페이로드 내 바이너리 16진수 바이트열(예: 0x90 0x90 NOP Sled)을 탐지하기 위해 content 옵션 안에서 바이트열을 감싸는 기호는?",
        "options": ["파이프 (|...|)", "따옴표 (\"...\")", "대괄호 ([...])", "중괄호 ({...})"],
        "answer": 1, "explanation": "Snort에서 바이너리 바이트값은 파이프(|) 기호로 감쌉니다. 예: content:\"|90 90 90 90|\";"
    })
    q.append({
        "id": "IP1_Q8", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스에서 각 사용자별 크론탭(crontab) 작업 설정 파일이 저장되는 표준 디렉토리 경로는?",
        "options": ["/var/spool/cron/", "/etc/cron.hourly/", "/var/log/cron/", "/usr/bin/crontab"],
        "answer": 1, "explanation": "각 사용자별 crontab 설정은 /var/spool/cron/ 또는 /var/spool/cron/crontabs/ 디렉토리에 사용자 계정명 파일로 저장됩니다."
    })
    q.append({
        "id": "IP1_Q9", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 시스템 명령어 실행 취약점(Command Injection)에서 한 줄에 여러 명령어를 연속으로 실행하거나 앞선 명령어의 성공 여부와 상관없이 뒷 명령어를 실행시키는 셸 메타문자는?",
        "options": ["; (세미콜론) 또는 | (파이프)", "* (와일드카드)", "> (리디렉션)", "$ (변수참조)"],
        "answer": 1, "explanation": "세미콜론(;)은 이전 명령 종료 후 다음 명령을 순차 실행하며, 파이프(|)는 이전 명령어의 출력을 다음 명령어로 넘겨 임의 명령을 실행하게 만듭니다."
    })
    q.append({
        "id": "IP1_Q10", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 자바 시큐어코딩에서 XSS 공격을 방지하기 위해 사용자 입력 문자 중 HTML 특수문자 '<', '>', '&', '\"', '\\''를 안전하게 치환하는 것을 무엇이라 하는가?",
        "options": ["HTML 인코딩 (HTML Entity 치환)", "Base64 인코딩", "URL 인코딩", "해싱"],
        "answer": 1, "explanation": "&lt;, &gt;, &amp;, &quot;, &#x27; 등으로 치환하는 HTML Entity 인코딩이 XSS 방어의 필수 조치입니다."
    })
    q.append({
        "id": "IP1_Q11", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 개인정보보호법 제34조에 따라 개인정보 유출 시 정보주체에게 지체 없이 통지해야 하는 법정 필수 통지 항목 5가지에 해당하지 않는 것은?",
        "options": [
            "유출된 개인정보의 항목",
            "유출된 시점과 그 경위",
            "유출 사고를 일으킨 해커의 신원 및 IP 주소",
            "정보주체가 취할 수 있는 조치 및 피해신고 접수처",
            "개인정보처리자의 대응조치 및 피해 구제절차"
        ],
        "answer": 3, "explanation": "법정 5대 통지사항은 ①유출 항목, ②유출 시점과 경위, ③피해 최소화 조치, ④대응조치 및 구제절차, ⑤담당부서 및 연락처입니다. 해커 신원은 포함되지 않습니다."
    })
    q.append({
        "id": "IP1_Q12", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 디지털 포렌식의 5대 기본 원칙 중 '수집된 디지털 증거가 최초 발견 및 압수 시점부터 법정에 제출될 때까지 위·변조되지 않았음'을 입증하는 원칙은?",
        "options": ["무결성의 원칙", "정당성의 원칙", "재현성의 원칙", "신속성의 원칙", "연계보관성의 원칙 (Chain of Custody)"],
        "answer": 1, "explanation": "무결성의 원칙(Integrity)은 해시값(MD5, SHA-256) 비교를 통해 증거가 일체 수정·변조되지 않았음을 입증하는 원칙입니다."
    })
    q.append({
        "id": "IP1_Q13", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스 시스템에서 sshd_config 파일 설정 중 root 계정의 원격 직접 접속을 차단하기 위한 설정 지시자와 파라미터 값은?",
        "options": ["PermitRootLogin no", "AllowUsers root", "DenyUsers guest", "PasswordAuthentication no"],
        "answer": 1, "explanation": "sshd_config 파일에 'PermitRootLogin no'를 설정하여 관리자 계정의 무차별 대입 직접 침투를 차단합니다."
    })
    q.append({
        "id": "IP1_Q14", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 웹 서버의 보안 설정을 위해 서버의 상세 소프트웨어 버전(예: Apache/2.4.52) 정보가 HTTP 응답 헤더(Server:)에 노출되지 않도록 Apache에서 설정하는 지시자는?",
        "options": ["ServerTokens Prod 및 ServerSignature Off", "ServerName localhost", "Timeout 60", "KeepAlive Off"],
        "answer": 1, "explanation": "ServerTokens Prod는 Server 헤더에 단순히 'Apache'만 출력하고 세부 OS/모듈 버전을 숨기며, ServerSignature Off는 에러 페이지의 서명을 제거합니다."
    })
    q.append({
        "id": "IP1_Q15", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스 /etc/login.defs 파일에서 패스워드의 최대 사용 기간(일수)과 최소 사용 기간을 지정하는 지시자 명칭의 조합은?",
        "options": ["PASS_MAX_DAYS 및 PASS_MIN_DAYS", "MAX_PASS_AGE", "PASS_WARN_AGE", "ACCOUNT_LOCK_DAYS"],
        "answer": 1, "explanation": "/etc/login.defs에서 PASS_MAX_DAYS(최대 유효일수, 예: 90), PASS_MIN_DAYS(최소 변경간격일수), PASS_MIN_LEN(최소길이) 등을 정의합니다."
    })
    q.append({
        "id": "IP1_Q16", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] KISA 주요정보통신기반시설 기술적 취약점 분석·평가 기준에서 유닉스 root 계정의 환경변수 파일(.profile, .bashrc 등)의 PATH 설정 시 보안상 가장 위험하여 반드시 제거해야 하는 문자는?",
        "options": [
            "현재 디렉토리를 의미하는 '.'(마침표) 또는 빈 경로(::)",
            "/usr/bin",
            "/bin",
            "/sbin"
        ],
        "answer": 1, "explanation": "PATH 환경변수에 현재 디렉토리('.')가 앞에 포함되어 있으면 악의적인 공격자가 해당 디렉토리에 트로이목마 명령어(ls 등)를 두고 root가 실행하도록 유도할 수 있습니다."
    })
    q.append({
        "id": "IP1_Q17", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 오픈SSL(OpenSSL)에서 TLS 암호화 통신 시 클라이언트와 서버 간 연결 유지를 위한 하트비트 확장 프로토콜의 버퍼 경계 검증 미흡으로 서버의 메모리 데이터가 평문으로 유출되었던 치명적 취약점 명칭은?",
        "options": ["Heartbleed (CVE-2014-0160)", "POODLE", "Shellshock", "EternalBlue", "Log4Shell"],
        "answer": 1, "explanation": "Heartbleed 취약점은 OpenSSL의 Heartbeat 요청 패킷 길이 검증 누락으로 최대 64KB의 프로세스 메모리(비밀키, 세션쿠키 등)가 평문으로 유출되는 취약점입니다."
    })
    q.append({
        "id": "IP1_Q18", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스에서 패스워드 무차별 대입 공격(Brute Force)을 방어하기 위해 /etc/pam.d/system-auth에 계정 잠금 모듈을 설정할 때 사용하는 PAM 모듈 이름은?",
        "options": ["pam_faillock.so (또는 pam_tally2.so)", "pam_unix.so", "pam_rootok.so", "pam_env.so"],
        "answer": 1, "explanation": "계정 로그인 실패 횟수 초과 시 잠금(lock)을 처리하는 표준 모듈은 pam_faillock.so (최신 RHEL) 또는 pam_tally2.so (이전 버전)입니다."
    })
    q.append({
        "id": "IP1_Q19", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 윈도우 시스템에서 파일 및 폴더의 공유 권한 및 NTFS 접근 제어 목록(ACL)을 커맨드라인에서 확인하고 수정하기 위해 사용하는 표준 명령어는?",
        "options": ["icacls (또는 cacls)", "net share", "attrib", "takeown"],
        "answer": 1, "explanation": "icacls는 윈도우 파일/디렉토리의 DACL 및 SACL 접근 권한을 확인하고 부여·제거하는 핵심 보안 명령어입니다."
    })
    q.append({
        "id": "IP1_Q20", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스에서 디스크 용량 고갈로 인한 시스템 불능을 막기 위해 사용자별, 그룹별로 사용할 수 있는 디스크 공간 및 파일 개수(i-node)를 제한하는 기능은?",
        "options": ["Disk Quota (디스크 쿼터)", "LVM", "RAID", "Swap Partition"],
        "answer": 1, "explanation": "디스크 쿼터(Quota)는 사용자/그룹의 디스크 블록 사용량 및 아이노드 생성 수를 제한하여 DoS를 방어합니다."
    })
    q.append({
        "id": "IP1_Q21", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 침해사고 분석 시 살아있는(Live) 시스템의 휘발성 데이터(Volatile Data) 수집 시 보존 순서(Order of Volatility)에서 가장 먼저 수집해야 하는 것은?",
        "options": ["CPU 레지스터 및 캐시 메모리", "물리적 RAM 메모리", "네트워크 상태 정보", "하드디스크 파일 시스템"],
        "answer": 1, "explanation": "휘발성 데이터 수집 순서는 레지스터/캐시 -> 라우팅테이블/ARP캐시/프로세스테이블 -> 물리 메모리(RAM) -> 임시 파일 -> 디스크 순입니다."
    })
    q.append({
        "id": "IP1_Q22", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 유닉스 시스템에서 계정의 셸(Shell)이 '/bin/false' 또는 '/sbin/nologin'으로 설정되어 있는 계정의 보안적 의미는?",
        "options": [
            "시스템 대화형 로그인이 불가능한 서비스 전용 데몬 계정이다.",
            "최고 관리자 root 권한을 위임받은 계정이다.",
            "임시 비밀번호가 발급된 계정이다.",
            "SSH 원격 접속만 가능한 계정이다."
        ],
        "answer": 1, "explanation": "/sbin/nologin 및 /bin/false는 서비스 구동용 데몬 계정이 대화형 터미널 셸을 획득하지 못하도록 로그인 접근을 원천 차단하는 설정입니다."
    })
    q.append({
        "id": "IP1_Q23", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 패킷 덤프 도구인 tcpdump에서 192.168.1.50 IP와 통신하는 모든 트래픽 중 포트가 80번이 아닌 트래픽만을 필터링하는 옵션 표현식은?",
        "options": [
            "tcpdump host 192.168.1.50 and not port 80",
            "tcpdump -i eth0 port 80",
            "tcpdump src 192.168.1.50 or port 80",
            "tcpdump dst 192.168.1.50"
        ],
        "answer": 1, "explanation": "BPF(Berkeley Packet Filter) 문법에 따라 'host 192.168.1.50 and not port 80'으로 조합합니다."
    })
    q.append({
        "id": "IP1_Q24", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 데이터 무결성 검증을 위해 리눅스 환경에서 특정 파일(sample.tar.gz)의 SHA-256 해시값을 생성하고 검증하는 표준 명령어는?",
        "options": ["sha256sum sample.tar.gz", "md5sum -c", "hash -sha256", "cksum -a 256"],
        "answer": 1, "explanation": "리눅스에서는 sha256sum, sha1sum, md5sum 명령어를 사용하여 표준 체크섬 해시를 계산 및 검증합니다."
    })
    q.append({
        "id": "IP1_Q25", "category": "infosec_practical", "exam": 1, "exam_name": "1회 실기 단답형 핵심 족보",
        "subject_id": 1, "subject_name": "1영역: 단답형 핵심 족보",
        "question": "[단답형] 리눅스 파일 시스템에서 파일에 설정할 경우 소유자나 root라 할지라도 파일을 삭제, 수정, 이름 변경하거나 링크를 걸 수 없도록 잠그는 chattr 명령어의 불변(Immutable) 속성 플래그는?",
        "options": ["+i (Immutable)", "+a (Append only)", "+s (Secure deletion)", "+u (Undeletable)"],
        "answer": 1, "explanation": "'chattr +i 파일명'을 적용하면 파일에 불변 속성이 부여되어 백도어 침투나 로그 삭제를 방지할 수 있습니다."
    })

    # ==========================================
    # [2회] 서술·실무형 침해사고 분석 (25문항)
    # ==========================================
    q.append({
        "id": "IP2_Q1", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[로그 분석] 다음 아파치 access.log 기록을 분석하여 시도된 공격 유형을 식별하시오.\n\n192.168.10.15 - - [12/Nov/2026:14:22:01 +0900] \"GET /board/view.php?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users--%20 HTTP/1.1\" 200 4521\n192.168.10.15 - - [12/Nov/2026:14:22:05 +0900] \"GET /board/view.php?id=1%20UNION%20SELECT%201,table_name,3%20FROM%20information_schema.tables--%20 HTTP/1.1\" 200 8920",
        "options": [
            "Union-Based SQL Injection (SQL 인젝션)",
            "Cross-Site Scripting (XSS)",
            "Directory Traversal (경로 조작)",
            "Command Injection (명령어 삽입)"
        ],
        "answer": 1, "explanation": "id 파라미터에 UNION SELECT 구문과 information_schema 메타데이터를 결합하여 사용자 계정과 DB 스키마를 유출하는 전형적인 Union-Based SQL Injection 공격입니다."
    })
    q.append({
        "id": "IP2_Q2", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[로그 분석] 다음 웹 서버 로그를 분석하여 공격자가 탈취하고자 한 파일과 시도된 공격 기법을 판단하시오.\n\n10.0.0.88 - - [12/Nov/2026:15:30:12 +0900] \"GET /download.jsp?file=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1\" 200 2410",
        "options": [
            "경로 조작(Path Traversal) 공격을 통한 리눅스 계정 파일(/etc/passwd) 열람",
            "파일 업로드를 통한 웹셸 실행",
            "SQL 인젝션을 통한 관리자 로그인 우회",
            "서버사이드 템플릿 인젝션(SSTI)"
        ],
        "answer": 1, "explanation": "%2e%2e%2f는 URL 디코딩 시 '../../'로 변환되며, 상위 디렉토리로 이동하여 시스템의 /etc/passwd 파일을 불법 열람하는 Path Traversal(디렉토리 순회) 공격입니다."
    })
    q.append({
        "id": "IP2_Q3", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 3, "subject_name": "3영역: 시큐어코딩 진단",
        "question": "[시큐어코딩] 다음 취약한 자바 코드의 결함을 진단하고 가장 안전한 수정 코드로 올바른 것은?\n\n[취약한 코드]\nString sql = \"SELECT * FROM member WHERE id = '\" + userID + \"' AND pw = '\" + userPW + \"'\";\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(sql);",
        "options": [
            "PreparedStatement pstmt = conn.prepareStatement(\"SELECT * FROM member WHERE id = ? AND pw = ?\");\npstmt.setString(1, userID);\npstmt.setString(2, userPW);\nResultSet rs = pstmt.executeQuery();",
            "String sql = \"SELECT * FROM member WHERE id = '\" + userID.replace(\"'\", \"\") + \"'\";",
            "Statement stmt = conn.createStatement(ResultSet.TYPE_SCROLL_INSENSITIVE, ResultSet.CONCUR_READ_ONLY);",
            "String sql = URLDecoder.decode(userID, \"UTF-8\");"
        ],
        "answer": 1, "explanation": "문자열 결합 방식의 Statement는 SQL 인젝션에 취약하므로, 위치 홀더(?)를 사용하는 PreparedStatement 객체에 파라미터 바인딩(setString)을 수행해야 안전합니다."
    })
    q.append({
        "id": "IP2_Q4", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[Snort 룰 분석] 다음 침입탐지 규칙이 탐지하고자 하는 악성 행위로 올바른 것은?\n\nalert tcp any any -> 192.168.1.100 80 (msg:\"WebShell Detection - cmd.jsp\"; content:\"cmd.jsp\"; nocase; content:\"cmd=\"; distance:0; sid:2000001;)",
        "options": [
            "웹 서버(80 포트)로 업로드된 jsp 웹셸(cmd.jsp)을 통한 시스템 명령어 실행 시도",
            "외부로의 데이터 대량 유출 시도",
            "DNS 증폭 반사 공격",
            "SSH 무차별 대입 공격"
        ],
        "answer": 1, "explanation": "URI나 요청에 cmd.jsp 웹셸 파일과 명령어 파라미터(cmd=)가 포함된 웹셸 악용 행위를 탐지하는 시그니처입니다."
    })
    q.append({
        "id": "IP2_Q5", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[방화벽 설정] 내부 사설망(192.168.1.0/24)에서 인터넷 웹 서핑(80, 443 포트)만을 허용하고 그 외의 모든 아웃바운드 트래픽을 차단하는 iptables 규칙 세트로 올바른 것은?",
        "options": [
            "iptables -P FORWARD DROP\niptables -A FORWARD -s 192.168.1.0/24 -p tcp -m multiport --dports 80,443 -j ACCEPT\niptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT",
            "iptables -A INPUT -p tcp --dport 80 -j DROP",
            "iptables -P INPUT ACCEPT",
            "iptables -F OUTPUT"
        ],
        "answer": 1, "explanation": "기본 정책(Policy)을 DROP으로 설정한 후 80, 443 포트 허용 및 세션 응답(ESTABLISHED, RELATED)을 허용하는 상태추적 방화벽 구성이 정답입니다."
    })
    q.append({
        "id": "IP2_Q6", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 3, "subject_name": "3영역: 시큐어코딩 진단",
        "question": "[시큐어코딩] 파일 업로드 취약점 방어를 위한 3대 안전수칙 중 확장자 검증 시 적용해야 할 올바른 정책은?",
        "options": [
            "화이트리스트(Whitelist) 방식으로 허용할 확장자(jpg, png, pdf 등)만 엄격히 허용",
            "블랙리스트 방식으로 jsp, php, asp 등만 금지",
            "확장자를 검사하지 않고 Content-Type만 신뢰",
            "클라이언트 측 자바스크립트로만 확장자 검사"
        ],
        "answer": 1, "explanation": "블랙리스트 방식은 우회(jspx, php5, phtml 등)가 쉬우므로, 허용된 안전한 확장자만을 허용하는 화이트리스트 검증을 서버사이드에서 수행해야 합니다."
    })
    q.append({
        "id": "IP2_Q7", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[시스템 분석] 리눅스 시스템 침해사고 분석 중 /etc/passwd 파일에 다음과 같은 계정이 발견되었다. 이 계정의 보안 위험성을 가장 올바르게 지적한 것은?\n\nhacker:x:0:0:root:/root:/bin/bash",
        "options": [
            "UID가 0으로 설정되어 있어 root와 완전히 동일한 최고 관리자 권한을 가진 백도어 계정이다.",
            "일반 사용자 계정으로 아무런 위험이 없다.",
            "비밀번호가 x로 잠겨 있어 로그인이 불가능하다.",
            "홈 디렉토리가 잘못 설정된 단순 설정 오류이다."
        ],
        "answer": 1, "explanation": "UID가 0이면 계정 이름에 상관없이 리눅스 커널은 최고 관리자 root 권한으로 인식하므로 전형적인 슈퍼유저 권한 백도어 계정입니다."
    })
    q.append({
        "id": "IP2_Q8", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[로그 분석] 리눅스 /var/log/secure 로그에서 다음과 같은 이력이 지속적으로 기록될 때 분석 내용으로 올바른 것은?\n\nFailed password for invalid user admin from 203.0.113.50 port 45211 ssh2\nFailed password for root from 203.0.113.50 port 45215 ssh2\nFailed password for test from 203.0.113.50 port 45220 ssh2",
        "options": [
            "외부 IP(203.0.113.50)로부터 SSH 계정 무차별 대입(Brute Force / Dictionary) 공격이 진행 중이다.",
            "정상적인 관리자의 일상 접속이다.",
            "웹 서버 서비스 거부 공격이다.",
            "ARP 스푸핑 공격이다."
        ],
        "answer": 1, "explanation": "동일 IP에서 다수의 관리자 및 기본 계정명으로 짧은 시간 동안 SSH 비밀번호 인증 실패가 반복되는 전형적인 SSH 사전 대입 공격 로그입니다."
    })
    q.append({
        "id": "IP2_Q9", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 3, "subject_name": "3영역: 시큐어코딩 진단",
        "question": "[시큐어코딩] 게시판 본문 출력 시 공격자가 삽입한 `<script>alert(document.cookie);</script>` 스크립트의 실행을 방어하기 위해 JSTL에서 사용하는 안전한 태그 출력 방식은?",
        "options": [
            "<c:out value=\"${board.content}\" escapeXml=\"true\" />",
            "<c:out value=\"${board.content}\" escapeXml=\"false\" />",
            "<%= request.getParameter(\"content\") %>",
            "<jsp:getProperty name=\"board\" property=\"content\" />"
        ],
        "answer": 1, "explanation": "JSTL의 <c:out> 태그는 기본적으로 escapeXml=\"true\" 속성이 적용되어 HTML 특수문자를 자동 엔티티 인코딩하여 XSS를 방어합니다."
    })
    q.append({
        "id": "IP2_Q10", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 4, "subject_name": "4영역: 서술형/관리",
        "question": "[서술형] 개인정보 안전성 확보조치 기준에 따라 개인정보취급자가 개인정보처리시스템에 접속하여 개인정보를 다운로드한 경우 취해야 할 사후 조치로 올바른 것은?",
        "options": [
            "다운로드 사유를 반드시 확인하고 기록·보관하여야 한다.",
            "다운로드 즉시 해당 개인정보를 원격 서버에서 삭제해야 한다.",
            "다운로드 내역은 별도 로그 없이 관리자 구두 승인만 받으면 된다.",
            "다운로드는 사유와 무관하게 전면 금지된다."
        ],
        "answer": 1, "explanation": "개인정보 다운로드 시에는 유출 사고를 방지하고 오남용을 추적하기 위해 다운로드 사유 확인 및 승인 절차를 수립하고 접속기록에 남겨야 합니다."
    })
    q.append({
        "id": "IP2_Q11", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[서술형] 리눅스 시스템에서 취약점 점검 스크립트를 작성할 때, 주요 환경변수 및 시스템 설정 파일(/etc/passwd, /etc/shadow)의 적절한 소유자 및 권한 설정 기준으로 올바른 것은?",
        "options": [
            "/etc/passwd: root 소유, 644 이하 / /etc/shadow: root 소유, 400 또는 000",
            "/etc/passwd: 777 / /etc/shadow: 777",
            "/etc/passwd: 666 / /etc/shadow: 644",
            "/etc/passwd: 755 / /etc/shadow: 666"
        ],
        "answer": 1, "explanation": "kisa 주요기반시설 점검 가이드에 따라 /etc/passwd는 root 소유 644(-rw-r--r--), 패스워드 해시가 들어있는 /etc/shadow는 root 소유 400(-r--------) 이하로 제한해야 안전합니다."
    })
    q.append({
        "id": "IP2_Q12", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 3, "subject_name": "3영역: 시큐어코딩 진단",
        "question": "[시큐어코딩] 무작위 난수 생성이 필요한 세션 ID, 비밀번호 재설정 토큰, 암호화 키 생성 시 취약한 'java.util.Random' 대신 사용해야 하는 암호학적으로 안전한 난수 생성 클래스는?",
        "options": ["java.security.SecureRandom", "Math.random()", "System.currentTimeMillis()", "UUID.randomUUID()"],
        "answer": 1, "explanation": "SecureRandom은 예측 불가능한 엔트로피 시드를 사용하여 난수를 생성하므로 암호학적 토큰 및 키 생성에 필수적입니다."
    })
    q.append({
        "id": "IP2_Q13", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[실무 설정] Nginx 웹 서버에서 클릭재킹(Clickjacking) 공격을 방지하기 위해 응답 헤더에 타 사이트의 프레임 삽입을 전면 차단하는 지시자 설정은?",
        "options": [
            "add_header X-Frame-Options DENY always;",
            "add_header X-Frame-Options ALLOW-FROM *;",
            "add_header X-XSS-Protection \"1; mode=block\";",
            "proxy_set_header Host $host;"
        ],
        "answer": 1, "explanation": "Nginx에서 'add_header X-Frame-Options DENY always;' 설정을 통해 어떠한 사이트에서도 해당 웹 페이지를 iframe 등에 로드할 수 없도록 강제합니다."
    })
    q.append({
        "id": "IP2_Q14", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[포렌식 분석] 윈도우 프리페치(Prefetch, .pf) 파일이 수사관 및 포렌식 분석가에게 제공하는 가장 결정적인 정보는 무엇인가?",
        "options": [
            "응용 프로그램의 최근 실행 시간, 실행 횟수, 실행 시 로드된 참조 파일 목록",
            "사용자가 입력한 패스워드 평문",
            "삭제된 파일의 완전한 바이너리 원본",
            "네트워크 카드 MAC 주소"
        ],
        "answer": 1, "explanation": "윈도우 프리페치(C:\\Windows\\Prefetch)는 응용 프로그램의 최초 및 최근 실행 일시(최대 8회), 실행 횟수, 실행 파일 경로와 DLL 목록을 담고 있어 악성코드 실행 증적 확보에 핵심입니다."
    })
    q.append({
        "id": "IP2_Q15", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[네트워크 분석] SYN Flooding 공격을 탐지하기 위해 netstat 명령어 실행 결과 특정 포트(80)에 비정상적으로 많이 쌓여 있는 TCP 연결 상태값은?",
        "options": ["SYN_RECEIVED (SYN_RECV)", "ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT", "FIN_WAIT_1"],
        "answer": 1, "explanation": "SYN 요청을 받고 SYN/ACK를 보낸 후 최종 ACK를 대기하는 반개방 상태가 지속될 때 SYN_RECV(SYN_RECEIVED) 상태의 소켓이 폭증합니다."
    })
    q.append({
        "id": "IP2_Q16", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 3, "subject_name": "3영역: 시큐어코딩 진단",
        "question": "[시큐어코딩] 파일 다운로드 취약점을 방지하기 위해 파일 경로 처리 시 적용해야 할 시큐어코딩 기법으로 올바른 것은?",
        "options": [
            "사용자가 전달한 파일명에서 '..', '/', '\\' 등의 경로 조작 문자를 제거하고 베이스 디렉토리와 결합하여 검증",
            "사용자 입력 파라미터를 그대로 new File(param)에 전달",
            "GET 대신 POST 방식을 적용",
            "파일 크기를 10MB로 제한"
        ],
        "answer": 1, "explanation": "파일 다운로드 시 파라미터에서 상위 경로 탐색 문자(../)를 필터링하거나, File.getCanonicalPath()로 정규화된 경로가 허용된 다운로드 루트 디렉토리 내에 위치하는지 검증해야 합니다."
    })
    q.append({
        "id": "IP2_Q17", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[시스템 점검] 리눅스 시스템에서 불필요하거나 취약한 원격 서비스 데몬 중 평문(Cleartext)으로 패스워드와 명령어를 전송하므로 비활성화해야 하는 서비스 3종의 조합은?",
        "options": ["Telnet, FTP, R-commands (rsh, rlogin)", "SSH, SFTP, HTTPS", "NTP, DNS, DHCP", "Syslog, Cron, Systemd"],
        "answer": 1, "explanation": "Telnet, FTP, rlogin/rsh/rcp는 통신 구간 암호화가 없어 스니핑에 취약하므로 SSH, SFTP, SCP 등 보안 프로토콜로 대체해야 합니다."
    })
    q.append({
        "id": "IP2_Q18", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[실무 서술] 침해사고 대응 절차(NIST SP 800-61) 4단계의 순서로 올바른 것은?",
        "options": [
            "준비(Preparation) -> 탐지 및 분석(Detection & Analysis) -> 봉쇄·제거 및 복구(Containment, Eradication & Recovery) -> 사후 활동(Post-Incident Activity)",
            "탐지 -> 복구 -> 준비 -> 제거",
            "분석 -> 준비 -> 봉쇄 -> 보고",
            "신고 -> 수사 -> 복구 -> 재개"
        ],
        "answer": 1, "explanation": "NIST 침해사고 대응 표준 4단계는 1. 준비 -> 2. 탐지 및 분석 -> 3. 봉쇄, 제거 및 복구 -> 4. 사후 검토 및 활동입니다."
    })
    q.append({
        "id": "IP2_Q19", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 3, "subject_name": "3영역: 시큐어코딩 진단",
        "question": "[시큐어코딩] C/C++ 언어에서 버퍼 오버플로우를 유발하는 위험 함수와 이를 대체할 안전한 함수의 매칭으로 올바르지 않은 것은?",
        "options": [
            "strcpy -> strncpy (또는 strcpy_s)",
            "strcat -> strncat (또는 strcat_s)",
            "sprintf -> snprintf (또는 sprintf_s)",
            "gets -> fgets",
            "printf -> gets"
        ],
        "answer": 5, "explanation": "gets는 버퍼 크기를 검사하지 않아 가장 취약한 함수이며 버퍼 길이를 지정받는 fgets로 대체해야 합니다."
    })
    q.append({
        "id": "IP2_Q20", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 4, "subject_name": "4영역: 서술형/관리",
        "question": "[서술형] 개인정보처리자가 개인정보의 처리를 제3자에게 위탁할 때 '위탁 계약서'에 법적으로 반드시 포함해야 하는 필수 문서화 항목이 아닌 것은?",
        "options": [
            "위탁업무 수행 목적 외 개인정보 처리 금지에 관한 사항",
            "개인정보의 기술적·관리적 보호조치에 관한 사항",
            "수탁사 직원의 주민등록번호 원본 목록",
            "위탁업무의 목적 및 범위",
            "재위탁 제한에 관한 사항 및 수탁사 관리·감독에 관한 사항"
        ],
        "answer": 3, "explanation": "개인정보보호법 제26조 위탁 계약 필수 사항은 ①위탁 목적/범위, ②목적외 처리 금지, ③보호조치, ④재위탁 제한, ⑤관리감독, ⑥손해배상 등입니다. 수탁사 직원 주민번호는 포함되지 않습니다."
    })
    q.append({
        "id": "IP2_Q21", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[로그 분석] 윈도우 이벤트 뷰어(Event Viewer) 보안 로그에서 사용자 계정의 로그인 성공과 로그인 실패를 나타내는 이벤트 ID(Event ID)의 조합은?",
        "options": [
            "성공: 4624, 실패: 4625",
            "성공: 1000, 실패: 1001",
            "성공: 7036, 실패: 7037",
            "성공: 4672, 실패: 4673"
        ],
        "answer": 1, "explanation": "윈도우 보안 이벤트 로그에서 이벤트 ID 4624는 로그인 성공(An account was successfully logged on), 4625는 로그인 실패(An account failed to log on)입니다."
    })
    q.append({
        "id": "IP2_Q22", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[실무 분석] 침해당한 리눅스 서버에서 숨겨진 프로세스를 찾기 위해 'ps -ef' 결과와 비교 검증해야 하는 커널 가상 파일 시스템 디렉토리는?",
        "options": ["/proc 디렉토리 내의 숫자(PID) 디렉토리", "/sys 디렉토리", "/dev 디렉토리", "/etc 디렉토리"],
        "answer": 1, "explanation": "루트킷이 ps 명령어를 후킹해 은닉했더라도 커널 메모리를 반영하는 /proc/[PID] 디렉토리를 전수 검사하여 숨겨진 악성 프로세스를 식별할 수 있습니다."
    })
    q.append({
        "id": "IP2_Q23", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 3, "subject_name": "3영역: 시큐어코딩 진단",
        "question": "[시큐어코딩] 비밀번호 암호화 저장 시 SHA-256과 같은 빠른 해시 함수를 단독으로 사용하는 것이 보안상 취약한 이유와 이에 대한 해결책은?",
        "options": [
            "GPU를 이용한 초당 수십억 번의 고속 대입(레인보우 테이블) 공격에 취약하므로, PBKDF2나 bcrypt, Argon2를 사용하여 솔트 추가 및 반복 연산(키 스트레칭)을 적용해야 한다.",
            "SHA-256은 복호화 키가 노출되기 쉬우므로 대칭키로 저장해야 한다.",
            "해시 함수는 길이가 짧으므로 평문으로 저장해야 한다.",
            "MD5로 변경해야 한다."
        ],
        "answer": 1, "explanation": "일반 암호학적 해시는 고속 계산에 최적화되어 있어 무차별 대입 공격에 취약합니다. 솔트(Salt)와 반복 연산을 강제하는 패스워드 전용 단방향 함수(bcrypt 등)를 써야 합니다."
    })
    q.append({
        "id": "IP2_Q24", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 2, "subject_name": "2영역: 시스템/네트워크 실무",
        "question": "[실무 점검] 리눅스에서 패스워드 없이 root 권한으로 명령어를 실행할 수 있도록 오설정된 sudoers(/etc/sudoers) 설정의 예시는?",
        "options": [
            "user01 ALL=(ALL) NOPASSWD: ALL",
            "root ALL=(ALL) ALL",
            "%wheel ALL=(ALL) ALL",
            "Defaults requiretty"
        ],
        "answer": 1, "explanation": "'NOPASSWD: ALL' 설정은 해당 계정이 비밀번호 검증 없이 즉시 root 권한의 모든 명령을 실행할 수 있어 계정 탈취 시 즉각적인 시스템 완전 장악으로 이어집니다."
    })
    q.append({
        "id": "IP2_Q25", "category": "infosec_practical", "exam": 2, "exam_name": "2회 실기 서술·실무형 분석",
        "subject_id": 4, "subject_name": "4영역: 서술형/관리",
        "question": "[서술형] 개인정보보호위원회 고시 '개인정보의 안전성 확보조치 기준'에 따른 접속기록 점검 주기는 최소 얼마에 1회 이상인가?",
        "options": ["매월 1회 이상", "매주 1회 이상", "반기 1회 이상", "매년 1회 이상"],
        "answer": 1, "explanation": "개인정보처리자는 개인정보처리시스템의 접속기록에 대해 월 1회 이상 정기적으로 불법 접근, 다운로드, 열람 등 이상 징후를 점검·확인하여야 합니다."
    })

    try:
        from . import practical_questions_extra
        q.extend(practical_questions_extra.get_extra_practical_questions())
    except ImportError:
        import practical_questions_extra
        q.extend(practical_questions_extra.get_extra_practical_questions())

    return q

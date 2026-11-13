// infosec_exam_data.js
// 2026 이기적 정보보안기사 필기+실기 올인원(영진닷컴) 및 ISMS-P 인증심사원 완전판 데이터셋
// 필기 200문항 (1~4회 각 50제) | 실기 100문항 (단답 50제 + 서술실무 50제) | ISMS-P 30문항 (1·2회 각 15제)

window.INFOSEC_WRITTEN_DATA = {
  "title": "2026 이기적 정보보안기사 (필기) 200제 & 내용별 심층요약·용어사전 80선",
  "description": "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1~4회 모의고사(각 50제) 총 200문항 및 내용별 심층 요약 35선 + 필수 핵심 용어사전 45선",
  "questions": [
    {
      "id": "IW1_Q1",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 파일 시스템에서 파일에 설정된 특수 권한 비트 중 SetUID 비트가 부여된 파일을 검색하기 위한 find 명령어로 가장 올바른 것은?",
      "options": [
        "find / -perm -4000 -type f",
        "find / -perm -2000 -type f",
        "find / -perm -1000 -type f",
        "find / -perm -7777 -type f",
        "find / -perm -0400 -type f"
      ],
      "answer": 1,
      "explanation": "SetUID 비트는 8진수 4000입니다. 'find / -perm -4000 -type f' 명령을 통해 소유자 권한으로 실행되는 파일을 전수 식별할 수 있습니다. (2000: SetGID, 1000: Sticky bit)"
    },
    {
      "id": "IW1_Q2",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "스택이나 힙과 같은 데이터 저장 영역에서 악성 셸코드가 실행되는 것을 하드웨어(CPU) 및 OS 차원에서 차단하는 메모리 보호 기법은?",
      "options": [
        "ASLR (Address Space Layout Randomization)",
        "DEP / NX (Data Execution Prevention)",
        "Stack Canary (스택 카나리)",
        "SafeSEH",
        "Shadow Stack"
      ],
      "answer": 2,
      "explanation": "DEP/NX(Data Execution Prevention)는 데이터 영역(Stack/Heap)에 실행(Execute) 권한을 제거하여 셸코드 실행을 원천 차단합니다. ASLR은 메모리 주소를 난수화하는 기술입니다."
    },
    {
      "id": "IW1_Q3",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 PAM(Pluggable Authentication Modules) 제어 플래그 중, 인증 실패 시 즉시 실패를 반환하지 않고 나머지 모듈을 계속 실행한 후 최종적으로 실패를 반환하는 플래그는?",
      "options": [
        "required",
        "requisite",
        "sufficient",
        "optional",
        "include"
      ],
      "answer": 1,
      "explanation": "required 플래그는 실패하더라도 스택의 나머지 모듈을 계속 수행하지만 최종 결과는 실패로 반환합니다. requisite는 실패 즉시 중단하고 실패를 반환합니다."
    },
    {
      "id": "IW1_Q4",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 시스템 로그 파일 중 바이너리 형태로 기록되어 lastlog 명령어를 통해서만 각 계정별 마지막 로그인 일시와 출발지 IP를 확인할 수 있는 파일은?",
      "options": [
        "/var/log/wtmp",
        "/var/log/utmp",
        "/var/log/lastlog",
        "/var/log/btmp",
        "/var/log/secure"
      ],
      "answer": 3,
      "explanation": "/var/log/lastlog는 계정별 최근 접속 기록을 저장하며 lastlog 명령어로 조회합니다. wtmp는 전체 로그인/로그아웃 이력(last), utmp는 현재 접속자(who), btmp는 로그인 실패(lastb)입니다."
    },
    {
      "id": "IW1_Q5",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 아키텍처에서 모든 객체에 대한 접근 제어 결정을 내리고 감사 메시지를 생성하는 커널 모드 핵심 보안 컴포넌트는?",
      "options": [
        "LSA (Local Security Authority)",
        "SAM (Security Accounts Manager)",
        "SRM (Security Reference Monitor)",
        "Winlogon",
        "Active Directory"
      ],
      "answer": 3,
      "explanation": "SRM(보안 참조 모니터)은 커널 모드에서 실행되며 사용자 토큰과 대상 객체의 DACL/SACL을 비교하여 접근 승인 여부를 결정하고 보안 감사 로그를 남깁니다."
    },
    {
      "id": "IW1_Q6",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스에서 파일의 무결성을 주기적으로 검증하기 위해 해시값 데이터베이스를 구축하고 비교하는 호스트 기반 침입탐지 도구(HIDS)는?",
      "options": [
        "Tripwire",
        "Snort",
        "Tcpdump",
        "Chkrootkit",
        "ClamAV"
      ],
      "answer": 1,
      "explanation": "Tripwire는 시스템 주요 파일들의 MD5/SHA 해시값을 사전에 DB로 생성해 두고, 변경 여부를 주기적으로 대조하여 변조를 탐지하는 무결성 검증 도구입니다."
    },
    {
      "id": "IW1_Q7",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "유닉스/리눅스 시스템에서 일반 사용자가 생성하는 디렉토리와 파일의 기본 권한을 750(rwxr-x---), 640(rw-r-----)으로 생성되도록 설정하는 umask 값은?",
      "options": [
        "022",
        "027",
        "077",
        "037",
        "002"
      ],
      "answer": 2,
      "explanation": "디렉토리 기본 권한 777에서 027을 빼면 750, 파일 기본 권한 666에서 027을 빼면(실행권한 제외) 640이 됩니다. 따라서 권장 보안 umask는 027입니다."
    },
    {
      "id": "IW1_Q8",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 레지스트리 경로 중 시스템 부팅 시 자동으로 실행되도록 악성코드가 가장 흔하게 등록하는 자동 실행 키 경로는?",
      "options": [
        "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "HKLM\\System\\CurrentControlSet\\Services\\EventLog",
        "HKCU\\Control Panel\\Desktop",
        "HKLM\\SAM\\SAM\\Domains\\Account",
        "HKCR\\CLSID\\InprocServer32"
      ],
      "answer": 1,
      "explanation": "윈도우 부팅 시 자동 실행을 위해 HKLM 및 HKCU의 \\Software\\Microsoft\\Windows\\CurrentVersion\\Run 또는 RunOnce 키에 악성 실행 경로를 등록합니다."
    },
    {
      "id": "IW1_Q9",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "프로세스가 파일이나 디렉토리 등의 자원을 점검하는 시점(Time of Check)과 실제 사용하는 시점(Time of Use) 사이의 시간차를 노려 공격하는 취약점은?",
      "options": [
        "Format String Attack",
        "Race Condition (TOCTOU)",
        "Heap Spraying",
        "Return-to-libc (RTL)",
        "Stack Pivoting"
      ],
      "answer": 2,
      "explanation": "TOCTOU(Time of Check to Time of Use) 경쟁 조건(Race Condition) 취약점은 자원 접근 권한 확인과 실제 작업 수행 사이의 간극을 이용해 심볼릭 링크 등을 바꿔치기하는 공격입니다."
    },
    {
      "id": "IW1_Q10",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 /etc/shadow 파일의 두 번째 필드에서 암호화 알고리즘 식별자가 '$6$'으로 시작할 때 사용된 단방향 해시 알고리즘은?",
      "options": [
        "MD5",
        "Blowfish",
        "SHA-256",
        "SHA-512",
        "DES"
      ],
      "answer": 4,
      "explanation": "shadow 파일의 알고리즘 식별자는 $1=MD5, $2a=Blowfish, $5=SHA-256, $6=SHA-512입니다."
    },
    {
      "id": "IW1_Q11",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "TCP 3-Way Handshake 과정에서 대량의 SYN 패킷을 전송하고 SYN/ACK에 대해 ACK를 보내지 않아 서버의 백로그 큐(Backlog Queue)를 고갈시키는 공격은?",
      "options": [
        "Smurf Attack",
        "TCP SYN Flooding",
        "Land Attack",
        "TearDrop",
        "Ping of Death"
      ],
      "answer": 2,
      "explanation": "TCP SYN Flooding은 공격자가 반가용(Half-Open) 상태를 유지시켜 서버의 백로그 큐를 채워 정상 접속을 불능으로 만드는 L4 DoS 공격입니다. SYN Cookie 기법 등으로 방어합니다."
    },
    {
      "id": "IW1_Q12",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IPSec 프로토콜에 대한 설명 중 가장 옳지 않은 것은?",
      "options": [
        "AH(Authentication Header)는 데이터의 무결성과 송신처 인증을 제공한다.",
        "ESP(Encapsulating Security Payload)는 암호화를 통한 기밀성, 무결성, 인증을 모두 제공할 수 있다.",
        "전송 모드(Transport Mode)는 원본 IP 헤더 뒤의 페이로드만 보호한다.",
        "터널 모드(Tunnel Mode)는 원본 패킷 전체를 캡슐화하고 새로운 외부 IP 헤더를 추가한다.",
        "AH 프로토콜은 NAT 환경에서 주소가 변환되어도 무결성 검증에 아무런 문제가 없다."
      ],
      "answer": 5,
      "explanation": "AH는 IP 헤더의 불변 필드까지 포함하여 ICV(무결성 체크값)를 계산하므로 IP 주소가 변경되는 NAT를 거치면 무결성 검증에 실패합니다. 따라서 NAT 환경에서는 ESP와 NAT-Traversal을 사용합니다."
    },
    {
      "id": "IW1_Q13",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "Snort IDS 규칙 설정에서 외부에서 웹 서버(80 포트)로 인입되는 패킷 중 '/admin' 문자열을 대소문자 구분 없이 탐지하기 위한 옵션 조합으로 올바른 것은?",
      "options": [
        "alert tcp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; content:\"/admin\"; nocase; sid:10001;)",
        "drop udp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; regex:\"/admin\";)",
        "log ip any any <> 192.168.1.10 80 (msg:\"Admin Access\"; string:\"/admin\";)",
        "alert tcp 192.168.1.10 80 -> any any (msg:\"Admin Access\"; payload:\"/admin\";)",
        "pass tcp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; offset:0;)"
      ],
      "answer": 1,
      "explanation": "Snort 룰은 헤더(액션, 프로토콜, IP/포트)와 바디의 msg, content, nocase(대소문자 무시), sid(고유식별자) 등으로 구성됩니다."
    },
    {
      "id": "IW1_Q14",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "출발지 IP 주소와 목적지 IP 주소를 희생자의 IP 주소로 동일하게 조작하여 전송함으로써 시스템이 자기 자신에게 응답하느라 루프에 빠지게 하는 공격은?",
      "options": [
        "Smurf Attack",
        "Land Attack",
        "TearDrop",
        "Bonk",
        "Fraggle"
      ],
      "answer": 2,
      "explanation": "Land Attack은 송신자 IP와 수신자 IP를 동일한 희생자 IP로 위조하여 패킷을 보냄으로써 시스템 리소스를 고갈시키는 공격입니다."
    },
    {
      "id": "IW1_Q15",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "TCP 스텔스 스캔(Stealth Scan) 중 포트가 열려 있을 때는 응답이 없고, 닫혀 있을 때만 대상 서버로부터 RST/ACK 패킷이 회신되는 스캔 기법의 조합은?",
      "options": [
        "TCP Connect 스캔",
        "TCP SYN(Half-Open) 스캔",
        "FIN 스캔, Null 스캔, Xmas 스캔",
        "ACK 스캔",
        "UDP 스캔"
      ],
      "answer": 3,
      "explanation": "FIN, Null, Xmas 스캔은 RFC 793 규약에 따라 열린 포트는 비정상 패킷을 무시(Drop)하여 무응답이고, 닫힌 포트는 RST/ACK를 응답하는 특성을 이용합니다."
    },
    {
      "id": "IW1_Q16",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "로컬 네트워크(LAN) 상에서 IP 주소와 MAC 주소 간의 바인딩 테이블을 위조하여 패킷을 가로채는 공격(ARP Spoofing)에 대한 가장 효과적인 대응 방안은?",
      "options": [
        "방화벽 도입",
        "정적(Static) ARP 테이블 설정",
        "DNSSEC 적용",
        "NAT 설정",
        "라우터 Hop 수 증가"
      ],
      "answer": 2,
      "explanation": "ARP는 무인증 프로토콜이므로 공격자의 위조 ARP Reply를 막기 위해서는 게이트웨이 및 주요 서버의 MAC 주소를 정적(Static, arp -s)으로 고정하는 것이 근본적인 대응책입니다."
    },
    {
      "id": "IW1_Q17",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IP 단편화(Fragmentation) 재조합 과정에서 Fragment Offset 값을 비정상적으로 겹치게 조작하여 수신 시스템의 OS 크래시를 유발하는 DoS 공격은?",
      "options": [
        "TearDrop",
        "Smurf",
        "Ping of Death",
        "Land Attack",
        "Slowloris"
      ],
      "answer": 1,
      "explanation": "TearDrop 공격은 IP 헤더의 오프셋(Offset) 값을 중첩되도록 조작하여 수신 시스템이 패킷 재조합 시 메모리 참조 오류로 다운되게 만듭니다."
    },
    {
      "id": "IW1_Q18",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "HTTP 헤더의 끝을 알리는 개행문자(\\r\\n\\r\\n)를 완성하지 않고 불완전한 헤더를 주기적으로 찔끔 전송하여 웹 서버의 연결 커넥션을 장시간 고갈시키는 공격은?",
      "options": [
        "Slow HTTP Header DoS (Slowloris)",
        "Slow HTTP POST DoS (RUDY)",
        "Slow HTTP Read DoS",
        "HTTP GET Flooding",
        "Hulk DoS"
      ],
      "answer": 1,
      "explanation": "Slowloris(Slow HTTP Header DoS)는 HTTP 요청 헤더의 끝을 닫지 않고 일정 시간마다 불필요한 헤더 라인을 추가 전송하여 연결을 독점하는 L7 저대역폭 공격입니다."
    },
    {
      "id": "IW1_Q19",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "무선 LAN 보안 프로토콜 중 사전 대입 공격(Dictionary Attack)과 오프라인 공격을 방어하기 위해 SAE(Simultaneous Authentication of Equals) 핸드셰이크를 도입한 최신 표준은?",
      "options": [
        "WEP",
        "WPA-TKIP",
        "WPA2-PSK",
        "WPA3",
        "LEAP"
      ],
      "answer": 4,
      "explanation": "WPA3는 기존 WPA2의 4-Way 핸드셰이크 취약점(KRACK 등)을 개선하여 Dragonfly 키 교환 기반의 동등 동시 인증(SAE) 핸드셰이크를 채택해 오프라인 사전 공격을 방어합니다."
    },
    {
      "id": "IW1_Q20",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "DNS 쿼리에 대한 위·변조를 방지하고 DNS 응답의 송신처 인증 및 무결성을 보장하기 위해 전자서명 기술을 적용한 확장 표준은?",
      "options": [
        "DNSSEC",
        "DoH (DNS over HTTPS)",
        "DoT (DNS over TLS)",
        "BGPsec",
        "DKIM"
      ],
      "answer": 1,
      "explanation": "DNSSEC(DNS Security Extensions)은 공개키 암호화 전자서명을 DNS 레코드(RRSIG, DNSKEY 등)에 부여하여 캐시 포이즈닝 및 DNS 스푸핑을 방지합니다."
    },
    {
      "id": "IW1_Q21",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 애플리케이션에서 사용자의 입력값을 검증하지 않고 SQL 쿼리문에 직접 결합할 때 발생하는 SQL 인젝션(Injection)의 가장 근본적인 시큐어코딩 방어 대책은?",
      "options": [
        "정규표현식을 통한 특수문자 치환",
        "파라미터화된 쿼리 (PreparedStatement) 및 바인딩 변수 사용",
        "에러 메시지 상세 출력",
        "웹 방화벽(WAF) 단독 의존",
        "GET 대신 POST 메소드 사용"
      ],
      "answer": 2,
      "explanation": "SQL 인젝션 방어의 최우선 안전수칙은 정적 컴파일된 PreparedStatement를 사용하여 사용자 입력을 단순 데이터 리터럴(Parameter)로만 처리하는 것입니다."
    },
    {
      "id": "IW1_Q22",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "공격자가 악성 스크립트를 게시판 등에 영구 저장하여, 해당 게시물을 열람하는 다수의 불특정 피해자 브라우저에서 스크립트가 실행되도록 하는 취약점은?",
      "options": [
        "Reflected XSS",
        "Stored (Persistent) XSS",
        "DOM-based XSS",
        "CSRF",
        "Clickjacking"
      ],
      "answer": 2,
      "explanation": "Stored XSS는 악성 스크립트가 데이터베이스에 저장되어 게시물을 조회하는 모든 사용자의 브라우저에서 세션 쿠키 탈취 등을 수행하는 공격입니다."
    },
    {
      "id": "IW1_Q23",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 브라우저의 자바스크립트(document.cookie)를 통한 세션 쿠키 탈취(XSS)를 원천적으로 방지하기 위해 설정하는 HTTP 쿠키 보안 플래그는?",
      "options": [
        "Secure",
        "HttpOnly",
        "SameSite=Strict",
        "Path=/admin",
        "Domain=.test.com"
      ],
      "answer": 2,
      "explanation": "HttpOnly 플래그가 설정된 쿠키는 브라우저 스크립트(document.cookie)를 통한 접근이 차단되어 XSS 공격 시 세션 탈취를 효과적으로 예방합니다. (Secure는 HTTPS 통신만 허용)"
    },
    {
      "id": "IW1_Q24",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "로그인된 사용자의 브라우저를 유도하여 사용자의 권한으로 공격자가 의도한 비정상적인 HTTP 요청(패스워드 변경, 글쓰기 등)을 서버로 전송시키는 공격은?",
      "options": [
        "XSS",
        "CSRF (Cross-Site Request Forgery)",
        "SSRF",
        "Directory Traversal",
        "File Inclusion"
      ],
      "answer": 2,
      "explanation": "CSRF는 인증된 사용자의 권한을 도용하여 악의적인 요청을 수행하게 하는 공격으로, CSRF 토큰 검증이나 SameSite 쿠키 속성으로 방어합니다."
    },
    {
      "id": "IW1_Q25",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "공격자가 웹 애플리케이션 취약점을 이용해 웹 서버가 내부 인트라넷 시스템(메타데이터 API, 내부 DB 등)으로 비인가 HTTP 요청을 전송하도록 강제하는 서버사이드 취약점은?",
      "options": [
        "CSRF",
        "SSRF (Server-Side Request Forgery)",
        "XXE",
        "SSTI",
        "Insecure Deserialization"
      ],
      "answer": 2,
      "explanation": "SSRF는 서버가 외부 자원을 fetch하는 기능에서 내부 비인가 IP(127.0.0.1, 169.254.169.254 등)로의 접근을 허용할 때 발생합니다."
    },
    {
      "id": "IW1_Q26",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 파일 업로드 취약점을 방어하기 위한 시큐어코딩 조치로 가장 적절하지 않은 것은?",
      "options": [
        "업로드 파일의 확장자를 안전한 화이트리스트(Whitelist) 방식으로 엄격히 제한한다.",
        "업로드 디렉토리의 웹 서버 실행(Execute) 권한을 제거한다.",
        "파일명을 원본 그대로 저장하여 사용자가 쉽게 식별할 수 있도록 한다.",
        "업로드 경로를 웹 루트(Web Root) 외부의 독립된 디렉토리로 격리한다.",
        "MIME-Type 검증과 파일 시그니처(Magic Number) 검증을 병행한다."
      ],
      "answer": 3,
      "explanation": "업로드된 파일은 웹셸 실행 및 경로 조작을 막기 위해 파일명을 난수(UUID 등)로 변경하고 확장자를 강제 분리해야 합니다. 원본 파일명을 그대로 사용하는 것은 취약합니다."
    },
    {
      "id": "IW1_Q27",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "이메일 보안 프로토콜 중 메일 송신 서버의 도메인 DNS에 개인키로 서명된 헤더를 검증할 수 있는 공개키를 등록하여 메일 위·변조를 검증하는 기술은?",
      "options": [
        "SPF",
        "DKIM (DomainKeys Identified Mail)",
        "DMARC",
        "PGP",
        "S/MIME"
      ],
      "answer": 2,
      "explanation": "DKIM은 송신 메일 헤더에 디지털 서명을 첨부하고, 수신자는 송신자 도메인의 DNS에 공개된 TXT 레코드 공개키로 이를 검증하여 메일 위조를 탐지합니다."
    },
    {
      "id": "IW1_Q28",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "브라우저에게 해당 웹사이트는 오직 HTTPS 통신만을 사용해야 함을 강제하여 SSL Stripping 공격을 방지하는 HTTP 응답 헤더는?",
      "options": [
        "Strict-Transport-Security (HSTS)",
        "Content-Security-Policy (CSP)",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Access-Control-Allow-Origin"
      ],
      "answer": 1,
      "explanation": "HSTS 헤더는 브라우저가 첫 연결 이후 무조건 암호화된 HTTPS 연결만을 시도하도록 강제하여 평문 다운그레이드 공격을 차단합니다."
    },
    {
      "id": "IW1_Q29",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "XML 파서가 외부 엔티티(External Entity)를 참조하도록 구성되었을 때 로컬 파일 유출이나 DoS(Billion Laughs)를 유발하는 취약점은?",
      "options": [
        "XXE (XML External Entity)",
        "XPATH Injection",
        "LDAP Injection",
        "Format String",
        "Buffer Overflow"
      ],
      "answer": 1,
      "explanation": "XXE 공격은 XML 문서 내 외부 DTD 엔티티 선언을 악용하여 시스템 내부 파일(/etc/passwd 등)을 탈취하거나 내부 포트 스캔을 수행하는 공격입니다."
    },
    {
      "id": "IW1_Q30",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "데이터베이스 암호화 방식 중 DBMS 커널에 독립된 플러그인을 탑재하여 SQL문 수정 없이 데이터 암·복호화를 수행하는 방식은?",
      "options": [
        "API 방식",
        "Plug-In 방식",
        "TDE (Transparent Data Encryption) 방식",
        "하이브리드 방식",
        "File 암호화"
      ],
      "answer": 2,
      "explanation": "Plug-In 방식은 DB 엔진 내부 모듈로 연동되어 애플리케이션 코드 수정이 거의 없으며 DBMS 엔진 성능을 활용합니다. TDE는 테이블스페이스 전체를 투명하게 파일 레벨에서 암호화합니다."
    },
    {
      "id": "IW1_Q31",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "블록 암호화 알고리즘의 운영 모드 중 동일한 평문 블록이 항상 동일한 암호문 블록을 생성하므로 기밀성이 낮아 일반 데이터 암호화에 권장되지 않는 모드는?",
      "options": [
        "ECB (Electronic Codebook) 모드",
        "CBC (Cipher Block Chaining) 모드",
        "CFB 모드",
        "OFB 모드",
        "CTR (Counter) 모드"
      ],
      "answer": 1,
      "explanation": "ECB 모드는 초기화 벡터(IV) 없이 각 블록을 독립적으로 암호화하므로 패턴이 그대로 노출되어 현대 암호에서 사용을 금지합니다."
    },
    {
      "id": "IW1_Q32",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "다중 보안 레벨 환경에서 군사적 기밀성을 보장하기 위해 고안된 모델로, 'No Read Up (단순 보안 속성)'과 'No Write Down (*-속성)'을 정의한 접근통제 모델은?",
      "options": [
        "벨-라파둘라 (Bell-LaPadula, BLP) 모델",
        "비바 (Biba) 모델",
        "클락-윌슨 (Clark-Wilson) 모델",
        "만리장성 (Chinese Wall) 모델",
        "RBAC 모델"
      ],
      "answer": 1,
      "explanation": "BLP 모델은 기밀성을 최우선으로 하여 상위 보안 레벨의 문서를 읽을 수 없고(No Read Up), 하위 보안 레벨로 기밀을 기록할 수 없습니다(No Write Down)."
    },
    {
      "id": "IW1_Q33",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "PKI 환경에서 인증서 폐지 목록(CRL) 다운로드에 따른 네트워크 대역폭 낭비와 갱신 지연 문제를 해결하기 위해, 인증서 폐지 여부를 실시간으로 조회하는 프로토콜은?",
      "options": [
        "OCSP (Online Certificate Status Protocol)",
        "LDAP",
        "SCEP",
        "CMP",
        "EST"
      ],
      "answer": 1,
      "explanation": "OCSP는 클라이언트가 인증서 시리얼 넘버를 질의하면 실시간으로 해당 인증서의 유효/폐지 여부를 응답하는 경량 프로토콜입니다."
    },
    {
      "id": "IW1_Q34",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "사용자의 역할(Role)에 따라 권한을 부여하고, 사용자가 조직 내 직무 변경 시 역할만 재할당함으로써 최소 권한 원칙과 직무 분리를 효율적으로 달성하는 접근통제 방식은?",
      "options": [
        "DAC (임의적 접근통제)",
        "MAC (강제적 접근통제)",
        "RBAC (역할기반 접근통제)",
        "ABAC (속성기반 접근통제)",
        "Rule-based Access Control"
      ],
      "answer": 3,
      "explanation": "RBAC(Role-Based Access Control)는 역할에 권한을 매핑하고 사용자에게 역할을 부여하여 관리가 용이하며 엔터프라이즈 환경에서 널리 쓰입니다."
    },
    {
      "id": "IW1_Q35",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "암호학적 일방향 해시 함수가 만족해야 하는 보안 특성 중, 주어진 해시값 h에 대해 H(m) = h를 만족하는 메시지 m을 찾는 것이 계산상 불가능해야 한다는 특성은?",
      "options": [
        "제1 역상 저항성 (Preimage Resistance)",
        "제2 역상 저항성 (Second Preimage Resistance)",
        "충돌 저항성 (Collision Resistance)",
        "눈사태 효과 (Avalanche Effect)",
        "비가역성"
      ],
      "answer": 1,
      "explanation": "제1 역상 저항성은 주어진 해시값으로부터 원래의 원본 메시지를 역산할 수 없어야 함을 의미합니다. (제2 역상은 특정 메시지와 같은 해시값을 갖는 다른 메시지를 찾기 어려운 성질)"
    },
    {
      "id": "IW1_Q36",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "한국인터넷진흥원(KISA)이 개발한 128비트 블록 암호화 알고리즘으로, Feistel 구조를 가지며 16라운드로 구성된 국가 표준 대칭키 암호는?",
      "options": [
        "ARIA",
        "SEED",
        "HIGHT",
        "LEA",
        "DES"
      ],
      "answer": 2,
      "explanation": "SEED는 128비트 블록/128비트 키의 Feistel 구조 표준 암호입니다. ARIA는 국가정보원이 개발한 SPN 구조 암호입니다."
    },
    {
      "id": "IW1_Q37",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "송신자가 대칭키(세션키)로 메시지를 암호화하고, 그 세션키를 수신자의 공개키로 암호화하여 메시지와 함께 전달함으로써 대용량 기밀성과 키 분배를 동시에 해결하는 기술은?",
      "options": [
        "전자봉투 (Digital Envelope)",
        "디지털 서명",
        "은닉 서명",
        "블라인드 서명",
        "영지식 증명"
      ],
      "answer": 1,
      "explanation": "전자봉투(Digital Envelope)는 공개키의 느린 연산 속도와 대칭키의 키 배송 문제를 결합하여 세션키를 비대칭키로 암호화해 전달하는 하이브리드 암호화 기술입니다."
    },
    {
      "id": "IW1_Q38",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "데이터의 무결성을 최우선으로 하여 부적격자에 의한 데이터 수정 방지 및 직무 분리를 보장하는 모델로, 'No Read Down'과 'No Write Up' 원칙을 적용한 모델은?",
      "options": [
        "벨-라파둘라 (BLP) 모델",
        "비바 (Biba) 모델",
        "클락-윌슨 모델",
        "디피-헬만 모델",
        "접근제어 행렬"
      ],
      "answer": 2,
      "explanation": "Biba 모델은 무결성 보호 모델로서 하위 무결성 레벨의 데이터를 읽을 수 없고(No Read Down), 상위 무결성 레벨로 쓸 수 없습니다(No Write Up)."
    },
    {
      "id": "IW1_Q39",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "사용자 인증 요소 중 지식 기반(Knowledge), 소유 기반(Possession), 생체 기반(Inherence)의 3대 요인 중 서로 다른 2개 이상의 요소를 조합하는 인증 방식은?",
      "options": [
        "SSO (Single Sign-On)",
        "MFA (Multi-Factor Authentication)",
        "OAuth 2.0",
        "OpenID Connect",
        "Kerberos"
      ],
      "answer": 2,
      "explanation": "MFA(다중 요소 인증)는 알고 있는 것(PW), 가지고 있는 것(OTP/스마트폰), 고유한 것(지문/홍채) 중 2가지 이상의 서로 다른 팩터를 결합해 인증합니다."
    },
    {
      "id": "IW1_Q40",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "금융 및 컨설팅 분야에서 이해관계 상충(Conflict of Interest)을 방지하기 위해 이전에 접근했던 데이터군에 따라 다른 데이터군에 대한 접근을 동적으로 차단하는 모델은?",
      "options": [
        "만리장성 (Chinese Wall / Brewer-Nash) 모델",
        "BLP 모델",
        "Biba 모델",
        "MAC 모델",
        "HRU 모델"
      ],
      "answer": 1,
      "explanation": "Chinese Wall(Brewer-Nash) 모델은 사용자의 이전 접근 이력에 기반하여 충돌하는 경쟁 회사의 데이터 접근을 동적으로 제한합니다."
    },
    {
      "id": "IW1_Q41",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보보호법상 개인정보처리자가 개인정보 유출 사실을 알게 되었을 때, 정당한 사유가 없는 한 정보주체에게 통지하고 관계 당국에 신고해야 하는 법정 시한은?",
      "options": [
        "24시간 이내",
        "48시간 이내",
        "72시간 이내",
        "5일 이내",
        "14일 이내"
      ],
      "answer": 3,
      "explanation": "개인정보보호법 제34조에 따라 개인정보 유출을 알게 된 때에는 정당한 사유가 없는 한 72시간 이내에 정보주체에게 통지하고 개인정보보호위원회 또는 KISA에 신고해야 합니다."
    },
    {
      "id": "IW1_Q42",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보통신망법 및 전자금융거래법상 정보보호최고책임자(CISO) 지정 의무 대상 기업 중, 타 업무(개인정보보호책임자 CPO 제외)와의 겸직이 법적으로 절대 금지되는 기준은?",
      "options": [
        "자산총액 1조 원 이상 및 정보보호 관리체계 의무대상자",
        "자산총액 7천억 원 이상 및 상시근로자 1천 명 이상",
        "자산총액 5천억 원 이상 및 정보통신서비스 매출액 100억 원 이상",
        "상시근로자 500명 이상",
        "전년도 매출액 500억 원 이상"
      ],
      "answer": 1,
      "explanation": "자산총액 1조 원 이상 또는 ISMS-P 인증 의무대상자 중 중대형 기업은 CISO가 타 직무(CIO, 개발책임자 등)를 겸직할 수 없도록 엄격히 분리 규정하고 있습니다."
    },
    {
      "id": "IW1_Q43",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "위험관리(Risk Management) 단계에서 수용 가능한 위험 수준을 설정하여 그 이하의 위험은 수용하고, 초과하는 위험은 처리 대책을 수립하도록 정하는 기준값은?",
      "options": [
        "DOA (Degree of Assurance)",
        "DOA (Degree of Acceptable Risk)",
        "ALE (Annual Loss Expectancy)",
        "ARO (Annual Rate of Occurrence)",
        "SLE (Single Loss Expectancy)"
      ],
      "answer": 2,
      "explanation": "DOA(Degree of Acceptable Risk, 수용 가능 위험 수준)는 조직의 위험 수용한도를 정의하는 척도로, 이를 초과하는 위험에 대해 감소, 회피, 전가 등의 통제를 적용합니다."
    },
    {
      "id": "IW1_Q44",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보보호법상 법령에 구체적인 근거가 있거나 정보주체로부터 별도의 동의를 얻은 경우를 제외하고는 원칙적으로 처리가 금지되는 고유식별정보 4가지에 해당하지 않는 것은?",
      "options": [
        "주민등록번호",
        "여권번호",
        "운전면허번호",
        "외국인등록번호",
        "휴대전화번호"
      ],
      "answer": 5,
      "explanation": "고유식별정보 4종은 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호입니다. 휴대전화번호는 일반 개인정보입니다."
    },
    {
      "id": "IW1_Q45",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보보호 관리체계(ISMS) 인증 의무 대상자 기준 중 정보통신서비스 부문 전년도 매출액 기준은 얼마 이상인가?",
      "options": [
        "10억 원 이상",
        "50억 원 이상",
        "100억 원 이상",
        "500억 원 이상",
        "1,000억 원 이상"
      ],
      "answer": 3,
      "explanation": "ISMS 의무 대상자 중 하나는 정보통신서비스 부문 전년도 매출액이 100억 원 이상이거나, 전년도 직전 3개월간 일일평균 이용자 수가 100만 명 이상인 자입니다."
    },
    {
      "id": "IW1_Q46",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "업무 연속성 계획(BCP) 수립 시 업무가 중단되었을 때 허용 가능한 최대 다운타임(중단 허용 시간)을 의미하는 핵심 지표는?",
      "options": [
        "RTO (Recovery Time Objective)",
        "RPO (Recovery Point Objective)",
        "MTBF (Mean Time Between Failures)",
        "MTTR (Mean Time to Repair)",
        "WRT (Work Recovery Time)"
      ],
      "answer": 1,
      "explanation": "RTO(목표 복구 시간)는 재해 발생 후 업무가 정상 복구되어야 하는 목표 시한을 의미합니다. RPO(목표 복구 시점)는 허용 가능한 데이터 손실 시점입니다."
    },
    {
      "id": "IW1_Q47",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보보호 기술적·관리적 보호조치 기준에서 5만 명 이상의 고유식별정보 또는 민감정보를 처리하는 시스템의 개인정보처리시스템 접속기록 보관 최소 기한은?",
      "options": [
        "6개월 이상",
        "1년 이상",
        "2년 이상",
        "3년 이상",
        "5년 이상"
      ],
      "answer": 3,
      "explanation": "개인정보 접속기록은 기본 1년 이상 보관해야 하지만, 5만 명 이상의 고유식별정보/민감정보를 처리하거나 기간통신사업자 시스템의 경우 2년 이상 안전하게 보관해야 합니다."
    },
    {
      "id": "IW1_Q48",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정량적 위험분석(Quantitative Risk Analysis)에서 단일손실예상액(SLE)이 1,000만 원이고 연간발생률(ARO)이 0.2일 때, 연간손실예상액(ALE)은 얼마인가?",
      "options": [
        "100만 원",
        "200만 원",
        "500만 원",
        "1,000만 원",
        "2,000만 원"
      ],
      "answer": 2,
      "explanation": "연간손실예상액(ALE) = 단일손실예상액(SLE) × 연간발생률(ARO) = 10,000,000 × 0.2 = 2,000,000원입니다."
    },
    {
      "id": "IW1_Q49",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 안전성 확보조치 기준상 내부망에 저장된 고유식별정보에 대해 암호화를 적용하지 않아도 되는 예외 조건은?",
      "options": [
        "위험도 분석 결과 암호화 미적용 시에도 영향이 미미한 경우",
        "주민등록번호를 암호화하여 저장하는 경우",
        "비밀번호를 일방향 암호화한 경우",
        "주민등록번호는 내부망이라 할지라도 예외 없이 반드시 100% 암호화하여야 한다.",
        "CPO가 서면으로 승인한 경우"
      ],
      "answer": 4,
      "explanation": "주민등록번호는 내부망/외부망을 불문하고 저장 시 100% 암호화가 법적 강제 사항이며 어떠한 예외도 허용되지 않습니다."
    },
    {
      "id": "IW1_Q50",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보통신기반보호법에 따른 주요정보통신기반시설 취약점 분석·평가 수행 주기로 올바른 것은?",
      "options": [
        "매월 1회",
        "반기 1회",
        "매년 1회 이상",
        "2년에 1회",
        "3년에 1회"
      ],
      "answer": 3,
      "explanation": "주요정보통신기반시설 관리기관의 장은 매년 정기적으로 취약점 분석·평가를 실시하여야 합니다."
    },
    {
      "id": "IW2_Q1",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 파일의 타임스탬프 중 파일의 소유자, 권한(chmod), 링크 수 등 메타데이터(i-node)가 변경될 때 갱신되며, utime 함수로 임의 변조할 수 없는 시간 속성은?",
      "options": [
        "atime (Access Time)",
        "mtime (Modification Time)",
        "ctime (Change Time)",
        "dtime (Deletion Time)",
        "crtime (Creation Time)"
      ],
      "answer": 3,
      "explanation": "ctime은 i-node 메타데이터의 변경 시점을 기록하며 시스템 커널에 의해서만 갱신되므로 일반 시스템 호출(utime 등)로 공격자가 과거 시간으로 속일 수 없습니다."
    },
    {
      "id": "IW2_Q2",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "포맷 스트링 취약점(Format String Attack)에서 특정 메모리 주소에 지금까지 출력된 바이트 수를 저장하기 위해 공격자가 사용하는 변환 지시자는?",
      "options": [
        "%s",
        "%x",
        "%p",
        "%n",
        "%d"
      ],
      "answer": 4,
      "explanation": "%n 지시자는 앞서 출력된 총 문자(바이트) 수를 지정된 포인터 변수 메모리에 직접 쓰는(Write) 기능을 수행하므로 임의 코드 실행이나 메모리 변조에 악용됩니다."
    },
    {
      "id": "IW2_Q3",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 NTFS 파일 시스템의 특성을 악용하여 하나의 파일 안에 숨은 데이터 스트림을 생성하고 백도어나 실행 파일을 은닉하는 기법은?",
      "options": [
        "Alternate Data Streams (ADS)",
        "Volume Shadow Copy",
        "MFT 은닉",
        "EFS 암호화",
        "Slack Space 주입"
      ],
      "answer": 1,
      "explanation": "NTFS의 ADS(대체 데이터 스트림)는 'filename.txt:hidden.exe' 형태로 메인 파일 뒤에 숨겨진 스트림을 생성할 수 있어 탐지를 우회하는 악성코드 은닉에 자주 쓰입니다."
    },
    {
      "id": "IW2_Q4",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 메모리 가상화 보호 기술 중 실행 파일이 메모리에 로드될 때마다 코드(Text), 스택(Stack), 힙(Heap), 라이브러리의 시작 주소를 무작위로 배치하는 기술은?",
      "options": [
        "ASLR",
        "DEP",
        "CFI (Control Flow Integrity)",
        "SafeSEH",
        "StackGuard"
      ],
      "answer": 1,
      "explanation": "ASLR(Address Space Layout Randomization)은 메모리 주소를 난수화하여 공격자가 고정된 셸코드나 리턴 주소를 하드코딩하지 못하도록 방어합니다."
    },
    {
      "id": "IW2_Q5",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "스택 보호를 위해 리턴 주소(RET) 앞에 특정 카나리(Canary) 값을 삽입하고 함수 종료 시 카나리 변조 여부를 점검하는 컴파일러 보호 옵션은?",
      "options": [
        "-fstack-protector",
        "-D_FORTIFY_SOURCE",
        "-pie",
        "-Wl,-z,relro",
        "-fno-builtin"
      ],
      "answer": 1,
      "explanation": "GCC의 -fstack-protector 옵션은 스택 버퍼 오버플로우로 인해 리턴 주소가 덮어씌워지기 전에 카나리 값을 먼저 검사하여 조작 시 프로세스를 강제 종료합니다."
    },
    {
      "id": "IW2_Q6",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "유닉스 계열에서 네트워크 서비스 요청을 수신하여 실제 서비스 데몬(telnet, ftp 등)을 실행해 주고, /etc/hosts.allow 및 /etc/hosts.deny를 통해 접근을 제어하는 수퍼 데몬은?",
      "options": [
        "inetd / xinetd",
        "systemd",
        "crond",
        "syslogd",
        "sshd"
      ],
      "answer": 1,
      "explanation": "inetd/xinetd는 수퍼 데몬으로서 서비스 요청이 올 때 자식 프로세스로 서비스를 구동하며 TCP Wrapper(/etc/hosts.allow/deny)와 연동되어 접근 제어를 수행합니다."
    },
    {
      "id": "IW2_Q7",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 로그온 과정에서 패스워드 해시값을 직접 크랙하지 않고 메모리(lsass.exe)에서 추출한 NTLM 해시값을 그대로 인증 서버에 전송하여 세션을 획득하는 공격은?",
      "options": [
        "Pass-the-Hash (PtH)",
        "Kerberoasting",
        "Golden Ticket",
        "Overpass-the-Hash",
        "Silver Ticket"
      ],
      "answer": 1,
      "explanation": "Pass-the-Hash 공격은 패스워드 평문을 몰라도 NTLM 해시값 자체를 인증 토큰으로 재사용하여 타 시스템에 권한을 획득하는 래터럴 무브먼트 기법입니다."
    },
    {
      "id": "IW2_Q8",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스에서 프로세스가 chroot 탈출(Breakout)을 수행할 수 있는 원인으로 가장 올바른 것은?",
      "options": [
        "프로세스가 root 권한을 보유하고 있고 새 디렉토리로 이동한 후 상위 디렉토리(..)를 지속 참조할 때",
        "SELinux가 Enforcing 모드일 때",
        "프로세스에 SetUID가 제거되어 있을 때",
        "디렉토리에 Sticky bit가 설정되어 있을 때",
        "파일 시스템이 read-only로 마운트되어 있을 때"
      ],
      "answer": 1,
      "explanation": "chroot 환경에서 root 권한을 가진 프로세스는 chroot를 재호출하거나 열려 있는 파일 디스크립터(fchdir)를 통해 감옥(jail) 외부로 탈출할 수 있습니다."
    },
    {
      "id": "IW2_Q9",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 부팅 과정에서 마스터 부트 레코드(MBR)나 VBR을 감염시켜 OS 커널 로딩 이전에 권한을 장악하고 탐지를 은닉하는 최상위 은닉 루트킷은?",
      "options": [
        "Bootkit",
        "User-mode Rootkit",
        "Firmware Rootkit",
        "Hypervisor Rootkit",
        "Memory Rootkit"
      ],
      "answer": 1,
      "explanation": "부트킷(Bootkit)은 부트 섹터(MBR)를 감염시켜 윈도우 커널이 초기화되기 전에 로드되어 커널 무결성 검증을 우회하고 보안 솔루션을 무력화합니다."
    },
    {
      "id": "IW2_Q10",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 rsyslog 설정 파일에서 'authpriv.* /var/log/secure' 지시자의 의미로 올바른 것은?",
      "options": [
        "모든 인증 관련 로그를 /var/log/secure 파일에 기록한다.",
        "커널 에러만 /var/log/secure에 기록한다.",
        "보안 감사 로그를 원격 서버로 전송한다.",
        "authpriv 시설의 debug 수준 로그만 기록한다.",
        "보안 로그를 /dev/null로 버린다."
      ],
      "answer": 1,
      "explanation": "authpriv 시설(Facility)의 모든 우선순위(*) 로그를 /var/log/secure 파일에 저장하도록 지정한 보안 인증 로그 설정입니다."
    },
    {
      "id": "IW2_Q11",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "스위치 환경에서 스위치의 MAC Address Table(CAM Table)을 무작위 가짜 MAC 주소로 고갈시켜 스위치가 허브처럼 모든 포트로 패킷을 플러딩(Flooding)하게 유도하는 스니핑 공격은?",
      "options": [
        "Switch Jamming (MAC Flooding)",
        "ARP Redirect",
        "ICMP Redirect",
        "DHCP Starvation",
        "VLAN Hopping"
      ],
      "answer": 1,
      "explanation": "Switch Jamming(스위치 재밍)은 CAM 테이블 버퍼를 고갈시켜 스위치가 Fail-Open 상태(Hub 모드)로 전환되게 만들어 트래픽을 가로채는 공격입니다."
    },
    {
      "id": "IW2_Q12",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "출발지 IP를 희생자의 IP로 위조한 후 서브넷의 브로드캐스트 주소로 ICMP Echo Request를 전송하여 대량의 증폭 응답을 유발하는 증폭 반사 공격은?",
      "options": [
        "Smurf Attack",
        "Fraggle Attack",
        "DNS Amplification",
        "NTP Amplification",
        "SNMP Flooding"
      ],
      "answer": 1,
      "explanation": "Smurf 공격은 ICMP Echo를 다이렉트 브로드캐스트로 보내 수많은 호스트가 일제히 희생자에게 Echo Reply를 전송하게 만드는 고전적 대역폭 고갈 공격입니다. (Fraggle은 UDP 사용)"
    },
    {
      "id": "IW2_Q13",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "방화벽 아키텍처 중 외부 네트워크와 내부 네트워크 사이에 스크리닝 라우터 2대와 배스천 호스트를 배치하여 완충 지대(DMZ)를 형성하는 가장 안전한 구성은?",
      "options": [
        "스크린드 서브넷 게이트웨이 (Screened Subnet Gateway)",
        "스크린드 호스트 게이트웨이",
        "듀얼 홈드 게이트웨이",
        "패킷 필터링 라우터",
        "하이브리드 방화벽"
      ],
      "answer": 1,
      "explanation": "스크린드 서브넷 게이트웨이는 외부 라우터와 내부 라우터 사이에 DMZ 망을 두어 배스천 호스트가 침해되더라도 내부망이 즉시 노출되지 않는 가장 견고한 구조입니다."
    },
    {
      "id": "IW2_Q14",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "DNS 캐시 포이즈닝(Cache Poisoning) 공격을 어렵게 만들기 위해 DNS 재귀 질의 시 트랜잭션 ID(TXID)와 함께 출발지 포트(Source Port)를 무작위로 변경하는 기술은?",
      "options": [
        "Source Port Randomization",
        "DNSSEC",
        "Anycast DNS",
        "Split DNS",
        "EDNS0"
      ],
      "answer": 1,
      "explanation": "소스 포트 무작위화(Kaminsky 공격 방어책)는 TXID 16비트 외에 포트 16비트를 무작위화하여 공격자의 위조 응답 적중 확률을 극도로 낮춥니다."
    },
    {
      "id": "IW2_Q15",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "공격자가 클라이언트와 서버 사이에서 TCP 시퀀스 넘버(Sequence Number)를 동기화하고 패킷을 위조 삽입하여 기존 연결을 가로채는 L4 공격은?",
      "options": [
        "TCP Session Hijacking",
        "SYN Flooding",
        "RST Injection",
        "Man-in-the-Middle",
        "Teardrop"
      ],
      "answer": 1,
      "explanation": "TCP 세션 하이재킹은 3-Way Handshake 이후 established 상태의 연결에서 서버와 클라이언트 간 시퀀스 번호를 가로채 세션 통제권을 획득하는 공격입니다."
    },
    {
      "id": "IW2_Q16",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "라우팅 프로토콜 중 BGP 라우팅의 경로 하이재킹(BGP Route Hijacking)을 방지하기 위해 RPKI(Resource Public Key Infrastructure)에서 발행하는 암호화 인증 객체는?",
      "options": [
        "ROA (Route Origin Authorization)",
        "BGPsec",
        "AS-PATH",
        "DNSKEY",
        "X.509 CRL"
      ],
      "answer": 1,
      "explanation": "ROA는 특정 AS(자율시스템) 번호가 해당 IP 프리픽스를 광고할 정당한 권한이 있음을 암호학적으로 서명 증명하는 RPKI 핵심 객체입니다."
    },
    {
      "id": "IW2_Q17",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "침입차단시스템(Firewall)의 세대별 유형 중 OSI 7계층에서 애플리케이션 프록시(Proxy)를 통해 패킷을 중계하며 세부적인 프로토콜 명령어를 검사할 수 있지만 성능 부하가 큰 방식은?",
      "options": [
        "애플리케이션 게이트웨이 (Application Gateway)",
        "패킷 필터링 (Packet Filtering)",
        "상태기반 검사 (Stateful Inspection)",
        "서킷 게이트웨이 (Circuit Gateway)",
        "차세대 방화벽 (NGFW)"
      ],
      "answer": 1,
      "explanation": "애플리케이션 게이트웨이 방식은 각 서비스별 전용 프록시 데몬을 통해 애플리케이션 페이로드까지 완벽히 검사하지만 속도가 느립니다."
    },
    {
      "id": "IW2_Q18",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "NTP 서비스의 'monlist' 쿼리 또는 DNS ANY 쿼리처럼 작은 요청에 대해 수십~수백 배 큰 응답을 반사시키는 공격 방식의 통칭은?",
      "options": [
        "DRDoS (Distributed Reflection Denial of Service)",
        "Slowloris",
        "Smurf",
        "SYN Flood",
        "Teardrop"
      ],
      "answer": 1,
      "explanation": "DRDoS(분산 반사 서비스 거부) 공격은 출발지 IP를 희생자로 위조하여 전 세계 개방형 반사 서버(DNS, NTP, SNMP, Memcached 등)로 질의하여 증폭 트래픽을 집중시킵니다."
    },
    {
      "id": "IW2_Q19",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IPSec 통신에서 양단 간 보안 정책(SP)을 협상하고 암호화 키를 자동으로 생성·교환 및 갱신하기 위해 UDP 500 포트를 사용하는 키 관리 프로토콜은?",
      "options": [
        "IKE (Internet Key Exchange)",
        "ISAKMP",
        "Diffie-Hellman",
        "RADIUS",
        "Kerberos"
      ],
      "answer": 1,
      "explanation": "IKE는 ISAKMP 프레임워크와 Oakley/SKEME 키 교환 프로토콜을 결합하여 SA(Security Association)와 키를 자동 협상하는 프로토콜입니다."
    },
    {
      "id": "IW2_Q20",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "네트워크 장비의 포트 미러링(Port Mirroring / SPAN) 기술을 통해 트래픽을 수집하여 시그니처 패턴과 일치 여부를 수동적으로 분석하는 침입탐지시스템(IDS) 구축 방식은?",
      "options": [
        "In-Line 방식",
        "Out-of-Path (Promiscuous) 방식",
        "Proxy 방식",
        "Host-based 방식",
        "Dual-homed 방식"
      ],
      "answer": 2,
      "explanation": "Out-of-Path(수동형/미러링) 구축은 네트워크 트래픽 흐름에 지장을 주지 않고 복사본을 전달받아 탐지하므로 패킷 전송 지연이 없습니다."
    },
    {
      "id": "IW2_Q21",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "SQL 인젝션 공격 중 에러 메시지가 화면에 출력되지 않는 블라인드 환경에서 참/거짓 조건에 따른 서버 응답 시간 지연(sleep, waitfor delay)을 유발해 데이터를 한 글자씩 추출하는 기법은?",
      "options": [
        "Time-Based Blind SQLi",
        "Boolean-Based Blind SQLi",
        "Error-Based SQLi",
        "Union-Based SQLi",
        "Out-of-Band SQLi"
      ],
      "answer": 1,
      "explanation": "Time-Based Blind SQL 인젝션은 응답 시간 지연 함수(SLEEP(5) 등)의 실행 여부를 측정하여 데이터베이스 정보를 추출하는 공격입니다."
    },
    {
      "id": "IW2_Q22",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "공격자가 서버에 요청을 전송할 때 URL 파라미터에 '../' 또는 인코딩된 '%2e%2e%2f' 문자열을 입력하여 웹 루트 상위의 시스템 파일에 무단 접근하는 취약점은?",
      "options": [
        "Path Traversal (Directory Traversal)",
        "Remote File Inclusion (RFI)",
        "Command Injection",
        "Local File Inclusion (LFI)",
        "Open Redirect"
      ],
      "answer": 1,
      "explanation": "경로 조작(Path Traversal) 취약점은 상위 디렉토리 이동 문자열을 검증하지 않아 시스템 중요 파일(/etc/passwd, win.ini 등)에 접근하는 취약점입니다."
    },
    {
      "id": "IW2_Q23",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 브라우저의 교차 출처 리소스 공유(CORS) 설정에서 보안상 가장 위험한 헤더 조합은?",
      "options": [
        "Access-Control-Allow-Origin: * 및 Access-Control-Allow-Credentials: true",
        "Access-Control-Allow-Origin: https://trust.com",
        "Access-Control-Allow-Methods: GET, POST",
        "Access-Control-Max-Age: 3600",
        "Access-Control-Allow-Headers: Content-Type"
      ],
      "answer": 1,
      "explanation": "모든 오리진(*)을 허용하면서 인증 쿠키 전송(Allow-Credentials: true)을 허용하는 설정은 표준 브라우저에서 차단되거나 심각한 정보 유출 통로가 됩니다."
    },
    {
      "id": "IW2_Q24",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "투명한 iframe을 정상 웹페이지 위에 겹쳐 놓고 사용자가 정상 버튼을 클릭하는 것으로 착각하게 만들어 결제나 권한 변경을 수행하게 하는 UI 레드레싱 공격은?",
      "options": [
        "Clickjacking",
        "CSRF",
        "Phishing",
        "Watering Hole",
        "Typo Squatting"
      ],
      "answer": 1,
      "explanation": "Clickjacking(클릭재킹)은 투명 프레임을 이용해 사용자의 클릭을 가로채는 공격으로, 'X-Frame-Options: DENY' 헤더나 CSP frame-ancestors로 방어합니다."
    },
    {
      "id": "IW2_Q25",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "전자상거래 전자지불 프로토콜 SET(Secure Electronic Transaction)에서 고객의 주문 정보는 상점에게만 보이고 계좌/카드 결제 정보는 카드사에게만 보이도록 보장하는 암호 기술은?",
      "options": [
        "이중 서명 (Dual Signature)",
        "전자봉투",
        "은닉 서명",
        "다자간 서명",
        "임계 서명"
      ],
      "answer": 1,
      "explanation": "SET의 이중 서명(Dual Signature)은 주문 정보 해시와 결제 정보 해시를 합쳐서 서명함으로써 상점은 결제정보를 못 보고 카드사는 주문 세부정보를 못 보게 합니다."
    },
    {
      "id": "IW2_Q26",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "자바(Java) 언어 기반 시큐어코딩에서 세션 하이재킹 및 동시성 오류를 방지하기 위해 싱글톤 객체에서 피해야 하는 변수 사용 방식은?",
      "options": [
        "인스턴스 변수(멤버 변수)에 상태값 및 사용자 세션 정보 저장",
        "지역 변수(Local Variable) 사용",
        "불변 객체(Immutable Object) 사용",
        "ConcurrentHashMap 사용",
        "final 키워드 적용"
      ],
      "answer": 1,
      "explanation": "서블릿이나 스프링 빈처럼 멀티스레드 환경에서 동작하는 싱글톤 객체에 상태를 갖는 인스턴스 멤버 변수를 두면 스레드 간 데이터 오염 및 세션 혼선이 발생합니다."
    },
    {
      "id": "IW2_Q27",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "오라클 DB 등에서 사용자 로그인 인증, 감사 로그 기록, 시스템 이벤트 감지를 위해 특정 테이블 이벤트 발생 시 자동 실행되도록 작성되는 보안 프로그램은?",
      "options": [
        "Trigger (트리거)",
        "Stored Procedure",
        "View",
        "Index",
        "Cursor"
      ],
      "answer": 1,
      "explanation": "데이터베이스 트리거(Trigger)는 DML(INSERT/UPDATE/DELETE)이나 DDL 이벤트 발생 시 자동으로 호출되어 무결성 검증과 실시간 감사 로그를 저장하는 데 쓰입니다."
    },
    {
      "id": "IW2_Q28",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 브라우저의 동일 출처 정책(SOP, Same-Origin Policy)에서 출처(Origin)를 결정하는 3대 요소에 해당하지 않는 것은?",
      "options": [
        "프로토콜 (Scheme)",
        "호스트 (Host / 도메인)",
        "포트 번호 (Port)",
        "URI 경로 (Path)",
        "모두 출처 결정 요소이다."
      ],
      "answer": 4,
      "explanation": "SOP에서 출처는 'Protocol + Host + Port'의 3가지가 일치해야 동일 출처로 판단합니다. URI 경로는 출처 판별에 영향을 주지 않습니다."
    },
    {
      "id": "IW2_Q29",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹사이트 내에서 허용된 스크립트 실행 출처, 이미지 및 스타일 로딩 위치를 엄격히 지정하여 XSS 및 데이터 주입 공격을 원천 완화하는 HTTP 헤더는?",
      "options": [
        "Content-Security-Policy (CSP)",
        "X-XSS-Protection",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Permissions-Policy"
      ],
      "answer": 1,
      "explanation": "CSP(Content Security Policy) 헤더는 브라우저가 다운로드하고 실행할 수 있는 유효한 도메인 화이트리스트를 지정하여 인라인 악성 스크립트 실행을 방지합니다."
    },
    {
      "id": "IW2_Q30",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "OWASP Top 10(2021)에서 1위를 차지하며, 권한 없는 사용자가 URL 조작이나 객체 ID(IDOR) 변조를 통해 타인의 정보나 관리자 기능을 호출하는 취약점 카테고리는?",
      "options": [
        "Broken Access Control (취약한 접근 제어)",
        "Cryptographic Failures",
        "Injection",
        "Insecure Design",
        "Security Misconfiguration"
      ],
      "answer": 1,
      "explanation": "A01:2021 Broken Access Control은 수평적/수직적 권한 우회, 직접 객체 참조(IDOR) 등 사용자의 권한 검증 미흡으로 발생하는 접근제어 결함입니다."
    },
    {
      "id": "IW2_Q31",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "블록 암호화 알고리즘의 운영 모드 중 블록 암호를 스트림 암호처럼 동작하게 하며, 카운터 값을 1씩 증가시키면서 병렬 처리가 가능하여 고속 암호화에 가장 적합한 모드는?",
      "options": [
        "CTR (Counter) 모드",
        "CBC 모드",
        "ECB 모드",
        "CFB 모드",
        "OFB 모드"
      ],
      "answer": 1,
      "explanation": "CTR 모드는 논스(Nonce)와 카운터를 결합하여 키스트림을 생성하므로 이전 블록에 종속되지 않고 완벽한 병렬 암·복호화 처리가 가능합니다."
    },
    {
      "id": "IW2_Q32",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "RSA 공개키 암호 알고리즘의 수학적 안전성의 근간이 되는 계산 복잡도 문제는?",
      "options": [
        "큰 수의 소인수분해 문제 (Prime Factorization)",
        "이산대수 문제 (Discrete Logarithm)",
        "타원곡선 이산대수 문제 (ECDLP)",
        "격자 기반 문제 (Lattice)",
        "배낭 문제 (Knapsack)"
      ],
      "answer": 1,
      "explanation": "RSA는 두 개의 매우 큰 소수 p와 q의 곱 n = p*q를 구하는 것은 쉽지만, n으로부터 p와 q를 찾아내는 소인수분해의 난해성에 안전성을 둡니다."
    },
    {
      "id": "IW2_Q33",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "암호화 해시 함수에서 임의의 두 입력값이 동일한 출력 해시값을 생성하지 않아야 한다는 성질을 뜻하는 용어는?",
      "options": [
        "충돌 저항성 (Collision Resistance)",
        "제1 역상 저항성",
        "제2 역상 저항성",
        "완전 역상 저항성",
        "압축성"
      ],
      "answer": 1,
      "explanation": "충돌 저항성(Collision Resistance)은 H(x) = H(y)를 만족하는 서로 다른 임의의 두 쌍 (x, y)를 찾는 것이 계산상 불가능해야 함을 의미합니다 (생일 패러독스 공격에 대응)."
    },
    {
      "id": "IW2_Q34",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "클락-윌슨(Clark-Wilson) 무결성 모델의 핵심 개념 중 오직 인증된 변환 절차(TP)를 통해서만 제약 데이터 항목(CDI)을 수정할 수 있도록 하여 무결성을 유지하는 원리는?",
      "options": [
        "잘 형성된 트랜잭션 (Well-formed Transaction)",
        "단순 무결성 속성",
        "*-속성",
        "상충 방지 규칙",
        "격자 규칙"
      ],
      "answer": 1,
      "explanation": "Clark-Wilson 모델은 상용 기업 환경의 무결성을 위해 '잘 형성된 트랜잭션(Well-formed Transaction)'과 직무 분리를 통해 데이터를 무단 수정하지 못하게 합니다."
    },
    {
      "id": "IW2_Q35",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "사전 공격(Dictionary Attack)이나 레인보우 테이블 공격을 무력화하기 위해 패스워드 해시 생성 시 랜덤한 솔트(Salt)를 추가하고 반복 해싱(Key Stretching)을 수행하는 표준 암호화 함수는?",
      "options": [
        "PBKDF2 / bcrypt / scrypt / Argon2",
        "MD5",
        "SHA-1",
        "CRC32",
        "Base64"
      ],
      "answer": 1,
      "explanation": "PBKDF2, bcrypt, Argon2 등은 솔트와 수천 번 이상의 반복 연산(키 스트레칭)을 적용하여 GPU를 통한 무차별 대입 공격을 방어합니다."
    },
    {
      "id": "IW2_Q36",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "전자서명의 3대 기능(무결성, 서명자 인증, 부인방지) 중 송신자가 메시지를 보낸 사실을 사후에 부인할 수 없도록 보장하는 기술적 원리는?",
      "options": [
        "송신자 본인만이 보유한 개인키(Private Key)로 서명값을 생성하기 때문",
        "수신자의 공개키로 암호화하기 때문",
        "대칭키를 사용하기 때문",
        "해시 함수가 복호화되기 때문",
        "인증서가 평문으로 전송되기 때문"
      ],
      "answer": 1,
      "explanation": "부인방지(Non-repudiation)는 서명자가 비밀로 간직한 고유의 개인키로만 전자서명이 생성되며, 누구나 서명자의 공개키로 검증할 수 있기 때문에 성립합니다."
    },
    {
      "id": "IW2_Q37",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "CBC 암호화 모드에서 이전 암호문 블록이 전송 중 1비트 에러가 발생했을 때 복호화 시 나타나는 에러 전파(Error Propagation) 현상으로 올바른 것은?",
      "options": [
        "해당 암호 블록 전체가 깨지고, 다음 평문 블록의 동일한 1비트 위치에 에러가 전파된다.",
        "이후의 모든 평문 블록이 영구적으로 복호화 불능 상태가 된다.",
        "해당 블록의 1비트만 깨지고 다른 블록은 전혀 영향이 없다.",
        "아무런 에러도 발생하지 않는다.",
        "이전 블록 전체가 복호화 불능이 된다."
      ],
      "answer": 1,
      "explanation": "CBC 모드 복호화는 P_i = D_k(C_i) XOR C_{i-1} 이므로, C_i의 에러는 해당 블록 P_i를 완전히 망가뜨리고 다음 블록 P_{i+1}의 동일 위치 1비트에 영향을 미친 후 전파가 끝납니다."
    },
    {
      "id": "IW2_Q38",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "비대칭키 암호 알고리즘 중 타원곡선 상의 점 덧셈 연산(ECC)을 활용하여 RSA보다 훨씬 짧은 키 길이(예: 256비트)로 RSA 3072비트 수준의 동등한 보안성을 제공하는 암호 방식은?",
      "options": [
        "ECDSA / ECDH",
        "ElGamal",
        "Rabin",
        "Knapsack",
        "Diffie-Hellman"
      ],
      "answer": 1,
      "explanation": "ECC(Elliptic Curve Cryptography)는 타원곡선 이산대수 문제의 난해성을 이용해 적은 연산량과 짧은 키 길이로 높은 보안을 제공하여 모바일 및 TLS 1.3 표준에 널리 쓰입니다."
    },
    {
      "id": "IW2_Q39",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "Diffie-Hellman 키 교환 프로토콜의 가장 치명적인 취약점으로, 공개 파라미터를 교환할 때 상대방의 신원을 검증하지 못해 발생하는 공격은?",
      "options": [
        "중간자 공격 (Man-in-the-Middle Attack)",
        "재전송 공격",
        "선택평문 공격",
        "사전 대입 공격",
        "타이밍 공격"
      ],
      "answer": 1,
      "explanation": "최초의 순수 디피-헬만 프로토콜은 인증 기능이 없으므로 공격자가 중간에 개입하여 각각 키를 교환하는 중간자(MITM) 공격에 취약합니다. (전자서명 결합 필요)"
    },
    {
      "id": "IW2_Q40",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "암호화 메시지 인증 코드(HMAC)가 보장하는 보안 특성의 조합으로 가장 올바른 것은?",
      "options": [
        "메시지의 무결성 및 송신처 인증",
        "메시지의 기밀성 및 무결성",
        "메시지의 기밀성 및 부인방지",
        "송신처 인증 및 부인방지",
        "가용성 및 기밀성"
      ],
      "answer": 1,
      "explanation": "HMAC(Hash-based MAC)은 비밀 대칭키와 해시 함수를 결합하여 데이터의 무결성(변조 여부)과 송신처 인증을 제공합니다. (대칭키이므로 부인방지는 제공하지 않음)"
    },
    {
      "id": "IW2_Q41",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보보호법상 개인정보 침해 사고 발생 시 부과될 수 있는 과징금 산정 기준으로 가장 올바른 것은?",
      "options": [
        "전체 매출액의 100분의 3 이하 (위반행위와 관련 없는 매출액 제외 가능)",
        "관련 매출액의 100분의 1 이하",
        "전체 매출액의 100분의 5 이하",
        "영업이익의 100분의 10 이하",
        "정액 5억 원 이하"
      ],
      "answer": 1,
      "explanation": "개정 개인정보보호법에 따라 위반 시 '전체 매출액의 3% 이하'의 과징금이 부과될 수 있으며, 다만 기업이 위반행위와 관련 없는 매출액임을 입증한 경우 이를 제외합니다."
    },
    {
      "id": "IW2_Q42",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "공공기관이 개인정보 파일을 구축·운용할 때 개인정보 침해 위험을 사전에 분석·평가하기 위해 개인정보보호위원회에 의무적으로 제출해야 하는 제도는?",
      "options": [
        "개인정보 영향평가 (PIA)",
        "ISMS 인증",
        "취약점 분석평가",
        "보안성 검토",
        "위험수준평가 (TRA)"
      ],
      "answer": 1,
      "explanation": "개인정보 영향평가(PIA)는 5만 명 이상의 민감정보 구축이나 100만 명 이상의 연계 시스템 등 일정 기준 이상의 공공기관 파일 구축 시 사전에 의무 수행합니다."
    },
    {
      "id": "IW2_Q43",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "위험 처리(Risk Treatment) 전략 중 위험도가 높은 정보 자산이나 비즈니스 프로세스 자체를 중단하거나 포기함으로써 위험 발생 가능성을 원천 제거하는 전략은?",
      "options": [
        "위험 회피 (Risk Avoidance)",
        "위험 감소 (Risk Mitigation / Reduction)",
        "위험 전가 (Risk Transfer)",
        "위험 수용 (Risk Acceptance)",
        "위험 공유"
      ],
      "answer": 1,
      "explanation": "위험 회피(Risk Avoidance)는 해당 서비스 운영을 중지하거나 고위험 프로젝트를 취소하여 위험 요인을 근원적으로 배제하는 방식입니다."
    },
    {
      "id": "IW2_Q44",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보보호법상 정보주체의 동의 없이도 개인정보를 처리할 수 있는 합법적 근거로 명시되지 않은 것은?",
      "options": [
        "법률에 특별한 규정이 있거나 법령상 의무를 준수하기 위하여 불가피한 경우",
        "공공기관이 법령 등에서 정하는 소관 업무의 수행을 위하여 불가피한 경우",
        "정보주체와의 계약 체결 및 이행을 위하여 불가피하게 필요한 경우",
        "기업의 단순 이윤 극대화 및 마케팅 목적인 경우",
        "명백히 정보주체 또는 제3자의 급박한 생명, 신체, 재산의 이익을 위하여 필요한 경우"
      ],
      "answer": 4,
      "explanation": "마케팅 목적은 정보주체의 명시적 동의(선택동의)가 필수적이며, 동의 없는 법적 처리 근거가 될 수 없습니다."
    },
    {
      "id": "IW2_Q45",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보통신망법상 침해사고가 발생했을 때 정보통신서비스 제공자가 과학기술정보통신부장관이나 한국인터넷진흥원(KISA)에 신고해야 하는 기한은?",
      "options": [
        "지체 없이 (발견 즉시)",
        "24시간 이내",
        "48시간 이내",
        "72시간 이내",
        "7일 이내"
      ],
      "answer": 1,
      "explanation": "정보통신망법 제48조의3에 따라 정보통신서비스 제공자는 침해사고가 발생한 때에는 지체 없이 그 사실을 과기정통부 또는 KISA에 즉시 신고해야 합니다."
    },
    {
      "id": "IW2_Q46",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 안전성 확보조치 기준에서 비밀번호의 작성 규칙으로 가장 올바른 것은?",
      "options": [
        "문자, 숫자, 특수문자 중 2종류 조합 시 최소 10자리 이상, 3종류 조합 시 최소 8자리 이상",
        "숫자만으로 최소 6자리 이상",
        "문자, 숫자 조합 시 최소 6자리 이상",
        "특수문자 조합 여부와 무관하게 무조건 12자리 이상",
        "생년월일이나 연속된 숫자 사용 권장"
      ],
      "answer": 1,
      "explanation": "안전성 확보조치 기준상 비밀번호는 2종류 조합 시 최소 10자리 이상, 3종류 이상 조합 시 최소 8자리 이상으로 설정해야 합니다."
    },
    {
      "id": "IW2_Q47",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "재해복구센터(DRS) 구축 유형 중 주 센터와 완전히 동일한 실시간 미러링 사이트를 유지하여 RTO를 거의 0(수초~수분)으로 유지하지만 구축 비용이 가장 큰 형태는?",
      "options": [
        "Mirror Site (미러 사이트)",
        "Hot Site",
        "Warm Site",
        "Cold Site",
        "Mobile Site"
      ],
      "answer": 1,
      "explanation": "Mirror Site는 주 센터와 동일한 전산 자원을 이중화하여 실시간 데이터 동기화를 수행함으로써 다운타임과 데이터 손실이 거의 없는 최고 수준의 DR 센터입니다."
    },
    {
      "id": "IW2_Q48",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보보호 정책-지침-절차 체계에서 최고경영자의 보안 의지와 조직의 최상위 기본 방향을 명시하며 개정 주기가 가장 긴 문서는?",
      "options": [
        "정보보호 정책 (Policy)",
        "정보보호 지침 (Standard / Guideline)",
        "정보보호 절차 (Procedure)",
        "작업 지침서",
        "감사 체크리스트"
      ],
      "answer": 1,
      "explanation": "정보보호 정책(Policy)은 조직의 보안 철학과 방향성을 담은 최상위 문서로 경영진 승인을 거쳐 수립되며 원칙적으로 자주 변경되지 않습니다."
    },
    {
      "id": "IW2_Q49",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "ISMS-P 인증기준에서 개인정보 파기 시 적용해야 할 기술적 조치로 가장 옳지 않은 것은?",
      "options": [
        "전자적 파일 형태는 복원이 불가능하도록 완전삭제 소프트웨어 또는 디가우저(Degausser)를 사용한다.",
        "종이 출력물은 분쇄기로 파쇄하거나 소각한다.",
        "휴지통 비우기(Delete)를 수행한 후 별도 조치 없이 보관한다.",
        "일부 파기 시 개인정보를 삭제한 후 복원할 수 없도록 마스킹 처리한다.",
        "파기 관리대장에 파기 일시, 항목, 담당자, 승인자를 기록하고 영구 보존한다."
      ],
      "answer": 3,
      "explanation": "단순 파일 삭제(휴지통 비우기)는 포렌식 도구로 복원이 가능하므로 법령상 '복구 불가능한 영구 파기'로 인정되지 않아 인증 결함에 해당합니다."
    },
    {
      "id": "IW2_Q50",
      "category": "infosec_written",
      "exam": 2,
      "exam_name": "2회 필기 고난도 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보보호법상 정보주체가 자신의 개인정보를 본인 또는 다른 개인정보처리자에게 전송해 줄 것을 요구할 수 있는 마이데이터(MyData) 권리의 명칭은?",
      "options": [
        "개인정보 전송요구권",
        "개인정보 열람요구권",
        "개인정보 처리정지요구권",
        "잊힐 권리 (삭제요구권)",
        "손해배상청구권"
      ],
      "answer": 1,
      "explanation": "개정 개인정보보호법 제35조의2에 신설된 '개인정보 전송요구권'은 정보주체가 자신에 관한 정보를 본인 또는 제3자에게 전송하도록 요구할 수 있는 권리입니다."
    },
    {
      "id": "IW3_Q1",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 시스템에서 /etc/shadow 파일의 각 필드 구조 중 세 번째 필드가 의미하는 것으로 가장 올바른 것은?",
      "options": [
        "최종 패스워드 변경 일자(1970-01-01 이후 일수)",
        "패스워드 최소 사용 기간(일수)",
        "패스워드 최대 사용 기간(일수)",
        "패스워드 만료 경고 기간(일수)",
        "계정 만료 일자"
      ],
      "answer": 1,
      "explanation": "shadow 파일의 필드 순서는 [사용자명:암호화패스워드:최종변경일:최소사용일수:최대사용일수:경고일수:비활성화일수:계정만료일:예약필드]입니다. 세 번째 필드는 1970년 1월 1일(Epoch)을 기준으로 패스워드를 마지막으로 변경한 날짜의 일수입니다."
    },
    {
      "id": "IW3_Q2",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 PAM(Pluggable Authentication Modules) 설정 파일에서 제어 플래그(Control Flag) 중 해당 모듈의 인증이 실패하더라도 즉시 실패를 반환하지 않고 나머지 모듈들을 끝까지 실행한 후 최종 실패를 반환하는 플래그는?",
      "options": [
        "required",
        "requisite",
        "sufficient",
        "optional",
        "include"
      ],
      "answer": 1,
      "explanation": "required는 실패 시 즉시 중단하지 않고 스택 내의 다른 모듈을 끝까지 실행한 후 최종 실패를 반환합니다. 반면 requisite는 실패 시 즉시 나머지 모듈 실행을 중단하고 실패를 반환합니다."
    },
    {
      "id": "IW3_Q3",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "다음 중 버퍼 오버플로우 공격을 방어하기 위해 바이너리 실행 시 스택, 힙, 라이브러리 등의 메모리 주소를 매번 무작위로 변경하여 배치하는 보호 기법은?",
      "options": [
        "ASLR (Address Space Layout Randomization)",
        "DEP / NX (Data Execution Prevention)",
        "Stack Canary",
        "RELRO (Relocation Read-Only)",
        "SafeSEH"
      ],
      "answer": 1,
      "explanation": "ASLR은 프로그램이 메모리에 적재될 때마다 스택, 힙, 라이브러리 주소를 난수화하여 공격자가 고정된 셸코드나 라이브러리 함수(RTL) 주소를 점프하지 못하도록 차단하는 기법입니다."
    },
    {
      "id": "IW3_Q4",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 운영체제에서 시스템 이벤트 로그 중 사용자의 성공 및 실패 로그온 시도를 기록하는 보안 감사 이벤트 ID로 올바른 것은?",
      "options": [
        "로그온 성공: 4624, 로그온 실패: 4625",
        "로그온 성공: 4672, 로그온 실패: 4673",
        "로그온 성공: 1102, 로그온 실패: 1104",
        "로그온 성공: 4720, 로그온 실패: 4726",
        "로그온 성공: 7036, 로그온 실패: 7040"
      ],
      "answer": 1,
      "explanation": "윈도우 Vista/2008 이상에서 로그온 성공 이벤트 ID는 4624, 로그온 실패(브루트포스 탐지 등) 이벤트 ID는 4625입니다. (4720: 계정 생성, 1102: 감사 로그 삭제)"
    },
    {
      "id": "IW3_Q5",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 로그 파일 중 현재 시스템에 로그인한 사용자들의 세션 정보를 담고 있으며 바이너리 형태로 who, w 등의 명령어로 조회되는 로그 파일은?",
      "options": [
        "/var/run/utmp",
        "/var/log/wtmp",
        "/var/log/btmp",
        "/var/log/lastlog",
        "/var/log/secure"
      ],
      "answer": 1,
      "explanation": "/var/run/utmp는 현재 시스템에 로그인되어 있는 사용자 정보를 저장하며, /var/log/wtmp는 과거 성공한 모든 로그인/로그아웃 및 재부팅 기록을 누적 저장합니다."
    },
    {
      "id": "IW3_Q6",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 ext2/3/4 파일시스템에서 root 권한을 가진 공격자라도 파일을 임의로 삭제하거나 수정할 수 없도록 속성을 부여하는 명령어로 올바른 것은?",
      "options": [
        "chattr +i [파일명]",
        "chattr +a [파일명]",
        "chmod 000 [파일명]",
        "setfacl -b [파일명]",
        "chattr +s [파일명]"
      ],
      "answer": 1,
      "explanation": "chattr +i(immutable) 명령을 설정하면 파일이 읽기 전용으로 잠기며, 슈퍼유저(root)라도 속성을 해제(-i)하기 전에는 파일 삭제, 이름 변경, 수정, 링크 생성이 불가능합니다."
    },
    {
      "id": "IW3_Q7",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 umask 값이 027로 설정되어 있을 때 새로 생성되는 일반 파일과 디렉토리의 기본 권한으로 올바른 것은?",
      "options": [
        "파일: 640(-rw-r-----), 디렉토리: 750(drwxr-x---)",
        "파일: 644(-rw-r--r--), 디렉토리: 755(drwxr-xr-x)",
        "파일: 666(-rw-rw-rw-), 디렉토리: 777(drwxrwxrwx)",
        "파일: 600(-rw-------), 디렉토리: 700(drwx------)",
        "파일: 660(-rw-rw----), 디렉토리: 770(drwxrwx---)"
      ],
      "answer": 1,
      "explanation": "기본 파일 최대권한은 666, 디렉토리는 777입니다. umask 027을 적용하면 파일은 666 - 027 = 640(-rw-r-----), 디렉토리는 777 - 027 = 750(drwxr-x---)이 됩니다."
    },
    {
      "id": "IW3_Q8",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "다음 중 레이스 컨디션(Race Condition / TOCTOU) 공격의 원인과 이를 방지하기 위한 보안 조치로 가장 적절한 것은?",
      "options": [
        "검사 시점(Time of Check)과 사용 시점(Time of Use) 사이의 시간 차이를 이용하므로, 임시 파일 생성 시 fstat(), open(O_CREAT|O_EXCL) 등을 사용하고 심볼릭 링크 생성을 통제한다.",
        "스택에 저장된 리턴 주소를 덮어쓰므로 스택 카나리를 주입한다.",
        "포맷 스트링 취약점을 방지하기 위해 printf(str) 대신 printf(\"%s\", str)을 사용한다.",
        "동적 메모리 해제 후 재참조(Use-After-Free)를 방지하기 위해 free 후 NULL을 대입한다.",
        "정수 오버플로우를 방지하기 위해 unsigned 변수 대신 signed 변수만 선언한다."
      ],
      "answer": 1,
      "explanation": "TOCTOU 취약점은 자원의 상태를 검사하는 시점과 이를 실제로 사용하는 시점 사이에 공격자가 심볼릭 링크 등을 조작하여 발생합니다. 원자적(Atomic) 파일 생성(O_CREAT|O_EXCL) 및 파일 디스크립터 기반 fstat 검증이 필수입니다."
    },
    {
      "id": "IW3_Q9",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "유닉스/리눅스 시스템에서 프로세스가 백그라운드로 실행되도록 할 때 터미널이 종료되어도 프로세스가 HUP(SIGHUP) 시그널을 무시하고 계속 실행되도록 지원하는 명령어는?",
      "options": [
        "nohup",
        "nice",
        "renice",
        "kill -9",
        "bg"
      ],
      "answer": 1,
      "explanation": "nohup(no hang up)은 사용자가 로그아웃하거나 터미널 창을 닫아 발생하는 SIGHUP 시그널을 무시하도록 하여 백그라운드 프로세스가 중단 없이 지속되게 합니다."
    },
    {
      "id": "IW3_Q10",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 시스템에서 Active Directory의 인증 프로토콜로 사용되며 티켓(Ticket) 기반으로 인증 및 인가를 수행하는 대표적인 프로토콜은?",
      "options": [
        "Kerberos",
        "NTLMv2",
        "RADIUS",
        "TACACS+",
        "LDAP"
      ],
      "answer": 1,
      "explanation": "윈도우 2000 이후 Active Directory 환경의 기본 인증 프로토콜은 커버로스(Kerberos v5)입니다. KDC(AS, TGS)를 통해 TGT 및 서비스 티켓을 발급받아 상호 인증을 수행합니다."
    },
    {
      "id": "IW3_Q11",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IP 패킷의 헤더 필드 중 패킷이 네트워크 상에서 무한 루프를 도는 것을 방지하기 위해 라우터를 거칠 때마다 1씩 감소하는 8비트 필드는?",
      "options": [
        "TTL (Time to Live)",
        "TOS (Type of Service)",
        "Total Length",
        "Identification",
        "Fragment Offset"
      ],
      "answer": 1,
      "explanation": "TTL(Time to Live)은 패킷의 생존 기간(홉 수)을 정의하는 8비트 필드로, 라우터를 통과할 때마다 1씩 차감되며 0이 되면 패킷이 폐기되고 송신지에 ICMP Time Exceeded(Type 11) 메시지가 회신됩니다."
    },
    {
      "id": "IW3_Q12",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "공격자가 출발지 IP 주소와 목적지 IP 주소를 희생자의 IP 주소와 동일하게 위조하여 패킷을 전송함으로써 희생자 스스로에게 응답 패킷을 반복 전송하여 시스템 자원을 고갈시키는 공격은?",
      "options": [
        "Land Attack",
        "Smurf Attack",
        "TearDrop Attack",
        "SYN Flooding",
        "Ping of Death"
      ],
      "answer": 1,
      "explanation": "Land 공격은 출발지 IP와 목적지 IP, 출발지 포트와 목적지 포트를 동일하게 조작하여 표적 호스트가 자기 자신에게 루프를 돌며 무한 응답하도록 만들어 과부하를 유발하는 공격입니다."
    },
    {
      "id": "IW3_Q13",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "다음 중 TCP 포트 스캔 기법 중 포트가 닫혀 있을 때만 대상 시스템으로부터 RST/ACK 패킷이 회신되고, 열려 있을 때는 응답이 오지 않는 스텔스(Stealth) 스캔 방식이 아닌 것은?",
      "options": [
        "TCP Open (Connect) 스캔",
        "TCP FIN 스캔",
        "TCP Null 스캔",
        "TCP Xmas 스캔",
        "ACK 스캔(방화벽 룰셋 진단용)"
      ],
      "answer": 1,
      "explanation": "TCP Connect(Open) 스캔은 완전한 3-Way Handshake를 수립하므로 시스템 로그에 접속 기록이 명확히 남아 스텔스 스캔이 아닙니다. FIN, Null, Xmas 스캔은 RFC 793 규약의 비정상 플래그 응답(Closed일 때만 RST 회신)을 이용합니다."
    },
    {
      "id": "IW3_Q14",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IPSec 프로토콜의 두 가지 세부 프로토콜인 AH(Authentication Header)와 ESP(Encapsulating Security Payload)에 대한 설명으로 가장 올바른 것은?",
      "options": [
        "AH는 인증, 무결성, 재전송 방지를 제공하지만 기밀성은 제공하지 않으며, ESP는 기밀성을 포함하여 인증과 무결성을 모두 제공할 수 있다.",
        "AH는 기밀성을 제공하고, ESP는 기밀성을 제공하지 않는다.",
        "AH와 ESP는 모두 기본적으로 페이로드 암호화(기밀성)를 강제한다.",
        "AH는 NAT 환경(NAT-T)을 완벽하게 지원하지만 ESP는 지원하지 못한다.",
        "ESP는 전송 모드에서 IP 헤더 전체를 암호화한다."
      ],
      "answer": 1,
      "explanation": "AH는 IP 프로토콜 번호 51번으로 데이터 기밀성(암호화)을 제공하지 않고 인증/무결성만 제공합니다. ESP는 IP 프로토콜 번호 50번으로 대칭키 암호화를 통한 기밀성 및 선택적 인증/무결성을 제공합니다."
    },
    {
      "id": "IW3_Q15",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "DNS 캐시 포이즈닝(Cache Poisoning) 공격을 원천적으로 차단하기 위해 DNS 데이터에 공개키 기반의 전자서명을 적용하여 데이터 무결성을 보장하는 기술은?",
      "options": [
        "DNSSEC (DNS Security Extensions)",
        "DoH (DNS over HTTPS)",
        "DoT (DNS over TLS)",
        "BGPsec",
        "mTLS"
      ],
      "answer": 1,
      "explanation": "DNSSEC는 공개키 암호화 방식을 활용해 DNS 응답 데이터(RRset)에 디지털 서명(RRSIG, DNSKEY, DS 레코드)을 첨부하여 위·변조 및 위조된 캐시 주입을 방어하는 확장 표준입니다."
    },
    {
      "id": "IW3_Q16",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "스니핑(Sniffing) 공격에 대한 설명 중 로컬 이더넷 스위치 환경에서 스위치의 MAC 주소 테이블(CAM 테이블) 버퍼를 위조된 MAC 주소로 가득 채워 스위치를 더미 허브(Hub)처럼 동작하게 만드는 공격 기법은?",
      "options": [
        "Switch Jamming (MAC Flooding)",
        "ARP Spoofing",
        "ICMP Redirect",
        "DHCP Starvation",
        "DNS Spoofing"
      ],
      "answer": 1,
      "explanation": "스위치 재밍(Switch Jamming 또는 MAC Flooding)은 스위치의 MAC 주소 테이블 용량을 초과시켜 Fail-Open 모드로 전환되게 함으로써 모든 포트로 패킷을 브로드캐스팅(Fail-Safe 미흡)하게 유도하는 공격입니다."
    },
    {
      "id": "IW3_Q17",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "무선 네트워크 보안 표준인 WPA3(Wi-Fi Protected Access 3)에서 사전 공격(Dictionary Attack) 및 무차별 대입 공격을 방어하기 위해 PSK(사전 공유 키) 대신 도입한 키 교환 방식은?",
      "options": [
        "SAE (Simultaneous Authentication of Equals)",
        "TKIP (Temporal Key Integrity Protocol)",
        "CCMP (Counter Mode CBC-MAC Protocol)",
        "WEP (Wired Equivalent Privacy)",
        "EAP-TLS"
      ],
      "answer": 1,
      "explanation": "WPA3 개인용(Personal) 표준은 Dragonfly 핸드셰이크 기반의 SAE(동시 동등 인증) 프로토콜을 사용하여 오프라인 딕셔너리 공격을 방어하고 전방향 보안(Forward Secrecy)을 제공합니다."
    },
    {
      "id": "IW3_Q18",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "다음 중 침입탐지시스템(IDS)에서 정상적인 사용자 활동을 침입이나 공격으로 잘못 판단하여 경보를 발생시키는 오류를 뜻하는 용어는?",
      "options": [
        "False Positive (오탐 / 거짓 양성)",
        "False Negative (미탐 / 거짓 음성)",
        "True Positive (정탐 / 참 양성)",
        "True Negative (정상 식별 / 참 음성)",
        "Zero-Day Exploit"
      ],
      "answer": 1,
      "explanation": "False Positive(오탐)은 비공격/정상 행위를 공격으로 잘못 판단한 오류이고, False Negative(미탐)은 실제 공격을 탐지하지 못하고 정상으로 통과시킨 오류입니다."
    },
    {
      "id": "IW3_Q19",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "Snort 룰 헤더에서 외부 인터넷의 임의 포트에서 내부 웹서버(192.168.1.100)의 80번 포트로 향하는 모든 TCP 트래픽을 감시하기 위한 룰 헤더 구문으로 가장 올바른 것은?",
      "options": [
        "alert tcp any any -> 192.168.1.100 80",
        "alert tcp 192.168.1.100 80 -> any any",
        "drop ip any any <> 192.168.1.100 80",
        "pass udp any any -> 192.168.1.100 80",
        "log tcp 192.168.1.100 any -> any 80"
      ],
      "answer": 1,
      "explanation": "Snort 룰 헤더의 기본 형식은 [Action] [Protocol] [SrcIP] [SrcPort] [Direction] [DstIP] [DstPort]입니다. 따라서 'alert tcp any any -> 192.168.1.100 80'이 정확합니다."
    },
    {
      "id": "IW3_Q20",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "네트워크 접근제어(NAC, Network Access Control) 솔루션의 주요 기능에 해당하지 않는 것은?",
      "options": [
        "패킷의 페이로드를 실시간 난독화 및 디코딩하여 SQL 인젝션을 원천 차단",
        "단말기의 무결성 점검 (백신 설치 유무, 최신 보안패치 적용 상태 확인)",
        "미인증 단말기의 네트워크 격리 및 등록 안내(Captive Portal)",
        "IP/MAC 주소 바인딩을 통한 비인가 단말 접속 통제",
        "사용자 역할(RBAC)에 따른 네트워크 VLAN 동적 할당"
      ],
      "answer": 1,
      "explanation": "페이로드를 분석하여 SQL 인젝션 등 웹 공격을 차단하는 것은 웹방화벽(WAF)의 기능입니다. NAC는 단말의 보안 상태 점검, 사용자 인증, 네트워크 접속 통제 및 격리를 담당합니다."
    },
    {
      "id": "IW3_Q21",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "SQL 인젝션 공격을 예방하기 위한 소프트웨어 개발보안 조치 중 동적 쿼리 조립을 금지하고 컴파일된 쿼리에 파라미터를 안전하게 바인딩하는 기법은?",
      "options": [
        "PreparedStatement (파라미터화된 쿼리)",
        "Statement 사용 및 문자열 결합(+)",
        "HTML Entity 치환 라이브러리 적용",
        "클라이언트 자바스크립트 유효성 검증",
        "X-Frame-Options 헤더 설정"
      ],
      "answer": 1,
      "explanation": "PreparedStatement를 사용하면 쿼리의 문법적 구조가 먼저 컴파일된 후 입력값이 단순한 데이터(리터럴)로 바인딩되므로, 악의적인 SQL 구문이 쿼리 구조를 변조하지 못합니다."
    },
    {
      "id": "IW3_Q22",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "XSS(Cross-Site Scripting) 공격의 3대 유형에 해당하지 않는 것은?",
      "options": [
        "Blind SQL Injection",
        "Stored (Persistent) XSS",
        "Reflected (Non-persistent) XSS",
        "DOM-based XSS",
        "Universal XSS (UXSS)"
      ],
      "answer": 1,
      "explanation": "Blind SQL Injection은 SQL 인젝션 공격 유형입니다. XSS 공격은 저장형(Stored), 반사형(Reflected), DOM 기반(DOM-based)으로 분류됩니다."
    },
    {
      "id": "IW3_Q23",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 브라우저에서 document.cookie와 같은 자바스크립트 API를 통해 세션 쿠키를 탈취하지 못하도록 보호하는 HTTP 쿠키 플래그는?",
      "options": [
        "HttpOnly",
        "Secure",
        "SameSite=Strict",
        "Path=/",
        "Domain"
      ],
      "answer": 1,
      "explanation": "HttpOnly 플래그가 설정된 쿠키는 브라우저의 클라이언트 스크립트(JavaScript)에서 접근할 수 없게 차단되어, XSS 취약점이 발생하더라도 쿠키 탈취를 방지합니다."
    },
    {
      "id": "IW3_Q24",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "CSRF(Cross-Site Request Forgery) 공격을 방어하기 위한 대책으로 가장 적절한 것은?",
      "options": [
        "요청마다 서버가 검증하는 예측 불가능한 난수형 CSRF 토큰(Token)을 발급 및 검증하고, SameSite 쿠키 속성을 적용한다.",
        "클라이언트 화면에 비밀번호를 마스킹 처리한다.",
        "사용자의 입력 데이터에 SQL 예약어를 필터링한다.",
        "서버의 응답에 Server 헤더 정보를 숨긴다.",
        "SSL/TLS 암호화 통신(HTTPS)만 단독으로 적용한다."
      ],
      "answer": 1,
      "explanation": "CSRF는 인증된 피해자의 브라우저 권한을 이용해 비인가 요청을 발생시키는 공격이므로, 예측 불가능한 동적 CSRF 토큰 검증, 재인증 요구, SameSite=Strict/Lax 쿠키 적용이 핵심 대책입니다."
    },
    {
      "id": "IW3_Q25",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "파일 업로드 취약점을 방지하기 위한 소프트웨어 개발보안 3대 수칙으로 가장 올바른 조합은?",
      "options": [
        "화이트리스트 확장자 검증, 업로드 파일명 난수화(UUID), 업로드 디렉토리의 실행 권한 박탈",
        "블랙리스트 확장자 검증, 원본 파일명 유지, 업로드 디렉토리 실행 권한 부여",
        "클라이언트 자바스크립트 검증만 적용, 실행 파일 허용, 홈 디렉토리에 저장",
        "확장자 대소문자 변환 허용, 업로드 디렉토리 웹 루트(WebRoot) 내 위치, DB 저장 배제",
        "파일 크기 제한만 10MB로 설정하고 확장자는 무제한 허용"
      ],
      "answer": 1,
      "explanation": "파일 업로드 보안은 1) 허용된 확장자만 명시하는 화이트리스트 검증, 2) 파일명 난수화(UUID) 및 웹 루트 외부 저장, 3) 웹서버 설정에서 해당 디렉토리의 스크립트 실행 권한 제거가 3대 원칙입니다."
    },
    {
      "id": "IW3_Q26",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "아파치(Apache) 웹서버에서 웹 브라우저로 특정 디렉토리에 접근했을 때 index.html 파일이 없더라도 디렉토리 내부의 파일 목록이 화면에 노출되지 않도록 설정하는 지시자는?",
      "options": [
        "Options -Indexes",
        "Options +FollowSymLinks",
        "ServerTokens Prod",
        "AllowOverride None",
        "DirectoryIndex disabled"
      ],
      "answer": 1,
      "explanation": "httpd.conf의 Directory 블록에서 'Options -Indexes'를 지정하면 디렉토리 리스팅(Directory Indexing)이 비활성화되어 파일 목록 노출 취약점이 제거됩니다."
    },
    {
      "id": "IW3_Q27",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "이메일 송신자가 도메인 소유자의 승인을 받은 공인된 메일 서버인지 검증하기 위해 DNS TXT 레코드에 공인 IP 주소 목록을 게시하는 이메일 인증 기술은?",
      "options": [
        "SPF (Sender Policy Framework)",
        "DKIM (DomainKeys Identified Mail)",
        "DMARC (Domain-based Message Authentication)",
        "S/MIME",
        "PGP"
      ],
      "answer": 1,
      "explanation": "SPF는 DNS의 TXT 레코드에 해당 도메인을 대신해 메일을 발송할 수 있는 공인 IP 주소를 등록하여 메일 발송 서버의 진위 여부를 판별하는 기술입니다."
    },
    {
      "id": "IW3_Q28",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "데이터베이스 암호화 방식 중 DBMS 엔진 내부에서 자체적으로 테이블스페이스나 파일 단위로 데이터를 자동 암·복호화하여 애플리케이션의 쿼리 수정이 전혀 필요 없는 방식은?",
      "options": [
        "TDE (Transparent Data Encryption)",
        "API 방식",
        "Plug-In 방식",
        "하이브리드 방식",
        "KMS 방식"
      ],
      "answer": 1,
      "explanation": "TDE(투명한 데이터 암호화)는 DBMS 커널 수준에서 저장소(Datafile, Tablespace)를 암호화하므로 기존 응용프로그램의 소스코드나 SQL 쿼리를 수정할 필요가 없습니다."
    },
    {
      "id": "IW3_Q29",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "SSRF(Server-Side Request Forgery) 공격에 대한 설명으로 가장 올바른 것은?",
      "options": [
        "공격자가 서버 애플리케이션으로 하여금 공격자가 의도한 내부망 주소나 비인가된 외부 URL로 HTTP/TCP 요청을 보내도록 유도하여 내부 비공개 자원을 탈취하는 공격이다.",
        "사용자의 브라우저를 속여 의도하지 않은 금융 이체를 발생시키는 공격이다.",
        "클라이언트 화면에 투명한 iframe을 띄워 클릭을 유도하는 공격이다.",
        "서버의 메모리 힙 공간을 조작하여 임의 코드를 실행하는 공격이다.",
        "DB 쿼리의 참/거짓 응답 시간을 지연시키는 공격이다."
      ],
      "answer": 1,
      "explanation": "SSRF는 서버 측에서 외부 자원을 페치(fetch)하는 로직을 악용하여, 방화벽 뒤에 숨겨진 내부 인프라(127.0.0.1, 169.254.169.254 메타데이터 서버 등)에 비인가 요청을 발생시키는 취약점입니다."
    },
    {
      "id": "IW3_Q30",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "전자상거래 보안 프로토콜인 SET(Secure Electronic Transaction)에서 고객의 주문 정보는 상점만 볼 수 있고 고객의 결제 정보(신용카드 번호)는 금융기관만 볼 수 있도록 이중으로 서명하는 기술은?",
      "options": [
        "이중 서명 (Dual Signature)",
        "전자 봉투 (Digital Envelope)",
        "은닉 서명 (Blind Signature)",
        "다중 서명 (Multi Signature)",
        "위임 서명 (Proxy Signature)"
      ],
      "answer": 1,
      "explanation": "SET의 이중 서명(Dual Signature)은 주문 정보의 해시값과 결제 정보의 해시값을 결합하여 고객의 개인키로 서명함으로써, 상점에는 결제 정보를 숨기고 금융기관에는 주문 세부 내역을 숨기는 기술입니다."
    },
    {
      "id": "IW3_Q31",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "블록 암호 알고리즘 구조 중 입력을 좌우 반으로 나누어 한쪽에만 라운드 함수를 적용하고 좌우를 교환(Swap)하며, 암호화와 복호화 과정이 동일한 구조는?",
      "options": [
        "Feistel 구조 (DES 등)",
        "SPN 구조 (AES, ARIA 등)",
        "스트림 암호 구조 (RC4)",
        "공개키 암호 구조 (RSA)",
        "해시 트리 구조 (Merkle Tree)"
      ],
      "answer": 1,
      "explanation": "Feistel 구조는 데이터를 좌우 블록(L, R)으로 양분하여 라운드를 수행하며, 역원이 존재하지 않아도 복호화가 가능합니다(DES, SEED 등). 반면 SPN은 Substitution-Permutation Network 구조로 전체 블록을 병렬 처리합니다(AES, ARIA)."
    },
    {
      "id": "IW3_Q32",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "미국 표준 블록 암호화 알고리즘인 AES(Advanced Encryption Standard)의 블록 크기와 지원하는 키 길이로 올바른 것은?",
      "options": [
        "블록 크기: 128비트, 키 길이: 128 / 192 / 256비트",
        "블록 크기: 64비트, 키 길이: 56비트",
        "블록 크기: 128비트, 키 길이: 64 / 128비트",
        "블록 크기: 256비트, 키 길이: 256비트 단독",
        "블록 크기: 64비트, 키 길이: 128비트"
      ],
      "answer": 1,
      "explanation": "AES(Rijndael)는 블록 크기가 128비트로 고정되어 있으며, 키 길이에 따라 128비트(10라운드), 192비트(12라운드), 256비트(14라운드)를 지원합니다."
    },
    {
      "id": "IW3_Q33",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "블록 암호 운용 모드 중 이전 라운드의 암호문 블록을 현재 평문 블록과 XOR 연산한 후 암호화하며, 초기화 벡터(IV)를 필요로 하는 모드는?",
      "options": [
        "CBC (Cipher Block Chaining) 모드",
        "ECB (Electronic Codebook) 모드",
        "CFB (Cipher Feedback) 모드",
        "OFB (Output Feedback) 모드",
        "CTR (Counter) 모드"
      ],
      "answer": 1,
      "explanation": "CBC 모드는 직전 단계의 암호문 블록과 현재 평문 블록을 XOR한 후 암호화 알고리즘을 거칩니다. 첫 블록에는 초기화 벡터(IV)가 사용됩니다."
    },
    {
      "id": "IW3_Q34",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "암호학적 해시 함수의 성질 중 주어진 해시값 h에 대해 H(x) = h를 만족하는 입력값 x를 찾는 것이 계산적으로 불가능해야 함을 의미하는 성질은?",
      "options": [
        "제1 역상 저항성 (단방향성)",
        "제2 역상 저항성 (약한 충돌 저항성)",
        "충돌 저항성 (강한 충돌 저항성)",
        "눈사태 효과 (Avalanche Effect)",
        "완전성"
      ],
      "answer": 1,
      "explanation": "제1 역상 저항성(Pre-image Resistance)은 출력값(해시값)이 주어졌을 때 원래의 입력값을 역산하기 불가능해야 한다는 성질(단방향성)입니다."
    },
    {
      "id": "IW3_Q35",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "공개키 인증서 폐기 상태를 실시간으로 확인하기 위해, CRL(인증서 폐기 목록) 다운로드 방식의 시간 지연 및 대역폭 낭비를 개선하여 클라이언트가 인증서 상태를 즉시 질의하는 온라인 프로토콜은?",
      "options": [
        "OCSP (Online Certificate Status Protocol)",
        "SCEP (Simple Certificate Enrollment Protocol)",
        "CMP (Certificate Management Protocol)",
        "PKCS #11",
        "X.509 v3"
      ],
      "answer": 1,
      "explanation": "OCSP(RFC 6960)는 인증서의 일련번호를 기반으로 폐기 여부를 실시간(Good, Revoked, Unknown) 질의 및 응답받을 수 있도록 설계된 경량 프로토콜입니다."
    },
    {
      "id": "IW3_Q36",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "보안 모델 중 군사적 보안 요구를 반영하여 기밀성(Confidentiality) 보장을 목적으로 설계되었으며, 단순 보안 규칙(No Read Up)과 *-보안 규칙(No Write Down)을 적용하는 모델은?",
      "options": [
        "벨-라파둘라 모델 (BLP Model)",
        "비바 무결성 모델 (Biba Model)",
        "클락-윌슨 모델 (Clark-Wilson Model)",
        "만리장성 모델 (Chinese Wall Model)",
        "만다토리 모델 (MAC Model)"
      ],
      "answer": 1,
      "explanation": "BLP(Bell-LaPadula) 모델은 기밀성을 최우선으로 하며, 상위 등급 문서를 읽을 수 없고(No Read Up) 하위 등급으로 문서를 작성할 수 없는(No Write Down) 규칙을 가집니다."
    },
    {
      "id": "IW3_Q37",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "금융 거래 등에서 이해상충(Conflict of Interest)을 방지하기 위해 사용자가 이전에 접근한 데이터 집합에 따라 다른 경쟁 업체의 데이터에 접근하지 못하도록 동적으로 장벽을 형성하는 보안 모델은?",
      "options": [
        "만리장성 모델 (Chinese Wall / Brewer-Nash)",
        "비바 모델 (Biba)",
        "벨-라파둘라 모델 (BLP)",
        "접근제어 행렬 (Access Control Matrix)",
        "격자 모델 (Lattice Model)"
      ],
      "answer": 1,
      "explanation": "차이니즈 월(Chinese Wall, Brewer-Nash) 모델은 주체의 이전 접근 이력을 추적하여 이해상충 관계에 있는 데이터 세그먼트 간의 정보 흐름을 동적으로 차단하는 모델입니다."
    },
    {
      "id": "IW3_Q38",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "정량적 위험 분석에서 단일 손실 예상액(SLE)을 구하는 올바른 공식은?",
      "options": [
        "SLE = 자산 가치(AV) × 노출 계수(EF)",
        "SLE = 연간 발생 빈도(ARO) × 자산 가치(AV)",
        "SLE = 연간 손실 예상액(ALE) / 노출 계수(EF)",
        "SLE = 자산 가치(AV) - 위험 감소치",
        "SLE = 위험도 × 취약점 가중치"
      ],
      "answer": 1,
      "explanation": "단일 손실 예상액 SLE(Single Loss Expectancy) = 자산 가치 AV(Asset Value) × 노출 계수 EF(Exposure Factor)입니다. 또한 연간 손실 예상액 ALE = SLE × ARO(연간 발생 빈도)입니다."
    },
    {
      "id": "IW3_Q39",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "재해복구시스템(DRS)의 복구 수준별 센터 유형 중 주 센터와 완전히 동일한 수준의 하드웨어와 실시간 데이터 미러링을 구축하여 재해 발생 시 수 분 내에 서비스 복구가 가능한 방식은?",
      "options": [
        "Mirror Site (미러 사이트)",
        "Hot Site (핫 사이트)",
        "Warm Site (웜 사이트)",
        "Cold Site (콜드 사이트)",
        "Mobile Site"
      ],
      "answer": 1,
      "explanation": "미러 사이트는 주 센터와 동일한 시스템을 구축하고 데이터를 실시간 복제(동기식)하여 RTO=0(즉각/수분 이내), RPO=0을 달성하는 최고 비용의 DRS 유형입니다."
    },
    {
      "id": "IW3_Q40",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "전자서명에서 송신자가 메시지를 자신의 개인키로 암호화하고, 수신자가 송신자의 공개키로 복호화함으로써 달성할 수 있는 보안 기능의 조합으로 가장 올바른 것은?",
      "options": [
        "인증, 무결성, 부인방지",
        "기밀성, 가용성, 부인방지",
        "기밀성, 인증, 접근통제",
        "가용성, 무결성, 확장성",
        "기밀성, 익명성, 책임추적성"
      ],
      "answer": 1,
      "explanation": "전자서명(송신자 개인키 서명)은 메시지가 송신자에 의해 작성되었음을 입증(인증), 전송 중 변조되지 않았음(무결성), 나중에 발송 사실을 부인할 수 없음(부인방지)을 제공합니다. (기밀성은 수신자의 공개키로 암호화해야 달성됨)"
    },
    {
      "id": "IW3_Q41",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 보호법상 원칙적으로 처리가 금지되며 법령의 구체적 위임이나 별도의 명시적 동의가 있어야만 처리할 수 있는 고유식별정보 4가지에 해당하지 않는 것은?",
      "options": [
        "여권번호",
        "주민등록번호",
        "운전면허번호",
        "외국인등록번호",
        "신용카드번호"
      ],
      "answer": 5,
      "explanation": "개인정보 보호법 시행령 제19조에 따른 고유식별정보 4가지는 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호입니다. 신용카드번호는 고유식별정보에 해당하지 않습니다."
    },
    {
      "id": "IW3_Q42",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보의 안전성 확보조치 기준에 따라 개인정보취급자가 개인정보처리시스템에 접속하여 개인정보를 처리한 접속기록의 최소 보관 기간에 대한 설명으로 올바른 것은?",
      "options": [
        "최소 1년 이상 보관하되, 5만 명 이상의 정보주체에 관한 개인정보를 처리하거나 고유식별정보 또는 민감정보를 처리하는 시스템은 2년 이상 보관해야 한다.",
        "모든 시스템은 예외 없이 3년 이상 보관해야 한다.",
        "접속기록은 최소 6개월 보관하면 충분하다.",
        "5만 명 미만 시스템은 접속기록을 보관할 의무가 면제된다.",
        "접속기록은 5년간 영구 보관해야 한다."
      ],
      "answer": 1,
      "explanation": "안전성 확보조치 기준 제8조에 따라 접속기록은 기본 1년 이상 보관·관리해야 하며, 5만 명 이상 정보주체 개인정보 또는 고유식별정보/민감정보 처리 시스템은 최소 2년 이상 보관해야 합니다."
    },
    {
      "id": "IW3_Q43",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보처리자가 개인정보 유출 사실을 알게 되었을 때 지체 없이 정보주체에게 통지하고 개인정보보호위원회 또는 한국인터넷진흥원(KISA)에 신고해야 하는 법정 기한으로 올바른 것은?",
      "options": [
        "72시간 이내 (1천 명 이상 유출 시 즉시 신고)",
        "24시간 이내",
        "48시간 이내",
        "5일 이내",
        "14일 이내"
      ],
      "answer": 1,
      "explanation": "개정 개인정보 보호법 제34조에 따라 개인정보가 유출된 사실을 안 때에는 지체 없이(정당한 사유가 없는 한 72시간 이내) 정보주체에게 통지하고, 1천 명 이상 유출된 경우 전문기관(보호위/KISA)에 신고해야 합니다."
    },
    {
      "id": "IW3_Q44",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "ISMS-P 인증 기준(총 102개)의 3대 영역과 각 영역별 세부 기준 개수로 올바르게 짝지어진 것은?",
      "options": [
        "1영역 관리체계 수립 및 운영(16개) / 2영역 보호대책 요구사항(64개) / 3영역 개인정보 처리단계별 요구사항(22개)",
        "1영역 관리체계(20개) / 2영역 기술보안(50개) / 3영역 물리보안(32개)",
        "1영역 기밀성(30개) / 2영역 무결성(40개) / 3영역 가용성(32개)",
        "1영역 기본요건(10개) / 2영역 침해대응(70개) / 3영역 개인정보(22개)",
        "1영역 인적보안(15개) / 2영역 시스템보안(65개) / 3영역 법적준거성(22개)"
      ],
      "answer": 1,
      "explanation": "ISMS-P 인증 기준은 1영역 관리체계 수립 및 운영 16개, 2영역 보호대책 요구사항 64개, 3영역 개인정보 처리단계별 요구사항 22개로 총 102개 기준입니다."
    },
    {
      "id": "IW3_Q45",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보통신망법상 정보보호최고책임자(CISO)의 겸직 제한 규정이 적용되는 대기업의 기준으로 올바른 것은?",
      "options": [
        "자산총액 5조 원 이상이거나, 자산총액 5천억 원 이상이면서 정보보호관리체계(ISMS) 의무대상자인 기업",
        "직원 수 1,000명 이상인 모든 기업",
        "자본금 100억 원 이상인 코스닥 상장사",
        "연간 매출액 1천억 원 이상인 모든 법인",
        "ISMS 인증을 자율 신청한 모든 중소기업"
      ],
      "answer": 1,
      "explanation": "정보통신망법 제45조의3에 따라 자산총액 5조 원 이상인 정보통신서비스 제공자 또는 자산총액 5천억 원 이상이면서 ISMS 의무대상자인 기업의 CISO는 정보기술(CIO)이나 기타 임원 직무를 겸직할 수 없습니다."
    },
    {
      "id": "IW3_Q46",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 보호법상 개인정보의 파기 의무에 따라 보유기간의 경과, 개인정보의 처리 목적 달성 등 개인정보가 불필요하게 되었을 때 파기해야 하는 기한으로 올바른 것은?",
      "options": [
        "정당한 사유가 없는 한 불필요하게 된 날로부터 5일 이내",
        "불필요하게 된 날로부터 10일 이내",
        "불필요하게 된 날로부터 14일 이내",
        "불필요하게 된 날로부터 30일 이내",
        "해당 분기 종료일까지"
      ],
      "answer": 1,
      "explanation": "개인정보 보호법 제21조 및 시행령 제16조에 따라 개인정보가 불필요하게 되었을 때에는 정당한 사유가 없는 한 그로부터 5일 이내에 영구 파기해야 합니다."
    },
    {
      "id": "IW3_Q47",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보통신기반 보호법에 따른 주요정보통신기반시설 취약점 분석·평가의 법정 주기로 올바른 것은?",
      "options": [
        "매년 1회 이상 정기적 실시",
        "2년에 1회 실시",
        "3년에 1회 실시",
        "침해사고 발생 시에만 실시",
        "반기 1회 실시"
      ],
      "answer": 1,
      "explanation": "정보통신기반 보호법 제9조에 따라 관리기관의 장은 소관 주요정보통신기반시설에 대하여 매년 취약점을 분석·평가하여야 합니다."
    },
    {
      "id": "IW3_Q48",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "전자서명법상 공인전자서명 제도가 폐지된 이후 전자서명의 효력에 관한 원칙으로 가장 올바른 것은?",
      "options": [
        "전자서명이라는 이유만으로 법적 효력이 부인되지 않으며, 당사자 간의 약정에 따른 전자서명은 서명·날인으로서의 효력을 가진다.",
        "정부가 인증한 단 1개의 전자서명만 법적 효력을 가진다.",
        "블록체인 기반의 전자서명만 법적 효력이 인정된다.",
        "전자서명은 법정에서 서면 증거로서의 효력을 상실하였다.",
        "금융기관용 공동인증서만 유일한 공적 효력을 인정받는다."
      ],
      "answer": 1,
      "explanation": "2020년 개정 전자서명법에 따라 공인인증서 제도가 폐지되고 다양한 민간 전자서명(카카오, 네이버, 패스 등)이 동일한 법적 효력을 갖게 되었습니다."
    },
    {
      "id": "IW3_Q49",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 보호법상 개인정보 침해 사고로 인하여 정보주체가 입은 손해에 대해 법원이 인정할 수 있는 징벌적 손해배상액의 상한으로 올바른 것은?",
      "options": [
        "손해액의 5배를 넘지 않는 범위",
        "손해액의 3배를 넘지 않는 범위",
        "손해액의 10배를 넘지 않는 범위",
        "정액 10억 원 한도",
        "손해액의 2배 범위"
      ],
      "answer": 1,
      "explanation": "개인정보 보호법 제39조 제3항에 따라 개인정보처리자의 고의 또는 중대한 과실로 인하여 개인정보가 분실·도난·유출·위조·변조 또는 훼손된 경우 손해액의 5배를 넘지 않는 범위에서 배상액을 정할 수 있습니다."
    },
    {
      "id": "IW3_Q50",
      "category": "infosec_written",
      "exam": 3,
      "exam_name": "3회 필기 최신 기출 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "클라우드 컴퓨팅 보안 가이드라인에 따라 클라우드 서비스 이용자(고객)와 공급자(CSP) 간의 보안 책임 분무 모델(Shared Responsibility Model)에 관한 설명으로 가장 올바른 것은?",
      "options": [
        "IaaS 환경에서 물리적 인프라와 하이퍼바이저 보안은 클라우드 사업자가 담당하고, 게스트 OS 패치 및 애플리케이션 보안은 이용자가 담당한다.",
        "SaaS 환경에서는 고객이 서버 운영체제 패치와 하드웨어 암호화를 담당한다.",
        "PaaS 환경에서는 고객이 네트워크 스위치와 물리적 데이터센터 경비를 담당한다.",
        "모든 클라우드 모델에서 데이터 보안의 최종 책임은 전적으로 클라우드 서비스 공급자에게 귀속된다.",
        "IaaS에서는 이용자가 하이퍼바이저 취약점을 직접 패치해야 한다."
      ],
      "answer": 1,
      "explanation": "IaaS(Infrastructure as a Service) 모델에서는 CSP가 물리 인프라, 전력, 네트워크, 가상화 하이퍼바이저를 책임지며, 고객은 가상머신 내의 게스트 OS, 방화벽 설정, 미들웨어, 애플리케이션, 데이터의 보안을 책임집니다."
    },
    {
      "id": "IW4_Q1",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 커널의 권한 통제 모델 중 전통적인 임의적 접근통제(DAC)의 한계를 극복하고, 프로세스와 객체마다 보안 컨텍스트(라벨)를 부여하여 강제적 접근통제(MAC)를 구현하는 커널 보안 모듈은?",
      "options": [
        "SELinux (Security-Enhanced Linux)",
        "AppArmor",
        "iptables",
        "PAM",
        "Chroot"
      ],
      "answer": 1,
      "explanation": "SELinux는 미국 NSA가 개발한 리눅스 커널용 MAC(강제적 접근통제) 보안 서브시스템으로, 주체(프로세스)와 객체(파일, 소켓 등)에 Type Enforcement 라벨을 부여해 root 권한 탈취 시에도 피해를 격리합니다."
    },
    {
      "id": "IW4_Q2",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 시스템에서 특정 디렉토리에 생성된 파일은 오직 파일의 소유자나 root 관리자만이 삭제 또는 이름 변경을 할 수 있도록 제한하는 특수 권한은?",
      "options": [
        "Sticky Bit (1000)",
        "SetUID (4000)",
        "SetGID (2000)",
        "Immutable (+i)",
        "Append Only (+a)"
      ],
      "answer": 1,
      "explanation": "Sticky Bit(권한값 1000, 표기 t)는 /tmp 디렉토리처럼 누구나 쓰기 권한이 있는 공용 디렉토리에서 다른 사용자가 생성한 파일을 타인이 임의로 삭제하거나 이동하지 못하도록 보호합니다."
    },
    {
      "id": "IW4_Q3",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "메모리 보호 기법 중 실행 코드 영역(Text Segment)을 제외한 데이터(Data), 스택(Stack), 힙(Heap) 세그먼트에서 CPU 명령어 실행을 하드웨어적으로 원천 차단하는 기술은?",
      "options": [
        "DEP / NX (Data Execution Prevention / Never eXecute)",
        "ASLR",
        "Stack Shield",
        "SafeSEH",
        "Shadow Stack"
      ],
      "answer": 1,
      "explanation": "DEP/NX(No-Execute) 비트는 메모리 영역 중 코드 영역이 아닌 스택이나 힙에 주입된 악의적인 셸코드(Shellcode)가 CPU에 의해 실행되는 것을 하드웨어(CPU NX 비트) 수준에서 차단합니다."
    },
    {
      "id": "IW4_Q4",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 시스템 로그 데몬(rsyslog)의 설정 파일(/etc/rsyslog.conf)에서 시설(Facility)과 심각도(Priority)에 따른 로그 처리 문법 중 'authpriv.* /var/log/secure'의 의미로 올바른 것은?",
      "options": [
        "개인 인증 및 보안 관련(authpriv) 모든 레벨(*)의 로그를 /var/log/secure 파일에 기록한다.",
        "인증 실패 로그만 /var/log/secure에 기록한다.",
        "커널 메시지만 /var/log/secure에 기록한다.",
        "모든 데몬의 오류 로그를 암호화하여 저장한다.",
        "원격 로그 서버로만 전송한다."
      ],
      "answer": 1,
      "explanation": "authpriv는 SSH, su, sudo 등 개인 인증 및 보안 인가와 관련된 시설(Facility)이며, .*는 디버그부터 이머전시까지 모든 심각도 레벨의 메시지를 지정된 파일(/var/log/secure)에 저장하라는 의미입니다."
    },
    {
      "id": "IW4_Q5",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스/유닉스 환경에서 시스템 침해 후 공격자가 백도어 프로세스나 네트워크 포트를 숨기기 위해 ps, netstat 등의 시스템 명령어를 변조하거나 커널 모듈을 조작하는 악성 소프트웨어는?",
      "options": [
        "Rootkit (루트킷)",
        "Ransomware (랜섬웨어)",
        "Worm (웜)",
        "Spyware (스파이웨어)",
        "Logic Bomb (논리폭탄)"
      ],
      "answer": 1,
      "explanation": "루트킷(Rootkit)은 관리자(root) 권한 획득 후 자신의 존재(프로세스, 파일, 포트, 로그)를 숨기고 지속적인 백도어 접근을 유지하기 위해 시스템 바이너리나 커널 시스템 콜 테이블을 조작하는 은닉형 악성 도구 모음입니다."
    },
    {
      "id": "IW4_Q6",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 레지스트리에서 부팅 시 또는 사용자 로그인 시 자동으로 실행되도록 등록된 악성코드를 탐지하기 위해 반드시 점검해야 하는 대표적인 Run 키 경로는?",
      "options": [
        "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\EventLog",
        "HKEY_CLASSES_ROOT\\.exe",
        "HKEY_CURRENT_CONFIG\\System",
        "HKEY_USERS\\.DEFAULT\\Control Panel"
      ],
      "answer": 1,
      "explanation": "윈도우에서 자동 실행되는 시작 프로그램 및 지속성(Persistence) 백도어는 주로 HKLM 및 HKCU의 Software\\Microsoft\\Windows\\CurrentVersion\\Run(또는 RunOnce) 키에 등록됩니다."
    },
    {
      "id": "IW4_Q7",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 crontab 설정에서 매주 월요일 오전 3시 30분에 특정 백업 스크립트(/root/backup.sh)를 정기 실행하도록 지정하는 구문으로 올바른 것은?",
      "options": [
        "30 3 * * 1 /root/backup.sh",
        "3 30 * * 1 /root/backup.sh",
        "* 3 30 * 1 /root/backup.sh",
        "30 3 1 * * /root/backup.sh",
        "0 3 30 * * /root/backup.sh"
      ],
      "answer": 1,
      "explanation": "crontab 필드 순서는 [분(0-59) 시(0-23) 일(1-31) 월(1-12) 요일(0-7, 1=월요일)]입니다. 따라서 30분, 3시, 매일, 매월, 월요일(1)인 '30 3 * * 1'이 올바릅니다."
    },
    {
      "id": "IW4_Q8",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "포맷 스트링(Format String) 취약점이 발생하는 원인과 이를 이용한 공격에 대한 설명으로 가장 올바른 것은?",
      "options": [
        "printf(buf)와 같이 서식 지정자 없이 사용자 입력을 출력 함수의 포맷 인자로 직접 전달할 때 발생하며, %x, %s로 메모리를 훔쳐보거나 %n으로 임의 주소에 값을 쓸 수 있다.",
        "입력 버퍼의 크기를 초과하여 리턴 주소를 직접 덮어쓰는 공격이다.",
        "동적 할당된 힙 청크의 메타데이터(fd, bk 포인터)를 조작하는 공격이다.",
        "커널 권한 상승을 위해 디바이스 드라이버의 IOCTL 인터페이스를 악용하는 공격이다.",
        "난수 생성기의 시드(seed) 값이 고정되어 발생하는 암호학적 취약점이다."
      ],
      "answer": 1,
      "explanation": "포맷 스트링 취약점은 프로그래머가 서식 문자열(%s 등)을 명시하지 않고 사용자 입력을 직접 printf(input) 형태로 전달할 때 발생하며, 공격자는 %x로 메모리를 유출하거나 %n 지시자로 지정된 메모리 주소에 기록된 바이트 수를 덮어쓸 수 있습니다."
    },
    {
      "id": "IW4_Q9",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "유닉스/리눅스 부팅 단계 중 커널이 메모리에 적재된 후 가장 먼저 실행되어 PID 1번을 부여받고 모든 사용자 공간 프로세스의 부모가 되는 초기화 프로세스는?",
      "options": [
        "init (또는 systemd)",
        "swapper (PID 0)",
        "kthreadd (PID 2)",
        "bash",
        "login"
      ],
      "answer": 1,
      "explanation": "리눅스 부팅 과정에서 커널 초기화 완료 후 사용자 공간(User Space)에서 가장 먼저 구동되는 프로세스는 PID 1번인 init(전통적 SysV) 또는 systemd(현대적 리눅스)입니다."
    },
    {
      "id": "IW4_Q10",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "윈도우 운영체제의 BitLocker 기능과 같이 하드웨어 기반으로 암호화 키를 안전하게 보관하고 부팅 무결성을 검증하는 보안 전용 마이크로컨트롤러 칩셋은?",
      "options": [
        "TPM (Trusted Platform Module)",
        "HSM (Hardware Security Module)",
        "UEFI",
        "Secure Boot",
        "Intel SGX"
      ],
      "answer": 1,
      "explanation": "TPM(신뢰 플랫폼 모듈)은 메인보드에 탑재되어 암호키 생성, 저장, 측정(PCR), 하드웨어 기반 부팅 무결성 검증을 수행하는 국제 표준 보안 칩입니다."
    },
    {
      "id": "IW4_Q11",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "TCP SYN Flooding 공격을 방어하기 위해 서버가 SYN 수신 시 백로그 큐(Backlog Queue)에 연결 자원을 할당하지 않고, 연결 정보를 인코딩한 특별한 초기 시퀀스 번호(ISN)를 SYN/ACK 패킷에 담아 응답하는 기법은?",
      "options": [
        "SYN Cookie (SYN 쿠키)",
        "RST Cookie",
        "TCP TFO (TCP Fast Open)",
        "Keep-Alive",
        "TCP Window Scaling"
      ],
      "answer": 1,
      "explanation": "SYN 쿠키는 서버의 SYN 수신 큐(SYN Backlog) 고갈을 방지하기 위해 클라이언트 IP, 포트, 타임스탬프, 서버 비밀키를 해시하여 SYN/ACK의 Sequence Number로 반환한 후, 최종 ACK가 올 때만 소켓을 생성하는 방어 기법입니다."
    },
    {
      "id": "IW4_Q12",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "스머프(Smurf) 공격과 프래글(Fraggle) 공격이 희생자 호스트를 증폭 공격하기 위해 악용하는 프로토콜의 조합으로 올바른 것은?",
      "options": [
        "Smurf: ICMP Echo Request, Fraggle: UDP (포트 7번 Echo / 포트 19번 Chargen)",
        "Smurf: TCP SYN, Fraggle: ICMP",
        "Smurf: IGMP, Fraggle: SNMP",
        "Smurf: DNS, Fraggle: NTP",
        "Smurf: ARP, Fraggle: RARP"
      ],
      "answer": 1,
      "explanation": "Smurf 공격은 출발지를 피해자 IP로 위조한 ICMP Echo Request를 브로드캐스트하여 대량의 ICMP Echo Reply를 유발하며, Fraggle 공격은 이를 UDP Echo(7번) 또는 Chargen(19번) 포트로 수행하는 증폭 공격입니다."
    },
    {
      "id": "IW4_Q13",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IP 단편화(Fragmentation) 오프셋 값을 고의로 중복되거나 비정상적으로 겹치게(Overlap) 조작하여 수신 시스템이 패킷을 재조합(Reassembly)하는 과정에서 충돌이나 시스템 다운을 유발하는 DoS 공격은?",
      "options": [
        "TearDrop Attack (티어드롭)",
        "Land Attack",
        "Bonk Attack",
        "Boink Attack",
        "Ping of Death"
      ],
      "answer": 1,
      "explanation": "TearDrop 공격은 IP 헤더의 Fragment Offset과 Data Length 값을 의도적으로 중첩되게 조작하여 수신측 OS가 재조합 시 메모리 참조 오류로 크래시를 일으키게 하는 취약점 공격입니다."
    },
    {
      "id": "IW4_Q14",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "HTTP 프로토콜의 특성을 악용한 L7 DoS 공격 중 웹서버로 불완전한 HTTP 헤더(끝을 알리는 빈 줄 \\r\\n\\r\\n 미전송)를 전송하고 비정상적인 추가 헤더를 극도로 느리게 지속 전송하여 서버의 동시 연결 스레드를 고갈시키는 공격은?",
      "options": [
        "Slowloris (Slow HTTP Header DoS)",
        "Slow HTTP POST (R.U.D.Y)",
        "Slow HTTP Read DoS",
        "HTTP GET Flooding",
        "Hulk DoS"
      ],
      "answer": 1,
      "explanation": "Slowloris는 헤더의 마지막 개행(\\r\\n\\r\\n)을 보내지 않고 수십 초 간격으로 더미 헤더(X-a: b\\r\\n)를 찔끔찔끔 보내어 웹서버의 연결 타임아웃을 연장시키며 가용 스레드/프로세스를 모두 잠식하는 공격입니다."
    },
    {
      "id": "IW4_Q15",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IPSec 통신에서 보안 연계(SA: Security Association)를 동적으로 협상하고 대칭 암호화 키를 안전하게 교환하기 위해 사용하는 핵심 키 관리 프로토콜은?",
      "options": [
        "IKE (Internet Key Exchange)",
        "ISAKMP 단독",
        "Oakley",
        "SKEME",
        "Diffie-Hellman 단독"
      ],
      "answer": 1,
      "explanation": "IKE(UDP 500번/4500번)는 ISAKMP 프레임워크와 Oakley 및 SKEME 키 교환 프로토콜을 결합하여 양 종단 간 암호화 알고리즘, 해시 방식, 키 수명 등을 협상하고 SA를 자동 생성하는 표준 프로토콜입니다."
    },
    {
      "id": "IW4_Q16",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "NTP, DNS, SSDP, Memcached 서버와 같이 응답 크기가 요청 크기에 비해 수십 배에서 수만 배 이상 큰 비연결형(UDP) 서비스를 악용하여 표적 시스템에 대량의 트래픽을 집중시키는 DDoS 공격 유형은?",
      "options": [
        "DRDoS (Distributed Reflection DoS / 반사 증폭 공격)",
        "SYN Flooding",
        "HTTP GET Flooding",
        "TearDrop",
        "Ping of Death"
      ],
      "answer": 1,
      "explanation": "DRDoS(분산 반사 서비스 거부)는 출발지 IP를 피해자 IP로 변조한 후 증폭율이 높은 공개 UDP 서버(반사체)들에 질의를 전송하여 피해자에게 막대한 반사 트래픽이 쏟아지게 만드는 공격입니다."
    },
    {
      "id": "IW4_Q17",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "SSL/TLS 통신에서 클라이언트가 하나의 웹서버 IP 주소에서 여러 개의 독립된 도메인(가상 호스트)과 개별 SSL 인증서를 바인딩하여 안전하게 서비스할 수 있도록 확장한 기술은?",
      "options": [
        "SNI (Server Name Indication)",
        "ALPN (Application-Layer Protocol Negotiation)",
        "OCSP Stapling",
        "HSTS",
        "Session Ticket"
      ],
      "answer": 1,
      "explanation": "SNI는 클라이언트가 TLS 핸드셰이크의 ClientHello 메시지에 접속하려는 도메인 이름을 포함하여 전송함으로써, 서버가 암호화 핸드셰이크 이전에 적절한 도메인의 SSL 인증서를 제시할 수 있게 하는 확장 규격입니다."
    },
    {
      "id": "IW4_Q18",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "다음 중 침입방지시스템(IPS)과 침입탐지시스템(IDS)의 가장 결정적인 차이점에 대한 설명으로 올바른 것은?",
      "options": [
        "IDS는 미러링(Out-of-Path) 방식으로 트래픽을 감시하여 침입 탐지 및 알람에 주력하고, IPS는 인라인(In-Line) 경로에 배치되어 탐지 즉시 패킷을 능동적으로 차단(Drop)한다.",
        "IDS는 시그니처 기반이고, IPS는 이상 탐지 기반이다.",
        "IDS는 하드웨어 장비이고, IPS는 소프트웨어 프로그램이다.",
        "IDS는 L7 트래픽만 보고, IPS는 L3 트래픽만 본다.",
        "IPS는 암호화된 트래픽을 복호화하지 못한다."
      ],
      "answer": 1,
      "explanation": "IDS는 스위치 미러(SPAN) 포트를 통해 패킷 사본을 분석하므로 실시간 차단 능력이 제한적인 반면, IPS는 네트워크 인라인(In-Line) 상에 물리적으로 직렬 연결되어 악성 패킷을 즉각 폐기(Drop)할 수 있습니다."
    },
    {
      "id": "IW4_Q19",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "가상사설망(VPN) 프로토콜 중 OSI 7계층 중 2계층(데이터링크 계층)에서 터널링을 수행하며, 마이크로소프트와 시스코의 기술이 결합되어 IPsec과 함께 자주 사용되는 프로토콜은?",
      "options": [
        "L2TP (Layer 2 Tunneling Protocol)",
        "PPTP",
        "IPSec",
        "SSL VPN",
        "WireGuard"
      ],
      "answer": 1,
      "explanation": "L2TP(RFC 2661)는 2계층 터널링 프로토콜로 시스코의 L2F와 MS의 PPTP를 결합한 규격입니다. 자체 암호화 기능이 없으므로 통상 IPSec(L2TP/IPSec)과 결합하여 기밀성을 보장합니다."
    },
    {
      "id": "IW4_Q20",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "방화벽의 구축 형태 중 외부 네트워크와 내부 사설망 사이에 양쪽 네트워크와 격리된 완충 지대(DMZ)를 형성하고, 외부 공개 서버(웹, 메일, DNS)들을 배치하는 구성 방식은?",
      "options": [
        "스크린드 서브넷 게이트웨이 (Screened Subnet)",
        "스크리닝 라우터 (Screening Router)",
        "베스천 호스트 단독 구성",
        "듀얼 홈드 게이트웨이 (Dual-Homed)",
        "스크린드 호스트 게이트웨이 (Screened Host)"
      ],
      "answer": 1,
      "explanation": "스크린드 서브넷 게이트웨이는 외부 방화벽과 내부 방화벽 사이에 DMZ(완충 지대) 서브넷을 구축하여 공개 서버 침해 시에도 내부 사설망으로의 직접 침투를 차단하는 가장 안전하고 표준적인 방화벽 구성입니다."
    },
    {
      "id": "IW4_Q21",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 브라우저의 보안 헤더 중 웹사이트가 HTTPS 프로토콜로만 안전하게 접속되도록 강제하고, 사용자의 평문(HTTP) 접속 시도를 브라우저 내부에서 강제로 HTTPS로 리다이렉트하는 헤더는?",
      "options": [
        "Strict-Transport-Security (HSTS)",
        "Content-Security-Policy (CSP)",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Access-Control-Allow-Origin"
      ],
      "answer": 1,
      "explanation": "HSTS(Strict-Transport-Security) 헤더는 브라우저에게 일정 기간 동안(max-age) 해당 도메인에 접근할 때 평문 HTTP 연결을 일절 시도하지 말고 무조건 HTTPS로만 통신하도록 강제하여 SSL Stripping 공격을 방어합니다."
    },
    {
      "id": "IW4_Q22",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 브라우저에서 실행될 수 있는 자바스크립트, CSS, 이미지 등의 신뢰할 수 있는 출처(Origin)를 서버가 HTTP 응답 헤더로 명시하여 XSS 공격 및 데이터 인젝션을 원천 차단하는 표준 보안 헤더는?",
      "options": [
        "Content-Security-Policy (CSP)",
        "X-XSS-Protection",
        "X-Frame-Options",
        "Permissions-Policy",
        "Referrer-Policy"
      ],
      "answer": 1,
      "explanation": "CSP(Content Security Policy)는 웹 페이지에서 로드할 수 있는 스크립트 출처(script-src), 스타일(style-src) 등을 화이트리스트로 제한하고 인라인 스크립트 실행을 금지하여 XSS를 강력하게 방어합니다."
    },
    {
      "id": "IW4_Q23",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "클릭재킹(Clickjacking / UI Redressing) 공격을 방어하기 위해 웹 페이지가 다른 사이트의 <frame>, <iframe>, <object> 내에 삽입되어 렌더링되는 것을 방지하는 HTTP 헤더와 설정값으로 가장 적절한 것은?",
      "options": [
        "X-Frame-Options: DENY (또는 SAMEORIGIN)",
        "X-Content-Type-Options: nosniff",
        "Content-Type: text/html",
        "Access-Control-Allow-Credentials: true",
        "Cache-Control: no-cache"
      ],
      "answer": 1,
      "explanation": "X-Frame-Options 헤더를 DENY(어디서도 프레임 삽입 불가) 또는 SAMEORIGIN(동일 출처에서만 허용)으로 지정하면 투명한 iframe을 이용한 클릭재킹을 방어할 수 있습니다."
    },
    {
      "id": "IW4_Q24",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "서버 측 템플릿 엔진(Jinja2, Thymeleaf, Freemarker 등)에 사용자의 악의적인 입력값이 검증 없이 전달되어 서버 측에서 임의 파이썬/자바 코드가 원격으로 실행되는 취약점은?",
      "options": [
        "SSTI (Server-Side Template Injection)",
        "CSRF",
        "XSS",
        "IDOR (Insecure Direct Object Reference)",
        "Open Redirect"
      ],
      "answer": 1,
      "explanation": "SSTI(서버 사이드 템플릿 인젝션)는 {{7*7}}과 같은 템플릿 표현식이 서버 측에서 평가되어 최종적으로 원격 코드 실행(RCE)으로 이어지는 고위험 취약점입니다."
    },
    {
      "id": "IW4_Q25",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "자바(Java) 시큐어코딩에서 파일 다운로드 취약점(경로 조작 / Directory Traversal)을 방어하기 위해 사용하는 안전한 경로 정규화 및 검증 메서드는?",
      "options": [
        "File.getCanonicalPath() 및 허용된 루트 디렉토리 시작(startsWith) 검증",
        "File.getAbsolutePath() 단독 사용",
        "String.replace(\"../\", \"\") 1회 치환",
        "File.getName()만 확인",
        "URLEncoder.encode()"
      ],
      "answer": 1,
      "explanation": "단순 문자열 치환(..././)은 우회될 수 있으므로, getCanonicalPath()를 사용하여 파일 시스템의 절대 정규 경로를 구한 후, 허용된 루트 디렉토리 경로로 시작하는지(startsWith) 엄격히 검증해야 합니다."
    },
    {
      "id": "IW4_Q26",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 애플리케이션의 인증 및 인가에 널리 사용되는 JWT(JSON Web Token)의 3대 구성 요소로 올바르게 나열된 것은?",
      "options": [
        "Header, Payload, Signature",
        "Header, Body, Hash",
        "Metadata, Claims, Certificate",
        "Issuer, Subject, Key",
        "Alg, Claims, MAC"
      ],
      "answer": 1,
      "explanation": "JWT는 마침표(.)로 구분되는 Header(알고리즘 및 토큰 타입), Payload(클레임/사용자 데이터), Signature(비밀키로 서명된 무결성 검증값) 3단계 구조로 구성됩니다."
    },
    {
      "id": "IW4_Q27",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "웹 세션 하이재킹(Session Hijacking) 공격 중 공격자가 사전에 발급받은 세션 ID를 희생자에게 주입한 후, 희생자가 해당 세션 ID로 로그인하면 공격자가 그 세션 권한을 획득하는 공격은?",
      "options": [
        "Session Fixation (세션 고정 공격)",
        "Session Sniffing",
        "Session Prediction",
        "Cross-Site Scripting",
        "Brute Force"
      ],
      "answer": 1,
      "explanation": "세션 고정(Session Fixation) 공격은 로그인 전 발급된 세션 ID를 로그인 성공 후에도 재사용할 때 발생하므로, 로그인 성공 시 반드시 기존 세션을 파기하고 새로운 세션 ID를 재생성(session.invalidate)해야 합니다."
    },
    {
      "id": "IW4_Q28",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "데이터베이스 보안에서 추론(Inference) 공격을 방지하기 위한 보안 통제 기법에 해당하지 않는 것은?",
      "options": [
        "동일 쿼리의 무제한 반복 실행 허용 및 응답 시간 단축",
        "쿼리 결과의 소규모 셀(Small Cell) 억제 (데이터 수가 적을 때 결과 은닉)",
        "데이터 교란(Perturbation) 및 난수 노이즈 추가",
        "다중 레벨 보안(MLS) 기반의 뷰(View) 분리",
        "사용자별 누적 질의 감사 로그 추적"
      ],
      "answer": 1,
      "explanation": "추론 공격은 비인가자가 여러 합법적 통계 질의를 조합하여 민감한 개인 정보를 유추하는 것이므로, 소규모 집합 결과 은닉, 노이즈 추가, 감사 추적이 필요합니다. 무제한 질의 허용은 추론 공격을 용이하게 만듭니다."
    },
    {
      "id": "IW4_Q29",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "이메일 보안 표준 중 송신자의 개인키로 메일 본문과 첨부파일에 디지털 서명을 첨부하고, 수신자의 공개키로 암호화하여 기밀성, 무결성, 인증, 부인방지를 제공하는 표준은?",
      "options": [
        "S/MIME (Secure/Multipurpose Internet Mail Extensions)",
        "SMTP",
        "POP3",
        "IMAP4",
        "SPF"
      ],
      "answer": 1,
      "explanation": "S/MIME은 X.509 공개키 인증서를 기반으로 MIME 데이터에 암호화 및 디지털 서명을 적용하여 이메일의 4대 보안 목표(기밀성, 무결성, 인증, 부인방지)를 모두 제공하는 IETF 표준입니다."
    },
    {
      "id": "IW4_Q30",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "Nginx 웹서버 설정에서 HTTP 응답 헤더에 Nginx의 상세 버전 정보(예: nginx/1.18.0)가 노출되지 않도록 차단하는 지시자는?",
      "options": [
        "server_tokens off;",
        "ServerTokens Prod;",
        "hide_server_version on;",
        "expose_php off;",
        "version_display off;"
      ],
      "answer": 1,
      "explanation": "Nginx에서는 nginx.conf의 http 블록에 'server_tokens off;'를 설정하면 Server 응답 헤더에서 세부 버전 번호가 제거되고 'Server: nginx'만 노출됩니다. (ServerTokens Prod는 Apache 지시자)"
    },
    {
      "id": "IW4_Q31",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "RSA 공개키 암호 알고리즘의 안전성 기반이 되는 수학적 난제와 타원곡선 암호(ECC)의 안전성 기반이 되는 수학적 난제의 조합으로 올바른 것은?",
      "options": [
        "RSA: 큰 정수의 소인수분해 난제 / ECC: 타원곡선 이산대수 난제(ECDLP)",
        "RSA: 이산대수 난제 / ECC: 소인수분해 난제",
        "RSA: 배낭 문제(Knapsack) / ECC: 격자 난제(Lattice)",
        "RSA: 양자 얽힘 / ECC: 해시 충돌",
        "RSA: 합동식 난제 / ECC: 모듈러 거듭제곱 난제"
      ],
      "answer": 1,
      "explanation": "RSA는 두 개의 매우 큰 소수의 곱을 소인수분해하는 수학적 어려움에 기반하고, ECC는 타원곡선 군 위에서의 이산대수 문제(ECDLP)의 난해성에 기반하여 256비트 키로도 RSA 3072비트 급의 보안성을 제공합니다."
    },
    {
      "id": "IW4_Q32",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "대한민국 국가 표준 블록 암호 알고리즘 중 1999년 KISA가 개발한 Feistel 구조의 128비트 블록 암호 알고리즘은?",
      "options": [
        "SEED",
        "ARIA",
        "HIGHT",
        "LEA",
        "DES"
      ],
      "answer": 1,
      "explanation": "SEED는 1999년 한국인터넷진흥원(KISA)과 전자통신연구원(ETRI)이 개발한 128비트 블록, 128비트 키 크기의 Feistel 구조 국가 표준 암호 알고리즘입니다. (ARIA는 2004년 개발된 SPN 구조)"
    },
    {
      "id": "IW4_Q33",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "블록 암호 운용 모드 중 카운터(Counter) 값을 블록 암호화한 후 평문 블록과 XOR하여 암호문을 생성하며, 1비트 에러가 다른 블록으로 전파되지 않고 병렬 처리가 가능한 모드는?",
      "options": [
        "CTR (Counter) 모드",
        "CBC 모드",
        "ECB 모드",
        "CFB 모드",
        "OFB 모드"
      ],
      "answer": 1,
      "explanation": "CTR 모드는 카운터를 암호화한 키 스트림을 평문과 XOR하므로 스트림 암호처럼 동작하며, 블록 간 종속성이 없어 완전한 병렬 처리가 가능하고 에러 전파가 발생하지 않습니다."
    },
    {
      "id": "IW4_Q34",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "비바(Biba) 무결성 모델의 두 가지 핵심 접근 통제 원칙으로 올바르게 짝지어진 것은?",
      "options": [
        "단순 무결성 규칙(No Read Down) / *-무결성 규칙(No Write Up)",
        "단순 보안 규칙(No Read Up) / *-보안 규칙(No Write Down)",
        "No Read Down / No Write Down",
        "No Read Up / No Write Up",
        "자유로운 읽기 / 엄격한 쓰기 통제"
      ],
      "answer": 1,
      "explanation": "비바(Biba) 모델은 무결성을 보호하기 위해 설계되었으며, 하위 무결성 등급의 데이터를 읽을 수 없고(No Read Down, 오염 방지), 상위 무결성 등급으로 데이터를 쓸 수 없는(No Write Up) 규칙을 적용합니다."
    },
    {
      "id": "IW4_Q35",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "접근 통제 보안 정책 중 중앙 관리자가 시스템의 모든 자원과 사용자에 대해 사전에 정의된 규칙(Rule)이나 역할(Role)에 따라 일괄적으로 접근 권한을 결정하며, 개별 소유자가 권한을 변경할 수 없는 정책은?",
      "options": [
        "강제적 접근 통제 (MAC / Mandatory Access Control)",
        "임의적 접근 통제 (DAC)",
        "사용자 정의 접근 통제",
        "신원 기반 접근 통제 (IBAC)",
        "접근 제어 목록 (ACL 단독)"
      ],
      "answer": 1,
      "explanation": "강제적 접근 통제(MAC)는 보안 레이블과 관리자 보안 정책에 의해 시스템이 접근을 강제하며, 파일 소유자라 할지라도 임의로 접근 권한을 부여하거나 변경할 수 없습니다."
    },
    {
      "id": "IW4_Q36",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "비즈니스 연속성 계획(BCP) 수립 시 업무 중단 시점부터 업무가 정상 수준으로 복구되기까지 허용되는 최대 시간을 의미하는 지표는?",
      "options": [
        "RTO (Recovery Time Objective / 복구 목표 시간)",
        "RPO (Recovery Point Objective / 복구 목표 시점)",
        "MTBF (Mean Time Between Failures)",
        "MTTR (Mean Time to Repair)",
        "BIA (Business Impact Analysis)"
      ],
      "answer": 1,
      "explanation": "RTO(복구 목표 시간)는 재해 발생 후 비즈니스 기능이 복구되어 재개될 때까지 허용되는 최대 시간 한계이며, RPO(복구 목표 시점)는 복구 시 허용 가능한 데이터 손실 허용 시점을 뜻합니다."
    },
    {
      "id": "IW4_Q37",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "공개키 기반 구조(PKI)에서 사용자에게 인증서를 발급하고 서명하는 주체(CA)와, 사용자의 신원을 직접 확인하고 인증서 발급 신청을 접수받아 CA에 전달하는 등록 주체(RA)의 역할 분담으로 올바른 것은?",
      "options": [
        "CA는 인증서 발행 및 폐기(서명)를 담당하고, RA는 사용자의 대면 신원 확인 및 등록 심사를 담당한다.",
        "RA가 인증서의 개인키를 직접 생성하여 보관한다.",
        "CA는 웹 브라우저이고, RA는 DNS 서버이다.",
        "사용자는 항상 CA와만 직접 통신하며 RA는 감사업무만 수행한다.",
        "인증서 폐기 목록(CRL)은 RA가 직접 서명하여 배포한다."
      ],
      "answer": 1,
      "explanation": "인증기관(CA)은 인증서의 발행, 서명, 폐기(CRL 생성)를 수행하는 핵심 발급 기관이며, 등록기관(RA)은 사용자의 신원 검증, 등록 접수 등 행정적 절차를 대행합니다."
    },
    {
      "id": "IW4_Q38",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "비대칭 암호와 대칭 암호의 장점을 결합하여, 대량의 평문 데이터는 고속 대칭키로 암호화하고, 그 대칭키는 수신자의 공개키로 암호화하여 함께 전송하는 기법은?",
      "options": [
        "전자 봉투 (Digital Envelope)",
        "전자 서명 (Digital Signature)",
        "블록체인 (Blockchain)",
        "영지식 증명 (Zero-Knowledge Proof)",
        "동형 암호 (Homomorphic Encryption)"
      ],
      "answer": 1,
      "explanation": "전자 봉투(Digital Envelope)는 세션키(대칭키)로 메시지를 고속 암호화하고, 그 세션키를 수신자의 공개키로 암호화하여 전송함으로써 속도와 키 분배 편의성을 동시에 달성하는 하이브리드 암호 기법입니다."
    },
    {
      "id": "IW4_Q39",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "위험 관리 전략 중 발생 가능성이 낮으나 피해 규모가 매우 큰 위험에 대해 보험 가입이나 전문 업체 위탁을 통해 손실 책임을 제3자에게 넘기는 방식은?",
      "options": [
        "위험 전가 (Risk Transfer)",
        "위험 회피 (Risk Avoidance)",
        "위험 감소 (Risk Reduction)",
        "위험 수용 (Risk Acceptance)",
        "위험 무시 (Risk Ignorance)"
      ],
      "answer": 1,
      "explanation": "위험 전가(Risk Transfer)는 보안 보험 가입, 아웃소싱 계약 등을 통해 위험으로 인한 재정적 손실 책임을 외부 기관에 이전하는 전략입니다."
    },
    {
      "id": "IW4_Q40",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "패스워드 기반 키 유도 함수(KDF) 중 레인보우 테이블 공격 및 GPU 기반 병렬 크래킹을 무력화하기 위해 솔트(Salt)와 함께 수만 번 이상의 해시 반복(키 스트레칭)을 표준화한 규격은?",
      "options": [
        "PBKDF2 (PKCS #5 v2.0)",
        "MD5 단독",
        "SHA-1 단독",
        "DES-Crypt",
        "CRC32"
      ],
      "answer": 1,
      "explanation": "PBKDF2는 솔트(Salt)를 추가하고 의도적으로 수만 번 이상의 HMAC 반복 연산(Iteration Count)을 거치게 하여 GPU 크래커나 레인보우 테이블 공격을 방어하는 표준 키 유도 함수입니다."
    },
    {
      "id": "IW4_Q41",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 보호법상 정보주체의 동의 없이도 개인정보를 수집·이용할 수 있는 합법적 요건(제15조 제1항)에 해당하지 않는 것은?",
      "options": [
        "사업자의 영업 이익 극대화를 위해 빅데이터 분석이 반드시 필요한 경우",
        "법률에 특별한 규정이 있거나 법령상 의무를 준수하기 위하여 불가피한 경우",
        "공공기관이 법령 등에서 정하는 소관 업무의 수행을 위하여 불가피한 경우",
        "정보주체와 체결한 계약의 체결 및 이행을 위하여 불가피하게 필요한 경우",
        "명백히 정보주체 또는 제3자의 급박한 생명, 신체, 재산의 이익을 위하여 필요하다고 인정되는 경우"
      ],
      "answer": 1,
      "explanation": "단순한 영업 이익 증대나 마케팅 목적은 법정 동의 면제 사유가 아니며, 반드시 정보주체의 사전 명시적 동의를 받아야 합니다."
    },
    {
      "id": "IW4_Q42",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보처리자가 개인정보의 안전성 확보조치 기준에 따라 비밀번호를 저장할 때 적용해야 하는 암호화 조치로 올바른 것은?",
      "options": [
        "복호화되지 않는 일방향 암호화(해시 함수 + 솔트)를 적용하여 저장해야 한다.",
        "양방향 대칭키(AES)로 암호화해야 한다.",
        "공개키(RSA)로 암호화하여 저장해야 한다.",
        "평문으로 저장하되 접근 권한만 차단하면 된다.",
        "클라이언트에서 마스킹만 적용하면 된다."
      ],
      "answer": 1,
      "explanation": "안전성 확보조치 기준 제7조에 따라 비밀번호는 관리자라 할지라도 원본을 알 수 없도록 안전한 일방향 암호화(One-Way Hash with Salt)를 적용하여 저장해야 합니다."
    },
    {
      "id": "IW4_Q43",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 보호법상 개인정보 영향평가(PIA)를 의무적으로 수행해야 하는 대상 기준으로 올바른 것은?",
      "options": [
        "50만 명 이상의 고유식별정보 또는 민감정보를 처리하거나, 500만 명 이상의 정보주체 개인정보를 구축·운용하는 공공기관",
        "모든 민간 기업",
        "연 매출 100억 원 이상 기업",
        "상장된 모든 금융기관",
        "직원 수 50인 이상인 모든 공공기관"
      ],
      "answer": 1,
      "explanation": "개인정보 영향평가는 공공기관을 대상으로 의무화되어 있으며, 50만 명 이상의 민감정보/고유식별정보 처리 시스템 또는 500만 명 이상의 개인정보 연계·구축 시스템 등이 법정 의무 대상입니다."
    },
    {
      "id": "IW4_Q44",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보통신망법상 침해사고가 발생한 정보통신서비스 제공자가 과학기술정보통신부장관 또는 한국인터넷진흥원(KISA)에 신고해야 하는 기한으로 올바른 것은?",
      "options": [
        "침해사고 발생을 안 때 즉시 (24시간 이내)",
        "72시간 이내",
        "5일 이내",
        "10일 이내",
        "해당 월말까지"
      ],
      "answer": 1,
      "explanation": "정보통신망 이용촉진 및 정보보호 등에 관한 법률 제48조의3에 따라 정보통신서비스 제공자는 침해사고가 발생하였을 때에는 즉시(안 때로부터 24시간 이내) 과기정통부 또는 KISA에 신고하여야 합니다."
    },
    {
      "id": "IW4_Q45",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "전자금융거래법상 전자금융사고(해킹, 전산장애 등)로 인해 이용자에게 손해가 발생한 경우 금융회사 또는 전자금융업자의 배상 책임에 관한 원칙으로 올바른 것은?",
      "options": [
        "금융회사 등은 원칙적으로 무과실 책임을 부담하며, 이용자의 고의나 중대한 과실이 입증된 경우에만 책임의 전부 또는 일부를 면할 수 있다.",
        "이용자가 금융회사의 고의를 직접 입증해야만 배상받을 수 있다.",
        "모든 사고는 국가가 전액 배상한다.",
        "금융회사는 일체 면책된다.",
        "배상 한도는 1인당 100만 원으로 제한된다."
      ],
      "answer": 1,
      "explanation": "전자금융거래법 제9조에 따라 금융회사 및 전자금융업자는 무과실 손해배상 책임을 지며, 이용자에게 고의나 중과실(비밀번호 누설 등)이 있음을 금융회사가 직접 입증하지 못하면 책임을 면할 수 없습니다."
    },
    {
      "id": "IW4_Q46",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "ISMS-P 인증 제도에서 인증의 유효기간과 매년 받아야 하는 사후 심사에 대한 설명으로 올바른 것은?",
      "options": [
        "인증 유효기간은 3년이며, 유효기간 중 매년 1회 이상 사후심사를 받아야 한다.",
        "유효기간은 1년이며, 매년 최초심사를 재수행한다.",
        "유효기간은 5년이며 사후심사는 생략된다.",
        "유효기간은 2년이며 사후심사는 격년으로 받는다.",
        "유효기간은 영구적이며 결함 발견 시에만 심사한다."
      ],
      "answer": 1,
      "explanation": "ISMS 및 ISMS-P 인증의 유효기간은 발급일로부터 3년이며, 인증 취득 기업은 인증 유효성을 지속적으로 유지하기 위해 매년 1회 이상 사후심사를 받아야 합니다."
    },
    {
      "id": "IW4_Q47",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 보호법상 정보주체의 동의 획득 시 14세 미만 아동의 개인정보를 처리하기 위해 법정대리인의 동의를 받아야 하는 최소 정보는?",
      "options": [
        "법정대리인의 성명, 연락처 등 동의를 받기 위해 필요한 최소한의 정보",
        "법정대리인의 주민등록번호 및 신용카드 정보",
        "법정대리인의 직장 주소 및 연봉 정보",
        "아동의 학교 및 담임교사 확인서",
        "가족관계증명서 원본 제출 필수"
      ],
      "answer": 1,
      "explanation": "개인정보 보호법 제22조의2에 따라 14세 미만 아동의 개인정보를 처리할 때에는 그 법정대리인의 동의를 받아야 하며, 법정대리인의 동의를 받기 위하여 필요한 최소한의 정보(성명, 연락처 등)는 아동으로부터 직접 수집할 수 있습니다."
    },
    {
      "id": "IW4_Q48",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "정보보호 및 개인정보보호 관리체계(ISMS-P) 구축 시 최고경영진을 위원장으로 구성하여 정보보호 정책 및 예산을 심의·의결하는 기구는?",
      "options": [
        "정보보호(보안)위원회",
        "인사위원회",
        "노사협의회",
        "준법지원팀",
        "감사위원회"
      ],
      "answer": 1,
      "explanation": "ISMS-P 기준 1.1.1(경영진의 참여)에 따라 조직은 최고경영진, CISO, CPO 및 주요 부서장이 참여하는 '정보보호위원회'를 구성하고 정기적으로 회의를 개최하여 정책과 예산을 의결해야 합니다."
    },
    {
      "id": "IW4_Q49",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 보호법상 가명정보(Pseudonymous Data)의 처리에 관한 설명으로 가장 올바른 것은?",
      "options": [
        "통계작성, 과학적 연구, 공익적 기록보존 등의 목적으로 정보주체의 동의 없이 가명정보를 처리할 수 있다.",
        "가명정보는 특정 개인을 알아볼 수 있으므로 어떠한 경우에도 동의 없이 처리할 수 없다.",
        "가명정보는 추가 정보와 결합하여 특정 개인을 재식별하는 행위가 전면 허용된다.",
        "가명정보를 처리할 때에는 안전성 확보조치를 이행할 필요가 없다.",
        "가명정보는 해외 제3자에게 자유롭게 매매할 수 있다."
      ],
      "answer": 1,
      "explanation": "개인정보 보호법 제28조의2에 따라 가명정보는 통계작성, 과학적 연구, 공익적 기록보존 등의 목적으로 정보주체의 동의 없이 안전하게 결합 및 처리될 수 있으며, 재식별은 엄격히 금지됩니다."
    },
    {
      "id": "IW4_Q50",
      "category": "infosec_written",
      "exam": 4,
      "exam_name": "4회 필기 고난도 심화 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 정보보안 관리 및 법률",
      "question": "개인정보 유출 사고 발생 시 개인정보보호위원회가 부과할 수 있는 과징금의 상한 기준(개정 개인정보 보호법)으로 올바른 것은?",
      "options": [
        "전체 매출액의 100분의 3(3%) 이하 (위반행위와 관련 없는 매출액 제외)",
        "위반행위 관련 매출액의 100분의 3 이하",
        "정액 5억 원 이하",
        "전체 매출액의 100분의 10 이하",
        "연간 영업이익의 100분의 5 이하"
      ],
      "answer": 1,
      "explanation": "2023년 개정 개인정보 보호법 제64조의2에 따라 과징금 부과 기준이 유럽 GDPR 수준으로 강화되어 '전체 매출액의 3% 이하'로 변경되었으며, 사업자가 관련 없는 매출액을 소명할 경우 이를 제외하고 산정합니다."
    }
  ],
  "summaries": [
    {
      "id": "sys_content_01",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "리눅스/유닉스 계정 파일 및 패스워드 암호화 구조",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>/etc/passwd 파일 구조:</strong> 계정명 : 암호(x) : UID : GID : 설명(GECOS) : 홈디렉토리 : 로그인셸 (7개 필드). UID 0은 root 관리자 권한을 의미하며, 일반 사용자의 UID가 0이면 백도어 계정으로 간주.",
        "<strong>/etc/shadow 파일 구조:</strong> 계정명 : 암호해시 : 최종변경일 : 최소사용일 : 최대사용일 : 경고일 : 유예일 : 만료일 : 예약필드 (9개 필드). 소유자 root, 권한 400 또는 000 엄격 통제.",
        "<strong>shadow 파일 암호 식별자($id$salt$hash):</strong> $1(MD5, 128bit 취약), $2a(Blowfish), $5(SHA-256), $6(SHA-512, 리눅스 표준 권장). Salt를 붙여 동일 패스워드라도 해시값이 달라지며 레인보우 테이블 공격을 무력화함.",
        "<strong>불필요한 서비스 계정 셸 제한:</strong> daemon, bin, sys, adm, lp 등 대화형 로그인이 필요 없는 계정은 로그인 셸을 /bin/false 또는 /sbin/nologin으로 지정하여 원격 셸 획득 차단."
      ]
    },
    {
      "id": "sys_content_02",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "특수 권한 비트(SetUID, SetGID, Sticky Bit)와 기본 권한(umask)",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>SetUID(4000, rwsr-xr-x):</strong> 실행 파일 구동 시 실행자 권한이 아닌 '파일 소유자 권한'으로 프로세스가 실행됨. 관리자 권한 상승 취약점의 주원인. 검색: find / -perm -4000 -type f.",
        "<strong>SetGID(2000, rwxr-sr-x):</strong> 실행 시 '소유 그룹 권한'으로 실행되거나, 디렉토리에 설정 시 내부 생성 파일이 디렉토리 소유 그룹을 자동 상속받음.",
        "<strong>Sticky Bit(1000, rwxrwxrwt):</strong> 공용 디렉토리(/tmp, /var/tmp)에 부여. 누구나 파일 생성이 가능하나, 파일 삭제 및 수정은 오직 '파일 소유자'와 root만 가능.",
        "<strong>기본 umask 계산법:</strong> 일반 파일 기본 최대 권한 666, 디렉토리 777 기준에서 umask 값을 뺀 권한으로 생성. KISA 표준 umask 027 적용 시 디렉토리는 750(rwxr-x---), 파일은 640(rw-r-----)으로 생성되어 Other의 읽기/쓰기/실행 완전 차단."
      ]
    },
    {
      "id": "sys_content_03",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "PAM(Pluggable Authentication Modules) 인증 모듈 및 제어 플래그",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>PAM 개념:</strong> 애플리케이션의 재컴파일 없이 시스템 인증 정책을 유연하게 교체할 수 있는 플러그인 인터페이스 (/etc/pam.d/ 설정 파일 참조).",
        "<strong>PAM 4대 모듈 타입:</strong> auth(사용자 신원 인증 및 토큰 발급), account(계정 유효성, 만료일, 접근 시간 점검), password(비밀번호 변경 및 복잡도 검증), session(로그인 전후 자원 할당, 마운트, 환경 로깅).",
        "<strong>PAM 4대 제어 플래그 동작 원리:</strong>",
        "• <code>required</code>: 실패 시 최종 결과는 실패로 확정되지만, 보안상 공격자가 실패 원인을 유추하지 못하도록 나머지 모듈을 계속 수행함.",
        "• <code>requisite</code>: 실패 즉시 다음 모듈 수행을 중단하고 즉시 시스템에 실패를 반환함.",
        "• <code>sufficient</code>: 성공 시 이전에 실패한 required 모듈이 없다면 즉시 최종 성공을 확정하고 탈출함. 실패 시 무시하고 다음 단계 진행.",
        "• <code>optional</code>: 성공/실패 여부가 전체 인증 결과에 결정적 영향을 주지 않음 (로깅이나 알림 용도).",
        "<strong>계정 잠금 임계값 설정:</strong> /etc/pam.d/system-auth 파일에 pam_faillock.so (구 pam_tally2)를 deny=5 unlock_time=1200 설정하여 무차별 대입 방어."
      ]
    },
    {
      "id": "sys_content_04",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "시스템 바이너리·텍스트 로그 구조 및 타임스탬프 분석",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>리눅스 4대 바이너리 로그:</strong>",
        "• <code>/var/log/wtmp</code>: 시스템 성공 로그인/로그아웃 및 재부팅 이력 저장. 확인 명령어: <code>last</code>",
        "• <code>/var/log/utmp</code>: 현재 시스템에 실시간 접속 중인 사용자 상태 저장. 확인 명령어: <code>who, w, users</code>",
        "• <code>/var/log/btmp</code>: 실패한 로그인 시도 이력(무차별 대입 공격 식별). 확인 명령어: <code>lastb</code>",
        "• <code>/var/log/lastlog</code>: 각 계정별 최종 접속 성공 시각 및 출발지 IP 저장. 확인 명령어: <code>lastlog</code>",
        "<strong>주요 텍스트 로그:</strong>",
        "• <code>/var/log/secure</code>: SSH 인증, sudo 실행, PAM 인증 관련 실시간 텍스트 로그.",
        "• <code>/var/log/messages</code>: 커널 및 일반 데몬 전반의 시스템 상태 메시지.",
        "• <code>/var/log/xferlog</code>: vsftpd 등 FTP 파일 송수신 전송 내역.",
        "<strong>파일 시스템 타임스탬프 (MAC Time):</strong>",
        "• <code>atime(Access)</code>: 파일 내용 읽기 시 갱신.",
        "• <code>mtime(Modify)</code>: 파일 내용 변경 시 갱신. (find -mtime -1: 최근 24시간 내 수정 파일 검색).",
        "• <code>ctime(Change)</code>: i-node 메타데이터(소유자, 권한, 크기) 변경 시 갱신. 커널이 직접 기록하므로 utime() 함수로 위·변조 불가능."
      ]
    },
    {
      "id": "sys_content_05",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "메모리 공격(버퍼 오버플로우·포맷스트링) 및 보안 메커니즘",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>스택 버퍼 오버플로우(Stack Buffer Overflow):</strong> 스택 프레임 구조 [지역변수 버퍼] -> [SFP(Saved Frame Pointer)] -> [RET(Return Address)]에서 경계 검사 없는 취약 함수(strcpy, gets, sprintf) 사용 시 복귀 주소를 악성 셸코드 주소로 덮어써 관리자 권한 획득.",
        "<strong>포맷 스트링 공격(Format String Attack):</strong> printf(user_input)처럼 포맷 스트링 인자 누락 시 %x(스택 메모리 덤프), %n(지금까지 출력된 바이트 수를 지정 메모리에 덮어쓰기)을 악용하여 임의 코드 실행.",
        "<strong>경쟁 조건(Race Condition / TOCTOU):</strong> Time of Check to Time of Use. 자원 권한 점검 시점과 실제 자원 사용 시점 사이의 극미한 시간차를 노려 심볼릭 링크를 대상 파일로 신속히 교체하여 root 권한 파일 탈취.",
        "<strong>메모리 5대 방어 기법:</strong>",
        "• <code>ASLR (Address Space Layout Randomization)</code>: 프로그램 실행 시마다 스택, 힙, 라이브러리 주소를 무작위 난수화.",
        "• <code>DEP / NX (Data Execution Prevention / No-Execute)</code>: 스택 및 힙 메모리 영역의 실행(Execute) 권한을 원천 박탈하여 주입된 셸코드 실행 차단.",
        "• <code>Stack Canary</code>: 지역변수와 SFP 사이에 랜덤 카나리 값을 삽입하여 함수 종료 전 값 변조 감지 시 즉시 프로세스 강제 종료(__stack_chk_fail).",
        "• <code>SafeSEH / SEHOP</code>: 윈도우 환경에서 예외 처리기(SEH) 덮어쓰기 공격 차단.",
        "• <code>ASCII Armor</code>: 공유 라이브러리 주소 상위에 0x00(NULL 바이트)을 포함시켜 문자열 복사 함수를 종료시킴."
      ]
    },
    {
      "id": "net_content_01",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "TCP 3-Way Handshake 및 L4 DoS/DDoS 공격 메커니즘",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>TCP 정상 연결 수립 (3-Way Handshake):</strong> Client -> [SYN] -> Server -> [SYN+ACK] -> Client -> [ACK] -> Server (ESTABLISHED).",
        "<strong>SYN Flooding 공격 원리:</strong> 공격자가 출발지 IP를 스푸핑하거나 ACK 패킷을 의도적으로 회신하지 않아, 서버의 백로그 큐(Backlog Queue)에 SYN_RECEIVED 상태의 Half-Open 연결을 대량 누적시켜 정상 접속 고갈 유발.",
        "<strong>SYN Flooding 방어 대책:</strong> SYN Cookie 활성화 (연결 정보를 서버 메모리가 아닌 TCP Sequence Number에 인코딩), 백로그 큐 크기 확장(net.ipv4.tcp_max_syn_backlog), SYN_RECV 타임아웃 단축.",
        "<strong>기타 주요 L4 DoS 공격 유형:</strong>",
        "• <code>Land Attack</code>: 패킷의 출발지 IP/Port와 목적지 IP/Port를 희생자 자신의 IP/Port로 동일하게 조작하여 자기 자신과 무한 루프 연결 시도 유발.",
        "• <code>Smurf Attack</code>: 출발지 IP를 희생자 IP로 위조한 뒤 다이렉트 브로드캐스트 주소로 대량의 ICMP Echo Request 전송. 서브넷 내 모든 호스트가 희생자에게 일제히 ICMP Echo Reply 증폭 전송.",
        "• <code>TearDrop Attack</code>: IP 단편화 재조합 시 오프셋(Offset) 값을 의도적으로 중첩/왜곡시켜 패킷 재조합 단계에서 시스템 크래시 유발.",
        "• <code>Ping of Death</code>: 규정된 최대 IP 패킷 크기(65,535 바이트)를 초과하는 거대 ICMP 패킷을 단편화 전송하여 버퍼 오버플로우 유발."
      ]
    },
    {
      "id": "net_content_02",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "L7 애플리케이션 서비스 거부 공격 및 슬로우 어택 기법",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>Slowloris (Slow HTTP Header):</strong> HTTP 요청 헤더의 끝을 알리는 개행문자(\\r\\n\\r\\n)를 전송하지 않고 끝없이 지연된 비정상 헤더 필드를 주기적으로 전송하여 웹 서버의 동시 연결 스레드/프로세스 슬롯 고갈.",
        "<strong>RUDY (Slow HTTP POST):</strong> Content-Length를 수만 바이트로 크게 지정한 후, HTTP Body 데이터를 1바이트씩 극도로 느린 간격으로 쪼개어 전송하여 연결 유지 강제.",
        "<strong>Slow HTTP Read Attack:</strong> 클라이언트의 TCP 수신 윈도우 크기(Window Size)를 0으로 유지하거나 극도로 작게 설정하여 웹 서버가 응답 데이터를 보내지 못하고 대기 상태에 빠지게 함.",
        "<strong>대응 방안:</strong> 웹 서버의 최소 데이터 전송 속도 제한(RequestReadTimeout 설정), 동시 연결 수 제한, L7 WAF를 통한 비정상 HTTP 연결 조기 차단."
      ]
    },
    {
      "id": "net_content_03",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "포트 스캔(Port Scan) 기법 및 RFC 793 스텔스 스캔 원리",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>TCP Open Scan (TCP Connect):</strong> 완전한 3-Way Handshake를 수립하여 포트 개방 여부 확인. 관리자 권한이 불필요하나 대상 서버의 접속 로그에 완전한 IP 연결 기록이 남음.",
        "<strong>TCP Half-Open Scan (SYN Scan):</strong> SYN 전송 -> 서버가 SYN+ACK 응답 시 포트 열림(Open) 판단 후 즉시 RST 전송하여 연결 강제 종료. 완전한 세션이 수립되지 않아 서버에 로그가 남지 않는 대표적 스텔스 스캔.",
        "<strong>RFC 793 기반 스텔스 스캔 (UNIX 계열 대상):</strong>",
        "• <code>FIN Scan</code>: FIN 플래그만 세팅하여 전송.",
        "• <code>Null Scan</code>: 모든 플래그를 0(비트 없음)으로 전송.",
        "• <code>Xmas Scan</code>: FIN, PSH, URG 플래그를 모두 1로 세팅하여 전송 (크리스마스 트리처럼 불이 켜짐).",
        "• <strong>결과 판정 규칙:</strong> 포트가 닫힌(Closed) 경우 서버는 <code>RST+ACK</code>를 회신함. 포트가 열린(Open) 경우 패킷을 무시하고 <code>무응답(No Response)</code>함."
      ]
    },
    {
      "id": "net_content_04",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "IPSec 프로토콜 구조(AH·ESP) 및 IKE 키 교환 메커니즘",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>IPSec 개요:</strong> 네트워크 계층(IP L3)에서 기밀성, 무결성, 송신처 인증을 제공하는 VPN 표준 보안 프로토콜 세트.",
        "<strong>AH (Authentication Header, 프로토콜 51):</strong> 송신처 인증 및 데이터 무결성 보장. 암호화(기밀성)는 제공하지 않음. IP 헤더까지 해시 검증에 포함하므로 IP 주소가 변환되는 NAT(공유기) 환경을 통과할 수 없음.",
        "<strong>ESP (Encapsulating Security Payload, 프로토콜 50):</strong> 기밀성(암호화), 무결성, 인증을 모두 제공. 페이로드 데이터를 대칭키로 암호화. NAT-Traversal(UDP 4500) 지원.",
        "<strong>동작 모드 2종:</strong>",
        "• <code>전송 모드(Transport Mode)</code>: 원래의 IP 헤더는 유지하고 상위 페이로드(TCP/UDP 데이터)만 암호화. 종단 호스트 간 통신(Host-to-Host)에 사용.",
        "• <code>터널 모드(Tunnel Mode)</code>: 원본 패킷 전체(원본 IP 헤더 포함)를 암호화하고 새로운 외부 IP 헤더를 덧붙임. 게이트웨이 간 통신(Site-to-Site VPN)에 필수 적용.",
        "<strong>IKE (Internet Key Exchange, UDP 500):</strong> ISAKMP 프레임워크와 Diffie-Hellman 키 교환을 기반으로 양단 간 SA(Security Association) 및 세션 암호키를 자동 협상."
      ]
    },
    {
      "id": "net_content_05",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "Snort 침입탐지 규칙(Rule) 문법 및 옵션 체계",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>Snort 룰 기본 구조:</strong> <code>[Rule Header] ([Rule Options])</code>",
        "• Header: <code>[Action] [Protocol] [Src IP] [Src Port] [Direction] [Dst IP] [Dst Port]</code>",
        "• 예시: <code>alert tcp any any -> 192.168.1.100 80 (...)</code>",
        "<strong>주요 Rule Action:</strong> alert(경고 발생 후 기록), log(패킷 로깅), pass(패킷 무시), drop(패킷 차단 및 드롭, 인라인 모드).",
        "<strong>핵심 Rule Options:</strong>",
        "• <code>msg:\"메시지\";</code>: 경고 발생 시 출력될 텍스트 설명.",
        "• <code>content:\"문자열\";</code>: 패킷 페이로드에서 탐지할 패턴. 바이너리 16진수 바이트는 <code>|90 90 90|</code>처럼 파이프 기호로 표기.",
        "• <code>nocase;</code>: 대소문자 구분 없이 매칭.",
        "• <code>offset / depth</code>: 패킷 페이로드 시작점 기준 검사 시작 위치(offset) 및 검사할 바이트 범위(depth).",
        "• <code>distance / within</code>: 이전 content 패턴 매칭 성공 지점 기준 상대적 시작 간격(distance) 및 검사 범위(within).",
        "• <code>sid:숫자;</code>: 규칙 고유 식별자 (999 이하: 시스템 예약, 1,000,000 이상: 사용자 정의 규칙)."
      ]
    },
    {
      "id": "net_content_06",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "무선 LAN 암호화 프로토콜(WEP·WPA·WPA2·WPA3) 및 DNSSEC",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>무선 LAN 보안 표준의 발전:</strong>",
        "• <code>WEP</code>: RC4 스트림 암호 및 24비트 짧은 IV 사용. 동일 IV 빈번 재사용으로 FMS 공격에 의해 수분 내 키 탈취 취약 (사용 금지).",
        "• <code>WPA</code>: WEP 취약점 임시 보완. 패킷마다 키를 동적으로 교체하는 TKIP(Temporal Key Integrity Protocol) 채택.",
        "• <code>WPA2</code>: IEEE 802.11i 표준. 강력한 블록 암호인 AES-CCMP를 도입하여 군사 등급의 무선 암호화 제공. 4-Way Handshake 도청 시 오프라인 사전 공격 취약점 존재.",
        "• <code>WPA3</code>: 최신 표준. SAE(Simultaneous Authentication of Equals, 동등동시인증) 핸드셰이크를 적용하여 오프라인 사전 대입 및 재전송 공격을 원천 차단.",
        "<strong>DNS 캐시 포이즈닝 & DNSSEC:</strong>",
        "• DNS 캐시 포이즈닝: Recursive DNS 서버에 가짜 IP 응답을 주입하여 사용자를 피싱 사이트로 유도.",
        "• DNSSEC(Domain Name System Security Extensions): DNS 응답 데이터에 공개키 기반 전자서명(RRSIG, DNSKEY, DS 레코드)을 부착하여 위·변조 방지 및 송신처 신뢰성 검증."
      ]
    },
    {
      "id": "app_content_01",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "SQL Injection 취약점 유형별 분석 및 시큐어코딩",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>SQL Injection 원리:</strong> 검증되지 않은 외부 입력값이 데이터베이스 쿼리 구조를 변조하여 인가되지 않은 데이터 조회/수정/삭제를 수행하는 취약점.",
        "<strong>공격 유형 4대 분류:</strong>",
        "• <code>In-Band (Error-Based)</code>: DB 에러 메시지에 시스템 정보나 데이터가 노출되는 취약점 악용.",
        "• <code>In-Band (Union-Based)</code>: UNION 연산자를 이용해 원래 쿼리에 공격자 쿼리를 결합. (컬럼 개수와 데이터 타입 일치 필수).",
        "• <code>Inferential (Boolean-Based Blind)</code>: 에러 메시지가 없을 때, 참/거짓 조건문(1=1 / 1=2)에 따른 페이지 응답 차이를 이용해 한 글자씩 추출.",
        "• <code>Inferential (Time-Based Blind)</code>: 응답 내용이 동일할 때, sleep() 또는 benchmark() 함수로 지연 시간을 유발하여 참/거짓 판단.",
        "<strong>시큐어코딩 최우선 원칙:</strong> 파라미터화된 쿼리(PreparedStatement) 사용. 입력값이 쿼리 문법으로 해석되지 않고 순수 데이터 리터럴로만 바인딩되도록 강제."
      ]
    },
    {
      "id": "app_content_02",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "XSS(Cross-Site Scripting) 3대 유형 및 브라우저 보안 헤더",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>XSS 개념:</strong> 공격자가 웹 페이지에 악성 스크립트를 삽입하여 희생자의 브라우저에서 실행되도록 유도, 세션 쿠키 탈취 또는 악성 행위 유발.",
        "<strong>XSS 3대 유형:</strong>",
        "• <code>Stored XSS (저장형)</code>: 게시판, 댓글 등 DB에 악성 스크립트가 저장되어 열람하는 모든 불특정 다수에게 자동 실행됨 (파급력 최상).",
        "• <code>Reflected XSS (반사형)</code>: 검색어 등 URL 파라미터에 스크립트를 포함시켜 악성 링크 클릭 시 서버가 그대로 반사 출력함.",
        "• <code>DOM-Based XSS</code>: 서버를 거치지 않고 브라우저 단 자바스크립트가 DOM 환경(document.location, innerHTML)을 조작하여 실행됨.",
        "<strong>방어 기법:</strong>",
        "• HTML Entity 인코딩: <code>&lt; &gt; &amp; &quot; &#x27;</code> 문자로 치환 출력.",
        "• 쿠키 보호: <code>HttpOnly</code> 플래그를 쿠키에 설정하여 자바스크립트의 document.cookie 접근 원천 차단.",
        "• <code>CSP (Content Security Policy)</code>: 스크립트 실행 출처를 화이트리스트로 제한."
      ]
    },
    {
      "id": "app_content_03",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "CSRF vs SSRF 메커니즘 비교 및 위조 요청 방어",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>CSRF (Cross-Site Request Forgery):</strong> 로그인된 정상 사용자의 브라우저 권한을 도용하여 사용자가 의도하지 않은 상태 변경 요청(패스워드 변경, 계좌 이체 등)을 서버로 강제 전송시키는 공격.",
        "• CSRF 방어: 일회성 <code>CSRF Token</code> 검증, 쿠키의 <code>SameSite</code> 속성을 Strict 또는 Lax로 설정, 재인증(CAPTCHA, 2차 비밀번호) 요구.",
        "<strong>SSRF (Server-Side Request Forgery):</strong> 공격자가 취약한 웹 서버를 중간 프록시로 악용하여, 외부에서 직접 접근할 수 없는 내부 인트라넷 시스템, 클라우드 메타데이터 API(169.254.169.254) 등으로 비정상 요청을 전송시키는 공격.",
        "• SSRF 방어: 서버가 외부 URL 호출 시 사설 IP 대역(10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.1) 요청을 원천 차단하는 화이트리스트 적용."
      ]
    },
    {
      "id": "app_content_04",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "파일 업로드/다운로드 취약점 및 경로 조작(Path Traversal)",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>파일 업로드 취약점 방어 3대 원칙:</strong>",
        "1. <code>화이트리스트 확장자 검증</code>: jpg, png, pdf 등 허용할 확장자만 엄격히 허용 (블랙리스트 검증은 .php5, .phtml, .jspx 등으로 우회 가능).",
        "2. <code>파일명 무작위 난수화</code>: 업로드된 원본 파일명을 버리고 UUID 등으로 난수화하여 저장.",
        "3. <code>실행 권한(No-Exec) 박탈 및 웹 루트 격리</code>: 업로드 전용 디렉토리에서 스크립트 실행 엔진 연동 해제, 웹 루트 외부 저장.",
        "<strong>경로 조작 (Path Traversal / Directory Traversal):</strong>",
        "• 공격자가 파일 다운로드 파라미터에 <code>../</code> 또는 URL 인코딩된 <code>%2e%2e%2f</code> 등을 삽입하여 상위 시스템 디렉토리의 기밀 파일(/etc/passwd, web.xml)을 탈취.",
        "• 방어책: 경로 조작 문자 필터링 및 <code>getCanonicalPath()</code>를 사용하여 정규화된 절대 경로가 허용된 다운로드 루트 내에 존재하는지 엄격히 대조."
      ]
    },
    {
      "id": "app_content_05",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "데이터베이스 암호화 방식(API·Plug-In·TDE) 및 접근 통제",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>DB 암호화 3대 구축 방식 비교:</strong>",
        "• <code>API 방식</code>: 애플리케이션 레벨에서 암·복호화 모듈을 호출하여 DB로 전송. 장점: DB 서버 부하 분산, 네트워크 구간 암호화. 단점: 애플리케이션 소스코드 수정 불가피.",
        "• <code>Plug-In 방식</code>: DBMS 엔진 내부의 플러그인 또는 트리거/뷰를 통해 암·복호화 수행. 장점: 애플리케이션 소스 수정 최소화. 단점: DB 서버에 암호화 연산 부하 집중.",
        "• <code>TDE (Transparent Data Encryption, 투명한 데이터 암호화)</code>: DBMS 저장소 파일 레벨에서 자동으로 블록 단위 암호화. 장점: 소스 수정 전혀 없음, 인덱스 검색 성능 유지. 단점: 메모리 적재 시 평문이므로 메모리 덤프 취약.",
        "<strong>DB 접근 통제 기법:</strong> DAC(테이블 소유자 기반 GRANT/REVOKE), MAC(보안 라벨 기반 강제 통제), RBAC(업무 역할별 권한 그룹 매핑)."
      ]
    },
    {
      "id": "app_content_06",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "전자상거래 SET 프로토콜·전자봉투 및 이메일 보안 3총사",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>SET (Secure Electronic Transaction) 이중 서명(Dual Signature):</strong>",
        "• 소비자가 전자상거래 결제 시 '주문 정보(OI)'와 '결제 정보(PI)'를 각각 분리 해시한 뒤, 두 해시값을 결합하여 전자서명을 생성함.",
        "• 효과: 상점은 주문 정보만 열람할 수 있고 카드번호는 볼 수 없으며, 카드사는 결제 정보만 열람하고 상품 상세 목록은 알 수 없음.",
        "<strong>전자봉투 (Digital Envelope):</strong> 대용량 본문은 빠른 대칭키(세션키)로 암호화하고, 그 세션키를 수신자의 공개키로 암호화하여 본문과 함께 전송하는 하이브리드 암호 기법.",
        "<strong>이메일 스푸핑 방어 3대 표준:</strong>",
        "• <code>SPF (Sender Policy Framework)</code>: 도메인 DNS TXT 레코드에 해당 도메인에서 메일을 발송할 수 있는 합법적 메일 서버 IP 목록을 등록.",
        "• <code>DKIM (DomainKeys Identified Mail)</code>: 발신 서버가 이메일 헤더에 전자서명을 첨부하고, 수신자가 발신 도메인의 DNS 공개키로 서명을 검증하여 위·변조 방지.",
        "• <code>DMARC</code>: SPF 및 DKIM 검증 실패 시 메일을 격리(Quarantine)하거나 수신 거부(Reject)하도록 송신 도메인 관리자가 정책을 수립."
      ]
    },
    {
      "id": "crypto_content_01",
      "type": "content",
      "category": "crypto",
      "category_name": "정보보안 일반·암호학",
      "title": "대칭키 암호 알고리즘 구조(Feistel vs SPN) 및 표준 암호",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>대칭키 기본 개념:</strong> 암호화키와 복호화키가 동일한 암호 시스템. 연산 속도가 매우 빠르나 키 분배 및 관리가 어려움 (N명 간 필요한 키 수: N(N-1)/2).",
        "<strong>구조적 분류:</strong>",
        "• <code>Feistel 구조</code>: 평문 블록을 좌우(L/R) 둘로 분할하여 라운드 함수를 거친 뒤 스왑. 역함수가 불필요하여 암·복호화 구조가 완전히 동일함. 알고리즘: DES, 3DES, SEED.",
        "• <code>SPN (Substitution-Permutation Network) 구조</code>: 혼돈을 위한 치환(S-Box)과 확산을 위한 순열(P-Box)을 반복. 고속 병렬 처리에 유리하나 복호화 시 역함수 구현 필수. 알고리즘: AES, ARIA.",
        "<strong>주요 표준 대칭키 알고리즘:</strong>",
        "• <code>DES</code>: 64비트 블록, 56비트 키 길이 (취약하여 퇴출).",
        "• <code>AES (Rijndael)</code>: 128비트 고정 블록, 128/192/256비트 키 길이, 라운드 수 10/12/14회. 전 세계 표준.",
        "• <code>국산 표준</code>: SEED(KISA 개발, 128비트, Feistel), ARIA(국정원 개발, 128비트, SPN), LEA(초경량 고속 블록 암호)."
      ]
    },
    {
      "id": "crypto_content_02",
      "type": "content",
      "category": "crypto",
      "category_name": "정보보안 일반·암호학",
      "title": "블록 암호 운영 모드 5종(ECB·CBC·CFB·OFB·CTR) 비교",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>블록 암호 운영 모드 비교 분석:</strong>",
        "• <code>ECB (Electronic Codebook)</code>: 각 블록을 독립적으로 암호화. 초기화벡터(IV) 불필요. 단점: 동일한 평문 블록이 항상 동일한 암호문 블록으로 변환되어 데이터 패턴이 그대로 노출됨 (보안 취약, 사용 금지).",
        "• <code>CBC (Cipher Block Chaining)</code>: 각 평문 블록을 이전 단계 암호문 블록과 XOR 연산 후 암호화. 첫 블록에 무작위 IV 필수. 한 블록의 에러가 다음 블록까지 2개 블록에 전파됨.",
        "• <code>CFB (Cipher Feedback)</code>: 이전 암호문 블록을 암호화한 뒤 평문과 XOR 연산하여 스트림 암호처럼 동작.",
        "• <code>OFB (Output Feedback)</code>: 암호화 함수의 출력값을 다음 암호화 입력으로 피드백. 전송 중 비트 에러가 다른 블록으로 전파되지 않음.",
        "• <code>CTR (Counter Mode)</code>: 1씩 증가하는 카운터 값을 암호화한 뒤 평문과 XOR. 완벽한 병렬 처리가 가능하여 최신 고속 통신(IPSec, WPA2)에서 표준으로 채택."
      ]
    },
    {
      "id": "crypto_content_03",
      "type": "content",
      "category": "crypto",
      "category_name": "정보보안 일반·암호학",
      "title": "공개키 암호(RSA·ECC) 및 단방향 해시 함수의 3대 안전성",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>공개키 암호 알고리즘:</strong> 암호화키(공개키)와 복호화키(개인키)가 상이. 키 분배가 용이하나 대칭키에 비해 연산 속도가 느림. N명 간 필요한 키 수: 2N개.",
        "• <code>RSA</code>: 거대한 두 소수의 곱을 구하기는 쉬우나, 이를 소인수분해하기는 극도로 어렵다는 수학적 난해성에 기반.",
        "• <code>ECC (Elliptic Curve Cryptography)</code>: 타원곡선 상의 이산대수 문제 기반. 256비트 키 길이로 RSA 3,072비트 급의 안전성을 제공하여 모바일 및 경량 환경에 최적화.",
        "<strong>단방향 해시 함수의 3대 보안 특성:</strong>",
        "1. <code>제1 역상 저항성 (Pre-image Resistance)</code>: 주어진 해시값 h에 대해, H(x) = h를 만족하는 원본 x를 찾는 것이 계산상 불가능해야 함.",
        "2. <code>제2 역상 저항성 (Second Pre-image Resistance)</code>: 특정 입력 x가 주어졌을 때, H(x) = H(y)이고 x ≠ y를 만족하는 또 다른 입력 y를 찾는 것이 계산상 불가능해야 함.",
        "3. <code>충돌 저항성 (Collision Resistance)</code>: H(x) = H(y)를 만족하는 임의의 서로 다른 두 입력쌍 (x, y)를 찾는 것이 계산상 불가능해야 함 (생일 공격 방어)."
      ]
    },
    {
      "id": "crypto_content_04",
      "type": "content",
      "category": "crypto",
      "category_name": "정보보안 일반·암호학",
      "title": "전자서명·PKI 구조 및 비밀번호 단방향 저장 안전성",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>전자서명(Digital Signature) 3대 보장 기능:</strong>",
        "• <code>송신처 인증</code>: 송신자의 개인키로 서명하므로 진정한 작성자임을 증명.",
        "• <code>무결성</code>: 본문 내용이 위·변조되지 않았음을 수신자가 공개키 검증으로 입증.",
        "• <code>부인 방지 (Non-repudiation)</code>: 송신자가 메시지를 전송한 사실을 사후에 부인할 수 없음.",
        "<strong>인증서 유효성 검증 방식:</strong>",
        "• <code>CRL (Certificate Revocation List)</code>: 인증기관이 주기적으로 발행하는 폐지된 인증서 목록. 단점: 실시간 폐지 상태 반영 지연, 파일 다운로드 부하.",
        "• <code>OCSP (Online Certificate Status Protocol)</code>: 클라이언트가 실시간으로 OCSP 서버에 단일 인증서의 유효 여부(Good, Revoked, Unknown)를 조회.",
        "<strong>안전한 비밀번호 해시 저장 기법:</strong>",
        "• 단순 고속 해시(MD5, SHA-256) 단독 사용 금지 (GPU 기반 레인보우 테이블 공격 취약).",
        "• <code>솔팅(Salting)</code>: 사용자마다 128비트 이상의 무작위 난수 Salt를 생성하여 결합.",
        "• <code>키 스트레칭(Key Stretching)</code>: 해시 연산을 수만 번 이상 반복 반복하여 브루트포스 속도 저하. 표준 알고리즘: <code>PBKDF2, bcrypt, scrypt, Argon2</code>."
      ]
    },
    {
      "id": "crypto_content_05",
      "type": "content",
      "category": "crypto",
      "category_name": "정보보안 일반·암호학",
      "title": "보안 모델 비교(BLP 기밀성 vs Biba 무결성 vs 만리장성)",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>BLP (Bell-LaPadula) 모델 - 기밀성 최우선 군사 모델:</strong>",
        "• <code>단순 보안 속성 (No Read Up)</code>: 주체는 자신보다 높은 보안 등급의 객체를 읽을 수 없음.",
        "• <code>*(스타) 보안 속성 (No Write Down)</code>: 주체는 자신보다 낮은 보안 등급의 객체에 데이터를 쓸 수 없음 (상위 기밀 정보가 하위 등급으로 누설 차단).",
        "<strong>Biba 모델 - 무결성 최우선 상업 모델:</strong>",
        "• <code>단순 무결성 속성 (No Read Down)</code>: 주체는 자신보다 낮은 무결성 등급의 객체를 읽을 수 없음 (오염된 데이터 수신 차단).",
        "• <code>*(스타) 무결성 속성 (No Write Up)</code>: 주체는 자신보다 높은 무결성 등급의 객체에 데이터를 쓸 수 없음 (상위 신뢰 데이터 오염 방지).",
        "<strong>Clark-Wilson 모델:</strong> 잘 형성된 트랜잭션(Well-formed Transaction)과 엄격한 직무 분리(Separation of Duties)를 통해 기업 회계 및 금융 무결성 보장.",
        "<strong>만리장성(Chinese Wall / Brewer-Nash) 모델:</strong> 이해관계 상충(Conflict of Interest)을 방지하기 위해, 사용자의 이전 접근 이력에 따라 충돌 집합에 속한 타 경쟁사의 데이터 접근을 동적으로 차단하는 상업 윤리 모델."
      ]
    },
    {
      "id": "law_content_01",
      "type": "content",
      "category": "law",
      "category_name": "정보보안 관리·법률",
      "title": "위험관리 프로세스 및 정량적·정성적 위험분석 기법",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>위험(Risk)의 구성 3요소:</strong> 자산(Asset) × 위협(Threat) × 취약점(Vulnerability).",
        "<strong>정량적 위험분석 핵심 공식:</strong>",
        "• <code>SLE (단일손실예상액)</code> = 자산가치(AV) × 노출계수(EF, %)",
        "• <code>ALE (연간손실예상액)</code> = SLE × ARO (연간발생빈도)",
        "• 통제 대책의 비용편익(CBA) = 통제 전 ALE - 통제 후 ALE - 통제 연간비용 (0보다 커야 도입 타당).",
        "<strong>정성적 위험분석 기법:</strong>",
        "• <code>델파이법 (Delphi)</code>: 전문가 그룹에게 익명 설문지를 반복 배포하여 편견 없이 합의 도출.",
        "• <code>시나리오법</code>: 발생 가능한 침해 시나리오를 구성하여 예상 손실을 정성 평가.",
        "• <code>순위결정법</code>: 위험의 상대적 우선순위만을 서열화하는 신속한 방식."
      ]
    },
    {
      "id": "law_content_02",
      "type": "content",
      "category": "law",
      "category_name": "정보보안 관리·법률",
      "title": "위험 처리 4대 전략 및 재해복구계획(BCP/DRP)",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>위험 처리 4대 전략:</strong>",
        "• <code>위험 감소 (Reduction)</code>: 보안 통제 및 솔루션을 도입하여 위험 수준을 DOA 이하로 낮춤.",
        "• <code>위험 회피 (Avoidance)</code>: 위험이 따르는 사업 영역이나 서비스를 중단/철수.",
        "• <code>위험 전가 (Transference)</code>: 보험 가입이나 보안 관제 외주를 통해 손실 책임을 제3자에게 이전.",
        "• <code>위험 수용 (Acceptance)</code>: 수용 가능 위험 수준(DOA) 이하의 잔여 위험을 경영진 승인 하에 감수.",
        "<strong>재해복구 목표 지표:</strong>",
        "• <code>RTO (목표 복구 시간)</code>: 재해 발생 후 업무가 정상 복구될 때까지 허용되는 최대 중단 시간.",
        "• <code>RPO (목표 복구 시점)</code>: 재해 발생 시 데이터 손실을 허용할 수 있는 최대 유실 시점.",
        "<strong>재해복구센터 4대 유형:</strong>",
        "• <code>Mirror Site</code>: 주 센터와 동일한 설비를 실시간 동기화 복제. RTO=0에 수렴. 최고 비용.",
        "• <code>Hot Site</code>: 주 센터와 동일 구성으로 대기하며 데이터 준실시간 동기화. RTO 수시간 이내.",
        "• <code>Warm Site</code>: 중요 장비만 구비하고 백업 테이프 등으로 데이터 수동 복구. RTO 수일 이내.",
        "• <code>Cold Site</code>: 기본 공간만 확보하고 장비는 재해 후 조달. RTO 수주 이상 소요. 최저 비용."
      ]
    },
    {
      "id": "law_content_03",
      "type": "content",
      "category": "law",
      "category_name": "정보보안 관리·법률",
      "title": "개인정보보호법 고유식별정보 4종 및 안전성 확보조치 기준",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>고유식별정보 4종:</strong> <code>주민등록번호, 여권번호, 운전면허번호, 외국인등록번호</code>. 원칙적 처리 금지이며, 별도 분리 동의 또는 법령의 구체적 근거가 있는 경우만 허용.",
        "• <strong>주민등록번호 암호화 의무:</strong> 인터넷망 및 내부망, PC 등 저장 위치와 무관하게 법적 예외 없이 100% 암호화 저장 강제.",
        "<strong>안전성 확보조치 기준 주요 고시 규정:</strong>",
        "• <code>접속기록 보관 기간</code>: 기본 1년 이상 보관. 단, 5만 명 이상의 정보주체 또는 고유식별정보/민감정보 처리시스템은 <strong>2년 이상</strong> 보관.",
        "• <code>접속기록 정기 점검</code>: 반기 1회가 아닌 <strong>월 1회 이상</strong> 정기 점검하여 비정상 다운로드, 열람 이상징후 탐지.",
        "• <code>비밀번호 작성 규칙</code>: 영문, 숫자, 특수문자 중 3종 이상 조합 시 8자리 이상, 2종 이상 조합 시 10자리 이상.",
        "• <code>물리적 안전조치</code>: 전산실, 자료보관실 등 통제구역 출입기록은 최소 3년 이상 보관."
      ]
    },
    {
      "id": "law_content_04",
      "type": "content",
      "category": "law",
      "category_name": "정보보안 관리·법률",
      "title": "개인정보 유출 통지·신고 시한 및 과징금 부과 체계",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>개인정보 유출 통지 및 신고 기준:</strong>",
        "• 개인정보 유출 확인 시 정당한 사유가 없는 한 <strong>72시간 이내</strong>에 정보주체에게 통지하고, 1천 명 이상 유출 시 개인정보보호위원회 또는 KISA에 지체 없이 신고.",
        "• <strong>정보주체 법정 필수 5대 통지 항목:</strong>",
        "1. 유출된 개인정보의 항목",
        "2. 유출된 시점과 그 경위",
        "3. 유출로 인해 발생할 수 있는 피해를 최소화하기 위하여 정보주체가 취할 수 있는 방법",
        "4. 개인정보처리자의 대응조치 및 피해 구제절차",
        "5. 정보주체에게 피해가 발생한 경우 신고 등을 접수할 수 있는 담당부서 및 연락처",
        "<strong>과징금 상한 개정:</strong> 전체 매출액의 <strong>3% 이하</strong> 부과 (단, 위반행위와 관련 없는 매출액임을 사업자가 입증한 경우 해당 매출액 제외)."
      ]
    },
    {
      "id": "law_content_05",
      "type": "content",
      "category": "law",
      "category_name": "정보보안 관리·법률",
      "title": "CISO 지정 및 겸직 금지 요건 / ISMS-P 인증 제도",
      "badge": "내용별 핵심정리",
      "points": [
        "<strong>CISO(정보보호최고책임자) 겸직 금지 의무:</strong>",
        "• 자산총액 1조 원 이상 또는 ISMS 의무대상자 중 정보통신서비스 부문 자산 1천억 원 이상 및 매출 1천억 원 이상인 중대형 기업은 CISO의 타 직무(CIO, IT개발, 경영 등) 겸직을 법적으로 엄격히 금지함 (전임 CISO 지정 의무).",
        "<strong>ISMS-P 인증 기준 체계 (총 102개 인증기준):</strong>",
        "• <code>1영역 관리체계 수립 및 운영 (16개)</code>: 경영진 참여, 위험관리, 정책 수립 등.",
        "• <code>2영역 보호대책 요구사항 (64개)</code>: 자산 관리, 접근 통제, 암호화, 시스템 개발, 물리 보안 등.",
        "• <code>3영역 개인정보 처리단계별 요구사항 (22개)</code>: 수집, 이용·제공, 파기, 정보주체 권리 보장 등."
      ]
    },
    {
      "id": "term_aslr",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] ASLR (Address Space Layout Randomization)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 프로그램 실행 시마다 스택, 힙, 라이브러리 메모리 주소를 난수화하여 고정된 주소를 노리는 셸코드 실행을 차단하는 메모리 보호 기법."
      ]
    },
    {
      "id": "term_dep___nx",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] DEP / NX (Data Execution Prevention / No-Execute)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 스택 및 힙 메모리 영역의 실행 권한을 원천 박탈하여 버퍼에 삽입된 악성 바이트 코드가 구동되지 못하도록 차단하는 기술."
      ]
    },
    {
      "id": "term_stack_canary",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] Stack Canary (스택 카나리 (스택 가드))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 함수의 지역변수와 SFP(복귀주소) 사이에 무작위 난수 카나리 값을 삽입하여, 함수 종료 시 카나리 변조 여부를 검사해 오버플로우를 감지하는 기법."
      ]
    },
    {
      "id": "term_toctou",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] TOCTOU (Time of Check to Time of Use)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 권한 검사 시점과 실제 자원 사용 시점 사이의 극미한 시간차를 악용하여 심볼릭 링크를 교체해 관리자 권한을 탈취하는 경쟁 조건 취약점."
      ]
    },
    {
      "id": "term_rootkit",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] Rootkit (루트킷)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 시스템 관리자 권한을 획득한 후 침투 사실을 숨기기 위해 ps, ls, netstat 등 명령어를 변조하거나 커널 LKM을 조작하여 프로세스 및 파일을 은닉하는 도구 세트."
      ]
    },
    {
      "id": "term_wtmp___utmp",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] wtmp / utmp (리눅스 로그인 계정 로그)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> wtmp는 성공한 로그인/로그아웃/재부팅 전체 누적 이력(last 조회), utmp는 현재 접속 중인 활성 사용자 상태(who/w 조회)를 기록하는 바이너리 로그."
      ]
    },
    {
      "id": "term_btmp___lastlog",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] btmp / lastlog (접속 실패 및 최종 접속 로그)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> btmp는 로그인 실패 시도 이력(lastb 조회), lastlog는 각 사용자 계정별 최종 접속 일시 및 출발지 IP(lastlog 조회)를 기록하는 바이너리 로그."
      ]
    },
    {
      "id": "term_sticky_bit",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] Sticky Bit (스티키 비트 (1000))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> /tmp 공용 디렉토리에 부여되어 누구나 파일을 생성할 수 있으나, 삭제 및 수정은 오직 해당 파일의 소유자와 root만 가능하도록 제한하는 특수 권한 비트."
      ]
    },
    {
      "id": "term_pam",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] PAM (Pluggable Authentication Modules)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 응용프로그램 재컴파일 없이 시스템 인증 정책을 교체할 수 있는 플러그인 모듈 인터페이스 (required, requisite, sufficient, optional 플래그 운영)."
      ]
    },
    {
      "id": "term_chattr_(+i)",
      "type": "term",
      "category": "system",
      "category_name": "시스템 필수 용어",
      "title": "[용어] chattr (+i) (파일 불변 속성 설정)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 리눅스 파일에 +i(Immutable) 속성을 부여할 경우 root 권한자라 할지라도 파일의 수정, 삭제, 이름 변경, 링크 생성을 원천 차단하는 명령어."
      ]
    },
    {
      "id": "term_syn_cookie",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] SYN Cookie (신 쿠키)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> SYN Flooding 공격 시 서버 메모리 백로그 큐를 소진하지 않고, 클라이언트 연결 정보를 암호화 해시하여 TCP Sequence Number에 인코딩해 회신하는 방어 기법."
      ]
    },
    {
      "id": "term_land_attack",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] Land Attack (랜드 어택)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 패킷의 출발지 IP/Port와 목적지 IP/Port를 희생자 자신의 IP/Port로 조작하여 자기 자신과 무한 루프 연결을 유발시키는 서비스 거부 공격."
      ]
    },
    {
      "id": "term_smurf_attack",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] Smurf Attack (스머프 어택)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 출발지 IP를 희생자 IP로 위조한 후 다이렉트 브로드캐스트 주소로 ICMP Echo Request를 전송하여 네트워크 내 모든 호스트의 응답을 희생자에게 증폭 집중시키는 공격."
      ]
    },
    {
      "id": "term_teardrop",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] TearDrop (티어드롭 어택)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> IP 패킷 단편화 시 오프셋 값을 인위적으로 중첩·왜곡시켜 수신 호스트가 패킷을 재조합하는 과정에서 크래시 및 재부팅을 유발하는 취약점 공격."
      ]
    },
    {
      "id": "term_slowloris",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] Slowloris (슬로로리스)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> HTTP 요청 헤더의 끝을 알리는 개행문자(\\r\\n\\r\\n)를 전송하지 않고 불완전한 헤더를 천천히 유지하여 웹 서버의 가용 연결 슬롯을 고갈시키는 L7 DoS 공격."
      ]
    },
    {
      "id": "term_rudy",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] RUDY (R-U-Dead-Yet (Slow HTTP POST))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> HTTP POST 요청 시 Content-Length를 거대하게 설정하고 본문 바이트 데이터를 극도로 느린 속도로 분할 전송하여 서버 연결을 장시간 점유하는 공격."
      ]
    },
    {
      "id": "term_ipsec_(ah___esp)",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] IPSec (AH / ESP) (IP Security Protocol)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 네트워크 계층(L3) VPN 표준 프로토콜로, AH는 인증과 무결성만 제공(NAT 불가), ESP는 기밀성(암호화), 무결성, 인증을 모두 제공(NAT-T 지원)."
      ]
    },
    {
      "id": "term_ike",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] IKE (Internet Key Exchange (UDP 500))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> IPSec에서 양단 호스트 간 보안 결합(SA) 협상 및 대칭 세션키를 Diffie-Hellman 알고리즘으로 안전하게 자동 생성·교환하는 표준 프로토콜."
      ]
    },
    {
      "id": "term_wpa3_sae",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] WPA3 SAE (동등동시인증 (SAE Handshake))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> WPA3 무선 LAN 표준에 도입된 상호 인증 프로토콜로, 강력한 암호화 키 교환을 통해 기존 4-Way Handshake의 오프라인 사전 대입 공격을 원천 무력화함."
      ]
    },
    {
      "id": "term_dnssec",
      "type": "term",
      "category": "network",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] DNSSEC (DNS 보안 확장 프로토콜)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> DNS 응답 데이터에 공개키 기반 전자서명(RRSIG)을 부착하여 악의적인 DNS 캐시 포이즈닝 및 도메인 파밍을 방지하는 보안 표준."
      ]
    },
    {
      "id": "term_preparedstatement",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] PreparedStatement (파라미터화된 쿼리 (바인딩 변수))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> SQL 쿼리 컴파일 시점에 입력값을 데이터 리터럴로 고정 바인딩하여, 사용자 입력값이 쿼리 문법 구조를 변조하지 못하도록 만드는 SQLi 최우선 방어책."
      ]
    },
    {
      "id": "term_stored_xss",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] Stored XSS (저장형 크로스사이트 스크립팅)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 공격자가 삽입한 악성 자바스크립트가 게시판 DB에 영구 저장되어, 해당 글을 조회하는 모든 무고한 사용자의 브라우저에서 자동 실행되는 가장 치명적인 XSS."
      ]
    },
    {
      "id": "term_csrf_token",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] CSRF Token (크로스사이트 요청 위조 방지 토큰)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 사용자의 세션마다 서버가 예측 불가능한 난수 토큰을 발급하여 폼 전송 시 검증함으로써, 타 사이트로부터 위조된 비인가 상태 변경 요청을 차단하는 기법."
      ]
    },
    {
      "id": "term_ssrf",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] SSRF (Server-Side Request Forgery)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 웹 서버가 취약한 URL 요청 파라미터를 그대로 처리할 때, 공격자가 서버를 중계 삼아 접근 통제된 내부망 인트라넷이나 클라우드 메타데이터 API를 호출하는 공격."
      ]
    },
    {
      "id": "term_httponly",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] HttpOnly (쿠키 보안 플래그)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 브라우저 자바스크립트의 document.cookie 객체 접근을 원천 차단하여, XSS 공격이 발생하더라도 세션 하이재킹용 쿠키 탈취를 방지하는 설정."
      ]
    },
    {
      "id": "term_samesite_cookie",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] SameSite Cookie (쿠키 전송 범위 제어 속성)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> Strict(타 사이트 링크 시 쿠키 전송 완전 차단) 또는 Lax(안전한 GET 탐색만 허용)를 설정하여 서드파티 컨텍스트에서의 CSRF 공격을 방어하는 최신 표준."
      ]
    },
    {
      "id": "term_hsts",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] HSTS (HTTP Strict Transport Security)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 브라우저가 해당 도메인 접속 시 첫 연결부터 모든 통신을 오직 HTTPS로만 강제 연결하도록 지시하여 평문 다운그레이드(SSL Stripping)를 방어하는 헤더."
      ]
    },
    {
      "id": "term_csp",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] CSP (Content Security Policy)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 웹 브라우저가 스크립트, 스타일, 이미지 등을 로드하고 실행할 수 있는 신뢰할 수 있는 출처 도메인을 화이트리스트로 지정하여 XSS 및 인젝션을 차단하는 헤더."
      ]
    },
    {
      "id": "term_tde",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] TDE (Transparent Data Encryption)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> DBMS 스토리지 파일 레벨에서 자동으로 실시간 암·복호화를 수행하여, 응용프로그램 수정 없이 백업 파일 유출 시 데이터 평문 유출을 방지하는 투명 암호화."
      ]
    },
    {
      "id": "term_dual_signature",
      "type": "term",
      "category": "app",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] Dual Signature (이중 서명 (SET 프로토콜))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 전자상거래에서 주문정보 해시와 결제정보 해시를 결합하여 한 번에 전자서명함으로써, 상점은 카드번호를 못 보고 카드사는 주문 품목을 알 수 없게 보장하는 기법."
      ]
    },
    {
      "id": "term_feistel_vs_spn",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Feistel vs SPN (블록 암호 구조)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> Feistel은 평문을 좌우 분할하여 스왑하며 암·복호화 구조가 동일(DES, SEED), SPN은 치환(S-Box)과 순열(P-Box)을 반복해 병렬 연산에 최적화(AES, ARIA)."
      ]
    },
    {
      "id": "term_aes",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] AES (Advanced Encryption Standard)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> Rijndael 알고리즘 기반 전 세계 표준 대칭키 블록 암호. 128비트 블록 크기, 128/192/256비트 키 길이를 지원하며 고속 하드웨어 연산 지원."
      ]
    },
    {
      "id": "term_ctr_mode",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] CTR Mode (카운터 운영 모드)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 1씩 증가하는 카운터 값을 블록 암호화한 뒤 평문과 XOR 연산하는 운영 모드로, 완벽한 병렬 처리가 가능하여 최신 고속 보안 통신에서 널리 활용."
      ]
    },
    {
      "id": "term_rsa",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] RSA (소인수분해 기반 공개키 암호)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 거대한 두 소수의 곱을 구하기는 쉬우나 합성수를 소인수분해하기는 극도로 어렵다는 수학적 난해성을 활용한 공개키 암호 및 전자서명 알고리즘."
      ]
    },
    {
      "id": "term_ecc",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] ECC (타원곡선 암호 (Elliptic Curve))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 타원곡선 상의 이산대수 난해성에 기반하여, 256비트의 매우 짧은 키 길이로 RSA 3,072비트와 동등한 안전성을 제공하는 모바일/경량 표준 공개키 암호."
      ]
    },
    {
      "id": "term_collision_resistance",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Collision Resistance (충돌 저항성)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 단방향 해시 함수에서 H(x) = H(y)를 만족하는 임의의 서로 다른 두 입력값 쌍 (x, y)를 찾아내는 것이 계산상 불가능해야 한다는 안전성 특성."
      ]
    },
    {
      "id": "term_ocsp",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] OCSP (Online Certificate Status Protocol)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 인증서 폐지 목록(CRL) 파일 전체를 다운로드하지 않고, 단일 인증서의 시리얼 번호로 폐지 여부(Good/Revoked/Unknown)를 실시간 온라인 조회하는 프로토콜."
      ]
    },
    {
      "id": "term_digital_envelope",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Digital Envelope (전자봉투)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 대용량 본문은 빠른 대칭 세션키로 암호화하고, 그 세션키만을 수신자의 공개키로 암호화하여 함께 전달하는 안전하고 효율적인 하이브리드 암호 전달 기법."
      ]
    },
    {
      "id": "term_pbkdf2___bcrypt",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] PBKDF2 / bcrypt (패스워드 전용 해시 함수)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 단방향 해시 시 솔트(Salt)를 추가하고 수만 번의 반복 연산(Key Stretching)을 강제하여 GPU 및 전용 하드웨어를 통한 고속 레인보우 테이블 무차별 대입을 무력화함."
      ]
    },
    {
      "id": "term_blp_model",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] BLP Model (Bell-LaPadula (기밀성 모델))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> No Read Up(상위 등급 읽기 금지), No Write Down(하위 등급 쓰기 금지) 원칙을 통해 상위 기밀 데이터의 하위 등급 유출을 철저히 차단하는 군사 보안 모델."
      ]
    },
    {
      "id": "term_biba_model",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Biba Model (비바 무결성 모델)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> No Read Down(하위 무결성 읽기 금지), No Write Up(상위 무결성 쓰기 금지) 원칙을 적용하여 신뢰할 수 없는 오염된 데이터가 상위 시스템으로 유입되는 것을 방지."
      ]
    },
    {
      "id": "term_chinese_wall",
      "type": "term",
      "category": "crypto",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Chinese Wall (만리장성 모델 (이해관계 상충 방지))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 금융 및 컨설팅 기업에서 사용자의 이전 데이터 접근 이력에 따라 이해관계가 상충되는 경쟁사의 기밀 데이터 접근을 동적으로 차단하는 상업 보안 모델."
      ]
    },
    {
      "id": "term_ale___sle___aro",
      "type": "term",
      "category": "law",
      "category_name": "관리·법률 필수 용어",
      "title": "[용어] ALE / SLE / ARO (정량적 위험분석 3대 공식)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> SLE(단일손실예상액) = 자산가치 × 노출계수, ALE(연간손실예상액) = SLE × ARO(연간발생빈도). 통제 대책 도입 타당성은 통제 전후 ALE 절감액으로 평가."
      ]
    },
    {
      "id": "term_rto_vs_rpo",
      "type": "term",
      "category": "law",
      "category_name": "관리·법률 필수 용어",
      "title": "[용어] RTO vs RPO (재해복구 목표 지표)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> RTO(목표 복구 시간)는 재해 발생 후 업무가 정상 복구될 때까지 허용 가능한 최대 다운타임, RPO(목표 복구 시점)는 허용 가능한 최대 데이터 유실 시점."
      ]
    },
    {
      "id": "term_72시간_통지_의무",
      "type": "term",
      "category": "law",
      "category_name": "관리·법률 필수 용어",
      "title": "[용어] 72시간 통지 의무 (개인정보 유출 신고 시한)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 개인정보 유출 사고 확인 시 정당한 사유가 없는 한 72시간 이내에 정보주체에게 통지하고, 1천 명 이상 유출 시 개인정보위 또는 KISA에 법적 필수 신고."
      ]
    }
  ]
};

window.INFOSEC_PRACTICAL_DATA = {
  "title": "2026 이기적 정보보안기사 (실기) 100제 & 단답형 족보·실무 가이드 50선",
  "description": "2026 이기적 정보보안기사 올인원 실기 편제 기준 1~4회(단답 50제 + 서술실무 50제) 총 100문항 및 실기 내용별 심층 요약 20선 + 단답형 족보 30선",
  "questions": [
    {
      "id": "IP1_Q1",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스 환경에서 일반 파일 기본 권한 666, 디렉토리 기본 권한 777일 때, 파일은 640(-rw-r-----), 디렉토리는 750(drwxr-x---)으로 생성되도록 지정하는 umask 값은 무엇인가?",
      "options": [
        "022",
        "027",
        "077",
        "037"
      ],
      "answer": 2,
      "explanation": "디렉토리(777 - 027 = 750), 파일(666 - 027 = 640, 실행비트 미부여)을 만족하는 보안 표준 umask 값은 027입니다."
    },
    {
      "id": "IP1_Q2",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 아파치(Apache) 웹 서버에서 디렉토리 인덱싱(디렉토리 내 파일 목록 전체 노출) 취약점을 차단하기 위해 httpd.conf 설정 파일의 Options 지시자에서 반드시 제거해야 하거나 앞에 '-'를 붙여야 하는 옵션 명칭은?",
      "options": [
        "Indexes",
        "FollowSymLinks",
        "Includes",
        "ExecCGI"
      ],
      "answer": 1,
      "explanation": "Options -Indexes 또는 Indexes 옵션을 제거해야 디렉토리 목록 노출(Directory Listing)을 방지할 수 있습니다."
    },
    {
      "id": "IP1_Q3",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스 시스템에서 현재 활성화된 네트워크 연결 상태, 열린 포트 번호, 그리고 해당 포트를 사용 중인 프로세스 ID(PID)와 프로그램 이름을 숫자로 확인하기 위한 netstat 명령어 옵션 조합은?",
      "options": [
        "netstat -antp",
        "netstat -r",
        "netstat -i",
        "netstat -s"
      ],
      "answer": 1,
      "explanation": "-a(모든 소켓), -n(IP/포트 숫자로 표시), -t(TCP), -p(프로세스 ID/이름 표시) 옵션인 'netstat -antp'가 침해사고 분석의 기본 명령어입니다."
    },
    {
      "id": "IP1_Q4",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 최근 24시간 이내에 수정(Modify)된 파일을 전체 루트 디렉토리(/)부터 검색하기 위한 find 명령어의 올바른 옵션은?",
      "options": [
        "find / -mtime -1",
        "find / -atime +1",
        "find / -ctime 1",
        "find / -perm 777"
      ],
      "answer": 1,
      "explanation": "-mtime -1은 수정된 지 1일(24시간) 이내인 파일을 의미합니다. (+1: 24시간 이전, 1: 정확히 24~48시간 사이)"
    },
    {
      "id": "IP1_Q5",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] TCP Wrapper 접근 제어 파일(/etc/hosts.allow, /etc/hosts.deny)에서 동일한 IP나 대역이 양쪽 파일 모두에 정의되어 있을 때 적용되는 우선순위 규칙은?",
      "options": [
        "/etc/hosts.allow 파일이 먼저 적용되어 허용된다.",
        "/etc/hosts.deny 파일이 먼저 적용되어 차단된다.",
        "나중에 수정된 파일이 우선한다.",
        "동일하게 충돌 시 무조건 차단된다."
      ],
      "answer": 1,
      "explanation": "TCP Wrapper는 /etc/hosts.allow를 먼저 확인하고 일치하면 즉시 허용하며, 없을 때 hosts.deny를 확인합니다. 둘 다 없으면 기본 허용됩니다."
    },
    {
      "id": "IP1_Q6",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스 iptables 방화벽에서 외부에서 서버의 22번(SSH) 포트로 들어오는 특정 IP(192.168.1.100)의 모든 TCP 접속 패킷을 폐기(차단)하고 로그를 남기지 않기 위한 명령어로 올바른 것은?",
      "options": [
        "iptables -A INPUT -p tcp -s 192.168.1.100 --dport 22 -j DROP",
        "iptables -D INPUT -p tcp -s 192.168.1.100 --sport 22 -j REJECT",
        "iptables -I OUTPUT -p tcp -d 192.168.1.100 --dport 22 -j ACCEPT",
        "iptables -A FORWARD -p tcp -s 192.168.1.100 -j DROP"
      ],
      "answer": 1,
      "explanation": "-A INPUT(인바운드 체인 추가), -p tcp(프로토콜), -s(출발지 IP), --dport 22(목적지 포트), -j DROP(폐기)이 정확한 문법입니다."
    },
    {
      "id": "IP1_Q7",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] Snort IDS 규칙에서 패킷 페이로드 내 바이너리 16진수 바이트열(예: 0x90 0x90 NOP Sled)을 탐지하기 위해 content 옵션 안에서 바이트열을 감싸는 기호는?",
      "options": [
        "파이프 (|...|)",
        "따옴표 (\"...\")",
        "대괄호 ([...])",
        "중괄호 ({...})"
      ],
      "answer": 1,
      "explanation": "Snort에서 바이너리 바이트값은 파이프(|) 기호로 감쌉니다. 예: content:\"|90 90 90 90|\";"
    },
    {
      "id": "IP1_Q8",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스에서 각 사용자별 크론탭(crontab) 작업 설정 파일이 저장되는 표준 디렉토리 경로는?",
      "options": [
        "/var/spool/cron/",
        "/etc/cron.hourly/",
        "/var/log/cron/",
        "/usr/bin/crontab"
      ],
      "answer": 1,
      "explanation": "각 사용자별 crontab 설정은 /var/spool/cron/ 또는 /var/spool/cron/crontabs/ 디렉토리에 사용자 계정명 파일로 저장됩니다."
    },
    {
      "id": "IP1_Q9",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 시스템 명령어 실행 취약점(Command Injection)에서 한 줄에 여러 명령어를 연속으로 실행하거나 앞선 명령어의 성공 여부와 상관없이 뒷 명령어를 실행시키는 셸 메타문자는?",
      "options": [
        "; (세미콜론) 또는 | (파이프)",
        "* (와일드카드)",
        "> (리디렉션)",
        "$ (변수참조)"
      ],
      "answer": 1,
      "explanation": "세미콜론(;)은 이전 명령 종료 후 다음 명령을 순차 실행하며, 파이프(|)는 이전 명령어의 출력을 다음 명령어로 넘겨 임의 명령을 실행하게 만듭니다."
    },
    {
      "id": "IP1_Q10",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 자바 시큐어코딩에서 XSS 공격을 방지하기 위해 사용자 입력 문자 중 HTML 특수문자 '<', '>', '&', '\"', '\\''를 안전하게 치환하는 것을 무엇이라 하는가?",
      "options": [
        "HTML 인코딩 (HTML Entity 치환)",
        "Base64 인코딩",
        "URL 인코딩",
        "해싱"
      ],
      "answer": 1,
      "explanation": "&lt;, &gt;, &amp;, &quot;, &#x27; 등으로 치환하는 HTML Entity 인코딩이 XSS 방어의 필수 조치입니다."
    },
    {
      "id": "IP1_Q11",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 개인정보보호법 제34조에 따라 개인정보 유출 시 정보주체에게 지체 없이 통지해야 하는 법정 필수 통지 항목 5가지에 해당하지 않는 것은?",
      "options": [
        "유출된 개인정보의 항목",
        "유출된 시점과 그 경위",
        "유출 사고를 일으킨 해커의 신원 및 IP 주소",
        "정보주체가 취할 수 있는 조치 및 피해신고 접수처",
        "개인정보처리자의 대응조치 및 피해 구제절차"
      ],
      "answer": 3,
      "explanation": "법정 5대 통지사항은 ①유출 항목, ②유출 시점과 경위, ③피해 최소화 조치, ④대응조치 및 구제절차, ⑤담당부서 및 연락처입니다. 해커 신원은 포함되지 않습니다."
    },
    {
      "id": "IP1_Q12",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 디지털 포렌식의 5대 기본 원칙 중 '수집된 디지털 증거가 최초 발견 및 압수 시점부터 법정에 제출될 때까지 위·변조되지 않았음'을 입증하는 원칙은?",
      "options": [
        "무결성의 원칙",
        "정당성의 원칙",
        "재현성의 원칙",
        "신속성의 원칙",
        "연계보관성의 원칙 (Chain of Custody)"
      ],
      "answer": 1,
      "explanation": "무결성의 원칙(Integrity)은 해시값(MD5, SHA-256) 비교를 통해 증거가 일체 수정·변조되지 않았음을 입증하는 원칙입니다."
    },
    {
      "id": "IP1_Q13",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스 시스템에서 sshd_config 파일 설정 중 root 계정의 원격 직접 접속을 차단하기 위한 설정 지시자와 파라미터 값은?",
      "options": [
        "PermitRootLogin no",
        "AllowUsers root",
        "DenyUsers guest",
        "PasswordAuthentication no"
      ],
      "answer": 1,
      "explanation": "sshd_config 파일에 'PermitRootLogin no'를 설정하여 관리자 계정의 무차별 대입 직접 침투를 차단합니다."
    },
    {
      "id": "IP1_Q14",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 웹 서버의 보안 설정을 위해 서버의 상세 소프트웨어 버전(예: Apache/2.4.52) 정보가 HTTP 응답 헤더(Server:)에 노출되지 않도록 Apache에서 설정하는 지시자는?",
      "options": [
        "ServerTokens Prod 및 ServerSignature Off",
        "ServerName localhost",
        "Timeout 60",
        "KeepAlive Off"
      ],
      "answer": 1,
      "explanation": "ServerTokens Prod는 Server 헤더에 단순히 'Apache'만 출력하고 세부 OS/모듈 버전을 숨기며, ServerSignature Off는 에러 페이지의 서명을 제거합니다."
    },
    {
      "id": "IP1_Q15",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스 /etc/login.defs 파일에서 패스워드의 최대 사용 기간(일수)과 최소 사용 기간을 지정하는 지시자 명칭의 조합은?",
      "options": [
        "PASS_MAX_DAYS 및 PASS_MIN_DAYS",
        "MAX_PASS_AGE",
        "PASS_WARN_AGE",
        "ACCOUNT_LOCK_DAYS"
      ],
      "answer": 1,
      "explanation": "/etc/login.defs에서 PASS_MAX_DAYS(최대 유효일수, 예: 90), PASS_MIN_DAYS(최소 변경간격일수), PASS_MIN_LEN(최소길이) 등을 정의합니다."
    },
    {
      "id": "IP1_Q16",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] KISA 주요정보통신기반시설 기술적 취약점 분석·평가 기준에서 유닉스 root 계정의 환경변수 파일(.profile, .bashrc 등)의 PATH 설정 시 보안상 가장 위험하여 반드시 제거해야 하는 문자는?",
      "options": [
        "현재 디렉토리를 의미하는 '.'(마침표) 또는 빈 경로(::)",
        "/usr/bin",
        "/bin",
        "/sbin"
      ],
      "answer": 1,
      "explanation": "PATH 환경변수에 현재 디렉토리('.')가 앞에 포함되어 있으면 악의적인 공격자가 해당 디렉토리에 트로이목마 명령어(ls 등)를 두고 root가 실행하도록 유도할 수 있습니다."
    },
    {
      "id": "IP1_Q17",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 오픈SSL(OpenSSL)에서 TLS 암호화 통신 시 클라이언트와 서버 간 연결 유지를 위한 하트비트 확장 프로토콜의 버퍼 경계 검증 미흡으로 서버의 메모리 데이터가 평문으로 유출되었던 치명적 취약점 명칭은?",
      "options": [
        "Heartbleed (CVE-2014-0160)",
        "POODLE",
        "Shellshock",
        "EternalBlue",
        "Log4Shell"
      ],
      "answer": 1,
      "explanation": "Heartbleed 취약점은 OpenSSL의 Heartbeat 요청 패킷 길이 검증 누락으로 최대 64KB의 프로세스 메모리(비밀키, 세션쿠키 등)가 평문으로 유출되는 취약점입니다."
    },
    {
      "id": "IP1_Q18",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스에서 패스워드 무차별 대입 공격(Brute Force)을 방어하기 위해 /etc/pam.d/system-auth에 계정 잠금 모듈을 설정할 때 사용하는 PAM 모듈 이름은?",
      "options": [
        "pam_faillock.so (또는 pam_tally2.so)",
        "pam_unix.so",
        "pam_rootok.so",
        "pam_env.so"
      ],
      "answer": 1,
      "explanation": "계정 로그인 실패 횟수 초과 시 잠금(lock)을 처리하는 표준 모듈은 pam_faillock.so (최신 RHEL) 또는 pam_tally2.so (이전 버전)입니다."
    },
    {
      "id": "IP1_Q19",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 윈도우 시스템에서 파일 및 폴더의 공유 권한 및 NTFS 접근 제어 목록(ACL)을 커맨드라인에서 확인하고 수정하기 위해 사용하는 표준 명령어는?",
      "options": [
        "icacls (또는 cacls)",
        "net share",
        "attrib",
        "takeown"
      ],
      "answer": 1,
      "explanation": "icacls는 윈도우 파일/디렉토리의 DACL 및 SACL 접근 권한을 확인하고 부여·제거하는 핵심 보안 명령어입니다."
    },
    {
      "id": "IP1_Q20",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스에서 디스크 용량 고갈로 인한 시스템 불능을 막기 위해 사용자별, 그룹별로 사용할 수 있는 디스크 공간 및 파일 개수(i-node)를 제한하는 기능은?",
      "options": [
        "Disk Quota (디스크 쿼터)",
        "LVM",
        "RAID",
        "Swap Partition"
      ],
      "answer": 1,
      "explanation": "디스크 쿼터(Quota)는 사용자/그룹의 디스크 블록 사용량 및 아이노드 생성 수를 제한하여 DoS를 방어합니다."
    },
    {
      "id": "IP1_Q21",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 침해사고 분석 시 살아있는(Live) 시스템의 휘발성 데이터(Volatile Data) 수집 시 보존 순서(Order of Volatility)에서 가장 먼저 수집해야 하는 것은?",
      "options": [
        "CPU 레지스터 및 캐시 메모리",
        "물리적 RAM 메모리",
        "네트워크 상태 정보",
        "하드디스크 파일 시스템"
      ],
      "answer": 1,
      "explanation": "휘발성 데이터 수집 순서는 레지스터/캐시 -> 라우팅테이블/ARP캐시/프로세스테이블 -> 물리 메모리(RAM) -> 임시 파일 -> 디스크 순입니다."
    },
    {
      "id": "IP1_Q22",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 유닉스 시스템에서 계정의 셸(Shell)이 '/bin/false' 또는 '/sbin/nologin'으로 설정되어 있는 계정의 보안적 의미는?",
      "options": [
        "시스템 대화형 로그인이 불가능한 서비스 전용 데몬 계정이다.",
        "최고 관리자 root 권한을 위임받은 계정이다.",
        "임시 비밀번호가 발급된 계정이다.",
        "SSH 원격 접속만 가능한 계정이다."
      ],
      "answer": 1,
      "explanation": "/sbin/nologin 및 /bin/false는 서비스 구동용 데몬 계정이 대화형 터미널 셸을 획득하지 못하도록 로그인 접근을 원천 차단하는 설정입니다."
    },
    {
      "id": "IP1_Q23",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 패킷 덤프 도구인 tcpdump에서 192.168.1.50 IP와 통신하는 모든 트래픽 중 포트가 80번이 아닌 트래픽만을 필터링하는 옵션 표현식은?",
      "options": [
        "tcpdump host 192.168.1.50 and not port 80",
        "tcpdump -i eth0 port 80",
        "tcpdump src 192.168.1.50 or port 80",
        "tcpdump dst 192.168.1.50"
      ],
      "answer": 1,
      "explanation": "BPF(Berkeley Packet Filter) 문법에 따라 'host 192.168.1.50 and not port 80'으로 조합합니다."
    },
    {
      "id": "IP1_Q24",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 데이터 무결성 검증을 위해 리눅스 환경에서 특정 파일(sample.tar.gz)의 SHA-256 해시값을 생성하고 검증하는 표준 명령어는?",
      "options": [
        "sha256sum sample.tar.gz",
        "md5sum -c",
        "hash -sha256",
        "cksum -a 256"
      ],
      "answer": 1,
      "explanation": "리눅스에서는 sha256sum, sha1sum, md5sum 명령어를 사용하여 표준 체크섬 해시를 계산 및 검증합니다."
    },
    {
      "id": "IP1_Q25",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "1회 실기 단답형 핵심 족보",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 족보",
      "question": "[단답형] 리눅스 파일 시스템에서 파일에 설정할 경우 소유자나 root라 할지라도 파일을 삭제, 수정, 이름 변경하거나 링크를 걸 수 없도록 잠그는 chattr 명령어의 불변(Immutable) 속성 플래그는?",
      "options": [
        "+i (Immutable)",
        "+a (Append only)",
        "+s (Secure deletion)",
        "+u (Undeletable)"
      ],
      "answer": 1,
      "explanation": "'chattr +i 파일명'을 적용하면 파일에 불변 속성이 부여되어 백도어 침투나 로그 삭제를 방지할 수 있습니다."
    },
    {
      "id": "IP2_Q1",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[로그 분석] 다음 아파치 access.log 기록을 분석하여 시도된 공격 유형을 식별하시오.\n\n192.168.10.15 - - [12/Nov/2026:14:22:01 +0900] \"GET /board/view.php?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users--%20 HTTP/1.1\" 200 4521\n192.168.10.15 - - [12/Nov/2026:14:22:05 +0900] \"GET /board/view.php?id=1%20UNION%20SELECT%201,table_name,3%20FROM%20information_schema.tables--%20 HTTP/1.1\" 200 8920",
      "options": [
        "Union-Based SQL Injection (SQL 인젝션)",
        "Cross-Site Scripting (XSS)",
        "Directory Traversal (경로 조작)",
        "Command Injection (명령어 삽입)"
      ],
      "answer": 1,
      "explanation": "id 파라미터에 UNION SELECT 구문과 information_schema 메타데이터를 결합하여 사용자 계정과 DB 스키마를 유출하는 전형적인 Union-Based SQL Injection 공격입니다."
    },
    {
      "id": "IP2_Q2",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[로그 분석] 다음 웹 서버 로그를 분석하여 공격자가 탈취하고자 한 파일과 시도된 공격 기법을 판단하시오.\n\n10.0.0.88 - - [12/Nov/2026:15:30:12 +0900] \"GET /download.jsp?file=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1\" 200 2410",
      "options": [
        "경로 조작(Path Traversal) 공격을 통한 리눅스 계정 파일(/etc/passwd) 열람",
        "파일 업로드를 통한 웹셸 실행",
        "SQL 인젝션을 통한 관리자 로그인 우회",
        "서버사이드 템플릿 인젝션(SSTI)"
      ],
      "answer": 1,
      "explanation": "%2e%2e%2f는 URL 디코딩 시 '../../'로 변환되며, 상위 디렉토리로 이동하여 시스템의 /etc/passwd 파일을 불법 열람하는 Path Traversal(디렉토리 순회) 공격입니다."
    },
    {
      "id": "IP2_Q3",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 3,
      "subject_name": "3영역: 시큐어코딩 진단",
      "question": "[시큐어코딩] 다음 취약한 자바 코드의 결함을 진단하고 가장 안전한 수정 코드로 올바른 것은?\n\n[취약한 코드]\nString sql = \"SELECT * FROM member WHERE id = '\" + userID + \"' AND pw = '\" + userPW + \"'\";\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(sql);",
      "options": [
        "PreparedStatement pstmt = conn.prepareStatement(\"SELECT * FROM member WHERE id = ? AND pw = ?\");\npstmt.setString(1, userID);\npstmt.setString(2, userPW);\nResultSet rs = pstmt.executeQuery();",
        "String sql = \"SELECT * FROM member WHERE id = '\" + userID.replace(\"'\", \"\") + \"'\";",
        "Statement stmt = conn.createStatement(ResultSet.TYPE_SCROLL_INSENSITIVE, ResultSet.CONCUR_READ_ONLY);",
        "String sql = URLDecoder.decode(userID, \"UTF-8\");"
      ],
      "answer": 1,
      "explanation": "문자열 결합 방식의 Statement는 SQL 인젝션에 취약하므로, 위치 홀더(?)를 사용하는 PreparedStatement 객체에 파라미터 바인딩(setString)을 수행해야 안전합니다."
    },
    {
      "id": "IP2_Q4",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[Snort 룰 분석] 다음 침입탐지 규칙이 탐지하고자 하는 악성 행위로 올바른 것은?\n\nalert tcp any any -> 192.168.1.100 80 (msg:\"WebShell Detection - cmd.jsp\"; content:\"cmd.jsp\"; nocase; content:\"cmd=\"; distance:0; sid:2000001;)",
      "options": [
        "웹 서버(80 포트)로 업로드된 jsp 웹셸(cmd.jsp)을 통한 시스템 명령어 실행 시도",
        "외부로의 데이터 대량 유출 시도",
        "DNS 증폭 반사 공격",
        "SSH 무차별 대입 공격"
      ],
      "answer": 1,
      "explanation": "URI나 요청에 cmd.jsp 웹셸 파일과 명령어 파라미터(cmd=)가 포함된 웹셸 악용 행위를 탐지하는 시그니처입니다."
    },
    {
      "id": "IP2_Q5",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[방화벽 설정] 내부 사설망(192.168.1.0/24)에서 인터넷 웹 서핑(80, 443 포트)만을 허용하고 그 외의 모든 아웃바운드 트래픽을 차단하는 iptables 규칙 세트로 올바른 것은?",
      "options": [
        "iptables -P FORWARD DROP\niptables -A FORWARD -s 192.168.1.0/24 -p tcp -m multiport --dports 80,443 -j ACCEPT\niptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT",
        "iptables -A INPUT -p tcp --dport 80 -j DROP",
        "iptables -P INPUT ACCEPT",
        "iptables -F OUTPUT"
      ],
      "answer": 1,
      "explanation": "기본 정책(Policy)을 DROP으로 설정한 후 80, 443 포트 허용 및 세션 응답(ESTABLISHED, RELATED)을 허용하는 상태추적 방화벽 구성이 정답입니다."
    },
    {
      "id": "IP2_Q6",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 3,
      "subject_name": "3영역: 시큐어코딩 진단",
      "question": "[시큐어코딩] 파일 업로드 취약점 방어를 위한 3대 안전수칙 중 확장자 검증 시 적용해야 할 올바른 정책은?",
      "options": [
        "화이트리스트(Whitelist) 방식으로 허용할 확장자(jpg, png, pdf 등)만 엄격히 허용",
        "블랙리스트 방식으로 jsp, php, asp 등만 금지",
        "확장자를 검사하지 않고 Content-Type만 신뢰",
        "클라이언트 측 자바스크립트로만 확장자 검사"
      ],
      "answer": 1,
      "explanation": "블랙리스트 방식은 우회(jspx, php5, phtml 등)가 쉬우므로, 허용된 안전한 확장자만을 허용하는 화이트리스트 검증을 서버사이드에서 수행해야 합니다."
    },
    {
      "id": "IP2_Q7",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[시스템 분석] 리눅스 시스템 침해사고 분석 중 /etc/passwd 파일에 다음과 같은 계정이 발견되었다. 이 계정의 보안 위험성을 가장 올바르게 지적한 것은?\n\nhacker:x:0:0:root:/root:/bin/bash",
      "options": [
        "UID가 0으로 설정되어 있어 root와 완전히 동일한 최고 관리자 권한을 가진 백도어 계정이다.",
        "일반 사용자 계정으로 아무런 위험이 없다.",
        "비밀번호가 x로 잠겨 있어 로그인이 불가능하다.",
        "홈 디렉토리가 잘못 설정된 단순 설정 오류이다."
      ],
      "answer": 1,
      "explanation": "UID가 0이면 계정 이름에 상관없이 리눅스 커널은 최고 관리자 root 권한으로 인식하므로 전형적인 슈퍼유저 권한 백도어 계정입니다."
    },
    {
      "id": "IP2_Q8",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[로그 분석] 리눅스 /var/log/secure 로그에서 다음과 같은 이력이 지속적으로 기록될 때 분석 내용으로 올바른 것은?\n\nFailed password for invalid user admin from 203.0.113.50 port 45211 ssh2\nFailed password for root from 203.0.113.50 port 45215 ssh2\nFailed password for test from 203.0.113.50 port 45220 ssh2",
      "options": [
        "외부 IP(203.0.113.50)로부터 SSH 계정 무차별 대입(Brute Force / Dictionary) 공격이 진행 중이다.",
        "정상적인 관리자의 일상 접속이다.",
        "웹 서버 서비스 거부 공격이다.",
        "ARP 스푸핑 공격이다."
      ],
      "answer": 1,
      "explanation": "동일 IP에서 다수의 관리자 및 기본 계정명으로 짧은 시간 동안 SSH 비밀번호 인증 실패가 반복되는 전형적인 SSH 사전 대입 공격 로그입니다."
    },
    {
      "id": "IP2_Q9",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 3,
      "subject_name": "3영역: 시큐어코딩 진단",
      "question": "[시큐어코딩] 게시판 본문 출력 시 공격자가 삽입한 `<script>alert(document.cookie);</script>` 스크립트의 실행을 방어하기 위해 JSTL에서 사용하는 안전한 태그 출력 방식은?",
      "options": [
        "<c:out value=\"${board.content}\" escapeXml=\"true\" />",
        "<c:out value=\"${board.content}\" escapeXml=\"false\" />",
        "<%= request.getParameter(\"content\") %>",
        "<jsp:getProperty name=\"board\" property=\"content\" />"
      ],
      "answer": 1,
      "explanation": "JSTL의 <c:out> 태그는 기본적으로 escapeXml=\"true\" 속성이 적용되어 HTML 특수문자를 자동 엔티티 인코딩하여 XSS를 방어합니다."
    },
    {
      "id": "IP2_Q10",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 4,
      "subject_name": "4영역: 서술형/관리",
      "question": "[서술형] 개인정보 안전성 확보조치 기준에 따라 개인정보취급자가 개인정보처리시스템에 접속하여 개인정보를 다운로드한 경우 취해야 할 사후 조치로 올바른 것은?",
      "options": [
        "다운로드 사유를 반드시 확인하고 기록·보관하여야 한다.",
        "다운로드 즉시 해당 개인정보를 원격 서버에서 삭제해야 한다.",
        "다운로드 내역은 별도 로그 없이 관리자 구두 승인만 받으면 된다.",
        "다운로드는 사유와 무관하게 전면 금지된다."
      ],
      "answer": 1,
      "explanation": "개인정보 다운로드 시에는 유출 사고를 방지하고 오남용을 추적하기 위해 다운로드 사유 확인 및 승인 절차를 수립하고 접속기록에 남겨야 합니다."
    },
    {
      "id": "IP2_Q11",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[서술형] 리눅스 시스템에서 취약점 점검 스크립트를 작성할 때, 주요 환경변수 및 시스템 설정 파일(/etc/passwd, /etc/shadow)의 적절한 소유자 및 권한 설정 기준으로 올바른 것은?",
      "options": [
        "/etc/passwd: root 소유, 644 이하 / /etc/shadow: root 소유, 400 또는 000",
        "/etc/passwd: 777 / /etc/shadow: 777",
        "/etc/passwd: 666 / /etc/shadow: 644",
        "/etc/passwd: 755 / /etc/shadow: 666"
      ],
      "answer": 1,
      "explanation": "kisa 주요기반시설 점검 가이드에 따라 /etc/passwd는 root 소유 644(-rw-r--r--), 패스워드 해시가 들어있는 /etc/shadow는 root 소유 400(-r--------) 이하로 제한해야 안전합니다."
    },
    {
      "id": "IP2_Q12",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 3,
      "subject_name": "3영역: 시큐어코딩 진단",
      "question": "[시큐어코딩] 무작위 난수 생성이 필요한 세션 ID, 비밀번호 재설정 토큰, 암호화 키 생성 시 취약한 'java.util.Random' 대신 사용해야 하는 암호학적으로 안전한 난수 생성 클래스는?",
      "options": [
        "java.security.SecureRandom",
        "Math.random()",
        "System.currentTimeMillis()",
        "UUID.randomUUID()"
      ],
      "answer": 1,
      "explanation": "SecureRandom은 예측 불가능한 엔트로피 시드를 사용하여 난수를 생성하므로 암호학적 토큰 및 키 생성에 필수적입니다."
    },
    {
      "id": "IP2_Q13",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[실무 설정] Nginx 웹 서버에서 클릭재킹(Clickjacking) 공격을 방지하기 위해 응답 헤더에 타 사이트의 프레임 삽입을 전면 차단하는 지시자 설정은?",
      "options": [
        "add_header X-Frame-Options DENY always;",
        "add_header X-Frame-Options ALLOW-FROM *;",
        "add_header X-XSS-Protection \"1; mode=block\";",
        "proxy_set_header Host $host;"
      ],
      "answer": 1,
      "explanation": "Nginx에서 'add_header X-Frame-Options DENY always;' 설정을 통해 어떠한 사이트에서도 해당 웹 페이지를 iframe 등에 로드할 수 없도록 강제합니다."
    },
    {
      "id": "IP2_Q14",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[포렌식 분석] 윈도우 프리페치(Prefetch, .pf) 파일이 수사관 및 포렌식 분석가에게 제공하는 가장 결정적인 정보는 무엇인가?",
      "options": [
        "응용 프로그램의 최근 실행 시간, 실행 횟수, 실행 시 로드된 참조 파일 목록",
        "사용자가 입력한 패스워드 평문",
        "삭제된 파일의 완전한 바이너리 원본",
        "네트워크 카드 MAC 주소"
      ],
      "answer": 1,
      "explanation": "윈도우 프리페치(C:\\Windows\\Prefetch)는 응용 프로그램의 최초 및 최근 실행 일시(최대 8회), 실행 횟수, 실행 파일 경로와 DLL 목록을 담고 있어 악성코드 실행 증적 확보에 핵심입니다."
    },
    {
      "id": "IP2_Q15",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[네트워크 분석] SYN Flooding 공격을 탐지하기 위해 netstat 명령어 실행 결과 특정 포트(80)에 비정상적으로 많이 쌓여 있는 TCP 연결 상태값은?",
      "options": [
        "SYN_RECEIVED (SYN_RECV)",
        "ESTABLISHED",
        "TIME_WAIT",
        "CLOSE_WAIT",
        "FIN_WAIT_1"
      ],
      "answer": 1,
      "explanation": "SYN 요청을 받고 SYN/ACK를 보낸 후 최종 ACK를 대기하는 반개방 상태가 지속될 때 SYN_RECV(SYN_RECEIVED) 상태의 소켓이 폭증합니다."
    },
    {
      "id": "IP2_Q16",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 3,
      "subject_name": "3영역: 시큐어코딩 진단",
      "question": "[시큐어코딩] 파일 다운로드 취약점을 방지하기 위해 파일 경로 처리 시 적용해야 할 시큐어코딩 기법으로 올바른 것은?",
      "options": [
        "사용자가 전달한 파일명에서 '..', '/', '\\' 등의 경로 조작 문자를 제거하고 베이스 디렉토리와 결합하여 검증",
        "사용자 입력 파라미터를 그대로 new File(param)에 전달",
        "GET 대신 POST 방식을 적용",
        "파일 크기를 10MB로 제한"
      ],
      "answer": 1,
      "explanation": "파일 다운로드 시 파라미터에서 상위 경로 탐색 문자(../)를 필터링하거나, File.getCanonicalPath()로 정규화된 경로가 허용된 다운로드 루트 디렉토리 내에 위치하는지 검증해야 합니다."
    },
    {
      "id": "IP2_Q17",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[시스템 점검] 리눅스 시스템에서 불필요하거나 취약한 원격 서비스 데몬 중 평문(Cleartext)으로 패스워드와 명령어를 전송하므로 비활성화해야 하는 서비스 3종의 조합은?",
      "options": [
        "Telnet, FTP, R-commands (rsh, rlogin)",
        "SSH, SFTP, HTTPS",
        "NTP, DNS, DHCP",
        "Syslog, Cron, Systemd"
      ],
      "answer": 1,
      "explanation": "Telnet, FTP, rlogin/rsh/rcp는 통신 구간 암호화가 없어 스니핑에 취약하므로 SSH, SFTP, SCP 등 보안 프로토콜로 대체해야 합니다."
    },
    {
      "id": "IP2_Q18",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[실무 서술] 침해사고 대응 절차(NIST SP 800-61) 4단계의 순서로 올바른 것은?",
      "options": [
        "준비(Preparation) -> 탐지 및 분석(Detection & Analysis) -> 봉쇄·제거 및 복구(Containment, Eradication & Recovery) -> 사후 활동(Post-Incident Activity)",
        "탐지 -> 복구 -> 준비 -> 제거",
        "분석 -> 준비 -> 봉쇄 -> 보고",
        "신고 -> 수사 -> 복구 -> 재개"
      ],
      "answer": 1,
      "explanation": "NIST 침해사고 대응 표준 4단계는 1. 준비 -> 2. 탐지 및 분석 -> 3. 봉쇄, 제거 및 복구 -> 4. 사후 검토 및 활동입니다."
    },
    {
      "id": "IP2_Q19",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 3,
      "subject_name": "3영역: 시큐어코딩 진단",
      "question": "[시큐어코딩] C/C++ 언어에서 버퍼 오버플로우를 유발하는 위험 함수와 이를 대체할 안전한 함수의 매칭으로 올바르지 않은 것은?",
      "options": [
        "strcpy -> strncpy (또는 strcpy_s)",
        "strcat -> strncat (또는 strcat_s)",
        "sprintf -> snprintf (또는 sprintf_s)",
        "gets -> fgets",
        "printf -> gets"
      ],
      "answer": 5,
      "explanation": "gets는 버퍼 크기를 검사하지 않아 가장 취약한 함수이며 버퍼 길이를 지정받는 fgets로 대체해야 합니다."
    },
    {
      "id": "IP2_Q20",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 4,
      "subject_name": "4영역: 서술형/관리",
      "question": "[서술형] 개인정보처리자가 개인정보의 처리를 제3자에게 위탁할 때 '위탁 계약서'에 법적으로 반드시 포함해야 하는 필수 문서화 항목이 아닌 것은?",
      "options": [
        "위탁업무 수행 목적 외 개인정보 처리 금지에 관한 사항",
        "개인정보의 기술적·관리적 보호조치에 관한 사항",
        "수탁사 직원의 주민등록번호 원본 목록",
        "위탁업무의 목적 및 범위",
        "재위탁 제한에 관한 사항 및 수탁사 관리·감독에 관한 사항"
      ],
      "answer": 3,
      "explanation": "개인정보보호법 제26조 위탁 계약 필수 사항은 ①위탁 목적/범위, ②목적외 처리 금지, ③보호조치, ④재위탁 제한, ⑤관리감독, ⑥손해배상 등입니다. 수탁사 직원 주민번호는 포함되지 않습니다."
    },
    {
      "id": "IP2_Q21",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[로그 분석] 윈도우 이벤트 뷰어(Event Viewer) 보안 로그에서 사용자 계정의 로그인 성공과 로그인 실패를 나타내는 이벤트 ID(Event ID)의 조합은?",
      "options": [
        "성공: 4624, 실패: 4625",
        "성공: 1000, 실패: 1001",
        "성공: 7036, 실패: 7037",
        "성공: 4672, 실패: 4673"
      ],
      "answer": 1,
      "explanation": "윈도우 보안 이벤트 로그에서 이벤트 ID 4624는 로그인 성공(An account was successfully logged on), 4625는 로그인 실패(An account failed to log on)입니다."
    },
    {
      "id": "IP2_Q22",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[실무 분석] 침해당한 리눅스 서버에서 숨겨진 프로세스를 찾기 위해 'ps -ef' 결과와 비교 검증해야 하는 커널 가상 파일 시스템 디렉토리는?",
      "options": [
        "/proc 디렉토리 내의 숫자(PID) 디렉토리",
        "/sys 디렉토리",
        "/dev 디렉토리",
        "/etc 디렉토리"
      ],
      "answer": 1,
      "explanation": "루트킷이 ps 명령어를 후킹해 은닉했더라도 커널 메모리를 반영하는 /proc/[PID] 디렉토리를 전수 검사하여 숨겨진 악성 프로세스를 식별할 수 있습니다."
    },
    {
      "id": "IP2_Q23",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 3,
      "subject_name": "3영역: 시큐어코딩 진단",
      "question": "[시큐어코딩] 비밀번호 암호화 저장 시 SHA-256과 같은 빠른 해시 함수를 단독으로 사용하는 것이 보안상 취약한 이유와 이에 대한 해결책은?",
      "options": [
        "GPU를 이용한 초당 수십억 번의 고속 대입(레인보우 테이블) 공격에 취약하므로, PBKDF2나 bcrypt, Argon2를 사용하여 솔트 추가 및 반복 연산(키 스트레칭)을 적용해야 한다.",
        "SHA-256은 복호화 키가 노출되기 쉬우므로 대칭키로 저장해야 한다.",
        "해시 함수는 길이가 짧으므로 평문으로 저장해야 한다.",
        "MD5로 변경해야 한다."
      ],
      "answer": 1,
      "explanation": "일반 암호학적 해시는 고속 계산에 최적화되어 있어 무차별 대입 공격에 취약합니다. 솔트(Salt)와 반복 연산을 강제하는 패스워드 전용 단방향 함수(bcrypt 등)를 써야 합니다."
    },
    {
      "id": "IP2_Q24",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 2,
      "subject_name": "2영역: 시스템/네트워크 실무",
      "question": "[실무 점검] 리눅스에서 패스워드 없이 root 권한으로 명령어를 실행할 수 있도록 오설정된 sudoers(/etc/sudoers) 설정의 예시는?",
      "options": [
        "user01 ALL=(ALL) NOPASSWD: ALL",
        "root ALL=(ALL) ALL",
        "%wheel ALL=(ALL) ALL",
        "Defaults requiretty"
      ],
      "answer": 1,
      "explanation": "'NOPASSWD: ALL' 설정은 해당 계정이 비밀번호 검증 없이 즉시 root 권한의 모든 명령을 실행할 수 있어 계정 탈취 시 즉각적인 시스템 완전 장악으로 이어집니다."
    },
    {
      "id": "IP2_Q25",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "2회 실기 서술·실무형 분석",
      "subject_id": 4,
      "subject_name": "4영역: 서술형/관리",
      "question": "[서술형] 개인정보보호위원회 고시 '개인정보의 안전성 확보조치 기준'에 따른 접속기록 점검 주기는 최소 얼마에 1회 이상인가?",
      "options": [
        "매월 1회 이상",
        "매주 1회 이상",
        "반기 1회 이상",
        "매년 1회 이상"
      ],
      "answer": 1,
      "explanation": "개인정보처리자는 개인정보처리시스템의 접속기록에 대해 월 1회 이상 정기적으로 불법 접근, 다운로드, 열람 등 이상 징후를 점검·확인하여야 합니다."
    },
    {
      "id": "IP3_Q1",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "Snort 룰 옵션 중 직전 매칭된 content 패턴의 끝 지점으로부터 다음 패턴을 탐색하기 시작할 상대적 시작 거리를 지정하는 옵션 키워드는 무엇인가?",
      "options": [
        "distance",
        "offset",
        "depth",
        "within",
        "nocase"
      ],
      "answer": 1,
      "explanation": "[정답: distance]\ndistance는 이전 content 매칭의 끝 지점부터 몇 바이트 떨어진 곳부터 다음 content 탐색을 시작할지(상대적 오프셋)를 지정하는 옵션입니다. 반면 within은 distance 지점부터 최대 몇 바이트 범위 내에서 찾을지를 지정합니다."
    },
    {
      "id": "IP3_Q2",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "리눅스 iptables에서 패킷을 차단할 때, 단순히 패킷을 버리고 송신자에게 아무런 응답을 주지 않는 DROP과 달리, 송신자에게 '연결 거부(ICMP Port Unreachable 또는 TCP RST)' 패킷을 회신하며 차단하는 타겟은 무엇인가?",
      "options": [
        "REJECT",
        "DENY",
        "DROP",
        "DISCARD",
        "LOG"
      ],
      "answer": 1,
      "explanation": "[정답: REJECT]\nREJECT 타겟은 접속을 차단하면서 클라이언트에게 즉시 ICMP unreachable 또는 TCP RST 응답을 돌려주어 클라이언트가 타임아웃까지 대기하지 않게 합니다. 반면 DROP은 패킷을 조용히 폐기합니다."
    },
    {
      "id": "IP3_Q3",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "리눅스 시스템에서 특정 파일이나 소켓, 네트워크 포트를 열고 있는 프로세스의 PID와 실행 계정 목록을 조회하는 침해사고 분석 명령어는 무엇인가?",
      "options": [
        "lsof (또는 fuser)",
        "netstat",
        "ps",
        "top",
        "strace"
      ],
      "answer": 1,
      "explanation": "[정답: lsof (또는 fuser)]\nlsof(List Open Files)는 시스템에서 활성화된 모든 파일 디스크립터(일반 파일, 디렉토리, 네트워크 소켓 등)와 이를 점유하고 있는 프로세스(PID) 정보를 출력하는 핵심 점검 도구입니다."
    },
    {
      "id": "IP3_Q4",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "리눅스 파일시스템에서 파일의 3대 타임스탬프(atime, mtime, ctime) 중 파일의 소유자, 권한(chmod), 속성 등 파일의 메타데이터(Inode 정보)가 변경된 시각을 나타내는 것은 무엇인가?",
      "options": [
        "ctime (Change Time)",
        "mtime (Modification Time)",
        "atime (Access Time)",
        "dtime (Deletion Time)",
        "btime (Birth Time)"
      ],
      "answer": 1,
      "explanation": "[정답: ctime]\nmtime은 파일의 실제 내용(데이터)이 수정된 시각이고, atime은 파일이 읽히거나 실행된 시각이며, ctime은 메타데이터(소유자, 권한 등 inode 속성)가 변경된 시각입니다."
    },
    {
      "id": "IP3_Q5",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "윈도우 Vista 이상 시스템의 보안 감사 이벤트 로그 중 관리자 권한을 가진 계정으로 특권(Privilege)이 할당되어 로그인했을 때 기록되는 이벤트 ID는 무엇인가?",
      "options": [
        "4672 (Special privileges assigned to new logon)",
        "4624",
        "4625",
        "4720",
        "1102"
      ],
      "answer": 1,
      "explanation": "[정답: 4672]\n4672 이벤트는 관리자(Administrator) 그룹에 속한 특권 계정이 로그인하여 시스템 관리 권한(SeDebugPrivilege 등)을 부여받았을 때 4624(일반 성공)와 함께 발생하는 감사 이벤트입니다."
    },
    {
      "id": "IP3_Q6",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "쿠키의 탈취 및 비인가 전송을 막기 위한 SameSite 속성값 중 타 사이트에서의 단순 링크 이동(GET 탐색) 시에는 쿠키를 전송하지만, 타 사이트의 POST 요청이나 이미지 임베딩 요청 등에서는 쿠키 전송을 차단하는 기본값은 무엇인가?",
      "options": [
        "Lax",
        "Strict",
        "None",
        "Secure",
        "HttpOnly"
      ],
      "answer": 1,
      "explanation": "[정답: Lax]\nSameSite=Strict는 타 사이트에서의 모든 요청에서 쿠키를 일절 배제하며, SameSite=Lax는 최상위 탐색(안전한 GET 링크 이동)을 제외한 모든 교차 출처 요청(POST 등)에서 쿠키 전송을 차단하여 CSRF를 방어합니다."
    },
    {
      "id": "IP3_Q7",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "시큐어코딩 가이드에서 SQL Injection 취약점을 제거하기 위해 MyBatis 등의 ORM 프레임워크 매퍼 XML 파일에서 동적 문자열 치환 기호인 ${param} 대신 반드시 사용해야 하는 파라미터 바인딩 표기는 무엇인가?",
      "options": [
        "#{param}",
        "${param}",
        "%{param}",
        ":param",
        "@{param}"
      ],
      "answer": 1,
      "explanation": "[정답: #{param}]\nMyBatis에서 ${param}은 파라미터 값을 따옴표 없이 그대로 쿼리 문자열에 합치므로 SQL 인젝션에 취약합니다. #{param}을 사용해야 PreparedStatement의 '?' 파라미터로 안전하게 바인딩됩니다."
    },
    {
      "id": "IP3_Q8",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "암호화 통신에서 송신자와 수신자의 장기 개인키가 사후에 유출되더라도 이전에 암호화되어 기록된 과거 세션 트래픽들이 복호화되지 않도록 보장하는 암호학적 특성은 무엇인가?",
      "options": [
        "완전 전방향 보안 (Forward Secrecy / PFS)",
        "상호 인증 (Mutual Authentication)",
        "부인 방지 (Non-Repudiation)",
        "충돌 저항성 (Collision Resistance)",
        "가용성 (Availability)"
      ],
      "answer": 1,
      "explanation": "[정답: 완전 전방향 보안 (PFS: Perfect Forward Secrecy)]\nEphemeral Diffie-Hellman(DHE, ECDHE)과 같이 세션마다 일회성 임시 키를 생성하고 폐기함으로써 장기 비밀키가 노출되어도 과거 트래픽의 복호화를 방지합니다."
    },
    {
      "id": "IP3_Q9",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "리눅스 bash 셸에서 이전 사용자가 입력했던 모든 명령어 히스토리가 기록되는 사용자 홈 디렉토리의 기본 파일명은 무엇인가?",
      "options": [
        ".bash_history",
        ".bashrc",
        ".bash_profile",
        "/var/log/history",
        ".history"
      ],
      "answer": 1,
      "explanation": "[정답: .bash_history]\n침해사고 분석 시 공격자가 터미널에서 수행한 행위를 확인하기 위해 사용자 홈 디렉토리 하위의 ~/.bash_history 파일을 우선 분석합니다."
    },
    {
      "id": "IP3_Q10",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "공개키 기반 구조(PKI)에서 인증서 상태를 확인하기 위해 CA가 주기적으로 발행하는 인증서 폐기 목록의 영문 약어는 무엇인가?",
      "options": [
        "CRL (Certificate Revocation List)",
        "OCSP",
        "CSR",
        "CA",
        "SCEP"
      ],
      "answer": 1,
      "explanation": "[정답: CRL (Certificate Revocation List)]\nCRL은 효력이 상실되거나 취소된 인증서들의 일련번호 목록을 CA가 전자서명하여 정기적으로 게시하는 공지 목록입니다."
    },
    {
      "id": "IP3_Q11",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "리눅스에서 바이너리 실행 파일 내부에 포함되어 있는 출력 가능한 ASCII 문자열들을 추출하여 악성코드의 C2 IP 주소나 문자열을 분석할 때 사용하는 명령어는 무엇인가?",
      "options": [
        "strings",
        "objdump",
        "readelf",
        "nm",
        "file"
      ],
      "answer": 1,
      "explanation": "[정답: strings]\nstrings 명령어는 실행 바이너리나 코어 덤프 파일에서 연속된 4글자 이상의 출력 가능한 텍스트 문자열을 추출하여 C2 도메인, IP, 오류 메시지 등을 신속히 파악할 수 있게 합니다."
    },
    {
      "id": "IP3_Q12",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "iptables 명령어에서 외부 인터페이스(eth0)로 들어오는 패킷 중 목적지 포트가 22번(SSH)인 TCP 패킷을 허용하는 규칙을 INPUT 체인의 맨 첫 번째(1번) 줄에 삽입하기 위한 옵션은 무엇인가?",
      "options": [
        "-I INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT",
        "-A INPUT -i eth0 -p tcp --dport 22 -j ACCEPT",
        "-D INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT",
        "-R INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT",
        "-N INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT"
      ],
      "answer": 1,
      "explanation": "[정답: -I (Insert)]\n-A(Append)는 체인의 맨 끝에 규칙을 추가하지만, -I(Insert)는 특정 행 번호(-I INPUT 1)에 규칙을 우선순위 최상단으로 삽입할 때 사용합니다."
    },
    {
      "id": "IP3_Q13",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "전자금융감독규정상 금융회사 및 전자금융업자가 정보보호 예산으로 편성해야 하는 최소 비율 기준(총 IT 예산 대비)으로 올바른 것은?",
      "options": [
        "총 IT 예산의 100분의 7 (7%) 이상",
        "총 IT 예산의 5% 이상",
        "총 IT 예산의 10% 이상",
        "총 IT 예산의 3% 이상",
        "총 예산의 1% 이상"
      ],
      "answer": 1,
      "explanation": "[정답: 7% 이상]\n전자금융감독규정 제8조에 따라 금융회사는 총 IT 인력의 5% 이상을 정보보호 전담인력으로 확보하고, 총 IT 예산의 7% 이상을 정보보호 예산으로 편성하도록 권고 및 규정하고 있습니다."
    },
    {
      "id": "IP3_Q14",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "개인정보 안전성 확보조치 기준에 따라 개인정보처리시스템에 관리자가 접속할 때 아이디와 비밀번호 외에 추가로 적용해야 하는 인증 방식은 무엇인가?",
      "options": [
        "안전한 다중인증 (2차 인증 / MFA: OTP, SMS, 보안토큰 등)",
        "IP 주소 화이트리스트 단독",
        "MAC 주소 필터링",
        "생체인증 단독",
        "인증서 비밀번호 단독"
      ],
      "answer": 1,
      "explanation": "[정답: 다중인증 (2차 인증 / Multi-Factor Authentication)]\n안전성 확보조치 기준에 따라 관리자 페이지 및 개인정보처리시스템에 외부 또는 내부에서 접속 시 패스워드 외에 OTP, 보안토큰 등 다중인증을 의무 적용해야 합니다."
    },
    {
      "id": "IP3_Q15",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "NIST SP 800-63B 디지털 신원 가이드라인에서 패스워드 정책에 대해 권고한 내용 중 기존 전통적 정책과 달라진 대표적인 변경점은 무엇인가?",
      "options": [
        "주기적인 강제 변경(90일 주기 등) 폐지 권고 및 유출된 패스워드 사전 대조 의무화",
        "패스워드 길이를 최소 6자리로 단축 권고",
        "특수문자 3종 이상 강제 조합 유지",
        "패스워드 힌트 필수 제공",
        "30일마다 패스워드 변경 의무화"
      ],
      "answer": 1,
      "explanation": "[정답: 주기적 강제 변경 폐지 및 유출 패스워드 사전 대조]\nNIST 가이드라인은 사용자가 패스워드를 억지로 변경하면서 패턴을 단순화하는 부작용을 막기 위해 주기적 강제 변경을 폐지하고, 최소 8자 이상(권장 12자 이상) 및 기유출 데이터베이스 대조를 권고합니다."
    },
    {
      "id": "IP3_Q16",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "사이버 킬체인(Cyber Kill Chain) 7단계 모델 중 공격자가 시스템 침투 후 내부 정찰 및 다른 시스템으로 권한을 확대해 나가는 횡적 이동(Lateral Movement)의 기반이 되는 단계는?",
      "options": [
        "Command & Control (명령제어) 및 Actions on Objectives",
        "Reconnaissance (정찰)",
        "Weaponization (무기화)",
        "Delivery (전달)",
        "Exploitation (취약점 공격)"
      ],
      "answer": 1,
      "explanation": "[정답: Command & Control (C2)]\n악성코드가 설치(Installation)된 후 C2 채널을 확립하여 공격자의 원격 명령을 수신하고, 이를 통해 내부 침투 심화 및 목적 달성(Actions on Objectives) 단계로 진입합니다."
    },
    {
      "id": "IP3_Q17",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "MITRE 사에서 실제 해커 조직의 사이버 공격 전술(Tactics)과 기술(Techniques), 그리고 공통 지식베이스를 체계화한 프레임워크의 명칭은 무엇인가?",
      "options": [
        "MITRE ATT&CK",
        "OWASP Top 10",
        "NIST CSF",
        "ISO 27001",
        "CIS Controls"
      ],
      "answer": 1,
      "explanation": "[정답: MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge)]\n공격자의 생애주기 전반에 걸친 세부 공격 기술을 매트릭스 형태로 분류하여 침해 탐지 및 모의훈련에 널리 활용되는 글로벌 프레임워크입니다."
    },
    {
      "id": "IP3_Q18",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "리눅스 시스템에서 관리자가 시스템의 감사 규칙(Audit Rules)을 설정하여 특정 시스템 콜이나 중요 파일(/etc/passwd 등)에 대한 접근 시도를 실시간 감사 로그에 기록하도록 통제하는 도구는?",
      "options": [
        "auditctl (또는 auditd)",
        "systemctl",
        "sysctl",
        "logrotate",
        "iptables"
      ],
      "answer": 1,
      "explanation": "[정답: auditctl]\nauditctl 명령어를 사용하여 리눅스 커널 감사 시스템(auditd)에 감시 규칙(-w /etc/passwd -p wa -k passwd_change)을 등록함으로써 주요 파일 변경을 실시간 감적 추적합니다."
    },
    {
      "id": "IP3_Q19",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "보안관제 센터(SOC)에서 이종 보안 솔루션의 경보를 자동 수집·분석하고, 플레이북(Playbook)에 따라 사전 정의된 대응 절차를 사람의 개입 없이 또는 최소한의 개입으로 자동 실행하는 기술은?",
      "options": [
        "SOAR (Security Orchestration, Automation and Response)",
        "SIEM",
        "EDR",
        "NDR",
        "XDR"
      ],
      "answer": 1,
      "explanation": "[정답: SOAR]\nSIEM이 로그 수집 및 상관분석에 초점을 맞춘다면, SOAR은 워크플로우 오케스트레이션과 플레이북 기반 자동화 대응을 결합하여 침해사고 대응 속도를 획기적으로 단축합니다."
    },
    {
      "id": "IP3_Q20",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "단말기(엔드포인트)에서 발생하는 프로세스 동작, 네트워크 연결, 파일 변경 등을 행위 기반으로 실시간 모니터링하고 악성 행위 탐지 시 즉시 프로세스를 격리하는 보안 기술은?",
      "options": [
        "EDR (Endpoint Detection and Response)",
        "기존 시그니처 백신(AV)",
        "EPP 단독",
        "방화벽",
        "DLP"
      ],
      "answer": 1,
      "explanation": "[정답: EDR]\nEDR은 엔드포인트의 모든 활동을 상세히 추적 및 기록하여 파일리스(Fileless) 공격, 랜섬웨어 및 알려지지 않은 제로데이 공격을 탐지하고 분석 및 대응 기능을 제공합니다."
    },
    {
      "id": "IP3_Q21",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "네트워크 장비의 포트 미러링(Port Mirroring) 기능 중 시스코(Cisco) 스위치에서 특정 포트나 VLAN의 송수신 패킷을 분석 장비가 연결된 다른 포트로 복제하여 전송하는 기능의 명칭은?",
      "options": [
        "SPAN (Switch Port Analyzer)",
        "RSPAN",
        "VTP",
        "CDP",
        "HSRP"
      ],
      "answer": 1,
      "explanation": "[정답: SPAN (Switch Port Analyzer)]\nSPAN은 로컬 스위치의 포트나 VLAN 트래픽을 IDS, 패킷 분석기(Wireshark)가 물려 있는 모니터링 포트로 그대로 복사(Mirroring)해 주는 기술입니다."
    },
    {
      "id": "IP3_Q22",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "윈도우 시스템에서 침해사고 조사 시 메모리 상주 프로세스나 드라이버 분석을 위해 커널 크래시 덤프나 라이브 RAM 메모리를 추출할 때 사용하는 대표적인 오픈소스 메모리 분석 프레임워크는?",
      "options": [
        "Volatility (볼라틸리티)",
        "Autopsy",
        "EnCase",
        "FTK Imager",
        "Wireshark"
      ],
      "answer": 1,
      "explanation": "[정답: Volatility]\nVolatility는 리눅스, 윈도우, 맥의 물리 RAM 덤프 이미지를 파싱하여 실행 중이던 프로세스 트리(pslist), 활성 네트워크 연결(netscan), 인젝트된 셸코드(malfind) 등을 정밀 분석하는 대표적 도구입니다."
    },
    {
      "id": "IP3_Q23",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "소프트웨어 공급망 공격(Supply Chain Attack)을 방어하기 위해 애플리케이션에 포함된 모든 오픈소스 라이브러리, 의존성, 버전 및 라이선스 목록을 기계 판독 가능한 표준 형식으로 기술한 명세서는?",
      "options": [
        "SBOM (Software Bill of Materials)",
        "CVE",
        "CWE",
        "CVSS",
        "SLA"
      ],
      "answer": 1,
      "explanation": "[정답: SBOM (Software Bill of Materials)]\nSBOM은 소프트웨어의 부품 명세서로, Log4j 사태와 같은 오픈소스 취약점 발생 시 해당 라이브러리를 사용 중인 자산을 즉시 식별하여 조치할 수 있게 합니다."
    },
    {
      "id": "IP3_Q24",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "개인정보 보호법상 개인정보취급자가 개인정보처리시스템에 접근한 접속기록에 반드시 포함되어야 하는 법정 필수 기록 항목 5가지에 해당하지 않는 것은?",
      "options": [
        "취급자의 신용등급",
        "계정(식별자)",
        "접속일시",
        "접속지 정보(IP 주소)",
        "수행한 업무(조회, 수정, 삭제 등) 및 정보주체 식별정보"
      ],
      "answer": 1,
      "explanation": "[정답: 취급자의 신용등급]\n안전성 확보조치 기준에 따른 필수 항목은 1) 계정(식별자), 2) 접속일시, 3) 접속자 IP 주소, 4) 수행한 업무내역(열람, 수정, 삭제, 출력 등), 5) 처리한 정보주체 식별정보입니다."
    },
    {
      "id": "IP3_Q25",
      "category": "infosec_practical",
      "exam": 3,
      "exam_name": "3회 실기 단답형 최신 기출 족보",
      "subject_id": 1,
      "subject_name": "실기 단답형",
      "question": "제로 트러스트(Zero Trust) 보안 아키텍처의 3대 핵심 기본 원칙 중 '내부 네트워크라 할지라도 결코 신뢰하지 않고 모든 접근을 엄격히 검증'하는 원칙을 나타내는 표어는?",
      "options": [
        "Never Trust, Always Verify (결코 신뢰하지 말고 항상 검증하라)",
        "Trust but Verify",
        "Security by Obscurity",
        "Fail-Safe",
        "Defense in Depth 단독"
      ],
      "answer": 1,
      "explanation": "[정답: Never Trust, Always Verify]\n경계선 보안 모델을 탈피하여 모든 사용자, 기기, 세션을 잠재적 위협으로 간주하고 세분화된 인증·인가 및 지속적 모니터링을 수행하는 제로 트러스트의 대원칙입니다."
    },
    {
      "id": "IP4_Q1",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[로그 분석] 다음 Apache 웹서버 access.log의 1개 라인을 보고 공격자가 시도한 웹 취약점 공격의 명칭과 공격 목적, 그리고 방어 대책을 기술하시오.\n\n로그: 192.168.10.55 - - [13/Nov/2026:14:22:01 +0900] \"GET /board/view.jsp?idx=10%20AND%20ASCII(SUBSTRING((SELECT%20user()%29,1,1)%29%3E100 HTTP/1.1\" 200 4520 \"-\" \"sqlmap/1.6#stable\"",
      "options": [
        "SQL Injection (Blind SQLi)",
        "XSS 공격",
        "CSRF 공격",
        "Path Traversal",
        "File Upload"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 공격 유형: Blind SQL Injection (참/거짓 조건 기반 불린 블라인드 인젝션)\n2. 공격 목적: SUBSTRING, ASCII 함수를 이용하여 DB 시스템의 현재 사용자명(user()) 1글자씩 바이트 단위로 참/거짓 응답을 대조해 데이터베이스 기밀 정보를 무차별 추출하려는 시도(User-Agent에 sqlmap 도구 흔적 존재).\n3. 방어 대책: SQL 쿼리 작성 시 파라미터가 쿼리 구조에 영향을 주지 않도록 PreparedStatement(파라미터화된 쿼리)를 필수로 적용하고, 정수형 파라미터(idx)는 Integer.parseInt() 등을 통해 숫자형 유효성 검증을 수행한다."
    },
    {
      "id": "IP4_Q2",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[Snort 룰 작성] 사내 네트워크(192.168.1.0/24)의 임의 호스트에서 외부 인터넷으로 TCP 통신을 시도할 때, 패킷 페이로드 내에 'eval(base64_decode' 문자열이 대소문자 구분 없이 포함되어 있는 악성 WebShell 트래픽을 탐지하여 alert을 발생시키는 Snort 룰을 작성하시오. (단, sid는 2000001, rev는 1로 설정)",
      "options": [
        "alert tcp 192.168.1.0/24 any -> any any (msg:\"WebShell Traffic Detected\"; content:\"eval(base64_decode\"; nocase; sid:2000001; rev:1;)",
        "drop tcp any any -> any any (content:\"eval\"; sid:2000001;)",
        "pass tcp 192.168.1.0/24 any -> any any (sid:2000001;)",
        "log ip any any -> any any (content:\"base64\"; sid:2000001;)",
        "alert udp any any -> any any (content:\"WebShell\"; sid:2000001;)"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\nalert tcp 192.168.1.0/24 any -> any any (msg:\"WebShell Traffic Detected\"; content:\"eval(base64_decode\"; nocase; sid:2000001; rev:1;)\n- 출발지 IP 대역: 192.168.1.0/24 any\n- 목적지 IP 대역: any any\n- content: 문자열 매칭\n- nocase: 대소문자 무시"
    },
    {
      "id": "IP4_Q3",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[방화벽 설정] 리눅스 iptables를 이용하여 사내 데이터베이스 서버(192.168.1.50)의 3306번(MySQL) 포트에 대해 오직 애플리케이션 웹서버(192.168.1.10)의 접속만 허용하고, 그 외의 모든 IP에서의 3306 포트 접속은 패킷을 조용히 버리도록(DROP) 정책을 구성하고자 한다. 올바른 2개의 iptables 명령어 조합은?",
      "options": [
        "1) iptables -A INPUT -p tcp -s 192.168.1.10 --dport 3306 -j ACCEPT\n2) iptables -A INPUT -p tcp --dport 3306 -j DROP",
        "1) iptables -A INPUT -p tcp --dport 3306 -j DROP\n2) iptables -A INPUT -p tcp -s 192.168.1.10 -j ACCEPT",
        "1) iptables -I INPUT -p tcp --dport 3306 -j REJECT",
        "1) iptables -F INPUT",
        "1) iptables -P INPUT ACCEPT"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\niptables는 순차적으로 룰을 평가하므로,\n1) iptables -A INPUT -p tcp -s 192.168.1.10 --dport 3306 -j ACCEPT (인가 웹서버 허용)\n2) iptables -A INPUT -p tcp --dport 3306 -j DROP (그 외 전면 차단)\n순서대로 등록해야 허용 룰이 먼저 적용된 후 차단 룰에 의해 나머지 접속이 방어됩니다."
    },
    {
      "id": "IP4_Q4",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[시큐어코딩 분석] 다음 Java 코드의 보안 취약점 유형과 이를 해결하기 위한 안전한 개선 코드를 기술하시오.\n\n취약 코드:\nString query = \"SELECT * FROM members WHERE user_id = '\" + id + \"' AND user_pw = '\" + pw + \"'\";\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(query);",
      "options": [
        "취약점: SQL Injection / 개선: PreparedStatement와 파라미터 인덱스(?) 바인딩 사용",
        "취약점: XSS / 개선: HTML 엔티티 인코딩",
        "취약점: CSRF / 개선: CSRF 토큰 발급",
        "취약점: Buffer Overflow / 개선: 문자열 길이 제한",
        "취약점: 암호화 미적용 / 개선: AES 암호화"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 취약점: SQL Injection (사용자 입력값이 쿼리 문자열에 동적으로 연결되어 쿼리 구조 변조 가능)\n2. 개선 코드:\nString query = \"SELECT * FROM members WHERE user_id = ? AND user_pw = ?\";\nPreparedStatement pstmt = conn.prepareStatement(query);\npstmt.setString(1, id);\npstmt.setString(2, pw);\nResultSet rs = pstmt.executeQuery();"
    },
    {
      "id": "IP4_Q5",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[시큐어코딩 분석] 다음 JSP 게시판 소스코드에서 발생하는 취약점과 안전한 방어 코드를 기술하시오.\n\n취약 코드:\n<% String content = request.getParameter(\"content\"); %>\n<div>내용: <%= content %></div>",
      "options": [
        "취약점: XSS (Cross-Site Scripting) / 개선: HTML 특수문자 치환 또는 JSTL <c:out escapeXml=\"true\"> 사용",
        "취약점: SQL Injection / 개선: PreparedStatement 사용",
        "취약점: 파일 다운로드 / 개선: getCanonicalPath 사용",
        "취약점: 세션 하이재킹 / 개선: SSL 적용",
        "취약점: 클릭재킹 / 개선: X-Frame-Options 설정"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 취약점: XSS (악의적인 자바스크립트 <script>alert(document.cookie)</script> 등이 브라우저에서 실행되어 세션 탈취 위험)\n2. 개선 코드: HTML 특수문자(&, <, >, \", ')를 HTML Entity(&amp;, &lt;, &gt;, &quot;, &#39;)로 변환하거나, JSTL 태그 라이브러리를 사용하여 <c:out value=\"${param.content}\" escapeXml=\"true\" />로 출력한다."
    },
    {
      "id": "IP4_Q6",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[로그 분석] 다음 Nginx access.log를 보고 침해사고 유형과 공격자가 탈취하려 한 시스템 자원을 파악하시오.\n\n로그: 203.0.113.19 - - [13/Nov/2026:15:40:12 +0900] \"GET /download.jsp?file=..%2F..%2F..%2Fetc%2Fshadow HTTP/1.1\" 403 162 \"-\" \"curl/7.88.1\"",
      "options": [
        "Path Traversal (디렉토리 경로 조작) / /etc/shadow (리눅스 시스템 패스워드 해시 파일)",
        "SQL Injection / DB 사용자 테이블",
        "Command Injection / 리눅스 셸",
        "XSS 공격 / 관리자 쿠키",
        "WebShell 업로드 / 악성 JSP 파일"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 침해 유형: Path Traversal (디렉토리 탐색 / 경로 조작 공격)\n2. 대상 자원: URL 인코딩된 '..%2F' (상위 디렉토리 이동 ../) 기법을 활용하여 웹 루트를 벗어나 시스템 최고 기밀인 /etc/shadow (계정 패스워드 해시 파일) 탈취를 시도함 (403 Forbidden으로 차단됨)."
    },
    {
      "id": "IP4_Q7",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[침해사고 대응] 리눅스 서버 침해 발생 시 포렌식 관점에서 휘발성 데이터를 수집하기 위해 반드시 지켜야 할 증거 수집 순서(Order of Volatility) 4단계를 기술하시오.",
      "options": [
        "1. 레지스터/캐시 -> 2. RAM 메모리 -> 3. 네트워크 활성 소켓 및 연결 상태 -> 4. 디스크 파일시스템 및 백업 미디어",
        "1. 하드디스크 백업 -> 2. RAM 메모리 -> 3. 시스템 재부팅 -> 4. 로그 분석",
        "1. 전원 차단 -> 2. 메모리 수집 -> 3. 네트워크 캡처 -> 4. 디스크 이미징",
        "1. 시스템 부팅 -> 2. 백신 검사 -> 3. 임시 파일 삭제 -> 4. 로그 백업",
        "1. 네트워크 케이블 분리 -> 2. 포맷 -> 3. 백업 복구 -> 4. 서비스 재개"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n증거의 휘발성이 높은 순서대로 수집해야 데이터 유실을 방지할 수 있습니다.\n1단계: CPU 레지스터 및 캐시 메모리\n2단계: 물리적 RAM 메모리 (메모리 덤프 확보)\n3단계: 네트워크 연결 상태(netstat, lsof) 및 실행 중인 프로세스(ps)\n4단계: 로컬 비휘발성 저장장치(디스크 이미지 원본 사본 및 타임라인 분석)"
    },
    {
      "id": "IP4_Q8",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[시큐어코딩] C 언어에서 strcpy, strcat, sprintf 등 경계값(Bound) 검사를 수행하지 않는 안전하지 않은 함수를 대체하여 버퍼 오버플로우를 예방하는 안전한 표준 대체 함수들을 기술하시오.",
      "options": [
        "strncpy, strncat, snprintf (크기 지정 함수)",
        "strcpy_fast, strcat_safe",
        "memcpy 단독",
        "gets, scanf",
        "printf, puts"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n버퍼 크기를 넘어서는 데이터 복사로 인한 스택 오버플로우를 막기 위해 대상 버퍼의 최대 길이를 명시하는 strncpy, strncat, snprintf 또는 윈도우 환경의 보안 강화 함수(strcpy_s, strcat_s, sprintf_s)를 사용해야 합니다."
    },
    {
      "id": "IP4_Q9",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[웹서버 보안 설정] Apache 웹서버(httpd.conf)에서 HTTP 요청 메서드 중 위험한 메서드(TRACE, DELETE, PUT 등)의 실행을 차단하고 오직 GET과 POST 메서드만 허용하기 위한 LimitExcept 설정 구문으로 올바른 것은?",
      "options": [
        "<Directory \"/var/www/html\">\n  <LimitExcept GET POST>\n    Require all denied\n  </LimitExcept>\n</Directory>",
        "<Limit GET POST> Allow from all </Limit>",
        "Options -Methods",
        "ServerSignature Off",
        "TraceEnable on"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n<LimitExcept GET POST>\n  Require all denied\n</LimitExcept>\nLimitExcept 지시자를 사용하여 GET과 POST를 제외한 모든 HTTP 메서드(TRACE: XST 공격 유발, PUT/DELETE: 임의 파일 조작)의 실행을 거부(denied) 처리합니다."
    },
    {
      "id": "IP4_Q10",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[네트워크 침해 분석] 스위칭 환경에서 공격자가 지속적으로 피해자 PC와 기본 게이트웨이(라우터)에 위조된 ARP 응답(Reply) 패킷을 브로드캐스팅하여 자신의 MAC 주소를 게이트웨이 MAC으로 변조시키는 공격의 명칭과 이를 정적으로 방어하는 명령어를 기술하시오.",
      "options": [
        "공격: ARP Spoofing / 방어: arp -s [IP] [정상MAC주소] (정적 ARP 테이블 등록)",
        "공격: IP Spoofing / 방어: route add",
        "공격: DNS Spoofing / 방어: nslookup",
        "공격: ICMP Redirect / 방어: ping -t",
        "공격: MAC Flooding / 방어: ifconfig down"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 공격 명칭: ARP Spoofing (ARP 캐시 포이즈닝)\n2. 방어 대책: 클라이언트 및 게이트웨이에서 'arp -s [게이트웨이IP] [정상MAC]' 명령어를 수행하여 ARP 테이블 엔트리를 동적(Dynamic)에서 정적(Static)으로 고정시키거나, 스위치에서 Dynamic ARP Inspection(DAI) 보안 기능을 활성화한다."
    },
    {
      "id": "IP4_Q11",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[로그 분석] 리눅스 /var/log/secure 로그에서 다음과 같은 로그가 수천 건 연속 발생했을 때의 공격 유형과 이를 자동으로 방어하기 위한 대표적인 오픈소스 도구는?\n\n로그: Failed password for invalid user admin from 198.51.100.22 port 48210 ssh2",
      "options": [
        "공격: SSH 무차별 대입 공격 (Brute Force / Dictionary Attack) / 방어 도구: fail2ban (또는 DenyHosts)",
        "공격: SYN Flooding / 방어: tcpdump",
        "공격: 버퍼 오버플로우 / 방어: gdb",
        "공격: SQL Injection / 방어: mod_security",
        "공격: 루트킷 침투 / 방어: tripwire"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 공격 유형: SSH 사전 무차별 대입 공격(Brute Force)\n2. 자동 방어 대책: fail2ban 도구를 설치하여 일정 시간 동안(예: 10분 내 5회 이상) 인증 실패 로그가 탐지되면 iptables 방화벽 규칙을 동적으로 생성하여 해당 공격자 IP를 일정 시간(1시간~영구) 자동 차단한다."
    },
    {
      "id": "IP4_Q12",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[시큐어코딩] Java 웹 애플리케이션에서 안전하지 않은 암호학적 난수 생성기를 사용하여 세션 토큰이나 비밀번호 초기화 토큰이 예측되는 취약점을 해결하기 위해 교체해야 하는 안전한 난수 클래스는?",
      "options": [
        "java.security.SecureRandom",
        "java.util.Random",
        "Math.random()",
        "System.currentTimeMillis()",
        "UUID.randomUUID() 단독"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\njava.util.Random이나 Math.random()은 선형 합동 생성기(LCG) 기반의 의사 난수로서 시드 값이 추정되면 다음 난수가 쉽게 예측됩니다. 보안에 민감한 키/토큰 생성 시에는 OS의 엔트로피 풀을 사용하는 암호학적으로 안전한 java.security.SecureRandom 클래스를 사용해야 합니다."
    },
    {
      "id": "IP4_Q13",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[포렌식 실무] 증거 수집 과정에서 디지털 증거의 획득, 이송, 보관, 분석, 법정 제출에 이르기까지 증거를 취급한 모든 담당자, 일시, 장소, 행위가 빈틈없이 문서화되어 증명되어야 한다는 법적 원칙은 무엇인가?",
      "options": [
        "연계보관성의 원칙 (Chain of Custody)",
        "무결성의 원칙",
        "재현성의 원칙",
        "정당성의 원칙",
        "신속성의 원칙"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n연계보관성의 원칙(Chain of Custody)은 디지털 증거가 최초 압수 시점부터 법정에 현출될 때까지 위조, 변조, 훼손되지 않았음을 입증하기 위해 증거 취급 이력을 연속적으로 기록하고 증명하는 절차적 원칙입니다."
    },
    {
      "id": "IP4_Q14",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[취약점 진단] 오픈 리다이렉트(Open Redirect) 취약점이 발생하는 원인과 이를 악용한 피싱 공격을 예방하기 위한 개발 보안 조치 방안을 기술하시오.",
      "options": [
        "원인: 사용자 입력 URL을 검증 없이 HTTP 302 리다이렉트 대상으로 사용할 때 발생 / 대책: 허용된 내부 도메인만 허용하는 화이트리스트 검증 적용",
        "원인: SQL 쿼리 파라미터 결합 / 대책: PreparedStatement 사용",
        "원인: 쿠키 플래그 미설정 / 대책: HttpOnly 적용",
        "원인: 포트 개방 / 대책: 포트 차단",
        "원인: 패스워드 미암호화 / 대책: 해시 적용"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 발생 원인: response.sendRedirect(url)과 같이 외부 사용자가 전달한 임의의 URL 파라미터로 무조건 이동시킬 때 발생.\n2. 방어 대책: 이동 가능한 URL을 사전에 정의된 도메인(예: 사내 도메인만 허용)으로 한정하는 엄격한 화이트리스트 검증을 적용하거나, 상대 경로(/index.do)로의 이동만 허용한다."
    },
    {
      "id": "IP4_Q15",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[시스템 무결성 점검] 리눅스 환경에서 주요 시스템 바이너리(ls, ps, netstat 등) 및 설정 파일의 해시값(SHA-256)을 사전에 DB로 구축해 두고, 주기적으로 파일 변경 여부를 감시하여 트로이목마 및 루트킷 변조를 탐지하는 호스트 무결성 점검 오픈소스 도구는?",
      "options": [
        "Tripwire (또는 AIDE)",
        "Wireshark",
        "Nmap",
        "John the Ripper",
        "Hydra"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\nTripwire(또는 AIDE)는 무결성 기준 데이터베이스(Baseline DB)를 생성한 후, 파일 크기, 해시값, 권한, 수정 시각 등을 정기적으로 비교하여 악성코드에 의한 파일 변조를 즉시 식별하는 HIDS 도구입니다."
    },
    {
      "id": "IP4_Q16",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[웹 보안 설정] HTTP Strict Transport Security(HSTS) 헤더를 웹서버 응답에 적용할 때 브라우저가 최소 1년(31536000초) 동안 모든 하위 도메인을 포함하여 HTTPS 접속만을 강제하도록 설정하는 헤더 지시문 전체를 작성하시오.",
      "options": [
        "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
        "X-Frame-Options: DENY",
        "Content-Security-Policy: default-src https:",
        "Cache-Control: no-store",
        "Access-Control-Allow-Origin: *"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\nStrict-Transport-Security: max-age=31536000; includeSubDomains; preload\n- max-age=31536000: 1년(초 단위)\n- includeSubDomains: 모든 서브도메인에도 동일 강제 적용\n- preload: 브라우저 내장 HSTS 프리로드 목록 등록 지원"
    },
    {
      "id": "IP4_Q17",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[DDoS 방어] DNS 증폭 디도스(DNS Amplification DDoS) 공격을 무력화하기 위해 사내 공인 DNS 서버에서 외부 임의 사용자의 재귀 질의(Recursion)를 차단하는 BIND 설정 파일(named.conf)의 지시자는 무엇인가?",
      "options": [
        "recursion no; (또는 allow-recursion { none; };)",
        "listen-on port 53 { any; };",
        "zone \".\" IN { type hint; };",
        "directory \"/var/named\";",
        "dnssec-enable no;"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n사내 도메인의 권한(Authoritative) DNS 서버는 외부 인터넷 사용자에 대해 재귀적 질의를 수행할 필요가 없습니다. named.conf의 options 블록에 'recursion no;' 또는 'allow-recursion { trusted_network; };'를 설정하여 Open Resolver 악용을 차단합니다."
    },
    {
      "id": "IP4_Q18",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[개인정보 기술적 보호조치] 고유식별정보(주민등록번호 등)를 저장할 때 암호화 적용 대상 저장소 3가지와 적용해야 하는 안전한 암호화 알고리즘 요건을 기술하시오.",
      "options": [
        "저장소: 데이터베이스, 로그/백업 파일, PC/단말기 파일 / 알고리즘: 안전한 대칭키 암호화(AES-256, ARIA-256 등)",
        "저장소: RAM 메모리만 대상 / 알고리즘: MD5",
        "저장소: 웹 브라우저 캐시 / 알고리즘: Base64",
        "저장소: DNS 레코드 / 알고리즘: DES",
        "저장소: 네트워크 스위치 / 알고리즘: RC4"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 암호화 대상 저장소: 데이터베이스(DB), 업무용 PC(하드디스크), 모바일 단말기, 보조저장매체(백업 테이프, USB), 로그 파일 등.\n2. 암호화 요건: 국가 표준 또는 국제적으로 공인된 안전한 양방향 대칭 암호화 알고리즘(AES, ARIA, SEED 등 128비트 이상, 권장 256비트)을 적용해야 한다."
    },
    {
      "id": "IP4_Q19",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[네트워크 모니터링] tcpdump 도구를 사용하여 eth0 인터페이스에서 IP가 192.168.1.100이고 TCP 80번 포트로 오가는 패킷 중 SYN 플래그만 설정되어 있는 패킷을 캡처하기 위한 필터링 표현식은?",
      "options": [
        "tcpdump -i eth0 'host 192.168.1.100 and tcp port 80 and tcp[tcpflags] & tcp-syn != 0'",
        "tcpdump -i eth0 port 80",
        "tcpdump -w dump.pcap",
        "tcpdump -i eth0 ip",
        "tcpdump -X host 192.168.1.100"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\ntcpdump -i eth0 'host 192.168.1.100 and tcp port 80 and (tcp[tcpflags] & tcp-syn != 0)'\nTCP 헤더 13번째 바이트의 플래그 비트 중 SYN 비트를 비트마스킹(&)하여 SYN Flooding 패킷을 정밀하게 추출합니다."
    },
    {
      "id": "IP4_Q20",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[SW 개발보안] 비밀번호를 단방향 해시 암호화할 때 레인보우 테이블 공격을 방어하기 위해 사용하는 솔트(Salt)의 올바른 생성 및 관리 방식으로 가장 적절한 것은?",
      "options": [
        "사용자마다 암호학적으로 안전한 난수 생성기로 최소 16바이트 이상의 고유한 솔트를 생성하여 해시값과 함께 DB에 저장한다.",
        "모든 사용자에 대해 사내 고정 문자열 1개를 솔트로 공통 적용한다.",
        "솔트 값을 암호화하여 별도 서버에 숨긴다.",
        "솔트로 사용자의 아이디를 그대로 사용한다.",
        "솔트 길이를 1바이트로 고정한다."
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n솔트는 사용자마다 고유하고 예측 불가능한 난수(SecureRandom, 최소 16바이트 이상)로 생성되어야 동일한 패스워드를 가진 사용자들의 해시값이 서로 달라지며, 레인보우 테이블 공격이 원천 무력화됩니다. 솔트는 공개되어도 안전하므로 해시값과 함께 평문으로 저장됩니다."
    },
    {
      "id": "IP4_Q21",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[침해사고 분석] 리눅스 시스템에서 공격자가 /tmp 디렉토리에 백도어 셸 스크립트를 숨겨두고 삭제한 상태에서 여전히 프로세스가 백그라운드로 실행 중일 때, /proc 가상 파일시스템을 통해 삭제된 바이너리를 복구하는 명령어는?",
      "options": [
        "cp /proc/[PID]/exe /tmp/recovered_malware",
        "ls -l /proc",
        "cat /proc/cpuinfo",
        "rm -rf /proc/[PID]",
        "kill -9 [PID]"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n공격자가 파일시스템에서 원본 파일을 unlink(rm)하여 삭제했더라도 프로세스가 메모리에서 실행 중인 동안에는 /proc/[PID]/exe 심볼릭 링크가 해당 실행 파일의 메모리 이미지를 가리키므로, 이를 복사하여 악성코드 원본 바이너리를 완벽히 복구할 수 있습니다."
    },
    {
      "id": "IP4_Q22",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[ISMS-P 결함판정] 심사원이 고객 상담 시스템을 점검하던 중, 상담원이 정보주체의 주민등록번호 전체(13자리)를 입력하여 조회한 화면에서 주민등록번호 전체가 마스킹 없이 그대로 표출되고 있는 사실을 확인하였다. ISMS-P 인증기준 중 위반된 기준과 올바른 개선 방안은?",
      "options": [
        "위반 기준: 2.7.2(암호화 적용) 또는 3.2.3(개인정보 표시제한) / 개선: 생년월일 또는 성별 뒤 6자리를 마스킹(***) 처리",
        "위반 기준: 1.1.1(경영진 참여)",
        "위반 기준: 2.4.1(출입통제)",
        "위반 기준: 3.4.1(개인정보 파기)",
        "결함 없음 (업무상 조회가 필요하므로 정당함)"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 위반 기준: 2.7.2(암호화 적용) 및 3.2.3(개인정보 표시제한/마스킹)\n2. 개선 대책: 개인정보 처리화면에서 주민등록번호, 계좌번호 등 고유식별정보를 표출할 때에는 업무상 필수적인 경우를 제외하고는 마스킹(생년월일 6자리 제외 뒷자리 *** 처리)하여 표출하고, 마스킹 해제 시에는 사유 입력 및 책임자 승인 이력을 기록해야 한다."
    },
    {
      "id": "IP4_Q23",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[시스템 보안 점검] 리눅스 시스템에서 일반 계정(UID 1000 이상) 중 패스워드가 설정되어 있지 않아 패스워드 없이 로그인이 가능한 취약 계정을 /etc/shadow 파일에서 점검하는 명령어와 그 원리는?",
      "options": [
        "awk -F: '($2 == \"\" || $2 == \"!\") {print $1}' /etc/shadow",
        "cat /etc/passwd",
        "useradd -m test",
        "chmod 777 /etc/shadow",
        "ls -l /etc/shadow"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n/etc/shadow 파일의 두 번째 필드는 암호화된 비밀번호입니다. 이 필드가 비어 있거나(\"\") 널 값인 경우 비밀번호 입력 없이 로그인이 가능하므로, awk나 getent 명령어로 두 번째 필드가 빈 계정을 전수 식별하여 계정 잠금(passwd -l) 또는 비밀번호 설정을 강제해야 합니다."
    },
    {
      "id": "IP4_Q24",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[취약점 분석] 웹 애플리케이션에서 파라미터로 명령어를 전달받아 실행하는 시스템 명령 실행(Command Injection) 취약점을 방지하기 위한 소프트웨어 개발 보안 방안 2가지를 기술하시오.",
      "options": [
        "1) Runtime.getRuntime().exec() 등의 외부 셸 직접 호출 지양 및 언어 내장 API 사용\n2) 불가피한 경우 화이트리스트 기반 특수문자(&, |, ;, `, $) 엄격 제거",
        "1) 쿼리 문자열 암호화\n2) SSL 적용",
        "1) 포트 변경\n2) 쿠키 세션 타임아웃 단축",
        "1) 패스워드 복잡도 강화\n2) OTP 적용",
        "1) 방화벽 룰 추가\n2) DNSSEC 적용"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 시스템 셸 명령어(exec, system)를 직접 호출하는 방식 대신 언어 자체에서 제공하는 안전한 라이브러리 API(예: 파일 복사는 FileCopy API)를 사용한다.\n2. 셸 호출이 불가피한 경우 세미콜론(;), 파이프(|), 백틱(`), 앰퍼샌드(&) 등 명령어 체이닝 문자를 철저히 필터링하고 화이트리스트 명령 인자만 허용한다."
    },
    {
      "id": "IP4_Q25",
      "category": "infosec_practical",
      "exam": 4,
      "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
      "subject_id": 2,
      "subject_name": "실기 서술·실무",
      "question": "[클라우드 보안] AWS, 애저 등 퍼블릭 클라우드 환경에서 IAM(Identity and Access Management) 사용 시 최소 권한의 원칙(Principle of Least Privilege)을 준수하기 위한 3대 핵심 보안 수칙을 기술하시오.",
      "options": [
        "1) 루트(Root) 계정의 일상적 사용 금지 및 MFA 필수 적용\n2) 개별 사용자별 IAM 계정 발급 및 역할(Role) 기반 임시 자격증명 활용\n3) 과도한 와일드카드(*) 권한 부여 금지 및 세분화된 최소 정책 적용",
        "1) 모든 권한을 AdministratorAccess로 통일\n2) 루트 계정 액세스 키를 깃허브에 공유\n3) MFA 해제",
        "1) 패스워드 없이 로그인 허용\n2) 모든 S3 버킷 Public 개방\n3) VPC 제거",
        "1) 로그 기능(CloudTrail) 비활성화로 성능 향상\n2) 보안그룹 0.0.0.0/0 허용",
        "1) 암호키 자동 로테이션 차단"
      ],
      "answer": 1,
      "explanation": "[실무 모범답안]\n1. 최상위 루트 계정은 일상 업무에 사용하지 않고 잠금 및 강력한 하드웨어 MFA를 적용한다.\n2. 장기 액세스 키(Access Key) 대신 임시 자격증명을 제공하는 IAM Role(역할)을 사용한다.\n3. 와일드카드(Action: \"*\") 권한을 금지하고 실제 수행할 작업에만 국한된 최소 권한 정책(Least Privilege Policy)을 부여한다."
    }
  ],
  "summaries": [
    {
      "id": "prac_content_01",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "리눅스 침해사고 분석 및 점검 필수 명령어 10선",
      "badge": "실기 단답·실무",
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
    },
    {
      "id": "prac_content_02",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "서버 및 네트워크 주요 보안 설정 파라미터 족보",
      "badge": "실기 단답·실무",
      "points": [
        "<code>umask 027</code>: 파일 생성 기본 권한 640(-rw-r-----), 디렉토리 750(drwxr-x---) 강제 설정.",
        "<code>/etc/ssh/sshd_config</code>: <code>PermitRootLogin no</code> (root 직접 접속 차단), <code>PasswordAuthentication no</code> (공개키 인증 강제).",
        "<code>httpd.conf (Apache)</code>: <code>Options -Indexes</code> (디렉토리 리스팅 제거), <code>ServerTokens Prod</code> (상세 버전 은닉).",
        "<code>nginx.conf (Nginx)</code>: <code>server_tokens off;</code>, <code>add_header X-Frame-Options DENY;</code> (클릭재킹 방지).",
        "<code>/etc/hosts.allow & hosts.deny</code>: TCP Wrapper 접근 제어. allow 파일이 우선 적용된 후 deny 파일 적용.",
        "<code>/etc/login.defs</code>: <code>PASS_MAX_DAYS 90</code>, <code>PASS_MIN_DAYS 1</code>, <code>PASS_WARN_AGE 7</code> 패스워드 만료 주기.",
        "<code>/etc/sudoers</code>: 특정 계정에 패스워드 없이 root 권한을 부여하는 취약 설정(NOPASSWD: ALL) 점검 및 제거."
      ]
    },
    {
      "id": "prac_content_03",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "웹 침해사고 로그 분석(SQLi·Path Traversal) 및 Snort 룰 작성",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>Union-Based SQLi 로그:</strong> <code>GET /view.php?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users--%20 HTTP/1.1</code> -> 공백 인코딩(%20), UNION SELECT 키워드, information_schema 조회 식별.",
        "<strong>Path Traversal 로그:</strong> <code>GET /down.jsp?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1</code> -> %2e%2e%2f(상위 경로 ../) 디코딩 및 시스템 기밀 파일(/etc/passwd) 탈취 패턴 분석.",
        "<strong>WebShell 업로드 탐지 Snort 룰 작성 표준:</strong>",
        "<code>alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell JSP Upload\"; content:\"multipart/form-data\"; content:\".jsp\"; nocase; sid:1000001;)</code>",
        "<code>alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell Execution - cmd.jsp\"; content:\"cmd.jsp\"; nocase; content:\"cmd=\"; distance:0; sid:1000002;)</code>"
      ]
    },
    {
      "id": "prac_content_04",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "SW 개발보안(시큐어코딩) 47개 보안약점 핵심 가이드",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>1. SQL Injection:</strong> 반드시 파라미터 바인딩을 지원하는 PreparedStatement 사용. (취약: <code>Statement.executeQuery(\"...'\" + id + \"'\")</code>).",
        "<strong>2. XSS (크로스사이트 스크립팅):</strong> HTML Entity 치환(&lt;, &gt;, &amp;, &quot;) 라이브러리 사용 및 JSTL <code>&lt;c:out escapeXml=\"true\"&gt;</code> 적용.",
        "<strong>3. 파일 업로드 보안 3대 수칙:</strong> 화이트리스트 확장자 검증, UUID 파일명 난수화 변경 저장, 업로드 디렉토리 실행 권한(No-Exec) 박탈.",
        "<strong>4. 파일 다운로드 보안:</strong> 경로 조작 문자('../') 제거 및 <code>getCanonicalPath()</code>로 다운로드 루트 범위 검증.",
        "<strong>5. 취약한 난수 생성:</strong> 예측 가능한 <code>java.util.Random</code> 대신 암호학적으로 안전한 <code>java.security.SecureRandom</code> 클래스 사용.",
        "<strong>6. 패스워드 암호화 저장:</strong> 고속 해시(MD5/SHA) 단독 사용 금지, <code>PBKDF2 / bcrypt / Argon2</code> 기반 솔트 및 키 스트레칭 필수 적용."
      ]
    },
    {
      "id": "prac_content_05",
      "type": "content",
      "category": "law",
      "category_name": "디지털 포렌식 & 법률",
      "title": "디지털 포렌식 5대 원칙 및 휘발성 데이터 수집 순서",
      "badge": "실기 서술·실무",
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
    },
    {
      "id": "prac_content_06",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "리눅스 iptables 방화벽 패킷 필터링 문법 및 체인 구조",
      "badge": "실기 단답·실무",
      "points": [
        "<strong>3대 기본 테이블:</strong> filter (기본 패킷 필터링), nat (IP/포트 주소 변환), mangle (특수 패킷 변조).",
        "<strong>filter 테이블 3대 기본 체인:</strong> <code>INPUT</code> (로컬 호스트로 들어오는 패킷), <code>FORWARD</code> (호스트를 통과하는 패킷), <code>OUTPUT</code> (로컬에서 나가는 패킷).",
        "<strong>핵심 옵션:</strong> <code>-A</code> (체인 끝에 추가), <code>-I</code> (지정 위치에 삽입), <code>-D</code> (규칙 삭제), <code>-p</code> (프로토콜), <code>-s</code> (출발지 IP), <code>-d</code> (목적지 IP), <code>--sport/--dport</code> (포트), <code>-j</code> (타겟 동작).",
        "<strong>주요 타겟(-j):</strong> <code>ACCEPT</code> (허용), <code>DROP</code> (무응답 폐기), <code>REJECT</code> (거부 메시지 회신 후 폐기), <code>LOG</code> (syslog에 기록 후 다음 룰 진행)."
      ]
    },
    {
      "id": "prac_content_07",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "윈도우 보안 감사 정책 및 핵심 이벤트 ID 총람",
      "badge": "실기 단답형",
      "points": [
        "<code>4624</code>: 계정 로그온 성공 (Logon Type: 2-대화형 콘솔, 3-네트워크 공유, 10-원격데스크톱 RDP).",
        "<code>4625</code>: 계정 로그온 실패 (무차별 대입 공격 및 패스워드 스프레이 탐지).",
        "<code>4672</code>: 관리자 특권(Special Privileges)이 새 세션에 할당됨.",
        "<code>4720</code>: 새 사용자 계정이 생성됨 (침해 후 지속성 계정 생성 감시).",
        "<code>4726</code>: 사용자 계정이 삭제됨.",
        "<code>1102</code>: 윈도우 보안 감사 로그가 지워짐(Clear Log) - 침해사고 강력한 은폐 지표."
      ]
    },
    {
      "id": "prac_content_08",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "L4 DoS 공격 유형별 패킷 패턴 분석 및 대응책",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>SYN Flooding:</strong> 미완결 TCP 3-Way Handshake로 Backlog 큐 고갈 -> SYN Cookie 활성화(<code>sysctl -w net.ipv4.tcp_syncookies=1</code>).",
        "<strong>Land Attack:</strong> 출발지 IP/Port와 목적지 IP/Port가 동일 -> 출발지와 목적지가 동일한 패킷 즉시 차단 룰 적용.",
        "<strong>Smurf Attack:</strong> 피해자 IP로 위조된 ICMP Echo Request를 서브넷 브로드캐스트로 전송 -> 라우터에서 Directed Broadcast 차단(<code>no ip directed-broadcast</code>).",
        "<strong>TearDrop:</strong> IP Fragment Offset 중첩 조작 -> 최신 OS 패치 및 방화벽에서 단편화 패킷 재조합 검증."
      ]
    },
    {
      "id": "prac_content_09",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "웹 브라우저 보안 헤더(HSTS, CSP, X-Frame-Options) 완벽 설정",
      "badge": "실기 실무",
      "points": [
        "<strong>HSTS (Strict-Transport-Security):</strong> <code>Strict-Transport-Security: max-age=31536000; includeSubDomains; preload</code> -> 1년간 무조건 HTTPS 강제.",
        "<strong>CSP (Content-Security-Policy):</strong> <code>default-src 'self'; script-src 'self' https://trusted.cdn.com; object-src 'none';</code> -> 비인가 스크립트 실행 차단.",
        "<strong>X-Frame-Options:</strong> <code>DENY</code> (어디서도 frame 불가) 또는 <code>SAMEORIGIN</code> -> 클릭재킹 UI Redressing 방어.",
        "<strong>X-Content-Type-Options:</strong> <code>nosniff</code> -> MIME 타입 스니핑 방지.",
        "<strong>Referrer-Policy:</strong> <code>strict-origin-when-cross-origin</code> -> 민감한 URL 쿼리 파라미터 외부 유출 방지."
      ]
    },
    {
      "id": "prac_content_10",
      "type": "content",
      "category": "law",
      "category_name": "디지털 포렌식 & 법률",
      "title": "개인정보 안전성 확보조치 접속기록 점검 및 이상징후 기준",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>접속기록 법정 항목 5가지:</strong> 1) 사용자 계정, 2) 접속일시, 3) 접속자 IP 주소, 4) 수행 업무(열람·수정·삭제 등), 5) 정보주체 식별정보.",
        "<strong>보관 기간:</strong> 기본 최소 1년 이상 (5만 명 이상 또는 고유식별정보·민감정보 처리 시 최소 2년 이상).",
        "<strong>월 1회 점검 필수 이상징후 시나리오:</strong>",
        "- 단시간 내 대량 개인정보 다운로드 또는 조회 (임계치 초과)",
        "- 근무 시간 외(심야·휴일) 비정상 원격 접속 및 데이터 열람",
        "- 관리자 계정의 비인가 접속지(해외 IP, 공용망)에서의 로그인 시도",
        "- 퇴직자 계정이나 장기 미사용 계정의 활성화 및 데이터 접근"
      ]
    },
    {
      "id": "prac_content_11",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "WebShell 업로드 방어 및 업로드 디렉토리 실행권한 제거",
      "badge": "실기 실무",
      "points": [
        "<strong>웹서버 실행권한 박탈:</strong> Apache 가상호스트 디렉토리 설정에서 <code>php_admin_flag engine off</code> (PHP 실행 중지) 또는 <code>Options -ExecCGI</code> 적용.",
        "<strong>Nginx 설정:</strong> <code>location ~* ^/upload/.*\\.(php|jsp|asp|sh)$ { deny all; }</code> 구문으로 업로드 경로 내 스크립트 직접 호출 전면 차단.",
        "<strong>저장소 분리:</strong> 웹 루트 디렉토리 외부(NAS 또는 S3 객체 스토리지)에 저장하고 파일명을 UUID 난수로 변경 저장."
      ]
    },
    {
      "id": "prac_content_12",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "리눅스 PAM 패스워드 복잡도 및 임계치 잠금 설정 족보",
      "badge": "실기 단답형",
      "points": [
        "<code>pam_pwquality.so</code>: <code>minlen=8 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1</code> -> 최소 8자, 숫자/대문자/소문자/특수문자 각 1자 이상 강제.",
        "<code>pam_faillock.so (또는 pam_tally2)</code>: <code>deny=5 unlock_time=600 even_deny_root</code> -> 5회 연속 인증 실패 시 계정 10분간(600초) 잠금.",
        "<strong>잠금 확인 및 해제:</strong> <code>faillock --user [계정]</code> 확인, <code>faillock --user [계정] --reset</code> 잠금 해제."
      ]
    },
    {
      "id": "prac_content_13",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "DNS 캐시 포이즈닝 원리와 DNSSEC 서명 레코드 족보",
      "badge": "실기 단답·실무",
      "points": [
        "<strong>공격 원리:</strong> 비권한 캐시 DNS 서버에 질의를 보낸 후 권한 서버 응답 전에 무작위 Transaction ID(16비트)와 소스 포트를 대량 스푸핑 전송하여 조작된 IP를 캐싱시킴.",
        "<strong>DNSSEC 4대 핵심 레코드:</strong>",
        "- <code>RRSIG</code>: DNS 리소스 레코드 세트(RRset)에 대한 암호학적 디지털 전자서명 레코드.",
        "- <code>DNSKEY</code>: RRSIG 서명을 검증하기 위한 공인 공개키 레코드 (KSK: 키 서명 키, ZSK: 존 서명 키).",
        "- <code>DS (Delegation Signer)</code>: 상위 존(TLD)에 등록된 하위 존 KSK의 SHA 해시값으로 신뢰의 사슬(Chain of Trust) 형성.",
        "- <code>NSEC / NSEC3</code>: 존재하지 않는 도메인 질의(NXDOMAIN)에 대한 부존재 증명 레코드."
      ]
    },
    {
      "id": "prac_content_14",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "윈도우 BitLocker 드라이브 암호화 및 TPM 부팅 무결성",
      "badge": "실기 실무",
      "points": [
        "<strong>BitLocker 작동 원리:</strong> 볼륨 전체를 AES-128/256으로 암호화하는 전체 디스크 암호화(FDE) 기술.",
        "<strong>TPM (Trusted Platform Module):</strong> 메인보드의 보안 칩에 키(VMK)를 저장하고 PCR(Platform Configuration Register) 레지스터로 부팅 펌웨어 무결성을 측정.",
        "부팅 시 펌웨어나 부트 로더가 변조되었을 경우 TPM이 복호화 키를 릴리즈하지 않아 BitLocker 복구 키 입력을 요구함."
      ]
    },
    {
      "id": "prac_content_15",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "데이터베이스 암호화 3대 방식(API, Plug-in, TDE) 장단점",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>API 방식:</strong> 애플리케이션 소스에서 암호화 API 호출 -> DB 서버 부하 없음, 애플리케이션 소스코드 수정 필요.",
        "<strong>Plug-in 방식:</strong> DBMS 내부에 플러그인(함수, 트리거)으로 설치 -> 애플리케이션 수정 최소화, DB 서버 연산 부하 증가.",
        "<strong>TDE (투명한 데이터 암호화) 방식:</strong> DBMS 커널 엔진이 파일/블록 단위로 자동 암·복호화 -> 소스코드 및 쿼리 수정 0%, 인덱스 검색 지원."
      ]
    },
    {
      "id": "prac_content_16",
      "type": "content",
      "category": "law",
      "category_name": "디지털 포렌식 & 법률",
      "title": "KISA 표준 사이버 침해사고 대응 7단계 절차",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>1단계 사고 전 준비:</strong> 보안 정책 수립, 관제 로그 수집 인프라 및 대응팀(CERT) 구성.",
        "<strong>2단계 사고 탐지:</strong> 침입탐지시스템(IDS/IPS), EDR, 방화벽 로그 분석을 통한 이상 징후 포착.",
        "<strong>3단계 초기 대응:</strong> 사고 통지, 침해 시스템 식별, 네트워크 물리적 격리(케이블 분리).",
        "<strong>4단계 대응 전략 수립:</strong> 사고 피해 규모 산정, 침해 원인 초기 진단, 법적 대응 여부 결정.",
        "<strong>5단계 사고 조사 및 분석:</strong> 휘발성 메모리 덤프, 디스크 이미징, 타임라인 분석, C2 IP 추적.",
        "<strong>6단계 복구 및 해결:</strong> 취약점 패치, 백도어 악성코드 제거, 무결성이 검증된 백업 데이터 복원.",
        "<strong>7단계 사후 검토 및 보고서 작성:</strong> 침해 원인 보고서 작성, 경영진 보고, 재발 방지 대책 수립."
      ]
    },
    {
      "id": "prac_content_17",
      "type": "content",
      "category": "system",
      "category_name": "시스템 보안",
      "title": "리눅스 메모리 상주 악성코드 복구 및 프로세스 역추적",
      "badge": "실기 실무",
      "points": [
        "공격자가 <code>rm -f /tmp/backdoor.sh</code>로 원본을 지우고 프로세스를 백그라운드로 실행한 경우:",
        "1. <code>ps -ef | grep backdoor</code> 또는 <code>lsof +L1</code>(Unlinked 오픈 파일 검색)로 PID 확인.",
        "2. <code>ls -l /proc/[PID]/exe</code> 확인 시 <code>(deleted)</code> 표시 확인.",
        "3. <code>cp /proc/[PID]/exe /tmp/recovered_malware</code> 명령어로 메모리에 매핑된 원본 바이너리 즉시 덤프 및 복구.",
        "4. <code>sha256sum /tmp/recovered_malware</code>로 해시값 산출 후 VirusTotal 분석."
      ]
    },
    {
      "id": "prac_content_18",
      "type": "content",
      "category": "network",
      "category_name": "네트워크 보안",
      "title": "SSL/TLS 중간자 공격(MITM) 및 SSL Stripping 방어",
      "badge": "실기 단답·실무",
      "points": [
        "<strong>SSL Stripping 공격:</strong> 클라이언트와 서버 간의 HTTPS 연결을 가로채어 클라이언트에게는 일반 HTTP로 다운그레이드 통신하게 만드는 공격.",
        "<strong>방어 대책:</strong>",
        "- <code>HSTS (Strict-Transport-Security)</code> 헤더를 브라우저에 등록하여 클라이언트가 애초에 HTTP 접속을 시도하지 못하게 차단.",
        "- <code>HSTS Preload</code> 리스트에 도메인을 정식 등록하여 최초 접속(First-Visit) 시에도 무조건 HTTPS 강제.",
        "- 클라이언트 인증서 기반의 <code>mTLS (상호 TLS 인증)</code> 도입."
      ]
    },
    {
      "id": "prac_content_19",
      "type": "content",
      "category": "app",
      "category_name": "애플리케이션 보안",
      "title": "Cross-Site Scripting (XSS) 3대 유형 및 다계층 방어",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>Stored XSS:</strong> 악성 스크립트가 게시판 DB에 저장되어 불특정 다수 방문자에게 지속적 피해 발생 (가장 위험).",
        "<strong>Reflected XSS:</strong> 검색어 URL 파라미터 등에 악성 스크립트가 포함되어 서버 응답 페이지로 즉시 반사되는 공격.",
        "<strong>DOM-based XSS:</strong> 서버로 전송되지 않고 브라우저 클라이언트 JS(innerHTML, document.write)에서 DOM 조작 시 발생.",
        "<strong>방어:</strong> 출력 시 HTML Entity 인코딩, 세션 쿠키 <code>HttpOnly</code> 플래그 강제, <code>CSP (Content-Security-Policy)</code> 적용."
      ]
    },
    {
      "id": "prac_content_20",
      "type": "content",
      "category": "law",
      "category_name": "디지털 포렌식 & 법률",
      "title": "클라우드 침해사고 대응 및 IAM 최소 권한 가이드라인",
      "badge": "실기 서술·실무",
      "points": [
        "<strong>Root 계정 보안:</strong> 일상 업무 사용 전면 금지, 하드웨어 보안 키(YubiKey 등) 기반 MFA 의무화.",
        "<strong>임시 자격증명:</strong> 영구적인 IAM User Access Key 발급을 금지하고 AssumeRole(STS 임시 토큰) 사용.",
        "<strong>최소 권한 정책:</strong> AdministratorAccess 및 Action: \"*\" 부여를 금지하고, 리소스 ARN별로 최소 권한 할당.",
        "<strong>클라우드 감사 로그:</strong> CloudTrail(API 호출 감사) 및 VPC Flow Logs(네트워크 흐름) 다중 리전 활성화 및 위·변조 방지 S3 보관."
      ]
    },
    {
      "id": "prac_term_01",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] find (-perm -4000)",
      "term": "find (-perm -4000)",
      "badge": "단답형 족보",
      "points": [
        "SetUID가 설정된 실행 바이너리를 전수 검색하여 권한 상승 취약점을 탐지하는 리눅스 명령어."
      ]
    },
    {
      "id": "prac_term_02",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] netstat (-antp)",
      "term": "netstat (-antp)",
      "badge": "단답형 족보",
      "points": [
        "활성 TCP/UDP 네트워크 소켓, 수신 포트, PID 및 프로세스명을 조회하는 핵심 포트 점검 명령어."
      ]
    },
    {
      "id": "prac_term_03",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] umask (027)",
      "term": "umask (027)",
      "badge": "단답형 족보",
      "points": [
        "신규 파일 생성 시 640(-rw-r-----), 디렉토리 생성 시 750(drwxr-x---) 권한을 강제 부여하는 마스크값."
      ]
    },
    {
      "id": "prac_term_04",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] chattr (+i / -i)",
      "term": "chattr (+i / -i)",
      "badge": "단답형 족보",
      "points": [
        "root 사용자라도 파일을 삭제, 수정, 이름 변경할 수 없도록 속성을 불변(Immutable) 상태로 잠그는 명령어."
      ]
    },
    {
      "id": "prac_term_05",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] lastlog (/var/log/lastlog)",
      "term": "lastlog (/var/log/lastlog)",
      "badge": "단답형 족보",
      "points": [
        "시스템 내 모든 사용자의 최근 로그인 일시와 출발지 IP를 확인하는 바이너리 로그 조회 명령어."
      ]
    },
    {
      "id": "prac_term_06",
      "type": "term",
      "category": "network",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] tcpdump",
      "term": "tcpdump",
      "badge": "단답형 족보",
      "points": [
        "네트워크 인터페이스(eth0 등)를 통과하는 패킷의 헤더와 페이로드를 실시간 캡처 및 필터링하는 도구."
      ]
    },
    {
      "id": "prac_term_07",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] icacls",
      "term": "icacls",
      "badge": "단답형 족보",
      "points": [
        "윈도우 NTFS 파일 시스템에서 파일 및 폴더의 접근 제어 목록(ACL) 권한을 명령줄에서 확인·수정하는 도구."
      ]
    },
    {
      "id": "prac_term_08",
      "type": "term",
      "category": "network",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] distance (Snort)",
      "term": "distance (Snort)",
      "badge": "단답형 족보",
      "points": [
        "직전 content 패턴 매칭 끝 지점으로부터 다음 패턴을 탐색할 상대적 시작 거리를 바이트 단위로 지정하는 Snort 옵션."
      ]
    },
    {
      "id": "prac_term_09",
      "type": "term",
      "category": "network",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] within (Snort)",
      "term": "within (Snort)",
      "badge": "단답형 족보",
      "points": [
        "distance 지점부터 최대 몇 바이트 범위 안에서 다음 패턴을 찾아야 하는지 탐색 범위를 한정하는 Snort 옵션."
      ]
    },
    {
      "id": "prac_term_10",
      "type": "term",
      "category": "network",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] iptables REJECT",
      "term": "iptables REJECT",
      "badge": "단답형 족보",
      "points": [
        "접속 패킷을 차단할 때 송신자에게 ICMP unreachable 또는 TCP RST 거부 응답을 명시적으로 회신하는 타겟."
      ]
    },
    {
      "id": "prac_term_11",
      "type": "term",
      "category": "app",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] PreparedStatement",
      "term": "PreparedStatement",
      "badge": "단답형 족보",
      "points": [
        "SQL 쿼리를 사전 컴파일하고 입력값을 파라미터로 안전하게 바인딩하여 SQL Injection을 원천 차단하는 인터페이스."
      ]
    },
    {
      "id": "prac_term_12",
      "type": "term",
      "category": "app",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] SameSite=Lax",
      "term": "SameSite=Lax",
      "badge": "단답형 족보",
      "points": [
        "타 사이트에서의 안전한 GET 최상위 링크 이동만 허용하고, 외부 POST 등 비인가 요청에서 쿠키 전송을 막는 CSRF 방어 속성."
      ]
    },
    {
      "id": "prac_term_13",
      "type": "term",
      "category": "app",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] Strict-Transport-Security (HSTS)",
      "term": "Strict-Transport-Security (HSTS)",
      "badge": "단답형 족보",
      "points": [
        "웹 브라우저가 평문 HTTP 연결을 일절 시도하지 않고 오직 HTTPS로만 통신하도록 강제하는 보안 헤더."
      ]
    },
    {
      "id": "prac_term_14",
      "type": "term",
      "category": "app",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] Content-Security-Policy (CSP)",
      "term": "Content-Security-Policy (CSP)",
      "badge": "단답형 족보",
      "points": [
        "브라우저에서 실행 가능한 스크립트, 스타일, 이미지 등의 신뢰 출처를 지정하여 XSS 공격을 방어하는 보안 헤더."
      ]
    },
    {
      "id": "prac_term_15",
      "type": "term",
      "category": "law",
      "category_name": "실기 단답형 용어 (포렌식)",
      "title": "[실기 단답] Volatility",
      "term": "Volatility",
      "badge": "단답형 족보",
      "points": [
        "물리 RAM 메모리 덤프 파일을 파싱하여 프로세스 트리, 네트워크 소켓, 셸코드 등을 역공학 분석하는 메모리 포렌식 도구."
      ]
    },
    {
      "id": "prac_term_16",
      "type": "term",
      "category": "general",
      "category_name": "실기 단답형 용어 (보안관리)",
      "title": "[실기 단답] SBOM",
      "term": "SBOM",
      "badge": "단답형 족보",
      "points": [
        "소프트웨어 공급망 보안을 위해 오픈소스 라이브러리, 패키지 버전, 의존성 관계를 기계 판독 가능하게 작성한 소프트웨어 자재 명세서."
      ]
    },
    {
      "id": "prac_term_17",
      "type": "term",
      "category": "general",
      "category_name": "실기 단답형 용어 (보안관제)",
      "title": "[실기 단답] SOAR",
      "term": "SOAR",
      "badge": "단답형 족보",
      "points": [
        "보안 솔루션 경보를 통합하고 사전 정의된 플레이북(Playbook)에 따라 침해 대응 프로세스를 자동 오케스트레이션하는 관제 기술."
      ]
    },
    {
      "id": "prac_term_18",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] EDR",
      "term": "EDR",
      "badge": "단답형 족보",
      "points": [
        "단말기(엔드포인트)의 프로세스 생성, 파일 변경, 네트워크 연결 행위를 실시간 모니터링하여 침해를 탐지·격리하는 솔루션."
      ]
    },
    {
      "id": "prac_term_19",
      "type": "term",
      "category": "network",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] SPAN (Port Mirroring)",
      "term": "SPAN (Port Mirroring)",
      "badge": "단답형 족보",
      "points": [
        "스위치 포트나 VLAN의 패킷을 네트워크 분석 장비(IDS, Wireshark)가 연결된 특정 모니터링 포트로 복제하는 기능."
      ]
    },
    {
      "id": "prac_term_20",
      "type": "term",
      "category": "general",
      "category_name": "실기 단답형 용어 (보안관리)",
      "title": "[실기 단답] MITRE ATT&CK",
      "term": "MITRE ATT&CK",
      "badge": "단답형 족보",
      "points": [
        "실제 사이버 공격자의 공격 전술(Tactics), 기술(Techniques), 절차(Procedures)를 매트릭스로 집대성한 지식 프레임워크."
      ]
    },
    {
      "id": "prac_term_21",
      "type": "term",
      "category": "general",
      "category_name": "실기 단답형 용어 (암호학)",
      "title": "[실기 단답] Perfect Forward Secrecy (PFS)",
      "term": "Perfect Forward Secrecy (PFS)",
      "badge": "단답형 족보",
      "points": [
        "서버의 장기 개인키가 유출되더라도 일회성 임시 세션키 폐기를 통해 과거 암호화 통신의 복호화를 방지하는 암호학적 특성."
      ]
    },
    {
      "id": "prac_term_22",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] auditctl",
      "term": "auditctl",
      "badge": "단답형 족보",
      "points": [
        "리눅스 커널 감사 서브시스템(auditd)에 특정 시스템 콜이나 중요 파일(/etc/passwd) 감시 규칙을 실시간 등록하는 도구."
      ]
    },
    {
      "id": "prac_term_23",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] fail2ban",
      "term": "fail2ban",
      "badge": "단답형 족보",
      "points": [
        "SSH 등에서 일정 횟수 이상 인증 실패 로그가 기록되면 방화벽(iptables)에 차단 룰을 동적으로 생성하여 무차별 대입을 막는 도구."
      ]
    },
    {
      "id": "prac_term_24",
      "type": "term",
      "category": "app",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] SecureRandom",
      "term": "SecureRandom",
      "badge": "단답형 족보",
      "points": [
        "선형 합동(LCG) 대신 암호학적으로 안전한 난수를 생성하여 예측 불가능한 세션 ID 및 솔트(Salt)를 발급하는 자바 클래스."
      ]
    },
    {
      "id": "prac_term_25",
      "type": "term",
      "category": "law",
      "category_name": "실기 단답형 용어 (포렌식)",
      "title": "[실기 단답] Chain of Custody (연계보관성)",
      "term": "Chain of Custody (연계보관성)",
      "badge": "단답형 족보",
      "points": [
        "디지털 증거가 압수된 순간부터 법정 제출 시까지 취급자, 보관 장소, 일시를 연속적으로 기록 증명하는 포렌식 기본 원칙."
      ]
    },
    {
      "id": "prac_term_26",
      "type": "term",
      "category": "app",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] Open Redirect",
      "term": "Open Redirect",
      "badge": "단답형 족보",
      "points": [
        "사용자 입력 URL을 검증 없이 HTTP 302 리다이렉트 대상으로 사용하여 악성 피싱 사이트로 연결시키는 웹 취약점."
      ]
    },
    {
      "id": "prac_term_27",
      "type": "term",
      "category": "system",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] Tripwire",
      "term": "Tripwire",
      "badge": "단답형 족보",
      "points": [
        "시스템 바이너리 및 설정 파일의 기준 해시값(SHA-256)을 저장해 두고 변경 여부를 감시하여 악성 변조를 탐지하는 HIDS 도구."
      ]
    },
    {
      "id": "prac_term_28",
      "type": "term",
      "category": "law",
      "category_name": "실기 단답형 용어 (포렌식)",
      "title": "[실기 단답] Order of Volatility",
      "term": "Order of Volatility",
      "badge": "단답형 족보",
      "points": [
        "디지털 증거 수집 시 휘발성이 높은 순서(레지스터/캐시 -> RAM -> 네트워크 연결 -> 디스크)대로 수집해야 한다는 원칙."
      ]
    },
    {
      "id": "prac_term_29",
      "type": "term",
      "category": "law",
      "category_name": "실기 단답형 용어 (법률)",
      "title": "[실기 단답] CISO 겸직금지",
      "term": "CISO 겸직금지",
      "badge": "단답형 족보",
      "points": [
        "자산 5조 원 이상 또는 자산 5천억 이상 ISMS 의무 대상 기업의 CISO는 정보기술(CIO) 등 타 임원 직무를 겸직할 수 없도록 한 규정."
      ]
    },
    {
      "id": "prac_term_30",
      "type": "term",
      "category": "general",
      "category_name": "실기 단답형 용어 (보안관리)",
      "title": "[실기 단답] Zero Trust (Never Trust, Always Verify)",
      "term": "Zero Trust (Never Trust, Always Verify)",
      "badge": "단답형 족보",
      "points": [
        "내부망이라 할지라도 결코 신뢰하지 않고 모든 사용자, 기기, 세션에 대해 지속적인 인증과 최소 권한을 부여하는 보안 철학."
      ]
    }
  ]
};

window.ISMSP_AUDITOR_DATA = {
  "title": "ISMS-P 인증심사원 실전 결함판정 퀴즈 (30제) & 102개 기준 결함사례",
  "description": "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 실전 결함판정 시나리오 퀴즈 1·2회(총 30문항) 및 102개 전 기준 결함사례 총람",
  "questions": [
    {
      "id": "ISMSP1_Q1",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 관리체계 수립·운영 (16개)",
      "question": "[결함 판정] 대규모 전자상거래 기업에서 CISO가 개발본부장(CIO)을 겸직하여 정보시스템 개발 및 인프라 운영 업무를 총괄 관리하도록 발령한 경우 위반되는 인증기준은?",
      "options": [
        "1.1.1 경영진의 참여",
        "1.1.2 최고책임자의 지정",
        "1.1.3 조직 구성",
        "1.1.4 범위 설정",
        "1.2.1 위험 식별"
      ],
      "answer": 2,
      "explanation": "ISMS-P 1.1.2 및 망법에 따라 일정 규모 이상 기업의 CISO는 회사의 다른 IT 부문 업무(CIO, 개발본부장 등)를 겸직할 수 없습니다."
    },
    {
      "id": "ISMSP1_Q2",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 관리체계 수립·운영 (16개)",
      "question": "[결함 판정] 정기 위험평가를 실시하여 위험도를 도출하였으나, 최고경영진이 승인한 수용 가능한 위험 수준(DOA)의 기준치가 정의되어 있지 않아 조치 대상을 객관적으로 선별할 수 없었던 사례가 위반한 기준은?",
      "options": [
        "1.2.1 위험 식별 및 분석",
        "1.2.2 위험 평가 및 정보보호 대책 수립",
        "1.1.1 경영진의 참여",
        "1.4.2 관리체계 점검",
        "1.3.1 보호대책 공유"
      ],
      "answer": 2,
      "explanation": "1.2.2 기준에 따라 조직의 환경을 고려하여 경영진이 승인한 DOA(Degree of Acceptance) 기준을 수립하고 이를 초과하는 위험에 대해 대책을 마련해야 합니다."
    },
    {
      "id": "ISMSP1_Q3",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 관리체계 수립·운영 (16개)",
      "question": "[결함 판정] 인증심사 범위에 포함된 신규 모바일 앱 서비스와 클라우드 인프라 자산이 자산관리 대장에 누락되어 위험평가 대상에서 제외된 사례가 위반한 기준은?",
      "options": [
        "1.1.4 범위 설정",
        "1.1.1 경영진의 참여",
        "1.3.2 이행점검",
        "1.4.1 법적 요구사항 검토",
        "1.2.2 위험 평가"
      ],
      "answer": 1,
      "explanation": "1.1.4 기준은 인증 범위 내의 모든 정보자산, 서비스, 네트워크, 개인정보 처리 흐름도를 누락 없이 식별하여 관리체계 범위로 설정하도록 요구합니다."
    },
    {
      "id": "ISMSP1_Q4",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] ISMS-P 2.6.7(접속기록 보관 및 점검) 기준상 5만명 이상의 고유식별정보 또는 민감정보를 처리하는 대규모 개인정보처리시스템의 접속기록 보관 및 점검 요건으로 올바른 것은?",
      "options": [
        "최소 1년 이상 보관, 분기 1회 점검",
        "최소 1년 이상 보관, 월 1회 점검",
        "최소 2년 이상 보관, 월 1회 점검",
        "최소 2년 이상 보관, 반기 1회 점검",
        "최소 3년 이상 보관, 연 1회 점검"
      ],
      "answer": 3,
      "explanation": "안전성 확보조치 기준 제8조에 따라 5만명 이상의 민감정보 또는 고유식별정보 처리 시스템은 접속기록을 2년 이상 보관하고 월 1회 이상 점검해야 합니다."
    },
    {
      "id": "ISMSP1_Q5",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 관리자 시스템의 초기 패스워드를 'Welcome123!'으로 일괄 부여하고, 최초 로그인 시 패스워드 변경을 강제하지 않아 수개월간 초기 패스워드가 방치된 사례가 위반한 기준은?",
      "options": [
        "2.5.1 사용자 식별",
        "2.5.4 비밀번호 관리",
        "2.6.1 네트워크 접근",
        "2.7.1 암호정책 적용",
        "2.5.2 사용자 인증"
      ],
      "answer": 2,
      "explanation": "2.5.4 기준에 따라 초기 비밀번호는 최초 접속 시 반드시 변경하도록 강제 통제해야 합니다."
    },
    {
      "id": "ISMSP1_Q6",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 개발 및 테스트 환경에서 실제 운영 DB의 고객 이름, 휴대폰번호, 주민등록번호 데이터를 마스킹이나 가명처리 없이 그대로 복사하여 사용한 사례가 위반한 기준은?",
      "options": [
        "2.8.5 시험 데이터 보안",
        "2.6.2 개발망/운영망 분리",
        "2.7.1 암호정책 적용",
        "2.9.1 운영절차 관리",
        "2.8.1 보안시스템 개발"
      ],
      "answer": 1,
      "explanation": "2.8.5(시험 데이터 보안) 기준에 따라 시스템 개발, 테스트 시 원칙적으로 실제 개인정보 사용이 금지되며, 부득이한 경우 가명·익명화 처리를 해야 합니다."
    },
    {
      "id": "ISMSP1_Q7",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 퇴사자가 발생하였으나 인사팀에서 보안/전산팀으로 통보가 지연되어 퇴사한 지 2주가 지난 직원의 사내 인트라넷 및 VPN 계정이 여전히 활성화되어 있던 사례가 위반한 기준은?",
      "options": [
        "2.2.3 퇴직 및 직무변경",
        "2.5.1 사용자 식별",
        "2.6.1 네트워크 접근",
        "2.3.1 외주용역 보안",
        "2.1.2 조직 구성"
      ],
      "answer": 1,
      "explanation": "2.2.3(퇴직 및 직무변경) 기준에 따라 퇴직 시 정보자산 반납 및 모든 접근 권한의 즉시 회수/비활성화가 이루어져야 합니다."
    },
    {
      "id": "ISMSP1_Q8",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 운영 데이터베이스에 저장된 주민등록번호와 비밀번호를 평문(Plaintext)으로 저장하여 보관하고 있던 사례가 위반한 기준은?",
      "options": [
        "2.7.1 암호정책 적용",
        "2.6.2 개발/운영 분리",
        "2.5.4 비밀번호 관리",
        "2.9.2 성능 및 용량 관리",
        "2.8.4 보안성 검토"
      ],
      "answer": 1,
      "explanation": "2.7.1(암호정책 적용) 기준에 따라 고유식별정보와 비밀번호(일방향 해시)는 저장 시 반드시 안전한 알고리즘으로 암호화하여야 합니다."
    },
    {
      "id": "ISMSP1_Q9",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 (22개)",
      "question": "[결함 판정] 회원가입 웹페이지에서 마케팅 활용 목적의 '생년월일'과 '관심사'를 필수항목으로 지정하고 미동의 시 기본 회원가입을 거부한 사례가 위반한 기준은?",
      "options": [
        "3.1.2 수집 제한 및 최소 수집",
        "3.1.1 수집 동의 기준",
        "3.2.1 개인정보 현황 관리",
        "3.3.1 제3자 제공",
        "3.5.1 권리 보장"
      ],
      "answer": 1,
      "explanation": "3.1.2 기준에 따라 선택항목 미제공을 이유로 기본 서비스 제공을 거부할 수 없습니다."
    },
    {
      "id": "ISMSP1_Q10",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 (22개)",
      "question": "[결함 판정] 보유기간(3년)이 도래한 이벤트 참여자 개인정보를 파기하지 않고 향후 마케팅 홍보에 재사용하기 위해 운영 DB에 방치한 사례가 위반한 기준은?",
      "options": [
        "3.4.1 개인정보 파기",
        "3.2.2 개인정보 품질 관리",
        "3.1.1 수집 동의 기준",
        "3.3.2 업무 위탁",
        "3.5.2 정보주체 통지"
      ],
      "answer": 1,
      "explanation": "3.4.1 기준에 따라 보유기간 경과 또는 처리 목적 달성 시 지체 없이(5일 이내) 복구 불가능한 방법으로 영구 파기해야 합니다."
    },
    {
      "id": "ISMSP1_Q11",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 (22개)",
      "question": "[결함 판정] 고객 배송 업무를 택배사에 위탁하면서 위탁계약서에 재위탁 제한 및 안전조치 의무 규정을 누락하고, 연 1회 수탁사 관리·감독 점검을 전혀 실시하지 않은 사례가 위반한 기준은?",
      "options": [
        "3.3.2 업무 위탁에 따른 관리·감독",
        "3.3.1 개인정보의 제3자 제공",
        "3.1.1 수집 동의 기준",
        "3.4.1 개인정보 파기",
        "2.3.1 외주용역 보안"
      ],
      "answer": 1,
      "explanation": "3.3.2 기준에 따라 위탁 계약 시 법정 필수사항(목적, 재위탁 제한, 안전조치)을 문서화하고 연 1회 이상 수탁사의 처리 실태를 정기 점검해야 합니다."
    },
    {
      "id": "ISMSP1_Q12",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 (22개)",
      "question": "[결함 판정] 정보주체가 자신의 개인정보에 대한 열람 및 삭제를 요구하였으나 정당한 사유나 통지 없이 법정 기한(10일)이 넘도록 아무런 조치를 취하지 않은 사례가 위반한 기준은?",
      "options": [
        "3.5.1 정보주체 권리보장",
        "3.4.1 개인정보 파기",
        "3.2.1 개인정보 현황 관리",
        "3.1.2 수집 제한",
        "1.4.1 법적 요구사항"
      ],
      "answer": 1,
      "explanation": "3.5.1 기준에 따라 정보주체의 열람, 정정, 삭제 요구에 대해 10일 이내에 조치 결과를 회신하여야 합니다."
    },
    {
      "id": "ISMSP1_Q13",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 개인정보처리시스템의 서버 접속 로그 파일이 저장된 디렉토리에 대해 백업을 수행하지 않고, 관리자 계정으로 로그 파일을 임의로 삭제하거나 위조할 수 있도록 쓰기 권한이 부여된 사례가 위반한 기준은?",
      "options": [
        "2.6.7 접속기록 보관 및 점검",
        "2.9.3 백업 및 복구",
        "2.5.3 특권 계정 관리",
        "2.7.2 암호키 관리",
        "2.10.1 침해사고 대응"
      ],
      "answer": 1,
      "explanation": "2.6.7 기준에 따라 접속기록은 위·변조 및 도난, 분실되지 않도록 안전한 별도 저장소에 백업 보관하고 접근 권한을 최소화하여야 합니다."
    },
    {
      "id": "ISMSP1_Q14",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 전산실 및 통제구역 출입문에 전자식 출입통제 시스템이 설치되어 있으나, 방문자의 출입 수기 대장이 비치되어 있지 않고 출입 로그가 1개월만 보관된 후 삭제된 사례가 위반한 기준은?",
      "options": [
        "2.4.1 출입통제",
        "2.4.2 물리적 보호구역 지정",
        "2.4.4 전산실 보호",
        "2.6.1 네트워크 접근",
        "2.2.1 임직원 보안"
      ],
      "answer": 1,
      "explanation": "2.4.1(출입통제) 기준에 따라 통제구역에 대한 출입기록은 최소 1년(또는 3년) 이상 보관하고 정기적으로 검토하여야 합니다."
    },
    {
      "id": "ISMSP1_Q15",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 (22개)",
      "question": "[결함 판정] 개인정보 처리방침에 기재된 수집 항목에는 '이메일'만 명시되어 있으나 실제 회원가입 시 '자택 전화번호'와 '직장명'을 추가 수집하여 처리방침과 실제 처리 현황이 불일치한 사례가 위반한 기준은?",
      "options": [
        "3.2.1 개인정보 현황 관리",
        "3.1.1 수집 동의 기준",
        "3.1.2 최소 수집",
        "3.5.2 개인정보 처리방침 공개",
        "1.1.4 범위 설정"
      ],
      "answer": 1,
      "explanation": "3.2.1(개인정보 현황 관리) 기준에 따라 개인정보 처리방침 및 내부 관리대장과 실제 시스템에서 수집·이용되는 개인정보 항목은 100% 일치해야 합니다."
    },
    {
      "id": "ISMSP2_Q1",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 관리체계 수립·운영 (16개)",
      "question": "[결함 판정] 회사의 내부감사 계획에 따라 ISMS-P 관리체계 내부감사를 실시하였으나, 감사 총괄 책임자로 정보보호최고책임자(CISO)가 임명되어 자신이 수립·운영한 보안 체계를 스스로 점검(자가 감사)한 경우 위반되는 인증기준은?",
      "options": [
        "1.4.2 관리체계 점검",
        "1.1.2 최고책임자의 지정",
        "1.3.1 보안 정책 수립",
        "1.2.2 위험 평가",
        "1.4.1 법적 요구사항 준수"
      ],
      "answer": 1,
      "explanation": "ISMS-P 1.4.2(관리체계 점검)에 따라 내부감사원은 피감사 조직(부서)과 독립된 인력으로 구성되어 객관적이고 독립적인 감사를 수행해야 합니다. CISO가 주관한 자가 감사는 독립성 결여로 명백한 결함입니다."
    },
    {
      "id": "ISMSP2_Q2",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 인사 이동으로 인해 개발팀에서 마케팅팀으로 전보된 직원의 형상관리 시스템(Git) 커밋 권한 및 개발 서버 SSH 접속 권한이 2개월이 경과하도록 회수되지 않고 유지된 경우 위반되는 인증기준은?",
      "options": [
        "2.2.3 퇴직 및 직무변경",
        "2.5.1 사용자 계정 관리",
        "2.6.2 개발망 분리",
        "2.1.1 보안 인력 확보",
        "2.5.2 특권 계정 관리"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.2.3(퇴직 및 직무변경)에 따라 직원의 퇴직 또는 부서 이동 등 직무 변경 발생 시 즉시 권한을 회수하거나 변경된 직무에 맞게 최소 권한으로 재조정하여야 합니다."
    },
    {
      "id": "ISMSP2_Q3",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 신규 입사자에게 발급된 시스템 초기 비밀번호가 사원번호와 동일하게 일괄 설정되어 있으며, 시스템 최초 로그인 시 비밀번호 변경을 강제하지 않아 다수의 직원이 초기 비밀번호를 수개월간 그대로 사용 중인 경우 위반되는 인증기준은?",
      "options": [
        "2.5.4 비밀번호 관리",
        "2.5.1 사용자 계정 관리",
        "2.2.1 인적 보안",
        "2.7.2 암호화 적용",
        "2.6.1 네트워크 접근"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.5.4(비밀번호 관리)에 따라 초기 임시 비밀번호는 안전하게 발급되어야 하며, 시스템 접속 시 즉시 본인의 비밀번호로 변경하도록 기술적으로 강제해야 합니다."
    },
    {
      "id": "ISMSP2_Q4",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 애플리케이션 개발자가 긴급 유지보수를 이유로 개인 업무용 PC에서 직접 운영 데이터베이스(Oracle DB)에 GUI 클라이언트로 접속하여 DDL 및 DML(UPDATE, DELETE) 작업을 수행할 수 있도록 방화벽이 개방되어 있는 경우 위반되는 인증기준은?",
      "options": [
        "2.6.2 개발·운영 시스템 분리",
        "2.8.1 개발 보안",
        "2.5.2 특권 계정 관리",
        "2.9.1 운영 절차 관리",
        "2.6.1 네트워크 접근"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.6.2(개발·운영 시스템 분리)에 따라 개발망과 운영망은 원칙적으로 분리되어야 하며, 개발자가 운영 DB에 직접 접속하는 것은 엄격히 금지되고 승인된 절차와 결재를 통해서만 접근해야 합니다."
    },
    {
      "id": "ISMSP2_Q5",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 신규 결제 모듈 기능 테스트를 위해 운영 데이터베이스에서 실제 고객 10만 명의 성명, 주민등록번호, 계좌번호 데이터를 아무런 마스킹이나 가명처리 없이 개발 테스트 서버로 복사하여 테스트에 사용한 경우 위반되는 인증기준은?",
      "options": [
        "2.8.5 시험 데이터 보안",
        "2.7.1 암호정책 적용",
        "3.2.3 개인정보 표시제한",
        "2.6.7 접속기록 관리",
        "3.1.2 수집 제한"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.8.5(시험 데이터 보안)에 따라 정보시스템 개발 및 테스트 시 실제 운영 개인정보의 사용은 원칙적으로 금지되며, 불가피한 경우 책임자 승인 하에 가명·익명 처리 또는 더미 데이터를 생성하여 사용해야 합니다."
    },
    {
      "id": "ISMSP2_Q6",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 서버 전산실(통제구역)에 입주한 외부 유지보수 협력업체 직원이 상주 직원의 동행이나 방문 출입 대장 작성 없이 출입증을 전달받아 단독으로 출입한 사실이 확인된 경우 위반되는 인증기준은?",
      "options": [
        "2.4.1 출입통제",
        "2.4.2 물리적 보안구역 지정",
        "2.2.2 계약 시 보안요구",
        "2.3.1 자산 식별",
        "2.9.1 운영 절차 관리"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.4.1(출입통제)에 따라 전산실 등 통제구역에 외부인이 출입할 때에는 반드시 사전 승인을 거치고 출입 대장을 기록하며 보안담당자가 입회·동행하여야 합니다."
    },
    {
      "id": "ISMSP2_Q7",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 대외 서비스를 제공하는 웹서버에 수개월 전 발표된 원격 코드 실행(RCE) 고위험 보안 취약점이 존재하고 패치 권고가 내려졌음에도, 서비스 중단 우려를 이유로 보안성 검토나 완화 조치 없이 방치된 경우 위반되는 인증기준은?",
      "options": [
        "2.10.1 보안시스템 운영 및 패치 관리",
        "2.8.4 배포 및 이관",
        "2.3.2 자산 중요도 분류",
        "2.9.2 변경 관리",
        "2.1.2 침해대응"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.10.1(보안시스템 운영/취약점 점검 및 조치)에 따라 취약점이 공지되거나 점검에서 식별된 경우 보안패치를 신속히 적용하거나 WAF 룰셋 등 대체 완화 대책을 마련해야 합니다."
    },
    {
      "id": "ISMSP2_Q8",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 코로나19 이후 사내 임직원들의 재택근무를 위해 구축된 원격접속(VPN) 시스템에서 ID와 단일 비밀번호만으로 로그인이 가능하도록 구성되어 있는 경우 위반되는 인증기준은?",
      "options": [
        "2.6.4 원격접근 통제",
        "2.6.1 네트워크 접근",
        "2.5.4 비밀번호 관리",
        "2.7.2 암호화 전송",
        "2.4.1 물리보안"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.6.4(원격접근 통제)에 따라 사외에서 사내망으로 원격 접속(VPN 등) 시에는 안전한 인증 수단(OTP, 보안토큰 등 다중인증 MFA)과 전송구간 암호화가 의무적으로 적용되어야 합니다."
    },
    {
      "id": "ISMSP2_Q9",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 매일 전체 데이터베이스 백업을 수행하고 외장 하드디스크에 백업본을 저장하고 있으나, 최근 2년간 단 한 번도 실제 복구 모의훈련을 실시하지 않아 백업 데이터의 유효성을 검증하지 못한 경우 위반되는 인증기준은?",
      "options": [
        "2.9.3 백업 및 복구 관리",
        "2.9.2 변경 관리",
        "2.10.3 악성코드 통제",
        "2.11.1 침해사고 예방",
        "1.3.2 운영 현황 관리"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.9.3(백업 및 복구 관리)에 따라 백업 매체의 정상 작동 여부와 데이터 복구 가능성을 검증하기 위해 연 1회 이상 정기적으로 실제 복구 훈련을 실시하고 그 결과를 기록해야 합니다."
    },
    {
      "id": "ISMSP2_Q10",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 100만 명의 개인정보 및 주민등록번호를 처리하는 개인정보처리시스템의 웹서버 및 DB 접속기록을 1년만 보관하고 이전 로그는 자동 삭제되도록 설정한 경우 위반되는 인증기준은?",
      "options": [
        "2.6.7 접속기록 관리",
        "2.5.1 사용자 계정 관리",
        "2.7.2 암호화 적용",
        "3.4.1 개인정보 파기",
        "2.9.1 운영 절차 관리"
      ],
      "answer": 1,
      "explanation": "ISMS-P 2.6.7 및 개인정보 안전성 확보조치 기준에 따라 5만 명 이상의 고유식별정보 또는 민감정보를 처리하는 시스템의 접속기록은 최소 2년 이상 보관·관리해야 하므로 결함입니다."
    },
    {
      "id": "ISMSP2_Q11",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 요구 (22개)",
      "question": "[결함 판정] 온라인 회원가입 화면에서 '마케팅 활용 및 이벤트 안내(선택)' 항목에 동의하지 않았다는 이유로 다음 단계인 회원가입 완료 버튼이 비활성화되어 가입이 불가능한 경우 위반되는 인증기준은?",
      "options": [
        "3.1.2 수집 제한 (선택동의 거부 금지)",
        "3.1.1 수집 동의 기준",
        "3.2.1 개인정보 현황 관리",
        "3.3.1 개인정보 제공",
        "3.5.1 정보주체 권리 보장"
      ],
      "answer": 1,
      "explanation": "ISMS-P 3.1.2 및 개인정보 보호법 제16조에 따라 정보주체가 선택항목에 동의하지 않는다는 이유로 기본 서비스의 제공을 거부할 수 없으므로 명백한 법적 결함입니다."
    },
    {
      "id": "ISMSP2_Q12",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 요구 (22개)",
      "question": "[결함 판정] 고객 배송 업무를 외부 택배회사에 위탁하면서 위탁 계약서에 개인정보의 목적 외 이용 금지, 기술적·관리적 보호조치 등 법정 필수사항을 기재하였으나, 연 1회 실시해야 하는 수탁사 점검(관리·감독)을 2년간 전혀 수행하지 않은 경우 위반되는 인증기준은?",
      "options": [
        "3.3.2 업무 위탁에 따른 관리·감독",
        "3.3.1 제3자 제공",
        "2.2.2 계약 시 보안요구",
        "3.1.4 민감정보 수집",
        "3.4.1 개인정보 파기"
      ],
      "answer": 1,
      "explanation": "ISMS-P 3.3.2(업무 위탁)에 따라 위탁자는 수탁사가 개인정보를 안전하게 처리하고 있는지 주기적으로(연 1회 이상) 관리·감독하고 실태 점검 결과를 문서화하여 보관해야 합니다."
    },
    {
      "id": "ISMSP2_Q13",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 요구 (22개)",
      "question": "[결함 판정] 회원이 자진 탈퇴를 요청하여 탈퇴 처리가 완료되었으나, 전자상거래법 등 타 법령에 따른 보존 근거가 없는 일반 정보(취미, 관심분야 등)가 탈퇴 후 6개월이 지나도록 운영 DB에 그대로 보관되고 있는 경우 위반되는 인증기준은?",
      "options": [
        "3.4.1 개인정보의 파기",
        "3.2.1 현황 관리",
        "3.5.1 정보주체 권리 보장",
        "3.4.2 분리보관",
        "3.1.2 수집 제한"
      ],
      "answer": 1,
      "explanation": "ISMS-P 3.4.1(개인정보의 파기)에 따라 보유기간 경과나 탈퇴 등 처리 목적이 달성된 개인정보는 정당한 사유가 없는 한 지체 없이(5일 이내) 영구 파기해야 합니다."
    },
    {
      "id": "ISMSP2_Q14",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 요구 (22개)",
      "question": "[결함 판정] 외부 해킹 공격으로 인해 5만 명의 고객 개인정보가 유출된 사실을 2026년 11월 1일 09시에 인지하였으나, 내부 보고 및 원인 조사를 이유로 지체되어 11월 6일에야 관할 기관(KISA/보호위)에 신고한 경우 위반되는 인증기준은?",
      "options": [
        "3.5.2 개인정보 유출 통지 및 신고",
        "2.11.2 침해사고 대응",
        "1.4.1 법적 요구사항 준수",
        "3.5.1 정보주체 권리 보장",
        "2.10.1 보안 모니터링"
      ],
      "answer": 1,
      "explanation": "ISMS-P 3.5.2 및 개정 개인정보 보호법에 따라 유출 사실을 안 때에는 정당한 사유가 없는 한 72시간 이내에 전문기관(보호위/KISA)에 신고해야 하므로 기한 초과 결함입니다."
    },
    {
      "id": "ISMSP2_Q15",
      "category": "ismsp_auditor",
      "exam": 2,
      "exam_name": "2회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 요구 (22개)",
      "question": "[결함 판정] 전자상거래법에 따라 계약 및 청약철회 기록(5년 보존)을 위해 탈퇴 회원의 결제 내역을 보존하고 있으나, 이를 현재 활성 서비스 운영 데이터베이스의 동일 테이블에 탈퇴 플래그(is_deleted='Y')만 설정한 채 보관하고 있는 경우 위반되는 인증기준은?",
      "options": [
        "3.4.2 개인정보의 분리보관",
        "3.4.1 개인정보의 파기",
        "3.2.2 개인정보 처리방침",
        "2.7.2 암호화 적용",
        "2.6.2 개발망 분리"
      ],
      "answer": 1,
      "explanation": "ISMS-P 3.4.2(개인정보의 분리보관)에 따라 타 법령에 의해 보존해야 하는 개인정보는 운영 중인 다른 개인정보와 물리적 또는 논리적으로 완전히 분리된 별도 저장소(DB)에 격리 보관하고 접근을 엄격히 통제해야 합니다."
    }
  ],
  "summaries": [
    {
      "title": "1영역. 관리체계 수립 및 운영 (16개 기준 핵심)",
      "topics": [
        {
          "name": "1.1 기반 마련 및 1.2 위험 관리",
          "points": [
            "1.1.1 경영진의 참여: 최고경영진의 보안위원회 주재 실적, 보안 예산 및 인력 배정 결재 증적 필수.",
            "1.1.2 최고책임자의 지정: CISO/CPO 정식 임명. 망법상 CISO 겸직 제한(대기업 CISO의 CIO/개발본부장 겸직 금지) 준수.",
            "1.1.4 범위 설정: 인증 대상 서비스 관련 시스템, 인프라, 네트워크, 개발망, 개인정보 흐름도 전수 식별.",
            "1.2.2 위험 평가: 최고경영진 승인 하에 DOA(수용 가능한 위험 수준) 설정 및 초과 위험 대책 수립 필수."
          ]
        },
        {
          "name": "1.3 운영·점검 및 1.4 개선",
          "points": [
            "1.4.1 법적 요구사항: 개정 법령(개인정보보호법, 망법 등) 준수 여부 연 1회 이상 정기 검토.",
            "1.4.2 관리체계 점검: 연 1회 이상 독립된 내부감사를 수행하고 발견 결함을 경영진에 공식 보고."
          ]
        }
      ]
    },
    {
      "title": "2영역. 보호대책 요구사항 (64개 기준 핵심)",
      "topics": [
        {
          "name": "인적·물리보안 및 접근통제 (2.1 ~ 2.6)",
          "points": [
            "2.2.3 퇴직 및 직무변경: 퇴직자 계정 및 모든 접근 권한은 당일 즉시 회수 및 비활성화 조치.",
            "2.4.1 출입통제: 전산실/통제구역 출입기록은 최소 1년(또는 3년) 이상 보관 및 주기적 점검.",
            "2.5.4 비밀번호 관리: 3종 8자리 또는 2종 10자리, 초기 패스워드 변경 강제 및 분기 1회 변경 유도.",
            "2.6.2 개발망/운영망 분리: 개발망과 운영망 물리적/논리적 분리, 운영 DB 직접 접근 통제."
          ]
        },
        {
          "name": "접속기록, 암호화 및 운영보안 (2.6 ~ 2.11)",
          "points": [
            "2.6.7 접속기록 보관: 최소 1년(5만명 이상 고유식별정보 처리 시 2년) 보관, 월 1회 이상 이상징후 점검.",
            "2.7.1 암호정책: 고유식별정보, 비밀번호(일방향), 바이오정보 저장 시 암호화 적용.",
            "2.8.5 시험 데이터 보안: 개발/테스트 시 실제 운영 개인정보 사용 금지(가명·익명 처리 데이터 사용).",
            "2.9.3 백업 및 복구: 주기적 백업 수행 및 연 1회 이상 실제 복구 모의훈련 실시 증적 확보."
          ]
        }
      ]
    },
    {
      "title": "3영역. 개인정보 처리단계별 요구사항 (22개 기준 핵심)",
      "topics": [
        {
          "name": "수집·이용 및 제공·위탁 (3.1 ~ 3.3)",
          "points": [
            "3.1.2 수집 제한: 필수항목과 선택항목을 엄격히 구분, 선택항목 미동의를 이유로 기본 서비스 제공 거부 금지.",
            "3.2.1 현황 관리: 개인정보 처리방침과 실제 시스템 수집·이용 항목 간 100% 일치성 유지.",
            "3.3.1 제3자 제공: 정보주체의 별도 동의 필수 (목적, 받는 자, 항목, 보유기간).",
            "3.3.2 업무 위탁: 계약서에 법정 필수사항 명시 및 연 1회 이상 수탁사 처리 실태 관리·감독 점검 실시."
          ]
        },
        {
          "name": "파기 및 정보주체 권리보장 (3.4 ~ 3.5)",
          "points": [
            "3.4.1 개인정보 파기: 보유기간 경과 또는 처리 목적 달성 시 지체 없이(5일 이내) 복구 불가능하게 영구 파기.",
            "3.4.1 분리보관: 타 법령에 따라 보존해야 하는 경우 운영 DB에서 물리적/논리적으로 분리된 별도 저장소에 보관.",
            "3.5.1 권리 보장: 정보주체의 열람, 정정, 삭제, 처리정지 요구에 대해 10일 이내에 조치 결과 통지."
          ]
        }
      ]
    }
  ]
};

// infosec_exam_data.js
// 2026 이기적 정보보안기사 필기+실기 올인원(영진닷컴) 및 ISMS-P 인증심사원 완전판 데이터셋
// 필기 100문항 (1회 50제 + 2회 50제) | 실기 50문항 (단답 25제 + 서술실무 25제) | ISMS-P 15문항

window.INFOSEC_WRITTEN_DATA = {
  "title": "2026 이기적 정보보안기사 (필기) 100제 & 5대 과목 심층 요약집",
  "description": "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1회 실전 모의고사(50제), 2회 고난도 기출 모의고사(50제) 총 100문항 및 1권 이론서 전 과목 핵심 요약노트",
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
    }
  ],
  "summary": {
    "title": "2026 이기적 정보보안기사 필기 5대 과목 심층 요약집 (1권 이론서 전편)",
    "sections": [
      {
        "title": "PART 01 시스템 보안 (운영체제 구조, 계정 관리, 시스템 공격 및 대응)",
        "topics": [
          {
            "name": "운영체제 구조 및 계정·권한 관리",
            "points": [
              "리눅스 계정 파일: /etc/passwd(계정명:암호x:UID:GID:설명:홈디렉토리:로그인셸), /etc/shadow(계정명:암호해시:최근수정일:최소일:최대일:경고일:유예일:만료일).",
              "shadow 암호 식별자: $1(MD5), $2a(Blowfish), $5(SHA-256), $6(SHA-512).",
              "특수 권한 비트: SetUID(4000, 실행 시 소유자 권한 실행), SetGID(2000, 실행 시 그룹 권한), Sticky bit(1000, 공유 디렉토리 내 본인 소유 파일만 삭제 가능).",
              "기본 umask: 파일 666, 디렉토리 777 기준에서 umask 값을 차감. 보안 표준 umask 027 적용 시 디렉토리 750(rwxr-x---), 파일 640(rw-r-----) 생성.",
              "PAM(Pluggable Authentication Modules): required(실패해도 나머지 진행 후 최종 실패), requisite(실패 즉시 중단 및 실패 반환), sufficient(성공 즉시 이전 실패 없으면 승인), optional(성공/실패 영향 없음)."
            ]
          },
          {
            "name": "로그 분석 및 무결성 점검",
            "points": [
              "리눅스 바이너리 로그: /var/log/wtmp(성공한 로그인/로그아웃 이력, last), /var/log/utmp(현재 접속 중인 사용자, who/w), /var/log/btmp(로그인 실패 이력, lastb), /var/log/lastlog(계정별 최종 접속, lastlog).",
              "텍스트 로그: /var/log/secure(인증 및 SSH 접속 로그), /var/log/messages(시스템 전반 커널/데몬 메시지).",
              "무결성 점검: Tripwire, AIDE 등 해시 데이터베이스 기반 변조 탐지 도구 활용.",
              "타임스탬프: atime(접근), mtime(내용 수정), ctime(i-node 메타데이터/권한 변경). ctime은 커널이 갱신하므로 utime 시스템 호출로 위조 불가."
            ]
          },
          {
            "name": "시스템 보안 위협 및 메모리 보호 기법",
            "points": [
              "버퍼 오버플로우: 스택의 복귀 주소(RET)를 조작하여 셸코드 실행. 방어책: ASLR(주소 난수화), DEP/NX(스택/힙 실행 권한 박탈), Stack Canary(스택 변조 감지), SafeSEH.",
              "포맷 스트링 공격: printf(str) 등 포맷 인자 누락 시 %x(메모리 덤프), %n(메모리 주소에 바이트 수 쓰기)을 이용해 관리자 권한 획득.",
              "레이스 컨디션(TOCTOU): 자원 점검 시점과 사용 시점 사이의 시간차를 노려 심볼릭 링크 바꿔치기.",
              "루트킷(Rootkit): ps, netstat, ls 등 시스템 명령어를 변조하거나 커널 모듈(LKM)을 조작하여 프로세스 및 파일 은닉. /proc 디렉토리 전수 검사로 식별."
            ]
          }
        ]
      },
      {
        "title": "PART 02 네트워크 보안 (TCP/IP 구조, L4/L7 공격, 보안장비, 무선보안)",
        "topics": [
          {
            "name": "TCP/IP 구조 및 취약점",
            "points": [
              "TCP 3-Way Handshake: SYN -> SYN/ACK -> ACK. SYN Flooding 공격은 ACK 미회신으로 서버 백로그 큐를 고갈시킴 (SYN Cookie로 방어).",
              "IP 단편화(Fragmentation) 공격: Tiny Fragment(패킷 필터링 우회), TearDrop(오프셋 중첩으로 재조합 크래시 유발), Ping of Death(65535 바이트 초과 ICMP 패킷 전송).",
              "IP/포트 위조 공격: Land Attack(출발지와 목적지 IP/포트를 동일 희생자로 지정), Smurf(ICMP Echo 브로드캐스트 전송), Fraggle(UDP 7/19 포트 이용 증폭).",
              "스텔스 포트 스캔: TCP Half-Open(SYN 스캔), FIN/Null/Xmas 스캔(RFC 793 규약: 열린 포트는 무응답, 닫힌 포트는 RST 응답)."
            ]
          },
          {
            "name": "네트워크 보안 장비 및 터널링 프로토콜",
            "points": [
              "침입차단시스템(방화벽): 패킷 필터링(1세대, 속도 빠름), 애플리케이션 게이트웨이(3세대, 프록시 기반 정밀 검사, 속도 저하), 상태기반 검사(Stateful Inspection, 세션 테이블 기반).",
              "스크린드 서브넷(Screened Subnet): 외부 라우터 - DMZ(웹/메일/DNS 배스천 호스트) - 내부 라우터 - 내부 사설망 3단계 격리 구조.",
              "IPSec: AH(인증/무결성만 제공, NAT 통과 불가), ESP(기밀성/무결성/인증 제공, NAT-T 지원). 전송 모드(페이로드만 보호), 터널 모드(패킷 전체 캡슐화 및 외부 IP 부착).",
              "IKE(Internet Key Exchange): UDP 500 포트 기반, ISAKMP 프레임워크와 디피-헬만 키 교환을 결합하여 SA 및 비밀키 자동 협상.",
              "Snort 룰 구조: [액션] [프로토콜] [출발지IP] [출발지포트] -> [목적지IP] [목적지포트] (msg:\"...\"; content:\"...\"; nocase; sid:고유값;)"
            ]
          },
          {
            "name": "무선 LAN 및 최신 네트워크 위협",
            "points": [
              "무선 암호화: WEP(RC4, IV 24비트 재사용 취약) -> WPA(TKIP) -> WPA2(AES-CCMP 802.11i) -> WPA3(SAE 동등동시인증, 오프라인 사전공격 차단).",
              "애플리케이션 DoS: Slowloris(HTTP 헤더 미완성), RUDY(Content-Length 크게 지정 후 POST 데이터 지연 전송), Slow Read(TCP 윈도우 크기 0 유지).",
              "DNSSEC: DNS 응답에 전자서명(RRSIG, DNSKEY 레코드)을 적용하여 DNS 캐시 포이즈닝 원천 차단."
            ]
          }
        ]
      },
      {
        "title": "PART 03 애플리케이션 보안 (웹 해킹 및 시큐어코딩, DB 보안, 전자상거래)",
        "topics": [
          {
            "name": "웹 취약점 진단 및 시큐어코딩",
            "points": [
              "SQL 인젝션: 파라미터화된 쿼리(PreparedStatement)와 바인딩 변수 사용이 최우선 방어책. Time-Based Blind는 sleep() 등 응답 지연 시간으로 참/거짓 판별.",
              "XSS(Cross-Site Scripting): Stored(DB 저장형), Reflected(URL 반사형), DOM(클라이언트 스크립트 실행). 방어책: HTML Entity 인코딩(&lt; &gt; 치환), HttpOnly 쿠키 플래그 설정.",
              "CSRF(Cross-Site Request Forgery): 로그인된 사용자 브라우저를 유도해 비정상 요청 강제 실행. 방어책: CSRF Token 검증, SameSite 쿠키(Strict/Lax) 설정.",
              "파일 업로드: 화이트리스트 확장자 검증, 파일명 UUID 난수 변경, 업로드 디렉토리 실행 권한(No-Exec) 제거, 웹 루트 외부 격리.",
              "경로 조작(Path Traversal): '../' 디코딩(%2e%2e%2f) 필터링 및 getCanonicalPath()를 통한 디렉토리 화이트리스트 검증."
            ]
          },
          {
            "name": "데이터베이스 보안",
            "points": [
              "DB 접근제어: DAC(테이블 소유자가 GRANT/REVOKE), MAC(보안 등급 기반 강제 통제), RBAC(역할별 권한 매핑).",
              "DB 암호화 방식: API 방식(애플리케이션 수정 필요, 서버 부하 분산), Plug-In 방식(DBMS 엔진 플러그인, SQL 수정 최소), TDE 방식(저장소 파일 레벨 투명 암호화, 인덱스 검색 유지).",
              "DB 감사(Audit): DDL 및 DML 트리거, 네트워크 스니핑 패킷 캡처, DBMS 서버 에이전트 방식을 통한 접속기록 로깅."
            ]
          },
          {
            "name": "전자상거래 보안 및 웹 보안 헤더",
            "points": [
              "SET(Secure Electronic Transaction): 전자서명과 이중 서명(Dual Signature)을 적용하여 상점은 주문 정보만, 카드사는 결제 정보만 열람하도록 보장.",
              "HSTS(Strict-Transport-Security): 브라우저가 첫 접속 후 모든 통신을 오직 HTTPS로만 연결하도록 강제 (SSL Stripping 방어).",
              "CSP(Content-Security-Policy): 스크립트, 이미지 로딩 출처 도메인을 화이트리스트로 제한하여 XSS 및 악성 코드 삽입 차단.",
              "X-Frame-Options: DENY 또는 SAMEORIGIN 설정을 통해 타 사이트의 iframe 프레임 로딩을 차단하여 클릭재킹 방어."
            ]
          }
        ]
      },
      {
        "title": "PART 04 정보보안 일반 (암호학, 접근 통제 모델, 전자서명 및 PKI)",
        "topics": [
          {
            "name": "대칭키 암호 및 블록 운영 모드",
            "points": [
              "대칭키 알고리즘: DES(64비트 블록, 56비트 키, Feistel), AES(128비트 블록, 128/192/256비트 키, SPN 구조), SEED(국산 KISA, 128비트, Feistel), ARIA(국정원, 128비트, SPN), LEA(경량 국산 고속 암호).",
              "블록 운영 모드: ECB(초기화벡터 없음, 평문 패턴 노출, 사용 금지), CBC(IV 필수, 이전 암호문 블록과 XOR 연산, 에러 전파 2블록), CTR(카운터 기반 스트림 암호화, 완벽한 병렬 처리 지원)."
            ]
          },
          {
            "name": "공개키 암호, 해시 함수 및 전자서명",
            "points": [
              "공개키 알고리즘: RSA(소인수분해 난해성), ECC(타원곡선 이산대수 난해성, 256비트로 RSA 3072비트 급 성능), ElGamal(이산대수 문제).",
              "해시 함수 3대 특성: 제1 역상 저항성(H(x)=h에서 x 찾기 불가), 제2 역상 저항성(주어진 x에 대해 H(x)=H(y)인 y 찾기 불가), 충돌 저항성(H(x)=H(y)인 임의의 쌍 (x,y) 찾기 불가).",
              "전자서명: 송신자의 개인키로 서명값을 암호화 생성하고 수신자가 공개키로 검증. 무결성, 인증, 부인방지(Non-repudiation) 보장.",
              "전자봉투(Digital Envelope): 세션키(대칭키)로 본문을 암호화하고, 세션키를 수신자의 공개키로 암호화하여 함께 전송하는 하이브리드 기법.",
              "인증서 상태 검증: CRL(주기적 폐지 목록 배포, 대역폭 부하) -> OCSP(실시간 온라인 인증서 상태 조회)."
            ]
          },
          {
            "name": "보안 모델 및 접근 통제",
            "points": [
              "BLP(Bell-LaPadula) 모델: 기밀성 최우선 군사 모델. No Read Up(상위 등급 읽기 금지), No Write Down(하위 등급 쓰기 금지).",
              "Biba 모델: 무결성 최우선 상업 모델. No Read Down(하위 무결성 읽기 금지), No Write Up(상위 무결성 오염 쓰기 금지).",
              "Clark-Wilson 모델: 잘 형성된 트랜잭션(Well-formed Transaction)과 직무 분리를 통한 기업 데이터 무결성 보장.",
              "만리장성(Chinese Wall / Brewer-Nash): 이해관계 상충(Conflict of Interest) 방지를 위해 사용자의 이전 접근 이력에 따라 동적으로 접근 차단."
            ]
          }
        ]
      },
      {
        "title": "PART 05 정보보안 관리 및 법률 (위험관리, ISMS-P, 관련 법령)",
        "topics": [
          {
            "name": "위험관리 및 업무 연속성 계획 (BCP/DRP)",
            "points": [
              "정량적 위험분석: ALE(연간손실예상액) = SLE(단일손실예상액) × ARO(연간발생빈도).",
              "위험 처리 전략: 위험 감소(통제 적용), 위험 회피(사업 중단/철수), 위험 전가(보험 가입/외주), 위험 수용(DOA 이하 방치).",
              "재해복구 목표: RTO(목표 복구 시간, 허용 최대 다운타임), RPO(목표 복구 시점, 허용 데이터 손실량).",
              "DR 센터 유형: Mirror(실시간 복제, RTO 거의 0, 최고 비용), Hot(수시간 이내 복구), Warm(수일 이내 복구), Cold(수주 이상 소요, 장비 미구비)."
            ]
          },
          {
            "name": "개인정보보호법 및 망법 핵심 규정",
            "points": [
              "고유식별정보 4종: 주민등록번호(예외 없이 암호화 법적 강제), 여권번호, 운전면허번호, 외국인등록번호.",
              "유출 통지 및 신고: 개인정보 유출 확인 시 정당한 사유가 없는 한 72시간 이내에 정보주체 통지 및 개인정보위/KISA에 신고.",
              "과징금 상한: 위반 시 전체 매출액의 3% 이하 부과 (위반행위 무관 매출액 제외 입증 가능 시 제외).",
              "접속기록 보관: 기본 1년 이상 보관 (5만 명 이상 고유식별정보 처리 시 2년 이상 보관), 월 1회 이상 정기 점검.",
              "CISO 지정 및 겸직 금지: 자산총액 1조 원 이상 또는 ISMS 의무대상자 중 중대형 기업은 CISO의 타 직무(CIO, 개발 등) 겸직 법적 절대 금지."
            ]
          }
        ]
      },
      {
        "title": "[특별부록] 2026 이기적 합격 핵심용어 108선 엄선 요약",
        "topics": [
          {
            "name": "핵심용어 108선 엄선 (시스템/네트워크)",
            "points": [
              "ASLR: 메모리 로딩 주소를 무작위화하여 셸코드 실행 주소 고정을 방지하는 기법.",
              "DEP/NX: 스택 및 힙 영역의 실행 권한을 박탈하여 셸코드 구동을 차단하는 기술.",
              "SYN Flooding: 백로그 큐 고갈을 유발하는 L4 DoS로 SYN Cookie 및 백로그 증설로 방어.",
              "Land Attack: 출발지/목적지 IP/포트를 희생자로 조작하여 루프 상태를 유발하는 공격.",
              "TearDrop: IP 단편 오프셋 중첩을 악용하여 패킷 재조합 시 시스템 크래시를 유발.",
              "Slowloris: 불완전한 HTTP 헤더를 장시간 유지하여 웹 서버 연결 자원을 고갈시키는 L7 공격.",
              "WPA3 SAE: 동등동시인증 핸드셰이크를 채택해 오프라인 사전 대입 공격을 차단하는 최신 무선 표준."
            ]
          },
          {
            "name": "핵심용어 108선 엄선 (애플리케이션/암호/법규)",
            "points": [
              "PreparedStatement: 컴파일된 SQL 쿼리에 파라미터를 바인딩하여 SQL Injection을 원천 방어.",
              "HttpOnly: 브라우저 자바스크립트의 document.cookie 접근을 차단하여 XSS 쿠키 탈취를 방지.",
              "HSTS: 모든 연결을 무조건 HTTPS로만 수행하도록 브라우저에 강제하는 보안 헤더.",
              "이중 서명(Dual Signature): SET 프로토콜에서 주문정보와 결제정보를 각각 분리 은닉하는 전자서명.",
              "Biba 모델: No Read Down, No Write Up 원칙으로 데이터 무결성을 보장하는 보안 모델.",
              "DOA(수용가능위험수준): 위험처리 대책 수립의 기준이 되는 조직의 위험 수용한도 척도.",
              "72시간 통지: 개인정보 유출 확인 시 정보주체 및 감독기관에 보고해야 하는 법정 시한."
            ]
          }
        ]
      }
    ]
  }
};

window.INFOSEC_PRACTICAL_DATA = {
  "title": "2026 이기적 정보보안기사 (실기) 50제 & 실무 가이드",
  "description": "2026 이기적 정보보안기사 필기+실기 올인원 실기 편제 기준 1회 단답형 핵심 족보(25제), 2회 서술·실무형 침해사고 분석(25제) 총 50문항 및 실무 요약",
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
    }
  ],
  "summary": {
    "title": "2026 이기적 정보보안기사 실기 핵심 실무 가이드 & 시큐어코딩 (3권 실기서 전편)",
    "sections": [
      {
        "title": "PART 07 실기 단답형 핵심 명령어 및 보안 설정 족보",
        "topics": [
          {
            "name": "리눅스/유닉스 핵심 점검 명령어",
            "points": [
              "find / -perm -4000 -type f: SetUID가 부여된 파일을 검색하여 권한 상승 취약점 점검.",
              "netstat -antp: 활성 소켓, 포트 번호(숫자), TCP 연결 상태, 실행 중인 PID 및 프로그램 확인.",
              "find / -mtime -1: 최근 24시간 이내에 수정(Modify)된 파일 검색 (침해사고 초기 분석).",
              "chattr +i [파일]: root를 포함하여 파일의 수정, 삭제, 이름 변경을 원천 차단(불변 속성).",
              "lastlog: /var/log/lastlog 바이너리 파일을 읽어 계정별 최근 접속 시간과 IP 확인.",
              "sha256sum [파일]: 무결성 검증을 위한 SHA-256 해시값 생성 및 대조."
            ]
          },
          {
            "name": "주요 보안 설정 파라미터",
            "points": [
              "umask 027: 기본 권한 디렉토리 750, 파일 640 생성 설정으로 타인(Other) 접근 차단.",
              "sshd_config: 'PermitRootLogin no' (root 원격 접속 차단), 'PasswordAuthentication no' (공개키 인증 강제).",
              "httpd.conf: 'Options -Indexes' (디렉토리 리스팅 제거), 'ServerTokens Prod' (서버 정보 은닉).",
              "/etc/hosts.allow & hosts.deny: TCP Wrapper 설정 파일. allow 파일이 우선 적용됨.",
              "/etc/login.defs: 'PASS_MAX_DAYS 90' (최대 유효기간), 'PASS_MIN_DAYS 1' (최소 변경주기)."
            ]
          }
        ]
      },
      {
        "title": "PART 08 실무형 침해사고 분석 & 시큐어코딩 47개 핵심",
        "topics": [
          {
            "name": "웹 침해사고 로그 분석 및 Snort 규칙 작성",
            "points": [
              "SQL 인젝션 로그: access.log 내 'UNION SELECT', 'OR 1=1', 'information_schema', 'sleep()' 패턴 분석.",
              "경로 조작(Path Traversal) 로그: '%2e%2e%2f', '../../', 'etc/passwd' 문자열 디코딩 및 탐지.",
              "SSH 무차별 대입 로그: secure 로그 내 동일 IP의 단시간 대량 'Failed password' 연속 이력 식별.",
              "Snort 룰 작성 표준: alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell Detected\"; content:\"cmd.jsp\"; nocase; sid:1000001;)"
            ]
          },
          {
            "name": "SW 개발보안 (시큐어코딩) 47개 보안약점 핵심 가이드",
            "points": [
              "SQL Injection: 파라미터 바인딩을 지원하는 PreparedStatement 사용 (Statement 결합 금지).",
              "XSS 방어: HTML Entity 치환 (&lt;, &gt;, &quot;, &amp;) 및 JSTL escapeXml=\"true\" 설정.",
              "파일 업로드: 화이트리스트 확장자 검증, 난수화된 파일명(UUID) 저장, 업로드 디렉토리 실행(No-Exec) 권한 제거.",
              "안전한 난수 생성: 취약한 java.util.Random 대신 java.security.SecureRandom 클래스 사용.",
              "패스워드 암호화: 고속 해시(MD5/SHA) 단독 사용 금지, PBKDF2/bcrypt/Argon2 기반 솔트 및 키 스트레칭 적용.",
              "입력값 경로 검증: 파일 다운로드 시 ../ 필터링 및 getCanonicalPath()를 통한 디렉토리 격리 검증."
            ]
          }
        ]
      }
    ]
  }
};

window.ISMSP_AUDITOR_DATA = {
  "title": "ISMS-P 인증심사원 실전 결함판정 퀴즈 & 102개 기준 결함사례",
  "description": "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 실전 결함판정 시나리오 퀴즈(총 15문항) 및 102개 전 기준 결함사례 총람",
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
    }
  ],
  "summary": {
    "title": "ISMS-P 102개 인증기준별 핵심 점검 포인트 및 결함도출 총람",
    "sections": [
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
  }
};

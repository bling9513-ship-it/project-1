# -*- coding: utf-8 -*-
"""
summary_notes.py
2026 이기적 정보보안기사 필기+실기 올인원 편제 기준
- 내용별(주제별) 핵심 심층 정리 35선
- 필수 핵심 용어 사전 45선
총 80개의 고밀도 세부 요약 모듈
"""

def get_written_summary():
    items = []

    # =========================================================================
    # 1. 시스템 보안 - 내용별 심층 정리
    # =========================================================================
    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    # =========================================================================
    # 2. 네트워크 보안 - 내용별 심층 정리
    # =========================================================================
    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    # =========================================================================
    # 3. 애플리케이션 보안 - 내용별 심층 정리
    # =========================================================================
    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    # =========================================================================
    # 4. 정보보안 일반 및 암호학 - 내용별 심층 정리
    # =========================================================================
    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    # =========================================================================
    # 5. 정보보안 관리 및 법률 - 내용별 심층 정리
    # =========================================================================
    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    items.append({
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
    })

    # =========================================================================
    # 6. 필수 핵심 용어 사전 45선 (A-Z / 가나다)
    # =========================================================================
    terms = [
        ("ASLR", "Address Space Layout Randomization", "시스템", "프로그램 실행 시마다 스택, 힙, 라이브러리 메모리 주소를 난수화하여 고정된 주소를 노리는 셸코드 실행을 차단하는 메모리 보호 기법."),
        ("DEP / NX", "Data Execution Prevention / No-Execute", "시스템", "스택 및 힙 메모리 영역의 실행 권한을 원천 박탈하여 버퍼에 삽입된 악성 바이트 코드가 구동되지 못하도록 차단하는 기술."),
        ("Stack Canary", "스택 카나리 (스택 가드)", "시스템", "함수의 지역변수와 SFP(복귀주소) 사이에 무작위 난수 카나리 값을 삽입하여, 함수 종료 시 카나리 변조 여부를 검사해 오버플로우를 감지하는 기법."),
        ("TOCTOU", "Time of Check to Time of Use", "시스템", "권한 검사 시점과 실제 자원 사용 시점 사이의 극미한 시간차를 악용하여 심볼릭 링크를 교체해 관리자 권한을 탈취하는 경쟁 조건 취약점."),
        ("Rootkit", "루트킷", "시스템", "시스템 관리자 권한을 획득한 후 침투 사실을 숨기기 위해 ps, ls, netstat 등 명령어를 변조하거나 커널 LKM을 조작하여 프로세스 및 파일을 은닉하는 도구 세트."),
        ("wtmp / utmp", "리눅스 로그인 계정 로그", "시스템", "wtmp는 성공한 로그인/로그아웃/재부팅 전체 누적 이력(last 조회), utmp는 현재 접속 중인 활성 사용자 상태(who/w 조회)를 기록하는 바이너리 로그."),
        ("btmp / lastlog", "접속 실패 및 최종 접속 로그", "시스템", "btmp는 로그인 실패 시도 이력(lastb 조회), lastlog는 각 사용자 계정별 최종 접속 일시 및 출발지 IP(lastlog 조회)를 기록하는 바이너리 로그."),
        ("Sticky Bit", "스티키 비트 (1000)", "시스템", "/tmp 공용 디렉토리에 부여되어 누구나 파일을 생성할 수 있으나, 삭제 및 수정은 오직 해당 파일의 소유자와 root만 가능하도록 제한하는 특수 권한 비트."),
        ("PAM", "Pluggable Authentication Modules", "시스템", "응용프로그램 재컴파일 없이 시스템 인증 정책을 교체할 수 있는 플러그인 모듈 인터페이스 (required, requisite, sufficient, optional 플래그 운영)."),
        ("chattr (+i)", "파일 불변 속성 설정", "시스템", "리눅스 파일에 +i(Immutable) 속성을 부여할 경우 root 권한자라 할지라도 파일의 수정, 삭제, 이름 변경, 링크 생성을 원천 차단하는 명령어."),
        ("SYN Cookie", "신 쿠키", "네트워크", "SYN Flooding 공격 시 서버 메모리 백로그 큐를 소진하지 않고, 클라이언트 연결 정보를 암호화 해시하여 TCP Sequence Number에 인코딩해 회신하는 방어 기법."),
        ("Land Attack", "랜드 어택", "네트워크", "패킷의 출발지 IP/Port와 목적지 IP/Port를 희생자 자신의 IP/Port로 조작하여 자기 자신과 무한 루프 연결을 유발시키는 서비스 거부 공격."),
        ("Smurf Attack", "스머프 어택", "네트워크", "출발지 IP를 희생자 IP로 위조한 후 다이렉트 브로드캐스트 주소로 ICMP Echo Request를 전송하여 네트워크 내 모든 호스트의 응답을 희생자에게 증폭 집중시키는 공격."),
        ("TearDrop", "티어드롭 어택", "네트워크", "IP 패킷 단편화 시 오프셋 값을 인위적으로 중첩·왜곡시켜 수신 호스트가 패킷을 재조합하는 과정에서 크래시 및 재부팅을 유발하는 취약점 공격."),
        ("Slowloris", "슬로로리스", "네트워크", "HTTP 요청 헤더의 끝을 알리는 개행문자(\\r\\n\\r\\n)를 전송하지 않고 불완전한 헤더를 천천히 유지하여 웹 서버의 가용 연결 슬롯을 고갈시키는 L7 DoS 공격."),
        ("RUDY", "R-U-Dead-Yet (Slow HTTP POST)", "네트워크", "HTTP POST 요청 시 Content-Length를 거대하게 설정하고 본문 바이트 데이터를 극도로 느린 속도로 분할 전송하여 서버 연결을 장시간 점유하는 공격."),
        ("IPSec (AH / ESP)", "IP Security Protocol", "네트워크", "네트워크 계층(L3) VPN 표준 프로토콜로, AH는 인증과 무결성만 제공(NAT 불가), ESP는 기밀성(암호화), 무결성, 인증을 모두 제공(NAT-T 지원)."),
        ("IKE", "Internet Key Exchange (UDP 500)", "네트워크", "IPSec에서 양단 호스트 간 보안 결합(SA) 협상 및 대칭 세션키를 Diffie-Hellman 알고리즘으로 안전하게 자동 생성·교환하는 표준 프로토콜."),
        ("WPA3 SAE", "동등동시인증 (SAE Handshake)", "네트워크", "WPA3 무선 LAN 표준에 도입된 상호 인증 프로토콜로, 강력한 암호화 키 교환을 통해 기존 4-Way Handshake의 오프라인 사전 대입 공격을 원천 무력화함."),
        ("DNSSEC", "DNS 보안 확장 프로토콜", "네트워크", "DNS 응답 데이터에 공개키 기반 전자서명(RRSIG)을 부착하여 악의적인 DNS 캐시 포이즈닝 및 도메인 파밍을 방지하는 보안 표준."),
        ("PreparedStatement", "파라미터화된 쿼리 (바인딩 변수)", "애플리케이션", "SQL 쿼리 컴파일 시점에 입력값을 데이터 리터럴로 고정 바인딩하여, 사용자 입력값이 쿼리 문법 구조를 변조하지 못하도록 만드는 SQLi 최우선 방어책."),
        ("Stored XSS", "저장형 크로스사이트 스크립팅", "애플리케이션", "공격자가 삽입한 악성 자바스크립트가 게시판 DB에 영구 저장되어, 해당 글을 조회하는 모든 무고한 사용자의 브라우저에서 자동 실행되는 가장 치명적인 XSS."),
        ("CSRF Token", "크로스사이트 요청 위조 방지 토큰", "애플리케이션", "사용자의 세션마다 서버가 예측 불가능한 난수 토큰을 발급하여 폼 전송 시 검증함으로써, 타 사이트로부터 위조된 비인가 상태 변경 요청을 차단하는 기법."),
        ("SSRF", "Server-Side Request Forgery", "애플리케이션", "웹 서버가 취약한 URL 요청 파라미터를 그대로 처리할 때, 공격자가 서버를 중계 삼아 접근 통제된 내부망 인트라넷이나 클라우드 메타데이터 API를 호출하는 공격."),
        ("HttpOnly", "쿠키 보안 플래그", "애플리케이션", "브라우저 자바스크립트의 document.cookie 객체 접근을 원천 차단하여, XSS 공격이 발생하더라도 세션 하이재킹용 쿠키 탈취를 방지하는 설정."),
        ("SameSite Cookie", "쿠키 전송 범위 제어 속성", "애플리케이션", "Strict(타 사이트 링크 시 쿠키 전송 완전 차단) 또는 Lax(안전한 GET 탐색만 허용)를 설정하여 서드파티 컨텍스트에서의 CSRF 공격을 방어하는 최신 표준."),
        ("HSTS", "HTTP Strict Transport Security", "애플리케이션", "브라우저가 해당 도메인 접속 시 첫 연결부터 모든 통신을 오직 HTTPS로만 강제 연결하도록 지시하여 평문 다운그레이드(SSL Stripping)를 방어하는 헤더."),
        ("CSP", "Content Security Policy", "애플리케이션", "웹 브라우저가 스크립트, 스타일, 이미지 등을 로드하고 실행할 수 있는 신뢰할 수 있는 출처 도메인을 화이트리스트로 지정하여 XSS 및 인젝션을 차단하는 헤더."),
        ("TDE", "Transparent Data Encryption", "애플리케이션", "DBMS 스토리지 파일 레벨에서 자동으로 실시간 암·복호화를 수행하여, 응용프로그램 수정 없이 백업 파일 유출 시 데이터 평문 유출을 방지하는 투명 암호화."),
        ("Dual Signature", "이중 서명 (SET 프로토콜)", "애플리케이션", "전자상거래에서 주문정보 해시와 결제정보 해시를 결합하여 한 번에 전자서명함으로써, 상점은 카드번호를 못 보고 카드사는 주문 품목을 알 수 없게 보장하는 기법."),
        ("Feistel vs SPN", "블록 암호 구조", "암호학", "Feistel은 평문을 좌우 분할하여 스왑하며 암·복호화 구조가 동일(DES, SEED), SPN은 치환(S-Box)과 순열(P-Box)을 반복해 병렬 연산에 최적화(AES, ARIA)."),
        ("AES", "Advanced Encryption Standard", "암호학", "Rijndael 알고리즘 기반 전 세계 표준 대칭키 블록 암호. 128비트 블록 크기, 128/192/256비트 키 길이를 지원하며 고속 하드웨어 연산 지원."),
        ("CTR Mode", "카운터 운영 모드", "암호학", "1씩 증가하는 카운터 값을 블록 암호화한 뒤 평문과 XOR 연산하는 운영 모드로, 완벽한 병렬 처리가 가능하여 최신 고속 보안 통신에서 널리 활용."),
        ("RSA", "소인수분해 기반 공개키 암호", "암호학", "거대한 두 소수의 곱을 구하기는 쉬우나 합성수를 소인수분해하기는 극도로 어렵다는 수학적 난해성을 활용한 공개키 암호 및 전자서명 알고리즘."),
        ("ECC", "타원곡선 암호 (Elliptic Curve)", "암호학", "타원곡선 상의 이산대수 난해성에 기반하여, 256비트의 매우 짧은 키 길이로 RSA 3,072비트와 동등한 안전성을 제공하는 모바일/경량 표준 공개키 암호."),
        ("Collision Resistance", "충돌 저항성", "암호학", "단방향 해시 함수에서 H(x) = H(y)를 만족하는 임의의 서로 다른 두 입력값 쌍 (x, y)를 찾아내는 것이 계산상 불가능해야 한다는 안전성 특성."),
        ("OCSP", "Online Certificate Status Protocol", "암호학", "인증서 폐지 목록(CRL) 파일 전체를 다운로드하지 않고, 단일 인증서의 시리얼 번호로 폐지 여부(Good/Revoked/Unknown)를 실시간 온라인 조회하는 프로토콜."),
        ("Digital Envelope", "전자봉투", "암호학", "대용량 본문은 빠른 대칭 세션키로 암호화하고, 그 세션키만을 수신자의 공개키로 암호화하여 함께 전달하는 안전하고 효율적인 하이브리드 암호 전달 기법."),
        ("PBKDF2 / bcrypt", "패스워드 전용 해시 함수", "암호학", "단방향 해시 시 솔트(Salt)를 추가하고 수만 번의 반복 연산(Key Stretching)을 강제하여 GPU 및 전용 하드웨어를 통한 고속 레인보우 테이블 무차별 대입을 무력화함."),
        ("BLP Model", "Bell-LaPadula (기밀성 모델)", "암호학", "No Read Up(상위 등급 읽기 금지), No Write Down(하위 등급 쓰기 금지) 원칙을 통해 상위 기밀 데이터의 하위 등급 유출을 철저히 차단하는 군사 보안 모델."),
        ("Biba Model", "비바 무결성 모델", "암호학", "No Read Down(하위 무결성 읽기 금지), No Write Up(상위 무결성 쓰기 금지) 원칙을 적용하여 신뢰할 수 없는 오염된 데이터가 상위 시스템으로 유입되는 것을 방지."),
        ("Chinese Wall", "만리장성 모델 (이해관계 상충 방지)", "암호학", "금융 및 컨설팅 기업에서 사용자의 이전 데이터 접근 이력에 따라 이해관계가 상충되는 경쟁사의 기밀 데이터 접근을 동적으로 차단하는 상업 보안 모델."),
        ("ALE / SLE / ARO", "정량적 위험분석 3대 공식", "관리·법률", "SLE(단일손실예상액) = 자산가치 × 노출계수, ALE(연간손실예상액) = SLE × ARO(연간발생빈도). 통제 대책 도입 타당성은 통제 전후 ALE 절감액으로 평가."),
        ("RTO vs RPO", "재해복구 목표 지표", "관리·법률", "RTO(목표 복구 시간)는 재해 발생 후 업무가 정상 복구될 때까지 허용 가능한 최대 다운타임, RPO(목표 복구 시점)는 허용 가능한 최대 데이터 유실 시점."),
        ("72시간 통지 의무", "개인정보 유출 신고 시한", "관리·법률", "개인정보 유출 사고 확인 시 정당한 사유가 없는 한 72시간 이내에 정보주체에게 통지하고, 1천 명 이상 유출 시 개인정보위 또는 KISA에 법적 필수 신고.")
    ]

    for t in terms:
        items.append({
            "id": f"term_{t[0].lower().replace(' ', '_').replace('/', '_')}",
            "type": "term",
            "category": "system" if t[2] == "시스템" else ("network" if t[2] == "네트워크" else ("app" if t[2] == "애플리케이션" else ("crypto" if t[2] == "암호학" else "law"))),
            "category_name": f"{t[2]} 필수 용어",
            "title": f"[용어] {t[0]} ({t[1]})",
            "badge": "필수 용어사전",
            "points": [
                f"<strong>핵심 정의:</strong> {t[3]}"
            ]
        })

    return {
        "title": "2026 이기적 정보보안기사 필기 내용별 심층 요약 & 필수 용어 사전 (총 80선)",
        "items": items
    }

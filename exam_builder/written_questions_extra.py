# -*- coding: utf-8 -*-
"""
written_questions_extra.py
이기적 2026 정보보안기사 필기+실기 올인원 편제 기준
- 3회 필기 최신 기출 복원 모의고사 (50문항: 1~5과목 각 10문항)
- 4회 필기 고난도 심화 모의고사 (50문항: 1~5과목 각 10문항)
총 100문항 추가 (누적 200문항)
"""

def get_extra_written_questions():
    q = []

    # ==========================================
    # [3회] 필기 최신 기출 복원 모의고사 (50문항)
    # ==========================================

    # --- 1과목: 시스템 보안 (Q101 ~ Q110) ---
    q.append({
        "id": "IW3_Q1", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 시스템에서 /etc/shadow 파일의 각 필드 구조 중 세 번째 필드가 의미하는 것으로 가장 올바른 것은?",
        "options": ["최종 패스워드 변경 일자(1970-01-01 이후 일수)", "패스워드 최소 사용 기간(일수)", "패스워드 최대 사용 기간(일수)", "패스워드 만료 경고 기간(일수)", "계정 만료 일자"],
        "answer": 1,
        "explanation": "shadow 파일의 필드 순서는 [사용자명:암호화패스워드:최종변경일:최소사용일수:최대사용일수:경고일수:비활성화일수:계정만료일:예약필드]입니다. 세 번째 필드는 1970년 1월 1일(Epoch)을 기준으로 패스워드를 마지막으로 변경한 날짜의 일수입니다."
    })
    q.append({
        "id": "IW3_Q2", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 PAM(Pluggable Authentication Modules) 설정 파일에서 제어 플래그(Control Flag) 중 해당 모듈의 인증이 실패하더라도 즉시 실패를 반환하지 않고 나머지 모듈들을 끝까지 실행한 후 최종 실패를 반환하는 플래그는?",
        "options": ["required", "requisite", "sufficient", "optional", "include"],
        "answer": 1,
        "explanation": "required는 실패 시 즉시 중단하지 않고 스택 내의 다른 모듈을 끝까지 실행한 후 최종 실패를 반환합니다. 반면 requisite는 실패 시 즉시 나머지 모듈 실행을 중단하고 실패를 반환합니다."
    })
    q.append({
        "id": "IW3_Q3", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "다음 중 버퍼 오버플로우 공격을 방어하기 위해 바이너리 실행 시 스택, 힙, 라이브러리 등의 메모리 주소를 매번 무작위로 변경하여 배치하는 보호 기법은?",
        "options": ["ASLR (Address Space Layout Randomization)", "DEP / NX (Data Execution Prevention)", "Stack Canary", "RELRO (Relocation Read-Only)", "SafeSEH"],
        "answer": 1,
        "explanation": "ASLR은 프로그램이 메모리에 적재될 때마다 스택, 힙, 라이브러리 주소를 난수화하여 공격자가 고정된 셸코드나 라이브러리 함수(RTL) 주소를 점프하지 못하도록 차단하는 기법입니다."
    })
    q.append({
        "id": "IW3_Q4", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "윈도우 운영체제에서 시스템 이벤트 로그 중 사용자의 성공 및 실패 로그온 시도를 기록하는 보안 감사 이벤트 ID로 올바른 것은?",
        "options": ["로그온 성공: 4624, 로그온 실패: 4625", "로그온 성공: 4672, 로그온 실패: 4673", "로그온 성공: 1102, 로그온 실패: 1104", "로그온 성공: 4720, 로그온 실패: 4726", "로그온 성공: 7036, 로그온 실패: 7040"],
        "answer": 1,
        "explanation": "윈도우 Vista/2008 이상에서 로그온 성공 이벤트 ID는 4624, 로그온 실패(브루트포스 탐지 등) 이벤트 ID는 4625입니다. (4720: 계정 생성, 1102: 감사 로그 삭제)"
    })
    q.append({
        "id": "IW3_Q5", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 로그 파일 중 현재 시스템에 로그인한 사용자들의 세션 정보를 담고 있으며 바이너리 형태로 who, w 등의 명령어로 조회되는 로그 파일은?",
        "options": ["/var/run/utmp", "/var/log/wtmp", "/var/log/btmp", "/var/log/lastlog", "/var/log/secure"],
        "answer": 1,
        "explanation": "/var/run/utmp는 현재 시스템에 로그인되어 있는 사용자 정보를 저장하며, /var/log/wtmp는 과거 성공한 모든 로그인/로그아웃 및 재부팅 기록을 누적 저장합니다."
    })
    q.append({
        "id": "IW3_Q6", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 ext2/3/4 파일시스템에서 root 권한을 가진 공격자라도 파일을 임의로 삭제하거나 수정할 수 없도록 속성을 부여하는 명령어로 올바른 것은?",
        "options": ["chattr +i [파일명]", "chattr +a [파일명]", "chmod 000 [파일명]", "setfacl -b [파일명]", "chattr +s [파일명]"],
        "answer": 1,
        "explanation": "chattr +i(immutable) 명령을 설정하면 파일이 읽기 전용으로 잠기며, 슈퍼유저(root)라도 속성을 해제(-i)하기 전에는 파일 삭제, 이름 변경, 수정, 링크 생성이 불가능합니다."
    })
    q.append({
        "id": "IW3_Q7", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 umask 값이 027로 설정되어 있을 때 새로 생성되는 일반 파일과 디렉토리의 기본 권한으로 올바른 것은?",
        "options": ["파일: 640(-rw-r-----), 디렉토리: 750(drwxr-x---)", "파일: 644(-rw-r--r--), 디렉토리: 755(drwxr-xr-x)", "파일: 666(-rw-rw-rw-), 디렉토리: 777(drwxrwxrwx)", "파일: 600(-rw-------), 디렉토리: 700(drwx------)", "파일: 660(-rw-rw----), 디렉토리: 770(drwxrwx---)"],
        "answer": 1,
        "explanation": "기본 파일 최대권한은 666, 디렉토리는 777입니다. umask 027을 적용하면 파일은 666 - 027 = 640(-rw-r-----), 디렉토리는 777 - 027 = 750(drwxr-x---)이 됩니다."
    })
    q.append({
        "id": "IW3_Q8", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "다음 중 레이스 컨디션(Race Condition / TOCTOU) 공격의 원인과 이를 방지하기 위한 보안 조치로 가장 적절한 것은?",
        "options": ["검사 시점(Time of Check)과 사용 시점(Time of Use) 사이의 시간 차이를 이용하므로, 임시 파일 생성 시 fstat(), open(O_CREAT|O_EXCL) 등을 사용하고 심볼릭 링크 생성을 통제한다.", "스택에 저장된 리턴 주소를 덮어쓰므로 스택 카나리를 주입한다.", "포맷 스트링 취약점을 방지하기 위해 printf(str) 대신 printf(\"%s\", str)을 사용한다.", "동적 메모리 해제 후 재참조(Use-After-Free)를 방지하기 위해 free 후 NULL을 대입한다.", "정수 오버플로우를 방지하기 위해 unsigned 변수 대신 signed 변수만 선언한다."],
        "answer": 1,
        "explanation": "TOCTOU 취약점은 자원의 상태를 검사하는 시점과 이를 실제로 사용하는 시점 사이에 공격자가 심볼릭 링크 등을 조작하여 발생합니다. 원자적(Atomic) 파일 생성(O_CREAT|O_EXCL) 및 파일 디스크립터 기반 fstat 검증이 필수입니다."
    })
    q.append({
        "id": "IW3_Q9", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "유닉스/리눅스 시스템에서 프로세스가 백그라운드로 실행되도록 할 때 터미널이 종료되어도 프로세스가 HUP(SIGHUP) 시그널을 무시하고 계속 실행되도록 지원하는 명령어는?",
        "options": ["nohup", "nice", "renice", "kill -9", "bg"],
        "answer": 1,
        "explanation": "nohup(no hang up)은 사용자가 로그아웃하거나 터미널 창을 닫아 발생하는 SIGHUP 시그널을 무시하도록 하여 백그라운드 프로세스가 중단 없이 지속되게 합니다."
    })
    q.append({
        "id": "IW3_Q10", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "윈도우 시스템에서 Active Directory의 인증 프로토콜로 사용되며 티켓(Ticket) 기반으로 인증 및 인가를 수행하는 대표적인 프로토콜은?",
        "options": ["Kerberos", "NTLMv2", "RADIUS", "TACACS+", "LDAP"],
        "answer": 1,
        "explanation": "윈도우 2000 이후 Active Directory 환경의 기본 인증 프로토콜은 커버로스(Kerberos v5)입니다. KDC(AS, TGS)를 통해 TGT 및 서비스 티켓을 발급받아 상호 인증을 수행합니다."
    })

    # --- 2과목: 네트워크 보안 (Q111 ~ Q120) ---
    q.append({
        "id": "IW3_Q11", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "IP 패킷의 헤더 필드 중 패킷이 네트워크 상에서 무한 루프를 도는 것을 방지하기 위해 라우터를 거칠 때마다 1씩 감소하는 8비트 필드는?",
        "options": ["TTL (Time to Live)", "TOS (Type of Service)", "Total Length", "Identification", "Fragment Offset"],
        "answer": 1,
        "explanation": "TTL(Time to Live)은 패킷의 생존 기간(홉 수)을 정의하는 8비트 필드로, 라우터를 통과할 때마다 1씩 차감되며 0이 되면 패킷이 폐기되고 송신지에 ICMP Time Exceeded(Type 11) 메시지가 회신됩니다."
    })
    q.append({
        "id": "IW3_Q12", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "공격자가 출발지 IP 주소와 목적지 IP 주소를 희생자의 IP 주소와 동일하게 위조하여 패킷을 전송함으로써 희생자 스스로에게 응답 패킷을 반복 전송하여 시스템 자원을 고갈시키는 공격은?",
        "options": ["Land Attack", "Smurf Attack", "TearDrop Attack", "SYN Flooding", "Ping of Death"],
        "answer": 1,
        "explanation": "Land 공격은 출발지 IP와 목적지 IP, 출발지 포트와 목적지 포트를 동일하게 조작하여 표적 호스트가 자기 자신에게 루프를 돌며 무한 응답하도록 만들어 과부하를 유발하는 공격입니다."
    })
    q.append({
        "id": "IW3_Q13", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "다음 중 TCP 포트 스캔 기법 중 포트가 닫혀 있을 때만 대상 시스템으로부터 RST/ACK 패킷이 회신되고, 열려 있을 때는 응답이 오지 않는 스텔스(Stealth) 스캔 방식이 아닌 것은?",
        "options": ["TCP Open (Connect) 스캔", "TCP FIN 스캔", "TCP Null 스캔", "TCP Xmas 스캔", "ACK 스캔(방화벽 룰셋 진단용)"],
        "answer": 1,
        "explanation": "TCP Connect(Open) 스캔은 완전한 3-Way Handshake를 수립하므로 시스템 로그에 접속 기록이 명확히 남아 스텔스 스캔이 아닙니다. FIN, Null, Xmas 스캔은 RFC 793 규약의 비정상 플래그 응답(Closed일 때만 RST 회신)을 이용합니다."
    })
    q.append({
        "id": "IW3_Q14", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "IPSec 프로토콜의 두 가지 세부 프로토콜인 AH(Authentication Header)와 ESP(Encapsulating Security Payload)에 대한 설명으로 가장 올바른 것은?",
        "options": ["AH는 인증, 무결성, 재전송 방지를 제공하지만 기밀성은 제공하지 않으며, ESP는 기밀성을 포함하여 인증과 무결성을 모두 제공할 수 있다.", "AH는 기밀성을 제공하고, ESP는 기밀성을 제공하지 않는다.", "AH와 ESP는 모두 기본적으로 페이로드 암호화(기밀성)를 강제한다.", "AH는 NAT 환경(NAT-T)을 완벽하게 지원하지만 ESP는 지원하지 못한다.", "ESP는 전송 모드에서 IP 헤더 전체를 암호화한다."],
        "answer": 1,
        "explanation": "AH는 IP 프로토콜 번호 51번으로 데이터 기밀성(암호화)을 제공하지 않고 인증/무결성만 제공합니다. ESP는 IP 프로토콜 번호 50번으로 대칭키 암호화를 통한 기밀성 및 선택적 인증/무결성을 제공합니다."
    })
    q.append({
        "id": "IW3_Q15", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "DNS 캐시 포이즈닝(Cache Poisoning) 공격을 원천적으로 차단하기 위해 DNS 데이터에 공개키 기반의 전자서명을 적용하여 데이터 무결성을 보장하는 기술은?",
        "options": ["DNSSEC (DNS Security Extensions)", "DoH (DNS over HTTPS)", "DoT (DNS over TLS)", "BGPsec", "mTLS"],
        "answer": 1,
        "explanation": "DNSSEC는 공개키 암호화 방식을 활용해 DNS 응답 데이터(RRset)에 디지털 서명(RRSIG, DNSKEY, DS 레코드)을 첨부하여 위·변조 및 위조된 캐시 주입을 방어하는 확장 표준입니다."
    })
    q.append({
        "id": "IW3_Q16", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "스니핑(Sniffing) 공격에 대한 설명 중 로컬 이더넷 스위치 환경에서 스위치의 MAC 주소 테이블(CAM 테이블) 버퍼를 위조된 MAC 주소로 가득 채워 스위치를 더미 허브(Hub)처럼 동작하게 만드는 공격 기법은?",
        "options": ["Switch Jamming (MAC Flooding)", "ARP Spoofing", "ICMP Redirect", "DHCP Starvation", "DNS Spoofing"],
        "answer": 1,
        "explanation": "스위치 재밍(Switch Jamming 또는 MAC Flooding)은 스위치의 MAC 주소 테이블 용량을 초과시켜 Fail-Open 모드로 전환되게 함으로써 모든 포트로 패킷을 브로드캐스팅(Fail-Safe 미흡)하게 유도하는 공격입니다."
    })
    q.append({
        "id": "IW3_Q17", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "무선 네트워크 보안 표준인 WPA3(Wi-Fi Protected Access 3)에서 사전 공격(Dictionary Attack) 및 무차별 대입 공격을 방어하기 위해 PSK(사전 공유 키) 대신 도입한 키 교환 방식은?",
        "options": ["SAE (Simultaneous Authentication of Equals)", "TKIP (Temporal Key Integrity Protocol)", "CCMP (Counter Mode CBC-MAC Protocol)", "WEP (Wired Equivalent Privacy)", "EAP-TLS"],
        "answer": 1,
        "explanation": "WPA3 개인용(Personal) 표준은 Dragonfly 핸드셰이크 기반의 SAE(동시 동등 인증) 프로토콜을 사용하여 오프라인 딕셔너리 공격을 방어하고 전방향 보안(Forward Secrecy)을 제공합니다."
    })
    q.append({
        "id": "IW3_Q18", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "다음 중 침입탐지시스템(IDS)에서 정상적인 사용자 활동을 침입이나 공격으로 잘못 판단하여 경보를 발생시키는 오류를 뜻하는 용어는?",
        "options": ["False Positive (오탐 / 거짓 양성)", "False Negative (미탐 / 거짓 음성)", "True Positive (정탐 / 참 양성)", "True Negative (정상 식별 / 참 음성)", "Zero-Day Exploit"],
        "answer": 1,
        "explanation": "False Positive(오탐)은 비공격/정상 행위를 공격으로 잘못 판단한 오류이고, False Negative(미탐)은 실제 공격을 탐지하지 못하고 정상으로 통과시킨 오류입니다."
    })
    q.append({
        "id": "IW3_Q19", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "Snort 룰 헤더에서 외부 인터넷의 임의 포트에서 내부 웹서버(192.168.1.100)의 80번 포트로 향하는 모든 TCP 트래픽을 감시하기 위한 룰 헤더 구문으로 가장 올바른 것은?",
        "options": ["alert tcp any any -> 192.168.1.100 80", "alert tcp 192.168.1.100 80 -> any any", "drop ip any any <> 192.168.1.100 80", "pass udp any any -> 192.168.1.100 80", "log tcp 192.168.1.100 any -> any 80"],
        "answer": 1,
        "explanation": "Snort 룰 헤더의 기본 형식은 [Action] [Protocol] [SrcIP] [SrcPort] [Direction] [DstIP] [DstPort]입니다. 따라서 'alert tcp any any -> 192.168.1.100 80'이 정확합니다."
    })
    q.append({
        "id": "IW3_Q20", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "네트워크 접근제어(NAC, Network Access Control) 솔루션의 주요 기능에 해당하지 않는 것은?",
        "options": ["패킷의 페이로드를 실시간 난독화 및 디코딩하여 SQL 인젝션을 원천 차단", "단말기의 무결성 점검 (백신 설치 유무, 최신 보안패치 적용 상태 확인)", "미인증 단말기의 네트워크 격리 및 등록 안내(Captive Portal)", "IP/MAC 주소 바인딩을 통한 비인가 단말 접속 통제", "사용자 역할(RBAC)에 따른 네트워크 VLAN 동적 할당"],
        "answer": 1,
        "explanation": "페이로드를 분석하여 SQL 인젝션 등 웹 공격을 차단하는 것은 웹방화벽(WAF)의 기능입니다. NAC는 단말의 보안 상태 점검, 사용자 인증, 네트워크 접속 통제 및 격리를 담당합니다."
    })

    # --- 3과목: 애플리케이션 보안 (Q121 ~ Q130) ---
    q.append({
        "id": "IW3_Q21", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "SQL 인젝션 공격을 예방하기 위한 소프트웨어 개발보안 조치 중 동적 쿼리 조립을 금지하고 컴파일된 쿼리에 파라미터를 안전하게 바인딩하는 기법은?",
        "options": ["PreparedStatement (파라미터화된 쿼리)", "Statement 사용 및 문자열 결합(+)", "HTML Entity 치환 라이브러리 적용", "클라이언트 자바스크립트 유효성 검증", "X-Frame-Options 헤더 설정"],
        "answer": 1,
        "explanation": "PreparedStatement를 사용하면 쿼리의 문법적 구조가 먼저 컴파일된 후 입력값이 단순한 데이터(리터럴)로 바인딩되므로, 악의적인 SQL 구문이 쿼리 구조를 변조하지 못합니다."
    })
    q.append({
        "id": "IW3_Q22", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "XSS(Cross-Site Scripting) 공격의 3대 유형에 해당하지 않는 것은?",
        "options": ["Blind SQL Injection", "Stored (Persistent) XSS", "Reflected (Non-persistent) XSS", "DOM-based XSS", "Universal XSS (UXSS)"],
        "answer": 1,
        "explanation": "Blind SQL Injection은 SQL 인젝션 공격 유형입니다. XSS 공격은 저장형(Stored), 반사형(Reflected), DOM 기반(DOM-based)으로 분류됩니다."
    })
    q.append({
        "id": "IW3_Q23", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "웹 브라우저에서 document.cookie와 같은 자바스크립트 API를 통해 세션 쿠키를 탈취하지 못하도록 보호하는 HTTP 쿠키 플래그는?",
        "options": ["HttpOnly", "Secure", "SameSite=Strict", "Path=/", "Domain"],
        "answer": 1,
        "explanation": "HttpOnly 플래그가 설정된 쿠키는 브라우저의 클라이언트 스크립트(JavaScript)에서 접근할 수 없게 차단되어, XSS 취약점이 발생하더라도 쿠키 탈취를 방지합니다."
    })
    q.append({
        "id": "IW3_Q24", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "CSRF(Cross-Site Request Forgery) 공격을 방어하기 위한 대책으로 가장 적절한 것은?",
        "options": ["요청마다 서버가 검증하는 예측 불가능한 난수형 CSRF 토큰(Token)을 발급 및 검증하고, SameSite 쿠키 속성을 적용한다.", "클라이언트 화면에 비밀번호를 마스킹 처리한다.", "사용자의 입력 데이터에 SQL 예약어를 필터링한다.", "서버의 응답에 Server 헤더 정보를 숨긴다.", "SSL/TLS 암호화 통신(HTTPS)만 단독으로 적용한다."],
        "answer": 1,
        "explanation": "CSRF는 인증된 피해자의 브라우저 권한을 이용해 비인가 요청을 발생시키는 공격이므로, 예측 불가능한 동적 CSRF 토큰 검증, 재인증 요구, SameSite=Strict/Lax 쿠키 적용이 핵심 대책입니다."
    })
    q.append({
        "id": "IW3_Q25", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "파일 업로드 취약점을 방지하기 위한 소프트웨어 개발보안 3대 수칙으로 가장 올바른 조합은?",
        "options": ["화이트리스트 확장자 검증, 업로드 파일명 난수화(UUID), 업로드 디렉토리의 실행 권한 박탈", "블랙리스트 확장자 검증, 원본 파일명 유지, 업로드 디렉토리 실행 권한 부여", "클라이언트 자바스크립트 검증만 적용, 실행 파일 허용, 홈 디렉토리에 저장", "확장자 대소문자 변환 허용, 업로드 디렉토리 웹 루트(WebRoot) 내 위치, DB 저장 배제", "파일 크기 제한만 10MB로 설정하고 확장자는 무제한 허용"],
        "answer": 1,
        "explanation": "파일 업로드 보안은 1) 허용된 확장자만 명시하는 화이트리스트 검증, 2) 파일명 난수화(UUID) 및 웹 루트 외부 저장, 3) 웹서버 설정에서 해당 디렉토리의 스크립트 실행 권한 제거가 3대 원칙입니다."
    })
    q.append({
        "id": "IW3_Q26", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "아파치(Apache) 웹서버에서 웹 브라우저로 특정 디렉토리에 접근했을 때 index.html 파일이 없더라도 디렉토리 내부의 파일 목록이 화면에 노출되지 않도록 설정하는 지시자는?",
        "options": ["Options -Indexes", "Options +FollowSymLinks", "ServerTokens Prod", "AllowOverride None", "DirectoryIndex disabled"],
        "answer": 1,
        "explanation": "httpd.conf의 Directory 블록에서 'Options -Indexes'를 지정하면 디렉토리 리스팅(Directory Indexing)이 비활성화되어 파일 목록 노출 취약점이 제거됩니다."
    })
    q.append({
        "id": "IW3_Q27", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "이메일 송신자가 도메인 소유자의 승인을 받은 공인된 메일 서버인지 검증하기 위해 DNS TXT 레코드에 공인 IP 주소 목록을 게시하는 이메일 인증 기술은?",
        "options": ["SPF (Sender Policy Framework)", "DKIM (DomainKeys Identified Mail)", "DMARC (Domain-based Message Authentication)", "S/MIME", "PGP"],
        "answer": 1,
        "explanation": "SPF는 DNS의 TXT 레코드에 해당 도메인을 대신해 메일을 발송할 수 있는 공인 IP 주소를 등록하여 메일 발송 서버의 진위 여부를 판별하는 기술입니다."
    })
    q.append({
        "id": "IW3_Q28", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "데이터베이스 암호화 방식 중 DBMS 엔진 내부에서 자체적으로 테이블스페이스나 파일 단위로 데이터를 자동 암·복호화하여 애플리케이션의 쿼리 수정이 전혀 필요 없는 방식은?",
        "options": ["TDE (Transparent Data Encryption)", "API 방식", "Plug-In 방식", "하이브리드 방식", "KMS 방식"],
        "answer": 1,
        "explanation": "TDE(투명한 데이터 암호화)는 DBMS 커널 수준에서 저장소(Datafile, Tablespace)를 암호화하므로 기존 응용프로그램의 소스코드나 SQL 쿼리를 수정할 필요가 없습니다."
    })
    q.append({
        "id": "IW3_Q29", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "SSRF(Server-Side Request Forgery) 공격에 대한 설명으로 가장 올바른 것은?",
        "options": ["공격자가 서버 애플리케이션으로 하여금 공격자가 의도한 내부망 주소나 비인가된 외부 URL로 HTTP/TCP 요청을 보내도록 유도하여 내부 비공개 자원을 탈취하는 공격이다.", "사용자의 브라우저를 속여 의도하지 않은 금융 이체를 발생시키는 공격이다.", "클라이언트 화면에 투명한 iframe을 띄워 클릭을 유도하는 공격이다.", "서버의 메모리 힙 공간을 조작하여 임의 코드를 실행하는 공격이다.", "DB 쿼리의 참/거짓 응답 시간을 지연시키는 공격이다."],
        "answer": 1,
        "explanation": "SSRF는 서버 측에서 외부 자원을 페치(fetch)하는 로직을 악용하여, 방화벽 뒤에 숨겨진 내부 인프라(127.0.0.1, 169.254.169.254 메타데이터 서버 등)에 비인가 요청을 발생시키는 취약점입니다."
    })
    q.append({
        "id": "IW3_Q30", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "전자상거래 보안 프로토콜인 SET(Secure Electronic Transaction)에서 고객의 주문 정보는 상점만 볼 수 있고 고객의 결제 정보(신용카드 번호)는 금융기관만 볼 수 있도록 이중으로 서명하는 기술은?",
        "options": ["이중 서명 (Dual Signature)", "전자 봉투 (Digital Envelope)", "은닉 서명 (Blind Signature)", "다중 서명 (Multi Signature)", "위임 서명 (Proxy Signature)"],
        "answer": 1,
        "explanation": "SET의 이중 서명(Dual Signature)은 주문 정보의 해시값과 결제 정보의 해시값을 결합하여 고객의 개인키로 서명함으로써, 상점에는 결제 정보를 숨기고 금융기관에는 주문 세부 내역을 숨기는 기술입니다."
    })

    # --- 4과목: 정보보안 일반 (Q131 ~ Q140) ---
    q.append({
        "id": "IW3_Q31", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "블록 암호 알고리즘 구조 중 입력을 좌우 반으로 나누어 한쪽에만 라운드 함수를 적용하고 좌우를 교환(Swap)하며, 암호화와 복호화 과정이 동일한 구조는?",
        "options": ["Feistel 구조 (DES 등)", "SPN 구조 (AES, ARIA 등)", "스트림 암호 구조 (RC4)", "공개키 암호 구조 (RSA)", "해시 트리 구조 (Merkle Tree)"],
        "answer": 1,
        "explanation": "Feistel 구조는 데이터를 좌우 블록(L, R)으로 양분하여 라운드를 수행하며, 역원이 존재하지 않아도 복호화가 가능합니다(DES, SEED 등). 반면 SPN은 Substitution-Permutation Network 구조로 전체 블록을 병렬 처리합니다(AES, ARIA)."
    })
    q.append({
        "id": "IW3_Q32", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "미국 표준 블록 암호화 알고리즘인 AES(Advanced Encryption Standard)의 블록 크기와 지원하는 키 길이로 올바른 것은?",
        "options": ["블록 크기: 128비트, 키 길이: 128 / 192 / 256비트", "블록 크기: 64비트, 키 길이: 56비트", "블록 크기: 128비트, 키 길이: 64 / 128비트", "블록 크기: 256비트, 키 길이: 256비트 단독", "블록 크기: 64비트, 키 길이: 128비트"],
        "answer": 1,
        "explanation": "AES(Rijndael)는 블록 크기가 128비트로 고정되어 있으며, 키 길이에 따라 128비트(10라운드), 192비트(12라운드), 256비트(14라운드)를 지원합니다."
    })
    q.append({
        "id": "IW3_Q33", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "블록 암호 운용 모드 중 이전 라운드의 암호문 블록을 현재 평문 블록과 XOR 연산한 후 암호화하며, 초기화 벡터(IV)를 필요로 하는 모드는?",
        "options": ["CBC (Cipher Block Chaining) 모드", "ECB (Electronic Codebook) 모드", "CFB (Cipher Feedback) 모드", "OFB (Output Feedback) 모드", "CTR (Counter) 모드"],
        "answer": 1,
        "explanation": "CBC 모드는 직전 단계의 암호문 블록과 현재 평문 블록을 XOR한 후 암호화 알고리즘을 거칩니다. 첫 블록에는 초기화 벡터(IV)가 사용됩니다."
    })
    q.append({
        "id": "IW3_Q34", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "암호학적 해시 함수의 성질 중 주어진 해시값 h에 대해 H(x) = h를 만족하는 입력값 x를 찾는 것이 계산적으로 불가능해야 함을 의미하는 성질은?",
        "options": ["제1 역상 저항성 (단방향성)", "제2 역상 저항성 (약한 충돌 저항성)", "충돌 저항성 (강한 충돌 저항성)", "눈사태 효과 (Avalanche Effect)", "완전성"],
        "answer": 1,
        "explanation": "제1 역상 저항성(Pre-image Resistance)은 출력값(해시값)이 주어졌을 때 원래의 입력값을 역산하기 불가능해야 한다는 성질(단방향성)입니다."
    })
    q.append({
        "id": "IW3_Q35", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "공개키 인증서 폐기 상태를 실시간으로 확인하기 위해, CRL(인증서 폐기 목록) 다운로드 방식의 시간 지연 및 대역폭 낭비를 개선하여 클라이언트가 인증서 상태를 즉시 질의하는 온라인 프로토콜은?",
        "options": ["OCSP (Online Certificate Status Protocol)", "SCEP (Simple Certificate Enrollment Protocol)", "CMP (Certificate Management Protocol)", "PKCS #11", "X.509 v3"],
        "answer": 1,
        "explanation": "OCSP(RFC 6960)는 인증서의 일련번호를 기반으로 폐기 여부를 실시간(Good, Revoked, Unknown) 질의 및 응답받을 수 있도록 설계된 경량 프로토콜입니다."
    })
    q.append({
        "id": "IW3_Q36", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "보안 모델 중 군사적 보안 요구를 반영하여 기밀성(Confidentiality) 보장을 목적으로 설계되었으며, 단순 보안 규칙(No Read Up)과 *-보안 규칙(No Write Down)을 적용하는 모델은?",
        "options": ["벨-라파둘라 모델 (BLP Model)", "비바 무결성 모델 (Biba Model)", "클락-윌슨 모델 (Clark-Wilson Model)", "만리장성 모델 (Chinese Wall Model)", "만다토리 모델 (MAC Model)"],
        "answer": 1,
        "explanation": "BLP(Bell-LaPadula) 모델은 기밀성을 최우선으로 하며, 상위 등급 문서를 읽을 수 없고(No Read Up) 하위 등급으로 문서를 작성할 수 없는(No Write Down) 규칙을 가집니다."
    })
    q.append({
        "id": "IW3_Q37", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "금융 거래 등에서 이해상충(Conflict of Interest)을 방지하기 위해 사용자가 이전에 접근한 데이터 집합에 따라 다른 경쟁 업체의 데이터에 접근하지 못하도록 동적으로 장벽을 형성하는 보안 모델은?",
        "options": ["만리장성 모델 (Chinese Wall / Brewer-Nash)", "비바 모델 (Biba)", "벨-라파둘라 모델 (BLP)", "접근제어 행렬 (Access Control Matrix)", "격자 모델 (Lattice Model)"],
        "answer": 1,
        "explanation": "차이니즈 월(Chinese Wall, Brewer-Nash) 모델은 주체의 이전 접근 이력을 추적하여 이해상충 관계에 있는 데이터 세그먼트 간의 정보 흐름을 동적으로 차단하는 모델입니다."
    })
    q.append({
        "id": "IW3_Q38", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "정량적 위험 분석에서 단일 손실 예상액(SLE)을 구하는 올바른 공식은?",
        "options": ["SLE = 자산 가치(AV) × 노출 계수(EF)", "SLE = 연간 발생 빈도(ARO) × 자산 가치(AV)", "SLE = 연간 손실 예상액(ALE) / 노출 계수(EF)", "SLE = 자산 가치(AV) - 위험 감소치", "SLE = 위험도 × 취약점 가중치"],
        "answer": 1,
        "explanation": "단일 손실 예상액 SLE(Single Loss Expectancy) = 자산 가치 AV(Asset Value) × 노출 계수 EF(Exposure Factor)입니다. 또한 연간 손실 예상액 ALE = SLE × ARO(연간 발생 빈도)입니다."
    })
    q.append({
        "id": "IW3_Q39", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "재해복구시스템(DRS)의 복구 수준별 센터 유형 중 주 센터와 완전히 동일한 수준의 하드웨어와 실시간 데이터 미러링을 구축하여 재해 발생 시 수 분 내에 서비스 복구가 가능한 방식은?",
        "options": ["Mirror Site (미러 사이트)", "Hot Site (핫 사이트)", "Warm Site (웜 사이트)", "Cold Site (콜드 사이트)", "Mobile Site"],
        "answer": 1,
        "explanation": "미러 사이트는 주 센터와 동일한 시스템을 구축하고 데이터를 실시간 복제(동기식)하여 RTO=0(즉각/수분 이내), RPO=0을 달성하는 최고 비용의 DRS 유형입니다."
    })
    q.append({
        "id": "IW3_Q40", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "전자서명에서 송신자가 메시지를 자신의 개인키로 암호화하고, 수신자가 송신자의 공개키로 복호화함으로써 달성할 수 있는 보안 기능의 조합으로 가장 올바른 것은?",
        "options": ["인증, 무결성, 부인방지", "기밀성, 가용성, 부인방지", "기밀성, 인증, 접근통제", "가용성, 무결성, 확장성", "기밀성, 익명성, 책임추적성"],
        "answer": 1,
        "explanation": "전자서명(송신자 개인키 서명)은 메시지가 송신자에 의해 작성되었음을 입증(인증), 전송 중 변조되지 않았음(무결성), 나중에 발송 사실을 부인할 수 없음(부인방지)을 제공합니다. (기밀성은 수신자의 공개키로 암호화해야 달성됨)"
    })

    # --- 5과목: 정보보안 관리 및 법률 (Q141 ~ Q150) ---
    q.append({
        "id": "IW3_Q41", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 보호법상 원칙적으로 처리가 금지되며 법령의 구체적 위임이나 별도의 명시적 동의가 있어야만 처리할 수 있는 고유식별정보 4가지에 해당하지 않는 것은?",
        "options": ["여권번호", "주민등록번호", "운전면허번호", "외국인등록번호", "신용카드번호"],
        "answer": 5,
        "explanation": "개인정보 보호법 시행령 제19조에 따른 고유식별정보 4가지는 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호입니다. 신용카드번호는 고유식별정보에 해당하지 않습니다."
    })
    q.append({
        "id": "IW3_Q42", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보의 안전성 확보조치 기준에 따라 개인정보취급자가 개인정보처리시스템에 접속하여 개인정보를 처리한 접속기록의 최소 보관 기간에 대한 설명으로 올바른 것은?",
        "options": ["최소 1년 이상 보관하되, 5만 명 이상의 정보주체에 관한 개인정보를 처리하거나 고유식별정보 또는 민감정보를 처리하는 시스템은 2년 이상 보관해야 한다.", "모든 시스템은 예외 없이 3년 이상 보관해야 한다.", "접속기록은 최소 6개월 보관하면 충분하다.", "5만 명 미만 시스템은 접속기록을 보관할 의무가 면제된다.", "접속기록은 5년간 영구 보관해야 한다."],
        "answer": 1,
        "explanation": "안전성 확보조치 기준 제8조에 따라 접속기록은 기본 1년 이상 보관·관리해야 하며, 5만 명 이상 정보주체 개인정보 또는 고유식별정보/민감정보 처리 시스템은 최소 2년 이상 보관해야 합니다."
    })
    q.append({
        "id": "IW3_Q43", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보처리자가 개인정보 유출 사실을 알게 되었을 때 지체 없이 정보주체에게 통지하고 개인정보보호위원회 또는 한국인터넷진흥원(KISA)에 신고해야 하는 법정 기한으로 올바른 것은?",
        "options": ["72시간 이내 (1천 명 이상 유출 시 즉시 신고)", "24시간 이내", "48시간 이내", "5일 이내", "14일 이내"],
        "answer": 1,
        "explanation": "개정 개인정보 보호법 제34조에 따라 개인정보가 유출된 사실을 안 때에는 지체 없이(정당한 사유가 없는 한 72시간 이내) 정보주체에게 통지하고, 1천 명 이상 유출된 경우 전문기관(보호위/KISA)에 신고해야 합니다."
    })
    q.append({
        "id": "IW3_Q44", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "ISMS-P 인증 기준(총 102개)의 3대 영역과 각 영역별 세부 기준 개수로 올바르게 짝지어진 것은?",
        "options": ["1영역 관리체계 수립 및 운영(16개) / 2영역 보호대책 요구사항(64개) / 3영역 개인정보 처리단계별 요구사항(22개)", "1영역 관리체계(20개) / 2영역 기술보안(50개) / 3영역 물리보안(32개)", "1영역 기밀성(30개) / 2영역 무결성(40개) / 3영역 가용성(32개)", "1영역 기본요건(10개) / 2영역 침해대응(70개) / 3영역 개인정보(22개)", "1영역 인적보안(15개) / 2영역 시스템보안(65개) / 3영역 법적준거성(22개)"],
        "answer": 1,
        "explanation": "ISMS-P 인증 기준은 1영역 관리체계 수립 및 운영 16개, 2영역 보호대책 요구사항 64개, 3영역 개인정보 처리단계별 요구사항 22개로 총 102개 기준입니다."
    })
    q.append({
        "id": "IW3_Q45", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "정보통신망법상 정보보호최고책임자(CISO)의 겸직 제한 규정이 적용되는 대기업의 기준으로 올바른 것은?",
        "options": ["자산총액 5조 원 이상이거나, 자산총액 5천억 원 이상이면서 정보보호관리체계(ISMS) 의무대상자인 기업", "직원 수 1,000명 이상인 모든 기업", "자본금 100억 원 이상인 코스닥 상장사", "연간 매출액 1천억 원 이상인 모든 법인", "ISMS 인증을 자율 신청한 모든 중소기업"],
        "answer": 1,
        "explanation": "정보통신망법 제45조의3에 따라 자산총액 5조 원 이상인 정보통신서비스 제공자 또는 자산총액 5천억 원 이상이면서 ISMS 의무대상자인 기업의 CISO는 정보기술(CIO)이나 기타 임원 직무를 겸직할 수 없습니다."
    })
    q.append({
        "id": "IW3_Q46", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 보호법상 개인정보의 파기 의무에 따라 보유기간의 경과, 개인정보의 처리 목적 달성 등 개인정보가 불필요하게 되었을 때 파기해야 하는 기한으로 올바른 것은?",
        "options": ["정당한 사유가 없는 한 불필요하게 된 날로부터 5일 이내", "불필요하게 된 날로부터 10일 이내", "불필요하게 된 날로부터 14일 이내", "불필요하게 된 날로부터 30일 이내", "해당 분기 종료일까지"],
        "answer": 1,
        "explanation": "개인정보 보호법 제21조 및 시행령 제16조에 따라 개인정보가 불필요하게 되었을 때에는 정당한 사유가 없는 한 그로부터 5일 이내에 영구 파기해야 합니다."
    })
    q.append({
        "id": "IW3_Q47", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "정보통신기반 보호법에 따른 주요정보통신기반시설 취약점 분석·평가의 법정 주기로 올바른 것은?",
        "options": ["매년 1회 이상 정기적 실시", "2년에 1회 실시", "3년에 1회 실시", "침해사고 발생 시에만 실시", "반기 1회 실시"],
        "answer": 1,
        "explanation": "정보통신기반 보호법 제9조에 따라 관리기관의 장은 소관 주요정보통신기반시설에 대하여 매년 취약점을 분석·평가하여야 합니다."
    })
    q.append({
        "id": "IW3_Q48", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "전자서명법상 공인전자서명 제도가 폐지된 이후 전자서명의 효력에 관한 원칙으로 가장 올바른 것은?",
        "options": ["전자서명이라는 이유만으로 법적 효력이 부인되지 않으며, 당사자 간의 약정에 따른 전자서명은 서명·날인으로서의 효력을 가진다.", "정부가 인증한 단 1개의 전자서명만 법적 효력을 가진다.", "블록체인 기반의 전자서명만 법적 효력이 인정된다.", "전자서명은 법정에서 서면 증거로서의 효력을 상실하였다.", "금융기관용 공동인증서만 유일한 공적 효력을 인정받는다."],
        "answer": 1,
        "explanation": "2020년 개정 전자서명법에 따라 공인인증서 제도가 폐지되고 다양한 민간 전자서명(카카오, 네이버, 패스 등)이 동일한 법적 효력을 갖게 되었습니다."
    })
    q.append({
        "id": "IW3_Q49", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 보호법상 개인정보 침해 사고로 인하여 정보주체가 입은 손해에 대해 법원이 인정할 수 있는 징벌적 손해배상액의 상한으로 올바른 것은?",
        "options": ["손해액의 5배를 넘지 않는 범위", "손해액의 3배를 넘지 않는 범위", "손해액의 10배를 넘지 않는 범위", "정액 10억 원 한도", "손해액의 2배 범위"],
        "answer": 1,
        "explanation": "개인정보 보호법 제39조 제3항에 따라 개인정보처리자의 고의 또는 중대한 과실로 인하여 개인정보가 분실·도난·유출·위조·변조 또는 훼손된 경우 손해액의 5배를 넘지 않는 범위에서 배상액을 정할 수 있습니다."
    })
    q.append({
        "id": "IW3_Q50", "category": "infosec_written", "exam": 3, "exam_name": "3회 필기 최신 기출 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "클라우드 컴퓨팅 보안 가이드라인에 따라 클라우드 서비스 이용자(고객)와 공급자(CSP) 간의 보안 책임 분무 모델(Shared Responsibility Model)에 관한 설명으로 가장 올바른 것은?",
        "options": ["IaaS 환경에서 물리적 인프라와 하이퍼바이저 보안은 클라우드 사업자가 담당하고, 게스트 OS 패치 및 애플리케이션 보안은 이용자가 담당한다.", "SaaS 환경에서는 고객이 서버 운영체제 패치와 하드웨어 암호화를 담당한다.", "PaaS 환경에서는 고객이 네트워크 스위치와 물리적 데이터센터 경비를 담당한다.", "모든 클라우드 모델에서 데이터 보안의 최종 책임은 전적으로 클라우드 서비스 공급자에게 귀속된다.", "IaaS에서는 이용자가 하이퍼바이저 취약점을 직접 패치해야 한다."],
        "answer": 1,
        "explanation": "IaaS(Infrastructure as a Service) 모델에서는 CSP가 물리 인프라, 전력, 네트워크, 가상화 하이퍼바이저를 책임지며, 고객은 가상머신 내의 게스트 OS, 방화벽 설정, 미들웨어, 애플리케이션, 데이터의 보안을 책임집니다."
    })

    # ==========================================
    # [4회] 필기 고난도 심화 모의고사 (50문항)
    # ==========================================

    # --- 1과목: 시스템 보안 (Q151 ~ Q160) ---
    q.append({
        "id": "IW4_Q1", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 커널의 권한 통제 모델 중 전통적인 임의적 접근통제(DAC)의 한계를 극복하고, 프로세스와 객체마다 보안 컨텍스트(라벨)를 부여하여 강제적 접근통제(MAC)를 구현하는 커널 보안 모듈은?",
        "options": ["SELinux (Security-Enhanced Linux)", "AppArmor", "iptables", "PAM", "Chroot"],
        "answer": 1,
        "explanation": "SELinux는 미국 NSA가 개발한 리눅스 커널용 MAC(강제적 접근통제) 보안 서브시스템으로, 주체(프로세스)와 객체(파일, 소켓 등)에 Type Enforcement 라벨을 부여해 root 권한 탈취 시에도 피해를 격리합니다."
    })
    q.append({
        "id": "IW4_Q2", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 시스템에서 특정 디렉토리에 생성된 파일은 오직 파일의 소유자나 root 관리자만이 삭제 또는 이름 변경을 할 수 있도록 제한하는 특수 권한은?",
        "options": ["Sticky Bit (1000)", "SetUID (4000)", "SetGID (2000)", "Immutable (+i)", "Append Only (+a)"],
        "answer": 1,
        "explanation": "Sticky Bit(권한값 1000, 표기 t)는 /tmp 디렉토리처럼 누구나 쓰기 권한이 있는 공용 디렉토리에서 다른 사용자가 생성한 파일을 타인이 임의로 삭제하거나 이동하지 못하도록 보호합니다."
    })
    q.append({
        "id": "IW4_Q3", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "메모리 보호 기법 중 실행 코드 영역(Text Segment)을 제외한 데이터(Data), 스택(Stack), 힙(Heap) 세그먼트에서 CPU 명령어 실행을 하드웨어적으로 원천 차단하는 기술은?",
        "options": ["DEP / NX (Data Execution Prevention / Never eXecute)", "ASLR", "Stack Shield", "SafeSEH", "Shadow Stack"],
        "answer": 1,
        "explanation": "DEP/NX(No-Execute) 비트는 메모리 영역 중 코드 영역이 아닌 스택이나 힙에 주입된 악의적인 셸코드(Shellcode)가 CPU에 의해 실행되는 것을 하드웨어(CPU NX 비트) 수준에서 차단합니다."
    })
    q.append({
        "id": "IW4_Q4", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 시스템 로그 데몬(rsyslog)의 설정 파일(/etc/rsyslog.conf)에서 시설(Facility)과 심각도(Priority)에 따른 로그 처리 문법 중 'authpriv.* /var/log/secure'의 의미로 올바른 것은?",
        "options": ["개인 인증 및 보안 관련(authpriv) 모든 레벨(*)의 로그를 /var/log/secure 파일에 기록한다.", "인증 실패 로그만 /var/log/secure에 기록한다.", "커널 메시지만 /var/log/secure에 기록한다.", "모든 데몬의 오류 로그를 암호화하여 저장한다.", "원격 로그 서버로만 전송한다."],
        "answer": 1,
        "explanation": "authpriv는 SSH, su, sudo 등 개인 인증 및 보안 인가와 관련된 시설(Facility)이며, .*는 디버그부터 이머전시까지 모든 심각도 레벨의 메시지를 지정된 파일(/var/log/secure)에 저장하라는 의미입니다."
    })
    q.append({
        "id": "IW4_Q5", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스/유닉스 환경에서 시스템 침해 후 공격자가 백도어 프로세스나 네트워크 포트를 숨기기 위해 ps, netstat 등의 시스템 명령어를 변조하거나 커널 모듈을 조작하는 악성 소프트웨어는?",
        "options": ["Rootkit (루트킷)", "Ransomware (랜섬웨어)", "Worm (웜)", "Spyware (스파이웨어)", "Logic Bomb (논리폭탄)"],
        "answer": 1,
        "explanation": "루트킷(Rootkit)은 관리자(root) 권한 획득 후 자신의 존재(프로세스, 파일, 포트, 로그)를 숨기고 지속적인 백도어 접근을 유지하기 위해 시스템 바이너리나 커널 시스템 콜 테이블을 조작하는 은닉형 악성 도구 모음입니다."
    })
    q.append({
        "id": "IW4_Q6", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "윈도우 레지스트리에서 부팅 시 또는 사용자 로그인 시 자동으로 실행되도록 등록된 악성코드를 탐지하기 위해 반드시 점검해야 하는 대표적인 Run 키 경로는?",
        "options": ["HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services\\EventLog", "HKEY_CLASSES_ROOT\\.exe", "HKEY_CURRENT_CONFIG\\System", "HKEY_USERS\\.DEFAULT\\Control Panel"],
        "answer": 1,
        "explanation": "윈도우에서 자동 실행되는 시작 프로그램 및 지속성(Persistence) 백도어는 주로 HKLM 및 HKCU의 Software\\Microsoft\\Windows\\CurrentVersion\\Run(또는 RunOnce) 키에 등록됩니다."
    })
    q.append({
        "id": "IW4_Q7", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "리눅스 crontab 설정에서 매주 월요일 오전 3시 30분에 특정 백업 스크립트(/root/backup.sh)를 정기 실행하도록 지정하는 구문으로 올바른 것은?",
        "options": ["30 3 * * 1 /root/backup.sh", "3 30 * * 1 /root/backup.sh", "* 3 30 * 1 /root/backup.sh", "30 3 1 * * /root/backup.sh", "0 3 30 * * /root/backup.sh"],
        "answer": 1,
        "explanation": "crontab 필드 순서는 [분(0-59) 시(0-23) 일(1-31) 월(1-12) 요일(0-7, 1=월요일)]입니다. 따라서 30분, 3시, 매일, 매월, 월요일(1)인 '30 3 * * 1'이 올바릅니다."
    })
    q.append({
        "id": "IW4_Q8", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "포맷 스트링(Format String) 취약점이 발생하는 원인과 이를 이용한 공격에 대한 설명으로 가장 올바른 것은?",
        "options": ["printf(buf)와 같이 서식 지정자 없이 사용자 입력을 출력 함수의 포맷 인자로 직접 전달할 때 발생하며, %x, %s로 메모리를 훔쳐보거나 %n으로 임의 주소에 값을 쓸 수 있다.", "입력 버퍼의 크기를 초과하여 리턴 주소를 직접 덮어쓰는 공격이다.", "동적 할당된 힙 청크의 메타데이터(fd, bk 포인터)를 조작하는 공격이다.", "커널 권한 상승을 위해 디바이스 드라이버의 IOCTL 인터페이스를 악용하는 공격이다.", "난수 생성기의 시드(seed) 값이 고정되어 발생하는 암호학적 취약점이다."],
        "answer": 1,
        "explanation": "포맷 스트링 취약점은 프로그래머가 서식 문자열(%s 등)을 명시하지 않고 사용자 입력을 직접 printf(input) 형태로 전달할 때 발생하며, 공격자는 %x로 메모리를 유출하거나 %n 지시자로 지정된 메모리 주소에 기록된 바이트 수를 덮어쓸 수 있습니다."
    })
    q.append({
        "id": "IW4_Q9", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "유닉스/리눅스 부팅 단계 중 커널이 메모리에 적재된 후 가장 먼저 실행되어 PID 1번을 부여받고 모든 사용자 공간 프로세스의 부모가 되는 초기화 프로세스는?",
        "options": ["init (또는 systemd)", "swapper (PID 0)", "kthreadd (PID 2)", "bash", "login"],
        "answer": 1,
        "explanation": "리눅스 부팅 과정에서 커널 초기화 완료 후 사용자 공간(User Space)에서 가장 먼저 구동되는 프로세스는 PID 1번인 init(전통적 SysV) 또는 systemd(현대적 리눅스)입니다."
    })
    q.append({
        "id": "IW4_Q10", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 1, "subject_name": "1과목: 시스템 보안",
        "question": "윈도우 운영체제의 BitLocker 기능과 같이 하드웨어 기반으로 암호화 키를 안전하게 보관하고 부팅 무결성을 검증하는 보안 전용 마이크로컨트롤러 칩셋은?",
        "options": ["TPM (Trusted Platform Module)", "HSM (Hardware Security Module)", "UEFI", "Secure Boot", "Intel SGX"],
        "answer": 1,
        "explanation": "TPM(신뢰 플랫폼 모듈)은 메인보드에 탑재되어 암호키 생성, 저장, 측정(PCR), 하드웨어 기반 부팅 무결성 검증을 수행하는 국제 표준 보안 칩입니다."
    })

    # --- 2과목: 네트워크 보안 (Q161 ~ Q170) ---
    q.append({
        "id": "IW4_Q11", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "TCP SYN Flooding 공격을 방어하기 위해 서버가 SYN 수신 시 백로그 큐(Backlog Queue)에 연결 자원을 할당하지 않고, 연결 정보를 인코딩한 특별한 초기 시퀀스 번호(ISN)를 SYN/ACK 패킷에 담아 응답하는 기법은?",
        "options": ["SYN Cookie (SYN 쿠키)", "RST Cookie", "TCP TFO (TCP Fast Open)", "Keep-Alive", "TCP Window Scaling"],
        "answer": 1,
        "explanation": "SYN 쿠키는 서버의 SYN 수신 큐(SYN Backlog) 고갈을 방지하기 위해 클라이언트 IP, 포트, 타임스탬프, 서버 비밀키를 해시하여 SYN/ACK의 Sequence Number로 반환한 후, 최종 ACK가 올 때만 소켓을 생성하는 방어 기법입니다."
    })
    q.append({
        "id": "IW4_Q12", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "스머프(Smurf) 공격과 프래글(Fraggle) 공격이 희생자 호스트를 증폭 공격하기 위해 악용하는 프로토콜의 조합으로 올바른 것은?",
        "options": ["Smurf: ICMP Echo Request, Fraggle: UDP (포트 7번 Echo / 포트 19번 Chargen)", "Smurf: TCP SYN, Fraggle: ICMP", "Smurf: IGMP, Fraggle: SNMP", "Smurf: DNS, Fraggle: NTP", "Smurf: ARP, Fraggle: RARP"],
        "answer": 1,
        "explanation": "Smurf 공격은 출발지를 피해자 IP로 위조한 ICMP Echo Request를 브로드캐스트하여 대량의 ICMP Echo Reply를 유발하며, Fraggle 공격은 이를 UDP Echo(7번) 또는 Chargen(19번) 포트로 수행하는 증폭 공격입니다."
    })
    q.append({
        "id": "IW4_Q13", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "IP 단편화(Fragmentation) 오프셋 값을 고의로 중복되거나 비정상적으로 겹치게(Overlap) 조작하여 수신 시스템이 패킷을 재조합(Reassembly)하는 과정에서 충돌이나 시스템 다운을 유발하는 DoS 공격은?",
        "options": ["TearDrop Attack (티어드롭)", "Land Attack", "Bonk Attack", "Boink Attack", "Ping of Death"],
        "answer": 1,
        "explanation": "TearDrop 공격은 IP 헤더의 Fragment Offset과 Data Length 값을 의도적으로 중첩되게 조작하여 수신측 OS가 재조합 시 메모리 참조 오류로 크래시를 일으키게 하는 취약점 공격입니다."
    })
    q.append({
        "id": "IW4_Q14", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "HTTP 프로토콜의 특성을 악용한 L7 DoS 공격 중 웹서버로 불완전한 HTTP 헤더(끝을 알리는 빈 줄 \\r\\n\\r\\n 미전송)를 전송하고 비정상적인 추가 헤더를 극도로 느리게 지속 전송하여 서버의 동시 연결 스레드를 고갈시키는 공격은?",
        "options": ["Slowloris (Slow HTTP Header DoS)", "Slow HTTP POST (R.U.D.Y)", "Slow HTTP Read DoS", "HTTP GET Flooding", "Hulk DoS"],
        "answer": 1,
        "explanation": "Slowloris는 헤더의 마지막 개행(\\r\\n\\r\\n)을 보내지 않고 수십 초 간격으로 더미 헤더(X-a: b\\r\\n)를 찔끔찔끔 보내어 웹서버의 연결 타임아웃을 연장시키며 가용 스레드/프로세스를 모두 잠식하는 공격입니다."
    })
    q.append({
        "id": "IW4_Q15", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "IPSec 통신에서 보안 연계(SA: Security Association)를 동적으로 협상하고 대칭 암호화 키를 안전하게 교환하기 위해 사용하는 핵심 키 관리 프로토콜은?",
        "options": ["IKE (Internet Key Exchange)", "ISAKMP 단독", "Oakley", "SKEME", "Diffie-Hellman 단독"],
        "answer": 1,
        "explanation": "IKE(UDP 500번/4500번)는 ISAKMP 프레임워크와 Oakley 및 SKEME 키 교환 프로토콜을 결합하여 양 종단 간 암호화 알고리즘, 해시 방식, 키 수명 등을 협상하고 SA를 자동 생성하는 표준 프로토콜입니다."
    })
    q.append({
        "id": "IW4_Q16", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "NTP, DNS, SSDP, Memcached 서버와 같이 응답 크기가 요청 크기에 비해 수십 배에서 수만 배 이상 큰 비연결형(UDP) 서비스를 악용하여 표적 시스템에 대량의 트래픽을 집중시키는 DDoS 공격 유형은?",
        "options": ["DRDoS (Distributed Reflection DoS / 반사 증폭 공격)", "SYN Flooding", "HTTP GET Flooding", "TearDrop", "Ping of Death"],
        "answer": 1,
        "explanation": "DRDoS(분산 반사 서비스 거부)는 출발지 IP를 피해자 IP로 변조한 후 증폭율이 높은 공개 UDP 서버(반사체)들에 질의를 전송하여 피해자에게 막대한 반사 트래픽이 쏟아지게 만드는 공격입니다."
    })
    q.append({
        "id": "IW4_Q17", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "SSL/TLS 통신에서 클라이언트가 하나의 웹서버 IP 주소에서 여러 개의 독립된 도메인(가상 호스트)과 개별 SSL 인증서를 바인딩하여 안전하게 서비스할 수 있도록 확장한 기술은?",
        "options": ["SNI (Server Name Indication)", "ALPN (Application-Layer Protocol Negotiation)", "OCSP Stapling", "HSTS", "Session Ticket"],
        "answer": 1,
        "explanation": "SNI는 클라이언트가 TLS 핸드셰이크의 ClientHello 메시지에 접속하려는 도메인 이름을 포함하여 전송함으로써, 서버가 암호화 핸드셰이크 이전에 적절한 도메인의 SSL 인증서를 제시할 수 있게 하는 확장 규격입니다."
    })
    q.append({
        "id": "IW4_Q18", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "다음 중 침입방지시스템(IPS)과 침입탐지시스템(IDS)의 가장 결정적인 차이점에 대한 설명으로 올바른 것은?",
        "options": ["IDS는 미러링(Out-of-Path) 방식으로 트래픽을 감시하여 침입 탐지 및 알람에 주력하고, IPS는 인라인(In-Line) 경로에 배치되어 탐지 즉시 패킷을 능동적으로 차단(Drop)한다.", "IDS는 시그니처 기반이고, IPS는 이상 탐지 기반이다.", "IDS는 하드웨어 장비이고, IPS는 소프트웨어 프로그램이다.", "IDS는 L7 트래픽만 보고, IPS는 L3 트래픽만 본다.", "IPS는 암호화된 트래픽을 복호화하지 못한다."],
        "answer": 1,
        "explanation": "IDS는 스위치 미러(SPAN) 포트를 통해 패킷 사본을 분석하므로 실시간 차단 능력이 제한적인 반면, IPS는 네트워크 인라인(In-Line) 상에 물리적으로 직렬 연결되어 악성 패킷을 즉각 폐기(Drop)할 수 있습니다."
    })
    q.append({
        "id": "IW4_Q19", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "가상사설망(VPN) 프로토콜 중 OSI 7계층 중 2계층(데이터링크 계층)에서 터널링을 수행하며, 마이크로소프트와 시스코의 기술이 결합되어 IPsec과 함께 자주 사용되는 프로토콜은?",
        "options": ["L2TP (Layer 2 Tunneling Protocol)", "PPTP", "IPSec", "SSL VPN", "WireGuard"],
        "answer": 1,
        "explanation": "L2TP(RFC 2661)는 2계층 터널링 프로토콜로 시스코의 L2F와 MS의 PPTP를 결합한 규격입니다. 자체 암호화 기능이 없으므로 통상 IPSec(L2TP/IPSec)과 결합하여 기밀성을 보장합니다."
    })
    q.append({
        "id": "IW4_Q20", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
        "question": "방화벽의 구축 형태 중 외부 네트워크와 내부 사설망 사이에 양쪽 네트워크와 격리된 완충 지대(DMZ)를 형성하고, 외부 공개 서버(웹, 메일, DNS)들을 배치하는 구성 방식은?",
        "options": ["스크린드 서브넷 게이트웨이 (Screened Subnet)", "스크리닝 라우터 (Screening Router)", "베스천 호스트 단독 구성", "듀얼 홈드 게이트웨이 (Dual-Homed)", "스크린드 호스트 게이트웨이 (Screened Host)"],
        "answer": 1,
        "explanation": "스크린드 서브넷 게이트웨이는 외부 방화벽과 내부 방화벽 사이에 DMZ(완충 지대) 서브넷을 구축하여 공개 서버 침해 시에도 내부 사설망으로의 직접 침투를 차단하는 가장 안전하고 표준적인 방화벽 구성입니다."
    })

    # --- 3과목: 애플리케이션 보안 (Q171 ~ Q180) ---
    q.append({
        "id": "IW4_Q21", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "웹 브라우저의 보안 헤더 중 웹사이트가 HTTPS 프로토콜로만 안전하게 접속되도록 강제하고, 사용자의 평문(HTTP) 접속 시도를 브라우저 내부에서 강제로 HTTPS로 리다이렉트하는 헤더는?",
        "options": ["Strict-Transport-Security (HSTS)", "Content-Security-Policy (CSP)", "X-Content-Type-Options", "X-Frame-Options", "Access-Control-Allow-Origin"],
        "answer": 1,
        "explanation": "HSTS(Strict-Transport-Security) 헤더는 브라우저에게 일정 기간 동안(max-age) 해당 도메인에 접근할 때 평문 HTTP 연결을 일절 시도하지 말고 무조건 HTTPS로만 통신하도록 강제하여 SSL Stripping 공격을 방어합니다."
    })
    q.append({
        "id": "IW4_Q22", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "웹 브라우저에서 실행될 수 있는 자바스크립트, CSS, 이미지 등의 신뢰할 수 있는 출처(Origin)를 서버가 HTTP 응답 헤더로 명시하여 XSS 공격 및 데이터 인젝션을 원천 차단하는 표준 보안 헤더는?",
        "options": ["Content-Security-Policy (CSP)", "X-XSS-Protection", "X-Frame-Options", "Permissions-Policy", "Referrer-Policy"],
        "answer": 1,
        "explanation": "CSP(Content Security Policy)는 웹 페이지에서 로드할 수 있는 스크립트 출처(script-src), 스타일(style-src) 등을 화이트리스트로 제한하고 인라인 스크립트 실행을 금지하여 XSS를 강력하게 방어합니다."
    })
    q.append({
        "id": "IW4_Q23", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "클릭재킹(Clickjacking / UI Redressing) 공격을 방어하기 위해 웹 페이지가 다른 사이트의 <frame>, <iframe>, <object> 내에 삽입되어 렌더링되는 것을 방지하는 HTTP 헤더와 설정값으로 가장 적절한 것은?",
        "options": ["X-Frame-Options: DENY (또는 SAMEORIGIN)", "X-Content-Type-Options: nosniff", "Content-Type: text/html", "Access-Control-Allow-Credentials: true", "Cache-Control: no-cache"],
        "answer": 1,
        "explanation": "X-Frame-Options 헤더를 DENY(어디서도 프레임 삽입 불가) 또는 SAMEORIGIN(동일 출처에서만 허용)으로 지정하면 투명한 iframe을 이용한 클릭재킹을 방어할 수 있습니다."
    })
    q.append({
        "id": "IW4_Q24", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "서버 측 템플릿 엔진(Jinja2, Thymeleaf, Freemarker 등)에 사용자의 악의적인 입력값이 검증 없이 전달되어 서버 측에서 임의 파이썬/자바 코드가 원격으로 실행되는 취약점은?",
        "options": ["SSTI (Server-Side Template Injection)", "CSRF", "XSS", "IDOR (Insecure Direct Object Reference)", "Open Redirect"],
        "answer": 1,
        "explanation": "SSTI(서버 사이드 템플릿 인젝션)는 {{7*7}}과 같은 템플릿 표현식이 서버 측에서 평가되어 최종적으로 원격 코드 실행(RCE)으로 이어지는 고위험 취약점입니다."
    })
    q.append({
        "id": "IW4_Q25", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "자바(Java) 시큐어코딩에서 파일 다운로드 취약점(경로 조작 / Directory Traversal)을 방어하기 위해 사용하는 안전한 경로 정규화 및 검증 메서드는?",
        "options": ["File.getCanonicalPath() 및 허용된 루트 디렉토리 시작(startsWith) 검증", "File.getAbsolutePath() 단독 사용", "String.replace(\"../\", \"\") 1회 치환", "File.getName()만 확인", "URLEncoder.encode()"],
        "answer": 1,
        "explanation": "단순 문자열 치환(..././)은 우회될 수 있으므로, getCanonicalPath()를 사용하여 파일 시스템의 절대 정규 경로를 구한 후, 허용된 루트 디렉토리 경로로 시작하는지(startsWith) 엄격히 검증해야 합니다."
    })
    q.append({
        "id": "IW4_Q26", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "웹 애플리케이션의 인증 및 인가에 널리 사용되는 JWT(JSON Web Token)의 3대 구성 요소로 올바르게 나열된 것은?",
        "options": ["Header, Payload, Signature", "Header, Body, Hash", "Metadata, Claims, Certificate", "Issuer, Subject, Key", "Alg, Claims, MAC"],
        "answer": 1,
        "explanation": "JWT는 마침표(.)로 구분되는 Header(알고리즘 및 토큰 타입), Payload(클레임/사용자 데이터), Signature(비밀키로 서명된 무결성 검증값) 3단계 구조로 구성됩니다."
    })
    q.append({
        "id": "IW4_Q27", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "웹 세션 하이재킹(Session Hijacking) 공격 중 공격자가 사전에 발급받은 세션 ID를 희생자에게 주입한 후, 희생자가 해당 세션 ID로 로그인하면 공격자가 그 세션 권한을 획득하는 공격은?",
        "options": ["Session Fixation (세션 고정 공격)", "Session Sniffing", "Session Prediction", "Cross-Site Scripting", "Brute Force"],
        "answer": 1,
        "explanation": "세션 고정(Session Fixation) 공격은 로그인 전 발급된 세션 ID를 로그인 성공 후에도 재사용할 때 발생하므로, 로그인 성공 시 반드시 기존 세션을 파기하고 새로운 세션 ID를 재생성(session.invalidate)해야 합니다."
    })
    q.append({
        "id": "IW4_Q28", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "데이터베이스 보안에서 추론(Inference) 공격을 방지하기 위한 보안 통제 기법에 해당하지 않는 것은?",
        "options": ["동일 쿼리의 무제한 반복 실행 허용 및 응답 시간 단축", "쿼리 결과의 소규모 셀(Small Cell) 억제 (데이터 수가 적을 때 결과 은닉)", "데이터 교란(Perturbation) 및 난수 노이즈 추가", "다중 레벨 보안(MLS) 기반의 뷰(View) 분리", "사용자별 누적 질의 감사 로그 추적"],
        "answer": 1,
        "explanation": "추론 공격은 비인가자가 여러 합법적 통계 질의를 조합하여 민감한 개인 정보를 유추하는 것이므로, 소규모 집합 결과 은닉, 노이즈 추가, 감사 추적이 필요합니다. 무제한 질의 허용은 추론 공격을 용이하게 만듭니다."
    })
    q.append({
        "id": "IW4_Q29", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "이메일 보안 표준 중 송신자의 개인키로 메일 본문과 첨부파일에 디지털 서명을 첨부하고, 수신자의 공개키로 암호화하여 기밀성, 무결성, 인증, 부인방지를 제공하는 표준은?",
        "options": ["S/MIME (Secure/Multipurpose Internet Mail Extensions)", "SMTP", "POP3", "IMAP4", "SPF"],
        "answer": 1,
        "explanation": "S/MIME은 X.509 공개키 인증서를 기반으로 MIME 데이터에 암호화 및 디지털 서명을 적용하여 이메일의 4대 보안 목표(기밀성, 무결성, 인증, 부인방지)를 모두 제공하는 IETF 표준입니다."
    })
    q.append({
        "id": "IW4_Q30", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
        "question": "Nginx 웹서버 설정에서 HTTP 응답 헤더에 Nginx의 상세 버전 정보(예: nginx/1.18.0)가 노출되지 않도록 차단하는 지시자는?",
        "options": ["server_tokens off;", "ServerTokens Prod;", "hide_server_version on;", "expose_php off;", "version_display off;"],
        "answer": 1,
        "explanation": "Nginx에서는 nginx.conf의 http 블록에 'server_tokens off;'를 설정하면 Server 응답 헤더에서 세부 버전 번호가 제거되고 'Server: nginx'만 노출됩니다. (ServerTokens Prod는 Apache 지시자)"
    })

    # --- 4과목: 정보보안 일반 (Q181 ~ Q190) ---
    q.append({
        "id": "IW4_Q31", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "RSA 공개키 암호 알고리즘의 안전성 기반이 되는 수학적 난제와 타원곡선 암호(ECC)의 안전성 기반이 되는 수학적 난제의 조합으로 올바른 것은?",
        "options": ["RSA: 큰 정수의 소인수분해 난제 / ECC: 타원곡선 이산대수 난제(ECDLP)", "RSA: 이산대수 난제 / ECC: 소인수분해 난제", "RSA: 배낭 문제(Knapsack) / ECC: 격자 난제(Lattice)", "RSA: 양자 얽힘 / ECC: 해시 충돌", "RSA: 합동식 난제 / ECC: 모듈러 거듭제곱 난제"],
        "answer": 1,
        "explanation": "RSA는 두 개의 매우 큰 소수의 곱을 소인수분해하는 수학적 어려움에 기반하고, ECC는 타원곡선 군 위에서의 이산대수 문제(ECDLP)의 난해성에 기반하여 256비트 키로도 RSA 3072비트 급의 보안성을 제공합니다."
    })
    q.append({
        "id": "IW4_Q32", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "대한민국 국가 표준 블록 암호 알고리즘 중 1999년 KISA가 개발한 Feistel 구조의 128비트 블록 암호 알고리즘은?",
        "options": ["SEED", "ARIA", "HIGHT", "LEA", "DES"],
        "answer": 1,
        "explanation": "SEED는 1999년 한국인터넷진흥원(KISA)과 전자통신연구원(ETRI)이 개발한 128비트 블록, 128비트 키 크기의 Feistel 구조 국가 표준 암호 알고리즘입니다. (ARIA는 2004년 개발된 SPN 구조)"
    })
    q.append({
        "id": "IW4_Q33", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "블록 암호 운용 모드 중 카운터(Counter) 값을 블록 암호화한 후 평문 블록과 XOR하여 암호문을 생성하며, 1비트 에러가 다른 블록으로 전파되지 않고 병렬 처리가 가능한 모드는?",
        "options": ["CTR (Counter) 모드", "CBC 모드", "ECB 모드", "CFB 모드", "OFB 모드"],
        "answer": 1,
        "explanation": "CTR 모드는 카운터를 암호화한 키 스트림을 평문과 XOR하므로 스트림 암호처럼 동작하며, 블록 간 종속성이 없어 완전한 병렬 처리가 가능하고 에러 전파가 발생하지 않습니다."
    })
    q.append({
        "id": "IW4_Q34", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "비바(Biba) 무결성 모델의 두 가지 핵심 접근 통제 원칙으로 올바르게 짝지어진 것은?",
        "options": ["단순 무결성 규칙(No Read Down) / *-무결성 규칙(No Write Up)", "단순 보안 규칙(No Read Up) / *-보안 규칙(No Write Down)", "No Read Down / No Write Down", "No Read Up / No Write Up", "자유로운 읽기 / 엄격한 쓰기 통제"],
        "answer": 1,
        "explanation": "비바(Biba) 모델은 무결성을 보호하기 위해 설계되었으며, 하위 무결성 등급의 데이터를 읽을 수 없고(No Read Down, 오염 방지), 상위 무결성 등급으로 데이터를 쓸 수 없는(No Write Up) 규칙을 적용합니다."
    })
    q.append({
        "id": "IW4_Q35", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "접근 통제 보안 정책 중 중앙 관리자가 시스템의 모든 자원과 사용자에 대해 사전에 정의된 규칙(Rule)이나 역할(Role)에 따라 일괄적으로 접근 권한을 결정하며, 개별 소유자가 권한을 변경할 수 없는 정책은?",
        "options": ["강제적 접근 통제 (MAC / Mandatory Access Control)", "임의적 접근 통제 (DAC)", "사용자 정의 접근 통제", "신원 기반 접근 통제 (IBAC)", "접근 제어 목록 (ACL 단독)"],
        "answer": 1,
        "explanation": "강제적 접근 통제(MAC)는 보안 레이블과 관리자 보안 정책에 의해 시스템이 접근을 강제하며, 파일 소유자라 할지라도 임의로 접근 권한을 부여하거나 변경할 수 없습니다."
    })
    q.append({
        "id": "IW4_Q36", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "비즈니스 연속성 계획(BCP) 수립 시 업무 중단 시점부터 업무가 정상 수준으로 복구되기까지 허용되는 최대 시간을 의미하는 지표는?",
        "options": ["RTO (Recovery Time Objective / 복구 목표 시간)", "RPO (Recovery Point Objective / 복구 목표 시점)", "MTBF (Mean Time Between Failures)", "MTTR (Mean Time to Repair)", "BIA (Business Impact Analysis)"],
        "answer": 1,
        "explanation": "RTO(복구 목표 시간)는 재해 발생 후 비즈니스 기능이 복구되어 재개될 때까지 허용되는 최대 시간 한계이며, RPO(복구 목표 시점)는 복구 시 허용 가능한 데이터 손실 허용 시점을 뜻합니다."
    })
    q.append({
        "id": "IW4_Q37", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "공개키 기반 구조(PKI)에서 사용자에게 인증서를 발급하고 서명하는 주체(CA)와, 사용자의 신원을 직접 확인하고 인증서 발급 신청을 접수받아 CA에 전달하는 등록 주체(RA)의 역할 분담으로 올바른 것은?",
        "options": ["CA는 인증서 발행 및 폐기(서명)를 담당하고, RA는 사용자의 대면 신원 확인 및 등록 심사를 담당한다.", "RA가 인증서의 개인키를 직접 생성하여 보관한다.", "CA는 웹 브라우저이고, RA는 DNS 서버이다.", "사용자는 항상 CA와만 직접 통신하며 RA는 감사업무만 수행한다.", "인증서 폐기 목록(CRL)은 RA가 직접 서명하여 배포한다."],
        "answer": 1,
        "explanation": "인증기관(CA)은 인증서의 발행, 서명, 폐기(CRL 생성)를 수행하는 핵심 발급 기관이며, 등록기관(RA)은 사용자의 신원 검증, 등록 접수 등 행정적 절차를 대행합니다."
    })
    q.append({
        "id": "IW4_Q38", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "비대칭 암호와 대칭 암호의 장점을 결합하여, 대량의 평문 데이터는 고속 대칭키로 암호화하고, 그 대칭키는 수신자의 공개키로 암호화하여 함께 전송하는 기법은?",
        "options": ["전자 봉투 (Digital Envelope)", "전자 서명 (Digital Signature)", "블록체인 (Blockchain)", "영지식 증명 (Zero-Knowledge Proof)", "동형 암호 (Homomorphic Encryption)"],
        "answer": 1,
        "explanation": "전자 봉투(Digital Envelope)는 세션키(대칭키)로 메시지를 고속 암호화하고, 그 세션키를 수신자의 공개키로 암호화하여 전송함으로써 속도와 키 분배 편의성을 동시에 달성하는 하이브리드 암호 기법입니다."
    })
    q.append({
        "id": "IW4_Q39", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "위험 관리 전략 중 발생 가능성이 낮으나 피해 규모가 매우 큰 위험에 대해 보험 가입이나 전문 업체 위탁을 통해 손실 책임을 제3자에게 넘기는 방식은?",
        "options": ["위험 전가 (Risk Transfer)", "위험 회피 (Risk Avoidance)", "위험 감소 (Risk Reduction)", "위험 수용 (Risk Acceptance)", "위험 무시 (Risk Ignorance)"],
        "answer": 1,
        "explanation": "위험 전가(Risk Transfer)는 보안 보험 가입, 아웃소싱 계약 등을 통해 위험으로 인한 재정적 손실 책임을 외부 기관에 이전하는 전략입니다."
    })
    q.append({
        "id": "IW4_Q40", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
        "question": "패스워드 기반 키 유도 함수(KDF) 중 레인보우 테이블 공격 및 GPU 기반 병렬 크래킹을 무력화하기 위해 솔트(Salt)와 함께 수만 번 이상의 해시 반복(키 스트레칭)을 표준화한 규격은?",
        "options": ["PBKDF2 (PKCS #5 v2.0)", "MD5 단독", "SHA-1 단독", "DES-Crypt", "CRC32"],
        "answer": 1,
        "explanation": "PBKDF2는 솔트(Salt)를 추가하고 의도적으로 수만 번 이상의 HMAC 반복 연산(Iteration Count)을 거치게 하여 GPU 크래커나 레인보우 테이블 공격을 방어하는 표준 키 유도 함수입니다."
    })

    # --- 5과목: 정보보안 관리 및 법률 (Q191 ~ Q200) ---
    q.append({
        "id": "IW4_Q41", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 보호법상 정보주체의 동의 없이도 개인정보를 수집·이용할 수 있는 합법적 요건(제15조 제1항)에 해당하지 않는 것은?",
        "options": ["사업자의 영업 이익 극대화를 위해 빅데이터 분석이 반드시 필요한 경우", "법률에 특별한 규정이 있거나 법령상 의무를 준수하기 위하여 불가피한 경우", "공공기관이 법령 등에서 정하는 소관 업무의 수행을 위하여 불가피한 경우", "정보주체와 체결한 계약의 체결 및 이행을 위하여 불가피하게 필요한 경우", "명백히 정보주체 또는 제3자의 급박한 생명, 신체, 재산의 이익을 위하여 필요하다고 인정되는 경우"],
        "answer": 1,
        "explanation": "단순한 영업 이익 증대나 마케팅 목적은 법정 동의 면제 사유가 아니며, 반드시 정보주체의 사전 명시적 동의를 받아야 합니다."
    })
    q.append({
        "id": "IW4_Q42", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보처리자가 개인정보의 안전성 확보조치 기준에 따라 비밀번호를 저장할 때 적용해야 하는 암호화 조치로 올바른 것은?",
        "options": ["복호화되지 않는 일방향 암호화(해시 함수 + 솔트)를 적용하여 저장해야 한다.", "양방향 대칭키(AES)로 암호화해야 한다.", "공개키(RSA)로 암호화하여 저장해야 한다.", "평문으로 저장하되 접근 권한만 차단하면 된다.", "클라이언트에서 마스킹만 적용하면 된다."],
        "answer": 1,
        "explanation": "안전성 확보조치 기준 제7조에 따라 비밀번호는 관리자라 할지라도 원본을 알 수 없도록 안전한 일방향 암호화(One-Way Hash with Salt)를 적용하여 저장해야 합니다."
    })
    q.append({
        "id": "IW4_Q43", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 보호법상 개인정보 영향평가(PIA)를 의무적으로 수행해야 하는 대상 기준으로 올바른 것은?",
        "options": ["50만 명 이상의 고유식별정보 또는 민감정보를 처리하거나, 500만 명 이상의 정보주체 개인정보를 구축·운용하는 공공기관", "모든 민간 기업", "연 매출 100억 원 이상 기업", "상장된 모든 금융기관", "직원 수 50인 이상인 모든 공공기관"],
        "answer": 1,
        "explanation": "개인정보 영향평가는 공공기관을 대상으로 의무화되어 있으며, 50만 명 이상의 민감정보/고유식별정보 처리 시스템 또는 500만 명 이상의 개인정보 연계·구축 시스템 등이 법정 의무 대상입니다."
    })
    q.append({
        "id": "IW4_Q44", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "정보통신망법상 침해사고가 발생한 정보통신서비스 제공자가 과학기술정보통신부장관 또는 한국인터넷진흥원(KISA)에 신고해야 하는 기한으로 올바른 것은?",
        "options": ["침해사고 발생을 안 때 즉시 (24시간 이내)", "72시간 이내", "5일 이내", "10일 이내", "해당 월말까지"],
        "answer": 1,
        "explanation": "정보통신망 이용촉진 및 정보보호 등에 관한 법률 제48조의3에 따라 정보통신서비스 제공자는 침해사고가 발생하였을 때에는 즉시(안 때로부터 24시간 이내) 과기정통부 또는 KISA에 신고하여야 합니다."
    })
    q.append({
        "id": "IW4_Q45", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "전자금융거래법상 전자금융사고(해킹, 전산장애 등)로 인해 이용자에게 손해가 발생한 경우 금융회사 또는 전자금융업자의 배상 책임에 관한 원칙으로 올바른 것은?",
        "options": ["금융회사 등은 원칙적으로 무과실 책임을 부담하며, 이용자의 고의나 중대한 과실이 입증된 경우에만 책임의 전부 또는 일부를 면할 수 있다.", "이용자가 금융회사의 고의를 직접 입증해야만 배상받을 수 있다.", "모든 사고는 국가가 전액 배상한다.", "금융회사는 일체 면책된다.", "배상 한도는 1인당 100만 원으로 제한된다."],
        "answer": 1,
        "explanation": "전자금융거래법 제9조에 따라 금융회사 및 전자금융업자는 무과실 손해배상 책임을 지며, 이용자에게 고의나 중과실(비밀번호 누설 등)이 있음을 금융회사가 직접 입증하지 못하면 책임을 면할 수 없습니다."
    })
    q.append({
        "id": "IW4_Q46", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "ISMS-P 인증 제도에서 인증의 유효기간과 매년 받아야 하는 사후 심사에 대한 설명으로 올바른 것은?",
        "options": ["인증 유효기간은 3년이며, 유효기간 중 매년 1회 이상 사후심사를 받아야 한다.", "유효기간은 1년이며, 매년 최초심사를 재수행한다.", "유효기간은 5년이며 사후심사는 생략된다.", "유효기간은 2년이며 사후심사는 격년으로 받는다.", "유효기간은 영구적이며 결함 발견 시에만 심사한다."],
        "answer": 1,
        "explanation": "ISMS 및 ISMS-P 인증의 유효기간은 발급일로부터 3년이며, 인증 취득 기업은 인증 유효성을 지속적으로 유지하기 위해 매년 1회 이상 사후심사를 받아야 합니다."
    })
    q.append({
        "id": "IW4_Q47", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 보호법상 정보주체의 동의 획득 시 14세 미만 아동의 개인정보를 처리하기 위해 법정대리인의 동의를 받아야 하는 최소 정보는?",
        "options": ["법정대리인의 성명, 연락처 등 동의를 받기 위해 필요한 최소한의 정보", "법정대리인의 주민등록번호 및 신용카드 정보", "법정대리인의 직장 주소 및 연봉 정보", "아동의 학교 및 담임교사 확인서", "가족관계증명서 원본 제출 필수"],
        "answer": 1,
        "explanation": "개인정보 보호법 제22조의2에 따라 14세 미만 아동의 개인정보를 처리할 때에는 그 법정대리인의 동의를 받아야 하며, 법정대리인의 동의를 받기 위하여 필요한 최소한의 정보(성명, 연락처 등)는 아동으로부터 직접 수집할 수 있습니다."
    })
    q.append({
        "id": "IW4_Q48", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "정보보호 및 개인정보보호 관리체계(ISMS-P) 구축 시 최고경영진을 위원장으로 구성하여 정보보호 정책 및 예산을 심의·의결하는 기구는?",
        "options": ["정보보호(보안)위원회", "인사위원회", "노사협의회", "준법지원팀", "감사위원회"],
        "answer": 1,
        "explanation": "ISMS-P 기준 1.1.1(경영진의 참여)에 따라 조직은 최고경영진, CISO, CPO 및 주요 부서장이 참여하는 '정보보호위원회'를 구성하고 정기적으로 회의를 개최하여 정책과 예산을 의결해야 합니다."
    })
    q.append({
        "id": "IW4_Q49", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 보호법상 가명정보(Pseudonymous Data)의 처리에 관한 설명으로 가장 올바른 것은?",
        "options": ["통계작성, 과학적 연구, 공익적 기록보존 등의 목적으로 정보주체의 동의 없이 가명정보를 처리할 수 있다.", "가명정보는 특정 개인을 알아볼 수 있으므로 어떠한 경우에도 동의 없이 처리할 수 없다.", "가명정보는 추가 정보와 결합하여 특정 개인을 재식별하는 행위가 전면 허용된다.", "가명정보를 처리할 때에는 안전성 확보조치를 이행할 필요가 없다.", "가명정보는 해외 제3자에게 자유롭게 매매할 수 있다."],
        "answer": 1,
        "explanation": "개인정보 보호법 제28조의2에 따라 가명정보는 통계작성, 과학적 연구, 공익적 기록보존 등의 목적으로 정보주체의 동의 없이 안전하게 결합 및 처리될 수 있으며, 재식별은 엄격히 금지됩니다."
    })
    q.append({
        "id": "IW4_Q50", "category": "infosec_written", "exam": 4, "exam_name": "4회 필기 고난도 심화 모의고사",
        "subject_id": 5, "subject_name": "5과목: 정보보안 관리 및 법률",
        "question": "개인정보 유출 사고 발생 시 개인정보보호위원회가 부과할 수 있는 과징금의 상한 기준(개정 개인정보 보호법)으로 올바른 것은?",
        "options": ["전체 매출액의 100분의 3(3%) 이하 (위반행위와 관련 없는 매출액 제외)", "위반행위 관련 매출액의 100분의 3 이하", "정액 5억 원 이하", "전체 매출액의 100분의 10 이하", "연간 영업이익의 100분의 5 이하"],
        "answer": 1,
        "explanation": "2023년 개정 개인정보 보호법 제64조의2에 따라 과징금 부과 기준이 유럽 GDPR 수준으로 강화되어 '전체 매출액의 3% 이하'로 변경되었으며, 사업자가 관련 없는 매출액을 소명할 경우 이를 제외하고 산정합니다."
    })

    return q

// infosec_exam_data.js
// 정보보안기사(필기), 정보보안기사(실기), ISMS-P 인증심사원 실전 기출/결함판정 문제 및 과목별 심층 요약 데이터셋

window.INFOSEC_WRITTEN_DATA = {
  "name": "정보보안기사 (필기)",
  "badge": "국가기술자격",
  "desc": "시스템·네트워크·애플리케이션·정보보안일반·법규 5대 전 과목 핵심 기출 모의고사 및 상세 해설",
  "subjects": [
    {
      "id": 1,
      "name": "1과목: 시스템 보안"
    },
    {
      "id": 2,
      "name": "2과목: 네트워크 보안"
    },
    {
      "id": 3,
      "name": "3과목: 애플리케이션 보안"
    },
    {
      "id": 4,
      "name": "4과목: 정보보안 일반"
    },
    {
      "id": 5,
      "name": "5과목: 보안관리 및 법규"
    }
  ],
  "questions": [
    {
      "id": "IW_Q1",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 시스템에서 특정 파일에 SetUID 비트가 설정되어 있는지 점검하기 위한 find 명령어로 가장 올바른 것은?",
      "options": [
        "find / -perm -4000 -type f",
        "find / -perm -2000 -type f",
        "find / -perm -1000 -type f",
        "find / -perm -7777 -type f",
        "find / -perm -0400 -type f"
      ],
      "answer": 1,
      "explanation": "SetUID 비트는 8진수 4000에 해당합니다. 'find / -perm -4000 -type f' 명령을 통해 소유자 권한으로 실행되는 파일을 찾아 취약점 및 백도어를 점검합니다. (2000은 SetGID, 1000은 Sticky bit)"
    },
    {
      "id": "IW_Q2",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "버퍼 오버플로우 공격을 방어하기 위한 운영체제 메모리 보호 기법 중, 스택과 힙 영역에서의 임의 코드 실행을 하드웨어 및 OS 수준에서 금지하는 기술은?",
      "options": [
        "ASLR (Address Space Layout Randomization)",
        "DEP / NX (Data Execution Prevention)",
        "Stack Canary (스택 카나리)",
        "SafeSEH",
        "Shadow Stack"
      ],
      "answer": 2,
      "explanation": "DEP(Data Execution Prevention) / NX(No-eXecute) 비트는 데이터 저장 영역(스택, 힙)에 실행(Execute) 권한을 박탈하여 셸코드가 직접 실행되는 것을 차단하는 기법입니다. ASLR은 주소 공간을 무작위화하는 기법입니다."
    },
    {
      "id": "IW_Q3",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 PAM(Pluggable Authentication Modules) 설정 파일에서 모듈 플래그(Control Flag) 중, 실패하더라도 즉시 중단되지 않고 다음 모듈을 계속 수행하지만 최종 인증은 실패로 처리되는 플래그는?",
      "options": [
        "required",
        "requisite",
        "sufficient",
        "optional",
        "include"
      ],
      "answer": 1,
      "explanation": "required는 실패 시에도 바로 종료하지 않고 스택의 나머지 모듈을 모두 수행한 후 최종 실패를 반환합니다. 반면 requisite는 실패 시 즉시 중단하고 인증 실패를 리턴합니다. sufficient는 이전 모듈이 실패하지 않았고 본 모듈이 성공하면 즉시 인증 성공으로 처리됩니다."
    },
    {
      "id": "IW_Q4",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 1,
      "subject_name": "1과목: 시스템 보안",
      "question": "리눅스 로그 파일 중 바이너리 형태로 기록되어 lastlog 명령어를 통해서만 사용자별 최근 로그인 시간과 접속 IP 정보를 확인할 수 있는 로그 파일은?",
      "options": [
        "/var/log/wtmp",
        "/var/log/utmp",
        "/var/log/lastlog",
        "/var/log/btmp",
        "/var/log/secure"
      ],
      "answer": 3,
      "explanation": "/var/log/lastlog는 각 사용자의 마지막 로그인 시간과 접속 호스트 정보를 저장하는 바이너리 로그로 lastlog 명령으로 조회합니다. wtmp는 성공한 모든 로그인/로그아웃 이력(last 명령), utmp는 현재 로그인 사용자 정보(who/w 명령), btmp는 실패한 로그인 기록(lastb 명령)입니다."
    },
    {
      "id": "IW_Q5",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "TCP 3-Way Handshake 취약점을 이용해 대량의 SYN 패킷을 전송하고 서버가 SYN/ACK 응답 후 대기하는 백로그 큐(Backlog Queue)를 고갈시키는 서비스 거부(DoS) 공격은?",
      "options": [
        "Smurf Attack",
        "TCP SYN Flooding",
        "Land Attack",
        "TearDrop",
        "Ping of Death"
      ],
      "answer": 2,
      "explanation": "TCP SYN Flooding은 공격자가 출발지 IP를 스푸핑하거나 ACK 응답을 보내지 않아 서버의 연결 백로그 큐를 가득 차게 만들어 정상적인 클라이언트의 연결을 차단하는 대표적인 L4 DoS 공격입니다. 대응책으로 SYN Cookie, Backlog Queue 증설 등이 사용됩니다."
    },
    {
      "id": "IW_Q6",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "IPSec 프로토콜 구조에 대한 설명 중 가장 옳지 않은 것은?",
      "options": [
        "AH(Authentication Header)는 데이터 발신처 인증 및 무결성을 제공하지만 암호화(기밀성)는 제공하지 않는다.",
        "ESP(Encapsulating Security Payload)는 기밀성, 무결성, 발신처 인증을 모두 제공할 수 있다.",
        "전송 모드(Transport Mode)는 IP 페이로드만 보호하며, 원래의 IP 헤더는 암호화되지 않는다.",
        "터널 모드(Tunnel Mode)는 전체 원본 IP 패킷을 보호하고 새로운 외부 IP 헤더를 추가한다.",
        "AH 프로토콜은 NAT 환경(NAT-T)에서도 IP 주소 변환 후 무결성 검증에 아무런 문제가 발생하지 않는다."
      ],
      "answer": 5,
      "explanation": "AH 프로토콜은 IP 헤더의 불변 필드까지 포함하여 무결성 해시(ICV)를 계산하므로, 중간에서 IP 헤더 주소를 변경하는 NAT 환경을 거치면 무결성 검증에 무조건 실패합니다. 따라서 NAT 환경에서는 ESP와 NAT-Traversal(NAT-T)을 사용해야 합니다."
    },
    {
      "id": "IW_Q7",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 2,
      "subject_name": "2과목: 네트워크 보안",
      "question": "다음 중 침입 탐지 시스템(IDS)의 Snort 룰 설정에서 외부에서 웹 서버(80번 포트)로 들어오는 패킷 중 '/admin' 문자열을 탐지하기 위한 룰 옵션으로 올바른 것은?",
      "options": [
        "alert tcp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; content:\"/admin\"; nocase; sid:10001;)",
        "drop udp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; regex:\"/admin\";)",
        "log ip any any <> 192.168.1.10 80 (msg:\"Admin Access\"; string:\"/admin\";)",
        "alert tcp 192.168.1.10 80 -> any any (msg:\"Admin Access\"; payload:\"/admin\";)",
        "pass tcp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; offset:0;)"
      ],
      "answer": 1,
      "explanation": "Snort 룰 헤더는 'action protocol src_ip src_port direction dst_ip dst_port' 형태이며, 페이로드 검색 옵션은 'content:\"문자열\";'을 사용합니다. 대소문자 무시는 'nocase;', 고유 식별자는 'sid:숫자;'로 지정합니다."
    },
    {
      "id": "IW_Q8",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "SQL 인젝션(SQL Injection) 공격을 원천적으로 차단하기 위한 개발 보안(시큐어코딩) 대책으로 가장 효과적인 것은?",
      "options": [
        "정규표현식을 이용한 동적 SQL 문자열 필터링",
        "PreparedStatement(매개변수화된 쿼리) 바인딩 사용",
        "클라이언트 단에서 자바스크립트로 특수문자 검증",
        "웹 방화벽(WAF) 전용 탐지 룰셋 단독 적용",
        "GET 방식 대신 POST 방식으로 모든 파라미터 전송"
      ],
      "answer": 2,
      "explanation": "PreparedStatement는 데이터베이스 쿼리의 구조(Syntax)를 미리 컴파일하고 사용자 입력을 단순 리터럴 데이터(Value)로만 바인딩하므로 쿼리의 의미 구조를 변경하는 SQL Injection을 원천 방어합니다."
    },
    {
      "id": "IW_Q9",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "크로스 사이트 스크립팅(XSS) 취약점을 방어하기 위해 웹 서버가 응답 HTTP 헤더에 설정하여 클라이언트 측 자바스크립트(document.cookie)를 통한 세션 쿠키 탈취를 차단하는 속성은?",
      "options": [
        "Secure 속성",
        "HttpOnly 속성",
        "SameSite=Strict 속성",
        "Domain 속성",
        "Path 속성"
      ],
      "answer": 2,
      "explanation": "HttpOnly 속성이 설정된 쿠키는 브라우저의 document.cookie 스크립트를 통해 접근할 수 없으므로, XSS 공격이 발생하더라도 세션 쿠키 탈취를 효과적으로 차단합니다. (Secure는 HTTPS 통신 시에만 쿠키 전송, SameSite는 CSRF 방어용)"
    },
    {
      "id": "IW_Q10",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 3,
      "subject_name": "3과목: 애플리케이션 보안",
      "question": "DNS를 통해 송신자의 메일 서버 IP가 실제 정당한 도메인 소유자의 메일 서버인지 검증하여 스팸 메일 및 피싱을 방지하는 이메일 인증 표준 기술 중, 공개키 암호화 기반의 전자서명을 메일 헤더에 추가하는 방식은?",
      "options": [
        "SPF (Sender Policy Framework)",
        "DKIM (DomainKeys Identified Mail)",
        "DMARC (Domain-based Message Authentication)",
        "PGP (Pretty Good Privacy)",
        "S/MIME"
      ],
      "answer": 2,
      "explanation": "DKIM은 송신자 메일 서버가 개인키로 메일 헤더에 전자서명을 첨부하고, 수신자는 송신자의 DNS TXT 레코드에 공개된 공개키를 조회하여 서명을 검증함으로써 위변조 여부를 식별합니다. (SPF는 송신 IP 대조, DMARC는 SPF+DKIM 정책 통합)"
    },
    {
      "id": "IW_Q11",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "블록 암호화 알고리즘의 운영 모드(Operation Mode) 중, 동일한 평문 블록이 항상 동일한 암호문 블록을 생성하여 구조적 취약점이 발생하며 패딩 오라클 공격 등에 취약한 가장 단순한 모드는?",
      "options": [
        "CBC (Cipher Block Chaining) 모드",
        "ECB (Electronic Codebook) 모드",
        "CFB (Cipher Feedback) 모드",
        "OFB (Output Feedback) 모드",
        "CTR (Counter) 모드"
      ],
      "answer": 2,
      "explanation": "ECB(Electronic Codebook) 모드는 각각의 블록을 독립적으로 암호화하므로 동일한 평문 블록은 항상 동일한 암호문 블록이 됩니다. 이미지 파일 등을 암호화할 경우 윤곽선 패턴이 그대로 노출되므로 기밀성이 요구되는 환경에서 사용을 금지합니다."
    },
    {
      "id": "IW_Q12",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "보안 모델 중 군사적 기밀성을 보장하기 위해 고안된 모델로, 'No Read Up (단순 보안 속성)'과 'No Write Down (*-보안 속성)'의 두 가지 강제적 접근통제(MAC) 규칙을 갖는 모델은?",
      "options": [
        "Biba 모델",
        "Bell-LaPadula (BLP) 모델",
        "Clark-Wilson 모델",
        "Chinese Wall 모델",
        "HRU 모델"
      ],
      "answer": 2,
      "explanation": "Bell-LaPadula(BLP) 모델은 기밀성(Confidentiality)을 최우선으로 하는 상태 머신 모델입니다. 낮은 등급은 높은 등급을 읽을 수 없고(NRU), 높은 등급 사용자가 낮은 등급 파일에 기밀을 쓸 수 없습니다(NWD). 무결성을 위한 모델은 Biba 모델(Read Up, Write Down)입니다."
    },
    {
      "id": "IW_Q13",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 4,
      "subject_name": "4과목: 정보보안 일반",
      "question": "공개키 기반구조(PKI)에서 인증서 폐지 목록(CRL)의 실시간성 결여 및 대용량 트래픽 문제를 해결하기 위해, 클라이언트가 특정 인증서의 유효성 여부만을 실시간으로 조회할 수 있도록 설계된 프로토콜은?",
      "options": [
        "LDAP",
        "OCSP (Online Certificate Status Protocol)",
        "SCEP (Simple Certificate Enrollment Protocol)",
        "S/MIME",
        "CMP"
      ],
      "answer": 2,
      "explanation": "OCSP는 클라이언트가 인증서 일련번호를 질의하면 OCSP 응답자가 즉시 'Good, Revoked, Unknown' 중 하나의 상태를 실시간 응답해 주는 경량 프로토콜로, 주기적으로 전체 폐지 목록을 다운로드해야 하는 CRL의 단점을 해결합니다."
    },
    {
      "id": "IW_Q14",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 보안관리 및 법규",
      "question": "개인정보 보호법상 개인정보가 유출되었음을 알게 된 경우, 개인정보처리자가 정당한 사유가 없는 한 정보주체에게 지체 없이 유출 사실을 통지해야 하는 법정 기한은?",
      "options": [
        "24시간 이내",
        "48시간 이내",
        "72시간 이내",
        "5일 이내",
        "7일 이내"
      ],
      "answer": 3,
      "explanation": "개인정보 보호법 제34조 제1항 및 시행령에 따라 개인정보처리자는 유출 사실을 알게 되었을 때 72시간 이내에 해당 정보주체에게 통지하여야 하며, 1천명 이상 유출 시에는 보호위원회 또는 KISA에 신고해야 합니다."
    },
    {
      "id": "IW_Q15",
      "category": "infosec_written",
      "exam": 1,
      "exam_name": "1회 필기 실전 모의고사",
      "subject_id": 5,
      "subject_name": "5과목: 보안관리 및 법규",
      "question": "정보통신망법 및 정보보호 및 개인정보보호 관리체계(ISMS-P) 인증에 따라 의무적으로 인증을 취득해야 하는 대상 기준 중 가장 옳지 않은 것은?",
      "options": [
        "정보통신망서비스를 제공하는 ISP 사업자",
        "수도권 및 모든 광역시에서 정보통신망서비스를 제공하는 자로서 집적된 정보통신시설을 운영하는 자(IDC)",
        "전년도 매출액 또는 세입 등이 1,500억원 이상인 종합병원",
        "재적학생 수가 1만명 이상인 고등교육법상 대학교",
        "연간 정보통신서비스 부문 매출액이 50억원 이상인 모든 일반 스타트업"
      ],
      "answer": 5,
      "explanation": "ISMS 의무인증 대상 중 정보통신서비스 제공자는 '정보통신서비스 부문 전년도 매출액이 100억원 이상'이거나 '전년도 직전 3개월간 일일평균 이용자 수가 100만명 이상'인 자에 한합니다. 연매출 50억원 스타트업은 의무 대상이 아닙니다."
    }
  ],
  "summaries": [
    {
      "title": "1과목. 시스템 보안 핵심 요약",
      "topics": [
        {
          "name": "계정·권한 및 리눅스 핵심 보안",
          "points": [
            "SetUID(4000) / SetGID(2000) / Sticky bit(1000): find / -perm -4000 -type f 로 점검.",
            "PAM 제어 플래그: required(실패해도 계속 진행 후 최종 실패), requisite(실패 시 즉시 중단), sufficient(성공 시 즉시 통과).",
            "섀도우 패스워드(/etc/shadow): 솔트(Salt)와 결합된 일방향 해시(SHA-512 $6$), 접근권한 400 또는 000.",
            "로그 파일 분석: wtmp(last, 로그인/로그아웃), utmp(who/w, 현재 접속자), btmp(lastb, 로그인 실패), lastlog(lastlog, 최근 접속)."
          ]
        },
        {
          "name": "메모리 공격 기법 및 OS 보호 대책",
          "points": [
            "버퍼 오버플로우: 스택/힙 버퍼에 할당된 크기 이상의 데이터를 입력하여 복귀 주소(RET)를 조작해 악성 셸코드 실행.",
            "ASLR: 스택, 힙, 라이브러리 메모리 주소를 매 실행마다 무작위로 재배치.",
            "DEP / NX: 데이터 영역(스택, 힙)에서의 실행 권한을 제거하여 셸코드 실행 차단.",
            "Stack Canary: 함수 프롤로그에서 복귀 주소 직전에 무작위 카나리 값을 삽입하고 에필로그에서 변조 여부 검사."
          ]
        }
      ]
    },
    {
      "title": "2과목. 네트워크 보안 핵심 요약",
      "topics": [
        {
          "name": "네트워크 공격 및 DoS/DDoS",
          "points": [
            "TCP SYN Flooding: 3-Way Handshake 백로그 큐 고갈. 대응책: SYN Cookie, Backlog 확장, Keep-Alive 조정.",
            "Smurf Attack: 출발지 IP를 희생자 IP로 위조하여 증폭 네트워크 브로드캐스트 주소로 ICMP Echo Request 전송.",
            "Land Attack: 출발지 IP/Port와 목적지 IP/Port를 희생자 시스템의 IP/Port로 동일하게 설정하여 루프 유발.",
            "ARP Spoofing: 위조된 ARP Reply 패킷을 주기적으로 브로드캐스팅하여 희생자의 ARP 캐시 테이블 게이트웨이 MAC 주소를 변조."
          ]
        },
        {
          "name": "IPSec 프로토콜 및 보안 장비",
          "points": [
            "AH (IP Protocol 51): 발신처 인증, 무결성 제공(ICV). 기밀성(암호화) 제공 안 함. NAT 환경 통과 불가.",
            "ESP (IP Protocol 50): 기밀성(암호화), 무결성, 발신처 인증 모두 제공. NAT-T(UDP 4500) 지원.",
            "전송 모드(Transport): IP 페이로드만 보호(호스트 간 통신). 터널 모드(Tunnel): 패킷 전체 보호 + 신규 IP 헤더 추가(VPN 게이트웨이 간 통신).",
            "Snort 탐지 룰 구조: [action] [protocol] [src_ip] [src_port] -> [dst_ip] [dst_port] (msg; content; nocase; sid; rev;)"
          ]
        }
      ]
    },
    {
      "title": "3과목. 애플리케이션 보안 핵심 요약",
      "topics": [
        {
          "name": "웹 취약점(OWASP Top 10) 및 시큐어코딩",
          "points": [
            "SQL Injection: 사용자 입력값이 SQL 쿼리 문법으로 해석되는 취약점. 대응: PreparedStatement 바인딩 필수.",
            "XSS (Cross-Site Scripting): 악성 스크립트가 피해자 브라우저에서 실행. 대응: 입출력 HTML Entity 인코딩, HttpOnly 쿠키 플래그.",
            "CSRF: 사용자의 권한을 도용하여 악의적인 요청을 서버에 전송. 대응: CSRF 토큰 검증, 재인증 요구, SameSite=Strict 쿠키.",
            "파일 업로드 취약점: 웹쉘 업로드 방지. 대응: 실행 확장자(.php, .jsp, .asp 등) 화이트리스트 검증, 실행 권한 없는 디렉토리에 저장."
          ]
        },
        {
          "name": "이메일 및 데이터베이스 보안",
          "points": [
            "SPF: DNS TXT 레코드에 정당한 메일 발송 IP 대역을 등록하여 수신자가 발송자 IP 검증.",
            "DKIM: 메일 헤더에 개인키 전자서명을 부착하고 DNS에 등록된 공개키로 수신자가 무결성 검증.",
            "DMARC: SPF와 DKIM 인증 결과를 기반으로 인증 실패 시 메일 처리 정책(none, quarantine, reject) 수립."
          ]
        }
      ]
    },
    {
      "title": "4과목 & 5과목. 정보보안 일반 및 법규 요약",
      "topics": [
        {
          "name": "암호학 및 접근통제 보안 모델",
          "points": [
            "대칭키(AES, SEED, ARIA, DES) vs 비대칭키(RSA, ECC, ElGamal): 기밀성은 대칭키, 키 분배/전자서명은 비대칭키.",
            "해시함수(SHA-256, SHA-512): 단방향성, 충돌 회피성, 무결성 검증에 사용.",
            "BLP 모델: 기밀성 최우선. No Read Up(단순 보안), No Write Down(*-보안 속성).",
            "Biba 모델: 무결성 최우선. No Read Down(단순 무결성), No Write Up(*-무결성 속성)."
          ]
        },
        {
          "name": "개인정보보호법 및 망법 핵심 규정",
          "points": [
            "유출 통지 기한: 지체 없이 72시간 이내 정보주체에게 통지, 1천명 이상 유출 시 보호위/KISA에 지체 없이 신고.",
            "고유식별정보: 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호(법령 구체적 근거 없이 처리 불가).",
            "암호화 의무 대상: 고유식별정보, 비밀번호(일방향), 바이오정보. (저장 시 및 네트워크 전송 시 암호화 적용)."
          ]
        }
      ]
    }
  ]
};

window.INFOSEC_PRACTICAL_DATA = {
  "name": "정보보안기사 (실기)",
  "badge": "국가기술자격",
  "desc": "실기 단답형 기출 족보 · 시스템/네트워크 설정 실무 · 소스코드 시큐어코딩 · 법규 서술형 실무 문제 및 모범 답안",
  "subjects": [
    {
      "id": 1,
      "name": "1영역: 단답형 핵심 용어·명령어"
    },
    {
      "id": 2,
      "name": "2영역: 시스템·네트워크 설정 실무"
    },
    {
      "id": 3,
      "name": "3영역: 웹 취약점 진단·시큐어코딩"
    },
    {
      "id": 4,
      "name": "4영역: 보안관리·침해사고 서술형"
    }
  ],
  "questions": [
    {
      "id": "IP_Q1",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "단답형 핵심 족보 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 용어·명령어",
      "question": "[단답형 실무] 다음 리눅스 시스템 보안 점검 지문에서 괄호에 들어갈 올바른 명령어와 설정값을 고르시오.\n\n\"리눅스 환경에서 일반 사용자가 생성하는 기본 파일과 디렉토리의 기본 권한을 안전하게 제한하기 위해 ( A ) 명령어를 설정 파일(/etc/profile)에 등록한다. 일반 파일 권한을 640(rw-r-----), 디렉토리 권한을 750(rwxr-x---)으로 생성되도록 설정하는 ( A ) 값은 ( B )이다.\"",
      "options": [
        "(A) chmod, (B) 750",
        "(A) umask, (B) 027",
        "(A) umask, (B) 022",
        "(A) chown, (B) 640",
        "(A) umask, (B) 077"
      ],
      "answer": 2,
      "explanation": "리눅스 파일 기본 권한은 666, 디렉토리 기본 권한은 777입니다. umask가 027인 경우:\n- 파일: 666 - 027 = 640 (rw-r-----)\n- 디렉토리: 777 - 027 = 750 (rwxr-x---)\n따라서 (A)는 umask, (B)는 027입니다."
    },
    {
      "id": "IP_Q2",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "단답형 핵심 족보 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 단답형 핵심 용어·명령어",
      "question": "[단답형 실무] 다음 Apache 웹 서버 설정 파일(httpd.conf)에서 디렉토리 목록 노출(Directory Listing) 취약점을 차단하기 위해 디렉토리 옵션에서 반드시 제거해야 하는 지시자는?",
      "options": [
        "FollowSymLinks",
        "Indexes",
        "Includes",
        "MultiViews",
        "ExecCGI"
      ],
      "answer": 2,
      "explanation": "Apache 웹 서버에서 디렉토리 요청 시 index.html 등 인덱스 파일이 없을 때 디렉토리 내의 모든 파일 목록을 웹 브라우저에 출력해 주는 옵션이 'Indexes'입니다. 이를 방지하려면 'Options -Indexes'로 설정하거나 'Indexes'를 제거해야 합니다."
    },
    {
      "id": "IP_Q3",
      "category": "infosec_practical",
      "exam": 1,
      "exam_name": "단답형 핵심 족보 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 시스템·네트워크 설정 실무",
      "question": "[실무형 설정] 리눅스 iptables를 이용하여 웹 서버로 유입되는 외부 트래픽 중, 특정 공격자 IP(203.0.113.50)로부터 80번 포트로 들어오는 패킷만을 즉시 차단(DROP)하기 위한 올바른 iptables 명령어는?",
      "options": [
        "iptables -A INPUT -p tcp -s 203.0.113.50 --dport 80 -j DROP",
        "iptables -A OUTPUT -p tcp -d 203.0.113.50 --sport 80 -j DROP",
        "iptables -D INPUT -p tcp -s 203.0.113.50 --dport 80 -j ACCEPT",
        "iptables -A FORWARD -p udp -s 203.0.113.50 --dport 80 -j REJECT",
        "iptables -I INPUT -p icmp -s 203.0.113.50 -j DROP"
      ],
      "answer": 1,
      "explanation": "외부에서 서버로 들어오는 패킷은 INPUT 체인에 추가(-A 또는 -I)하며, 출발지 IP(-s 203.0.113.50), 프로토콜(-p tcp), 목적지 포트(--dport 80), 대상 타겟(-j DROP)으로 구성합니다."
    },
    {
      "id": "IP_Q4",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "서술형·실무형 실전 분석",
      "subject_id": 3,
      "subject_name": "3영역: 웹 취약점 진단·시큐어코딩",
      "question": "[서술형 분석] 다음 자바(Java) 서블릿 코드에서 발견되는 치명적인 취약점과 이를 시큐어코딩 가이드에 맞게 개선하는 가장 올바른 조치 방안은?\n\n```java\nString userGrade = request.getParameter(\"grade\");\nString query = \"SELECT * FROM members WHERE grade = '\" + userGrade + \"'\";\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(query);\n```",
      "options": [
        "취약점: XSS / 조치: HTML Entity 인코딩 처리",
        "취약점: CSRF / 조치: 요청 헤더에 Referer 토큰 추가",
        "취약점: SQL Injection / 조치: PreparedStatement 바인딩 변수(?) 사용",
        "취약점: Path Traversal / 조치: .. 디렉토리 순회 문자열 치환",
        "취약점: Buffer Overflow / 조치: 배열 크기 제한 검증"
      ],
      "answer": 3,
      "explanation": "사용자 입력값(userGrade)을 문자열 연산(+)으로 직접 동적 SQL 문에 연결하여 실행하는 전형적인 SQL Injection 취약점입니다. 조치 방안: Statement 대신 PreparedStatement를 사용하고 쿼리를 'SELECT * FROM members WHERE grade = ?'로 작성한 뒤 pstmt.setString(1, userGrade); 로 매개변수를 바인딩해야 합니다."
    },
    {
      "id": "IP_Q5",
      "category": "infosec_practical",
      "exam": 2,
      "exam_name": "서술형·실무형 실전 분석",
      "subject_id": 4,
      "subject_name": "4영역: 보안관리·침해사고 서술형",
      "question": "[서술형 실무] 개인정보처리자가 이용자의 비밀번호를 데이터베이스에 저장할 때 준수해야 하는 법적 기술적 보호조치 기준에 대한 설명으로 가장 올바른 서술은?",
      "options": [
        "AES-256과 같은 안전한 양방향 대칭키 암호화 알고리즘을 적용하여 저장한다.",
        "단순 MD5 해시 함수를 사용하여 해시값을 단독으로 저장한다.",
        "SHA-256 이상의 안전한 일방향 암호화(해시) 알고리즘을 적용하고, 레인보우 테이블 공격 방지를 위해 사용자별 솔트(Salt)를 추가 적용한다.",
        "비밀번호 분실 시 복구 안내를 위해 복호화 가능한 비대칭키 공개키로 암호화한다.",
        "내부 데이터베이스 관리자만 접근 가능한 통제구역 내에서는 평문 저장이 허용된다."
      ],
      "answer": 3,
      "explanation": "개인정보의 안전성 확보조치 기준 제7조에 따라 비밀번호는 복호화되지 않는 일방향 암호화(SHA-256 이상)를 적용하여 저장해야 하며, 동일 비밀번호의 해시값 일치를 방지하고 사전/레인보우 테이블 공격을 무력화하기 위해 솔트(Salt)를 결합하여 키 스트레칭(PBKDF2, bcrypt 등)을 적용하는 것이 안전합니다."
    }
  ],
  "summaries": [
    {
      "title": "실기 필수 1. 시스템 & 서버 보안 실무",
      "topics": [
        {
          "name": "리눅스 계정 및 파일 권한 실무",
          "points": [
            "/etc/passwd (644), /etc/shadow (400 또는 000): 패스워드 복잡도 및 솔트 해시 관리.",
            "umask 022(파일 644/디렉토리 755), umask 027(파일 640/디렉토리 750): 보안 권고 umask는 022 또는 027.",
            "불필요한 SetUID 파일 제거: chmod -s /usr/bin/newgrp 등 특권 상승 잠재 파일 권한 축소.",
            "SSH 보안 설정(/etc/ssh/sshd_config): PermitRootLogin no, Port 변경, MaxAuthTries 5, Protocol 2."
          ]
        },
        {
          "name": "주요 보안 점검 명령어 족보",
          "points": [
            "열린 포트 점검: netstat -antp | grep LISTEN 또는 ss -tuln",
            "의심 프로세스 확인: ps -ef | grep 프로세스명, lsof -i :포트번호",
            "파일 무결성 점검: tripwire 또는 AIDE, find / -mtime -1 (최근 1일 내 변경된 파일 검색)",
            "로그 확인 명령어: last(wtmp), lastb(btmp), lastlog(lastlog), who/w(utmp)"
          ]
        }
      ]
    },
    {
      "title": "실기 필수 2. 네트워크 & 시큐어코딩 실무",
      "topics": [
        {
          "name": "iptables & Snort 실무 문법",
          "points": [
            "iptables 체인: INPUT(유입), OUTPUT(유출), FORWARD(경유). 기본 정책: iptables -P INPUT DROP",
            "특정 포트 허용 예: iptables -A INPUT -p tcp --dport 443 -j ACCEPT",
            "상태 추적: iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT",
            "Snort 탐지 옵션: content:\"|0d 0a|\"; offset:0; depth:100; nocase; flags:S; threshold:type both, track by_src, count 10, seconds 1;"
          ]
        },
        {
          "name": "소프트웨어 개발보안 (시큐어코딩 47개 보안약점)",
          "points": [
            "SQL Injection: PreparedStatement(매개변수 바인딩) 필수 적용. 동적 문자열 연결(+) 절대 금지.",
            "XSS: 공격 스크립트 실행 방지 -> 문자열 치환(& -> &amp;, < -> &lt;, > -> &gt;, \" -> &quot;).",
            "경로 조작(Path Traversal): 외부 입력 파일명에서 ../ 등 경로 순회 문자열 필터링 및 화이트리스트 검증.",
            "부적절한 예외 처리: e.printStackTrace() 직접 노출 금지(시스템 내부 구조 노출 방지), 사용자 정의 오류 페이지 적용."
          ]
        }
      ]
    }
  ]
};

window.ISMSP_AUDITOR_DATA = {
  "name": "ISMS-P 인증심사원",
  "badge": "국가전문자격",
  "desc": "1영역 관리체계 수립(16개) · 2영역 보호대책(64개) · 3영역 개인정보 처리단계(22개) 102개 인증기준별 실전 결함 판정 시나리오 퀴즈 & 결함 사례집",
  "subjects": [
    {
      "id": 1,
      "name": "1영역: 관리체계 수립·운영 (16개)"
    },
    {
      "id": 2,
      "name": "2영역: 보호대책 요구사항 (64개)"
    },
    {
      "id": 3,
      "name": "3영역: 개인정보 처리단계별 (22개)"
    }
  ],
  "questions": [
    {
      "id": "ISMSP_Q1",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 관리체계 수립·운영 (16개)",
      "question": "[결함 판정] 다음 A 기업의 인증심사 인터뷰 내용 중 ISMS-P 인증기준 '1.1.2(최고책임자의 지정)'에 대한 결함(Non-conformity)으로 판정할 수 있는 사례는?",
      "options": [
        "자산총액 5조원 이상의 대규모 전자금융업자가 전산 CIO와 정보보호최고책임자(CISO)를 별개의 임원으로 독립 분리하여 임명하였다.",
        "자산총액 1천억원 이상의 기업에서 CISO를 임원급으로 지정하고 관련 법령에 따른 자격요건을 충족하여 과학기술정보통신부에 신고를 완료하였다.",
        "정보통신망법상 CISO 겸직 제한 대상인 전자상거래 기업에서 CISO가 개인정보보호책임자(CPO) 역할을 겸직하도록 내부 규정에 명시하였다.",
        "일정 규모 이상의 기업에서 CISO가 개발본부장(CIO)을 겸직하여 정보시스템 개발 및 인프라 운영 업무를 총괄 관리하도록 발령하였다.",
        "CISO의 법정 자격요건(정보보호/정보기술 경력) 충족 여부를 인사팀 검증을 거쳐 이사회에 보고하였다."
      ],
      "answer": 4,
      "explanation": "정보통신망법 제45조의3 제3항 및 ISMS-P 1.1.2 기준에 따라 자산총액 및 정보통신서비스 매출액이 일정 규모 이상인 기업의 CISO는 회사의 다른 정보기술 부문 업무(CIO, 개발본부장 등)를 겸직할 수 없습니다. 개발본부장을 겸직하도록 한 것은 중대한 결함입니다. (단, CISO와 CPO 간의 겸직은 허용됩니다.)"
    },
    {
      "id": "ISMSP_Q2",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 1,
      "subject_name": "1영역: 관리체계 수립·운영 (16개)",
      "question": "[결함 판정] ISMS-P 인증기준 '1.2.2(위험 평가 및 정보보호 대책 수립)'에 대한 심사원의 결함 판정 사례로 가장 타당한 것은?",
      "options": [
        "위험 평가 결과를 바탕으로 수용 가능한 위험 수준(DOA)을 초과하는 위험에 대해 정보보호 대책을 수립하였다.",
        "정보보호 대책명세서에 우선순위와 일정, 담당 부서, 소요 예산을 명시하여 경영진 승인을 받았다.",
        "자산 위험평가를 수행하여 위험도를 도출하였으나, 경영진이 승인한 수용 가능한 위험 수준(DOA)의 기준치 자체가 내부 규정 어디에도 정의되어 있지 않아 초과 위험 식별이 불가능하였다.",
        "연간 정보보호 대책 이행 계획을 보안위원회에 상정하여 예산 편성을 확정하였다.",
        "잔여 위험에 대해 최고경영진이 서명으로 최종 위험 수용을 공식 승인하였다."
      ],
      "answer": 3,
      "explanation": "위험관리 기준(1.2.2)에서는 조직의 환경을 고려하여 최고경영진이 승인한 수용 가능한 위험 수준(DOA: Degree of Acceptance)을 명확히 설정해야 합니다. DOA 기준이 부재하면 어떤 위험을 개선 조치하고 어떤 위험을 수용할지 객관적 판정이 불가하므로 전형적인 결함 사례입니다."
    },
    {
      "id": "ISMSP_Q3",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] ISMS-P 2.6.7(접속기록 보관 및 점검) 기준에 따라 5만명 이상의 고유식별정보 또는 민감정보를 처리하는 대규모 개인정보처리시스템의 접속기록 보관 및 점검 요건으로 올바른 것은?",
      "options": [
        "최소 1년 이상 보관하고, 분기 1회 이상 이상유무를 점검해야 한다.",
        "최소 1년 이상 보관하고, 월 1회 이상 이상유무를 점검해야 한다.",
        "최소 2년 이상 보관하고, 월 1회 이상 이상유무를 점검해야 한다.",
        "최소 2년 이상 보관하고, 반기 1회 이상 이상유무를 점검해야 한다.",
        "최소 3년 이상 보관하고, 연 1회 이상 이상유무를 점검해야 한다."
      ],
      "answer": 3,
      "explanation": "개인정보의 안전성 확보조치 기준 제8조에 따라 5만명 이상의 정보주체에 관하여 민감정보 또는 고유식별정보를 처리하거나 정보통신망을 통해 대규모 개인정보를 처리하는 시스템은 접속기록을 2년 이상 보관해야 하며, 월 1회 이상 접속기록을 점검해야 합니다."
    },
    {
      "id": "ISMSP_Q4",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] 다음 중 ISMS-P 인증기준 '2.5.4(비밀번호 관리)'에 따른 결함으로 판정해야 하는 경우는?",
      "options": [
        "영문 대소문자, 숫자, 특수문자 중 3종류 이상 조합 시 최소 8자리 이상으로 설정하도록 강제하였다.",
        "영문, 숫자 2종류 조합 시 최소 10자리 이상으로 설정하도록 시스템 통제를 구현하였다.",
        "분기별(90일) 1회 이상 비밀번호를 주기적으로 변경하도록 알림 및 변경 유도를 적용하였다.",
        "관리자 시스템의 비밀번호 변경 시 직전 사용했던 비밀번호 3개에 대한 재사용을 방지하였다.",
        "시스템 관리자 계정의 초기 비밀번호를 'Welcome123!'으로 일괄 부여하고, 최초 로그인 시 비밀번호 변경을 강제하지 않아 수개월간 초기 암호가 유지되었다."
      ],
      "answer": 5,
      "explanation": "관리자 또는 사용자 계정의 초기 비밀번호 부여 시 최초 접속 시점에 즉시 안전한 비밀번호로 변경하도록 강제 통제해야 합니다. 초기 비밀번호가 변경 없이 유지되도록 방치한 것은 2.5.4 기준의 명백한 결함입니다."
    },
    {
      "id": "ISMSP_Q5",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 2,
      "subject_name": "2영역: 보호대책 요구사항 (64개)",
      "question": "[결함 판정] ISMS-P 2.7.1(암호정책 적용) 기준상 다음 중 저장 시 암호화가 법적으로 의무화된 개인정보 항목으로만 바르게 짝지어진 것은?",
      "options": [
        "이름, 연락처, 주소, 이메일",
        "주민등록번호, 여권번호, 운전면허번호, 외국인등록번호, 비밀번호, 바이오정보",
        "생년월일, 성별, 배송지주소, 신용카드번호",
        "로그인 아이디, 닉네임, 접속 IP, 회원등급",
        "학력, 경력사항, 부서명, 직책"
      ],
      "answer": 2,
      "explanation": "개인정보 보호법 및 안전성 확보조치 기준에 따라 저장 시 암호화 의무 대상은 ① 고유식별정보(주민등록번호, 여권번호, 운전면허번호, 외국인등록번호), ② 비밀번호(일방향 해시), ③ 바이오정보입니다. 신용카드번호나 계좌번호 등 금융정보는 전자금융거래법 등에 따릅니다."
    },
    {
      "id": "ISMSP_Q6",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 (22개)",
      "question": "[결함 판정] ISMS-P 3.1.2(수집 제한 및 최소 수집) 기준에서 '필수정보와 선택정보의 구분'에 관한 중대한 결함 사례는?",
      "options": [
        "회원가입 웹페이지에서 이름, 휴대폰번호, 아이디, 비밀번호를 필수동의로 설정하였다.",
        "이벤트 경품 수령을 위한 자택 주소 입력을 선택동의로 두고 미입력 시에도 회원가입이 완료되도록 하였다.",
        "회원가입 시 마케팅 활용 목적의 '생년월일'과 '관심 상품'을 필수 입력 항목으로 지정하고, 동의하지 않으면 기본 회원가입을 거부하였다.",
        "필수항목과 선택항목의 수집 목적, 보유기간을 이용자가 보기 쉽게 구분하여 고지하였다.",
        "선택항목에 동의하지 않았음을 이유로 기본 서비스 이용에 차별을 두지 않았다."
      ],
      "answer": 3,
      "explanation": "개인정보 보호법 제16조 제3항 및 ISMS-P 3.1.2 기준에 따라 개인정보처리자는 필수항목 외의 선택항목 제공에 동의하지 않는다는 이유로 이용자에게 기본 재화 또는 서비스의 제공을 거부해서는 안 됩니다. 마케팅 항목 미동의 시 가입을 차단하는 것은 대표적 위반 결함입니다."
    },
    {
      "id": "ISMSP_Q7",
      "category": "ismsp_auditor",
      "exam": 1,
      "exam_name": "1회 실전 결함판정 모의고사",
      "subject_id": 3,
      "subject_name": "3영역: 개인정보 처리단계별 (22개)",
      "question": "[결함 판정] ISMS-P 3.4.1(개인정보 파기) 기준에서 파기 및 분리보관 통제에 대한 결함 사례로 옳은 것은?",
      "options": [
        "회원 탈퇴 회원의 개인정보를 전자상거래법에 따른 거래기록 보존 기간(5년) 동안 운영 DB에서 물리적/논리적으로 분리된 별도 저장소로 이관하여 보관하였다.",
        "개인정보 보유기간이 경과하거나 처리 목적이 달성된 개인정보를 영구 삭제(디가우징 또는 덮어쓰기)하였다.",
        "1년 이상 서비스를 이용하지 않은 장기 미이용자의 개인정보를 다른 이용자의 개인정보와 분리하여 별도로 저장·관리하였다.",
        "분리보관된 휴면계정 개인정보에 대해 일반 직원의 접근 권한을 엄격히 차단하였다.",
        "보유기간(3년)이 도래한 이벤트 참여자 개인정보를 파기하지 않고, 향후 신규 이벤트 홍보에 재사용하기 위해 운영 DB 테이블에 그대로 보관하였다."
      ],
      "answer": 5,
      "explanation": "개인정보 보호법 제21조 및 ISMS-P 3.4.1 기준에 따라 보유기간이 경과하거나 처리 목적이 달성된 개인정보는 지체 없이(5일 이내) 파기하여야 합니다. 다른 법령에 따른 보존 근거 없이 마케팅 재사용을 위해 파기를 누락하고 운영 DB에 보관한 것은 명백한 결함입니다."
    }
  ],
  "summaries": [
    {
      "title": "1영역. 관리체계 수립 및 운영 (16개 기준 핵심)",
      "topics": [
        {
          "name": "1.1 관리체계 기반 마련 (4개 기준)",
          "points": [
            "1.1.1 경영진의 참여: 최고경영진의 보안위원회 주재, 보안 예산 및 인력 자원 승인 실적 필수.",
            "1.1.2 최고책임자의 지정: CISO/CPO의 정식 임명 및 망법 겸직금지 규정(대규모 기업 CISO의 CIO 겸직 금지) 준수.",
            "1.1.3 조직 구성: 보안담당자, 개인정보담당자, IT운영자 간 명확한 R&R 수립 및 부서별 보안협의체 가동.",
            "1.1.4 범위 설정: 인증 대상 서비스 관련 시스템, 네트워크, 개발망, 개인정보 처리 흐름 전수 식별."
          ]
        },
        {
          "name": "1.2 위험 관리 (2개 기준)",
          "points": [
            "1.2.1 위험 식별 및 분석: 자산 중요도 산정, 위협/취약점 식별, 연 1회 이상 정기 위험평가 실시.",
            "1.2.2 위험 평가 및 정보보호 대책 수립: 최고경영진 승인하에 DOA(수용 가능 위험 수준)를 설정하고 초과 위험 대책 수립."
          ]
        },
        {
          "name": "1.3 & 1.4 운영·점검 및 개선 (10개 기준)",
          "points": [
            "1.3.1 보호대책 공유: 연간 보호대책을 유관 부서에 전파하고 이행 상황을 정기 모니터링.",
            "1.4.1 법적 요구사항 검토: 개정 법령(개인정보보호법, 정보통신망법 등) 준수 여부를 연 1회 이상 검토.",
            "1.4.2 관리체계 점검: 연 1회 이상 독립된 내부감사팀을 통한 내부점검 수행 및 경영진 보고."
          ]
        }
      ]
    },
    {
      "title": "2영역. 보호대책 요구사항 (64개 기준 핵심)",
      "topics": [
        {
          "name": "접근통제 및 암호화 (2.5 ~ 2.7)",
          "points": [
            "2.5.1 사용자 식별: 공용 계정 사용 금지, 1인 1계정 원칙 준수, 퇴사자 계정 즉시 삭제/비활성화.",
            "2.5.4 비밀번호 관리: 영문/숫자/특수문자 3종 8자리 또는 2종 10자리, 초기 비밀번호 변경 강제.",
            "2.6.2 개발망/운영망 분리: 개발망과 운영망 물리적/논리적 분리, 운영 DB 직접 접근 통제.",
            "2.6.7 접속기록 보관 및 점검: 접속기록 최소 1년(대규모·고유식별정보 2년) 보관, 월 1회 이상 점검.",
            "2.7.1 암호정책: 고유식별정보, 비밀번호(일방향 해시), 바이오정보 저장 시 암호화 필수 적용."
          ]
        },
        {
          "name": "운영보안 및 사고관리 (2.8 ~ 2.11)",
          "points": [
            "2.8.5 시험 데이터 보안: 개발/테스트 시 실제 운영 개인정보 사용 금지, 가명·익명 테스트 데이터 활용.",
            "2.9.3 백업 및 복구: 주기적 백업 수행 및 연 1회 이상 실제 복구 모의훈련 실시.",
            "2.10.1 침해사고 대응: 침해사고 대응절차 수립, 탐지 시 침해사고 대응팀(CERT) 즉시 가동."
          ]
        }
      ]
    },
    {
      "title": "3영역. 개인정보 처리단계별 요구사항 (22개 기준 핵심)",
      "topics": [
        {
          "name": "수집 및 이용 (3.1 ~ 3.2)",
          "points": [
            "3.1.1 수집 동의 기준: 동의 4대 고지사항(목적, 항목, 보유기간, 거부권 및 불이익) 명시, 만 14세 미만 법정대리인 동의.",
            "3.1.2 최소 수집: 필수항목과 선택항목을 엄격히 구분, 선택항목 미동의를 이유로 기본 서비스 거부 금지.",
            "3.2.1 개인정보 현황 관리: 개인정보 처리방침과 실제 수집·이용 항목 간 100% 일치성 유지."
          ]
        },
        {
          "name": "제공·위탁 및 파기 (3.3 ~ 3.5)",
          "points": [
            "3.3.1 제3자 제공: 정보주체의 별도 동의 필수 (목적, 받는 자, 항목, 보유기간).",
            "3.3.2 업무 위탁: 위탁계약서에 위탁업무 목적, 재위탁 제한, 안전성 확보조치, 감독 사항 명시 및 연 1회 수탁사 실태 점검.",
            "3.4.1 파기: 목적 달성 시 복구 불가능한 방법으로 영구 파기, 법령 보존 시 분리보관 시스템 적용.",
            "3.5.1 권리 보장: 정보주체의 열람, 정정, 삭제, 처리정지 요구에 대해 10일 이내 회신 및 조치."
          ]
        }
      ]
    }
  ]
};

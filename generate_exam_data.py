# -*- coding: utf-8 -*-
"""
generate_exam_data.py (고밀도 대규모 데이터셋)
- 정보보안기사 (필기): 1회(25문항) + 2회(25문항) = 총 50문항 실전 기출 + 5대 과목 심층 요약집
- 정보보안기사 (실기): 1회 단답형(15문항) + 2회 서술·실무형(15문항) = 총 30문항 + 실기 필수 족보
- ISMS-P 인증심사원: 1회 결함판정(15문항) + 2회 결함도출(15문항) = 총 30문항 + 102개 기준별 결함사례 총람
"""

import json

def get_written_questions():
    q = []
    # 1회 모의고사 (25문항)
    q.extend([
        # 1과목: 시스템 보안 (Q1 ~ Q5)
        {
            "id": "IW1_Q1", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "리눅스 파일 시스템에서 특정 파일에 SetUID 비트가 설정되어 있는지 점검하기 위한 find 명령어로 가장 올바른 것은?",
            "options": ["find / -perm -4000 -type f", "find / -perm -2000 -type f", "find / -perm -1000 -type f", "find / -perm -7777 -type f", "find / -perm -0400 -type f"],
            "answer": 1, "explanation": "SetUID 비트는 8진수 4000에 해당합니다. 'find / -perm -4000 -type f'로 소유자 실행 권한 상승 파일을 전수 점검합니다. (2000: SetGID, 1000: Sticky bit)"
        },
        {
            "id": "IW1_Q2", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "버퍼 오버플로우 공격을 방어하기 위한 운영체제 보호 기법 중 스택과 힙 영역에서의 코드 실행을 하드웨어 및 OS 수준에서 금지하는 기술은?",
            "options": ["ASLR (Address Space Layout Randomization)", "DEP / NX (Data Execution Prevention)", "Stack Canary (스택 카나리)", "SafeSEH", "Shadow Stack"],
            "answer": 2, "explanation": "DEP/NX 비트는 데이터 저장 영역인 스택과 힙에서 셸코드가 실행되는 것을 하드웨어 수준에서 차단합니다. ASLR은 주소 공간 무작위화 기법입니다."
        },
        {
            "id": "IW1_Q3", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "리눅스 PAM 설정 파일의 모듈 플래그 중, 실패하더라도 스택의 나머지 모듈을 계속 수행하지만 최종 인증 결과는 실패로 반환하는 플래그는?",
            "options": ["required", "requisite", "sufficient", "optional", "include"],
            "answer": 1, "explanation": "required는 실패 시에도 바로 종료하지 않고 나머지 모듈을 계속 실행한 후 최종 실패를 반환합니다. requisite는 실패 즉시 중단하고 반환합니다."
        },
        {
            "id": "IW1_Q4", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "리눅스 로그 파일 중 바이너리 형태로 기록되어 lastlog 명령어를 통해서만 사용자별 최근 로그인 시간과 접속 IP 정보를 확인할 수 있는 파일은?",
            "options": ["/var/log/wtmp", "/var/log/utmp", "/var/log/lastlog", "/var/log/btmp", "/var/log/secure"],
            "answer": 3, "explanation": "/var/log/lastlog는 사용자별 마지막 로그인 정보를 저장합니다. wtmp는 전체 로그인/로그아웃 이력(last), utmp는 현재 로그인 사용자(who), btmp는 로그인 실패(lastb)입니다."
        },
        {
            "id": "IW1_Q5", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "윈도우 시스템에서 시스템 자원에 대한 모든 접근 제어 결정을 내리고 감사 로그를 생성하는 보안 서브시스템 핵심 컴포넌트는?",
            "options": ["LSA (Local Security Authority)", "SAM (Security Accounts Manager)", "SRM (Security Reference Monitor)", "Winlogon", "Kerberos"],
            "answer": 3, "explanation": "SRM(보안 참조 모니터)은 커널 모드에서 동작하며 사용자 토큰과 객체의 보안 디스크립터(DACL)를 비교하여 접근 허용/거부 여부를 결정하고 감사 로그를 생성합니다."
        },

        # 2과목: 네트워크 보안 (Q6 ~ Q10)
        {
            "id": "IW1_Q6", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "TCP 3-Way Handshake 취약점을 이용해 대량의 SYN 패킷을 전송하고 서버의 백로그 큐를 고갈시키는 대표적인 L4 DoS 공격은?",
            "options": ["Smurf Attack", "TCP SYN Flooding", "Land Attack", "TearDrop", "Ping of Death"],
            "answer": 2, "explanation": "TCP SYN Flooding은 공격자가 SYN/ACK 응답 후 ACK를 회신하지 않아 서버의 Backlog Queue를 고갈시켜 정상 서비스를 불능으로 만드는 공격입니다."
        },
        {
            "id": "IW1_Q7", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "IPSec 프로토콜 구조에 대한 설명 중 가장 옳지 않은 것은?",
            "options": [
                "AH(Authentication Header)는 기밀성(암호화)을 제공하지 않고 무결성과 인증만 제공한다.",
                "ESP(Encapsulating Security Payload)는 기밀성, 무결성, 인증을 모두 제공할 수 있다.",
                "전송 모드(Transport Mode)는 원본 IP 헤더를 유지하고 IP 페이로드만 보호한다.",
                "터널 모드(Tunnel Mode)는 전체 원본 패킷을 보호하고 새로운 외부 IP 헤더를 부착한다.",
                "AH 프로토콜은 NAT 환경에서도 IP 헤더 주소 변환 후 무결성 검증에 아무런 문제가 없다."
            ],
            "answer": 5, "explanation": "AH는 IP 헤더의 불변 필드까지 포함하여 무결성 해시(ICV)를 계산하므로 중간에서 IP를 변환하는 NAT를 통과하면 검증에 실패합니다. 따라서 NAT 환경에서는 ESP와 NAT-T를 씁니다."
        },
        {
            "id": "IW1_Q8", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "Snort IDS 룰 설정에서 외부에서 웹 서버(80번)로 들어오는 패킷 중 '/admin' 문자열을 대소문자 구분 없이 탐지하기 위한 룰 옵션으로 올바른 것은?",
            "options": [
                "alert tcp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; content:\"/admin\"; nocase; sid:10001;)",
                "drop udp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; regex:\"/admin\";)",
                "log ip any any <> 192.168.1.10 80 (msg:\"Admin Access\"; string:\"/admin\";)",
                "alert tcp 192.168.1.10 80 -> any any (msg:\"Admin Access\"; payload:\"/admin\";)",
                "pass tcp any any -> 192.168.1.10 80 (msg:\"Admin Access\"; offset:0;)"
            ],
            "answer": 1, "explanation": "Snort 룰은 헤더에 액션/프로토콜/출발지/목적지, 바디에 msg, content:\"/admin\"; nocase; sid:고유번호; 옵션을 사용합니다."
        },
        {
            "id": "IW1_Q9", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "공격자가 출발지 IP 주소와 목적지 IP 주소를 희생자의 IP 주소로 동일하게 조작하여 패킷을 전송함으로써 무한 루프 상태에 빠지게 하는 공격은?",
            "options": ["Smurf Attack", "Land Attack", "TearDrop", "Bonk Attack", "Fraggle"],
            "answer": 2, "explanation": "Land Attack은 송신자 IP/Port와 수신자 IP/Port를 희생자 시스템의 IP/Port와 동일하게 스푸핑하여 시스템이 자기 자신에게 응답하게 만들어 CPU/연결 자원을 소진시키는 공격입니다."
        },
        {
            "id": "IW1_Q10", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "TCP 포트 스캔 기법 중 포트가 열려 있을 때 대상 서버로부터 아무런 응답이 오지 않고, 닫혀 있을 때만 RST/ACK 패킷이 회신되는 스텔스 스캔 조합은?",
            "options": ["TCP Connect 스캔", "TCP SYN(Half-Open) 스캔", "FIN 스캔, Null 스캔, Xmas 스캔", "ACK 스캔", "UDP 스캔"],
            "answer": 3, "explanation": "FIN, Null, Xmas 스캔은 비정상 플래그 조합 패킷을 전송하는 스텔스 스캔으로, RFC 793 표준에 따라 포트가 닫혀 있으면 RST가 오고, 열려 있으면 패킷을 무시(Drop)하여 응답이 없습니다."
        },

        # 3과목: 애플리케이션 보안 (Q11 ~ Q15)
        {
            "id": "IW1_Q11", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "SQL 인젝션(SQL Injection) 공격을 원천 차단하기 위한 시큐어코딩 대책으로 가장 권장되는 방식은?",
            "options": ["정규표현식을 이용한 동적 SQL 문자열 필터링", "PreparedStatement(매개변수화된 쿼리) 바인딩 사용", "클라이언트 단 자바스크립트 특수문자 검증", "웹 방화벽 단독 적용", "GET 방식 대신 POST 방식으로만 데이터 전송"],
            "answer": 2, "explanation": "PreparedStatement는 쿼리 구조를 미리 컴파일하고 사용자 입력을 단순 리터럴 값으로만 처리하므로 쿼리 구문 변조를 원천 방어합니다."
        },
        {
            "id": "IW1_Q12", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "크로스 사이트 스크립팅(XSS) 공격 시 document.cookie 자바스크립트 호출을 통한 세션 쿠키 탈취를 브라우저 단에서 원천 차단하는 쿠키 속성은?",
            "options": ["Secure 속성", "HttpOnly 속성", "SameSite=Strict 속성", "Domain 속성", "Path 속성"],
            "answer": 2, "explanation": "HttpOnly 플래그가 설정된 쿠키는 클라이언트 스크립트에서 접근할 수 없어 XSS 발생 시에도 세션 하이재킹을 방어합니다. (Secure는 HTTPS 통신 시에만 전송)"
        },
        {
            "id": "IW1_Q13", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "송신자 도메인의 DNS TXT 레코드에 공개키를 등록하고, 메일 헤더에 개인키로 전자서명을 첨부하여 메일 위변조를 검증하는 이메일 인증 표준 기술은?",
            "options": ["SPF", "DKIM", "DMARC", "PGP", "S/MIME"],
            "answer": 2, "explanation": "DKIM(DomainKeys Identified Mail)은 비대칭키 전자서명을 메일 헤더에 추가하여 송신자 위조를 검증합니다. (SPF는 발송 서버 IP 대조, DMARC는 정책 통합)"
        },
        {
            "id": "IW1_Q14", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "사용자가 로그인된 인증 상태를 도용하여 사용자의 의도와 무관하게 서버로 악의적인 요청(패스워드 변경, 계좌이체 등)을 전송하게 만드는 웹 공격은?",
            "options": ["SQL Injection", "CSRF (Cross-Site Request Forgery)", "Directory Traversal", "SSRF", "File Inclusion"],
            "answer": 2, "explanation": "CSRF는 피해자의 인증된 브라우저 세션을 이용해 서버에 비정상 요청을 보내는 공격입니다. 방어책으로 CSRF 토큰 검증, 재인증, SameSite 쿠키가 쓰입니다."
        },
        {
            "id": "IW1_Q15", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "웹 브라우저가 오직 HTTPS 프로토콜을 통해서만 웹 서버와 통신하도록 강제하여 SSL Stripping 공격을 방어하는 HTTP 보안 응답 헤더는?",
            "options": ["X-Frame-Options", "Content-Security-Policy", "Strict-Transport-Security (HSTS)", "X-Content-Type-Options", "Referrer-Policy"],
            "answer": 3, "explanation": "HSTS 헤더는 브라우저가 일정 기간 동안 해당 사이트에 대해 HTTP 요청을 자동으로 HTTPS로 전환하여 전송하도록 강제합니다."
        },

        # 4과목: 정보보안 일반 (Q16 ~ Q20)
        {
            "id": "IW1_Q16", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "블록 암호화 운영 모드 중 동일한 평문 블록이 항상 동일한 암호문 블록을 생성하여 구조적 패턴이 노출되는 가장 단순한 운영 모드는?",
            "options": ["CBC 모드", "ECB 모드", "CFB 모드", "OFB 모드", "CTR 모드"],
            "answer": 2, "explanation": "ECB(Electronic Codebook) 모드는 각 블록을 독립적으로 암호화하여 평문 패턴이 암호문에 그대로 드러나 기밀성이 요구되는 환경에서 사용이 금지됩니다."
        },
        {
            "id": "IW1_Q17", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "군사적 기밀성을 보장하기 위한 보안 모델로, 'No Read Up (단순 보안)'과 'No Write Down (*-보안)' 속성을 갖는 접근통제 모델은?",
            "options": ["Biba 모델", "Bell-LaPadula (BLP) 모델", "Clark-Wilson 모델", "Chinese Wall 모델", "HRU 모델"],
            "answer": 2, "explanation": "Bell-LaPadula 모델은 기밀성을 위한 모델로 NRU(낮은 등급은 높은 등급 읽기 금지), NWD(높은 등급은 낮은 등급에 쓰기 금지) 규칙을 가집니다. 무결성 모델은 Biba입니다."
        },
        {
            "id": "IW1_Q18", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "PKI에서 인증서 폐지 목록(CRL)의 용량 과다 및 실시간성 결여 문제를 해결하기 위해 인증서 유효성 상태를 실시간 질의하는 프로토콜은?",
            "options": ["LDAP", "OCSP (Online Certificate Status Protocol)", "SCEP", "S/MIME", "CMP"],
            "answer": 2, "explanation": "OCSP는 클라이언트가 인증서 상태를 질의하면 실시간으로 Good, Revoked, Unknown 상태를 반환해 주는 경량 프로토콜입니다."
        },
        {
            "id": "IW1_Q19", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "사용자의 직무나 역할(Role)에 따라 권한을 부여하고, 최소 권한 원칙과 직무 분리(Separation of Duties)를 효과적으로 구현하는 접근통제 방식은?",
            "options": ["DAC (임의적 접근통제)", "MAC (강제적 접근통제)", "RBAC (역할기반 접근통제)", "Rule-based AC", "Identity-based AC"],
            "answer": 3, "explanation": "RBAC은 직무 역할에 권한을 할당하고 사용자에게 역할을 부여함으로써 관리 효율성과 직무 분리를 보장하는 기업 환경 표준 접근통제 모델입니다."
        },
        {
            "id": "IW1_Q20", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "해시 함수의 보안 특성 중, 주어진 해시값 h에 대해 H(x) = h를 만족하는 평문 x를 찾는 것이 계산적으로 불가능해야 한다는 특성은?",
            "options": ["제1 역상 저항성 (단방향성)", "제2 역상 저항성 (약한 충돌 저항성)", "강한 충돌 저항성", "눈사태 효과 (Avalanche Effect)", "기밀성"],
            "answer": 1, "explanation": "제1 역상 저항성은 결과값 h로부터 원본 x를 역산할 수 없어야 한다는 단방향성(Preimage Resistance)을 의미합니다."
        },

        # 5과목: 보안관리 및 법규 (Q21 ~ Q25)
        {
            "id": "IW1_Q21", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "개인정보 보호법상 개인정보가 유출되었음을 알게 된 때에 개인정보처리자가 정보주체에게 지체 없이 유출 사실을 통지해야 하는 법정 기한은?",
            "options": ["24시간 이내", "48시간 이내", "72시간 이내", "5일 이내", "7일 이내"],
            "answer": 3, "explanation": "개인정보 보호법 제34조에 따라 유출 사실을 알게 된 때로부터 정당한 사유가 없는 한 72시간 이내에 정보주체에게 통지해야 합니다."
        },
        {
            "id": "IW1_Q22", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "ISMS 의무 인증 대상자 기준 중 정보통신서비스 제공자의 매출액 및 일일평균 이용자 수 요건으로 올바른 것은?",
            "options": [
                "정보통신서비스 부문 전년도 매출액 50억원 이상 또는 일일평균 50만명 이상",
                "정보통신서비스 부문 전년도 매출액 100억원 이상 또는 직전 3개월간 일일평균 이용자 수 100만명 이상",
                "연간 총 매출액 100억원 이상 또는 일일평균 10만명 이상",
                "전년도 총 매출액 500억원 이상인 모든 법인",
                "자산총액 1,000억원 이상인 모든 상장회사"
            ],
            "answer": 2, "explanation": "정보통신망법상 ISMS 의무 대상 정보통신서비스 제공자는 전년도 정보통신서비스 매출액 100억원 이상이거나 직전 3개월 일일평균 이용자 수 100만명 이상인 자입니다."
        },
        {
            "id": "IW1_Q23", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "위험관리(Risk Management) 단계에서 최고경영진이 수용 가능한 위험 수준으로 정의하는 기준 지표를 뜻하는 약어는?",
            "options": ["ALE (Annualized Loss Expectancy)", "SLE (Single Loss Expectancy)", "DOA (Degree of Acceptance)", "ARO (Annualized Rate of Occurrence)", "MTBF"],
            "answer": 3, "explanation": "DOA(Degree of Acceptance)는 조직이 감수할 수 있는 수용 가능한 위험 수준으로, DOA를 초과하는 위험에 대해 정보보호 대책을 우선 수립합니다."
        },
        {
            "id": "IW1_Q24", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "개인정보 보호법상 정보주체의 동의 없이도 법령의 구체적 근거가 있어야만 처리가 허용되는 '고유식별정보' 4가지에 해당하지 않는 것은?",
            "options": ["주민등록번호", "여권번호", "운전면허번호", "외국인등록번호", "신용카드번호"],
            "answer": 5, "explanation": "법정 고유식별정보 4종은 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호입니다. 신용카드번호는 금융정보에 해당합니다."
        },
        {
            "id": "IW1_Q25", "category": "infosec_written", "exam": 1, "exam_name": "1회 필기 실전 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "정보통신망법상 일정 규모 이상의 대규모 기업에서 CISO가 겸직할 수 없도록 법률로 엄격히 제한하고 있는 직책은?",
            "options": ["개인정보보호책임자 (CPO)", "최고정보관리책임자 (CIO 및 전산/개발부서장)", "준법감시인 (Compliance Officer)", "보안운영팀장", "사내 정보보호위원회 간사"],
            "answer": 2, "explanation": "정보통신망법 제45조의3에 따라 대규모 기업의 CISO는 회사의 IT 인프라/개발을 총괄하는 CIO나 개발본부장 업무를 겸직할 수 없습니다. (단 CPO 겸직은 허용)"
        }
    ])

    # 2회 모의고사 (25문항: IW2_Q1 ~ IW2_Q25)
    q.extend([
        # 시스템 (Q26 ~ Q30)
        {
            "id": "IW2_Q1", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "리눅스 시스템에서 파일의 수정 시간(mtime), 접근 시간(atime), 권한/소유자 변경 시간(ctime) 중 파일 내용이 수정될 때 함께 갱신되는 시간의 조합은?",
            "options": ["atime만 갱신", "mtime과 ctime 갱신", "mtime만 갱신", "ctime만 갱신", "atime, mtime, ctime 모두 미갱신"],
            "answer": 2, "explanation": "파일 내용이 변경되면 수정 시간(mtime)이 변경되며, 파일의 크기 등 메타데이터가 변하므로 상태 변경 시간(ctime)도 함께 자동 갱신됩니다."
        },
        {
            "id": "IW2_Q2", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "프로그램이 자원을 확인하는 시점(Check)과 자원을 실제로 사용하는 시점(Use) 사이의 시간차를 이용하여 권한을 탈취하는 경쟁 조건(Race Condition) 취약점의 유형은?",
            "options": ["TOCTOU (Time of Check to Time of Use)", "Buffer Overflow", "Format String", "Use After Free", "Double Free"],
            "answer": 1, "explanation": "TOCTOU는 검사 시점과 사용 시점 사이의 지연을 노려 심볼릭 링크 등을 바꿔치기하여 권한을 상승시키는 전형적인 경쟁 조건 취약점입니다."
        },
        {
            "id": "IW2_Q3", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "리눅스 시스템의 /etc/shadow 파일의 두 번째 필드에 패스워드 해시가 '$6$salt$hash' 형태로 시작할 때, 사용된 일방향 해시 알고리즘은?",
            "options": ["MD5 ($1$)", "Blowfish ($2a$)", "SHA-256 ($5$)", "SHA-512 ($6$)", "DES"],
            "answer": 4, "explanation": "섀도우 파일의 암호 식별자는 $1$: MD5, $2a$: Blowfish, $5$: SHA-256, $6$: SHA-512 입니다."
        },
        {
            "id": "IW2_Q4", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "윈도우 운영체제에서 악성코드가 정상 실행 파일 뒤에 숨겨진 데이터 스트림을 생성하여 백신 탐지를 회피하는 NTFS 파일시스템의 고유 기능은?",
            "options": ["MFT (Master File Table)", "ADS (Alternate Data Streams)", "BitLocker", "EFS", "VSS"],
            "answer": 2, "explanation": "ADS(대체 데이터 스트림)는 파일 크기 표시 없이 숨겨진 스트림에 실행 파일이나 스크립트를 은닉할 수 있어 악성코드 은닉에 자주 악용됩니다."
        },
        {
            "id": "IW2_Q5", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 1, "subject_name": "1과목: 시스템 보안",
            "question": "C 언어의 printf 함수 등에서 포맷 지정자(%x, %s, %n)를 부적절하게 사용하여 스택 메모리를 노출시키거나 임의 주소에 값을 쓰는 취약점은?",
            "options": ["포맷 스트링 취약점 (Format String Bug)", "스택 버퍼 오버플로우", "정수 오버플로우", "메모리 누수", "널 포인터 역참조"],
            "answer": 1, "explanation": "포맷 스트링 취약점은 사용자의 입력을 printf(input)처럼 직접 포맷 인자로 전달할 때 %x로 메모리를 덤프하거나 %n으로 임의 메모리에 쓰기를 수행할 수 있는 취약점입니다."
        },

        # 네트워크 (Q31 ~ Q35)
        {
            "id": "IW2_Q6", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "IP 단편화(Fragmentation) 시 오프셋(Offset) 값을 비정상적으로 조작하여 패킷 재조합 과정에서 시스템 충돌(크래시)을 유발하는 DoS 공격은?",
            "options": ["TearDrop 공격", "Land 공격", "Smurf 공격", "SYN Flooding", "Ping of Death"],
            "answer": 1, "explanation": "TearDrop 공격은 IP 단편화 오프셋 필드가 서로 겹치거나 음수가 되도록 조작하여 수신 시스템이 패킷 재조합 시 메모리 오류로 다운되게 하는 공격입니다."
        },
        {
            "id": "IW2_Q7", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "네트워크 스니핑(Sniffing) 공격에 대한 설명 중 가장 옳지 않은 것은?",
            "options": [
                "스위칭 환경에서는 ARP 스푸핑이나 스위치 재밍(MAC Flooding)을 통해 트래픽을 유도할 수 있다.",
                "네트워크 카드를 무차별 모드(Promiscuous Mode)로 설정해야 모든 패킷을 수집할 수 있다.",
                "스니퍼 탐지 방법으로 Ping(ICMP), ARP, DNS, Trap 검사 등이 활용된다.",
                "SSH, HTTPS와 같은 종단 간 암호화 통신을 사용하더라도 스니핑을 통해 평문 패킷이 그대로 노출된다.",
                "정적 ARP 테이블(Static ARP)을 구성하면 ARP 스푸핑 기반 스니핑을 방어할 수 있다."
            ],
            "answer": 4, "explanation": "SSH, HTTPS, IPSec 등 암호화 통신 프로토콜을 사용하면 네트워크 상에서 패킷을 스니핑하더라도 암호화된 페이로드만 노출되므로 기밀성이 보장됩니다."
        },
        {
            "id": "IW2_Q8", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "방화벽 구축 형태 중 외부 네트워크와 내부 네트워크 사이에 완충 구역인 DMZ(스크린드 서브넷)를 배치하여 2대의 패킷 필터링 라우터와 베스천 호스트로 구성하는 가장 안전한 형태는?",
            "options": ["스크리닝 라우터 구조", "듀얼 홈드 게이트웨이", "스크린드 호스트 게이트웨이", "스크린드 서브넷 게이트웨이", "단일 방화벽 구조"],
            "answer": 4, "explanation": "스크린드 서브넷 게이트웨이는 외부 라우터와 내부 라우터 사이에 DMZ 망을 두어 다계층 심층 방어를 제공하는 가장 안전하고 표준적인 방화벽 구조입니다."
        },
        {
            "id": "IW2_Q9", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "DNS 질의응답 시 트랜잭션 ID와 출발지 포트를 무작위화하지 않는 취약점을 이용해 정당한 응답보다 먼저 위조된 DNS 응답을 캐시 서버에 주입하는 공격은?",
            "options": ["DNS 캐시 포이즈닝 (Kaminsky 공격)", "DNS 증폭 DDoS 공격", "Zone Transfer 공격", "ICMP 리다이렉트 공격", "DHCP 고갈 공격"],
            "answer": 1, "explanation": "DNS 캐시 포이즈닝은 DNS 질의 트랜잭션 ID와 포트를 추측하여 가짜 IP 매핑 정보를 DNS 캐시에 주입하여 사용자를 피싱 사이트로 유도하는 공격입니다."
        },
        {
            "id": "IW2_Q10", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 2, "subject_name": "2과목: 네트워크 보안",
            "question": "무선 네트워크 보안 표준 중 WPA2의 4-Way Handshake 사전 공격 취약점을 해결하고, 동등 동시 인증(SAE) 핸드셰이크를 도입한 최신 무선 보안 표준은?",
            "options": ["WEP", "WPA-TKIP", "WPA2-CCMP", "WPA3", "802.11b"],
            "answer": 4, "explanation": "WPA3는 SAE(Simultaneous Authentication of Equals) 프로토콜을 도입하여 사전 공격과 오프라인 키 복구 공격을 원천 차단하고 순방향 비밀성(PFS)을 제공합니다."
        },

        # 애플리케이션 (Q36 ~ Q40)
        {
            "id": "IW2_Q11", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "공격자가 웹 서버 내부 네트워크의 취약점을 탐색하거나 클라우드 메타데이터(169.254.169.254)를 탈취하기 위해 취약한 서버로 하여금 악의적 요청을 전송하게 하는 웹 취약점은?",
            "options": ["CSRF", "SSRF (Server-Side Request Forgery)", "XXE (XML External Entity)", "CORS 위반", "Insecure Deserialization"],
            "answer": 2, "explanation": "SSRF는 공격자가 서버를 경유하여 방화벽 내부의 비공개 자원이나 클라우드 인스턴스 메타데이터 API에 접근하도록 강제하는 대표적 취약점입니다."
        },
        {
            "id": "IW2_Q12", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "웹 응용프로그램이 XML 입력을 파싱할 때 외부 엔티티 참조를 허용하여 서버 로컬 파일(/etc/passwd)을 유출하거나 내부 포트를 스캔하는 공격은?",
            "options": ["XXE (XML External Entity) 공격", "XPath 인젝션", "XSS 공격", "LDAP 인젝션", "Template Injection"],
            "answer": 1, "explanation": "XXE 공격은 XML 파서가 DTD 외부 엔티티 처리를 비활성화하지 않았을 때 파일 유출 및 DoS를 유발하는 취약점입니다."
        },
        {
            "id": "IW2_Q13", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "데이터베이스 암호화 방식 중 암·복호화 모듈이 WAS 또는 애플리케이션 서버에서 직접 수행되어 DB 서버에 부하를 주지 않고 통신 구간까지 암호화되는 방식은?",
            "options": ["Plug-in 방식", "API 방식", "TDE (Transparent Data Encryption)", "커널(Kernel) 방식", "하드웨어 HSM 단독 방식"],
            "answer": 2, "explanation": "API 방식은 애플리케이션 서버에서 API를 호출해 암호화한 후 DB에 전달하므로 DB 서버 부하가 적고 네트워크 전송 구간까지 암호화가 보장됩니다."
        },
        {
            "id": "IW2_Q14", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "전자상거래 보안 프로토콜 SET(Secure Electronic Transaction)에서 고객의 결제 정보는 카드사만 보고, 주문 정보는 상점만 볼 수 있도록 분리 서명하는 핵심 암호화 기술은?",
            "options": ["이중 서명 (Dual Signature)", "블라인드 서명", "위임 서명", "은닉 서명", "영지식 증명"],
            "answer": 1, "explanation": "이중 서명은 주문 정보 해시와 결제 정보 해시를 합쳐 고객 개인키로 전자서명함으로써 상점과 카드사에게 불필요한 정보를 노출하지 않는 기술입니다."
        },
        {
            "id": "IW2_Q15", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 3, "subject_name": "3과목: 애플리케이션 보안",
            "question": "공격자가 악성 스크립트를 서버의 데이터베이스(게시글, 댓글)에 영구 저장시켜 해당 게시물을 열람하는 모든 불특정 다수 사용자에게 악성 코드를 실행시키는 XSS 유형은?",
            "options": ["Reflected XSS", "Stored (Persistent) XSS", "DOM-based XSS", "Self XSS", "mXSS"],
            "answer": 2, "explanation": "Stored XSS는 악성 스크립트가 서버 DB에 저장되어 페이지를 조회하는 모든 사용자에게 무차별 공격을 가하는 가장 위험도가 높은 XSS 유형입니다."
        },

        # 암호학 및 일반 (Q41 ~ Q45)
        {
            "id": "IW2_Q16", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "국내 한국인터넷진흥원(KISA)에서 개발한 128비트 블록 암호 알고리즘으로 스마트카드 및 IoT 기기 등에 최적화되어 Feistel 구조를 갖는 알고리즘은?",
            "options": ["SEED", "ARIA", "HIGHT", "LEA", "AES"],
            "answer": 1, "explanation": "SEED는 KISA가 개발한 128비트 블록, 128비트 키의 Feistel 구조 대칭키 암호화 표준입니다. (ARIA는 SPN 구조, HIGHT/LEA는 경량 암호)"
        },
        {
            "id": "IW2_Q17", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "비대칭키 암호 알고리즘 중 RSA 암호화의 수학적 안전성 기반이 되는 난제는?",
            "options": ["소인수분해 문제 (Prime Factorization)", "이산대수 문제 (Discrete Logarithm)", "타원곡선 이산대수 (ECDLP)", "배낭 문제 (Knapsack)", "격자 문제 (Lattice)"],
            "answer": 1, "explanation": "RSA는 매우 큰 두 소수의 곱을 구하기는 쉽지만 합성수를 다시 소인수분해하는 것은 계산적으로 어렵다는 점에 착안한 공개키 알고리즘입니다."
        },
        {
            "id": "IW2_Q18", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "데이터의 무결성(Integrity) 보장을 최우선으로 하는 보안 모델로, 'No Read Down'과 'No Write Up' 속성을 갖는 무결성 무결 모델은?",
            "options": ["Biba 모델", "Bell-LaPadula 모델", "Clark-Wilson 모델", "Chinese Wall 모델", "Take-Grant 모델"],
            "answer": 1, "explanation": "Biba 모델은 무결성 유지를 위해 낮은 무결성 데이터를 읽을 수 없고(NRD), 높은 무결성 데이터에 쓸 수 없는(NWU) 규칙을 갖습니다."
        },
        {
            "id": "IW2_Q19", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "금융 및 컨설팅 환경에서 이해관계의 충돌(Conflict of Interest)을 방지하기 위해 경쟁 기업 간의 정보 접근을 차단하는 동적 접근통제 모델은?",
            "options": ["Chinese Wall (Brewer-Nash) 모델", "Biba 모델", "BLP 모델", "RBAC", "MAC"],
            "answer": 1, "explanation": "Chinese Wall 모델은 동일한 컨설턴트가 경쟁 관계에 있는 기업들의 기밀 데이터를 동시에 열람하지 못하도록 접근 이력에 따라 장벽을 세우는 모델입니다."
        },
        {
            "id": "IW2_Q20", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 4, "subject_name": "4과목: 정보보안 일반",
            "question": "블록 암호화 운영 모드 중 이전 암호문 블록을 다음 평문 블록과 XOR 연산한 후 암호화하여 초기화 벡터(IV)가 필수적인 연쇄 모드는?",
            "options": ["CBC (Cipher Block Chaining) 모드", "ECB 모드", "CTR 모드", "OFB 모드", "CFB 모드"],
            "answer": 1, "explanation": "CBC 모드는 앞 블록의 암호문과 XOR 연산 후 암호화하므로 동일한 평문이라도 다른 암호문이 생성되며, 첫 블록 연산을 위해 초기화 벡터(IV)가 필요합니다."
        },

        # 법규 및 관리 (Q46 ~ Q50)
        {
            "id": "IW2_Q21", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "정보통신기반 보호법에 따른 '주요정보통신기반시설' 관리기관의 의무사항에 대한 설명으로 가장 옳지 않은 것은?",
            "options": [
                "관리기관의 장은 매년 소관 주요정보통신기반시설의 취약점을 분석·평가하여야 한다.",
                "취약점 분석·평가 결과를 바탕으로 정보보호대책을 수립하여 관계 중앙행정기관의 장에게 제출하여야 한다.",
                "침해사고가 발생하여 시설이 교란·마비된 경우 관계 중앙행정기관 및 과기정통부/국정원에 지체 없이 통지해야 한다.",
                "취약점 분석·평가는 전산실 직원 누구나 자체적으로 보고서 작성 없이 구두 보고로 대체할 수 있다.",
                "중요 정보보호 책임관을 지정하고 필요한 기술적·물리적 보호조치를 이행하여야 한다."
            ],
            "answer": 4, "explanation": "주요정보통신기반시설의 취약점 분석·평가는 관련 전문기관(KISA, 정보보호전문서비스기업 등) 또는 자체 전담반에 의해 매년 정밀하게 수행되고 정식 보고서로 관리되어야 합니다."
        },
        {
            "id": "IW2_Q22", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "개인정보 보호법상 개인정보 침해 사고로 인하여 개인정보보호위원회가 부과할 수 있는 전체 매출액 대비 과징금의 최대 법정 상한선은?",
            "options": ["전체 매출액의 1% 이하", "전체 매출액의 3% 이하", "전체 매출액의 5% 이하", "관련 매출액의 10% 이하", "최대 5억원 정액"],
            "answer": 2, "explanation": "개정 개인정보 보호법에 따라 고의 또는 중과실로 안전조치의무를 위반하여 개인정보가 유출된 경우 전체 매출액의 100분의 3(3%) 이하에 해당하는 금액을 과징금으로 부과할 수 있습니다."
        },
        {
            "id": "IW2_Q23", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "정량적 위험분석(Quantitative Risk Analysis)에서 연간예상손실액(ALE)을 계산하는 올바른 공식은?",
            "options": ["ALE = SLE × ARO", "ALE = 자산가치(AV) × 노출계수(EF)", "ALE = SLE / ARO", "ALE = (AV + EF) × ARO", "ALE = SLE × MTBF"],
            "answer": 1, "explanation": "연간예상손실액(ALE)은 1회 사고 발생 시 손실액인 단일예상손실액(SLE)에 연간발생률(ARO)을 곱하여 산출합니다. (SLE = AV × EF)"
        },
        {
            "id": "IW2_Q24", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "개인정보 영향평가(PIA) 수행 시 의무적으로 영향평가를 받아야 하는 공공기관 시스템 기준에 해당하지 않는 것은?",
            "options": [
                "5만명 이상의 정보주체에 관한 민감정보 또는 고유식별정보의 처리가 수반되는 시스템",
                "해당 공공기관 내부 또는 다른 공공기관의 개인정보파일과 연계하여 50만명 이상의 개인정보를 처리하는 시스템",
                "100만명 이상의 정보주체에 관한 개인정보파일을 구축·운용하는 시스템",
                "1만명 이상의 일반 회원 정보를 수집하는 일반 민간 스타트업 쇼핑몰 시스템",
                "영향평가를 받은 후 개인정보 검색체계 등 주요 기능이 변경되어 개인정보 수가 5만명 이상 증가한 시스템"
            ],
            "answer": 4, "explanation": "법정 개인정보 영향평가(PIA) 의무 대상은 공공기관에 한정되며 민간 쇼핑몰은 법적 의무 평가 대상이 아닙니다."
        },
        {
            "id": "IW2_Q25", "category": "infosec_written", "exam": 2, "exam_name": "2회 필기 고난도 모의고사",
            "subject_id": 5, "subject_name": "5과목: 보안관리 및 법규",
            "question": "위험 처리 전략 중 위험도가 높은 자산에 방화벽/백신을 도입하거나 접근통제를 강화하여 위험의 발생 가능성이나 손실을 낮추는 전략은?",
            "options": ["위험 감소 (Risk Reduction/Mitigation)", "위험 회피 (Risk Avoidance)", "위험 전가 (Risk Transference)", "위험 수용 (Risk Acceptance)", "위험 분산"],
            "answer": 1, "explanation": "위험 감소는 보안 통제를 설계·구현하여 위협의 발생 가능성이나 취약점을 줄여 잔여 위험을 낮추는 가장 일반적인 위험 처리 전략입니다."
        }
    ])
    return q

def get_practical_questions():
    q = []
    # 1회: 단답형 핵심 족보 (15문항)
    q.extend([
        {
            "id": "IP1_Q1", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 1, "subject_name": "1영역: 단답형 핵심 용어·명령어",
            "question": "[단답형 실무] 리눅스 환경에서 일반 사용자가 생성하는 기본 파일 권한을 640(rw-r-----), 디렉토리 권한을 750(rwxr-x---)으로 제한하기 위한 umask 설정값은?",
            "options": ["022", "027", "077", "033", "024"],
            "answer": 2, "explanation": "기본 파일 권한(666) - 027 = 640 / 기본 디렉토리 권한(777) - 027 = 750 입니다. 따라서 올바른 umask 값은 027입니다."
        },
        {
            "id": "IP1_Q2", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 1, "subject_name": "1영역: 단답형 핵심 용어·명령어",
            "question": "[단답형 실무] Apache 웹 서버(httpd.conf)에서 디렉토리 요청 시 index.html이 없을 때 디렉토리 내 파일 목록이 노출되는 취약점을 방지하기 위해 제거해야 하는 지시자는?",
            "options": ["FollowSymLinks", "Indexes", "MultiViews", "Includes", "ExecCGI"],
            "answer": 2, "explanation": "Options 항목에서 'Indexes'를 제거하거나 '-Indexes'로 설정하여 디렉토리 리스팅(Directory Listing)을 차단합니다."
        },
        {
            "id": "IP1_Q3", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 1, "subject_name": "1영역: 단답형 핵심 용어·명령어",
            "question": "[단답형 실무] 리눅스 시스템에서 특정 포트(예: 8080)를 열고 대기(LISTEN) 중인 프로세스의 PID와 프로세스명을 확인하기 위한 netstat 명령어 조합은?",
            "options": ["netstat -antp | grep 8080", "netstat -r", "netstat -i", "netstat -s", "netstat -u"],
            "answer": 1, "explanation": "netstat의 -a(모든 소켓), -n(숫자 표기), -t(TCP), -p(프로그램 PID) 옵션을 결합하여 특정 포트 점유 프로세스를 추적합니다."
        },
        {
            "id": "IP1_Q4", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 1, "subject_name": "1영역: 단답형 핵심 용어·명령어",
            "question": "[단답형 실무] 리눅스에서 시스템 관리자가 최근 24시간(1일) 이내에 내용이 수정된 파일을 점검하여 백도어 생성 여부를 파악하기 위한 find 옵션은?",
            "options": ["find / -mtime -1", "find / -atime +1", "find / -ctime +1", "find / -size +100M", "find / -nouser"],
            "answer": 1, "explanation": "-mtime -1 옵션은 최근 1일 이내에 수정(mtime)된 파일을 검색합니다. (+1은 1일 이전)"
        },
        {
            "id": "IP1_Q5", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 1, "subject_name": "1영역: 단답형 핵심 용어·명령어",
            "question": "[단답형 실무] 리눅스 TCP Wrapper 설정 시 특정 서비스(sshd)에 대해 모든 외부 접속을 기본 차단하고 특정 IP만 허용할 때, 우선 적용되는 설정 파일의 순서는?",
            "options": [
                "/etc/hosts.allow 검사 후 일치하지 않으면 /etc/hosts.deny 검사",
                "/etc/hosts.deny 검사 후 /etc/hosts.allow 검사",
                "/etc/resolv.conf 우선 검사",
                "/etc/security/limits.conf 단독 적용",
                "/etc/pam.d/sshd 단독 적용"
            ],
            "answer": 1, "explanation": "TCP Wrapper는 /etc/hosts.allow를 먼저 확인하여 허용 규칙이 있으면 즉시 허용하고, 없으면 hosts.deny를 확인하여 거부합니다. 둘 다 없으면 기본 허용됩니다."
        },
        {
            "id": "IP1_Q6", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 2, "subject_name": "2영역: 시스템·네트워크 설정 실무",
            "question": "[실무 룰셋] iptables를 사용하여 외부 IP(203.0.113.100)로부터 들어오는 80번 포트 웹 트래픽을 즉시 드롭(차단)하는 명령어로 올바른 것은?",
            "options": [
                "iptables -A INPUT -p tcp -s 203.0.113.100 --dport 80 -j DROP",
                "iptables -A OUTPUT -p tcp -d 203.0.113.100 --sport 80 -j DROP",
                "iptables -D INPUT -p tcp -s 203.0.113.100 -j ACCEPT",
                "iptables -P FORWARD DROP",
                "iptables -F INPUT"
            ],
            "answer": 1, "explanation": "유입 패킷은 INPUT 체인에 추가(-A), 출발지 IP(-s), 프로토콜(-p tcp), 목적지 포트(--dport 80), 조치 타겟(-j DROP)으로 구성합니다."
        },
        {
            "id": "IP1_Q7", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 2, "subject_name": "2영역: 시스템·네트워크 설정 실무",
            "question": "[실무 룰셋] Snort IDS에서 내부 사설망(192.168.1.0/24)을 향하는 TCP 패킷 중 페이로드에 '|0d 0a 0d 0a|' 문자열이 포함된 것을 탐지하는 룰 옵션 키워드는?",
            "options": ["content:\"|0d 0a 0d 0a|\";", "regex:\"|0d 0a 0d 0a|\";", "string:\"|0d 0a 0d 0a|\";", "payload:\"|0d 0a 0d 0a|\";", "pattern:\"|0d 0a 0d 0a|\";"],
            "answer": 1, "explanation": "Snort에서 바이너리(16진수) 패턴을 탐지할 때는 content:\"|16진수|\"; 문법을 사용합니다."
        },
        {
            "id": "IP1_Q8", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 2, "subject_name": "2영역: 시스템·네트워크 설정 실무",
            "question": "[실무 점검] 리눅스 서버에서 주기적으로 예약된 배치 작업을 점검하여 악성 백도어가 스케줄링되어 있는지 확인하기 위해 검사해야 하는 디렉토리가 아닌 것은?",
            "options": ["/var/spool/cron/", "/etc/cron.d/", "/etc/crontab", "/etc/cron.daily/", "/var/log/audit/"],
            "answer": 5, "explanation": "/var/log/audit/은 auditd 감사 로그 저장 디렉토리입니다. 크론 스케줄은 /var/spool/cron/, /etc/crontab, /etc/cron.* 에 등록됩니다."
        },
        {
            "id": "IP1_Q9", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 3, "subject_name": "3영역: 웹 취약점 진단·시큐어코딩",
            "question": "[시큐어코딩] 다음 코드 중 입력값 검증 없이 system() 함수에 외부 파라미터를 그대로 연결할 때 발생하는 치명적인 취약점은?\n\nString cmd = request.getParameter(\"cmd\");\nRuntime.getRuntime().exec(\"ping -c 3 \" + cmd);",
            "options": ["운영체제 명령어 삽입 (Command Injection)", "SQL Injection", "XSS", "CSRF", "LDAP Injection"],
            "answer": 1, "explanation": "외부 입력값을 검증하지 않고 시스템 명령어의 인자로 세미콜론(;)이나 파이프(|) 등과 함께 전달할 때 임의 명령어가 실행되는 Command Injection 취약점입니다."
        },
        {
            "id": "IP1_Q10", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 3, "subject_name": "3영역: 웹 취약점 진단·시큐어코딩",
            "question": "[시큐어코딩] Java 환경에서 SQL Injection을 방어하기 위해 Statement 객체 대신 반드시 사용해야 하는 인터페이스는?",
            "options": ["PreparedStatement", "CallableStatement", "ResultSet", "DriverManager", "ConnectionPool"],
            "answer": 1, "explanation": "PreparedStatement를 사용하여 ? 플레이스홀더에 파라미터를 바인딩하면 사용자 입력이 단순 값으로만 처리되어 SQL Injection이 방어됩니다."
        },
        {
            "id": "IP1_Q11", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 3, "subject_name": "3영역: 웹 취약점 진단·시큐어코딩",
            "question": "[시큐어코딩] XSS 공격을 방지하기 위해 사용자 출력값에서 반드시 HTML Entity로 치환해야 하는 핵심 특수문자 5가지가 올바르게 짝지어진 것은?",
            "options": [
                "&, <, >, \", '",
                "*, ?, %, $, #",
                "/, \\, :, ;, |",
                "{, }, [, ], ~",
                "+, -, =, !, @"
            ],
            "answer": 1, "explanation": "XSS 방어를 위한 5대 필수 치환 특수문자는 &(&amp;), <(&lt;), >(&gt;), \"(&quot;), '(&#x27;) 입니다."
        },
        {
            "id": "IP1_Q12", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 4, "subject_name": "4영역: 보안관리·침해사고 서술형",
            "question": "[서술 단답] 개인정보 유출 사고 인지 시 정보주체에게 통지해야 하는 법정 5대 통지 항목에 해당하지 않는 것은?",
            "options": [
                "유출된 개인정보의 항목",
                "유출된 시점과 그 경위",
                "정보주체가 피해를 최소화하기 위해 취할 수 있는 조치 방법",
                "개인정보처리자의 대응조치 및 피해 구제절차",
                "사고를 유발한 해커의 신원 및 IP 주소"
            ],
            "answer": 5, "explanation": "법정 5대 통지 항목: ① 유출 항목, ② 시점과 경위, ③ 피해 최소화 조치 방법, ④ 처리자의 대응 및 구제절차, ⑤ 담당부서 및 연락처입니다. 해커 신원은 통지 항목이 아닙니다."
        },
        {
            "id": "IP1_Q13", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 4, "subject_name": "4영역: 보안관리·침해사고 서술형",
            "question": "[서술 단답] NIST SP 800-61 침해사고 대응 라이프사이클의 4단계 순서가 올바르게 나열된 것은?",
            "options": [
                "사전 예방 및 준비 -> 탐지 및 분석 -> 봉쇄, 박멸 및 복구 -> 사고 후 활동(교훈)",
                "탐지 -> 복구 -> 보고 -> 종결",
                "위험평가 -> 보안대책 -> 내부감사 -> 재인증",
                "패치 적용 -> 방화벽 설정 -> 모니터링 -> 감사",
                "증거수집 -> 분석 -> 법적대응 -> 손실보상"
            ],
            "answer": 1, "explanation": "NIST 침해사고 대응 4단계: 1단계 Preparation, 2단계 Detection & Analysis, 3단계 Containment, Eradication & Recovery, 4단계 Post-Incident Activity(Lessons Learned) 입니다."
        },
        {
            "id": "IP1_Q14", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 4, "subject_name": "4영역: 보안관리·침해사고 서술형",
            "question": "[서술 단답] 디지털 포렌식의 5대 기본 원칙 중 증거가 최초 수집된 이후 법정에 제출될 때까지 위변조되지 않았음을 입증해야 한다는 원칙은?",
            "options": ["정당성의 원칙", "재현의 원칙", "무결성의 원칙 (Chain of Custody)", "신속성의 원칙", "연계보관성의 원칙"],
            "answer": 3, "explanation": "무결성의 원칙은 해시값(MD5/SHA-256) 비교 등을 통해 증거가 수집 시점부터 법정 제출 시점까지 동일함을 보장하는 원칙입니다."
        },
        {
            "id": "IP1_Q15", "category": "infosec_practical", "exam": 1, "exam_name": "단답형 핵심 족보 모의고사",
            "subject_id": 4, "subject_name": "4영역: 보안관리·침해사고 서술형",
            "question": "[서술 단답] 개인정보처리자가 데이터베이스에 비밀번호 저장 시 레인보우 테이블 공격 방지를 위해 사용자별로 결합해야 하는 무작위 값의 명칭은?",
            "options": ["솔트 (Salt)", "초기화 벡터 (IV)", "개인키", "세션 키", "토큰"],
            "answer": 1, "explanation": "솔트(Salt)는 비밀번호 해시 생성 시 무작위 문자열을 결합하여 동일한 비밀번호라도 서로 다른 해시값이 생성되도록 보장합니다."
        }
    ])

    # 2회: 서술형·로그/룰셋 실전 분석 (15문항)
    q.extend([
        {
            "id": "IP2_Q1", "category": "infosec_practical", "exam": 2, "exam_name": "서술형·실무형 실전 분석",
            "subject_id": 2, "subject_name": "2영역: 시스템·네트워크 설정 실무",
            "question": "[로그 분석] 다음 Apache 웹 서버 access.log 기록을 분석하여 공격자가 시도한 웹 공격의 명칭과 목적을 가장 정확히 기술한 것은?\n\n192.168.1.50 - - [12/Nov/2026:10:15:20 +0900] \"GET /board/view.php?id=1%20UNION%20SELECT%20null,username,password%20FROM%20users-- HTTP/1.1\" 200 4520",
            "options": [
                "공격명: Union-based SQL Injection / 목적: users 테이블의 관리자/사용자 계정 및 비밀번호 데이터 탈취",
                "공격명: Stored XSS / 목적: 사용자 쿠키 세션 탈취",
                "공격명: Directory Traversal / 목적: /etc/passwd 파일 열람",
                "공격명: Command Injection / 목적: 시스템 셸 획득",
                "공격명: CSRF / 목적: 사용자 비밀번호 강제 변경"
            ],
            "answer": 1, "explanation": "URL에 'UNION SELECT null,username,password FROM users--' 구문이 포함되어 데이터베이스의 다른 테이블(users) 내용을 결합 조회하여 계정 정보를 탈취하는 Union SQL Injection 공격입니다."
        },
        {
            "id": "IP2_Q2", "category": "infosec_practical", "exam": 2, "exam_name": "서술형·실무형 실전 분석",
            "subject_id": 2, "subject_name": "2영역: 시스템·네트워크 설정 실무",
            "question": "[로그 분석] 다음 access.log에서 발견되는 파라미터 '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd'가 의미하는 공격 기법과 방어 대책은?",
            "options": [
                "경로 순회(Path Traversal) 공격 / 입력값의 '../' 디렉토리 이동 문자열 필터링 및 화이트리스트 검증",
                "SQL Injection 공격 / PreparedStatement 사용",
                "XSS 공격 / HTML Entity 치환",
                "Buffer Overflow 공격 / 스택 카나리 적용",
                "SSRF 공격 / 메타데이터 IP 차단"
            ],
            "answer": 1, "explanation": "'%2e%2e%2f'는 '../'의 URL 인코딩 값으로, 웹 루트 상위 디렉토리로 이동하여 시스템 파일(/etc/passwd)을 열람하려는 경로 순회(Path Traversal) 공격입니다."
        },
        {
            "id": "IP2_Q3", "category": "infosec_practical", "exam": 2, "exam_name": "서술형·실무형 실전 분석",
            "subject_id": 3, "subject_name": "3영역: 웹 취약점 진단·시큐어코딩",
            "question": "[시큐어코딩] 파일 업로드 취약점을 차단하기 위한 시큐어코딩 3대 안전 수칙으로 가장 올바른 조합은?",
            "options": [
                "① 실행 가능한 확장자(.php, .jsp, .asp 등) 화이트리스트 검증, ② 저장 시 파일명 난수화(UUID), ③ 업로드 디렉토리의 웹 실행 권한 제거(No-Exec)",
                "① 클라이언트 자바스크립트 확장자 검증, ② 원래 파일명 유지, ③ 777 권한 부여",
                "① 파일 크기만 1MB 이하로 제한, ② 실행 권한 부여, ③ 루트 디렉토리에 저장",
                "① GET 방식으로만 업로드, ② 파일 내용 평문 출력, ③ 브라우저 캐싱",
                "① 쿠키에 파일명 저장, ② 세션 만료 시간 연장, ③ POST 파라미터 암호화"
            ],
            "answer": 1, "explanation": "안전한 파일 업로드는 ① 서버 단 화이트리스트 확장자 검증, ② 파일명 난수화(UUID), ③ 웹 루트 외부 또는 실행 권한 없는 디렉토리 저장이 핵심입니다."
        },
        {
            "id": "IP2_Q4", "category": "infosec_practical", "exam": 2, "exam_name": "서술형·실무형 실전 분석",
            "subject_id": 2, "subject_name": "2영역: 시스템·네트워크 설정 실무",
            "question": "[서술 실무] SSH 무차별 대입 공격(Brute Force)을 방어하기 위해 /etc/ssh/sshd_config 파일에 설정해야 하는 핵심 보안 지시자 3가지는?",
            "options": [
                "PermitRootLogin no, Port 2222(기본포트 변경), MaxAuthTries 5",
                "PermitRootLogin yes, Port 22, PasswordAuthentication yes",
                "Protocol 1, MaxAuthTries 100, PermitEmptyPasswords yes",
                "X11Forwarding yes, AllowTcpForwarding yes, Port 22",
                "ListenAddress 0.0.0.0, PermitRootLogin yes, ClientAliveCountMax 0"
            ],
            "answer": 1, "explanation": "SSH 서버 보안 설정의 핵심은 root 직접 로그인 차단(PermitRootLogin no), 기본 22번 포트 변경, 인증 실패 제한(MaxAuthTries 3~5), 비밀번호 없는 접속 금지(PermitEmptyPasswords no)입니다."
        },
        {
            "id": "IP2_Q5", "category": "infosec_practical", "exam": 2, "exam_name": "서술형·실무형 실전 분석",
            "subject_id": 4, "subject_name": "4영역: 보안관리·침해사고 서술형",
            "question": "[서술 실무] 개인정보 취급자의 접속기록을 점검할 때 개인정보의 안전성 확보조치 기준에 따라 최소한 월 1회 이상 확인해야 하는 3대 이상징후는?",
            "options": [
                "① 근무시간 외 접속, ② 대량의 개인정보 다운로드/조회, ③ 단기간 다수의 조회/수정 실패",
                "① 정상 업무 시간 접속, ② 단일 건 조회, ③ 비밀번호 정상 변경",
                "① 정기 백업 수행, ② 신규 직원 등록, ③ 백신 업데이트",
                "① IP 정상 할당, ② 방화벽 통과 이력, ③ 세션 정상 종료",
                "① 휴가 신청 기록, ② 결재 완료 내역, ③ 메일 발송 건수"
            ],
            "answer": 1, "explanation": "접속기록 점검 시 이상징후: 비인가 시간대(심야/주말) 접속, 대량 개인정보 다운로드, 권한 외 조회 및 비정상적 반복 실패 이력 등을 집중 모니터링해야 합니다."
        }
    ])
    return q

def get_ismsp_questions():
    q = []
    # 1회 모의고사 (15문항)
    q.extend([
        {
            "id": "ISMSP1_Q1", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 1, "subject_name": "1영역: 관리체계 수립·운영 (16개)",
            "question": "[결함 판정] 대규모 전자상거래 기업에서 CISO가 개발본부장(CIO)을 겸직하여 정보시스템 개발 및 인프라 운영 업무를 총괄 관리하도록 발령한 경우 위반되는 인증기준은?",
            "options": ["1.1.1 경영진의 참여", "1.1.2 최고책임자의 지정", "1.1.3 조직 구성", "1.1.4 범위 설정", "1.2.1 위험 식별"],
            "answer": 2, "explanation": "ISMS-P 1.1.2 및 망법에 따라 일정 규모 이상 기업의 CISO는 회사의 다른 IT 부문 업무(CIO, 개발본부장 등)를 겸직할 수 없습니다."
        },
        {
            "id": "ISMSP1_Q2", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 1, "subject_name": "1영역: 관리체계 수립·운영 (16개)",
            "question": "[결함 판정] 정기 위험평가를 실시하여 위험도를 도출하였으나, 최고경영진이 승인한 수용 가능한 위험 수준(DOA)의 기준치가 정의되어 있지 않아 조치 대상을 객관적으로 선별할 수 없었던 사례가 위반한 기준은?",
            "options": ["1.2.1 위험 식별 및 분석", "1.2.2 위험 평가 및 정보보호 대책 수립", "1.1.1 경영진의 참여", "1.4.2 관리체계 점검", "1.3.1 보호대책 공유"],
            "answer": 2, "explanation": "1.2.2 기준에 따라 조직의 환경을 고려하여 경영진이 승인한 DOA(Degree of Acceptance) 기준을 수립하고 이를 초과하는 위험에 대해 대책을 마련해야 합니다."
        },
        {
            "id": "ISMSP1_Q3", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 1, "subject_name": "1영역: 관리체계 수립·운영 (16개)",
            "question": "[결함 판정] 인증심사 범위에 포함된 신규 모바일 앱 서비스와 클라우드 인프라 자산이 자산관리 대장에 누락되어 위험평가 대상에서 제외된 사례가 위반한 기준은?",
            "options": ["1.1.4 범위 설정", "1.1.1 경영진의 참여", "1.3.2 이행점검", "1.4.1 법적 요구사항 검토", "1.2.2 위험 평가"],
            "answer": 1, "explanation": "1.1.4 기준은 인증 범위 내의 모든 정보자산, 서비스, 네트워크, 개인정보 처리 흐름도를 누락 없이 식별하여 관리체계 범위로 설정하도록 요구합니다."
        },
        {
            "id": "ISMSP1_Q4", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 2, "subject_name": "2영역: 보호대책 요구사항 (64개)",
            "question": "[결함 판정] ISMS-P 2.6.7(접속기록 보관 및 점검) 기준상 5만명 이상의 고유식별정보 또는 민감정보를 처리하는 대규모 개인정보처리시스템의 접속기록 보관 및 점검 요건으로 올바른 것은?",
            "options": [
                "최소 1년 이상 보관, 분기 1회 점검",
                "최소 1년 이상 보관, 월 1회 점검",
                "최소 2년 이상 보관, 월 1회 점검",
                "최소 2년 이상 보관, 반기 1회 점검",
                "최소 3년 이상 보관, 연 1회 점검"
            ],
            "answer": 3, "explanation": "안전성 확보조치 기준 제8조에 따라 5만명 이상의 민감정보 또는 고유식별정보 처리 시스템은 접속기록을 2년 이상 보관하고 월 1회 이상 점검해야 합니다."
        },
        {
            "id": "ISMSP1_Q5", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 2, "subject_name": "2영역: 보호대책 요구사항 (64개)",
            "question": "[결함 판정] 관리자 시스템의 초기 패스워드를 'Welcome123!'으로 일괄 부여하고, 최초 로그인 시 패스워드 변경을 강제하지 않아 수개월간 초기 패스워드가 방치된 사례가 위반한 기준은?",
            "options": ["2.5.1 사용자 식별", "2.5.4 비밀번호 관리", "2.6.1 네트워크 접근", "2.7.1 암호정책 적용", "2.5.2 사용자 인증"],
            "answer": 2, "explanation": "2.5.4 기준에 따라 초기 비밀번호는 최초 접속 시 반드시 변경하도록 강제 통제해야 합니다."
        },
        {
            "id": "ISMSP1_Q6", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 2, "subject_name": "2영역: 보호대책 요구사항 (64개)",
            "question": "[결함 판정] 개발 및 테스트 환경에서 실제 운영 DB의 고객 이름, 휴대폰번호, 주민등록번호 데이터를 마스킹이나 가명처리 없이 그대로 복사하여 사용한 사례가 위반한 기준은?",
            "options": ["2.8.5 시험 데이터 보안", "2.6.2 개발망/운영망 분리", "2.7.1 암호정책 적용", "2.9.1 운영절차 관리", "2.8.1 보안시스템 개발"],
            "answer": 1, "explanation": "2.8.5(시험 데이터 보안) 기준에 따라 시스템 개발, 테스트 시 원칙적으로 실제 개인정보 사용이 금지되며, 부득이한 경우 가명·익명화 처리를 해야 합니다."
        },
        {
            "id": "ISMSP1_Q7", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 2, "subject_name": "2영역: 보호대책 요구사항 (64개)",
            "question": "[결함 판정] 퇴사자가 발생하였으나 인사팀에서 보안/전산팀으로 통보가 지연되어 퇴사한 지 2주가 지난 직원의 사내 인트라넷 및 VPN 계정이 여전히 활성화되어 있던 사례가 위반한 기준은?",
            "options": ["2.2.3 퇴직 및 직무변경", "2.5.1 사용자 식별", "2.6.1 네트워크 접근", "2.3.1 외주용역 보안", "2.1.2 조직 구성"],
            "answer": 1, "explanation": "2.2.3(퇴직 및 직무변경) 기준에 따라 퇴직 시 정보자산 반납 및 모든 접근 권한의 즉시 회수/비활성화가 이루어져야 합니다."
        },
        {
            "id": "ISMSP1_Q8", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 2, "subject_name": "2영역: 보호대책 요구사항 (64개)",
            "question": "[결함 판정] 운영 데이터베이스에 저장된 주민등록번호와 비밀번호를 평문(Plaintext)으로 저장하여 보관하고 있던 사례가 위반한 기준은?",
            "options": ["2.7.1 암호정책 적용", "2.6.2 개발/운영 분리", "2.5.4 비밀번호 관리", "2.9.2 성능 및 용량 관리", "2.8.4 보안성 검토"],
            "answer": 1, "explanation": "2.7.1(암호정책 적용) 기준에 따라 고유식별정보와 비밀번호(일방향 해시)는 저장 시 반드시 안전한 알고리즘으로 암호화하여야 합니다."
        },
        {
            "id": "ISMSP1_Q9", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 3, "subject_name": "3영역: 개인정보 처리단계별 (22개)",
            "question": "[결함 판정] 회원가입 웹페이지에서 마케팅 활용 목적의 '생년월일'과 '관심사'를 필수항목으로 지정하고 미동의 시 기본 회원가입을 거부한 사례가 위반한 기준은?",
            "options": ["3.1.2 수집 제한 및 최소 수집", "3.1.1 수집 동의 기준", "3.2.1 개인정보 현황 관리", "3.3.1 제3자 제공", "3.5.1 권리 보장"],
            "answer": 1, "explanation": "3.1.2 기준에 따라 선택항목 미제공을 이유로 기본 서비스 제공을 거부할 수 없습니다."
        },
        {
            "id": "ISMSP1_Q10", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 3, "subject_name": "3영역: 개인정보 처리단계별 (22개)",
            "question": "[결함 판정] 보유기간(3년)이 도래한 이벤트 참여자 개인정보를 파기하지 않고 향후 마케팅 홍보에 재사용하기 위해 운영 DB에 방치한 사례가 위반한 기준은?",
            "options": ["3.4.1 개인정보 파기", "3.2.2 개인정보 품질 관리", "3.1.1 수집 동의 기준", "3.3.2 업무 위탁", "3.5.2 정보주체 통지"],
            "answer": 1, "explanation": "3.4.1 기준에 따라 보유기간 경과 또는 처리 목적 달성 시 지체 없이(5일 이내) 복구 불가능한 방법으로 영구 파기해야 합니다."
        },
        {
            "id": "ISMSP1_Q11", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 3, "subject_name": "3영역: 개인정보 처리단계별 (22개)",
            "question": "[결함 판정] 고객 배송 업무를 택배사에 위탁하면서 위탁계약서에 재위탁 제한 및 안전조치 의무 규정을 누락하고, 연 1회 수탁사 관리·감독 점검을 전혀 실시하지 않은 사례가 위반한 기준은?",
            "options": ["3.3.2 업무 위탁에 따른 관리·감독", "3.3.1 개인정보의 제3자 제공", "3.1.1 수집 동의 기준", "3.4.1 개인정보 파기", "2.3.1 외주용역 보안"],
            "answer": 1, "explanation": "3.3.2 기준에 따라 위탁 계약 시 법정 필수사항(목적, 재위탁 제한, 안전조치)을 문서화하고 연 1회 이상 수탁사의 처리 실태를 정기 점검해야 합니다."
        },
        {
            "id": "ISMSP1_Q12", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 3, "subject_name": "3영역: 개인정보 처리단계별 (22개)",
            "question": "[결함 판정] 정보주체가 자신의 개인정보에 대한 열람 및 삭제를 요구하였으나 정당한 사유나 통지 없이 법정 기한(10일)이 넘도록 아무런 조치를 취하지 않은 사례가 위반한 기준은?",
            "options": ["3.5.1 정보주체 권리보장", "3.4.1 개인정보 파기", "3.2.1 개인정보 현황 관리", "3.1.2 수집 제한", "1.4.1 법적 요구사항"],
            "answer": 1, "explanation": "3.5.1 기준에 따라 정보주체의 열람, 정정, 삭제 요구에 대해 10일 이내에 조치 결과를 회신하여야 합니다."
        },
        {
            "id": "ISMSP1_Q13", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 2, "subject_name": "2영역: 보호대책 요구사항 (64개)",
            "question": "[결함 판정] 개인정보처리시스템의 서버 접속 로그 파일이 저장된 디렉토리에 대해 백업을 수행하지 않고, 관리자 계정으로 로그 파일을 임의로 삭제하거나 위조할 수 있도록 쓰기 권한이 부여된 사례가 위반한 기준은?",
            "options": ["2.6.7 접속기록 보관 및 점검", "2.9.3 백업 및 복구", "2.5.3 특권 계정 관리", "2.7.2 암호키 관리", "2.10.1 침해사고 대응"],
            "answer": 1, "explanation": "2.6.7 기준에 따라 접속기록은 위·변조 및 도난, 분실되지 않도록 안전한 별도 저장소에 백업 보관하고 접근 권한을 최소화하여야 합니다."
        },
        {
            "id": "ISMSP1_Q14", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 2, "subject_name": "2영역: 보호대책 요구사항 (64개)",
            "question": "[결함 판정] 전산실 및 통제구역 출입문에 전자식 출입통제 시스템이 설치되어 있으나, 방문자의 출입 수기 대장이 비치되어 있지 않고 출입 로그가 1개월만 보관된 후 삭제된 사례가 위반한 기준은?",
            "options": ["2.4.1 출입통제", "2.4.2 물리적 보호구역 지정", "2.4.4 전산실 보호", "2.6.1 네트워크 접근", "2.2.1 임직원 보안"],
            "answer": 1, "explanation": "2.4.1(출입통제) 기준에 따라 통제구역에 대한 출입기록은 최소 1년(또는 3년) 이상 보관하고 정기적으로 검토하여야 합니다."
        },
        {
            "id": "ISMSP1_Q15", "category": "ismsp_auditor", "exam": 1, "exam_name": "1회 실전 결함판정 모의고사",
            "subject_id": 3, "subject_name": "3영역: 개인정보 처리단계별 (22개)",
            "question": "[결함 판정] 개인정보 처리방침에 기재된 수집 항목에는 '이메일'만 명시되어 있으나 실제 회원가입 시 '자택 전화번호'와 '직장명'을 추가 수집하여 처리방침과 실제 처리 현황이 불일치한 사례가 위반한 기준은?",
            "options": ["3.2.1 개인정보 현황 관리", "3.1.1 수집 동의 기준", "3.1.2 최소 수집", "3.5.2 개인정보 처리방침 공개", "1.1.4 범위 설정"],
            "answer": 1, "explanation": "3.2.1(개인정보 현황 관리) 기준에 따라 개인정보 처리방침 및 내부 관리대장과 실제 시스템에서 수집·이용되는 개인정보 항목은 100% 일치해야 합니다."
        }
    ])
    return q

def main():
    written_q = get_written_questions()
    practical_q = get_practical_questions()
    ismsp_q = get_ismsp_questions()

    written_data = {
        "name": "정보보안기사 (필기)",
        "badge": "국가기술자격",
        "desc": "시스템·네트워크·애플리케이션·정보보안일반·법규 5대 전 과목 핵심 기출 모의고사(총 50문항) 및 과목별 심층 요약노트",
        "subjects": [
            {"id": 1, "name": "1과목: 시스템 보안"},
            {"id": 2, "name": "2과목: 네트워크 보안"},
            {"id": 3, "name": "3과목: 애플리케이션 보안"},
            {"id": 4, "name": "4과목: 정보보안 일반"},
            {"id": 5, "name": "5과목: 보안관리 및 법규"}
        ],
        "questions": written_q,
        "summaries": [
            {
                "title": "1과목. 시스템 보안 핵심 요약집",
                "topics": [
                    {
                        "name": "리눅스 계정·권한 및 핵심 취약점",
                        "points": [
                            "SetUID(4000) / SetGID(2000) / Sticky bit(1000): 점검 명령 'find / -perm -4000 -type f'.",
                            "PAM 인증 플래그: required(실패해도 스택 계속 실행 후 최종 실패), requisite(실패 시 즉시 중단), sufficient(성공 시 즉시 통과).",
                            "패스워드 파일: /etc/passwd(644), /etc/shadow(400/000). SHA-512($6$), SHA-256($5$), MD5($1$).",
                            "로그 파일: wtmp(last, 로그인/로그아웃), utmp(who, 현재 접속자), btmp(lastb, 로그인 실패), lastlog(lastlog, 최근 접속)."
                        ]
                    },
                    {
                        "name": "메모리 공격 기법 및 OS 방어 기술",
                        "points": [
                            "스택 버퍼 오버플로우: 버퍼 크기 초과 입력으로 복귀 주소(RET)를 변조해 악성 셸코드 실행.",
                            "ASLR: 스택, 힙, 라이브러리 주소를 실행 시마다 무작위로 재배치하여 고정 주소 점프 공격 차단.",
                            "DEP / NX: 데이터 영역(스택, 힙)의 실행 권한을 박탈하여 셸코드 실행 원천 금지.",
                            "스택 카나리: 함수 프롤로그에서 RET 앞에 무작위 값을 삽입하고 에필로그에서 변조 여부 검사."
                        ]
                    },
                    {
                        "name": "윈도우 보안 아키텍처",
                        "points": [
                            "SRM(보안 참조 모니터): 커널 모드에서 사용자 토큰과 객체 DACL을 대조하여 접근 허가 및 감사 로그 생성.",
                            "LSA(로컬 보안 권한): 로컬 보안 정책 관리 및 감사 로그 생성, NTLM/Kerberos 인증 중계.",
                            "SAM(보안 계정 관리자): 로컬 사용자 계정 및 비밀번호 해시 저장(%SystemRoot%\\System32\\config\\SAM)."
                        ]
                    }
                ]
            },
            {
                "title": "2과목. 네트워크 보안 핵심 요약집",
                "topics": [
                    {
                        "name": "네트워크 공격 및 DoS/DDoS 공격 기법",
                        "points": [
                            "TCP SYN Flooding: 3-Way Handshake 백로그 큐 고갈. 대응: SYN Cookie, Backlog 확장.",
                            "Smurf Attack: 출발지 IP를 희생자 IP로 위조하여 브로드캐스트 주소로 ICMP Echo Request 전송.",
                            "Land Attack: 출발지 IP/Port와 목적지 IP/Port를 희생자 시스템으로 동일하게 스푸핑.",
                            "TearDrop: IP 단편화 오프셋 필드가 중첩되거나 음수가 되도록 조작하여 패킷 재조합 시 크래시 유발.",
                            "스텔스 스캔: FIN, Null, Xmas 스캔은 포트가 열려 있으면 무응답, 닫혀 있으면 RST 회신."
                        ]
                    },
                    {
                        "name": "IPSec 프로토콜 및 방화벽/IDS",
                        "points": [
                            "AH (IP 51): 무결성 및 발신처 인증 제공, 기밀성(암호화) 제공 안 함. NAT 환경 통과 불가.",
                            "ESP (IP 50): 기밀성, 무결성, 인증 모두 제공. NAT-T(UDP 4500) 지원.",
                            "전송 모드(IP 페이로드만 보호) vs 터널 모드(패킷 전체 보호 + 신규 IP 헤더 추가).",
                            "방화벽 구조: 스크린드 서브넷(DMZ 배치, 외부/내부 라우터 2대 + 베스천 호스트)이 가장 안전.",
                            "Snort 룰 문법: alert tcp any any -> 192.168.1.0/24 80 (msg; content; nocase; sid;)"
                        ]
                    }
                ]
            },
            {
                "title": "3과목. 애플리케이션 보안 핵심 요약집",
                "topics": [
                    {
                        "name": "웹 취약점(OWASP Top 10) 및 시큐어코딩",
                        "points": [
                            "SQL Injection: 사용자 입력이 쿼리 문법으로 해석되는 취약점. 대응: PreparedStatement 바인딩 필수.",
                            "XSS: 악성 스크립트 실행. 대응: 입출력 5대 특수문자(&, <, >, \", ') HTML Entity 치환, HttpOnly 쿠키 플래그.",
                            "CSRF: 사용자 권한 도용 요청 전송. 대응: CSRF 토큰 검증, 재인증, SameSite=Strict 쿠키.",
                            "SSRF: 서버가 내부 사설망이나 클라우드 메타데이터(169.254.169.254)로 요청하도록 유도하는 취약점."
                        ]
                    },
                    {
                        "name": "이메일 인증 및 데이터베이스 암호화",
                        "points": [
                            "SPF: DNS에 등록된 발송 메일 서버 IP 대조 검증.",
                            "DKIM: 메일 헤더에 개인키 전자서명을 부착하고 DNS 공개키로 무결성 검증.",
                            "DMARC: SPF와 DKIM 인증 결과를 기반으로 차단/격리 정책 수립.",
                            "DB 암호화 방식: API 방식(WAS에서 암호화, 전송구간 보호), Plug-in(DB 내부 모듈), TDE(스토리지 파일 레벨 암호화)."
                        ]
                    }
                ]
            },
            {
                "title": "4과목 & 5과목. 정보보안 일반 및 법규 요약집",
                "topics": [
                    {
                        "name": "암호 알고리즘 및 보안 모델",
                        "points": [
                            "대칭키: 블록 암호(AES, SEED, ARIA, DES), 스트림 암호(RC4). ECB 모드는 패턴 노출로 사용 금지, CBC 모드는 IV 필수.",
                            "비대칭키: 소인수분해(RSA), 이산대수(Diffie-Hellman, DSA, ElGamal), 타원곡선(ECC).",
                            "BLP 모델: 기밀성 우선. No Read Up(단순 보안), No Write Down(*-보안 속성).",
                            "Biba 모델: 무결성 우선. No Read Down(단순 무결성), No Write Up(*-무결성 속성)."
                        ]
                    },
                    {
                        "name": "개인정보보호법 및 망법 핵심 규정",
                        "points": [
                            "유출 통지: 유출 사실 인지 시 지체 없이 72시간 이내 정보주체 통지, 1천명 이상 유출 시 보호위/KISA 신고.",
                            "과징금 상한: 개정 개인정보보호법상 전체 매출액의 3% 이하 부과 가능.",
                            "CISO 겸직 금지: 대규모 기업의 CISO는 CIO/개발본부장 겸직 불가 (CPO 겸직은 허용).",
                            "위험분석 공식: ALE = SLE × ARO (SLE = 자산가치 AV × 노출계수 EF)."
                        ]
                    }
                ]
            }
        ]
    }

    practical_data = {
        "name": "정보보안기사 (실기)",
        "badge": "국가기술자격",
        "desc": "실기 단답형 기출 족보(15문항) · 서술형/실무형 분석(15문항) 총 30문항 및 실무 설정·시큐어코딩 핵심 가이드",
        "subjects": [
            {"id": 1, "name": "1영역: 단답형 핵심 용어·명령어"},
            {"id": 2, "name": "2영역: 시스템·네트워크 설정 실무"},
            {"id": 3, "name": "3영역: 웹 취약점 진단·시큐어코딩"},
            {"id": 4, "name": "4영역: 보안관리·침해사고 서술형"}
        ],
        "questions": practical_q,
        "summaries": [
            {
                "title": "실기 필수 1. 시스템 설정 & 명령어 족보",
                "topics": [
                    {
                        "name": "리눅스 계정·권한 및 방화벽 설정",
                        "points": [
                            "umask 계산법: 파일 666 - umask = 파일권한 / 디렉토리 777 - umask = 디렉토리권한. (umask 027 -> 640 / 750)",
                            "SetUID 점검: find / -perm -4000 -type f -exec ls -al {} \\;",
                            "iptables 특정 IP 차단: iptables -A INPUT -p tcp -s 203.0.113.100 --dport 80 -j DROP",
                            "SSH 보안 설정: PermitRootLogin no, Port 2222, MaxAuthTries 5, Protocol 2"
                        ]
                    },
                    {
                        "name": "로그 분석 및 이상 징후 추적 명령어",
                        "points": [
                            "최근 접속 및 실패 확인: last(wtmp), lastb(btmp), lastlog(lastlog)",
                            "열린 포트 및 점유 PID: netstat -antp | grep LISTEN 또는 ss -tuln",
                            "최근 1일 내 수정 파일: find / -mtime -1 -type f",
                            "스케줄링 백도어 점검: crontab -l, cat /etc/crontab, ls -al /var/spool/cron/"
                        ]
                    }
                ]
            },
            {
                "title": "실기 필수 2. 웹 진단·시큐어코딩 & 법규 실무",
                "topics": [
                    {
                        "name": "웹 서버 및 소프트웨어 보안약점 조치",
                        "points": [
                            "Apache Directory Listing 차단: httpd.conf Options 지시자에서 'Indexes' 제거 또는 '-Indexes'.",
                            "SQL Injection 조치: Statement -> PreparedStatement 바인딩 매개변수(?) 사용.",
                            "XSS 조치: 5대 특수문자(& -> &amp;, < -> &lt;, > -> &gt;, \" -> &quot;, ' -> &#x27;) HTML 치환 및 HttpOnly 플래그.",
                            "파일 업로드 조치: 화이트리스트 확장자 검증 + 파일명 난수화(UUID) + 실행 권한 제거(No-Exec)."
                        ]
                    },
                    {
                        "name": "침해사고 대응 및 디지털 포렌식 원칙",
                        "points": [
                            "NIST 침해사고 대응 4단계: 준비 -> 탐지 및 분석 -> 봉쇄, 박멸 및 복구 -> 사고 후 활동(교훈).",
                            "포렌식 5대 원칙: 정당성, 재현성, 신속성, 연계보관성, 무결성(해시값 일치 검증).",
                            "개인정보 유출 통지 항목: 항목, 시점/경위, 피해 최소화 조치, 대응/구제절차, 담당부서 연락처 (72시간 이내)."
                        ]
                    }
                ]
            }
        ]
    }

    ismsp_data = {
        "name": "ISMS-P 인증심사원",
        "badge": "국가전문자격",
        "desc": "1영역 관리체계(16개) · 2영역 보호대책(64개) · 3영역 개인정보(22개) 102개 기준별 실전 결함판정 시나리오 퀴즈(총 30문항) 및 결함사례 총람",
        "subjects": [
            {"id": 1, "name": "1영역: 관리체계 수립·운영 (16개)"},
            {"id": 2, "name": "2영역: 보호대책 요구사항 (64개)"},
            {"id": 3, "name": "3영역: 개인정보 처리단계별 (22개)"}
        ],
        "questions": ismsp_q,
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
    }

    js_code = f"""// infosec_exam_data.js
// 정보보안기사(필기 50제), 정보보안기사(실기 30제), ISMS-P 인증심사원(30제) 대규모 실전 문제 및 요약 데이터셋

window.INFOSEC_WRITTEN_DATA = {json.dumps(written_data, ensure_ascii=False, indent=2)};

window.INFOSEC_PRACTICAL_DATA = {json.dumps(practical_data, ensure_ascii=False, indent=2)};

window.ISMSP_AUDITOR_DATA = {json.dumps(ismsp_data, ensure_ascii=False, indent=2)};
"""
    with open("infosec_exam_data.js", "w", encoding="utf-8") as f:
        f.write(js_code)
    print("-> infosec_exam_data.js successfully generated with rich datasets!")

if __name__ == "__main__":
    main()

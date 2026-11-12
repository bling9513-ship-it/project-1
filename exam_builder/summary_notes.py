# -*- coding: utf-8 -*-
"""
summary_notes.py
2026 이기적 정보보안기사 필기+실기 올인원 1권 이론서 & 핵심용어 108선 편제 요약집
- PART 01 시스템 보안
- PART 02 네트워크 보안
- PART 03 애플리케이션 보안
- PART 04 정보보안 일반
- PART 05 정보보안 관리 및 법률
- [특별부록] 합격 핵심용어 108선 엄선 요약집
"""

def get_written_summary():
    return {
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

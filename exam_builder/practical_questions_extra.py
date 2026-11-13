# -*- coding: utf-8 -*-
"""
practical_questions_extra.py
2026 이기적 정보보안기사 올인원 실기 편제 기준
- 3회 실무 단답형 최신 기출 족보 (25문항)
- 4회 침해사고 분석 및 시큐어코딩 실무 서술형 (25문항)
총 50문항 추가 (누적 실기 100문항)
"""

def get_extra_practical_questions():
    q = []

    # ==========================================
    # [3회] 실기 단답형 최신 기출 족보 (25문항)
    # ==========================================
    q.append({
        "id": "IP3_Q1", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "Snort 룰 옵션 중 직전 매칭된 content 패턴의 끝 지점으로부터 다음 패턴을 탐색하기 시작할 상대적 시작 거리를 지정하는 옵션 키워드는 무엇인가?",
        "options": ["distance", "offset", "depth", "within", "nocase"],
        "answer": 1,
        "explanation": "[정답: distance]\ndistance는 이전 content 매칭의 끝 지점부터 몇 바이트 떨어진 곳부터 다음 content 탐색을 시작할지(상대적 오프셋)를 지정하는 옵션입니다. 반면 within은 distance 지점부터 최대 몇 바이트 범위 내에서 찾을지를 지정합니다."
    })
    q.append({
        "id": "IP3_Q2", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "리눅스 iptables에서 패킷을 차단할 때, 단순히 패킷을 버리고 송신자에게 아무런 응답을 주지 않는 DROP과 달리, 송신자에게 '연결 거부(ICMP Port Unreachable 또는 TCP RST)' 패킷을 회신하며 차단하는 타겟은 무엇인가?",
        "options": ["REJECT", "DENY", "DROP", "DISCARD", "LOG"],
        "answer": 1,
        "explanation": "[정답: REJECT]\nREJECT 타겟은 접속을 차단하면서 클라이언트에게 즉시 ICMP unreachable 또는 TCP RST 응답을 돌려주어 클라이언트가 타임아웃까지 대기하지 않게 합니다. 반면 DROP은 패킷을 조용히 폐기합니다."
    })
    q.append({
        "id": "IP3_Q3", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "리눅스 시스템에서 특정 파일이나 소켓, 네트워크 포트를 열고 있는 프로세스의 PID와 실행 계정 목록을 조회하는 침해사고 분석 명령어는 무엇인가?",
        "options": ["lsof (또는 fuser)", "netstat", "ps", "top", "strace"],
        "answer": 1,
        "explanation": "[정답: lsof (또는 fuser)]\nlsof(List Open Files)는 시스템에서 활성화된 모든 파일 디스크립터(일반 파일, 디렉토리, 네트워크 소켓 등)와 이를 점유하고 있는 프로세스(PID) 정보를 출력하는 핵심 점검 도구입니다."
    })
    q.append({
        "id": "IP3_Q4", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "리눅스 파일시스템에서 파일의 3대 타임스탬프(atime, mtime, ctime) 중 파일의 소유자, 권한(chmod), 속성 등 파일의 메타데이터(Inode 정보)가 변경된 시각을 나타내는 것은 무엇인가?",
        "options": ["ctime (Change Time)", "mtime (Modification Time)", "atime (Access Time)", "dtime (Deletion Time)", "btime (Birth Time)"],
        "answer": 1,
        "explanation": "[정답: ctime]\nmtime은 파일의 실제 내용(데이터)이 수정된 시각이고, atime은 파일이 읽히거나 실행된 시각이며, ctime은 메타데이터(소유자, 권한 등 inode 속성)가 변경된 시각입니다."
    })
    q.append({
        "id": "IP3_Q5", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "윈도우 Vista 이상 시스템의 보안 감사 이벤트 로그 중 관리자 권한을 가진 계정으로 특권(Privilege)이 할당되어 로그인했을 때 기록되는 이벤트 ID는 무엇인가?",
        "options": ["4672 (Special privileges assigned to new logon)", "4624", "4625", "4720", "1102"],
        "answer": 1,
        "explanation": "[정답: 4672]\n4672 이벤트는 관리자(Administrator) 그룹에 속한 특권 계정이 로그인하여 시스템 관리 권한(SeDebugPrivilege 등)을 부여받았을 때 4624(일반 성공)와 함께 발생하는 감사 이벤트입니다."
    })
    q.append({
        "id": "IP3_Q6", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "쿠키의 탈취 및 비인가 전송을 막기 위한 SameSite 속성값 중 타 사이트에서의 단순 링크 이동(GET 탐색) 시에는 쿠키를 전송하지만, 타 사이트의 POST 요청이나 이미지 임베딩 요청 등에서는 쿠키 전송을 차단하는 기본값은 무엇인가?",
        "options": ["Lax", "Strict", "None", "Secure", "HttpOnly"],
        "answer": 1,
        "explanation": "[정답: Lax]\nSameSite=Strict는 타 사이트에서의 모든 요청에서 쿠키를 일절 배제하며, SameSite=Lax는 최상위 탐색(안전한 GET 링크 이동)을 제외한 모든 교차 출처 요청(POST 등)에서 쿠키 전송을 차단하여 CSRF를 방어합니다."
    })
    q.append({
        "id": "IP3_Q7", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "시큐어코딩 가이드에서 SQL Injection 취약점을 제거하기 위해 MyBatis 등의 ORM 프레임워크 매퍼 XML 파일에서 동적 문자열 치환 기호인 ${param} 대신 반드시 사용해야 하는 파라미터 바인딩 표기는 무엇인가?",
        "options": ["#{param}", "${param}", "%{param}", ":param", "@{param}"],
        "answer": 1,
        "explanation": "[정답: #{param}]\nMyBatis에서 ${param}은 파라미터 값을 따옴표 없이 그대로 쿼리 문자열에 합치므로 SQL 인젝션에 취약합니다. #{param}을 사용해야 PreparedStatement의 '?' 파라미터로 안전하게 바인딩됩니다."
    })
    q.append({
        "id": "IP3_Q8", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "암호화 통신에서 송신자와 수신자의 장기 개인키가 사후에 유출되더라도 이전에 암호화되어 기록된 과거 세션 트래픽들이 복호화되지 않도록 보장하는 암호학적 특성은 무엇인가?",
        "options": ["완전 전방향 보안 (Forward Secrecy / PFS)", "상호 인증 (Mutual Authentication)", "부인 방지 (Non-Repudiation)", "충돌 저항성 (Collision Resistance)", "가용성 (Availability)"],
        "answer": 1,
        "explanation": "[정답: 완전 전방향 보안 (PFS: Perfect Forward Secrecy)]\nEphemeral Diffie-Hellman(DHE, ECDHE)과 같이 세션마다 일회성 임시 키를 생성하고 폐기함으로써 장기 비밀키가 노출되어도 과거 트래픽의 복호화를 방지합니다."
    })
    q.append({
        "id": "IP3_Q9", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "리눅스 bash 셸에서 이전 사용자가 입력했던 모든 명령어 히스토리가 기록되는 사용자 홈 디렉토리의 기본 파일명은 무엇인가?",
        "options": [".bash_history", ".bashrc", ".bash_profile", "/var/log/history", ".history"],
        "answer": 1,
        "explanation": "[정답: .bash_history]\n침해사고 분석 시 공격자가 터미널에서 수행한 행위를 확인하기 위해 사용자 홈 디렉토리 하위의 ~/.bash_history 파일을 우선 분석합니다."
    })
    q.append({
        "id": "IP3_Q10", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "공개키 기반 구조(PKI)에서 인증서 상태를 확인하기 위해 CA가 주기적으로 발행하는 인증서 폐기 목록의 영문 약어는 무엇인가?",
        "options": ["CRL (Certificate Revocation List)", "OCSP", "CSR", "CA", "SCEP"],
        "answer": 1,
        "explanation": "[정답: CRL (Certificate Revocation List)]\nCRL은 효력이 상실되거나 취소된 인증서들의 일련번호 목록을 CA가 전자서명하여 정기적으로 게시하는 공지 목록입니다."
    })
    q.append({
        "id": "IP3_Q11", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "리눅스에서 바이너리 실행 파일 내부에 포함되어 있는 출력 가능한 ASCII 문자열들을 추출하여 악성코드의 C2 IP 주소나 문자열을 분석할 때 사용하는 명령어는 무엇인가?",
        "options": ["strings", "objdump", "readelf", "nm", "file"],
        "answer": 1,
        "explanation": "[정답: strings]\nstrings 명령어는 실행 바이너리나 코어 덤프 파일에서 연속된 4글자 이상의 출력 가능한 텍스트 문자열을 추출하여 C2 도메인, IP, 오류 메시지 등을 신속히 파악할 수 있게 합니다."
    })
    q.append({
        "id": "IP3_Q12", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "iptables 명령어에서 외부 인터페이스(eth0)로 들어오는 패킷 중 목적지 포트가 22번(SSH)인 TCP 패킷을 허용하는 규칙을 INPUT 체인의 맨 첫 번째(1번) 줄에 삽입하기 위한 옵션은 무엇인가?",
        "options": ["-I INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT", "-A INPUT -i eth0 -p tcp --dport 22 -j ACCEPT", "-D INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT", "-R INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT", "-N INPUT 1 -i eth0 -p tcp --dport 22 -j ACCEPT"],
        "answer": 1,
        "explanation": "[정답: -I (Insert)]\n-A(Append)는 체인의 맨 끝에 규칙을 추가하지만, -I(Insert)는 특정 행 번호(-I INPUT 1)에 규칙을 우선순위 최상단으로 삽입할 때 사용합니다."
    })
    q.append({
        "id": "IP3_Q13", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "전자금융감독규정상 금융회사 및 전자금융업자가 정보보호 예산으로 편성해야 하는 최소 비율 기준(총 IT 예산 대비)으로 올바른 것은?",
        "options": ["총 IT 예산의 100분의 7 (7%) 이상", "총 IT 예산의 5% 이상", "총 IT 예산의 10% 이상", "총 IT 예산의 3% 이상", "총 예산의 1% 이상"],
        "answer": 1,
        "explanation": "[정답: 7% 이상]\n전자금융감독규정 제8조에 따라 금융회사는 총 IT 인력의 5% 이상을 정보보호 전담인력으로 확보하고, 총 IT 예산의 7% 이상을 정보보호 예산으로 편성하도록 권고 및 규정하고 있습니다."
    })
    q.append({
        "id": "IP3_Q14", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "개인정보 안전성 확보조치 기준에 따라 개인정보처리시스템에 관리자가 접속할 때 아이디와 비밀번호 외에 추가로 적용해야 하는 인증 방식은 무엇인가?",
        "options": ["안전한 다중인증 (2차 인증 / MFA: OTP, SMS, 보안토큰 등)", "IP 주소 화이트리스트 단독", "MAC 주소 필터링", "생체인증 단독", "인증서 비밀번호 단독"],
        "answer": 1,
        "explanation": "[정답: 다중인증 (2차 인증 / Multi-Factor Authentication)]\n안전성 확보조치 기준에 따라 관리자 페이지 및 개인정보처리시스템에 외부 또는 내부에서 접속 시 패스워드 외에 OTP, 보안토큰 등 다중인증을 의무 적용해야 합니다."
    })
    q.append({
        "id": "IP3_Q15", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "NIST SP 800-63B 디지털 신원 가이드라인에서 패스워드 정책에 대해 권고한 내용 중 기존 전통적 정책과 달라진 대표적인 변경점은 무엇인가?",
        "options": ["주기적인 강제 변경(90일 주기 등) 폐지 권고 및 유출된 패스워드 사전 대조 의무화", "패스워드 길이를 최소 6자리로 단축 권고", "특수문자 3종 이상 강제 조합 유지", "패스워드 힌트 필수 제공", "30일마다 패스워드 변경 의무화"],
        "answer": 1,
        "explanation": "[정답: 주기적 강제 변경 폐지 및 유출 패스워드 사전 대조]\nNIST 가이드라인은 사용자가 패스워드를 억지로 변경하면서 패턴을 단순화하는 부작용을 막기 위해 주기적 강제 변경을 폐지하고, 최소 8자 이상(권장 12자 이상) 및 기유출 데이터베이스 대조를 권고합니다."
    })
    q.append({
        "id": "IP3_Q16", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "사이버 킬체인(Cyber Kill Chain) 7단계 모델 중 공격자가 시스템 침투 후 내부 정찰 및 다른 시스템으로 권한을 확대해 나가는 횡적 이동(Lateral Movement)의 기반이 되는 단계는?",
        "options": ["Command & Control (명령제어) 및 Actions on Objectives", "Reconnaissance (정찰)", "Weaponization (무기화)", "Delivery (전달)", "Exploitation (취약점 공격)"],
        "answer": 1,
        "explanation": "[정답: Command & Control (C2)]\n악성코드가 설치(Installation)된 후 C2 채널을 확립하여 공격자의 원격 명령을 수신하고, 이를 통해 내부 침투 심화 및 목적 달성(Actions on Objectives) 단계로 진입합니다."
    })
    q.append({
        "id": "IP3_Q17", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "MITRE 사에서 실제 해커 조직의 사이버 공격 전술(Tactics)과 기술(Techniques), 그리고 공통 지식베이스를 체계화한 프레임워크의 명칭은 무엇인가?",
        "options": ["MITRE ATT&CK", "OWASP Top 10", "NIST CSF", "ISO 27001", "CIS Controls"],
        "answer": 1,
        "explanation": "[정답: MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge)]\n공격자의 생애주기 전반에 걸친 세부 공격 기술을 매트릭스 형태로 분류하여 침해 탐지 및 모의훈련에 널리 활용되는 글로벌 프레임워크입니다."
    })
    q.append({
        "id": "IP3_Q18", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "리눅스 시스템에서 관리자가 시스템의 감사 규칙(Audit Rules)을 설정하여 특정 시스템 콜이나 중요 파일(/etc/passwd 등)에 대한 접근 시도를 실시간 감사 로그에 기록하도록 통제하는 도구는?",
        "options": ["auditctl (또는 auditd)", "systemctl", "sysctl", "logrotate", "iptables"],
        "answer": 1,
        "explanation": "[정답: auditctl]\nauditctl 명령어를 사용하여 리눅스 커널 감사 시스템(auditd)에 감시 규칙(-w /etc/passwd -p wa -k passwd_change)을 등록함으로써 주요 파일 변경을 실시간 감적 추적합니다."
    })
    q.append({
        "id": "IP3_Q19", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "보안관제 센터(SOC)에서 이종 보안 솔루션의 경보를 자동 수집·분석하고, 플레이북(Playbook)에 따라 사전 정의된 대응 절차를 사람의 개입 없이 또는 최소한의 개입으로 자동 실행하는 기술은?",
        "options": ["SOAR (Security Orchestration, Automation and Response)", "SIEM", "EDR", "NDR", "XDR"],
        "answer": 1,
        "explanation": "[정답: SOAR]\nSIEM이 로그 수집 및 상관분석에 초점을 맞춘다면, SOAR은 워크플로우 오케스트레이션과 플레이북 기반 자동화 대응을 결합하여 침해사고 대응 속도를 획기적으로 단축합니다."
    })
    q.append({
        "id": "IP3_Q20", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "단말기(엔드포인트)에서 발생하는 프로세스 동작, 네트워크 연결, 파일 변경 등을 행위 기반으로 실시간 모니터링하고 악성 행위 탐지 시 즉시 프로세스를 격리하는 보안 기술은?",
        "options": ["EDR (Endpoint Detection and Response)", "기존 시그니처 백신(AV)", "EPP 단독", "방화벽", "DLP"],
        "answer": 1,
        "explanation": "[정답: EDR]\nEDR은 엔드포인트의 모든 활동을 상세히 추적 및 기록하여 파일리스(Fileless) 공격, 랜섬웨어 및 알려지지 않은 제로데이 공격을 탐지하고 분석 및 대응 기능을 제공합니다."
    })
    q.append({
        "id": "IP3_Q21", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "네트워크 장비의 포트 미러링(Port Mirroring) 기능 중 시스코(Cisco) 스위치에서 특정 포트나 VLAN의 송수신 패킷을 분석 장비가 연결된 다른 포트로 복제하여 전송하는 기능의 명칭은?",
        "options": ["SPAN (Switch Port Analyzer)", "RSPAN", "VTP", "CDP", "HSRP"],
        "answer": 1,
        "explanation": "[정답: SPAN (Switch Port Analyzer)]\nSPAN은 로컬 스위치의 포트나 VLAN 트래픽을 IDS, 패킷 분석기(Wireshark)가 물려 있는 모니터링 포트로 그대로 복사(Mirroring)해 주는 기술입니다."
    })
    q.append({
        "id": "IP3_Q22", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "윈도우 시스템에서 침해사고 조사 시 메모리 상주 프로세스나 드라이버 분석을 위해 커널 크래시 덤프나 라이브 RAM 메모리를 추출할 때 사용하는 대표적인 오픈소스 메모리 분석 프레임워크는?",
        "options": ["Volatility (볼라틸리티)", "Autopsy", "EnCase", "FTK Imager", "Wireshark"],
        "answer": 1,
        "explanation": "[정답: Volatility]\nVolatility는 리눅스, 윈도우, 맥의 물리 RAM 덤프 이미지를 파싱하여 실행 중이던 프로세스 트리(pslist), 활성 네트워크 연결(netscan), 인젝트된 셸코드(malfind) 등을 정밀 분석하는 대표적 도구입니다."
    })
    q.append({
        "id": "IP3_Q23", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "소프트웨어 공급망 공격(Supply Chain Attack)을 방어하기 위해 애플리케이션에 포함된 모든 오픈소스 라이브러리, 의존성, 버전 및 라이선스 목록을 기계 판독 가능한 표준 형식으로 기술한 명세서는?",
        "options": ["SBOM (Software Bill of Materials)", "CVE", "CWE", "CVSS", "SLA"],
        "answer": 1,
        "explanation": "[정답: SBOM (Software Bill of Materials)]\nSBOM은 소프트웨어의 부품 명세서로, Log4j 사태와 같은 오픈소스 취약점 발생 시 해당 라이브러리를 사용 중인 자산을 즉시 식별하여 조치할 수 있게 합니다."
    })
    q.append({
        "id": "IP3_Q24", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "개인정보 보호법상 개인정보취급자가 개인정보처리시스템에 접근한 접속기록에 반드시 포함되어야 하는 법정 필수 기록 항목 5가지에 해당하지 않는 것은?",
        "options": ["취급자의 신용등급", "계정(식별자)", "접속일시", "접속지 정보(IP 주소)", "수행한 업무(조회, 수정, 삭제 등) 및 정보주체 식별정보"],
        "answer": 1,
        "explanation": "[정답: 취급자의 신용등급]\n안전성 확보조치 기준에 따른 필수 항목은 1) 계정(식별자), 2) 접속일시, 3) 접속자 IP 주소, 4) 수행한 업무내역(열람, 수정, 삭제, 출력 등), 5) 처리한 정보주체 식별정보입니다."
    })
    q.append({
        "id": "IP3_Q25", "category": "infosec_practical", "exam": 3, "exam_name": "3회 실기 단답형 최신 기출 족보",
        "subject_id": 1, "subject_name": "실기 단답형",
        "question": "제로 트러스트(Zero Trust) 보안 아키텍처의 3대 핵심 기본 원칙 중 '내부 네트워크라 할지라도 결코 신뢰하지 않고 모든 접근을 엄격히 검증'하는 원칙을 나타내는 표어는?",
        "options": ["Never Trust, Always Verify (결코 신뢰하지 말고 항상 검증하라)", "Trust but Verify", "Security by Obscurity", "Fail-Safe", "Defense in Depth 단독"],
        "answer": 1,
        "explanation": "[정답: Never Trust, Always Verify]\n경계선 보안 모델을 탈피하여 모든 사용자, 기기, 세션을 잠재적 위협으로 간주하고 세분화된 인증·인가 및 지속적 모니터링을 수행하는 제로 트러스트의 대원칙입니다."
    })

    # ==========================================
    # [4회] 침해사고 분석 및 시큐어코딩 실무 서술형 (25문항)
    # ==========================================
    q.append({
        "id": "IP4_Q1", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[로그 분석] 다음 Apache 웹서버 access.log의 1개 라인을 보고 공격자가 시도한 웹 취약점 공격의 명칭과 공격 목적, 그리고 방어 대책을 기술하시오.\n\n로그: 192.168.10.55 - - [13/Nov/2026:14:22:01 +0900] \"GET /board/view.jsp?idx=10%20AND%20ASCII(SUBSTRING((SELECT%20user()%29,1,1)%29%3E100 HTTP/1.1\" 200 4520 \"-\" \"sqlmap/1.6#stable\"",
        "options": ["SQL Injection (Blind SQLi)", "XSS 공격", "CSRF 공격", "Path Traversal", "File Upload"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 공격 유형: Blind SQL Injection (참/거짓 조건 기반 불린 블라인드 인젝션)\n2. 공격 목적: SUBSTRING, ASCII 함수를 이용하여 DB 시스템의 현재 사용자명(user()) 1글자씩 바이트 단위로 참/거짓 응답을 대조해 데이터베이스 기밀 정보를 무차별 추출하려는 시도(User-Agent에 sqlmap 도구 흔적 존재).\n3. 방어 대책: SQL 쿼리 작성 시 파라미터가 쿼리 구조에 영향을 주지 않도록 PreparedStatement(파라미터화된 쿼리)를 필수로 적용하고, 정수형 파라미터(idx)는 Integer.parseInt() 등을 통해 숫자형 유효성 검증을 수행한다."
    })
    q.append({
        "id": "IP4_Q2", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[Snort 룰 작성] 사내 네트워크(192.168.1.0/24)의 임의 호스트에서 외부 인터넷으로 TCP 통신을 시도할 때, 패킷 페이로드 내에 'eval(base64_decode' 문자열이 대소문자 구분 없이 포함되어 있는 악성 WebShell 트래픽을 탐지하여 alert을 발생시키는 Snort 룰을 작성하시오. (단, sid는 2000001, rev는 1로 설정)",
        "options": ["alert tcp 192.168.1.0/24 any -> any any (msg:\"WebShell Traffic Detected\"; content:\"eval(base64_decode\"; nocase; sid:2000001; rev:1;)", "drop tcp any any -> any any (content:\"eval\"; sid:2000001;)", "pass tcp 192.168.1.0/24 any -> any any (sid:2000001;)", "log ip any any -> any any (content:\"base64\"; sid:2000001;)", "alert udp any any -> any any (content:\"WebShell\"; sid:2000001;)"],
        "answer": 1,
        "explanation": "[실무 모범답안]\nalert tcp 192.168.1.0/24 any -> any any (msg:\"WebShell Traffic Detected\"; content:\"eval(base64_decode\"; nocase; sid:2000001; rev:1;)\n- 출발지 IP 대역: 192.168.1.0/24 any\n- 목적지 IP 대역: any any\n- content: 문자열 매칭\n- nocase: 대소문자 무시"
    })
    q.append({
        "id": "IP4_Q3", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[방화벽 설정] 리눅스 iptables를 이용하여 사내 데이터베이스 서버(192.168.1.50)의 3306번(MySQL) 포트에 대해 오직 애플리케이션 웹서버(192.168.1.10)의 접속만 허용하고, 그 외의 모든 IP에서의 3306 포트 접속은 패킷을 조용히 버리도록(DROP) 정책을 구성하고자 한다. 올바른 2개의 iptables 명령어 조합은?",
        "options": ["1) iptables -A INPUT -p tcp -s 192.168.1.10 --dport 3306 -j ACCEPT\n2) iptables -A INPUT -p tcp --dport 3306 -j DROP", "1) iptables -A INPUT -p tcp --dport 3306 -j DROP\n2) iptables -A INPUT -p tcp -s 192.168.1.10 -j ACCEPT", "1) iptables -I INPUT -p tcp --dport 3306 -j REJECT", "1) iptables -F INPUT", "1) iptables -P INPUT ACCEPT"],
        "answer": 1,
        "explanation": "[실무 모범답안]\niptables는 순차적으로 룰을 평가하므로,\n1) iptables -A INPUT -p tcp -s 192.168.1.10 --dport 3306 -j ACCEPT (인가 웹서버 허용)\n2) iptables -A INPUT -p tcp --dport 3306 -j DROP (그 외 전면 차단)\n순서대로 등록해야 허용 룰이 먼저 적용된 후 차단 룰에 의해 나머지 접속이 방어됩니다."
    })
    q.append({
        "id": "IP4_Q4", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[시큐어코딩 분석] 다음 Java 코드의 보안 취약점 유형과 이를 해결하기 위한 안전한 개선 코드를 기술하시오.\n\n취약 코드:\nString query = \"SELECT * FROM members WHERE user_id = '\" + id + \"' AND user_pw = '\" + pw + \"'\";\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(query);",
        "options": ["취약점: SQL Injection / 개선: PreparedStatement와 파라미터 인덱스(?) 바인딩 사용", "취약점: XSS / 개선: HTML 엔티티 인코딩", "취약점: CSRF / 개선: CSRF 토큰 발급", "취약점: Buffer Overflow / 개선: 문자열 길이 제한", "취약점: 암호화 미적용 / 개선: AES 암호화"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 취약점: SQL Injection (사용자 입력값이 쿼리 문자열에 동적으로 연결되어 쿼리 구조 변조 가능)\n2. 개선 코드:\nString query = \"SELECT * FROM members WHERE user_id = ? AND user_pw = ?\";\nPreparedStatement pstmt = conn.prepareStatement(query);\npstmt.setString(1, id);\npstmt.setString(2, pw);\nResultSet rs = pstmt.executeQuery();"
    })
    q.append({
        "id": "IP4_Q5", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[시큐어코딩 분석] 다음 JSP 게시판 소스코드에서 발생하는 취약점과 안전한 방어 코드를 기술하시오.\n\n취약 코드:\n<% String content = request.getParameter(\"content\"); %>\n<div>내용: <%= content %></div>",
        "options": ["취약점: XSS (Cross-Site Scripting) / 개선: HTML 특수문자 치환 또는 JSTL <c:out escapeXml=\"true\"> 사용", "취약점: SQL Injection / 개선: PreparedStatement 사용", "취약점: 파일 다운로드 / 개선: getCanonicalPath 사용", "취약점: 세션 하이재킹 / 개선: SSL 적용", "취약점: 클릭재킹 / 개선: X-Frame-Options 설정"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 취약점: XSS (악의적인 자바스크립트 <script>alert(document.cookie)</script> 등이 브라우저에서 실행되어 세션 탈취 위험)\n2. 개선 코드: HTML 특수문자(&, <, >, \", ')를 HTML Entity(&amp;, &lt;, &gt;, &quot;, &#39;)로 변환하거나, JSTL 태그 라이브러리를 사용하여 <c:out value=\"${param.content}\" escapeXml=\"true\" />로 출력한다."
    })
    q.append({
        "id": "IP4_Q6", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[로그 분석] 다음 Nginx access.log를 보고 침해사고 유형과 공격자가 탈취하려 한 시스템 자원을 파악하시오.\n\n로그: 203.0.113.19 - - [13/Nov/2026:15:40:12 +0900] \"GET /download.jsp?file=..%2F..%2F..%2Fetc%2Fshadow HTTP/1.1\" 403 162 \"-\" \"curl/7.88.1\"",
        "options": ["Path Traversal (디렉토리 경로 조작) / /etc/shadow (리눅스 시스템 패스워드 해시 파일)", "SQL Injection / DB 사용자 테이블", "Command Injection / 리눅스 셸", "XSS 공격 / 관리자 쿠키", "WebShell 업로드 / 악성 JSP 파일"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 침해 유형: Path Traversal (디렉토리 탐색 / 경로 조작 공격)\n2. 대상 자원: URL 인코딩된 '..%2F' (상위 디렉토리 이동 ../) 기법을 활용하여 웹 루트를 벗어나 시스템 최고 기밀인 /etc/shadow (계정 패스워드 해시 파일) 탈취를 시도함 (403 Forbidden으로 차단됨)."
    })
    q.append({
        "id": "IP4_Q7", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[침해사고 대응] 리눅스 서버 침해 발생 시 포렌식 관점에서 휘발성 데이터를 수집하기 위해 반드시 지켜야 할 증거 수집 순서(Order of Volatility) 4단계를 기술하시오.",
        "options": ["1. 레지스터/캐시 -> 2. RAM 메모리 -> 3. 네트워크 활성 소켓 및 연결 상태 -> 4. 디스크 파일시스템 및 백업 미디어", "1. 하드디스크 백업 -> 2. RAM 메모리 -> 3. 시스템 재부팅 -> 4. 로그 분석", "1. 전원 차단 -> 2. 메모리 수집 -> 3. 네트워크 캡처 -> 4. 디스크 이미징", "1. 시스템 부팅 -> 2. 백신 검사 -> 3. 임시 파일 삭제 -> 4. 로그 백업", "1. 네트워크 케이블 분리 -> 2. 포맷 -> 3. 백업 복구 -> 4. 서비스 재개"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n증거의 휘발성이 높은 순서대로 수집해야 데이터 유실을 방지할 수 있습니다.\n1단계: CPU 레지스터 및 캐시 메모리\n2단계: 물리적 RAM 메모리 (메모리 덤프 확보)\n3단계: 네트워크 연결 상태(netstat, lsof) 및 실행 중인 프로세스(ps)\n4단계: 로컬 비휘발성 저장장치(디스크 이미지 원본 사본 및 타임라인 분석)"
    })
    q.append({
        "id": "IP4_Q8", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[시큐어코딩] C 언어에서 strcpy, strcat, sprintf 등 경계값(Bound) 검사를 수행하지 않는 안전하지 않은 함수를 대체하여 버퍼 오버플로우를 예방하는 안전한 표준 대체 함수들을 기술하시오.",
        "options": ["strncpy, strncat, snprintf (크기 지정 함수)", "strcpy_fast, strcat_safe", "memcpy 단독", "gets, scanf", "printf, puts"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n버퍼 크기를 넘어서는 데이터 복사로 인한 스택 오버플로우를 막기 위해 대상 버퍼의 최대 길이를 명시하는 strncpy, strncat, snprintf 또는 윈도우 환경의 보안 강화 함수(strcpy_s, strcat_s, sprintf_s)를 사용해야 합니다."
    })
    q.append({
        "id": "IP4_Q9", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[웹서버 보안 설정] Apache 웹서버(httpd.conf)에서 HTTP 요청 메서드 중 위험한 메서드(TRACE, DELETE, PUT 등)의 실행을 차단하고 오직 GET과 POST 메서드만 허용하기 위한 LimitExcept 설정 구문으로 올바른 것은?",
        "options": ["<Directory \"/var/www/html\">\n  <LimitExcept GET POST>\n    Require all denied\n  </LimitExcept>\n</Directory>", "<Limit GET POST> Allow from all </Limit>", "Options -Methods", "ServerSignature Off", "TraceEnable on"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n<LimitExcept GET POST>\n  Require all denied\n</LimitExcept>\nLimitExcept 지시자를 사용하여 GET과 POST를 제외한 모든 HTTP 메서드(TRACE: XST 공격 유발, PUT/DELETE: 임의 파일 조작)의 실행을 거부(denied) 처리합니다."
    })
    q.append({
        "id": "IP4_Q10", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[네트워크 침해 분석] 스위칭 환경에서 공격자가 지속적으로 피해자 PC와 기본 게이트웨이(라우터)에 위조된 ARP 응답(Reply) 패킷을 브로드캐스팅하여 자신의 MAC 주소를 게이트웨이 MAC으로 변조시키는 공격의 명칭과 이를 정적으로 방어하는 명령어를 기술하시오.",
        "options": ["공격: ARP Spoofing / 방어: arp -s [IP] [정상MAC주소] (정적 ARP 테이블 등록)", "공격: IP Spoofing / 방어: route add", "공격: DNS Spoofing / 방어: nslookup", "공격: ICMP Redirect / 방어: ping -t", "공격: MAC Flooding / 방어: ifconfig down"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 공격 명칭: ARP Spoofing (ARP 캐시 포이즈닝)\n2. 방어 대책: 클라이언트 및 게이트웨이에서 'arp -s [게이트웨이IP] [정상MAC]' 명령어를 수행하여 ARP 테이블 엔트리를 동적(Dynamic)에서 정적(Static)으로 고정시키거나, 스위치에서 Dynamic ARP Inspection(DAI) 보안 기능을 활성화한다."
    })
    q.append({
        "id": "IP4_Q11", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[로그 분석] 리눅스 /var/log/secure 로그에서 다음과 같은 로그가 수천 건 연속 발생했을 때의 공격 유형과 이를 자동으로 방어하기 위한 대표적인 오픈소스 도구는?\n\n로그: Failed password for invalid user admin from 198.51.100.22 port 48210 ssh2",
        "options": ["공격: SSH 무차별 대입 공격 (Brute Force / Dictionary Attack) / 방어 도구: fail2ban (또는 DenyHosts)", "공격: SYN Flooding / 방어: tcpdump", "공격: 버퍼 오버플로우 / 방어: gdb", "공격: SQL Injection / 방어: mod_security", "공격: 루트킷 침투 / 방어: tripwire"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 공격 유형: SSH 사전 무차별 대입 공격(Brute Force)\n2. 자동 방어 대책: fail2ban 도구를 설치하여 일정 시간 동안(예: 10분 내 5회 이상) 인증 실패 로그가 탐지되면 iptables 방화벽 규칙을 동적으로 생성하여 해당 공격자 IP를 일정 시간(1시간~영구) 자동 차단한다."
    })
    q.append({
        "id": "IP4_Q12", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[시큐어코딩] Java 웹 애플리케이션에서 안전하지 않은 암호학적 난수 생성기를 사용하여 세션 토큰이나 비밀번호 초기화 토큰이 예측되는 취약점을 해결하기 위해 교체해야 하는 안전한 난수 클래스는?",
        "options": ["java.security.SecureRandom", "java.util.Random", "Math.random()", "System.currentTimeMillis()", "UUID.randomUUID() 단독"],
        "answer": 1,
        "explanation": "[실무 모범답안]\njava.util.Random이나 Math.random()은 선형 합동 생성기(LCG) 기반의 의사 난수로서 시드 값이 추정되면 다음 난수가 쉽게 예측됩니다. 보안에 민감한 키/토큰 생성 시에는 OS의 엔트로피 풀을 사용하는 암호학적으로 안전한 java.security.SecureRandom 클래스를 사용해야 합니다."
    })
    q.append({
        "id": "IP4_Q13", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[포렌식 실무] 증거 수집 과정에서 디지털 증거의 획득, 이송, 보관, 분석, 법정 제출에 이르기까지 증거를 취급한 모든 담당자, 일시, 장소, 행위가 빈틈없이 문서화되어 증명되어야 한다는 법적 원칙은 무엇인가?",
        "options": ["연계보관성의 원칙 (Chain of Custody)", "무결성의 원칙", "재현성의 원칙", "정당성의 원칙", "신속성의 원칙"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n연계보관성의 원칙(Chain of Custody)은 디지털 증거가 최초 압수 시점부터 법정에 현출될 때까지 위조, 변조, 훼손되지 않았음을 입증하기 위해 증거 취급 이력을 연속적으로 기록하고 증명하는 절차적 원칙입니다."
    })
    q.append({
        "id": "IP4_Q14", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[취약점 진단] 오픈 리다이렉트(Open Redirect) 취약점이 발생하는 원인과 이를 악용한 피싱 공격을 예방하기 위한 개발 보안 조치 방안을 기술하시오.",
        "options": ["원인: 사용자 입력 URL을 검증 없이 HTTP 302 리다이렉트 대상으로 사용할 때 발생 / 대책: 허용된 내부 도메인만 허용하는 화이트리스트 검증 적용", "원인: SQL 쿼리 파라미터 결합 / 대책: PreparedStatement 사용", "원인: 쿠키 플래그 미설정 / 대책: HttpOnly 적용", "원인: 포트 개방 / 대책: 포트 차단", "원인: 패스워드 미암호화 / 대책: 해시 적용"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 발생 원인: response.sendRedirect(url)과 같이 외부 사용자가 전달한 임의의 URL 파라미터로 무조건 이동시킬 때 발생.\n2. 방어 대책: 이동 가능한 URL을 사전에 정의된 도메인(예: 사내 도메인만 허용)으로 한정하는 엄격한 화이트리스트 검증을 적용하거나, 상대 경로(/index.do)로의 이동만 허용한다."
    })
    q.append({
        "id": "IP4_Q15", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[시스템 무결성 점검] 리눅스 환경에서 주요 시스템 바이너리(ls, ps, netstat 등) 및 설정 파일의 해시값(SHA-256)을 사전에 DB로 구축해 두고, 주기적으로 파일 변경 여부를 감시하여 트로이목마 및 루트킷 변조를 탐지하는 호스트 무결성 점검 오픈소스 도구는?",
        "options": ["Tripwire (또는 AIDE)", "Wireshark", "Nmap", "John the Ripper", "Hydra"],
        "answer": 1,
        "explanation": "[실무 모범답안]\nTripwire(또는 AIDE)는 무결성 기준 데이터베이스(Baseline DB)를 생성한 후, 파일 크기, 해시값, 권한, 수정 시각 등을 정기적으로 비교하여 악성코드에 의한 파일 변조를 즉시 식별하는 HIDS 도구입니다."
    })
    q.append({
        "id": "IP4_Q16", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[웹 보안 설정] HTTP Strict Transport Security(HSTS) 헤더를 웹서버 응답에 적용할 때 브라우저가 최소 1년(31536000초) 동안 모든 하위 도메인을 포함하여 HTTPS 접속만을 강제하도록 설정하는 헤더 지시문 전체를 작성하시오.",
        "options": ["Strict-Transport-Security: max-age=31536000; includeSubDomains; preload", "X-Frame-Options: DENY", "Content-Security-Policy: default-src https:", "Cache-Control: no-store", "Access-Control-Allow-Origin: *"],
        "answer": 1,
        "explanation": "[실무 모범답안]\nStrict-Transport-Security: max-age=31536000; includeSubDomains; preload\n- max-age=31536000: 1년(초 단위)\n- includeSubDomains: 모든 서브도메인에도 동일 강제 적용\n- preload: 브라우저 내장 HSTS 프리로드 목록 등록 지원"
    })
    q.append({
        "id": "IP4_Q17", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[DDoS 방어] DNS 증폭 디도스(DNS Amplification DDoS) 공격을 무력화하기 위해 사내 공인 DNS 서버에서 외부 임의 사용자의 재귀 질의(Recursion)를 차단하는 BIND 설정 파일(named.conf)의 지시자는 무엇인가?",
        "options": ["recursion no; (또는 allow-recursion { none; };)", "listen-on port 53 { any; };", "zone \".\" IN { type hint; };", "directory \"/var/named\";", "dnssec-enable no;"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n사내 도메인의 권한(Authoritative) DNS 서버는 외부 인터넷 사용자에 대해 재귀적 질의를 수행할 필요가 없습니다. named.conf의 options 블록에 'recursion no;' 또는 'allow-recursion { trusted_network; };'를 설정하여 Open Resolver 악용을 차단합니다."
    })
    q.append({
        "id": "IP4_Q18", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[개인정보 기술적 보호조치] 고유식별정보(주민등록번호 등)를 저장할 때 암호화 적용 대상 저장소 3가지와 적용해야 하는 안전한 암호화 알고리즘 요건을 기술하시오.",
        "options": ["저장소: 데이터베이스, 로그/백업 파일, PC/단말기 파일 / 알고리즘: 안전한 대칭키 암호화(AES-256, ARIA-256 등)", "저장소: RAM 메모리만 대상 / 알고리즘: MD5", "저장소: 웹 브라우저 캐시 / 알고리즘: Base64", "저장소: DNS 레코드 / 알고리즘: DES", "저장소: 네트워크 스위치 / 알고리즘: RC4"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 암호화 대상 저장소: 데이터베이스(DB), 업무용 PC(하드디스크), 모바일 단말기, 보조저장매체(백업 테이프, USB), 로그 파일 등.\n2. 암호화 요건: 국가 표준 또는 국제적으로 공인된 안전한 양방향 대칭 암호화 알고리즘(AES, ARIA, SEED 등 128비트 이상, 권장 256비트)을 적용해야 한다."
    })
    q.append({
        "id": "IP4_Q19", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[네트워크 모니터링] tcpdump 도구를 사용하여 eth0 인터페이스에서 IP가 192.168.1.100이고 TCP 80번 포트로 오가는 패킷 중 SYN 플래그만 설정되어 있는 패킷을 캡처하기 위한 필터링 표현식은?",
        "options": ["tcpdump -i eth0 'host 192.168.1.100 and tcp port 80 and tcp[tcpflags] & tcp-syn != 0'", "tcpdump -i eth0 port 80", "tcpdump -w dump.pcap", "tcpdump -i eth0 ip", "tcpdump -X host 192.168.1.100"],
        "answer": 1,
        "explanation": "[실무 모범답안]\ntcpdump -i eth0 'host 192.168.1.100 and tcp port 80 and (tcp[tcpflags] & tcp-syn != 0)'\nTCP 헤더 13번째 바이트의 플래그 비트 중 SYN 비트를 비트마스킹(&)하여 SYN Flooding 패킷을 정밀하게 추출합니다."
    })
    q.append({
        "id": "IP4_Q20", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[SW 개발보안] 비밀번호를 단방향 해시 암호화할 때 레인보우 테이블 공격을 방어하기 위해 사용하는 솔트(Salt)의 올바른 생성 및 관리 방식으로 가장 적절한 것은?",
        "options": ["사용자마다 암호학적으로 안전한 난수 생성기로 최소 16바이트 이상의 고유한 솔트를 생성하여 해시값과 함께 DB에 저장한다.", "모든 사용자에 대해 사내 고정 문자열 1개를 솔트로 공통 적용한다.", "솔트 값을 암호화하여 별도 서버에 숨긴다.", "솔트로 사용자의 아이디를 그대로 사용한다.", "솔트 길이를 1바이트로 고정한다."],
        "answer": 1,
        "explanation": "[실무 모범답안]\n솔트는 사용자마다 고유하고 예측 불가능한 난수(SecureRandom, 최소 16바이트 이상)로 생성되어야 동일한 패스워드를 가진 사용자들의 해시값이 서로 달라지며, 레인보우 테이블 공격이 원천 무력화됩니다. 솔트는 공개되어도 안전하므로 해시값과 함께 평문으로 저장됩니다."
    })
    q.append({
        "id": "IP4_Q21", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[침해사고 분석] 리눅스 시스템에서 공격자가 /tmp 디렉토리에 백도어 셸 스크립트를 숨겨두고 삭제한 상태에서 여전히 프로세스가 백그라운드로 실행 중일 때, /proc 가상 파일시스템을 통해 삭제된 바이너리를 복구하는 명령어는?",
        "options": ["cp /proc/[PID]/exe /tmp/recovered_malware", "ls -l /proc", "cat /proc/cpuinfo", "rm -rf /proc/[PID]", "kill -9 [PID]"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n공격자가 파일시스템에서 원본 파일을 unlink(rm)하여 삭제했더라도 프로세스가 메모리에서 실행 중인 동안에는 /proc/[PID]/exe 심볼릭 링크가 해당 실행 파일의 메모리 이미지를 가리키므로, 이를 복사하여 악성코드 원본 바이너리를 완벽히 복구할 수 있습니다."
    })
    q.append({
        "id": "IP4_Q22", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[ISMS-P 결함판정] 심사원이 고객 상담 시스템을 점검하던 중, 상담원이 정보주체의 주민등록번호 전체(13자리)를 입력하여 조회한 화면에서 주민등록번호 전체가 마스킹 없이 그대로 표출되고 있는 사실을 확인하였다. ISMS-P 인증기준 중 위반된 기준과 올바른 개선 방안은?",
        "options": ["위반 기준: 2.7.2(암호화 적용) 또는 3.2.3(개인정보 표시제한) / 개선: 생년월일 또는 성별 뒤 6자리를 마스킹(***) 처리", "위반 기준: 1.1.1(경영진 참여)", "위반 기준: 2.4.1(출입통제)", "위반 기준: 3.4.1(개인정보 파기)", "결함 없음 (업무상 조회가 필요하므로 정당함)"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 위반 기준: 2.7.2(암호화 적용) 및 3.2.3(개인정보 표시제한/마스킹)\n2. 개선 대책: 개인정보 처리화면에서 주민등록번호, 계좌번호 등 고유식별정보를 표출할 때에는 업무상 필수적인 경우를 제외하고는 마스킹(생년월일 6자리 제외 뒷자리 *** 처리)하여 표출하고, 마스킹 해제 시에는 사유 입력 및 책임자 승인 이력을 기록해야 한다."
    })
    q.append({
        "id": "IP4_Q23", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[시스템 보안 점검] 리눅스 시스템에서 일반 계정(UID 1000 이상) 중 패스워드가 설정되어 있지 않아 패스워드 없이 로그인이 가능한 취약 계정을 /etc/shadow 파일에서 점검하는 명령어와 그 원리는?",
        "options": ["awk -F: '($2 == \"\" || $2 == \"!\") {print $1}' /etc/shadow", "cat /etc/passwd", "useradd -m test", "chmod 777 /etc/shadow", "ls -l /etc/shadow"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n/etc/shadow 파일의 두 번째 필드는 암호화된 비밀번호입니다. 이 필드가 비어 있거나(\"\") 널 값인 경우 비밀번호 입력 없이 로그인이 가능하므로, awk나 getent 명령어로 두 번째 필드가 빈 계정을 전수 식별하여 계정 잠금(passwd -l) 또는 비밀번호 설정을 강제해야 합니다."
    })
    q.append({
        "id": "IP4_Q24", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[취약점 분석] 웹 애플리케이션에서 파라미터로 명령어를 전달받아 실행하는 시스템 명령 실행(Command Injection) 취약점을 방지하기 위한 소프트웨어 개발 보안 방안 2가지를 기술하시오.",
        "options": ["1) Runtime.getRuntime().exec() 등의 외부 셸 직접 호출 지양 및 언어 내장 API 사용\n2) 불가피한 경우 화이트리스트 기반 특수문자(&, |, ;, `, $) 엄격 제거", "1) 쿼리 문자열 암호화\n2) SSL 적용", "1) 포트 변경\n2) 쿠키 세션 타임아웃 단축", "1) 패스워드 복잡도 강화\n2) OTP 적용", "1) 방화벽 룰 추가\n2) DNSSEC 적용"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 시스템 셸 명령어(exec, system)를 직접 호출하는 방식 대신 언어 자체에서 제공하는 안전한 라이브러리 API(예: 파일 복사는 FileCopy API)를 사용한다.\n2. 셸 호출이 불가피한 경우 세미콜론(;), 파이프(|), 백틱(`), 앰퍼샌드(&) 등 명령어 체이닝 문자를 철저히 필터링하고 화이트리스트 명령 인자만 허용한다."
    })
    q.append({
        "id": "IP4_Q25", "category": "infosec_practical", "exam": 4, "exam_name": "4회 실무 침해사고 분석 및 시큐어코딩",
        "subject_id": 2, "subject_name": "실기 서술·실무",
        "question": "[클라우드 보안] AWS, 애저 등 퍼블릭 클라우드 환경에서 IAM(Identity and Access Management) 사용 시 최소 권한의 원칙(Principle of Least Privilege)을 준수하기 위한 3대 핵심 보안 수칙을 기술하시오.",
        "options": ["1) 루트(Root) 계정의 일상적 사용 금지 및 MFA 필수 적용\n2) 개별 사용자별 IAM 계정 발급 및 역할(Role) 기반 임시 자격증명 활용\n3) 과도한 와일드카드(*) 권한 부여 금지 및 세분화된 최소 정책 적용", "1) 모든 권한을 AdministratorAccess로 통일\n2) 루트 계정 액세스 키를 깃허브에 공유\n3) MFA 해제", "1) 패스워드 없이 로그인 허용\n2) 모든 S3 버킷 Public 개방\n3) VPC 제거", "1) 로그 기능(CloudTrail) 비활성화로 성능 향상\n2) 보안그룹 0.0.0.0/0 허용", "1) 암호키 자동 로테이션 차단"],
        "answer": 1,
        "explanation": "[실무 모범답안]\n1. 최상위 루트 계정은 일상 업무에 사용하지 않고 잠금 및 강력한 하드웨어 MFA를 적용한다.\n2. 장기 액세스 키(Access Key) 대신 임시 자격증명을 제공하는 IAM Role(역할)을 사용한다.\n3. 와일드카드(Action: \"*\") 권한을 금지하고 실제 수행할 작업에만 국한된 최소 권한 정책(Least Privilege Policy)을 부여한다."
    })

    return q

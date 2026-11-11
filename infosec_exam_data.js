// infosec_exam_data.js: 정보보안기사 & ISMS-P 인증심사원 실전 기출/핵심 문제 및 요약 데이터셋

window.INFOSEC_ENGINEER_DATA = {
  name: "정보보안기사",
  badge: "국가기술자격",
  desc: "시스템·네트워크·애플리케이션 보안 및 법규 4대 과목 실전 핵심 퀴즈",
  subjects: [
    { id: 1, name: "1과목: 시스템 보안" },
    { id: 2, name: "2과목: 네트워크 보안" },
    { id: 3, name: "3과목: 애플리케이션 보안" },
    { id: 4, name: "4과목: 보안관리 및 법규" }
  ],
  questions: [
    {
      id: "IS_Q1",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 1,
      subject_name: "1과목: 시스템 보안",
      question: "리눅스 시스템에서 특정 파일에 SetUID 비트가 설정되어 있는지 점검하기 위한 find 명령어로 가장 올바른 것은?",
      options: [
        "find / -perm -4000 -type f",
        "find / -perm -2000 -type f",
        "find / -perm -1000 -type f",
        "find / -perm -7777 -type f",
        "find / -perm -0400 -type f"
      ],
      answer: 1,
      explanation: "SetUID 비트는 8진수 4000에 해당합니다. 따라서 'find / -perm -4000 -type f'를 사용하여 파일 소유자의 실행 권한으로 실행되는 파일들을 탐지합니다. (2000은 SetGID, 1000은 Sticky bit입니다.)"
    },
    {
      id: "IS_Q2",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 1,
      subject_name: "1과목: 시스템 보안",
      question: "버퍼 오버플로우 공격을 방어하기 위해 운영체제 수준에서 도입된 메모리 보호 기법 중, 스택과 힙 메모리 영역에서의 코드 실행을 금지하는 기술은?",
      options: [
        "ASLR (Address Space Layout Randomization)",
        "DEP / NX (Data Execution Prevention)",
        "Stack Canary (스택 카나리)",
        "Shadow Stack",
        "SafeSEH"
      ],
      answer: 2,
      explanation: "DEP(Data Execution Prevention) / NX(No-eXecute) 비트는 데이터 영역인 스택이나 힙 메모리에서 셸코드 등 프로그램 코드가 직접 실행되는 것을 하드웨어/OS 수준에서 원천 차단하는 방어 기법입니다."
    },
    {
      id: "IS_Q3",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 2,
      subject_name: "2과목: 네트워크 보안",
      question: "TCP 3-Way Handshake 취약점을 이용해 대량의 SYN 패킷을 전송하고 서버가 SYN/ACK 응답 후 대기하는 백로그 큐를 고갈시키는 서비스 거부(DoS) 공격은?",
      options: [
        "Smurf Attack",
        "TCP SYN Flooding",
        "Teardrop Attack",
        "Land Attack",
        "Ping of Death"
      ],
      answer: 2,
      explanation: "TCP SYN Flooding은 공격자가 위조된 IP로 수많은 SYN 패킷을 보내 서버가 Half-Open 상태로 백로그 큐를 유지하게 만들어 정상 사용자의 연결을 방해하는 DoS 공격입니다. 대응책으로 SYN Cookie가 사용됩니다."
    },
    {
      id: "IS_Q4",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 2,
      subject_name: "2과목: 네트워크 보안",
      question: "공격자가 동일한 로컬 네트워크(LAN) 상에서 게이트웨이나 타겟 시스템의 MAC 주소를 자신의 MAC 주소로 변조하여 통신 트래픽을 도청하는 스니핑 공격 기법은?",
      options: [
        "DNS Spoofing",
        "ARP Spoofing",
        "IP Spoofing",
        "DHCP Starvation",
        "BGP Hijacking"
      ],
      answer: 2,
      explanation: "ARP Spoofing은 ARP 프로토콜의 인증 취약점을 이용해 희생자의 ARP 캐시 테이블에 게이트웨이의 MAC 주소를 공격자의 MAC 주소로 속여 패킷을 가로채는 공격입니다. 정적 ARP 테이블(Static ARP) 설정으로 대응합니다."
    },
    {
      id: "IS_Q5",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 3,
      subject_name: "3과목: 애플리케이션 보안",
      question: "사용자 입력값이 데이터베이스 쿼리문으로 직접 조립되어 실행되는 취약점을 악용하는 SQL Injection을 원천 방어하기 위한 가장 확실한 시큐어 코딩 기법은?",
      options: [
        "입력값 길이 제한 및 정규표현식 검사",
        "PreparedStatement (매개변수화된 쿼리/바인딩 변수) 사용",
        "웹 방화벽(WAF) 단독 설치 및 시그니처 갱신",
        "데이터베이스 관리자(DBA) 권한으로 웹서버 실행",
        "에러 메시지를 클라이언트에 상세히 출력하지 않기"
      ],
      answer: 2,
      explanation: "SQL Injection의 가장 근본적인 방어책은 쿼리 구조와 입력 데이터가 엄격히 분리되는 PreparedStatement(Parameterized Query)를 사용하는 것입니다. 입력값이 쿼리의 문법으로 해석되지 않고 순수 데이터로만 처리됩니다."
    },
    {
      id: "IS_Q6",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 3,
      subject_name: "3과목: 애플리케이션 보안",
      question: "웹 브라우저의 쿠키 탈취를 방지하기 위해 JavaScript(document.cookie)를 통한 쿠키 접근을 차단하는 브라우저 보안 플래그는?",
      options: [
        "Secure",
        "HttpOnly",
        "SameSite=Strict",
        "Path=/",
        "X-Content-Type-Options"
      ],
      answer: 2,
      explanation: "HttpOnly 플래그는 클라이언트 스크립트(JavaScript)에서 해당 쿠키를 조회하거나 조작하지 못하도록 차단하여, XSS 공격으로 세션 쿠키가 탈취되는 피해를 방어합니다."
    },
    {
      id: "IS_Q7",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 4,
      subject_name: "4과목: 보안관리 및 법규",
      question: "정보보안의 3대 요소인 CIA(기밀성, 완전성, 가용성) 중 '인가되지 않은 사용자에 의해 정보가 변경되거나 파괴되지 않음을 보장하는 특성'은?",
      options: [
        "기밀성 (Confidentiality)",
        "무결성 (Integrity)",
        "가용성 (Availability)",
        "부인방지 (Non-repudiation)",
        "책임추적성 (Accountability)"
      ],
      answer: 2,
      explanation: "무결성(Integrity)은 정보가 오직 인가된 절차와 인가된 사용자에 의해서만 수정, 생성, 삭제될 수 있음을 보장하는 특성입니다. 해시 함수, 전자서명 등으로 무결성을 검증합니다."
    },
    {
      id: "IS_Q8",
      category: "infosec_engineer",
      exam: 1,
      exam_name: "기출 핵심 모의고사",
      subject_id: 4,
      subject_name: "4과목: 보안관리 및 법규",
      question: "재해나 재난 발생 시 핵심 비즈니스 기능을 일정 수준으로 복구하는 데 허용되는 최대 시간을 의미하는 용어는?",
      options: [
        "RPO (Recovery Point Objective)",
        "RTO (Recovery Time Objective)",
        "MTBF (Mean Time Between Failures)",
        "MTTR (Mean Time To Repair)",
        "BIA (Business Impact Analysis)"
      ],
      answer: 2,
      explanation: "RTO(목표 복구 시간)는 재해 발생 시점부터 시스템과 업무 기능이 복구되어 정상 가동되기까지 허용되는 최대 지연 시간입니다. (RPO는 허용 가능한 데이터 손실 시점/크기입니다.)"
    }
  ],
  summaries: [
    {
      title: "1과목. 시스템 보안 핵심 요약",
      topics: [
        {
          name: "계정 관리 및 인증 체계 (PAM, Shadow)",
          points: [
            "리눅스 패스워드는 /etc/shadow에 일방향 솔트 해시(SHA-512)로 보관 (접근권한 000 또는 400).",
            "PAM(Pluggable Authentication Modules)은 계정 인증, 계정 제어, 세션 관리, 패스워드 정책을 모듈화하여 관리.",
            "SetUID/SetGID 파일은 취약점 악용 시 root 권한 획득의 경로가 되므로 주기적으로 전수 감사 실시."
          ]
        },
        {
          name: "메모리 보호 메커니즘 (DEP, ASLR, Canary)",
          points: [
            "ASLR: 프로세스가 실행될 때마다 스택, 힙, 라이브러리 메모리 주소를 난수화하여 고정 주소 공격(ROP 등)을 방어.",
            "Stack Canary: 함수 복귀 주소(RET) 바로 앞에 무작위 값을 삽입하고 복귀 전 변조 여부를 점검.",
            "DEP/NX: 스택 및 힙 메모리 세그먼트에 실행 권한(Execute)을 박탈하여 셸코드 실행 차단."
          ]
        }
      ]
    },
    {
      title: "2과목. 네트워크 보안 핵심 요약",
      topics: [
        {
          name: "TCP/IP 4계층 프로토콜 및 주요 공격",
          points: [
            "네트워크 계층: IP Spoofing, ICMP Flooding(Smurf), Teardrop(IP 파편화 재조합 오류 악용).",
            "전송 계층: TCP SYN Flooding (Half-Open 연결 고갈), UDP/TCP 포트 스캔 (SYN Scan, FIN/Null/Xmas Stealth Scan).",
            "응용 계층: DNS 증폭 공격 (Any 질의 악용), HTTP Slowloris / Slow Read DoS."
          ]
        },
        {
          name: "보안 장비 기술 체계 (FW vs IPS vs WAF)",
          points: [
            "방화벽(Firewall): IP 및 포트 기반 L3/L4 접근제어 패킷 필터링 (상태 기반 검사 Stateful Inspection).",
            "침입방지시스템(IPS): 시그니처 및 이상 징후 기반으로 유해 트래픽을 인라인(In-line) 실시간 차단.",
            "웹 방화벽(WAF): HTTP/HTTPS L7 페이로드를 검사하여 SQLi, XSS, 웹셸 업로드 차단."
          ]
        }
      ]
    }
  ]
};

window.ISMSP_AUDITOR_DATA = {
  name: "ISMS-P 인증심사원",
  badge: "KISA 공인자격",
  desc: "관리체계 수립·보호대책 요구사항·개인정보 처리단계 3개 영역 실전 결함 판정 퀴즈",
  subjects: [
    { id: 1, name: "1영역: 관리체계 수립 및 운영" },
    { id: 2, name: "2영역: 보호대책 요구사항" },
    { id: 3, name: "3영역: 개인정보 처리단계별" }
  ],
  questions: [
    {
      id: "ISMSP_Q1",
      category: "ismsp_auditor",
      exam: 1,
      exam_name: "인증기준 실전 결함평가",
      subject_id: 1,
      subject_name: "1영역: 관리체계 수립 및 운영",
      question: "ISMS-P 1.1.2(최고책임자의 지정) 인증기준에 관한 설명으로 가장 올바르지 않은 것은?",
      options: [
        "정보보호 최고책임자(CISO)와 개인정보 보호책임자(CPO)를 임명하고 권한과 책임을 문서화해야 한다.",
        "전자금융거래법 대상 금융회사의 경우 총자산 10조원 이상이면 CISO의 타 업무 겸직이 엄격히 금지된다.",
        "CPO는 반드시 정보보안 부서장이 겸임해야 하며 일반 임원은 CPO로 임명될 수 없다.",
        "최고책임자는 매년 정보보호 및 개인정보보호 계획을 수립하고 최고경영자(CEO)의 승인을 받아야 한다.",
        "CISO와 CPO의 역할과 보고체계는 내부관리계획 및 관련 규정에 명시되어야 한다."
      ],
      answer: 3,
      explanation: "CPO(개인정보 보호책임자)는 사업주, 대표자, 또는 개인정보 처리에 관한 업무를 담당하는 부서의 장(임원 등) 중에서 지정할 수 있으며, 반드시 보안 부서장이 독점 겸임해야 하는 것은 아닙니다."
    },
    {
      id: "ISMSP_Q2",
      category: "ismsp_auditor",
      exam: 1,
      exam_name: "인증기준 실전 결함평가",
      subject_id: 2,
      subject_name: "2영역: 보호대책 요구사항",
      question: "ISMS-P 2.5.4(비밀번호 관리) 인증기준에 따라 다음 결함 사례 중 인증기준 위반에 해당하는 것은?",
      options: [
        "비밀번호 변경 시 직전 사용했던 비밀번호 3개에 대한 재사용을 방지하고 있다.",
        "비밀번호 입력 시 5회 연속 오류 발생 시 계정 접근을 차단하고 본인확인 절차를 거친다.",
        "운영자 공용계정(admin)에 대해 패스워드를 16자리 특수문자 조합으로 설정하였으나 퇴사자가 발생해도 패스워드를 변경하지 않았다.",
        "영문, 숫자, 특수문자를 조합하여 10자리 이상으로 설정하도록 시스템이 강제하고 있다.",
        "비밀번호는 일방향 암호화 알고리즘(SHA-256 이상)에 솔트(Salt)를 추가하여 저장하고 있다."
      ],
      answer: 3,
      explanation: "공용계정의 사용은 원칙적으로 제한되어야 하며, 부득이 사용 시 업무 담당자 퇴사, 부서 이동 등 인사이동이 발생했을 때 지체 없이 비밀번호를 변경해야 합니다. 변경하지 않은 것은 명백한 결함사항입니다."
    },
    {
      id: "ISMSP_Q3",
      category: "ismsp_auditor",
      exam: 1,
      exam_name: "인증기준 실전 결함평가",
      subject_id: 2,
      subject_name: "2영역: 보호대책 요구사항",
      question: "ISMS-P 2.6.7(접속기록 보관 및 점검) 기준에 따라 대규모 개인정보처리시스템(5만명 이상 민감/고유식별정보 처리)의 접속기록 최소 보관기간과 점검 주기는?",
      options: [
        "1년 이상 보관, 반기 1회 점검",
        "1년 이상 보관, 매월 1회 점검",
        "2년 이상 보관, 매월 1회 점검",
        "2년 이상 보관, 반기 1회 점검",
        "3년 이상 보관, 분기 1회 점검"
      ],
      answer: 3,
      explanation: "개인정보 보호법 및 안전성 확보조치 기준에 따라 5만명 이상의 정보주체에 관하여 민감정보 또는 고유식별정보를 처리하는 시스템은 접속기록을 2년 이상 보관하고, 월 1회 이상 이상유무를 점검해야 합니다."
    },
    {
      id: "ISMSP_Q4",
      category: "ismsp_auditor",
      exam: 1,
      exam_name: "인증기준 실전 결함평가",
      subject_id: 3,
      subject_name: "3영역: 개인정보 처리단계별",
      question: "ISMS-P 3.1.2(수집 제한 및 최소 수집) 기준에서 '필수정보와 선택정보의 구분'에 관한 결함 사례로 옳은 것은?",
      options: [
        "회원가입 시 배송에 필요한 주소와 연락처를 필수항목으로 수집하였다.",
        "이벤트 안내 및 마케팅 수신동의를 선택항목으로 두고 동의하지 않아도 기본 회원가입을 완료할 수 있도록 하였다.",
        "서비스 이용을 위한 회원가입 시 마케팅 활용 목적의 '생년월일'과 '관심사'를 필수항목으로 지정하여 미동의 시 가입을 거부하였다.",
        "필수동의 항목과 선택동의 항목을 명확히 구분하여 체크박스를 별도로 제공하였다.",
        "선택정보 미제공을 이유로 재화 또는 서비스의 제공을 거부하지 않았다."
      ],
      answer: 3,
      explanation: "개인정보 보호법 제16조 제3항 및 ISMS-P 3.1.2 기준에 따라 정보주체가 선택정보의 제공에 동의하지 않는다는 이유로 기본 서비스 제공을 거부해서는 안 됩니다. 이를 위반하여 가입을 거부한 것은 대표적 결함입니다."
    }
  ],
  summaries: [
    {
      title: "1영역. 관리체계 수립 및 운영 (16개 기준)",
      topics: [
        {
          name: "1.1 관리체계 기반 마련 (4개 기준)",
          points: [
            "1.1.1 경영진의 참여: 최고경영진의 의사결정 및 자원(예산, 인력) 할당, 보안위원회 운영.",
            "1.1.2 최고책임자의 지정: CISO/CPO의 독립적 임명과 자격요건 준수, 겸직 제한 규정 준수.",
            "1.1.3 조직 구성: 부서별 역할과 책임 정의, 전사 협의체 가동.",
            "1.1.4 범위 설정: 핵심 서비스 및 정보자산, 네트워크, 개인정보 처리 흐름도를 누락 없이 식별."
          ]
        },
        {
          name: "1.2 위험 관리 (2개 기준)",
          points: [
            "1.2.1 위험 식별 및 분석: 자산 중요도 산정, 위협/취약점 분석 및 위험도(Risk Level) 도출.",
            "1.2.2 위험 평가 및 정보보호 대책 수립: 수용 가능한 위험 수준(DOA) 설정 및 위험 처리 계획 이행."
          ]
        }
      ]
    },
    {
      title: "2영역 & 3영역 핵심 점검 포인트",
      topics: [
        {
          name: "2영역 보호대책 요구사항 (64개 기준)",
          points: [
            "접근통제: 직무별 최소 권한 원칙(Need-to-know), 미사용 계정 비활성화, 3단계 비밀번호 복잡도.",
            "암호화: 고유식별정보, 비밀번호, 바이오정보 등 필수 암호화 대상(저장 및 전송 구간) 전수 적용.",
            "물리보안: 전산실/통제구역 출입통제 및 출입기록 보관, 반입/반출 장비 통제."
          ]
        },
        {
          name: "3영역 개인정보 처리단계별 요구사항 (22개 기준)",
          points: [
            "수집/이용: 동의 4대 고지사항(목적, 항목, 보유기간, 거부권), 만 14세 미만 아동 법정대리인 동의.",
            "제공/위탁: 제3자 제공(정보주체 이익 위함, 별도 동의) vs 위탁(위탁자 이익 위함, 체결문서화).",
            "파기: 목적 달성 시 복구 불가능한 영구 삭제(소각, 디가우징, 덮어쓰기), 분리보관 시스템 구축."
          ]
        }
      ]
    }
  ]
};

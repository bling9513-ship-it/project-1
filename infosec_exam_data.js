// infosec_exam_data.js
// SQLite DB(archive.db)에서 자동 생성된 최신 데이터셋
// 필기 200문항 | 실기 100문항 | ISMS-P 30문항

window.INFOSEC_WRITTEN_DATA = {
  "title": "2026 이기적 정보보안기사 (필기) 200제 & 내용별 심층요약·용어사전 80선",
  "description": "2026 이기적 정보보안기사 필기+실기 올인원 편제 기준 1~4회 모의고사(각 50제) 총 200문항 및 내용별 심층 요약 35선 + 필수 핵심 용어사전 45선",
  "questions": [
    {
      "id": "written_q1",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SetUID 비트는 8진수 4000입니다. 'find / -perm -4000 -type f' 명령을 통해 소유자 권한으로 실행되는 파일을 전수 식별할 수 있습니다. (2000: SetGID, 1000: Sticky bit)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q1",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "ctime은 i-node 메타데이터의 변경 시점을 기록하며 시스템 커널에 의해서만 갱신되므로 일반 시스템 호출(utime 등)로 공격자가 과거 시간으로 속일 수 없습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q1",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "shadow 파일의 필드 순서는 [사용자명:암호화패스워드:최종변경일:최소사용일수:최대사용일수:경고일수:비활성화일수:계정만료일:예약필드]입니다. 세 번째 필드는 1970년 1월 1일(Epoch)을 기준으로 패스워드를 마지막으로 변경한 날짜의 일수입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q1",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SELinux는 미국 NSA가 개발한 리눅스 커널용 MAC(강제적 접근통제) 보안 서브시스템으로, 주체(프로세스)와 객체(파일, 소켓 등)에 Type Enforcement 라벨을 부여해 root 권한 탈취 시에도 피해를 격리합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q2",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "DEP/NX(Data Execution Prevention)는 데이터 영역(Stack/Heap)에 실행(Execute) 권한을 제거하여 셸코드 실행을 원천 차단합니다. ASLR은 메모리 주소를 난수화하는 기술입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q2",
      "prompt": "",
      "choices": [],
      "answer": 4,
      "explanation": "%n 지시자는 앞서 출력된 총 문자(바이트) 수를 지정된 포인터 변수 메모리에 직접 쓰는(Write) 기능을 수행하므로 임의 코드 실행이나 메모리 변조에 악용됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q2",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "required는 실패 시 즉시 중단하지 않고 스택 내의 다른 모듈을 끝까지 실행한 후 최종 실패를 반환합니다. 반면 requisite는 실패 시 즉시 나머지 모듈 실행을 중단하고 실패를 반환합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q2",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Sticky Bit(권한값 1000, 표기 t)는 /tmp 디렉토리처럼 누구나 쓰기 권한이 있는 공용 디렉토리에서 다른 사용자가 생성한 파일을 타인이 임의로 삭제하거나 이동하지 못하도록 보호합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q3",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "required 플래그는 실패하더라도 스택의 나머지 모듈을 계속 수행하지만 최종 결과는 실패로 반환합니다. requisite는 실패 즉시 중단하고 실패를 반환합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q3",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "NTFS의 ADS(대체 데이터 스트림)는 'filename.txt:hidden.exe' 형태로 메인 파일 뒤에 숨겨진 스트림을 생성할 수 있어 탐지를 우회하는 악성코드 은닉에 자주 쓰입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q3",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ASLR은 프로그램이 메모리에 적재될 때마다 스택, 힙, 라이브러리 주소를 난수화하여 공격자가 고정된 셸코드나 라이브러리 함수(RTL) 주소를 점프하지 못하도록 차단하는 기법입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q3",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "DEP/NX(No-Execute) 비트는 메모리 영역 중 코드 영역이 아닌 스택이나 힙에 주입된 악의적인 셸코드(Shellcode)가 CPU에 의해 실행되는 것을 하드웨어(CPU NX 비트) 수준에서 차단합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q4",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "/var/log/lastlog는 계정별 최근 접속 기록을 저장하며 lastlog 명령어로 조회합니다. wtmp는 전체 로그인/로그아웃 이력(last), utmp는 현재 접속자(who), btmp는 로그인 실패(lastb)입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q4",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ASLR(Address Space Layout Randomization)은 메모리 주소를 난수화하여 공격자가 고정된 셸코드나 리턴 주소를 하드코딩하지 못하도록 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q4",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "윈도우 Vista/2008 이상에서 로그온 성공 이벤트 ID는 4624, 로그온 실패(브루트포스 탐지 등) 이벤트 ID는 4625입니다. (4720: 계정 생성, 1102: 감사 로그 삭제)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q4",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "authpriv는 SSH, su, sudo 등 개인 인증 및 보안 인가와 관련된 시설(Facility)이며, .*는 디버그부터 이머전시까지 모든 심각도 레벨의 메시지를 지정된 파일(/var/log/secure)에 저장하라는 의미입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q5",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "SRM(보안 참조 모니터)은 커널 모드에서 실행되며 사용자 토큰과 대상 객체의 DACL/SACL을 비교하여 접근 승인 여부를 결정하고 보안 감사 로그를 남깁니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q5",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "GCC의 -fstack-protector 옵션은 스택 버퍼 오버플로우로 인해 리턴 주소가 덮어씌워지기 전에 카나리 값을 먼저 검사하여 조작 시 프로세스를 강제 종료합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q5",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "/var/run/utmp는 현재 시스템에 로그인되어 있는 사용자 정보를 저장하며, /var/log/wtmp는 과거 성공한 모든 로그인/로그아웃 및 재부팅 기록을 누적 저장합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q5",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "루트킷(Rootkit)은 관리자(root) 권한 획득 후 자신의 존재(프로세스, 파일, 포트, 로그)를 숨기고 지속적인 백도어 접근을 유지하기 위해 시스템 바이너리나 커널 시스템 콜 테이블을 조작하는 은닉형 악성 도구 모음입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q6",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Tripwire는 시스템 주요 파일들의 MD5/SHA 해시값을 사전에 DB로 생성해 두고, 변경 여부를 주기적으로 대조하여 변조를 탐지하는 무결성 검증 도구입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q6",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "inetd/xinetd는 수퍼 데몬으로서 서비스 요청이 올 때 자식 프로세스로 서비스를 구동하며 TCP Wrapper(/etc/hosts.allow/deny)와 연동되어 접근 제어를 수행합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q6",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "chattr +i(immutable) 명령을 설정하면 파일이 읽기 전용으로 잠기며, 슈퍼유저(root)라도 속성을 해제(-i)하기 전에는 파일 삭제, 이름 변경, 수정, 링크 생성이 불가능합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q6",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "윈도우에서 자동 실행되는 시작 프로그램 및 지속성(Persistence) 백도어는 주로 HKLM 및 HKCU의 Software\\Microsoft\\Windows\\CurrentVersion\\Run(또는 RunOnce) 키에 등록됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q7",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "디렉토리 기본 권한 777에서 027을 빼면 750, 파일 기본 권한 666에서 027을 빼면(실행권한 제외) 640이 됩니다. 따라서 권장 보안 umask는 027입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q7",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Pass-the-Hash 공격은 패스워드 평문을 몰라도 NTLM 해시값 자체를 인증 토큰으로 재사용하여 타 시스템에 권한을 획득하는 래터럴 무브먼트 기법입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q7",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "기본 파일 최대권한은 666, 디렉토리는 777입니다. umask 027을 적용하면 파일은 666 - 027 = 640(-rw-r-----), 디렉토리는 777 - 027 = 750(drwxr-x---)이 됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q7",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "crontab 필드 순서는 [분(0-59) 시(0-23) 일(1-31) 월(1-12) 요일(0-7, 1=월요일)]입니다. 따라서 30분, 3시, 매일, 매월, 월요일(1)인 '30 3 * * 1'이 올바릅니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q8",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "윈도우 부팅 시 자동 실행을 위해 HKLM 및 HKCU의 \\Software\\Microsoft\\Windows\\CurrentVersion\\Run 또는 RunOnce 키에 악성 실행 경로를 등록합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q8",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "chroot 환경에서 root 권한을 가진 프로세스는 chroot를 재호출하거나 열려 있는 파일 디스크립터(fchdir)를 통해 감옥(jail) 외부로 탈출할 수 있습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q8",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TOCTOU 취약점은 자원의 상태를 검사하는 시점과 이를 실제로 사용하는 시점 사이에 공격자가 심볼릭 링크 등을 조작하여 발생합니다. 원자적(Atomic) 파일 생성(O_CREAT|O_EXCL) 및 파일 디스크립터 기반 fstat 검증이 필수입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q8",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "포맷 스트링 취약점은 프로그래머가 서식 문자열(%s 등)을 명시하지 않고 사용자 입력을 직접 printf(input) 형태로 전달할 때 발생하며, 공격자는 %x로 메모리를 유출하거나 %n 지시자로 지정된 메모리 주소에 기록된 바이트 수를 덮어쓸 수 있습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q9",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "TOCTOU(Time of Check to Time of Use) 경쟁 조건(Race Condition) 취약점은 자원 접근 권한 확인과 실제 작업 수행 사이의 간극을 이용해 심볼릭 링크 등을 바꿔치기하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q9",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "부트킷(Bootkit)은 부트 섹터(MBR)를 감염시켜 윈도우 커널이 초기화되기 전에 로드되어 커널 무결성 검증을 우회하고 보안 솔루션을 무력화합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q9",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "nohup(no hang up)은 사용자가 로그아웃하거나 터미널 창을 닫아 발생하는 SIGHUP 시그널을 무시하도록 하여 백그라운드 프로세스가 중단 없이 지속되게 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q9",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "리눅스 부팅 과정에서 커널 초기화 완료 후 사용자 공간(User Space)에서 가장 먼저 구동되는 프로세스는 PID 1번인 init(전통적 SysV) 또는 systemd(현대적 리눅스)입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q10",
      "prompt": "",
      "choices": [],
      "answer": 4,
      "explanation": "shadow 파일의 알고리즘 식별자는 $1=MD5, $2a=Blowfish, $5=SHA-256, $6=SHA-512입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q10",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "authpriv 시설(Facility)의 모든 우선순위(*) 로그를 /var/log/secure 파일에 저장하도록 지정한 보안 인증 로그 설정입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q10",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "윈도우 2000 이후 Active Directory 환경의 기본 인증 프로토콜은 커버로스(Kerberos v5)입니다. KDC(AS, TGS)를 통해 TGT 및 서비스 티켓을 발급받아 상호 인증을 수행합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q10",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TPM(신뢰 플랫폼 모듈)은 메인보드에 탑재되어 암호키 생성, 저장, 측정(PCR), 하드웨어 기반 부팅 무결성 검증을 수행하는 국제 표준 보안 칩입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q11",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "TCP SYN Flooding은 공격자가 반가용(Half-Open) 상태를 유지시켜 서버의 백로그 큐를 채워 정상 접속을 불능으로 만드는 L4 DoS 공격입니다. SYN Cookie 기법 등으로 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q11",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Switch Jamming(스위치 재밍)은 CAM 테이블 버퍼를 고갈시켜 스위치가 Fail-Open 상태(Hub 모드)로 전환되게 만들어 트래픽을 가로채는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q11",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TTL(Time to Live)은 패킷의 생존 기간(홉 수)을 정의하는 8비트 필드로, 라우터를 통과할 때마다 1씩 차감되며 0이 되면 패킷이 폐기되고 송신지에 ICMP Time Exceeded(Type 11) 메시지가 회신됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q11",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SYN 쿠키는 서버의 SYN 수신 큐(SYN Backlog) 고갈을 방지하기 위해 클라이언트 IP, 포트, 타임스탬프, 서버 비밀키를 해시하여 SYN/ACK의 Sequence Number로 반환한 후, 최종 ACK가 올 때만 소켓을 생성하는 방어 기법입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q12",
      "prompt": "",
      "choices": [],
      "answer": 5,
      "explanation": "AH는 IP 헤더의 불변 필드까지 포함하여 ICV(무결성 체크값)를 계산하므로 IP 주소가 변경되는 NAT를 거치면 무결성 검증에 실패합니다. 따라서 NAT 환경에서는 ESP와 NAT-Traversal을 사용합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q12",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Smurf 공격은 ICMP Echo를 다이렉트 브로드캐스트로 보내 수많은 호스트가 일제히 희생자에게 Echo Reply를 전송하게 만드는 고전적 대역폭 고갈 공격입니다. (Fraggle은 UDP 사용)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q12",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Land 공격은 출발지 IP와 목적지 IP, 출발지 포트와 목적지 포트를 동일하게 조작하여 표적 호스트가 자기 자신에게 루프를 돌며 무한 응답하도록 만들어 과부하를 유발하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q12",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Smurf 공격은 출발지를 피해자 IP로 위조한 ICMP Echo Request를 브로드캐스트하여 대량의 ICMP Echo Reply를 유발하며, Fraggle 공격은 이를 UDP Echo(7번) 또는 Chargen(19번) 포트로 수행하는 증폭 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q13",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Snort 룰은 헤더(액션, 프로토콜, IP/포트)와 바디의 msg, content, nocase(대소문자 무시), sid(고유식별자) 등으로 구성됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q13",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "스크린드 서브넷 게이트웨이는 외부 라우터와 내부 라우터 사이에 DMZ 망을 두어 배스천 호스트가 침해되더라도 내부망이 즉시 노출되지 않는 가장 견고한 구조입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q13",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TCP Connect(Open) 스캔은 완전한 3-Way Handshake를 수립하므로 시스템 로그에 접속 기록이 명확히 남아 스텔스 스캔이 아닙니다. FIN, Null, Xmas 스캔은 RFC 793 규약의 비정상 플래그 응답(Closed일 때만 RST 회신)을 이용합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q13",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TearDrop 공격은 IP 헤더의 Fragment Offset과 Data Length 값을 의도적으로 중첩되게 조작하여 수신측 OS가 재조합 시 메모리 참조 오류로 크래시를 일으키게 하는 취약점 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q14",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "Land Attack은 송신자 IP와 수신자 IP를 동일한 희생자 IP로 위조하여 패킷을 보냄으로써 시스템 리소스를 고갈시키는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q14",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "소스 포트 무작위화(Kaminsky 공격 방어책)는 TXID 16비트 외에 포트 16비트를 무작위화하여 공격자의 위조 응답 적중 확률을 극도로 낮춥니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q14",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "AH는 IP 프로토콜 번호 51번으로 데이터 기밀성(암호화)을 제공하지 않고 인증/무결성만 제공합니다. ESP는 IP 프로토콜 번호 50번으로 대칭키 암호화를 통한 기밀성 및 선택적 인증/무결성을 제공합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q14",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Slowloris는 헤더의 마지막 개행(\\r\\n\\r\\n)을 보내지 않고 수십 초 간격으로 더미 헤더(X-a: b\\r\\n)를 찔끔찔끔 보내어 웹서버의 연결 타임아웃을 연장시키며 가용 스레드/프로세스를 모두 잠식하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q15",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "FIN, Null, Xmas 스캔은 RFC 793 규약에 따라 열린 포트는 비정상 패킷을 무시(Drop)하여 무응답이고, 닫힌 포트는 RST/ACK를 응답하는 특성을 이용합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q15",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TCP 세션 하이재킹은 3-Way Handshake 이후 established 상태의 연결에서 서버와 클라이언트 간 시퀀스 번호를 가로채 세션 통제권을 획득하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q15",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "DNSSEC는 공개키 암호화 방식을 활용해 DNS 응답 데이터(RRset)에 디지털 서명(RRSIG, DNSKEY, DS 레코드)을 첨부하여 위·변조 및 위조된 캐시 주입을 방어하는 확장 표준입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q15",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "IKE(UDP 500번/4500번)는 ISAKMP 프레임워크와 Oakley 및 SKEME 키 교환 프로토콜을 결합하여 양 종단 간 암호화 알고리즘, 해시 방식, 키 수명 등을 협상하고 SA를 자동 생성하는 표준 프로토콜입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q16",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "ARP는 무인증 프로토콜이므로 공격자의 위조 ARP Reply를 막기 위해서는 게이트웨이 및 주요 서버의 MAC 주소를 정적(Static, arp -s)으로 고정하는 것이 근본적인 대응책입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q16",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ROA는 특정 AS(자율시스템) 번호가 해당 IP 프리픽스를 광고할 정당한 권한이 있음을 암호학적으로 서명 증명하는 RPKI 핵심 객체입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q16",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "스위치 재밍(Switch Jamming 또는 MAC Flooding)은 스위치의 MAC 주소 테이블 용량을 초과시켜 Fail-Open 모드로 전환되게 함으로써 모든 포트로 패킷을 브로드캐스팅(Fail-Safe 미흡)하게 유도하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q16",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "DRDoS(분산 반사 서비스 거부)는 출발지 IP를 피해자 IP로 변조한 후 증폭율이 높은 공개 UDP 서버(반사체)들에 질의를 전송하여 피해자에게 막대한 반사 트래픽이 쏟아지게 만드는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q17",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TearDrop 공격은 IP 헤더의 오프셋(Offset) 값을 중첩되도록 조작하여 수신 시스템이 패킷 재조합 시 메모리 참조 오류로 다운되게 만듭니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q17",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "애플리케이션 게이트웨이 방식은 각 서비스별 전용 프록시 데몬을 통해 애플리케이션 페이로드까지 완벽히 검사하지만 속도가 느립니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q17",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "WPA3 개인용(Personal) 표준은 Dragonfly 핸드셰이크 기반의 SAE(동시 동등 인증) 프로토콜을 사용하여 오프라인 딕셔너리 공격을 방어하고 전방향 보안(Forward Secrecy)을 제공합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q17",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SNI는 클라이언트가 TLS 핸드셰이크의 ClientHello 메시지에 접속하려는 도메인 이름을 포함하여 전송함으로써, 서버가 암호화 핸드셰이크 이전에 적절한 도메인의 SSL 인증서를 제시할 수 있게 하는 확장 규격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q18",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Slowloris(Slow HTTP Header DoS)는 HTTP 요청 헤더의 끝을 닫지 않고 일정 시간마다 불필요한 헤더 라인을 추가 전송하여 연결을 독점하는 L7 저대역폭 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q18",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "DRDoS(분산 반사 서비스 거부) 공격은 출발지 IP를 희생자로 위조하여 전 세계 개방형 반사 서버(DNS, NTP, SNMP, Memcached 등)로 질의하여 증폭 트래픽을 집중시킵니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q18",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "False Positive(오탐)은 비공격/정상 행위를 공격으로 잘못 판단한 오류이고, False Negative(미탐)은 실제 공격을 탐지하지 못하고 정상으로 통과시킨 오류입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q18",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "IDS는 스위치 미러(SPAN) 포트를 통해 패킷 사본을 분석하므로 실시간 차단 능력이 제한적인 반면, IPS는 네트워크 인라인(In-Line) 상에 물리적으로 직렬 연결되어 악성 패킷을 즉각 폐기(Drop)할 수 있습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q19",
      "prompt": "",
      "choices": [],
      "answer": 4,
      "explanation": "WPA3는 기존 WPA2의 4-Way 핸드셰이크 취약점(KRACK 등)을 개선하여 Dragonfly 키 교환 기반의 동등 동시 인증(SAE) 핸드셰이크를 채택해 오프라인 사전 공격을 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q19",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "IKE는 ISAKMP 프레임워크와 Oakley/SKEME 키 교환 프로토콜을 결합하여 SA(Security Association)와 키를 자동 협상하는 프로토콜입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q19",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Snort 룰 헤더의 기본 형식은 [Action] [Protocol] [SrcIP] [SrcPort] [Direction] [DstIP] [DstPort]입니다. 따라서 'alert tcp any any -> 192.168.1.100 80'이 정확합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q19",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "L2TP(RFC 2661)는 2계층 터널링 프로토콜로 시스코의 L2F와 MS의 PPTP를 결합한 규격입니다. 자체 암호화 기능이 없으므로 통상 IPSec(L2TP/IPSec)과 결합하여 기밀성을 보장합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q20",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "DNSSEC(DNS Security Extensions)은 공개키 암호화 전자서명을 DNS 레코드(RRSIG, DNSKEY 등)에 부여하여 캐시 포이즈닝 및 DNS 스푸핑을 방지합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q20",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "Out-of-Path(수동형/미러링) 구축은 네트워크 트래픽 흐름에 지장을 주지 않고 복사본을 전달받아 탐지하므로 패킷 전송 지연이 없습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q20",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "페이로드를 분석하여 SQL 인젝션 등 웹 공격을 차단하는 것은 웹방화벽(WAF)의 기능입니다. NAC는 단말의 보안 상태 점검, 사용자 인증, 네트워크 접속 통제 및 격리를 담당합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q20",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "스크린드 서브넷 게이트웨이는 외부 방화벽과 내부 방화벽 사이에 DMZ(완충 지대) 서브넷을 구축하여 공개 서버 침해 시에도 내부 사설망으로의 직접 침투를 차단하는 가장 안전하고 표준적인 방화벽 구성입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q21",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "SQL 인젝션 방어의 최우선 안전수칙은 정적 컴파일된 PreparedStatement를 사용하여 사용자 입력을 단순 데이터 리터럴(Parameter)로만 처리하는 것입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q21",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Time-Based Blind SQL 인젝션은 응답 시간 지연 함수(SLEEP(5) 등)의 실행 여부를 측정하여 데이터베이스 정보를 추출하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q21",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "PreparedStatement를 사용하면 쿼리의 문법적 구조가 먼저 컴파일된 후 입력값이 단순한 데이터(리터럴)로 바인딩되므로, 악의적인 SQL 구문이 쿼리 구조를 변조하지 못합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q21",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "HSTS(Strict-Transport-Security) 헤더는 브라우저에게 일정 기간 동안(max-age) 해당 도메인에 접근할 때 평문 HTTP 연결을 일절 시도하지 말고 무조건 HTTPS로만 통신하도록 강제하여 SSL Stripping 공격을 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q22",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "Stored XSS는 악성 스크립트가 데이터베이스에 저장되어 게시물을 조회하는 모든 사용자의 브라우저에서 세션 쿠키 탈취 등을 수행하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q22",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "경로 조작(Path Traversal) 취약점은 상위 디렉토리 이동 문자열을 검증하지 않아 시스템 중요 파일(/etc/passwd, win.ini 등)에 접근하는 취약점입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q22",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Blind SQL Injection은 SQL 인젝션 공격 유형입니다. XSS 공격은 저장형(Stored), 반사형(Reflected), DOM 기반(DOM-based)으로 분류됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q22",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "CSP(Content Security Policy)는 웹 페이지에서 로드할 수 있는 스크립트 출처(script-src), 스타일(style-src) 등을 화이트리스트로 제한하고 인라인 스크립트 실행을 금지하여 XSS를 강력하게 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q23",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "HttpOnly 플래그가 설정된 쿠키는 브라우저 스크립트(document.cookie)를 통한 접근이 차단되어 XSS 공격 시 세션 탈취를 효과적으로 예방합니다. (Secure는 HTTPS 통신만 허용)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q23",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "모든 오리진(*)을 허용하면서 인증 쿠키 전송(Allow-Credentials: true)을 허용하는 설정은 표준 브라우저에서 차단되거나 심각한 정보 유출 통로가 됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q23",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "HttpOnly 플래그가 설정된 쿠키는 브라우저의 클라이언트 스크립트(JavaScript)에서 접근할 수 없게 차단되어, XSS 취약점이 발생하더라도 쿠키 탈취를 방지합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q23",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "X-Frame-Options 헤더를 DENY(어디서도 프레임 삽입 불가) 또는 SAMEORIGIN(동일 출처에서만 허용)으로 지정하면 투명한 iframe을 이용한 클릭재킹을 방어할 수 있습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q24",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "CSRF는 인증된 사용자의 권한을 도용하여 악의적인 요청을 수행하게 하는 공격으로, CSRF 토큰 검증이나 SameSite 쿠키 속성으로 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q24",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Clickjacking(클릭재킹)은 투명 프레임을 이용해 사용자의 클릭을 가로채는 공격으로, 'X-Frame-Options: DENY' 헤더나 CSP frame-ancestors로 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q24",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "CSRF는 인증된 피해자의 브라우저 권한을 이용해 비인가 요청을 발생시키는 공격이므로, 예측 불가능한 동적 CSRF 토큰 검증, 재인증 요구, SameSite=Strict/Lax 쿠키 적용이 핵심 대책입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q24",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SSTI(서버 사이드 템플릿 인젝션)는 {{7*7}}과 같은 템플릿 표현식이 서버 측에서 평가되어 최종적으로 원격 코드 실행(RCE)으로 이어지는 고위험 취약점입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q25",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "SSRF는 서버가 외부 자원을 fetch하는 기능에서 내부 비인가 IP(127.0.0.1, 169.254.169.254 등)로의 접근을 허용할 때 발생합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q25",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SET의 이중 서명(Dual Signature)은 주문 정보 해시와 결제 정보 해시를 합쳐서 서명함으로써 상점은 결제정보를 못 보고 카드사는 주문 세부정보를 못 보게 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q25",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "파일 업로드 보안은 1) 허용된 확장자만 명시하는 화이트리스트 검증, 2) 파일명 난수화(UUID) 및 웹 루트 외부 저장, 3) 웹서버 설정에서 해당 디렉토리의 스크립트 실행 권한 제거가 3대 원칙입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q25",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "단순 문자열 치환(..././)은 우회될 수 있으므로, getCanonicalPath()를 사용하여 파일 시스템의 절대 정규 경로를 구한 후, 허용된 루트 디렉토리 경로로 시작하는지(startsWith) 엄격히 검증해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q26",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "업로드된 파일은 웹셸 실행 및 경로 조작을 막기 위해 파일명을 난수(UUID 등)로 변경하고 확장자를 강제 분리해야 합니다. 원본 파일명을 그대로 사용하는 것은 취약합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q26",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "서블릿이나 스프링 빈처럼 멀티스레드 환경에서 동작하는 싱글톤 객체에 상태를 갖는 인스턴스 멤버 변수를 두면 스레드 간 데이터 오염 및 세션 혼선이 발생합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q26",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "httpd.conf의 Directory 블록에서 'Options -Indexes'를 지정하면 디렉토리 리스팅(Directory Indexing)이 비활성화되어 파일 목록 노출 취약점이 제거됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q26",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "JWT는 마침표(.)로 구분되는 Header(알고리즘 및 토큰 타입), Payload(클레임/사용자 데이터), Signature(비밀키로 서명된 무결성 검증값) 3단계 구조로 구성됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q27",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "DKIM은 송신 메일 헤더에 디지털 서명을 첨부하고, 수신자는 송신자 도메인의 DNS에 공개된 TXT 레코드 공개키로 이를 검증하여 메일 위조를 탐지합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q27",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "데이터베이스 트리거(Trigger)는 DML(INSERT/UPDATE/DELETE)이나 DDL 이벤트 발생 시 자동으로 호출되어 무결성 검증과 실시간 감사 로그를 저장하는 데 쓰입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q27",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SPF는 DNS의 TXT 레코드에 해당 도메인을 대신해 메일을 발송할 수 있는 공인 IP 주소를 등록하여 메일 발송 서버의 진위 여부를 판별하는 기술입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q27",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "세션 고정(Session Fixation) 공격은 로그인 전 발급된 세션 ID를 로그인 성공 후에도 재사용할 때 발생하므로, 로그인 성공 시 반드시 기존 세션을 파기하고 새로운 세션 ID를 재생성(session.invalidate)해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q28",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "HSTS 헤더는 브라우저가 첫 연결 이후 무조건 암호화된 HTTPS 연결만을 시도하도록 강제하여 평문 다운그레이드 공격을 차단합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q28",
      "prompt": "",
      "choices": [],
      "answer": 4,
      "explanation": "SOP에서 출처는 'Protocol + Host + Port'의 3가지가 일치해야 동일 출처로 판단합니다. URI 경로는 출처 판별에 영향을 주지 않습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q28",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "TDE(투명한 데이터 암호화)는 DBMS 커널 수준에서 저장소(Datafile, Tablespace)를 암호화하므로 기존 응용프로그램의 소스코드나 SQL 쿼리를 수정할 필요가 없습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q28",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "추론 공격은 비인가자가 여러 합법적 통계 질의를 조합하여 민감한 개인 정보를 유추하는 것이므로, 소규모 집합 결과 은닉, 노이즈 추가, 감사 추적이 필요합니다. 무제한 질의 허용은 추론 공격을 용이하게 만듭니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q29",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "XXE 공격은 XML 문서 내 외부 DTD 엔티티 선언을 악용하여 시스템 내부 파일(/etc/passwd 등)을 탈취하거나 내부 포트 스캔을 수행하는 공격입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q29",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "CSP(Content Security Policy) 헤더는 브라우저가 다운로드하고 실행할 수 있는 유효한 도메인 화이트리스트를 지정하여 인라인 악성 스크립트 실행을 방지합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q29",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SSRF는 서버 측에서 외부 자원을 페치(fetch)하는 로직을 악용하여, 방화벽 뒤에 숨겨진 내부 인프라(127.0.0.1, 169.254.169.254 메타데이터 서버 등)에 비인가 요청을 발생시키는 취약점입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q29",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "S/MIME은 X.509 공개키 인증서를 기반으로 MIME 데이터에 암호화 및 디지털 서명을 적용하여 이메일의 4대 보안 목표(기밀성, 무결성, 인증, 부인방지)를 모두 제공하는 IETF 표준입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q30",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "Plug-In 방식은 DB 엔진 내부 모듈로 연동되어 애플리케이션 코드 수정이 거의 없으며 DBMS 엔진 성능을 활용합니다. TDE는 테이블스페이스 전체를 투명하게 파일 레벨에서 암호화합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q30",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "A01:2021 Broken Access Control은 수평적/수직적 권한 우회, 직접 객체 참조(IDOR) 등 사용자의 권한 검증 미흡으로 발생하는 접근제어 결함입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q30",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SET의 이중 서명(Dual Signature)은 주문 정보의 해시값과 결제 정보의 해시값을 결합하여 고객의 개인키로 서명함으로써, 상점에는 결제 정보를 숨기고 금융기관에는 주문 세부 내역을 숨기는 기술입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q30",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Nginx에서는 nginx.conf의 http 블록에 'server_tokens off;'를 설정하면 Server 응답 헤더에서 세부 버전 번호가 제거되고 'Server: nginx'만 노출됩니다. (ServerTokens Prod는 Apache 지시자)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q31",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ECB 모드는 초기화 벡터(IV) 없이 각 블록을 독립적으로 암호화하므로 패턴이 그대로 노출되어 현대 암호에서 사용을 금지합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q31",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "CTR 모드는 논스(Nonce)와 카운터를 결합하여 키스트림을 생성하므로 이전 블록에 종속되지 않고 완벽한 병렬 암·복호화 처리가 가능합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q31",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Feistel 구조는 데이터를 좌우 블록(L, R)으로 양분하여 라운드를 수행하며, 역원이 존재하지 않아도 복호화가 가능합니다(DES, SEED 등). 반면 SPN은 Substitution-Permutation Network 구조로 전체 블록을 병렬 처리합니다(AES, ARIA).",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q31",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "RSA는 두 개의 매우 큰 소수의 곱을 소인수분해하는 수학적 어려움에 기반하고, ECC는 타원곡선 군 위에서의 이산대수 문제(ECDLP)의 난해성에 기반하여 256비트 키로도 RSA 3072비트 급의 보안성을 제공합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q32",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "BLP 모델은 기밀성을 최우선으로 하여 상위 보안 레벨의 문서를 읽을 수 없고(No Read Up), 하위 보안 레벨로 기밀을 기록할 수 없습니다(No Write Down).",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q32",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "RSA는 두 개의 매우 큰 소수 p와 q의 곱 n = p*q를 구하는 것은 쉽지만, n으로부터 p와 q를 찾아내는 소인수분해의 난해성에 안전성을 둡니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q32",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "AES(Rijndael)는 블록 크기가 128비트로 고정되어 있으며, 키 길이에 따라 128비트(10라운드), 192비트(12라운드), 256비트(14라운드)를 지원합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q32",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "SEED는 1999년 한국인터넷진흥원(KISA)과 전자통신연구원(ETRI)이 개발한 128비트 블록, 128비트 키 크기의 Feistel 구조 국가 표준 암호 알고리즘입니다. (ARIA는 2004년 개발된 SPN 구조)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q33",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "OCSP는 클라이언트가 인증서 시리얼 넘버를 질의하면 실시간으로 해당 인증서의 유효/폐지 여부를 응답하는 경량 프로토콜입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q33",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "충돌 저항성(Collision Resistance)은 H(x) = H(y)를 만족하는 서로 다른 임의의 두 쌍 (x, y)를 찾는 것이 계산상 불가능해야 함을 의미합니다 (생일 패러독스 공격에 대응).",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q33",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "CBC 모드는 직전 단계의 암호문 블록과 현재 평문 블록을 XOR한 후 암호화 알고리즘을 거칩니다. 첫 블록에는 초기화 벡터(IV)가 사용됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q33",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "CTR 모드는 카운터를 암호화한 키 스트림을 평문과 XOR하므로 스트림 암호처럼 동작하며, 블록 간 종속성이 없어 완전한 병렬 처리가 가능하고 에러 전파가 발생하지 않습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q34",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "RBAC(Role-Based Access Control)는 역할에 권한을 매핑하고 사용자에게 역할을 부여하여 관리가 용이하며 엔터프라이즈 환경에서 널리 쓰입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q34",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Clark-Wilson 모델은 상용 기업 환경의 무결성을 위해 '잘 형성된 트랜잭션(Well-formed Transaction)'과 직무 분리를 통해 데이터를 무단 수정하지 못하게 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q34",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "제1 역상 저항성(Pre-image Resistance)은 출력값(해시값)이 주어졌을 때 원래의 입력값을 역산하기 불가능해야 한다는 성질(단방향성)입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q34",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "비바(Biba) 모델은 무결성을 보호하기 위해 설계되었으며, 하위 무결성 등급의 데이터를 읽을 수 없고(No Read Down, 오염 방지), 상위 무결성 등급으로 데이터를 쓸 수 없는(No Write Up) 규칙을 적용합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q35",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "제1 역상 저항성은 주어진 해시값으로부터 원래의 원본 메시지를 역산할 수 없어야 함을 의미합니다. (제2 역상은 특정 메시지와 같은 해시값을 갖는 다른 메시지를 찾기 어려운 성질)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q35",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "PBKDF2, bcrypt, Argon2 등은 솔트와 수천 번 이상의 반복 연산(키 스트레칭)을 적용하여 GPU를 통한 무차별 대입 공격을 방어합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q35",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "OCSP(RFC 6960)는 인증서의 일련번호를 기반으로 폐기 여부를 실시간(Good, Revoked, Unknown) 질의 및 응답받을 수 있도록 설계된 경량 프로토콜입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q35",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "강제적 접근 통제(MAC)는 보안 레이블과 관리자 보안 정책에 의해 시스템이 접근을 강제하며, 파일 소유자라 할지라도 임의로 접근 권한을 부여하거나 변경할 수 없습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q36",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "SEED는 128비트 블록/128비트 키의 Feistel 구조 표준 암호입니다. ARIA는 국가정보원이 개발한 SPN 구조 암호입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q36",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "부인방지(Non-repudiation)는 서명자가 비밀로 간직한 고유의 개인키로만 전자서명이 생성되며, 누구나 서명자의 공개키로 검증할 수 있기 때문에 성립합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q36",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "BLP(Bell-LaPadula) 모델은 기밀성을 최우선으로 하며, 상위 등급 문서를 읽을 수 없고(No Read Up) 하위 등급으로 문서를 작성할 수 없는(No Write Down) 규칙을 가집니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q36",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "RTO(복구 목표 시간)는 재해 발생 후 비즈니스 기능이 복구되어 재개될 때까지 허용되는 최대 시간 한계이며, RPO(복구 목표 시점)는 복구 시 허용 가능한 데이터 손실 허용 시점을 뜻합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q37",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "전자봉투(Digital Envelope)는 공개키의 느린 연산 속도와 대칭키의 키 배송 문제를 결합하여 세션키를 비대칭키로 암호화해 전달하는 하이브리드 암호화 기술입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q37",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "CBC 모드 복호화는 P_i = D_k(C_i) XOR C_{i-1} 이므로, C_i의 에러는 해당 블록 P_i를 완전히 망가뜨리고 다음 블록 P_{i+1}의 동일 위치 1비트에 영향을 미친 후 전파가 끝납니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q37",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "차이니즈 월(Chinese Wall, Brewer-Nash) 모델은 주체의 이전 접근 이력을 추적하여 이해상충 관계에 있는 데이터 세그먼트 간의 정보 흐름을 동적으로 차단하는 모델입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q37",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "인증기관(CA)은 인증서의 발행, 서명, 폐기(CRL 생성)를 수행하는 핵심 발급 기관이며, 등록기관(RA)은 사용자의 신원 검증, 등록 접수 등 행정적 절차를 대행합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q38",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "Biba 모델은 무결성 보호 모델로서 하위 무결성 레벨의 데이터를 읽을 수 없고(No Read Down), 상위 무결성 레벨로 쓸 수 없습니다(No Write Up).",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q38",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ECC(Elliptic Curve Cryptography)는 타원곡선 이산대수 문제의 난해성을 이용해 적은 연산량과 짧은 키 길이로 높은 보안을 제공하여 모바일 및 TLS 1.3 표준에 널리 쓰입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q38",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "단일 손실 예상액 SLE(Single Loss Expectancy) = 자산 가치 AV(Asset Value) × 노출 계수 EF(Exposure Factor)입니다. 또한 연간 손실 예상액 ALE = SLE × ARO(연간 발생 빈도)입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q38",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "전자 봉투(Digital Envelope)는 세션키(대칭키)로 메시지를 고속 암호화하고, 그 세션키를 수신자의 공개키로 암호화하여 전송함으로써 속도와 키 분배 편의성을 동시에 달성하는 하이브리드 암호 기법입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q39",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "MFA(다중 요소 인증)는 알고 있는 것(PW), 가지고 있는 것(OTP/스마트폰), 고유한 것(지문/홍채) 중 2가지 이상의 서로 다른 팩터를 결합해 인증합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q39",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "최초의 순수 디피-헬만 프로토콜은 인증 기능이 없으므로 공격자가 중간에 개입하여 각각 키를 교환하는 중간자(MITM) 공격에 취약합니다. (전자서명 결합 필요)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q39",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "미러 사이트는 주 센터와 동일한 시스템을 구축하고 데이터를 실시간 복제(동기식)하여 RTO=0(즉각/수분 이내), RPO=0을 달성하는 최고 비용의 DRS 유형입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q39",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "위험 전가(Risk Transfer)는 보안 보험 가입, 아웃소싱 계약 등을 통해 위험으로 인한 재정적 손실 책임을 외부 기관에 이전하는 전략입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q40",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Chinese Wall(Brewer-Nash) 모델은 사용자의 이전 접근 이력에 기반하여 충돌하는 경쟁 회사의 데이터 접근을 동적으로 제한합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q40",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "HMAC(Hash-based MAC)은 비밀 대칭키와 해시 함수를 결합하여 데이터의 무결성(변조 여부)과 송신처 인증을 제공합니다. (대칭키이므로 부인방지는 제공하지 않음)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q40",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "전자서명(송신자 개인키 서명)은 메시지가 송신자에 의해 작성되었음을 입증(인증), 전송 중 변조되지 않았음(무결성), 나중에 발송 사실을 부인할 수 없음(부인방지)을 제공합니다. (기밀성은 수신자의 공개키로 암호화해야 달성됨)",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q40",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "PBKDF2는 솔트(Salt)를 추가하고 의도적으로 수만 번 이상의 HMAC 반복 연산(Iteration Count)을 거치게 하여 GPU 크래커나 레인보우 테이블 공격을 방어하는 표준 키 유도 함수입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q41",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "개인정보보호법 제34조에 따라 개인정보 유출을 알게 된 때에는 정당한 사유가 없는 한 72시간 이내에 정보주체에게 통지하고 개인정보보호위원회 또는 KISA에 신고해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q41",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개정 개인정보보호법에 따라 위반 시 '전체 매출액의 3% 이하'의 과징금이 부과될 수 있으며, 다만 기업이 위반행위와 관련 없는 매출액임을 입증한 경우 이를 제외합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q41",
      "prompt": "",
      "choices": [],
      "answer": 5,
      "explanation": "개인정보 보호법 시행령 제19조에 따른 고유식별정보 4가지는 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호입니다. 신용카드번호는 고유식별정보에 해당하지 않습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q41",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "단순한 영업 이익 증대나 마케팅 목적은 법정 동의 면제 사유가 아니며, 반드시 정보주체의 사전 명시적 동의를 받아야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q42",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "자산총액 1조 원 이상 또는 ISMS-P 인증 의무대상자 중 중대형 기업은 CISO가 타 직무(CIO, 개발책임자 등)를 겸직할 수 없도록 엄격히 분리 규정하고 있습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q42",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개인정보 영향평가(PIA)는 5만 명 이상의 민감정보 구축이나 100만 명 이상의 연계 시스템 등 일정 기준 이상의 공공기관 파일 구축 시 사전에 의무 수행합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q42",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "안전성 확보조치 기준 제8조에 따라 접속기록은 기본 1년 이상 보관·관리해야 하며, 5만 명 이상 정보주체 개인정보 또는 고유식별정보/민감정보 처리 시스템은 최소 2년 이상 보관해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q42",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "안전성 확보조치 기준 제7조에 따라 비밀번호는 관리자라 할지라도 원본을 알 수 없도록 안전한 일방향 암호화(One-Way Hash with Salt)를 적용하여 저장해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q43",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "DOA(Degree of Acceptable Risk, 수용 가능 위험 수준)는 조직의 위험 수용한도를 정의하는 척도로, 이를 초과하는 위험에 대해 감소, 회피, 전가 등의 통제를 적용합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q43",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "위험 회피(Risk Avoidance)는 해당 서비스 운영을 중지하거나 고위험 프로젝트를 취소하여 위험 요인을 근원적으로 배제하는 방식입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q43",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개정 개인정보 보호법 제34조에 따라 개인정보가 유출된 사실을 안 때에는 지체 없이(정당한 사유가 없는 한 72시간 이내) 정보주체에게 통지하고, 1천 명 이상 유출된 경우 전문기관(보호위/KISA)에 신고해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q43",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개인정보 영향평가는 공공기관을 대상으로 의무화되어 있으며, 50만 명 이상의 민감정보/고유식별정보 처리 시스템 또는 500만 명 이상의 개인정보 연계·구축 시스템 등이 법정 의무 대상입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q44",
      "prompt": "",
      "choices": [],
      "answer": 5,
      "explanation": "고유식별정보 4종은 주민등록번호, 여권번호, 운전면허번호, 외국인등록번호입니다. 휴대전화번호는 일반 개인정보입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q44",
      "prompt": "",
      "choices": [],
      "answer": 4,
      "explanation": "마케팅 목적은 정보주체의 명시적 동의(선택동의)가 필수적이며, 동의 없는 법적 처리 근거가 될 수 없습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q44",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 인증 기준은 1영역 관리체계 수립 및 운영 16개, 2영역 보호대책 요구사항 64개, 3영역 개인정보 처리단계별 요구사항 22개로 총 102개 기준입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q44",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "정보통신망 이용촉진 및 정보보호 등에 관한 법률 제48조의3에 따라 정보통신서비스 제공자는 침해사고가 발생하였을 때에는 즉시(안 때로부터 24시간 이내) 과기정통부 또는 KISA에 신고하여야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q45",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "ISMS 의무 대상자 중 하나는 정보통신서비스 부문 전년도 매출액이 100억 원 이상이거나, 전년도 직전 3개월간 일일평균 이용자 수가 100만 명 이상인 자입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q45",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "정보통신망법 제48조의3에 따라 정보통신서비스 제공자는 침해사고가 발생한 때에는 지체 없이 그 사실을 과기정통부 또는 KISA에 즉시 신고해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q45",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "정보통신망법 제45조의3에 따라 자산총액 5조 원 이상인 정보통신서비스 제공자 또는 자산총액 5천억 원 이상이면서 ISMS 의무대상자인 기업의 CISO는 정보기술(CIO)이나 기타 임원 직무를 겸직할 수 없습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q45",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "전자금융거래법 제9조에 따라 금융회사 및 전자금융업자는 무과실 손해배상 책임을 지며, 이용자에게 고의나 중과실(비밀번호 누설 등)이 있음을 금융회사가 직접 입증하지 못하면 책임을 면할 수 없습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q46",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "RTO(목표 복구 시간)는 재해 발생 후 업무가 정상 복구되어야 하는 목표 시한을 의미합니다. RPO(목표 복구 시점)는 허용 가능한 데이터 손실 시점입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q46",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "안전성 확보조치 기준상 비밀번호는 2종류 조합 시 최소 10자리 이상, 3종류 이상 조합 시 최소 8자리 이상으로 설정해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q46",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개인정보 보호법 제21조 및 시행령 제16조에 따라 개인정보가 불필요하게 되었을 때에는 정당한 사유가 없는 한 그로부터 5일 이내에 영구 파기해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q46",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS 및 ISMS-P 인증의 유효기간은 발급일로부터 3년이며, 인증 취득 기업은 인증 유효성을 지속적으로 유지하기 위해 매년 1회 이상 사후심사를 받아야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q47",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "개인정보 접속기록은 기본 1년 이상 보관해야 하지만, 5만 명 이상의 고유식별정보/민감정보를 처리하거나 기간통신사업자 시스템의 경우 2년 이상 안전하게 보관해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q47",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "Mirror Site는 주 센터와 동일한 전산 자원을 이중화하여 실시간 데이터 동기화를 수행함으로써 다운타임과 데이터 손실이 거의 없는 최고 수준의 DR 센터입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q47",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "정보통신기반 보호법 제9조에 따라 관리기관의 장은 소관 주요정보통신기반시설에 대하여 매년 취약점을 분석·평가하여야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q47",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개인정보 보호법 제22조의2에 따라 14세 미만 아동의 개인정보를 처리할 때에는 그 법정대리인의 동의를 받아야 하며, 법정대리인의 동의를 받기 위하여 필요한 최소한의 정보(성명, 연락처 등)는 아동으로부터 직접 수집할 수 있습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q48",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "연간손실예상액(ALE) = 단일손실예상액(SLE) × 연간발생률(ARO) = 10,000,000 × 0.2 = 2,000,000원입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q48",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "정보보호 정책(Policy)은 조직의 보안 철학과 방향성을 담은 최상위 문서로 경영진 승인을 거쳐 수립되며 원칙적으로 자주 변경되지 않습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q48",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "2020년 개정 전자서명법에 따라 공인인증서 제도가 폐지되고 다양한 민간 전자서명(카카오, 네이버, 패스 등)이 동일한 법적 효력을 갖게 되었습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q48",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 기준 1.1.1(경영진의 참여)에 따라 조직은 최고경영진, CISO, CPO 및 주요 부서장이 참여하는 '정보보호위원회'를 구성하고 정기적으로 회의를 개최하여 정책과 예산을 의결해야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q49",
      "prompt": "",
      "choices": [],
      "answer": 4,
      "explanation": "주민등록번호는 내부망/외부망을 불문하고 저장 시 100% 암호화가 법적 강제 사항이며 어떠한 예외도 허용되지 않습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q49",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "단순 파일 삭제(휴지통 비우기)는 포렌식 도구로 복원이 가능하므로 법령상 '복구 불가능한 영구 파기'로 인정되지 않아 인증 결함에 해당합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q49",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개인정보 보호법 제39조 제3항에 따라 개인정보처리자의 고의 또는 중대한 과실로 인하여 개인정보가 분실·도난·유출·위조·변조 또는 훼손된 경우 손해액의 5배를 넘지 않는 범위에서 배상액을 정할 수 있습니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q49",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개인정보 보호법 제28조의2에 따라 가명정보는 통계작성, 과학적 연구, 공익적 기록보존 등의 목적으로 정보주체의 동의 없이 안전하게 결합 및 처리될 수 있으며, 재식별은 엄격히 금지됩니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q50",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "주요정보통신기반시설 관리기관의 장은 매년 정기적으로 취약점 분석·평가를 실시하여야 합니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q50",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "개정 개인정보보호법 제35조의2에 신설된 '개인정보 전송요구권'은 정보주체가 자신에 관한 정보를 본인 또는 제3자에게 전송하도록 요구할 수 있는 권리입니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q50",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "IaaS(Infrastructure as a Service) 모델에서는 CSP가 물리 인프라, 전력, 네트워크, 가상화 하이퍼바이저를 책임지며, 고객은 가상머신 내의 게스트 OS, 방화벽 설정, 미들웨어, 애플리케이션, 데이터의 보안을 책임집니다.",
      "subject": "시스템 보안"
    },
    {
      "id": "written_q50",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "2023년 개정 개인정보 보호법 제64조의2에 따라 과징금 부과 기준이 유럽 GDPR 수준으로 강화되어 '전체 매출액의 3% 이하'로 변경되었으며, 사업자가 관련 없는 매출액을 소명할 경우 이를 제외하고 산정합니다.",
      "subject": "시스템 보안"
    }
  ],
  "summaries": [
    {
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] ASLR (Address Space Layout Randomization)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 프로그램 실행 시마다 스택, 힙, 라이브러리 메모리 주소를 난수화하여 고정된 주소를 노리는 셸코드 실행을 차단하는 메모리 보호 기법."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] DEP / NX (Data Execution Prevention / No-Execute)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 스택 및 힙 메모리 영역의 실행 권한을 원천 박탈하여 버퍼에 삽입된 악성 바이트 코드가 구동되지 못하도록 차단하는 기술."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] Stack Canary (스택 카나리 (스택 가드))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 함수의 지역변수와 SFP(복귀주소) 사이에 무작위 난수 카나리 값을 삽입하여, 함수 종료 시 카나리 변조 여부를 검사해 오버플로우를 감지하는 기법."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] TOCTOU (Time of Check to Time of Use)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 권한 검사 시점과 실제 자원 사용 시점 사이의 극미한 시간차를 악용하여 심볼릭 링크를 교체해 관리자 권한을 탈취하는 경쟁 조건 취약점."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] Rootkit (루트킷)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 시스템 관리자 권한을 획득한 후 침투 사실을 숨기기 위해 ps, ls, netstat 등 명령어를 변조하거나 커널 LKM을 조작하여 프로세스 및 파일을 은닉하는 도구 세트."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] wtmp / utmp (리눅스 로그인 계정 로그)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> wtmp는 성공한 로그인/로그아웃/재부팅 전체 누적 이력(last 조회), utmp는 현재 접속 중인 활성 사용자 상태(who/w 조회)를 기록하는 바이너리 로그."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] btmp / lastlog (접속 실패 및 최종 접속 로그)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> btmp는 로그인 실패 시도 이력(lastb 조회), lastlog는 각 사용자 계정별 최종 접속 일시 및 출발지 IP(lastlog 조회)를 기록하는 바이너리 로그."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] Sticky Bit (스티키 비트 (1000))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> /tmp 공용 디렉토리에 부여되어 누구나 파일을 생성할 수 있으나, 삭제 및 수정은 오직 해당 파일의 소유자와 root만 가능하도록 제한하는 특수 권한 비트."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] PAM (Pluggable Authentication Modules)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 응용프로그램 재컴파일 없이 시스템 인증 정책을 교체할 수 있는 플러그인 모듈 인터페이스 (required, requisite, sufficient, optional 플래그 운영)."
      ]
    },
    {
      "type": "term",
      "category_name": "시스템 필수 용어",
      "title": "[용어] chattr (+i) (파일 불변 속성 설정)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 리눅스 파일에 +i(Immutable) 속성을 부여할 경우 root 권한자라 할지라도 파일의 수정, 삭제, 이름 변경, 링크 생성을 원천 차단하는 명령어."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] SYN Cookie (신 쿠키)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> SYN Flooding 공격 시 서버 메모리 백로그 큐를 소진하지 않고, 클라이언트 연결 정보를 암호화 해시하여 TCP Sequence Number에 인코딩해 회신하는 방어 기법."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] Land Attack (랜드 어택)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 패킷의 출발지 IP/Port와 목적지 IP/Port를 희생자 자신의 IP/Port로 조작하여 자기 자신과 무한 루프 연결을 유발시키는 서비스 거부 공격."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] Smurf Attack (스머프 어택)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 출발지 IP를 희생자 IP로 위조한 후 다이렉트 브로드캐스트 주소로 ICMP Echo Request를 전송하여 네트워크 내 모든 호스트의 응답을 희생자에게 증폭 집중시키는 공격."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] TearDrop (티어드롭 어택)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> IP 패킷 단편화 시 오프셋 값을 인위적으로 중첩·왜곡시켜 수신 호스트가 패킷을 재조합하는 과정에서 크래시 및 재부팅을 유발하는 취약점 공격."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] Slowloris (슬로로리스)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> HTTP 요청 헤더의 끝을 알리는 개행문자(\\r\\n\\r\\n)를 전송하지 않고 불완전한 헤더를 천천히 유지하여 웹 서버의 가용 연결 슬롯을 고갈시키는 L7 DoS 공격."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] RUDY (R-U-Dead-Yet (Slow HTTP POST))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> HTTP POST 요청 시 Content-Length를 거대하게 설정하고 본문 바이트 데이터를 극도로 느린 속도로 분할 전송하여 서버 연결을 장시간 점유하는 공격."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] IPSec (AH / ESP) (IP Security Protocol)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 네트워크 계층(L3) VPN 표준 프로토콜로, AH는 인증과 무결성만 제공(NAT 불가), ESP는 기밀성(암호화), 무결성, 인증을 모두 제공(NAT-T 지원)."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] IKE (Internet Key Exchange (UDP 500))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> IPSec에서 양단 호스트 간 보안 결합(SA) 협상 및 대칭 세션키를 Diffie-Hellman 알고리즘으로 안전하게 자동 생성·교환하는 표준 프로토콜."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] WPA3 SAE (동등동시인증 (SAE Handshake))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> WPA3 무선 LAN 표준에 도입된 상호 인증 프로토콜로, 강력한 암호화 키 교환을 통해 기존 4-Way Handshake의 오프라인 사전 대입 공격을 원천 무력화함."
      ]
    },
    {
      "type": "term",
      "category_name": "네트워크 필수 용어",
      "title": "[용어] DNSSEC (DNS 보안 확장 프로토콜)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> DNS 응답 데이터에 공개키 기반 전자서명(RRSIG)을 부착하여 악의적인 DNS 캐시 포이즈닝 및 도메인 파밍을 방지하는 보안 표준."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] PreparedStatement (파라미터화된 쿼리 (바인딩 변수))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> SQL 쿼리 컴파일 시점에 입력값을 데이터 리터럴로 고정 바인딩하여, 사용자 입력값이 쿼리 문법 구조를 변조하지 못하도록 만드는 SQLi 최우선 방어책."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] Stored XSS (저장형 크로스사이트 스크립팅)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 공격자가 삽입한 악성 자바스크립트가 게시판 DB에 영구 저장되어, 해당 글을 조회하는 모든 무고한 사용자의 브라우저에서 자동 실행되는 가장 치명적인 XSS."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] CSRF Token (크로스사이트 요청 위조 방지 토큰)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 사용자의 세션마다 서버가 예측 불가능한 난수 토큰을 발급하여 폼 전송 시 검증함으로써, 타 사이트로부터 위조된 비인가 상태 변경 요청을 차단하는 기법."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] SSRF (Server-Side Request Forgery)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 웹 서버가 취약한 URL 요청 파라미터를 그대로 처리할 때, 공격자가 서버를 중계 삼아 접근 통제된 내부망 인트라넷이나 클라우드 메타데이터 API를 호출하는 공격."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] HttpOnly (쿠키 보안 플래그)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 브라우저 자바스크립트의 document.cookie 객체 접근을 원천 차단하여, XSS 공격이 발생하더라도 세션 하이재킹용 쿠키 탈취를 방지하는 설정."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] SameSite Cookie (쿠키 전송 범위 제어 속성)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> Strict(타 사이트 링크 시 쿠키 전송 완전 차단) 또는 Lax(안전한 GET 탐색만 허용)를 설정하여 서드파티 컨텍스트에서의 CSRF 공격을 방어하는 최신 표준."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] HSTS (HTTP Strict Transport Security)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 브라우저가 해당 도메인 접속 시 첫 연결부터 모든 통신을 오직 HTTPS로만 강제 연결하도록 지시하여 평문 다운그레이드(SSL Stripping)를 방어하는 헤더."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] CSP (Content Security Policy)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 웹 브라우저가 스크립트, 스타일, 이미지 등을 로드하고 실행할 수 있는 신뢰할 수 있는 출처 도메인을 화이트리스트로 지정하여 XSS 및 인젝션을 차단하는 헤더."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] TDE (Transparent Data Encryption)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> DBMS 스토리지 파일 레벨에서 자동으로 실시간 암·복호화를 수행하여, 응용프로그램 수정 없이 백업 파일 유출 시 데이터 평문 유출을 방지하는 투명 암호화."
      ]
    },
    {
      "type": "term",
      "category_name": "애플리케이션 필수 용어",
      "title": "[용어] Dual Signature (이중 서명 (SET 프로토콜))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 전자상거래에서 주문정보 해시와 결제정보 해시를 결합하여 한 번에 전자서명함으로써, 상점은 카드번호를 못 보고 카드사는 주문 품목을 알 수 없게 보장하는 기법."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Feistel vs SPN (블록 암호 구조)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> Feistel은 평문을 좌우 분할하여 스왑하며 암·복호화 구조가 동일(DES, SEED), SPN은 치환(S-Box)과 순열(P-Box)을 반복해 병렬 연산에 최적화(AES, ARIA)."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] AES (Advanced Encryption Standard)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> Rijndael 알고리즘 기반 전 세계 표준 대칭키 블록 암호. 128비트 블록 크기, 128/192/256비트 키 길이를 지원하며 고속 하드웨어 연산 지원."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] CTR Mode (카운터 운영 모드)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 1씩 증가하는 카운터 값을 블록 암호화한 뒤 평문과 XOR 연산하는 운영 모드로, 완벽한 병렬 처리가 가능하여 최신 고속 보안 통신에서 널리 활용."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] RSA (소인수분해 기반 공개키 암호)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 거대한 두 소수의 곱을 구하기는 쉬우나 합성수를 소인수분해하기는 극도로 어렵다는 수학적 난해성을 활용한 공개키 암호 및 전자서명 알고리즘."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] ECC (타원곡선 암호 (Elliptic Curve))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 타원곡선 상의 이산대수 난해성에 기반하여, 256비트의 매우 짧은 키 길이로 RSA 3,072비트와 동등한 안전성을 제공하는 모바일/경량 표준 공개키 암호."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Collision Resistance (충돌 저항성)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 단방향 해시 함수에서 H(x) = H(y)를 만족하는 임의의 서로 다른 두 입력값 쌍 (x, y)를 찾아내는 것이 계산상 불가능해야 한다는 안전성 특성."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] OCSP (Online Certificate Status Protocol)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 인증서 폐지 목록(CRL) 파일 전체를 다운로드하지 않고, 단일 인증서의 시리얼 번호로 폐지 여부(Good/Revoked/Unknown)를 실시간 온라인 조회하는 프로토콜."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Digital Envelope (전자봉투)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 대용량 본문은 빠른 대칭 세션키로 암호화하고, 그 세션키만을 수신자의 공개키로 암호화하여 함께 전달하는 안전하고 효율적인 하이브리드 암호 전달 기법."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] PBKDF2 / bcrypt (패스워드 전용 해시 함수)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 단방향 해시 시 솔트(Salt)를 추가하고 수만 번의 반복 연산(Key Stretching)을 강제하여 GPU 및 전용 하드웨어를 통한 고속 레인보우 테이블 무차별 대입을 무력화함."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] BLP Model (Bell-LaPadula (기밀성 모델))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> No Read Up(상위 등급 읽기 금지), No Write Down(하위 등급 쓰기 금지) 원칙을 통해 상위 기밀 데이터의 하위 등급 유출을 철저히 차단하는 군사 보안 모델."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Biba Model (비바 무결성 모델)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> No Read Down(하위 무결성 읽기 금지), No Write Up(상위 무결성 쓰기 금지) 원칙을 적용하여 신뢰할 수 없는 오염된 데이터가 상위 시스템으로 유입되는 것을 방지."
      ]
    },
    {
      "type": "term",
      "category_name": "암호학 필수 용어",
      "title": "[용어] Chinese Wall (만리장성 모델 (이해관계 상충 방지))",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> 금융 및 컨설팅 기업에서 사용자의 이전 데이터 접근 이력에 따라 이해관계가 상충되는 경쟁사의 기밀 데이터 접근을 동적으로 차단하는 상업 보안 모델."
      ]
    },
    {
      "type": "term",
      "category_name": "관리·법률 필수 용어",
      "title": "[용어] ALE / SLE / ARO (정량적 위험분석 3대 공식)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> SLE(단일손실예상액) = 자산가치 × 노출계수, ALE(연간손실예상액) = SLE × ARO(연간발생빈도). 통제 대책 도입 타당성은 통제 전후 ALE 절감액으로 평가."
      ]
    },
    {
      "type": "term",
      "category_name": "관리·법률 필수 용어",
      "title": "[용어] RTO vs RPO (재해복구 목표 지표)",
      "badge": "필수 용어사전",
      "points": [
        "<strong>핵심 정의:</strong> RTO(목표 복구 시간)는 재해 발생 후 업무가 정상 복구될 때까지 허용 가능한 최대 다운타임, RPO(목표 복구 시점)는 허용 가능한 최대 데이터 유실 시점."
      ]
    },
    {
      "type": "term",
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
      "id": "prac_q1",
      "prompt": "",
      "choices": [],
      "answer": "2",
      "explanation": "디렉토리(777 - 027 = 750), 파일(666 - 027 = 640, 실행비트 미부여)을 만족하는 보안 표준 umask 값은 027입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q1",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "id 파라미터에 UNION SELECT 구문과 information_schema 메타데이터를 결합하여 사용자 계정과 DB 스키마를 유출하는 전형적인 Union-Based SQL Injection 공격입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q1",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: distance]\ndistance는 이전 content 매칭의 끝 지점부터 몇 바이트 떨어진 곳부터 다음 content 탐색을 시작할지(상대적 오프셋)를 지정하는 옵션입니다. 반면 within은 distance 지점부터 최대 몇 바이트 범위 내에서 찾을지를 지정합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q1",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 공격 유형: Blind SQL Injection (참/거짓 조건 기반 불린 블라인드 인젝션)\n2. 공격 목적: SUBSTRING, ASCII 함수를 이용하여 DB 시스템의 현재 사용자명(user()) 1글자씩 바이트 단위로 참/거짓 응답을 대조해 데이터베이스 기밀 정보를 무차별 추출하려는 시도(User-Agent에 sqlmap 도구 흔적 존재).\n3. 방어 대책: SQL 쿼리 작성 시 파라미터가 쿼리 구조에 영향을 주지 않도록 PreparedStatement(파라미터화된 쿼리)를 필수로 적용하고, 정수형 파라미터(idx)는 Integer.parseInt() 등을 통해 숫자형 유효성 검증을 수행한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q2",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "Options -Indexes 또는 Indexes 옵션을 제거해야 디렉토리 목록 노출(Directory Listing)을 방지할 수 있습니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q2",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "%2e%2e%2f는 URL 디코딩 시 '../../'로 변환되며, 상위 디렉토리로 이동하여 시스템의 /etc/passwd 파일을 불법 열람하는 Path Traversal(디렉토리 순회) 공격입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q2",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: REJECT]\nREJECT 타겟은 접속을 차단하면서 클라이언트에게 즉시 ICMP unreachable 또는 TCP RST 응답을 돌려주어 클라이언트가 타임아웃까지 대기하지 않게 합니다. 반면 DROP은 패킷을 조용히 폐기합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q2",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\nalert tcp 192.168.1.0/24 any -> any any (msg:\"WebShell Traffic Detected\"; content:\"eval(base64_decode\"; nocase; sid:2000001; rev:1;)\n- 출발지 IP 대역: 192.168.1.0/24 any\n- 목적지 IP 대역: any any\n- content: 문자열 매칭\n- nocase: 대소문자 무시",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q3",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "-a(모든 소켓), -n(IP/포트 숫자로 표시), -t(TCP), -p(프로세스 ID/이름 표시) 옵션인 'netstat -antp'가 침해사고 분석의 기본 명령어입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q3",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "문자열 결합 방식의 Statement는 SQL 인젝션에 취약하므로, 위치 홀더(?)를 사용하는 PreparedStatement 객체에 파라미터 바인딩(setString)을 수행해야 안전합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q3",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: lsof (또는 fuser)]\nlsof(List Open Files)는 시스템에서 활성화된 모든 파일 디스크립터(일반 파일, 디렉토리, 네트워크 소켓 등)와 이를 점유하고 있는 프로세스(PID) 정보를 출력하는 핵심 점검 도구입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q3",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\niptables는 순차적으로 룰을 평가하므로,\n1) iptables -A INPUT -p tcp -s 192.168.1.10 --dport 3306 -j ACCEPT (인가 웹서버 허용)\n2) iptables -A INPUT -p tcp --dport 3306 -j DROP (그 외 전면 차단)\n순서대로 등록해야 허용 룰이 먼저 적용된 후 차단 룰에 의해 나머지 접속이 방어됩니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q4",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "-mtime -1은 수정된 지 1일(24시간) 이내인 파일을 의미합니다. (+1: 24시간 이전, 1: 정확히 24~48시간 사이)",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q4",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "URI나 요청에 cmd.jsp 웹셸 파일과 명령어 파라미터(cmd=)가 포함된 웹셸 악용 행위를 탐지하는 시그니처입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q4",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: ctime]\nmtime은 파일의 실제 내용(데이터)이 수정된 시각이고, atime은 파일이 읽히거나 실행된 시각이며, ctime은 메타데이터(소유자, 권한 등 inode 속성)가 변경된 시각입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q4",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 취약점: SQL Injection (사용자 입력값이 쿼리 문자열에 동적으로 연결되어 쿼리 구조 변조 가능)\n2. 개선 코드:\nString query = \"SELECT * FROM members WHERE user_id = ? AND user_pw = ?\";\nPreparedStatement pstmt = conn.prepareStatement(query);\npstmt.setString(1, id);\npstmt.setString(2, pw);\nResultSet rs = pstmt.executeQuery();",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q5",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "TCP Wrapper는 /etc/hosts.allow를 먼저 확인하고 일치하면 즉시 허용하며, 없을 때 hosts.deny를 확인합니다. 둘 다 없으면 기본 허용됩니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q5",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "기본 정책(Policy)을 DROP으로 설정한 후 80, 443 포트 허용 및 세션 응답(ESTABLISHED, RELATED)을 허용하는 상태추적 방화벽 구성이 정답입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q5",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: 4672]\n4672 이벤트는 관리자(Administrator) 그룹에 속한 특권 계정이 로그인하여 시스템 관리 권한(SeDebugPrivilege 등)을 부여받았을 때 4624(일반 성공)와 함께 발생하는 감사 이벤트입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q5",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 취약점: XSS (악의적인 자바스크립트 <script>alert(document.cookie)</script> 등이 브라우저에서 실행되어 세션 탈취 위험)\n2. 개선 코드: HTML 특수문자(&, <, >, \", ')를 HTML Entity(&amp;, &lt;, &gt;, &quot;, &#39;)로 변환하거나, JSTL 태그 라이브러리를 사용하여 <c:out value=\"${param.content}\" escapeXml=\"true\" />로 출력한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q6",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "-A INPUT(인바운드 체인 추가), -p tcp(프로토콜), -s(출발지 IP), --dport 22(목적지 포트), -j DROP(폐기)이 정확한 문법입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q6",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "블랙리스트 방식은 우회(jspx, php5, phtml 등)가 쉬우므로, 허용된 안전한 확장자만을 허용하는 화이트리스트 검증을 서버사이드에서 수행해야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q6",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: Lax]\nSameSite=Strict는 타 사이트에서의 모든 요청에서 쿠키를 일절 배제하며, SameSite=Lax는 최상위 탐색(안전한 GET 링크 이동)을 제외한 모든 교차 출처 요청(POST 등)에서 쿠키 전송을 차단하여 CSRF를 방어합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q6",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 침해 유형: Path Traversal (디렉토리 탐색 / 경로 조작 공격)\n2. 대상 자원: URL 인코딩된 '..%2F' (상위 디렉토리 이동 ../) 기법을 활용하여 웹 루트를 벗어나 시스템 최고 기밀인 /etc/shadow (계정 패스워드 해시 파일) 탈취를 시도함 (403 Forbidden으로 차단됨).",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q7",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "Snort에서 바이너리 바이트값은 파이프(|) 기호로 감쌉니다. 예: content:\"|90 90 90 90|\";",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q7",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "UID가 0이면 계정 이름에 상관없이 리눅스 커널은 최고 관리자 root 권한으로 인식하므로 전형적인 슈퍼유저 권한 백도어 계정입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q7",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: #{param}]\nMyBatis에서 ${param}은 파라미터 값을 따옴표 없이 그대로 쿼리 문자열에 합치므로 SQL 인젝션에 취약합니다. #{param}을 사용해야 PreparedStatement의 '?' 파라미터로 안전하게 바인딩됩니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q7",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n증거의 휘발성이 높은 순서대로 수집해야 데이터 유실을 방지할 수 있습니다.\n1단계: CPU 레지스터 및 캐시 메모리\n2단계: 물리적 RAM 메모리 (메모리 덤프 확보)\n3단계: 네트워크 연결 상태(netstat, lsof) 및 실행 중인 프로세스(ps)\n4단계: 로컬 비휘발성 저장장치(디스크 이미지 원본 사본 및 타임라인 분석)",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q8",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "각 사용자별 crontab 설정은 /var/spool/cron/ 또는 /var/spool/cron/crontabs/ 디렉토리에 사용자 계정명 파일로 저장됩니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q8",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "동일 IP에서 다수의 관리자 및 기본 계정명으로 짧은 시간 동안 SSH 비밀번호 인증 실패가 반복되는 전형적인 SSH 사전 대입 공격 로그입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q8",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: 완전 전방향 보안 (PFS: Perfect Forward Secrecy)]\nEphemeral Diffie-Hellman(DHE, ECDHE)과 같이 세션마다 일회성 임시 키를 생성하고 폐기함으로써 장기 비밀키가 노출되어도 과거 트래픽의 복호화를 방지합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q8",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n버퍼 크기를 넘어서는 데이터 복사로 인한 스택 오버플로우를 막기 위해 대상 버퍼의 최대 길이를 명시하는 strncpy, strncat, snprintf 또는 윈도우 환경의 보안 강화 함수(strcpy_s, strcat_s, sprintf_s)를 사용해야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q9",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "세미콜론(;)은 이전 명령 종료 후 다음 명령을 순차 실행하며, 파이프(|)는 이전 명령어의 출력을 다음 명령어로 넘겨 임의 명령을 실행하게 만듭니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q9",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "JSTL의 <c:out> 태그는 기본적으로 escapeXml=\"true\" 속성이 적용되어 HTML 특수문자를 자동 엔티티 인코딩하여 XSS를 방어합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q9",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: .bash_history]\n침해사고 분석 시 공격자가 터미널에서 수행한 행위를 확인하기 위해 사용자 홈 디렉토리 하위의 ~/.bash_history 파일을 우선 분석합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q9",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n<LimitExcept GET POST>\n  Require all denied\n</LimitExcept>\nLimitExcept 지시자를 사용하여 GET과 POST를 제외한 모든 HTTP 메서드(TRACE: XST 공격 유발, PUT/DELETE: 임의 파일 조작)의 실행을 거부(denied) 처리합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q10",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "&lt;, &gt;, &amp;, &quot;, &#x27; 등으로 치환하는 HTML Entity 인코딩이 XSS 방어의 필수 조치입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q10",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "개인정보 다운로드 시에는 유출 사고를 방지하고 오남용을 추적하기 위해 다운로드 사유 확인 및 승인 절차를 수립하고 접속기록에 남겨야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q10",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: CRL (Certificate Revocation List)]\nCRL은 효력이 상실되거나 취소된 인증서들의 일련번호 목록을 CA가 전자서명하여 정기적으로 게시하는 공지 목록입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q10",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 공격 명칭: ARP Spoofing (ARP 캐시 포이즈닝)\n2. 방어 대책: 클라이언트 및 게이트웨이에서 'arp -s [게이트웨이IP] [정상MAC]' 명령어를 수행하여 ARP 테이블 엔트리를 동적(Dynamic)에서 정적(Static)으로 고정시키거나, 스위치에서 Dynamic ARP Inspection(DAI) 보안 기능을 활성화한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q11",
      "prompt": "",
      "choices": [],
      "answer": "3",
      "explanation": "법정 5대 통지사항은 ①유출 항목, ②유출 시점과 경위, ③피해 최소화 조치, ④대응조치 및 구제절차, ⑤담당부서 및 연락처입니다. 해커 신원은 포함되지 않습니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q11",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "kisa 주요기반시설 점검 가이드에 따라 /etc/passwd는 root 소유 644(-rw-r--r--), 패스워드 해시가 들어있는 /etc/shadow는 root 소유 400(-r--------) 이하로 제한해야 안전합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q11",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: strings]\nstrings 명령어는 실행 바이너리나 코어 덤프 파일에서 연속된 4글자 이상의 출력 가능한 텍스트 문자열을 추출하여 C2 도메인, IP, 오류 메시지 등을 신속히 파악할 수 있게 합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q11",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 공격 유형: SSH 사전 무차별 대입 공격(Brute Force)\n2. 자동 방어 대책: fail2ban 도구를 설치하여 일정 시간 동안(예: 10분 내 5회 이상) 인증 실패 로그가 탐지되면 iptables 방화벽 규칙을 동적으로 생성하여 해당 공격자 IP를 일정 시간(1시간~영구) 자동 차단한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q12",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "무결성의 원칙(Integrity)은 해시값(MD5, SHA-256) 비교를 통해 증거가 일체 수정·변조되지 않았음을 입증하는 원칙입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q12",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "SecureRandom은 예측 불가능한 엔트로피 시드를 사용하여 난수를 생성하므로 암호학적 토큰 및 키 생성에 필수적입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q12",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: -I (Insert)]\n-A(Append)는 체인의 맨 끝에 규칙을 추가하지만, -I(Insert)는 특정 행 번호(-I INPUT 1)에 규칙을 우선순위 최상단으로 삽입할 때 사용합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q12",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\njava.util.Random이나 Math.random()은 선형 합동 생성기(LCG) 기반의 의사 난수로서 시드 값이 추정되면 다음 난수가 쉽게 예측됩니다. 보안에 민감한 키/토큰 생성 시에는 OS의 엔트로피 풀을 사용하는 암호학적으로 안전한 java.security.SecureRandom 클래스를 사용해야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q13",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "sshd_config 파일에 'PermitRootLogin no'를 설정하여 관리자 계정의 무차별 대입 직접 침투를 차단합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q13",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "Nginx에서 'add_header X-Frame-Options DENY always;' 설정을 통해 어떠한 사이트에서도 해당 웹 페이지를 iframe 등에 로드할 수 없도록 강제합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q13",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: 7% 이상]\n전자금융감독규정 제8조에 따라 금융회사는 총 IT 인력의 5% 이상을 정보보호 전담인력으로 확보하고, 총 IT 예산의 7% 이상을 정보보호 예산으로 편성하도록 권고 및 규정하고 있습니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q13",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n연계보관성의 원칙(Chain of Custody)은 디지털 증거가 최초 압수 시점부터 법정에 현출될 때까지 위조, 변조, 훼손되지 않았음을 입증하기 위해 증거 취급 이력을 연속적으로 기록하고 증명하는 절차적 원칙입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q14",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "ServerTokens Prod는 Server 헤더에 단순히 'Apache'만 출력하고 세부 OS/모듈 버전을 숨기며, ServerSignature Off는 에러 페이지의 서명을 제거합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q14",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "윈도우 프리페치(C:\\Windows\\Prefetch)는 응용 프로그램의 최초 및 최근 실행 일시(최대 8회), 실행 횟수, 실행 파일 경로와 DLL 목록을 담고 있어 악성코드 실행 증적 확보에 핵심입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q14",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: 다중인증 (2차 인증 / Multi-Factor Authentication)]\n안전성 확보조치 기준에 따라 관리자 페이지 및 개인정보처리시스템에 외부 또는 내부에서 접속 시 패스워드 외에 OTP, 보안토큰 등 다중인증을 의무 적용해야 합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q14",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 발생 원인: response.sendRedirect(url)과 같이 외부 사용자가 전달한 임의의 URL 파라미터로 무조건 이동시킬 때 발생.\n2. 방어 대책: 이동 가능한 URL을 사전에 정의된 도메인(예: 사내 도메인만 허용)으로 한정하는 엄격한 화이트리스트 검증을 적용하거나, 상대 경로(/index.do)로의 이동만 허용한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q15",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "/etc/login.defs에서 PASS_MAX_DAYS(최대 유효일수, 예: 90), PASS_MIN_DAYS(최소 변경간격일수), PASS_MIN_LEN(최소길이) 등을 정의합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q15",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "SYN 요청을 받고 SYN/ACK를 보낸 후 최종 ACK를 대기하는 반개방 상태가 지속될 때 SYN_RECV(SYN_RECEIVED) 상태의 소켓이 폭증합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q15",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: 주기적 강제 변경 폐지 및 유출 패스워드 사전 대조]\nNIST 가이드라인은 사용자가 패스워드를 억지로 변경하면서 패턴을 단순화하는 부작용을 막기 위해 주기적 강제 변경을 폐지하고, 최소 8자 이상(권장 12자 이상) 및 기유출 데이터베이스 대조를 권고합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q15",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\nTripwire(또는 AIDE)는 무결성 기준 데이터베이스(Baseline DB)를 생성한 후, 파일 크기, 해시값, 권한, 수정 시각 등을 정기적으로 비교하여 악성코드에 의한 파일 변조를 즉시 식별하는 HIDS 도구입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q16",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "PATH 환경변수에 현재 디렉토리('.')가 앞에 포함되어 있으면 악의적인 공격자가 해당 디렉토리에 트로이목마 명령어(ls 등)를 두고 root가 실행하도록 유도할 수 있습니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q16",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "파일 다운로드 시 파라미터에서 상위 경로 탐색 문자(../)를 필터링하거나, File.getCanonicalPath()로 정규화된 경로가 허용된 다운로드 루트 디렉토리 내에 위치하는지 검증해야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q16",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: Command & Control (C2)]\n악성코드가 설치(Installation)된 후 C2 채널을 확립하여 공격자의 원격 명령을 수신하고, 이를 통해 내부 침투 심화 및 목적 달성(Actions on Objectives) 단계로 진입합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q16",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\nStrict-Transport-Security: max-age=31536000; includeSubDomains; preload\n- max-age=31536000: 1년(초 단위)\n- includeSubDomains: 모든 서브도메인에도 동일 강제 적용\n- preload: 브라우저 내장 HSTS 프리로드 목록 등록 지원",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q17",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "Heartbleed 취약점은 OpenSSL의 Heartbeat 요청 패킷 길이 검증 누락으로 최대 64KB의 프로세스 메모리(비밀키, 세션쿠키 등)가 평문으로 유출되는 취약점입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q17",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "Telnet, FTP, rlogin/rsh/rcp는 통신 구간 암호화가 없어 스니핑에 취약하므로 SSH, SFTP, SCP 등 보안 프로토콜로 대체해야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q17",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge)]\n공격자의 생애주기 전반에 걸친 세부 공격 기술을 매트릭스 형태로 분류하여 침해 탐지 및 모의훈련에 널리 활용되는 글로벌 프레임워크입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q17",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n사내 도메인의 권한(Authoritative) DNS 서버는 외부 인터넷 사용자에 대해 재귀적 질의를 수행할 필요가 없습니다. named.conf의 options 블록에 'recursion no;' 또는 'allow-recursion { trusted_network; };'를 설정하여 Open Resolver 악용을 차단합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q18",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "계정 로그인 실패 횟수 초과 시 잠금(lock)을 처리하는 표준 모듈은 pam_faillock.so (최신 RHEL) 또는 pam_tally2.so (이전 버전)입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q18",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "NIST 침해사고 대응 표준 4단계는 1. 준비 -> 2. 탐지 및 분석 -> 3. 봉쇄, 제거 및 복구 -> 4. 사후 검토 및 활동입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q18",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: auditctl]\nauditctl 명령어를 사용하여 리눅스 커널 감사 시스템(auditd)에 감시 규칙(-w /etc/passwd -p wa -k passwd_change)을 등록함으로써 주요 파일 변경을 실시간 감적 추적합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q18",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 암호화 대상 저장소: 데이터베이스(DB), 업무용 PC(하드디스크), 모바일 단말기, 보조저장매체(백업 테이프, USB), 로그 파일 등.\n2. 암호화 요건: 국가 표준 또는 국제적으로 공인된 안전한 양방향 대칭 암호화 알고리즘(AES, ARIA, SEED 등 128비트 이상, 권장 256비트)을 적용해야 한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q19",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "icacls는 윈도우 파일/디렉토리의 DACL 및 SACL 접근 권한을 확인하고 부여·제거하는 핵심 보안 명령어입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q19",
      "prompt": "",
      "choices": [],
      "answer": "5",
      "explanation": "gets는 버퍼 크기를 검사하지 않아 가장 취약한 함수이며 버퍼 길이를 지정받는 fgets로 대체해야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q19",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: SOAR]\nSIEM이 로그 수집 및 상관분석에 초점을 맞춘다면, SOAR은 워크플로우 오케스트레이션과 플레이북 기반 자동화 대응을 결합하여 침해사고 대응 속도를 획기적으로 단축합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q19",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\ntcpdump -i eth0 'host 192.168.1.100 and tcp port 80 and (tcp[tcpflags] & tcp-syn != 0)'\nTCP 헤더 13번째 바이트의 플래그 비트 중 SYN 비트를 비트마스킹(&)하여 SYN Flooding 패킷을 정밀하게 추출합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q20",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "디스크 쿼터(Quota)는 사용자/그룹의 디스크 블록 사용량 및 아이노드 생성 수를 제한하여 DoS를 방어합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q20",
      "prompt": "",
      "choices": [],
      "answer": "3",
      "explanation": "개인정보보호법 제26조 위탁 계약 필수 사항은 ①위탁 목적/범위, ②목적외 처리 금지, ③보호조치, ④재위탁 제한, ⑤관리감독, ⑥손해배상 등입니다. 수탁사 직원 주민번호는 포함되지 않습니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q20",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: EDR]\nEDR은 엔드포인트의 모든 활동을 상세히 추적 및 기록하여 파일리스(Fileless) 공격, 랜섬웨어 및 알려지지 않은 제로데이 공격을 탐지하고 분석 및 대응 기능을 제공합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q20",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n솔트는 사용자마다 고유하고 예측 불가능한 난수(SecureRandom, 최소 16바이트 이상)로 생성되어야 동일한 패스워드를 가진 사용자들의 해시값이 서로 달라지며, 레인보우 테이블 공격이 원천 무력화됩니다. 솔트는 공개되어도 안전하므로 해시값과 함께 평문으로 저장됩니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q21",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "휘발성 데이터 수집 순서는 레지스터/캐시 -> 라우팅테이블/ARP캐시/프로세스테이블 -> 물리 메모리(RAM) -> 임시 파일 -> 디스크 순입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q21",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "윈도우 보안 이벤트 로그에서 이벤트 ID 4624는 로그인 성공(An account was successfully logged on), 4625는 로그인 실패(An account failed to log on)입니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q21",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: SPAN (Switch Port Analyzer)]\nSPAN은 로컬 스위치의 포트나 VLAN 트래픽을 IDS, 패킷 분석기(Wireshark)가 물려 있는 모니터링 포트로 그대로 복사(Mirroring)해 주는 기술입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q21",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n공격자가 파일시스템에서 원본 파일을 unlink(rm)하여 삭제했더라도 프로세스가 메모리에서 실행 중인 동안에는 /proc/[PID]/exe 심볼릭 링크가 해당 실행 파일의 메모리 이미지를 가리키므로, 이를 복사하여 악성코드 원본 바이너리를 완벽히 복구할 수 있습니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q22",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "/sbin/nologin 및 /bin/false는 서비스 구동용 데몬 계정이 대화형 터미널 셸을 획득하지 못하도록 로그인 접근을 원천 차단하는 설정입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q22",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "루트킷이 ps 명령어를 후킹해 은닉했더라도 커널 메모리를 반영하는 /proc/[PID] 디렉토리를 전수 검사하여 숨겨진 악성 프로세스를 식별할 수 있습니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q22",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: Volatility]\nVolatility는 리눅스, 윈도우, 맥의 물리 RAM 덤프 이미지를 파싱하여 실행 중이던 프로세스 트리(pslist), 활성 네트워크 연결(netscan), 인젝트된 셸코드(malfind) 등을 정밀 분석하는 대표적 도구입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q22",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 위반 기준: 2.7.2(암호화 적용) 및 3.2.3(개인정보 표시제한/마스킹)\n2. 개선 대책: 개인정보 처리화면에서 주민등록번호, 계좌번호 등 고유식별정보를 표출할 때에는 업무상 필수적인 경우를 제외하고는 마스킹(생년월일 6자리 제외 뒷자리 *** 처리)하여 표출하고, 마스킹 해제 시에는 사유 입력 및 책임자 승인 이력을 기록해야 한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q23",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "BPF(Berkeley Packet Filter) 문법에 따라 'host 192.168.1.50 and not port 80'으로 조합합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q23",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "일반 암호학적 해시는 고속 계산에 최적화되어 있어 무차별 대입 공격에 취약합니다. 솔트(Salt)와 반복 연산을 강제하는 패스워드 전용 단방향 함수(bcrypt 등)를 써야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q23",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: SBOM (Software Bill of Materials)]\nSBOM은 소프트웨어의 부품 명세서로, Log4j 사태와 같은 오픈소스 취약점 발생 시 해당 라이브러리를 사용 중인 자산을 즉시 식별하여 조치할 수 있게 합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q23",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n/etc/shadow 파일의 두 번째 필드는 암호화된 비밀번호입니다. 이 필드가 비어 있거나(\"\") 널 값인 경우 비밀번호 입력 없이 로그인이 가능하므로, awk나 getent 명령어로 두 번째 필드가 빈 계정을 전수 식별하여 계정 잠금(passwd -l) 또는 비밀번호 설정을 강제해야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q24",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "리눅스에서는 sha256sum, sha1sum, md5sum 명령어를 사용하여 표준 체크섬 해시를 계산 및 검증합니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q24",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "'NOPASSWD: ALL' 설정은 해당 계정이 비밀번호 검증 없이 즉시 root 권한의 모든 명령을 실행할 수 있어 계정 탈취 시 즉각적인 시스템 완전 장악으로 이어집니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q24",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: 취급자의 신용등급]\n안전성 확보조치 기준에 따른 필수 항목은 1) 계정(식별자), 2) 접속일시, 3) 접속자 IP 주소, 4) 수행한 업무내역(열람, 수정, 삭제, 출력 등), 5) 처리한 정보주체 식별정보입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q24",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 시스템 셸 명령어(exec, system)를 직접 호출하는 방식 대신 언어 자체에서 제공하는 안전한 라이브러리 API(예: 파일 복사는 FileCopy API)를 사용한다.\n2. 셸 호출이 불가피한 경우 세미콜론(;), 파이프(|), 백틱(`), 앰퍼샌드(&) 등 명령어 체이닝 문자를 철저히 필터링하고 화이트리스트 명령 인자만 허용한다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q25",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "'chattr +i 파일명'을 적용하면 파일에 불변 속성이 부여되어 백도어 침투나 로그 삭제를 방지할 수 있습니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q25",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "개인정보처리자는 개인정보처리시스템의 접속기록에 대해 월 1회 이상 정기적으로 불법 접근, 다운로드, 열람 등 이상 징후를 점검·확인하여야 합니다.",
      "subject": "실무 보안",
      "type": "essay"
    },
    {
      "id": "prac_q25",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[정답: Never Trust, Always Verify]\n경계선 보안 모델을 탈피하여 모든 사용자, 기기, 세션을 잠재적 위협으로 간주하고 세분화된 인증·인가 및 지속적 모니터링을 수행하는 제로 트러스트의 대원칙입니다.",
      "subject": "실무 보안",
      "type": "short"
    },
    {
      "id": "prac_q25",
      "prompt": "",
      "choices": [],
      "answer": "1",
      "explanation": "[실무 모범답안]\n1. 최상위 루트 계정은 일상 업무에 사용하지 않고 잠금 및 강력한 하드웨어 MFA를 적용한다.\n2. 장기 액세스 키(Access Key) 대신 임시 자격증명을 제공하는 IAM Role(역할)을 사용한다.\n3. 와일드카드(Action: \"*\") 권한을 금지하고 실제 수행할 작업에만 국한된 최소 권한 정책(Least Privilege Policy)을 부여한다.",
      "subject": "실무 보안",
      "type": "essay"
    }
  ],
  "summaries": [
    {
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "content",
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
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] find (-perm -4000)",
      "badge": "단답형 족보",
      "points": [
        "SetUID가 설정된 실행 바이너리를 전수 검색하여 권한 상승 취약점을 탐지하는 리눅스 명령어."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] netstat (-antp)",
      "badge": "단답형 족보",
      "points": [
        "활성 TCP/UDP 네트워크 소켓, 수신 포트, PID 및 프로세스명을 조회하는 핵심 포트 점검 명령어."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] umask (027)",
      "badge": "단답형 족보",
      "points": [
        "신규 파일 생성 시 640(-rw-r-----), 디렉토리 생성 시 750(drwxr-x---) 권한을 강제 부여하는 마스크값."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] chattr (+i / -i)",
      "badge": "단답형 족보",
      "points": [
        "root 사용자라도 파일을 삭제, 수정, 이름 변경할 수 없도록 속성을 불변(Immutable) 상태로 잠그는 명령어."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] lastlog (/var/log/lastlog)",
      "badge": "단답형 족보",
      "points": [
        "시스템 내 모든 사용자의 최근 로그인 일시와 출발지 IP를 확인하는 바이너리 로그 조회 명령어."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] tcpdump",
      "badge": "단답형 족보",
      "points": [
        "네트워크 인터페이스(eth0 등)를 통과하는 패킷의 헤더와 페이로드를 실시간 캡처 및 필터링하는 도구."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] icacls",
      "badge": "단답형 족보",
      "points": [
        "윈도우 NTFS 파일 시스템에서 파일 및 폴더의 접근 제어 목록(ACL) 권한을 명령줄에서 확인·수정하는 도구."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] distance (Snort)",
      "badge": "단답형 족보",
      "points": [
        "직전 content 패턴 매칭 끝 지점으로부터 다음 패턴을 탐색할 상대적 시작 거리를 바이트 단위로 지정하는 Snort 옵션."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] within (Snort)",
      "badge": "단답형 족보",
      "points": [
        "distance 지점부터 최대 몇 바이트 범위 안에서 다음 패턴을 찾아야 하는지 탐색 범위를 한정하는 Snort 옵션."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] iptables REJECT",
      "badge": "단답형 족보",
      "points": [
        "접속 패킷을 차단할 때 송신자에게 ICMP unreachable 또는 TCP RST 거부 응답을 명시적으로 회신하는 타겟."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] PreparedStatement",
      "badge": "단답형 족보",
      "points": [
        "SQL 쿼리를 사전 컴파일하고 입력값을 파라미터로 안전하게 바인딩하여 SQL Injection을 원천 차단하는 인터페이스."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] SameSite=Lax",
      "badge": "단답형 족보",
      "points": [
        "타 사이트에서의 안전한 GET 최상위 링크 이동만 허용하고, 외부 POST 등 비인가 요청에서 쿠키 전송을 막는 CSRF 방어 속성."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] Strict-Transport-Security (HSTS)",
      "badge": "단답형 족보",
      "points": [
        "웹 브라우저가 평문 HTTP 연결을 일절 시도하지 않고 오직 HTTPS로만 통신하도록 강제하는 보안 헤더."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] Content-Security-Policy (CSP)",
      "badge": "단답형 족보",
      "points": [
        "브라우저에서 실행 가능한 스크립트, 스타일, 이미지 등의 신뢰 출처를 지정하여 XSS 공격을 방어하는 보안 헤더."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (포렌식)",
      "title": "[실기 단답] Volatility",
      "badge": "단답형 족보",
      "points": [
        "물리 RAM 메모리 덤프 파일을 파싱하여 프로세스 트리, 네트워크 소켓, 셸코드 등을 역공학 분석하는 메모리 포렌식 도구."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (보안관리)",
      "title": "[실기 단답] SBOM",
      "badge": "단답형 족보",
      "points": [
        "소프트웨어 공급망 보안을 위해 오픈소스 라이브러리, 패키지 버전, 의존성 관계를 기계 판독 가능하게 작성한 소프트웨어 자재 명세서."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (보안관제)",
      "title": "[실기 단답] SOAR",
      "badge": "단답형 족보",
      "points": [
        "보안 솔루션 경보를 통합하고 사전 정의된 플레이북(Playbook)에 따라 침해 대응 프로세스를 자동 오케스트레이션하는 관제 기술."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] EDR",
      "badge": "단답형 족보",
      "points": [
        "단말기(엔드포인트)의 프로세스 생성, 파일 변경, 네트워크 연결 행위를 실시간 모니터링하여 침해를 탐지·격리하는 솔루션."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (네트워크)",
      "title": "[실기 단답] SPAN (Port Mirroring)",
      "badge": "단답형 족보",
      "points": [
        "스위치 포트나 VLAN의 패킷을 네트워크 분석 장비(IDS, Wireshark)가 연결된 특정 모니터링 포트로 복제하는 기능."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (보안관리)",
      "title": "[실기 단답] MITRE ATT&CK",
      "badge": "단답형 족보",
      "points": [
        "실제 사이버 공격자의 공격 전술(Tactics), 기술(Techniques), 절차(Procedures)를 매트릭스로 집대성한 지식 프레임워크."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (암호학)",
      "title": "[실기 단답] Perfect Forward Secrecy (PFS)",
      "badge": "단답형 족보",
      "points": [
        "서버의 장기 개인키가 유출되더라도 일회성 임시 세션키 폐기를 통해 과거 암호화 통신의 복호화를 방지하는 암호학적 특성."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] auditctl",
      "badge": "단답형 족보",
      "points": [
        "리눅스 커널 감사 서브시스템(auditd)에 특정 시스템 콜이나 중요 파일(/etc/passwd) 감시 규칙을 실시간 등록하는 도구."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] fail2ban",
      "badge": "단답형 족보",
      "points": [
        "SSH 등에서 일정 횟수 이상 인증 실패 로그가 기록되면 방화벽(iptables)에 차단 룰을 동적으로 생성하여 무차별 대입을 막는 도구."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] SecureRandom",
      "badge": "단답형 족보",
      "points": [
        "선형 합동(LCG) 대신 암호학적으로 안전한 난수를 생성하여 예측 불가능한 세션 ID 및 솔트(Salt)를 발급하는 자바 클래스."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (포렌식)",
      "title": "[실기 단답] Chain of Custody (연계보관성)",
      "badge": "단답형 족보",
      "points": [
        "디지털 증거가 압수된 순간부터 법정 제출 시까지 취급자, 보관 장소, 일시를 연속적으로 기록 증명하는 포렌식 기본 원칙."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (웹/앱)",
      "title": "[실기 단답] Open Redirect",
      "badge": "단답형 족보",
      "points": [
        "사용자 입력 URL을 검증 없이 HTTP 302 리다이렉트 대상으로 사용하여 악성 피싱 사이트로 연결시키는 웹 취약점."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (시스템)",
      "title": "[실기 단답] Tripwire",
      "badge": "단답형 족보",
      "points": [
        "시스템 바이너리 및 설정 파일의 기준 해시값(SHA-256)을 저장해 두고 변경 여부를 감시하여 악성 변조를 탐지하는 HIDS 도구."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (포렌식)",
      "title": "[실기 단답] Order of Volatility",
      "badge": "단답형 족보",
      "points": [
        "디지털 증거 수집 시 휘발성이 높은 순서(레지스터/캐시 -> RAM -> 네트워크 연결 -> 디스크)대로 수집해야 한다는 원칙."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (법률)",
      "title": "[실기 단답] CISO 겸직금지",
      "badge": "단답형 족보",
      "points": [
        "자산 5조 원 이상 또는 자산 5천억 이상 ISMS 의무 대상 기업의 CISO는 정보기술(CIO) 등 타 임원 직무를 겸직할 수 없도록 한 규정."
      ]
    },
    {
      "type": "term",
      "category_name": "실기 단답형 용어 (보안관리)",
      "title": "[실기 단답] Zero Trust (Never Trust, Always Verify)",
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
      "id": "ismsp_q1",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "ISMS-P 1.1.2 및 망법에 따라 일정 규모 이상 기업의 CISO는 회사의 다른 IT 부문 업무(CIO, 개발본부장 등)를 겸직할 수 없습니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q1",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 1.4.2(관리체계 점검)에 따라 내부감사원은 피감사 조직(부서)과 독립된 인력으로 구성되어 객관적이고 독립적인 감사를 수행해야 합니다. CISO가 주관한 자가 감사는 독립성 결여로 명백한 결함입니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q2",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "1.2.2 기준에 따라 조직의 환경을 고려하여 경영진이 승인한 DOA(Degree of Acceptance) 기준을 수립하고 이를 초과하는 위험에 대해 대책을 마련해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q2",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.2.3(퇴직 및 직무변경)에 따라 직원의 퇴직 또는 부서 이동 등 직무 변경 발생 시 즉시 권한을 회수하거나 변경된 직무에 맞게 최소 권한으로 재조정하여야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q3",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "1.1.4 기준은 인증 범위 내의 모든 정보자산, 서비스, 네트워크, 개인정보 처리 흐름도를 누락 없이 식별하여 관리체계 범위로 설정하도록 요구합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q3",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.5.4(비밀번호 관리)에 따라 초기 임시 비밀번호는 안전하게 발급되어야 하며, 시스템 접속 시 즉시 본인의 비밀번호로 변경하도록 기술적으로 강제해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q4",
      "prompt": "",
      "choices": [],
      "answer": 3,
      "explanation": "안전성 확보조치 기준 제8조에 따라 5만명 이상의 민감정보 또는 고유식별정보 처리 시스템은 접속기록을 2년 이상 보관하고 월 1회 이상 점검해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q4",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.6.2(개발·운영 시스템 분리)에 따라 개발망과 운영망은 원칙적으로 분리되어야 하며, 개발자가 운영 DB에 직접 접속하는 것은 엄격히 금지되고 승인된 절차와 결재를 통해서만 접근해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q5",
      "prompt": "",
      "choices": [],
      "answer": 2,
      "explanation": "2.5.4 기준에 따라 초기 비밀번호는 최초 접속 시 반드시 변경하도록 강제 통제해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q5",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.8.5(시험 데이터 보안)에 따라 정보시스템 개발 및 테스트 시 실제 운영 개인정보의 사용은 원칙적으로 금지되며, 불가피한 경우 책임자 승인 하에 가명·익명 처리 또는 더미 데이터를 생성하여 사용해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q6",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "2.8.5(시험 데이터 보안) 기준에 따라 시스템 개발, 테스트 시 원칙적으로 실제 개인정보 사용이 금지되며, 부득이한 경우 가명·익명화 처리를 해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q6",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.4.1(출입통제)에 따라 전산실 등 통제구역에 외부인이 출입할 때에는 반드시 사전 승인을 거치고 출입 대장을 기록하며 보안담당자가 입회·동행하여야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q7",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "2.2.3(퇴직 및 직무변경) 기준에 따라 퇴직 시 정보자산 반납 및 모든 접근 권한의 즉시 회수/비활성화가 이루어져야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q7",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.10.1(보안시스템 운영/취약점 점검 및 조치)에 따라 취약점이 공지되거나 점검에서 식별된 경우 보안패치를 신속히 적용하거나 WAF 룰셋 등 대체 완화 대책을 마련해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q8",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "2.7.1(암호정책 적용) 기준에 따라 고유식별정보와 비밀번호(일방향 해시)는 저장 시 반드시 안전한 알고리즘으로 암호화하여야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q8",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.6.4(원격접근 통제)에 따라 사외에서 사내망으로 원격 접속(VPN 등) 시에는 안전한 인증 수단(OTP, 보안토큰 등 다중인증 MFA)과 전송구간 암호화가 의무적으로 적용되어야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q9",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "3.1.2 기준에 따라 선택항목 미제공을 이유로 기본 서비스 제공을 거부할 수 없습니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q9",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.9.3(백업 및 복구 관리)에 따라 백업 매체의 정상 작동 여부와 데이터 복구 가능성을 검증하기 위해 연 1회 이상 정기적으로 실제 복구 훈련을 실시하고 그 결과를 기록해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q10",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "3.4.1 기준에 따라 보유기간 경과 또는 처리 목적 달성 시 지체 없이(5일 이내) 복구 불가능한 방법으로 영구 파기해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q10",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 2.6.7 및 개인정보 안전성 확보조치 기준에 따라 5만 명 이상의 고유식별정보 또는 민감정보를 처리하는 시스템의 접속기록은 최소 2년 이상 보관·관리해야 하므로 결함입니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q11",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "3.3.2 기준에 따라 위탁 계약 시 법정 필수사항(목적, 재위탁 제한, 안전조치)을 문서화하고 연 1회 이상 수탁사의 처리 실태를 정기 점검해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q11",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 3.1.2 및 개인정보 보호법 제16조에 따라 정보주체가 선택항목에 동의하지 않는다는 이유로 기본 서비스의 제공을 거부할 수 없으므로 명백한 법적 결함입니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q12",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "3.5.1 기준에 따라 정보주체의 열람, 정정, 삭제 요구에 대해 10일 이내에 조치 결과를 회신하여야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q12",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 3.3.2(업무 위탁)에 따라 위탁자는 수탁사가 개인정보를 안전하게 처리하고 있는지 주기적으로(연 1회 이상) 관리·감독하고 실태 점검 결과를 문서화하여 보관해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q13",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "2.6.7 기준에 따라 접속기록은 위·변조 및 도난, 분실되지 않도록 안전한 별도 저장소에 백업 보관하고 접근 권한을 최소화하여야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q13",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 3.4.1(개인정보의 파기)에 따라 보유기간 경과나 탈퇴 등 처리 목적이 달성된 개인정보는 정당한 사유가 없는 한 지체 없이(5일 이내) 영구 파기해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q14",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "2.4.1(출입통제) 기준에 따라 통제구역에 대한 출입기록은 최소 1년(또는 3년) 이상 보관하고 정기적으로 검토하여야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q14",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 3.5.2 및 개정 개인정보 보호법에 따라 유출 사실을 안 때에는 정당한 사유가 없는 한 72시간 이내에 전문기관(보호위/KISA)에 신고해야 하므로 기한 초과 결함입니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q15",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "3.2.1(개인정보 현황 관리) 기준에 따라 개인정보 처리방침 및 내부 관리대장과 실제 시스템에서 수집·이용되는 개인정보 항목은 100% 일치해야 합니다.",
      "subject": "인증기준 결함판정"
    },
    {
      "id": "ismsp_q15",
      "prompt": "",
      "choices": [],
      "answer": 1,
      "explanation": "ISMS-P 3.4.2(개인정보의 분리보관)에 따라 타 법령에 의해 보존해야 하는 개인정보는 운영 중인 다른 개인정보와 물리적 또는 논리적으로 완전히 분리된 별도 저장소(DB)에 격리 보관하고 접근을 엄격히 통제해야 합니다.",
      "subject": "인증기준 결함판정"
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

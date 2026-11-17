# -*- coding: utf-8 -*-
"""
summary_notes_ext.py
2026 이기적 정보보안기사 필기+실기 올인원 편제 기준
- 내용별 심층 정리 추가분 15선 (기존 35선 -> 총 50선)
- 각 카드 6~9개 고밀도 불릿: 명령어/옵션, 포트, 수치, 공격 vs 방어 비교
"""


def get_extra_written_content():
    items = []

    # =========================================================================
    # 시스템 보안 (+4)
    # =========================================================================
    items.append({
        "id": "sys_content_08",
        "type": "content",
        "category": "system",
        "category_name": "시스템 보안",
        "title": "윈도우 레지스트리 구조·로컬 보안 정책·계정 잠금 정책",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>레지스트리 5대 루트 키:</strong> HKLM(시스템 전역 정책), HKCU(현재 사용자 프로필), HKCR(파일 확장자 연결), HKU(모든 사용자), HKCC(하드웨어 임시 정보). 실체 파일은 <code>%SystemRoot%\\System32\\config</code>의 SAM·SECURITY·SOFTWARE·SYSTEM 하이브이며, 관리자도 실행 중에는 직접 편집할 수 없고 <code>regedit</code>의 하이브 로드 또는 <code>reg save</code>로만 추출된다.",
            "<strong>악성코드가 즐겨 쓰는 자동실행 키:</strong> <code>HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run</code>, <code>RunOnce</code>, <code>Winlogon\\Userinit</code>, <code>Image File Execution Options</code>(디버거 하이재킹). 서비스 등록은 <code>HKLM\\SYSTEM\\CurrentControlSet\\Services</code>에서 이루어지므로 점검 대상 1순위.",
            "<strong>계정 정책(secpol.msc → 보안 설정 → 계정 정책):</strong> 암호 최소 길이 8자 이상, 암호 복잡성 사용, 최대 사용 기간 90일(또는 60일), 최근 암호 기억 24개, 최소 사용 기간 1일. KISA 서버 취약점 점검 기준과 동일한 수치.",
            "<strong>계정 잠금 정책:</strong> 잠금 임계값 5회 이하, 잠금 기간 30분 이상, 잠금 카운터 재설정 30분 이상. 임계값을 1~2회로 과도하게 낮추면 타인이 계정을 고의로 잠그는 <strong>계정 잠금 DoS</strong>에 노출되므로 5회 전후가 표준.",
            "<strong>감사 정책(auditpol):</strong> 로그온 감사 성공 4624 / 실패 4625, 명시적 자격증명 4648(원격 실행 정황), 특수 권한 할당 4672, 계정 생성 4720·삭제 4726, 그룹 추가 4732, 감사 로그 삭제 1102. <code>auditpol /get /category:*</code>로 현재 설정 전수 확인, <code>secedit /export /cfg policy.inf</code>로 정책 백업.",
            "<strong>위험 레지스트리 설정:</strong> 자동 로그온 <code>Winlogon\\DefaultPassword</code> 평문 저장, <code>AlwaysInstallElevated=1</code>(일반 사용자도 MSI 설치 시 SYSTEM 권한 → 권한 상승), 익명 SID 변환 허용 <code>RestrictAnonymous=0</code>, SMB 서명 미사용 <code>RequireSecuritySignature=0</code>.",
            "<strong>권한 모델:</strong> 공유 권한(최대 Full Control)과 NTFS ACL(17개 세부 권한) 중 <strong>더 제한적인 쪽이 최종 적용</strong>. 상속 차단 후 <code>icacls</code>로 명시 ACE 부여, <code>Everyone</code>·<code>Users</code>의 쓰기 권한은 제거 원칙."
        ]
    })

    items.append({
        "id": "sys_content_09",
        "type": "content",
        "category": "system",
        "category_name": "시스템 보안",
        "title": "리눅스 강제접근통제(SELinux·AppArmor)와 샌드박스 격리",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>DAC vs MAC:</strong> DAC(파일 소유자·권한 비트)는 root가 모든 통제를 우회할 수 있다는 한계가 있어, 커널이 정책으로 판단하는 MAC을 병행한다. root도 SELinux 정책을 위반하면 <strong>Permission denied</strong>가 발생한다.",
            "<strong>SELinux 3모드:</strong> <code>enforcing</code>(위반 차단+로그), <code>permissive</code>(차단 없이 로그만, 정책 개발용), <code>disabled</code>(커널 기능 자체 미동작). 확인 <code>getenforce</code>, 임시 전환 <code>setenforce 0</code>, 영구 설정 <code>/etc/selinux/config</code>의 <code>SELINUX=</code>.",
            "<strong>보안 컨텍스트 4요소:</strong> <code>user:role:type:level</code> (예: system_u:object_r:httpd_sys_content_t:s0). 실무에서 실제 판단 기준은 <strong>type</strong>이며, <code>ls -Z</code>로 확인, <code>chcon -t</code>로 임시 변경, <code>semanage fcontext -a -t</code> + <code>restorecon -Rv</code>로 영구 규칙 적용.",
            "<strong>정책 유형:</strong> targeted(기본, 네트워크 데몬만 제한), minimum(최소), mls(군사용 다중등급). 부울 설정은 <code>getsebool -a</code>, <code>setsebool -P httpd_can_network_connect on</code>(-P는 재부팅 후 유지).",
            "<strong>거부 로그 추적:</strong> <code>/var/log/audit/audit.log</code>의 AVC denied 메시지를 <code>ausearch -m avc -ts recent</code>, <code>sealert -a</code>로 분석. 웹 루트에 파일을 옮긴 뒤 403이 뜨는 전형적 원인이 컨텍스트 불일치다.",
            "<strong>AppArmor:</strong> 경로 기반 프로파일(<code>/etc/apparmor.d/</code>)로 SELinux보다 문법이 단순. <code>aa-status</code>(적용 현황), <code>aa-enforce</code>/<code>aa-complain</code>(모드 전환), <code>aa-genprof</code>(프로파일 생성).",
            "<strong>샌드박스 격리 기법:</strong> <code>chroot</code>(루트 디렉터리 변경, 단 root 권한 프로세스는 탈출 가능), namespace(pid·net·mnt·user 격리)+cgroup(자원 제한) 조합이 컨테이너의 기반, seccomp로 시스템 콜 화이트리스트 적용, <code>systemd</code>의 PrivateTmp·ProtectSystem 지시자.",
            "<strong>마운트 옵션 강화:</strong> <code>/etc/fstab</code>에 <code>nosuid</code>(SetUID 무시), <code>noexec</code>(실행 차단), <code>nodev</code>(장치 파일 무시), <code>ro</code>. /tmp·/var/tmp·/home을 별도 파티션으로 분리하고 nosuid·noexec를 적용하는 것이 KISA 권고."
        ]
    })

    items.append({
        "id": "sys_content_10",
        "type": "content",
        "category": "system",
        "category_name": "시스템 보안",
        "title": "악성코드 7대 유형·감염 경로·탐지 기법과 랜섬웨어 대응",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>바이러스 vs 웜:</strong> 바이러스는 숙주 파일·부트섹터·매크로에 기생해 사용자 실행 시 전파, 웜은 숙주 없이 스스로 네트워크를 통해 전파. 대표 웜: 슬래머(SQL Server 1434/UDP), 블래스터(RPC 135), 코드레드(IIS 80), 님다(다중 벡터).",
            "<strong>트로이목마·백도어:</strong> 정상 프로그램으로 위장해 설치되며 원격 제어(백도어), 정보 유출, 추가 악성코드 다운로드 기능. 서버형(RAT)·클라이언트형·프락시형으로 분류.",
            "<strong>랜섬웨어:</strong> 파일을 암호화한 뒤 복호화 대가를 요구. 워너크라이(2017, SMB 445/MS17-010 이터널블루)처럼 취약점으로 자체 전파하는 웜형, 최근에는 <strong>이중 갈취</strong>(암호화 + 탈취 데이터 공개 협박)와 서비스형(RaaS) 모델이 표준.",
            "<strong>그 외 유형:</strong> 루트킷(커널 LKM·부트킷으로 프로세스·파일·포트 은닉), 스파이웨어·키로거, 애드웨어, 논리폭탄(특정 날짜·조건 트리거), 봇(좀비)·다운로더, 파일리스 악성코드(PowerShell·WMI·레지스트리 상주).",
            "<strong>감염 경로:</strong> 악성 첨부·URL 메일(피싱), 웹 드라이브바이 다운로드, 공급망(정품 업데이트·오픈소스 패키지), P2P·불법 SW, USB 자동실행(autorun.inf), 원격접속 취약 계정(RDP 3389 무차별 대입).",
            "<strong>탐지 3계열:</strong> 시그니처(알려진 해시·패턴, 오탐 낮고 신종 미탐), 휴리스틱·행위기반(API 호출·파일 암호화 대량 발생 등 행위 판단), 샌드박스(가상 환경 실행 관찰). EDR은 프로세스 계보·네트워크 연결·레지스트리 변경을 상시 수집해 탐지·차단·롤백을 수행.",
            "<strong>랜섬웨어 대응:</strong> ① 네트워크 즉시 격리 ② 감염 단말 전원 유지(메모리 증거 보존) 및 이미지 백업 ③ <code>3-2-1 백업</code>(사본 3, 매체 2, 오프라인 1) 확인 후 복구 ④ 복구 전 백업 무결성·랜섬웨어 잔존 검사 ⑤ 복호화 도구 배포 여부 확인 후 신고(KISA 118).",
            "<strong>사후 조치:</strong> 침입 경로(IOC) 분석 → 취약점 패치 → 계정·권한 재설정 → 재발방지 대책 문서화. 백업은 반드시 <strong>복구 모의훈련</strong>까지 수행해야 실효가 있다."
        ]
    })

    items.append({
        "id": "sys_content_11",
        "type": "content",
        "category": "system",
        "category_name": "시스템 보안",
        "title": "가상화·클라우드·컨테이너 보안과 책임분담모델",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>가상화 위협:</strong> 하이퍼바이저 취약점을 악용한 <strong>VM 이스케이프</strong>(게스트 → 호스트 권한 획득), VM 스프롤(방치된 가상머신), 스냅샷·템플릿 이미지에 남은 계정·키, 가상 스위치 트래픽 도청.",
            "<strong>클라우드 책임분담모델:</strong> IaaS는 고객이 OS·미들웨어·애플리케이션·데이터까지, PaaS는 애플리케이션·데이터, SaaS는 데이터·계정·권한을 책임진다. 물리·네트워크·하이퍼바이저는 사업자 책임 — 경계를 오해하면 <strong>설정 오류</strong>가 곧 유출 사고가 된다.",
            "<strong>대표 클라우드 사고 원인:</strong> 공용 스토리지(S3 버킷) 공개 설정, 과도한 IAM 권한(<code>*:*</code>), 액세스 키 하드코딩, 메타데이터 서비스(169.254.169.254) SSRF 악용, 보안그룹 0.0.0.0/0 허용, 로그 미수집.",
            "<strong>컨테이너 격리:</strong> 리눅스 namespace(프로세스·네트워크·마운트·사용자) + cgroup(CPU·메모리)로 격리하며 VM보다 격리 강도가 약하다. root로 실행되는 컨테이너, <code>--privileged</code>, 호스트 디렉터리 마운트는 탈출 위험.",
            "<strong>이미지·파이프라인 보안:</strong> 공식 이미지 사용 및 digest 고정, 취약 패키지 스캔(Trivy·Grype), 최소 베이스 이미지(distroless), 이미지 서명·검증, CI/CD 시크릿 분리, IaC 스캔(Terraform <code>tfsec</code>).",
            "<strong>쿠버네티스 설정:</strong> RBAC 최소 권한(ClusterRole 광범위 부여 금지), NetworkPolicy로 네임스페이스 간 통신 차단, Secret은 etcd 암호화 및 외부 KMS 연동, <code>kubelet</code> 익명 인증 비활성, CIS Benchmark 점검.",
            "<strong>점검 도구·기준:</strong> CSPM(설정 오류 상시 점검), CWPP(워크로드 보호), CIS Benchmark, CSA CCM. 국내는 클라우드 보안인증(CSAP)과 ISMS-P의 가상화·클라우드 기준을 함께 본다."
        ]
    })

    # =========================================================================
    # 네트워크 보안 (+3)
    # =========================================================================
    items.append({
        "id": "net_content_09",
        "type": "content",
        "category": "network",
        "category_name": "네트워크 보안",
        "title": "ARP 스푸핑·DNS 캐시 포이즈닝 등 스푸핑/스니핑 공격과 대응",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>ARP 동작 원리:</strong> 요청은 브로드캐스트, 응답은 유니캐스트이며 <strong>응답을 받지 않은 상태에서도 갱신</strong>(무상태)한다. 이 구조적 결함이 ARP 스푸핑의 근본 원인이다.",
            "<strong>ARP 스푸핑:</strong> 게이트웨이 IP에 공격자 MAC을 매핑한 위조 ARP Reply를 지속 송신해 피해자 트래픽을 자신을 경유시킨다(MITM). 이후 스니핑·세션 하이재킹·SSL Stripping으로 확장된다.",
            "<strong>탐지·대응:</strong> <code>arp -a</code>에서 동일 MAC이 서로 다른 IP에 매핑되는지 확인, <code>arpwatch</code>·XArp 경보, 정적 ARP 등록(<code>arp -s</code>), 스위치의 <strong>DAI(Dynamic ARP Inspection)</strong> + DHCP Snooping 신뢰 포트 설정, 포트 보안(sticky MAC), 중요 구간 암호화(IPSec·TLS).",
            "<strong>DNS 캐시 포이즈닝:</strong> 재귀 질의의 TXID(16bit)와 소스 포트를 추측해 위조 응답을 먼저 주입, 캐시를 오염시켜 다수 사용자를 악성 사이트로 유도(Kaminsky 공격, 2008).",
            "<strong>DNS 대응:</strong> DNSSEC(응답 서명·무결성 검증), 무작위 소스 포트·TXID, 0x20 인코딩(질의 이름 대소문자 무작위화), 응답률 제한(RRL), 외부·내부 DNS 분리, 재귀 질의 제한(<code>allow-recursion</code>), DNS over HTTPS/TLS.",
            "<strong>DNS 악용 공격:</strong> DNS 터널링(iodine·dnscat2, TXT·NULL 레코드로 데이터 은닉), DNS 증폭·반사(ANY·DNSSEC 레코드, 53/UDP 스푸핑), Fast Flux·DGA(도메인 자동 생성으로 C&C 은닉), 타이포스쿼팅.",
            "<strong>스니핑:</strong> NIC를 무차별(Promiscuous) 모드로 전환해 동일 세그먼트 패킷을 도청. 허브 환경에서는 즉시 가능하지만 스위치 환경에서는 <strong>MAC 플러딩이나 ARP 스푸핑이 선행</strong>되어야 한다. 대응은 스위치 포트 미러링 통제, 암호화 통신(SSH·TLS·IPSec), 스니핑 탐지 도구(ARPWatch·Snort 룰).",
            "<strong>스푸핑 계열 정리:</strong> IP 스푸핑(반사·증폭 공격, TCP는 3-way 핸드셰이크 때문에 세션 탈취 불가), MAC 스푸핑, 이메일 스푸핑(SPF·DKIM·DMARC로 대응), 웹 스푸핑(클릭재킹)."
        ]
    })

    items.append({
        "id": "net_content_10",
        "type": "content",
        "category": "network",
        "category_name": "네트워크 보안",
        "title": "라우팅 프로토콜 보안(BGP·OSPF)과 L2 스위치 보안",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>OSPF 기본:</strong> 링크상태 라우팅, Hello 패킷 224.0.0.5(DR/BDR은 224.0.0.6), Area 0이 백본이며 타 Area는 반드시 Area 0 경유. 관리거리 110, 프로토콜 번호 89.",
            "<strong>OSPF 보안:</strong> <code>area 0 authentication message-digest</code>로 MD5/SHA 인증(평문 인증은 스니핑에 취약), <code>passive-interface</code>로 사용자 구간 광고 차단, 라우터 ID 고정, 인접 라우터에만 Update 허용, 필요 시 가상링크 최소화.",
            "<strong>BGP 위협:</strong> TCP 179 기반, AS-PATH로 최적 경로를 판단하므로 <strong>위조 AS-PATH를 앞세운 경로 하이재킹</strong>, 상위 ISP로 사설 경로를 누출하는 route leak, 세션 재설정 유발 DoS가 대표적.",
            "<strong>BGP 보안:</strong> RPKI(ROA로 발신 AS·prefix 검증) + ROV, prefix-list·filter-list, 최대 prefix 수 제한(<code>maximum-prefix</code>), TTL Security(GTSM, 255 고정), TCP MD5, <code>bgp dampening</code>으로 플래핑 억제.",
            "<strong>L2 위협 1 — MAC 플러딩:</strong> 위조 출발 MAC을 대량 학습시켜 CAM 테이블을 포화시킨다. 스위치가 미지 목적지 패킷을 모든 포트로 <strong>플러딩(hub처럼 동작)</strong>해 스니핑이 가능해진다. 대응: <code>switchport port-security maximum 3</code>, <code>violation shutdown</code>.",
            "<strong>L2 위협 2 — VLAN 호핑:</strong> 스위치 간 링크를 trunk로 협상시키는 Switch Spoofing(DTP), 이중 802.1Q 태그를 붙이는 Double Tagging으로 다른 VLAN에 접근. 대응: 미사용 포트 <code>switchport mode access</code>, <code>switchport nonegotiate</code>, native VLAN을 사용하지 않는 ID로 변경.",
            "<strong>L2 위협 3 — STP 루트 하이재킹:</strong> 우선순위가 낮은(0) BPDU를 위조 송신해 자신을 루트 브리지로 선출시키고 전 트래픽을 경유시킨다. 대응: <code>spanning-tree bpduguard enable</code>(사용자 포트 BPDU 수신 시 차단), <code>root guard</code>(상위 포트의 우수 BPDU 차단).",
            "<strong>기타 L2 통제:</strong> DHCP Snooping(위조 DHCP 서버 차단), IP Source Guard(출발지 IP·MAC 검증), ARP Inspection, 802.1X 포트 인증, NAC로 미등록 단말 격리."
        ]
    })

    items.append({
        "id": "net_content_11",
        "type": "content",
        "category": "network",
        "category_name": "네트워크 보안",
        "title": "무선랜 인증 체계(802.1X·EAP·RADIUS)와 무선 침해 대응",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>무선 3대 구성요소:</strong> STA(단말) — AP(인증자/Authenticator) — <strong>RADIUS(인증서버, UDP 1812 인증/1813 과금)</strong>. 802.1X는 이 3자 구조로 포트 기반 인증을 수행하며, 인증 전에는 EAPOL 트래픽 외 차단(Controlled Port).",
            "<strong>EAP 프로토콜 비교:</strong> EAP-MD5(단방향·해시만, 취약), LEAP(시스코 독자, MS-CHAPv2 사전공격에 취약), <strong>EAP-TLS(서버·클라이언트 상호 인증서, 가장 강력하나 인증서 배포 부담)</strong>, PEAP(서버 인증서로 TLS 터널을 만든 뒤 내부 MS-CHAPv2 인증), EAP-TTLS(터널 내 다양한 레거시 인증 허용).",
            "<strong>WPA2 4-Way Handshake:</strong> PSK(또는 802.1X 결과)인 PMK로 ANonce·SNonce·MAC 주소를 섞어 PTK를 유도하고, 마지막에 GTK를 전달·MIC 검증. <strong>KRACK(2017)</strong>은 이 핸드셰이크의 키 재설치 취약점으로 패치가 필요하다.",
            "<strong>WPA3:</strong> SAE(Dragonfly)로 오프라인 사전공격을 무력화하고, 개방형 망에서도 OWE로 암호화, 192bit Suite-B(Enterprise) 지원, 관리프레임 보호(802.11w) 기본 적용.",
            "<strong>무선 침해 유형:</strong> War Driving(대역 스캔), Evil Twin(동일 SSID 위장 AP로 피싱), Rogue AP(내부에 무단 설치), <strong>Deauth Flood</strong>(관리프레임 위조로 연결 강제 종료 후 가짜 AP 유도), WPS PIN 무차별 대입, PMKID 캡처를 통한 오프라인 크래킹.",
            "<strong>무선 대응:</strong> WPA3 또는 WPA2-AES(CCMP) 강제, TKIP·WEP 비활성, WPS OFF, RADIUS 기반 EAP-TLS/PEAP, <strong>WIPS</strong>로 비인가 AP·Deauth 공격 탐지, 802.11w 관리프레임 보호, SSID 은닉은 보안 대책이 아님(스캔으로 쉽게 노출).",
            "<strong>게스트망 분리:</strong> 사내망과 VLAN·정책을 분리하고, 캡티브 포털은 인증 우회 취약점에 주의하며, IoT 구간은 별도 SSID·별도 VLAN으로 격리한다."
        ]
    })

    # =========================================================================
    # 애플리케이션 보안 (+3)
    # =========================================================================
    items.append({
        "id": "app_content_08",
        "type": "content",
        "category": "app",
        "category_name": "애플리케이션 보안",
        "title": "XXE(XML 외부 엔티티) 공격 원리와 파서별 방어 설정",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>원리:</strong> XML 파서가 DOCTYPE 내부의 외부 엔티티(SYSTEM) 선언을 처리하는 기능을 악용한다. <code>&lt;!DOCTYPE foo [&lt;!ENTITY xxe SYSTEM \"file:///etc/passwd\"&gt;]&gt;&lt;foo&gt;&amp;xxe;&lt;/foo&gt;</code>처럼 선언 후 참조하면 응답에 파일 내용이 반영된다.",
            "<strong>3대 영향:</strong> ① 로컬 파일 읽기(설정·키·계정 파일) ② <strong>SSRF</strong>(<code>http://169.254.169.254/</code> 클라우드 메타데이터 조회, 내부망 스캔) ③ Billion Laughs(엔티티 재귀 확장으로 메모리 고갈 → DoS).",
            "<strong>블라인드 XXE(OOB):</strong> 응답에 결과가 보이지 않을 때 외부 DTD를 공격자 서버에 두고 <code>%</code> 파라미터 엔티티로 파일 내용을 아웃오브밴드 채널로 전송한다. <code>ftp</code>/<code>http</code> 스킴과 DNS 질의가 유출 경로로 쓰인다.",
            "<strong>Java 방어:</strong> <code>DocumentBuilderFactory</code>에 <code>setFeature(\"http://apache.org/xml/features/disallow-doctype-decl\", true)</code>, <code>external-general-entities</code>/<code>external-parameter-entities</code> false, <code>XMLConstants.FEATURE_SECURE_PROCESSING</code> true. JAXB·SOAP 라이브러리도 동일 설정 필요.",
            "<strong>언어별 방어:</strong> PHP는 libxml2 2.9 이상에서 <code>libxml_disable_entity_loader(true)</code>(PHP 8부터 기본 비활성), .NET은 <code>XmlReaderSettings.DtdProcessing = Prohibit</code>·<code>XmlResolver = null</code>, Python은 <code>defusedxml</code> 또는 lxml <code>resolve_entities=False</code>.",
            "<strong>근본 대책:</strong> XML 대신 JSON 사용, DTD·외부 스키마 참조 금지, XSD 기반 화이트리스트 검증, 파서 라이브러리 최신화. WAF는 인코딩·중첩 우회로 일부만 방어하므로 근본 대책이 아니다.",
            "<strong>유사 취약점 비교:</strong> <strong>SSRF</strong>는 서버가 임의 URL로 요청하는 취약점(내부망·메타데이터 접근), <strong>SSTI</strong>는 템플릿 엔진에 사용자 입력이 코드로 삽입되는 취약점, <strong>XPath Injection</strong>은 XPath 질의 조작으로 인증 우회. 셋 다 '입력이 해석기로 전달되는 경계' 문제라는 공통점이 있다."
        ]
    })

    items.append({
        "id": "app_content_09",
        "type": "content",
        "category": "app",
        "category_name": "애플리케이션 보안",
        "title": "SQL Injection 고급 유형(Blind·Time-based·2차)과 DB별 우회·방어",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>Error-based:</strong> <code>' AND 1=1 --</code> 등으로 오류 메시지에 DB 정보를 노출. MySQL <code>extractvalue()</code>·<code>updatexml()</code>, MSSQL <code>convert(int, @@version)</code>로 버전·테이블명을 뽑는다.",
            "<strong>Union-based:</strong> <code>ORDER BY n</code>으로 컬럼 수를 맞춘 뒤 <code>UNION SELECT null, username, password FROM users</code>로 데이터를 한 번에 추출. 컬럼 타입이 맞아야 출력된다.",
            "<strong>Blind(Boolean):</strong> 응답 내용 대신 참/거짓 차이(정상 페이지 vs 빈 페이지)로 한 글자씩 추론. <code>SUBSTRING()</code>·<code>ASCII()</code>와 함께 사용.",
            "<strong>Time-based Blind:</strong> MySQL <code>SLEEP(5)</code>, PostgreSQL <code>pg_sleep()</code>, MSSQL <code>WAITFOR DELAY '0:0:5'</code>, Oracle <code>dbms_lock.sleep()</code>. 응답 지연 여부로 판별하며 로그에 흔적이 적다.",
            "<strong>2차(Stored) Injection:</strong> 게시글·프로필 등에 저장된 값이 이후 다른 기능(관리자 화면·통계 배치)에서 검증 없이 질의에 결합되어 실행. 입력 시점이 아니라 <strong>사용 시점</strong>에 터지므로 저장 단계 필터만으로는 막을 수 없다.",
            "<strong>우회 기법:</strong> 공백 대신 <code>/**/</code>·<code>%09</code>·괄호, 대소문자 혼용(<code>UnIoN</code>), 인코딩(URL·유니코드·16진수), 주석으로 뒷부분 절단(<code>--</code>, <code>#</code>), <code>OR '1'='1' --</code>로 인증 우회.",
            "<strong>피해 범위:</strong> 인증 우회, 개인정보 대량 유출, 파일 읽기·쓰기(<code>INTO OUTFILE</code>로 웹셸), MSSQL <code>xp_cmdshell</code>로 OS 명령 실행, 계정 권한 상승.",
            "<strong>방어 5계층:</strong> ① <strong>PreparedStatement(바인딩 변수)</strong>로 코드와 데이터 분리 ② 최소 권한 DB 계정(애플리케이션 계정에 DROP·FILE 권한 금지) ③ 저장 프로시저·ORM 화이트리스트 ④ 오류 메시지 일반화 및 DB 버전 은닉 ⑤ WAF·입력 검증(길이·타입·허용 문자). 근본 대책은 언제나 ①이다."
        ]
    })

    items.append({
        "id": "app_content_10",
        "type": "content",
        "category": "app",
        "category_name": "애플리케이션 보안",
        "title": "취약점 진단 도구·모의해킹 5단계·CVSS 위험도 산정",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>모의해킹 5단계:</strong> ① 정보수집(Footprinting/OSINT — WHOIS, DNS, 구글 해킹, <code>theHarvester</code>) ② 스캐닝(<code>nmap</code>, <code>masscan</code>) ③ 취약점 분석(<code>Nessus</code>, <code>OpenVAS</code>, <code>Nikto</code>) ④ 익스플로잇(<code>Metasploit</code>, <code>sqlmap</code>, <code>Burp</code>) ⑤ 보고서 작성·검증.",
            "<strong>Nmap 주요 옵션:</strong> <code>-sS</code>(SYN 스텔스, root 필요), <code>-sT</code>(TCP connect), <code>-sU</code>(UDP), <code>-sV</code>(버전 탐지), <code>-O</code>(OS 추정), <code>-p-</code>(전체 65535), <code>-Pn</code>(ICMP 무시), <code>-T4</code>(속도), <code>--script vuln</code>(NSE 취약점 스크립트), <code>-oX</code>(XML 출력).",
            "<strong>스캔 응답 판별:</strong> SYN+ACK=열림, RST=닫힘, 무응답=필터링(방화벽 DROP). <code>-sF</code>/<code>-sN</code>/<code>-sX</code>는 닫힌 포트가 RST를 보내지 않는 RFC 793 동작을 이용한 스텔스 스캔이며, 윈도우 대상으로는 신뢰할 수 없다.",
            "<strong>웹 진단 도구:</strong> Burp Suite·OWASP ZAP(프록시·리피터·스캐너), <code>sqlmap</code>(자동 SQLi), <code>Nikto</code>(서버 설정·구버전 점검), <code>dirb</code>/<code>gobuster</code>(디렉터리 탐색), <code>wfuzz</code>(파라미터 퍼징), <code>Searchsploit</code>(익스플로잇 DB 검색).",
            "<strong>CVSS v3.1:</strong> 기본 점수 0.0~10.0, 8개 지표 — AV(공격 경로), AC(공격 복잡도), PR(필요 권한), UI(사용자 상호작용), S(범위 변경), C/I/A(기밀성·무결성·가용성 영향). 0.1~3.9 Low, 4.0~6.9 Medium, 7.0~8.9 High, 9.0~10.0 Critical. 시간·환경 지표로 조정.",
            "<strong>식별자 체계:</strong> CVE(공개 취약점 고유 번호), CWE(취약점 유형 분류, 예: CWE-89 SQLi, CWE-79 XSS), CVSS(심각도 점수), KISA 취약점 점검 기준(리눅스 U-01~U-73, 윈도우 W-01~W-xx).",
            "<strong>법적 전제:</strong> 정보통신망법 제48조(침해금지)에 따라 <strong>사전 서면 동의(진단 범위·기간·시간대)</strong> 없이 스캔·익스플로잇을 수행하면 불법이다. 운영 중 서비스는 부하·가용성 영향을 고려해 시간대를 합의한다.",
            "<strong>보고서 구성:</strong> 개요·범위·방법론 → 요약(위험도 분포) → 취약점별 상세(항목·위험도·재현 절차·증적 캡처·영향) → 조치 권고(단기·중기·장기) → 재진단 결과. 위험도는 CVSS와 자산 중요도를 함께 반영한다."
        ]
    })

    # =========================================================================
    # 암호학 (+2)
    # =========================================================================
    items.append({
        "id": "crypto_content_07",
        "type": "content",
        "category": "crypto",
        "category_name": "암호학·정보보안 일반",
        "title": "블록암호 인증 운영모드(ECB·CBC·CTR·GCM·CCM)와 패딩 오라클",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>ECB:</strong> 블록마다 독립 암호화. 동일 평문 블록이 동일 암호문이 되어 패턴이 노출(펭귄 이미지 사례). 병렬 처리 가능, IV 불필요하지만 <strong>실무 사용 금지</strong>.",
            "<strong>CBC:</strong> 직전 암호문과 XOR 후 암호화. 암호화는 순차, 복호화는 병렬 가능. <strong>IV 재사용 금지</strong>, PKCS#7 패딩 필요. 비트 플리핑으로 앞 블록 평문을 변조할 수 있고, 패딩 검증 오류 메시지가 다르면 <strong>패딩 오라클 공격</strong>(POODLE·BEAST 계열)에 노출된다.",
            "<strong>CFB/OFB:</strong> 블록 암호를 스트림 암호처럼 운용. CFB는 이전 암호문을 피드백(복호화 병렬 불가), OFB는 이전 출력을 피드백(오류 전파 없음, 동기화 필요).",
            "<strong>CTR:</strong> <code>Nonce||Counter</code>를 암호화한 키스트림과 평문을 XOR. 완전 병렬·랜덤 액세스 가능, 패딩 불필요. <strong>같은 키에서 nonce가 재사용되면 키스트림이 재사용</strong>되어 두 평문의 XOR이 노출된다.",
            "<strong>GCM:</strong> CTR 암호화 + GHASH 인증 태그를 결합한 <strong>AEAD</strong> 모드. 기밀성과 무결성을 동시 제공하며 96bit IV, 128bit 태그가 권장. IV(카운터) 재사용 시 인증키(H)가 복원되어 위조가 가능하므로 <strong>nonce 관리가 생명</strong>이다.",
            "<strong>CCM:</strong> CTR + CBC-MAC 조합의 AEAD. 무선 802.11i(CCMP)에서 사용. GCM보다 구현이 단순하지만 병렬성은 낮다.",
            "<strong>모드 선택 기준:</strong> 저장 데이터(디스크)는 XTS/CBC, 네트워크 전송은 GCM(AEAD), 하드웨어 제약 환경은 CCM. 인증 없는 CBC·CTR 단독 사용은 무결성 결여로 위험.",
            "<strong>관련 공격:</strong> 패딩 오라클(CBC, 오류 응답 차이), 비트 플리핑(CBC·CTR), IV 재사용(CTR·GCM), sweet32(64bit 블록 암호 대량 트래픽 충돌)."
        ]
    })

    items.append({
        "id": "crypto_content_08",
        "type": "content",
        "category": "crypto",
        "category_name": "암호학·정보보안 일반",
        "title": "Kerberos 인증 흐름·전자봉투·이중서명(SET) 구조 비교",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>Kerberos 개요:</strong> 대칭키 기반 티켓 인증 프로토콜, <strong>KDC(AS + TGS)</strong>, 포트 <strong>88/TCP·UDP</strong>. 사용자 비밀번호 해시를 마스터키로 사용하며 평문 비밀번호는 네트워크에 전송하지 않는다.",
            "<strong>3단계 흐름:</strong> ① <code>AS-REQ/AS-REP</code> — 인증 후 <strong>TGT</strong>와 세션키 발급 ② <code>TGS-REQ/TGS-REP</code> — TGT로 접근할 서비스의 <strong>Service Ticket</strong> 발급 ③ <code>AP-REQ/AP-REP</code> — 서버에 티켓 제시, 상호 인증. 이후 티켓 갱신(<code>TGS-REQ</code>)으로 재인증 없이 사용.",
            "<strong>취약점·공격:</strong> AS-REP Roasting(사전 인증 비활성 계정), <strong>Kerberoasting</strong>(SPN 계정 티켓을 오프라인 크래킹), Golden Ticket(krbtgt 해시로 무제한 위조), Silver Ticket(서비스 계정 해시), 시간 오차 5분 초과 시 인증 실패, KDC 단일 장애점.",
            "<strong>대응:</strong> 사전 인증 강제, 서비스 계정 긴 랜덤 암호(25자 이상)·gMSA, krbtgt 주기 변경, AES 전용( RC4 비활성), 관리자 계정 티켓 수명 단축, NTP 시간 동기화, 이벤트 4768·4769 모니터링.",
            "<strong>전자봉투:</strong> 대용량 문서는 속도가 빠른 <strong>대칭키(세션키)</strong>로 암호화하고, 그 세션키만 수신자의 <strong>공개키</strong>로 암호화해 함께 보낸다. 하이브리드 방식으로 기밀성과 성능을 동시에 확보하며, 세션키는 매 건 새로 생성한다.",
            "<strong>이중서명(SET):</strong> 구매자는 OI(주문정보) 해시와 PI(지불정보) 해시를 결합해 한 번만 서명한다. 상점은 PI를 볼 수 없고 카드사는 OI를 볼 수 없어 <strong>프라이버시와 부인방지</strong>를 동시에 만족한다. 현재는 토큰화(PAN 대체)·3-D Secure가 실무 표준.",
            "<strong>전자서명과의 구분:</strong> 전자서명은 무결성·인증·부인방지 3가지를 보장하지만 <strong>기밀성은 제공하지 않는다</strong>. 기밀성이 필요하면 서명 후 암호화(또는 전자봉투)를 별도로 적용해야 한다."
        ]
    })

    # =========================================================================
    # 관리·법률 (+3)
    # =========================================================================
    items.append({
        "id": "law_content_08",
        "type": "content",
        "category": "law",
        "category_name": "보안 관리·법규",
        "title": "디지털 포렌식 증거 수집 절차·휘발성 순서·연계보관성",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>5대 원칙:</strong> ① 정당성(적법 절차·영장·동의) ② 재현성(동일 절차로 동일 결과) ③ 신속성(휘발성 데이터 선점) ④ <strong>연계보관성(Chain of Custody — 수집·이송·보관·분석·제출 각 단계의 취급자·일시·장소 기록)</strong> ⑤ 무결성(해시값으로 원본과 사본 동일성 증명).",
            "<strong>휘발성 순서(RFC 3227):</strong> CPU 레지스터·캐시 → 라우팅 테이블·ARP 캐시·프로세스 목록 → <strong>RAM(메모리 덤프)</strong> → 임시 파일·스왑 → 디스크(비휘발성) → 원격 모니터링·로그 → 백업·아카이브. 위에서 아래로 갈수록 휘발성이 낮다.",
            "<strong>절차:</strong> 사전 준비(영장·도구·인력) → 현장 보존(사진·출입통제) → 휘발성 증거 수집 → 디스크 이미징(<code>dd</code>·<code>dcfldd</code>·FTK Imager, <strong>Write Blocker</strong> 사용) → 증거 포장·이송 → 분석 → 보고서 → 법정 제출.",
            "<strong>도구:</strong> EnCase·FTK(상용 종합), Autopsy·TSK(오픈소스), Volatility(메모리 분석), <code>dd</code>/<code>dcfldd</code>(이미징), <code>sha256sum</code>(무결성), Wireshark·tcpdump(네트워크 증거), <code>sleuthkit</code>(파일시스템).",
            "<strong>무결성 검증:</strong> 수집 즉시 원본과 사본의 SHA-256 해시를 계산해 대조하고, 원본은 봉인 보관, 분석은 <strong>사본</strong>으로 수행. 해시가 다르면 증거 능력이 상실된다.",
            "<strong>안티포렌식:</strong> 타임스탬프 조작(<code>touch -d</code>), 로그 삭제·와이핑(<code>shred</code>·<code>cipher /w</code>), 파일 슬랙·MFT 조작, 스테가노그래피, 암호화(랜섬웨어·볼륨 암호화), USB 흔적 삭제. 대응은 아티팩트 교차 검증(레지스트리·프리페치·이벤트로그·$MFT·저널).",
            "<strong>윈도우 아티팩트:</strong> <code>NTUSER.DAT</code>·<code>UsrClass.dat</code>(사용자 행위), <code>Amcache</code>·<code>Prefetch</code>(실행 흔적), <code>$MFT</code>·<code>$UsnJrnl</code>(파일 생성·변경), 이벤트 로그(4624·4625·4688·7045), 브라우저 히스토리, <code>pagefile.sys</code>·<code>hiberfil.sys</code>.",
            "<strong>법적 효력:</strong> 위법 수집 증거는 배제될 수 있고, 디지털 증거는 전문법칙의 예외(제313조) 요건을 충족해야 증거 능력이 인정된다. 그래서 연계보관성 기록이 곧 증거 능력이다."
        ]
    })

    items.append({
        "id": "law_content_09",
        "type": "content",
        "category": "law",
        "category_name": "보안 관리·법규",
        "title": "침해사고 대응 절차 7단계와 신고·공유 체계",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>7단계(국내 실무 기준):</strong> ① 사전 준비(대응 조직·연락망·도구·모의훈련) ② 징후 포착(IDS·SIEM 경보, 사용자 신고) ③ 정밀 분석(로그·패킷·악성코드 분석으로 공격 경로 규명) ④ 전파 및 보고(내부 보고 체계, 외부 신고) ⑤ 대응·억제(격리·차단·계정 잠금) ⑥ 복구(백업 복원·서비스 정상화) ⑦ 보안강화 및 사후 분석(원인 분석·재발방지).",
            "<strong>NIST 800-61과 대응:</strong> 준비 → 탐지·분석 → 억제·근절·복구 → 사후 활동. 국내 7단계와 순서만 다를 뿐 <strong>증거 보존 → 격리 → 근절 → 복구 → 학습</strong>의 흐름은 동일하다.",
            "<strong>억제 전략:</strong> 감염 단말 네트워크 차단(스위치 포트 shutdown·VLAN 격리), 방화벽·IPS 룰로 C&C IP·도메인 차단, 침해 계정 비활성·비밀번호 일괄 변경, 필요 시 서비스 일시 중단. 억제보다 <strong>증거 보존이 우선</strong>되는 경우(포렌식 대상)를 먼저 판단한다.",
            "<strong>신고 시한:</strong> 개인정보 유출은 인지 후 <strong>72시간 이내</strong> 정보주체 통지(1천 명 이상 유출 시 개인정보보호위원회·KISA 신고), 정보통신서비스 침해사고는 <strong>24시간 이내</strong> KISA(118) 신고(망법 제48조의3), 전자금융사고는 금융회사가 금융감독원에 지체 없이 보고.",
            "<strong>공유 체계:</strong> KISA KrCERT/CC(침해사고 접수·기술 지원), ISAC(업종별 정보공유분석센터 — 금융·통신·에너지), CERT(기업 내부 대응팀), 경찰청 사이버수사국(형사 사건), 과기정통부(정책).",
            "<strong>대응 조직 역할:</strong> CISO(의사결정·대외 보고), 보안관제팀(24×7 모니터링), 사고대응팀(분석·복구), 법무·홍보(법적 검토·공지), 서비스 운영팀(복구 협조). 사전에 <strong>의사결정 권한과 연락망</strong>을 문서화해야 한다.",
            "<strong>사후 활동:</strong> 타임라인 재구성, 근본원인분석(RCA), IOC 추출·공유, 취약점 패치·정책 개선, 재발방지 대책 이행 점검, 모의훈련(레드팀·테이블톱)으로 검증.",
            "<strong>실무 함정:</strong> 증거 확보 없이 재부팅·재설치를 먼저 하면 원인 규명이 불가능해지고, 신고 시한을 넘기면 과태료·과징금 대상이 된다. 통지는 <strong>유출 인지 시점</strong>부터 기산한다."
        ]
    })

    items.append({
        "id": "law_content_10",
        "type": "content",
        "category": "law",
        "category_name": "보안 관리·법규",
        "title": "정보통신망법 vs 전자서명법 vs 전자금융거래법 핵심 비교",
        "badge": "내용별 핵심정리",
        "points": [
            "<strong>정보통신망법:</strong> 정보통신서비스 제공자의 안전성 확보조치(제45조), 침해사고 신고·통지(제48조의3), 이용자 정보 보호, 스팸规制. 2020년 데이터 3법 개정으로 개인정보 관련 조항 상당수가 <strong>개인정보보호법으로 이관</strong>되어 일반법은 개인정보보호법, 망법은 통신서비스 특례를 담당한다.",
            "<strong>전자서명법:</strong> 2020년 12월 전부개정으로 <strong>공인전자서명·공인인증기관 제도 폐지</strong>. 전자서명은 법령이 정한 경우 또는 당사자 약정에 따라 효력이 인정되며, 인증기관은 자유롭게 사업 가능(평가·인정은 민간). 전자문서의 서면 효력은 전자문서법이 담당.",
            "<strong>전자금융거래법:</strong> 전자금융거래의 안전성·신뢰성 확보. <strong>접근매체(비밀번호·OTP·인증서·생체정보)</strong>의 양도·대여·대출 금지, 전자금융사고 신고·이용자 통지 의무, 사고 책임 원칙 — 이용자의 고의·중과실이 없으면 금융회사·전자금융업자가 손실을 부담.",
            "<strong>비교 축:</strong> ① 목적(망 이용 촉진·정보보호 / 전자서명 효력·인증 신뢰 / 금융거래 안전) ② 적용대상(정보통신서비스 제공자 / 서명·인증 사업자·이용자 / 금융회사·전자금융업자·이용자) ③ 핵심 의무(안전조치·신고 / 효력 요건·인증 / 접근매체 관리·사고 책임).",
            "<strong>벌칙 비교:</strong> 망법상 침해사고 신고 태만은 과태료, 개인정보 유출·목적 외 이용은 개인정보보호법에 따라 <strong>5년 이하 징역 또는 5천만원 이하 벌금</strong> 및 전체 매출액의 3% 이하 과징금(2026. 9. 11. 시행 개정으로 재범·1천만 명 이상 피해·시정명령 불이행 시 10%·50억원 가중 상한 신설). 전금법상 접근매체 양도·대여는 <strong>3년 이하 징역 또는 2천만원 이하 벌금</strong>.",
            "<strong>겸직·조직 규정:</strong> 망법상 일정 규모 이상 정보통신서비스 제공자는 정보보호 최고책임자(CISO)를 지정해야 하고, 자산 5조원 이상(또는 5천억원 이상 + ISMS 의무) 기업의 CISO는 CIO 등 타 업무 총괄 임원 겸직이 제한된다.",
            "<strong>시험 포인트:</strong> 신고 시한(개인정보 72시간 / 침해사고 24시간), 접근매체 정의, 공인인증 폐지 시점(2020.12.10), 데이터 3법 이관(2020.8.5)을 연도와 함께 묶어 외운다."
        ]
    })

    return items

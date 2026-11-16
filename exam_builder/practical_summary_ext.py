# -*- coding: utf-8 -*-
"""
practical_summary_ext.py
2026 이기적 정보보안기사 실기 편제 기준 확장분
- 실기 내용별 심층 실무 요약 15선 (기존 20선 -> 총 35선)
- 실기 단답형 핵심 족보 30선 (기존 30선 -> 총 60선)
"""


def get_extra_practical_content():
    items = []

    # ---------------------------- 네트워크/시스템 ----------------------------
    items.append({
        "id": "prac_content_21", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "Snort 룰 헤더·옵션 총정리와 룰 작성 실전", "badge": "실기 단답·실무",
        "points": [
            "<strong>룰 7필드 구조:</strong> <code>action proto src_ip src_port -&gt; dst_ip dst_port (options)</code>. 예: <code>alert tcp any any -&gt; 192.168.0.10 80 (msg:\"WEB SQLi\"; content:\"union select\"; nocase; sid:1000001; rev:1;)</code>",
            "<strong>action 5종:</strong> <code>alert</code>(경보), <code>log</code>(기록), <code>pass</code>(무시), <code>drop</code>(차단, IPS 모드), <code>reject</code>(차단+거부 응답). 차단은 inline(af_packet/NFQ) 모드에서만 동작한다.",
            "<strong>방향 연산자:</strong> <code>-&gt;</code>(단방향), <code>&lt;&gt;</code>(양방향). 변수는 <code>$HOME_NET</code>, <code>$EXTERNAL_NET</code>, <code>any</code>, <code>!192.168.0.0/16</code>(부정). 포트는 <code>[80,443]</code>, <code>1:1024</code> 범위 표기.",
            "<strong>핵심 옵션:</strong> <code>msg</code>, <code>sid</code>(1000001~ 로컬, 1~999999 예약), <code>rev</code>, <code>content</code>(바이트 매칭), <code>nocase</code>, <code>depth</code>/<code>offset</code>(시작 구간 제한), <code>distance</code>/<code>within</code>(이전 매칭 기준 상대 위치), <code>pcre</code>(정규식), <code>flow:established,to_server</code>, <code>flags:S</code>, <code>threshold</code>/<code>detection_filter</code>(경보 빈도 제어).",
            "<strong>룰 예시 — SQLi:</strong> <code>alert tcp $EXTERNAL_NET any -&gt; $HTTP_SERVERS $HTTP_PORTS (msg:\"SQL Injection attempt\"; flow:to_server,established; content:\"union\"; nocase; content:\"select\"; nocase; distance:0; classtype:web-application-attack; sid:1000010; rev:2;)</code>",
            "<strong>룰 예시 — SYN 플러드:</strong> <code>alert tcp $EXTERNAL_NET any -&gt; $HOME_NET any (msg:\"SYN Flood\"; flags:S; threshold:type both, track by_dst, count 200, seconds 10; sid:1000020; rev:1;)</code>",
            "<strong>성능·운영:</strong> content는 빠른 패턴을 앞에 두고 <code>fast_pattern</code>을 지정, 룰 수보다 <code>flow</code>·<code>ports</code> 제한으로 검사 범위를 줄인다. <code>snort -T -c /etc/snort/snort.conf</code>로 문법 검증, <code>-A console</code>로 실시간 경보 확인.",
            "<strong>탐지 위치:</strong> 네트워크 IDS는 우회(단편화·인코딩)에 취약하므로 호스트 기반 로그와 상관분석이 필요하다. Snort 3는 <code>snort.lua</code> 설정으로 전환되었다."
        ]
    })

    items.append({
        "id": "prac_content_22", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "iptables·nftables 체인·타겟·상태추적(stateful) 실전", "badge": "실기 단답·실무",
        "points": [
            "<strong>테이블·체인:</strong> filter(INPUT·FORWARD·OUTPUT), nat(PREROUTING·POSTROUTING), mangle, raw. 규칙은 위에서 아래로 <strong>첫 매칭 시 종료</strong>되므로 순서가 곧 정책이다.",
            "<strong>기본 정책:</strong> <code>iptables -P INPUT DROP</code>, <code>-P FORWARD DROP</code>, <code>-P OUTPUT ACCEPT</code>. 정책을 DROP으로 두고 허용 규칙만 추가하는 화이트리스트 방식이 원칙.",
            "<strong>필수 허용 세트:</strong> <code>-A INPUT -i lo -j ACCEPT</code>, <code>-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT</code>, <code>-A INPUT -p tcp --dport 22 -s 10.0.0.0/24 -j ACCEPT</code>, <code>-A INPUT -p icmp --icmp-type echo-request -j ACCEPT</code>.",
            "<strong>타겟:</strong> ACCEPT(통과), DROP(응답 없이 폐기), REJECT(거부 응답 — <code>--reject-with tcp-reset</code>), LOG(기록 후 다음 규칙 계속), RETURN(상위 체인 복귀), SNAT/DNAT/MASQUERADE.",
            "<strong>NAT 예:</strong> <code>iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE</code>(공유), <code>-A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.5:8080</code>(포트 포워딩). <code>net.ipv4.ip_forward=1</code> 필요.",
            "<strong>상태 추적:</strong> <code>-m conntrack --ctstate NEW,ESTABLISHED,RELATED,INVALID</code>. INVALID는 DROP, ESTABLISHED·RELATED는 초반에 ACCEPT해 성능·가용성을 확보한다.",
            "<strong>보호 기법:</strong> <code>-m limit --limit 10/min --limit-burst 20</code>(연결 폭주 제한), <code>-m recent</code>(반복 접속 차단), <code>-m geoip</code>, 포트 스캔 탐지(<code>--tcp-flags ALL NONE</code> DROP), <code>fail2ban</code> 연동.",
            "<strong>nftables 전환:</strong> <code>nft add table inet filter</code>, <code>nft add chain inet filter input { type filter hook input priority 0 \\; policy drop \\; }</code>, <code>nft add rule inet filter input ct state established,related accept</code>. 규칙 저장은 <code>iptables-save</code>/<code>nft list ruleset</code>."
        ]
    })

    items.append({
        "id": "prac_content_23", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "Apache·Nginx·IIS 웹 로그 공격 패턴 판별법", "badge": "실기 단답·실무",
        "points": [
            "<strong>Apache access 로그 형식:</strong> <code>%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"</code> — IP, 사용자, 시각, 요청라인, 상태코드, 바이트, 리퍼러, UA. 결합 로그(combined)가 기본.",
            "<strong>SQLi 흔적:</strong> <code>union+select</code>, <code>%27</code>(작은따옴표), <code>or+1%3D1</code>, <code>information_schema</code>, <code>sleep(</code>, <code>benchmark(</code>가 URL 쿼리에 등장. 200 응답이 반복되면 Blind 추출 시도로 판단.",
            "<strong>XSS·LFI 흔적:</strong> <code>&lt;script&gt;</code>, <code>%3Cscript%3E</code>, <code>onerror=</code>, <code>javascript:</code> / <code>../../../etc/passwd</code>, <code>..%2f..%2f</code>, <code>php://filter</code>, <code>/proc/self/environ</code>.",
            "<strong>웹셸·스캔 흔적:</strong> <code>.php</code>·<code>.jsp</code> 업로드 후 <code>POST</code> 반복, <code>cmd=</code>, <code>eval(</code>, <code>base64_decode(</code>, 404를 대량 발생시키는 디렉터리 스캔(<code>/admin</code>, <code>/backup.zip</code>, <code>/.git</code>), Nikto·sqlmap UA(<code>sqlmap/1.x</code>, <code>Nikto</code>).",
            "<strong>상태코드 판독:</strong> 200(성공·침해 의심), 302(리다이렉트·인증 우회 시도), 403(권한 차단 시도 반복), 404(스캔), 500(인젝션·파일 조작으로 인한 오류). <strong>동일 IP의 404 폭증 → 이후 200 등장</strong>은 성공한 공격의 전형적 신호.",
            "<strong>Nginx 로그:</strong> <code>log_format main '$remote_addr - $remote_user [$time_local] \"$request\" $status $body_bytes_sent \"$http_referer\" \"$http_user_agent\" $request_time';</code> — 기본 access_log에는 <code>$request_body</code>가 없어 POST 본문은 별도 설정이 필요하다.",
            "<strong>IIS 로그:</strong> <code>%date %time %s-ip %cs-method %cs-uri-stem %cs-uri-query %s-port %cs(User-Agent) %sc-status</code> 형식, 기본 경로 <code>%SystemRoot%\\System32\\LogFiles\\W3SVC1</code>, 필드는 사이트별로 선택 가능(cs-uri-query 활성화 여부 확인).",
            "<strong>로그 분석 실무:</strong> <code>awk '{print $1}' access.log | sort | uniq -c | sort -rn | head</code>(상위 IP), 400·500만 추출, 시간대별 급증 확인, 에러 로그(<code>error.log</code>)와 대조, 침해 시 <strong>로그 보존(원본 해시)</strong>이 우선."
        ]
    })

    items.append({
        "id": "prac_content_24", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "Java·PHP·Python 시큐어코딩 취약 코드 vs 수정 코드", "badge": "실기 단답·실무",
        "points": [
            "<strong>Java — SQL 삽입:</strong> 취약 <code>String q = \"SELECT * FROM users WHERE id='\" + id + \"'\"; stmt.executeQuery(q);</code> → 수정 <code>PreparedStatement ps = con.prepareStatement(\"SELECT * FROM users WHERE id=?\"); ps.setString(1, id);</code>",
            "<strong>Java — XSS·경로 조작:</strong> 취약 <code>out.println(\"<div>\" + name + \"</div>\");</code> → 수정 <code>ESAPI.encoder().encodeForHTML(name)</code> 또는 JSTL <code>&lt;c:out&gt;</code>. 파일 경로는 <code>new File(base, filename).getCanonicalPath().startsWith(base)</code>로 검증.",
            "<strong>Java — 역직렬화·XXE:</strong> <code>ObjectInputStream</code> 사용 금지(화이트리스트 <code>ObjectInputFilter</code>), <code>DocumentBuilderFactory</code>에 <code>disallow-doctype-decl=true</code> 설정, <code>Runtime.exec()</code> 대신 인자 분리 API 사용.",
            "<strong>PHP — 명령·파일 삽입:</strong> 취약 <code>system(\"ping -c 1 \".$_GET['ip']);</code> → 수정 <code>escapeshellarg($ip)</code> 또는 <code>filter_var($ip, FILTER_VALIDATE_IP)</code> 후 <code>exec</code> 인자 배열 사용. 파일 포함은 취약 <code>include($_GET['page'].'.php')</code> → 화이트리스트 매핑 배열 사용.",
            "<strong>PHP — 업로드·출력:</strong> <code>move_uploaded_file</code> 전 <code>finfo_file()</code>로 MIME 확인, 확장자 화이트리스트, 저장 파일명 난수화(<code>bin2hex(random_bytes(16))</code>), 출력 시 <code>htmlspecialchars($v, ENT_QUOTES, 'UTF-8')</code>.",
            "<strong>Python — SQL·명령·역직렬화:</strong> 취약 <code>cursor.execute(\"SELECT * FROM t WHERE id='%s'\" % id)</code> → 수정 <code>cursor.execute(\"SELECT * FROM t WHERE id=%s\", (id,))</code>. 취약 <code>os.system(\"ping \" + host)</code> → <code>subprocess.run([\"ping\", \"-c\", \"1\", host], shell=False)</code>. <code>pickle.loads()</code>·<code>yaml.load()</code> 대신 <code>yaml.safe_load()</code>.",
            "<strong>공통 원칙 7:</strong> ① 입력 검증(서버 측·화이트리스트) ② 출력 인코딩(컨텍스트별) ③ 인증·권한 검사(매 요청) ④ 에러 메시지 일반화 ⑤ 최소 권한 실행 ⑥ 안전한 기본값(보안 헤더·세션 플래그) ⑦ 의존성·라이브러리 최신화.",
            "<strong>실기 서술 포인트:</strong> '취약 코드 → 공격 시나리오 → 수정 코드 → 재발방지'의 4단으로 쓰면 감점이 없다. 수정 코드에는 반드시 <strong>검증·인코딩·권한</strong> 중 무엇을 적용했는지 명시한다."
        ]
    })

    items.append({
        "id": "prac_content_25", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "리눅스 U-01~U-73 주요 취약점 점검 항목과 조치법", "badge": "실기 단답·실무",
        "points": [
            "<strong>U-01 root 원격 접속 제한:</strong> <code>/etc/ssh/sshd_config</code>에 <code>PermitRootLogin no</code>, <code>/etc/pam.d/sshd</code> 또는 <code>/etc/securetty</code>로 tty 제한. 점검: <code>grep -i permitrootlogin /etc/ssh/sshd_config</code>.",
            "<strong>U-02 비밀번호 복잡성:</strong> <code>/etc/pam.d/system-auth</code>에 <code>pam_pwquality.so minlen=8 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1 retry=3</code>, <code>pam_pwhistory.so remember=4</code>.",
            "<strong>U-03 계정 잠금:</strong> <code>pam_faillock.so deny=5 unlock_time=1200</code>(또는 <code>pam_tally2 --deny=5</code>), <code>/etc/login.defs</code>의 <code>PASS_MAX_DAYS 90</code>. 점검: <code>grep -E 'deny|unlock_time' /etc/pam.d/*</code>.",
            "<strong>U-04 패스워드 파일 보호:</strong> <code>/etc/shadow</code> 사용 여부(<code>passwd: files shadow</code>), <code>/etc/passwd</code> 두 번째 필드가 <code>x</code>인지 확인. 권한은 400·소유자 root.",
            "<strong>U-05~U-08 계정·환경:</strong> 불필요 계정(adm·lp·uucp·nuucp) 셸 <code>/sbin/nologin</code>, UID 0 중복 계정 제거, <code>/etc/profile</code>의 <code>umask 022</code>, PATH에 <code>.</code>(현재 디렉터리) 미포함.",
            "<strong>U-09~U-13 서비스·파일:</strong> <code>ls -l</code>로 <code>/etc/passwd</code>·<code>shadow</code>·<code>services</code>·<code>hosts</code> 권한 확인(644/600), SUID/SGID 파일 전수 검색(<code>find / -perm -4000 -o -perm -2000</code>), world-writable 파일(<code>-perm -2</code>) 점검.",
            "<strong>U-14~U-20 서비스 관리:</strong> 불필요 RPC·NFS·FTP·telnet·SMTP 서비스 중지(<code>systemctl disable --now telnet.socket</code>), anonymous FTP 차단, <code>/etc/exports</code>에 <code>everyone</code>·<code>*</code> 미사용, DNS zone transfer 제한(<code>allow-transfer { none; }</code>).",
            "<strong>U-21~U-30·U-40번대:</strong> <code>/etc/hosts.equiv</code>·<code>.rhosts</code> 제거, cron·at 권한(<code>at.allow</code>·<code>cron.allow</code>, <code>at.deny</code> 비움), NFS 접근통제, finger·r계열 서비스 중지, 각종 서비스 배너·버전 은닉(<code>ServerTokens Prod</code>)을 함께 점검한다."
        ]
    })

    items.append({
        "id": "prac_content_26", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "nmap 옵션별 패킷 응답 분석과 스캔 결과 해석", "badge": "실기 단답·실무",
        "points": [
            "<strong>SYN 스텔스(<code>-sS</code>):</strong> SYN만 보내고 응답이 SYN+ACK면 열림, RST면 닫힘. 연결을 완성하지 않아 로그가 적게 남는다(root 권한 필요).",
            "<strong>Connect 스캔(<code>-sT</code>):</strong> OS의 connect()를 사용해 3-way 핸드셰이크 완성 후 종료. 애플리케이션 로그에 남고 권한이 필요 없다.",
            "<strong>FIN/NULL/XMAS(<code>-sF -sN -sX</code>):</strong> RFC 793의 '닫힌 포트는 RST 응답' 특성을 이용. 열린 포트는 무응답, 닫힌 포트는 RST. <strong>윈도우는 무관하게 RST를 보내 판별 불가</strong>.",
            "<strong>UDP 스캔(<code>-sU</code>):</strong> 응답이 없으면 open|filtered, ICMP port unreachable(3/3)이 오면 closed. 느리고 신뢰도가 낮아 161(SNMP)·53(DNS)·123(NTP) 등 주요 포트만 검사한다.",
            "<strong>탐지·지문:</strong> <code>-sV</code>(서비스 버전), <code>-O</code>(OS 추정, 열린 1·닫힌 1 포트 필요), <code>--script=banner,vuln</code>(NSE), <code>-A</code>(종합), <code>--traceroute</code>.",
            "<strong>속도·은닉:</strong> <code>-T0~-T5</code>(높을수록 빠르고 흔적↑), <code>--max-retries 1</code>, <code>-D RND:10</code>(디코이), <code>--spoof-mac</code>, <code>-f</code>(단편화), <code>--data-length</code>. 방화벽 DROP 정책이면 <code>-Pn</code>으로 호스트 생존 판정을 생략.",
            "<strong>결과 표기:</strong> <code>open</code>(응답 있음), <code>closed</code>(RST 수신), <code>filtered</code>(무응답·방화벽), <code>open|filtered</code>(구분 불가), <code>unfiltered</code>(도달하나 상태 미확정).",
            "<strong>실무 해석:</strong> 22·3306·1521이 외부에 열려 있으면 즉각 취약 후보, 445·3389 노출은 랜섬웨어·RDP 공격의 전조다. 스캔 결과는 자산 대장과 대조해 미등록 서비스를 찾는 데 쓴다."
        ]
    })

    items.append({
        "id": "prac_content_27", "type": "content", "category": "network", "category_name": "네트워크 보안",
        "title": "tcpdump·Wireshark 캡처 필터 문법과 패킷 분석", "badge": "실기 단답·실무",
        "points": [
            "<strong>tcpdump 기본:</strong> <code>tcpdump -i eth0 -nn -s 0 -w cap.pcap</code>(-nn: 이름 해석 금지, -s 0: 전체 캡처, -w: 파일 저장), 읽기는 <code>-r cap.pcap</code>, 화면 확인은 <code>-A</code>(ASCII)·<code>-X</code>(HEX+ASCII).",
            "<strong>BPF 필터:</strong> <code>host 10.0.0.5</code>, <code>src host</code>, <code>dst port 80</code>, <code>net 192.168.1.0/24</code>, <code>tcp and port 443</code>, <code>not port 22</code>, <code>tcp[13] &amp; 2 != 0</code>(SYN 플래그만), <code>icmp[icmptype] == 8</code>(echo request).",
            "<strong>실전 예:</strong> <code>tcpdump -i any -nn 'tcp port 80 and host 10.0.0.5' -c 100</code>, SYN만 보기 <code>'tcp[tcpflags] &amp; tcp-syn != 0'</code>, DNS <code>udp port 53</code>, ARP <code>arp</code>.",
            "<strong>Wireshark 디스플레이 필터:</strong> <code>ip.addr==10.0.0.5</code>, <code>tcp.port==80</code>, <code>http.request.method==\"POST\"</code>, <code>http.response.code==404</code>, <code>tcp.flags.syn==1 and tcp.flags.ack==0</code>, <code>dns.qry.name contains \"malicious\"</code>, <code>tls.handshake.type==1</code>(ClientHello).",
            "<strong>유용 기능:</strong> Statistics → Conversations(통신량 상위 IP), Follow TCP Stream(세션 재조립), Expert Information(재전송·RST·체크섬 오류), <code>tcp.analysis.retransmission</code>, 파일 추출 File → Export Objects → HTTP.",
            "<strong>공격 패턴 판독:</strong> 다수 IP의 SYN만 반복(플러드), 1:1로 같은 크기 요청 반복(Slowloris), 80 포트에 <code>union select</code> 문자열, 대량 DNS 질의(터널링), ARP 응답 폭주(스푸핑), ICMP 대형 패킷(터널링).",
            "<strong>캡처 주의:</strong> 스위치 환경에서 전체 트래픽이 보이지 않으므로 SPAN(포트 미러링)·TAP을 사용하고, 증거용 캡처는 <code>sha256sum</code>으로 무결성을 기록하며 개인정보 포함 여부를 검토한다."
        ]
    })

    # ---------------------------- 관리·법률 ----------------------------
    items.append({
        "id": "prac_content_28", "type": "content", "category": "law", "category_name": "디지털 포렌식 & 법률",
        "title": "위험도 산정과 정보보호 관리체계 서술형 답안 템플릿", "badge": "실기 단답·실무",
        "points": [
            "<strong>정량적 산정:</strong> 자산가치(AV) × 노출계수(EF) = SLE, SLE × 연간발생빈도(ARO) = <strong>ALE</strong>. 대책 도입 판단은 <code>ALE(대책 전) - ALE(대책 후) &gt; 대책 비용</code>일 때 타당하다.",
            "<strong>정성적 산정:</strong> 발생가능성(상·중·하) × 영향도(상·중·하) 매트릭스로 위험등급(심각·높음·보통·낮음)을 결정. 정량화가 어려운 신규 위협·규제 리스크에 적합하다.",
            "<strong>위험 처리 4전략:</strong> 감소(통제 적용), 회피(서비스·기능 중단), 전가(보험·외주), 수용(잔여 위험 승인). 처리 결과는 <strong>잔여 위험</strong>으로 문서화하고 경영진 승인을 받는다.",
            "<strong>서술형 기본 골격:</strong> ① 현황·문제 정의 ② 관련 기준·법령 근거(ISMS-P 2.x, 개인정보보호법 제29조 등) ③ 위험 분석(자산-위협-취약점) ④ 대책(예방·탐지·대응·복구) ⑤ 기대효과·이행 일정 ⑥ 검증 방법.",
            "<strong>대책 서술 4분류:</strong> 예방(접근통제·암호화·교육), 탐지(IDS·SIEM·로그 점검), 대응(격리·차단·신고), 복구(백업·DR·대체 절차). 한 항목만 쓰면 감점, 네 층을 모두 제시해야 완성된다.",
            "<strong>수치 근거 제시:</strong> 접속기록 1년(5만명 이상 2년), 비밀번호 3종 8자리/2종 10자리, 유출 통지 72시간, 침해사고 신고 24시간, 백업 복구 훈련 연 1회 — 숫자를 포함하면 논리적 완결성이 올라간다.",
            "<strong>감점 회피:</strong> '철저히 관리한다' 같은 선언적 표현 대신 <strong>주체·주기·산출물</strong>을 명시한다(예: '보안담당자는 월 1회 접속기록을 점검하고 점검 결과를 CISO에 보고한다').",
            "<strong>ISMS-P 심사 연계 답안:</strong> 기준 번호(예: 2.5.1 사용자 계정 관리)를 제시하고, 요구사항 → 확인 증적(정책서·로그·승인서) → 결함 판정 포인트 순으로 3단 서술하면 실기 서술형과 인증심사 실무 모두에 통한다."
        ]
    })

    items.append({
        "id": "prac_content_29", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "윈도우 서버 취약점 점검 항목(W 항목)과 조치", "badge": "실기 단답·실무",
        "points": [
            "<strong>계정·암호:</strong> Administrator 이름 변경 및 사용 중지, Guest 비활성, 암호 최대 사용 기간 90일·복잡성 사용, <strong>계정 잠금 임계값 5회</strong>, 최근 암호 기억 24개. 확인: <code>net user</code>, <code>secpol.msc</code>.",
            "<strong>서비스·포트:</strong> 불필요 서비스(Telnet·Simple TCP/IP·SNMP·FTP Publishing) 중지, <code>netstat -ano</code>로 LISTENING 포트 확인, 445·3389 외부 노출 차단, SMBv1 제거(<code>Disable-WindowsOptionalFeature -FeatureName SMB1Protocol</code>).",
            "<strong>공유·권한:</strong> <code>net share</code>로 불필요 공유 제거(IPC$·C$는 기본), 공유 권한과 NTFS 권한 중 더 제한적인 값 적용, Everyone 쓰기 권한 제거, <code>icacls</code>로 상속 정리.",
            "<strong>감사·로그:</strong> 로그온 성공·실패, 계정 관리, 정책 변경, 객체 액세스 감사 활성화, 보안 로그 크기 20MB 이상·덮어쓰기 정책, 원격 로그 전송(WEF)으로 변조 대비. 이벤트 4624·4625·4720·4672·1102.",
            "<strong>레지스트리·정책:</strong> <code>AlwaysInstallElevated=0</code>, <code>RestrictAnonymous=1</code>, 자동 로그온 비활성, 화면 보호기 잠금(스크린세이버 암호), LM 해시 저장 차단(<code>NoLMHash=1</code>), <code>secedit /export</code>로 정책 백업.",
            "<strong>패치·백신:</strong> 최신 보안 업데이트 적용(WSUS), 백신 실시간 감시·정의 업데이트, Windows Defender 방화벽 도메인·개인·공용 프로필 모두 활성, 불필요 기능(파워셸 v2·SMB1) 제거.",
            "<strong>원격·웹:</strong> RDP NLA 강제·포트 변경(보안 효과 미미, 접근제어 병행), IIS 불필요 모듈·디렉터리 브라우징 제거, <code>Server</code> 헤더 은닉, FTP 대신 SFTP, 관리 콘솔 접근 IP 제한.",
            "<strong>점검 절차:</strong> 자산·OS 버전 확인 → 계정·서비스·공유·레지스트리·감사 순으로 스크립트 점검(또는 CIS Benchmark 도구) → 항목별 양호/취약/수동 판정 → 취약 항목 조치 후 <strong>재점검 증적</strong> 확보."
        ]
    })

    items.append({
        "id": "prac_content_30", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "DBMS(MySQL·Oracle) 취약점 점검과 권한 관리", "badge": "실기 단답·실무",
        "points": [
            "<strong>계정·권한 원칙:</strong> 애플리케이션 계정은 DML만, 관리 계정은 원격 접속 차단, <code>root</code>·<code>SYSTEM</code>·<code>SYS</code> 직접 사용 금지, 계정별 출발지 IP 제한(<code>'user'@'10.0.0.%'</code>).",
            "<strong>MySQL 점검:</strong> <code>SELECT user, host, authentication_string FROM mysql.user;</code>로 빈 암호·% 호스트 계정 확인, <code>SHOW GRANTS FOR 'app'@'%';</code>로 과도 권한 확인, <code>FILE</code>·<code>SUPER</code>·<code>PROCESS</code> 권한 회수, <code>local_infile=OFF</code>.",
            "<strong>MySQL 설정:</strong> <code>skip-grant-tables</code> 사용 금지, <code>bind-address=127.0.0.1</code> 또는 내부 IP, <code>--skip-symbolic-links</code>, 히스토리 파일 노출 방지, <code>general_log</code> 운영 중 상시 활성 금지(개인정보 포함).",
            "<strong>Oracle 점검:</strong> <code>SELECT username, account_status FROM dba_users;</code>, 기본 계정(SCOTT·OUTLN·DBSNMP) 잠금·삭제, <code>dba_sys_privs</code>에서 <code>ANY</code> 권한 회수, <code>REMOTE_OS_AUTHENT=FALSE</code>, <code>O7_DICTIONARY_ACCESSIBILITY=FALSE</code>, <code>sec_case_sensitive_logon=TRUE</code>.",
            "<strong>Oracle 프로파일:</strong> <code>FAILED_LOGIN_ATTEMPTS 5</code>, <code>PASSWORD_LIFE_TIME 90</code>, <code>PASSWORD_REUSE_MAX 4</code>, <code>PASSWORD_VERIFY_FUNCTION</code> 지정. TNS 리스너 원격 관리(<code>admin</code>) 사용 금지.",
            "<strong>감사·로그:</strong> MySQL <code>audit_log</code> 플러그인, Oracle <code>AUDIT_TRAIL=DB,EXTENDED</code> 및 <code>DBMS_AUDIT_MGMT</code> 보관 주기, 접속 실패·DDL·권한 변경 감사, 로그 접근 권한 분리.",
            "<strong>암호화:</strong> 저장 데이터(TDE·컬럼 암호화), 전송 구간(TLS 강제, MySQL <code>require_secure_transport=ON</code>), 백업 파일 암호화, 키 관리는 DB 외부(KMS·HSM).",
            "<strong>SQLi 대비:</strong> 애플리케이션 계정에 메타데이터 조회 권한(<code>information_schema</code> 전체)을 주지 않고, 오류 메시지를 클라이언트에 노출하지 않으며, 웹 계정과 배치 계정을 분리한다."
        ]
    })

    items.append({
        "id": "prac_content_31", "type": "content", "category": "app", "category_name": "애플리케이션 보안",
        "title": "웹 취약점 진단 실무 — 점검 항목·도구·증적", "badge": "실기 단답·실무",
        "points": [
            "<strong>진단 순서:</strong> 범위·계정 확보 → 사이트맵·엔드포인트 수집(크롤링) → 입력 지점 목록화(파라미터·헤더·쿠키·업로드) → 항목별 수동 점검 → 자동 스캔 교차 확인 → 증적 정리.",
            "<strong>Burp Suite 활용:</strong> Proxy로 전 트래픽 기록 → Repeater에서 요청 1건씩 변조 → Intruder로 페이로드 자동 대입 → Scanner(Pro) 결과를 <strong>수동 재검증</strong>. <code>sqlmap -r req.txt --batch --dbs</code>는 사전 승인 범위에서만.",
            "<strong>인증·세션 점검:</strong> 로그인 후 세션 ID 재발급 여부, 쿠키 HttpOnly·Secure·SameSite, 로그아웃 후 세션 무효화, 동시 로그인·세션 만료, 비밀번호 정책·잠금, 캡차·MFA.",
            "<strong>접근통제 점검:</strong> URL 직접 접근(<code>/admin/main.do</code>), 파라미터 변조로 타 사용자 조회(IDOR), 관리자 기능 호출, HTTP 메서드(<code>PUT</code>·<code>DELETE</code>) 허용 여부, 디렉터리 리스팅.",
            "<strong>인젝션·스크립트 점검:</strong> SQLi(에러·Union·Blind), XSS(반사·저장·DOM), XXE, SSRF(<code>url=http://169.254.169.254/</code>), 명령 삽입, 경로 조작(<code>../../etc/passwd</code>), 파일 업로드(웹셸).",
            "<strong>설정·정보노출:</strong> 보안 헤더(HSTS·CSP·X-Frame-Options·X-Content-Type-Options), 서버 버전·스택트레이스 노출, 주석·백업파일(<code>.git</code>·<code>.env</code>·<code>web.config</code>), 에러 페이지, HTTPS 혼용 콘텐츠.",
            "<strong>증적 정리:</strong> 요청·응답 원문(스크린샷 + HTTP 메시지), 재현 절차 5단계, 영향(개인정보 건수·권한), 위험도(CVSS), 조치 권고(파라미터 바인딩·인코딩·권한검사)를 세트로 남긴다.",
            "<strong>주의사항:</strong> 운영 데이터 변조·대량 요청 금지, 테스트 데이터 사용, 발견 즉시 중요 취약점(인증 우회·개인정보 노출)은 담당자에게 <strong>구두 즉시 통보</strong>, 결과물은 암호화 보관."
        ]
    })

    items.append({
        "id": "prac_content_32", "type": "content", "category": "system", "category_name": "시스템 보안",
        "title": "리눅스 침해 흔적 추적 — 프로세스·크론·웹셸·계정", "badge": "실기 단답·실무",
        "points": [
            "<strong>계정 흔적:</strong> <code>awk -F: '$3==0{print $1}' /etc/passwd</code>(UID 0 계정), 최근 생성 계정 <code>ls -lt /etc/passwd</code>, <code>/etc/shadow</code> 암호 없는 계정, <code>lastlog</code>·<code>last</code>로 비정상 로그인 시간대 확인.",
            "<strong>프로세스·포트:</strong> <code>ps -ef --forest</code>, <code>ls -l /proc/[PID]/exe</code>(실행 경로), <code>/proc/[PID]/cwd</code>, 삭제된 파일 참조(<code>lsof +L1</code>), <code>ss -antp</code>·<code>netstat -antp</code>로 외부 연결, <code>/etc/services</code>에 없는 포트 리스닝.",
            "<strong>자동 실행·지속성:</strong> <code>crontab -l</code>·<code>/etc/cron.*</code>·<code>/var/spool/cron</code>, <code>/etc/rc.local</code>, <code>systemctl list-unit-files --state=enabled</code>, <code>/etc/init.d</code>, 사용자 <code>.bashrc</code>·<code>.profile</code>, <code>/etc/ld.so.preload</code>(라이브러리 후킹).",
            "<strong>웹셸 탐색:</strong> 웹 루트에서 최근 생성 파일(<code>find /var/www -mtime -7 -type f</code>), 의심 문자열(<code>grep -rEl 'eval\\(|base64_decode|system\\(|passthru' /var/www</code>), 업로드 디렉터리 실행 권한 확인.",
            "<strong>바이너리·무결성:</strong> <code>rpm -Va</code>·<code>debsums</code>로 패키지 변조 확인, <code>find / -perm -4000 -type f</code>(SUID 증가), <code>lsattr</code>로 불변 속성, Tripwire·AIDE 기준선 대조, <code>sha256sum</code>으로 의심 파일 해시 확보.",
            "<strong>로그 분석:</strong> <code>/var/log/secure</code>(SSH 인증·sudo), <code>messages</code>, <code>auth.log</code>, 웹 access/error 로그의 시간대별 급증, 실패 후 성공(4625→4624 유사 패턴), 계정 삭제·로그 초기화 흔적.",
            "<strong>은닉 탐지:</strong> <code>ps</code>와 <code>/proc</code> 목록 대조, 커널 모듈(<code>lsmod</code>·<code>/proc/modules</code>) 이상 항목, 루트킷 검사(<code>rkhunter</code>·<code>chkrootkit</code>·<code>unhide</code>), <code>ss</code>와 <code>/proc/net/tcp</code> 교차 확인.",
            "<strong>대응 순서:</strong> 라이브 응답(메모리·프로세스·연결) 기록 → 네트워크 격리 → 이미지 백업 → 계정·서비스 정리 → 재설치·복구 → 재발방지. <strong>재부팅·프로세스 종료 전에 증거를 남긴다.</strong>"
        ]
    })

    items.append({
        "id": "prac_content_33", "type": "content", "category": "law", "category_name": "디지털 포렌식 & 법률",
        "title": "디스크·메모리 포렌식 실무(dd·FTK·Volatility)", "badge": "실기 단답·실무",
        "points": [
            "<strong>이미징:</strong> <code>dcfldd if=/dev/sda of=/evidence/sda.dd hash=sha256 bs=512 conv=noerror,sync</code>, 쓰기 방지(Write Blocker) 필수, 원본은 봉인. <code>dd</code>는 <code>conv=noerror,sync</code>를 빠뜨리면 오류 구간에서 크기가 어긋난다.",
            "<strong>무결성:</strong> 원본·사본 해시 동시 기록(<code>sha256sum</code>), 해시 목록을 증거와 함께 보관, 분석은 사본으로만 수행, 연계보관성 대장에 취급자·일시·장소를 기록한다.",
            "<strong>메모리 수집:</strong> <code>LiME</code>(리눅스), <code>DumpIt</code>·<code>winpmem</code>·FTK Imager(윈도우). 메모리에는 프로세스·네트워크 연결·암호화 키·악성코드 평문이 남아 <strong>가장 먼저 수집</strong>해야 한다.",
            "<strong>Volatility 실무:</strong> <code>volatility -f mem.raw imageinfo</code>(프로파일 확인) → <code>pslist</code>·<code>psscan</code>(프로세스) → <code>netscan</code>(연결) → <code>malfind</code>(주입 코드) → <code>dlllist</code>·<code>cmdline</code>·<code>hashdump</code>. Volatility 3는 <code>vol -f mem.raw windows.pslist</code> 형식.",
            "<strong>파일시스템 분석:</strong> Autopsy·TSK(<code>fls</code>·<code>icat</code>)로 삭제 파일 복구, <code>$MFT</code>·<code>$UsnJrnl</code>으로 생성·변경 이력, 슬랙·미할당 영역, 타임라인(<code>mactime</code>)으로 사건 재구성.",
            "<strong>아티팩트:</strong> 윈도우 Prefetch·Amcache·Shimcache(실행 흔적), 이벤트 로그(EVTX), 브라우저 히스토리·캐시, USB 흔적(레지스트리 USBSTOR), <code>pagefile.sys</code>·<code>hiberfil.sys</code>, 썸네일 캐시.",
            "<strong>안티포렌식 대응:</strong> 타임스탬프 불일치(<code>stat</code>의 mtime vs ctime), 로그 공백, 대량 삭제 흔적, 암호화 볼륨, 스테가노그래피 의심 파일. 여러 아티팩트를 교차 검증해 위조를 판별한다.",
            "<strong>보고서:</strong> 수집 대상·도구·절차, 해시값, 분석 결과(타임라인), 결론, 증거 목록을 기술하고 <strong>법정 제출 요건</strong>(원본성·연속성·재현성)을 충족해야 한다."
        ]
    })

    items.append({
        "id": "prac_content_34", "type": "content", "category": "crypto", "category_name": "암호학·인증 실무",
        "title": "OpenSSL 실무 명령 — 키·CSR·인증서·TLS 점검", "badge": "실기 단답·실무",
        "points": [
            "<strong>키 생성:</strong> <code>openssl genrsa -aes256 -out priv.key 2048</code>, EC는 <code>openssl ecparam -name prime256v1 -genkey -noout -out ec.key</code>. 개인키 권한은 600으로 제한한다.",
            "<strong>CSR 생성·확인:</strong> <code>openssl req -new -key priv.key -out req.csr -subj \"/C=KR/O=Example/CN=example.com\"</code>, 내용 확인 <code>openssl req -in req.csr -noout -text</code>(SAN 항목 포함 여부 필수 확인).",
            "<strong>자체서명·서명:</strong> <code>openssl req -x509 -new -key priv.key -days 365 -out cert.crt</code>, CA 서명 <code>openssl x509 -req -in req.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out cert.crt -days 365</code>.",
            "<strong>인증서 확인:</strong> <code>openssl x509 -in cert.crt -noout -text</code>(Subject·Issuer·Validity·SAN·KeyUsage·BasicConstraints), 만료 확인 <code>openssl x509 -enddate -noout -in cert.crt</code>, 체인 검증 <code>openssl verify -CAfile ca.crt cert.crt</code>.",
            "<strong>TLS 연결 점검:</strong> <code>openssl s_client -connect example.com:443 -servername example.com</code>, 프로토콜 제한 <code>-tls1_2</code>, 취약 프로토콜 확인(<code>-tls1</code>·<code>-ssl3</code> 응답 여부), 인증서 체인 표시 <code>-showcerts</code>, 세션 재사용·암호 스위트 확인.",
            "<strong>암호 스위트·취약점:</strong> <code>openssl ciphers -v 'HIGH:!aNULL:!MD5'</code>, RC4·3DES·NULL·EXPORT 제거, TLS 1.0/1.1 비활성(2020년 이후 사실상 폐기), <code>nmap --script ssl-enum-ciphers -p 443 host</code>로 전수 점검.",
            "<strong>해시·무결성:</strong> <code>openssl dgst -sha256 file</code>, <code>openssl passwd -6</code>(SHA-512 해시), <code>openssl rand -base64 32</code>(세션키·salt 생성), <code>openssl enc -aes-256-cbc -pbkdf2 -salt -in f -out f.enc</code>.",
            "<strong>실무 함정:</strong> CN만 있고 SAN이 없으면 최신 브라우저가 거부하고, 개인키에 암호를 걸면 서비스 자동 시작 시 복호화 실패가 발생하며, 인증서 만료 자동 점검(30일 전 알림)이 운영 필수 항목이다."
        ]
    })

    items.append({
        "id": "prac_content_35", "type": "content", "category": "law", "category_name": "디지털 포렌식 & 법률",
        "title": "침해사고 분석형 서술 답안 — 로그 타임라인과 공격 재구성", "badge": "실기 단답·실무",
        "points": [
            "<strong>답안 구조:</strong> ① 사고 개요(일시·대상·영향) ② 침해 지표(IOC) ③ <strong>공격 단계별 타임라인</strong> ④ 공격자 행위·권한 ⑤ 유출 범위 ⑥ 대응·복구 ⑦ 재발방지. 타임라인은 반드시 '시각 — 근거 로그 — 해석' 3열로 정리한다.",
            "<strong>공격 단계 매핑(MITRE ATT&CK):</strong> 정찰(스캔) → 초기 침투(취약점·피싱) → 실행·지속성(크론·서비스 등록) → 권한 상승(SUID·커널 취약점) → 자격증명 탈취 → 내부 확산 → 유출·파괴.",
            "<strong>로그 대조:</strong> 방화벽(허용·차단 시각) → 웹 access/error(요청 라인·상태코드) → 인증 로그(4624·4625 / secure) → 프로세스·네트워크(EDR·NetFlow) → 파일 변경($MFT·audit). 시각은 <strong>KST로 통일</strong>하고 NTP 오차를 명시한다.",
            "<strong>전형적 서술 예:</strong> '09:12 외부 IP가 /bbs/board.php에 union select 요청(200) → 09:15 업로드 경로에 shell.php 생성 → 09:16 shell.php로 POST 명령 3회 → 09:18 DB 계정으로 대량 조회(5만 건) → 09:22 외부 443으로 1.2GB 전송'.",
            "<strong>영향 산정:</strong> 유출 항목·건수, 암호화 여부, 정보주체 범위, 서비스 중단 시간, 2차 피해 가능성. 개인정보라면 <strong>72시간 통지</strong>·1천 명 이상 신고 대상 여부를 함께 판단한다.",
            "<strong>대응 서술:</strong> 즉시 조치(계정 잠금·차단·격리), 증거 보존, 복구(백업 시점 확인), 신고(KISA 118·개인정보위), 정보주체 통지, 재발방지(취약점 조치·WAF 룰·권한 최소화·모니터링 강화).",
            "<strong>감점 회피:</strong> '해킹당했다'는 결론만 쓰면 0점에 가깝다. <strong>어떤 로그의 어떤 필드</strong>에서 무엇을 확인했는지 근거를 붙이고, 확인되지 않은 부분은 '추정'으로 명시해 단정하지 않는다.",
            "<strong>마무리 문장:</strong> '침입 경로는 OO 취약점이며, 동일 취약점이 잔존하는 시스템 N대에 대해 조치 완료, 재점검 결과 양호'로 끝맺으면 실무형 답안의 완성도가 올라간다."
        ]
    })

    return items


# (정답 키워드, 실전 출제 형태, 암기 팁)
PRACTICAL_TERMS_EXT = [
    ("SetUID 취약 파일 검색", "find / -perm -4000 -type f 2>/dev/null",
     "실기 단답: 'SetUID가 설정된 파일을 검색하는 명령어를 쓰시오' — 옵션 -perm -4000(또는 -04000)과 -type f를 함께 써야 정답.",
     "4000=SetUID, 2000=SetGID, 1000=Sticky. -perm 앞의 '-'는 '해당 비트를 포함'이라는 의미다."),
    ("umask 022 결과", "파일 644, 디렉터리 755",
     "실기 계산 문제: umask 022일 때 생성되는 파일과 디렉터리 권한. 파일 666-022=644, 디렉터리 777-022=755.",
     "파일은 실행 비트가 없으므로 666 기준, 디렉터리는 777 기준으로 계산한다."),
    ("/etc/passwd 7개 필드", "계정명:암호(x):UID:GID:설명:홈:셸",
     "실기 단답: 필드 순서와 의미, UID 0이면 root 권한이라는 점.",
     "구분자는 콜론(:). 두 번째 필드가 x면 shadow 사용, 빈 값이면 암호 없는 계정이다."),
    ("PAM 제어 플래그 4종", "required, requisite, sufficient, optional",
     "실기 단답: 4개 플래그 이름과 동작 차이(특히 required와 requisite).",
     "required=실패해도 계속(원인 은닉), requisite=즉시 중단, sufficient=성공 시 조기 종료, optional=결과에 영향 없음."),
    ("Tripwire / AIDE", "파일 무결성 검사(FIM) 도구",
     "실기 단답: 기준선(baseline) 대비 해시·권한 변경을 탐지하는 도구 이름과 목적.",
     "Tripwire는 상용 표준, AIDE는 오픈소스. '기준선'과 '해시 대조'가 정답 키워드다."),
    ("chattr +i", "파일 불변(Immutable) 속성",
     "실기 단답: root도 삭제·수정·이름변경이 불가하도록 설정하는 명령과 확인 명령(lsattr).",
     "+i는 불변, +a는 추가만 허용. chmod와 다른 계층(속성)이라는 점을 기억한다."),
    ("find -mtime -1", "최근 24시간 내 수정된 파일 검색",
     "실기 단답: 침해 시점 이후 변경된 파일을 찾는 명령. -mtime -1(1일 이내), +1(1일 초과).",
     "-mtime은 mtime(내용 변경) 기준이다. ctime은 -ctime, 접근은 -atime."),
    ("ps -ef / netstat -antp", "프로세스·포트 점검",
     "실기 단답: 현재 실행 중인 프로세스와 리스닝 포트를 PID·프로그램과 함께 확인하는 명령.",
     "-antp: a=전체, n=숫자, t=TCP, p=PID/프로그램. 최근 배포판은 ss -antp를 권장한다."),
    ("TCP 플래그 조합", "SYN=2, ACK=16, FIN=1, RST=4, PSH=8, URG=32",
     "실기 단답: 플래그별 의미와 정상 3-way(SYN → SYN+ACK → ACK) 순서.",
     "SYN+ACK는 18(2+16). 스텔스 스캔은 이 플래그 조합을 비정상으로 보내는 기법이다."),
    ("NULL / FIN / XMAS 스캔", "플래그를 비정상으로 보내는 스텔스 스캔",
     "실기 단답: 각 스캔이 보내는 플래그 조합(NULL=없음, FIN=FIN, XMAS=FIN+PSH+URG)과 윈도우에서 통하지 않는 이유.",
     "닫힌 포트는 RST, 열린 포트는 무응답(RFC 793). 윈도우는 항상 RST를 보내 판별 불가."),
    ("Snort 룰 액션 5종", "alert, log, pass, drop, reject",
     "실기 단답: 룰 헤더의 액션 목록과 drop이 동작하는 모드(inline/IPS).",
     "drop·reject는 IPS 모드에서만 유효하다. IDS 모드에서는 alert로 동작한다."),
    ("iptables 타겟", "ACCEPT, DROP, REJECT, LOG, RETURN",
     "실기 단답: DROP과 REJECT의 차이(응답 없음 vs 거부 응답), 기본 정책 설정 방법.",
     "DROP=무응답(스캔 지연), REJECT=즉시 거부 응답. 서비스 거부감을 줄이려면 REJECT가 낫다."),
    ("tcpdump 캡처 옵션", "-i, -nn, -s 0, -w, -r, -A, -X",
     "실기 단답: 특정 호스트·포트만 저장하는 명령 작성(예: tcpdump -i eth0 -nn 'tcp port 80 and host 10.0.0.5' -w a.pcap).",
     "-s 0은 전체 길이 캡처(과거 기본 68바이트 절단 방지). -w는 저장, -r은 읽기다."),
    ("nmap 옵션", "-sS, -sT, -sU, -sV, -O, -p-, -Pn, -T4",
     "실기 단답: SYN 스텔스와 TCP connect 스캔의 차이, 전체 포트 검사 옵션.",
     "-sS는 root 필요(로그 적음), -sT는 일반 사용자. -p-는 1~65535 전 범위."),
    ("SQL Injection 방어", "PreparedStatement(바인딩 변수)",
     "실기 단답: SQLi 근본 대책 1가지를 쓰라는 문제의 정답 키워드.",
     "'입력값 검증'은 보조 수단이다. 코드와 데이터를 분리하는 바인딩이 정답이다."),
    ("XSS 방어", "출력 인코딩(HTML·URL·JS 컨텍스트별) + CSP",
     "실기 단답: 저장형 XSS 대응 2가지(출력 인코딩, HttpOnly, CSP, 화이트리스트 검증).",
     "입력 시 필터링보다 '출력 시 인코딩'이 핵심이다. 컨텍스트별로 인코딩 방식이 다르다."),
    ("CSRF 방어", "CSRF 토큰 + SameSite 쿠키 + Referer 검증",
     "실기 단답: CSRF와 XSS의 차이, 방어 기법 3가지.",
     "CSRF는 사용자의 '인증된 브라우저'를 이용한다. 토큰이 세션에 묶여야 유효하다."),
    ("파일 업로드 방어", "확장자 화이트리스트 + MIME 검증 + 실행 권한 제거",
     "실기 단답: 웹셸 업로드를 막는 방법 3가지를 쓰라는 문제.",
     "확장자만 막으면 우회된다. 업로드 디렉터리의 실행 권한 제거가 가장 강력하다."),
    ("DDoS 대응", "Rate Limit, 임계치 기반 차단, CDN·스크러빙, SYN Cookie",
     "실기 단답: 대역폭 소진형과 서비스 마비형(L7) 대응의 차이.",
     "L4는 네트워크 장비·ISP 협조, L7은 WAF·캐시·커넥션 타임아웃이 중심이다."),
    ("WPA2 4-way handshake", "PMK → PTK 유도, GTK 전달, MIC 검증",
     "실기 단답: WPA2-PSK 핸드셰이크 4단계와 KRACK 취약점의 의미.",
     "PMK는 PSK+SSID+salt에서, PTK는 ANonce·SNonce·MAC으로 만든다."),
    ("IPSec ESP vs AH", "ESP=암호화+무결성(50), AH=무결성만(51)",
     "실기 단답: 두 프로토콜의 제공 기능과 프로토콜 번호, NAT 통과 가능 여부.",
     "AH는 IP 헤더 전체를 무결성 보호하므로 NAT를 통과하지 못한다."),
    ("SSL/TLS 핸드셰이크", "ClientHello → ServerHello → 인증서 → 키교환 → Finished",
     "실기 단답: 핸드셰이크 순서와 세션키 합성(ECDHE) 개념, TLS 1.3의 1-RTT.",
     "인증서 검증 → 키 합의 → Finished(암호화 시작) 순서. TLS 1.3은 축약되었다."),
    ("전자서명 절차", "송신자: 해시 → 개인키 서명 / 수신자: 공개키 검증",
     "실기 단답: 서명 생성·검증 순서, 보장 3요소(무결성·인증·부인방지).",
     "기밀성은 보장하지 않는다. 암호화는 수신자 공개키로 별도 수행한다."),
    ("해시 vs 암호화 vs 인코딩", "해시=복호화 불가, 암호화=키로 복호화, 인코딩=형식 변환",
     "실기 단답: 세 개념의 차이와 용도(무결성·기밀성·전송).",
     "Base64는 암호화가 아니다. 누구나 디코딩할 수 있다."),
    ("대칭키 vs 공개키", "n(n-1)/2 vs 2n 키 개수",
     "실기 계산 문제: 참여자 n명일 때 필요한 키 개수. 대칭키 n(n-1)/2, 공개키 2n.",
     "10명이면 45개 vs 20개. 대칭키가 빠르고, 공개키는 키 배분 문제를 해결한다."),
    ("RTO / RPO", "RTO=복구 시간, RPO=데이터 유실 시점",
     "실기 단답: 두 지표의 정의와 값이 작을수록 비용이 증가한다는 점.",
     "RTO=Time(시간), RPO=Point(시점). MTD는 최대 허용 중단 시간이다."),
    ("SLE / ALE 계산", "SLE=자산가치×노출계수, ALE=SLE×ARO",
     "실기 계산 문제: 자산 1억·노출계수 40%·연 2회 발생 → SLE 4천만, ALE 8천만.",
     "ALE는 '연간' 손실이다. 대책 비용과 비교해 타당성(ROI)을 판단한다."),
    ("개인정보 유출 신고", "72시간 통지, 1천 명 이상 신고",
     "실기 단답: 유출 인지 후 통지 시한과 신고 대상 기관·기준.",
     "기산점은 '인지 시점'이다. 5만 명 이상 민감정보 유출은 조사·신고 요건이 강화된다."),
    ("정보보호 관리체계 PDCA", "Plan-Do-Check-Act (수립-운영-점검-개선)",
     "실기 단답: ISMS·ISMS-P 인증의 4단계 사이클과 영역별 기준 수(16·64·22).",
     "P(정책·위험평가) D(대책 구현) C(내부감사·법적 검토) A(개선)."),
    ("디지털 포렌식 5원칙", "정당성·재현성·신속성·연계보관성·무결성",
     "실기 단답: 5원칙 나열과 휘발성 순서(레지스터→RAM→디스크).",
     "연계보관성(Chain of Custody)은 취급자·일시·장소 기록, 무결성은 해시로 증명한다."),
]


# 기존 30선(단문 정의)에 [출제 형태]·[암기 팁]을 붙여 실기 족보 밀도를 보강
PRACTICAL_ENRICH = {
    "find (-perm -4000)": ("실기 단답: 'SetUID 파일을 찾는 명령어' 또는 'SUID 취약 파일 전수조사' 문제로 나온다.",
                          "-perm -4000의 '-'를 빠트리면 4000과 정확히 일치하는 파일만 찾게 된다. 2>/dev/null로 권한 오류를 숨긴다."),
    "netstat (-antp)": ("실기 단답: '포트·프로세스 확인 명령' 또는 '비정상 리스닝 포트 찾기' 문제.",
                        "-a 전체, -n 숫자, -t TCP, -p PID. 최근에는 ss -antp를 쓰지만 시험은 netstat이 기준이다."),
    "umask (027)": ("실기 계산: umask 027일 때 파일 640, 디렉터리 750을 구하는 문제.",
                    "파일 666-027=640, 디렉터리 777-027=750. KISA 권고 umask는 022 또는 027이다."),
    "chattr (+i / -i)": ("실기 단답: root도 삭제 불가하게 만드는 명령, 확인은 lsattr.",
                         "+i 불변, +a 추가만 허용. chmod(권한)와 chattr(속성)는 다른 계층이다."),
    "lastlog (/var/log/lastlog)": ("실기 단답: 계정별 최근 로그인 시각·IP를 확인하는 명령과 로그 파일 경로.",
                                   "last(wtmp, 전체 이력)·who(utmp, 현재)·lastb(btmp, 실패)·lastlog(계정별 최종) 4종을 세트로 외운다."),
    "tcpdump": ("실기 단답: 특정 호스트·포트 패킷을 파일로 저장하는 명령 작성.",
                "-nn(이름 해석 금지), -s 0(전체 캡처), -w(저장), -r(읽기), -A(ASCII). BPF 필터는 and/or로 연결한다."),
    "icacls": ("실기 단답: 윈도우 NTFS ACL 확인·부여 명령(Linux chmod/chown 대응).",
               "/grant:r, /remove, /inheritance:r 옵션. 공유 권한과 NTFS 권한 중 더 제한적인 것이 적용된다."),
    "distance (Snort)": ("실기 단답: content 매칭 이후 상대 위치 지정 옵션의 의미.",
                         "offset은 패킷 시작 기준, distance는 직전 매칭 끝 기준, within은 distance 이후 탐색 범위다."),
    "within (Snort)": ("실기 단답: distance와 짝을 이루는 탐색 범위 제한 옵션.",
                       "'distance로 출발점, within으로 도착 범위'로 묶어 기억한다."),
    "iptables REJECT": ("실기 단답: DROP과 REJECT의 차이, --reject-with 옵션.",
                        "DROP은 무응답(지연), REJECT는 즉시 거부 응답(ICMP unreachable·tcp-reset)이다."),
    "PreparedStatement": ("실기 단답: SQLi 근본 대책 키워드로 반드시 등장한다.",
                          "'사전 컴파일 + 파라미터 바인딩'이 정답 문구. 입력 검증·이스케이프는 보조 수단이다."),
    "SameSite=Lax": ("실기 단답: CSRF 방어를 위한 쿠키 속성 3값(Strict·Lax·None).",
                     "Lax는 최상위 GET 이동만 허용, Strict는 외부 진입 시 로그인 풀림, None은 Secure 필수다."),
    "Strict-Transport-Security (HSTS)": ("실기 단답: SSL Stripping 방어 헤더 이름과 max-age 설정.",
                                         "max-age=31536000; includeSubDomains; preload. 최초 평문 요청은 preload로만 막힌다."),
    "Content-Security-Policy (CSP)": ("실기 단답: XSS 방어 헤더와 default-src·script-src 지시자.",
                                       "unsafe-inline을 허용하면 XSS 방어 효과가 사라진다. frame-ancestors는 클릭재킹 방어다."),
    "Volatility": ("실기 단답: 메모리 덤프 분석 도구 이름과 대표 플러그인(pslist·netscan·malfind).",
                   "메모리는 휘발성이 가장 높아 최우선 수집 대상이다. imageinfo로 프로파일을 먼저 확인한다."),
    "SBOM": ("실기 단답: 공급망 보안 요소(SPDX·CycloneDX)와 취약점 관리 연계.",
             "'소프트웨어 자재 명세서'가 정답 키워드. Log4j 사고 이후 의무화 논의가 확대되었다."),
    "SOAR": ("실기 단답: SIEM·SOAR·EDR의 역할 차이 구분.",
             "SIEM=수집·상관분석, SOAR=플레이북 자동화, EDR=단말 행위 탐지·격리. 세 글자 약어의 역할을 구분한다."),
    "EDR": ("실기 단답: 단말 위협 탐지·대응 솔루션의 기능 3가지.",
            "행위 모니터링·탐지·격리·롤백. 백신(시그니처)과 달리 행위 기반이라는 점이 핵심이다."),
    "SPAN (Port Mirroring)": ("실기 단답: 스위치 환경에서 IDS가 패킷을 보는 방법.",
                              "미러링 포트·TAP. 허브 환경이 아니면 스니핑이 불가능하므로 SPAN이 필요하다."),
    "MITRE ATT&CK": ("실기 서술: 침해사고 분석 시 공격 단계를 매핑하는 프레임워크.",
                     "전술(Tactic, 왜) → 기술(Technique, 어떻게) → 절차(Procedure, 실제 사례) 계층 구조다."),
    "Perfect Forward Secrecy (PFS)": ("실기 단답: ECDHE 사용 이유, 서버 키 유출 시 과거 트래픽 보호.",
                                      "세션키를 일회성으로 생성·폐기하는 특성. RSA 키 교환은 PFS를 제공하지 않는다."),
    "auditctl": ("실기 단답: 파일 감시 규칙 등록 명령(-w -p -k).",
                 "-p wa(쓰기·속성변경), -k 키. 규칙은 /etc/audit/rules.d/에 영구 저장해야 한다."),
    "fail2ban": ("실기 단답: SSH 무차별 대입 자동 차단 도구와 연동 방화벽.",
                 "/etc/fail2ban/jail.local의 maxretry·bantime·findtime 3개 값이 설정 핵심이다."),
    "SecureRandom": ("실기 단답: 예측 가능한 난수 사용의 위험과 안전한 난수 클래스.",
                     "java.util.Random은 LCG로 시드 예측이 가능하다. 세션 ID·salt에는 SecureRandom을 쓴다."),
    "Chain of Custody (연계보관성)": ("실기 단답: 포렌식 5원칙 중 증거 능력과 직결되는 원칙.",
                                     "취급자·일시·장소·이동 경로를 기록. 해시(무결성)와 함께 증거 능력의 두 축이다."),
    "Open Redirect": ("실기 단답: 피싱에 악용되는 리다이렉트 취약점과 대응.",
                      "returnUrl·redirect 파라미터를 화이트리스트로 검증. 302 응답의 Location 조작이 핵심이다."),
    "Tripwire": ("실기 단답: 파일 무결성 검사 도구와 기준선(Baseline) 개념.",
                 "SHA-256 기준선 저장 → 주기적 재수집 → 대조·경보. AIDE는 오픈소스 대안이다."),
    "Order of Volatility": ("실기 단답: 휘발성 높은 순서대로 수집하는 원칙(RFC 3227).",
                            "레지스터·캐시 → RAM → 네트워크 연결 → 디스크 → 원격 로그 → 백업 순."),
    "CISO 겸직금지": ("실기 단답: CISO 겸직 제한의 규모 요건과 근거 법령(정보통신망법).",
                      "자산 5조원 이상 또는 5천억원 이상 + ISMS 의무 대상. CIO·개인정보보호책임자 겸직 제한을 함께 본다."),
    "Zero Trust (Never Trust, Always Verify)": ("실기 서술: 경계 보안의 한계와 제로트러스트 3원칙.",
                                               "지속 검증·최소 권한·침해 가정. 내부망도 신뢰하지 않는 것이 핵심이다."),
}


def get_extra_practical_terms():
    items = []
    for name, keyword, exam, tip in PRACTICAL_TERMS_EXT:
        cat = "system"
        if any(k in name for k in ["TCP", "Snort", "tcpdump", "nmap", "WPA", "IPSec", "SSL"]):
            cat = "network"
        elif any(k in name for k in ["SQL", "XSS", "CSRF", "파일 업로드"]):
            cat = "app"
        elif any(k in name for k in ["해시", "대칭키", "전자서명"]):
            cat = "crypto"
        elif any(k in name for k in ["RTO", "SLE", "개인정보", "관리체계", "포렌식"]):
            cat = "law"
        items.append({
            "id": "prac_term_ext_" + str(len(items) + 31).zfill(2),
            "type": "term",
            "category": cat,
            "category_name": "실기 단답형 용어 (핵심 족보)",
            "title": f"[실기 단답] {name}",
            "term": name,
            "badge": "단답형 족보",
            "points": [
                f"<strong>정답 키워드:</strong> {keyword}",
                f"<strong>출제 형태:</strong> {exam}",
                f"<strong>암기 팁:</strong> {tip}"
            ]
        })
    return items

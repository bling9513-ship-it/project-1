# -*- coding: utf-8 -*-
"""
practical_summary.py
2026 이기적 정보보안기사 필기+실기 올인원 3권 실기 핵심 실무 가이드 & 시큐어코딩
- PART 07 실기 단답형 핵심 명령어 및 설정 족보
- PART 08 실무형 침해사고 분석 & 시큐어코딩 47개 가이드
"""

def get_practical_summary():
    return {
        "title": "2026 이기적 정보보안기사 실기 핵심 실무 가이드 & 시큐어코딩 (3권 실기서 전편)",
        "sections": [
            {
                "title": "PART 07 실기 단답형 핵심 명령어 및 보안 설정 족보",
                "topics": [
                    {
                        "name": "리눅스/유닉스 핵심 점검 명령어",
                        "points": [
                            "find / -perm -4000 -type f: SetUID가 부여된 파일을 검색하여 권한 상승 취약점 점검.",
                            "netstat -antp: 활성 소켓, 포트 번호(숫자), TCP 연결 상태, 실행 중인 PID 및 프로그램 확인.",
                            "find / -mtime -1: 최근 24시간 이내에 수정(Modify)된 파일 검색 (침해사고 초기 분석).",
                            "chattr +i [파일]: root를 포함하여 파일의 수정, 삭제, 이름 변경을 원천 차단(불변 속성).",
                            "lastlog: /var/log/lastlog 바이너리 파일을 읽어 계정별 최근 접속 시간과 IP 확인.",
                            "sha256sum [파일]: 무결성 검증을 위한 SHA-256 해시값 생성 및 대조."
                        ]
                    },
                    {
                        "name": "주요 보안 설정 파라미터",
                        "points": [
                            "umask 027: 기본 권한 디렉토리 750, 파일 640 생성 설정으로 타인(Other) 접근 차단.",
                            "sshd_config: 'PermitRootLogin no' (root 원격 접속 차단), 'PasswordAuthentication no' (공개키 인증 강제).",
                            "httpd.conf: 'Options -Indexes' (디렉토리 리스팅 제거), 'ServerTokens Prod' (서버 정보 은닉).",
                            "/etc/hosts.allow & hosts.deny: TCP Wrapper 설정 파일. allow 파일이 우선 적용됨.",
                            "/etc/login.defs: 'PASS_MAX_DAYS 90' (최대 유효기간), 'PASS_MIN_DAYS 1' (최소 변경주기)."
                        ]
                    }
                ]
            },
            {
                "title": "PART 08 실무형 침해사고 분석 & 시큐어코딩 47개 핵심",
                "topics": [
                    {
                        "name": "웹 침해사고 로그 분석 및 Snort 규칙 작성",
                        "points": [
                            "SQL 인젝션 로그: access.log 내 'UNION SELECT', 'OR 1=1', 'information_schema', 'sleep()' 패턴 분석.",
                            "경로 조작(Path Traversal) 로그: '%2e%2e%2f', '../../', 'etc/passwd' 문자열 디코딩 및 탐지.",
                            "SSH 무차별 대입 로그: secure 로그 내 동일 IP의 단시간 대량 'Failed password' 연속 이력 식별.",
                            "Snort 룰 작성 표준: alert tcp any any -> 192.168.1.100 80 (msg:\"WebShell Detected\"; content:\"cmd.jsp\"; nocase; sid:1000001;)"
                        ]
                    },
                    {
                        "name": "SW 개발보안 (시큐어코딩) 47개 보안약점 핵심 가이드",
                        "points": [
                            "SQL Injection: 파라미터 바인딩을 지원하는 PreparedStatement 사용 (Statement 결합 금지).",
                            "XSS 방어: HTML Entity 치환 (&lt;, &gt;, &quot;, &amp;) 및 JSTL escapeXml=\"true\" 설정.",
                            "파일 업로드: 화이트리스트 확장자 검증, 난수화된 파일명(UUID) 저장, 업로드 디렉토리 실행(No-Exec) 권한 제거.",
                            "안전한 난수 생성: 취약한 java.util.Random 대신 java.security.SecureRandom 클래스 사용.",
                            "패스워드 암호화: 고속 해시(MD5/SHA) 단독 사용 금지, PBKDF2/bcrypt/Argon2 기반 솔트 및 키 스트레칭 적용.",
                            "입력값 경로 검증: 파일 다운로드 시 ../ 필터링 및 getCanonicalPath()를 통한 디렉토리 격리 검증."
                        ]
                    }
                ]
            }
        ]
    }

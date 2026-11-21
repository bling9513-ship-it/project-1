# -*- coding: utf-8 -*-
"""한글 한 칸 변신(hangul.html) — 단어 사다리 퍼즐 빌더.

규칙 요약
  · 두 글자 단어에서 매 턴 한 음절의 자모(초성·중성·종성) 하나 또는 한 글자(음절)만
    바꿔 사전에 있는 단어를 거쳐 목표 단어까지 도달한다.
  · 이동 수가 최소 이동 수(par, BFS 최단 거리)와 같으면 별 3개, 2수 이내 초과면 별 2개,
    그보다 많으면 별 1개. 힌트를 쓰지 않으면 퍼펙트 배지.
  · 일일 14판( KST 날짜 순환) + 자유 연습 12판(입문·중급·고급 각 4판)을 미리 만들고,
    각 판의 par 를 사전 그래프 BFS 로 계산해 데이터에 심는다.
  · 기록은 localStorage(hangul_ladder_stats_v1)에만 저장하며, 일일 기록은 판을 시작한
    날짜(dayKey)에 귀속해 자정을 넘겨도 초기화되지 않는다.
"""
import itertools
import json
import os
from collections import deque
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "hangul_data.json")
HANGUL_HTML = os.path.join(BASE_DIR, "hangul.html")
KST = timezone(timedelta(hours=9))

DAILY_COUNT = 14

# ---------------------------------------------------------------- 사전
# 두 글자 한국어 단어(명사·부사·일부 용언 활용형). 게임 규칙상 모든 단어는 두 음절이다.
WORD_SOURCE = """
가방 가위 가구 가스 가지 가죽 가면 가슴 가을 가족 가게 가수 가사 가시 가로 가루
각도 간판 갈비 감기 감자 강물 개미 거미 거울 거실 건물 검사 겨울 계단 고기 고추
골목 공원 공기 공책 과자 과일 관심 광고 교실 교통 구름 구두 구역 국수 군인 굴뚝
극장 근육 글자 기차 기사 기억 기온 기름 김치 김밥 까치 꼬리 꽃병 꿀벌
나무 나비 나라 나이 나물 낙엽 난로 날개 날씨 남자 남매 냄비 냉면 노래 노을 노트
농부 눈물 눈썹 다리 단추 달력 달빛 담장 대답 대문 대추 도시 도로 도마 도움 독서
동네 동물 동생 두부 등산 등불 딸기 라면 로봇 마늘 마당 마음 마을 만두 매미 먹이
멸치 명함 모기 모래 모자 목욕 무릎 물건 물감 미역 미용 미소 미터
바늘 바다 바람 바위 바지 박수 반지 반찬 발목 발음 방문 배우 배추 백성 버스 번개
벌레 벽돌 별빛 병원 보리 봉투 부엌 부두 북극 분필 불꽃 불빛
비누 빵집 사과 사람 사슴 사진 사탕 산길 산불 상자 새벽 색깔 생선 서리 선물 설탕
성냥 소금 소리 손님 손목 수건 수박 수업 시계 시장 시내 시민 식당 식물 신발 신문
실내 실수 심장 싸움 아들 아내 아침 아이 안개 안경 안방 약국 양말 양파 어깨 언어
얼굴 엄마 여우 여름 여행 연필 열매 열쇠 염소 영화 옆집 예산 오이 오후 오전 오늘
내일 어제 모레 온도 올해 옷장 왕자 외투 요리 우산 우유 운동 운전 울음 웃음
월급 유리 은행 음식 음악 의자 의사 이불 이마 이웃 이름 인형 일기 잉크 자매 자리
잔디 장갑 장미 재킷 저녁 저울 전구 전등 전화 절반 점심 정원 종이 좌석 주말 주방
주인 주차 준비 지갑 지도 지붕 지하 지구 지식 질문 차표 창문 창고 채소 책상 책방
천장 철도 청소 체조 축구 치마 치약 칫솔 친구 칠판 침대 커피 코트 콧물 탁자 태양
택시 토끼 퇴근 트럭 파도 파리 편지 평화 포도 표정 풍경 피부 피자 필통
하늘 하루 학교 학생 한강 항구 해변 행복 향기 허리 현관 형제 호수 호박 홍수 화가
회사 회의 휴가 휴지
보안 암호 해킹 공격 방어 침해 유출 복구 백업 서버 파일 폴더 코드 버그 패치 로그
권한 인증 접속 차단 탐지 분석 대응 예방 점검 신고 경보 경계 위험 안전 사고 피해
손실 책임 의무 권리 자유 진실 거짓 소문 정답 오답 문제 해답 시험 공부 숙제 강의
발표 보고 계약 거래 결제 환불 할인 가격 비용 이익 손해 자금 저축 투자 대출 이자
세금 연봉 퇴직 채용 면접 이력 경력 신입 승진 출근 야근 회식 동료 상사 부서
목표 계획 약속 규칙 질서 정의 전쟁 승리 패배 실패 성공 노력 열정 용기 지혜 정보
사랑 우정 슬픔 분노 기쁨 희망 생각 감정 느낌 사실
봄날 밤낮 정오 자정 주중 평일 휴일 연휴 명절 설날 추석 생일 매일 항상 가끔 자주
지금 방금 아까 이따 나중 먼저 다시 아직 벌써
습도 강수 소나기 장마 태풍 가뭄 폭설 한파 폭염 천둥 햇빛 달빛 일출 일몰
밥상 국물 찌개 전골 조림 구이 무침 볶음 튀김 떡국 콜라 맥주 소주 와인 생수 참외
후추 간장
밥솥 수저 식탁 매트 커튼 책장 서랍 선반 화분 샴푸 욕조 변기 셔츠 조끼 구두
벨트 해커 보관 저장 삭제 수정 편집 검색 접근 허가 금지 규정 정책 대책
보상 배상 법원 판결 증거 수사 경찰 소방 구급 구조 대피 화재 지진 사무 출장 결재
업무 일정 팀장 과장 부장 사장 회장 대리 사원 직원 교사 교수 성적 학점 졸업
입학 전공 학습 도서 서점 약사 주사 수술 치료 진찰 건강 체력 산책 수영 야구 농구
배구 골프 눈썹 입술 손등 발등 기침 계곡 폭포 들판 하천 행성 은하 혜성 유성 일식
월식 등대 어선 연어 갈치 조기 명태 대구 광어 문어 낙지 전복 새우 조개 오리 거위
참새 제비 늑대 사자 기린 낙타 돼지 절망 설렘 감동 용서 화해 갈등 다툼
"""

CHO = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
JUNG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ",
        "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

# (id, 표시 제목, 시작 단어, 목표 단어) — par 는 아래에서 BFS 로 계산한다.
DAILY_SPECS = [
    ("d01", "서재 정리", "의자", "책상"),
    ("d02", "내일로", "오늘", "내일"),
    ("d03", "집수리", "창문", "지붕"),
    ("d04", "과일 가게", "사과", "포도"),
    ("d05", "방어 훈련", "공격", "방어"),
    ("d06", "파도와 모래", "파도", "모래"),
    ("d07", "아침 안개", "안개", "구름"),
    ("d08", "시험 전날", "공부", "시험"),
    ("d09", "점심 메뉴", "국수", "김치"),
    ("d10", "병원 가는 길", "병원", "약국"),
    ("d11", "현관 앞", "신발", "양말"),
    ("d12", "계절 바꾸기", "겨울", "여름"),
    ("d13", "졸업 후", "학교", "회사"),
    ("d14", "휴가 첫날", "휴가", "여행"),
]

# (id, 난이도, 표시 제목, 시작 단어, 목표 단어)
PRACTICE_SPECS = [
    ("p-b1", "입문", "첫 변신", "바다", "하늘"),
    ("p-b2", "입문", "환승", "버스", "택시"),
    ("p-b3", "입문", "아침 이불", "이불", "침대"),
    ("p-b4", "입문", "복구 작업", "유출", "복구"),
    ("p-m1", "중급", "분기 목표", "목표", "계획"),
    ("p-m2", "중급", "회의 정리", "회의", "보고"),
    ("p-m3", "중급", "카페 사다리", "커피", "우유"),
    ("p-m4", "중급", "나갈 준비", "지갑", "열쇠"),
    ("p-a1", "고급", "침해 탐지", "해킹", "탐지"),
    ("p-a2", "고급", "신고 접수", "경찰", "소방"),
    ("p-a3", "고급", "밤샘", "저녁", "새벽"),
    ("p-a4", "고급", "해산물 사다리", "조개", "문어"),
]

def two_syllable_words():
    """두 음절 한글 단어만 남겨 정렬한다."""
    out = []
    for word in WORD_SOURCE.split():
        if len(word) != 2:
            continue
        if not all(0xAC00 <= ord(ch) <= 0xD7A3 for ch in word):
            continue
        out.append(word)
    return sorted(set(out))


def build_graph(words):
    """한 음절만 다른 두 단어를 잇는 무향 그래프."""
    buckets = {}
    for word in words:
        for index, syllable in enumerate(word):
            buckets.setdefault((index, syllable), []).append(word)
    graph = {word: set() for word in words}
    for group in buckets.values():
        for left, right in itertools.combinations(group, 2):
            graph[left].add(right)
            graph[right].add(left)
    return graph


def distance(graph, start, goal):
    if start == goal:
        return 0
    seen = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in graph[current]:
            if nxt in seen:
                continue
            seen[nxt] = seen[current] + 1
            if nxt == goal:
                return seen[nxt]
            queue.append(nxt)
    return -1


def rival_ms(par):
    """기준 라이벌 기록(가상) — 최소 이동 + 이동당 11초 + 준비 12초."""
    return 12000 + par * 11000


def build_data(now=None):
    words = two_syllable_words()
    word_set = set(words)
    graph = build_graph(words)

    daily = []
    for puzzle_id, title, start, goal in DAILY_SPECS:
        assert start in word_set and goal in word_set, (puzzle_id, start, goal)
        par = distance(graph, start, goal)
        assert par >= 2, (puzzle_id, start, goal, par)
        assert graph[start] and graph[goal], puzzle_id
        daily.append({
            "id": puzzle_id,
            "title": title,
            "start": start,
            "goal": goal,
            "par": par,
            "rivalMs": rival_ms(par),
        })

    practice = []
    for puzzle_id, level, title, start, goal in PRACTICE_SPECS:
        assert start in word_set and goal in word_set, (puzzle_id, start, goal)
        par = distance(graph, start, goal)
        assert par >= 2, (puzzle_id, start, goal, par)
        practice.append({
            "id": puzzle_id,
            "level": level,
            "title": title,
            "start": start,
            "goal": goal,
            "par": par,
            "rivalMs": rival_ms(par),
        })

    pairs = [(item["start"], item["goal"]) for item in daily + practice]
    assert len(pairs) == len(set(pairs)), "중복된 시작·목표 쌍이 있습니다"

    generated = (now or datetime.now(KST)).strftime("%Y-%m-%d %H:%M KST")
    # 글자 모드 팔레트: 사전에 실제로 등장하는 모든 음절을 초성별로 묶는다.
    everything = sorted({ch for word in words for ch in word})
    groups = {cho: [] for cho in CHO}
    for syllable in everything:
        code = ord(syllable) - 0xAC00
        groups[CHO[code // 588]].append(syllable)
    return {
        "generated": generated,
        "words": words,
        "cho": CHO,
        "jung": JUNG,
        "jong": JONG,
        "syllableGroups": groups,
        "syllables": everything,
        "daily": daily,
        "practice": practice,
    }


CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;

      --bg-page: #f8fafc;
      --bg-surface: #ffffff;
      --bg-subtle: #f1f5f9;
      --bg-muted: #e2e8f0;

      --border-subtle: #f1f5f9;
      --border-default: #e2e8f0;
      --border-strong: #cbd5e1;

      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;

      --accent-primary: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;

      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;
      --warn-bg: #fffbeb; --warn-text: #b45309; --warn-border: #fde68a;
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
    }

    [data-theme="dark"] {
      --bg-page: #09090b;
      --bg-surface: #18181b;
      --bg-subtle: #27272a;
      --bg-muted: #3f3f46;

      --border-subtle: #1f1f23;
      --border-default: #27272a;
      --border-strong: #3f3f46;

      --text-primary: #f4f4f5;
      --text-secondary: #a1a1aa;
      --text-muted: #71717a;

      --accent-primary: #3b82f6;
      --accent-hover: #60a5fa;
      --accent-subtle: rgba(59, 130, 246, 0.15);

      --ok-bg: rgba(16, 185, 129, 0.12);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.32);
      --warn-bg: rgba(245, 158, 11, 0.12); --warn-text: #fcd34d; --warn-border: rgba(245, 158, 11, 0.32);
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-page);
      color: var(--text-primary);
      line-height: 1.5;
      letter-spacing: -0.02em;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    a { color: inherit; }

    .navbar { position: sticky; top: 0; z-index: 50; background: var(--bg-surface); border-bottom: 1px solid var(--border-default); }
    .nav-container { max-width: 1360px; margin: 0 auto; padding: 0 20px; height: 60px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
    .brand-logo-img { width: 28px; height: 28px; border-radius: 7px; object-fit: cover; display: block; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15); flex-shrink: 0; }
    .brand-name { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; white-space: nowrap; }
    .update-meta { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); white-space: nowrap; }
    .live-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block; flex-shrink: 0; }
    .icon-btn { width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; cursor: pointer; text-decoration: none; }
    .icon-btn:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .hg-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 72px; }

    .hg-hero { margin-bottom: 13px; }
    .hg-pill {
      display: inline-block;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 8px;
      margin-bottom: 8px;
    }
    .hg-hero h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.035em; }
    .hg-hero p { margin-top: 5px; font-size: 13px; color: var(--text-secondary); max-width: 700px; }

    .hg-shell { display: grid; grid-template-columns: 324px minmax(0, 1fr); gap: 16px; align-items: start; }
    .hg-rail { display: flex; flex-direction: column; gap: 12px; position: sticky; top: 76px; }

    .hg-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 16px;
      padding: 13px 14px;
      box-shadow: var(--card-shadow);
      min-width: 0;
    }
    .hg-card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
    .hg-card-head h2 { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; }
    .hg-card-head span { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; white-space: nowrap; }
    .hg-foot { margin-top: 9px; font-size: 10px; line-height: 1.45; color: var(--text-muted); }

    .hg-seg { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 11px; }
    .hg-seg-btn {
      border: 0; background: transparent; border-radius: 8px; padding: 8px 4px;
      font-family: inherit; font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary); cursor: pointer; white-space: nowrap;
      transition: background-color 160ms ease, color 160ms ease;
    }
    .hg-seg-btn:hover { color: var(--text-primary); }
    .hg-seg-btn.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }
    .hg-seg-small .hg-seg-btn { padding: 6px 10px; font-size: 11.5px; }

    .hg-meter { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 11px; font-size: 11.5px; color: var(--text-secondary); }
    .hg-meter strong { font-size: 16px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .hg-meter span { white-space: nowrap; }
    .hg-remain { font-size: 11px; font-weight: 600; color: var(--accent-primary); }
    .hg-remain.is-done { color: var(--ok-text); }

    .hg-stars { display: flex; align-items: center; gap: 4px; margin-top: 8px; }
    .hg-star { width: 19px; height: 19px; flex-shrink: 0; color: var(--bg-muted); transition: color 200ms ease, transform 200ms ease; }
    .hg-star.is-on { color: #f59e0b; }
    .hg-star.is-pop { animation: hgStarPop 320ms ease; }
    .hg-stars-big { justify-content: center; gap: 7px; margin: 8px 0 4px; }
    .hg-stars-big .hg-star { width: 30px; height: 30px; }

    .hg-streakrow { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 9px; }
    .hg-chip {
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 10.5px; font-weight: 700; letter-spacing: -0.01em;
      color: var(--accent-primary); background: var(--accent-subtle);
      border: 1px solid var(--border-default); border-radius: 999px; padding: 3px 8px;
      font-variant-numeric: tabular-nums; white-space: nowrap;
    }
    .hg-chip.is-hot { color: var(--warn-text); background: var(--warn-bg); border-color: var(--warn-border); }
    .hg-chip.is-over { color: var(--no-text); background: var(--no-bg); border-color: var(--no-border); }
    .hg-streak-best { font-size: 10px; color: var(--text-muted); white-space: nowrap; }

    .hg-daybadge {
      display: block; margin-top: 8px; padding: 6px 8px;
      font-size: 10.5px; line-height: 1.4; color: var(--warn-text);
      background: var(--warn-bg); border: 1px solid var(--warn-border); border-radius: 8px;
    }

    /* ----- 게임 방법(한 번만 움직이는 데모) ----- */
    .hg-guide-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .hg-guide-head h2 { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; }
    .hg-guide-toggle {
      border: 0; background: transparent; font-family: inherit; font-size: 11px; font-weight: 600;
      color: var(--accent-primary); cursor: pointer; padding: 4px 0 4px 8px; white-space: nowrap;
    }
    .hg-guide-body { margin-top: 8px; }
    .hg-demo {
      position: relative; padding: 12px 10px 9px;
      border: 1px solid var(--border-default); border-radius: 12px; background: var(--bg-page);
    }
    .hg-demo-tiles { display: flex; align-items: center; justify-content: center; gap: 7px; }
    .hg-demo-tile {
      display: inline-flex; align-items: center; justify-content: center;
      width: 46px; height: 46px; border-radius: 12px;
      border: 1px solid var(--border-strong); background: var(--bg-surface);
      font-size: 21px; font-weight: 700; letter-spacing: -0.03em;
      transition: border-color 160ms ease, background-color 160ms ease;
    }
    .hg-demo-tile.is-target { border-color: var(--accent-primary); background: var(--accent-subtle); color: var(--accent-primary); }
    .hg-demo-tile.is-pop { animation: hgPop 380ms ease; }
    .hg-demo-arrow { font-size: 12px; color: var(--text-muted); }
    .hg-demo-steps { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 9px; }
    .hg-demo-step {
      display: inline-flex; align-items: center; gap: 3px;
      font-size: 9px; font-weight: 600; color: var(--text-muted);
      padding: 2px 5px; border-radius: 999px; border: 1px solid transparent;
      transition: color 160ms ease, background-color 160ms ease, border-color 160ms ease;
    }
    .hg-demo-step.is-on { color: var(--accent-primary); background: var(--accent-subtle); border-color: var(--border-default); }
    .hg-guide-note { margin-top: 7px; font-size: 10px; line-height: 1.5; color: var(--text-muted); min-height: 30px; }
    .hg-guide-foot { margin-top: 6px; font-size: 10px; line-height: 1.5; color: var(--text-muted); }
    .hg-guide-replay {
      margin-top: 7px; width: 100%; border: 1px solid var(--border-default); border-radius: 9px;
      background: var(--bg-surface); color: var(--accent-primary);
      font-family: inherit; font-size: 11px; font-weight: 600; padding: 7px 8px; cursor: pointer;
    }
    .hg-guide-replay:hover { background: var(--bg-subtle); border-color: var(--border-strong); }

    /* ----- 기록 ----- */
    .hg-record-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px; }
    .hg-record-grid dt { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
    .hg-record-grid dd { font-size: 14px; font-weight: 700; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .hg-record-list { list-style: none; display: flex; flex-direction: column; gap: 5px; margin-top: 9px; }
    .hg-record-list li { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 11px; color: var(--text-secondary); }
    .hg-record-list b { font-weight: 600; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .hg-record-empty { font-size: 10.5px; color: var(--text-muted); }

    /* ----- 자유 연습 ----- */
    .hg-practice-group + .hg-practice-group { margin-top: 10px; }
    .hg-practice-label { font-size: 10px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.02em; margin-bottom: 5px; }
    .hg-practice-list { display: flex; flex-direction: column; gap: 5px; }
    .hg-practice-btn {
      display: flex; align-items: center; justify-content: space-between; gap: 8px;
      width: 100%; text-align: left; border: 1px solid var(--border-default); border-radius: 9px;
      background: var(--bg-surface); padding: 7px 9px; cursor: pointer; font-family: inherit;
    }
    .hg-practice-btn:hover { background: var(--bg-subtle); border-color: var(--border-strong); }
    .hg-practice-btn.is-active { border-color: var(--accent-primary); background: var(--accent-subtle); }
    .hg-practice-title { font-size: 11.5px; font-weight: 600; color: var(--text-primary); }
    .hg-practice-meta { font-size: 9.5px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    /* ----- 보드 ----- */
    .hg-board { padding: 14px 15px 13px; }
    .hg-board-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
    .hg-board-title { min-width: 0; }
    .hg-board-title h2 { font-size: 16px; font-weight: 700; letter-spacing: -0.03em; }
    .hg-board-title span { display: block; margin-top: 2px; font-size: 10.5px; color: var(--text-muted); }
    .hg-board-top .hg-seg { width: 178px; flex-shrink: 0; }

    .hg-route { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; margin-top: 11px; font-size: 12px; color: var(--text-secondary); }
    .hg-route-label { font-size: 10px; color: var(--text-muted); }
    .hg-route strong { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); }
    .hg-route svg { width: 15px; height: 15px; color: var(--text-muted); flex-shrink: 0; }
    .hg-route-chips { display: flex; align-items: center; gap: 6px; margin-left: auto; }

    .hg-progress { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-subtle); }
    .hg-progress-main { display: flex; align-items: baseline; gap: 4px; font-size: 11.5px; color: var(--text-secondary); white-space: nowrap; }
    .hg-progress-main strong { font-size: 18px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; letter-spacing: -0.03em; }
    .hg-progress .hg-stars { margin-top: 0; }
    .hg-progress .hg-remain { margin-left: auto; }

    .hg-word { display: flex; align-items: flex-start; justify-content: center; gap: 14px; margin: 12px 0 5px; }
    .hg-unit { display: flex; flex-direction: column; align-items: center; gap: 5px; }
    .hg-syl {
      width: 92px; height: 92px; border-radius: 20px; border: 1px solid var(--border-default);
      background: var(--bg-surface); box-shadow: var(--card-shadow);
      display: flex; align-items: center; justify-content: center;
      font-family: inherit; font-size: 42px; font-weight: 600; letter-spacing: -0.04em; color: var(--text-primary);
      cursor: pointer; transition: border-color 140ms ease, box-shadow 140ms ease, background-color 140ms ease;
    }
    .hg-syl:hover { background: var(--bg-subtle); }
    .hg-syl.is-active { border-color: var(--accent-primary); box-shadow: 0 0 0 2px var(--accent-primary); color: var(--accent-primary); background: var(--accent-subtle); }
    .hg-syl.is-changed { animation: hgPop 340ms ease; }
    .hg-syl.is-reject { animation: hgShake 340ms ease; color: var(--no-text); }
    .hg-parts { display: flex; gap: 4px; }
    .hg-part {
      position: relative; width: 29px; height: 36px; padding: 0;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      border: 1px solid var(--border-default); border-radius: 9px;
      background: var(--bg-surface); color: var(--text-secondary); font-family: inherit;
      cursor: pointer; transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease;
    }
    .hg-part:hover { background: var(--bg-subtle); border-color: var(--border-strong); }
    .hg-part-jamo { font-size: 14px; font-weight: 600; line-height: 1.15; }
    .hg-part-label { font-size: 7.5px; line-height: 1; color: var(--text-muted); }
    .hg-part.is-empty .hg-part-jamo { color: var(--text-muted); }
    .hg-part.is-active { border-color: var(--accent-primary); background: var(--accent-subtle); color: var(--accent-primary); }
    .hg-part.is-active .hg-part-label { color: var(--accent-primary); }
    .hg-part.is-changed { animation: hgPop 340ms ease; }
    .hg-part.is-reject { animation: hgShake 340ms ease; color: var(--no-text); }
    .hg-wordnote { text-align: center; font-size: 10.5px; color: var(--text-muted); }
    .hg-wordnote b { font-weight: 700; color: var(--text-secondary); }

    .hg-pad { margin-top: 12px; }
    .hg-pad-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
    .hg-pad-hint { font-size: 10.5px; color: var(--text-muted); min-width: 0; }
    .hg-keys { display: grid; grid-template-columns: repeat(auto-fill, minmax(36px, 1fr)); gap: 5px; }
    .hg-letterpad { display: flex; flex-direction: column; gap: 6px; }
    .hg-cho-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(30px, 1fr)); gap: 4px; }
    .hg-cho {
      height: 28px; border-radius: 8px; border: 1px solid var(--border-default);
      background: var(--bg-subtle); color: var(--text-secondary);
      font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer;
    }
    .hg-cho:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .hg-cho.is-active { border-color: var(--accent-primary); background: var(--accent-subtle); color: var(--accent-primary); }
    .hg-keys-letters { grid-template-columns: repeat(auto-fill, minmax(40px, 1fr)); max-height: 118px; overflow-y: auto; padding: 6px 2px 0 0; border-top: 1px solid var(--border-subtle); }
    .hg-key {
      height: 36px; border-radius: 10px; border: 1px solid var(--border-default);
      background: var(--bg-surface); color: var(--text-primary);
      font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer;
      transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease;
    }
    .hg-key:hover { background: var(--bg-subtle); border-color: var(--border-strong); }
    .hg-key.is-current { border-color: var(--accent-primary); background: var(--accent-subtle); color: var(--accent-primary); }
    .hg-key.is-off { font-size: 10px; font-weight: 600; color: var(--text-secondary); }
    .hg-pad-note { margin-top: 7px; font-size: 10px; color: var(--text-muted); }

    .hg-actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; margin-top: 11px; }
    .hg-btn {
      border: 1px solid var(--border-default); border-radius: 10px; background: var(--bg-surface);
      color: var(--text-primary); font-family: inherit; font-size: 12px; font-weight: 600;
      padding: 10px 6px; cursor: pointer; white-space: nowrap;
      transition: background-color 140ms ease, border-color 140ms ease, opacity 140ms ease;
    }
    .hg-btn:hover:not(:disabled) { background: var(--bg-subtle); border-color: var(--border-strong); }
    .hg-btn:disabled { opacity: 0.45; cursor: default; }
    .hg-btn-primary { background: var(--accent-primary); border-color: var(--accent-primary); color: #ffffff; }
    .hg-btn-primary:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }
    .hg-btn-ghost { color: var(--text-secondary); }

    .hg-status { margin-top: 9px; min-height: 17px; font-size: 11px; line-height: 1.5; color: var(--text-secondary); }
    .hg-status.is-bad { color: var(--no-text); }
    .hg-status.is-good { color: var(--ok-text); }

    /* ----- 결과 ----- */
    .hg-result { margin-top: 10px; border: 1px solid var(--ok-border); background: var(--ok-bg); border-radius: 14px; padding: 12px 13px; }
    .hg-result-head { display: flex; align-items: center; justify-content: center; gap: 7px; }
    .hg-result-badge {
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 10.5px; font-weight: 700; color: var(--ok-text);
      border: 1px solid var(--ok-border); border-radius: 999px; padding: 2px 8px; background: var(--bg-surface);
    }
    .hg-perfect { font-size: 10.5px; font-weight: 700; color: var(--accent-primary); border: 1px solid var(--border-default); border-radius: 999px; padding: 2px 8px; background: var(--bg-surface); }
    .hg-result-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; margin-top: 8px; text-align: center; }
    .hg-result-grid dt { font-size: 10px; color: var(--text-secondary); }
    .hg-result-grid dd { font-size: 15px; font-weight: 700; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .hg-result-note { margin-top: 7px; text-align: center; font-size: 11px; color: var(--text-secondary); }
    .hg-result-next { margin-top: 2px; text-align: center; font-size: 10.5px; color: var(--text-muted); }
    .hg-result-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 9px; }

    @keyframes hgPop {
      0% { transform: scale(1); }
      38% { transform: scale(1.16); background: var(--accent-subtle); color: var(--accent-primary); }
      100% { transform: scale(1); }
    }
    @keyframes hgShake {
      0%, 100% { transform: translateX(0); }
      25% { transform: translateX(-3px); }
      55% { transform: translateX(3px); }
      80% { transform: translateX(-1px); }
    }
    @keyframes hgStarPop {
      0% { transform: scale(0.8); }
      55% { transform: scale(1.18); }
      100% { transform: scale(1); }
    }

    @media (max-width: 940px) {
      .hg-shell { grid-template-columns: 1fr; }
      .hg-main { order: -1; }
      .hg-rail { position: static; }
    }

    @media (max-width: 640px) {
      .hg-wrap { padding: 10px 12px 72px; }
      .hg-hero { margin-bottom: 9px; }
      .hg-hero h1 { font-size: 18px; }
      .hg-hero p { margin-top: 4px; font-size: 11.5px; line-height: 1.45; }
      .hg-pill { margin-bottom: 6px; }
      .hg-card { padding: 10px 11px; border-radius: 14px; }
      .hg-board { padding: 10px 11px; }
      .hg-board-top .hg-seg { width: 100%; }
      .hg-board-title h2 { font-size: 15px; }
      .hg-route { margin-top: 8px; }
      .hg-route strong { font-size: 16px; }
      .hg-route-chips { margin-left: 0; }
      .hg-progress { margin-top: 8px; padding-top: 8px; gap: 6px; }
      .hg-progress-main strong { font-size: 16px; }
      .hg-word { gap: 10px; margin: 9px 0 4px; }
      .hg-syl { width: 82px; height: 82px; border-radius: 18px; font-size: 37px; }
      .hg-parts { gap: 3px; }
      .hg-part { width: 25px; height: 32px; }
      .hg-part-jamo { font-size: 12.5px; }
      .hg-pad { margin-top: 9px; }
      .hg-pad-head { margin-bottom: 6px; }
      .hg-keys { grid-template-columns: repeat(auto-fill, minmax(33px, 1fr)); gap: 4px; }
      .hg-key { height: 33px; font-size: 14px; border-radius: 9px; }
      .hg-cho { height: 26px; }
      .hg-keys-letters { grid-template-columns: repeat(auto-fill, minmax(36px, 1fr)); max-height: 104px; }
      .hg-record-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 5px; }
      .hg-actions { margin-top: 9px; }
      .hg-btn { font-size: 11.5px; padding: 8px 4px; }
      .hg-status { margin-top: 7px; font-size: 10.5px; }
    }

    @media (max-width: 420px) {
      .hg-streak-best { display: none; }
    }

    @media (max-width: 360px) {
      .hg-wrap { padding: 8px 10px 72px; }
      .hg-word { gap: 8px; }
      .hg-syl { width: 74px; height: 74px; font-size: 33px; border-radius: 16px; }
      .hg-part { width: 23px; height: 31px; }
      .hg-part-jamo { font-size: 12px; }
      .hg-keys { grid-template-columns: repeat(auto-fill, minmax(30px, 1fr)); }
      .hg-key { height: 32px; font-size: 13px; }
    }

    @media (prefers-reduced-motion: reduce) {
      .hg-syl.is-changed, .hg-syl.is-reject, .hg-part.is-changed, .hg-part.is-reject,
      .hg-star.is-pop, .hg-demo-tile.is-pop { animation: none !important; }
      .hg-star, .hg-demo-tile, .hg-seg-btn { transition: none !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 한글 한 칸 변신</title>
  <meta name="description" content="두 글자 단어에서 초성·중성·종성 한 칸 또는 글자 하나만 바꿔 목표 단어까지 가는 한국어 단어 사다리 퍼즐. 최소 이동 수(par)와 별 3개, 연속 클리어, 라이벌 기록에 도전합니다.">
  <link rel="icon" type="image/png" href="logo.png">
  <link rel="apple-touch-icon" href="logo.png">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" integrity="sha384-SN6A48CJQjx946+DRb8wsoifC4a8ur9ZS6R+HCTgnBHOKCa6GLXAR3Qn8d1jztxg" crossorigin="anonymous" />
  <style>__CSS__</style>
  <script>
    (function () {
      try {
        var saved = localStorage.getItem('secjobs-theme');
        if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
          document.documentElement.setAttribute('data-theme', 'dark');
        }
      } catch (e) {}
    })();
  </script>
</head>
<body>

  <!-- Global Nav -->
  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
      </div>
      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>매일 KST 00:00 새 문제</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="화면 테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        </button>
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기" aria-label="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <main class="hg-wrap">
    <div class="hg-hero">
      <span class="hg-pill">한글 사다리 · 일일 퍼즐</span>
      <h1>한 칸만 바꿔 목표 단어까지</h1>
      <p>초성·중성·종성 중 한 칸, 또는 글자 하나만 바꿔 사전에 있는 단어를 거쳐 목표 단어에 도달하세요. 최소 이동 수에 가까울수록 별이 쌓입니다.</p>
    </div>

    <div class="hg-shell">
      <aside class="hg-rail" aria-label="게임 안내">
        <section class="hg-card hg-guide" id="guideCard" aria-labelledby="guideTitle">
          <div class="hg-guide-head">
            <h2 id="guideTitle">게임 방법</h2>
            <button type="button" class="hg-guide-toggle" id="guideToggle" aria-expanded="true" aria-controls="guideBody">접기</button>
          </div>
          <div class="hg-guide-body" id="guideBody">
            <div class="hg-demo" id="guideStage" aria-hidden="true">
              <div class="hg-demo-tiles" id="guideTiles">
                <span class="hg-demo-tile" data-side="0">바</span>
                <span class="hg-demo-arrow">→</span>
                <span class="hg-demo-tile" data-side="1">다</span>
                <span class="hg-demo-arrow">→</span>
                <span class="hg-demo-tile hg-demo-goal" data-side="2">?</span>
              </div>
              <div class="hg-demo-steps">
                <span class="hg-demo-step is-on" data-step="1">① 칸 탭</span>
                <span class="hg-demo-step" data-step="2">② 자모 선택</span>
                <span class="hg-demo-step" data-step="3">③ 목표 도착</span>
              </div>
            </div>
            <p class="hg-guide-note" id="guideNote">바꿀 칸을 탭하고 자모 하나를 고르면 그 칸만 바뀝니다.</p>
            <button type="button" class="hg-guide-replay" id="guideReplay">다시 보기</button>
            <p class="hg-guide-foot">처음 한 번만 자동으로 움직이고 멈춥니다. 다시 보기로 언제든 되돌려 볼 수 있습니다.</p>
          </div>
        </section>

        <section class="hg-card" id="recordCard">
          <div class="hg-card-head">
            <h2>기록</h2>
            <span id="recordScope">오늘</span>
          </div>
          <dl class="hg-record-grid">
            <div><dt>최고 별</dt><dd id="recordBest">0</dd></div>
            <div><dt>완주</dt><dd id="recordPlays">0판</dd></div>
            <div><dt>연속</dt><dd id="recordStreak">0회</dd></div>
            <div><dt>최단</dt><dd id="recordTime">—</dd></div>
          </dl>
          <ul class="hg-record-list" id="recordList"></ul>
          <p class="hg-foot">기록은 이 브라우저(localStorage)에만 저장됩니다. 서버로 보내지 않습니다.</p>
        </section>

        <section class="hg-card" id="practiceCard" hidden>
          <div class="hg-card-head">
            <h2>자유 연습</h2>
            <span id="practiceMeta">12판</span>
          </div>
          <div id="practiceList"></div>
          <p class="hg-foot">입문·중급·고급 각 4판. 최소 이동 수는 판마다 다릅니다.</p>
        </section>
      </aside>

      <section class="hg-main" aria-label="한 칸 변신 보드">
        <section class="hg-card hg-board" id="board">
          <div class="hg-board-top">
            <div class="hg-board-title">
              <h2 id="boardTitle">서재 정리</h2>
              <span id="boardMeta">오늘의 문제 · 기준 4수</span>
            </div>
            <div class="hg-seg" role="group" aria-label="게임 모드">
              <button type="button" class="hg-seg-btn is-active" id="modeDaily" aria-pressed="true">오늘의 문제</button>
              <button type="button" class="hg-seg-btn" id="modePractice" aria-pressed="false">자유 연습</button>
            </div>
          </div>

          <div class="hg-route">
            <span class="hg-route-label">지금</span><strong id="startWord">의자</strong>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="4" y1="12" x2="18" y2="12"></line><polyline points="13 7 18 12 13 17"></polyline></svg>
            <span class="hg-route-label">목표</span><strong id="goalWord">책상</strong>
            <span class="hg-route-chips">
              <span class="hg-chip" id="timerValue">0:00</span>
              <span class="hg-chip" id="rivalValue">라이벌 4수 · 0:56</span>
            </span>
          </div>

          <div class="hg-progress">
            <span class="hg-progress-main">이동 <strong id="moveValue">0</strong> / <span id="parValue">4</span>수</span>
            <span class="hg-stars" id="starGauge" aria-label="별 3개 중 3개"></span>
            <span class="hg-chip" id="streakChip">연속 0회</span>
            <span class="hg-streak-best" id="streakBest">최고 0회</span>
            <span class="hg-remain" id="remainValue">최소 4수 남음</span>
          </div>
          <p class="hg-daybadge" id="dayBadge" hidden></p>

          <div class="hg-word" id="wordRow" role="group" aria-label="현재 단어 자모"></div>
          <p class="hg-wordnote" id="wordNote">현재 단어 <b>의자</b> · 목표까지 최소 4수</p>

          <div class="hg-result" id="resultBox" hidden>
            <div class="hg-result-head">
              <span class="hg-result-badge">클리어</span>
              <span class="hg-perfect" id="resultPerfect" hidden>퍼펙트</span>
            </div>
            <div class="hg-stars hg-stars-big" id="resultStars"></div>
            <dl class="hg-result-grid">
              <div><dt>이동</dt><dd id="resultMoves">4수</dd></div>
              <div><dt>시간</dt><dd id="resultTime">0:41</dd></div>
              <div><dt>최소</dt><dd id="resultPar">4수</dd></div>
            </dl>
            <p class="hg-result-note" id="resultRival">라이벌보다 15초 빨랐습니다.</p>
            <p class="hg-result-next" id="resultNext">다음 문제가 기다립니다.</p>
            <div class="hg-result-actions">
              <button type="button" class="hg-btn hg-btn-primary" id="nextBtn">다음 문제</button>
              <button type="button" class="hg-btn hg-btn-ghost" id="retryBtn">다시 하기</button>
            </div>
          </div>

          <div class="hg-pad" id="pad">
            <div class="hg-pad-head">
              <div class="hg-seg hg-seg-small" role="tablist" aria-label="바꾸기 방식">
                <button type="button" class="hg-seg-btn is-active" id="padTabJamo" role="tab" aria-selected="true">자모</button>
                <button type="button" class="hg-seg-btn" id="padTabLetter" role="tab" aria-selected="false">글자</button>
              </div>
              <span class="hg-pad-hint" id="padHint">바꿀 칸을 탭하세요</span>
            </div>
            <div class="hg-keys" id="jamoKeys" role="group" aria-label="자모 선택"></div>
            <div class="hg-letterpad" id="letterKeys" hidden>
              <div class="hg-cho-row" id="letterChoRow" role="group" aria-label="초성 고르기"></div>
              <div class="hg-keys hg-keys-letters" id="letterGrid" role="group" aria-label="글자 선택"></div>
            </div>
            <p class="hg-pad-note" id="padNote">사전에 없는 단어는 이동으로 세지 않고 되돌립니다.</p>
          </div>

          <div class="hg-actions" id="actionRow">
            <button type="button" class="hg-btn" id="undoBtn" disabled>한 수 되돌리기</button>
            <button type="button" class="hg-btn" id="hintBtn">힌트</button>
            <button type="button" class="hg-btn hg-btn-ghost" id="resetBtn">처음부터</button>
          </div>
          <p class="hg-status" id="statusLine" role="status" aria-live="polite">바꿀 칸을 탭하고 자모를 골라 보세요.</p>
        </section>
      </section>
    </div>
  </main>

  <script id="hangulData" type="application/json">__DATA_JSON__</script>
  <script>
__JS__
  </script>
</body>
</html>
"""

JS = r"""
(function () {
  'use strict';

  var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var DATA = JSON.parse(document.getElementById('hangulData').textContent);
  var WORDS = DATA.words;
  var WORD_SET = Object.create(null);
  WORDS.forEach(function (word) { WORD_SET[word] = true; });

  var STORE_KEY = 'hangul_ladder_stats_v1';
  var GUIDE_KEY = 'hangul_guide_seen_v1';
  var CHO = DATA.cho, JUNG = DATA.jung, JONG = DATA.jong;
  var PART_LABEL = { cho: '초성', jung: '중성', jong: '종성' };
  var PART_SHORT = { cho: '초', jung: '중', jong: '종' };
  var PARTS = ['cho', 'jung', 'jong'];

  var el = {};
  [
    'themeToggle', 'modeDaily', 'modePractice', 'moveValue', 'parValue',
    'remainValue', 'starGauge', 'streakChip', 'streakBest', 'dayBadge',
    'boardTitle', 'boardMeta', 'startWord', 'goalWord', 'timerValue', 'rivalValue',
    'wordRow', 'wordNote', 'resultBox', 'resultStars', 'resultPerfect', 'resultMoves',
    'resultTime', 'resultPar', 'resultRival', 'resultNext', 'nextBtn', 'retryBtn',
    'pad', 'padTabJamo', 'padTabLetter', 'padHint', 'jamoKeys', 'letterKeys', 'letterChoRow', 'letterGrid', 'padNote',
    'undoBtn', 'hintBtn', 'resetBtn', 'statusLine', 'actionRow',
    'recordScope', 'recordBest', 'recordPlays', 'recordStreak', 'recordTime', 'recordList',
    'practiceCard', 'practiceList', 'practiceMeta',
    'guideCard', 'guideToggle', 'guideBody', 'guideStage', 'guideTiles', 'guideNote', 'guideReplay'
  ].forEach(function (id) { el[id] = document.getElementById(id); });

  /* ------------------------------------------------------------------ 자모 */
  function decompose(syllable) {
    var code = syllable.charCodeAt(0) - 0xAC00;
    if (code < 0 || code > 11171) return null;
    return {
      cho: CHO[Math.floor(code / 588)],
      jung: JUNG[Math.floor((code % 588) / 28)],
      jong: JONG[code % 28]
    };
  }

  function compose(cho, jung, jong) {
    var choIndex = CHO.indexOf(cho);
    var jungIndex = JUNG.indexOf(jung);
    var jongIndex = JONG.indexOf(jong);
    if (choIndex < 0 || jungIndex < 0 || jongIndex < 0) return null;
    return String.fromCharCode(0xAC00 + choIndex * 588 + jungIndex * 28 + jongIndex);
  }

  function jamoDiff(a, b) {
    var count = 0;
    for (var i = 0; i < Math.min(a.length, b.length); i += 1) {
      if (a[i] === b[i]) continue;
      var left = decompose(a[i]);
      var right = decompose(b[i]);
      if (!left || !right) return 99;
      count += (left.cho !== right.cho ? 1 : 0)
        + (left.jung !== right.jung ? 1 : 0)
        + (left.jong !== right.jong ? 1 : 0);
    }
    return count;
  }

  /* ------------------------------------------------------------ 단어 그래프 */
  var NEI = Object.create(null);
  (function buildGraph() {
    var buckets = Object.create(null);
    WORDS.forEach(function (word) {
      NEI[word] = [];
      for (var i = 0; i < word.length; i += 1) {
        var key = i + '|' + word[i];
        if (!buckets[key]) buckets[key] = [];
        buckets[key].push(word);
      }
    });
    Object.keys(buckets).forEach(function (key) {
      var group = buckets[key];
      for (var i = 0; i < group.length; i += 1) {
        for (var j = i + 1; j < group.length; j += 1) {
          NEI[group[i]].push(group[j]);
          NEI[group[j]].push(group[i]);
        }
      }
    });
  })();

  function distance(from, to) {
    if (from === to) return 0;
    var dist = Object.create(null);
    dist[from] = 0;
    var queue = [from];
    var head = 0;
    while (head < queue.length) {
      var current = queue[head];
      head += 1;
      var neighbours = NEI[current] || [];
      for (var i = 0; i < neighbours.length; i += 1) {
        var next = neighbours[i];
        if (next in dist) continue;
        dist[next] = dist[current] + 1;
        if (next === to) return dist[next];
        queue.push(next);
      }
    }
    return -1;
  }

  function bestStep(from, to) {
    var total = distance(from, to);
    if (total <= 0) return null;
    var neighbours = NEI[from] || [];
    var best = null;
    var bestDiff = 99;
    for (var i = 0; i < neighbours.length; i += 1) {
      var candidate = neighbours[i];
      if (distance(candidate, to) !== total - 1) continue;
      var diff = jamoDiff(from, candidate);
      if (diff < bestDiff) {
        bestDiff = diff;
        best = candidate;
        if (diff === 1) break;
      }
    }
    return best;
  }

  /* ------------------------------------------------------------------ 저장 */
  function emptyStore() {
    return {
      v: 1,
      daily: { plays: 0, streak: 0, bestStreak: 0, bestStars: 0, bestMs: 0, days: {} },
      practice: { plays: 0, streak: 0, bestStreak: 0, bestStars: 0, bestMs: 0, puzzles: {} },
      recent: []
    };
  }

  function readStore() {
    var raw = null;
    try { raw = localStorage.getItem(STORE_KEY); } catch (e) { raw = null; }
    if (!raw) return emptyStore();
    var parsed;
    try { parsed = JSON.parse(raw); } catch (e) { parsed = null; }
    if (!parsed || typeof parsed !== 'object') return emptyStore();
    var base = emptyStore();
    ['daily', 'practice'].forEach(function (key) {
      var source = parsed[key];
      if (!source || typeof source !== 'object') return;
      ['plays', 'streak', 'bestStreak', 'bestStars', 'bestMs'].forEach(function (field) {
        if (typeof source[field] === 'number' && isFinite(source[field])) base[key][field] = source[field];
      });
      if (source.days && typeof source.days === 'object') base.daily.days = source.days;
      if (source.puzzles && typeof source.puzzles === 'object') base.practice.puzzles = source.puzzles;
    });
    if (Array.isArray(parsed.recent)) base.recent = parsed.recent.slice(0, 8);
    return base;
  }

  function saveStore() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state.store)); } catch (e) {}
  }

  /* ------------------------------------------------------------------ 날짜 */
  function kstKey(date) {
    var now = date || new Date();
    var kst = new Date(now.getTime() + 9 * 3600000);
    var month = String(kst.getUTCMonth() + 1);
    var day = String(kst.getUTCDate());
    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;
    return kst.getUTCFullYear() + '-' + month + '-' + day;
  }

  function dayOrdinal(key) {
    var parts = key.split('-');
    return Math.floor(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])) / 86400000);
  }

  function dayLabel(key) {
    var parts = key.split('-');
    return Number(parts[1]) + '/' + Number(parts[2]);
  }

  function fmtDuration(ms) {
    var total = Math.max(0, Math.round(ms / 1000));
    var minutes = Math.floor(total / 60);
    var seconds = total % 60;
    return minutes + ':' + (seconds < 10 ? '0' + seconds : String(seconds));
  }

  /* ------------------------------------------------------------------ 상태 */
  var state = {
    mode: 'daily',
    puzzle: null,
    dayKey: '',
    todayKey: '',
    word: '',
    history: [],
    moves: 0,
    par: 0,
    hints: 0,
    startedAt: 0,
    elapsedMs: 0,
    running: false,
    cleared: false,
    cell: null,
    padTab: 'jamo',
    letterCho: null,
    lastPracticeId: null,
    store: emptyStore(),
    timer: null,
    guideTimers: []
  };

  function modeBucket() {
    return state.mode === 'daily' ? state.store.daily : state.store.practice;
  }

  function currentRecord() {
    if (state.mode === 'daily') return state.store.daily.days[state.dayKey] || null;
    return state.store.practice.puzzles[state.puzzle.id] || null;
  }

  function starsFor(moves, par) {
    var over = moves - par;
    if (over <= 0) return 3;
    if (over <= 2) return 2;
    return 1;
  }

  function liveStars() {
    return starsFor(state.moves, state.par);
  }

  /* ------------------------------------------------------------------ 렌더 */
  function starSvg(on, big) {
    return '<svg class="hg-star' + (on ? ' is-on' : '') + '" viewBox="0 0 24 24" aria-hidden="true">'
      + '<path fill="currentColor" d="M12 3.4l2.7 5.5 6 .9-4.3 4.2 1 6-5.4-2.9-5.4 2.9 1-6L3.3 9.8l6-.9z"></path></svg>';
  }

  function paintStars(target, count) {
    var html = '';
    for (var i = 1; i <= 3; i += 1) html += starSvg(i <= count);
    target.innerHTML = html;
    target.setAttribute('aria-label', '별 3개 중 ' + count + '개');
  }

  function buildWordRow() {
    el.wordRow.innerHTML = '';
    for (var i = 0; i < state.word.length; i += 1) {
      var unit = document.createElement('div');
      unit.className = 'hg-unit';
      unit.setAttribute('data-pos', String(i));

      var syllable = document.createElement('button');
      syllable.type = 'button';
      syllable.className = 'hg-syl';
      syllable.setAttribute('data-pos', String(i));
      unit.appendChild(syllable);

      var parts = document.createElement('div');
      parts.className = 'hg-parts';
      for (var p = 0; p < PARTS.length; p += 1) {
        var part = PARTS[p];
        var cell = document.createElement('button');
        cell.type = 'button';
        cell.className = 'hg-part';
        cell.setAttribute('data-pos', String(i));
        cell.setAttribute('data-part', part);
        cell.innerHTML = '<span class="hg-part-jamo"></span><span class="hg-part-label">' + PART_SHORT[part] + '</span>';
        parts.appendChild(cell);
      }
      unit.appendChild(parts);
      el.wordRow.appendChild(unit);
    }
  }

  function paintWord() {
    for (var i = 0; i < state.word.length; i += 1) {
      var syllable = state.word[i];
      var parts = decompose(syllable) || { cho: '', jung: '', jong: '' };
      var syllableButton = el.wordRow.querySelector('.hg-syl[data-pos="' + i + '"]');
      if (syllableButton) {
        syllableButton.textContent = syllable;
        syllableButton.setAttribute('aria-label', (i + 1) + '번째 글자 ' + syllable + ' 통째로 바꾸기');
      }
      for (var p = 0; p < PARTS.length; p += 1) {
        var part = PARTS[p];
        var cell = el.wordRow.querySelector('.hg-part[data-pos="' + i + '"][data-part="' + part + '"]');
        if (!cell) continue;
        cell.querySelector('.hg-part-jamo').textContent = parts[part] || '·';
        cell.classList.toggle('is-empty', !parts[part]);
        cell.setAttribute('aria-label', (i + 1) + '번째 글자 ' + PART_LABEL[part] + ' ' + (parts[part] || '없음') + ' 바꾸기');
      }
    }
    syncSelection();
  }

  function syncSelection() {
    var cells = el.wordRow.querySelectorAll('.hg-part');
    for (var i = 0; i < cells.length; i += 1) {
      var selected = !!state.cell
        && state.cell.pos === Number(cells[i].getAttribute('data-pos'))
        && state.cell.part === cells[i].getAttribute('data-part');
      cells[i].classList.toggle('is-active', selected);
    }
    var syllables = el.wordRow.querySelectorAll('.hg-syl');
    for (var j = 0; j < syllables.length; j += 1) {
      var whole = !!state.cell && state.cell.part === 'whole'
        && state.cell.pos === Number(syllables[j].getAttribute('data-pos'));
      syllables[j].classList.toggle('is-active', whole);
    }
  }

  function currentCellJamo() {
    if (!state.cell || state.cell.part === 'whole') return null;
    var parts = decompose(state.word[state.cell.pos]);
    return parts ? parts[state.cell.part] : null;
  }

  function buildJamoKeys() {
    el.jamoKeys.innerHTML = '';
    if (!state.cell) {
      el.padHint.textContent = '바꿀 칸을 탭하세요';
      return;
    }
    if (state.cell.part === 'whole') {
      el.padHint.textContent = '글자를 고르면 그 글자로 바뀝니다';
      return;
    }
    var part = state.cell.part;
    var list = part === 'cho' ? CHO : (part === 'jung' ? JUNG : JONG);
    var current = currentCellJamo();
    el.padHint.textContent = (state.cell.pos + 1) + '번째 글자 ' + PART_LABEL[part] + ' 바꾸기';
    for (var i = 0; i < list.length; i += 1) {
      var jamo = list[i];
      var button = document.createElement('button');
      button.type = 'button';
      var cls = 'hg-key';
      if (jamo === current) cls += ' is-current';
      if (!jamo) cls += ' is-off';
      button.className = cls;
      button.setAttribute('data-jamo', jamo);
      button.textContent = jamo || '없음';
      if (part === 'jong' && !jamo) button.setAttribute('aria-label', '받침 없음으로 바꾸기');
      else button.setAttribute('aria-label', PART_LABEL[part] + ' ' + jamo + '으로 바꾸기');
      el.jamoKeys.appendChild(button);
    }
  }

  function buildLetterKeys() {
    var current = state.cell && state.cell.part === 'whole' ? state.word[state.cell.pos] : '';
    if (!state.letterCho) {
      var parts = current ? decompose(current) : null;
      state.letterCho = parts ? parts.cho : CHO[0];
    }
    el.letterChoRow.innerHTML = '';
    for (var c = 0; c < CHO.length; c += 1) {
      var choButton = document.createElement('button');
      choButton.type = 'button';
      choButton.className = 'hg-cho' + (CHO[c] === state.letterCho ? ' is-active' : '');
      choButton.setAttribute('data-cho', CHO[c]);
      choButton.setAttribute('aria-label', '초성 ' + CHO[c] + ' 글자 보기');
      choButton.textContent = CHO[c];
      el.letterChoRow.appendChild(choButton);
    }
    el.padHint.textContent = '초성 ' + state.letterCho + ' · 글자를 고르면 그 글자로 바뀝니다';
    var list = DATA.syllableGroups[state.letterCho] || [];
    el.letterGrid.innerHTML = '';
    for (var i = 0; i < list.length; i += 1) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'hg-key' + (list[i] === current ? ' is-current' : '');
      button.setAttribute('data-syllable', list[i]);
      button.textContent = list[i];
      button.setAttribute('aria-label', list[i] + ' 글자로 바꾸기');
      el.letterGrid.appendChild(button);
    }
  }

  function paintMode() {
    var daily = state.mode === 'daily';
    el.modeDaily.classList.toggle('is-active', daily);
    el.modePractice.classList.toggle('is-active', !daily);
    el.modeDaily.setAttribute('aria-pressed', daily ? 'true' : 'false');
    el.modePractice.setAttribute('aria-pressed', daily ? 'false' : 'true');
    el.practiceCard.hidden = daily;
    el.recordScope.textContent = daily ? (state.dayKey ? dayLabel(state.dayKey) : '오늘') : '연습';
    el.boardMeta.textContent = (daily ? '오늘의 문제' : state.puzzle.level + ' 연습') + ' · 기준 ' + state.par + '수';
    el.padTabJamo.classList.toggle('is-active', state.padTab === 'jamo');
    el.padTabLetter.classList.toggle('is-active', state.padTab === 'letter');
    el.padTabJamo.setAttribute('aria-selected', state.padTab === 'jamo' ? 'true' : 'false');
    el.padTabLetter.setAttribute('aria-selected', state.padTab === 'letter' ? 'true' : 'false');
    el.jamoKeys.hidden = state.padTab !== 'jamo';
    el.letterKeys.hidden = state.padTab !== 'letter';
  }

  function paint() {
    var daily = state.mode === 'daily';
    el.boardTitle.textContent = state.puzzle.title;
    el.startWord.textContent = state.word;
    el.goalWord.textContent = state.puzzle.goal;
    el.moveValue.textContent = String(state.moves);
    el.parValue.textContent = String(state.par);
    el.rivalValue.textContent = '라이벌 ' + state.par + '수 · ' + fmtDuration(state.puzzle.rivalMs);
    el.timerValue.textContent = fmtDuration(state.elapsedMs);
    el.timerValue.classList.toggle('is-over', state.elapsedMs > state.puzzle.rivalMs);

    var remain = distance(state.word, state.puzzle.goal);
    if (remain <= 0) {
      el.remainValue.textContent = '목표 도착';
      el.remainValue.classList.add('is-done');
    } else {
      el.remainValue.textContent = (remain === 1 ? '한 수만 더!' : '최소 ' + remain + '수 남음');
      el.remainValue.classList.remove('is-done');
    }
    el.wordNote.innerHTML = '현재 단어 <b>' + state.word + '</b> · 목표까지 최소 ' + Math.max(0, remain) + '수';

    paintStars(el.starGauge, state.cleared ? starsFor(state.moves, state.par) : liveStars());
    var bucket = modeBucket();
    el.streakChip.textContent = '연속 ' + bucket.streak + '회';
    el.streakChip.classList.toggle('is-hot', bucket.streak >= 3);
    el.streakBest.textContent = '최고 ' + bucket.bestStreak + '회';

    el.undoBtn.disabled = state.cleared || state.history.length === 0;
    el.hintBtn.disabled = state.cleared;
    el.resetBtn.disabled = false;
    el.pad.hidden = state.cleared;
    el.actionRow.hidden = state.cleared;
    el.resultBox.hidden = !state.cleared;

    paintWord();
    if (state.padTab === 'letter') buildLetterKeys();
    else buildJamoKeys();
    paintMode();
    paintRecord();

    if (state.mode === 'practice') paintPractice();
  }

  function paintRecord() {
    var record = currentRecord();
    var bucket = modeBucket();
    el.recordBest.textContent = String(record ? record.bestStars : 0);
    el.recordPlays.textContent = (record ? record.clears : 0) + '판';
    el.recordStreak.textContent = bucket.streak + '회';
    el.recordTime.textContent = record && record.bestMs ? fmtDuration(record.bestMs) : '—';

    el.recordList.innerHTML = '';
    var entries = state.store.recent.filter(function (entry) {
      return state.mode === 'daily' ? entry.mode === 'daily' : entry.mode === 'practice';
    }).slice(0, 4);
    if (!entries.length) {
      var empty = document.createElement('li');
      empty.className = 'hg-record-empty';
      empty.textContent = state.mode === 'daily' ? '오늘 클리어 기록이 아직 없습니다.' : '연습 클리어 기록이 아직 없습니다.';
      el.recordList.appendChild(empty);
      return;
    }
    entries.forEach(function (entry) {
      var item = document.createElement('li');
      var name = document.createElement('span');
      name.textContent = entry.title;
      var value = document.createElement('b');
      value.textContent = entry.moves + '수 · 별 ' + entry.stars + ' · ' + fmtDuration(entry.ms);
      item.appendChild(name);
      item.appendChild(value);
      el.recordList.appendChild(item);
    });
  }

  function paintPractice() {
    var groups = {};
    DATA.practice.forEach(function (puzzle) {
      if (!groups[puzzle.level]) groups[puzzle.level] = [];
      groups[puzzle.level].push(puzzle);
    });
    el.practiceList.innerHTML = '';
    ['입문', '중급', '고급'].forEach(function (level) {
      if (!groups[level]) return;
      var wrap = document.createElement('div');
      wrap.className = 'hg-practice-group';
      var label = document.createElement('div');
      label.className = 'hg-practice-label';
      label.textContent = level;
      wrap.appendChild(label);
      var list = document.createElement('div');
      list.className = 'hg-practice-list';
      groups[level].forEach(function (puzzle) {
        var record = state.store.practice.puzzles[puzzle.id];
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'hg-practice-btn' + (state.puzzle.id === puzzle.id ? ' is-active' : '');
        button.setAttribute('data-id', puzzle.id);
        var title = document.createElement('span');
        title.className = 'hg-practice-title';
        title.textContent = puzzle.title;
        var meta = document.createElement('span');
        meta.className = 'hg-practice-meta';
        meta.textContent = puzzle.par + '수 · 별 ' + (record ? record.bestStars : 0);
        button.appendChild(title);
        button.appendChild(meta);
        list.appendChild(button);
      });
      wrap.appendChild(list);
      el.practiceList.appendChild(wrap);
    });
  }

  function setStatus(text, tone) {
    el.statusLine.textContent = text;
    el.statusLine.classList.toggle('is-bad', tone === 'bad');
    el.statusLine.classList.toggle('is-good', tone === 'good');
  }

  function cellNode(pos, part) {
    if (part === 'whole') return el.wordRow.querySelector('.hg-syl[data-pos="' + pos + '"]');
    return el.wordRow.querySelector('.hg-part[data-pos="' + pos + '"][data-part="' + part + '"]');
  }

  function popCell(pos, part) {
    if (reduceMotion) return;
    var cell = cellNode(pos, part);
    if (!cell) return;
    cell.classList.remove('is-changed');
    void cell.offsetWidth;
    cell.classList.add('is-changed');
    window.setTimeout(function () { cell.classList.remove('is-changed'); }, 380);
  }

  function shakeCell(pos, part) {
    if (reduceMotion) return;
    var cell = cellNode(pos, part);
    if (!cell) return;
    cell.classList.remove('is-reject');
    void cell.offsetWidth;
    cell.classList.add('is-reject');
    window.setTimeout(function () { cell.classList.remove('is-reject'); }, 380);
  }

  /* ------------------------------------------------------------------ 진행 */
  function stopTimer() {
    state.running = false;
    if (state.timer) {
      window.clearInterval(state.timer);
      state.timer = null;
    }
  }

  function startTimer() {
    if (state.running) return;
    state.running = true;
    state.startedAt = Date.now() - state.elapsedMs;
    state.timer = window.setInterval(function () {
      if (!state.running) return;
      state.elapsedMs = Date.now() - state.startedAt;
      el.timerValue.textContent = fmtDuration(state.elapsedMs);
      el.timerValue.classList.toggle('is-over', state.elapsedMs > state.puzzle.rivalMs);
    }, 250);
  }

  function loadPuzzle(puzzle, options) {
    var opts = options || {};
    if (!opts.keepStreak && state.puzzle && !state.cleared && state.moves > 0) {
      modeBucket().streak = 0;
    }
    stopTimer();
    state.puzzle = puzzle;
    if (state.mode === 'practice') state.lastPracticeId = puzzle.id;
    state.word = puzzle.start;
    state.par = puzzle.par;
    state.history = [];
    state.moves = 0;
    state.hints = 0;
    state.elapsedMs = 0;
    state.cleared = false;
    state.cell = { pos: 0, part: 'cho' };
    state.padTab = 'jamo';
    state.letterCho = null;
    state.dayKey = opts.dayKey || state.dayKey || state.todayKey;
    el.dayBadge.hidden = state.mode !== 'daily' || state.dayKey === state.todayKey;
    if (state.mode === 'daily') el.dayBadge.hidden = true;
    buildWordRow();
    paint();
    setStatus('시작 단어 ' + puzzle.start + ' · 목표 ' + puzzle.goal + ' · 최소 ' + puzzle.par + '수. 바꿀 칸을 탭하세요.');
  }

  function todayDaily() {
    var index = dayOrdinal(state.todayKey) % DATA.daily.length;
    return DATA.daily[index];
  }

  function setMode(mode) {
    if (state.mode === mode && !(mode === 'practice' && !state.puzzle)) return;
    if (mode === state.mode) return;
    state.mode = mode;
    var puzzle;
    if (mode === 'daily') {
      state.dayKey = state.todayKey;
      puzzle = todayDaily();
    } else {
      puzzle = DATA.practice.filter(function (item) {
        return item.id === state.lastPracticeId;
      })[0] || DATA.practice[0];
      state.dayKey = state.todayKey;
    }
    loadPuzzle(puzzle, { keepStreak: false });
    setStatus(mode === 'daily'
      ? '오늘의 문제로 돌아왔습니다. 최소 ' + puzzle.par + '수에 도전하세요.'
      : '자유 연습입니다. 아래 연습 목록에서 판을 고를 수 있습니다.');
  }

  function commit(next, pos, part) {
    if (next === state.word) {
      setStatus('같은 글자입니다. 다른 자모를 골라 보세요.');
      return;
    }
    if (!WORD_SET[next]) {
      shakeCell(pos, part);
      setStatus('"' + next + '"는 사전에 없는 단어입니다. 이동으로 세지 않았어요.', 'bad');
      return;
    }
    state.history.push(state.word);
    state.word = next;
    state.moves += 1;
    if (!state.running) startTimer();
    paint();
    popCell(pos, part);

    if (state.word === state.puzzle.goal) {
      finishRun();
      return;
    }
    var remain = distance(state.word, state.puzzle.goal);
    var neighbours = NEI[state.word] ? NEI[state.word].length : 0;
    if (!neighbours) {
      setStatus('막다른 단어입니다. "한 수 되돌리기"로 돌아가세요.', 'bad');
    } else if (remain === 1) {
      setStatus('한 수만 더 가면 목표입니다!', 'good');
    } else {
      setStatus(state.moves + '수째 · 목표까지 최소 ' + remain + '수 남았습니다.');
    }
  }

  function applyJamo(jamo) {
    if (!state.cell || state.cell.part === 'whole' || state.cleared) return;
    var pos = state.cell.pos;
    var part = state.cell.part;
    var parts = decompose(state.word[pos]);
    if (!parts) return;
    if (parts[part] === jamo) {
      setStatus('이미 ' + (jamo || '받침 없음') + '입니다. 다른 자모를 골라 보세요.');
      return;
    }
    var nextSyllable = compose(
      part === 'cho' ? jamo : parts.cho,
      part === 'jung' ? jamo : parts.jung,
      part === 'jong' ? jamo : parts.jong
    );
    if (!nextSyllable) return;
    var next = state.word.slice(0, pos) + nextSyllable + state.word.slice(pos + 1);
    commit(next, pos, part);
  }

  function applySyllable(syllable) {
    if (!state.cell || state.cell.part !== 'whole' || state.cleared) return;
    var pos = state.cell.pos;
    if (state.word[pos] === syllable) {
      setStatus('같은 글자입니다. 다른 글자를 골라 보세요.');
      return;
    }
    var next = state.word.slice(0, pos) + syllable + state.word.slice(pos + 1);
    commit(next, pos, 'whole');
  }

  function finishRun() {
    stopTimer();
    state.cleared = true;
    var stars = starsFor(state.moves, state.par);
    var bucket = modeBucket();
    bucket.plays += 1;
    bucket.streak += 1;
    bucket.bestStreak = Math.max(bucket.bestStreak, bucket.streak);
    bucket.bestStars = Math.max(bucket.bestStars, stars);
    if (!bucket.bestMs || state.elapsedMs < bucket.bestMs) bucket.bestMs = state.elapsedMs;

    var record;
    if (state.mode === 'daily') {
      record = bucket.days[state.dayKey];
      if (!record) {
        record = { puzzleId: state.puzzle.id, clears: 0, bestStars: 0, bestMoves: 0, bestMs: 0 };
        bucket.days[state.dayKey] = record;
      }
    } else {
      record = bucket.puzzles[state.puzzle.id];
      if (!record) {
        record = { clears: 0, bestStars: 0, bestMoves: 0, bestMs: 0 };
        bucket.puzzles[state.puzzle.id] = record;
      }
    }
    record.clears += 1;
    record.bestStars = Math.max(record.bestStars, stars);
    record.bestMoves = record.bestMoves ? Math.min(record.bestMoves, state.moves) : state.moves;
    record.bestMs = record.bestMs ? Math.min(record.bestMs, state.elapsedMs) : state.elapsedMs;

    state.store.recent.unshift({
      mode: state.mode,
      id: state.puzzle.id,
      title: state.puzzle.title,
      moves: state.moves,
      stars: stars,
      ms: state.elapsedMs,
      day: state.dayKey
    });
    state.store.recent = state.store.recent.slice(0, 8);
    saveStore();

    el.resultStars.innerHTML = '';
    for (var i = 1; i <= 3; i += 1) el.resultStars.innerHTML += starSvg(i <= stars);
    el.resultStars.setAttribute('aria-label', '별 3개 중 ' + stars + '개');
    el.resultMoves.textContent = state.moves + '수';
    el.resultTime.textContent = fmtDuration(state.elapsedMs);
    el.resultPar.textContent = state.par + '수';
    el.resultPerfect.hidden = state.hints > 0;
    var rivalDiff = state.puzzle.rivalMs - state.elapsedMs;
    if (state.hints > 0) {
      el.resultPerfect.textContent = '퍼펙트';
    }
    if (rivalDiff >= 0) {
      el.resultRival.textContent = '라이벌(' + fmtDuration(state.puzzle.rivalMs) + ')보다 ' + fmtDuration(rivalDiff) + ' 빠릅니다.';
    } else {
      el.resultRival.textContent = '라이벌(' + fmtDuration(state.puzzle.rivalMs) + ')보다 ' + fmtDuration(-rivalDiff) + ' 느립니다. 한 번 더 도전해 보세요.';
    }
    if (state.mode === 'daily') {
      el.resultNext.textContent = '오늘의 문제를 마쳤습니다. 연습 목록에서 다른 판을 골라도 됩니다.';
      el.nextBtn.textContent = '자유 연습';
    } else {
      var nextPractice = nextPracticePuzzle();
      el.resultNext.textContent = nextPractice ? '다음 연습: ' + nextPractice.title : '연습을 모두 둘러봤습니다.';
      el.nextBtn.textContent = '다음 문제';
    }
    paint();
    setStatus('목표 도착! ' + state.moves + '수 · 별 ' + stars + '개 · ' + fmtDuration(state.elapsedMs) + '.', 'good');
  }

  function nextPracticePuzzle() {
    var index = DATA.practice.findIndex(function (item) { return item.id === state.puzzle.id; });
    if (index < 0 || index + 1 >= DATA.practice.length) return null;
    return DATA.practice[index + 1];
  }

  function undo() {
    if (state.cleared || !state.history.length) return;
    var previous = state.history.pop();
    var pos = 0;
    for (var i = 0; i < previous.length; i += 1) {
      if (previous[i] !== state.word[i]) { pos = i; break; }
    }
    var changedPart = 'cho';
    var before = decompose(previous[pos]);
    var after = decompose(state.word[pos]);
    if (before && after) {
      var diffs = 0;
      if (before.cho !== after.cho) diffs += 1;
      if (before.jung !== after.jung) diffs += 1;
      if (before.jong !== after.jong) diffs += 1;
      if (diffs > 1) changedPart = 'whole';
      else if (before.jung !== after.jung) changedPart = 'jung';
      else if (before.jong !== after.jong) changedPart = 'jong';
    }
    state.word = previous;
    state.moves = Math.max(0, state.moves - 1);
    paint();
    popCell(pos, changedPart);
    setStatus('한 수 되돌렸습니다. ' + state.moves + '수째입니다.');
  }

  function resetRun() {
    if (!state.cleared && state.moves > 0) modeBucket().streak = 0;
    stopTimer();
    state.word = state.puzzle.start;
    state.history = [];
    state.moves = 0;
    state.hints = 0;
    state.elapsedMs = 0;
    state.cleared = false;
    state.cell = { pos: 0, part: 'cho' };
    state.padTab = 'jamo';
    state.letterCho = null;
    buildWordRow();
    paint();
    setStatus('처음부터 다시 시작합니다. 기록은 그대로입니다.');
  }

  function showHint() {
    if (state.cleared) return;
    var next = bestStep(state.word, state.puzzle.goal);
    if (!next) {
      setStatus('지금 단어에서 목표까지 가는 길을 찾지 못했습니다. 되돌려 보세요.', 'bad');
      return;
    }
    state.hints += 1;
    for (var i = 0; i < state.word.length; i += 1) {
      if (state.word[i] === next[i]) continue;
      var before = decompose(state.word[i]);
      var after = decompose(next[i]);
      if (!before || !after) break;
      for (var p = 0; p < PARTS.length; p += 1) {
        var part = PARTS[p];
        if (before[part] === after[part]) continue;
        state.cell = { pos: i, part: part };
        state.padTab = 'jamo';
        state.letterCho = null;
        paint();
        if (!after[part]) setStatus('힌트 · ' + (i + 1) + '번째 글자의 받침을 없애 보세요.', 'good');
        else setStatus('힌트 · ' + (i + 1) + '번째 글자 ' + PART_LABEL[part] + ' → ' + after[part], 'good');
        return;
      }
    }
    setStatus('힌트를 찾지 못했습니다.', 'bad');
  }

  /* ------------------------------------------------------------ 가이드 데모 */
  function clearGuideTimers() {
    state.guideTimers.forEach(function (timer) { window.clearTimeout(timer); });
    state.guideTimers = [];
  }

  function guideTiles() {
    return el.guideTiles.querySelectorAll('.hg-demo-tile');
  }

  function setGuideStep(step) {
    var steps = el.guideStage.querySelectorAll('.hg-demo-step');
    for (var i = 0; i < steps.length; i += 1) {
      steps[i].classList.toggle('is-on', Number(steps[i].getAttribute('data-step')) === step);
    }
  }

  function guidePop(side) {
    if (reduceMotion) return;
    var tile = guideTiles()[side];
    if (!tile) return;
    tile.classList.remove('is-pop');
    void tile.offsetWidth;
    tile.classList.add('is-pop');
  }

  function guideResetState() {
    var tiles = guideTiles();
    if (tiles.length < 3) return;
    tiles[0].textContent = '바';
    tiles[1].textContent = '다';
    tiles[2].textContent = '?';
    tiles[0].classList.remove('is-target');
    tiles[1].classList.add('is-target');
    el.guideNote.textContent = '① 바꿀 칸을 탭합니다. 지금은 두 번째 글자를 고릅니다.';
    setGuideStep(1);
  }

  function playGuide() {
    clearGuideTimers();
    guideResetState();
    // 자동 재생은 첫 방문 한 번뿐 — 이후에는 정지된 마지막 장면만 남긴다.
    try { localStorage.setItem(GUIDE_KEY, '1'); } catch (e) {}
    if (reduceMotion) {
      var tiles = guideTiles();
      tiles[0].textContent = '가';
      tiles[1].textContent = '지';
      tiles[2].textContent = '가지';
      tiles[0].classList.remove('is-target');
      el.guideNote.textContent = '바꿀 칸을 탭하고 자모를 고르면 그 칸만 바뀝니다. 두 번이면 목표 단어에 도착합니다.';
      setGuideStep(3);
      return;
    }
    state.guideTimers.push(window.setTimeout(function () {
      var tiles2 = guideTiles();
      tiles2[1].textContent = '지';
      guidePop(1);
      el.guideNote.textContent = '② 두 번째 글자 ' + '다' + '를 ' + '지' + '로 바꿉니다. 사전에 있는 단어면 한 수로 인정됩니다.';
      setGuideStep(2);
    }, 900));
    state.guideTimers.push(window.setTimeout(function () {
      var tiles3 = guideTiles();
      tiles3[0].textContent = '가';
      guidePop(0);
      tiles3[1].classList.remove('is-target');
      el.guideNote.textContent = '③ 첫 글자도 한 칸 바꾸면 목표 단어 가지에 도착합니다. 여기서 데모가 멈춥니다.';
      setGuideStep(3);
    }, 1800));
    state.guideTimers.push(window.setTimeout(function () {
      var tiles4 = guideTiles();
      tiles4[2].textContent = '가지';
    }, 2400));
  }

  function setGuideOpen(open, remember) {
    el.guideBody.hidden = !open;
    el.guideToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    el.guideToggle.textContent = open ? '접기' : '게임 방법';
    if (!open && remember) {
      try { localStorage.setItem(GUIDE_KEY, '1'); } catch (e) {}
    }
  }

  function initGuide() {
    var seen = null;
    try { seen = localStorage.getItem(GUIDE_KEY); } catch (e) { seen = null; }
    if (seen) {
      setGuideOpen(false, false);
      guideResetState();
      var tiles = guideTiles();
      tiles[0].textContent = '가';
      tiles[1].textContent = '지';
      tiles[2].textContent = '가지';
      tiles[1].classList.remove('is-target');
      setGuideStep(3);
      el.guideNote.textContent = '바꿀 칸을 탭하고 자모를 고르면 그 칸만 바뀝니다. 다시 보기로 데모를 볼 수 있습니다.';
      return;
    }
    setGuideOpen(true, false);
    playGuide();
  }

  /* ------------------------------------------------------------------ 날짜 */
  function checkDay() {
    var key = kstKey();
    if (key === state.todayKey) return;
    state.todayKey = key;
    if (state.mode !== 'daily') {
      paintRecord();
      return;
    }
    if (state.cleared || state.moves > 0) {
      el.dayBadge.hidden = false;
      el.dayBadge.textContent = '새 날짜 문제가 열렸습니다 · 이 판은 ' + dayLabel(state.dayKey) + ' 기록으로 남습니다.';
      paintRecord();
      setStatus(dayLabel(state.dayKey) + ' 문제로 시작했으니 이 판은 그날 기록으로 마칩니다. 새 문제는 다음 시작 때 열립니다.');
      return;
    }
    state.dayKey = key;
    loadPuzzle(todayDaily(), { dayKey: key, keepStreak: true });
    el.dayBadge.hidden = true;
    setStatus('날짜가 바뀌어 오늘의 새 문제가 열렸습니다.');
  }

  /* ---------------------------------------------------------------- 이벤트 */
  el.wordRow.addEventListener('click', function (event) {
    if (state.cleared) return;
    var target = event.target;
    if (!target || !target.closest) return;
    var syllable = target.closest('.hg-syl');
    if (syllable) {
      state.cell = { pos: Number(syllable.getAttribute('data-pos')), part: 'whole' };
      state.padTab = 'letter';
      state.letterCho = null;
      paint();
      return;
    }
    var cell = target.closest('.hg-part');
    if (!cell) return;
    state.cell = { pos: Number(cell.getAttribute('data-pos')), part: cell.getAttribute('data-part') };
    state.padTab = 'jamo';
    paint();
  });

  el.jamoKeys.addEventListener('click', function (event) {
    var button = event.target.closest ? event.target.closest('.hg-key') : null;
    if (!button) return;
    applyJamo(button.getAttribute('data-jamo') || '');
  });

  el.letterGrid.addEventListener('click', function (event) {
    var button = event.target.closest ? event.target.closest('.hg-key') : null;
    if (!button) return;
    applySyllable(button.getAttribute('data-syllable') || '');
  });

  el.padTabJamo.addEventListener('click', function () {
    state.padTab = 'jamo';
    if (state.cell && state.cell.part === 'whole') state.cell = { pos: state.cell.pos, part: 'cho' };
    paint();
  });

  el.padTabLetter.addEventListener('click', function () {
    state.padTab = 'letter';
    if (state.cell) state.cell = { pos: state.cell.pos, part: 'whole' };
    state.letterCho = null;
    paint();
  });

  el.letterChoRow.addEventListener('click', function (event) {
    var button = event.target.closest ? event.target.closest('.hg-cho') : null;
    if (!button) return;
    state.letterCho = button.getAttribute('data-cho');
    paint();
  });

  el.undoBtn.addEventListener('click', undo);
  el.hintBtn.addEventListener('click', showHint);
  el.resetBtn.addEventListener('click', resetRun);

  el.modeDaily.addEventListener('click', function () { setMode('daily'); });
  el.modePractice.addEventListener('click', function () { setMode('practice'); });

  el.nextBtn.addEventListener('click', function () {
    if (state.mode === 'daily') {
      setMode('practice');
      setStatus('자유 연습으로 이동했습니다. 아래 목록에서 판을 골라 보세요.');
      return;
    }
    var next = nextPracticePuzzle();
    if (next) loadPuzzle(next, { keepStreak: true });
    else setMode('practice');
  });

  el.retryBtn.addEventListener('click', function () {
    if (state.mode === 'daily') {
      // 날짜가 바뀐 뒤에는 '다시 하기'가 오늘의 새 문제를 연다.
      state.dayKey = state.todayKey;
      loadPuzzle(todayDaily(), { keepStreak: true, dayKey: state.dayKey });
    } else {
      loadPuzzle(state.puzzle, { keepStreak: true });
    }
    setStatus('같은 문제를 다시 시작합니다. 최소 ' + state.par + '수에 도전하세요.');
  });

  el.practiceList.addEventListener('click', function (event) {
    var button = event.target.closest ? event.target.closest('.hg-practice-btn') : null;
    if (!button) return;
    var id = button.getAttribute('data-id');
    var puzzle = DATA.practice.filter(function (item) { return item.id === id; })[0];
    if (!puzzle) return;
    loadPuzzle(puzzle, { keepStreak: false });
    setStatus(puzzle.level + ' · ' + puzzle.title + ' · 최소 ' + puzzle.par + '수.');
  });

  el.guideToggle.addEventListener('click', function () {
    setGuideOpen(el.guideBody.hidden, true);
    if (!el.guideBody.hidden) playGuide();
  });

  el.guideReplay.addEventListener('click', function () {
    setGuideOpen(true, false);
    playGuide();
  });

  el.themeToggle.addEventListener('click', function () {
    var root = document.documentElement;
    var dark = root.getAttribute('data-theme') === 'dark';
    if (dark) root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', 'dark');
    try { localStorage.setItem('secjobs-theme', dark ? 'light' : 'dark'); } catch (e) {}
  });

  /* ------------------------------------------------------------------ 초기화 */
  state.store = readStore();
  state.todayKey = kstKey();
  state.dayKey = state.todayKey;
  initGuide();
  loadPuzzle(todayDaily(), { dayKey: state.dayKey, keepStreak: true });

  window.setInterval(checkDay, 60000);
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) checkDay();
  });
})();
"""


def build():
    kst_now = datetime.now(KST)
    data = build_data(kst_now)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__DATA_JSON__", payload)
            .replace("__JS__", JS))

    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(HANGUL_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "hangul")))

    index = (kst_now.date() - datetime(1970, 1, 1).date()).days % DAILY_COUNT
    today = data["daily"][index]
    levels = {}
    for puzzle in data["practice"]:
        levels[puzzle["level"]] = levels.get(puzzle["level"], 0) + 1

    print("-> 'hangul_data.json' 저장 완료 (단어 %d개 · 일일 %d판 · 연습 %d판)"
          % (len(data["words"]), len(data["daily"]), len(data["practice"])))
    print("-> 'hangul.html' 생성 완료 (오늘 %s · %s · %s→%s · 최소 %d수)"
          % (kst_now.date().isoformat(), today["id"], today["start"], today["goal"], today["par"]))
    return {
        "words": len(data["words"]),
        "daily": len(data["daily"]),
        "practice": len(data["practice"]),
        "levels": levels,
        "today": today["id"],
        "today_title": today["title"],
        "today_par": today["par"],
        "today_start": today["start"],
        "today_goal": today["goal"],
        "pars": sorted({item["par"] for item in data["daily"] + data["practice"]}),
    }


if __name__ == "__main__":
    build()

# -*- coding: utf-8 -*-
"""
하루 한 판 · 3단서 추리 (clue.html) 빌더.

문제의 원본은 SQLite DB(archive.db)의 clue_questions 테이블이다.
- 초기 시드 14문제(기술·생활·문화·과학·자연·역사)는 아래 SEEDS를 최초 1회 DB로 이관해 id를 그대로 보존한다.
- 매일 08:00 clue_generator.py 가 EXAONE으로 새 문제 1개를 추가하면 is_daily=1 로 쌓인다.

게임 방식
- 처음에는 단서 1만 열려 있고, '다음 단서 열기'를 누를 때마다 단서 2 → 3이 열린다.
- 4지선다에서 정답을 고르면 해설과 스포일러 없는 결과 문구(정답 텍스트 없음)가 열린다.
- 진행 기록(해결 여부·연 단서 수·시도 수)과 연속 해결일은 localStorage(secjobs-clue-v1)에만 저장한다.
"""
import json
import os
from datetime import datetime, timezone, timedelta
from html import escape as esc

from html_guard import harden_html, safe_json_for_script
import ui_shell
import game_guide

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLUE_HTML = os.path.join(BASE_DIR, "clue.html")

CATEGORIES = [
    {"key": "tech", "label": "기술"},
    {"key": "life", "label": "생활"},
    {"key": "culture", "label": "문화"},
    {"key": "science", "label": "과학"},
    {"key": "nature", "label": "자연"},
    {"key": "history", "label": "역사"},
]

SEEDS = [
    {
        "id": "seed-01", "puzzle_date": "2026-11-07", "category": "life",
        "title": "실패한 접착제가 책갈피가 된 날",
        "prompt": "자국 없이 붙였다 떼는 이 문구류는 무엇일까요?",
        "clues": [
            "1968년, 한 화학자는 아주 강한 접착제를 만들려 했지만 결과물은 손끝에 살짝 붙는 정도였다.",
            "이 물질은 사내에서 실패작으로 분류됐고, 동료가 찬송가 책의 페이지를 표시하는 데 쓰기 시작했다.",
            "1977년 시제품이 나왔고 1980년 전국 판매가 시작된 이 문구류는, 붙였다 떼도 자국이 남지 않는다.",
        ],
        "choices": ["포스트잇", "청테이프", "자석 메모홀더", "양면테이프"],
        "answer": 0,
        "explanation": "3M의 스펜서 실버는 1968년 강한 접착제를 만들려다 접착력이 약한 소재를 얻었습니다. 동료 아서 프라이가 찬송가 책갈피로 쓰면서 용도를 찾았고, 1980년 포스트잇으로 전국 판매되며 사무용 필수품이 됐습니다.",
    },
    {
        "id": "seed-02", "puzzle_date": "2026-11-08", "category": "nature",
        "title": "피가 파란 바다의 두뇌",
        "prompt": "이 동물은 무엇일까요?",
        "clues": [
            "심장이 세 개이고, 산소를 나르는 단백질이 구리를 품어 피가 푸르게 보이는 무척추동물이다.",
            "몸 표면의 색소 세포를 0.2초 만에 바꿔 주변 환경과 감정을 표현한다.",
            "뉴런의 3분의 2가 다리에 몰려 있어, 다리 하나만 떼어 내도 먹이를 향해 움직인다.",
        ],
        "choices": ["문어", "오징어", "해파리", "불가사리"],
        "answer": 0,
        "explanation": "문어는 헤모시아닌 때문에 피가 파랗고 심장이 세 개입니다. 중앙 뇌보다 다리의 신경이 많아 분산형 지능을 갖춘 것으로 알려져 있습니다. 오징어도 피는 푸르지만 다리가 열 개입니다.",
    },
    {
        "id": "seed-03", "puzzle_date": "2026-11-09", "category": "life",
        "title": "성을 지킨 검은 물",
        "prompt": "이 음료는 무엇일까요?",
        "clues": [
            "17세기 후반, 한 도시를 포위했던 군대가 철수하며 자루에 든 검은 낟알을 남겨 두었다.",
            "도시 사람들은 처음엔 이 낟알을 낙타 사료로 여겼지만, 끓인 물의 향에 끌려 마시기 시작했다.",
            "이후 유럽에 퍼진 이 음료는 악마의 음료라 불리다가, 오늘날 아침을 여는 대표 음료가 됐다.",
        ],
        "choices": ["커피", "홍차", "코코아", "맥주"],
        "answer": 0,
        "explanation": "1683년 빈을 포위했던 오스만 군대가 철수하며 남긴 자루가 커피였다는 이야기가 전해집니다. 터키식으로 끓여 마시는 법이 유럽에 퍼지며 커피하우스 문화가 시작됐습니다.",
    },
    {
        "id": "seed-04", "puzzle_date": "2026-11-10", "category": "science",
        "title": "달력이 맞추지 못한 여섯 시간",
        "prompt": "4년에 한 번만 오는 이 날짜는 언제일까요?",
        "clues": [
            "지구가 태양을 한 바퀴 도는 데 걸리는 시간은 달력의 1년보다 약 6시간 길다.",
            "이 차이를 그대로 두면 계절이 조금씩 밀려나, 100년이면 24일가량 어긋난다.",
            "그래서 4년마다 하루를 더 넣는데, 그날이 있는 해는 연도가 4의 배수인지로 판단한다.",
        ],
        "choices": ["2월 29일", "12월 31일", "1월 1일", "6월 31일"],
        "answer": 0,
        "explanation": "1년은 365.2422일이라 4년마다 약 하루가 남습니다. 그래서 윤년에 2월 29일을 넣고, 100의 배수 해는 윤년에서 빼되 400의 배수 해는 다시 포함합니다.",
    },
    {
        "id": "seed-05", "puzzle_date": "2026-11-11", "category": "culture",
        "title": "1999년 일본에서 태어난 176개의 그림",
        "prompt": "이 그림 문자는 무엇일까요?",
        "clues": [
            "휴대전화 화면의 12×12 격자를 채우려고 그린 작은 그림들이 시작이었다.",
            "1999년 한 일본 통신사의 디자이너가 176개를 완성했고, 문자처럼 보내며 메시지 문화를 바꿨다.",
            "2010년 유니코드 표준에 들어가 기기와 나라를 넘어 같은 그림으로 보이게 됐고, 지금은 3,700개를 넘는다.",
        ],
        "choices": ["이모지", "카오모지", "아스키 아트", "픽토그램"],
        "answer": 0,
        "explanation": "일본 통신사 NTT도코모가 1999년 176개의 그림 문자를 만들면서 이모지가 시작됐습니다. 이후 유니코드에 등재되며 애플·구글 기기에서 같은 코드로 표현됩니다.",
    },
    {
        "id": "seed-06", "puzzle_date": "2026-11-12", "category": "tech",
        "title": "주머니 속에서 살아남는 얇은 판",
        "prompt": "휴대전화 앞면을 덮는 이 유리는 무엇일까요?",
        "clues": [
            "두께가 1mm 남짓인데도 바닥에 떨어뜨려도 쉽게 깨지지 않아, 휴대전화 앞면을 덮는다.",
            "일반 유리를 400도 부근의 용융염에 담그면 표면의 작은 이온이 더 큰 이온으로 바뀐다.",
            "표면이 눌린 상태로 굳어 생긴 압축층이 흠을 막아, 같은 두께의 보통 유리보다 훨씬 질기다.",
        ],
        "choices": ["강화유리", "아크릴", "폴리카보네이트", "사파이어 유리"],
        "answer": 0,
        "explanation": "이온 교환으로 표면에 압축 응력을 만든 강화유리입니다. 1960년대 코닝이 개발한 이 공정은 오늘날 스마트폰 커버 글래스의 기본이 됐습니다.",
    },
    {
        "id": "seed-07", "puzzle_date": "2026-11-13", "category": "history",
        "title": "백성이 글을 읽게 하려고 만든 28자",
        "prompt": "이 문자는 무엇일까요?",
        "clues": [
            "1443년, 한 왕이 백성이 글을 몰라 억울한 일을 겪는 것을 안타깝게 여겨 직접 만들었다.",
            "처음에는 기본 자모가 28자였고, 하늘·땅·사람의 모양을 본떠 만든 자음이 들어갔다.",
            "창제 당시 이름은 《훈민정음》이며, 오늘날 24자로 정리되어 국어를 적는 데 쓰인다.",
        ],
        "choices": ["한글", "한자", "키릴 문자", "가나"],
        "answer": 0,
        "explanation": "세종이 1443년 창제하고 1446년 《훈민정음》으로 반포했습니다. 자음은 발음 기관의 모양을, 모음은 하늘·땅·사람을 본떴으며 지금은 자모 24자를 씁니다.",
    },
    {
        "id": "seed-08", "puzzle_date": "2026-11-14", "category": "nature",
        "title": "우주에서 보이는 살아 있는 구조",
        "prompt": "이 구조는 무엇일까요?",
        "clues": [
            "2,000km 넘게 이어지는 이 구조는 흙이나 돌이 아니라 살아 있는 생물이 만든 것이다.",
            "작은 생물과 그 몸속에 사는 조류가 함께 살며 탄산칼슘 껍데기를 쌓아 만든다.",
            "호주 동북 해안에 있고 1981년 유네스코 세계유산이 됐으며, 수온 상승으로 백화가 반복된다.",
        ],
        "choices": ["그레이트 배리어 리프", "미드-아틀란틱 릿지", "사하라 사막", "아마존 열대우림"],
        "answer": 0,
        "explanation": "산호 폴립과 공생 조류가 만든 그레이트 배리어 리프는 2,300km에 걸쳐 이어지는 세계 최대 산호초 지대입니다. 수온 상승으로 산호 백화가 반복되고 있습니다.",
    },
    {
        "id": "seed-09", "puzzle_date": "2026-11-15", "category": "tech",
        "title": "사진 한 장에 숨은 2,000자",
        "prompt": "사진 파일에 함께 저장되는 이 정보는 무엇일까요?",
        "clues": [
            "이미지 파일을 열면 눈에 보이는 사진 뒤에 작은 글자 데이터가 함께 들어 있다.",
            "찍은 시각, 기기 이름, 조리개 값, 때로는 촬영 위치 좌표까지 기록된다.",
            "올리는 서비스에 따라 이 정보가 지워지기도 하는데, 그대로 두면 집 위치가 드러날 수 있다.",
        ],
        "choices": ["EXIF", "썸네일", "해시태그", "메타 태그"],
        "answer": 0,
        "explanation": "EXIF는 카메라와 휴대전화가 사진에 남기는 촬영 정보입니다. 위치 좌표와 기기 정보까지 담을 수 있어, 공개 게시 전 제거 여부를 확인하는 것이 좋습니다.",
    },
    {
        "id": "seed-10", "puzzle_date": "2026-11-16", "category": "culture",
        "title": "한 장의 종이를 접어 만드는 1,000개의 모양",
        "prompt": "이 놀이는 무엇일까요?",
        "clues": [
            "6세기 무렵 종이와 함께 전해져 예법과 놀이로 자리 잡은 종이 문화다.",
            "같은 종이라도 접는 순서에 따라 모양이 달라져, 1,000개를 접으면 소원이 이뤄진다는 이야기가 있다.",
            "2010년대에는 이 접는 방식을 응용해 접히는 태양광 패널과 의료 기구까지 설계된다.",
        ],
        "choices": ["종이접기", "페이퍼 커팅", "종이죽 공예", "다도"],
        "answer": 0,
        "explanation": "일본의 오리가미는 에도 시대에 대중화됐고, 학 1,000마리 전설은 지금도 세계에 퍼져 있습니다. 현대에는 접기 구조가 공학 설계에도 쓰입니다.",
    },
    {
        "id": "seed-11", "puzzle_date": "2026-11-17", "category": "nature",
        "title": "절반만 잠드는 바다의 숨",
        "prompt": "이 동물은 무엇일까요?",
        "clues": [
            "포유류라서 물 밖에서 숨을 쉬어야 하지만, 바다에서 평생 산다.",
            "잠을 잘 때 뇌의 절반만 재우고, 나머지 절반은 숨을 쉬게 한다.",
            "잠자는 동안 한쪽 눈을 뜨고 헤엄치며, 무리와 함께 조류를 따라 움직인다.",
        ],
        "choices": ["돌고래", "바다거북", "상어", "물개"],
        "answer": 0,
        "explanation": "돌고래는 반구 교대 수면을 합니다. 한쪽 뇌가 깨어 숨을 관리하고 다른 쪽은 쉬며, 잠자는 동안에도 몸이 가라앉지 않도록 움직입니다.",
    },
    {
        "id": "seed-12", "puzzle_date": "2026-11-18", "category": "history",
        "title": "1844년, 네 단어가 바꾼 거리",
        "prompt": "이 통신 장치는 무엇일까요?",
        "clues": [
            "1844년 5월, 워싱턴에서 볼티모어까지 철도 옆에 깔린 선을 따라 신호가 전해졌다.",
            "메시지는 What hath God wrought 네 단어였고, 60km 거리가 순식간에 닿았다.",
            "점과 선의 조합으로 글자를 보내는 이 방식은 이후 해저 케이블과 통신의 기초가 됐다.",
        ],
        "choices": ["전신기", "전화기", "팩시밀리", "라디오"],
        "answer": 0,
        "explanation": "새뮤얼 모스의 전신기가 1844년 5월 24일 시연됐습니다. 모스 부호는 점과 선의 길이 조합으로 글자를 전달하며 통신의 첫 표준 부호가 됐습니다.",
    },
    {
        "id": "seed-13", "puzzle_date": "2026-11-19", "category": "tech",
        "title": "두 자리 숫자가 만든 세기의 소동",
        "prompt": "이 문제는 무엇이라고 부를까요?",
        "clues": [
            "저장 공간을 아끼려고 연도를 1999 대신 99처럼 뒤 두 자리로만 저장하던 관행이 있었다.",
            "2000년이 되면 이 값이 00이 되어 시스템이 1900년으로 읽을 수 있다는 우려가 퍼졌다.",
            "1999년 말 전 세계가 대비했고, 큰 사고 없이 넘어가자 과대포장이었다는 말도 나왔다.",
        ],
        "choices": ["밀레니엄 버그(Y2K)", "윤초", "랜섬웨어", "데드락"],
        "answer": 0,
        "explanation": "Y2K 문제는 연도 두 자리 저장 방식이 2000년에 1900으로 해석될 수 있다는 우려였습니다. 점검 비용은 컸지만 미리 고쳐 둔 덕에 실제 피해는 제한적이었습니다.",
    },
    {
        "id": "seed-14", "puzzle_date": "2026-11-20", "category": "science",
        "title": "1초를 다시 정의한 진동",
        "prompt": "이 원자는 무엇일까요?",
        "clues": [
            "1967년 국제도량형총회는 1초의 기준을 지구 자전에서 다른 것으로 바꿨다.",
            "어떤 원자의 두 에너지 상태 사이를 오갈 때 나오는 전자기파의 진동 수를 세기로 했다.",
            "그 원자는 이 원소이며, 이 진동이 9,192,631,770번 일어나는 시간을 1초로 정했다.",
        ],
        "choices": ["세슘", "수소", "루비듐", "우라늄"],
        "answer": 0,
        "explanation": "세슘-133 원자의 특정 전이 진동 9,192,631,770회가 1초입니다. 원자 시계는 이 진동을 세어 지구 자전보다 안정적인 시간 기준을 제공합니다.",
    },
]


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
      --no-bg: #fef2f2;  --no-text: #b91c1c;  --no-border: #fecaca;

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04);

      --cat-tech: #2563eb;
      --cat-life: #059669;
      --cat-culture: #7c3aed;
      --cat-science: #0891b2;
      --cat-nature: #65a30d;
      --cat-history: #b45309;
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
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);

      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
      --card-shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }

    html { scroll-behavior: smooth; }

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

    .navbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    .nav-container {
      max-width: 1360px;
      margin: 0 auto;
      padding: 0 20px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }

    .brand-logo-img {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      object-fit: cover;
      display: block;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
      flex-shrink: 0;
    }

    .brand-name {
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      white-space: nowrap;
    }

    .nav-tabs {
      display: flex;
      gap: 5px;
      margin-left: 10px;
      flex: 1 1 auto;
      min-width: 0;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }

    .nav-tabs::-webkit-scrollbar { display: none; }

    .nav-tab-item {
      padding: 5px 10px;
      border-radius: 18px;
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      color: var(--text-secondary);
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .nav-tab-item:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .nav-tab-item.active { background: var(--accent-primary); color: #ffffff !important; }

    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .update-meta {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
      white-space: nowrap;
    }

    .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      display: inline-block;
      flex-shrink: 0;
    }

    .icon-btn {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
      text-decoration: none;
    }

    .icon-btn:hover {
      background: var(--bg-subtle);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }

    .container { max-width: 820px; margin: 0 auto; padding: 32px 20px 80px; }

    .hero { margin-bottom: 18px; }

    .hero-pill {
      display: inline-block;
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 9px;
      margin-bottom: 12px;
    }

    .hero-title { font-size: 26px; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 8px; }

    .hero-desc {
      font-size: 14.5px;
      color: var(--text-secondary);
      line-height: 1.65;
      margin-bottom: 14px;
      max-width: 720px;
    }

    .hero-stats { display: flex; flex-wrap: wrap; gap: 8px; }

    .stat-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .stat-chip strong { color: var(--text-primary); font-weight: 600; }

    .panel {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      box-shadow: var(--card-shadow);
      margin-bottom: 14px;
      min-width: 0;
    }

    .player { padding: 20px; }

    .player-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .player-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0; }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: 999px;
      border: 1px solid var(--border-default);
      background: var(--bg-page);
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .badge::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
      flex-shrink: 0;
    }

    .badge.cat-tech::before { background: var(--cat-tech); }
    .badge.cat-life::before { background: var(--cat-life); }
    .badge.cat-culture::before { background: var(--cat-culture); }
    .badge.cat-science::before { background: var(--cat-science); }
    .badge.cat-nature::before { background: var(--cat-nature); }
    .badge.cat-history::before { background: var(--cat-history); }

    .player-date { font-size: 12px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    .today-tag {
      font-size: 10.5px;
      font-weight: 600;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border-radius: 5px;
      padding: 2px 7px;
    }

    .dots { display: flex; align-items: center; gap: 5px; }

    .dots .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--bg-muted);
      display: block;
      transition: background-color 0.2s ease;
    }

    .dots .dot.on { background: var(--accent-primary); }

    .player-title { font-size: 19px; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 14px; }

    .clues { display: flex; flex-direction: column; gap: 8px; }

    .clue {
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 12px 14px;
      background: var(--bg-surface);
      min-width: 0;
    }

    .clue.open { background: var(--bg-page); }

    .clue.locked {
      border-style: dashed;
      background: transparent;
    }

    .clue-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 5px;
    }

    .clue-label {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.01em;
      color: var(--accent-primary);
    }

    .clue.locked .clue-label { color: var(--text-muted); }

    .clue-step { font-size: 10.5px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    .clue-text { font-size: 13.5px; line-height: 1.65; color: var(--text-primary); }

    .clue.locked .clue-text { color: var(--text-muted); font-size: 12.5px; }

    .clue-foot {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 12px;
      flex-wrap: wrap;
    }

    .btn {
      font-family: inherit;
      border-radius: 9px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: -0.02em;
      padding: 9px 16px;
      cursor: pointer;
      transition: all 0.15s ease;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-primary);
      white-space: nowrap;
    }

    .btn:hover { background: var(--bg-subtle); border-color: var(--border-strong); }

    .btn:disabled { opacity: 0.5; cursor: default; }

    .btn-line { border-color: var(--border-strong); }

    .btn-primary {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      color: #ffffff;
    }

    .btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }

    .btn-text {
      font-family: inherit;
      border: none;
      background: none;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      padding: 4px 2px;
      cursor: pointer;
      text-decoration: underline;
      text-underline-offset: 3px;
    }

    .btn-text:hover { color: var(--text-primary); }

    .clue-note { font-size: 11.5px; color: var(--text-muted); }

    .ask {
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
    }

    .ask-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 6px;
    }

    .ask-label { font-size: 11px; font-weight: 700; letter-spacing: 0.02em; color: var(--text-muted); }

    .ask-hint { font-size: 11.5px; color: var(--text-muted); }

    .ask-q { font-size: 15px; font-weight: 600; margin-bottom: 10px; }

    .options { display: flex; flex-direction: column; gap: 7px; }

    .opt {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      text-align: left;
      font-family: inherit;
      font-size: 13.5px;
      font-weight: 500;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 11px 13px;
      cursor: pointer;
      transition: all 0.15s ease;
      min-width: 0;
    }

    .opt:hover { border-color: var(--border-strong); background: var(--bg-subtle); }

    .opt:disabled { cursor: default; }

    .opt .key {
      flex: 0 0 20px;
      width: 20px;
      height: 20px;
      border-radius: 6px;
      background: var(--bg-subtle);
      color: var(--text-secondary);
      font-size: 10.5px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .opt .body { min-width: 0; flex: 1 1 auto; }

    .opt.is-correct {
      border-color: var(--ok-border);
      background: var(--ok-bg);
      color: var(--ok-text);
    }

    .opt.is-correct .key { background: var(--ok-border); color: var(--ok-text); }

    .opt.is-wrong {
      border-color: var(--no-border);
      background: var(--no-bg);
      color: var(--no-text);
    }

    .opt.is-wrong .key { background: var(--no-border); color: var(--no-text); }

    .ask-foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-top: 10px;
      flex-wrap: wrap;
    }

    .ask-msg { font-size: 12px; color: var(--text-secondary); }
    .ask-msg.no { color: var(--no-text); }

    .result {
      margin-top: 16px;
      border: 1px solid var(--ok-border);
      background: var(--ok-bg);
      border-radius: 12px;
      padding: 15px 16px;
    }

    .result.gave-up { border-color: var(--border-strong); background: var(--bg-page); }

    .result-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }

    .result-badge {
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 5px;
      background: var(--ok-text);
      color: #ffffff;
    }

    .result.gave-up .result-badge { background: var(--text-muted); }

    .result-title { font-size: 14px; font-weight: 700; color: var(--ok-text); }

    .result.gave-up .result-title { color: var(--text-primary); }

    .result-answer { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }

    .result-answer strong { color: var(--text-primary); font-size: 14px; }

    .result-explain { font-size: 13px; line-height: 1.65; color: var(--text-primary); margin-bottom: 12px; }

    .share {
      display: flex;
      align-items: center;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid var(--border-default);
      flex-wrap: wrap;
    }

    .share-preview {
      flex: 1 1 240px;
      min-width: 0;
      font-size: 11.5px;
      line-height: 1.55;
      color: var(--text-secondary);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 8px;
      padding: 8px 10px;
      white-space: pre-line;
      word-break: break-word;
    }

    .share-note { font-size: 11px; color: var(--text-muted); margin-top: 8px; }

    .archive { padding: 18px 20px 20px; }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .panel-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; }

    .panel-title .bar {
      width: 3px;
      height: 14px;
      border-radius: 2px;
      background: var(--accent-primary);
      display: inline-block;
    }

    .panel-meta { font-size: 11.5px; color: var(--text-muted); }

    .chips { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 12px; }

    .chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      border: 1px solid var(--border-default);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: -0.02em;
      padding: 5px 11px;
      border-radius: 16px;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .chip:hover { border-color: var(--border-strong); color: var(--text-primary); }

    .chip.active { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }

    .chip em { font-style: normal; font-size: 10.5px; font-variant-numeric: tabular-nums; opacity: 0.62; }

    .arc-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }

    .arc-card {
      display: flex;
      flex-direction: column;
      gap: 6px;
      text-align: left;
      font-family: inherit;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 10px;
      padding: 12px 13px;
      cursor: pointer;
      transition: all 0.15s ease;
      min-width: 0;
    }

    .arc-card:hover { border-color: var(--border-strong); box-shadow: var(--card-shadow-hover); }

    .arc-card.current { border-color: var(--accent-primary); }

    .arc-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }

    .arc-date { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }

    .arc-title {
      font-size: 13px;
      font-weight: 600;
      line-height: 1.45;
      color: var(--text-primary);
      word-break: keep-all;
    }

    .arc-state { font-size: 11px; color: var(--text-muted); }
    .arc-state.done { color: var(--ok-text); font-weight: 600; }

    .empty { font-size: 12.5px; color: var(--text-muted); padding: 10px 2px; }

    .footer {
      margin-top: 22px;
      padding-top: 16px;
      border-top: 1px solid var(--border-default);
      font-size: 11.5px;
      line-height: 1.7;
      color: var(--text-muted);
    }

    @media (max-width: 640px) {
      .nav-container { padding: 0 12px; height: 54px; gap: 6px; }
      .brand-logo-img { width: 24px; height: 24px; }
      .brand-name { font-size: 15px; }
      .nav-tabs { margin-left: 6px; gap: 4px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; border-radius: 14px; }
      .update-meta { display: none !important; }
      .nav-actions a.icon-btn { display: none; }
      .container { padding: 18px 12px 60px; }
      .hero-title { font-size: 21px; }
      .hero-desc { font-size: 13px; line-height: 1.6; }
      .hero-stats { gap: 6px; }
      .stat-chip { font-size: 11px; padding: 3px 8px; }
      .player { padding: 15px 14px; border-radius: 12px; }
      .player-title { font-size: 16.5px; }
      .clue { padding: 11px 12px; }
      .clue-text { font-size: 12.8px; }
      .ask-q { font-size: 14px; }
      .opt { font-size: 12.8px; padding: 10px 11px; }
      .share { flex-direction: column; align-items: stretch; }
      .share-preview { flex: 1 1 auto; }
      .share .btn-primary { width: 100%; }
      .archive { padding: 15px 14px 16px; border-radius: 12px; }
      .arc-grid { grid-template-columns: minmax(0, 1fr); }
      .arc-title { font-size: 12.5px; }
    }

    @media (max-width: 560px) {
      .brand-name { display: none; }
    }

    @media (max-width: 1440px) {
      .nav-container { max-width: 1360px; padding: 0 16px; }
      .nav-tabs { gap: 4px; margin-left: 8px; }
      .nav-tab-item { padding: 4px 8px; font-size: 11.5px; }
    }

    @media (max-width: 1024px) {
      .nav-brand { min-width: 0; }
      .nav-tabs { flex: 1 1 auto; min-width: 0; overflow-x: auto; white-space: nowrap; scrollbar-width: none; -ms-overflow-style: none; }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 7px; font-size: 11px; }
    }

    @media (max-width: 430px) {
      .nav-container { padding: 0 8px; height: 52px; gap: 4px; }
      .brand-logo-img { width: 22px; height: 22px; }
      .nav-tabs {
        margin-left: 2px;
        gap: 1px;
        flex: 1 1 auto;
        min-width: 0;
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
      }
      .nav-tabs::-webkit-scrollbar { display: none; }
      .nav-tab-item { padding: 4px 5px; font-size: 10px; border-radius: 11px; letter-spacing: -0.045em; }
      .nav-actions { gap: 4px; }
      .nav-actions .icon-btn { width: 28px; height: 28px; }
    }

    /* ===== 2차 UI/UX: PC 2단(좌 플레이어 ↔ 우 지난 문제 레일) · 모바일 1줄 요약 ===== */
    .clue-overview {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 18px;
    }
    .clue-overview-copy { min-width: 0; }
    .clue-overview .hero-pill { margin-bottom: 10px; }
    .clue-overview .hero-title { margin-bottom: 6px; }
    .clue-overview .hero-desc { margin-bottom: 0; }

    .clue-kpis { display: flex; gap: 8px; flex: 0 0 auto; }
    .clue-kpi {
      min-width: 92px;
      padding: 8px 12px 9px;
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 12px;
      box-shadow: var(--card-shadow);
    }
    .clue-kpi-label { display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 2px; white-space: nowrap; }
    .clue-kpi-value { font-size: 16px; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); font-variant-numeric: tabular-nums; white-space: nowrap; }

    .clue-layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 336px;
      gap: 20px;
      align-items: start;
    }
    .clue-main { min-width: 0; }
    .clue-main .player { margin-bottom: 0; }

    .clue-rail {
      position: sticky;
      top: 78px;
      display: flex;
      flex-direction: column;
      max-height: calc(100vh - 98px);
      min-width: 0;
    }
    .clue-rail .archive {
      display: flex;
      flex-direction: column;
      margin-bottom: 0;
      min-height: 0;
      padding: 16px;
    }
    .clue-rail .chips { margin-bottom: 10px; gap: 4px; }
    .clue-rail .chip { padding: 4px 9px; font-size: 11px; border-radius: 8px; }
    .clue-rail .arc-grid {
      display: flex;
      flex-direction: column;
      gap: 5px;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: thin;
      min-height: 0;
      padding: 1px;
    }
    .clue-rail .arc-card { padding: 9px 10px; gap: 4px; border-radius: 9px; }
    .clue-rail .arc-title { font-size: 12px; }
    .clue-rail .arc-date,
    .clue-rail .arc-state { font-size: 10.5px; }

    @media (min-width: 1024px) {
      .container { max-width: 1200px; }
      .clue-layout { grid-template-columns: minmax(0, 1fr) 320px; }
    }

    @media (max-width: 1023px) {
      .clue-overview-copy { display: none; }
      .clue-overview { margin-bottom: 10px; }
      .clue-kpis { flex: 1 1 auto; gap: 6px; }
      .clue-kpi { flex: 1 1 0; min-width: 0; padding: 7px 10px; }
      .clue-kpi-label { font-size: 10.5px; }
      .clue-kpi-value { font-size: 14px; }
      .clue-layout { grid-template-columns: minmax(0, 1fr); gap: 14px; }
      .clue-rail { position: static; max-height: none; }
      .clue-rail .arc-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
        overflow: visible;
      }
      .clue-rail .arc-card { padding: 11px 12px; }
      .clue-rail .arc-title { font-size: 13px; }
    }

    @media (max-width: 640px) {
      .clue-rail .arc-grid { grid-template-columns: minmax(0, 1fr); }
    }
""" + game_guide.GUIDE_CSS + r"""
    /* ----- 3단서 추리: 단서 타임라인·즉시 피드백·결과 격차 ----- */
    .clue-track { display: flex; align-items: center; gap: 0; }
    .track-step {
      display: inline-flex; align-items: center; gap: 4px;
      font-size: 9.5px; font-weight: 600; color: var(--text-muted); white-space: nowrap;
      transition: color 160ms ease;
    }
    .track-step .dot {
      width: 7px; height: 7px; border-radius: 50%; background: var(--bg-muted);
      display: block; transition: background-color 160ms ease, transform 160ms ease;
    }
    .track-step.is-on { color: var(--accent-primary); }
    .track-step.is-on .dot { background: var(--accent-primary); }
    .track-step.is-pop .dot { animation: clueDotPop 340ms ease; }
    .track-line { width: 10px; height: 1px; background: var(--border-default); margin: 0 3px; flex: 0 0 auto; }
    @keyframes clueDotPop { 0% { transform: scale(1); } 45% { transform: scale(1.7); } 100% { transform: scale(1); } }

    .clue-flash {
      display: flex; align-items: center; gap: 6px; margin-bottom: 8px; padding: 7px 9px;
      border-radius: 9px; font-size: 11.5px; font-weight: 600; line-height: 1.45;
      border: 1px solid var(--border-default); background: var(--bg-page); color: var(--text-primary);
    }
    .clue-flash.ok { border-color: var(--ok-border); background: var(--ok-bg); color: var(--ok-text); }
    .clue-flash.no { border-color: var(--no-border); background: var(--no-bg); color: var(--no-text); }
    .clue-flash-tag {
      flex: 0 0 auto; font-size: 9px; font-weight: 700; padding: 1px 5px; border-radius: 4px;
      background: var(--accent-subtle); color: var(--accent-primary);
    }
    .clue-flash.ok .clue-flash-tag { background: var(--ok-text); color: #ffffff; }
    .clue-flash.no .clue-flash-tag { background: var(--no-text); color: #ffffff; }

    .clue.is-fresh { animation: cluePop 380ms ease; }
    .clue.is-fresh .clue-label { color: var(--accent-primary); }
    @keyframes cluePop { 0% { transform: translateY(-3px); opacity: 0.4; } 100% { transform: none; opacity: 1; } }

    .clue-demo { display: flex; align-items: center; gap: 5px; }
    .clue-demo-card {
      flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; gap: 1px;
      padding: 5px 6px; border-radius: 7px; border: 1px dashed var(--border-default);
      background: var(--bg-surface); color: var(--text-muted);
      transition: border-color 160ms ease, background-color 160ms ease, color 160ms ease;
    }
    .clue-demo-card b { font-size: 9px; font-weight: 700; }
    .clue-demo-card i { font-style: normal; font-size: 10.5px; font-weight: 600; }
    .clue-demo-card.is-open {
      border-style: solid; border-color: var(--accent-primary);
      background: var(--accent-subtle); color: var(--accent-primary);
    }
    .clue-demo-pick {
      flex: 0 0 auto; align-self: center; font-size: 9px; font-weight: 700; color: #15803d;
      background: #dcfce7; border: 1px solid #86efac; border-radius: 6px; padding: 3px 5px;
    }

    .result-gap {
      display: flex; align-items: flex-start; gap: 6px; margin: 0 0 10px;
      font-size: 12px; font-weight: 600; line-height: 1.5; color: var(--text-primary);
    }
    .result-gap-tag {
      flex: 0 0 auto; font-size: 9px; font-weight: 700; padding: 1px 5px; border-radius: 4px;
      background: var(--bg-surface); border: 1px solid var(--border-default); color: var(--accent-primary);
    }
    .result-acts { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); gap: 6px; margin-top: 10px; }
    .result-acts button {
      font-family: inherit; font-size: 12.5px; font-weight: 700; padding: 10px 6px;
      border-radius: 9px; border: 1px solid var(--border-default);
      background: var(--bg-surface); color: var(--text-primary); cursor: pointer; white-space: nowrap;
    }
    .result-acts .result-next { background: var(--accent-primary); border-color: var(--accent-primary); color: #ffffff; }
    @media (prefers-reduced-motion: reduce) {
      .track-step, .track-step .dot, .clue-demo-card { transition: none !important; }
      .track-step.is-pop .dot, .clue.is-fresh { animation: none !important; }
    }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 하루 한 판 3단서 추리</title>
  <meta name="description" content="매일 한 문제, 단서 세 개로 답을 맞히는 1분 추리 게임. 첫 단서만 열린 상태에서 시작해 필요할 때 다음 단서를 열고, 적게 열수록 좋은 기록입니다. 기술·생활·문화·과학·자연·역사 분야의 지난 문제를 다시 풀고 연속 해결 기록을 남길 수 있습니다.">
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
        <div class="nav-tabs">
          <a href="index.html" class="nav-tab-item">채용공고</a>
          <a href="study.html" class="nav-tab-item">시험 공부</a>
          <a href="ai.html" class="nav-tab-item">AI 트렌드</a>
          <a href="cve.html" class="nav-tab-item">CVE 리포트</a>
          <a href="outfit.html" class="nav-tab-item">옷차림</a>
          <a href="wargame.html" class="nav-tab-item">워게임</a>
          <a href="tools.html" class="nav-tab-item">실무 유틸</a>
          <a href="radar.html" class="nav-tab-item">피싱 레이더</a>
          <a href="pick.html" class="nav-tab-item">오늘 뭐 먹지</a>
          <a href="clue.html" class="nav-tab-item active">3단서 추리</a>
          <a href="mission.html" class="nav-tab-item">퇴근길 미션</a>
          <a href="chart.html" class="nav-tab-item">차트 추리실</a>
        </div>
      </div>

      <div class="nav-actions">
        <div class="update-meta">
          <span class="live-dot"></span>
          <span>매일 08:00 새 문제</span>
        </div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path>
          </svg>
        </a>
      </div>
    </div>
  </header>

  <script>
    // 좁은 화면에서 현재 페이지 탭이 가려지지 않도록 탭 영역만 살짝 스크롤한다.
    (function () {
      function keepActiveTabVisible() {
        var box = document.querySelector('.nav-tabs');
        if (!box) return;
        var act = box.querySelector('.nav-tab-item.active');
        if (!act || box.scrollWidth <= box.clientWidth) return;
        var br = box.getBoundingClientRect();
        var ar = act.getBoundingClientRect();
        if (ar.right > br.right) box.scrollLeft += (ar.right - br.right) + 8;
        else if (ar.left < br.left) box.scrollLeft -= (br.left - ar.left) + 8;
      }
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', keepActiveTabVisible);
      else keepActiveTabVisible();
      window.addEventListener('resize', keepActiveTabVisible);
    })();
  </script>

  <main class="container">

    <section class="clue-overview">
      <div class="clue-overview-copy">
        <span class="hero-pill">DAILY PUZZLE</span>
        <h1 class="hero-title">하루 한 판 · 3단서 추리</h1>
        <p class="hero-desc">단서는 세 개, 시간은 1분. 첫 단서만 열린 채로 시작해 필요할 때 다음 단서를 열고, 적게 열고 맞힐수록 기록이 좋습니다. 정답을 고르면 해설이 열리고, 정답을 담지 않은 결과 문구를 복사해 공유할 수 있습니다. 지난 문제는 분야별로 골라 다시 풀 수 있습니다.</p>
      </div>
      <div class="clue-kpis" aria-label="추리 기록 요약">
        <div class="clue-kpi">
          <span class="clue-kpi-label">오늘 분야</span>
          <span class="clue-kpi-value">__TODAY_CAT__</span>
        </div>
        <div class="clue-kpi">
          <span class="clue-kpi-label">연속</span>
          <span class="clue-kpi-value" id="streakNum">0일</span>
        </div>
        <div class="clue-kpi">
          <span class="clue-kpi-label">해결</span>
          <span class="clue-kpi-value" id="solvedStat">0 / __TOTAL__</span>
        </div>
      </div>
    </section>

    <div class="clue-layout">
      <div class="clue-main">

    __GUIDE__

    <section class="panel player" id="playPanel" aria-label="3단서 추리 플레이어">
      <div class="player-top">
        <div class="player-meta">
          <span class="badge" id="pCat">분야</span>
          <span class="player-date" id="pDate">—</span>
          <span class="today-tag" id="pToday" hidden>오늘의 문제</span>
        </div>
        <div class="clue-track" id="pDots" aria-label="열린 단서 수">
          <span class="track-step is-on" data-step="1"><i class="dot on"></i>1 사건</span>
          <span class="track-line"></span>
          <span class="track-step" data-step="2"><i class="dot"></i>2 정황</span>
          <span class="track-line"></span>
          <span class="track-step" data-step="3"><i class="dot"></i>3 결정</span>
        </div>
      </div>
      <h2 class="player-title" id="pTitle">문제를 불러오는 중입니다</h2>

      <div class="clue-flash" id="clueFlash" role="status" aria-live="polite" hidden></div>
      <div class="clues" id="clueList"></div>

      <div class="clue-foot">
        <button class="btn btn-line" id="nextClue" type="button">다음 단서 열기</button>
        <span class="clue-note" id="clueNote">단서를 적게 열수록 기록이 좋아집니다</span>
      </div>

      <div class="ask">
        <div class="ask-head">
          <span class="ask-label">정답 고르기</span>
          <span class="ask-hint" id="triesText"></span>
        </div>
        <p class="ask-q" id="pPrompt"></p>
        <div class="options" id="options"></div>
        <div class="ask-foot">
          <span class="ask-msg" id="askMsg"></span>
          <button class="btn-text" id="giveUp" type="button">정답 보기</button>
        </div>
      </div>

      <div class="result" id="resultBox" hidden>
        <div class="result-head">
          <span class="result-badge" id="resultBadge">정답</span>
          <span class="result-title" id="resultTitle">1단서 만에 해결</span>
        </div>
        <p class="result-answer">정답 <strong id="resultAnswer"></strong></p>
        <p class="result-explain" id="resultExplain"></p>
        <div class="result-gap">
          <span class="result-gap-tag">다음 목표</span>
          <span id="resultGapText"></span>
        </div>
        <div class="result-acts">
          <button type="button" id="retryBtn">한 판 더</button>
          <button type="button" class="result-next" id="nextBtn">다른 문제</button>
        </div>
        <div class="share">
          <div class="share-preview" id="sharePreview"></div>
          <button class="btn btn-primary" id="copyBtn" type="button">결과 복사</button>
        </div>
        <p class="share-note">결과 문구에는 정답이 들어가지 않습니다. 링크에 이 문제 ID가 들어가, 받은 사람이 같은 문제를 바로 열 수 있습니다.</p>
      </div>
    </section>

      </div>

      <aside class="clue-rail" aria-label="지난 문제 아카이브">
    <section class="panel archive" id="archivePanel">
      <div class="panel-head">
        <div class="panel-title"><span class="bar"></span>지난 문제</div>
        <span class="panel-meta">분야를 골라 다시 풀 수 있습니다</span>
      </div>
      <div class="chips" id="catFilter">__CAT_CHIPS__</div>
      <div class="arc-grid" id="arcGrid">
__ARC_CARDS__
      </div>
      <div class="empty" id="arcEmpty" hidden>이 분야의 문제가 아직 없습니다. 다른 분야를 골라 보세요.</div>
    </section>
      </aside>
    </div>

    <footer class="footer">
      Infosec Archive · 하루 한 판 · 3단서 추리<br>
      정답·단서는 학습과 오락을 위한 것으로, 사실 확인을 거친 소재를 짧게 각색했습니다. 풀이 기록은 이 브라우저(localStorage)에만 저장되며 서버로 전송되지 않습니다.<br>
      __BUILT_AT__ 기준 · 매일 08:00 새 문제
    </footer>
  </main>

  <script>
    // ---- Theme (다른 페이지와 같은 secjobs-theme 동기화) ----
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');

    function setTheme(theme) {
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'block';
        localStorage.setItem('secjobs-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
        if (moonIcon) moonIcon.style.display = 'block';
        if (sunIcon) sunIcon.style.display = 'none';
        localStorage.setItem('secjobs-theme', 'light');
      }
    }

    (function initTheme() {
      let saved = null;
      try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) setTheme('dark');
      else setTheme('light');
    })();

    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    // ---- 데이터 ----
    const DATA = __DATA_JSON__;
    __GUIDE_SCRIPTS__
    const CATS = __CATS_JSON__;
    const STORE_KEY = 'secjobs-clue-v1';
    const TODAY = '__TODAY__';
    const SITE = 'https://bling9513-ship-it.github.io/project-1/clue.html';

    const catLabel = {};
    CATS.forEach(c => { catLabel[c.key] = c.label; });
    const byId = {};
    DATA.forEach(p => { byId[p.id] = p; });

    // ---- 공유 링크 (?id=<문제 ID> · 예전 #<문제 ID> 해시도 받아 준다) ----
    function puzzleUrl(id) {
      return SITE + '?id=' + encodeURIComponent(id);
    }

    function puzzleIdFromUrl() {
      let q = null;
      try { q = new URLSearchParams(location.search).get('id'); } catch (e) { q = null; }
      if (q && byId[q]) return q;
      let h = String(location.hash || '').replace(/^#/, '');
      if (h) {
        try { h = decodeURIComponent(h); } catch (e) {}
        if (byId[h]) return h;
      }
      return null;
    }

    function syncUrl(id) {
      // 지난 문제를 열면 주소창도 그 문제의 공유 링크로 맞춰 둔다(뒤로 가기 기록은 늘리지 않는다).
      try {
        const next = '?id=' + encodeURIComponent(id);
        if (location.search !== next || location.hash) history.replaceState(null, '', next);
      } catch (e) {}
    }

    function escapeHtml(s) {
      return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // ---- 기록 ----
    function emptyRecord() {
      const r = {};
      DATA.forEach(p => { r[p.id] = { solved: false, clues: 1, attempts: 0, gaveUp: false, wrong: [] }; });
      return r;
    }

    function loadRecord() {
      const base = emptyRecord();
      let raw = null;
      try { raw = localStorage.getItem(STORE_KEY); } catch (e) {}
      if (!raw) return base;
      let saved = null;
      try { saved = JSON.parse(raw); } catch (e) { return base; }
      Object.keys(base).forEach(id => {
        const s = saved && saved[id];
        if (!s || typeof s !== 'object') return;
        base[id].solved = !!s.solved;
        base[id].clues = Math.min(3, Math.max(1, Number(s.clues) || 1));
        base[id].attempts = Number(s.attempts) || 0;
        base[id].gaveUp = !!s.gaveUp;
        base[id].wrong = Array.isArray(s.wrong) ? s.wrong.map(Number).filter(n => n >= 0 && n < 4) : [];
      });
      return base;
    }

    let RECORD = loadRecord();

    function saveRecord() {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(RECORD)); } catch (e) {}
    }

    function rec(id) {
      if (!RECORD[id]) RECORD[id] = { solved: false, clues: 1, attempts: 0, gaveUp: false, wrong: [] };
      return RECORD[id];
    }

    // ---- 플레이어 ----
    const pCat = document.getElementById('pCat');
    const pDate = document.getElementById('pDate');
    const pToday = document.getElementById('pToday');
    const pTitle = document.getElementById('pTitle');
    const pPrompt = document.getElementById('pPrompt');
    const pDots = document.getElementById('pDots');
    const clueList = document.getElementById('clueList');
    const nextClueBtn = document.getElementById('nextClue');
    const clueNote = document.getElementById('clueNote');
    const optionsBox = document.getElementById('options');
    const triesText = document.getElementById('triesText');
    const askMsg = document.getElementById('askMsg');
    const giveUpBtn = document.getElementById('giveUp');
    const resultBox = document.getElementById('resultBox');
    const resultBadge = document.getElementById('resultBadge');
    const resultTitle = document.getElementById('resultTitle');
    const resultAnswer = document.getElementById('resultAnswer');
    const resultExplain = document.getElementById('resultExplain');
    const sharePreview = document.getElementById('sharePreview');
    const copyBtn = document.getElementById('copyBtn');
    const clueFlash = document.getElementById('clueFlash');
    const resultGapText = document.getElementById('resultGapText');

    let currentId = null;
    // 단서를 방금 열었을 때 타임라인 점을 튀게 하기 위한 표시
    let popStep = -1;
    // 같은 문제를 연습모드로 다시 풀 때만 쓰는 임시 진행 상황(기록은 건드리지 않는다).
    let practiceRun = null;

    function runOf(p) {
      if (practiceRun && practiceRun.id === p.id) return practiceRun;
      return rec(p.id);
    }

    function isPractice(p) { return !!(practiceRun && practiceRun.id === p.id); }

    function showFlash(kind, tag, text) {
      if (!clueFlash) return;
      clueFlash.hidden = false;
      clueFlash.className = 'clue-flash' + (kind ? ' ' + kind : '');
      clueFlash.innerHTML = '<span class="clue-flash-tag"></span><span class="clue-flash-text"></span>';
      clueFlash.querySelector('.clue-flash-tag').textContent = tag;
      clueFlash.querySelector('.clue-flash-text').textContent = text;
    }

    function hideFlash() {
      if (!clueFlash) return;
      clueFlash.hidden = true;
      clueFlash.className = 'clue-flash';
      clueFlash.textContent = '';
    }

    function fmtDate(d) {
      const parts = String(d || '').split('-');
      if (parts.length !== 3) return d || '';
      return parts[0] + '.' + parts[1] + '.' + parts[2];
    }

    function dotsText(n) {
      let out = '';
      for (let i = 1; i <= 3; i++) out += (i <= n ? '\\u25cf' : '\\u25cb');
      return out;
    }

    function shareText(p, r) {
      const state = r.solved ? (r.clues + '단서 만에 해결') : (r.gaveUp ? '정답 확인' : '풀이 중');
      return '하루 한 판 · 3단서 추리\\n' + fmtDate(p.date) + ' · ' + (catLabel[p.cat] || p.cat)
        + ' · ' + state + ' (' + dotsText(r.clues) + ')\\n' + puzzleUrl(p.id);
    }

    function renderClues(p, r) {
      const lockedText = '다음 단서를 열면 공개됩니다.';
      let html = '';
      for (let i = 0; i < 3; i++) {
        const open = i < r.clues;
        const fresh = i === r.clues - 1 && r.clues > 1;
        html += '<div class="clue ' + (open ? 'open' : 'locked') + (fresh ? ' is-fresh' : '') + '">'
          + '<div class="clue-head">'
          + '<span class="clue-label">단서 ' + (i + 1) + '</span>'
          + '<span class="clue-step">' + (i + 1) + ' / 3</span>'
          + '</div>'
          + '<p class="clue-text">' + escapeHtml(open ? p.clues[i] : lockedText) + '</p>'
          + '</div>';
      }
      clueList.innerHTML = html;
    }

    function renderDots(n, popIndex) {
      const steps = pDots.querySelectorAll('.track-step');
      steps.forEach((step, i) => {
        const on = i < n;
        step.classList.toggle('is-on', on);
        const dot = step.querySelector('.dot');
        if (dot) dot.classList.toggle('on', on);
        step.classList.remove('is-pop');
        if (popIndex === i && on) {
          void step.offsetWidth;
          step.classList.add('is-pop');
        }
      });
      pDots.setAttribute('aria-label', n + '단서 공개');
    }

    function renderOptions(p, r) {
      const finished = r.solved || r.gaveUp;
      let html = '';
      p.choices.forEach((choice, i) => {
        const classes = ['opt'];
        if (finished && i === p.answer) classes.push('is-correct');
        else if (r.wrong.indexOf(i) !== -1) classes.push('is-wrong');
        html += '<button class="' + classes.join(' ') + '" type="button" data-idx="' + i + '"'
          + (finished || r.wrong.indexOf(i) !== -1 ? ' disabled' : '') + '>'
          + '<span class="key">' + 'ABCD'[i] + '</span>'
          + '<span class="body">' + escapeHtml(choice) + '</span>'
          + '</button>';
      });
      optionsBox.innerHTML = html;
      optionsBox.querySelectorAll('.opt').forEach(btn => {
        btn.addEventListener('click', () => pick(Number(btn.dataset.idx)));
      });
    }

    function renderResult(p, r) {
      if (!r.solved && !r.gaveUp) {
        resultBox.hidden = true;
        return;
      }
      resultBox.hidden = false;
      resultBox.classList.toggle('gave-up', !r.solved);
      resultBadge.textContent = r.solved ? (isPractice(p) ? '연습 정답' : '정답') : '정답 확인';
      resultTitle.textContent = r.solved ? (r.clues + '단서 만에 해결 (' + dotsText(r.clues) + ')') : '정답을 확인했습니다';
      if (resultGapText) resultGapText.textContent = gapText(r);
      resultAnswer.textContent = '';
      resultAnswer.textContent = p.choices[p.answer];
      resultExplain.textContent = p.explain;
      sharePreview.textContent = shareText(p, r);
      copyBtn.textContent = '결과 복사';
    }

    function renderPlayer() {
      const p = byId[currentId];
      if (!p) return;
      const r = runOf(p);
      pCat.textContent = catLabel[p.cat] || p.cat;
      pCat.className = 'badge cat-' + p.cat;
      pDate.textContent = fmtDate(p.date);
      pToday.hidden = !(p.date === TODAY);
      pTitle.textContent = p.title;
      pPrompt.textContent = p.prompt;
      renderDots(r.clues, popStep);
      popStep = -1;
      hideFlash();
      renderClues(p, r);
      renderOptions(p, r);
      renderResult(p, r);

      const finished = r.solved || r.gaveUp;
      nextClueBtn.hidden = r.clues >= 3;
      nextClueBtn.disabled = finished;
      nextClueBtn.textContent = r.clues === 1 ? '다음 단서 열기 (2/3)' : '마지막 단서 열기 (3/3)';
      clueNote.hidden = finished;
      giveUpBtn.hidden = finished;
      triesText.textContent = r.attempts ? ('시도 ' + r.attempts + '회') : '정답을 고르면 바로 채점됩니다';
      askMsg.textContent = '';
      askMsg.className = 'ask-msg';
      markCurrentCard();
    }

    function pick(idx) {
      const p = byId[currentId];
      if (!p) return;
      const practice = isPractice(p);
      const r = runOf(p);
      if (!practice && (r.solved || r.gaveUp)) return;
      if (r.wrong.indexOf(idx) !== -1) return;
      r.attempts += 1;
      if (idx === p.answer) {
        r.solved = true;
        if (!practice) saveRecord();
        renderPlayer();
        renderStats();
        renderArchive();
        showFlash('ok', '정답', (practice ? '연습 · ' : '') + r.clues + '단서 만에 해결했습니다.');
        return;
      }
      r.wrong.push(idx);
      if (!practice) saveRecord();
      renderOptions(p, r);
      triesText.textContent = '시도 ' + r.attempts + '회';
      askMsg.textContent = r.clues < 3
        ? '다시 골라 보세요. 다음 단서를 열면 범위가 좁혀집니다.'
        : '아직 정답이 아닙니다. 남은 보기를 다시 살펴보세요.';
      askMsg.className = 'ask-msg no';
      showFlash('no', '오답', r.clues < 3
        ? '다음 단서를 열면 범위가 좁혀집니다. 같은 보기를 다시 고를 수는 없습니다.'
        : '남은 보기에서 다시 골라 보세요.');
    }

    function revealNextClue() {
      const p = byId[currentId];
      if (!p) return;
      const r = runOf(p);
      if (r.solved || r.gaveUp || r.clues >= 3) return;
      r.clues += 1;
      if (!isPractice(p)) saveRecord();
      popStep = r.clues - 1;
      renderPlayer();
      renderStats();
      renderArchive();
    }

    function startPractice() {
      const p = byId[currentId];
      if (!p) return;
      practiceRun = { id: p.id, solved: false, clues: 1, attempts: 0, gaveUp: false, wrong: [] };
      renderPlayer();
      const top = document.getElementById('playPanel').getBoundingClientRect().top + window.scrollY - 70;
      window.scrollTo({ top , behavior: 'smooth' });
      nextClueBtn.focus();
    }

    function openNextPuzzle() {
      if (!DATA.length) return;
      const index = DATA.findIndex(p => p.id === currentId);
      let next = null;
      for (let step = 1; step <= DATA.length; step++) {
        const candidate = DATA[(index + step) % DATA.length];
        if (!rec(candidate.id).solved) { next = candidate; break; }
      }
      if (!next) next = DATA[(index + 1) % DATA.length];
      practiceRun = null;
      loadPuzzle(next.id, true);
    }

    function giveUp() {
      const p = byId[currentId];
      if (!p) return;
      const practice = isPractice(p);
      const r = runOf(p);
      if (r.solved || r.gaveUp) return;
      r.gaveUp = true;
      if (!practice) saveRecord();
      renderPlayer();
      renderStats();
      renderArchive();
    }

    function copyResult() {
      const p = byId[currentId];
      const r = rec(currentId);
      const text = shareText(p, r);
      const done = () => {
        copyBtn.textContent = '복사됨';
        window.setTimeout(() => { copyBtn.textContent = '결과 복사'; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(() => fallbackCopy(text, done));
      } else {
        fallbackCopy(text, done);
      }
    }

    function fallbackCopy(text, done) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', 'readonly');
      ta.style.position = 'fixed';
      ta.style.top = '-1000px';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      if (ok) done();
      else {
        copyBtn.textContent = '복사 실패';
        window.setTimeout(() => { copyBtn.textContent = '결과 복사'; }, 1800);
      }
    }

    nextClueBtn.addEventListener('click', revealNextClue);
    giveUpBtn.addEventListener('click', giveUp);
    copyBtn.addEventListener('click', copyResult);
    const retryResultBtn = document.getElementById('retryBtn');
    if (retryResultBtn) retryResultBtn.addEventListener('click', startPractice);
    const nextResultBtn = document.getElementById('nextBtn');
    if (nextResultBtn) nextResultBtn.addEventListener('click', openNextPuzzle);

    // ---- 지난 문제 ----
    const catFilter = document.getElementById('catFilter');
    const arcGrid = document.getElementById('arcGrid');
    const arcEmpty = document.getElementById('arcEmpty');
    let activeCat = 'all';

    function stateText(r) {
      if (r.solved) return '해결 · ' + r.clues + '단서';
      if (r.gaveUp) return '정답 확인';
      if (r.attempts) return '풀이 중';
      return '아직 안 풀었어요';
    }

    function renderArchive() {
      const cards = arcGrid.querySelectorAll('.arc-card');
      let shown = 0;
      cards.forEach(card => {
        const id = card.dataset.id;
        const r = rec(id);
        const el = card.querySelector('.arc-state');
        if (el) {
          el.textContent = stateText(r);
          el.classList.toggle('done', r.solved);
        }
        const visible = activeCat === 'all' || card.dataset.cat === activeCat;
        card.hidden = !visible;
        if (visible) shown += 1;
      });
      arcEmpty.hidden = shown > 0;
    }

    function markCurrentCard() {
      arcGrid.querySelectorAll('.arc-card').forEach(card => {
        card.classList.toggle('current', card.dataset.id === currentId);
      });
    }

    function loadPuzzle(id, scroll) {
      if (!byId[id]) return;
      currentId = id;
      syncUrl(id);
      renderPlayer();
      if (scroll) {
        const top = document.getElementById('playPanel').getBoundingClientRect().top + window.scrollY - 70;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    }

    arcGrid.querySelectorAll('.arc-card').forEach(card => {
      card.addEventListener('click', () => loadPuzzle(card.dataset.id, true));
    });

    // 주소 끝의 #<문제 ID> 가 바뀌면 그 문제를 연다.
    window.addEventListener('hashchange', function () {
      const id = puzzleIdFromUrl();
      if (id && id !== currentId) loadPuzzle(id, false);
    });

    catFilter.addEventListener('click', ev => {
      const chip = ev.target.closest('.chip');
      if (!chip) return;
      activeCat = chip.dataset.value;
      catFilter.querySelectorAll('.chip').forEach(c => {
        const on = c === chip;
        c.classList.toggle('active', on);
        c.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      renderArchive();
    });

    // ---- 요약·연속 기록 ----
    function dayNumber(d) {
      const parts = String(d || '').split('-');
      if (parts.length !== 3) return NaN;
      return Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])) / 86400000;
    }

    function renderStats() {
      const total = DATA.length;
      const solved = DATA.filter(p => rec(p.id).solved).length;
      document.getElementById('solvedStat').textContent = solved + ' / ' + total;
      document.getElementById('streakNum').textContent = streakDays() + '일';
    }

    function streakDays() {
      const solvedDates = {};
      DATA.forEach(p => { if (rec(p.id).solved) solvedDates[p.date] = true; });
      const todayN = dayNumber(TODAY);
      let start = solvedDates[TODAY] ? todayN : todayN - 1;
      let streak = 0;
      while (solvedDates[dateString(start)]) {
        streak += 1;
        start -= 1;
      }
      return streak;
    }

    function gapText(r) {
      const streak = streakDays();
      const streakText = '연속 ' + streak + '일 도전!';
      if (!r.solved) return streakText + ' · 다음 문제로 연속을 이어 가세요.';
      const clueText = r.clues > 1
        ? '최소 단서 클리어까지 ' + (r.clues - 1) + '단계!'
        : '최소 단서 클리어 달성!';
      return streakText + ' · ' + clueText;
    }

    function dateString(dayN) {
      const d = new Date(dayN * 86400000);
      const y = d.getUTCFullYear();
      const m = String(d.getUTCMonth() + 1).padStart(2, '0');
      const day = String(d.getUTCDate()).padStart(2, '0');
      return y + '-' + m + '-' + day;
    }

    // ---- 시작 ----
    (function start() {
      const todays = DATA.filter(p => p.date === TODAY);
      const fallbackId = todays.length ? todays[0].id : (DATA[0] ? DATA[0].id : null);
      const wanted = puzzleIdFromUrl();
      if (wanted) {
        loadPuzzle(wanted, false);
      } else {
        currentId = fallbackId;
        if (currentId) renderPlayer();
      }
      renderArchive();
      renderStats();
      initClueGuide();
    })();

    // ---- 게임 방법 데모: 단서 열기 → 좁히기 → 정답 (처음 한 번만 움직임) ----
    function initClueGuide() {
      const stage = document.getElementById('clueGuideStage');
      if (!stage) return;
      const cards = stage.querySelectorAll('[data-demo-card]');
      const pick = stage.querySelector('[data-demo-pick]');
      function paint(n) {
        cards.forEach(function (card) {
          const index = Number(card.getAttribute('data-demo-card'));
          card.classList.toggle('is-open', index < n);
        });
        if (pick) pick.hidden = n < 3;
      }
      GameGuide.create({
        key: 'clue_demo_seen_v1',
        steps: document.getElementById('clueGuideSteps'),
        note: document.getElementById('clueGuideNote'),
        replay: document.getElementById('clueGuideReplay'),
        notes: [
          '① 첫 단서를 읽고 가능한 범위를 머리에 둡니다.',
          '② 필요하면 다음 단서를 열어 범위를 좁힙니다.',
          '③ 범위가 좁혀지면 정답을 고릅니다. 열은 단서가 적을수록 좋은 기록입니다.'
        ],
        reset: function () { paint(0); },
        step: paint
      });
    }
  </script>
</body>
</html>
"""


def _render_arc_card(p, idx):
    return (
        '        <button class="arc-card" type="button" data-id="%s" data-cat="%s">\n'
        '          <span class="arc-top"><span class="arc-date">%s</span>'
        '<span class="badge cat-%s">%s</span></span>\n'
        '          <span class="arc-title">%s</span>\n'
        '          <span class="arc-state">아직 안 풀었어요</span>\n'
        '        </button>'
        % (esc(p["id"]), esc(p["category"]), esc(p["puzzle_date"][5:].replace("-", ".")),
           esc(p["category"]), esc(dict((c["key"], c["label"]) for c in CATEGORIES)[p["category"]]),
           esc(p["title"]))
    )


def _cat_chips(questions):
    counts = {}
    for q in questions:
        counts[q["category"]] = counts.get(q["category"], 0) + 1
    parts = ['<button class="chip active" type="button" data-value="all" aria-pressed="true">전체 <em>%d</em></button>'
             % len(questions)]
    for c in CATEGORIES:
        parts.append(
            '<button class="chip" type="button" data-value="%s" aria-pressed="false">%s <em>%d</em></button>'
            % (c["key"], c["label"], counts.get(c["key"], 0))
        )
    return "".join(parts)


def _rotate_choices(q, target):
    """정답 위치를 target 으로 돌면서 보기 내용은 그대로 유지한다(시드 정답이 한쪽에 몰리지 않게)."""
    old = q["answer"]
    if target == old:
        return q
    shift = (target - old) % 4
    out = dict(q)
    out["choices"] = q["choices"][-shift:] + q["choices"][:-shift]
    out["answer"] = target
    return out


def seed_db(verbose=True):
    """초기 시드 14문제를 archive.db(clue_questions)로 이관한다 (id 보존, 재실행 안전)."""
    from db_manager import seed_clue_questions, count_clue_questions
    before = count_clue_questions()
    questions = [_rotate_choices(q, i % 4) for i, q in enumerate(SEEDS)]
    inserted = seed_clue_questions(questions)
    after = count_clue_questions()
    if verbose:
        print("-> clue_questions 이관: %d개 추가 (전체 %d개)" % (inserted, after))
    return before, inserted, after


def load_questions(verbose=True):
    """DB의 clue_questions를 읽는다. 테이블이 비었으면 시드를 이관하고, DB 장애 시 내장 문제로 대체한다."""
    try:
        from db_manager import get_clue_questions, count_clue_questions
        if count_clue_questions() == 0:
            seed_db(verbose=verbose)
        qs = get_clue_questions()
        if qs:
            return qs
    except Exception as e:  # DB 손상·권한 문제 시에도 페이지는 떠야 한다
        if verbose:
            print("  [경고] DB에서 3단서 추리 문제를 읽지 못해 내장 문제로 빌드합니다: %s: %s"
                  % (type(e).__name__, e))
    fallback = []
    for i, q in enumerate(SEEDS):
        item = _rotate_choices(q, i % 4)
        item["is_daily"] = 0
        item["sort_order"] = i
        fallback.append(item)
    return fallback


GUIDE_STAGE = (
    '<div class="clue-demo">'
    '<span class="clue-demo-card" data-demo-card="0"><b>단서 1</b><i>사건</i></span>'
    '<span class="clue-demo-card" data-demo-card="1"><b>단서 2</b><i>정황</i></span>'
    '<span class="clue-demo-card" data-demo-card="2"><b>단서 3</b><i>결정</i></span>'
    '<span class="clue-demo-pick" data-demo-pick hidden>정답</span>'
    '</div>'
)

GUIDE_HTML = game_guide.guide_html(
    'clueGuide', GUIDE_STAGE,
    ['① 단서 열기', '② 좁히기', '③ 정답'],
    '단서를 하나씩 열면 위 타임라인이 채워지고, 범위가 좁혀집니다.',
)


def build():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    built_at = now.strftime("%Y-%m-%d %H:%M KST")
    today_str = now.strftime("%Y-%m-%d")

    questions = load_questions()

    payload = []
    for q in questions:
        payload.append({
            "id": q["id"],
            "date": q["puzzle_date"],
            "cat": q["category"],
            "title": q["title"],
            "prompt": q["prompt"],
            "clues": [c for c in q["clues"][:3]],
            "choices": q["choices"],
            "answer": q["answer"],
            "explain": q["explanation"],
        })

    data_json = safe_json_for_script(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    cats_json = safe_json_for_script(json.dumps(CATEGORIES, ensure_ascii=False, separators=(",", ":")))

    arc_cards = "\n".join(_render_arc_card(q, i) for i, q in enumerate(questions))
    todays = [q for q in questions if q["puzzle_date"] == today_str]
    today_cat = (dict((c["key"], c["label"]) for c in CATEGORIES).get(todays[0]["category"], "—")
                 if todays else "—")

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__GUIDE__", GUIDE_HTML)
    html = html.replace("__GUIDE_SCRIPTS__", game_guide.GUIDE_JS)
    html = html.replace("__CAT_CHIPS__", _cat_chips(questions))
    html = html.replace("__ARC_CARDS__", arc_cards)
    html = html.replace("__DATA_JSON__", data_json.replace("</", "<\\/"))
    html = html.replace("__CATS_JSON__", cats_json.replace("</", "<\\/"))
    html = html.replace("__TOTAL__", str(len(questions)))
    html = html.replace("__TODAY_CAT__", esc(today_cat))
    html = html.replace("__TODAY__", today_str)
    html = html.replace("__BUILT_AT__", esc(built_at))

    with open(CLUE_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(ui_shell.apply(html, 'clue')))

    daily_count = len([q for q in questions if q.get("is_daily")])
    print("-> 'clue.html' 생성 완료 (문제 %d개 · 시드 %d개 · 데일리 %d개 · 오늘 %s)"
          % (len(questions), len(questions) - daily_count, daily_count,
             (todays[0]["title"] if todays else "없음")))
    return len(questions)


if __name__ == "__main__":
    import sys
    if "--migrate" in sys.argv:
        seed_db()
    if "--migrate-only" not in sys.argv:
        build()

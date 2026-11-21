# -*- coding: utf-8 -*-
"""
퇴근 전 60초 관제실 (ops.html) 빌더.

- 하루 한 판, KST 날짜 시드로 정해지는 서비스 경보 6건(인프라 3 · 보안 3)이 교대조에 들어온다.
- 대응 인력 2명(인프라·자동화 / 보안·분석)에게 경보를 탭으로 배치한다.
  전문 담당이 맡으면 처리 시간 40% 단축 · 점수 15% 보너스.
- 실전 60초: 도착하는 경보를 실시간으로 배치하고, 60초가 끝나면 미처리·다운타임이 결과에 남는다.
- 연습(타이머 없음): 6건을 모두 배치한 뒤 시뮬레이션해 최적 배치와 비교한다(턴/스텝 단위 실험).
- 기록은 localStorage(ops_room_stats_v1)에만 남는다. 서버로 보내는 값은 없다.
- 경보 풀 24건(인프라 12 · 보안 12)과 14일치 일일 세트는 ops_data.json 으로 생성한다.
"""
import json
import os
import random
from datetime import datetime, timedelta, timezone
from html import escape as esc

from html_guard import harden_html, safe_json_for_script
import game_guide
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPS_HTML = os.path.join(BASE_DIR, "ops.html")
DATA_PATH = os.path.join(BASE_DIR, "ops_data.json")
KST = timezone(timedelta(hours=9))
DAILY_DAYS = 14
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

RESPONDERS = [
    {"id": "infra", "name": "인프라·자동화", "short": "인프라", "spec": "infra", "desc": "서버·배포·수집"},
    {"id": "sec", "name": "보안·분석", "short": "보안", "spec": "sec", "desc": "탐지·계정·악성코드"},
]

# id, 제목, 서비스, 전문(spec), 영향도(sev 1~3), 기본 처리 시간(초)
POOL = [
    {"id": "inf-01", "title": "결제 API 5xx 급증", "service": "결제 게이트웨이", "spec": "infra", "sev": 3, "base": 9},
    {"id": "inf-02", "title": "수집 배치 잡 지연", "service": "데이터 파이프라인", "spec": "infra", "sev": 2, "base": 8},
    {"id": "inf-03", "title": "로그 파이프라인 적체", "service": "로그 수집기", "spec": "infra", "sev": 2, "base": 7},
    {"id": "inf-04", "title": "CDN 캐시 미스 폭증", "service": "정적 자원 CDN", "spec": "infra", "sev": 1, "base": 6},
    {"id": "inf-05", "title": "DB 커넥션 풀 고갈", "service": "주문 DB", "spec": "infra", "sev": 3, "base": 11},
    {"id": "inf-06", "title": "TLS 인증서 만료 임박", "service": "API 게이트웨이", "spec": "infra", "sev": 2, "base": 5},
    {"id": "inf-07", "title": "CI 러너 디스크 92%", "service": "빌드 러너", "spec": "infra", "sev": 1, "base": 7},
    {"id": "inf-08", "title": "오토스케일링 미동작", "service": "웹 프런트", "spec": "infra", "sev": 3, "base": 10},
    {"id": "inf-09", "title": "알림 큐 적체", "service": "메시지 큐", "spec": "infra", "sev": 2, "base": 8},
    {"id": "inf-10", "title": "이미지 워커 중단", "service": "미디어 워커", "spec": "infra", "sev": 1, "base": 6},
    {"id": "inf-11", "title": "사내 DNS 응답 지연", "service": "DNS 서버", "spec": "infra", "sev": 2, "base": 6},
    {"id": "inf-12", "title": "야간 백업 누락", "service": "백업 서버", "spec": "infra", "sev": 1, "base": 5},
    {"id": "sec-01", "title": "WAF 차단 급증(SQLi)", "service": "웹 방화벽", "spec": "sec", "sev": 3, "base": 8},
    {"id": "sec-02", "title": "비정상 로그인 성공", "service": "계정 인증", "spec": "sec", "sev": 3, "base": 10},
    {"id": "sec-03", "title": "악성 파일 업로드 의심", "service": "파일 저장소", "spec": "sec", "sev": 3, "base": 9},
    {"id": "sec-04", "title": "취약점 스캐너 대량 요청", "service": "외부 노출 API", "spec": "sec", "sev": 2, "base": 7},
    {"id": "sec-05", "title": "권한 상승 시도 탐지", "service": "관리자 콘솔", "spec": "sec", "sev": 3, "base": 11},
    {"id": "sec-06", "title": "피싱 메일 대량 유입", "service": "메일 게이트웨이", "spec": "sec", "sev": 2, "base": 8},
    {"id": "sec-07", "title": "EDR 격리 요청 미처리", "service": "단말 관제", "spec": "sec", "sev": 2, "base": 7},
    {"id": "sec-08", "title": "비인가 크롤링 증가", "service": "공개 API", "spec": "sec", "sev": 1, "base": 6},
    {"id": "sec-09", "title": "시크릿 키 노출 의심", "service": "소스 저장소", "spec": "sec", "sev": 3, "base": 9},
    {"id": "sec-10", "title": "IDS 이상 트래픽", "service": "네트워크 센서", "spec": "sec", "sev": 2, "base": 8},
    {"id": "sec-11", "title": "계정 잠금 폭주", "service": "인증 서비스", "spec": "sec", "sev": 1, "base": 5},
    {"id": "sec-12", "title": "감사 로그 누락", "service": "감사 로그", "spec": "sec", "sev": 1, "base": 6},
]

SPEC_KEYS = ("infra", "sec")

GUIDE_STAGE = (
    '<div class="ops-demo">'
    '<div class="ops-demo-board">'
    '<span class="ops-demo-alert" data-demo-alert="0"><i></i>결제 API 5xx</span>'
    '<div class="ops-demo-people">'
    '<span class="ops-demo-person" data-demo-person="infra"><b>인프라</b>'
    '<em class="ops-demo-rec" data-demo-rec hidden>추천</em>'
    '<span class="ops-demo-check" data-demo-check hidden>'
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.3 4.3L19 7.2"></path></svg>'
    '</span></span>'
    '<span class="ops-demo-person" data-demo-person="sec"><b>보안</b></span>'
    '</div>'
    '</div>'
    '<div class="ops-demo-foot">'
    '<span class="ops-demo-count" data-demo-count="0">남은 경보 6건</span>'
    '<span class="ops-demo-done" data-demo-done hidden>처리 완료 · +345점</span>'
    '</div>'
    '</div>'
)

GUIDE_HTML = game_guide.guide_html(
    'opsGuide', GUIDE_STAGE,
    ['① 경보 탭', '② 추천 담당', '③ 처리 완료'],
    '경보 카드를 누르면 전문 담당 카드가 파란색으로 켜집니다. 그 담당에게 배정하면 처리 시간이 40% 줄어듭니다.',
)


def _validate_pool():
    ids = set()
    counts = {"infra": 0, "sec": 0}
    for item in POOL:
        missing = [k for k in ("id", "title", "service", "spec", "sev", "base") if k not in item]
        if missing:
            raise SystemExit("[중단] 경보 %s: 필수 필드 누락 %s" % (item.get("id"), missing))
        if item["id"] in ids:
            raise SystemExit("[중단] 경보 ID 중복: %s" % item["id"])
        ids.add(item["id"])
        if item["spec"] not in SPEC_KEYS:
            raise SystemExit("[중단] 경보 %s: 전문 분야 오류 %s" % (item["id"], item["spec"]))
        counts[item["spec"]] += 1
        if not (1 <= int(item["sev"]) <= 3):
            raise SystemExit("[중단] 경보 %s: 영향도 범위 오류" % item["id"])
        if not (3 <= int(item["base"]) <= 14):
            raise SystemExit("[중단] 경보 %s: 처리 시간 범위 오류" % item["id"])
        if not str(item["title"]).strip() or not str(item["service"]).strip():
            raise SystemExit("[중단] 경보 %s: 제목·서비스가 비었습니다" % item["id"])
    for key in SPEC_KEYS:
        if counts[key] < 12:
            raise SystemExit("[중단] %s 경보가 12건 미만입니다: %d" % (key, counts[key]))
    return counts


def daily_ids(day_key):
    """KST 날짜 → 경보 6건(인프라 3 · 보안 3). 같은 날짜는 언제나 같은 세트."""
    rng = random.Random(int(day_key.replace("-", "")))
    picked = []
    for spec in SPEC_KEYS:
        bucket = [item["id"] for item in POOL if item["spec"] == spec]
        picked.extend(rng.sample(bucket, 3))
    rng.shuffle(picked)
    return picked


def build_data(now):
    _validate_pool()
    days = {}
    seen = set()
    for offset in range(DAILY_DAYS):
        key = (now.date() + timedelta(days=offset)).isoformat()
        ids = daily_ids(key)
        signature = tuple(sorted(ids))
        if signature in seen:
            raise SystemExit("[중단] %s: 14일 안에 같은 경보 세트가 반복됩니다" % key)
        seen.add(signature)
        days[key] = ids
    data = {
        "version": 1,
        "built_date": now.date().isoformat(),
        "built_at": now.strftime("%Y-%m-%d %H:%M KST"),
        "responders": RESPONDERS,
        "alerts": POOL,
        "days": days,
        "settings": {"live_seconds": 60, "arrivals": [0, 0, 0, 2, 4, 6], "penalty_per_second": 8,
                     "match_speed": 0.6, "match_bonus": 1.15},
    }
    for key, ids in days.items():
        if len(ids) != 6 or len(set(ids)) != 6:
            raise SystemExit("[중단] %s: 경보 6건 구성 실패" % key)
        specs = [next(a["spec"] for a in POOL if a["id"] == i) for i in ids]
        if specs.count("infra") != 3 or specs.count("sec") != 3:
            raise SystemExit("[중단] %s: 인프라/보안 3:3 구성 실패" % key)
    return data


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
      --warn-bg: #fffbeb; --warn-text: #b45309; --warn-border: #fde68a;

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
      --no-bg: rgba(239, 68, 68, 0.12);   --no-text: #fca5a5;  --no-border: rgba(239, 68, 68, 0.32);
      --warn-bg: rgba(245, 158, 11, 0.14); --warn-text: #fcd34d; --warn-border: rgba(245, 158, 11, 0.32);

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

    .navbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
    }
    .nav-container { max-width: 1360px; margin: 0 auto; padding: 0 20px; height: 60px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .nav-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
    .brand-logo-img { width: 28px; height: 28px; border-radius: 7px; object-fit: cover; display: block; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15); flex-shrink: 0; }
    .brand-name { font-size: 17px; font-weight: 700; letter-spacing: -0.03em; white-space: nowrap; }
    .update-meta { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); white-space: nowrap; }
    .live-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; display: inline-block; flex-shrink: 0; }
    .icon-btn { width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; cursor: pointer; text-decoration: none; }
    .icon-btn:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .nav-actions { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

    .ops-wrap { max-width: 1180px; margin: 0 auto; padding: 22px 20px 72px; }

    .ops-hero { margin-bottom: 14px; }
    .ops-pill {
      display: inline-block;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent-primary);
      background: var(--accent-subtle);
      border: 1px solid var(--border-default);
      border-radius: 6px;
      padding: 3px 8px;
      margin-bottom: 9px;
    }
    .ops-hero h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.035em; }
    .ops-hero p { margin-top: 5px; font-size: 13px; color: var(--text-secondary); max-width: 640px; }

    .ops-shell { display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 16px; align-items: start; }
    .ops-rail { display: flex; flex-direction: column; gap: 12px; position: sticky; top: 76px; }

    .ops-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: 16px;
      padding: 13px 14px;
      box-shadow: var(--card-shadow);
    }
    .ops-card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 9px; }
    .ops-card-head h2 { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; }
    .ops-card-head span { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; white-space: nowrap; }

    .ops-seg { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 11px; }
    .ops-seg-btn {
      border: 0; background: transparent; border-radius: 8px; padding: 8px 4px;
      font-family: inherit; font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary); cursor: pointer;
      transition: background-color 160ms ease, color 160ms ease;
    }
    .ops-seg-btn.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.1); }
    .ops-seg-btn:active { transform: scale(0.98); }

    .ops-clock { margin-top: 11px; }
    .ops-clock-top { display: flex; align-items: baseline; gap: 5px; }
    .ops-clock-label { font-size: 11.5px; font-weight: 600; color: var(--text-muted); }
    .ops-clock-value { margin-left: auto; font-size: 25px; font-weight: 700; letter-spacing: -0.045em; font-variant-numeric: tabular-nums; }
    .ops-clock-unit { font-size: 11.5px; color: var(--text-muted); }
    .ops-bar { height: 6px; border-radius: 999px; background: var(--bg-muted); overflow: hidden; margin: 7px 0 6px; }
    .ops-bar span { display: block; height: 100%; width: 100%; background: var(--accent-primary); border-radius: 999px; transition: width 120ms linear; }
    .ops-bar.is-low span { background: #dc2626; }

    .ops-scoreline { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; font-size: 11px; color: var(--text-muted); }
    .ops-scoreline > span { white-space: nowrap; }
    .ops-scoreline strong { color: var(--text-primary); font-size: 12.5px; font-variant-numeric: tabular-nums; }
    .ops-status { margin-top: 4px; min-height: 16px; font-size: 11px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    .ops-primary {
      width: 100%; margin-top: 10px; padding: 11px 12px; border: 0; border-radius: 11px;
      background: var(--accent-primary); color: #ffffff;
      font-family: inherit; font-size: 13.5px; font-weight: 700; letter-spacing: -0.02em;
      cursor: pointer; transition: background-color 160ms ease, transform 160ms ease;
    }
    .ops-primary:hover { background: var(--accent-hover); }
    .ops-primary:active { transform: scale(0.99); }
    .ops-primary:disabled { background: var(--bg-muted); color: var(--text-muted); cursor: default; transform: none; }
    .ops-ghost {
      width: 100%; margin-top: 7px; padding: 9px 12px; border-radius: 10px;
      border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer;
    }
    .ops-ghost:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .ops-person {
      display: grid; grid-template-columns: 34px minmax(0, 1fr); gap: 10px; align-items: center;
      width: 100%; padding: 9px 10px; border: 1px solid var(--border-default); border-radius: 12px;
      background: var(--bg-page); font-family: inherit; text-align: left; cursor: pointer;
      transition: border-color 160ms ease, background-color 160ms ease;
    }
    .ops-person + .ops-person { margin-top: 7px; }
    .ops-person:hover { border-color: var(--border-strong); }
    .ops-person.is-active { border-color: var(--accent-primary); background: var(--accent-subtle); }
    .ops-person-avatar { width: 34px; height: 34px; border-radius: 10px; background: var(--bg-subtle); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .ops-person.is-active .ops-person-avatar { background: var(--bg-surface); color: var(--accent-primary); }
    .ops-person-body { min-width: 0; }
    .ops-person-top { display: flex; align-items: baseline; gap: 6px; justify-content: space-between; }
    .ops-person-name { font-size: 12.5px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ops-person-count { font-size: 10.5px; color: var(--text-muted); white-space: nowrap; }
    .ops-person-state { display: block; font-size: 11px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ops-person-bar { height: 3px; border-radius: 999px; background: var(--bg-muted); overflow: hidden; margin-top: 5px; }
    .ops-person-bar span { display: block; height: 100%; width: 0; background: var(--accent-primary); border-radius: 999px; transition: width 120ms linear; }
    .ops-hint { margin-top: 9px; font-size: 10.5px; line-height: 1.45; color: var(--text-muted); }

    .ops-record-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
    .ops-record-grid dt { font-size: 10.5px; color: var(--text-muted); white-space: nowrap; }
    .ops-record-grid dd { font-size: 14.5px; font-weight: 700; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .ops-history { list-style: none; display: flex; flex-direction: column; gap: 5px; margin-top: 9px; }
    .ops-history li { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 11px; color: var(--text-secondary); }
    .ops-history li span:last-child { font-variant-numeric: tabular-nums; font-weight: 600; }
    .ops-history li.is-empty { color: var(--text-muted); }

    .ops-main { min-width: 0; }
    .ops-main-head { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; margin-bottom: 9px; }
    .ops-main-goal {
      display: none; align-items: center; gap: 5px; margin: 0 0 8px;
      font-size: 10.5px; font-weight: 600; line-height: 1.4; color: var(--text-primary);
    }
    @media (min-width: 768px) {
      .ops-guide { margin-bottom: 12px; }
    }
    .ops-main-goal .tag {
      flex: 0 0 auto; font-size: 8.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border: 1px solid var(--border-default); border-radius: 4px; padding: 0 4px;
    }
    .ops-main-title { font-size: 14px; font-weight: 700; letter-spacing: -0.02em; }
    .ops-main-sub { font-size: 11.5px; color: var(--text-muted); text-align: right; }

    .ops-board { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }

    .ops-alert {
      display: flex; flex-direction: column; gap: 5px; min-height: 118px;
      padding: 11px 12px; border: 1px solid var(--border-default); border-radius: 14px;
      background: var(--bg-surface); box-shadow: var(--card-shadow);
      font-family: inherit; text-align: left; cursor: pointer; position: relative; overflow: hidden;
      transition: border-color 160ms ease, background-color 160ms ease, transform 160ms ease;
    }
    .ops-alert:hover { border-color: var(--border-strong); }
    .ops-alert:active { transform: scale(0.995); }
    .ops-alert[data-state="waiting"] { border-style: dashed; background: var(--bg-page); color: var(--text-muted); cursor: default; }
    .ops-alert[data-state="queued"] { border-color: var(--border-strong); }
    .ops-alert[data-state="working"] { border-color: var(--accent-primary); }
    .ops-alert[data-state="done"] { border-color: var(--ok-border); background: var(--ok-bg); }
    .ops-alert[data-state="missed"] { border-color: var(--no-border); background: var(--no-bg); }

    .oa-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
    .oa-sev { font-size: 10px; font-weight: 700; letter-spacing: 0.01em; padding: 2px 6px; border-radius: 6px; background: var(--bg-subtle); color: var(--text-secondary); }
    .oa-sev.sev-3 { background: var(--no-bg); color: var(--no-text); }
    .oa-sev.sev-2 { background: var(--warn-bg); color: var(--warn-text); }
    .oa-spec { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
    .oa-title { font-size: 13px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.35; color: var(--text-primary); }
    .ops-alert[data-state="waiting"] .oa-title { color: var(--text-secondary); }
    .oa-service { font-size: 11px; color: var(--text-muted); }
    .oa-foot { display: flex; align-items: baseline; justify-content: space-between; gap: 6px; margin-top: auto; padding-top: 4px; font-size: 10.5px; color: var(--text-secondary); }
    .oa-state { font-weight: 600; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .oa-meta { color: var(--text-muted); white-space: nowrap; }
    .oa-progress { height: 3px; border-radius: 999px; background: var(--bg-muted); overflow: hidden; }
    .oa-progress span { display: block; height: 100%; width: 0; background: var(--accent-primary); border-radius: 999px; }
    .ops-alert[data-state="working"] .oa-progress span { transition: width 120ms linear; }
    .ops-alert[data-state="done"] .oa-progress span { width: 100%; background: var(--ok-text); }
    .ops-alert[data-state="missed"] .oa-progress span { width: 100%; background: var(--no-text); opacity: 0.5; }

    .ops-result {
      margin-top: 14px; padding: 16px;
      border: 1px solid var(--border-default); border-radius: 16px;
      background: var(--bg-surface); box-shadow: var(--card-shadow);
    }
    .ops-result-badge { display: inline-block; font-size: 10.5px; font-weight: 700; padding: 3px 8px; border-radius: 6px; background: var(--accent-subtle); color: var(--accent-primary); }
    .ops-result-badge.is-missed { background: var(--no-bg); color: var(--no-text); }
    .ops-result-title { margin-top: 8px; font-size: 15px; font-weight: 700; letter-spacing: -0.03em; }
    .ops-result-score { display: flex; align-items: baseline; gap: 6px; margin-top: 2px; }
    .ops-result-score strong { font-size: 32px; font-weight: 700; letter-spacing: -0.05em; font-variant-numeric: tabular-nums; }
    .ops-result-score .unit { font-size: 13px; color: var(--text-muted); }
    .ops-result-best { margin-left: auto; font-size: 11.5px; color: var(--text-muted); }
    .ops-result-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-subtle); }
    .ops-result-grid dt { font-size: 10.5px; color: var(--text-muted); }
    .ops-result-grid dd { font-size: 14px; font-weight: 700; font-variant-numeric: tabular-nums; }
    .ops-result-hint { margin-top: 12px; padding: 10px 12px; border-radius: 10px; background: var(--bg-subtle); font-size: 12px; line-height: 1.55; color: var(--text-secondary); }
    .ops-result-actions { display: flex; gap: 8px; margin-top: 12px; }
    .ops-result-actions .ops-primary, .ops-result-actions .ops-ghost { margin-top: 0; flex: 1 1 0; }

    .ops-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); }

    @media (max-width: 1100px) {
      .ops-shell { grid-template-columns: 280px minmax(0, 1fr); }
    }

    @media (max-width: 900px) {
      .ops-hero h1 { font-size: 20px; }
      .ops-hero p { font-size: 12.5px; }
    }

    @media (max-width: 767px) {
      .ops-shell { grid-template-columns: 1fr; gap: 10px; }
      .ops-rail { display: contents; }
      .ops-main { display: contents; }
      .ops-guide { display: block; order: 0; margin-bottom: 0; }
      .ops-rail > .ops-card:nth-of-type(1) { order: 1; }
      .ops-rail > .ops-card:nth-of-type(2) { order: 2; }
      .ops-main-head { order: 3; }
      .ops-board { order: 4; }
      .ops-result { order: 5; }
      .ops-foot { order: 6; }
      .ops-rail > .ops-card:nth-of-type(3) { order: 7; }
      .ops-guide .gg-card { margin-bottom: 0; }
      .ops-card { padding: 11px 12px; }
      .ops-card-head { margin-bottom: 7px; }
      .ops-clock { margin-top: 8px; }
      .ops-bar { margin: 6px 0 5px; }
      .ops-primary { margin-top: 8px; }
      #rosterList { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; }
      .ops-person + .ops-person { margin-top: 0; }
      .ops-person { grid-template-columns: 28px minmax(0, 1fr); gap: 8px; padding: 8px 9px; }
      .ops-person-avatar { width: 28px; height: 28px; border-radius: 9px; }
      .ops-person-avatar svg { width: 16px; height: 16px; }
      .ops-person-name { font-size: 12px; }
      .ops-person-count { display: none; }
      .ops-person-state { font-size: 10.5px; }
      .ops-hint { margin-top: 7px; font-size: 10px; }
      .ops-board { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 620px) {
      .ops-wrap { padding: 12px 14px 76px; }
      .ops-hero { margin-bottom: 8px; }
      .ops-hero .ops-pill { display: none; }
      .ops-hero h1 { font-size: 19px; }
      .ops-hero p { display: none; }
      .ops-hint { display: none; }
      .ops-main-sub { display: none; }
      .ops-main-head { justify-content: flex-start; gap: 8px; margin-bottom: 5px; }
      .ops-main-goal { display: flex; margin-bottom: 6px; }
      .ops-alert { min-height: 108px; }
      .ops-result-score strong { font-size: 28px; }
      .ops-clock-value { font-size: 22px; }
    }

    @media (max-width: 420px) {
      .ops-board { grid-template-columns: 1fr; }
      .ops-person { grid-template-columns: 24px minmax(0, 1fr); gap: 7px; padding: 7px 8px; }
      .ops-person-avatar { width: 24px; height: 24px; }
      .ops-person-name { font-size: 11.5px; }
      .ops-main-count { font-size: 10.5px; }
    }

    @media (max-width: 767px) {
      .ops-demo-board { gap: 6px; }
      .ops-demo-alert { font-size: 9px; padding: 4px 6px; }
      .ops-demo-person { font-size: 9px; padding: 4px 6px; }
    }

    @media (max-width: 380px) {
      .ops-wrap { padding: 14px 11px 76px; }
      .ops-card { padding: 12px; border-radius: 14px; }
      .oa-title { font-size: 12.5px; }
    }

    /* ----- 게임 방법 데모 (경보 탭 → 추천 담당 → 처리 완료) ----- */
    .ops-guide { max-width: 560px; }
    .ops-demo { display: flex; flex-direction: column; gap: 6px; max-width: 520px; }
    .ops-guide .gg-steps { justify-content: flex-start; }
    .ops-demo-board { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .ops-demo-alert {
      display: inline-flex; align-items: center; gap: 5px; min-width: 0;
      padding: 5px 7px; border: 1px solid var(--border-default); border-radius: 8px;
      background: var(--bg-surface); font-size: 9.5px; font-weight: 700; color: var(--text-secondary);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      transition: border-color 160ms ease, background-color 160ms ease, color 160ms ease;
    }
    .ops-demo-alert i { width: 6px; height: 6px; border-radius: 50%; background: var(--no-text); flex: 0 0 auto; }
    .ops-demo-alert.is-tap { border-color: var(--accent-primary); color: var(--accent-primary); background: var(--accent-subtle); }
    .ops-demo-alert.is-done { border-color: var(--ok-border); color: var(--ok-text); background: var(--ok-bg); }
    .ops-demo-alert.is-done i { background: var(--ok-text); }
    .ops-demo-people { display: inline-flex; align-items: center; gap: 5px; }
    .ops-demo-person {
      position: relative; display: inline-flex; align-items: center; gap: 4px;
      padding: 5px 7px; border: 1px solid var(--border-default); border-radius: 8px;
      background: var(--bg-surface); font-size: 9.5px; font-weight: 700; color: var(--text-secondary);
      white-space: nowrap;
      transition: border-color 160ms ease, background-color 160ms ease, color 160ms ease, box-shadow 160ms ease;
    }
    .ops-demo-person b { font-weight: 700; }
    .ops-demo-rec {
      font-style: normal; font-size: 7.5px; font-weight: 700; color: #ffffff;
      background: var(--accent-primary); border-radius: 4px; padding: 1px 3px;
    }
    .ops-demo-person.is-rec { border-color: var(--accent-primary); background: var(--accent-subtle); color: var(--accent-primary); box-shadow: 0 0 0 2px var(--accent-subtle); }
    .ops-demo-check {
      position: absolute; right: -5px; top: -5px; width: 12px; height: 12px; border-radius: 50%;
      background: var(--ok-text); display: flex; align-items: center; justify-content: center;
    }
    .ops-demo-check svg { width: 8px; height: 8px; stroke: #ffffff; stroke-width: 3.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }
    .ops-demo-foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .ops-demo-count { font-size: 9px; font-weight: 600; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .ops-demo-done { font-size: 9px; font-weight: 700; color: var(--ok-text); font-variant-numeric: tabular-nums; }

    /* ----- 보드 즉시 피드백: 추천 담당 · 추천 경보 · 남은 경보 카운터 ----- */
    .ops-person { position: relative; }
    .ops-person-badge {
      display: none; font-size: 8px; font-weight: 700; color: #ffffff;
      background: var(--accent-primary); border-radius: 4px; padding: 1px 4px; margin-left: 4px;
      vertical-align: 1px;
    }
    .ops-person.is-rec { border-color: var(--accent-primary); background: var(--accent-subtle); box-shadow: 0 0 0 2px var(--accent-subtle); }
    .ops-person.is-rec .ops-person-badge { display: inline-block; }
    .ops-person.is-rec .ops-person-avatar { background: var(--bg-surface); color: var(--accent-primary); }
    .ops-alert .oa-badge {
      display: none; position: absolute; right: 9px; top: 9px;
      font-size: 8px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border: 1px solid var(--accent-primary); border-radius: 4px; padding: 0 4px;
    }
    .ops-alert.is-suggested { border-color: var(--accent-primary); border-style: dashed; }
    .ops-alert.is-suggested .oa-badge { display: inline-block; }
    .ops-alert.is-pop { animation: opsCardPop 320ms ease-out; }
    .ops-person.is-done-pop .ops-person-count { animation: opsCountPop 320ms ease-out; }
    .ops-main-count {
      font-size: 11px; font-weight: 600; color: var(--text-secondary);
      font-variant-numeric: tabular-nums; white-space: nowrap;
    }
    .ops-main-count.is-pop { animation: opsCountPop 320ms ease-out; }
    @keyframes opsCardPop {
      0% { transform: scale(1); }
      45% { transform: scale(0.965); }
      100% { transform: scale(1); }
    }
    @keyframes opsCountPop {
      0% { transform: scale(1); }
      40% { transform: scale(1.18); color: var(--accent-primary); }
      100% { transform: scale(1); }
    }

    /* ----- 결과: 목표 격차 + 원탭 재도전 최우선 ----- */
    .ops-result-gap {
      display: flex; align-items: flex-start; gap: 6px; margin-top: 9px;
      font-size: 12.5px; font-weight: 700; line-height: 1.5; color: var(--text-primary);
    }
    .ops-result-gap .tag {
      flex: 0 0 auto; margin-top: 1px; font-size: 8.5px; font-weight: 700;
      color: var(--accent-primary); background: var(--accent-subtle);
      border: 1px solid var(--border-default); border-radius: 4px; padding: 1px 4px;
    }
    .ops-result-actions.is-first { margin-top: 10px; }

    @media (prefers-reduced-motion: reduce) {
      .ops-seg-btn, .ops-person, .ops-alert { transition: none !important; }
      .ops-bar span, .oa-progress span, .ops-person-bar span { transition: none !important; }
      .ops-alert.is-pop, .ops-person.is-done-pop .ops-person-count, .ops-main-count.is-pop { animation: none !important; }
      .ops-demo-alert, .ops-demo-person { transition: none !important; }
    }
"""

CSS = CSS + game_guide.GUIDE_CSS

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 퇴근 전 60초 관제실</title>
  <meta name="description" content="서비스 경보 6건을 인프라·자동화 담당과 보안·분석 담당에게 배치해 다운타임과 미처리 경보를 줄이는 60초 관제 게임. 매일 KST 날짜 시드로 같은 경보가 나오고, 타이머 없는 연습 모드에서 최적 배치를 실험할 수 있습니다.">
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
          <span>매일 KST 00:00 새 경보</span>
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

  <main class="ops-wrap">
    <div class="ops-hero">
      <span class="ops-pill">일일 챌린지</span>
      <h1>퇴근 전 60초 관제실</h1>
      <p>경보 6건이 들어옵니다. 인프라·자동화 담당과 보안·분석 담당에게 배치해 다운타임과 미처리 경보를 줄이세요. 전문 담당이 맡으면 처리 시간이 40% 줄고 점수가 15% 오릅니다.</p>
    </div>

    <div class="ops-shell">
      <aside class="ops-rail" aria-label="관제 설정">
        <section class="ops-card">
          <div class="ops-card-head">
            <h2>모드</h2>
            <span id="modeNote">실전</span>
          </div>
          <div class="ops-seg" role="group" aria-label="게임 모드">
            <button type="button" class="ops-seg-btn is-active" id="modeLive" data-mode="live" aria-pressed="true">실전 60초</button>
            <button type="button" class="ops-seg-btn" id="modePractice" data-mode="practice" aria-pressed="false">연습</button>
          </div>
          <div class="ops-clock">
            <div class="ops-clock-top">
              <span class="ops-clock-label" id="clockLabel">남은 시간</span>
              <strong class="ops-clock-value" id="clockValue">60.0</strong>
              <span class="ops-clock-unit" id="clockUnit">초</span>
            </div>
            <div class="ops-bar" id="clockBar"><span id="clockFill"></span></div>
            <div class="ops-scoreline">
              <span>점수 <strong id="liveScore">0</strong></span>
              <span>다운타임 <strong id="liveDowntime">0</strong>초</span>
            </div>
            <p class="ops-status" id="opsStatus" role="status" aria-live="polite">교대 시작을 누르면 경보가 들어옵니다</p>
          </div>
          <button type="button" class="ops-primary" id="startBtn">교대 시작</button>
          <button type="button" class="ops-ghost" id="resetPlanBtn" hidden>배치 비우기</button>
        </section>

        <section class="ops-card">
          <div class="ops-card-head">
            <h2>대응 인력</h2>
            <span>2명</span>
          </div>          <div id="rosterList"></div>
          <p class="ops-hint">담당을 고른 뒤 경보 카드를 누르면 배치됩니다. 이미 배치한 경보를 다시 누르면 대기열 맨 뒤로 갑니다.</p>
        </section>

        <section class="ops-card">
          <div class="ops-card-head">
            <h2>기록</h2>
            <span id="recordDate">—</span>
          </div>
          <dl class="ops-record-grid">
            <div><dt>오늘 최고</dt><dd id="recBest">—</dd></div>
            <div><dt>연속 플레이</dt><dd id="recStreak">0일</dd></div>
            <div><dt>최근 점수</dt><dd id="recLast">—</dd></div>
          </dl>
          <ul class="ops-history" id="recHistory"></ul>
        </section>
      </aside>

      <section class="ops-main" aria-label="경보 보드">
        <div class="ops-guide">__GUIDE__</div>
        <div class="ops-main-head">
          <h2 class="ops-main-title" id="boardDate">오늘의 경보 6건</h2>
          <span class="ops-main-count" id="boardCount" aria-live="polite">남은 6건</span>
          <span class="ops-main-sub" id="boardSub">두 담당에게 나눠 배치하세요</span>
        </div>
        <p class="ops-main-goal"><span class="tag">목표</span>60초 안에 경보 6건을 전문 담당에게 배정해 다운타임 0초</p>
        <div class="ops-board" id="alertBoard" aria-label="경보 목록"></div>

        <section class="ops-result" id="resultBox" aria-labelledby="resultTitle" hidden>
          <span class="ops-result-badge" id="resultBadge">교대 종료</span>
          <h2 class="ops-result-title" id="resultTitle">60초 관제 결과</h2>
          <p class="ops-result-gap" id="resultGap"><span class="tag">다음 목표</span><span id="resultGapText">—</span></p>
          <div class="ops-result-actions is-first">
            <button type="button" class="ops-primary" id="retryBtn">바로 재도전</button>
            <button type="button" class="ops-ghost" id="switchPracticeBtn">연습 모드</button>
          </div>
          <div class="ops-result-score">
            <strong id="resultScore">0</strong><span class="unit">점</span>
            <span class="ops-result-best" id="resultBest"></span>
          </div>
          <dl class="ops-result-grid">
            <div><dt>처리 완료</dt><dd id="resultCompleted">0 / 6</dd></div>
            <div><dt>미처리</dt><dd id="resultMissed">0건</dd></div>
            <div><dt>다운타임</dt><dd id="resultDowntime">0초</dd></div>
          </dl>
          <p class="ops-result-hint" id="resultHint"></p>
        </section>

        <p class="ops-foot">배치·점수 기록은 이 브라우저(localStorage)에만 저장됩니다. 서버로 보내지 않습니다.</p>
      </section>
    </div>
  </main>

  <script type="application/json" id="opsData">__DATA_JSON__</script>

  <script>
__GUIDE_SCRIPTS__
  </script>

  <script>
  (function () {
    'use strict';

    /* ---------------------------------------------------------------- 데이터 */
    var dataEl = document.getElementById('opsData');
    var DATA = {};
    try { DATA = JSON.parse(dataEl.textContent || '{}'); } catch (e) { DATA = {}; }
    var POOL = Array.isArray(DATA.alerts) ? DATA.alerts : [];
    var DAILY = (DATA.days && typeof DATA.days === 'object') ? DATA.days : {};
    var byId = {};
    POOL.forEach(function (item) { byId[item.id] = item; });

    var RESPONDERS = (Array.isArray(DATA.responders) && DATA.responders.length === 2) ? DATA.responders : [
      { id: 'infra', name: '인프라·자동화', short: '인프라', spec: 'infra', desc: '서버·배포·수집' },
      { id: 'sec', name: '보안·분석', short: '보안', spec: 'sec', desc: '탐지·계정·악성코드' }
    ];
    var SPEC_LABEL = { infra: '인프라', sec: '보안' };
    var SEV_LABEL = { 3: '심각', 2: '주의', 1: '보통' };
    var SETTINGS = (DATA.settings && typeof DATA.settings === 'object') ? DATA.settings : {};
    var ARRIVALS = (Array.isArray(SETTINGS.arrivals) && SETTINGS.arrivals.length === 6) ? SETTINGS.arrivals : [0, 0, 0, 2, 4, 6];
    var LIVE_SECONDS = Number(SETTINGS.live_seconds) || 60;
    var TICK = 0.2;
    var PENALTY = Number(SETTINGS.penalty_per_second) || 5;
    var STORE_KEY = 'ops_room_stats_v1';
    var WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];

    /* ---------------------------------------------------------------- DOM */
    var el = {};
    ['modeLive', 'modePractice', 'modeNote', 'clockLabel', 'clockValue', 'clockUnit', 'clockBar', 'clockFill',
     'liveScore', 'liveDowntime', 'opsStatus', 'startBtn', 'resetPlanBtn', 'rosterList', 'alertBoard',
     'resultBox', 'resultBadge', 'resultTitle', 'resultScore', 'resultBest', 'resultCompleted', 'resultMissed',
     'resultDowntime', 'resultHint', 'retryBtn', 'switchPracticeBtn', 'recBest', 'recStreak', 'recLast',
     'recHistory', 'recordDate', 'boardDate', 'boardSub', 'boardCount', 'resultGap', 'resultGapText',
     'themeToggle', 'moonIcon', 'sunIcon'
    ].forEach(function (id) { el[id] = document.getElementById(id); });

    var rosterEls = {};
    var cardEls = {};

    /* ---------------------------------------------------------------- 상태 */
    var state = {
      mode: 'live',
      phase: 'idle',          // idle | running | ended
      ticks: 0,
      lastT: 0,
      startedAt: 0,
      alerts: [],
      queues: { infra: [], sec: [] },
      active: 'infra',
      points: 0,
      downtime: 0,
      timer: null,
      result: null,
      best: null,
      recommend: null,
      store: null
    };

    /* ---------------------------------------------------------------- 유틸 */
    function pad2(n) { return (n < 10 ? '0' : '') + n; }

    function kstKey(offsetDays) {
      var t = new Date(Date.now() + 9 * 3600 * 1000 + (offsetDays || 0) * 86400000);
      return t.getUTCFullYear() + '-' + pad2(t.getUTCMonth() + 1) + '-' + pad2(t.getUTCDate());
    }

    function todayKey() { return kstKey(0); }

    function dayLabel(key) {
      var parts = key.split('-').map(Number);
      var d = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
      return key + ' (' + WEEKDAYS[d.getUTCDay()] + ')';
    }

    function round1(v) { return Math.round(v * 10) / 10; }

    function esc(value) {
      return String(value).replace(/[&<>"']/g, function (ch) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
      });
    }

    function basePoints(sev) { return sev >= 3 ? 300 : (sev === 2 ? 200 : 120); }

    function pointsFor(alert, rid) {
      var p = basePoints(alert.sev);
      return alert.spec === rid ? Math.round(p * 1.15) : p;
    }

    function durFor(alert, rid) {
      return round1(alert.spec === rid ? alert.base * 0.6 : alert.base);
    }

    function specLabel(spec) { return SPEC_LABEL[spec] || spec; }

    function findAlert(id) {
      for (var i = 0; i < state.alerts.length; i += 1) {
        if (state.alerts[i].id === id) return state.alerts[i];
      }
      return null;
    }

    /* 경과 시간은 0.2초 콜백 횟수가 아니라 시작 시각(Date.now) 기준으로 계산한다.
       탭이 백그라운드에서 스로틀된 뒤 돌아와도 남은 시간이 실제와 어긋나지 않는다. */
    function currentTime() {
      if (state.phase === 'ended') return LIVE_SECONDS;
      if (state.phase !== 'running' || !state.startedAt) return 0;
      return Math.min(LIVE_SECONDS, Math.max(0, (Date.now() - state.startedAt) / 1000));
    }

    /* 마지막으로 처리한 시점(lastT)에서 목표 시점까지 0.2초 간격 모델을 시간순으로 따라가며
       경보 도착 → 처리 완료 → 60초 종료를 빠짐없이 일괄 반영한다. */
    function advanceTo(target) {
      var goal = Math.min(LIVE_SECONDS, Math.max(0, target));
      var guard = 0;
      while (state.lastT + 1e-9 < goal && guard < 600) {
        guard += 1;
        var next = Math.min(goal, round1(state.lastT + TICK));
        state.lastT = next;
        state.ticks = Math.round(next / TICK);
        state.alerts.forEach(function (a) {
          if (a.state === 'waiting' && next + 1e-9 >= a.arrival) a.state = 'ready';
        });
        RESPONDERS.forEach(function (r) { pump(r.id, next); });
        if (next >= LIVE_SECONDS - 1e-9) { endLive(); return; }
      }
      if (goal >= LIVE_SECONDS - 1e-9) return;
      render();
    }

    /* 탭 재개(visibilitychange·focus)나 다음 틱에서 밀린 시간을 한 번에 따라잡는다. */
    function syncClock() {
      if (state.mode !== 'live' || state.phase !== 'running') return;
      advanceTo(currentTime());
    }

    function setStatus(text) { el.opsStatus.textContent = text; }

    /* 카드·카운터가 살아 움직이게: 클래스를 붙였다 잠시 뒤 뺀다. */
    function pulse(node, cls) {
      if (!node) return;
      node.classList.remove(cls);
      void node.offsetWidth;
      node.classList.add(cls);
      window.setTimeout(function () { node.classList.remove(cls); }, 380);
    }

    function flashRecommend(rid) {
      state.recommend = rid;
      renderRoster();
      window.setTimeout(function () {
        if (state.recommend === rid) { state.recommend = null; renderRoster(); }
      }, 1500);
    }

    function assignedCount() { return state.queues.infra.length + state.queues.sec.length; }

    /* ---------------------------------------------------------------- 일일 세트 */
    function dailyIds(key) {
      var list = DAILY[key];
      if (Array.isArray(list) && list.length === 6) return list.slice();
      return fallbackIds(key);
    }

    // 빌드된 14일 범위를 벗어난 날짜: 날짜 문자열 해시로 같은 규칙(인프라 3 + 보안 3)의 세트를 만든다.
    function fallbackIds(key) {
      var seed = 2166136261 >>> 0;
      for (var i = 0; i < key.length; i += 1) {
        seed ^= key.charCodeAt(i);
        seed = Math.imul(seed, 16777619) >>> 0;
      }
      function rnd() {
        seed = (seed + 0x6D2B79F5) >>> 0;
        var t = seed;
        t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
        t = (t ^ (t + Math.imul(t ^ (t >>> 7), t | 61))) >>> 0;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      }
      function shuffle(list) {
        var copy = list.slice();
        for (var j = copy.length - 1; j > 0; j -= 1) {
          var k = Math.floor(rnd() * (j + 1));
          var tmp = copy[j]; copy[j] = copy[k]; copy[k] = tmp;
        }
        return copy;
      }
      var infra = shuffle(POOL.filter(function (a) { return a.spec === 'infra'; }).map(function (a) { return a.id; })).slice(0, 3);
      var sec = shuffle(POOL.filter(function (a) { return a.spec === 'sec'; }).map(function (a) { return a.id; })).slice(0, 3);
      return shuffle(infra.concat(sec));
    }

    /* ---------------------------------------------------------------- 저장소 */
    function emptyStore() {
      return { version: 1, days: {}, streak: { count: 0, lastDate: '' }, history: [] };
    }

    function loadStore() {
      var store = emptyStore();
      try {
        var raw = localStorage.getItem(STORE_KEY);
        if (!raw) return store;
        var parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== 'object') return store;
        if (parsed.days && typeof parsed.days === 'object') {
          Object.keys(parsed.days).forEach(function (key) {
            if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(key)) return;
            var day = parsed.days[key];
            if (!day || typeof day !== 'object') return;
            store.days[key] = {
              best: Number(day.best) || 0,
              bestMode: day.bestMode === 'practice' ? 'practice' : 'live',
              plays: Number(day.plays) || 0,
              last: Number(day.last) || 0,
              lastCleared: Number(day.lastCleared) || 0,
              lastDowntime: Number(day.lastDowntime) || 0
            };
          });
        }
        if (parsed.streak && typeof parsed.streak === 'object') {
          store.streak = {
            count: Math.max(0, Math.min(3650, Number(parsed.streak.count) || 0)),
            lastDate: /^\\d{4}-\\d{2}-\\d{2}$/.test(String(parsed.streak.lastDate || '')) ? parsed.streak.lastDate : ''
          };
        }
        if (Array.isArray(parsed.history)) {
          store.history = parsed.history.slice(0, 8).filter(function (item) {
            return item && typeof item === 'object' && /^\\d{4}-\\d{2}-\\d{2}$/.test(String(item.date || ''));
          }).map(function (item) {
            return {
              date: item.date,
              mode: item.mode === 'practice' ? 'practice' : 'live',
              score: Number(item.score) || 0,
              cleared: Number(item.cleared) || 0,
              downtime: Number(item.downtime) || 0
            };
          });
        }
      } catch (e) {
        return emptyStore();
      }
      return store;
    }

    function saveRun(result) {
      var store = loadStore();
      var key = todayKey();
      var day = store.days[key] || { best: 0, bestMode: 'live', plays: 0, last: 0, lastCleared: 0, lastDowntime: 0 };
      day.plays += 1;
      if (result.score > day.best) {
        day.best = result.score;
        day.bestMode = result.mode;
      }
      day.last = result.score;
      day.lastCleared = result.completed;
      day.lastDowntime = result.downtime;
      store.days[key] = day;

      var keys = Object.keys(store.days).sort();
      while (keys.length > 30) { delete store.days[keys.shift()]; }

      if (store.streak.lastDate !== key) {
        store.streak.count = (store.streak.lastDate === kstKey(-1)) ? store.streak.count + 1 : 1;
        store.streak.lastDate = key;
      }

      store.history = [{
        date: key,
        mode: result.mode,
        score: result.score,
        cleared: result.completed,
        downtime: result.downtime
      }].concat(store.history).slice(0, 8);

      try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); } catch (e) {}
      state.store = store;
    }

    /* ---------------------------------------------------------------- 시뮬레이션 */
    function arrivalMap() {
      var map = {};
      state.alerts.forEach(function (a) { map[a.id] = a.arrival; });
      return map;
    }

    function simulate(plan, arrivals) {
      var total = 0;
      var downtime = 0;
      var timeline = [];
      ['infra', 'sec'].forEach(function (rid) {
        var cursor = 0;
        (plan[rid] || []).forEach(function (id) {
          var data = byId[id];
          if (!data) return;
          var arrival = arrivals[id] || 0;
          var start = Math.max(cursor, arrival);
          var dur = durFor(data, rid);
          var done = round1(start + dur);
          cursor = done;
          timeline.push({ id: id, owner: rid, start: start, done: done });
          total += pointsFor(data, rid);
          downtime += Math.max(0, done - arrival);
        });
      });
      downtime = round1(downtime);
      return {
        points: total,
        downtime: downtime,
        score: Math.max(0, Math.round(total - PENALTY * downtime)),
        completed: timeline.length,
        timeline: timeline
      };
    }

    function computeBest(arrivals) {
      var ids = state.alerts.map(function (a) { return a.id; });
      var used = {};
      var seq = [];
      var best = null;

      function evaluate(order) {
        for (var k = 0; k <= order.length; k += 1) {
          var plan = { infra: order.slice(0, k), sec: order.slice(k) };
          var sim = simulate(plan, arrivals);
          if (!best || sim.score > best.score) {
            best = { score: sim.score, plan: plan, downtime: sim.downtime };
          }
        }
      }

      function walk() {
        if (seq.length === ids.length) { evaluate(seq); return; }
        for (var i = 0; i < ids.length; i += 1) {
          if (used[ids[i]]) continue;
          used[ids[i]] = true;
          seq.push(ids[i]);
          walk();
          seq.pop();
          used[ids[i]] = false;
        }
      }

      walk();
      return best;
    }

    /* ---------------------------------------------------------------- 보드 구성 */
    function buildRoster() {
      el.rosterList.innerHTML = '';
      RESPONDERS.forEach(function (r) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'ops-person';
        btn.id = 'person-' + r.id;
        btn.dataset.responder = r.id;
        btn.setAttribute('aria-pressed', 'false');
        btn.innerHTML =
          '<span class="ops-person-avatar">' + responderIcon(r.id) + '</span>' +
          '<span class="ops-person-body">' +
            '<span class="ops-person-top"><span class="ops-person-name">' + esc(r.name) +
            '<span class="ops-person-badge">추천</span></span>' +
            '<span class="ops-person-count">배치 0건</span></span>' +
            '<span class="ops-person-state">대기 중</span>' +
            '<span class="ops-person-bar"><span></span></span>' +
          '</span>';
        btn.addEventListener('click', function () { selectResponder(r.id); });
        el.rosterList.appendChild(btn);
        rosterEls[r.id] = btn;
      });
    }

    function responderIcon(id) {
      if (id === 'sec') {
        return '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v5.5c0 4.2-2.9 7.9-7 9.5-4.1-1.6-7-5.3-7-9.5V6z"></path>' +
          '<path d="M9.2 12.2l2 2 3.6-3.9"></path></svg>';
      }
      return '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="6" rx="1.8"></rect>' +
        '<rect x="3" y="14" width="18" height="6" rx="1.8"></rect><path d="M7 7h.01M7 17h.01"></path></svg>';
    }

    function buildBoard() {
      el.alertBoard.innerHTML = '';
      cardEls = {};
      state.alerts.forEach(function (a) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'ops-alert';
        btn.dataset.id = a.id;
        btn.dataset.spec = a.data.spec;
        btn.dataset.sev = String(a.data.sev);
        btn.dataset.state = a.state;
        btn.innerHTML =
          '<span class="oa-badge" aria-hidden="true">추천</span>' +
          '<span class="oa-top"><span class="oa-sev sev-' + a.data.sev + '">' + SEV_LABEL[a.data.sev] + '</span>' +
          '<span class="oa-spec">' + specLabel(a.data.spec) + ' 전문</span></span>' +
          '<strong class="oa-title">' + esc(a.data.title) + '</strong>' +
          '<span class="oa-service">' + esc(a.data.service) + '</span>' +
          '<span class="oa-foot"><span class="oa-state">도착 대기</span>' +
          '<span class="oa-meta">기본 ' + a.data.base + '초</span></span>' +
          '<span class="oa-progress"><span></span></span>';
        btn.addEventListener('click', function () { assign(a.id, state.active); });
        el.alertBoard.appendChild(btn);
        cardEls[a.id] = btn;
      });
    }

    /* ---------------------------------------------------------------- 초기화 */
    function resetBoard() {
      stopTimer();
      var ids = dailyIds(todayKey());
      state.ticks = 0;
      state.lastT = 0;
      state.startedAt = 0;
      state.points = 0;
      state.downtime = 0;
      state.result = null;
      state.phase = 'idle';
      state.queues = { infra: [], sec: [] };
      state.alerts = ids.map(function (id, index) {
        var data = byId[id];
        if (!data) return null;
        return {
          id: id,
          data: data,
          arrival: ARRIVALS[index] || 0,
          owner: null,
          start: null,
          done: null,
          dur: 0,
          state: state.mode === 'live' ? 'waiting' : 'ready'
        };
      }).filter(Boolean);
      state.best = computeBest(arrivalMap());
      el.resultBox.hidden = true;
      buildBoard();
      render();
      el.boardDate.textContent = '오늘의 경보';
      el.boardSub.textContent = dayLabel(todayKey()) + ' · 같은 판으로 다시 도전';
    }

    function selectResponder(rid) {
      state.active = rid;
      renderRoster();
      setStatus(SPEC_LABEL[rid] + ' 담당 선택 · 경보 카드를 누르세요');
    }

    /* ---------------------------------------------------------------- 배치 */
    function assign(id, rid) {
      var a = findAlert(id);
      if (!a) return;
      if (state.phase === 'ended') { setStatus('다시 도전을 눌러 새 판을 시작하세요.'); return; }
      if (state.mode === 'live' && state.phase !== 'running') { setStatus('교대 시작을 누른 뒤 배치할 수 있습니다.'); return; }
      if (a.state === 'waiting') { setStatus('아직 도착하지 않은 경보입니다.'); return; }
      if (a.state === 'done' || a.state === 'missed') return;

      if (a.state === 'working') { setStatus('처리 중인 경보는 옮길 수 없습니다.'); return; }

      if (a.owner === rid && a.state === 'queued') {
        var queue = state.queues[rid];
        var idx = queue.indexOf(id);
        if (idx >= 0 && idx < queue.length - 1) {
          queue.splice(idx, 1);
          queue.push(id);
          setStatus('대기열 맨 뒤로 옮겼습니다.');
        } else {
          setStatus('이미 ' + SPEC_LABEL[rid] + ' 대기열에 있습니다.');
        }
        render();
        return;
      }

      if (a.owner) {
        var old = state.queues[a.owner];
        var at = old.indexOf(id);
        if (at >= 0) old.splice(at, 1);
      }

      a.owner = rid;
      a.state = 'queued';
      state.queues[rid].push(id);
      setStatus(SPEC_LABEL[rid] + ' 담당에 배치' + (a.data.spec === rid ? ' · 전문 매칭' : ' · 비전문'));
      if (a.data.spec === rid) flashRecommend(rid);
      pulse(cardEls[id], 'is-pop');
      if (state.mode === 'live') pump(rid, currentTime());
      render();
    }

    /* ---------------------------------------------------------------- 실전 진행 */
    function startTimer() {
      stopTimer();
      state.timer = window.setInterval(tick, TICK * 1000);
    }

    function stopTimer() {
      if (state.timer) {
        window.clearInterval(state.timer);
        state.timer = null;
      }
    }

    function startLive() {
      state.phase = 'running';
      state.ticks = 0;
      state.lastT = 0;
      state.startedAt = Date.now();
      state.points = 0;
      state.downtime = 0;
      state.alerts.forEach(function (a) {
        a.state = a.arrival <= 0 ? 'ready' : 'waiting';
      });
      setStatus('경보가 도착하는 즉시 담당에게 배치하세요.');
      startTimer();
      render();
    }

    function tick() {
      advanceTo(currentTime());
    }

    function workingAlert(rid) {
      for (var i = 0; i < state.alerts.length; i += 1) {
        var a = state.alerts[i];
        if (a.owner === rid && a.state === 'working') return a;
      }
      return null;
    }

    function pump(rid, t) {
      if (t >= LIVE_SECONDS) return;
      var guard = 0;
      while (guard < 12) {
        guard += 1;
        var cur = workingAlert(rid);
        if (cur) {
          var finish = round1(cur.start + cur.dur);
          if (t + 1e-9 >= finish) {
            completeAlert(cur, finish);
            continue;
          }
          return;
        }
        var nextId = null;
        for (var i = 0; i < state.queues[rid].length; i += 1) {
          var candidate = findAlert(state.queues[rid][i]);
          if (candidate && candidate.state === 'queued' && candidate.arrival <= t + 1e-9) { nextId = candidate; break; }
        }
        if (!nextId) return;
        nextId.state = 'working';
        nextId.start = Math.max(t, nextId.arrival);
        nextId.dur = durFor(nextId.data, rid);
      }
    }

    function completeAlert(a, doneAt) {
      a.state = 'done';
      a.done = doneAt;
      state.points += pointsFor(a.data, a.owner);
      state.downtime += Math.max(0, round1(doneAt - a.arrival));
      var queue = state.queues[a.owner];
      var idx = queue.indexOf(a.id);
      if (idx >= 0) queue.splice(idx, 1);
    }

    function endLive() {
      stopTimer();
      var t = Math.min(currentTime(), LIVE_SECONDS);
      state.ticks = Math.round(t / TICK);
      state.phase = 'ended';
      var completed = 0;
      var missed = 0;
      state.alerts.forEach(function (a) {
        if (a.state === 'done') { completed += 1; return; }
        a.state = 'missed';
        missed += 1;
        if (a.arrival <= t) state.downtime += Math.max(0, round1(t - a.arrival));
      });
      finish({
        mode: 'live',
        score: Math.max(0, Math.round(state.points - PENALTY * state.downtime)),
        completed: completed,
        missed: missed,
        downtime: round1(state.downtime)
      });
    }

    function runPractice() {
      if (assignedCount() !== state.alerts.length) return;
      var sim = simulate(state.queues, arrivalMap());
      sim.timeline.forEach(function (item) {
        var a = findAlert(item.id);
        if (!a) return;
        a.state = 'done';
        a.start = item.start;
        a.done = item.done;
        a.owner = item.owner;
      });
      state.points = sim.points;
      state.downtime = sim.downtime;
      finish({
        mode: 'practice',
        score: sim.score,
        completed: sim.completed,
        missed: 0,
        downtime: sim.downtime
      });
    }

    /* ---------------------------------------------------------------- 결과 */
    /* 한 가지 목표 격차: 다음 등급(B→A→S)까지 남은 점수, 또는 남은 경보 건수. */
    function gapFor(result) {
      var best = state.best && state.best.score ? state.best.score : 0;
      if (!best) return '오늘의 최적 배치를 계산하지 못했습니다. 한 판 더 진행해 보세요.';
      var targets = [{ name: 'B', min: 0.6 }, { name: 'A', min: 0.8 }, { name: 'S', min: 0.95 }];
      var next = null;
      targets.forEach(function (target) {
        if (next) return;
        if (result.score < target.min * best) {
          next = { name: target.name, need: Math.max(1, Math.ceil(target.min * best - result.score)) };
        }
      });
      if (result.mode === 'live' && result.missed > 0) {
        return '남은 경보 ' + result.missed + '건만 더 처리하면 ' +
          (next ? next.name + '등급까지 ' + next.need + '점!' : '오늘 최적에 더 가까워집니다!');
      }
      if (next) return '다음 등급 ' + next.name + '까지 ' + next.need + '점!';
      return '오늘 최적 배치(S등급)를 달성했습니다!';
    }

    function hintFor(result) {
      var best = state.best || { score: result.score };
      var gap = Math.max(0, best.score - result.score);
      if (gap <= 0) {
        return '오늘의 최적 배치와 같습니다. 이론상 최고점(' + best.score + '점)입니다.';
      }
      var mismatched = state.alerts.filter(function (a) {
        return a.owner && a.data.spec !== a.owner;
      }).sort(function (x, y) { return y.data.sev - x.data.sev; });

      if (mismatched.length) {
        var wrong = mismatched[0];
        return '최적 ' + best.score + '점 · 이번 ' + result.score + '점. "' + wrong.data.title + '"은(는) ' +
          specLabel(wrong.data.spec) + ' 전문 경보입니다. ' + specLabel(wrong.data.spec) + ' 담당에게 넘기면 최대 ' +
          best.score + '점까지 오릅니다.';
      }
      if (result.mode === 'live' && result.missed > 0) {
        return '최적 ' + best.score + '점 · 이번 ' + result.score + '점. 미처리 ' + result.missed +
          '건이 남았습니다. 도착 즉시 전문 담당에게 배치하면 점수가 오릅니다.';
      }
      var slow = null;
      RESPONDERS.forEach(function (r) {
        if (slow) return;
        var queue = state.queues[r.id];
        for (var i = 0; i < queue.length && !slow; i += 1) {
          var a = findAlert(queue[i]);
          if (!a) continue;
          for (var j = i + 1; j < queue.length; j += 1) {
            var b = findAlert(queue[j]);
            if (!b) continue;
            if (durFor(b.data, r.id) < durFor(a.data, r.id)) { slow = { alert: a, quick: b }; break; }
          }
        }
      });
      if (slow) {
        return '최적 ' + best.score + '점 · 이번 ' + result.score + '점. "' + slow.alert.data.title + '"(' +
          durFor(slow.alert.data, slow.alert.owner) + '초)보다 짧게 끝나는 "' + slow.quick.data.title +
          '"을(를) 앞 순서로 두면 최대 ' + best.score + '점까지 오릅니다.';
      }
      var waited = null;
      state.alerts.forEach(function (a) {
        if (!a.done || a.start === null) return;
        if (a.start - a.arrival < 0.5) return;
        if (!waited || (a.start - a.arrival) > (waited.start - waited.arrival)) waited = a;
      });
      if (waited) {
        return '최적 ' + best.score + '점 · 이번 ' + result.score + '점. "' + waited.data.title +
          '"을(를) 도착 즉시 맡겼다면 ' + round1(waited.start - waited.arrival) + '초만큼 다운타임이 줄었습니다.';
      }
      return '최적 ' + best.score + '점 · 이번 ' + result.score + '점. 배치 순서를 조금만 바꾸면 최대 ' +
        best.score + '점까지 오릅니다.';
    }

    function finish(result) {
      stopTimer();
      state.phase = 'ended';
      state.result = result;
      saveRun(result);
      render();
      var isLive = result.mode === 'live';
      el.resultBadge.textContent = isLive ? (result.missed ? '교대 종료' : '전 경보 처리') : '배치 완료';
      el.resultBadge.classList.toggle('is-missed', isLive && result.missed > 0);
      el.resultTitle.textContent = isLive ? '60초 관제 결과' : '연습 배치 결과';
      el.resultScore.textContent = String(result.score);
      var day = state.store && state.store.days[todayKey()];
      el.resultBest.textContent = day ? '오늘 최고 ' + day.best + '점' : '';
      el.resultCompleted.textContent = result.completed + ' / ' + state.alerts.length;
      el.resultMissed.textContent = result.missed + '건';
      el.resultDowntime.textContent = result.downtime + '초';
      el.resultHint.textContent = hintFor(result);
      el.resultGapText.textContent = gapFor(result);
      el.resultBox.hidden = false;
      el.resultBox.scrollIntoView({ block: 'nearest' });
    }

    /* ---------------------------------------------------------------- 렌더 */
    function render() {
      renderMode();
      renderClock();
      renderRoster();
      renderBoard();
      renderRecord();
    }

    function renderMode() {
      var isLive = state.mode === 'live';
      el.modeLive.classList.toggle('is-active', isLive);
      el.modePractice.classList.toggle('is-active', !isLive);
      el.modeLive.setAttribute('aria-pressed', isLive ? 'true' : 'false');
      el.modePractice.setAttribute('aria-pressed', isLive ? 'false' : 'true');
      el.modeNote.textContent = isLive ? '실전' : '스텝 배치';
    }

    function renderClock() {
      var isLive = state.mode === 'live';
      var t = currentTime();
      if (isLive) {
        el.clockLabel.textContent = state.phase === 'ended' ? '종료' : (state.phase === 'running' ? '남은 시간' : '준비');
        el.clockUnit.textContent = '초';
        el.clockValue.textContent = Math.max(0, LIVE_SECONDS - t).toFixed(1);
        var remainRatio = Math.max(0, 1 - t / LIVE_SECONDS);
        el.clockFill.style.width = (remainRatio * 100) + '%';
        el.clockBar.classList.toggle('is-low', remainRatio <= 0.25);
        el.liveScore.textContent = String(Math.max(0, Math.round(state.points - PENALTY * state.downtime)));
        el.liveDowntime.textContent = String(round1(state.downtime));
      } else {
        var placed = assignedCount();
        el.clockLabel.textContent = '배치';
        el.clockUnit.textContent = '건';
        el.clockValue.textContent = placed + ' / ' + state.alerts.length;
        el.clockFill.style.width = (state.alerts.length ? (placed / state.alerts.length) * 100 : 0) + '%';
        el.clockBar.classList.remove('is-low');
        el.liveScore.textContent = String(Math.max(0, Math.round(state.points - PENALTY * state.downtime)));
        el.liveDowntime.textContent = String(round1(state.downtime));
      }

      var label;
      var disabled = false;
      if (state.phase === 'ended') {
        label = '다시 도전';
      } else if (isLive) {
        label = state.phase === 'running' ? '교대 종료' : '교대 시작';
      } else {
        var ready = assignedCount() === state.alerts.length;
        label = ready ? '배치 실행' : '경보 ' + assignedCount() + '/' + state.alerts.length + ' 배치';
        disabled = !ready;
      }
      el.startBtn.textContent = label;
      el.startBtn.disabled = disabled;
      el.resetPlanBtn.hidden = !(state.phase !== 'ended' && assignedCount() > 0);
    }

    function renderRoster() {
      var t = currentTime();
      RESPONDERS.forEach(function (r) {
        var card = rosterEls[r.id];
        if (!card) return;
        var working = workingAlert(r.id);
        var queued = state.queues[r.id].length;
        card.classList.toggle('is-active', state.active === r.id);
        card.classList.toggle('is-busy', !!working);
        card.classList.toggle('is-rec', state.recommend === r.id);
        card.setAttribute('aria-pressed', state.active === r.id ? 'true' : 'false');
        card.querySelector('.ops-person-count').textContent = '배치 ' + queued + '건';
        var stateText;
        if (working) {
          stateText = '처리 중 · ' + working.data.title;
        } else if (state.phase === 'ended') {
          stateText = '교대 종료';
        } else if (state.mode === 'live' && state.phase === 'idle') {
          stateText = '대기 · 교대 시작 전';
        } else {
          stateText = queued ? '대기 ' + queued + '건' : '대기 중';
        }
        card.querySelector('.ops-person-state').textContent = stateText;
        var fill = card.querySelector('.ops-person-bar span');
        if (working) {
          var pct = ((t - working.start) / working.dur) * 100;
          fill.style.width = Math.max(0, Math.min(100, pct)) + '%';
        } else {
          fill.style.width = '0%';
        }
      });
    }

    function renderBoard() {
      var t = currentTime();
      var isLive = state.mode === 'live';
      var remaining = 0;
      state.alerts.forEach(function (a) {
        if (a.state !== 'done' && a.state !== 'missed') remaining += 1;
        var card = cardEls[a.id];
        if (!card) return;
        card.dataset.state = a.state;
        card.classList.toggle('is-suggested',
          a.state === 'ready' && a.data.spec === state.active && state.phase !== 'ended');
        var stateText = '';
        var meta = '기본 ' + a.data.base + '초';
        var pct = 0;
        if (a.state === 'waiting') {
          stateText = isLive ? '도착까지 ' + Math.max(0, Math.ceil(a.arrival - t)) + '초' : '대기';
        } else if (a.state === 'ready') {
          stateText = '미배치 · 탭해서 배치';
        } else if (a.state === 'queued') {
          var pos = state.queues[a.owner] ? state.queues[a.owner].indexOf(a.id) + 1 : 0;
          stateText = specLabel(a.owner) + ' 대기 ' + Math.max(1, pos) + '번째';
          meta = '예상 ' + durFor(a.data, a.owner) + '초';
        } else if (a.state === 'working') {
          var left = Math.max(0, round1(a.start + a.dur - t));
          stateText = specLabel(a.owner) + ' 처리 중 · ' + left.toFixed(1) + '초';
          meta = a.data.spec === a.owner ? '전문 매칭' : '비전문';
          pct = Math.max(0, Math.min(100, ((t - a.start) / a.dur) * 100));
        } else if (a.state === 'done') {
          stateText = '복구 완료 · ' + round1(a.done - a.arrival) + '초';
          meta = a.data.spec === a.owner ? '전문 매칭' : '비전문';
          pct = 100;
        } else if (a.state === 'missed') {
          stateText = '미처리';
          meta = '교대 종료';
          pct = 100;
        }
        card.querySelector('.oa-state').textContent = stateText;
        card.querySelector('.oa-meta').textContent = meta;
        card.querySelector('.oa-progress span').style.width = pct + '%';
      });
      if (el.boardCount) {
        var countText = '남은 ' + remaining + '건 · 처리 ' + (state.alerts.length - remaining) + '/' + state.alerts.length;
        if (el.boardCount.textContent !== countText) {
          el.boardCount.textContent = countText;
          pulse(el.boardCount, 'is-pop');
        }
      }
    }

    function renderRecord() {
      var store = state.store || loadStore();
      var day = store.days[todayKey()];
      el.recordDate.textContent = todayKey();
      el.recBest.textContent = day && day.best ? day.best + '점' : '—';
      el.recStreak.textContent = (store.streak.count || 0) + '일';
      el.recLast.textContent = day && day.last ? day.last + '점' : '—';

      el.recHistory.innerHTML = '';
      if (!store.history.length) {
        var empty = document.createElement('li');
        empty.className = 'is-empty';
        empty.textContent = '아직 기록이 없습니다. 한 판 시작해 보세요.';
        el.recHistory.appendChild(empty);
        return;
      }
      store.history.slice(0, 3).forEach(function (item) {
        var li = document.createElement('li');
        var left = document.createElement('span');
        left.textContent = item.date.slice(5) + ' · ' + (item.mode === 'practice' ? '연습' : '실전');
        var right = document.createElement('span');
        right.textContent = item.score + '점';
        li.appendChild(left);
        li.appendChild(right);
        el.recHistory.appendChild(li);
      });
    }

    /* ---------------------------------------------------------------- 이벤트 */
    function setMode(mode) {
      if (state.mode === mode) return;
      state.mode = mode;
      resetBoard();
      setStatus(mode === 'live'
        ? '교대 시작을 누르면 60초가 시작됩니다.'
        : '경보 6건을 두 담당에게 배치한 뒤 실행하세요.');
    }

    el.modeLive.addEventListener('click', function () { setMode('live'); });
    el.modePractice.addEventListener('click', function () { setMode('practice'); });

    el.startBtn.addEventListener('click', function () {
      if (state.phase === 'ended') { resetBoard(); setStatus('새 판을 시작합니다.'); return; }
      if (state.mode === 'practice') { runPractice(); return; }
      if (state.phase === 'running') { endLive(); return; }
      startLive();
    });

    // 탭이 돌아오면 스로틀 동안 놓친 경보 도착·처리 완료·종료를 즉시 따라잡는다.
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) syncClock();
    });
    window.addEventListener('focus', syncClock);

    el.resetPlanBtn.addEventListener('click', function () {
      state.queues = { infra: [], sec: [] };
      state.alerts.forEach(function (a) {
        if (a.state === 'queued') { a.owner = null; a.state = state.mode === 'live' ? 'ready' : 'ready'; }
      });
      setStatus('배치를 비웠습니다.');
      render();
    });

    el.retryBtn.addEventListener('click', function () {
      resetBoard();
      setStatus(state.mode === 'live' ? '교대 시작을 누르면 60초가 시작됩니다.' : '경보 6건을 두 담당에게 배치한 뒤 실행하세요.');
    });

    el.switchPracticeBtn.addEventListener('click', function () {
      setMode('practice');
      el.resultBox.hidden = true;
    });

    el.boardDate.textContent = '오늘의 경보';

    /* ---------------------------------------------------------------- 테마 */
    function setTheme(theme) {
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (el.moonIcon) el.moonIcon.style.display = 'none';
        if (el.sunIcon) el.sunIcon.style.display = 'block';
        try { localStorage.setItem('secjobs-theme', 'dark'); } catch (e) {}
      } else {
        document.documentElement.removeAttribute('data-theme');
        if (el.moonIcon) el.moonIcon.style.display = 'block';
        if (el.sunIcon) el.sunIcon.style.display = 'none';
        try { localStorage.setItem('secjobs-theme', 'light'); } catch (e) {}
      }
    }

    (function initTheme() {
      var saved = null;
      try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
      if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) setTheme('dark');
      else setTheme('light');
    })();

    if (el.themeToggle) {
      el.themeToggle.addEventListener('click', function () {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    /* ---------------------------------------------------------------- 시작 */
    // ---- 게임 방법 데모: 경보 탭 → 추천 담당 → 처리 완료 (처음 한 번만 움직임) ----
    (function initOpsGuide() {
      var stage = document.getElementById('opsGuideStage');
      if (!stage) return;
      var alertChip = stage.querySelector('[data-demo-alert]');
      var person = stage.querySelector('[data-demo-person="infra"]');
      var rec = stage.querySelector('[data-demo-rec]');
      var check = stage.querySelector('[data-demo-check]');
      var count = stage.querySelector('[data-demo-count]');
      var done = stage.querySelector('[data-demo-done]');

      function paint(n) {
        if (alertChip) {
          alertChip.classList.toggle('is-tap', n >= 1);
          alertChip.classList.toggle('is-done', n >= 3);
        }
        if (person) person.classList.toggle('is-rec', n === 2);
        if (rec) rec.hidden = n !== 2;
        if (check) check.hidden = n < 3;
        if (count) count.textContent = n >= 3 ? '남은 경보 5건' : '남은 경보 6건';
        if (done) done.hidden = n < 3;
      }

      GameGuide.create({
        key: 'ops_demo_seen_v1',
        steps: document.getElementById('opsGuideSteps'),
        note: document.getElementById('opsGuideNote'),
        replay: document.getElementById('opsGuideReplay'),
        notes: [
          '① 도착한 경보 카드를 누릅니다. 전문 담당이 파란색 추천으로 켜집니다.',
          '② 추천 담당에게 배정하면 처리 시간이 40% 줄어듭니다.',
          '③ 처리가 끝나면 카드가 팝하고 남은 경보 수가 줄어듭니다.'
        ],
        reset: function () { paint(0); },
        step: paint
      });
    })();

    state.store = loadStore();
    buildRoster();
    resetBoard();
    setStatus('교대 시작을 누르면 경보가 들어옵니다.');
  })();
  </script>
</body>
</html>
"""


def build():
    kst_now = datetime.now(KST)
    data = build_data(kst_now)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    html = HTML_TEMPLATE
    html = html.replace("__CSS__", CSS)
    html = html.replace("__GUIDE__", GUIDE_HTML)
    html = html.replace("__GUIDE_SCRIPTS__", game_guide.GUIDE_JS)
    html = html.replace("__DATA_JSON__", payload)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with open(OPS_HTML, "w", encoding="utf-8") as f:
        f.write(harden_html(ui_shell.apply(html, "ops")))

    print("-> 'ops_data.json' 저장 완료 (경보 %d건 · 일일 세트 %d일치)"
          % (len(POOL), DAILY_DAYS))
    print("-> 'ops.html' 생성 완료 (오늘 %s · %s)"
          % (kst_now.date().isoformat(), " · ".join(data["days"][kst_now.date().isoformat()])))
    for offset in range(DAILY_DAYS):
        key = (kst_now.date() + timedelta(days=offset)).isoformat()
        print("   · %s %s" % (key, " ".join(data["days"][key])))
    return len(POOL)


if __name__ == "__main__":
    build()

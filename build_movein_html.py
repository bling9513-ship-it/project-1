#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""자취방 입주 점검 카드(movein.html).

무엇을 하나
  · 원룸·자취방 계약 전 현장에서 한 손으로 훑는 구역별 점검 카드.
    현관 · 거실/방 · 주방 · 욕실 · 베란다/외부 5개 구역, 항목마다 확인 방법을 함께 적는다.
  · 항목별 3상태(확인필요·하자 / 정상 / 해당없음)와 메모를 남기면 진행률이 차고,
    하자 항목만 추려 텍스트로 복사하거나 Canvas 로 점검 리포트 PNG 를 만들어 내려받는다.
  · 입력값은 브라우저 localStorage(`secjobs-movein-v1`)에만 저장한다(전송 없음).
  · 수압·배수·결로·창문·계량기는 선 그림(SVG)으로 확인 위치를 짚어 준다.

지키는 것
  · 이모지 0 · 그라데이션 0 · 인라인 이벤트 핸들러 0 · unsafe-inline 미사용(html_guard CSP 해시)
  · PC(1180px) 요약·진행 레일 + 구역 카드 / 모바일(390px) 한 손 조작 · 하단 고정 바
"""
import json
import os
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(BASE_DIR, "movein.html")
KST = timezone(timedelta(hours=9))
STORE_KEY = "secjobs-movein-v1"

STATES = [
    ("ok", "정상"),
    ("issue", "확인필요·하자"),
    ("na", "해당없음"),
]

# 구역별 점검 항목. key 가 있으면 아래 GUIDE_SVG 의 선 그림을 함께 보여 준다.
SECTIONS = [
    {
        "id": "entry",
        "name": "현관",
        "hint": "문을 닫고 열어 보며 소리·틈·잠금을 먼저 본다",
        "items": [
            {"id": "lock", "title": "도어락·잠금장치", "how": "잠그고 열기 3회, 비밀번호 변경 방법과 관리인 연락처 확인"},
            {"id": "door-gap", "title": "문틀·문 아래 틈", "how": "문을 닫고 바람이 들어오는지 손등으로 확인, 방음·방풍 패드 유무"},
            {"id": "intercom", "title": "인터폰·초인종", "how": "현관 호출과 실내 수화기 통화를 직접 눌러 확인"},
            {"id": "shoe", "title": "신발장 냄새·곰팡이", "how": "문을 열어 바닥과 뒷판 곰팡이, 환기 구멍 확인"},
            {"id": "mailbox", "title": "우편함·택배 보관 위치", "how": "무인택배함 위치와 경비실 수령 가능 시간 확인"},
        ],
    },
    {
        "id": "room",
        "name": "거실·방",
        "hint": "벽·천장 물자국과 창문·콘센트를 먼저 본다",
        "items": [
            {"id": "ceiling", "title": "천장·벽지 물자국", "how": "모서리와 천장 가장자리의 갈색 얼룩·부풀음(누수 흔적)"},
            {"id": "window", "title": "창문 잠금·틈", "how": "잠금장치 작동, 창틀 틈으로 바람, 방충망 찢김", "key": "window"},
            {"id": "condensation", "title": "창틀 결로·곰팡이", "how": "창틀 아래 물자국과 벽지 들뜸, 실리콘 검은 점", "key": "condensation"},
            {"id": "socket", "title": "콘센트 수·접지", "how": "냉장고·히터를 꽂을 자리, 접지 구멍(둥근 구멍) 유무"},
            {"id": "floor", "title": "바닥 들뜸·삐걱임", "how": "장판 이음새를 밟아 들뜸·소리 확인"},
            {"id": "noise", "title": "층간·외부 소음", "how": "창 열고 닫고 1분씩, 위층 발소리와 도로 소음"},
            {"id": "boiler", "title": "보일러·난방 작동", "how": "온수 틀어 3분 안에 따뜻해지는지, 실내 온도 조절 확인"},
            {"id": "light", "title": "채광·환기", "how": "낮에 방문해 창 방향과 맞은편 건물 거리 확인"},
        ],
    },
    {
        "id": "kitchen",
        "name": "주방",
        "hint": "수도·배수는 두 곳을 동시에 틀어 본다",
        "items": [
            {"id": "pressure", "title": "수압·온수", "how": "싱크대와 욕실을 동시에 틀어 수압·온수 온도 확인", "key": "pressure"},
            {"id": "sink-drain", "title": "싱크대 배수", "how": "물을 가득 받았다가 한 번에 빼며 역류·소리 확인", "key": "drain"},
            {"id": "drain-smell", "title": "배수구 냄새·트랩", "how": "배수구를 들여다보고 트랩(물막이) 유무와 냄새 확인"},
            {"id": "gas", "title": "가스레인지·경보기", "how": "점화 3회, 가스 경보기 작동 램프, 밸브 위치 확인"},
            {"id": "hood", "title": "후드 배기", "how": "후드 켜고 종이를 대어 흡입되는지 확인"},
            {"id": "fridge", "title": "냉장고 자리·전원", "how": "냉장고 폭·높이와 전용 콘센트, 문 열림 공간 확인"},
        ],
    },
    {
        "id": "bath",
        "name": "욕실",
        "hint": "물을 실제로 틀어 배수·수압·누수를 본다",
        "items": [
            {"id": "toilet", "title": "변기 물내림", "how": "3회 내려 수압과 하단 누수(바닥 물기) 확인"},
            {"id": "basin", "title": "세면대 배수", "how": "물을 받았다 빼며 배수 속도와 아래 배관 누수 확인"},
            {"id": "shower", "title": "샤워 수압·온수", "how": "샤워기를 틀어 3분간 온수 유지와 배수 확인"},
            {"id": "trap", "title": "욕실 냄새·환풍기", "how": "환풍기 켜고 배기되는지, 바닥 배수구 냄새 확인"},
            {"id": "mold", "title": "타일·실리콘 곰팡이", "how": "모서리 실리콘 검은 점, 줄눈 벗겨짐"},
            {"id": "bath-ceiling", "title": "욕실 천장 누수", "how": "천장 얼룩과 물방울, 윗집 배관 위치 확인"},
        ],
    },
    {
        "id": "outside",
        "name": "베란다·외부",
        "hint": "계량기 번호와 공용부 상태를 사진으로 남긴다",
        "items": [
            {"id": "meter", "title": "전기·수도·가스 계량기", "how": "계량기 번호와 검침값을 사진으로 남기고 현재 사용량 확인", "key": "meter"},
            {"id": "breaker", "title": "분전함·두꺼비집", "how": "차단기 위치와 누전 차단기 시험 버튼 확인"},
            {"id": "balcony-drain", "title": "베란다 배수", "how": "배수구 막힘과 물 고임, 세탁기 연결 호스 확인"},
            {"id": "screen", "title": "방충망·창호", "how": "방충망 찢김과 창호 잠금, 베란다 문 틈"},
            {"id": "common", "title": "공용부 조명·CCTV·주차", "how": "복도 조명·CCTV·주차 가능 대수와 위치 확인"},
        ],
    },
]

# 핵심 확인 포인트 선 그림(색은 CSS currentColor 를 따른다).
GUIDE_SVG = {
    "pressure": (
        '<svg viewBox="0 0 120 72" aria-hidden="true"><path d="M14 58h92" stroke="currentColor" stroke-width="1.6" fill="none" opacity=".4"/>'
        '<path d="M30 58V26h14M44 26v-8" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        '<path d="M44 18c-4 0-7 3-7 6" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        '<path d="M20 34c4-3 9-3 13 0" stroke="currentColor" stroke-width="1.6" fill="none" opacity=".7"/>'
        '<path d="M76 58V30h12v-4" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        '<circle cx="92" cy="24" r="5" stroke="currentColor" stroke-width="1.8" fill="none"/>'
        '<path d="M30 44h14M30 50h14" stroke="currentColor" stroke-width="1.4" opacity=".55"/></svg>'
    ),
    "drain": (
        '<svg viewBox="0 0 120 72" aria-hidden="true"><rect x="26" y="14" width="68" height="18" rx="3" stroke="currentColor" stroke-width="1.8" fill="none"/>'
        '<circle cx="60" cy="23" r="4" stroke="currentColor" stroke-width="1.6" fill="none"/>'
        '<path d="M60 32v18c0 6-8 6-8 12" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        '<circle cx="52" cy="64" r="4" stroke="currentColor" stroke-width="1.6" fill="none"/>'
        '<path d="M48 64c0-4 4-6 8-6" stroke="currentColor" stroke-width="1.4" fill="none" opacity=".6"/>'
        '<path d="M34 23h16M70 23h16" stroke="currentColor" stroke-width="1.4" opacity=".5"/></svg>'
    ),
    "condensation": (
        '<svg viewBox="0 0 120 72" aria-hidden="true"><rect x="22" y="10" width="76" height="50" rx="2" stroke="currentColor" stroke-width="1.8" fill="none"/>'
        '<path d="M22 36h76M60 10v50" stroke="currentColor" stroke-width="1.6" opacity=".6"/>'
        '<path d="M28 46c3-4 7-4 10 0M44 50c3-4 7-4 10 0M70 46c3-4 7-4 10 0" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
        '<circle cx="33" cy="56" r="1.6" fill="currentColor"/><circle cx="49" cy="58" r="1.6" fill="currentColor"/><circle cx="75" cy="55" r="1.6" fill="currentColor"/></svg>'
    ),
    "window": (
        '<svg viewBox="0 0 120 72" aria-hidden="true"><rect x="24" y="12" width="72" height="48" rx="2" stroke="currentColor" stroke-width="1.8" fill="none"/>'
        '<path d="M60 12v48" stroke="currentColor" stroke-width="1.6" opacity=".6"/>'
        '<path d="M52 36h8" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'
        '<path d="M56 32l4 4-4 4" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M30 54h12M78 54h12" stroke="currentColor" stroke-width="1.4" opacity=".5"/>'
        '<path d="M96 20c4 4 4 10 0 14" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>'
    ),
    "meter": (
        '<svg viewBox="0 0 120 72" aria-hidden="true"><rect x="28" y="10" width="64" height="48" rx="4" stroke="currentColor" stroke-width="1.8" fill="none"/>'
        '<circle cx="60" cy="32" r="12" stroke="currentColor" stroke-width="1.6" fill="none"/>'
        '<path d="M60 32l7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
        '<path d="M38 50h44" stroke="currentColor" stroke-width="1.4" opacity=".5"/>'
        '<path d="M40 22h6M74 22h6" stroke="currentColor" stroke-width="1.6" opacity=".7"/></svg>'
    ),
}


# ---------------------------------------------------------------------------
# 데이터 검증
# ---------------------------------------------------------------------------
def validate(sections=None):
    sections = sections if sections is not None else SECTIONS
    if len(sections) != 5:
        raise SystemExit("구역이 %d개입니다(5개 필요)." % len(sections))
    seen = set()
    total = 0
    keys = set()
    for section in sections:
        if not section.get("items"):
            raise SystemExit("%s 구역에 항목이 없습니다." % section.get("name"))
        for item in section["items"]:
            if item["id"] in seen:
                raise SystemExit("항목 ID 중복: %s" % item["id"])
            seen.add(item["id"])
            if not item.get("title") or not item.get("how"):
                raise SystemExit("%s 항목에 제목/확인 방법이 비었습니다." % item["id"])
            if item.get("key"):
                if item["key"] not in GUIDE_SVG:
                    raise SystemExit("%s 그림이 없습니다: %s" % (item["id"], item["key"]))
                keys.add(item["key"])
            total += 1
    if total < 25:
        raise SystemExit("점검 항목이 %d개입니다(25개 이상 필요)." % total)
    if keys != set(GUIDE_SVG):
        raise SystemExit("핵심 확인 그림이 항목에 모두 연결되지 않았습니다: %s" % sorted(set(GUIDE_SVG) - keys))
    return sections


def payload_for():
    validate()
    return {
        "sections": [
            {
                "id": section["id"],
                "name": section["name"],
                "hint": section["hint"],
                "items": [
                    {"id": item["id"], "title": item["title"], "how": item["how"], "key": item.get("key")}
                    for item in section["items"]
                ],
            }
            for section in SECTIONS
        ],
        "states": [{"id": key, "label": label} for key, label in STATES],
        "storeKey": STORE_KEY,
        "total": sum(len(section["items"]) for section in SECTIONS),
    }


def build(out_path=None, today=None):
    today = today or datetime.now(KST).date()
    payload = payload_for()

    sections_html = ""
    for section in payload["sections"]:
        items_html = ""
        for item in section["items"]:
            guide = ""
            if item["key"]:
                guide = ('<div class="mv-guide" aria-hidden="true">' + GUIDE_SVG[item["key"]] + '</div>')
            items_html += (
                '<article class="mv-item" data-item="{iid}" data-section="{sid}">'
                '<div class="mv-item-head">'
                '<div class="mv-item-title"><h3>{title}</h3><p>{how}</p></div>'
                '{guide}'
                '</div>'
                '<div class="mv-seg" role="group" aria-label="{title} 상태">'
                '<button type="button" class="mv-seg-btn" data-state="issue" aria-pressed="false">'
                '<span class="mv-dot is-issue"></span>확인필요·하자</button>'
                '<button type="button" class="mv-seg-btn" data-state="ok" aria-pressed="false">'
                '<span class="mv-dot is-ok"></span>정상</button>'
                '<button type="button" class="mv-seg-btn" data-state="na" aria-pressed="false">'
                '<span class="mv-dot is-na"></span>해당없음</button>'
                '</div>'
                '<div class="mv-note-wrap" hidden>'
                '<label class="mv-sr" for="note-{iid}">{title} 메모</label>'
                '<input class="mv-note" id="note-{iid}" data-note="{iid}" type="text" '
                'placeholder="예: 창틀 아래 물자국, 보일러 온수 늦음" maxlength="120" autocomplete="off">'
                '</div>'
                '</article>'
            ).format(iid=item["id"], sid=section["id"], title=item["title"],
                     how=item["how"], guide=guide)
        sections_html += (
            '<section class="mv-section" id="mv-sec-{sid}" aria-labelledby="mv-h-{sid}">'
            '<div class="mv-section-head"><h2 id="mv-h-{sid}">{name}</h2>'
            '<p>{hint}</p></div>'
            '<div class="mv-items">{items}</div>'
            '</section>'
        ).format(sid=section["id"], name=section["name"], hint=section["hint"], items=items_html)

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__SECTIONS__", sections_html)
            .replace("__TOTAL__", str(payload["total"]))
            .replace("__TODAY__", today.isoformat())
            .replace("__DATA_JSON__", safe_json_for_script(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":"))))
            .replace("__JS__", JS))

    with open(out_path or OUT_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "movein")))

    print("-> 'movein.html' 생성 완료 (구역 %d · 항목 %d · 3상태 토글 · Canvas 리포트)"
          % (len(payload["sections"]), payload["total"]))
    return {"sections": len(payload["sections"]), "items": payload["total"]}


CSS = """
    :root {
      --font-sans: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
      --bg-page: #f8fafc;  --bg-surface: #ffffff;  --bg-subtle: #f1f5f9;  --bg-muted: #e2e8f0;
      --border-subtle: #f1f5f9;  --border-default: #e2e8f0;  --border-strong: #cbd5e1;
      --text-primary: #0f172a;  --text-secondary: #475569;  --text-muted: #94a3b8;
      --accent-primary: #2563eb;  --accent-subtle: #eff6ff;
      --ok-bg: #ecfdf5;  --ok-text: #047857;  --ok-border: #a7f3d0;  --ok-ink: #0f766e;
      --warn-bg: #fffbeb;  --warn-text: #b45309;  --warn-border: #fde68a;
      --issue-bg: #fef2f2;  --issue-text: #b91c1c;  --issue-border: #fecaca;
      --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    }
    [data-theme="dark"] {
      --bg-page: #09090b;  --bg-surface: #18181b;  --bg-subtle: #27272a;  --bg-muted: #3f3f46;
      --border-subtle: #1f1f23;  --border-default: #27272a;  --border-strong: #3f3f46;
      --text-primary: #f4f4f5;  --text-secondary: #a1a1aa;  --text-muted: #71717a;
      --accent-primary: #3b82f6;  --accent-subtle: rgba(59, 130, 246, 0.15);
      --ok-bg: rgba(16, 185, 129, 0.14);  --ok-text: #6ee7b7;  --ok-border: rgba(16, 185, 129, 0.34);  --ok-ink: #5eead4;
      --warn-bg: rgba(245, 158, 11, 0.14);  --warn-text: #fcd34d;  --warn-border: rgba(245, 158, 11, 0.34);
      --issue-bg: rgba(239, 68, 68, 0.14);  --issue-text: #fca5a5;  --issue-border: rgba(239, 68, 68, 0.32);
      --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    [hidden] { display: none !important; }
    body { font-family: var(--font-sans); background: var(--bg-page); color: var(--text-primary);
      line-height: 1.5; letter-spacing: -0.02em; min-height: 100vh; -webkit-font-smoothing: antialiased;
      transition: background-color .2s ease, color .2s ease; }
    .mv-sr { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    .mv-wrap { max-width: 1180px; margin: 0 auto; padding: 20px 20px 110px; }
    .mv-hero h1 { font-size: 25px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .mv-hero p { margin-top: 6px; font-size: 13px; color: var(--text-secondary); max-width: 660px; word-break: keep-all; }
    .mv-pill { display: inline-block; font-size: 11.5px; font-weight: 700; color: var(--accent-primary);
      background: var(--accent-subtle); border-radius: 7px; padding: 3px 9px; }
    .mv-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px; margin-top: 10px;
      font-size: 11.5px; color: var(--text-muted); }
    .mv-dot-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); display: inline-block; }

    .mv-main { display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 16px; margin-top: 16px; align-items: start; }
    .mv-main > * { min-width: 0; }
    .mv-panel { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 17px; box-shadow: var(--card-shadow); }
    .mv-panel h2 { font-size: 12.5px; font-weight: 700; color: var(--text-muted); }
    .mv-rail { display: grid; gap: 12px; position: sticky; top: 76px; }

    .mv-field { margin-top: 10px; display: grid; gap: 5px; }
    .mv-field label { font-size: 10.5px; font-weight: 700; color: var(--text-muted); }
    .mv-field input { width: 100%; border: 1px solid var(--border-default); background: var(--bg-page);
      border-radius: 10px; padding: 9px 11px; font-family: inherit; font-size: 12.5px; color: var(--text-primary); }
    .mv-field input:focus { outline: 2px solid var(--accent-primary); outline-offset: 1px; border-color: transparent; }

    .mv-progress-head { display: flex; align-items: baseline; justify-content: space-between; margin-top: 12px; }
    .mv-progress-head span { font-size: 11px; font-weight: 700; color: var(--text-muted); }
    .mv-progress-head b { font-size: 20px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
    .mv-bar { position: relative; height: 10px; margin-top: 7px; border-radius: 999px; background: var(--bg-subtle);
      overflow: hidden; border: 1px solid var(--border-default); }
    .mv-bar-fill { position: absolute; left: 0; top: 0; bottom: 0; width: 0; background: var(--text-primary);
      border-radius: 999px; transition: width .22s cubic-bezier(0.2, 0.8, 0.2, 1); }
    .mv-counts { margin-top: 11px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
    .mv-count { border: 1px solid var(--border-subtle); border-radius: 10px; padding: 7px 8px; background: var(--bg-page); }
    .mv-count span { display: block; font-size: 10px; font-weight: 700; color: var(--text-muted); }
    .mv-count b { display: block; margin-top: 1px; font-size: 15px; font-weight: 800; font-variant-numeric: tabular-nums; }
    .mv-count.is-issue b { color: var(--issue-text); }
    .mv-count.is-ok b { color: var(--ok-ink); }

    .mv-btn { width: 100%; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary);
      border-radius: 11px; padding: 11px; font-family: inherit; font-size: 12.5px; font-weight: 800; cursor: pointer;
      transition: background-color .15s ease, border-color .15s ease, transform .15s ease, opacity .15s ease; }
    .mv-btn:hover { background: var(--bg-subtle); color: var(--text-primary); }
    .mv-btn:active { transform: scale(0.985); }
    .mv-btn:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }
    .mv-btn:disabled { opacity: .4; cursor: default; }
    .mv-btn.is-primary { border-color: var(--text-primary); background: var(--text-primary); color: var(--bg-surface); margin-top: 12px; }
    .mv-btn.is-primary:hover { opacity: .9; }
    .mv-btn.is-ghost { margin-top: 7px; border-style: dashed; }
    .mv-status { min-height: 16px; margin-top: 7px; font-size: 11px; font-weight: 600; color: var(--ok-ink); }

    .mv-issue-list { margin-top: 9px; display: grid; gap: 6px; max-height: 240px; overflow-y: auto; }
    .mv-issue-empty { font-size: 11.5px; color: var(--text-muted); line-height: 1.55; }
    .mv-issue-row { border: 1px solid var(--issue-border); background: var(--issue-bg); border-radius: 10px;
      padding: 7px 9px; display: flex; flex-direction: column; gap: 1px; }
    .mv-issue-row b { font-size: 11.5px; font-weight: 700; color: var(--issue-text); }
    .mv-issue-row span { font-size: 10.5px; color: var(--text-secondary); word-break: keep-all; }

    .mv-sections { display: grid; gap: 12px; }
    .mv-section { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px;
      padding: 17px; box-shadow: var(--card-shadow); }
    .mv-section-head { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
    .mv-section-head h2 { font-size: 16px; font-weight: 800; letter-spacing: -0.03em; }
    .mv-section-head p { font-size: 11px; color: var(--text-muted); }
    .mv-items { margin-top: 11px; display: grid; gap: 8px; }
    .mv-item { border: 1px solid var(--border-default); border-radius: 13px; padding: 11px 12px; background: var(--bg-page);
      transition: border-color .15s ease, background-color .15s ease; }
    .mv-item.is-issue { border-color: var(--issue-border); background: var(--issue-bg); }
    .mv-item.is-ok { border-color: var(--ok-border); background: var(--ok-bg); }
    .mv-item-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
    .mv-item-title { min-width: 0; }
    .mv-item h3 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.02em; }
    .mv-item-title p { margin-top: 2px; font-size: 11px; color: var(--text-secondary); word-break: keep-all; }
    .mv-guide { flex: 0 0 auto; width: 78px; height: 47px; color: var(--text-muted); opacity: .9; }
    .mv-guide svg { width: 100%; height: 100%; }
    .mv-seg { margin-top: 9px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; }
    .mv-seg-btn { display: inline-flex; align-items: center; justify-content: center; gap: 5px; border: 1px solid var(--border-default);
      background: var(--bg-surface); color: var(--text-muted); border-radius: 9px; padding: 7px 4px;
      font-family: inherit; font-size: 10.5px; font-weight: 700; cursor: pointer; white-space: nowrap;
      transition: background-color .15s ease, border-color .15s ease, color .15s ease; }
    .mv-seg-btn:hover { border-color: var(--border-strong); }
    .mv-seg-btn:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .mv-seg-btn[aria-pressed="true"][data-state="issue"] { border-color: var(--issue-text); background: var(--issue-text); color: #fff; }
    .mv-seg-btn[aria-pressed="true"][data-state="ok"] { border-color: var(--ok-ink); background: var(--ok-ink); color: #fff; }
    .mv-seg-btn[aria-pressed="true"][data-state="na"] { border-color: var(--text-secondary); background: var(--text-secondary); color: var(--bg-surface); }
    .mv-dot { width: 6px; height: 6px; border-radius: 50%; flex: 0 0 auto; }
    .mv-dot.is-issue { background: var(--issue-text); }
    .mv-dot.is-ok { background: var(--ok-ink); }
    .mv-dot.is-na { background: var(--text-muted); }
    .mv-seg-btn[aria-pressed="true"] .mv-dot { background: #fff; }
    .mv-note-wrap { margin-top: 7px; }
    .mv-note { width: 100%; border: 1px solid var(--border-default); background: var(--bg-surface); border-radius: 9px;
      padding: 7px 9px; font-family: inherit; font-size: 11.5px; color: var(--text-primary); }
    .mv-note:focus { outline: 2px solid var(--accent-primary); outline-offset: 1px; border-color: transparent; }

    .mv-mobile-bar { display: none; }

    .mv-notes { margin-top: 22px; background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 16px; padding: 17px 18px; box-shadow: var(--card-shadow); }
    .mv-notes h2 { font-size: 13.5px; font-weight: 800; letter-spacing: -0.03em; }
    .mv-notes ul { margin-top: 10px; display: grid; gap: 7px; padding-left: 16px; }
    .mv-notes li { font-size: 11.5px; line-height: 1.62; color: var(--text-secondary); word-break: keep-all; }
    .mv-notes li b { color: var(--text-primary); }
    .mv-foot { margin-top: 14px; font-size: 10.5px; color: var(--text-muted); text-align: center; line-height: 1.6; }

    @media (max-width: 900px) {
      .mv-wrap { padding: 14px 13px 150px; }
      .mv-hero h1 { font-size: 21px; }
      .mv-hero p { font-size: 12px; }
      .mv-main { display: flex; flex-direction: column; align-items: stretch; gap: 10px; margin-top: 12px; }
      .mv-rail { position: static; order: 2; }
      .mv-sections { order: 1; }
      .mv-panel, .mv-section { padding: 14px; }
      .mv-section-head h2 { font-size: 15px; }
      .mv-item { padding: 10px; }
      .mv-guide { width: 62px; height: 38px; }
      .mv-seg-btn { font-size: 10px; padding: 8px 2px; gap: 3px; }
      .mv-mobile-bar {
        display: flex; align-items: center; gap: 10px; position: fixed; left: 10px; right: 10px;
        bottom: calc(var(--ia-tabbar-h, 64px) + 10px); z-index: 40; padding: 8px 8px 8px 13px;
        background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 14px;
        box-shadow: 0 8px 24px -12px rgba(15, 23, 42, 0.4);
      }
      .mv-mobile-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; flex: 1 1 auto; }
      .mv-mobile-info b { font-size: 15px; font-weight: 800; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
      .mv-mobile-info span { font-size: 10.5px; font-weight: 600; color: var(--text-muted); }
      .mv-mobile-btn { flex: 0 0 auto; border: 1px solid var(--text-primary); background: var(--text-primary);
        color: var(--bg-surface); border-radius: 10px; padding: 10px 14px; font-family: inherit; font-size: 12.5px;
        font-weight: 800; cursor: pointer; }
    }
    @media (max-width: 380px) {
      .mv-seg { gap: 3px; }
      .mv-seg-btn { font-size: 9.5px; }
      .mv-guide { display: none; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 자취방 입주 점검 카드</title>
  <meta name="description" content="원룸·자취방 계약 전 현장에서 한 손으로 훑는 구역별(현관·거실/방·주방·욕실·베란다) 입주 점검 카드. 항목별 3상태(확인필요·하자/정상/해당없음)와 메모, 진행률, 하자만 추린 텍스트 복사와 점검 리포트 PNG 내려받기. 입력은 이 기기에만 저장합니다.">
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

  <header class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <a href="index.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:inherit;">
          <img src="logo.png" alt="Infosec Archive 로고" class="brand-logo-img">
          <span class="brand-name">Infosec Archive</span>
        </a>
      </div>
      <div class="nav-actions">
        <div class="update-meta"><span class="live-dot"></span><span>입주 점검 항목 __TOTAL__개 · 5구역</span></div>
        <button class="icon-btn" id="themeToggle" title="화면 테마 변경" aria-label="화면 테마 변경">
          <svg id="moonIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
          <svg id="sunIcon" style="display:none;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
        </button>
        <a href="https://github.com/bling9513-ship-it/project-1" target="_blank" rel="noopener noreferrer" class="icon-btn" title="GitHub 저장소 바로가기" aria-label="GitHub 저장소 바로가기">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path></svg>
        </a>
      </div>
    </div>
  </header>

  <main class="mv-wrap">
    <section class="mv-hero">
      <span class="mv-pill">생활 · 입주 점검</span>
      <h1>집 보러 온 그 자리에서, 한 손으로 점검</h1>
      <p>원룸·자취방 계약 전에 현관부터 베란다까지 5개 구역을 훑습니다. 항목마다 확인 방법이 적혀 있고, 확인필요·하자만 추려 집주인·부동산에 보낼 문구와 리포트 이미지로 만들 수 있습니다.</p>
      <div class="mv-meta">
        <span>구역 5 · 항목 __TOTAL__개</span>
        <span class="mv-dot-sep"></span>
        <span>입력은 이 기기에만 저장</span>
        <span class="mv-dot-sep"></span>
        <span>기록 기준 __TODAY__</span>
      </div>
    </section>

    <div class="mv-main">
      <aside class="mv-rail" aria-label="점검 요약">
        <section class="mv-panel">
          <h2>점검 대상</h2>
          <div class="mv-field">
            <label for="mvAddress">주소 (동·호수까지)</label>
            <input id="mvAddress" type="text" maxlength="80" autocomplete="off" placeholder="예: 성수동 123-4, 302호">
          </div>
          <div class="mv-field">
            <label for="mvDate">점검일</label>
            <input id="mvDate" type="date">
          </div>
          <div class="mv-progress-head">
            <span>진행률</span>
            <b id="mvPercent">0%</b>
          </div>
          <div class="mv-bar" role="img" aria-labelledby="mvBarLabel">
            <span class="mv-bar-fill" id="mvBarFill"></span>
          </div>
          <p class="mv-sr" id="mvBarLabel">점검 항목 진행률</p>
          <p class="mv-progress-head"><span id="mvDone">0 / __TOTAL__ 확인</span><span id="mvLeft">남은 항목 __TOTAL__</span></p>
          <div class="mv-counts">
            <div class="mv-count is-issue"><span>하자</span><b id="mvIssueCount">0</b></div>
            <div class="mv-count is-ok"><span>정상</span><b id="mvOkCount">0</b></div>
            <div class="mv-count"><span>없음</span><b id="mvNaCount">0</b></div>
          </div>
          <button type="button" class="mv-btn is-primary" id="mvCopy">하자만 추려 텍스트 복사</button>
          <button type="button" class="mv-btn" id="mvPng">점검 리포트 PNG 저장</button>
          <button type="button" class="mv-btn is-ghost" id="mvReset">전체 초기화</button>
          <p class="mv-status" id="mvStatus" role="status" aria-live="polite"></p>
        </section>

        <section class="mv-panel">
          <h2>확인필요·하자 <span id="mvIssueBadge">0건</span></h2>
          <div class="mv-issue-list" id="mvIssueList">
            <p class="mv-issue-empty">아직 하자로 표시한 항목이 없습니다. 현장에서 확인한 문제를 그때그때 눌러 두세요.</p>
          </div>
        </section>
      </aside>

      <section class="mv-sections" aria-label="구역별 점검 항목">
        __SECTIONS__
      </section>
    </div>

    <div class="mv-mobile-bar" id="mvMobileBar">
      <div class="mv-mobile-info">
        <b id="mvMobilePercent">0%</b>
        <span id="mvMobileSub">하자 0 · 확인 0/__TOTAL__</span>
      </div>
      <button type="button" class="mv-mobile-btn" id="mvMobilePng">리포트</button>
    </div>

    <section class="mv-notes">
      <h2>알아 두실 점</h2>
      <ul>
        <li><b>보는 순서</b> — 문을 닫고 들어와 현관 잠금·틈부터, 이어서 물을 실제로 틀어 수압·배수·누수를 봅니다. 물건이 들어오기 전에 하는 것이 가장 좋습니다.</li>
        <li><b>사진</b> — 하자로 표시한 항목은 메모와 함께 사진을 남기세요. 계약서 특약에 적을 때 근거가 됩니다.</li>
        <li><b>계량기</b> — 입주 전 전기·수도·가스 계량기 번호와 검침값을 사진으로 남기면 이후 요금 분쟁을 줄일 수 있습니다.</li>
        <li><b>전달 문구</b> — 복사되는 글은 확인필요·하자 항목만 담습니다. 정상·해당없음 항목은 넣지 않습니다.</li>
        <li><b>저장</b> — 입력값은 이 브라우저(localStorage)에만 저장되며 서버로 보내지 않습니다. 다른 기기·브라우저에서는 보이지 않습니다.</li>
      </ul>
      <p class="mv-foot">점검 항목은 계약 전 확인용 안내이며 법적 효력이 있는 감정이 아닙니다 · 하자 판단은 계약서와 현장 확인을 따르세요.</p>
    </section>
  </main>

  <script type="application/json" id="mvData">__DATA_JSON__</script>
  <script>__JS__</script>
</body>
</html>
"""

JS = r"""
(function () {
  'use strict';

  // ---------- 화면 테마 ----------
  var themeBtn = document.getElementById('themeToggle');
  var moonIcon = document.getElementById('moonIcon');
  var sunIcon = document.getElementById('sunIcon');
  function applyTheme(dark, persist) {
    if (dark) document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    if (moonIcon) moonIcon.style.display = dark ? 'none' : 'block';
    if (sunIcon) sunIcon.style.display = dark ? 'block' : 'none';
    if (persist) { try { localStorage.setItem('secjobs-theme', dark ? 'dark' : 'light'); } catch (e) {} }
  }
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      applyTheme(document.documentElement.getAttribute('data-theme') !== 'dark', true);
    });
  }
  (function initTheme() {
    var saved = null;
    try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
    applyTheme(saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches), false);
  })();

  var DATA;
  try { DATA = JSON.parse(document.getElementById('mvData').textContent); } catch (e) { return; }
  var STORE_KEY = DATA.storeKey;
  var TOTAL = DATA.total;
  var LABEL = {};
  DATA.states.forEach(function (state) { LABEL[state.id] = state.label; });
  var SECTION_NAME = {};
  DATA.sections.forEach(function (section) { SECTION_NAME[section.id] = section.name; });

  function pad(v) { return v < 10 ? '0' + v : String(v); }
  function todayString() {
    var now = new Date();
    var shifted = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + 9 * 3600000);
    return shifted.getFullYear() + '-' + pad(shifted.getMonth() + 1) + '-' + pad(shifted.getDate());
  }

  var store = { address: '', date: todayString(), states: {}, notes: {}, updated: '' };
  (function load() {
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); } catch (e) { raw = null; }
    if (!raw || typeof raw !== 'object') return;
    store.address = typeof raw.address === 'string' ? raw.address : '';
    store.date = typeof raw.date === 'string' && raw.date ? raw.date : todayString();
    store.states = raw.states && typeof raw.states === 'object' ? raw.states : {};
    store.notes = raw.notes && typeof raw.notes === 'object' ? raw.notes : {};
    store.updated = typeof raw.updated === 'string' ? raw.updated : '';
  })();
  function save() {
    store.updated = new Date().toISOString();
    try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); } catch (e) {}
  }

  var els = {
    address: document.getElementById('mvAddress'),
    date: document.getElementById('mvDate'),
    percent: document.getElementById('mvPercent'),
    bar: document.getElementById('mvBarFill'),
    done: document.getElementById('mvDone'),
    left: document.getElementById('mvLeft'),
    issue: document.getElementById('mvIssueCount'),
    ok: document.getElementById('mvOkCount'),
    na: document.getElementById('mvNaCount'),
    issueList: document.getElementById('mvIssueList'),
    issueBadge: document.getElementById('mvIssueBadge'),
    status: document.getElementById('mvStatus'),
    copy: document.getElementById('mvCopy'),
    png: document.getElementById('mvPng'),
    reset: document.getElementById('mvReset'),
    mobileBar: document.getElementById('mvMobileBar'),
    mobilePercent: document.getElementById('mvMobilePercent'),
    mobileSub: document.getElementById('mvMobileSub'),
    mobilePng: document.getElementById('mvMobilePng')
  };

  var itemsById = {};
  DATA.sections.forEach(function (section) {
    section.items.forEach(function (item) {
      itemsById[item.id] = { item: item, section: section };
    });
  });

  function itemEl(id) { return document.querySelector('.mv-item[data-item="' + id + '"]'); }

  function counts() {
    var result = { issue: 0, ok: 0, na: 0, done: 0 };
    Object.keys(itemsById).forEach(function (id) {
      var state = store.states[id];
      if (state === 'issue') result.issue += 1;
      else if (state === 'ok') result.ok += 1;
      else if (state === 'na') result.na += 1;
      if (state) result.done += 1;
    });
    return result;
  }

  function applyItem(id) {
    var root = itemEl(id);
    if (!root) return;
    var state = store.states[id];
    root.classList.toggle('is-issue', state === 'issue');
    root.classList.toggle('is-ok', state === 'ok');
    Array.prototype.forEach.call(root.querySelectorAll('.mv-seg-btn'), function (btn) {
      btn.setAttribute('aria-pressed', btn.dataset.state === state ? 'true' : 'false');
    });
    var wrap = root.querySelector('.mv-note-wrap');
    var input = root.querySelector('.mv-note');
    if (wrap) {
      wrap.hidden = state !== 'issue';
      if (state === 'issue' && input) input.value = store.notes[id] || '';
    } else if (input) {
      input.value = store.notes[id] || '';
    }
  }

  function renderIssues() {
    els.issueList.innerHTML = '';
    var rows = [];
    DATA.sections.forEach(function (section) {
      section.items.forEach(function (item) {
        if (store.states[item.id] === 'issue') {
          rows.push({ section: section.name, id: item.id, title: item.title, note: store.notes[item.id] || '' });
        }
      });
    });
    els.issueBadge.textContent = rows.length + '건';
    if (!rows.length) {
      var empty = document.createElement('p');
      empty.className = 'mv-issue-empty';
      empty.textContent = '아직 하자로 표시한 항목이 없습니다. 현장에서 확인한 문제를 그때그때 눌러 두세요.';
      els.issueList.appendChild(empty);
      return rows;
    }
    rows.forEach(function (row) {
      var box = document.createElement('div');
      box.className = 'mv-issue-row';
      var title = document.createElement('b');
      title.textContent = row.section + ' · ' + row.title;
      box.appendChild(title);
      var note = document.createElement('span');
      note.textContent = row.note || '메모 없음';
      box.appendChild(note);
      els.issueList.appendChild(box);
    });
    return rows;
  }

  function render() {
    var c = counts();
    var percent = Math.round(c.done / TOTAL * 100);
    els.percent.textContent = percent + '%';
    els.bar.style.width = percent + '%';
    els.done.textContent = c.done + ' / ' + TOTAL + ' 확인';
    els.left.textContent = '남은 항목 ' + (TOTAL - c.done);
    els.issue.textContent = String(c.issue);
    els.ok.textContent = String(c.ok);
    els.na.textContent = String(c.na);
    els.mobilePercent.textContent = percent + '%';
    els.mobileSub.textContent = '하자 ' + c.issue + ' · 확인 ' + c.done + '/' + TOTAL;
    renderIssues();
  }

  function setItemState(id, state) {
    if (!itemsById[id]) return;
    if (store.states[id] === state) {
      delete store.states[id];
      if (state === 'issue') delete store.notes[id];
    } else {
      store.states[id] = state;
    }
    save();
    applyItem(id);
    render();
    els.status.textContent = '';
  }

  // ---------- 텍스트 리포트 ----------
  function issueRows() {
    var rows = [];
    DATA.sections.forEach(function (section) {
      section.items.forEach(function (item) {
        if (store.states[item.id] === 'issue') {
          rows.push({ section: section.name, title: item.title, note: store.notes[item.id] || '' });
        }
      });
    });
    return rows;
  }

  function reportText() {
    var c = counts();
    var lines = [];
    lines.push('자취방 입주 점검 리포트');
    lines.push('점검일 ' + (store.date || todayString()) + ' · ' + (store.address || '주소 미입력'));
    lines.push('확인 ' + c.done + '/' + TOTAL + ' · 정상 ' + c.ok + ' · 확인필요·하자 ' + c.issue + ' · 해당없음 ' + c.na);
    lines.push('');
    var rows = issueRows();
    if (!rows.length) {
      lines.push('확인필요·하자 항목 없음');
    } else {
      var current = null;
      rows.forEach(function (row) {
        if (row.section !== current) {
          current = row.section;
          lines.push('[' + current + ']');
        }
        lines.push('- ' + row.title + (row.note ? ' : ' + row.note : ''));
      });
    }
    lines.push('');
    lines.push('Infosec Archive · 자취방 입주 점검 카드');
    return lines.join('\n');
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function () { return fallbackCopy(text); });
    }
    fallbackCopy(text);
    return Promise.resolve();
  }
  function fallbackCopy(text) {
    try {
      var area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', 'readonly');
      area.style.position = 'fixed';
      area.style.top = '-1000px';
      document.body.appendChild(area);
      area.select();
      document.execCommand('copy');
      document.body.removeChild(area);
    } catch (e) {}
    return Promise.resolve();
  }

  // ---------- Canvas 리포트 ----------
  var FONT_STACK = '"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif';

  function wrapLines(ctx, text, maxWidth) {
    var words = String(text).split(' ');
    var lines = [];
    var line = '';
    words.forEach(function (word) {
      var next = line ? line + ' ' + word : word;
      if (ctx.measureText(next).width > maxWidth && line) {
        lines.push(line);
        line = word;
      } else {
        line = next;
      }
    });
    if (line) lines.push(line);
    return lines;
  }

  function buildReportCanvas() {
    var rows = issueRows();
    var c = counts();
    var width = 1080;
    var pad = 64;
    var probe = document.createElement('canvas').getContext('2d');
    probe.font = '400 26px ' + FONT_STACK;
    var body = [];
    var lastSection = null;
    rows.forEach(function (row) {
      if (row.section !== lastSection) {
        body.push({ kind: 'section', text: row.section });
        lastSection = row.section;
      }
      body.push({ kind: 'item', text: row.title });
      if (row.note) body.push({ kind: 'note', text: row.note });
    });
    if (!body.length) body.push({ kind: 'empty', text: '확인필요·하자 항목이 없습니다.' });

    var lines = [];
    body.forEach(function (entry) {
      if (entry.kind === 'section') {
        lines.push({ kind: 'section', text: entry.text });
      } else if (entry.kind === 'item') {
        wrapLines(probe, '- ' + entry.text, width - pad * 2 - 24).forEach(function (text) {
          lines.push({ kind: 'item', text: text });
        });
      } else if (entry.kind === 'note') {
        wrapLines(probe, entry.text, width - pad * 2 - 52).forEach(function (text) {
          lines.push({ kind: 'note', text: text });
        });
      } else {
        wrapLines(probe, entry.text, width - pad * 2).forEach(function (text) {
          lines.push({ kind: 'empty', text: text });
        });
      }
    });

    var headerHeight = 300;
    var rowHeight = 34;
    var height = headerHeight + lines.length * rowHeight + 170;
    var scale = 2;
    var canvas = document.createElement('canvas');
    canvas.width = width * scale;
    canvas.height = height * scale;
    var ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);

    // 종이 바탕
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, width, 10);

    ctx.fillStyle = '#2563eb';
    ctx.font = '700 22px ' + FONT_STACK;
    ctx.fillText('자취방 입주 점검', pad, 74);
    ctx.fillStyle = '#0f172a';
    ctx.font = '800 44px ' + FONT_STACK;
    ctx.fillText('입주 점검 리포트', pad, 128);
    ctx.fillStyle = '#475569';
    ctx.font = '500 24px ' + FONT_STACK;
    ctx.fillText('점검일 ' + (store.date || todayString()) + ' · ' + (store.address || '주소 미입력'), pad, 172);

    // 요약 칸
    var chips = [
      { label: '확인', value: c.done + '/' + TOTAL, color: '#0f172a' },
      { label: '하자', value: String(c.issue), color: '#b91c1c' },
      { label: '정상', value: String(c.ok), color: '#047857' },
      { label: '해당없음', value: String(c.na), color: '#64748b' }
    ];
    var chipWidth = (width - pad * 2 - 18 * 3) / 4;
    chips.forEach(function (chip, index) {
      var x = pad + index * (chipWidth + 18);
      ctx.fillStyle = '#f8fafc';
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 1;
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(x, 200, chipWidth, 72, 14);
      else ctx.rect(x, 200, chipWidth, 72);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#94a3b8';
      ctx.font = '700 17px ' + FONT_STACK;
      ctx.fillText(chip.label, x + 18, 228);
      ctx.fillStyle = chip.color;
      ctx.font = '800 28px ' + FONT_STACK;
      ctx.fillText(chip.value, x + 18, 260);
    });

    ctx.fillStyle = '#0f172a';
    ctx.font = '700 24px ' + FONT_STACK;
    ctx.fillText('확인필요 · 하자', pad, headerHeight + 10);

    var y = headerHeight + 48;
    lines.forEach(function (line) {
      if (line.kind === 'section') {
        y += 10;
        ctx.fillStyle = '#2563eb';
        ctx.font = '800 23px ' + FONT_STACK;
        ctx.fillText(line.text, pad, y);
        ctx.fillStyle = '#e2e8f0';
        ctx.fillRect(pad, y + 12, width - pad * 2, 1);
      } else if (line.kind === 'item') {
        ctx.fillStyle = '#0f172a';
        ctx.font = '600 24px ' + FONT_STACK;
        ctx.fillText(line.text, pad + 4, y);
      } else if (line.kind === 'note') {
        ctx.fillStyle = '#64748b';
        ctx.font = '500 21px ' + FONT_STACK;
        ctx.fillText(line.text, pad + 34, y);
      } else {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '500 23px ' + FONT_STACK;
        ctx.fillText(line.text, pad, y);
      }
      y += rowHeight;
    });

    var footerY = height - 66;
    ctx.fillStyle = '#e2e8f0';
    ctx.fillRect(pad, footerY - 22, width - pad * 2, 1);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 19px ' + FONT_STACK;
    ctx.fillText('Infosec Archive · 자취방 입주 점검 카드 · 입력값은 이 브라우저에만 저장됩니다', pad, footerY + 6);
    return canvas;
  }

  function downloadPng() {
    var canvas;
    try {
      canvas = buildReportCanvas();
    } catch (e) {
      els.status.textContent = '리포트 이미지를 만들지 못했습니다. 텍스트 복사를 이용해 주세요.';
      return;
    }
    var url;
    try { url = canvas.toDataURL('image/png'); } catch (e) { url = ''; }
    if (!url) {
      els.status.textContent = '이 브라우저에서는 이미지 저장이 막혀 있습니다. 텍스트 복사를 이용해 주세요.';
      return;
    }
    var link = document.createElement('a');
    link.href = url;
    link.download = '입주점검_' + (store.date || todayString()) + '.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    els.status.textContent = '점검 리포트 PNG 를 내려받았습니다. 확인필요·하자 ' + counts().issue + '건이 담겼습니다.';
  }

  // ---------- 이벤트 ----------
  document.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('.mv-seg-btn') : null;
    if (!btn) return;
    var root = btn.closest('.mv-item');
    if (!root) return;
    setItemState(root.dataset.item, btn.dataset.state);
  });

  document.addEventListener('input', function (event) {
    var input = event.target;
    if (!input || !input.dataset) return;
    if (input.id === 'mvAddress') {
      store.address = input.value;
      save();
      return;
    }
    if (input.id === 'mvDate') {
      store.date = input.value;
      save();
      return;
    }
    if (input.dataset.note) {
      store.notes[input.dataset.note] = input.value;
      save();
      renderIssues();
    }
  });

  els.copy.addEventListener('click', function () {
    var text = reportText();
    copyText(text);
    els.status.textContent = counts().issue
      ? '확인필요·하자 ' + counts().issue + '건을 추려 복사했습니다.'
      : '하자 항목이 없어 "확인필요·하자 항목 없음" 문구를 복사했습니다.';
  });
  els.png.addEventListener('click', downloadPng);
  els.mobilePng.addEventListener('click', downloadPng);

  var resetArmed = false;
  var resetTimer = null;
  els.reset.addEventListener('click', function () {
    if (!resetArmed) {
      resetArmed = true;
      els.reset.textContent = '한 번 더 누르면 모두 지웁니다';
      els.status.textContent = '초기화하면 주소·메모·모든 상태가 지워집니다.';
      resetTimer = window.setTimeout(function () {
        resetArmed = false;
        els.reset.textContent = '전체 초기화';
      }, 4000);
      return;
    }
    if (resetTimer) window.clearTimeout(resetTimer);
    resetArmed = false;
    els.reset.textContent = '전체 초기화';
    store.address = '';
    store.date = todayString();
    store.states = {};
    store.notes = {};
    save();
    els.address.value = '';
    els.date.value = store.date;
    Object.keys(itemsById).forEach(applyItem);
    render();
    els.status.textContent = '모두 지웠습니다.';
  });

  // ---------- 시작 ----------
  els.address.value = store.address;
  els.date.value = store.date || todayString();
  if (!store.date) { store.date = els.date.value; save(); }
  Object.keys(itemsById).forEach(applyItem);
  render();

  // 테스트·디버깅용
  window.MOVEIN = {
    data: DATA,
    store: store,
    set: function (id, state) { setItemState(id, state); },
    note: function (id, text) {
      store.notes[id] = text;
      save();
      var input = document.querySelector('.mv-note[data-note="' + id + '"]');
      if (input) input.value = text;
      if (store.states[id] === 'issue') applyItem(id);
      render();
    },
    counts: counts,
    report: reportText,
    canvas: function () { return buildReportCanvas(); },
    download: downloadPng
  };
})();
"""


if __name__ == "__main__":
    build()

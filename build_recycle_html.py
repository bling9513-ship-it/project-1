# -*- coding: utf-8 -*-
"""재질 표시·분리배출 도식(recycle.html) — 한 장 생활 도식 빌더.

구성
  · 재질 도감: 포장재에 인쇄되는 분리배출 표시(마크)를 계열별로 배치한다.
    기후에너지환경부 「분리배출 표시에 관한 지침」의 표시문자·표시재질·권장 색을 따르며,
    무색페트 · 플라스틱(PET/HDPE/LDPE/PP/PS/OTHER) · 비닐류 · 종이 · 일반팩 · 멸균팩 ·
    캔류(철·알루미늄) · 유리 · 도포·첩합 9종을 인라인 SVG 로 그린다.
  · 마크를 누르면(키보드 Enter/Space 포함) 설명 카드에 재질 이름 · 배출 원칙 ·
    헷갈리기 쉬운 점(종량제 예외)이 바로 열린다.
  · '마크(재질 표시)'와 '배출 방법(지자체 조례)'이 서로 다른 정보임을 카드로 분리해 설명한다.
  · 분리배출 퀴즈: 실제 생활 품목 7종의 표시 조합을 보여 주고 4지선다로 배출 방법을 고른다.
    답을 고르면 근거가 된 마크가 라벨 위에서 강조되고 해설·최종 점수가 나온다.
  · 이모지 0 · 그라데이션 0 · 입력 필드 0. 마크 그림은 법정 도안을 복제하지 않고 뜻을 살려
    단순화한 것으로, 실제 인쇄와 굵기·모양이 조금 다를 수 있다.
"""
import json
import math
import os
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "recycle_data.json")
RECYCLE_HTML = os.path.join(BASE_DIR, "recycle.html")
KST = timezone(timedelta(hours=9))
CHECKED_ON = "2026-11-22"

SOURCES = [
    {
        "label": "기후에너지환경부 「재활용가능자원의 분리수거 등에 관한 지침」",
        "detail": "기후에너지환경부훈령 제18호 · 2026-01-01 시행 · 별표 1 품목별 배출요령",
        "url": "https://www.law.go.kr/admRulLsInfoP.do?admRulId=25829",
    },
    {
        "label": "기후에너지환경부 「분리배출 표시에 관한 지침」",
        "detail": "기후에너지환경부고시 제2026-189호 · 2026-07-23 시행 · 별표 표시 도안",
        "url": "https://www.law.go.kr/LSW/admRulInfoR.do?admRulSeq=2100000283152&chrClsCd=010201",
    },
    {
        "label": "생활폐기물 분리배출 누리집",
        "detail": "기후에너지환경부 운영 · 품목 730종 우리 동네 배출 방법",
        "url": "https://www.wasteguide.or.kr",
    },
    {
        "label": "한국환경공단 분리배출표시 도안",
        "detail": "재질별 표시 도안 원본 내려받기",
        "url": "https://portal.budamgum.or.kr/cmb/portal/epr/system/eprSstmGdce.do?tp=02",
    },
]

GROUPS = ["플라스틱·비닐", "종이·종이팩", "금속·유리", "복합"]

RESINS = [
    {"code": "PET", "name": "폴리에틸렌테레프탈레이트", "use": "투명 음료·생수병"},
    {"code": "HDPE", "name": "고밀도 폴리에틸렌", "use": "세제·샴푸·우유 용기"},
    {"code": "LDPE", "name": "저밀도 폴리에틸렌", "use": "비닐봉투·필름"},
    {"code": "PP", "name": "폴리프로필렌", "use": "요구르트·배달 용기, 뚜껑"},
    {"code": "PS", "name": "폴리스티렌", "use": "컵라면 용기, 스티로폼(EPS)"},
    {"code": "OTHER", "name": "기타·복합 수지", "use": "여러 수지가 섞인 용기"},
]


# ---------------------------------------------------------------------------
# 인라인 SVG — 48×48 뷰박스, 세 변 화살표 + 안쪽 표시문자
# ---------------------------------------------------------------------------
_A = (24.0, 7.6)
_B = (41.0, 36.6)
_C = (7.0, 36.6)


def _arrow(p, q, gap=3.4, head=4.3):
    """p→q 방향 변을 gap 만큼 줄여 그리고 끝에 화살촉을 붙인다."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    sx, sy = p[0] + ux * gap, p[1] + uy * gap
    ex, ey = q[0] - ux * gap, q[1] - uy * gap
    tipx, tipy = ex + ux * 2.4, ey + uy * 2.4
    bx, by = ex - ux * 1.4, ey - uy * 1.4
    left = (bx - uy * head, by + ux * head)
    right = (bx + uy * head, by - ux * head)
    line = '<path d="M%.1f %.1fL%.1f %.1f"/>' % (sx, sy, ex, ey)
    tri = ('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="currentColor" '
           'stroke="none"/>' % (tipx, tipy, left[0], left[1], right[0], right[1]))
    return line + tri


def mark_svg(inner="", slashed=False):
    """분리배출 표시 마크. inner 는 마크 안쪽 표시문자(2~4자)."""
    parts = [
        _arrow(_C, _B),   # 아래 변: 왼쪽 → 오른쪽
        _arrow(_B, _A),   # 오른쪽 변: 아래 → 위
        _arrow(_A, _C),   # 왼쪽 변: 위 → 아래
    ]
    if inner:
        size = {1: 11.0, 2: 10.0, 3: 7.8}.get(len(inner), 6.2)
        parts.append(
            '<text x="24" y="30.6" text-anchor="middle" font-size="%.1f" '
            'font-weight="700" fill="currentColor" stroke="none">%s</text>'
            % (size, inner)
        )
    if slashed:
        parts.append('<path d="M7 5.6L41 42.4" stroke-width="3"/>')
    return (
        '<svg class="rc-svg" viewBox="0 0 48 48" aria-hidden="true" focusable="false" '
        'fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" '
        'stroke-linejoin="round">' + "".join(parts) + "</svg>"
    )


# ---------------------------------------------------------------------------
# 마크 사전 — id · 계열 · 표시문자 · 표시재질 · 이름 · 뜻 · 배출 원칙 · 주의
# ---------------------------------------------------------------------------
def mark(mid, group, inner, short, material, name, meaning, rule, caution, color):
    return {
        "id": mid,
        "group": group,
        "inner": inner,
        "short": short,
        "material": material,
        "name": name,
        "meaning": meaning,
        "rule": rule,
        "caution": caution,
        "color": color,
        "svg": mark_svg(inner, slashed=(mid == "composite")),
    }


MARKS = [
    mark(
        "pet-clear", "플라스틱·비닐", "무색페트", "무색페트", "–", "무색페트 (무색 PET병)",
        "무색 투명한 먹는샘물·음료 페트병",
        "라벨을 떼고 내용물을 비운 뒤 압착해 뚜껑을 닫아, 무색페트로 따로 모아요.",
        "유색 페트병과 화장품·세제 병은 여기로 오지 않아요. 식용이 아닌 화학제품 병은 "
        "무색 투명 PET라도 '플라스틱·PET'으로 표시돼요.",
        "yellow",
    ),
    mark(
        "plastic", "플라스틱·비닐", "플라스틱", "플라스틱", "PET · HDPE · LDPE · PP · PS · OTHER",
        "플라스틱 용기·트레이",
        "용기·트레이 모양의 합성수지 포장재",
        "내용물을 비우고 물로 헹군 뒤 라벨·부속품을 떼어요. 펌프는 안쪽 철제 스프링을 빼요.",
        "물로 헹굴 수 없는 치약 용기는 내용물만 비워요. 칫솔·옷걸이처럼 다른 재질이 붙어 "
        "분리되지 않으면 종량제(큰 것은 대형폐기물)로 가요. PVC는 2021년 개정으로 표시재질 목록에서 빠졌어요.",
        "blue",
    ),
    mark(
        "vinyl", "플라스틱·비닐", "비닐류", "비닐류", "플라스틱과 같은 문자", "비닐류 (필름·시트)",
        "과자·라면 봉지, 1회용 봉투 같은 얇은 막 포장재",
        "내용물을 비우고 헹궈 이물질을 뺀 뒤, 흩날리지 않게 투명·반투명 봉투에 담아요.",
        "두께 0.25mm 미만이 필름형, 그 이상은 시트형이에요. 이물질이 안 지워진 랩필름, "
        "식탁보·고무장갑·장판은 종량제나 대형폐기물이에요.",
        "purple",
    ),
    mark(
        "paper", "종이·종이팩", "종이", "종이", "–", "종이 (고지류)",
        "신문·책자·전단지·골판지 상자",
        "테이프·철핀·비닐코팅을 떼고 반듯하게 펴서 끈으로 묶어요.",
        "영수증(감열지), 금박·은박지, 비닐 코팅 전단지, 벽지, 양면 코팅 종이컵은 종량제예요. "
        "종이 마크는 지정승인을 받은 포장재에만 붙어요.",
        "black",
    ),
    mark(
        "soft-pack", "종이·종이팩", "일반팩", "일반팩", "–", "일반팩 (살균팩)",
        "합성수지가 붙은 종이팩 — 우유팩",
        "내용물을 비우고 물로 헹궈 말린 뒤 빨대·비닐을 떼고 종이팩 전용수거함에 넣어요.",
        "알루미늄박이 붙은 두유·주스팩은 멸균팩이에요. 구분 없이 종이팩으로 내도 되지만, "
        "따로 모으면 재활용이 더 쉬워요.",
        "green",
    ),
    mark(
        "sterile-pack", "종이·종이팩", "멸균팩", "멸균팩", "–", "멸균팩",
        "알루미늄박이 붙은 종이팩 — 두유·주스팩",
        "일반팩과 같이 헹궈 말린 뒤 종이팩 전용수거함에 넣어요. 되도록 일반팩과 따로 모아요.",
        "종이컵은 종이팩이 아니라 종이류예요(양면 코팅이면 종량제). 전용수거함이 없으면 "
        "종이류와 구분되게 묶어 종이류 수거함에 내요.",
        "teal",
    ),
    mark(
        "can", "금속·유리", "캔류", "캔류", "철 · 알루미늄", "캔류 (금속캔)",
        "음료·주류캔, 통조림캔",
        "내용물을 비우고 헹군 뒤 플라스틱 뚜껑을 떼고, 가능하면 압착해요.",
        "부탄가스·살충제 용기는 내용물을 완전히 빼야 해요. 알루미늄 호일은 종량제, "
        "냄비·공구 같은 고철은 캔이 아니라 '고철류'로 나눠요.",
        "gray",
    ),
    mark(
        "glass", "금속·유리", "유리", "유리병", "–", "유리병",
        "음료수병·기타 병류",
        "내용물을 비우고 헹궈 깨지지 않게 내요. 소주·맥주병은 소매점에 반납하면 보증금을 돌려받아요.",
        "깨진 유리컵·유리 조각은 유리병 수거함에서 빼고 지자체 안내대로 내요. 서울시는 "
        "소량을 신문지에 싸서 종량제, 다량은 특수규격마대로 내고, 인천 부평구처럼 가정의 깨진 "
        "유리도 전용 PP마대에 담아 배출하는 곳도 있어요. 내열유리·크리스탈·판유리·도자기는 "
        "특수규격마대나 대형폐기물로 내요.",
        "orange",
    ),
    mark(
        "composite", "복합", "", "도포·첩합", "–", "도포·첩합 등",
        "다른 재질을 붙이거나 코팅해 떼어낼 수 없는 포장재",
        "재질을 나눌 수 없으니 종량제 봉투로 내요.",
        "종이팩 마개가 무게의 10%를 넘거나, 페트병·PSP·용기·트레이에 금속·생분해 수지가 붙어 "
        "분리되지 않는 경우예요. '재활용 어려움' 등급 표시와는 다른 제도예요.",
        "red",
    ),
]

MARK_BY_ID = {item["id"]: item for item in MARKS}


def _quiz(qid, item, meta, symbols, options, answer, evidence, explain):
    return {
        "id": qid,
        "item": item,
        "meta": meta,
        "symbols": symbols,
        "question": "어디에 어떻게 버릴까요?",
        "options": options,
        "answer": answer,
        "evidence": evidence,
        "explain": explain,
    }


def _sym(sid, mark_id, inner, caption):
    return {"id": sid, "mark": mark_id, "inner": inner, "caption": caption}


QUIZZES = [
    _quiz(
        "water-bottle", "무색 생수 페트병",
        "500mL · 몸체 무색페트 · 뚜껑 HDPE · 라벨 PP",
        [_sym("b1", "pet-clear", "무색페트", "몸체"),
         _sym("b2", "plastic", "HDPE", "뚜껑"),
         _sym("b3", "plastic", "PP", "라벨")],
        [
            "라벨을 떼고 내용물을 비운 뒤 압착해 뚜껑을 닫아, 무색페트로 따로 내요.",
            "라벨과 뚜껑을 붙인 채 그대로 플라스틱 용기 수거함에 넣어요.",
            "라벨은 종이류로, 병은 종량제 봉투에 넣어요.",
            "유리병 수거함에 넣고 소매점에서 보증금을 돌려받아요.",
        ],
        0, ["b1"],
        "몸체에 무색페트 표시가 있으니 무색페트로 따로 모아요. 라벨은 떼어 필름이면 비닐류로, "
        "뚜껑은 닫아 함께 내요. 설탕·유기물이 든 음료는 물로 헹군 뒤 말려요.",
    ),
    _quiz(
        "milk-soy", "우유팩과 두유팩",
        "우유팩 = 일반팩(살균팩) · 두유팩 = 멸균팩(알루미늄박)",
        [_sym("m1", "soft-pack", "일반팩", "우유팩"),
         _sym("m2", "sterile-pack", "멸균팩", "두유팩")],
        [
            "우유팩은 종이류, 두유팩은 종량제 봉투에 넣어요.",
            "둘 다 종이팩 전용수거함에 넣되, 되도록 따로 모아요.",
            "물로 헹구지 말고 그대로 종량제 봉투에 넣어요.",
            "우유팩은 플라스틱, 두유팩은 유리로 나눠 버려요.",
        ],
        1, ["m1", "m2"],
        "일반팩과 멸균팩은 모두 종이팩이에요. 내용물을 비우고 헹궈 말린 뒤 빨대·비닐을 떼고 "
        "전용수거함에 넣어요. 알루미늄박이 붙은 멸균팩은 따로 모으면 재활용이 더 쉬워요.",
    ),
    _quiz(
        "snack-bag", "과자봉지와 라면봉지",
        "얇은 막 포장재 · 표면적이 작으면 표시가 없을 수 있어요",
        [_sym("s1", "vinyl", "비닐류", "과자봉지"),
         _sym("s2", "vinyl", "비닐류", "라면봉지")],
        [
            "종이류로 반듯하게 펴서 묶어 내요.",
            "플라스틱 용기 수거함에 넣어요.",
            "부스러기를 털어내고 투명 봉투에 담아 비닐류로 내요.",
            "음식물이 묻었으니 무조건 종량제 봉투에 넣어요.",
        ],
        2, ["s1", "s2"],
        "과자·라면 봉지는 비닐류예요. 부스러기를 털어내고 흩날리지 않게 투명·반투명 봉투에 "
        "담아 내요. 기름때가 심해 이물질이 지워지지 않으면 종량제로 가요.",
    ),
    _quiz(
        "receipt-flyer", "광택 전단지와 편의점 영수증",
        "전단지에는 종이 표시 · 영수증(감열지)에는 표시가 없어요",
        [_sym("p1", "paper", "종이", "광택 전단지")],
        [
            "둘 다 종이류로 펴서 묶어 내요.",
            "영수증은 종이류, 전단지는 비닐류로 나눠요.",
            "영수증은 종량제, 전단지는 종이류로 내요.",
            "비닐 코팅된 전단지와 영수증은 둘 다 종량제 봉투에 넣어요.",
        ],
        3, ["p1"],
        "영수증은 열을 받으면 색이 바뀌는 감열지라 재활용이 안 되고, 비닐 코팅된 광택 전단지도 "
        "종이류가 아니에요. 코팅이 없거나 한 면만 코팅된 전단지는 종이류로 낼 수 있어요.",
    ),
    _quiz(
        "broken-glass", "깨진 유리컵과 빈 맥주병",
        "같은 유리지만 깨지면 유리병 수거함 대상이 아니에요",
        [_sym("g1", "glass", "유리", "맥주병"),
         _sym("g2", "glass", "유리", "깨진 유리컵")],
        [
            "깨진 유리컵은 유리병 수거함에서 빼고 지자체 안내대로 배출하고, 맥주병은 유리병으로 "
            "분리하거나 보증금 대상이면 반납해요.",
            "깨진 유리컵과 맥주병을 씻어서 모두 유리병 수거함에 넣어요.",
            "깨진 유리컵은 신문지에 싸서 종량제, 맥주병도 깨서 종량제 봉투에 넣어요.",
            "깨진 유리컵은 유리병 수거함에, 맥주병은 종량제 봉투에 넣어요.",
        ],
        0, ["g1", "g2"],
        "깨진 유리컵·유리 조각은 유리병 수거함에 넣지 않아요. 서울시는 소량을 신문지에 싸서 "
        "종량제봉투, 다량은 특수규격마대로 배출하도록 안내하고, 인천 부평구처럼 가정에서 나온 "
        "깨진 유리도 전용 PP마대를 사서 수거업체에 요청하는 지자체도 있어요. 온전한 맥주·소주병은 "
        "유리병으로 내고, 빈용기보증금 대상이면 소매점에 반납해 보증금을 받아요.",
    ),
    _quiz(
        "toothbrush-tube", "칫솔과 튜브형 치약",
        "치약 용기에만 플라스틱 표시가 있어요",
        [_sym("t1", "plastic", "플라스틱", "치약 튜브")],
        [
            "둘 다 플라스틱 용기 수거함에 넣어요.",
            "둘 다 종량제 봉투에 넣어요.",
            "칫솔은 종량제, 치약 튜브는 내용물만 비워 플라스틱으로 내요.",
            "칫솔은 비닐류, 치약 튜브는 유리로 나눠 버려요.",
        ],
        2, ["t1"],
        "치약 용기는 플라스틱 표시가 있고 물로 헹굴 수 없으니 내용물만 비워 플라스틱으로 내요. "
        "칫솔은 손잡이와 모가 다른 재질로 붙어 있어 지침상 플라스틱 비해당 품목이라 종량제로 가요.",
    ),
    _quiz(
        "can-pot", "참치캔과 플라스틱 손잡이 냄비",
        "캔과 고철은 같은 금속이어도 모으는 곳이 달라요",
        [_sym("c1", "can", "캔류", "참치캔"),
         _sym("c2", "can", "철", "냄비")],
        [
            "둘 다 종량제 봉투에 넣어요.",
            "참치캔은 캔류, 냄비는 손잡이를 떼고 고철류로 내요.",
            "둘 다 플라스틱 용기 수거함에 넣어요.",
            "참치캔은 고철류, 냄비는 캔류로 바꿔 내요.",
        ],
        1, ["c1", "c2"],
        "캔류 마크는 철·알루미늄 캔이에요. 냄비처럼 캔이 아닌 금속은 '고철류'로 따로 모아요. "
        "플라스틱 손잡이 같은 다른 재질은 떼어내고 이물질을 닦아 내요.",
    ),
]


def build_data(now=None):
    kst_now = now or datetime.now(KST)
    ids = [item["id"] for item in MARKS]
    if len(ids) != len(set(ids)):
        raise ValueError("마크 ID 가 중복됩니다")
    if {item["group"] for item in MARKS} != set(GROUPS):
        raise ValueError("마크 계열이 GROUPS 와 어긋납니다")
    for item in MARKS:
        for field in ("name", "meaning", "rule", "caution"):
            if not item.get(field):
                raise ValueError("마크 %s 의 %s 가 비었습니다" % (item["id"], field))
        if "<svg" not in item["svg"]:
            raise ValueError("마크 %s 에 SVG 가 없습니다" % item["id"])
        if len(item["inner"]) > 4:
            raise ValueError("마크 %s 의 표시문자가 너무 깁니다" % item["id"])

    quiz_ids = [q["id"] for q in QUIZZES]
    if len(quiz_ids) != len(set(quiz_ids)):
        raise ValueError("퀴즈 ID 가 중복됩니다")
    if len(QUIZZES) < 6:
        raise ValueError("퀴즈는 6종 이상이어야 합니다")
    for quiz in QUIZZES:
        for sym in quiz["symbols"]:
            sym["svg"] = mark_svg(sym["inner"], slashed=(sym["mark"] == "composite"))
        if len(quiz["options"]) != 4:
            raise ValueError("%s 보기가 4개가 아닙니다" % quiz["id"])
        if len(set(quiz["options"])) != 4:
            raise ValueError("%s 보기가 중복됩니다" % quiz["id"])
        if not 0 <= quiz["answer"] < 4:
            raise ValueError("%s 정답 인덱스가 범위를 벗어났습니다" % quiz["id"])
        sym_ids = [s["id"] for s in quiz["symbols"]]
        if len(sym_ids) != len(set(sym_ids)):
            raise ValueError("%s 라벨 기호 ID 가 중복됩니다" % quiz["id"])
        for sym in quiz["symbols"]:
            if sym["mark"] not in MARK_BY_ID:
                raise ValueError("%s 가 없는 마크 %s 를 가리킵니다" % (quiz["id"], sym["mark"]))
        if not quiz["evidence"] or not set(quiz["evidence"]) <= set(sym_ids):
            raise ValueError("%s 근거 기호가 라벨 기호에 없습니다" % quiz["id"])

    return {
        "generated": kst_now.strftime("%Y-%m-%d %H:%M KST"),
        "checkedOn": CHECKED_ON,
        "sources": SOURCES,
        "groups": GROUPS,
        "marks": MARKS,
        "resins": RESINS,
        "quizzes": QUIZZES,
        "split": [
            {
                "tag": "① 재질 표시",
                "title": "무엇으로 만들었나",
                "body": "포장재에 인쇄된 삼각 화살표예요. 안쪽 글자(종이·캔류·플라스틱)와 "
                        "아래 재질 문자(철·PET)가 재질을 알려 줘요. 「분리배출 표시에 관한 지침」으로 "
                        "전국이 같은 기준을 써요.",
                "source": "전국 공통 · 제조사가 표시",
            },
            {
                "tag": "② 배출 방법",
                "title": "어디에 내놓나",
                "body": "수거함인지 종량제 봉투인지, 언제 내놓는지는 지자체 조례가 정해요. "
                        "같은 마크라도 동네마다 수거함과 요일이 다를 수 있어요.",
                "source": "지자체별 · 조례가 다름",
            },
        ],
    }


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def _mark_button(item):
    return (
        '<button type="button" class="rc-mark" data-mark="%s" aria-pressed="false" '
        'aria-label="%s">'
        '<span class="rc-mark-art" data-color="%s">%s</span>'
        '<span class="rc-mark-name">%s</span></button>'
        % (item["id"], item["name"], item["color"], item["svg"], item["short"])
    )


def _rows():
    parts = []
    for group in GROUPS:
        items = [m for m in MARKS if m["group"] == group]
        parts.append(
            '<div class="rc-row" data-group="%s">'
            '<span class="rc-row-name">%s</span>'
            '<div class="rc-row-marks">%s</div></div>'
            % (group, group, "".join(_mark_button(m) for m in items))
        )
    return "".join(parts)


def _split_cards(data):
    parts = []
    for card in data["split"]:
        parts.append(
            '<article class="rc-split-card">'
            '<span class="rc-split-tag">%s</span>'
            '<h3>%s</h3>'
            '<p>%s</p>'
            '<span class="rc-split-src">%s</span></article>'
            % (card["tag"], card["title"], card["body"], card["source"])
        )
    return "".join(parts)


def _resin_chips():
    return "".join(
        '<button type="button" class="rc-resin-chip" data-resin="%s" aria-pressed="false">%s</button>'
        % (resin["code"], resin["code"])
        for resin in RESINS
    )


def _sources_html():
    parts = []
    for source in SOURCES:
        parts.append(
            '<a href="%s" target="_blank" rel="noopener noreferrer">%s</a> (%s)'
            % (source["url"], source["label"], source["detail"])
        )
    return " · ".join(parts)


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

      --mk-yellow: #b8860b;
      --mk-blue: #2563eb;
      --mk-purple: #7c3aed;
      --mk-black: #0f172a;
      --mk-green: #15803d;
      --mk-teal: #0f766e;
      --mk-gray: #64748b;
      --mk-orange: #c2410c;
      --mk-red: #dc2626;
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

      --mk-yellow: #eab308;
      --mk-blue: #60a5fa;
      --mk-purple: #a78bfa;
      --mk-black: #e4e4e7;
      --mk-green: #4ade80;
      --mk-teal: #2dd4bf;
      --mk-gray: #94a3b8;
      --mk-orange: #fb923c;
      --mk-red: #f87171;
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

    .rc-wrap { max-width: 900px; margin: 0 auto; padding: 16px 16px 88px; }

    .rc-hero h1 { font-size: 20px; font-weight: 800; letter-spacing: -0.045em; margin-top: 6px; }
    .rc-hero p { margin-top: 3px; font-size: 12px; color: var(--text-secondary); }
    .rc-pill {
      display: inline-block; font-size: 11px; font-weight: 600;
      color: var(--accent-primary); background: var(--accent-subtle);
      border: 1px solid var(--border-default); border-radius: 6px; padding: 3px 8px;
    }
    .rc-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 7px; margin-top: 5px; font-size: 10.5px; color: var(--text-muted); }
    .rc-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); }

    .rc-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 12px; margin: 10px 0; }
    .rc-tab {
      border: 0; background: transparent; border-radius: 9px; padding: 7px 4px;
      font-family: inherit; font-size: 12.5px; font-weight: 600; color: var(--text-secondary);
      cursor: pointer; transition: background-color 160ms ease, color 160ms ease;
    }
    .rc-tab:hover { color: var(--text-primary); }
    .rc-tab.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }
    .rc-tab:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .rc-chips { display: flex; gap: 6px; overflow-x: auto; padding: 1px 0 6px; scrollbar-width: none; }
    .rc-chips::-webkit-scrollbar { display: none; }
    .rc-chip {
      flex: 0 0 auto; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 999px; padding: 4px 10px;
      font-family: inherit; font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap;
      transition: background-color 140ms ease, color 140ms ease, border-color 140ms ease;
    }
    .rc-chip:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .rc-chip.is-active { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }
    .rc-chip:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .rc-guide-grid { display: grid; gap: 9px; align-items: start; }
    .rc-side { display: grid; gap: 9px; align-content: start; min-width: 0; }

    .rc-board {
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 14px; padding: 8px 10px 6px; box-shadow: var(--card-shadow);
    }
    .rc-board-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; padding-bottom: 6px; border-bottom: 1px solid var(--border-subtle); }
    .rc-board-title { font-size: 9.5px; font-weight: 700; letter-spacing: 0.08em; color: var(--text-secondary); }
    .rc-board-note { font-size: 9.5px; color: var(--text-muted); white-space: nowrap; }
    .rc-row { display: flex; align-items: center; gap: 4px; padding: 3px 0; border-bottom: 1px dashed var(--border-default); }
    .rc-row:last-child { border-bottom: 0; }
    .rc-row-name { flex: 0 0 42px; font-size: 10px; font-weight: 600; line-height: 1.25; color: var(--text-muted); word-break: keep-all; }
    .rc-row-marks { flex: 1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2px; min-width: 0; }
    .rc-mark {
      display: flex; flex-direction: column; align-items: center; gap: 2px;
      padding: 4px 2px 3px; border: 1px solid transparent; border-radius: 10px;
      background: transparent; font-family: inherit; cursor: pointer;
      transition: background-color 140ms ease, border-color 140ms ease;
    }
    .rc-mark:hover { background: var(--bg-subtle); }
    .rc-mark:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .rc-mark.is-active { background: var(--accent-subtle); border-color: var(--accent-primary); }
    .rc-mark-art { display: block; width: 34px; height: 34px; }
    .rc-svg { width: 100%; height: 100%; display: block; }
    .rc-mark-name { font-size: 9.5px; font-weight: 600; color: var(--text-secondary); white-space: nowrap; }
    .rc-mark.is-active .rc-mark-name { color: var(--accent-primary); }
    .rc-mark-art[data-color="yellow"] { color: var(--mk-yellow); }
    .rc-mark-art[data-color="blue"] { color: var(--mk-blue); }
    .rc-mark-art[data-color="purple"] { color: var(--mk-purple); }
    .rc-mark-art[data-color="black"] { color: var(--mk-black); }
    .rc-mark-art[data-color="green"] { color: var(--mk-green); }
    .rc-mark-art[data-color="teal"] { color: var(--mk-teal); }
    .rc-mark-art[data-color="gray"] { color: var(--mk-gray); }
    .rc-mark-art[data-color="orange"] { color: var(--mk-orange); }
    .rc-mark-art[data-color="red"] { color: var(--mk-red); }

    .rc-desc {
      display: grid; grid-template-columns: 48px minmax(0, 1fr); gap: 9px;
      padding: 10px; background: var(--bg-surface);
      border: 1px solid var(--border-default); border-radius: 14px; box-shadow: var(--card-shadow);
    }
    .rc-desc-art { width: 48px; height: 48px; padding: 5px; border-radius: 11px; background: var(--bg-subtle); }
    .rc-desc-art[data-color="yellow"] { color: var(--mk-yellow); }
    .rc-desc-art[data-color="blue"] { color: var(--mk-blue); }
    .rc-desc-art[data-color="purple"] { color: var(--mk-purple); }
    .rc-desc-art[data-color="black"] { color: var(--mk-black); }
    .rc-desc-art[data-color="green"] { color: var(--mk-green); }
    .rc-desc-art[data-color="teal"] { color: var(--mk-teal); }
    .rc-desc-art[data-color="gray"] { color: var(--mk-gray); }
    .rc-desc-art[data-color="orange"] { color: var(--mk-orange); }
    .rc-desc-art[data-color="red"] { color: var(--mk-red); }
    .rc-desc-group { font-size: 9.5px; font-weight: 700; color: var(--accent-primary); }
    .rc-desc-name { font-size: 14.5px; font-weight: 800; letter-spacing: -0.035em; margin-top: 1px; }
    .rc-desc-material { font-size: 10px; font-weight: 600; color: var(--text-muted); margin-top: 1px; }
    .rc-desc-meaning { font-size: 11.5px; color: var(--text-secondary); margin-top: 2px; }
    .rc-desc-rule { display: flex; align-items: flex-start; gap: 4px; margin-top: 4px; font-size: 10.5px; line-height: 1.45; color: var(--text-secondary); }
    .rc-tag { flex: 0 0 auto; font-size: 9px; font-weight: 700; border-radius: 4px; padding: 0 4px; }
    .rc-tag-rule { color: var(--accent-primary); background: var(--accent-subtle); border: 1px solid var(--border-default); }
    .rc-desc-caution { display: flex; align-items: flex-start; gap: 4px; margin-top: 4px; font-size: 10.5px; line-height: 1.45; color: var(--text-secondary); }
    .rc-tag-warn { color: var(--warn-text); background: var(--warn-bg); border: 1px solid var(--warn-border); }

    .rc-split { display: grid; gap: 8px; margin-top: 10px; }
    .rc-split-card { padding: 10px 11px; border: 1px solid var(--border-default); border-radius: 12px; background: var(--bg-surface); }
    .rc-split-tag { font-size: 9.5px; font-weight: 700; color: var(--text-muted); }
    .rc-split-card h3 { font-size: 12.5px; font-weight: 800; letter-spacing: -0.03em; margin-top: 1px; }
    .rc-split-card p { font-size: 10.5px; line-height: 1.5; color: var(--text-secondary); margin-top: 3px; }
    .rc-split-src { display: block; margin-top: 4px; font-size: 9.5px; color: var(--text-muted); }
    .rc-note { margin-top: 8px; padding: 8px 10px; border-radius: 10px; background: var(--bg-subtle); font-size: 10.5px; line-height: 1.5; color: var(--text-secondary); }

    .rc-resin { padding: 9px 11px 10px; border: 1px solid var(--border-default); border-radius: 12px; background: var(--bg-surface); }
    .rc-resin-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
    .rc-resin-head h3 { font-size: 12px; font-weight: 800; letter-spacing: -0.03em; }
    .rc-resin-head span { font-size: 9.5px; color: var(--text-muted); }
    .rc-resin-chips { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
    .rc-resin-chip {
      border: 1px solid var(--border-default); background: var(--bg-page); color: var(--text-secondary);
      border-radius: 7px; padding: 3px 8px; font-family: inherit; font-size: 10.5px; font-weight: 700;
      letter-spacing: 0.01em; cursor: pointer;
    }
    .rc-resin-chip:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .rc-resin-chip.is-active { background: var(--accent-primary); border-color: var(--accent-primary); color: #ffffff; }
    .rc-resin-chip:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .rc-resin-note { margin-top: 6px; font-size: 10px; line-height: 1.5; color: var(--text-muted); }

    .rc-foot { margin-top: 10px; font-size: 10px; line-height: 1.6; color: var(--text-muted); }
    .rc-foot a { color: var(--text-secondary); text-decoration: underline; text-underline-offset: 2px; }

    .rc-quiz-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 0 2px 7px; font-size: 11px; color: var(--text-muted); }
    .rc-quiz-head strong { color: var(--text-secondary); font-weight: 700; font-variant-numeric: tabular-nums; }
    .rc-item { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 14px; padding: 11px; box-shadow: var(--card-shadow); }
    .rc-item-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
    .rc-item-head h2 { font-size: 15px; font-weight: 800; letter-spacing: -0.04em; }
    .rc-item-head span { font-size: 9.5px; color: var(--text-muted); text-align: right; max-width: 52%; }
    .rc-ghint { margin-top: 6px; font-size: 10px; line-height: 1.45; color: var(--text-muted); }
    .rc-qlabel { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-top: 7px; padding: 7px 6px; background: var(--bg-subtle); border-radius: 11px; min-height: 62px; }
    .rc-qsym { display: inline-flex; flex-direction: column; align-items: center; gap: 0; width: 58px; padding: 4px 2px 3px; border: 1px solid transparent; border-radius: 9px; }
    .rc-qsym-art { width: 34px; height: 34px; color: var(--text-primary); }
    .rc-qsym-mark { font-size: 9px; font-weight: 700; color: var(--text-primary); white-space: nowrap; line-height: 1.35; }
    .rc-qsym-cap { font-size: 8.5px; font-weight: 600; color: var(--text-muted); white-space: nowrap; line-height: 1.35; }
    .rc-qsym.is-evidence { background: var(--accent-subtle); border-color: var(--accent-primary); }
    .rc-qsym.is-evidence .rc-qsym-art { color: var(--accent-primary); }
    .rc-qsym.is-evidence .rc-qsym-mark { color: var(--accent-primary); }
    .rc-qsym.is-evidence .rc-qsym-cap { color: var(--accent-primary); }
    .rc-question { margin: 10px 2px 7px; font-size: 13px; font-weight: 700; letter-spacing: -0.02em; }
    .rc-quiz-grid { display: grid; gap: 9px; align-items: start; }
    .rc-quiz-main { min-width: 0; }
    .rc-options { display: grid; gap: 5px; }
    .rc-opt {
      display: flex; align-items: center; gap: 8px; width: 100%; text-align: left;
      padding: 9px 10px; border: 1px solid var(--border-default); border-radius: 11px;
      background: var(--bg-surface); color: var(--text-primary); font-family: inherit;
      font-size: 12px; line-height: 1.4; letter-spacing: -0.02em; cursor: pointer;
      transition: background-color 140ms ease, border-color 140ms ease;
    }
    .rc-opt:hover:not(:disabled) { background: var(--bg-subtle); }
    .rc-opt:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .rc-opt-num { flex: 0 0 auto; width: 18px; height: 18px; border-radius: 50%; background: var(--bg-subtle); color: var(--text-secondary); font-size: 10px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; }
    .rc-opt.is-correct { background: var(--ok-bg); border-color: var(--ok-border); color: var(--ok-text); }
    .rc-opt.is-correct .rc-opt-num { background: var(--ok-border); color: var(--ok-bg); }
    .rc-opt.is-wrong { background: var(--no-bg); border-color: var(--no-border); color: var(--no-text); }
    .rc-opt.is-wrong .rc-opt-num { background: var(--no-border); color: var(--no-bg); }
    .rc-opt.is-muted { opacity: 0.5; }
    .rc-opt:disabled { cursor: default; }

    .rc-result { margin-top: 8px; padding: 10px 11px; border-radius: 11px; border: 1px solid var(--ok-border); background: var(--ok-bg); }
    .rc-result.is-no { border-color: var(--no-border); background: var(--no-bg); }
    .rc-result h3 { font-size: 12.5px; font-weight: 800; color: var(--ok-text); }
    .rc-result.is-no h3 { color: var(--no-text); }
    .rc-result p { margin-top: 3px; font-size: 11px; line-height: 1.5; color: var(--text-secondary); }
    .rc-result b { color: var(--text-primary); font-weight: 700; }
    .rc-evidence { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin-top: 6px; }
    .rc-evidence-tag { font-size: 9px; font-weight: 700; color: var(--text-muted); }
    .rc-evidence-item { font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 999px; border: 1px solid var(--accent-primary); color: var(--accent-primary); }

    .rc-actions { display: flex; gap: 7px; margin-top: 9px; }
    .rc-primary { flex: 1; min-height: 42px; border: 0; border-radius: 11px; background: var(--accent-primary); color: #ffffff; font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer; transition: background-color 140ms ease; }
    .rc-primary:hover:not(:disabled) { background: var(--accent-hover); }
    .rc-primary:disabled { background: var(--bg-muted); color: var(--text-muted); cursor: default; }
    .rc-primary:focus-visible { outline: 2px solid var(--accent-hover); outline-offset: 2px; }
    .rc-ghost { min-height: 42px; padding: 0 14px; border-radius: 11px; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary); font-family: inherit; font-size: 12.5px; font-weight: 600; cursor: pointer; }
    .rc-ghost:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .rc-summary { margin-top: 9px; padding: 15px 13px; border: 1px solid var(--border-default); border-radius: 13px; background: var(--bg-surface); text-align: center; box-shadow: var(--card-shadow); }
    .rc-summary h2 { font-size: 15px; font-weight: 800; letter-spacing: -0.035em; }
    .rc-summary p { margin-top: 4px; font-size: 11.5px; color: var(--text-secondary); }
    .rc-summary-score { font-size: 26px; font-weight: 800; letter-spacing: -0.04em; margin-top: 7px; font-variant-numeric: tabular-nums; }
    .rc-summary-score span { font-size: 12.5px; color: var(--text-muted); font-weight: 700; margin-left: 3px; }

    @media (min-width: 900px) {
      .rc-wrap { padding: 22px 22px 96px; }
      .rc-hero h1 { font-size: 24px; }
      .rc-hero p { font-size: 13px; }
      .rc-meta { font-size: 11.5px; }
      .rc-tabs { max-width: 380px; }
      .rc-guide-grid { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 12px; }
      .rc-board { padding: 11px 13px 8px; }
      .rc-row { padding: 5px 0; }
      .rc-row-name { flex-basis: 50px; font-size: 10.5px; }
      .rc-mark { padding: 6px 3px 4px; }
      .rc-mark-art { width: 42px; height: 42px; }
      .rc-mark-name { font-size: 10px; }
      .rc-desc { grid-template-columns: 60px minmax(0, 1fr); padding: 13px; gap: 12px; }
      .rc-desc-art { width: 60px; height: 60px; padding: 6px; }
      .rc-desc-name { font-size: 16px; }
      .rc-desc-meaning { font-size: 12px; }
      .rc-desc-rule { font-size: 11px; }
      .rc-desc-caution { font-size: 11px; }
      .rc-split { grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }
      .rc-quiz-grid { grid-template-columns: minmax(0, 1fr) minmax(0, 1.02fr); gap: 13px; }
      .rc-question { margin-top: 0; }
      .rc-qlabel { padding: 10px 8px; }
      .rc-qsym { width: 60px; }
      .rc-qsym-art { width: 40px; height: 40px; }
      .rc-item-head h2 { font-size: 16px; }
    }

    @media (max-width: 430px) {
      .rc-wrap { padding: 12px 12px 84px; }
      .rc-hero h1 { font-size: 18.5px; }
      .rc-hero p { font-size: 11.5px; }
      .rc-meta { font-size: 10px; }
      .rc-row-name { flex: 0 0 40px; font-size: 9.5px; }
      .rc-mark-art { width: 36px; height: 36px; }
      .rc-mark-name { font-size: 9px; }
      .rc-desc { grid-template-columns: 44px minmax(0, 1fr); gap: 8px; padding: 9px; }
      .rc-desc-art { width: 44px; height: 44px; padding: 4px; }
      .rc-desc-name { font-size: 13.5px; }
      .rc-item-head h2 { font-size: 14.5px; }
      .rc-opt { font-size: 11.5px; padding: 8px 9px; }
    }

    @media (max-width: 340px) {
      .rc-row-name { flex: 0 0 36px; font-size: 9px; }
      .rc-mark-art { width: 29px; height: 29px; }
      .rc-mark-name { font-size: 8.5px; }
      .rc-desc { grid-template-columns: 38px minmax(0, 1fr); }
      .rc-desc-art { width: 38px; height: 38px; padding: 3px; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 재질 표시·분리배출</title>
  <meta name="description" content="포장재에 인쇄된 분리배출 표시(마크)를 눌러 재질과 배출 원칙, 헷갈리는 점을 바로 보고 실제 생활 품목 7종으로 풀어 보는 한 장 생활 도식. 기후에너지환경부 「분리배출 표시에 관한 지침」(제2026-189호) · 「재활용가능자원의 분리수거 등에 관한 지침」(제18호) 기준, 2026-11-22 확인.">
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
          <span>분리배출 표시 지침 확인 2026-11-22</span>
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

  <main class="rc-wrap">
    <section class="rc-hero">
      <span class="rc-pill">생활 도식 · 분리배출</span>
      <h1>재질 표시, 한 장으로 읽기</h1>
      <p>포장재의 마크를 누르면 배출 원칙과 헷갈리는 점이 열립니다. 마지막엔 실제 생활 품목으로 풀어 보세요.</p>
      <div class="rc-meta">
        <span>기후에너지환경부 표시·분리수거 지침</span>
        <span class="rc-sep"></span>
        <span>확인 2026-11-22</span>
      </div>
    </section>

    <div class="rc-tabs" role="tablist" aria-label="보기 전환">
      <button type="button" class="rc-tab is-active" id="rcTabGuide" role="tab" aria-selected="true" aria-controls="rcPanelGuide" data-tab="guide">재질 도감</button>
      <button type="button" class="rc-tab" id="rcTabQuiz" role="tab" aria-selected="false" aria-controls="rcPanelQuiz" data-tab="quiz" tabindex="-1">분리배출 퀴즈</button>
    </div>

    <section id="rcPanelGuide" role="tabpanel" aria-labelledby="rcTabGuide">
      <div class="rc-chips" role="group" aria-label="마크 계열">
        <button type="button" class="rc-chip is-active" data-group="전체" aria-pressed="true">전체</button>
        <button type="button" class="rc-chip" data-group="플라스틱·비닐" aria-pressed="false">플라스틱·비닐</button>
        <button type="button" class="rc-chip" data-group="종이·종이팩" aria-pressed="false">종이·종이팩</button>
        <button type="button" class="rc-chip" data-group="금속·유리" aria-pressed="false">금속·유리</button>
        <button type="button" class="rc-chip" data-group="복합" aria-pressed="false">복합</button>
      </div>

      <div class="rc-guide-grid">
        <div class="rc-board" id="rcBoard" aria-label="재질 표시 마크 도감">
          <div class="rc-board-head">
            <span class="rc-board-title">RECYCLING MARK · 분리배출 표시</span>
            <span class="rc-board-note">마크는 재질 · 수거함은 지자체</span>
          </div>
          __ROWS__
        </div>

        <div class="rc-side">
          <div class="rc-desc" id="rcDesc" aria-live="polite">
            <div class="rc-desc-art" id="rcDescArt" data-color="__FIRST_COLOR__" aria-hidden="true">__FIRST_SVG__</div>
            <div class="rc-desc-body">
              <span class="rc-desc-group" id="rcDescGroup">__FIRST_GROUP__</span>
              <h2 class="rc-desc-name" id="rcDescName">__FIRST_NAME__</h2>
              <p class="rc-desc-material" id="rcDescMaterial">표시재질 __FIRST_MATERIAL__</p>
              <p class="rc-desc-meaning" id="rcDescMeaning">__FIRST_MEANING__</p>
              <p class="rc-desc-rule"><span class="rc-tag rc-tag-rule">배출</span><span id="rcDescRule">__FIRST_RULE__</span></p>
              <p class="rc-desc-caution"><span class="rc-tag rc-tag-warn">주의</span><span id="rcDescCaution">__FIRST_CAUTION__</span></p>
            </div>
          </div>

          <section class="rc-resin" aria-label="플라스틱 재질 문자">
            <div class="rc-resin-head">
              <h3>플라스틱 재질 문자</h3>
              <span>라벨에 이 글자가 있으면 눌러 보세요</span>
            </div>
            <div class="rc-resin-chips" role="group" aria-label="플라스틱 재질 문자">
              __RESIN_CHIPS__
            </div>
            <p class="rc-resin-note">표시 재질 목록에는 PVC가 없지만, 배출 지침의 용기 재질 목록에는 PVC·PSP가 남아 있어요. 같은 플라스틱이라도 표시와 배출 안내가 조금 다를 수 있어요.</p>
          </section>
        </div>
      </div>

      <section class="rc-split" aria-label="마크와 배출 방법의 차이">
        __SPLIT__
      </section>
      <p class="rc-note">그래서 이 페이지는 마크를 읽는 법(전국 공통)과 지침 기준 배출 원칙까지 알려 주고, 마지막 확인은 우리 동네 기준으로 하도록 안내해요.</p>

      <p class="rc-foot">
        출처: __SOURCES__ · 확인일 2026-11-22.
        <br>지자체별 수거 기준이 다를 수 있어요. 수거함 위치·배출 요일·종량제 여부는 우리 동네 조례와 안내를 확인하세요.
        <br>마크 그림은 법정 도안을 그대로 옮기지 않고 뜻을 살려 단순하게 다시 그린 것이에요. 색은 권장 색이라 실제 인쇄는 흑백일 수 있고, 표시가 없는 포장재가 '아무거나 괜찮다'는 뜻은 아니에요.
        <br>분리수거 지침은 2026-11-17 일부개정(제63호)되어 2027-01-01 시행을 앞두고 있어요. 이 도식은 2026-11-22 현재 시행 중인 제18호를 따랐어요.
      </p>
    </section>

    <section id="rcPanelQuiz" role="tabpanel" aria-labelledby="rcTabQuiz" hidden>
      <div class="rc-quiz-head">
        <span id="rcQuizProgress">1 / 7</span>
        <span>정답 <strong id="rcQuizScore">0</strong></span>
      </div>
      <div id="rcQuizBody">
        <div class="rc-quiz-grid">
          <article class="rc-item">
            <div class="rc-item-head">
              <h2 id="rcItemName"></h2>
              <span id="rcItemMeta"></span>
            </div>
            <div class="rc-qlabel" id="rcQuizLabel" aria-label="이 품목의 재질 표시"></div>
            <p class="rc-ghint">표시를 읽고 답을 골라 보세요. 답을 고르면 근거가 된 마크가 파랗게 표시됩니다.</p>
          </article>
          <div class="rc-quiz-main">
            <p class="rc-question" id="rcQuestion"></p>
            <div class="rc-options" id="rcOptions" role="group" aria-label="보기"></div>
            <div class="rc-result" id="rcResult" hidden></div>
            <div class="rc-actions">
              <button type="button" class="rc-primary" id="rcNext" disabled>다음 품목</button>
            </div>
          </div>
        </div>
      </div>
      <div class="rc-summary" id="rcSummary" hidden>
        <h2>일곱 가지를 모두 봤어요</h2>
        <p>고른 답의 근거가 된 마크는 라벨에서 파랗게 표시됐어요. 재질 도감에서 다시 확인해 보세요.</p>
        <div class="rc-summary-score"><b id="rcSummaryNum">0</b><span id="rcSummaryTotal">/ 7</span></div>
        <div class="rc-actions">
          <button type="button" class="rc-primary" id="rcRestart">다시 풀기</button>
          <button type="button" class="rc-ghost" id="rcBackGuide">재질 도감으로</button>
        </div>
      </div>
    </section>
  </main>

  <script type="application/json" id="recycleData">__DATA_JSON__</script>
  <script>
const RECYCLE = JSON.parse(document.getElementById('recycleData').textContent);
__JS__
  </script>
</body>
</html>
"""

JS = r"""
(function () {
  // ---------- 화면 테마 (공통 셸 헤더의 토글) ----------
  const themeBtn = document.getElementById('themeToggle');
  const moonIcon = document.getElementById('moonIcon');
  const sunIcon = document.getElementById('sunIcon');
  function applyTheme(dark, persist) {
    if (dark) document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
    if (moonIcon) moonIcon.style.display = dark ? 'none' : 'block';
    if (sunIcon) sunIcon.style.display = dark ? 'block' : 'none';
    if (persist) {
      try { localStorage.setItem('secjobs-theme', dark ? 'dark' : 'light'); } catch (e) {}
    }
  }
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      applyTheme(document.documentElement.getAttribute('data-theme') !== 'dark', true);
    });
  }
  (function initTheme() {
    let saved = null;
    try { saved = localStorage.getItem('secjobs-theme'); } catch (e) {}
    applyTheme(saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches), false);
  })();

  const MARKS = {};
  RECYCLE.marks.forEach(function (item) { MARKS[item.id] = item; });
  const RESINS = {};
  RECYCLE.resins.forEach(function (item) { RESINS[item.code] = item; });
  const QUIZ = RECYCLE.quizzes;
  const TOTAL = QUIZ.length;

  // ---------- 탭 ----------
  const tabs = Array.from(document.querySelectorAll('.rc-tab'));
  const panels = {
    guide: document.getElementById('rcPanelGuide'),
    quiz: document.getElementById('rcPanelQuiz'),
  };
  function selectTab(key, focus) {
    tabs.forEach(function (tab) {
      const on = tab.getAttribute('data-tab') === key;
      tab.classList.toggle('is-active', on);
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.setAttribute('tabindex', on ? '0' : '-1');
      if (on && focus) tab.focus();
    });
    Object.keys(panels).forEach(function (name) {
      panels[name].hidden = name !== key;
    });
  }
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () { selectTab(tab.getAttribute('data-tab')); });
    tab.addEventListener('keydown', function (event) {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      selectTab(tab.getAttribute('data-tab') === 'guide' ? 'quiz' : 'guide', true);
    });
  });

  // ---------- 마크 도감 ----------
  const markButtons = Array.from(document.querySelectorAll('.rc-mark'));
  const resinChips = Array.from(document.querySelectorAll('.rc-resin-chip'));
  const desc = {
    art: document.getElementById('rcDescArt'),
    group: document.getElementById('rcDescGroup'),
    name: document.getElementById('rcDescName'),
    material: document.getElementById('rcDescMaterial'),
    meaning: document.getElementById('rcDescMeaning'),
    rule: document.getElementById('rcDescRule'),
    caution: document.getElementById('rcDescCaution'),
  };
  let currentMark = null;

  function clearResin() {
    resinChips.forEach(function (chip) {
      chip.classList.remove('is-active');
      chip.setAttribute('aria-pressed', 'false');
    });
  }

  function showMark(id) {
    const item = MARKS[id];
    if (!item) return;
    currentMark = id;
    clearResin();
    markButtons.forEach(function (btn) {
      const on = btn.getAttribute('data-mark') === id;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    desc.art.innerHTML = item.svg;
    desc.art.setAttribute('data-color', item.color);
    desc.group.textContent = item.group;
    desc.name.textContent = item.name;
    desc.material.textContent = '표시재질 ' + (item.material === '–' ? '공란(–)' : item.material);
    desc.meaning.textContent = item.meaning;
    desc.rule.textContent = item.rule;
    desc.caution.textContent = item.caution;
  }

  function showResin(code) {
    const resin = RESINS[code];
    if (!resin) return;
    showMark('plastic');
    resinChips.forEach(function (chip) {
      const on = chip.getAttribute('data-resin') === code;
      chip.classList.toggle('is-active', on);
      chip.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    desc.name.textContent = '플라스틱 · ' + resin.code;
    desc.material.textContent = '표시재질 ' + resin.code + ' · ' + resin.name;
    desc.meaning.textContent = resin.use + '에 주로 쓰는 재질이에요.';
    desc.rule.textContent = MARKS.plastic.rule;
    desc.caution.textContent = MARKS.plastic.caution;
  }

  markButtons.forEach(function (btn) {
    btn.addEventListener('click', function () { showMark(btn.getAttribute('data-mark')); });
  });
  resinChips.forEach(function (chip) {
    chip.addEventListener('click', function () { showResin(chip.getAttribute('data-resin')); });
  });
  if (markButtons.length) showMark(markButtons[0].getAttribute('data-mark'));

  // 계열 칩: 고른 계열의 줄만 남긴다.
  const chips = Array.from(document.querySelectorAll('.rc-chip'));
  const rows = Array.from(document.querySelectorAll('.rc-row'));
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      const group = chip.getAttribute('data-group');
      chips.forEach(function (other) {
        const on = other === chip;
        other.classList.toggle('is-active', on);
        other.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      rows.forEach(function (row) {
        row.hidden = group !== '전체' && row.getAttribute('data-group') !== group;
      });
    });
  });

  // ---------- 분리배출 퀴즈 ----------
  const els = {
    progress: document.getElementById('rcQuizProgress'),
    score: document.getElementById('rcQuizScore'),
    body: document.getElementById('rcQuizBody'),
    name: document.getElementById('rcItemName'),
    meta: document.getElementById('rcItemMeta'),
    label: document.getElementById('rcQuizLabel'),
    question: document.getElementById('rcQuestion'),
    options: document.getElementById('rcOptions'),
    result: document.getElementById('rcResult'),
    next: document.getElementById('rcNext'),
    summary: document.getElementById('rcSummary'),
    summaryNum: document.getElementById('rcSummaryNum'),
    summaryTotal: document.getElementById('rcSummaryTotal'),
    restart: document.getElementById('rcRestart'),
    back: document.getElementById('rcBackGuide'),
  };

  let index = 0;
  let answered = false;
  let correctCount = 0;

  function symName(quiz, id) {
    const sym = quiz.symbols.filter(function (item) { return item.id === id; })[0];
    if (!sym) return id;
    const mark = MARKS[sym.mark];
    return (mark ? mark.short : sym.mark) + ' · ' + sym.caption;
  }

  function renderQuiz() {
    const quiz = QUIZ[index];
    answered = false;
    els.body.hidden = false;
    els.summary.hidden = true;
    els.progress.textContent = (index + 1) + ' / ' + TOTAL;
    els.score.textContent = String(correctCount);
    els.name.textContent = quiz.item;
    els.meta.textContent = quiz.meta;
    els.label.innerHTML = quiz.symbols.map(function (sym) {
      const mark = MARKS[sym.mark];
      return '<span class="rc-qsym" data-sym="' + sym.id + '" aria-hidden="true">'
        + '<span class="rc-qsym-art">' + (sym.svg || (mark ? mark.svg : '')) + '</span>'
        + '<span class="rc-qsym-mark">' + sym.inner + '</span>'
        + '<span class="rc-qsym-cap">' + sym.caption + '</span></span>';
    }).join('');
    els.label.setAttribute('aria-label', quiz.item + ' 재질 표시: '
      + quiz.symbols.map(function (sym) { return sym.caption + ' ' + sym.inner; }).join(', '));
    els.question.textContent = quiz.question;
    els.options.innerHTML = quiz.options.map(function (text, idx) {
      return '<button type="button" class="rc-opt" data-idx="' + idx + '">'
        + '<span class="rc-opt-num">' + (idx + 1) + '</span>'
        + '<span class="rc-opt-text">' + text + '</span></button>';
    }).join('');
    els.result.hidden = true;
    els.result.className = 'rc-result';
    els.result.innerHTML = '';
    els.next.disabled = true;
    els.next.textContent = index === TOTAL - 1 ? '결과 보기' : '다음 품목';
  }

  function markEvidence(quiz) {
    Array.from(els.label.querySelectorAll('.rc-qsym')).forEach(function (node) {
      const id = node.getAttribute('data-sym');
      node.classList.toggle('is-evidence', quiz.evidence.indexOf(id) >= 0);
    });
  }

  function showResult(quiz, ok) {
    els.result.className = 'rc-result' + (ok ? '' : ' is-no');
    els.result.innerHTML = ''
      + '<h3>' + (ok ? '정답이에요' : '표시를 다시 보세요') + '</h3>'
      + '<p>' + quiz.explain + '</p>'
      + (ok ? '' : '<p>맞는 답: <b>' + quiz.options[quiz.answer] + '</b></p>')
      + '<div class="rc-evidence"><span class="rc-evidence-tag">근거 마크</span>'
      + quiz.evidence.map(function (id) {
        return '<span class="rc-evidence-item">' + symName(quiz, id) + '</span>';
      }).join('')
      + '</div>';
    els.result.hidden = false;
    markEvidence(quiz);
    els.next.disabled = false;
  }

  els.options.addEventListener('click', function (event) {
    const btn = event.target.closest('.rc-opt');
    if (!btn || answered) return;
    const quiz = QUIZ[index];
    const picked = Number(btn.getAttribute('data-idx'));
    const ok = picked === quiz.answer;
    answered = true;
    if (ok) correctCount += 1;
    els.score.textContent = String(correctCount);
    Array.from(els.options.querySelectorAll('.rc-opt')).forEach(function (node) {
      const idx = Number(node.getAttribute('data-idx'));
      node.disabled = true;
      if (idx === quiz.answer) node.classList.add('is-correct');
      else if (idx === picked) node.classList.add('is-wrong');
      else node.classList.add('is-muted');
    });
    showResult(quiz, ok);
  });

  els.next.addEventListener('click', function () {
    if (index === TOTAL - 1) {
      els.body.hidden = true;
      els.summary.hidden = false;
      els.summaryNum.textContent = String(correctCount);
      els.summaryTotal.textContent = '/ ' + TOTAL;
      els.progress.textContent = TOTAL + ' / ' + TOTAL;
      return;
    }
    index += 1;
    renderQuiz();
  });

  els.restart.addEventListener('click', function () {
    index = 0;
    correctCount = 0;
    renderQuiz();
  });

  els.back.addEventListener('click', function () {
    selectTab('guide', true);
  });

  renderQuiz();
  selectTab('guide');
})();
"""


def build():
    kst_now = datetime.now(KST)
    data = build_data(kst_now)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    first = MARKS[0]

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__ROWS__", _rows())
            .replace("__SPLIT__", _split_cards(data))
            .replace("__RESIN_CHIPS__", _resin_chips())
            .replace("__SOURCES__", _sources_html())
            .replace("__FIRST_SVG__", first["svg"])
            .replace("__FIRST_COLOR__", first["color"])
            .replace("__FIRST_GROUP__", first["group"])
            .replace("__FIRST_NAME__", first["name"])
            .replace("__FIRST_MATERIAL__", first["material"])
            .replace("__FIRST_MEANING__", first["meaning"])
            .replace("__FIRST_RULE__", first["rule"])
            .replace("__FIRST_CAUTION__", first["caution"])
            .replace("__DATA_JSON__", payload)
            .replace("__JS__", JS))

    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(RECYCLE_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "recycle")))

    print("-> 'recycle_data.json' 저장 완료 (마크 %d종 · 품목 %d개)" % (len(MARKS), len(QUIZZES)))
    print("-> 'recycle.html' 생성 완료 (확인일 %s)" % CHECKED_ON)
    return {
        "marks": len(MARKS),
        "quizzes": len(QUIZZES),
        "groups": len(GROUPS),
        "checkedOn": CHECKED_ON,
    }


if __name__ == "__main__":
    build()

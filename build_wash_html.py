# -*- coding: utf-8 -*-
"""세탁 라벨 읽기(wash.html) — 한 장 생활 도식 빌더.

구성
  · 기호 도감: 실제 옷 케어라벨 모양의 카드 안에 KS K 0021:2024 / ISO 3758:2023 취급표시기호를
    카테고리(물세탁 · 표백 · 건조 · 다림질·드라이)별로 배치한다. 기호를 누르면
    (키보드 Enter/Space 포함) 아래 설명 카드에 이름 · 한 줄 뜻 · 주의할 점이 바로 열린다.
  · 라벨 읽기 퀴즈: 옷 6종의 기호 조합 라벨을 보여 주고 4지선다로 세탁법을 고르게 한다.
    답을 고르면 정답 여부와 함께 근거가 되는 기호가 라벨 위에서 파란색으로 강조된다.
  · 모든 기호는 인라인 SVG 로 직접 그린다(이모지 0 · 그라데이션 0). 그림은 표준 도안을
    복제하지 않고 뜻을 살려 단순화한 것으로, 실제 라벨과 굵기·모양이 조금 다를 수 있다.
  · 출처(국가기술표준원 KS K 0021:2024 · ISO 3758:2023 대조)와 확인일을 하단에 표기한다.
"""
import json
import os
from datetime import datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "wash_data.json")
WASH_HTML = os.path.join(BASE_DIR, "wash.html")
KST = timezone(timedelta(hours=9))
CHECKED_ON = "2026-11-22"
STANDARD = "KS K 0021:2024"
STANDARD_TITLE = "섬유 제품의 취급에 관한 표시 기호 및 그 표시 방법"
STANDARD_EDITION = "2024-12-31 개정 · 국가기술표준원 고시 제2024-0699호"
STANDARD_INTL = "ISO 3758:2023"
STANDARD_INTL_NOTE = "GINETEX 케어 기호 안내(ISO 3758:2023) 대조"
STANDARD_URL = ("https://www.standard.go.kr/KSCI/standardIntro/getStandardSearchView.do"
                "?ksNo=KSK0021")

CATEGORIES = ["물세탁", "표백", "건조", "다림질·드라이"]


# ---------------------------------------------------------------------------
# 인라인 SVG 기호 — 48×48 뷰박스, currentColor 선
# ---------------------------------------------------------------------------
def _svg(inner):
    return (
        '<svg class="ws-svg" viewBox="0 0 48 48" aria-hidden="true" focusable="false" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round">' + inner + "</svg>"
    )


def _text(x, y, txt, size=12.5, weight="700"):
    return (
        '<text x="%s" y="%s" text-anchor="middle" font-size="%s" font-weight="%s" '
        'fill="currentColor" stroke="none">%s</text>' % (x, y, size, weight, txt)
    )


_TUB = (
    '<path d="M7.5 15h33"/>'
    '<path d="M10.5 15l2.9 16.4A6 6 0 0 0 19.3 36h9.4a6 6 0 0 0 5.9-4.6L37.5 15"/>'
)
_WAVE = '<path d="M14 20.4c2.2-1.7 4.2 1.7 6.4 0s4.2 1.7 6.4 0 4.2 1.7 6.4 0" stroke-width="1.5"/>'
_UNDERLINE = '<path d="M13.5 41.6h21"/>'
_CROSS = '<path d="M5.5 5.5l37 37M42.5 5.5l-37 37" stroke-width="2.3"/>'
_HAND = (
    '<path d="M19.4 32.8v-4.6h9.4v4.6a4.7 4.7 0 0 1-9.4 0z" stroke-width="1.8"/>'
    '<path d="M21.4 28.2v-6.1M24.1 28.2v-7.3M26.8 28.2v-6.1" stroke-width="2"/>'
    '<path d="M19.4 30.6c-1.7-.2-2.8-1.4-2.8-2.9" stroke-width="1.8"/>'
)


def tub(number=None, hand=False, weak=False, prohibited=False):
    inner = _TUB
    if hand:
        inner += _HAND
    else:
        inner += _WAVE
        if number:
            inner += _text(24, 31.6, number)
    if weak:
        inner += _UNDERLINE
    if prohibited:
        inner += _CROSS
    return _svg(inner)


_TRIANGLE = '<path d="M24 9.5l17.5 27h-35z"/>'


def triangle(oxygen_only=False, prohibited=False):
    inner = _TRIANGLE
    if oxygen_only:
        inner += ('<path d="M18.6 20.4l9 12.1M23.6 17.4l9 12.1" stroke-width="1.6"/>')
    if prohibited:
        inner += _CROSS
    return _svg(inner)


_SQUARE = '<rect x="8.5" y="9.5" width="31" height="29" rx="1.5"/>'
_HANGER = (
    '<path d="M14 29h20"/>'
    '<path d="M14 29l10-5.4 10 5.4"/>'
    '<path d="M24 23.6v-2.2a2 2 0 0 1 2.8-1.9" stroke-width="1.9"/>'
)


def square(kind="hanger", prohibited=False):
    if kind == "hanger":
        inner = _SQUARE + _HANGER
    elif kind == "shade":
        inner = _SQUARE + '<path d="M9.8 19.6l5.4-5.4" stroke-width="1.8"/>' + _HANGER
    elif kind == "flat":
        inner = _SQUARE + '<path d="M13.5 24h21" stroke-width="1.8"/>'
    elif kind == "machine":
        inner = _SQUARE + '<circle cx="24" cy="24" r="9.5"/>'
    else:
        raise ValueError("알 수 없는 건조 기호: " + kind)
    if prohibited:
        inner += _CROSS
    return _svg(inner)


_IRON = (
    '<path d="M8 34h32"/>'
    '<path d="M12 34c0-6.5 5.4-11 12-11h9a4.5 4.5 0 0 1 4.5 4.5V34"/>'
    '<path d="M21.5 23.2v-3.4a3.2 3.2 0 0 1 3.2-3.2h3.4a3.2 3.2 0 0 1 3.2 3.2v3.4"/>'
)
_DOT = '<circle cx="32" cy="28.6" r="1.5" fill="currentColor" stroke="none"/>'


def iron(prohibited=False):
    inner = _IRON + _DOT
    if prohibited:
        inner += _CROSS
    return _svg(inner)


def dry_clean(letter=None, prohibited=False):
    inner = '<circle cx="24" cy="24" r="14"/>'
    if letter:
        inner += _text(24, 29.6, letter, 15)
    if prohibited:
        inner += _CROSS
    return _svg(inner)


# ---------------------------------------------------------------------------
# 기호 사전 — id · 카테고리 · 이름 · 한 줄 뜻 · 주의할 점
# ---------------------------------------------------------------------------
def symbol(sid, cat, name, meaning, caution, svg):
    return {
        "id": sid,
        "cat": cat,
        "name": name,
        "meaning": meaning,
        "caution": caution,
        "svg": svg,
    }


SYMBOLS = [
    symbol(
        "wash-30", "물세탁", "30℃ 이하 일반 세탁",
        "세탁기 일반 코스로, 30℃를 넘지 않는 물에 세탁해요.",
        "숫자는 권장 온도가 아니라 넘지 말아야 할 최고 온도예요. 더 찬물은 괜찮아요.",
        tub("30"),
    ),
    symbol(
        "wash-30-weak", "물세탁", "30℃ 이하 약한 세탁",
        "물통 아래 밑줄 하나는 약한 세탁(섬세·울 코스)을 뜻해요.",
        "탈수를 짧게 하고 세탁물을 적게 넣어요. 세탁망을 함께 쓰면 더 안전해요.",
        tub("30", weak=True),
    ),
    symbol(
        "wash-40", "물세탁", "40℃ 이하 일반 세탁",
        "세탁기 일반 코스로 40℃ 이하 물에 세탁해요.",
        "표시보다 뜨거운 물은 줄어듦·이염의 원인이 돼요. 새 옷은 단독으로 먼저 빨아 보세요.",
        tub("40"),
    ),
    symbol(
        "wash-hand", "물세탁", "손세탁 (세탁기 사용 금지)",
        "세탁기를 쓰지 말고 손으로 살살 주물러 빨아요. 물통 안에 숫자가 있으면 그 온도가 넘지 말아야 할 최고 온도예요.",
        "KS K 0021:2024는 30℃·40℃ 손세탁으로 나눠 표시하고, 숫자가 없는 국제 기호(ISO 3758:2023)는 상온(약 20~30℃) 손세탁이에요. 세탁기 울 코스도 쓰지 말고, 비틀어 짜지 말고 눌러서 물을 빼요.",
        tub(hand=True),
    ),
    symbol(
        "wash-no", "물세탁", "물세탁 금지",
        "집에서 물로 빨지 말고 세탁소에 맡겨요.",
        "드라이클리닝 표시를 함께 확인하세요. 둘 다 금지면 전문점에 문의해요.",
        tub(prohibited=True),
    ),
    symbol(
        "bleach-any", "표백", "염소계·산소계 표백 가능",
        "빈 세모는 염소계·산소계 표백제를 모두 써도 된다는 뜻이에요.",
        "표백제 라벨의 희석 농도와 물 온도를 먼저 확인하고, 색이 있는 옷은 눈에 안 띄는 곳에 시험해요.",
        triangle(),
    ),
    symbol(
        "bleach-oxygen", "표백", "산소계 표백만 가능",
        "세모 안 사선 두 개는 산소계만 되고 염소계는 안 된다는 뜻이에요.",
        "락스 같은 염소계 표백제는 절대 넣지 마세요. 얼룩엔 산소계 표백제를 미지근한 물에 풀어요.",
        triangle(oxygen_only=True),
    ),
    symbol(
        "bleach-no", "표백", "표백 금지",
        "X 표시는 어떤 표백제도 쓰지 말라는 뜻이에요.",
        "'조금만'도 안 돼요. 얼룩은 표백 대신 중성세제로 부분 세탁해요.",
        triangle(prohibited=True),
    ),
    symbol(
        "dry-hanger", "건조", "옷걸이에 걸어 건조",
        "네모 안 옷걸이는 옷걸이에 걸어 말리라는 뜻이에요.",
        "직사광선보다 바람이 잘 통하는 곳에 걸어요. 젖은 채 오래 두면 냄새가 배요.",
        square("hanger"),
    ),
    symbol(
        "dry-shade", "건조", "그늘에서 건조",
        "네모 왼쪽 위의 짧은 선은 그늘에서 말리라는 표시예요.",
        "햇빛에 오래 두면 색이 바래고 소재가 상해요. 통풍이 잘 되는 그늘을 골라요.",
        square("shade"),
    ),
    symbol(
        "dry-flat", "건조", "뉘어서 건조",
        "네모 안 가로선은 수평으로 뉘어서 말리라는 뜻이에요.",
        "젖은 채 걸면 늘어나요. 울·니트는 특히 뉘어서 말려요.",
        square("flat"),
    ),
    symbol(
        "dry-machine-no", "건조", "기계 건조(건조기) 금지",
        "네모 안 원에 X는 건조기를 쓰지 말라는 뜻이에요.",
        "건조기 열에 줄거나 코팅이 벗겨질 수 있어요. 물기는 눌러 빼고 자연 건조해요.",
        square("machine", prohibited=True),
    ),
    symbol(
        "iron-low", "다림질·드라이", "120℃ 이하 다림질",
        "다리미 점 하나는 최대 120℃로 다리라는 뜻이에요(KS K 0021:2024 · ISO 3758:2023).",
        "스팀은 피하고 헝겊을 한 장 덮으세요. 옛 판본 자료에는 110℃로 적혀 있으니, 옷 라벨에 숫자가 있으면 그 숫자를 먼저 따르세요.",
        iron(),
    ),
    symbol(
        "iron-no", "다림질·드라이", "다림질 금지",
        "다리미에 X는 열을 가하지 말라는 뜻이에요.",
        "코팅·인조가죽·프린트는 열에 눌어붙어요. 주름은 걸어 두고 펴세요.",
        iron(prohibited=True),
    ),
    symbol(
        "clean-p", "다림질·드라이", "드라이클리닝 가능 (P)",
        "동그라미 P는 전문 세탁소의 드라이클리닝이 가능하다는 뜻이에요.",
        "P는 퍼클로로에틸렌 등 일반 용제를 뜻해요. 집에서 쓰는 용제로는 대신하지 마세요.",
        dry_clean("P"),
    ),
    symbol(
        "clean-f", "다림질·드라이", "석유계 드라이클리닝",
        "동그라미 F는 석유계 용제만 쓸 수 있다는 뜻이에요.",
        "세탁소에 '석유계만'이라고 알려 주세요. 용제가 다르면 소재가 상할 수 있어요.",
        dry_clean("F"),
    ),
    symbol(
        "clean-no", "다림질·드라이", "드라이클리닝 금지",
        "동그라미에 X는 드라이클리닝을 하지 말라는 뜻이에요.",
        "물세탁 표시와 함께 보세요. 둘 다 금지된 옷은 전문점에 직접 문의해요.",
        dry_clean(prohibited=True),
    ),
]

SYMBOL_BY_ID = {item["id"]: item for item in SYMBOLS}

# 라벨 안 줄 순서 — 실제 케어라벨은 보통 물세탁 → 표백 → 다림질 → 드라이클리닝 → 건조 순이에요.
LABEL_ROWS = [
    ("물세탁", ["wash-30", "wash-30-weak", "wash-40", "wash-hand", "wash-no"]),
    ("표백", ["bleach-any", "bleach-oxygen", "bleach-no"]),
    ("다림질", ["iron-low", "iron-no"]),
    ("드라이", ["clean-p", "clean-f", "clean-no"]),
    ("건조", ["dry-hanger", "dry-shade", "dry-flat", "dry-machine-no"]),
]


def _quiz(qid, garment, material, symbols, options, answer, evidence, explain):
    return {
        "id": qid,
        "garment": garment,
        "material": material,
        "symbols": symbols,
        "question": "이 옷은 어떻게 세탁해야 할까요?",
        "options": options,
        "answer": answer,
        "evidence": evidence,
        "explain": explain,
    }


QUIZZES = [
    _quiz(
        "wool-knit", "울 니트", "울 100% · 겨울",
        ["wash-hand", "bleach-no", "dry-flat", "iron-no"],
        [
            "상온(약 20~30℃) 물에 손세탁하고, 뉘어서 말려요.",
            "세탁기 울 코스로 돌린 뒤 건조기에 넣어요.",
            "염소계 표백제로 얼룩을 뺀 뒤 다림질해요.",
            "40℃ 일반 세탁 후 옷걸이에 걸어 말려요.",
        ],
        0, ["wash-hand", "dry-flat"],
        "손세탁 표시는 세탁기 울 코스도 쓰지 말라는 뜻이에요. 표백과 다림질은 금지, "
        "건조는 뉘어서 해야 늘어나지 않아요.",
    ),
    _quiz(
        "windbreaker", "기능성 바람막이", "폴리에스터 100% · 발수 코팅",
        ["wash-30-weak", "bleach-no", "dry-shade", "iron-no"],
        [
            "30℃ 약한 코스로 세탁하고 그늘에서 말려요.",
            "40℃ 일반 세탁 후 건조기로 바싹 말려요.",
            "염소계 표백제를 넣고 뜨거운 다리미로 펴요.",
            "드라이클리닝만 맡기고 물세탁은 하지 않아요.",
        ],
        0, ["wash-30-weak", "dry-shade"],
        "코팅이 있는 옷은 약한 세탁과 그늘 건조가 기본이에요. 표백과 다림질은 코팅을 상하게 해요.",
    ),
    _quiz(
        "white-shirt", "흰 면 셔츠", "면 100% · 흰색",
        ["wash-40", "bleach-any", "iron-low", "clean-p"],
        [
            "40℃ 일반 세탁, 염소 표백 가능, 120℃ 이하 다림질이에요.",
            "30℃ 손세탁만 되고 표백은 금지예요.",
            "건조기 고온 건조 후 뜨거운 다리미를 대요.",
            "물세탁과 드라이클리닝이 모두 금지예요.",
        ],
        0, ["wash-40", "bleach-any", "iron-low"],
        "흰 면은 40℃ 일반 세탁과 염소계 표백이 가능해요. 다림질은 점 하나, 120℃ 이하로 낮게 해요.",
    ),
    _quiz(
        "padding", "패딩 점퍼", "겉감 나일론 · 충전재 오리털",
        ["wash-30", "bleach-no", "dry-machine-no", "clean-f"],
        [
            "30℃ 일반 세탁, 표백 금지, 건조기 사용 금지예요.",
            "40℃ 강한 세탁 후 염소계 표백제를 넣어요.",
            "건조기 고온으로 빠르게 말려 부피를 살려요.",
            "뜨거운 다리미로 눌러 주름을 펴요.",
        ],
        0, ["wash-30", "dry-machine-no"],
        "겉감 코팅과 충전재는 건조기 열에 상해요. 세탁 후 물기를 눌러 빼고 그늘에 걸어 말려요.",
    ),
    _quiz(
        "denim", "데님 팬츠", "면 98% · 폴리우레탄 2%",
        ["wash-30", "bleach-no", "iron-low", "clean-no"],
        [
            "뒤집어 30℃로 세탁하고 표백과 드라이클리닝은 피해요.",
            "40℃에서 삶아 빨고 염소계 표백제를 넣어요.",
            "건조기로 고온 건조해 물기를 완전히 빼요.",
            "드라이클리닝 후 뜨거운 다리미로 눌러요.",
        ],
        0, ["wash-30", "bleach-no", "clean-no"],
        "데님은 물 빠짐이 있어요. 뒤집어 30℃로 단독 세탁하고, 표백과 드라이클리닝은 피해요.",
    ),
    _quiz(
        "cashmere-coat", "캐시미어 코트", "캐시미어 90% · 울 10%",
        ["wash-no", "bleach-no", "clean-f"],
        [
            "물세탁은 피하고 석유계 드라이클리닝만 맡겨요.",
            "찬물에 손세탁한 뒤 뉘어서 말려요.",
            "염소계 표백제로 소독한 뒤 그늘에서 말려요.",
            "세탁기 울 코스로 세탁하고 건조기에 넣어요.",
        ],
        0, ["wash-no", "clean-f"],
        "물세탁 금지 표시가 있으면 세탁기 울 코스도 안 돼요. 드라이클리닝은 석유계(F)만 가능해요.",
    ),
]


def build_data(now=None):
    kst_now = now or datetime.now(KST)
    ids = [item["id"] for item in SYMBOLS]
    if len(ids) != len(set(ids)):
        raise ValueError("기호 ID 가 중복됩니다")
    if set(item["cat"] for item in SYMBOLS) != set(CATEGORIES):
        raise ValueError("기호 카테고리가 CATEGORIES 와 어긋납니다")
    for item in SYMBOLS:
        for field in ("name", "meaning", "caution", "svg"):
            if not item.get(field):
                raise ValueError("기호 %s 의 %s 가 비었습니다" % (item["id"], field))
        if "<svg" not in item["svg"]:
            raise ValueError("기호 %s 에 SVG 가 없습니다" % item["id"])

    row_ids = [sid for _name, ids in LABEL_ROWS for sid in ids]
    if sorted(row_ids) != sorted(ids):
        raise ValueError("라벨 줄 구성이 기호 목록과 어긋납니다")

    quiz_ids = [q["id"] for q in QUIZZES]
    if len(quiz_ids) != len(set(quiz_ids)):
        raise ValueError("퀴즈 ID 가 중복됩니다")
    if len(QUIZZES) < 5:
        raise ValueError("퀴즈는 5종 이상이어야 합니다")
    for quiz in QUIZZES:
        if len(quiz["options"]) != 4:
            raise ValueError("%s 보기가 4개가 아닙니다: %d" % (quiz["id"], len(quiz["options"])))
        if not 0 <= quiz["answer"] < 4:
            raise ValueError("%s 정답 인덱스가 범위를 벗어났습니다" % quiz["id"])
        if not quiz["evidence"]:
            raise ValueError("%s 근거 기호가 없습니다" % quiz["id"])
        for sid in quiz["symbols"] + quiz["evidence"]:
            if sid not in SYMBOL_BY_ID:
                raise ValueError("%s 가 없는 기호 %s 를 가리킵니다" % (quiz["id"], sid))
        if not set(quiz["evidence"]) <= set(quiz["symbols"]):
            raise ValueError("%s 근거 기호가 라벨 기호에 없습니다" % quiz["id"])

    return {
        "generated": kst_now.strftime("%Y-%m-%d %H:%M KST"),
        "checkedOn": CHECKED_ON,
        "standard": {
            "code": STANDARD,
            "title": STANDARD_TITLE,
            "org": "국가기술표준원",
            "edition": STANDARD_EDITION,
            "intl": STANDARD_INTL,
            "intlNote": STANDARD_INTL_NOTE,
            "url": STANDARD_URL,
        },
        "categories": CATEGORIES,
        "symbols": SYMBOLS,
        "quizzes": QUIZZES,
    }


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def _symbol_button(item):
    return (
        '<button type="button" class="ws-sym" data-sym="%s" aria-pressed="false" '
        'aria-label="%s">%s</button>' % (item["id"], item["name"], item["svg"])
    )


def _label_rows():
    parts = []
    for name, ids in LABEL_ROWS:
        cat = SYMBOL_BY_ID[ids[0]]["cat"]
        parts.append(
            '<div class="ws-row" data-cat="%s" data-row="%s">'
            '<span class="ws-row-name">%s</span>'
            '<div class="ws-row-syms">%s</div></div>'
            % (cat, name, name, "".join(_symbol_button(SYMBOL_BY_ID[sid]) for sid in ids))
        )
    return "".join(parts)


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

    .ws-wrap { max-width: 880px; margin: 0 auto; padding: 18px 18px 88px; }

    .ws-hero h1 { font-size: 21px; font-weight: 800; letter-spacing: -0.045em; margin-top: 7px; }
    .ws-hero p { margin-top: 4px; font-size: 12.5px; color: var(--text-secondary); }
    .ws-pill {
      display: inline-block; font-size: 11px; font-weight: 600;
      color: var(--accent-primary); background: var(--accent-subtle);
      border: 1px solid var(--border-default); border-radius: 6px; padding: 3px 8px;
    }
    .ws-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 7px; margin-top: 6px; font-size: 11px; color: var(--text-muted); }
    .ws-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); }

    .ws-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 12px; margin: 11px 0; }
    .ws-tab {
      border: 0; background: transparent; border-radius: 9px; padding: 8px 4px;
      font-family: inherit; font-size: 12.5px; font-weight: 600; color: var(--text-secondary);
      cursor: pointer; transition: background-color 160ms ease, color 160ms ease;
    }
    .ws-tab:hover { color: var(--text-primary); }
    .ws-tab.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }
    .ws-tab:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .ws-chips { display: flex; gap: 6px; overflow-x: auto; padding: 1px 0 7px; scrollbar-width: none; }
    .ws-chips::-webkit-scrollbar { display: none; }
    .ws-chip {
      flex: 0 0 auto; border: 1px solid var(--border-default); background: var(--bg-surface);
      color: var(--text-secondary); border-radius: 999px; padding: 5px 11px;
      font-family: inherit; font-size: 11.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
      transition: background-color 140ms ease, color 140ms ease, border-color 140ms ease;
    }
    .ws-chip:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .ws-chip.is-active { background: var(--text-primary); border-color: var(--text-primary); color: var(--bg-surface); }
    .ws-chip:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }

    .ws-label {
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 14px; padding: 9px 12px 5px; box-shadow: var(--card-shadow);
    }
    .ws-label-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; padding-bottom: 7px; border-bottom: 1px solid var(--border-subtle); }
    .ws-label-title { font-size: 9.5px; font-weight: 700; letter-spacing: 0.09em; color: var(--text-secondary); }
    .ws-label-note { font-size: 9.5px; color: var(--text-muted); white-space: nowrap; }
    .ws-row { display: flex; align-items: center; gap: 6px; padding: 4px 0; border-bottom: 1px dashed var(--border-default); }
    .ws-row:last-child { border-bottom: 0; }
    .ws-row-name { flex: 0 0 44px; font-size: 10.5px; font-weight: 600; color: var(--text-muted); white-space: nowrap; }
    .ws-row-syms { flex: 1; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1px; min-width: 0; }
    .ws-sym {
      width: 100%; max-width: 52px; height: 42px; padding: 6px; border: 1px solid transparent; border-radius: 10px;
      background: transparent; color: var(--text-primary); cursor: pointer; justify-self: center;
      display: inline-flex; align-items: center; justify-content: center;
      transition: background-color 140ms ease, color 140ms ease, border-color 140ms ease;
    }
    .ws-sym:hover { background: var(--bg-subtle); }
    .ws-sym.is-active { background: var(--accent-subtle); border-color: var(--accent-primary); color: var(--accent-primary); }
    .ws-sym:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .ws-svg { width: 100%; height: 100%; display: block; }

    .ws-guide-grid { display: grid; gap: 10px; align-items: start; }
    .ws-desc {
      display: grid; grid-template-columns: 56px minmax(0, 1fr); gap: 11px;
      padding: 12px; background: var(--bg-surface);
      border: 1px solid var(--border-default); border-radius: 14px; box-shadow: var(--card-shadow);
    }
    .ws-desc-art { width: 56px; height: 56px; padding: 8px; border-radius: 12px; background: var(--bg-subtle); color: var(--accent-primary); }
    .ws-desc-cat { font-size: 10px; font-weight: 700; color: var(--accent-primary); }
    .ws-desc-name { font-size: 15px; font-weight: 800; letter-spacing: -0.035em; margin-top: 1px; }
    .ws-desc-meaning { font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin-top: 3px; }
    .ws-desc-caution { display: flex; align-items: flex-start; gap: 5px; margin-top: 5px; font-size: 11px; color: var(--text-secondary); line-height: 1.45; }
    .ws-caution-tag {
      flex: 0 0 auto; font-size: 9.5px; font-weight: 700; color: var(--warn-text);
      background: var(--warn-bg); border: 1px solid var(--warn-border); border-radius: 4px; padding: 0 4px;
    }

    .ws-foot { margin-top: 11px; font-size: 10.5px; line-height: 1.65; color: var(--text-muted); }
    .ws-foot a { color: var(--text-secondary); text-decoration: underline; text-underline-offset: 2px; }

    .ws-quiz-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 0 2px 8px; font-size: 11px; color: var(--text-muted); }
    .ws-quiz-head strong { color: var(--text-secondary); font-weight: 700; font-variant-numeric: tabular-nums; }
    .ws-garment { background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 16px; padding: 12px; box-shadow: var(--card-shadow); }
    .ws-garment-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
    .ws-garment-head h2 { font-size: 16px; font-weight: 800; letter-spacing: -0.04em; }
    .ws-garment-head span { font-size: 10.5px; color: var(--text-muted); text-align: right; }
    .ws-ghint { margin-top: 9px; font-size: 10.5px; line-height: 1.5; color: var(--text-muted); }
    .ws-qlabel { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 4px; margin-top: 9px; padding: 7px 6px; background: var(--bg-subtle); border-radius: 12px; min-height: 54px; }
    .ws-qsym { width: 44px; height: 44px; padding: 6px; border: 1px solid transparent; border-radius: 9px; color: var(--text-primary); display: inline-flex; transition: background-color 160ms ease, border-color 160ms ease, color 160ms ease; }
    .ws-qsym.is-evidence { background: var(--accent-subtle); border-color: var(--accent-primary); color: var(--accent-primary); }
    .ws-question { margin: 12px 2px 8px; font-size: 13.5px; font-weight: 700; letter-spacing: -0.02em; }
    .ws-quiz-grid { display: grid; gap: 10px; align-items: start; }
    .ws-quiz-main { min-width: 0; }
    .ws-options { display: grid; gap: 6px; }
    .ws-opt {
      display: flex; align-items: center; gap: 9px; width: 100%; text-align: left;
      padding: 10px 11px; border: 1px solid var(--border-default); border-radius: 12px;
      background: var(--bg-surface); color: var(--text-primary); font-family: inherit;
      font-size: 12.5px; line-height: 1.4; letter-spacing: -0.02em; cursor: pointer;
      transition: background-color 140ms ease, border-color 140ms ease;
    }
    .ws-opt:hover:not(:disabled) { background: var(--bg-subtle); }
    .ws-opt:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 1px; }
    .ws-opt-num { flex: 0 0 auto; width: 18px; height: 18px; border-radius: 50%; background: var(--bg-subtle); color: var(--text-secondary); font-size: 10px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; }
    .ws-opt.is-correct { background: var(--ok-bg); border-color: var(--ok-border); color: var(--ok-text); }
    .ws-opt.is-correct .ws-opt-num { background: var(--ok-border); color: var(--ok-bg); }
    .ws-opt.is-wrong { background: var(--no-bg); border-color: var(--no-border); color: var(--no-text); }
    .ws-opt.is-wrong .ws-opt-num { background: var(--no-border); color: var(--no-bg); }
    .ws-opt.is-muted { opacity: 0.5; }
    .ws-opt:disabled { cursor: default; }

    .ws-result { margin-top: 10px; padding: 11px 12px; border-radius: 12px; border: 1px solid var(--ok-border); background: var(--ok-bg); }
    .ws-result.is-no { border-color: var(--no-border); background: var(--no-bg); }
    .ws-result h3 { font-size: 13px; font-weight: 800; color: var(--ok-text); }
    .ws-result.is-no h3 { color: var(--no-text); }
    .ws-result p { margin-top: 4px; font-size: 11.5px; line-height: 1.55; color: var(--text-secondary); }
    .ws-result b { color: var(--text-primary); font-weight: 700; }
    .ws-evidence { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin-top: 7px; }
    .ws-evidence-tag { font-size: 9.5px; font-weight: 700; color: var(--text-muted); }
    .ws-evidence-item { font-size: 10.5px; font-weight: 600; padding: 2px 7px; border-radius: 999px; border: 1px solid var(--accent-primary); color: var(--accent-primary); }

    .ws-actions { display: flex; gap: 8px; margin-top: 10px; }
    .ws-primary { flex: 1; min-height: 44px; border: 0; border-radius: 12px; background: var(--accent-primary); color: #ffffff; font-family: inherit; font-size: 13px; font-weight: 700; cursor: pointer; transition: background-color 140ms ease; }
    .ws-primary:hover:not(:disabled) { background: var(--accent-hover); }
    .ws-primary:disabled { background: var(--bg-muted); color: var(--text-muted); cursor: default; }
    .ws-primary:focus-visible { outline: 2px solid var(--accent-hover); outline-offset: 2px; }
    .ws-ghost { min-height: 44px; padding: 0 16px; border-radius: 12px; border: 1px solid var(--border-default); background: var(--bg-surface); color: var(--text-secondary); font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer; }
    .ws-ghost:hover { background: var(--bg-subtle); color: var(--text-primary); }

    .ws-summary { margin-top: 10px; padding: 16px 14px; border: 1px solid var(--border-default); border-radius: 14px; background: var(--bg-surface); text-align: center; box-shadow: var(--card-shadow); }
    .ws-summary h2 { font-size: 16px; font-weight: 800; letter-spacing: -0.035em; }
    .ws-summary p { margin-top: 5px; font-size: 12px; color: var(--text-secondary); }
    .ws-summary-score { font-size: 27px; font-weight: 800; letter-spacing: -0.04em; margin-top: 8px; font-variant-numeric: tabular-nums; }
    .ws-summary-score span { font-size: 13px; color: var(--text-muted); font-weight: 700; margin-left: 3px; }

    @media (min-width: 900px) {
      .ws-hero h1 { font-size: 24px; }
      .ws-tabs { max-width: 380px; }
      .ws-hero p { font-size: 13px; }
      .ws-guide-grid { grid-template-columns: minmax(0, 1.18fr) minmax(0, 1fr); gap: 12px; }
      .ws-quiz-grid { grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: 14px; }
      .ws-row { padding: 7px 0; }
      .ws-row-name { flex-basis: 52px; font-size: 11px; }
      .ws-sym { height: 46px; max-width: 56px; padding: 7px; }
      .ws-desc { grid-template-columns: 64px minmax(0, 1fr); padding: 14px; gap: 12px; }
      .ws-desc-art { width: 64px; height: 64px; }
      .ws-desc-name { font-size: 16px; }
      .ws-desc-meaning { font-size: 12.5px; }
      .ws-qlabel { padding: 10px 8px; }
      .ws-qsym { width: 46px; height: 46px; }
      .ws-question { margin-top: 0; }
    }

    @media (max-width: 430px) {
      .ws-wrap { padding: 14px 14px 84px; }
      .ws-hero h1 { font-size: 19.5px; }
      .ws-row-name { flex: 0 0 46px; font-size: 10px; }
      .ws-sym { width: 40px; height: 40px; padding: 5px; }
      .ws-desc { grid-template-columns: 50px minmax(0, 1fr); gap: 10px; padding: 11px; }
      .ws-desc-art { width: 50px; height: 50px; padding: 7px; }
      .ws-desc-name { font-size: 14px; }
      .ws-garment-head h2 { font-size: 15px; }
      .ws-opt { font-size: 12px; padding: 9px 10px; }
    }

    @media (max-width: 340px) {
      .ws-row-name { flex: 0 0 40px; font-size: 9.5px; }
      .ws-sym { width: 37px; height: 37px; }
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
  <title>Infosec Archive · 세탁 라벨 읽기</title>
  <meta name="description" content="옷 케어라벨의 세탁 기호를 눌러 뜻과 주의할 점을 바로 보고, 실제 옷 라벨 6종으로 세탁법을 맞혀 보는 한 장 생활 도식. 국가기술표준원 KS K 0021:2024(2024-12-31 개정) 기준, ISO 3758:2023 대조.">
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
          <span>KS K 0021:2024 확인 2026-11-22</span>
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

  <main class="ws-wrap">
    <section class="ws-hero">
      <span class="ws-pill">생활 도식 · 세탁</span>
      <h1>세탁 라벨, 한 장으로 읽기</h1>
      <p>기호를 누르면 뜻과 주의할 점이 바로 열립니다. 마지막에는 실제 옷 라벨로 풀어 보세요.</p>
      <div class="ws-meta">
        <span>국가기술표준원 KS K 0021:2024</span>
        <span class="ws-sep"></span>
        <span>ISO 3758:2023 대조</span>
      </div>
    </section>

    <div class="ws-tabs" role="tablist" aria-label="보기 전환">
      <button type="button" class="ws-tab is-active" id="wsTabGuide" role="tab" aria-selected="true" aria-controls="wsPanelGuide" data-tab="guide">기호 도감</button>
      <button type="button" class="ws-tab" id="wsTabQuiz" role="tab" aria-selected="false" aria-controls="wsPanelQuiz" data-tab="quiz" tabindex="-1">라벨 읽기 퀴즈</button>
    </div>

    <section id="wsPanelGuide" role="tabpanel" aria-labelledby="wsTabGuide">
      <div class="ws-chips" role="group" aria-label="기호 분류">
        <button type="button" class="ws-chip is-active" data-cat="전체" aria-pressed="true">전체</button>
        <button type="button" class="ws-chip" data-cat="물세탁" aria-pressed="false">물세탁</button>
        <button type="button" class="ws-chip" data-cat="표백" aria-pressed="false">표백</button>
        <button type="button" class="ws-chip" data-cat="건조" aria-pressed="false">건조</button>
        <button type="button" class="ws-chip" data-cat="다림질·드라이" aria-pressed="false">다림질·드라이</button>
      </div>

      <div class="ws-guide-grid">
      <div class="ws-label" id="wsLabel" aria-label="가상 옷 케어라벨">
        <div class="ws-label-head">
          <span class="ws-label-title">CARE LABEL · 취급표시</span>
          <span class="ws-label-note">가상의 라벨 · 눌러서 뜻 보기</span>
        </div>
        __LABEL_ROWS__
      </div>

      <div class="ws-desc" id="wsDesc" aria-live="polite">
        <div class="ws-desc-art" id="wsDescArt" aria-hidden="true">__FIRST_SVG__</div>
        <div class="ws-desc-body">
          <span class="ws-desc-cat" id="wsDescCat">__FIRST_CAT__</span>
          <h2 class="ws-desc-name" id="wsDescName">__FIRST_NAME__</h2>
          <p class="ws-desc-meaning" id="wsDescMeaning">__FIRST_MEANING__</p>
          <p class="ws-desc-caution"><span class="ws-caution-tag">주의</span><span id="wsDescCaution">__FIRST_CAUTION__</span></p>
        </div>
      </div>

      </div>

      <p class="ws-foot">
        출처: 국가기술표준원 <a href="__STANDARD_URL__" target="_blank" rel="noopener noreferrer">KS K 0021:2024 섬유 제품의 취급에 관한 표시 기호 및 그 표시 방법</a> · 2024-12-31 개정(고시 제2024-0699호) · 국제 비교: GINETEX 케어 기호 안내(ISO 3758:2023) · 확인일 2026-11-22.
        실제 라벨은 보통 물세탁 → 표백 → 다림질 → 드라이클리닝 → 건조 순서로 놓여요.
        그림은 표준 도안을 복제하지 않고 뜻을 살려 단순하게 다시 그린 것으로, 실제 라벨과 굵기·모양이 조금 다를 수 있습니다. 표시가 없는 칸은 '아무거나 괜찮다'는 뜻이 아니에요.
      </p>
    </section>

    <section id="wsPanelQuiz" role="tabpanel" aria-labelledby="wsTabQuiz" hidden>
      <div class="ws-quiz-head">
        <span id="wsQuizProgress">1 / 6</span>
        <span>정답 <strong id="wsQuizScore">0</strong></span>
      </div>
      <div id="wsQuizBody">
        <div class="ws-quiz-grid">
        <article class="ws-garment">
          <div class="ws-garment-head">
            <h2 id="wsGarmentName"></h2>
            <span id="wsGarmentMeta"></span>
          </div>
          <div class="ws-qlabel" id="wsQuizLabel" aria-label="이 옷의 케어라벨 기호"></div>
          <p class="ws-ghint">라벨의 기호를 하나씩 읽고 답을 골라 보세요. 답을 고르면 근거가 된 기호가 파랗게 표시됩니다.</p>
        </article>
        <div class="ws-quiz-main">
        <p class="ws-question" id="wsQuestion"></p>
        <div class="ws-options" id="wsOptions" role="group" aria-label="보기"></div>
        <div class="ws-result" id="wsResult" hidden></div>
        <div class="ws-actions">
          <button type="button" class="ws-primary" id="wsNext" disabled>다음 옷</button>
        </div>
        </div>
        </div>
      </div>
      <div class="ws-summary" id="wsSummary" hidden>
        <h2>여섯 벌을 모두 봤어요</h2>
        <p>고른 답의 근거가 된 기호는 라벨에서 파랗게 표시됐어요. 기호 도감에서 다시 확인해 보세요.</p>
        <div class="ws-summary-score"><b id="wsSummaryNum">0</b><span id="wsSummaryTotal">/ 6</span></div>
        <div class="ws-actions">
          <button type="button" class="ws-primary" id="wsRestart">다시 풀기</button>
          <button type="button" class="ws-ghost" id="wsBackGuide">기호 도감으로</button>
        </div>
      </div>
    </section>
  </main>

  <script type="application/json" id="washData">__DATA_JSON__</script>
  <script>
const WASH = JSON.parse(document.getElementById('washData').textContent);
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

  const SYM = {};
  WASH.symbols.forEach(function (item) { SYM[item.id] = item; });
  const QUIZ = WASH.quizzes;
  const TOTAL = QUIZ.length;

  // ---------- 탭 ----------
  const tabs = Array.from(document.querySelectorAll('.ws-tab'));
  const panels = {
    guide: document.getElementById('wsPanelGuide'),
    quiz: document.getElementById('wsPanelQuiz'),
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
      const next = tab.getAttribute('data-tab') === 'guide' ? 'quiz' : 'guide';
      selectTab(next, true);
    });
  });

  // ---------- 기호 도감 ----------
  const symButtons = Array.from(document.querySelectorAll('.ws-sym'));
  const desc = {
    art: document.getElementById('wsDescArt'),
    cat: document.getElementById('wsDescCat'),
    name: document.getElementById('wsDescName'),
    meaning: document.getElementById('wsDescMeaning'),
    caution: document.getElementById('wsDescCaution'),
  };
  let currentSym = null;

  function showSymbol(id) {
    const item = SYM[id];
    if (!item) return;
    currentSym = id;
    symButtons.forEach(function (btn) {
      const on = btn.getAttribute('data-sym') === id;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    desc.art.innerHTML = item.svg;
    desc.cat.textContent = item.cat;
    desc.name.textContent = item.name;
    desc.meaning.textContent = item.meaning;
    desc.caution.textContent = item.caution;
  }

  symButtons.forEach(function (btn) {
    btn.addEventListener('click', function () { showSymbol(btn.getAttribute('data-sym')); });
  });
  if (symButtons.length) showSymbol(symButtons[0].getAttribute('data-sym'));

  // 카테고리 칩: 고른 분류의 줄만 남긴다.
  const chips = Array.from(document.querySelectorAll('.ws-chip'));
  const rows = Array.from(document.querySelectorAll('.ws-row'));
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      const cat = chip.getAttribute('data-cat');
      chips.forEach(function (other) {
        const on = other === chip;
        other.classList.toggle('is-active', on);
        other.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      rows.forEach(function (row) {
        row.hidden = cat !== '전체' && row.getAttribute('data-cat') !== cat;
      });
    });
  });

  // ---------- 라벨 읽기 퀴즈 ----------
  const els = {
    progress: document.getElementById('wsQuizProgress'),
    score: document.getElementById('wsQuizScore'),
    body: document.getElementById('wsQuizBody'),
    name: document.getElementById('wsGarmentName'),
    meta: document.getElementById('wsGarmentMeta'),
    label: document.getElementById('wsQuizLabel'),
    question: document.getElementById('wsQuestion'),
    options: document.getElementById('wsOptions'),
    result: document.getElementById('wsResult'),
    next: document.getElementById('wsNext'),
    summary: document.getElementById('wsSummary'),
    summaryNum: document.getElementById('wsSummaryNum'),
    restart: document.getElementById('wsRestart'),
    back: document.getElementById('wsBackGuide'),
  };

  let index = 0;
  let answered = false;
  let correctCount = 0;
  let answeredCount = 0;

  function evidenceNames(quiz) {
    return quiz.evidence.map(function (id) { return SYM[id] ? SYM[id].name : id; });
  }

  function renderQuiz() {
    const quiz = QUIZ[index];
    answered = false;
    els.body.hidden = false;
    els.summary.hidden = true;
    els.progress.textContent = (index + 1) + ' / ' + TOTAL;
    els.score.textContent = String(correctCount);
    els.name.textContent = quiz.garment;
    els.meta.textContent = quiz.material;
    els.label.innerHTML = quiz.symbols.map(function (id) {
      const item = SYM[id];
      return '<span class="ws-qsym" data-sym="' + id + '" aria-hidden="true">'
        + (item ? item.svg : '') + '</span>';
    }).join('');
    els.label.setAttribute('aria-label', quiz.garment + ' 라벨: '
      + quiz.symbols.map(function (id) { return SYM[id] ? SYM[id].name : id; }).join(', '));
    els.question.textContent = quiz.question;
    els.options.innerHTML = quiz.options.map(function (text, idx) {
      return '<button type="button" class="ws-opt" data-idx="' + idx + '">'
        + '<span class="ws-opt-num">' + (idx + 1) + '</span>'
        + '<span class="ws-opt-text">' + text + '</span></button>';
    }).join('');
    els.result.hidden = true;
    els.result.className = 'ws-result';
    els.result.innerHTML = '';
    els.next.disabled = true;
    els.next.textContent = index === TOTAL - 1 ? '결과 보기' : '다음 옷';
  }

  function markEvidence(quiz) {
    Array.from(els.label.querySelectorAll('.ws-qsym')).forEach(function (node) {
      const id = node.getAttribute('data-sym');
      node.classList.toggle('is-evidence', quiz.evidence.indexOf(id) >= 0);
    });
  }

  function showResult(quiz, ok) {
    const names = evidenceNames(quiz);
    els.result.className = 'ws-result' + (ok ? '' : ' is-no');
    els.result.innerHTML = ''
      + '<h3>' + (ok ? '정답이에요' : '라벨을 다시 보세요') + '</h3>'
      + '<p>' + quiz.explain + '</p>'
      + (ok ? '' : '<p>맞는 답: <b>' + quiz.options[quiz.answer] + '</b></p>')
      + '<div class="ws-evidence"><span class="ws-evidence-tag">근거 기호</span>'
      + names.map(function (name) {
        return '<span class="ws-evidence-item">' + name + '</span>';
      }).join('')
      + '</div>';
    els.result.hidden = false;
    markEvidence(quiz);
    els.next.disabled = false;
  }

  els.options.addEventListener('click', function (event) {
    const btn = event.target.closest('.ws-opt');
    if (!btn || answered) return;
    const quiz = QUIZ[index];
    const picked = Number(btn.getAttribute('data-idx'));
    const ok = picked === quiz.answer;
    answered = true;
    answeredCount += 1;
    if (ok) correctCount += 1;
    els.score.textContent = String(correctCount);
    Array.from(els.options.querySelectorAll('.ws-opt')).forEach(function (node) {
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
      els.progress.textContent = TOTAL + ' / ' + TOTAL;
      return;
    }
    index += 1;
    renderQuiz();
  });

  els.restart.addEventListener('click', function () {
    index = 0;
    correctCount = 0;
    answeredCount = 0;
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
    first = SYMBOLS[0]

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__LABEL_ROWS__", _label_rows())
            .replace("__FIRST_SVG__", first["svg"])
            .replace("__FIRST_CAT__", first["cat"])
            .replace("__FIRST_NAME__", first["name"])
            .replace("__FIRST_MEANING__", first["meaning"])
            .replace("__FIRST_CAUTION__", first["caution"])
            .replace("__STANDARD_URL__", STANDARD_URL)
            .replace("__DATA_JSON__", payload)
            .replace("__JS__", JS))

    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(WASH_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "wash")))

    print("-> 'wash_data.json' 저장 완료 (기호 %d개 · 옷 %d벌)" % (len(SYMBOLS), len(QUIZZES)))
    print("-> 'wash.html' 생성 완료 (기준 %s · 확인일 %s)" % (STANDARD, CHECKED_ON))
    return {
        "symbols": len(SYMBOLS),
        "quizzes": len(QUIZZES),
        "categories": len(CATEGORIES),
        "checkedOn": CHECKED_ON,
    }


if __name__ == "__main__":
    build()

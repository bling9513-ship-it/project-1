# -*- coding: utf-8 -*-
"""오늘의 카드(cards.html) — 인스타그램 카드뉴스 스타일 데일리 카드 덱 빌더.

구성
  · 덱 2개: `컨디션 키워드`(건강) · `1분 디지털 생활`(디지털 습관)
  · 덱마다 테마 4개 × 카드 3장 = 12장. KST 날짜로 테마를 하루씩 순환한다
    (index = 1970-01-01 부터 지난 날수 % 테마 수). 페이지는 로드 시점의 KST 날짜로
    같은 계산을 다시 해, 자정이 지나면 새 테마가 바로 열린다.
  · 카드 고정 포맷: 인라인 SVG 그림 → 핵심 한 줄 + 1~2줄 요약 → 오늘 해볼 한 가지 체크.
  · 건강 카드에는 공신력 있는 기관명·페이지 주제·확인일을 표기한다. 개인 건강정보를
    입력받는 필드는 두지 않는다(입력 요소 자체가 없다).
  · 저장(`daily_cards_saved_v1`)과 실천 체크(`daily_cards_done_v1`)는 localStorage 에만
    남기며, 읽을 때 카드 ID 화이트리스트로 걸러 화면에는 순수 텍스트로만 그린다.
"""
import json
import os
from datetime import date, datetime, timedelta, timezone

from html_guard import harden_html, safe_json_for_script
import ui_shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "cards_data.json")
CARDS_HTML = os.path.join(BASE_DIR, "cards.html")
KST = timezone(timedelta(hours=9))
CHECKED_ON = "2026-11-22"
EPOCH = date(1970, 1, 1)


def _source(org, topic, url):
    return {"org": org, "topic": topic, "checked": CHECKED_ON, "url": url}


KDCA = "질병관리청 국가건강정보포털"
ASAN = "서울아산병원 건강이야기"
OPHTH = "대한안과학회"
AAO = "미국안과학회(AAO)"
NCMH = "국립정신건강센터"
PIPC = "개인정보보호위원회"
KMCC = "방송미디어통신위원회"
GOOGLE = "Google 계정 고객센터"

# 카드별 원문 주소. 모두 실제로 열리는 페이지이며, 카드 문구의 근거 문장이 그 안에 있다.
KDCA_URL = ("https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/"
            "gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=")
URL_SLEEP = "https://www.mentalhealth.go.kr/portal/disease/diseaseDetail.do?dissId=32"
URL_20_20_20 = "https://www.aao.org/eye-health/tips-prevention/what-is-eye-strain"
URL_DRY_EYE_FAQ = "https://www.ophthalmology.org/content/reference/faq_list.html"
URL_DRY_EYE_ASAN = "https://www.amc.seoul.kr/asan/healthtv/video/videoDetail.do?videoId=334"
URL_FORWARD_HEAD = KDCA_URL + "5972"
URL_DEHYDRATION = KDCA_URL + "6551"
URL_COLD_WAVE = KDCA_URL + "2048"
URL_APP_PERMISSION = ("https://www.kmcc.go.kr/user.do?boardId=1099&boardSeq=44582&cp=1&dc=&mode=view"
                      "&page=A02030700")
URL_PUBLIC_WIFI = "https://m.blog.naver.com/pipcpr/223924781140"
URL_BACKUP_CODES = "https://support.google.com/accounts/answer/1187538?hl=ko"


def card(cid, headline, summary, action, art, source=None):
    item = {
        "id": cid,
        "headline": headline,
        "summary": summary,
        "action": action,
        "art": art,
    }
    if source:
        item["source"] = source
    return item


THEMES = {
    "condition": [
        {
            "id": "sleep",
            "title": "수면 리듬",
            "cards": [
                card("cond-sleep-1", "잠은 같은 시간에 시작",
                     "성인은 하루 7~8시간이 기준이에요. 주말에도 기상 시간을 크게 흔들지 않으면 리듬이 덜 깨집니다.",
                     "오늘 잠들 시간을 정해 알람 맞추기", "sleep-bed",
                     _source(NCMH, "수면과 수면장애", URL_SLEEP)),
                card("cond-sleep-2", "아침 햇빛 5분",
                     "일어난 뒤 창가에서 빛을 쬐면 몸의 시계가 낮을 알아차려요. 밤잠이 조금 더 규칙적으로 옵니다.",
                     "커튼 열고 창가에 5분 서 있기", "sleep-sun",
                     _source(NCMH, "수면과 수면장애", URL_SLEEP)),
                card("cond-sleep-3", "오후 커피는 한 잔 미루기",
                     "카페인은 몸에 오래 남아 잠드는 시간을 밀어내요. 늦은 오후 한 잔을 물이나 보리차로 바꿔 보세요.",
                     "오늘 오후 커피 한 잔을 물로 바꾸기", "sleep-cup",
                     _source(NCMH, "수면과 수면장애", URL_SLEEP)),
            ],
        },
        {
            "id": "eyes",
            "title": "20-20-20 눈 휴식",
            "cards": [
                card("cond-eyes-1", "20분 보면 20초 쉬기",
                     "화면을 20분 보면 6m 밖을 20초 동안 바라봐요. 눈의 조절근이 풀리고 깜빡임이 돌아옵니다.",
                     "지금 창밖 먼 곳을 20초 보기", "eyes-2020",
                     _source(AAO, "디지털 눈 피로와 20-20-20 규칙", URL_20_20_20)),
                card("cond-eyes-2", "1시간에 5~10분은 자리 비우기",
                     "컴퓨터 작업은 1시간에 5~10분 쉬는 편이 좋아요. 화면을 끄고 일어나면 눈과 목이 같이 쉽니다.",
                     "다음 정각에 일어나 5분 걷기", "eyes-break",
                     _source(OPHTH, "건성안 자주 묻는 질문", URL_DRY_EYE_FAQ)),
                card("cond-eyes-3", "눈 깜빡임 한 번 더",
                     "화면에 집중하면 깜빡임이 절반 이하로 줄어요. 의식적으로 한 번 더 깜빡이면 건조함이 덜해집니다.",
                     "지금부터 천천히 10번 깜빡이기", "eyes-blink",
                     _source(ASAN, "안구건조증", URL_DRY_EYE_ASAN)),
            ],
        },
        {
            "id": "neck",
            "title": "거북목·어깨",
            "cards": [
                card("cond-neck-1", "화면을 눈높이로",
                     "고개를 15도만 숙여도 목에 걸리는 무게가 12kg으로 늘어요. 모니터와 폰을 눈높이까지 올려 보세요.",
                     "모니터를 받침으로 5cm 올리기", "neck-height",
                     _source(KDCA, "일자목(거북목)증후군", URL_FORWARD_HEAD)),
                card("cond-neck-2", "30~40분마다 목 돌리기",
                     "같은 자세로 오래 있으면 목 뒤 근육이 굳어요. 30~40분마다 천천히 10회 돌려 주세요.",
                     "지금 목을 좌우로 10회 돌리기", "neck-turn",
                     _source(KDCA, "일자목(거북목)증후군", URL_FORWARD_HEAD)),
                card("cond-neck-3", "턱 당기기 20초",
                     "턱을 살짝 당겨 20~30초 유지하면 목 앞쪽 속근육이 깨어나요. 어깨 힘은 빼고 해요.",
                     "턱 당기기 20초를 세 번", "neck-chin",
                     _source(KDCA, "일자목(거북목)증후군", URL_FORWARD_HEAD)),
            ],
        },
        {
            "id": "winter",
            "title": "겨울 수분·습도",
            "cards": [
                card("cond-winter-1", "물은 나눠서 한 잔씩",
                     "필요한 물의 양은 활동량·환경·건강 상태에 따라 달라져요. 건강한 성인은 하루 1.5~2L를 한 시간에 한 잔씩 나눠 마시면 놓치지 않습니다.",
                     "책상에 물컵 두고 지금 한 모금", "winter-water",
                     _source(KDCA, "탈수", URL_DEHYDRATION)),
                card("cond-winter-2", "실내 습도 40~50%",
                     "난방을 켜면 실내가 금세 건조해져요. 습도 40~50%를 지키면 코와 목 점막이 덜 마릅니다.",
                     "가습기나 젖은 수건으로 습도 맞추기", "winter-humid",
                     _source(KDCA, "겨울철 한파대비 건강수칙", URL_COLD_WAVE)),
                card("cond-winter-3", "하루 세 번, 10분 환기",
                     "2~3시간 간격으로 하루 세 번, 10~30분 창문을 열어 환기해요. 맞바람이 나게 두 창을 함께 열면 좋아요.",
                     "오늘 세 번, 창문 열어 두기", "winter-air",
                     _source(KDCA, "겨울철 한파대비 건강수칙", URL_COLD_WAVE)),
            ],
        },
    ],
    "digital": [
        {
            "id": "permission",
            "title": "앱 권한 점검",
            "cards": [
                card("dig-perm-1", "위치는 쓸 때만",
                     "날씨나 지도가 아니면 늘 켜 둘 이유가 없어요. 앱별로 사용 중에만으로 바꾸면 동선이 덜 남습니다.",
                     "위치 권한이 항상인 앱 하나 바꾸기", "perm-location",
                     _source(KMCC, "스마트폰 앱 접근권한 개인정보보호 안내서", URL_APP_PERMISSION)),
                card("dig-perm-2", "사진은 고른 것만",
                     "사진첩 전체를 넘겨줄 필요는 없어요. 선택한 사진만 허용으로 바꾸면 필요한 것만 보입니다.",
                     "사진 권한이 모든 사진인 앱 점검", "perm-photo",
                     _source(KMCC, "스마트폰 앱 접근권한 개인정보보호 안내서", URL_APP_PERMISSION)),
                card("dig-perm-3", "마이크·카메라는 필요할 때만",
                     "권한이 켜져 있으면 앱이 뒤에서도 접근할 수 있어요. 안 쓰는 앱은 꺼 두면 마음이 놓입니다.",
                     "제어 센터에서 마이크·카메라 표시 확인", "perm-mic",
                     _source(KMCC, "스마트폰 앱 접근권한 개인정보보호 안내서", URL_APP_PERMISSION)),
            ],
        },
        {
            "id": "notify",
            "title": "알림 피로 줄이기",
            "cards": [
                card("dig-notify-1", "알림은 사람만 남기기",
                     "광고와 프로모션 알림을 끄면 진짜 연락이 눈에 들어와요. 앱마다 종류를 골라 끌 수 있습니다.",
                     "지난 하루 알림 중 광고 세 개 끄기", "notify-flood"),
                card("dig-notify-2", "잘 때는 방해 금지",
                     "자는 동안 알림을 막으면 깨지 않고 잠을 이어 갈 수 있어요. 급한 연락만 예외로 둘 수 있습니다.",
                     "취침 시간에 맞춰 방해 금지 예약", "notify-mute"),
                card("dig-notify-3", "일주일에 한 번 알림 점검",
                     "새로 깐 앱은 알림을 기본으로 켜 두는 경우가 많아요. 목록을 훑어 안 쓰는 것부터 끄세요.",
                     "설정에서 안 쓰는 앱 알림 두 개 끄기", "notify-list"),
            ],
        },
        {
            "id": "wifi",
            "title": "공용 와이파이",
            "cards": [
                card("dig-wifi-1", "자동 연결은 꺼 두기",
                     "이름이 같은 가짜 와이파이에 저절로 붙을 수 있어요. 자동 연결을 끄면 내가 고른 곳에만 붙습니다.",
                     "와이파이 설정에서 자동 연결 끄기", "wifi-auto",
                     _source(PIPC, "공용 와이파이, 얼마나 위험할까?", URL_PUBLIC_WIFI)),
                card("dig-wifi-2", "연결 경고와 주소 확인",
                     "브라우저가 '안전하지 않음'으로 표시하면 그 화면에서 로그인·결제는 피하세요. 접속한 사이트 주소가 맞는지도 함께 보세요.",
                     "지금 열린 탭의 주소 확인", "wifi-warn",
                     _source(PIPC, "공용 와이파이, 얼마나 위험할까?", URL_PUBLIC_WIFI)),
                card("dig-wifi-3", "결제는 통신사 망으로",
                     "카페 와이파이로 결제하면 중간에서 보일 수 있어요. 금융 작업만큼은 LTE나 5G로 바꿔 주세요.",
                     "결제 전 와이파이 잠시 끄기", "wifi-pay",
                     _source(PIPC, "공용 와이파이, 얼마나 위험할까?", URL_PUBLIC_WIFI)),
            ],
        },
        {
            "id": "backup",
            "title": "2단계 인증 백업 코드",
            "cards": [
                card("dig-backup-1", "백업 코드 10개 받아 두기",
                     "휴대폰을 잃어버려도 백업 코드가 있으면 로그인할 수 있어요. 구글은 10개짜리 세트를 발급합니다.",
                     "계정 보안 설정에서 백업 코드 받기", "backup-code",
                     _source(GOOGLE, "백업 코드로 로그인하기", URL_BACKUP_CODES)),
                card("dig-backup-2", "종이에 인쇄해 따로 보관",
                     "코드는 비밀번호처럼 다뤄요. 화면 캡처나 메모 앱보다 인쇄해 서류와 함께 두는 편이 안전합니다.",
                     "백업 코드를 인쇄해 서랍에 넣기", "backup-print",
                     _source(GOOGLE, "백업 코드로 로그인하기", URL_BACKUP_CODES)),
                card("dig-backup-3", "한 코드는 한 번만",
                     "한 번 쓴 코드는 바로 꺼져요. 다 썼다면 새 세트를 만들면 이전 코드는 자동으로 무효가 됩니다.",
                     "남은 코드 수 확인하고 새로 발급", "backup-once",
                     _source(GOOGLE, "백업 코드로 로그인하기", URL_BACKUP_CODES)),
            ],
        },
    ],
}

DECK_META = {
    "condition": ("컨디션 키워드", "몸의 리듬을 가볍게 맞추는 3장"),
    "digital": ("1분 디지털 생활", "오늘 바로 바꿀 수 있는 설정 3장"),
}


# ---------------------------------------------------------------- 인라인 SVG 그림
def _svg(inner):
    return (
        '<svg viewBox="0 0 320 168" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
        'focusable="false" role="presentation">'
        '<rect x="0" y="0" width="320" height="168" rx="18" fill="var(--art-plate)"/>'
        + inner
        + "</svg>"
    )


def _t(x, y, text, size=12, color="var(--art-muted)", weight="600", anchor="middle"):
    return ('<text x="%d" y="%d" font-size="%d" font-weight="%s" fill="%s" '
            'text-anchor="%s">%s</text>' % (x, y, size, weight, color, anchor, text))


ART = {
    # ---- 컨디션 · 수면 리듬
    "sleep-bed": _svg(
        '<rect x="196" y="18" width="92" height="62" rx="10" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<line x1="242" y1="18" x2="242" y2="80" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M266 30a13 13 0 1 0 0 26 17 17 0 0 1 0-26z" fill="var(--art-blue)"/>'
        + '<circle cx="272" cy="56" r="1.8" fill="var(--art-muted)"/>'
        + '<rect x="30" y="124" width="190" height="9" rx="4.5" fill="var(--art-ink)"/>'
        + '<rect x="38" y="98" width="164" height="28" rx="9" fill="var(--art-sky)"/>'
        + '<rect x="38" y="98" width="164" height="28" rx="9" fill="none" stroke="var(--art-blue)" stroke-width="2"/>'
        + '<rect x="50" y="84" width="48" height="18" rx="9" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M104 100h92v26h-92z" fill="var(--art-blue)" opacity="0.35"/>'
        + '<rect x="30" y="70" width="9" height="56" rx="4.5" fill="var(--art-ink)"/>'
        + '<circle cx="262" cy="126" r="18" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2"/>'
        + '<path d="M262 126v-9M262 126l7 4" stroke="var(--art-ink)" stroke-width="2" stroke-linecap="round"/>'
        + '<rect x="206" y="122" width="8" height="5" rx="1" fill="var(--art-ink)"/>'
        + '<rect x="216" y="120" width="8" height="7" rx="1" fill="var(--art-ink)"/>'
    ),
    "sleep-sun": _svg(
        '<rect x="196" y="18" width="92" height="66" rx="10" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<circle cx="242" cy="50" r="16" fill="var(--art-coral)"/>'
        + '<path d="M242 24v-6M242 82v-6M216 50h-6M274 50h-6M224 32l-4-4M264 72l4 4M260 32l4-4M220 72l-4 4" stroke="var(--art-coral)" stroke-width="2" stroke-linecap="round"/>'
        + '<path d="M196 18c12 10 12 56 0 66z" fill="var(--art-blue)" opacity="0.35"/>'
        + '<circle cx="118" cy="96" r="26" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="3"/>'
        + '<path d="M96 78l-10-8M96 114l-10 8M140 78l10-8M140 114l10 8" stroke="var(--art-ink)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M118 96v-12M118 96l9 6" stroke="var(--art-ink)" stroke-width="3" stroke-linecap="round"/>'
        + '<rect x="104" y="130" width="28" height="6" rx="3" fill="var(--art-ink)"/>'
    ),
    "sleep-cup": _svg(
        '<path d="M96 62h92v34a30 30 0 0 1-30 30h-32a30 30 0 0 1-30-30z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M188 72h12a16 16 0 0 1 0 32h-12" fill="none" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M108 70h68v24a22 22 0 0 1-22 22h-24a22 22 0 0 1-22-22z" fill="var(--art-coral)" opacity="0.28"/>'
        + '<path d="M122 46c-6-8 6-10 0-18M144 46c-6-8 6-10 0-18M166 46c-6-8 6-10 0-18" stroke="var(--art-muted)" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        + '<rect x="78" y="128" width="150" height="8" rx="4" fill="var(--art-ink)"/>'
        + '<circle cx="258" cy="98" r="20" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2"/>'
        + '<path d="M258 98V86M258 98l8 5" stroke="var(--art-ink)" stroke-width="2" stroke-linecap="round"/>'
        + '<circle cx="258" cy="40" r="17" fill="none" stroke="var(--art-coral)" stroke-width="3"/>'
        + '<path d="M248 30l20 20" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round"/>'
        + _t(258, 144, "오후 3시 이후", 10)
    ),
    # ---- 컨디션 · 20-20-20
    "eyes-2020": _svg(
        '<rect x="34" y="42" width="132" height="82" rx="9" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<rect x="44" y="52" width="112" height="62" rx="5" fill="var(--art-sky)"/>'
        + '<path d="M62 104l22-24 16 18 12-12 22 18z" fill="var(--art-blue)" opacity="0.55"/>'
        + '<rect x="88" y="124" width="24" height="10" fill="var(--art-ink)"/>'
        + '<rect x="66" y="134" width="68" height="7" rx="3.5" fill="var(--art-ink)"/>'
        + '<circle cx="244" cy="84" r="40" fill="none" stroke="var(--art-line)" stroke-width="8"/>'
        + '<path d="M244 44a40 40 0 0 1 34 61" fill="none" stroke="var(--art-blue)" stroke-width="8" stroke-linecap="round"/>'
        + _t(244, 78, "20분", 16, "var(--art-ink)", "700")
        + _t(244, 98, "→ 20초", 12, "var(--art-muted)")
        + '<circle cx="286" cy="132" r="4" fill="var(--art-coral)"/>'
        + '<circle cx="300" cy="132" r="4" fill="var(--art-line)"/>'
        + '<circle cx="272" cy="132" r="4" fill="var(--art-line)"/>'
    ),
    "eyes-break": _svg(
        '<rect x="28" y="34" width="118" height="76" rx="8" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<rect x="38" y="44" width="98" height="56" rx="4" fill="var(--art-mist)"/>'
        + '<path d="M60 86l18-20 14 16 10-10 18 14z" fill="var(--art-line)"/>'
        + '<rect x="26" y="110" width="122" height="7" rx="3.5" fill="var(--art-ink)"/>'
        + '<rect x="182" y="26" width="110" height="82" rx="10" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<circle cx="238" cy="52" r="13" fill="var(--art-coral)"/>'
        + '<circle cx="226" cy="88" r="13" fill="var(--art-blue)" opacity="0.6"/>'
        + '<circle cx="250" cy="100" r="16" fill="var(--art-sky)"/>'
        + '<path d="M182 26c10 12 10 70 0 82z" fill="var(--art-blue)" opacity="0.2"/>'
        + '<path d="M150 74h34" stroke="var(--art-blue)" stroke-width="2.5" stroke-dasharray="5 4" stroke-linecap="round"/>'
        + '<path d="M176 68l8 6-8 6" fill="none" stroke="var(--art-blue)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        + _t(108, 140, "1시간에 5~10분", 11)
    ),
    "eyes-blink": _svg(
        '<path d="M66 84c26-28 78-28 104 0-26 30-78 30-104 0z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M92 84c10-10 26-10 36 0" fill="none" stroke="var(--art-ink)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M84 92c-4 4-6 8-6 12M118 98v10M152 92c4 4 6 8 6 12" stroke="var(--art-ink)" stroke-width="2" stroke-linecap="round"/>'
        + '<circle cx="244" cy="84" r="38" fill="none" stroke="var(--art-line)" stroke-width="8"/>'
        + '<path d="M244 46a38 38 0 0 1 26 64" fill="none" stroke="var(--art-blue)" stroke-width="8" stroke-linecap="round"/>'
        + _t(244, 90, "20초", 17, "var(--art-ink)", "700")
    ),
    # ---- 컨디션 · 거북목
    "neck-height": _svg(
        '<rect x="26" y="88" width="84" height="54" rx="7" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<rect x="36" y="98" width="64" height="34" rx="4" fill="var(--art-mist)"/>'
        + '<rect x="34" y="142" width="90" height="6" rx="3" fill="var(--art-ink)"/>'
        + '<path d="M150 128c0-26 10-38 26-38 12 0 18 8 18 20 0 14-10 18-10 24z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M182 86c14 0 22 8 30 8" fill="none" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M164 60v64" stroke="var(--art-blue)" stroke-width="2" stroke-dasharray="5 4"/>'
        + '<path d="M158 68l6-8 6 8M158 116l6 8 6-8" fill="none" stroke="var(--art-blue)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        + '<path d="M226 128c0-30 8-44 26-44 14 0 22 10 22 22v22z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<circle cx="248" cy="62" r="16" fill="var(--art-sky)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M186 46h112" stroke="var(--art-coral)" stroke-width="2" stroke-dasharray="5 4"/>'
        + _t(242, 38, "눈높이", 11, "var(--art-coral)", "700")
    ),
    "neck-turn": _svg(
        '<circle cx="160" cy="52" r="18" fill="var(--art-sky)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M138 82c8-8 36-8 44 0l6 54h-56z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M142 96c-14 6-18 18-14 30M178 96c14 6 18 18 14 30" fill="none" stroke="var(--art-ink)" stroke-width="2.5" stroke-linecap="round"/>'
        + '<path d="M104 104a56 56 0 0 1 0 34" fill="none" stroke="var(--art-blue)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M98 136l6 10 10-6" fill="none" stroke="var(--art-blue)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        + '<path d="M216 104a56 56 0 0 0 0 34" fill="none" stroke="var(--art-blue)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M222 136l-6 10-10-6" fill="none" stroke="var(--art-blue)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        + _t(160, 163, "30~40분마다 좌우 10회", 9.5)
    ),
    "neck-chin": _svg(
        '<circle cx="146" cy="58" r="20" fill="var(--art-sky)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M122 92c10-10 38-10 48 0l8 52h-64z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M120 74h-26" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M136 58h-30" stroke="var(--art-blue)" stroke-width="2.5" stroke-dasharray="4 4"/>'
        + '<path d="M112 50l-8 8 8 8" fill="none" stroke="var(--art-blue)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        + '<circle cx="244" cy="86" r="38" fill="none" stroke="var(--art-line)" stroke-width="8"/>'
        + '<path d="M244 48a38 38 0 0 1 34 55" fill="none" stroke="var(--art-coral)" stroke-width="8" stroke-linecap="round"/>'
        + _t(244, 92, "20초", 17, "var(--art-ink)", "700")
        + _t(244, 110, "× 3", 12)
        + '<rect x="266" y="132" width="26" height="8" rx="4" fill="var(--art-line)"/>'
    ),
    # ---- 컨디션 · 겨울
    "winter-water": _svg(
        '<path d="M126 44h60l-7 78a14 14 0 0 1-14 13h-18a14 14 0 0 1-14-13z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M132 76h48l-5 46a14 14 0 0 1-14 13h-18a14 14 0 0 1-14-13z" fill="var(--art-blue)" opacity="0.45"/>'
        + '<path d="M126 44h60" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M142 26c-4-6 4-8 0-14M170 26c-4-6 4-8 0-14" stroke="var(--art-muted)" stroke-width="2" fill="none" stroke-linecap="round"/>'
        + '<circle cx="70" cy="60" r="10" fill="none" stroke="var(--art-blue)" stroke-width="2.5"/>'
        + '<circle cx="94" cy="60" r="10" fill="var(--art-blue)"/>'
        + '<circle cx="118" cy="60" r="10" fill="none" stroke="var(--art-blue)" stroke-width="2.5"/>'
        + '<circle cx="70" cy="88" r="10" fill="var(--art-blue)"/>'
        + '<circle cx="94" cy="88" r="10" fill="none" stroke="var(--art-blue)" stroke-width="2.5"/>'
        + '<circle cx="118" cy="88" r="10" fill="var(--art-blue)"/>'
        + '<circle cx="70" cy="116" r="10" fill="none" stroke="var(--art-blue)" stroke-width="2.5"/>'
        + '<circle cx="94" cy="116" r="10" fill="var(--art-blue)"/>'
        + _t(248, 76, "한 잔씩", 16, "var(--art-ink)", "700")
        + _t(248, 96, "한 시간마다", 11)
        + '<path d="M228 108h40" stroke="var(--art-line)" stroke-width="2" stroke-dasharray="4 4"/>'
        + _t(248, 126, "필요한 만큼", 11)
    ),
    "winter-humid": _svg(
        '<circle cx="112" cy="82" r="46" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="3"/>'
        + '<path d="M112 44a38 38 0 0 1 27 65" fill="none" stroke="var(--art-blue)" stroke-width="7" stroke-linecap="round"/>'
        + '<path d="M112 82l20-16" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round"/>'
        + '<circle cx="112" cy="82" r="4" fill="var(--art-ink)"/>'
        + _t(112, 150, "40~50%", 11, "var(--art-ink)", "700")
        + '<path d="M206 118c0-16 12-26 12-26s12 10 12 26a12 12 0 0 1-24 0z" fill="var(--art-sky)" stroke="var(--art-blue)" stroke-width="2.5"/>'
        + '<rect x="196" y="126" width="44" height="10" rx="5" fill="var(--art-ink)"/>'
        + '<path d="M240 64c6-6 12-6 18 0M246 82c5-4 9-4 14 0M234 100c4-3 8-3 12 0" stroke="var(--art-muted)" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        + _t(258, 142, "가습", 10)
    ),
    "winter-air": _svg(
        '<rect x="52" y="26" width="128" height="104" rx="8" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2.5"/>'
        + '<path d="M116 26v104" stroke="var(--art-line)" stroke-width="2.5"/>'
        + '<path d="M52 26l64 104M180 26l-64 104" stroke="var(--art-mist)" stroke-width="2"/>'
        + '<path d="M52 26l44-14 84 0 0 14z" fill="var(--art-sky)" opacity="0.6"/>'
        + '<path d="M196 62h44M196 84h58M196 106h38" stroke="var(--art-blue)" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        + '<path d="M232 56l8 6-8 6M246 78l8 6-8 6M226 100l8 6-8 6" fill="none" stroke="var(--art-blue)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        + '<rect x="26" y="140" width="272" height="6" rx="3" fill="var(--art-ink)"/>'
        + _t(112, 163, "하루 3번 · 10~30분", 9.5)
    ),
    # ---- 디지털 · 앱 권한
    "perm-location": _svg(
        '<rect x="34" y="26" width="148" height="112" rx="12" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M34 74h148M82 26v112M34 118h148" stroke="var(--art-mist)" stroke-width="2"/>'
        + '<path d="M108 52c12 0 21 9 21 20 0 15-21 36-21 36S87 87 87 72c0-11 9-20 21-20z" fill="var(--art-coral)"/>'
        + '<circle cx="108" cy="72" r="7" fill="var(--art-paper)"/>'
        + '<rect x="196" y="66" width="82" height="30" rx="15" fill="var(--art-mist)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<circle cx="212" cy="81" r="11" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2.5"/>'
        + '<rect x="228" y="74" width="38" height="14" rx="7" fill="var(--art-line)"/>'
        + _t(237, 118, "항상 → 사용할 때만", 10, "var(--art-muted)")
        + '<circle cx="64" cy="110" r="4" fill="var(--art-blue)"/>'
    ),
    "perm-photo": _svg(
        '<rect x="28" y="34" width="112" height="84" rx="8" fill="var(--art-sky)" stroke="var(--art-blue)" stroke-width="2" transform="rotate(-8 84 76)"/>'
        + '<rect x="42" y="40" width="112" height="84" rx="8" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<rect x="52" y="50" width="92" height="58" rx="4" fill="var(--art-mist)"/>'
        + '<circle cx="78" cy="68" r="8" fill="var(--art-coral)"/>'
        + '<path d="M52 108l28-30 20 22 14-14 30 22z" fill="var(--art-blue)" opacity="0.5"/>'
        + '<rect x="196" y="64" width="56" height="44" rx="9" fill="var(--art-blue)"/>'
        + '<path d="M208 64v-9a16 16 0 0 1 32 0v9" fill="none" stroke="var(--art-ink)" stroke-width="4"/>'
        + '<circle cx="224" cy="84" r="6" fill="var(--art-paper)"/>'
        + '<path d="M224 84v10" stroke="var(--art-paper)" stroke-width="4" stroke-linecap="round"/>'
        + _t(224, 134, "고른 사진만", 11)
    ),
    "perm-mic": _svg(
        '<rect x="52" y="40" width="26" height="52" rx="13" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M38 74a27 27 0 0 0 54 0M65 101v16M50 120h30" fill="none" stroke="var(--art-ink)" stroke-width="2.5" stroke-linecap="round"/>'
        + '<rect x="150" y="58" width="54" height="38" rx="8" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M204 68l26-10v38l-26-10z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<circle cx="177" cy="77" r="8" fill="var(--art-sky)"/>'
        + '<circle cx="258" cy="122" r="18" fill="var(--art-coral)"/>'
        + '<path d="M250 122h16" stroke="var(--art-paper)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M96 44l72 84" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round" opacity="0.8"/>'
        + _t(92, 148, "필요할 때만 켜 두기", 11)
    ),
    # ---- 디지털 · 알림
    "notify-flood": _svg(
        '<rect x="104" y="20" width="76" height="128" rx="14" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<rect x="112" y="34" width="60" height="96" rx="6" fill="var(--art-mist)"/>'
        + '<rect x="130" y="136" width="24" height="5" rx="2.5" fill="var(--art-ink)"/>'
        + '<circle cx="126" cy="52" r="9" fill="var(--art-coral)"/>'
        + '<circle cx="158" cy="72" r="9" fill="var(--art-coral)"/>'
        + '<circle cx="126" cy="92" r="9" fill="var(--art-coral)"/>'
        + '<circle cx="158" cy="112" r="9" fill="var(--art-coral)"/>'
        + '<path d="M78 40c-8 4-10 10-8 16M226 40c8 4 10 10 8 16M70 96c-8 4-10 10-8 16M234 96c8 4 10 10 8 16" stroke="var(--art-line)" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        + _t(160, 162, "알림이 몰려오는 하루", 9)
    ),
    "notify-mute": _svg(
        '<path d="M212 40a34 34 0 1 0 0 56 42 42 0 0 1 0-56z" fill="var(--art-sky)" stroke="var(--art-blue)" stroke-width="2.5"/>'
        + '<path d="M96 56c0-10 8-18 18-18s18 8 18 18v18l10 12H68l10-12z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M104 104a10 10 0 0 0 20 0" fill="none" stroke="var(--art-ink)" stroke-width="2.5" stroke-linecap="round"/>'
        + '<path d="M76 44l76 66" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M244 116c0-8 6-12 10-16 4 4 10 8 10 16a10 10 0 0 1-20 0z" fill="var(--art-blue)" opacity="0.5"/>'
        + _t(114, 140, "방해 금지", 11)
        + _t(160, 162, "자는 동안은 조용히", 9)
    ),
    "notify-list": _svg(
        '<rect x="40" y="26" width="176" height="116" rx="12" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<circle cx="64" cy="56" r="9" fill="var(--art-mist)"/>'
        + '<path d="M82 50h54M82 62h34" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<rect x="166" y="48" width="34" height="16" rx="8" fill="var(--art-mist)"/>'
        + '<circle cx="174" cy="56" r="6" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<circle cx="64" cy="86" r="9" fill="var(--art-mist)"/>'
        + '<path d="M82 80h44M82 92h30" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<rect x="166" y="78" width="34" height="16" rx="8" fill="var(--art-blue)"/>'
        + '<circle cx="192" cy="86" r="6" fill="var(--art-paper)"/>'
        + '<circle cx="64" cy="116" r="9" fill="var(--art-mist)"/>'
        + '<path d="M82 110h50M82 122h26" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<rect x="166" y="108" width="34" height="16" rx="8" fill="var(--art-mist)"/>'
        + '<circle cx="174" cy="116" r="6" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M238 62h34M238 86h34M238 110h34" stroke="var(--art-mist)" stroke-width="3" stroke-linecap="round"/>'
        + _t(160, 158, "안 쓰는 앱부터 끄기", 9)
    ),
    # ---- 디지털 · 공용 와이파이
    "wifi-auto": _svg(
        '<path d="M74 74a58 58 0 0 1 76 0" fill="none" stroke="var(--art-ink)" stroke-width="3.5" stroke-linecap="round"/>'
        + '<path d="M90 92a34 34 0 0 1 44 0" fill="none" stroke="var(--art-ink)" stroke-width="3.5" stroke-linecap="round"/>'
        + '<circle cx="112" cy="110" r="5" fill="var(--art-ink)"/>'
        + '<rect x="186" y="66" width="88" height="32" rx="16" fill="var(--art-mist)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<circle cx="203" cy="82" r="12" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2.5"/>'
        + '<rect x="218" y="75" width="42" height="14" rx="7" fill="var(--art-line)"/>'
        + _t(112, 140, "자동 연결 끄기", 11)
        + _t(230, 122, "내가 고른 곳에만", 9, "var(--art-coral)")
    ),
    "wifi-warn": _svg(
        '<rect x="24" y="26" width="272" height="34" rx="17" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M44 38l9 15H35z" fill="var(--art-coral)"/>'
        + '<path d="M44 43v5" stroke="var(--art-paper)" stroke-width="2" stroke-linecap="round"/>'
        + '<circle cx="44" cy="51" r="1.2" fill="var(--art-paper)"/>'
        + '<text x="62" y="49" font-size="10" font-weight="600" fill="var(--art-ink)">shop.example.com</text>'
        + '<rect x="196" y="35" width="88" height="16" rx="8" fill="var(--art-coral)"/>'
        + '<text x="240" y="46.5" font-size="8.5" font-weight="700" fill="var(--art-paper)" text-anchor="middle">안전하지 않음</text>'
        + '<rect x="30" y="84" width="118" height="30" rx="8" fill="var(--art-paper)" stroke="var(--art-blue)" stroke-width="2"/>'
        + '<text x="89" y="103" font-size="9" font-weight="700" fill="var(--art-ink)" text-anchor="middle">bank.example.com</text>'
        + '<rect x="172" y="84" width="118" height="30" rx="8" fill="var(--art-paper)" stroke="var(--art-coral)" stroke-width="2"/>'
        + '<text x="231" y="103" font-size="9" font-weight="700" fill="var(--art-coral)" text-anchor="middle">bank-example.com</text>'
        + '<path d="M152 99h14" stroke="var(--art-muted)" stroke-width="2" stroke-dasharray="4 3"/>'
        + _t(89, 128, "원래 주소", 9)
        + _t(231, 128, "비슷한 다른 주소", 9, "var(--art-coral)")
        + '<path d="M96 134h128" stroke="var(--art-line)" stroke-width="2" stroke-dasharray="5 4"/>'
        + _t(160, 152, "경고가 뜨면 로그인·결제 멈추기", 10, "var(--art-ink)", "600")
    ),
    "wifi-pay": _svg(
        '<rect x="38" y="26" width="72" height="116" rx="12" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M52 116v-8M64 116v-16M76 116v-24M88 116v-32" stroke="var(--art-blue)" stroke-width="4" stroke-linecap="round"/>'
        + _t(74, 136, "LTE · 5G", 9)
        + '<rect x="150" y="54" width="96" height="60" rx="10" fill="var(--art-blue)"/>'
        + '<rect x="162" y="66" width="26" height="18" rx="4" fill="var(--art-coral)"/>'
        + '<path d="M150 98h96" stroke="var(--art-paper)" stroke-width="3"/>'
        + '<path d="M196 34c8 8 20 8 28 0" fill="none" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M202 44c4 4 12 4 16 0" fill="none" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M184 26l44 44" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round"/>'
        + _t(198, 136, "결제는 통신사 망으로", 10)
        + '<circle cx="268" cy="120" r="16" fill="var(--art-coral)"/>'
        + '<path d="M262 120l4 5 8-9" fill="none" stroke="var(--art-paper)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
    # ---- 디지털 · 백업 코드
    "backup-code": _svg(
        '<rect x="70" y="24" width="136" height="120" rx="10" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M206 24v22h-22" fill="var(--art-mist)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M84 44h58M84 58h40" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M84 80h50M146 80h40M84 94h42M138 94h48M84 108h56M152 108h34M84 122h44M140 122h46" stroke="var(--art-ink)" stroke-width="3" stroke-linecap="round" opacity="0.55"/>'
        + '<circle cx="250" cy="102" r="24" fill="var(--art-blue)"/>'
        + '<path d="M250 92v14M250 114h0.1" stroke="var(--art-paper)" stroke-width="3.5" stroke-linecap="round"/>'
        + _t(250, 146, "10개", 11)
    ),
    "backup-print": _svg(
        '<rect x="52" y="34" width="92" height="76" rx="6" fill="var(--art-paper)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M64 50h60M64 62h44M64 74h52M64 86h38" stroke="var(--art-ink)" stroke-width="3" stroke-linecap="round" opacity="0.45"/>'
        + '<rect x="86" y="112" width="120" height="34" rx="6" fill="var(--art-mist)" stroke="var(--art-line)" stroke-width="2"/>'
        + '<path d="M100 124h92M100 136h60" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M160 34v64" stroke="var(--art-blue)" stroke-width="2.5" stroke-dasharray="5 4"/>'
        + '<path d="M152 90l8 10 8-10" fill="none" stroke="var(--art-blue)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        + '<rect x="196" y="52" width="70" height="46" rx="8" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<circle cx="231" cy="75" r="11" fill="none" stroke="var(--art-blue)" stroke-width="2.5"/>'
        + '<path d="M231 64v22M220 75h22" stroke="var(--art-blue)" stroke-width="2"/>'
        + _t(160, 158, "인쇄해 서류와 함께", 10)
    ),
    "backup-once": _svg(
        '<path d="M60 44h130a12 12 0 0 1 12 12v56a12 12 0 0 1-12 12H60a12 12 0 0 1-12-12V56a12 12 0 0 1 12-12z" fill="var(--art-paper)" stroke="var(--art-ink)" stroke-width="2.5"/>'
        + '<path d="M64 60v48" stroke="var(--art-line)" stroke-width="2" stroke-dasharray="4 4"/>'
        + '<path d="M84 70h56M84 84h40M84 98h48" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M150 70h26M150 84h18" stroke="var(--art-line)" stroke-width="3" stroke-linecap="round"/>'
        + '<circle cx="232" cy="92" r="30" fill="var(--art-blue)"/>'
        + '<path d="M218 92l10 11 19-21" fill="none" stroke="var(--art-paper)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
        + '<path d="M196 40l30 30" stroke="var(--art-coral)" stroke-width="3" stroke-linecap="round"/>'
        + '<circle cx="182" cy="120" r="16" fill="none" stroke="var(--art-coral)" stroke-width="2.5"/>'
        + '<path d="M174 112l16 16" stroke="var(--art-coral)" stroke-width="2.5" stroke-linecap="round"/>'
        + _t(232, 142, "한 번만 사용", 10)
    ),
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

      --art-ink: #0f172a;
      --art-blue: #3182f6;
      --art-sky: #dbeafe;
      --art-coral: #ff6b57;
      --art-coral-soft: #ffe4de;
      --art-line: #cbd5e1;
      --art-paper: #ffffff;
      --art-plate: #f3f6fb;
      --art-mist: #e8eef6;
      --art-muted: #8794a7;

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

      --art-ink: #e5e7eb;
      --art-blue: #4f9cf9;
      --art-sky: rgba(79, 156, 249, 0.24);
      --art-coral: #ff8b78;
      --art-coral-soft: rgba(255, 139, 120, 0.2);
      --art-line: #414148;
      --art-paper: #212127;
      --art-plate: #101014;
      --art-mist: #26262c;
      --art-muted: #8b8b96;

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

    .cd-wrap { max-width: 660px; margin: 0 auto; padding: 22px 20px 84px; }

    .cd-hero { margin-bottom: 12px; }
    .cd-pill {
      display: inline-block;
      font-size: 11px; font-weight: 600; letter-spacing: 0.01em;
      color: var(--accent-primary); background: var(--accent-subtle);
      border: 1px solid var(--border-default); border-radius: 6px;
      padding: 3px 8px; margin-bottom: 8px;
    }
    .cd-hero h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.04em; }
    .cd-hero p { margin-top: 5px; font-size: 12.5px; color: var(--text-secondary); }
    .cd-meta { display: flex; align-items: center; gap: 7px; margin-top: 7px; font-size: 11px; color: var(--text-muted); }
    .cd-meta strong { font-weight: 700; color: var(--text-secondary); font-variant-numeric: tabular-nums; }
    .cd-meta .cd-dot-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); }

    .cd-decks { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 3px; padding: 3px; background: var(--bg-subtle); border-radius: 12px; margin-bottom: 12px; }
    .cd-deck {
      border: 0; background: transparent; border-radius: 9px; padding: 9px 3px; min-width: 0;
      font-family: inherit; font-size: 12px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary); cursor: pointer; white-space: nowrap; overflow: hidden;
      display: inline-flex; align-items: center; justify-content: center; gap: 5px;
      transition: background-color 160ms ease, color 160ms ease;
    }
    .cd-deck:hover { color: var(--text-primary); }
    .cd-deck.is-active { background: var(--bg-surface); color: var(--text-primary); box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }
    .cd-count {
      display: inline-flex; align-items: center; justify-content: center;
      min-width: 16px; height: 16px; padding: 0 4px; border-radius: 999px;
      background: var(--bg-muted); color: var(--text-secondary);
      font-size: 9.5px; font-weight: 700; font-variant-numeric: tabular-nums;
    }
    .cd-deck.is-active .cd-count { background: var(--accent-subtle); color: var(--accent-primary); }

    .cd-card {
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 18px; padding: 14px; box-shadow: var(--card-shadow);
      min-width: 0; touch-action: pan-y; will-change: transform;
    }
    .cd-card.is-enter { animation: cdEnter 220ms ease; }
    .cd-card.is-dragging { transition: none; }
    .cd-card-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .cd-theme { font-size: 10.5px; font-weight: 700; letter-spacing: 0.01em; color: var(--accent-primary); }
    .cd-index { font-size: 10.5px; font-weight: 600; color: var(--text-muted); font-variant-numeric: tabular-nums; white-space: nowrap; }

    .cd-art { margin-top: 9px; height: 176px; border-radius: 14px; overflow: hidden; background: var(--art-plate); }
    .cd-art svg { display: block; width: 100%; height: 100%; }
    .cd-art text { font-family: inherit; }

    .cd-headline { margin-top: 13px; font-size: 19px; font-weight: 800; letter-spacing: -0.045em; line-height: 1.3; }
    .cd-summary { margin-top: 6px; font-size: 12.5px; line-height: 1.55; color: var(--text-secondary); }

    .cd-action {
      margin-top: 12px; padding: 10px 11px; border-radius: 12px;
      background: var(--bg-subtle); border: 1px solid var(--border-subtle);
      display: flex; align-items: center; justify-content: space-between; gap: 10px;
    }
    .cd-action-text { min-width: 0; }
    .cd-action-label { display: block; font-size: 9.5px; font-weight: 700; letter-spacing: 0.03em; color: var(--text-muted); }
    .cd-action-text p { margin-top: 2px; font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em; }
    .cd-check {
      flex-shrink: 0; display: inline-flex; align-items: center; gap: 5px;
      border: 1px solid var(--border-default); background: var(--bg-surface);
      border-radius: 999px; padding: 7px 10px; cursor: pointer;
      font-family: inherit; font-size: 11px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary); white-space: nowrap;
      transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
    }
    .cd-check svg { width: 13px; height: 13px; }
    .cd-check:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .cd-check.is-done { background: var(--ok-bg); border-color: var(--ok-border); color: var(--ok-text); }

    .cd-foot { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; margin-top: 10px; }
    .cd-source { flex: 1; min-width: 0; font-size: 9.5px; line-height: 1.6; color: var(--text-muted); }
    .cd-source a.cd-source-link { color: var(--accent-primary); font-weight: 700; text-decoration: underline; text-underline-offset: 2px; white-space: nowrap; }
    .cd-source a.cd-source-link:hover { color: var(--accent-hover); }
    .cd-save {
      flex-shrink: 0; display: inline-flex; align-items: center; gap: 5px;
      border: 1px solid var(--border-default); background: var(--bg-surface);
      border-radius: 8px; padding: 6px 9px; cursor: pointer;
      font-family: inherit; font-size: 11px; font-weight: 600; letter-spacing: -0.02em;
      color: var(--text-secondary);
      transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
    }
    .cd-save svg { width: 13px; height: 13px; }
    .cd-save:hover { border-color: var(--border-strong); color: var(--text-primary); }
    .cd-save.is-saved { background: var(--accent-subtle); border-color: var(--border-strong); color: var(--accent-primary); }

    .cd-controls { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 11px; }
    .cd-nav {
      flex: 0 0 92px; height: 40px; border-radius: 10px; border: 1px solid var(--border-default);
      background: var(--bg-surface); color: var(--text-secondary);
      font-family: inherit; font-size: 12.5px; font-weight: 600; letter-spacing: -0.02em;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 5px;
      transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
    }
    .cd-nav:hover { background: var(--bg-subtle); color: var(--text-primary); border-color: var(--border-strong); }
    .cd-nav svg { width: 14px; height: 14px; }
    .cd-dots { display: flex; align-items: center; justify-content: center; gap: 6px; }
    .cd-dot { width: 7px; height: 7px; padding: 0; border: 0; border-radius: 999px; background: var(--bg-muted); cursor: pointer; transition: width 160ms ease, background-color 160ms ease; }
    .cd-dot:hover { background: var(--border-strong); }
    .cd-dot.is-active { width: 20px; background: var(--accent-primary); }

    .cd-hint { margin-top: 9px; text-align: center; font-size: 10px; color: var(--text-muted); }
    .cd-hint kbd { font-family: inherit; font-weight: 600; color: var(--text-secondary); }

    .cd-savedlist { display: flex; flex-direction: column; gap: 9px; }
    .cd-alllist { display: flex; flex-direction: column; gap: 16px; }
    .cd-allgroup { display: flex; flex-direction: column; gap: 7px; }
    .cd-allgroup-head { display: flex; align-items: baseline; gap: 7px; padding: 0 2px; }
    .cd-allgroup-deck { font-size: 12px; font-weight: 800; letter-spacing: -0.03em; }
    .cd-allgroup-theme { font-size: 10.5px; font-weight: 700; color: var(--accent-primary); }
    .cd-allgroup-count { margin-left: auto; font-size: 9.5px; font-weight: 600; color: var(--text-muted); font-variant-numeric: tabular-nums; }
    .cd-allrow {
      display: flex; flex-direction: column;
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 12px; overflow: hidden;
      transition: border-color 150ms ease, background-color 150ms ease;
    }
    .cd-allrow:hover { border-color: var(--border-strong); }
    .cd-allrow-open {
      display: flex; gap: 10px; align-items: flex-start; width: 100%; text-align: left;
      background: transparent; border: 0; padding: 9px 10px 0; cursor: pointer;
      font-family: inherit; color: inherit;
    }
    .cd-allrow-open:hover .cd-allrow-title { color: var(--accent-primary); }
    .cd-allrow-art { display: block; flex: 0 0 56px; height: 42px; border-radius: 8px; overflow: hidden; background: var(--art-plate); }
    .cd-allrow-art svg { display: block; width: 100%; height: 100%; }
    .cd-allrow-body { display: block; flex: 1; min-width: 0; }
    .cd-allrow-title { display: block; font-size: 12.5px; font-weight: 700; letter-spacing: -0.03em; }
    .cd-allrow-summary { display: block; margin-top: 2px; font-size: 10.5px; line-height: 1.45; color: var(--text-secondary); }
    .cd-allrow-src { display: block; margin: 4px 0 0; padding: 0 10px 9px; font-size: 9px; line-height: 1.55; color: var(--text-muted); }
    .cd-allrow-src a.cd-source-link { color: var(--accent-primary); font-weight: 700; text-decoration: underline; text-underline-offset: 2px; }
    .cd-savedrow {
      display: flex; gap: 10px; align-items: flex-start;
      background: var(--bg-surface); border: 1px solid var(--border-default);
      border-radius: 14px; padding: 11px; box-shadow: var(--card-shadow);
    }
    .cd-savedrow-art { flex: 0 0 64px; height: 48px; border-radius: 9px; overflow: hidden; background: var(--art-plate); }
    .cd-savedrow-art svg { display: block; width: 100%; height: 100%; }
    .cd-savedrow-body { flex: 1; min-width: 0; }
    .cd-savedrow-meta { font-size: 9.5px; font-weight: 700; color: var(--accent-primary); }
    .cd-savedrow h3 { margin-top: 2px; font-size: 13.5px; font-weight: 700; letter-spacing: -0.03em; }
    .cd-savedrow-summary { margin-top: 3px; font-size: 11.5px; line-height: 1.5; color: var(--text-secondary); }
    .cd-savedrow-action { margin-top: 4px; font-size: 10.5px; font-weight: 600; color: var(--text-secondary); }
    .cd-saved-remove {
      flex-shrink: 0; border: 1px solid var(--border-default); background: var(--bg-surface);
      border-radius: 8px; padding: 5px 8px; cursor: pointer;
      font-family: inherit; font-size: 10.5px; font-weight: 600; color: var(--text-muted);
    }
    .cd-saved-remove:hover { color: var(--no-text); border-color: var(--no-border); background: var(--no-bg); }
    .cd-empty {
      text-align: center; padding: 34px 18px; border: 1px dashed var(--border-default);
      border-radius: 14px; background: var(--bg-surface);
    }
    .cd-empty strong { display: block; font-size: 13.5px; font-weight: 700; }
    .cd-empty p { margin-top: 5px; font-size: 11.5px; color: var(--text-muted); }

    @keyframes cdEnter {
      from { opacity: 0.3; transform: translateY(6px); }
      to { opacity: 1; transform: none; }
    }

    @media (max-width: 768px) {
      .cd-wrap { padding: 14px 14px 84px; }
      .cd-hero h1 { font-size: 20px; }
      .cd-hero p { font-size: 12px; }
      .cd-art { height: 168px; }
    }

    @media (max-width: 560px) {
      .cd-decks { grid-template-columns: 1fr 1fr; }
    }

    @media (max-width: 420px) {
      .cd-wrap { padding: 12px 12px 84px; }
      .cd-hero { margin-bottom: 10px; }
      .cd-pill { margin-bottom: 6px; }
      .cd-hero h1 { font-size: 19px; }
      .cd-hero p { margin-top: 4px; font-size: 11.5px; line-height: 1.45; }
      .cd-meta { margin-top: 6px; font-size: 10.5px; }
      .cd-decks { margin-bottom: 10px; }
      .cd-deck { font-size: 11.5px; padding: 8px 2px; }
      .cd-card { padding: 11px; border-radius: 16px; }
      .cd-art { height: 150px; margin-top: 8px; }
      .cd-headline { margin-top: 10px; font-size: 18px; }
      .cd-summary { margin-top: 5px; font-size: 12px; line-height: 1.5; }
      .cd-action { margin-top: 9px; padding: 9px 10px; }
      .cd-action-text p { font-size: 12px; }
      .cd-check { font-size: 10.5px; padding: 6px 8px; }
      .cd-foot { margin-top: 8px; }
      .cd-source { font-size: 9px; }
      .cd-controls { margin-top: 9px; }
      .cd-nav { flex: 1; height: 40px; }
      .cd-hint { display: none; }
    }

    @media (max-width: 360px) {
      .cd-wrap { padding: 10px 10px 84px; }
      .cd-deck { font-size: 10.5px; }
      .cd-art { height: 136px; }
      .cd-headline { font-size: 17px; }
      .cd-summary { font-size: 11.5px; }
    }

    @media (prefers-reduced-motion: reduce) {
      .cd-card.is-enter { animation: none !important; }
      .cd-card, .cd-dot, .cd-deck, .cd-nav, .cd-check, .cd-save { transition: none !important; }
    }
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Infosec Archive · 오늘의 카드</title>
  <meta name="description" content="인스타그램 카드뉴스처럼 넘겨 보는 데일리 카드. 컨디션 키워드와 1분 디지털 생활을 3장씩, 그림과 한 줄로 읽고 오늘 해볼 한 가지를 체크합니다.">
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
          <span>매일 KST 00:00 새 카드</span>
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

  <main class="cd-wrap">
    <section class="cd-hero">
      <span class="cd-pill">오늘의 카드 · 데일리</span>
      <h1>하루 3장, 한 가지만 해보세요</h1>
      <p>넘겨 보며 읽고, 마음에 드는 장은 저장해 두세요. '전체 카드'에서 24장을 테마별로 모두 볼 수 있습니다.</p>
      <div class="cd-meta">
        <span id="cdDate">오늘</span>
        <span class="cd-dot-sep"></span>
        <span id="cdDoneMeter">오늘 실천 <strong>0/3</strong></span>
      </div>
    </section>

    <div class="cd-decks" role="tablist" aria-label="카드 묶음">
      <button type="button" class="cd-deck is-active" id="cdDeckCondition" role="tab" aria-selected="true" data-deck="condition">컨디션 키워드</button>
      <button type="button" class="cd-deck" id="cdDeckDigital" role="tab" aria-selected="false" data-deck="digital">1분 디지털 생활</button>
      <button type="button" class="cd-deck" id="cdDeckAll" role="tab" aria-selected="false" data-deck="all">전체 카드</button>
      <button type="button" class="cd-deck" id="cdDeckSaved" role="tab" aria-selected="false" data-deck="saved">저장한 카드 <span class="cd-count" id="cdSavedCount">0</span></button>
    </div>

    <section id="cdPanel" aria-live="polite">
      <article class="cd-card" id="cdCard" aria-labelledby="cdHeadline">
        <header class="cd-card-top">
          <span class="cd-theme" id="cdTheme">오늘의 테마</span>
          <span class="cd-index" id="cdIndex">1 / 3</span>
        </header>
        <div class="cd-art" id="cdArt" aria-hidden="true"></div>
        <h2 class="cd-headline" id="cdHeadline"></h2>
        <p class="cd-summary" id="cdSummary"></p>
        <div class="cd-action">
          <div class="cd-action-text">
            <span class="cd-action-label">오늘 해볼 한 가지</span>
            <p id="cdActionText"></p>
          </div>
          <button type="button" class="cd-check" id="cdDoneBtn" aria-pressed="false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6L9 17l-5-5"></path></svg>
            <span id="cdDoneLabel">실천 체크</span>
          </button>
        </div>
        <div class="cd-foot">
          <p class="cd-source" id="cdSource"></p>
          <button type="button" class="cd-save" id="cdSaveBtn" aria-pressed="false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
            <span id="cdSaveLabel">저장</span>
          </button>
        </div>
      </article>
      <div class="cd-savedlist" id="cdSavedList" hidden></div>
      <div class="cd-alllist" id="cdAllList" hidden></div>
    </section>

    <div class="cd-controls" id="cdControls">
      <button type="button" class="cd-nav" id="cdPrev">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"></path></svg>
        이전
      </button>
      <div class="cd-dots" id="cdDots" role="tablist" aria-label="카드 위치"></div>
      <button type="button" class="cd-nav" id="cdNext">
        다음
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"></path></svg>
      </button>
    </div>
    <p class="cd-hint">좌우로 넘기거나 <kbd>←</kbd> <kbd>→</kbd> 키로도 볼 수 있어요. 저장과 실천 기록은 이 브라우저에만 남습니다.</p>
  </main>

  <script type="application/json" id="cardsData">__DATA_JSON__</script>
  <script>
const CD_ART = __ART_JSON__;
const CD_DATA = JSON.parse(document.getElementById('cardsData').textContent);
__JS__
  </script>
</body>
</html>
"""


JS = r"""
(function () {
  const SAVED_KEY = 'daily_cards_saved_v1';
  const DONE_KEY = 'daily_cards_done_v1';
  const REDUCE = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const WEEK = ['일', '월', '화', '수', '목', '금', '토'];

  const ITEMS = [];
  const BY_ID = {};
  CD_DATA.decks.forEach(function (deck) {
    deck.themes.forEach(function (theme) {
      theme.cards.forEach(function (raw) {
        const item = {
          id: raw.id,
          headline: raw.headline,
          summary: raw.summary,
          action: raw.action,
          art: raw.art,
          source: raw.source || null,
          deckId: deck.id,
          deckTitle: deck.title,
          themeId: theme.id,
          themeTitle: theme.title
        };
        ITEMS.push(item);
        BY_ID[item.id] = item;
      });
    });
  });

  const el = {
    date: document.getElementById('cdDate'),
    doneMeter: document.getElementById('cdDoneMeter'),
    decks: Array.prototype.slice.call(document.querySelectorAll('.cd-deck')),
    savedCount: document.getElementById('cdSavedCount'),
    card: document.getElementById('cdCard'),
    theme: document.getElementById('cdTheme'),
    index: document.getElementById('cdIndex'),
    art: document.getElementById('cdArt'),
    headline: document.getElementById('cdHeadline'),
    summary: document.getElementById('cdSummary'),
    action: document.getElementById('cdActionText'),
    source: document.getElementById('cdSource'),
    saveBtn: document.getElementById('cdSaveBtn'),
    saveLabel: document.getElementById('cdSaveLabel'),
    doneBtn: document.getElementById('cdDoneBtn'),
    doneLabel: document.getElementById('cdDoneLabel'),
    savedList: document.getElementById('cdSavedList'),
    allList: document.getElementById('cdAllList'),
    controls: document.getElementById('cdControls'),
    dots: document.getElementById('cdDots')
  };

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
    const dark = saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
    applyTheme(dark, false);
  })();

  const state = { deck: CD_DATA.decks[0].id, index: 0, themeId: null, drag: null, dayKey: '' };

  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function kstNow() { return new Date(Date.now() + 9 * 3600 * 1000); }
  function kstKey() {
    const d = kstNow();
    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  }
  function dayIndex() {
    const d = kstNow();
    return Math.floor(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()) / 86400000);
  }
  function deckById(id) {
    return CD_DATA.decks.filter(function (d) { return d.id === id; })[0];
  }
  function todayTheme(deck) {
    const i = ((dayIndex() % deck.themes.length) + deck.themes.length) % deck.themes.length;
    return deck.themes[i];
  }
  function currentDeck() { return deckById(state.deck); }
  function currentChosenDeck() { return deckById(state.deck) || CD_DATA.decks[0]; }
  function isSavedView() { return state.deck === 'saved'; }
  function isAllView() { return state.deck === 'all'; }
  function isListView() { return isSavedView() || isAllView(); }
  function themeById(deck, id) {
    return deck.themes.filter(function (t) { return t.id === id; })[0] || null;
  }
  function shownTheme(deck) {
    return (state.themeId && themeById(deck, state.themeId)) || todayTheme(deck);
  }
  function themeCards(theme) {
    return theme.cards.map(function (c) { return BY_ID[c.id]; });
  }

  function readSaved() {
    let raw;
    try { raw = JSON.parse(localStorage.getItem(SAVED_KEY) || '[]'); } catch (e) { return []; }
    if (!Array.isArray(raw)) return [];
    const out = [];
    raw.forEach(function (id) {
      if (typeof id === 'string' && BY_ID[id] && out.indexOf(id) < 0) out.push(id);
    });
    return out.slice(0, 60);
  }
  function writeSaved(ids) {
    try { localStorage.setItem(SAVED_KEY, JSON.stringify(ids.slice(0, 60))); } catch (e) {}
  }
  function readDone() {
    const key = kstKey();
    let raw;
    try { raw = JSON.parse(localStorage.getItem(DONE_KEY) || '{}'); } catch (e) { return { date: key, ids: [] }; }
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return { date: key, ids: [] };
    if (raw.date !== key) return { date: key, ids: [] };
    const ids = Array.isArray(raw.ids) ? raw.ids.filter(function (id) { return typeof id === 'string' && BY_ID[id]; }) : [];
    return { date: key, ids: ids };
  }
  function writeDone(ids) {
    try { localStorage.setItem(DONE_KEY, JSON.stringify({ date: kstKey(), ids: ids })); } catch (e) {}
  }
  state.done = readDone();

  function visibleItems() {
    if (isListView()) return [];
    return themeCards(shownTheme(currentDeck()));
  }

  function updateCount() {
    const n = readSaved().length;
    el.savedCount.textContent = String(n);
    el.savedCount.setAttribute('aria-label', '저장한 카드 ' + n + '장');
  }

  function updateMeta() {
    const d = kstNow();
    const label = (d.getUTCMonth() + 1) + '월 ' + d.getUTCDate() + '일 (' + WEEK[d.getUTCDay()] + ')';
    el.date.textContent = label;
    if (isAllView()) {
      el.doneMeter.innerHTML = '카드 <strong>' + ITEMS.length + '장</strong>';
      return;
    }
    const items = isSavedView() ? [] : themeCards(shownTheme(currentDeck()));
    const done = items.filter(function (c) { return state.done.ids.indexOf(c.id) >= 0; }).length;
    el.doneMeter.innerHTML = '오늘 실천 <strong>' + done + '/' + items.length + '</strong>';
  }

  function renderDots(count) {
    el.dots.textContent = '';
    for (let i = 0; i < count; i += 1) {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'cd-dot' + (i === state.index ? ' is-active' : '');
      dot.setAttribute('role', 'tab');
      dot.setAttribute('aria-selected', i === state.index ? 'true' : 'false');
      dot.setAttribute('aria-label', (i + 1) + '번째 카드');
      dot.addEventListener('click', function () { goTo(i); });
      el.dots.appendChild(dot);
    }
  }

  function safeSourceUrl(url) {
    return (typeof url === 'string' && url.indexOf('https://') === 0 && url.indexOf(' ') < 0) ? url : '';
  }

  function sourceLine(item, compact) {
    const box = document.createElement('span');
    if (item.source) {
      const org = item.source.org || '';
      const topic = item.source.topic || '';
      const checked = item.source.checked || CD_DATA.checkedOn;
      box.appendChild(document.createTextNode(
        (compact ? org : '출처 ' + org) + ' · ' + topic + ' · ' + checked + ' 확인'
      ));
      const href = safeSourceUrl(item.source.url);
      if (href) {
        const link = document.createElement('a');
        link.className = 'cd-source-link';
        link.setAttribute('href', href);
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
        link.setAttribute('aria-label', org + ' ' + topic + ' 원문 열기(새 창)');
        link.textContent = '원문 보기';
        box.appendChild(document.createTextNode(' · '));
        box.appendChild(link);
      }
    } else {
      box.appendChild(document.createTextNode('생활 팁 · ' + CD_DATA.checkedOn + ' 정리'));
    }
    return box;
  }

  function renderCard(animate) {
    const items = visibleItems();
    if (!items.length) return;
    if (state.index >= items.length) state.index = 0;
    if (state.index < 0) state.index = items.length - 1;
    const item = items[state.index];

    const deck = currentChosenDeck();
    const isToday = shownTheme(deck).id === todayTheme(deck).id;
    el.theme.textContent = (isToday ? '오늘의 테마 · ' : '테마 · ') + item.themeTitle;
    el.index.textContent = (state.index + 1) + ' / ' + items.length;
    el.art.innerHTML = CD_ART[item.art] || '';
    el.headline.textContent = item.headline;
    el.summary.textContent = item.summary;
    el.action.textContent = item.action;

    el.source.hidden = false;
    el.source.textContent = '';
    el.source.appendChild(sourceLine(item, false));

    const saved = readSaved().indexOf(item.id) >= 0;
    el.saveBtn.classList.toggle('is-saved', saved);
    el.saveBtn.setAttribute('aria-pressed', saved ? 'true' : 'false');
    el.saveLabel.textContent = saved ? '저장됨' : '저장';

    const done = state.done.ids.indexOf(item.id) >= 0;
    el.doneBtn.classList.toggle('is-done', done);
    el.doneBtn.setAttribute('aria-pressed', done ? 'true' : 'false');
    el.doneLabel.textContent = done ? '체크 완료' : '실천 체크';

    renderDots(items.length);
    updateCount();
    updateMeta();

    if (animate && !REDUCE) {
      el.card.classList.remove('is-enter');
      void el.card.offsetWidth;
      el.card.classList.add('is-enter');
    }
  }

  function savedRow(item) {
    const row = document.createElement('article');
    row.className = 'cd-savedrow';

    const thumb = document.createElement('div');
    thumb.className = 'cd-savedrow-art';
    thumb.setAttribute('aria-hidden', 'true');
    thumb.innerHTML = CD_ART[item.art] || '';

    const body = document.createElement('div');
    body.className = 'cd-savedrow-body';
    const meta = document.createElement('p');
    meta.className = 'cd-savedrow-meta';
    meta.textContent = item.deckTitle + ' · ' + item.themeTitle;
    const title = document.createElement('h3');
    title.textContent = item.headline;
    const summary = document.createElement('p');
    summary.className = 'cd-savedrow-summary';
    summary.textContent = item.summary;
    const action = document.createElement('p');
    action.className = 'cd-savedrow-action';
    action.textContent = '오늘 해볼 한 가지 · ' + item.action;
    const src = document.createElement('p');
    src.className = 'cd-allrow-src';
    src.appendChild(sourceLine(item, true));
    body.appendChild(meta);
    body.appendChild(title);
    body.appendChild(summary);
    body.appendChild(action);
    body.appendChild(src);

    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'cd-saved-remove';
    remove.textContent = '빼기';
    remove.setAttribute('aria-label', title.textContent + ' 저장 빼기');
    remove.addEventListener('click', function () {
      writeSaved(readSaved().filter(function (id) { return id !== item.id; }));
      render();
    });

    row.appendChild(thumb);
    row.appendChild(body);
    row.appendChild(remove);
    return row;
  }

  function renderSavedList() {
    el.savedList.textContent = '';
    const ids = readSaved();
    if (!ids.length) {
      const empty = document.createElement('div');
      empty.className = 'cd-empty';
      const strong = document.createElement('strong');
      strong.textContent = '아직 저장한 카드가 없어요';
      const p = document.createElement('p');
      p.textContent = '카드를 넘기다 마음에 드는 장은 저장해 두면 여기에 모입니다.';
      empty.appendChild(strong);
      empty.appendChild(p);
      el.savedList.appendChild(empty);
      return;
    }
    ids.forEach(function (id) { el.savedList.appendChild(savedRow(BY_ID[id])); });
  }

  function render() {
    el.decks.forEach(function (btn) {
      const active = btn.getAttribute('data-deck') === state.deck;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    const saved = isSavedView();
    const all = isAllView();
    el.card.hidden = saved || all;
    el.controls.hidden = saved || all;
    el.savedList.hidden = !saved;
    el.allList.hidden = !all;
    if (saved) {
      renderSavedList();
      updateCount();
      updateMeta();
    } else if (all) {
      renderAllList();
      updateCount();
      updateMeta();
    } else {
      renderCard(true);
    }
  }

  // ---- 전체 카드: 덱 → 테마 → 카드 24장 목록. 날짜와 상관없이 언제나 모두 열린다.
  function allRow(item) {
    const row = document.createElement('div');
    row.className = 'cd-allrow';
    row.setAttribute('data-card', item.id);
    row.setAttribute('data-deck', item.deckId);
    row.setAttribute('data-theme', item.themeId);
    row.setAttribute('data-headline', item.headline);

    const open = document.createElement('button');
    open.type = 'button';
    open.className = 'cd-allrow-open';
    open.setAttribute('aria-label', item.deckTitle + ' ' + item.themeTitle + ' ' + item.headline + ' 열기');

    const thumb = document.createElement('span');
    thumb.className = 'cd-allrow-art';
    thumb.setAttribute('aria-hidden', 'true');
    thumb.innerHTML = CD_ART[item.art] || '';

    const body = document.createElement('span');
    body.className = 'cd-allrow-body';
    const title = document.createElement('span');
    title.className = 'cd-allrow-title';
    title.textContent = item.headline;
    const summary = document.createElement('span');
    summary.className = 'cd-allrow-summary';
    summary.textContent = item.summary;
    body.appendChild(title);
    body.appendChild(summary);
    open.appendChild(thumb);
    open.appendChild(body);
    open.addEventListener('click', function () { openCard(item.id); });

    const src = document.createElement('p');
    src.className = 'cd-allrow-src';
    src.appendChild(sourceLine(item, true));

    row.appendChild(open);
    row.appendChild(src);
    return row;
  }

  function renderAllList() {
    el.allList.textContent = '';
    CD_DATA.decks.forEach(function (deck) {
      deck.themes.forEach(function (theme) {
        const group = document.createElement('section');
        group.className = 'cd-allgroup';
        group.setAttribute('data-theme', theme.id);
        const head = document.createElement('div');
        head.className = 'cd-allgroup-head';
        const deckName = document.createElement('span');
        deckName.className = 'cd-allgroup-deck';
        deckName.textContent = deck.title;
        const themeName = document.createElement('span');
        themeName.className = 'cd-allgroup-theme';
        themeName.textContent = theme.title;
        const count = document.createElement('span');
        count.className = 'cd-allgroup-count';
        count.textContent = theme.cards.length + '장';
        head.appendChild(deckName);
        head.appendChild(themeName);
        head.appendChild(count);
        group.appendChild(head);
        theme.cards.forEach(function (c) { group.appendChild(allRow(BY_ID[c.id])); });
        el.allList.appendChild(group);
      });
    });
  }

  function openCard(id) {
    const item = BY_ID[id];
    if (!item) return;
    const deck = deckById(item.deckId);
    const theme = deck ? themeById(deck, item.themeId) : null;
    if (!deck || !theme) return;
    const at = theme.cards.map(function (c) { return c.id; }).indexOf(id);
    state.deck = deck.id;
    state.themeId = theme.id;
    state.index = at < 0 ? 0 : at;
    render();
  }

  function go(step) {
    if (isListView()) return;
    const items = visibleItems();
    if (!items.length) return;
    state.index = ((state.index + step) % items.length + items.length) % items.length;
    renderCard(true);
  }
  function goTo(index) {
    if (isListView()) return;
    const items = visibleItems();
    if (index < 0 || index >= items.length) return;
    state.index = index;
    renderCard(true);
  }

  el.decks.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const next = btn.getAttribute('data-deck');
      if (next === state.deck) {
        // 같은 칩을 다시 누르면 오늘 테마로 돌아온다(전체 카드에서 연 다른 테마를 넣어 둔 경우).
        if (!isListView() && state.themeId) {
          state.themeId = null;
          state.index = 0;
          render();
        }
        return;
      }
      state.deck = next;
      state.index = 0;
      state.themeId = null;
      render();
    });
  });

  document.getElementById('cdPrev').addEventListener('click', function () { go(-1); });
  document.getElementById('cdNext').addEventListener('click', function () { go(1); });

  el.saveBtn.addEventListener('click', function () {
    const items = visibleItems();
    const item = items[state.index];
    if (!item) return;
    const ids = readSaved();
    const at = ids.indexOf(item.id);
    if (at >= 0) ids.splice(at, 1); else ids.unshift(item.id);
    writeSaved(ids);
    render();
  });

  el.doneBtn.addEventListener('click', function () {
    const items = visibleItems();
    const item = items[state.index];
    if (!item) return;
    const ids = state.done.ids.slice();
    const at = ids.indexOf(item.id);
    if (at >= 0) ids.splice(at, 1); else ids.push(item.id);
    state.done = { date: kstKey(), ids: ids };
    writeDone(ids);
    renderCard(true);
  });

  document.addEventListener('keydown', function (event) {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const tag = (event.target && event.target.tagName) ? event.target.tagName.toLowerCase() : '';
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return;
    if (isListView()) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); go(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); go(1); }
  });

  el.card.addEventListener('pointerdown', function (event) {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    if (event.target.closest && event.target.closest('button, a')) return;
    state.drag = { x: event.clientX, y: event.clientY, dx: 0, id: event.pointerId, active: false };
  });
  el.card.addEventListener('pointermove', function (event) {
    const drag = state.drag;
    if (!drag || event.pointerId !== drag.id) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    if (!drag.active) {
      if (Math.abs(dx) < 10 || Math.abs(dx) <= Math.abs(dy)) return;
      drag.active = true;
      el.card.classList.add('is-dragging');
      if (el.card.setPointerCapture) {
        try { el.card.setPointerCapture(event.pointerId); } catch (e) {}
      }
    }
    drag.dx = dx;
    if (!REDUCE) {
      el.card.style.transform = 'translateX(' + Math.max(-56, Math.min(56, dx)) + 'px)';
    }
  });
  function endDrag() {
    const drag = state.drag;
    state.drag = null;
    if (!drag) return;
    el.card.classList.remove('is-dragging');
    el.card.style.transform = '';
    if (drag.active && drag.dx <= -40) go(1);
    else if (drag.active && drag.dx >= 40) go(-1);
  }
  el.card.addEventListener('pointerup', endDrag);
  el.card.addEventListener('pointercancel', endDrag);

  function checkDay() {
    const key = kstKey();
    if (key === state.dayKey) return;
    state.dayKey = key;
    state.done = readDone();
    if (!state.themeId) state.index = 0;
    render();
  }
  window.setInterval(checkDay, 60000);
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) checkDay();
  });

  state.dayKey = kstKey();
  render();
})();
"""


def build_data(now=None):
    kst_now = now or datetime.now(KST)
    index_days = (kst_now.date() - EPOCH).days
    decks = []
    for key in ("condition", "digital"):
        title, subtitle = DECK_META[key]
        themes = THEMES[key]
        if len(themes) != 4:
            raise ValueError("%s 덱의 테마가 4개가 아닙니다: %d" % (key, len(themes)))
        for theme in themes:
            if len(theme["cards"]) != 3:
                raise ValueError("%s/%s 카드가 3장이 아닙니다: %d" % (key, theme["id"], len(theme["cards"])))
        decks.append({
            "id": key,
            "title": title,
            "subtitle": subtitle,
            "todayTheme": themes[index_days % len(themes)]["id"],
            "themes": themes,
        })
    ids = [c["id"] for deck in decks for theme in deck["themes"] for c in theme["cards"]]
    if len(ids) != len(set(ids)):
        raise ValueError("카드 ID 가 중복됩니다")
    for deck in decks:
        for theme in deck["themes"]:
            for c in theme["cards"]:
                if c["art"] not in ART:
                    raise ValueError("카드 %s 의 그림 키가 없습니다: %s" % (c["id"], c["art"]))
    return {
        "generated": kst_now.strftime("%Y-%m-%d %H:%M KST"),
        "checkedOn": CHECKED_ON,
        "rotation": {deck["id"]: deck["todayTheme"] for deck in decks},
        "decks": decks,
    }


def build():
    kst_now = datetime.now(KST)
    data = build_data(kst_now)
    payload = safe_json_for_script(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    art_payload = safe_json_for_script(json.dumps(ART, ensure_ascii=False, separators=(",", ":")))

    html = (HTML_TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__DATA_JSON__", payload)
            .replace("__ART_JSON__", art_payload)
            .replace("__JS__", JS))

    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(CARDS_HTML, "w", encoding="utf-8") as handle:
        handle.write(harden_html(ui_shell.apply(html, "cards")))

    total = sum(len(c) for deck in data["decks"] for theme in deck["themes"] for c in [theme["cards"]])
    print("-> 'cards_data.json' 저장 완료 (카드 %d장 · 덱 %d개 · 테마 %d개)"
          % (total, len(data["decks"]), sum(len(d["themes"]) for d in data["decks"])))
    print("-> 'cards.html' 생성 완료 (오늘: %s)" % ", ".join(
        "%s=%s" % (d["id"], d["todayTheme"]) for d in data["decks"]))
    return {
        "cards": total,
        "decks": len(data["decks"]),
        "themes": sum(len(d["themes"]) for d in data["decks"]),
        "today": data["rotation"],
        "checkedOn": data["checkedOn"],
    }


if __name__ == "__main__":
    build()

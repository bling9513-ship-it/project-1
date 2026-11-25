#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국내·해외 증시 이슈 수집·요약 크롤러 (Infosec Archive · market.html)

무엇을 모으나
  [뉴스]  재배포·자동 수집이 공개 피드로 허용된 곳만 쓴다.
          · CNBC Top News / Markets / World Markets (공개 RSS)
          · MarketWatch Top Stories (공개 RSS)
          · 연방준비제도(Federal Reserve) 보도자료 (공식 RSS, 미국 정부 저작물)
          · 연합뉴스·매일경제는 무허가 AI 활용·자동 수집을 제한하므로 수집하지 않는다.
  [공식 일정] ① 연준 FOMC 회의·의사록 — federalreserve.gov 공개 calendar.json
              ② 미 CPI·고용보고서 발표일 — BLS 공개 일정표
                 (bls.gov 직접 접속이 막히면 web.archive.org 의 같은 공식 페이지 사본을 쓰고,
                  보관일과 bls.gov 원문 링크를 일정 카드에 함께 남긴다)
              ③ 한국은행 금통위 — bok.or.kr 통화정책방향 결정회의 일정
              ④ 주요 기업 실적 — api.nasdaq.com 실적 캘린더에서 미국 대형주만(시총은 거르는 데만 쓴다)
  [시세]  재게시하지 않는다. 지수·종목·환율 수치는 화면에 싣지 않고,
          KRX 정보데이터시스템·네이버 증권·Nasdaq 등 원문 확인 링크만 안내한다.
          (Yahoo Finance 등은 자사 시세 재배포를 금지한다.)

장 상태
  거래소 캘린더(KRX·NYSE/Nasdaq 휴장일·조기 마감)로 계산한다.
  · KRX 09:00~15:30 (수능일 등 늦은 개장 별도)
  · NYSE/Nasdaq 09:30~16:00 ET (추수감사절 다음 날·크리스마스 이브는 13:00 ET 조기 마감)
  · 상태: 개장 전 / 장 진행 중 / 조기 마감 / 오늘 장 마감 / 휴장

요약
  - ai_news_crawler.py 와 같은 EXAONE(k-exaone_v2.5) 호출·캐시·폴백 패턴을 쓴다.
    · market_cache.json 캐시(성공한 분석만 저장) → 재실행 시 호출 절감
    · API 한도·오류·키 없음 → 원문 제목 그대로 + '뚜렷한 원인 미확인' 정직 표기
  - 기사 RSS 설명(description)은 EXAONE 입력에도, 공개 JSON 에도 쓰지 않는다.
    제목·매체·시각·섹터·원문 링크만 남긴다.
  - 원인은 제목에 적힌 것만 쓴다. 근거가 약하면 confidence='미확인', why='뚜렷한 원인 미확인'.

보안
  - EXAONE_API_KEY 는 .env(로컬) 또는 환경변수에서만 읽고 로그·JSON·Git 어디에도 쓰지 않는다.
  - 외부 응답은 net_guard 로 크기 상한을 두고, XML 은 DTD/ENTITY 선언을 거부한다(safe_xml_fromstring).

실행
  python3 market_crawler.py            # 수집 + 요약 → market_data.json
  python3 market_crawler.py --no-ai    # EXAONE 호출 없이 폴백만(오프라인 확인용)
"""
import argparse
import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from net_guard import MAX_HTML_BYTES, read_limited, safe_xml_fromstring

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(BASE_DIR, "market_data.json")
CACHE_FILE = os.path.join(BASE_DIR, "market_cache.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

KST = timezone(timedelta(hours=9))
ET = ZoneInfo("America/New_York")
SEOUL = ZoneInfo("Asia/Seoul")

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 화면에서 쓰는 섹터 묶음. AI 분석도 이 목록 안에서만 고르게 한다.
SECTORS = ["AI·반도체", "2차전지", "방산", "바이오", "금융", "자동차", "조선", "에너지·화학",
           "유통·소비", "인터넷·플랫폼", "매크로"]
SECTOR_ALIASES = {
    "반도체": "AI·반도체", "AI": "AI·반도체", "인공지능": "AI·반도체", "半导体": "AI·반도체",
    "배터리": "2차전지", "이차전지": "2차전지", "방위산업": "방산", "제약": "바이오",
    "은행": "금융", "증권": "금융", "보험": "금융", "조선기자재": "조선",
    "화학": "에너지·화학", "정유": "에너지·화학", "에너지": "에너지·화학",
    "소비재": "유통·소비", "유통": "유통·소비", "플랫폼": "인터넷·플랫폼",
    "금리": "매크로", "환율": "매크로", "물가": "매크로", "고용": "매크로", "정책": "매크로",
}

# ---------------------------------------------------------------------------
# 거래소 캘린더 (장 상태 계산용)
#   KRX: 한국거래소 휴장일 목록(2026년 17일) — 2026-11-26 교차 확인.
#        ※ 2027년 일정은 거래소 공지가 나오면 이 표에 추가한다(그 전까지 coverage 밖은 '확인 필요').
#   NYSE/Nasdaq: nyse.com Holidays & Trading Hours (2026·2027) — 2026-11-26 확인.
#        추수감사절 다음 날·크리스마스 이브는 13:00 ET 조기 마감.
# ---------------------------------------------------------------------------
KRX_HOLIDAYS_2026 = {
    "2026-01-01": "신정",
    "2026-02-16": "설날 연휴",
    "2026-02-17": "설날",
    "2026-02-18": "설날 연휴",
    "2026-03-02": "삼일절 대체휴일",
    "2026-05-01": "근로자의 날",
    "2026-05-05": "어린이날",
    "2026-05-25": "부처님오신날 대체휴일",
    "2026-06-03": "전국동시지방선거일",
    "2026-07-17": "제헌절",
    "2026-08-17": "광복절 대체휴일",
    "2026-09-24": "추석 연휴",
    "2026-09-25": "추석",
    "2026-10-05": "개천절 대체휴일",
    "2026-10-09": "한글날",
    "2026-12-25": "성탄절",
    "2026-12-31": "연말 휴장일",
}

NYSE_HOLIDAYS = {
    "2026-01-01": "New Year's Day",
    "2026-01-19": "Martin Luther King, Jr. Day",
    "2026-02-16": "Washington's Birthday",
    "2026-04-03": "Good Friday",
    "2026-05-25": "Memorial Day",
    "2026-06-19": "Juneteenth",
    "2026-07-03": "Independence Day(observed)",
    "2026-09-07": "Labor Day",
    "2026-11-26": "Thanksgiving Day",
    "2026-12-25": "Christmas Day",
    "2027-01-01": "New Year's Day",
    "2027-01-18": "Martin Luther King, Jr. Day",
    "2027-02-15": "Washington's Birthday",
    "2027-03-26": "Good Friday",
    "2027-05-31": "Memorial Day",
    "2027-06-18": "Juneteenth(observed)",
    "2027-07-05": "Independence Day(observed)",
    "2027-09-06": "Labor Day",
    "2027-11-25": "Thanksgiving Day",
    "2027-12-24": "Christmas Day(observed)",
}

NYSE_HOLIDAY_KO = {
    "New Year's Day": "신정",
    "Martin Luther King, Jr. Day": "마틴 루터 킹 데이",
    "Washington's Birthday": "대통령의 날",
    "Good Friday": "성금요일",
    "Memorial Day": "메모리얼 데이",
    "Juneteenth": "준틴스의 날",
    "Juneteenth(observed)": "준틴스의 날(대체)",
    "Independence Day(observed)": "독립기념일(대체)",
    "Labor Day": "노동절",
    "Thanksgiving Day": "추수감사절",
    "Christmas Day": "크리스마스",
    "Christmas Day(observed)": "크리스마스(대체)",
}

CALENDARS = {
    "domestic": {
        "name": "한국거래소(KRX)",
        "short": "국내",
        "timezone": "Asia/Seoul",
        "tzLabel": "KST",
        "open": (9, 0),
        "close": (15, 30),
        "holidays": KRX_HOLIDAYS_2026,
        "holidayLabels": {},
        # 늦은 개장·늦은 마감(수능일 등) — 거래소 공지 기준
        "specialSessions": {"2026-11-19": ((10, 0), (16, 30))},
        "earlyCloses": {},
        "coverage": ("2026-01-01", "2026-12-31"),
        "calendarName": "한국거래소 증시일정(휴장일)",
        "calendarUrl": "https://www.krx.co.kr/main/main.jsp",
    },
    "global": {
        "name": "NYSE·Nasdaq",
        "short": "해외",
        "timezone": "America/New_York",
        "tzLabel": "ET",
        "open": (9, 30),
        "close": (16, 0),
        "holidays": NYSE_HOLIDAYS,
        "holidayLabels": NYSE_HOLIDAY_KO,
        "specialSessions": {},
        "earlyCloses": {"2026-11-27": (13, 0), "2026-12-24": (13, 0), "2027-11-26": (13, 0)},
        "coverage": ("2026-01-01", "2027-12-31"),
        "calendarName": "NYSE 거래시간·휴장일",
        "calendarUrl": "https://www.nyse.com/trade/hours-calendars",
    },
}

# 시세를 재게시하지 않는 대신 원문에서 직접 확인하도록 안내하는 링크.
MARKET_LINKS = {
    "domestic": [
        {"label": "KRX 정보데이터시스템", "url": "https://data.krx.co.kr/"},
        {"label": "네이버 증권", "url": "https://finance.naver.com/"},
        {"label": "서울외국환중개(원/달러)", "url": "https://www.smbs.biz/"},
        {"label": "한국은행 ECOS", "url": "https://ecos.bok.or.kr/"},
    ],
    "global": [
        {"label": "Nasdaq", "url": "https://www.nasdaq.com/market-activity"},
        {"label": "Yahoo Finance", "url": "https://finance.yahoo.com/"},
        {"label": "CNBC Markets", "url": "https://www.cnbc.com/markets/"},
        {"label": "MarketWatch", "url": "https://www.marketwatch.com/"},
    ],
}

# 뉴스 RSS — (매체, 구분, URL, 언어, 공식 여부)
# 연합뉴스·매일경제는 자동 수집·AI 활용을 제한해 넣지 않는다.
FEEDS = [
    ("CNBC", "Top News", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "en", False),
    ("CNBC", "Markets", "https://www.cnbc.com/id/20910258/device/rss/rss.html", "en", False),
    ("CNBC", "World Markets", "https://www.cnbc.com/id/10000664/device/rss/rss.html", "en", False),
    ("MarketWatch", "Top Stories", "https://feeds.content.dowjones.io/public/rss/mw_topstories", "en", False),
    ("연방준비제도", "보도자료", "https://www.federalreserve.gov/feeds/press_all.xml", "en", True),
]

# 시장 관련 기사만 남기는 키워드.
GLOBAL_TERMS = re.compile(
    r"(stock|stocks|wall street|nasdaq|s&p|dow|futures|rally|selloff|sell-off|fed|federal reserve|"
    r"rate cut|rate hike|treasury|yield|bond|dollar|oil|gold|earnings|revenue|profit|guidance|"
    r"chip|chips|semiconductor|nvidia|apple|microsoft|google|alphabet|amazon|meta|tesla|(?<![a-z])ai(?![a-z])|"
    r"artificial intelligence|inflation|cpi|jobs report|payroll|tariff|trade deal|ipo|merger|"
    r"acquisition|kospi|nikkei|hang seng|bitcoin|crypto|shares|valuation|dividend|buyback|"
    r"economy|economic|recession|gdp|market|prices|bank|employment|unemployment|labor|"
    r"monetary policy|discount rate|financial stability|fomc)", re.I)
# 헤드라인 모음·포토 같은 목록 기사는 이슈 카드로 쓰지 않는다.
NEWS_EXCLUDE = re.compile(r"(이 시각 헤드라인|주요 뉴스|헤드라인\]|포토\]|화보\]|종합\]|만평|오늘의 날씨|^\s*\[표\]|\[게시판\]|시세표|럭셔리 어드벤트|부동산 시세|연예|advent calendar|mansion|celebrity|relists|real estate|luxury|home price|^\[(코스피|코스닥|외환|증시|주요지수)\]|장종료\)$)", re.I)
# 연준 보도자료 중 시장과 무관한 행사·채용 안내는 뺀다.
FED_NOISE = re.compile(r"(Challenge winners|award|ceremony|speech|testimony|opening remarks|"
                       r"appointment|Board announces|community|scholarship)", re.I)

# 실적 일정은 '주요 기업'만 — 미국 대형주 위주 관심 목록(시가총액 조건과 함께 본다).
EARNINGS_WATCH = {
    "NVDA", "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "AVGO", "AMD", "TSM", "MU",
    "ORCL", "CRM", "ADBE", "NFLX", "COST", "WMT", "JPM", "BAC", "GS", "MS", "C", "XOM", "CVX",
    "JNJ", "PFE", "LLY", "UNH", "KO", "PEP", "DIS", "INTC", "QCOM", "MRVL", "SNPS", "ADSK", "NOW",
    "INTU", "DE", "CAT", "BA", "NKE", "SBUX", "PYPL", "UBER", "ABNB", "PLTR", "SMCI", "ARM", "TXN",
}

MAX_NEWS = 46           # market_data.json 에 담을 기사 상한
CACHE_VERSION = "v3"   # 프롬프트 규칙을 바꾸면 올린다(예전 분석은 쓰지 않음)
AI_ITEM_LIMIT = 12      # 이번 실행에서 EXAONE 으로 정리할 기사 수(최근 기사 우선 · 하루 100회 한도 보호)
AI_BATCH = 3            # EXAONE 한 번에 분석할 기사 수(추론 토큰이 많아 3건이 안정적)
AI_MAX_CALLS = 12       # EXAONE 분석 호출 상한(일일 100회 한도 보호)
NEWS_WINDOW_HOURS = 48  # 이 시간 안에 올라온 기사만
UNKNOWN_CAUSE = "뚜렷한 원인 미확인"
CONFIDENCE_VALUES = ("원문 근거", "추정", "미확인")

# 시세·요약 재게시를 막아야 하는 매체(수집·출력 금지 목록). 검증에서도 쓴다.
BLOCKED_SOURCES = ("연합뉴스", "매일경제", "Yahoo Finance")


# ---------------------------------------------------------------------------
# 공통 유틸
# ---------------------------------------------------------------------------
def now_kst():
    return datetime.now(KST)


def kst_text(dt):
    return dt.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S KST")


def fetch_bytes(url, timeout=25, tries=3, headers=None):
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    last_err = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return read_limited(resp, MAX_HTML_BYTES)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if attempt < tries - 1:
                time.sleep(1.2 * (attempt + 1))
    raise RuntimeError("요청 실패 %s: %s" % (url, last_err))


def clean_text(text, limit=None):
    if not text:
        return ""
    text = html.unescape(str(text))
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def norm_title(title):
    return re.sub(r"[^0-9a-z가-힣]+", "", (title or "").lower())


def dedupe_key(title):
    """같은 기사 판별용 키 — 대괄호 머리표·(종합) 꼬리표를 떼고 비교한다."""
    cleaned = re.sub(r"[\[（(][^\]）)]{0,12}[\]）)]", "", title or "")
    return norm_title(cleaned)[:36]


def item_id(source, title, url):
    raw = "%s|%s|%s" % (source, norm_title(title)[:60], url)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def parse_pub(text):
    """RSS pubDate 문자열 → KST datetime (실패하면 None)."""
    if not text:
        return None
    value = text.strip()
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(value, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(KST)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# 1) 장 상태 — 거래소 캘린더 기준
# ---------------------------------------------------------------------------
def _hm(text):
    hour, minute = str(text).split(":")
    return int(hour), int(minute)


def _is_trading_day(market, day):
    cal = CALENDARS[market]
    return day.weekday() < 5 and day.isoformat() not in cal["holidays"]


def _session_times(market, day):
    cal = CALENDARS[market]
    key = day.isoformat()
    if key in cal["specialSessions"]:
        return cal["specialSessions"][key]
    close = cal["earlyCloses"].get(key) or cal["close"]
    return cal["open"], close


def _next_trading_day(market, day, include_today=False):
    cal = CALENDARS[market]
    start = day if include_today else day + timedelta(days=1)
    for offset in range(0, 60):
        candidate = start + timedelta(days=offset)
        if _is_trading_day(market, candidate):
            return candidate
    return None


def _prev_trading_day(market, day, include_today=False):
    start = day if include_today else day - timedelta(days=1)
    for offset in range(0, 60):
        candidate = start - timedelta(days=offset)
        if _is_trading_day(market, candidate):
            return candidate
    return None


def _date_label(day):
    return "%d월 %d일(%s)" % (day.month, day.day, "월화수목금토일"[day.weekday()])


def market_session(market, now):
    """거래소 캘린더로 장 상태를 계산한다(시세 봉이 오지 않아도 휴장으로 오표기하지 않는다)."""
    cal = CALENDARS[market]
    tz = ZoneInfo(cal["timezone"])
    local = now.astimezone(tz)
    today = local.date()
    key = today.isoformat()
    open_t, close_t = _session_times(market, today)
    now_hm = (local.hour, local.minute)
    early_close = key in cal["earlyCloses"]
    coverage_start, coverage_end = cal["coverage"]
    outside = not (coverage_start <= key <= coverage_end)
    holiday_reason = cal["holidays"].get(key, "")
    holiday_reason = cal.get("holidayLabels", {}).get(holiday_reason, holiday_reason)

    if today.weekday() >= 5:
        state, label, reason = "holiday", "휴장", "주말"
    elif holiday_reason:
        state, label, reason = "holiday", "휴장", holiday_reason
    elif now_hm < open_t:
        state, label, reason = "preopen", "개장 전", ""
    elif now_hm < close_t:
        state, label, reason = "open", "장 진행 중", ""
    elif early_close:
        state, label, reason = "early_closed", "조기 마감", "13:00 ET 조기 마감" if market == "global" else "조기 마감"
    else:
        state, label, reason = "closed", "오늘 장 마감", ""

    if state in ("open", "closed", "early_closed"):
        last_trading = today
    else:
        last_trading = _prev_trading_day(market, today, include_today=False)

    if state == "preopen":
        next_trading = today
    elif state == "holiday":
        next_trading = _next_trading_day(market, today, include_today=True)
    else:
        next_trading = _next_trading_day(market, today, include_today=False)

    session_text = "%02d:%02d~%02d:%02d" % (open_t[0], open_t[1], close_t[0], close_t[1])
    return {
        "state": state,
        "stateLabel": label,
        "reason": reason,
        "marketName": cal["name"],
        "timezone": cal["timezone"],
        "tzLabel": cal["tzLabel"],
        "localNow": local.strftime("%m-%d %H:%M"),
        "localDate": key,
        "sessionText": session_text,
        "earlyClose": early_close,
        "lastTradingDate": last_trading.isoformat() if last_trading else "",
        "lastTradingLabel": _date_label(last_trading) if last_trading else "",
        "nextTradingDate": next_trading.isoformat() if next_trading else "",
        "nextTradingLabel": _date_label(next_trading) if next_trading else "",
        "outsideCalendar": outside,
        "calendarName": cal["calendarName"],
        "calendarUrl": cal["calendarUrl"],
    }


# ---------------------------------------------------------------------------
# 2) 뉴스 수집 — 제목·매체·시각만 (RSS 설명은 저장하지 않는다)
# ---------------------------------------------------------------------------
def parse_feed(raw, source, section, lang, official):
    items = []
    try:
        root = safe_xml_fromstring(raw)
    except ET.ParseError:
        return items
    for node in root.iter("item"):
        title = clean_text(node.findtext("title") or "")
        link = (node.findtext("link") or "").strip()
        pub = parse_pub(node.findtext("pubDate") or node.findtext("{http://purl.org/dc/elements/1.1/}date") or "")
        if not title or not link.startswith("http"):
            continue
        items.append({
            "title": title,
            "url": link,
            "published": pub,
            "source": source,
            "section": section,
            "lang": lang,
            "official": official,
        })
    return items


def collect_news(now, sources):
    window_start = now - timedelta(hours=NEWS_WINDOW_HOURS)
    collected = []
    for source, section, url, lang, official in FEEDS:
        entry = {"name": "%s %s" % (source, section), "kind": "공식 발표" if official else "뉴스",
                 "url": url, "status": "ok", "count": 0}
        try:
            raw = fetch_bytes(url, timeout=25)
            rows = parse_feed(raw, source, section, lang, official)
        except Exception as exc:  # noqa: BLE001
            entry["status"] = "실패"
            entry["error"] = type(exc).__name__
            sources.append(entry)
            print("  [뉴스] %s %s 실패: %s" % (source, section, exc))
            continue
        kept = 0
        for row in rows:
            if row["published"] and row["published"] < window_start:
                continue
            if NEWS_EXCLUDE.search(row["title"]):
                continue
            if official and FED_NOISE.search(row["title"]):
                continue
            if not GLOBAL_TERMS.search(row["title"]):
                continue
            row["id"] = item_id(row["source"], row["title"], row["url"])
            row["market"] = "domestic" if row["lang"] == "ko" else "global"
            row["published_kst"] = row["published"].strftime("%m-%d %H:%M") if row["published"] else ""
            collected.append(row)
            kept += 1
        entry["count"] = kept
        sources.append(entry)
        print("  [뉴스] %s %s %d건" % (source, section, kept))

    seen = set()
    unique = []
    for row in sorted(collected, key=lambda r: r["published"] or datetime(1970, 1, 1, tzinfo=KST), reverse=True):
        key = dedupe_key(row["title"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)

    # 국내·해외를 번갈아 담아 한쪽이 목록을 다 차지하지 않게 한다.
    domestic = [r for r in unique if r["market"] == "domestic"]
    global_ = [r for r in unique if r["market"] == "global"]
    mixed = []
    for i in range(max(len(domestic), len(global_))):
        if i < len(domestic):
            mixed.append(domestic[i])
        if i < len(global_):
            mixed.append(global_[i])
    return mixed[:MAX_NEWS]


# ---------------------------------------------------------------------------
# 3) 공식 일정
# ---------------------------------------------------------------------------
MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def et_to_kst(date_obj, hour, minute):
    local = datetime(date_obj.year, date_obj.month, date_obj.day, hour, minute, tzinfo=ET)
    return local.astimezone(KST)


def parse_et_time(text):
    """'2:00 p.m.' / '08:30 AM' → (시, 분). 못 읽으면 None."""
    if not text:
        return None
    raw = text.strip().lower().replace(".", "")
    match = re.match(r"^(\d{1,2}):(\d{2})\s*([ap]m)?$", raw)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    marker = match.group(3)
    if marker == "pm" and hour != 12:
        hour += 12
    if marker == "am" and hour == 12:
        hour = 0
    return hour, minute


def calendar_fomc(now, sources):
    """연준 FOMC 회의(결정)·의사록 — federalreserve.gov 공개 calendar.json."""
    url = "https://www.federalreserve.gov/json/calendar.json"
    out = []
    try:
        raw = fetch_bytes(url, timeout=30)
        data = json.loads(raw.decode("utf-8-sig"))
        events = data.get("events") or []
    except Exception as exc:  # noqa: BLE001
        sources.append({"name": "연준(FOMC)", "kind": "공식 일정", "url": url, "status": "실패",
                        "count": 0, "error": type(exc).__name__})
        print("  [일정] FOMC 실패: %s" % exc)
        return out

    for event in events:
        if event.get("type") != "FOMC":
            continue
        title = (event.get("title") or "").strip()
        month = event.get("month") or ""
        days = event.get("days") or ""
        if not re.match(r"^\d{4}-\d{2}$", month) or not str(days).isdigit():
            continue
        try:
            date_obj = datetime.strptime("%s-%02d" % (month, int(days)), "%Y-%m-%d").date()
        except ValueError:
            continue
        if date_obj < now.date() - timedelta(days=1) or date_obj > now.date() + timedelta(days=120):
            continue
        lowered = title.lower()
        if "press conference" in lowered:
            continue  # 회의 결정과 같은 날이라 따로 적지 않는다
        parsed = parse_et_time(event.get("time"))
        if "minutes" in lowered:
            label, category = "FOMC 의사록 공개", "금리"
            note = "직전 회의 의사록"
        elif "meeting" in lowered:
            label, category = "FOMC 회의·금리 결정", "금리"
            note = "이틀 회의 마지막 날 결정 발표(현지 14:00)"
        else:
            continue
        if parsed:
            kst_dt = et_to_kst(date_obj, parsed[0], parsed[1])
        else:
            kst_dt = et_to_kst(date_obj, 14, 0)
        out.append({
            "id": "fomc-%s-%s" % (month, days),
            "date": kst_dt.date().isoformat(),
            "timeKst": kst_dt.strftime("%H:%M") if parsed else "",
            "title": label,
            "category": category,
            "region": "해외",
            "note": note,
            "source": "연방준비제도(Federal Reserve)",
            "sourceUrl": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            "localDate": date_obj.isoformat(),
        })
    sources.append({"name": "연준(FOMC)", "kind": "공식 일정", "url": url,
                    "status": "ok", "count": len(out)})
    print("  [일정] FOMC %d건" % len(out))
    return out


def _bls_schedule_rows(raw_html):
    """BLS 일정표(Reference Month | Release Date | Release Time)를 (날짜, 시각) 목록으로.

    셀 경계만 구분자(\\x00)로 바꾸고 셀 안의 공백("October 2026", "Nov. 10, 2026")은 그대로 둔다.
    """
    text = re.sub(r"<script.*?</script>", " ", raw_html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\x00", text)
    text = html.unescape(text).replace("\xa0", " ").replace("&nbsp;", " ")
    text = re.sub(r"[ \t\r\n]+", " ", text)
    text = re.sub(r"(?:\x00 ?)+", "\x00", text)
    rows = []
    for match in re.finditer(
            "\\x00([A-Z][a-z]+ \\d{4})\\x00([A-Z][a-z]{2})\\.? ?(\\d{1,2}), (\\d{4})"
            "\\x00(\\d{1,2}:\\d{2} [AP]M)", text):
        month = MONTHS.get(match.group(2).lower())
        if not month:
            continue
        try:
            date_obj = datetime(int(match.group(4)), month, int(match.group(3))).date()
        except ValueError:
            continue
        parsed = parse_et_time(match.group(5))
        rows.append((date_obj, parsed))
    return rows


def _bls_from_archive(url):
    """web.archive.org 의 같은 BLS 페이지 사본에서 일정표를 읽는다(보관일도 함께 돌려준다)."""
    try:
        probe = fetch_bytes("https://archive.org/wayback/available?url=%s"
                            % urllib.parse.quote(url.split("://", 1)[1], safe="/:?=&\""),
                            timeout=25)
        info = json.loads(probe.decode("utf-8"))
        closest = ((info.get("archived_snapshots") or {}).get("closest") or {})
        snapshot = closest.get("url")
        if not snapshot:
            return [], "", "", "실패"
        if snapshot.startswith("http://"):
            snapshot = "https://" + snapshot[len("http://"):]
        stamp = str(closest.get("timestamp") or "")
        snapshot_date = ("%s-%s-%s" % (stamp[0:4], stamp[4:6], stamp[6:8])
                         if re.match(r"^\d{8}", stamp) else "")
        raw = fetch_bytes(snapshot, timeout=40)
        rows = _bls_schedule_rows(raw.decode("utf-8", "ignore"))
        return rows, snapshot, snapshot_date, ("보관 사본" if rows else "실패")
    except Exception as exc:  # noqa: BLE001
        print("  [일정] BLS 보관 사본 실패: %s" % exc)
        return [], "", "", "실패"


def calendar_bls(now, sources):
    """미 CPI·고용보고서 발표 일정 — BLS 공개 일정표(직접 접속 실패 시 보관 사본)."""
    out = []
    targets = [
        ("cpi", "미 소비자물가지수(CPI)", "https://www.bls.gov/schedule/news_release/cpi.htm", "물가"),
        ("jobs", "미 고용보고서(비농업 고용)", "https://www.bls.gov/schedule/news_release/empsit.htm", "고용"),
    ]
    for key, label, url, category in targets:
        rows = []
        status = "실패"
        used_url = url
        snapshot_date = ""
        try:
            rows = _bls_schedule_rows(fetch_bytes(url, timeout=25).decode("utf-8", "ignore"))
            if rows:
                status = "ok"
        except Exception:  # noqa: BLE001
            rows = []
        if not rows:
            # bls.gov 가 막혀 있으면 같은 공식 페이지의 웹 아카이브 사본을 쓴다(연간 일정표라 날짜는 그대로다).
            rows, used_url, snapshot_date, status = _bls_from_archive(url)
        for date_obj, parsed in rows:
            if date_obj < now.date() - timedelta(days=1) or date_obj > now.date() + timedelta(days=120):
                continue
            kst_dt = et_to_kst(date_obj, parsed[0], parsed[1]) if parsed else et_to_kst(date_obj, 8, 30)
            row = {
                "id": "%s-%s" % (key, date_obj.isoformat()),
                "date": kst_dt.date().isoformat(),
                "timeKst": kst_dt.strftime("%H:%M") if parsed else "",
                "title": label,
                "category": category,
                "region": "해외",
                "note": "현지 08:30 발표",
                "source": "미 노동통계국(BLS)",
                "sourceUrl": url,
                "localDate": date_obj.isoformat(),
            }
            if snapshot_date:
                row["snapshotDate"] = snapshot_date
                row["archiveUrl"] = used_url
            out.append(row)
        entry = {"name": "미 노동통계국(BLS) %s" % label, "kind": "공식 일정",
                 "url": url, "status": status, "count": len(rows)}
        if snapshot_date:
            entry["archiveUrl"] = used_url
            entry["snapshotDate"] = snapshot_date
            entry["note"] = "bls.gov 직접 접속 차단 → web.archive.org 보관 사본 사용"
        sources.append(entry)
        print("  [일정] %s %d건 (%s%s)" % (label, len(rows), status,
                                          ", 보관 %s" % snapshot_date if snapshot_date else ""))
    return out


def calendar_bok(now, sources):
    """한국은행 금통위(통화정책방향 결정회의) 일정 — bok.or.kr 공개 목록."""
    out = []
    url = ("https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do"
           "?menuNo=200755&mtgSe=A&pYear=%d")
    fetched = 0
    for year in (now.year, now.year + 1):
        try:
            raw = fetch_bytes(url % year, timeout=30).decode("utf-8", "ignore")
        except Exception as exc:  # noqa: BLE001
            print("  [일정] 한국은행 %d년 실패: %s" % (year, exc))
            continue
        found = 0
        for month, day, weekday in re.findall(r"(\d{2})월\s*(\d{2})일\s*\(([월화수목금토일])\)", raw):
            try:
                date_obj = datetime(year, int(month), int(day)).date()
            except ValueError:
                continue
            if date_obj < now.date() - timedelta(days=1) or date_obj > now.date() + timedelta(days=120):
                continue
            out.append({
                "id": "bok-%s" % date_obj.isoformat(),
                "date": date_obj.isoformat(),
                "timeKst": "",
                "title": "한국은행 금통위 기준금리 결정",
                "category": "금리",
                "region": "국내",
                "note": "결정문 발표 시각은 당일 공지(보통 오전)",
                "source": "한국은행",
                "sourceUrl": "https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?menuNo=200755",
                "localDate": date_obj.isoformat(),
            })
            found += 1
        fetched += found
    sources.append({"name": "한국은행 금통위", "kind": "공식 일정", "url": url % now.year,
                    "status": "ok" if fetched else "실패", "count": fetched})
    print("  [일정] 한국은행 금통위 %d건" % fetched)
    return out


def calendar_earnings(now, sources):
    """주요 기업 실적 — api.nasdaq.com 실적 캘린더에서 미국 대형주(관심 목록)만.

    시가총액은 '거르는 기준'으로만 쓰고 화면에는 쓰지 않는다(시세 재게시 방지).
    관심 목록에 걸린 기업이 한 주에 없으면 시가총액 상위 4건으로 대신한다.
    """
    picked = []
    candidates = []
    status = "ok"
    for offset in range(0, 15):
        day = now.date() + timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        url = "https://api.nasdaq.com/api/calendar/earnings?date=%s" % day.isoformat()
        try:
            raw = fetch_bytes(url, timeout=20, headers={"Accept": "application/json"})
            data = json.loads(raw.decode("utf-8")).get("data") or {}
        except Exception:  # noqa: BLE001
            status = "일부 실패"
            continue
        for row in data.get("rows") or []:
            cap_text = str(row.get("marketCap") or "")
            digits = re.sub(r"[^0-9]", "", cap_text)
            if not digits or int(digits) < 100_000_000_000:
                continue
            symbol = (row.get("symbol") or "").strip().upper()
            timing = (row.get("time") or "").strip()
            if timing == "time-pre-market":
                note = "현지 장 시작 전"
                kst_date = day
            elif timing == "time-after-hours":
                # 미 동부 16시 이후 발표 → 한국은 다음 날 새벽
                note = "현지 장 마감 후(한국 다음 날 새벽)"
                kst_date = day + timedelta(days=1)
            else:
                note = "발표 시각 미정"
                kst_date = day
            entry = {
                "id": "earn-%s-%s" % (day.isoformat(), symbol),
                "date": kst_date.isoformat(),
                "timeKst": "",
                "title": "%s 실적 발표" % clean_text(row.get("name") or symbol),
                "category": "실적",
                "region": "해외",
                "note": note,
                "source": "Nasdaq 실적 캘린더",
                "sourceUrl": "https://www.nasdaq.com/market-activity/earnings",
                "localDate": day.isoformat(),
            }
            candidates.append((int(digits), entry))
            if symbol in EARNINGS_WATCH:
                picked.append((int(digits), entry))
        time.sleep(0.25)
    rows = picked
    if not rows:
        rows = sorted(candidates, key=lambda item: item[0], reverse=True)[:4]
    out = [entry for _cap, entry in sorted(rows, key=lambda item: (item[1]["date"], -item[0]))]
    sources.append({"name": "Nasdaq 실적 캘린더", "kind": "공식 일정",
                    "url": "https://www.nasdaq.com/market-activity/earnings",
                    "status": status, "count": len(out)})
    print("  [일정] 주요 기업 실적 %d건" % len(out))
    return out


def collect_calendar(now, sources):
    rows = (calendar_fomc(now, sources) + calendar_bls(now, sources)
            + calendar_bok(now, sources) + calendar_earnings(now, sources))
    # 같은 날 같은 제목은 한 번만, 가까운 날짜 순.
    seen = set()
    unique = []
    for row in rows:
        key = (row["date"], row["title"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    unique.sort(key=lambda r: (r["date"], r["timeKst"] or "99:99"))
    return [row for row in unique if row["date"] <= (now.date() + timedelta(days=21)).isoformat()]


# ---------------------------------------------------------------------------
# 4) EXAONE 요약 (캐시 + 폴백) — 기사 제목만 입력한다
# ---------------------------------------------------------------------------
def get_api_key():
    key = os.environ.get("EXAONE_API_KEY")
    if key:
        return key.strip()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip().startswith("EXAONE_API_KEY="):
                    return line.strip().split("=", 1)[1].strip()
    return None


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:  # noqa: BLE001
            return {}
    return {}


def prune_cache(cache):
    """현재 분석 형식(v3)이 아닌 캐시는 버린다.

    예전 캐시에는 연합뉴스·매일경제 RSS 설명에서 만든 요약문이 들어 있어
    공개 산출물로 흘러가지 않도록 남기지 않는다.
    """
    kept = {key: value for key, value in cache.items()
            if str(key).startswith(CACHE_VERSION + "|") and isinstance(value, dict)}
    return kept, len(cache) - len(kept)


def save_cache(cache):
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(cache, handle, ensure_ascii=False, indent=2)
    os.replace(tmp, CACHE_FILE)


MARKET_SYSTEM_PROMPT = (
    "당신은 증시 기사 제목을 정리하는 한국어 금융 기자입니다. 주어진 제목에 없는 원인·수치·전망은 "
    "만들지 않습니다. 반드시 지정된 JSON 만 출력합니다."
)


def call_exaone(prompt, api_key, max_tokens=3000, timeout=150):
    payload = {
        "model": "k-exaone_v2.5",
        "messages": [
            {"role": "system", "content": MARKET_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "reasoning_effort": "low",
    }
    req = urllib.request.Request(
        "https://api.exaone.ai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(read_limited(resp).decode("utf-8"))
    choice = (data.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content") or ""
    return content, choice.get("finish_reason")


def parse_json_block(content):
    """응답에서 첫 JSON 객체/배열만 꺼낸다"""
    if not content:
        return None
    text = content.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    for open_char, close_char in (("[", "]"), ("{", "}")):
        start = text.find(open_char)
        end = text.rfind(close_char)
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue
    return None


def normalize_sector(raw):
    values = raw if isinstance(raw, list) else [raw]
    sectors = []
    for value in values:
        name = clean_text(str(value or ""))
        if not name:
            continue
        if name in SECTORS:
            sectors.append(name)
            continue
        for alias, target in SECTOR_ALIASES.items():
            if alias in name:
                sectors.append(target)
                break
    deduped = []
    for name in sectors:
        if name not in deduped:
            deduped.append(name)
    return deduped[:2] or ["매크로"]


RULE_SECTOR_TERMS = [
    ("AI·반도체", r"(반도체|삼성전자|SK하이닉스|엔비디아|nvidia|hbm|파운드리|인공지능|(?<![a-z])ai(?![a-z])|칩|chip)"),
    ("2차전지", r"(2차전지|배터리|battery|양극재|음극재|리튬|전기차)"),
    ("방산", r"(방산|방위|무기|수출 계약|한화에어로|k-방산|defen[cs]e)"),
    ("바이오", r"(바이오|제약|임상|신약|바이오시밀러|fda)"),
    ("금융", r"(은행|증권|보험|금융지주|예금|대출|kb금융|신한지주|bank)"),
    ("자동차", r"(자동차|현대차|기아|완성차|전기차 판매)"),
    ("조선", r"(조선|선박|수주잔고|hd현대중공업)"),
    ("에너지·화학", r"(정유|화학|유가|원유|wti|석유|가스|opec|oil|energy)"),
    ("유통·소비", r"(유통|소비|백화점|편의점|면세|카드 매출|retail|consumer)"),
    ("인터넷·플랫폼", r"(플랫폼|네이버|카카오|구글|메타|쿠팡|이커머스|platform)"),
    ("매크로", r"(금리|물가|환율|고용|연준|fed|fomc|cpi|관세|정책|경기|gdp|rate|inflation)"),
]


def rule_sectors(item):
    """제목만 보고 섹터를 고른다(요약문은 쓰지 않는다)."""
    blob = item.get("title", "")
    for name, pattern in RULE_SECTOR_TERMS:
        if re.search(pattern, blob, re.I):
            return [name]
    return ["매크로"]


def fallback_analysis(item):
    """AI 없이도 화면이 비지 않게 — 원문 제목 그대로, 원인은 '미확인'으로 정직하게."""
    return {
        "title_ko": item["title"],
        "why": UNKNOWN_CAUSE,
        "confidence": "미확인",
        "sectors": rule_sectors(item),
        "analyzed_by": "fallback",
    }


def build_issue_prompt(chunk):
    lines = []
    for index, item in enumerate(chunk, 1):
        lines.append(
            "[%d] 매체: %s | 시각: %s\n제목: %s"
            % (index, item["source"], item.get("published_kst") or "미상", item["title"])
        )
    body = "\n\n".join(lines)
    return (
        "다음 증시 관련 기사 제목 %d건을 보고 JSON 배열로만 답하세요. 기사 본문은 주지 않습니다.\n"
        "각 항목 키:\n"
        "- id: 입력 번호(정수)\n"
        "- title_ko: 한국어 제목 34자 이내. 영어 제목은 자연스러운 한국어로 옮기고, "
        "기업·지수·제품 이름은 원문 표기(NVIDIA, S&P500 등) 유지\n"
        "- why: '무엇 때문에 주가·지수가 움직였는지' 한 줄 60자 이내. "
        "제목에 원인이 드러나 있을 때만 그 표현을 살려 쓰고, "
        "제목만으로 알 수 없으면 정확히 \"%s\" 라고만 쓴다\n"
        "- confidence: \"원문 근거\"(제목에 원인·수치가 명시) / \"추정\"(정황상 짐작) / \"미확인\"(알 수 없음)\n"
        "- sectors: 다음 중 1~2개 — %s\n"
        "제목에 없는 내용·수치·전망을 새로 만들지 마세요. 요약문은 쓰지 않습니다.\n\n"
        "%s\n\n"
        "출력: [{\"id\":1,\"title_ko\":\"...\",\"why\":\"...\",\"confidence\":\"...\",\"sectors\":[\"...\"]}]"
        % (len(chunk), UNKNOWN_CAUSE, ", ".join(SECTORS), body)
    )


def analyze_news(items, api_key, cache, max_calls=AI_MAX_CALLS):
    """기사별 한 줄 원인·섹터. 캐시 → EXAONE → 폴백 순서."""
    for item in items:
        cached = cache.get(CACHE_VERSION + "|" + item["id"])
        if cached and cached.get("title_ko") and cached.get("why"):
            item.update({k: cached[k] for k in ("title_ko", "why", "confidence", "sectors")
                         if k in cached})
            item["analyzed_by"] = "cache"
        else:
            item.update(fallback_analysis(item))

    pending = [item for item in items if item.get("analyzed_by") == "fallback"][:AI_ITEM_LIMIT]
    if not pending:
        cached = sum(1 for item in items if item.get("analyzed_by") == "cache")
        print("  [요약] 새로 분석할 기사 없음(캐시 %d건) — 호출 생략" % cached)
        return {"used": False, "analyzed": 0, "fallback": 0}
    if not api_key:
        print("  [요약] EXAONE 키 없음/꺼짐 — 대기 %d건은 폴백" % len(pending))
        return {"used": False, "analyzed": 0, "fallback": len(pending)}

    print("  [요약] EXAONE 분석 대기 %d건 (호출 상한 %d회)" % (len(pending), max_calls))
    used = 0
    calls = 0
    for start in range(0, len(pending), AI_BATCH):
        if calls >= max_calls:
            print("  [요약] 호출 상한 도달 → 남은 %d건은 폴백" % (len(pending) - start))
            break
        chunk = pending[start:start + AI_BATCH]
        prompt = build_issue_prompt(chunk)
        calls += 1
        content = None
        for attempt in range(2):
            try:
                content, finish = call_exaone(prompt, api_key, max_tokens=3000)
                if not (content or "").strip():
                    print("  [요약] 빈 응답(finish=%s) → 재시도" % finish)
                    raise RuntimeError("빈 응답")
                break
            except urllib.error.HTTPError as exc:
                if exc.code in (401, 403):
                    print("  [요약] 키 인증 실패 → 폴백으로 전환")
                    api_key = None
                    break
                wait = 20 if exc.code == 429 else 4 * (attempt + 1)
                print("  [요약] HTTP %d → %d초 후 재시도" % (exc.code, wait))
                time.sleep(wait)
                content = None
            except Exception as exc:  # noqa: BLE001
                print("  [요약] 오류 %s: %s" % (type(exc).__name__, exc))
                time.sleep(2)
                content = None
        if not api_key:
            break
        parsed = parse_json_block(content) if content else None
        if not isinstance(parsed, list):
            print("  [요약] JSON 파싱 실패 → 이 묶음은 폴백")
            continue
        by_id = {}
        for row in parsed:
            if isinstance(row, dict) and str(row.get("id", "")).isdigit():
                by_id[int(row["id"])] = row
        for index, item in enumerate(chunk, 1):
            row = by_id.get(index)
            if not row:
                continue
            why = clean_text(row.get("why") or "", 80) or UNKNOWN_CAUSE
            confidence = clean_text(row.get("confidence") or "")
            if why == UNKNOWN_CAUSE or "미확인" in confidence:
                why, confidence = UNKNOWN_CAUSE, "미확인"
            elif confidence not in CONFIDENCE_VALUES:
                confidence = "추정"
            analysis = {
                "title_ko": clean_text(row.get("title_ko") or item["title"], 60) or item["title"],
                "why": why,
                "confidence": confidence,
                "sectors": normalize_sector(row.get("sectors")),
                "analyzed_by": "exaone",
            }
            item.update(analysis)
            cache[CACHE_VERSION + "|" + item["id"]] = analysis
            used += 1
        save_cache(cache)  # 중간 저장 — 중단되어도 다음 실행이 캐시로 이어 간다
        time.sleep(1.8)  # 무료 한도(초당 1회) 보호
    save_cache(cache)
    remaining = sum(1 for item in items if item.get("analyzed_by") == "fallback")
    return {"used": used > 0, "analyzed": used, "fallback": remaining}


# ---------------------------------------------------------------------------
# 5) 브리핑 — 수치 없이 제목·일정·장 상태만으로 만든다
# ---------------------------------------------------------------------------
def _clip(text, limit=80):
    text = clean_text(text)
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def _nearest_calendar(calendar, market, limit=2):
    rows = [row for row in (calendar or []) if (row["region"] == "국내") == (market == "domestic")]
    return rows[:limit]


def _calendar_line(row):
    when = row["date"][5:].replace("-", "/")
    return "%s %s %s" % (when, row.get("timeKst") or "시간 미정", row["title"])


def build_briefings(news, calendar, sessions):
    """시장별 3줄 — 오늘의 이슈 + 다음 거래일 점검.

    시세 수치를 쓰지 않는다. 기사 제목과 공식 일정, 장 상태만으로 채운다.
    """
    briefing = {"analyzed_by": {"domestic": "template", "global": "template"}}
    for market in ("domestic", "global"):
        session = sessions[market]
        rows = [row for row in news if row["market"] == market]

        issue_lines = []
        for row in rows[:3]:
            issue_lines.append(_clip("%s: %s" % (row["source"], row.get("title_ko") or row["title"])))
        if not issue_lines:
            if market == "domestic":
                issue_lines.append("국내 기사는 재배포·AI 활용이 허용된 공식 피드가 없어 제목을 싣지 않습니다.")
                issue_lines.append("국내 시세·수급은 KRX 정보데이터시스템과 네이버 증권에서 직접 확인하세요.")
            else:
                issue_lines.append("수집된 해외 기사가 없습니다. 아래 원문 링크에서 확인하세요.")
        while len(issue_lines) < 3:
            if market == "domestic":
                issue_lines.append("국내 공식 발표(한국은행) 일정은 아래 '이번 주 시장 일정'에 정리했습니다.")
            else:
                issue_lines.append("원인이 확인되지 않은 움직임은 '뚜렷한 원인 미확인'으로 표시합니다.")
        briefing[market] = {"issues": issue_lines[:3]}

        next_lines = []
        label = session["stateLabel"]
        if session.get("reason"):
            label = "%s(%s)" % (label, session["reason"])
        next_lines.append("현재 %s · 거래 시간 %s %s" % (label, session["sessionText"], session["tzLabel"]))
        upcoming = _nearest_calendar(calendar, market)
        if upcoming:
            next_lines.append("다음 일정 %s" % _calendar_line(upcoming[0]))
            if len(upcoming) > 1:
                next_lines.append("그다음 일정 %s" % _calendar_line(upcoming[1]))
        else:
            next_lines.append("예정된 공식 일정이 없습니다. 거래소·기관 일정표를 확인하세요.")
        while len(next_lines) < 3:
            next_lines.append("시세는 이 페이지에 싣지 않습니다. 위 '공식 시세 확인' 링크를 쓰세요.")
        briefing[market]["next"] = next_lines[:3]
    return briefing


# ---------------------------------------------------------------------------
# 6) 조립
# ---------------------------------------------------------------------------
def build_sector_board(news):
    board = []
    for name in SECTORS:
        rows = [item for item in news if name in (item.get("sectors") or [])]
        board.append({
            "name": name,
            "count": len(rows),
            "items": [{"title": item.get("title_ko") or item["title"], "source": item["source"],
                       "url": item["url"]} for item in rows[:3]],
        })
    return board


def assemble(now, news, calendar, briefing, ai_stats, sources):
    sessions = {market: market_session(market, now) for market in ("domestic", "global")}
    issues = []
    for item in news:
        issues.append({
            "id": item["id"],
            "market": item["market"],
            "title": item.get("title_ko") or item["title"],
            "titleOriginal": item["title"],
            "why": item.get("why") or UNKNOWN_CAUSE,
            "confidence": item.get("confidence") or "미확인",
            "sectors": item.get("sectors") or ["매크로"],
            "source": item["source"],
            "sourceSection": item.get("section") or "",
            "official": bool(item.get("official")),
            "url": item["url"],
            "publishedKst": item.get("published_kst") or "",
            "analyzedBy": item.get("analyzed_by") or "fallback",
        })
    notes = [
        "지수·종목·환율 수치는 이 페이지에 게시하지 않습니다. 위 '공식 시세 확인' 링크(KRX 정보데이터시스템·네이버 증권·Nasdaq 등)에서 직접 확인하세요.",
        "기사는 제목·매체·시각·원문 링크만 보여 줍니다. 전문과 저작권은 각 매체에 있습니다.",
        "연합뉴스·매일경제처럼 자동 수집·AI 활용을 제한하는 매체는 수집하지 않습니다.",
        "원인이 제목만으로 확인되지 않으면 '뚜렷한 원인 미확인'으로 표시하고 추측으로 채우지 않습니다.",
        "BLS 일정 중 web.archive.org 보관 사본에서 읽은 항목은 카드에 보관일과 bls.gov 원문 링크를 함께 표기합니다.",
        "장 상태는 거래소 캘린더(휴장·조기 마감) 기준입니다. 임시 휴장·거래시간 변경은 거래소 공지를 확인하세요.",
        "일정의 한국시간은 서머타임에 따라 1시간 달라질 수 있습니다(현지 시각을 함께 적었습니다).",
    ]
    return {
        "meta": {
            "collectedAt": kst_text(now),
            "collectedAtIso": now.isoformat(timespec="seconds"),
            "ai": ai_stats,
            "sources": sources,
            "notes": notes,
            "newsCount": len(issues),
            "calendarCount": len(calendar),
        },
        "sessions": sessions,
        "marketLinks": MARKET_LINKS,
        "briefing": briefing,
        "issues": issues,
        "sectors": build_sector_board(news),
        "calendar": calendar,
    }


def validate(payload):
    """내보내기 전 최소 검증 — 빈 화면·깨진 링크·재게시 잔여물을 여기서 막는다."""
    problems = []
    if len(payload["issues"]) < 6:
        problems.append("기사 %d건(6건 미만)" % len(payload["issues"]))
    if not payload["calendar"]:
        problems.append("일정 0건")
    for issue in payload["issues"]:
        if not issue["url"].startswith("https://") and not issue["url"].startswith("http://"):
            problems.append("기사 링크 형식: %s" % issue["id"])
        if issue["source"] in BLOCKED_SOURCES:
            problems.append("재배포 제한 매체: %s" % issue["id"])
        if issue["confidence"] not in CONFIDENCE_VALUES:
            problems.append("confidence 값: %s" % issue["id"])
        if issue["confidence"] == "미확인" and issue["why"] != UNKNOWN_CAUSE:
            problems.append("미확인인데 원인 문장 있음: %s" % issue["id"])
        if any(name not in SECTORS for name in issue["sectors"]):
            problems.append("섹터 값: %s" % issue["id"])
    for row in payload["calendar"]:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", row["date"]):
            problems.append("일정 날짜: %s" % row["id"])
    for market, session in payload["sessions"].items():
        if session["state"] not in ("open", "closed", "preopen", "holiday", "early_closed", "unknown"):
            problems.append("장 상태 값: %s" % market)
        if session.get("outsideCalendar"):
            problems.append("거래소 캘린더 범위 밖: %s (%s)" % (market, session["localDate"]))
    return problems


def crawl(use_ai=True, out_path=None, now=None):
    now = now or now_kst()
    print("=== [증시 이슈] 수집 시작 %s ===" % kst_text(now))
    sources = []

    print("[1/4] 뉴스")
    news = collect_news(now, sources)

    print("[2/4] 공식 일정")
    calendar = collect_calendar(now, sources)

    print("[3/4] 요약")
    api_key = get_api_key() if use_ai else None
    cache, dropped = prune_cache(load_cache())
    if dropped:
        print("  [캐시] 예전 형식 분석 %d건 제거(연합뉴스·매일경제 설명 기반 포함)" % dropped)
        save_cache(cache)  # 공개 산출물로 흘러갈 수 있는 예전 요약문을 파일에서도 없앤다
    ai_stats = analyze_news(news, api_key, cache)
    # 캐시로 이미 정리된 기사까지 합쳐 실제 상태를 적는다.
    analyzed = sum(1 for item in news if item.get("analyzed_by") in ("exaone", "cache"))
    ai_stats.update({"used": analyzed > 0, "analyzed": analyzed,
                     "fallback": sum(1 for item in news if item.get("analyzed_by") == "fallback")})
    ai_stats["model"] = "k-exaone_v2.5" if ai_stats.get("used") else ""

    print("[4/4] 조립")
    sessions = {market: market_session(market, now) for market in ("domestic", "global")}
    briefing = build_briefings(news, calendar, sessions)
    payload = assemble(now, news, calendar, briefing, ai_stats, sources)
    problems = validate(payload)
    for problem in problems:
        print("  [검증] %s" % problem)

    target = out_path or OUT_JSON
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print("-> '%s' 저장 완료 (기사 %d건 · 일정 %d건 · AI %s)"
          % (os.path.basename(target), len(payload["issues"]), len(calendar),
             "%d건" % ai_stats.get("analyzed", 0) if ai_stats.get("used") else "폴백"))
    return payload


def analyze_existing(path=None, max_calls=AI_MAX_CALLS, now=None, skip_briefing=False):
    """이미 저장된 market_data.json 의 기사를 EXAONE 으로 이어서 분석한다(수집 없이)."""
    path = path or OUT_JSON
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    news = []
    for issue in payload["issues"]:
        news.append({
            "id": issue["id"],
            "title": issue.get("titleOriginal") or issue["title"],
            "source": issue["source"],
            "market": issue["market"],
            "published_kst": issue.get("publishedKst") or "",
            "url": issue["url"],
            "sectors": issue.get("sectors"),
            "official": issue.get("official", False),
        })
    cache, dropped = prune_cache(load_cache())
    stats = analyze_news(news, get_api_key(), cache, max_calls=max_calls)
    by_id = {item["id"]: item for item in news}
    for issue in payload["issues"]:
        item = by_id[issue["id"]]
        issue.update({
            "title": item.get("title_ko") or issue["title"],
            "why": item.get("why") or issue["why"],
            "confidence": item.get("confidence") or issue["confidence"],
            "sectors": item.get("sectors") or issue["sectors"],
            "analyzedBy": item.get("analyzed_by") or issue.get("analyzedBy"),
        })
    payload["sectors"] = build_sector_board(
        [{"id": issue["id"], "title": issue.get("titleOriginal") or issue["title"],
          "title_ko": issue["title"], "source": issue["source"], "url": issue["url"],
          "sectors": issue["sectors"]} for issue in payload["issues"]])
    ai_meta = dict(payload["meta"].get("ai") or {})
    ai_meta.update({"used": ai_meta.get("used") or stats["used"],
                    "analyzed": sum(1 for issue in payload["issues"] if issue.get("analyzedBy") in ("exaone", "cache")),
                    "fallback": sum(1 for issue in payload["issues"] if issue.get("analyzedBy") == "fallback"),
                    "model": "k-exaone_v2.5" if (ai_meta.get("used") or stats["used"]) else ""})
    if ai_meta.get("analyzed"):
        ai_meta["used"] = True
        ai_meta["model"] = "k-exaone_v2.5"
    payload["meta"]["ai"] = ai_meta
    if dropped:
        print("  [캐시] 예전 형식 분석 %d건 제거" % dropped)

    def _write():
        problems = validate(payload)
        for problem in problems:
            print("  [검증] %s" % problem)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    # 기사 분석 결과를 먼저 저장한다 — 중간에 끊겨도 분석분은 남는다.
    _write()

    if not skip_briefing:
        sessions = payload.get("sessions") or {}
        if len(sessions) == 2:
            briefing = build_briefings(news, payload.get("calendar") or [], sessions)
            payload["briefing"] = briefing
            _write()

    print("-> 'market_data.json' 갱신 (AI 분석 %d건 · 폴백 %d건)"
          % (ai_meta["analyzed"], ai_meta["fallback"]))
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description="증시 이슈 수집·요약")
    parser.add_argument("--no-ai", action="store_true", help="EXAONE 호출 없이 폴백만 사용")
    parser.add_argument("--out", default=None, help="저장 경로(기본 market_data.json)")
    parser.add_argument("--ai-only", action="store_true", help="수집 없이 저장된 market_data.json 의 기사만 이어서 요약")
    parser.add_argument("--max-calls", type=int, default=AI_MAX_CALLS, help="이번 실행의 EXAONE 호출 상한")
    parser.add_argument("--no-briefing", action="store_true", help="이어서 분석할 때 브리핑 재계산은 건너뛴다")
    args = parser.parse_args(argv)
    if args.ai_only:
        analyze_existing(args.out, max_calls=args.max_calls, skip_briefing=args.no_briefing)
        return 0
    crawl(use_ai=not args.no_ai, out_path=args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

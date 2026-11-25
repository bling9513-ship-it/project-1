#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국내·해외 증시 이슈 수집·요약 크롤러 (Infosec Archive · market.html)

무엇을 모으나
  [시세]  Yahoo Finance 공개 차트 API — 코스피·코스닥·나스닥·S&P500·다우·필라델피아 반도체,
          빅테크 7종(NVDA·AAPL·MSFT·GOOGL·AMZN·META·TSLA), 원/달러 환율(지연 시세)
  [국내 뉴스] 연합뉴스 마켓+ · 연합뉴스 경제 · 매일경제 헤드라인 (공개 RSS)
  [해외 뉴스] CNBC Economy · CNBC Finance · MarketWatch Top Stories (공개 RSS)
  [공식 일정] ① 연준 FOMC 회의·의사록 — federalreserve.gov 공개 calendar.json
              ② 미 CPI·고용보고서 발표일 — BLS(Bureau of Labor Statistics) 공개 일정표
                 (bls.gov 직접 접속이 막히면 web.archive.org 의 같은 공식 페이지 사본을 쓴다)
              ③ 한국은행 금통위 — bok.or.kr 통화정책방향 결정회의 일정
              ④ 주요 기업 실적 — api.nasdaq.com 실적 캘린더에서 시가총액 500억 달러 이상만

요약
  - ai_news_crawler.py 와 같은 EXAONE(k-exaone_v2.5) 호출·캐시·폴백 패턴을 쓴다.
    · market_cache.json 캐시(성공한 분석만 저장) → 재실행 시 호출 절감
    · API 한도·오류·키 없음 → 원문 제목 그대로 + '뚜렷한 원인 미확인' 정직 표기
  - 원인은 원문에 적힌 것만 쓴다. 근거가 약하면 confidence='미확인', why='뚜렷한 원인 미확인'.

저작권·시세
  - 뉴스는 제목·한 줄 요약·원문 링크만 보여 준다(전문 재게시 없음). 출처 매체 이름을 항상 함께 적는다.
  - 지수·종목 값은 지연 시세이며 참고용이다. 화면에도 '지연 시세' 라고 밝힌다.

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
from datetime import datetime, timedelta, timezone
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

# 지수·종목 (Yahoo Finance 심볼). value 는 '지연 시세' 임을 화면에 표시한다.
INDICES = [
    ("kospi", "코스피", "^KS11", "domestic", "KOSPI"),
    ("kosdaq", "코스닥", "^KQ11", "domestic", "KOSDAQ"),
    ("nasdaq", "나스닥", "^IXIC", "global", "NASDAQ Composite"),
    ("sp500", "S&P500", "^GSPC", "global", "S&P 500"),
    ("dow", "다우", "^DJI", "global", "Dow Jones"),
    ("sox", "필라델피아 반도체", "^SOX", "global", "PHLX Semiconductor"),
]
BIGTECH = [
    ("NVDA", "엔비디아"), ("AAPL", "애플"), ("MSFT", "마이크로소프트"),
    ("GOOGL", "알파벳"), ("AMZN", "아마존"), ("META", "메타"), ("TSLA", "테슬라"),
]
FX = [("usdkrw", "원/달러", "KRW=X")]

# 뉴스 RSS — (매체, 구분, URL, 언어)
FEEDS = [
    ("연합뉴스", "마켓+", "https://www.yna.co.kr/rss/market.xml", "ko"),
    ("연합뉴스", "경제", "https://www.yna.co.kr/rss/economy.xml", "ko"),
    ("매일경제", "헤드라인", "https://www.mk.co.kr/rss/30000001/", "ko"),
    ("CNBC", "Economy", "https://www.cnbc.com/id/20910258/device/rss/rss.html", "en"),
    ("CNBC", "Finance", "https://www.cnbc.com/id/10000664/device/rss/rss.html", "en"),
    ("MarketWatch", "Top Stories", "https://feeds.content.dowjones.io/public/rss/mw_topstories", "en"),
]

# 시장 관련 기사만 남기는 키워드.
#  · 강한 신호(주가·지수·수급·공시·금리 등)가 하나라도 있어야 증시 기사로 본다.
#    '반도체' '은행' 같은 업종 단어만 있는 기사(수상·채용·관광 뉴스)는 걸러진다.
#  · 그래도 남는 기사가 너무 적으면 업종 단어만 있는 기사를 뒤에 붙인다.
DOMESTIC_STRONG = re.compile(
    r"(코스피|코스닥|증시|주가|주식시장|지수|시가총액|순매수|순매도|공모주|상장|IPO|"
    r"영업이익|영업손실|잠정실적|실적 발표|어닝|배당|자사주|공매도|유상증자|무상증자|액면분할|"
    r"전환사채|합병|인수|매각|환율|금리|국고채|채권|증안펀드|사이드카|예탁금|투자심리|주주총회|"
    r"공시|펀드|수주|가이던스|증권사|자산운용|주가조작|미공개정보|대주주|종목|특징주)")
DOMESTIC_TERMS = re.compile(
    r"(반도체|삼성전자|SK하이닉스|2차전지|배터리|방산|바이오|제약|조선|자동차|은행|보험|"
    r"부동산|ETF|코인|비트코인|수출|무역|관세|물가|소비자물가|고용|소비|유통|플랫폼)")
GLOBAL_TERMS = re.compile(
    r"(stock|stocks|wall street|nasdaq|s&p|dow|futures|rally|selloff|sell-off|fed|federal reserve|"
    r"rate cut|rate hike|treasury|yield|bond|dollar|oil|gold|earnings|revenue|profit|guidance|"
    r"chip|chips|semiconductor|nvidia|apple|microsoft|google|alphabet|amazon|meta|tesla|ai |"
    r"artificial intelligence|inflation|cpi|jobs report|payroll|tariff|trade deal|ipo|merger|"
    r"acquisition|kospi|nikkei|hang seng|bitcoin|crypto|shares|valuation|dividend|buyback)", re.I)
# 헤드라인 모음·포토 같은 목록 기사는 이슈 카드로 쓰지 않는다.
NEWS_EXCLUDE = re.compile(r"(이 시각 헤드라인|주요 뉴스|헤드라인\]|포토\]|화보\]|종합\]|만평|오늘의 날씨|^\[표\]|\[게시판\]|시세표|럭셔리 어드벤트|부동산 시세|연예|advent calendar|mansion|celebrity|relists|real estate|luxury|home price|^\[(코스피|코스닥|외환|증시|주요지수)\]|장종료\)$)", re.I)

# 실적 일정은 '주요 기업'만 — 미국 대형주 위주 관심 목록(시가총액 조건과 함께 본다).
EARNINGS_WATCH = {
    "NVDA", "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "AVGO", "AMD", "TSM", "MU",
    "ORCL", "CRM", "ADBE", "NFLX", "COST", "WMT", "JPM", "BAC", "GS", "MS", "C", "XOM", "CVX",
    "JNJ", "PFE", "LLY", "UNH", "KO", "PEP", "DIS", "INTC", "QCOM", "MRVL", "SNPS", "ADSK", "NOW",
    "INTU", "DE", "CAT", "BA", "NKE", "SBUX", "PYPL", "UBER", "ABNB", "PLTR", "SMCI", "ARM", "TXN",
}

MAX_NEWS = 46           # market_data.json 에 담을 기사 상한
CACHE_VERSION = "v2"   # 프롬프트 규칙을 바꾸면 올린다(예전 분석은 쓰지 않음)
AI_ITEM_LIMIT = 18      # 이번 실행에서 EXAONE 으로 정리할 기사 수(최근 기사 우선)
AI_BATCH = 3            # EXAONE 한 번에 분석할 기사 수(추론 토큰이 많아 3건이 안정적)
AI_MAX_CALLS = 12       # EXAONE 분석 호출 상한(일일 100회 한도 보호)
NEWS_WINDOW_HOURS = 48  # 이 시간 안에 올라온 기사만


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
# 1) 뉴스 수집
# ---------------------------------------------------------------------------
def parse_feed(raw, source, section, lang):
    items = []
    try:
        root = safe_xml_fromstring(raw)
    except ET.ParseError:
        return items
    for node in root.iter("item"):
        title = clean_text(node.findtext("title") or "")
        link = (node.findtext("link") or "").strip()
        desc = clean_text(node.findtext("description") or "")
        pub = parse_pub(node.findtext("pubDate") or node.findtext("{http://purl.org/dc/elements/1.1/}date") or "")
        if not title or not link.startswith("http"):
            continue
        items.append({
            "title": title,
            "url": link,
            "summary_orig": desc,
            "published": pub,
            "source": source,
            "section": section,
            "lang": lang,
        })
    return items


def collect_news(now, sources):
    window_start = now - timedelta(hours=NEWS_WINDOW_HOURS)
    collected = []
    for source, section, url, lang in FEEDS:
        entry = {"name": source, "kind": "뉴스", "url": url, "status": "ok", "count": 0}
        try:
            raw = fetch_bytes(url, timeout=25)
            rows = parse_feed(raw, source, section, lang)
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
            blob = row["title"] + " " + row["summary_orig"]
            if row["lang"] == "ko":
                score = 0
                if DOMESTIC_STRONG.search(blob):
                    score = 2
                elif DOMESTIC_TERMS.search(blob):
                    score = 1
                if not score:
                    continue
            else:
                if not GLOBAL_TERMS.search(blob):
                    continue
                score = 2
            row["id"] = item_id(row["source"], row["title"], row["url"])
            row["market"] = "domestic" if row["lang"] == "ko" else "global"
            row["published_kst"] = row["published"].strftime("%m-%d %H:%M") if row["published"] else ""
            row["score"] = score
            collected.append(row)
            kept += 1
        entry["count"] = kept
        sources.append(entry)
        print("  [뉴스] %s %s %d건" % (source, section, kept))

    # 같은 기사(제목 앞부분 동일) 중복 제거 — 연합뉴스 마켓+/경제 양쪽에 뜨는 경우가 흔하다.
    strong = [row for row in collected if row.get("score", 0) >= 2]
    if len(strong) >= 12:
        collected = strong  # 증시 신호가 분명한 기사만 쓴다
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
# 2) 지수·종목 시세 (지연)
# ---------------------------------------------------------------------------
def yahoo_chart(symbol, range_="1mo", interval="1d"):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=%s"
           % (urllib.parse.quote(symbol), range_, interval))
    raw = fetch_bytes(url, timeout=20, headers={"Accept": "application/json"})
    data = json.loads(raw.decode("utf-8"))
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        raise RuntimeError("차트 응답 없음: %s" % symbol)
    return result[0]


def quote_of(symbol, name, market, label=None, source="Yahoo Finance"):
    node = yahoo_chart(symbol)
    meta = node.get("meta") or {}
    stamps = node.get("timestamp") or []
    closes = ((node.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    bars = []
    for ts, close in zip(stamps, closes):
        if close is None:
            continue
        tz_name = meta.get("exchangeTimezoneName") or "UTC"
        bars.append((datetime.fromtimestamp(ts, tz=ZoneInfo(tz_name)).date(), float(close)))
    price = meta.get("regularMarketPrice")
    if price is None and bars:
        price = bars[-1][1]
    prev = None
    if len(bars) >= 2:
        prev = bars[-2][1]
    change = meta.get("regularMarketChangePercent")
    if change is None and prev:
        change = (float(price) - prev) / prev * 100.0
    last_date = bars[-1][0].isoformat() if bars else ""
    tz_name = meta.get("exchangeTimezoneName") or "UTC"
    return {
        "id": symbol,
        "name": label or name,
        "symbol": symbol,
        "market": market,
        "currency": meta.get("currency") or "",
        "exchange": meta.get("fullExchangeName") or meta.get("exchangeName") or "",
        "value": round(float(price), 2) if price is not None else None,
        "prevClose": round(float(prev), 2) if prev is not None else None,
        "changePct": round(float(change), 2) if change is not None else None,
        "lastTradingDate": last_date,
        "timezone": tz_name,
        "source": source,
        "sourceUrl": "https://finance.yahoo.com/quote/%s" % urllib.parse.quote(symbol),
        "delayed": True,
    }


def session_state(market, quotes, now):
    """현지 거래일·휴장 여부를 시세 봉에서 계산한다(추측한 공휴일 목록을 쓰지 않는다)."""
    rows = [q for q in quotes if q["market"] == market and q.get("lastTradingDate")]
    if not rows:
        return {"state": "unknown", "stateLabel": "거래일 확인 실패", "lastTradingDate": "", "localNow": ""}
    tz_name = rows[0]["timezone"]
    tz = ZoneInfo(tz_name)
    local_now = now.astimezone(tz)
    last_date = max(row["lastTradingDate"] for row in rows)
    close_hour, close_minute = (15, 30) if market == "domestic" else (16, 0)
    open_hour, open_minute = (9, 0) if market == "domestic" else (9, 30)
    label_date = datetime.fromisoformat(last_date)
    weekday = "월화수목금토일"[label_date.weekday()]
    if last_date == local_now.date().isoformat():
        closed = (local_now.hour, local_now.minute) >= (close_hour, close_minute)
        state = "closed" if closed else "open"
        state_label = "오늘 장 마감" if closed else "오늘 장 진행 중"
    else:
        if local_now.weekday() >= 5:
            state, state_label = "holiday", "주말 휴장"
        elif (local_now.hour, local_now.minute) < (open_hour, open_minute):
            state, state_label = "preopen", "개장 전"
        else:
            state, state_label = "holiday", "휴장(공휴일 가능)"
    return {
        "state": state,
        "stateLabel": state_label,
        "lastTradingDate": last_date,
        "lastTradingLabel": "%d월 %d일(%s)" % (label_date.month, label_date.day, weekday),
        "localNow": local_now.strftime("%m-%d %H:%M"),
        "timezone": tz_name,
    }


def collect_quotes(sources):
    indices, bigtech, fx = [], [], []
    failed = 0
    for key, name, symbol, market, label in INDICES:
        try:
            row = quote_of(symbol, name, market, label=name)
            row["id"] = key
            indices.append(row)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print("  [시세] %s 실패: %s" % (name, exc))
    for symbol, name in BIGTECH:
        try:
            row = quote_of(symbol, name, "global", label=name)
            row["id"] = symbol.lower()
            bigtech.append(row)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print("  [시세] %s 실패: %s" % (symbol, exc))
    for key, name, symbol in FX:
        try:
            row = quote_of(symbol, name, "fx", label=name)
            row["id"] = key
            fx.append(row)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print("  [시세] %s 실패: %s" % (name, exc))
    sources.append({
        "name": "Yahoo Finance", "kind": "지연 시세",
        "url": "https://finance.yahoo.com/", "status": "ok" if not failed else ("일부 실패" if indices else "실패"),
        "count": len(indices) + len(bigtech) + len(fx),
    })
    return indices, bigtech, fx


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
        if not re.match(r"^\d{4}-\d{2}$", month) or not days.isdigit():
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

    셀 경계만 구분자(\x00)로 바꾸고 셀 안의 공백("October 2026", "Nov. 10, 2026")은 그대로 둔다.
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
        try:
            rows = _bls_schedule_rows(fetch_bytes(url, timeout=25).decode("utf-8", "ignore"))
            if rows:
                status = "ok"
        except Exception:  # noqa: BLE001
            rows = []
        if not rows:
            # bls.gov 가 막혀 있으면 같은 공식 페이지의 웹 아카이브 사본을 쓴다(연간 일정표라 날짜는 그대로다).
            rows, used_url, status = _bls_from_archive(url)
        for date_obj, parsed in rows:
            if date_obj < now.date() - timedelta(days=1) or date_obj > now.date() + timedelta(days=120):
                continue
            kst_dt = et_to_kst(date_obj, parsed[0], parsed[1]) if parsed else et_to_kst(date_obj, 8, 30)
            out.append({
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
            })
        sources.append({"name": "미 노동통계국(BLS) %s" % label, "kind": "공식 일정",
                        "url": used_url, "status": status, "count": len(rows)})
        print("  [일정] %s %d건 (%s)" % (label, len(rows), status))
    return out


def _bls_from_archive(url):
    """web.archive.org 의 같은 BLS 페이지 사본에서 일정표를 읽는다."""
    try:
        probe = fetch_bytes("https://archive.org/wayback/available?url=%s"
                            % urllib.parse.quote(url.split("://", 1)[1], safe="/:?=&"),
                            timeout=25)
        info = json.loads(probe.decode("utf-8"))
        closest = ((info.get("archived_snapshots") or {}).get("closest") or {})
        snapshot = closest.get("url")
        if not snapshot:
            return [], url, "실패"
        raw = fetch_bytes(snapshot, timeout=40)
        rows = _bls_schedule_rows(raw.decode("utf-8", "ignore"))
        return rows, snapshot, ("보관 사본" if rows else "실패")
    except Exception as exc:  # noqa: BLE001
        print("  [일정] BLS 보관 사본 실패: %s" % exc)
        return [], url, "실패"


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

    시가총액 1,000억 달러 이상 + EARNINGS_WATCH(미국 대형주) 조건을 함께 본다.
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
                "note": note + " · 시가총액 %d억 달러" % (int(digits) // 100_000_000),
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
# 4) EXAONE 요약 (캐시 + 폴백)
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


def save_cache(cache):
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(cache, handle, ensure_ascii=False, indent=2)
    os.replace(tmp, CACHE_FILE)


MARKET_SYSTEM_PROMPT = (
    "당신은 증시 시황을 정리하는 한국어 금융 기자입니다. 제공된 기사 원문만 근거로 삼고, "
    "원문에 없는 원인·수치·전망은 만들지 않습니다. 반드시 지정된 JSON 만 출력합니다."
)

CONFIDENCE_VALUES = ("원문 근거", "추정", "미확인")
UNKNOWN_CAUSE = "뚜렷한 원인 미확인"


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
    """응답에서 첫 JSON 객체/배열만 꺼낸다(코드블록·설명 섞임 대비)."""
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


def fallback_analysis(item):
    """AI 없이도 화면이 비지 않게 — 원문 제목 그대로, 원인은 '미확인'으로 정직하게."""
    return {
        "title_ko": item["title"],
        "why": UNKNOWN_CAUSE,
        "confidence": "미확인",
        "sectors": rule_sectors(item),
        "summary": clean_text(item.get("summary_orig") or "", 90),
        "analyzed_by": "fallback",
    }


RULE_SECTOR_TERMS = [
    ("AI·반도체", r"(반도체|삼성전자|SK하이닉스|엔비디아|nvidia|hbm|파운드리|ai|인공지능|칩|chip)"),
    ("2차전지", r"(2차전지|배터리|battery|양극재|음극재|리튬|전기차)"),
    ("방산", r"(방산|방위|무기|수출 계약|한화에어로|k-방산|defen[cs]e)"),
    ("바이오", r"(바이오|제약|임상|신약|바이오시밀러|fda)"),
    ("금융", r"(은행|증권|보험|금융지주|예금|대출|kb금융|신한지주)"),
    ("자동차", r"(자동차|현대차|기아|완성차|전기차 판매)"),
    ("조선", r"(조선|선박|수주잔고|hd현대중공업)"),
    ("에너지·화학", r"(정유|화학|유가|원유|wti|석유|가스|opec)"),
    ("유통·소비", r"(유통|소비|백화점|편의점|면세|카드 매출)"),
    ("인터넷·플랫폼", r"(플랫폼|네이버|카카오|구글|메타|쿠팡|이커머스)"),
    ("매크로", r"(금리|물가|환율|고용|연준|fed|fomc|cpi|관세|정책|경기|gdp)"),
]


def rule_sectors(item):
    blob = "%s %s" % (item.get("title", ""), item.get("summary_orig", ""))
    for name, pattern in RULE_SECTOR_TERMS:
        if re.search(pattern, blob, re.I):
            return [name]
    return ["매크로"]


def build_issue_prompt(chunk):
    lines = []
    for index, item in enumerate(chunk, 1):
        lines.append(
            "[%d] 매체: %s | 시장: %s | 시각: %s\n제목: %s\n원문 요약: %s"
            % (index, item["source"], "국내" if item["market"] == "domestic" else "해외",
               item.get("published_kst") or "미상", item["title"],
               (item.get("summary_orig") or "(원문 요약 없음)")[:420])
        )
    body = "\n\n".join(lines)
    return (
        "다음 증시 관련 기사 %d건을 분석해 JSON 배열로만 답하세요. 각 항목 키:\n"
        "- id: 입력 번호(정수)\n"
        "- title_ko: 한국어 제목 34자 이내. 영어 기사는 자연스러운 한국어로 옮기고, "
        "기업·지수·제품 이름은 원문 표기(NVIDIA, S&P500 등) 유지\n"
        "- why: '무엇 때문에 주가·지수가 움직였는지' 한 줄 60자 이내. "
        "원문에 원인이 적혀 있으면 그대로, 제목·요약으로 미루어 알 수 있으면 근거 표현을 넣어 쓰고, "
        "정말 알 수 없을 때만 정확히 \"%s\" 라고만 쓴다\n"
        "- confidence: \"원문 근거\"(원문에 원인·수치가 명시) / \"추정\"(정황상 원인을 짐작할 수 있음) / \"미확인\"(원인을 알 수 없음)\n"
        "- sectors: 다음 중 1~2개 — %s\n"
        "- summary: 기사 핵심 한 문장 70자 이내(수치는 원문에 있는 것만)\n\n"
        "%s\n\n"
        "출력: [{\"id\":1,\"title_ko\":\"...\",\"why\":\"...\",\"confidence\":\"...\","
        "\"sectors\":[\"...\"],\"summary\":\"...\"}]"
        % (len(chunk), UNKNOWN_CAUSE, ", ".join(SECTORS), body)
    )


def analyze_news(items, api_key, cache, max_calls=AI_MAX_CALLS):
    """기사별 한 줄 원인·섹터. 캐시 → EXAONE → 폴백 순서."""
    for item in items:
        cached = cache.get(CACHE_VERSION + "|" + item["id"])
        if cached and cached.get("title_ko") and cached.get("why"):
            item.update({k: cached[k] for k in ("title_ko", "why", "confidence", "sectors", "summary")
                         if k in cached})
            item["analyzed_by"] = "cache"
        else:
            item.update(fallback_analysis(item))

    pending = [item for item in items if item.get("analyzed_by") == "fallback"][:AI_ITEM_LIMIT]
    if not api_key or not pending:
        print("  [요약] EXAONE 호출 없음(키 %s, 대기 %d건) — 폴백 사용"
              % ("있음" if api_key else "없음/꺼짐", len(pending)))
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
                content, finish = call_exaone(prompt, api_key, max_tokens=4000)
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
                "summary": clean_text(row.get("summary") or "", 120),
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


def build_briefing_prompt(market_label, index_rows, news_rows, moves, calendar_rows):
    index_lines = "\n".join(
        "- %s: %s (%+.2f%%) · 현지 %s" % (row["name"], format_value(row["value"]), row["changePct"] or 0,
                                          row["lastTradingDate"])
        for row in index_rows if row.get("value") is not None)
    news_lines = "\n".join("- %s" % (row.get("title_ko") or row["title"]) for row in news_rows[:8])
    move_lines = "\n".join("- %s %+.2f%%" % (row["name"], row["changePct"] or 0) for row in moves[:5])
    cal_lines = "\n".join("- %s %s %s %s" % (row["date"], row.get("timeKst") or "시간 미정",
                                             row["title"], row.get("note") or "")
                          for row in (calendar_rows or [])[:4]) or "- 없음"
    return (
        "아래 자료만 근거로 %s 마감 시황을 3줄로 쓰세요. JSON 배열 [\"...\",\"...\",\"...\"] 만 출력합니다.\n\n"
        "[지수]\n%s\n\n[주요 종목]\n%s\n\n[오늘 기사 제목]\n%s\n\n[다가오는 일정]\n%s\n\n"
        "규칙:\n"
        "- 1줄: 지수 마감 수치와 등락률(위 [지수] 값만 사용)\n"
        "- 2줄: 오늘 시장을 움직인 이슈. 원인이 기사 제목에 드러날 때만 쓰고, 아니면 정확히 \"%s\"라고 쓴다\n"
        "- 3줄: 아래 일정 중 가장 가까운 하나를 '날짜·시각·내용'으로 안내\n"
        "- 각 줄 45~75자, '~했다' 체, 이모지·전망·추측 금지"
        % (market_label, index_lines or "- 없음", move_lines or "- 없음",
           news_lines or "- 없음", cal_lines, UNKNOWN_CAUSE)
    )


def format_value(value):
    if value is None:
        return "-"
    return "{:,.2f}".format(value)


def morning_lines(market, indices, calendar, fx, bigtech):
    """아침 점검 3줄 — AI 없이 지수·일정·환율에서 사실만 골라 만든다."""
    rows = [row for row in indices if row["market"] == market and row.get("value") is not None]
    lines = []
    if rows:
        lines.append(" · ".join("%s %s(%+.2f%%)" % (row["name"], format_value(row["value"]),
                                                   row["changePct"] or 0) for row in rows[:2]) + " 종가에서 출발")
    own_events = [row for row in (calendar or []) if (row["region"] == "국내") == (market == "domestic")]
    if own_events:
        event = own_events[0]
        lines.append("%s %s %s" % (event["date"][5:].replace("-", "/"),
                                   event.get("timeKst") or "시간 미정", event["title"]))
    if market == "domestic" and fx:
        row = fx[0]
        lines.append("원/달러 %s원(%+.2f%%) · 지연 시세" % (format_value(row.get("value")), row.get("changePct") or 0))
    elif market == "global" and bigtech:
        top = sorted([row for row in bigtech if row.get("changePct") is not None],
                     key=lambda item: abs(item["changePct"]), reverse=True)[0]
        lines.append("빅테크 %s %+.2f%% (전일 미국장 종가)" % (top["name"], top["changePct"]))
    while len(lines) < 3:
        lines.append("원인이 확인되지 않은 움직임은 '뚜렷한 원인 미확인'으로 표시")
    return lines[:3]


def key_headline(news_rows):
    """마감 시황 3줄에 넣을 대표 헤드라인 — 지수·반도체가 제목에 있는 기사를 먼저 고른다."""
    markers = ("코스피", "코스닥", "나스닥", "S&P500", "반도체", "증시")
    for row in news_rows:
        title = row.get("title_ko") or row["title"]
        if any(marker in title for marker in markers):
            return title
    return (news_rows[0].get("title_ko") or news_rows[0]["title"]) if news_rows else ""


def fallback_briefing(market_label, index_rows, news_rows):
    close = []
    for row in index_rows[:2]:
        if row.get("value") is None:
            continue
        close.append("%s %s (%+.2f%%)로 마감" % (row["name"], format_value(row["value"]),
                                                row["changePct"] or 0))
    headline = key_headline(news_rows)
    if headline:
        close.append("헤드라인: %s" % headline[:60])
    while len(close) < 3:
        close.append("수집된 기사로 확인된 추가 시황 없음")
    return close[:3]


def build_briefings(indices, bigtech, news, api_key, calendar=None, fx=None):
    domestic_idx = [row for row in indices if row["market"] == "domestic"]
    global_idx = [row for row in indices if row["market"] == "global"]
    domestic_news = [row for row in news if row["market"] == "domestic"][:8]
    global_news = [row for row in news if row["market"] == "global"][:8]
    top_movers = sorted([row for row in bigtech if row.get("changePct") is not None],
                        key=lambda row: abs(row["changePct"]), reverse=True)[:5]

    briefing = {
        "domestic": {
            "close": fallback_briefing("국내", domestic_idx, domestic_news),
            "morning": morning_lines("domestic", indices, calendar or [], fx or [], bigtech),
        },
        "global": {
            "close": fallback_briefing("해외", global_idx, global_news),
            "morning": morning_lines("global", indices, calendar or [], fx or [], bigtech),
        },
        "analyzed_by": {"domestic": "fallback", "global": "fallback"},
    }
    if not api_key:
        return briefing

    for key, label, idx, rows, moves in (
            ("domestic", "국내(코스피·코스닥)", domestic_idx, domestic_news, []),
            ("global", "해외(미국)", global_idx, global_news, top_movers)):
        prompt = build_briefing_prompt(label, idx, rows, moves, calendar)
        content = None
        for attempt in range(2):
            try:
                content, finish = call_exaone(prompt, api_key, max_tokens=6000)
                if (content or "").strip():
                    break
                print("  [브리핑] 빈 응답(finish=%s)" % finish)
                content = None
            except urllib.error.HTTPError as exc:
                if exc.code in (401, 403):
                    print("  [브리핑] 키 인증 실패 → 폴백")
                    return briefing
                time.sleep(20 if exc.code == 429 else 4 * (attempt + 1))
            except Exception as exc:  # noqa: BLE001
                print("  [브리핑] 오류 %s: %s" % (type(exc).__name__, exc))
                time.sleep(2)
        parsed = parse_json_block(content) if content else None
        if isinstance(parsed, dict):
            parsed = parsed.get("close") or parsed.get("lines")
        lines = [clean_text(line, 90) for line in (parsed or [])
                 if isinstance(line, str) and clean_text(line, 90)]
        if len(lines) >= 2:
            briefing[key]["close"] = lines[:3]
            briefing["analyzed_by"][key] = "exaone"
            print("  [브리핑] %s 완료" % label)
        else:
            print("  [브리핑] %s 줄 수 부족 → 폴백" % label)
        time.sleep(1.8)
    return briefing


# ---------------------------------------------------------------------------
# 5) 조립
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


def assemble(now, news, indices, bigtech, fx, calendar, briefing, ai_stats, sources):
    domestic_session = session_state("domestic", indices, now)
    global_session = session_state("global", indices, now)
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
            "summary": item.get("summary") or "",
            "source": item["source"],
            "sourceSection": item.get("section") or "",
            "url": item["url"],
            "publishedKst": item.get("published_kst") or "",
            "analyzedBy": item.get("analyzed_by") or "fallback",
        })
    notes = [
        "지수·종목 값은 Yahoo Finance 지연 시세이며 참고용입니다. 실제 주문·판단의 근거로 쓰지 마세요.",
        "뉴스는 제목·한 줄 요약·원문 링크만 보여 줍니다. 기사 전문과 저작권은 각 매체에 있습니다.",
        "원인이 원문에 없으면 '뚜렷한 원인 미확인'으로 표시합니다. 추측으로 채우지 않습니다.",
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
        "sessions": {"domestic": domestic_session, "global": global_session},
        "indices": indices,
        "bigtech": bigtech,
        "fx": fx,
        "briefing": briefing,
        "issues": issues,
        "sectors": build_sector_board(news),
        "calendar": calendar,
    }


def validate(payload):
    """내보내기 전 최소 검증 — 빈 화면·깨진 링크를 여기서 막는다."""
    problems = []
    if not payload["indices"]:
        problems.append("지수 시세 0건")
    if len(payload["issues"]) < 6:
        problems.append("기사 %d건(6건 미만)" % len(payload["issues"]))
    if not payload["calendar"]:
        problems.append("일정 0건")
    for issue in payload["issues"]:
        if not issue["url"].startswith("https://") and not issue["url"].startswith("http://"):
            problems.append("기사 링크 형식: %s" % issue["id"])
        if issue["confidence"] not in CONFIDENCE_VALUES:
            problems.append("confidence 값: %s" % issue["id"])
        if issue["confidence"] == "미확인" and issue["why"] != UNKNOWN_CAUSE:
            problems.append("미확인인데 원인 문장 있음: %s" % issue["id"])
        if any(name not in SECTORS for name in issue["sectors"]):
            problems.append("섹터 값: %s" % issue["id"])
    for row in payload["calendar"]:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", row["date"]):
            problems.append("일정 날짜: %s" % row["id"])
    return problems


def crawl(use_ai=True, out_path=None, now=None):
    now = now or now_kst()
    print("=== [증시 이슈] 수집 시작 %s ===" % kst_text(now))
    sources = []

    print("[1/4] 시세")
    indices, bigtech, fx = collect_quotes(sources)

    print("[2/4] 뉴스")
    news = collect_news(now, sources)

    print("[3/4] 공식 일정")
    calendar = collect_calendar(now, sources)

    print("[4/4] 요약")
    api_key = get_api_key() if use_ai else None
    cache = load_cache()
    ai_stats = analyze_news(news, api_key, cache)
    briefing = build_briefings(indices, bigtech, news, api_key if ai_stats.get("used") else None,
                               calendar=calendar, fx=fx)
    if ai_stats.get("analyzed"):
        ai_stats["used"] = True
    ai_stats["model"] = "k-exaone_v2.5" if ai_stats.get("used") else ""

    payload = assemble(now, news, indices, bigtech, fx, calendar, briefing, ai_stats, sources)
    problems = validate(payload)
    for problem in problems:
        print("  [검증] %s" % problem)

    target = out_path or OUT_JSON
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print("-> 'market_data.json' 저장 완료 (기사 %d건 · 지수 %d · 종목 %d · 일정 %d건 · AI %s)"
          % (len(payload["issues"]), len(indices), len(bigtech), len(calendar),
             "%d건" % ai_stats.get("analyzed", 0) if ai_stats.get("used") else "폴백"))
    return payload


def analyze_existing(path=None, max_calls=AI_MAX_CALLS, now=None, skip_briefing=False):
    """이미 저장된 market_data.json 의 기사를 EXAONE 으로 이어서 분석한다(수집 없이).

    수집과 요약을 나눠 실행하면 한 번의 실행 시간을 짧게 유지할 수 있고,
    중간에 끊겨도 캐시(market_cache.json) 덕분에 다음 실행이 이어 간다.
    """
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
            "summary_orig": issue.get("summary") or "",
            "url": issue["url"],
            "sectors": issue.get("sectors"),
        })
    cache = load_cache()
    stats = analyze_news(news, get_api_key(), cache, max_calls=max_calls)
    by_id = {item["id"]: item for item in news}
    for issue in payload["issues"]:
        item = by_id[issue["id"]]
        issue.update({
            "title": item.get("title_ko") or issue["title"],
            "why": item.get("why") or issue["why"],
            "confidence": item.get("confidence") or issue["confidence"],
            "sectors": item.get("sectors") or issue["sectors"],
            "summary": item.get("summary") or issue["summary"],
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

    def _write():
        problems = validate(payload)
        for problem in problems:
            print("  [검증] %s" % problem)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    # 기사 분석 결과를 먼저 저장한다 — 브리핑에서 시간이 끊겨도 분석분은 남는다.
    _write()

    if stats["used"] and not skip_briefing:
        briefing = build_briefings(payload["indices"], payload["bigtech"], news, get_api_key(),
                                   calendar=payload.get("calendar") or [], fx=payload.get("fx") or [])
        # 이미 EXAONE 으로 만든 브리핑은 유지하고, 이번에 성공한 것만 갈아 끼운다.
        for key in ("domestic", "global"):
            if (briefing.get("analyzed_by") or {}).get(key) == "exaone":
                payload["briefing"][key] = briefing[key]
                payload["briefing"].setdefault("analyzed_by", {})[key] = "exaone"
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
    parser.add_argument("--no-briefing", action="store_true", help="이어서 분석할 때 브리핑 호출은 건너뛴다")
    args = parser.parse_args(argv)
    if args.ai_only:
        analyze_existing(args.out, max_calls=args.max_calls, skip_briefing=args.no_briefing)
        return 0
    crawl(use_ai=not args.no_ai, out_path=args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

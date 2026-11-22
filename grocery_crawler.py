#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""grocery_crawler.py — 장보기 타이밍(grocery.html) 원본 수집기.

소스 (공식 · 인증키 불필요)
  aT 한국농수산식품유통공사 KAMIS(농산물유통정보) 「간편가격정보 > 소매가격」
  https://www.kamis.or.kr/customer/info/retail/period.do
  · 로그인·Open-API 인증키 없이 GET 파라미터(action=daily·기간·지역·품목)로
    일별 소매가격 표를 서버에서 렌더링해 내려준다.
  · KAMIS Open-API(xml.do)는 cert_key 없이 호출하면 에러 900(인증키 필요)이라 쓰지 않는다.
  · robots.txt 는 통합검색 경로만 막고 있어 이 경로는 수집 허용 범위다(2026-11-22 확인).

수집 방식
  · 지역: 서울(1101) · 수원(3111) — KAMIS 소매가격 조사 지역 코드
  · 품목: 8종(계란·대파·배추·무·양파·시금치·애호박·사과)
  · 기간: 오늘 포함 최근 28일(4주) 창 → 주중 조사값 20회 안팎
  · 축산물(계란)은 지역 구분 없이 전국 단일 조사라 한 번만 받아 양 지역에 같은 값을 쓴다.
  · 요청 사이 0.6초 간격, 응답은 net_guard 로 크기 상한을 두고 읽는다.

산출
  grocery_data.json — 품목·지역별 최신 조사값, 28일 관측치, 중앙값, 중앙값 대비 등락률,
  전월·전년·평년 비교, 공식 출처 링크. 값은 사이트에 적힌 그대로이며 어떤 수치도 만들지 않는다.

  수집이 실패한 품목은 직전 grocery_data.json 값을 그대로 승계하고 stale=true 로 표시한다.
  승계값에는 observedDate(실제 조사일) · fetchedDate(기준일) · staleDays(경과일)를 다시 계산해
  넣는다. 승계가 여러 번 이어져도 경과일이 1일로 굳지 않고 실제 조사일에서 매번 세진다.
  승계할 값도 없으면 그 품목을 빼고 경고만 남긴다(가짜 값 금지).

실행
  python3 grocery_crawler.py                # 수집 + grocery_data.json 저장
  python3 grocery_crawler.py --check        # 수집만 하고 저장하지 않음(점검용)
"""
import argparse
import json
import os
import re
import statistics
import sys
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

from net_guard import MAX_HTML_BYTES, open_http, read_limited

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "grocery_data.json")
KST = timezone(timedelta(hours=9))

SOURCE_BASE = "https://www.kamis.or.kr/customer/info/retail/period.do"
SOURCE_LABEL = "aT 한국농수산식품유통공사 KAMIS 농산물유통정보 · 간편가격정보 소매가격"
SOURCE_ROOT = "https://www.kamis.or.kr/customer/info/retail/period.do"
HOWTO_URL = "https://www.kamis.or.kr/customer/price/knowhow/knowhow.do"
OPENAPI_URL = "https://www.kamis.or.kr/customer/info/retail/period.do"

WINDOW_DAYS = 28
REQUEST_GAP = 0.6   # 요청 사이 간격(초) — 같은 사이트를 연달아 두드리지 않는다
REQUEST_TIMEOUT = 25
MIN_OBSERVATIONS = 5        # 28일 창 최소 관측치(주중 조사 4주 ≈ 20회)
STALE_DAYS = 7              # 최신 조사값이 이보다 오래되면 경고를 남긴다(값은 그대로 표시)
MIN_ITEMS = 6               # 빌더가 요구하는 최소 품목 수

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept-Language": "ko-KR,ko;q=0.9",
}

REGIONS = [
    {"id": "seoul", "name": "서울", "code": "1101"},
    {"id": "suwon", "name": "수원", "code": "3111"},
]

# cat = KAMIS 부류 코드, code = 품목 코드. KAMIS 기본 품종(첫 번째)을 쓴다.
# scope = "national" 이면 지역 구분 없는 전국 단일 조사(축산물).
ITEMS = [
    {"id": "egg", "name": "계란", "cat": "500", "code": "9903", "scope": "national",
     "short": "계란 한 판(10구)"},
    {"id": "greenonion", "name": "대파", "cat": "200", "code": "246", "short": "대파 1kg"},
    {"id": "cabbage", "name": "배추", "cat": "200", "code": "211", "short": "배추 1포기"},
    {"id": "radish", "name": "무", "cat": "200", "code": "231", "short": "무 1개"},
    {"id": "onion", "name": "양파", "cat": "200", "code": "245", "short": "양파 1kg"},
    {"id": "spinach", "name": "시금치", "cat": "200", "code": "213", "short": "시금치 100g"},
    {"id": "zucchini", "name": "애호박", "cat": "200", "code": "224", "short": "애호박 1개"},
    {"id": "apple", "name": "사과", "cat": "400", "code": "411", "short": "사과 10개"},
]

DATE_ROW_RE = re.compile(r"^20\d\d\.\d\d\.\d\d$")


# ---------------------------------------------------------------------------
# 수집
# ---------------------------------------------------------------------------
def _window(today):
    return today - timedelta(days=WINDOW_DAYS - 1), today


def source_url(item, region, start, end, kind_code=None):
    params = [
        ("action", "daily"),
        ("startday", start.strftime("%Y.%m.%d")),
        ("endday", end.strftime("%Y.%m.%d")),
        ("itemcategorycode", item["cat"]),
        ("itemcode", item["code"]),
    ]
    if kind_code:
        params.append(("kindcode", kind_code))
    params += [("productrankcode", "0"), ("countycode", region["code"])]
    return SOURCE_BASE + "?" + urllib.parse.urlencode(params)


def fetch(url):
    req = open_http(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    with req as resp:
        return read_limited(resp, MAX_HTML_BYTES).decode("utf-8", "replace")


def _text(fragment):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", fragment)).strip()


def parse_page(html):
    """KAMIS 일별 소매가격 표 → 제목 정보 + 관측치 목록."""
    title_match = re.search(r'<span id="title_1">(.*?)</span>', html, re.S)
    title = _text(title_match.group(1)) if title_match else ""

    kind = grade = unit = ""
    if title:
        m_grade = re.search(r"등급\s*:\s*([^,]*?)\s*,", title)
        m_unit = re.search(r"단위\s*:\s*(.+)$", title)
        grade = m_grade.group(1).strip() if m_grade else ""
        unit = m_unit.group(1).strip() if m_unit else ""
        head = title.split(",")[0]
        parts = [p.strip() for p in head.split("/")]
        if len(parts) >= 3:
            kind = parts[2]
        elif len(parts) == 2:
            kind = ""

    used_kind = re.search(r'id="kindcode"\s+name="kindcode"\s+value="([^"]*)"', html)
    used_kind = used_kind.group(1) if used_kind else ""

    tbody = html.split("<tbody>")[1].split("</tbody>")[0] if "<tbody>" in html else ""
    observations, comparisons = [], {}
    for row in re.finditer(r"<tr>(.*?)</tr>", tbody, re.S):
        cells = [_text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row.group(1), re.S)]
        if len(cells) < 2:
            continue
        label, raw_price = cells[0], cells[1]
        pct = cells[2] if len(cells) > 2 else ""
        if DATE_ROW_RE.match(label):
            price = _int(raw_price)
            if price is None:
                continue
            observations.append({
                "date": label.replace(".", "-"),
                "price": price,
                "changePctWeb": _float(pct),
            })
        elif label:
            comparisons[label.replace(" ", "")] = _int(raw_price)

    return {
        "title": title,
        "kind": kind,
        "grade": grade,
        "unit": unit,
        "kindCode": used_kind,
        "observations": observations,
        "comparisons": comparisons,
    }


def _int(text):
    if text is None:
        return None
    cleaned = re.sub(r"[^0-9]", "", text)
    return int(cleaned) if cleaned else None


def _float(text):
    try:
        return float((text or "").strip())
    except ValueError:
        return None


def summarize(parsed, today, start=None, end=None):
    """관측치 → 최신값·28일 중앙값·등락률 등 화면에 쓰는 수치.

    KAMIS 화면은 요청한 기간에 걸친 주(週)의 값을 한 줄 더 내려줄 때가 있어
    (예: 10-26 부터 요청했는데 10-23 값이 함께 옴) 28일 창 안의 값만 남기고 계산한다.
    """
    obs = sorted(parsed["observations"], key=lambda row: row["date"])
    if start and end:
        obs = [row for row in obs
               if start.isoformat() <= row["date"] <= end.isoformat()]
    if not obs:
        return None
    prices = [row["price"] for row in obs]
    median = statistics.median(prices)
    latest = obs[-1]
    prev = obs[-2] if len(obs) > 1 else None
    gap = (latest["price"] - median) / median * 100 if median else 0.0
    latest_date = datetime.strptime(latest["date"], "%Y-%m-%d").date()
    comparisons = parsed["comparisons"]
    return {
        "latest": {"date": latest["date"], "price": latest["price"]},
        "prev": {"date": prev["date"], "price": prev["price"]} if prev else None,
        "median": int(median) if float(median).is_integer() else round(median, 1),
        "gapPct": round(gap, 1),
        "min": {"date": obs[prices.index(min(prices))]["date"], "price": min(prices)},
        "max": {"date": obs[prices.index(max(prices))]["date"], "price": max(prices)},
        "observations": len(obs),
        "series": [{"d": row["date"], "p": row["price"]} for row in obs],
        "compare": {
            "prevMonth": comparisons.get("전월순"),
            "prevYear": comparisons.get("전년순"),
            # KAMIS 표의 마지막 비교행은 '순 평년' → 공백 제거 시 '순평년' 이다.
            "avgYear": comparisons.get("순평년") or comparisons.get("평년순"),
        },
        "compareRaw": comparisons,
        # 조사일 기준 경과일 — 수집에 성공한 값은 stale=false, 승계값은 _inherit 에서 다시 계산한다.
        "observedDate": latest["date"],
        "fetchedDate": today.isoformat(),
        "stale": False,
        "staleDays": (today - latest_date).days,
    }


# ---------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------
def collect(today=None):
    today = today or datetime.now(KST).date()
    start, end = _window(today)
    previous = load_previous()

    items_out, warnings, requests = [], [], 0
    last_kind = {}

    for item in ITEMS:
        regions = REGIONS if item.get("scope") != "national" else REGIONS[:1]
        by_region = {}
        meta = None
        for region in regions:
            url = source_url(item, region, start, end, last_kind.get(item["id"]))
            try:
                parsed = parse_page(fetch(url))
                requests += 1
                if not parsed["observations"] and item["id"] not in last_kind and requests > 1:
                    # 품종 코드가 비어 기본값이 어긋난 경우: 코드 없이 한 번 더
                    parsed = parse_page(fetch(source_url(item, region, start, end)))
                    requests += 1
                if not parsed["observations"]:
                    raise ValueError("조사값이 없습니다")
                meta = parsed
                if parsed["kindCode"]:
                    last_kind[item["id"]] = parsed["kindCode"]
                stats = summarize(parsed, today, start, end)
                if stats["observations"] < MIN_OBSERVATIONS:
                    warnings.append("%s/%s 관측치 %d회(최소 %d회 미만)"
                                    % (item["name"], region["name"], stats["observations"], MIN_OBSERVATIONS))
                if stats["staleDays"] > STALE_DAYS:
                    warnings.append("%s/%s 최신 조사값이 %d일 전(%s) — KAMIS 조사 지연 가능"
                                    % (item["name"], region["name"], stats["staleDays"],
                                       stats["observedDate"]))
                stats["sourceUrl"] = url
                by_region[region["id"]] = stats
            except Exception as exc:  # noqa: BLE001 - 한 품목 실패가 전체를 막지 않는다
                warnings.append("%s/%s 수집 실패: %s" % (item["name"], region["name"], exc))
                inherited = _inherit(previous, item["id"], region["id"], today)
                if inherited:
                    warnings.append("%s/%s 직전 수집값 승계(%s)"
                                    % (item["name"], region["name"], inherited["latest"]["date"]))
                    by_region[region["id"]] = inherited
            finally:
                time.sleep(REQUEST_GAP)

        if not by_region:
            warnings.append("%s 제외 — 수집값도 승계값도 없습니다" % item["name"])
            continue

        if item.get("scope") == "national":
            # 축산물은 전국 단일 조사 — 지역 코드를 붙이지 않은 출처 링크로 맞춘다.
            only = by_region[REGIONS[0]["id"]]
            by_region = {}
            for region in REGIONS:
                stats = json.loads(json.dumps(only))
                stats["sourceUrl"] = source_url(item, {"code": ""}, start, end,
                                                last_kind.get(item["id"]))
                by_region[region["id"]] = stats

        entry = {
            "id": item["id"],
            "name": item["name"],
            "short": item["short"],
            "scope": item.get("scope", "regional"),
            "kind": meta["kind"] if meta else _first_meta(previous, item["id"], "kind", ""),
            "grade": meta["grade"] if meta else _first_meta(previous, item["id"], "grade", ""),
            "unit": meta["unit"] if meta else _first_meta(previous, item["id"], "unit", ""),
            "byRegion": by_region,
        }
        if not entry["unit"]:
            warnings.append("%s 규격(단위)을 읽지 못했습니다" % item["name"])
        items_out.append(entry)

    if len(items_out) < MIN_ITEMS:
        raise SystemExit("품목이 %d개뿐입니다(최소 %d개). 수집 상태를 확인하세요: %s"
                         % (len(items_out), MIN_ITEMS, "; ".join(warnings[-4:])))

    return {
        "generated": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
        "window": {"start": start.isoformat(), "end": end.isoformat(), "days": WINDOW_DAYS},
        "regionList": [{"id": r["id"], "name": r["name"], "code": r["code"]} for r in REGIONS],
        "source": {
            "label": SOURCE_LABEL,
            "url": SOURCE_ROOT,
            "howtoUrl": HOWTO_URL,
            "note": ("KAMIS 공개 소매가격 페이지에서 기간·지역·품목을 지정해 받은 일별 조사값. "
                     "조사는 주중에 이뤄지며 축산물(계란)은 지역 구분 없이 전국 단일 조사다."),
        },
        "items": items_out,
        "warnings": warnings,
    }


def _inherit(previous, item_id, region_id, today):
    if not previous:
        return None
    for item in previous.get("items", []):
        if item.get("id") == item_id:
            stats = (item.get("byRegion") or {}).get(region_id)
            if stats:
                carried = json.loads(json.dumps(stats))
                # 승계값의 경과일은 '직전 수집 때의 값'이 아니라 실제 조사일에서 다시 센다.
                # (이전 실행의 staleDays 를 그대로 두면 실패가 이어져도 1일로 굳는다)
                observed = carried.get("observedDate") or (carried.get("latest") or {}).get("date")
                if not observed:
                    return None
                observed_date = datetime.strptime(observed, "%Y-%m-%d").date()
                carried["observedDate"] = observed_date.isoformat()
                carried["fetchedDate"] = today.isoformat()
                carried["staleDays"] = (today - observed_date).days
                carried["stale"] = True
                carried["inherited"] = True
                return carried
    return None


def _first_meta(previous, item_id, field, default):
    if not previous:
        return default
    for item in previous.get("items", []):
        if item.get("id") == item_id and item.get(field):
            return item[field]
    return default


def load_previous():
    try:
        with open(DATA_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save(data):
    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="KAMIS 소매가격 수집 → grocery_data.json")
    parser.add_argument("--check", action="store_true", help="수집만 확인하고 저장하지 않음")
    args = parser.parse_args(argv)

    data = collect()
    if not args.check:
        save(data)
        print("-> 'grocery_data.json' 저장 완료 (품목 %d개 · %s ~ %s)"
              % (len(data["items"]), data["window"]["start"], data["window"]["end"]))
    for item in data["items"]:
        seoul = item["byRegion"]["seoul"]
        print("  %-4s %s %s/%s — 최신 %s원(%s) · 28일 중앙값 %s원 · %+.1f%%"
              % (item["name"], item["unit"], item["kind"] or "-", item["grade"] or "-",
                 format(seoul["latest"]["price"], ","), seoul["latest"]["date"],
                 format(seoul["median"], ","), seoul["gapPct"]))
    for warning in data["warnings"]:
        print("  [warn] %s" % warning)
    return 0


if __name__ == "__main__":
    sys.exit(main())

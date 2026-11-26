# -*- coding: utf-8 -*-
"""차트 추리실 합성 OHLCV 회귀 테스트.

확인하는 것
- chart_data.json·chart.html 에 외부 시세(Yahoo Finance) 재배포 흔적이 없다.
- 16문항의 OHLCV 무결성(고가·저가·시가·종가·거래량·날짜 정렬)과 가려진 구간 길이.
- 정답이 만들어진 종가와 정확히 맞고, 보기 4개가 겹치지 않는다.
- 해설에 적힌 시작·종료 종가와 등락률이 실제 데이터와 같다.
- 생성기가 같은 입력에서 같은 데이터를 다시 만든다(재현성).
- 화면에 '합성 학습 차트' 표기가 있다.
- 패턴 문항은 보이는 구간이 그 패턴으로 읽히는지 생성기 검증 규칙을 다시 돌린다.

실행: python3 tests/test_chart_synthetic.py
"""
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import chart_generate_data as gen  # noqa: E402

DATA_PATH = os.path.join(BASE_DIR, "chart_data.json")
HTML_PATH = os.path.join(BASE_DIR, "chart.html")

BANNED = (
    "yahoo", "finance.yahoo", "source_url", "액면분할",
    "코스피", "코스닥", "삼성전자", "엔비디아", "메타 플랫폼스", "애플", "마이크로소프트",
    "s&p 500", "나스닥", "비트코인", "닛케이", "원/달러", "금 선물", "vix 변동성",
)
TICKER_RE = re.compile(
    r"\b(?:NVDA|AAPL|MSFT|META|GOOGL|AMZN|TSLA|BTC-USD|KRW=X|\^KS11|\^KQ11|\^NDX|\^GSPC|\^N225|\^VIX|CL=F|GC=F|005930\.KS)\b")
CATEGORY_COUNTS = {"trend": 4, "breakout": 4, "level": 4, "volume": 4}


def load():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def fail(message):
    raise AssertionError(message)


def check_data(data):
    assert data.get("synthetic") is True, "chart_data.json 에 합성 표시가 없습니다"
    assert data.get("notice") and "합성" in data["notice"], "합성 고지 문구가 없습니다"
    blob = json.dumps(data, ensure_ascii=False).lower()
    hits = [word for word in BANNED if word in blob]
    assert not hits, "외부 시세 흔적이 남아 있습니다: %s" % hits
    assert not TICKER_RE.search(json.dumps(data, ensure_ascii=False)), \
        "chart_data.json 에 실제 티커가 남아 있습니다"

    cats = [c["key"] for c in data["categories"]]
    assert cats == list(CATEGORY_COUNTS), "분야 구성이 다릅니다: %s" % cats
    episodes = data["episodes"]
    assert len(episodes) == 16, "문항이 16개가 아닙니다: %d" % len(episodes)
    counts = {}
    for ep in episodes:
        counts[ep["category"]] = counts.get(ep["category"], 0) + 1
    assert counts == CATEGORY_COUNTS, "분야별 문항 수가 다릅니다: %s" % counts

    ids = [ep["id"] for ep in episodes]
    assert len(ids) == len(set(ids)), "문항 id 가 겹칩니다"

    max_move = {"1d": 0.0, "1wk": 0.0}
    for ep in episodes:
        eid = ep["id"]
        assert ep["synthetic"] is True and ep["data_note"], "%s: 합성 표기 누락" % eid
        assert ep["name"].startswith(ep["code"]), "%s: 코드와 이름이 어긋납니다" % eid
        bars = ep["bars"]
        split = ep["split_index"]
        assert 44 <= len(bars) <= 80, "%s: 봉 수 %d" % (eid, len(bars))
        assert split + 1 >= 30, "%s: 보이는 구간이 너무 짧습니다" % eid
        assert 10 <= len(bars) - split - 1 <= 25, "%s: 가려진 구간 %d" % (eid, len(bars) - split - 1)

        stamps = []
        for bar in bars:
            assert isinstance(bar, list) and len(bar) == 6, "%s: 봉 형식 %s" % (eid, bar)
            stamp, o, h, l, c, v = bar
            assert re.match(r"^\d{4}-\d{2}-\d{2}$", stamp), "%s: 날짜 형식 %s" % (eid, stamp)
            assert all(isinstance(x, (int, float)) for x in (o, h, l, c)), "%s: 가격 형식" % eid
            assert o > 0 and c > 0 and h > 0 and l > 0, "%s: 0 이하 가격" % eid
            assert h >= max(o, c) - 1e-9, "%s: 고가가 시가·종가보다 낮습니다 %s" % (eid, bar)
            assert l <= min(o, c) + 1e-9, "%s: 저가가 시가·종가보다 높습니다 %s" % (eid, bar)
            assert isinstance(v, int) and v > 0, "%s: 거래량 %s" % (eid, v)
            stamps.append(stamp)
        assert stamps == sorted(stamps) and len(set(stamps)) == len(stamps), "%s: 날짜 정렬" % eid
        assert ep["visible_until"] == stamps[split], "%s: 공개 시점 불일치" % eid
        assert ep["period"] == "%s ~ %s" % (stamps[0], stamps[-1]), "%s: 기간 표기" % eid
        for i in range(1, len(bars)):
            move = abs(bars[i][4] / bars[i - 1][4] - 1)
            max_move[ep["interval"]] = max(max_move[ep["interval"]], move)
        assert len(ep["explanation"]) >= 80, "%s: 해설이 너무 짧습니다" % eid

        ret = (bars[-1][4] / bars[split][4] - 1) * 100
        assert abs(ret - ep["future_return"]) < 0.06, "%s: future_return 불일치" % eid

        quiz = ep["quiz"]
        assert len(quiz["choices"]) == 4 and len(set(quiz["choices"])) == 4, "%s: 보기 4개" % eid
        assert 0 <= quiz["answer"] < 4, "%s: 정답 위치" % eid
        answer = quiz["choices"][quiz["answer"]]
        band_key, band_label = gen.band_for(ret / 100)
        if quiz["type"] == "next":
            assert quiz["band"] == band_key, "%s: 정답 구간 계산 불일치" % eid
            assert answer == band_label, "%s: 정답 문구 불일치" % eid
            assert quiz["prompt"].startswith("가려진 마지막 구간(%d봉)" % (len(bars) - split - 1)), \
                "%s: 문제 문구의 봉 수가 다릅니다" % eid
        elif quiz["type"] == "pattern":
            assert ep["pattern"] == answer, "%s: 패턴 정답 불일치" % eid
            assert all(choice in gen.PATTERN_POOL for choice in quiz["choices"]), "%s: 패턴 보기" % eid
            gen.verify_pattern(answer, bars, split)
        else:
            fail("%s: 알 수 없는 문제 유형 %s" % (eid, quiz["type"]))

        # 해설 속 수치가 실제 데이터와 같은지 — 시작/종료 종가와 등락률
        start_txt = gen._px(bars[split][4])
        end_txt = gen._px(bars[-1][4])
        assert start_txt in ep["explanation"] and end_txt in ep["explanation"], \
            "%s: 해설의 종가가 데이터와 다릅니다" % eid
        assert ("%.1f%%" % abs(ret)) in ep["explanation"], "%s: 해설의 등락률이 다릅니다" % eid
        assert band_label in ep["explanation"], "%s: 해설에 정답 구간 표기가 없습니다" % eid

    assert max_move["1d"] < 0.12, "일봉 한 봉 변동이 12%%를 넘습니다: %.1f%%" % (max_move["1d"] * 100)
    assert max_move["1wk"] < 0.20, "주봉 한 봉 변동이 20%%를 넘습니다: %.1f%%" % (max_move["1wk"] * 100)
    return episodes


def check_determinism(data):
    again = gen.build_dataset(write=False)["episodes"]
    assert json.dumps(again, ensure_ascii=False, sort_keys=True) == \
        json.dumps(data["episodes"], ensure_ascii=False, sort_keys=True), \
        "같은 코드로 다시 만들어도 데이터가 달라집니다(재현성 깨짐)"


def check_html(data):
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    low = html.lower()
    hits = [word for word in BANNED if word in low]
    assert not hits, "chart.html 에 외부 시세 흔적이 남아 있습니다: %s" % hits
    assert not TICKER_RE.search(html), "chart.html 에 실제 티커가 남아 있습니다"
    for phrase in ("합성 학습 차트", "실제 시세 아님", "합성 구간", "합성 학습 데이터"):
        assert phrase in html, "chart.html 에 '%s' 표기가 없습니다" % phrase
    for ep in data["episodes"]:
        assert '"id\\":\\"%s\\"' % ep["id"] in html or '"id":"%s"' % ep["id"] in html, \
            "chart.html 에 %s 문항이 없습니다" % ep["id"]
        assert ep["id"] in html, "chart.html 에 %s 문항이 없습니다" % ep["id"]
    assert "finance.yahoo" not in low and "target=\"_blank\"" not in html.split("revealSource")[1][:200], \
        "공개 영역에 외부 링크가 남아 있습니다"


def main():
    data = load()
    episodes = check_data(data)
    check_determinism(data)
    check_html(data)
    next_cnt = sum(1 for ep in episodes if ep["quiz"]["type"] == "next")
    pattern_cnt = sum(1 for ep in episodes if ep["quiz"]["type"] == "pattern")
    print("차트 추리실 합성 데이터 검증 통과: 문항 %d개(흐름 %d · 패턴 %d) · 봉 %d~%d"
          % (len(episodes), next_cnt, pattern_cnt,
             min(len(ep["bars"]) for ep in episodes), max(len(ep["bars"]) for ep in episodes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

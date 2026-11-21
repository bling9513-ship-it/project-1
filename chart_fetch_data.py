# -*- coding: utf-8 -*-
"""
차트 추리실(chart.html) 데이터 수집기.

Yahoo Finance 공개 일별/주별 시세에서 '문제로 쓸 과거 구간'만 잘라 chart_data.json 으로 저장한다.
- 차트에 그리는 값은 실제 과거 시세(시가·고가·저가·종가·거래량)이며, 가공·각색하지 않는다.
- 정답(가려진 다음 구간의 흐름)은 사람이 적지 않고 이 스크립트가 실제 종가로 계산해 붙인다.
- 네트워크가 없는 빌드 환경에서도 build_chart_html.py 가 돌도록, 결과는 저장소에 커밋되는
  chart_data.json 하나로 고정한다. (이 스크립트는 데이터를 새로 받을 때만 실행)

실행: python3 chart_fetch_data.py
"""
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "chart_data.json")
UA = "Mozilla/5.0 (compatible; InfosecArchiveChartData/1.0)"

CATEGORIES = [
    {"key": "domestic", "label": "국내 증시"},
    {"key": "bigtech", "label": "미국 빅테크"},
    {"key": "market", "label": "지수·원자재"},
    {"key": "event", "label": "금융 이벤트"},
]

# 다음 구간 흐름(정답)은 미리 적지 않는다 — 실제 종가로 계산해 구간 라벨을 고른다.
FLOW_BANDS = [
    ("surge", "10% 넘게 상승", lambda r: r >= 0.10),
    ("up", "2~10% 상승", lambda r: 0.02 <= r < 0.10),
    ("flat", "보합권(±2% 이내)", lambda r: -0.02 < r < 0.02),
    ("down", "2~10% 하락", lambda r: -0.10 < r <= -0.02),
    ("plunge", "10% 넘게 하락", lambda r: r <= -0.10),
]

EVENTS = (
    {
        "id": "ch-kospi-covid",
        "category": "domestic",
        "symbol": "^KS11",
        "interval": "1d",
        "name": "코스피 지수",
        "start": "2020-01-02",
        "end": "2020-04-17",
        "split": "2020-03-20",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 4주), 코스피는 어떻게 흘렀을까요?",
        "explanation": "2020년 3월 중순 코스피는 1,440선까지 밀렸다가 저점을 찍고, 각국 중앙은행의 유동성 공급과 진단검사 확대에 힘입어 4월 중순 1,900선 위로 반등했습니다. 폭락 뒤 첫 반등은 낙폭이 컸던 지수일수록 컸지만, 실물 충격이 확인되기 전이라 변동성도 함께 컸던 구간입니다.",
        "source": "Yahoo Finance ^KS11 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/%5EKS11/history",
    },
    {
        "id": "ch-samsung-peak",
        "category": "domestic",
        "symbol": "005930.KS",
        "interval": "1d",
        "name": "삼성전자",
        "start": "2020-10-12",
        "end": "2021-02-10",
        "split": "2021-01-13",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 4주), 이 종목의 주가는?",
        "explanation": "삼성전자는 2021년 1월 11일 장중 9만 6,800원으로 정점을 찍은 뒤, 외국인 순매도와 메모리 가격 고점 논쟁으로 2월 중순 8만 1,600원까지 밀렸습니다. 개인 투자자의 순매수가 이어졌지만 지수 대형주가 조정을 받으면 수급이 빠르게 돌아선 사례입니다.",
        "source": "Yahoo Finance 005930.KS 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/005930.KS/history",
    },
    {
        "id": "ch-kosdaq-peak",
        "category": "domestic",
        "symbol": "^KQ11",
        "interval": "1d",
        "name": "코스닥 지수",
        "start": "2021-06-01",
        "end": "2021-09-30",
        "split": "2021-08-10",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 7주), 코스닥은 어떻게 흘렀을까요?",
        "explanation": "코스닥은 2021년 8월 10일 1,060선을 넘어 연고점을 찍은 뒤, 한국은행의 기준금리 인상(8월 26일)과 2차전지·바이오 대형주의 차익 실현으로 9월 말 1,000선 아래로 내려왔습니다. 금리 인상 국면에서는 이익이 먼 성장주부터 조정이 온다는 점이 드러난 구간입니다.",
        "source": "Yahoo Finance ^KQ11 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/%5EKQ11/history",
    },
    {
        "id": "ch-kospi-bottom",
        "category": "domestic",
        "symbol": "^KS11",
        "interval": "1d",
        "name": "코스피 지수",
        "start": "2022-08-01",
        "end": "2022-11-18",
        "split": "2022-10-06",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 6주), 코스피는 어떻게 흘렀을까요?",
        "explanation": "코스피는 2022년 9월 30일 2,155까지 밀려 연중 저점을 만든 뒤, 10월 초 반등에 성공해 11월 중순 2,440선까지 올라왔습니다. 미국 물가 상승률이 꺾이기 시작하고 달러 강세가 진정되면서 외국인 수급이 돌아온 것이 반등의 배경이었습니다.",
        "source": "Yahoo Finance ^KS11 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/%5EKS11/history",
    },
    {
        "id": "ch-nvda-2018",
        "category": "bigtech",
        "symbol": "NVDA",
        "interval": "1d",
        "name": "엔비디아",
        "start": "2018-08-01",
        "end": "2018-11-16",
        "split": "2018-10-19",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 4주), 이 종목의 주가는?",
        "explanation": "2018년 가을 엔비디아는 암호화폐 채굴용 그래픽카드 수요가 사라지며 재고가 쌓였고, 11월 15일 실적 발표에서 데이터센터 매출까지 예상치를 밑돌자 하루 만에 18% 넘게 급락했습니다. 2018년 반도체 조정의 상징이 된 구간입니다(차트 가격은 이후 액면분할을 반영해 조정된 값).",
        "source": "Yahoo Finance NVDA 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/NVDA/history",
    },
    {
        "id": "ch-meta-2022",
        "category": "bigtech",
        "symbol": "META",
        "interval": "1d",
        "name": "메타 플랫폼스",
        "start": "2021-11-01",
        "end": "2022-03-14",
        "split": "2022-02-02",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 6주), 이 종목의 주가는?",
        "explanation": "메타는 2022년 2월 2일 실적 발표에서 일간 활성 이용자 감소와 메타버스 투자 확대를 함께 내놓았고, 다음 날 주가가 26% 폭락하며 시가총액 2,000억 달러가 사라졌습니다. 이후에도 3월까지 하락이 이어져 고점 대비 40% 넘게 빠졌습니다.",
        "source": "Yahoo Finance META 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/META/history",
    },
    {
        "id": "ch-aapl-2019",
        "category": "bigtech",
        "symbol": "AAPL",
        "interval": "1d",
        "name": "애플",
        "start": "2018-10-01",
        "end": "2019-01-31",
        "split": "2019-01-03",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 4주), 이 종목의 주가는?",
        "explanation": "애플은 2019년 1월 2일 중국 수요 부진을 이유로 분기 매출 전망을 낮췄고, 다음 날 주가가 10% 가까이 빠졌습니다. 그러나 1월 말 실적에서 아이폰 외 서비스 매출이 버텨 주자 저점 대비 16% 넘게 빠르게 회복했습니다(차트 가격은 액면분할 조정 기준).",
        "source": "Yahoo Finance AAPL 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/AAPL/history",
    },
    {
        "id": "ch-msft-2020",
        "category": "bigtech",
        "symbol": "MSFT",
        "interval": "1d",
        "name": "마이크로소프트",
        "start": "2019-12-02",
        "end": "2020-04-17",
        "split": "2020-03-20",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 4주), 이 종목의 주가는?",
        "explanation": "마이크로소프트는 2020년 3월 20일 137달러까지 밀렸다가, 재택근무로 클라우드 사용량이 늘면서 4월 중순 177달러까지 반등했습니다. 같은 기간 S&P500보다 빠르게 회복해, 원격 근무 수요가 실적으로 확인된 대표 사례가 됐습니다.",
        "source": "Yahoo Finance MSFT 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/MSFT/history",
    },
    {
        "id": "ch-gold-2011",
        "category": "market",
        "symbol": "GC=F",
        "interval": "1wk",
        "name": "금 선물(COMEX)",
        "start": "2010-11-01",
        "end": "2012-01-31",
        "split": "2011-09-06",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 5개월), 금 가격은 어떻게 흘렀을까요?",
        "explanation": "금은 2011년 9월 초 온스당 1,900달러를 넘어 사상 최고치를 찍은 뒤, 유럽 재정위기 대응과 미국의 추가 양적완화 기대가 후퇴하면서 이듬해 1월 1,700달러 아래로 내려왔습니다. 안전자산 수요는 금리가 오르면 빠르게 빠진다는 점을 보여 준 구간입니다.",
        "source": "Yahoo Finance GC=F 주별 시세",
        "source_url": "https://finance.yahoo.com/quote/GC%3DF/history",
    },
    {
        "id": "ch-oil-2020",
        "category": "market",
        "symbol": "CL=F",
        "interval": "1d",
        "name": "WTI 원유 선물",
        "start": "2020-01-16",
        "end": "2020-05-20",
        "split": "2020-04-21",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 4주), 유가 흐름은?",
        "explanation": "2020년 4월 20일 WTI 5월물은 저장 공간이 사라지며 사상 처음 마이너스 가격(-37.63달러)으로 만기됐습니다. 이후 6월물로 넘어가며 5월 중순 33달러까지 급반등했는데, 감산 합의와 수요 회복 기대가 반영된 것입니다.",
        "source": "Yahoo Finance CL=F 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/CL%3DF/history",
    },
    {
        "id": "ch-ndx-dotcom",
        "category": "market",
        "symbol": "^NDX",
        "interval": "1wk",
        "name": "나스닥 100 지수",
        "start": "1999-06-01",
        "end": "2000-06-30",
        "split": "2000-03-10",
        "quiz": "regime",
        "prompt": "이 흐름 직후 벌어진 일은 무엇일까요?",
        "choices": [
            "닷컴 버블 정점 이후 기술주가 2년 넘게 폭락",
            "2008년 리먼 브라더스 파산으로 인한 금융위기",
            "코로나19 팬데믹으로 인한 전 세계 락다운",
            "1987년 블랙먼데이 하루 -22% 폭락",
        ],
        "answer": 0,
        "explanation": "나스닥 100은 2000년 3월 24일 4,700을 넘겨 정점을 찍은 뒤 2년 반 동안 80% 가까이 폭락했습니다. 수익 없이 이용자 수만 늘리던 기업이 잇달아 상장폐지되며, '이익 없는 성장'에 붙은 프리미엄이 사라진 사건이었습니다.",
        "source": "Yahoo Finance ^NDX 주별 시세",
        "source_url": "https://finance.yahoo.com/quote/%5ENDX/history",
    },
    {
        "id": "ch-vix-2018",
        "category": "market",
        "symbol": "^VIX",
        "interval": "1d",
        "name": "VIX 변동성 지수",
        "start": "2017-11-01",
        "end": "2018-02-28",
        "split": "2018-02-02",
        "quiz": "regime",
        "prompt": "이 흐름 직후 벌어진 일은 무엇일까요?",
        "choices": [
            "변동성 매도 포지션 청산으로 VIX가 하루 만에 2배 이상 급등",
            "리먼 브라더스 파산과 글로벌 금융위기",
            "그리스 국가부도 위기로 유럽 증시 폭락",
            "2010년 플래시 크래시로 다우가 장중 1,000p 폭락",
        ],
        "answer": 0,
        "explanation": "2018년 2월 5일 VIX는 17에서 장중 50까지 치솟았습니다(흔히 '볼마겟돈'). VIX가 낮게 유지될 것이라 베팅한 ETN과 변동성 매도 포지션이 밀리며 청산이 연쇄됐고, 하루 만에 14% 넘게 빠진 다우지수 기록도 함께 나왔습니다.",
        "source": "Yahoo Finance ^VIX 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/%5EVIX/history",
    },
    {
        "id": "ch-lehman-2008",
        "category": "event",
        "symbol": "^GSPC",
        "interval": "1d",
        "name": "S&P 500 지수",
        "start": "2008-06-02",
        "end": "2008-10-10",
        "split": "2008-09-12",
        "quiz": "regime",
        "prompt": "이 흐름 직후 벌어진 일은 무엇일까요?",
        "choices": [
            "리먼 브라더스 파산으로 신용경색이 번지며 지수가 급락",
            "닷컴 버블 붕괴로 기술주가 무너짐",
            "코로나19 확산으로 3월에 역대급 폭락",
            "미국 국가신용등급 강등으로 8월에 급락",
        ],
        "answer": 0,
        "explanation": "2008년 9월 15일 리먼 브라더스가 파산 보호를 신청하자 신용경색이 전 세계로 번졌고, S&P500은 10월 10일까지 900선 아래로 밀렸습니다. 이후에도 2009년 3월 676까지 하락해 고점 대비 57%가 사라졌습니다.",
        "source": "Yahoo Finance ^GSPC 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/%5EGSPC/history",
    },
    {
        "id": "ch-btc-2017",
        "category": "event",
        "symbol": "BTC-USD",
        "interval": "1wk",
        "name": "비트코인(USD)",
        "start": "2017-03-01",
        "end": "2018-02-28",
        "split": "2017-12-17",
        "quiz": "regime",
        "prompt": "이 흐름 직후 벌어진 일은 무엇일까요?",
        "choices": [
            "2만 달러 정점을 찍고 1년 만에 70% 넘게 폭락",
            "중국이 채굴을 전면 금지해 반토막",
            "테라·루나 스테이블코인 붕괴로 신뢰가 무너짐",
            "비트코인 현물 ETF 승인으로 사상 최고가 경신",
        ],
        "answer": 0,
        "explanation": "비트코인은 2017년 12월 17일 1만 9,800달러 부근에서 정점을 찍은 뒤, 선물 상장과 규제 우려가 겹치며 2018년 12월 3,200달러까지 84% 하락했습니다. 개인 투자자가 몰린 자산일수록 상승의 끝에서 변동성이 커진 사례입니다.",
        "source": "Yahoo Finance BTC-USD 주별 시세",
        "source_url": "https://finance.yahoo.com/quote/BTC-USD/history",
    },
    {
        "id": "ch-nikkei-1989",
        "category": "event",
        "symbol": "^N225",
        "interval": "1d",
        "name": "닛케이 225 지수",
        "start": "1989-11-01",
        "end": "1990-01-31",
        "split": "1989-12-29",
        "quiz": "regime",
        "prompt": "이 흐름 직후 벌어진 일은 무엇일까요?",
        "choices": [
            "버블 정점을 찍고 1990년부터 장기 하락이 시작",
            "아시아 외환위기로 1997년에 급락",
            "동일본 대지진으로 2011년에 폭락",
            "1987년 블랙먼데이로 하루 만에 폭락",
        ],
        "answer": 0,
        "explanation": "닛케이 225는 1989년 12월 29일 38,915로 사상 최고치를 기록했고, 1990년 1월부터 하락이 시작돼 1992년 14,000까지 내려왔습니다. 이후 34년이 지난 2024년에야 그 고점을 다시 넘어섰습니다.",
        "source": "Yahoo Finance ^N225 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/%5EN225/history",
    },
    {
        "id": "ch-usdkrw-2022",
        "category": "event",
        "symbol": "KRW=X",
        "interval": "1d",
        "name": "원/달러 환율",
        "start": "2022-08-01",
        "end": "2022-11-30",
        "split": "2022-10-31",
        "quiz": "next",
        "prompt": "가려진 마지막 구간(약 4주), 환율은 어떻게 흘렀을까요?",
        "explanation": "원/달러는 2022년 10월 1,440원대까지 올라 연고점을 찍은 뒤, 11월 말 1,325원까지 내려왔습니다. 미국 물가 상승률이 꺾이며 달러 강세가 진정되고, 국내 수출 기업의 달러 매도가 늘어난 것이 원화 강세로 이어진 구간입니다.",
        "source": "Yahoo Finance KRW=X 일별 시세",
        "source_url": "https://finance.yahoo.com/quote/KRW%3DX/history",
    },
)


def _epoch(day):
    return int(datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())


def fetch(symbol, interval, start, end):
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=%s&events=history"
        % (urllib.parse.quote(symbol), _epoch(start), _epoch(end), interval)
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as resp:
        payload = json.load(resp)
    result = payload["chart"]["result"][0]
    stamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    bars = []
    for i, ts in enumerate(stamps):
        o, h, l, c = (quote["open"][i], quote["high"][i], quote["low"][i], quote["close"][i])
        if None in (o, h, l, c):
            continue
        v = quote["volume"][i] if quote["volume"] else None
        bars.append([
            datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d"),
            round(float(o), 2), round(float(h), 2), round(float(l), 2), round(float(c), 2),
            int(v) if isinstance(v, (int, float)) else 0,
        ])
    return bars


def _shuffle(seq, seed):
    """id 기반 결정적 섞기 — 보기를 매번 같은 순서로 두고, 정답 위치를 한쪽에 몰지 않는다."""
    items = list(seq)
    for i in range(len(items) - 1, 0, -1):
        digest = hashlib.sha256((seed + ":" + str(i)).encode("utf-8")).hexdigest()
        j = int(digest[:8], 16) % (i + 1)
        items[i], items[j] = items[j], items[i]
    return items


def band_for(ret):
    for key, label, test in FLOW_BANDS:
        if test(ret):
            return key, label
    raise ValueError("no band for %.4f" % ret)


def build_dataset():
    out = []
    for spec in EVENTS:
        bars = fetch(spec["symbol"], spec["interval"], spec["start"], spec["end"])
        dates = [b[0] for b in bars]
        split_idx = max(i for i, d in enumerate(dates) if d <= spec["split"])
        visible, hidden = split_idx + 1, len(bars) - split_idx - 1
        if visible < 30 or hidden < 5:
            raise SystemExit("%s: 구간이 너무 짧습니다(보이는 %d봉 · 가려진 %d봉)" % (spec["id"], visible, hidden))
        if len(bars) > 95:
            raise SystemExit("%s: 봉이 너무 많습니다(%d봉)" % (spec["id"], len(bars)))
        split_close = bars[split_idx][4]
        last_close = bars[-1][4]
        ret = last_close / split_close - 1 if split_close else 0.0

        quiz = {"type": spec["quiz"], "prompt": spec["prompt"]}
        if spec["quiz"] == "next":
            key, label = band_for(ret)
            others = [l for k, l, _ in FLOW_BANDS if k != key]
            decoys = _shuffle(others, spec["id"])[:3]
            quiz.update({"correct": label, "decoys": decoys, "band": key})
        else:
            correct = spec["choices"][spec["answer"]]
            decoys = _shuffle([c for c in spec["choices"] if c != correct], spec["id"])
            quiz.update({"correct": correct, "decoys": decoys, "event": correct})

        out.append({
            "id": spec["id"],
            "spec": spec,
            "category": spec["category"],
            "symbol": spec["symbol"],
            "name": spec["name"],
            "interval": spec["interval"],
            "period": "%s ~ %s" % (dates[0], dates[-1]),
            "visible_until": dates[split_idx],
            "split_index": split_idx,
            "future_return": round(ret * 100, 2),
            "bars": bars,
            "quiz": quiz,
            "explanation": spec["explanation"],
            "source": spec["source"],
            "source_url": spec["source_url"],
        })
        print("%-18s %-22s 봉 %2d (보이는 %2d · 가려진 %2d)  다음구간 %+6.1f%%"
              % (spec["id"], spec["name"], len(bars), visible, hidden, ret * 100))

    # 정답 위치를 0·1·2·3 으로 고르게 돌려, 한 자리만 고르는 요령이 통하지 않게 한다.
    for i, ep in enumerate(out):
        quiz = ep["quiz"]
        decoys = list(quiz.pop("decoys"))
        quiz.pop("spec", None)
        pos = i % 4
        choices = decoys[:]
        choices.insert(pos, quiz.pop("correct"))
        quiz["choices"] = choices
        quiz["answer"] = pos
        del ep["spec"]
        print("%-18s 정답 %d/%d  %s" % (ep["id"], pos + 1, len(choices), choices[pos][:34]))

    payload = {
        "generated_at": datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "categories": CATEGORIES,
        "episodes": out,
    }
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("\n저장: %s (문제 %d개, %.1f KB)" % (DATA_PATH, len(out), os.path.getsize(DATA_PATH) / 1024))


if __name__ == "__main__":
    build_dataset()
    sys.exit(0)

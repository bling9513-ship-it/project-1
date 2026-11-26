#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""옷차림 기온 구간(band_for) 회귀 테스트.

검증 구간
  1) 경계값: 각 구간의 min/max 는 그 구간에 그대로 들어간다.
  2) 빈틈값: 구간 사이 소수 기온(예: 8.3°C)이 4°C 이하 한파(b1)로 떨어지지 않고
     가장 가까운 구간(b2)으로 붙는다. 예전에는 빈틈이면 무조건 b1 이었다.
  3) 범위 밖: 아주 낮은 값은 b1, 아주 높은 값은 마지막 구간(b8)으로 붙는다.
  4) None: 기본 구간(b4)을 돌려준다.

실행: python3 tests/test_outfit_band.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from build_outfit_html import BANDS, band_for  # noqa: E402


def check():
    problems = []
    keys = {b["key"] for b in BANDS}

    # 1) 경계값
    for b in BANDS:
        for t in (b["min"], b["max"]):
            got = band_for(t)
            if got["key"] != b["key"]:
                problems.append(f"경계 {t}°C → {got['key']} (기대 {b['key']})")

    # 2) 구간 빈틈 — 가장 가까운 구간으로
    gaps = [
        (4.5, "b1"),
        (8.3, "b2"),
        (8.9, "b3"),
        (11.5, "b3"),
        (16.4, "b4"),
        (19.5, "b5"),
        (22.5, "b6"),
        (27.5, "b7"),
    ]
    for t, expected in gaps:
        got = band_for(t)
        if got["key"] != expected:
            problems.append(f"빈틈 {t}°C → {got['key']} (기대 {expected})")
        if got["key"] not in keys:
            problems.append(f"{t}°C 결과가 정의되지 않은 구간: {got['key']}")

    # 3) 범위 밖
    if band_for(-40)["key"] != BANDS[0]["key"]:
        problems.append("-40°C 가 첫 구간이 아니다")
    if band_for(70)["key"] != BANDS[-1]["key"]:
        problems.append("70°C 가 마지막 구간이 아니다")

    # 4) None
    if band_for(None)["key"] != BANDS[3]["key"]:
        problems.append("None 이 기본 구간(b4)이 아니다")

    return problems


if __name__ == "__main__":
    found = check()
    if found:
        print("실패:")
        for p in found:
            print("  -", p)
        raise SystemExit(1)
    print("OK: 옷차림 기온 구간 매핑 정상")

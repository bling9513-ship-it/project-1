#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""근무지(location) 정규화·표기·지역 필터 회귀 테스트.

검증 구간
  1) normalize_location(): 플랫폼 원문 표기 → '서울 강남구' / '경기 성남시 분당구' / '재택·원격'
       · 상세 주소(도로명·건물·층)는 버리고 시/도 + 시·군·구까지만 남긴다
       · '외' · '전지역' · '>' 같은 잔여 기호를 없앤다
       · 여러 지역 나열('서울/경기')은 첫 지역으로 대표화한다
       · 근무지가 아닌 값('경력무관')은 빈 문자열로 돌려 카드에 잘못 찍히지 않게 한다
       · 같은 값을 다시 정규화해도 결과가 바뀌지 않는다(멱등)
  2) location_group(): 정규화 값 → 화면 지역 필터 그룹(서울 · 경기·인천 …)
  3) 빌드 산출물(index.html · jobs.json)
       · 지역 필터 칩(data-filter="region")과 카드 근무지 표기(job-loc)가 들어 있다
       · 검색이 근무지도 훑는다(matchLocation)
       · jobs.json 의 근무지가 정규화 표기이고, 대부분 채워져 있다

실행: python3 tests/test_location_normalize.py
"""
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crawler import location_group, normalize_location  # noqa: E402

failures = []


def check(name, cond, detail=""):
    if cond:
        return
    failures.append(f"{name}{(' — ' + str(detail)) if detail else ''}")


NORMALIZE_CASES = [
    # 원문 → 기대값
    ("서울", "서울"),
    ("서울 강남구", "서울 강남구"),
    ("서울 강남구 외", "서울 강남구"),
    ("서울 종로구 외", "서울 종로구"),
    ("서울특별시 강남구 테헤란로 123", "서울 강남구"),
    ("서울시 강남구 선릉로 92길 36, 대동빌딩 6층", "서울 강남구"),
    ("서울 금천구 가산디지털2로98, 1동 401호", "서울 금천구"),
    ("서울강남구", "서울 강남구"),
    ("경기도 성남시 분당구 판교로 256", "경기 성남시 분당구"),
    ("경기 성남시 분당구", "경기 성남시 분당구"),
    ("경기 수원시 영통구 외", "경기 수원시 영통구"),
    ("경기 화성시 만세구 장안로 566-21", "경기 화성시 만세구"),
    ("대전광역시 유성구 대학로 99", "대전 유성구"),
    ("세종전지역", "세종"),
    ("부산 > 전지역 외", "부산"),
    ("전남광주 동구", "전남"),
    ("재택", "재택·원격"),
    ("원격근무", "재택·원격"),
    ("재택/원격", "재택·원격"),
    ("(재택) 서울 마포구", "서울 마포구"),
    ("서울 (재택 병행)", "서울"),
    ("서울/경기", "서울"),
    ("서울·경기", "서울"),
    ("전국", "전국"),
    ("해외", "해외"),
    ("", ""),
    ("경력무관", ""),
]

GROUP_CASES = [
    ("서울 강남구", "서울"),
    ("강남구", "서울"),
    ("경기 성남시 분당구", "경기·인천"),
    ("인천 연수구", "경기·인천"),
    ("대전 유성구", "대전·세종·충청"),
    ("세종", "대전·세종·충청"),
    ("충북 청주시 흥덕구", "대전·세종·충청"),
    ("부산 해운대구", "부산·울산·경남"),
    ("경남 거제시", "부산·울산·경남"),
    ("대구 수성구", "대구·경북"),
    ("광주 북구", "광주·전라"),
    ("전남 여수시", "광주·전라"),
    ("강원 양양군", "강원·제주"),
    ("제주 제주시", "강원·제주"),
    ("재택·원격", "재택·원격"),
    ("전국", "전국·기타"),
    ("", ""),
]


def test_normalize():
    for raw, expected in NORMALIZE_CASES:
        got = normalize_location(raw)
        check(f"normalize({raw!r})", got == expected, f"{got!r} != {expected!r}")
        if got:
            check(f"normalize 멱등({got!r})", normalize_location(got) == got, repr(normalize_location(got)))


def test_group():
    for loc, expected in GROUP_CASES:
        got = location_group(loc)
        check(f"location_group({loc!r})", got == expected, f"{got!r} != {expected!r}")


def test_jobs_json():
    path = os.path.join(BASE_DIR, "jobs.json")
    with open(path, encoding="utf-8") as f:
        jobs = json.load(f)
    check("jobs.json 건수", len(jobs) > 100, len(jobs))
    filled = [j for j in jobs if (j.get("location") or "").strip()]
    ratio = len(filled) / max(1, len(jobs))
    check("jobs.json 근무지 채움 비율 ≥ 95%", ratio >= 0.95, f"{ratio:.1%} ({len(filled)}/{len(jobs)})")
    dirty = []
    for job in jobs:
        loc = (job.get("location") or "").strip()
        if not loc:
            continue
        if normalize_location(loc) != loc:
            dirty.append((loc, normalize_location(loc)))
        if re.search(r"\d", loc) or loc.endswith(" 외") or ">" in loc or "특별시" in loc or "광역시" in loc:
            dirty.append((loc, "상세 주소·잔여 기호"))
    check("jobs.json 근무지 정규화 표기", not dirty, dirty[:5])


def test_index_html():
    path = os.path.join(BASE_DIR, "index.html")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    check("지역 필터 칩", src.count('data-filter="region"') >= 3, src.count('data-filter="region"'))
    check("지역 필터 그룹 값(서울)", 'data-filter="region" data-val="서울"' in src)
    check("지역 필터 그룹 값(경기·인천)", 'data-val="경기·인천"' in src)
    check("카드 근무지 표기", 'class="job-loc' in src)
    check("리스트 근무지 표기", 'list-location' in src)
    check("검색 근무지 매칭", "matchLocation" in src)
    check("지역 그룹 함수", "function locGroup" in src)
    check("빈 근무지 안내", "지역 미표기" in src)


if __name__ == "__main__":
    test_normalize()
    test_group()
    test_jobs_json()
    test_index_html()
    if failures:
        print(f"실패 {len(failures)}건")
        for item in failures:
            print("  ✗", item)
        sys.exit(1)
    total = len(NORMALIZE_CASES) + len(GROUP_CASES)
    print(f"통과: 근무지 정규화 {total}케이스 · jobs.json · index.html 지역 필터/표기")

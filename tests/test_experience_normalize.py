#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""경력(experience) 정규화·표기·필터 회귀 테스트.

검증 구간
  1) normalize_experience(): 플랫폼 원문 표기 → 짧은 표시 라벨
       · '경력 8년 이상' · '경력3년이상' · '경력 2~5년' · '신입·경력' · '경력무관' · '인턴’
       · 확인할 수 없는 값은 빈 문자열(화면에서는 '경력 미표기')
       · 같은 라벨을 다시 정규화해도 결과가 바뀌지 않는다(멱등)
  2) experience_from_years(): 플랫폼 API 연차(하한·상한·신입 여부) → 라벨
  3) experience_group(): 라벨 → 화면 경력 필터 그룹(신입 · 신입·경력 · 경력 · 경력무관 · 인턴 · 미표기)
  4) 빌드 산출물(index.html · jobs.json · README.md)
       · 상단 경력 현황 요약 바와 경력 필터 칩(data-filter="experience")이 들어 있다
       · 카드·리스트에 경력 라벨(job-exp / list-exp)이 붙고, 검색이 경력도 훑는다
       · 저장 검색 상태에 경력 조건이 포함된다
       · jobs.json 경력 채움률 ≥ 95% 이고 표기가 모두 표준 라벨이다
       · README 공고 표에 경력 열이 있다

실행: python3 tests/test_experience_normalize.py
"""
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crawler import (  # noqa: E402
    EXPERIENCE_EMPTY_LABEL,
    EXPERIENCE_GROUPS,
    experience_from_years,
    experience_group,
    normalize_experience,
)

failures = []


def check(name, cond, detail=""):
    if cond:
        return
    failures.append(f"{name}{(' — ' + str(detail)) if detail else ''}")


NORMALIZE_CASES = [
    # 원문 → 기대 라벨
    ("경력무관", "경력무관"),
    ("경력 무관", "경력무관"),
    ("무관", "경력무관"),
    ("신입", "신입"),
    ("신입 0~1년", "신입"),
    ("경력", "경력"),
    ("경력채용", "경력"),
    ("경력 3년↑", "경력 3년↑"),
    ("경력 3년 이상", "경력 3년↑"),
    ("경력3년이상", "경력 3년↑"),
    ("1년 이상", "경력 1년↑"),
    ("경력 2~5년", "경력 2~5년"),
    ("경력 5-11년", "경력 5~11년"),
    ("경력 3년 ~ 5년", "경력 3~5년"),
    ("5년~10년", "경력 5~10년"),
    ("경력 3년 이상 5년 이하", "경력 3~5년"),
    ("경력 12년", "경력 12년"),
    ("신입·경력", "신입·경력"),
    ("신입/경력", "신입·경력"),
    ("신입·경력3년↑", "신입·경력"),
    ("인턴", "인턴"),
    ("인턴 6개월", "인턴"),
    ("", ""),
    (None, ""),
    ("  ", ""),
]

YEARS_CASES = [
    # (하한, 상한, 신입여부) → 라벨
    ((0, 0, False), "신입"),
    ((0, 1, False), "신입"),
    ((0, 0, True), "신입"),
    ((0, 12, False), "신입·경력"),
    ((0, None, False), "신입·경력"),
    ((None, None, True), "신입"),
    ((None, None, False), ""),
    ((None, 100, False), "경력무관"),
    ((None, 5, False), "신입·경력"),
    ((3, 8, False), "경력 3~8년"),
    ((3, 3, False), "경력 3년"),
    ((5, None, False), "경력 5년↑"),
    ((7, 100, False), "경력 7년↑"),
    ((2, 7, True), "경력 2~7년"),
]

GROUP_CASES = [
    ("경력 3년↑", "경력"),
    ("경력 2~5년", "경력"),
    ("경력", "경력"),
    ("신입", "신입"),
    ("신입·경력", "신입·경력"),
    ("경력무관", "경력무관"),
    ("인턴", "인턴"),
    ("", "미표기"),
    ("알 수 없음", "미표기"),
]

LABEL_RE = re.compile(r"^(신입·경력|신입|경력무관|인턴|경력(?: \d{1,2}(?:~\d{1,2})?년↑?)?)$")


def test_normalize():
    for raw, expected in NORMALIZE_CASES:
        got = normalize_experience(raw)
        check(f"normalize({raw!r})", got == expected, f"{got!r} != {expected!r}")
        if got:
            again = normalize_experience(got)
            check(f"normalize 멱등({got!r})", again == got, repr(again))


def test_years():
    for args, expected in YEARS_CASES:
        lo, hi, newcomer = args
        got = experience_from_years(lo, hi, newcomer=newcomer)
        check(f"experience_from_years{args}", got == expected, f"{got!r} != {expected!r}")


def test_group():
    for label, expected in GROUP_CASES:
        got = experience_group(label)
        check(f"experience_group({label!r})", got == expected, f"{got!r} != {expected!r}")
    check("그룹 목록 6종", EXPERIENCE_GROUPS == ("신입", "신입·경력", "경력", "경력무관", "인턴", "미표기"),
          EXPERIENCE_GROUPS)


def test_jobs_json():
    path = os.path.join(BASE_DIR, "jobs.json")
    with open(path, encoding="utf-8") as f:
        jobs = json.load(f)
    check("jobs.json 건수", len(jobs) > 100, len(jobs))
    filled = [j for j in jobs if (j.get("experience") or "").strip()]
    ratio = len(filled) / max(1, len(jobs))
    check("jobs.json 경력 채움 비율 ≥ 95%", ratio >= 0.95, f"{ratio:.1%} ({len(filled)}/{len(jobs)})")

    dirty = []
    for job in jobs:
        label = (job.get("experience") or "").strip()
        if not label:
            continue
        if not LABEL_RE.match(label):
            dirty.append(label)
        elif normalize_experience(label) != label:
            dirty.append(f"{label} -> {normalize_experience(label)}")
    check("jobs.json 경력 표기 표준화", not dirty, dirty[:5])

    groups = {experience_group(j.get("experience")) for j in jobs}
    check("jobs.json 경력 그룹 다양성", len(groups) >= 3, groups)


def test_index_html():
    path = os.path.join(BASE_DIR, "index.html")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    check("경력 현황 요약 영역", 'class="xp-summary"' in src)
    check("경력 현황 막대", 'class="xp-bar"' in src)
    check("경력 필터 칩", src.count('data-filter="experience"') >= 3, src.count('data-filter="experience"'))
    for group in ("신입", "신입·경력", "경력", "경력무관"):
        check(f"경력 필터 칩({group})", f'data-filter="experience" data-val="{group}"' in src)
    check("카드 경력 라벨", 'class="job-exp' in src)
    check("리스트 경력 라벨", 'list-exp' in src)
    check("경력 미표기 안내", EXPERIENCE_EMPTY_LABEL in src)
    check("경력 그룹 함수", "function xpGroup" in src)
    check("검색 경력 매칭", "matchExperience" in src)
    check("저장 검색 경력 조건", "experience: selectedExperience" in src)
    check("경력 상태 변수", "let selectedExperience = 'all';" in src)


def test_readme():
    path = os.path.join(BASE_DIR, "README.md")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    check("README 경력 열", "| 회사명 | 공고명 | 근무지 | 경력 | 플랫폼 |" in src)
    check("README 경력 분포", "경력 분포" in src)


if __name__ == "__main__":
    test_normalize()
    test_years()
    test_group()
    test_jobs_json()
    test_index_html()
    test_readme()
    if failures:
        print(f"실패 {len(failures)}건")
        for item in failures:
            print("  ✗", item)
        sys.exit(1)
    total = len(NORMALIZE_CASES) + len(YEARS_CASES) + len(GROUP_CASES)
    print(f"통과: 경력 정규화 {total}케이스 · jobs.json · index.html 경력 현황/필터/표기 · README")

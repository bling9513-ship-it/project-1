#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""수집 데이터 품질 검증 통합 러너.

한 번의 실행으로 아래를 묶어 확인한다.
  1) 퍼즐·워게임 회귀 테스트
       tests/test_mission_puzzles.py · tests/test_seat_puzzles.py · tests/test_load_puzzles.py
       · tests/test_hangul_puzzles.py · tests/test_cards_data.py
       · tests/test_wargame_rotate.py · tests/test_wargame_spread.py
  2) 커밋된 수집 결과(JSON) 무결성
       - 파싱 실패·필수 필드 누락·ID 중복·날짜 형식 오류·미래 시각
       - meta.total 과 실제 건수 불일치
       - 오래된(갱신 누락) 수집 시각 — 경고, 14일 초과는 실패
  3) HTML 에 심긴 데이터와 원본 JSON 의 정합성(빌드 누락 검출)
       index·cve·ai·study·outfit·pick 이 마지막 데이터로 다시 빌드됐는지
  4) archive.db 검사(있을 때만)
       테이블별 ID 중복·필수 값·정답 범위·날짜 형식

CI(GitHub Actions)에는 브라우저가 없고 archive.db 가 없을 수도 있으므로,
커밋된 JSON·HTML·스크립트만으로 동작하고 DB 는 존재할 때만 검사한다.
네트워크는 쓰지 않는다.

실행: python3 tests/check_data_quality.py
      python3 tests/check_data_quality.py --skip-unit-tests   # 빠른 데이터만
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = timezone(timedelta(hours=9))

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} KST$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:?\d{2})?)?$")
CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$")
URL_RE = re.compile(r"^https?://[^\s\"'<>]+$")
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"}
DEADLINE_STATUS = {"ALWAYS", "D_DAY", "UPCOMING", "URGENT", "WHEN_FILLED"}
STALE_WARN_DAYS = 3
STALE_FAIL_DAYS = 14

failures = []
warnings = []
checks_run = 0


def check(name, cond, detail=""):
    global checks_run
    checks_run += 1
    if not cond:
        failures.append("%s %s" % (name, ("— %s" % detail) if detail else ""))
    return bool(cond)


def warn(name, detail=""):
    warnings.append("%s %s" % (name, ("— %s" % detail) if detail else ""))


def load_json(name):
    path = os.path.join(BASE_DIR, name)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        check("%s 존재" % name, False, "파일 없음")
    except json.JSONDecodeError as exc:
        check("%s JSON 파싱" % name, False, str(exc))
    return None


def parse_stamp(value):
    """'YYYY-MM-DD HH:MM:SS KST' 또는 KST 생략 형식."""
    if not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S KST", "%Y-%m-%d %H:%M KST",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value.strip(), fmt).replace(tzinfo=KST)
        except ValueError:
            continue
    return None


def parse_iso(value):
    if not isinstance(value, str) or not ISO_RE.match(value):
        return None
    text = value.replace("Z", "+00:00")
    if " " in text:
        text = text.replace(" ", "T", 1)
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=KST)


def is_date(value):
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def not_future(dt, slack_days=1):
    return dt is not None and dt <= datetime.now(KST) + timedelta(days=slack_days)


def stale_note(label, dt):
    if dt is None:
        return
    age = (datetime.now(KST) - dt).days
    if age >= STALE_FAIL_DAYS:
        check("%s 갱신" % label, False, "%d일 지남(%s)" % (age, dt.strftime("%m-%d %H:%M")))
    elif age >= STALE_WARN_DAYS:
        warn("%s 갱신" % label, "%d일 지남" % age)


def embedded_json(page, marker):
    """HTML/JS 안에 심긴 `marker` 뒤의 JSON 을 읽는다."""
    path = os.path.join(BASE_DIR, page)
    try:
        with open(path, encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        return None
    pos = src.find(marker)
    if pos == -1:
        return None
    start = pos + len(marker)
    while start < len(src) and src[start] in " \n\t":
        start += 1
    try:
        data, _ = json.JSONDecoder().raw_decode(src[start:])
    except json.JSONDecodeError:
        return None
    return data


def count_articles(page, css_class):
    path = os.path.join(BASE_DIR, page)
    try:
        with open(path, encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        return None
    return len(re.findall(r'<article class="%s"' % re.escape(css_class), src))


# ---------------------------------------------------------------- 1) 회귀 테스트
def run_unit_tests():
    scripts = ["tests/test_mission_puzzles.py", "tests/test_seat_puzzles.py", "tests/test_load_puzzles.py",
               "tests/test_hangul_puzzles.py", "tests/test_cards_data.py",
               "tests/test_wargame_rotate.py", "tests/test_wargame_spread.py",
               "tests/test_job_dedup.py"]
    for script in scripts:
        path = os.path.join(BASE_DIR, script)
        if not os.path.exists(path):
            check("%s 존재" % script, False, "파일 없음")
            continue
        proc = subprocess.run([sys.executable, path], cwd=BASE_DIR, capture_output=True, text=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        tail = output.strip().splitlines()[-1] if output.strip() else ""
        check("%s 통과" % script, proc.returncode == 0, tail[:160])
        print("  [%s] %s · %s" % ("통과" if proc.returncode == 0 else "실패", script, tail[:120]))


# ---------------------------------------------------------------- 2) JSON 무결성
def check_jobs():
    jobs = load_json("jobs.json")
    if jobs is None:
        return
    check("jobs.json 목록", isinstance(jobs, list) and len(jobs) > 0, "건수 %s" % (len(jobs) if isinstance(jobs, list) else "?"))
    if not isinstance(jobs, list):
        return
    seen_title = set()
    exact = 0
    bad_stamp = bad_deadline_status = bad_future = 0
    url_seen = {}
    for job in jobs:
        if not isinstance(job, dict):
            check("jobs.json 항목 형식", False, "dict 아님")
            return
        company = (job.get("company") or "").strip()
        title = (job.get("title") or "").strip()
        url = (job.get("url") or "").strip()
        check("jobs.json 회사·제목", bool(company) and bool(title), repr(title)[:40])
        check("jobs.json URL 형식", bool(URL_RE.match(url)), url[:60])
        key = (company, title, url)
        if key in seen_title:
            exact += 1
        seen_title.add(key)
        url_seen.setdefault(url, set()).add(title)
        status = job.get("deadline_status")
        if status is not None and status not in DEADLINE_STATUS:
            bad_deadline_status += 1
        first, last = parse_stamp(job.get("first_seen_at")), parse_stamp(job.get("last_seen_at"))
        if first is None or last is None:
            bad_stamp += 1
        else:
            if last < first:
                check("jobs.json 수집 시각 순서", False, "%s < %s" % (last, first))
            if not not_future(last):
                bad_future += 1
        dl = job.get("deadline")
        if isinstance(dl, str) and re.match(r"^\u0000", dl):  # 방어적: 제어문자 유입
            check("jobs.json 마감 표기", False, repr(dl)[:40])
    check("jobs.json 중복 항목", exact == 0, "%d건" % exact)
    job_keys = [job.get("job_key") for job in jobs]
    check("jobs.json 공고 키", all(isinstance(k, str) and k for k in job_keys),
          "빈 키 %d건" % sum(1 for k in job_keys if not k))
    check("jobs.json 공고 키 중복", len(set(job_keys)) == len(job_keys),
          "중복 %d건" % (len(job_keys) - len(set(job_keys))))
    check("jobs.json 수집 시각 형식", bad_stamp == 0, "%d건" % bad_stamp)
    check("jobs.json 마감 상태값", bad_deadline_status == 0, "%d건" % bad_deadline_status)
    check("jobs.json 미래 수집 시각", bad_future == 0, "%d건" % bad_future)
    shared = sum(1 for titles in url_seen.values() if len(titles) > 1)
    if shared:
        warn("jobs.json 같은 URL 다른 공고", "%d건(통합 링크 · job_key 로 분리)" % shared)
    stamps = [parse_stamp(j.get("last_seen_at")) for j in jobs]
    stamps = [s for s in stamps if s]
    if stamps:
        stale_note("jobs.json 최근 수집", max(stamps))


def check_cve():
    data = load_json("cve_data.json")
    if not isinstance(data, dict):
        return
    items = data.get("items") or []
    meta = data.get("meta") or {}
    check("cve_data.json 건수", len(items) > 0, "%d건" % len(items))
    check("cve_data.json meta.total", meta.get("total") == len(items), "%s vs %d" % (meta.get("total"), len(items)))
    ids = [str(item.get("cve_id") or "") for item in items]
    check("cve_data.json CVE ID 중복", len(ids) == len(set(ids)), "%d건 중복" % (len(ids) - len(set(ids))))
    bad_id = [i for i in ids if not CVE_RE.match(i)]
    check("cve_data.json CVE ID 형식", not bad_id, bad_id[:3])
    bad_sev = [item.get("cve_id") for item in items if item.get("severity") not in SEVERITIES]
    check("cve_data.json 심각도 값", not bad_sev, bad_sev[:3])
    bad_date = []
    for item in items:
        for field in ("published_at", "kev_date_added", "kev_due_date"):
            value = item.get(field)
            if value in (None, ""):
                continue
            if not is_date(value):
                bad_date.append("%s:%s=%r" % (item.get("cve_id"), field, value))
        updated = item.get("updated_at")
        if updated not in (None, "") and not (is_date(updated) or parse_stamp(updated)):
            bad_date.append("%s:updated_at=%r" % (item.get("cve_id"), updated))
        if not str(item.get("title_ko") or "").strip():
            check("cve_data.json 제목", False, item.get("cve_id"))
    check("cve_data.json 날짜 형식", not bad_date, bad_date[:3])
    collected = parse_stamp(meta.get("collected_at"))
    check("cve_data.json 수집 시각", collected is not None, meta.get("collected_at"))
    if collected:
        check("cve_data.json 미래 수집 시각", not_future(collected), meta.get("collected_at"))
        stale_note("cve_data.json 수집", collected)


def check_ai():
    data = load_json("ai_data.json")
    if not isinstance(data, dict):
        return
    items = data.get("items") or []
    check("ai_data.json 건수", len(items) > 0, "%d건" % len(items))
    check("ai_data.json total", data.get("total") == len(items), "%s vs %d" % (data.get("total"), len(items)))
    keys = [str(item.get("item_key") or "") for item in items]
    check("ai_data.json item_key 중복", len(keys) == len(set(keys)), "%d건" % (len(keys) - len(set(keys))))
    check("ai_data.json item_key 형식", all(keys), "빈 값 있음")
    bad_url = [item.get("item_key") for item in items if not URL_RE.match(str(item.get("url") or ""))]
    check("ai_data.json URL 형식", not bad_url, bad_url[:3])
    bad_date = [item.get("item_key") for item in items
                if item.get("published_at") not in (None, "") and not is_date(str(item.get("published_at"))[:10])]
    check("ai_data.json 발행일 형식", not bad_date, bad_date[:3])
    cats = [c.get("key") for c in (data.get("categories") or []) if isinstance(c, dict)]
    if cats:
        bad_cat = [item.get("item_key") for item in items if item.get("category") not in cats]
        check("ai_data.json 카테고리", not bad_cat, bad_cat[:3])
    updated = parse_stamp(data.get("updated_at"))
    check("ai_data.json 수집 시각", updated is not None, data.get("updated_at"))
    if updated:
        check("ai_data.json 미래 수집 시각", not_future(updated), data.get("updated_at"))
        stale_note("ai_data.json 수집", updated)


def check_chart():
    data = load_json("chart_data.json")
    if not isinstance(data, dict):
        return
    episodes = data.get("episodes") or []
    check("chart_data.json 문항", len(episodes) > 0, "%d건" % len(episodes))
    ids = [e.get("id") for e in episodes]
    check("chart_data.json ID 중복", len(ids) == len(set(ids)), "%d건" % (len(ids) - len(set(ids))))
    for ep in episodes:
        eid = ep.get("id")
        bars = ep.get("bars") or []
        check("chart_data.json 봉 데이터 %s" % eid, len(bars) >= 10, "%d봉" % len(bars))
        if bars:
            keys = []
            for bar in bars:
                if not isinstance(bar, (list, tuple)) or len(bar) < 4:
                    check("chart_data.json 봉 형식 %s" % eid, False, repr(bar)[:40])
                    break
                stamp = bar[0]
                if isinstance(stamp, str) and is_date(stamp[:10]):
                    keys.append(stamp[:10])
                    continue
                try:
                    keys.append(float(stamp))
                except (TypeError, ValueError):
                    check("chart_data.json 봉 시각 %s" % eid, False, repr(stamp))
                    break
            if len(keys) == len(bars):
                check("chart_data.json 봉 정렬 %s" % eid, keys == sorted(keys), "시각 역순")
                check("chart_data.json 봉 중복 시각 %s" % eid, len(set(keys)) == len(keys))
        quiz = ep.get("quiz") or {}
        choices = quiz.get("choices") or []
        check("chart_data.json 선택지 %s" % eid, len(choices) >= 2, "%d개" % len(choices))
        answer = quiz.get("answer")
        check("chart_data.json 정답 범위 %s" % eid,
              isinstance(answer, int) and 0 <= answer < max(len(choices), 1), answer)
        check("chart_data.json 공개 시점 %s" % eid, is_date(ep.get("visible_until")), ep.get("visible_until"))
    generated = parse_iso(data.get("generated_at"))
    check("chart_data.json 생성 시각", generated is not None, data.get("generated_at"))
    if generated:
        check("chart_data.json 미래 생성 시각", not_future(generated), data.get("generated_at"))


def check_study():
    questions = load_json("cppg_questions.json")
    if isinstance(questions, list):
        check("cppg_questions.json 문항", len(questions) > 0, "%d문항" % len(questions))
        ids = [q.get("id") for q in questions]
        check("cppg_questions.json ID 중복", len(ids) == len(set(ids)), "%d건" % (len(ids) - len(set(ids))))
        bad = []
        for q in questions:
            choices = q.get("choices") or []
            try:
                answer = int(q.get("answer"))
            except (TypeError, ValueError):
                answer = None
            if len(choices) < 2:
                bad.append("%s:선택지%d" % (q.get("id"), len(choices)))
            elif answer is None or not 1 <= answer <= len(choices):
                bad.append("%s:정답%s" % (q.get("id"), q.get("answer")))
            elif not str(q.get("prompt") or "").strip():
                bad.append("%s:문제없음" % q.get("id"))
        check("cppg_questions.json 정답·선택지", not bad, bad[:3])

    units = load_json("custom_study.json")
    if isinstance(units, list):
        ids = [u.get("id") for u in units]
        check("custom_study.json ID 중복", len(ids) == len(set(ids)), "%d건" % (len(ids) - len(set(ids))))
        bad = []
        for unit in units:
            for q in unit.get("questions") or []:
                choices = q.get("choices") or []
                try:
                    answer = int(q.get("answer"))
                except (TypeError, ValueError):
                    answer = None
                if len(choices) < 2 or answer is None or not 1 <= answer <= len(choices):
                    bad.append("%s/%s" % (unit.get("id"), q.get("id")))
        check("custom_study.json 정답·선택지", not bad, bad[:3])
        bad_date = [u.get("id") for u in units if not parse_stamp(u.get("created_at"))]
        check("custom_study.json 생성 시각", not bad_date, bad_date[:3])


# ---------------------------------------------------------------- 3) HTML ↔ 데이터
def check_pages():
    jobs = load_json("jobs.json")
    if isinstance(jobs, list):
        embedded = embedded_json("index.html", "const JOBS = ")
        if isinstance(embedded, list):
            check("index.html 공고 수", len(embedded) == len(jobs), "%d vs %d" % (len(embedded), len(jobs)))
            a = {str(j.get("url")) for j in jobs if isinstance(j, dict)}
            b = {str(j.get("url")) for j in embedded if isinstance(j, dict)}
            check("index.html 공고 일치", a == b, "차이 %d건" % len(a ^ b))
        else:
            check("index.html 데이터 블록", False, "const JOBS 파싱 실패")

    cve = load_json("cve_data.json")
    if isinstance(cve, dict):
        embedded = embedded_json("cve.html", "const CVE_ITEMS = ")
        meta = embedded_json("cve.html", "const CVE_META = ")
        items = cve.get("items") or []
        if isinstance(embedded, list):
            check("cve.html CVE 수", len(embedded) == len(items), "%d vs %d" % (len(embedded), len(items)))
            check("cve.html CVE ID 일치",
                  {i.get("cve_id") for i in embedded} == {i.get("cve_id") for i in items},
                  "ID 집합 불일치")
            if isinstance(meta, dict):
                page_stamp = parse_stamp(meta.get("built_at")) or parse_stamp(meta.get("collected_at"))
                data_stamp = parse_stamp((cve.get("meta") or {}).get("collected_at"))
                if page_stamp and data_stamp:
                    check("cve.html 최신 수집 반영", page_stamp >= data_stamp - timedelta(seconds=1),
                          "페이지 %s < 수집 %s" % (page_stamp, data_stamp))
        else:
            check("cve.html 데이터 블록", False, "const CVE_ITEMS 파싱 실패")

    ai = load_json("ai_data.json")
    if isinstance(ai, dict):
        embedded = embedded_json("ai.html", "const AI_ITEMS = ")
        meta = embedded_json("ai.html", "const AI_META = ")
        if isinstance(embedded, list):
            # ai.html 은 DB(archive.db)에서 최근 N건을 렌더링하고, ai_data.json 은 수집 캐시다.
            # 페이지 안에서 메타와 목록이 어긋나지 않는지, 항목 자체가 온전한지를 본다.
            keys = [str(i.get("item_key") or "") for i in embedded]
            check("ai.html item_key 중복", len(keys) == len(set(keys)), "%d건" % (len(keys) - len(set(keys))))
            check("ai.html item_key 값", all(keys), "빈 값 있음")
            bad_url = [k for k, i in zip(keys, embedded) if not URL_RE.match(str(i.get("url") or ""))]
            check("ai.html URL 형식", not bad_url, bad_url[:3])
            if isinstance(meta, dict):
                check("ai.html meta.total", meta.get("total") == len(embedded),
                      "%s vs %d" % (meta.get("total"), len(embedded)))
                stamp = parse_stamp(meta.get("updated_at"))
                check("ai.html 갱신 시각", stamp is not None, meta.get("updated_at"))
                data_stamp = parse_stamp(ai.get("updated_at"))
                if stamp and data_stamp:
                    check("ai.html 최신 수집 반영", stamp >= data_stamp - timedelta(seconds=1),
                          "페이지 %s < 수집 %s" % (meta.get("updated_at"), ai.get("updated_at")))
            else:
                check("ai.html 데이터 블록", False, "const AI_META 파싱 실패")
        else:
            check("ai.html 데이터 블록", False, "const AI_ITEMS 파싱 실패")

    # 학습 데이터: JS 사본이 JSON 원본과 같은지
    questions = load_json("cppg_questions.json")
    if isinstance(questions, list):
        js = embedded_json("cppg_questions.js", "window.ALL_QUESTIONS = ")
        if isinstance(js, list):
            check("cppg_questions.js 문항 수", len(js) == len(questions), "%d vs %d" % (len(js), len(questions)))
            check("cppg_questions.js ID 일치",
                  [q.get("id") for q in js] == [q.get("id") for q in questions], "순서·ID 불일치")
        else:
            check("cppg_questions.js 데이터 블록", False, "window.ALL_QUESTIONS 파싱 실패")

    units = load_json("custom_study.json")
    if isinstance(units, list):
        js = embedded_json("custom_study.js", "window.CUSTOM_STUDIES = ")
        if isinstance(js, list):
            check("custom_study.js 단원 수", len(js) == len(units), "%d vs %d" % (len(js), len(units)))
        else:
            check("custom_study.js 데이터 블록", False, "window.CUSTOM_STUDIES 파싱 실패")

    # 옷차림·오늘 뭐 먹지: 카드 수 = 데이터 수
    outfit_cards = count_articles("outfit.html", "outfit-card")
    check("outfit.html 코디 카드", outfit_cards == 24, "%s개" % outfit_cards)
    path = os.path.join(BASE_DIR, "outfit.html")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            src = f.read()
        check("outfit.html 기온 구간", src.count('class="band-section') >= 8,
              "%d개" % src.count('class="band-section'))

    # 오늘의 카드: cards_data.json 과 cards.html 에 심긴 데이터가 같은지
    cards_json = load_json("cards_data.json")
    cards_embedded = embedded_json("cards.html", 'id="cardsData">')
    if isinstance(cards_json, dict):
        check("cards_data.json 덱 2개", len(cards_json.get("decks") or []) == 2,
              len(cards_json.get("decks") or []))
        total = sum(len(t.get("cards") or []) for d in cards_json.get("decks") or [] for t in d.get("themes") or [])
        check("cards_data.json 카드 24장", total == 24, total)
    if isinstance(cards_json, dict) and isinstance(cards_embedded, dict):
        check("cards.html ↔ cards_data.json 일치", cards_json.get("decks") == cards_embedded.get("decks"))
    else:
        check("cards.html 데이터 블록", False, "id=cardsData 파싱 실패")

    menus = embedded_json("pick.html", "const MENUS = ")
    courses = embedded_json("pick.html", "const COURSES = ")
    menu_cards = count_articles("pick.html", "menu-card")
    course_cards = count_articles("pick.html", "course-card")
    if isinstance(menus, list):
        check("pick.html 메뉴 카드", menu_cards == len(menus), "%s vs %d" % (menu_cards, len(menus)))
        check("pick.html 메뉴 ID 중복", len({m.get("id") for m in menus}) == len(menus))
    if isinstance(courses, list):
        check("pick.html 나들이 카드", course_cards == len(courses), "%s vs %d" % (course_cards, len(courses)))


# ---------------------------------------------------------------- 3-b) 오늘 허브(today.html)
def check_today():
    data = embedded_json("today.html", "const TODAY = ")
    if data is None:
        check("today.html 데이터 블록", False, "const TODAY 파싱 실패")
        return
    check("today.html 오늘 날짜", is_date(data.get("today")), data.get("today"))
    built = parse_stamp(data.get("built_at"))
    check("today.html 빌드 시각", built is not None, data.get("built_at"))
    if built:
        check("today.html 미래 빌드 시각", not_future(built), data.get("built_at"))
        stale_note("today.html 빌드", built)

    jobs = data.get("jobs") or {}
    cve = data.get("cve") or {}
    ai = data.get("ai") or {}
    check("today.html 마감 공고 수", isinstance(jobs.get("count"), int) and jobs.get("count") >= 0,
          jobs.get("count"))
    check("today.html 공고 갱신 시각", bool(jobs.get("updated")), jobs.get("updated"))
    check("today.html KEV 수", isinstance(cve.get("kev"), int), cve.get("kev"))

    cve_data = load_json("cve_data.json")
    if isinstance(cve_data, dict):
        kev = sum(1 for item in cve_data.get("items") or [] if item.get("is_kev"))
        check("today.html KEV 일치", cve.get("kev") == kev, "%s vs %d" % (cve.get("kev"), kev))
        check("today.html CVE 갱신 일치",
              cve.get("updated") == (cve_data.get("meta") or {}).get("collected_at"),
              "%s vs %s" % (cve.get("updated"), (cve_data.get("meta") or {}).get("collected_at")))
    ai_data = load_json("ai_data.json")
    if isinstance(ai_data, dict):
        check("today.html AI 건수 일치", ai.get("total") == ai_data.get("total"),
              "%s vs %s" % (ai.get("total"), ai_data.get("total")))
        check("today.html AI 브리핑", bool(str(ai.get("briefing") or "").strip()), "브리핑 비어 있음")

    weather = data.get("weather") or {}
    check("today.html 날씨 상태값", isinstance(weather.get("ok"), bool), weather.get("ok"))
    if weather.get("ok"):
        check("today.html 기온", isinstance(weather.get("temp"), (int, float)), weather.get("temp"))
        check("today.html 옷차림 한 줄", bool(str(weather.get("line") or "").strip()), weather.get("line"))

    games = data.get("games") or {}
    check("today.html 오늘의 게임", bool((games.get("wargame") or {}).get("title")) or bool((games.get("clue") or {}).get("title")),
          "게임 문제 없음")

    path = os.path.join(BASE_DIR, "today.html")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    for chip in ("jobsState", "cveState", "studyState", "aiState", "weatherState", "gameState"):
        check("today.html 상태 칩 %s" % chip, chip in src, "없음")
    for href in ("index.html", "cve.html", "study.html", "ai.html", "outfit.html", "wargame.html", "clue.html"):
        check("today.html 링크 %s" % href, 'href="%s"' % href in src, "없음")
    for key in ("study_review_queue_v1", "study_user_answers_v4", "study_bookmarks_v1"):
        check("today.html 복습 저장소 %s" % key, key in src, "없음")


# ---------------------------------------------------------------- 4) DB
def check_db():
    path = os.path.join(BASE_DIR, "archive.db")
    if not os.path.exists(path):
        warn("archive.db", "없음 — DB 검사 생략(커밋 데이터만 검사)")
        return
    try:
        conn = sqlite3.connect(path)
    except sqlite3.Error as exc:
        check("archive.db 열기", False, str(exc))
        return
    try:
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        for name, minimum in (("jobs", 1), ("study_questions", 1), ("wargame_questions", 20),
                              ("clue_questions", 10), ("cve_reports", 1), ("ai_insights", 1)):
            if name not in tables:
                check("archive.db %s 테이블" % name, False, "없음")
                continue
            count = conn.execute("SELECT COUNT(*) FROM %s" % name).fetchone()[0]
            check("archive.db %s 행 수" % name, count >= minimum, "%d행" % count)

        def duplicates(sql, label):
            rows = conn.execute(sql).fetchall()
            return [r[0] for r in rows if r[1] > 1], label

        for sql, label in (
            ("SELECT cve_id, COUNT(*) FROM cve_reports GROUP BY cve_id HAVING COUNT(*)>1", "cve_reports.cve_id"),
            ("SELECT id, COUNT(*) FROM study_questions GROUP BY id HAVING COUNT(*)>1", "study_questions.id"),
            ("SELECT id, COUNT(*) FROM wargame_questions GROUP BY id HAVING COUNT(*)>1", "wargame_questions.id"),
            ("SELECT id, COUNT(*) FROM clue_questions GROUP BY id HAVING COUNT(*)>1", "clue_questions.id"),
            ("SELECT item_key, COUNT(*) FROM ai_insights GROUP BY item_key HAVING COUNT(*)>1", "ai_insights.item_key"),
        ):
            dup, _ = duplicates(sql, label)
            check("archive.db %s 중복" % label, not dup, str(dup[:3]))

        if "jobs" in tables:
            bad = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE TRIM(COALESCE(company,''))='' OR TRIM(COALESCE(title,''))=''"
            ).fetchone()[0]
            check("archive.db jobs 필수값", bad == 0, "%d행" % bad)
            bad = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE COALESCE(url,'') NOT LIKE 'http%'").fetchone()[0]
            check("archive.db jobs URL", bad == 0, "%d행" % bad)
            bad = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE first_seen_at IS NOT NULL AND last_seen_at IS NOT NULL "
                "AND last_seen_at < first_seen_at").fetchone()[0]
            check("archive.db jobs 수집 시각 순서", bad == 0, "%d행" % bad)

        for table, column in (("study_questions", "category"), ("wargame_questions", "kind"),
                              ("clue_questions", "category")):
            if table in tables:
                bad = conn.execute("SELECT COUNT(*) FROM %s WHERE TRIM(COALESCE(%s,''))=''" % (table, column)).fetchone()[0]
                check("archive.db %s.%s 값" % (table, column), bad == 0, "%d행" % bad)

        if "clue_questions" in tables:
            rows = conn.execute("SELECT id, puzzle_date FROM clue_questions").fetchall()
            bad = [r[0] for r in rows if r[1] and not is_date(str(r[1])[:10])]
            check("archive.db clue_questions.puzzle_date", not bad, str(bad[:3]))

        if "wargame_questions" in tables:
            bad = []
            for qid, choices_json, answer in conn.execute(
                    "SELECT id, choices_json, answer_idx FROM wargame_questions"):
                try:
                    choices = json.loads(choices_json or "[]")
                except json.JSONDecodeError:
                    bad.append("%s:choices" % qid)
                    continue
                if choices and (not isinstance(answer, int) or not 0 <= answer < len(choices)):
                    bad.append("%s:answer%s" % (qid, answer))
            check("archive.db wargame 정답 범위", not bad, str(bad[:3]))

        if "study_questions" in tables:
            bad = []
            for qid, choices_raw, answer in conn.execute(
                    "SELECT id, choices, answer FROM study_questions"):
                try:
                    choices = json.loads(choices_raw or "[]")
                except json.JSONDecodeError:
                    choices = []
                try:
                    answer_no = int(answer)
                except (TypeError, ValueError):
                    answer_no = None
                if len(choices) >= 2 and (answer_no is None or not 1 <= answer_no <= len(choices)):
                    bad.append("%s:answer%s" % (qid, answer))
            check("archive.db study 정답 범위", not bad, str(bad[:3]))

        if "cve_reports" in tables:
            bad = conn.execute(
                "SELECT COUNT(*) FROM cve_reports WHERE COALESCE(published_at,'')<>'' AND "
                "published_at NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'").fetchone()[0]
            check("archive.db cve published_at 형식", bad == 0, "%d행" % bad)
    finally:
        conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="수집 데이터 품질 검증")
    parser.add_argument("--skip-unit-tests", action="store_true", help="퍼즐·워게임 회귀 테스트 생략")
    args = parser.parse_args(argv)

    global failures, warnings, checks_run
    failures, warnings, checks_run = [], [], 0

    print("[1/4] 퍼즐·워게임 회귀 테스트")
    if args.skip_unit_tests:
        print("  생략(--skip-unit-tests)")
    else:
        run_unit_tests()

    print("[2/4] 수집 결과 JSON 무결성")
    check_jobs()
    check_cve()
    check_ai()
    check_chart()
    check_study()

    print("[3/4] HTML ↔ 데이터 정합성(빌드 누락)")
    check_pages()

    check_today()

    print("[4/4] archive.db")
    check_db()

    for message in warnings:
        print("  [경고] %s" % message)
    if failures:
        print("\n데이터 품질 검사 실패 %d건 (검사 %d항목)" % (len(failures), checks_run))
        for message in failures:
            print("  [실패] %s" % message)
        raise SystemExit(1)
    print("데이터 품질 검사 통과: %d항목%s" % (checks_run, (" · 경고 %d건" % len(warnings)) if warnings else ""))
    return 0


if __name__ == "__main__":
    main()

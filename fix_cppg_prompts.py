# -*- coding: utf-8 -*-
"""CPPG 문항 지문(question/prompt) 포맷 정규화.

수험서 PDF 에서 뽑아낸 1~3회 300문항 지문에는 PDF 줄바꿈이 그대로 남아
`있으 ⏎ 면` 처럼 단어 중간이 끊기거나, 정당화 여백이 여러 칸 공백으로 박혀 있다.
`study.html` 은 지문을 `white-space: pre-wrap` 으로 그리므로 그 줄바꿈·여백이
화면에 그대로 보인다.

이 스크립트는 의미를 바꾸지 않는 범위(줄바꿈·여백만)에서 지문을 정리한다.

- 목록/문단 머리(1. 2. / ㄱ. ㄴ. / · / 질문 : / 제N조 / * 등)는 줄을 유지한다.
- 그 밖의 줄바꿈은 앞 줄에 이어 붙인다. 앞 줄이 공백 없이 끝났으면(단어 중간 절단)
  공백 없이, 공백으로 끝났으면 공백 하나를 넣고, 다음 줄이 들여쓰기로 시작하면
  (PDF 정당화로 끊긴 낱말) 공백 없이 잇는다.
- 3칸 이상 공백은 빈칸(______)으로 바꾼다. 줄 끝/줄 머리의 여러 칸 공백도 같다.
- 남은 여러 칸 공백은 한 칸으로 줄이고, `다.다음` 처럼 붙은 문장 구분에는 띄어쓰기를 넣는다.

`--dry-run` 은 바뀌는 문항만, `--show-all` 은 정규화 결과 전문을 보여 준다.
DB(archive.db)를 원천으로 고치고, `export_study_data_from_db()` 가
`cppg_questions.json`·`cppg_questions.js` 를 다시 쓰게 한다.
"""
import argparse
import difflib
import json
import os
import re
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive.db")

BLANK = "______"

# 목록·문단 머리로 볼 줄 (앞 줄에 이어 붙이지 않고 새 줄로 둔다)
_STRUCTURAL = [
    re.compile(r"^\d{1,3}[.)]\s"),          # 1. / 2)
    re.compile(r"^[ㄱ-ㅎ][.)]\s?"),          # ㄱ. / ㄴ)
    re.compile(r"^[ㄱ-ㅎ]\s*:"),              # ㄱ : 설명
    re.compile(r"^ㅁ\s*:"),
    re.compile(r"^[·•*※]\s?"),              # 글머리표
    re.compile(r"^질문\s*:"),
    re.compile(r"^제\d+조"),
    re.compile(r"^\(\d+\)"),
    re.compile(r"^\d{1,3}\)\s"),            # 1) 형태
    re.compile(r"^_+\s*:"),                 # 빈칸 라벨(______ : ...)
    re.compile(r"^<[a-zA-Z/!]"),            # 코드·태그 예문
    re.compile(r"^https?://"),               # URL 예문
]


def _is_structural(text):
    stripped = text.lstrip()
    return any(p.match(stripped) for p in _STRUCTURAL)


def normalize_prompt(raw, stats=None):
    """지문 한 건을 정리한다(줄바꿈·공백만 손댄다)."""
    if not raw:
        return raw or ""
    text = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    lines = text.split("\n")
    blocks = []  # [(content)]
    prev_trailing = 0  # 바로 앞 줄이 공백으로 끝났는지(낱말 경계 신호)

    for index, line in enumerate(lines):
        nxt = lines[index + 1] if index + 1 < len(lines) else ""

        if not line.strip():
            continue

        # 줄 머리의 여러 칸 공백 + 콜론 → 빈칸 라벨
        lead_blank_label = re.match(r"^\s{3,}:\s*", line)
        if lead_blank_label:
            if stats is not None:
                stats["blank"] += 1
            content = BLANK + " : " + line[lead_blank_label.end():].strip()
            blocks.append(content)
            continue

        trailing = len(line) - len(line.rstrip(" "))
        body = line.rstrip(" ")

        # 줄 끝 여러 칸 공백: 다음 줄이 이어지는 낱말이면 정당화 여백, 아니면 빈칸
        blank_at_end = trailing >= 3 and (not nxt.strip() or _is_structural(nxt))
        if blank_at_end:
            if stats is not None:
                stats["blank"] += 1
            body = body + " " + BLANK

        # 줄 안쪽의 여러 칸 공백은 빈칸으로 바꾼다(들여쓰기가 아닌 자리)
        body = re.sub(r"(?<=\S) {3,}(?=\S)", " " + BLANK + " ", body)
        if stats is not None and BLANK in body and "blank" in stats:
            stats["blank"] += 1

        # 현재 줄이 들여쓰기로 시작하면 앞 줄에서 이어진 낱말이다(PDF 정당화 줄바꿈).
        # 다만 들여쓰기가 얕으면 낱말 경계로 끊긴 경우가 있어 공백을 넣는다.
        cur_indent = len(line) - len(line.lstrip(" "))

        if _is_structural(body) or not blocks:
            blocks.append(body.strip())
            prev_trailing = trailing
            continue

        prev = blocks[-1]
        if cur_indent >= 2 and (cur_indent >= 8 or prev_trailing <= 1):
            joined = prev + body.strip()            # 들여쓰기로 이어진 낱말(단어 중간 절단)
            if stats is not None:
                stats["join_nospace"] += 1
        elif re.search(r"[.?!]$", prev) and re.match(r"^[가-힣A-Za-z(]", body.strip()):
            joined = prev + "\n" + body.strip()     # 앞 문장이 끝난 뒤 새 문단
            if stats is not None:
                stats["paragraph"] += 1
        elif prev_trailing >= 1 or re.search(r" $", prev):
            joined = prev + " " + body.strip()      # 낱말 경계
            if stats is not None:
                stats["join_space"] += 1
        else:
            joined = prev + body.strip()            # 단어 중간 절단
            if stats is not None:
                stats["join_nospace"] += 1
        blocks[-1] = joined
        prev_trailing = trailing

    out = "\n".join(blocks)

    # 남은 여러 칸 공백 정리(빈칸 표식은 보존)
    out = re.sub(r" {2,}", " ", out)
    out = re.sub(r" *\n *", "\n", out)
    # 서술어 종결(`다.`) 뒤에 바로 붙은 글자·숫자, 줄 머리의 목록 표시에는 띄어쓰기를 넣는다
    # (`상황이다.다음` → `상황이다. 다음`, `ㄷ.법정대리인` → `ㄷ. 법정대리인`).
    # 영문 코드·URL 예문(`img.src`, `attacker.com`)은 건드리지 않는다.
    out = re.sub(r"다\.(?=\S)", "다. ", out)
    out = re.sub(r"(?m)^([ㄱ-ㅎ])\.(?=\S)", r"\1. ", out)
    return out.strip()


def normalize_all(dry_run=False, show_all=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, round_id, question_num, prompt FROM study_questions "
        "WHERE category = 'cppg' ORDER BY CAST(SUBSTR(round_id, 2) AS INTEGER), question_num"
    ).fetchall()

    changed = []
    stats = {"join_nospace": 0, "join_space": 0, "paragraph": 0, "blank": 0}
    for row in rows:
        before = row["prompt"] or ""
        after = normalize_prompt(before, stats)
        if after == before:
            if show_all:
                print(f"\n===== {row['round_id']} q{row['question_num']} (변경 없음) =====")
                print(after)
            continue
        if show_all:
            print(f"\n===== {row['round_id']} q{row['question_num']} =====")
            print(after)
        changed.append((row["id"], row["round_id"], row["question_num"], before, after))

    # 두 번 돌려도 같은지(멱등성) 확인
    for _id, round_id, qnum, _before, after in changed:
        if normalize_prompt(after) != after:
            raise SystemExit(f"[실패] 정규화가 멱등하지 않음: {round_id} q{qnum}")

    print(f"-> CPPG 지문 {len(rows)}건 점검, {len(changed)}건 변경 "
          f"(이어붙임 {stats['join_nospace']}·{stats['join_space']}회, 문단 {stats['paragraph']}, 빈칸 {stats['blank']})")

    if dry_run:
        for _id, round_id, qnum, before, after in changed:
            diff = difflib.unified_diff(before.split("\n"), after.split("\n"),
                                        lineterm="", n=1)
            print(f"\n----- {round_id} q{qnum} -----")
            for line in diff:
                if line.startswith(("---", "+++", "@@")):
                    continue
                print(line)
        print("\n(드라이런: DB는 그대로입니다)")
        return len(changed)

    for qid, _round_id, _qnum, _before, after in changed:
        conn.execute("UPDATE study_questions SET prompt = ? WHERE id = ?", (after, qid))
    conn.commit()
    conn.close()
    print("-> archive.db 지문 업데이트 완료(cppg_questions.json·js 는 build_all_from_db.py 가 DB에서 다시 씁니다)")
    return len(changed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CPPG 문항 지문 줄바꿈·공백 정규화")
    parser.add_argument("--dry-run", action="store_true", help="DB를 고치지 않고 변경 내역만 출력")
    parser.add_argument("--show-all", action="store_true", help="정규화 결과 전문 출력")
    args = parser.parse_args()
    normalize_all(dry_run=args.dry_run, show_all=args.show_all)

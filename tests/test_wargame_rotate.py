#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""워게임 정답 회전(rotate_answer / balance_answers) 회귀 테스트.

shift 부호가 뒤집히면 보기 내용은 그대로인 채 answer_idx 만 바뀌어
'화면에 표시되는 정답'이 틀어지므로, 회전 후에도 정답 보기 텍스트가
지정한 위치에 그대로 있는지를 전수 조합으로 확인한다.

실행: python3 tests/test_wargame_rotate.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from wargame_generator import balance_answers, rotate_answer  # noqa: E402

failures = []


def check(name, cond, detail=""):
    if cond:
        print("  [통과] %s" % name)
    else:
        print("  [실패] %s %s" % (name, detail))
        failures.append(name)


def q(answer=0, tag="q"):
    # 각 문제마다 보기 텍스트를 다르게 만들어, 회전 시 다른 문제의 보기와 섞여도 잡히게 한다
    return {"choices": ["%s-A" % tag, "%s-B" % tag, "%s-C" % tag, "%s-D" % tag], "answer": answer}


def main():
    print("== rotate_answer 단일 케이스 (brief 예시) ==")
    item = q(0)
    rotate_answer(item, 1)
    check("old=0 -> new_idx=1 이면 choices[1] == 'q-A'",
          item["answer"] == 1 and item["choices"][1] == "q-A", item)

    print("== rotate_answer 전수 조합 (old, new 16쌍) ==")
    for old in range(4):
        for new in range(4):
            item = q(old, tag="%d%d" % (old, new))
            correct = item["choices"][old]
            before = list(item["choices"])
            rotate_answer(item, new)
            check("old=%d -> new=%d : 정답 텍스트 유지" % (old, new),
                  item["answer"] == new and item["choices"][new] == correct
                  and sorted(item["choices"]) == sorted(before), item)

    print("== balance_answers: 같은 정답 위치가 겹칠 때 4곳으로 분산 ==")
    items = [q(0, tag="b%d" % i) for i in range(4)]
    correct_texts = ["b%d-A" % i for i in range(4)]
    balance_answers(items)
    check("정답 위치가 0,1,2,3 으로 분산", sorted(x["answer"] for x in items) == [0, 1, 2, 3],
          [x["answer"] for x in items])
    for i, x in enumerate(items):
        check("문제 %d 의 정답 보기가 그대로 유지" % i, x["choices"][x["answer"]] == correct_texts[i],
              x["choices"][x["answer"]])

    print("== balance_answers: 일부만 겹치는 경우 ==")
    items = [q(0, tag="c0"), q(2, tag="c1"), q(0, tag="c2")]
    correct_texts = ["c0-A", "c1-C", "c2-A"]
    balance_answers(items)
    for i, x in enumerate(items):
        check("문제 %d 의 정답 보기가 그대로 유지(중복 회전 포함)" % i,
              x["choices"][x["answer"]] == correct_texts[i], x["choices"][x["answer"]])

    print("== rotate_answer 잘못된 입력 거부 ==")
    try:
        rotate_answer(q(0), 4)
        check("new_idx=4 는 거부", False)
    except ValueError:
        check("new_idx=4 는 거부", True)
    try:
        rotate_answer({"choices": ["A", "B", "C"], "answer": 0}, 1)
        check("보기 3개는 거부", False)
    except ValueError:
        check("보기 3개는 거부", True)

    print()
    if failures:
        print("[실패] %d건: %s" % (len(failures), ", ".join(failures)))
        return 1
    print("[통과] rotate_answer / balance_answers 회귀 테스트 전부 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())

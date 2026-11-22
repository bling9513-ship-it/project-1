#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""검증용 미리보기 페이지 생성기(테스트·스크린샷 전용 · 저장소에 커밋하지 않는다).

만드는 것
  _preview_grocery_stale.html — 14일 지난 승계값(stale) 품목 1건이 섞인 장보기 타이밍 화면.
      · grocery_crawler._inherit() 를 실제로 통과시켜 staleDays 를 계산한다(손으로 채우지 않음).
      · grocery_data.json 은 건드리지 않고 미리보기 파일만 만든다.
  _preview_grocery_stale_data.json — 위 미리보기의 입력 데이터(검산용).
  _preview_study_monetization.html — 제휴 카드·후원 링크를 켠 임시 설정으로 빌드한 시험 공부 화면.
      · monetization_config.json 은 건드리지 않고 환경 변수로만 임시 설정을 넣는다.

실행
  python3 tests/make_preview_pages.py            # 미리보기 3개 생성
  python3 tests/make_preview_pages.py --clean    # 미리보기 파일 삭제
"""
import json
import os
import subprocess
import sys
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import grocery_crawler  # noqa: E402
import build_grocery_html  # noqa: E402
import monetization  # noqa: E402

STALE_ITEM = "spinach"          # 시금치 — 두 지역 모두 14일 지난 승계값으로 만든다
STALE_DAYS_BACK = 14

GROCERY_HTML = os.path.join(BASE_DIR, "_preview_grocery_stale.html")
GROCERY_JSON = os.path.join(BASE_DIR, "_preview_grocery_stale_data.json")
STUDY_HTML = os.path.join(BASE_DIR, "_preview_study_monetization.html")
STUDY_CONFIG = os.path.join(BASE_DIR, "_preview_monetization_config.json")

PREVIEW_FILES = (GROCERY_HTML, GROCERY_JSON, STUDY_HTML, STUDY_CONFIG)


def build_grocery_preview(out_html=None, out_json=None):
    """실제 수집 데이터에 14일 지난 승계값 1품목을 섞어 장보기 화면을 다시 그린다."""
    out_html = out_html or GROCERY_HTML
    out_json = out_json or GROCERY_JSON
    with open(grocery_crawler.DATA_PATH, encoding="utf-8") as handle:
        data = json.load(handle)
    today = date.fromisoformat(data["window"]["end"])
    observed = (today - timedelta(days=STALE_DAYS_BACK)).isoformat()

    previous = json.loads(json.dumps(data))
    target = [item for item in previous["items"] if item["id"] == STALE_ITEM]
    if not target:
        raise SystemExit("미리보기용 품목(%s)이 grocery_data.json 에 없습니다" % STALE_ITEM)
    for rid, stats in target[0]["byRegion"].items():
        # 직전 수집 시점에는 이 값이 '정상 수집값'이었다고 가정한다(조사일만 14일 전으로 이동).
        stats["latest"] = {"date": observed, "price": stats["latest"]["price"]}
        stats["observedDate"] = observed
        stats["fetchedDate"] = (today - timedelta(days=STALE_DAYS_BACK - 1)).isoformat()
        stats["staleDays"] = STALE_DAYS_BACK - 1
        stats["stale"] = False
        stats.pop("inherited", None)

    for item in data["items"]:
        if item["id"] != STALE_ITEM:
            continue
        for rid in item["byRegion"]:
            inherited = grocery_crawler._inherit(previous, item["id"], rid, today)
            if not inherited:
                raise SystemExit("승계값을 만들지 못했습니다: %s/%s" % (item["id"], rid))
            item["byRegion"][rid] = inherited

    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    build_grocery_html.build(data_path=out_json, out_path=out_html)
    stale = data["items"][[item["id"] for item in data["items"]].index(STALE_ITEM)]["byRegion"]["seoul"]
    return {"staleDays": stale["staleDays"], "observedDate": stale["observedDate"],
            "fetchedDate": stale["fetchedDate"], "price": stale["latest"]["price"]}


def build_study_preview(out_html=None, out_config=None):
    """임시 제휴·후원 설정으로 시험 공부 화면을 빌드한다(실제 파일·설정은 그대로)."""
    out_html = out_html or STUDY_HTML
    out_config = out_config or STUDY_CONFIG
    sample = {
        "version": 1,
        "studyAffiliate": {
            "title": "수험서 구매",
            "description": "정보보안기사·CPPG 수험서를 서점에서 확인합니다.",
            "buttonLabel": "수험서 보기",
            "url": "https://www.yes24.com/Product/Goods/0000000",
            "disclosure": "이 링크를 통해 구매하면 운영자가 수수료를 받을 수 있습니다",
        },
        "supportLink": {
            "title": "이 사이트 돕기",
            "description": "서버·수집 비용을 후원으로 이어갑니다.",
            "buttonLabel": "후원하기",
            "url": "https://buymeacoffee.com/infosec-archive",
            "kind": "후원",
        },
    }
    with open(out_config, "w", encoding="utf-8") as handle:
        json.dump(sample, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    env = dict(os.environ, MONETIZATION_CONFIG=out_config, STUDY_OUT_HTML=out_html)
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "build_study_html.py")],
                   cwd=BASE_DIR, env=env, check=True)
    return monetization.load_config(out_config)


def clean():
    for path in PREVIEW_FILES:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
        print("미리보기 파일을 지웠습니다.")
        raise SystemExit(0)
    grocery = build_grocery_preview()
    study = build_study_preview()
    print("미리보기 생성 완료: %s · %s · %s" % (GROCERY_HTML, STUDY_HTML, STUDY_CONFIG))
    print("  승계값: %s 조사 · %d일 전 기준 · %s원" % (grocery["observedDate"], grocery["staleDays"],
                                                format(grocery["price"], ",")))
    print("  제휴 카드: %s / 후원: %s" % (bool(study["studyAffiliate"]["url"]),
                                     bool(study["supportLink"]["url"])))

"""2차 대량 요약 배치 실행기 (엑사원 API 호출 상한 엄수 / 시간 예산 내 클린 종료)

사용법: python3 run_batch2.py <총허용HTTP수> <이번실행시간예산초>
- HTTP 호출 수를 총 허용치까지 하드 캡하고, batch2_state.json에 누적 기록.
- 배치마다 ai_cache.json에 즉시 저장되므로 중단 후 이어서 실행 가능.
"""
import os
import sys
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import ai_enricher
import crawler

TOTAL_ALLOWED = int(sys.argv[1]) if len(sys.argv) > 1 else 25
BUDGET_S = int(sys.argv[2]) if len(sys.argv) > 2 else 240
BATCH_SIZE = int(os.environ.get('EXAONE_BATCH', '5'))
STATE_FILE = os.path.join(BASE, 'batch2_state.json')

_orig_urlopen = urllib.request.urlopen
_counter = {'n': 0}


class QuotaGuard(BaseException):
    pass


READ_TIMEOUT = int(os.environ.get('EXAONE_TIMEOUT', '200'))


def guarded_urlopen(req, *args, **kwargs):
    if _counter['n'] >= max(0, TOTAL_ALLOWED - used_before):
        raise QuotaGuard()
    if time.time() + READ_TIMEOUT + 8 > RUN_DEADLINE:
        raise QuotaGuard()
    kwargs['timeout'] = READ_TIMEOUT
    _counter['n'] += 1
    print(f"[HTTP 누적 {used_before + _counter['n']}/{TOTAL_ALLOWED}] {time.strftime('%H:%M:%S')}", flush=True)
    return _orig_urlopen(req, *args, **kwargs)


state = {'http_total': 0, 'runs': []}
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception:
        pass
used_before = state.get('http_total', 0)
_today = time.strftime('%Y-%m-%d')
if state.get('date') != _today:
    # 일일 한도는 날짜가 바뀌면 초기화된다.
    used_before = 0
    state['http_total'] = 0
    state['date'] = _today

urllib.request.urlopen = guarded_urlopen

jobs_path = os.path.join(BASE, 'jobs.json')
with open(jobs_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

start_cache = len(ai_enricher.load_cache())
print(f"시작: 전체 {len(jobs)}건 / 캐시 {start_cache}건 / 누적 HTTP {used_before}/{TOTAL_ALLOWED}", flush=True)

RUN_DEADLINE = time.time() + BUDGET_S
while _counter['n'] + used_before < TOTAL_ALLOWED and time.time() + READ_TIMEOUT + 8 < RUN_DEADLINE:
    before = len(ai_enricher.load_cache())
    try:
        jobs = ai_enricher.enrich_jobs_batch(jobs, max_calls=1, batch_size=BATCH_SIZE)
    except QuotaGuard:
        print(">>> 호출 상한 도달.", flush=True)
        break
    after = len(ai_enricher.load_cache())
    if after <= before:
        print(">>> 진행 없음(한도/오류) — 중단.", flush=True)
        break

end_cache = len(ai_enricher.load_cache())
print(f"이번 실행: HTTP {_counter['n']}회 / 캐시 {start_cache} -> {end_cache} (신규 {end_cache - start_cache}건)", flush=True)

# 캐시 병합(호출 없이)
jobs = ai_enricher.enrich_jobs_batch(jobs, api_key=None, max_calls=0, batch_size=BATCH_SIZE)

with open(jobs_path, 'w', encoding='utf-8') as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)

kst = timezone(timedelta(hours=9))
now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
with open(os.path.join(BASE, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(crawler.generate_html(jobs, now_kst))

state['http_total'] = used_before + _counter['n']
state['date'] = _today
state['runs'].append({'at': now_kst, 'http': _counter['n'], 'cache': end_cache})
with open(STATE_FILE, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

summary = {
    'http_this_run': _counter['n'],
    'http_total': state['http_total'],
    'cache_before': start_cache,
    'cache_after': end_cache,
    'new_summaries_this_run': end_cache - start_cache,
    'jobs_total': len(jobs),
    'jobs_with_summary': sum(1 for j in jobs if j.get('summary')),
    'generated_at': now_kst,
}
with open(os.path.join(BASE, 'batch2_result.json'), 'w', encoding='utf-8') as f:
    json.dump({'latest': summary, 'state': state}, f, ensure_ascii=False, indent=2)
print(json.dumps(summary, ensure_ascii=False), flush=True)

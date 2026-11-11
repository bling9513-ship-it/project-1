import os
import json
import time
import urllib.request
import urllib.error
import re

CACHE_FILE = os.path.join(os.path.dirname(__file__), 'ai_cache.json')
ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')

def get_api_key():
    key = os.environ.get('EXAONE_API_KEY')
    if key:
        return key.strip()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('EXAONE_API_KEY='):
                    return line.strip().split('=', 1)[1].strip()
    return None

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load AI cache: {e}")
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save AI cache: {e}")

def get_cache_key(job):
    url = job.get('url', '').strip()
    if url:
        return url
    return f"{job.get('company', '').strip()}:{job.get('title', '').strip()}"

def enrich_jobs_batch(jobs, api_key=None, max_calls=10, batch_size=5):
    if not api_key:
        api_key = get_api_key()
        
    cache = load_cache()
    
    # Identify jobs needing enrichment
    unprocessed_jobs = []
    for job in jobs:
        key = get_cache_key(job)
        if key not in cache:
            unprocessed_jobs.append(job)
            
    print(f"Total jobs: {len(jobs)}, Cached: {len(cache)}, Needing enrichment: {len(unprocessed_jobs)}")
    
    # Pre-apply existing cache to all jobs
    for job in jobs:
        key = get_cache_key(job)
        if key in cache:
            job['summary'] = cache[key].get('summary', '')
            job['tags'] = cache[key].get('tags', [])

    if not unprocessed_jobs or not api_key:
        return jobs
        
    calls_made = 0
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    for i in range(0, min(len(unprocessed_jobs), max_calls * batch_size), batch_size):
        chunk = unprocessed_jobs[i:i + batch_size]
        items_desc = []
        for idx, j in enumerate(chunk):
            items_desc.append(f"공고 {idx + 1}:\n- ID: {idx + 1}\n- 회사: {j.get('company', '')}\n- 공고명: {j.get('title', '')}")
            
        prompt = (
            f"다음 정보보안 채용공고 {len(chunk)}건의 회사명과 공고명을 분석하여, 각 공고의 핵심 직무 요약(1문장, 35~50자 내외)과 "
            "정밀 기술/직무 해시태그(3~4개, 예: #모의해킹, #ISMS-P, #클라우드보안, #보안관제, #취약점분석, #개인정보보호 등)를 "
            "JSON 배열로 추출해줘. 반드시 오직 순수 JSON 배열 포맷만 출력해줘.\n\n"
            + "\n\n".join(items_desc)
            + "\n\n출력 포맷:\n"
            "[\n"
            "  {\"id\": 1, \"summary\": \"...\", \"tags\": [\"#태그1\", \"#태그2\", \"#태그3\"]}\n"
            "]"
        )
        
        payload = {
            'model': 'k-exaone_v2.5',
            'messages': [
                {'role': 'system', 'content': '당신은 정보보안 전문 채용 분석 AI입니다. 지정된 JSON 배열 포맷으로만 답변합니다.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 2500,
            'temperature': 0.2,
            'reasoning_effort': 'low'
        }
        
        success = False
        for retry in range(1):
            try:
                req = urllib.request.Request(
                    'https://api.exaone.ai/v1/chat/completions',
                    data=json.dumps(payload).encode('utf-8'),
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    content = data['choices'][0]['message']['content'].strip()
                    
                    if '```' in content:
                        match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                        if match:
                            content = match.group(1)
                        else:
                            match2 = re.search(r'(\[.*?\])', content, re.DOTALL)
                            if match2:
                                content = match2.group(1)
                                
                    results = json.loads(content)
                    for res in results:
                        idx = res.get('id', 0) - 1
                        if 0 <= idx < len(chunk):
                            target_job = chunk[idx]
                            k = get_cache_key(target_job)
                            summary = res.get('summary', '').strip()
                            raw_tags = res.get('tags', [])
                            tags = []
                            for t in raw_tags:
                                t = t.strip()
                                if t and not t.startswith('#'):
                                    t = '#' + t
                                if t and t not in tags:
                                    tags.append(t)
                                    
                            cache[k] = {
                                'summary': summary,
                                'tags': tags,
                                'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                            target_job['summary'] = summary
                            target_job['tags'] = tags
                            
                save_cache(cache)
                calls_made += 1
                success = True
                print(f"Successfully enriched batch {calls_made}: {len(chunk)} jobs (Total cached: {len(cache)})")
                time.sleep(1.5)
                break
                
            except urllib.error.HTTPError as e:
                print(f"EXAONE API HTTP error: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
                if e.code == 429:
                    print("Rate limit reached. Stopping enrichment.")
                    return jobs
            except Exception as e:
                print(f"Error enriching batch (attempt {retry + 1}): {e}")
                time.sleep(2)
                
        if not success:
            print("Batch failed after retries, continuing.")
            
    # Apply all cache entries to jobs
    for job in jobs:
        key = get_cache_key(job)
        if key in cache:
            job['summary'] = cache[key].get('summary', '')
            job['tags'] = cache[key].get('tags', [])
            
    print(f"Enrichment cycle done. Total calls made: {calls_made}, Total cached: {len(cache)}")
    return jobs

if __name__ == '__main__':
    jobs_path = os.path.join(os.path.dirname(__file__), 'jobs.json')
    with open(jobs_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
        
    enriched = enrich_jobs_batch(jobs, max_calls=10, batch_size=5)
    with open(jobs_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    print("Done enrichment run.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정보보안 채용공고 자동 수집 & 중복 제거 크롤러
대상 플랫폼: 원티드 (Wanted), 점핏 (Jumpit), 사람인 (Saramin)
대상 키워드: 정보보안, 정보보호, 취약점 진단, 모의해킹
"""

import urllib.request
import urllib.parse
import json
import re
import html
from datetime import datetime, timezone, timedelta

KEYWORDS = ["정보보안", "정보보호", "취약점 진단", "모의해킹"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/"
}

def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()

def normalize_key(company, title):
    """중복 제거를 위한 정규화 키 생성"""
    c = clean_text(company)
    c = re.sub(r"[\(주\)|㈜|주식회사|\s]", "", c).lower()
    
    t = clean_text(title)
    # 신입, 경력, 대괄호 태그 제거하여 제목 유사도 매칭
    t = re.sub(r"\[.*?\]|\(.*?\)|<.*?>", "", t)
    t = re.sub(r"[\s\-_/|·]", "", t).lower()
    return f"{c}_{t[:12]}"

def fetch_jumpit(keyword):
    """점핏 (Jumpit) API 수집"""
    results = []
    encoded = urllib.parse.quote(keyword)
    url = f"https://api.jumpit.co.kr/api/positions?keyword={encoded}&page=1"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode("utf-8"))
            positions = data.get("result", {}).get("positions", [])
            for p in positions:
                results.append({
                    "platform": "점핏",
                    "company": clean_text(p.get("companyName")),
                    "title": clean_text(p.get("title")),
                    "url": f"https://www.jumpit.co.kr/position/{p.get('id')}",
                    "location": clean_text(p.get("location", "")),
                    "keyword": keyword
                })
    except Exception as e:
        print(f"[Jumpit] Error for '{keyword}': {e}")
    return results

def fetch_wanted(keyword):
    """원티드 (Wanted) API 수집"""
    results = []
    encoded = urllib.parse.quote(keyword)
    url = f"https://www.wanted.co.kr/api/chaos/navigation/v1/results?query={encoded}&years=-1&country=kr"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode("utf-8"))
            items = data.get("data", [])
            for item in items:
                results.append({
                    "platform": "원티드",
                    "company": clean_text(item.get("company", {}).get("name")),
                    "title": clean_text(item.get("position")),
                    "url": f"https://www.wanted.co.kr/wd/{item.get('id')}",
                    "location": clean_text(item.get("address", {}).get("location", "")),
                    "keyword": keyword
                })
    except Exception as e:
        print(f"[Wanted] Error for '{keyword}': {e}")
    return results

def fetch_saramin(keyword):
    """사람인 (Saramin) 검색 결과 수집"""
    results = []
    encoded = urllib.parse.quote(keyword)
    url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword={encoded}&recruitPage=1"
    
    try:
        saramin_headers = dict(HEADERS)
        saramin_headers["Referer"] = "https://www.saramin.co.kr/"
        req = urllib.request.Request(url, headers=saramin_headers)
        with urllib.request.urlopen(req, timeout=8) as res:
            page = res.read().decode("utf-8", errors="ignore")
            
            pattern = r'<strong class="corp_name"[^>]*>.*?<a[^>]*>(.*?)</a>.*?<h2 class="job_tit"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>.*?<span>(.*?)</span>'
            matches = re.findall(pattern, page, re.DOTALL)
            
            for m in matches:
                corp = clean_text(m[0])
                link_part = html.unescape(m[1]).split("&searchType")[0]
                if not link_part.startswith("http"):
                    link = "https://www.saramin.co.kr" + link_part
                else:
                    link = link_part
                title = clean_text(m[2])
                
                results.append({
                    "platform": "사람인",
                    "company": corp,
                    "title": title,
                    "url": link,
                    "location": "",
                    "keyword": keyword
                })
    except Exception as e:
        print(f"[Saramin] Error for '{keyword}': {e}")
    return results

def collect_all_jobs():
    raw_jobs = []
    print("=== 채용 정보 수집 시작 ===")
    for kw in KEYWORDS:
        print(f"-> 키워드 탐색 중: '{kw}'")
        jumpit_jobs = fetch_jumpit(kw)
        wanted_jobs = fetch_wanted(kw)
        saramin_jobs = fetch_saramin(kw)
        
        print(f"   [점핏: {len(jumpit_jobs)}건, 원티드: {len(wanted_jobs)}건, 사람인: {len(saramin_jobs)}건]")
        raw_jobs.extend(jumpit_jobs)
        raw_jobs.extend(wanted_jobs)
        raw_jobs.extend(saramin_jobs)
        
    print(f"\n총 원시 수집 건수: {len(raw_jobs)}건")
    
    # 중복 제거 로직
    deduped = {}
    for job in raw_jobs:
        if not job["company"] or not job["title"]:
            continue
            
        key = normalize_key(job["company"], job["title"])
        if key not in deduped:
            deduped[key] = {
                "company": job["company"],
                "title": job["title"],
                "url": job["url"],
                "platforms": [job["platform"]],
                "keywords": [job["keyword"]],
                "location": job["location"]
            }
        else:
            if job["platform"] not in deduped[key]["platforms"]:
                deduped[key]["platforms"].append(job["platform"])
            if job["keyword"] not in deduped[key]["keywords"]:
                deduped[key]["keywords"].append(job["keyword"])
            if not deduped[key]["location"] and job["location"]:
                deduped[key]["location"] = job["location"]
                
    job_list = list(deduped.values())
    print(f"중복 제거 후 최종 고유 공고: {len(job_list)}건")
    return job_list

def generate_html(jobs, update_time_str):
    """GitHub Pages 배포용 정적 웹페이지 생성 (검색, 필터, 리다이렉트 지원)"""
    jobs_json_str = json.dumps(jobs, ensure_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>정보보안 채용공고 피드 | 자동 수집 대시보드</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-hover: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --wanted: #3b82f6;
      --jumpit: #10b981;
      --saramin: #f97316;
      --tag-bg: #0284c7;
      --border: #334155;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px 16px;
    }}
    .container {{
      max-width: 1040px;
      margin: 0 auto;
    }}
    header {{
      text-align: center;
      margin-bottom: 28px;
    }}
    header h1 {{
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
      color: #fff;
    }}
    header p {{
      color: var(--text-muted);
      font-size: 14px;
    }}
    .time-badge {{
      display: inline-block;
      margin-top: 8px;
      padding: 4px 12px;
      background: rgba(56, 189, 248, 0.1);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
    }}
    .controls {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 24px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .search-bar {{
      width: 100%;
      padding: 12px 16px;
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 10px;
      color: #fff;
      font-size: 15px;
      outline: none;
      transition: border-color 0.2s;
    }}
    .search-bar:focus {{
      border-color: var(--accent);
    }}
    .filter-group {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      font-size: 13px;
    }}
    .filter-label {{
      color: var(--text-muted);
      font-weight: 600;
      margin-right: 4px;
    }}
    .chip {{
      padding: 6px 12px;
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 20px;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 13px;
      transition: all 0.15s ease;
      user-select: none;
    }}
    .chip.active {{
      background: var(--accent);
      color: #0f172a;
      font-weight: 700;
      border-color: var(--accent);
    }}
    .count-stat {{
      color: var(--text-muted);
      font-size: 14px;
      margin-bottom: 14px;
      padding: 0 4px;
      font-weight: 600;
    }}
    .count-stat span {{
      color: var(--accent);
      font-weight: 700;
    }}
    .job-list {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }}
    @media (min-width: 768px) {{
      .job-list {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}
    .job-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
      cursor: pointer;
      transition: transform 0.15s ease, background 0.15s ease, border-color 0.15s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      text-decoration: none;
      color: inherit;
    }}
    .job-card:hover {{
      transform: translateY(-2px);
      background: var(--card-hover);
      border-color: var(--accent);
    }}
    .job-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
      margin-bottom: 8px;
    }}
    .company-name {{
      font-size: 14px;
      font-weight: 700;
      color: var(--text-muted);
    }}
    .platform-badges {{
      display: flex;
      gap: 4px;
      flex-shrink: 0;
    }}
    .badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 6px;
      color: #fff;
    }}
    .badge-원티드 {{ background-color: var(--wanted); }}
    .badge-점핏 {{ background-color: var(--jumpit); }}
    .badge-사람인 {{ background-color: var(--saramin); }}
    .job-title {{
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      line-height: 1.4;
      margin-bottom: 12px;
    }}
    .job-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      font-size: 12px;
    }}
    .keyword-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }}
    .tag {{
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
    }}
    .click-hint {{
      color: var(--text-muted);
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .no-results {{
      text-align: center;
      padding: 48px 16px;
      color: var(--text-muted);
      font-size: 16px;
      grid-column: 1 / -1;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🛡️ 정보보안 채용공고 모음</h1>
      <p>원티드 · 점핏 · 사람인 실시간 자동 수집 및 중복 제거 피드</p>
      <div class="time-badge">마지막 갱신: {update_time_str}</div>
    </header>

    <div class="controls">
      <input type="text" id="searchInput" class="search-bar" placeholder="🔍 회사명 또는 공고명으로 실시간 검색...">
      
      <div class="filter-group">
        <span class="filter-label">키워드:</span>
        <div class="chip active" data-filter="keyword" data-val="all">전체</div>
        <div class="chip" data-filter="keyword" data-val="정보보안">정보보안</div>
        <div class="chip" data-filter="keyword" data-val="정보보호">정보보호</div>
        <div class="chip" data-filter="keyword" data-val="취약점 진단">취약점 진단</div>
        <div class="chip" data-filter="keyword" data-val="모의해킹">모의해킹</div>
      </div>

      <div class="filter-group">
        <span class="filter-label">플랫폼:</span>
        <div class="chip active" data-filter="platform" data-val="all">전체 플랫폼</div>
        <div class="chip" data-filter="platform" data-val="원티드">원티드</div>
        <div class="chip" data-filter="platform" data-val="점핏">점핏</div>
        <div class="chip" data-filter="platform" data-val="사람인">사람인</div>
      </div>
    </div>

    <div class="count-stat">검색된 공고: <span id="countNum">0</span>개 (공고 클릭 시 원문 사이트로 바로 이동)</div>

    <div class="job-list" id="jobList"></div>
  </div>

  <script>
    const JOBS = {jobs_json_str};
    let activeKeyword = 'all';
    let activePlatform = 'all';
    let searchTerm = '';

    const jobListEl = document.getElementById('jobList');
    const countNumEl = document.getElementById('countNum');
    const searchInput = document.getElementById('searchInput');

    function renderJobs() {{
      const filtered = JOBS.filter(job => {{
        // 키워드 필터
        if (activeKeyword !== 'all' && !job.keywords.includes(activeKeyword)) {{
          return false;
        }}
        // 플랫폼 필터
        if (activePlatform !== 'all' && !job.platforms.includes(activePlatform)) {{
          return false;
        }}
        // 검색어 필터
        if (searchTerm) {{
          const term = searchTerm.toLowerCase();
          const matchCompany = job.company.toLowerCase().includes(term);
          const matchTitle = job.title.toLowerCase().includes(term);
          if (!matchCompany && !matchTitle) return false;
        }}
        return true;
      }});

      countNumEl.textContent = filtered.length;

      if (filtered.length === 0) {{
        jobListEl.innerHTML = '<div class="no-results">조건에 일치하는 채용공고가 없습니다.</div>';
        return;
      }}

      jobListEl.innerHTML = filtered.map(job => {{
        const badges = job.platforms.map(p => `<span class="badge badge-${{p}}">${{p}}</span>`).join('');
        const tags = job.keywords.map(k => `<span class="tag">#${{k}}</span>`).join('');
        
        return `
          <a class="job-card" href="${{job.url}}" target="_blank" rel="noopener noreferrer">
            <div>
              <div class="job-header">
                <span class="company-name">${{escapeHtml(job.company)}}</span>
                <div class="platform-badges">${{badges}}</div>
              </div>
              <div class="job-title">${{escapeHtml(job.title)}}</div>
            </div>
            <div class="job-footer">
              <div class="keyword-tags">${{tags}}</div>
              <div class="click-hint">공고 보기 ↗</div>
            </div>
          </a>
        `;
      }}).join('');
    }}

    function escapeHtml(str) {{
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    // 필터 이벤트 바인딩
    document.querySelectorAll('.chip').forEach(chip => {{
      chip.addEventListener('click', e => {{
        const type = chip.getAttribute('data-filter');
        const val = chip.getAttribute('data-val');

        document.querySelectorAll(`.chip[data-filter="${{type}}"]`).forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        if (type === 'keyword') activeKeyword = val;
        if (type === 'platform') activePlatform = val;
        renderJobs();
      }});
    }});

    searchInput.addEventListener('input', e => {{
      searchTerm = e.target.value.trim();
      renderJobs();
    }});

    // 최초 렌더링
    renderJobs();
  </script>
</body>
</html>
"""
    return html_content

def generate_readme(jobs, update_time_str):
    """GitHub 저장소 메인에 노출될 마크다운 테이블 리스트 생성"""
    lines = [
        "# 🛡️ 정보보안 채용공고 리스트 (자동 업데이트)",
        "",
        f"> **마지막 업데이트**: `{update_time_str}` (매일 자동 수집)",
        f"> **현재 등록된 공고**: 총 **{len(jobs)}**개 (중복 제거 완료)",
        "",
        "| 회사명 | 공고명 (클릭 시 이동) | 플랫폼 | 매칭 키워드 |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
    for job in jobs:
        platforms_str = ", ".join(job["platforms"])
        keywords_str = ", ".join([f"`{k}`" for k in job["keywords"]])
        # 마크다운 링크 파이프 문자 이스케이프
        title_escaped = job["title"].replace("|", "\\|")
        company_escaped = job["company"].replace("|", "\\|")
        lines.append(f"| **{company_escaped}** | [{title_escaped}]({job['url']}) | {platforms_str} | {keywords_str} |")
        
    lines.append("")
    lines.append("---")
    lines.append("💡 **GitHub Pages 웹 대시보드**: 저장소의 `Settings > Pages`에서 활성화하면 검색/필터 기능이 있는 웹사이트로 이용할 수 있습니다.")
    return "\n".join(lines)

def main():
    jobs = collect_all_jobs()
    
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    
    # 1. JSON 파일 저장
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print("-> 'jobs.json' 저장 완료")
    
    # 2. index.html 생성
    html_data = generate_html(jobs, now_kst)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_data)
    print("-> 'index.html' 웹 대시보드 생성 완료")
    
    # 3. README.md 생성
    readme_data = generate_readme(jobs, now_kst)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_data)
    print("-> 'README.md' 저장 완료")
    
    print("\n모든 산출물이 성공적으로 생성되었습니다!")

if __name__ == "__main__":
    main()

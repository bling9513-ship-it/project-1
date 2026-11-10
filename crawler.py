#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정보보안 채용공고 자동 수집 & 중복 제거 크롤러 (키워드별 분리 뷰 지원)
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
    """GitHub Pages 배포용 정적 웹페이지 생성 (키워드별 분리 모아보기 + 필터 검색)"""
    jobs_json_str = json.dumps(jobs, ensure_ascii=False)
    
    # 키워드별 건수 계산
    kw_counts = {kw: sum(1 for j in jobs if kw in j.get("keywords", [])) for kw in KEYWORDS}
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>정보보안 채용공고 피드 | 키워드별 분리 대시보드</title>
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
      margin-bottom: 24px;
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
    .view-mode-tabs {{
      display: flex;
      justify-content: center;
      gap: 8px;
      margin-bottom: 20px;
    }}
    .tab-btn {{
      padding: 8px 18px;
      background: #1e293b;
      border: 1px solid var(--border);
      border-radius: 10px;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      transition: all 0.15s ease;
    }}
    .tab-btn.active {{
      background: var(--accent);
      color: #0f172a;
      border-color: var(--accent);
      font-weight: 800;
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
    .section-title {{
      font-size: 20px;
      font-weight: 800;
      color: #fff;
      margin: 28px 0 12px 0;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .section-title span.badge-cnt {{
      font-size: 13px;
      padding: 3px 10px;
      border-radius: 12px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
    }}
    .job-list {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
      margin-bottom: 20px;
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
      padding: 16px;
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
      font-size: 15px;
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
      <h1>🛡️ 정보보안 직무 채용공고 모음</h1>
      <p>원티드 · 점핏 · 사람인 실시간 자동 수집 및 중복 제거 피드</p>
      <div class="time-badge">마지막 갱신: {update_time_str}</div>
    </header>

    <div class="view-mode-tabs">
      <button class="tab-btn active" id="tabSections">📑 키워드별 분리 모아보기</button>
      <button class="tab-btn" id="tabFilter">🔍 통합 검색 & 필터</button>
    </div>

    <div class="controls" id="filterControls" style="display: none;">
      <input type="text" id="searchInput" class="search-bar" placeholder="🔍 회사명 또는 공고명으로 실시간 검색...">
      
      <div class="filter-group">
        <span class="filter-label">키워드:</span>
        <div class="chip active" data-filter="keyword" data-val="all">전체 ({len(jobs)})</div>
        <div class="chip" data-filter="keyword" data-val="정보보안">정보보안 ({kw_counts.get("정보보안", 0)})</div>
        <div class="chip" data-filter="keyword" data-val="정보보호">정보보호 ({kw_counts.get("정보보호", 0)})</div>
        <div class="chip" data-filter="keyword" data-val="취약점 진단">취약점 진단 ({kw_counts.get("취약점 진단", 0)})</div>
        <div class="chip" data-filter="keyword" data-val="모의해킹">모의해킹 ({kw_counts.get("모의해킹", 0)})</div>
      </div>

      <div class="filter-group">
        <span class="filter-label">플랫폼:</span>
        <div class="chip active" data-filter="platform" data-val="all">전체 플랫폼</div>
        <div class="chip" data-filter="platform" data-val="원티드">원티드</div>
        <div class="chip" data-filter="platform" data-val="점핏">점핏</div>
        <div class="chip" data-filter="platform" data-val="사람인">사람인</div>
      </div>
    </div>

    <div class="count-stat" id="countStat">공고 카드 클릭 시 원문 사이트로 바로 이동합니다.</div>

    <div id="contentArea"></div>
  </div>

  <script>
    const JOBS = {jobs_json_str};
    const KEYWORDS = ["정보보안", "정보보호", "취약점 진단", "모의해킹"];
    const ICONS = {{
      "정보보안": "🛡️",
      "정보보호": "🔒",
      "취약점 진단": "🔍",
      "모의해킹": "💻"
    }};

    let viewMode = 'sections'; // 'sections' or 'filter'
    let activeKeyword = 'all';
    let activePlatform = 'all';
    let searchTerm = '';

    const contentArea = document.getElementById('contentArea');
    const filterControls = document.getElementById('filterControls');
    const countStat = document.getElementById('countStat');
    const searchInput = document.getElementById('searchInput');

    function createJobCard(job) {{
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
            <div class="click-hint">원문 보기 ↗</div>
          </div>
        </a>
      `;
    }}

    function renderView() {{
      if (viewMode === 'sections') {{
        filterControls.style.display = 'none';
        countStat.textContent = `4개 키워드별로 분류된 총 ${{JOBS.length}}건의 공고입니다. (카드 클릭 시 원문 이동)`;
        
        let html = '';
        KEYWORDS.forEach(kw => {{
          const icon = ICONS[kw] || '🏷️';
          const list = JOBS.filter(j => j.keywords && j.keywords.includes(kw));
          
          html += `
            <div class="section-title">
              <span>${{icon}} ${{kw}}</span>
              <span class="badge-cnt">${{list.length}}건</span>
            </div>
            <div class="job-list">
              ${{list.map(createJobCard).join('')}}
            </div>
          `;
        }});
        contentArea.innerHTML = html;
      }} else {{
        filterControls.style.display = 'flex';
        const filtered = JOBS.filter(job => {{
          if (activeKeyword !== 'all' && !job.keywords.includes(activeKeyword)) return false;
          if (activePlatform !== 'all' && !job.platforms.includes(activePlatform)) return false;
          if (searchTerm) {{
            const term = searchTerm.toLowerCase();
            const matchCompany = job.company.toLowerCase().includes(term);
            const matchTitle = job.title.toLowerCase().includes(term);
            if (!matchCompany && !matchTitle) return false;
          }}
          return true;
        }});

        countStat.innerHTML = `검색 및 필터된 공고: <span>${{filtered.length}}</span>개 (공고 클릭 시 원문 사이트로 바로 이동)`;

        if (filtered.length === 0) {{
          contentArea.innerHTML = '<div class="no-results">조건에 일치하는 채용공고가 없습니다.</div>';
          return;
        }}

        contentArea.innerHTML = `<div class="job-list">${{filtered.map(createJobCard).join('')}}</div>`;
      }}
    }}

    function escapeHtml(str) {{
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    document.getElementById('tabSections').addEventListener('click', () => {{
      viewMode = 'sections';
      document.getElementById('tabSections').classList.add('active');
      document.getElementById('tabFilter').classList.remove('active');
      renderView();
    }});

    document.getElementById('tabFilter').addEventListener('click', () => {{
      viewMode = 'filter';
      document.getElementById('tabFilter').classList.add('active');
      document.getElementById('tabSections').classList.remove('active');
      renderView();
    }});

    document.querySelectorAll('.chip').forEach(chip => {{
      chip.addEventListener('click', () => {{
        const type = chip.getAttribute('data-filter');
        const val = chip.getAttribute('data-val');

        document.querySelectorAll(`.chip[data-filter="${{type}}"]`).forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        if (type === 'keyword') activeKeyword = val;
        if (type === 'platform') activePlatform = val;
        renderView();
      }});
    }});

    searchInput.addEventListener('input', e => {{
      searchTerm = e.target.value.trim();
      renderView();
    }});

    // 초기 렌더링: 키워드별 분리 모아보기 기본
    renderView();
  </script>
</body>
</html>
"""
    return html_content

def generate_readme(jobs, update_time_str):
    """GitHub 저장소 메인에 노출될 마크다운: 4대 키워드별 명확한 분리 테이블"""
    keyword_jobs = {kw: [] for kw in KEYWORDS}
    for job in jobs:
        for kw in job.get("keywords", []):
            if kw in keyword_jobs:
                keyword_jobs[kw].append(job)

    icons = {
        "정보보안": "🛡️",
        "정보보호": "🔒",
        "취약점 진단": "🔍",
        "모의해킹": "💻"
    }

    lines = [
        "# 🛡️ 정보보안 직무 채용공고 피드 (키워드별 분류)",
        "",
        f"> **마지막 업데이트**: `{update_time_str}` (매일 06:30 KST 자동 수집)",
        f"> **전체 고유 공고**: 총 **{len(jobs)}**개 (중복 제거 완료)",
        "",
        "### 📌 키워드별 바로가기 목차",
        "| 키워드 | 등록 공고 수 | 목차 링크 |",
        "| :--- | :---: | :--- |"
    ]

    for kw in KEYWORDS:
        count = len(keyword_jobs[kw])
        anchor = kw.replace(" ", "-")
        icon = icons.get(kw, "🏷️")
        lines.append(f"| {icon} **{kw}** | **{count}개** | [공고 목록 바로가기](#-{anchor}-{count}건) |")

    lines.append("")
    lines.append("---")
    lines.append("")

    for kw in KEYWORDS:
        kw_list = keyword_jobs[kw]
        icon = icons.get(kw, "🏷️")
        lines.append(f"## {icon} {kw} ({len(kw_list)}건)")
        lines.append("")
        if not kw_list:
            lines.append("_현재 등록된 공고가 없습니다._")
            lines.append("")
            continue

        lines.append("| 회사명 | 공고명 (클릭 시 이동) | 플랫폼 | 상세 태그 |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for job in kw_list:
            platforms_str = ", ".join(job["platforms"])
            keywords_str = ", ".join([f"`{k}`" for k in job["keywords"]])
            title_escaped = job["title"].replace("|", "\\|")
            company_escaped = job["company"].replace("|", "\\|")
            lines.append(f"| **{company_escaped}** | [{title_escaped}]({job['url']}) | {platforms_str} | {keywords_str} |")
        
        lines.append("")
        lines.append("[⬆️ 맨 위로 이동](#-정보보안-직무-채용공고-피드-키워드별-분류)")
        lines.append("")
        lines.append("---")
        lines.append("")

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
    print("-> 'index.html' 키워드 분리 대시보드 생성 완료")
    
    # 3. README.md 생성
    readme_data = generate_readme(jobs, now_kst)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_data)
    print("-> 'README.md' 키워드 분리 테이블 저장 완료")
    
    print("\n모든 산출물이 성공적으로 생성되었습니다!")

if __name__ == "__main__":
    main()

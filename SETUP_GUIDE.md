# 🚀 GitHub 무료 채용공고 서비스 배포 가이드 (3분 완성)

이 프로젝트는 **서버 비용 0원**으로 매일 아침 채용공고를 자동 수집하고, 웹사이트로 서비스할 수 있도록 구성되어 있습니다.

---

### 1단계: GitHub 저장소(Repository) 만들기
1. [GitHub](https://github.com)에 로그인 후 우측 상단 `+` 버튼 -> **New repository**를 누릅니다.
2. Repository name에 원하는 이름(예: `security-job-board`)을 적고 **Public**으로 설정한 뒤 생성합니다.
   *(Public 저장소는 GitHub Actions와 GitHub Pages가 무제한 무료입니다)*

### 2단계: 파일 업로드 (Git Push)
터미널에서 이 폴더(`infosec-job-crawler`)로 이동 후 아래 명령어를 입력합니다.

```bash
git init
git add .
git commit -m "feat: 초기 채용공고 크롤러 및 웹 대시보드 구축"
git branch -M main
git remote add origin https://github.com/{사용자이름}/{저장소이름}.git
git push -u origin main
```

### 3단계: GitHub Pages 무료 웹사이트 켜기
1. 생성한 GitHub 저장소 페이지의 상단 메뉴에서 **Settings**를 클릭합니다.
2. 좌측 사이드바에서 **Pages**를 클릭합니다.
3. **Build and deployment > Source**에서 `Deploy from a branch`를 선택합니다.
4. **Branch**를 `main` / `/(root)`로 설정하고 **Save**를 누릅니다.
5. 1~2분 뒤 상단에 생성된 전용 웹사이트 주소(`https://{사용자이름}.github.io/{저장소이름}/`)로 접속하면 끝!

---

### 💡 동작 방식
- **자동 업데이트**: 매일 아침 7시(KST)마다 GitHub Actions가 자동으로 실행되어 새 공고를 수집하고 커밋합니다.
- **수동 즉시 실행**: 저장소의 `Actions` 탭 -> `Update Security Jobs` -> `Run workflow` 버튼을 누르면 언제든 즉시 새 공고를 긁어옵니다.
- **클릭 리다이렉션**: 웹 대시보드나 README에서 공고를 누르면 해당 채용 플랫폼의 상세 원문 페이지로 바로 이동합니다.

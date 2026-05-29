# 🚀 배포 가이드 (비개발자용, 처음부터 끝까지)

이 가이드를 따라하면 매일 자동으로 통신 3사 요금제를 크롤링하고,
웹 대시보드에서 비교할 수 있는 시스템이 완성됩니다.

소요 시간: 약 30~40분

---

## 📋 준비물

- 인터넷 연결된 PC (지금 사용 중인 PC면 됩니다)
- 이메일 주소 1개 (GitHub 가입용)

---

## STEP 1: GitHub 계정 만들기 (5분)

1. 브라우저에서 **https://github.com** 접속
2. 우측 상단 **Sign up** 클릭
3. 이메일, 비밀번호, 사용자명 입력 후 가입 완료
4. 이메일 인증 (받은 메일에서 인증 버튼 클릭)

---

## STEP 2: Git 설치하기 (5분)

1. 브라우저에서 **https://git-scm.com/download/win** 접속
2. 자동으로 다운로드 시작됨 → 다운로드된 파일 실행
3. 설치 화면에서 **모두 "Next" 클릭** → 마지막에 "Install" 클릭
4. 설치 완료 후 PC 재시작 (권장)

### 설치 확인
1. 키보드에서 `Windows키 + R` 누르기
2. `cmd` 입력 후 Enter
3. 검은 창에 아래 입력 후 Enter:
```
git --version
```
4. `git version 2.xx.x` 같은 메시지가 나오면 성공!

---

## STEP 3: GitHub에 새 저장소(Repository) 만들기 (3분)

1. **https://github.com** 로그인
2. 우측 상단 **+** 버튼 → **New repository** 클릭
3. 아래처럼 입력:
   - **Repository name**: `usim-promo-dashboard`
   - **Description**: `통신 3사 USIM 요금제 프로모션 비교 대시보드`
   - **Public** 선택 (무료로 GitHub Actions 무제한 사용 가능)
   - ⚠️ "Add a README file" 체크 **하지 마세요** (비워두세요)
4. **Create repository** 버튼 클릭
5. 나오는 페이지에서 HTTPS 주소를 복사해 두세요
   - 예: `https://github.com/내아이디/usim-promo-dashboard.git`

---

## STEP 4: 코드를 GitHub에 올리기 (5분)

1. 키보드에서 `Windows키 + R` → `cmd` 입력 → Enter
2. 아래 명령어를 **한 줄씩** 입력하고 Enter:

```
cd C:\Users\SKTelecom\Desktop\kiro
```

```
git init
```

```
git add .
```

```
git commit -m "initial: USIM promo dashboard"
```

```
git branch -M main
```

```
git remote add origin https://github.com/내아이디/usim-promo-dashboard.git
```
⚠️ 위에서 `내아이디` 부분을 본인 GitHub 아이디로 바꿔주세요!

```
git push -u origin main
```

4. GitHub 로그인 창이 뜨면 → 아이디/비밀번호 입력 (또는 브라우저 인증)
5. 완료! GitHub 페이지를 새로고침하면 파일들이 올라가 있습니다.

---

## STEP 5: 크롤링 자동 실행 테스트 (3분)

1. GitHub에서 본인 repository 페이지 접속
   - `https://github.com/내아이디/usim-promo-dashboard`
2. 상단 탭에서 **Actions** 클릭
3. 왼쪽에 **Daily USIM Crawl** 이 보입니다 → 클릭
4. 우측에 **Run workflow** 버튼 클릭 → **Run workflow** 한번 더 클릭
5. 노란 동그라미가 돌다가 초록 체크(✅)로 바뀌면 성공!
   - 빨간 X가 뜨면: 클릭해서 로그 확인 (대부분 사이트 구조 변경 때문)

### 확인하기
- Actions 완료 후 repository 메인 페이지로 돌아가면
- `data/` 폴더 안에 `latest.csv`, `history/` 폴더가 생겨 있습니다
- 이게 크롤링된 데이터입니다!

---

## STEP 6: 대시보드 배포하기 (10분)

1. 브라우저에서 **https://share.streamlit.io/** 접속
2. **Continue with GitHub** 클릭 → GitHub 로그인
3. 처음이면 Streamlit에 GitHub 접근 권한 허용 (Authorize 클릭)
4. **New app** 버튼 클릭
5. 아래처럼 설정:
   - **Repository**: `내아이디/usim-promo-dashboard` 선택
   - **Branch**: `main`
   - **Main file path**: `dashboard-app/app.py` 입력
6. **Deploy!** 버튼 클릭
7. 1~2분 기다리면 대시보드가 열립니다! 🎉

### 대시보드 URL
- 배포 완료 후 주소가 생깁니다 (예: `https://usim-promo-dashboard.streamlit.app`)
- 이 URL을 팀원에게 공유하면 누구나 접속 가능합니다
- 로그인 필요 없음!

---

## STEP 7: 정상 동작 확인 (2분)

대시보드에 접속해서 확인:

1. **왼쪽 사이드바**: 수집 상태에 ✅ 표시가 있는지 확인
2. **비교 테이블 페이지**: 3사 요금제가 테이블로 표시되는지 확인
3. **트렌드 차트 페이지**: (2일 이상 데이터 쌓이면 차트 표시)

---

## ✅ 완료! 이후에는 자동으로 동작합니다

- **매일 오전 10시 (한국시간)**: GitHub Actions가 자동으로 크롤링 실행
- **크롤링 결과**: `data/` 폴더에 자동 저장 & 커밋
- **대시보드**: 자동으로 최신 데이터 반영 (앱 재시작 시)

---

## ❓ 자주 묻는 질문

### Q: 크롤링이 실패하면?
- GitHub > Actions 탭에서 실패한 작업 클릭 → 로그 확인
- 대부분 통신사 사이트 구조 변경이 원인
- 대시보드에는 마지막 성공 데이터가 계속 표시됩니다

### Q: 대시보드가 안 열려요
- Streamlit Cloud 무료 tier는 사용하지 않으면 앱이 "잠듭니다"
- URL 접속하면 30초 정도 기다리면 다시 깨어납니다

### Q: 비용이 발생하나요?
- **아니요!** 모든 서비스가 무료입니다
  - GitHub: Public repo 무료
  - GitHub Actions: Public repo 무제한
  - Streamlit Cloud: 무료

### Q: 크롤링 시간을 바꾸고 싶어요
- `.github/workflows/crawl.yml` 파일에서
- `cron: '0 1 * * *'` 부분을 수정
- 예: 오후 2시로 변경 → `cron: '0 5 * * *'` (UTC 05:00 = KST 14:00)

### Q: 수동으로 크롤링을 실행하고 싶어요
- GitHub > Actions > Daily USIM Crawl > Run workflow 클릭

---

## 🆘 문제가 생기면

1. GitHub Actions 로그 확인 (Actions 탭 > 실패한 작업 클릭)
2. Streamlit Cloud 로그 확인 (앱 관리 페이지 > Logs)
3. 이 채팅에서 에러 메시지를 붙여넣기 해주시면 도와드립니다!

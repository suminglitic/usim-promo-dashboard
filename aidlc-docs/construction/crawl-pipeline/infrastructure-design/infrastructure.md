# Infrastructure Design — crawl-pipeline (완전 무료)

## 아키텍처 변경: AWS → GitHub Actions + CSV

| 항목 | 이전 (AWS) | 변경 (무료) |
|------|-----------|-------------|
| 스케줄러 | EventBridge | GitHub Actions cron |
| 실행 환경 | Lambda (Docker) | GitHub Actions Runner |
| 데이터 저장 | S3 (Parquet) | GitHub Repo (CSV) |
| 쿼리 엔진 | Athena | Pandas (메모리 내) |
| 비용 | ~$0.16/월 | **$0/월** |

---

## 1. GitHub Actions Workflow

| 항목 | 설정 |
|------|------|
| **Workflow File** | `.github/workflows/crawl.yml` |
| **Schedule** | `cron: '0 1 * * *'` (UTC 01:00 = KST 10:00) |
| **Runner** | ubuntu-latest (무료) |
| **Timeout** | 10분 |

### Workflow 구성
```yaml
name: Daily USIM Crawl
on:
  schedule:
    - cron: '0 1 * * *'  # KST 10:00
  workflow_dispatch:  # 수동 실행 가능

jobs:
  crawl:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r crawl-pipeline/requirements.txt
      - name: Install Chrome
        uses: browser-actions/setup-chrome@v1
      - name: Run crawler
        run: python crawl-pipeline/main.py
      - name: Commit data
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/
          git diff --staged --quiet || git commit -m "data: daily crawl $(date +%Y-%m-%d)"
          git push
```

### GitHub Actions 무료 한도
- 월 2,000분 (Public repo: 무제한)
- 일 10분 사용 → 월 300분 → **한도 내 충분**
- Public repo로 설정하면 무제한

---

## 2. 데이터 저장: GitHub Repository

### 저장 구조
```
data/
├── latest.csv              # 최신 수집 데이터 (대시보드 빠른 로딩용)
├── history/
│   ├── 2026-05-29.csv      # 일별 스냅샷
│   ├── 2026-05-28.csv
│   ├── ...
│   └── (최근 90일분)
└── metadata.json           # 수집 상태 메타데이터
```

### CSV 스키마
```csv
carrier,plan_name,monthly_fee,perceived_price,total_benefit,monthly_benefit,benefit_duration,benefit_detail,collected_date
SKT,T플랜 에센셜,55000,45000,120000,10000,12,네이버페이 12만원,2026-05-29
KT,요고 61,61000,41000,240000,20000,12,카카오페이 24만원,2026-05-29
LG,너겟 69,69000,45000,288000,24000,12,네이버페이 등 28만8천원,2026-05-29
```

### metadata.json
```json
{
  "last_crawl": {
    "SKT": {"date": "2026-05-29", "success": true, "plan_count": 5},
    "KT": {"date": "2026-05-29", "success": true, "plan_count": 4},
    "LG": {"date": "2026-05-29", "success": true, "plan_count": 8}
  }
}
```

### 데이터 보존 정책
- 90일 초과 CSV 파일은 크롤링 시 자동 삭제 (Python 스크립트에서 처리)
- 90일 x ~30개 요금제 = ~2,700행 → 수십 KB, repo 크기 문제 없음

---

## 3. Selenium/Chrome 설정 (GitHub Actions)

GitHub Actions runner에는 Chrome이 기본 설치되어 있지 않으므로:

- **browser-actions/setup-chrome@v1** 액션으로 Chrome 설치
- **selenium** + **webdriver-manager** 로 ChromeDriver 자동 관리
- headless 모드로 실행

---

## 4. 비용 요약

| 서비스 | 비용 |
|--------|------|
| GitHub Actions | 무료 (Public repo 무제한 / Private 월 2,000분) |
| GitHub Repository | 무료 |
| Streamlit Community Cloud | 무료 |
| **합계** | **$0/월** |

---

## 5. 제한사항 및 대응

| 제한 | 영향 | 대응 |
|------|------|------|
| GitHub Actions cron 정확도 | ±5~15분 지연 가능 | 데이터 수집 목적상 문제 없음 |
| Private repo 월 2,000분 | 일 10분 x 30일 = 300분 | 충분 (또는 Public repo로 무제한) |
| Repo 크기 제한 (5GB 권장) | 90일 CSV = 수십 KB | 전혀 문제 없음 |
| Actions 동시성 | 무료 tier: 20 동시 작업 | 1개 작업만 사용, 문제 없음 |

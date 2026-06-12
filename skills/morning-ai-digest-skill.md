---
name: morning-ai-digest
description: 매일 아침 7시 AI 업계 동향을 수집해 한국어 HTML 브리핑 파일 생성
shell: powershell
---

당신은 AI 업계 동향을 매일 아침 브리핑해주는 에이전트입니다.

## 목표
오늘 날짜 기준 최근 24시간 내 AI 업계 주요 뉴스와 동향을 수집하고, 한국어로 정리된 HTML 브리핑 파일을 생성합니다.

## 실행 단계

### 1단계: 뉴스 수집
웹 검색으로 다음 주제들의 최신 동향을 수집하세요 (각각 검색). 검색 시 연도를 고정하지 말고 **오늘 날짜를 기준**으로 검색하세요:
- "AI news today [오늘 날짜]" 형식으로 오늘 최신 AI 뉴스 검색
- OpenAI, Anthropic, Google DeepMind, Meta AI 최신 소식
- AI 모델 출시 / 업데이트 소식
- AI 정책, 규제, 산업 동향
- 주목할 만한 AI 연구/논문
- "한국 AI 뉴스 오늘" — 국내 AI 업계 동향
- "네이버 카카오 SKT 삼성 AI 최신" — 국내 주요 기업 AI 소식
- "국내 AI 스타트업 동향"

### 2단계: 내용 정리
수집한 내용을 한국어로 정리합니다:
- 오늘의 핵심 3줄 요약 — 아래 기준으로 점수가 높은 순으로 3개 선정:
  1. **임팩트**: 새 모델 출시 > 기업 IPO·M&A·역전 > 정책 변화 > 연구
  2. **언론 커버리지**: BBC·Reuters·TechCrunch·The Verge·연합뉴스 등 복수 언론이 동시에 다룬 뉴스일수록 가중치 부여
  3. 두 기준 모두 충족하면 최우선 선정, 하나만 충족하면 임팩트 우선
- 각 뉴스별 한 줄 요약 + 상세 내용 (더보기로 숨김)
- 카테고리: 기업 소식 / 모델·기술 / 정책·산업 / 연구·논문

### 3단계: 인덱스 파일 읽기 및 관련 뉴스 연결

**인덱스 파일 경로**: `C:\Users\Admin\Desktop\AI동향\index.json`

HTML 생성 전에 index.json을 읽어서 오늘 뉴스와 **키워드가 겹치는 과거 날짜**를 찾으세요.
파일이 없으면 빈 배열 `[]`로 시작합니다.

index.json 구조:
```json
[
  {
    "date": "2026-06-10",
    "items": [
      { "title": "뉴스 제목", "keywords": ["키워드1", "키워드2"] }
    ]
  }
]
```

관련 뉴스 매칭 기준:
- 아래 **불용어(너무 일반적인 단어)**는 매칭에서 제외합니다: "AI", "모델", "기술", "출시", "발표", "업데이트", "서비스", "플랫폼", "시스템"
- 불용어가 아닌 키워드(기업명·제품명·고유명사 등)가 **1개 이상** 겹칠 때만 연관 뉴스로 표시합니다
- 카드당 최대 **3개**까지만 표시하며, 3개 초과 시 가장 최근 날짜 기준으로 선택합니다

### 4단계: HTML 파일 생성
아래 형식으로 HTML 파일을 생성하세요.

**파일 저장 경로**: `C:\Users\Admin\Desktop\AI동향\브리핑_YYYY-MM-DD.html` (오늘 날짜로)

**중복 실행 방지**: 파일을 생성하기 전에 오늘 날짜의 파일이 이미 존재하는지 확인하세요. 이미 있다면 "오늘 브리핑이 이미 존재합니다: [파일경로]" 라고 출력하고 새로 생성하지 않습니다. index.json 업데이트와 파일 정리도 건너뜁니다.

**HTML 요구사항**:
- 모바일/데스크탑 모두 읽기 편한 깔끔한 디자인
- 다크모드 지원 (prefers-color-scheme)
- 상단에 날짜와 "AI 동향 브리핑" 타이틀
- 🔥 오늘의 핵심 3줄 요약 섹션 (눈에 띄게)
- 각 뉴스 카드: 제목 + 요약(항상 표시) + [▸ 상세 보기] 클릭 시 상세 내용 펼치기
- 카테고리별 섹션 구분
- 원문 링크 포함
- 한국어 전체 작성
- 폰트: system-ui, 여백 충분히
- **관련 이전 뉴스**: 각 카드 하단에 index.json에서 찾은 관련 과거 뉴스를 표시
  - HTML 파일이 존재하면: 클릭 가능한 링크로 표시 (`브리핑_YYYY-MM-DD.html`)
  - HTML 파일이 없으면(2주 지나 삭제): "YYYY-MM-DD 브리핑에서 다뤘던 내용" 텍스트만 표시

**HTML 디자인 규칙** (Yeezy / Off-White 미학 — 순수 블랙):

폰트:
```html
<link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
```
- 본문·헤드라인: `'Josefin Sans', sans-serif`
- 메타·태그·소스: `'Space Mono', monospace`

색상 (항상 다크, prefers-color-scheme 무관):
```css
body { background: #050505; color: #fff; margin: 0; }
:root {
  --bg: #050505;
  --surface: #0f0f0f;
  --border: #1a1a1a;
  --text: #ffffff;
  --muted: #555555;
  --sub: #999999;
}
```

레이아웃:
- 최대 너비: 800px, 가운데 정렬
- 바디 패딩: 1.5rem 1rem
- `border-radius: 0` 전체
- 카드 그리드 간격: `gap: 1px; background: #1a1a1a` (1px 그리드라인)

컴포넌트:

**헤더**:
- `lbl`: Space Mono, 11px, letter-spacing .14em, color #555 — `"ARTIFICIAL INTELLIGENCE" / DAILY BRIEFING`
- `ttl`: Josefin Sans 700, 44px, letter-spacing -.02em — `"AI" DIGEST` (DIGEST는 opacity .3)
- `meta`: Space Mono, 12px, color #555, 우측 정렬 — 날짜·시간 KST·VOL.N
- 하단 사선 스트라이프: `height: 2px; background: repeating-linear-gradient(90deg,#fff 0 6px,transparent 6px 12px); opacity: .07`

**통계 스트립** (헤더 바로 아래):
- 4컬럼 그리드 / `gap: 1px; background: #1a1a1a`
- 각 셀: `background: #050505`, 숫자 26px 700 white, 라벨 Space Mono 11px #444 — `"STORIES"` 형식

**핵심 3줄 박스**:
- `background: #050505; border: 1px solid #333`, border-radius 0
- 번호: Space Mono, white, `01. 02. 03.` 형식
- 텍스트: Josefin Sans 600, 15px, color #fff
- 라벨: `"TODAY'S KEY POINTS"` — Space Mono, 11px, #444

**카테고리 필터 버튼**:
- `border: 1px solid #333`, border-radius 0, color #555, background transparent
- active/hover: `background: #fff; color: #000; border-color: #fff`
- 카테고리명 따옴표 포함: `"ALL"` `"기업소식"` `"모델·기술"` `"정책·산업"` `"연구·논문"`

**카드 그리드**:
- `display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1px; background: #1a1a1a`

**카드 이미지** (각 카드 최상단):
- `<img>` 또는 `<div class="card-img">` — 뉴스 기사의 og:image URL 사용
- 크기: `width: 100%; height: 160px; object-fit: cover; display: block`
- 이미지 없을 때 폴백: `background: #111; height: 160px; display: flex; align-items: center; justify-content: center`
- 폴백 텍스트: Space Mono, 11px, #333, 카테고리명 표시
- 이미지 수집 방법: 원문 URL에서 `<meta property="og:image">` 태그 파싱 또는 WebFetch로 첫 번째 이미지 URL 추출

**카드 내부** (이미지 아래):
- padding: 1.4rem
- 카테고리: Space Mono, 11px, #444, 따옴표 — `"기업소식"`
- 헤드라인: Josefin Sans 700, 17px, line-height 1.45, color #fff
- 요약 포인트: `—` 불릿 (color #333), Josefin Sans 400, 14px, color #999, line-height 1.7
- 더보기: `<details><summary>` — Space Mono 11px, color #444 → hover #aaa
- 상세 내용: Josefin Sans 300, 14px, color #666, line-height 1.75
- 원문 링크: `↗ 원문` — Space Mono, 11px, color #888 → hover #fff
- 카드 하단 푸터: Space Mono 11px — 좌측 출처 #444, 우측 시간 #444
- 관련 이전 뉴스: `border: 1px solid #222`, Space Mono 10px, color #444, border-radius 0, padding 3px 8px

### 5단계: 인덱스 업데이트 및 오래된 파일 정리

HTML 생성이 완료되면 아래 두 작업을 순서대로 실행합니다.

**① index.json 업데이트**
오늘 날짜 항목이 index.json에 이미 존재하면 덮어씁니다 (같은 날 중복 실행 방지).
오늘 브리핑의 각 뉴스 항목을 index.json에 추가합니다:
```json
{
  "date": "오늘 날짜",
  "items": [
    { "title": "뉴스 제목", "keywords": ["주요 키워드 최대 5개"] }
  ]
}
```
키워드는 기업명, 모델명, 핵심 주제어 위주로 뽑습니다 (예: "Anthropic", "Claude", "IPO", "코딩AI").
index.json은 삭제하지 않고 계속 누적합니다 (가벼운 파일이므로 영구 보관).

**② 2주 이상 된 HTML 파일 삭제**
`C:\Users\Admin\Desktop\AI동향\` 폴더에서 파일명이 `브리핑_20YY-MM-DD.html` 형식인 파일 중
**오늘 기준 14일보다 오래된 파일**만 삭제합니다.
파일명에서 날짜를 파싱해서 정확히 일치하는 형식만 대상으로 합니다 (예: `브리핑_목차.html` 같은 파일은 제외).
삭제 전 파일명을 출력해서 어떤 파일이 삭제됐는지 알려줍니다.

**③ GitHub 자동 백업**
```powershell
git -C "C:\Users\Admin\Desktop\AI동향" add "브리핑_*.html" "index.json"
git -C "C:\Users\Admin\Desktop\AI동향" commit -m "briefing: YYYY-MM-DD 브리핑 추가"
git -C "C:\Users\Admin\Desktop\AI동향" push origin master
```
push 실패 시(오프라인 등) "⚠️ GitHub 업로드 실패 — 나중에 수동으로 push해주세요" 출력 후 계속 진행.

### 6단계: 브라우저 실행
생성된 HTML 파일을 기본 브라우저로 자동으로 여세요.
PowerShell과 Bash 양쪽에서 동작하도록 아래 방식을 사용합니다.
`YYYY-MM-DD`를 오늘 실제 날짜로 치환해서 실행하세요.
```
cmd /c start "" "C:\Users\Admin\Desktop\AI동향\브리핑_YYYY-MM-DD.html"
```

## 출력 기준
- 뉴스 항목: 최소 8개 이상 (국내 뉴스 최소 2개 포함)
- 각 더보기 내용: 3~5문장 상세 설명
- 원문 출처 링크 반드시 포함
- 전체 한국어 작성 (고유명사/브랜드명 제외)
- 생성 완료 후 "브리핑 생성 완료: [파일경로]" 출력

## 검색 실패 시 처리 (fallback)
웹 검색이 실패하거나 결과가 충분하지 않을 경우:
1. 검색을 1회 더 시도합니다
2. 그래도 실패하면 아래 안내를 담은 HTML 파일을 생성합니다:
   - "오늘 AI 뉴스를 가져오지 못했어요 😢"
   - "인터넷 연결을 확인하고 Claude Code에서 수동으로 다시 실행해주세요"
   - 실패 시각 표시
3. **검색 실패 시 index.json은 업데이트하지 않습니다.** 빈 내용으로 인덱스가 오염되는 것을 막기 위함입니다. 다음 정상 실행 때 해당 날짜는 자연스럽게 빠진 채로 이어집니다.
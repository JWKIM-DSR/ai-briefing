---
name: audit-to-issue
shell: powershell
description: |
  현재 작업 내용(코드, 설정 파일, 스케줄드 태스크, HTML 등)을 분석해서 버그·개선점·이슈를 찾아내고 GitHub 이슈로 자동 등록하는 스킬.
  사용자가 "이슈 등록", "버그 확인해서 올려줘", "개선점 이슈로 등록", "현재 작업 이슈 등록 ㄱㄱ", "깃헙에 이슈 올려줘", "문제점 찾아서 이슈 등록", "이슈 뽑아줘", "re-issue", "이슈 다시 뽑아줘", "audit", "analyze-and-file-issues", "analyze and file" 같은 말을 하면 반드시 이 스킬을 사용해야 한다.
  gh CLI를 사용해서 bug / enhancement 라벨로 구분해 이슈를 등록하며, gh CLI가 없으면 설치 안내를 먼저 제공한다.
  이슈 등록 후 초보자도 이해할 수 있는 설명 댓글을 자동으로 추가한다.
---

## 목표

지정된 파일 또는 현재 세션 작업 전반을 검토해 **버그(bug)**와 **개선점(enhancement)**을 도출하고, GitHub 이슈로 자동 등록한 뒤 초보자용 설명 댓글을 단다.

---

## 분석 범위 결정

사용자가 특정 파일을 지정한 경우 (예: "SKILL.md re-issue", "이 파일 이슈 뽑아줘"):
- 해당 파일만 집중 분석

파일 지정 없이 일반적으로 요청한 경우:
- 현재 세션에서 생성·수정한 파일 전체
- 실행 중 발생한 에러·경고 메시지
- 사용자가 직접 언급한 불편함

---

## 실행 단계

### 1단계: 사전 확인

```powershell
# PATH 갱신 (gh CLI를 찾지 못하는 문제 방지)
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
```

순서대로 확인:
1. `gh auth status` — 로그인 안 된 경우 `gh auth login` 안내 후 중단
2. gh CLI 없는 경우 `winget install GitHub.cli` 안내 후 중단
3. `git remote get-url origin`으로 레포 URL 확인 후 OWNER/REPO 추출:
   ```powershell
   $remoteUrl = git remote get-url origin
   # HTTPS: https://github.com/OWNER/REPO.git
   # SSH:   git@github.com:OWNER/REPO.git
   $repo = $remoteUrl -replace '^.*github\.com[:/](.+?)(?:\.git)?$', '$1'
   # 결과 예시: JWKIM-DSR/ai-briefing
   ```
   레포 없으면 사용자에게 URL 직접 입력 요청
4. `gh issue list --repo $repo --state all --limit 200` — open + closed 이슈 모두 확인 (중복 방지)
   - 제목이 유사한 closed 이슈가 있으면 "(이미 해결된 이슈 #번호와 유사)" 라고 표시 후 계속 진행

### 2단계: 이슈 도출

아래 기준으로 이슈를 발굴한다:

**버그 (bug 라벨)**
- 실제로 재현된 에러 (명령어 실패, 파일 생성 실패 등)
- 잘못된 값 하드코딩 (연도, 경로, 사용자명 등 변경될 수 있는 값)
- 플랫폼 / 환경 불일치 (PowerShell vs Bash, OS 차이 등)
- 예외 처리 없이 실패할 수 있는 지점
- 실행 순서 오류 (앞 단계 결과에 의존하는데 체크 없음)

**개선점 (enhancement 라벨)**
- 중복 실행 / 동시성 문제 처리 부재
- 에러 발생 시 fallback 또는 사용자 안내 없음
- 리소스 무한 누적 (로그, 파일, 캐시 정리 없음)
- 특정 지역·언어·환경 편향
- 매칭·필터 기준이 너무 넓거나 좁음
- 사용자 편의를 높이는 기능 (가이드, 자동화, 알림 등)

각 이슈 구성:
- **제목**: `[Bug]` 또는 `[Enhancement]` 접두사 + 한 줄 요약
- **본문**: 현상 / 원인 / 수정 방향 (3섹션) + 우선순위

우선순위 기준:
- 🔴 높음 — 현재 동작이 깨지거나 데이터 손실 가능
- 🟡 중간 — 지금 당장은 아니지만 곧 문제가 될 수 있음
- 🟢 낮음 — 있으면 좋지만 급하지 않음

### 3단계: 이슈 등록

이슈 본문은 반드시 **Write 도구로 임시 파일에 저장** 후 `--body-file`로 등록한다.
`--body`에 직접 긴 텍스트를 넣으면 대괄호·특수문자·줄바꿈에서 파싱 오류가 발생한다.

```powershell
# 임시 파일 경로 — 타임스탬프로 고유화 (동시 실행 시 충돌 방지)
$ts = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$tmpFile     = "$env:TEMP\gh_issue_${ts}_N.txt"   # N을 이슈 순번으로 교체
$commentFile = "$env:TEMP\gh_comment_${ts}_N.txt"
```

등록 순서: 버그 먼저, 개선점 나중에 (심각도 높은 것부터).

등록 실패 시 처리:
- 개별 이슈 등록 실패해도 전체를 멈추지 않고 다음 이슈 계속 진행
- 실패한 이슈는 별도로 기록해두고, 5단계 결과 보고에서 "등록 실패" 목록으로 표시

### 4단계: 초보자용 설명 댓글 자동 추가

이슈 등록이 성공한 경우(gh 명령어가 URL을 반환한 경우)에만 해당 이슈에 댓글을 단다.
등록 실패한 이슈는 건너뛴다.

```powershell
$url = gh issue create --repo $repo --title $title --label $label --body-file $tmpFile
if ($url) { gh issue comment ($url -split '/')[-1] --repo $repo --body-file $commentFile }
```

각 이슈 등록 직후 `gh issue comment`로 댓글을 단다.
댓글은 개발을 처음 접하는 사람도 이해할 수 있게 작성한다:

```markdown
## 🙋 이게 무슨 문제인가요?
[일상 언어로 쉽게 설명 — 비유 활용 환영]

## ✅ 어떻게 고치면 되나요?
[구체적인 수정 방향, 코드 예시 포함]

## 📌 우선순위
🔴/🟡/🟢 [높음/중간/낮음] — [한 줄 이유]
```

댓글도 이슈 본문과 마찬가지로 Write 도구로 파일 저장 후 `--body-file` 사용.

### 5단계: 결과 보고

등록 완료 후 표 형태로 요약 출력:

```
| #  | 제목                     | 종류           | 우선순위 | 링크                                           |
|----|--------------------------|----------------|----------|------------------------------------------------|
| 8  | index.json 중복 항목     | 🐛 Bug         | 🔴 높음  | [#8](https://github.com/OWNER/REPO/issues/8)  |
| 9  | 날짜 플레이스홀더 미치환 | 🐛 Bug         | 🟡 중간  | [#9](https://github.com/OWNER/REPO/issues/9)  |
| 11 | 키워드 과매칭 위험        | ✨ Enhancement | 🟡 중간  | [#11](https://github.com/OWNER/REPO/issues/11)|
```

링크 열의 URL은 `gh issue create` 가 반환한 실제 URL을 그대로 사용한다 (`$url` 변수).
`#번호` 텍스트만 쓰면 클릭할 수 없으므로 반드시 `[#N](URL)` 마크다운 링크로 작성한다.

버그가 있으면 "지금 바로 수정할까요?" 라고 물어본다.

결과 보고 후 임시 파일 정리:
```powershell
Remove-Item "$env:TEMP\gh_issue_*.txt" -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\gh_comment_*.txt" -ErrorAction SilentlyContinue
```

---

## 이슈 품질 기준

- 제목은 `[Bug]` 또는 `[Enhancement]`로 시작
- 본문은 **현상 / 원인 / 수정 방향** 3섹션 + 우선순위 필수
- 모호한 이슈 (예: "코드가 복잡함") 는 등록하지 않는다
- 이미 등록된 이슈와 중복되면 건너뛴다
- 이슈는 최소 2개 이상, 최대 10개 이내로 압축

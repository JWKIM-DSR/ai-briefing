---
name: issues-plan-and-resolve
shell: powershell
description: |
  GitHub 이슈 번호를 지정하면 해당 이슈를 읽고, 수정 계획을 수립하여 사용자 승인 후 코드를 직접 수정하고 이슈를 close하는 스킬.
  사용자가 "이슈 #N 해결해줘", "resolve #N", "이슈 수정해줘 #N", "#N 고쳐줘", "이슈 처리해줘" 같은 말을 하면 반드시 이 스킬을 사용해야 한다.
  여러 이슈를 동시에 지정할 수 있으며 (예: "#12 #15 해결해줘"), 각 이슈를 순서대로 처리한다.
---

## 목표

지정된 GitHub 이슈를 읽고, 관련 코드를 파악하여 **수정 계획을 사용자에게 보여준 뒤 승인을 받아** 실제 코드를 수정하고 이슈를 close한다.

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
   $repo = $remoteUrl -replace '^.*github\.com[:/](.+?)(?:\.git)?$', '$1'
   ```
4. 사용자가 지정한 이슈 번호 목록 파악 (없으면 번호 입력 요청)

### 2단계: 이슈 내용 읽기

각 이슈 번호에 대해:
```powershell
$issueContent = gh issue view $issueNumber --repo $repo 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Output "❌ #$issueNumber 이슈를 찾을 수 없습니다 — 건너뜀"
    continue
}
```

- 제목, 본문(현상/원인/수정 방향), 기존 댓글 모두 읽기
- 이슈가 이미 closed 상태면 "이미 해결된 이슈입니다 (#N)" 표시 후 건너뜀
- 유효한 이슈가 하나도 없으면 "처리할 이슈 없음" 출력 후 전체 중단
- 관련 파일 경로가 본문에 언급된 경우 해당 파일 확인
- 파일 경로가 언급되지 않은 경우: ① 이슈 제목 키워드로 Grep 검색 → ② 스킬명이 제목에 있으면 `skills/` 하위 우선 확인 → ③ 그래도 불분명하면 사용자에게 파일 경로 질문

### 3단계: 수정 계획 수립 및 승인

각 이슈에 대해 아래 형식으로 수정 계획을 출력한다:

```
## 이슈 #N: [제목]

**문제**: [한 줄 요약]
**수정할 파일**: [파일 경로]
**수정 내용**:
  1. [구체적인 변경 사항 1]
  2. [구체적인 변경 사항 2]
**예상 효과**: [수정 후 어떻게 달라지는지]
```

여러 이슈인 경우 모두 보여준 뒤 한 번에 승인 요청:
> "위 계획대로 수정을 진행할까요? (수정하고 싶은 부분이 있으면 말씀해 주세요)"

**사용자가 승인하기 전까지 절대 코드를 수정하지 않는다.**

### 4단계: 코드 수정

승인 후 수정 계획에 따라 파일을 수정한다.

- 수정 범위는 이슈에서 지적한 부분만으로 제한
- 관련 없는 코드는 건드리지 않음
- 수정 완료 후 변경된 파일 목록을 간략히 출력

### 5단계: 해결 댓글 추가 및 이슈 close

각 이슈에 대해 댓글 파일 작성 후 등록, 그 다음 close:

```powershell
$ts = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$commentFile = "$env:TEMP\gh_resolve_comment_${ts}_${issueNumber}.txt"
```

댓글 형식:
```markdown
## ✅ 해결 완료

**수정 내용**
[실제로 변경한 내용 요약]

**수정된 파일**
- `파일경로` — [어떤 부분을 어떻게 바꿨는지]

**확인 방법**
[수정이 잘 됐는지 확인하는 방법 — 초보자도 이해할 수 있게]
```

```powershell
gh issue comment $issueNumber --repo $repo --body-file $commentFile
if ($LASTEXITCODE -ne 0) {
    Write-Output "⚠️ #$issueNumber 댓글 등록 실패 — close는 진행, 결과표에 표시"
    $commentFailed = $true
} else {
    $commentFailed = $false
}
gh issue close $issueNumber --repo $repo
```

댓글 실패 시 close는 계속 진행하되, 6단계 결과표에 `⚠️ 댓글 등록 실패` 표시.

### 6단계: 결과 보고

```
| #  | 제목                  | 상태                    | 링크                                           |
|----|------------------------|-------------------------|------------------------------------------------|
| 12 | index.json 중복 항목  | ✅ 해결됨               | [#12](https://github.com/OWNER/REPO/issues/12)|
| 15 | 날짜 하드코딩 문제    | ⚠️ 댓글 등록 실패·close됨 | [#15](https://github.com/OWNER/REPO/issues/15)|
```

링크는 `gh issue view` 또는 `gh issue close`가 반환한 실제 URL 사용.

결과 보고 후 임시 파일 정리:
```powershell
Remove-Item "$env:TEMP\gh_resolve_comment_*.txt" -ErrorAction SilentlyContinue
```

---

## 주의 사항

- **승인 게이트 필수**: 3단계에서 사용자 OK 없이 코드 수정 절대 금지
- **범위 제한**: 이슈와 무관한 코드 개선·리팩터링은 하지 않음
- **실패 처리**: 개별 이슈 처리 실패해도 다음 이슈 계속 진행, 실패 목록 결과 보고에 표시
- **댓글 → close 순서**: 반드시 댓글 먼저, close 나중

---
name: briefingimprover
shell: powershell
description: |
  audit-to-issue → issues-plan-and-resolve → optimize-docs 세 스킬을 순서대로 실행하는 풀 사이클 개선 스킬.
  사용자가 "전체 개선", "풀 사이클", "briefing improve", "한 번에 다 돌려줘", "이슈 등록하고 고치고 문서까지 정리해줘" 같은 말을 하면 반드시 이 스킬을 사용해야 한다.
---

## 목표

코드·문서의 문제를 발견하고, 고치고, 정리하는 전 과정을 한 번에 완료한다.

---

## 실행 순서

```
[1단계] audit-to-issue
    ↓ 등록된 이슈 번호 목록 전달
[2단계] issues-plan-and-resolve
    ↓ 해결 완료 확인
[3단계] optimize-docs
```

각 단계 사이에 이전 단계가 완전히 끝났는지 확인 후 다음으로 넘어간다.

---

## 1단계: audit-to-issue 실행

`audit-to-issue` 스킬을 그대로 따른다.

완료 기준:
- 이슈가 GitHub에 등록되고 댓글까지 달림
- 결과 표가 출력됨 (등록된 이슈 번호 목록 확보)

1단계 완료 후 이슈 번호를 임시 파일에 저장 (2단계 전달용):
```powershell
$issueNumbers -join "," | Out-File "$env:TEMP\briefing_issue_ids.txt" -Encoding utf8
```

등록된 이슈가 0개면 "발견된 이슈 없음 — 2단계 건너뜀" 출력 후 3단계로 이동.

---

## 2단계: issues-plan-and-resolve 실행

시작 시 1단계에서 저장한 이슈 번호 복원:
```powershell
$issueNumbers = (Get-Content "$env:TEMP\briefing_issue_ids.txt" -ErrorAction SilentlyContinue) -split ","
```

복원된 **모든 이슈 번호**를 대상으로 `issues-plan-and-resolve` 스킬을 실행한다.

- 수정 계획은 이슈별로 각각 보여주지 않고 **전체를 한 번에 보여준 뒤 일괄 승인** 받는다
- 승인 후 이슈 순서대로 처리 (버그 먼저, 개선점 나중)

완료 기준:
- 모든 이슈가 close됨 (또는 실패 목록 정리됨)

2단계 완료 후 코드 수정 내용을 커밋:
```powershell
git add <수정된 파일 목록>
git commit -m "fix: resolve issues $(($issueNumbers | ForEach-Object { '#' + $_ }) -join ', ')

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 3단계: optimize-docs 실행

`optimize-docs` 스킬을 그대로 따른다.

- 2단계에서 수정된 파일도 포함해 전체 문서 검토
- git commit까지 완료

---

## 최종 보고

세 단계 결과를 한 번에 요약한다:

```
## 브리핑 개선 완료

### 1단계: 이슈 등록 (audit-to-issue)
| # | 제목 | 종류 | 링크 |
|---|------|------|------|
| ... | ... | ... | ... |

### 2단계: 이슈 해결 (issues-plan-and-resolve)
| # | 제목 | 상태 | 링크 |
|---|------|------|------|
| ... | ... | ... | ... |

### 3단계: 문서 최적화 (optimize-docs)
[optimize-docs 완료 보고 그대로]
```

---

## 사전 점검 (실행 전 자동 수행)

아래 두 파일 내용이 일치하는지 확인한다:
- `C:\Users\Admin\Desktop\AI동향\skills\morning-ai-digest-skill.md`
- `C:\Users\Admin\.claude\scheduled-tasks\morning-ai-digest\SKILL.md`

불일치 발견 시 아래 메시지를 출력하고 자동 복사 없이 종료한다 (자동 복사는 Claude Code 권한 차단됨):

```
⚠️ 스킬 파일 불일치 감지 — 아래 명령어를 터미널에서 직접 실행해 동기화하세요:
Copy-Item 'C:\Users\Admin\Desktop\AI동향\skills\morning-ai-digest-skill.md' 'C:\Users\Admin\.claude\scheduled-tasks\morning-ai-digest\SKILL.md' -Force
```

---

## 알려진 오류 패턴

| 증상 | 원인 | 조치 |
|------|------|------|
| 오늘 브리핑이 오전 7시에 발행 안 됨 | 스케줄 cron이 UTC 기준으로 저장돼 한국 시간과 불일치 | `mcp__scheduled-tasks__update_scheduled_task`로 cronExpression 재설정 (로컬 시간 기준 `0 7 * * *`) |
| 스킬 수정 후 스케줄드 태스크에 미반영 | `skills/`와 `scheduled-tasks/` 이중 관리 구조 | 사전 점검 단계에서 자동 동기화됨 |

---

## 중단 조건

- 1단계 `gh auth` 실패 → 전체 중단
- 2단계 사용자가 승인 거부 → 2단계만 건너뛰고 3단계 진행
- 3단계 실패 → 1·2단계 결과는 유지, 실패 사유 출력

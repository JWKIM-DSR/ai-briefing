# CLAUDE.md

Claude Code 운영 지침. 철학은 SOUL.md, 사람용 안내는 README.md.

---

## 환경

- OS: Windows 11 / Shell: PowerShell (Bash 보조)
- 작업 디렉터리: `C:\Users\Admin\Desktop\AI동향\`

## 경로

| 용도 | 경로 |
|------|------|
| 브리핑 출력 | `C:\Users\Admin\Desktop\AI동향\브리핑_YYYY-MM-DD.html` |
| 뉴스 인덱스 | `C:\Users\Admin\Desktop\AI동향\index.json` |
| 스킬 | `C:\Users\Admin\Desktop\AI동향\skills\` |

## 스킬

| 스킬 | 파일 | 하는 일 |
|------|------|---------|
| `morning-ai-digest` | `skills/morning-ai-digest-skill.md` | AI 뉴스 수집 → HTML 생성 → 인덱스 업데이트 → 브라우저 실행 |
| `audit-to-issue` | `skills/audit-to-issue/SKILL.md` | 버그·개선점 분석 → GitHub 이슈 등록 + 댓글 |
| `issues-plan-and-resolve` | `skills/issues-plan-and-resolve/SKILL.md` | 이슈 번호 지정 → 수정 계획 승인 → 코드 수정 → close |
| `optimize-docs` | `skills/optimize-docs/SKILL.md` | 문서 중복 제거 → 하드코딩 점검 → git commit |
| `briefingimprover` | `skills/briefingimprover.md` | audit-to-issue → issues-plan-and-resolve → optimize-docs 풀 사이클 |

## 에이전트 팀 하네스

활성화 조건: `~/.claude/settings.json`에 `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` 설정 필요.

### 구조

```
briefing-lead (오케스트레이터)
├── news-scout       뉴스 수집
├── html-publisher   HTML 브리핑 생성 + index.json 업데이트
├── code-auditor     버그·이슈 발굴 (분석만)
├── issue-manager    GitHub 이슈 등록·해결·close
└── doc-optimizer    문서 중복 제거·git commit
```

에이전트 파일 위치: `.claude/agents/`

### 요청 → 워크플로 매핑

| 요청 | 실행 순서 |
|------|-----------|
| 브리핑 만들어줘 | news-scout → html-publisher |
| 이슈 등록해줘 | code-auditor → issue-manager(등록) |
| 이슈 #N 해결해줘 | issue-manager(해결) |
| 문서 최적화 | doc-optimizer |
| 풀 사이클 / 전체 개선 | code-auditor → issue-manager(등록) → issue-manager(해결) → doc-optimizer |

### 에이전트별 허용 툴

| 에이전트 | 툴 | effort |
|----------|----|--------|
| `briefing-lead` | 전체 | xhigh |
| `news-scout` | WebSearch, WebFetch, Read | high |
| `html-publisher` | Read, Write, Edit | high |
| `code-auditor` | Read, Grep, Glob | medium |
| `issue-manager` | Bash, Read, Write | medium |
| `doc-optimizer` | Read, Edit, Grep, Glob, Bash | low |

---

## 규칙

1. **한국어**: 출력·파일명·이슈 본문 모두 한국어 (고유명사 제외)
2. **중복 금지**: 오늘 날짜 브리핑 파일이 이미 있으면 생성하지 않는다
3. **index.json 영구 보관**: HTML은 2주 후 삭제, index.json은 삭제하지 않는다

## Claude Code 메모

- `skills/` 자동 로드됨
- 스킬 frontmatter 사용 가능 필드:
  `name`, `description`, `disallowed-tools`, `allowed-tools`,
  `effort`(low/medium/high/xhigh/max), `context`(fork), `paths`(글롭 패턴),
  `shell`(bash/powershell), `model`, `argument-hint`
  — `experimental`은 폐지됨 (무시됨)
- 훅 이벤트:
  - `PostToolUse` — 도구 실행 후 (`updatedToolOutput`으로 결과 수정 가능)
  - `Stop` — 응답 완료 시 차단/피드백 (`decision: block`, `additionalContext`)
  - `SubagentStop` — 자식 에이전트 완료 시 (`agent_id`, `agent_type` 필드 포함)
- `.claude/rules/*.md` — `paths` frontmatter로 경로별 조건부 규칙 지정 가능

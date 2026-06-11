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
| `analyze-and-file-issues` | `skills/analyze-and-file-issues/SKILL.md` | 버그·개선점 분석 → GitHub 이슈 등록 |
| `optimize-docs` | `skills/optimize-docs/SKILL.md` | 문서 중복 제거 → 하드코딩 점검 → git commit |

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

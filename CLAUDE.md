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
4. **이슈 파일**: `gh issue create`는 반드시 `--body-file $env:TEMP\gh_issue_N.txt` 사용
5. **이슈 실패**: 개별 등록 실패해도 나머지 계속 진행
6. **PATH 갱신**: gh CLI 실행 전 `$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")`

## Claude Code 메모 (2026-06-11)

- `skills/` 자동 로드됨
- 스킬 frontmatter: `disallowed-tools`, `experimental` 사용 가능
- 훅: `PostToolUse`, `Stop`, `SubagentStop` 사용 가능

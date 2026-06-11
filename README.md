# AI 동향 브리핑

매일 아침 7시, AI 업계 동향을 자동 수집해 한국어 HTML 브리핑으로 제공하는 Claude Code 프로젝트.
레포: [JWKIM-DSR/ai-briefing](https://github.com/JWKIM-DSR/ai-briefing)

---

## 기능

- 최근 24시간 AI 뉴스를 국내외 수집해 카테고리별 정리
- 다크모드 지원 HTML 파일 생성 후 브라우저 자동 실행
- 이전 브리핑과 관련 뉴스 자동 연결
- 2주 지난 브리핑 파일 자동 삭제

## 사전 준비

- [Claude Code 데스크탑 앱](https://claude.ai/code)
- [GitHub CLI](https://cli.github.com/) + `gh auth login`
- 인터넷 연결 (웹 검색 권한)

## 파일 구조

```
AI동향/
├── CLAUDE.md
├── README.md
├── SOUL.md
├── index.json
├── 브리핑_YYYY-MM-DD.html
└── skills/
    ├── morning-ai-digest-skill.md
    └── analyze-and-file-issues/SKILL.md
```

## 사용법

| 작업 | 방법 |
|------|------|
| 브리핑 수동 실행 | "브리핑 만들어줘" |
| 자동 스케줄 | 데스크탑 앱 스케줄드 태스크로 매일 7시 실행 |
| 이슈 등록 | "이슈 등록해줘" 또는 "re-issue" |

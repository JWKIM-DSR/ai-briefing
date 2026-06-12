# 🤖 AI 동향 브리핑

> 매일 아침 7시, AI 업계 소식을 자동 수집해 한국어 HTML 브리핑으로 전달하는 Claude Code 프로젝트

[![repo](https://img.shields.io/badge/GitHub-JWKIM--DSR%2Fai--briefing-6366f1?style=flat-square&logo=github)](https://github.com/JWKIM-DSR/ai-briefing)
[![platform](https://img.shields.io/badge/Claude_Code-Desktop-818cf8?style=flat-square)](https://claude.ai/code)

---

## 무엇을 하나요?

| 기능 | 설명 |
|------|------|
| 📰 뉴스 수집 | 국내외 AI 기업·모델·정책·연구 뉴스 자동 수집 |
| 🗂️ 카테고리 정리 | 기업 소식 / 모델·기술 / 정책·산업 / 연구·논문 |
| 🔗 맥락 연결 | index.json 기반 이전 브리핑과 관련 뉴스 자동 연결 |
| 🗑️ 자동 정리 | 2주 지난 브리핑 파일 자동 삭제 |

---

## 사전 준비

```
1. Claude Code 데스크탑 앱   https://claude.ai/code
2. GitHub CLI                winget install GitHub.cli
                             gh auth login
3. 인터넷 연결               (웹 검색 권한 필요)
```

---

## 사용법

| 작업 | 입력 |
|------|------|
| 브리핑 수동 실행 | `브리핑 만들어줘` |
| 자동 실행 | 데스크탑 앱 스케줄드 태스크 → 매일 오전 7시 |
| GitHub 이슈 등록 | `이슈 등록해줘` / `re-issue` |
| 이슈 해결 | `이슈 #N 해결해줘` / `resolve #N` |
| 전체 개선 사이클 | `한 번에 다 돌려줘` / `풀 사이클` |
| 문서 중복 제거 | `문서 최적화` |

---

## 파일 구조

```
AI동향/
├── CLAUDE.md                          # Claude 운영 지침
├── README.md                          # 이 파일
├── SOUL.md                            # 설계 철학
├── .gitignore
├── index.json                         # 뉴스 키워드 인덱스 (영구 보관)
├── 브리핑_YYYY-MM-DD.html             # 생성된 브리핑 (로컬 2주 보관, GitHub 아카이브)
├── scripts/
│   ├── collect.py                     # RSS 기반 독립 수집 스크립트
│   └── requirements.txt
└── skills/
    ├── morning-ai-digest-skill.md     # 브리핑 생성 스킬 (디자인 규칙 포함)
    ├── audit-to-issue/
    │   └── SKILL.md                   # GitHub 이슈 등록 스킬
    ├── issues-plan-and-resolve/
    │   └── SKILL.md                   # 이슈 해결 스킬
    ├── briefingimprover.md            # 풀 사이클 개선 스킬
    └── optimize-docs/
        └── SKILL.md                   # 문서 중복 제거 스킬
```

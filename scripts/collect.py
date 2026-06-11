"""
AI 동향 브리핑 자동 수집 스크립트
실행: python scripts/collect.py
출력: 브리핑_YYYY-MM-DD.html + index.json 업데이트
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import feedparser
    import requests
except ImportError:
    print("의존성 설치 중... pip install -r scripts/requirements.txt")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "scripts/requirements.txt"], check=True)
    import feedparser
    import requests

# ── 설정 ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR
INDEX_FILE = BASE_DIR / "index.json"
TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = OUTPUT_DIR / f"브리핑_{TODAY}.html"
KEEP_DAYS = 14

RSS_SOURCES = [
    # 글로벌
    {"name": "TechCrunch AI",   "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "lang": "en"},
    {"name": "The Verge AI",    "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "lang": "en"},
    {"name": "VentureBeat AI",  "url": "https://venturebeat.com/category/ai/feed/", "lang": "en"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "lang": "en"},
    # 국내
    {"name": "AI타임스",        "url": "https://www.aitimes.com/rss/allArticle.xml", "lang": "ko"},
    {"name": "인공지능신문",    "url": "https://www.aitimes.kr/rss/allArticle.xml", "lang": "ko"},
]

AI_KEYWORDS = [
    "AI", "인공지능", "artificial intelligence", "machine learning", "deep learning",
    "LLM", "GPT", "Claude", "Gemini", "ChatGPT", "OpenAI", "Anthropic", "Google DeepMind",
    "Meta AI", "Mistral", "Llama", "model", "모델", "neural", "generative", "생성형",
    "로봇", "robot", "자율주행", "autonomous",
]

CATEGORY_RULES = {
    "기업 소식":   ["OpenAI", "Anthropic", "Google", "Meta", "Microsoft", "Apple", "삼성", "SKT", "네이버", "카카오", "IPO", "인수", "투자", "파트너십"],
    "모델·기술":   ["모델", "model", "출시", "release", "update", "업데이트", "GPT", "Claude", "Gemini", "Llama", "코딩", "coding", "추론", "reasoning"],
    "정책·산업":   ["규제", "regulation", "법", "law", "정책", "policy", "EU", "정부", "government", "시장", "market", "투자", "funding"],
    "연구·논문":   ["연구", "research", "논문", "paper", "arxiv", "benchmark", "벤치마크", "CVPR", "ICLR", "NeurIPS"],
}

# ── 수집 ──────────────────────────────────────────────────────────────────────

def fetch_articles() -> list[dict]:
    articles = []
    cutoff = datetime.now() - timedelta(hours=48)

    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:20]:
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                link = entry.get("link", "")
                published = entry.get("published_parsed")

                # 48시간 이내 기사만
                if published:
                    pub_dt = datetime(*published[:6])
                    if pub_dt < cutoff:
                        continue

                # AI 관련 필터
                text = (title + " " + summary).lower()
                if not any(kw.lower() in text for kw in AI_KEYWORDS):
                    continue

                articles.append({
                    "title": title,
                    "summary": re.sub(r"<[^>]+>", "", summary)[:300],
                    "link": link,
                    "source": source["name"],
                    "lang": source["lang"],
                })
        except Exception as e:
            print(f"  ⚠ {source['name']} 수집 실패: {e}")

    return articles


def categorize(article: dict) -> str:
    text = article["title"] + " " + article["summary"]
    for category, keywords in CATEGORY_RULES.items():
        if any(kw.lower() in text.lower() for kw in keywords):
            return category
    return "기업 소식"


def extract_keywords(article: dict) -> list[str]:
    stopwords = {"AI", "모델", "기술", "출시", "발표", "업데이트", "서비스", "플랫폼", "시스템"}
    candidates = re.findall(r"[A-Z][a-zA-Z]+|[가-힣]{2,6}", article["title"])
    return [w for w in dict.fromkeys(candidates) if w not in stopwords][:5]

# ── index.json ────────────────────────────────────────────────────────────────

def load_index() -> list:
    if INDEX_FILE.exists():
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    return []


def save_index(index: list, articles: list[dict]) -> None:
    # 오늘 날짜 항목 덮어쓰기
    index = [e for e in index if e["date"] != TODAY]
    index.append({
        "date": TODAY,
        "items": [{"title": a["title"], "keywords": extract_keywords(a)} for a in articles],
    })
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def find_related(index: list, article: dict) -> list[dict]:
    stopwords = {"AI", "모델", "기술", "출시", "발표", "업데이트", "서비스", "플랫폼", "시스템"}
    my_keywords = set(extract_keywords(article)) - stopwords
    related = []
    for entry in index:
        if entry["date"] == TODAY:
            continue
        for item in entry["items"]:
            match = my_keywords & (set(item.get("keywords", [])) - stopwords)
            if match:
                related.append({"date": entry["date"], "title": item["title"]})
    # 최근 날짜 기준 최대 3개
    related.sort(key=lambda x: x["date"], reverse=True)
    return related[:3]

# ── HTML 생성 ─────────────────────────────────────────────────────────────────

def make_related_html(related: list[dict]) -> str:
    if not related:
        return ""
    parts = []
    for r in related:
        path = OUTPUT_DIR / f"브리핑_{r['date']}.html"
        if path.exists():
            parts.append(f'<a href="브리핑_{r["date"]}.html" class="related-link">🔗 {r["title"][:30]} — {r["date"][5:]}</a>')
        else:
            parts.append(f'<span class="related-text">🔗 {r["title"][:30]} — {r["date"][5:]}</span>')
    return '<div class="related">' + "".join(parts) + "</div>"


CAT_CLASS = {"기업 소식": "company", "모델·기술": "model", "정책·산업": "policy", "연구·논문": "research"}
CAT_LABEL = {"기업 소식": "기업", "모델·기술": "모델", "정책·산업": "정책", "연구·논문": "연구"}
CAT_ICON  = {"기업 소식": "🏢", "모델·기술": "🧠", "정책·산업": "📋", "연구·논문": "🔬"}
CAT_DOT   = {"기업 소식": "#3b82f6", "모델·기술": "#8b5cf6", "정책·산업": "#f59e0b", "연구·논문": "#10b981"}


def make_card(article: dict, cat: str, related_html: str) -> str:
    cls = CAT_CLASS.get(cat, "company")
    lbl = CAT_LABEL.get(cat, cat)
    return f"""
    <div class="card {cls}">
      <div class="card-head">
        <div class="card-title">{article['title']}</div>
        <span class="cat-tag">{lbl}</span>
      </div>
      <div class="card-summary">{article['summary'][:160]}</div>
      <details>
        <summary>상세 보기</summary>
        <div class="detail-body">
          {article['summary']}
          <a class="source-link" href="{article['link']}" target="_blank">↗ 원문</a>
        </div>
      </details>
      {related_html}
    </div>"""


STYLE = """
:root{--bg:#f4f5f9;--surface:#fff;--border:#e2e4ef;--text:#18182a;--muted:#6b7280;--shadow:0 1px 8px rgba(0,0,0,.06);--c-company:#3b82f6;--c-model:#8b5cf6;--c-policy:#f59e0b;--c-research:#10b981}
@media(prefers-color-scheme:dark){:root{--bg:#0d0d1a;--surface:#16162a;--border:#252540;--text:#e8e8f4;--muted:#8b8ba8;--shadow:0 1px 8px rgba(0,0,0,.35)}}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15px;line-height:1.6;padding:1.25rem 1rem}
.container{max-width:740px;margin:0 auto}
header{display:flex;align-items:baseline;gap:.75rem;margin-bottom:1.25rem}
header h1{font-size:1.25rem;font-weight:800;letter-spacing:-.02em}
header .date{color:var(--muted);font-size:.82rem}
.top3{background:linear-gradient(135deg,#4f46e5,#7c3aed);border-radius:14px;padding:1.25rem 1.4rem;margin-bottom:1.75rem;color:#fff}
.top3-label{font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;opacity:.75;margin-bottom:.9rem}
.top3-item{display:flex;align-items:flex-start;gap:.75rem;margin-bottom:.65rem}
.top3-item:last-child{margin-bottom:0}
.top3-num{flex-shrink:0;width:1.4rem;height:1.4rem;border-radius:50%;background:rgba(255,255,255,.2);font-size:.72rem;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:.1rem}
.top3-text{font-size:.92rem;line-height:1.45}
.section{display:flex;align-items:center;gap:.5rem;margin:1.75rem 0 .75rem;font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.section-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.section-line{flex:1;height:1px;background:var(--border)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;border-left:4px solid var(--cat-color,#6366f1);padding:.95rem 1.1rem;margin-bottom:.65rem;box-shadow:var(--shadow)}
.card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:.5rem;margin-bottom:.35rem}
.card-title{font-weight:650;font-size:.95rem;line-height:1.4;flex:1}
.cat-tag{flex-shrink:0;font-size:.67rem;font-weight:700;padding:.15rem .5rem;border-radius:20px;background:color-mix(in srgb,var(--cat-color,#6366f1) 12%,transparent);color:var(--cat-color,#6366f1);margin-top:.1rem;white-space:nowrap}
.card-summary{font-size:.86rem;color:var(--muted);line-height:1.5;margin-bottom:.55rem}
details summary{font-size:.8rem;color:var(--cat-color,#6366f1);cursor:pointer;user-select:none;list-style:none;opacity:.85}
details summary::-webkit-details-marker{display:none}
details summary::before{content:"▸ ";font-size:.65rem}
details[open] summary::before{content:"▾ "}
.detail-body{margin-top:.65rem;padding-top:.65rem;border-top:1px solid var(--border);font-size:.86rem;line-height:1.65}
.source-link{display:inline-block;margin-top:.45rem;font-size:.78rem;color:var(--cat-color,#6366f1);text-decoration:none;opacity:.8}
.source-link:hover{opacity:1;text-decoration:underline}
.related{margin-top:.55rem;display:flex;flex-wrap:wrap;gap:.3rem}
.related a,.related span{font-size:.73rem;color:var(--muted);background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:.1rem .45rem;text-decoration:none}
.related a:hover{color:var(--text)}
.company{--cat-color:var(--c-company)}.model{--cat-color:var(--c-model)}.policy{--cat-color:var(--c-policy)}.research{--cat-color:var(--c-research)}
footer{margin-top:2.5rem;text-align:center;font-size:.74rem;color:var(--muted);opacity:.6}
"""


def generate_html(articles: list[dict], index: list) -> str:
    by_cat: dict[str, list] = {c: [] for c in CATEGORY_RULES}

    for a in articles:
        cat = categorize(a)
        a["related"] = find_related(index, a)
        by_cat.setdefault(cat, []).append(a)

    # 핵심 3줄: 임팩트(카테고리 우선순위) + 언론 커버리지
    top3 = sorted(articles, key=lambda a: (
        ["모델·기술", "기업 소식", "정책·산업", "연구·논문"].index(categorize(a))
    ))[:3]
    top3_items = "\n".join(
        f'<div class="top3-item"><div class="top3-num">{i+1}</div>'
        f'<div class="top3-text">{a["title"]}</div></div>'
        for i, a in enumerate(top3)
    )

    sections_html = ""
    for cat, cat_articles in by_cat.items():
        if not cat_articles:
            continue
        dot_color = CAT_DOT.get(cat, "#6366f1")
        icon = CAT_ICON.get(cat, "")
        section_header = (
            f'<div class="section">'
            f'<div class="section-dot" style="background:{dot_color}"></div>'
            f'{icon} {cat}'
            f'<div class="section-line"></div></div>'
        )
        cards = "".join(make_card(a, cat, make_related_html(a["related"])) for a in cat_articles)
        sections_html += section_header + cards

    total = sum(len(v) for v in by_cat.values())
    date_str = datetime.now().strftime('%Y년 %m월 %d일 (%a)').replace(
        'Mon','월').replace('Tue','화').replace('Wed','수').replace('Thu','목'
        ).replace('Fri','금').replace('Sat','토').replace('Sun','일')

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>AI 동향 브리핑 — {TODAY}</title>
  <style>{STYLE}</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🤖 AI 동향 브리핑</h1>
    <span class="date">{date_str} &middot; 뉴스 {total}건</span>
  </header>
  <div class="top3">
    <div class="top3-label">🔥 오늘의 핵심</div>
    {top3_items}
  </div>
  {sections_html}
  <footer>AI 동향 브리핑 · {TODAY} · scripts/collect.py 자동 생성</footer>
</div>
</body>
</html>"""

# ── 오래된 파일 정리 ──────────────────────────────────────────────────────────

def cleanup_old_files() -> None:
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    pattern = re.compile(r"브리핑_(\d{4}-\d{2}-\d{2})\.html$")
    for f in OUTPUT_DIR.glob("브리핑_*.html"):
        m = pattern.match(f.name)
        if m and datetime.strptime(m.group(1), "%Y-%m-%d") < cutoff:
            print(f"  🗑 삭제: {f.name}")
            f.unlink()

# ── 메인 ──────────────────────────────────────────────────────────────────────

def main():
    if OUTPUT_FILE.exists():
        print(f"오늘 브리핑이 이미 존재합니다: {OUTPUT_FILE.name}")
        if "--force" not in sys.argv:
            sys.exit(0)

    print("📡 뉴스 수집 중...")
    articles = fetch_articles()
    print(f"  → {len(articles)}개 수집")

    if len(articles) < 3:
        print("⚠ 수집된 뉴스가 너무 적습니다. 인터넷 연결을 확인하세요.")
        sys.exit(1)

    print("📖 index.json 읽는 중...")
    index = load_index()

    print("📝 HTML 생성 중...")
    html = generate_html(articles, index)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"✅ 브리핑 생성 완료: {OUTPUT_FILE.name}")

    print("💾 index.json 업데이트...")
    save_index(index, articles)

    print("🗑 오래된 파일 정리...")
    cleanup_old_files()

    # 브라우저 열기
    import subprocess as sp
    sp.Popen(["cmd", "/c", "start", "", str(OUTPUT_FILE)], shell=False)


if __name__ == "__main__":
    main()

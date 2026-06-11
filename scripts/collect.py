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


def make_card(article: dict, related_html: str) -> str:
    return f"""
    <div class="card">
      <div class="card-title">{article['title']}</div>
      <div class="card-summary">{article['summary'][:120]}…</div>
      <div class="card-meta">{article['source']}</div>
      <details>
        <summary>더보기</summary>
        <div class="detail-body">
          {article['summary']}
          <a class="source-link" href="{article['link']}" target="_blank">↗ 원문 보기</a>
        </div>
      </details>
      {related_html}
    </div>"""


STYLE = """
:root{--bg:#f8f9fc;--surface:#fff;--border:#e5e7ef;--text:#1e1e2e;--muted:#6b7280;--accent:#6366f1;--accent-light:#eef2ff;--shadow:0 2px 12px rgba(0,0,0,.07)}
@media(prefers-color-scheme:dark){:root{--bg:#0f0f1a;--surface:#1a1a2e;--border:#2a2a40;--text:#e8e8f0;--muted:#9ca3af;--accent:#818cf8;--accent-light:#1e1e3a;--shadow:0 2px 12px rgba(0,0,0,.3)}}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,sans-serif;line-height:1.6;padding:1.5rem}
.container{max-width:780px;margin:0 auto}
header h1{font-size:1.6rem;font-weight:700;color:var(--accent)}
header p{color:var(--muted);font-size:.9rem;margin-top:.3rem}
.summary-box{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border-radius:14px;padding:1.4rem 1.6rem;margin:1.5rem 0}
.summary-box h2{font-size:1rem;margin-bottom:.8rem;opacity:.9}
.summary-box ol{padding-left:1.2rem}
.summary-box li{margin-bottom:.4rem;font-size:.95rem}
.section-title{font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:2rem 0 .9rem;padding-bottom:.4rem;border-bottom:1px solid var(--border)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:.85rem;box-shadow:var(--shadow)}
.card-title{font-weight:600;font-size:.97rem;margin-bottom:.3rem}
.card-summary{font-size:.88rem;color:var(--muted);margin-bottom:.3rem}
.card-meta{font-size:.75rem;color:var(--accent);margin-bottom:.5rem}
details summary{font-size:.83rem;color:var(--accent);cursor:pointer;user-select:none;list-style:none}
details summary::before{content:'+ '}
details[open] summary::before{content:'− '}
.detail-body{margin-top:.7rem;font-size:.87rem;border-top:1px solid var(--border);padding-top:.7rem}
.source-link{display:inline-block;margin-top:.5rem;font-size:.8rem;color:var(--accent);text-decoration:none}
.source-link:hover{text-decoration:underline}
.related{margin-top:.6rem;font-size:.78rem;color:var(--muted)}
.related-link{display:block;color:var(--accent);text-decoration:none;margin-top:.2rem}
.related-text{display:block;margin-top:.2rem}
footer{margin-top:3rem;text-align:center;font-size:.78rem;color:var(--muted)}
"""


def generate_html(articles: list[dict], index: list) -> str:
    by_cat: dict[str, list] = {c: [] for c in CATEGORY_RULES}

    for a in articles:
        cat = categorize(a)
        a["related"] = find_related(index, a)
        by_cat.setdefault(cat, []).append(a)

    # 핵심 3줄: 임팩트(카테고리 우선순위) + 언론 커버리지(한 번에 여러 소스 언급)
    top3 = sorted(articles, key=lambda a: (
        ["모델·기술", "기업 소식", "정책·산업", "연구·논문"].index(categorize(a))
    ))[:3]
    top3_html = "\n".join(f"<li>{a['title']}</li>" for a in top3)

    sections_html = ""
    icons = {"기업 소식": "🏢", "모델·기술": "🧠", "정책·산업": "📋", "연구·논문": "🔬"}
    for cat, cat_articles in by_cat.items():
        if not cat_articles:
            continue
        cards = "".join(make_card(a, make_related_html(a["related"])) for a in cat_articles)
        sections_html += f'<div class="section-title">{icons.get(cat,"")} {cat}</div>{cards}'

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
    <p>{datetime.now().strftime('%Y년 %m월 %d일')} · RSS 자동 수집</p>
  </header>
  <div class="summary-box">
    <h2>🔥 오늘의 핵심 3줄</h2>
    <ol>{top3_html}</ol>
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

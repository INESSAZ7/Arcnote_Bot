import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from newspaper import Article

YOUTUBE_RE = re.compile(r"(youtube\.com|youtu\.be)")
GITHUB_RE = re.compile(r"github\.com")

def detect_type(url: str) -> str:
    if YOUTUBE_RE.search(url):
        return "youtube"
    elif GITHUB_RE.search(url):
        return "github"
    elif "medium.com" in url:
        return "medium"
    elif "arxiv.org" in url:
        return "arxiv"
    elif "habr.com" in url:
        return "habr"
    else:
        return "generic"

async def extract_metadata(url: str) -> tuple[str, str, str]:
    source = detect_type(url)
    try:
        if source == "youtube":
            title, desc = await parse_youtube(url)
            return title, desc, source
        elif source == "github":
            title, desc = parse_github(url)
            return title, desc, source
        elif source in {"medium", "generic"}:
            title, desc = parse_article(url)
            return title, desc, source
        elif source == "arxiv":
            title, desc = parse_arxiv(url)
            return title, desc, source
        elif source == "habr":
            title, desc = parse_habr(url)
            return title, desc, source
        else:
            title, desc = fallback(url)
            return title, desc, source
    except Exception:
        title, desc = fallback(url)
        return title, desc, source

def parse_article(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article.title or "Без названия", article.summary or ""

def parse_github(url):
    match = re.search(r"github\.com/([^/]+/[^/]+)", url)
    title = f"GitHub Repo: {match.group(1)}" if match else "GitHub Repo"
    return title, ""

async def parse_youtube(url):
    # Используем oEmbed
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    resp = requests.get(oembed_url)
    if resp.ok:
        data = resp.json()
        return data.get("title", "YouTube видео"), data.get("author_name", "")
    return "YouTube видео", ""

def parse_arxiv(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("h1", class_="title")
    abstract = soup.find("blockquote", class_="abstract")
    return title.get_text(strip=True) if title else "ArXiv статья", \
           abstract.get_text(strip=True).replace("Abstract:", "") if abstract else ""

def parse_habr(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("h1")
    summary = soup.find("meta", {"name": "description"})
    return title.get_text(strip=True) if title else "Habr статья", \
           summary.get("content", "") if summary else ""

def fallback(url):
    domain = urlparse(url).netloc
    return f"Ссылка с {domain}", ""



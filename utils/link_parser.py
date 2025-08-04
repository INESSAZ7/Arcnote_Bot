import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yt_dlp

YOUTUBE_RE = re.compile(r"(youtube\.com|youtu\.be)")
GITHUB_RE = re.compile(r"github\.com")


def truncate_description(text: str, max_length: int = 500) -> str:
    """
    Truncates text to a specified length and adds an ellipsis if necessary.
    """
    return text[:max_length].rstrip() + "..." if len(text) > max_length else text



def detect_type(url: str) -> str:
    """
    Detects the type of link.
    """
    if YOUTUBE_RE.search(url):
        return "youtube"
    elif GITHUB_RE.search(url):
        return "github"
    elif "arxiv.org" in url:
        return "arxiv"
    elif "habr.com" in url:
        return "habr"
    else:
        return "generic"

async def extract_metadata(url: str) -> tuple[str, str, str]:
    """
    Extracts metadata from a link.
    """
    source = detect_type(url)
    try:
        if source == "youtube":
            title, desc = await parse_youtube(url)

        elif source == "github":
            title, desc = parse_github(url)

        elif source == "arxiv":
            title, desc = parse_arxiv(url)

        elif source == "habr":
            title, desc = parse_habr(url)

        else:   
            title, desc = parse_article(url)

    except Exception:
        title, desc = fallback(url)
    
    return title, desc, source

def parse_article(url: str) -> tuple[str, str]:
    """
    Universal parser for the title and short description from the HTML page.
    Returns: (title, description)
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Заголовок
        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else "Без названия"
        )

        # Описание (в приоритете — OpenGraph, потом meta name)
        description = ""
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            description = og_desc["content"].strip()
        else:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                description = meta_desc["content"].strip()

        return title, truncate_description(description)

    except Exception:
        return "Без названия", ""

def parse_github(url):
    match = re.search(r"github\.com/([^/]+/[^/]+)", url)
    title = f"GitHub Repo: {match.group(1)}" if match else "GitHub Repo"
    return title, ""

def parse_youtube(url: str) -> tuple[str, str]:

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "YouTube видео")
            description = truncate_description(info.get("description", ""))
            return title, truncate_description(description)
    except Exception:
        return "YouTube видео", ""

def parse_arxiv(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("h1", class_="title")
    abstract = soup.find("blockquote", class_="abstract")
    return title.get_text(strip=True) if title else "ArXiv статья", \
           truncate_description(abstract.get_text(strip=True).replace("Abstract:", "") if abstract else "")

def parse_habr(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("h1")
    summary = soup.find("meta", {"name": "description"})
    return title.get_text(strip=True) if title else "Habr статья", \
           truncate_description(summary.get("content", "") if summary else "")

def fallback(url):
    domain = urlparse(url).netloc
    return f"Ссылка с {domain}", ""



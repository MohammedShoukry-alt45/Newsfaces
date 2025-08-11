# core/warc_processing.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_image_urls(html_content, base_url):
    soup = BeautifulSoup(html_content, "html.parser")
    image_urls = []

    # <img src="">
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            abs_url = urljoin(base_url, src)
            if is_valid_url(abs_url):
                image_urls.append(abs_url)

    # <link rel="image_src" href="">
    for link in soup.find_all("link", rel="image_src"):
        href = link.get("href")
        if href:
            abs_url = urljoin(base_url, href)
            if is_valid_url(abs_url):
                image_urls.append(abs_url)

    return list(set(image_urls))  # remove duplicates

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme in ["http", "https"] and parsed.netloc)

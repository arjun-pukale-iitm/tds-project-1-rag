import os
import json
import re
from datetime import datetime
from urllib.parse import urljoin
from markdownify import markdownify as md
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://tds.s-anand.net/#/2025-01/"
BASE_ORIGIN = "https://tds.s-anand.net"
OUTPUT_DIR = "tds_pages_md"
METADATA_FILE = "website_content.json"

visited = set()
metadata = []


def cleanHtmlTags(text):
  try:
    soup = BeautifulSoup(text, "html.parser")
    # Remove all code and pre tags
    for tag in soup(['code', 'pre']):
      tag.decompose()
    clean_text = soup.get_text(separator=" ", strip=True)
  except:
    clean_text = text
  return clean_text

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip().replace(" ", "_")

def extract_all_internal_links(page):
    links = page.eval_on_selector_all("a[href]", "els => els.map(el => el.href)")
    return list(set(
        link for link in links
        if BASE_ORIGIN in link and '/#/' in link
    ))

def wait_for_article_and_get_html(page):
    page.wait_for_selector("article.markdown-section#main", timeout=10000)
    return page.inner_html("article.markdown-section#main")

def crawl_page(page, url):
    url = url.split("?")[0] #ignore query parameters to avoid duplicacy
    url = url.replace("/../","/") #to avoid duplicate urls
    if url in visited:
        return
    visited.add(url)

    print(f"📄 Visiting: {url}")
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        html = wait_for_article_and_get_html(page)
    except Exception as e:
        print(f"❌ Error loading page: {url}\n{e}")
        return

    # Extract title
    title = page.title().split(" - ")[0].strip() or f"page_{len(visited)}"


    metadata.append({
        "title": title,
        "original_url": url,
        "downloaded_at": datetime.now().isoformat(),
        "content":cleanHtmlTags(html)
    })

    # Recursively crawl all links found on the page (not just main content)
    links = extract_all_internal_links(page)
    for link in links:
        if link not in visited:
            crawl_page(page, link)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    global visited, metadata

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        crawl_page(page, BASE_URL)

        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✅ Completed. {len(metadata)} pages saved.")
        browser.close()

if __name__ == "__main__":
    main()
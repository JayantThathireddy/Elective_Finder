"""
ingest.py — Collect r/UNCCharlotte threads about courses and professors.

Uses Playwright to render Reddit pages as a real browser would.
Saves each thread as a JSON file in documents/.
Run: python ingest.py
"""

import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

DOCUMENTS_DIR = Path("documents")
SUBREDDIT = "UNCCharlotte"
BASE_URL = "https://www.reddit.com"

SEARCH_QUERIES = [
    "course recommendation",
    "easy class",
    "elective",
    "professor recommendation",
    "GPA booster",
    "liberal studies",
    "writing requirement",
    "best professor",
    "what classes should I take",
    "easy courses",
    "class advice",
    "ITCS recommendation",
]

MIN_COMMENTS = 2
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def extract_comments_from_page(page) -> list:
    """Extract all visible shreddit-comment elements from a loaded thread page."""
    return page.evaluate("""
        () => {
            const comments = Array.from(document.querySelectorAll('shreddit-comment'));
            return comments.map(c => {
                const slot = c.querySelector('[slot="comment"]');
                const body = slot ? slot.innerText.trim() : '';
                return {
                    id: c.getAttribute('thingid') || '',
                    author: c.getAttribute('author') || '',
                    body: body,
                    score: parseInt(c.getAttribute('score') || '0', 10),
                    depth: parseInt(c.getAttribute('depth') || '0', 10),
                };
            }).filter(c => c.body && c.body.length > 5
                       && c.body !== '[deleted]' && c.body !== '[removed]');
        }
    """)


def extract_post_body(page) -> str:
    """Extract the selftext body of the post."""
    return page.evaluate("""
        () => {
            const bodyEl = document.querySelector('[slot="text-body"]');
            return bodyEl ? bodyEl.innerText.trim() : '';
        }
    """)


def scroll_to_load_comments(page, scrolls: int = 4):
    """Scroll down multiple times to trigger lazy-loading of comments."""
    for _ in range(scrolls):
        page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
        page.wait_for_timeout(1200)


def scrape_thread(page, url: str) -> dict | None:
    """Load a thread URL and extract post + comments."""
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
    except PWTimeout:
        page.wait_for_timeout(2000)

    page.wait_for_timeout(2000)
    scroll_to_load_comments(page, scrolls=5)

    # Get post title from shreddit-post element
    post_data = page.evaluate("""
        () => {
            const post = document.querySelector('shreddit-post');
            if (!post) return null;
            return {
                title: post.getAttribute('post-title') || '',
                permalink: post.getAttribute('permalink') || '',
                score: parseInt(post.getAttribute('score') || '0', 10),
                author: post.getAttribute('author') || '',
                created: post.getAttribute('created-timestamp') || '',
                commentCount: parseInt(post.getAttribute('comment-count') || '0', 10),
            };
        }
    """)

    if not post_data or not post_data.get("title"):
        return None

    body = extract_post_body(page)
    comments = extract_comments_from_page(page)

    return {
        "thread_id": url.split("/comments/")[1].split("/")[0] if "/comments/" in url else "",
        "title": post_data["title"],
        "url": url,
        "subreddit": SUBREDDIT,
        "score": post_data["score"],
        "author": post_data["author"],
        "body": body,
        "comments": [
            {
                "comment_id": c["id"],
                "author": c["author"],
                "body": c["body"],
                "score": c["score"],
                "depth": c["depth"],
            }
            for c in comments
        ],
    }


def get_post_links_from_search(page, query: str, limit: int = 8) -> list[str]:
    """Search r/UNCCharlotte and return unique post URLs."""
    url = (
        f"{BASE_URL}/r/{SUBREDDIT}/search/"
        f"?q={query.replace(' ', '+')}&restrict_sr=1&sort=top&t=all"
    )
    try:
        page.goto(url, wait_until="networkidle", timeout=25000)
    except PWTimeout:
        page.wait_for_timeout(1000)

    page.wait_for_timeout(3000)

    links = page.evaluate(f"""
        () => {{
            const pattern = /\\/r\\/{SUBREDDIT.lower()}\\/comments\\/[a-z0-9]+/i;
            const seen = new Set();
            const results = [];
            document.querySelectorAll('a[href]').forEach(a => {{
                const href = a.href;
                if (pattern.test(href) && !seen.has(href)) {{
                    seen.add(href);
                    results.push(href);
                }}
            }});
            return results.slice(0, {limit});
        }}
    """.replace("SUBREDDIT.lower()", f'"{SUBREDDIT.lower()}"'))

    return links


def main():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    seen_ids: set[str] = set()

    for existing in DOCUMENTS_DIR.glob("*.json"):
        thread_id = existing.stem.split("_")[0]
        seen_ids.add(thread_id)

    print(f"Starting with {len(seen_ids)} existing documents.\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()

        for query in SEARCH_QUERIES:
            print(f'Searching: "{query}"')
            try:
                links = get_post_links_from_search(page, query)
            except Exception as e:
                print(f"  Search error: {e}")
                continue

            print(f"  Found {len(links)} links")
            for link in links:
                match = re.search(r"/comments/([a-z0-9]+)/", link)
                if not match:
                    continue
                thread_id = match.group(1)
                if thread_id in seen_ids:
                    continue
                seen_ids.add(thread_id)

                try:
                    thread = scrape_thread(page, link)
                    if not thread:
                        print(f"  No post data extracted: {link[:60]}")
                        continue

                    n_comments = len(thread["comments"])
                    if n_comments < MIN_COMMENTS:
                        print(f"  Skip ({n_comments} comments): {thread['title'][:55]}")
                        continue

                    title_slug = re.sub(r"[^a-z0-9]+", "_", thread["title"].lower())[:40].strip("_")
                    filename = f"{thread_id}_{title_slug}.json"
                    filepath = DOCUMENTS_DIR / filename
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(thread, f, ensure_ascii=False, indent=2)

                    print(f"  Saved ({n_comments} comments): {thread['title'][:55]}")
                    time.sleep(1)

                except Exception as e:
                    print(f"  Error on {link[:60]}: {e}")

        browser.close()

    total = len(list(DOCUMENTS_DIR.glob("*.json")))
    print(f"\nDone. {total} thread files in documents/")


if __name__ == "__main__":
    main()

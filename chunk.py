"""
chunk.py — Split saved Reddit threads into retrievable chunks.

Each comment or post body becomes one chunk (if under MAX_CHARS).
Longer text is split with a small overlap.
Every chunk is prefixed with the post title for context.

Run standalone to inspect sample chunks:
    python chunk.py
"""

import json
from pathlib import Path
from typing import Generator

DOCUMENTS_DIR = Path("documents")
MAX_CHARS = 600
OVERLAP_CHARS = 75
MIN_CHUNK_CHARS = 30


def _split_long_text(text: str) -> Generator[str, None, None]:
    """Split text exceeding MAX_CHARS at sentence boundaries with overlap."""
    if len(text) <= MAX_CHARS:
        yield text
        return

    start = 0
    while start < len(text):
        end = start + MAX_CHARS
        if end < len(text):
            # Try to break at a sentence boundary
            break_at = text.rfind(". ", start, end)
            if break_at > start + MAX_CHARS // 2:
                end = break_at + 1
        chunk = text[start:end].strip()
        if len(chunk) >= MIN_CHUNK_CHARS:
            yield chunk
        start = end - OVERLAP_CHARS


def chunk_thread(thread: dict) -> list[dict]:
    """Convert a thread dict into a list of chunk dicts."""
    chunks = []
    title = thread.get("title", "").strip()
    url = thread.get("url", "")
    prefix = f"[r/UNCCharlotte | {title}] "

    def make_chunk(text: str, chunk_type: str, index: int) -> dict:
        return {
            "text": prefix + text,
            "source": url,
            "title": title,
            "type": chunk_type,
            "chunk_index": index,
        }

    # Post body
    body = thread.get("body", "").strip()
    if body and body not in ("[deleted]", "[removed]") and len(body) >= MIN_CHUNK_CHARS:
        for i, segment in enumerate(_split_long_text(body)):
            chunks.append(make_chunk(segment, "post_body", i))

    # Comments (flat — replies are stored at top level by ingest.py)
    for comment in thread.get("comments", []):
        body = comment.get("body", "").strip()
        if not body or body in ("[deleted]", "[removed]") or len(body) < MIN_CHUNK_CHARS:
            continue
        for i, segment in enumerate(_split_long_text(body)):
            chunks.append(make_chunk(segment, "comment", i))

    return chunks


def chunk_all_documents() -> list[dict]:
    """Load every JSON file in documents/ and return all chunks."""
    files = sorted(DOCUMENTS_DIR.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No .json files found in {DOCUMENTS_DIR}/. Run ingest.py first.")

    all_chunks: list[dict] = []
    for filepath in files:
        with open(filepath, encoding="utf-8") as f:
            thread = json.load(f)
        thread_chunks = chunk_thread(thread)
        all_chunks.extend(thread_chunks)
        print(f"  {filepath.name}: {len(thread_chunks)} chunks")

    return all_chunks


if __name__ == "__main__":
    import random

    print(f"Processing documents in {DOCUMENTS_DIR}/...\n")
    chunks = chunk_all_documents()
    print(f"\nTotal chunks: {len(chunks)}")

    print("\n--- 5 random sample chunks ---")
    for chunk in random.sample(chunks, min(5, len(chunks))):
        print(f"\n[{chunk['type']} | {chunk['source']}]")
        print(chunk["text"][:400])
        if len(chunk["text"]) > 400:
            print("...")

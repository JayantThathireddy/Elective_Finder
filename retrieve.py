"""
retrieve.py — Query ChromaDB for the top-k most relevant chunks.

Can be run standalone to test retrieval against a set of queries:
    python retrieve.py
"""

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "uncc_electives"
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5

# Lazy-loaded singletons — loaded on first call to retrieve()
_model: SentenceTransformer | None = None
_collection: chromadb.Collection | None = None


def _load():
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Return the top-k chunks most semantically similar to query.

    Each result dict has:
        text     — the full chunk text (includes [r/UNCCharlotte | title] prefix)
        source   — Reddit thread URL
        title    — post title
        distance — cosine distance (lower = more similar; < 0.5 is good)
    """
    _load()
    embedding = _model.encode([query]).tolist()
    results = _collection.query(
        query_embeddings=embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "text": doc,
            "source": meta["source"],
            "title": meta["title"],
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


if __name__ == "__main__":
    test_queries = [
        "What are easy electives at UNCC for non-majors?",
        "Which professors at UNCC are most recommended?",
        "What courses satisfy the writing requirement at UNC Charlotte?",
        "Are there any GPA booster classes at UNCC?",
        "What advice do students give freshmen about picking classes?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        results = retrieve(query)
        for i, r in enumerate(results, 1):
            print(f"  [{i}] dist={r['distance']:.3f} | {r['title'][:55]}")
            print(f"       {r['text'][len('[r/UNCCharlotte | '):].split('] ', 1)[-1][:120]}...")

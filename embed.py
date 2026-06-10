"""
embed.py — Embed all chunks and load them into ChromaDB.

Run this once after chunking to build the vector store:
    python embed.py

Re-running drops and recreates the collection.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from chunk import chunk_all_documents

COLLECTION_NAME = "uncc_electives"
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 100


def build_vector_store() -> chromadb.Collection:
    print("Loading chunks...")
    chunks = chunk_all_documents()
    print(f"\n{len(chunks)} total chunks\n")

    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    print("Embedding chunks (this may take a minute on CPU)...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32).tolist()

    print("\nConnecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Drop existing collection to rebuild clean
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Dropped existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    print(f"Inserting {len(chunks)} chunks into ChromaDB in batches of {BATCH_SIZE}...")
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start : batch_start + BATCH_SIZE]
        batch_emb = embeddings[batch_start : batch_start + BATCH_SIZE]
        collection.add(
            ids=[f"chunk_{batch_start + j}" for j in range(len(batch))],
            embeddings=batch_emb,
            documents=[c["text"] for c in batch],
            metadatas=[
                {
                    "source": c["source"],
                    "title": c["title"],
                    "type": c["type"],
                }
                for c in batch
            ],
        )

    print(f"\nDone. {len(chunks)} chunks stored in ChromaDB at {CHROMA_PATH}/")
    return collection


if __name__ == "__main__":
    build_vector_store()

# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This system covers **elective course and professor recommendations for UNCC (UNC Charlotte) students**, sourced from student discussions on the r/uncc subreddit.

Official channels — the course catalog, department websites, and advisor meetings — tell you what a course covers and how many credits it gives. They do not tell you whether a professor grades fairly, whether the workload is manageable alongside other commitments, or which courses students actually found worthwhile. Students figure this out by asking each other on Reddit, Discord, and in the hallways — but that knowledge is scattered across hundreds of threads with no way to search it systematically. This system makes that student-generated knowledge searchable and answerable.

---

## Documents

Sources are Reddit threads from r/uncc collected via the public JSON API. Searches used the following queries against r/uncc with `sort=top&t=all`: "elective", "easy class", "course recommendation", "professor recommendation", "GPA booster", "liberal studies", "writing intensive", "best professor", "what classes should I take".

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/uncc Reddit thread | Students asking for easy elective recommendations | https://www.reddit.com/r/uncc/ (search: "elective") |
| 2 | r/uncc Reddit thread | Students asking about GPA booster courses | https://www.reddit.com/r/uncc/ (search: "GPA booster") |
| 3 | r/uncc Reddit thread | Students asking about course recommendations | https://www.reddit.com/r/uncc/ (search: "course recommendation") |
| 4 | r/uncc Reddit thread | Students asking about easy classes | https://www.reddit.com/r/uncc/ (search: "easy class") |
| 5 | r/uncc Reddit thread | Students asking about professor recommendations | https://www.reddit.com/r/uncc/ (search: "professor recommendation") |
| 6 | r/uncc Reddit thread | Students asking about liberal studies requirements | https://www.reddit.com/r/uncc/ (search: "liberal studies") |
| 7 | r/uncc Reddit thread | Students asking about writing intensive courses | https://www.reddit.com/r/uncc/ (search: "writing intensive") |
| 8 | r/uncc Reddit thread | Students asking for best professors | https://www.reddit.com/r/uncc/ (search: "best professor") |
| 9 | r/uncc Reddit thread | Students asking what classes to take | https://www.reddit.com/r/uncc/ (search: "what classes should I take") |
| 10 | r/uncc Reddit thread | Top-voted course advice posts from r/uncc | https://www.reddit.com/r/uncc/ (top posts, course-related) |

Exact thread URLs are embedded in each saved JSON file in the `documents/` folder as the `url` field.

---

## Chunking Strategy

**Chunk size:** 600 characters maximum per chunk (effective content ~570 chars after title prefix)

**Overlap:** 75 characters — applied only when a post body or comment exceeds 600 chars and must be split

**Reasoning:**

Reddit comments are the primary unit of information in this corpus. A typical comment expressing a course recommendation is 1–3 sentences: "Take MUSC 1100 — super chill professor, no prior music experience needed, easy A as long as you show up." This is roughly 100–200 characters. A longer, multi-paragraph comment might reach 500–800 characters.

Treating each comment as its own chunk makes sense because:
1. Comments are already self-contained opinions — they were written as standalone thoughts
2. Splitting a comment mid-sentence would lose its conclusion (e.g., "I liked this professor because..." without the reason)
3. Most comments fit comfortably under 600 chars with no splitting needed

The 75-character overlap is small by design. When a long comment does get split, the overlap carries the tail of the prior sentence into the next chunk, preventing the most common boundary problem (losing the beginning of a thought). It doesn't need to be large because we're not dealing with long-form prose where context builds over many paragraphs.

Each chunk is prefixed with `[r/uncc | {post title}]` so that even a short comment like "Yes, loved that class" carries enough context for the embedding model to understand what the comment is about.

**Final chunk count:** Updated after corpus collection — target range is 150–800 chunks across 10–20 threads.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

This model runs locally with no API key or rate limits, produces 384-dimensional embeddings, and is fast enough to embed several hundred chunks in under a minute on CPU. It was designed for semantic similarity tasks and performs well on short, informal text — which matches our Reddit comment corpus.

**Top-k:** 5

Retrieving 5 chunks gives the LLM enough different perspectives to synthesize an answer without flooding the context with loosely related content. At k=5 with ~150 chars of usable content per chunk on average, the total context passed to the LLM is roughly 750–3000 characters — well within the model's limit and focused enough to stay on-topic.

**Production tradeoff reflection:**

If deploying this for real users, I would weigh:

- **Accuracy on informal text**: `all-MiniLM-L6-v2` is a general-purpose model. A domain-adapted model (fine-tuned on academic or student forum text) would likely produce more precise embeddings for queries like "which professor grades easy." OpenAI's `text-embedding-3-large` or Cohere's `embed-v3` would be candidates — higher accuracy but API cost and rate limits.
- **Context length**: `all-MiniLM-L6-v2` has a 256-token input limit; longer chunks would get truncated. For a corpus with longer documents, a model like `text-embedding-3-large` (8191 tokens) would handle those without truncation.
- **Latency**: Local models add startup time but have zero per-query API cost and no network latency once loaded. For a production system with many concurrent users, an API-hosted model with a warm connection pool might have lower p99 latency.
- **Multilingual support**: Not needed here (r/uncc is English), but Cohere's multilingual embed model would matter for a broader university audience.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What UNCC courses do students recommend as easy electives for non-majors? | Names of specific courses (e.g., introductory music, art, or LBST courses) with comments about low workload or easy grading |
| 2 | Which UNCC professors are most recommended by students for undergraduate courses? | Names of specific professors with positive feedback about teaching style, helpfulness, or fair grading |
| 3 | What do students say about UNCC courses that satisfy the liberal studies writing requirement? | Specific course names or professor names for writing-intensive courses, with opinions on workload |
| 4 | Are there any UNCC courses that students consider GPA boosters? | Specific course names mentioned as easy A's or grade-friendly, with student reasoning |
| 5 | What advice do UNCC students give about picking electives as a freshman or sophomore? | General advice about course load, which departments have easy courses, timing, and registration tips |

*Note: Expected answers will be updated with specific course/professor names after the corpus is collected and reviewed.*

---

## Anticipated Challenges

1. **Short comments with no standalone meaning**: Many Reddit replies are very short ("Same, took it last semester and loved it") and reference the parent post or a prior comment without restating it. Even with the post title prefix, the embedding may not capture enough signal to match a specific query. This could cause those chunks to score low on relevant queries or, worse, surface for unrelated queries that happen to share words like "loved" or "semester." Mitigation: filter out comments under 30 characters before chunking.

2. **Post title prefix not matching query vocabulary**: A query like "easy electives" might retrieve chunks from a thread titled "Course recommendations for spring?" rather than one titled "Easy electives at UNCC?" — or miss the most relevant thread because the post title uses different wording. Since every chunk is prefixed with the title, a misleading title can misdirect retrieval. Mitigation: test retrieval with varied phrasings of the same question during Milestone 4 evaluation.

3. **Outdated information**: Reddit posts from several years ago may reference professors who have left, courses that have been renamed, or requirements that have changed. The system has no way to filter by date during retrieval. A user getting confident-sounding but outdated advice is a real risk. Mitigation: store `created_utc` in chunk metadata and surface it in the source attribution so users can judge recency.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UNCC Elective Finder Pipeline                 │
└─────────────────────────────────────────────────────────────────────┘

  [1] Document Ingestion          [2] Chunking
  ──────────────────────          ─────────────
  Reddit JSON API                 chunk.py
  (requests, no auth)    ──────►  Per-comment + post-body chunks
  ingest.py                       600 char max, 75 char overlap
  Saves: documents/*.json         Prefix: [r/uncc | {post title}]
                                  Saves: in-memory list of dicts
         │
         ▼
  [3] Embedding + Vector Store    [4] Retrieval
  ────────────────────────────    ─────────────
  embed.py                        retrieve.py
  Model: all-MiniLM-L6-v2  ────►  Query → embed → ChromaDB.query()
  (sentence-transformers)         top-k=5, returns chunks + distances
  Store: ChromaDB (local)         + source metadata
  Path: ./chroma_db/
         │
         ▼
  [5] Generation                  [6] Interface
  ──────────────────              ─────────────
  generate.py                     app.py
  Groq API               ──────►  Gradio web UI
  llama-3.3-70b-versatile         Input: text question
  Grounding prompt                Output: answer + source list
  Source attribution              localhost:7860
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**

I will give Claude my Documents section (the list of r/uncc search queries and the JSON structure of a saved thread) and my Chunking Strategy section, and ask it to implement `ingest.py` (Reddit JSON API scraper that saves threads to `documents/*.json`) and `chunk.py` (per-comment chunker with the 600-char limit, 75-char overlap, and title prefix). I will verify that: (1) ingest.py actually saves files with the correct JSON structure, (2) chunk.py produces chunks that are readable when printed, (3) no chunks contain `[deleted]` or `[removed]` text, and (4) the total chunk count is in the 150–800 range.

**Milestone 4 — Embedding and retrieval:**

I will give Claude my Retrieval Approach section (model name, top-k value) and my Architecture diagram (ChromaDB as the vector store, metadata fields needed for source attribution), and ask it to implement `embed.py` (load chunks from chunk.py, embed with all-MiniLM-L6-v2, store in ChromaDB with source/title/type metadata) and `retrieve.py` (query function returning top-k chunks with distances). I will verify by running 3 of my 5 eval questions and checking that: (1) returned chunks visibly relate to the query, (2) distance scores on top results are below 0.5, and (3) source metadata is correctly attached.

**Milestone 5 — Generation and interface:**

I will give Claude my grounding requirement (LLM must answer only from retrieved chunks, cite source thread titles), the output format (answer + sources list), and the Gradio skeleton from the project instructions. I will ask it to implement `generate.py` (Groq client, system prompt enforcing grounding, context formatting) and `app.py` (Gradio UI). I will verify by: (1) testing that the system prompt actually refuses to answer out-of-scope questions, (2) confirming source citations appear in every response, and (3) manually checking 2–3 responses against the retrieved chunks to confirm the answer is grounded.

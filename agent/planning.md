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

Sources are Reddit threads from r/UNCCharlotte, collected using Playwright (a headless browser) to bypass Reddit's 2025 API lockdown on unauthenticated access. Searches used the following queries against r/UNCCharlotte with `sort=top&t=all`: "course recommendation", "easy class", "elective", "professor recommendation", "GPA booster", "liberal studies", "writing requirement", "best professor", "what classes should I take", "easy courses", "class advice", "ITCS recommendation".

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/UNCCharlotte | What's up with the hype around John Taylor (Calc 1) | https://www.reddit.com/r/UNCCharlotte/comments/181jbzn/ |
| 2 | r/UNCCharlotte | Best GPA booster classes | https://www.reddit.com/r/UNCCharlotte/comments/18ulbk9/ |
| 3 | r/UNCCharlotte | Easy GPA Boosters | https://www.reddit.com/r/UNCCharlotte/comments/7nqyhe/ |
| 4 | r/UNCCharlotte | Any interesting GPA boosters? | https://www.reddit.com/r/UNCCharlotte/comments/1mdnxit/ |
| 5 | r/UNCCharlotte | Easiest Liberal Studies (LBST) Course | https://www.reddit.com/r/UNCCharlotte/comments/v84z6f/ |
| 6 | r/UNCCharlotte | LBST courses? | https://www.reddit.com/r/UNCCharlotte/comments/4clp16/ |
| 7 | r/UNCCharlotte | Elective class recommendations | https://www.reddit.com/r/UNCCharlotte/comments/1kp7521/ |
| 8 | r/UNCCharlotte | What are some easy classes for my non-business elective | https://www.reddit.com/r/UNCCharlotte/comments/apzhcu/ |
| 9 | r/UNCCharlotte | Easiest classes to take for credits?? | https://www.reddit.com/r/UNCCharlotte/comments/ox7jv6/ |
| 10 | r/UNCCharlotte | MATH 1103 and ITCS 3688 Professors | https://www.reddit.com/r/UNCCharlotte/comments/k5oivt/ |
| 11 | r/UNCCharlotte | Recommended Teachers for spring classes | https://www.reddit.com/r/UNCCharlotte/comments/59c47d/ |
| 12 | r/UNCCharlotte | Remember: Pick your professors, not your classes | https://www.reddit.com/r/UNCCharlotte/comments/13u6y6q/ |
| 13–63 | r/UNCCharlotte | Additional advice, campus guide, and course threads | documents/*.json (url field in each file) |

63 thread files collected total. All are from r/UNCCharlotte. Exact URLs embedded in each `documents/*.json` file.

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

Each chunk is prefixed with `[r/UNCCharlotte | {post title}]` so that even a short comment like "Yes, loved that class" carries enough context for the embedding model to understand what the comment is about.

**Final chunk count:** 1,408 chunks from 63 threads (average ~22 chunks per thread).

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

This model runs locally with no API key or rate limits, produces 384-dimensional embeddings, and is fast enough to embed several hundred chunks in under a minute on CPU. It was designed for semantic similarity tasks and performs well on short, informal text — which matches our Reddit comment corpus.

**Top-k:** 8 (increased from initial spec of 5 after observing that k=5 retrieved question posts but not enough answer comments)

Retrieving 5 chunks gives the LLM enough different perspectives to synthesize an answer without flooding the context with loosely related content. At k=5 with ~150 chars of usable content per chunk on average, the total context passed to the LLM is roughly 750–3000 characters — well within the model's limit and focused enough to stay on-topic.

**Production tradeoff reflection:**

If deploying this for real users, I would weigh:

- **Accuracy on informal text**: `all-MiniLM-L6-v2` is a general-purpose model. A domain-adapted model (fine-tuned on academic or student forum text) would likely produce more precise embeddings for queries like "which professor grades easy." OpenAI's `text-embedding-3-large` or Cohere's `embed-v3` would be candidates — higher accuracy but API cost and rate limits.
- **Context length**: `all-MiniLM-L6-v2` has a 256-token input limit; longer chunks would get truncated. For a corpus with longer documents, a model like `text-embedding-3-large` (8191 tokens) would handle those without truncation.
- **Latency**: Local models add startup time but have zero per-query API cost and no network latency once loaded. For a production system with many concurrent users, an API-hosted model with a warm connection pool might have lower p99 latency.
- **Multilingual support**: Not needed here (r/UNCCharlotte is English), but Cohere's multilingual embed model would matter for a broader university audience.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What GPA booster classes do students recommend at UNCC? | Specific course names: GEOG 3180 (Hazards and Disasters with Dr. Collins), THEA 1502/LBST 1104 with Morong, ROTC, business ethics and film; comment on low workload or easy grading |
| 2 | Which professors do UNCC students recommend for undergraduate courses? | Names of specific professors with positive teaching comments: John Taylor (Calc 1), Aileen Benedict (ITCS 3162), Morong (THEA), Dr. Klotz (LBST Music) |
| 3 | What do UNCC students say about the easiest liberal studies (LBST) courses? | LBST 2102 with Professor Viale, LBST Music with Dr. Klotz (online), LBST geography with Barbara John; opinions on workload |
| 4 | What do students say about John Taylor's Calculus 1 class at UNCC? | Discussion of John Taylor's structured teaching, workbook, neat handwriting, no surprises on exams; highly recommended |
| 5 | What is the best sushi restaurant in Charlotte? | System should refuse: "I don't have enough information in the available student discussions to answer that." |

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
  Playwright browser              chunk.py
  (r/UNCCharlotte)       ──────►  Per-comment + post-body chunks
  ingest.py                       600 char max, 75 char overlap
  Saves: documents/*.json         Prefix: [r/UNCCharlotte | {post title}]
                                  Saves: in-memory list of dicts
         │
         ▼
  [3] Embedding + Vector Store    [4] Retrieval
  ────────────────────────────    ─────────────
  embed.py                        retrieve.py
  Model: all-MiniLM-L6-v2  ────►  Query → embed → ChromaDB.query()
  (sentence-transformers)         top-k=8, returns chunks + distances
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

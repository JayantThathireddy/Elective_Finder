# The Unofficial Guide — UNCC Elective Finder

---

## Domain

This system covers **elective course and professor recommendations for UNC Charlotte (UNCC) students**, sourced from real student discussions on the r/UNCCharlotte subreddit.

Official channels — the course catalog, department websites, and advisor meetings — describe what a course covers and how many credits it awards. They do not tell you whether a professor grades fairly, whether the workload is manageable alongside four other courses, or which courses students actually found valuable or easy. Students figure this out by asking each other on Reddit, Discord, and in person. That knowledge is scattered across hundreds of threads with no searchable structure. This system makes it answerable.

---

## Document Sources

All documents are Reddit threads from r/UNCCharlotte, collected using a Playwright-based scraper (no API credentials required — the subreddit is publicly accessible when rendered in a real browser). Searches were run against r/UNCCharlotte for the following queries: "course recommendation", "easy class", "elective", "professor recommendation", "GPA booster", "liberal studies", "writing requirement", "best professor", "what classes should I take", "easy courses", "class advice", "ITCS recommendation".

| # | Source | Type | URL |
|---|--------|------|-----|
| 1 | What's up with the hype around John Taylor (Calc 1) | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/181jbzn/ |
| 2 | Best GPA booster classes | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/18ulbk9/ |
| 3 | Easy GPA Boosters | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/7nqyhe/ |
| 4 | Any interesting GPA boosters? | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/1mdnxit/ |
| 5 | Easiest Liberal Studies (LBST) Course | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/v84z6f/ |
| 6 | LBST courses? | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/4clp16/ |
| 7 | Elective class recommendations | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/1kp7521/ |
| 8 | What are some easy classes for my non-business elective | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/apzhcu/ |
| 9 | Easiest classes to take for credits?? | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/ox7jv6/ |
| 10 | MATH 1103 and ITCS 3688 Professors | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/k5oivt/ |
| 11 | Recommended Teachers for spring classes | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/59c47d/ |
| 12 | Remember: Pick your professors, not your classes | Reddit thread | https://www.reddit.com/r/UNCCharlotte/comments/13u6y6q/ |
| 13–63 | Additional r/UNCCharlotte threads (advice, course tips, campus guides) | Reddit threads | documents/*.json |

63 total thread files collected. Full source URLs are embedded in each `documents/*.json` file as the `url` field.

---

## Chunking Strategy

**Chunk size:** 600 characters maximum per chunk

**Overlap:** 75 characters — applied only when a single comment or post body exceeds 600 characters and must be split

**Why these choices fit your documents:**

Reddit comments are the primary unit of information in this corpus. A typical course recommendation comment is 1–3 sentences: "LBST Music with Dr. Klotz is the easiest class I've ever taken as long as you do your assignments on time." That's roughly 100–200 characters. An unusually detailed comment reaches 400–600 characters.

Treating each comment as its own chunk makes sense because comments are written as standalone thoughts. Splitting a comment mid-sentence would break its conclusion — a comment recommending a professor without naming why would be useless as a retrieved chunk. The 600-character ceiling is generous enough that most comments fit in one chunk. When a longer post body or detailed comment must be split, the 75-character overlap carries the tail of the prior sentence into the next chunk.

Each chunk is prefixed with `[r/UNCCharlotte | {post title}]` so that a short comment like "Yes, Morong is super easy" carries the context of what thread it came from. Without the prefix, the embedding model would treat this as a semantically empty fragment.

**Final chunk count:** 1,408 chunks from 63 threads (average: ~22 chunks per thread)

**Sample chunks** (5 representative examples, verbatim):

```
[comment | https://www.reddit.com/r/UNCCharlotte/comments/v84z6f/...]
[r/UNCCharlotte | Easiest Liberal Studies (LBST) Course] lbst music with dr klotz
online, easiest class ive ever taken. just do your assignments on time and participate
in the discussions for extra credit

[comment | https://www.reddit.com/r/UNCCharlotte/comments/181jbzn/...]
[r/UNCCharlotte | What's up with the hype around John Taylor (Calc 1)] He provides a
heavily structured curriculum with relevant homework sets that prepare you for the tests.
There are no surprises in the taylors' calc classes. If you do the work, you'll ace
the tests.

[comment | https://www.reddit.com/r/UNCCharlotte/comments/1mdnxit/...]
[r/UNCCharlotte | Any interesting GPA boosters?] Try the American studies department,
lots of random electives about different subjects. Or the English department has a lot
of classes that aren't locked to the major that could be interesting. I've taken two
classes about Disney and one about Beyoncé trying to boost my gpa and get to 120
credits lol

[post_body | https://www.reddit.com/r/UNCCharlotte/comments/1mdnxit/...]
[r/UNCCharlotte | Any interesting GPA boosters?] My GPA is pretty good right now
(3.42) but I don't really want to miss out on some scholarships with a 3.5 GPA cutoff.
I tried getting into venture's rock climbing course but it filled up before I could
join. Any other GPA boosters that I could join that won't just be discussion boards?

[comment | https://www.reddit.com/r/UNCCharlotte/comments/v84z6f/...]
[r/UNCCharlotte | Easiest Liberal Studies (LBST) Course] LBST 2102 with Professor viale
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key)

This model was chosen because it runs entirely on CPU with no API cost or rate limits, produces 384-dimensional embeddings, and is designed for semantic similarity tasks. It performs well on short, informal text — which matches the Reddit comment corpus. The model was downloaded once on first use and cached locally.

**Production tradeoff reflection:**

If deploying for real users, I would weigh:

- **Accuracy on domain-specific text:** `all-MiniLM-L6-v2` is a general-purpose model. Queries like "easy electives" don't always retrieve answers that use the equivalent phrase "GPA boosters" — the vocabulary gap between the query and the answer reduces recall. A model fine-tuned on student forum text or academic course discussions would close that gap. OpenAI's `text-embedding-3-large` or Cohere's `embed-v3` score higher on retrieval benchmarks and would be candidates for a production system.
- **Context length:** `all-MiniLM-L6-v2` has a 256-token input limit. Longer chunks would be truncated. For corpora with longer documents, `text-embedding-3-large` (8,191 tokens) handles full-length documents without truncation.
- **Cost and latency:** Local embedding has zero per-query cost and no network latency once loaded. For many concurrent users, an API-hosted model with a warm connection pool might have lower p99 latency than cold-starting a local model.
- **Multilingual support:** Not needed here (r/UNCCharlotte is English), but Cohere's multilingual embed model would matter for a broader student population.

---

## Retrieval Test Results

Three queries were run against the vector store to verify retrieval quality before wiring in generation. Top-5 chunks are shown with cosine distances (lower = more similar; below 0.5 is acceptable).

---

**Query 1: "What do students say about John Taylor's Calculus 1 class at UNCC?"**

| Rank | Distance | Source thread | Chunk text (excerpt) |
|------|----------|---------------|---------------------|
| 1 | 0.274 | What's up with the hype around John Taylor (Calc 1) | `2 at UNCC so thats why the faster teaching wasn't as big a problem for me. But yeah If you can get a Taylor get one, if you can get John Taylor especially if you're new to calculus, GET HIM!!!!!` |
| 2 | 0.276 | What's up with the hype around John Taylor (Calc 1) | `you don't take Taylor for Calc 1, watch his videos along with your classes. He has many lectures on YouTube, including all of Calc 1...` |
| 3 | 0.280 | What's up with the hype around John Taylor (Calc 1) | `The Taylors are just very concise and set things up in patterns that are more easily memorized. They write the notes book/guide book that's required for the class...` |
| 4 | 0.287 | What's up with the hype around John Taylor (Calc 1) | `He provides a heavily structured curriculum with relevant homework sets that prepare you for the tests. There are no surprises in the taylors' calc classes.` |
| 5 | 0.292 | What's up with the hype around John Taylor (Calc 1) | `For a strong foundation in calculus, Taylor is what you need. He wrote a workbook that you follow along with...` |

**Why these chunks are relevant:** All 5 results come from the single dedicated thread about John Taylor. Every chunk is either a direct student recommendation or a specific description of his teaching style. Distances are tight (0.274–0.292), indicating the query matched the corpus with high precision. The chunks name Taylor by full name, describe his curriculum structure, workbook, YouTube lectures, and exam style — exactly what the query is asking.

---

**Query 2: "What do UNCC students say about the easiest liberal studies (LBST) courses?"**

| Rank | Distance | Source thread | Chunk text (excerpt) |
|------|----------|---------------|---------------------|
| 1 | 0.222 | Easiest Liberal Studies (LBST) Course | `I am a computer engineering major, and in my plan of study, they want me to do a liberal studies course. All of it looks boring and not so much of my interest. Which one is the easiest to do and complete with an A?` |
| 2 | 0.261 | Easiest Liberal Studies (LBST) Course | `Most of the assignments are hella easy and projects feel like high school` |
| 3 | 0.265 | Easiest Liberal Studies (LBST) Course | `It's more about the professor than the class.` |
| 7 | 0.318 | Easiest Liberal Studies (LBST) Course | `LBST 2102 with Professor viale` |
| 8 | 0.338 | Easiest Liberal Studies (LBST) Course | `lbst music with dr klotz online, easiest class ive ever taken. just do your assignments on time and participate in the discussions for extra credit` |

**Why these chunks are relevant:** All 5 (and the k=8 results shown at ranks 7–8) come directly from the "Easiest Liberal Studies (LBST) Course" thread. The top chunks are the original question and general opinions; the answer chunks with specific course names (LBST 2102, LBST Music with Dr. Klotz) appear at ranks 7–8 because their short length carries less semantic signal than the longer question post. Still, both answer chunks are retrieved and used in generation.

---

**Query 3: "What GPA booster classes do students recommend at UNCC?"**

| Rank | Distance | Source thread | Chunk text (excerpt) |
|------|----------|---------------|---------------------|
| 1 | 0.215 | Best GPA booster classes | `Hey I'm looking for a few easy classes to get my gpa up a bit. If you guys have any classes that you've taken in the past that were particularly easy or simple to follow I'd love to know.` |
| 2 | 0.235 | Any interesting GPA boosters? | `what courses were they, i'm interested` |
| 6 | 0.304 | Any interesting GPA boosters? | `My GPA is pretty good right now (3.42) but I don't really want to miss out on some scholarships with a 3.5 GPA cutoff. I tried getting into venture's rock climbing course...` |
| 8 | 0.317 | Any interesting GPA boosters? | `Try the American studies department, lots of random electives about different subjects. Or the English department has a lot of classes that aren't locked to the major that could be interesting. I've taken two classes about Disney and one about Beyoncé trying to boost my gpa and get to 120 credits lol` |

The top-ranked chunks for this query are the question posts — students asking for GPA boosters — rather than the answer comments containing specific course names. The one actionable answer (rank 8, American Studies / English / Disney / Beyoncé) appears only at k=8. This is the vocabulary gap failure: the answer comments with specific course codes (GEOG 3180, THEA 1502) exist in the corpus but rank outside the top 8 because their short texts don't share enough vocabulary with the query phrase "GPA booster."

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant for UNC Charlotte (UNCC) students who want honest,
student-sourced advice about elective courses and professors.

You will be given excerpts from real student discussions on r/UNCCharlotte.
Answer the user's question using ONLY the information in those excerpts.
Do NOT draw on your own general knowledge about universities or courses.

Rules:
1. If the excerpts contain enough information, answer directly and specifically.
2. If the excerpts do NOT contain enough information to answer, say exactly:
   "I don't have enough information in the available student discussions to answer that."
3. Never speculate or guess beyond what is in the excerpts.
4. End your response with: "Sources:" followed by the post titles you used.
```

**How source attribution is surfaced in the response:**

Sources are enforced at two levels:
1. The system prompt instructs the LLM to end every response with a "Sources:" list of the post titles it drew from.
2. After generation, the pipeline programmatically appends the retrieved Reddit thread URLs to the response output (separate from the LLM-generated citation), so source links are always present even if the model omits them.

The LLM also receives each chunk prefixed with its post title: `[Excerpt N — from post: "Post Title"]`, which reinforces grounding by labeling exactly which text the model is allowed to use.

**Example grounded responses:**

*Query: "What do students say about John Taylor's Calculus 1 class at UNCC?"*

> Students highly recommend John Taylor for Calculus 1, citing his concise and structured teaching style, which makes the material easier to memorize. He provides a heavily structured curriculum with relevant homework sets, and his classes are well-organized, leaving no surprises on tests. Students also appreciate his sense of humor, neat handwriting, and ability to explain every step clearly. He has made a workbook that is used by all calculus classes, and his online lectures are highly regarded, with some students using them as their primary study resource.
>
> Sources: What's up with the hype around John Taylor (Calc 1)

*Query: "What do UNCC students say about the easiest LBST courses?"*

> According to student discussions, LBST 2102 with Professor Viale and LBST Music with Dr. Klotz (online) are considered easy courses. One student mentioned that LBST Music with Dr. Klotz was the "easiest class I've ever taken" as long as you do your assignments on time and participate in discussions for extra credit. However, opinions vary — another student warned that what makes a class easy is more about the professor than the class itself.
>
> Sources: Easiest Liberal Studies (LBST) Course, LBST courses?

**Out-of-scope refusal example:**

*Query: "What is the best sushi restaurant in Charlotte?"*

> I don't have enough information in the available student discussions to answer that.

The system correctly declined because no retrieved chunk addressed restaurants, and the distances on all retrieved chunks were above 0.58 — a signal that retrieval found nothing relevant.

---

## Query Interface

The interface is a Gradio web app (`app.py`), accessible at `http://localhost:7860` after running `python app.py`.

**Input field:** A text box labeled "Your question" with placeholder text showing example queries. Users can press Enter or click the "Ask" button to submit.

**Output fields:** Two side-by-side text boxes:
- **Answer (from student discussions):** The LLM-generated response, grounded in retrieved chunks. Includes inline source post titles at the end.
- **Source threads (r/UNCCharlotte):** The Reddit thread URLs the answer was retrieved from, one per line.

**Sample interaction transcript:**

```
Input: What GPA booster classes do students recommend at UNCC?

Answer: Students recommend classes from the American Studies department and the English
department as GPA boosters. Specifically, classes about different subjects, Disney,
and Beyoncé are mentioned as examples of interesting electives that can help boost GPA.

Sources: [r/UNCCharlotte | Any interesting GPA boosters?]

Source threads (r/UNCCharlotte):
• https://www.reddit.com/r/UNCCharlotte/comments/18ulbk9/best_gpa_booster_classes/
• https://www.reddit.com/r/UNCCharlotte/comments/1mdnxit/any_interesting_gpa_boosters/
• https://www.reddit.com/r/UNCCharlotte/comments/7nqyhe/easy_gpa_boosters/
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What GPA booster classes do students recommend at UNCC? | Specific course names: GEOG 3180, THEA 1502/LBST 1104, ROTC, business ethics, film | Mentioned American Studies/English GPA boosters (Disney, Beyoncé courses), THEA 1502 with Morong; missed GEOG 3180 and ROTC | Relevant | Partially accurate |
| 2 | Which professors do UNCC students recommend for undergraduate courses? | Names of specific professors with positive comments: John Taylor, Aileen Benedict, Morong | "I don't have enough information" — retrieved chunks were questions asking for professor names, not responses with names | Partially relevant | Inaccurate |
| 3 | What do UNCC students say about the easiest LBST courses? | LBST 1104, LBST 2102, LBST Music with Dr. Klotz, geography with Barbara John | Named LBST 2102 with Professor Viale and LBST Music with Dr. Klotz as easiest; included nuance about professor mattering more than the class | Relevant | Accurate |
| 4 | What do students say about John Taylor's Calculus 1 class at UNCC? | Discussion of John Taylor's structured teaching, workbook, popularity among Calc 1 students | Named structured curriculum, open workbook, neat handwriting, humor, no surprises on exams; well-grounded in retrieved chunks | Relevant | Accurate |
| 5 | What is the best sushi restaurant in Charlotte? | System should refuse to answer | "I don't have enough information in the available student discussions to answer that." | Off-target (dist > 0.58 on all chunks) | Accurate (correct refusal) |

---

## Failure Case Analysis

**Question that failed:** "Which professors do UNCC students recommend for undergraduate courses?"

**What the system returned:** "I don't have enough information in the available student discussions to answer that."

**Root cause (tied to a specific pipeline stage):**

This is a retrieval failure caused by a mismatch between how the query embeds and how the answer chunks embed. The query "which professors are recommended" semantically matches threads that *ask* for professor recommendations (like "MATH 1103 and ITCS 3688 Professors — Does anyone have any recommendations?") rather than threads that *provide* them. The answer chunks — individual comments that name a specific professor — are short (e.g., "Take Dr. Smith for ITCS 3162, she's fantastic") and don't share much vocabulary with the query "which professors are recommended." Short chunks carrying only a professor's name provide very little semantic signal for the `all-MiniLM-L6-v2` model to match.

The result is that the top-8 retrieved chunks are questions asking for recommendations, not answers. When the LLM sees 8 excerpts that all ask "who should I take?" without any answers, it correctly says it can't answer.

**What you would change to fix it:**

Two approaches would help:
1. **Increase k significantly (to 15–20):** Getting deeper into the retrieval results would surface more answer comments alongside the question posts. The answer comments exist in the corpus — they're just ranked below the question posts.
2. **Context-enriched chunking:** Instead of chunking comments in isolation, include the immediate parent comment or the top-voted reply alongside each comment chunk. That way a chunk like "Take Dr. Smith for ITCS" carries more context and embeds more robustly. This would require restructuring the chunker to be reply-tree-aware rather than treating all comments as flat.

---

## Spec Reflection

**One way the spec helped you during implementation:**

Writing the chunking strategy in planning.md before touching any code forced a concrete decision: treat each Reddit comment as its own chunk, prefixed with the post title. When chunk.py was being implemented, the logic was already defined — no experimentation with chunk sizes that produced bad results before settling on a number. The spec also identified the risk of short, decontextualized comments (Anticipated Challenge 1), which is exactly what materialized in the Q2 professor retrieval failure.

**One way your implementation diverged from the spec, and why:**

The spec assumed data would be collected using Reddit's public JSON API (via `requests`) and used `r/uncc` as the target subreddit. In implementation, both assumptions proved wrong: Reddit's JSON API now returns 403 for all unauthenticated requests, and the correct subreddit for UNCC students is `r/UNCCharlotte`, not `r/uncc`. The ingestion approach was rebuilt using Playwright (a headless browser) to render Reddit as a real browser would, which bypassed the API block. The subreddit was corrected after the first screenshot showed `r/uncc` was restricted and empty. These pivots were not in the spec because they couldn't have been — the API change was discovered empirically during implementation.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline**

- *What I gave the AI:* The Documents section and Chunking Strategy section from planning.md, including the per-comment chunking rationale, the 600-character max, the 75-character overlap, and the title-prefix format. I also described the JSON structure of a saved Reddit thread.
- *What it produced:* `ingest.py` (Playwright-based Reddit scraper) and `chunk.py` (per-comment chunker with split_long_text helper). The scraper correctly targeted r/UNCCharlotte, waited for dynamic content to render, and saved threads in the expected JSON structure.
- *What I changed or overrode:* The initial `ingest.py` used Python `requests` with the Reddit JSON API, which returned 403 on all endpoints. I diagnosed the failure (Reddit's 2024–2025 API lockdown), searched for alternatives, tested Playwright, and directed the AI to rebuild the scraper around Playwright's browser automation instead. I also changed the target subreddit from `r/uncc` to `r/UNCCharlotte` after discovering via screenshot that r/uncc was restricted.

**Instance 2 — Embedding, retrieval, and generation pipeline**

- *What I gave the AI:* The Retrieval Approach section from planning.md (model name `all-MiniLM-L6-v2`, top-k=5, ChromaDB as the vector store, source metadata fields), the Architecture diagram, and the grounding requirement (answer only from retrieved context, cite source post titles, refuse out-of-scope questions with a specific phrase).
- *What it produced:* `embed.py`, `retrieve.py`, and `generate.py`. The embedding script used sentence-transformers correctly and stored chunks with the right metadata. The retrieval function returned distances alongside chunks. The system prompt enforced grounding with explicit rules.
- *What I changed or overrode:* I increased the default `k` from 5 to 8 after observing that k=5 was retrieving only question posts and missing answer comments. I also ran the evaluation tests myself and identified Q1 and Q2 as partial and full failures rather than accepting the system's output uncritically — the AI couldn't run the evaluation itself.

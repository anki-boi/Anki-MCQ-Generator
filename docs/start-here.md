# Start Here — Practical First Steps

If you're asking "where do we start?", start with a **thin vertical slice** that proves the pipeline works end-to-end.

## Goal of Sprint 1 (Vertical Slice)
By the end of Sprint 1, a user should be able to:
1. Upload one PDF from Android.
2. Process it into topic-based chunks.
3. Generate MCQs from one selected chunk via Gemini.
4. Download a CSV preview of cards.

Do **not** start with `.apkg` packaging first. CSV-first lets you validate content quality faster.

## Day-by-Day Execution (7 Days)

### Day 1 — Contracts + API Skeleton
- Lock request/response contracts for jobs, sources, chunks, and card output.
- Implement endpoints:
  - `POST /v1/jobs`
  - `POST /v1/jobs/{id}/sources`
  - `POST /v1/jobs/{id}/start`
  - `GET /v1/jobs/{id}`
  - `GET /v1/jobs/{id}/preview`
- Store job status in DB (`queued`, `parsing`, `chunking`, `generating`, `done`, `failed`).

### Day 2 — PDF Text Extraction
- Parse native PDF text.
- Add OCR fallback for scanned pages.
- Persist `source_segments` with page + offsets.

### Day 3 — Topic-First Chunking
- Build heading-aware topic/subtopic tree.
- Chunk to target 5k–10k tokens:
  - split large nodes by subheadings, then semantically.
  - merge tiny siblings under same parent when coherent.
- Save chunk metadata (`topic`, `subtopic`, `token_estimate`, `source_refs`).

### Day 4 — Gemini Generation Integration
- Use `prompts/mcq_generation_prompt.md` as the generation template.
- Run 1 chunk → JSON card output.
- Validate against `backend/schemas/card_output.schema.json`.

### Day 5 — Validation + CSV Export
- Enforce hard rules:
  - no true/false
  - >= 6 options
  - options > correct answers
- Convert output to pipe-separated CSV with `<br>` in choice/answer columns.

### Day 6 — Android MVP Screen Flow
- Screens: Upload → Job status → Card preview → Download CSV.
- Poll job status every few seconds while active.

### Day 7 — QA + Prompt Tuning
- Test 3 real PDFs (small, medium, scanned).
- Tune prompt and post-validation heuristics based on failure cases.

## Strict Priorities (in order)
1. Correctness of extraction/chunking.
2. MCQ quality constraints.
3. Usable preview loop.
4. Then `.apkg`.

## Exit Criteria for Sprint 1
- One complete PDF pipeline works without manual intervention.
- At least 80% of generated cards pass validation automatically.
- CSV imports correctly into Anki note template.

---

## Sprint 2 Preview (After CSV MVP)
- Add `.apkg` export with subdecks: `Course::Topic::Subtopic`.
- Include topic evidence images in media bundle.
- Append image references in `Extra`.
- Add deterministic note IDs to prevent duplicate imports.

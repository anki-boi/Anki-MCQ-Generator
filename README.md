# Anki MCQ Generator (Android-First)

Android app + backend pipeline for turning **PDFs, text, screenshots, and pictures** into high-quality MCQ flashcards based on the [True Anki MCQ Note Template](https://github.com/anki-boi/True-Anki-MCQ-Note-Template).

## Product Goals
- Accept learning sources from mobile users with minimal friction.
- Extract and chunk content by **topic/subtopic** (not just fixed length).
- Feed chunks to Gemini for MCQ generation with controlled token budgets.
- Export results as:
  - `CSV` (for manual review/import), or
  - `.apkg` (with subdecks, media, and populated `Extra` resources).

## Repository Layout
- `docs/system-architecture.md` – End-to-end architecture and components.
- `docs/implementation-roadmap.md` – Practical build sequence for MVP → V2.
- `prompts/mcq_generation_prompt.md` – Production prompt template for Gemini.
- `backend/schemas/` – JSON schemas for chunks and generated cards.

## High-Level Flow
1. Upload (PDF/text/image) from Android.
2. Parse & OCR content.
3. Build topic outline and semantic chunks targeting ~5k–10k tokens/chunk.
4. Generate MCQs via Gemini.
5. Validate output structure + quality rules.
6. Export CSV and/or `.apkg` with subdecks + media references in `Extra`.

## Key Technical Constraints
- Keep generation context compact and hierarchical: one outline + one chunk at a time.
- Enforce output guardrails to keep card quality high (distractor parity, no T/F, minimum option count).
- For `.apkg`, attach topic evidence images and place references in `Extra` per card.

## Suggested Stack
- **Android:** Kotlin + Jetpack Compose + WorkManager + Room.
- **Backend API:** FastAPI or NestJS.
- **Queue workers:** Celery/RQ (Python) or BullMQ (Node).
- **LLM:** Gemini 1.5 Pro / latest long-context model.
- **Storage:** Postgres + object storage (S3-compatible) for source files and media.
- **Anki packaging:** Python `genanki` + media manifest.

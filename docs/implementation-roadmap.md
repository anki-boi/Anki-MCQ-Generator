# Implementation Roadmap

## Phase 0 — Foundations
- Set up mono-repo structure:
  - `android-app/`
  - `backend-api/`
  - `workers/`
- Provision Postgres + object storage.
- Add auth and basic job model.

## Phase 1 — MVP (CSV First)
- Upload PDF/text/image from Android.
- Parse text + OCR pipeline.
- Topic-first chunking (5k–10k tokens target).
- Gemini generation using strict prompt template.
- CSV export with required field formatting.
- Human preview screen to approve/reject cards.

## Phase 2 — `.apkg` Export
- Implement True Anki MCQ note model mapping.
- Build deck/subdeck hierarchy from topic tree.
- Capture topic evidence images from PDF pages/regions.
- Embed media + references in `Extra` field.

## Phase 3 — Quality Upgrades
- Distractor parity scoring and auto-repair.
- Duplicate question clustering.
- Per-domain prompt presets (medicine, law, engineering).

## Phase 4 — Scale + UX
- Batch jobs and background queue autoscaling.
- Resume/cancel jobs.
- Shared decks and collaboration features.

## Acceptance Criteria (MVP)
- User can submit at least one PDF and receive valid CSV cards.
- Every output card conforms to the MCQ format constraints.
- Chunking logs show semantic/topic-based splits, not naive fixed windows.
- End-to-end job status visible in app.

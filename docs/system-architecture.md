# System Architecture

## 1) Core Services

### A. Android Client
- Handles file capture/upload:
  - PDFs
  - pasted text
  - screenshots
  - camera pictures
- Displays ingestion status:
  - uploaded
  - parsing
  - chunking
  - generating
  - exported
- Allows users to pick output format (`CSV`, `.apkg`, or both).

### B. API Gateway
- Auth + upload endpoints.
- Creates a generation job and returns a `job_id`.
- Persists job metadata and user preferences.

### C. Ingestion & Parsing Worker
- PDF extraction (native text first, OCR fallback).
- Image OCR + layout segmentation.
- Normalizes text into sections with page/region provenance.

### D. Outline + Chunking Worker
- Builds a topic tree:
  - topic
  - subtopic
  - source spans
- Produces chunks based on semantic boundaries and token budget.
- Target chunk size:
  - Preferred: 5k–10k input tokens
  - Hard max per request: model-safe threshold configured in service

### E. MCQ Generation Worker (Gemini)
- Runs per chunk with:
  - course metadata
  - topic/subtopic labels
  - source chunk
  - strict prompt template
- Emits structured JSON card candidates.

### F. Validation + Dedup Worker
- Enforces rules:
  - no true/false
  - >= 6 options
  - options > correct answers
  - choice parity checks (length, structure heuristics)
- Deduplicates near-identical cards across chunks.
- Merges cards to deck/subdeck buckets.

### G. Export Worker
- CSV exporter:
  - pipes as separators
  - `<br>` inside answer fields
- `.apkg` exporter:
  - one deck per topic/subtopic path
  - note model mapped to True Anki MCQ fields
  - media bundle includes topic evidence screenshots/snippets
  - `Extra` includes rationale, optional correction note, and resource image link

## 2) Data Model (Minimal)
- `users`
- `jobs`
- `sources`
- `source_segments` (page, bbox, text)
- `topic_nodes`
- `chunks`
- `cards_raw`
- `cards_validated`
- `exports`

## 3) API Surface (Example)
- `POST /v1/jobs`
  - create job + upload references
- `POST /v1/jobs/{id}/sources`
  - add text/PDF/image sources
- `POST /v1/jobs/{id}/start`
  - start processing pipeline
- `GET /v1/jobs/{id}`
  - status + progress
- `GET /v1/jobs/{id}/preview`
  - card preview and validation report
- `POST /v1/jobs/{id}/export`
  - request CSV/apkg build
- `GET /v1/exports/{export_id}/download`

## 4) Chunking Strategy (Topic-First)
1. Build hierarchical outline from headings + semantic similarity.
2. Collect source spans per node.
3. Estimate tokens per node.
4. If node > 10k tokens:
   - split by subheadings first
   - then paragraph-level semantic split
5. If node < 5k tokens:
   - merge with adjacent sibling within same parent when coherent
6. Add overlap window (5%–10%) to preserve continuity.

## 5) .apkg-specific Considerations
- Use deterministic note IDs to avoid duplicates on regeneration.
- Deck naming convention:
  - `Course::Topic::Subtopic`
- Add media files referenced in `Extra`:
  - e.g., `evidence_topic_03_page_12.png`
- Keep image references stable and relative for Anki packaging.

## 6) Quality/Safety Controls
- PII redaction pass before model submission.
- Hallucination risk control:
  - require source anchoring metadata in raw output
  - flag cards with weak source match
- Retry policy:
  - exponential backoff
  - chunk-level retry only (not whole job)


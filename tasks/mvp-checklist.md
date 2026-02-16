# MVP Build Checklist

## Backend
- [ ] Job lifecycle endpoints implemented.
- [ ] Upload pipeline supports PDF/text/image.
- [ ] PDF extraction + OCR fallback.
- [ ] Topic/subtopic chunking (5k–10k token target).
- [ ] Gemini generation call with retries.
- [ ] JSON schema validation for model output.
- [ ] CSV export formatter compatible with Anki template.

## Android
- [ ] Auth + create job.
- [ ] Upload source files.
- [ ] Start processing job.
- [ ] Live status screen.
- [ ] Card preview UI.
- [ ] Download/share CSV.

## Quality
- [ ] No true/false cards.
- [ ] Minimum 6 options.
- [ ] options > correct answers.
- [ ] Basic duplicate detection.
- [ ] Spot-check distractor parity.

## Launch Gate (MVP)
- [ ] 3 sample documents run end-to-end.
- [ ] CSV imports correctly into Anki.
- [ ] Failures are visible with actionable messages.

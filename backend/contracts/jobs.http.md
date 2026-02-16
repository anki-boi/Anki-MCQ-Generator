# API Contract Examples (HTTP)

## Create Job
`POST /v1/jobs`

Request:
```json
{
  "course_name": "Pharmacology 101",
  "output_format": ["csv", "apkg"]
}
```

Response:
```json
{
  "job_id": "job_123",
  "status": "queued"
}
```

## Upload Source
`POST /v1/jobs/{job_id}/sources`

Multipart form data:
- `file` (pdf/png/jpg/txt)
- `source_type` (`pdf` | `image` | `text`)

Response:
```json
{
  "source_id": "src_456",
  "status": "uploaded"
}
```

## Start Processing
`POST /v1/jobs/{job_id}/start`

Response:
```json
{
  "job_id": "job_123",
  "status": "parsing"
}
```

## Get Job Status
`GET /v1/jobs/{job_id}`

Response:
```json
{
  "job_id": "job_123",
  "status": "chunking",
  "progress": 42,
  "current_step": "topic segmentation"
}
```

## Get Chunks
`GET /v1/jobs/{job_id}/chunks`

Response:
```json
{
  "job_id": "job_123",
  "status": "generating",
  "chunks": [
    {
      "chunk_id": "chk_001",
      "topic": "Antibiotics",
      "subtopic": "default",
      "token_estimate": 6123,
      "text": "..."
    }
  ]
}
```

## Get Card Preview
`GET /v1/jobs/{job_id}/preview`

Response:
```json
{
  "job_id": "job_123",
  "status": "done",
  "cards": [
    {
      "question": "...",
      "multiple_choice": ["..."],
      "correct_answers": ["..."],
      "extra": "Rationale: ..."
    }
  ],
  "validation": {
    "total": 100,
    "passed": 87,
    "failed": 13
  }
}
```


## Validation Report
`GET /v1/jobs/{job_id}/validation`

Response:
```json
{
  "job_id": "job_123",
  "summary": {
    "total": 100,
    "passed": 87,
    "failed": 13
  },
  "failed_cards": [
    {
      "reason": "true/false style options are forbidden",
      "card": {
        "question": "...",
        "multiple_choice": ["..."],
        "correct_answers": ["..."],
        "extra": "..."
      }
    }
  ]
}
```

## Request Export
`POST /v1/jobs/{job_id}/export`

Request:
```json
{
  "format": "csv"
}
```

Response:
```json
{
  "export_id": "exp_987",
  "job_id": "job_123",
  "format": "csv",
  "filename": "Pharmacology_101_job_123.csv",
  "status": "ready"
}
```

## Download Export
`GET /v1/exports/{export_id}/download`

Response:
```json
{
  "export_id": "exp_987",
  "filename": "Pharmacology_101_job_123.csv",
  "content_type": "text/csv",
  "content": "Question|Multiple Choice|Correct Answers|Extra"
}
```

# API Contract Examples (HTTP)

## Create Job
`POST /v1/jobs`

Request:
```json
{
  "course_name": "Pharmacology 101",
  "output_format": ["csv"]
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

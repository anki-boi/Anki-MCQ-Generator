# Backend API (MVP Scaffold)

## Run
```bash
cd backend_api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test
```bash
cd backend_api
source .venv/bin/activate
pytest
```


### Dependency-light unit tests
```bash
cd backend_api
python -m unittest discover -s tests_unit -q
```

## Implemented Endpoints
- `POST /v1/jobs`
- `POST /v1/jobs/{job_id}/sources`
- `POST /v1/jobs/{job_id}/start`
- `GET /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/chunks`
- `GET /v1/jobs/{job_id}/preview`
- `GET /v1/jobs/{job_id}/validation`
- `POST /v1/jobs/{job_id}/export`
- `GET /v1/exports/{export_id}/download`

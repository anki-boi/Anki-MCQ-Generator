from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile

from .pipeline import cards_to_pipe_csv, run_job
from .schemas import (
    ChunksResponse,
    CsvExportResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobPreviewResponse,
    JobStartResponse,
    JobStatus,
    JobStatusResponse,
    SourceType,
    SourceUploadResponse,
    ValidationSummary,
)
from .store import InMemoryStore

app = FastAPI(title="Anki MCQ Generator Backend", version="0.2.0")
store = InMemoryStore()


@app.post("/v1/jobs", response_model=JobCreateResponse)
def create_job(payload: JobCreateRequest) -> JobCreateResponse:
    job = store.create_job(course_name=payload.course_name, output_format=payload.output_format)
    return JobCreateResponse(job_id=job.job_id, status=job.status)


@app.post("/v1/jobs/{job_id}/sources", response_model=SourceUploadResponse)
async def upload_source(
    job_id: str,
    file: UploadFile = File(...),
    source_type: SourceType = Form(...),
) -> SourceUploadResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty file")

    try:
        raw_text = content.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = f"Binary source ({file.filename}) uploaded. OCR pipeline pending."

    source = store.add_source(job_id, source_type=source_type, filename=file.filename or "upload", raw_text=raw_text)
    return SourceUploadResponse(source_id=source.source_id, status="uploaded")


@app.post("/v1/jobs/{job_id}/start", response_model=JobStartResponse)
def start_job(job_id: str, background_tasks: BackgroundTasks) -> JobStartResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if not job.sources:
        raise HTTPException(status_code=400, detail="at least one source is required")

    if job.status not in {JobStatus.QUEUED, JobStatus.FAILED}:
        raise HTTPException(status_code=409, detail="job already started")

    background_tasks.add_task(run_job, store, job_id)
    return JobStartResponse(job_id=job_id, status=JobStatus.PARSING)


@app.get("/v1/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        current_step=job.current_step,
    )


@app.get("/v1/jobs/{job_id}/chunks", response_model=ChunksResponse)
def get_chunks(job_id: str) -> ChunksResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status not in {JobStatus.CHUNKING, JobStatus.GENERATING, JobStatus.DONE}:
        raise HTTPException(status_code=409, detail="chunks not ready")

    return ChunksResponse(job_id=job.job_id, status=job.status, chunks=job.chunks)


@app.get("/v1/jobs/{job_id}/preview", response_model=JobPreviewResponse)
def preview(job_id: str) -> JobPreviewResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=409, detail="job not complete")

    total = len(job.cards)
    return JobPreviewResponse(
        job_id=job.job_id,
        status=job.status,
        cards=job.cards,
        validation=ValidationSummary(total=total, passed=total, failed=0),
    )


@app.get("/v1/jobs/{job_id}/export/csv", response_model=CsvExportResponse)
def export_csv(job_id: str) -> CsvExportResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=409, detail="job not complete")

    return CsvExportResponse(
        job_id=job.job_id,
        status=job.status,
        filename=f"{job.course_name.replace(' ', '_')}_{job.job_id}.csv",
        content=cards_to_pipe_csv(job.cards),
    )

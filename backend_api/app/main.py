from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile

from .pipeline import cards_to_apkg_manifest, cards_to_pipe_csv, run_job
from .schemas import (
    ChunksResponse,
    ExportDownloadResponse,
    ExportRequest,
    ExportResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobPreviewResponse,
    JobStartResponse,
    JobStatus,
    JobStatusResponse,
    OutputFormat,
    SourceType,
    SourceUploadResponse,
    ValidationSummary,
)
from .store import InMemoryStore

app = FastAPI(title="Anki MCQ Generator Backend", version="0.3.0")
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


@app.post("/v1/jobs/{job_id}/export", response_model=ExportResponse)
def export_job(job_id: str, payload: ExportRequest) -> ExportResponse:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=409, detail="job not complete")

    safe_course_name = job.course_name.replace(" ", "_")

    if payload.format == OutputFormat.CSV:
        filename = f"{safe_course_name}_{job.job_id}.csv"
        content = cards_to_pipe_csv(job.cards)
        content_type = "text/csv"
    else:
        filename = f"{safe_course_name}_{job.job_id}.apkg"
        content = cards_to_apkg_manifest(job.cards, deck_name=f"{job.course_name}::Default")
        content_type = "application/octet-stream"

    export = store.create_export(
        job_id=job.job_id,
        export_format=payload.format,
        filename=filename,
        content_type=content_type,
        content=content,
    )
    return ExportResponse(
        export_id=export.export_id,
        job_id=export.job_id,
        format=export.export_format,
        filename=export.filename,
        status="ready",
    )


@app.get("/v1/exports/{export_id}/download", response_model=ExportDownloadResponse)
def download_export(export_id: str) -> ExportDownloadResponse:
    export = store.get_export(export_id)
    if not export:
        raise HTTPException(status_code=404, detail="export not found")

    return ExportDownloadResponse(
        export_id=export.export_id,
        filename=export.filename,
        content_type=export.content_type,
        content=export.content,
    )

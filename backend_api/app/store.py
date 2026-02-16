from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from .schemas import Card, Chunk, JobStatus, OutputFormat, SourceType


@dataclass
class SourceRecord:
    source_id: str
    source_type: SourceType
    filename: str
    raw_text: str


@dataclass
class ExportRecord:
    export_id: str
    job_id: str
    export_format: OutputFormat
    filename: str
    content_type: str
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class JobRecord:
    job_id: str
    course_name: str
    output_format: list[OutputFormat]
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0
    current_step: str = "queued"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sources: list[SourceRecord] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)
    cards: list[Card] = field(default_factory=list)


class InMemoryStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._exports: dict[str, ExportRecord] = {}
        self._lock = Lock()

    def create_job(self, course_name: str, output_format: list[OutputFormat]) -> JobRecord:
        job = JobRecord(job_id=f"job_{uuid4().hex[:10]}", course_name=course_name, output_format=output_format)
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def add_source(self, job_id: str, source_type: SourceType, filename: str, raw_text: str) -> SourceRecord:
        source = SourceRecord(
            source_id=f"src_{uuid4().hex[:10]}", source_type=source_type, filename=filename, raw_text=raw_text
        )
        with self._lock:
            self._jobs[job_id].sources.append(source)
        return source

    def update_progress(self, job_id: str, *, status: JobStatus, progress: int, current_step: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = status
            job.progress = progress
            job.current_step = current_step

    def set_chunks(self, job_id: str, chunks: list[Chunk]) -> None:
        with self._lock:
            self._jobs[job_id].chunks = chunks

    def set_cards(self, job_id: str, cards: list[Card]) -> None:
        with self._lock:
            self._jobs[job_id].cards = cards

    def mark_failed(self, job_id: str, reason: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = JobStatus.FAILED
            job.current_step = f"failed: {reason}"

    def create_export(
        self,
        *,
        job_id: str,
        export_format: OutputFormat,
        filename: str,
        content_type: str,
        content: str,
    ) -> ExportRecord:
        export = ExportRecord(
            export_id=f"exp_{uuid4().hex[:10]}",
            job_id=job_id,
            export_format=export_format,
            filename=filename,
            content_type=content_type,
            content=content,
        )
        with self._lock:
            self._exports[export.export_id] = export
        return export

    def get_export(self, export_id: str) -> ExportRecord | None:
        with self._lock:
            return self._exports.get(export_id)

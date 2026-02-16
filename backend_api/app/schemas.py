from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class JobStatus(str, Enum):
    QUEUED = "queued"
    PARSING = "parsing"
    CHUNKING = "chunking"
    GENERATING = "generating"
    DONE = "done"
    FAILED = "failed"


class OutputFormat(str, Enum):
    CSV = "csv"
    APKG = "apkg"


class SourceType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"


class JobCreateRequest(BaseModel):
    course_name: str = Field(min_length=1)
    output_format: list[OutputFormat] = Field(default_factory=lambda: [OutputFormat.CSV])


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class SourceUploadResponse(BaseModel):
    source_id: str
    status: Literal["uploaded"]


class JobStartResponse(BaseModel):
    job_id: str
    status: JobStatus


class Chunk(BaseModel):
    chunk_id: str
    topic: str
    subtopic: str
    token_estimate: int = Field(ge=1)
    text: str = Field(min_length=1)


class ChunksResponse(BaseModel):
    job_id: str
    status: JobStatus
    chunks: list[Chunk]


class Card(BaseModel):
    question: str
    multiple_choice: list[str] = Field(min_length=6)
    correct_answers: list[str] = Field(min_length=1)
    extra: str

    @model_validator(mode="after")
    def validate_option_count(self) -> "Card":
        if len(self.multiple_choice) <= len(self.correct_answers):
            raise ValueError("multiple_choice must be greater than correct_answers")
        return self


class ValidationSummary(BaseModel):
    total: int
    passed: int
    failed: int


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    current_step: str


class JobPreviewResponse(BaseModel):
    job_id: str
    status: JobStatus
    cards: list[Card]
    validation: ValidationSummary


class CsvExportResponse(BaseModel):
    job_id: str
    status: JobStatus
    filename: str
    content: str

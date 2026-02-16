from __future__ import annotations

import re
from uuid import uuid4

from .schemas import Card, Chunk, JobStatus, ValidationErrorItem, ValidationSummary
from .store import InMemoryStore
from .validation import validate_cards
from .text_utils import estimate_tokens, extract_topics


def build_chunks(sections: dict[str, list[str]], target_min_tokens: int = 5000, target_max_tokens: int = 10000) -> list[Chunk]:
    chunks: list[Chunk] = []
    for topic, lines in sections.items():
        if not lines:
            continue

        buffer: list[str] = []
        for line in lines:
            prospective = "\n".join(buffer + [line])
            if buffer and estimate_tokens(prospective) > target_max_tokens:
                text = "\n".join(buffer)
                chunks.append(
                    Chunk(
                        chunk_id=f"chk_{uuid4().hex[:10]}",
                        topic=topic,
                        subtopic="default",
                        token_estimate=estimate_tokens(text),
                        text=text,
                    )
                )
                buffer = [line]
            else:
                buffer.append(line)

        if buffer:
            text = "\n".join(buffer)
            chunks.append(
                Chunk(
                    chunk_id=f"chk_{uuid4().hex[:10]}",
                    topic=topic,
                    subtopic="default",
                    token_estimate=estimate_tokens(text),
                    text=text,
                )
            )

    merged: list[Chunk] = []
    for chunk in chunks:
        if merged and merged[-1].topic == chunk.topic and merged[-1].token_estimate < target_min_tokens:
            combined_text = f"{merged[-1].text}\n{chunk.text}".strip()
            merged[-1] = Chunk(
                chunk_id=f"chk_{uuid4().hex[:10]}",
                topic=chunk.topic,
                subtopic="default",
                token_estimate=estimate_tokens(combined_text),
                text=combined_text,
            )
        else:
            merged.append(chunk)

    return merged


def create_cards_from_chunk(chunk: Chunk) -> list[Card]:
    unique_terms: list[str] = []
    seen = set()

    for token in re.findall(r"\b[A-Za-z][A-Za-z0-9\-]{3,}\b", chunk.text):
        lowered = token.lower()
        if lowered not in seen:
            seen.add(lowered)
            unique_terms.append(token)
        if len(unique_terms) >= 8:
            break

    if not unique_terms:
        unique_terms = ["ConceptA", "ConceptB", "ConceptC", "ConceptD", "ConceptE", "ConceptF"]
    elif len(unique_terms) < 6:
        unique_terms.extend([f"Distractor{i}" for i in range(1, 7 - len(unique_terms))])

    correct = unique_terms[0]
    options = unique_terms[:6]

    card = Card(
        question=f"High-yield term associated with {chunk.topic}",
        multiple_choice=options,
        correct_answers=[correct],
        extra=(
            f"Rationale: {correct} appears prominently in the chunk for {chunk.topic}."
            f"<br><br>Source Anchor: {chunk.chunk_id}"
        ),
    )
    return [card]


def cards_to_pipe_csv(cards: list[Card]) -> str:
    rows: list[str] = []
    for card in cards:
        choices = "<br>".join(card.multiple_choice)
        answers = "<br>".join(card.correct_answers)
        row = f"{card.question}|{choices}|{answers}|{card.extra}"
        rows.append(row)
    return "\n".join(rows)


def cards_to_apkg_manifest(cards: list[Card], deck_name: str) -> str:
    """Placeholder .apkg payload representation until binary packaging is integrated."""
    lines = [f"DECK={deck_name}", "FORMAT=apkg-placeholder", f"CARDS={len(cards)}"]
    for idx, card in enumerate(cards, start=1):
        lines.append(f"CARD_{idx}_Q={card.question}")
        lines.append(f"CARD_{idx}_A={'<br>'.join(card.correct_answers)}")
    return "\n".join(lines)


def run_job(store: InMemoryStore, job_id: str) -> None:
    job = store.get_job(job_id)
    if job is None:
        return

    try:
        store.update_progress(job_id, status=JobStatus.PARSING, progress=20, current_step="parsing source text")
        merged_text = "\n".join(source.raw_text for source in job.sources)

        store.update_progress(job_id, status=JobStatus.CHUNKING, progress=45, current_step="topic segmentation")
        sections = extract_topics(merged_text)
        chunks = build_chunks(sections)
        store.set_chunks(job_id, chunks)

        store.update_progress(job_id, status=JobStatus.GENERATING, progress=75, current_step="card generation")
        raw_cards: list[Card] = []
        for chunk in chunks:
            raw_cards.extend(create_cards_from_chunk(chunk))

        passed_cards, issues = validate_cards(raw_cards)
        failed_cards = [ValidationErrorItem(reason=i.reason, card=i.card) for i in issues]
        summary = ValidationSummary(total=len(raw_cards), passed=len(passed_cards), failed=len(failed_cards))
        store.set_validated_cards(job_id, passed_cards, summary, failed_cards)

        store.update_progress(job_id, status=JobStatus.DONE, progress=100, current_step="completed")
    except Exception as exc:
        store.mark_failed(job_id, str(exc))

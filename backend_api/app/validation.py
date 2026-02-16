from __future__ import annotations

from dataclasses import dataclass

from .schemas import Card


FORBIDDEN_QUESTION_PREFIXES = ("what ", "which ", "where ", "how ", "why ")


@dataclass
class ValidationIssue:
    reason: str
    card: Card


def _is_true_false_style(card: Card) -> bool:
    lowered_options = {o.strip().lower() for o in card.multiple_choice}
    tf_sets = ({"true", "false"}, {"t", "f"}, {"yes", "no"})
    return any(tf.issubset(lowered_options) for tf in tf_sets)


def _has_forbidden_question_prefix(question: str) -> bool:
    return question.strip().lower().startswith(FORBIDDEN_QUESTION_PREFIXES)


def validate_cards(cards: list[Card]) -> tuple[list[Card], list[ValidationIssue]]:
    passed: list[Card] = []
    failed: list[ValidationIssue] = []

    for card in cards:
        if _is_true_false_style(card):
            failed.append(ValidationIssue(reason="true/false style options are forbidden", card=card))
            continue

        if _has_forbidden_question_prefix(card.question):
            failed.append(ValidationIssue(reason="question starts with forbidden interrogative", card=card))
            continue

        if len(card.multiple_choice) < 6:
            failed.append(ValidationIssue(reason="minimum of 6 choices required", card=card))
            continue

        if len(card.multiple_choice) <= len(card.correct_answers):
            failed.append(ValidationIssue(reason="choices must outnumber correct answers", card=card))
            continue

        passed.append(card)

    return passed, failed

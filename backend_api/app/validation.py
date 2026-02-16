from __future__ import annotations

from dataclasses import dataclass

from .quality_rules import (
    choices_outnumber_correct,
    has_forbidden_question_prefix,
    has_minimum_choices,
    is_true_false_options,
)
from .schemas import Card


@dataclass
class ValidationIssue:
    reason: str
    card: Card


def validate_cards(cards: list[Card]) -> tuple[list[Card], list[ValidationIssue]]:
    passed: list[Card] = []
    failed: list[ValidationIssue] = []

    for card in cards:
        if is_true_false_options(card.multiple_choice):
            failed.append(ValidationIssue(reason="true/false style options are forbidden", card=card))
            continue

        if has_forbidden_question_prefix(card.question):
            failed.append(ValidationIssue(reason="question starts with forbidden interrogative", card=card))
            continue

        if not has_minimum_choices(card.multiple_choice, minimum=6):
            failed.append(ValidationIssue(reason="minimum of 6 choices required", card=card))
            continue

        if not choices_outnumber_correct(card.multiple_choice, card.correct_answers):
            failed.append(ValidationIssue(reason="choices must outnumber correct answers", card=card))
            continue

        passed.append(card)

    return passed, failed

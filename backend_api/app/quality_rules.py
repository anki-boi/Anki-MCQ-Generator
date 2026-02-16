from __future__ import annotations

FORBIDDEN_QUESTION_PREFIXES = ("what ", "which ", "where ", "how ", "why ")


def is_true_false_options(options: list[str]) -> bool:
    lowered_options = {o.strip().lower() for o in options}
    tf_sets = ({"true", "false"}, {"t", "f"}, {"yes", "no"})
    return any(tf.issubset(lowered_options) for tf in tf_sets)


def has_forbidden_question_prefix(question: str) -> bool:
    return question.strip().lower().startswith(FORBIDDEN_QUESTION_PREFIXES)


def has_minimum_choices(options: list[str], minimum: int = 6) -> bool:
    return len(options) >= minimum


def choices_outnumber_correct(choices: list[str], correct_answers: list[str]) -> bool:
    return len(choices) > len(correct_answers)

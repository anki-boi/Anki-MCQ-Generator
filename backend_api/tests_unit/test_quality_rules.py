import unittest

from app.quality_rules import (
    choices_outnumber_correct,
    has_forbidden_question_prefix,
    has_minimum_choices,
    is_true_false_options,
)


class QualityRulesTests(unittest.TestCase):
    def test_true_false_detection(self) -> None:
        self.assertTrue(is_true_false_options(["True", "False", "Maybe"]))
        self.assertTrue(is_true_false_options(["Yes", "No", "Depends"]))
        self.assertFalse(is_true_false_options(["Penicillin", "Ibuprofen", "Aspirin"]))

    def test_forbidden_prefix_detection(self) -> None:
        self.assertTrue(has_forbidden_question_prefix("What is the mechanism?"))
        self.assertTrue(has_forbidden_question_prefix("which class includes beta-lactams"))
        self.assertFalse(has_forbidden_question_prefix("Mechanism associated with beta-lactams"))

    def test_choice_constraints(self) -> None:
        self.assertTrue(has_minimum_choices(["a", "b", "c", "d", "e", "f"]))
        self.assertFalse(has_minimum_choices(["a", "b", "c"]))
        self.assertTrue(choices_outnumber_correct(["a", "b", "c", "d", "e", "f"], ["a"]))
        self.assertFalse(choices_outnumber_correct(["a", "b"], ["a", "b"]))


if __name__ == "__main__":
    unittest.main()

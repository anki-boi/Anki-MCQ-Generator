import unittest

from app.text_utils import estimate_tokens, extract_topics


class TextUtilsTests(unittest.TestCase):
    def test_estimate_tokens(self) -> None:
        self.assertEqual(estimate_tokens("abcd"), 1)
        self.assertEqual(estimate_tokens("a" * 40), 10)

    def test_extract_topics_with_headings(self) -> None:
        text = "# Antibiotics\nPenicillin\nCephalosporins\n# Analgesics\nIbuprofen"
        topics = extract_topics(text)
        self.assertIn("Antibiotics", topics)
        self.assertIn("Analgesics", topics)
        self.assertEqual(topics["Antibiotics"], ["Penicillin", "Cephalosporins"])
        self.assertEqual(topics["Analgesics"], ["Ibuprofen"])

    def test_extract_topics_fallback(self) -> None:
        topics = extract_topics("Line one\nLine two")
        self.assertIn("General", topics)
        self.assertEqual(topics["General"], ["Line one", "Line two"])


if __name__ == "__main__":
    unittest.main()

import unittest

from build_case_study import clean_dataset, generate_raw_dataset, parse_float, parse_int


class CleaningTests(unittest.TestCase):
    def test_nonfinite_numbers_are_missing_not_pipeline_errors(self):
        for value in ["inf", "-inf", "NaN", "1e999", "-1", "", "bad"]:
            with self.subTest(value=value):
                self.assertIsNone(parse_float(value))
                self.assertEqual(parse_int(value), 0)
        self.assertEqual(parse_float("$ 1,234.50"), 1234.5)
        self.assertEqual(parse_int("2.5"), 2)

    def test_malformed_numeric_lead_can_be_cleaned_and_reported(self):
        raw = generate_raw_dataset()[0]
        raw.update(deal_value="inf", probability="inf", meeting_count="inf")
        row = clean_dataset([raw])[0]
        self.assertEqual(row["deal_value"], 0)
        self.assertEqual(row["expected_value"], 0)
        self.assertEqual(row["meeting_count"], 0)
        self.assertGreaterEqual(row["probability"], 0)
        self.assertLessEqual(row["probability"], 1)


if __name__ == "__main__":
    unittest.main()

import csv
import tempfile
import unittest
from pathlib import Path

from main import normalize_row, normalize_text, process_csv, validate_row


class NormalizationTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace(self):
        self.assertEqual(normalize_text("  USB-C   Cable \n"), "USB-C Cable")

    def test_normalize_row_uppercases_sku(self):
        self.assertEqual(normalize_row({"sku": " ab-12 ", "name": "  Mouse "})["sku"], "AB-12")
        self.assertEqual(normalize_row({"sku": " ab-12 ", "name": "  Mouse "})["name"], "Mouse")


class ValidationTests(unittest.TestCase):
    def test_invalid_price_is_reported(self):
        row = {"sku": "A-1", "name": "Mouse", "price": "free", "stock": "2"}
        self.assertIn("price", {issue.field for issue in validate_row(row, 2)})

    def test_negative_stock_is_reported(self):
        row = {"sku": "A-1", "name": "Mouse", "price": "10.00", "stock": "-1"}
        self.assertIn("stock", {issue.field for issue in validate_row(row, 2)})

    def test_missing_name_is_reported(self):
        row = {"sku": "A-1", "name": "", "price": "10.00", "stock": "2"}
        self.assertIn("name", {issue.field for issue in validate_row(row, 2)})


class CsvProcessingTests(unittest.TestCase):
    def test_duplicate_sku_is_reported_and_bad_rows_are_excluded(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            input_file = root / "products.csv"
            input_file.write_text(
                "sku,name,price,stock\nA-1,Mouse,10.00,2\na-1,Duplicate,11.00,3\nB-2,Hub,invalid,1\n",
                encoding="utf-8",
            )
            output_dir = root / "output"
            report = process_csv(input_file, output_dir)

            self.assertEqual(report["total_rows"], 3)
            self.assertEqual(report["valid_rows"], 1)
            self.assertEqual(report["invalid_rows"], 2)
            self.assertTrue((output_dir / "validation_report.json").exists())
            with (output_dir / "cleaned_products.csv").open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual([row["sku"] for row in rows], ["A-1"])
            self.assertIn("Duplicate SKU.", [issue["message"] for issue in report["issues"]])

    def test_missing_required_column_raises_error(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            input_file = root / "products.csv"
            input_file.write_text("sku,name\nA-1,Mouse\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                process_csv(input_file, root / "output")


if __name__ == "__main__":
    unittest.main()

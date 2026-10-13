"""Validate, normalize, and report on product inventory CSV files."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {"sku", "name", "price", "stock"}


@dataclass
class ValidationIssue:
    row: int
    sku: str
    field: str
    message: str


def normalize_text(value: str | None) -> str:
    """Trim leading/trailing whitespace and collapse repeated spaces."""
    return re.sub(r"\s+", " ", (value or "").strip())


def normalize_row(row: dict[str, str | None]) -> dict[str, str]:
    """Normalize text fields and convert SKU values to uppercase."""
    cleaned = {key: normalize_text(value) for key, value in row.items() if key is not None}
    cleaned["sku"] = cleaned.get("sku", "").upper()
    return cleaned


def validate_row(row: dict[str, str], row_number: int) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sku = row.get("sku", "")

    if not sku:
        issues.append(ValidationIssue(row_number, sku, "sku", "SKU is required."))
    if not row.get("name", ""):
        issues.append(ValidationIssue(row_number, sku, "name", "Product name is required."))

    try:
        price = Decimal(row.get("price", ""))
        if not price.is_finite() or price < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        issues.append(ValidationIssue(row_number, sku, "price", "Price must be a valid non-negative number."))

    stock_value = row.get("stock", "")
    try:
        stock = int(stock_value)
        if stock < 0 or str(stock) != stock_value:
            raise ValueError
    except ValueError:
        issues.append(ValidationIssue(row_number, sku, "stock", "Stock must be a non-negative whole number."))

    return issues


def process_csv(input_path: Path, output_dir: Path) -> dict[str, Any]:
    """Process a CSV and write cleaned records plus a JSON report."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = output_dir / "cleaned_products.csv"
    report_path = output_dir / "validation_report.json"

    with input_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - headers)
        if missing_columns:
            raise ValueError("CSV is missing required columns: " + ", ".join(missing_columns))

        valid_rows: list[dict[str, str]] = []
        issues: list[ValidationIssue] = []
        seen_skus: set[str] = set()
        total_rows = 0

        for row_number, raw_row in enumerate(reader, start=2):
            total_rows += 1
            row = normalize_row(raw_row)
            row_issues = validate_row(row, row_number)

            sku = row.get("sku", "")
            if sku and sku in seen_skus:
                row_issues.append(ValidationIssue(row_number, sku, "sku", "Duplicate SKU."))
            elif sku:
                seen_skus.add(sku)

            if row_issues:
                issues.extend(row_issues)
            else:
                valid_rows.append({column: row.get(column, "") for column in ("sku", "name", "price", "stock")})

    with cleaned_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["sku", "name", "price", "stock"])
        writer.writeheader()
        writer.writerows(valid_rows)

    report = {
        "input_file": input_path.name,
        "total_rows": total_rows,
        "valid_rows": len(valid_rows),
        "invalid_rows": total_rows - len(valid_rows),
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and clean product inventory CSV files.")
    parser.add_argument("input", type=Path, help="Path to the input CSV file")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directory for generated files (default: output)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = process_csv(args.input, args.output_dir)
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        return 1

    print(f"Processed {report['total_rows']} rows.")
    print(f"Valid rows: {report['valid_rows']}")
    print(f"Invalid rows: {report['invalid_rows']}")
    print(f"Validation issues: {report['issue_count']}")
    print(f"Output files saved to: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

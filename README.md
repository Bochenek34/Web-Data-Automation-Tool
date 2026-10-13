# Web Data Automation Toolkit

A small Python command-line tool that validates and cleans product inventory CSV files, then creates a machine-readable JSON report. It is designed as a portfolio project demonstrating practical data automation, input validation, error handling, and automated tests.

## Features

- Reads inventory data from CSV files.
- Normalizes whitespace and converts SKUs to uppercase.
- Validates required fields, prices, and stock quantities.
- Detects duplicate SKUs.
- Exports valid records to `cleaned_products.csv`.
- Writes a detailed `validation_report.json` with row numbers and validation issues.
- Includes automated tests using Python's built-in `unittest` framework.
- Uses only the Python standard library; no third-party dependencies are required.

## Requirements

- Python 3.10 or newer

## Run the tool

From the project root, run:

```bash
python main.py data/products.csv
```

Choose a different output directory with:

```bash
python main.py data/products.csv --output-dir results
```

The default output directory is `output/`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## CSV format

The input CSV must contain these columns:

| Column | Description | Example |
| --- | --- | --- |
| `sku` | Unique product identifier | `KB-200` |
| `name` | Product name | `Mechanical Keyboard` |
| `price` | Non-negative numeric price | `199.00` |
| `stock` | Non-negative whole-number quantity | `12` |

A sample file is available at `data/products.csv`. It deliberately includes a few incorrect rows so you can see the validator in action.

## Output

- `cleaned_products.csv` — normalized records that pass validation.
- `validation_report.json` — summary counts and a list of issues, including CSV row number, SKU, field, and explanation.

A row with any validation issue is excluded from the cleaned CSV. Duplicate SKU values are reported on the later occurrence.

## Project structure

```text
web-data-automation-toolkit/
├── data/
│   └── products.csv
├── output/
│   └── .gitkeep
├── tests/
│   └── test_main.py
├── .gitignore
├── LICENSE
├── main.py
└── README.md
```

## Skills demonstrated

- Python scripting and CLI argument parsing
- CSV and JSON processing
- Data normalization and validation
- Defensive error handling
- Automated unit tests
- Documentation and Git-ready project structure

## Possible next steps

- Add configurable validation rules.
- Export reports as HTML.
- Add structured logging.
- Expose the validator through a FastAPI endpoint.
- Add a PHP web interface for uploading a CSV and displaying the report.

## License

MIT — see [LICENSE](LICENSE).

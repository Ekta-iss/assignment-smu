# Task 2 – Decision Date Extraction from HTML

## Overview

This script processes HTML files stored in `inputFiles/` and extracts the **decision date** for each file. It writes the results to `output/decision_dates.csv` in the format:

```
filename,decision_date
example1.html,2000-03-11
example2.html,2019-07-23
...
```

The extraction logic is as follows:

1. Check for an explicit **“Decision Date”** field in HTML tables.
2. If not found, scan the **first 50 lines of the HTML text** and pick the **latest date** found.

---

## 1. Specific Methods and Techniques Used

### HTML Parsing

* **BeautifulSoup** is used to parse HTML files reliably.
* Table rows are scanned using `soup.find_all("tr")` for labeled fields like `Decision Date`.
* Text is extracted using `get_text(strip=True)` to normalize whitespace.

### Date Extraction

* **Regex patterns** match human-readable dates like `11 March 2000`.
* Multiple formats are supported: `DD-MM-YYYY`, `YYYY-MM-DD`, `DD/MM/YYYY`, and textual months.
* A **month map dictionary** converts month names to numeric values.

### Fallback Strategy

* If no explicit decision date is found, the script scans the **first 50 lines** of the HTML content to find candidate dates.
* The **latest date** among candidates is chosen as a conservative estimate.

### File Handling

* Input files: `*.html` or `*.htm` in `inputFiles/`
* Output CSV: `output/decision_dates.csv`
* Safe and robust I/O practices ensure minimal errors during reading/writing.

---

## 2. Handling Edge Cases and Unknown Unknowns

* **Missing Decision Date:** fallback to scanning first 50 lines.
* **Truncated or malformed HTML:** `errors="ignore"` when reading to skip invalid characters.
* **Non-standard date formats:** regex and multiple `strptime` patterns provide coverage.
* **Invalid date values:** `ValueError` is caught in `parse_human_date` and returns `None`.
* **No date found:** blank value (`""`) is written in the CSV.
* **Empty or missing input folder:** script prints a clear message and exits gracefully.

---

## 3. Testing and Accuracy Verification

* **Unit tests (manual/automatic):**

  * HTML files with explicit decision dates
  * HTML files with only dates in text
  * Files with invalid/malformed dates
* **Cross-verification:**

  * Compare extracted dates against known ground truth
  * Ensure CSV row count matches input files count
* **Sample runs:**

  ```bash
  python task2.py
  ```

  * Output CSV is checked for correct ISO date formatting (`YYYY-MM-DD`)
* Logging to console provides real-time verification for each file processed.

---

## 4. Code Quality and Best Practices

* **Variable names:** descriptive, e.g., `html_files`, `decision_date`, `MONTH_MAP`
* **Function decomposition:** small, single-responsibility functions:

  * `parse_human_date`
  * `extract_decision_date_field`
  * `extract_latest_date_first_lines`
  * `extract_decision_date_html`
* **Readability:** clear comments and docstrings explain logic
* **Robustness:** exception handling and fallbacks for unknown or malformed inputs
* **Reusability:** functions are independent and testable
* **Output consistency:** ISO 8601 date format ensures machine-readable output
* **Clean directory structure:** inputs in `inputFiles/`, outputs in `output/`

---

## 5. How to Run

```bash
mkdir inputFiles
# add your .html files to inputFiles/
python task2.py
# results in output/decision_dates.csv
```

---

## Notes

* Script uses **BeautifulSoup 4**: `pip install beautifulsoup4` if not already installed
* Designed for robustness and clarity: incomplete or malformed files do not break

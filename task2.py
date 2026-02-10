"""
task2.py - FINAL VERSION

Logic per HTML file:
1) Explicit "Decision Date" field → use it
2) Else → latest date in first 50 lines
Output: output/decision_dates.csv (filename,decision_date)
"""

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("pip install beautifulsoup4")
    exit(1)

INPUT_DIR = Path("inputFiles")
OUTPUT_DIR = Path("output")
OUTPUT_CSV = OUTPUT_DIR / "decision_dates.csv"

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12,
}

def parse_human_date(text: str) -> Optional[datetime]:
    text = text.strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    
    m = re.search(r'(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]{3,9})\.?,?\s+(?P<year>\d{4})', text, re.I)
    if not m:
        return None
    
    day, year = int(m.group("day")), int(m.group("year"))
    month_name = m.group("month").lower()
    month = MONTH_MAP.get(month_name)
    if not month:
        return None
    
    try:
        return datetime(year, month, day)
    except ValueError:
        return None

def extract_decision_date_field(soup: BeautifulSoup) -> Optional[datetime]:
    # Table row: |Decision Date|:|11 March 2000|
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).lower()
            if "decision date" in label:
                value = cells[-1].get_text(strip=True)
                d = parse_human_date(value)
                if d:
                    return d
    return None

def extract_latest_date_first_lines(soup: BeautifulSoup, max_lines=50) -> Optional[datetime]:
    text = soup.get_text("\n", strip=True)
    lines = text.splitlines()[:max_lines]
    
    candidates = []
    date_pattern = re.compile(r'\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b', re.I)
    
    for line in lines:
        for match in date_pattern.findall(line):
            d = parse_human_date(match)
            if d:
                candidates.append(d)
    
    return max(candidates) if candidates else None

def extract_decision_date_html(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    
    # 1) Explicit Decision Date
    d = extract_decision_date_field(soup)
    if d:
        return d.date().isoformat()
    
    # 2) Latest date in first 50 lines
    d = extract_latest_date_first_lines(soup)
    if d:
        return d.date().isoformat()
    
    return None

def main():
    rows = []
    
    print("Scanning inputFiles/...")
    if INPUT_DIR.exists():
        html_files = list(INPUT_DIR.glob("*.html")) + list(INPUT_DIR.glob("*.htm"))
        print(f"Found {len(html_files)} HTML files")
        
        for path in sorted(html_files):
            html = path.read_text(encoding="utf-8", errors="ignore")
            decision_date = extract_decision_date_html(html) or ""
            rows.append({"filename": path.name, "decision_date": decision_date})
            print(f"{path.name}: {decision_date}")
    else:
        print("No inputFiles/ folder found. Create it and add your .html files.")
    
    # Write CSV
    OUTPUT_DIR.mkdir(exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "decision_date"])
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\nDone! Check output/decision_dates.csv ({len(rows)} rows)")

if __name__ == "__main__":
    main()

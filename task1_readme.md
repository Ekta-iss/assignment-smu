# 📄 Fast eLitigation Judgment Scraper

A **high-performance, fault-tolerant web scraper** that downloads Singapore eLitigation judgments efficiently and reliably using parallel downloads and resilient networking techniques.

---

## 🚀 Features
- Parallel downloads (ThreadPoolExecutor)
- Retry + backoff
- Connection pooling
- Resume safe
- Deduplication
- Atomic writes
- Clean modular design

---

##  Project Structure
```bash
.
├── task1.py
├── judgments_html/
└── task1_readme.md
```

---

##  Installation Requirementse
```bash
.
    pip install requests beautifulsoup4 lxml
```

---

## ▶️ Usage
```bash
python task1.py
```

---

## Default configuration
- max_pages = 1040
- max_workers = 15
- delay = 0.2

---

## Test with smaller runs first
- scraper.scrape_all(max_pages=5)

---

## 🏗 Design
Hybrid approach:
- Listing pages → sequential
- Downloads → parallel

### Techniques
- requests.Session
- Retry strategy
- ThreadPoolExecutor
- BeautifulSoup
- Atomic file writes
- Deduplication

---

## ⚠ Edge Cases
- Network retries
- Timeouts
- Skip existing files
- Defensive parsing
- Thread safety
- Rate limiting

---

## 🧪 Testing
- Small runs first
- Validate file counts
- Manual sampling
- Logging

---

## 🧹 Code Quality
- Clear functions
- Descriptive names
- No magic numbers
- Idempotent design

---



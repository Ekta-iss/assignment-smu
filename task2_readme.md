# 📄 Decision Date Extraction from HTML

This script processes HTML files stored in inputFiles/ and extracts the decision date for each file. It writes the results to output/decision_dates.csv in the format:

```bash
filename,decision_date
example1.html,2000-03-11
example2.html,2019-07-23
```

---

## The extraction logic is as follows:

 1.Check for an explicit “Decision Date” field in HTML tables.

 2. If not found, scan the first 50 lines of the HTML text and pick the latest date found.

----
"""
Please refer to task1_readme.md for detailed code explanation, edge case handling, features, validation, clean code architecture, etc.
"""

import time
import logging
import requests
from pathlib import Path
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import re
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# =========================
# CONFIG
# =========================

BASE_URL = "https://www.elitigation.sg"
SAVE_DIR = Path("judgments_html")
SAVE_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 3
TIMEOUT = 20


# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =========================
# SCRAPER
# =========================

class FastEliteScraper:

    def __init__(self, delay=0.2, max_workers=15):
        """
        delay: delay between listing pages (politeness)
        max_workers: parallel downloads per page
        """

        self.delay = delay
        self.max_workers = max_workers

        self.session = self._create_session()

        self.downloaded = 0
        self.lock = Lock()  # thread-safe counter

        self.failed = []


    # ---------------------
    # Networking
    # ---------------------

    def _create_session(self):
        """
        Session with connection pooling + retry + backoff
        """
        session = requests.Session()

        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=50,
            pool_maxsize=50
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update({
            "User-Agent": "Academic-Research-Bot/3.0"
        })

        return session


    # ---------------------
    # Listing Page
    # ---------------------

    def fetch_listing_page(self, page_num):
        url = f"{BASE_URL}/gd/Home/Index?CurrentPage={page_num}"

        try:
            r = self.session.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text

        except requests.RequestException as e:
            logging.error(f"Listing page {page_num} failed: {e}")
            return None


    # ---------------------
    # Parse links
    # ---------------------

    def extract_judgments(self, html):
        """
        Extract and deduplicate judgment URLs
        """
        soup = BeautifulSoup(html, "html.parser")

        seen = set()
        results = []

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if "/gd/s/" not in href:
                continue

            m = re.search(r"/gd/s/([A-Za-z0-9_]+)", href)
            if not m:
                continue

            slug = m.group(1)

            if slug in seen:
                continue

            seen.add(slug)

            results.append((urljoin(BASE_URL, href), slug))

        return results


    # ---------------------
    # Download
    # ---------------------

    def download_single(self, item):
        """
        Download one file safely
        """
        url, slug = item
        filepath = SAVE_DIR / f"{slug}.html"

        if filepath.exists():
            return "exists"

        try:
            r = self.session.get(url, timeout=TIMEOUT)
            r.raise_for_status()

            # avoid saving empty responses
            if len(r.text) < 500:
                raise ValueError("Suspiciously small response")

            tmp = filepath.with_suffix(".tmp")

            tmp.write_text(r.text, encoding="utf-8")
            tmp.rename(filepath)  # atomic write

            with self.lock:
                self.downloaded += 1

            return "downloaded"

        except Exception as e:
            logging.error(f"Failed {slug}: {e}")
            self.failed.append(slug)
            return "failed"


    # ---------------------
    # Page processing
    # ---------------------

    def scrape_page_parallel(self, page_num):

        html = self.fetch_listing_page(page_num)
        if not html:
            return

        judgments = self.extract_judgments(html)

        logging.info(f"Page {page_num}: {len(judgments)} links")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            futures = [executor.submit(self.download_single, j) for j in judgments]

            for f in as_completed(futures):
                result = f.result()


    # ---------------------
    # Main
    # ---------------------

    def scrape_all(self, max_pages):

        logging.info(
            f"Start scraping {max_pages} pages | workers={self.max_workers}"
        )

        for page in range(1, max_pages + 1):

            self.scrape_page_parallel(page)

            if page % 10 == 0:
                logging.info(
                    f"Progress {page}/{max_pages} | downloaded={self.downloaded}"
                )

            time.sleep(self.delay)

        logging.info(f"Done. Total downloaded: {self.downloaded}")

        if self.failed:
            logging.warning(f"{len(self.failed)} failures")


# =========================
# RUN
# =========================

if __name__ == "__main__":

    scraper = FastEliteScraper(
        delay=0.3,
        max_workers=15
    )

    scraper.scrape_all(max_pages=1040)

"""
15 workers work in parallel to download judgements from each listing page
In Input, we give max pages in last line, I have set it to 1040 for full run
This is a 10x FASTER scraper using ThreadPoolExecutor
Downloads 10 judgments in parallel per listing page
"""

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://www.elitigation.sg"
SAVE_DIR = Path("judgments_html")
SAVE_DIR.mkdir(exist_ok=True)

class FastEliteScraper:
    def __init__(self, delay=0.2, max_workers=20):
        self.session = requests.Session()
        
        # Connection pooling + retries
        retry_strategy = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=50, pool_maxsize=50)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.delay = delay
        self.max_workers = max_workers
        self.downloaded = 0
        self.session.headers.update({
            "User-Agent": "Academic-Research-Bot/2.0 (Optimized)"
        })
    
    def fetch_listing_page(self, page_num):
        """Fetch ONE listing page (optimized)."""
        url = f"{BASE_URL}/gd/Home/Index?CurrentPage={page_num}"
        
        try:
            r = self.session.get(url, timeout=20)
            if r.status_code == 200:
                return r.text
        except:
            pass
        return None
    
    def extract_judgments(self, html):
        """Extract judgment URLs (cached parser)."""
        soup = BeautifulSoup(html, "html.parser")
        judgments = []
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/gd/s/" in href:
                match = re.search(r'/gd/s/([A-Za-z0-9_]+)', href)
                if match:
                    slug = match.group(1)
                    full_url = urljoin(BASE_URL, href)
                    judgments.append((full_url, slug))
        
        return judgments
    
    def download_single(self, args):
        """Download ONE judgment (thread-safe)."""
        url, slug = args
        filepath = SAVE_DIR / f"{slug}.html"
        
        if filepath.exists():
            return slug, True, "exists"
        
        try:
            r = self.session.get(url, timeout=15)
            if r.status_code == 200:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(r.text)
                return slug, True, "downloaded"
        except:
            pass
        
        return slug, False, "failed"
    
    def scrape_page_parallel(self, page_num):
        """Process ONE listing page with parallel judgment downloads."""
        print(f"Page {page_num}...")
        
        html = self.fetch_listing_page(page_num)
        if not html:
            print("  ❌ No HTML")
            return 0
        
        judgments = self.extract_judgments(html)
        print(f"  Found {len(judgments)} judgments")
        if not judgments:
            print("  ❌ No judgments found")
            return 0
        
        # PARALLEL DOWNLOAD (key part that was missing in debug)
        downloaded_count = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.download_single, judgment) for judgment in judgments]
            
            for future in as_completed(futures):
                slug, success, status = future.result()
                if success and status == "downloaded":
                    self.downloaded += 1
                    downloaded_count += 1
                    print(f"  ✓ {slug} ({self.downloaded})")
                elif status == "exists":
                    print(f"  ⏭️  {slug} (already exists)")
        
        print(f"  Page {page_num}: {downloaded_count} new downloads")
        return downloaded_count
    
    def scrape_all(self, max_pages=1040):
        """Main loop: listing pages are sequential, judgments are parallel."""
        print(f"🚀 FAST MODE: {max_pages} pages, {self.max_workers} parallel workers")
        
        for page_num in range(1, max_pages + 1):
            self.scrape_page_parallel(page_num)
            
            # Rate limit between listing pages only
            time.sleep(self.delay * 2)
            
            if page_num % 10 == 0:
                print(f"\n📊 Progress: Page {page_num}/{max_pages}, Total: {self.downloaded}\n")
        
        print(f"\n🎉 COMPLETE: {self.downloaded} judgments")

if __name__ == "__main__":
    scraper = FastEliteScraper(delay=0.2, max_workers=15)  # 15 parallel downloads
    scraper.scrape_all(max_pages=1040)  # Test first, then 1040

from typing import List, Optional
from app.models.job import Job
from app.scraping.base import BaseScraper

class SimplifyScraper(BaseScraper):
    def scrape_job(self, url: str) -> Optional[Job]:
        # TODO: Implement Simplify job details scraping
        print(f"Scraping Simplify URL: {url}")
        return None

    def search_jobs(self, query: str, location: str, limit: int = 10) -> List[Job]:
        # TODO: Implement Simplify search
        print(f"Searching Simplify for {query} in {location}")
        return []

from typing import List, Optional
from app.models.job import Job
from app.scraping.base import BaseScraper

class JobrightScraper(BaseScraper):
    def scrape_job(self, url: str) -> Optional[Job]:
        # TODO: Implement Jobright job details scraping
        print(f"Scraping Jobright URL: {url}")
        return None

    def search_jobs(self, query: str, location: str, limit: int = 10) -> List[Job]:
        # TODO: Implement Jobright search
        print(f"Searching Jobright for {query} in {location}")
        return []

from abc import ABC, abstractmethod
from typing import List, Optional
from playwright.sync_api import Playwright, Browser, Page
from app.models.job import Job

class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    Manages Playwright browser lifecycle and defines common interface.
    """
    
    def __init__(self, playwright: Playwright, headless: bool = True):
        self.playwright = playwright
        self.headless = headless
        self.browser: Optional[Browser] = None
        self._context = None

    def start_browser(self, **context_args):
        """Initializes the browser."""
        if not self.browser:
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self._context = self.browser.new_context(**context_args)

    def stop_browser(self):
        """Closes the browser."""
        if self.browser:
            self.browser.close()
            self.browser = None

    def get_page(self) -> Page:
        """Returns a new page in the current context."""
        if not self.browser:
            self.start_browser()
        return self._context.new_page()

    @abstractmethod
    def scrape_job(self, url: str) -> Optional[Job]:
        """
        Scrapes a single job posting URL.
        Returns None if scraping fails.
        """
        pass

    @abstractmethod
    @abstractmethod
    def search_jobs(self, query: str, location: str, limit: int = 10) -> tuple:
        """
        Searches for jobs matching criteria.
        Returns: (List[Job], str_total_count)
        """
        pass
        """
        Searches for jobs matching criteria.
        """
        pass

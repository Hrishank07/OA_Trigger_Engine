import pytest
from playwright.sync_api import Playwright
from app.scraping.linkedin import LinkedInScraper
from app.scraping.jobright import JobrightScraper
from app.scraping.simplify import SimplifyScraper

@pytest.fixture
def playwright_instance(playwright):
    """Fixture to provide Playwright instance"""
    return playwright

def test_linkedin_scraper_instantiation(playwright_instance):
    scraper = LinkedInScraper(playwright_instance)
    assert isinstance(scraper, LinkedInScraper)
    
    # Test browser start/stop (mocked or actual if playwright is installed)
    # This verifies the base class logic
    assert scraper.browser is None
    scraper.start_browser()
    assert scraper.browser is not None
    scraper.stop_browser()
    assert scraper.browser is None

def test_jobright_scraper_instantiation(playwright_instance):
    scraper = JobrightScraper(playwright_instance)
    assert isinstance(scraper, JobrightScraper)

def test_simplify_scraper_instantiation(playwright_instance):
    scraper = SimplifyScraper(playwright_instance)
    assert isinstance(scraper, SimplifyScraper)

def test_scraper_contract(playwright_instance):
    """Ensure all scrapers implement required methods"""
    scrapers = [
        LinkedInScraper(playwright_instance),
        JobrightScraper(playwright_instance),
        SimplifyScraper(playwright_instance)
    ]
    
    for scraper in scrapers:
        assert hasattr(scraper, "scrape_job")
        assert hasattr(scraper, "search_jobs")

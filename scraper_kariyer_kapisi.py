import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from database import save_job

URL = "https://www.kariyer.net/is-ilanlari/bilgisayar-yazilim-it"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _clean_text(element) -> str:
    if element is None:
        return ""
    text = element.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)


def scrape_kariyer_kapisi_jobs() -> int:
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        parsed_jobs = []
        seen_urls = set()

        # Kariyer.net job listings
        for job_item in soup.select(".list-view-item, .job-item, .position-item"):
            title_el = job_item.select_one(
                "h2, h3, .position-title, .job-title, a.position-link"
            )
            if title_el is None:
                continue

            company_el = job_item.select_one(".company-name, .company, .employer")
            location_el = job_item.select_one(".location, .city, .region, .position-location")
            link_el = job_item.select_one("a[href*='/is-ilanlari/']")

            if link_el is None or not link_el.get("href"):
                continue

            title = _clean_text(title_el)
            company = _clean_text(company_el) if company_el else "Belirtilmemiş"
            location = _clean_text(location_el) if location_el else "Uzaktan"
            url = urljoin("https://www.kariyer.net", link_el.get("href"))

            if not title or not url or url in seen_urls:
                continue

            seen_urls.add(url)
            parsed_jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "source": "kariyer.net",
                    "url": url,
                }
            )

        new_jobs = 0
        for job in parsed_jobs:
            saved = save_job(
                title=job["title"],
                company=job["company"],
                location=job["location"],
                source=job["source"],
                url=job["url"],
            )
            if saved:
                new_jobs += 1

        return new_jobs
    except Exception as e:
        print(f"Error scraping Kariyer.net: {e}")
        return 0

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from database import save_job

URL = "https://weworkremotely.com/categories/remote-back-end-programming-jobs"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _clean_text(element) -> str:
    if element is None:
        return ""
    text = element.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)


def scrape_jobs() -> int:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    parsed_jobs = []
    seen_urls = set()

    for card in soup.select("article, li, .job, .listing, .job-listing"):
        title_el = (
            card.select_one("h2, h3, h5, .title, .job-title, .listing-title")
            or card.select_one("a[href]")
        )
        if title_el is None:
            continue

        company_el = (
            card.select_one(".company, .company-name, .listing-company, .company-title")
            or card.select_one("span.company")
        )
        location_el = (
            card.select_one(".location, .listing-location, .job-location, .region")
            or card.select_one("span.location")
        )
        link_el = card.select_one("a[href]")
        if link_el is None:
            continue

        href = link_el.get("href", "")
        if not href:
            continue

        title = _clean_text(title_el)
        company = _clean_text(company_el) if company_el else "Unknown"
        location = _clean_text(location_el) if location_el else "Remote"
        url = urljoin(URL, href)

        if not title or not url or url in seen_urls:
            continue

        seen_urls.add(url)
        parsed_jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "source": "weworkremotely",
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

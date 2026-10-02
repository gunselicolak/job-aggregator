import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from database import save_job

URL = "https://remoteok.com/remote-backend-jobs"
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


def scrape_remote_ok_jobs() -> int:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    parsed_jobs = []
    seen_urls = set()

    for row in soup.select("tr[data-id]"):
        job_link = row.select_one("a[href*='/jobs/']")
        if job_link is None:
            continue

        href = job_link.get("href", "")
        if not href:
            continue

        title_el = row.select_one("h2, .job_title, td:nth-child(2)")
        company_el = row.select_one(".company_name, td:nth-child(3)")
        location_el = row.select_one(".location, td:nth-child(4), .region")

        title = _clean_text(title_el)
        company = _clean_text(company_el) if company_el else "Unknown"
        location = _clean_text(location_el) if location_el else "Remote"
        url = urljoin("https://remoteok.com", href)

        if not title or not url or url in seen_urls:
            continue

        seen_urls.add(url)
        parsed_jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "source": "remoteok",
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

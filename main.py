from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Query

from database import count_jobs, get_jobs, init_db
from scraper_weworkremotely import scrape_weworkremotely_jobs
from scraper_remote_ok import scrape_remote_ok_jobs
from scraper_youthall import scrape_youthall_jobs

app = FastAPI(
    title="Job Aggregator API",
    description="International and Turkish job/internship aggregator",
    version="1.2.0",
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/")
def read_root() -> dict:
    return {
        "message": "Job Aggregator API is running",
        "sources": ["weworkremotely", "remoteok", "youthall"],
        "status": "ok",
    }


@app.get("/jobs")
def list_jobs(
    query: Optional[str] = Query(default=None, description="Search by title, company, or location."),
    source: Optional[str] = Query(default=None, description="Filter by source: weworkremotely, remoteok, youthall"),
    skip: int = Query(default=0, ge=0, description="Offset for pagination"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of results to return"),
) -> dict:
    jobs = get_jobs(query=query, source=source, skip=skip, limit=limit)
    total = count_jobs(query=query, source=source)
    return {
        "jobs": jobs,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@app.post("/trigger-scrape")
def trigger_scrape(background_tasks: BackgroundTasks) -> dict:
    background_tasks.add_task(scrape_weworkremotely_jobs)
    background_tasks.add_task(scrape_remote_ok_jobs)
    background_tasks.add_task(scrape_youthall_jobs)

    return {
        "message": "Scrape started in the background for all configured sources",
        "status": "accepted",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

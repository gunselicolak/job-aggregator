from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Query

from database import get_jobs, init_db
from scraper import scrape_jobs

app = FastAPI(title="Job Aggregator API", version="1.0.0")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/")
def read_root() -> dict:
    return {"message": "Job Aggregator API is running"}


@app.get("/jobs")
def list_jobs(query: Optional[str] = Query(default=None, description="Search jobs by title, company, or location.")) -> dict:
    return {"jobs": get_jobs(query)}


@app.post("/trigger-scrape")
def trigger_scrape(background_tasks: BackgroundTasks) -> dict:
    background_tasks.add_task(scrape_jobs)
    return {"message": "Scrape started in the background", "status": "accepted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

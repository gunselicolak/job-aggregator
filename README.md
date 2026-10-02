# Job Aggregator

A FastAPI-based backend that aggregates backend developer jobs from WeWorkRemotely and stores them in a SQLite database.

## Features

- FastAPI REST API
- SQLite persistence with a `jobs.db` database
- Background job scraping via `BackgroundTasks`
- Searchable job listings by title, company, or location
- WeWorkRemotely backend job scraping using BeautifulSoup

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The app will automatically initialize the SQLite database on startup.

## API Endpoints

### GET /

Health check endpoint.

Example response:

```json
{
  "message": "Job Aggregator API is running"
}
```

### GET /jobs

Returns all jobs or filters by `query` string.

Query parameters:

- `query` (optional): search jobs by title, company, or location.

Example:

```bash
curl "http://localhost:8000/jobs?query=python"
```

### POST /trigger-scrape

Starts the scraper in the background and returns immediately.

Example:

```bash
curl -X POST http://localhost:8000/trigger-scrape
```

Example response:

```json
{
  "message": "Scrape started in the background",
  "status": "accepted"
}
```

## Notes

- The scraper targets backend developer jobs on WeWorkRemotely.
- Duplicate job URLs are ignored automatically.
- The database file is stored as `jobs.db` in the project root.

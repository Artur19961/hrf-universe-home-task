# Days-to-Hire Statistics Test task

This project provides an API and CLI tools to calculate and retrieve days-to-hire statistics based on job posting data stored in PostgreSQL.

---

## How to Run the Project with Docker

### 1. Build Docker images and start containers

```bash
docker-compose build
docker-compose up -d
```

### 2. Copy migration data into the PostgreSQL container

```bash
docker cp migrations/data/. hrf_universe_postgres:/tmp/data
```

### 3. Run Alembic migrations inside the API container

```bash
docker exec -it hrf_universe_api alembic upgrade head
```

### 4. Run the CLI command to compute and store statistics

```bash
docker exec -it hrf_universe_api poetry run python -m home_task.cli.stats stats store --min-required 5
```

### 5. Query the stored statistics using the API

Example of request:
```bash
curl -X GET "http://localhost:8000/stats/days-to-hire?standard_job_id=5affc1b4-1d9f-4dec-b404-876f3d9977a0&country_code=DE" \
  -H "accept: application/json"
```

Example JSON Response:
```json
{
  "standard_job_id": "5affc1b4-1d9f-4dec-b404-876f3d9977a0",
  "country_code": "DE",
  "min_days": 11.0,
  "avg_days": 50.5,
  "max_days": 80.9,
  "job_postings_count": 123
}
```
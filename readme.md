# Health Record Validator

![CI](https://github.com/YOUR_USERNAME/health-validator/actions/workflows/ci.yml/badge.svg)

A REST API for validating health record data quality — built to demonstrate a production-grade CI/CD pipeline on Azure.

Inspired by real data validation work done on Snowflake databases in a healthcare environment.

---

## What it does

- Validates individual or batched health records (patient ID, age, blood pressure, heart rate, date)
- Returns structured results: `is_valid`, `warnings`, and `errors`
- Catches common data quality issues: impossible BP readings, future dates, out-of-range vitals

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| POST | `/validate` | Validate a single record |
| POST | `/validate/batch` | Validate up to 100 records |

## Run locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/health-validator.git
cd health-validator

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload

# API docs available at:
# http://localhost:8000/docs
```

## Run with Docker

```bash
docker build -t health-validator .
docker run -p 8000:8000 health-validator
```

## Run tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

## CI/CD Pipeline

Every push to `main` or `dev` automatically:

1. Runs linting (ruff)
2. Runs 13 pytest tests with coverage report
3. Builds and smoke-tests the Docker image

Deployments to Azure Container Apps trigger on merge to `main` (see Week 3).

## Tech stack

- **API**: FastAPI + Pydantic v2
- **Testing**: pytest + httpx
- **Container**: Docker (python:3.11-slim, non-root user)
- **CI/CD**: GitHub Actions
- **Cloud**: Azure Container Registry + Azure Container Apps

## Project structure

```
health-validator/
├── app/
│   └── main.py          # FastAPI application
├── tests/
│   └── test_main.py     # 13 pytest tests
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions pipeline
├── Dockerfile
├── requirements.txt
└── README.md
```
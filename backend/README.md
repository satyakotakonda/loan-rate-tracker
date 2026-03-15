# Backend — Loan Rate Tracker API

A Python FastAPI backend that acts as an agent to collect, aggregate, and display Personal Loan and Home Loan interest rates from major Indian banks.

## Features

- Fetches loan rates from 8 major Indian banks (SBI, HDFC, ICICI, Axis, PNB, Kotak, Bank of Baroda, Canara Bank)
- RBI benchmark rate service (Repo Rate, Reverse Repo Rate, Bank Rate, MCLR)
- TTL-based in-memory caching to avoid repeated requests
- Graceful fallback to realistic default rates if scraping fails
- EMI calculator endpoint
- Interactive API docs at `/docs`

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/rates` | All rates (filterable) |
| GET | `/api/v1/rates/personal-loan` | Personal loan rates |
| GET | `/api/v1/rates/home-loan` | Home loan rates |
| GET | `/api/v1/rates/best` | Best rates per type |
| GET | `/api/v1/rates/bank/{bank_name}` | Rates for a specific bank |
| GET | `/api/v1/rbi/benchmark` | RBI benchmark rates |
| POST | `/api/v1/calculator/emi` | Calculate EMI |
| POST | `/api/v1/rates/refresh` | Force refresh cache |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_TTL` | `1800` | Cache TTL in seconds (30 min) |
| `CACHE_MAXSIZE` | `100` | Max cache entries |
| `REQUEST_TIMEOUT` | `10` | HTTP request timeout in seconds |
| `DEBUG` | `false` | Enable debug logging |

# 🏦 Loan Rate Tracker

> An agent that collects, aggregates, and displays **Personal Loan** and **Home Loan** interest rates from major **Indian banks** — built with **Python (FastAPI)** + **React.js**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📋 Features

- 🔄 **Live rate fetching** from 8 major Indian banks with graceful fallback
- 📊 **RBI benchmark rates** (Repo Rate, Reverse Repo Rate, Bank Rate, MCLR)
- 💼 **Personal Loan** & 🏠 **Home Loan** rate comparison
- 🧮 **EMI Calculator** with pie chart breakdown
- 📈 **Interactive charts** (bar chart comparison)
- 📋 **Sortable & filterable** comparison table
- ⚡ **TTL caching** (30 minutes) to avoid repeated scraping
- 🐳 **Docker support** for one-command deployment

---

## 🏗️ Architecture

```
loan-rate-tracker/
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Configuration settings
│   │   ├── models/
│   │   │   └── loan_rate.py  # Pydantic models
│   │   ├── scrapers/         # Bank-specific scrapers
│   │   │   ├── base_scraper.py
│   │   │   ├── sbi_scraper.py
│   │   │   ├── hdfc_scraper.py
│   │   │   ├── icici_scraper.py
│   │   │   ├── axis_scraper.py
│   │   │   ├── pnb_scraper.py
│   │   │   ├── kotak_scraper.py
│   │   │   ├── bob_scraper.py
│   │   │   └── canara_scraper.py
│   │   ├── services/
│   │   │   ├── rate_aggregator.py  # Aggregates + caches rates
│   │   │   └── rbi_service.py      # RBI benchmark data
│   │   ├── api/
│   │   │   └── routes.py           # REST API endpoints
│   │   └── utils/
│   │       └── helpers.py          # EMI formula, formatters
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React.js frontend
│   ├── src/
│   │   ├── App.js
│   │   ├── components/       # UI components
│   │   ├── services/api.js   # Axios API layer
│   │   ├── hooks/            # useLoanRates custom hook
│   │   └── utils/formatters.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🏦 Banks Covered

| Bank | Personal Loan | Home Loan |
|------|:---:|:---:|
| State Bank of India (SBI) | ✅ | ✅ |
| HDFC Bank | ✅ | ✅ |
| ICICI Bank | ✅ | ✅ |
| Axis Bank | ✅ | ✅ |
| Punjab National Bank (PNB) | ✅ | ✅ |
| Kotak Mahindra Bank | ✅ | ✅ |
| Bank of Baroda | ✅ | ✅ |
| Canara Bank | ✅ | ✅ |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/satyakotakonda/loan-rate-tracker.git
cd loan-rate-tracker
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/rates` | All rates (filterable by `loan_type`, `bank_name`, `sort_by`, `order`) |
| `GET` | `/api/v1/rates/personal-loan` | Personal loan rates (sorted by lowest) |
| `GET` | `/api/v1/rates/home-loan` | Home loan rates (sorted by lowest) |
| `GET` | `/api/v1/rates/best` | Best rates for each loan type |
| `GET` | `/api/v1/rates/bank/{bank_name}` | Rates for a specific bank |
| `GET` | `/api/v1/rbi/benchmark` | RBI benchmark rates |
| `POST` | `/api/v1/calculator/emi` | Calculate EMI |
| `POST` | `/api/v1/rates/refresh` | Force refresh cached rates |

**EMI Calculator payload:**
```json
{
  "principal": 1000000,
  "rate": 8.50,
  "tenure": 240
}
```

Interactive API docs: http://localhost:8000/docs

---

## ⚙️ Configuration

**Backend** (environment variables):

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_TTL` | `1800` | Cache TTL in seconds (30 min) |
| `CACHE_MAXSIZE` | `100` | Max cache entries |
| `REQUEST_TIMEOUT` | `10` | HTTP request timeout (seconds) |
| `DEBUG` | `false` | Enable debug logging |

**Frontend** (environment variables):

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `/api/v1` | Backend API base URL |

---

## 🔄 Scheduled Rate Refresh (Cron)

To refresh rates periodically (e.g., every hour), add a cron job:

```bash
# Refresh rates every hour
0 * * * * curl -X POST http://localhost:8000/api/v1/rates/refresh
```

Or use a scheduler like APScheduler in the backend for automated refreshes.

---

## 🛡️ Data & Disclaimer

- Rates are sourced from publicly available bank websites and RBI publications
- Fallback data reflects realistic rates as of early 2026
- Rates are indicative and may change. Always verify with your bank before applying
- This tool is for informational purposes only

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Data Fetching | httpx, BeautifulSoup4 |
| Caching | cachetools (TTLCache) |
| Frontend | React 18, Recharts, Axios |
| Containerization | Docker, Docker Compose, Nginx |
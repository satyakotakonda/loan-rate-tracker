# Frontend — Loan Rate Tracker UI

A React.js frontend for visualizing and comparing loan rates from major Indian banks.

## Features

- 📊 Real-time rate comparison dashboard
- 🃏 Rate cards with color-coded indicators (best/average/high)
- 📋 Sortable and filterable comparison table
- 📈 Bar chart for visual rate comparison
- 🧮 EMI calculator with pie chart breakdown
- 📊 RBI benchmark rates section
- 📱 Fully responsive design

## Running Locally

```bash
npm install
npm start
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The app proxies API requests to `http://localhost:8000` (see `package.json` proxy setting).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `/api/v1` | Backend API base URL |

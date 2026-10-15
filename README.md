# Social Media Privacy Risk Assessment Framework

A defensive, educational privacy-awareness application. It evaluates **self-reported privacy settings** and synthetic demo responses. It does not scrape social media, access accounts, track people, or require actual phone numbers, addresses, birthdays, passwords, or private messages.

## Features
- 40+ self-assessment questions across 10 categories
- Explainable category risk scores and overall score (0–100; higher = more assessed exposure)
- Findings and personalized recommendations
- Privacy improvement simulator
- Synthetic dataset generator (1,000 fictional records)
- React/Vite dashboard with category bar chart
- FastAPI backend and automated tests
- Printable report from the browser

## Educational risk bands
- 0–20: LOW
- 21–40: MODERATE
- 41–70: HIGH
- 71–100: CRITICAL

These weights and thresholds are educational assumptions, not a validated prediction of compromise.

## Stack
- Frontend: React + Vite
- Backend: Python + FastAPI
- Data: synthetic CSV generator; assessment processing is in-memory by default
- Tests: pytest

## Requirements
Python 3.10+ and Node.js 18+.

## Run on Windows (PowerShell)
### 1. Backend
Open a terminal in the project root:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python data\generate_dataset.py
python -m uvicorn backend.main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

### 2. Frontend
Open a second terminal in the project root:
```powershell
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite (usually http://localhost:5173).

## Test
In the activated backend environment:
```powershell
python -m pytest -q
```

## Safety and privacy
- Only self-reported answers or fictional demo data are assessed.
- Do not upload real social-media exports or images in this starter.
- No scraping, tracking, account enumeration, or bypassing privacy controls.
- Scores are explainable coaching signals, not guarantees of safety.
- The current starter does not persist personal assessment answers.

## Project structure
- `backend/main.py`: API, questionnaire, scoring, findings, recommendations, simulator
- `data/generate_dataset.py`: synthetic 1,000-row CSV generator
- `frontend/src/App.jsx`: questionnaire and dashboard
- `frontend/src/App.css`: responsive styling
- `tests/test_api.py`: API and scoring tests
- `docs/`: architecture and threat-model notes

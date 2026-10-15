# Architecture

```text
User
  |
  v
React questionnaire (self-reported answers only)
  |
  v
FastAPI input validation
  |
  v
Feature mapping / category aggregation
  |
  v
Weighted risk scoring (0–100)
  |
  +--> Findings and recommendations
  |
  +--> Improvement simulation
  |
  v
React dashboard, chart, and downloadable JSON report
```

## Design choices
- No scraping, account enumeration, or platform login.
- No sensitive values are requested. Inputs describe whether a setting exposes information.
- Assessment processing is in-memory; this starter does not save individual answers to a database.
- Synthetic CSV records are generated separately for demonstration/analytics exercises.
- CORS is restricted to local development origins.
- Risk scoring is explainable and rule-based; weights are illustrative and require validation before professional use.

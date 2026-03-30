# Prostate Cancer Risk, Trends & Disparities Dashboard
**Ava McClinton | Data Science Capstone | Spring 2026**

An interactive Flask + Plotly dashboard exploring population-level prostate cancer statistics.

## Quick Start

```bash
pip install -r requirements.txt
python run.py
# Open http://127.0.0.1:5000
```

## Capstone Requirements Satisfied

| Requirement | Implementation |
|---|---|
| Web Scraping | requests + BeautifulSoup4 targeting ACS, SEER, PMC, USPSTF |
| Data Mining | SEER API + CDC WONDER API; trend detection; disparity analysis |
| Data Visualization | 8 interactive Plotly charts (line, bar, choropleth, area, scatter) |
| Data Interaction | Flask API routes + JS: stage filter, race selector, metric toggle, risk panel |
| Useful Insights | "Your Risk" panel + callout boxes tailored to adults aged 50-65 |

## Deployment
Push to GitHub, deploy on Render.com with start command: `gunicorn src.app.app:app`

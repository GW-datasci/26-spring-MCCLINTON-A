# Capstone Project Plan
## Exploring Prostate Cancer Risk, Trends, and Disparities Through an Interactive Data Dashboard
**Ava McClinton | Spring 2026**

---

## Overview

This plan outlines the full architecture, data strategy, technical approach, and timeline for building an interactive Flask + Plotly dashboard on prostate cancer statistics. The project satisfies five capstone requirements: **web scraping**, **data mining**, **data visualization**, **data interaction**, and **useful insights for a target audience of adults aged 50–65**.

---

## 1. Capstone Requirements — How Each Is Satisfied

| Requirement | How It's Met |
|---|---|
| **Web Scraping** | Scrape ACS key statistics page, PMC/PubMed article tables, and USPSTF guideline timeline pages using `requests` + `BeautifulSoup` |
| **Data Mining** | Query SEER API and CDC WONDER API programmatically; extract structured tables from research PDFs; detect trends via time-series analysis |
| **Data Visualization** | 6–8 interactive Plotly charts: line trends, grouped bar charts, choropleth map, sunburst/donut for stage breakdown, survival curves |
| **Data Interaction** | Flask-powered filters: year range slider, race/ethnicity selector, geographic region dropdown, stage toggle, age group filter |
| **Useful Insights (age 50–65)** | Personalized risk framing, plain-language explanations, "What does this mean for me?" callout boxes on every chart |

---

## 2. Data Sources

### 2a. API Access (Programmatic — No Scraping Needed)

| Source | What It Provides | Access Method |
|---|---|---|
| **SEER API** (`api.seer.cancer.gov`) | Incidence, mortality, survival rates by year, age, race, stage | Free API key registration |
| **CDC WONDER API** (`wonder.cdc.gov`) | Cancer incidence/mortality by state and region; XML format | HTTP POST requests (no key needed) |
| **NCI SEER*Explorer** | Downloadable CSV tables for prostate cancer | Direct CSV download |

### 2b. Web Scraping Targets

| Source | What to Scrape | Method |
|---|---|---|
| **American Cancer Society** (`cancer.org/cancer/types/prostate-cancer/about/key-statistics.html`) | New case estimates, death estimates, lifetime risk, 2025 projections | `BeautifulSoup` HTML table parsing |
| **SEER Cancer Stat Facts** (`seer.cancer.gov/statfacts/html/prost.html`) | Survival by stage, age distribution at diagnosis | `BeautifulSoup` + `pandas` |
| **PMC Article — Kratzer et al. 2025** (`pmc.ncbi.nlm.nih.gov/articles/PMC12593258/`) | Trend data tables from the 2025 statistics update | `BeautifulSoup` table extraction |
| **PMC Article — Incidence Trends 2000–2020** (`ncbi.nlm.nih.gov/pmc/articles/PMC10720073`) | Race/ethnicity × stage × year trend tables | `BeautifulSoup` table extraction |
| **USPSTF Guidelines** (`uspreventiveservicestaskforce.org`) | Screening recommendation dates (2012, 2018) for timeline markers | `requests` + date parsing |

### 2c. Direct Download / Static Sources

| Source | Format | Use |
|---|---|---|
| CDC U.S. Cancer Statistics public use data | CSV | Race/ethnicity incidence rates, state-level data |
| SEER Research Limited-Field Data (2000–2021) | Requires data-use agreement — apply early | Detailed individual-level patterns |
| Siegel et al., Cancer Statistics 2024 | PDF table extraction via `pdfplumber` | Overall cancer burden context |

---

## 3. Tech Stack

```
Backend:       Python 3.11, Flask
Data Layer:    pandas, SQLite (via sqlite3 or SQLAlchemy)
Scraping:      requests, BeautifulSoup4, pdfplumber
Visualization: Plotly (plotly.express + plotly.graph_objects)
Frontend:      Flask + Jinja2 templates, Bootstrap 5, Plotly.js
Deployment:    Render (free tier) — connects to GitHub repo
Version Ctrl:  Git + GitHub (required for capstone reproducibility)
```

---

## 4. Dashboard Features & Visualizations

### Chart 1 — Incidence & Mortality Trends Over Time (Line Chart)
- X-axis: Year (2000–2022), Y-axis: Rate per 100,000
- Two lines: incidence rate vs. mortality rate
- **Vertical markers** at 2012 (USPSTF discourages PSA screening) and 2018 (USPSTF revises to shared decision-making)
- Interactive: hover tooltips with year-specific values; annotation explains the policy context
- **Insight for 50–65 audience:** "Incidence dropped after 2012 when routine PSA screening was discouraged, but late-stage diagnoses started rising — here's what that means for men your age."

### Chart 2 — Racial & Ethnic Disparities (Grouped Bar Chart)
- Groups: Non-Hispanic White, Non-Hispanic Black, Hispanic, Asian/PI, AIAN
- Metrics toggle: incidence rate / mortality rate / 5-year survival
- **Insight:** Black men face 2× higher mortality than any other group; highlights why the 50–65 window is particularly critical for Black men to discuss screening with their doctor.

### Chart 3 — Geographic Heatmap (Choropleth — U.S. States)
- Color scale: age-adjusted incidence or mortality rate by state
- Dropdown to toggle between incidence and mortality
- Hover shows state name, rate, national average comparison
- **Insight:** Geographic variation reveals where late-stage detection is most common.

### Chart 4 — Stage at Diagnosis Over Time (Stacked Area / Animated Bar)
- Stages: Localized, Regional, Distant, Unknown
- Animates year-by-year to show shift toward distant-stage diagnoses post-2012
- **Insight:** "Distant-stage prostate cancer has a 38% 5-year survival rate vs. nearly 100% for localized — this chart shows why when you get screened matters."

### Chart 5 — Survival Rates by Stage (Horizontal Bar or Funnel)
- 5-year relative survival: Localized (~99%), Regional (~100%), Distant (~38%)
- Plain-language labels designed for a non-medical audience
- Callout box: "If caught early, prostate cancer is one of the most survivable cancers."

### Chart 6 — Age Distribution at Diagnosis (Histogram)
- Distribution of diagnoses by age group
- Shaded band highlighting the 50–65 range
- **Insight:** Most diagnoses occur between 55–74; 50–65 is the window where screening conversations matter most.

### Chart 7 — Race × Stage Breakdown (Sunburst / Treemap)
- Outer ring: race/ethnicity; inner ring: stage at diagnosis
- Shows that Black men are disproportionately diagnosed at distant stage
- Interactive: click to drill down

### Chart 8 — "Am I at Risk?" Risk Context Panel
- Not a predictive model, but a **data-driven summary** personalized to the user's selected age group and race/ethnicity
- Pulls from pre-loaded statistics to display: lifetime risk estimate, median age at diagnosis, recommended screening conversation age
- Framed clearly as general population statistics, not individual predictions
- **Designed specifically for the 50–65 audience**

---

## 5. Project File Structure

```
26-spring-MCCLINTON-A/
├── data/
│   ├── raw/              ← scraped + downloaded data (CSV, JSON, XML)
│   ├── cleaned/          ← processed, analysis-ready datasets
│   └── sampledata/       ← subset for demo/testing
├── demo/
│   ├── dashboard.html    ← static export / demo screenshot
│   └── fig/
├── poster/
├── presentation/
├── proposal/
├── report/
└── src/                  ← NEW: all source code
    ├── scraping/
    │   ├── scrape_acs.py
    │   ├── scrape_seer_statfacts.py
    │   ├── scrape_pmc.py
    │   └── scrape_uspstf.py
    ├── pipeline/
    │   ├── fetch_seer_api.py
    │   ├── fetch_cdc_wonder.py
    │   ├── clean.py
    │   └── load_db.py
    ├── analysis/
    │   ├── trend_analysis.py
    │   └── disparity_analysis.py
    ├── viz/
    │   ├── charts.py       ← all Plotly figure builders
    │   └── layout.py
    ├── app/
    │   ├── app.py          ← Flask app entry point
    │   ├── routes.py
    │   └── templates/
    │       ├── index.html
    │       ├── base.html
    │       └── components/
    └── requirements.txt
```

---

## 6. Data Pipeline Flow

```
[Web Scraping]          [API Calls]            [CSV Downloads]
ACS, SEER StatFacts,    SEER API,              CDC USCS Public Data,
PMC Articles,           CDC WONDER API         SEER CSR tables
USPSTF pages
        |                    |                       |
        └────────────────────┼───────────────────────┘
                             ▼
                    [raw data/ folder]
                    CSV, JSON, XML files
                             |
                             ▼
                    [clean.py + load_db.py]
                    Standardize, merge, validate
                    → SQLite database (prostate.db)
                             |
                             ▼
                    [analysis/ scripts]
                    Trend detection, disparity metrics
                    → analysis summary tables
                             |
                             ▼
                    [viz/charts.py]
                    Plotly figures built from DB queries
                             |
                             ▼
                    [Flask app + Jinja2 templates]
                    Interactive dashboard with filters
                             |
                             ▼
                    [Render.com deployment]
                    Public URL → submit for capstone
```

---

## 7. Timeline (8 Weeks)

### Phase 1 — Data Collection (Weeks 1–2)
- [ ] Register for SEER API key
- [ ] Submit SEER data-use agreement (if needed for detailed files)
- [ ] Write and run all scraping scripts (`scrape_acs.py`, `scrape_seer_statfacts.py`, `scrape_pmc.py`, `scrape_uspstf.py`)
- [ ] Pull data from SEER API and CDC WONDER API
- [ ] Download CDC USCS public CSV files
- [ ] Store everything in `data/raw/`

### Phase 2 — Data Cleaning & Mining (Weeks 3–4)
- [ ] Standardize column names, date formats, rate units across all sources
- [ ] Merge into unified SQLite database
- [ ] Run trend analysis (APC — Annual Percent Change calculations)
- [ ] Run disparity analysis (race × stage × mortality rate comparisons)
- [ ] Document all data limitations (suppressed counts, reporting delays, classification changes)
- [ ] Store cleaned outputs in `data/cleaned/`

### Phase 3 — Dashboard Development (Weeks 5–6)
- [ ] Build all 8 Plotly charts in `viz/charts.py`
- [ ] Build Flask routes and templates
- [ ] Implement interactive filters (year range, race, region, stage, age)
- [ ] Add contextual annotation text and "Insight for 50–65" callout boxes
- [ ] Write ethical disclaimers and data limitation notes in the UI

### Phase 4 — Refinement & Deployment (Weeks 7–8)
- [ ] User test with at least 2–3 people outside of data science
- [ ] Refine language for the 50–65 lay audience
- [ ] Push to GitHub with full README and reproducibility instructions
- [ ] Deploy to Render.com
- [ ] Finalize report, presentation, and poster materials

---

## 8. Key Sources

- [SEER Cancer Stat Facts: Prostate Cancer](https://seer.cancer.gov/statfacts/html/prost.html)
- [SEER API](https://api.seer.cancer.gov/)
- [CDC U.S. Cancer Statistics — Prostate Cancer Incidence](https://www.cdc.gov/united-states-cancer-statistics/publications/prostate-cancer.html)
- [CDC WONDER API](https://wonder.cdc.gov/wonder/help/wonder-api.html)
- [ACS Key Statistics for Prostate Cancer](https://www.cancer.org/cancer/types/prostate-cancer/about/key-statistics.html)
- [Kratzer et al., Prostate Cancer Statistics 2025 — CA: A Cancer Journal for Clinicians](https://acsjournals.onlinelibrary.wiley.com/doi/full/10.3322/caac.70028)
- [Kratzer et al., PMC Open Access Version](https://pmc.ncbi.nlm.nih.gov/articles/PMC12593258/)
- [Incidence Trends by Race/Ethnicity 2000–2020 — PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10720073)
- [USPSTF Prostate Cancer Screening Guidelines (2018)](https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/prostate-cancer-screening)
- [ACS 2025 Prostate Cancer Report Press Release](https://pressroom.cancer.org/2025-Prostate-Cancer-Report)

---

## 9. Ethical Considerations

- **No individual-level predictions:** All statistics are population-level. The "Am I at risk?" panel will be clearly framed as general population context, not diagnostic.
- **Racial disparities framing:** Disparities are presented as structural/systemic patterns, not biological determinism. Contextual text will explain the role of access to care, screening history, and socioeconomic factors.
- **Screening nuance:** The dashboard will present both sides of the screening debate (overdiagnosis vs. late-stage risk) transparently, consistent with USPSTF's shared decision-making recommendation.
- **Data suppression transparency:** Small counts suppressed by CDC/SEER will be labeled as such with explanatory tooltips.
- **Observational data caution:** All trend analysis will include a disclaimer that correlation with screening policy changes does not imply causation.

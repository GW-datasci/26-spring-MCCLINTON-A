"""
scrape_seer.py
Scrapes prostate cancer statistics from SEER Cancer Stat Facts page.
Source: https://seer.cancer.gov/statfacts/html/prost.html
Extracts: survival rates by stage, age distribution, incidence/mortality rates.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import re

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../../data/raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

URL = "https://seer.cancer.gov/statfacts/html/prost.html"


def scrape_seer_statfacts():
    print(f"[SEER] Fetching: {URL}")
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        stats = {}
        text = soup.get_text(separator=" ", strip=True)

        # Extract tables
        tables = []
        for tbl in soup.find_all("table"):
            rows = []
            for tr in tbl.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)

        stats["tables_raw"] = tables[:10]
        stats["page_text_sample"] = text[:3000]
        stats["source"] = "NCI SEER Cancer Stat Facts: Prostate Cancer"
        stats["url"] = URL

        # Try to extract specific numbers
        stats.update(parse_seer_stats(text))

    except Exception as e:
        print(f"[SEER] Scraping failed: {e}. Using fallback.")
        stats = fallback_seer_stats()

    out_path = os.path.join(OUTPUT_DIR, "seer_statfacts.json")
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"[SEER] Saved to {out_path}")
    return stats


def parse_seer_stats(text):
    parsed = {}
    # 5-year survival rate overall
    m = re.search(r"5.year relative survival.*?([\d\.]+)%", text, re.IGNORECASE)
    if m:
        parsed["5yr_survival_overall_pct"] = float(m.group(1))

    # Incidence rate
    m = re.search(r"([\d\.]+)\s+per\s+100,000", text, re.IGNORECASE)
    if m:
        parsed["incidence_rate_per_100k"] = float(m.group(1))

    return parsed


def fallback_seer_stats():
    """
    Hard-coded from SEER Cancer Stat Facts: Prostate Cancer (2018-2022 data).
    Source: https://seer.cancer.gov/statfacts/html/prost.html
    """
    print("[SEER] Using hard-coded fallback statistics.")
    return {
        "source": "NCI SEER Cancer Stat Facts: Prostate Cancer (2018-2022, fallback)",
        "url": URL,
        "incidence_rate_per_100k": 112.7,
        "mortality_rate_per_100k": 19.6,
        "5yr_survival_overall_pct": 97.5,
        "new_cases_2024_estimate": 299010,
        "deaths_2024_estimate": 35250,
        "median_age_diagnosis": 67,
        "pct_diagnosed_localized": 76,

        # 5-year survival by stage
        "survival_by_stage": [
            {"stage": "Localized", "5yr_survival_pct": 99.9, "pct_cases": 76},
            {"stage": "Regional",  "5yr_survival_pct": 99.9, "pct_cases": 13},
            {"stage": "Distant",   "5yr_survival_pct": 38.0, "pct_cases": 8},
            {"stage": "Unknown",   "5yr_survival_pct": 77.6, "pct_cases": 3},
        ],

        # Age distribution at diagnosis (% of cases)
        "age_distribution": [
            {"age_group": "<45",   "pct_cases": 0.6},
            {"age_group": "45-54", "pct_cases": 8.6},
            {"age_group": "55-64", "pct_cases": 30.5},
            {"age_group": "65-74", "pct_cases": 36.1},
            {"age_group": "75-84", "pct_cases": 18.9},
            {"age_group": "85+",   "pct_cases": 5.3},
        ],
    }


if __name__ == "__main__":
    result = scrape_seer_statfacts()
    print(f"[SEER] Done. Keys: {list(result.keys())}")

"""
scrape_acs.py
Scrapes key prostate cancer statistics from the American Cancer Society website.
Source: https://www.cancer.org/cancer/types/prostate-cancer/about/key-statistics.html
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../../data/raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

URL = "https://www.cancer.org/cancer/types/prostate-cancer/about/key-statistics.html"


def scrape_acs_key_stats():
    print(f"[ACS] Fetching: {URL}")
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ACS] Request failed: {e}")
        return fallback_acs_stats()

    soup = BeautifulSoup(resp.text, "lxml")
    paragraphs = soup.find_all("p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30]

    stats = {
        "source": "American Cancer Society",
        "url": URL,
        "scraped_text": text_blocks[:30],
    }

    # Parse key numeric stats from text
    parsed = parse_numeric_stats(text_blocks)
    stats.update(parsed)

    out_path = os.path.join(OUTPUT_DIR, "acs_key_stats.json")
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"[ACS] Saved to {out_path}")
    return stats


def parse_numeric_stats(text_blocks):
    """Extract key numbers from ACS text."""
    import re
    parsed = {}
    full_text = " ".join(text_blocks)

    # New cases estimate
    m = re.search(r"([\d,]+)\s+new cases", full_text, re.IGNORECASE)
    if m:
        parsed["new_cases_estimate"] = int(m.group(1).replace(",", ""))

    # Deaths estimate
    m = re.search(r"([\d,]+)\s+(deaths|men will die)", full_text, re.IGNORECASE)
    if m:
        parsed["deaths_estimate"] = int(m.group(1).replace(",", ""))

    # Lifetime risk
    m = re.search(r"1\s+in\s+([\d]+)", full_text, re.IGNORECASE)
    if m:
        parsed["lifetime_risk_1_in"] = int(m.group(1))

    return parsed


def fallback_acs_stats():
    """Hard-coded fallback from ACS 2025 report if scraping fails."""
    print("[ACS] Using fallback hard-coded statistics (ACS 2025 report)")
    stats = {
        "source": "American Cancer Society (2025, fallback)",
        "new_cases_estimate": 313780,
        "deaths_estimate": 35770,
        "lifetime_risk_1_in": 8,
        "note": (
            "Prostate cancer is the most common cancer in men (30% of male cancers). "
            "It is the 2nd leading cause of cancer death in men behind lung cancer. "
            "5-year survival for distant-stage: 38%. For localized: ~100%."
        ),
        "incidence_trend": {
            "2007_2014_annual_change_pct": -6.4,
            "2014_2021_annual_change_pct": 3.0,
            "distant_stage_annual_change_pct": 4.7,
        },
        "mortality_trend": {
            "1990s_2000s_annual_decline_pct": -3.5,
            "recent_annual_decline_pct": -0.6,
        },
    }
    out_path = os.path.join(OUTPUT_DIR, "acs_key_stats.json")
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"[ACS] Fallback saved to {out_path}")
    return stats


if __name__ == "__main__":
    result = scrape_acs_key_stats()
    print(f"[ACS] Done. Keys: {list(result.keys())}")

"""
scrape_uspstf.py
Scrapes USPSTF prostate cancer screening guideline timeline.
Used to annotate the incidence trend chart with key policy change markers.
"""

import requests
from bs4 import BeautifulSoup
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

URL = "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/prostate-cancer-screening"


def scrape_uspstf():
    print(f"[USPSTF] Fetching: {URL}")
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        text = soup.get_text(separator=" ", strip=True)
        summary = text[:3000]
        result = {"source": "USPSTF", "url": URL, "text_sample": summary}
    except Exception as e:
        print(f"[USPSTF] Failed: {e}. Using fallback.")
        result = fallback_uspstf()

    out_path = os.path.join(OUTPUT_DIR, "uspstf_guidelines.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[USPSTF] Saved to {out_path}")
    return result


def fallback_uspstf():
    """Key USPSTF screening timeline data for chart annotations."""
    return {
        "source": "USPSTF Prostate Cancer Screening Guidelines (fallback)",
        "url": URL,
        "timeline": [
            {
                "year": 2012,
                "grade": "D",
                "summary": "USPSTF recommended AGAINST routine PSA-based screening for all men regardless of age (Grade D). Cited concern over overdiagnosis and overtreatment.",
                "impact": "Led to sharp decline in PSA screening rates and a subsequent drop in incidence of localized prostate cancer."
            },
            {
                "year": 2018,
                "grade": "C",
                "summary": "USPSTF revised to Grade C for men aged 55–69: individualized decision-making. Men should discuss benefits and harms of PSA screening with their clinician.",
                "impact": "Began reversal of screening decline. Incidence rates began rising again, particularly for localized disease."
            },
        ],
        "current_recommendation": (
            "For men aged 55–69: Grade C — discuss with your doctor. "
            "For men 70+: Grade D — routine screening not recommended. "
            "Shared decision-making is the current standard."
        ),
        "note_for_50_65_audience": (
            "If you are between 50 and 69, the USPSTF recommends talking with your "
            "doctor about whether PSA screening is right for you. Black men and those "
            "with a family history of prostate cancer may benefit from earlier discussion."
        ),
    }


if __name__ == "__main__":
    result = scrape_uspstf()
    print(f"[USPSTF] Done. Keys: {list(result.keys())}")

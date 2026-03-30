"""
run.py  —  One-step setup and launch script
Run:   python run.py

What it does:
  1. Runs all scrapers (live web fetch → fallback to published stats if blocked)
  2. Builds the SQLite database
  3. Launches the Flask dashboard at http://127.0.0.1:5000
"""

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(cmd, desc):
    print(f"\n{'='*50}")
    print(f"  {desc}")
    print(f"{'='*50}")
    result = subprocess.run([sys.executable] + cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"  [WARN] Step exited with code {result.returncode} — continuing.")


if __name__ == "__main__":
    # Step 1: Run scrapers
    run(["src/scraping/scrape_acs.py"],    "Scraping American Cancer Society…")
    run(["src/scraping/scrape_seer.py"],   "Scraping SEER Stat Facts…")
    run(["src/scraping/scrape_pmc.py"],    "Scraping PMC research articles…")
    run(["src/scraping/scrape_uspstf.py"], "Scraping USPSTF guidelines…")

    # Step 2: Build database
    run(["src/pipeline/build_database.py"], "Building SQLite database…")

    # Step 3: Launch app
    print("\n" + "="*50)
    print("  Launching dashboard → http://127.0.0.1:5000")
    print("="*50 + "\n")
    os.execv(sys.executable, [sys.executable, "src/app/app.py"])

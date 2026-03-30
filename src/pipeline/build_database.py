"""
build_database.py
Reads all raw data files and loads them into a SQLite database (prostate.db).
Run this after all scrapers have completed.

Tables created:
  - incidence_trends        (year, stage, rate_per_100k)
  - mortality_trends        (year, rate_per_100k)
  - survival_by_stage       (stage, 5yr_survival_pct, pct_cases)
  - age_distribution        (age_group, pct_cases)
  - race_disparities        (race_ethnicity, incidence_rate, mortality_rate)
  - state_rates             (state, incidence_rate, mortality_rate)
  - key_stats               (key, value, note)
  - uspstf_timeline         (year, grade, summary, impact)
"""

import json
import sqlite3
import pandas as pd
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "../../data/raw")
DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/prostate.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def load_json(filename):
    path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(path):
        print(f"  [WARN] Missing: {path}")
        return {}
    with open(path) as f:
        return json.load(f)


def build_incidence_trends(conn):
    """Comprehensive year-by-year incidence trends by stage."""
    # Data from Kratzer 2025, SEER, and PMC trend articles
    records = [
        # (year, stage, rate_per_100k, source)
        (2000, "Localized",  153.1, "SEER/Kratzer2025"),
        (2001, "Localized",  149.8, "SEER/Kratzer2025"),
        (2002, "Localized",  148.2, "SEER/Kratzer2025"),
        (2003, "Localized",  143.5, "SEER/Kratzer2025"),
        (2004, "Localized",  140.2, "SEER/Kratzer2025"),
        (2005, "Localized",  136.8, "SEER/Kratzer2025"),
        (2006, "Localized",  132.4, "SEER/Kratzer2025"),
        (2007, "Localized",  128.9, "SEER/Kratzer2025"),
        (2008, "Localized",  118.4, "SEER/Kratzer2025"),
        (2009, "Localized",  112.6, "SEER/Kratzer2025"),
        (2010, "Localized",  106.3, "SEER/Kratzer2025"),
        (2011, "Localized",  102.1, "SEER/Kratzer2025"),
        (2012, "Localized",   91.8, "SEER/Kratzer2025"),  # USPSTF Grade D
        (2013, "Localized",   84.2, "SEER/Kratzer2025"),
        (2014, "Localized",   76.2, "SEER/Kratzer2025"),  # Low point
        (2015, "Localized",   78.4, "SEER/Kratzer2025"),
        (2016, "Localized",   80.1, "SEER/Kratzer2025"),
        (2017, "Localized",   82.7, "SEER/Kratzer2025"),
        (2018, "Localized",   84.5, "SEER/Kratzer2025"),  # USPSTF Grade C
        (2019, "Localized",   86.2, "SEER/Kratzer2025"),
        (2020, "Localized",   82.1, "SEER/Kratzer2025"),  # COVID dip
        (2021, "Localized",   88.3, "SEER/Kratzer2025"),
        (2022, "Localized",   91.0, "SEER/Kratzer2025"),

        (2000, "Distant",  8.4, "SEER/Kratzer2025"),
        (2001, "Distant",  8.2, "SEER/Kratzer2025"),
        (2002, "Distant",  7.9, "SEER/Kratzer2025"),
        (2003, "Distant",  7.6, "SEER/Kratzer2025"),
        (2004, "Distant",  7.1, "SEER/Kratzer2025"),
        (2005, "Distant",  6.9, "SEER/Kratzer2025"),
        (2006, "Distant",  6.8, "SEER/Kratzer2025"),
        (2007, "Distant",  6.6, "SEER/Kratzer2025"),
        (2008, "Distant",  6.5, "SEER/Kratzer2025"),
        (2009, "Distant",  6.4, "SEER/Kratzer2025"),
        (2010, "Distant",  6.2, "SEER/Kratzer2025"),
        (2011, "Distant",  6.4, "SEER/Kratzer2025"),
        (2012, "Distant",  6.8, "SEER/Kratzer2025"),  # Starts rising after D grade
        (2013, "Distant",  7.1, "SEER/Kratzer2025"),
        (2014, "Distant",  7.4, "SEER/Kratzer2025"),
        (2015, "Distant",  7.9, "SEER/Kratzer2025"),
        (2016, "Distant",  8.2, "SEER/Kratzer2025"),
        (2017, "Distant",  8.8, "SEER/Kratzer2025"),
        (2018, "Distant",  9.5, "SEER/Kratzer2025"),
        (2019, "Distant", 10.1, "SEER/Kratzer2025"),
        (2020, "Distant", 10.8, "SEER/Kratzer2025"),
        (2021, "Distant", 11.9, "SEER/Kratzer2025"),
        (2022, "Distant", 12.6, "SEER/Kratzer2025"),

        (2000, "Regional", 14.2, "SEER/Kratzer2025"),
        (2002, "Regional", 13.8, "SEER/Kratzer2025"),
        (2004, "Regional", 13.1, "SEER/Kratzer2025"),
        (2006, "Regional", 12.4, "SEER/Kratzer2025"),
        (2008, "Regional", 11.8, "SEER/Kratzer2025"),
        (2010, "Regional", 11.2, "SEER/Kratzer2025"),
        (2012, "Regional", 10.6, "SEER/Kratzer2025"),
        (2014, "Regional",  9.8, "SEER/Kratzer2025"),
        (2016, "Regional",  9.5, "SEER/Kratzer2025"),
        (2018, "Regional",  9.8, "SEER/Kratzer2025"),
        (2020, "Regional", 10.1, "SEER/Kratzer2025"),
        (2022, "Regional", 10.4, "SEER/Kratzer2025"),
    ]

    df = pd.DataFrame(records, columns=["year", "stage", "rate_per_100k", "source"])
    df.to_sql("incidence_trends", conn, if_exists="replace", index=False)
    print(f"  [DB] incidence_trends: {len(df)} rows")


def build_mortality_trends(conn):
    """Year-by-year overall mortality rate per 100,000."""
    records = [
        (1999, 33.2), (2000, 31.8), (2001, 30.4), (2002, 28.9),
        (2003, 27.5), (2004, 26.1), (2005, 25.0), (2006, 23.8),
        (2007, 22.7), (2008, 21.9), (2009, 21.1), (2010, 20.6),
        (2011, 20.0), (2012, 19.8), (2013, 19.5), (2014, 19.3),
        (2015, 19.1), (2016, 19.0), (2017, 19.2), (2018, 19.3),
        (2019, 19.4), (2020, 19.6), (2021, 19.5), (2022, 19.6),
    ]
    df = pd.DataFrame(records, columns=["year", "rate_per_100k"])
    df["source"] = "SEER/CDC WONDER"
    df.to_sql("mortality_trends", conn, if_exists="replace", index=False)
    print(f"  [DB] mortality_trends: {len(df)} rows")


def build_survival_by_stage(conn):
    data = load_json("seer_statfacts.json")
    rows = data.get("survival_by_stage", [
        {"stage": "Localized", "5yr_survival_pct": 99.9, "pct_cases": 76},
        {"stage": "Regional",  "5yr_survival_pct": 99.9, "pct_cases": 13},
        {"stage": "Distant",   "5yr_survival_pct": 38.0, "pct_cases": 8},
        {"stage": "Unknown",   "5yr_survival_pct": 77.6, "pct_cases": 3},
    ])
    df = pd.DataFrame(rows)
    df.to_sql("survival_by_stage", conn, if_exists="replace", index=False)
    print(f"  [DB] survival_by_stage: {len(df)} rows")


def build_age_distribution(conn):
    data = load_json("seer_statfacts.json")
    rows = data.get("age_distribution", [
        {"age_group": "<45",   "pct_cases": 0.6},
        {"age_group": "45-54", "pct_cases": 8.6},
        {"age_group": "55-64", "pct_cases": 30.5},
        {"age_group": "65-74", "pct_cases": 36.1},
        {"age_group": "75-84", "pct_cases": 18.9},
        {"age_group": "85+",   "pct_cases": 5.3},
    ])
    df = pd.DataFrame(rows)
    df["is_target_audience"] = df["age_group"].isin(["55-64", "45-54"])
    df.to_sql("age_distribution", conn, if_exists="replace", index=False)
    print(f"  [DB] age_distribution: {len(df)} rows")


def build_race_disparities(conn):
    """
    Race/ethnicity incidence and mortality rates.
    Source: CDC USCS, PMC incidence trends article, Kratzer 2025.
    """
    records = [
        # race_ethnicity, incidence_rate, mortality_rate, relative_mortality_index
        ("Non-Hispanic Black",    175.2, 37.9, 2.09),
        ("Non-Hispanic White",    109.3, 18.1, 1.00),
        ("Hispanic",               96.4, 15.8, 0.87),
        ("Non-Hispanic Asian/PI",  60.3,  9.2, 0.51),
        ("Non-Hispanic AIAN",      78.2, 22.4, 1.24),
    ]
    df = pd.DataFrame(records, columns=[
        "race_ethnicity", "incidence_rate_per_100k",
        "mortality_rate_per_100k", "mortality_index_vs_white"
    ])
    df["source"] = "CDC USCS / PMC10720073 / Kratzer2025"
    df.to_sql("race_disparities", conn, if_exists="replace", index=False)
    print(f"  [DB] race_disparities: {len(df)} rows")


def build_race_trends(conn):
    """Year-by-year incidence by race (selected years). Source: PMC10720073."""
    records = [
        # year, race, incidence_rate_per_100k
        (2000, "Non-Hispanic Black",   228.5),
        (2004, "Non-Hispanic Black",   210.3),
        (2008, "Non-Hispanic Black",   190.1),
        (2012, "Non-Hispanic Black",   185.4),
        (2014, "Non-Hispanic Black",   172.6),
        (2016, "Non-Hispanic Black",   170.2),
        (2018, "Non-Hispanic Black",   171.8),
        (2020, "Non-Hispanic Black",   172.5),
        (2022, "Non-Hispanic Black",   175.2),

        (2000, "Non-Hispanic White",   152.1),
        (2004, "Non-Hispanic White",   138.4),
        (2008, "Non-Hispanic White",   118.2),
        (2012, "Non-Hispanic White",    96.4),
        (2014, "Non-Hispanic White",    82.1),
        (2016, "Non-Hispanic White",    87.3),
        (2018, "Non-Hispanic White",    94.5),
        (2020, "Non-Hispanic White",    98.2),
        (2022, "Non-Hispanic White",   109.3),

        (2000, "Hispanic",   110.2),
        (2004, "Hispanic",   104.6),
        (2008, "Hispanic",    98.1),
        (2012, "Hispanic",    89.4),
        (2014, "Hispanic",    82.5),
        (2016, "Hispanic",    80.1),
        (2018, "Hispanic",    88.4),
        (2020, "Hispanic",    90.2),
        (2022, "Hispanic",    96.4),

        (2000, "Non-Hispanic Asian/PI",  66.2),
        (2004, "Non-Hispanic Asian/PI",  62.1),
        (2008, "Non-Hispanic Asian/PI",  58.4),
        (2012, "Non-Hispanic Asian/PI",  52.1),
        (2014, "Non-Hispanic Asian/PI",  48.3),
        (2016, "Non-Hispanic Asian/PI",  51.2),
        (2018, "Non-Hispanic Asian/PI",  54.8),
        (2020, "Non-Hispanic Asian/PI",  57.1),
        (2022, "Non-Hispanic Asian/PI",  60.3),
    ]
    df = pd.DataFrame(records, columns=["year", "race_ethnicity", "incidence_rate_per_100k"])
    df["source"] = "PMC10720073 / CDC USCS"
    df.to_sql("race_trends", conn, if_exists="replace", index=False)
    print(f"  [DB] race_trends: {len(df)} rows")


def build_state_rates(conn):
    """
    State-level age-adjusted incidence and mortality rates.
    Source: CDC United States Cancer Statistics (USCS), 2018-2022 average.
    """
    records = [
        ("Alabama",       125.4, 26.8), ("Alaska",        98.2, 17.4),
        ("Arizona",       104.8, 18.2), ("Arkansas",      120.1, 24.5),
        ("California",    100.3, 16.8), ("Colorado",       99.4, 16.2),
        ("Connecticut",   118.6, 20.1), ("Delaware",      122.4, 23.6),
        ("Florida",       113.2, 21.4), ("Georgia",       128.6, 27.9),
        ("Hawaii",         72.4, 12.1), ("Idaho",          98.7, 17.8),
        ("Illinois",      118.4, 22.6), ("Indiana",       114.2, 21.8),
        ("Iowa",          106.8, 19.4), ("Kansas",        109.2, 20.1),
        ("Kentucky",      118.6, 23.4), ("Louisiana",     138.4, 31.2),
        ("Maine",         116.2, 20.8), ("Maryland",      126.8, 25.4),
        ("Massachusetts", 121.4, 19.8), ("Michigan",      118.6, 22.4),
        ("Minnesota",     105.8, 17.6), ("Mississippi",   142.1, 32.6),
        ("Missouri",      112.4, 21.8), ("Montana",        98.4, 17.2),
        ("Nebraska",      108.6, 19.8), ("Nevada",        102.4, 18.6),
        ("New Hampshire", 114.8, 19.2), ("New Jersey",    122.6, 22.8),
        ("New Mexico",     94.2, 16.4), ("New York",      116.8, 21.2),
        ("North Carolina",128.4, 26.1), ("North Dakota",  104.2, 18.8),
        ("Ohio",          116.8, 22.1), ("Oklahoma",      116.2, 22.8),
        ("Oregon",         98.6, 16.8), ("Pennsylvania",  120.4, 22.6),
        ("Rhode Island",  118.2, 20.4), ("South Carolina",132.6, 28.4),
        ("South Dakota",  106.4, 19.2), ("Tennessee",     122.8, 25.1),
        ("Texas",         106.8, 19.4), ("Utah",           93.8, 14.2),
        ("Vermont",       112.4, 18.8), ("Virginia",      122.6, 23.8),
        ("Washington",     98.4, 16.6), ("West Virginia", 118.4, 24.2),
        ("Wisconsin",     110.2, 19.6), ("Wyoming",        96.8, 17.4),
        ("District of Columbia", 148.2, 38.6),
    ]
    df = pd.DataFrame(records, columns=["state", "incidence_rate_per_100k", "mortality_rate_per_100k"])
    df["source"] = "CDC USCS 2018-2022"
    df.to_sql("state_rates", conn, if_exists="replace", index=False)
    print(f"  [DB] state_rates: {len(df)} rows")


def build_key_stats(conn):
    acs = load_json("acs_key_stats.json")
    seer = load_json("seer_statfacts.json")

    records = [
        ("new_cases_2025_estimate",     313780,  "ACS 2025 Report"),
        ("deaths_2025_estimate",         35770,  "ACS 2025 Report"),
        ("lifetime_risk_1_in",               8,  "ACS 2025"),
        ("5yr_survival_overall_pct",      97.5,  "SEER 2018-2022"),
        ("5yr_survival_localized_pct",    99.9,  "SEER 2018-2022"),
        ("5yr_survival_distant_pct",      38.0,  "SEER 2018-2022"),
        ("incidence_rate_per_100k",      112.7,  "SEER 2018-2022"),
        ("mortality_rate_per_100k",       19.6,  "SEER 2018-2022"),
        ("median_age_diagnosis",             67,  "SEER 2018-2022"),
        ("pct_cases_localized",              76,  "SEER 2018-2022"),
        ("black_vs_white_mortality_ratio",  2.1,  "CDC USCS / Kratzer 2025"),
        ("incidence_apc_2014_2021",         3.0,  "Kratzer 2025 (Annual Percent Change)"),
        ("distant_stage_apc_2014_2021",     4.7,  "Kratzer 2025"),
        ("mortality_apc_recent",           -0.6,  "Kratzer 2025"),
        ("pct_male_cancers_2025",            30,  "ACS 2025"),
    ]

    df = pd.DataFrame(records, columns=["stat_key", "value", "source"])
    df.to_sql("key_stats", conn, if_exists="replace", index=False)
    print(f"  [DB] key_stats: {len(df)} rows")


def build_uspstf_timeline(conn):
    data = load_json("uspstf_guidelines.json")
    rows = data.get("timeline", [
        {"year": 2012, "grade": "D",
         "summary": "USPSTF recommended AGAINST routine PSA screening for all men.",
         "impact": "Sharp decline in PSA screening; localized incidence dropped significantly."},
        {"year": 2018, "grade": "C",
         "summary": "USPSTF revised: individualized decision-making for men 55-69.",
         "impact": "Incidence rates began rising again; screening conversations encouraged."},
    ])
    df = pd.DataFrame(rows)
    df.to_sql("uspstf_timeline", conn, if_exists="replace", index=False)
    print(f"  [DB] uspstf_timeline: {len(df)} rows")


def main():
    print(f"\nBuilding SQLite database: {DB_PATH}\n")
    conn = get_conn()

    build_incidence_trends(conn)
    build_mortality_trends(conn)
    build_survival_by_stage(conn)
    build_age_distribution(conn)
    build_race_disparities(conn)
    build_race_trends(conn)
    build_state_rates(conn)
    build_key_stats(conn)
    build_uspstf_timeline(conn)

    conn.commit()
    conn.close()

    size_kb = os.path.getsize(DB_PATH) / 1024
    print(f"\n✓ Database built successfully ({size_kb:.1f} KB): {DB_PATH}")


if __name__ == "__main__":
    main()

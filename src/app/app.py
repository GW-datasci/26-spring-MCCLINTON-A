"""
app.py
Flask application entry point for the Prostate Cancer Data Dashboard.

Run:
    python src/app/app.py

Then open: http://127.0.0.1:5000
"""

import sys
import os

# Add src/ to path so imports work from any working directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, jsonify, request
from viz.charts import (
    chart_incidence_mortality_trends,
    chart_race_disparities,
    chart_state_map,
    chart_stage_over_time,
    chart_survival_by_stage,
    chart_age_distribution,
    chart_race_trends,
    chart_race_scatter,
    get_key_stats,
    get_risk_context,
)

app = Flask(__name__, template_folder="templates")


# ── Main dashboard ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    stats = get_key_stats()
    return render_template("index.html", stats=stats)


# ── API routes for interactive chart updates ─────────────────────────────────

@app.route("/api/chart/trends")
def api_trends():
    stage = request.args.get("stage", "All")
    return jsonify(chart_incidence_mortality_trends(stage_filter=stage))


@app.route("/api/chart/race-disparities")
def api_race_disparities():
    metric = request.args.get("metric", "incidence")
    return jsonify(chart_race_disparities(metric=metric))


@app.route("/api/chart/map")
def api_map():
    metric = request.args.get("metric", "incidence")
    return jsonify(chart_state_map(metric=metric))


@app.route("/api/chart/stage-over-time")
def api_stage_over_time():
    return jsonify(chart_stage_over_time())


@app.route("/api/chart/survival")
def api_survival():
    return jsonify(chart_survival_by_stage())


@app.route("/api/chart/age-distribution")
def api_age():
    return jsonify(chart_age_distribution())


@app.route("/api/chart/race-trends")
def api_race_trends():
    races = request.args.getlist("races")
    return jsonify(chart_race_trends(selected_races=races if races else None))


@app.route("/api/chart/race-scatter")
def api_race_scatter():
    return jsonify(chart_race_scatter())


@app.route("/api/risk-context")
def api_risk_context():
    age_group = request.args.get("age_group", "55-64")
    race = request.args.get("race", "Non-Hispanic White")
    return jsonify(get_risk_context(age_group=age_group, race=race))


@app.route("/api/key-stats")
def api_key_stats():
    return jsonify(get_key_stats())


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Prostate Cancer Dashboard — Ava McClinton, 2026")
    print("  Open: http://127.0.0.1:5000")
    print("="*55 + "\n")
    app.run(debug=True, port=5000)

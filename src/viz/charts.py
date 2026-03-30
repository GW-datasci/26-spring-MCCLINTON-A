"""
charts.py
All Plotly figure builders for the prostate cancer dashboard.
Each function returns a Plotly figure dict (JSON-serializable).
"""

import sqlite3
import json
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/prostate.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query_df(sql, params=()):
    conn = get_db()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


# ── Color palette ────────────────────────────────────────────────────────────
COLORS = {
    "localized": "#2196F3",
    "distant":   "#F44336",
    "regional":  "#FF9800",
    "mortality": "#9C27B0",
    "black":     "#1A237E",
    "white":     "#42A5F5",
    "hispanic":  "#26A69A",
    "asian":     "#EF5350",
    "aian":      "#FFA726",
    "highlight": "#E53935",
    "neutral":   "#78909C",
    "bg":        "#FAFAFA",
    "card":      "#FFFFFF",
}

RACE_COLOR_MAP = {
    "Non-Hispanic Black":    "#1A237E",
    "Non-Hispanic White":    "#42A5F5",
    "Hispanic":              "#26A69A",
    "Non-Hispanic Asian/PI": "#EF5350",
    "Non-Hispanic AIAN":     "#FFA726",
}

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", color="#1e293b", size=13),
    margin=dict(t=50, b=60, l=65, r=30),
    legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#e2e8f0", borderwidth=1,
                font=dict(size=12)),
    hovermode="x unified",
    xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0", linecolor="#cbd5e1"),
    yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0", linecolor="#cbd5e1"),
)


def _fig_to_json(fig):
    return json.loads(fig.to_json())


# ── Chart 1: Incidence & Mortality Trends ────────────────────────────────────
def chart_incidence_mortality_trends(stage_filter="All"):
    import plotly.graph_objects as go

    df_inc = query_df("SELECT * FROM incidence_trends ORDER BY year")
    df_mort = query_df("SELECT * FROM mortality_trends ORDER BY year")
    df_uspstf = query_df("SELECT * FROM uspstf_timeline ORDER BY year")

    fig = go.Figure()

    stages = df_inc["stage"].unique() if stage_filter == "All" else [stage_filter]
    stage_colors = {"Localized": COLORS["localized"], "Distant": COLORS["distant"], "Regional": COLORS["regional"]}

    for stage in stages:
        d = df_inc[df_inc["stage"] == stage]
        fig.add_trace(go.Scatter(
            x=d["year"], y=d["rate_per_100k"],
            name=f"{stage} Stage",
            mode="lines+markers",
            line=dict(color=stage_colors.get(stage, "#999"), width=2.5),
            marker=dict(size=5),
            hovertemplate=f"<b>{stage}</b><br>Year: %{{x}}<br>Rate: %{{y:.1f}} per 100k<extra></extra>",
        ))

    fig.add_trace(go.Scatter(
        x=df_mort["year"], y=df_mort["rate_per_100k"],
        name="Mortality Rate",
        mode="lines",
        line=dict(color=COLORS["mortality"], width=2.5, dash="dot"),
        hovertemplate="<b>Mortality</b><br>Year: %{x}<br>Rate: %{y:.1f} per 100k<extra></extra>",
    ))

    # USPSTF guideline markers
    grade_colors = {"D": "#B71C1C", "C": "#F57F17"}
    for _, row in df_uspstf.iterrows():
        fig.add_vline(
            x=row["year"], line_dash="dash",
            line_color=grade_colors.get(row["grade"], "#666"), line_width=2,
            annotation_text=f"USPSTF {row['year']}<br>Grade {row['grade']}",
            annotation_position="top left",
            annotation_font_size=11,
        )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Prostate Cancer Incidence & Mortality Trends (2000–2022)", font=dict(size=17)),
        xaxis=dict(title="Year", dtick=2),
        yaxis=dict(title="Age-Adjusted Rate per 100,000 Men"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return _fig_to_json(fig)


# ── Chart 2: Racial & Ethnic Disparities ─────────────────────────────────────
def chart_race_disparities(metric="incidence"):
    import plotly.graph_objects as go

    df = query_df("SELECT * FROM race_disparities ORDER BY incidence_rate_per_100k DESC")
    col = "incidence_rate_per_100k" if metric == "incidence" else "mortality_rate_per_100k"
    label = "Incidence" if metric == "incidence" else "Mortality"

    colors = [RACE_COLOR_MAP.get(r, "#aaa") for r in df["race_ethnicity"]]

    fig = go.Figure(go.Bar(
        x=df["race_ethnicity"],
        y=df[col],
        marker_color=colors,
        text=[f"{v:.1f}" for v in df[col]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Rate: %{y:.1f} per 100k<extra></extra>",
    ))

    # National average line
    avg = df[col].mean()
    fig.add_hline(y=avg, line_dash="dot", line_color="#555",
                  annotation_text=f"National avg: {avg:.1f}",
                  annotation_position="top right")

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=f"Prostate Cancer {label} Rate by Race/Ethnicity (2018–2022)", font=dict(size=17)),
        xaxis_title="Race/Ethnicity",
        yaxis_title=f"Age-Adjusted {label} Rate per 100,000 Men",
        showlegend=False,
    )
    return _fig_to_json(fig)


# ── Chart 3: Geographic Heatmap ───────────────────────────────────────────────
def chart_state_map(metric="incidence"):
    import plotly.graph_objects as go

    df = query_df("SELECT * FROM state_rates")

    # State abbreviation mapping
    state_abbr = {
        "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
        "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
        "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA",
        "Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
        "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
        "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH",
        "New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC",
        "North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA",
        "Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN",
        "Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
        "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","District of Columbia":"DC",
    }
    df["abbr"] = df["state"].map(state_abbr)
    col = "incidence_rate_per_100k" if metric == "incidence" else "mortality_rate_per_100k"
    label = "Incidence" if metric == "incidence" else "Mortality"
    cscale = "Blues" if metric == "incidence" else "Reds"

    fig = go.Figure(go.Choropleth(
        locations=df["abbr"],
        z=df[col],
        locationmode="USA-states",
        colorscale=cscale,
        colorbar=dict(title=f"{label}<br>Rate/100k"),
        hovertemplate="<b>%{text}</b><br>Rate: %{z:.1f} per 100k<extra></extra>",
        text=df["state"],
        zmin=df[col].min(),
        zmax=df[col].max(),
    ))

    geo_layout = {k: v for k, v in LAYOUT_DEFAULTS.items()
                  if k not in ("hovermode", "xaxis", "yaxis")}
    fig.update_layout(
        **geo_layout,
        hovermode="closest",
        title=dict(text=f"Prostate Cancer {label} Rate by State (2018–2022, per 100,000)", font=dict(size=17)),
        geo=dict(scope="usa", projection_type="albers usa",
                 showlakes=True, lakecolor="#dbeafe",
                 bgcolor="rgba(0,0,0,0)",
                 landcolor="#f8fafc", subunitcolor="#cbd5e1"),
        margin=dict(t=50, b=10, l=0, r=0),
    )
    return _fig_to_json(fig)


# ── Chart 4: Stage at Diagnosis Over Time ─────────────────────────────────────
def chart_stage_over_time():
    import plotly.graph_objects as go

    df = query_df("SELECT * FROM incidence_trends WHERE stage IN ('Localized','Distant') ORDER BY year")
    stages = ["Localized", "Distant"]
    colors = [COLORS["localized"], COLORS["distant"]]

    fig = go.Figure()
    for stage, color in zip(stages, colors):
        d = df[df["stage"] == stage]
        fig.add_trace(go.Scatter(
            x=d["year"], y=d["rate_per_100k"],
            name=stage, fill="tozeroy" if stage == "Localized" else None,
            mode="lines",
            line=dict(color=color, width=2.5),
            fillcolor="rgba(33,150,243,0.12)" if stage == "Localized" else "rgba(244,67,54,0.12)",
            hovertemplate=f"<b>{stage}</b><br>%{{x}}: %{{y:.1f}} per 100k<extra></extra>",
        ))

    # Policy markers
    fig.add_vrect(x0=2012, x1=2014, fillcolor="#FFCDD2", opacity=0.3,
                  annotation_text="USPSTF Grade D<br>(2012)", annotation_position="top left",
                  annotation_font_size=10)
    fig.add_vrect(x0=2018, x1=2020, fillcolor="#FFF9C4", opacity=0.4,
                  annotation_text="USPSTF Grade C<br>(2018)", annotation_position="top right",
                  annotation_font_size=10)

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Localized vs. Distant Stage Incidence Over Time", font=dict(size=17)),
        xaxis=dict(title="Year", dtick=2),
        yaxis=dict(title="Age-Adjusted Rate per 100,000 Men"),
    )
    return _fig_to_json(fig)


# ── Chart 5: Survival by Stage ───────────────────────────────────────────────
def chart_survival_by_stage():
    import plotly.graph_objects as go

    df = query_df("SELECT * FROM survival_by_stage")
    stage_colors = {
        "Localized": COLORS["localized"],
        "Regional":  COLORS["regional"],
        "Distant":   COLORS["distant"],
        "Unknown":   COLORS["neutral"],
    }
    colors = [stage_colors.get(s, "#aaa") for s in df["stage"]]

    fig = go.Figure(go.Bar(
        x=df["5yr_survival_pct"],
        y=df["stage"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.0f}%" for v in df["5yr_survival_pct"]],
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="<b>%{y}</b><br>5-Year Survival: %{x:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="5-Year Relative Survival Rate by Stage at Diagnosis", font=dict(size=17)),
        xaxis=dict(title="5-Year Relative Survival (%)", range=[0, 110]),
        yaxis=dict(title="Stage"),
        showlegend=False,
    )
    return _fig_to_json(fig)


# ── Chart 6: Age Distribution ─────────────────────────────────────────────────
def chart_age_distribution():
    import plotly.graph_objects as go

    df = query_df("SELECT * FROM age_distribution")
    colors = [COLORS["highlight"] if t else COLORS["neutral"] for t in df["is_target_audience"]]

    fig = go.Figure(go.Bar(
        x=df["age_group"],
        y=df["pct_cases"],
        marker_color=colors,
        text=[f"{v:.1f}%" for v in df["pct_cases"]],
        textposition="outside",
        hovertemplate="<b>Age %{x}</b><br>%{y:.1f}% of diagnoses<extra></extra>",
    ))

    # Annotation
    fig.add_annotation(
        x="55-64", y=df[df["age_group"] == "55-64"]["pct_cases"].values[0] + 3,
        text="⬅ Your age group<br>accounts for 30.5%<br>of all diagnoses",
        showarrow=False, bgcolor="rgba(229,57,53,0.1)",
        bordercolor=COLORS["highlight"], borderwidth=1,
        font=dict(size=11, color=COLORS["highlight"]),
    )

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Age Distribution at Prostate Cancer Diagnosis (2018–2022)", font=dict(size=17)),
        xaxis_title="Age Group at Diagnosis",
        yaxis_title="Percentage of All Cases (%)",
        showlegend=False,
    )
    return _fig_to_json(fig)


# ── Chart 7: Race × Incidence Trends Over Time ───────────────────────────────
def chart_race_trends(selected_races=None):
    import plotly.graph_objects as go

    df = query_df("SELECT * FROM race_trends ORDER BY year")
    if selected_races:
        df = df[df["race_ethnicity"].isin(selected_races)]
    else:
        selected_races = df["race_ethnicity"].unique()

    fig = go.Figure()
    for race in selected_races:
        d = df[df["race_ethnicity"] == race]
        if d.empty:
            continue
        fig.add_trace(go.Scatter(
            x=d["year"], y=d["incidence_rate_per_100k"],
            name=race,
            mode="lines+markers",
            line=dict(color=RACE_COLOR_MAP.get(race, "#999"), width=2.5),
            marker=dict(size=6),
            hovertemplate=f"<b>{race}</b><br>Year: %{{x}}<br>Rate: %{{y:.1f}}<extra></extra>",
        ))

    # Policy lines
    fig.add_vline(x=2012, line_dash="dash", line_color="#B71C1C", line_width=1.5,
                  annotation_text="USPSTF Grade D", annotation_font_size=10)
    fig.add_vline(x=2018, line_dash="dash", line_color="#F57F17", line_width=1.5,
                  annotation_text="USPSTF Grade C", annotation_font_size=10)

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Prostate Cancer Incidence Trends by Race/Ethnicity (2000–2022)", font=dict(size=17)),
        xaxis=dict(title="Year", dtick=4),
        yaxis=dict(title="Age-Adjusted Incidence Rate per 100,000 Men"),
    )
    return _fig_to_json(fig)


# ── Chart 8: Incidence vs Mortality Scatter (Race) ───────────────────────────
def chart_race_scatter():
    import plotly.graph_objects as go

    df = query_df("SELECT * FROM race_disparities")

    fig = go.Figure(go.Scatter(
        x=df["incidence_rate_per_100k"],
        y=df["mortality_rate_per_100k"],
        mode="markers+text",
        text=df["race_ethnicity"],
        textposition="top center",
        marker=dict(
            size=df["incidence_rate_per_100k"] / 6,
            color=[RACE_COLOR_MAP.get(r, "#999") for r in df["race_ethnicity"]],
            opacity=0.85,
            line=dict(width=1, color="#fff"),
        ),
        hovertemplate="<b>%{text}</b><br>Incidence: %{x:.1f}/100k<br>Mortality: %{y:.1f}/100k<extra></extra>",
    ))

    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Incidence vs. Mortality Rate by Race/Ethnicity", font=dict(size=17)),
        xaxis_title="Incidence Rate per 100,000",
        yaxis_title="Mortality Rate per 100,000",
        showlegend=False,
    )
    return _fig_to_json(fig)


# ── Summary stats for KPI cards ──────────────────────────────────────────────
def get_key_stats():
    df = query_df("SELECT stat_key, value FROM key_stats")
    return dict(zip(df["stat_key"], df["value"]))


# ── Risk context for target audience ─────────────────────────────────────────
def get_risk_context(age_group="55-64", race="Non-Hispanic White"):
    stats = get_key_stats()
    df_race = query_df(
        "SELECT * FROM race_disparities WHERE race_ethnicity = ?", [race]
    )

    if df_race.empty:
        inc_rate = stats.get("incidence_rate_per_100k", 112.7)
        mort_rate = stats.get("mortality_rate_per_100k", 19.6)
    else:
        inc_rate = float(df_race["incidence_rate_per_100k"].iloc[0])
        mort_rate = float(df_race["mortality_rate_per_100k"].iloc[0])

    df_age = query_df(
        "SELECT pct_cases FROM age_distribution WHERE age_group = ?", [age_group]
    )
    pct_age = float(df_age["pct_cases"].iloc[0]) if not df_age.empty else 30.5

    return {
        "age_group": age_group,
        "race": race,
        "incidence_rate": inc_rate,
        "mortality_rate": mort_rate,
        "pct_diagnoses_this_age": pct_age,
        "lifetime_risk": f"1 in {int(stats.get('lifetime_risk_1_in', 8))}",
        "survival_if_caught_early": f"{stats.get('5yr_survival_localized_pct', 99.9):.0f}%",
        "survival_if_late_stage": f"{stats.get('5yr_survival_distant_pct', 38.0):.0f}%",
        "screening_note": (
            "The USPSTF recommends that men aged 55–69 discuss PSA screening with their doctor. "
            "Black men and those with a family history of prostate cancer should start this "
            "conversation earlier — some guidelines suggest age 40–45."
        ),
    }

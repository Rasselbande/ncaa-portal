import streamlit as st
import pandas as pd
import sqlite3

# ==============================
# CONFIG
# ==============================

DB_PATH    = "data/portal.db"
TABLE_NAME = "portal_players"

COLUMN_LABELS = {
    "TIER_LEVEL":  "Tier",
    "POS_GROUP":   "Position",
    "CONFERENCE":  "Conf",
    "HT_display":  "HT",
    "TRB%":        "REB%",
}

st.set_page_config(
    page_title="Rebound Board – NCAA Portal",
    layout="wide"
)

# ==============================
# LOAD DATA
# ==============================

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    df.columns = df.columns.str.strip().str.replace("-", "_")
    return df

df = load_data()
df["POS_GROUP"] = df["POS_GROUP"].str.capitalize()

# ==============================
# SIDEBAR FILTERS
# ==============================

st.sidebar.header("Filters")

portal_only = st.sidebar.toggle("Portal players only", value=True)
base_df = df[df["PORTAL"] == 1].copy() if portal_only else df.copy()

st.sidebar.markdown("---")

# ── Dropdowns ─────────────────────────────────────────────────────
tier_options = sorted(base_df["TIER_LEVEL"].dropna().unique())
tier_select  = st.sidebar.multiselect("Tier", tier_options)

conf_options = sorted(base_df["CONFERENCE"].dropna().unique())
conf_select  = st.sidebar.multiselect("Conference", conf_options)

pos_options  = sorted(base_df["POS_GROUP"].dropna().unique())
pos_select   = st.sidebar.multiselect("Position", pos_options)

role_options = sorted(base_df["ROLE"].dropna().unique())
role_select  = st.sidebar.multiselect("Role", role_options)

st.sidebar.markdown("---")

# ── Sliders ───────────────────────────────────────────────────────
min_rpg = st.sidebar.slider(
    "Min RPG", 0.0, float(base_df["RPG"].max()), 0.0, 0.5
)
min_trb = st.sidebar.slider(
    "Min REB%", 0.0, float(base_df["TRB%"].max()), 0.0, 0.5
)
min_mpg = st.sidebar.slider(
    "Min MPG", 0.0, float(base_df["MPG"].max()), 0.0, 1.0
)
min_ppg = st.sidebar.slider(
    "Min PPG", 0.0, float(base_df["PPG"].max()), 0.0, 0.5
)

# ==============================
# APPLY FILTERS
# ==============================

filtered = base_df.copy()

if tier_select:
    filtered = filtered[filtered["TIER_LEVEL"].isin(tier_select)]
if conf_select:
    filtered = filtered[filtered["CONFERENCE"].isin(conf_select)]
if pos_select:
    filtered = filtered[filtered["POS_GROUP"].isin(pos_select)]
if role_select:
    filtered = filtered[filtered["ROLE"].isin(role_select)]

filtered = filtered[
    (filtered["RPG"]  >= min_rpg) &
    (filtered["TRB%"] >= min_trb) &
    (filtered["MPG"]  >= min_mpg) &
    (filtered["PPG"]  >= min_ppg)
]

filtered = filtered.sort_values("RPG", ascending=False)

# ==============================
# HEADER
# ==============================

st.title("🏀 Rebound Board")
st.markdown("Find the best rebounders in the Transfer Portal — filter by volume, rate, and role.")
st.markdown("---")

# ==============================
# DISPLAY TABLE
# ==============================

display_cols = [
    "Player", "CLASS", "HT_display", "POS_GROUP", "Team", "CONFERENCE",
    "TIER_LEVEL", "ROLE",
    "MPG", "PPG", "TRB%", "ORB", "DRB", "RPG",
]
display_cols = [c for c in display_cols if c in filtered.columns]

st.markdown(f"Showing **{len(filtered)}** players")

st.dataframe(
    filtered[display_cols]
    .rename(columns=COLUMN_LABELS)
    .style.format({
        "MPG":   "{:.1f}",
        "PPG":   "{:.1f}",
        "RPG":   "{:.1f}",
        "ORB":   "{:.1f}",
        "DRB":   "{:.1f}",
        "REB%":  "{:.1f}",
    }),
    use_container_width=True,
    hide_index=True
)

# ==============================
# FOOTER
# ==============================

st.markdown("---")
st.caption(
    "RPG = rebounds per game | ORB = offensive rebounds per game | "
    "DRB = defensive rebounds per game | REB% = total rebound rate (% of available rebounds grabbed)"
)

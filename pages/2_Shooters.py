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
    "ARCHETYPE":   "Style",
    "3P%":         "3FG%",
    "HT":          "HT",
}

st.set_page_config(
    page_title="Shooter Scout – NCAA Portal",
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

# Capitalize position
df["POS_GROUP"] = df["POS_GROUP"].str.capitalize()

# ==============================
# SIDEBAR FILTERS
# ==============================

st.sidebar.header("Filters")

# Portal toggle on top
portal_only = st.sidebar.toggle("Portal players only", value=True)

st.sidebar.markdown("---")

base_df = df[df["PORTAL"] == 1].copy() if portal_only else df.copy()

# ── Dropdowns: Tier, Conference, Position, Role ───────────────────
tier_options = sorted(base_df["TIER_LEVEL"].dropna().unique())
tier_select  = st.sidebar.multiselect("Tier", tier_options)

conf_options = sorted(base_df["CONFERENCE"].dropna().unique())
conf_select  = st.sidebar.multiselect("Conference", conf_options)

pos_options  = sorted(base_df["POS_GROUP"].dropna().unique())
pos_select   = st.sidebar.multiselect("Position", pos_options)

role_options = sorted(base_df["ROLE"].dropna().unique())
role_select  = st.sidebar.multiselect("Role", role_options)

st.sidebar.markdown("---")

# ── Sliders: 3PA, 3FG%, MPG, PPG ─────────────────────────────────
min_3pa = st.sidebar.slider(
    "Min 3PA (per game)",
    0.0, float(base_df["3PA"].max()), 1.0, 0.5
)

min_3p = st.sidebar.slider(
    "Min 3FG%", 0, 100, 30, 1,
    help="Three-point shooting percentage"
) / 100.0

min_mpg = st.sidebar.slider(
    "Min MPG", 0.0, float(base_df["MPG"].max()), 10.0, 1.0
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
    (filtered["3PA"]  >= min_3pa) &
    (filtered["3P%"]  >= min_3p)  &
    (filtered["MPG"]  >= min_mpg) &
    (filtered["PPG"]  >= min_ppg)
]

filtered = filtered.sort_values("3P%", ascending=False)

# ==============================
# HEADER
# ==============================

st.title("🏀 Shooting Board")
st.markdown("Find the best shooters in the Transfer Portal — filter by volume, efficiency, and role.")
st.markdown("---")

# ==============================
# DISPLAY TABLE
# ==============================

display_cols = [
    "Player", "CLASS", "HT", "POS_GROUP", "Team", "CONFERENCE",
    "TIER_LEVEL", "ROLE",
    "MPG", "PPG", "3PM", "3PA", "3P%",
]
display_cols = [c for c in display_cols if c in filtered.columns]

st.markdown(f"Showing **{len(filtered)}** players")

st.dataframe(
    filtered[display_cols]
    .rename(columns=COLUMN_LABELS)
    .style.format({
        "MPG":   "{:.1f}",
        "PPG":   "{:.1f}",
        "3PA":   "{:.1f}",
        "3PM":   "{:.1f}",
        "3FG%":  "{:.1%}",
    }),
    use_container_width=True,
    hide_index=True
)

# ==============================
# FOOTER
# ==============================

st.markdown("---")
st.caption(
    "3FG% = three-point shooting percentage | "
    "3PA = three-point attempts per game | "
    "3PM = three-pointers made per game"
)

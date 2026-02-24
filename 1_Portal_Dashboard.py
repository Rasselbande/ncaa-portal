import streamlit as st
import pandas as pd
import sqlite3

# ==============================
# CONFIG
# ==============================

DB_PATH    = "data/portal.db"
TABLE_NAME = "portal_players"

COLUMN_LABELS = {
    "PORTAL_IMPACT_SCORE": "Rank",
    "TIER_LEVEL":          "Tier",
    "POS_GROUP":           "Position",
    "PLAYER_PROFILE":      "Profile",
    "CONFERENCE":          "Conf",
    "ARCHETYPE":           "Style",
    "CLASS":               "Class",
    "ROLE":                "Role",
    "HT_display":          "HT",
}

st.set_page_config(
    page_title="NCAA Transfer Portal Dashboard",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
thead tr th {
    font-weight: 700 !important;
    color: #000000 !important;
    text-align: center !important;
}
tbody tr td {
    text-align: center !important;
}
tbody tr td:first-child {
    text-align: left !important;
    font-weight: 500;
}
tbody tr td:last-child {
    text-align: right !important;
}
</style>
""", unsafe_allow_html=True)

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

# Capitalize position values for cleaner display
df["POS_GROUP"] = df["POS_GROUP"].str.capitalize()

# ==============================
# HEADER
# ==============================

st.title("🏀 NCAA Transfer Portal Dashboard")
st.markdown("### Top Portal Players")

with st.expander("ℹ️ How does the Rank work?"):
    st.markdown("""
**Rank is a percentile score (0–100) based on raw stats — not on Role.**

It measures four components across all players in the dataset:

- **Production (40%)** — PPG, RPG, APG, MPG
- **Efficiency (30%)** — TS%, PER, TOV%
- **Defense (15%)** — STL%, BLK%, TRB%
- **Context (15%)** — Role value, Tier level

A player ranked 99.9 is in the top 0.1% of all 3,000+ players by this combined score.

**Why can a Role Player rank higher than an Impact Player?**
Role and Rank measure different things. Role is assigned by fixed thresholds based on MPG and USG%. A player can fall just under those cutoffs but still produce elite numbers when on the court.

Oscar Cluff is a good example: 17.6 PPG, 12.3 RPG, and a 36.2 PER as a Big puts him in the top 0.1% of all players regardless of role label. Rank rewards what the stats say — Role describes how the team uses the player.

**In short:** use Role to understand a player's function. Use Rank to compare production across the whole dataset.
    """)

# ==============================
# PORTAL ONLY
# ==============================

portal_df = df[df["PORTAL"] == 1].copy()

# ==============================
# SIDEBAR FILTERS
# ==============================

st.sidebar.header("Filters")

# ── Dropdowns: Tier, Conference, Position, Role, Style ────────────
tier_options = sorted(portal_df["TIER_LEVEL"].dropna().unique())
tier_select  = st.sidebar.multiselect("Tier", tier_options)

conf_options = sorted(portal_df["CONFERENCE"].dropna().unique())
conf_select  = st.sidebar.multiselect("Conference", conf_options)

pos_options  = sorted(portal_df["POS_GROUP"].dropna().unique())
pos_select   = st.sidebar.multiselect("Position", pos_options)

role_options = sorted(portal_df["ROLE"].dropna().unique())
role_select  = st.sidebar.multiselect("Role", role_options)

arch_options = sorted(portal_df["ARCHETYPE"].dropna().unique())
arch_select  = st.sidebar.multiselect("Style", arch_options)

st.sidebar.markdown("---")

# ── Sliders ───────────────────────────────────────────────────────
min_ppg = st.sidebar.slider(
    "Minimum PPG", 0.0, float(portal_df["PPG"].max()), 10.0, 0.5
)
if "HT" in portal_df.columns and portal_df["HT"].notna().any():
    ht_min = int(portal_df["HT"].dropna().min())
    ht_max = int(portal_df["HT"].dropna().max())
    min_ht = st.sidebar.slider("Minimum HT (inches)", ht_min, ht_max, ht_min, 1)
else:
    min_ht = 0
min_ht = 0
min_mpg = st.sidebar.slider(
    "Minimum MPG", 0.0, float(portal_df["MPG"].max()), 0.0, 0.5
)
min_rpg = st.sidebar.slider(
    "Minimum RPG", 0.0, float(portal_df["RPG"].max()), 0.0, 0.5
)
min_apg = st.sidebar.slider(
    "Minimum APG", 0.0, float(portal_df["APG"].max()), 0.0, 0.5
)
min_impact = st.sidebar.slider(
    "Minimum Rank", 0.0, 100.0, 50.0, 1.0
)

# ==============================
# APPLY FILTERS
# ==============================

filtered = portal_df.copy()

if tier_select:
    filtered = filtered[filtered["TIER_LEVEL"].isin(tier_select)]
if conf_select:
    filtered = filtered[filtered["CONFERENCE"].isin(conf_select)]
if pos_select:
    filtered = filtered[filtered["POS_GROUP"].isin(pos_select)]
if role_select:
    filtered = filtered[filtered["ROLE"].isin(role_select)]
if arch_select:
    filtered = filtered[filtered["ARCHETYPE"].isin(arch_select)]

filtered = filtered[
    (filtered["PPG"] >= min_ppg) &
    (filtered["MPG"] >= min_mpg) &
    (filtered["RPG"] >= min_rpg) &
    (filtered["APG"] >= min_apg) &
    (filtered["PORTAL_IMPACT_SCORE"] >= min_impact)
]
if "HT" in filtered.columns:
    filtered = filtered[filtered["HT"].isna() | (filtered["HT"] >= min_ht)]



filtered = filtered.sort_values(
    ["PORTAL_IMPACT_SCORE", "PPG"], ascending=False
)

# ==============================
# DISPLAY TABLE
# ==============================

display_cols = [
    "Player", "CLASS", "HT_display", "POS_GROUP", "Team", "CONFERENCE",
    "TIER_LEVEL", "ROLE", "ARCHETYPE",
    "MPG", "PPG", "HT", "RPG", "APG",
    "PORTAL_IMPACT_SCORE",
]
# Remove duplicate HT and missing cols
seen = set()
clean_cols = []
for c in display_cols:
    if c not in seen and c in filtered.columns:
        seen.add(c)
        clean_cols.append(c)

# Put HT right after CLASS
final_cols = []
for c in clean_cols:
    final_cols.append(c)

st.dataframe(
    filtered[final_cols]
    .rename(columns=COLUMN_LABELS)
    .style.format({
        "MPG":  "{:.1f}",
        "PPG":  "{:.1f}",
        "RPG":  "{:.1f}",
        "APG":  "{:.1f}",
        "Rank": "{:.1f}",
    }),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Player":   st.column_config.TextColumn("Player",   width="medium"),
        "Style":    st.column_config.TextColumn("Style",    width="medium"),
        "Rank":     st.column_config.NumberColumn("Rank",   width="small"),
        "MPG":      st.column_config.NumberColumn("MPG",    width="small"),
        "PPG":      st.column_config.NumberColumn("PPG",    width="small"),
        "RPG":      st.column_config.NumberColumn("RPG",    width="small"),
        "APG":      st.column_config.NumberColumn("APG",    width="small"),
        "HT":       st.column_config.NumberColumn("HT",     width="small"),
        "Class":    st.column_config.TextColumn("Class",    width="small"),
        "Position": st.column_config.TextColumn("Position", width="small"),
        "Team":     st.column_config.TextColumn("Team",     width="small"),
        "Conf":     st.column_config.TextColumn("Conf",     width="small"),
        "Tier":     st.column_config.TextColumn("Tier",     width="small"),
        "Role":     st.column_config.TextColumn("Role",     width="small"),
    }
)

# ==============================
# FOOTER
# ==============================

st.markdown("---")
st.markdown(
    f"Showing **{len(filtered)}** portal players "
    f"(filtered from {len(portal_df)} total portal entries)."
)

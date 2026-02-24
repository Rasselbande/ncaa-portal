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
**Rank is a percentile score (0–100) that measures overall player value across four components. Conference level is baked into the production numbers before scoring begins.**

**Production (35%)** — Scoring, rebounding, assists, and minutes — adjusted for conference level before scoring. A player's raw stats are multiplied by a conference weight so that production in stronger leagues carries more value. Two players with identical raw numbers will score differently if they play in different conferences.

**Efficiency (30%)** — True shooting percentage, Player Efficiency Rating, and AST/TO ratio. Measures how well a player produces relative to his opportunities. AST/TO captures both playmaking and turnover risk in a single number — a higher ratio means more value with fewer mistakes.

**Defense (15%)** — Steal rate, block rate, and total rebound rate. Reflects defensive activity and presence on both the perimeter and at the rim.

**Context (20%)** — Role value and tier level. A player carrying a heavy load at a high level scores higher than a bench player at a lower tier. This component rewards players who are trusted by their coaching staff and play meaningful minutes in competitive environments.

**Conference weights applied to production:**
- Power 5: full value
- High-Major: 88%
- Mid-Major: 76%
- Low-Major: 58%

**Role vs Rank** — Role describes how a team uses a player based on minutes and usage thresholds. Rank scores what the stats show after adjusting for competition level. A Role Player can rank very highly if his per-minute production is elite. Use Role to understand function — use Rank to compare value across the full dataset.
    """)

with st.expander("ℹ️ How are Tiers defined?"):
    st.markdown("""
Tiers group conferences by competitive level based on NCAA tournament performance, NET rankings, and KenPom data. Each tier carries a different weight in the Rank formula.

| Tier | Level | Conferences | Logic |
|------|-------|-------------|-------|
| 1 | Power 5 | ACC, B10, B12, Big East, SEC | Consistently rank in the top 5 of NET and KenPom. Receive the vast majority of at-large bids. |
| 2 | High-Major | A-10, AAC, MVC, MWC, WCC | At-large threats that regularly earn 2–4 tournament bids. Often rank ahead of individual Power 5 teams in efficiency. |
| 3 | Mid-Major | BWC, CAA, C-USA, IVY, MAC, OVC, Sun Belt, WAC | Solid conferences with 1–2 dominant teams that are dangerous in the first round but usually only get 1 bid. |
| 4 | Low-Major | AEC, A-Sun, BSky, BSC, Horizon, MAAC, MEAC, NEC, Patriot, SLC, SoCon, Summit, SWC, SWAC | Primarily one-bid leagues. Statistically these conferences occupy the bottom third of NET rankings. |

Production stats for players in lower tiers are discounted in the Rank formula to reflect the difference in competition level.
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

ht_options = {
    "Any": 0,
    "6-0+": 72, "6-1+": 73, "6-2+": 74, "6-3+": 75,
    "6-4+": 76, "6-5+": 77, "6-6+": 78, "6-7+": 79,
    "6-8+": 80, "6-9+": 81, "6-10+": 82, "6-11+": 83,
    "7-0+": 84,
}
ht_select = st.sidebar.selectbox("Minimum Height", list(ht_options.keys()))
min_ht = ht_options[ht_select]

st.sidebar.markdown("---")

# ── Sliders ───────────────────────────────────────────────────────
min_ppg = st.sidebar.slider(
    "Minimum PPG", 0.0, float(portal_df["PPG"].max()), 0.0, 0.5
)

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
    "Minimum Rank", 0.0, 100.0, 0.0, 1.0
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
if "HT" in filtered.columns and min_ht > 0:
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
    "MPG", "PPG", "RPG", "APG",
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

selection = st.dataframe(
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
    on_select="rerun",
    selection_mode="single-row",
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

# ── PLAYER CARD ───────────────────────────────────────────────────
selected_rows = selection.selection.rows if selection.selection.rows else []
if selected_rows:
    idx = filtered.iloc[selected_rows[0]]
    
    def fmt(val, dec=1):
        try: return f"{float(val):.{dec}f}"
        except: return "—"

    portal_status = "✅ In Portal" if idx.get("PORTAL", 0) == 1 else "❌ Not in Portal"
    
    st.markdown("---")
    st.markdown(f"""
<div style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:10px;padding:20px;margin-top:10px;">
    <div style="font-size:22px;font-weight:700;margin-bottom:4px;">{idx.get("Player","—")}</div>
    <div style="color:#666;font-size:13px;margin-bottom:16px;">
        {idx.get("Team","—")} &nbsp;|&nbsp; {idx.get("CONFERENCE","—")} &nbsp;|&nbsp; 
        {idx.get("TIER_LEVEL","—")} &nbsp;|&nbsp; {idx.get("CLASS","—")} &nbsp;|&nbsp; 
        {idx.get("HT_display", idx.get("HT","—"))} &nbsp;|&nbsp; {portal_status}
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;">
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Role</div>
            <div style="font-size:15px;font-weight:600;">{idx.get("ROLE","—")}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Position</div>
            <div style="font-size:15px;font-weight:600;">{idx.get("POS_GROUP","—")}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Style</div>
            <div style="font-size:15px;font-weight:600;">{idx.get("ARCHETYPE","—")}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Rank</div>
            <div style="font-size:15px;font-weight:600;">{fmt(idx.get("PORTAL_IMPACT_SCORE","—"))}</div>
        </div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;">
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">PPG</div>
            <div style="font-size:18px;font-weight:700;">{fmt(idx.get("PPG"))}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">RPG</div>
            <div style="font-size:18px;font-weight:700;">{fmt(idx.get("RPG"))}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">APG</div>
            <div style="font-size:18px;font-weight:700;">{fmt(idx.get("APG"))}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">MPG</div>
            <div style="font-size:18px;font-weight:700;">{fmt(idx.get("MPG"))}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">PER</div>
            <div style="font-size:18px;font-weight:700;">{fmt(idx.get("PER"))}</div>
        </div>
        <div style="background:#fff;border-radius:8px;padding:10px;text-align:center;">
            <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">TS%</div>
            <div style="font-size:18px;font-weight:700;">{fmt(idx.get("TS%"))}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================

st.markdown("---")
st.markdown(
    f"Showing **{len(filtered)}** portal players "
    f"(filtered from {len(portal_df)} total portal entries)."
)

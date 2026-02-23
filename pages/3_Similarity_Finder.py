import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# ==============================
# CONFIG
# ==============================

DB_PATH    = "/Users/phil/ncaa_portal/data/portal.db"
TABLE_NAME = "portal_players"

SIM_FEATURES = [
    'TS%', 'USG%', '3P%',
    'AST%', 'TOV%', 'STL%', 'BLK%', 'TRB%',
    'FTR', '3PATR'
]

COLUMN_LABELS = {
    "PORTAL_IMPACT_SCORE": "Rank",
    "TIER_LEVEL":          "Tier",
    "POS_GROUP":           "Position",
    "PLAYER_PROFILE":      "Profile",
    "CONFERENCE":          "Conf",
    "ARCHETYPE":           "Style",
}

st.set_page_config(
    page_title="Player Similarity – NCAA Portal",
    layout="wide"
)

# ==============================
# LOAD & PREP DATA
# ==============================

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    df.columns = df.columns.str.strip().str.replace("-", "_")
    return df

@st.cache_data
def build_similarity_matrix(df):
    features = [f for f in SIM_FEATURES if f in df.columns]
    df_sim = df.dropna(subset=features).copy().reset_index(drop=True)
    scaler = StandardScaler()
    X = scaler.fit_transform(df_sim[features])
    return df_sim, X, features

df_all = load_data()
df_sim, X, features = build_similarity_matrix(df_all)

# ==============================
# SIDEBAR
# ==============================

st.sidebar.header("Search Options")

top_n = st.sidebar.slider(
    "Number of similar players",
    min_value=3,
    max_value=25,
    value=8
)

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Similarity computed on {len(features)} style features:\n\n"
    + ", ".join(features)
)

# ==============================
# PAGE HEADER
# ==============================

st.title("🔍 Player Similarity Finder")
st.markdown(
    "Search for any player and find the most statistically similar players "
    "currently in the **Transfer Portal** — matched by playing style."
)
st.markdown("---")

# ==============================
# SEARCH INPUT
# ==============================

all_names = sorted(df_sim["Player"].dropna().unique())
player_input = st.selectbox(
    "🏀 Select or type a player name",
    options=[""] + all_names,
    index=0,
)

if not player_input:
    st.info("👆 Select a player above to find similar portal players.")
    st.stop()

# ==============================
# LOCATE PLAYER & COMPUTE
# ==============================

matches = df_sim[df_sim["Player"] == player_input]

if len(matches) == 0:
    st.error(f'Player "{player_input}" not found.')
    st.stop()

local_idx = matches.index[0]
p = df_sim.loc[local_idx]

sim_scores = cosine_similarity([X[local_idx]], X)[0]

result = df_sim.copy()
result["Similarity"] = sim_scores
result = result[result.index != local_idx]

# Restrict to same archetype
archetype = p.get("ARCHETYPE", None)
if pd.notna(archetype) and str(archetype) not in ["Unknown", "nan", "None"]:
    result = result[result["ARCHETYPE"] == archetype]
    archetype_note = f"Style: {archetype}"
else:
    archetype_note = "Style: Unknown — showing all positions"

# Portal only
result = result[result["PORTAL"] == 1]

# Top N
result = result.nlargest(top_n, "Similarity")

# ==============================
# PLAYER CARD — clean styled box
# ==============================

st.markdown("### Searched Player")

# Build a clean info card using a styled container
portal_badge = "✅ In Portal" if p.get("PORTAL") == 1 else "❌ Not in Portal"

st.markdown(f"""
<div style="
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 8px;
">
    <div style="font-size: 22px; font-weight: 700; color: #1a1a1a; margin-bottom: 12px;">
        {p.get('Player', '—')}
    </div>
    <div style="display: flex; gap: 48px; flex-wrap: wrap;">
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Team</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('Team', '—')}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Tier</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('TIER_LEVEL', '—')}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Class</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('CLASS', '—')}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Role</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('ROLE', '—')}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Style</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{archetype_note.replace('Style: ', '')}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">PPG</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('PPG', 0):.1f}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">RPG</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('RPG', 0):.1f}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">APG</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('APG', 0):.1f}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">PER</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{p.get('PER', 0):.1f}</div>
        </div>
        <div>
            <div style="font-size: 11px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Status</div>
            <div style="font-size: 15px; font-weight: 600; color: #212529;">{portal_badge}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================
# RESULTS TABLE
# ==============================

if len(result) == 0:
    st.warning(
        "No portal players found with the same style/archetype. "
        "Try a different player or check that clustering ran in your notebook."
    )
    st.stop()

st.markdown(f"### 🔁 {len(result)} Most Similar Portal Players")

display_cols = [
    "Player", "CLASS", "POS_GROUP", "Team", "CONFERENCE",
    "TIER_LEVEL", "ROLE", "ARCHETYPE",
    "MPG", "PPG", "RPG", "APG",
    "PORTAL_IMPACT_SCORE", "Similarity"
]
display_cols = [c for c in display_cols if c in result.columns]

st.dataframe(
    result[display_cols]
    .rename(columns=COLUMN_LABELS)
    .style.format({
        "MPG":        "{:.1f}",
        "PPG":        "{:.1f}",
        "RPG":        "{:.1f}",
        "APG":        "{:.1f}",
        "Rank":       "{:.1f}",
        "Similarity": "{:.3f}",
    }),
    use_container_width=True,
    hide_index=True
)

# ==============================
# STYLE COMPARISON TABLE
# ==============================

st.markdown("---")
st.markdown("### 📊 Style Profile Comparison")
st.caption("Searched player (highlighted) vs. similar portal players — style features")

style_cols = [f for f in SIM_FEATURES if f in df_sim.columns]

searched_row = p[["Player"] + style_cols].to_frame().T
similar_rows = result[["Player"] + style_cols].head(top_n)

compare_df = pd.concat([searched_row, similar_rows], ignore_index=True)
compare_df = compare_df.set_index("Player")
compare_df = compare_df.astype(float)

def highlight_searched(df):
    styles = pd.DataFrame('', index=df.index, columns=df.columns)
    styles.iloc[0] = 'background-color: #fff3cd; font-weight: bold'
    return styles

st.dataframe(
    compare_df.style
    .apply(highlight_searched, axis=None)
    .format("{:.1f}"),
    use_container_width=True
)

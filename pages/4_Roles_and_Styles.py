import streamlit as st

st.set_page_config(
    page_title="Roles & Styles – NCAA Portal",
    layout="wide"
)

st.title("🏀 Roles & Styles")
st.markdown("Reference for all **Roles** and **Styles** used in this dashboard.")
st.markdown("---")

# ==============================
# ROLES
# ==============================

st.markdown("## 🏀 Roles")
st.caption(
    "Roles are assigned based on minutes per game (MPG), usage rate (USG%), and scoring (PPG). "
    "They reflect how much the offense runs through a player, not raw talent alone. "
    "MPG alone is not used to define Stars — foul trouble and blowouts can suppress minutes "
    "for players who are clearly the focal point of their team."
)
st.markdown("")

st.markdown("""
**Star**
The go-to guy. Qualifies with MPG ≥ 26, USG% ≥ 24, and PPG ≥ 12 — meaning the offense runs through him whenever he is on the court. Strong PER and true shooting, plus real playmaking ability. USG% is weighted more heavily than minutes here because it reflects impact regardless of foul trouble or game situation. Avg: 15.6 PPG, 32.0 MPG, 26.1% USG, 19.3 PER.

---

**Starter**
A reliable, everyday contributor. Solid minutes (MPG ≥ 24) and meaningful usage (USG% ≥ 17). Not the focal point but a trusted piece — coaches know exactly what they're getting. Good efficiency and consistent production across the board. Avg: 11.1 PPG, 28.2 MPG, 21.3% USG, 16.4 PER.

---

**Role Player**
The backbone of any roster. Moderate minutes (MPG ≥ 16) and limited scoring, but contributes in specific ways — rebounding, defense, spacing. Lower usage means this player thrives in a defined role rather than creating on their own. High availability in the portal makes this the most searchable group. Avg: 6.9 PPG, 21.6 MPG, 17.6% USG, 14.2 PER.

---

**Bench**
Limited minutes (below 16 MPG) and low usage — but don't overlook this group. Some bench players are young freshmen or role-specific specialists (shooters, rim protectors) who haven't had the opportunity yet. Lowest PER but highest upside for development at a new program. Avg: 3.8 PPG, 12.9 MPG, 16.8% USG, 12.4 PER.
""")

st.markdown("---")

# ==============================
# STYLES
# ==============================

st.markdown("## 🏀 Styles")
st.caption(
    "Styles are assigned by clustering players based on how they play — "
    "shot selection, passing, rebounding, and defensive activity. "
    "Two players can have the same Role but very different Styles."
)
st.markdown("")

st.markdown("### Guards")
st.markdown("""
**Scoring Guard**
A perimeter scorer who lives behind the arc. Highest three-point attempt rate (59.7%) in the dataset with solid shooting. Limited playmaking and rebounding — this player's job is to space the floor and score off movement. Avg: 8.6 PPG, 2.4 RPG, 1.5 APG.

---

**Primary Creator**
The engine of the offense. Highest assist rate (23.1%) and strong usage, comfortable putting the ball on the floor and creating for others. Shoots threes at a decent clip but not a volume shooter. Avg: 9.6 PPG, 2.8 RPG, 3.1 APG.

---

**Two-Way Guard**
The most versatile guard — above-average steal rate (2.3%), solid rebounding for the position (10.8% TRB), and a balanced offensive profile. Not a specialist, but brings real value on both ends. Avg: 8.3 PPG, 4.0 RPG, 1.5 APG.
""")

st.markdown("")
st.markdown("### Wings")
st.markdown("""
**Stretch Wing**
A wing built to shoot — second-highest three-point attempt rate (59.6%) of all archetypes. Moves well off the ball, spaces the floor, and provides some defensive activity. Limited creation. Avg: 8.7 PPG, 3.1 RPG, 1.1 APG.

---

**Offensive Wing**
A scoring wing with more interior presence than the Stretch Wing. Higher usage (22.9%), attacks the basket more, and contributes on the glass. Versatile offensive threat who can score in multiple ways. Avg: 11.5 PPG, 4.7 RPG, 1.9 APG.

---

**Utility Wing**
The glue guy. Lowest scoring of the wings but contributes across the board — decent assist rate, steals, and rebounding. Does a bit of everything without dominating any single category. Avg: 5.5 PPG, 3.7 RPG, 1.1 APG.
""")

st.markdown("")
st.markdown("### Forwards")
st.markdown("""
**Offensive Forward**
A high-usage forward who attacks the basket and scores inside-out. Strong assist rate (14.1%) for a forward, good free throw rate, and meaningful three-point volume. A modern, multi-dimensional threat. Avg: 10.7 PPG, 5.1 RPG, 1.8 APG.

---

**Stretch Forward**
A forward who spaces the floor with high three-point attempt rate (52.9%). Lower usage and scoring than the Offensive Forward — his value is floor spacing and off-ball movement to open driving lanes for teammates. Avg: 7.1 PPG, 3.2 RPG, 0.9 APG.

---

**Interior Forward**
A physical, paint-based forward. Highest rebounding rate among forwards (15.3% TRB), strong block rate, and very low three-point attempts. Does the dirty work — screens, boards, and finishes at the rim. Avg: 6.4 PPG, 4.7 RPG, 0.8 APG.
""")

st.markdown("")
st.markdown("### Bigs")
st.markdown("""
**Offensive Big**
A skilled big with the highest usage (24.1%) and assist rate (14.8%) among bigs — can face up, pass out of the post, and score in multiple ways. Shoots some threes. A modern, versatile center. Avg: 11.1 PPG, 6.3 RPG, 1.7 APG.

---

**Stretch Big**
A big who spaces the floor with high three-point attempt rate (36.5%) for the position. Lower rebounding and block numbers — sacrifices traditional big-man roles for perimeter spacing. Best paired alongside a Rim Protector. Avg: 5.9 PPG, 3.5 RPG, 0.8 APG.

---

**Rim Protector**
The anchor. Highest block rate (6.2%) in the entire dataset, strong rebounding, and almost zero three-point attempts. His value is defensive deterrence and interior presence — changes the game without scoring. Avg: 5.1 PPG, 4.4 RPG, 0.5 APG.
""")

st.markdown("---")
st.caption(
    "Role thresholds: Star = MPG ≥ 26 & USG% ≥ 24 & PPG ≥ 12 | "
    "Starter = MPG ≥ 24 & USG% ≥ 17 | Role Player = MPG ≥ 16 | Bench = below all thresholds."
)

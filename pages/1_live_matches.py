import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ================= 🎨 Page Configuration & Professional Styling =================
st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom sleek UI adjustments overriding default canvas margins
custom_css = """
<style>
    /* Light grey background for the app */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
    }
    /* Clean white background with border for sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    /* Title styling tweak */
    h1 {
        color: #1e293b !important;
        font-weight: 700 !important;
    }
    h2, h3 {
        color: #334155 !important;
    }
    /* Buttons typography styling */
    div.stButton > button {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: background-color 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #0369a1 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ================= 🔑 API Configuration =================
# Professional tip: Ideally move this to st.secrets for absolute safety.
CRICBUZZ_API_KEY = "759e4323e3msh8c6046223e5f544p1163e1jsneb8afe748d67"
CRICBUZZ_HOST = "cricbuzz-cricket.p.rapidapi.com"

if not CRICBUZZ_API_KEY:
    st.error("🔒 RAPIDAPI_KEY configuration missing. Set it inside secrets or your script environment variables.")
    st.stop()


class CricbuzzAPI:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": CRICBUZZ_API_KEY,
            "x-rapidapi-host": CRICBUZZ_HOST,
        }
        self.base_url = "https://cricbuzz-cricket.p.rapidapi.com"

    @st.cache_data(ttl=30) # Cache the live scores API call for 30 seconds to minimize rate limits
    def get_live_matches(_self):
        """Fetch all live matches"""
        try:
            url = f"{_self.base_url}/matches/v1/live"
            response = requests.get(url, headers=_self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"⚠️ Error fetching live matches: {e}")
            return {}

    @st.cache_data(ttl=15) # Shorter cache duration for ongoing fast ball-by-ball scorecards
    def get_scorecard(_self, match_id: str):
        """Fetch detailed scorecard by matchId"""
        try:
            url = f"{_self.base_url}/mcenter/v1/{match_id}/scard"
            response = requests.get(url, headers=_self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"⚠️ Error fetching scorecard: {e}")
            return {}


def format_time(epoch_ms):
    """Convert epoch ms to human-readable format"""
    try:
        if epoch_ms:
            return datetime.fromtimestamp(int(epoch_ms) / 1000).strftime("%d %b %Y, %I:%M %p")
        return "N/A"
    except:
        return "N/A"


def show_innings_scorecard(api: CricbuzzAPI, match_id: str):
    """Display batting & bowling scorecard for selected match"""
    with st.spinner("Retrieving innings analytics..."):
        data = api.get_scorecard(match_id)
        
    if not data or "scorecard" not in data:
        st.warning("⚠️ No detailed scorecard matrix data available for this match yet.")
        return

    for i, innings in enumerate(data.get("scorecard", []), start=1):
        st.markdown(f"### 📊 Inning {i} — **{innings.get('batteamname', 'Unknown')}**")

        # 🏏 Batting Table Data Cleaning
        batsmen_list = [
            {
                "Batsman": b.get("name", ""),
                "Runs": b.get("runs", 0),
                "Balls": b.get("balls", 0),
                "4s": b.get("fours", 0),
                "6s": b.get("sixes", 0),
                "Strike Rate": b.get("strkrate", 0),
                "Dismissal": b.get("outdec", ""),
            }
            for b in innings.get("batsman", [])
        ]
        batsmen_df = pd.DataFrame(batsmen_list)
        if not batsmen_df.empty:
            st.caption("🏏 **Batting Performance**")
            st.dataframe(batsmen_df.set_index("Batsman"), use_container_width=True)

        # 🎯 Bowling Table Data Cleaning
        bowlers_list = [
            {
                "Bowler": bl.get("name", ""),
                "Overs": bl.get("overs", 0),
                "Maidens": bl.get("maidens", 0),
                "Runs": bl.get("runs", 0),
                "Wickets": bl.get("wickets", 0),
                "Economy": bl.get("economy", 0),
            }
            for bl in innings.get("bowler", [])
        ]
        bowlers_df = pd.DataFrame(bowlers_list)
        if not bowlers_df.empty:
            st.caption("☄️ **Bowling Summary**")
            st.dataframe(bowlers_df.set_index("Bowler"), use_container_width=True)

        st.markdown("---")


def show_live_matches():
    """Main dashboard renderer loop"""
    # Header layout using neat native structures
    col_header, col_logo = st.columns([5, 1])
    with col_header:
        st.title("Cricbuzz LiveStats")
        st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top:-15px;'>Real-time operational dashboard for tracking current match series metrics</p>", unsafe_allow_html=True)
    with col_logo:
        # Replaced large distracting gif with a clean static SVG animation reference
        st.image("https://cdnl.iconscout.com/lottie/premium/thumb/cricket-bat-8547074-6737094.gif", width=90)

    api = CricbuzzAPI()
    with st.spinner("Polling live matches from Cricbuzz Network..."):
        data = api.get_live_matches()

    if not data or "typeMatches" not in data:
        st.info("ℹ️ No tournament matches are broadcasted live at this moment.")
        return

    series_options = {}
    for type_match in data.get("typeMatches", []):
        match_type = type_match.get("matchType", "Unknown")
        for series in type_match.get("seriesMatches", []):
            series_info = series.get("seriesAdWrapper", {})
            if "matches" in series_info:
                series_name = series_info.get("seriesName", "Unknown Series")
                key = f"{series_name} ({match_type.upper()})"
                series_options[key] = series_info["matches"]

    if not series_options:
        st.warning("⚠️ Operational rosters are active but find no current series lines running.")
        return

    # Clean dropdown metric selection
    selected_series = st.selectbox(
        "Select Active Series / League:", list(series_options.keys())
    )
    matches = series_options[selected_series]

    st.markdown("### Match Details")
    
    # Process and build cards for matches in selected series
    for match in matches:
        match_info = match.get("matchInfo", {})
        match_score = match.get("matchScore", {})

        team1 = match_info.get("team1", {}).get("teamName", "Team 1")
        team2 = match_info.get("team2", {}).get("teamName", "Team 2")
        match_id = match_info.get("matchId", "")

        # Wrap each match profile inside a neat modern UI Container Border Box
        with st.container(border=True):
            col_t, col_s = st.columns([3, 1])
            with col_t:
                st.markdown(f"#### **{team1} vs {team2}**")
                st.caption(f"📍 {match_info.get('matchDesc', '')} | {match_info.get('matchFormat', '')}")
            with col_s:
                # Custom status badge layout logic inside standard metrics UI
                state_title = match_info.get('stateTitle', '').upper()
                st.metric(label="Match State", value=state_title)

            # Meta specifications tracking metrics inside clean layout columns
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                venue = venue = match_info.get("venueInfo", {})
                st.markdown(f"🏟️ **Venue:**\n{venue.get('ground', '')}, {venue.get('city', '')}")
            with m_col2:
                st.markdown(f"⏰ **Start Time:**\n{format_time(match_info.get('startDate'))}")
            with m_col3:
                st.markdown(f"📢 **Current Status:**\n*{match_info.get('status', '')}*")

            # Scores Section layout adjustment inside metrics components instead of success tags
            if "team1Score" in match_score or "team2Score" in match_score:
                st.markdown("<p style='font-weight:600; margin-bottom:2px; margin-top:10px; color:#475569;'>Current Innings scoreboard</p>", unsafe_allow_html=True)
                score_col1, score_col2 = st.columns(2)
                
                with score_col1:
                    if "team1Score" in match_score:
                        t1 = match_info.get("team1", {}).get("teamSName", "Team 1")
                        t1_inn = match_score.get("team1Score", {}).get("inngs1", {})
                        val_str = f"{t1_inn.get('runs', 0)}/{t1_inn.get('wickets', 0)}"
                        delta_str = f"Overs: {t1_inn.get('overs', 0)}"
                        st.metric(label=f"🏏 {t1}", value=val_str, delta=delta_str, delta_color="normal")
                
                with score_col2:
                    if "team2Score" in match_score:
                        t2 = match_info.get("team2", {}).get("teamSName", "Team 2")
                        t2_inn = match_score.get("team2Score", {}).get("inngs1", {})
                        val_str = f"{t2_inn.get('runs', 0)}/{t2_inn.get('wickets', 0)}"
                        delta_str = f"Overs: {t2_inn.get('overs', 0)}"
                        st.metric(label=f"🏏 {t2}", value=val_str, delta=delta_str, delta_color="normal")

            # Actions Row
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if match_id:
                # Removed dynamic emojis inside unique loop string states to fix UI string rendering quirks
                if st.button("View Live Analytical Scorecard Table", key=f"btn_{match_id}"):
                    st.markdown("---")
                    show_innings_scorecard(api, match_id)


# ================= ℹ️ Sidebar Structure Formatting =================
with st.sidebar:
    st.markdown("### 📋 System Information")
    st.markdown(
        """
        **Cricbuzz LiveStats Engine** An enterprise analytics layout tracking data streams over standard data architecture protocol.
        
        **Supported Analytics Metrics:**
        * Real-time Match Status Updates
        * Dynamic League Series Sorting
        * Interactive Analytical Scorecards
        """
    )
    st.markdown("---")
    st.caption("v1.2.0 | Dashboard Engine Core")

# 🚀 Init System Loop App Execution
if __name__ == "__main__":
    show_live_matches()
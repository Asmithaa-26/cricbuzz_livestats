import streamlit as st
import http.client
import json
import requests
import pandas as pd
from urllib.parse import quote

# ---------------- 🎨 Page Configuration & Professional Styling ----------------
st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise CSS injection targeting clean canvas structures, avoiding harsh multi-color gradients
custom_css = """
<style>
    /* Premium neutral theme palette application */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    /* Typography adjustments */
    h1 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }
    h2, h3, h4 {
        color: #1e293b !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
    }
    /* Tab formatting tweaks */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #64748b !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0284c7 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------- 🔑 API Key Architecture Configuration ----------------
API_KEY = "759e4323e3msh8c6046223e5f544p1163e1jsneb8afe748d67"
BASE_URL = "cricbuzz-cricket.p.rapidapi.com"
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": BASE_URL}

if not API_KEY:
    st.error("🔒 Security Halt: RAPIDAPI_KEY initialization value missing. Please verify configuration keys.")
    st.stop()


# ---------------- 📡 Optimised Structural Fetch Implementations ----------------
@st.cache_data(ttl=300) # Cache entity profiles for 5 minutes to prevent rate limit throttling
def search_players(query):
    """Search for players by name"""
    query_encoded = quote(query)
    conn = http.client.HTTPSConnection(BASE_URL)
    conn.request("GET", f"/stats/v1/player/search?plrN={query_encoded}", headers=HEADERS)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    try:
        return json.loads(data.decode("utf-8"))
    except:
        return {}

@st.cache_data(ttl=300)
def get_player_details(player_id):
    """Fetch player details"""
    conn = http.client.HTTPSConnection(BASE_URL)
    conn.request("GET", f"/stats/v1/player/{player_id}", headers=HEADERS)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    try:
        return json.loads(data.decode("utf-8"))
    except:
        return {}

@st.cache_data(ttl=300)
def get_player_stats(player_id, stat_type="batting"):
    """Fetch player stats (batting or bowling)"""
    url = f"https://{BASE_URL}/stats/v1/player/{player_id}/{stat_type}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"⚠️ Query Network Interface Error: {e}")
    return {}

def parse_stats_table(stats_json, drop_columns=None):
    """Convert raw stats JSON into a standardized, indexed DataFrame"""
    if not stats_json or "headers" not in stats_json or "values" not in stats_json:
        return pd.DataFrame()
    headers = stats_json["headers"]
    rows = [row["values"] for row in stats_json["values"]]
    df = pd.DataFrame(rows, columns=headers)
    if drop_columns:
        df = df.drop(columns=drop_columns, errors="ignore")
    if not df.empty and "matchType" in df.columns:
        df = df.set_index("matchType")
    return df


# ---------------- ℹ️ Sidebars ----------------
with st.sidebar:
    st.markdown("### 📊 Operational Intel")
    st.markdown(
        """
        **Cricbuzz LiveStats Intelligence Suite** Enterprise environment interface pulling raw player telemetry profiles directly from cricbuzz central nodes.
        
        **Available Data Scopes:**
        * Standard Core Profile Elements
        * High-Density ICC Ranking Matrices
        * Contextual Format Performance Tables
        """
    )
    st.markdown("---")
    st.caption("v2.1.0 | Stable Node Build")


# ---------------- 🏁 Primary Layout Matrix ----------------
st.title("🏏 Player Telemetry & Performance Dashboard")
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top:-15px;'>Inspect performance metrics, records, and real-time standing rankings across competitive formats</p>", unsafe_allow_html=True)

# Main Query Selector Interface
player_name = st.text_input("Search Registry Database:", placeholder="Type a player name (e.g. Virat Kohli, Joe Root)...")

if player_name:
    with st.spinner("Searching master registry database..."):
        results = search_players(player_name)

    if "player" in results and results["player"]:
        player_options = {p["name"]: p for p in results["player"]}
        
        # Wrap search refinement options cleanly 
        col_select, _ = st.columns([2, 2])
        with col_select:
            selected_name = st.selectbox("Refine Identifier Selection:", list(player_options.keys()))
            
        selected_player = player_options[selected_name]

        # Clean native functional dashboard tabs divider
        tabs = st.tabs(["📋 Biographical Profile", "Analytics"])

        # ---------------- 📋 Tab 1: Profile Matrix ----------------
        with tabs[0]:
            with st.spinner("Compiling biometric profile files..."):
                details = get_player_details(selected_player["id"])
            
            st.markdown(f"## {selected_player['name']}")
            st.markdown(f"<p style='color: #0284c7; font-weight: 600; margin-top: -15px;'>Primary Representative: {selected_player.get('teamName','N/A')}</p>", unsafe_allow_html=True)
            
            # Use structural columns instead of raw markdown lists for standard metadata profiles
            with st.container(border=True):
                meta_col1, meta_col2, meta_col3 = st.columns(3)
                with meta_col1:
                    st.markdown(f"**📅 Date of Birth:**\n{selected_player.get('dob', 'N/A')}")
                    st.markdown(f"**🌍 Place of Birth:**\n{details.get('birthPlace', 'N/A')}")
                with meta_col2:
                    st.markdown(f"**🧢 Field Role:**\n{details.get('role', 'N/A')}")
                    st.markdown(f"**🏏 Batting Mechanics:**\n{details.get('bat', 'N/A')}")
                with meta_col3:
                    st.markdown(f"**⚾ Bowling Style:**\n{details.get('bowl', 'N/A')}")
            
            # Render descriptive rosters tracking external squad rosters
            if details.get('teams'):
                with st.container(border=True):
                    st.markdown(f"**📋 Rostered Team Allocations:**\n*{details.get('teams')}*")

            

        # ---------------- 🏏 Tab 2: Analytics ----------------
        with tabs[1]:
            st.markdown("### 📈 Comprehensive Batting Metrics Matrix")
            with st.spinner("Extracting performance timelines..."):
                batting_stats = get_player_stats(selected_player["id"], "batting")
            
            df_bat = parse_stats_table(batting_stats, drop_columns=["400"])
            if not df_bat.empty:
                st.dataframe(df_bat, use_container_width=True)
            else:
                st.info("ℹ️ Performance metrics registry found no active history lines for this category.")

        
    else:
        st.warning("⚠️ No database entity files matches the current entry. Refine search strings.")
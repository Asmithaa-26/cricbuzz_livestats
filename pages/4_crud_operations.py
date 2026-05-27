import streamlit as st
import pandas as pd
import sqlite3

# ---------------- SQLite Configuration ----------------
# No credentials or network port configs needed for local storage file context
DB_FILE_PATH = "notebooks\cricbuzz_db.db"

def get_conn():
    return sqlite3.connect(DB_FILE_PATH)

# ---------------- Helpers ----------------
def fetch_players():
    conn = get_conn()
    # To mimic MySQL's dictionary cursor layout context, assign custom row factory 
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, full_name FROM players ORDER BY full_name;")
    players = cursor.fetchall()
    cursor.close()
    conn.close()
    return players

def fetch_all_players():
    conn = get_conn()
    # COALESCE remains completely valid syntax structure cross-platform
    df = pd.read_sql("""
        SELECT player_id, full_name,
               COALESCE(playing_role,'—') AS playing_role,
               COALESCE(batting_style,'N/A') AS batting_style,
               COALESCE(bowling_style,'N/A') AS bowling_style,
               COALESCE(total_runs,0) AS total_runs,
               COALESCE(total_wickets,0) AS total_wickets,
               COALESCE(country,'—') AS country
        FROM players
        ORDER BY player_id;
    """, conn)
    conn.close()
    return df

def insert_player(data):
    conn = get_conn()
    cursor = conn.cursor()
    # ❓ Converted placeholders from %s to ?
    cursor.execute("""
        INSERT INTO players
        (player_id, full_name, playing_role, batting_style, bowling_style, total_runs, total_wickets, country)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        data["player_id"], data["full_name"], data.get("playing_role", None),
        data["batting_style"], data["bowling_style"],
        data.get("total_runs",0), data.get("total_wickets",0),
        data.get("country", None)
    ))
    conn.commit()
    cursor.close()
    conn.close()

def update_player(pid, data):
    conn = get_conn()
    cursor = conn.cursor()
    # ❓ Converted placeholders from %s to ?
    cursor.execute("""
        UPDATE players
        SET full_name=?, playing_role=?, batting_style=?, bowling_style=?,
            total_runs=?, total_wickets=?, country=?
        WHERE player_id=?
    """, (
        data["full_name"], data.get("playing_role", None),
        data["batting_style"], data["bowling_style"],
        data.get("total_runs",0), data.get("total_wickets",0),
        data.get("country", None), pid
    ))
    conn.commit()
    cursor.close()
    conn.close()

def delete_player(pid):
    conn = get_conn()
    cursor = conn.cursor()
    # ❓ Converted placeholders from %s to ?
    cursor.execute("DELETE FROM players WHERE player_id=?", (pid,))
    conn.commit()
    cursor.close()
    conn.close()

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="✍️ Cricbuzz CRUD Manager", layout="wide")

# ---------------- Gradient & Styling ----------------
st.markdown("""
<style>
/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
    color: #1f2937;
    font-family: 'Segoe UI', sans-serif;
    padding: 15px;
}

/* Header ribbon */
.header-ribbon {
    text-align:center; padding:16px;
    background:linear-gradient(90deg, #f97316, #facc15);
    color:white; border-radius:10px; margin-bottom:15px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #0ea5e9, #14b8a6) !important;
    color: white !important;
    font-weight: bold;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown("""
<div class="header-ribbon">
    <h1>✍️ Cricbuzz CRUD Manager</h1>
    <p>Add, Update, Delete & View Players from Database</p>
</div>
""", unsafe_allow_html=True)

# Session state
if "last_modified_id" not in st.session_state: st.session_state.last_modified_id = None
if "last_deleted_id" not in st.session_state: st.session_state.last_deleted_id = None

roles = ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper", "Captain", "—"]
batting_styles = ["Right-hand Bat", "Left-hand Bat", "N/A"]
bowling_styles = [
    "Right-arm Fast", "Right-arm Medium", "Right-arm Offbreak",
    "Left-arm Fast", "Left-arm Medium", "Left-arm Orthodox", "Legbreak Googly", "N/A"
]

# ---------------- Tabs ----------------
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add", "✏️ Update", "🗑 Delete", "📊 View"])

# ---------------- Add Player ----------------
with tab1:
    st.markdown("### ➕ Add New Player")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            player_id = st.number_input("Player ID", min_value=1, step=1)
            full_name = st.text_input("Full Name")
            playing_role = st.selectbox("Role", roles)
        with col2:
            batting_style = st.selectbox("Batting Style", batting_styles)
            bowling_style = st.selectbox("Bowling Style", bowling_styles)
            total_runs = st.number_input("Total Runs", min_value=0, step=1)
            total_wickets = st.number_input("Total Wickets", min_value=0, step=1)
            country = st.text_input("Country")
        submit = st.form_submit_button("✅ Add Player")
        if submit:
            if not full_name.strip():
                st.error("⚠️ Full Name is required")
            else:
                insert_player({
                    "player_id": player_id,
                    "full_name": full_name.strip(),
                    "playing_role": playing_role,
                    "batting_style": batting_style,
                    "bowling_style": bowling_style,
                    "total_runs": total_runs,
                    "total_wickets": total_wickets,
                    "country": country.strip() or None
                })
                st.session_state.last_modified_id = player_id
                st.session_state.last_deleted_id = None
                st.success(f"🎉 Player **{full_name}** added successfully")
                st.balloons()

# ---------------- Update Player ----------------
with tab2:
    st.markdown("### ✏️ Update Player")
    players = fetch_players()
    if not players: st.warning("No players found.")
    else:
        pick = st.selectbox("Select Player", players, format_func=lambda x: x['full_name'])
        sel_id = pick["player_id"]
        df = fetch_all_players()
        row = df[df["player_id"] == sel_id].iloc[0]
        with st.form("update_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name", value=row["full_name"])
                playing_role = st.selectbox("Role", roles, index=roles.index(row["playing_role"]) if row["playing_role"] in roles else len(roles)-1)
            with col2:
                batting_style = st.selectbox("Batting Style", batting_styles, index=batting_styles.index(row["batting_style"]) if row["batting_style"] in batting_styles else 2)
                bowling_style = st.selectbox("Bowling Style", bowling_styles, index=bowling_styles.index(row["bowling_style"]) if row["bowling_style"] in bowling_styles else len(bowling_styles)-1)
                total_runs = st.number_input("Total Runs", min_value=0, step=1, value=int(row["total_runs"]))
                total_wickets = st.number_input("Total Wickets", min_value=0, step=1, value=int(row["total_wickets"]))
                country = st.text_input("Country", value=row["country"])
            submit = st.form_submit_button("🔄 Update Player")
            if submit:
                update_player(sel_id, {
                    "full_name": full_name.strip(),
                    "playing_role": playing_role,
                    "batting_style": batting_style,
                    "bowling_style": bowling_style,
                    "total_runs": total_runs,
                    "total_wickets": total_wickets,
                    "country": country.strip() or None
                })
                st.session_state.last_modified_id = sel_id
                st.session_state.last_deleted_id = None
                st.success(f"✅ Player **{full_name}** updated successfully")
                st.balloons()

# ---------------- Delete Player ----------------
with tab3:
    st.markdown("### 🗑 Delete Player")
    players = fetch_players()
    if not players: st.warning("No players to delete.")
    else:
        pick = st.selectbox("Select Player to Delete", players, format_func=lambda x: x['full_name'])
        sel_id = pick["player_id"]
        with st.form("delete_form"):
            st.warning("⚠️ Deletion is permanent!")
            confirm = st.checkbox("Confirm delete?")
            submit = st.form_submit_button("🚨 Delete")
            if submit:
                if not confirm:
                    st.error("Please confirm delete.")
                else:
                    delete_player(sel_id)
                    st.session_state.last_deleted_id = sel_id
                    st.session_state.last_modified_id = None
                    st.success("❌ Player deleted successfully")
                    st.balloons()

# ---------------- View Players ----------------
with tab4:
    st.markdown("### 📊 Player Records")
    df = fetch_all_players()
    search = st.text_input("🔍 Search Player")
    if search: df = df[df["full_name"].str.contains(search, case=False)]

    def highlight_row(x):
        if 'player_id' in x:
            if st.session_state.last_modified_id and x['player_id'] == st.session_state.last_modified_id:
                return ['background-color: #fef08a'] * len(x)
            if st.session_state.last_deleted_id and x['player_id'] == st.session_state.last_deleted_id:
                return ['background-color: #fca5a5'] * len(x)
        return [''] * len(x)

    st.dataframe(df.style.apply(highlight_row, axis=1))
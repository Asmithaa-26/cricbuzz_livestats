import os
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

# ---------------- Page config ----------------
st.set_page_config(page_title="SQL Queries", page_icon="🧠", layout="wide")

# ---------------- Gradient Header ----------------
st.markdown("""
<style>
.sql-header {
    text-align: center;
    padding: 16px;
    background: linear-gradient(90deg, #f59e0b, #ec4899);  /* Orange -> Pink */
    color: white;
    border-radius: 10px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.stButton>button {
    background: linear-gradient(90deg, #0ea5e9, #14b8a6) !important;
    color: white !important;
    font-weight: bold;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    border: none !important;
}
</style>

<div class="sql-header">
    <h1>SQL Queries</h1>
    <p>Run custom or prebuilt SQL queries on your Cricbuzz SQLite database.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Safe Multi-Page Absolute Path Resolution ----------------
CURRENT_DIR = Path(__file__).parent
# If this file is inside your "pages/" folder, go up one level to find the root DB file
PROJECT_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name == "pages" else CURRENT_DIR
SQLITE_DB_PATH = os.path.join(PROJECT_ROOT, "notebooks\cricbuzz_db.db")

# ---------------- Context Connection Manager ----------------
def run_query_safely(sql_statement):
    """Opens a short-lived connection context to eliminate thread locking or early closures."""
    try:
        with sqlite3.connect(SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_statement)
            rows = cursor.fetchall()
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                cursor.close()
                return pd.DataFrame(rows, columns=columns), "DATASET"
            
            cursor.close()
            return None, "COMMAND_SUCCESS"
    except Exception as ex:
        return str(ex), "ERROR"


# ✅ Prebuilt queries thoroughly adjusted for actual pipeline table names
prebuilt_queries = {
    "1. Players who represent India": "SELECT player_id, full_name, playing_role, batting_style, bowling_style FROM players WHERE country = 'India';",
    
    "2. Recent matches": "SELECT match_desc, team1, team2, venue, venue_city, start_date FROM recent_matches ORDER BY start_date DESC LIMIT 10;",
    
    "3. Top 10 ODI run scorers": "SELECT player_id, player_name, runs FROM top_odi_runs ORDER BY runs DESC LIMIT 10;",
    
    "4. Venues with capacity > 30000": "SELECT venue_name, city, country, capacity FROM venues WHERE CAST(capacity AS INTEGER) > 30000 ORDER BY CAST(capacity AS INTEGER) DESC;",
    
    "5. Matches won by each team": "SELECT match_winner, COUNT(*) AS wins FROM combined_matches WHERE match_winner IS NOT NULL AND match_winner <> '' GROUP BY match_winner ORDER BY wins DESC;",
    
    "6. Count of players by role": "SELECT playing_role, COUNT(*) AS player_count FROM players GROUP BY playing_role ORDER BY player_count DESC;",
    
    "7. Highest score per format": """
        SELECT
            cm.format,
            b.player_name,
            b.runs AS score,
            cm.team2 AS opponent
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        JOIN (
            SELECT cm.format AS format, MAX(b.runs) AS max_runs
            FROM batting_data b
            JOIN combined_matches cm ON b.match_id = cm.match_id
            GROUP BY cm.format
        ) AS max_scores
        ON cm.format = max_scores.format AND b.runs = max_scores.max_runs
        ORDER BY score DESC;
    """,
    
    "8. Series started in 2024": """
        SELECT 
            series_name,
            MIN(venue) AS host_venue,
            format AS match_type,
            MIN(match_date) AS start_date,
            COUNT(*) AS total_matches
        FROM combined_matches
        WHERE strftime('%Y', match_date) = '2024'
        GROUP BY series_name, format
        ORDER BY start_date;
    """,
    
    "9. All-rounders with career aggregates": """
        SELECT full_name, country, total_runs, total_wickets 
        FROM players
        WHERE total_runs > 500 OR total_wickets > 20
        ORDER BY total_runs DESC;
    """,
    
    "10. Last 20 completed matches": """
        SELECT 
            match_desc,
            team1,
            team2,
            status,
            venue
        FROM recent_matches
        WHERE status LIKE '%won%' OR status LIKE '%drawn%'
        ORDER BY start_date DESC
        LIMIT 20;
    """,
    
    "11. Player performance across formats": """
        SELECT 
            b.player_id,
            b.player_name,
            SUM(CASE WHEN cm.format = 'Test' THEN b.runs ELSE 0 END) AS test_runs,
            SUM(CASE WHEN cm.format = 'ODI' THEN b.runs ELSE 0 END) AS odi_runs,
            SUM(CASE WHEN cm.format = 'T20' THEN b.runs ELSE 0 END) AS t20_runs,
            ROUND(CAST(SUM(b.runs) AS REAL) / COUNT(DISTINCT b.match_id), 2) AS overall_avg
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        GROUP BY b.player_id, b.player_name
        ORDER BY overall_avg DESC;
    """,
    
    "12. Team Win Margins Breakdown": """
        SELECT 
            match_winner AS team_name,
            COUNT(*) AS total_wins,
            SUM(CASE WHEN win_margin LIKE '%runs%' THEN 1 ELSE 0 END) AS wins_defending,
            SUM(CASE WHEN win_margin LIKE '%wickets%' THEN 1 ELSE 0 END) AS wins_chasing
        FROM combined_matches
        WHERE match_winner IS NOT NULL AND match_winner <> ''
        GROUP BY match_winner
        ORDER BY total_wins DESC;
    """,
    
    "13. Partnerships with 100+ runs": """
        SELECT match_id, innings_no, batter1_name, batter2_name, runs_partnership, balls_faced
        FROM players_partnerships_data
        WHERE CAST(runs_partnership AS INTEGER) >= 100
        ORDER BY CAST(runs_partnership AS INTEGER) DESC;
    """,
    
    "14. Bowling performance at venues": """
        SELECT player_id, player_name, venue, ROUND(AVG(economy_rate), 2) AS avg_economy, SUM(wickets) AS total_wickets, COUNT(*) AS matches_played
        FROM bowlers_bowling_venue_data
        WHERE overs >= 4
        GROUP BY player_id, player_name, venue
        HAVING COUNT(*) >= 1
        ORDER BY total_wickets DESC;
    """,
    
    "15. Player performance in close matches": """
        SELECT 
            b.player_id, b.player_name, ROUND(AVG(b.runs), 2) AS avg_runs, COUNT(*) AS close_matches_played,
            SUM(CASE WHEN b.team = cm.match_winner THEN 1 ELSE 0 END) AS matches_won_by_team
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        WHERE (cm.win_margin LIKE '%10 runs%' OR cm.win_margin LIKE '%1 wicket%' OR cm.win_margin LIKE '%2 wickets%')
        GROUP BY b.player_id, b.player_name
        ORDER BY avg_runs DESC;
    """,
    
    "16. Batting performance by year": """
        SELECT b.player_id, b.player_name, strftime('%Y', cm.match_date) AS year,
               ROUND(AVG(b.runs), 2) AS avg_runs, ROUND(AVG(b.strike_rate), 2) AS avg_sr, COUNT(*) AS matches_played
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        GROUP BY b.player_id, b.player_name, strftime('%Y', cm.match_date)
        ORDER BY year DESC, avg_runs DESC;
    """,
    
    "17. Toss win advantage": """
        SELECT format, toss_decision, COUNT(*) AS total_matches,
               SUM(CASE WHEN toss_winner = match_winner THEN 1 ELSE 0 END) AS toss_win_success,
               ROUND(SUM(CASE WHEN toss_winner = match_winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_pct
        FROM combined_matches
        WHERE toss_decision IS NOT NULL AND toss_decision <> ''
        GROUP BY format, toss_decision
        ORDER BY format, win_pct DESC;
    """,
    
    "18. Most economical bowlers": """
        SELECT player_id, player_name, ROUND(AVG(economy_rate), 2) AS avg_economy, SUM(wickets) AS total_wickets,
               COUNT(*) AS matches_played
        FROM bowling_data
        GROUP BY player_id, player_name
        ORDER BY avg_economy ASC;
    """,
    
    "19. Consistent batsmen (Innings with 10+ balls faced)": """
        SELECT b.player_id, b.player_name, ROUND(AVG(b.runs), 2) AS avg_runs,
               COUNT(*) AS innings_played
        FROM batting_data b
        WHERE b.balls_faced >= 10
        GROUP BY b.player_id, b.player_name
        ORDER BY avg_runs DESC;
    """,
    
    "20. Matches played and batting avg per format": """
        SELECT b.player_id, b.player_name, cm.format, COUNT(*) AS matches_played,
               ROUND(CAST(SUM(b.runs) AS REAL) / NULLIF(SUM(CASE WHEN b.dismissal != 'not out' THEN 1 ELSE 0 END), 0), 2) AS avg_bat
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        GROUP BY b.player_id, b.player_name, cm.format
        ORDER BY b.player_id, cm.format;
    """,
    
    "21. Multi-Dimensional Performance Points ranking": """
        SELECT b.player_id, b.player_name, cm.format, 'Batting' AS dimension,
               (SUM(b.runs) * 0.01 + ROUND(AVG(b.runs), 2) * 0.5) AS score
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        GROUP BY b.player_id, b.player_name, cm.format
        UNION ALL
        SELECT bw.player_id, bw.player_name, cm.format, 'Bowling' AS dimension,
               (SUM(bw.wickets) * 2.5 + (6 - AVG(bw.economy_rate)) * 2) AS score
        FROM bowling_data bw
        JOIN combined_matches cm ON bw.match_id = cm.match_id
        GROUP BY bw.player_id, bw.player_name, cm.format
        ORDER BY score DESC;
    """,
    
    "22. Head-to-head analysis": """
        SELECT m.team1, m.team2, COUNT(*) AS matches_played,
               SUM(CASE WHEN m.match_winner = m.team1 THEN 1 ELSE 0 END) AS team1_wins,
               SUM(CASE WHEN m.match_winner = m.team2 THEN 1 ELSE 0 END) AS team2_wins
        FROM combined_matches m
        GROUP BY m.team1, m.team2
        ORDER BY matches_played DESC;
    """,
    
    "23. Recent form tracking parameters": """
        WITH ranked_stats AS (
            SELECT player_id, player_name, match_id, runs, balls_faced,
                   ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY match_id DESC) AS rn
            FROM batting_data
            WHERE runs IS NOT NULL
        ),
        last_5 AS (SELECT * FROM ranked_stats WHERE rn <= 5)
        SELECT player_id, player_name, ROUND(AVG(runs),2) AS avg_last_5,
               COUNT(CASE WHEN runs >= 50 THEN 1 END) AS fifties_last_5
        FROM last_5
        GROUP BY player_id, player_name
        ORDER BY avg_last_5 DESC;
    """,
    
    "24. Best partnership pairs": """
        SELECT 
               CASE WHEN batter1_name < batter2_name THEN batter1_name ELSE batter2_name END AS player1, 
               CASE WHEN batter1_name > batter2_name THEN batter1_name ELSE batter2_name END AS player2,
               ROUND(AVG(CAST(runs_partnership AS INTEGER)),2) AS avg_runs,
               MAX(CAST(runs_partnership AS INTEGER)) AS highest_partnership,
               COUNT(*) AS total_partnerships
        FROM players_partnerships_data
        GROUP BY player1, player2
        ORDER BY total_partnerships DESC;
    """,
    
    "25. Time-series batting evolution trends": """
        SELECT b.player_id, b.player_name, strftime('%Y', cm.match_date) AS running_year,
               AVG(b.runs) AS yearly_avg, COUNT(*) AS matches_played
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        GROUP BY b.player_id, b.player_name, running_year
        ORDER BY b.player_id, running_year ASC;
    """
}

# ----------- Dropdown for prebuilt queries -----------
selected_query = st.selectbox("📂 Choose a prebuilt SQL query:", ["-- Select a query --"] + list(prebuilt_queries.keys()))

# ----------- Run execution routing -----------
if st.button("Run Query"):
    if selected_query != "-- Select a query --":
        query_to_run = prebuilt_queries[selected_query]
        
        # Call encapsulated execution block
        result, result_type = run_query_safely(query_to_run)
        
        if result_type == "DATASET":
            if not result.empty:
                st.success(f"✅ Query executed successfully. {len(result)} rows returned.")
                # Fixed: Changed parameter from use_container_width=True to width="stretch"
                st.dataframe(result, width="stretch")
            else:
                st.info("✅ Query executed, but no matching records were found in the database.")
                
        elif result_type == "COMMAND_SUCCESS":
            st.success("✅ Query executed successfully (Database state modified or structural command complete).")
            
        elif result_type == "ERROR":
            st.error(f"❌ Error executing query: {result}")
            st.info(f"💡 Expected Database Location: `{SQLITE_DB_PATH}`")
    else:
        st.warning("Please select a valid query from the dropdown before clicking Run.")
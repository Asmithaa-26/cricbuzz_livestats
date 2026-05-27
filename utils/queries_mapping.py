PREDEFINED_QUERIES = {

    # ---------------BEGINNER------------------
    "Q1. Players who represent India": """
        SELECT player_id, full_name, batting_style, bowling_style
        FROM players
        WHERE country = 'India';
    """,

    "Q2. Recent matches": """
        SELECT match_desc, team1, team2, venue, venue_city, start_date
        FROM recent_matches
        ORDER BY start_date DESC
        LIMIT 10;
    """,

    "Q3. Top 10 ODI run scorers": """
        SELECT player_id, player_name, runs
        FROM top_odi_runs
        ORDER BY runs DESC
        LIMIT 10;
    """,

    "Q4. Venues with capacity > 30000": """
        SELECT venue_name, city, country, capacity
        FROM venues
        WHERE capacity > 30000
        ORDER BY capacity DESC;
    """,

    "Q5. Matches won by each team": """
        SELECT match_winner, COUNT(*) AS wins
        FROM combined_matches
        WHERE match_winner IS NOT NULL AND match_winner <> ''
        GROUP BY match_winner
        ORDER BY wins DESC;
    """,

    "Q6. Count of players by role": """
        SELECT playing_role, COUNT(*) AS player_count
        FROM players
        GROUP BY playing_role
        ORDER BY player_count DESC;
    """,

    "Q7. Highest score per format": """
        SELECT
            cm.format,
            bbd.player_name,
            bbd.runs AS score,
            cm.team2 AS opponent
        FROM batters_batting_data bbd
        JOIN combined_matches cm ON bbd.match_id = cm.match_id
        JOIN (
            SELECT cm.format AS format, MAX(bbd.runs) AS max_runs
            FROM batters_batting_data bbd
            JOIN combined_matches cm ON bbd.match_id = cm.match_id
            GROUP BY cm.format
        ) AS max_scores
        ON cm.format = max_scores.format AND bbd.runs = max_scores.max_runs
        ORDER BY score DESC;
    """,

    "Q8. Series started in 2024": """
        SELECT 
          series_name,
          MIN(venue) AS host_country,
          format AS match_type,
          MIN(match_date) AS start_date,
          COUNT(*) AS total_matches
        FROM combined_matches
        WHERE strftime('%Y', match_date) = '2024'
        GROUP BY series_name, format
        ORDER BY start_date;
    """,

    # -----------INTERMEDIATE----------------
    "Q9. All-rounders with >1000 runs and >50 wickets": """
        SELECT 
          full_name,
          total_runs,
          total_wickets,
          'Career' AS format
        FROM players
        WHERE total_runs > 1000 AND total_wickets > 50
        ORDER BY total_runs DESC;
    """,

    "Q10. Last 20 completed matches": """
        SELECT 
          match_desc,
          team1,
          team2,
          status AS winner_team_name,
          CASE
            WHEN status LIKE '%won by%' THEN 'Check Details'
            ELSE NULL
          END AS winning_margin,
          CASE
            WHEN status LIKE '%won by%' AND status LIKE '%wkts%' THEN 'Wickets'
            WHEN status LIKE '%won by%' AND status LIKE '%runs%' THEN 'Runs'
            ELSE 'N/A'
          END AS victory_type,
          venue
        FROM recent_matches
        WHERE status LIKE '%won by%'
        ORDER BY start_date DESC
        LIMIT 20;
    """,

    "Q11. Player performance across formats": """
        SELECT 
          b.player_id,
          SUM(CASE WHEN cm.format = 'Test' THEN b.runs ELSE 0 END) AS test_runs,
          SUM(CASE WHEN cm.format = 'ODI' THEN b.runs ELSE 0 END) AS odi_runs,
          SUM(CASE WHEN cm.format = 'T20I' THEN b.runs ELSE 0 END) AS t20i_runs,
          ROUND(SUM(b.runs) * 1.0 / COUNT(DISTINCT b.match_id), 2) AS overall_avg
        FROM batters_batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        GROUP BY b.player_id
        HAVING COUNT(DISTINCT cm.format) >= 2
        ORDER BY overall_avg DESC;
    """,

    "Q12. Home vs Away wins": """
        SELECT 
          cm.match_winner AS team_name,
          SUM(CASE WHEN t.country = v.country THEN 1 ELSE 0 END) AS home_wins,
          SUM(CASE WHEN t.country <> v.country THEN 1 ELSE 0 END) AS away_wins
        FROM combined_matches cm
        JOIN team_country_map t ON cm.match_winner = t.team_name
        JOIN venue_country_map v ON cm.venue = v.venue
        WHERE cm.match_winner IS NOT NULL
        GROUP BY cm.match_winner
        ORDER BY away_wins DESC;
    """,

    "Q13. Partnerships with 100+ runs": """
        SELECT 
          batter1_name,
          batter2_name,
          runs_partnership,
          innings_no,
          match_id
        FROM players_partnerships_data
        WHERE runs_partnership >= 100
          AND wicket_fallen BETWEEN 1 AND 9
        ORDER BY runs_partnership DESC;
    """,

    "Q14. Bowling performance at venues": """
        SELECT 
          player_id,
          player_name,
          venue,
          AVG(economy_rate) AS avg_economy,
          SUM(wickets) AS total_wickets,
          COUNT(*) AS matches_played
        FROM bowlers_bowling_venue_data
        WHERE overs >= 4
        GROUP BY player_id, player_name, venue
        HAVING COUNT(*) >= 3
        ORDER BY total_wickets DESC;
    """,

    "Q15. Player performance in close matches": """
        SELECT 
          b.player_id,
          b.player_name,
          AVG(b.runs) AS avg_runs,
          COUNT(*) AS close_matches_played,
          SUM(CASE WHEN b.team = cm.match_winner THEN 1 ELSE 0 END) AS matches_won_by_team
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        WHERE (
            (cm.win_margin LIKE '%runs' AND CAST(cm.win_margin AS INT) < 50)
            OR
            (cm.win_margin LIKE '%wickets' AND CAST(cm.win_margin AS INT) < 5)
        )
        GROUP BY b.player_id, b.player_name
        ORDER BY avg_runs DESC;
    """,

    # ----------INTERMEDIATE / ADVANCED----------
    "Q16. Batting performance by year": """
        SELECT 
          b.player_id,
          b.player_name,
          strftime('%Y', cm.match_date) AS year,
          AVG(b.runs) AS avg_runs,
          AVG(b.strike_rate) AS avg_sr,
          COUNT(*) AS matches_played
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        WHERE cm.match_date >= '2020-01-01'
        GROUP BY b.player_id, b.player_name, strftime('%Y', cm.match_date)
        HAVING COUNT(*) >= 5
        ORDER BY year, avg_runs DESC;
    """,

    "Q17. Toss win advantage": """
        SELECT 
          format,
          toss_decision,
          COUNT(*) AS total_matches,
          SUM(CASE WHEN toss_winner = match_winner THEN 1 ELSE 0 END) AS toss_win_success,
          ROUND(SUM(CASE WHEN toss_winner = match_winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_pct
        FROM combined_matches
        WHERE toss_decision IS NOT NULL
        GROUP BY format, toss_decision
        ORDER BY format, win_pct DESC;
    """,

    "Q18. Most economical bowlers (ODI + T20)": """
        SELECT 
          player_id,
          player_name,
          ROUND(AVG(economy_rate), 2) AS avg_economy,
          SUM(wickets) AS total_wickets,
          COUNT(*) AS matches_played,
          ROUND(SUM(overs) * 1.0 / COUNT(*), 2) AS avg_overs_per_match
        FROM bowling_data
        WHERE match_id IN (
            SELECT match_id FROM combined_matches
            WHERE LOWER(format) IN ('odi', 't20')
        )
        GROUP BY player_id, player_name
        HAVING matches_played >= 10 AND avg_overs_per_match >= 2
        ORDER BY avg_economy ASC;
    """,

    "Q19. Consistent batsmen": """
        SELECT 
          b.player_id,
          b.player_name,
          ROUND(AVG(b.runs), 2) AS avg_runs,
          ROUND(SQRT((SUM(b.runs * b.runs) - (SUM(b.runs) * SUM(b.runs) / COUNT(*))) / COUNT(*)), 2) AS run_stddev,
          COUNT(*) AS innings_played
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        WHERE b.balls_faced >= 10 AND cm.match_date >= '2022-01-01'
        GROUP BY b.player_id, b.player_name
        HAVING innings_played >= 5
        ORDER BY run_stddev ASC, avg_runs DESC;
    """,

    "Q20. Matches played and batting avg per format": """
        WITH player_totals AS (
          SELECT player_id, COUNT(*) AS total_matches
          FROM batting_data
          GROUP BY player_id
          HAVING total_matches >= 20
        )
        SELECT 
          b.player_id,
          cm.format,
          COUNT(*) AS matches_played,
          ROUND(SUM(b.runs) * 1.0 / NULLIF(SUM(CASE WHEN b.dismissal != 'not out' THEN 1 ELSE 0 END), 0), 2) AS avg_bat
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        JOIN player_totals pt ON b.player_id = pt.player_id
        GROUP BY b.player_id, cm.format
        ORDER BY b.player_id, cm.format;
    """,

    "Q21. Performance ranking": """
        /* Batting score */
        SELECT 
          b.player_id,
          cm.format,
          (SUM(b.runs) * 0.01 +
           (SUM(b.runs) * 1.0 / NULLIF(SUM(CASE WHEN b.dismissal != 'not out' THEN 1 ELSE 0 END), 0)) * 0.5 +
           (SUM(b.runs) * 100.0 / NULLIF(SUM(b.balls_faced), 0)) * 0.3) AS score
        FROM batting_data b
        JOIN combined_matches cm ON b.match_id = cm.match_id
        GROUP BY b.player_id, cm.format

        UNION ALL

        /* Bowling score */
        SELECT 
          bw.player_id,
          cm.format,
          (SUM(bw.wickets) * 2 +
           (50 - (SUM(bw.runs_conceded) * 1.0 / NULLIF(SUM(bw.wickets), 0))) * 0.5 +
           (6 - (SUM(bw.runs_conceded) * 1.0 / NULLIF(SUM(bw.overs), 0))) * 2) AS score
        FROM bowling_data bw
        JOIN combined_matches cm ON bw.match_id = cm.match_id
        GROUP BY bw.player_id, cm.format

        UNION ALL

        /* Fielding score */
        SELECT 
          f.player_id,
          cm.format,
          (SUM(f.catches) * 1 + SUM(f.stumpings) * 2) AS score
        FROM fielding_data_two f
        JOIN combined_matches cm ON f.match_id = cm.match_id
        GROUP BY f.player_id, cm.format;
    """,

    "Q22. Head-to-head analysis": """
        SELECT 
          m.team1,
          m.team2,
          COUNT(*) AS matches_played,
          SUM(CASE WHEN m.match_winner = m.team1 THEN 1 ELSE 0 END) AS team1_wins,
          SUM(CASE WHEN m.match_winner = m.team2 THEN 1 ELSE 0 END) AS team2_wins,
          ROUND(AVG(CASE WHEN m.match_winner = m.team1 THEN CAST(m.win_margin AS INT) ELSE NULL END), 2) AS avg_margin_team1,
          ROUND(AVG(CASE WHEN m.match_winner = m.team2 THEN CAST(m.win_margin AS INT) ELSE NULL END), 2) AS avg_margin_team2,
          ROUND(SUM(CASE WHEN m.match_winner = m.team1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS team1_win_pct,
          ROUND(SUM(CASE WHEN m.match_winner = m.team2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS team2_win_pct
        FROM combined_matches m
        WHERE m.match_date >= date('now', '-3 years')
        GROUP BY m.team1, m.team2
        HAVING matches_played >= 5
        ORDER BY matches_played DESC, team1_win_pct DESC
        LIMIT 1000;
    """,

    "Q23. Recent form": """
        WITH ranked_stats AS (
          SELECT 
            player_id,
            match_id,
            runs,
            balls_faced,
            ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY match_id DESC) AS rn
          FROM batting_data
          WHERE runs IS NOT NULL
        ),
        last_10 AS (
          SELECT * FROM ranked_stats WHERE rn <= 10
        ),
        last_5 AS (
          SELECT * FROM ranked_stats WHERE rn <= 5
        ),
        stats_10 AS (
          SELECT 
            player_id,
            ROUND(AVG(runs), 2) AS avg_last_10,
            ROUND(AVG(runs * 100.0 / NULLIF(balls_faced, 0)), 2) AS strike_rate_10,
            COUNT(CASE WHEN runs >= 50 THEN 1 END) AS fifties_10,
            ROUND(SQRT((SUM(runs * runs) - (SUM(runs) * SUM(runs) / COUNT(*))) / COUNT(*)), 2) AS consistency_score
          FROM last_10
          GROUP BY player_id
        ),
        stats_5 AS (
          SELECT 
            player_id,
            ROUND(AVG(runs), 2) AS avg_last_5
          FROM last_5
          GROUP BY player_id
        )
        SELECT 
          s10.player_id,
          s5.avg_last_5,
          s10.avg_last_10,
          s10.strike_rate_10,
          s10.fifties_10,
          s10.consistency_score,
          CASE
            WHEN s10.avg_last_10 >= 50 AND s10.consistency_score <= 15 THEN 'Excellent Form'
            WHEN s10.avg_last_10 >= 35 THEN 'Good Form'
            WHEN s10.avg_last_10 >= 20 THEN 'Average Form'
            ELSE 'Poor Form'
          END AS form_category
        FROM stats_10 s10
        JOIN stats_5 s5 ON s10.player_id = s5.player_id
        ORDER BY s10.avg_last_10 DESC;
    """,

    "Q24. Best partnerships": """
        SELECT 
          CASE WHEN batter1_name < batter2_name THEN batter1_name ELSE batter2_name END AS player1,
          CASE WHEN batter1_name > batter2_name THEN batter1_name ELSE batter2_name END AS player2,
          ROUND(AVG(runs_partnership), 2) AS avg_runs,
          COUNT(CASE WHEN runs_partnership > 50 THEN 1 END) AS fifty_plus,
          MAX(runs_partnership) AS highest,
          ROUND(COUNT(CASE WHEN runs_partnership > 50 THEN 1 END) * 100.0 / COUNT(*), 2) AS success_rate,
          COUNT(*) AS total_partnerships
        FROM players_partnerships_data
        GROUP BY 
          CASE WHEN batter1_id < batter2_id THEN batter1_id ELSE batter2_id END,
          CASE WHEN batter1_id > batter2_id THEN batter1_id ELSE batter2_id END,
          CASE WHEN batter1_name < batter2_name THEN batter1_name ELSE batter2_name END,
          CASE WHEN batter1_name > batter2_name THEN batter1_name ELSE batter2_name END
        ORDER BY total_partnerships DESC
        LIMIT 100;
    """,

    "Q25. Time-series performance evolution": """
        WITH player_quarter_stats AS (
          SELECT 
            player_id,
            CAST(strftime('%Y', date) AS INT) AS year,
            CASE 
              WHEN strftime('%m', date) BETWEEN '01' AND '03' THEN 1
              WHEN strftime('%m', date) BETWEEN '04' AND '06' THEN 2
              WHEN strftime('%m', date) BETWEEN '07' AND '09' THEN 3
              ELSE 4
            END AS quarter,
            AVG(runs) AS avg_runs,
            AVG(strike_rate) AS avg_sr,
            COUNT(*) AS matches_played
          FROM batters_batting_data
          GROUP BY player_id, year, quarter
          HAVING COUNT(*) >= 1
        ),
        eligible_players AS (
          SELECT player_id
          FROM player_quarter_stats
          GROUP BY player_id
          HAVING COUNT(*) >= 6
        ),
        player_trends AS (
          SELECT 
            p1.player_id,
            (p1.year || '-Q' || p1.quarter) AS current_qtr,
            p1.avg_runs AS current_runs,
            p1.avg_sr AS current_sr,
            (p2.year || '-Q' || p2.quarter) AS prev_qtr,
            p2.avg_runs AS prev_runs,
            p2.avg_sr AS prev_sr,
            CASE 
              WHEN p1.avg_runs > p2.avg_runs AND p1.avg_sr > p2.avg_sr THEN 'Improving'
              WHEN p1.avg_runs < p2.avg_runs AND p1.avg_sr < p2.avg_sr THEN 'Declining'
              ELSE 'Stable'
            END AS performance_trend
          FROM player_quarter_stats p1
          JOIN player_quarter_stats p2 
            ON p1.player_id = p2.player_id 
            AND (
              (p1.year = p2.year AND p1.quarter = p2.quarter + 1) OR
              (p1.year = p2.year + 1 AND p1.quarter = 1 AND p2.quarter = 4)
            )
          WHERE p1.player_id IN (SELECT player_id FROM eligible_players)
        )
        SELECT 
          b.player_name,
          pt.player_id,
          COUNT(*) AS transitions,
          SUM(CASE WHEN pt.performance_trend = 'Improving' THEN 1 ELSE 0 END) AS improving_count,
          SUM(CASE WHEN pt.performance_trend = 'Declining' THEN 1 ELSE 0 END) AS declining_count,
          SUM(CASE WHEN pt.performance_trend = 'Stable' THEN 1 ELSE 0 END) AS stable_count,
          CASE 
            WHEN SUM(CASE WHEN pt.performance_trend = 'Improving' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) >= 0.6 THEN 'Career Ascending'
            WHEN SUM(CASE WHEN pt.performance_trend = 'Declining' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) >= 0.6 THEN 'Career Declining'
            ELSE 'Career Stable'
          END AS career_phase
        FROM player_trends pt
        JOIN batters_batting_data b ON pt.player_id = b.player_id
        GROUP BY pt.player_id, b.player_name;
    """,
}
import sqlite3
c = sqlite3.connect('football_trivia.db').cursor()
oldest_player = c.execute("SELECT known_as, birth_date FROM players WHERE birth_date IS NOT NULL AND birth_date != '' AND birth_date != 'None' ORDER BY birth_date ASC LIMIT 1").fetchone()
print(f"Oldest player: {oldest_player}")
sample_history = c.execute("SELECT start_year, end_year FROM player_team_history LIMIT 5").fetchall()
print(f"Sample history: {sample_history}")
earliest_year = c.execute("SELECT start_year, end_year FROM player_team_history WHERE start_year IS NOT NULL AND start_year != '' AND start_year != 'None' ORDER BY CAST(start_year AS INTEGER) ASC LIMIT 1").fetchone()
print(f"Earliest history: {earliest_year}")

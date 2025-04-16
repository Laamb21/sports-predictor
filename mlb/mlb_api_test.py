'''
File to test MLB-StatAPI Python wrapper
'''

import statsapi
import pandas as pd

# Get today's schedule - includes live, upcoming, and completed games
games_today = statsapi.schedule(date=None, sportId=1)

# DataFrame for easy viewing
df = pd.DataFrame(games_today)
print(df[['game_id', 'game_datetime', 'home_name', 'away_name', 'status']])

# Filter for live games
live_games = [game for game in games_today if game['status'] in ('In Progress')]
print("\nLive Games:")
for game in live_games:
    print(f"{game['away_name']} at {game['home_name']} - {game['status']} @ {game['game_datetime']}")

# Get live game data
if live_games:
    game_id = live_games[0]['game_id']
    live_feed = statsapi.get('game', {'gamePk': game_id})

    # Get current inning and score
    teams = live_feed['liveData']['boxscore']['teams']
    current_inning = live_feed['liveData']['linescore']['currentInning']
    home_team = teams['home']['team']['name']
    away_team = teams['away']['team']['name']
    home_score = teams['home']['teamStats']['batting']['runs']
    away_score = teams['away']['teamStats']['batting']['runs']

    print(f"\n{away_team} {away_score} - {home_team} {home_score} (Inning {current_inning})")



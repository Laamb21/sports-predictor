import statsapi

# Get today's schedule
games_today = statsapi.schedule(date=None, sportId=1)

# Filter to games that are live or upcoming
live_upcoming_games = [game for game in games_today if game['status'] in ('Pre-Game', 'In Progress')]

print("Live or Upcoming MLB Games:\n")

for game in live_upcoming_games:
    game_id = game['game_id']
    home_team = game['home_name']
    away_team = game['away_name']
    status = game['status']

    try:
        live_feed = statsapi.get('game', {'gamePk': game_id})
        linescore = live_feed['liveData'].get('linescore', {})
        inning = linescore.get('currentInning', 'N/A')

        boxscore = live_feed['liveData'].get('boxscore', {})
        home_score = boxscore['teams']['home']['teamStats']['batting'].get('runs', 'N/A')
        away_score = boxscore['teams']['away']['teamStats']['batting'].get('runs', 'N/A')

        print(f"{away_team} {away_score} - {home_team} {home_score} (Inning: {inning}, Status: {status})")

    except Exception as e:
        print(f"Failed to fetch game data for {away_team} vs {home_team}: {e}")

import statsapi
from datetime import datetime, timedelta
from team_stats import get_team_stats
from pitcher_stats import get_pitcher_stats

'''
Broken weather logic 

# Helper function to get weather using python-weather
async def get_weather_forecast(city_name):
    try:
        async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
            weather = await client.get(city_name)
            hourly_forecasts = weather.hourly_forecasts[:24]
            return [
                {
                    'time': h.date.strftime("%Y-%m-%d %H:%M:%S"),
                    'temperature': h.temperature,
                    'sky_text': h.sky_text
                } 
                for h in hourly_forecasts
            ]
    except Exception as e:
        print(f"Weather error for {city_name}: {e}")
        return []
    
def extract_weather_for_game(hourly_forecast, game_datetime):
    game_hour = game_datetime.strftime("%Y-%M-%d %H:00:00")
    for forecast in hourly_forecast:
        if forecast['time'].startswith(game_hour[:13]):
            return {
                'temperature': forecast['temperature'],
                'sky_text': forecast['sky_text']
            }
    return {'temperature': None, 'sky_text': None}


'''

def get_games_for_dates(dates):
    all_games = []
    for date in dates:
        schedule = statsapi.schedule(start_date=date, end_date=date)
        for game in schedule:
            raw_time = game.get('game_datetime')
            game_time_obj = None
            if raw_time:
                try:
                    game_time_obj = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%SZ")
                except Exception as e:
                    print(f"Could not parse game time: {raw_time} - {e}")

            game_data = {
                'date': date,
                'home_team': game['home_name'],
                'away_team': game['away_name'],
                'home_pitcher': game.get('home_probable_pitcher'),
                'away_pitcher': game.get('away_probable_pitcher'),
                'game_time': game_time_obj
            }
            all_games.append(game_data)
    return all_games

def build_game_features(games):
    features = []

    for game in games:
        print(f"Processing: {game['away_team']} at {game['home_team']} on {game['date']}")

        # Get team stats
        home_stats = get_team_stats(game['home_team'])
        away_stats = get_team_stats(game['away_team'])

        # Get pitcher stats
        home_pitcher_stats = get_pitcher_stats(game['home_pitcher'] if game['home_pitcher'] != 'TBD' else {})
        away_pitcher_stats = get_pitcher_stats(game['away_pitcher'] if game['away_pitcher'] != 'TBD' else {})

        '''
        # Get weather forecast using home team city
        weather_forecast = asyncio.run(get_weather_forecast(game['home_team']))
        weather_data = extract_weather_for_game(weather_forecast, game['game_time']) if game['game_time'] else {}
        '''
        weather_data = {'temperature': None, 'sky_text': None}
        

        game_feature = {
            'date': game['date'],
            'home_team': home_stats.get('Team', game['home_team']),
            'away_team': away_stats.get('Team', game['away_team']),
            'home_win_pct': home_stats.get('Win %'),
            'away_win_pct': away_stats.get('Win %'),
            'home_batting_avg': home_stats.get('Batting Avg (last 5 games)'),
            'away_batting_avg': away_stats.get('Batting Avg (last 5 games)'),
            'home_runs_5g': home_stats.get('Runs Scored (last 5 games)'),
            'away_runs_5g': away_stats.get('Runs Scored (last 5 games)'),
            'home_team_era': home_stats.get('ERA (last 5 games)'),
            'away_team_era': away_stats.get('ERA (last 5 games)'),
            'home_pitcher': game['home_pitcher'],
            'away_pitcher': game['away_pitcher'],
            'home_pitcher_era': home_pitcher_stats.get('ERA'),
            'away_pitcher_era': away_pitcher_stats.get('ERA'),
            'home_pitcher_k_per_9': home_pitcher_stats.get('K/9'),
            'away_pitcher_k_per_9': away_pitcher_stats.get('K/9'),
            'home_pitcher_last3_era': home_pitcher_stats.get('Last 3 ERA'),
            'away_pitcher_last3_era': away_pitcher_stats.get('Last 3 ERA'),
            'weather_temperature': None,
            'weather_conditions': None
        }
        features.append(game_feature)

    return features

if __name__ == "__main__":
    target_dates = ['04/18/2025', '04/18/2025']
    games = get_games_for_dates(target_dates)
    game_features = build_game_features(games)

    for game in games:
        print(game)

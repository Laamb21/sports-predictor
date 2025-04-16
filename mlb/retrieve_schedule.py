import statsapi
from datetime import datetime
import pytz

def get_mlb_schedule(date_str=None):
    '''
    Fetches MLB games schedules for a given date

    Args:
        date_str (str): Date in the format 'MM/DD/YYYY'. If None, defaults to todays date.

    Returns:
        List of dictionaries containing game information.
    '''

    if not date_str:
        date_str = datetime.today().strftime('%m/%d/%Y')

    try:
        schedule = statsapi.schedule(start_date=date_str, end_date=date_str)
        if not schedule:
            print(f"No games scheduled for {date_str}.")
            return []

        print(f"\nMLB Games on {date_str}:\n")
        for game in schedule:
            game_time_utc = datetime.strptime(game['game_datetime'], '%Y-%m-%dT%H:%M:%SZ')
            timezone = 'US/Eastern'  # Define a default timezone
            local_time = game_time_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))
            formatted_time = local_time.strftime('%I:%M %p %Z')
            away_pitcher = game.get('away_probable_pitcher')
            home_pitcher = game.get('home_probable_pitcher')
            print(f"{game['away_name']} ({away_pitcher}) at {game['home_name']} ({home_pitcher}) - {formatted_time}\n")

        return schedule
    
    except Exception as e:
        print(f"An error occured: {e}")
        return []
    
if __name__ == "__main__":
    user_input = input("Enter a date (MM/DD/YYYY) or press Enter for today: ").strip()
    get_mlb_schedule(user_input if user_input else None)
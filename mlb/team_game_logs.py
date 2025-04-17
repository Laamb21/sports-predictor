import requests
from collections import defaultdict

def get_team_game_logs(team_id, season=2025, game_type='R', recent_games=5):
    """
    Returns a list of dictionaries with both batting and pitching stats grouped by game date.
    """
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/stats"
    params = {
        "stats": "gameLog",
        "group": "hitting,pitching",
        "season": season,
        "gameType": game_type
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch game logs for team {team_id}. Status: {response.status_code}")
        return []

    data = response.json()
    raw_splits = data.get('stats', [])

    # Organize into a dict by game date
    grouped_logs = defaultdict(dict)
    for group in raw_splits:
        stat_type = group['group']['displayName'].lower()  # "hitting" or "pitching"
        for split in group['splits']:
            date = split['date']
            grouped_logs[date][stat_type] = split['stat']

    # Get most recent games (sorted by date descending)
    sorted_games = sorted(grouped_logs.items(), reverse=True)
    return [entry[1] for entry in sorted_games[:recent_games]]

import statsapi

def get_pitcher_stats(pitcher_name):
    player = statsapi.lookup_player(pitcher_name)
    if not player:
        return None
    
    player_id = player[0]['id']
    stat_data = statsapi.player_stat_data(player_id, group='pitching', type='season')
    pitching_stats = stat_data.get('stats', [])

    if not pitching_stats or 'stats' not in pitching_stats[0]:
        print(f'No season stats available for {pitcher_name}')

    stats = pitching_stats[0]['stats']

    return {
        'Name': pitcher_name,
        'ERA': stats.get('era'),
        'WHIP': stats.get('whip'),
        'Strikeouts': stats.get('strikeOuts'),
        'Walks': stats.get('baseOnBalls'),
        'Innings Pitched': stats.get('inningsPitched'),
        'Games Started': stats.get('gamesStarted')
    }

# Example Usage:
stats = get_pitcher_stats("Corbin Burnes")
print(stats)
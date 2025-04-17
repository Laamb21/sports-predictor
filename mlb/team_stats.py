import statsapi
from datetime import datetime
from team_game_logs import get_team_game_logs

def get_team_stats(team_name, season=None, recent_games=5):
    team = statsapi.lookup_team(team_name)
    if not team:
        print(f"No team found for: {team_name}")
        return None
    team_id = team[0]['id']

    if season is None:
        season = datetime.now().year

    # Get standings info
    standings = statsapi.standings_data(leagueId="103,104", division="all", season=season)
    team_info = None
    for division_data in standings.values():
        for t in division_data['teams']:
            if t.get('team_id') == team_id:
                team_info = t
                break
        if team_info:
            break

    if not team_info:
        print(f"Could not find standings info for {team_name}")
        return None

    try:
        wins = int(team_info.get('w', 0))
        losses = int(team_info.get('l', 0))
        win_pct = round(wins / (wins + losses), 3) if (wins + losses) > 0 else 'N/A'
    except:
        win_pct = 'N/A'

    # ⬇️ Pull recent game logs
    game_logs = get_team_game_logs(team_id=team_id, season=season)
    recent_logs = game_logs[:recent_games]

    total_hits = 0
    total_at_bats = 0
    total_runs = 0
    total_earned_runs = 0
    total_innings_pitched = 0.0

    for game in recent_logs:
        hitting = game.get('hitting', {})
        pitching = game.get('pitching', {})

        total_hits += int(hitting.get('hits', 0))
        total_at_bats += int(hitting.get('atBats', 0))
        total_runs += int(hitting.get('runs', 0))

        total_earned_runs += float(pitching.get('earnedRuns', 0))
        ip = pitching.get('inningsPitched', '0.0')
        if '.' in ip:
            whole, fraction = map(int, ip.split('.'))
            ip_float = whole + (fraction * (1/3))
        else:
            ip_float = float(ip)
        total_innings_pitched += ip_float

    batting_avg = round(total_hits / total_at_bats, 3) if total_at_bats > 0 else 'N/A'
    era = round((total_earned_runs * 9) / total_innings_pitched, 2) if total_innings_pitched > 0 else 'N/A'



    return {
        'Team': team_info.get('team_name', team_name),
        'Wins': wins,
        'Losses': losses,
        'Win %': win_pct,
        'Batting Avg (last 5 games)': batting_avg,
        'Runs Scored (last 5 games)': total_runs,
        'ERA (last 5 games)': era,
    }

# Example usage
if __name__ == "__main__":
    stats = get_team_stats("Baltimore Orioles")
    if stats:
        for k, v in stats.items():
            print(f"{k}: {v}")

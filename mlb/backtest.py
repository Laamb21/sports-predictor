from generate_game_features import get_games_for_dates, build_game_features
from predict_winners import score_team
import statsapi
from datetime import datetime, timedelta

# Hard-coded date range for back-testing
START_DATE = "04/01/2025"
END_DATE   = "04/25/2025"


def get_team_id(team_name: str) -> int:
    """
    Look up the MLB team ID for a given team name using statsapi.lookup_team.
    """
    teams = statsapi.lookup_team(team_name)
    if isinstance(teams, list) and teams:
        return teams[0].get('id')
    if isinstance(teams, dict) and teams.get('id'):
        return teams.get('id')
    raise ValueError(f"Team ID not found for '{team_name}'")


def get_historical_team_stats(team_name: str, as_of_date: str) -> dict:
    """
    Calculate team stats (win percentage) up to as_of_date by fetching all games
    from season start to the given date.
    """
    # Parse as_of_date and convert to ISO
    date_obj = datetime.strptime(as_of_date, "%m/%d/%Y")
    year = date_obj.year
    season_start = f"{year}-03-01"
    end_iso = date_obj.strftime("%Y-%m-%d")

    # Look up team ID and fetch games up to as_of_date
    team_id = get_team_id(team_name)
    sched = statsapi.schedule(
        start_date=season_start,
        end_date=end_iso,
        team=team_id
    )

    wins, games = 0, 0
    for game in sched:
        # Determine if this team was home or away
        if game['home_name'] == team_name:
            scored, allowed = game['home_score'], game['away_score']
        else:
            scored, allowed = game['away_score'], game['home_score']
        if scored > allowed:
            wins += 1
        games += 1

    win_pct = wins / games if games else 0.0
    return {'win_pct': win_pct}


def get_historical_pitcher_stats(pitcher_name: str, as_of_date: str) -> dict:
    """
    Placeholder: currently returns latest cumulative stats. For full historical accuracy,
    implement filtering of game logs up to as_of_date.
    """
    from pitcher_stats import get_pitcher_stats
    return get_pitcher_stats(pitcher_name)


def run_backtest(start_date: str, end_date: str):
    # Build a list of dates between start_date and end_date (inclusive)
    start = datetime.strptime(start_date, "%m/%d/%Y")
    end   = datetime.strptime(end_date,   "%m/%d/%Y")
    days  = (end - start).days
    dates = [
        (start + timedelta(days=i)).strftime("%m/%d/%Y")
        for i in range(days + 1)
    ]

    all_preds = []
    for date in dates:
        # Convert date to ISO for API calls
        date_obj = datetime.strptime(date, "%m/%d/%Y")
        iso_date = date_obj.strftime("%Y-%m-%d")

        # 1) Fetch matchups and build features
        games    = get_games_for_dates([date])
        features = build_game_features(games)

        # 2) Fetch actual results for this date
        schedule = statsapi.schedule(
            start_date=iso_date, end_date=iso_date
        )

        for game in features:
            # Historical stats as of this date
            h_stats = get_historical_team_stats(game['home_team'], date)
            a_stats = get_historical_team_stats(game['away_team'], date)

            h_pitch = get_historical_pitcher_stats(game['home_pitcher'], date)
            a_pitch = get_historical_pitcher_stats(game['away_pitcher'], date)

            # Score using existing heuristic
            h_score = score_team(h_stats, h_pitch, a_pitch.get('ERA', 0))
            a_score = score_team(a_stats, a_pitch, h_pitch.get('ERA', 0))
            pick    = game['home_team'] if h_score > a_score else game['away_team']

            # Determine actual winner
            actual = None
            for s in schedule:
                if (s['home_name'], s['away_name']) == (game['home_team'], game['away_team']):
                    actual = (
                        game['home_team'] if s['home_score'] > s['away_score']
                        else game['away_team']
                    )
                    break

            all_preds.append({
                'date': date,
                'home': game['home_team'],
                'away': game['away_team'],
                'predicted': pick,
                'actual': actual,
                'correct': (pick == actual)
            })

    # Print summary
    total   = len(all_preds)
    correct = sum(p['correct'] for p in all_preds)
    pct     = (correct / total * 100) if total else 0.0
    print(f"Back-test {start_date}\u2192{end_date}: {correct}/{total} correct ({pct:.2f}% accuracy)")


if __name__ == "__main__":
    run_backtest(START_DATE, END_DATE)

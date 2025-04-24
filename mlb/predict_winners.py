from generate_game_features import get_games_for_dates, build_game_features
from team_stats import get_team_stats
from pitcher_stats import get_pitcher_stats

# Define a basic scoring system using data from generate_game_features

def score_team(team_stats, pitcher_stats, opponent_pitcher_era):
    try:
        win_pct = float(team_stats.get('Win %') or 0)
        batting_avg = float(team_stats.get('Batting Avg (last 5 games)') or 0)
        runs = int(team_stats.get('Runs Scored (last 5 games)') or 0)
        team_era = float(team_stats.get('ERA (last 5 games)') or 999)
        opp_pitcher_era = float(opponent_pitcher_era or 0)
    except:
        win_pct, batting_avg, runs, team_era, opp_pitcher_era = 0, 0, 0, 999, 0

    score = (
        win_pct * 100 +
        batting_avg * 1000 +
        runs +
        opp_pitcher_era * 5 -
        team_era * 5
    )
    return round(score, 2)

if __name__ == "__main__":
    target_dates = ['04/24/2025']
    games = get_games_for_dates(target_dates)
    features = build_game_features(games)

    predictions = []

    for game in features:
        home_score = score_team(
            get_team_stats(game['home_team']),
            get_pitcher_stats(game['home_pitcher']),
            get_pitcher_stats(game['away_pitcher']).get('ERA')
        )

        away_score = score_team(
            get_team_stats(game['away_team']),
            get_pitcher_stats(game['away_pitcher']),
            get_pitcher_stats(game['home_pitcher']).get('ERA')
        )

        predicted = game['home_team'] if home_score > away_score else game['away_team']
        confidence = abs(home_score - away_score)

        predictions.append({
            'date': game['date'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'predicted_winner': predicted,
            'home_score': home_score,
            'away_score': away_score,
            'confidence': round(confidence, 2)
        })

    print("\n=== GAME WINNER PREDICTIONS ===")
    for p in predictions:
        print(f"{p['date']}: {p['away_team']} at {p['home_team']} — Predicted Winner: {p['predicted_winner']}\n    Scores — {p['home_team']}: {p['home_score']}, {p['away_team']}: {p['away_score']} | Confidence Level: {p['confidence']}\n")

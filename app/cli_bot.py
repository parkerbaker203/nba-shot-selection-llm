from pipelines import ingest, transformation
from llm.summarizer import summarize_comparison
from viz.charts import plot_shot_chart
from pathlib import Path

## Run the code from git bash to start the bot
# PYTHONPATH=. py app/cli_bot.py


def main():
    # Printing messages to the terminal for the bots response and to prompt the user
    print("Welcome to the NBA Shot Selection Assistant!")
    # Getting the user's desired information
    team_name = input("Enter your team of interest: ").strip()
    opponent_name = input("Enter opponent team name or 'league': ").strip()
    season = input("Enter the season (e.g., 2024-25): ").strip()
    season_type = input(
        "Enter season type (Regular Season, Playoffs, Preseason, AllStar): "
    ).strip()
    show_visual = (
        input("Would you like a visual shot chart? (yes/no): ").strip().lower()
    )
    # If the user wants a visual, then ask for a specific player to subset the shot chart data when displaying
    if show_visual == "yes":
        visual_subject = input(
            "Would you like to see a specific player's shot chart or the team's attempt? (Jalen Brunson, team): "
        ).strip()
    else:
        visual_subject = None

    # Ingest team data
    print(f"\nFetching shot data for {team_name}...")
    team_shots = ingest.ingest_data(
        team_name=team_name, num_players=-1, season=season, season_type=season_type
    )

    # Compare team to opponent or league
    print("Comparing to opponent data...")
    comparison = transformation.compare_to_league(
        team_shots,
        opponent_team_name=opponent_name,
        season=season,
        season_type=season_type,
    )

    # Generate LLM summary
    print("\nGenerating LLM summary...")
    summary = summarize_comparison(team_name, opponent_name, comparison)
    print("\nLLM Analysis:\n")
    print(summary)

    # Optional visualization
    if show_visual == "yes":
        print("\nCreating visual shot chart...")
        output_dir = Path.cwd() / "data" / "visuals"
        output_path = output_dir / f"{team_name}_{season}_{season_type}_shot_chart.png"
        if visual_subject == "team":
            plot_shot_chart(team_shots, output_path, plt_title=team_name)
        else:
            player_shots = team_shots[team_shots["PLAYER_NAME"] == visual_subject]
            plot_shot_chart(player_shots, output_path, plt_title=visual_subject)


if __name__ == "__main__":
    main()

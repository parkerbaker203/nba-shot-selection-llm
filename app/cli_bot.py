from llm.prompts import SYSTEM_NBA_ASSISTANT, initial_user_prompt
from llm.summarizer import summarize_text
from pipelines.ingest import ingest_data
from pipelines.transformation import compare_to_league, summarize_player_shots
from viz.charts import plot_shot_chart  # example visualization function


def run_bot():
    # Step 1: LLM prompts user
    user_input_prompt = initial_user_prompt()
    print(user_input_prompt)
    user_response = input("Your response:\n")  # For CLI simplicity

    # Step 2: Parse user input
    # (Simple example: CSV style input: Team,Season,SeasonType,Opponent,Visual)
    team, season, season_type, opponent, show_visual = [
        x.strip() for x in user_response.split(",")
    ]
    show_visual = show_visual.lower() in ["yes", "true", "1"]

    # Step 3: Run ingestion + transformation
    team_shots = ingest_data(
        team, num_players=5, season=season, season_type=season_type
    )

    # Compare to league or opponent
    comparison_df = compare_to_league(
        team_shots, opponent_team_name=opponent, season=season, season_type=season_type
    )

    # Step 4: Generate summary with LLM
    summary = summarize_text(
        [
            {"role": "system", "content": SYSTEM_NBA_ASSISTANT},
            {
                "role": "user",
                "content": f"Summarize the shot selection and comparisons: {comparison_df.to_dict()}",
            },
        ]
    )
    print("\nLLM Summary:\n", summary)

    # Step 5: Optional visualization
    if show_visual:
        plot_shot_chart(team_shots)


if __name__ == "__main__":
    run_bot()

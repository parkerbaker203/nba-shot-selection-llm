import ollama


from pipelines.ingest import ingest_data
from pipelines.transformation import summarize_player_shots
from llm.summarizer import summarize_player_or_team
from pipelines.transformation import summarize_team_shots

# Example: get Knicks shot data
team_shots = ingest_data(
    team_name="New York Knicks",
    num_players=5,  # top 5 players
    season="2024-25",
    season_type="Playoffs",
)

# Choose a player
player_name = "Jalen Brunson"

# Summarize the shots per player
player_df = summarize_player_shots(team_shots)
player_shots = player_df[player_df["PLAYER_NAME"] == player_name]

# Pass to your LLM function
summary = summarize_player_or_team(player_name, player_shots)
print(summary)

team_summary_df = summarize_team_shots(team_shots)
team_summary = summarize_player_or_team("New York Knicks", team_summary_df)
print(team_summary)

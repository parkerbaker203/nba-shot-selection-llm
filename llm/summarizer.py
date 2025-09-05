import ollama
from llm.prompts import SYSTEM_NBA_ANALYST
from pipelines.transformation import compare_to_league
import pandas as pd


def stats_to_dict(comparison_df: pd.DataFrame):
    """Convert comparison dataframe to dictionary format for LLM context."""
    return comparison_df.to_dict(orient="records")


def summarize_comparison(team_name, opponent_name, comparison_df):
    """Send structured stats to LLM and get a natural language summary."""
    stats_data = stats_to_dict(comparison_df)

    user_prompt = (
        f"Analyze the {team_name}'s shot selection compared to "
        f"{'the league average' if opponent_name.lower() == 'league' else opponent_name}.\n"
        f"Here is the shot zone data:\n{stats_data}\n\n"
        "Please provide a clear summary of where the team excelled or struggled."
    )

    response = ollama.chat(
        model="llama2",
        messages=[
            {"role": "system", "content": SYSTEM_NBA_ANALYST},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]

import ollama
from llm.prompts import SYSTEM_NBA_ANALYST
from pipelines.transformation import compare_to_league
import pandas as pd


def stats_to_dict(comparison_df):
    """Convert comparison dataframe to dictionary format for LLM context.
    Parameters:
    - comparison_df (pd.DataFrame): Dataframe containing the comparison information between the team selected and selected opponent
    Returns:
    - (dict): Dictionary form of the comparison dataframe
    """
    return comparison_df.to_dict(orient="records")


def summarize_comparison(team_name, opponent_name, comparison_df):
    """Send structured stats to LLM and get a natural language summary.
    Parameters:
    - team_name (str): User submitted full team name
    - opponent_name (str): User submitted full opponent name. Can also be "league" for the league average information
    - comparison_df (pd.DataFrame): Dataframe of the comparison of shot chart data between the selected team and selected opponent
    Returns:
    - Response from the LLM after it has been provided the user prompt and its role as NBA Analyst
    """
    # Converts the comparison dataframe to a dictionary
    stats_data = stats_to_dict(comparison_df)
    # Initializing a prompt to feed the LLM
    user_prompt = (
        f"Analyze the {team_name}'s shot selection compared to "
        f"{'the league average' if opponent_name.lower() == 'league' else opponent_name}.\n"
        f"Here is the shot zone data:\n{stats_data}\n\n"
        "Please provide a clear summary of where the team excelled or struggled."
    )
    # Feeding the LLM the role and prompt, then getting the response
    response = ollama.chat(
        model="llama2",
        messages=[
            {"role": "system", "content": SYSTEM_NBA_ANALYST},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]

# llm/summarizer.py
import ollama
from pipelines.transformation import stats_to_dict
import json
import pandas as pd

import ollama


def summarize_text(messages):
    """
    messages: list of dicts like [{"role": "system", "content": ...}, {"role": "user", "content": ...}]
    """
    response = ollama.chat(
        model="llama2",
        messages=messages,
    )
    return response["message"]["content"]


def summarize_player_or_team(player_name: str, df_shots: pd.DataFrame) -> str:
    stats_dict = stats_to_dict(df_shots)
    prompt_text = f"""
    Summarize the shot selection for {player_name}.
    Stats by zone: {json.dumps(stats_dict)}
    Give a concise summary in 2-3 sentences focusing on style and efficiency.
    """
    return summarize_text(prompt_text)

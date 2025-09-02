# llm/prompts.py

SYSTEM_NBA_ASSISTANT = "You are an NBA analyst assistant. Guide the user to provide team, season, opponent, and visualization preferences."


def initial_user_prompt():
    return """Hi! I can summarize NBA shot selection data. 
Please provide:
1. Team name
2. Season (e.g., 2024-25)
3. Season type (Regular, Playoffs, etc.)
4. Opponent team name or 'league' for league average
5. Do you want a visual shot chart? (yes/no)
"""

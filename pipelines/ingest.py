"""Data Ingestion for NBA-SHOT-SELECTION-LLM
=====================================================
Author: Parker Baker
Date: 08/31/2025

Parameters user must provide:
- Full Team Name --  Example: "Knicks"
- Number of Players to include: 5 is default, should work in some kind of error control for providing all players, might kill processing though
- Season -- Example: "2024-25"
- Season Type -- Example: "Playoffs"

Pipeline:
1. team_id = get_team_id(team_name = "New York Knicks")
2. game_ids = get_game_ids(team_id, season="2024-25", season_type="playoffs")
3. cum_team_stats = get_cum_team_stats(team_id, game_ids)
4. avg_minutes = get_average_playtime(game_stats_dict=cum_team_stats)
5. top_x_player_ids = top_x_players_by_min(avg_minutes, num_players=5)
6. team_shots = get_team_shots(team_id: int, player_ids: list, season="2024-25", season_type="Playoffs")
=====================================================
"""

import pandas as pd
import time

from nba_api.stats.endpoints import ShotChartDetail
from nba_api.stats.static import teams
from nba_api.stats.endpoints import LeagueGameFinder
from nba_api.stats.endpoints import CumeStatsTeam


def get_team_id(team_name="New York Knicks"):
    """Gets the team id given the full team name using the NBA api
    Parameters:
    - team_name (str): Full team name that corresponds to the NBA api's names
    Returns:
    - team_id (int): The team_id corresponding to the provided team_name
    """
    nba_teams = teams.get_teams()
    team_id = [team for team in nba_teams if team["full_name"] == team_name][0]["id"]
    return team_id


def get_game_ids(team_id, season="2024-25", season_type="playoffs"):
    """Gets all the game ids for a given team, year, and season type
    Parameters:
    - team_id (int): The team_id corresponding to the provided team_name
    - season (str): Season year string for the desired time frame
    - season_type (str): Time of season ^(Regular Season)|(Pre Season)|(Playoffs)|(All Star)$
    Returns:
    - game_ids (list): List of game ids
    """
    # Get a list of game ids
    game_ids = (
        LeagueGameFinder(
            team_id_nullable=team_id,
            season_nullable=season,
            season_type_nullable=season_type.title(),  # Season type is case sensitive
        )
        .get_data_frames()[0]["GAME_ID"]
        .tolist()
    )
    return game_ids


def get_cum_team_stats(team_id, game_ids):
    """Get the game stats for all game ids for the provided team - rate limited to sleep for 3 seconds
    Parameters:
    - team_id (int): The team_id corresponding to the provided team_name
    - game_ids (list): List of game ids from the get_game_ids() function
    Returns:
    - game_stats (dict): Dictionary containing dataframes of stats for each game id
    """
    game_stats = {}
    for game_id in game_ids:
        game_stats[game_id] = CumeStatsTeam(
            team_id=team_id, game_ids=game_id
        ).get_data_frames()[0]
        print("Collected data for", game_id)
        time.sleep(3)
    return game_stats


def get_average_playtime(game_stats_dict):
    """Calculates the average minutes for each player from the game_stats dictionary
    Parameters:
    - game_stats (dict): Dictionary containing dataframes of stats for each game id from the get_cum_team_stats() function
    Returns:
    - avg_minutes (pd.DataFrame): Dataframe containing the player name, player id, and average minutes played sorted by minutes
    """
    # Step 1: Combine all game DataFrames into one
    combined_stats = pd.concat(game_stats_dict.values(), ignore_index=True)
    # Step 2: Group by player and calculate average minutes
    avg_minutes = (
        combined_stats.groupby("PLAYER")[["ACTUAL_MINUTES", "PERSON_ID"]]
        .mean()
        .reset_index()
        .sort_values(by="ACTUAL_MINUTES", ascending=False)
    )
    avg_minutes["PERSON_ID"] = avg_minutes["PERSON_ID"].astype(int)
    return avg_minutes


def top_x_players_by_min(avg_minutes, num_players=5):
    """Returns the top x player ids to from the output of get_average_playtime() function
    Parameters:
    - avg_minutes (pd.DataFrame): Dataframe containing the player name, player id, and average minutes played sorted by minutes
    - num_players (int): Top number of players to get player ids of
    Returns:
    - top_num_player_ids (list): List of the top x player ids by minutes played
    """
    top_num_player_ids = avg_minutes.nlargest(num_players, "ACTUAL_MINUTES")[
        "PERSON_ID"
    ].tolist()
    return top_num_player_ids


def get_team_shots(
    team_id: int, player_ids: list, season="2024-25", season_type="Playoffs"
):
    """Pulls data on all shots taken by players on provided team during a year and season type
    Parameters:
    - team_id (int): The team_id corresponding to the provided team_name
    - player_ids (list): List of the player ids
    - season (str): Season year string for the desired time frame
    - season_type (str): Time of season ^(Regular Season)|(Pre Season)|(Playoffs)|(All Star)$
    Returns:
    - df_shots_filtered (pd.DataFrame): Dataframe of all shots taken in period by team and information on makes, shot type, etc.
    """
    shot_chart = ShotChartDetail(
        team_id=team_id,
        season_nullable=season,
        season_type_all_star=season_type.title(),
        player_id=0,  # 0 = all players on team
        context_measure_simple="FGA",
    )

    df_shots = shot_chart.get_data_frames()[0]

    # Subset to only the requested players
    df_shots_filtered = df_shots[df_shots["PLAYER_ID"].isin(player_ids)].reset_index(
        drop=True
    )

    return df_shots_filtered


def ingest_data(team_name, num_players, season, season_type):
    """Runs the full ingestion pipeline in one function
    Parameters:
    - team_name (str): Full team name that corresponds to the NBA api's names
    - num_players (int): Top number of players to get player ids of
    - season (str): Season year string for the desired time frame
    - season_type (str): Time of season ^(Regular Season)|(Pre Season)|(Playoffs)|(All Star)$
    Returns:
    - team_shots (pd.DataFrame): Filtered dataframe of all shots taken in period by team and information on makes, shot type, etc.
    """
    team_id = get_team_id(team_name=team_name)
    game_ids = get_game_ids(team_id=team_id, season=season, season_type=season_type)
    cum_team_stats = get_cum_team_stats(team_id, game_ids)
    avg_minutes = get_average_playtime(game_stats_dict=cum_team_stats)
    top_x_player_ids = top_x_players_by_min(avg_minutes, num_players=num_players)
    team_shots = get_team_shots(
        team_id=team_id,
        player_ids=top_x_player_ids,
        season=season,
        season_type=season_type,
    )
    return team_shots

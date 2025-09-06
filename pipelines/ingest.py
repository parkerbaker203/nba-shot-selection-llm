"""Data Ingestion for NBA-SHOT-SELECTION-LLM
=====================================================
Author: Parker Baker
Date: 08/31/2025

Parameters user must provide:
- Full Team Name --  Example: "Knicks"
- Number of Players to include: Defaults to top 5, but if "-1" is given it will return stats for all players on the roster
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

from pathlib import Path


def get_team_id(team_name="New York Knicks"):
    nba_teams = teams.get_teams()
    matches = [
        team for team in nba_teams if team["full_name"].strip() == team_name.strip()
    ]

    if not matches:
        raise ValueError(
            f"Team name '{team_name}' not found. Check spelling and capitalization."
        )

    return matches[0]["id"]


def get_game_ids(team_id, season="2024-25", season_type="playoffs"):
    """Gets all the game ids for a given team, year, and season type
    Parameters:
    - team_id (int): The team_id corresponding to the provided team_name
    - season (str): Season year string for the desired time frame
    - season_type (str): Time of season ^(Regular Season)|(Pre Season)|(Playoffs)|(All Star)$
    Returns:
    - game_ids (list): List of game ids
    """
    # Get a list of game ids from nba api
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
    # Initialzing dictionary to hold all game data
    game_stats = {}
    i = 1  # counter for printing progress
    total_games = len(game_ids)
    # Looping through each game id and calling nba api to get cumalative stats for that game
    for game_id in game_ids:
        game_stats[game_id] = CumeStatsTeam(
            team_id=team_id, game_ids=game_id
        ).get_data_frames()[0]
        print(f"Game {i} of {total_games} has been processed - ID = {game_id}")
        i += 1
        time.sleep(1)  # Rate limit set to 1 second so nba_api doesn't throttle
    return game_stats


def get_average_playtime(game_stats_dict):
    """Calculates the average minutes for each player from the game_stats dictionary
    Parameters:
    - game_stats (dict): Dictionary containing dataframes of stats for each game id from the get_cum_team_stats() function
    Returns:
    - avg_minutes (pd.DataFrame): Dataframe containing the player name, player id, and average minutes played sorted by minutes
    """
    # Concatentating all game data into one dataframe
    combined_stats = pd.concat(game_stats_dict.values(), ignore_index=True)
    # Grouping by player to get average minutes played
    avg_minutes = (
        combined_stats.groupby("PLAYER")[["ACTUAL_MINUTES", "PERSON_ID"]]
        .mean()
        .reset_index()
        .sort_values(by="ACTUAL_MINUTES", ascending=False)
    )
    avg_minutes["PERSON_ID"] = avg_minutes["PERSON_ID"].astype(
        int
    )  # Converting id to int to keep data integrity
    return avg_minutes


def top_x_players_by_min(avg_minutes, num_players=5):
    """Returns the top x player ids to from the output of get_average_playtime() function
    Parameters:
    - avg_minutes (pd.DataFrame): Dataframe containing the player name, player id, and average minutes played sorted by minutes
    - num_players (int): Top number of players to get player ids of. If "-1" submitted then all players will be returned.
    Returns:
    - top_num_player_ids (list): List of the top x player ids by minutes played
    """
    # If user wants all players, the -1 parameter can be set, otherwise take the amount requested
    if num_players == -1:
        top_num_player_ids = avg_minutes["PERSON_ID"].tolist()
    else:  # Takes the top_n based on avg minutes
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
    # Getting shot chart information for the whole season for all players on a team
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
    data_dir = Path.cwd() / "data" / "shotcharts"
    data_dir.mkdir(parents=True, exist_ok=True)
    team_path = data_dir / f"shots_{team_name}_{season}_{season_type}.parquet"
    if team_path.exists():
        team_shots = pd.read_parquet(team_path)
        print(f"Loading file from cached parquet: {team_path}")
    else:
        # Grabs the team id
        team_id = get_team_id(team_name=team_name)
        # Grabs the game ids for the users team, season, and season_type
        game_ids = get_game_ids(team_id=team_id, season=season, season_type=season_type)

        # Getting all cumalitive game stats for that team and games
        cum_team_stats = get_cum_team_stats(team_id, game_ids)
        # Calculating the average playtime for all players on the team in that span of games
        avg_minutes = get_average_playtime(game_stats_dict=cum_team_stats)
        # Gets the top x players based on average play time to create shot chart data
        top_x_player_ids = top_x_players_by_min(avg_minutes, num_players=num_players)
        # Pulls shot chart data from nba_api
        team_shots = get_team_shots(
            team_id=team_id,
            player_ids=top_x_player_ids,
            season=season,
            season_type=season_type,
        )
        team_shots.to_parquet(team_path, index=False)
    return team_shots

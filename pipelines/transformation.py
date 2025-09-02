import pandas as pd
from pathlib import Path
import pipelines.ingest as ing
import os

from nba_api.stats.endpoints import ShotChartLeagueWide


def summarize_team_shots(df_shots):
    """Rolls up a teams shot data based on SHOT_ZONE_BASIC, also calculates the fg_pct
    Parameters:
    - df_shots (pd.DataFrame): Dataframe of shot chart data from ingest.py
    Returns:
    - summary (pd.DataFrame): Dataframe of summarized shot data based on location
    """
    # Rolling up shot chart data on shot zone, calculating the fga/fgm/fg_pct
    summary = (
        df_shots.groupby("SHOT_ZONE_BASIC")
        .agg(attempts=("SHOT_MADE_FLAG", "count"), makes=("SHOT_MADE_FLAG", "sum"))
        .reset_index()
    )
    summary["fg_pct"] = summary["makes"] / summary["attempts"]
    return summary


def summarize_player_shots(df_shots):
    """Rolls up team shot chart data on player name and shot zone
    Parameters:
    - df_shots (pd.DataFrame): Dataframe of shot chart data from ingest.py
    Returns:
    - summary (pd.DataFrame): Dataframe of summarized shot data based on location and player
    """
    # Rolling up the shot chart data on a player and shot zone level
    summary = (
        df_shots.groupby(["PLAYER_NAME", "SHOT_ZONE_BASIC"])
        .agg(attempts=("SHOT_MADE_FLAG", "count"), makes=("SHOT_MADE_FLAG", "sum"))
        .reset_index()
    )
    # Calculating the fgm/fga/fg_pct
    summary["fg_pct"] = summary["makes"] / summary["attempts"]
    return summary


def summarize_league_avg(league_avg):
    """Summarizes league average data by rolling up on shot zone
    Parameters:
    - league_avg (pd.DataFrame): Dataframe of league shot chart data from ShotChartLeagueWide
    Returns:
    - summary (pd.DataFrame): Dataframe of summarized shot data based on location

    """
    # Rolling up the league average shot chart data to shot zone
    summary = league_avg.groupby("SHOT_ZONE_BASIC", as_index=False).agg(
        attempts=("FGA", "sum"), makes=("FGM", "sum")
    )
    # Calculating the fgm/fga/fg_pct
    summary["fg_pct"] = summary["makes"] / summary["attempts"]
    return summary


def compare_stats(team_shots, opponent_shots, league_y_n=True):
    """Creates an outer merged dataframe linked on SHOT_ZONE_BASIC between team of interest and selected opponent (league or individual team)
    Parameters:
    - team_shots (pd.DataFrame): Dataframe of shot chart data from ingest.py
    - opponent_shots (pd.DataFrame): Dataframe of opponent shot chart data
    - league_y_n (Boolean): Binary indicator for whether you want the league average or an individual opponent
    Returns:
    - comparison (pd.DataFrame): Outer merged dataframe showing the shot chart data for the current team against the opponents fga/fgm/fg_pct
    """
    # Summarizing the current team shot chart
    team_summary = summarize_team_shots(team_shots)
    # Checks if the user wants to compare against the league average or a specific opponent
    if league_y_n == True:
        # Summarizing the league average shot chart
        oppo_summary = summarize_league_avg(opponent_shots)
    else:
        # summarizing the opponents shot chart
        oppo_summary = summarize_team_shots(opponent_shots)

    # Merging results on shot zone and adding suffixes
    comparison = pd.merge(
        team_summary,
        oppo_summary,
        on="SHOT_ZONE_BASIC",
        suffixes=("_team", "_opponent"),
        how="outer",
    ).fillna(0)

    return comparison


def compare_to_league(
    team_shots, opponent_team_name="league", season="2024-25", season_type="Playoffs"
):
    """Performs full comparison between the current shot chart data and user selected opponent, season, and season type.
    Also caches/pulls existing shot chart data to reduce api call time.
    Parameters:
    - team_shots (pd.DataFrame): Dataframe of shot chart data from ingest.py
    - opponent_team_name (str): Full team name to compare against
    - season (str): Season of interest for comparison against provided team shot chart data
    - season_type (str): Time of season ^(Regular Season)|(Pre Season)|(Playoffs)|(All Star)$
    Returns:
    - comparison (pd.DataFrame): Outer merged dataframe showing the shot chart data for the current team against the opponents fga/fgm/fg_pct
    """
    # Identifying and creating the data_dir if necessary
    data_dir = Path.cwd()
    data_dir = Path.cwd().parent / "data" / "shotcharts"
    data_dir.mkdir(
        parents=True, exist_ok=True
    )  # <-- parents=True creates all missing dirs
    # Checking if the opponent team name has been submitted
    if opponent_team_name == "league":
        # League average mode
        league_path = data_dir / f"league_avg_{season}.parquet"
        # Checking if the league average data is cached
        if league_path.exists():
            league_avg = pd.read_parquet(league_path)
        else:
            # Fetch from API
            league_avg = ShotChartLeagueWide(season=season).get_data_frames()[0]
            league_avg.to_parquet(league_path, index=False)
        # Comparing the current team to league average
        comparison = compare_stats(team_shots, league_avg, league_y_n=True)
        return comparison

    # Opponent mode
    oppo_path = data_dir / f"opponent_shots_{opponent_team_name}_{season}.parquet"
    # Checking if the data is already cached
    if oppo_path.exists():
        opponent_shots = pd.read_parquet(oppo_path)
    else:
        # Run ingestion pipeline for opponent
        opponent_shots = ing.ingest_data(
            team_name=opponent_team_name,
            num_players=-1,
            season=season,
            season_type=season_type,
        )
        opponent_shots.to_parquet(oppo_path, index=False)
    # Comparing the current team to specified opponent
    comparison = compare_stats(team_shots, opponent_shots, league_y_n=False)
    return comparison


def prepare_shot_chart_data(df_shots):
    """Prepares the raw shot chart data for creating a visual shot chart of misses and makes
    Parameters:
    df_shots (pd.DataFrame): Dataframe of shot chart data from ingest.py
    Returns:
    A subset dataframe including only the coordinate locations of the shot, whether it was a make or a miss, and the player name
    """
    # Subsetting shot chart data to get players coordinate locations on shots
    return df_shots[["LOC_X", "LOC_Y", "SHOT_MADE_FLAG", "PLAYER_NAME"]]


def stats_to_dict(df_shots_summarized):
    """Converts a summarized shot DataFrame into a dictionary suitable for LLM consumption."""
    df = df_shots_summarized[["SHOT_ZONE_BASIC", "attempts", "makes", "fg_pct"]].copy()
    df["fg_pct"] = (df["fg_pct"] * 100).round(1)

    stats_dict = {}
    for _, row in df.iterrows():
        stats_dict[row["SHOT_ZONE_BASIC"]] = {
            "attempts": int(row["attempts"]),
            "makes": int(row["makes"]),
            "fg_pct": row["fg_pct"],
        }
    return stats_dict

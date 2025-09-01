"""Data Transformation for NBA-SHOT-SELECTION-LLM
=====================================================
Author: Parker Baker
Date: 08/31/2025

=====================================================
"""

import pandas as pd


# ----------------------------
# TEAM-LEVEL TRANSFORMATIONS
# ----------------------------
def summarize_team_shots(df_shots):
    """
    Summarize team shot selection:
    - count of shots per zone
    - FG% per zone
    """
    summary = (
        df_shots.groupby("SHOT_ZONE_BASIC")
        .agg(attempts=("SHOT_MADE_FLAG", "count"), makes=("SHOT_MADE_FLAG", "sum"))
        .reset_index()
    )
    summary["fg_pct"] = summary["makes"] / summary["attempts"]
    return summary


# ----------------------------
# PLAYER-LEVEL TRANSFORMATIONS
# ----------------------------
def summarize_player_shots(df_shots: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize shots for each player by zone.
    """
    summary = (
        df_shots.groupby(["PLAYER_NAME", "SHOT_ZONE_BASIC"])
        .agg(attempts=("SHOT_MADE_FLAG", "count"), makes=("SHOT_MADE_FLAG", "sum"))
        .reset_index()
    )
    summary["fg_pct"] = summary["makes"] / summary["attempts"]
    return summary


# ----------------------------
# LEAGUE COMPARISONS
# ----------------------------
def compare_to_league(team_shots_df, season="2024-25", opponent_team_name=None):
    if opponent_team_name is None:
        # load league averages
        league_avg = pd.read_parquet(f"data/league_avg_{season}.parquet")
        comparison = _compare_stats(team_shots_df, league_avg)
        return comparison

    # Opponent mode
    fname = f"data/opponents/opponent_shots_{opponent_team_name}_{season}.parquet"
    if os.path.exists(fname):
        opponent_shots = pd.read_parquet(fname)
    else:
        # Run ingestion pipeline for opponent
        opponent_shots = get_team_shots(team_name=opponent_team_name, season=season)
        opponent_shots.to_parquet(fname, index=False)

    comparison = _compare_stats(team_shots_df, opponent_shots)
    return comparison


# ----------------------------
# VISUALIZATION PREP
# ----------------------------
def prepare_shot_chart_data(df_shots: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare raw shot chart data for plotting (scatter on a court).
    Only keep necessary cols: LOC_X, LOC_Y, SHOT_MADE_FLAG.
    """
    return df_shots[["LOC_X", "LOC_Y", "SHOT_MADE_FLAG", "PLAYER_NAME"]]


import pandas as pd


def compare_stats(team_shots_df, comparison_df):
    """
    Compare a team's shots against either league averages or opponent shots.
    """

    # ---- Aggregate TEAM shots ----
    team_summary = (
        team_shots_df.groupby("SHOT_ZONE_BASIC")
        .agg(attempts=("SHOT_MADE_FLAG", "count"), makes=("SHOT_MADE_FLAG", "sum"))
        .reset_index()
    )
    team_summary["fg_pct"] = team_summary["makes"] / team_summary["attempts"]

    # ---- Handle comparison dataset ----
    if "FGA" in comparison_df.columns:
        # Case 1: League averages (already aggregated)
        comp_summary = comparison_df.rename(
            columns={
                "SHOT_ZONE_BASIC": "SHOT_ZONE_BASIC",
                "FGA": "attempts",
                "FGM": "makes",
                "FG_PCT": "fg_pct",
            }
        )[["SHOT_ZONE_BASIC", "attempts", "makes", "fg_pct"]]

    else:
        # Case 2: Opponent/team raw shots — aggregate first
        comp_summary = (
            comparison_df.groupby("SHOT_ZONE_BASIC")
            .agg(attempts=("SHOT_MADE_FLAG", "count"), makes=("SHOT_MADE_FLAG", "sum"))
            .reset_index()
        )
        comp_summary["fg_pct"] = comp_summary["makes"] / comp_summary["attempts"]

    # ---- Merge results for comparison ----
    comparison = pd.merge(
        team_summary,
        comp_summary,
        on="SHOT_ZONE_BASIC",
        suffixes=("_team", "_comparison"),
        how="outer",
    ).fillna(0)

    return comparison


def compare_to_league(
    team_shots_df, season="2024-25", opponent_team_name=None, season_type="Playoffs"
):
    # Identifying and creating the data_dir if necessary
    data_dir = Path("data")
    opponents_dir = data_dir / "shotcharts"
    data_dir.mkdir(exist_ok=True)
    opponents_dir.mkdir(exist_ok=True)
    # Checking if the opponent team name has been submitted
    if opponent_team_name is None:
        # League average mode
        league_path = data_dir / f"league_avg_{season}.parquet"
        if league_path.exists():
            league_avg = pd.read_parquet(league_path)
        else:
            # Fetch from API
            league_avg = ShotChartLeagueWide(season=season).get_data_frames()[0]
            league_avg.to_parquet(league_path, index=False)

        comparison = compare_stats(team_shots_df, league_avg)
        return comparison

    # Opponent mode
    oppo_path = opponents_dir / f"opponent_shots_{opponent_team_name}_{season}.parquet"
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

    comparison = compare_stats(team_shots_df, opponent_shots)
    return comparison

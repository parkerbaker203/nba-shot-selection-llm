# example_plot.py
from pipelines.ingest import ingest_data
from pipelines.transformation import prepare_shot_chart_data, summarize_player_shots
from viz.charts import plot_shot_chart

# Ingest data for team
team_shots = ingest_data(
    team_name="New York Knicks", num_players=5, season="2024-25", season_type="Playoffs"
)

# Prepare data for plotting
jalen = team_shots[team_shots["PLAYER_NAME"] == "Jalen Brunson"]
df_shots = prepare_shot_chart_data(jalen)

# Plotting the data
plot_shot_chart(df_shots)

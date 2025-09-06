# viz/charts.py
import matplotlib.pyplot as plt
from viz.court import draw_court


def plot_shot_chart(df_shots, output_path, plt_title="Shot Chart"):
    """Plots the shot chart data onto the empty half court plot
    Parameters:
    - df_shots (pd.DataFrame): DataFrame with columns ['LOC_X', 'LOC_Y', 'SHOT_MADE_FLAG']
    - output_path (str): Filepath to export the png to
    - plt_title (str): Title to be displayed above the shot chart
    """
    ax = draw_court()

    # Scatter: makes vs misses
    made = df_shots[df_shots["SHOT_MADE_FLAG"] == 1]
    missed = df_shots[df_shots["SHOT_MADE_FLAG"] == 0]

    ax.scatter(missed["LOC_X"], missed["LOC_Y"], c="red", alpha=0.6, label="Miss", s=50)
    ax.scatter(made["LOC_X"], made["LOC_Y"], c="green", alpha=0.6, label="Make", s=50)

    ax.legend(loc="upper right")
    ax.set_title(plt_title, fontsize=18)

    # Saving the plot to a png file
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saving plot to: {output_path}")
    # Displaying the plot for the user to see
    plt.show()

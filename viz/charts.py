# viz/charts.py
import matplotlib.pyplot as plt
from viz.court import draw_court


def plot_shot_chart(df_shots, title="Shot Chart"):
    """
    df_shots: DataFrame with columns ['LOC_X', 'LOC_Y', 'SHOT_MADE_FLAG']
    """
    ax = draw_court()

    # Scatter: makes vs misses
    made = df_shots[df_shots["SHOT_MADE_FLAG"] == 1]
    missed = df_shots[df_shots["SHOT_MADE_FLAG"] == 0]

    ax.scatter(missed["LOC_X"], missed["LOC_Y"], c="red", alpha=0.6, label="Miss", s=50)
    ax.scatter(made["LOC_X"], made["LOC_Y"], c="green", alpha=0.6, label="Make", s=50)

    ax.legend(loc="upper right")
    ax.set_title(title, fontsize=18)
    plt.show()

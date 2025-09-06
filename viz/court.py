# viz/court.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def draw_court(color="black", lw=2):
    """Draws an NBA court using matplotlib patches
    Parameters:
    - color (str): Color of the halfcourt lines, defaults to black
    - lw (int): Size of the line widths
    Returns
    - ax (plt): Emtpy plot of half court to display shot chart information on
    """
    fig, ax = plt.subplots(figsize=(15, 7.5))

    # Hoop
    hoop = patches.Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Backboard
    backboard = patches.Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # Paint
    outer_box = patches.Rectangle(
        (-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False
    )
    inner_box = patches.Rectangle(
        (-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False
    )

    # 3-pt line
    corner_left = patches.Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_right = patches.Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    arc = patches.Arc((0, 0), 475, 475, theta1=0, theta2=180, linewidth=lw, color=color)

    court_elements = [
        hoop,
        backboard,
        outer_box,
        inner_box,
        corner_left,
        corner_right,
        arc,
    ]

    for element in court_elements:
        ax.add_patch(element)

    # Set limits and aspect
    ax.set_xlim(-250, 250)
    ax.set_ylim(-47.5, 422.5)
    ax.set_aspect("equal")
    ax.axis("off")

    return ax

"""
Add colorbar to map.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import typer
from matplotlib import patheffects
from matplotlib.axes import Axes


def add_colorbar(
    map_path: Path = typer.Option(...),
    colorbar_path: Path = typer.Option(...),
    label: str = typer.Option(...),
    output_path: Path = typer.Option(...),
):
    """
    Add colorbar to map.
    """
    img = plt.imread(map_path)
    w, h = 3779 / 1000, 3749 / 1000
    fig, ax = plt.subplots(dpi=100)
    assert isinstance(ax, Axes)
    ax.imshow(img)
    ax.axis("off")

    colorbar_ax = fig.add_axes([0.040, 0.113, 0.3, 0.3])
    colorbar_ax.imshow(plt.imread(colorbar_path), alpha=0.9)
    colorbar_ax.axis("off")

    # Add label as well
    ax.text(
        x=0.01,
        y=0.95,
        s=label,
        fontdict=dict(
            size="xx-large",
            path_effects=[patheffects.withStroke(linewidth=1, foreground="white")],
        ),
        transform=ax.transAxes,
    )

    fig.set_size_inches(w, h)
    fig.savefig(output_path, bbox_inches="tight", dpi=1000)

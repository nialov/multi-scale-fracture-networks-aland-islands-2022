"""
Create custom colorbar.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import typer
from matplotlib import cm, colors
from matplotlib.colorbar import ColorbarBase


def create_colorbar(
    vmin: float = typer.Option(...),
    vmax: float = typer.Option(...),
    label: str = typer.Option(...),
    colormap: str = typer.Option(...),
    output: Path = typer.Option(...),
):
    """
    Create custom colorbar.
    """
    fig, ax = plt.subplots(figsize=(0.4, 6))
    fig.subplots_adjust(bottom=0.5)

    cmap = cm.get_cmap(colormap)
    norm = colors.Normalize(vmin=vmin, vmax=vmax)

    cb1 = ColorbarBase(
        ax,
        cmap=cmap,
        norm=norm,
        orientation="vertical",
        ticklocation="left",
    )
    cb1.set_label(label, fontdict=dict(size="xx-large"))
    cb1.ax.tick_params(labelsize="xx-large")

    fig.savefig(output, bbox_inches="tight")

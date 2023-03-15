"""
Striations plots.
"""
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import typer
from beartype.typing import Tuple
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.quiver import Quiver
from rich.console import Console
from rich.traceback import install
from shapely.geometry import Polygon
from shapely.wkt import loads

import background
from fractopo.analysis import azimuth
from fractopo.general import read_geofile

CONSOLE = Console()
install()

print = CONSOLE.print

# APP = typer.Typer()


def _azimuth_to_unit_vector(azimuth: float) -> np.ndarray:
    """
    Convert azimuth to unit vector.
    """
    azimuth_rad = np.deg2rad(azimuth)
    return np.array([np.sin(azimuth_rad), np.cos(azimuth_rad)])


def _reverse_azimuth(azimuth: float) -> float:
    """
    Reverse azimuth direction.
    """
    reversed_azimuth = azimuth + 180
    if reversed_azimuth > 360:
        reversed_azimuth = reversed_azimuth - 360
    return reversed_azimuth


def plot_striations(
    aland_clip_box: Polygon,
    striations_full_gdf: gpd.GeoDataFrame,
    fig: Figure,
    ax: Axes,
) -> Tuple[gpd.GeoDataFrame, Figure, Axes, Quiver]:
    """
    Create striation map and rose plot.
    """
    # load data
    striations_invalid = gpd.clip(
        striations_full_gdf,
        aland_clip_box,
    )

    # Validate
    striations_gdf = background.STRIATIONS_SCHEMA.validate(striations_invalid)
    assert isinstance(striations_gdf, gpd.GeoDataFrame)

    # Plot data
    # Setup figure
    # fig, ax = plt.subplots(figsize=(8.27, 11.75))

    # Plot striations
    # striations.plot(ax=ax, marker="v")
    xs = [geom.x for geom in striations_gdf.geometry.values]
    ys = [geom.y for geom in striations_gdf.geometry.values]
    unit_vectors = [
        _azimuth_to_unit_vector(azim)
        for azim in striations_gdf[background.JAATIKON_TULOSUUNTA].values
    ]

    # Use minus to reverse direction to glacial flow direction
    us = np.array([-uv[0] for uv in unit_vectors])
    vs = np.array([-uv[1] for uv in unit_vectors])

    # ax.quiver(xs, ys, us, vs, us + vs, color="black")
    quiver = ax.quiver(xs, ys, us, vs, color="navy", alpha=0.5)

    return striations_gdf, fig, ax, quiver

    # Identify aged striae
    # aged_rows = (
    #     striations_gdf[background.SUHTEELLINEN_IKA] != background.Age.UNDEFINED.value
    # )
    # for (_, row), x, y in zip(striations_gdf.loc[aged_rows].iterrows(), xs, ys):
    #     label = (
    #         "O"
    #         if row[background.SUHTEELLINEN_IKA] == background.Age.OLDER.value
    #         else "Y"
    #     )
    #     ax.text(x, y, label, alpha=0.65, fontsize="small", va="bottom", ha="center")


def striations(
    shoreline_path: Path = typer.Argument(...),
    striations_path: Path = typer.Argument(...),
    aland_clip_box_path: Path = typer.Argument(...),
    striations_output_path: Path = typer.Argument(...),
    rose_output_path: Path = typer.Argument(...),
):
    """
    Create striation map and rose plot.
    """
    aland_clip_box = loads(aland_clip_box_path.read_text())
    assert isinstance(aland_clip_box, Polygon)
    # load data
    shoreline_gdf = read_geofile(shoreline_path)
    striations_full_gdf = read_geofile(striations_path)

    fig, ax = plt.subplots(figsize=(8.27, 11.75))

    striations_gdf, fig, ax, _ = plot_striations(
        aland_clip_box=aland_clip_box,
        striations_full_gdf=striations_full_gdf,
        fig=fig,
        ax=ax,
    )

    # Plot shoreline
    shoreline_gdf.boundary.plot(ax=ax, linewidth=0.6, color="black")
    shoreline_gdf.plot(ax=ax, color="black", alpha=0.05)
    # shoreline_gdf_clipped.plot(linewidth=0, ax=ax, color=\"black\", alpha=1.0)\n,

    # Set axis limits better
    # xmin, ymin, xmax, ymax = 75000, 6.64e6, 145000, 6.73e6
    # ax.set_xlim(xmin, xmax)
    # ax.set_ylim(ymin, ymax)
    xmin, ymin, xmax, ymax = aland_clip_box.bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title("Åland - Glacial Striations", fontsize="x-large")

    ax.xaxis.set_major_formatter(plt.FuncFormatter(background.format_func_m_to_km))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(background.format_func_m_to_km))

    # Set correct unit labels
    ax.set_ylabel("Y (km)")
    ax.set_xlabel("X (km)")

    # Add scale bar
    # https://geopandas.org/en/stable/gallery/matplotlib_scalebar.html
    background.add_scale_bar(ax=ax, bbox_coords=(0.93, 0.2))

    # Add north arrow
    # x, y, arrow_length = 0.86, 0.93, 0.05
    # background.add_north_arrow(ax=ax, x=x, y=y, arrow_length=arrow_length)
    x, y, arrow_length = 0.06, 0.98, 0.05
    background.add_north_arrow(ax=ax, x=x, y=y, arrow_length=arrow_length)

    # Save plot
    striations_output_path.parent.mkdir(exist_ok=True)
    fig.savefig(striations_output_path, bbox_inches="tight")

    azimuth_array = striations_gdf[background.JAATIKON_TULOSUUNTA].values
    azimuth_array_rev = [_reverse_azimuth(azimuth) for azimuth in azimuth_array]
    ones = np.ones(len(azimuth_array_rev))
    _, fig, ax = azimuth.plot_azimuth_plot(
        azimuth_array=np.array(azimuth_array_rev),
        length_array=ones,
        azimuth_set_array=ones,
        azimuth_set_names=ones.astype(str),
        label="Åland - Glacial Striations",
        axial=False,
        azimuth_set_ranges=(),
        visualize_sets=False,
        plain=True,
    )

    ax.set_title(None)

    # Save plot
    fig.savefig(rose_output_path, bbox_inches="tight")

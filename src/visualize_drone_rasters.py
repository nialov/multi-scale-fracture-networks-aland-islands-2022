"""
Script to visualize drone target areas and traces.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import rasterio
import seaborn as sns
import typer
from beartype.typing import List
from rasterio.plot import show

from fractopo.general import read_geofile

RASTER_AREA_PAIRS = {
    # "getaberget1_20m_070820_orto_test_1_1_area.tif": [
    #     "getaberget_20m_1_1_area.geojson",
    # ],
    "Getaberget4_20m_080820_orto.tif": {
        "areas": [
            "getaberget_20m_4_3_area.geojson",
        ],
        "traces": [
            "getaberget_20m_4_traces.geojson",
        ],
    },
    "Getaberget9_20m_120820_orto.tif": {
        "areas": [
            "getaberget_20m_9_2_area.geojson",
        ],
        "traces": [
            "getaberget_20m_9_traces.geojson",
        ],
    },
    "Getaberget8_20m_120820_orto.tif": {
        "areas": [
            "getaberget_20m_8_3_area.geojson",
        ],
        "traces": [
            "getaberget_20m_8_traces.geojson",
        ],
    },
    "Getaberget7_20m_100820_orto.tif": {
        "areas": [
            "getaberget_20m_7_1_area.geojson",
            "getaberget_20m_7_2_area.geojson",
        ],
        "traces": [
            "getaberget_20m_7_traces.geojson",
        ],
    },
    "Getaberget5_20m_100820_orto.tif": {
        "areas": [
            "getaberget_20m_5_1_area.geojson",
        ],
        "traces": [
            "getaberget_20m_5_traces.geojson",
        ],
    },
    "Getaberget2_20m_070820_orto.tif": {
        "areas": [
            "getaberget_20m_2_1_area.geojson",
            "getaberget_20m_2_2_area.geojson",
        ],
        "traces": [
            "getaberget_20m_2_traces.geojson",
        ],
    },
    "Getaberget1_20m_070820_orto.tif": {
        "areas": [
            "getaberget_20m_1_1_area.geojson",
            "getaberget_20m_1_2_area.geojson",
            "getaberget_20m_1_3_area.geojson",
            "getaberget_20m_1_4_area.geojson",
        ],
        "traces": [
            "getaberget_20m_1_traces.geojson",
        ],
    },
    "Havsvidden_20m_7_8_2020.tif": {
        "areas": [
            "havsvidden_20m_1_area.geojson",
        ],
        "traces": [
            "havsvidden_20m_traces.geojson",
        ],
    },
}


def visualize_drone_rasters(
    traces_paths: List[Path] = typer.Option(...),
    area_paths: List[Path] = typer.Option(...),
    raster_path: Path = typer.Option(...),
    output_path: Path = typer.Option(...),
    # polygons: bool = typer.Option(...),
):
    """
    Visualize drone rasters.
    """
    # raster_name = raster_path.name
    # raster_areas = RASTER_AREA_PAIRS[raster_name]["areas"]
    # raster_traces = RASTER_AREA_PAIRS[raster_name]["traces"]
    # area_paths = [data.ALAND_20M_AREA_DATA_PATH / name for name in raster_areas]
    # traces_paths = [data.ALAND_20M_TRACES_DATA_PATH / name for name in raster_traces]
    area_gdfs = [read_geofile(path) for path in area_paths]
    traces_gdfs = [read_geofile(path) for path in traces_paths]

    fig, ax = plt.subplots()
    with rasterio.open(raster_path) as raster:

        show(raster.read(), transform=raster.transform, ax=ax)

    for traces_gdf in traces_gdfs:
        traces_gdf.plot(color="blue", ax=ax, linewidth=0.25)

    for area_gdf in area_gdfs:
        area_gdf.boundary.plot(color="red", ax=ax)

    # Add scalebar
    # background.add_scale_bar(ax=ax, bbox_coords=(0.9, 0.1))

    # Remove axes
    sns.despine(ax=ax, right=True, left=True, top=True, bottom=False)
    plt.tick_params(
        axis="y",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        left=False,
        labelleft=False,
    )  # labels along the bottom edge are off
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda value, _: round(value / 1000, 1))
    )
    ax.xaxis.set_tick_params(labelsize="xx-large")
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(500))

    fig.savefig(output_path, bbox_inches="tight")

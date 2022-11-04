"""
Utilities for analysing background data.
"""

from enum import Enum, unique
from pathlib import Path
from typing import List, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
import pandera as pa
from beartype import beartype
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnchoredOffsetbox
from matplotlib_scalebar import scalebar
from shapely.geometry import LineString, MultiPolygon, Polygon

JAATIKON_TULOSUUNTA = "JAATIKON_TULOSUUNTA"
SUHTEELLINEN_IKA = "SUHTEELLINEN_IKA"

SUITE = "SUITE_"

ROCK_NAME = "ROCK_NAME_"

LAYER = "br200k_lithological_unit"


@beartype
def remove_invalid_border(line: LineString):
    """
    Check for completely invalid LineString geometries.
    """
    try:

        line.is_simple
        return True
    except Exception:
        return False


def format_func_m_to_km(value, tick_number):
    """
    Format meters to km.
    """
    return int(value / 1000)


@beartype
def bedrock_gdf_load(bedrock_path: Path, layer: str = LAYER) -> gpd.GeoDataFrame:
    """
    Load bedrock_gdf layer.
    """
    bedrock_gdf = gpd.read_file(bedrock_path, layer=layer)
    assert isinstance(bedrock_gdf, gpd.GeoDataFrame)
    return bedrock_gdf


@beartype
def bedrock_gdf_clip(
    bedrock_gdf: gpd.GeoDataFrame, extent_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Clip bedrock_gdf to extent.

    Extent should contain on (Multi)Polygon.
    """
    assert extent_gdf.shape[0] == 1
    extent_poly = extent_gdf.geometry.values[0]
    assert isinstance(extent_poly, (Polygon, MultiPolygon))
    bedrock_gdf_clipped = bedrock_gdf.loc[bedrock_gdf.intersects(extent_poly)]
    assert isinstance(bedrock_gdf_clipped, gpd.GeoDataFrame)
    return bedrock_gdf_clipped


@beartype
def shoreline_gdf_largest(shoreline_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Get largest shorelines.

    shoreline_gdf should already be processed to only contain valid geometries.
    """
    assert shoreline_gdf.shape[0] > 0
    poly_area_col = "poly_area"
    sorted = shoreline_gdf.sort_values(by=poly_area_col, ascending=False)
    assert isinstance(sorted, gpd.GeoDataFrame)
    largest_indexes = sorted.index[0:400]
    assert isinstance(largest_indexes, pd.Index)
    largest = shoreline_gdf.iloc[largest_indexes]
    assert isinstance(largest, gpd.GeoDataFrame)
    return largest


@beartype
def bedrock_gdf_suite_union(
    bedrock_gdf: gpd.GeoDataFrame,
    suite_filter: str = "Åland rapakivi suite",
    other_suite: Optional[str] = None,
) -> gpd.GeoDataFrame:
    """
    Create a union polygon of a suite from bedrock map.

    If other_suite is passed then the gdf is filtered to NOT suite_filter
    and all not filtered are assumed to be part of other_suite.
    """
    other_suite_is_none = other_suite is None

    # Clip to suite condition
    condition = (
        bedrock_gdf[SUITE] == suite_filter
        if other_suite_is_none
        else bedrock_gdf[SUITE] != suite_filter
    )
    clipped = bedrock_gdf.loc[condition]

    # Union the whole suite into single geometry, Polygon or MultiPolygon
    unioned = clipped.unary_union
    assert isinstance(unioned, (Polygon, MultiPolygon))

    # Determine resulting suite
    result_suite = suite_filter if other_suite_is_none else other_suite

    # Wrap the geometry in GeoDataFrame
    bedrock_gdf_union = gpd.GeoDataFrame(
        {"geometry": [unioned], **{"SUITE_": [result_suite]}},
        crs=bedrock_gdf.crs,
    )
    return bedrock_gdf_union


@beartype
def circle_bounds_center_bottom(bounds: np.ndarray) -> Tuple[float, float]:
    """
    Resolve center bottom from circle bounds.
    """
    min_x, min_y, max_x, max_y = bounds
    assert all(isinstance(value, float) for value in (min_x, min_y, max_x, max_y))
    bottom = min_y
    center = max_x - (max_x - min_x) / 2
    return center, bottom


@beartype
def resolve_largest_polygon(polygons: List[Polygon]) -> Polygon:
    """
    Resolve largest polygon.
    """
    areas = [polygon.area for polygon in polygons]

    index_of_max = areas.index(max(areas))

    return polygons[index_of_max]


def add_scale_bar(ax: Axes, bbox_coords: Tuple[float, float]):
    """
    Add scale bar.
    """
    # https://geopandas.org/en/stable/gallery/matplotlib_scalebar.html

    # Override to allow finegrained location setting
    # Also pull request for that matter here:
    # https://github.com/ppinard/matplotlib-scalebar/pull/40

    # Create partial class of AnchoredOffsetbox
    my_anchored = lambda *args, **kwargs: AnchoredOffsetbox(  # noqa: E731
        *args, **kwargs, bbox_to_anchor=bbox_coords, bbox_transform=ax.transAxes
    )
    # Override in scalebar.py
    scalebar.AnchoredOffsetbox = my_anchored
    # Create scalebar (note no location set here)
    sb = scalebar.ScaleBar(1, "m", length_fraction=0.5)
    ax.add_artist(sb)


def add_north_arrow(ax: Axes, x: float, y: float, arrow_length: float):
    """
    Add north arrow with annotate.
    """
    # Add north arrow
    # x, y, arrow_length = 0.86, 0.93, 0.05
    xytext = (x, y - arrow_length)
    ax.annotate(
        "",
        xy=(x, y),
        xytext=xytext,
        arrowprops=dict(facecolor="black", width=1.5, headwidth=8),
        ha="center",
        va="center",
        fontsize=20,
        xycoords=ax.transAxes,
    )
    ax.text(
        x=xytext[0] + 0.02,
        y=xytext[1] + 0.02,
        s="N",
        transform=ax.transAxes,
        fontsize="x-large",
        fontweight="bold",
    )


@unique
class Age(Enum):

    """
    Enums for age strings.
    """

    UNDEFINED = "Ikäsuhde määrittelemätön"
    OLDER = "Vanhempi uurresuunta"
    YOUNGEST = "Nuorin uurresuunta"


STRIATIONS_SCHEMA = pa.DataFrameSchema(
    columns={
        JAATIKON_TULOSUUNTA: pa.Column(int, checks=pa.Check.in_range(0, 360)),
        SUHTEELLINEN_IKA: pa.Column(
            str, checks=pa.Check.isin([age.value for age in Age])
        ),
    }
)

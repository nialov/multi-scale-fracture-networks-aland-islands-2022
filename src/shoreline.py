"""
Create processed shoreline.
"""


from pathlib import Path

import geopandas as gpd
import typer
from shapely.wkt import loads

import background
from fractopo.general import read_geofile


def shoreline(
    aland_clip_box_wkt_path: Path = typer.Argument(...),
    shoreline_path: Path = typer.Argument(...),
    output: Path = typer.Argument(...),
):
    """
    Create processed shoreline.
    """
    shoreline_gdf = read_geofile(shoreline_path).to_crs("EPSG:3067")
    assert isinstance(shoreline_gdf, gpd.GeoDataFrame)
    shoreline_gdf["poly_area"] = shoreline_gdf.geometry.area
    processed_shoreline = background.shoreline_gdf_largest(shoreline_gdf=shoreline_gdf)

    clipped = gpd.clip(processed_shoreline, loads(aland_clip_box_wkt_path.read_text()))

    clipped.to_file(output, driver="GeoJSON")

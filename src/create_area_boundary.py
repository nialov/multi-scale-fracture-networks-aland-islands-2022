"""
Script to convert area polygon to line boundary.
"""

from pathlib import Path

import typer
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon

from fractopo.general import read_geofile
from utils import print


def _create_tmp_boundary(
    geo_path: Path, boundary_path: Path, polygons: bool, buffer_value: float
):
    """
    Convert geometries to boundary buffer.
    """
    # Convert polygon area to boundary buffer
    boundary_path.parent.mkdir(exist_ok=True)
    gdf = read_geofile(geo_path)
    boundaries = gdf.boundary if polygons else gdf.geometry
    assert all(
        isinstance(boundary, (LineString, MultiLineString)) for boundary in boundaries
    )
    # boundaries_buffered = boundaries.buffer(0.25)
    boundaries_buffered = boundaries.buffer(buffer_value)
    assert all(
        isinstance(boundary, (Polygon, MultiPolygon))
        for boundary in boundaries_buffered
    )
    if boundaries_buffered.empty:
        print(f"Empty geodataframe {geo_path}.")
        boundary_path.touch(exist_ok=True)
        return
    boundaries_buffered.to_file(boundary_path, driver="GeoJSON")


def create_area_boundary(
    geo_path: Path = typer.Argument(...),
    boundary_path: Path = typer.Argument(...),
    polygons: bool = typer.Option(...),
):
    """
    Create buffered boundary from area.
    """
    buffer_value = 1.0 if polygons else 0.1
    assert geo_path.exists()
    boundary_path.unlink(missing_ok=True)
    boundary_path.parent.mkdir(exist_ok=True, parents=True)
    _create_tmp_boundary(
        geo_path=geo_path,
        boundary_path=boundary_path,
        polygons=polygons,
        buffer_value=buffer_value,
    )

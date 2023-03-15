"""
Network characterization of each scale.
"""

import json
import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
import typer
from beartype.typing import List

from fractopo.general import crop_to_target_areas, read_geofile
from utils import print


def convert_sequence_columns(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Convert sequence (list/tuple) type columns to string.

    Imported from tracerepo.
    """
    gdf = gdf.copy()
    if gdf.empty:
        return gdf
    for column in gdf.columns.values:
        column_data = gdf[column]
        assert isinstance(column_data, pd.Series)
        first_val = column_data.values[0]
        if isinstance(first_val, (list, tuple)):
            logging.info(f"Converting {column} from {type(first_val)} to str.")
            gdf[column] = [str(tuple(item)) for item in column_data.values]
    return gdf


GEOJSON_DRIVER = "GeoJSON"


def write_geodata(gdf: gpd.GeoDataFrame, path: Path, driver: str = GEOJSON_DRIVER):
    """
    Write geodata with driver.

    Default is GeoJSON.

    Imported from tracerepo.
    """
    if gdf.empty:
        # Handle empty GeoDataFrames
        path.write_text(gdf.to_json())
    else:
        gdf = convert_sequence_columns(gdf)

        gdf.to_file(path, driver=driver)

    if driver != GEOJSON_DRIVER:
        return

    # Format geojson with indent of 1
    read_json = path.read_text()
    loaded_json = json.loads(read_json)
    dumped_json = json.dumps(loaded_json, indent=1)
    path.write_text(dumped_json)


def concatenate_scale(
    traces_paths: List[Path] = typer.Option(...),
    area_paths: List[Path] = typer.Option(...),
    concat_traces_path: Path = typer.Option(...),
    concat_area_path: Path = typer.Option(...),
):
    """
    Concatenate scale datasets.
    """
    # CONSOLE.print(f"WARNING: LOADING ONLY LIMITED DATASET FOR 20m", style="red")

    trace_gdfs = [read_geofile(traces_path) for traces_path in traces_paths]
    area_gdfs = [read_geofile(area_path) for area_path in area_paths]
    dataset_traces = pd.concat(trace_gdfs)
    dataset_areas = pd.concat(area_gdfs)
    print(f"Concatenated traces (n={dataset_traces.shape[0]})")
    print(f"Concatenated areas (n={dataset_areas.shape[0]})")

    assert isinstance(dataset_traces, gpd.GeoDataFrame)
    assert isinstance(dataset_areas, gpd.GeoDataFrame)

    # Only one crs in all
    assert len(set(gdf.crs for gdf in [*trace_gdfs, *area_gdfs])) == 1

    # Clip to target areas
    dataset_traces = crop_to_target_areas(
        dataset_traces, dataset_areas, keep_column_data=False
    )
    assert isinstance(dataset_traces, gpd.GeoDataFrame)

    concat_traces_path.parent.mkdir(exist_ok=True, parents=True)
    write_geodata(gdf=dataset_traces, path=concat_traces_path)
    write_geodata(gdf=dataset_areas, path=concat_area_path)

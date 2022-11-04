"""
Create latex table of trace counts by raster source.
"""

from pathlib import Path
from typing import List

import pandas as pd
import typer
from shapely.geometry import MultiPolygon

from fractopo.general import read_geofile
from utils import print


def data_count_table(
    latex_table_output: Path = typer.Argument(...),
    source_traces: List[Path] = typer.Option(...),
    source_names: List[str] = typer.Option(...),
    source_areas: List[Path] = typer.Option(...),
):
    """
    Create latex table of trace counts by raster source.
    """
    for opt in (source_traces, source_names):
        if len(opt) == 0:
            raise ValueError("Expected no inputs to be empty.")

    raster_source = "Raster Source"
    count = "Count"

    traces = [read_geofile(path) for path in source_traces]
    areas = [read_geofile(path) for path in source_areas]
    counts = []
    for traces, area, _ in zip(traces, areas, source_traces):
        intersecting = traces.intersects(MultiPolygon(area.geometry.values))

        # Accept small deviations due to spatial operation drift
        diff = abs(sum(intersecting) - traces.shape[0])
        assert diff < 5

        counts.append(sum(intersecting))

    # counts = [ti.shape[0] for ti in traces_intersect]
    assert all(isinstance(count, int) and count > 0 for count in counts)

    dataframe = pd.DataFrame({raster_source: source_names, count: counts})

    # dataframe.set_index(raster_source, inplace=True)

    dataframe.to_latex(
        latex_table_output,
        index=False,
        caption=(
            "Counts of digitized fractures and lineaments from each source"
            " that intersect their respective target areas."
        ),
        label="tab:lineament_counts",
    )

    print(f"Wrote latex count table to disk at {latex_table_output}")

"""
Create latex table of trace azimuth sets.
"""

import json
from pathlib import Path

import pandas as pd
import typer
from beartype.typing import List

from utils import print


def azimuth_set_table(
    latex_table_output: Path = typer.Argument(...),
    azimuth_set_json_path: Path = typer.Option(..., exists=True),
):
    """
    Create latex table of azimuths sets.
    """
    # starts = [set_range[0] for set_range in AZIMUTH_SET_RANGES]
    # ends = [set_range[1] for set_range in AZIMUTH_SET_RANGES]
    az_set_label = "Azimuth Set Label and Range (degrees)"
    occurs_in = "Relative Abundance"
    column_index_tuples = pd.MultiIndex.from_tuples(
        [
            ("", az_set_label),
            (occurs_in, "1:10"),
            (occurs_in, "1:20 000"),
            (occurs_in, "1:200 000"),
        ]
    )
    # occurs = ("OXX", "XXO", "XOX")
    azimuth_set_data = json.loads(azimuth_set_json_path.read_text())
    assert isinstance(azimuth_set_data, list)
    set_labels: List[str] = []
    for item in azimuth_set_data:
        assert isinstance(item, dict)
        set_labels.append(item["name"])
    values = [
        # N-S
        (set_labels[0], 3, 1, 2),
        # NE-SW
        (set_labels[1], 2, 2, 3),
        # WNW-ESE
        (set_labels[2], 1, 3, 1),
    ]
    dataframe = pd.DataFrame(
        values,
        columns=column_index_tuples,
    )

    tex_label = "tab:azimuth_set_table"
    caption = (
        "Visually determined multi-scale trace azimuth sets"
        " along with relative abundance in each scale where"
        " 1 equals the most abundant of the sets and 3 the least abundant."
    )
    dataframe_latex = dataframe.to_latex(
        None, index=False, label=tex_label, caption=caption
    )
    assert isinstance(dataframe_latex, str)
    latex_table_output.write_text(dataframe_latex)

    print(f"Wrote latex azimuth set table to disk at {latex_table_output}")

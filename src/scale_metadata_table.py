"""
Create latex table of fracture and lineament counts.
"""

from pathlib import Path
from textwrap import dedent

# import numpy as np
import pandas as pd
import typer
from beartype.typing import List

from fractopo.general import read_geofile


def scientific_notation(value: int):
    """
    Conditionally format value.
    """
    return f"{value:,.0f}"
    # if value < 100000:
    #     return f"{int(value)} $m^2$"
    # else:
    #     # return f"{value:.5E}"
    #     return f"{int(value / 1000)} $km^2$"


def scale_metadata_table(
    area_paths: List[Path] = typer.Argument(...),
    latex_table_output: Path = typer.Option(...),
):
    """
    Create latex table of scale of observation metadata.
    """
    name_col = "Representative Factor / Name"
    cell_col = "Cell Size [$m$]"
    area_col = "Total Target Area [$m^2$]"
    # ratio_col = "Ratio of Extent to Resolution (L/S)"
    area_values = [sum(read_geofile(path).area) for path in area_paths]
    dataframe = pd.DataFrame(
        {
            name_col: ["1:10", "1:20 000", "1:200 000"],
            cell_col: [0.0055, 5, 150],
            area_col: [scientific_notation(value) for value in area_values],
        }
    )

    dataframe.to_latex(
        latex_table_output,
        index=False,
        caption=dedent(
            r"""
                       Definitions of scales of observation used in this study.
                       The name of each scale comes from the
                       \textit{Representative Factor} that roughly represents
                       the resolution of the raster used as the base map.
                       The resolution of each named scale is given as the
                       \textit{Cell Size} of the raster. Areal extent is given
                       as the \textit{Total Target Trea} of the target areas
                       used in the digitization of fractures or interpretation
                       of lineaments.
                       """
        ).strip(),
        label="tab:scale_metadata",
        escape=False,
    )

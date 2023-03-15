"""
Create table of set-wise length distribution analysis.
"""

from pathlib import Path
from textwrap import dedent

import pandas as pd
import typer
from beartype.typing import List

# import utils


def float_formatter(value: float) -> str:
    """
    Format floats in table.
    """
    # Determine string (float or scientific notation)
    is_very_low = abs(value) < 0.01
    float_descriptive = f"{value:.2e}" if is_very_low else str(round(value, 2))
    return float_descriptive


def set_wise_fits_table(
    csv_paths: List[Path] = typer.Argument(...),
    latex_output: Path = typer.Option(...),
    csv_output: Path = typer.Option(...),
):
    """
    Create table of set-wise length distribution analysis.
    """
    dataframe = pd.concat([pd.read_csv(path, index_col="Name") for path in csv_paths])

    tex_label = "tab:set_wise_fits"
    # caption = (
    #     "Set-wise length distribution fits for all scales. "
    #     "PL = power-law, LN = lognormal. R-value represents"
    # )
    caption = dedent(
        """
        Parameters of length distribution fits for traces and
        branches for all scales along with set-wise fits of traces
        for all scales. PL = power-law, LN = lognormal. R-value is
        the loglikelihood ratio where a positive value indicates
        that the power-law fit is more likely and a negative value
        that the lognormal fit is more likely. The p-value
        represents the significance of the likelihood where low
        values (<0.1) correspond to high statistical significance.
    """.strip()
    )
    dataframe.to_csv(csv_output)
    dataframe_latex = dataframe.to_latex(
        None,
        index=True,
        label=tex_label,
        caption=caption,
        float_format=float_formatter,
        escape=False,
        column_format="lp{0.7cm}p{1.1cm}p{1.1cm}p{1.1cm}p{1.1cm}p{1.1cm}p{1.1cm}p{1.3cm}",
    )
    assert isinstance(dataframe_latex, str)
    latex_output.write_text(dataframe_latex)

"""
Create figure of censoring cut-of vs. power-law characteristics.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import typer
from beartype.typing import List
from joblib import Parallel, delayed, dump

from fractopo.analysis.length_distributions import determine_fit
from fractopo.general import JOBLIB_CACHE


def _determine_censoring_cut_off_fit(censoring_cut_off, lengths):
    censor_cut_off_lengths = lengths[lengths < censoring_cut_off]
    fit = determine_fit(censor_cut_off_lengths)
    return fit.xmin, fit.data, fit.alpha


@JOBLIB_CACHE.cache
def _resolve_censoring_fits(lengths: tuple, num: int = 20):
    lengths = np.array(lengths)
    censoring_cut_offs = np.linspace(
        start=lengths.max() + 0.001, stop=lengths.min(), num=num
    )
    # fits = []

    # for censoring_cut_off in censoring_cut_offs:
    #     censor_cut_off_lengths = lengths[lengths < censoring_cut_off]
    #     fit = determine_fit(censor_cut_off_lengths)
    #     fits.append(fit)

    fits = Parallel(n_jobs=-1)(
        delayed(_determine_censoring_cut_off_fit)(
            censoring_cut_off=censoring_cut_off,
            lengths=lengths,
        )
        for censoring_cut_off in censoring_cut_offs
    )
    assert isinstance(fits, list)

    return tuple(fits), tuple(censoring_cut_offs)


def _create_trace_lengths_dict(trace_length_csvs, trace_names):
    def _read_lengths(csv_path):
        return pd.read_csv(csv_path)["lengths"].values

    trace_lengths_dict = {
        trace_name: lengths
        for trace_name, lengths in zip(
            trace_names,
            map(
                _read_lengths,
                trace_length_csvs,
            ),
        )
    }
    return trace_lengths_dict


def censoring_analysis(
    trace_length_csvs: List[Path] = typer.Option(...),
    trace_names: List[str] = typer.Option(...),
    dump_path: Path = typer.Option(...),
):
    """
    Analyse censoring cut-off vs. power-law characteristics.
    """
    trace_lengths_dict = _create_trace_lengths_dict(
        trace_length_csvs=trace_length_csvs, trace_names=trace_names
    )

    all_fits, all_censoring_cut_offs = zip(
        *[
            _resolve_censoring_fits(lengths=tuple(trace_lengths), num=50)
            for trace_lengths in trace_lengths_dict.values()
        ]
    )

    dump((all_fits, all_censoring_cut_offs, trace_lengths_dict), dump_path)

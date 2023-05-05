"""
Create figure of censoring cut-of vs. power-law characteristics.
"""

import string
from functools import partial
from pathlib import Path
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import typer
from joblib import load
from matplotlib import ticker

from fractopo.analysis.length_distributions import calculate_exponent


class FitBase(NamedTuple):
    """
    Holder for fit data.
    """

    xmin: float
    data: np.ndarray
    alpha: float


def _visualize_effect_of_censoring(
    fig, censoring_cut_offs, fits, suptitle, lengths, row_idx, label_gen, color
):
    censoring_cut_offs = np.array(censoring_cut_offs)
    fits = [FitBase(xmin=fit[0], data=fit[1], alpha=fit[2]) for fit in fits]

    exponents = np.array([calculate_exponent(fit.alpha) for fit in fits])
    cut_offs = [fit.xmin for fit in fits]

    cut_off_proportions = np.array(
        [1 - (sum(fit.data > fit.xmin) / len(lengths)) for fit in fits]
    )

    # Plotting
    with sns.plotting_context(
        "paper", rc={"font": {"style": "italic"}}
    ), sns.axes_style("ticks"):
        axes = fig.subplots(1, 3)

        def _set_sub_label(ax, label_gen):
            ax.text(
                x=-0.2,
                y=1.08,
                s=next(label_gen),
                transform=ax.transAxes,
                fontsize="large",
            )

        # set_sub_label = lambda ax, label_gen: ax.text(
        #     x=-0.2,
        #     y=1.08,
        #     s=next(label_gen),
        #     transform=ax.transAxes,
        #     fontsize="large",
        # )
        colored_scatterplot = partial(
            sns.scatterplot, x=censoring_cut_offs, color=color
        )

        ax_1 = axes[0]
        colored_scatterplot(ax=ax_1, y=exponents)
        # sns.scatterplot(ax=ax_1, x=censoring_cut_offs, y=exponents, color=color)
        # ax_1.scatter(x=censoring_cut_offs, y=exponents)
        if row_idx == 0:
            ax_1.set_title("Censoring Cut-Off vs.\nPower-law Exponent")
        ax_1.set_ylabel("Power-law Exponent", fontstyle="italic")
        y_max = -1.0
        y_min = max([-4.5, exponents[~np.isnan(exponents)].min()]) - 0.5
        ax_1.set_ylim(y_min, y_max)
        ax_1.vlines(
            censoring_cut_offs[exponents < y_min], ymin=-5, ymax=-4.9, color=color
        )
        ax_1.vlines(
            censoring_cut_offs[exponents > y_max], ymin=1.1, ymax=0, color=color
        )
        # ax_1.yaxis.set_major_locator(ticker.MaxNLocator(integer=False))

        ax_2 = axes[1]
        colored_scatterplot(ax=ax_2, y=cut_offs)
        # sns.scatterplot(ax=ax_2, x=censoring_cut_offs, y=cut_offs, color=color)
        # ax_2.scatter(x=censoring_cut_offs, y=cut_offs)
        if row_idx == 0:
            ax_2.set_title("Censoring Cut-Off vs.\nTruncation Cut-Off")
        ax_2.set_ylabel("Truncation Cut-Off [$m$]", fontstyle="italic")

        ax_3 = axes[2]
        colored_scatterplot(ax=ax_3, y=cut_off_proportions * 100)
        # sns.scatterplot(ax=ax_3, x=censoring_cut_offs, y=cut_off_proportions * 100)
        # ax_3.scatter(x=censoring_cut_offs, y=cut_off_proportions)
        if row_idx == 0:
            ax_3.set_title("Censoring Cut-Off vs.\nCut-Off Proportion")
        ax_3.set_ylabel("Cut-Off %", fontstyle="italic")

        for ax in axes:
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=4))
            if row_idx == 2:
                ax.set_xlabel("Censoring Cut-Off [$m$]", fontstyle="italic")
            _set_sub_label(ax, label_gen)
            ax.grid(zorder=-10, color="black", alpha=0.25)
            # ax.set_xticks()
            # xticks = ax.get_xticks()
            # print(xticks)
            # assert False

        fig.subplots_adjust(wspace=0.45)
        fig.suptitle(
            suptitle, x=0.04, y=0.5, rotation=90, va="center", fontweight="bold"
        )
    return fig, axes


def censoring_plot(
    dump_path: Path = typer.Option(...),
    output_path: Path = typer.Option(...),
):
    """
    Create plot of censoring cut-off vs. power-law characteristics.
    """
    all_fits, all_censoring_cut_offs, trace_lengths_dict = load(dump_path)

    main_fig = plt.figure(figsize=(8.23, 6.5))
    subfigs = main_fig.subfigures(3)

    label_gen = map("({})".format, string.ascii_lowercase)
    colors = ["darkblue", "darkred", "darkgreen"]

    for idx, (fig, fits, suptitle, censoring_cut_offs, lengths, color) in enumerate(
        zip(
            subfigs,
            all_fits,
            trace_lengths_dict,
            all_censoring_cut_offs,
            trace_lengths_dict.values(),
            colors,
        )
    ):
        # Populates subfigures of main_fig
        _visualize_effect_of_censoring(
            fig=fig,
            fits=fits,
            suptitle=suptitle,
            censoring_cut_offs=censoring_cut_offs,
            lengths=lengths,
            row_idx=idx,
            label_gen=label_gen,
            color=color,
        )

    main_fig.savefig(output_path, bbox_inches="tight")
    plt.close("all")

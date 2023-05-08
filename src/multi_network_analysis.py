"""
Network characterization of all scales together.
"""

import json
import logging
from pathlib import Path
from textwrap import dedent

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import powerlaw
import typer
from beartype.typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# import utils
from fractopo import MultiNetwork
from fractopo.analysis import length_distributions
from fractopo.analysis.length_distributions import Dist
from fractopo.analysis.network import Network
from fractopo.general import MINIMUM_LINE_LENGTH, NAME, Param, ParamInfo, read_geofile
from utils import print


def _KS(self, data=None):
    """
    Override powerlaw.Distribution.KS
    """
    if data is None and hasattr(self, "parent_Fit"):
        data = self.parent_Fit.data
    data = powerlaw.trim_to_range(data, xmin=self.xmin, xmax=self.xmax)
    if len(data) < 2:
        print("Not enough data. Returning np.nan")
        self.D = np.nan
        self.D_plus = np.nan
        self.D_minus = np.nan
        self.Kappa = np.nan
        self.V = np.nan
        self.Asquare = np.nan
        return self.D

    if hasattr(self, "parent_Fit"):
        bins = self.parent_Fit.fitting_cdf_bins
        Actual_CDF = self.parent_Fit.fitting_cdf
        ind = bins >= self.xmin
        bins = bins[ind]
        Actual_CDF = Actual_CDF[ind]
        dropped_probability = Actual_CDF[0]
        Actual_CDF -= dropped_probability
        Actual_CDF /= 1 - dropped_probability
    else:
        bins, Actual_CDF = powerlaw.cdf(data)

    Theoretical_CDF = self.cdf(bins)

    CDF_diff = Theoretical_CDF - Actual_CDF

    self.D_plus = CDF_diff.max()
    self.D_minus = -1.0 * CDF_diff.min()
    self.Kappa = 1 + np.mean(CDF_diff)

    self.V = self.D_plus + self.D_minus
    self.D = max(self.D_plus, self.D_minus)
    # self.Asquare = np.sum(
    #     ((CDF_diff**2) / (Theoretical_CDF * (1 - Theoretical_CDF) + 1e-12))[1:]
    # )
    return self.D


powerlaw.Distribution.KS = _KS


def save_fig(
    fig: Figure,
    results_dir: Path,
    name: str,
    extension: Literal["png", "svg"] = "png",
    **kwargs,
):
    """
    Save figure as svg image to results dir.
    """
    assert results_dir.exists() and results_dir.is_dir()
    assert len(name) > 0
    fig.savefig(results_dir / f"{name}.{extension}", bbox_inches="tight", **kwargs)
    plt.close("all")


def add_identifier(ax, identifier):
    """
    Add identifier to multi-scale length plots.
    """
    ax.text(
        x=0.07,
        y=0.07,
        s=identifier,
        fontdict=dict(fontsize="xx-large", style="italic", weight="bold"),
        transform=ax.transAxes,
    )


def basic_latex_table_formatter(
    value: Union[str, float, int]
) -> Union[str, float, int]:
    """
    Format table values for latex table.
    """
    if isinstance(value, int):
        return str(value)

    elif isinstance(value, float):
        if abs(value) < 0.01 or value > 100000:
            return "{:.2e}".format(value)
        elif np.isclose(value % 1, 0):
            return str(int(value))
        else:
            return str(round(value, 2))
    elif isinstance(value, str):
        return value
    else:
        raise ValueError(f"Expected str, int or float as cell type. Got {type(value)}")


def _setup_length_plot_axlims(
    ax: Axes,
    length_array: np.ndarray,
    ccm_array: np.ndarray,
    # cut_off: float,
):
    """
    Set ax limits for length plotting.
    """
    # truncated_length_array = (
    #     length_array[length_array > cut_off] if cut_off is not None else length_array
    # )

    # TODO: Anomalous very low value lengths can mess up xlims
    left_base = (
        np.quantile(length_array, 0.001)
        if length_array.min() < 0.001
        else length_array.min()
    )
    left = left_base / 10
    # left = length_array.min() / 10
    right = length_array.max() * 10
    bottom = ccm_array.min() / 20
    top = ccm_array.max() * 100
    try:
        ax.set_xlim(left, right)
        ax.set_ylim(bottom, top)
    except ValueError:
        logging.error("Failed to set up x and y limits.", exc_info=True)
        # Don't try setting if it errors


def plot_distribution_fits(
    length_array: np.ndarray,
    label: str,
    using_branches: bool,
    use_probability_density_function: bool,
    cut_off: Optional[float] = None,
    fit: Optional[powerlaw.Fit] = None,
    fig: Optional[Figure] = None,
    ax: Optional[Axes] = None,
    fits_to_plot: Tuple[Dist, ...] = (Dist.EXPONENTIAL, Dist.LOGNORMAL, Dist.POWERLAW),
) -> Tuple[powerlaw.Fit, Figure, Axes]:
    """
    Plot length distribution and `powerlaw` fits.

    If a powerlaw.Fit is not given it will be automatically determined (using
    the optionally given cut_off).
    """
    if fit is None:
        # Determine powerlaw, exponential, lognormal fits
        fit = length_distributions.determine_fit(length_array, cut_off)

    if fig is None:
        if ax is None:
            # Create figure, ax
            fig, ax = plt.subplots(figsize=(7, 7))
        else:
            fig_maybe = ax.get_figure()
            assert isinstance(fig_maybe, Figure)
            fig = fig_maybe

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)
    assert ax is not None
    assert fit is not None

    # Get the x, y data from fit
    # y values are either the complementary cumulative distribution function
    # or the probability density function
    # Depends on use_probability_density_function boolean
    cut_off_is_lower = fit.xmin < length_array.min()
    if not use_probability_density_function:
        # complementary cumulative distribution
        truncated_length_array, y_array = fit.ccdf()
        full_length_array, full_y_array = fit.ccdf(original_data=True)
    else:
        # probability density function
        bin_edges, y_array = fit.pdf()

        # Use same bin_edges and y_array if xmin/cut-off is lower than
        # smallest line length
        full_bin_edges, full_y_array = fit.pdf(original_data=True)

        # fit.pdf returns the bin edges. These need to be transformed to
        # centers for plotting.
        truncated_length_array = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        full_length_array = (full_bin_edges[:-1] + full_bin_edges[1:]) / 2.0

        # filter out zeros
        is_zero_y = np.isclose(y_array, 0.0)
        is_zero_full_y = np.isclose(full_y_array, 0.0)
        truncated_length_array = truncated_length_array[~is_zero_y]
        full_length_array = full_length_array[~is_zero_full_y]
        y_array = y_array[~is_zero_y]
        full_y_array = full_y_array[~is_zero_full_y]

    assert len(truncated_length_array) == len(y_array)
    assert len(full_length_array) == len(full_y_array)

    # Plot truncated length scatter plot
    ax.scatter(
        x=truncated_length_array,
        y=y_array,
        s=25,
        label=label,
        alpha=1.0,
        color="black",
        marker="x",
    )

    if not cut_off_is_lower:
        # Normalize full_ccm_array to the truncated ccm_array
        full_y_array = full_y_array / (
            full_y_array[len(full_y_array) - len(y_array)] / y_array.max()
        )
        # Plot full length scatter plot with different color and transparency
        ax.scatter(
            x=full_length_array,
            y=full_y_array,
            s=3,
            # label=f"{label} (cut)",
            alpha=0.5,
            color="gray",
            marker="x",
            zorder=-10,
        )

    # Plot the actual fits (powerlaw, exp...)
    for fit_distribution in fits_to_plot:
        length_distributions.plot_fit_on_ax(
            ax,
            fit,
            fit_distribution,
            use_probability_density_function=use_probability_density_function,
        )

    # Plot cut-off if applicable

    # Set title with exponent
    # rounded_exponent = round(length_distributions.calculate_exponent(fit.alpha), 3)
    # target = "Branches" if using_branches else "Traces"
    # if not plain:
    ax.set_title(
        label,
        fontdict=dict(fontsize="xx-large"),
    )

    # Setup of ax appearance and axlims
    length_distributions.setup_ax_for_ld(
        ax,
        using_branches=using_branches,
        indiv_fit=True,
        use_probability_density_function=use_probability_density_function,
    )
    _setup_length_plot_axlims(
        ax=ax,
        length_array=truncated_length_array,
        ccm_array=y_array,
    )

    return fit, fig, ax


def _scale_network_analysis(
    network: Network,
    scale_output_dir: Path,
):
    """
    Conduct network analysis of a scale.
    """
    numerical_desc = network.numerical_network_description()
    numerical_desc_df = pd.DataFrame([numerical_desc])

    # Clean old
    if scale_output_dir.exists():
        for path in scale_output_dir.iterdir():
            path.unlink()

    # scale_output_dir: Path = data.NETWORK_OUTPUTS_PATH / scale.value
    scale_output_dir.mkdir(exist_ok=True, parents=True)

    csv_output_path = scale_output_dir / "numerical_desc.csv"

    numerical_desc_df.to_csv(csv_output_path)

    print(f"Saved numerical characteristics to: {csv_output_path}")
    print("Creating network plots.")

    with mpl.rc_context(
        rc={
            # "legend.fontsize": 13.0,
            "font.size": 14.0,
            # "xtick.major.size": 12.0,
            # "xtick.minor.size": 12.0,
        }
    ):
        _, fig, _ = network.plot_trace_azimuth(
            visualize_sets=True, append_azimuth_set_text=True, add_abundance_order=True
        )
    save_fig(
        fig=fig, results_dir=scale_output_dir, name="trace_rose_plot", extension="svg"
    )

    # Save lengths to csvs in scale_output_dir
    trace_lengths_df = pd.DataFrame({"lengths": network.trace_length_array})
    branch_lengths_df = pd.DataFrame({"lengths": network.branch_length_array})
    trace_lengths_df.to_csv(scale_output_dir / "trace_lengths.csv")
    branch_lengths_df.to_csv(scale_output_dir / "branch_lengths.csv")

    with mpl.rc_context(
        rc={
            # "legend.fontsize": "small",
            "font.size": 12.0,
            # "axes.titlesize": "small",
        }
    ):
        fit, fig, ax = network.plot_trace_lengths()
        ax.set_xlim(
            max(fit.data.min(), 0.1) / 50,
            fit.data.max() * 5,
        )
        save_fig(
            fig=fig,
            results_dir=scale_output_dir,
            name="trace_length_plot",
            extension="svg",
        )

        fit, fig, ax = network.plot_branch_lengths()
        ax.set_xlim(
            max(fit.data.min(), 0.1) / 50,
            # network.branch_data.length_array.min() / 10,
            fit.data.max() * 5,
        )
        save_fig(
            fig=fig,
            results_dir=scale_output_dir,
            name="branch_length_plot",
            extension="svg",
        )

    # Set-wise length distributions as numeric table
    name_key = "Name"
    count_key = "n"
    cut_off_prop_col = "{} lengths cut off proportion"
    column_renames_base = {
        "{} power_law exponent": "PL Exp.",
        "{} power_law cut-off": r"PL Cut-Off [$m$]",
        cut_off_prop_col: r"Cut-Off \%",
        "{} lognormal sigma": "LN Sigma",
        "{} lognormal mu": "LN Mu",
        "{} power_law vs. lognormal R": "PL vs. LN R",
        "{} power_law vs. lognormal p": "PL vs. LN p",
    }

    all_desc_traces: Dict[str, Any] = network.trace_lengths_powerlaw_fit_description
    all_desc_traces[name_key] = f"{network.name} Traces All"
    all_desc_traces[count_key] = len(network.trace_length_array)

    all_desc_branches: Dict[str, Any] = network.branch_lengths_powerlaw_fit_description
    all_desc_branches_mod = {}
    for key in column_renames_base:
        trace_key = key.format("trace")
        branch_key = key.format("branch")
        # Set values of branch descriptions to same name as trace descriptions
        all_desc_branches_mod[trace_key] = all_desc_branches[branch_key]
    all_desc_branches_mod[name_key] = f"{network.name} Branches All"
    all_desc_branches_mod[count_key] = len(network.branch_length_array)

    descs = [all_desc_traces, all_desc_branches_mod]
    for (
        azimuth_set_name,
        set_lengths,
    ) in network.trace_data.azimuth_set_length_arrays.items():
        fit = length_distributions.determine_fit(length_array=set_lengths, cut_off=None)
        desc: Dict[str, Any] = length_distributions.describe_powerlaw_fit(
            fit=fit, length_array=set_lengths, label="trace"
        )
        desc[name_key] = f"{network.name} Traces {azimuth_set_name}"
        desc[count_key] = len(set_lengths)
        descs.append(desc)

    set_wise_df = pd.DataFrame(descs)
    set_wise_df.set_index(name_key, inplace=True, drop=True)

    column_renames_traces = {
        key.format("trace"): value for key, value in column_renames_base.items()
    }
    column_renames_all = {
        name_key: name_key,
        count_key: count_key,
        **column_renames_traces,
    }

    set_wise_df.drop(
        columns=[
            column for column in set_wise_df.columns if column not in column_renames_all
        ],
        inplace=True,
    )
    set_wise_df = set_wise_df[[col for col in column_renames_all if col != "Name"]]
    assert isinstance(set_wise_df, pd.DataFrame)

    # Multiple cut-off proportion to percents
    cut_off_prop_col_traces = cut_off_prop_col.format("trace")
    set_wise_df[cut_off_prop_col_traces] = (
        set_wise_df[cut_off_prop_col_traces].values * 100
    )
    set_wise_df.rename(columns=column_renames_all, inplace=True)

    set_wise_csv_path = scale_output_dir / "set_wise_df.csv"
    set_wise_df.to_csv(set_wise_csv_path)

    # Also create set_wise plots for traces
    _, figs, _ = network.plot_trace_azimuth_set_lengths()
    for fig, azimuth_set in zip(figs, network.azimuth_set_names):
        clean_label = "".join(filter(str.isalpha, azimuth_set))
        save_fig(fig=fig, results_dir=scale_output_dir, name=clean_label)

    # Save branches and nodes
    network.write_branches_and_nodes(output_dir_path=scale_output_dir)

    # Appendix table of lognormal and exponential fits to full length data
    column_renames_appendix_base = {
        "power_law exponent": "PL Exp.",
        "lognormal sigma": "LN Sigma",
        "lognormal mu": "LN Mu",
        "exponential lambda": "Exp Lambda",
        "lognormal Kolmogorov-Smirnov distance D": "LN D",
        "exponential Kolmogorov-Smirnov distance D": "Exp D",
        "lognormal vs. exponential R": "LN vs. Exp R",
        "lognormal vs. exponential p": "LN vs. Exp p",
    }

    all_desc_appendix_traces: Dict[str, Any] = network.trace_data.describe_fit(
        cut_off=MINIMUM_LINE_LENGTH,
    )
    all_desc_appendix_traces[name_key] = f"{network.name} Traces"
    all_desc_appendix_traces[count_key] = len(network.trace_length_array)

    all_desc_appendix_branches: Dict[str, Any] = network.branch_data.describe_fit(
        cut_off=MINIMUM_LINE_LENGTH,
    )
    all_desc_appendix_branches[name_key] = f"{network.name} Branches"
    all_desc_appendix_branches[count_key] = len(network.branch_length_array)

    appendix_df = pd.DataFrame([all_desc_appendix_traces, all_desc_appendix_branches])
    appendix_df.rename(columns=column_renames_appendix_base, inplace=True)
    appendix_columns = [name_key, count_key, *column_renames_appendix_base.values()]
    appendix_df = appendix_df[appendix_columns]
    appendix_df.set_index(name_key, inplace=True, drop=True)
    appendix_df_path = scale_output_dir / "appendix_df.csv"
    appendix_df.to_csv(appendix_df_path)

    # Appendix figure of lognormal and exponential length distribution fits
    # to full data

    for using_branches, line_data in zip(
        [False, True], [network.trace_data, network.branch_data]
    ):
        fit, fig, ax = plot_distribution_fits(
            length_array=line_data.length_array,
            label=network.name,
            using_branches=using_branches,
            use_probability_density_function=False,
            cut_off=MINIMUM_LINE_LENGTH,
            fits_to_plot=(
                length_distributions.Dist.EXPONENTIAL,
                length_distributions.Dist.LOGNORMAL,
                length_distributions.Dist.POWERLAW,
            ),
        )
        save_fig(
            fig=fig,
            results_dir=scale_output_dir,
            name="branch_length_plot_full"
            if using_branches
            else "trace_length_plot_full",
            extension="svg",
        )


def _pretty_name(scale: str):
    split = scale.split("_")
    start, end = split[0], split[1]
    end_int = int(end)
    end_pretty = f"{end_int:,}".replace(",", " ")
    return f"{start}:{end_pretty}"


def multi_network_analysis(
    multi_scale_outputs_path: Path = typer.Argument(...),
    traces_paths: List[Path] = typer.Option(..., file_okay=True, exists=True),
    area_paths: List[Path] = typer.Option(..., file_okay=True, exists=True),
    network_output_paths: List[Path] = typer.Option(..., file_okay=False, exists=False),
    scale_names: List[str] = typer.Option(...),
    azimuth_set_json_path: Path = typer.Option(..., exists=True),
    latex_output_path: Path = typer.Option(...),
):
    """
    Conduct multi-scale network analysis.
    """
    # Make plot directory
    multi_scale_outputs_path.mkdir(exist_ok=True, parents=True)

    # Set multi-scale network characteristics
    azimuth_set_data = json.loads(azimuth_set_json_path.read_text())
    assert isinstance(azimuth_set_data, list)
    set_labels: List[str] = []
    set_ranges: List[Tuple[int, int]] = []
    for item in azimuth_set_data:
        assert isinstance(item, dict)
        set_labels.append(item["name"])
        set_ranges.append((item["start"], item["end"]))

    # Collect Networks
    networks = []
    for (
        tp,
        ap,
        scale,
        scale_output_dir,
    ) in zip(traces_paths, area_paths, scale_names, network_output_paths):
        trace_gdf, area_gdf = read_geofile(tp), read_geofile(ap)
        network = Network(
            trace_gdf=trace_gdf,
            area_gdf=area_gdf,
            name=_pretty_name(scale),
            circular_target_area=True,
            truncate_traces=True,
            determine_branches_nodes=True,
            azimuth_set_ranges=tuple(set_ranges),
            azimuth_set_names=tuple(set_labels),
        )

        _scale_network_analysis(network=network, scale_output_dir=scale_output_dir)

        networks.append(network)

    # Create DataFrame of network descriptions
    network_desc_df = pd.DataFrame(
        [network.numerical_network_description() for network in networks]
    )
    # Set Network name as index
    network_desc_df.set_index("Name", inplace=True)

    # Write to disk
    network_desc_path = multi_scale_outputs_path / "numerical_descriptions.csv"
    network_desc_df.to_csv(network_desc_path)

    # Create MultiNetwork from loaded Networks
    multi_network = MultiNetwork(tuple(networks))

    ternary_colors = ["darkblue", "darkred", "darkgreen"]
    # Plot branch ternary plot
    fig, _, _ = multi_network.plot_branch(colors=ternary_colors)
    save_fig(
        fig=fig,
        results_dir=multi_scale_outputs_path,
        name="branches",
        extension="svg",
        dpi=300,
    )

    # Plot xyi ternary plot
    fig, _, _ = multi_network.plot_xyi(colors=ternary_colors)
    save_fig(
        fig=fig,
        results_dir=multi_scale_outputs_path,
        name="xyi",
        extension="svg",
        dpi=300,
    )

    # Plot trace optimized multi-scale length distribution
    _, optimized_mld = multi_network.multi_length_distributions(
        using_branches=False
    ).optimize_cut_offs()
    _, fig, _ = optimized_mld.plot_multi_length_distributions(
        automatic_cut_offs=False, plot_truncated_data=True
    )
    save_fig(
        fig=fig,
        results_dir=multi_scale_outputs_path,
        name="trace_lengths_opt",
    )

    def append_unit(value: ParamInfo) -> str:
        """
        Compose parameter description.
        """
        return f"{value.name} [{value.unit}]"

    # Choose columns and their types and potential renames
    columns: Dict[str, Tuple[Optional[str], Type]] = {
        NAME: (None, str),
        Param.NUMBER_OF_TRACES.value.name: (
            f"{Param.NUMBER_OF_TRACES.value.name} $^a$",
            int,
        ),
        Param.NUMBER_OF_BRANCHES.value.name: (
            f"{Param.NUMBER_OF_BRANCHES.value.name} $^a$",
            int,
        ),
        Param.NUMBER_OF_TRACES_TRUE.value.name: (
            f"{Param.NUMBER_OF_TRACES_TRUE.value.name} $^b$",
            int,
        ),
        # Param.NUMBER_OF_BRANCHES_REAL.value.name: (
        #     None,
        #     int,
        # ),
        Param.AREA.value.name: (
            append_unit(Param.AREA.value),
            float,
        ),
        Param.TRACE_MAX_LENGTH.value.name: (
            append_unit(Param.TRACE_MAX_LENGTH.value),
            float,
        ),
        Param.TRACE_MEAN_LENGTH.value.name: (
            append_unit(Param.TRACE_MEAN_LENGTH.value),
            float,
        ),
        Param.BRANCH_MAX_LENGTH.value.name: (
            append_unit(Param.BRANCH_MAX_LENGTH.value),
            float,
        ),
        Param.BRANCH_MEAN_LENGTH.value.name: (
            append_unit(Param.BRANCH_MEAN_LENGTH.value),
            float,
        ),
        Param.FRACTURE_INTENSITY_P21.value.name: (
            append_unit(Param.FRACTURE_INTENSITY_P21.value),
            float,
        ),
        Param.DIMENSIONLESS_INTENSITY_P22.value.name: (
            None,
            float,
        ),
        Param.DIMENSIONLESS_INTENSITY_B22.value.name: (
            None,
            float,
        ),
        "trace power_law exponent": ("Trace Power-law Exponent", float),
        "branch power_law exponent": ("Branch Power-law Exponent", float),
        "X": (None, int),
        "Y": (None, int),
        "I": (None, int),
        "C - C": (None, int),
        "C - I": (None, int),
        "I - I": (None, int),
        Param.CONNECTIONS_PER_TRACE.value.name: (
            None,
            float,
        ),
        Param.CONNECTIONS_PER_BRANCH.value.name: (
            None,
            float,
        ),
    }

    # Numerical table of basic parameters
    basic_network_descriptions_df = multi_network.basic_network_descriptions_df(
        columns=columns
    )

    # Add relative proportions of nodes and branches
    for network_name in basic_network_descriptions_df.columns:
        values = basic_network_descriptions_df[network_name]
        x_count, y_count, i_count = values["X"], values["Y"], values["I"]
        nodes_sum = sum([x_count, y_count, i_count])
        cc_count, ci_count, ii_count = values["C - C"], values["C - I"], values["I - I"]
        branches_sum = sum([cc_count, ci_count, ii_count])
        x_perc = int((x_count / nodes_sum) * 100)
        y_perc = int((y_count / nodes_sum) * 100)
        i_perc = int((i_count / nodes_sum) * 100)
        cc_perc = int((cc_count / branches_sum) * 100)
        ci_perc = int((ci_count / branches_sum) * 100)
        ii_perc = int((ii_count / branches_sum) * 100)

        for label, value in zip(
            [
                "X",
                "Y",
                "I",
                "C - C",
                "C - I",
                "I - I",
            ],
            [
                rf"{int(x_count)} ({x_perc} \%)",
                rf"{int(y_count)} ({y_perc} \%)",
                rf"{int(i_count)} ({i_perc} \%)",
                rf"{int(cc_count)} ({cc_perc} \%)",
                rf"{int(ci_count)} ({ci_perc} \%)",
                rf"{int(ii_count)} ({ii_perc} \%)",
            ],
        ):
            basic_network_descriptions_df[network_name][label] = value

    # Add data source information
    sources = ("Orthomosaics", "LiDAR", "LiDAR+EM+Mag")
    source_data = dict(zip(basic_network_descriptions_df.columns, sources))
    sources_row = pd.Series(data=source_data, name="Data Source(s)")
    sources_df = pd.DataFrame(
        data=[sources_row], columns=basic_network_descriptions_df.columns
    )

    # Concat with original
    basic_network_descriptions_df = pd.concat(
        [sources_df, basic_network_descriptions_df]
    )

    # Write as csv and latex
    basic_network_descriptions_df.to_csv(
        multi_scale_outputs_path / "basic_descriptions.csv"
    )
    basic_network_descriptions_df_latex = basic_network_descriptions_df.to_latex(
        None,
        caption=dedent(
            r"""
                       Basic network descriptions of all scales of observation
                       with units displayed when applicable. EM =
                       Electromagnetic 3kHz quadrature. Mag = Magnetic rasters.
                       $^a$ Based on node counting \citep{sanderson_use_2015}.
                       $^b$ The absolute i.e. the "real" count of trace geometries.
        """.strip()
        ),
        # caption=(
        #     r"Basic network descriptions of all scales of observation"
        #     r" with units displayed when applicable."
        #     r" $^a$ Based on node counting "
        #     r"\citep{sanderson_use_2015}."
        # ),
        float_format=basic_latex_table_formatter,
        bold_rows=True,
        label="tab:basic_network_desc",
        escape=False,
    )
    assert isinstance(basic_network_descriptions_df_latex, str)
    # latex_output_path.write_text(utils.wide_table(basic_network_descriptions_df_latex))
    latex_output_path.parent.mkdir(parents=True, exist_ok=True)
    latex_output_path.write_text(basic_network_descriptions_df_latex)

    # Plot trace multi-scale length distribution
    using_branches = False
    _, _, fig, ax = multi_network.plot_multi_length_distribution(
        using_branches=using_branches,
        automatic_cut_offs=True,
        plot_truncated_data=True,
    )
    # Add identifier
    add_identifier(ax=ax, identifier="All")

    # Change legend font size
    for item in ax.get_legend().get_texts():
        item.set_fontsize("large")

    save_fig(
        fig=fig,
        results_dir=multi_scale_outputs_path,
        name="trace_lengths",
        extension="svg",
    )

    # Set-wise multi-scale distributions
    mlds, _, figs, axes = multi_network.plot_trace_azimuth_set_lengths(
        automatic_cut_offs=True,
        plot_truncated_data=True,
        # legend_font_size="large",
    )

    multi_scale_set_dir_path = multi_scale_outputs_path / "multi_scale_set_lengths"
    multi_scale_set_dir_path.mkdir(parents=True, exist_ok=True)
    for azimuth_set_label, fig, ax in zip(mlds.keys(), figs, axes):
        # Add set identifier
        add_identifier(ax=ax, identifier=azimuth_set_label)

        # Change legend font size
        for item in ax.get_legend().get_texts():
            item.set_fontsize("large")

        # Save plot
        clean_label = "".join(filter(str.isalpha, azimuth_set_label))
        output_name = multi_scale_set_dir_path / f"{clean_label}_lengths"
        save_fig(
            fig=fig,
            results_dir=multi_scale_set_dir_path,
            name=output_name.name,
            extension="svg",
        )

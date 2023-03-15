"""
Command-line entrypoint to analysis.
"""
import typer
from rich.traceback import install

import add_colorbar
import appendix_fits_table
import azimuth_set_table
import concatenate_scales
import create_area_boundary
import create_colorbar
import data_count_table
import lithology
import multi_network_analysis
import scale_metadata_table
import set_wise_fits_table
import shoreline
import striations
import visualize_drone_rasters

# Install rich python tracebacks
install()

APP = typer.Typer()

for entrypoint in (
    lithology.lithology,
    striations.striations,
    add_colorbar.add_colorbar,
    azimuth_set_table.azimuth_set_table,
    concatenate_scales.concatenate_scale,
    create_area_boundary.create_area_boundary,
    create_colorbar.create_colorbar,
    data_count_table.data_count_table,
    multi_network_analysis.multi_network_analysis,
    set_wise_fits_table.set_wise_fits_table,
    shoreline.shoreline,
    visualize_drone_rasters.visualize_drone_rasters,
    scale_metadata_table.scale_metadata_table,
    appendix_fits_table.appendix_fits_table,
):

    APP.command()(entrypoint)


if __name__ == "__main__":
    APP()

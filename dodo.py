"""
doit tasks for the project.
"""

import logging
import os
from functools import wraps
from itertools import chain
from pathlib import Path
from shutil import rmtree
from typing import Any, Dict, List, Tuple

from doit.tools import config_changed, run_once

ACTIONS = "actions"
FILE_DEP = "file_dep"
TASK_DEP = "task_dep"
TARGETS = "targets"
NAME = "name"
PARAMS = "params"
UP_TO_DATE = "uptodate"

QGIS_PATH = Path("qgis")
DATA_PATH = Path("data")
SRC_PATH = Path("src")
OUTPUTS_PATH = Path("outputs")
FIGURES_PATH = Path("figures")
FINAL_OUTPUTS_PATH = OUTPUTS_PATH / "final"

# Data paths
BACKGROUND_PATH = DATA_PATH / "background"
POETRY_LOCK = Path("poetry.lock")
FRACTOPO_FILES = [
    *list(Path("fractopo/fractopo").rglob("*.py")),
    Path("fractopo/poetry.lock"),
]
TRACE_DATA_PATH = DATA_PATH / "trace_data/traces"
AREA_DATA_PATH = DATA_PATH / "trace_data/area"
TRACES_20M_DIR = TRACE_DATA_PATH / "20m"
AREA_20M_DIR = AREA_DATA_PATH / "20m"
TRACES_20M_PATHS = [
    TRACES_20M_DIR / path
    for path in (
        "getaberget_20m_1_traces.geojson",
        "getaberget_20m_2_traces.geojson",
        "getaberget_20m_4_traces.geojson",
        "getaberget_20m_5_traces.geojson",
        "getaberget_20m_7_traces.geojson",
        "getaberget_20m_8_traces.geojson",
        "getaberget_20m_9_traces.geojson",
        "havsvidden_20m_traces.geojson",
    )
]
AREA_20M_PATHS = [
    AREA_20M_DIR / path
    for path in (
        "getaberget_20m_1_1_area.geojson",
        "getaberget_20m_1_2_area.geojson",
        "getaberget_20m_1_3_area.geojson",
        "getaberget_20m_1_4_area.geojson",
        "getaberget_20m_2_1_area.geojson",
        "getaberget_20m_2_2_area.geojson",
        "getaberget_20m_4_3_area.geojson",
        "getaberget_20m_5_1_area.geojson",
        "getaberget_20m_7_1_area.geojson",
        "getaberget_20m_7_2_area.geojson",
        "getaberget_20m_8_3_area.geojson",
        "getaberget_20m_9_2_area.geojson",
        "havsvidden_20m_1_area.geojson",
    )
]
TRACES_20K_DIR = TRACE_DATA_PATH / "infinity"
AREA_20K_DIR = AREA_DATA_PATH / "infinity"
TRACES_20K_PATHS = [
    TRACES_20K_DIR / path
    for path in ("ahvenanmaa_lidar_lineaments_1_20000_traces.geojson",)
]
AREA_20K_PATHS = [
    AREA_20K_DIR / path
    for path in (
        "geta_lidar_lineaments_1_20000_circular_area.geojson",
        "godby_lidar_lineaments_1_20000_circular_area.geojson",
    )
]
TRACES_200K_DIR = TRACE_DATA_PATH / "200000"
AREA_200K_DIR = AREA_DATA_PATH / "200000"
LIDAR_TRACES_200K_PATH = (
    TRACES_200K_DIR / "ahvenanmaa_lidar_lineaments_1_200000_traces.geojson"
)
EM_TRACES_200K_PATH = (
    TRACES_200K_DIR / "ahvenanmaa_em_lineaments_1_200000_traces.geojson"
)
MAG_TRACES_200K_PATH = (
    TRACES_200K_DIR / "ahvenanmaa_mag_lineaments_1_200000_traces.geojson"
)
INT_TRACES_200K_PATH = (
    TRACES_200K_DIR / "ahvenanmaa_integrated_lineaments_1_200000_traces.geojson"
)
AREA_200K_PATH = (
    AREA_200K_DIR / "ahvenanmaa_integ_lineaments_1_200k_circular_area.geojson"
)
ALAND_CLIP_BOX_WKT_PATH = DATA_PATH / "aland_clip_box_wkt.txt"
AZIMUTH_SET_JSON_PATH = DATA_PATH / "azimuth_sets.json"
MAP_DEM_PATH = QGIS_PATH / "map_dem.qgz"
MAP_EM_PATH = QGIS_PATH / "map_em.qgz"
MAP_MAG_1_PATH = QGIS_PATH / "map_mag_1.qgz"
MAP_MAG_2_PATH = QGIS_PATH / "map_mag_2.qgz"
MAP_MAG_3_PATH = QGIS_PATH / "map_mag_3.qgz"
MAP_INT_PATH = QGIS_PATH / "map_int.qgz"
ALL_MAPS = [
    MAP_DEM_PATH,
    MAP_EM_PATH,
    MAP_MAG_1_PATH,
    MAP_MAG_2_PATH,
    MAP_MAG_3_PATH,
    MAP_INT_PATH,
]
POINTS_OF_INTEREST_PATH = BACKGROUND_PATH / "points_of_interest.geojson"

# Intermediary output paths
BACKGROUND_OUTPUTS_PATH = OUTPUTS_PATH / "background"
QGIS_FIGS_PATH = QGIS_PATH / "outputs"
RASTERS_PATH = OUTPUTS_PATH / "rasters"
RESAMPLED_RASTERS_PATH = RASTERS_PATH / "resampled_rasters"
OPTIMIZED_RASTERS_PATH = RASTERS_PATH / "optimized_rasters"
CONCATENATED_DATA_PATH = OUTPUTS_PATH / "concatenated"
NETWORK_OUTPUTS_PATH = OUTPUTS_PATH / "networks"
QGIS_OUTPUTS_PATH = OUTPUTS_PATH / "qgis"
MULTI_SCALE_OUTPUTS_PATH = NETWORK_OUTPUTS_PATH / "multi-scale"
INTERSECTING_OUTPUTS_PATH = NETWORK_OUTPUTS_PATH / "intersecting"
STRIATIONS_GEOJSON_PATH = BACKGROUND_OUTPUTS_PATH / "striations.geojson"
SHORELINE_PATH = BACKGROUND_OUTPUTS_PATH / "shoreline_GSHHS_f_L1.geojson"
ADMINISTRATIVE_BOUNDARIES_PATH = (
    BACKGROUND_OUTPUTS_PATH / "administrative-boundaries.geojson"
)
FULL_BEDROCK_GEOJSON_PATH = BACKGROUND_OUTPUTS_PATH / "bedrock_of_finland_200k.geojson"
SFINLAND_BEDROCK_GEOJSON_PATH = (
    BACKGROUND_OUTPUTS_PATH / "bedrock_of_finland_200k_s_finland.geojson"
)
NUMERICAL_DESC_PATH = MULTI_SCALE_OUTPUTS_PATH / "numerical_descriptions.csv"
BASIC_DESC_PATH = MULTI_SCALE_OUTPUTS_PATH / "basic_descriptions.csv"
MULTI_SCALE_SET_LENGTHS = MULTI_SCALE_OUTPUTS_PATH / "multi_scale_set_lengths"
SHORELINE_PROCESSED_PATH = BACKGROUND_OUTPUTS_PATH / "shoreline_processed.geojson"
SET_WISE_CSV_OUTPUT_PATH = OUTPUTS_PATH / "concat_set_wise_table.csv"
COLORBAR_OUTPUTS_PATH = OUTPUTS_PATH / "colorbars"
SOURCE_RASTERS_OUTPUTS_PATH = OUTPUTS_PATH / "source_rasters"


DRONE_RASTER_MONTAGE = OUTPUTS_PATH / "drone_raster_montage.jpg"

# Python script paths
CONCATENATE_SCALES_PY_PATH = SRC_PATH / "concatenate_scales.py"
DATA_LOAD_PY_PATH = SRC_PATH / "data_load.py"
UTILS_PY_PATH = SRC_PATH / "utils.py"
MULTI_NETWORK_ANALYSIS_PY_PATH = SRC_PATH / "multi_network_analysis.py"
DATA_COUNT_TABLE_PY_PATH = SRC_PATH / "data_count_table.py"
AZIMUTH_SET_TABLE_PY_PATH = SRC_PATH / "azimuth_set_table.py"
SET_WISE_FITS_PY_PATH = SRC_PATH / "set_wise_fits_table.py"
SCALE_METADATA_TABLE_PY_PATH = SRC_PATH / "scale_metadata_table.py"
SHORELINE_PY_PATH = SRC_PATH / "shoreline.py"
CREATE_AREA_BOUNDARY_PY_PATH = SRC_PATH / "create_area_boundary.py"
VISUALIZE_DRONE_RASTERS_PY_PATH = SRC_PATH / "visualize_drone_rasters.py"
LITHOLOGY_PY_PATH = SRC_PATH / "lithology.py"
CLI_PY_PATH = SRC_PATH / "cli.py"
STRIATIONS_PY_PATH = SRC_PATH / "striations.py"
CREATE_COLORBAR_PY_PATH = SRC_PATH / "create_colorbar.py"
ADD_COLORBAR_PY_PATH = SRC_PATH / "add_colorbar.py"


# Final output paths
AZIMUTH_SET_TABLE = FINAL_OUTPUTS_PATH / "azimuth_set_table.tex"
DATA_COUNT_TABLE = FINAL_OUTPUTS_PATH / "data_count_table.tex"
MULTI_NETWORK_ANALYSIS_MONTAGE = FINAL_OUTPUTS_PATH / "multi_scale_ternary_montage.pdf"
SET_WISE_MULTI_SCALE_FITS = FINAL_OUTPUTS_PATH / "set_wise_multi_scale_fits.pdf"
NETWORK_ANALYSIS_MONTAGE = FINAL_OUTPUTS_PATH / "scale_characterizations.pdf"
BACKGROUND_LITHOLOGY = FINAL_OUTPUTS_PATH / "bedrock_aland.pdf"
MULTI_SCALE_ANALYSIS_TABLE = FINAL_OUTPUTS_PATH / "basic_descriptions.tex"
DRONE_INDEX_FIGURE = FIGURES_PATH / "combined_location_map_mod.png"
DRONE_RASTER_MONTAGE_WITH_INDEX = (
    FINAL_OUTPUTS_PATH / "drone_raster_montage_with_index.jpg"
)
SCALE_METADATA_TABLE = FINAL_OUTPUTS_PATH / "scale_metadata_table.tex"
SOURCE_MONTAGE = FINAL_OUTPUTS_PATH / "source_montage.jpg"
SOURCE_MONTAGE_APPENDIX = FINAL_OUTPUTS_PATH / "source_montage_appendix.jpg"
SET_WISE_TEX_OUTPUT_PATH = FINAL_OUTPUTS_PATH / "concat_set_wise_table.tex"
SCALE_1_20000_FIG_PATH = FINAL_OUTPUTS_PATH / "scale_1_20000_fig.jpg"

# Static variables
MONTAGE_PLOT_TYPES = ("trace_rose_plot", "trace_length_plot", "branch_length_plot")
RASTER_AREA_PAIRS = {
    # "getaberget1_20m_070820_orto_test_1_1_area.tif": [
    #     "getaberget_20m_1_1_area.geojson",
    # ],
    "Getaberget4_20m_080820_orto.tif": {
        "areas": [
            "getaberget_20m_4_3_area.geojson",
        ],
        "traces": [
            "getaberget_20m_4_traces.geojson",
        ],
    },
    "Getaberget9_20m_120820_orto.tif": {
        "areas": [
            "getaberget_20m_9_2_area.geojson",
        ],
        "traces": [
            "getaberget_20m_9_traces.geojson",
        ],
    },
    "Getaberget8_20m_120820_orto.tif": {
        "areas": [
            "getaberget_20m_8_3_area.geojson",
        ],
        "traces": [
            "getaberget_20m_8_traces.geojson",
        ],
    },
    "Getaberget7_20m_100820_orto.tif": {
        "areas": [
            "getaberget_20m_7_1_area.geojson",
            "getaberget_20m_7_2_area.geojson",
        ],
        "traces": [
            "getaberget_20m_7_traces.geojson",
        ],
    },
    "Getaberget5_20m_100820_orto.tif": {
        "areas": [
            "getaberget_20m_5_1_area.geojson",
        ],
        "traces": [
            "getaberget_20m_5_traces.geojson",
        ],
    },
    "Getaberget2_20m_070820_orto.tif": {
        "areas": [
            "getaberget_20m_2_1_area.geojson",
            "getaberget_20m_2_2_area.geojson",
        ],
        "traces": [
            "getaberget_20m_2_traces.geojson",
        ],
    },
    "Getaberget1_20m_070820_orto.tif": {
        "areas": [
            "getaberget_20m_1_1_area.geojson",
            "getaberget_20m_1_2_area.geojson",
            "getaberget_20m_1_3_area.geojson",
            "getaberget_20m_1_4_area.geojson",
        ],
        "traces": [
            "getaberget_20m_1_traces.geojson",
        ],
    },
    "Havsvidden_20m_7_8_2020.tif": {
        "areas": [
            "havsvidden_20m_1_area.geojson",
        ],
        "traces": [
            "havsvidden_20m_traces.geojson",
        ],
    },
}
TRACES_LIST = [
    TRACES_20M_PATHS,
    # [TRACES_20K_PATH],
    TRACES_20K_PATHS,
    [LIDAR_TRACES_200K_PATH],
    [EM_TRACES_200K_PATH],
    [MAG_TRACES_200K_PATH],
    [INT_TRACES_200K_PATH],
]
AREAS_LIST = [
    AREA_20M_PATHS,
    # [AREA_20K_PATH],
    AREA_20K_PATHS,
    [AREA_200K_PATH],
    [AREA_200K_PATH],
    [AREA_200K_PATH],
    [AREA_200K_PATH],
]
SCALE_1_10 = "1_10"
SCALE_1_20000 = "1_20000"
SCALE_1_200000_LIDAR = "1_200000_lidar"
SCALE_1_200000_EM = "1_200000_em"
SCALE_1_200000_MAG = "1_200000_mag"
SCALE_1_200000_INT = "1_200000_int"
DATASET_NAMES = [
    SCALE_1_10,
    SCALE_1_20000,
    SCALE_1_200000_LIDAR,
    SCALE_1_200000_EM,
    SCALE_1_200000_MAG,
    SCALE_1_200000_INT,
]
assert len(TRACES_LIST) == len(AREAS_LIST)
assert len(TRACES_LIST) == len(DATASET_NAMES)


def resolve_task_name(func) -> str:
    """
    Resolve name of task without ``task_`` prefix.
    """
    return func.__name__.replace("task_", "")


def _qgis_available():
    return Path("/mnt/c/Program Files/QGIS 3.18/bin/qgis-bin.exe").exists()


def non_reproducible(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _qgis_available():
            return func(*args, **kwargs)
        else:
            logging.warning(
                f"Task {func.__name__} is not available. See Caveats in README.rst."
            )
            return

    return wrapper


def ignore_in_ci(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.environ.get("CI", None) is None:
            return func(*args, **kwargs)
        else:
            logging.warning(
                f"Task {func.__name__} is not available. See Caveats in README.rst."
            )
            return

    return wrapper


def _concat_paths(name: str) -> Tuple[Path, Path]:
    assert name in DATASET_NAMES
    traces_path = CONCATENATED_DATA_PATH / f"{name}_traces.geojson"
    area_path = CONCATENATED_DATA_PATH / f"{name}_area.geojson"
    return traces_path, area_path


def _check_paths(paths: List[Path], is_file: bool = True):
    """
    Check that paths exist.
    """

    def check_path(path: Path, is_file: bool = True):
        """
        Check that path exists.
        """
        if not path.exists() and (path.is_file() and is_file):
            raise FileNotFoundError(f"Expected {path} to exist.")

    for path in paths:
        check_path(path, is_file=is_file)


def _mkdir_cmd(directory: Path) -> str:
    return f"mkdir -p {directory}"


def command(parts: List[Any]) -> str:
    """
    Compile command-line command from parts.
    """
    return " ".join(list(map(str, parts)))


@non_reproducible
def task_qgis_source_rasters():
    """
    Create QGIS prints of source rasters with lineaments.

    Requires external QGIS and must be run from WSL. Due
    to these requirements the task is not available
    if your system does not match the system of the author
    exactly which is unlikely. The qgis tasks are responsible
    for the 1:200 000 and 1:20 000 lineament figures.
    """

    # if not _qgis_available():
    #     return

    def in_windows_file_system():
        current_path = Path(".").absolute()
        if not current_path.is_relative_to("/mnt/c/"):
            raise EnvironmentError(
                "Cannot run source_rasters task from wsl file system."
            )
        return True

    # qgz_paths = list(QGIS_PATH.glob("map_*.qgz"))

    for path in ALL_MAPS:
        target_path = QGIS_OUTPUTS_PATH / f"{path.stem}.jpg"

        yield {
            NAME: path.name,
            FILE_DEP: [
                path,
                QGIS_PATH / "create_print_layout.py",
                QGIS_PATH / "snapshots.bash",
                SHORELINE_PROCESSED_PATH,
            ],
            TASK_DEP: ["concatenate_scales"],
            TARGETS: [target_path],
            ACTIONS: [
                in_windows_file_system,
                f"cd qgis && ./snapshots.bash {path.name} || exit 0",
            ],
        }


@non_reproducible
def task_create_colorbar():
    """
    Create custom colorbars for rasters.
    """
    # if not _qgis_available():
    #     return
    labels = [
        "DEM (with hillshade)",
        "3 kHz quadrature",
        "Total field DGRF-65",
        "Sharp-filtered DGRF-65",
        "Tilt derivative DGRF-65",
        "DEM (with hillshade)",
    ]
    colormaps = ["RdBu_r", "gray", "gray_r", "gray", "gray_r", "RdBu_r"]
    vmins = [-1, -100, -1000, 0, -1.6, -1]
    vmaxs = [40, 2000, 2000, 255, 1.6, 40]
    cmd_base = command(
        [
            "python",
            CLI_PY_PATH,
            "create-colorbar",
            "--vmin='{}'",
            "--vmax='{}'",
            "--label='{}'",
            "--colormap='{}'",
            "--output='{}'",
        ]
    )
    for path, label, cmap, vmin, vmax in zip(ALL_MAPS, labels, colormaps, vmins, vmaxs):
        output_path = COLORBAR_OUTPUTS_PATH / path.with_suffix(".png").name
        cmd = cmd_base.format(vmin, vmax, label, cmap, output_path)
        yield {
            NAME: path.stem,
            FILE_DEP: [CREATE_COLORBAR_PY_PATH],
            UP_TO_DATE: [
                config_changed(
                    dict(
                        labels=labels,
                        colormaps=colormaps,
                        vmins=vmins,
                        vmaxs=vmaxs,
                        cmd=cmd_base,
                    )
                )
            ],
            ACTIONS: [_mkdir_cmd(COLORBAR_OUTPUTS_PATH), cmd],
            TARGETS: [output_path],
        }


@non_reproducible
def task_add_colorbar():
    """
    Add custom colorbars to rasters.
    """
    labels = ["A.", "C.", "A.", "B.", "B.", "D."]
    cmd_base = command(
        [
            "python",
            CLI_PY_PATH,
            "add-colorbar",
            # f"--map-path='{map_path}'",
            # f"--colorbar-path='{colorbar_path}'",
            # f"--label='{label}'",
            # f"--output-path='{output_path}'",
            "--map-path='{}'",
            "--colorbar-path='{}'",
            "--label='{}'",
            "--output-path='{}'",
        ]
    )

    # Resize all to be exactly the same size
    mogrify_cmd = command(
        [
            "mogrify",
            "-resize 3150x3097!",
            "{}",
        ]
    )
    for path, label in zip(ALL_MAPS, labels):
        map_path = QGIS_OUTPUTS_PATH / path.with_suffix(".jpg").name
        colorbar_path = COLORBAR_OUTPUTS_PATH / path.with_suffix(".png").name
        output_path = SOURCE_RASTERS_OUTPUTS_PATH / path.with_suffix(".jpg").name
        cmd = cmd_base.format(map_path, colorbar_path, label, output_path)
        mogrify_cmd_formatted = mogrify_cmd.format(output_path)
        yield {
            NAME: path.stem,
            FILE_DEP: [ADD_COLORBAR_PY_PATH, map_path, colorbar_path],
            UP_TO_DATE: [
                config_changed(
                    dict(labels=labels, cmd_base=cmd_base, mogrify_cmd=mogrify_cmd)
                )
            ],
            ACTIONS: [
                _mkdir_cmd(SOURCE_RASTERS_OUTPUTS_PATH),
                cmd,
                mogrify_cmd_formatted,
            ],
            TARGETS: [output_path],
        }


def add_label_to_image_cmd(path, label, x=30, y=60, fontsize=50):
    """
    Add label to image for imagemagick processing.
    """
    return [
        "-pointsize",
        str(fontsize),
        r"\( ",
        str(path),
        "-draw",
        f""" "text {x},{y} '{label}.'" """,
        r" \)",
    ]


@non_reproducible
def task_qgis_fig03_and_figA01_source_rasters_montage():
    """
    Create montage of raster prints.
    """
    # if not _qgis_available():
    #     return
    # target_path = FINAL_OUTPUTS_PATH / "source_montage.jpg"
    # target_appendix_path = FINAL_OUTPUTS_PATH / "source_montage_appendix.jpg"
    # dem_path = SOURCE_RASTERS_OUTPUTS_PATH / "map_dem.jpg"
    dem_path = SOURCE_RASTERS_OUTPUTS_PATH / MAP_DEM_PATH.with_suffix(".jpg").name
    em_path = SOURCE_RASTERS_OUTPUTS_PATH / MAP_EM_PATH.with_suffix(".jpg").name
    # mag_path = SOURCE_RASTERS_OUTPUTS_PATH / "map_mag_2.jpg"
    mag_1_path = SOURCE_RASTERS_OUTPUTS_PATH / MAP_MAG_1_PATH.with_suffix(".jpg").name
    mag_2_path = SOURCE_RASTERS_OUTPUTS_PATH / MAP_MAG_2_PATH.with_suffix(".jpg").name
    mag_3_path = SOURCE_RASTERS_OUTPUTS_PATH / MAP_MAG_3_PATH.with_suffix(".jpg").name
    int_path = SOURCE_RASTERS_OUTPUTS_PATH / MAP_INT_PATH.with_suffix(".jpg").name

    cmd_base = command(
        [
            "magick",
            "montage",
            "-background",
            "black",
            "-font",
            "Liberation-Mono-Bold",
            "{}",
            "-mattecolor",
            "black",
            "-fill",
            "black",
            "-stroke",
            "white",
            "-bordercolor",
            "black",
            "-geometry",
            "1100x",
            "-tile",
            # "2x2",
            "{}",
            "-border",
            "2",
            "-frame",
            "2",
            "{}",
        ]
    )
    indiv_opts = ""
    cmd = cmd_base.format(
        # " ".join(map(str, (dem_path, mag_2_path, em_path, int_path))),
        " ".join(
            [
                f"{indiv_opts} {path}"
                for path in (dem_path, mag_2_path, em_path, int_path)
            ]
        ),
        "2x2",
        SOURCE_MONTAGE,
    )
    paths_appendix = (mag_1_path, mag_3_path)
    cmd_appendix = cmd_base.format(
        " ".join(map(str, paths_appendix)), "1x2", SOURCE_MONTAGE_APPENDIX
    )

    yield {
        NAME: SOURCE_MONTAGE.name,
        FILE_DEP: [dem_path, em_path, mag_2_path, int_path],
        UP_TO_DATE: [config_changed(dict(cmd_base=cmd_base, indiv_opts=indiv_opts))],
        # TASK_DEP: ["qgis_source_rasters"],
        TASK_DEP: [resolve_task_name(task_qgis_source_rasters)],
        TARGETS: [SOURCE_MONTAGE],
        ACTIONS: [cmd],
    }

    yield {
        NAME: SOURCE_MONTAGE_APPENDIX.name,
        FILE_DEP: [*paths_appendix],
        UP_TO_DATE: [config_changed(cmd_base)],
        TASK_DEP: [resolve_task_name(task_qgis_source_rasters)],
        # TASK_DEP: ["qgis_source_rasters"],
        TARGETS: [SOURCE_MONTAGE_APPENDIX],
        ACTIONS: [cmd_appendix],
    }


@non_reproducible
def task_qgis_fig04_montage():
    """
    Create montage of 1:20k target area raster prints.
    """
    geta_path = QGIS_FIGS_PATH / "geta_1_20k_lineaments.jpg"
    godby_path = QGIS_FIGS_PATH / "godby_1_20k_lineaments.jpg"

    cmd_base = command(
        [
            "magick",
            "montage",
            "-background",
            "black",
            "-font",
            "Liberation-Mono-Bold",
            "{}",
            "-mattecolor",
            "black",
            "-fill",
            "black",
            "-stroke",
            "white",
            "-bordercolor",
            "black",
            "-geometry",
            "1100x",
            "-tile",
            "2x1",
            "-border",
            "2",
            "-frame",
            "2",
            "{}",
        ]
    )
    label_opts = dict(fontsize=250, y=240)
    cmd = cmd_base.format(
        # " ".join(map(str, (dem_path, mag_2_path, em_path, int_path))),
        " ".join(
            [
                " ".join(add_label_to_image_cmd(path=path, label=label, **label_opts))
                for path, label in zip((geta_path, godby_path), ("A", "B"))
            ]
        ),
        SCALE_1_20000_FIG_PATH,
    )

    yield {
        NAME: SCALE_1_20000_FIG_PATH.name,
        FILE_DEP: [geta_path, godby_path],
        UP_TO_DATE: [config_changed(dict(cmd_base=cmd_base, label_opts=label_opts))],
        TARGETS: [SCALE_1_20000_FIG_PATH],
        ACTIONS: [cmd],
    }


def task_final_fig01_background_lithology():
    """
    Create background figure from notebook execution.
    """
    deps = [
        SFINLAND_BEDROCK_GEOJSON_PATH,
        POINTS_OF_INTEREST_PATH,
        SHORELINE_PROCESSED_PATH,
        *AREA_20K_PATHS,
        AREA_200K_PATH,
        ALAND_CLIP_BOX_WKT_PATH,
        ADMINISTRATIVE_BOUNDARIES_PATH,
        LITHOLOGY_PY_PATH,
        STRIATIONS_PY_PATH,
        STRIATIONS_GEOJSON_PATH,
    ]
    _check_paths(deps)

    _, areas_20k = _concat_paths(name=SCALE_1_20000)
    cmd = command(
        [
            "python",
            # LITHOLOGY_PY_PATH,
            CLI_PY_PATH,
            "lithology",
            # bedrock
            SFINLAND_BEDROCK_GEOJSON_PATH,
            # shoreline
            SHORELINE_PROCESSED_PATH,
            # 20k areas
            areas_20k,
            # 200k area
            AREA_200K_PATH,
            # points of interest
            POINTS_OF_INTEREST_PATH,
            # clip box wkt file
            ALAND_CLIP_BOX_WKT_PATH,
            # administrative boundaries
            ADMINISTRATIVE_BOUNDARIES_PATH,
            # striations_path
            STRIATIONS_GEOJSON_PATH,
            # output path
            BACKGROUND_LITHOLOGY,
        ]
    )

    return {
        FILE_DEP: deps,
        TARGETS: [BACKGROUND_LITHOLOGY],
        ACTIONS: [_mkdir_cmd(BACKGROUND_OUTPUTS_PATH), cmd],
    }


def task_concatenate_scales():
    """
    Concatenate and clip datasets to respective areas.
    """
    traces_opt = "--traces-paths={}"
    area_opt = "--area-paths={}"

    for traces, areas, name in zip(TRACES_LIST, AREAS_LIST, DATASET_NAMES):

        concat_traces_path, concat_area_path = _concat_paths(name=name)
        cmd = command(
            [
                "python",
                CLI_PY_PATH,
                "concatenate-scale",
                *[traces_opt.format(trace) for trace in traces],
                *[area_opt.format(area) for area in areas],
                f"--concat-traces-path={concat_traces_path}",
                f"--concat-area-path={concat_area_path}",
            ]
        )

        yield {
            NAME: name,
            FILE_DEP: [*traces, *areas, CONCATENATE_SCALES_PY_PATH],
            ACTIONS: [_mkdir_cmd(CONCATENATED_DATA_PATH), cmd],
            TARGETS: [concat_traces_path, concat_area_path],
        }


def task_final_fig05_network_analysis_montage():
    """
    Create montage of network plots.
    """
    scales = [SCALE_1_10, SCALE_1_20000, SCALE_1_200000_INT]

    plot_svgs: Dict[str, List[Path]] = dict()
    scale_dirs = [OUTPUTS_PATH / f"networks/{scale}" for scale in scales]
    for scale_dir in scale_dirs:
        # scale_dir = OUTPUTS_PATH / f"networks/{scale}"
        for plot_type in MONTAGE_PLOT_TYPES:
            # svg_path = list(scale_dir.glob(f"{plot_type}.svg"))[0]
            svg_path = scale_dir / f"{plot_type}.svg"
            values = plot_svgs.get(plot_type, list())
            values.append(svg_path)
            plot_svgs[plot_type] = values

    # First create montages of rose and length plots individually
    montage_paths = []

    cmd_base = command(
        [
            "magick",
            "montage",
            "-font",
            "DejaVu-Sans",
        ]
    )
    cmd_montage_options = command(
        [
            "-geometry",
            "1080x1080+4+4",
            "-tile",
        ]
    )
    tilings = ("3x1", "1x3")
    density_option = "-density 300"
    for plot_type, plot_paths in plot_svgs.items():

        output_path_horizontal = OUTPUTS_PATH / f"networks/{plot_type}_montage.png"
        output_path_vertical = (
            OUTPUTS_PATH / f"networks/{plot_type}_vertical_montage.png"
        )
        output_paths = (output_path_horizontal, output_path_vertical)
        cmds = [
            command(
                [
                    cmd_base,
                    *[f"{density_option} {path.absolute()}" for path in plot_paths],
                    cmd_montage_options,
                    orient,
                    output_path,
                ]
            )
            for orient, output_path in zip(
                tilings,
                output_paths,
            )
        ]
        for output_path, cmd in zip(output_paths, cmds):
            yield {
                NAME: f"{plot_type}_{output_path.stem}",
                FILE_DEP: [*plot_paths],
                # UP_TO_DATE: [config_changed(cmd_base + str(tilings))],
                UP_TO_DATE: [
                    config_changed(
                        dict(
                            cmd_base=cmd_base,
                            tilings=str(tilings),
                            density_option=density_option,
                        )
                    )
                ],
                # TASK_DEP: ["final_multi_network_analysis"],
                TASK_DEP: [resolve_task_name(task_final_tab03_multi_network_analysis)],
                ACTIONS: [_mkdir_cmd(output_path.parent), cmd],
                TARGETS: [output_path],
            }
            # Do not add vertical plots for labeling
            if output_path == output_path_horizontal:
                montage_paths.append(output_path)

    # Then create montage of the individual montages into single final montage
    with_labels = [
        # ["-density", "300"]+
        add_label_to_image_cmd(path, label, fontsize=90, y=80, x=15)
        for path, label in zip(montage_paths, ("A", "B", "C"))
    ]
    montage_options = command(
        [
            "-geometry",
            "2200x+4+4",
            "-frame",
            "4",
            "-tile",
            "1x3",
        ]
    )
    final_montage_cmd = command(
        [
            "magick",
            "montage",
            "-font",
            "DejaVu-Sans",
            *list(chain(*with_labels)),
            montage_options,
            str(NETWORK_ANALYSIS_MONTAGE),
        ]
    )

    yield {
        NAME: "combined",
        FILE_DEP: [
            *montage_paths,
        ],
        UP_TO_DATE: [config_changed(final_montage_cmd)],
        # TASK_DEP: ["final_multi_network_analysis"],
        TASK_DEP: [resolve_task_name(task_final_tab03_multi_network_analysis)],
        ACTIONS: [
            _mkdir_cmd(NETWORK_ANALYSIS_MONTAGE.parent),
            final_montage_cmd,
        ],
        TARGETS: [NETWORK_ANALYSIS_MONTAGE],
    }


def task_final_fig06_multi_scale_fits_figure_montage():
    """
    Create montage of set-wise multi-scale polyfit plots.
    """

    def check_length_paths(dep_paths):
        for path in dep_paths:
            if not path.exists():
                raise FileNotFoundError(f"Expected {path} to exist.")

    # Sets defined in src/data.py
    sets = ("NS", "NESW", "WNWESE")
    all_path = MULTI_SCALE_OUTPUTS_PATH / "trace_lengths.svg"
    set_filenames = [f"{azi_set}_lengths.svg" for azi_set in sets]
    set_paths = [MULTI_SCALE_SET_LENGTHS / filename for filename in set_filenames]
    dep_paths = [all_path, *set_paths]
    # dep_paths_with_opt = [f"-density 300 {path}" for path in [all_path, *set_paths]]
    labels = ["A", "B", "C", "D"]
    label_opts = dict(fontsize=40, y=130)
    dep_paths_with_opt = [
        " ".join(
            add_label_to_image_cmd(f"-density 300 {path}", label=label, **label_opts)
        )
        for path, label in zip([all_path, *set_paths], labels)
    ]

    cmd = command(
        [
            "magick",
            "montage",
            "-font",
            "DejaVu-Sans",
            "-geometry",
            "+4+4",
            *dep_paths_with_opt,
            "-tile",
            "2x2",
            SET_WISE_MULTI_SCALE_FITS,
        ]
    )

    return {
        FILE_DEP: [*dep_paths],
        # TASK_DEP: ["final_multi_network_analysis"],
        TASK_DEP: [resolve_task_name(task_final_tab03_multi_network_analysis)],
        UP_TO_DATE: [config_changed(dict(cmd=cmd, label_opts=label_opts))],
        ACTIONS: [
            _mkdir_cmd(SET_WISE_MULTI_SCALE_FITS.parent),
            lambda: check_length_paths(dep_paths),
            cmd,
        ],
        TARGETS: [SET_WISE_MULTI_SCALE_FITS],
    }


def task_final_tab03_multi_network_analysis():
    """
    Determine multi-scale network characteristics and create montage.
    """
    cmd = [
        "python",
        str(CLI_PY_PATH),
        "multi-network-analysis",
        str(MULTI_SCALE_OUTPUTS_PATH),
        f"--azimuth-set-json-path={AZIMUTH_SET_JSON_PATH}",
        f"--latex-output-path={MULTI_SCALE_ANALYSIS_TABLE}",
    ]
    traces_paths_opt = "--traces-paths={}"
    area_paths_opt = "--area-paths={}"
    scale_names_opt = "--scale-names={}"
    network_outputs_opt = "--network-output-paths={}"

    file_deps = [
        MULTI_NETWORK_ANALYSIS_PY_PATH,
        POETRY_LOCK,
        *FRACTOPO_FILES,
        UTILS_PY_PATH,
        AZIMUTH_SET_JSON_PATH,
    ]
    output_dirs = []
    for scale in [SCALE_1_10, SCALE_1_20000, SCALE_1_200000_INT]:
        traces_path, area_path = _concat_paths(name=scale)
        scale_output_dir = NETWORK_OUTPUTS_PATH / scale
        cmd.extend(
            [
                traces_paths_opt.format(traces_path),
                area_paths_opt.format(area_path),
                scale_names_opt.format(scale),
                network_outputs_opt.format(scale_output_dir),
            ]
        )
        file_deps.extend([traces_path, area_path])
        output_dirs.append(scale_output_dir)

    return {
        TARGETS: [MULTI_SCALE_OUTPUTS_PATH, MULTI_SCALE_ANALYSIS_TABLE, *output_dirs],
        ACTIONS: [
            # Clean output dir before new analysis
            lambda: rmtree(MULTI_SCALE_OUTPUTS_PATH, ignore_errors=True),
            _mkdir_cmd(MULTI_SCALE_OUTPUTS_PATH),
            " ".join(cmd),
        ],
        FILE_DEP: file_deps,
        # TASK_DEP: ["concatenate_scales"],
        TASK_DEP: [resolve_task_name(task_concatenate_scales)],
    }


def task_final_fig07_multi_network_analysis_montage():
    """
    Create montage of results.
    """
    montage_target_plot_names = ["xyi.svg", "branches.svg"]
    montage_target_plots = [
        MULTI_SCALE_OUTPUTS_PATH / name for name in montage_target_plot_names
    ]
    with_labels = [
        ["-density", "300"]
        + add_label_to_image_cmd(path=path, label=label, x=30, y=240, fontsize=50)
        for path, label in zip(montage_target_plots, ("A", "B"))
    ]
    montage_cmd = command(
        [
            "magick",
            "montage",
            "-font",
            "DejaVu-Sans",
            *list(chain(*with_labels)),
            "-geometry",
            "x1200",
            "-tile",
            "1x2",
            str(MULTI_NETWORK_ANALYSIS_MONTAGE),
        ]
    )
    # optipng_cmd = command(
    #     [
    #         "optipng",
    #         "-o7",
    #         str(MULTI_NETWORK_ANALYSIS_MONTAGE),
    #     ]
    # )
    return {
        TARGETS: [MULTI_NETWORK_ANALYSIS_MONTAGE],
        ACTIONS: [
            _mkdir_cmd(MULTI_NETWORK_ANALYSIS_MONTAGE.parent),
            montage_cmd,
            # optipng_cmd,
        ],
        FILE_DEP: [*montage_target_plots],
        UP_TO_DATE: [
            config_changed(
                dict(
                    montage_cmd=montage_cmd,
                    # optipng_cmd=optipng_cmd,
                )
            )
        ],
        # TASK_DEP: ["final_multi_network_analysis"],
        TASK_DEP: [resolve_task_name(task_final_fig05_network_analysis_montage)],
    }


def task_final_tab02_data_count_table():
    """
    Create count table categorized by raster source for traces.
    """
    traces_paths_200k, area_paths_200k = zip(
        *[
            _concat_paths(name)
            for name in (
                SCALE_1_200000_LIDAR,
                SCALE_1_200000_MAG,
                SCALE_1_200000_EM,
                SCALE_1_200000_INT,
            )
        ]
    )

    traces_path_20k, area_path_20k = _concat_paths(SCALE_1_20000)
    traces_path_20m, area_path_20m = _concat_paths(SCALE_1_10)

    traces_paths = [*traces_paths_200k, traces_path_20k, traces_path_20m]
    area_paths = [*area_paths_200k, area_path_20k, area_path_20m]
    assert all(isinstance(path, Path) for path in [*traces_paths, *area_paths])

    traces_options = [f"--source-traces={path}" for path in traces_paths]
    area_options = [f"--source-areas={path}" for path in area_paths]

    names_200k = ["LiDAR", "Magnetic", "Electromagnetic", "Integrated"]
    names = [
        *[f"{name} 1:200 000" for name in names_200k],
        "LiDAR 1:20 000",
        "Orthomosaics 1:10",
    ]
    name_options = [f"--source-names='{name}'" for name in names]
    cmd = [
        "python",
        str(CLI_PY_PATH),
        "data-count-table",
        str(DATA_COUNT_TABLE),
        *traces_options,
        *name_options,
        *area_options,
    ]

    return {
        FILE_DEP: [
            *traces_paths,
            *area_paths,
            DATA_COUNT_TABLE_PY_PATH,
        ],
        ACTIONS: [_mkdir_cmd(INTERSECTING_OUTPUTS_PATH), " ".join(cmd)],
        TARGETS: [DATA_COUNT_TABLE, INTERSECTING_OUTPUTS_PATH],
    }


def task_processed_shoreline():
    """
    Process shoreline.
    """
    cmd = command(
        [
            "python",
            CLI_PY_PATH,
            "shoreline",
            # SHORELINE_PY_PATH,
            ALAND_CLIP_BOX_WKT_PATH,
            SHORELINE_PATH,
            SHORELINE_PROCESSED_PATH,
        ]
    )
    return {
        FILE_DEP: [
            SHORELINE_PY_PATH,
            SHORELINE_PATH,
            ALAND_CLIP_BOX_WKT_PATH,
        ],
        ACTIONS: [
            _mkdir_cmd(SHORELINE_PROCESSED_PATH.parent),
            cmd,
        ],
        TARGETS: [SHORELINE_PROCESSED_PATH],
    }


def task_final_tab04_azimuth_set_table():
    """
    Create azimuth set table with counts and occurrence.
    """
    cmd = command(
        [
            "python",
            CLI_PY_PATH,
            "azimuth-set-table",
            AZIMUTH_SET_TABLE,
            f"--azimuth-set-json-path={AZIMUTH_SET_JSON_PATH}",
        ]
    )

    return {
        FILE_DEP: [
            AZIMUTH_SET_TABLE_PY_PATH,
            MULTI_NETWORK_ANALYSIS_PY_PATH,
            UTILS_PY_PATH,
        ],
        ACTIONS: [_mkdir_cmd(AZIMUTH_SET_TABLE.parent), cmd],
        TARGETS: [AZIMUTH_SET_TABLE],
    }


def task_final_tab05_set_wise_fit_table():
    """
    Concatenate table of set-wise length distribution analysis from each scale.
    """
    scale_csvs = [
        OUTPUTS_PATH / f"networks/{scale}/set_wise_df.csv"
        for scale in (SCALE_1_10, SCALE_1_20000, SCALE_1_200000_INT)
    ]

    cmd = [
        "python",
        str(CLI_PY_PATH),
        "set-wise-fits-table",
        *list(map(str, scale_csvs)),
        "--latex-output",
        str(SET_WISE_TEX_OUTPUT_PATH),
        "--csv-output",
        str(SET_WISE_CSV_OUTPUT_PATH),
    ]

    return {
        FILE_DEP: [
            SET_WISE_FITS_PY_PATH,
            MULTI_NETWORK_ANALYSIS_PY_PATH,
            UTILS_PY_PATH,
            *scale_csvs,
        ],
        # TASK_DEP: ["final_multi_network_analysis"],
        TASK_DEP: [resolve_task_name(task_final_fig05_network_analysis_montage)],
        ACTIONS: [
            _mkdir_cmd(SET_WISE_TEX_OUTPUT_PATH.parent),
            _mkdir_cmd(SET_WISE_CSV_OUTPUT_PATH.parent),
            " ".join(cmd),
        ],
        TARGETS: [SET_WISE_TEX_OUTPUT_PATH, SET_WISE_CSV_OUTPUT_PATH],
    }


@ignore_in_ci
def task_visualize_rasters():
    """
    Plot rasters with traces and area.
    """
    # rasters = list(RASTERS_PATH.glob("*.tif"))
    rasters = [(RASTERS_PATH / raster_target) for raster_target in RASTER_AREA_PAIRS]
    resample_raster_cmd_base = "gdalwarp -tr 0.5 0.5 {} {}"
    for raster in rasters:
        resampled_raster = RESAMPLED_RASTERS_PATH / raster.name
        traces_names = RASTER_AREA_PAIRS[raster.name]["traces"]
        area_names = RASTER_AREA_PAIRS[raster.name]["areas"]
        traces_paths = [TRACES_20M_DIR / name for name in traces_names]
        area_paths = [AREA_20M_DIR / name for name in area_names]
        traces_path_opt = "--traces-paths={}"
        area_path_opt = "--area-paths={}"

        # Resample rasters so that matplotlib can plot them
        # resample_raster_cmd = f"gdalwarp -tr 0.5 0.5 {raster} {resampled_raster}"
        resample_raster_cmd = resample_raster_cmd_base.format(raster, resampled_raster)

        output_path = OPTIMIZED_RASTERS_PATH / resampled_raster.with_suffix(".png").name

        # f"python {VISUALIZE_DRONE_RASTERS_PY_PATH} {resampled_raster} {output_path}",
        visualize_cmd = command(
            [
                "python",
                CLI_PY_PATH,
                "visualize-drone-rasters",
                *[traces_path_opt.format(path) for path in traces_paths],
                *[area_path_opt.format(path) for path in area_paths],
                f"--raster-path={resampled_raster}",
                f"--output-path={output_path}",
            ]
        )
        yield {
            NAME: raster.name,
            FILE_DEP: [
                # Hash for raster is expensive time-wise to calculate so ignore
                # raster,
                VISUALIZE_DRONE_RASTERS_PY_PATH,
            ],
            # TASK_DEP: ["download_rasters"],
            TASK_DEP: [resolve_task_name(task_download_rasters)],
            UP_TO_DATE: [
                config_changed(
                    dict(
                        resample_raster_cmd=resample_raster_cmd,
                        visualize_cmd=visualize_cmd,
                    )
                ),
            ],
            TARGETS: [resampled_raster],
            ACTIONS: [
                f"rm -f {resampled_raster}",
                _mkdir_cmd(resampled_raster.parent),
                resample_raster_cmd,
                _mkdir_cmd(output_path.parent),
                visualize_cmd,
            ],
        }


@ignore_in_ci
def task_optimize_rasters_montage():
    """
    Create montage of drone rasters.
    """
    # Get paths to plots with raster+traces+area visualized
    rasters = [
        (OPTIMIZED_RASTERS_PATH / name).with_suffix(".png")
        for name in RASTER_AREA_PAIRS
    ]
    # Compose montage command
    montage_cmd = command(
        [
            "magick",
            "montage",
            "-font",
            "DejaVu-Sans",
            *rasters,
            # *list(chain(*rasters_with_labels)),
            "-geometry",
            "595x595",
            "-tile",
            "4x2",
            "-background",
            "none",
            "-bordercolor",
            "white",
            "-frame",
            "5",
            "-mattecolor",
            "black",
            DRONE_RASTER_MONTAGE,
        ]
    )

    def annotate(x: int, y: int, text: str) -> List[str]:
        cmd_list = [
            "-annotate",
            f"0x0+{x}+{y}",
            text,
        ]
        return cmd_list

    # Annotation conversion
    anno_cmd = command(
        [
            "convert",
            "-font",
            "DejaVu-Sans",
            "-pointsize",
            "60",
            "-stroke",
            "white",
            "-strokewidth",
            "2",
            *annotate(x=475, y=250, text="1"),
            *annotate(x=800, y=375, text="2"),
            *annotate(x=1650, y=275, text="3"),
            *annotate(x=2000, y=250, text="4"),
            *annotate(x=2100, y=375, text="5"),
            *annotate(x=175, y=850, text="6"),
            *annotate(x=625, y=825, text="7"),
            *annotate(x=900, y=1100, text="8"),
            *annotate(x=1325, y=900, text="9"),
            *annotate(x=1450, y=800, text="10"),
            *annotate(x=1450, y=1100, text="11"),
            *annotate(x=1650, y=950, text="12"),
            *annotate(x=2000, y=950, text="13"),
            DRONE_RASTER_MONTAGE,
            DRONE_RASTER_MONTAGE,
        ]
    )

    return {
        # TASK_DEP: ["visualize_rasters"],
        TASK_DEP: [resolve_task_name(task_visualize_rasters)],
        ACTIONS: [
            _mkdir_cmd(DRONE_RASTER_MONTAGE.parent),
            montage_cmd,
            anno_cmd,
        ],
        FILE_DEP: [*rasters],
        UP_TO_DATE: [config_changed(dict(montage_cmd=montage_cmd, anno_cmd=anno_cmd))],
        TARGETS: [DRONE_RASTER_MONTAGE],
    }


@ignore_in_ci
def task_final_fig02_add_index_to_drone_rasters():
    """
    Add index map to drone raster montage.
    """
    # Compose montage command
    cmd = command(
        [
            "magick",
            "montage",
            "-font",
            "DejaVu-Sans",
            *add_label_to_image_cmd(
                path=DRONE_INDEX_FIGURE, label="A", fontsize=125, y=100
            ),
            *add_label_to_image_cmd(
                path=DRONE_RASTER_MONTAGE, label="B", fontsize=125, y=120
            ),
            # str(DRONE_INDEX_FIGURE),
            # str(DRONE_RASTER_MONTAGE),
            "-geometry",
            "1800x",
            "-tile",
            "1x2",
            "-background",
            "none",
            "-bordercolor",
            "white",
            "-frame",
            "5",
            "-mattecolor",
            "black",
            DRONE_RASTER_MONTAGE_WITH_INDEX,
        ]
    )

    return {
        # TASK_DEP: ["optimize_rasters_montage"],
        TASK_DEP: [resolve_task_name(task_optimize_rasters_montage)],
        ACTIONS: [
            _mkdir_cmd(DRONE_RASTER_MONTAGE_WITH_INDEX.parent),
            cmd,
        ],
        FILE_DEP: [DRONE_INDEX_FIGURE, DRONE_RASTER_MONTAGE],
        UP_TO_DATE: [config_changed(cmd)],
        TARGETS: [DRONE_RASTER_MONTAGE_WITH_INDEX],
    }


def task_final_tab01_scale_metadata_table():
    """
    Create latex table of scale of observation metadata.
    """
    area_paths = []
    for scale in (SCALE_1_10, SCALE_1_20000, SCALE_1_200000_INT):
        _, area_path = _concat_paths(scale)
        area_paths.append(area_path)

    cmd = [
        "python",
        str(CLI_PY_PATH),
        "scale-metadata-table",
        *list(map(str, area_paths)),
        f"--latex-table-output={SCALE_METADATA_TABLE}"
        # str(SCALE_METADATA_TABLE),
    ]

    return {
        FILE_DEP: [
            SCALE_METADATA_TABLE_PY_PATH,
            *area_paths,
        ],
        ACTIONS: [_mkdir_cmd(SCALE_METADATA_TABLE.parent), " ".join(cmd)],
        TARGETS: [SCALE_METADATA_TABLE],
    }


@ignore_in_ci
def task_download_rasters():
    """
    Download drone orthomosaics from zenodo if not found locally.
    """
    # Download url for Getaberget orthomosaic tiff rasters
    url = "https://zenodo.org/record/4719627/files/geta_orthomosaics.zip?download=1"

    # Temporary path for downloaded zip
    zip_path = OUTPUTS_PATH / "geta_orthomosaics.zip"

    actions = [
        # Create OUTPUTS_PATH directory
        f"mkdir -p {OUTPUTS_PATH}",
        # Download rasters in a zip file
        # --continue flag is used for if download is interrupted,
        # it can be continued seamlessly
        f"wget {url} --progress=dot --continue --output-document  {zip_path}",
        # Create RASTERS_PATH directory
        f"mkdir -p {RASTERS_PATH}",
        # Unzip rasters to RASTERS_PATH (removed -u flag as it only updated based on file age)
        f"unzip -q -o {zip_path} -d {RASTERS_PATH}",
        # Remove zip file
        # f"rm -f {zip_path}",
    ]
    return {
        ACTIONS: actions,
        TARGETS: [zip_path, RASTERS_PATH],
        UP_TO_DATE: [run_once, config_changed(dict(url=url, actions=actions))],
    }


def task_download_striations():
    """
    Download striations from Geological Survey of Finland WFS service.
    """
    # WFS service
    wfs_url = "WFS:http://gtkdata.gtk.fi/arcgis/services/Rajapinnat/GTK_Maapera_WFS/MapServer/WFSServer?"

    layer = "Rajapinnat_GTK_Maapera_WFS:uurteet"

    actions = [
        # Create BACKGROUND_OUTPUTS_PATH directory
        f"mkdir -p {BACKGROUND_OUTPUTS_PATH}",
        f"ogr2ogr -f GEOJSON {STRIATIONS_GEOJSON_PATH} {wfs_url} {layer}",
    ]

    return {
        ACTIONS: actions,
        TARGETS: [STRIATIONS_GEOJSON_PATH],
        UP_TO_DATE: [
            run_once,
            config_changed(
                dict(
                    wfs_url=wfs_url,
                    layer=layer,
                    actions=actions,
                )
            ),
        ],
    }


def task_download_administrative_boundaries():
    """
    Download administrative boundaries geojson from opendatasoft.com.
    """
    # Download url
    download_url = "https://public.opendatasoft.com/explore/dataset/world-administrative-boundaries/download/?format=geojson&timezone=Europe/Helsinki&lang=en"

    actions = [
        # Create BACKGROUND_OUTPUTS_PATH directory
        f"mkdir -p {BACKGROUND_OUTPUTS_PATH}",
        f"wget '{download_url}' --continue --output-document {ADMINISTRATIVE_BOUNDARIES_PATH}",
    ]
    return {
        ACTIONS: actions,
        TARGETS: [ADMINISTRATIVE_BOUNDARIES_PATH],
        UP_TO_DATE: [
            run_once,
            config_changed(dict(download_url=download_url, actions=actions)),
        ],
    }


def task_download_bedrock():
    """
    Download bedrock of finland 200k data.
    """
    # Download url for Getaberged orthomosaic tiff rasters
    wfs_url = "WFS:http://gtkdata.gtk.fi/arcgis/services/Rajapinnat/GTK_Kalliopera_WFS/MapServer/WFSServer?"

    # Layer name
    # layer = "Rajapinnat_GTK_Kalliopera_WFS:kalliopera_200k_kivilajit"
    # Changed 2022.10.25 due to upstream (weird) layer name changes. Data seems
    # slightly updated.
    layer = "Rajapinnat_GTK_Kalliopera_WFS:Litologiset_yksiköt_200k"

    actions = [
        # Create BACKGROUND_OUTPUTS_PATH directory
        f"mkdir -p {BACKGROUND_OUTPUTS_PATH}",
        f"rm -f {FULL_BEDROCK_GEOJSON_PATH}",
        f"ogr2ogr -f GEOJSON {FULL_BEDROCK_GEOJSON_PATH} {wfs_url} {layer}",
        f"rm -f {SFINLAND_BEDROCK_GEOJSON_PATH}",
        f"ogr2ogr -f GEOJSON -spat 80000 6650000 140000 6725000 {SFINLAND_BEDROCK_GEOJSON_PATH} {FULL_BEDROCK_GEOJSON_PATH}",
    ]

    return {
        ACTIONS: actions,
        TARGETS: [FULL_BEDROCK_GEOJSON_PATH, SFINLAND_BEDROCK_GEOJSON_PATH],
        UP_TO_DATE: [
            run_once,
            config_changed(dict(wfs_url=wfs_url, layer=layer, actions=actions)),
        ],
    }


def task_download_shoreline():
    """
    Download global shoreline vector file.
    """
    # Download url
    download_url = (
        "https://www.ngdc.noaa.gov/mgg/shorelines/data/gshhg/latest/gshhg-shp-2.3.7.zip"
    )

    # Temporary zip path
    zip_path = BACKGROUND_OUTPUTS_PATH / "gshhg-shp-2.3.7.zip"

    # Temporary extract path
    extract_path = BACKGROUND_OUTPUTS_PATH / "gshhg-shp-2.3.7"

    # Target shoreline files
    target_pattern = "GSHHS_shp/f/GSHHS_f_L1.*"
    target_shp = extract_path / target_pattern.replace("*", "shp")

    actions = [
        # Create BACKGROUND_OUTPUTS_PATH directory
        f"mkdir -p {BACKGROUND_OUTPUTS_PATH}",
        f"wget '{download_url}' --continue --output-document {zip_path}",
        f"mkdir -p {extract_path}",
        # Unzip shoreline
        f"unzip -u {zip_path} {target_pattern} -d {extract_path}",
        # Convert shapefile to geojson
        f"ogr2ogr -f GEOJSON -spat 60000 6550000 160000 6825000 -spat_srs EPSG:3067 {SHORELINE_PATH} {target_shp}",
    ]

    return {
        ACTIONS: actions,
        TARGETS: [SHORELINE_PATH],
        UP_TO_DATE: [
            run_once,
            config_changed(dict(download_url=download_url, actions=actions)),
        ],
    }

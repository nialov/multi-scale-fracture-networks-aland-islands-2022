"""
Parameters for tests.
"""
from contextlib import nullcontext as does_not_raise

import pytest

import data
from fractopo.general import read_geofile

GTK_BEDROCK_GDF = read_geofile(data.GTK_BEDROCK_GDF_SAMPLE_PATH)
GTK_BEDROCK_GDF_CROPPED = read_geofile(data.GTK_BEDROCK_GDF_CROPPED_PATH)
EXTENT_GDF = read_geofile(data.EXTENT_PATH)
SHORELINE_GDF = read_geofile(data.SHORELINE_PATH)

TEST_BEDROCK_GDF_SUITE_UNION_PARAMS = [
    pytest.param(
        GTK_BEDROCK_GDF_CROPPED,
        "Åland rapakivi suite",
        does_not_raise(),
        id="correct_suite",
    ),
    pytest.param(
        GTK_BEDROCK_GDF_CROPPED,
        "Some Other Suite That Does Not Exist",
        pytest.raises((ValueError, AssertionError)),
        id="incorrect_suite",
    ),
]

TEST_BEDROCK_GDF_CLIP_PARAMS = [
    pytest.param(GTK_BEDROCK_GDF, EXTENT_GDF, does_not_raise(), id="correct_gdfs"),
    pytest.param(
        GTK_BEDROCK_GDF,
        EXTENT_GDF.iloc[0:0],
        pytest.raises(AssertionError),
        id="empty_extent_gdf",
    ),
]

TEST_SHORELINE_GDF_LARGEST_PARAMS = [
    pytest.param(SHORELINE_GDF, does_not_raise(), id="correct_gdf"),
    pytest.param(
        SHORELINE_GDF.iloc[0:0],
        pytest.raises(AssertionError),
        id="empty_gdf",
    ),
]

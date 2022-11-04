"""
Tests for src/utils.py.
"""

import geopandas as gpd
import pytest

import background
import tests


@pytest.mark.parametrize(
    "bedrock_gdf,suite_filter,expectation", tests.TEST_BEDROCK_GDF_SUITE_UNION_PARAMS
)
def test_bedrock_gdf_suite_union(
    bedrock_gdf: gpd.GeoDataFrame,
    suite_filter: str,
    expectation,
):
    """
    Test bedrock_gdf_suite_union.
    """
    with expectation:
        bedrock_gdf_union = background.bedrock_gdf_suite_union(
            bedrock_gdf=bedrock_gdf, suite_filter=suite_filter
        )

        assert isinstance(bedrock_gdf_union, gpd.GeoDataFrame)
        assert bedrock_gdf_union.shape[0] > 0


@pytest.mark.parametrize(
    "bedrock_gdf,extent_gdf,expectation", tests.TEST_BEDROCK_GDF_CLIP_PARAMS
)
def test_bedrock_gdf_clip(
    bedrock_gdf: gpd.GeoDataFrame,
    extent_gdf: gpd.GeoDataFrame,
    expectation,
):
    """
    Test bedrock_gdf_clip.
    """
    assert isinstance(extent_gdf, gpd.GeoDataFrame)

    with expectation:
        bedrock_gdf_clipped = background.bedrock_gdf_clip(
            bedrock_gdf=bedrock_gdf, extent_gdf=extent_gdf
        )

        assert isinstance(bedrock_gdf_clipped, gpd.GeoDataFrame)
        assert bedrock_gdf_clipped.shape[0] > 0


@pytest.mark.parametrize(
    "shoreline_gdf,expectation", tests.TEST_SHORELINE_GDF_LARGEST_PARAMS
)
def test_shoreline_gdf_largest(
    shoreline_gdf: gpd.GeoDataFrame,
    expectation,
):
    """
    Test shoreline_gdf_largest.
    """
    assert isinstance(shoreline_gdf, gpd.GeoDataFrame)

    with expectation:
        shoreline_gdf_clipped = background.shoreline_gdf_largest(
            shoreline_gdf=shoreline_gdf
        )

        assert isinstance(shoreline_gdf_clipped, gpd.GeoDataFrame)
        assert shoreline_gdf_clipped.shape[0] > 0

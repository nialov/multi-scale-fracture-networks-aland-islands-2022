"""
Lithology script.
"""
from pathlib import Path
from textwrap import fill

import geopandas as gpd
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import pandas as pd
import typer
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from rich.console import Console
from rich.traceback import install
from shapely.geometry import Polygon, box
from shapely.wkt import loads

import background
from fractopo.general import geom_bounds, read_geofile
from striations import plot_striations

CONSOLE = Console()
install()

print = CONSOLE.print

# APP = typer.Typer()


def _add_index_map(ax, aland_clip_box, boundaries_path: Path):
    # Create separate index map figure
    boundaries = read_geofile(boundaries_path)
    min_x, min_y, max_x, max_y = 13.0, 53.0, 34.00, 71.0
    fennoscandian_boundaries = gpd.clip(boundaries, box(min_x, min_y, max_x, max_y))
    # Setup figure
    # fig, ax = plt.subplots(figsize=(8.27, 11.75))
    fennoscandian_boundaries.boundary.plot(color="black", linewidth=0.5, ax=ax)
    # sns.despine(bottom=True, left=True, right=True, top=True)
    ax.set_xticks([])
    ax.set_yticks([])
    gpd.GeoSeries([aland_clip_box], crs="EPSG:3067").to_crs("EPSG:4326").boundary.plot(
        ax=ax, color="red"
    )
    ax.text(x=22.55, y=61.9, s="Finland", fontsize="small")
    ax.text(x=14.1, y=63.0, s="Sweden", fontsize="small", rotation=60)
    # ax.text(x=30.5, y=58.7, s="Russia", fontsize="large")
    # ax.text(x=24.5, y=58.7, s="Estonia", fontsize="large")

    # Add scale bar
    # https://geopandas.org/en/stable/gallery/matplotlib_scalebar.html
    # background.add_scale_bar(ax=ax, bbox_coords=(0.91, 0.15))

    # Add north arrow
    # x, y, arrow_length = 0.08, 0.93, 0.08
    # background.add_north_arrow(ax=ax, x=x, y=y, arrow_length=arrow_length)

    # Set axis limits
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)


def lithology(
    bedrock_gdf_cropped_path: Path = typer.Argument(...),
    shoreline_path: Path = typer.Argument(...),
    area_1_20000_path: Path = typer.Argument(...),
    area_1_200000_path: Path = typer.Argument(...),
    poi_path: Path = typer.Argument(...),
    aland_clip_box_path: Path = typer.Argument(...),
    boundaries_path: Path = typer.Argument(...),
    striations_path: Path = typer.Argument(...),
    output_path: Path = typer.Argument(...),
):
    """
    Create processed shoreline.
    """
    bedrock_gdf_s_finland = read_geofile(bedrock_gdf_cropped_path)
    shoreline_gdf_largest = read_geofile(shoreline_path)
    poi_gdf = read_geofile(poi_path)

    area_1_20000 = read_geofile(area_1_20000_path)
    area_1_200000 = read_geofile(area_1_200000_path)

    # Define boundary for map
    aland_clip_box = loads(aland_clip_box_path.read_text())
    assert isinstance(aland_clip_box, Polygon)

    # Clip shoreline & bedrock to boundary
    shoreline_gdf_clipped = gpd.clip(shoreline_gdf_largest, aland_clip_box)
    bedrock_gdf_clipped = gpd.clip(bedrock_gdf_s_finland, aland_clip_box)

    # Names for suites as defined in GeoDataFrame
    aland_rapakivi_suite_name = "Åland rapakivi suite"
    southern_finland_plutonic_suite_name = "Southern Finland plutonic suite"
    undetermined_name = "Undetermined Mesoproterozoic suite"

    # Setup explicit coloring of bedrock suites
    suites_colors = {
        undetermined_name: "#e4c8ed",
        southern_finland_plutonic_suite_name: "#e4e7c5",
        aland_rapakivi_suite_name: "#f8a2cc",
    }

    # Setup explicit coloring of bedrock names
    # rock_name_colors = {
    #     "Anorthosite": "#c1ba92",
    #     "Aplitic rapakivi granite": "#ffd1cd",
    #     "Dolerite (diabase)": "#8B444B",
    #     "Porphyritic rapakivi granite": "#DB97C8",
    #     "Pyterlite": "#ffd2ef",
    #     "Quartz porphyritic rapakivi granite": "#F9A0A1",
    #     "Rapakivi granite (s.s.)": "#f8a2cc",
    #     "Wiborgite": "#DD98CA",
    # }

    # In[ ]:

    # Setup figure
    fig, ax = plt.subplots(figsize=(8.27, 11.75))
    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)

    # Plot shoreline polygons with very low alpha
    shoreline_gdf_clipped.plot(linewidth=0, ax=ax, color="black", alpha=1.0)

    # Plot shoreline boundary
    shoreline_gdf_clipped.boundary.plot(linewidth=0.6, ax=ax, color="black")

    # Plot bedrock
    bedrock_alpha = 0.9
    # rapakivi_bedrock_gdf = bedrock_gdf_clipped.loc[
    #     bedrock_gdf_clipped[background.SUITE] == aland_rapakivi_suite_name
    # ]
    # rapakivi_bedrock_gdf.plot(
    #     linewidth=1,
    #     ax=ax,
    #     alpha=bedrock_alpha,
    #     color=[
    #         rock_name_colors[rock_name]
    #         for rock_name in rapakivi_bedrock_gdf[background.ROCK_NAME].values
    #     ],
    # )

    # Plot boundary of suite
    # boundary_linewidth = 2.0
    rapakivi_bedrock_gdf_union = background.bedrock_gdf_suite_union(
        bedrock_gdf=bedrock_gdf_clipped
    )
    # rapakivi_bedrock_gdf_union.boundary.plot(
    #     color="black", linewidth=boundary_linewidth, ax=ax
    # )

    # Plot other suites around rapakivi suite
    non_rapakivi_bedrock_gdf = bedrock_gdf_clipped.loc[
        bedrock_gdf_clipped[background.SUITE] != "Åland rapakivi suite"
    ]

    # Unary_union does not successfully merge all polygons
    southern_finland_plutonic_suite = background.bedrock_gdf_suite_union(
        non_rapakivi_bedrock_gdf, "", southern_finland_plutonic_suite_name
    )

    # Get largest polygon which covers the wanted area only
    largest_poly = background.resolve_largest_polygon(
        list(southern_finland_plutonic_suite.geometry.values[0].geoms)
    )

    # Join back into a GeoDataFrame
    southern_finland_plutonic_suite = gpd.GeoDataFrame(
        geometry=[largest_poly],
        data={background.SUITE: [southern_finland_plutonic_suite_name]},
        crs=bedrock_gdf_clipped.crs,
    )

    # Plot both mesoproterozoic and sf suite
    mesoproterozoic_formation = background.bedrock_gdf_suite_union(
        non_rapakivi_bedrock_gdf,
        southern_finland_plutonic_suite_name,
        undetermined_name,
    )

    # Get largest polygon which covers the wanted area only
    largest_poly_meso = background.resolve_largest_polygon(
        list(mesoproterozoic_formation.geometry.values[0].geoms)
    )

    # Join back into a GeoDataFrame
    mesoproterozoic_formation = gpd.GeoDataFrame(
        geometry=[largest_poly_meso],
        data={background.SUITE: [undetermined_name]},
        crs=bedrock_gdf_clipped.crs,
    )

    # Concatenate into a single GeoDataFrame
    other_suites = pd.concat(
        (
            southern_finland_plutonic_suite,
            mesoproterozoic_formation,
            rapakivi_bedrock_gdf_union,
        ),
        ignore_index=True,
    )
    assert isinstance(other_suites, gpd.GeoDataFrame)

    other_suites.plot(
        linewidth=1,
        ax=ax,
        alpha=bedrock_alpha,
        color=[suites_colors[suite] for suite in other_suites[background.SUITE].values],
    )

    for idx in range(other_suites.shape[0]):
        gdf_slice = other_suites[idx : idx + 1]
        suite = gdf_slice[background.SUITE].iloc[0]
        ax = gdf_slice.plot(
            linewidth=1,
            ax=ax,
            alpha=0.4,
            color=suites_colors[suite],
        )

    # ax.annotate(
    #     xy=shoreline_point,
    #     text="Getaberget Outcrop",
    #     xytext=((100000, 6.727 * 1e6)),
    #     arrowprops={"arrowstyle": "->"},
    #     va="center",
    # )

    # Set axis limits better
    xmin, ymin, xmax, ymax = aland_clip_box.bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title(
        "Åland - Bedrock of Finland 1:200 000 & Glacial Striations", fontsize="x-large"
    )

    ax.xaxis.set_major_formatter(plt.FuncFormatter(background.format_func_m_to_km))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(background.format_func_m_to_km))

    # Set correct unit labels
    ax.set_ylabel("Y (km)")
    ax.set_xlabel("X (km)")

    # Plot lineament interpretation areas
    boundary_kwargs = dict(
        linewidth=3.0, ax=ax, color="black", linestyle="--", alpha=0.8
    )
    area_1_200000.boundary.plot(**boundary_kwargs)
    area_1_20000.boundary.plot(**boundary_kwargs)

    # Annotate the target area circles
    for area, title in zip((area_1_200000, area_1_20000), ("1:200 000", "1:20 000")):
        # 1:20k consists of two circles
        for target_area in area.geometry.values:
            assert isinstance(target_area, Polygon)
            bounds = geom_bounds(target_area)
            center, bottom = background.circle_bounds_center_bottom(bounds)
            txt = ax.text(
                s=title,
                x=center,
                y=bottom + 4000,
                fontsize="large",
                color="black",
                ha="center",
            )
            txt.set_path_effects(
                [
                    PathEffects.withStroke(
                        linewidth=4.5, foreground="lightgray", alpha=0.75
                    )
                ]
            )

    # Annotate suites
    text_kwargs = dict(rotation=-55, fontsize="large", va="center", ha="center")
    southern_finland_plutonic_suite_name_wrap = fill(
        southern_finland_plutonic_suite_name, width=20
    )
    undetermined_name_wrap = fill(undetermined_name, width=20)
    ax.text(
        x=100000,
        y=6670 * 10e2,
        s=southern_finland_plutonic_suite_name_wrap,
        **text_kwargs
    )
    ax.text(x=90000, y=6666 * 10e2, s=undetermined_name_wrap, **text_kwargs)
    aland_kwargs = text_kwargs.copy()
    aland_kwargs.update({"rotation": 45})
    ax.text(x=88000, y=6717 * 10e2, s=aland_rapakivi_suite_name, **aland_kwargs)

    # Add striations
    _, fig, ax, quiver = plot_striations(
        aland_clip_box=aland_clip_box,
        striations_full_gdf=read_geofile(striations_path),
        fig=fig,
        ax=ax,
    )

    # Create legend
    # Patches for rock names
    legend_patches = [
        Patch(facecolor=value, edgecolor="black", label=key, alpha=bedrock_alpha)
        for key, value in suites_colors.items()
    ]

    # legend_patches.append(
    #     Arrow(
    #         x=-1,
    #         y=0,
    #         dx=1,
    #         dy=0,
    #         facecolor="navy",
    #         label="Striations",
    #         alpha=bedrock_alpha,
    #     )
    # )

    # Add to ax
    # ax.legend(handles=[boundary_patch], loc="lower left", fontsize="medium")
    ax.legend(
        handles=legend_patches,
        loc="lower center",
        title="Suites",
        fontsize="medium",
        ncol=2,
        framealpha=1,
        edgecolor="black",
    )
    # Patch for striations
    ax.quiverkey(
        quiver,
        0.65,
        0.125,
        2.5,
        "Glacial Striations",
        color="navy",
        # angle=270,
        labelpos="E",
        # width=10,
        fontproperties=dict(size="large"),
    )

    # Add scale bar
    # https://geopandas.org/en/stable/gallery/matplotlib_scalebar.html
    background.add_scale_bar(ax=ax, bbox_coords=(0.93, 0.2))

    # Add north arrow
    x, y, arrow_length = 0.06, 0.98, 0.05
    background.add_north_arrow(ax=ax, x=x, y=y, arrow_length=arrow_length)

    # Add points of interest
    for _, row in poi_gdf.iterrows():
        point = row["geometry"]
        x, y = point.x, point.y
        label_line = row["Label"]
        assert isinstance(label_line, str)
        label = fill(label_line, width=11)

        txt = ax.annotate(
            text=label,
            xy=(x, y),
            xytext=(x + 2000, y - 2000),
            fontsize="large",
            arrowprops=dict(arrowstyle="->"),
        )
        # Add path effects to annotate arrow
        txt.arrow_patch.set_path_effects(
            [PathEffects.Stroke(linewidth=5, foreground="w"), PathEffects.Normal()]
        )
        txt.set_path_effects(
            [PathEffects.withStroke(linewidth=4.5, foreground="w", alpha=0.75)]
        )

    # left, bottom, width, height (range 0 to 1)
    index_ax = fig.add_axes([0.745, 0.630, 0.15, 0.225])
    _add_index_map(
        ax=index_ax, aland_clip_box=aland_clip_box, boundaries_path=boundaries_path
    )

    # Save plot
    output_path.parent.mkdir(exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")


# if __name__ == "__main__":
#     APP()

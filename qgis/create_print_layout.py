"""
Script mostly follows:
https://data.library.virginia.edu/how-to-create-and-export-print-layouts-in-python-for-qgis-3/
"""

import uuid
from pathlib import Path

from PyQt5.QtGui import QColor, QFont

from qgis.utils import iface

# Get current project
project = QgsProject.instance()

# Get layout manager
manager = project.layoutManager()

# Use project file (*.qgz) as root directory and save layout output image
# to <root>/outputs/<project>.jpg

ahvenanmaa_scalability_name = "ahvenanmaa-scalability"

project = QgsProject.instance()

is_ortho = ahvenanmaa_scalability_name == project.baseName()

project_path = Path(project.readPath("."))

filename_hash = str(uuid.uuid4())
# filename_hash = "debug"
if is_ortho:
    output_path = (
        project_path / f"outputs/ortho/{project.baseName()}_{filename_hash}.jpg"
    )
else:
    output_path = project_path / f"outputs/{project.baseName()}.jpg"


# Name the layout
layoutName = "PrintLayout"

# We only want certain layers in legend i.e. the rasters
wanted_layer_names = [
    "LiDAR DEM",
    "Electromagnetic",
    # Magnetic 1 = Tilt derivative
    "Magnetic 1",
    # Magnetic 2 = sharp-filtered
    "Magnetic 2",
    # Magnetic 3 = greyscale
    "Magnetic 3",
    "Biskopssten_10m_110820_orto",
    "Ekholm_20m_250820_orto",
    "Eköhällen_20m_6_8_20_orto",
    "Flatö_20m_250620_orto",
    "Flatö_5m_250620_orto",
    "Getaberget1_20m_070820_orto",
    "Getaberget2_20m_070820_orto",
    "Getaberget3_20m_080820_orto80jpg",
    "Getaberget4_20m_080820_orto",
    "Getaberget5_20m_100820_orto",
    "Getaberget6_20m_100820_orto",
    "Getaberget7_20m_100820_orto",
    "Getaberget7_20m_100820_orto",
    "Getaberget8_20m_120820_orto",
    "Getaberget9_20m_120820_orto",
    "Granhamnsholmen_20m_26_08_20",
    "Hamnholmen_20m_25_6_20",
    "Havsvidden_20m_7_8_2020",
    "Hundklobben_20m_240620_orto",
    "Hästskär_20m_110820",
    "Kummelberg_20m_250820_orto",
    "Kåpskärsklobben_20m_240620_orto",
    "Låkan_20m_240620_orto",
    "Prästskär_20m_240820_orto",
    "Rödkon_10m_250820_orto",
    "Rödskär_20m_260820_orto",
    "Segelskär1_20m_060820_orto",
    "Segelskär2_20m_060820_orto",
    "Skatan_20m_080820_orto",
    "Trutklobbarna_20m_050820_orto",
    "Vårdö_20m_260620_orto",
    "YttreBoklobben_20m_5_8_20_orto",
    "ÖstraÖren_20m_110820_orto",
    "Överö_20m_040820_orto",
]

# Remove old print layout if one exists
layouts_list = manager.printLayouts()
for layout in layouts_list:
    if layout.name() == layoutName:
        manager.removeLayout(layout)

# Create new print layout
layout = QgsPrintLayout(project)

# Initialize default settings for blank print layout canvas
layout.initializeDefaults()

# Set the layout name
layout.setName(layoutName)

# Add the layout to layout manager
manager.addLayout(layout)

# Create a layout map item
map = QgsLayoutItemMap(layout)

# Set the location of the map object in the canvas
map.setRect(0, 0, 320, 0)

# Set Map Extent
# defines map extent using map coordinates
current_extent = iface.mapCanvas().extent()
e_xmax = current_extent.xMaximum()
e_ymax = current_extent.yMaximum()
e_xmin = current_extent.xMinimum()
e_ymin = current_extent.yMinimum()
manual_extents = (
    88056,
    6681500,
    129000,
    6721300,
)
# xmin, ymin, xmax, ymax
rectangle = QgsRectangle(*manual_extents)
# rectangle = QgsRectangle(e_xmin, e_ymin, e_xmax, e_ymax)
map.setExtent(rectangle)

ms = QgsMapSettings()
ms.setExtent(rectangle)

canvas = iface.mapCanvas()
canvas.setExtent(rectangle)
canvas.refresh()

# Add map to print layout
layout.addLayoutItem(map)

# Checks layer tree objects and stores them in a list. This includes csv tables
# Only gathers the wanted raster layers
checked_layers = [
    layer.name()
    for layer in QgsProject().instance().layerTreeRoot().children()
    if (layer.isVisible() and layer.name() in wanted_layer_names)
]
print(f"Adding {checked_layers} to legend.")

# Explicitly get layers that we want in legend
layers_to_add = [
    layer
    for layer in QgsProject().instance().mapLayers().values()
    if layer.name() in checked_layers
]

symbol_font = QFont("Arial", 28)


def create_legend(layout):
    # Create layout legend
    legend = QgsLayoutItemLegend(layout)
    # legend.setTitle("")

    # Format the legend box
    legend.setSymbolHeight(40.0)
    legend.setSymbolWidth(20.0)
    legend.setBoxSpace(2.0)
    legend.setStyleFont(QgsLegendStyle.Title, symbol_font)
    legend.setStyleFont(QgsLegendStyle.Subgroup, symbol_font)
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, symbol_font)
    legend.setOpacity(0.9)
    legend.setFrameEnabled(True)

    # Create new tree of layers for legend to use
    qgs_root = QgsLayerTree()

    # Add only the earlier gathered layers
    for layer in layers_to_add:
        qgs_root.addLayer(layer)

    # Extract legend model
    model = legend.model()

    # Join the earlier collected tree into the legend explicitly
    model.setRootGroup(qgs_root)

    # Get root of the raster layer
    root = model.rootGroup().findLayer(layers_to_add[0])

    # Get legend model nodes
    nodes = model.children()
    # If only one raster layer is enabled and it has the below
    # band identifier then this will remove italic
    band_legend_text = "Band 1 (Gray)"
    if nodes[0].data(0) == band_legend_text:
        print(f"Removing text: {band_legend_text}")

        # Get slice of only nodes that come after the text and set them as the
        # nodes of the legend model
        indexes = list(range(1, len(nodes)))
        print(indexes, root)
        QgsMapLayerLegendUtils.setLegendNodeOrder(root, indexes)

        # Refresh the legend
        model.refreshLayerLegend(root)

    print("Adding legend to layout")
    # Add the legend to layout
    layout.addLayoutItem(legend)

    print("Moving legend")
    # Move the legend
    legend.attemptMove(QgsLayoutPoint(3, 252, QgsUnitTypes.LayoutMillimeters))
    return legend, indexes, root


if len(layers_to_add) == 1:
    print("Only one layer to add -> creating legend")
    # legend, indexes, root = create_legend(layout=layout)


print("Creating scalebar")
# Add scalebar
scaleBar = QgsLayoutItemScaleBar(layout)
# Style possibilities are:
# 'Single Box', 'Double Box', 'Line Ticks Middle',
# 'Line Ticks Down', 'Line Ticks Up', 'Numeric'
scaleBar.setStyle("Single Box")
scaleBar.setLinkedMap(map)
scaleBar.applyDefaultSize()
# scaleBar.setNumberOfSegmentsLeft(5)
scaleBar.setNumberOfSegments(4 if not is_ortho else 2)
scaleBar.setFont(symbol_font)
label, units = ("km", 1000) if not is_ortho else ("m", 1)
scaleBar.setUnitLabel(label)
scaleBar.setMapUnitsPerScaleBarUnit(units)
if is_ortho:
    scaleBar.setUnitsPerSegment(5)

# if numUnitsPerSegment is not None:
# scaleBar.setUnitsPerSegment(numUnitsPerSegment)
# scaleBar.setFont(scaleBarFontSize)
scaleBar.setBackgroundEnabled(1)
scaleBar.setOpacity(0.8)
scaleBar.setFrameEnabled(True)
layout.addItem(scaleBar)
print("Moving scalebar")
if not is_ortho:
    scaleBar.attemptMove(QgsLayoutPoint(207, 292, QgsUnitTypes.LayoutMillimeters))
else:
    scaleBar.attemptMove(QgsLayoutPoint(213, 275, QgsUnitTypes.LayoutMillimeters))

scaleBar.setFrameEnabled(True)

print("Adding north arrow")
# Add north arrow
north = QgsLayoutItemPicture(layout)
arrow_svg_path = (project_path / "north_arrow.svg").absolute()
north.setPicturePath(str(arrow_svg_path))
north.setBackgroundEnabled(True)
north.setBackgroundColor(QColor("white"))
north.setOpacity(0.8)
layout.addLayoutItem(north)
north.attemptResize(QgsLayoutSize(16, 23, QgsUnitTypes.LayoutMillimeters))
north.attemptMove(QgsLayoutPoint(300, 0, QgsUnitTypes.LayoutMillimeters))

# Save layout

print(f"Saving layout to {output_path}")
# this accesses a specific layout, by name (which is a string)
layout = manager.layoutByName(layoutName)

print("Setting export settings")
# this creates a QgsLayoutExporter object
exporter = QgsLayoutExporter(layout)

# this exports a pdf of the layout object
# exporter.exportToPdf('/Users/ep9k/Desktop/TestLayout.pdf', QgsLayoutExporter.PdfExportSettings())
export_settings = exporter.ImageExportSettings()
export_settings.cropToContents = True
export_settings.dpi = 300.0
print("Exporting to image")
exporter.exportToImage(str(output_path), export_settings)

# this exports an image of the layout object
# exporter.exportToImage('/Users/ep9k/Desktop/TestLayout.png', QgsLayoutExporter.ImageExportSettings())

# Exit qgis (better with --snapshot)
# iface.actionExit().trigger()

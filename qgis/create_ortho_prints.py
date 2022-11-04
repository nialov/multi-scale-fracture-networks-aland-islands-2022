"""
Script mostly follows:
https://data.library.virginia.edu/how-to-create-and-export-print-layouts-in-python-for-qgis-3/
"""

import uuid
from ast import literal_eval
from pathlib import Path

from PyQt5.QtGui import QColor, QFont

from qgis.utils import iface

# Get current project
project = QgsProject.instance()

# Get layout manager
manager = project.layoutManager()

# Use project file (*.qgz) as root directory and save layout output image
# to <root>/outputs/<project>.jpg


project = QgsProject.instance()


project_path = Path(project.readPath("."))

extents = (project_path / "outputs/extents.txt").read_text().splitlines()


def create_print(extent: tuple):

    filename_hash = str(uuid.uuid4())
    # filename_hash = "debug"
    output_path = (
        project_path / f"outputs/ortho/{project.baseName()}_{filename_hash}.jpg"
    )

    # Name the layout
    layoutName = "PrintLayout"

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
    map.setRect(0, 0, 300, 200)

    # Set Map Extent
    # defines map extent using map coordinates
    # current_extent = iface.mapCanvas().extent()
    # e_xmax = current_extent.xMaximum()
    # e_ymax = current_extent.yMaximum()
    # e_xmin = current_extent.xMinimum()
    # e_ymin = current_extent.yMinimum()
    # manual_extents = 109561.37,6719792.98,109611.37,6719842.98
    # rectangle = QgsRectangle(*manual_extents)
    rectangle = QgsRectangle(*extent)
    map.setExtent(rectangle)

    # Add map to print layout
    layout.addLayoutItem(map)

    symbol_font = QFont("Arial", 28)

    # Add scalebar
    scaleBar = QgsLayoutItemScaleBar(layout)
    # Style possibilities are:
    # 'Single Box', 'Double Box', 'Line Ticks Middle',
    # 'Line Ticks Down', 'Line Ticks Up', 'Numeric'
    scaleBar.setStyle("Single Box")
    scaleBar.setLinkedMap(map)
    scaleBar.applyDefaultSize()
    # scaleBar.setNumberOfSegmentsLeft(5)
    scaleBar.setNumberOfSegments(2)
    scaleBar.setFont(symbol_font)
    label, units = "m", 1
    scaleBar.setUnitLabel(label)
    scaleBar.setMapUnitsPerScaleBarUnit(units)
    scaleBar.setUnitsPerSegment(5)

    # if numUnitsPerSegment is not None:
    # scaleBar.setUnitsPerSegment(numUnitsPerSegment)
    # scaleBar.setFont(scaleBarFontSize)
    scaleBar.setBackgroundEnabled(1)
    scaleBar.setOpacity(0.8)
    scaleBar.setFrameEnabled(True)
    layout.addItem(scaleBar)
    scaleBar.attemptMove(QgsLayoutPoint(213, 275, QgsUnitTypes.LayoutMillimeters))

    scaleBar.setFrameEnabled(True)

    # Add north arrow
    north = QgsLayoutItemPicture(layout)
    arrow_svg_path = (project_path / "north_arrow.svg").absolute()
    north.setPicturePath(str(arrow_svg_path))
    north.setBackgroundEnabled(True)
    north.setBackgroundColor(QColor("white"))
    north.setOpacity(0.8)
    layout.addLayoutItem(north)
    north.attemptResize(QgsLayoutSize(16, 23, QgsUnitTypes.LayoutMillimeters))
    north.attemptMove(QgsLayoutPoint(283, 0, QgsUnitTypes.LayoutMillimeters))

    # Save layout

    # this accesses a specific layout, by name (which is a string)
    layout = manager.layoutByName(layoutName)

    # this creates a QgsLayoutExporter object
    exporter = QgsLayoutExporter(layout)

    # this exports a pdf of the layout object
    # exporter.exportToPdf('/Users/ep9k/Desktop/TestLayout.pdf', QgsLayoutExporter.PdfExportSettings())
    export_settings = exporter.ImageExportSettings()
    export_settings.cropToContents = True
    exporter.exportToImage(str(output_path), export_settings)

    # this exports an image of the layout object
    # exporter.exportToImage('/Users/ep9k/Desktop/TestLayout.png', QgsLayoutExporter.ImageExportSettings())

    # Exit qgis (better with --snapshot)
    # iface.actionExit().trigger()


for extent in extents:
    eval_extent = literal_eval(extent)
    assert isinstance(eval_extent, tuple)
    create_print(extent=eval_extent)

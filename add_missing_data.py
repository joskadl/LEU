# Note: this script requires to be run from a conda virtual environment with below packages installed

from pathlib import Path

import geopandas as gpd
import fiona

"""
Goals:
- Fill in missing area codes for points and polygons
- Then, change 1899 and null dates to first july of the year that area was monitored
- Fill in above missing data, and write back to __fixed.gdb file
"""

file_to_fix = Path(r"MAC-data-totaal-feb-2023.gdb")

areas_layer = "Gebiedenselectie"  # Contains polygons corresponding to named areas


def find_polygon_and_point_layers(file: Path):
    # Return dict of dicts, organizing layers by geometry type and linking layer names to their content
    # NOTE: this can probably be done more elegantly using pandas-style logic
    layers = {"points": dict(), "polygons": dict()}
    for layer in fiona.listlayers(file):
        if layer != areas_layer:
            layer_content = gpd.read_file(file, layer=layer)
            layer_geom_type = layer_content.geom_type.values[0]
            if layer_geom_type == "MultiPolygon":
                layers['polygons'][layer] = layer_content
            elif layer_geom_type == "Point":
                layers['points'][layer] = layer_content
    return layers


def get_area_polygons(file, layer):
    # Return dictionary linking area codes to their MultiPolygon geometry
    areas = dict()
    layer_content = gpd.read_file(file, layer=layer)
    for area in layer_content["GEB_NR"]:
        areas[area] = layer_content[layer_content["GEB_NR"] == area].geometry
    return areas


def map_areas_to_geometry(layer):
    """Takes a layer of geometry type (e.g. points or polygons) and iterates over rows, adding geometry object to
    list of values for a key corresponding to the area code
    """
    geometry_areas = {} # A dictionary of area codes linked to a list of geometry objects
    for area, geometry in zip(layer["GEB"], layer.geometry):
        if area not in layer.keys():
            geometry_areas[area] = [geometry]
        else:
            geometry_areas[area].append(geometry)
    return geometry_areas


# TODO: Question: There are some area codes without hyphenation (e.g. GR05).
#  Should I merge these with hyphenated codes (e.g. GR-05)?

# Extract names of polygon and point layers
polygon_and_point_layers = find_polygon_and_point_layers(file_to_fix)

# TODO: we use a single monitoring round below. This should later be a loop over all monitoring rounds
points_nulmetingen_df = polygon_and_point_layers["points"]["Puntelementen_nulmetingen_totaal"]

'''
# Sanity check: Confirm that points with area code 'GR-03' fall within area_polygon with area code 'GR-03'
  # This is the case for vast majority of points. Same for area GR-04

area_polygons = get_area_polygons(file_to_fix, areas_layer)
area_code = 'GR-04'
area_polygon = area_polygons[area_code].values[0]
for point in points_nulmetingen_df.loc[points_nulmetingen_df["GEB"] == area_code].iterrows():
    print(point[-1]['geometry'].within(area_polygon))  # Confirm point falls within polygon for indicated area
'''

# Get the polygons corresponding to measurement areas
area_polygons = get_area_polygons(file_to_fix, areas_layer)

# Loop over all points without area code
# TODO: should I check for area values such as None as well as " "?
#   Or: check for any "GEB" value which does not contain letters (or is 'Falsy'). Regular expressions?
for point in points_nulmetingen_df.loc[points_nulmetingen_df["GEB"] == " "].iterrows():
    point_geometry = point[-1]["geometry"]
    # Check whether point falls within any polygon belonging to a measurement area
    for area in area_polygons.keys():
        if point_geometry.within(area_polygons[area].values[0]):
            # Assign area code of the area_polygon it falls within
            print(f"Point {point_geometry} falls within area {area}")
            # TODO: assign area code to point (how?)

# TODO: Do the same for polygons
# TODO: Also add missing dates: check for relevant measurement round what year an area was monitored
# TODO: Iterate over all measurement rounds (not just 'Nulmetingen')
# TODO: Write all these back to a GDB file

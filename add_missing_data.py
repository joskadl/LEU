# Note: this script requires to be run from a conda virtual environment with below packages installed

from pathlib import Path

import geopandas as gpd
import fiona

"""
Goals:
- Fill in missing area codes for points and polygons
- Then, change 1899 and null dates to first july of the year that area was monitored
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


def map_areas_to_polygons(polygon_layer):
    polygon_areas = {} # A dictionary of area codes linked to a list of MULTIPOLYGON objects
    # TODO: account for missing areas? Some are mapped to ' ' and some to None
    for area, polygon in zip(polygon_layer["GEB"], polygon_layer.geometry):
        if area not in polygon_areas.keys():
            polygon_areas[area] = [polygon]
        else:
            polygon_areas[area].append(polygon)
    return polygon_areas


def map_areas_to_points(point_layer):
    point_areas = {} # A dictionary of area codes each linked to a list of POINT objects
    for area, point in zip(point_layer["GEB"], point_layer.geometry):
        if area not in point_areas.keys():
            point_areas[area] = [point]
        else:
            point_areas[area].append(point)
    return point_areas


"""
Plan:
- Find out whether all points/polygons without area code fall within a polygon that does have an area code. Assign area if so.
    - As a sanity check, confirm that points with an area code fall within polygon with same area code
      Use geopandas.GeoSeries.contains(Point) https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.contains.html
- Once missing data is added, write back to GeoPackage or FileGeoDatabase file

Question: There are some area codes without hyphenation (e.g. GR05). Should I merge these with hyphenated codes (e.g. GR-05)?
"""

# Extract names of polygon and point layers
polygon_and_point_layers = find_polygon_and_point_layers(file_to_fix)

# Get the polygons corresponding to measurement areas
area_polygons = get_area_polygons(file_to_fix, areas_layer)

# Sanity check: Confirm that points with area code 'GR-03' fall within area_polygon with area code 'GR-03'
  # This is the case for vast majority of points. Same for area GR-04
area_code = 'GR-03'
area_polygon = area_polygons[area_code].values[0]
points_nulmetingen_df = polygon_and_point_layers["points"]["Puntelementen_nulmetingen_totaal"]
for point in points_nulmetingen_df.loc[points_nulmetingen_df["GEB"] == area_code].iterrows():
    # print(point[-1]['geometry'].within(area_polygon))  # Confirm point falls within polygon for indicated area
    pass

# Loop over all points without area code
#   TODO: should I check for None as well as " "?
for point in points_nulmetingen_df.loc[points_nulmetingen_df["GEB"] == " "].iterrows():
    point = point[-1]["geometry"]
    # Check whether point falls within any polygon belonging to a measurement area
    for area in area_polygons.keys():
        if point.within(area_polygons[area].values[0]):
            # Assign area code of the area_polygon it falls within
            print(f"Point {point} falls within area {area}")
            # TODO: assign area code to point

# TODO: Do the same for polygons
# TODO: Also add missing dates: check for relevant measurement round what year an area was monitored
# TODO: Write all these back to a GDB file

# Note: this script requires to be run from a conda virtual environment with below packages installed

from pathlib import Path

import geopandas as gpd
import fiona

"""
Goals:
- Fill in missing area codes for points (perhaps geopandas can confirm whether points are within polygon area?)
- Then, change 1899 and null dates to first july of the year that area was monitored
"""

file_to_fix = Path(r"Monitoring-ronde1-totaal.gdb")  # TODO: loop over all files later

def find_polygon_and_point_layers(file: Path):
    # Note: this assumes only one polygon layer and one point layer is in file, as first of each is returned
    for layer in fiona.listlayers(file):
        layer_content = gpd.read_file(file, layer=layer)
        layer_geom_type = layer_content.geom_type.values[0]
        if layer_geom_type == "MultiPolygon":
            polygon_layer = layer_content
        elif layer_geom_type == "Point":
            point_layer = layer_content
    return [polygon_layer, point_layer]


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
- Find out whether all points without area code fall within a polygon that does have an area code. Assign area if so.
    - As a sanity check, confirm that points with an area code fall within polygon with same area code
      Use geopandas.GeoSeries.contains(Point) https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.contains.html
- Once missing data is added, write back to GeoPackage or FileGeoDatabase file

Question: There are some area codes without hyphenation (e.g. GR05). Should I merge these with hyphenated codes (e.g. GR-05)?
Question: What to do with polygons that don't have area code? 
    - Is it enough to fix area codes for points, or is this also needed for polygons?
"""

# Extract polygon and point layers, and map area codes to polygons and points
polygon_layer, point_layer = find_polygon_and_point_layers(file_to_fix)
polygon_areas = map_areas_to_polygons(polygon_layer)
point_areas = map_areas_to_points(point_layer)

# Find points without assigned area code
points_without_area_code = point_areas[" "] + point_areas[None]

# Confirm that points for an area fall within the (multi)polygons for that area
area_code = "GR-03"  # TODO: This is a random single area code for development purposes. Loop/make general later.

for point in point_areas[area_code]:
    # Check whether point falls in one of multipolygons
    print(True in [point.within(multipolygon) for multipolygon in polygon_areas[area_code]])
    # TODO: Some are True, but many are False. What is happening?

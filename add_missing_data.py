# Note: this script requires to be run from a conda virtual environment with below packages installed

from pathlib import Path
from typing import List

import geopandas as gpd
import fiona

"""
Goals:
- Fill in missing area codes for points (perhaps geopandas can confirm whether points are within polygon area?)
- Then, change 1899 and null dates to first july of the year that area was monitored
"""

file_to_fix = Path(r"Monitoring-ronde1-totaal.gdb")  # TODO: loop over all files later


def find_polygon_and_point_layers(file: Path):
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
    # TODO: account for missing areas? Some are listed as ' ' (130 polygons) and some as None (42 polygons)
    for area, polygon in zip(polygon_layer["GEB"], polygon_layer.geometry):
        if area not in polygon_areas.keys():
            polygon_areas[area] = [polygon]
        else:
            polygon_areas[area].append(polygon)
    return polygon_areas


def map_areas_to_points(point_layer):
    point_areas = {} # A dictionary of area codes linked to a list of POINT objects
    for area, point in zip(polygon_layer["GEB"], point_layer.geometry):
        if area not in point_areas.keys():
            point_areas[area] = [point]
        else:
            point_areas[area].append(point)
    return point_areas


def return_first_element_of_single_element_list(l: List):
    """Confirm list has only one element before returning it"""
    if len(l) == 1:
        return l[0]
    else:
        print(f"More than one element found in list: {l}")
        # raise Exception("Single element list expected, but multiple elements found.")


# Extract polygon and point layers, and map area codes to polygons and points
polygon_layer, point_layer = find_polygon_and_point_layers(file_to_fix)
polygon_areas = map_areas_to_polygons(polygon_layer)
point_areas = map_areas_to_points(point_layer)

# Find points without assigned area code
points_without_area_code = point_areas[" "] + point_areas[None]

"""
Plan:
- Find out whether all points without area code fall within a polygon that does have an area code. Assign area if so.
    - As a sanity check, confirm that points with an area code fall within polygon with same area code
      Use geopandas.GeoSeries.contains(Point) https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.contains.html
- Once missing data is added, write back to GeoPackage or FileGeoDatabase file

Question: Do I need to convert MultiPolygon to GeoSeries of Polygon objects? -> probably
Question: It looks like the point coordinates are indeed quite different from those of the polygons. Why?
    Log on to arcgis.com and confirm coordinates? Different projection?
Question: Does it make sense that we have multiple polygons for each area code? e.g. 19 times 'OV-07'?
Question: There are some area codes without hyphenation (e.g. GR05). Should I merge these with hyphenated codes (e.g. GR-05)?
Question: What to do with polygons that don't have area code?
Question: Is it enough to fix area codes for points, or is this also needed for polygons?
"""

# TODO: Below we're confirming that the points for a specific area fall within the polygon(s) for that area code:

area_code = "GR-06"  # TODO: This is a random single area code for development purposes. Loop/make general later.
polygons_in_area = gpd.GeoSeries(return_first_element_of_single_element_list(list(p)) for p in polygon_areas[area_code])
# TODO: do I only need first element of list(p)? And is it actually required that this list only has one element?
#   GR-03 has a list(p) for an area, which has multiple elements. How to treat this?
points_in_area = point_areas[area_code]

# TODO: an area seems to have as many polygons as points (may or may not be universal). Why? What do?

for point in points_in_area:
    # Check whether point falls in one of polygons
    print(True in [polygon.contains(point) for polygon in polygons_in_area])

    # TODO: this only gives 'False' results. Why?
    #   Try making simple point and polygon to check whether this works.
    #   (If needed, use online ArcGIS)




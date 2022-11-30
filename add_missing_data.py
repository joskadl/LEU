# Note: this script requires to be run from a conda virtual environment with below packages installed

from pathlib import Path

import geopandas as gpd
import fiona

"""
Goals:
- Fill in missing area codes for points (perhaps geopandas can confirm whether points are within polygon area?)
- Then, change 1899 and null dates to first july of the year that area was monitored
"""


# TODO: loop over all files later
file_to_fix = Path(r"Monitoring-ronde1-totaal.gdb")

# Find polygon layer and points layer for this file
for layer in fiona.listlayers(file_to_fix):
    layer_content = gpd.read_file(file_to_fix, layer=layer)
    layer_geom_type = layer_content.geom_type.values[0]
    if layer_geom_type == "MultiPolygon":
        polygon_layer = layer_content
    elif layer_geom_type == "Point":
        point_layer = layer_content


polygon_areas = {} # A dictionary of area codes linked to a list of MULTIPOLYGON objects
# TODO: account for missing areas? Some are listed as ' ' (130 polygons) and some as None (42 polygons)
for area, polygon in zip(polygon_layer["GEB"], polygon_layer.geometry):
    if area not in polygon_areas.keys():
        polygon_areas[area] = [polygon]
    else:
        polygon_areas[area].append(polygon)

# for k in polygon_areas.keys():
#     print(f"{k} has {len(polygon_areas[k])} points")


point_areas = {} # A dictionary of area codes linked to a list of POINT objects
# TODO: account for missing areas? Some are listed as ' ' (130 points) and some as None (42 points)
for area, point in zip(polygon_layer["GEB"], point_layer.geometry):
    if area not in point_areas.keys():
        point_areas[area] = [point]
    else:
        point_areas[area].append(point)

# for k in point_areas.keys():
#     print(f"{k} has {len(point_areas[k])} points")


# TODO: find out whether all points without area code fall within a polygon that does have an area code
points_without_area_code = point_areas[" "] + point_areas[None]

# for point in points_without_area_code:
#     print(point)


# TODO: check whether points with area code fall within polygon with the same area code
#   Use geopandas.GeoSeries.contains(Point) https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.contains.html
#   If this behaves as expected, see whether this also works for points with missing area code

gr_04_polygons = gpd.GeoSeries(polygon_areas["GR-04"])
gr_04_points = point_areas["GR-04"]

for point in gr_04_points:
    point_found = False
    print(True in gr_04_polygons.contains(point))
    # TODO: this only gives 'False' results. Why?

# TODO: once missing data is added, write all layers back to .gpkg file


# Question: Does it make sense that we have multiple polygons for each area code? e.g. 19 times 'OV-07'?
# There are some area codes without hyphenation (e.g. GR05). Should I merge these with hyphenated codes (e.g. GR-05)?
# Question: What to do with polygons that don't have area code?
# Question: Is it enough to fix area codes for points, or is this also needed for polygons?

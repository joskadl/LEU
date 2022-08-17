import geopandas as gpd
import fiona

# Find all gdb files, and make overview of

# Find all layers in these gdb files
layers = fiona.listlayers("./MAC2020_totaal.gdb/")
# TODO: this should be a loop over gdb files later

# Sort layers by geometry type
point_layers = []
line_layers = []
polygon_layers = []
empty_layers_attach = []
empty_layers_other = []
for layer in layers:
    layer_content = gpd.read_file('./MAC2020_totaal.gdb/', layer=layer)
    if len(layer_content.geom_type) > 0:
        geom_type = layer_content.geom_type[0]
        if geom_type == "Point":
            point_layers.append(layer)
        if geom_type == "MultiLineString":
            line_layers.append(layer)
        if geom_type == "MultiPolygon":
            polygon_layers.append(layer)
    else:
        if "ATTACH" in layer:
            empty_layers_attach.append(layer)
        else:
            empty_layers_other.append(layer)
        # TODO: confirm geometry of empty dataframes (attachments vs empty df columns)

# TODO: for all points layers, check intersection of column names, and individual additions for each layer
# TODO: do this for points, lines, polygons
column_names_sets = []
for layer in point_layers:
    layer_content = gpd.read_file('./MAC2020_totaal.gdb/', layer=layer)
    column_names_sets.append(set(layer_content.columns))

# print(column_names)

common_column_names = set.intersection(*column_names_sets)
print(f"{common_column_names=}")

for column_names in column_names_sets:
    # TODO: incorporate layer name
    non_common_names = column_names - common_column_names
    print(sorted(non_common_names))

# print(f"{len(point_layers)=}, {len(line_layers)=}, {len(polygon_layers)=}")
# print(line_layers)
# print(empty_layers_attach)
# print(empty_layers_other)

"""
TODO:
- Get overview of all .gdb files
- Get overview of all layers in these files, with corresponding geometries
- Get field names of all layers
  - Sort by type
  - Check overlap in field names, e.g. to check miss-spellings (intersection and difference)
- Some data may exist as .shp files instead of .gdb -> check where these exist
  - Get field names of .shp files
- When there is redundancy (e.g. .shp and .gdb) check for duplicates, and decide which to use
"""

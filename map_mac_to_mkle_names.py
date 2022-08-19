import geopandas as gpd
import fiona

gdb_file = './MAC2020_totaal.gdb/'

# Find all layers in a given .gdb file
# TODO: this should be a loop over all relevant .gdb files later (and shapefiles?)
layers = fiona.listlayers(gdb_file)

# Sort layers by geometry type
point_layers = []
line_layers = []
polygon_layers = []
empty_layers_attach = []
empty_layers_other = []
for layer in layers:
    layer_content = gpd.read_file(gdb_file, layer=layer)
    if len(layer_content.geom_type) > 0:
        geom_type = layer_content.geom_type[0]
        if geom_type == "Point":
            point_layers.append(layer)
        if geom_type == "MultiLineString":
            line_layers.append(layer)
        if geom_type == "MultiPolygon":
            polygon_layers.append(layer)
    # Sort empty layers by type
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
    layer_content = gpd.read_file(gdb_file, layer=layer)
    column_names_sets.append(set(layer_content.columns))

common_column_names = set.intersection(*column_names_sets)  # Column names occurring in all point layers
print(f"{common_column_names=}")

for column_names in column_names_sets:
    # TODO: incorporate layer name
    non_common_names = column_names - common_column_names
    print(sorted(non_common_names))


"""
TODO:
- This script should yield a CSV file with the mapping from used (MAC) names to desired (KLEi) names
- The column headers for this file will be as follows:
  - 'geom_type': indicates the type of the layer ('points', 'lines', or 'polygons')
  - 'source': the column names used in the source data
  - 'target': the MKLE-name to which this source name should map (from KLEi set)
  - 'common': indicates whether or not this source name occurs in all source data of the current geom_type

Notes:
- Using a command line interface, users will be prompted to pick (numerically) which KLEi-name a source name should be mapped to
  - Answers are stored in a mapping file, to save time when running this script again
  - This mapping file will be in plain-text, and can be checked or amended manually if needed
- Some data may exist as .shp files instead of .gdb -> check where these exist
  - Get field names of .shp files
- When there is redundancy (e.g. .shp and .gdb) check for duplicates, and decide which to use
"""

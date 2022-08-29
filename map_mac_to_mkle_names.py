import geopandas as gpd
import fiona

gdb_file = './MAC2020_totaal.gdb/'
klei_names_file = './python_scripts/klei_names.txt'

# Make dictionary linking 'Punt', 'Vlak' and 'Lijn' to their KLEi names
with open(klei_names_file) as f:
    klei_names = {line.split(":")[0]: [x.strip() for x in line.split(":")[1].split(",")] for line in f.readlines()}

# TODO: this should be a loop over all relevant .gdb files later (and shapefiles?)
# Find all layers in a given .gdb file
layers = fiona.listlayers(gdb_file)

# Make a dictionary that links geom_type to used names in layer:
# {"Point": [{"GlobalID": "common"}, {'Gelaagdhei': 'not common'},  ...]}
names = dict()
for layer in layers:
    layer_content = gpd.read_file(gdb_file, layer=layer)
    if len(layer_content.geom_type) > 0:  # Ignore layers without geom_type
        geom_type = layer_content.geom_type[0]
        if geom_type not in names:
            names[geom_type] = [{column_name: "common"} for column_name in layer_content.columns]
        else:
            # The intersection of existing common column names and new column names will be marked "common"
            common_columns = set(list(x.keys())[0] if list(x.values())[0] == "common" else None for x in names[geom_type]).intersection(set(layer_content.columns))
            # Iterate over combination of existing and new columns. Assign value "not common" unless in common_columns
            all_columns = {list(x.keys())[0] for x in names[geom_type]}.union(set(layer_content.columns))
            names[geom_type] = [{x: "common" if x in common_columns else "not common"} for x in all_columns]



"""
TODO:
- This script should yield a CSV file with the mapping from used (MAC) names to desired (KLEi) names
- The column headers for this file will be as follows:
  - 'geom_type': indicates the type of the layer ('points', 'lines', or 'polygons')
  - 'source': the column names used in the source data
  - 'target': the MKLE-name to which this source name should map (from KLEi set)
  - 'common': indicates whether or not this source name occurs in all source data of the current geom_type

Notes:
- Using a command line interface, users will be prompted to pick (numerically) 
  which KLEi-name a source name should be mapped to
  - Answers are stored in a mapping file, to save time when running this script again
  - This mapping file will be in plain-text, and can be checked or amended manually if needed
- Some data may exist as .shp files instead of .gdb -> check where these exist
  - Get field names of .shp files
- When there is redundancy (e.g. .shp and .gdb) check for duplicates, and decide which to use
"""

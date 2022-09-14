import geopandas as gpd
import fiona
from pathlib import Path

# Note: this script may require to be run from a conda virtual environment

gdb_file = "./MAC2020_totaal.gdb/"
klei_names_file = "./python_scripts/klei_names.txt"
separator = ";"  # CSV separator for Excel readability

# Make dictionary linking 'Punt', 'Vlak' and 'Lijn' to their KLEi target names
with open(klei_names_file) as f:
    klei_names = {
        line.split(":")[0]: [x.strip() for x in line.split(":")[1].split(",")]
        for line in f.readlines()
    }


# TODO: this should be a loop over all relevant .gdb files later (and shapefiles?)
# Find all layers in a given .gdb file
layers = fiona.listlayers(gdb_file)

# Make a dictionary that links geom_type to used names in layer:
# {"Point": [{"GlobalID": "common"}, {'Gelaagdhei': 'not common'},  ...]}
names = dict()
for layer in layers:
    layer_content = gpd.read_file(gdb_file, layer=layer)
    # Ignore layers without geom_type
    if len(layer_content.geom_type) > 0 and layer_content.geom_type[0] is not None:
        geom_type = layer_content.geom_type[0]
        if geom_type not in names:
            names[geom_type] = [
                {column_name: "common"} for column_name in layer_content.columns
            ]
        else:
            # The intersection of existing common column names and new column names will be marked "common"
            common_columns = set(
                list(x.keys())[0] if list(x.values())[0] == "common" else None
                for x in names[geom_type]
            ).intersection(set(layer_content.columns))
            # Iterate over combination of existing and new columns. Assign value "not common" unless in common_columns
            all_columns = {list(x.keys())[0] for x in names[geom_type]}.union(
                set(layer_content.columns)
            )
            names[geom_type] = [
                {x: "common" if x in common_columns else "not common"}
                for x in all_columns
            ]

# Make a dictionary that maps found names to acceptable KLEi target names (or ###-nader_bepalen or ###-laten_vervallen)
# Loop over found names for each geom_type, and if no mapping found for that name+geom_type,
# propose numbered list of KLEi names
# Write new mapping to file immediately, so manual entry can be paused and continued when code exits
# TODO: Should I map names automatically if they exist in KLEi names set? Or enforce manual choices?

# Make temporary mapping file, to allow interruption of manual data entry. Read this file if it already exists.
tmp_mapping_file = "tmp_mapping.csv"
mapping = dict()
if Path(tmp_mapping_file).exists():
    # Read mapping to dictionary
    with open(tmp_mapping_file, "r") as f:
        f.readline()  # Skip headers
        for line in f.readlines():
            geom_type, source, target = [x.strip() for x in line.split(separator)]
            if geom_type not in mapping.keys():
                mapping[geom_type] = dict()
            mapping[geom_type][source] = target
    print(f"Reading existing tmp_mapping file: {mapping}\n")
else:
    # Make mapping file with headers
    with open(tmp_mapping_file, "w") as f:
        f.write(separator.join(["geom_type", "source", "target"]) + "\n")
        print("Created new tmp_mapping file")

# Append new mappings to temporary mapping file
with open(tmp_mapping_file, "a") as f:
    for geom_type in names.keys():
        if geom_type not in mapping.keys():
            mapping[geom_type] = dict()
        for name in names[geom_type]:
            if (source := list(name.keys())[0]) not in mapping[geom_type].keys():
                # Propose numbered list of KLEi names to choose from
                options = ["###-nader_bepalen", "###-laten_vervallen"] + klei_names[geom_type]
                for number, option in enumerate(options):
                    print(f"{number}: {option}")
                # TODO: handle incorrect user input elegantly
                choice = input(f"What KLEi name does {source} correspond to for geom_type {geom_type}? "
                               f"Pick a number listed above and press enter:")
                mapping[geom_type][source] = (target := options[int(choice)])
                f.write(separator.join([geom_type, source, target]) + "\n")
                print(f"{source} is now mapped to {target} for geom_type {geom_type}.\n")


# Write a CSV file showing source names for all geom_types, indicating whether these are shared by all layers
# of this geom_type, along with proposed target (KLEi) name
mapping_file = "mapping.csv"
with open(mapping_file, "w") as f:
    # Write CSV headers
    f.write(separator.join(["geom_type", "source", "target", "common"]) + "\n")
    for geom_type in names.keys():
        for name in names[geom_type]:
            # TODO: include target name in CSV
            f.write(
                separator.join(
                    [geom_type, list(name.keys())[0], "N/A", list(name.values())[0]]
                )
                + "\n"
            )


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

import geopandas as gpd
import fiona

gdb_file = "./MAC2020_totaal.gdb/"
klei_names_file = "./python_scripts/klei_names.txt"

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
# TODO: Read file to make dictionary that maps MAC to KLEi names, where they have been entered already
mapping = dict()
with open("mac_to_klei.txt", "w") as f:
    for geom_type in names.keys():
        for name in names[geom_type]:
            # Propose numbered list of KLEi names to choose from
            options = ["###-nader_bepalen", "###-laten_vervallen"] + klei_names[geom_type]
            for number, option in enumerate(options):
                print(f"{number}: {option}")
            # TODO: handle incorrect user input elegantly
            choice = input(f"What KLEi name does {list(name.keys())[0]} correspond to? Pick a number listed above and press enter:")
            print(f"{list(name.keys())[0]} is now mapped to {options[int(choice)]} for geom_type {geom_type}.")
            # TODO: the actual mapping and writing to file


# Write a CSV file showing source names for all geom_types, indicating whether these are shared by all layers
# of this geom_type, along with proposed target (KLEi) name
separator = ";"  # CSV separator for Excel readability
with open("mapping.csv", "w") as f:
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

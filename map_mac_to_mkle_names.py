from pathlib import Path
import sys

import geopandas as gpd
import fiona

# Note: this script requires to be run from a conda virtual environment

# Path to source files:
data_directory = Path(r"C:\Users\jla23480\Downloads\Data")
mkle_names_file = "./python_scripts/mkle_names.txt"

# Find all .gdb files in data directory
gdb_files = [x for x in (data_directory.glob("**/*")) if x.suffix == ".gdb"]

# Some .gdb files may need to be ignored in further analysis.
# Leave the list below empty, or list your own files to ignore
files_to_ignore = [
    Path(r'C:/Users/jla23480/Downloads/Data/Data/Levering 2012/Flevoland/MAC Flevoland 2012/gebieden.gdb'),
    Path(r'C:/Users/jla23480/Downloads/Data/Data/Levering 2017/Gelderland/20171218_opleveringveldwerkGE.gdb'),
    Path(r"C:\Users\jla23480\Downloads\Data\Data\Levering 2017\Gelderland\20171218_opleveringveldwerkGE_zonderdomains.gdb"),
    Path(r"C:\Users\jla23480\Downloads\Data\Data\Levering 2017\Groningen\mac_2015-2019_ontvangst_data_na_veldwerk2017_gr_slgr.gdb"),
    Path(r"C:\Users\jla23480\Downloads\Data\Data\Levering 2017\Groningen\mac_2015-2019_ontvangst_data_na_veldwerk2017_gr_slgr.gdb\mac_2015-2019_ontvangst_data_na_veldwerk2017_gr_slgr.gdb"),
    Path(r"C:\Users\jla23480\Downloads\Data\Data\Levering 2017\Zeeland\MAC_ZL06_veldwerk2017_nacontrole20180109.gdb"),
]
for f in files_to_ignore:
    if f in gdb_files:
        gdb_files.remove(f)

separator = ";"  # CSV separator for Excel readability

# Make a dictionary linking 'Point', 'MultiLineString' and 'MultiPolygon' to their allowed MKLE target names
with open(mkle_names_file) as f:
    mkle_names = {
        line.split(":")[0]: [x.strip() for x in line.split(":")[1].split(",")]
        for line in f.readlines()
    }


# Make a dictionary that links geom_type to used names in each layer of that type for all .gdb files.
# Names that occur for all layers of a geom_type are marked 'common' - the other ones 'not common':
# {"Point": [{"GlobalID": "common"}, {'Gelaagdhei': 'not common'},  ...]}
names = dict()
for gdb_file in gdb_files:
    print(f"Analyzing .gdb file: {gdb_file}")
    for layer in fiona.listlayers(gdb_file):
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
                # Iterate over combination of existing and new columns.
                # Assign value "not common" unless in common_columns
                all_columns = {list(x.keys())[0] for x in names[geom_type]}.union(
                    set(layer_content.columns)
                )
                names[geom_type] = [
                    {x: "common" if x in common_columns else "not common"}
                    for x in all_columns
                ]

# Read temporary mapping file if it already exists, and store as dictionary. Make this file if it's not there yet.
# This file allows the user to abort the script during data entry, and pick up again where they left off.
tmp_mapping_file = "tmp_mapping.csv"
mapping = dict()
if Path(tmp_mapping_file).exists():
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

# Loop over names from each layer of listed .gdb files.
# If no mapping is found for a name+geom_type, propose numbered choices of MKLE target names to user.
# ("###-nader_bepalen" and "###-laten_vervallen" are added to these choices)
# Append new mappings to the temporary mapping file.
with open(tmp_mapping_file, "a") as f:
    for geom_type in names.keys():
        if geom_type not in mapping.keys():
            mapping[geom_type] = dict()
        for name in names[geom_type]:
            if (source := list(name.keys())[0]) not in mapping[geom_type].keys():
                # Propose numbered list of MKLE names to choose from
                options = ["###-nader_bepalen", "###-laten_vervallen"] + mkle_names[
                    geom_type
                ]
                for number, option in enumerate(options):
                    print(f"{number}: {option}")

                # Only allow numerical user input corresponding to numbered options
                choice = -1
                while choice not in range(len(options)):
                    try:
                        choice = int(
                            input(
                                f"What MKLE name does {source} correspond to for geom_type {geom_type}? "
                                f"Pick a number listed above and press enter:"
                            )
                        )
                        if int(choice) not in range(len(options)):
                            raise ValueError("Number outside range!")
                    except KeyboardInterrupt:
                        print("\n\nProgram manually aborted.")
                        sys.exit()  # Allow for exiting code by pressing ctrl+c
                    except:
                        print(
                            f"Incorrect input. Please enter a number between 0 and {len(options)-1}"
                        )

                mapping[geom_type][source] = (target := options[int(choice)])
                f.write(separator.join([geom_type, source, target]) + "\n")
                print(
                    f"{source} is now mapped to {target} for geom_type {geom_type}.\n"
                )


# Write a CSV file with the user-defined mapping of MAC-names to MKLE-names for each geom_type.
# The "common" column indicates whether a specific source name occurs in all layers of this geom_type.
mapping_file = "mapping.csv"
print(f"Writing mapping file: {mapping_file}")
with open(mapping_file, "w") as f:
    # Write CSV headers
    f.write(separator.join(["geom_type", "source", "target", "common"]) + "\n")
    for geom_type in names.keys():
        for name in names[geom_type]:
            source = list(name.keys())[0]
            source_commonality = list(name.values())[0]
            target = mapping[geom_type][source]
            f.write(
                separator.join([geom_type, source, target, source_commonality]) + "\n"
            )

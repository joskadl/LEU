from operator import add
from functools import reduce
from pathlib import Path
import zipfile

"""This script creates a CSV file displaying a tree of relevant files/folders within a directory"""

# Folder for which to create the tree:
data_directory = Path(r"C:\Users\jla23480\Downloads\Data")
# Contents of directory of interest:
data_directory_contents = data_directory.glob("**/*")
filetypes_of_interest = [".shp", ".mdb", ".gml", ".gdb", ".zip"]


def list_zip_contents(file: Path) -> list:
    """Return list of file paths with relevant extensions within zip file"""
    with zipfile.ZipFile(file, "r") as f:
        return [
            file / x for x in f.namelist() if Path(x).suffix in filetypes_of_interest
        ]


# Get all .zip, .shp, .mdb and .gml file paths
files = [x for x in data_directory_contents if x.suffix in filetypes_of_interest]

# Replace .zip file elements with their content  # TODO: filter for relevant extensions again?
files = [list_zip_contents(file) if file.suffix == ".zip" else [file] for file in files]

# Unpack lists of nested paths from .zip files to one list of all relevant file paths
files = reduce(add, files)

# Make all filepaths relative to data_directory
files = [x.relative_to(data_directory) for x in files]

# Get deepest filepath to get number of required CSV columns
length_longest_filepath = max([len(x.parts) for x in files])

# Create a tree of all relevant folders and files
separator = ";"  # Separator for CSV file (semicolon for Excel readability)
previous_path = Path()  # Path to compare next filepath to
with open("file_tree.csv", "w", encoding="utf-8") as f:
    for filepath in files:
        shared_path_length = len(
            [x for x, y in zip(previous_path.parts, filepath.parts) if x == y]
        )

        # For all new parts in filepath, write a newline for this part, preceded by appropriate number of separators
        for n in range(shared_path_length, len(filepath.parts)):
            # First separator is to make a column for indicating what to do with a file or folder
            f.write(
                f"{separator}{separator*n}{filepath.parts[n]}{separator*(length_longest_filepath-n-1)}\n"
            )

        previous_path = filepath  # Remember filepath to compare next path with

from operator import add
from functools import reduce
from pathlib import Path
import zipfile

# Goal: make a tree of data directory, in CSV format, listing .gdb, .shp, .mdb and .gml files (also in .zip)

data_directory = Path(r"C:\Users\jla23480\Downloads\Data")
data_directory_contents = data_directory.glob("**/*")  # Directory containing all data
filetypes_of_interest = [".shp", ".mdb", ".gml", ".gdb", ".zip"]


def list_zip_contents(file: Path) -> list:
    """Return list of file paths within zip file, for relevant extensions"""
    with zipfile.ZipFile(file, "r") as f:
        return [file/x for x in f.namelist() if Path(x).suffix in filetypes_of_interest]


# Get all .zip, .shp, .mdb and .gml file paths
files = [x for x in data_directory_contents if x.suffix in filetypes_of_interest]

# For all .zip files, replace entry with entry appended with internal file paths wit relevant suffix
files = [list_zip_contents(file) if file.suffix == ".zip" else [file] for file in files]

# Unpack lists of nested paths from .zip files to one list of all relevant file paths
files = reduce(add, files)

# Create a tree of all relevant folders and files
separator = "\t"  # Separator for CSV file (comma or semicolon for Excel readability)
previous_path = Path()  # Path to compare next filepath to
for filepath in files:
    filepath = filepath.relative_to(data_directory)
    shared_path_length = len([x for x, y in zip(previous_path.parts, filepath.parts) if x == y])

    # For all new parts in filepath, print a newline for this part, preceded by appropriate number of separators
    for n in range(shared_path_length, len(filepath.parts)):
        print(f"{separator*n}{filepath.parts[n]}")

    previous_path = filepath  # Remember filepath to compare next path with

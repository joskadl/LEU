# TODO: make a tree of data directory, in CSV format, listing .gdb, .shp, .mdb and .gml files (also in .zip)
from operator import add
from functools import reduce
from pathlib import Path
import zipfile

data_directory = Path(r"C:\Users\jla23480\Downloads\Data").glob("**/*")  # Directory containing all data
filetypes_of_interest = [".shp", ".mdb", ".gml", ".gdb", ".zip"]


def list_zip_contents(file: Path) -> list:
    """Return list of file paths within zip file, for relevant extensions"""
    with zipfile.ZipFile(file, "r") as f:
        return [file/x for x in f.namelist() if Path(x).suffix in filetypes_of_interest]


# Get all .zip, .shp, .mdb and .gml file paths
files = [x for x in data_directory if x.suffix in filetypes_of_interest]

# For all .zip files, replace entry with entry appended with internal file paths wit relevant suffix
files = [list_zip_contents(file) if file.suffix == ".zip" else [file] for file in files]

# Unpack lists of nested paths from .zip files to one list of all relevant file paths
files = reduce(add, files)

for file in files:
    print(file)

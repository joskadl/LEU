import datetime
from pathlib import Path

import geopandas as gpd
import fiona

# Note: this script requires to be run from a conda virtual environment

"""This script serves to iterate over a list of 'problem files', which cannot be opened in ArcGis because of missing
data in the 'Velddatum' column. These missing fields are filled with the standard OleAut date ("1899-12-30T00:00:00"),
and the fixed files are written to the original folder structure, based on the 'fixed_files' root folder.
"""

problem_files = [
    Path(r"Overige-data-ronde-1_ronde-2/2020/2020_Veldwerk_toevoegingen/e7ab4f57ed89462b90da62ae326aa22d.gdb"),
    Path(r"Overige-data-ronde-1_ronde-2\2020\2020_Veldwerk_MAC_2020_WFL1\be6fc8639b80467084bb208465dd44b4.gdb"),
    Path(r"Overige-data-ronde-1_ronde-2\2021\2021_Veldwerk_MAC_DRENTHE (1)\9a925e79-3854-41f2-af13-d3258384e32e.gdb"),
    Path(r"Overige-data-ronde-1_ronde-2\2021\2021_Veldwerk_MAC_WFL1_Drenthe_3-11-2021\06dbb976-5062-4050-8cee-835f71454009.gdb"),
    Path(r"Overige-data-ronde-1_ronde-2\2021\MAC_FL_FRL_NH_UT_ZH_export_3-11-2021_1300_uur\e1dda71f-90f1-43af-bc2a-03fcf6e6f9eb.gdb"),
    Path(r"Overige-data-ronde-1_ronde-2\2021\MAC_FL_FRL_NH_UT_ZH_export_3-11-2021_1300_uur (1)\e1dda71f-90f1-43af-bc2a-03fcf6e6f9eb.gdb"),
    Path(r"Overige-data-ronde-1_ronde-2\2021-2\2021_Veldwerk_MAC_WFL1_3235613306241120939\61488098-0ec8-4bb1-ba92-d4d966ac8413.gdb"),
    Path(r"Overige-data-ronde-1_ronde-2\2021-2\MAC_FL_FRL_NH_UT_ZH_-920725533293801705\fd99986b-5f99-44cc-825e-53a594ab1fb2.gdb"),
]

for problem_file in problem_files:
    print(f"Trying to fix: {problem_file}")
    for layer in fiona.listlayers(problem_file):
        layer_content = gpd.read_file(problem_file, layer=layer)
        if "Velddatum" in layer_content:
            for velddatum in layer_content["Velddatum"]:
                if velddatum is None:
                    print("None found!")
                else:
                    # See whether casting to datetime yields errors, as a sanity check
                    new_date = datetime.datetime.fromisoformat(velddatum)

            layer_content["Velddatum"] = layer_content["Velddatum"].fillna("1899-12-30T00:00:00")
            # Write back to file, in fixed_files root directory
            fixed_file = "fixed_files"/problem_file.with_name(f"{problem_file.stem}_fixed").with_suffix('.gpkg')
            fixed_file.parent.mkdir(parents=True, exist_ok=True)
            layer_content.to_file(fixed_file, layer=layer, driver="GPKG")

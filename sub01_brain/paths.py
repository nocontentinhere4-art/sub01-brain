"""Where the data files live (one place to change; data/DATA.md says where each file comes from and its licence).

Default: the `data/` directory next to this package in a checkout. Override with the environment variable
SUB01_BRAIN_DATA (a directory with the same layout) when the package is installed elsewhere or the data is swapped,
e.g. for a connectome of your own built with pipeline/build_connectome.py. Every loader takes an explicit path too.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent                # the checkout (sub01_brain/ and data/ side by side)
DATA = Path(os.environ.get("SUB01_BRAIN_DATA") or ROOT / "data")

MRI = DATA / "mri"                                           # derived from the person's scans: CC BY-SA 4.0 (data/mri/LICENSE)
CONNECTOME = MRI / "connectome.npz"                         # 214 regions: streamline counts, fibre lengths (mm), names, centroids
CONNECTOME_V2 = MRI / "connectome_v2.npz"                   # MRtrix3 + SIFT2 version (the slow layer was fitted on it)
ATLAS_NAMES = MRI / "atlas_names.json"                      # the 214 region names, in the order every array uses
REGION_VOLUMES = MRI / "region_volumes.json"                # mm3 per region (population sizes of the spiking networks)
REST_DIR = MRI / "rest"                                     # recorded resting-state runs, z-scored region x time (+ qc.json)
SLOW_LAYER = MRI / "slow_layer.npz"                         # the fitted BOLD-band Hopf layer (twin/hopf.py SlowLayer)
RECEPTORS = DATA / "receptors" / "receptors_214.csv"        # receptor densities per region (twin/neurochem.py): group post-mortem
                                                             # data of other people, CC BY 4.0 (data/receptors/LICENSE)

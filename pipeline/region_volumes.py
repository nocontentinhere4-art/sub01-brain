"""Build data/mri/region_volumes.json: the volume (mm3) of every atlas region in the subject's own 1 mm T1 labels.

The spiking networks size each region's population in proportion to this (spiking/wiring.py allocate). Voxels are
1 mm3 on the atlas_subject.py grid, so volume = voxel count of label k+1 for region k of data/mri/atlas_names.json.

    python pipeline/region_volumes.py            # reads data/mri/t1/labels_t1.nii.gz, writes data/mri/region_volumes.json
"""
import json
from pathlib import Path

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = json.loads((ROOT / "data" / "mri" / "atlas_names.json").read_text())
    img = nib.load(ROOT / "data" / "mri" / "t1" / "labels_t1.nii.gz")
    lab = np.asanyarray(img.dataobj).astype(np.int32)
    vox_mm3 = float(abs(np.linalg.det(img.affine[:3, :3])))
    counts = np.bincount(lab.ravel(), minlength=len(names) + 1)[1:len(names) + 1]
    out = {"unit": "mm3", "source": "data/mri/t1/labels_t1.nii.gz voxel counts (1 mm T1, subject space)",
           "volumes": {nm: int(round(c * vox_mm3)) for nm, c in zip(names, counts)}}
    (ROOT / "data" / "mri" / "region_volumes.json").write_text(json.dumps(out))
    print(f"{len(names)} regions, {int(counts.sum())} labelled voxels, smallest {counts.min()} largest {counts.max()}")


if __name__ == "__main__":
    main()

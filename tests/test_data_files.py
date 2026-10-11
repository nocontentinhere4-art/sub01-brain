"""The released data files agree with each other (one region order everywhere; data/DATA.md).

    python -m pytest tests/test_data_files.py -q
"""
import csv
import json

import numpy as np
import pytest

from sub01_brain import paths


def names():
    return json.loads(paths.ATLAS_NAMES.read_text())


def test_atlas_has_214_regions_in_schaefer_then_nuclei_order():
    nm = names()
    assert len(nm) == 214 and nm[0].startswith("7Networks_LH_") and nm[199].startswith("7Networks_RH_")
    assert all(any(k in x for k in ("Thalamus", "Caudate", "Putamen", "Pallidum", "Hippocampus", "Amygdala", "Accumbens"))
               for x in nm[200:])


@pytest.mark.parametrize("path", [paths.CONNECTOME, paths.CONNECTOME_V2])
def test_connectomes_match_the_atlas(path):
    if not path.exists():
        pytest.skip(f"{path.name} not present")
    z = np.load(path, allow_pickle=True)
    assert [str(x) for x in z["names"]] == names()
    W, L = z["weights"], z["lengths"]
    assert W.shape == L.shape == (214, 214) and np.allclose(W, W.T) and np.all(np.diag(W) == 0)
    assert (L[W > 0] > 0).all() and L.max() < 400                     # mm (longest mean fibre length ~360)
    assert z["centroids"].shape == (214, 3)


def test_region_volumes_cover_the_atlas():
    vol = json.loads(paths.REGION_VOLUMES.read_text())["volumes"]
    assert set(vol) == set(names()) and min(vol.values()) > 0


def test_slow_layer_and_receptors_follow_the_atlas():
    if paths.SLOW_LAYER.exists():
        d = np.load(paths.SLOW_LAYER, allow_pickle=False)
        assert [str(x) for x in d["names"]] == names() and d["C_wiring"].shape == (214, 214)
    rows = list(csv.DictReader(open(paths.RECEPTORS)))
    assert [r["name"] for r in rows] == names()


def test_rest_runs_are_z_scored_region_time_series():
    files = sorted(paths.REST_DIR.glob("*.npz"))
    if not files:
        pytest.skip("resting-state runs not present")
    qc = json.loads((paths.REST_DIR / "qc.json").read_text())
    kept = {k for k, v in qc.items() if v.get("kept", True)}
    assert {f.stem for f in files} <= set(qc) and all(f.stem in kept for f in files)
    d = np.load(files[0])
    ts = np.nan_to_num(d["ts"].astype(np.float32))
    assert ts.shape[1] == 214 and float(d["tr"]) > 0
    assert abs(np.nanmean(ts)) < 0.1 and 0.5 < np.nanstd(ts) < 1.5

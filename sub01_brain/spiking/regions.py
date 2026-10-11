"""Regions of the real wiring: names, volumes, connectome weights, fibre lengths and stimulus groups.

Self-contained (no import of brain_sim) so a GPU pod only needs numpy + torch. The group patterns are the
same as brain_sim.GROUPS so the page and the chat rules speak about the same networks.
"""
import json
from pathlib import Path

import numpy as np

from sub01_brain import paths

GROUPS = {
    "visual": ["_Vis_"],
    "somatomotor": ["_SomMot_"],
    "attention": ["_DorsAttn_"],
    "salience": ["_SalVentAttn_"],
    "limbic": ["_Limbic_"],
    "control": ["_Cont_"],
    "default": ["_Default_"],
    "reward": ["Accumbens", "Caudate", "Putamen"],
    "fear": ["Amygdala"],
    "memory": ["Hippocampus"],
    "relay": ["Thalamus"],
}


def is_language(name):
    """Left temporal + frontal operculum parcels (language proxy, as in brain_sim.LANGUAGE)."""
    return "_LH_" in name and ("Temp" in name or "FrOper" in name)


class Regions:
    def __init__(self, connectome=paths.CONNECTOME, volumes=paths.REGION_VOLUMES):
        """connectome: an npz with weights, lengths, names, centroids (pipeline/build_connectome.py); volumes: the JSON
        {"volumes": {name: mm3}} the population sizes follow."""
        z = np.load(Path(connectome), allow_pickle=True)
        self.names = [str(x) for x in z["names"]]
        self.n = len(self.names)
        self.W = z["weights"].astype(np.float64)              # streamline counts (symmetric, zero diagonal)
        L = z["lengths"].astype(np.float64)                   # mean fibre length, mm
        self.lengths = np.where(L > 0, L, np.nanmean(L[L > 0]))
        self.centroids = z["centroids"].astype(np.float64)
        vol = json.loads(Path(volumes).read_text())["volumes"]
        self.volumes = np.array([vol[nm] for nm in self.names], dtype=np.float64)   # mm3, subject T1 labels
        self.groups = {k: [i for i, nm in enumerate(self.names) if any(p in nm for p in pats)]
                       for k, pats in GROUPS.items()}
        self.groups["language"] = [i for i, nm in enumerate(self.names) if is_language(nm)]

    def idx(self, pred):
        return [i for i, nm in enumerate(self.names) if pred(nm)]

    def hemisphere(self, i):
        nm = self.names[i]
        return "L" if ("_LH_" in nm or nm.startswith("Left")) else "R"

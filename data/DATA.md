# The data files

Everything the model runs on, 23 MB in all; nothing is larger than 6 MB, so there are no release assets outside git.
Two bundles, two licences; the full attributions are in [NOTICE.md](../NOTICE.md). Every array uses one region order:
`mri/atlas_names.json` (200 Schaefer cortical parcels, then 14 Harvard-Oxford deep nuclei), checked by
`tests/test_data_files.py`. The loaders take explicit paths, so any file can be swapped for one of your own (e.g. a
connectome built with `pipeline/build_connectome.py` from another public dataset); `SUB01_BRAIN_DATA` points the whole
package at another data directory with this layout.

## `mri/`: derived from one person's public MRI scans. Licence: **CC BY-SA 4.0** ([mri/LICENSE](mri/LICENSE))

Source: the MyConnectome dataset, OpenNeuro ds000031 (licence CC0; PDDL on the legacy OpenfMRI record); acknowledgement
and citation as the dataset record requires, in NOTICE.md. The raw scans (~900 MB) are not here: `pipeline/fetch_data.sh`
downloads them. Everything below is the project's own processing of them.

| file | size | what | built by |
|---|---|---|---|
| `connectome.npz` | 756 KB | v1: 214 x 214 streamline counts (`weights`), mean fibre lengths in mm (`lengths`), `names`, `centroids` (DWI world mm); dipy CSD tractography | `pipeline/atlas_subject.py` → `pipeline/build_connectome.py` |
| `connectome_v2.npz` | 424 KB | v2: MRtrix3 msmt-CSD + iFOD2 + SIFT2, consistency-thresholded; `weights`, `counts`, `lengths`, `names`, `centroids`, `meta`. The slow layer was fitted on it | `pipeline/tract.sh` (on a many-core machine) → `pipeline/build_connectome_v2.py` |
| `atlas_names.json` | 8 KB | the 214 region names, the order of every array | `pipeline/atlas_subject.py` |
| `region_volumes.json` | 8 KB | mm3 per region in the subject's 1 mm T1 labels: the spiking populations' sizes | `pipeline/region_volumes.py` |
| `rest/*.npz` (131 files) + `rest/qc.json` | 22 MB | the 131 QC-passed resting-state runs (of 132; one failed the homotopic-correlation QC): `ts` (T x 214, float16, band-passed 0.01-0.1 Hz, z-scored), `tr` (s), `key` (the run's path in the dataset). `qc.json`: homotopic vs mean correlation per run and whether it was kept | `pipeline/process_rest.py` |
| `slow_layer.npz` | 100 KB | the fitted BOLD-band Hopf layer: `C_wiring` (connectome v2 x one fitted global coupling), `C` (effective connectivity), `freqs`, `a`, `beta`, `names`, `meta` (held-out scores and the fit / held-out session split) | `pipeline/real_wiring.py export` |
| `t1/labels_t1.nii.gz` | 460 KB | the atlas warped into the subject's 1 mm T1 (labels 1-214). An adaptation of the Harvard-Oxford atlas: the file that makes the bundle CC BY-SA | `pipeline/atlas_subject.py` |
| `t1/brainmask_t1.nii.gz`, `t1/t1_to_dwi.npy` | 172 KB, 4 KB | skull-stripped T1 (no face, no skull), its brain mask (the ICBM mask warped), the rigid T1 → DWI transform. Only `pipeline/process_rest.py` needs them (to register each run); drop them if you do not rebuild the rest series | `pipeline/atlas_subject.py` | (the skull-stripped T1 itself is not shipped: `pipeline/atlas_subject.py` rebuilds it from the public scans)

## `receptors/`: group post-mortem receptor data from other people. Licence: **CC BY 4.0** ([receptors/LICENSE](receptors/LICENSE))

| file | size | what | built by |
|---|---|---|---|
| `zilles2017_all_layers.csv` | 8 KB | 15 receptors x 44 cortical areas (Zilles & Palomero-Gallagher 2017, Supplementary Table 2) + our approximate MNI centroid per area | `pipeline/build_receptors.py` (download + extract) |
| `receptors_214.csv` | 36 KB | 7 receptors mapped onto the 200 Schaefer parcels by inverse-distance weighting; the 14 subcortical rows are blank (no data; the model uses a flagged cortical-mean fallback) | `pipeline/build_receptors.py` |
| `RECEPTORS_SOURCES.md` | | the sources looked at, used and not used (non-commercial PET maps were rejected) | hand-written |

## The scanned person stays anonymous

The derived files carry no face, skull, name, age, sex or scanner identifier; a 214-region matrix or a parcel-mean time
series can be matched only against the public source scans themselves, which adds nothing. The identification risk is
in words, not numbers: this repository names the dataset and cites its paper because the data record requires it, and
says nothing else about the participant. Do not add names, demographics, links or dataset metadata (`Authors`, contact
lines). Every result in `docs/` is a statement about the model, never about anyone's health.

## Rebuilding or swapping

`pipeline/README.md` gives the order of the scripts and what each needs. A connectome from another public dataset or
a synthetic one works as long as the npz has `weights`, `lengths`, `names`, `centroids` with one row per region and a
matching `region_volumes.json`; the group patterns in `brain_sim.GROUPS` / `spiking/regions.py` expect Schaefer-style
names (`_Vis_`, `_SomMot_`, …) and the nucleus names (`Hippocampus`, `Thalamus`, …).

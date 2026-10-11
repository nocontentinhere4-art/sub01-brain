# Rebuilding the data from the raw MRI

Nothing here is needed to run the model: `data/` ships every derived file. These scripts show how each one was made and
let you rebuild them, or build the same files for another public dataset. They need the MRI stack
(`pip install -r requirements-pipeline.txt`: dipy, nilearn, nibabel, netneurotools, torch, matplotlib) and, for the v2
connectome, MRtrix3. Run everything from the repository root. `raw/` (downloads) and `out/` (working files) are
git-ignored; the finished files are copied into `data/mri/`.

| step | script | needs | writes | time |
|---|---|---|---|---|
| 1. download the scans (~900 MB: one T1, one DWI) | `pipeline/fetch_data.sh` | curl | `raw/` | minutes |
| 2. atlas into the subject's anatomy: ICBM template → the T1 (affine + SyN), Schaefer-200 + Harvard-Oxford nuclei warped along, brain mask, rigid T1 → DWI | `python pipeline/atlas_subject.py` | step 1, step 3's `out/mean_b0.nii.gz` for the last transform (run 3 once, then 2, then 3 again, or copy `data/mri/t1/t1_to_dwi.npy`) | `out/t1_1mm.nii.gz`, `out/t1_brain_1mm.nii.gz`, `out/brainmask_t1.nii.gz`, `out/labels_t1.nii.gz`, `out/atlas_names.json`, `out/t1_to_dwi.npy` | ~30 min |
| 3. connectome v1: CSD + deterministic tractography (dipy), streamline counts and lengths per region pair | `python pipeline/build_connectome.py` | steps 1-2 | `out/connectome.npz` (+ `fa`, `mean_b0`, `labels_dwi`) | ~1 h, 16 cores |
| 4. region volumes (the spiking populations' sizes) | `python pipeline/region_volumes.py` | `data/mri/t1/labels_t1.nii.gz`, `data/mri/atlas_names.json` | `data/mri/region_volumes.json` | seconds |
| 5. resting-state series: stream each BOLD run, register to the T1, parcel means, band-pass, z-score; QC (homotopic correlation) | `mkdir -p out && cp data/mri/t1/labels_t1.nii.gz data/mri/t1/t1_brain_1mm.nii.gz data/mri/atlas_names.json out/ && python pipeline/process_rest.py 132 --workers 6` | `pipeline/rest_runs.txt` (the 132 runs), ~2 GB RAM per worker | `out/rest/*.npz`, `out/rest/qc.json` → copy to `data/mri/rest/` | ~2 h |
| 6. connectome v2: MRtrix3 (dwigradcheck, msmt-CSD, iFOD2 in independent chunks, SIFT2), then a consistency threshold | `pipeline/tract.sh` on a many-core machine with MRtrix3 3.0.8 (inputs: 5TT, labels and mask on the T1 grid; see the script's header), then `python pipeline/build_connectome_v2.py` | step 2 | `data/analysis/connectome_v2_raw.tar.gz` → `data/mri/connectome_v2.npz` | hours |
| 7. the slow layer: fit the Hopf model on half of the runs (by session), score on the other half, against 100 + 100 randomised wirings; export | `python pipeline/real_wiring.py prep --conn data/mri/connectome_v2.npz --tag v2 --nulls 100`, `run --tag v2 --workers 30`, `report --tags v2`, `export --tag v2` | steps 5-6, torch, netneurotools | `docs/real_wiring/`, `data/mri/slow_layer.npz` | hours (30 cores) |
| 8. receptor maps: Zilles & Palomero-Gallagher 2017 table → 200 parcels by inverse-distance weighting | `python pipeline/build_receptors.py` | internet (GitHub mirrors), `data/mri/atlas_names.json` | `data/receptors/*.csv` | minutes |

`atlas_subject.py`, `build_connectome.py` and `process_rest.py` read and write `out/` and `raw/` relative to the
current directory, as in the parent project; copy their results into `data/mri/` by hand (the layout is in
`data/DATA.md`). `build_connectome_v2.py`, `real_wiring.py`, `region_volumes.py` and `build_receptors.py` read and write
`data/` directly.

The scripts name the OpenNeuro accession in their download URLs because they have to; that is the dataset's public
identifier and the whole of what this repository says about its source (see `NOTICE.md`). Another BIDS dataset works
by changing `fetch_data.sh`, `rest_runs.txt` and the file names at the top of `build_connectome.py` / `atlas_subject.py`.

What each step does and why, with the numbers, is in `docs/real_wiring_report.md` (connectome v2, the slow layer, the
null models) and `docs/spiking_report.md` §1 (how the connectome becomes a spiking network).

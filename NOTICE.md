# Notice and attribution

This licence covers the code (sub01_brain/, pipeline/, tests/) and the documentation. The data files under `data/` (`sub01_brain/data/`)
are licensed separately, per directory: data/mri/LICENSE (CC BY-SA 4.0) and data/receptors/LICENSE (CC BY 4.0).
NOTICE.md lists every third-party source and the attribution it requires.

This repository contains a computer model of large-scale brain activity and the derived data it runs on. It is a
model, not a mind: it does not think, feel or understand, it is not conscious and it is not the person whose scans
it was built from. Code is © 2026 SUB-01 project, MIT License (see LICENSE). Derived data are licensed per
directory (see the LICENSE file in each data directory: data/mri/ CC BY-SA 4.0, data/receptors/ CC BY 4.0).
Third-party sources:

## MRI data (one person's public scans; the person is not named here or anywhere in this repository)

Data for the MyConnectome project were obtained from the OpenNeuro database (ds000031),
https://openneuro.org/datasets/ds000031 (licence: CC0; the legacy OpenfMRI record states PDDL). Also cite:
Poldrack et al. (2015). Long-term neural and physiological phenotyping of a single human. Nature Communications
6:8885, doi:10.1038/ncomms9885. The raw scans are not redistributed here; the scripts in pipeline/ download them.
Files derived from them (connectome matrices, parcellated resting-state time series, a skull-stripped T1, the atlas
labels in the subject's space, the fitted slow layer) are provided under CC BY-SA 4.0 (see data/mri/LICENSE). None of
them contains a face, a skull or any personal data.

**The real person stays anonymous.** Nothing in this repository identifies them, and nothing may be added that does:
no name, no demographics, no profession, no links to personal pages, no field copied from the dataset's metadata that
carries a name (`dataset_description.json` → `Authors`, the legacy record's contact line). The citation above is the
one the dataset record requires and is the whole of what this repository says about the source. Every number reported
here is a statement about the *model* (a fit, a test score), never a finding about anyone's brain or health. The
BIDS file names (`sub-01_ses-NNN_…`) are the dataset's own anonymous labels.

## Atlases used to parcellate the scans

- Schaefer A, Kong R, Gordon EM, Laumann TO, Zuo X-N, Holmes AJ, Eickhoff SB, Yeo BTT (2018). Local-global
  parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. Cerebral Cortex 28:3095-3114.
  Parcellation and centroids © 2016 Computational Brain Imaging Group (CBIG), MIT License,
  https://github.com/ThomasYeoLab/CBIG.
- Harvard-Oxford subcortical structural atlas (Harvard Center for Morphometric Analysis), distributed with FSL under
  CC BY-SA 4.0 (https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html). Cite: Desikan RS et al. (2006) NeuroImage
  31:968-980; Frazier JA et al. (2005) Am J Psychiatry 162:1256-1265; Makris N et al. (2006) Schizophr Res
  83:155-171; Goldstein JM et al. (2007) Biol Psychiatry 61:935-945. The warped label image
  data/mri/t1/labels_t1.nii.gz is an adaptation of this atlas and is therefore CC BY-SA 4.0.
- ICBM 152 2009c nonlinear asymmetric template (used for registration and for the brain mask): Copyright (C)
  1993-2004 Louis Collins, McConnell Brain Imaging Centre, Montreal Neurological Institute, McGill University.
  Permission to use, copy, modify, and distribute this software and its documentation for any purpose and without
  fee is hereby granted, provided that the above copyright notice appear in all copies. Fonov V et al. (2011)
  NeuroImage 54:313-327. Obtained via nilearn (`fetch_icbm152_2009`).

## Receptor densities (group post-mortem data from other people)

Zilles K, Palomero-Gallagher N (2017) Multiple transmitter receptors in regions and layers of the human cerebral
cortex. Frontiers in Neuroanatomy 11:78, doi:10.3389/fnana.2017.00078, © 2017 Zilles and Palomero-Gallagher,
Creative Commons Attribution License (CC BY). Table mirrored from https://github.com/AlGoulas/receptor_principles
(MIT, Copyright (c) 2020 AlGoulas). Changes: 7 receptors mapped onto the Schaefer-200 parcels by inverse-distance
weighting; subcortical rows left blank (see data/receptors/RECEPTORS_SOURCES.md).

## Software used, not redistributed

numpy, scipy (BSD); PyTorch (BSD-style); dipy (BSD-3, © 2008-2026 dipy developers); nilearn (BSD-3); nibabel (MIT);
netneurotools (BSD-3); MRtrix3 (MPL-2.0; Tournier J-D et al. (2019) NeuroImage 202:116137), used as a tool in
pipeline/tract.sh. Each under its own licence; none is copied into this repository.

## Published models re-implemented here (no code copied)

Deco G, Kringelbach ML, Jirsa VK, Ritter P (2017) Sci Rep 7:3095 (Hopf whole-brain model); Ponce-Alvarez A, Deco G
(2024) Sci Rep (its linear approximation); Gilson M et al. (2016) PLoS Comput Biol (effective connectivity);
Izhikevich EM (2007) Cereb Cortex 17:2443 (dopamine-modulated STDP); Kagan BJ et al. (2022) Neuron 110:3952 (the
Pong task design, not its claims); Bergman RN et al. (1979) and Dalla Man C et al. (2006) (the glucose model);
Phillips AJK, Robinson PA (2007) J Biol Rhythms 22:167 (the sleep circuit the parent project's sleep engine uses; the
engine itself is not in this repository).

## Not in this repository

The parent project's 3D room, character, web pages, browsing/chat machinery and the brain page's neuron and vessel
assets (NeuroMorpho.Org, H01, BodyParts3D, VENAT) are not part of this package and carry their own notices there.

# Contributing

Thank you for looking. A few rules keep this repository what it is.

**What it is.** A model of brain activity: a rate/Hopf model and spiking networks on one real public connectome. It is
not a mind. Code, docstrings, docs and commit messages never say it thinks, understands, feels, wants, is conscious or
alive; "it decides" means the race in `spiking/choice.py`, nothing more. The scanned person is anonymous: cite the
dataset exactly as `NOTICE.md` does and add nothing about the participant (no name, demographics, links or dataset
metadata). Report results as results about the model, including the negative ones.

**Before a pull request.**

```bash
pip install -r requirements.txt pytest
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q
python -m sub01_brain.demo --quick
```

With torch installed (`requirements-torch.txt`) the spiking tests run in full; without it they skip, as in CI.

**Style.** Dense, commented code: say why, cite the paper or the measurement a constant comes from, keep the units in
the comment. Tests sit next to the behaviour (`tests/test_<module>.py`). Small, behaviour-preserving diffs over
rewrites. New data files go under `data/<bundle>/` with their licence and a row in `data/DATA.md`; anything larger
than 50 MB is a release asset, not a commit. No secrets, no owner media, no third-party page copies.

**Changing the model.** The connectome weights `w0` are never learned over (learning lives in `dw`); the synapse set is
a deterministic function of `(Config structural fields, seed)` and `Config.config_hash()` guards learned-weight files:
if you change the construction, bump `spiking/config.py VERSION`. The numpy network (`spiking/live.py`) and the torch
network (`spiking/net.py`) must keep the same synapses (`tests/test_spiking_live.py::test_live_net_has_the_synapses_of_net_py`).

**Licence.** Code contributions are MIT like the rest; data contributions name their licence in `data/DATA.md`.

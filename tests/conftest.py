"""pytest setup: the checkout root on sys.path (so `sub01_brain` imports without installing) and one BLAS thread.

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q
The matrices are small (214 x 214); more BLAS threads only spin. Tests that need torch skip without it.
"""
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

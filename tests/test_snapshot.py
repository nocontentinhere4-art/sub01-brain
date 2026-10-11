"""sub01_brain.snapshot: a restored Brain continues exactly where the saved one was (random streams included).

    python -m pytest tests/test_snapshot.py -q
"""
import numpy as np
import pytest

from sub01_brain import paths, snapshot
from sub01_brain.brain_sim import Brain


@pytest.mark.parametrize("slow", [True, False], ids=["slow_on", "slow_off"])
def test_restore_continues_bit_for_bit(tmp_path, slow):
    if slow and not paths.SLOW_LAYER.exists():
        pytest.skip("slow layer not fitted")
    a = Brain(seed=3, slow=slow)
    a.run(1.0)
    a.stimulate("reward", 6.0)
    a.set_rhythm(6.0, coupling=0.8, noise=0.4)
    a.neuromod = np.linspace(-0.2, 0.2, a.n)
    a.step(37)                                                # mid-way between slow-layer updates
    snapshot.save(a, tmp_path / "s.npz")
    b = snapshot.load(tmp_path / "s.npz", seed=99, slow=slow)   # another seed: the state must come from the file
    assert b.t == a.t and b.f_hz == a.f_hz and b.g == a.g and b.slow_on == a.slow_on
    sa, sb = a.run(2.0), b.run(2.0)
    assert np.abs(sa - sb).max() < 1e-12
    assert a.state() == b.state()


def test_restore_refuses_another_wiring(tmp_path):
    a = Brain(seed=0, slow=False)
    snap = snapshot.snapshot(a)
    b = Brain(seed=0, slow=False)
    b.n += 1                                                  # pretend another atlas
    with pytest.raises(ValueError):
        snapshot.restore(b, snap)

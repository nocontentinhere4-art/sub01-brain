"""Snapshot and restore the dynamic state of the rate model (brain_sim.Brain), bit for bit.

The wiring (W, delays, names, group indices) is rebuilt from the data files by Brain(); what changes while it runs is
the delay ring buffer, the step counter, the stimulus / drive / neuromodulator vectors, the rhythm, the slow layer's
complex state and the random streams. `snapshot` collects exactly those; `restore` puts them back into a Brain built
with the same data, so `restore(Brain(), load(p))` continues the run as if it had never stopped (the random stream is
restored too, so the continuation is identical to 1e-12; tests/test_snapshot.py checks it).

    from sub01_brain.brain_sim import Brain
    from sub01_brain import snapshot
    b = Brain(); b.run(10)
    snapshot.save(b, "brain_state.npz")
    c = snapshot.load("brain_state.npz")        # a new Brain, in the saved state (same data files, same seed)
"""
import json
import pickle

import numpy as np

VERSION = 1


def _rng_state(rng):
    return pickle.dumps(rng.bit_generator.state)


def snapshot(brain):
    """The dynamic state as a dict of arrays + a JSON meta string (see module doc for what counts as state)."""
    d = {"buf": brain.buf, "stim": brain.stim, "drive": brain.drive, "slow_x": brain.slow_x,
         "neuromod": brain.neuromod, "omega": brain.omega, "rng": np.frombuffer(_rng_state(brain.rng), dtype=np.uint8)}
    meta = {"version": VERSION, "t": int(brain.t), "n": brain.n, "hist": brain.hist, "g": brain.g, "f_hz": brain.f_hz,
            "noise": brain.noise, "slow_on": bool(brain.slow_on), "slow_gain": brain.slow_gain,
            "names_hash": hash(tuple(brain.names)) & 0xFFFFFFFF, "slow": brain.slow is not None}
    if brain.slow is not None:
        d["slow_z"] = brain.slow.z
        d["slow_rng"] = np.frombuffer(_rng_state(brain.slow.rng), dtype=np.uint8)
        meta["slow_acc"] = brain.slow.acc
        meta["slow_which"] = brain.slow.which
    d["meta"] = np.array(json.dumps(meta))
    return d


def restore(brain, snap):
    """Put a snapshot (the dict of `snapshot`, or a loaded npz) into `brain`, in place; returns the brain."""
    meta = json.loads(str(snap["meta"]))
    if meta["n"] != brain.n or meta["hist"] != brain.hist:
        raise ValueError(f"snapshot is for another wiring ({meta['n']} regions, hist {meta['hist']}; "
                         f"this brain has {brain.n}, {brain.hist})")
    if meta["slow"] and brain.slow is None:
        raise ValueError("snapshot has a slow layer; build the Brain with slow=True (data/slow_layer.npz present)")
    brain.buf = np.array(snap["buf"], dtype=complex)
    brain.stim, brain.drive = np.array(snap["stim"], dtype=float), np.array(snap["drive"], dtype=float)
    brain.slow_x, brain.neuromod = np.array(snap["slow_x"], dtype=float), np.array(snap["neuromod"], dtype=float)
    brain.omega = np.array(snap["omega"], dtype=float)
    brain.t, brain.g, brain.f_hz, brain.noise = meta["t"], meta["g"], meta["f_hz"], meta["noise"]
    brain.slow_gain = meta["slow_gain"]
    brain.rng.bit_generator.state = pickle.loads(np.asarray(snap["rng"], dtype=np.uint8).tobytes())
    if meta["slow"]:
        brain.slow.z = np.array(snap["slow_z"], dtype=complex)
        brain.slow.x = brain.slow.z.real / brain.slow.sd
        brain.slow.acc = meta["slow_acc"]
        brain.slow.rng.bit_generator.state = pickle.loads(np.asarray(snap["slow_rng"], dtype=np.uint8).tobytes())
        brain.slow_on = meta["slow_on"]
    else:
        brain.use_slow_layer(False)
    return brain


def save(brain, path):
    np.savez_compressed(path, **snapshot(brain))


def load(path, brain=None, **brain_kw):
    """A Brain in the saved state: `brain` (an existing one, restored in place) or a new Brain(**brain_kw)."""
    from sub01_brain.brain_sim import Brain
    with np.load(path, allow_pickle=False) as z:
        snap = {k: z[k] for k in z.files}
    return restore(brain if brain is not None else Brain(**brain_kw), snap)

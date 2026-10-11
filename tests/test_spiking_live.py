"""The day network (spiking/live.py): cues and pools from labels, learning against a frozen twin, the child-process protocol.

numpy only (no torch), so it runs in CI. The learning check builds a 10k-neuron network and
its frozen twin (~25 s on one core). The torch check at the end (the same synapses as net.py) is skipped where torch is
absent.

    python -m pytest tests/test_spiking_live.py -q
"""
import asyncio
import json
import sys
import time
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sub01_brain.spiking import frames as frames_mod  # noqa: E402
from sub01_brain.spiking import live as L  # noqa: E402
from sub01_brain.spiking.config import Config  # noqa: E402

SMALL = 5000


def run(coro):
    return asyncio.run(coro)


@pytest.fixture(scope="module")
def small():
    return L.LiveBrain(SMALL, None)


# --- cues and pools from real labels ---------------------------------------------------------------------------------
def test_variable_offer_sets_any_labels(small):
    offers = [["read about bread", "wander somewhere else"],
              ["パン", "", "next page", "a", "keep reading this page"],
              ["apple", "river", "cloud", "stone", "lamp", "bird"],
              ["Search Tokyo parks", "search tokyo PARKS!", "museum hours"]]
    for labels in offers:
        d = small.decide(labels)
        assert d["pick"] in range(len(labels)) and len(d["pool_rates"]) == len(labels)
        assert 0 < d["sim_ms"] <= L.TIMEOUT_MS and np.isfinite(d["pool_rates"]).all()
        assert d["twin_pick"] in range(len(labels)) and len(d["twin_rates"]) == len(labels)
    assert len(small.decide([str(i) + " option" for i in range(9)])["pool_rates"]) == L.MAX_OPTIONS
    with pytest.raises(ValueError):
        small.decide(["only one"])


def test_pools_are_disjoint_and_words_keep_their_neurons(small):
    ch = small.ch
    labels = ["read about bread", "bread recipes", "tokyo parks", "wander somewhere else"]
    for lb in labels:
        ch.cue(lb)
    pools = L.label_pools(ch.action, [ch._aff[lb] for lb in labels])
    allp = np.concatenate(pools)
    assert len(allp) == len(np.unique(allp)) == len(ch.action) and all(len(p) > 0 for p in pools)
    # the same word lands on the same neurons in every label (what is learned about "bread" carries over)
    bread = L.label_cue(small.net, "bread", ch.cue_space)
    assert np.isin(bread, ch.cue("read about bread")).all() and np.isin(bread, ch.cue("bread recipes")).all()
    assert set(ch.cue("bread")) <= set(ch.cue_space)
    # rank-normalised affinity: a long label does not get a smaller pool on average
    a = L.label_affinity("one two three four", 1000)
    assert abs(a.mean() - 0.5) < 1e-9 and abs(a.std() - L.label_affinity("one", 1000).std()) < 1e-9


def test_lean_is_bounded_and_centred():
    ln = L.lean([5.0, 9.0, 4.0])
    assert ln[1] > 0 > ln[2] and np.all(np.abs(ln) <= 1) and abs(L.lean([3, 3])[0]) < 1e-12


# --- learning -------------------------------------------------------------------------------------------------------
def test_learning_beats_the_frozen_twin_on_a_synthetic_stream():
    t0 = time.process_time()
    b = L.LiveBrain(10_000, None)
    r = L.synthetic(b, trials=100, seed=1)
    cpu = time.process_time() - t0
    print(f"\nlive 10k, 100 decisions with variable offers: learned {r['learned']}, frozen twin {r['twin']}, "
          f"chance {r['chance']}; curve {r['curve']} vs {r['twin_curve']}; {cpu:.1f} s CPU")
    assert r["learned"] >= r["twin"] + 0.15 and r["learned"] >= r["chance"] + 0.15
    assert abs(r["twin"] - r["chance"]) < 0.15                     # the twin never learns: near chance
    assert np.abs(b.tw.net.w[b.ch.pidx] - b.ch.w0).max() == 0      # the twin's weights never moved
    assert np.abs(b.dw).max() > 0 and (b.ch.w0 + b.dw <= b.ch.w_max + 1e-6).all() and (b.ch.w0 + b.dw >= -1e-6).all()


def test_learning_rate_decays_to_a_floor(small):
    n0 = small.n_learn
    try:
        small.n_learn = 0
        assert small.eta() == L.ETA
        small.n_learn = int(L.ETA_HALF)
        assert abs(small.eta() - L.ETA / 2) < 1e-12
        small.n_learn = 10 ** 6
        assert small.eta() == L.ETA * L.ETA_FLOOR
    finally:
        small.n_learn = n0


def test_learn_tags_the_followed_pool_only_for_that_decision(small):
    d = small.decide(["read about bread", "tokyo parks", "jazz records"], did="x")
    dw0 = small.dw.copy()
    assert small.learn("unknown", 0, 0.5)["ok"] is False
    assert small.learn("x", 7, 0.5)["ok"] is False                 # not an offered option: nothing learned
    small.decide(["read about bread", "tokyo parks", "jazz records"], did="x")
    r = small.learn("x", 0, 0.5)
    assert r["ok"] and r["da"] == 1.0                              # DA_GAIN x 0.5, clipped to 1
    up = small.dw - dw0
    q = small.ch.post
    assert not np.any(up[(q < 0) | ~np.isin(q, small.ch.action)])  # only synapses onto offered pools moved
    assert small.learn("x", 0, 0.5)["ok"] is False                 # one dopamine per decision
    assert d["pick"] in (0, 1, 2)
    small.decide(["a b", "c d"], did="own")
    assert small.learn("own", None, -0.2)["ok"]                    # no "followed": the network's own pick


def test_weights_persist_across_a_restart_and_a_torn_file_is_kept_aside(tmp_path):
    path = tmp_path / "spiking" / "live_weights.npz"
    a = L.LiveBrain(SMALL, path, twin=False)
    thr = a.ch.thr_hz
    for i in range(3):
        a.decide(["read about bread", "tokyo parks"], did=i)
        a.learn(i, 0, 0.4)
    b = L.LiveBrain(SMALL, path, twin=False)
    assert b.n_learn == 3 and b.n_decisions == 3 and b.calib is None and b.ch.thr_hz == thr   # no recalibration
    assert np.array_equal(a.dw, b.dw) and np.array_equal(a.net.w, b.net.w)
    assert not list(path.parent.glob("*.tmp"))
    path.write_bytes(path.read_bytes()[:100])                      # torn by a kill mid-write
    c = L.LiveBrain(SMALL, path, twin=False)
    assert c.n_learn == 0 and not np.any(c.dw) and list(path.parent.glob("live_weights.npz.corrupt-*"))
    d = L.LiveBrain(SMALL + 1000, path, twin=False)                # another network: starts fresh, never mixes
    assert d.n_learn == 0


# --- the child process -------------------------------------------------------------------------------------------
async def _ready(cl, s=60):
    for _ in range(int(s * 10)):
        if cl.ready:
            return True
        await asyncio.sleep(0.1)
    return False


def test_child_process_protocol_frames_learning_and_restart(tmp_path):
    async def go():
        cl = L.LiveClient(tmp_path, n_neurons=SMALL)
        frames = []

        async def on_frame(f):
            frames.append(f)
        cl.on_frame = on_frame
        assert (await cl.decide(["a b", "c d"]))["why"] == "spiking network offline"
        await cl.start()
        try:
            assert await _ready(cl)
            ans = await cl.decide(["read about bread", "tokyo parks", "wander somewhere else"], did="b-1")
            assert ans["type"] == "decision" and ans["id"] == "b-1" and len(ans["pool_rates"]) == 3
            assert ans["pick"] in range(3) and ans["sim_ms"] > 0 and ans["n_neurons"] == SMALL and ans["wall_ms"] < 2000
            await asyncio.sleep(0.2)
            f = [x for x in frames if x.get("phase") == "deciding"]
            assert f and f[-1]["net"] == "cpu" and f[-1]["n_neurons"] == SMALL and "reward" in f[-1]["groups"]
            r = f[-1]["raster"]
            assert r["n"] == SMALL and r["t1"] > r["t0"] and "spikes" not in r       # every neuron recorded (#62)
            n3 = f[-1]["n3"]                                            # ...and packed: region, slot, ms (frames.py)
            sp = frames_mod.unpack_spikes(n3["sq"], n3["span"])
            assert n3["race"] and n3["ns"] > 0 and 0 < len(sp) <= frames_mod.SPIKE_CAP and len(n3["rq"]) == 288
            assert (sp[:, 0] < 214).all() and (sp[:, 2] <= n3["span"]).all()
            assert len(json.dumps(f[-1])) < 3_000                      # small frames
            assert cl.reward("b-1", 0.2, followed=1)                    # dopamine for that decision
            st = await cl.call("status")
            assert st["n_learn"] == 1 and st["n_decisions"] == 1
            n0 = len(frames)
            await asyncio.sleep(L.IDLE_EVERY_S + 1.0)                   # between decisions: an idle pulse
            assert any(x.get("phase") == "idle" for x in frames[n0:])
            assert cl.state() == "live"
            cl.proc.kill()                                              # the child dies: the vote goes on without it
            await cl.proc.wait()
            await asyncio.sleep(0.2)
            assert "offline" in (await cl.decide(["a", "b"]))["why"]
        finally:
            await cl.stop()
        assert (tmp_path / "spiking" / "live_weights.npz").exists()
    run(go())


def test_a_slow_child_is_skipped_after_the_timeout_and_never_blocks_the_loop(tmp_path):
    """A child that never answers: decide() gives up after `timeout`; the event loop keeps ticking meanwhile (the
    50 ms brain tick is never delayed by the spiking network)."""
    async def go():
        cl = L.LiveClient(tmp_path, timeout=0.5, python=sys.executable)
        cl.proc = await asyncio.create_subprocess_exec(sys.executable, "-c", "import sys,time\nfor l in sys.stdin: time.sleep(60)",
                                                       stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        cl._reader_task = asyncio.get_running_loop().create_task(cl._read(cl.proc))
        cl.ready = True
        ticks, stop = [], False

        async def ticker():
            while not stop:
                ticks.append(time.perf_counter())
                await asyncio.sleep(0.05)
        tk = asyncio.get_running_loop().create_task(ticker())
        t0 = time.perf_counter()
        ans = await cl.decide(["a", "b", "c"])
        dt = time.perf_counter() - t0
        stop = True
        await tk
        cl.proc.kill()
        await cl.proc.wait()
        assert "slower than 0.5 s" in ans["why"] and 0.45 < dt < 1.0 and cl.slow == 1
        gaps = np.diff(ticks)
        assert len(ticks) >= 8 and gaps.max() < 0.15
    run(go())


# --- the decision backend: GPU first, CPU second, rate model last; the day's decisions log -------------------------
# --- with torch: the same synapses as net.py, and the night's replay ------------------------------------------------
def test_live_net_has_the_synapses_of_net_py():
    torch = pytest.importorskip("torch")
    from sub01_brain.spiking.net import SpikingNet
    cfg = Config(n_neurons=SMALL)
    a, b = SpikingNet(cfg, "cpu"), L.LiveNet(cfg)
    assert a.n == b.n and a.D == b.D and a.n_syn == b.n_syn
    assert np.array_equal(a.dst.numpy(), b.dst) and np.array_equal(a.w.numpy(), b.w)
    assert np.array_equal(a.rowptr.numpy(), b.rowptr) and np.array_equal(a.src.numpy(), b.src)
    assert np.array_equal(a.delay.numpy().astype(np.int64) * a.n + a.dst.numpy(), b.slot_off)
    from sub01_brain.spiking.memory import MemorySystem
    ch = L.Chooser(b)
    assert np.array_equal(ch.cue("bread"), np.intersect1d(MemorySystem(a, frac=L.WORD_FRAC).word_neurons("bread"),
                                                          ch.cue_space))
    del torch

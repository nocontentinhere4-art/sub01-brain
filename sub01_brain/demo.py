"""Five-minute quickstart: the rate model for a minute of simulated time, then a small spiking network that decides.

    python -m sub01_brain.demo                      # ~20-40 s on one CPU core, numpy + scipy only
    python -m sub01_brain.demo --seconds 120 --neurons 20000
    python -m sub01_brain.demo --quick              # the tests' version (a few seconds)

1. brain_sim.Brain: 214 regions, delayed Stuart-Landau oscillators at ~10 Hz on the real connectome, the fitted slow
   layer underneath. Runs `--seconds` of simulated time, a stimulus to the visual and reward groups halfway, and prints
   the mean amplitude per network before and after, plus the global synchrony.
2. spiking.live.LiveBrain: a numpy LIF network (`--neurons`) on the same wiring. Prints its background rates per group,
   then a few decisions among labelled options with a reward for one of them: the pick, the pool rates, the frozen
   twin's pick and how much the cue -> striatum weights moved.
Everything printed is simulated activity; none of it is a thought or a feeling.
"""
import argparse
import time

import numpy as np


def rate_model(seconds=60.0, seed=0, say=print):
    from sub01_brain.brain_sim import Brain
    t0 = time.time()
    b = Brain(seed=seed)
    say(f"[rate model] {b.n} regions, max delay {b.hist - 1} ms, slow layer {'on' if b.slow_on else 'off'}, "
        f"built in {time.time() - t0:.1f} s")
    half = seconds / 2
    say(f"[rate model] {half:.0f} s of rest ...")
    base_sig = b.run(half)                                      # (T, n) real part, sampled every 10 ms
    s0 = b.state()
    b.stimulate("visual", 8.0)
    b.stimulate("reward", 12.0)
    say(f"[rate model] stimulus: visual +8, reward +12 (decays with a 2 s time constant); {half:.0f} s more ...")
    after_sig = b.run(half)
    s1 = b.state()
    say(f"[rate model] signal shape {base_sig.shape} + {after_sig.shape} (10 ms samples x regions), "
        f"wall {time.time() - t0:.1f} s for {seconds:.0f} s of simulated time")
    say(f"  {'network':12s} {'before':>8s} {'after':>8s}   (mean oscillation amplitude per region group)")
    for k in s0:
        if k != "sync":
            say(f"  {k:12s} {s0[k]:8.3f} {s1[k]:8.3f}")
    say(f"  {'sync':12s} {s0['sync']:8.3f} {s1['sync']:8.3f}   (phase synchrony across regions, 0..1)")
    return b, s0, s1


def spiking_network(n_neurons=10_000, trials=6, say=print):
    from sub01_brain.spiking import live as L
    t0 = time.time()
    lb = L.LiveBrain(n_neurons, weights=None, twin=True, log=say)
    st = lb.status()
    say(f"[spiking] {st['n_neurons']:,} LIF neurons, {st['n_synapses']:,} synapses ({st['n_plastic']} plastic cue -> "
        f"striatum), decision threshold {st['threshold_hz']} Hz, built + calibrated in {time.time() - t0:.1f} s")
    net = lb.net
    net.drive()
    c0 = net.count.copy()
    net.run(1000)                                               # 1 s of background activity
    rr = np.add.reduceat(net.count - c0, net.off) / net.size   # Hz per region
    say(f"[spiking] 1 s of background: mean rate {float((net.count - c0).sum()) / net.n:.2f} Hz; per group: " +
        ", ".join(f"{g} {float((rr[ix] * net.size[ix]).sum() / net.size[ix].sum()):.1f}"
                  for g, ix in net.reg.groups.items() if ix and g in ("visual", "somatomotor", "reward", "memory", "language")))
    labels = ["read about bread", "tokyo parks", "jazz records"]
    say(f"[spiking] {trials} decisions among {labels}; option 0 is rewarded (+0.5) when followed, the others -0.5")
    for i in range(trials):
        d = lb.decide(labels, did=i)
        delta = 0.5 if d["pick"] == 0 else -0.5
        r = lb.learn(i, d["pick"], delta)
        say(f"  {i + 1}. pick {d['pick']} ({labels[d['pick']]}), pool rates {d['pool_rates']} Hz, {d['sim_ms']:.0f} ms"
            f"{' (timeout)' if d['timeout'] else ''}; frozen twin picked {d['twin_pick']}; dopamine {r['da']:+.2f}, "
            f"eta {r['eta']} mV, |dw| mean {r['dw_abs_mean']} mV")
    say(f"[spiking] wall {time.time() - t0:.1f} s. Learned weights live in LiveBrain.dw (save with weights=<path>).")
    return lb


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seconds", type=float, default=60.0, help="simulated seconds of the rate model (default 60)")
    ap.add_argument("--neurons", type=int, default=10_000, help="size of the numpy spiking network (default 10000)")
    ap.add_argument("--trials", type=int, default=6, help="decisions of the spiking network (default 6)")
    ap.add_argument("--quick", action="store_true", help="a few seconds in all (the tests)")
    a = ap.parse_args(argv)
    if a.quick:
        a.seconds, a.neurons, a.trials = 2.0, 3000, 2
    print("sub01-brain demo: a model of brain activity, not a mind. Everything below is simulated.")
    rate_model(a.seconds)
    spiking_network(a.neurons, a.trials)


if __name__ == "__main__":
    main()

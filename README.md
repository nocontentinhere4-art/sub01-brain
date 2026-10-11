# sub01-brain

**The brain model of SUB-01, a fictional simulated character. A model of brain activity, not a mind.**

Two models run on one real connectome: 214 brain regions and the nerve-fibre bundles between them, traced from the
public MRI scans of one anonymous person ([data/DATA.md](data/DATA.md)).

- **A rate model** (`brain_sim.Brain`): one Stuart-Landau (Hopf) oscillator per region at ~10 Hz, coupled through the
  connectome with conduction delays from the fibre lengths. Underneath, a **slow layer** (`twin/hopf.SlowLayer`): a
  BOLD-band Hopf model fitted on half of the person's resting-state recordings and scored on the other half, which
  gives the fast layer its slow waxing and waning. On unseen sessions it matches the recorded co-activity pattern at
  r = 0.21; randomised wiring reaches 0.16-0.17 ([docs/real_wiring_report.md](docs/real_wiring_report.md)).
- **Spiking networks** on the same wiring: leaky integrate-and-fire populations per region (size from the region's
  volume), long-range synapses drawn from the streamline counts with delays from the fibre lengths, dopamine-gated
  plasticity. In **numpy** (`spiking/live.py`, 20k-500k neurons on one CPU core: the "day network" that chooses among
  labelled options and learns from reward) and in **PyTorch** (`spiking/net.py`, up to 1M neurons on a GPU, with a
  hippocampal memory, a Pong task and a K-armed choice task).
- A minimal **body** (heart rate, breathing, glucose, hunger) and **neuromodulators** with receptor maps that turn
  dopamine / serotonin / noradrenaline / acetylcholine levels into a per-region gain (`twin/`).

In the parent project this model drives a character who lives in a 3D room: it decides when he sleeps, what he clicks
on and what he replays at night. None of that is here; this is the brain alone, so people can run it, study it, combine
it with other things and make it learn.

**Honest framing.** It simulates large-scale activity rhythms and spikes. It does not understand, feel or think; it has
no thoughts, memories or dreams of anyone; it is not conscious and not alive. "It decides" means a race between
striatal pools (`spiking/choice.py`); "it learns" means weights change under a reward signal; "it remembers" means a
pattern can be completed from half its cue. The character is fiction. The real person whose scans were used is
anonymous and stays so: this repository names the dataset and cites its paper because the data licence asks for that,
and says nothing else about them ([NOTICE.md](NOTICE.md)). Every number here is about the model, never about anyone's
brain or health.

## What is in the repository

```
sub01_brain/                 the package (MIT)
  brain_sim.py               Brain: the rate model (fast layer) + the slow layer underneath
  real_baseline.py           RealBaseline: the recorded resting-state runs as a slow drive (optional, the old default)
  snapshot.py                save / restore a Brain's dynamic state bit for bit
  demo.py                    the quickstart:  python -m sub01_brain.demo
  paths.py                   where the data files are (SUB01_BRAIN_DATA overrides)
  spiking/
    config.py                Config: every parameter, config_hash() guards learned-weight files
    regions.py wiring.py     the atlas regions; populations, synapses and word -> neuron hashing (numpy, shared by both nets)
    live.py                  LiveNet / LiveBrain: the numpy network that decides and learns; the JSON-lines protocol; LiveClient
    net.py plasticity.py     SpikingNet (torch): the network; three-factor STDP, Hebbian memory rule, homeostasis, weight files
    memory.py pong.py        MemorySystem: words -> patterns -> hippocampal assemblies -> REM replay; the Pong task
    choice.py                ChoiceTask / LiveChooser: the K-armed choice task, read-outs, the live decision race
    session.py               python -m sub01_brain.spiking.session: a full phased session of the torch network
    frames.py words.py       compact activity frames for a display; the word tokeniser
  twin/
    hopf.py                  SlowLayer (numpy) and the fitting maths (torch): Deco 2017 Hopf model, linearisation, EC
    body.py neurochem.py     Body; Neuromodulators + receptor-weighted region gain
data/                        23 MB, licensed per bundle: mri/ (CC BY-SA 4.0), receptors/ (CC BY 4.0)  -> data/DATA.md
pipeline/                    the scripts that built data/ from the raw MRI (needs the MRI stack)  -> pipeline/README.md
docs/                        the reports, numbers included: real wiring, spiking, choice, the day network, body, neurochem
tests/                       python -m pytest -q  (torch tests skip without torch)
```

## Install

Python 3.10+, CPU only, two dependencies:

```bash
git clone <this repo> && cd sub01-brain
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt            # numpy, scipy
python -m sub01_brain.demo                 # ~10-40 s
```

Optional: `pip install -r requirements-torch.txt` (or `pip install torch --index-url https://download.pytorch.org/whl/cpu`)
for the PyTorch network, the memory / Pong / choice-task code and the slow-layer fitting; `pip install -e .` to import
the package from anywhere (the data stays in `data/`; set `SUB01_BRAIN_DATA=/path/to/data` if the checkout moves);
`requirements-pipeline.txt` to rebuild the data from the raw MRI.

Set `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`: the matrices are 214 x 214, more BLAS threads only spin.

## Five-minute quickstart

```bash
python -m sub01_brain.demo                       # 60 s of the rate model, then a 10k-neuron spiking network
python -m sub01_brain.demo --seconds 120 --neurons 20000 --trials 10
```

What it prints (one CPU core, 10 s wall in all):

```
[rate model] 214 regions, max delay 60 ms, slow layer on, built in 0.9 s
[rate model] 30 s of rest ...
[rate model] stimulus: visual +8, reward +12 (decays with a 2 s time constant); 30 s more ...
[rate model] signal shape (3000, 214) + (3000, 214) (10 ms samples x regions), wall 6.8 s for 60 s of simulated time
  network        before    after   (mean oscillation amplitude per region group)
  visual          0.129    0.114
  somatomotor     0.142    0.172
  ...
  sync            0.098    0.104   (phase synchrony across regions, 0..1)
[spiking] 10,000 LIF neurons, 1,009,600 synapses (372 plastic cue -> striatum), decision threshold 9.496 Hz, built + calibrated in 1.3 s
[spiking] 1 s of background: mean rate 5.98 Hz; per group: visual 5.9, somatomotor 6.1, reward 5.9, memory 4.1, language 6.2
[spiking] 6 decisions among ['read about bread', 'tokyo parks', 'jazz records']; option 0 is rewarded (+0.5) when followed, the others -0.5
  1. pick 1 (tokyo parks), pool rates [5.585, 5.968, 5.63] Hz, 250 ms (timeout); frozen twin picked 2; dopamine -1.00, ...
  ...
  6. pick 0 (read about bread), pool rates [11.321, 9.206, 5.926] Hz, 50 ms; frozen twin picked 1; dopamine +1.00, ...
```

(The "after" amplitudes of the stimulated groups depend on where the stimulus lands in the slow layer's fluctuation;
over 6 s of simulation they rise, over a 30 s window they are averaged out. Six decisions are an illustration, not a
learning curve: the measured curves are in `docs/spiking/live_cpu.md` and `docs/spiking/choice.md`.)

The same network as a decision server, one JSON object per line on stdin / stdout (the protocol below):

```bash
printf '{"type":"decide","id":"d1","options":["read about bread","tokyo parks"],"kind":"browse","deadline_ms":2000}\n{"type":"reward","id":"d1","value":0.4,"followed":0}\n{"type":"stop"}\n' \
  | python -m sub01_brain.spiking.live --data-dir ./state --neurons 20000
```

## The public interfaces

### The rate model: `brain_sim.Brain`

```python
from sub01_brain.brain_sim import Brain, GROUPS
b = Brain(seed=0)                 # Brain(path=paths.CONNECTOME, f_hz=10, a=-5, g=5, velocity_m_s=6, noise=0.5, dt=1e-3, slow=True)
b.names, b.centroids, b.W         # 214 region names (atlas order), centroids (mm), normalised log-weights
b.group_idx["visual"]             # region indices per group: GROUPS keys + "language"
b.stimulate("reward", 12.0)       # stimulus in: adds drive to a group; decays with a 2 s time constant
b.drive[:] = z                    # stimulus in: a per-region excitability vector you control (not decayed)
b.neuromod[:] = gain - 1          # stimulus in: per-region excitability from neuromodulators (twin.neurochem)
b.set_rhythm(2.0, coupling=1.4, noise=0.3)   # the global rhythm: frequency, coupling x baseline, noise (sleep stages)
z = b.step(k=50)                  # k ms; returns the complex state (n,): amplitude = |z|, phase = angle(z)
x = b.run(seconds=10, every=10)   # activity out: real part sampled every `every` ms, shape (T, n), EEG-like
b.state()                         # activity out: {"visual": mean amplitude, ..., "sync": phase synchrony 0..1}
c = b.clone()                     # an independent copy sharing the wiring: try a stimulus without touching the live brain
b.use_slow_layer(False)           # switch the slow layer off (e.g. to replay a recorded run through b.drive)
```

Time is `dt` = 1 ms per step. Everything is deterministic given `seed`. **Snapshot:** `sub01_brain.snapshot.save(b, path)`
/ `snapshot.load(path)` store and restore the ring buffer, drives, rhythm, slow-layer state and random streams; a
restored brain continues identically (`tests/test_snapshot.py`).

**The slow layer** on its own: `twin.hopf.SlowLayer(seed=0, which="wiring"|"ec").advance(dt)` returns the z-scored
BOLD-band signal per region; `status()` says what it is and how well it fits held-out data. **The recorded runs** on
their own: `real_baseline.RealBaseline(b.names).advance(dt)` plays the person's resting-state time series back,
interpolated; `Brain.drive` is where it used to go.

### The numpy spiking network: `spiking.live`

```python
from sub01_brain.spiking import live as L
lb = L.LiveBrain(n_neurons=20_000, weights="state/live_weights.npz", twin=True)   # built + calibrated in ~2 s at 20k
lb.status()                                        # neurons, synapses, plastic synapses, threshold, learned decisions, ...
d = lb.decide(["read about bread", "tokyo parks", "jazz records"], did="d1")
#   -> {"pick", "pool_rates" (Hz per option), "sim_ms", "timeout", "twin_pick", "twin_rates", "threshold_hz", "cpu_ms"}
lb.learn("d1", followed=0, delta=0.4)              # dopamine for that decision: a reward-prediction error in about -0.5..0.5
net = lb.net                                       # LiveNet: .run(ms), .drive(ids, amp_mV), .count (spikes per neuron),
                                                   #   .off / .size (population layout), .reg.groups, .w / .src / .dst (synapses)
```

Labels are any text: their content words are hashed to fixed neurons of the visual and language parcels (the same word
lands on the same neurons in every label and every session), the striatal neurons are split into one pool per option,
and the first pool whose rate crosses the calibrated threshold wins (forced choice at 250 ms). The frozen twin takes
the same decisions with no learning, as the control. `L.synthetic(lb, trials=100)` runs the benchmark of
`docs/spiking/live_cpu.md`. `LiveClient(data_dir, n_neurons)` runs the network as a child process from asyncio and
never waits longer than its timeout.

### The PyTorch spiking network: `spiking.net` and friends (needs torch)

```python
from sub01_brain.spiking.config import Config
from sub01_brain.spiking.net import SpikingNet
from sub01_brain.spiking.memory import MemorySystem, sleep_block
from sub01_brain.spiking.choice import ChoiceTask, LiveChooser, experiment
from sub01_brain.spiking.pong import Pong
from sub01_brain.real_baseline import RealBaseline
net = SpikingNet(Config(n_neurons=20_000), device="cpu")      # "cuda" for 1M neurons (5.7 GB)
net.attach_baseline(RealBaseline(net.reg.names))              # the recorded resting-state activity as per-region drive
net.set_region_drive("stim", vec_mV)                          # stimulus in: a (214,) vector on the regions' mean input
net.set_neuron_drive("pattern", idx, amp_mV)                  # stimulus in: a set of neurons
snap = net.snapshot(); net.run(1000)                          # 1 s
net.region_rates_since(snap)                                  # activity out: Hz per region (214,), atlas order
net.group_rates(net.region_rates_since(snap))                 # activity out: Hz per group
net.plast.dopamine(1.0)                                       # reward: three-factor STDP on the dopamine-gated synapses
mem = MemorySystem(net); mem.encode("warm bread in the quiet morning", day="d1"); mem.test("d1", lures=8)
sleep_block(net, mem, minutes=1)                              # NREM / REM with replay
experiment(net, trials=160, k=4)                              # the K-armed choice task with its controls
net.plast.save("weights.npz"); net.plast.load("weights.npz", elapsed_days=1.0)   # learned dw only; w0 is never stored
```

`python -m sub01_brain.spiking.session` runs a phased session from a JSON config in `SUB01_SESSION` (phases: bench,
rates, delays, encode, pong_train, pong_exam, choice_train, choice_exam, memory_test, sleep, live_decide, ...), writing
`status.json` / `results.json` / `weights.npz` to `SUB01_OUT`; the websocket link to a server is optional and off
without `SUB01_SERVER_URL`. The numpy and torch networks build the **same synapses** from the same `Config` and seed
(`spiking/wiring.py`), checked bit for bit in `tests/test_spiking_live.py`.

### Body and neuromodulators: `twin.body`, `twin.neurochem`

```python
from sub01_brain.twin.body import Body
from sub01_brain.twin.neurochem import Neuromodulators
body = Body(); body.eat(carbs_g=40); body.update(dt_sim=30.0, levels=nm.levels, amygdala=0.0, stage="AWAKE")
body.vitals()                      # {"hr_bpm", "resp_per_min", "glucose_mg_dl", ...};  body.hunger (0..1)
body.intero_drive()                # {"insula": amount, ...} -> brain.stimulate(group, amount)
nm = Neuromodulators(); nm.burst(0.5); nm.update(dt=1.0, sleep_levels=None)
nm.levels                          # {"DA", "5HT", "NE", "ACh"}, 1.0 = resting wake
brain.neuromod = nm.region_gain() - 1.0     # per-region gain from receptor maps -> the rate model's excitability
```

Both have `to_dict()` / `from_dict()` for persistence.

## How to make it learn

Learning lives in `dw`, the learned component of each plastic synapse; the connectome-derived weights `w0` are never
changed and never stored. Three places:

1. **The day network's choice learning** (`spiking/live.py`, numpy): `decide()` tags the cue -> striatum synapses that
   were active (eligibility: pre = cue rate, post = +1 on the followed option's pool, -1/(K-1) on the other offered
   pools); `learn(id, followed, delta)` applies `dw += eta * da * pre * post` with `da = clip(2 * delta, -1, 1)` and a
   learning rate that decays with the number of rewards (`ETA / (1 + n / 50)`, floor 0.25). Only 754 of 2 M synapses
   are plastic at 20k neurons. Weights persist in `<data-dir>/spiking/live_weights.npz` (atomic write, checked against
   `Config.config_hash()`, a torn file is kept aside). Any reward signal in about -0.5..0.5 works: the parent project
   uses the prediction error of a taste model; `L.synthetic` uses a bandit. Measured: 0.57-0.65 correct vs 0.28-0.32
   for the frozen twin on a synthetic stream ([docs/spiking/live_cpu.md](docs/spiking/live_cpu.md)).
2. **Three-factor STDP x dopamine** (`spiking/plasticity.py`, torch): STDP eligibility traces (1 s) on the E -> E
   synapses onto the `da_groups` (somatomotor by default), converted into weight change by phasic dopamine
   (`plast.dopamine(amount)`); homeostasis keeps rates near 5 Hz. Used by Pong (`spiking/pong.py`, which the 1M
   network did **not** learn: 17.5 % vs 25 % for the no-plasticity control, [docs/spiking_report.md](docs/spiking_report.md))
   and by the choice task (`spiking/choice.py`, which it did: criterion in 20-61 trials at 20k, 84 at 1M,
   [docs/spiking/choice.md](docs/spiking/choice.md)).
3. **Hebbian memory** (`spiking/memory.py`, torch): words -> sparse patterns -> a fast Hebbian rate rule binds
   hippocampal assemblies (CA3-like collaterals); a recall test completes a pattern from half its words against lures;
   REM replay (`sleep_block`) reinstates assemblies and slowly strengthens cortical synapses. Learned weights decay
   between sessions (hippocampal in days, cortical in weeks: `plast.load(path, elapsed_days)`).

All of it is reported with its controls (frozen twin, random chooser, no-plasticity network). Keep it that way.

## How to combine it with other models

The contract is **stimulus in / activity out**, on the 214-region atlas order of `data/mri/atlas_names.json`:

| | in | out |
|---|---|---|
| rate model | `Brain.stimulate(group, amount)`; `Brain.drive` (214,) excitability; `Brain.neuromod` (214,); `set_rhythm(f, coupling, noise)` | `Brain.run()` (T, 214) real signal; `Brain.step()` complex state; `Brain.state()` per-group amplitude + synchrony |
| numpy spiking | option labels (any text, 2-6); reward `delta` per decision; `LiveNet.drive(ids, mV)` | pick, pool rates (Hz), decision time; `LiveNet.count` spikes per neuron; frames (`spiking/frames.py`: per-region rates one byte each + a spike sample) |
| torch spiking | `set_region_drive(name, (214,) mV)`, `set_neuron_drive(name, ids, mV)`, `plast.dopamine(x)`, `attach_baseline(obj with .advance(dt) -> (214,))` | `region_rates_since(snap)` (214,) Hz, `group_rates`, `pop_raster()` spikes, `plast.stats()` |
| body / neurochem | `Body.eat`, `Body.update(levels, amygdala, stage)`; `Neuromodulators.burst / update(sleep_levels)` | `vitals()`, `hunger`, `intero_drive()`; `levels`, `region_gain()` (214,) |

Across processes, the day network speaks JSON lines (`spiking/live.py` docstring): `decide` -> `decision`,
`reward` -> `rewarded`, `status`, `burst`, `stop`, plus unsolicited `{"type": "spiking", ...}` activity frames; the
torch session answers the same `decide` / `reward` messages over its optional websocket. A sleep model sets the rhythm
(`set_rhythm`) and the stage the body and neuromodulators see; a language model's words go in as `stimulate("language")`
or as memory items; a sensor goes in as a region drive; whatever reads `run()` or the region rates gets activity out.
Anything that keeps the atlas order and the units (mV on `mu`, Hz out) plugs in. Swapping the connectome itself is
`Brain(path=...)` / `Regions(connectome=..., volumes=...)` ([data/DATA.md](data/DATA.md), "Rebuilding or swapping").

## Growing the network

**TODO: neurogenesis.** Another branch is implementing growth of the spiking network: adding neurons and synapses while
it runs, keeping `Config.config_hash()` and the learned-weight files coherent, and measuring what growth does to the
rates, the memory capacity and the choice task. This section will describe the interface (where new neurons go, how
their synapses are drawn, how `dw` survives a resize) and the results. Until then, the network's size is fixed at
construction (`Config.n_neurons`), and the two nets stay identical for a given `(Config, seed)`.

## What this is not

- **Not a mind.** No thoughts, understanding, feelings, intentions or awareness; no claim of consciousness. The
  perturbational complexity of the rate model was measured and is far below the clinical cut-off (0.18 awake vs 0.31).
- **Not the person.** It is built on one anonymous person's wiring and the statistics of their resting-state
  recordings; it has none of their memories, thoughts or dreams, which MRI cannot read. It must never be presented as
  that person, and nothing in it or around it may identify them.
- **Not a whole-brain simulation.** 214 regions; a rate model with one oscillator per region; spiking populations with
  100 synapses per neuron (not a balanced large-K network); no layers, no cell types beyond E/I, no glia, no
  neuromodulator chemistry beyond gain; receptor maps are group data from other people and cover the cortex only.
- **Not a strong result.** The wiring-only slow layer beats randomised wiring by about 0.04-0.07 of r and is only
  borderline against geometry-preserving nulls (p = 0.059); the 1M-neuron network did not learn Pong; the choice task
  is a 4-armed bandit with fixed cues. The reports keep every negative number.
- **Not medical, not financial.** Nothing here is advice of any kind.

## Tests

```bash
pip install pytest
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q      # 71 passed, 10 skipped without torch, ~70 s
```

`tests/test_brain_step.py` (the sparse step equals the dense reference to 1e-9), `test_real_wiring.py` (slow-layer
maths, split, public API, no-torch run), `test_snapshot.py`, `test_spiking_live.py` (cues, pools, learning vs the twin,
weights file, child process), `test_spiking_choice.py` / `test_spiking_readout.py` (task logic; network parts need
torch), `test_spiking_model.py` (torch: rates, delays, STDP bounds, memory, Pong), `test_neurochem.py`, `test_body.py`,
`test_data_files.py` (the bundles agree), `test_demo.py`. CI (`.github/workflows/test.yml`) runs the CPU suite on
Python 3.10 and 3.12 and the torch suite on a CPU wheel.

## Data, attribution, licence

- Data: [data/DATA.md](data/DATA.md) (what each file is, how it was built, its licence). The MRI-derived bundle
  `data/mri/` is CC BY-SA 4.0; the receptor bundle `data/receptors/` is CC BY 4.0. Nothing is larger than 6 MB.
- Attribution: [NOTICE.md](NOTICE.md): the dataset acknowledgement and citation the data record requires, the atlases
  (Schaefer-200, Harvard-Oxford, ICBM), the receptor source, the models re-implemented.
- Code: MIT, © 2026 SUB-01 project ([LICENSE](LICENSE)). Contributing: [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

SUB-01 is an art and science project. This repository is a model of large-scale brain activity, not a mind, and not
the scanned person; the character it drives elsewhere is fiction. Nothing here is medical or financial advice.

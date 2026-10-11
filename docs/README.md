# Reports

These are the parent project's reports on the model, copied as they were written (2026-09/10), including the
results that did not work. Paths in them (`out/…`, `twin/data/…`, `analysis/…`, `brain_vote.py`, `live_server.py`,
GPU "pods", a "page" or "card") refer to the parent project's layout and runtime; in this repository the data is under
`data/mri/` and `data/receptors/`, the build scripts under `pipeline/`, and the site around the model is not included.
Every number is a statement about the model, never about anyone's brain or health.

| report | what |
|---|---|
| [real_wiring_report.md](real_wiring_report.md) | Does the connectome do the work? The slow Hopf layer fitted on half of the recordings, scored on the other half, against 100 geometry- and 100 strength-preserving randomised wirings (figures in `real_wiring/`). Headline: wiring-only model r = 0.21 on unseen sessions vs 0.16-0.17 for randomised wiring (p = 0.01 strength, 0.059 geometry). |
| [spiking_report.md](spiking_report.md) | The spiking network: architecture, rates, delays, memory test, Pong (the 1M-neuron network did **not** learn Pong: 17.5 % vs 25 % for the no-plasticity control). |
| [spiking/choice.md](spiking/choice.md) | The K-armed choice task: the network learns from dopamine alone to pick the rewarded cue (20k CPU: criterion in 20-61 trials; 1M GPU: 84), the read-outs that scale, the live learning benchmark, and the drift that the decaying learning rate fixes. |
| [spiking/live_cpu.md](spiking/live_cpu.md) | The numpy day network (`spiking/live.py`): design, the decision protocol, cost per decision, learning on a synthetic stream against its frozen twin (0.57-0.65 correct vs 0.28-0.32), and "reading it honestly". |
| [twin/neurochem.md](twin/neurochem.md) | Neuromodulators and receptor-weighted gain: equations, sources, what is not realistic (no D2 map; subcortical fallback). |
| [twin/body.md](twin/body.md) | The minimal body: heart rate, breathing, glucose, hunger; textbook constants, nothing fitted to the person. |

The parent project's sleep engine (a Phillips & Robinson 2007 circuit) drives the rhythm changes these reports mention
(`set_rhythm`, NREM / REM); it is part of the character's life, not of this package, so its report is not here.

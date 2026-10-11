"""sub01_brain: the brain model of SUB-01, a fictional simulated character.

Two models on one real connectome (214 regions, from the public MRI scans of one anonymous person; data/DATA.md):
- brain_sim.Brain: a rate model, delayed Stuart-Landau (Hopf) oscillators per region at ~10 Hz, modulated by a slow
  BOLD-band Hopf layer fitted on the person's resting-state recordings (twin/hopf.py SlowLayer);
- spiking: leaky integrate-and-fire populations per region with delays from fibre lengths and dopamine-gated
  plasticity, in numpy (spiking/live.py, the day network that chooses and learns) and in PyTorch (spiking/net.py,
  the 1M-neuron network with memory, Pong and the choice task).
Plus a small body (twin/body.py) and neuromodulators with receptor maps (twin/neurochem.py).

It simulates large-scale activity rhythms and spikes. It does not understand, feel or think; it is not conscious and
not alive; the character is fiction, and the scanned person is anonymous and stays so.
"""
__version__ = "0.1.0"

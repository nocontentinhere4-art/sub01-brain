"""The quickstart runs end to end on numpy alone (the --quick sizes), and prints what the README promises.

    python -m pytest tests/test_demo.py -q
"""
from sub01_brain import demo


def test_quick_demo_runs(capsys):
    demo.main(["--quick"])
    out = capsys.readouterr().out
    assert "[rate model] 214 regions" in out and "[spiking] 3,000 LIF neurons" in out
    assert "not a mind" in out
    assert out.count("pick ") == 2                            # two decisions
    assert "sync" in out and "reward" in out


def test_rate_model_reacts_to_the_stimulus():
    _, s0, s1 = demo.rate_model(seconds=6.0, say=lambda *a: None)
    assert set(s0) == set(s1) and "visual" in s0 and "sync" in s0
    assert s1["visual"] > s0["visual"] and s1["reward"] > s0["reward"]   # the stimulated groups oscillate more

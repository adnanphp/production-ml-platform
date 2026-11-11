from src.platform.serving.app import create_app
from src.platform.serving.model_loader import ConstantModel, ModelSlot
from src.platform.serving.router import Router


def _router_with_weight(w: float, n: int = 2000):
    inc = ModelSlot("incumbent", ConstantModel(0.1, "inc"))
    cand = ModelSlot("candidate", ConstantModel(0.9, "cand"))
    r = Router(incumbent=inc, candidate=cand, incumbent_weight=w)
    outs = [r.predict([0.0])["model"] for _ in range(n)]
    return outs


def test_90_10_split_is_approximately_correct():
    outs = _router_with_weight(0.90, n=2000)
    inc_frac = outs.count("incumbent") / len(outs)
    # allow 4 percentage points of sampling noise at n=2000
    assert abs(inc_frac - 0.90) < 0.04, f"incumbent fraction was {inc_frac}"


def test_all_to_incumbent_when_weight_is_1():
    outs = _router_with_weight(1.0, n=100)
    assert set(outs) == {"incumbent"}


def test_all_to_candidate_when_weight_is_0():
    outs = _router_with_weight(0.0, n=100)
    assert set(outs) == {"candidate"}

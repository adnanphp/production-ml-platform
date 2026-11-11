from src.platform.rollback import perform_rollback
from src.platform.rollback.triggers import TriggerResult
from src.platform.serving.model_loader import ConstantModel, ModelSlot


def test_rollback_duration_is_positive():
    slot = ModelSlot("candidate", ConstantModel(0.9, "candidate-bad"))
    trigger = TriggerResult(fires=True, reasons=["test"])
    result = perform_rollback(
        slot=slot,
        incumbent_model=ConstantModel(0.5, "incumbent-good"),
        incumbent_metrics={"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0},
        trigger=trigger,
    )
    assert result.performed
    assert result.duration_ms >= 0.0
    # Sanity: a swap should be sub-millisecond-ish; allow generous bound
    assert result.duration_ms < 1000.0


def test_no_trigger_returns_noop():
    slot = ModelSlot("candidate", ConstantModel(0.9, "candidate-ok"))
    trigger = TriggerResult(fires=False, reasons=[])
    result = perform_rollback(
        slot=slot,
        incumbent_model=ConstantModel(0.5, "incumbent"),
        incumbent_metrics={"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0},
        trigger=trigger,
    )
    assert not result.performed
    assert slot.get().model_hash == "candidate-ok"    # nothing swapped

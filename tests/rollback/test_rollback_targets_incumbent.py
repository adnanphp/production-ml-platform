from src.platform.rollback import perform_rollback
from src.platform.rollback.triggers import TriggerResult
from src.platform.serving.model_loader import ConstantModel, ModelSlot


def test_rollback_swaps_to_incumbent_hash():
    # Slot currently holds a "candidate" that we want to roll back away from.
    bad_candidate = ConstantModel(p=0.9, model_hash="candidate-bad")
    slot = ModelSlot("candidate", bad_candidate)

    good_incumbent = ConstantModel(p=0.5, model_hash="incumbent-good")
    trigger = TriggerResult(fires=True, reasons=["drift detector fired"])

    result = perform_rollback(
        slot=slot,
        incumbent_model=good_incumbent,
        incumbent_metrics={"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0},
        trigger=trigger,
    )

    assert result.performed
    assert result.from_hash == "candidate-bad"
    assert result.to_hash == "incumbent-good"
    # slot actually swapped
    assert slot.get().model_hash == "incumbent-good"
    # prediction now comes from incumbent
    assert slot.get().predict_proba([0.0]) == 0.5

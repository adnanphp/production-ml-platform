"""Evaluation gate. Implementation lands in Phase 1."""
from dataclasses import dataclass


@dataclass
class Decision:
    status: str      # "PROMOTE" | "REJECT"
    reason: str


def evaluate_candidate(candidate: dict, incumbent: dict | None) -> Decision:
    raise NotImplementedError("Phase 1: implement the promotion rule from DESIGN.md")

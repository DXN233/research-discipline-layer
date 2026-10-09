"""Sentinel validity: every sentinel must fire on known-bad inputs (control reversal).

A sentinel that certifies runs by matching surface features (a magic phrase, a
status string) will be satisfied by the very failure it was meant to catch.
Invalidated sentinels force a fallback to independent recomputation.
"""
from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class SentinelReport:
    name: str
    valid: bool
    failures: List[str] = field(default_factory=list)


def control_reversal(name: str, sentinel_trusts: Callable[[str], bool],
                     known_bad: List[str]) -> SentinelReport:
    failures = [s for s in known_bad if sentinel_trusts(s)]
    return SentinelReport(
        name=name,
        valid=not failures,
        failures=[f"trusted known-bad sample: {s[:70]!r}" for s in failures],
    )


def phrase_sentinel(phrase: str) -> Callable[[str], bool]:
    """Example sentinel: trusts any report containing the phrase. Defeated trivially."""

    def trusts(report: str) -> bool:
        return phrase in report

    return trusts

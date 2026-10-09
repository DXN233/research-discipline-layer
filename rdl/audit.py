"""Final audit gate: claimed numbers must match numbers recomputed from artifacts."""
from typing import Dict, List

from .ledger import Entry


def cross_check(entries: List[Entry], recomputed: Dict[str, float],
                tol: float = 1e-9) -> List[str]:
    violations = []
    for e in entries:
        for key, claimed in (e.numbers or {}).items():
            actual = recomputed.get(key)
            if actual is None:
                violations.append(
                    f"entry {e.id}: number '{key}' has no artifact counterpart"
                )
            elif abs(claimed - actual) > tol:
                violations.append(
                    f"entry {e.id}: '{key}' claimed {claimed}, "
                    f"artifacts recompute to {actual} (claim: '{e.claim}')"
                )
    return violations


def verdict(alarm_count: int) -> str:
    return "QUARANTINED" if alarm_count else "PASS"

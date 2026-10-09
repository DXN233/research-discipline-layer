"""Stage health: completion is derived from artifacts, never from self-report.

Scorers are recomputed from per-item data; self-reported summary fields are
treated as claims, not as evidence.
"""
from typing import Dict, List


def recompute(results: Dict, baseline: str = "model_a",
              candidate: str = "model_b") -> Dict[str, float]:
    m = {}
    for model, blob in results.items():
        per = blob["per_item"]
        m[f"{model}::win_pct"] = round(100.0 * sum(per) / len(per), 1)
    m["delta_pp"] = round(m[f"{candidate}::win_pct"] - m[f"{baseline}::win_pct"], 1)
    m["n"] = len(results[candidate]["per_item"])
    return m


def verify_completion(claimed: Dict[str, Dict[str, int]], results: Dict) -> List[str]:
    out = []
    for model, claim in claimed.items():
        per = results[model]["per_item"]
        truth = sum(per)
        if claim.get("passed") != truth:
            out.append(
                f"{model}: completion self-report says {claim.get('passed')}/{claim.get('total')}, "
                f"per_item recomputes to {truth}/{len(per)}"
            )
        summary = results[model].get("summary", {}).get("passed")
        if summary is not None and summary != truth:
            out.append(
                f"{model}: artifact summary field says {summary} but per_item recomputes to "
                f"{truth} (self-reported fields are not evidence)"
            )
    return out

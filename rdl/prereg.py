"""Preregistration: freeze claim thresholds and stop-loss conditions before the run starts.

The frozen file is hashed; any later edit changes the hash and is detectable.
Conclusion vocabulary ("decisive", "wins", ...) is gated by preregistered
minimums checked against recomputed metrics at audit time.
"""
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


def content_sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


def freeze(path, doc: Dict[str, Any]) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    return content_sha(path)


def verify_unchanged(path, sha: str) -> bool:
    return content_sha(path) == sha


def check_claim_word(prereg: Dict[str, Any], word: str,
                     metrics: Dict[str, float]) -> List[str]:
    rules = prereg.get("claim_vocabulary", {}).get(word)
    if rules is None:
        return []
    violations = []
    for key, minimum in rules.items():
        actual = metrics.get(key)
        if actual is None or actual < minimum:
            violations.append(
                f"claim word '{word}' requires {key}>={minimum}, recomputed {key}={actual}"
            )
    return violations

"""Campaign ledger: every claim carries an epistemic tag, every observation an anchor.

Tags: OBSERVED (needs an artifact anchor) / INFERRED / DECIDED.
Confidence: HIGH / MEDIUM / LOW / ABSTAIN.
Every append is verified by a write-back/read-back check on three numbers
(entry count, last entry id, last entry hash) -- a torn or tampered write raises.
"""
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

TAGS = ("OBSERVED", "INFERRED", "DECIDED")
CONFIDENCE_TIERS = ("HIGH", "MEDIUM", "LOW", "ABSTAIN")


class LedgerIntegrityError(RuntimeError):
    pass


@dataclass
class Entry:
    id: int
    ts: str
    tag: str
    claim: str
    anchor: Optional[str] = None
    confidence: Optional[str] = None
    numbers: Optional[Dict[str, float]] = None


def _canonical(entry: Entry) -> str:
    return json.dumps(asdict(entry), sort_keys=True, ensure_ascii=False)


def _triple(entries: List[Entry]):
    return (
        len(entries),
        entries[-1].id if entries else None,
        hashlib.sha256(_canonical(entries[-1]).encode("utf-8")).hexdigest()[:12] if entries else None,
    )


class Ledger:
    """JSONL ledger with mandatory read-back verification."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self._entries = self._load()

    def _load(self) -> List[Entry]:
        entries = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(Entry(**json.loads(line)))
        return entries

    def append(self, tag: str, claim: str, anchor: Optional[str] = None,
               confidence: Optional[str] = None,
               numbers: Optional[Dict[str, float]] = None) -> Entry:
        if tag not in TAGS:
            raise ValueError(f"tag must be one of {TAGS}, got {tag!r}")
        if confidence is not None and confidence not in CONFIDENCE_TIERS:
            raise ValueError(f"confidence must be one of {CONFIDENCE_TIERS}, got {confidence!r}")
        entry = Entry(
            id=(self._entries[-1].id + 1) if self._entries else 1,
            ts=time.strftime("%Y-%m-%dT%H:%M:%S"),
            tag=tag, claim=claim, anchor=anchor, confidence=confidence, numbers=numbers,
        )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(_canonical(entry) + "\n")
        self._readback(entry, expected_count=len(self._entries) + 1)
        self._entries.append(entry)
        return entry

    def _readback(self, expected_last: Entry, expected_count: int):
        on_disk = self._load()
        if _triple(on_disk) != _triple(self._entries + [expected_last]):
            raise LedgerIntegrityError(
                f"read-back mismatch: disk={_triple(on_disk)} "
                f"expected={_triple(self._entries + [expected_last])}"
            )

    def readback_triple(self):
        return _triple(self._entries)

    def entries(self) -> List[Entry]:
        return list(self._entries)

    def audit_anchors(self) -> List[str]:
        return [
            f"OBSERVED claim without anchor: '{e.claim}'"
            for e in self._entries
            if e.tag == "OBSERVED" and not e.anchor
        ]

"""RDL -- Research Discipline Layer.

Gates for long autonomous agent research runs. The layer does not help your
agent do research; it stops the run from lying to you.
"""
from . import audit, health, ledger, prereg, sentinel

__version__ = "0.1.0"

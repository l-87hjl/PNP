"""
PNP: A P vs NP experimentation tool based on lock-and-SAT equivalence.

This package provides tools for creating, solving, and visualizing constraint-based
locks that encode SAT problems.
"""

from .lock_types import LockInstance, LockSolution

__version__ = "0.1.0"
__all__ = ["LockInstance", "LockSolution"]

"""
This script defines the graph structure for the Expert System based on Propositional Calculus.
It includes the `FactV` class for atomic propositions and the `RuleV` class for inference rules.

Dependencies:
    - dataclasses
    - typing: Set for type hinting
    - truth: A module containing the Truth enumeration for representing truth values.
    - parser: A module containing the Node class for representing nodes in the rule structure.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set

from truth import Truth
from parser import Node


@dataclass
class FactV:
    """Vertex for one atomic proposition (A…Z)."""
    name: str
    state: Truth | None = None
    in_rules:  Set["RuleV"] = field(default_factory=set) # rules that conclude this fact
    out_rules: Set["RuleV"] = field(default_factory=set) # rules that require this fact

    # helpers so we can stick FactV objects in sets
    def __hash__(self) -> int: return hash(self.name)
    def __repr__(self) -> str: return f"Fact({self.name},{self.state.name})"


@dataclass
class RuleV:
    """Vertex for one inference rule."""
    idx: int
    premise: Node
    conclusions: Node
    truth: Truth = Truth.UNKNOWN
    in_facts:  Set[FactV] = field(default_factory=set) # facts in premise
    out_facts: Set[FactV] = field(default_factory=set) # facts in conclusion
    text: str = "" # original textual form

    def __hash__(self) -> int: return self.idx
    def __repr__(self) -> str: return f"Rule#{self.idx}:{self.text}"

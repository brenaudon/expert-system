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
    """
    Vertex for one atomic proposition (fact).

    @ivar name: The name of the fact (e.g., 'A', 'B').
    @type name: str
    @ivar state: The truth value of the fact, which can be TRUE, FALSE, or UNKNOWN.
    @type state: Truth | None
    @ivar initial_fact: Whether this fact was in the initial set of facts.
    @type initial_fact: bool
    @ivar in_rules: A set of rules that conclude this fact.
    @type in_rules: Set[RuleV]
    @ivar out_rules: A set of rules that require this fact.
    @type out_rules: Set[RuleV]
    """
    name: str
    state: Truth | None = None
    initial_fact: bool = False  # whether this fact was in the initial set of facts
    in_rules: Set["RuleV"] = field(default_factory=set) # rules that conclude this fact
    out_rules: Set["RuleV"] = field(default_factory=set) # rules that require this fact

    # helpers so we can stick FactV objects in sets
    def __hash__(self) -> int: return hash(self.name)
    def __repr__(self) -> str: return f"Fact({self.name},{self.state.name})"


@dataclass
class RuleV:
    """
    Vertex for one inference rule.

    @ivar idx: The index of the rule, used for identification.
    @type idx: int
    @ivar premise: The premise of the rule, represented as a Node.
    @type premise: Node
    @ivar conclusions: The conclusions of the rule, represented as a Node.
    @type conclusions: Node
    @ivar truth: The truth value of the rule, which can be TRUE, FALSE, or UNKNOWN.
    @type truth: Truth
    @ivar in_facts: A set of facts that are in the premise of the rule.
    @type in_facts: Set[FactV]
    @ivar out_facts: A set of facts that are in the conclusions of the rule.
    @type out_facts: Set[FactV]
    """
    idx: int
    premise: Node
    conclusions: Node
    truth: Truth = Truth.UNKNOWN
    in_facts: Set[FactV] = field(default_factory=set) # facts in premise
    out_facts: Set[FactV] = field(default_factory=set) # facts in conclusion
    text: str = ""

    def __hash__(self) -> int: return self.idx
    def __repr__(self) -> str: return f"Rule#{self.idx}:{self.text}"

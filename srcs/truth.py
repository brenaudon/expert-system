"""
This script defines the `Truth` enumeration for the Expert System based on Propositional Calculus.
It represents the truth values of facts, which can be TRUE, FALSE, or UNKNOWN.

Dependencies:
    - enum

"""

from enum import Enum, auto

class Truth(Enum):
    """
    Represents the truth value of a fact in the expert system.
    """
    TRUE = auto()
    FALSE = auto()
    UNKNOWN = auto()

    def __str__(self):
        return self.name
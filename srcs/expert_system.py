"""
This script implements an expert system that processes rules and facts to answer queries.
It uses propositional calculus to evaluate the truth values of facts based on defined rules.
It supports logical operations such as AND, OR, XOR, and NOT, and can handle cycles in reasoning.
It provides explanations for the reasoning behind each fact's truth value.

Dependencies:
    - collections
    - typing
    - truth: Contains the Truth enumeration for representing truth values (TRUE, FALSE, UNKNOWN).
    - graph: Contains definitions for FactV and RuleV, which represent vertices in the reasoning graph.
    - parser.py: Contains definitions for Rule, Node, FactNode, UnaryNode, BinaryNode, and TokenType.

"""

from collections import defaultdict
from typing import Dict, List, Set
from truth import Truth
from graph import FactV, RuleV
from parser import Rule, Node, FactNode, UnaryNode, BinaryNode, TokenType


def _collect_facts(node: Node, bucket: Set[str]) -> None:
    """
    Recursively collects all fact names from a node and adds them to the provided bucket.
    This function traverses the node structure and gathers all fact names that are part of the node.
    It handles different types of nodes (FactNode, UnaryNode, BinaryNode) and adds fact names to the bucket.
    This is used to gather all facts that are part of a rule or conclusion.

    @param node: The node to traverse and collect facts from.
    @type node: Node
    @param bucket: A set to which the collected fact names will be added.
    @type bucket: Set[str]

    @return: None
    """
    if isinstance(node, FactNode):
        bucket.add(node.name)
    elif isinstance(node, UnaryNode):
        _collect_facts(node.child, bucket)
    elif isinstance(node, BinaryNode):
        _collect_facts(node.left,  bucket)
        _collect_facts(node.right, bucket)


class ExpertSystem:
    """
    Represents the expert system that processes rules and facts to answer queries.

    @ivar reason_log: A dictionary mapping facts to lists of reasoning steps explaining their truth value.
    @type reason_log: Dict[str, List[str]]
    @ivar cycles: A set of facts that are part of cycles in the reasoning graph.
    @type cycles: Set[str]
    @ivar true_nodes: A list of nodes that are guaranteed to be true.
    @type true_nodes: List[str]
    @ivar facts: A dictionary mapping fact names to their corresponding FactV objects.
    @type facts: Dict[str, FactV]
    @ivar rules: A list of RuleV objects representing the rules defined in the system.
    @type rules: List[RuleV]
    """
    def __init__(self, rules: List[Rule], facts_init: Set[str]):
        """
        Initializes the expert system with given rules and initial facts.

        @param rules: List of rules defining the logic of the expert system.
        @type rules: List[Rule]
        @param facts_init: Set of initial facts known to the system.
        @type facts_init: Set[str]
        """
        self.reason_log: Dict[str, List[str]] = defaultdict(list)
        self.cycles: Set[str] = set()
        self.true_nodes = list()

        # Global graph of facts and rules
        self.facts: Dict[str, FactV] = {}
        self.rules: List[RuleV] = []

        def fv(name: str) -> FactV:
            if name not in self.facts:
                self.facts[name] = FactV(name)
            return self.facts[name]

        for f in facts_init:
            fact_v = fv(f)
            fact_v.state = Truth.TRUE
            fact_v.initial_fact = True

        for idx, r in enumerate(rules):
            rv = RuleV(idx, r.lhs, r.conclusions, text=r.text)
            self.rules.append(rv)

            # premise facts
            prem_set: Set[str] = set()
            _collect_facts(r.lhs, prem_set)
            for f in prem_set:
                fact_v = fv(f)
                rv.in_facts.add(fact_v)
                fact_v.out_rules.add(rv)

            # conclusion facts
            conc_set: Set[str] = set()
            _collect_facts(r.conclusions, conc_set)
            for f in conc_set:
                fact_v = fv(f)
                rv.out_facts.add(fact_v)
                fact_v.in_rules.add(rv)


    def collect_conclusion_facts(self, node: Node) -> Set[str]:
        """
        Collects all facts that are part of the mandatory conclusions of a rule.
        This method traverses the conclusion node and gathers all fact names
        that are guaranteed to be true when the rule is applied.

        @param node: The conclusion node to analyze.
        @type node: Node

        @return: A set of fact names that are guaranteed to be true.
        @rtype: Set[str]
        """
        if isinstance(node, FactNode):
            return {node.name}
        if isinstance(node, UnaryNode):
            return self.collect_conclusion_facts(node.child)
        if isinstance(node, BinaryNode):
            return self.collect_conclusion_facts(node.left) | self.collect_conclusion_facts(node.right)
        return set()


    def query(self, fact: str) -> Truth:
        """
        Queries the expert system for the truth value of a given fact.
        This method checks if the fact is known and evaluates it using the rules
        defined in the system. It uses memoization to avoid redundant calculations.
        If the fact is not known, it returns UNKNOWN and logs the reasoning.

        @param fact: The fact to query.
        @type fact: str

        @return: The truth value of the fact (TRUE, FALSE, or UNKNOWN).
        @rtype: Truth
        """
        # Check if the fact is already known
        if self.facts.get(fact) is None:
            self.reason_log[fact].append(f"No data about {fact}.")
            return Truth.FALSE
        return self.solve(fact, set())

    def solve(self, fact: str, path: Set[str]) -> Truth:
        """
        Recursively evaluates the truth value of a fact using the rules defined in the system.
        This method checks if the fact is already known, evaluates it based on the rules,
        and uses memoization to store results for future queries. It also handles cycles
        in the reasoning graph to prevent infinite recursion.

        @param fact: The fact to evaluate.
        @type fact: str
        @param path: Set of facts currently being evaluated to detect cycles.
        @type path: Set[str]

        @return: The truth value of the fact (TRUE, FALSE, or UNKNOWN).
        @rtype: Truth
        """
        # Already known
        if self.facts[fact].state:
            if self.facts[fact].state == Truth.TRUE and fact not in self.reason_log:
                if self.facts[fact].initial_fact:
                    self.reason_log[fact].append(f"{fact} is an initial fact.")
                else:
                    self.reason_log[fact].append(f"{fact} is already known to be TRUE.")
            elif self.facts[fact].state == Truth.FALSE and fact not in self.reason_log:
                self.reason_log[fact].append(f"{fact} is already known to be FALSE.")
            return self.facts[fact].state

        # Avoid infinite recursion (cycles)
        if fact in path:
            self.cycles.add(fact)
            return Truth.UNKNOWN
        path.add(fact)

        # Try each rule that can conclude fact
        proved_true  = False
        proved_false = False
        unknown_due_to_disjunction = False
        for rv in self.facts[fact].in_rules:          # global graph lookup
            rule = self.rules[rv.idx]
            if rule.truth == Truth.TRUE:
                res = Truth.TRUE
            else:
                res = self.eval_expr(rule.premise, path)
            if res == Truth.TRUE:
                self.true_nodes.append(rule.conclusions)
                if self.conclusion_guarantees_fact(rule.conclusions, fact):
                    self.reason_log[fact].append(
                        f"Rule '{rule.text}' fires and conclusively sets {fact} true.")
                    self.facts[fact].state = Truth.TRUE
                    proved_true = True
                elif self.conclusion_negates_fact(rule.conclusions, fact):
                    self.facts[fact].state = Truth.FALSE
                    self.reason_log[fact].append(
                        f"Rule '{rule.text}' fires and conclusively sets {fact} false.")
                    proved_false = True
                else:
                    # Disjunctive conclusion: cannot be sure
                    unknown_due_to_disjunction = True
                    self.reason_log[fact].append(
                        f"Rule '{rule.text}' fires but does not uniquely identify {fact}.")
            elif res == Truth.UNKNOWN:
                unknown_due_to_disjunction = True
        path.remove(fact)

        # ── decide final truth value ─────────────────────────────────────────────
        if proved_true and proved_false:
            self.reason_log[fact].append(
                f"Contradiction: some rules set {fact} true, others false.")
            self.facts[fact].state = Truth.UNKNOWN
            return Truth.UNKNOWN
        if proved_true:
            self.facts[fact].state = Truth.TRUE
            return Truth.TRUE
        if proved_false:
            self.facts[fact].state = Truth.FALSE
            return Truth.FALSE
        if unknown_due_to_disjunction:
            self.facts[fact].state = Truth.UNKNOWN
            # log cycle only if it really blocked the answer
            if fact in self.cycles:
                self.reason_log[fact].append(
                    f"Cycle detected while evaluating {fact}.")
            return Truth.UNKNOWN

        self.facts[fact].state = Truth.FALSE
        self.reason_log[fact].append(
            f"No rule proved {fact}; keeping default FALSE.")
        return Truth.FALSE

    # Evaluate arbitrary expression node
    def eval_expr(self, node: Node, path: Set[str]) -> Truth:
        """
        Evaluates a logical expression represented by a node in the expert system.
        This method recursively evaluates the expression based on the type of node
        (fact, unary, or binary) and returns the truth value of the expression.
        It handles the evaluation of AND, OR, and XOR operations, as well as negation.
        It also checks for previously computed results to optimize performance.

        @param node: The node representing the logical expression to evaluate.
        @type node: Node
        @param path: A set of facts currently being evaluated to detect cycles.
        @type path: Set[str]

        @return: The truth value of the evaluated expression (TRUE, FALSE, or UNKNOWN).
        @rtype: Truth
        """
        if self.true_nodes and node in self.true_nodes:
            return Truth.TRUE
        # Fact node
        if isinstance(node, FactNode):
            return self.solve(node.name, path)
        # Unary node (negation)
        if isinstance(node, UnaryNode):
            child_val = self.eval_expr(node.child, path)
            if child_val == Truth.UNKNOWN:
                return Truth.UNKNOWN
            return Truth.FALSE if child_val == Truth.TRUE else Truth.TRUE
        # Binary node (AND, OR, XOR)
        if isinstance(node, BinaryNode):
            left = self.eval_expr(node.left, path)
            right = self.eval_expr(node.right, path)
            op = node.op
            if op == TokenType.AND:
                if left == Truth.FALSE or right == Truth.FALSE:
                    return Truth.FALSE
                if left == Truth.TRUE and right == Truth.TRUE:
                    return Truth.TRUE
                return Truth.UNKNOWN
            if op == TokenType.OR:
                if left == Truth.TRUE or right == Truth.TRUE:
                    return Truth.TRUE
                if left == Truth.FALSE and right == Truth.FALSE:
                    return Truth.FALSE
                return Truth.UNKNOWN
            if op == TokenType.XOR:
                if left == Truth.UNKNOWN or right == Truth.UNKNOWN:
                    return Truth.UNKNOWN
                return Truth.TRUE if (left == Truth.TRUE) ^ (right == Truth.TRUE) else Truth.FALSE
        raise RuntimeError("Invalid node type in eval_expr")


    def conclusion_guarantees_fact(self, node: Node, fact: str) -> bool:
        """
        Checks if the conclusion represented by the node guarantees that a specific fact is true.
        This method evaluates the conclusion node and determines if it guarantees the truth of the given fact.
        It handles different types of nodes (fact, unary, binary) and checks the logical operations involved.
        This is used to determine if a rule conclusively sets a fact to true.

        @param node: The conclusion node to evaluate.
        @type node: Node
        @param fact: The fact to check if it is guaranteed by the conclusion.
        @type fact: str

        @return: True if the conclusion guarantees the fact, False otherwise.
        @rtype: bool
        """
        # Check if the node is a fact node and matches the fact
        if isinstance(node, FactNode):
            return node.name == fact
        if isinstance(node, BinaryNode):
            # AND list guarantees each fact
            if node.op == TokenType.AND:
                return self.conclusion_guarantees_fact(node.left, fact) or self.conclusion_guarantees_fact(node.right, fact)
            # OR/XOR do NOT guarantee
            return False
        return False

    def conclusion_negates_fact(self, node: Node, fact: str) -> bool:
        """
        Checks if the conclusion represented by the node negates a specific fact.
        This method evaluates the conclusion node and determines if it negates the truth of the given fact.
        It handles different types of nodes (fact, unary, binary) and checks the logical operations involved.
        This is used to determine if a rule conclusively sets a fact to false.

        @param node: The conclusion node to evaluate.
        @type node: Node
        @param fact: The fact to check if it is negated by the conclusion.
        @type fact: str

        @return: True if the conclusion negates the fact, False otherwise.
        @rtype: bool
        """
        if isinstance(node, UnaryNode) and node.op == TokenType.NOT:
            return isinstance(node.child, FactNode) and node.child.name == fact
        # Allow lists like  !C + D
        if isinstance(node, BinaryNode) and node.op == TokenType.AND:
            return (self.conclusion_negates_fact(node.left,  fact) or
                    self.conclusion_negates_fact(node.right, fact))
        return False

    # ---------------------------------------------------------------------
    def explain(self, fact: str):
        """
        Prints the reasoning log for a given fact.
        This method retrieves the reasoning steps recorded for the fact and prints them.
        If the fact has never been queried, it indicates that no explanation is available.

        @param fact: The fact for which to print the explanation.
        @type fact: str

        @return: None
        """
        if fact in self.reason_log:
            for line in self.reason_log[fact]:
                print("  ", line)
        else:
            print("  No explanation recorded (fact never queried).")

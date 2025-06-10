"""
This script serves as a parser for the Expert System, reading rules, initial facts, and queries from a specified file.

Dependencies:
    - re
    - enum
    - typing
    - dataclasses

"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Set, Tuple, Union


# Tokeniser & Grammar ----------------------------------------------------------

TOKEN_RE = re.compile(r"\s*([A-Z]|!|\+|\||\^|\(|\)|=>|<=>|:)\s*")

class TokenType(Enum):
    """
    Enum representing different types of tokens in propositional logic expressions.
    Each token type corresponds to a specific operator or fact in the logic expression.
        - FACT: Represents a propositional fact (single letter).
        - NOT: Represents the negation operator.
        - AND: Represents the logical AND operator.
        - OR: Represents the logical OR operator.
        - XOR: Represents the exclusive OR operator.
        - IMPLIES: Represents the implication operator (=>).
        - IFF: Represents the biconditional operator (<=>).
        - LPAREN: Represents the left parenthesis.
        - RPAREN: Represents the right parenthesis.
    """
    FACT = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    IMPLIES = auto()
    IFF = auto()
    LPAREN = auto()
    RPAREN = auto()

_tok_map = {
    '!': TokenType.NOT,
    '+': TokenType.AND,
    '|': TokenType.OR,
    '^': TokenType.XOR,
    '=>': TokenType.IMPLIES,
    '<=>': TokenType.IFF,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
}

@dataclass
class Token:
    """
    Represents a token in the propositional logic expression.

    @ivar type: The type of the token, which is an instance of TokenType.
    @type type: TokenType
    @ivar value: The string representation of the token, such as a fact or operator.
    @type value: str
    """
    type: TokenType
    value: str

# AST (Abstract Syntax Tree) ---------------------------------------------------

class Node:
    """
    Base class for all nodes in the Abstract Syntax Tree (AST).
    """
    pass

@dataclass
class FactNode(Node):
    """
    Represents a fact node in the AST, which corresponds to a propositional fact.

    @ivar name: The name of the fact, typically a single letter.
    @type name: str
    """
    name: str  # single letter

@dataclass
class UnaryNode(Node):
    """
    Represents a unary operation node in the AST (NOT).

    @ivar op: The operator type, which is always NOT in this case.
    @type op: TokenType
    @ivar child: The child node that this unary operation applies to.
    @type child: Node
    """
    op: TokenType  # only NOT
    child: Node

@dataclass
class BinaryNode(Node):
    """
    Represents a binary operation node in the AST (AND, OR, XOR).

    @ivar op: The operator type, which can be AND, OR, or XOR.
    @type op: TokenType
    @ivar left: The left child node of the binary operation.
    @type left: Node
    @ivar right: The right child node of the binary operation.
    @type right: Node
    """
    op: TokenType  # AND / OR / XOR
    left: Node
    right: Node

# Parser (shunting‑yard) -------------------------------------------------------

# Precedence and associativity for operators
# Precedence defines the order of operations
# Associativity defines how operators of the same precedence are grouped
PRECEDENCE = {
    TokenType.NOT: 4,
    TokenType.AND: 3,
    TokenType.XOR: 2,
    TokenType.OR: 1,
}

LEFT_ASSOC = {TokenType.AND, TokenType.OR, TokenType.XOR}
RIGHT_ASSOC = {TokenType.NOT}


def tokenize(expr: str) -> List[Token]:
    """
    Tokenizes the input expression string into a list of tokens.

    @param expr: The input expression string to tokenize.
    @type expr: str

    @return: A list of tokens parsed from the expression.
    @rtype: List[Token]
    """
    pos = 0
    tokens: List[Token] = []
    while pos < len(expr):
        m = TOKEN_RE.match(expr, pos)
        if not m:
            raise ValueError(f"Bad token at pos {pos}: …{expr[pos:pos+10]}")
        raw = m.group(1)
        pos = m.end()
        if raw.isalpha():
            tokens.append(Token(TokenType.FACT, raw))
        else:
            tokens.append(Token(_tok_map[raw], raw))
    return tokens


def parse_expression(expr: str) -> Node:
    """
    Parses a propositional logic expression into an Abstract Syntax Tree (AST).
    This function uses the shunting-yard algorithm to convert infix notation
    to postfix notation and then builds the AST from the postfix tokens.

    @param expr: The input expression string in propositional logic.
    @type expr: str

    @return: The root node of the AST representing the expression.
    @rtype: Node
    """
    output: List[Union[Token, Node]] = []
    stack: List[Token] = []
    for tok in tokenize(expr):
        if tok.type == TokenType.FACT:
            output.append(FactNode(tok.value))
        elif tok.type == TokenType.NOT:
            stack.append(tok)
        elif tok.type in (TokenType.AND, TokenType.OR, TokenType.XOR):
            while stack and stack[-1].type in PRECEDENCE and (
                    (stack[-1].type in LEFT_ASSOC and PRECEDENCE[stack[-1].type] >= PRECEDENCE[tok.type]) or
                    (stack[-1].type in RIGHT_ASSOC and PRECEDENCE[stack[-1].type] > PRECEDENCE[tok.type])
            ):
                pop_to_output(stack, output)
            stack.append(tok)
        elif tok.type == TokenType.LPAREN:
            stack.append(tok)
        elif tok.type == TokenType.RPAREN:
            while stack and stack[-1].type != TokenType.LPAREN:
                pop_to_output(stack, output)
            if not stack:
                raise ValueError("Mismatched parentheses")
            stack.pop()  # remove LPAREN
        else:
            raise ValueError(f"Unsupported token {tok}")
    while stack:
        if stack[-1].type in (TokenType.LPAREN, TokenType.RPAREN):
            raise ValueError("Mismatched parentheses at end")
        pop_to_output(stack, output)
    assert len(output) == 1 and isinstance(output[0], Node) # ensure single root node
    return output[0]  # type: ignore[index]


def pop_to_output(stack: List[Token], output: List[Union[Token, Node]]):
    """
    Pops an operator from the stack and creates a node in the output.
    This function handles both unary and binary operators, creating the appropriate AST nodes.

    @param stack: The stack containing tokens, where the top is the operator to pop.
    @type stack: List[Token]
    @param output: The output list where the resulting AST nodes will be appended.
    @type output: List[Union[Token, Node]]

    @return: None
    """
    op_tok = stack.pop()
    if op_tok.type == TokenType.NOT:
        assert output, "Unary op with no operand"
        child = output.pop()
        output.append(UnaryNode(op_tok.type, child))
    else:
        right = output.pop()
        left = output.pop()
        output.append(BinaryNode(op_tok.type, left, right))


#  Rule Representation ---------------------------------------------------------

@dataclass
class Rule:
    """
    Represents a rule in the expert system.
    A rule consists of a left-hand side (lhs) and one or more conclusions (rhs).

    @ivar lhs: The left-hand side of the rule, which is a Node representing the condition.
    @type lhs: Node
    @ivar conclusions: The right-hand side of the rule, which can be a single FactNode or a BinaryNode representing multiple conclusions.
    @type conclusions: Node
    @ivar text: The original text of the rule for explanations and debugging.
    @type text: str
    """
    lhs: Node
    conclusions: Node  # may be BinaryNode with OR/XOR/AND or single FactNode
    text: str  # original text for explanations


# File Parsing -----------------------------------------------------------------

def parse_file(path: str) -> Tuple[List[Rule], Set[str], List[str]]:
    """
    Parses a file containing rules, initial facts, and queries for the expert system.
    The file format is expected to have:
        - Lines starting with '=' to denote initial facts.
        - Lines starting with '?' to denote queries.
        - Lines containing rules in the format 'A => B' or 'A <=> B', where A and B are propositional expressions.
        - Lines can also contain comments starting with '#'.
    The function returns a list of rules, a set of initial facts, and a list of queries.

    @param path: The path to the file containing rules, facts, and queries.
    @type path: str
    @return: A tuple containing:
        - A list of Rule objects representing the rules in the file.
        - A set of initial facts (single letters).
        - A list of queries (single letters).
    @rtype: Tuple[List[Rule], Set[str], List[str]]
    """
    rules: List[Rule] = []
    initial_facts: Set[str] = set()
    queries: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#", 1)[0].strip()  # remove comments
            if not line:
                continue
            if line.startswith("="):
                initial_facts.update(list(line[1:].strip()))
                continue
            if line.startswith("?"):
                queries.extend(list(line[1:].strip()))
                continue
            # Must be a rule
            if "<=>" in line:
                lhs_txt, rhs_txt = map(str.strip, line.split("<=>"))
                lhs_expr = parse_expression(lhs_txt)
                rhs_expr = parse_expression(rhs_txt)
                # Biconditional => two rules
                rules.append(Rule(lhs=lhs_expr, conclusions=rhs_expr, text=line.strip()))
                rules.append(Rule(lhs=rhs_expr, conclusions=lhs_expr, text=line.strip()))
            elif "=>" in line:
                lhs_txt, rhs_txt = map(str.strip, line.split("=>"))
                lhs_expr = parse_expression(lhs_txt)
                rhs_expr = parse_expression(rhs_txt)
                rules.append(Rule(lhs=lhs_expr, conclusions=rhs_expr, text=line.strip()))
            else:
                raise ValueError(f"Malformed rule: {line}")
    return rules, initial_facts, queries
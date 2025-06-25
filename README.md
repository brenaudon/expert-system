# **Expert System**

---

## **Project Overview**

A propositional‑logic **expert system** written in pure Python. It parses a text file that contains rules, initial facts and queries, then answers each query with *True / False / Unknown* and prints an *explanation trace*.  The engine supports:

* Logical operators **NOT (!)**, **AND (+)**, **OR (|)**, **XOR (^)** and full parentheses.
* Multi‑premise and multi‑conclusion rules, including **OR/XOR** in the right‑hand side.
* Biconditionals **<=>** (expanded into two opposite rules).
* Contradiction detection + cycle detection.
* Interactive mode (`-i` flag) to tweak facts on the fly.

### **Input file format**

The input file consists of three sections:
1. **Rules** – each line contains a rule with premises and conclusions, e.g. `A + B => C`.
2. **Initial facts** – a single line with initial facts, e.g. `=AB` means `A` and `B` are true.
3. **Queries** – a single line with queries, e.g. `?CDE` means check if `C`, `D`, and `E` are true.

Comments (starting with #) and blank lines are allowed.

Example input file (`examples/rules.txt`):

```
A + B => C
A + B <=> D | E # This is a comment
C ^ G => F
F | H => I ^ J

=AB
?CDEFI
# This is also a comment
```

---

## **Project Documentation**

[Auto-generated documentation from Docstrings](https://brenaudon.github.io/expert-system/)

---

## **Setup Project**

To set up the project, follow these steps:
1. **Clone the repository:**
   ```bash
    git clone git@github.com:brenaudon/expert-system.git expert-system
    cd expert-system
    ```
2. **Install dependencies:**
   Optionally, you can create a virtual environment to isolate the project dependencies.
   ```bash
    python -m venv venv
    source venv/bin/activate  # Adapt this to your distribution
   ```
   Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Usage**

To run the expert system, use the following commands:

```bash
python main.py <path_to_input_file>        # answer queries and exit
python main.py examples/rules.txt -i     # answer queries then enter interactive mode
```

---

## **Tokenisation**

`parser.TOKEN_RE` is a single regex that matches *one* token while trimming optional whitespace on both sides:

```
\s*([A-Z]|!|\+|\||\^|\(|\)|=>|<=>|:)\s*
```

* `[A‑Z]` → **FACT** token, value is the letter itself.
* Everything else is mapped to a `TokenType` via `_tok_map`.

The lexer (`tokenize`) returns a flat list: `[Token(TokenType.FACT,"A"), Token(TokenType.AND,"+"), …]`.  We keep both the **type** and the **raw lexeme** because different facts share the same type and we want faithful error messages.

---

## **Abstract Syntax Tree (AST)**

An AST is a compact, hierarchical in-memory model that captures the logical structure of the expression but discards all non-essential punctuation and whitespace.  
We build the AST in `parser.parse_expression()` using shunting‑yard algorithm.

Each expression is converted into immutable, typed nodes:

* `FactNode(name)`
* `UnaryNode(op, child)` — only **NOT** here
* `BinaryNode(op, left, right)`— **AND / OR / XOR**

`Node` is an empty base class so the evaluator can rely on `isinstance(node, Node)`.

We're want to get:
```

!(A + B) | C ^ D   →     OR
                      /      \
                    NOT      XOR
                     |      /   \
                    AND    C     D
                   /   \
                  A     B
```

---

## **Shunting‑yard parsing**

`parse_expression()` implements shunting‑yard algorithm:

1. Scan tokens left→right.
2. Two tracks: **operator stack** (list of Tokens) and **output list** (list of Nodes).
3. Precedence table

   ```python
   PRECEDENCE = {NOT:4, AND:3, XOR:2, OR:1}
   LEFT_ASSOC  = {AND, OR, XOR}
   RIGHT_ASSOC = {NOT}
   ```
4. Parentheses act as sentinels.
5. When an operator is popped, `pop_to_output()` consumes 1 (unary) or 2 (binary) nodes from the output list and pushes a freshly built AST node.
6. At the end we assert `len(output)==1`; that node is the root of the expression tree.

Precedence are used to determine how operators are grouped. For example, `A + B | C` is parsed as `(A + B) | C` because `AND` has higher precedence than `OR`.
Associativity determines how operators of the same precedence are grouped. For example, `A + B + C` is parsed as `(A + B) + C` because `AND` is left associative.

---

## **Inference engine (back‑ward chaining)**

`ExpertSystem.solve()` proves a queried fact by recursion on rules whose **conclusions** mention that fact.

* **Memoisation** – results cached in `self.memo`.
* **Cycles** – a `path` set tracks the current chain. Encountering the same fact again adds it to `self.cycles` and returns *Unknown*.
* **Contradictions** – if one rule proves a fact *True* and another *False*, the final result is *Unknown* and the log notes the conflict.
* **Disjunctive RHS** – AND guarantees every sub‑fact; OR/XOR leave them undetermined.  The full RHS (Right-Hand Side) string is cached in `self.true_rules` so a later rule can reuse the composite truth (needed for chained XOR/OR conclusions).

Evaluation of the AST is done in `eval_expr()`, which recursively evaluates each node. Recursion go down to the leaves (facts) and then back up, combining results according to the logical operators.

### Truth tables inside `eval_expr()`

| Not         | Result  |
|-------------|---------|
| **True**    | False   |
| **False**   | True    |
| **Unknown** | Unknown |

| AND         | True    | False | Unknown |
|-------------|---------|-------|---------|
| **True**    | True    | False | Unknown |
| **False**   | False   | False | False   |
| **Unknown** | Unknown | False | Unknown |

| OR          | True | False   | Unknown |
|-------------|------|---------|---------|
| **True**    | True | True    | True    |
| **False**   | True | False   | Unknown |
| **Unknown** | True | Unknown | Unknown |

| XOR         | True    | False   | Unknown  |
|-------------|---------|---------|----------|
| **True**    | False   | True    | Unknown  |
| **False**   | True    | False   | Unknown  |
| **Unknown** | Unknown | Unknown | Unknown  |

---

## **Interactive mode**

In interactive mode (`-i` flag), the system allows you to modify facts on the fly. You can add or remove facts, and the system will re-evaluate the queries based on the updated facts.

### Commands in interactive mode:
* `+X` – add fact `X` (set it to true).
* `-X` – remove fact `X` (set it to false).
* `?X` – query fact `X`.
* `/q` – exit interactive mode.


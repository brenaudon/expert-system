"""
This script serves as the entry point for the Expert System based on Propositional Calculus.
It processes an input file containing rules, facts, and queries, and provides an interface to query the system.

Dependencies:
    - argparse
    - typing
    - parser: A module to parse the input file and extract rules, facts, and queries.
    - expert_system: A module containing the ExpertSystem class that implements the logic for handling rules and queries.

"""

import argparse
from collections import defaultdict
from typing import Set
from parser import parse_file
from expert_system import ExpertSystem, Truth


def interactive(es: ExpertSystem, facts_init: Set[str]):
    """
    Interactive mode for the Expert System, allowing users to set facts and query them.
    This function provides a command-line interface where users can:
        - Set a fact to true or false
        - Query the truth value of a fact
        - Explain the reasoning behind the truth value of a fact

    @param es: An instance of the ExpertSystem class that manages the facts and rules.
    @type es: ExpertSystem
    @param facts_init: A set of initial facts.
    @type facts_init: Set[str]

    @return: None
    """
    print("Entering interactive mode. Commands:\n  +X : set fact X true\n  -X : set fact X false\n  ?X : query fact X\n  /q : quit")
    while True:
        try:
            cmd = input("expert> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not cmd:
            continue
        if cmd == "/Q":
            break
        if cmd.startswith("+") and len(cmd) == 2 and cmd[1].isalpha():
            fact = cmd[1]
            # Reset all non-initial facts to None
            for name, f in es.facts.items():
                if f.name not in facts_init:
                    f.state = None
            # Set the fact to True
            es.facts[fact].state = Truth.TRUE
            # Add the fact to the initial facts set so it is not reset next time
            facts_init.add(fact)
            # Reset reason log to empty for each entry of the dictionary
            es.reason_log = defaultdict(list)
            print(f"Set {fact}=True")
            continue
        if cmd.startswith("-") and len(cmd) == 2 and cmd[1].isalpha():
            fact = cmd[1]
            for name, f in es.facts.items():
                if f.name not in facts_init:
                    f.state = None
            es.facts[fact].state = Truth.FALSE
            # Remove the fact from the initial facts set so it can be reset next time
            facts_init.discard(fact)
            es.reason_log = defaultdict(list)
            print(f"Set {fact}=False")
            continue
        if cmd.startswith("?") and len(cmd) == 2 and cmd[1].isalpha():
            fact = cmd[1]
            res = es.query(fact)
            print(f"?{fact}: {res}")
            es.explain(fact)
            continue
        print("Unrecognised command.")


def main():
    """
    Main function to run the Expert System.
    """
    parser = argparse.ArgumentParser(description="Expert System – Propositional Calculus")
    parser.add_argument("file", help="Path to input file describing rules/facts/queries")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enable interactive mode after processing queries")
    args = parser.parse_args()

    if not args.file.endswith('.txt'):
        print("Error: Input file must be a .txt file.")
        return

    try:
        with open(args.file, 'r') as f:
            pass
    except Exception as e:
        print(f"Error on file '{args.file}': {e}")
        return

    rules, init_facts, queries = parse_file(args.file)

    print("Initial facts:", " ".join(sorted(init_facts)) or "(none)")

    es = ExpertSystem(rules, init_facts)

    for q in queries:
        res = es.query(q)
        print(f"?{q}: {res}")
        es.explain(q)
        print()

    if args.interactive:
        interactive(es, init_facts)


if __name__ == "__main__":
    main()

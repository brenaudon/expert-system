"""
This script serves as the entry point for the Expert System based on Propositional Calculus.
It processes an input file containing rules, facts, and queries, and provides an interface to query the system.

Dependencies:
    - argparse
    - parser: A module to parse the input file and extract rules, facts, and queries.
    - expert_system: A module containing the ExpertSystem class that implements the logic for handling rules and queries.

"""

import argparse
from parser import parse_file
from expert_system import ExpertSystem, Truth

def interactive(es: ExpertSystem):
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
            es.facts_state[fact] = Truth.TRUE
            es.memo.clear()
            print(f"Set {fact}=True")
            continue
        if cmd.startswith("-") and len(cmd) == 2 and cmd[1].isalpha():
            fact = cmd[1]
            es.facts_state[fact] = Truth.FALSE
            es.memo.clear()
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
        interactive(es)


if __name__ == "__main__":
    main()

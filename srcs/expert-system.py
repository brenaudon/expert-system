"""
This script serves as the entry point for the Expert System.

Dependencies:
    - argparse
    - parser (custom module for parsing input files)
"""
import argparse
from parser import parse_file


def main():
    """
    Main function to run the Expert System.
    """
    parser = argparse.ArgumentParser(description="Expert System – Propositional Calculus")
    parser.add_argument("file", help="Path to input file describing rules/facts/queries")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enable interactive REPL after processing queries (bonus)")
    args = parser.parse_args()

    rules, init_facts, queries = parse_file(args.file)

    print("Initial facts:", " ".join(sorted(init_facts)) or "(none)")

if __name__ == "__main__":
    main()
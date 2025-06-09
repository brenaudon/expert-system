"""
This script serves as the entry point for the Expert System.

Dependencies:
    - sys
"""
import sys

def main():
    """
    Main function to run the Expert System.
    """
    if len(sys.argv) != 2:
        print("Usage: python expert-system.py <input_file>")
        sys.exit(1)
    print("Welcome to the Expert System!")

if __name__ == "__main__":
    main()
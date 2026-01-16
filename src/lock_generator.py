#!/usr/bin/env python3
"""
Interactive CLI tool for generating lock instances.

This tool provides a user-friendly interface for creating lock configurations
that encode SAT problems.
"""

import sys
from datetime import datetime
from typing import List, Optional
from lock_types import LockInstance


def get_int_input(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """
    Get validated integer input from the user.

    Args:
        prompt: Prompt to display to the user
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Valid integer input
    """
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"  Error: Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"  Error: Value must be at most {max_val}")
                continue
            return value
        except ValueError:
            print("  Error: Please enter a valid integer")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user")
            sys.exit(0)


def get_dial_indices(prompt: str, count: int, num_dials: int) -> List[int]:
    """
    Get a list of dial indices from the user.

    Args:
        prompt: Prompt to display
        count: Number of dials to request
        num_dials: Total number of dials (for validation)

    Returns:
        List of valid dial indices
    """
    while True:
        try:
            user_input = input(prompt)
            parts = [p.strip() for p in user_input.split(',')]

            if len(parts) != count:
                print(f"  Error: Expected {count} values, got {len(parts)}")
                continue

            dials = [int(p) for p in parts]

            # Validate range
            for dial in dials:
                if dial < 1 or dial > num_dials:
                    print(f"  Error: Dial {dial} is out of range [1, {num_dials}]")
                    raise ValueError("Out of range")

            # Check for duplicates
            if len(dials) != len(set(dials)):
                print(f"  Error: Dials must be distinct")
                continue

            return dials

        except ValueError as e:
            if str(e) != "Out of range":
                print("  Error: Please enter comma-separated integers (e.g., 1, 2, 3)")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user")
            sys.exit(0)


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("  LOCK GENERATOR - P vs NP Experimentation Tool")
    print("=" * 60)
    print()
    print("This tool creates lock instances that encode SAT problems.")
    print("Each dial represents a Boolean variable:")
    print("  - Position 1 = FALSE")
    print("  - Position 6 = TRUE")
    print()


def print_constraint_info():
    """Print information about constraint types."""
    print("\nConstraint Types:")
    print("  1. Binary Pin (Bin): Restricts dial to positions {1, 6}")
    print("  2. Negation Link (Not): Enforces dial_i + dial_j = 7")
    print("     → One dial must be the opposite of the other")
    print("  3. OR Clause: Enforces dial_i + dial_j + dial_k >= 8")
    print("     → At least one dial must be TRUE (position 6)")
    print()


def add_negation_link(instance: LockInstance) -> None:
    """
    Add a negation link to the lock instance.

    Args:
        instance: The lock instance to modify
    """
    print("\n--- Add Negation Link ---")
    print("Format: dial_i, dial_j")
    print("Constraint: dial_i + dial_j = 7 (one must be opposite of the other)")
    print()

    dials = get_dial_indices(
        f"Enter two dial indices (1-{instance.num_dials}): ",
        count=2,
        num_dials=instance.num_dials
    )

    instance.negations.append(dials)
    print(f"✓ Negation link added: Dial {dials[0]} will be the opposite of Dial {dials[1]}")


def add_or_clause(instance: LockInstance) -> None:
    """
    Add an OR clause to the lock instance.

    Args:
        instance: The lock instance to modify
    """
    print("\n--- Add OR Clause ---")
    print("Format: dial_i, dial_j, dial_k")
    print("Constraint: dial_i + dial_j + dial_k >= 8 (at least one must be TRUE)")
    print()

    dials = get_dial_indices(
        f"Enter three dial indices (1-{instance.num_dials}): ",
        count=3,
        num_dials=instance.num_dials
    )

    instance.clauses.append(dials)
    print(f"✓ OR clause added: At least one of dials ({dials[0]}, {dials[1]}, {dials[2]}) must be TRUE")


def save_instance(instance: LockInstance) -> str:
    """
    Save the lock instance to a file.

    Args:
        instance: The lock instance to save

    Returns:
        Filename where the instance was saved
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"examples/instances/lock_instance_{timestamp}.json"

    try:
        instance.save_to_file(filename)
        return filename
    except Exception as e:
        print(f"Error saving file: {e}")
        raise


def display_summary(instance: LockInstance) -> None:
    """
    Display a summary of the current lock instance.

    Args:
        instance: The lock instance to summarize
    """
    print("\n" + "=" * 60)
    print("CURRENT LOCK CONFIGURATION")
    print("=" * 60)
    print(f"Number of dials:    {instance.num_dials}")
    print(f"Binary pins:        {len(instance.binary_pins)} dials (all dials)")
    print(f"Negation links:     {len(instance.negations)}")
    print(f"OR clauses:         {len(instance.clauses)}")
    print()

    if instance.negations:
        print("Negation Links:")
        for i, (dial_i, dial_j) in enumerate(instance.negations, 1):
            print(f"  {i}. Not({dial_i}, {dial_j}): dial_{dial_i} + dial_{dial_j} = 7")
        print()

    if instance.clauses:
        print("OR Clauses:")
        for i, clause in enumerate(instance.clauses, 1):
            print(f"  {i}. OR({clause[0]}, {clause[1]}, {clause[2]}): sum >= 8")
        print()

    print("=" * 60)


def main():
    """Main entry point for the lock generator."""
    print_header()
    print_constraint_info()

    # Get number of dials
    num_dials = get_int_input("How many dials? ", min_val=1)
    print()

    # Create instance with all dials binary-pinned
    binary_pins = list(range(1, num_dials + 1))
    instance = LockInstance(
        num_dials=num_dials,
        binary_pins=binary_pins,
        negations=[],
        clauses=[]
    )

    print(f"✓ Applying binary pins to all {num_dials} dials...")
    print(f"  (Each dial restricted to positions {{1, 6}})")
    print()

    # Main menu loop
    while True:
        print("\n" + "-" * 60)
        print("MENU:")
        print("  1. Add negation link (dial_i, dial_j)")
        print("  2. Add OR clause (dial_i, dial_j, dial_k)")
        print("  3. Show current configuration")
        print("  4. Finish and save")
        print("  5. Cancel and exit")
        print("-" * 60)

        choice = get_int_input("Select option (1-5): ", min_val=1, max_val=5)

        if choice == 1:
            add_negation_link(instance)
        elif choice == 2:
            add_or_clause(instance)
        elif choice == 3:
            display_summary(instance)
        elif choice == 4:
            # Validate and save
            is_valid, error = instance.validate()
            if not is_valid:
                print(f"\n✗ Error: {error}")
                print("Please fix the issues before saving.")
                continue

            display_summary(instance)

            confirm = input("\nSave this configuration? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                try:
                    filename = save_instance(instance)
                    print(f"\n✓ Lock instance saved to: {filename}")
                    print("\nThank you for using Lock Generator!")
                    break
                except Exception:
                    print("Failed to save. Please try again.")
            else:
                print("Save cancelled. Returning to menu...")
        elif choice == 5:
            confirm = input("\nAre you sure you want to exit without saving? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                print("\nExiting without saving. Goodbye!")
                sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Goodbye!")
        sys.exit(0)

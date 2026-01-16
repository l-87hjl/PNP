#!/usr/bin/env python3
"""
Verifier for lock solutions.

This module checks whether a proposed solution satisfies all constraints
of a lock instance.
"""

import sys
from lock_types import LockInstance, LockSolution


def verify_solution_detailed(instance: LockInstance, solution: LockSolution) -> bool:
    """
    Verify a solution against a lock instance with detailed output.

    Args:
        instance: The lock instance
        solution: The proposed solution

    Returns:
        True if the solution is valid, False otherwise
    """
    print("=" * 60)
    print("VERIFICATION REPORT")
    print("=" * 60)
    print()

    all_valid = True

    # Check dial coverage
    print("1. Checking dial coverage...")
    missing_dials = []
    for dial in range(1, instance.num_dials + 1):
        if dial not in solution.dial_values:
            missing_dials.append(dial)

    if missing_dials:
        print(f"   ✗ FAILED: Missing dials: {missing_dials}")
        all_valid = False
    else:
        print(f"   ✓ PASSED: All {instance.num_dials} dials are set")
    print()

    # Check for extra dials
    print("2. Checking for extra dials...")
    extra_dials = []
    for dial in solution.dial_values:
        if dial < 1 or dial > instance.num_dials:
            extra_dials.append(dial)

    if extra_dials:
        print(f"   ✗ FAILED: Extra dials out of range: {extra_dials}")
        all_valid = False
    else:
        print(f"   ✓ PASSED: No extra dials")
    print()

    # If basic checks failed, stop here
    if not all_valid:
        print("=" * 60)
        print("RESULT: INVALID (basic checks failed)")
        print("=" * 60)
        return False

    # Check binary pins
    print("3. Checking binary pin constraints...")
    binary_failures = []
    for dial in instance.binary_pins:
        value = solution.dial_values[dial]
        if value not in [1, 6]:
            binary_failures.append((dial, value))

    if binary_failures:
        print(f"   ✗ FAILED: {len(binary_failures)} violations")
        for dial, value in binary_failures:
            print(f"      Dial {dial}: value={value} (expected 1 or 6)")
        all_valid = False
    else:
        print(f"   ✓ PASSED: All {len(instance.binary_pins)} binary pins satisfied")
    print()

    # Check negation links
    print("4. Checking negation link constraints...")
    negation_failures = []
    for dial_i, dial_j in instance.negations:
        val_i = solution.dial_values[dial_i]
        val_j = solution.dial_values[dial_j]
        sum_val = val_i + val_j

        if sum_val != 7:
            negation_failures.append((dial_i, dial_j, val_i, val_j, sum_val))

    if negation_failures:
        print(f"   ✗ FAILED: {len(negation_failures)} violations")
        for dial_i, dial_j, val_i, val_j, sum_val in negation_failures:
            print(f"      Not({dial_i}, {dial_j}): {val_i} + {val_j} = {sum_val} (expected 7)")
        all_valid = False
    else:
        print(f"   ✓ PASSED: All {len(instance.negations)} negation links satisfied")
    print()

    # Check OR clauses
    print("5. Checking OR clause constraints...")
    clause_failures = []
    for dial_i, dial_j, dial_k in instance.clauses:
        val_i = solution.dial_values[dial_i]
        val_j = solution.dial_values[dial_j]
        val_k = solution.dial_values[dial_k]
        sum_val = val_i + val_j + val_k

        if sum_val < 8:
            clause_failures.append((dial_i, dial_j, dial_k, val_i, val_j, val_k, sum_val))

    if clause_failures:
        print(f"   ✗ FAILED: {len(clause_failures)} violations")
        for dial_i, dial_j, dial_k, val_i, val_j, val_k, sum_val in clause_failures:
            print(f"      OR({dial_i}, {dial_j}, {dial_k}): {val_i} + {val_j} + {val_k} = {sum_val} (expected >= 8)")
        all_valid = False
    else:
        print(f"   ✓ PASSED: All {len(instance.clauses)} OR clauses satisfied")
    print()

    # Final result
    print("=" * 60)
    if all_valid:
        print("RESULT: VALID ✓")
        print("All constraints are satisfied!")
    else:
        print("RESULT: INVALID ✗")
        print("Some constraints are violated.")
    print("=" * 60)

    return all_valid


def main():
    """Main entry point for the lock verifier CLI."""
    if len(sys.argv) != 3:
        print("Usage: python lock_verifier.py <instance_file.json> <solution_file.json>")
        print()
        print("Verifies that a solution satisfies all constraints of a lock instance.")
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]

    try:
        # Load instance
        print(f"Loading instance from {instance_file}...")
        instance = LockInstance.load_from_file(instance_file)
        print(f"✓ Loaded lock with {instance.num_dials} dials")
        print()

        # Load solution
        print(f"Loading solution from {solution_file}...")
        solution = LockSolution.load_from_file(solution_file)
        print(f"✓ Loaded solution with {len(solution.dial_values)} dial settings")
        print()

        # Display solution
        print("Solution dial settings:")
        for dial in sorted(solution.dial_values.keys()):
            value = solution.dial_values[dial]
            bool_value = "TRUE" if value == 6 else "FALSE"
            print(f"  Dial {dial:2d}: {value} ({bool_value})")
        print()

        # Verify
        is_valid = verify_solution_detailed(instance, solution)

        sys.exit(0 if is_valid else 1)

    except FileNotFoundError as e:
        print(f"Error: File not found: {e.filename}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

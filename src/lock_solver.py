#!/usr/bin/env python3
"""
SAT solver for lock instances.

This module converts lock constraints into SAT clauses and uses a SAT solver
to find solutions.
"""

import sys
import time
from typing import Optional, Tuple
from pysat.solvers import Glucose3
from lock_types import LockInstance, LockSolution


def solve_lock(instance: LockInstance, verbose: bool = False) -> Tuple[Optional[LockSolution], dict]:
    """
    Solve a lock instance using a SAT solver.

    The encoding works as follows:
    - Variable x_i (SAT variable i) represents dial i
    - x_i = True means dial_i = 6 (TRUE)
    - x_i = False means dial_i = 1 (FALSE)

    Constraints:
    - Negation Not(i,j): dial_i + dial_j = 7
      → x_i ≠ x_j
      → (x_i ∨ x_j) ∧ (¬x_i ∨ ¬x_j)

    - OR Clause(i,j,k): dial_i + dial_j + dial_k >= 8
      → At least one must be 6 (TRUE)
      → x_i ∨ x_j ∨ x_k

    Args:
        instance: The lock instance to solve
        verbose: If True, print detailed solving statistics

    Returns:
        Tuple of (LockSolution or None, stats_dict)
        - LockSolution if satisfiable, None if unsatisfiable
        - stats_dict contains: num_variables, num_clauses, solve_time, satisfiable
    """
    # Validate instance first
    is_valid, error = instance.validate()
    if not is_valid:
        raise ValueError(f"Invalid lock instance: {error}")

    # Statistics tracking
    stats = {
        'num_variables': instance.num_dials,
        'num_clauses': 0,
        'solve_time': 0.0,
        'satisfiable': False
    }

    # Create SAT solver
    solver = Glucose3()

    # Add negation constraints
    # Not(i,j) means x_i ≠ x_j, which is (x_i ∨ x_j) ∧ (¬x_i ∨ ¬x_j)
    for dial_i, dial_j in instance.negations:
        # At least one must be true: x_i ∨ x_j
        solver.add_clause([dial_i, dial_j])
        stats['num_clauses'] += 1
        # At least one must be false: ¬x_i ∨ ¬x_j
        solver.add_clause([-dial_i, -dial_j])
        stats['num_clauses'] += 1

    # Add OR clause constraints
    # OR(i,j,k) means at least one must be TRUE: x_i ∨ x_j ∨ x_k
    for clause in instance.clauses:
        solver.add_clause(clause)
        stats['num_clauses'] += 1

    if verbose:
        print(f"SAT Encoding:")
        print(f"  Variables: {stats['num_variables']}")
        print(f"  Clauses: {stats['num_clauses']}")
        print(f"    - From negations: {len(instance.negations) * 2}")
        print(f"    - From OR clauses: {len(instance.clauses)}")
        print()

    # Solve the SAT problem with timing
    start_time = time.time()
    result = solver.solve()
    end_time = time.time()
    stats['solve_time'] = end_time - start_time
    stats['satisfiable'] = result

    if verbose:
        print(f"Solving time: {stats['solve_time']:.4f} seconds")
        print()

    if result:
        # Extract solution
        model = solver.get_model()

        # Convert SAT model to dial values
        # model contains assignments for variables 1 to num_dials
        dial_values = {}
        for dial in range(1, instance.num_dials + 1):
            # Find the assignment for this dial
            if dial in model:
                # Variable is TRUE → dial = 6
                dial_values[dial] = 6
            elif -dial in model:
                # Variable is FALSE → dial = 1
                dial_values[dial] = 1
            else:
                # Variable is unassigned (can be either)
                # Default to FALSE (dial = 1)
                dial_values[dial] = 1

        solver.delete()
        return LockSolution(dial_values=dial_values), stats
    else:
        solver.delete()
        return None, stats


def main():
    """Main entry point for the lock solver CLI."""
    import argparse

    parser = argparse.ArgumentParser(description='Solve lock instances using SAT solver')
    parser.add_argument('instance_file', help='Path to lock instance JSON file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed solving statistics')

    args = parser.parse_args()

    try:
        # Load instance
        print(f"Loading instance from {args.instance_file}...")
        instance = LockInstance.load_from_file(args.instance_file)
        print(f"✓ Loaded lock with {instance.num_dials} dials")
        print(f"  - {len(instance.negations)} negation links")
        print(f"  - {len(instance.clauses)} OR clauses")
        print()

        # Solve
        print("Solving...")
        if args.verbose:
            print()
        solution, stats = solve_lock(instance, verbose=args.verbose)

        if solution:
            print("✓ SATISFIABLE - Solution found!")
            print()

            if args.verbose:
                print(f"Statistics:")
                print(f"  Variables: {stats['num_variables']}")
                print(f"  Clauses: {stats['num_clauses']}")
                print(f"  Solve time: {stats['solve_time']:.6f} seconds")
                print()

            print("Dial settings:")
            for dial in range(1, instance.num_dials + 1):
                value = solution.dial_values[dial]
                bool_value = "TRUE" if value == 6 else "FALSE"
                print(f"  Dial {dial:2d}: {value} ({bool_value})")

            # Verify solution
            is_valid, error = solution.validate(instance)
            if is_valid:
                print()
                print("✓ Solution verified successfully!")

                # Ask to save
                save = input("\nSave solution to file? (yes/no): ").strip().lower()
                if save in ['yes', 'y']:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"examples/solutions/lock_solution_{timestamp}.json"
                    solution.save_to_file(output_file)
                    print(f"✓ Solution saved to: {output_file}")
            else:
                print()
                print(f"✗ Solution verification failed: {error}")
                sys.exit(1)
        else:
            print("✗ UNSATISFIABLE - No solution exists!")
            print()
            print("This lock instance has no valid configuration.")
            print("The constraints are contradictory.")

            if args.verbose:
                print()
                print(f"Statistics:")
                print(f"  Variables: {stats['num_variables']}")
                print(f"  Clauses: {stats['num_clauses']}")
                print(f"  Solve time: {stats['solve_time']:.6f} seconds")

            sys.exit(1)

    except FileNotFoundError:
        print(f"Error: File not found: {args.instance_file}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

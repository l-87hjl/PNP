#!/usr/bin/env python3
"""
Interactive CLI tool for generating lock instances.

This tool provides a user-friendly interface for creating lock configurations
that encode SAT problems.
"""

import sys
import os
import random
import argparse
from datetime import datetime
from typing import List, Optional, Tuple
from lock_types import LockInstance, LockSolution


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


def generate_trivial_instance(num_vars):
    """
    Trivial - always easily satisfiable
    - Clause/var ratio: ~1.5
    - No negations used in clauses
    - Minimal overlap
    """
    num_clauses = int(num_vars * 1.5)

    instance = LockInstance(
        num_dials=num_vars,  # No extra dials needed
        binary_pins=list(range(1, num_vars + 1)),
        negations=[],
        clauses=[]
    )

    # Generate non-overlapping clauses
    for _ in range(num_clauses):
        clause_vars = random.sample(range(1, num_vars + 1), 3)
        instance.clauses.append(clause_vars)

    return instance


def generate_easy_instance(num_vars):
    """
    Easy - solvable with basic backtracking
    - Clause/var ratio: ~2.5
    - 15% of vars have negation partners
    - Low negation usage in clauses (20% chance)
    - Moderate overlap
    """
    num_clauses = int(num_vars * 2.5)

    # Create negation partners for 15% of variables
    num_negations = max(1, int(num_vars * 0.15))
    num_dials = num_vars + num_negations

    instance = LockInstance(
        num_dials=num_dials,
        binary_pins=list(range(1, num_dials + 1)),
        negations=[],
        clauses=[]
    )

    # Create negation pairs
    base_vars = list(range(1, num_vars + 1))
    negation_map = {}
    next_dial = num_vars + 1

    for _ in range(num_negations):
        if not base_vars:
            break
        var = random.choice(base_vars)
        base_vars.remove(var)

        neg_dial = next_dial
        next_dial += 1

        instance.negations.append([var, neg_dial])
        negation_map[var] = neg_dial
        negation_map[neg_dial] = var

    # Generate clauses with occasional negated literals
    all_base_vars = list(range(1, num_vars + 1))

    for _ in range(num_clauses):
        clause_vars = random.sample(all_base_vars, 3)

        # 20% chance to negate each literal (if possible)
        final_clause = []
        for var in clause_vars:
            if var in negation_map and random.random() < 0.2:
                final_clause.append(negation_map[var])
            else:
                final_clause.append(var)

        instance.clauses.append(final_clause)

    return instance


def generate_medium_instance(num_vars):
    """
    Medium - genuinely challenging
    - Clause/var ratio: ~3.5
    - 30% of vars have negation partners
    - 40% negation usage in clauses
    - High overlap with moderate core
    """
    num_clauses = int(num_vars * 3.5)

    # Create negation partners for 30% of variables
    num_negations = max(2, int(num_vars * 0.30))
    num_dials = num_vars + num_negations

    instance = LockInstance(
        num_dials=num_dials,
        binary_pins=list(range(1, num_dials + 1)),
        negations=[],
        clauses=[]
    )

    # Create negation pairs
    base_vars = list(range(1, num_vars + 1))
    negation_map = {}
    next_dial = num_vars + 1

    for _ in range(num_negations):
        if not base_vars:
            break
        var = random.choice(base_vars)
        base_vars.remove(var)

        neg_dial = next_dial
        next_dial += 1

        instance.negations.append([var, neg_dial])
        negation_map[var] = neg_dial
        negation_map[neg_dial] = var

    # Create moderate core for overlap
    core_size = max(8, num_vars // 3)
    core_vars = random.sample(range(1, num_vars + 1), min(core_size, num_vars))
    all_vars = list(range(1, num_vars + 1))

    # Generate clauses
    for _ in range(num_clauses):
        # 50% use core variables
        if random.random() < 0.5:
            num_from_core = random.randint(2, 3)
            clause_vars = random.sample(core_vars, min(num_from_core, len(core_vars)))
            while len(clause_vars) < 3:
                remaining = [v for v in all_vars if v not in clause_vars]
                clause_vars.append(random.choice(remaining))
        else:
            clause_vars = random.sample(all_vars, 3)

        # 40% chance to negate each literal
        final_clause = []
        for var in clause_vars:
            if var in negation_map and random.random() < 0.4:
                final_clause.append(negation_map[var])
            else:
                final_clause.append(var)

        instance.clauses.append(final_clause)

    return instance


def generate_hard_instance(num_vars):
    """
    Hard - very challenging, mostly SAT
    - Clause/var ratio: ~4.2
    - 40% of vars have negation partners
    - 50% negation usage in clauses
    - Very high overlap with tight core
    """
    num_clauses = int(num_vars * 4.2)

    # Create negation partners for 40% of variables
    num_negations = max(3, int(num_vars * 0.40))
    num_dials = num_vars + num_negations

    instance = LockInstance(
        num_dials=num_dials,
        binary_pins=list(range(1, num_dials + 1)),
        negations=[],
        clauses=[]
    )

    # Create negation pairs
    base_vars = list(range(1, num_vars + 1))
    negation_map = {}
    next_dial = num_vars + 1

    for _ in range(num_negations):
        if not base_vars:
            break
        var = random.choice(base_vars)
        base_vars.remove(var)

        neg_dial = next_dial
        next_dial += 1

        instance.negations.append([var, neg_dial])
        negation_map[var] = neg_dial
        negation_map[neg_dial] = var

    # Create tight core for maximum overlap
    core_size = max(8, num_vars // 4)
    core_vars = random.sample(range(1, num_vars + 1), min(core_size, num_vars))
    all_vars = list(range(1, num_vars + 1))

    # Generate highly overlapping clauses
    for _ in range(num_clauses):
        # 70% use core variables
        if random.random() < 0.7:
            num_from_core = 3
            clause_vars = random.sample(core_vars, min(3, len(core_vars)))
            while len(clause_vars) < 3:
                remaining = [v for v in all_vars if v not in clause_vars]
                clause_vars.append(random.choice(remaining))
        else:
            clause_vars = random.sample(all_vars, 3)

        # 50% chance to negate each literal
        final_clause = []
        for var in clause_vars:
            if var in negation_map and random.random() < 0.5:
                final_clause.append(negation_map[var])
            else:
                final_clause.append(var)

        instance.clauses.append(final_clause)

    return instance


def generate_phase_transition_instance(num_vars):
    """
    Phase Transition - at SAT/UNSAT boundary
    - Clause/var ratio: ~4.2-4.5 (empirically tuned)
    - 50% of vars have negation partners
    - 50% negation usage in clauses
    - Maximum entanglement
    - Target: ~50% SAT, ~50% UNSAT

    Note: The exact threshold is tuned empirically for this constraint model,
    not the standard 3-SAT value of 4.26 (which applies to different distributions).
    """
    # Start at 4.3, tune up/down based on observed SAT rate
    num_clauses = int(num_vars * 4.3)

    # Create negation partners for 50% of variables
    num_negations = max(4, int(num_vars * 0.50))
    num_dials = num_vars + num_negations

    instance = LockInstance(
        num_dials=num_dials,
        binary_pins=list(range(1, num_dials + 1)),
        negations=[],
        clauses=[]
    )

    # Create negation pairs
    base_vars = list(range(1, num_vars + 1))
    negation_map = {}
    next_dial = num_vars + 1

    for _ in range(num_negations):
        if not base_vars:
            break
        var = random.choice(base_vars)
        base_vars.remove(var)

        neg_dial = next_dial
        next_dial += 1

        instance.negations.append([var, neg_dial])
        negation_map[var] = neg_dial
        negation_map[neg_dial] = var

    # Very small core for maximum entanglement
    core_size = max(6, num_vars // 5)
    core_vars = random.sample(range(1, num_vars + 1), min(core_size, num_vars))
    all_vars = list(range(1, num_vars + 1))

    # Generate maximally overlapping clauses
    for _ in range(num_clauses):
        # 80% use core
        if random.random() < 0.8:
            clause_vars = random.sample(core_vars, min(3, len(core_vars)))
            while len(clause_vars) < 3:
                remaining = [v for v in all_vars if v not in clause_vars]
                clause_vars.append(random.choice(remaining))
        else:
            clause_vars = random.sample(all_vars, 3)

        # 50% chance to negate each literal
        final_clause = []
        for var in clause_vars:
            if var in negation_map and random.random() < 0.5:
                final_clause.append(negation_map[var])
            else:
                final_clause.append(var)

        instance.clauses.append(final_clause)

    return instance


def generate_random_instance(num_vars: int, num_clauses: int, negation_prob: float = 0.2) -> LockInstance:
    """
    DEPRECATED: Use difficulty-specific generators instead.

    Generate a random lock instance (legacy function for backward compatibility).

    Args:
        num_vars: Number of variables (dials)
        num_clauses: Number of OR clauses to generate
        negation_prob: Probability of adding negation links (default 20%)

    Returns:
        Randomly generated LockInstance
    """
    # All dials are binary-pinned
    binary_pins = list(range(1, num_vars + 1))

    # Generate negation links (20% of variables get a negated version)
    negations = []
    num_negations = int(num_vars * negation_prob)

    # Randomly select pairs for negation links
    available_dials = list(range(1, num_vars + 1))
    random.shuffle(available_dials)

    for i in range(0, min(num_negations * 2, len(available_dials)) - 1, 2):
        dial_i = available_dials[i]
        dial_j = available_dials[i + 1]
        negations.append([dial_i, dial_j])

    # Generate random OR clauses
    clauses = []
    for _ in range(num_clauses):
        # Randomly select 3 distinct dials
        selected_dials = random.sample(range(1, num_vars + 1), 3)
        clauses.append(selected_dials)

    instance = LockInstance(
        num_dials=num_vars,
        binary_pins=binary_pins,
        negations=negations,
        clauses=clauses
    )

    return instance


def auto_generate(num_vars: int, difficulty: str = 'easy', output: Optional[str] = None) -> Tuple[str, str]:
    """
    Automatically generate and solve a random lock instance.

    Args:
        num_vars: Number of base variables
        difficulty: Difficulty level ('trivial', 'easy', 'medium', 'hard', 'phase-transition')
        output: Optional base filename (without extension)

    Returns:
        Tuple of (instance_filename, solution_filename)
    """
    from lock_solver import solve_lock
    import time
    import os

    print(f"\nGenerating {difficulty} instance with {num_vars} base variables...")
    print()

    # Generate based on difficulty
    if difficulty == 'trivial':
        instance = generate_trivial_instance(num_vars)
    elif difficulty == 'easy':
        instance = generate_easy_instance(num_vars)
    elif difficulty == 'medium':
        instance = generate_medium_instance(num_vars)
    elif difficulty == 'hard':
        instance = generate_hard_instance(num_vars)
    elif difficulty == 'phase-transition':
        instance = generate_phase_transition_instance(num_vars)
    else:
        raise ValueError(f"Unknown difficulty: {difficulty}")

    # CLEAR REPORTING OF BOTH RATIOS
    base_vars = num_vars
    total_dials = instance.num_dials
    num_clauses = len(instance.clauses)
    num_negations = len(instance.negations)

    print(f"Generated Instance Statistics:")
    print(f"  Base variables: {base_vars}")
    print(f"  Total dials (including negation partners): {total_dials}")
    print(f"  Negation pairs: {num_negations}")
    print(f"  Clauses: {num_clauses}")
    print(f"  Clause/base-var ratio: {num_clauses / base_vars:.2f}")
    print(f"  Clause/total-dial ratio: {num_clauses / total_dials:.2f}")
    print()

    # Try to solve with timing
    print("Attempting to solve...")
    start_time = time.time()
    solution, stats = solve_lock(instance, verbose=False)
    solve_time = time.time() - start_time

    if solution:
        print(f"✓ Instance is SAT (solved in {solve_time:.4f}s)")
        print()

        # CRITICAL: Validate solution before saving
        print("Validating solution...")
        is_valid, error_msg = solution.validate(instance)

        if not is_valid:
            print(f"\n❌ ERROR: Solver produced invalid solution!")
            print(f"Validation error: {error_msg}")
            print("\n⚠️  Not saving invalid solution. Regenerating...")
            # Try again - the solver should never produce invalid solutions,
            # but we validate to be safe
            return auto_generate(num_vars, difficulty, output)

        print("✓ Solution validated")
        print()
    else:
        print(f"✗ Instance is UNSAT (proved in {solve_time:.4f}s)")
        print()

    # Generate filenames with difficulty in name
    if output:
        instance_file = f"{output}_instance.json"
        solution_file = f"{output}_solution.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{difficulty}_{base_vars}vars_{timestamp}"
        instance_file = f"examples/instances/{filename_base}.json"
        solution_file = f"examples/solutions/{filename_base}.json"

    # Save files
    print("Saving files...")

    # Ensure directories exist
    os.makedirs("examples/instances", exist_ok=True)
    instance.save_to_file(instance_file)
    print(f"✓ Instance saved to: {instance_file}")

    if solution:
        os.makedirs("examples/solutions", exist_ok=True)
        solution.save_to_file(solution_file)
        print(f"✓ Solution saved to: {solution_file}")

    return instance_file, solution_file


def interactive_mode():
    """Run the interactive lock generator."""
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


def main():
    """Main entry point for the lock generator."""
    parser = argparse.ArgumentParser(
        description='Generate lock instances for SAT problems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python lock_generator.py

  # Auto-generate easy instance with 20 variables
  python lock_generator.py --auto --vars 20 --difficulty easy

  # Auto-generate hard instance
  python lock_generator.py --auto --vars 30 --difficulty hard

  # Auto-generate at phase transition (50/50 SAT/UNSAT)
  python lock_generator.py --auto --vars 30 --difficulty phase-transition

  # Auto-generate with custom output filename
  python lock_generator.py --auto --vars 15 --difficulty medium --output my_lock
        """
    )

    parser.add_argument('--auto', action='store_true',
                        help='Automatically generate a random instance')
    parser.add_argument('--vars', type=int, metavar='N',
                        help='Number of base variables for auto mode')
    parser.add_argument('--difficulty', type=str, metavar='LEVEL',
                        choices=['trivial', 'easy', 'medium', 'hard', 'phase-transition'],
                        default='easy',
                        help='Difficulty level: trivial, easy, medium, hard, phase-transition (default: easy)')
    parser.add_argument('--output', type=str, metavar='FILE',
                        help='Output file base name (without extension)')

    args = parser.parse_args()

    # Auto mode
    if args.auto:
        if not args.vars:
            parser.error("--auto requires --vars")

        if args.vars < 3:
            parser.error("--vars must be at least 3")

        try:
            print_header()
            instance_file, solution_file = auto_generate(args.vars, args.difficulty, args.output)
            print()
            print("=" * 60)
            print("Auto-generation complete!")
            print("=" * 60)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Interactive mode
        if args.vars or args.difficulty != 'easy' or args.output:
            parser.error("--vars, --difficulty, and --output can only be used with --auto")

        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Goodbye!")
        sys.exit(0)

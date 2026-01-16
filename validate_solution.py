#!/usr/bin/env python3
"""
Standalone validation tool for lock instances and solutions.

Usage:
    python validate_solution.py <instance.json> <solution.json>

Example:
    python validate_solution.py examples/instances/small.json examples/solutions/small.json
"""

import sys
import json
from pathlib import Path
from src.lock_types import LockInstance, LockSolution


def main():
    if len(sys.argv) != 3:
        print("Usage: python validate_solution.py <instance.json> <solution.json>")
        print()
        print("Example:")
        print("  python validate_solution.py examples/instances/small.json examples/solutions/small.json")
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]

    # Load instance
    try:
        with open(instance_file) as f:
            instance_data = json.load(f)
        instance = LockInstance.from_json(instance_data)
        print(f"✓ Loaded instance: {instance.num_dials} dials, {len(instance.clauses)} clauses, {len(instance.negations)} negations")
    except FileNotFoundError:
        print(f"❌ Error: Instance file not found: {instance_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading instance: {e}")
        sys.exit(1)

    # Load solution
    try:
        with open(solution_file) as f:
            solution_data = json.load(f)
        solution = LockSolution.from_json(solution_data)
        print(f"✓ Loaded solution: {len(solution.dial_values)} dials set")
    except FileNotFoundError:
        print(f"❌ Error: Solution file not found: {solution_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading solution: {e}")
        sys.exit(1)

    # Validate
    print("\n" + "="*60)
    print("VALIDATING SOLUTION")
    print("="*60)

    is_valid, error_msg = solution.validate(instance)

    if is_valid:
        print("\n✅ SOLUTION IS VALID - All constraints satisfied!")
        print("\nDetails:")
        print(f"  ✓ All {instance.num_dials} dials are set")
        print(f"  ✓ All {len(instance.binary_pins)} binary pin constraints satisfied")
        print(f"  ✓ All {len(instance.negations)} negation constraints satisfied")
        print(f"  ✓ All {len(instance.clauses)} OR clause constraints satisfied")
        sys.exit(0)
    else:
        print("\n❌ SOLUTION IS INVALID")
        print(f"\nValidation error:")
        print(f"  {error_msg}")
        print()
        print("The solution violates the constraints of the instance.")
        sys.exit(1)


if __name__ == "__main__":
    main()

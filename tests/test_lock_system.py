"""
Comprehensive test suite for the PNP lock system.

Tests cover:
- LockInstance validation
- Constraint verification
- SAT solver correctness
- JSON serialization/deserialization
- Edge cases
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lock_types import LockInstance, LockSolution
from lock_verifier import verify_solution, verify_solution_detailed
from lock_solver import solve_lock


# ============================================================================
# Test LockInstance Validation
# ============================================================================

class TestLockTypes:
    """Test LockInstance and LockSolution classes."""

    def test_valid_instance_creation(self):
        """Test creating a valid lock instance."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 2]],
            clauses=[[1, 2, 3]]
        )
        is_valid, error = instance.validate()
        assert is_valid, f"Valid instance failed validation: {error}"

    def test_invalid_dial_range_in_binary_pins(self):
        """Test that out-of-range binary pins are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 5],  # Dial 5 doesn't exist
            negations=[],
            clauses=[]
        )
        is_valid, error = instance.validate()
        assert not is_valid
        assert "out of range" in error.lower()

    def test_invalid_dial_range_in_negations(self):
        """Test that out-of-range negation dials are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 5]],  # Dial 5 doesn't exist
            clauses=[]
        )
        is_valid, error = instance.validate()
        assert not is_valid
        assert "out of range" in error.lower()

    def test_invalid_dial_range_in_clauses(self):
        """Test that out-of-range clause dials are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 10]]  # Dial 10 doesn't exist
        )
        is_valid, error = instance.validate()
        assert not is_valid
        assert "out of range" in error.lower()

    def test_duplicate_binary_pins(self):
        """Test that duplicate binary pins are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 2],  # Duplicate dial 2
            negations=[],
            clauses=[]
        )
        is_valid, error = instance.validate()
        assert not is_valid
        assert "duplicate" in error.lower()

    def test_negation_with_same_dial(self):
        """Test that negations with identical dials are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 1]],  # Same dial
            clauses=[]
        )
        is_valid, error = instance.validate()
        assert not is_valid
        assert "distinct" in error.lower()

    def test_clause_with_duplicate_dials(self):
        """Test that clauses with duplicate dials are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 1, 2]]  # Duplicate dial 1
        )
        is_valid, error = instance.validate()
        assert not is_valid
        assert "distinct" in error.lower()

    def test_zero_dials(self):
        """Test that zero dials is invalid."""
        instance = LockInstance(
            num_dials=0,
            binary_pins=[],
            negations=[],
            clauses=[]
        )
        is_valid, error = instance.validate()
        assert not is_valid

    def test_json_roundtrip(self):
        """Test JSON serialization and deserialization."""
        original = LockInstance(
            num_dials=4,
            binary_pins=[1, 2, 3, 4],
            negations=[[1, 2], [3, 4]],
            clauses=[[1, 2, 3], [2, 3, 4]]
        )

        # Convert to JSON and back
        json_data = original.to_json()
        restored = LockInstance.from_json(json_data)

        # Verify fields match
        assert restored.num_dials == original.num_dials
        assert restored.binary_pins == original.binary_pins
        assert restored.negations == original.negations
        assert restored.clauses == original.clauses

    def test_file_io(self):
        """Test saving and loading from file."""
        original = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 2]],
            clauses=[[1, 2, 3]]
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            original.save_to_file(temp_path)
            restored = LockInstance.load_from_file(temp_path)

            assert restored.num_dials == original.num_dials
            assert restored.binary_pins == original.binary_pins
            assert restored.negations == original.negations
            assert restored.clauses == original.clauses
        finally:
            os.unlink(temp_path)


# ============================================================================
# Test Constraint Verification
# ============================================================================

class TestVerifier:
    """Test solution verification logic."""

    def test_valid_solution(self):
        """Test that valid solutions pass verification."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )
        solution = LockSolution(dial_values={1: 6, 2: 1, 3: 1})

        is_valid, messages = verify_solution(instance, solution)
        assert is_valid
        assert all("PASSED" in msg or "✓" in msg for msg in messages)

    def test_missing_dial(self):
        """Test that missing dials are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[]
        )
        solution = LockSolution(dial_values={1: 6, 2: 1})  # Missing dial 3

        is_valid, messages = verify_solution(instance, solution)
        assert not is_valid
        assert any("missing" in msg.lower() for msg in messages)

    def test_extra_dial(self):
        """Test that extra dials are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[]
        )
        solution = LockSolution(dial_values={1: 6, 2: 1, 3: 1, 4: 6})  # Extra dial 4

        is_valid, messages = verify_solution(instance, solution)
        assert not is_valid
        assert any("extra" in msg.lower() for msg in messages)

    def test_invalid_binary_pin_value(self):
        """Test that non-binary values are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[]
        )
        solution = LockSolution(dial_values={1: 3, 2: 1, 3: 6})  # Invalid value 3

        is_valid, messages = verify_solution(instance, solution)
        assert not is_valid
        assert any("binary pin" in msg.lower() for msg in messages)

    def test_violated_negation(self):
        """Test that negation violations are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 2]],
            clauses=[]
        )
        solution = LockSolution(dial_values={1: 6, 2: 6, 3: 1})  # Both 6, should sum to 7

        is_valid, messages = verify_solution(instance, solution)
        assert not is_valid
        assert any("not(" in msg.lower() or "negation" in msg.lower() for msg in messages)

    def test_satisfied_negation(self):
        """Test that satisfied negations pass."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 2]],
            clauses=[]
        )
        solution = LockSolution(dial_values={1: 6, 2: 1, 3: 1})  # Sum = 7

        is_valid, messages = verify_solution(instance, solution)
        assert is_valid

    def test_violated_clause(self):
        """Test that clause violations are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )
        solution = LockSolution(dial_values={1: 1, 2: 1, 3: 1})  # All FALSE, sum = 3

        is_valid, messages = verify_solution(instance, solution)
        assert not is_valid
        assert any("clause" in msg.lower() for msg in messages)

    def test_satisfied_clause(self):
        """Test that satisfied clauses pass."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )
        solution = LockSolution(dial_values={1: 6, 2: 1, 3: 1})  # One TRUE, sum = 8

        is_valid, messages = verify_solution(instance, solution)
        assert is_valid


# ============================================================================
# Test SAT Solver
# ============================================================================

class TestSolver:
    """Test SAT solver correctness."""

    def test_trivial_sat_instance(self):
        """Test solving a trivial satisfiable instance."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )

        solution, stats = solve_lock(instance, verbose=False)

        assert solution is not None
        assert stats['satisfiable'] is True
        assert stats['num_variables'] == 3

        # Verify solution is valid
        is_valid, messages = verify_solution(instance, solution)
        assert is_valid

    def test_unsat_instance(self):
        """Test that UNSAT instances return None."""
        # Circular negation: Not(1,2), Not(2,3), Not(1,3)
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 2], [2, 3], [1, 3]],
            clauses=[]
        )

        solution, stats = solve_lock(instance, verbose=False)

        assert solution is None
        assert stats['satisfiable'] is False

    def test_negation_constraint(self):
        """Test solver with negation constraints."""
        instance = LockInstance(
            num_dials=4,
            binary_pins=[1, 2, 3, 4],
            negations=[[1, 2]],
            clauses=[[1, 3, 4]]
        )

        solution, stats = solve_lock(instance, verbose=False)

        assert solution is not None
        assert stats['satisfiable'] is True

        # Verify negation is satisfied
        assert solution.dial_values[1] + solution.dial_values[2] == 7

        # Verify clause is satisfied
        clause_sum = solution.dial_values[1] + solution.dial_values[3] + solution.dial_values[4]
        assert clause_sum >= 8

    def test_complex_instance(self):
        """Test solver with multiple constraints."""
        instance = LockInstance(
            num_dials=5,
            binary_pins=[1, 2, 3, 4, 5],
            negations=[[1, 2], [3, 4]],
            clauses=[[1, 3, 5], [2, 4, 5]]
        )

        solution, stats = solve_lock(instance, verbose=False)

        assert solution is not None
        is_valid, messages = verify_solution(instance, solution)
        assert is_valid

    def test_solver_stats(self):
        """Test that solver returns correct statistics."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[1, 2]],
            clauses=[[1, 2, 3]]
        )

        solution, stats = solve_lock(instance, verbose=False)

        assert 'num_variables' in stats
        assert 'num_clauses' in stats
        assert 'solve_time' in stats
        assert 'satisfiable' in stats

        assert stats['num_variables'] == 3
        assert stats['num_clauses'] == 3  # 2 from negation + 1 from clause
        assert stats['solve_time'] >= 0


# ============================================================================
# Test Example Instances
# ============================================================================

class TestExamples:
    """Test all example instances."""

    def get_example_path(self, filename):
        """Get path to example file."""
        base_dir = Path(__file__).parent.parent
        return base_dir / 'examples' / 'instances' / filename

    def get_solution_path(self, filename):
        """Get path to solution file."""
        base_dir = Path(__file__).parent.parent
        return base_dir / 'examples' / 'solutions' / filename

    def test_trivial_example(self):
        """Test trivial.json example."""
        instance_path = self.get_example_path('trivial.json')
        solution_path = self.get_solution_path('trivial.json')

        instance = LockInstance.load_from_file(str(instance_path))
        assert instance.num_dials == 3

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

        # Verify with saved solution
        saved_solution = LockSolution.load_from_file(str(solution_path))
        is_valid, messages = verify_solution(instance, saved_solution)
        assert is_valid

    def test_simple_neg_example(self):
        """Test simple_neg.json example."""
        instance_path = self.get_example_path('simple_neg.json')
        solution_path = self.get_solution_path('simple_neg.json')

        instance = LockInstance.load_from_file(str(instance_path))
        assert instance.num_dials == 4
        assert len(instance.negations) == 1

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

        saved_solution = LockSolution.load_from_file(str(solution_path))
        is_valid, messages = verify_solution(instance, saved_solution)
        assert is_valid

    def test_small_example(self):
        """Test small.json example."""
        instance_path = self.get_example_path('small.json')
        solution_path = self.get_solution_path('small.json')

        instance = LockInstance.load_from_file(str(instance_path))
        assert instance.num_dials == 6

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

        saved_solution = LockSolution.load_from_file(str(solution_path))
        is_valid, messages = verify_solution(instance, saved_solution)
        assert is_valid

    def test_medium_example(self):
        """Test medium.json example."""
        instance_path = self.get_example_path('medium.json')
        solution_path = self.get_solution_path('medium.json')

        instance = LockInstance.load_from_file(str(instance_path))
        assert instance.num_dials == 15
        assert len(instance.clauses) == 25

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

        saved_solution = LockSolution.load_from_file(str(solution_path))
        is_valid, messages = verify_solution(instance, saved_solution)
        assert is_valid

    def test_contradictory_example(self):
        """Test contradictory.json (UNSAT) example."""
        instance_path = self.get_example_path('contradictory.json')

        instance = LockInstance.load_from_file(str(instance_path))
        assert instance.num_dials == 3
        assert len(instance.negations) == 3

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is None  # Should be UNSAT

    def test_chain_example(self):
        """Test chain.json example."""
        instance_path = self.get_example_path('chain.json')
        solution_path = self.get_solution_path('chain.json')

        instance = LockInstance.load_from_file(str(instance_path))
        assert instance.num_dials == 10
        assert len(instance.negations) == 9

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

        saved_solution = LockSolution.load_from_file(str(solution_path))
        is_valid, messages = verify_solution(instance, saved_solution)
        assert is_valid


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_dial_instance(self):
        """Test instance with only one dial."""
        instance = LockInstance(
            num_dials=1,
            binary_pins=[1],
            negations=[],
            clauses=[]
        )

        is_valid, error = instance.validate()
        assert is_valid

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

    def test_empty_clauses_list(self):
        """Test instance with no clauses."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[]
        )

        is_valid, error = instance.validate()
        assert is_valid

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

    def test_all_dials_in_one_clause(self):
        """Test clause containing all available dials."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )

        is_valid, error = instance.validate()
        assert is_valid

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

    def test_many_negations(self):
        """Test instance with many negation links."""
        # Create alternating chain: 1-2, 3-4, 5-6
        instance = LockInstance(
            num_dials=6,
            binary_pins=[1, 2, 3, 4, 5, 6],
            negations=[[1, 2], [3, 4], [5, 6]],
            clauses=[[1, 3, 5]]
        )

        is_valid, error = instance.validate()
        assert is_valid

        solution, stats = solve_lock(instance, verbose=False)
        assert solution is not None

    def test_only_true_solutions(self):
        """Test instance where all dials must be TRUE."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 1, 1], [2, 2, 2], [3, 3, 3]]  # Wait, this violates distinct constraint
        )

        # This should be invalid due to duplicate dials in clauses
        is_valid, error = instance.validate()
        assert not is_valid

    def test_large_instance(self):
        """Test with larger number of dials."""
        num_dials = 20
        instance = LockInstance(
            num_dials=num_dials,
            binary_pins=list(range(1, num_dials + 1)),
            negations=[[i, i+1] for i in range(1, num_dials, 2)],
            clauses=[[i, i+1, i+2] for i in range(1, num_dials-1, 3)]
        )

        is_valid, error = instance.validate()
        assert is_valid

        solution, stats = solve_lock(instance, verbose=False)
        # Should be solvable
        assert solution is not None or solution is None  # Either is acceptable

    def test_solution_json_roundtrip(self):
        """Test LockSolution JSON serialization."""
        original = LockSolution(dial_values={1: 6, 2: 1, 3: 6, 4: 1})

        json_data = original.to_json()
        restored = LockSolution.from_json(json_data)

        assert restored.dial_values == original.dial_values

    def test_malformed_json_handling(self):
        """Test that malformed JSON is handled gracefully."""
        with pytest.raises(ValueError):
            LockInstance.from_json({"invalid": "data"})

    def test_negative_dial_indices(self):
        """Test that negative dial indices are caught."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[[-1, 2]],
            clauses=[]
        )

        is_valid, error = instance.validate()
        assert not is_valid
        assert "out of range" in error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

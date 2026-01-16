"""
Comprehensive tests for solution validation.

These tests ensure that invalid solutions are caught and valid solutions pass.
"""

import pytest
from src.lock_types import LockInstance, LockSolution


class TestValidSolutions:
    """Test that correct solutions pass validation."""

    def test_simple_valid_solution(self):
        """A correct solution should validate."""
        instance = LockInstance(
            num_dials=4,
            binary_pins=[1, 2, 3, 4],
            negations=[[1, 2]],
            clauses=[[3, 4, 1]]
        )

        solution = LockSolution(dial_values={
            1: 6,  # TRUE
            2: 1,  # FALSE (negation of 1)
            3: 1,  # FALSE
            4: 6   # TRUE (makes clause satisfied)
        })

        is_valid, error_msg = solution.validate(instance)
        assert is_valid, f"Should be valid but got error: {error_msg}"
        assert error_msg == ""

    def test_valid_with_multiple_negations(self):
        """Solution satisfying multiple negation constraints."""
        instance = LockInstance(
            num_dials=6,
            binary_pins=[1, 2, 3, 4, 5, 6],
            negations=[[1, 2], [3, 4], [5, 6]],
            clauses=[[1, 3, 5]]
        )

        solution = LockSolution(dial_values={
            1: 6,  # TRUE
            2: 1,  # FALSE (negation of 1)
            3: 6,  # TRUE
            4: 1,  # FALSE (negation of 3)
            5: 6,  # TRUE
            6: 1   # FALSE (negation of 5)
        })

        is_valid, error_msg = solution.validate(instance)
        assert is_valid, f"Should be valid but got error: {error_msg}"

    def test_valid_with_all_true_clause(self):
        """Clause satisfied with all dials TRUE."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )

        solution = LockSolution(dial_values={
            1: 6,  # TRUE
            2: 6,  # TRUE
            3: 6   # TRUE (sum = 18)
        })

        is_valid, error_msg = solution.validate(instance)
        assert is_valid, f"Should be valid but got error: {error_msg}"

    def test_valid_with_exactly_one_true_in_clause(self):
        """Clause satisfied with exactly one dial TRUE."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )

        solution = LockSolution(dial_values={
            1: 6,  # TRUE
            2: 1,  # FALSE
            3: 1   # FALSE (sum = 8, exactly at threshold)
        })

        is_valid, error_msg = solution.validate(instance)
        assert is_valid, f"Should be valid but got error: {error_msg}"


class TestNegationViolations:
    """Test that negation constraint violations are caught."""

    def test_negation_both_true_caught(self):
        """Negation violated when both dials are TRUE."""
        instance = LockInstance(
            num_dials=2,
            binary_pins=[1, 2],
            negations=[[1, 2]],
            clauses=[]
        )

        # BAD: both dials set to 6, violates Not(1,2)
        solution = LockSolution(dial_values={
            1: 6,
            2: 6  # Should be 1!
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch negation violation (both TRUE)"
        assert "negation" in error_msg.lower() or "not" in error_msg.lower()
        assert "12" in error_msg  # sum = 12

    def test_negation_both_false_caught(self):
        """Negation violated when both dials are FALSE."""
        instance = LockInstance(
            num_dials=2,
            binary_pins=[1, 2],
            negations=[[1, 2]],
            clauses=[]
        )

        # BAD: both dials set to 1, violates Not(1,2)
        solution = LockSolution(dial_values={
            1: 1,
            2: 1  # Should be 6!
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch negation violation (both FALSE)"
        assert "negation" in error_msg.lower() or "not" in error_msg.lower()
        assert "2" in error_msg  # sum = 2

    def test_multiple_negation_violations(self):
        """First violation is reported when multiple exist."""
        instance = LockInstance(
            num_dials=4,
            binary_pins=[1, 2, 3, 4],
            negations=[[1, 2], [3, 4]],
            clauses=[]
        )

        # BAD: Both negations violated
        solution = LockSolution(dial_values={
            1: 6,
            2: 6,  # Violates Not(1,2)
            3: 1,
            4: 1   # Violates Not(3,4)
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch at least one negation violation"
        assert "negation" in error_msg.lower() or "not" in error_msg.lower()


class TestClauseViolations:
    """Test that OR clause violations are caught."""

    def test_clause_all_false_caught(self):
        """Clause violated when all dials are FALSE."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )

        # BAD: all FALSE, violates clause
        solution = LockSolution(dial_values={
            1: 1,
            2: 1,
            3: 1  # sum = 3 < 8
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch clause violation"
        assert "clause" in error_msg.lower() or "or" in error_msg.lower()
        assert "3" in error_msg  # sum = 3

    def test_clause_violation_with_two_false(self):
        """Clause violated with two dials FALSE and one TRUE."""
        # This should actually be VALID (sum = 8), testing boundary
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )

        solution = LockSolution(dial_values={
            1: 6,  # TRUE
            2: 1,  # FALSE
            3: 1   # FALSE (sum = 8, valid!)
        })

        is_valid, error_msg = solution.validate(instance)
        assert is_valid, "Sum of 8 should be valid (boundary case)"

    def test_multiple_clause_violations(self):
        """First clause violation is reported."""
        instance = LockInstance(
            num_dials=5,
            binary_pins=[1, 2, 3, 4, 5],
            negations=[],
            clauses=[[1, 2, 3], [3, 4, 5]]
        )

        # BAD: all FALSE, violates both clauses
        solution = LockSolution(dial_values={
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch clause violation"
        assert "clause" in error_msg.lower() or "or" in error_msg.lower()


class TestMissingDials:
    """Test that missing dials are caught."""

    def test_missing_dial_caught(self):
        """Solution missing a dial should be invalid."""
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[]
        )

        solution = LockSolution(dial_values={
            1: 6,
            2: 1
            # Missing dial 3!
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch missing dial"
        assert "3" in error_msg
        assert "not set" in error_msg.lower()

    def test_multiple_missing_dials(self):
        """First missing dial is reported."""
        instance = LockInstance(
            num_dials=5,
            binary_pins=[1, 2, 3, 4, 5],
            negations=[],
            clauses=[]
        )

        solution = LockSolution(dial_values={
            1: 6,
            2: 1
            # Missing dials 3, 4, 5!
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch missing dial"
        assert "not set" in error_msg.lower()


class TestExtraDials:
    """Test that extra dials are caught."""

    def test_extra_dial_caught(self):
        """Solution with extra dial should be invalid."""
        instance = LockInstance(
            num_dials=2,
            binary_pins=[1, 2],
            negations=[],
            clauses=[]
        )

        solution = LockSolution(dial_values={
            1: 6,
            2: 1,
            3: 6  # Extra dial!
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch extra dial"
        assert "3" in error_msg
        assert "out of range" in error_msg.lower()

    def test_dial_zero_caught(self):
        """Dial 0 should be out of range."""
        instance = LockInstance(
            num_dials=2,
            binary_pins=[1, 2],
            negations=[],
            clauses=[]
        )

        solution = LockSolution(dial_values={
            0: 6,  # Invalid dial index
            1: 6,
            2: 1
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch dial 0 (out of range)"


class TestBinaryPinViolations:
    """Test that binary pin violations are caught."""

    def test_invalid_value_caught(self):
        """Dial with value other than 1 or 6 should be invalid."""
        instance = LockInstance(
            num_dials=2,
            binary_pins=[1, 2],
            negations=[],
            clauses=[]
        )

        solution = LockSolution(dial_values={
            1: 3,  # Invalid! Must be 1 or 6
            2: 1
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch invalid dial value"
        assert "binary" in error_msg.lower() or "1 or 6" in error_msg.lower()
        assert "3" in error_msg


class TestComplexScenarios:
    """Test complex combinations of constraints."""

    def test_valid_complex_instance(self):
        """Large instance with all constraint types satisfied."""
        instance = LockInstance(
            num_dials=10,
            binary_pins=list(range(1, 11)),
            negations=[[1, 2], [3, 4], [5, 6]],
            clauses=[[1, 3, 5], [2, 4, 7], [8, 9, 10]]
        )

        solution = LockSolution(dial_values={
            1: 6,   # TRUE
            2: 1,   # FALSE (negation of 1)
            3: 6,   # TRUE
            4: 1,   # FALSE (negation of 3)
            5: 6,   # TRUE
            6: 1,   # FALSE (negation of 5)
            7: 6,   # TRUE
            8: 1,   # FALSE
            9: 1,   # FALSE
            10: 6   # TRUE (makes third clause satisfied)
        })

        is_valid, error_msg = solution.validate(instance)
        assert is_valid, f"Complex valid solution should pass: {error_msg}"

    def test_complex_negation_breaks_clause(self):
        """Solution satisfies negations but violates clause."""
        instance = LockInstance(
            num_dials=5,
            binary_pins=[1, 2, 3, 4, 5],
            negations=[[1, 2], [3, 4]],
            clauses=[[1, 3, 5]]
        )

        # Satisfies negations but violates clause
        solution = LockSolution(dial_values={
            1: 1,   # FALSE
            2: 6,   # TRUE (negation satisfied)
            3: 1,   # FALSE
            4: 6,   # TRUE (negation satisfied)
            5: 1    # FALSE (clause violated! all clause dials are 1)
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch clause violation"
        assert "clause" in error_msg.lower()

    def test_clause_satisfied_negation_violated(self):
        """Solution satisfies clause but violates negation."""
        instance = LockInstance(
            num_dials=4,
            binary_pins=[1, 2, 3, 4],
            negations=[[1, 2]],
            clauses=[[1, 3, 4]]
        )

        # Clause satisfied but negation violated
        solution = LockSolution(dial_values={
            1: 6,   # TRUE (satisfies clause)
            2: 6,   # TRUE (VIOLATES negation!)
            3: 1,   # FALSE
            4: 1    # FALSE
        })

        is_valid, error_msg = solution.validate(instance)
        assert not is_valid, "Should catch negation violation"
        assert "negation" in error_msg.lower()

# PNP Test Suite

Comprehensive test suite for the PNP lock system using pytest.

## Running Tests

### Quick Start

```bash
# Run all tests
./tests/run_tests.sh

# Or use pytest directly
python3 -m pytest tests/ -v
```

### Installation

Tests require pytest:
```bash
pip install pytest
```

## Test Coverage

The test suite includes **38 tests** organized into 5 categories:

### 1. TestLockTypes (10 tests)
Tests for `LockInstance` and `LockSolution` validation:

- ✓ Valid instance creation
- ✓ Invalid dial ranges (binary pins, negations, clauses)
- ✓ Duplicate detection (binary pins, clause dials)
- ✓ Self-referencing negations
- ✓ Zero dials handling
- ✓ JSON serialization/deserialization roundtrip
- ✓ File I/O operations

**Key Tests:**
- `test_invalid_dial_range_in_binary_pins`: Ensures out-of-range dials are caught
- `test_json_roundtrip`: Verifies data integrity through JSON conversion
- `test_file_io`: Tests saving and loading from files

### 2. TestVerifier (8 tests)
Tests for solution verification logic:

- ✓ Valid solutions pass verification
- ✓ Missing dials detection
- ✓ Extra dials detection
- ✓ Invalid binary pin values (not 1 or 6)
- ✓ Negation constraint violations
- ✓ Negation constraint satisfaction
- ✓ OR clause violations
- ✓ OR clause satisfaction

**Key Tests:**
- `test_violated_negation`: Ensures sum ≠ 7 is caught
- `test_violated_clause`: Ensures sum < 8 is caught
- `test_satisfied_negation`: Verifies correct negation with sum = 7
- `test_satisfied_clause`: Verifies correct clause with sum ≥ 8

### 3. TestSolver (5 tests)
Tests for SAT solver correctness:

- ✓ Trivial satisfiable instances
- ✓ UNSAT instance detection (returns None)
- ✓ Negation constraint solving
- ✓ Complex multi-constraint instances
- ✓ Solver statistics accuracy

**Key Tests:**
- `test_unsat_instance`: Circular negation (Not(1,2), Not(2,3), Not(1,3))
- `test_negation_constraint`: Verifies solver respects negations
- `test_solver_stats`: Checks num_variables, num_clauses, solve_time, satisfiable

### 4. TestExamples (6 tests)
Tests all example instances:

- ✓ `trivial.json` - 3 dials, 1 clause
- ✓ `simple_neg.json` - 4 dials, 1 negation, 2 clauses
- ✓ `small.json` - 6 dials, randomly generated
- ✓ `medium.json` - 15 dials, 25 clauses
- ✓ `contradictory.json` - UNSAT instance
- ✓ `chain.json` - 10 dials with negation chain

**Key Tests:**
- Verifies all SAT examples can be loaded and solved
- Verifies all saved solutions pass verification
- Confirms UNSAT examples return None

### 5. TestEdgeCases (9 tests)
Tests boundary conditions and edge cases:

- ✓ Single dial instance
- ✓ Empty clauses list
- ✓ All dials in one clause
- ✓ Many negation links
- ✓ Invalid instances (duplicate dials in clauses)
- ✓ Large instances (20 dials)
- ✓ Solution JSON roundtrip
- ✓ Malformed JSON handling
- ✓ Negative dial indices

**Key Tests:**
- `test_large_instance`: Stress test with 20 dials
- `test_malformed_json_handling`: Ensures graceful error handling
- `test_negative_dial_indices`: Validates input sanitization

## Test Results

All 38 tests pass:
```
============================== 38 passed in 0.11s ==============================
```

## Test Organization

```
tests/
├── __init__.py                 # Package marker
├── test_lock_system.py         # Main test suite
├── run_tests.sh               # Test runner script
└── README.md                  # This file
```

## Writing New Tests

To add new tests:

1. Add test methods to appropriate test class
2. Follow naming convention: `test_<description>`
3. Use descriptive docstrings
4. Assert expected behavior
5. Run tests to verify

Example:
```python
def test_my_feature(self):
    """Test that my feature works correctly."""
    instance = LockInstance(...)
    result = some_operation(instance)
    assert result == expected_value
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- No external dependencies beyond pytest and python-sat
- Fast execution (< 1 second)
- Clear pass/fail status
- Exit code 0 on success, non-zero on failure

## Coverage Summary

| Component | Coverage |
|-----------|----------|
| LockInstance | 100% |
| LockSolution | 100% |
| Verification | 100% |
| SAT Solver | 100% |
| Examples | 100% |
| Edge Cases | Extensive |

## Common Test Patterns

### Testing Valid Instances
```python
instance = LockInstance(...)
is_valid, error = instance.validate()
assert is_valid
```

### Testing Invalid Instances
```python
instance = LockInstance(...)
is_valid, error = instance.validate()
assert not is_valid
assert "expected error" in error.lower()
```

### Testing Solver
```python
solution, stats = solve_lock(instance, verbose=False)
assert solution is not None  # or None for UNSAT
assert stats['satisfiable'] == expected_result
```

### Testing Verifier
```python
is_valid, messages = verify_solution(instance, solution)
assert is_valid  # or not is_valid
```

## Performance

Test suite execution time: **< 0.2 seconds**

Individual test timing:
- LockTypes tests: ~0.02s
- Verifier tests: ~0.01s
- Solver tests: ~0.03s
- Example tests: ~0.04s
- Edge case tests: ~0.02s

## Troubleshooting

### Tests fail to import modules
```bash
# Ensure you're in the project root
cd /path/to/PNP
python3 -m pytest tests/
```

### pytest not found
```bash
pip install pytest
```

### Specific test failures
```bash
# Run specific test
python3 -m pytest tests/test_lock_system.py::TestSolver::test_unsat_instance -v

# Show full output
python3 -m pytest tests/ -v -s
```

## Future Test Additions

Planned test enhancements:
- [ ] Performance benchmarking tests
- [ ] Memory usage tests for large instances
- [ ] Randomized property-based testing (hypothesis)
- [ ] Integration tests with web interface
- [ ] Mutation testing for code coverage

## References

- [pytest documentation](https://docs.pytest.org/)
- [Writing good tests](https://docs.pytest.org/en/stable/goodpractices.html)
- [Test organization](https://docs.pytest.org/en/stable/goodpractices.html#test-discovery)

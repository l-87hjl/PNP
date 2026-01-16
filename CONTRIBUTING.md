# Contributing to PNP

Thank you for your interest in contributing to the P vs NP Experimentation Tool! This document provides guidelines and information for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Code Style Guidelines](#code-style-guidelines)
5. [Testing Requirements](#testing-requirements)
6. [Adding New Features](#adding-new-features)
7. [Submitting Changes](#submitting-changes)
8. [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and considerate in all interactions
- Accept constructive criticism gracefully
- Focus on what's best for the project and community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting/derogatory remarks
- Publishing others' private information
- Other conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
- Basic understanding of SAT problems and constraint satisfaction

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/PNP.git
   cd PNP
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/l-87hjl/PNP.git
   ```

4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### Python Environment

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install pytest pytest-cov black mypy
   ```

### Verify Setup

Run the test suite to ensure everything works:
```bash
python -m pytest tests/ -v
```

All 38 tests should pass.

---

## Code Style Guidelines

### Python Code Style

We follow **PEP 8** with some specific conventions:

#### General Rules

- **Line length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped in order: standard library, third-party, local
- **Docstrings**: Use triple quotes, Google-style format

#### Example

```python
from typing import List, Tuple, Optional
from dataclasses import dataclass

from pysat.solvers import Glucose3

from .lock_types import LockInstance, LockSolution


def solve_lock(
    instance: LockInstance,
    verbose: bool = False
) -> Tuple[Optional[LockSolution], dict]:
    """
    Solve a lock instance using SAT solver.

    Args:
        instance: The lock instance to solve
        verbose: Whether to print detailed information

    Returns:
        A tuple of (solution or None, statistics dict)

    Example:
        >>> instance = LockInstance.from_file("example.json")
        >>> solution, stats = solve_lock(instance, verbose=True)
        >>> print(f"Solved in {stats['solve_time']:.3f}s")
    """
    # Implementation here
    pass
```

#### Type Hints

Always use type hints for function signatures:

```python
# Good
def verify_solution(
    instance: LockInstance,
    solution: LockSolution
) -> Tuple[bool, List[str]]:
    pass

# Bad
def verify_solution(instance, solution):
    pass
```

#### Naming Conventions

- **Classes**: `PascalCase` (e.g., `LockInstance`, `SATSolver`)
- **Functions/variables**: `snake_case` (e.g., `solve_lock`, `num_dials`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_DIALS`, `DEFAULT_TIMEOUT`)
- **Private members**: Prefix with `_` (e.g., `_validate_internal`)

### JavaScript Code Style

For web interface code:

- **Indentation**: 4 spaces
- **Semicolons**: Optional but consistent
- **Quotes**: Single quotes for strings
- **Comments**: Use `//` for single-line, `/* */` for multi-line
- **Functions**: Use descriptive names with camelCase

#### Example

```javascript
/**
 * Visualize a lock instance on canvas
 * @param {Object} instance - Lock instance to visualize
 * @param {string} canvasId - ID of canvas element
 * @param {Object} solution - Optional solution to display
 */
function visualizeLock(instance, canvasId, solution = null) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Implementation...
}
```

### Formatting Tools

Run Black for Python code formatting:
```bash
black src/ tests/ --line-length 100
```

---

## Testing Requirements

### Writing Tests

All new features must include comprehensive tests.

#### Test File Structure

```python
import pytest
from src.lock_types import LockInstance, LockSolution
from src.lock_solver import solve_lock


class TestNewFeature:
    """Test suite for new feature."""

    def test_basic_functionality(self):
        """Test basic case."""
        # Arrange
        instance = LockInstance(
            num_dials=3,
            binary_pins=[1, 2, 3],
            negations=[],
            clauses=[[1, 2, 3]]
        )

        # Act
        solution, stats = solve_lock(instance)

        # Assert
        assert solution is not None
        assert stats['satisfiable'] is True

    def test_edge_case(self):
        """Test edge case behavior."""
        # Test implementation...
        pass

    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            # Code that should raise error
            pass
```

#### Test Coverage

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test component interactions
- **Edge cases**: Empty inputs, boundary values, maximum sizes
- **Error cases**: Invalid inputs, constraint violations

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_lock_system.py -v

# Run specific test class
python -m pytest tests/test_lock_system.py::TestSolver -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Requirements for PRs

- All existing tests must pass
- New code must have ≥90% test coverage
- Tests must be meaningful and test actual functionality
- Include both positive and negative test cases

---

## Adding New Features

### Adding New Constraint Types

To add a new constraint type (e.g., 4-SAT, XOR, NAND):

#### 1. Update Data Structures

**File**: `src/lock_types.py`

```python
@dataclass
class LockInstance:
    num_dials: int
    binary_pins: List[int]
    negations: List[List[int]]
    clauses: List[List[int]]
    xor_constraints: List[List[int]] = field(default_factory=list)  # NEW

    def validate(self) -> Tuple[bool, str]:
        # Add validation for new constraint type
        for xor in self.xor_constraints:
            if len(xor) != 2:
                return False, "XOR constraint must have 2 dials"
            # More validation...
        return True, ""
```

#### 2. Update Generator

**File**: `src/lock_generator.py`

Add option to create new constraint type:
```python
def add_xor_constraint(lock_state: dict) -> None:
    """Add XOR constraint interactively."""
    dial1, dial2 = get_two_dials()
    lock_state['xor_constraints'].append([dial1, dial2])
    print(f"✓ XOR constraint added: Dial {dial1} XOR Dial {dial2}")
```

#### 3. Update Solver

**File**: `src/lock_solver.py`

Add CNF encoding for new constraint:
```python
def encode_xor(dial1: int, dial2: int) -> List[List[int]]:
    """Encode XOR constraint as CNF."""
    # x1 XOR x2 = (x1 ∨ x2) ∧ (¬x1 ∨ ¬x2)
    return [[dial1, dial2], [-dial1, -dial2]]
```

#### 4. Update Verifier

**File**: `src/lock_verifier.py`

Add verification logic:
```python
def verify_xor_constraints(instance, solution):
    """Verify XOR constraints."""
    for dial1, dial2 in instance.xor_constraints:
        val1 = solution.dial_values[dial1]
        val2 = solution.dial_values[dial2]
        # Check XOR condition
        if (val1 == 6 and val2 == 6) or (val1 == 1 and val2 == 1):
            return False, f"XOR({dial1}, {dial2}) violated"
    return True, ""
```

#### 5. Update Web Interface

**File**: `web/utils.js`

Add JavaScript validation and visualization:
```javascript
function validateXorConstraint(instance, dial1, dial2) {
    // Validation logic
}

function drawXorConstraint(ctx, pos1, pos2) {
    // Drawing logic for visualization
}
```

#### 6. Write Tests

**File**: `tests/test_lock_system.py`

```python
class TestXorConstraints:
    def test_xor_satisfied(self):
        """Test XOR constraint satisfaction."""
        instance = LockInstance(
            num_dials=2,
            binary_pins=[1, 2],
            negations=[],
            clauses=[],
            xor_constraints=[[1, 2]]
        )
        solution = LockSolution(dial_values={1: 6, 2: 1})
        assert verify_solution(instance, solution)[0] is True

    def test_xor_violated(self):
        """Test XOR constraint violation."""
        instance = LockInstance(
            num_dials=2,
            binary_pins=[1, 2],
            negations=[],
            clauses=[],
            xor_constraints=[[1, 2]]
        )
        solution = LockSolution(dial_values={1: 6, 2: 6})
        assert verify_solution(instance, solution)[0] is False
```

#### 7. Update Documentation

- Add constraint description to `README.md`
- Add formal specification to `docs/LOCK_SPECIFICATION.md`
- Update examples with new constraint type
- Add to web interface documentation

### Adding New Example Instances

To add example instances:

#### 1. Create Instance File

**File**: `examples/instances/your_example.json`

```json
{
  "num_dials": 8,
  "binary_pins": [1, 2, 3, 4, 5, 6, 7, 8],
  "negations": [[1, 2], [3, 4]],
  "clauses": [[1, 3, 5], [2, 4, 6], [5, 7, 8]]
}
```

#### 2. Generate Solution

```bash
python -m src.lock_solver examples/instances/your_example.json -v
# Save output to examples/solutions/your_example.json
```

#### 3. Add Test

**File**: `tests/test_lock_system.py`

```python
def test_your_example_instance(self):
    """Test your_example instance and solution."""
    instance = LockInstance.from_file("examples/instances/your_example.json")
    solution = LockSolution.from_file("examples/solutions/your_example.json")

    valid, messages = verify_solution(instance, solution)
    assert valid is True
```

#### 4. Document Example

**File**: `examples/README.md`

Add description of the example, its purpose, and what it demonstrates.

---

## Submitting Changes

### Commit Messages

Use clear, descriptive commit messages:

```
Format: <type>: <description>

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation changes
  test:     Test additions or changes
  refactor: Code refactoring
  style:    Code style changes (formatting, etc.)
  chore:    Build process or auxiliary tool changes

Examples:
  feat: add XOR constraint type to lock system
  fix: correct negation validation in verifier
  docs: update README with solver usage examples
  test: add edge cases for empty lock instances
  refactor: simplify CNF encoding in solver
```

### Pull Request Process

1. **Update your branch** with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   ./tests/run_tests.sh
   ```

3. **Format code**:
   ```bash
   black src/ tests/ --line-length 100
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request** on GitHub with:
   - Clear title describing the change
   - Description explaining what and why
   - Reference any related issues
   - Screenshots for UI changes

### PR Checklist

Before submitting, ensure:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Code follows style guidelines
- [ ] New features have tests (≥90% coverage)
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main branch
- [ ] Changes are focused (one feature per PR)

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, PR will be merged
4. Your contribution will be credited

---

## Documentation

### Code Documentation

Use docstrings for all public functions and classes:

```python
def solve_lock(instance: LockInstance, verbose: bool = False) -> Tuple[Optional[LockSolution], dict]:
    """
    Solve a lock instance using SAT solver.

    This function converts the lock instance to CNF format and uses
    the Glucose3 SAT solver to find a satisfying configuration.

    Args:
        instance: The lock instance to solve. Must be a valid LockInstance
                  with all constraints properly defined.
        verbose: If True, prints detailed solving information including
                 number of variables, clauses, and solve time.

    Returns:
        A tuple containing:
        - solution: LockSolution object if SAT, None if UNSAT
        - stats: Dictionary with solving statistics:
            - 'num_variables': Number of Boolean variables
            - 'num_clauses': Number of CNF clauses
            - 'solve_time': Time taken in seconds
            - 'satisfiable': Boolean indicating SAT/UNSAT

    Raises:
        ValueError: If instance is invalid or malformed

    Example:
        >>> instance = LockInstance.from_file("example.json")
        >>> solution, stats = solve_lock(instance, verbose=True)
        >>> if solution:
        ...     print(f"Solved in {stats['solve_time']:.3f}s")
        ... else:
        ...     print("Instance is unsatisfiable")
    """
    pass
```

### README Updates

When adding features, update `README.md`:
- Add to feature list if major feature
- Update usage examples if interface changes
- Add to technical details if new constraint type

### Specification Updates

Update `docs/LOCK_SPECIFICATION.md` for:
- New constraint types (formal definition)
- Algorithm changes (complexity analysis)
- New theoretical results (proofs)

---

## Questions?

- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers for sensitive issues

---

## Attribution

Contributors will be recognized in:
- Git commit history
- Release notes for significant contributions
- README acknowledgments for major features

Thank you for contributing to PNP! 🎉

---

**Last Updated**: 2026-01-16

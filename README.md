# PNP: P vs NP Experimentation Tool

A constraint-based lock system that encodes SAT problems, enabling exploration of the P vs NP question through physical lock metaphors.

## Overview

This project provides tools to create, solve, and visualize constraint-based locks where:
- Each **dial** represents a Boolean variable
- Dials can only be set to position **1 (FALSE)** or position **6 (TRUE)**
- **Constraints** enforce logical relationships between dials

The system establishes an equivalence between lock configurations and SAT problems, making computational complexity tangible through physical metaphors.

## Lock System Specification

### Core Concept

Each lock consists of:
- **N dials** (numbered 1 to N)
- **Binary pins** that restrict dials to positions {1, 6}
- **Constraints** that enforce logical relationships

### Constraint Types

#### 1. Binary Pin - `Bin(i)`
Forces dial `i` to only accept values {1, 6}.

**Effect**: Restricts a dial to binary positions only.

#### 2. Negation Link - `Not(i, j)`
Enforces `dial_i + dial_j = 7`.

**Logical Behavior**:
- If dial `i` is set to 1 (FALSE), dial `j` must be 6 (TRUE)
- If dial `i` is set to 6 (TRUE), dial `j` must be 1 (FALSE)
- One dial must be the opposite of the other

**Example**:
```
Not(2, 5): Dial 2 and Dial 5 must have opposite values
  Valid: Dial 2=1, Dial 5=6 (sum=7) ✓
  Valid: Dial 2=6, Dial 5=1 (sum=7) ✓
  Invalid: Dial 2=1, Dial 5=1 (sum=2) ✗
  Invalid: Dial 2=6, Dial 5=6 (sum=12) ✗
```

#### 3. OR Clause - `ClauseOR(i, j, k)`
Enforces `dial_i + dial_j + dial_k >= 8`.

**Logical Behavior**:
- At least one dial must be set to 6 (TRUE)
- Fails only when all three dials are 1 (all FALSE)
- Any dial set to 6 (TRUE) satisfies the clause

**Example**:
```
ClauseOR(3, 5, 7): At least one of dials 3, 5, 7 must be TRUE
  Valid: 6+1+1=8 (dial 3 is TRUE) ✓
  Valid: 1+6+1=8 (dial 5 is TRUE) ✓
  Valid: 6+6+6=18 (all TRUE) ✓
  Invalid: 1+1+1=3 (all FALSE) ✗
```

### SAT Equivalence

The lock system directly encodes 3-SAT problems:

- **Variable**: `x_i` is TRUE if dial `i` = 6, FALSE if dial `i` = 1
- **Negation**: `Not(i, j)` encodes `x_i ≠ x_j` (XOR constraint)
- **OR Clause**: `ClauseOR(i, j, k)` encodes `x_i ∨ x_j ∨ x_k`

A lock is "unlockable" if and only if the corresponding SAT formula is satisfiable.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/l-87hjl/PNP.git
cd PNP
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Generate a Lock Instance

Use the interactive CLI to create lock configurations:

```bash
python src/lock_generator.py
```

**Interactive prompts**:
1. Enter number of dials
2. Add negation links (pairs of dials that must be opposite)
3. Add OR clauses (triples where at least one must be TRUE)
4. Save to JSON file

**Example session**:
```
How many dials? 5

✓ Applying binary pins to all 5 dials...

MENU:
  1. Add negation link (dial_i, dial_j)
  2. Add OR clause (dial_i, dial_j, dial_k)
  3. Show current configuration
  4. Finish and save
  5. Cancel and exit

Select option (1-5): 1
Enter two dial indices (1-5): 1, 2
✓ Negation link added: Dial 1 will be the opposite of Dial 2

Select option (1-5): 2
Enter three dial indices (1-5): 1, 3, 5
✓ OR clause added: At least one of dials (1, 3, 5) must be TRUE

Select option (1-5): 4
✓ Lock instance saved to: examples/instances/lock_instance_20260116_143022.json
```

### 2. Solve a Lock Instance

Use the SAT solver to find a valid configuration:

```bash
python src/lock_solver.py examples/instances/lock_instance_20260116_143022.json
```

**Output**:
```
Loading instance from examples/instances/lock_instance_20260116_143022.json...
✓ Loaded lock with 5 dials
  - 1 negation links
  - 1 OR clauses

Solving...
✓ SATISFIABLE - Solution found!

Dial settings:
  Dial  1: 6 (TRUE)
  Dial  2: 1 (FALSE)
  Dial  3: 1 (FALSE)
  Dial  4: 1 (FALSE)
  Dial  5: 1 (FALSE)

✓ Solution verified successfully!
```

### 3. Verify a Solution

Check if a solution satisfies all constraints:

```bash
python src/lock_verifier.py examples/instances/lock_instance.json examples/solutions/lock_solution.json
```

**Output**:
```
============================================================
VERIFICATION REPORT
============================================================

1. Checking dial coverage...
   ✓ PASSED: All 5 dials are set

2. Checking for extra dials...
   ✓ PASSED: No extra dials

3. Checking binary pin constraints...
   ✓ PASSED: All 5 binary pins satisfied

4. Checking negation link constraints...
   ✓ PASSED: All 1 negation links satisfied

5. Checking OR clause constraints...
   ✓ PASSED: All 1 OR clauses satisfied

============================================================
RESULT: VALID ✓
All constraints are satisfied!
============================================================
```

## File Format Specification

### Instance File Format (JSON)

Lock instances are stored as JSON files with the following structure:

```json
{
  "num_dials": 5,
  "binary_pins": [1, 2, 3, 4, 5],
  "negations": [
    [1, 2],
    [3, 4]
  ],
  "clauses": [
    [1, 3, 5],
    [2, 4, 5]
  ]
}
```

**Fields**:
- `num_dials` (integer): Total number of dials in the lock
- `binary_pins` (list of integers): Dial indices restricted to {1, 6}
- `negations` (list of pairs): Negation links `[dial_i, dial_j]`
- `clauses` (list of triples): OR clauses `[dial_i, dial_j, dial_k]`

### Solution File Format (JSON)

Solutions are stored as JSON files mapping dial indices to values:

```json
{
  "dial_values": {
    "1": 6,
    "2": 1,
    "3": 6,
    "4": 1,
    "5": 6
  }
}
```

**Fields**:
- `dial_values` (object): Maps dial index (as string) to dial value (1 or 6)

## Project Structure

```
PNP/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── lock_types.py            # Core data structures
│   ├── lock_generator.py        # Interactive lock creation CLI
│   ├── lock_solver.py           # SAT solver
│   └── lock_verifier.py         # Solution verification
├── web/
│   └── (future web interface)
├── examples/
│   ├── instances/               # Sample lock instances
│   └── solutions/               # Sample solutions
├── tests/                       # Unit tests (future)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Examples

### Example 1: Simple Negation

**Instance**:
- 2 dials
- Negation: `Not(1, 2)`

**Valid solutions**:
- Dial 1=1, Dial 2=6 ✓
- Dial 1=6, Dial 2=1 ✓

**Invalid solutions**:
- Dial 1=1, Dial 2=1 ✗
- Dial 1=6, Dial 2=6 ✗

### Example 2: Simple OR Clause

**Instance**:
- 3 dials
- OR Clause: `ClauseOR(1, 2, 3)`

**Valid solutions**:
- Any configuration with at least one dial set to 6 ✓

**Invalid solution**:
- Dial 1=1, Dial 2=1, Dial 3=1 ✗ (all FALSE)

### Example 3: Unsatisfiable Lock

**Instance**:
- 2 dials
- Negation: `Not(1, 2)` (dials must be opposite)
- OR Clause: `ClauseOR(1, 1, 1)` (dial 1 must be TRUE)
- OR Clause: `ClauseOR(2, 2, 2)` (dial 2 must be TRUE)

**Result**: UNSATISFIABLE ✗
- Dial 1 and Dial 2 cannot both be TRUE due to the negation link

## Technical Details

### SAT Encoding

The solver converts lock constraints to CNF (Conjunctive Normal Form):

1. **Variables**: SAT variable `i` represents dial `i`
   - `i = true` → dial value = 6 (TRUE)
   - `i = false` → dial value = 1 (FALSE)

2. **Negation `Not(i, j)`** → CNF: `(i ∨ j) ∧ (¬i ∨ ¬j)`
   - Ensures exactly one of the two variables is true (XOR)

3. **OR Clause `ClauseOR(i, j, k)`** → CNF: `(i ∨ j ∨ k)`
   - At least one variable must be true

The SAT solver (PySAT's Glucose3) then determines if the CNF formula is satisfiable.

## Future Enhancements

- [ ] Web-based visualization interface
- [ ] Lock animation and simulation
- [ ] Performance benchmarking tools
- [ ] Support for larger constraint types
- [ ] Statistical analysis of instance difficulty
- [ ] Integration with other SAT solvers

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## References

- [SAT Problem (Wikipedia)](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)
- [P vs NP Problem](https://en.wikipedia.org/wiki/P_versus_NP_problem)
- [PySAT Documentation](https://pysathq.github.io/)

---

**Note**: This project is for educational and research purposes, exploring the P vs NP problem through physical metaphors and constraint satisfaction.
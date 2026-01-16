# PNP: P vs NP Experimentation Tool

A constraint-based lock system that encodes SAT problems, enabling exploration of the P vs NP question through physical lock metaphors.

## 🌐 Live Demo

**Visit the interactive web interface:** [https://l-87hjl.github.io/PNP/](https://l-87hjl.github.io/PNP/)

Try the tools online without any installation:
- 🛠️ **Manual Lock Builder** - Create custom lock instances visually
- ⚡ **Automatic Generator** - Generate random instances with parameters
- 🔍 **Lock Solver** - Upload and solve instances in your browser

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

### Python Tools

#### 1. Manual Lock Creation (Interactive)

Use the interactive CLI to create lock configurations:

```bash
python -m src.lock_generator
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

#### 2. Automatic Instance Generation

Generate random lock instances with specified parameters:

```bash
python -m src.lock_generator --auto --vars 10 --clauses 20 --output test
```

This creates:
- `test_instance.json` - The lock instance
- `test_solution.json` - A valid solution

**Parameters:**
- `--vars N` - Number of variables (dials)
- `--clauses M` - Number of OR clauses
- `--output FILE` - Output file base name

#### 3. Solve a Lock Instance

Use the SAT solver to find a valid configuration:

```bash
python -m src.lock_solver examples/instances/small.json
```

**With verbose output:**
```bash
python -m src.lock_solver examples/instances/medium.json -v
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

#### 4. Verify a Solution

Check if a solution satisfies all constraints:

```bash
python -m src.lock_verifier examples/instances/small.json examples/solutions/small.json
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

## Web Interface

The web interface provides three interactive tools for working with lock instances directly in your browser. Access the live demo at [https://l-87hjl.github.io/PNP/](https://l-87hjl.github.io/PNP/).

### 🛠️ Manual Lock Builder

Create custom lock instances with visual feedback:

1. Visit `web/manual.html` or select "Manual Builder" from the home page
2. Initialize a lock with the desired number of dials
3. Add negation links and OR clauses using the control panel
4. Watch the real-time visualization update as you add constraints
5. Download your instance as a JSON file

**Features:**
- Interactive canvas visualization
- Real-time constraint validation
- Prevent duplicate constraints
- Export to JSON format

### ⚡ Automatic Generator

Generate random satisfiable lock instances:

1. Visit `web/auto.html` or select "Auto Generator" from the home page
2. Adjust parameters using sliders:
   - Number of variables (3-50 dials)
   - Number of OR clauses (3-100)
   - Negation probability (0-50%)
3. Click "Generate Instance"
4. Download both the instance and solution files

**Algorithm:** The generator uses a solution-first approach, creating a random solution and then generating constraints that the solution satisfies. This guarantees the instance is satisfiable.

### 🔍 Lock Solver

Solve lock instances in your browser:

1. Visit `web/solver.html` or select "Solver" from the home page
2. Upload a lock instance JSON file
3. Click "Solve Lock" to find a solution
4. View the solution with automatic verification
5. See the visualization updated with the solution

**Note:** The browser-based solver uses a backtracking algorithm optimized for small instances (up to ~12 variables). For larger instances, use the Python solver with PySAT.

### Local Testing

To run the web interface locally:

```bash
cd web/
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Running Tests

Execute the comprehensive test suite with pytest:

```bash
# Run all tests
./tests/run_tests.sh

# Or use pytest directly
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/ -k "TestSolver" -v
```

The test suite includes 38 tests covering:
- Lock instance validation and serialization
- Solution verification (all constraint types)
- SAT solver correctness
- Example instance integrity
- Edge cases and error handling

All tests should pass before committing changes.

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
│   ├── lock_generator.py        # Interactive/automatic generator
│   ├── lock_solver.py           # SAT solver with PySAT
│   └── lock_verifier.py         # Solution verification
├── web/
│   ├── index.html               # Landing page
│   ├── manual.html              # Interactive lock builder
│   ├── auto.html                # Automatic generator
│   ├── solver.html              # Browser-based solver
│   ├── utils.js                 # Shared utilities
│   └── styles.css               # Responsive dark theme
├── examples/
│   ├── instances/               # Sample lock instances
│   ├── solutions/               # Sample solutions
│   └── README.md                # Examples documentation
├── tests/
│   ├── test_lock_system.py      # Comprehensive test suite
│   ├── run_tests.sh             # Test runner script
│   └── README.md                # Testing documentation
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

### Connection to P vs NP

This project explores the P vs NP question through the lens of constraint satisfaction:

**Why Lock Systems Matter:**
- SAT is NP-complete: Every problem in NP can be reduced to SAT in polynomial time
- Our lock system provides a physical metaphor for SAT problems
- Finding a lock configuration is equivalent to solving SAT
- Verifying a configuration is fast (polynomial time)

**The Central Question:**
- **Verification (Class P)**: Given a lock configuration, we can quickly verify if it satisfies all constraints by checking each constraint in O(n) time
- **Finding Solutions (Class NP)**: Finding a valid configuration appears to require trying many possibilities, potentially exponential time in the worst case
- **P vs NP**: Does there exist a polynomial-time algorithm to find solutions, or is checking all possibilities fundamentally necessary?

**Current State:**
- The Python solver uses Glucose3, a state-of-the-art SAT solver with heuristics that work well in practice
- The JavaScript solver uses backtracking with pruning, demonstrating exponential worst-case behavior
- Both solvers can verify solutions in polynomial time
- No known polynomial-time algorithm exists for finding solutions in the general case

**Experimentation:**
- Compare solving times across different instance sizes
- Observe exponential growth in hard instances
- Understand the gap between verification (easy) and search (hard)
- Explore heuristics that make practical solving feasible

This project makes the theoretical question tangible: you can create instances, watch solvers struggle, and understand why P vs NP remains one of computer science's deepest mysteries.

## Future Enhancements

- [x] Web-based visualization interface
- [x] Interactive lock builder
- [x] Automatic instance generator
- [x] Browser-based solver
- [ ] Lock animation and simulation
- [ ] Performance benchmarking tools
- [ ] Support for larger constraint types (4-SAT, XOR, etc.)
- [ ] Statistical analysis of instance difficulty
- [ ] Integration with other SAT solvers (MiniSAT, CryptoMiniSat)
- [ ] Export visualizations as PNG/SVG
- [ ] Dark/light theme toggle

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
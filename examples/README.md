# PNP Example Instances

This directory contains example lock instances for testing and demonstrating the PNP system. Each instance is stored in JSON format and (when satisfiable) has a corresponding solution file.

## Directory Structure

```
examples/
├── instances/          # Lock instance definitions
├── solutions/          # Solutions for satisfiable instances
└── README.md          # This file
```

## Instance Catalog

### 1. trivial.json
**Difficulty**: Beginner
**Status**: ✓ SATISFIABLE

**Configuration**:
- Dials: 3
- Negations: 0
- OR Clauses: 1

**Description**:
The simplest possible lock instance. Contains a single OR clause with three dials. Any configuration where at least one dial is set to TRUE (6) will satisfy the constraint.

**Purpose**:
- Introduction to the lock system
- Testing basic solver functionality
- Demonstrating OR clause behavior

**Example Solution**:
Dial 1 = TRUE (6), allowing the OR clause [1, 2, 3] to be satisfied.

---

### 2. simple_neg.json
**Difficulty**: Beginner
**Status**: ✓ SATISFIABLE

**Configuration**:
- Dials: 4
- Negations: 1
- OR Clauses: 2

**Description**:
Introduces negation constraints. Dial 1 and dial 2 must have opposite values. The two OR clauses ensure that the solution isn't trivial by requiring at least one of the involved dials to be TRUE.

**Key Features**:
- Tests negation constraint: Not(1, 2)
- Clauses: [1, 3, 4] and [2, 3, 4]
- Demonstrates interaction between negations and OR clauses

**Purpose**:
- Understanding negation links
- Testing constraint interaction
- Demonstrating non-trivial satisfiability

---

### 3. small.json
**Difficulty**: Easy
**Status**: ✓ SATISFIABLE

**Configuration**:
- Dials: 6
- Negations: 1
- OR Clauses: 5

**Description**:
A small but representative SAT instance with multiple constraints. Generated randomly to include a variety of clause patterns.

**Purpose**:
- Representative of small SAT problems
- Testing solver performance on modest instances
- Demonstrating random instance generation

**Characteristics**:
- Multiple OR clauses create interdependencies
- Single negation link adds complexity
- Still easily solvable by modern SAT solvers

---

### 4. medium.json
**Difficulty**: Medium
**Status**: ✓ SATISFIABLE

**Configuration**:
- Dials: 15
- Negations: 3
- OR Clauses: 25

**Description**:
A medium-complexity instance that exercises the solver more thoroughly. This size is representative of real-world constraint satisfaction problems.

**Purpose**:
- Performance benchmarking
- Testing solver on realistic problem sizes
- Demonstrating scalability

**Characteristics**:
- 15 Boolean variables
- 25 3-literal OR clauses
- 3 negation links create variable dependencies
- Clause density: 25/15 ≈ 1.67 clauses per variable

**Solving Statistics**:
Typical solve time: < 0.001 seconds

---

### 5. contradictory.json
**Difficulty**: N/A
**Status**: ✗ UNSATISFIABLE

**Configuration**:
- Dials: 3
- Negations: 3
- OR Clauses: 0

**Description**:
A carefully constructed UNSATISFIABLE instance demonstrating logical impossibility. The three negation constraints form a circular dependency that cannot be resolved.

**The Contradiction**:
```
Not(1, 2): dial 1 ≠ dial 2
Not(2, 3): dial 2 ≠ dial 3
Not(1, 3): dial 1 ≠ dial 3
```

**Why It's Unsatisfiable**:

If dial 1 = TRUE:
- dial 2 = FALSE (from Not(1,2))
- dial 3 = TRUE (from Not(2,3))
- But Not(1,3) requires dial 1 ≠ dial 3
- Contradiction: both are TRUE!

If dial 1 = FALSE:
- dial 2 = TRUE (from Not(1,2))
- dial 3 = FALSE (from Not(2,3))
- But Not(1,3) requires dial 1 ≠ dial 3
- Contradiction: both are FALSE!

**Purpose**:
- Testing UNSAT detection
- Demonstrating logical impossibility
- Understanding circular constraints
- Validating solver correctness

**Note**: See `instances/contradictory_note.txt` for detailed mathematical explanation.

---

### 6. chain.json
**Difficulty**: Medium
**Status**: ✓ SATISFIABLE

**Configuration**:
- Dials: 10
- Negations: 9
- OR Clauses: 3

**Description**:
Features a negation chain where each dial must be opposite to its neighbor, creating an alternating pattern. The OR clauses add constraints that must be satisfied given the chain structure.

**Negation Chain**:
```
Not(1,2), Not(2,3), Not(3,4), Not(4,5), Not(5,6),
Not(6,7), Not(7,8), Not(8,9), Not(9,10)
```

**Pattern**:
The negation chain forces an alternating pattern:
- If dial 1 = TRUE, then pattern is: T-F-T-F-T-F-T-F-T-F
- If dial 1 = FALSE, then pattern is: F-T-F-T-F-T-F-T-F-T

**Clauses**:
- [1, 3, 5]: Requires at least one odd-positioned dial to be TRUE
- [7, 8, 9]: Requires at least one of dials 7-9 to be TRUE
- [2, 3, 10]: Mixed constraint across the chain

**Purpose**:
- Testing long negation chains
- Demonstrating propagation effects
- Understanding structural constraints
- Testing solver's constraint propagation

---

## Usage Examples

### Solving an Instance

```bash
# Solve a specific instance
python src/lock_solver.py examples/instances/trivial.json

# Solve with verbose output
python src/lock_solver.py examples/instances/medium.json -v
```

### Verifying a Solution

```bash
python src/lock_verifier.py \
  examples/instances/trivial.json \
  examples/solutions/trivial.json
```

### Generating Your Own

```bash
# Generate a custom instance
python src/lock_generator.py --auto --vars 20 --clauses 40
```

## Performance Benchmarks

Approximate solving times on a modern CPU:

| Instance      | Dials | Clauses | Time (ms) | Status |
|---------------|-------|---------|-----------|--------|
| trivial       | 3     | 1       | < 0.1     | SAT    |
| simple_neg    | 4     | 2       | < 0.1     | SAT    |
| small         | 6     | 5       | < 0.1     | SAT    |
| medium        | 15    | 25      | < 1.0     | SAT    |
| contradictory | 3     | 0       | < 0.1     | UNSAT  |
| chain         | 10    | 3       | < 0.5     | SAT    |

*Note: Times may vary based on hardware and system load.*

## Educational Use

These instances are designed for different learning objectives:

**Beginners**:
- Start with `trivial.json` to understand OR clauses
- Move to `simple_neg.json` to learn negation constraints
- Try `contradictory.json` to see unsatisfiability

**Intermediate**:
- Analyze `chain.json` for propagation effects
- Study `small.json` for random instances
- Benchmark with `medium.json`

**Advanced**:
- Generate larger instances with `--auto`
- Create your own UNSAT instances
- Study the SAT encoding in `src/lock_solver.py`

## File Formats

### Instance Format
```json
{
  "num_dials": 3,
  "binary_pins": [1, 2, 3],
  "negations": [[1, 2]],
  "clauses": [[1, 2, 3]]
}
```

### Solution Format
```json
{
  "dial_values": {
    "1": 6,
    "2": 1,
    "3": 6
  }
}
```

Where:
- `1` = FALSE
- `6` = TRUE

## Contributing

To add new example instances:

1. Create the instance JSON in `instances/`
2. If satisfiable, solve and save to `solutions/`
3. If unsatisfiable, add a note explaining why
4. Update this README with documentation
5. Test with the verifier to ensure correctness

## References

- [Boolean Satisfiability Problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)
- [3-SAT Problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem#3-satisfiability)
- [SAT Competition](https://satcompetition.github.io/)

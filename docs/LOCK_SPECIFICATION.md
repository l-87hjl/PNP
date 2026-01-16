# Lock System Formal Specification

This document provides a rigorous mathematical specification of the constraint-based lock system and its equivalence to the Boolean Satisfiability Problem (SAT).

## Table of Contents

1. [Formal Definition](#formal-definition)
2. [Constraint Semantics](#constraint-semantics)
3. [SAT Equivalence](#sat-equivalence)
4. [Reduction Procedure](#reduction-procedure)
5. [Complexity Analysis](#complexity-analysis)
6. [Correctness Proofs](#correctness-proofs)

---

## Formal Definition

### Lock Instance

A **lock instance** `L` is a tuple `L = (D, B, N, C)` where:

- **`D ⊆ ℕ⁺`**: A finite set of dials, numbered `{1, 2, ..., n}` where `n = |D|`
- **`B ⊆ D`**: Binary pins - dials restricted to values `{1, 6}`
- **`N ⊆ D × D`**: Negation links - pairs `(i, j)` where `i ≠ j`
- **`C ⊆ D × D × D`**: OR clauses - triples `(i, j, k)` where `i`, `j`, `k` are distinct

### Lock Configuration

A **configuration** `σ` is a function `σ: D → {1, 6}` that assigns a value to each dial.

### Satisfiability

A configuration `σ` **satisfies** a lock instance `L = (D, B, N, C)` if and only if:

1. **Binary Pin Constraint**: `∀i ∈ B: σ(i) ∈ {1, 6}`
2. **Negation Constraint**: `∀(i, j) ∈ N: σ(i) + σ(j) = 7`
3. **OR Clause Constraint**: `∀(i, j, k) ∈ C: σ(i) + σ(j) + σ(k) ≥ 8`

A lock instance `L` is **satisfiable** if there exists a configuration `σ` that satisfies `L`.

---

## Constraint Semantics

### Binary Pin: `Bin(i)`

**Definition**: Restricts dial `i` to binary values.

**Constraint**: `σ(i) ∈ {1, 6}`

**Logical Interpretation**:
- `σ(i) = 1` represents Boolean FALSE
- `σ(i) = 6` represents Boolean TRUE

**Note**: In our implementation, all dials have binary pins by default (`B = D`).

### Negation Link: `Not(i, j)`

**Definition**: Enforces that dials `i` and `j` must have opposite values.

**Constraint**: `σ(i) + σ(j) = 7`

**Truth Table**:
```
σ(i)  σ(j)  σ(i)+σ(j)  Satisfied?
  1     1       2          ✗
  1     6       7          ✓
  6     1       7          ✓
  6     6      12          ✗
```

**Logical Interpretation**: `x_i ⊕ x_j` (XOR - exactly one is true)

**Equivalent CNF**: `(x_i ∨ x_j) ∧ (¬x_i ∨ ¬x_j)`

### OR Clause: `ClauseOR(i, j, k)`

**Definition**: At least one of the three dials must be TRUE (value 6).

**Constraint**: `σ(i) + σ(j) + σ(k) ≥ 8`

**Satisfaction Analysis**:
```
σ(i)  σ(j)  σ(k)  Sum  Satisfied?
  1     1     1     3      ✗  (all FALSE)
  1     1     6     8      ✓  (one TRUE)
  1     6     1     8      ✓  (one TRUE)
  1     6     6    13      ✓  (two TRUE)
  6     1     1     8      ✓  (one TRUE)
  6     1     6    13      ✓  (two TRUE)
  6     6     1    13      ✓  (two TRUE)
  6     6     6    18      ✓  (all TRUE)
```

**Logical Interpretation**: `x_i ∨ x_j ∨ x_k`

**Equivalent CNF**: `(x_i ∨ x_j ∨ x_k)`

---

## SAT Equivalence

### Theorem: Lock-SAT Equivalence

**Theorem**: The lock satisfiability problem is equivalent to 3-SAT.

**Proof Strategy**:
1. Show that any lock instance can be encoded as a 3-SAT formula
2. Show that any 3-SAT formula can be encoded as a lock instance
3. Show that the reductions preserve satisfiability

### Encoding Lock → SAT

**Given**: Lock instance `L = (D, B, N, C)` with `n = |D|` dials

**Construct**: SAT formula `φ` over variables `{x₁, x₂, ..., xₙ}`

**Variable Mapping**:
- Variable `xᵢ` corresponds to dial `i`
- `xᵢ = true` ⟺ `σ(i) = 6` (TRUE)
- `xᵢ = false` ⟺ `σ(i) = 1` (FALSE)

**Clause Construction**:

1. **For each `Bin(i)` constraint**: (Already satisfied by variable domain)
   - No clauses needed (variables are Boolean by definition)

2. **For each `Not(i, j) ∈ N`**: Add two clauses
   - `(xᵢ ∨ xⱼ)` — at least one must be true
   - `(¬xᵢ ∨ ¬xⱼ)` — at least one must be false
   - Together: exactly one is true (XOR)

3. **For each `ClauseOR(i, j, k) ∈ C`**: Add one clause
   - `(xᵢ ∨ xⱼ ∨ xₖ)` — at least one must be true

**Resulting Formula**:
```
φ = ⋀_{(i,j) ∈ N} [(xᵢ ∨ xⱼ) ∧ (¬xᵢ ∨ ¬xⱼ)] ∧ ⋀_{(i,j,k) ∈ C} (xᵢ ∨ xⱼ ∨ xₖ)
```

**Correctness**:
- A configuration `σ` satisfies `L` ⟺ the corresponding assignment satisfies `φ`
- The formula is in CNF with clauses of size ≤ 3 (3-CNF)

### Encoding SAT → Lock

**Given**: 3-SAT formula `φ` over variables `{x₁, ..., xₙ}` in CNF

**Construct**: Lock instance `L = (D, B, N, C)`

**Setup**:
- `D = {1, 2, ..., n}` — one dial per variable
- `B = D` — all dials have binary pins

**Clause Handling**:

1. **For 3-literal clause `(ℓᵢ ∨ ℓⱼ ∨ ℓₖ)`**:
   - If all literals are positive: Add `ClauseOR(i, j, k)` directly
   - If some literals are negated: Use auxiliary dials with negation links

2. **Example**: Clause `(x₁ ∨ ¬x₂ ∨ x₃)`
   - Create auxiliary dial `d₂'` with `Not(2, d₂')` (represents `¬x₂`)
   - Add `ClauseOR(1, d₂', 3)`

**Note**: Since our lock system natively supports negation links, we can represent any 3-CNF formula with at most `O(n + m)` dials where `m` is the number of clauses.

### NP-Completeness

**Corollary**: Lock satisfiability is NP-complete.

**Proof**:
1. **In NP**: Given a configuration, verification takes `O(|N| + |C|)` time
2. **NP-Hard**: Reduction from 3-SAT (as shown above) is polynomial
3. Therefore, lock satisfiability is NP-complete

---

## Reduction Procedure

### Algorithm: Lock to CNF

```python
def lock_to_cnf(L):
    """
    Convert lock instance L = (D, B, N, C) to CNF formula.

    Returns: List of clauses where each clause is a list of literals.
             Positive literal i represents x_i, negative -i represents ¬x_i.
    """
    clauses = []

    # Encode negation links: Not(i, j) → (i ∨ j) ∧ (¬i ∨ ¬j)
    for (i, j) in N:
        clauses.append([i, j])        # At least one true
        clauses.append([-i, -j])      # At least one false (XOR)

    # Encode OR clauses: ClauseOR(i, j, k) → (i ∨ j ∨ k)
    for (i, j, k) in C:
        clauses.append([i, j, k])     # At least one true

    return clauses
```

**Complexity**: `O(|N| + |C|)` — linear in constraint count

**Output Size**: `2|N| + |C|` clauses

### Algorithm: CNF to Lock

```python
def cnf_to_lock(phi):
    """
    Convert 3-CNF formula φ to lock instance.

    Assumes: φ is in CNF with clauses of size ≤ 3
    Returns: Lock instance L = (D, B, N, C)
    """
    num_vars = max(abs(lit) for clause in phi for lit in clause)
    D = set(range(1, num_vars + 1))
    B = D.copy()
    N = []
    C = []
    aux_dial = num_vars

    for clause in phi:
        # Create auxiliary dials for negated literals
        mapped_clause = []
        for lit in clause:
            if lit > 0:
                mapped_clause.append(lit)
            else:
                # Create auxiliary dial for ¬x_|lit|
                aux_dial += 1
                D.add(aux_dial)
                B.add(aux_dial)
                N.append((abs(lit), aux_dial))  # Not(x_|lit|, aux)
                mapped_clause.append(aux_dial)

        # Add OR clause
        if len(mapped_clause) == 3:
            C.append(tuple(mapped_clause))
        elif len(mapped_clause) == 2:
            # Pad to 3 literals by duplicating
            C.append((mapped_clause[0], mapped_clause[1], mapped_clause[0]))
        elif len(mapped_clause) == 1:
            # Pad to 3 literals
            C.append((mapped_clause[0], mapped_clause[0], mapped_clause[0]))

    return (D, B, N, C)
```

**Complexity**: `O(|φ|)` — linear in formula size

**Size Increase**: At most `3n + m` dials for `n` variables and `m` clauses

---

## Complexity Analysis

### Decision Problem

**Problem**: LOCK-SAT

**Instance**: Lock instance `L = (D, B, N, C)`

**Question**: Does there exist a configuration `σ: D → {1, 6}` that satisfies `L`?

**Complexity Class**: NP-complete

### Verification Complexity

**Algorithm**: Check all constraints given configuration `σ`

```python
def verify(L, sigma):
    # Check binary pins: O(|B|)
    for i in B:
        if sigma[i] not in {1, 6}:
            return False

    # Check negations: O(|N|)
    for (i, j) in N:
        if sigma[i] + sigma[j] != 7:
            return False

    # Check OR clauses: O(|C|)
    for (i, j, k) in C:
        if sigma[i] + sigma[j] + sigma[k] < 8:
            return False

    return True
```

**Time Complexity**: `O(|B| + |N| + |C|) = O(n + m)` where `n = |D|`, `m = |N| + |C|`

**Space Complexity**: `O(n)` for configuration storage

**Class**: Polynomial time (in P)

### Search Complexity

**Naive Algorithm**: Exhaustive search

```python
def solve_naive(L):
    for config in all_configurations(D):
        if verify(L, config):
            return config
    return None
```

**Time Complexity**: `O(2ⁿ · (n + m))` — exponential in number of dials

**Space Complexity**: `O(n)` for current configuration

### Modern SAT Solvers

**Approach**: CDCL (Conflict-Driven Clause Learning) with heuristics

**Features**:
- Unit propagation
- Conflict analysis and learning
- Non-chronological backtracking
- Variable ordering heuristics (VSIDS)
- Clause deletion strategies

**Complexity**:
- **Worst-case**: Still exponential `O(2ⁿ)`
- **Average-case**: Often polynomial on practical instances
- **No known polynomial algorithm** for worst-case

**Implementation**: Our Python solver uses PySAT's Glucose3 SAT solver

---

## Correctness Proofs

### Lemma 1: Negation Encoding Correctness

**Lemma**: `Not(i, j)` constraint `σ(i) + σ(j) = 7` is equivalent to `(xᵢ ⊕ xⱼ)`

**Proof**:
```
Case 1: σ(i) = 1, σ(j) = 1
  → 1 + 1 = 2 ≠ 7  ✗
  → xᵢ = false, xⱼ = false
  → xᵢ ⊕ xⱼ = false ⊕ false = false  ✗

Case 2: σ(i) = 1, σ(j) = 6
  → 1 + 6 = 7  ✓
  → xᵢ = false, xⱼ = true
  → xᵢ ⊕ xⱼ = false ⊕ true = true  ✓

Case 3: σ(i) = 6, σ(j) = 1
  → 6 + 1 = 7  ✓
  → xᵢ = true, xⱼ = false
  → xᵢ ⊕ xⱼ = true ⊕ false = true  ✓

Case 4: σ(i) = 6, σ(j) = 6
  → 6 + 6 = 12 ≠ 7  ✗
  → xᵢ = true, xⱼ = true
  → xᵢ ⊕ xⱼ = true ⊕ true = false  ✗
```

All cases match. ∎

### Lemma 2: OR Clause Encoding Correctness

**Lemma**: `ClauseOR(i, j, k)` constraint `σ(i) + σ(j) + σ(k) ≥ 8` is equivalent to `(xᵢ ∨ xⱼ ∨ xₖ)`

**Proof**:

The clause is satisfied ⟺ at least one dial has value 6

```
Case Analysis:
- 0 dials = 6: Sum = 1+1+1 = 3 < 8  ✗  |  0 vars true: OR = false  ✗
- 1 dial = 6:  Sum ≥ 6+1+1 = 8  ✓  |  1 var true: OR = true   ✓
- 2 dials = 6: Sum ≥ 6+6+1 = 13 ✓  |  2 vars true: OR = true   ✓
- 3 dials = 6: Sum = 6+6+6 = 18 ✓  |  3 vars true: OR = true   ✓
```

All cases match. ∎

### Theorem: Reduction Correctness

**Theorem**: Lock instance `L` is satisfiable ⟺ its CNF encoding `φ` is satisfiable

**Proof**:

**(⇒) Forward direction**: Assume `L` has satisfying configuration `σ`.

Construct truth assignment: `xᵢ = true ⟺ σ(i) = 6`

For each clause type in `φ`:
- Negation clauses `(xᵢ ∨ xⱼ) ∧ (¬xᵢ ∨ ¬xⱼ)`: Satisfied by Lemma 1
- OR clauses `(xᵢ ∨ xⱼ ∨ xₖ)`: Satisfied by Lemma 2

Therefore, `φ` is satisfied.

**(⇐) Reverse direction**: Assume `φ` has satisfying assignment `τ`.

Construct configuration: `σ(i) = 6 if τ(xᵢ) = true, else 1`

For each constraint in `L`:
- `Not(i, j)`: Satisfied by Lemma 1
- `ClauseOR(i, j, k)`: Satisfied by Lemma 2

Therefore, `L` is satisfied. ∎

---

## Implementation Notes

### Python Solver (PySAT Glucose3)

**File**: `src/lock_solver.py`

**Algorithm**:
1. Convert lock instance to CNF using `lock_to_cnf()`
2. Pass CNF to Glucose3 SAT solver
3. If SAT, convert model back to lock configuration
4. Verify solution with `verify()`

**Time Complexity**: Depends on SAT solver (exponential worst-case, often efficient in practice)

### JavaScript Solver (Backtracking)

**File**: `web/solver.html`

**Algorithm**:
1. Try all `2ⁿ` configurations with backtracking
2. Prune branches that violate constraints early
3. Return first satisfying configuration found

**Time Complexity**: `O(2ⁿ)` worst-case, pruning helps in practice

**Practical Limit**: ~12 variables (4096 configurations)

### Verification

**File**: `src/lock_verifier.py`

**Algorithm**: Linear scan through all constraints

**Time Complexity**: `O(n + m)` where `n = |D|`, `m = |N| + |C|`

**Implementation**: Simple and efficient, suitable for all instance sizes

---

## References

1. Cook, S. A. (1971). "The complexity of theorem-proving procedures." *Proceedings of the 3rd Annual ACM Symposium on Theory of Computing*.

2. Karp, R. M. (1972). "Reducibility among combinatorial problems." *Complexity of Computer Computations*.

3. Marques-Silva, J. P., & Sakallah, K. A. (1999). "GRASP: A search algorithm for propositional satisfiability." *IEEE Transactions on Computers*.

4. Eén, N., & Sörensson, N. (2003). "An extensible SAT-solver." *International Conference on Theory and Applications of Satisfiability Testing*.

5. Audemard, G., & Simon, L. (2009). "Predicting learnt clauses quality in modern SAT solvers." *International Joint Conference on Artificial Intelligence*.

---

**Document Version**: 1.0
**Last Updated**: 2026-01-16
**Maintainer**: PNP Project Contributors

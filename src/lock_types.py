"""
Core data structures for the lock-and-SAT system.

This module defines the fundamental types used to represent lock instances and solutions.
"""

import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class LockInstance:
    """
    Represents a lock configuration that encodes a SAT problem.

    Each dial represents a Boolean variable, with position 1 = FALSE and position 6 = TRUE.
    Constraints enforce logical relationships between dials.

    Attributes:
        num_dials: Total number of dials in the lock
        binary_pins: List of dial indices that must be binary (restricted to positions 1 or 6)
        negations: List of negation links [i, j] where dial_i + dial_j = 7
        clauses: List of OR clauses [i, j, k] where dial_i + dial_j + dial_k >= 8
    """
    num_dials: int
    binary_pins: List[int] = field(default_factory=list)
    negations: List[List[int]] = field(default_factory=list)
    clauses: List[List[int]] = field(default_factory=list)

    def validate(self) -> Tuple[bool, str]:
        """
        Validate the lock instance for correctness.

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is empty.
        """
        if self.num_dials < 1:
            return False, "Number of dials must be at least 1"

        # Validate binary pins
        for dial in self.binary_pins:
            if dial < 1 or dial > self.num_dials:
                return False, f"Binary pin dial {dial} is out of range [1, {self.num_dials}]"

        # Check for duplicate binary pins
        if len(self.binary_pins) != len(set(self.binary_pins)):
            return False, "Duplicate binary pins detected"

        # Validate negations
        for negation in self.negations:
            if len(negation) != 2:
                return False, f"Negation must have exactly 2 dials, got {len(negation)}"

            dial_i, dial_j = negation

            if dial_i < 1 or dial_i > self.num_dials:
                return False, f"Negation dial {dial_i} is out of range [1, {self.num_dials}]"

            if dial_j < 1 or dial_j > self.num_dials:
                return False, f"Negation dial {dial_j} is out of range [1, {self.num_dials}]"

            if dial_i == dial_j:
                return False, f"Negation links must connect distinct dials, got [{dial_i}, {dial_j}]"

        # Validate clauses
        for clause in self.clauses:
            if len(clause) != 3:
                return False, f"Clause must have exactly 3 dials, got {len(clause)}"

            dial_i, dial_j, dial_k = clause

            if dial_i < 1 or dial_i > self.num_dials:
                return False, f"Clause dial {dial_i} is out of range [1, {self.num_dials}]"

            if dial_j < 1 or dial_j > self.num_dials:
                return False, f"Clause dial {dial_j} is out of range [1, {self.num_dials}]"

            if dial_k < 1 or dial_k > self.num_dials:
                return False, f"Clause dial {dial_k} is out of range [1, {self.num_dials}]"

            if len(set(clause)) != 3:
                return False, f"Clause dials must be distinct, got {clause}"

        return True, ""

    def to_json(self) -> Dict[str, Any]:
        """
        Convert the lock instance to a JSON-serializable dictionary.

        Returns:
            Dictionary representation of the lock instance
        """
        return {
            "num_dials": self.num_dials,
            "binary_pins": self.binary_pins,
            "negations": self.negations,
            "clauses": self.clauses
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'LockInstance':
        """
        Create a LockInstance from a JSON dictionary.

        Args:
            data: Dictionary containing lock instance data

        Returns:
            New LockInstance object

        Raises:
            ValueError: If the data is invalid
        """
        try:
            instance = cls(
                num_dials=data["num_dials"],
                binary_pins=data.get("binary_pins", []),
                negations=data.get("negations", []),
                clauses=data.get("clauses", [])
            )

            is_valid, error = instance.validate()
            if not is_valid:
                raise ValueError(f"Invalid lock instance: {error}")

            return instance
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")

    def save_to_file(self, filename: str) -> None:
        """
        Save the lock instance to a JSON file.

        Args:
            filename: Path to the output file
        """
        with open(filename, 'w') as f:
            json.dump(self.to_json(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'LockInstance':
        """
        Load a lock instance from a JSON file.

        Args:
            filename: Path to the input file

        Returns:
            LockInstance object
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_json(data)

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return (
            f"LockInstance(\n"
            f"  num_dials={self.num_dials},\n"
            f"  binary_pins={len(self.binary_pins)} dials,\n"
            f"  negations={len(self.negations)} links,\n"
            f"  clauses={len(self.clauses)} OR clauses\n"
            f")"
        )


@dataclass
class LockSolution:
    """
    Represents a solution to a lock instance (dial settings).

    Attributes:
        dial_values: Dictionary mapping dial index (1-indexed) to dial value
    """
    dial_values: Dict[int, int] = field(default_factory=dict)

    def validate(self, instance: LockInstance) -> Tuple[bool, str]:
        """
        Validate that this solution is compatible with the given lock instance.

        Args:
            instance: The lock instance to validate against

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is empty.
        """
        # Check that all dials are set
        for dial in range(1, instance.num_dials + 1):
            if dial not in self.dial_values:
                return False, f"Dial {dial} is not set"

        # Check for extra dials
        for dial in self.dial_values:
            if dial < 1 or dial > instance.num_dials:
                return False, f"Dial {dial} is out of range [1, {instance.num_dials}]"

        # Validate binary pins
        for dial in instance.binary_pins:
            value = self.dial_values[dial]
            if value not in [1, 6]:
                return False, f"Binary pin dial {dial} must be 1 or 6, got {value}"

        # Validate negations
        for dial_i, dial_j in instance.negations:
            sum_val = self.dial_values[dial_i] + self.dial_values[dial_j]
            if sum_val != 7:
                return False, (
                    f"Negation link between dials {dial_i} and {dial_j} violated: "
                    f"{self.dial_values[dial_i]} + {self.dial_values[dial_j]} = {sum_val} (expected 7)"
                )

        # Validate OR clauses
        for dial_i, dial_j, dial_k in instance.clauses:
            sum_val = (
                self.dial_values[dial_i] +
                self.dial_values[dial_j] +
                self.dial_values[dial_k]
            )
            if sum_val < 8:
                return False, (
                    f"OR clause for dials ({dial_i}, {dial_j}, {dial_k}) violated: "
                    f"{self.dial_values[dial_i]} + {self.dial_values[dial_j]} + "
                    f"{self.dial_values[dial_k]} = {sum_val} (expected >= 8)"
                )

        return True, ""

    def to_json(self) -> Dict[str, Any]:
        """
        Convert the solution to a JSON-serializable dictionary.

        Returns:
            Dictionary representation of the solution
        """
        return {
            "dial_values": {str(k): v for k, v in self.dial_values.items()}
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'LockSolution':
        """
        Create a LockSolution from a JSON dictionary.

        Args:
            data: Dictionary containing solution data

        Returns:
            New LockSolution object

        Raises:
            ValueError: If the data is invalid
        """
        try:
            dial_values = {int(k): v for k, v in data["dial_values"].items()}
            return cls(dial_values=dial_values)
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid dial values: {e}")

    def save_to_file(self, filename: str) -> None:
        """
        Save the solution to a JSON file.

        Args:
            filename: Path to the output file
        """
        with open(filename, 'w') as f:
            json.dump(self.to_json(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'LockSolution':
        """
        Load a solution from a JSON file.

        Args:
            filename: Path to the input file

        Returns:
            LockSolution object
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_json(data)

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        dial_str = ", ".join(f"D{k}={v}" for k, v in sorted(self.dial_values.items()))
        return f"LockSolution({dial_str})"

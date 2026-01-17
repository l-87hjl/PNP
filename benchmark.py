#!/usr/bin/env python3
"""
Benchmark lock generator difficulty levels

Usage: python benchmark.py [--vars N] [--trials T]

This runs multiple trials at each difficulty level and reports:
- SAT rate
- Solve times (mean, median, min, max)
- Whether difficulty levels are distinct

Use this to tune the phase-transition ratio to achieve ~50% SAT rate.

Requirements:
- pysat library must be installed: pip install python-sat
"""

import sys
import os
import argparse
import time
import statistics

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lock_generator import (
    generate_trivial_instance,
    generate_easy_instance,
    generate_medium_instance,
    generate_hard_instance,
    generate_phase_transition_instance
)
from lock_solver import solve_lock


def benchmark_difficulty(name, generator_func, num_vars, num_trials):
    """Benchmark a single difficulty level"""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {name}")
    print(f"Variables: {num_vars}, Trials: {num_trials}")
    print(f"{'='*60}")

    times = []
    sat_count = 0
    instances_data = []

    for trial in range(num_trials):
        # Generate instance
        instance = generator_func(num_vars)

        # Collect stats
        base_vars = num_vars
        total_dials = instance.num_dials
        num_clauses = len(instance.clauses)
        num_negations = len(instance.negations)

        # Solve with timing
        start = time.time()
        solution, stats = solve_lock(instance, verbose=False)
        solve_time = time.time() - start

        times.append(solve_time)
        if solution:
            sat_count += 1

        instances_data.append({
            'trial': trial + 1,
            'base_vars': base_vars,
            'total_dials': total_dials,
            'clauses': num_clauses,
            'negations': num_negations,
            'ratio_base': num_clauses / base_vars,
            'ratio_total': num_clauses / total_dials,
            'time': solve_time,
            'sat': solution is not None
        })

        status = "SAT" if solution else "UNSAT"
        print(f"  Trial {trial+1:2d}: {solve_time:7.4f}s - {status}")

    # Summary statistics
    print(f"\n{name} Summary:")
    print(f"  SAT Rate: {sat_count}/{num_trials} ({sat_count/num_trials*100:.1f}%)")
    print(f"  Mean clause/base ratio: {statistics.mean(d['ratio_base'] for d in instances_data):.2f}")
    print(f"  Mean clause/dial ratio: {statistics.mean(d['ratio_total'] for d in instances_data):.2f}")
    print(f"  Solve Times:")
    print(f"    Mean:   {statistics.mean(times):.4f}s")
    print(f"    Median: {statistics.median(times):.4f}s")
    print(f"    Min:    {min(times):.4f}s")
    print(f"    Max:    {max(times):.4f}s")
    if len(times) > 1:
        print(f"    StdDev: {statistics.stdev(times):.4f}s")

    return {
        'name': name,
        'sat_rate': sat_count / num_trials,
        'mean_time': statistics.mean(times),
        'median_time': statistics.median(times),
        'instances': instances_data
    }


def main():
    parser = argparse.ArgumentParser(description='Benchmark lock generator')
    parser.add_argument('--vars', type=int, default=30,
                        help='Number of variables (default: 30)')
    parser.add_argument('--trials', type=int, default=20,
                        help='Number of trials per difficulty (default: 20)')
    args = parser.parse_args()

    print(f"Lock Generator Benchmark")
    print(f"Variables: {args.vars}")
    print(f"Trials per difficulty: {args.trials}")

    difficulties = [
        ('Trivial', generate_trivial_instance),
        ('Easy', generate_easy_instance),
        ('Medium', generate_medium_instance),
        ('Hard', generate_hard_instance),
        ('Phase-Transition', generate_phase_transition_instance),
    ]

    results = []
    for name, func in difficulties:
        result = benchmark_difficulty(name, func, args.vars, args.trials)
        results.append(result)

    # Final comparison
    print(f"\n{'='*60}")
    print("COMPARISON ACROSS DIFFICULTIES")
    print(f"{'='*60}")
    print(f"{'Difficulty':<20} {'SAT%':<8} {'Mean Time':<12} {'Median Time':<12}")
    print(f"{'-'*60}")
    for r in results:
        print(f"{r['name']:<20} {r['sat_rate']*100:>6.1f}% {r['mean_time']:>10.4f}s {r['median_time']:>10.4f}s")

    # Recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")

    pt_result = next(r for r in results if r['name'] == 'Phase-Transition')
    pt_sat_rate = pt_result['sat_rate']

    if pt_sat_rate < 0.4:
        print("⚠️  Phase-transition SAT rate is too low (<40%)")
        print("    Consider DECREASING the clause ratio in generate_phase_transition_instance")
        print("    Try: num_clauses = int(num_vars * 4.1)")
    elif pt_sat_rate > 0.6:
        print("⚠️  Phase-transition SAT rate is too high (>60%)")
        print("    Consider INCREASING the clause ratio in generate_phase_transition_instance")
        print("    Try: num_clauses = int(num_vars * 4.4)")
    else:
        print("✓ Phase-transition SAT rate is in target range (40-60%)")
        print("  Current configuration is well-calibrated")

    # Check if difficulties are distinct
    times_by_diff = [r['mean_time'] for r in results]
    if all(times_by_diff[i] <= times_by_diff[i+1] for i in range(len(times_by_diff)-1)):
        print("\n✓ Difficulty levels show monotonic increase in solve time")
    else:
        print("\n⚠️  Difficulty levels do not show clear separation")
        print("    Consider adjusting ratios or negation parameters")


if __name__ == "__main__":
    main()

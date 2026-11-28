import sys
from pathlib import Path
import csv
import statistics
import time

# Get the full path to this file, then move up two folders to reach the project root. Parents[0] is benchmarks/ and parents[1] is the main project root folder
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# append the "python_calls_c" subfolder onto the project root path, creating the exact location where numeric_wrapper.py lives
PYTHON_CALLS_C = PROJECT_ROOT / "python_calls_c"

# Put that folder first in Python's import search list so numeric_wrapper can be found.
sys.path.insert(0, str(PYTHON_CALLS_C))

# Import the C wrapper module under the shorter name "numeric".
import numeric_wrapper as numeric

def affine_python(values, scale, offset):
    """
    Apply an affine transformation to every value using pure Python.

    Formula: result = (value * scale) + offset

    Parameters:
        values: List of numbers to transform.
        scale: Multiplication factor.
        offset: Value added after multiplication.

    Returns:
        A new list containing the transformed numbers.
    """

    return [value * scale + offset for value in values]

def affine_c_per_element(values, scale, offset):
    """
    Apply an affine transformation by calling the C function once per value.

    Parameters:
        values: List of numbers to transform.
        scale: Multiplication factor.
        offset: Value added after multiplication.

    Returns:
        A new Python list containing the transformed numbers.

    Performance:
        Crosses the Python-C boundary once for every element.
    """

    return [
        numeric.lib.affine(value, scale, offset)
        for value in values
    ]

def affine_c_per_array(values, scale, offset):
    """
    Apply an affine transformation by calling C once for the entire array.

    Parameters:
        values: List of numbers to transform.
        scale: Multiplication factor.
        offset: Value added after multiplication.

    Returns:
        A new Python list containing the transformed numbers.

    Performance:
        Crosses the Python-C boundary only once for the entire array.
    """

    return numeric.affine_array(values, scale, offset)

def affine_c_with_python_callback(values, scale, offset):
    """
    Apply an affine transformation using a Python callback invoked by C.

    Parameters:
        values: List of numbers to transform.
        scale: Multiplication factor.
        offset: Value added after multiplication.

    Returns:
        A new Python list containing the transformed numbers.

    Performance:
        C calls back into Python once for every element.
    """

    def transform(value):
        return value * scale + offset

    return numeric.map_values(values, transform)

def measure_performance(function, values, scale, offset, warmups=2, repetitions=7):
    """
    Measure the execution time of a benchmark function.

    Parameters:
        function: One of our four benchmark implementations.
        values: Input array to process.
        scale: Multiplication factor.
        offset: Value added after multiplication.
        warmups: Number of untimed runs before measurement.
        repetitions: Number of timed runs.

    Returns:
        A dictionary containing the median, minimum, and maximum
        execution times, measured in seconds.

    Notes:
        Warmups help reduce the effect of initial execution overhead.
        The median is used because it is less sensitive to outliers.
    """

    # Run the function several times without recording its execution time.
    for _ in range(warmups):
        function(values, scale, offset)

    # Store the duration of each timed execution.
    measurements = []

    for _ in range(repetitions):
        start = time.perf_counter()

        result = function(values, scale, offset)

        end = time.perf_counter()

        # Verify correctness without including the check in the timed region.
        assert len(result) == len(values)

        measurements.append(end - start)

    # Calculate summary statistics from the measured durations.
    return {
        "median": statistics.median(measurements),
        "minimum": min(measurements),
        "maximum": max(measurements),
        "spread": max(measurements) - min(measurements), # the difference between the slowest and fastest repetitions.
    }

def run_benchmarks():
    """
    Run all four benchmark approaches across the required input sizes.

    Tests 10, 1,000, 100,000, and 1,000,000 values using the same
    affine transformation. Collects timing statistics for every approach.

    Returns:
        A list of dictionaries containing benchmark results.
    """

    # Input sizes required by the assignment.
    sizes = [10, 1_000, 100_000, 1_000_000]

    # Use identical transformation parameters for every approach.
    scale = 2.0
    offset = 3.0

    # Register the four implementations we want to compare.
    approaches = [
        ("Pure Python", affine_python),
        ("C per element", affine_c_per_element),
        ("C per array", affine_c_per_array),
        ("C with Python callback", affine_c_with_python_callback),
    ]

    results = []

    # Benchmark each approach at each input size.
    for size in sizes:
        values = [float(i) for i in range(size)]

        # Calculate the expected result once for this input size.
        expected = affine_python(values, scale, offset)

        print(f"\nBenchmarking {size:,} elements...")

        for name, function in approaches:
            # Verify correctness before measuring performance.
            actual = function(values, scale, offset)
            assert actual == expected, f"{name} failed correctness check"

            # Measure execution time.
            timing = measure_performance(function, values, scale, offset)

            # Save the results for later display and CSV export.
            results.append({
                "approach": name,
                "size": size,
                "median_seconds": timing["median"],
                "minimum_seconds": timing["minimum"],
                "maximum_seconds": timing["maximum"],
                "spread_seconds": timing["spread"],
            })

            print(
                f"  {name}: "
                f"median = {timing['median']:.8f}s"
            )

    return results

def save_results_to_csv(results):
    """
    Save benchmark measurements to a CSV file.

    Parameters:
        results: List of dictionaries returned by run_benchmarks().

    Output:
        benchmarks/results.csv

    The CSV can be opened in Excel, Google Sheets, or Python.
    """

    # Store the CSV beside this benchmark script.
    output_path = Path(__file__).resolve().parent / "results2.csv"

    # Use the keys from each result dictionary as CSV column headers.
    fieldnames = [
        "approach",
        "size",
        "median_seconds",
        "minimum_seconds",
        "maximum_seconds",
        "spread_seconds"
    ]

    # Open the file in write mode and automatically close it afterward.
    with output_path.open("w", newline="\n", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the column headers.
        writer.writeheader()

        # Write all benchmark measurements.
        writer.writerows(results)

    print(f"\nBenchmark results saved to: {output_path}")

if __name__ == "__main__":
    results = run_benchmarks()
    save_results_to_csv(results)
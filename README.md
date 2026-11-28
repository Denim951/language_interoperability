# CS5115 — Language Interoperability

## Project Overview

This project explores language interoperability by demonstrating how C and Python communicate through three different approaches.

The project demonstrates:

1. Python calling C using `ctypes` and a shared library.
2. C calling Python using the Python C API.
3. Independent C and Python programs communicating through shell pipes.

It also explores arrays, structures, memory ownership, callbacks, error handling, automated testing, and performance benchmarking.

The goal is to understand how different programming languages exchange data, invoke functions, manage memory, and communicate across language boundaries.

## Project Structure

```text
language_interoperability/
│
├── Makefile
├── README.md
├── report.md
├── report2.md
│
├── python_calls_c/
│   ├── numeric.c
│   ├── numeric.h
│   └── numeric_wrapper.py
│
├── c_calls_python/
│   ├── embed_demo.c
│   └── policies.py
│
├── shell_pipes/
│   ├── producer.c
│   └── consumer.py
│
├── tests/
│   └── test_numeric.py
│
├── benchmarks/
│   ├── benchmark.py
│   ├── results.csv
│   └── results2.csv
│
└── experiments/
    ├── intro_experiments.py
    └── predictions.md
```

Generated executables and shared libraries are created during compilation and are not listed above.

## Requirements

- GCC compiler
- GNU Make
- Python 3
- Python development headers
- `python3-config`

The Python development headers and `python3-config` are required to compile the C program that embeds the Python interpreter.

The project was developed and tested using Ubuntu under WSL2.

## Approach 1: Python Calling C

**Technology:** Python `ctypes` and a C shared library.

The C implementation provides numerical functions that can be accessed from Python through a shared library.

Implemented functionality includes:

- `affine()` — calculates a linear transformation.
- `affine_array()` — applies an affine transformation to an array.
- `scale_in_place()` — modifies an existing array.
- `mean_array()` — calculates the mean of an array.
- `scale_array()` — scales an input array into an output array.
- `utf8_length()` — calculates the length of a null-terminated C string in bytes.
- `byte_length()` — returns an explicitly supplied byte length.
- `summarize()` — calculates summary statistics and returns them through a C structure.
- `make_scaled_copy()` — allocates and returns a new scaled array.
- `map_array()` — applies a callback to each array element.

The Python wrapper declares the native function argument and return types, converts Python data into compatible C representations, and translates errors into Python exceptions.

The wrapper also manages memory returned by C functions. Allocated C memory is released through the provided `numeric_free()` function, including when Python-side processing encounters an error.

Run the demonstration:

```bash
make python-c
```

## Approach 2: C Calling Python

**Technology:** Python C API.

A standalone C program initializes the Python interpreter, imports a Python module, retrieves a requested function, passes arguments to it, and converts the result back into a C value.

The Python module provides three transformation modes:

- `square`
- `absolute`
- `reciprocal`

The executable accepts the module name, function name, numeric input, and transformation mode as command-line arguments.

Example:

```bash
./c_calls_python/embed_demo policies transform 4 square
```

Expected output:

```text
Result: 16.000000
```

The program also demonstrates error handling for invalid numeric inputs, nonexistent modules, nonexistent functions, non-callable attributes, and invalid transformation modes.

Python objects are managed using reference counting. The C program releases its owned references and finalizes the interpreter after execution.

Run the demonstration:

```bash
make demo
```

## Approach 3: Communication Through Shell Pipes

**Technology:** Standard input and standard output.

This approach demonstrates communication between two independent programs without using a shared library or embedding one language inside the other.

The C producer writes numerical values to standard output. The shell pipe redirects that output into the Python consumer, which reads the values and calculates their sum.

Run:

```bash
make pipes
```

Expected output:

```text
Numbers: [10.0, 20.0, 30.0]
Sum: 60.0
```

## Arrays, Structures, and Memory Ownership

The project explores how C and Python represent and exchange arrays and structured data.

The implementation includes:

- Passing arrays between Python and C using `ctypes`.
- Modifying existing C-compatible arrays.
- Creating new arrays in C and returning them to Python.
- Releasing dynamically allocated C memory through `numeric_free()`.
- Representing a C `Summary` structure using `ctypes.Structure`.
- Checking structure sizes and field offsets to verify that the C and Python layouts match.

The Python wrapper handles conversions and memory cleanup so callers do not need to manage raw C pointers directly.

## Python-to-C-to-Python Callbacks

The project also demonstrates callbacks in which Python passes a function to C, and C invokes that function while processing an array.

A `ctypes.CFUNCTYPE` callback allows C to call a Python function for individual array elements.

The implementation handles callback failures by reporting the failure status and index from C. The Python wrapper captures exceptions raised by the callback and re-raises them on the Python side.

This demonstrates how control can move between languages multiple times during a single operation.

## Building the Project

From the project root directory, run:

```bash
make
```

This builds all three compiled components:

- The C shared library.
- The C executable that embeds Python.
- The standalone C producer.

To rebuild everything from scratch:

```bash
make clean
make
```

## Makefile Commands

| Command | Description |
|---|---|
| `make` | Builds all compiled components. |
| `make python-c` | Runs the Python-to-C demonstration. |
| `make demo` | Runs the C-to-Python demonstration. |
| `make pipes` | Runs the shell-pipe demonstration. |
| `make test` | Runs the automated unit tests. |
| `make benchmark` | Runs the performance benchmarks and generates CSV results. |
| `make clean` | Removes generated binaries and shared libraries. |

## Testing

Automated tests are implemented in `tests/test_numeric.py` using Python's `unittest` framework.

The tests cover:

- Numerical function correctness.
- Array operations and empty-array behavior.
- Input validation and error handling.
- In-place modification and memory ownership behavior.
- C and Python structure layout compatibility.
- Callback execution and callback exceptions.
- String and byte-length handling.

Run the complete test suite:

```bash
make test
```

## Benchmarking

The performance experiments compare four approaches:

1. Pure Python per-element affine transformation.
2. Python calling C once per element using `ctypes`.
3. Python calling C once for an entire array using `ctypes`.
4. C calling a Python callback for each element.

Each approach is tested with:

- 10 elements
- 1,000 elements
- 100,000 elements
- 1,000,000 elements

Each measurement uses two warmup runs followed by seven timed repetitions.

The benchmark records:

- Median execution time.
- Minimum execution time.
- Maximum execution time.
- Spread between maximum and minimum execution times.

Correctness is checked before timing. Compilation, library loading, and initial imports are excluded from timed measurements. The Python-to-C array approach includes data conversion and copying overhead.

The original report and benchmark files are retained as earlier project snapshots. The updated performance analysis and latest benchmark measurements are available in report2.md and benchmarks/results2.csv.

Results are saved in:

```text
benchmarks/results2.csv
```

To reproduce the benchmark:

```bash
make benchmark
```

## Benchmark Environment

The performance experiments were conducted in the following environment:

- **Operating System:** Ubuntu 26.04 LTS running under WSL2
- **Linux Kernel:** 6.6.114.1-microsoft-standard-WSL2
- **Architecture:** x86_64
- **Processor:** 12th Gen Intel Core i5-1235U
- **Logical CPUs:** 12
- **Available Memory:** 15 GiB
- **Python:** 3.14.4
- **GCC:** 15.2.0

## Key Concepts Demonstrated

- Shared libraries and dynamic linking.
- C function calls from Python using `ctypes`.
- Python interpreter initialization and finalization.
- Python object management through reference counting.
- Data conversion across language boundaries.
- Array and structure interoperability.
- Memory allocation, ownership, and cleanup.
- Python callbacks invoked from C.
- Error handling across language boundaries.
- Standard input, standard output, and shell pipes.
- Automated testing and performance benchmarking.
- Trade-offs between per-element calls and batched operations.

## Author

CS5115 — Language Interoperability Project
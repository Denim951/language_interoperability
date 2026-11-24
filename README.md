# CS5115 — Language Interoperability

## Project Overview

This project explores language interoperability by demonstrating how C and Python can communicate with each other using three different approaches.

The project demonstrates:

1. Python calling C using `ctypes` and a shared library.
2. C calling Python using the Python C API.
3. Independent C and Python programs communicating through shell pipes.

The goal is to understand how different programming languages exchange data, invoke functions, and communicate across language boundaries.

## Project Structure

```text
language_interoperability/
│
├── Makefile
├── README.md
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
├── benchmarks/
│   └── benchmark.py
│
├── experiments/
│   └── predictions.md
│
└── tests/
```

## Requirements

- GCC compiler
- GNU Make
- Python 3
- Python development headers
- `python3-config`

The Python development headers are required for compiling C programs that embed the Python interpreter.

## Approach 1: Python Calling C

**Technology:** Python `ctypes` and a C shared library.

The C implementation provides numerical functions that can be accessed from Python.

Implemented functions include:

- `affine()` — calculates a linear transformation.
- `scale_in_place()` — scales an existing array.
- `utf8_length()` — calculates the length of a null-terminated C string in bytes.
- `byte_length()` — returns an explicitly supplied byte length.
- `mean_array()` — calculates the mean of an array.
- `scale_array()` — scales an input array into an output array.

Python uses `ctypes` to load the compiled shared library and define the argument and return types of the C functions.

Run:

```bash
make python-c
```

## Approach 2: C Calling Python

**Technology:** Python C API.

A standalone C program initializes the Python interpreter, imports a Python module, locates a Python function, passes arguments to it, and retrieves its result.

The Python module implements three transformation modes:

- `square`
- `absolute`
- `reciprocal`

The program also handles Python exceptions and releases Python objects after use.

Run:

```bash
make demo
```

Example:

```bash
./c_calls_python/embed_demo 4 square
```

Expected output:

```text
Result: 16.000000
```

## Approach 3: Communication Through Shell Pipes

**Technology:** Standard input and standard output.

This approach demonstrates communication between two independent programs without using a shared library or directly embedding one language inside the other.

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

## Building the Project

From the project root directory, run:

```bash
make
```

This builds all three compiled components:

- The C shared library.
- The C executable that embeds Python.
- The standalone C producer.

## Makefile Commands

| Command | Description |
|---|---|
| `make` | Builds all components. |
| `make demo` | Runs the C-to-Python demonstration. |
| `make pipes` | Runs the shell-pipe demonstration. |
| `make python-c` | Runs the Python-to-C demonstration. |
| `make clean` | Removes generated binaries and shared libraries. |

To rebuild everything from scratch:

```bash
make clean
make
```

## Key Concepts Demonstrated

- Shared libraries and dynamic linking.
- C function calls from Python using `ctypes`.
- Python interpreter initialization and finalization.
- Python object management through reference counting.
- Data exchange between C and Python.
- Standard input, standard output, and shell pipes.
- Automated compilation using Makefiles.

## Author

CS5115 — Language Interoperability Project
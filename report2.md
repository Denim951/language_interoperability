# Language Interoperability: Calling Across the C–Python Boundary

## 1. Introduction

The goal of this project was to explore how C and Python can communicate and work together through different interoperability techniques. Although Python provides simplicity and flexibility, C offers lower-level memory control and can be useful for performance-sensitive operations. Combining the two languages allows developers to use the strengths of each.

This project implements three approaches: calling C functions from Python using `ctypes`, embedding Python inside a standalone C program using the Python C API, and communicating between separate processes through Unix pipes. It also explores arrays, structures, memory ownership, callbacks, exception handling, and performance differences between implementations.

## 2. Python Calling C

The first approach uses Python's `ctypes` library to load a compiled C shared library (`libnumeric.so`). This allows Python to call C functions without requiring a separate Python extension module.

The C library implements several numerical operations, including affine transformations, array scaling, calculating summaries, and working with dynamically allocated memory.

One important consideration when using `ctypes` is correctly defining argument and return types. For example, C's `double` corresponds to `ctypes.c_double`, while pointers to doubles require `ctypes.POINTER(ctypes.c_double)`. Incorrect type declarations can cause unexpected behavior or memory errors.

The project also implements a C `Summary` structure and a matching Python `ctypes.Structure`. The structure contains a count, minimum, maximum, and mean. Its size and field offsets are compared between C and Python to verify that both languages interpret the memory layout consistently.

Memory ownership is important when C allocates memory dynamically. The `make_scaled_copy` function returns newly allocated memory, which the Python wrapper copies into a Python list before releasing it with `numeric_free`. A `finally` block guarantees cleanup. Similarly, `mean_array` returns a status code and writes its result through an output pointer. This avoids confusing a valid mean of `0.0` with an error. The wrapper also converts Python lists into temporary C-compatible arrays, translates C errors into Python exceptions, and avoids modifying the caller's original lists.

## 3. C Calling Python

The second approach embeds the Python interpreter inside a standalone C executable using the Python C API.

The `embed_demo.c` program initializes Python, imports a specified module, retrieves a specified function, and calls it with arguments supplied through the command line. The Python module `policies.py` provides transformation functions for squaring, calculating absolute values, and finding reciprocals.

The program uses functions such as `Py_Initialize`, `PyImport_ImportModule`, `PyObject_GetAttrString`, and `PyObject_CallObject` to interact with Python. Python objects are reference-counted, so the C program must release references using `Py_DECREF` or `Py_XDECREF` when appropriate.

Error handling is particularly important. If a Python function raises an exception, `PyObject_CallObject` returns `NULL`. The C program detects this condition and uses `PyErr_Print` to display the Python traceback. The implementation also checks for missing modules, missing functions, invalid numeric input, and non-finite numbers.

This demonstrates that Python exceptions and errors must be explicitly handled when crossing the language boundary.

## 4. Arrays, Structures, and Callbacks

The project explores passing arrays between Python and C, returning dynamically allocated arrays, and matching structures across the two languages.

The `affine_array` function performs an affine transformation on an entire array in one C call. This reduces the number of transitions between Python and C compared with calling the scalar `affine` function separately for every element.

The project also implements `map_array`, which accepts a C callback function pointer. Python supplies a callback through `ctypes.CFUNCTYPE`, allowing C to invoke Python code for individual array elements.

Callback failures require special handling. Python exceptions should not be allowed to propagate directly through C. Instead, the wrapper captures the exception, returns an error status to C, and re-raises the original Python exception after control returns to Python.

This demonstrates the flexibility of callbacks while also showing that crossing language boundaries introduces additional complexity.

## 5. Benchmarking and Performance Analysis

Four implementations were benchmarked:

1. Pure Python affine transformation.
2. Python calling the C affine function once per element.
3. Python calling the C affine_array function once per array.
4. C processing an array while invoking a Python callback for each element.

The benchmark tested arrays containing 10, 1,000, 100,000, and 1,000,000 elements. Each implementation received two warm-up runs followed by seven timed repetitions. Median, minimum, maximum, and timing spread were recorded. Correctness checks were performed outside the timed measurements, and compilation and import startup were excluded.

The following table shows the median execution times from the benchmark:

| Array Size | Pure Python | C Per Element | C Per Array | C Callback |
|---|---:|---:|---:|---:|
| 10 | 0.40 µs | 6.09 µs | 4.19 µs | 8.43 µs |
| 1,000 | 20.56 µs | 505.13 µs | 206.82 µs | 509.17 µs |
| 100,000 | 3.37 ms | 46.86 ms | 18.26 ms | 47.28 ms |
| 1,000,000 | 31.24 ms | 403.54 ms | 140.22 ms | 413.74 ms |

The results demonstrate that calling C once per element can be expensive because each call introduces Python-to-C boundary overhead. Batching operations into a single C call significantly reduces this overhead. At one million elements, the array-based C implementation was approximately 2.9 times faster than calling the scalar C function individually.

However, pure Python was still approximately 4.5 times faster than the batched C implementation for this particular operation. This is because the operation itself is very simple, and the C implementation includes the overhead of constructing ctypes arrays and converting the results back into a Python list. These results show that using C does not automatically make a program faster. The amount of work performed per boundary crossing matters significantly.

## 6. Embedding, Threading, and Alternatives

Embedding Python inside C is useful when an existing C application needs access to Python functionality. In contrast, loading a C shared library from Python is useful when Python applications need access to native functionality.

Both approaches have different ownership and initialization requirements. Embedding requires initializing and managing the Python interpreter, while `ctypes` requires correctly defining function signatures and managing memory passed across the boundary.

Python's Global Interpreter Lock (GIL) is another consideration. In traditional CPython builds, the GIL generally restricts simultaneous execution of Python bytecode by multiple threads within one interpreter. Native C code can sometimes perform work without holding the GIL, but callbacks into Python require the appropriate Python thread state and GIL handling. This becomes especially important in multithreaded applications.

An alternative to in-process interoperability is communication between separate processes. This project demonstrates that approach using Unix pipes. A C producer sends numerical data through standard output, and a Python consumer reads and processes it. This approach avoids sharing memory between languages and provides process isolation, although serialization and communication introduce their own overhead.

## 7. Conclusion

This project demonstrated multiple ways to combine C and Python, including shared libraries, interpreter embedding, callbacks, and inter-process communication.

The most important performance finding was that reducing the number of language-boundary crossings can matter more than simply moving computation into C. The experiments also highlighted the importance of type compatibility, memory ownership, reference counting, and exception handling.

Overall, the project provided practical experience with language interoperability and demonstrated that choosing the right approach depends on the application's requirements, performance characteristics, and complexity.
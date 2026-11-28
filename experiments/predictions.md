# Benchmark Predictions and Observations

## 1. Expected Performance

Based on the design of the four approaches, the following performance characteristics are expected:

1. **Pure Python:** Python's list comprehension should perform reasonably well because it avoids communication overhead between languages.
2. **C per element:** Calling a C function separately for every element is expected to introduce significant overhead because each element requires a Python-to-C transition.
3. **C per array:** Passing an entire array to C in one call should reduce the number of language transitions. This approach is expected to perform better than calling C once per element, although converting data between Python and C still introduces overhead.
4. **C with Python callback:** Calling a Python function from C for every element is expected to introduce overhead because execution repeatedly crosses the language boundary.

These are theoretical expectations based on the implementation. They were documented after the benchmark was run, rather than recorded beforehand.

## 2. Actual Benchmark Results

The benchmark used four input sizes, two warmup runs, and seven timed repetitions per approach. Results below show median execution time.

| Approach | 10 elements | 1,000 elements | 100,000 elements | 1,000,000 elements |
|---|---:|---:|---:|---:|
| Pure Python | 0.585 µs | 25.13 µs | 3.56 ms | 26.83 ms |
| C per element | 7.06 µs | 664.55 µs | 51.51 ms | 448.44 ms |
| C per array | 4.45 µs | 173.31 µs | 13.22 ms | 136.58 ms |
| C with Python callback | 10.77 µs | 695.07 µs | 37.33 ms | 402.98 ms |

### Timing Variability

The benchmark also recorded the minimum, maximum, and spread for each approach. Spread is calculated as:

Spread = Maximum execution time - Minimum execution time.

These measurements are available in `benchmarks/results.csv`. The median is used for the primary performance comparisons because it is less sensitive to unusually fast or slow individual executions.

## 3. Analysis

Pure Python was the fastest approach at all four input sizes. This demonstrates that using C does not automatically improve performance when the cost of crossing the language boundary is greater than the computational work being performed.

Calling C once per element was considerably slower than pure Python. At 1,000,000 elements, this approach took approximately 448.44 ms, compared with 26.83 ms for pure Python. The repeated Python-to-C transitions introduced substantial overhead.

Calling C once for the entire array performed significantly better than calling C separately for every element. At 1,000,000 elements, batching was approximately 3.3 times faster than the per-element approach. This demonstrates the performance benefit of reducing the number of language transitions.

The callback approach was also slower than pure Python. This is expected because C must invoke Python for every element, introducing repeated C-to-Python transitions. At 1,000,000 elements, the callback approach took approximately 402.98 ms.

One interesting observation is that the callback approach was somewhat faster than calling C once per element in the larger tests. Although both approaches involve repeated language transitions, their implementation and conversion overhead differ.

One important consideration is that the array benchmark includes the overhead of converting Python lists into ctypes arrays and converting the results back into Python lists. The callback benchmark also includes array conversion and callback setup. Therefore, these measurements represent the cost of the complete Python-facing operations rather than only the execution time of the C functions.

Timing variability was also observed, particularly in some smaller tests and the one-million-element pure Python test. This reinforces the importance of using multiple repetitions and reporting median and spread rather than relying on a single execution.

## 4. Conclusion

The results demonstrate that interoperability performance depends on more than the execution speed of the underlying language. Data conversion, function-call overhead, and the frequency of transitions between languages all affect performance.

For this experiment, batching data into a single C call was substantially more efficient than making individual calls. However, pure Python remained the fastest overall for this relatively simple affine transformation.

The one-million-element benchmark reinforces these findings. Pure Python completed in approximately 26.83 ms, while the batched C approach took 136.58 ms. Batching was approximately 3.3 times faster than individual C calls, but pure Python remained approximately 5.1 times faster than the batched C wrapper.

The results suggest that C becomes more attractive when its computational workload is substantial enough to outweigh the cost of crossing the language boundary. More computationally intensive operations or approaches that minimize data conversion may produce different results.

## 5. Introductory Interoperability Experiments

The introductory experiments demonstrate how Python and C handle function arguments, memory, and strings across the language boundary. The code is available in `experiments/intro_experiments.py`.

### A1. First Cross-Language Call

The C function `affine(x, scale, offset)` calculates:

`(x * scale) + offset`

For the call `affine(3.0, 2.0, 1.0)`, the predicted result was 7.0. The experiment returned 7.0.

Passing the string `"3.0"` instead of the floating-point value `3.0` raised a `ctypes.ArgumentError`. The string was rejected before reaching the C function because the Python binding declared the arguments as `ctypes.c_double`. This demonstrates that `ctypes` performs argument validation and conversion at the language boundary.

### A2. Mutation Versus Copying

The experiment created a three-element ctypes array containing `[1.0, 2.0, 3.0]` and passed it to the C function `scale_in_place()` with a factor of 2.0.

The array changed to `[2.0, 4.0, 6.0]`, confirming that C modified the same memory visible to Python. The ctypes array provided storage that could be passed to C through a pointer.

Passing an ordinary Python list directly instead raised a `ctypes.ArgumentError`. A Python list is not automatically converted into a C-compatible `double` array for this pointer parameter. An explicit conversion or wrapper is required.

### A3. Strings and Byte Buffers

The Python string `"café"` contains four Unicode characters, so `len(text)` returned 4. Encoding it as UTF-8 produced five bytes, so `len(payload)` returned 5. The additional byte is needed because the character `é` occupies two bytes in UTF-8.

The experiment also passed `b"A\x00B"` to two C functions. The NUL-terminated string function returned 1 because `strlen()` stops at the first zero byte. The explicit-length byte function returned 3 because it received the buffer length separately and did not depend on NUL termination.

### Prediction and Observation Summary

| Experiment | Prediction | Observation |
|---|---|---|
| A1: Numeric affine call | Result would be 7.0 | Returned 7.0 |
| A1: String passed as double | The incompatible argument would be rejected | `ctypes.ArgumentError` |
| A2: C modifies ctypes array | Python would see the changes | `[1.0, 2.0, 3.0]` became `[2.0, 4.0, 6.0]` |
| A2: Ordinary list passed as pointer | The list would not be accepted automatically | `ctypes.ArgumentError` |
| A3: UTF-8 encoding | Five bytes for four characters | `len(text) = 4`, `len(payload) = 5` |
| A3: Embedded NUL | C string length would stop at the NUL | Returned 1 |
| A3: Explicit byte length | All bytes would be counted | Returned 3 |

These experiments show that interoperability requires attention to type conversion, memory ownership, mutation, and data representation. Python and C do not automatically share the same assumptions about these concepts.


import ctypes
from pathlib import Path

# Load our compiled C shared library
library_path = Path(__file__).resolve().parent / "libnumeric.so"
lib = ctypes.CDLL(str(library_path))

# Using ctypes.c_double translates Python's decimal numbers into the exact binary format our
#  C function needs to read and modify them properly.
lib.affine.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.affine.restype = ctypes.c_double

# Call the C function
result = lib.affine(3.0, 2.0, 1.0)

print(result)

lib.scale_in_place.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t, # In C, size_t is an unsigned integer (meaning it can only hold zero or positive numbers), it tells Python to pass the second argument as a positive integer
    ctypes.c_double
]

lib.scale_in_place.restype = None

values = [2.0, 4.0, 6.0]

DoubleArray = ctypes.c_double * len(values) #Double Array - custom Python class, will be a C-style array that holds three doubles, created on the spot
c_values = DoubleArray(*values) # actually allocates the memory and creates the C array

lib.scale_in_place(c_values, len(values), 3.0)

# print(list(c_values))

lib.utf8_length.argtypes = [
    ctypes.c_char_p #represents a pointer to a C-style string.
]

lib.utf8_length.restype = ctypes.c_size_t # returns and unsigned integer

text = "cafē"

encoded_text = text.encode("utf-8")

result = lib.utf8_length(encoded_text)

# print("Python character count:", len(text))
# print("UTF-8 byte count:", result)

data = b"A\x00B"

result = lib.utf8_length(data)

# print("Actual byte count:", len(data))
# print("C string length:", result)

lib.byte_length.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t
]

lib.byte_length.restype = ctypes.c_size_t

result = lib.byte_length(data, len(data))

# print("Actual byte count:", len(data))
# print("C explicit-length result:", result)

lib.mean_array.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_double)
]

lib.mean_array.restype = ctypes.c_int

values = [10.0, 20.0, 30.0, 40.0]

DoubleArray = ctypes.c_double * len(values)
c_values = DoubleArray(*values)

mean_result = ctypes.c_double() # creates a C-compatible double variable

status = lib.mean_array(
    c_values,
    len(values),
    ctypes.byref(mean_result) #Passes its memory address to C
)

# if status == 0:
#     print("Mean:", mean_result.value)
# else:
#     print("Mean calculation failed. Status:", status)

lib.scale_array.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double)
]

lib.scale_array.restype = ctypes.c_int

input_values = [2.0, 4.0, 6.0]

DoubleArray = ctypes.c_double * len(input_values)

c_input = DoubleArray(*input_values)
c_output = DoubleArray()

status = lib.scale_array(
    c_input,
    len(input_values),
    3.0,
    c_output
)

# if status == 0:
#     print("Original:", input_values)
#     print("Scaled:", list(c_output))
# else:
#     print("Scaling failed. Status:", status)
    
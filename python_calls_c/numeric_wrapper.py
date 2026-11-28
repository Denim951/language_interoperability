import ctypes
from pathlib import Path

# Load our compiled C shared library
library_path = Path(__file__).resolve().parent / "libnumeric.so"
lib = ctypes.CDLL(str(library_path))

# Using ctypes.c_double translates Python's decimal numbers into the exact binary format our
#  C function needs to read and modify them properly.
lib.affine.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.affine.restype = ctypes.c_double

lib.affine_array.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double)
]
lib.affine_array.restype = ctypes.c_int

lib.scale_in_place.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t, # In C, size_t is an unsigned integer (meaning it can only hold zero or positive numbers), it tells Python to pass the second argument as a positive integer
    ctypes.c_double
]

lib.scale_in_place.restype = None

lib.utf8_length.argtypes = [
    ctypes.c_char_p #represents a pointer to a C-style string.
]

lib.utf8_length.restype = ctypes.c_size_t # returns and unsigned integer

lib.byte_length.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t
]

lib.byte_length.restype = ctypes.c_size_t

lib.mean_array.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_double)
]

lib.mean_array.restype = ctypes.c_int

lib.scale_array.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double)
]

lib.scale_array.restype = ctypes.c_int

class Summary(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_size_t),
        ("minimum", ctypes.c_double),
        ("maximum", ctypes.c_double),
        ("mean", ctypes.c_double),
    ]


lib.summarize.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.POINTER(Summary),
]
lib.summarize.restype = ctypes.c_int


lib.make_scaled_copy.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
]
lib.make_scaled_copy.restype = ctypes.c_int


lib.numeric_free.argtypes = [
    ctypes.POINTER(ctypes.c_double),
]
lib.numeric_free.restype = None

def affine(value, scale, offset):
    # Call the C affine function on a single number: (value * scale) + offset.
    # Because we set argtypes and restype earlier, ctypes handles the float conversion automatically.
    return lib.affine(value, scale, offset)

def affine_array(values, scale, offset):
    """
    Apply an affine transformation to an entire list using C.

    Formula: result = (value * scale) + offset

    Parameters:
        values: List of numbers to transform.
        scale: Multiplication factor.
        offset: Value added after multiplication.

    Returns:
        A new Python list containing the transformed numbers.

    Memory:
        Creates temporary C arrays owned by this function.
        Python manages their memory automatically.
    """

    # An empty list requires no C call.
    if not values:
        return []

    # Convert the Python list into a C-compatible double array.
    count = len(values)
    # multiplying a ctypes type by an integer doesn't do math; ctypes overrides * to mean "make an array type of this exact length."
    # (*values) instantiates that array type and populates it. The * unpacks your Python list so that values = [1.0, 2.0, 3.0] is passed as separate arguments
    input_array = (ctypes.c_double * count)(*values)

    # Allocate an output array for C to fill.
    output_array = (ctypes.c_double * count)()

    # Call the C function and capture its status code.
    status = lib.affine_array(
        input_array,
        count,
        scale,
        offset,
        output_array
    )

    # Raise an exception if C reports invalid arguments.
    if status != 0:
        raise ValueError(f"C affine_array failed with status {status}")

    # Convert the C output array into a regular Python list.
    return list(output_array)

def mean(values):
    """
    Calculate the arithmetic mean of a list using the C mean_array function.

    Raises:
        ValueError: If the input list is empty or C reports invalid arguments.
    """
    if not values:
        raise ValueError("Cannot calculate the mean of an empty list")

    array_type = ctypes.c_double * len(values)
    c_values = array_type(*values)

    result = ctypes.c_double()

    status = lib.mean_array(
        c_values,
        len(values),
        ctypes.byref(result)
    )

    if status != 0:
        raise ValueError("C mean_array() failed")

    return result.value

def scale(values, factor):
    """
    Return a new list with every element multiplied by factor.

    The original Python list is not modified.
    """
    if not values:
        return []

    array_type = ctypes.c_double * len(values)

    c_input = array_type(*values)
    c_output = array_type()

    status = lib.scale_array(
        c_input,
        len(values),
        factor,
        c_output
    )

    if status != 0:
        raise ValueError("C scale_array() failed")

    return list(c_output)

def summarize(values):
    array_type = ctypes.c_double * len(values)
    c_values = array_type(*values)

    result = Summary()

    status = lib.summarize(
        c_values,
        len(values),
        ctypes.byref(result)
    )

    if status != 0:
        raise ValueError("C summarize() failed")

    return {
        "count": result.count,
        "minimum": result.minimum,
        "maximum": result.maximum,
        "mean": result.mean,
    }


def make_scaled_copy(values, factor):
    array_type = ctypes.c_double * len(values)
    c_values = array_type(*values)

    output_pointer = ctypes.POINTER(ctypes.c_double)()

    status = lib.make_scaled_copy(
        c_values,
        len(values),
        factor,
        ctypes.byref(output_pointer)
    )

    if status != 0:
        raise ValueError("C make_scaled_copy() failed")

    if len(values) == 0:
        return []

    try:
        return [output_pointer[i] for i in range(len(values))]
    finally:
        lib.numeric_free(output_pointer)

lib.summary_size.argtypes = []
lib.summary_size.restype = ctypes.c_size_t

lib.summary_offset_count.argtypes = []
lib.summary_offset_count.restype = ctypes.c_size_t

lib.summary_offset_minimum.argtypes = []
lib.summary_offset_minimum.restype = ctypes.c_size_t

lib.summary_offset_maximum.argtypes = []
lib.summary_offset_maximum.restype = ctypes.c_size_t

lib.summary_offset_mean.argtypes = []
lib.summary_offset_mean.restype = ctypes.c_size_t

def check_structure_layout():
    python_offsets = {
        "count": Summary.count.offset,
        "minimum": Summary.minimum.offset,
        "maximum": Summary.maximum.offset,
        "mean": Summary.mean.offset,
    }

    c_offsets = {
        "count": lib.summary_offset_count(),
        "minimum": lib.summary_offset_minimum(),
        "maximum": lib.summary_offset_maximum(),
        "mean": lib.summary_offset_mean(),
    }

    print("\nStructure layout comparison:")
    print("Python size:", ctypes.sizeof(Summary))
    print("C size:", lib.summary_size())
    print("Python offsets:", python_offsets)
    print("C offsets:", c_offsets)

    assert ctypes.sizeof(Summary) == lib.summary_size()
    assert python_offsets == c_offsets

    print("SUCCESS: Structure layouts match!")

CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_void_p
)

lib.map_array.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    CALLBACK,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_size_t),
]

lib.map_array.restype = ctypes.c_int

def map_values(values, function):
    array_type = ctypes.c_double * len(values)
    c_input = array_type(*values)

    c_output = array_type()
    failed_index = ctypes.c_size_t()

    callback_error = []

    def python_callback(input_value, output_pointer, context):
        try:
            output_pointer[0] = function(input_value)
            return 0
        except Exception as error:
            callback_error.append(error)
            return 1

    callback = CALLBACK(python_callback)

    status = lib.map_array(
        c_input,
        len(values),
        callback,
        None,
        c_output,
        ctypes.byref(failed_index)
    )

    if callback_error:
        raise callback_error[0]

    if status == 1:
        raise ValueError("C map_array() received invalid arguments")

    if status == 2:
        raise RuntimeError(
            f"C callback failed at index {failed_index.value}"
        )

    return list(c_output)

if __name__ == "__main__":
    check_structure_layout()

    print("\nSummary test:")
    print(summarize([2.0, 4.0, 6.0, 8.0]))

    print("\nScaled copy test:")
    print(make_scaled_copy([2.0, 4.0, 6.0], 3.0))

    print("\nCallback success test:")
    print(map_values([1.0, 2.0, 3.0, 4.0], lambda x: x * x))

    print("\nCallback failure test:")
    try:
        map_values([2.0, 1.0, 0.0, 4.0], lambda x: 1 / x)
    except ZeroDivisionError as error:
        print("Caught expected exception:", error)

    print("\nEmpty callback test:")
    print(map_values([], lambda x: x * 2))
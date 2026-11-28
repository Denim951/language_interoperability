import ctypes
from pathlib import Path

library_path = Path(__file__).resolve().parents[1] / "python_calls_c" / "libnumeric.so"
lib = ctypes.CDLL(str(library_path))

lib.affine.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.affine.restype = ctypes.c_double

lib.scale_in_place.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_double,
]

lib.utf8_length.argtypes = [ctypes.c_char_p]
lib.utf8_length.restype = ctypes.c_size_t

lib.byte_length.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
lib.byte_length.restype = ctypes.c_size_t


print("A1: First cross-language call")
print("affine(3.0, 2.0, 1.0):", lib.affine(3.0, 2.0, 1.0))

try:
    lib.affine("3.0", 2.0, 1.0)
except (TypeError, ctypes.ArgumentError) as error:
    print("String argument rejected:", type(error).__name__)


print("\nA2: Mutation versus copying")
values = (ctypes.c_double * 3)(1.0, 2.0, 3.0)
print("Before C call:", list(values))

lib.scale_in_place(values, 3, 2.0)
print("After C call:", list(values))

try:
    lib.scale_in_place([1.0, 2.0, 3.0], 3, 2.0)
except (TypeError, ctypes.ArgumentError) as error:
    print("Ordinary Python list rejected:", type(error).__name__)


print("\nA3: Strings and byte buffers")
text = "café"
payload = text.encode("utf-8")

print("Text:", text)
print("len(text):", len(text))
print("len(payload):", len(payload))
print("UTF-8 bytes:", payload)

data = b"A\x00B"
print("Byte data:", data)
print("C string length:", lib.utf8_length(data))
print("Explicit byte length:", lib.byte_length(data, len(data)))

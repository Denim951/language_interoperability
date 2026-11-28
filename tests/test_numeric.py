import sys
import unittest
from pathlib import Path

# Add the python_calls_c directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_CALLS_C = PROJECT_ROOT / "python_calls_c"
sys.path.insert(0, str(PYTHON_CALLS_C))

import numeric_wrapper as numeric

# Group related tests into a class that unittest recognizes.
class TestNumeric(unittest.TestCase):

    # Any method starting with "test_" is automatically run as a test.
    def test_summarize_valid_values(self):
        # Call summarize() on sample numbers and save the returned dictionary.
        result = numeric.summarize([2.0, 4.0, 6.0, 8.0])

        # Check that each summary value matches what we expect.
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["minimum"], 2.0)
        self.assertEqual(result["maximum"], 8.0)
        self.assertEqual(result["mean"], 5.0)

    def test_summarize_empty_values(self):
        with self.assertRaises(ValueError):
            numeric.summarize([])

    def test_make_scaled_copy(self):
        result = numeric.make_scaled_copy([2.0, 4.0, 6.0], 3.0)

        self.assertEqual(result, [6.0, 12.0, 18.0])

    def test_make_scaled_copy_empty(self):
        result = numeric.make_scaled_copy([], 3.0)

        self.assertEqual(result, [])

    def test_structure_layout(self):
        self.assertEqual(
            numeric.ctypes.sizeof(numeric.Summary),
            numeric.lib.summary_size()
        )

        self.assertEqual(
            numeric.Summary.count.offset,
            numeric.lib.summary_offset_count()
        )

        self.assertEqual(
            numeric.Summary.minimum.offset,
            numeric.lib.summary_offset_minimum()
        )

        self.assertEqual(
            numeric.Summary.maximum.offset,
            numeric.lib.summary_offset_maximum()
        )

        self.assertEqual(
            numeric.Summary.mean.offset,
            numeric.lib.summary_offset_mean()
        )

    def test_map_values_square(self):
        result = numeric.map_values(
            [1.0, 2.0, 3.0, 4.0],
            lambda x: x * x
        )

        self.assertEqual(result, [1.0, 4.0, 9.0, 16.0])

    def test_map_values_empty(self):
        result = numeric.map_values([], lambda x: x * 2)

        self.assertEqual(result, [])

    def test_map_values_callback_exception(self):
        with self.assertRaises(ZeroDivisionError):
            numeric.map_values(
                [2.0, 1.0, 0.0, 4.0],
                lambda x: 1 / x
            )

    def test_mean_invalid_input_does_not_modify_output(self):
        result = numeric.ctypes.c_double(123.0)

        status = numeric.lib.mean_array(
            None,
            0,
            numeric.ctypes.byref(result)
        )

        self.assertEqual(status, 1)
        self.assertEqual(result.value, 123.0)

    def test_scale_empty_null_pointers(self):
        status = numeric.lib.scale_array(
            None,
            0,
            3.0,
            None
        )

        self.assertEqual(status, 0)

    def test_scale_exact_in_place_alias(self):
        values = (numeric.ctypes.c_double * 3)(2.0, 4.0, 6.0)

        status = numeric.lib.scale_array(
            values,
            3,
            3.0,
            values
        )

        self.assertEqual(status, 0)
        self.assertEqual(list(values), [6.0, 12.0, 18.0])

    def test_affine(self):
        result = numeric.lib.affine(3.0, 2.0, 1.0)

        self.assertEqual(result, 7.0)

    def test_affine_array(self):
        values = [1.0, 2.0, 3.0, 4.0]

        result = numeric.affine_array(values, 2.0, 3.0)

        self.assertEqual(result, [5.0, 7.0, 9.0, 11.0])

    def test_mean(self):
        result = numeric.mean([2.0, 4.0, 6.0, 8.0])

        self.assertEqual(result, 5.0)

    def test_mean_empty(self):
        with self.assertRaises(ValueError):
            numeric.mean([])

    def test_scale(self):
        values = [2.0, 4.0, 6.0]

        result = numeric.scale(values, 3.0)

        self.assertEqual(result, [6.0, 12.0, 18.0])
        self.assertEqual(values, [2.0, 4.0, 6.0])

    def test_scale_empty(self):
        result = numeric.scale([], 3.0)

        self.assertEqual(result, [])

    def test_utf8_length(self):
        text = "cafē"
        result = numeric.lib.utf8_length(text.encode("utf-8"))

        self.assertEqual(result, 5)

    def test_scale_in_place(self):
        values = [2.0, 4.0, 6.0]
        array_type = numeric.ctypes.c_double * len(values)
        c_values = array_type(*values)

        numeric.lib.scale_in_place(c_values, len(values), 3.0)

        self.assertEqual(list(c_values), [6.0, 12.0, 18.0])

    def test_byte_length(self):
        data = b"A\x00B"
        result = numeric.lib.byte_length(data, len(data))

        self.assertEqual(result, 3)


# Only run tests when this file is executed directly, not when imported.
if __name__ == "__main__":
    unittest.main()
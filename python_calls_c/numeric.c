#include <string.h>
#include <math.h>
#include <stdlib.h>
#include <stdint.h>
#include "numeric.h"


/*
 * Applies an affine transformation to a single number.
 *
 * Formula: result = (x * scale) + offset
 *
 * Parameters:
 *   x      - Input number to transform.
 *   scale  - Multiplication factor.
 *   offset - Value added after multiplication.
 *
 * Returns:
 *   The transformed number.
 */
double affine(double x, double scale, double offset)
{
    return x * scale + offset;
}


/*
 * Applies an affine transformation to every element in an array.
 *
 * Formula: output[i] = (input[i] * scale) + offset
 *
 * Parameters:
 *   input  - Array containing the original numbers.
 *   n      - Number of elements in the input array.
 *   scale  - Multiplication factor.
 *   offset - Value added after multiplication.
 *   output - Array where the transformed numbers are stored.
 *            The caller must provide enough space for n doubles.
 *
 * Returns:
 *   NUMERIC_OK    - Transformation completed successfully.
 *   NUMERIC_EINVAL - Invalid input or output pointer.
 *
 * Memory:
 *   Does not allocate or free memory. The caller owns both arrays.
 */
int affine_array(
    const double *input,
    size_t n,
    double scale,
    double offset,
    double *output
)
{
    // An empty array is valid; there is nothing to transform.
    if (n == 0)
    {
        return NUMERIC_OK;
    }

    // Both pointers must be valid when processing at least one element.
    if (input == NULL || output == NULL)
    {
        return NUMERIC_EINVAL;
    }

    // Transform each element and store the result in the output array.
    for (size_t i = 0; i < n; i++)
    {
        output[i] = affine(input[i], scale, offset);
    }

    return NUMERIC_OK;
}

void scale_in_place(double *values, size_t n, double factor)
{
    for (size_t i = 0; i < n; i++)
    {
        values[i] = values[i] * factor;
    }
}

size_t utf8_length(const char *text)
{
    return strlen(text);
}

size_t byte_length(const char *data, size_t n)
{
    (void)data; //explicitly tells the compiler that we're intentionally not using this parameter
    return n;
}

int mean_array(const double *values, size_t n, double *out_mean)
{
    if (values == NULL || out_mean == NULL || n == 0)
    {
        return NUMERIC_EINVAL;
    }

    double sum = 0.0;

    for (size_t i = 0; i < n; i++)
    {
        sum += values[i];
    }

    *out_mean = sum / n;

    return NUMERIC_OK;
}

int scale_array(
    const double *input,
    size_t n,
    double factor,
    double *output
)
{   // Empty arrays are allowed
    if (n == 0)
    {
        return NUMERIC_OK;
    }
    // Input and output pointers must be valid when n > 0
    if (input == NULL || output == NULL)
    {
        return NUMERIC_EINVAL;
    }

    for (size_t i = 0; i < n; i++)
    {
        output[i] = input[i] * factor;
    }

    return NUMERIC_OK;
}

int summarize(
    const double *values,
    size_t n,
    Summary *out_summary
)
{
    if (values == NULL || out_summary == NULL || n == 0)
    {
        return NUMERIC_EINVAL;
    }

    Summary result;

    result.count = n;
    result.minimum = values[0];
    result.maximum = values[0];

    double sum = 0.0;

    for (size_t i = 0; i < n; i++)
    {
        if (!isfinite(values[i]))
        {
            return NUMERIC_EINVAL;
        }

        sum += values[i];

        if (values[i] < result.minimum)
        {
            result.minimum = values[i];
        }

        if (values[i] > result.maximum)
        {
            result.maximum = values[i];
        }
    }

    result.mean = sum / n;

    *out_summary = result;

    return NUMERIC_OK;
}

int make_scaled_copy(
    const double *values,
    size_t n,
    double factor,
    double **out_values
)
{
    if (out_values == NULL)
    {
        return NUMERIC_EINVAL;
    }

    *out_values = NULL;

    if (n == 0)
    {
        return NUMERIC_OK;
    }

    if (values == NULL || !isfinite(factor))
    {
        return NUMERIC_EINVAL;
    }

    if (n > SIZE_MAX / sizeof(double))
    {
        return NUMERIC_EINVAL;
    }

    double *copy = malloc(n * sizeof(double));

    if (copy == NULL)
    {
        return NUMERIC_ENOMEM;
    }

    for (size_t i = 0; i < n; i++)
    {
        if (!isfinite(values[i]))
        {
            free(copy);
            return NUMERIC_EINVAL;
        }

        copy[i] = values[i] * factor;

        if (!isfinite(copy[i]))
        {
            free(copy);
            return NUMERIC_EINVAL;
        }
    }

    *out_values = copy;

    return NUMERIC_OK;
}

void numeric_free(double *values)
{
    free(values);
}

size_t summary_size(void)
{
    return sizeof(Summary);
}

size_t summary_offset_count(void)
{
    return offsetof(Summary, count);
}

size_t summary_offset_minimum(void)
{
    return offsetof(Summary, minimum);
}

size_t summary_offset_maximum(void)
{
    return offsetof(Summary, maximum);
}

size_t summary_offset_mean(void)
{
    return offsetof(Summary, mean);
}

int map_array(
    const double *input,
    size_t n,
    transform_callback callback,
    void *context,
    double *output,
    size_t *failed_index
)
{
    if (failed_index != NULL)
    {
        *failed_index = n;
    }

    if (callback == NULL)
    {
        return NUMERIC_EINVAL;
    }

    if (n == 0)
    {
        return NUMERIC_OK;
    }

    if (input == NULL || output == NULL)
    {
        return NUMERIC_EINVAL;
    }

    for (size_t i = 0; i < n; i++)
    {
        int status = callback(input[i], &output[i], context);

        if (status != 0)
        {
            if (failed_index != NULL)
            {
                *failed_index = i;
            }

            return NUMERIC_ECALLBACK;
        }
    }

    return NUMERIC_OK;
}
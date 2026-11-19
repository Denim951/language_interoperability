#include <string.h>
#include "numeric.h"


double affine(double x, double scale, double offset)
{
    return x * scale + offset;
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
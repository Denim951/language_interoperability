// Other C files can include numeric.h and use the functions 
// without needing to know their internal implementation.

#ifndef NUMERIC_H //Prevent the header from being included multiple times in the same compilation unit.
#define NUMERIC_H

#include <stddef.h>

// define a set of named integer constants
enum numeric_status { 
    NUMERIC_OK = 0, //function worked
    NUMERIC_EINVAL = 1, //Invalid Argument
    NUMERIC_ECALLBACK = 2, //an error occurred inside or while handling a callback function
    NUMERIC_ENOMEM = 3 // represents a memory allocation failure
};

typedef struct {
    size_t count;
    double minimum;
    double maximum;
    double mean;
} Summary;

int summarize(
    const double *values,
    size_t n,
    Summary *out_summary
);

int make_scaled_copy(
    const double *values,
    size_t n,
    double factor,
    double **out_values
);

void numeric_free(double *values);

size_t summary_size(void);
size_t summary_offset_count(void);
size_t summary_offset_minimum(void);
size_t summary_offset_maximum(void);
size_t summary_offset_mean(void);

double affine(double x, double scale, double offset);

int affine_array(
    const double *input,
    size_t n,
    double scale,
    double offset,
    double *output
);

int mean_array(
    const double *values,
    size_t n,
    double *out_mean
);

int scale_array(
    const double *input,
    size_t n,
    double factor,
    double *output
);

void scale_in_place(double *values, size_t n, double factor);

size_t utf8_length(const char *text);

size_t byte_length(const char *data, size_t n);

typedef int (*transform_callback)(
    double input,
    double *output,
    void *context
);

int map_array(
    const double *input,
    size_t n,
    transform_callback callback,
    void *context,
    double *output,
    size_t *failed_index
);

#endif
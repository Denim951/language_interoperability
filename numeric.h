// Other C files can include numeric.h and use the functions 
// without needing to know their internal implementation.

#ifndef NUMERIC_H //Prevent the header from being included multiple times in the same compilation unit.
#define NUMERIC_H

#include <stddef.h>

// define a set of named integer constants
enum numeric_status { 
    NUMERIC_OK = 0, //function worked
    NUMERIC_EINVAL = 1, //Invalid Argument
    NUMERIC_ECALLBACK = 2 //an error occurred inside or while handling a callback function
};

double affine(double x, double scale, double offset);

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

#endif
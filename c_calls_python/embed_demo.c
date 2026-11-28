
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char *argv[])
{
    if (argc != 5)
    {
        printf("Usage: ./embed_demo <module> <function> <number> <mode>\n");
        return 1;
    }

    char *endptr;
    double x = strtod(argv[3], &endptr);

    if (endptr == argv[3] || *endptr != '\0')
    {
        fprintf(stderr, "Error: '%s' is not a valid number.\n", argv[3]);
        return 1;
    }

    if (!isfinite(x))
    {
        fprintf(stderr, "Error: Please enter a finite number.\n");
        return 1;
    }

    Py_Initialize();

    if (PyRun_SimpleString("import sys") != 0 ||
    PyRun_SimpleString("sys.path.insert(0, 'c_calls_python')") != 0)
    {
        PyErr_Print();
        Py_Finalize();
        return 1;
    }
    PyObject *module = PyImport_ImportModule(argv[1]);

    if (module == NULL)
    {
        PyErr_Print();
        Py_Finalize();
        return 1;
    }

    PyObject *function = PyObject_GetAttrString(module, argv[2]);

    if (function == NULL || !PyCallable_Check(function))
    {
        PyErr_Print();
        printf("Could not find callable function: %s\n", argv[2]);
        Py_XDECREF(function);
        Py_DECREF(module);
        Py_Finalize();
        return 1;
    }

    PyObject *args = Py_BuildValue("(ds)", x, argv[4]);

    if (args == NULL)
    {
        PyErr_Print();
        Py_DECREF(function);
        Py_DECREF(module);
        Py_Finalize();
        return 1;
    }

    PyObject *result = PyObject_CallObject(function, args);

    if (result == NULL)
    {
        PyErr_Print();
        Py_DECREF(args);
        Py_DECREF(function);
        Py_DECREF(module);
        Py_Finalize();
        return 1;
    }

    double output = PyFloat_AsDouble(result);

    if (PyErr_Occurred())
    {
        PyErr_Print();
        Py_DECREF(result);
        Py_DECREF(args);
        Py_DECREF(function);
        Py_DECREF(module);
        Py_Finalize();
        return 1;
    }

    printf("Result: %f\n", output);

    Py_DECREF(result);
    Py_DECREF(args);
    Py_DECREF(function);
    Py_DECREF(module);

    Py_Finalize();

    return 0;
}

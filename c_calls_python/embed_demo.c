
#include <Python.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        printf("Usage: ./embed_demo <number> <mode>\n");
        return 1;
    }

    double x = atof(argv[1]);

    Py_Initialize();

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.insert(0, 'c_calls_python')");
    PyObject *module = PyImport_ImportModule("policies");

    if (module == NULL)
    {
        PyErr_Print();
        Py_Finalize();
        return 1;
    }

    PyObject *function = PyObject_GetAttrString(module, "transform");

    if (function == NULL || !PyCallable_Check(function))
    {
        PyErr_Print();
        printf("Could not find callable transform function.\n");
        Py_XDECREF(function);
        Py_DECREF(module);
        Py_Finalize();
        return 1;
    }

    PyObject *args = Py_BuildValue("(ds)", x, argv[2]);

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

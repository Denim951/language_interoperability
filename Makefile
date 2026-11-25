
CC = gcc
CFLAGS = -Wall -Wextra -O2

# Python configuration
PYTHON_CONFIG = python3-config
PYTHON_INCLUDES = $(shell $(PYTHON_CONFIG) --includes)
PYTHON_LDFLAGS = $(shell $(PYTHON_CONFIG) --embed --ldflags)

# These are actions, not actual files
.PHONY: all demo pipes python-c test clean

# Default target: build everything
all: python_calls_c/libnumeric.so c_calls_python/embed_demo shell_pipes/producer

# Python calls C using ctypes
python_calls_c/libnumeric.so: python_calls_c/numeric.c python_calls_c/numeric.h
	$(CC) $(CFLAGS) -shared -fPIC -o $@ python_calls_c/numeric.c

# C embeds Python and calls a Python function
c_calls_python/embed_demo: c_calls_python/embed_demo.c
	$(CC) $(CFLAGS) $(PYTHON_INCLUDES) -o $@ $< $(PYTHON_LDFLAGS)

# C program sends output through a shell pipe
shell_pipes/producer: shell_pipes/producer.c
	$(CC) $(CFLAGS) -o $@ $<

# Run C calling Python
demo: c_calls_python/embed_demo
	./c_calls_python/embed_demo 4 square

# Run shell pipe communication
pipes: shell_pipes/producer
	./shell_pipes/producer | python3 shell_pipes/consumer.py

# Run Python calling C
python-c: python_calls_c/libnumeric.so
	python3 python_calls_c/numeric_wrapper.py

# Run unit tests
test:
	python3 -m unittest discover -s tests -v

# Remove generated files
clean:
	rm -f python_calls_c/libnumeric.so
	rm -f c_calls_python/embed_demo
	rm -f shell_pipes/producer
	rm -rf __pycache__ python_calls_c/__pycache__ c_calls_python/__pycache__ shell_pipes/__pycache__

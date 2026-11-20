
CC = gcc
CFLAGS = -Wall -Wextra -O2

PYTHON_CONFIG = python3-config // tells GCC where to find Python.h
PYTHON_INCLUDES = $(shell $(PYTHON_CONFIG) --includes) // $(shell ...) tells Make to execute a shell command and capture its output
PYTHON_LDFLAGS = $(shell $(PYTHON_CONFIG) --embed --ldflags) //retrieves the linker flags required to embed Python

.PHONY: all demo pipes python-c clean //tells Make that these names represent actions, not actual files

all: python_calls_c/libnumeric.so c_calls_python/embed_demo shell_pipes/producer

python_calls_c/libnumeric.so: python_calls_c/numeric.c python_calls_c/numeric.h
	$(CC) $(CFLAGS) -shared -fPIC -o $@ python_calls_c/numeric.c

c_calls_python/embed_demo: c_calls_python/embed_demo.c
	$(CC) $(CFLAGS) $(PYTHON_INCLUDES) -o $@ $< $(PYTHON_LDFLAGS)

shell_pipes/producer: shell_pipes/producer.c
	$(CC) $(CFLAGS) -o $@ $<

demo: c_calls_python/embed_demo
	./c_calls_python/embed_demo 4 square

pipes: shell_pipes/producer
	./shell_pipes/producer | python3 shell_pipes/consumer.py

python-c: python_calls_c/libnumeric.so
	python3 python_calls_c/numeric_wrapper.py

clean:
	rm -f python_calls_c/libnumeric.so
	rm -f c_calls_python/embed_demo
	rm -f shell_pipes/producer
	rm -rf __pycache__ python_calls_c/__pycache__ c_calls_python/__pycache__ shell_pipes/__pycache__

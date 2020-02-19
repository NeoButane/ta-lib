OS:=$(shell uname -s)

ifeq ($(OS),Linux)
  NPROC    = "-j $(shell nproc --all)"
else
  NPROC    = "-j1"
endif

.PHONY: build

build:
	python setup.py build_ext --inplace $(NPROC)

install:
	pip install -e . -v --no-binary TA-Lib

talib/_func.pxi: tools/generate_func.py
	python tools/generate_func.py > talib/_func.pxi

talib/_stream.pxi: tools/generate_stream.py
	python tools/generate_stream.py > talib/_stream.pxi

generate: talib/_func.pxi talib/_stream.pxi

cython:
	cython --directive emit_code_comments=False talib/_ta_lib.pyx

clean:
	rm -rf build talib/_ta_lib.so talib/*.pyc

perf:
	python tools/perf_talib.py

test: build
	LD_LIBRARY_PATH=${VIRTUAL_ENV}/lib:/usr/local/lib:${LD_LIBRARY_PATH} nosetests

sdist:
	python setup.py sdist --formats=gztar,zip

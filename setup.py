#!/usr/bin/env python

import sys
import os
import warnings

# Check if shell is currently in a virtual environment
# https://stackoverflow.com/a/40099080
try:
    os.environ['VIRTUAL_ENV']
except KeyError:
    print('VIRTUAL_ENV not set, exiting')
    exit()

_install_prefix = os.environ['VIRTUAL_ENV']
#_include_prefix = os.environ['VIRTUAL_ENV'] + '/include'
#_lib_prefix = os.environ['VIRTUAL_ENV'] + /

from distutils.dist import Distribution

display_option_names = Distribution.display_option_names + ['help', 'help-commands']
query_only = any('--' + opt in sys.argv for opt in display_option_names) or len(sys.argv) < 2 or sys.argv[1] == 'egg_info'

try:
    from setuptools import setup, Extension
    requires = {"install_requires": ["numpy"]}
except:
    from distutils.core import setup
    from distutils.extension import Extension
    requires = {"requires": ["numpy"]}

lib_talib_name = 'ta_lib'  # the underlying C library's name

runtime_lib_dirs = []

platform_supported = False
for prefix in ['darwin', 'linux', 'bsd', 'sunos']:
    if prefix in sys.platform:
        platform_supported = True
        include_dirs = [
            _install_prefix + '/include',
            _install_prefix + '/usr/include',
            '/usr/include',
            '/usr/local/include',
            '/opt/include',
            '/opt/local/include',
        ]
        if 'TA_INCLUDE_PATH' in os.environ:
            include_dirs.append(os.environ['TA_INCLUDE_PATH'])
        else:
            print("Remember to set TA_INCLUDE_PATH in your virtual environment!")
            include_dirs.append(['VIRTUAL_ENV'])
        lib_talib_dirs = [
            _install_prefix + '/lib',
            _install_prefix + '/lib64',
            _install_prefix + '/usr/lib',
            _install_prefix + '/lib',
            _install_prefix + '/usr/lib64',
            '/usr/local/lib',
            '/usr/lib64',
            '/usr/local/lib64',
            '/opt/lib',
            '/opt/local/lib',
        ]
        if 'TA_LIBRARY_PATH' in os.environ:
            runtime_lib_dirs = os.environ['TA_LIBRARY_PATH']
            if runtime_lib_dirs:
                runtime_lib_dirs = runtime_lib_dirs.split(os.pathsep)
                lib_talib_dirs.extend(runtime_lib_dirs)
        else:
           TA_LIBRARY_PATH = _install_prefix + '/lib'
           print("Remember to set TA_LIBRARY_PATH in your virtual environment!")
        break

if sys.platform == "win32":
    platform_supported = True
    lib_talib_name = 'ta_libc_cdr'
    include_dirs = [r"c:\ta-lib\c\include"]
    lib_talib_dirs = [r"c:\ta-lib\c\lib"]

if not platform_supported:
    raise NotImplementedError(sys.platform)

# Do not require numpy or cython for just querying the package
if not query_only:
    import numpy
    include_dirs.insert(0, numpy.get_include())

try:
    from Cython.Distutils import build_ext
    has_cython = True
except ImportError:
    has_cython = False

for lib_talib_dir in lib_talib_dirs:
    try:
        files = os.listdir(lib_talib_dir)
        if any(lib_talib_name in f for f in files):
            break
    except OSError:
        pass
else:
    warnings.warn('Cannot find ta-lib library, installation may fail.')

cmdclass = {}
if has_cython:
    cmdclass['build_ext'] = build_ext

ext_modules = [
    Extension(
        'talib._ta_lib',
        ['talib/_ta_lib.pyx' if has_cython else 'talib/_ta_lib.c'],
        include_dirs=include_dirs,
        library_dirs=lib_talib_dirs,
        libraries=[lib_talib_name],
        runtime_library_dirs=runtime_lib_dirs
    )
]

setup(
    name = 'TA-Lib',
    version = '0.4.18',
    description = 'Python wrapper for TA-Lib',
    author = 'John Benediktsson',
    author_email = 'mrjbq7@gmail.com',
    url = 'http://github.com/mrjbq7/ta-lib',
    download_url = 'https://github.com/mrjbq7/ta-lib/releases',
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Cython",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
    ],
    packages = ['talib'],
    ext_modules = ext_modules,
    cmdclass = cmdclass,
    **requires
)

if 'TA_INCLUDE_PATH' not in os.environ:
   print("\033[1;31;40mRemember to set TA_INCLUDE_PATH in your virtual environment!")
if 'TA_LIBRARY_PATH' not in os.environ:
    print("\033[1;31;40mRemember to set TA_LIBRARY_PATH in your virtual environment!")

# os-rotatefile
[![Build Status](https://www.travis-ci.org/cfhamlet/os-rotatefile.svg?branch=master)](https://www.travis-ci.org/cfhamlet/os-rotatefile)
[![codecov](https://codecov.io/gh/cfhamlet/os-rotatefile/branch/master/graph/badge.svg)](https://codecov.io/gh/cfhamlet/os-rotatefile)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/os-rotatefile.svg)](https://pypi.python.org/pypi/os-rotatefile)
[![PyPI](https://img.shields.io/pypi/v/os-rotatefile.svg)](https://pypi.python.org/pypi/os-rotatefile)

Read and write size rotate file.

# Install
  `pip install os-rotatefile`

# Usage
  * Write
  ```
    from os_roatefile import open_file

    f = open_file('file', 'w', roll_size='1G')
    f.write('Your data')
    f.close()
  ```
  * Read
  ```
    from os_roatefile import open_file

    f = open_file('file', 'r', buffer_size='128K')
    f.readline()
    f.read(100)
    if not f.read():
        f.close()
  ```


# Unit Tests
  `$ tox`

# License
MIT licensed.


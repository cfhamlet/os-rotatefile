import os

import pytest
from os_rotatefile import open_file
from os_rotatefile.rotatefile import valid_size


def test_flush(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('abc', 'w')
        f.write(b'data1')
        f.flush()
        f.close()
        with pytest.raises(ValueError):
            f.flush()


def test_read_single_file(tmpdir):
    with tmpdir.as_cwd():
        word = b"abc"
        f = tmpdir.join('abc')
        f.write(word)
        f = open_file('abc', 'r')
        c = f.read()
        assert c == word


def test_write_append(tmpdir):
    with tmpdir.as_cwd():
        f1 = tmpdir.join('abc0')
        f1.write(b'abc')
        f = open_file('abc', 'w', roll_size=4)
        f.write(b'1234')
        f.close()
        f = open('abc0', 'rb')
        c = f.read()
        assert c == b'abc1'
        f = open('abc1', 'rb')
        c = f.read()
        assert c == b'234'


def test_write_max_idx(tmpdir):
    with tmpdir.as_cwd():
        f1 = tmpdir.join('abc0')
        f1.write(b'abc')
        f1 = tmpdir.join('abc3')
        f1.write(b'123')
        f = open_file('abc', 'w', roll_size=3)
        f.write(b'xyz')
        f.close()
        f = open('abc4')
        c = f.read()
        assert len(c) == 3


def test_mode(tmpdir):
    with tmpdir.as_cwd():
        with pytest.raises(ValueError):
            open_file('abc', 'c')


def test_close(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('abc', 'w', roll_size=10)
        f.write(b'abc')
        f.close()
        assert f.closed == True
        with pytest.raises(ValueError):
            f.write(b'123')


def test_readline(tmpdir):
    with tmpdir.as_cwd():
        t1 = tmpdir.join('abc0')
        t1.write(b'abc')
        t2 = tmpdir.join('abc1')
        t2.write(b'123\n')
        f = open_file('abc', 'r')
        assert f.readline() == b'abc123\n'


def test_read_not_exist():
    with pytest.raises(IOError):
        open('not_exist', 'r')


def test_read(tmpdir):
    with tmpdir.as_cwd():
        t1 = tmpdir.join('abc0')
        t1.write(b'abc')
        t2 = tmpdir.join('abc1')
        t2.write(b'123')
        f = open_file('abc', 'r')
        assert f.read(10) == b'abc123'
        f = open_file('abc', 'r')
        assert f.read() == b'abc123'
        f = open_file('abc', 'r', buffer_size=2)
        assert f.read() == b'ab'
        assert f.read() == b'c1'
        assert f.read() == b'23'


def test_write_rotate(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('abc', 'w', roll_size=10)
        f.write(b'1' * 100)
        f.close()
        for i in range(0, 10):
            fn = 'abc%d' % i
            assert os.path.exists(fn)
            assert os.path.getsize(fn) == 10


def test_valid_roll_size():
    data = [
        ('1', 1),
        ('1k', 1024),
        ('1K', 1024),
        ('1m', 1024 * 1024),
        ('1M', 1024 * 1024),
        ('1g', 1024 * 1024 * 1024),
        ('1G', 1024 * 1024 * 1024),
        (100, 100),
        ('1.2k', int(1.2 * 1024))
    ]

    for k, v in data:
        assert valid_size(k) == v

    with pytest.raises(TypeError):
        valid_size(True)
    with pytest.raises(ValueError):
        valid_size('-1k')
    with pytest.raises(ValueError):
        valid_size('0')
    with pytest.raises(ValueError):
        valid_size(str(1024**10))

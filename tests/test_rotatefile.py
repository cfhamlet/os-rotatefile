import os
import pytest
import StringIO
from os_rotatefile import open_file
from os_rotatefile.rotatefile import valid_roll_size


def test_write_append(tmpdir):
    with tmpdir.as_cwd():
        f1 = tmpdir.join('abc0')
        f1.write('abc')
        f = open_file('abc', 'w', roll_size=4)
        f.write('1234')
        f.close()
        f = open('abc0')
        c = f.read()
        assert c == 'abc1'
        f = open('abc1')
        c = f.read()
        assert c == '234'


def test_write_max_idx(tmpdir):
    with tmpdir.as_cwd():
        f1 = tmpdir.join('abc0')
        f1.write('abc')
        f1 = tmpdir.join('abc3')
        f1.write('123')
        f = open_file('abc', 'w', roll_size=3)
        f.write('xyz')
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
        f.write('abc')
        f.close()
        assert f.closed == True
        with pytest.raises(ValueError):
            f.write('123')


def test_readline(tmpdir):
    with tmpdir.as_cwd():
        t1 = tmpdir.join('abc0')
        t1.write('abc')
        t2 = tmpdir.join('abc1')
        t2.write('123\n')
        f = open_file('abc', 'r')
        assert f.readline() == 'abc123\n'


def test_read_not_exist():
    with pytest.raises(IOError):
        open('not_exist', 'r')


def test_read(tmpdir):
    with tmpdir.as_cwd():
        t1 = tmpdir.join('abc0')
        t1.write('abc')
        t2 = tmpdir.join('abc1')
        t2.write('123')
        f = open_file('abc', 'r')
        assert f.read(10) == 'abc123'


def test_write_rotate(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('abc', 'w', roll_size=10)
        f.write('1' * 100)
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
        assert valid_roll_size(k) == v

    with pytest.raises(TypeError):
        valid_roll_size(True)

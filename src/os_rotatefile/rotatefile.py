import os
import sys
from io import BytesIO

_PY3 = sys.version_info[0] == 3
if _PY3:
    string_types = str
    integer_types = int

else:
    string_types = basestring
    integer_types = (int, long)


def _complain_ifclosed(closed):
    if closed:
        raise ValueError("I/O operation on closed file")


class RotateBase(object):
    def __init__(self, base_filename):
        self._prefix = os.path.basename(base_filename)
        self._path = os.path.abspath(os.path.dirname(base_filename))
        self._fp = None
        self._idx = -1
        self.closed = True

    def _get_filename(self, idx):
        if idx < 0:
            raise ValueError('idx must >= 0')
        return os.path.join(self._path, '%s%d' % (self._prefix, idx))

    def close(self):
        if self.closed:
            return
        if self._fp is not None:
            self._fp.close()
            self._fp = None
        self.closed = True


class RotateReader(RotateBase):
    def __init__(self, base_filename, buffer_size='128k'):
        super(RotateReader, self).__init__(base_filename)
        self._idx = None
        self._end = False
        self._buffer_size = valid_size(buffer_size)
        self._open_next()

    def _open_next(self):
        if self._end:
            return
        if self._idx is None:
            for x in [x for x in os.listdir(self._path) if x.startswith(self._prefix)]:
                idx = x[len(self._prefix):]
                if not idx.isdigit():
                    continue
                if idx.startswith('0') and idx != '0':
                    continue
                idx = int(idx)
                if idx < 0:
                    continue
                self._idx = idx if self._idx is None else min(
                    self._idx, idx)
            if self._idx is not None:
                self._idx -= 1
            else:
                raise IOError('file not found')

        self._idx += 1
        filename = self._get_filename(self._idx)
        self._fp = open(filename, "rb")
        self.closed = False

    def read(self, size=-1):
        if size < 0:
            size = self._buffer_size
        _complain_ifclosed(self.closed)
        assert size >= 0, 'size must >= 0'
        if self._end or size == 0:
            return b''
        buf = BytesIO()
        need = size
        while buf.tell() < size:
            data = self._fp.read(need)
            if not data:
                try:
                    self._fp.close()
                    self._open_next()
                    continue
                except IOError:
                    self._end = True
                    break

            buf.write(data)
            need = size - buf.tell()

        buf.seek(0)
        return buf.read()

    def readline(self):
        _complain_ifclosed(self.closed)
        if self._end:
            return b''
        buffer = BytesIO()
        e = b''
        while e != b'\n':
            line = self._fp.readline()
            if not line:
                try:
                    self._fp.close()
                    self._open_next()
                except IOError:
                    self._end = True
                    break
            buffer.write(line)
            buffer.seek(-1, 1)
            e = buffer.read(1)
        buffer.seek(0)
        return buffer.read()


class RotateWriter(RotateBase):
    def __init__(self, base_filename, roll_size='1G'):
        super(RotateWriter, self).__init__(base_filename)
        self._roll_size = valid_size(roll_size)
        assert self._roll_size > 0, 'roll_size must > 0'
        self._size = -1
        self._open_next()

    def _open_next(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)

        if self._idx < 0:
            for x in [x for x in os.listdir(self._path) if x.startswith(self._prefix)]:
                idx = x[len(self._prefix):]
                if not idx.isdigit():
                    continue
                if idx.startswith('0') and idx != '0':
                    continue
                idx = int(idx)
                if idx < 0:
                    continue
                self._idx = max(self._idx, int(idx))

            if self._idx >= 0:
                filename = self._get_filename(self._idx)
                size = os.path.getsize(filename)
                if size < self._roll_size:
                    self._idx -= 1

        self._idx += 1
        filename = self._get_filename(self._idx)
        self._fp = open(filename, "ab")
        self._size = os.path.getsize(filename)
        self.closed = False

    def write(self, data, flush=False):
        _complain_ifclosed(self.closed)
        if not isinstance(data, bytes):
            raise TypeError('unsupported type: {}'.format(type(data).__name__))
        if self._fp is None:
            self._open_next()
        while True:
            can_write = self._roll_size - self._size
            if len(data) <= can_write:
                self._fp.write(data)
                if flush:
                    self._fp.flush()
                self._size += len(data)
                break
            elif can_write > 0:
                self._fp.write(data[:can_write])
                self._size += can_write
                self.close()
                self._open_next()
                data = data[can_write:]
            else:
                self.close()
                self._open_next()

    def flush(self):
        _complain_ifclosed(self.closed)
        self._fp.flush()


def open_file(name, mode='r', **kwargs):
    base_filename = os.path.basename(name)
    if not base_filename:
        raise ValueError("not support open path")

    if os.path.isfile(name) and mode == 'r':
        return open(name, 'rb')

    def not_support(name, **kwargs):
        raise ValueError("mode must be 'r' or 'w'")
    c = {'w': RotateWriter, 'r': RotateReader}.get(mode, not_support)
    return c(name, **kwargs)


MAX_FILE_SIZE = 1024 ** 4


def valid_size(size):
    if not isinstance(size, (integer_types, string_types)) or isinstance(size, bool):
        raise TypeError('size must be int or string type')
    if isinstance(size, integer_types):
        size = str(int(size))
    else:
        size = size.lower()
    multi = 1
    weight = {'k': 1, 'm': 2, 'g': 3, 't': 4}
    if size[-1] in weight:
        multi = pow(1024, weight[size[-1]])
        size = size[:-1]
    r = int(float(size) * multi)
    if r <= 0:
        raise ValueError('size must > 0')
    elif r > MAX_FILE_SIZE:
        raise ValueError('size must <= %d' % MAX_FILE_SIZE)
    return r

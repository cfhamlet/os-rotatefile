import os
import six
import sys
import StringIO


def _complain_ifclosed(closed):
    if closed:
        raise ValueError, "I/O operation on closed file"


class RotateBase(object):
    def __init__(self, base_filename):
        self._prefix = os.path.basename(base_filename)
        self._path = os.path.abspath(os.path.dirname(base_filename))
        self._fp = None
        self._idx = -1
        self.closed = True

    def _get_filename(self, idx):
        if idx < 0:
            raise ValueError, 'idx must >= 0'
        return os.path.join(self._path, '%s%d' % (self._prefix, idx))

    def close(self):
        if self.closed:
            return
        if self._fp is not None:
            self._fp.close()
            self._fp = None
        self.closed = True


class RotateReader(RotateBase):
    def __init__(self, base_filename):
        super(RotateReader, self).__init__(base_filename)
        self._idx = None
        self._end = False
        self._open_next()

    def _open_next(self):
        if self._end:
            return
        if self._idx is None:
            self._idx = sys.maxint
            has_min = False
            for x in [x for x in os.listdir(self._path) if x.startswith(self._prefix)]:
                try:
                    self._idx = min(
                        self._idx, int(x[len(self._prefix):]))
                    has_min = True
                except:
                    continue
            if has_min and self._idx >= 0:
                self._idx += -1

        self._idx += 1
        filename = self._get_filename(self._idx)
        self._fp = open(filename, "r")
        self.closed = False

    def read(self, size):
        _complain_ifclosed(self.closed)
        assert size >= 0, 'size must >= 0'
        if self._end or size == 0:
            return ''
        buffer = StringIO.StringIO()
        need = size
        while buffer.len < size:
            data = self._fp.read(need)
            if not data:
                try:
                    fp = self._fp
                    self._open_next()
                    fp.close()
                    continue
                except IOError:
                    self._end = True
                    break

            buffer.write(data)
            need = size - buffer.len

        buffer.seek(0)
        return buffer.read()

    def readline(self):
        _complain_ifclosed(self.closed)
        if self._end:
            return ''
        buffer = StringIO.StringIO()
        e = ''
        while e != '\n':
            line = self._fp.readline()
            if not line:
                try:
                    fp = self._fp
                    self._open_next()
                    fp.close
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
        self._roll_size = valid_roll_size(roll_size)
        assert self._roll_size > 0, 'roll_size must > 0'
        self._size = -1
        self._open_next()

    def _open_next(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)

        if self._idx < 0:
            for x in [x for x in os.listdir(self._path) if x.startswith(self._prefix)]:
                try:
                    self._idx = max(
                        self._idx, int(x[len(self._prefix):]))
                except:
                    continue

            if self._idx >= 0:
                filename = self._get_filename(self._idx)
                size = os.path.getsize(filename)
                if size < self._roll_size:
                    self._idx += -1

        self._idx += 1
        filename = self._get_filename(self._idx)
        self._fp = open(filename, "a")
        self._size = os.path.getsize(filename)
        self.closed = False

    def write(self, data, flush=False):
        _complain_ifclosed(self.closed)
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


def open_file(name, mode='r', **kwargs):
    def not_support(name, **kwargs):
        raise ValueError, "mode must be 'r' or 'w'"
    c = {'w': RotateWriter, 'r': RotateReader}.get(mode, not_support)
    return c(name, **kwargs)


def valid_roll_size(roll_size):
    if not isinstance(roll_size, (six.types.IntType, six.types.StringType)) or isinstance(roll_size, six.types.BooleanType):
        raise TypeError, 'roll_size must be int or string type'
    if isinstance(roll_size, six.types.IntType):
        roll_size = int(roll_size)
        return roll_size
    roll_size = roll_size.lower()
    multi = 1
    for idx, x in enumerate(["k", "m", "g"]):
        if x == roll_size[-1]:
            roll_size = roll_size[:-1]
            multi = pow(1024, idx + 1)
    return int(float(roll_size) * multi)

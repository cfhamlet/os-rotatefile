import sys
from .rotatefile import open_file
__all__ = ['__version__', 'version_info', 'open_file']

import pkgutil
__version__ = pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()
version_info = tuple(int(v) if v.isdigit() else v
                     for v in __version__.split('.'))
del pkgutil

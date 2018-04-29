# -*- coding: utf-8 -*-

from six import PY3
from six import string_types
from six import binary_type
from six import text_type

basestring = string_types
bytes = binary_type
unicode = text_type

try:
    import queue as Queue
except ImportError:
    import Queue


__all__ = (
    'PY3',
    'basestring',
    'bytes',
    'unicode',
    'Queue',
    'string_types',
    'binary_type',
    'text_type',
)

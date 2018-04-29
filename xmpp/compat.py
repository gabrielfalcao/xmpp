# -*- coding: utf-8 -*-
import codecs
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


def encode_b64(s):
    return cast_string(codecs.encode(cast_bytes(s), 'base64'))


def decode_b64(s):
    return cast_string(codecs.decode(cast_bytes(s), 'base64'))


def cast_bytes(s, encoding='utf-8'):
    if isinstance(s, binary_type):
        return s
    elif isinstance(s, text_type):
        return s.encode(encoding)

    return cast_bytes(text_type(s))


def cast_string(s, encoding='utf-8'):
    if isinstance(s, text_type):
        return s
    elif isinstance(s, binary_type):
        return s.decode(encoding)

    return text_type(s)


__all__ = (
    'PY3',
    'basestring',
    'bytes',
    'unicode',
    'Queue',
    'string_types',
    'binary_type',
    'text_type',
    'cast_string',
    'cast_bytes',
)

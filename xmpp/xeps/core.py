#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xmpp._registry import _EXTENSION_MAPPING


class MetaExtension(type):
    def __init__(ExtensionClass, name, bases, members):
        xep = members.get("__xep__") or getattr(ExtensionClass, '__xep__', None)

        if name == 'Extension':
            return super(MetaExtension, ExtensionClass).__init__(name, bases, members)

        if not xep:
            raise ExtensionDefinitionError('missing __xep__ attribute')

        if not xep.isdigit():
            raise ExtensionDefinitionError('__xep__ must be a string containg only numbers')

        if xep in _EXTENSION_MAPPING:
            other = _EXTENSION_MAPPING[xep]
            msg = 'xep {0} is already defined by {1}.{2}'
            raise ExtensionDefinitionError(msg.format(xep, other, other.__module__))

        _EXTENSION_MAPPING[xep] = ExtensionClass

        super(MetaExtension, ExtensionClass).__init__(name, bases, members)


class ExtensionDefinitionError(Exception):
    pass


class Extension(object):
    __metaclass__ = MetaExtension

    def __init__(self, stream):
        self.stream = stream
        self.initialize()

    def initialize(self):
        pass


def get_known_extensions():
    return _EXTENSION_MAPPING.items()

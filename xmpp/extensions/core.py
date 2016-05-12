#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xmpp._registry import _EXTENSION_MAPPING


class MetaExtension(type):
    def __init__(ExtensionClass, name, bases, members):
        xep = members.get("__xep__", getattr(ExtensionClass, '__xep__', None))
        init = members.get("initialize", getattr(ExtensionClass, 'initialize', None))

        if name == 'Extension':
            return super(MetaExtension, ExtensionClass).__init__(name, bases, members)

        if not xep:
            msg = 'class {0} is missing __xep__ attribute'.format(name)
            raise ExtensionDefinitionError(msg)

        if not xep.isdigit():
            msg = '{0}.__xep__ must be a string containg only numbers: {1}'.format(name, xep)
            raise ExtensionDefinitionError(msg)

        if xep in _EXTENSION_MAPPING:
            other = _EXTENSION_MAPPING[xep]
            msg = 'xep {0} is already defined by {1}.{2}'
            raise ExtensionDefinitionError(msg.format(xep, other.__module__, other.__name__))

        if not init:
            msg = 'extension {0}.{1}[{2}] needs an initialize(self) method defined, even if blank'
            raise ExtensionDefinitionError(msg.format(ExtensionClass.__module__, name, xep))
        elif not callable(init):
            msg = 'extension {0}.{1}.initialize must be a callable'
            raise ExtensionDefinitionError(msg.format(ExtensionClass.__module__, name))

        _EXTENSION_MAPPING[xep] = ExtensionClass

        super(MetaExtension, ExtensionClass).__init__(name, bases, members)


class ExtensionDefinitionError(Exception):
    pass


class Extension(object):
    __metaclass__ = MetaExtension

    def __init__(self, stream):
        self.stream = stream
        self.initialize()


def get_known_extensions():
    return _EXTENSION_MAPPING.items()

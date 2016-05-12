#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import uuid
import xml.etree.ElementTree as ET

from collections import OrderedDict
from xmpp._registry import _NODE_MAPPING


def split_tag_and_namespace(attribute):
    found = re.search(r'^\s*([{](.*)[}])?\s*(\w+)\s*', attribute.strip()).groups()
    _, ns, name = found

    if not ns:
        return attribute, ''

    return name.strip(), ns.strip()


def fixup_unknown_element(element, uri_map=None):
    uri_map = uri_map or {}
    tag, xmlns = split_tag_and_namespace(element.tag)
    element.tag = tag

    for name in list(element.attrib):
        value = element.attrib.pop(name)
        attr, ns = split_tag_and_namespace(name)
        if ns not in uri_map:
            uri_map[ns] = attr

        if ns:
            new = ':'.join(['xmlns', attr])
        else:
            new = attr
        element.set(new, value)

    element.set('xmlns', xmlns)

    for child in element.getchildren():
        fixup_element(child, uri_map)

    return element


def fixup_element(original_elem, uri_map=None):
    if '{' not in original_elem.tag:
        return original_elem

    elem = original_elem
    uri_map = uri_map or {}

    # build uri map and add to root element
    node = _NODE_MAPPING.get(elem.tag)
    if not node:
        return fixup_unknown_element(original_elem)

    elem.tag = node.__tag__
    for prefix, uri in OrderedDict(node.__namespaces__).items():
        uri_map[uri] = prefix
        if prefix:
            elem.set(b":".join([b'xmlns', bytes(prefix)]), uri)
        else:
            elem.set(b"xmlns", bytes(uri))

    for elem in elem.getiterator():
        fixup_element(elem, uri_map)

    return original_elem


def node_to_string(node):
    if node._element is not None:
        element = node._element.copy()
    else:
        element = ET.Element(node.tag, node.attr)

    fixup_element(element)

    output = ET.tostring(element, 'utf-8')

    return output


def generate_id():
    return bytes(uuid.uuid4())


__all__ = [
    'split_tag_and_namespace',
    'ET',
    'node_to_string',
]

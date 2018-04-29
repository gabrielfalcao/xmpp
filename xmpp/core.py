# -*- coding: utf-8 -*-
#
# <xmpp - stateless and concurrency-agnostic XMPP library for python>
#
# Copyright (C) <2016-2017> Gabriel Falcao <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



import re
import uuid
import xml.etree.ElementTree as ET
from collections import OrderedDict

from xmpp.compat import text_type
from xmpp.compat import cast_string
from xmpp.compat import cast_bytes

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

        element.set(attr, value)

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
            elem.set(":".join(['xmlns', text_type(prefix)]), uri)
        else:
            elem.set("xmlns", text_type(uri))

    for elem in elem.getiterator():
        fixup_element(elem, uri_map)

    return original_elem


def copy_element(element, encoding='utf-8'):
    return element


def raw_element_to_string(element, encoding='utf-8'):
    return ET.tostring(element, encoding)


def element_to_string(element, encoding='utf-8'):
    fixup_element(element)
    return raw_element_to_string(element, encoding)


def node_to_string(node, encoding='utf-8'):
    element = copy_element(node._element)
    output = element_to_string(element, encoding)
    return cast_string(output, encoding)


def generate_id():
    return cast_bytes(uuid.uuid4())


def is_element(element):
    return ET.iselement(element)


__all__ = [
    'split_tag_and_namespace',
    'ET',
    'node_to_string',
]

# <xmpp - stateless and concurrency-agnostic XMPP library for python>
#
# (C) Copyright 2016 Gabriel Falcao <gabriel@nacaolivre.org>
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

from collections import OrderedDict
from xmpp.core import ET
from xmpp.core import node_to_string
from xmpp.core import split_tag_and_namespace
from xmpp.core import fixup_element
from xmpp._registry import _NODE_MAPPING


class MetaNode(type):
    def __init__(NodeClass, name, bases, members):
        if name == 'Node':
            return super(MetaNode, NodeClass).__init__(name, bases, members)

        tag = (members.get("__tag__") or getattr(NodeClass, '__tag__', None) or '').strip()
        namespaces = members.get("__namespaces__") or getattr(NodeClass, '__namespaces__', None) or []

        etag = (members.get("__etag__") or getattr(NodeClass, '__etag__', tag) or '').strip()
        children_of = members.get("__children_of__") or getattr(NodeClass, '__children_of__', None)

        xmlns = dict(namespaces).get('', None)

        if etag and etag != tag:
            _NODE_MAPPING[etag] = NodeClass

        if tag and xmlns:
            _NODE_MAPPING[(tag, xmlns)] = NodeClass

        NodeClass.__children__ = []
        NodeClass.__tag__ = tag.strip()
        NodeClass.__etag__ = etag.strip()
        NodeClass.__namespaces__ = namespaces

        if children_of:
            siblings = getattr(children_of, '__children__', [])
            siblings.append(NodeClass)
            children_of.__children__ = siblings

        super(MetaNode, NodeClass).__init__(name, bases, members)


class Node(object):
    __tag__ = None
    __etag__ = None
    __namespaces__ = []
    __prefixes__ = None
    __single__ = False
    __children_of__ = None

    __metaclass__ = MetaNode

    def __init__(self, element, closed=False):
        # self._original = element.copy()
        self._element = fixup_element(element)
        self._closed = closed or self.__single__
        if not element.tag:
            raise TypeError('invalid element {0}'.format(element))

        self._tag, self._namespaces = self.extract_namespace(element.tag)

        self._attributes = OrderedDict()
        for attr in element.attrib:
            clean, namespace = self.extract_namespace(attr)
            self._namespaces.update(namespace)
            self._attributes[clean] = element.attrib[attr]

        self.initialize()

    def initialize(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.to_dict() == other.to_dict()

    def close(self):
        self._closed = True

    def is_parent_of(self, other_node):
        return other_node.__children_of__ == self.__class__

    @classmethod
    def extract_namespace(cls, attribute):
        name, ns = split_tag_and_namespace(attribute.strip())
        if not ns:
            return attribute, OrderedDict()

        return name, OrderedDict([(name, ns)])

    @classmethod
    def create(cls, **kw):
        etag = cls.__etag__
        if not etag:
            etag = cls.__tag__

        element = ET.Element(
            etag,
            **kw
        )
        return Node.from_element(element)

    @property
    def tag(self):
        return self._tag

    @property
    def attr(self):
        return self._attributes.copy()

    @property
    def namespaces(self):
        return self._namespaces.copy()

    @property
    def is_closed(self):
        return self.__single__ or self._closed

    def query(self, xpath):
        items = []
        for element in self._element.findall(xpath):
            items.append(Node.from_element(element, allow_fixedup=True))

        return items

    def get(self, xpath):
        element = self._element.find(xpath)
        if element is None:
            return

        return Node.from_element(element, allow_fixedup=True)

    def get_children(self):
        return [Node.from_element(e, allow_fixedup=True) for e in self._element.getchildren()]

    def get_value(self):
        return self._element.text or b''

    def set_value(self, value):
        self._element.text = value

    value = property(fset=set_value, fget=get_value)

    @classmethod
    def from_xml(cls, xml):
        node = ET.fromstring(xml)

        return Node.from_element(node)

    def add_text(self, text):
        if not self._element.text:
            self._element.text = b''

        self._element.text += bytes(text)

        enclosing = '</{0}>'.format(self.tag)
        if enclosing in text or text.strip().endswith('/>'):
            self.close()

    def append(self, node):
        if self.is_closed:
            raise TypeError('I refuse to append a child in a closed node')

        self._element.append(node._element)

    def to_dict(self):
        data = {
            'tag': self.tag,
        }
        if not self.__single__:
            data['nodes'] = [Node.from_element(c).to_dict() for c in self._element]

        if self.value:
            data['value'] = self.value

        if self.attr:
            data['attributes'] = dict(self.attr)

        if self.namespaces:
            data['namespaces'] = dict(self.namespaces)

        return data

    def to_xml(self):
        return node_to_string(self)

    def __str__(self):
        return self.to_xml()

    def __repr__(self):
        if self._element is None:
            return '{0}(_element=None)'.format(self.__class__.__name__)

        return '{3}(tag={0}, attributes={1}, namespaces={2})'.format(
            self._element.tag,
            self.attr,
            self.namespaces,
            self.__class__.__name__
        )

    @staticmethod
    def from_element(element, allow_fixedup=False):
        NodeClass = _NODE_MAPPING.get(element.tag, None)

        if allow_fixedup and NodeClass is None:
            # element might be fixed up already, let's
            # try to fetch its Node
            key = element.tag, element.attrib.get('xmlns')
            NodeClass = _NODE_MAPPING.get(key, None)

        if NodeClass is None:
            # could not find any specialized Node subclasses to
            # represent this `element` let's fallback to Node
            NodeClass = Node

        return NodeClass(element)

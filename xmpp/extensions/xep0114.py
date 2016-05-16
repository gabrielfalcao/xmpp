# -*- coding: utf-8 -*-
#
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

import hashlib
from speakers import Speaker as Events
from xmpp.models import Node, StartTLS, Stream
from xmpp.extensions import Extension


class ComponentStream(Stream):
    """``<stream:stream xmlns='jabber:component:accept' xmlns:stream='http://etherx.jabber.org/streams' />``"""

    __tag__ = 'stream:stream'
    __etag__ = None
    __namespaces__ = [
        ('', 'jabber:component:accept'),
        ('stream', 'http://etherx.jabber.org/streams'),
    ]


class SecretHandshake(Node):
    """``<handshake>hash</handshake>``"""
    __tag__ = 'handshake'
    __etag__ = '{jabber:component:accept}handshake'
    __namespaces__ = []
    __children_of__ = ComponentStream


class SuccessHandshake(Node):
    """``<handshake />``"""
    __etag__ = 'handshake'
    __children_of__ = ComponentStream


class Component(Extension):
    """Provides an `external component
    <http://www.xmpp.org/extensions/xep-0114.html>`_ API while keeping
    minimal state based on a single boolean flag.
    """
    __xep__ = '0114'

    def initialize(self):
        self.on = Events('component', [
            'success',  # the server returned a <handshake />
            'error',  # the server returned a stream error
        ])
        self.stream.on.node(self.route_nodes)
        self.__success_handshake = None

    def route_nodes(self, event, node):
        if isinstance(node, SuccessHandshake):
            self.__success_handshake = node
            self.on.success.shout(node)

    def is_authenticated(self):
        """:returns: ``True`` if a success handshake was received by the bound
        XMLStream"""
        return self.__success_handshake is not None

    def authenticate(self, secret):
        """sends a ``<handshake>`` to the server with the encoded version of the given secret
        :param secret: the secret string to authenticate the component
        """
        stream_id = self.stream.id
        text = "".join([stream_id, secret])
        secret = hashlib.sha1(text).hexdigest()
        handshake = SecretHandshake.create(secret)
        self.stream.send(handshake)

    def create_node(self, to, tls=False):
        """creates a :py:class:`~xmpp.extensions.xep0114.ComponentStream` with
        an optional ``<starttls />`` in it.
        """

        node = ComponentStream.create(to=to)
        if tls:
            node.append(StartTLS.create())

        return node

    def open(self, domain, tls=False):
        """sends an ``<stream:stream xmlns="jabber:component:accept">``"""

        initial = self.create_node(to=domain, tls=tls)
        self.stream.send(initial)

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
from mock import ANY, patch

from tests.unit.util import EventHandlerMock
from tests.unit.util import FakeConnection

from xmpp.stream import XMLStream
from xmpp.extensions.xep0114 import SuccessHandshake


def test_is_authenticated_component():
    ('XMLStream.is_authenticated_component() should return '
     'true if there is success node in the stream')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)
    success_handler = EventHandlerMock('on_success')

    component = stream.extension['0114']
    component.on.success(success_handler)

    handshake = SuccessHandshake.create()
    component.route_nodes(None, handshake)

    component.is_authenticated().should.be.true

    success_handler.assert_called_once_with(ANY, handshake)


def test_create_component():
    ("xmpp.models.core.Stream.create_component() should return a valid node")

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    component = stream.extension['0114']

    # Regular Component
    component.create_node('capulet.com').to_xml().should.look_like(
        '<stream:stream to="capulet.com" xmlns="jabber:component:accept" xmlns:stream="http://etherx.jabber.org/streams">'
    )

    # TLS Component
    component.create_node('capulet.com', tls=True).to_xml().should.look_like(
        '<stream:stream to="capulet.com" xmlns="jabber:component:accept" xmlns:stream="http://etherx.jabber.org/streams">'
        '<starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls" />'
    )


def test_open():
    ("xmpp.models.core.Stream.create_component() should return a valid node")
    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    component = stream.extension['0114']

    # Regular Component
    component.open('capulet.com', True)

    connection.output.should.equal([
        '<stream:stream to="capulet.com" xmlns="jabber:component:accept" xmlns:stream="http://etherx.jabber.org/streams"><starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls" />'
    ])

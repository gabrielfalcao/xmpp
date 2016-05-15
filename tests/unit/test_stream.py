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
from mock import Mock, ANY, patch

from xmpp import XMLStream
from xmpp.models.core import Node
from xmpp.models.core import IQ
from xmpp.models.core import Message
from xmpp.models.core import Presence
from xmpp.models.core import ResourceBind
from xmpp.models.core import MissingJID
from xmpp.models.core import ServiceUnavailable
from util import EventHandlerMock, event_test, FakeConnection


@event_test
def test_stream_reader_open(context):
    ('XMLStream#feed should set the state to "open" if received the tag <stream> completely')

    # Given a connection
    connection = Mock(name='connection')
    # And an event handler
    event_handler = EventHandlerMock('on_open')

    # And a XMLStream
    stream = XMLStream(connection)
    stream.on.open(event_handler)

    # When I feed the reader
    stream.feed(
        ' <stream:stream from="juliet@im.example.com" to="im.example.com" version="1.0" xml:lang="en" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams"> ')

    # Then it should have returned a Node object
    stream.state.should.equal('OPEN')

    # And it dispatched the expected signal
    event_handler.assert_called_once_with(ANY, stream.stream_node)


@event_test
def test_stream_reader_closing(context):
    ('XMLStream#feed should set the state to "close" if received the closing </stream> tag')

    # Given a connection
    connection = Mock(name='connection')
    # And an event handler
    event_handler = EventHandlerMock('on_close')

    # And a XMLStream
    stream = XMLStream(connection)
    stream.on.open(event_handler)

    # When I feed the reader
    stream.feed(
        ' <stream:stream from="juliet@im.example.com" to="im.example.com" version="1.0" xml:lang="en" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams"> ')
    stream.state.should.equal('OPEN')

    stream.feed('</stream:stream>')

    # Then it should have closed the stream
    stream.state.should.equal('CLOSED')

    # And it dispatched the expected signal
    event_handler.assert_called_once_with(ANY, stream.stream_node)


@event_test
def test_stream_reader_set_invalid_State(context):
    ('XMLStream#set_state should raise an error when raising a wrong state')

    # Given a connection
    connection = Mock(name='connection')
    # And a XMLStream
    stream = XMLStream(connection)

    # When I call set_state with an invalid stage
    when_called = stream.set_state.when.called_with('wat')

    # Then it should have raised
    when_called.should.have.raised(TypeError, 'invalid state was given: wat')


def test_send_presence():
    ('XMLStream.send_presence when no `from` '
     'defined fallbacks to bound_jid')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)
    stream.handle_bound_jid(
        ResourceBind.create('juliet@capulet')
    )

    # When I call send_presence
    stream.send_presence(
        to='romeo@monteque',
    )

    # Then it should have sent the correct XML
    connection.output.should.equal([
        '<presence from="juliet@capulet" to="romeo@monteque"><priority>10</priority></presence>'
    ])


def test_send_presence_jid():
    ('XMLStream.send_presence when no `from` '
     'defined fallbacks')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # When I call send_presence
    stream.send_presence(
        **{
            'to': 'juliet@capulet',
            'from': 'romeu@monteque',
        }
    )

    # Then it should have sent the correct XML
    connection.output.should.equal([
        '<presence from="romeu@monteque" to="juliet@capulet"><priority>10</priority></presence>',
    ])


def test_send_presence_missing_jid():
    ('XMLStream.send_presence() complains '
     'if there is no bound jid and no provided `from` jid')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # When I call send_presence
    stream.send_presence.when.called_with(
        **{
            'to': 'juliet@capulet',
        }
    ).should.have.raised(
        MissingJID, 'Presence cannot be sent when missing the "from" jid'
    )


def test_send_presence_delay():
    ('XMLStream.send_presence should be able to send delay')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # When I call send_presence
    stream.send_presence(
        **{
            'to': 'juliet@capulet',
            'from': 'romeu@monteque',
            'delay': 'foobar'
        }
    )

    # Then it should have sent the correct XML
    connection.output.should.equal([
        '<presence from="romeu@monteque" to="juliet@capulet"><delay from="romeu@monteque" stamp="foobar" xmlns="urn:xmpp:delay" /><priority>10</priority></presence>'
    ])


def test_send_message():
    ('XMLStream.send_message() should send a message with body')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # When I call send_presence
    stream.send_message(
        'Hello',
        **{
            'to': 'juliet@capulet',
            'from': 'romeu@monteque',
        }
    )

    # Then it should have sent the correct XML
    connection.output.should.equal([
        '<message from="romeu@monteque" to="juliet@capulet" type="chat"><body>Hello</body></message>'
    ])


def test_is_authenticated_component():
    ('XMLStream.is_authenticated_component() should return '
     'true if there is success node in the stream')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    stream.handle_success_handshake(True)
    stream.is_authenticated_component().should.be.true


def test_handle_message():
    ('XMLStream.handle_message() should forward the `on.message` event')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # And an event handler
    handle_message = EventHandlerMock('on_message')
    stream.on.message(handle_message)

    # When I call handle message
    message = Message.create()
    stream.route_nodes(None, message)

    handle_message.assert_called_once_with(ANY, message)


def test_handle_presence():
    ('XMLStream.handle_presence() should forward the `on.presence` event')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # And an event handler
    handle_presence = EventHandlerMock('on_presence')
    stream.on.presence(handle_presence)

    # When I call handle presence
    presence = Presence.create()
    stream.handle_presence(presence)

    handle_presence.assert_called_once_with(ANY, presence)


def test_handle_iq_get():
    ('XMLStream.handle_iq() should forward the `on.iq_get` event')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # And an event handler
    handle_iq_get = EventHandlerMock('on_iq_get')
    stream.on.iq_get(handle_iq_get)

    # When I call handle iq
    node = IQ.create(type='get')
    stream.handle_iq(node)

    handle_iq_get.assert_called_once_with(ANY, node)


def test_handle_iq_set():
    ('XMLStream.handle_iq() should forward the `on.iq_set` event')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # And an event handler
    handle_iq_set = EventHandlerMock('on_iq_set')
    stream.on.iq_set(handle_iq_set)

    # When I call handle iq
    node = IQ.create(type='set')
    stream.handle_iq(node)

    handle_iq_set.assert_called_once_with(ANY, node)


def test_handle_iq_error():
    ('XMLStream.handle_iq() should forward the `on.iq_error` event')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # And an event handler
    handle_iq_error = EventHandlerMock('on_iq_error')
    stream.on.iq_error(handle_iq_error)

    # When I call handle iq
    node = IQ.create(type='error')
    stream.handle_iq(node)

    handle_iq_error.assert_called_once_with(ANY, node)


def test_handle_iq_result():
    ('XMLStream.handle_iq() should forward the `on.iq_result` event')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # And an event handler
    handle_iq_result = EventHandlerMock('on_iq_result')
    stream.on.iq_result(handle_iq_result)

    # When I call handle iq
    node = IQ.create(type='result')
    stream.handle_iq(node)

    handle_iq_result.assert_called_once_with(ANY, node)


# def test_route_nodes_undefined():
#     ('XMLStream.route_nodes() should warn about unknown nodes')

#     # Given a connection
#     connection = FakeConnection()

#     # And a XMLStream
#     stream = XMLStream(connection)

#     # And an event handler
#     handle_iq_result = EventHandlerMock('on_iq_result')
#     stream.on.iq_result(handle_iq_result)

#     # When I call handle iq
#     node = IQ.create(type='result')
#     stream.handle_iq(node)

#     handle_iq_result.assert_called_once_with(ANY, node)


def test_route_nodes_error():
    ('XMLStream.route_nodes() should warn about error nodes')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # And an event handler
    handle_error = EventHandlerMock('on_error')
    stream.on.error(handle_error)

    # When I call route_nodes
    node = ServiceUnavailable.create()
    stream.route_nodes(None, node)

    handle_error.assert_called_once_with(ANY, node)


@patch('xmpp.stream.logger')
def test_route_nodes_undefined(logger):
    ('XMLStream.route_nodes() should warn about undefined nodes')

    # Given a connection
    connection = FakeConnection()

    # And a XMLStream
    stream = XMLStream(connection)

    # When I call route_nodes with a bare Node
    empty = Node.create(type='character', name='romeo')
    stream.route_nodes(None, empty)

    # Then the logger should have been called appropriately
    logger.warning.assert_called_once_with(
        'no model defined for %s: %r', '<xmpp-unknown name="romeo" type="character" />',
        empty
    )

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
from mock import Mock, ANY

from xmpp import XMLStream
from util import EventHandlerMock, event_test


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

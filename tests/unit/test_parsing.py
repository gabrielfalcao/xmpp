# <xmpp - stateless and concurrency-agnostic XMPP library for python>
#
# Copyright (C) <2016> Gabriel Falcao <gabriel@nacaolivre.org>
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

from mock import Mock, ANY, call

from xmpp import XMLStream
from xmpp.models import (
    SASLMechanism,
    SASLMechanismSet,
    StartTLS,
    IQRegister,
    StreamFeatures,
    StreamError,
    InvalidNamespace
)

from util import XML, EventHandlerMock, nodes_from_call, event_test


@event_test
def test_stream_parse_stream_features(context):
    ('XMLStream.feed can recognize StreamFeatures')

    open_stream = XML('''
    <stream:stream
        from="my.server"
        id="c2a55811-7b4f-4429-919a-c3d91a666f83"
        version="1.0"
        xmlns="jabber:client"
        xmlns:stream="http://etherx.jabber.org/streams" xml:lang="en">
    ''')

    features = XML('''
       <stream:features>
             <mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl">
                 <mechanism>SCRAM-SHA-1</mechanism>
             </mechanisms>
             <starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls"/>
             <register xmlns="http://jabber.org/features/iq-register"/>
       </stream:features>
    ''')

    # Given a connection
    connection = Mock(name='connection')
    # And a node handler
    node_handler = EventHandlerMock('on_node')
    unhandled_handler = EventHandlerMock('on_unhandled_xml')

    # And a XMLStream
    stream = XMLStream(connection)
    stream.on.node(node_handler)
    stream.on.unhandled_xml(unhandled_handler)

    # When I feed the reader
    stream.feed(open_stream)
    stream.feed(features)

    # Then it should have triggered the calls
    node_handler.assert_has_calls([
        call(ANY, ANY),
        call(ANY, ANY),
        call(ANY, ANY),
        call(ANY, ANY),
    ])
    nodes_from_call(node_handler).should.equal([
        SASLMechanism,
        SASLMechanismSet,
        StartTLS,
        IQRegister,
        StreamFeatures
    ])
    unhandled_handler.assert_has_calls([])


# @event_test
# def test_stream_parse_stream_error(context):
#     ('XMLStream.feed can recognize StreamError')

#     open_stream = XML('''
#     <stream:stream
#         from="my.server"
#         id="c2a55811-7b4f-4429-919a-c3d91a666f83"
#         version="1.0"
#         xmlns="jabber:client"
#         xmlns:stream="http://etherx.jabber.org/streams" xml:lang="en">
#     ''')

#     errors = XML('''
#     <stream:error><invalid-namespace xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error></stream:stream>
#     ''')

#     # Given a connection
#     connection = Mock(name='connection')
#     # And a node handler
#     node_handler = EventHandlerMock('on_node')
#     closed_handler = EventHandlerMock('on_closed')
#     unhandled_handler = EventHandlerMock('on_unhandled_xml')

#     # And a XMLStream
#     stream = XMLStream(connection)
#     stream.on.node(node_handler)
#     stream.on.closed(closed_handler)
#     stream.on.unhandled_xml(unhandled_handler)

#     # When I feed the reader
#     stream.feed(open_stream)
#     stream.feed(errors)

#     # Then it should have triggered the calls

#     closed_handler.assert_has_calls([call(ANY, ANY)])

#     node_handler.assert_has_calls([
#         call(ANY, ANY),
#         call(ANY, ANY),
#     ])
#     nodes_from_call(node_handler).should.equal([
#         StreamError,
#         InvalidNamespace,
#     ])

#     unhandled_handler.assert_has_calls([])

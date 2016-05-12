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

from mock import Mock, ANY, call

from xmpp import XMLStream
from xmpp.models import (SASLMechanism, SASLMechanisms, StartTLS, IQRegister, StreamFeatures)

from util import XML, EventHandlerMock, nodes_from_call, event_test


# @event_test
# def test_stream_parse_stream(context):
#     ('XMLStream#feed should parse the stream')

#     source = XML('''
#     <stream:stream
#         from="my.server"
#         id="c2a55811-7b4f-4429-919a-c3d91a666f83"
#         version="1.0"
#         xmlns="jabber:client"
#         xmlns:stream="http://etherx.jabber.org/streams" xml:lang="en">

#        <stream:features>
#              <mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl">
#                  <mechanism>SCRAM-SHA-1</mechanism>
#              </mechanisms>
#              <starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls"/>
#              <register xmlns="http://jabber.org/features/iq-register"/>
#        </stream:features>

#     </stream:stream>
#     ''')

#     # Given a connection
#     connection = Mock(name='connection')
#     # And a node handler
#     node_handler = EventHandlerMock('on_node')

#     # And a XMLStream
#     stream = XMLStream(connection)
#     stream.on.node(node_handler)
#     # When I feed the reader
#     stream.feed(source)

#     node = stream.parse()
#     node.to_dict().should.equal({
#         'attributes': {
#             'from': 'my.server',
#             'id': 'c2a55811-7b4f-4429-919a-c3d91a666f83',
#             'lang': 'en',
#             'version': '1.0',
#             'xmlns': 'jabber:client',
#             'xmlns:stream': 'http://etherx.jabber.org/streams'
#         },
#         'namespaces': {
#             'lang': 'http://www.w3.org/XML/1998/namespace'
#         },
#         'nodes': [
#             {
#                 'nodes': [
#                     {
#                         'attributes': {'xmlns': 'urn:ietf:params:xml:ns:xmpp-sasl'},
#                         'nodes': [
#                             {
#                                 'nodes': [],
#                                 'tag': 'mechanism',
#                                 'value': 'SCRAM-SHA-1'
#                             }
#                         ],
#                         'tag': 'mechanisms'
#                     },
#                     {
#                         'attributes': {
#                             'xmlns': 'urn:ietf:params:xml:ns:xmpp-tls'
#                         },
#                         'nodes': [],
#                         'tag': 'starttls'
#                     },
#                     {
#                         'attributes': {
#                             'xmlns': 'http://jabber.org/features/iq-register'
#                         },
#                         'nodes': [],
#                         'tag': 'register'
#                     }
#                 ],
#                 'tag': 'stream:features'}
#         ],
#         'tag': 'stream:stream'
#     })
#     node.to_xml().should.look_like(source.replace('</stream:stream>', ''))

#     node_handler.assert_has_calls([
#         call(ANY, ANY),
#         call(ANY, ANY),
#         call(ANY, ANY),
#         call(ANY, ANY),
#     ])
#     nodes_from_call(node_handler).should.equal([
#         SASLMechanism,
#         SASLMechanisms,
#         StartTLS,
#         IQRegister,
#         StreamFeatures
#     ])


# @event_test
# def test_stream_two(context):
#     source = XML('<stream:stream id="" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams"><stream:error><invalid-namespace xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error></stream:stream>')

#     # Given a connection
#     connection = Mock(name='connection')
#     # And a node handler
#     node_handler = EventHandlerMock('on_node')

#     # And a XMLStream
#     stream = XMLStream(connection)
#     stream.on.node(node_handler)
#     # When I feed the reader
#     stream.feed(source)

#     item = stream.parse()
#     item.to_xml().should.look_like(source.replace('</stream:stream>', ''))

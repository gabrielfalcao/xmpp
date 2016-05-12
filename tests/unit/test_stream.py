#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import Mock, ANY, call

from xmpp import XMLStream
from xmpp.models import (SASLMechanism, SASLMechanisms, StartTLS, IQRegister, StreamFeatures)

from util import XML, EventHandlerMock, nodes_from_call, event_test


@event_test
def test_stream_parse_stream(context):
    ('XMLStream#feed should parse the stream')

    source = XML('''
    <stream:stream
        from="my.server"
        id="c2a55811-7b4f-4429-919a-c3d91a666f83"
        version="1.0"
        xmlns="jabber:client"
        xmlns:stream="http://etherx.jabber.org/streams" xml:lang="en">

       <stream:features>
             <mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl">
                 <mechanism>SCRAM-SHA-1</mechanism>
             </mechanisms>
             <starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls"/>
             <register xmlns="http://jabber.org/features/iq-register"/>
       </stream:features>

    </stream:stream>
    ''')

    # Given a connection
    connection = Mock(name='connection')
    # And a node handler
    node_handler = EventHandlerMock('on_node')

    # And a XMLStream
    stream = XMLStream(connection)
    stream.on.node(node_handler)
    # When I feed the reader
    stream.feed(source)

    node = stream.parse()
    node.to_dict().should.equal({
        'attributes': {
            'from': 'my.server',
            'id': 'c2a55811-7b4f-4429-919a-c3d91a666f83',
            'lang': 'en',
            'version': '1.0',
            'xmlns': 'jabber:client',
            'xmlns:stream': 'http://etherx.jabber.org/streams'
        },
        'namespaces': {
            'lang': 'http://www.w3.org/XML/1998/namespace'
        },
        'nodes': [
            {
                'nodes': [
                    {
                        'attributes': {'xmlns': 'urn:ietf:params:xml:ns:xmpp-sasl'},
                        'nodes': [
                            {
                                'nodes': [],
                                'tag': 'mechanism',
                                'value': 'SCRAM-SHA-1'
                            }
                        ],
                        'tag': 'mechanisms'
                    },
                    {
                        'attributes': {
                            'xmlns': 'urn:ietf:params:xml:ns:xmpp-tls'
                        },
                        'nodes': [],
                        'tag': 'starttls'
                    },
                    {
                        'attributes': {
                            'xmlns': 'http://jabber.org/features/iq-register'
                        },
                        'nodes': [],
                        'tag': 'register'
                    }
                ],
                'tag': 'stream:features'}
        ],
        'tag': 'stream:stream'
    })
    node.to_xml().should.look_like(source.replace('</stream:stream>', ''))

    node_handler.assert_has_calls([
        call(ANY, ANY),
        call(ANY, ANY),
        call(ANY, ANY),
        call(ANY, ANY),
    ])
    nodes_from_call(node_handler).should.equal([
        SASLMechanism,
        SASLMechanisms,
        StartTLS,
        IQRegister,
        StreamFeatures
    ])


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


@event_test
def test_stream_two(context):
    source = XML('<stream:stream id="" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams"><stream:error><invalid-namespace xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error></stream:stream>')

    # Given a connection
    connection = Mock(name='connection')
    # And a node handler
    node_handler = EventHandlerMock('on_node')

    # And a XMLStream
    stream = XMLStream(connection)
    stream.on.node(node_handler)
    # When I feed the reader
    stream.feed(source)

    item = stream.parse()
    item.to_xml().should.look_like(source.replace('</stream:stream>', ''))

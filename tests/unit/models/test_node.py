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


from xmpp.models import Node
from xmpp.models import IQ
from xmpp.models import ResourceBind
from xmpp.models import Stream


from tests.unit.util import XML


def test_parse_stream():
    ('Node#from_xml("<stream:stream>") should return valid Stream Node')

    # Given a valid XML
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

    # When I parse the string
    item = Node.from_xml(source)

    # Then it should have returned a Stream object
    item.should.be.a(Stream)

    # And the node should be able to reconstruct in the exact same XML
    item.to_xml().should.look_like(source.replace('</stream:stream>', ''))

    # And it should recognize TLS support
    item.supports_tls().should.be.true

    # And it should recognize IQ register support
    item.accepts_registration().should.be.true

    # And it should recognize SASL support
    item.sasl_support().should.equal([
        'SCRAM-SHA-1',
    ])


def test_create_client_stream():
    ('Stream.create_client() should return valid open Stream')

    # Given a client opening a stream
    initial = Stream.create_client(
        to='domain.im'
    )

    # When I check its xml output
    result = initial.to_xml()

    # Then it should be an open tag
    result.should.equal(
        '<stream:stream to="domain.im" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams">')


def test_parse_iq():
    ('Node.from_xml("<iq />") should return a valid IQ node')

    # Given a valid XML
    source = XML('''
        <iq id="536f8b3c-54e6-408b-ac00-ffb63ffd0177" type="result">
          <bind xmlns="urn:ietf:params:xml:ns:xmpp-bind">
            <jid>presence1@falcao.it/xmpp-test</jid>
          </bind>
        </iq>
    ''')

    # When I parse the string
    item = Node.from_xml(source)

    # Then it should have returned an IQ object
    item.should.be.an(IQ)


def test_equality():
    ('Node objects should be comparable')

    IQ.create(foo='bar').should.equal(IQ.create(foo='bar'))
    (IQ.create(foo='bar') == 'not a node').should.be.false


def test_close():
    ('Node objects should be comparable')

    node = IQ.create(foo='bar')
    node.is_closed.should.be.false
    node.close().should.be.false
    node.is_closed.should.be.true


def test_attr():
    ('Node objects should be comparable')

    node = ResourceBind.with_resource('wat')
    dict(node.attr).should.equal({
        'xmlns': 'urn:ietf:params:xml:ns:xmpp-bind'
    })
    node.set_attribute('foo', 'bar')
    node.to_dict().should.equal({
        'attributes': {
            'foo': 'bar',
            'xmlns': 'urn:ietf:params:xml:ns:xmpp-bind'
        },
        'nodes': [
            {
                'nodes': [],
                'tag': 'resource',
                'value': 'wat'
            }
        ],
        'tag': 'bind'
    })
    str(node).should.look_like(
        '<bind foo="bar" xmlns="urn:ietf:params:xml:ns:xmpp-bind"><resource>wat</resource></bind>')


def test_append():
    ('You should not be able to append to a node that is closed')
    node = IQ.create(foo='bar')
    node.close()
    node.append.when.called_with(IQ.create()).should.have.raised(
        TypeError,
        'Refused to append a child to the closed node: <iq foo="bar" />',
    )

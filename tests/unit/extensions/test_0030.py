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
from mock import ANY

from tests.unit.util import FakeXMLStream
from tests.unit.util import EventHandlerMock

from xmpp.extensions.xep0030 import ServiceDiscovery
from xmpp.extensions.xep0030 import Identity
from xmpp.extensions.xep0030 import Item
from xmpp.extensions.xep0030 import Feature
from xmpp.extensions.xep0030 import QueryInfo
from xmpp.extensions.xep0030 import QueryItems


def test_disco_query_info():
    ('xep0030.ServiceDiscovery.query_info() should send')

    # Given a stream
    stream = FakeXMLStream('test@foo.com/bar')

    # And an instance of disco
    disco = ServiceDiscovery(stream)

    # When I call query_info
    disco.query_info(
        to='foo.com'
    )

    # Then the node should be there
    stream.output.should.have.length_of(1)
    stream.output[0].to_xml().should.equal(
        '<iq to="foo.com" type="get"><query to="foo.com" xmlns="http://jabber.org/protocol/disco#info" /></iq>'
    )


def test_disco_query_items():
    ('xep0030.ServiceDiscovery.query_items() should send')

    # Given a stream
    stream = FakeXMLStream('test@foo.com/bar')

    # And an instance of disco
    disco = ServiceDiscovery(stream)

    # When I call query_items
    disco.query_items(
        to='foo.com'
    )

    # Then the node should be there
    stream.output.should.have.length_of(1)
    stream.output[0].to_xml().should.equal(
        '<iq to="foo.com" type="get"><query to="foo.com" xmlns="http://jabber.org/protocol/disco#items" /></iq>'
    )


def test_identity_representation():
    ('xep0030.Identity should be representable as string')

    node = Identity.create(category='one', type='two', name='three')
    repr(node).should.equal('one:two:three')


def test_item_jid_representation():
    ('xep0030.Item should be representable as string')

    node = Item.create(jid='component.foo.com')
    repr(node).should.equal('component:jid:component.foo.com')


def test_item_representation():
    ('xep0030.Item should be representable as string')

    node = Item.create(foo='bar')
    repr(node).should.equal("item:[('foo', 'bar'), ('xmlns', 'http://jabber.org/protocol/disco#items')]")


def test_feature_representation():
    ('xep0030.Feature should be representable as string')

    node = Feature.create(var='bar')
    repr(node).should.equal("feature:bar")


def test_disco_events():
    ('xep0030.ServiceDiscovery should forward events of its known nodes')

    # Given a stream
    stream = FakeXMLStream('test@foo.com/bar')

    # And an event handler
    handle_query_items = EventHandlerMock('query_items')
    handle_query_info = EventHandlerMock('query_info')

    # And an instance of disco
    disco = ServiceDiscovery(stream)

    # When I hookup the handler
    disco.on.query_items(handle_query_items)
    disco.on.query_info(handle_query_info)

    # When I publish a QueryInfo
    query_info = QueryInfo.create(query='info')
    stream.on.node.shout(query_info)

    # And I publish a QueryItems
    query_items = QueryItems.create(query='items')
    stream.on.node.shout(query_items)

    # Then the handler should have been called appropriately
    handle_query_items.assert_called_once_with(ANY, query_items)
    handle_query_info.assert_called_once_with(ANY, query_info)

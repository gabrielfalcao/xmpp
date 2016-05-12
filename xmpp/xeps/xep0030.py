# -*- coding: utf-8 -*-
from speakers import Speaker as Events
from xmpp.models import Node, IQ
from xmpp.xeps import Extension


class QueryInfo(Node):
    __tag__ = 'query'
    __etag__ = '{http://jabber.org/protocol/disco#info}query'
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/disco#info')
    ]
    __children_of__ = IQ


class QueryItems(Node):
    __tag__ = 'query'
    __etag__ = '{http://jabber.org/protocol/disco#items}query'
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/disco#items')
    ]
    __children_of__ = IQ


class Item(Node):
    __tag__ = 'item'
    __etag__ = '{http://jabber.org/protocol/disco#items}item'
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/disco#items'),
    ]
    __single__ = True
    __children_of__ = QueryItems

    def __repr__(self):
        if 'jid' in self.attr:
            return 'component:{jid}'.format(**self.attr)

        return 'item:{0}'.format(self.to_xml())


class Identity(Node):
    __tag__ = 'identity'
    __etag__ = '{http://jabber.org/protocol/disco#info}identity'
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/disco#info'),
    ]
    __children_of__ = QueryInfo

    def __repr__(self):
        return ':'.join(filter(bool, [
            self.attr.get('category'),
            self.attr.get('type'),
            self.attr.get('name'),
        ]))
        return


class Feature(Node):
    __tag__ = 'feature'
    __etag__ = '{http://jabber.org/protocol/disco#info}feature'
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/disco#info'),
    ]
    __children_of__ = QueryInfo

    def __repr__(self):
        return ":".join([
            "item",
            self.attr.get('var', self.value),
        ])


class ServiceDiscovery(Extension):
    """extension for discovering information about other XMPP
    entities. Two kinds of information can be discovered: (1) the identity
    and capabilities of an entity, including the protocols and features it
    supports; and (2) the items associated with an entity, such as the
    list of rooms hosted at a multi-user chat service."""

    __xep__ = '0030'

    def initialize(self):
        self.on = Events('disco', [
            'query_items',
            'query_info',
            'item',
            'identity',
            'feature',
        ])
        self.stream.on.node(self.route_nodes)

    def route_nodes(self, event, node):
        ROUTES = {
            QueryInfo: self.on.query_info,
            QueryItems: self.on.query_items,
            Item: self.on.item,
            Identity: self.on.identity,
            Feature: self.on.feature,
        }
        NodeClass = type(node)
        event = ROUTES.get(NodeClass)

        if event:
            event.shout(node)

    def query_items(self, to=None, node=None):
        to = to or self.stream.bound_jid.domain
        iq = IQ.create(type='get', to=to)
        params = {}
        if node:
            params['node'] = node

        query = QueryItems.create(**params)
        iq.append(query)
        self.stream.send(iq)

    def query_info(self, to=None, node=None):
        to = to or self.stream.bound_jid.domain
        iq = IQ.create(type='get', to=to)
        params = {}
        if node:
            params['node'] = node

        query = QueryInfo.create(**params)
        iq.append(query)
        self.stream.send(iq)

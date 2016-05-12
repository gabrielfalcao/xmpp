#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from collections import OrderedDict
from xmpp.core import ET
from xmpp.models.node import Node


class JID(object):
    regex = re.compile(r'^(?P<full>(?P<bare>(?P<nick>[^@]+)@?(?P<domain>[^/]+))(/(?P<resource>\S+))?)$')

    def __init__(self, data, generate_resource=False):
        if isinstance(data, basestring):
            found = self.regex.search(data)
            if not found:
                raise TypeError('invalid JID: {0}'.format(data))

            self.parts = found.groupdict()

        elif isinstance(data, dict):
            self.parts = data
        elif isinstance(data, JID):
            self.parts = data.parts

        if generate_resource and not self.parts.get('resource'):
            self.parts['resource'] = generate_resource()

    @property
    def full(self):
        return self.parts.get('full')

    @property
    def bare(self):
        return self.parts.get('bare')

    @property
    def nick(self):
        return self.parts.get('nick')

    @property
    def domain(self):
        return self.parts.get('domain')

    @property
    def resource(self):
        return self.parts.get('resource')

    @property
    def muc(self):
        return {
            'nick': self.resource,
            'room': self.nick,
            'server': self.domain,
        }

    @property
    def text(self):
        return '{nick}@{domain}/{resource}'.format(**self.parts)

    def __str__(self):
        return self.text

    def __repr__(self):
        return 'JID({0})'.format(self.parts)


class Stream(Node):
    __tag__ = 'stream:stream'
    __etag__ = '{http://etherx.jabber.org/streams}stream'

    __namespaces__ = [
        ('', 'jabber:client'),
        ('stream', 'http://etherx.jabber.org/streams'),
    ]

    def initialize(self):
        self._features = {}

    @classmethod
    def create(cls, **kw):
        params = OrderedDict()
        if not cls.__etag__:
            tag = cls.__tag__
            for suffix, ns in cls.__namespaces__:
                attr = ":".join(filter(bool, ['xmlns', suffix]))
                params[attr] = ns
        else:
            tag = cls.__etag__

        params.update(kw)

        element = ET.Element(tag, **params)
        return Node.from_element(element, allow_fixedup=True)

    def to_xml(self, close=False):
        xml = super(Stream, self).to_xml()
        if close:
            return xml

        END = '</stream:stream>'
        if END in xml:
            xml = xml.replace(END, '')
        else:
            xml = re.sub(r'\s*[/][>]\s*$', '>', xml)

        return xml

    @staticmethod
    def create_client(to, tls=False):
        node = ClientStream.create(to=to, version='1.0')
        if tls:
            node.append(StartTLS.create())

        return node

    @staticmethod
    def create_component(to):
        return ComponentStream.create(to=to)

    def get_features(self):
        children = self.get_children()
        if not children:
            return {}

        features_node = children[0]
        data = {}
        for feature in features_node.get_children():
            name = feature.attr['xmlns']
            value = filter(bool, [x.value for x in feature.get_children()])
            data[name] = value

        return data

    @property
    def features(self):
        if not self._features:
            self._features.update(self.get_features())

        return self._features

    def supports_tls(self):
        return 'urn:ietf:params:xml:ns:xmpp-tls' in self.features

    def accepts_registration(self):
        return 'http://jabber.org/features/iq-register' in self.features

    def sasl_support(self):
        return self.features.get('urn:ietf:params:xml:ns:xmpp-sasl', [])


class ComponentStream(Stream):
    __tag__ = 'stream:stream'
    __etag__ = None
    __namespaces__ = [
        ('', 'jabber:component:accept'),
        ('stream', 'http://etherx.jabber.org/streams'),
    ]


class SecretHandshake(Node):
    __tag__ = 'handshake'
    __etag__ = '{jabber:component:accept}handshake'
    __namespaces__ = []
    __children_of__ = ComponentStream


class SuccessHandshake(Node):
    __etag__ = 'handshake'
    __children_of__ = ComponentStream


class ClientStream(Stream):
    __tag__ = 'stream:stream'
    __etag__ = None
    __namespaces__ = [
        ('', 'jabber:client'),
        ('stream', 'http://etherx.jabber.org/streams'),
    ]


class StreamFeatures(Node):
    __tag__ = 'stream:features'
    __etag__ = '{http://etherx.jabber.org/streams}features'
    __children_of__ = Stream
    __namespaces__ = []


class Feature(Node):
    def get_name(self):
        return self.tag


class SASLMechanisms(Feature):
    __tag__ = 'mechanisms'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}mechanisms'
    __children_of__ = StreamFeatures

    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-sasl'),
    ]

    def supported_mechanisms(self):
        return [c.value.strip() for c in self.get_children()]


class SASLMechanism(Node):
    __tag__ = 'mechanism'
    __single__ = True
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}mechanism'
    __children_of__ = SASLMechanisms
    __namespaces__ = []


class IQRegister(Feature):
    __tag__ = 'register'
    __single__ = True
    __etag__ = '{http://jabber.org/features/iq-register}register'
    __children_of__ = StreamFeatures

    __namespaces__ = [
        ('', "http://jabber.org/features/iq-register"),
    ]


class StartTLS(Node):
    __tag__ = 'starttls'
    __single__ = True
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-tls}starttls'
    __children_of__ = StreamFeatures
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-tls'),
    ]


class ProceedTLS(Node):
    __tag__ = 'proceed'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-tls}proceed'
    __single__ = True
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-tls'),
    ]


class Message(Node):
    __etag__ = 'message'
    __children_of__ = Stream

    @property
    def states(self):
        return [c.tag for c in self.get_children()]

    def is_composing(self):
        return 'composing' in self.states

    def is_active(self):
        return 'active' in self.states

    def get_body(self):
        data = []

        for item in self.query('body'):
            data.append(item.value)

        return u''.join(map(unicode, data))

    def add_body_text(self, text):
        body = self.get('body')
        if not body:
            body = MessageBody.create()
            self.append(body)

        body.add_text(text)


class Presence(Node):
    __etag__ = 'presence'
    __children_of__ = Stream

    @property
    def delay(self):
        delay = self.get('delay')
        if delay:
            return delay.attr.get('stamp')

    @property
    def show(self):
        node = self.get('show')
        if node:
            return node.value

        return ''

    @property
    def status(self):
        node = self.get('status')
        if node:
            return node.value

        return ''


class IQ(Node):
    __etag__ = 'iq'
    __children_of__ = Stream

    @staticmethod
    def with_child_and_attributes(child, **params):
        node = IQ.create(**params)
        node.append(child)
        return node


class IQBind(Node):
    __tag__ = 'bind'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-bind}bind'
    __namespaces__ = [
    ]
    __children_of__ = IQ


class ResourceBind(Node):
    __tag__ = 'bind'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-bind}bind'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-bind'),
    ]
    __children_of__ = StreamFeatures

    @staticmethod
    def with_resource(resource):
        node = ResourceBind.create()
        if resource:
            echild = ET.Element('resource', {})
            echild.text = resource.strip()
            node._element.append(echild)

        return node


class BoundJid(Node):
    __tag__ = 'jid'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-bind}jid'
    __namespaces__ = []
    __children_of__ = ResourceBind


class BindRequired(Node):
    __tag__ = 'required'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-bind}required'
    __single__ = True
    __namespaces__ = []
    __children_of__ = ResourceBind


class BindOptional(Node):
    __tag__ = 'optional'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-bind}optional'
    __single__ = True
    __namespaces__ = []
    __children_of__ = ResourceBind


class Session(Node):
    __tag__ = 'session'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-session}session'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-session'),
    ]
    __children_of__ = StreamFeatures


class SessionRequired(Node):
    __tag__ = 'required'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-session}required'
    __single__ = True
    __namespaces__ = []
    __children_of__ = Session


class SessionOptional(Node):
    __tag__ = 'optional'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-session}optional'
    __single__ = True
    __namespaces__ = []
    __children_of__ = Session


class RosterVersioning(Node):
    __tag__ = 'ver'
    __etag__ = '{urn:xmpp:features:rosterver}ver'
    __single__ = True
    __namespaces__ = [
        ('', 'urn:xmpp:features:rosterver'),

    ]
    __children_of__ = StreamFeatures


class SASLAuth(Node):
    __tag__ = 'auth'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}auth'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-sasl'),
    ]

    @staticmethod
    def prepare(mechanism, message):
        node = SASLAuth.create(mechanism=mechanism)
        node.value = message
        return node


class SASLFailure(Node):
    __tag__ = 'failure'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}failure'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-sasl'),
    ]


class SASLText(Node):
    __tag__ = 'text'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}text'
    __namespaces__ = [
    ]


class SASLMalformedRequest(Node):
    __tag__ = 'malformed-request'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}malformed-request'
    __namespaces__ = [
    ]


class SASLChallenge(Node):
    __tag__ = 'challenge'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}challenge'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-sasl'),
    ]

    def get_data(self):
        return self.value.decode('base64')


class SASLSuccess(Node):
    __tag__ = 'success'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}success'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-sasl'),
        ('stream', 'http://etherx.jabber.org/streams'),
    ]

    def get_data(self):
        return self.value.decode('base64')


class SASLResponse(Node):
    __tag__ = 'response'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-sasl}response'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-sasl'),
    ]

    @staticmethod
    def prepare(mechanism, message):
        node = SASLResponse.create(mechanism=mechanism)
        node.value = message
        return node


class EntityCapability(Node):
    __tag__ = 'c'
    __etag__ = '{http://jabber.org/protocol/caps}c'
    __single__ = True
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/caps'),
    ]


class VCardUpdate(Node):
    __tag__ = 'x'
    __etag__ = '{vcard-temp:x:update}x'
    __namespaces__ = [
        ('', 'vcard-temp:x:update')
    ]


class ChatStateComposing(Node):
    __tag__ = 'composing'
    __etag__ = '{http://jabber.org/protocol/chatstates}composing'
    __single__ = True
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/chatstates')
    ]


class ChatStateActive(Node):
    __tag__ = 'active'
    __etag__ = '{http://jabber.org/protocol/chatstates}active'
    __single__ = True
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/chatstates')
    ]


class ChatStatePaused(Node):
    __tag__ = 'paused'
    __etag__ = '{http://jabber.org/protocol/chatstates}paused'
    __single__ = True
    __namespaces__ = [
        ('', 'http://jabber.org/protocol/chatstates')
    ]


class MessageBody(Node):
    __etag__ = 'body'
    __children_of__ = Message


class Delay(Node):
    __tag__ = 'delay'
    __etag__ = '{urn:xmpp:delay}delay'
    __single__ = True
    __namespaces__ = [
        ('', 'urn:xmpp:delay')
    ]


class PresencePriority(Node):
    __etag__ = 'priority'
    __children_of__ = Presence


class MessageDelay(Node):
    __tag__ = 'delay'
    __etag__ = '{jabber:x:delay}delay'
    __single__ = True
    __namespaces__ = [
        ('', 'jabber:x:delay')
    ]
    __children_of__ = Message


class VCardPhoto(Node):
    __tag__ = 'photo'
    __etag__ = '{vcard-temp:x:update}photo'
    __single__ = True
    __namespaces__ = [
        ('', 'vcard-temp:x:update')
    ]


class Error(Node):
    __etag__ = 'error'


class Text(Node):
    __tag__ = 'text'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-stanzas}text'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-stanzas')
    ]


class StreamError(Error):
    __tag__ = 'stream:error'
    __tag__ = 'error'
    __children_of__ = Stream


# stream errors
class BadFormat(Error):
    __tag__ = 'bad-format'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-streams}bad-format'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-streams')
    ]
    __children_of__ = StreamError


class BadNamespace(Error):
    __tag__ = 'bad-namespace'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-streams}bad-namespace'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-streams')
    ]
    __children_of__ = StreamError


class Conflict(Error):
    __tag__ = 'conflict'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-streams}conflict'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-streams')
    ]
    __children_of__ = StreamError


class ConnectionTimeout(Error):
    __tag__ = 'connection-timeout'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-streams}connection-timeout'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-streams')
    ]
    __children_of__ = StreamError


class HostGone(Error):
    __tag__ = 'host-gone'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-streams}host-gone'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-streams')
    ]
    __children_of__ = StreamError


class NotAuthorized(Error):
    __tag__ = 'not-authorized'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-streams}not-authorized'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-streams')
    ]
    __children_of__ = StreamError


class UnsupportedStanzaType(Error):
    __tag__ = 'unsupported-stanza-type'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-streams}unsupported-stanza-type'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-streams')
    ]
    __children_of__ = StreamError


# stanza errors

class ServiceUnavailable(Error):
    __tag__ = 'service-unavailable'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-stanzas}service-unavailable'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-stanzas')
    ]


class BadRequest(Error):
    __tag__ = 'bad-request'
    __etag__ = '{urn:ietf:params:xml:ns:xmpp-stanzas}bad-request'
    __namespaces__ = [
        ('', 'urn:ietf:params:xml:ns:xmpp-stanzas')
    ]


class VCard(Node):
    __tag__ = 'vCard'
    __etag__ = '{vcard-temp}vCard'
    __namespaces__ = [
        ('', 'vcard-temp')
    ]
    __children_of__ = IQ


class PresenceStatus(Node):
    __etag__ = 'status'
    __children_of__ = Presence


class PresenceShow(Node):
    __etag__ = 'show'
    __children_of__ = Presence


class RosterQuery(Node):
    __tag__ = 'query'
    __etag__ = '{jabber:iq:roster}query'
    __namespaces__ = [
        ('', 'jabber:iq:roster')
    ]
    __children_of__ = IQ


class RosterItem(Node):
    __etag__ = 'item'
    __children_of__ = RosterQuery


class RosterGroup(Node):
    __tag__ = 'group'
    __etag__ = 'query'
    __namespaces__ = [
        ('', 'jabber:iq:roster')
    ]
    __children_of__ = RosterItem

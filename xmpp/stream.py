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

import re
import uuid
import logging
import hashlib
from xmpp.core import ET

from speakers import Speaker as Events
from xmpp.core import generate_id
from xmpp.extensions import get_known_extensions
from xmpp.models import (
    Node,
    PresencePriority,
    Stream,
    StreamError,
    ProceedTLS,
    SASLAuth,
    SASLChallenge,
    SASLResponse,
    SASLSuccess,
    SASLFailure,
    Message,
    Presence,
    IQ,
    ResourceBind,
    SASLMechanismSet,
    BoundJid,
    JID,
    StartTLS,
    IQRegister,
    PresenceDelay,
    SecretHandshake,
    SuccessHandshake,
    RosterQuery,
    RosterItem,
    RosterGroup,
)

logger = logging.getLogger('xmpp.stream')


class STREAM_STATES(object):
    IDLE = 'IDLE'
    AUTHENTICATED = 'AUTHENTICATED'
    READY = 'READY'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    @classmethod
    def keys(cls):
        return filter(lambda k: k.upper() == k, dir(cls))

    @classmethod
    def is_valid(cls, state):
        return state in cls.keys()


xml_cleanup_regex1 = re.compile(r'^[<][?]xml[^?]+[^>]+[>]')


def is_beginning_of_stream(string):
    return string.lstrip().startswith('<stream:stream')


def sanitize_feed(data):
    data = xml_cleanup_regex1.sub('', data)
    return data.lstrip()


def create_spool(data):
    treated = data.replace('><', '>\n<')
    return treated.splitlines()


class NodeHandler(object):
    def __init__(self, parent):
        self.nodes = []
        self._data = []
        self.parent = parent

    def start(self, tag, attrib):
        parent_node = self.nodes and self.nodes[-1] or None
        has_parent = parent_node and not parent_node.is_closed
        element = ET.Element(tag, attrib)
        node = self.notify_and_store_node(element)

        if has_parent:
            parent_node.append(node)

        self.parent.node_did_open(node)

    def end(self, tag):
        current = self.nodes.pop()
        ancestry = []
        while self.nodes and not tag == current.__etag__:
            ancestry.append(current)
            current = self.nodes.pop()

        if ancestry:
            self.nodes.extend(ancestry)

        elif not self.nodes:
            self.nodes.append(current)
            return

        possible_parent = self.nodes[-1]
        if possible_parent.is_parent_of(current):
            self.parent.node_did_close(current)

    def close(self):
        if not self.nodes:
            return

        for node in reversed(self.nodes):
            if node.is_closed:
                return node._element

        return node._element

    def data(self, data):
        target = self.nodes[-1]._element
        if not target.text:
            target.text = data
        elif len(target.text) < self.parent.max_text_length:
            target.text += "\n"
            target.text += data
        else:
            target.text = '[TRUNCATED]'

        return False

    def notify_and_store_node(self, element):
        node = Node.from_element(element)
        self.nodes.append(node)
        return node


def create_stream_events():
    return Events('stream', [
        'feed',                 # the XMLStream has just been fed with xml
        'open',                 # the XMLStream is open
        'closed',               # the XMLStream has been closed
        'error',                # received a <stream:error></stream:error> from the server
        'unhandled_xml',        # the XMLStream failed to feed the incremental XML parser with the given value
        'node',                 # a new xmpp.Node was just parsed by the stream and is available to use
        'iq',                   # a new xmpp.IQ was node was received
        'message',              # a new xmpp.Message node was received
        'presence',             # a new xmpp.Presence node was received
        'start_stream',         # a new stream is being negotiated
        'start_tls',            # server sent <starttls />
        'tls_proceed',          # the peer allowed the TCP connection to upgrade to TLS
        'sasl_challenge',       # the peer sent a SASL challenge
        'sasl_success',         # the peer sent a SASL success
        'sasl_failure',         # the peer sent a SASL failure
        'sasl_response',        # the peer sent a SASL response
        'sasl_support',         # the peer says it supports SASL
        'bind_support',         # the peer says it supports binding resource
        'iq_result',            # the peer returned a <iq type="result"></iq>
        'iq_set',               # the peer returned a <iq type="set"></iq>
        'iq_get',               # the peer returned a <iq type="get"></iq>
        'iq_error',             # the peer returned a <iq type="error"></iq>
        'user_registration',    # the peer supports user registration
        'bound_jid',            # the peer returned a <jid>username@domain/resource</jid> that should be used in the from= of stanzas
        'success_handshake',      # the server authorized the component to reopen the stream and start sending stanzas
    ])


class XMLStream(object):
    def __init__(self, connection, max_text_length=1024 * 64, debug=False):
        self._state = STREAM_STATES.IDLE
        self._connection = connection
        self._tls_connection = None
        self._connection.on.ready_to_write(self.ready_to_write)
        self._connection.on.ready_to_read(self.ready_to_read)
        self.max_text_length = max_text_length
        self.extension = {}
        self.on = create_stream_events()
        self.on.node(self.route_nodes)
        # if debug:
        #     self.on.open(lambda event, data: logger.debug("STREAM OPEN: %s", data))
        #     self.on.closed(lambda event, data: logger.debug("STREAM CLOSED: %s", data))
        #     self.on.node(lambda event, node: logger.debug("STREAM NODE: %s", node.to_xml()))
        # if not debug:
        #     self.on.unhandled_xml(lambda event, xml: logger.critical("unhandled xml: %s", xml))
        self.on.unhandled_xml(lambda event, xml: logger.warning("unhandled xml: %s", xml))
        self.recycle()

    @property
    def bound_jid(self):
        return self.__bound_jid

    def recycle(self):
        self._buffer = []
        # minimal state:
        self.__success_handshake = None
        self.__sasl_result = None
        self.__bound_jid = None

        self.resource_name = 'xmpp-{0}'.format(uuid.uuid4())
        self.nodes = []
        self.stream_node = None
        self.parser = self.make_parser()
        self.load_extensions()

    def load_extensions(self):
        self.extension = {}
        for number, Extension in get_known_extensions():
            self.extension[number] = Extension(self)

    def has_gone_through_sasl(self):
        return self.__sasl_result is not None

    def finish_tls_upgrade(self, connection):
        if self._connection != connection:
            logger.critical("finish_tls_upgrade: weird!!")

        self._tls_connection = connection

    def is_under_tls(self):
        return self._tls_connection is not None

    def finish_sasl(self, result):
        self.__sasl_result = result
        self.set_state(STREAM_STATES.AUTHENTICATED)

    def handle_sasl_success(self, node):
        self.on.sasl_success.shout(node)

    def handle_sasl_failure(self, node):
        self.__sasl_result = None
        self.on.sasl_failure.shout(node)

    def handle_bound_jid(self, node):
        jid = JID(node.value.strip())
        self.__bound_jid = jid
        self.on.bound_jid.shout(jid)

    def handle_success_handshake(self, node):
        self.__success_handshake = node
        self.on.success_handshake.shout(node)

    def handle_message(self, node):
        self.on.message.shout(node)

    def handle_presence(self, node):
        self.on.presence.shout(node)

    def handle_iq(self, node):
        iq_type = node.attr.get('type')
        ROUTES = {
            'get': self.on.iq_get,
            'set': self.on.iq_set,
            'error': self.on.iq_error,
            'result': self.on.iq_result,
        }
        event = ROUTES.get(iq_type)
        if event:
            event.shout(node)
        else:
            logger.warning("received an IQ with invalid 'type': %s", node.to_xml())

    def route_nodes(self, event, node):
        ROUTES = {
            # direct shout throught the event handlers
            ProceedTLS: self.on.tls_proceed,
            SASLChallenge: self.on.sasl_challenge,
            SASLResponse: self.on.sasl_response,
            StartTLS: self.on.start_tls,
            ResourceBind: self.on.bind_support,
            SASLMechanismSet: self.on.sasl_support,
            IQRegister: self.on.user_registration,
            StreamError: self.on.error,
            # internal affairs when handling node before shouting it
            # through event handlers
            IQ: self.handle_iq,
            Message: self.handle_message,
            Presence: self.handle_presence,
            BoundJid: self.handle_bound_jid,
            SASLFailure: self.handle_sasl_failure,
            SASLSuccess: self.handle_sasl_success,
            SuccessHandshake: self.handle_success_handshake,
        }
        NodeClass = type(node)
        event = ROUTES.get(NodeClass)
        if type(node) == Node:
            logger.critical("no model defined for %s: %r", node.to_xml(), node)

        if event:
            if hasattr(event, 'shout'):
                event.shout(node)
            else:
                event(node)

        elif NodeClass.__children_of__ == StreamError:
            self.on.error.shout(node)

    @property
    def id(self):
        """returns the stream id provided by the server.

        Mainly used by the send_component_handshake() when crafting
        the secret.
        """
        if self.stream_node is None:
            return

        return self.stream_node.attr.get('id')

    def parse(self):
        try:
            if self._buffer and self._buffer[-1].endswith('>'):
                element = self.parser.close()
                self.parser = self.make_parser()
            else:
                element = None

        except ET.ParseError:
            return

        if element is None and len(self.nodes) > 0:
            return self.nodes[-1]
        elif element is None:
            return

        return Node.from_element(element, allow_fixedup=True)

    def ready_to_read(self, event, connection):
        self.feed(connection.receive())

        node = self.parse()
        if node:
            self.on.node.shout(node)

    def ready_to_write(self, event, connection):
        self.set_state(STREAM_STATES.READY)
        return

    def append_node(self, node):
        self.nodes.append(node)

    def node_did_open(self, node):
        if isinstance(node, Stream):
            self.set_state(STREAM_STATES.OPEN)
            self.stream_node = node
            self.on.open.shout(node)

        self.append_node(node)

    def send(self, node):
        self._connection.send(node.to_xml())

    def close(self, disconnect=True):
        self._connection.send(b'</stream:stream>')
        self._state = STREAM_STATES.IDLE

        if disconnect:
            self._connection.disconnect()

        self.recycle()
        self._connection = None

    def open_client(self, domain):
        initial = Stream.create_client(
            to=domain,
        )
        self.send(initial)

    def open_component(self, domain):
        initial = Stream.create_component(
            to=domain,
        )
        self.send(initial)

    def node_did_close(self, node):
        if node.__tag__ == 'stream:stream':
            self.set_state(STREAM_STATES.CLOSED)
        else:
            self.on.node.shout(node)

    @property
    def state(self):
        return self._state

    def set_state(self, state):
        if not STREAM_STATES.is_valid(state):
            msg = 'invalid state was given: {0}'.format(state)
            raise TypeError(msg)

        self._state = state

    def make_parser(self):
        self.target = NodeHandler(self)
        return ET.XMLTreeBuilder(target=self.target)

    def matches_closed_stream(self, string):
        return string.rstrip().endswith('</stream:stream>')

    def feed(self, data, attempt=1):
        self.on.feed.shout(data)
        data = sanitize_feed(data)
        spool = create_spool(data)

        if not self.matches_closed_stream(data):
            if len(spool) > 1:
                for item in spool:
                    self.feed_from_spool(item)
            else:
                self.feed_from_spool(data)

        else:
            self.set_state(STREAM_STATES.CLOSED)
            if self.stream_node:
                self.on.closed.shout(self.stream_node)

    def feed_from_spool(self, item, attempt=0):
        try:
            self.parser.feed(item)
            self._buffer.append(item)
        except ET.ParseError:
            if attempt > 1:
                self.on.unhandled_xml.shout(item)
                return

            self.parser = self.make_parser()
            return self.feed_from_spool(item, attempt + 1)

    def start_tls_handshake(self, domain):
        self.send(StartTLS.create())

    def send_sasl_auth(self, mechanism, message):
        node = SASLAuth.prepare(mechanism, message)
        self.send(node)
        return node

    def send_sasl_response(self, mechanism, message):
        node = SASLResponse.prepare(mechanism, message)
        self.send(node)
        return node

    def bind_to_resource(self, name):
        iq = IQ.create(type='set', id=generate_id())
        iq.append(ResourceBind.with_resource(name))
        self.send(iq)

    def send_presence(self, to=None, delay=None, priority=10, **params):
        if self.bound_jid and 'from' not in params:
            params['from'] = self.bound_jid.full

        if to:
            params['to'] = to

        from_jid = params.get('from')
        presence = Presence.create(**params)

        if delay:
            delay_params = {
                'stamp': delay.isoformat(),
            }
            if from_jid:
                delay_params['from_jid'] = from_jid

            presence.append(PresenceDelay.create(**delay_params))

        if priority:
            node = PresencePriority.create(bytes(priority))
            presence.append(node)

        self.send(presence)

    def send_message(self, message, **params):
        self.send(Message.create(message, **params))

    def is_authenticated_component(self):
        return self.__success_handshake is not None

    def send_secret_handshake(self, secret):
        secret = hashlib.sha1("".join([self.id, secret])).hexdigest()
        handshake = SecretHandshake.create(secret)
        self.send(handshake)

    def add_contact(self, contact_jid, from_jid=None, groups=None):
        from_jid = JID(from_jid or self.bound_jid)
        contact_jid = JID(contact_jid)

        new_contact = RosterQuery.create()
        item = RosterItem.create(
            jid=contact_jid.full,
            name=contact_jid.nick.title()
        )
        groups = groups or []
        for group_name in groups:
            group = RosterGroup.create(group_name)
            item.append(group)

        new_contact.append(item)
        params = {
            'type': 'set',
            'from': from_jid.full,
            'to': contact_jid.domain
        }
        self.send(IQ.with_child_and_attributes(new_contact, **params))


class FakeXMLStream(object):
    """Fake XMLStream that is used for testing extensions that send nodes
    to the server.
    """
    def __init__(self, jid):
        self.output = []
        self.on = create_stream_events()
        self.bound_jid = JID(jid)
        self.jid = jid

    def send(self, node):
        self.output.append(node)

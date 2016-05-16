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
from xmpp.core import ET

from speakers import Speaker as Events
from xmpp.core import generate_id
from xmpp.util import stderr
from xmpp.extensions import get_known_extensions
from xmpp.models import (
    Node,
    Error,
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
    RosterQuery,
    RosterItem,
    RosterGroup,
    MissingJID,
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


def sanitize_feed(data):
    data = xml_cleanup_regex1.sub('', data)
    return data.lstrip()


def create_spool(data):
    treated = data.replace('><', '>\n<')
    return treated.splitlines()


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
    ])


class XMLStream(object):
    """`XML Stream <https://xmpp.org/rfcs/rfc3920.html#streams>`_ behavior class.

    :param connection: a :py:class:`~xmpp.networking.core.XMPPConnection` instance
    :param debug: whether to print errors to the stderr
    """

    def __init__(self, connection, debug=False):
        self._state = STREAM_STATES.IDLE
        self._connection = connection
        self._tls_connection = None
        self._connection.on.ready_to_write(self.ready_to_write)
        self._connection.on.ready_to_read(self.ready_to_read)
        self.extension = {}
        self.on = create_stream_events()
        self.on.node(self.route_nodes)

        if debug:
            self.on.error(lambda _, data: stderr.bold_red("error: {0}".format(data)))
            self.on.closed(lambda _, data: stderr.bold_yellow("XMLStream closed by the server"))
            self.on.iq_error(lambda _, data: stderr.bold_red("error: {0}".format(data)))
            self.on.unhandled_xml(lambda _, data: stderr.bold_red("unhandled xml: {0}".format(data)))
        else:
            self.on.unhandled_xml(lambda event, xml: logger.warning("unhandled xml: %s", xml))

        self.reset()

    @property
    def bound_jid(self):
        """a :py:class:`~xmpp.models.core.JID` or ``None``

        Automatically captured from the XML traffic.
        """
        return self.__bound_jid

    def reset(self):
        """resets the minimal state of the XML Stream, that is:
        * attributes of the <stream> sent by the server during negotiation, used by :py:meth:`~xmpp.stream.XMLStream.id`
        * a bound JID sent by the server
        * a successful sasl result node to leverage :py:meth:`~xmpp.stream.XMLStream.has_gone_through_sasl`
        """
        self._buffer = []
        # minimal state:
        self.__sasl_result = None
        self.__bound_jid = None

        self.resource_name = 'xmpp-{0}'.format(uuid.uuid4())
        self.nodes = []
        self.stream_node = None
        self.parser = self.make_parser()
        self.load_extensions()

    def load_extensions(self):
        """reloads all the available extensions bound to this stream"""
        self.extension = {}
        for number, Extension in get_known_extensions():
            self.extension[number] = Extension(self)

    def handle_bound_jid(self, node):
        jid = JID(node.value.strip())
        self.__bound_jid = jid
        self.on.bound_jid.shout(jid)

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

    def route_nodes(self, _, node):
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
        }
        NodeClass = type(node)
        event = ROUTES.get(NodeClass)
        if type(node) == Node:
            logger.warning("no model defined for %s: %r", node.to_xml(), node)
            return

        if isinstance(node, Error):
            self.on.error.shout(node)

        if event:
            if hasattr(event, 'shout'):
                event.shout(node)
            else:
                event(node)

    @property
    def id(self):
        """returns the stream id provided by the server. ``<stream:stream id="SOMETHING">``

        Mainly used by the
        :py:meth:`~xmpp.extensions.xep0114.Component.authenticate`
        when crafting the secret.
        """
        if self.stream_node is None:
            return

        return self.stream_node.attr.get('id')

    def parse(self):
        """attempts to parse whatever is in the buffer of the incremental XML
        parser and creates a new parser."""
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

    def ready_to_read(self, _, connection):
        """event handler for the ``on.ready_to_read`` event of a XMPP Connection.

        You should probably never have to call this by hand, use
        :py:meth:`~xmpp.stream.XMLStream.bind` instead
        """

        self.feed(connection.receive())

        node = self.parse()
        if node:
            self.on.node.shout(node)

    def ready_to_write(self, _, connection):
        """even handler for the ``on.ready_to_write`` event of a XMPP
        Connection.

        You should probably never have to call this by hand, use
        :py:meth:`~xmpp.stream.XMLStream.bind` instead
        """
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
        """sends a XML serialized Node through the bound XMPP connection

        :param node: the :py:class:`~xmpp.models.node.Node`
        """
        self._connection.send(node.to_xml())

    def close(self, disconnect=True):
        """sends a final ``</stream:stream>`` to the server then immediately
        closes the bound TCP connection,disposes it and resets the
        minimum state kept by the stream, so it can be reutilized right away.
        """
        self._connection.send(b'</stream:stream>')
        self._state = STREAM_STATES.IDLE

        if disconnect:
            self._connection.disconnect()

        self.reset()
        self._connection = None

    def open_client(self, domain):
        """Sends a <stream:stream xmlns="jabber:client"> to the given domain

        :param domain: the FQDN of the XMPP server
        """
        initial = Stream.create_client(
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
        """feeds the stream with incoming data from the XMPP server.
        This is the basic entrypoint for usage with the XML received
        from the :py:class:`~xmpp.networking.core.XMPPConnection`

        :param data: the XML string

        """
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

    # def finish_tls_upgrade(self, connection):
    #     if self._connection != connection:
    #         logger.critical("finish_tls_upgrade: weird!!")

    #     self._tls_connection = connection

    # def is_under_tls(self):
    #     return self._tls_connection is not None
    def handle_sasl_success(self, node):
        self.on.sasl_success.shout(node)

    def handle_sasl_failure(self, node):
        self.__sasl_result = None
        self.on.sasl_failure.shout(node)

    def finish_sasl(self, result):
        self.__sasl_result = result
        self.set_state(STREAM_STATES.AUTHENTICATED)

    def has_gone_through_sasl(self):
        return self.__sasl_result is not None

    def send_sasl_auth(self, mechanism, message):
        """sends a SASL response to the server in order to proceed with authentication handshakes

        :param mechanism: the name of SASL mechanism (i.e. SCRAM-SHA-1, PLAIN, EXTERNAL)
        """
        node = SASLAuth.prepare(mechanism, message.encode())
        self.send(node)
        return node

    def send_sasl_response(self, mechanism, message):
        """sends a SASL response to the server in order to proceed with authentication handshakes

        :param mechanism: the name of SASL mechanism (i.e. SCRAM-SHA-1, PLAIN, EXTERNAL)
        """
        node = SASLResponse.prepare(mechanism, message)
        self.send(node)
        return node

    def bind_to_resource(self, name):
        """sends an ``<iq type="set"><resource>name</resource></iq>`` in order to bind the resource

        :param name: the name of the resource
        """
        iq = IQ.create(type='set', id=generate_id())
        iq.append(ResourceBind.with_resource(name))
        self.send(iq)

    def send_presence(self, to=None, delay=None, priority=10, **params):
        """sends presence

        :param to: jid to receive presence.
        :param delay: if set, it must be a ISO compatible date string
        :param priority: the priority of this resource
        """

        from_jid = params.get('from')
        if from_jid:
            from_jid = JID(from_jid)
        elif self.bound_jid:
            from_jid = self.bound_jid
        else:
            msg = 'Presence cannot be sent when missing the "from" jid'
            raise MissingJID(msg)

        params['from'] = from_jid.full
        if to:
            params['to'] = JID(to).full

        presence = Presence.create(**params)

        if delay:
            delay_params = {
                'stamp': delay,
                'from': from_jid.full
            }
            presence.append(PresenceDelay.create(**delay_params))

        if priority:
            node = PresencePriority.create(bytes(priority))
            presence.append(node)

        self.send(presence)

    def send_message(self, message, to, **params):
        """
        :param message: the string with the message
        :param to: the jid to send the message to
        :param **params: keyword args for designating attributes of the message
        """
        self.send(Message.create(message, to=to, **params))

    def add_contact(self, contact_jid, from_jid=None, groups=None):
        """adds a contact to the roster of the ``bound_jid`` or the provided ``from_jid`` parameter.

        `Automatically <https://xmpp.org/rfcs/rfc3921.html#int>`_
        sends a ``<presence type="subscribe">`` with a subsequent
        ``<iq type="set">``.


        :param contact_jid: the jid to add in the roster
        :param from_jid: custom ``from=`` field to designate the owner of the roster
        :param groups: a list of strings with group names to categorize this contact in the roster

        """
        from_jid = JID(from_jid or self.bound_jid)
        contact_jid = JID(contact_jid)

        new_contact = RosterQuery.create()
        item = RosterItem.create(
            jid=contact_jid.full,
            name=contact_jid.nick.title()
        )
        if isinstance(groups, basestring):
            groups = [groups]
        elif not isinstance(groups, list):
            groups = []

        for group_name in groups:
            group = RosterGroup.create(group_name)
            item.append(group)

        new_contact.append(item)
        params = {
            'type': 'set',
            'from': from_jid.full,
            'to': contact_jid.bare,
        }
        self.send_presence(**{'from': from_jid.bare, 'to': contact_jid.full, 'type': 'subscribe'})
        self.send(IQ.with_child_and_attributes(new_contact, **params))


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
        if not self.nodes:
            # always have only one node
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
        else:
            target.text += data

        return False

    def notify_and_store_node(self, element):
        node = Node.from_element(element)
        self.nodes.append(node)
        return node

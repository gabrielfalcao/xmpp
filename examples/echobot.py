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
import time
import logging
import traceback
import coloredlogs

from xmpp import XMLStream
from xmpp import XMPPConnection
from xmpp import JID
from xmpp.auth import SASLAuthenticationHandler

DEBUG = True

DOMAIN = 'falcao.it'
jid = JID('presence1@falcao.it/xmpp-test')
password = 'presence1'
SASL_MECHANISM = 'SCRAM-SHA-1'


def application():
    # Setting up logs
    coloredlogs.install(level=DEBUG and logging.DEBUG or logging.INFO)

    # create a non-blocking XMPP-connection
    connection = XMPPConnection(DOMAIN, 5222, debug=DEBUG)

    # create a XML stream
    stream = XMLStream(connection, debug=DEBUG)

    # prepare the SASL mechanism
    sasl = SASLAuthenticationHandler(SASL_MECHANISM, jid, password)
    sasl.bind(stream)

    @stream.on.closed
    def stream_closed(event, node):
        connection.disconnect()
        connection.connect()
        stream.reset()

    @stream.on.presence
    def handle_presence(event, presence):
        logging.debug("presence from: %s %s(%s)", presence.attr['from'], presence.status.strip(), presence.show.strip())

    @connection.on.tcp_established
    def step1_open_stream(event, host_ip):
        "sends a <stream:stream> to the XMPP server"
        logging.info("connected to %s", host_ip)
        stream.open_client(jid.domain)

    @stream.on.sasl_support
    def step2_send_sasl_auth(event, node):
        "sends a <auth /> to the XMPP server"
        sasl.authenticate()

    @sasl.on.success
    def step3_handle_success(event, result):
        "the SASL authentication succeeded, it's our time to reopen the stream"
        stream.open_client(jid.domain)

    @stream.on.bind_support
    def step4_bind_to_a_resource_name(event, node):
        "the server said it supports binding"
        stream.bind_to_resource(jid.resource)

    @stream.on.bound_jid
    def step5_send_presence(event, jid):
        stream.send_presence()
        logging.info("echobot jid: %s", jid.text)

    @stream.on.presence
    def step6_ensure_connectivity(event, presence):
        if presence.delay:
            stream.send_presence()

    @connection.on.ready_to_write
    def keep_alive(event, connection):
        if stream.has_gone_through_sasl() and (time.time() % 60 == 0):
            print('keepalive')
            connection.send_whitespace_keepalive()

    @stream.on.message
    def auto_reply(event, message):
        stream.send_presence()

        from_jid = JID(message.attr['from'])
        if message.is_composing():
            logging.warning("%s is composing", from_jid.nick)

        if message.is_active():
            logging.warning("%s is active", from_jid.nick)

        body = message.get_body()
        if body:
            logging.critical("%s says: %s", from_jid.nick, body)
            stream.send_message(body, to=from_jid.text)
            stream.send_presence(to=from_jid.text)

    connection.connect()

    try:
        while connection.is_alive():
            connection.loop_once()

    except KeyboardInterrupt as e:
        print("\r{0}".format(traceback.format_exc(e)))

        raise SystemExit(1)


if __name__ == '__main__':
    application()

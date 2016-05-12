#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging
import traceback
import coloredlogs

from xmpp import XMLStream
from xmpp import XMPPConnection
from xmpp import JID
from xmpp import sasl
from xmpp.auth import SASLAuthenticationHandler


DEBUG = True

DOMAIN = 'falcao.it'
jid = JID('presence1@falcao.it/xmpp-test')
password = 'presence1'
SASL_MECHANISM = 'SCRAM-SHA-1'
SASL_HANDLER = sasl.client_authenticator_factory(SASL_MECHANISM)


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

    # prepare service discovery helper
    service_discovery = stream.extension['0030']

    @stream.on.closed
    def stream_closed(event, node):
        connection.disconnect()
        connection.connect()
        stream.recycle()

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
        logging.info("Querying %s for disco items", jid.domain)
        service_discovery.query_items(to=jid.domain)
        logging.info("Querying %s for disco features and components", jid.domain)
        service_discovery.query_info(to=jid.domain)

    @stream.on.presence
    def step6_ensure_connectivity(event, presence):
        if presence.delay:
            stream.send_presence()

    @connection.on.ready_to_write
    def keep_alive(event, connection):
        if stream.has_gone_through_sasl() and (time.time() % 60 == 0):
            print 'keepalive'
            connection.send_whitespace_keepalive()

    @service_discovery.on.query_items
    def handle_disco_items(event, query):
        logging.info("Disco Items:\n%s", "\n".join(map(repr, query.get_children())))

    @service_discovery.on.query_info
    def handle_disco_info(event, query):
        logging.info("Disco Features and Components:\n%s", "\n".join(map(repr, query.get_children())))

    connection.connect()

    try:
        while connection.is_alive():
            connection.poll()

    except KeyboardInterrupt as e:
        print "\r{0}".format(traceback.format_exc(e))

        raise SystemExit(1)

if __name__ == '__main__':
    application()

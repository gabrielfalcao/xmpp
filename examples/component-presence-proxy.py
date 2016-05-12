#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import logging
import traceback
import coloredlogs

from xmpp import XMLStream
from xmpp import JID
from xmpp import XMPPConnection


DEBUG = True
DOMAIN = 'falcao.it'
PORT = 5347
COMPONENT_NAME = 'internal.falcao.it'
COMPONENT_SECRET = 'somethingsecret'
MANAGER_JID = 'manager@falcao.it'
PRESENCE_JIDS = ['presence{0}@internal.falcao.it/smallclient'.format(i) for i in range(10)]


def application():
    # Setting up logs
    coloredlogs.install(level=DEBUG and logging.DEBUG or logging.INFO)

    # create a non-blocking XMPP-connection
    connection = XMPPConnection(DOMAIN, PORT, debug=DEBUG)

    # create a XML stream
    stream = XMLStream(connection, debug=DEBUG)

    @stream.on.closed
    def auto_reconnect(event, node):
        logging.warning("server closed stream %s:", node)

    @stream.on.error
    def stream_error(event, error):
        logging.error(error.to_xml())

    @connection.on.ready_to_write
    def keep_alive(event, connection):
        "send whitespace keep alive every 60 seconds"
        if stream.is_authenticated_component() and (int(time.time()) % 60 == 0):
            print 'keepalive'
            connection.send_whitespace_keepalive()

    @connection.on.tcp_established
    def step1_open_stream(event, host_ip):
        "sends a <stream:stream> to the XMPP server"
        logging.info("connected to %s", host_ip)
        stream.open_component(COMPONENT_NAME)

    @stream.on.open
    def step2_send_handshake(event, node):
        "sends a <auth /> to the XMPP server"
        stream.send_secret_handshake(COMPONENT_SECRET)

    @stream.on.presence
    def step3_auto_subscribe(event, presence):
        from_jid = presence.attr['to']
        presence_type = presence.attr.get('type')

        params = {'from': from_jid, 'to': presence.attr['from']}
        if presence_type == 'subscribe':
            stream.send_presence(type='subscribed', **params)

        elif presence_type == 'subscribed':
            stream.send_presence(**params)

    @stream.on.success_handshake
    def send_presence(event, node):
        stream.send_presence(**{'from': random.choice(PRESENCE_JIDS), 'to': 'falcao.it'})

    connection.connect()

    try:
        while connection.is_alive():
            connection.poll()
            from_jid = random.choice(PRESENCE_JIDS)
            if stream.is_authenticated_component():
                stream.send_presence(**{'from': from_jid, 'to': MANAGER_JID})
                connection.poll()
                stream.add_contact(MANAGER_JID, from_jid=from_jid)
                connection.poll()

    except KeyboardInterrupt as e:
        print "\r{0}".format(traceback.format_exc(e))

        raise SystemExit(1)


if __name__ == '__main__':
    application()

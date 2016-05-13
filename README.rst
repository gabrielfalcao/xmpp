XMPP
====

+---------+--------+
| version | 0.1.1  |
+---------+--------+
| license | LGPLv3 |
+---------+--------+


Simplistic and stateless XMPP implementation for python. A building
block for non-blocking XMPP clients, components, gateways and servers.



Acknowledgements
================

This library was mostly written from scratch, except for the ``xmpp.sasl`` which is a modified copy of the contents of the ``pyxmpp2`` library


Examples
========


Echo Bot
--------

.. code:: python

    from xmpp import XMLStream
    from xmpp import XMPPConnection
    from xmpp import JID
    from xmpp.auth import SASLAuthenticationHandler

    DEBUG = True

    DOMAIN = 'falcao.it'
    jid = JID('presence1@falcao.it/xmpp-test')
    password = 'presence1'
    SASL_MECHANISM = 'SCRAM-SHA-1'

    sasl = SASLAuthenticationHandler(SASL_MECHANISM, jid, password)

    # create a network connection
    connection = XMPPConnection(DOMAIN, 5222, debug=DEBUG)
    # create handler of XML nodes
    stream = XMLStream(connection, debug=DEBUG)
    # attach the authenticator to events of the stream
    sasl.bind(stream)

    @stream.on.bound_jid
    def step5_send_presence(event, jid):
        stream.send_presence()
        logging.info("echobot jid: %s", jid.text)

    @stream.on.message
    def act_as_echobot(event, message):
        "finally the echobot"
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

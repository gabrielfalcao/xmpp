XMPP
----

Simplistic and stateless XMPP implementation for python. A building
block for non-blocking XMPP clients, components, gateways and servers.


.. code:: python


.. testcode::

    import logging
    import coloredlogs
    coloredlogs.install(level=logging.DEBUG)

    from xmpp import XMLStream
    from xmpp import XMPPConnection


    connection = XMPPConnection('falcao.it', 5222)
    stream = XMLStream(connection)

    @stream.on.node
    def node_in(event, node):
        logging.info("NODE: %s", node.to_xml())

    @connection.on.read
    def read(event, data):
        logging.info("RECV: %s", data)

    @connection.on.write
    def write(event, data):
        logging.info("SEND: %s", data)

    connection.connect()
    stream.authenticate(
        jid='manager@falcao.it/xmpp-test',
        password='bot1234'
    )

    try:
        while connection.is_alive():
            connection.negotiate()
    except KeyboardInterrupt:
        raise SystemExit(1)

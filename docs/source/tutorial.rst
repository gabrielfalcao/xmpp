.. _Tutorial:

.. highlight:: python


XMPP Tutorial
=============

This is a simple barebones tutorial of XMPP in python.


.. note:: This tutorial **does not** cover use of parallel execution
          like light threads, posix threads or subprocessed. For the
          didatic purposes we will be building a **blocking**
          application.


Client TCP Connection
---------------------

Let's start by creating a simple TCP connection to a XMPP server.

The XMPP toolkit provides the
:py:class:`~xmpp.networking.core.XMPPConnection` that performs all the
TCP socket management and exposes simple events.


code
~~~~

Let's open stream by sending a raw XML string, so that you can get a
feeling of what the stream negotiation looks like.

Notice the ``debug=True`` in the connection creation, that tells the
lib to print the traffic in the ``stderr``, this can be useful for
debugging your application.


.. code:: python

    from xmpp import XMPPConnection
    from xmpp import JID


    user = JID('test@falcao.it/xmpp-toolkit')

    connection = XMPPConnection(user.domain, 5222, debug=True)


    @connection.on.tcp_established
    def step1_open_stream(event, host_ip):
        "sends a <stream:stream> to the XMPP server"

        connection.send('''<stream:stream
              from='test@falcao.it'
              to='falcao.it'
              version='1.0'
              xml:lang='en'
              xmlns='jabber:client'
              xmlns:stream='http://etherx.jabber.org/streams'>
        ''')


    @connection.on.read
    def step2_show_output(event, host_ip):
        connection.close()

    connection.connect()

    while connection.is_active():
        connection.loop_once()

would output something like this

.. code:: bash

    XMPP SEND: <?xml version='1.0'?><stream:stream
            from='test@falcao.it'
            to='falcao.it'
            version='1.0'
            xml:lang='en'
            xmlns='jabber:client'
            xmlns:stream='http://etherx.jabber.org/streams'>
    XMPP RECV: <?xml version='1.0'?><stream:stream
          xmlns:stream='http://etherx.jabber.org/streams'
          version='1.0'
          from='falcao.it'
          id='c1a2cc21-a35d-4545-807b-2b368e567e4e'
          xml:lang='en'
          xmlns='jabber:client'>
            <stream:features>
              <starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>
              <register xmlns='http://jabber.org/features/iq-register'/>
              <mechanisms xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>
                <mechanism>SCRAM-SHA-1</mechanism>
              </mechanisms>
            </stream:features>
    TCP DISCONNECT: intentional

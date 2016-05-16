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

Also you should never write XML manually, instead use a :py:class:`~xmpp.stream.XMLStream` bound to a connection in order to send

code
~~~~

Notice the ``debug=True`` in the connection creation, that tells the
lib to print the traffic in the ``stderr``, this can be useful for
debugging your application.


.. code:: python

    from xmpp import XMPPConnection
    from xmpp import XMLStream
    from xmpp import JID


    class Application(object):

        def __init__(self, jid, password):
            self.user = JID(jid)
            self.password = password
            self.connection = XMPPConnection(self.user.domain, 5222, debug=True)
            self.stream = XMLStream(self.connection, debug=True)

            self.setup_handlers()

        def setup_handlers(self):
            self.connection.on.tcp_established(self.do_open_stream)
            self.connection.on.read(self.do_disconnect)

        def do_open_stream(self, *args, **kw):
            self.stream.open(self.user.domain)

        def do_disconnect(self, *args, **kw):
            self.connection.close()

        def run_forever(self):
            self.connection.connect()

            while self.connection.is_active():
                self.connection.loop_once()


    if __name__ == '__main__':
        app = Application('romeo@capulet.com', 'juli3t')
        app.run_forever()

would output something like this

.. code:: bash

    XMPP SEND: <?xml version='1.0'?><stream:stream
            from='romeo@capulet.com'
            to='capulet.com'
            version='1.0'
            xml:lang='en'
            xmlns='jabber:client'
            xmlns:stream='http://etherx.jabber.org/streams'>
    XMPP RECV: <?xml version='1.0'?><stream:stream
          xmlns:stream='http://etherx.jabber.org/streams'
          version='1.0'
          from='capulet.com'
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

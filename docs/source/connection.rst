.. _Connection:

.. highlight:: python


XMPP Connection
===============


Events
------

+------------------------+--------------------------------------------------+
| **tcp_established**    | the TCP connection was established               |
+------------------------+--------------------------------------------------+
| **tcp_restablished**   | the TCP connection was lost and restablished     |
+------------------------+--------------------------------------------------+
| **tcp_downgraded**     | the TLS connection was downgraded to TCP         |
+------------------------+--------------------------------------------------+
| **tcp_disconnect**     | the TCP connection was lost                      |
+------------------------+--------------------------------------------------+
| **tcp_failed**         | the TCP connection failed to be established      |
+------------------------+--------------------------------------------------+
| **ssl_established**    | the TLS connection was established               |
+------------------------+--------------------------------------------------+
| **ssl_invalid_chain**  | the TLS handshake failed for invalid chain       |
+------------------------+--------------------------------------------------+
| **ssl_invalid_cert**   | the TLS handshake failed for invalid server cert |
+------------------------+--------------------------------------------------+
| **ssl_failed**         | failed to establish a TLS connection             |
+------------------------+--------------------------------------------------+
| **ssl_start**          | started SSL negotiation                          |
+------------------------+--------------------------------------------------+
| **write**              | the TCP/TLS connection is ready to send data     |
+------------------------+--------------------------------------------------+
| **read**               | the TCP/TLS connection is ready to receive data  |
+------------------------+--------------------------------------------------+
| **ready_to_write**     | the TCP/TLS connection is ready to send data     |
+------------------------+--------------------------------------------------+
| **ready_to_read**      | the TCP/TLS connection is ready to receive data  |
+------------------------+--------------------------------------------------+


API
---

.. autoclass:: xmpp.networking.core.XMPPConnection
   :members:

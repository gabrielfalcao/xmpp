XMPP
====

+---------+--------+
| version | 0.1.3  |
+---------+--------+
| license | LGPLv3 |
+---------+--------+


Simplistic and stateless XMPP implementation for python. A building
block for non-blocking XMPP clients, components, gateways and servers.

.. image:: https://readthedocs.org/projects/xmpp/badge/?version=latest
   :target: http://xmpp.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://travis-ci.org/gabrielfalcao/xmpp.svg?branch=master
   :target: https://travis-ci.org/gabrielfalcao/xmpp

Acknowledgements
================

This library was mostly written from scratch, except for the ``xmpp.sasl`` which is a modified copy of the contents of the ``pyxmpp2`` library

Documentation
=============

Available at `xmpp.readthedocs.io <https://xmpp.readthedocs.io/en/latest/>`_


Client Bot Examples
===================

You can find some in the examples folder:

* `Echo Bot <https://github.com/gabrielfalcao/xmpp/blob/master/examples/echobot.py>`_: Auto Replies to anyone who messages it
* `Service Discovery <https://github.com/gabrielfalcao/xmpp/blob/master/examples/service_discovery.py>`_: How to use the Disco (xep 0030)
* `Presence Bot <https://github.com/gabrielfalcao/xmpp/blob/master/examples/presence-auto-subscriber.py>`_: Client that automatically sends presence and befriends anyone who sends it presence


Component Examples
==================

You can find some in the examples folder:

* `Presence Proxy notifier <https://github.com/gabrielfalcao/xmpp/blob/master/examples/component-presence-proxy.py>`_: Component that befriends a specific JID and sends present to it, in behalf of many jids

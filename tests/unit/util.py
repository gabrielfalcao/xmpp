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

import re
from sure import scenario
from speakers import Speaker as Events
from mock import MagicMock
from mock import Mock
from xmpp.models.core import JID
from xmpp.stream import create_stream_events
from xmpp.networking.core import create_connection_events


def XML(string):
    return re.sub(r'\n\s+', ' ', string).replace('> <', '><').strip()


def EventHandlerMock(name):
    filename = "{}.py".format(name)
    handler = MagicMock(name=name, __name__=name)
    handler.func_code = Mock(name='func_code({})'.format(name))
    handler.__code__ = Mock(name='__code__({})'.format(name))
    handler.func_code.co_firstlineno = 1
    handler.func_code.co_filename = filename
    handler.__code__.co_firstlineno = 1
    handler.__code__.co_filename = filename
    handler.return_value = True
    return handler


def nodes_from_call(handler):
    nodes = []
    for call in handler.call_args_list:
        nodes.append(call[0][-1].__class__)

    return nodes


def clear_events(context):
    Events.release_all()


event_test = scenario(clear_events, clear_events)


class FakeConnection(object):
    def __init__(self):
        self.output = []
        self.on = create_connection_events()

    def send(self, data):
        self.output.append(data)


class FakeXMLStream(object):
    """Fake XMLStream that is used for testing extensions that send nodes
    to the server.
    """
    def __init__(self, jid):
        self.output = []
        self.on = create_stream_events()
        self.bound_jid = JID(jid)
        self.jid = jid

    def send(self, node):
        self.output.append(node)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from sure import scenario
from speakers import Speaker as Events
from mock import MagicMock


def XML(string):
    return re.sub(r'\n\s+', ' ', string).replace('> <', '><').strip()


def EventHandlerMock(name):
    handler = MagicMock(name=name, __name__=name)
    handler.func_code.co_firstlineno = 1
    handler.func_code.co_filename = name
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

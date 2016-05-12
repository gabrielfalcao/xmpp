#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from xmpp import sasl
from xmpp.models import JID
from speakers import Speaker as Events


class SASLAuthenticationHandler(object):
    def __init__(self, mechanism, jid, password):
        self.jid = JID(jid)
        self.password = password
        self.mechanism = mechanism
        self.sasl = sasl.client_authenticator_factory(mechanism)
        self.on = Events('sasl', [
            'success',  # sasl authentication succeeded
            'failure',  # sasl authentication failure
            'unknown',  # received a sasl response but the stream is already authenticated
        ])
        self.stream = None
        self.connection = None

    @property
    def properties(self):
        return {
            'username': self.jid.nick,
            'password': self.password,
        }

    def bind(self, stream):
        if self.stream:
            raise RuntimeError('{0} is already bound to the stream {1}'.format(stream))

        self.stream = stream
        self.stream.on.sasl_challenge(self.on_challenge)
        self.stream.on.sasl_success(self.on_response)
        self.stream.on.sasl_failure(self.on_failure)

    def authenticate(self):
        message = self.sasl.start(self.properties)
        self.stream.send_sasl_auth(self.mechanism, message.encode())

    def on_failure(self, event, error):
        logging.error("Failed SASL negotiation: %s", error)

    def on_challenge(self, event, challenge):
        if self.stream.has_gone_through_sasl():
            return

        data = challenge.get_data()
        message = self.sasl.challenge(data)
        self.stream.send_sasl_response(self.mechanism, message.encode())

    def on_response(self, event, response):
        if self.stream.has_gone_through_sasl():
            return

        data = response.get_data()
        result = self.sasl.finish(data)
        if isinstance(result, sasl.Success):
            self.stream.finish_sasl(result)
            self.on.success.shout(result)

        else:
            logging.error("Failed SASL verification %s", result)
            self.on.failure.shout(result)

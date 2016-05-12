# <xmpp - stateless and concurrency-agnostic XMPP library for python>
#
# (C) Copyright 2016 Gabriel Falcao <gabriel@nacaolivre.org>
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

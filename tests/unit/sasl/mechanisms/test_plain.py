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

from xmpp.sasl.core import Success
from xmpp.sasl.core import Failure
from xmpp.sasl.core import Challenge
from xmpp.sasl.core import Response
from xmpp.sasl.plain import PlainClientAuthenticator


def test_start_plain_client_authenticator_start():
    ('PlainClientAuthenticator.start() should return a challenge response')

    # Given a plain authenticator
    authenticator = PlainClientAuthenticator()

    # When I call start providing username and password
    response = authenticator.start({
        'username': 'romeo',
        'password': 'jul137my10v3',
    })

    # Then it should return the initial challenge as a xmpp.sasl.Response
    response.should.be.a(Response)
    response.data.should.equal(b'\x00romeo\x00jul137my10v3')
    response.encode().should.equal('AHJvbWVvAGp1bDEzN215MTB2Mw==')

    # And challenging manually will fail
    result = authenticator.challenge(None)
    result.should.be.a(Failure)
    result.reason.should.equal('extra-challenge')


def test_start_plain_client_authenticator_finish():
    ('PlainClientAuthenticator.finish() should return the authentication properties')

    # Given a plain authenticator
    authenticator = PlainClientAuthenticator()

    # When I call start providing username and password
    authenticator.start({
        'username': 'romeo',
        'password': 'jul137my10v3',
        'authzid': 'w00t',
    })
    response = authenticator.finish(None)

    # Then it should return the initial challenge as a xmpp.sasl.Response
    response.should.be.a(Success)
    response.properties.should.equal({
        'username': 'romeo',
        'authzid': 'w00t',
    })

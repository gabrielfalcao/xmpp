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

from xmpp.sasl import get_client_mechanisms
from xmpp.sasl import get_server_mechanisms
from xmpp.sasl import client_authenticator_factory
from xmpp.sasl import server_authenticator_factory
from xmpp.sasl import filter_mechanism_list
from xmpp.sasl import PasswordDatabase


def test_get_client_mechanisms():
    "xmpp.sasl.get_client_mechanisms() should return a list of supported mechanisms"

    get_client_mechanisms().should.equal(['EXTERNAL', 'PLAIN', 'SCRAM-SHA-1', 'SCRAM-SHA-1-PLUS'])


def test_get_server_mechanisms():
    "xmpp.sasl.get_server_mechanisms() should return a list of supported mechanisms"

    get_server_mechanisms().should.equal(['PLAIN', 'SCRAM-SHA-1', 'SCRAM-SHA-1-PLUS'])


def test_server_authenticator_factory():
    "xmpp.sasl.server_authenticator_factory() should return an authenticator"

    # given a password database
    database = PasswordDatabase()

    # when i get an authenticator
    authenticator = server_authenticator_factory('SCRAM-SHA-1', database)

    # then it should be correct
    authenticator.name.should.equal('SCRAM-SHA-1')


def test_client_authenticator_factory():
    "xmpp.sasl.client_authenticator_factory() should return an authenticator"

    # when i get an authenticator
    authenticator = client_authenticator_factory('SCRAM-SHA-1')

    # then it should be correct
    authenticator.name.should.equal('SCRAM-SHA-1')


def test_filter_mechanisms():
    "xmpp.sasl.filter_mechanism_list() should a list of valid mechanisms"

    # client side allowing
    filter_mechanism_list(
        [
            'FOO',
            'PLAIN',
            'SCRAM-SHA-1'
            'SCRAM-SHA-1-PLUS',
            'EXTERNAL',
        ],
        {
            'username': 'foo',
            'password': 'bar',
        },
        server_side=False,
        allow_insecure=False,
    ).should.equal(['PLAIN'])

    # client side with security layer
    filter_mechanism_list(
        [
            'FOO',
            'PLAIN',
            'SCRAM-SHA-1'
            'SCRAM-SHA-1-PLUS',
            'EXTERNAL',
        ],
        {
            'username': 'foo',
            'password': 'bar',
            'security-layer': 'tls',
        },
        server_side=False,
        allow_insecure=False,
    ).should.equal(['PLAIN', 'EXTERNAL'])

    # client side allowing insecure
    filter_mechanism_list(
        [
            'FOO',
            'PLAIN',
            'SCRAM-SHA-1'
            'SCRAM-SHA-1-PLUS',
            'EXTERNAL',
        ],
        {
            'username': 'foo',
            'password': 'bar',
            'security-layer': 'tls',
        },
        server_side=False,
        allow_insecure=True,
    ).should.equal(['PLAIN', 'EXTERNAL'])

    # client side insufficient properties
    filter_mechanism_list(
        [
            'foo',
            'plain',
            'scram-sha-1'
            'scram-sha-1-plus',
            'external',
        ],
        {
        },
        server_side=True,
        allow_insecure=True,
    ).should.equal(['PLAIN'])

    # server side allowing
    filter_mechanism_list(
        [
            'FOO',
            'PLAIN',
            'SCRAM-SHA-1'
            'SCRAM-SHA-1-PLUS',
            'EXTERNAL',
        ],
        {
            'username': 'foo',
            'password': 'bar',
        },
        server_side=True,
        allow_insecure=False,
    ).should.equal(['PLAIN'])

    # server side with security layer
    filter_mechanism_list(
        [
            'foo',
            'plain',
            'scram-sha-1'
            'scram-sha-1-plus',
            'external',
        ],
        {
            'username': 'foo',
            'password': 'bar',
            'security-layer': 'tls',
        },
        server_side=True,
        allow_insecure=False,
    ).should.equal(['PLAIN'])

    # server side allowing insecure
    filter_mechanism_list(
        [
            'foo',
            'plain',
            'scram-sha-1'
            'scram-sha-1-plus',
            'external',
        ],
        {
            'username': 'foo',
            'password': 'bar',
        },
        server_side=True,
        allow_insecure=True,
    ).should.equal(['PLAIN'])

    # server side insufficient properties
    filter_mechanism_list(
        [
            'foo',
            'plain',
            'scram-sha-1'
            'scram-sha-1-plus',
            'external',
        ],
        {
        },
        server_side=True,
        allow_insecure=True,
    ).should.equal(['PLAIN'])

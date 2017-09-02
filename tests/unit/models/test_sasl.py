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

from xmpp.models import SASLAuth
from xmpp.models import SASLChallenge
from xmpp.models import SASLResponse
from xmpp.models import SASLSuccess


def test_auth_prepare():
    "SASLAuth.prepare() should return a node with the mechanism name"

    node = SASLAuth.prepare('SCRAM-SHA-1', 'data')
    node.to_xml().should.equal(
        '<auth mechanism="SCRAM-SHA-1" xmlns="urn:ietf:params:xml:ns:xmpp-sasl">data</auth>'
    )


def test_challenge_decoded():
    ("SASLChallenge.decoded should return the base64 "
     "decoded version of the challenge")

    node = SASLChallenge.create('something'.encode('base64'))
    node.decoded.should.equal('something')


def test_success_decoded():
    ("SASLSuccess.decoded should return the base64 "
     "decoded version of the success")

    node = SASLSuccess.create('something'.encode('base64'))
    node.decoded.should.equal('something')


def test_response_prepare():
    "SASLResponse.prepare() should return a node with the mechanism name"

    node = SASLResponse.prepare('SCRAM-SHA-1', 'data')
    node.to_xml().should.equal(
        '<response mechanism="SCRAM-SHA-1" xmlns="urn:ietf:params:xml:ns:xmpp-sasl">data</response>'
    )

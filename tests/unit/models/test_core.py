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

from xmpp.models import SASLMechanismSet, SASLMechanism, Message


def test_feature_name():
    ('xmpp.models.core.Feature should have a name')

    SASLMechanismSet.create().name.should.equal('mechanisms')


def test_supported_sasl_mechanisms():
    ('xmpp.models.core.SASLMechanismSet should return a list')

    mechanisms = SASLMechanismSet.create()
    mechanisms.append(SASLMechanism.create('SCRAM-SHA-1'))
    mechanisms.append(SASLMechanism.create('MD5-DIGEST'))
    mechanisms.append(SASLMechanism.create('EXTERNAL'))

    mechanisms.supported_mechanisms().should.equal([
        'SCRAM-SHA-1',
        'MD5-DIGEST',
        'EXTERNAL',
    ])


def test_message_get_body():
    ('xmpp.models.core.Message.get_body should return '
     'the message bodies concatenated as string')

    msg = Message.create('Hello', **{'from': 'foo@bar.com', 'to': 'john@doe.com'})
    msg.add_text(' World')

    msg.get_body().should.equal('Hello World')
    msg.to_xml().should.look_like(
        '<message from="foo@bar.com" to="john@doe.com" type="chat"><body>Hello World</body></message>')


def test_message_composing():
    ('xmpp.models.core.Message. should return '
     'the message bodies concatenated as string')

    msg = Message.create('Hello', **{'from': 'foo@bar.com', 'to': 'john@doe.com'})
    msg.set_composing()

    msg.is_composing().should.be.true
    msg.to_xml().should.look_like(
        '<message from="foo@bar.com" to="john@doe.com" type="chat">'
        '  <body>Hello</body>'
        '  <composing xmlns="http://jabber.org/protocol/chatstates" />'
        '</message>'
    )


def test_message_active():
    ('xmpp.models.core.Message. should return '
     'the message bodies concatenated as string')

    msg = Message.create('Hello', **{'from': 'foo@bar.com', 'to': 'john@doe.com'})
    msg.set_active()

    msg.is_active().should.be.true
    msg.to_xml().should.look_like(
        '<message from="foo@bar.com" to="john@doe.com" type="chat">'
        '  <body>Hello</body>'
        '  <active xmlns="http://jabber.org/protocol/chatstates" />'
        '</message>'
    )


def test_message_paused():
    ('xmpp.models.core.Message. should return '
     'the message bodies concatenated as string')

    msg = Message.create('Hello', **{'from': 'foo@bar.com', 'to': 'john@doe.com'})
    msg.set_paused()

    msg.is_paused().should.be.true
    msg.to_xml().should.look_like(
        '<message from="foo@bar.com" to="john@doe.com" type="chat">'
        '  <body>Hello</body>'
        '  <paused xmlns="http://jabber.org/protocol/chatstates" />'
        '</message>'
    )

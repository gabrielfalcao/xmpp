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

from xmpp.models import Presence
from xmpp.models import PresenceDelay
from xmpp.models import PresencePriority
from xmpp.models import PresenceStatus
from xmpp.models import PresenceShow


def test_presence_empty():
    ('xmpp.models.Presence has properties defaulting to empty')

    node = Presence.create()
    node.delay.should.be.none
    node.priority.should.equal('')
    node.status.should.equal('')
    node.show.should.equal('')


def test_presence_delay():
    ('xmpp.models.Presence.delay should be a property '
     'that returns the stamp')

    # Given a presence with delay
    node = Presence.create()
    node.append(PresenceDelay.create(stamp='2016-05-13T14:53:30'))

    # When I check its delay
    node.delay.should.equal('2016-05-13T14:53:30')


def test_presence_priority():
    ('xmpp.models.Presence.priority should be a property '
     'that returns the stamp')

    # Given a presence with priority
    node = Presence.create()
    node.append(PresencePriority.create('10'))

    # When I check its priority
    node.priority.should.equal('10')


def test_presence_status():
    ('xmpp.models.Presence.status should be a property '
     'that returns the stamp')

    # Given a presence with status
    node = Presence.create()
    node.append(PresenceStatus.create('away'))

    # When I check its status
    node.status.should.equal('away')


def test_presence_show():
    ('xmpp.models.Presence.show should be a property '
     'that returns the stamp')

    # Given a presence with show
    node = Presence.create()
    node.append(PresenceShow.create('away'))

    # When I check its show
    node.show.should.equal('away')

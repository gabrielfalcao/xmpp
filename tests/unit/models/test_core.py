# -*- coding: utf-8 -*-
#
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

from xmpp.models import JID


def test_jid_from_string():
    ('JID() should accept a string')

    # Given a JID from string
    item = JID('user@domain.com/resource')

    # It can be represented as a full jid
    item.full.should.equal('user@domain.com/resource')

    # It can be represented as a bare jid
    item.bare.should.equal('user@domain.com')

    # It has the nick
    item.nick.should.equal('user')

    # It has the domain
    item.domain.should.equal('domain.com')

    # It has the resource
    item.resource.should.equal('resource')

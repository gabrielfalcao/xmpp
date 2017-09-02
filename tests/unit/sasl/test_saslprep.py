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

from xmpp.sasl.saslprep import SASLPREP, StringprepError


def test_rfc_examples():
    ("SASLPREP should comply with RFC examples")
    SASLPREP.prepare(u"user").should.equal(u"user")
    SASLPREP.prepare(u"USER").should.equal(u"USER")
    SASLPREP.prepare(u"\u00AA").should.equal(u"a")
    SASLPREP.prepare(u"\u2168").should.equal(u"IX")
    SASLPREP.prepare(u"I\u00ADX").should.equal(u"IX")

    (SASLPREP.prepare
     .when
     .called_with(u"\u0007")
     .should
     .have.raised(StringprepError))

    (SASLPREP.prepare
     .when
     .called_with(u"\u0627\u0031")
     .should
     .have.raised(StringprepError))

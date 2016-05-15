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
from xmpp.models.core import Stream


def test_create_client():
    ("xmpp.models.core.Stream.create_client() should return a valid node")

    # Regular Client
    Stream.create_client(to='capulet.com').to_xml().should.look_like(
        '<stream:stream to="capulet.com" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams">'
    )

    # TLS Client
    Stream.create_client(to='capulet.com', tls=True).to_xml().should.look_like(
        '<stream:stream to="capulet.com" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams">'
        '<starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls" />'
    )


def test_get_features_empty():
    ("xmpp.models.core.Stream.get_features() should return an empty dict")

    # Regular Component
    features = Stream.create_client(to='capulet.com').get_features()
    features.should.be.a(dict)
    features.should.be.empty

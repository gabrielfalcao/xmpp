# <xmpp - stateless and concurrency-agnostic XMPP library for python>
#
# Copyright (C) <2016> Gabriel Falcao <gabriel@nacaolivre.org>
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
from mock import patch
from xmpp.core import ET
from xmpp.core import generate_id
from xmpp.core import is_element
from xmpp.core import fixup_unknown_element
from tests.unit.util import XML


def test_fixup_unknown_element():
    ('fixup_unknown_element() should fix the namespace of an unknown element')

    # Given a XML
    source = XML('''
    <Scenario name="Foo Bar" xmlns="python:scenario">
        <Given xmlns="python:scenario:given">A XML</Given>
    </Scenario>''')

    # And an element from it
    element = ET.fromstring(source)

    # When I fix it up
    fixup_unknown_element(element)

    # Then it should have fixed it up
    ET.tostring(element).should.look_like(source)


@patch('xmpp.core.uuid')
def test_generate_id(uuid):
    ('core.generate_id() should generate a uuid4')

    uuid.uuid4.return_value = 'romeo'

    generate_id().should.equal(b'romeo')


def test_is_element():
    ('xmpp.core.is_element()')

    is_element(ET.Element('tag')).should.be.true
    is_element(None).should.be.false

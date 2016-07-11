# -*- coding: utf-8 -*-
#
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

from xmpp.models import IQ
from xmpp.models import ResourceBind


def test_with_child_and_attributes():
    ('xmpp.models.IQ.with_child_and_attributes has properties defaulting to empty')

    params = {
        'from': 'juliet@capulet.com',
        'to': 'capulet.com',
    }
    node = IQ.with_child_and_attributes(
        ResourceBind.with_resource('hut'),
        **params
    )

    node.to_xml().should.look_like(
        '<iq from="juliet@capulet.com" to="capulet.com"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><resource>hut</resource></bind></iq>'
    )

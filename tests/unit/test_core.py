# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from xmpp.core import ET
from xmpp.core import fixup_unknown_element
from tests.unit.util import XML


def test_fixup_unknown_element():
    ('fixup_unknown_element() should fix the namespace of an unknown element')

    # Given a XML
    source = XML('''<TestCase name="Foo Bar" xmlns="http://falcao.it/unit/testcase">
    <Given xmlns="http://falcao.it/unit/testcase">A XML</Given>
    </TestCase>''')

    # And an element from it
    element = ET.fromstring(source)

    # When I fix it up
    fixup_unknown_element(element)

    # Then it should have fixed it up
    ET.tostring(element).should.look_like(source)

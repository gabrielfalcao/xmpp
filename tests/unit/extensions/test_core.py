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
from mock import patch
from xmpp.extensions.core import Extension
from xmpp.extensions.core import ExtensionDefinitionError
from xmpp.extensions.core import get_known_extensions


def test_get_known_extensions():
    ('xmpp.extensions.get_known_extensions() returns all known extensions')

    map(lambda (x, y): (x, y.__name__), get_known_extensions()).should.equal([
        ('0030', 'ServiceDiscovery'),
        ('0114', 'Component'),
    ])


def test_definition_errors():
    ('the library should raise a nice exception')

    def missing_xep():
        class Juliet(Extension):
            pass

    def invalid_xep_number():
        class Romeo(Extension):
            __xep__ = 'xep9999'

    def already_existing_xep_number():
        class Mercutio(Extension):
            __xep__ = '0030'

    def missing_initialize():
        class Benvolio(Extension):
            __xep__ = '9999'

    def invalid_initialize():
        class Tybalt(Extension):
            __xep__ = '9999'
            initialize = 'some variable'

    missing_xep.when.called.should.have.raised(
        ExtensionDefinitionError,
        'class Juliet is missing __xep__ attribute'
    )
    invalid_xep_number.when.called.should.have.raised(
        ExtensionDefinitionError,
        'Romeo.__xep__ must be a string containg only numbers: xep9999'
    )
    already_existing_xep_number.when.called.should.have.raised(
        ExtensionDefinitionError,
        'xep 0030 is already defined by xmpp.extensions.xep0030.ServiceDiscovery'
    )
    missing_initialize.when.called.should.have.raised(
        ExtensionDefinitionError,
        'extension tests.unit.extensions.test_core.Benvolio[9999] needs an initialize(self) method defined, even if blank'
    )
    invalid_initialize.when.called.should.have.raised(
        ExtensionDefinitionError,
        'extension tests.unit.extensions.test_core.Tybalt.initialize must be a callable'
    )

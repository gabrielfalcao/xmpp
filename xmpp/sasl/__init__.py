# -*- coding: utf-8 -*-
#
# (C) Copyright 2016 Gabriel Falcao <gabriel@nacaolivre.org>
# (C) Copyright 2003-2011 Jacek Konieczny <jajcus@jajcus.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License Version
# 2.1 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
"""SASL authentication implementaion for PyXMPP.

Normative reference:
  - `RFC 4422 <http://www.ietf.org/rfc/rfc4422.txt>`__
"""

from __future__ import division


import logging

from xmpp.sasl.core import Reply, Response, Challenge, Success, Failure
from xmpp.sasl.core import PasswordDatabase
from xmpp.sasl.core import CLIENT_MECHANISMS, SECURE_CLIENT_MECHANISMS
from xmpp.sasl.core import SERVER_MECHANISMS, SECURE_SERVER_MECHANISMS
from xmpp.sasl.core import CLIENT_MECHANISMS_D, SERVER_MECHANISMS_D

from xmpp.sasl import plain
from xmpp.sasl import external
from xmpp.sasl import scram


__all__ = [
    'filter_mechanism_list',
    'server_authenticator_factory',
    'client_authenticator_factory',
    'scram',
    'external',
    'plain',
    'Success',
    'Failure',
    'Challenge',
    'Response',
    'Reply',
    'PasswordDatabase',
    'CLIENT_MECHANISMS',
    'CLIENT_MECHANISMS_D',
    'SECURE_CLIENT_MECHANISMS',
    'SERVER_MECHANISMS',
    'SERVER_MECHANISMS_D',
    'SECURE_SERVER_MECHANISMS',
]


logger = logging.getLogger("xmpp.sasl")


def get_client_mechanisms():
    return CLIENT_MECHANISMS_D.keys()


def get_server_mechanisms():
    return SERVER_MECHANISMS_D.keys()


def client_authenticator_factory(mechanism):
    """Create a client authenticator object for given SASL mechanism.

    :Parameters:
        - `mechanism`: name of the SASL mechanism ("PLAIN", "DIGEST-MD5" or
          "GSSAPI").
    :Types:
        - `mechanism`: `unicode`

    :raises `KeyError`: if no client authenticator is available for this
              mechanism

    :return: new authenticator.
    :returntype: `sasl.core.ClientAuthenticator`"""
    authenticator = CLIENT_MECHANISMS_D[mechanism]
    return authenticator()


def server_authenticator_factory(mechanism, password_database):
    """Create a server authenticator object for given SASL mechanism and
    password databaser.

    :Parameters:
        - `mechanism`: name of the SASL mechanism ("PLAIN", "DIGEST-MD5" or "GSSAPI").
        - `password_database`: name of the password database object to be used
          for authentication credentials verification.
    :Types:
        - `mechanism`: `str`
        - `password_database`: `PasswordDatabase`

    :raises `KeyError`: if no server authenticator is available for this
              mechanism

    :return: new authenticator.
    :returntype: `sasl.core.ServerAuthenticator`"""
    authenticator = SERVER_MECHANISMS_D[mechanism]
    return authenticator(password_database)


def filter_mechanism_list(mechanisms, properties, allow_insecure=False,
                          server_side=False):
    """Filter a mechanisms list only to include those mechanisms that cans
    succeed with the provided properties and are secure enough.

    :Parameters:
        - `mechanisms`: list of the mechanisms names
        - `properties`: available authentication properties
        - `allow_insecure`: allow insecure mechanisms
    :Types:
        - `mechanisms`: sequence of `unicode`
        - `properties`: mapping
        - `allow_insecure`: `bool`

    :returntype: `list` of `unicode`
    """

    result = []
    for mechanism in mechanisms:
        mechanism = mechanism.upper()
        try:
            if server_side:
                klass = SERVER_MECHANISMS_D[mechanism]
            else:
                klass = CLIENT_MECHANISMS_D[mechanism]
        except KeyError:
            continue
        secure = properties.get("security-layer")
        if not allow_insecure and not klass._pyxmpp_sasl_secure and not secure:
            continue
        if not klass.are_properties_sufficient(properties):
            continue

        result.append(mechanism)
    return result

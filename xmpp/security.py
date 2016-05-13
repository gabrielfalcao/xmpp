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

from datetime import datetime
from pyasn1.codec.der import decoder
from pyasn1.type.univ import OctetString
from pyasn1.type.univ import ObjectIdentifier
from pyasn1.type.char import BMPString, IA5String, UTF8String
from pyasn1.type.useful import GeneralizedTime
from pyasn1_modules.rfc2459 import (
    Certificate,
    DirectoryString,
    SubjectAltName,
    # GeneralNames,
    # GeneralName,
)
from pyasn1_modules.rfc2459 import id_ce_subjectAltName as SUBJECT_ALT_NAME
from pyasn1_modules.rfc2459 import id_at_commonName as COMMON_NAME

XMPP_ADDR = ObjectIdentifier('1.3.6.1.5.5.7.8.5')
SRV_NAME = ObjectIdentifier('1.3.6.1.5.5.7.8.7')


class CertificateError(Exception):
    pass


def decode_str(data):
    encoding = 'utf-16-be' if isinstance(data, BMPString) else 'utf-8'
    return bytes(data).decode(encoding)


def extract_names(raw_cert):
    results = {'CN': set(),
               'DNS': set(),
               'SRV': set(),
               'URI': set(),
               'XMPPAddr': set()}

    cert = decoder.decode(raw_cert, asn1Spec=Certificate())[0]
    tbs = cert.getComponentByName('tbsCertificate')
    subject = tbs.getComponentByName('subject')
    extensions = tbs.getComponentByName('extensions') or []

    # Extract the CommonName(s) from the cert.
    for rdnss in subject:
        for rdns in rdnss:
            for name in rdns:
                oid = name.getComponentByName('type')
                value = name.getComponentByName('value')

                if oid != COMMON_NAME:
                    continue

                value = decoder.decode(value, asn1Spec=DirectoryString())[0]
                value = decode_str(value.getComponent())
                results['CN'].add(value)

    # Extract the Subject Alternate Names (DNS, SRV, URI, XMPPAddr)
    for extension in extensions:
        oid = extension.getComponentByName('extnID')
        if oid != SUBJECT_ALT_NAME:
            continue

        value = decoder.decode(extension.getComponentByName('extnValue'),
                               asn1Spec=OctetString())[0]
        sa_names = decoder.decode(value, asn1Spec=SubjectAltName())[0]
        for name in sa_names:
            name_type = name.getName()
            if name_type == 'dNSName':
                results['DNS'].add(decode_str(name.getComponent()))
            if name_type == 'uniformResourceIdentifier':
                value = decode_str(name.getComponent())
                if value.startswith('xmpp:'):
                    results['URI'].add(value[5:])
            elif name_type == 'otherName':
                name = name.getComponent()

                oid = name.getComponentByName('type-id')
                value = name.getComponentByName('value')

                if oid == XMPP_ADDR:
                    value = decoder.decode(value, asn1Spec=UTF8String())[0]
                    results['XMPPAddr'].add(decode_str(value))
                elif oid == SRV_NAME:
                    value = decoder.decode(value, asn1Spec=IA5String())[0]
                    results['SRV'].add(decode_str(value))

    return results


def extract_dates(raw_cert):
    cert = decoder.decode(raw_cert, asn1Spec=Certificate())[0]
    tbs = cert.getComponentByName('tbsCertificate')
    validity = tbs.getComponentByName('validity')

    not_before = validity.getComponentByName('notBefore')
    not_before = str(not_before.getComponent())

    not_after = validity.getComponentByName('notAfter')
    not_after = str(not_after.getComponent())

    if isinstance(not_before, GeneralizedTime):
        not_before = datetime.strptime(not_before, '%Y%m%d%H%M%SZ')
    else:
        not_before = datetime.strptime(not_before, '%y%m%d%H%M%SZ')

    if isinstance(not_after, GeneralizedTime):
        not_after = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
    else:
        not_after = datetime.strptime(not_after, '%y%m%d%H%M%SZ')

    return not_before, not_after


def get_ttl(raw_cert):
    not_before, not_after = extract_dates(raw_cert)
    if not_after is None:
        return None
    return not_after - datetime.utcnow()


def verify_certificate(expected, raw_cert):
    not_before, not_after = extract_dates(raw_cert)
    cert_names = extract_names(raw_cert)

    now = datetime.utcnow()

    if not_before > now:
        raise CertificateError(
            'Certificate has not entered its valid date range.')

    if not_after <= now:
        raise CertificateError(
            'Certificate has expired.')

    if '.' in expected:
        expected_wild = expected[expected.index('.'):]
    else:
        expected_wild = expected
    expected_srv = '_xmpp-client.%s' % expected

    for name in cert_names['XMPPAddr']:
        if name == expected:
            return True
    for name in cert_names['SRV']:
        if name == expected_srv or name == expected:
            return True
    for name in cert_names['DNS']:
        if name == expected:
            return True
        if name.startswith('*'):
            if '.' in name:
                name_wild = name[name.index('.'):]
            else:
                name_wild = name
            if expected_wild == name_wild:
                return True
    for name in cert_names['URI']:
        if name == expected:
            return True
    for name in cert_names['CN']:
        if name == expected:
            return True

    raise CertificateError(
        'Could not match certificate against hostname: %s' % expected)


def sasl_to_dict(data):
    return dict([x.split('=', 1) for x in data.split(',')])

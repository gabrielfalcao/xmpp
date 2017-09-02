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
from xmpp.security import extract_names, extract_dates, pem_to_der


# dummy self-signed
KEY = pem_to_der("""
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA9aio6AsZUR43jnSrFCnmth+Bhnh1g1QzpzCd7w5y0kNhO4Ms
ieSrSjWrX8K3VU3LIBX8B/U+uvONIANPm/b//1/F9RKqKPu3vo/KgjrhYjzcibR2
2xMUhSj3m9cYML0VSIb97QWOloVgRsDp2f9cZoBPu3T1+zpJUXE0JUIeOjujPkQW
Kk6J26eF0eW2TdNI2zpF0/wmrTKQ1MFXuqzxbBDU0PCa2BrxMTeNZIHeaRIxhFTj
+CoruhLSYacT9kO6rsPchp93CqAcnjELG4SgxWosyVw4GNoLf8woUggfKV9Td+ts
SSnsXnhq3CQA/mafhiWj4J0E5Wv36cDvZsafhQIDAQABAoIBAQCWL+YL73Ur7cBj
fJp3OmLNp5dlodGeV+U4avWziG7Uc9NHMhwRtdavCP7cDcxN/8CWvjoWl24hl/MI
xl1uaeT6uQ/qk92qLrKYc4qIcf0HNVRTcBxWNWUPQAuZoDgu2/reG4G03ffduG8y
8pBF8eQI2ptkbM5SKMFYZFBQEwst58NsTrO6/XZY++C0AWZASGqfTfL2nBsqlF5o
rW7YEvL6DyabjXOUgCGRnRjAaBBUrdSgO9k8S2tj2F38c+wx9b0BID9YDjSqaK5x
f6hV/aG+ksUduhO/sUEjXTLnJkmWG93LsvdEGqQzPYBQ3JI/KJvplJNkzWLtYd0j
RROJ7ClFAoGBAP5KmLt/zjCpd477E/EpJ4DPn7rWBmtZplbC4KTtudYfyW+dCVVh
0lZvE1TLxOJ/F2DULfWdatoGjS+ptztIL7Dbz69ueohr3XiMJ4KiXvbs/hFpTGkh
1p1QvuDPYWtpjXgrnSqKPNkoZ08Hb9Ww5s/3Cnoq0OB8hNzXuOdUe/AHAoGBAPdP
NuPJ6PBm/lPoCbTt4onPF+fYGLIGil+/SmmVFt4BYFddjGiFOuLh5F014lmvWbuO
6xX+JkJW9jj2yFman4/Ls0oyFNBOLsL0hkDVEFMsWu86eOcposLrzWdgwTaJIyKw
P6UMPlnyp77iKQ3k/y/3RithuNkoeXMErSbAu/kTAoGAQG/ougKN3jjjSgEHsaGr
F/IE2NRpNgS2qN+jC0gOQls1sSnK9q7eHPbyoBcuofJwmyHJL6cfL3ZfiodoHgaR
xzA8NYk6VZ13tpdVX74DcHDnhMP5D976Qkz2wYLrfct2hNAQeHolJyYc36LTzQOR
yXshVYnJ+kizZj7n5P68lTsCgYBVXbSWwHV1tjeIAwqGt66A30ljMAamPPe6wS8Q
bvQrwdHdll8HHSYMduj6+8ScLJkO0vB28PmH4LixRQ43T9ZQLoI+1Da3CKW/ieRl
sKYn76Gb/lUJhie2nOqUCqPnDUNhj/EIKcfECKy6iRqevzMO/Y3tH5hM7VmuyCh0
vgaknQKBgGEY8KHhiYKVMRP0BNOkPiSNhB5x5Zr8W1Ku7BfbSWkenzhiGrjEmCz3
cfD303K524aPfeshuJkJUvo+1VFhX47yNLkChLwZJHmQGeyGz3VEiChGpVTTDEd0
MaRwmcsZB4zsJa9FaC3l1gBv9Qfp6XMXyQvyYbQ+jf3rbm3KV+tW
-----END RSA PRIVATE KEY-----

""")


# def test_extract_dates():
#     ('xmpp.security.extract_dates() should return the "not before" '
#      'and "not after" from the raw PEM certificate')

#     extract_dates(KEY).should.equal((None,))


# def test_extract_names():
#     ('xmpp.security.extract_names() should return a dict ')

#     extract_names(KEY).should.equal({})

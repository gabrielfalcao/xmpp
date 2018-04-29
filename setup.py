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
import io
import os
from setuptools import setup, find_packages


def read_version():
    ctx = {}
    exec(local_file('xmpp', 'version.py'), ctx)
    return ctx['version']


local_file = lambda *f: \
    io.open(os.path.join(os.path.dirname(__file__), *f), encoding='utf-8').read()


dependencies = list(filter(bool, local_file('requirements.txt').splitlines()))


setup(
    name='xmpp',
    version=read_version(),
    entry_points={
        'console_scripts': ['xmpp = xmpp.cli.main:entrypoint'],
    },
    description='stateless and concurrency-agnostic XMPP library for python',
    long_description=local_file('README.rst'),
    author=u'Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='https://github.com/gabrielfalcao/xmpp',
    packages=find_packages(exclude=['*tests*']),
    install_requires=dependencies,
    include_package_data=True,
    license='LGPLv3',
    package_data={
        'xmpp': 'COPYING requirements.txt *.rst docs/source/*'.split(),
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Conferencing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)

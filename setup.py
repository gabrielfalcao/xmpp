#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
from setuptools import setup, find_packages


local_file = lambda *f: \
    open(os.path.join(os.path.dirname(__file__), *f)).read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('xmpp', 'version.py')))
    return finder.version


dependencies = filter(bool, local_file('requirements.txt').splitlines())


setup(
    name='xmpp',
    version=read_version(),
    entry_points={
        'console_scripts': ['xmpp = xmpp.cli.main:entrypoint'],
    },
    description='minimalistic XMPP client that is agnostic of concurrency framework and stateless',
    author=u'Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='https://falcao.it',

    # find all modules with __init__.py, except the test ones. The
    # reason for not distributing tests with the binary is to avoid
    # any accidents with the dangerous things that could happen if the
    # test files are imported in production servers by any chance :)

    packages=find_packages(exclude=['*tests*']),
    install_requires=dependencies,

    # By setting this flag to true, setuptools will read the
    # MANIFEST.in file in the same path as this very setup.py that you
    # read, then include any data files (i.e: not *.py)
    include_package_data=True,
    # Python allows you to import modules that are compressed in a zip
    # file.  In the other hand, setuptools is a very very naughty boy
    # and always tries to optimize the final build size for you.
    #
    # With that said, let's explicitly tell it NOT to build the
    # xmpp module as a xmpp.zip file, simply
    # because that generates all sorts of nightmare
    # (i.e. it obfuscates the traceback in the logs when something goes wrong, making the life of the devops team worse)
    zip_safe=False,
)

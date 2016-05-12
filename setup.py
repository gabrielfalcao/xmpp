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
    description='stateless and concurrency-agnostic XMPP library for python',
    author=u'Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='https://github.com/gabrielfalcao/xmpp',
    packages=find_packages(exclude=['*tests*']),
    install_requires=dependencies,
    include_package_data=True,
    zip_safe=False,
)

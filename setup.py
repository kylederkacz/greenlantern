#!/usr/bin/env python

from setuptools import setup
from os.path import join, dirname

try:
    long_description = open(join(dirname(__file__), 'README.md')).read()
except Exception:
    long_description = None

setup(
    name='greenlantern',
    version='0.0.1',
    description='A python based template extract library',
    author='Kyle Derkacz',
    author_email='kyle@kylederkacz.com',
    url='http://github.com/kylederkacz/greenlantern',

    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=['greenlantern'],
    provides=['greenlantern'],
    requires=[],
    install_requires=[],
)

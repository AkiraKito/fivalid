# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = __import__('fivalid').__version__

setup(
    name='fivalid',
    version=version,
    license='BSD',
    author='Akira Kito',
    description='Lightweight field data validator.',
    long_description=open('README.rst').read(),
    packages=['fivalid'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    platforms='any'
)


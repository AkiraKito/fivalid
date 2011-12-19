# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='fivalid',
    version='0.1.1',
    license='BSD',
    author='Akira Kito',
    description='Lightweight field value validator.',
    long_description=open('README.rst').read(),
    packages=['fivalid'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    platforms='any'
)

#!/usr/bin/env python

from distutils.core import setup

setup(name='Distutils',
    version='1.0',
    description='Algorithmic trading in Python.',
    author='Anthony Krivonos',
    author_email='info@anthonykrivonos.com',
    url='https://github.com/anthonykrivonos/Quantico',
    packages=['python-dotenv', 'numpy', 'mpl_finance', 'pandas_market_calendars']
)

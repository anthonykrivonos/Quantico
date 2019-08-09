# Anthony Krivonos
# Oct 29, 2018
# setup.py

from distutils.core import setup

# Abstract: Setup script for packaging.

setup(
    name='Quantico',
    version='1.0',
    description='Algorithmic trading in Python.',
    author='Anthony Krivonos',
    author_email='info@anthonykrivonos.com',
    url='https://github.com/anthonykrivonos/Quantico',
    packages=[
        'python-dotenv',
        'termcolor',
        'textblob',
        'mpl_finance',
        'pandas',
        'pandas_market_calendars',
        'scipy',
        'git+https://github.com/Jamonek/Robinhood.git'
    ]
)

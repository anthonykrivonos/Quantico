# Anthony Krivonos
# Oct 29, 2018
# tests/tests.py

# Abstract: File with platform tests.

# Global Imports
import sys
import os
sys.path.append('src')

# Start .env
from os.path import join, dirname
from dotenv import Dotenv
dotenv = Dotenv(join(dirname(__file__)+"/../", '.env'))
os.environ.update(dotenv)
# End .env

# Local Imports
from query import *
from utility import *
from nodaytrades import *

# Plotting
import numpy as np

# Query Tests
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Helper

# Initialize Query object with credentials from .env
query = Query(EMAIL, PASSWORD)

# Plotting Test

# historicals = query.get_history("CRMD")
# Utility.plot_historicals(historicals, is_candlestick_chart=True)

# print(query.user_stock_portfolio())

# NoDayTradesAlgorithm(query)

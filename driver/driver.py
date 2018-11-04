# Anthony Krivonos
# Oct 29, 2018
# driver/driver.py

# Abstract: Main script to run algorithms from.

# Global Imports
import sys
import os
sys.path.append('src')

# Start .env
from os.path import join, dirname
from dotenv import load_dotenv
dotenv = load_dotenv(join(dirname(__file__)+"/../", '.env'))
# End .env

# Local Imports
from query import *
from utility import *

from algorithms import *

# Plotting
import numpy as np

# Query Tests
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Initialize Query object with credentials from .env
query = Query(EMAIL, PASSWORD)

TopMoversNoDayTradesAlgorithm(query)

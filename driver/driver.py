# Anthony Krivonos
# Oct 29, 2018
# driver/driver.py

# Global Imports
import sys
import os
import numpy as np
from os.path import join, dirname
from dotenv import load_dotenv
sys.path.append('src')

# Local Imports
from query import *
from utility import *
from enums import *
from algorithms import *
from models import *

# Plotting
import numpy as np

# Abstract: Main script to run algorithms from.

#
#   Driver
#
# Load EMAIL and PASSWORD constants from .env
dotenv = load_dotenv(join(dirname(__file__)+"/../", '.env'))
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Login and intialize query object with credentials from .env
query = None
try:
    query = Query(EMAIL, PASSWORD)
except Exception as e:
    Utility.error("Could not log in: " + str(e))
    sys.exit()

my_port = query.user_portfolio()
# their_port = Portfolio(query, [Quote("AAPL", 0), Quote("GOOG", 0)], "Cool Port")

# Run algorithm
NoDayTradesAlgorithm(query, my_port)

# history = my_port.get_history()
# print(my_port.get_market_data_tuple())
# print(history)

# print(my_port.sharpe_optimization())

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

from algorithms import *

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

# Run algorithm
TopMoversNoDayTradesAlgorithm(query)

# Test compiling today's orders
# todays_orders =  list(map(lambda order: order['instrument'], ))
# todays_orders = [ order for order in (query.user_orders()['results'] or []) if Utility.iso_to_datetime(order['last_transaction_at']) ]
# print(todays_orders)

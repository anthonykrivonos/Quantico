# Anthony Krivonos
# Oct 29, 2018
# tests/tests.py

# Abstract: File with platform tests.

# Imports
import sys
import os
sys.path.append('src')

# Start .env
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__)+"/../", '.env')
load_dotenv(dotenv_path)
# End .env

from query import *

# Query Tests
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Initialize Query object with credentials from .env
query = Query(USERNAME, PASSWORD)

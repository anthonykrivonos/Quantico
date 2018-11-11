# Anthony Krivonos
# Nov 9th, 2018
# src/models/quote.py

# Imports
import sys

# Abstract: Simple model that maps symbols to quantities.

class Quote:

    def __init__(self, symbol, count = 0, weight = 0.0):

        # Set properties
        self.symbol = symbol
        self.count = count
        self.weight = weight

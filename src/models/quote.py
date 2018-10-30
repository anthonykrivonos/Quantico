# Anthony Krivonos
# Oct 29, 2018
# src/models/quote.py

# Abstract: Model for quote objects returned from the API.

# Imports
import sys

# Factory Methods
class Factory:

    # Converts a quote object into a model
    @staticmethod
    def convert(quote):

# Anthony Krivonos
# Nov 9th, 2018
# src/models/price.py

# Imports
import sys

# Pandas
import pandas as pd

# NumPy
import numpy as np

# Enums
from enums import *

# Math
from math import exp

# Abstract: Model that stores an instantaneous price.

class Price:

    def __init__(self, time, open, close, high, low):

        # Set properties
        self.time = time
        self.open = open
        self.close = close
        self.high = high
        self.low = low

    @staticmethod
    def props_as_array():
        return ['time', 'open', 'close', 'high', 'low']

    def __str__(self):
        return str(self.as_dict())

    def as_tuple(self):
        return (self.time, self.open, self.close, self.high, self.low)

    def as_dict(self):
        props = np.array(self.props_as_array())
        vals = np.array(self.values_as_array())
        count = len(props)
        dict = {}
        for i, prop in enumerate(props):
            dict[prop] = vals[i]
        return dict

    def values_as_array(self):
        return [self.time, self.open, self.close, self.high, self.low]

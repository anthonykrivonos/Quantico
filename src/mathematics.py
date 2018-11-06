# Anthony Krivonos
# Oct 29, 2018
# src/factory.py

# Imports
import sys

# Pandas
import pandas as pd

# NumPy
import numpy as np

# Enums
from enums import *

# Abstract: Math functions for dataset analysis.

# Math Methods
class Math:

    # poly:[float]
    # param x:float => List of x values.
    # param y:float => List of y values.
    # returns A list of length |deg| for coefficients of the polynomial.
    @staticmethod
    def poly(x, y, degree):
        x = np.array(x)
        y = np.array(y)
        return np.polyfit(x, y, degree)

    # deriv:[float]
    # param poly:[float] => A list of length |deg| for coefficients of the polynomial.
    # param order:integer => Order of the differentiation.
    # returns A list of length |deg| for coefficients of the differentiated polynomial.
    @staticmethod
    def deriv(poly, order):
        while order > 0:
            poly = np.polyder(poly)
            order -= 1
        return poly

    # eval:float
    # param poly:[float] => A list of length |deg| for coefficients of the polynomial.
    # param x:float => Value to evaluate the polynomial at.
    # returns The value of the polynomial at the given x.
    @staticmethod
    def eval(poly, x):
        return np.polyval(poly, x)

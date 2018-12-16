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

# Math
from math import exp

# Warnings
import warnings

# Abstract: Math functions for dataset analysis.

# Math Methods
class Math:

    # poly:[float]
    # param x:float => List of x values.
    # param y:float => List of y values.
    # returns A list of length |deg| for coefficients of the polynomial.
    @staticmethod
    def poly(x, y, degree):
        warnings.filterwarnings("error")
        while degree > 0:
            try:
                x = np.array(x)
                y = np.array(y)
                return np.polyfit(x, y, degree)
            except:
                degree -= 1
        return np.polyfit(x, y, 0)

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

    # get_discrete_present_value:Float
    # param price:Float => Current asset price.
    # param years:Int => Number of years from now.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the future value of the price, accounting for inflation.
    @staticmethod
    def get_discrete_present_value(price, years, rate = 0.025):
        return price * (1 + rate) ** years

    # get_discrete_future_value:Float
    # param price:Float => Future asset price.
    # param years:Int => Number of years after this year.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the present value of the price, accounting for inflation.
    @staticmethod
    def get_discrete_future_value(price, years, rate = 0.025):
        return (1 + rate) ** -years

    # get_discrete_present_value:Float
    # param price:Float => Current asset price.
    # param years:Int => Number of years from now.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the future value of the price, accounting for inflation.
    @staticmethod
    def get_continuous_present_value(price, years, rate = 0.025):
        return price * exp(rate * years)

    # get_discrete_future_value:Float
    # param price:Float => Future asset price.
    # param years:Int => Number of years after this year.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the present value of the price, accounting for inflation.
    @staticmethod
    def get_continuous_future_value(price, years, rate = 0.025):
        return price * exp(-rate * years)

    # get_zero_coupon_bond_price:Float
    # param par:Float => Par value of the bond price.
    # param years:Int => Number of years after this year.
    # param rate:Float => The interest rate.
    # Returns the price of the bond in given year's time.
    @staticmethod
    def get_zero_coupon_bond_price(par, years, rate):
        return Math.get_discrete_present_value(par, years, rate)

    # get_zero_coupon_bond_price:Float
    # param par:Float => Coupon rate of the bond.
    # param par:Float => Par value of the bond price.
    # param years:Int => Number of years after this year.
    # param rate:Float => The interest rate.
    # Returns the price of the bond in given year's time.
    @staticmethod
    def get_bond_price(coupon, par, years, rate):
        return ((coupon * par) / rate)(1 - (1 / (1 + rate) ** years)) + Math.get_zero_coupon_bond_price(par, years, rate)

    # get_returns:Float
    # param cur_price:Float or [Float] => Current price(s) of the asset.
    # param prev_price:Float or [Float] => Previous price(s) of the asset (one unit of time ago).
    # Returns the expected returns of the stock(s).
    @staticmethod
    def get_returns(cur_price, prev_price):
        return np.log(cur_price/prev_price)

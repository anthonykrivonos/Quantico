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
from sympy import *
from mpmath import *

# Warnings
import warnings

# Abstract: Math functions for dataset analysis.

# Configure mpmath
EPSILON = 20
mp.dps = EPSILON
mp.pretty = False

# Math Methods
class Math:

    ##
    #
    #   Polynomial Mathematics
    #
    ##

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
                degree = int(Math.p_sub(degree, 1))
        return np.polyfit(x, y, 0)

    # deriv:[float]
    # param poly:[float] => A list of length |deg| for coefficients of the polynomial.
    # param order:integer => Order of the differentiation.
    # returns A list of length |deg| for coefficients of the differentiated polynomial.
    @staticmethod
    def deriv(poly, order):
        while order > 0:
            poly = np.polyder(poly)
            order = int(Math.p_sub(order, 1))
        return poly

    # eval:float
    # param poly:[float] => A list of length |deg| for coefficients of the polynomial.
    # param x:float => Value to evaluate the polynomial at.
    # returns The value of the polynomial at the given x.
    @staticmethod
    def eval(poly, x):
        ev = np.polyval(poly, x)
        if isinstance(ev, list):
            ev = 0
        return ev

    ##
    #
    #   Portfolio Mathematics
    #
    ##

    # get_discrete_present_value:Float
    # param price:Float => Current asset price.
    # param years:Int => Number of years from now.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the future value of the price, accounting for inflation.
    @staticmethod
    def get_discrete_present_value(price, years, rate = 0.025):
        return Math.p_mul(price, Math.p_exp(Math.p_add(1, rate), years))

    # get_discrete_future_value:Float
    # param price:Float => Future asset price.
    # param years:Int => Number of years after this year.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the present value of the price, accounting for inflation.
    @staticmethod
    def get_discrete_future_value(price, years, rate = 0.025):
        return Math.p_exp(Math.p_add(1, rate), -years)

    # get_discrete_present_value:Float
    # param price:Float => Current asset price.
    # param years:Int => Number of years from now.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the future value of the price, accounting for inflation.
    @staticmethod
    def get_continuous_present_value(price, years, rate = 0.025):
        return Math.p_mul(price, exp(Math.p_mul(rate, years)))

    # get_discrete_future_value:Float
    # param price:Float => Future asset price.
    # param years:Int => Number of years after this year.
    # param rate:Float => The interest rate. (defaults to 0.025)
    # Returns the present value of the price, accounting for inflation.
    @staticmethod
    def get_continuous_future_value(price, years, rate = 0.025):
        return Math.p_mul(price, exp(Math.p_mul(-rate, years)))

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
        return Math.p_add(Math.p_mul(Math.p_div(Math.p_mul(coupon, par), rate), Math.p_sub(1, Math.p_div(1, Math.p_exp(Math.p_add(1, rate), years)))), Math.get_zero_coupon_bond_price(par, years, rate))

    # get_returns:Float
    # param cur_price:Float or [Float] => Current price(s) of the asset.
    # param prev_price:Float or [Float] => Previous price(s) of the asset (one unit of time ago).
    # Returns the expected returns of the stock(s).
    @staticmethod
    def get_returns(cur_price, prev_price):
        return np.log(cur_price/prev_price)

    # get_returns:Float
    # param cur_price:Float or [Float] => Current price(s) of the asset.
    # param prev_price:Float or [Float] => Previous price(s) of the asset (one unit of time ago).
    # Returns the expected returns of the stock(s).
    @staticmethod
    def get_returns(cur_price, prev_price):
        return np.log(cur_price/prev_price)

    ##
    #
    #   Precision Arithmetic
    #
    ##

    # __mp_to_float:Float
    # param n:mpf => MPMath floating point number.
    # Returns a precise float conversion from an mpf float.
    def __mp_to_float(n):
        return Float(str(n), EPSILON)

    # p_mul:Float
    # param a:Float => First number to multiply.
    # param b:Float => Second number to multiply.
    # Returns a precise multiplication of the two numbers.
    @staticmethod
    def p_mul(a, b):
        m = fmul(a, b)
        return Math.__mp_to_float(m)

    # p_exp:Float
    # param a:Float => Base number.
    # param b:Float => Exponent number.
    # Returns a precise exponentiation of a^b.
    @staticmethod
    def p_exp(a, b):
        m = mpmathify(a)
        while b > 1:
            m = fmul(m, m)
            b -= 1
        return Math.__mp_to_float(m)

    # p_div:Float
    # param a:Float => First number to divide.
    # param b:Float => Second number to divide.
    # Returns a precise division of the two numbers.
    @staticmethod
    def p_div(a, b):
        m = fdiv(a, b)
        return Math.__mp_to_float(m)

    # p_add:Float
    # param a:Float => First number to add.
    # param b:Float => Second number to add.
    # Returns a precise addition of the two numbers.
    @staticmethod
    def p_add(a, b):
        m = fadd(a, b)
        return Math.__mp_to_float(m)

    # p_sub:Float
    # param a:Float => First number to subtract.
    # param b:Float => Second number to subtract.
    # Returns a precise subtraction of the two numbers.
    @staticmethod
    def p_sub(a, b):
        m = fsub(a, b)
        return Math.__mp_to_float(m)

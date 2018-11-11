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

# PriceModel
from models.price import *

# Abstract: Model storing stock info and historical prices.

class Portfolio:

    def __init__(self, query, quotes):

        # Set properties
        self.query = query
        self.quotes = quotes
        self.total_assets = 0

        # Update quantities
        self.update()

        # Set Pandas properties
        pd.options.display.max_columns = 3000
        pd.options.display.max_rows = 3000

    ##
    #
    #   MARK: - UPDATERS
    #
    ##

    def update(self):
        self.total_assets = 0
        for quote in self.quotes:
            self.total_assets += quote.count
        if self.total_assets > 0:
            for quote in self.quotes:
                quote.weight = quote.count / self.total_assets
        else:
            for quote in self.quotes:
                quote.weight = 0.0

    ##
    #
    #   MARK: - GETTERS
    #
    ##

    # get_history_data:DataFrame
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns Pandas data frame with Price properties mapped by time.
    def get_history_data(self, symbol, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        history = np.array(list(map(lambda price: price.values_as_array(), self.get_history(symbol, interval, span, bounds))))
        return pd.DataFrame(history, columns=Price.props_as_array(), index=None)

    # get_history:[Price]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns List of Price models with the time, volume, open, close, high, low for each time in the interval.
    def get_history(self, symbol, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        historicals = self.query.get_history(symbol, interval, span, bounds)['historicals']
        historicals = list(map(lambda h: Price(h['begins_at'], h['volume'], h['open_price'], h['close_price'], h['high_price'], h['low_price']), historicals))
        return historicals

# Anthony Krivonos
# Oct 29, 2018
# src/alg/nodaytrades.py

# Global Imports
import numpy as np
import math

# Local Imports
from utility import *
from enums import *
from mathematics import *

# PriceModel
from models.price import *

from algorithms.__algorithm import *

# Abstract: Algorithm that sells rapidly when stocks perform below a threshold.

class ShortIntensiveAlgorithm(Algorithm):

    # __init__:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    # param
    def __init__(self, query, portfolio, sec_interval = 900):

        # Initialize properties

        # Set to True if buys and sells should not go through
        self.debug = False

        # Range of prices for stock purchasing
        self.buy_range = (6.00, 40.00)

        # Percentage threshold for buying and selling
        self.threshold = 0.05

        # List of categories for stocks to be traded
        self.categories = [ Tag.TOP_MOVERS, Tag.MOST_POPULAR, Tag.INVESTMENT_OR_TRUST ]

        # List of stock symbols to trade
        self.symbols = []

        # Map of symbols to lists of Price models
        self.stock_data = {}

        # Map of symbols to first derivatives (rate of change)
        self.stock_delta1 = {}

        # Map of symbols to second derivatives (concavity)
        self.stock_delta2 = {}

        # Map of symbols for percentage change
        self.stock_delta_perc = {}

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "No Day Trades", buy_range = self.buy_range, debug = self.debug)

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):
        Algorithm.initialize(self)

        # Get all fundamentals within the buy range
        unsorted_fundamentals = self.query.get_fundamentals_by_criteria(self.buy_range, self.categories)

        # Store the symbols of each candidate fundamental into a separate array
        self.symbols = sorted([ fund['symbol'] for fund in unsorted_fundamentals ])

        for symbol in self.symbols:
            self.stock_data[symbol] = []
            self.stock_delta1[symbol] = 0
            self.stock_delta2[symbol] = 0
            self.stock_delta_perc[symbol] = 0

        self.update_stock_data()

        pass

    #
    # Event Functions
    #

    # on_market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self):
        Algorithm.on_market_will_open(self)
        pass

    # on_market_open:Void
    # NOTE: Called exactly when the market opens.
    def on_market_open(self):
        Algorithm.on_market_open(self)
        pass

    # while_market_open:Void
    # NOTE: Called on an interval while market is open.
    def while_market_open(self):
        Algorithm.while_market_open(self)

        self.update_stock_data()
        self.perform_buy_sell()

        pass

    # on_market_close:Void
    # NOTE: Called exactly when the market closes.
    def on_market_close(self):
        Algorithm.on_market_close(self)

        Algorithm.cancel_open_orders(self)

        pass

    #
    # Algorithm
    #

    # update_stock_data:Void
    def update_stock_data(self):

        for symbol in self.stock_data:

            # Get current price of the stock
            current_price = self.query.get_current_price(quote.symbol)

            # Append current price to list
            self.stock_data[symbol].append(Price(self.utility.now_datetime64(), current_price, current_price, current_price, current_price))

            # Turn stock data into polynomial
            t = y = []
            for price in self.stock_data[symbol]:
                t.append(price.time)
                y.append(price.open)

            # Get polynomial for symbol
            try:
                symbol_poly = Math.poly(t, y, 3)
            except:
                symbol_poly = Math.poly(t, y, 2)

            # First derivative
            self.stock_delta1[symbol] = Math.eval(Math.deriv(symbol_poly, 1))
            self.stock_delta_perc[symbol] = self.stock_delta1[symbol]/y[-1]

            # Second derivative
            self.stock_delta2[symbol] = Math.eval(Math.deriv(symbol_poly, 2))

        pass

    # perform_buy_sell:Void
    def perform_buy_sell(self):

        Algorithm.log(self, "Executing perform_buy_sell:")

        port = self.portfolio.get_quotes()
        symbols_in_port = [ quote.symbol for quote in port ]

        for symbol in self.symbols:
            if self.stock_delta_perc[symbol] >= self.threshold/2:
                # Algorithm.buy(self, symbol, stock_shares, None, current_price)
            elif self.stock_delta_perc[symbol] <= -self.threshold:
                if self.portfolio.is_symbol_in_portfolio(symbol):
                    stock_shares = self.portfolio.get_quote_from_portfolio(symbol).count or 0
                    Algorithm.sell(self, symbol, stock_shares, None, current_price)

        Algorithm.log(self, "Finished run of perform_buy_sell")


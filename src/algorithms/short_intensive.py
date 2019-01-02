# Anthony Krivonos
# Oct 29, 2018
# src/algorithms/short_intensive.py

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
    def __init__(self, query, portfolio, sec_interval = 900, test = False, cash = 0.00):

        # Initialize properties

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
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "Short Intensive", buy_range = self.buy_range, test = test, cash = cash)

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):
        Algorithm.initialize(self)

        # Get all fundamentals within the buy range
        unsorted_fundamentals = self.query.get_fundamentals_by_criteria(self.buy_range, self.categories)

        # Store the symbols of each candidate fundamental into a separate array
        self.symbols = sorted([ fund['symbol'] for fund in unsorted_fundamentals ])

        # Append the user's owned symbols
        for quote in self.portfolio.get_quotes():
            self.symbols.append(quote.symbol)

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
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self, cash = None, prices = None):
        Algorithm.on_market_will_open(self, cash, prices)
        pass

    # on_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market opens.
    def on_market_open(self, cash = None, prices = None):
        Algorithm.on_market_open(self, cash, prices)
        pass

    # while_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called on an interval while market is open.
    def while_market_open(self, cash = None, prices = None):
        Algorithm.while_market_open(self, cash, prices)

        self.update_stock_data()
        self.perform_buy_sell()

        pass

    # on_market_close:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market closes.
    def on_market_close(self, cash = None, prices = None):
        Algorithm.on_market_close(self, cash, prices)

        Algorithm.cancel_open_orders(self)

        pass

    #
    # Algorithm
    #

    # update_stock_data:Void
    def update_stock_data(self):

        for symbol in self.stock_data:

            # Get current price of the stock
            current_price = self.price(symbol)

            # Append current price to list
            self.stock_data[symbol].append(Price(Utility.now_timestamp(), current_price, current_price, current_price, current_price))

            # Turn stock data into polynomial
            t = y = []
            for price in self.stock_data[symbol]:
                t.append(price.time)
                y.append(price.open)

            # Get polynomial for symbol
            try:
                symbol_poly = Math.poly(t, y, 2)
            except:
                symbol_poly = Math.poly(t, y, 1)

            # First derivative
            self.stock_delta1[symbol] = Math.eval(Math.deriv(symbol_poly, 1), t[-1])
            self.stock_delta_perc[symbol] = Math.p_div(self.stock_delta1[symbol], y[-1])

            # Second derivative
            self.stock_delta2[symbol] = Math.eval(Math.deriv(symbol_poly, 2), t[-1])

        Algorithm.log(self, "Rates of change:")
        Algorithm.log(self, self.stock_delta1)
        Algorithm.log(self, "Percentage change:")
        Algorithm.log(self, self.stock_delta_perc)
        Algorithm.log(self, "Concavity:")
        Algorithm.log(self, self.stock_delta2)

    # perform_buy_sell:Void
    def perform_buy_sell(self):

        Algorithm.log(self, "Executing perform_buy_sell:")

        port = self.portfolio.get_quotes()
        symbols_in_port = [ quote.symbol for quote in port ]

        for symbol in self.symbols:

            # Get stock's price
            current_price = self.price(symbol)

            if self.stock_delta_perc[symbol] >= self.threshold/2:
                # Buy if it reaches above half the buy threshold
                cash = self.cash
                spend_amount = min(cash, Math.p_mul(Math.p_mul(cash, self.stock_delta_perc[symbol]), 10))
                stock_shares = self.portfolio.get_quote_from_portfolio(symbol).count or 0
                stock_shares_to_buy = round(spend_amount/current_price)
                did_buy = Algorithm.buy(self, symbol, stock_shares_to_buy, None, current_price)
                if did_buy:
                    if symbol not in self.stock_data:
                        self.stock_data[symbol] = []
                        self.stock_delta1[symbol] = 0
                        self.stock_delta2[symbol] = 0
                        self.stock_delta_perc[symbol] = 0

            elif self.stock_delta_perc[symbol] <= -self.threshold:
                # Sell if it reaches below the short threshold
                if self.portfolio.is_symbol_in_portfolio(symbol):
                    stock_shares = self.portfolio.get_quote_from_portfolio(symbol).count or 0
                    did_sell = Algorithm.sell(self, symbol, stock_shares, None, current_price)

        Algorithm.log(self, "Finished run of perform_buy_sell")

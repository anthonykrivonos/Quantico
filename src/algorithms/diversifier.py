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
from algorithm import Algorithm

# Abstract: Algorithm employing a diversification tactic.

class DiversifierAlgorithm(Algorithm):

    # __init__:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    def __init__(self, query, portfolio, sec_interval = 900):

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "Diversifier")

        self.perform_buy_sell()

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):
        Algorithm.initialize(self)

        pass

    #
    # Event Functions
    #


    # on_market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self):
        Algorithm.on_market_will_open(self)

        self.perform_buy_sell()
        pass

    # on_market_open:Void
    # NOTE: Called exactly when the market opens. Cannot include a buy or sell.
    def on_market_open(self):
        Algorithm.on_market_open(self)

        self.perform_buy_sell()
        pass

    # on_market_close:Void
    # NOTE: Called exactly when the market closes.
    def on_market_close(self):
        Algorithm.on_market_close(self)

        self.perform_buy_sell()
        pass

    #
    # Algorithm
    #

    # perform_buy_sell:Void
    # NOTE: Algorithm works like this:
    #   - Assign "purchase propensities" depending on the following criteria:
    #   - ROUND 1: Concavity of price graph
    #   - ROUND 2: Most recent rate of change in the price graph
    #   - ROUND 3: Last closing price of the stock
    #   - Sell bottom 2/3 of performers
    #   - Buy top 1/3 of performers by ratio
    def perform_buy_sell(self):
        pass

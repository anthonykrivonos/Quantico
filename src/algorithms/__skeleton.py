# Anthony Krivonos
# src/algorithms/skeleton.py

# Global Imports
import numpy as np
import math

# Local Imports
from utility import *
from enums import *
from mathematics import *

# Local Model Imports
from models.portfolio import *
from models.price import *
from models.quote import *

# Parent Class Import
from algorithms.__algorithm import *

# Abstract: Thoroughly commented file used to describe how to write algorithms on Quantico.

class SkeletonAlgorithm(Algorithm):

    # __init__:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer? => Time interval in seconds for event handling.
    # param test:Boolean? => Set to True if backtesting, false otherwise.
    # param cash:Float? => Must set this amount (user's buying power) if backtesting. Otherwise, leave alone.
    def __init__(self, query, portfolio, sec_interval = 900, test = False, cash = 0.00):

        # Name the algorithm something creative
        algorithm_name = "Skeleton"

        # Set algorithm properties
        buy_range = (0.00, 20.00) # Lower and upper bounds for stocks to purchase (in this case, $0 to $20)

        # Set custom properties
        self.initialize_your_own_variables_here = True

        """
            NOTES:
            - Useful methods and properties available anywhere:
              - self.value(): Returns the current value of the user's portfolio.
              - self.price(symbol): Returns the current ask price of the string symbol.
              - self.cash: Stores the user's current cash, updated at each event call.
              - self.on_custom_timer(func, repeat_sec, start_d64, stop_d64): Calls a custom timer using datetime64 objects.
              - self.log(message, type): Logs messages both into the console and in the algorithm object.
              - self.get_logs(last): Get last # (or all, if none) of logs in the algorithm.
              - Algorithm.buy(symbol, quantity, stop, limit): Performs a stop/limit buy.
              - Algorithm.sell(symbol, quantity, stop, limit): Performs a stop/limit sell.
              - Algorithm.cancel(order_id): Cancels the order with the given ID.
              - Algorithm.cancel_open_orders(): Cancels all of the user's open orders.
            - Otherwise, access trading methods via the query property. (See query.py for all methods.)
        """

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = algorithm_name, buy_range = buy_range, test = test, cash = cash)

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):
        Algorithm.initialize(self)

        """
            NOTES:
            - This function is automatically called at the end of the parent class's constructor.
            - It will only be called once, so do long-term configurations here.
            - An example would be defining the types of stocks to buy and making a list of symbols.
        """

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

        """
            NOTES:
            - ALWAYS call the super method before running any other code.
            - NEVER access cash and prices. They are only necessary in backtesting.
            - This function is called an hour before markets open.
        """

        pass

    # on_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market opens.
    def on_market_open(self, cash = None, prices = None):
        Algorithm.on_market_open(self, cash, prices)

        """
            NOTES:
            - ALWAYS call the super method before running any other code.
            - NEVER access cash and prices. They are only necessary in backtesting.
            - This function is called precisely when markets open.
        """

        pass

    # while_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called on an interval while market is open.
    def while_market_open(self, cash = None, prices = None):
        Algorithm.while_market_open(self, cash, prices)

        """
            NOTES:
            - ALWAYS call the super method before running any other code.
            - NEVER access cash and prices. They are only necessary in backtesting.
            - This function is called repeatedly, on the provided sec_interval, between market open and close times.
        """

        pass

    # on_market_close:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market closes.
    def on_market_close(self, cash = None, prices = None):
        Algorithm.on_market_close(self, cash, prices)

        """
            NOTES:
            - ALWAYS call the super method before running any other code.
            - NEVER access cash and prices. They are only necessary in backtesting.
            - This function is called on market close.
        """

        pass

    #
    # Algorithm
    #

    """
        NOTES:
        - Define all algorithm-specific functions here.
    """
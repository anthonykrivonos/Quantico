# Anthony Krivonos
# Oct 29, 2018
# src/algorithm.py

# Global Imports
import numpy as np
import math

# Local Imports
from utility import *
from enums import *
from mathematics import *

# Abstract: Generic/abstract algorithm parent class.

class Algorithm:

    # initialize:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    # param name:String => Name of the algorithm.
    def __init__(self, query, portfolio, sec_interval = 900, name = "Algorithm"):

        Utility.log("Initialized Algorithm: \'" + name + "\'")

        # Initialize properties
        self.name = name
        self.query = query
        self.portfolio = portfolio
        self.sec_interval = sec_interval

        # Initialize the algorithm
        self.initialize()

    #
    # Event Functions
    #

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):

        # Actual upcoming open and close market hours
        market_hours = Utility.get_next_market_hours()
        self.pre_open_hour = market_hours[0] - datetime.timedelta(hours=1)
        self.open_hour = market_hours[0]
        self.close_hour = market_hours[1]

        Utility.log("Next Market Open:  " + str(self.open_hour))
        Utility.log("Next Market Close: " + str(self.close_hour))

        # Schedule event functions
        sec_interval = self.sec_interval
        Utility.sleep_then_execute(time=self.pre_open_hour, sec=sec_interval, action=lambda: self.market_will_open())
        Utility.execute_between_times(start_time=self.open_hour, stop_time=self.close_hour, sec=sec_interval, action=lambda: self.on_market_open())
        Utility.sleep_then_execute(time=self.close_hour, sec=sec_interval, action=lambda: self.on_market_close())

    # market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def market_will_open(self):
        Utility.log("Market will open.")
        pass

    # on_market_open:Void
    # NOTE: Called exactly when the market opens. Cannot include a buy or sell.
    def on_market_open(self):
        Utility.log("Market has opened.")
        pass

    # on_market_close:Void
    # NOTE: Called exactly when the market closes.
    def on_market_close(self):
        Utility.log("Market has closed.")
        # Run initialize to start trading next day
        self.initialize()
        pass

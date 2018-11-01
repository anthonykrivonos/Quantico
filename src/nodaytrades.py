# Anthony Krivonos
# Oct 29, 2018
# src/alg/nodaytrades.py

# Abstract: Algorithm employing the no-day-trades tactic.

import numpy as np #needed for NaN handling
import math #ceil and floor are useful for rounding

from utility import *

class NoDayTradesAlgorithm:

    def __init__(self, query):

        # NOTE: For now, the properties don't do anything, obviously.

        # Query
        self.query = query

        # Properties
        self.max_stocks = 100
        self.max_simultaneous_buys = 30
        self.min_price = 3.00
        self.max_price = 20.00
        self.super_sale_price = self.min_price
        self.super_sale_age = 6

        self.age = {}

        market_hours = Utility.get_next_market_hours()
        prior_hour = market_hours[0] - datetime.timedelta(hours=1)

        # Actual upcoming open and close market hours
        open_hour = market_hours[0]
        close_hour = market_hours[1]

        # Test times for event calls
        test_start = datetime.datetime.today() + datetime.timedelta(seconds=10)
        test_stop = datetime.datetime.today() + datetime.timedelta(seconds=20)

        # Execute event functions
        Utility.sleep_then_execute(time=test_start, sec=1, action=lambda: self.market_will_open())
        Utility.execute_between_times(start_time=test_start, stop_time=test_stop, sec=1, action=lambda: self.on_market_open())
        Utility.sleep_then_execute(time=test_stop, sec=1, action=lambda: self.on_market_close())

    #
    # Event Functions
    #

    # market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def market_will_open(self):
        print("Market will open.")
        pass

    # on_market_open:Void
    # NOTE: Called exactly when the market opens. Cannot include a buy or sell.
    def on_market_open(self):
        print("Market has opened.")
        pass

    # on_market_close:Void
    # NOTE: Called exactly when the market closes.
    def on_market_close(self):
        print("Market has closed.")
        pass


    #
    # Get Functions
    #

    def get_yesterdays_quotes(self):
        pass

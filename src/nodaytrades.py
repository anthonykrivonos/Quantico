# Anthony Krivonos
# Oct 29, 2018
# src/alg/nodaytrades.py

# Abstract: Algorithm employing the no-day-trades tactic.

import numpy as np #needed for NaN handling
import math #ceil and floor are useful for rounding

from utility import *

class NoDayTradesAlgorithm:

    def __init__(self, query):

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
        open_hour = market_hours[0]
        close_hour = market_hours[1]
        print(open_hour)
        print(close_hour)

        # Execute event functions
        Utility.sleep_then_execute(time=prior_hour, secInterval=60, action=lambda: self.market_will_open())
        Utility.execute_then_sleep(time=open_hour, secInterval=60, action=lambda: self.on_market_open())
        Utility.sleep_then_execute(time=close_hour, secInterval=60, action=lambda: self.on_market_close())

    def market_will_open():

        pass

    def on_market_open():

        pass

    def on_market_close():

        pass

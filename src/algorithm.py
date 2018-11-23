# Anthony Krivonos
# Oct 29, 2018
# src/algorithm.py

# Global Imports
import sys
import numpy as np
import math

# Local Imports
from utility import *
from enums import *
from mathematics import *

# QuoteModel
from models.quote import *

# Abstract: Generic/abstract algorithm parent class.

class Algorithm:

    # initialize:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    # param name:String => Name of the algorithm.
    def __init__(self, query, portfolio, sec_interval = 900, name = "Algorithm"):

        # Declare the start of a run
        Utility.log("Initialized Algorithm: \'" + name + "\'")

        # Initialize properties
        self.name = name                      # String name of the algorithm
        self.query = query                    # Query class for making API calls
        self.portfolio = portfolio            # The portfolio to call the algorithm on
        self.sec_interval = sec_interval      # Interval (in s) of event executions
        self.buy_list = []                    # List of stocks bought in the past day
        self.sell_list = []                   # List of stocks sold in the past day
        self.buy_range = (0.00, sys.maxsize)  # Range of prices for purchasing stocks

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

        # Indicate the market hours
        Utility.log("Next Market Open:  " + str(self.open_hour))
        Utility.log("Next Market Close: " + str(self.close_hour))

        # Schedule event functions
        sec_interval = self.sec_interval
        self.on_custom_timer(lambda: self.on_market_will_open(), start_d64 = self.pre_open_hour)
        self.on_custom_timer(lambda: self.on_market_open(), repeat_sec = sec_interval, start_d64 = self.open_hour, stop_d64 = self.close_hour)
        self.on_custom_timer(lambda: self.on_market_close(), start_d64 = self.close_hour)

        # Prevent day trading:

        # Refresh buy and sell lists
        self.buy_list = []
        self.sell_list = []

        # Update buy list and sell list with today's orders
        todays_orders = self.query.user_orders()['results'] or []
        todays_buys = []
        todays_sells = []
        for order in todays_orders:
            if order['side'] == Side.BUY.value:
                todays_buys.append(order)
            else:
                todays_sells.append(order)
        todays_buys = [ self.query.stock_from_instrument_url(order['instrument'])['symbol'] for order in todays_buys if Utility.iso_to_datetime(order['last_transaction_at']).date() == datetime.datetime.now().date() ]
        todays_sells = [ self.query.stock_from_instrument_url(order['instrument'])['symbol'] for order in todays_sells if Utility.iso_to_datetime(order['last_transaction_at']).date() == datetime.datetime.now().date() ]
        self.buy_list = todays_buys
        self.sell_list = todays_sells

        Utility.log('Today Bought: ' + str(self.buy_list))
        Utility.log('Today Sold  : ' + str(self.sell_list))

    # on_market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self):
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
        pass

    # on_custom_timer:Void
    # param func:Function => Function to call on the timer.
    # param repeat_sec:Integer => Number of seconds between each repeated function call. Leave None to prevent repetition of calls.
    # param start_d64:Datetime64? => Date to start the function calls.
    # param stop_d64:Datetime64? => Date to stop the function calls.
    # NOTE: - Starts a custom timer that fires with the given parameters.
    def on_custom_timer(self, func, repeat_sec = None, start_d64 = None, stop_d64 = None):
        if not repeat_sec:
            if start_d64 is None:
                func()
            else:
                Utility.sleep_then_execute(time=start_d64, sec=1, action=lambda: func())
        else:
            Utility.execute_between_times(action=lambda: func(), start_time=start_d64, stop_time=stop_d64, sec=repeat_sec)


    #
    # Execution Functions
    #

    # buy:Boolean
    # param symbol:String => String symbol of the instrument.
    # param quantity:Number => Number of shares to execute buy for.
    # param stop:Number? => Sets a stop price on the buy, if not None.
    # param limit:Number? => Sets a limit price on the buy, if not None.
    # NOTE: Safely executes a buy order outside of open hours, if possible.
    def buy(self, symbol, quantity, stop = None, limit = None):
        try:
            if limit <= self.buy_range[1] and limit >= self.buy_range[0] and symbol not in self.buy_list and symbol not in self.sell_list:
                self.query.exec_buy(symbol, quantity, stop, limit)
                self.buy_list.append(symbol)
                Utility.log("Bought " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                self.portfolio.add_quote(Quote(symbol, quantity))
                return True
            else:
                if limit > self.buy_range[1]:
                    Utility.error("Could not buy " + symbol + ": Stock too expensive")
                elif limit < self.buy_range[0]:
                    Utility.error("Could not buy " + symbol + ": Stock too cheap")
                elif symbol in self.buy_list:
                    Utility.error("Could not buy " + symbol + ": Stock already bought today")
                elif symbol in self.sell_list:
                    Utility.error("Could not buy " + symbol + ": Stock already sold today")
        except Exception as e:
            Utility.error("Could not buy " + symbol + ": " + str(e))
        return False


    # sell:Boolean
    # param symbol:String => String symbol of the instrument.
    # param quantity:Number => Number of shares to execute sell for.
    # param stop:Number? => Sets a stop price on the sell, if not None.
    # param limit:Number? => Sets a limit price on the sell, if not None.
    # NOTE: Safely executes a sell order outside of open hours, if possible.
    def sell(self, symbol, quantity, stop = None, limit = None):
        try:
            if symbol not in self.sell_list and symbol not in self.buy_list:
                self.query.exec_sell(symbol, quantity, stop, limit)
                self.sell_list.append(symbol)
                Utility.log("Sold " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                self.portfolio.remove_quote(Quote(symbol, quantity))
                return True
            else:
                if symbol in self.sell_list:
                    Utility.error("Could not sell " + symbol + ": Stock already sold today")
                elif symbol in self.buy_list:
                    Utility.error("Could not sell " + symbol + ": Stock already bought today")
        except Exception as e:
            Utility.error("Could not sell " + symbol + ": " + str(e))
        return False


    # cancel:Void
    # param order_id:String => ID of the order to cancel.
    # NOTE: Safely cancels an order given its ID, if possible.
    def cancel(self, order_id):
        try:
            self.query.exec_cancel(order_id)
            Utility.log("Cancelled order " + order_id)
            return True
        except:
            Utility.log("Could not cancel " + symbol + ": A client error occurred")
        return False

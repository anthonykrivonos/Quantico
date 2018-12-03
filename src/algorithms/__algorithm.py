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
# NOTE: All algorithms DO NOT perform day trades.

class Algorithm:

    # initialize:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    # param name:String => Name of the algorithm.
    def __init__(self, query, portfolio, sec_interval = 900, name = "Algorithm", buy_range = (0.00, sys.maxsize), debug = False):

        # Initialize properties
        self.name = name                      # String name of the algorithm
        self.query = query                    # Query class for making API calls
        self.portfolio = portfolio            # The portfolio to call the algorithm on
        self.sec_interval = sec_interval      # Interval (in s) of event executions
        self.buy_list = []                    # List of stocks bought in the past day
        self.sell_list = []                   # List of stocks sold in the past day
        self.buy_range = buy_range            # Range of prices for purchasing stocks
        self.debug = debug                    # Set to True if buys and sells should not go through
        self.logs = []                        # List of logged output

        # Declare the start of a run
        self.log("Initialized Algorithm: \'" + name + "\'")

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
        self.log("Next Market Open:  " + str(self.open_hour))
        self.log("Next Market Close: " + str(self.close_hour))

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

        self.log('Today Bought: ' + str(self.buy_list))
        self.log('Today Sold  : ' + str(self.sell_list))

    # on_market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self):
        self.log("Market will open.")
        pass

    # on_market_open:Void
    # NOTE: Called exactly when the market opens. Cannot include a buy or sell.
    def on_market_open(self):
        self.log("Market has opened.")
        pass

    # on_market_close:Void
    # NOTE: Called exactly when the market closes.
    def on_market_close(self):
        self.log("Market has closed.")
        pass

    # on_custom_timer:Void
    # param func:Function => Function to call on the timer.
    # param repeat_sec:Integer => Number of seconds between each repeated function call. Leave None to prevent repetition of calls.
    # param start_d64:Datetime64? => Date to start the function calls.
    # param stop_d64:Datetime64? => Date to stop the function calls.
    # NOTE: Starts a custom timer that fires with the given parameters.
    def on_custom_timer(self, func, repeat_sec = None, start_d64 = None, stop_d64 = None):
        if not repeat_sec:
            if start_d64 is None:
                func()
            else:
                Utility.sleep_then_execute(time=start_d64, sec=1, action=lambda: func())
        else:
            Utility.execute_between_times(action=lambda: func(), start_time=start_d64, stop_time=stop_d64, sec=repeat_sec)

    # log:Void
    # param message:String => The string message to log.
    # param type:String => The string representation of the type of message this is.
    # NOTE: Logs the output and adds it to the list of logs.
    def log(self, message, type = 'log'):
        if type == 'error' or type == 'w' or type == 'err':
            self.logs.append(Utility.error(message))
        elif type == 'warning' or type == 'w' or type == 'warn':
            self.logs.append(Utility.warning(message))
        else:
            self.logs.append(Utility.log(message))

    # get_logs:[String]
    # param last:Integer => Latest number of logs to output.
    # returns A list of logs
    def get_logs(self, last):
        count = -min(len(self.logs), last if last is not None else len(self.logs))
        return self.logs[count:]
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
                if not self.debug:
                    self.query.exec_buy(symbol, quantity, stop, limit)
                    self.log("Bought " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                else:
                    Utility.warning("Would have bought " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop) + " if not in 'debug' mode")
                self.buy_list.append(symbol)
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
                if not self.debug:
                    self.query.exec_sell(symbol, quantity, stop, limit)
                    self.log("Sold " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                else:
                    Utility.warning("Would have sold " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop) + " if not in 'debug' mode")
                self.sell_list.append(symbol)
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
            if not self.debug:
                self.query.exec_cancel(order_id)
                self.log("Cancelled order " + order_id)
            else:
                Utility.warning("Would have cancelled order " + order_id + " if not in 'debug' mode")
            return True
        except:
            Utility.error("Could not cancel " + symbol + ": A client error occurred")
        return False

    # cancel_open_orders:Void
    # NOTE: Safely cancels all open orders, if possible.
    def cancel_open_orders(self):
        try:
            if not self.debug:
                cancelled_order_ids = self.query.exec_cancel_open_orders()
                Utility.log("Cancelled orders " + cancelled_order_ids)
            else:
                Utility.warning("Would have cancelled all open orders if not in 'debug' mode")
            return True
        except:
            Utility.error("Could not cancel open orders: A client error occurred")
        return False

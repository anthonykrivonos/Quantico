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
    def __init__(self, query, portfolio, sec_interval = 900, name = "Algorithm", buy_range = (0.00, sys.maxsize), test = False, cash = 0.00):

        # Initialize properties
        self.name = name                        # String name of the algorithm
        self.query = query                      # Query class for making API calls
        self.portfolio = portfolio              # The portfolio to call the algorithm on
        self.sec_interval = sec_interval        # Interval (in s) of event executions
        self.buy_list = []                      # List of stocks bought in the past day
        self.sell_list = []                     # List of stocks sold in the past day
        self.buy_range = buy_range              # Range of prices for purchasing stocks
        self.logs = []                          # List of logged output
        self.prices = {}                        # Map of symbols to the current ask price of one share
        self.cash = cash                        # Float buying power amount.
        self.timestamp = Utility.now_timestamp()# Updated timestamp the algorithm is running.
        self.event = Event.ON_MARKET_WILL_OPEN  # Current even the algorithm is on

        # Backtesting properties
        self.test = test                        # Set to True if backtesting

        # Initialize the algorithm
        self.initialize()

    #
    # Initialization Functions
    #

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):
        if self.test:
            # User is performing a backtest, don't schedule event functions
            self.log("Initialized algorithm \'" + self.name + "\' for backtesting...", 't')
            self.__backtest()
        else:
            # User is live trading, schedule event functions
            self.log("Initialized algorithm \'" + self.name + "\' for live trading...")

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
            self.on_custom_timer(lambda: self.on_market_open(), start_d64 = self.open_hour)
            self.on_custom_timer(lambda: self.while_market_open(), repeat_sec = sec_interval, start_d64 = self.open_hour, stop_d64 = self.close_hour)
            self.on_custom_timer(lambda: self.on_market_close(), start_d64 = self.close_hour)

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

    # __reset_for_next_day:Void
    # NOTE: Resets the algorithm for execution the following day.
    def __reset_for_next_day(self):
        self.buy_list = []
        self.sell_list = []
        if not self.test:
            self.timestamp = Utility.now_timestamp()

    #
    # Event Functions
    #

    # on_market_will_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self, cash = None, prices = None):
        self.log("Market will open.")
        self.event = Event.ON_MARKET_WILL_OPEN
        self.__reset_for_next_day()
        self.__update_cash(cash)
        self.__update_prices(prices)
        pass

    # on_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market opens.
    def on_market_open(self, cash = None, prices = None):
        self.log("Market just opened.")
        self.event = Event.ON_MARKET_OPEN
        self.__update_cash(cash)
        self.__update_prices(prices)
        pass

    # while_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called on an interval while market is open.
    def while_market_open(self, cash = None, prices = None):
        self.log("Market currently open.")
        self.event = Event.WHILE_MARKET_OPEN
        self.__update_cash(cash)
        self.__update_prices(prices)
        pass

    # on_market_close:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market closes.
    def on_market_close(self, cash = None, prices = None):
        self.log("Market has closed.")
        self.event = Event.ON_MARKET_CLOSE
        self.__update_cash(cash)
        self.__update_prices(prices)
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
        type = type.lower()
        if not isinstance(message, str):
            message = str(message)
        if self.test and (type != "t" and type != "test"):
            self.logs.append("Backtest: " + message)
        elif type == 'error' or type == 'w' or type == 'err':
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
    # Backtesting and Live Value Functions
    #

    # value:Float
    # Returns the value of the portfolio.
    def value(self):
        value = 0.00
        for quote in self.portfolio.get_quotes():
            value += (self.price(quote.symbol) * quote.count)
        return value

    # price:Void
    # param symbol:String => Symbol.
    # Returns the current price of the given symbol.
    def price(self, symbol):
        if symbol in self.prices:
            return self.prices[symbol]
        elif self.test and self.timestamp in self.portfolio.get_symbol_history_map(symbol):
            price = self.portfolio.get_symbol_history_map(symbol)[self.timestamp]
            if self.event == Event.WHILE_MARKET_OPEN:
                return price.low
            elif self.event == Event.ON_MARKET_CLOSE:
                return price.close
            else:
                return price.open
            return
        return self.query.get_current_price(symbol)

    # __update_prices:Void
    # param prices:{String:Float}? => Map of prices to update the global map to.
    # NOTE: Updates map of symbols to their current ask prices.
    def __update_prices(self, prices = None):
        if prices is None:
            # If prices is None, update it with current market values.
            self.prices = {}
            for quote in self.portfolio.get_quotes():
                self.prices[quote.symbol] = self.query.get_current_price(quote.symbol)
        else:
            # Otherwise, update it with given values.
            self.prices = prices

    # __update_cash:Void
    # param cash:Float => User's buying power.
    # NOTE: Updates user's buying power.
    def __update_cash(self, cash = None):
        if cash is None:
            # If cash is None, update it with current user's buying power.
            self.cash = self.query.user_buying_power()
        else:
            # Otherwise, update it with given value.
            self.cash = cash

    #
    # Backtesting
    #

    # __backtest:Void
    # NOTE: Performs a backtest on the algorithm.
    def __backtest(self):
        # Map each symbol to a list of historical prices.
        historicals_map, historical_times = self.portfolio.get_history_tuple(Span.DAY, Span.YEAR, Bounds.REGULAR)
        symbols = self.portfolio.get_symbols()

        # Assure enough historicals data will be processed
        if len(historical_times) == 0:
            self.log("Not enough data for a backtest.", 'error', 't')
            return

        # Assure enough cash is allocated
        if self.cash == 0.00:
            self.log("Not enough starting cash for backtest.", 'error', 't')
            return

        previous_value = self.value()
        self.cash += previous_value
        start_cash = self.cash

        self.log("Starting backtest from " + Utility.get_timestamp_string(historical_times[0]) + " to " + Utility.get_timestamp_string(historical_times[-1]) + " with $" + str(start_cash), 't')

        # Run through timeline
        for time in historical_times:

            self.timestamp = time

            self.cash -= previous_value
            previous_value = self.value()
            self.cash += previous_value

            # Announce progress
            percentage = (self.cash - start_cash) / start_cash * 100
            difference = self.cash - start_cash
            if percentage >= 0.00:
                self.log(Utility.get_timestamp_string(time) + " (backtest): cash($" + str(self.cash) + "), gain(" + str(abs(percentage)) + "%, $" + str(abs(difference)) + ")", 't')
            else:
                self.log(Utility.get_timestamp_string(time) + " (backtest): cash($" + str(self.cash) + "), loss(" + str(abs(percentage)) + "%, $" + str(abs(difference)) + ")", 't')

            # Store five maps of symbols to instantaneous prices
            on_market_will_open_prices = {}
            on_market_open_prices = {}
            while_market_open_low_prices = {}
            while_market_open_high_prices = {}
            on_market_close_prices = {}
            for symbol in symbols:
                price = historicals_map[symbol][time]
                on_market_will_open_prices[symbol] = price.open
                on_market_open_prices[symbol] = price.open
                while_market_open_low_prices[symbol] = price.low
                while_market_open_high_prices[symbol] = price.high
                on_market_close_prices[symbol] = price.close

            # Execute events with appropriate prices
            self.on_market_will_open(self.cash, on_market_will_open_prices)
            self.on_market_open(self.cash, on_market_open_prices)
            self.while_market_open(self.cash, while_market_open_low_prices)
            self.while_market_open(self.cash, while_market_open_high_prices)
            self.on_market_close(self.cash, on_market_close_prices)

        end_cash = self.cash

        # Announce final progress
        final_percentage = (end_cash - start_cash) / start_cash * 100
        final_difference = end_cash - start_cash
        if final_percentage >= 0.00:
            self.log("Final results (backtest): cash($" + str(end_cash) + "), gain(" + str(abs(final_percentage)) + "%, $" + str(abs(final_difference)) + ")", 't')
        else:
            self.log("Final results (backtest): cash($" + str(end_cash) + "), loss(" + str(abs(final_percentage)) + "%, $" + str(abs(final_difference)) + ")", 't')
        pass

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
            price = limit if not None else stop
            if price <= self.cash and price <= self.buy_range[1] and price >= self.buy_range[0] and symbol not in self.sell_list:
                if not self.test:
                    self.query.exec_buy(symbol, quantity, stop, limit)
                    self.log("Bought " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                else:
                    self.log("Backtest: Bought " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                self.cash -= (quantity * price)
                self.buy_list.append(symbol)
                self.portfolio.add_quote(Quote(symbol, quantity))
                return True
            else:
                if price > self.buy_range[1]:
                    self.log("Could not buy " + symbol + ": Stock too expensive", 'error')
                elif price < self.buy_range[0]:
                    self.log("Could not buy " + symbol + ": Stock too cheap", 'error')
                elif symbol in self.sell_list:
                    self.log("Could not buy " + symbol + ": Stock already sold today", 'error')
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
            price = limit if not None else stop
            if symbol not in self.buy_list:
                if not self.test:
                    self.query.exec_sell(symbol, quantity, stop, limit)
                    self.log("Sold " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                else:
                    self.log("Backtest: Sold " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                self.cash += (quantity * price)
                self.sell_list.append(symbol)
                self.portfolio.remove_quote(Quote(symbol, quantity))
                return True
            else:
                if symbol in self.buy_list:
                    Utility.error("Could not sell " + symbol + ": Stock already bought today")
        except Exception as e:
            Utility.error("Could not sell " + symbol + ": " + str(e))
        return False

    # cancel:Void
    # param order_id:String => ID of the order to cancel.
    # NOTE: Safely cancels an order given its ID, if possible.
    def cancel(self, order_id):
        try:
            if not self.test:
                self.query.exec_cancel(order_id)
                self.log("Cancelled order " + order_id)
            else:
                self.log("Backtest: Cancelled order " + order_id)
            return True
        except:
            Utility.error("Could not cancel " + symbol + ": A client error occurred")
        return False

    # cancel_open_orders:Void
    # NOTE: Safely cancels all open orders, if possible.
    def cancel_open_orders(self):
        try:
            if not self.test:
                cancelled_order_ids = self.query.exec_cancel_open_orders()
                Utility.log("Cancelled orders " + str(cancelled_order_ids))
            else:
                self.log("Backtest: Cancelled open orders")
            return True
        except:
            Utility.error("Could not cancel open orders: A client error occurred")
        return False

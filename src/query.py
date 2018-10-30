# Anthony Krivonos
# Oct 29, 2018
# src/query.py

# Abstract: Offers query methods that act as a wrapper for the Robinhood API and convert the returned objects into workable models.

# Imports
import sys
sys.path.append('ext_modules')
from datetime import date
from enum import Enum

from Robinhood import Robinhood

# Option Enum
class Option(Enum):
    CALL = "call" # "call" order
    PUT = "put"   # "put" order

# Time Enum
class Time(Enum):
    GOOD_FOR_DAY = "GFD"        # "GFD" time
    GOOD_TIL_CANCELED = "GTC"   # "GTC" time

# Query Class
class Query:

    # __init__:Void
    # param username:String => Username of the Robinhood user.
    # param password:String => Password for the Robinhood user.
    def __init__(self, username, password):
        self.trader = Robinhood()
        self.trader.login(username=username, password=password)

    ##           ##
    #   Getters   #
    ##           ##

    # get_quote:[String:String]
    # param symbol:String => String symbol of the instrument to return.
    # returns Quote data for the instrument with the given symbol.
    def get_quote(self, symbol):
        return self.trader.quote_data(symbol)[0] or None

    # get_quotes:[[String:String]]
    # param symbol:[String] => List of string symbols of the instrument to return.
    # returns Quote data for the instruments with the given symbols.
    def get_quotes(self, symbols):
        return self.trader.quotes_data(symbols)


    # get_instrument:[String:String]
    # param symbol:String => String symbol of the instrument.
    # returns The instrument with the given symbol.
    def get_instrument(self, symbol):
        return self.trader.instruments(symbol)[0] or None

    # get_history:[[String:String]]
    # param symbol:String => String symbol of the instrument.
    # returns Historical quote data for the instruments with the given symbols on a 5-minute, weekly interval.
    def get_history(self, symbol):
        return self.trader.quotes_data(symbol, "5minute", "week")

    # get_news:[[String:String]]
    # param symbol:String => String symbol of the instrument.
    # returns News for the instrument with the given symbol.
    def get_news(self, symbol):
        return self.trader.get_news(symbol)

    # get_fundamentals:Dict[String:String]
    # param symbol:String => String symbol of the instrument.
    # returns Fundamentals for the instrument with the given symbol.
    def get_fundamentals(self, symbol):
        return self.trader.get_fundamentals(symbol)

    # get_fundamentals:[String:String]
    # param symbol:String => String symbol of the instrument.
    # param dates:Date => List of datetime.date objects.
    # param type:Option => Option.CALL or Option.PUT
    # returns Options for the given symbol within the listed dates for the given type.
    def get_options(self, symbol, dates, type):
        return self.trader.get_options(symbol, list(map(lambda date: date.isoFormat(), dates)), type.value)

    # get_market_data:[String:String]
    # param optionId:String => Option ID for the option to return.
    # returns Options for the given ID.
    def get_market_data(self, optionId):
        return self.trader.get_option_market_data(optionId)

    ##                ##
    #   User Methods   #
    ##                ##

    # user_portfolio:[String:String]
    # returns Portfolio for the logged in user.
    def user_portfolio(self):
        return self.trader.portfolios()

    # user_portfolio:[String:String]
    # returns Positions for the logged in user.
    def user_positions(self):
        return self.trader.positions()

    # user_dividends:[String:String]
    # returns Dividends for the logged in user.
    def user_dividends(self):
        return self.trader.dividends()

    # user_securities:[String:String]
    # returns Securities for the logged in user.
    def user_securities(self):
        return self.trader.positions()

    # user_equity:[String:String]
    # returns Equity for the logged in user.
    def user_equity(self):
        return self.trader.equity()

    # user_equity_prev:[String:String]
    # returns Equity upon the previous close for the logged in user.
    def user_equity_prev(self):
        return self.trader.equity_previous_close()

    # user_equity_adj_prev:[String:String]
    # returns Adjusted equity upon the previous close for the logged in user.
    def user_equity_adj_prev(self):
        return self.trader.adjusted_equity_previous_close()

    # user_equity_ext_hours:[String:String]
    # returns Extended hours equity for the logged in user.
    def user_equity_ext_hours(self):
        return self.trader.extended_hours_equity()

    # user_equity_last_core:[String:String]
    # returns Last core equity for the logged in user.
    def user_equity_last_core(self):
        return self.trader.last_core_equity()

    # user_excess_margin:[String:String]
    # returns Excess margin for the logged in user.
    def user_excess_margin(self):
        return self.trader.excess_margin()

    # user_market_value:[String:String]
    # returns Market value for the logged in user.
    def user_market_value(self):
        return self.trader.market_value()

    # user_market_value_ext_hours:[String:String]
    # returns Extended hours market value for the logged in user.
    def user_market_value_ext_hours(self):
        return self.trader.extended_hours_market_value()

    # user_market_value_last_core:[String:String]
    # returns Last core market value for the logged in user.
    def user_market_value_last_core(self):
        return self.trader.last_core_market_value()

    # user_order_history:[String:String]
    # param orderId:String => The order ID to return the order for.
    # returns A specified order executed by the logged in user.
    def user_order(self, orderId):
        return self.trader.order_history(self, orderId)

    # user_orders:[[String:String]]
    # returns The order history for the logged in user.
    def user_orders(self):
        return self.trader.order_history(self, None)

    ##                     ##
    #   Execution Methods   #
    ##                     ##

    # exec_buy:[String:String]
    # param symbol:String => String symbol of the instrument.
    # param quantity:Number => Number of shares to execute buy for.
    # param stop:Number? => Sets a stop price on the buy, if not None.
    # param limit:Number? => Sets a limit price on the buy, if not None.
    # param time:Time? => Defines the expiration for a limited buy.
    # returns The order response.
    def exec_buy(self, symbol, quantity, stop = None, limit = None, time = None):
        if time is None:
            time = Time.GOOD_TIL_CANCELED
        if limit is not None:
            if stop is not None:
                return self.trader.place_stop_limit_buy_order(None, symbol, time.value, stop, quantity)
            return self.trader.place_limit_buy_order(None, symbol, time.value, limit, quantity)
        elif stop is not None:
            return self.trader.place_stop_loss_buy_order(None, symbol, time.value, stop, quantity)
        return self.trader.place_market_buy_order(None, symbol, time.value, quantity)

    # exec_sell:[String:String]
    # param symbol:String => String symbol of the instrument.
    # param quantity:Number => Number of shares to execute sell for.
    # param stop:Number? => Sets a stop price on the sell, if not None.
    # param limit:Number? => Sets a limit price on the sell, if not None.
    # param time:Time? => Defines the expiration for a limited buy.
    # returns The order response.
    def exec_sell(self, symbol, quantity, stop = None, limit = None, time = None):
        if time is None:
            time = Time.GOOD_TIL_CANCELED
        if limit is not None:
            if stop is not None:
                return self.trader.place_stop_limit_sell_order(None, symbol, time.value, stop, quantity)
            return self.trader.place_limit_sell_order(None, symbol, time.value, limit, quantity)
        elif stop is not None:
            return self.trader.place_stop_loss_sell_order(None, symbol, time.value, stop, quantity)
        return self.trader.place_market_sell_order(None, symbol, time.value, quantity)

    # exec_cancel:[String:String]
    # param orderId:String => ID of the order to cancel.
    # returns The canceled order response.
    def exec_cancel(self, orderId):
        return query.trader.cancel_order(orderId)

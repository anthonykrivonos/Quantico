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

# Abstract: Algorithm employing a no-day-trades tactic.
#           For more info on this algorithm, see:
#           https://www.quantopian.com/algorithms/5bf47d593f88ef0045e55e55

class NoDayTradesAlgorithm(Algorithm):

    # __init__:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    def __init__(self, query, portfolio, sec_interval = 900):

        # Initialize properties

        # Set to True if buys and sells should not go through
        self.debug = False

        # Range of prices for stock purchasing
        self.buy_range = (0.00, 5.00)

        # All stocks available to buy/sell
        self.candidates = []

        # List of stocks to trade
        self.candidates_to_trade = []

        # Weight of stocks to trade
        self.candidates_to_trade_weight = 0.00

        # Total number of stocks to trade in this algorithm
        self.max_candidates = 100

        # Number of buy orders that can be placed concurrently
        self.max_simult_buy_orders = 30

        # Price of any stock that must immediately be sold
        self.immediate_sale_price = self.buy_range[0]

        # Number of days to hold a stock until it must be sold
        self.immediate_sale_age = 6

        # Over simplistic tracking of position age
        self.age = {}

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "No Day Trades", buy_range = self.buy_range, debug = self.debug)

        self.on_market_will_open()

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

        self.candidates, self.candidates_to_trade, self.candidates_to_trade_weight = self.generate_candidates()

        lowest_price = self.buy_range[0]
        for quote in self.portfolio.get_quotes():
            current_price = self.query.get_current_price(quote.symbol)
            if current_price < lowest_price:
                lowest_price = current_price
            if quote.symbol in self.age:
                self.age[quote.symbol] += 1
            else:
                self.age[quote.symbol] = 1
        for symbol in self.age:
            if not self.portfolio.is_symbol_in_portfolio(symbol):
                self.age[quote.symbol] = 0
            Utility.log("stock.symbol: " + symbol + " : age: " + str(self.age[symbol]))

        self.perform_buy_sell()

        pass

    # on_market_open:Void
    # NOTE: Called exactly when the market opens. Cannot include a buy or sell.
    def on_market_open(self):
        Algorithm.on_market_open(self)
        pass

    # on_market_close:Void
    # NOTE: Called exactly when the market closes.
    def on_market_close(self):
        Algorithm.on_market_close(self)

        self.query.exec_cancel_open_orders()

        pass

    #
    # Algorithm
    #

    def generate_candidates(self):

        # Get all fundamentals within the buy range
        unsorted_fundamentals = self.query.get_fundementals_by_criteria(self.buy_range)

        # Sort the unsorted fundamentals by low price (close would be preferred, but is unavailable)
        candidate_fundamentals = sorted(unsorted_fundamentals, key=lambda fund: fund['low'])

        # Store the symbols of each candidate fundamental into a separate array
        all_candidate_symbols = [ fund['symbol'] for fund in candidate_fundamentals ]

        # Instantiate list of long and short fundamentals, as well as the average of their low prices
        short_candidate_fundamentals = []
        short_candidate_low_avg = 0.00
        long_candidate_fundamentals = []
        long_candidate_low_avg = 0.00

        # Update long and short data
        for fund in candidate_fundamentals:
            if self.portfolio.is_symbol_in_portfolio(fund['symbol']):
                # Stock is long
                long_candidate_fundamentals.append(fund)
                long_candidate_low_avg += float(fund['low'])
            else:
                # Stock is short
                short_candidate_fundamentals.append(fund)
                short_candidate_low_avg += float(fund['low'])
        long_candidate_low_avg /= max(len(long_candidate_fundamentals), 1)
        short_candidate_low_avg /= max(len(short_candidate_fundamentals), 1)

        # Create a new list of candidates to trade
        candidates_to_trade_length = min(self.max_candidates + 1, len(candidate_fundamentals) + 1)
        candidates_to_trade_symbols = [ fund['symbol'] for fund in candidate_fundamentals[0:candidates_to_trade_length] ]

        # Set a weight for trades
        to_trade_weight = 1.00 / len(candidates_to_trade_symbols)

        return (all_candidate_symbols, candidates_to_trade_symbols, to_trade_weight)

    # perform_buy_sell:Void
    def perform_buy_sell(self):

        Utility.log("Executing perform_buy_sell:")

        # Percentage of the current price to submit buy orders at
        BUY_FACTOR = 0.99

        # Percentage of the current price to submit sell orders at
        SELL_FACTOR = 1.01

        # Factor at which the stock may be higher than its average price over the past day and can still be bought
        GAIN_FACTOR = 1.25

        # Get the user's buying power, or cash
        cash = self.query.user_buying_power()

        # Cancel all of the user's open orders
        self.query.exec_cancel_open_orders()

        # Track the user's open orders
        open_orders = self.query.user_open_orders()
        open_order_symbols = {}
        open_buy_order_count = 0
        for order in open_orders:

            stock = self.query.stock_from_instrument_url(order['instrument'])
            open_order_symbols[stock['symbol']] = True

            # Increment number of current buy orders
            if 'side' in order and order['side'] == 'buy':
                open_buy_order_count += 1

        # Sell stocks at profit target in hope that somebody actually buys it
        for quote in self.portfolio.get_quotes():

            # Assure the given quote is not part of any open orders
            if quote.symbol not in open_order_symbols:

                # Get the number of shares of the stock in the given portfolio
                stock_shares = quote.count

                # Current price of the given stock
                current_price = self.query.get_current_price(quote.symbol)

                # Sell if the age has exceeded the immediate sale age and the immediate sale price is greater than the current price
                if quote.symbol in self.age:
                    if self.age[quote.symbol] < 2:
                        pass
                    elif self.immediate_sale_age <= self.age[quote.symbol] and self.immediate_sale_price >= current_price:
                        Algorithm.sell(self, quote.symbol, stock_shares, None, current_price)
                        pass
                else:
                    self.age[quote.symbol] = 1

        # Instantiate the weight for the number of simultaneous buy orders to be made
        weight_for_buy_order = float(1.00 / self.max_simult_buy_orders)

        # Iterate over each candidate to sell
        open_buy_order_count
        for symbol in self.candidates:

            # Finish buying stocks once the limit has been reached
            if open_buy_order_count > self.max_simult_buy_orders:
                break

            # Store the current price of the candidate stock
            current_price = self.query.get_current_price(symbol)

            # Get the history of the stock
            history = self.portfolio.get_symbol_history(symbol, Span.TEN_MINUTE, Span.DAY)

            if current_price != 0.0:

                # Calculate stock close price mean over the past day
                mean = 0.00
                for price in history:
                    mean += price.close
                mean /= max(len(history), 1)
                mean = round(mean, 2)

                if mean != 0.0:

                    # Calculate buy price
                    if current_price > float(GAIN_FACTOR * mean):
                        # Set the buy_price to the current price if the stock is at a high compared to the average
                        buy_price = current_price
                    else:
                        # Otherwise, set the buy price equal to the current price
                        buy_price = current_price * BUY_FACTOR
                    buy_price = round(buy_price, 2)

                    # Number of shares to buy is the weight of the buy order divided by the buy price times the number of available cash
                    stock_shares = int(weight_for_buy_order * cash / buy_price)
                    if stock_shares > 0:
                        did_buy = Algorithm.buy(self, symbol, stock_shares, None, buy_price)
                        if did_buy:
                            # Decrement available cash and increment the number of buy orders
                            cash -= stock_shares * buy_price
                            open_buy_order_count += 1

        Utility.log("Finished run of perform_buy_sell")

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

        # Range of prices to purchase stocks at: (low, high)
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
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "No Day Trades")

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

        # print(self.query.get_by_tag(Tag.TECHNOLOGY))
        unsorted_fundamentals = self.query.get_fundementals_by_criteria(self.buy_range)
        candidate_fundamentals = sorted(unsorted_fundamentals, key=lambda fund: fund['low'])

        all_candidate_symbols = [ fund['symbol'] for fund in candidate_fundamentals ]

        portfolio_map = {}
        for quote in self.portfolio.get_quotes():
            portfolio_map[quote.symbol] = True

        short_candidate_fundamentals = []
        short_candidate_low_avg = 0.00
        long_candidate_fundamentals = []
        long_candidate_low_avg = 0.00

        for fund in candidate_fundamentals:
            if fund['symbol'] in portfolio_map:
                long_candidate_fundamentals.append(fund)
                long_candidate_low_avg += float(fund['low'])
            else:
                short_candidate_fundamentals.append(fund)
                short_candidate_low_avg += float(fund['low'])

        long_candidate_low_avg /= max(len(long_candidate_fundamentals), 1)
        short_candidate_low_avg /= max(len(short_candidate_fundamentals), 1)

        percent_difference = (short_candidate_low_avg - long_candidate_low_avg) / max(long_candidate_low_avg, 1)

        candidate_length = min(self.max_candidates + 1, len(candidate_fundamentals))
        candidates_to_trade_symbols = [ fund['symbol'] for fund in candidate_fundamentals[0:candidate_length] ]

        to_trade_weight = 1.00 / len(candidates_to_trade_symbols)

        return (all_candidate_symbols, candidates_to_trade_symbols, to_trade_weight)

    # perform_buy_sell:Void
    def perform_buy_sell(self):

        Utility.log("Executing perform_buy_sell:")

        buy_factor = .99
        sell_factor = 1.01

        cash = self.query.user_buying_power()

        self.query.exec_cancel_open_orders()

        open_orders = self.query.user_open_orders()
        open_order_symbols = {}
        for order in open_orders:
            stock = self.query.stock_from_instrument_url(order['instrument'])
            open_order_symbols[stock['symbol']] = True

        # Order sell at profit target in hope that somebody actually buys it
        for quote in self.portfolio.get_quotes():
            if quote.symbol not in open_order_symbols:
                stock_shares = quote.count
                current_price = self.query.get_current_price(quote.symbol)

                if quote.symbol in self.age and self.age[quote.symbol] == 1:
                    pass
                elif quote.symbol in self.age and self.immediate_sale_age <= self.age[quote.symbol] and self.immediate_sale_price > current_price:
                    if (quote.symbol in self.age and self.age[quote.symbol] < 2):
                        pass
                    elif quote.symbol not in self.age:
                        self.age[quote.symbol] = 1
                    else:
                        Algorithm.sell(self, quote.symbol, stock_shares, None, current_price)
                        pass
                else:
                    if (quote.symbol in self.age and self.age[quote.symbol] < 2) :
                        pass
                    elif quote.symbol not in self.age:
                        self.age[quote.symbol] = 1
                    else:
                        Algorithm.sell(self, quote.symbol, stock_shares, None, current_price)
                        pass

        weight_for_buy_order = float(1.00 / self.max_simult_buy_orders)

        for i, symbol in enumerate(self.candidates):
            if i >= self.max_simult_buy_orders:
                break

            current_price = self.query.get_current_price(symbol)
            history = self.portfolio.get_symbol_history(symbol, Span.TEN_MINUTE, Span.DAY)

            if current_price != 0.0:
                # Calculate stock close price mean
                mean = 0.00
                for price in history:
                    mean += price.close
                mean /= max(len(history), 1)
                if mean == 0.00:
                    mean = current_price

                if current_price > float(1.25 * mean):
                    buy_price = current_price
                else:
                    buy_price = current_price * buy_factor
                print(current_price)
                print(buy_price)
                print(buy_factor)
                stock_shares = int(weight_for_buy_order * cash / buy_price)
                Algorithm.buy(self, quote.symbol, stock_shares, None, buy_price)

        Utility.log("Finished run of perform_buy_sell")
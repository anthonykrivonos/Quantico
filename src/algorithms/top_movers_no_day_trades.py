# Anthony Krivonos
# Oct 29, 2018
# src/algorithms/top_movers_no_day_trades.py

# Global Imports
import numpy as np
import math

# Local Imports
from utility import *
from enums import *
from mathematics import *

from algorithms.__algorithm import *

# Abstract: Algorithm employing a top movers tactic.

class TopMoversNoDayTradesAlgorithm(Algorithm):

    # __init__:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    def __init__(self, query, portfolio, sec_interval = 900, test = False, cash = 0.00):

        # Initialize properties
        self.buy_range = (0.00, 5.00)

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "Top Movers, No Day Trades", buy_range = self.buy_range, test = test, cash = cash)

        self.perform_buy_sell()

    #
    # Event Functions
    #


    # on_market_will_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self, cash = None, prices = None):
        Algorithm.on_market_will_open(self, cash, prices)

        self.perform_buy_sell()
        pass

    # on_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market opens.
    def on_market_open(self, cash = None, prices = None):
        Algorithm.on_market_open(self, cash, prices)
        pass

    # while_market_open:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called on an interval while market is open.
    def while_market_open(self, cash = None, prices = None):
        Algorithm.while_market_open(self, cash, prices)

        self.perform_buy_sell()
        pass

    # on_market_close:Void
    # param cash:Float => User's buying power.
    # param prices:{String:Float}? => Map of symbols to ask prices.
    # NOTE: Called exactly when the market closes.
    def on_market_close(self, cash = None, prices = None):
        Algorithm.on_market_close(self, cash, prices)

        self.perform_buy_sell()
        pass

    #
    # Algorithm
    #

    # perform_buy_sell:Void
    # NOTE: Algorithm works like this:
    #   - Assign "purchase propensities" depending on the following criteria:
    #   - ROUND 1: Concavity of price graph
    #   - ROUND 2: Most recent rate of change in the price graph
    #   - ROUND 3: Last closing price of the stock
    #   - Sell bottom 2/3 of performers
    #   - Buy top 1/3 of performers by ratio
    def perform_buy_sell(self):

        Algorithm.log(self, "Executing perform_buy_sell:")

        # The percentage of the user's total equity to use for this algorithm
        USER_CASH_PERCENTAGE = 0.6

        # Weight of each round of propensity calculation
        ROUND_1_WEIGHT = 1.1
        ROUND_2_WEIGHT = 1.7
        ROUND_3_WEIGHT = 1.3

        Algorithm.log(self, "Cash percentage: " + str(USER_CASH_PERCENTAGE))
        Algorithm.log(self, "Round 1 weight: " + str(ROUND_1_WEIGHT))
        Algorithm.log(self, "Round 2 weight: " + str(ROUND_2_WEIGHT))
        Algorithm.log(self, "Round 3 weight: " + str(ROUND_3_WEIGHT))

        symbols_to_analyze = []
        symbol_quantity_map = {}

        for quote in self.portfolio.get_quotes():
            symbols_to_analyze.append(quote.symbol)
            symbol_quantity_map[quote.symbol] = quote.count

        for symbol in self.query.get_by_tag(Tag.TOP_MOVERS):
            if symbol not in symbol_quantity_map:
                symbols_to_analyze.append(symbol)
                symbol_quantity_map[symbol] = 0

        # Store symbol count
        symbol_count = len(symbols_to_analyze)

        # Store tuples for symbols to multiple different values

        # symbol: quintuple
        symbol_quintuple_map = {}
        # (symbol, quintuple)
        symbol_quintuples = []

        # Store tuples for polynomial evaluation
        # (symbol, value)
        symbol_first_deriv = []
        symbol_second_deriv = []

        # Propensity to buy each stock
        # symbol: propensity
        symbol_purchase_propensity = {}

        # Loop through symbols
        for symbol in symbols_to_analyze:

            # Default purchase propensity = 0
            symbol_purchase_propensity[symbol] = 0

            # Get historicals over past week
            symbol_historical = self.query.get_history(symbol, Span.TEN_MINUTE, Span.WEEK)

            # Get historical quintuples per symbol
            quintuples = Utility.get_quintuples_from_historicals(symbol_historical)

            # Store the list of quintuples in the first map
            symbol_quintuples.append((symbol, quintuples))
            symbol_quintuple_map[symbol] = quintuples

            # Keep track of x and y values to find the polynomial of best fit
            x = []
            y = []
            for quintuple in quintuples:
                x.append(quintuple[Quintuple.TIME.value])
                y.append(quintuple[Quintuple.CLOSE.value])

            # Store the polynomial (deg 2), first derivative (deg 1), and second derivative (deg 1)
            symbol_poly = Math.poly(x, y, 2)

            # First derivative
            symbol_first_deriv.append((symbol, Math.eval(Math.deriv(symbol_poly, 1), x[-1])))

            # Second derivative
            symbol_second_deriv.append((symbol, Math.eval(Math.deriv(symbol_poly, 2), x[-1])))

        # Store quintuples by open price, ascending
        symbol_quintuples = sorted(symbol_quintuples, key=lambda pair: pair[1][-1][Quintuple.CLOSE.value])

        # Sort lists of derivatives, descending
        symbol_first_deriv = sorted(symbol_first_deriv, key=lambda pair: pair[1], reverse=True)
        symbol_second_deriv = sorted(symbol_second_deriv, key=lambda pair: pair[1], reverse=True)

        # Assign 1st round of purchase propensities, by second derivative
        factor = ROUND_1_WEIGHT ** symbol_count
        for pair in symbol_second_deriv:
            symbol_purchase_propensity[pair[0]] += factor
            factor /= ROUND_1_WEIGHT

        # Assign 2nd round of purchase propensities, by first derivative
        factor = ROUND_2_WEIGHT ** symbol_count
        for pair in symbol_first_deriv:
            symbol_purchase_propensity[pair[0]] += factor
            factor /= ROUND_2_WEIGHT

        # Assign 3rd round of purchase propensities, by open price
        factor = ROUND_3_WEIGHT ** symbol_count
        for pair in symbol_quintuples:
            symbol_purchase_propensity[pair[0]] += factor
            factor /= ROUND_3_WEIGHT

        # Convert the list of propensities into an array of tuples
        symbol_propensity_list = []
        for symbol, propensity in symbol_purchase_propensity.items():
            symbol_propensity_list.append((symbol, propensity))

        # Sort the propensity list by order propensity
        symbol_propensity_list = sorted(symbol_propensity_list, key=lambda pair: pair[1], reverse=True)

        #
        # First Execution - Sell bottom 2/3 performers
        #

        # Count the quotes to sell
        bad_performer_count = round(symbol_count * 2 / 3)
        bad_performer_list = symbol_propensity_list[-1 * bad_performer_count:symbol_count]

        Algorithm.log(self, "Bad performers: " + str(bad_performer_list))

        # Sell each poor performer
        for pair in bad_performer_list:
            symbol = pair[0]
            quantity = symbol_quantity_map[symbol]
            limit = symbol_quintuple_map[symbol][-1][Quintuple.LOW.value]
            if quantity > 0.0:
                did_sell = Algorithm.sell(self, symbol, quantity, limit=limit)

        #
        # Second Execution - Buy top 1/4 performers
        #

        # Count the quotes to buy
        good_performer_count = symbol_count - bad_performer_count
        good_performer_list = symbol_propensity_list[0:good_performer_count]

        Algorithm.log(self, "Good performers: " + str(good_performer_list))

        user_cash = USER_CASH_PERCENTAGE * self.cash

        # Determine quantity of each stock to buy
        # Add a third value to the good_performer tuple, which is the amount we're able to spend on that stock
        total_propensity = 0
        for performer in good_performer_list:
            total_propensity += performer[1]
        for i, performer in enumerate(good_performer_list):
            amount_to_spend = (performer[1] / total_propensity) * user_cash
            good_performer_list[i] = (performer[0], performer[1], amount_to_spend)
            pass

        # Buy each good performer
        for triple in good_performer_list:
            symbol = triple[0]
            quantity = round(triple[2] / symbol_quintuple_map[symbol][-1][Quintuple.HIGH.value])
            limit = symbol_quintuple_map[symbol][-1][Quintuple.LOW.value]
            if quantity > 0.0:
                did_buy = Algorithm.buy(self, symbol, quantity, limit=limit)

        Algorithm.log(self, "Finished run of perform_buy_sell")

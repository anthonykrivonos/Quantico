# Anthony Krivonos
# Oct 29, 2018
# src/alg/nodaytrades.py

# Abstract: Algorithm employing the no-day-trades tactic.

import numpy as np #needed for NaN handling
import math #ceil and floor are useful for rounding

from utility import *
from enums import *

from algmath import *

class NoDayTradesAlgorithm:

    def __init__(self, query):

        Utility.log("Initialized NoDayTradesAlgorithm")

        # Query
        self.query = query

        # Properties
        self.buys_allowed = 10
        self.sells_allowed = 10
        self.cancels_allowed = 20

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

        # Schedule event functions
        sec_interval = 900 # 15 minutes
        Utility.sleep_then_execute(time=self.pre_open_hour, sec=sec_interval, action=lambda: self.market_will_open())
        Utility.execute_between_times(start_time=self.open_hour, stop_time=self.close_hour, sec=sec_interval, action=lambda: self.on_market_open())
        Utility.sleep_then_execute(time=self.close_hour, sec=sec_interval, action=lambda: self.on_market_close())


    # market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def market_will_open(self):
        Utility.log("Market will open.")
        self.weights_trading_algorithm()
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
        self.weights_trading_algorithm()

        # Run initialize to start trading next day
        self.initialize()
        pass

    #
    # Algorithm
    #

    # weights_trading_algorithm:Void
    # NOTE: Algorithm works like this:
    #   - Assign "purchase propensities" depending on the following criteria:
    #   - ROUND 1: Concavity of price graph
    #   - ROUND 2: Most recent rate of change in the price graph
    #   - ROUND 3: Price of the stock
    #   - Sell bottom 2/3 of performers
    #   - Buy top 1/3 of performers by ratio
    def weights_trading_algorithm(self):

        Utility.log("Executing weights_trading_algorithm:")

        # The percentage of the user's total equity to use for this algorithm
        USER_CASH_PERCENTAGE = 0.6

        # Weight of each round of propensity calculation
        ROUND_1_WEIGHT = 1.45
        ROUND_2_WEIGHT = 1.70
        ROUND_3_WEIGHT = 1.20

        Utility.log("Cash percentage: " + str(USER_CASH_PERCENTAGE))
        Utility.log("Round 1 weight: " + str(ROUND_1_WEIGHT))
        Utility.log("Round 2 weight: " + str(ROUND_2_WEIGHT))
        Utility.log("Round 3 weight: " + str(ROUND_3_WEIGHT))

        # Query for all symbols owned by the user
        all_user_symbols = []

        # Story the quantities of each stock owned, as well as the symbol into a list of all symbols
        user_portfolio = self.query.user_stock_portfolio()
        symbol_quantity_map = {}
        for stock in user_portfolio:
            symbol_quantity_map[stock['symbol']] = float(stock['quantity']) or 0.0
            all_user_symbols.append(stock['symbol'])

        # Store symbol count
        symbol_count = len(all_user_symbols)

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
        for symbol in all_user_symbols:

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

        Utility.log("Bad performers: " + str(bad_performer_list))

        # Sell each poor performer
        for pair in bad_performer_list:
            symbol = pair[0]
            quantity = symbol_quantity_map[symbol]
            limit = symbol_quintuple_map[symbol][-1][Quintuple.LOW.value]
            if quantity > 0.0:
                Utility.log("Selling " + str(quantity) + " shares of " + symbol + " with limit " + str(limit))
                self.safe_sell(symbol, quantity, limit=limit)

        #
        # Second Execution - Buy top 1/4 performers
        #

        # Count the quotes to buy
        good_performer_count = symbol_count - bad_performer_count
        good_performer_list = symbol_propensity_list[0:good_performer_count]

        Utility.log("Good performers: " + str(good_performer_list))

        user_cash = USER_CASH_PERCENTAGE * self.query.user_buying_power()

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
                self.safe_buy(symbol, quantity, limit=limit)

        Utility.log("Finished run of weights_trading_algorithm")


    #
    # Execution Functions
    #

    # safe_buy:Void
    # param symbol:String => String symbol of the instrument.
    # param quantity:Number => Number of shares to execute buy for.
    # param stop:Number? => Sets a stop price on the buy, if not None.
    # param limit:Number? => Sets a limit price on the buy, if not None.
    # NOTE: Safely executes a buy order outside of open hours, if possible.
    def safe_buy(self, symbol, quantity, stop = None, limit = None):
        now = Utility.now_datetime64()
        try:
            if self.buys_allowed > 0 and (now < self.open_hour or now > self.close_hour):
                self.query.exec_buy(symbol, quantity, stop, limit)
                self.buys_allowed -= 1
                Utility.log("Bought " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                return True
            else:
                if self.buys_allowed == 0:
                    Utility.log("Could not buy " + symbol + ": Ran out of buys allowed")
                elif now >= self.open_hour and now <= self.close_hour:
                    Utility.log("Could not buy " + symbol + ": Inside market hours")
        except:
            Utility.log("Could not buy " + symbol + ": A client error occurred")
        return False


    # safe_sell:Boolean
    # param symbol:String => String symbol of the instrument.
    # param quantity:Number => Number of shares to execute sell for.
    # param stop:Number? => Sets a stop price on the sell, if not None.
    # param limit:Number? => Sets a limit price on the sell, if not None.
    # NOTE: Safely executes a sell order outside of open hours, if possible.
    def safe_sell(self, symbol, quantity, stop = None, limit = None):
        now = Utility.now_datetime64()
        try:
            if self.sells_allowed > 0 and (now < self.open_hour or now > self.close_hour):
                self.query.exec_sell(symbol, quantity, stop, limit)
                self.sells_allowed -= 1
                Utility.log("Sold " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                return True
            else:
                if self.sells_allowed == 0:
                    Utility.log("Could not sell " + symbol + ": Ran out of sells allowed")
                elif now >= self.open_hour and now <= self.close_hour:
                    Utility.log("Could not sell " + symbol + ": Inside market hours")
        except:
            Utility.log("Could not sell " + symbol + ": A client error occurred")
        return False


    # safe_cancel:Void
    # param order_id:String => ID of the order to cancel.
    # NOTE: Safely cancels an order given its ID, if possible.
    def safe_cancel(self, order_id):
        now = Utility.now_datetime64()
        try:
            if self.cancels_allowed > 0 and (now < self.open_hour or now > self.close_hour):
                self.query.exec_cancel(order_id)
                self.cancels_allowed -= 1
                Utility.log("Cancelled order " + order_id)
                return True
            else:
                if self.cancels_allowed == 0:
                    Utility.log("Could not cancel order " + order_id + ": Ran out of cancels allowed")
                elif now >= self.open_hour and now <= self.close_hour:
                    Utility.log("Could not cancel order " + order_id + ": Inside market hours")
        except:
            Utility.log("Could not cancel " + symbol + ": A client error occurred")
        return False

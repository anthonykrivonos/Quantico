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

# Abstract: Algorithm employing the no-day-trades tactic.

class TopMoversNoDayTradesAlgorithm(Algorithm):

    # __init__:Void
    # param query:Query => Query object for API access.
    # param sec_interval:Integer => Time interval in seconds for event handling.
    def __init__(self, query, portfolio, sec_interval = 900):

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "Top Movers, No Day Trades")

        # Properties
        self.buy_list = []          # List of stocks bought in the current day
        self.sell_list = []         # List of stocks sold in the current day
        self.price_limit = 5.00     # Dollar limit for the maximum price of stocks to buy
        self.buys_allowed = 2000    # Number of buys allowed per day
        self.sells_allowed = 2000   # Number of sells allowed per day

        self.perform_buy_sell()

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):

        Algorithm.initialize(self)

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

    #
    # Event Functions
    #


    # market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def market_will_open(self):
        Algorithm.market_will_open(self)

        self.perform_buy_sell()
        pass

    # on_market_open:Void
    # NOTE: Called exactly when the market opens. Cannot include a buy or sell.
    def on_market_open(self):
        Algorithm.on_market_open(self)

        self.perform_buy_sell()
        pass

    # on_market_close:Void
    # NOTE: Called exactly when the market closes.
    def on_market_close(self):
        Algorithm.on_market_close(self)

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

        Utility.log("Executing perform_buy_sell:")

        # The percentage of the user's total equity to use for this algorithm
        USER_CASH_PERCENTAGE = 0.6

        # Weight of each round of propensity calculation
        ROUND_1_WEIGHT = 1.1
        ROUND_2_WEIGHT = 1.7
        ROUND_3_WEIGHT = 1.3

        Utility.log("Cash percentage: " + str(USER_CASH_PERCENTAGE))
        Utility.log("Round 1 weight: " + str(ROUND_1_WEIGHT))
        Utility.log("Round 2 weight: " + str(ROUND_2_WEIGHT))
        Utility.log("Round 3 weight: " + str(ROUND_3_WEIGHT))

        symbols_to_analyze = []
        symbol_quantity_map = {}

        for quote in self.portfolio.get_quotes():
            symbols_to_analyze.append(quote.symbol)
            symbol_quantity_map[quote.symbol] = quote.count

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

        Utility.log("Bad performers: " + str(bad_performer_list))

        # Sell each poor performer
        for pair in bad_performer_list:
            symbol = pair[0]
            quantity = symbol_quantity_map[symbol]
            limit = symbol_quintuple_map[symbol][-1][Quintuple.LOW.value]
            if quantity > 0.0:
                did_sell = self.safe_sell(symbol, quantity, limit=limit)

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
                did_buy = self.safe_buy(symbol, quantity, limit=limit)

        Utility.log("Finished run of perform_buy_sell")


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
            if len(self.buy_list) < self.buys_allowed and symbol not in self.buy_list and symbol not in self.sell_list:
                self.query.exec_buy(symbol, quantity, stop, limit)
                self.buy_list.append(symbol)
                Utility.log("Bought " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                return True
            else:
                if len(self.buy_list) == self.buys_allowed:
                    Utility.error("Could not buy " + symbol + ": Ran out of buys allowed")
                elif now >= self.open_hour and now <= self.close_hour:
                    Utility.error("Could not buy " + symbol + ": Inside market hours")
                elif symbol in self.buy_list:
                    Utility.error("Could not buy " + symbol + ": Stock already bought today")
                elif symbol in self.sell_list:
                    Utility.error("Could not buy " + symbol + ": Stock already sold today")
        except Exception as e:
            Utility.error("Could not buy " + symbol + ": " + str(e))
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
            if len(self.sell_list) < self.sells_allowed and symbol not in self.sell_list and symbol not in self.buy_list:
                self.query.exec_sell(symbol, quantity, stop, limit)
                self.sell_list.append(symbol)
                Utility.log("Sold " + str(quantity) + " shares of " + symbol + " with limit " + str(limit) + " and stop " + str(stop))
                return True
            else:
                if len(self.sell_list) < self.sells_allowed:
                    Utility.error("Could not sell " + symbol + ": Ran out of sells allowed")
                elif now >= self.open_hour and now <= self.close_hour:
                    Utility.error("Could not sell " + symbol + ": Inside market hours")
                elif symbol in self.sell_list:
                    Utility.error("Could not sell " + symbol + ": Stock already sold today")
                elif symbol in self.buy_list:
                    Utility.error("Could not sell " + symbol + ": Stock already bought today")
        except Exception as e:
            Utility.error("Could not sell " + symbol + ": " + str(e))
        return False


    # safe_cancel:Void
    # param order_id:String => ID of the order to cancel.
    # NOTE: Safely cancels an order given its ID, if possible.
    def safe_cancel(self, order_id):
        now = Utility.now_datetime64()
        try:
            if self.cancels_allowed > 0:
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

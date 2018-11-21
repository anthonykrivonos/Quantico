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

        # Call super.__init__
        Algorithm.__init__(self, query, portfolio, sec_interval, name = "No Day Trades")

        # Initialize properties
        self.buy_range = (0.00, 5.00)

        self.MaxCandidates = 100
        self.MaxBuyOrdersAtOnce = 30
        self.MyLeastPrice=3.00
        self.MyMostPrice=20.00
        self.MyFireSalePrice=self.MyLeastPrice
        self.MyFireSaleAge=6

        # over simplistic tracking of position age
        self.age={}

        self.perform_buy_sell()

    # initialize:void
    # NOTE: Configures the algorithm to run indefinitely.
    def initialize(self):

        Algorithm.initialize(self)

        self.make_pipeline()

        # Rebalance
        # my_rebalance()

    #
    # Event Functions
    #

    # on_market_will_open:Void
    # NOTE: Called an hour before the market opens.
    def on_market_will_open(self):
        Algorithm.on_market_will_open(self)

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

        self.cancel_open_orders()
        self.my_record_vars()

        pass

    #
    # Algorithm
    #

    def make_pipeline(self):

        # print(self.query.get_by_tag(Tag.TECHNOLOGY))
        print(self.query.get_symbols_by_criteria(self.buy_range))

        pass

        #
        # # Filter for primary share equities. IsPrimaryShare is a built-in filter.
        # primary_share = IsPrimaryShare()
        #
        # # Equities listed as common stock (as opposed to, say, preferred stock).
        # # 'ST00000001' indicates common stock.
        # common_stock = morningstar.share_class_reference.security_type.latest.eq('ST00000001')
        #
        # # Non-depositary receipts. Recall that the ~ operator inverts filters,
        # # turning Trues into Falses and vice versa
        # not_depositary = ~morningstar.share_class_reference.is_depositary_receipt.latest
        #
        # # Equities not trading over-the-counter.
        # not_otc = ~morningstar.share_class_reference.exchange_id.latest.startswith('OTC')
        #
        # # Not when-issued equities.
        # not_wi = ~morningstar.share_class_reference.symbol.latest.endswith('.WI')
        #
        # # Equities without LP in their name, .matches does a match using a regular
        # # expression
        # not_lp_name = ~morningstar.company_reference.standard_name.latest.matches('.* L[. ]?P.?$')
        #
        # # Equities with a null value in the limited_partnership Morningstar
        # # fundamental field.
        # not_lp_balance_sheet = morningstar.balance_sheet.limited_partnership.latest.isnull()
        #
        # # Equities whose most recent Morningstar market cap is not null have
        # # fundamental data and therefore are not ETFs.
        # have_market_cap = morningstar.valuation.market_cap.latest.notnull()
        #
        # # At least a certain price
        # price = USEquityPricing.close.latest
        # AtLeastPrice   = (price >= context.MyLeastPrice)
        # AtMostPrice    = (price <= context.MyMostPrice)
        #
        # # Filter for stocks that pass all of our previous filters.
        # tradeable_stocks = (
        #     primary_share
        #     & common_stock
        #     & not_depositary
        #     & not_otc
        #     & not_wi
        #     & not_lp_name
        #     & not_lp_balance_sheet
        #     & have_market_cap
        #     & AtLeastPrice
        #     & AtMostPrice
        # )
        #
        # LowVar=6
        # HighVar=40
        #
        # log.info('\nAlgorithm initialized variables:\n context.MaxCandidates %s \n LowVar %s \n HighVar %s'
        #     % (context.MaxCandidates, LowVar, HighVar)
        # )
        #
        # # High dollar volume filter.
        # base_universe = AverageDollarVolume(
        #     window_length=20,
        #     mask=tradeable_stocks
        # ).percentile_between(LowVar, HighVar)
        #
        # # Short close price average.
        # ShortAvg = SimpleMovingAverage(
        #     inputs=[USEquityPricing.close],
        #     window_length=3,
        #     mask=base_universe
        # )
        #
        # # Long close price average.
        # LongAvg = SimpleMovingAverage(
        #     inputs=[USEquityPricing.close],
        #     window_length=45,
        #     mask=base_universe
        # )
        #
        # percent_difference = (ShortAvg - LongAvg) / LongAvg
        #
        # # Filter to select securities to long.
        # stocks_worst = percent_difference.bottom(context.MaxCandidates)
        # securities_to_trade = (stocks_worst)
        #
        # return Pipeline(
        #     columns={
        #         'stocks_worst': stocks_worst
        #     },
        #     screen=(securities_to_trade),
        # )

    # perform_buy_sell:Void
    def perform_buy_sell(self):

        Utility.log("Executing perform_buy_sell:")



        Utility.log("Finished run of perform_buy_sell")

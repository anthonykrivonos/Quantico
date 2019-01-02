# Anthony Krivonos
# Nov 9th, 2018
# src/models/price.py

# Imports
import sys

# Pandas
import pandas as pd

# NumPy
import numpy as np

# SciPy
import scipy.optimize as optimize

# Enums
from enums import *

# Math
from math import exp

# PriceModel
from models.price import *

# QuoteModel
from models.quote import *

# Utility
from utility import *

# Mathematics
from mathematics import *

# Matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Abstract: Model storing stock info and historical prices.

class Portfolio:

    def __init__(self, query, quotes, name='Portfolio'):

        # Set properties
        self.__query = query
        self.__quotes = quotes
        self.__name = name
        self.__symbol_map = {}
        self.__total_assets = 0
        self.__expected_return = 0
        self.__covariance = 0

        # Update assets
        self.update_assets()

    ##
    #
    #   MARK: - UPDATERS
    #
    ##

    # update_assets:Void
    # NOTE: - Updates the total asset count and weights of each quote.
    def update_assets(self):
        self.__total_assets = 0
        self.__symbol_map = {}
        for quote in self.__quotes:
            self.__total_assets += quote.count
            self.__symbol_map[quote.symbol] = quote
        if self.__total_assets > 0:
            for quote in self.__quotes:
                quote.weight = quote.count / self.__total_assets
        else:
            for quote in self.__quotes:
                quote.weight = 0.0
        market_data = self.get_market_data_tuple()
        self.__expected_return = market_data[1]        # Set portfolio return
        self.__covariance = market_data[2]             # Set portfolio covariance

    ##
    #
    #   MARK: - CHECKERS
    #
    ##

    # is_symbol_in_portfolio:Boolean
    # param symbol:String => A string stock symbol.
    def is_symbol_in_portfolio(self, symbol):
        return symbol in self.__symbol_map

    # is_symbol_in_portfolio:Boolean
    # param symbol:String => A string stock symbol.
    def get_quote_from_portfolio(self, symbol):
        return self.__symbol_map[symbol] if self.is_symbol_in_portfolio(symbol) else None

    ##
    #
    #   MARK: - SETTERS
    #
    ##

    # add_quote:Void
    # param quote:Quote => A quote object to add to the portfolio. Overwrites existing quotes.
    def add_quote(self, quote):
        for i, q in enumerate(self.__quotes):
            if q.symbol == quote.symbol:
                self.__quotes[i].count += quote.count
                self.update_assets()
                return
        self.__quotes.append(quote)
        self.update_assets()

    # remove_quote:Void
    # param quoteOrSymbol:Quote => A quote object or symbol string to remove from the portfolio, if it exists.
    def remove_quote(self, quote_or_symbol):
        for i, q in enumerate(self.__quotes):
            if (isinstance(quote_or_symbol, Quote) and q.symbol == quote.symbol) or quote_or_symbol == q.symbol:
                if isinstance(quote_or_symbol, Quote) and quote_or_symbol.count > self.__quotes[i].count:
                    self.__quotes[i].count -= quote_or_symbol.count
                else:
                    self.__quotes.remove(i)
                self.update_assets()
                return

    # set_name:Void
    # param quotes:[Quote] => A list of quote objects to set.
    def set_quotes(self, quotes):
        self.__quotes = quotes
        self.update_assets()

    # set_name:Void
    # param name:String => The name of the portfolio.
    def set_name(self, name):
        self.__name = name

    ##
    #
    #   MARK: - GETTERS
    #
    ##

    # get_quotes:[Quote]
    # Returns a list of quote objects in the portfolio.
    def get_quotes(self):
        return self.__quotes

    # get_symbols:[String]
    # Returns a list of symbols in the portfolio.
    def get_symbols(self):
        return list(map(lambda quote: quote.symbol, self.__quotes))

    # get_expected_return:[Quote]
    # Returns a float percentage for the return of this portfolio.
    def get_expected_return(self):
        return self.__expected_return

    # get_covariance:[Quote]
    # Returns the float covariance of this portfolio.
    # NOTE: - If > 0, the stocks in this portfolio are interrelated. Otherwise, not.
    def get_covariance(self):
        return self.__covariance

    # get_history:[String:[Price]]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns Map of symbols to lists of Price models.
    def get_history(self, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        historicals = {}
        for quote in self.__quotes:
            historicals[quote.symbol] = list(map(lambda price: price, self.get_symbol_history(quote.symbol, interval, span, bounds)))
        return historicals

    # get_history_tuple:([String:[Float:Price]], [Float])
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns Tuple containing: (map of symbols to map of float timestamps to Price models, list of all times in historicals map).
    def get_history_tuple(self, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        historicals = {}
        times = {}
        time_list = []
        for quote in self.__quotes:
            hist_map = {}
            hist_array = list(map(lambda price: price, self.get_symbol_history(quote.symbol, interval, span, bounds)))
            for price in hist_array:
                hist_map[price.time] = price
                if price.time not in times:
                    times[price.time] = True
            historicals[quote.symbol] = hist_map
        for time in times:
            time_list.append(time)
        time_list = sorted(time_list)
        return (historicals, time_list)

    # get_history_tuples:[[(time, open, close, high, low)]]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns List of price tuples with the time, volume, open, close, high, low for each time in the interval.
    def get_history_tuples(self, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        history = self.get_history(interval, span, bounds)
        for symbol in history:
            history[symbol] = [ quote.as_tuple() for quote in history[quote] ]
        return history

    # get_symbol_history:[Price]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns List of Price models with the time, volume, open, close, high, low for each time in the interval.
    def get_symbol_history(self, symbol, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        historicals = self.__query.get_history(symbol, interval, span, bounds)['historicals']
        historicals = list(map(lambda h: Price(Utility.datetime_to_float(Utility.iso_to_datetime(h['begins_at'])), float(h['open_price']), float(h['close_price']), float(h['high_price']), float(h['low_price'])), historicals))
        return historicals

    # get_symbol_history_map:[Float:Price]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns Map of float timestamps to prices for the given symbol.
    def get_symbol_history_map(self, symbol, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        historicals = self.__query.get_history(symbol, interval, span, bounds)['historicals']
        historicals = list(map(lambda h: Price(Utility.datetime_to_float(Utility.iso_to_datetime(h['begins_at'])), float(h['open_price']), float(h['close_price']), float(h['high_price']), float(h['low_price'])), historicals))
        history = {}
        for price in historicals:
            history[price.time] = price
        return history

    # get_portfolio_history:[Price]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns Map of Price model symbols to price tuples.
    def get_portfolio_history(self, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        portfolio_history = {}
        for quote in quotes:
            portfolio_history[quote.symbol] = quote.price.as_tuple()
        return portfolio_history

    # get_market_data_tuple:(dataFrame, float, float, [float], [float])
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns A tuple containing (dataFrame, float, float, [float], [float]).
    def get_market_data_tuple(self, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):

        # Create dataFrame with times as rows, symbols as columns, and close prices as data
        historicals = self.get_history(interval, span, bounds)
        times = []
        close_prices = []
        weights = []
        market_days = 0
        for quote in self.__quotes:
            t = []
            close_prices = []
            for price in historicals[quote.symbol]:
                if len(times) is 0:
                    t.append(price.time)
                close_prices.append(price.close)
            if len(times) is 0:
                times = t
                time_filled = True
                market_days = len(times)
            historicals[quote.symbol] = close_prices
            weights.append(quote.weight)
        df = pd.DataFrame(historicals)
        df.index = times

        # Calculate the returns for the given data
        returns = Math.get_returns(df, df.shift(1))

        # Portfolio's return
        portfolio_stats = self.get_portfolio_statistics(weights, returns)
        portfolio_return = portfolio_stats[0]
        portfolio_covariance = portfolio_stats[1]

        return (
            df,
            portfolio_return,
            portfolio_covariance,
            returns,
            weights
        )

    # get_portfolio_statistics:(float, float)
    # param weights:[float] => List of weights per quote, in order.
    # param returns:[float] => List of returns per quote, in order.
    # returns A tuple containing (portfolio_return, portfolio_covariance).
    def get_portfolio_statistics(self, weights, returns):
        returns_mean = returns.mean()
        returns_cov = returns.cov()
        market_days = len(returns)
        portfolio_return = np.sum(returns.mean()*weights)*market_days
        portfolio_covariance = np.sqrt(np.dot(np.transpose(weights), np.dot(returns.cov()*market_days, weights)))
        return (portfolio_return, portfolio_covariance)

    ##
    #
    #   MARK: - PORTFOLIO ANALYSIS
    #
    ##

    # sharpe_optimization:([Quote], float, float)
    # NOTE: - Optimizes according to the sharp ratio with the Markowitz Model.
    # Returns A tuple with list of quotes with quantities that would produce the optimal portfolio for the given symbols, optimized return, and optimized covariance.
    def sharpe_optimization(self):
        quote_count = len(self.__quotes)

        market_data = self.get_market_data_tuple()
        returns = market_data[3]
        market_days = len(returns)
        portfolio_return = market_data[1]
        portfolio_covariance = market_data[2]
        weights = [ quote.weight for quote in self.__quotes ]

        def min_sharpe_function(weights, returns):
            cur_stats = self.get_portfolio_statistics(weights, returns)
            return -cur_stats[0]/cur_stats[1]

        # Optimization
        constraints = ({ 'type': 'eq', 'fun': lambda x: np.sum(x) - 1 })
        bounds = tuple((0, 1) for x in range(quote_count))

        optimized_weights = optimize.minimize(fun=min_sharpe_function, x0=weights, args=returns, method='SLSQP', bounds=bounds, constraints=constraints)['x'].round(3)

        optimized_quotes = []
        for i, weight in enumerate(optimized_weights):
            optimized_quotes.append(Quote(self.__quotes[i], weight*100, weight))

        optimized_stats = self.get_portfolio_statistics(optimized_weights, returns)
        optimized_return = optimized_stats[0]
        optimized_covariance = optimized_stats[1]

        return (
            optimized_quotes,
            optimized_return,
            optimized_covariance
        )

    ##
    #
    #   MARK: - PLOTTING
    #
    ##

    # plot_historicals:Void(static)
    # param historicals:String => Raw dictionary returned from get_history(...) method in __query.
    # param is_candlestick_chart:Boolean => If true, plots a candlestick plot. Else, plots a line plot.
    # param legend_on:Boolean => If true, shows the legend. Else, hides the legend.
    def plot_historicals(self, is_candlestick_chart = True, legend_on = True):

        # Set Pandas properties
        pd.options.display.max_columns = 3000
        pd.options.display.max_rows = 3000

        historicals_list = self.get_history_tuples()

        colors = [Utility.get_random_hex() for historicals in historicals_list]

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(bottom=0.2)

        legend = []

        # Plot closes
        for i, historicals in enumerate(historicals_list):
            if is_candlestick_chart:
                mpf.candlestick_ochl(ax, historicals, width=0.1, colorup=colors[i], colordown=colors[i])
            else:
                closes = list(map(lambda quote: quote[2], historicals))
                dates = list(map(lambda quote: quote[0], historicals))
                ax.plot(dates, closes, colors[i])
            legend.append(mpatches.Patch(color=colors[i], label=self.__quotes[i].symbol))

        # Set legend
        if legend_on:
            plt.legend(handles=legend)

        for label in ax.xaxis.get_ticklabels():

            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(10))
            ax.grid(True)

            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title(self.__name)
            plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)

            label.set_rotation(45)

        plt.show()

# Anthony Krivonos
# Nov 9th, 2018
# src/models/price.py

# Imports
import sys

# Pandas
import pandas as pd

# NumPy
import numpy as np

# Enums
from enums import *

# Math
from math import exp

# PriceModel
from models.price import *

# Utility
from utility import *

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
        self.__total_assets = 0

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
        for quote in self.__quotes:
            self.__total_assets += quote.count
        if self.__total_assets > 0:
            for quote in self.__quotes:
                quote.weight = quote.count / self.__total_assets
        else:
            for quote in self.__quotes:
                quote.weight = 0.0

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
                self.__quotes[i] = quote
                self.update_assets()
                return
        self.__quotes.append(quote)
        self.update_assets()

    # remove_quote:Void
    # param quoteOrSymbol:Quote => A quote object or symbol string to remove from the portfolio, if it exists.
    def remove_quote(self, quote_or_symbol):
        for i, q in enumerate(self.__quotes):
            if (isinstance(quote_or_symbol, Quote) && q.symbol == quote.symbol) or quote_or_symbol == q.symbol:
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



    # get_history:[[Price]]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns List of Price models with the time, volume, open, close, high, low for each time in the interval.
    def get_history_tuples(self, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        historicals = []
        for quote in self.__quotes:
            historicals.append(list(map(lambda price: price.as_tuple(), self.get_symbol_history(quote.symbol, interval, span, bounds))))
        return historicals

    # get_symbol_history:[Price]
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns List of Price models with the time, volume, open, close, high, low for each time in the interval.
    def get_symbol_history(self, symbol, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        historicals = self.__query.get_history(symbol, interval, span, bounds)['historicals']
        historicals = list(map(lambda h: Price(mpl.dates.date2num(Utility.iso_to_datetime(h['begins_at'])), float(h['open_price']), float(h['close_price']), float(h['high_price']), float(h['low_price'])), historicals))
        return historicals

    # get_symbol_history_data:DataFrame
    # param symbol:String => String symbol of the instrument.
    # param interval:Span => Time in between each value. (default: DAY)
    # param span:Span => Range for the data to be returned. (default: YEAR)
    # param bounds:Span => The bounds to be included. (default: REGULAR)
    # returns Pandas data frame with Price properties mapped by time.
    def get_symbol_history_data(self, symbol, interval = Span.DAY, span = Span.YEAR, bounds = Bounds.REGULAR):
        history = np.array(list(map(lambda price: price.values_as_array(), self.get_symbol_history(symbol, interval, span, bounds))))
        return pd.DataFrame(history, columns=Price.props_as_array(), index=None)

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

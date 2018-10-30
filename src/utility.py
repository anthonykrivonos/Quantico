# Anthony Krivonos
# Oct 29, 2018
# src/factory.py

# Abstract: Utility methods for Quantico.

# Imports
import sys
import re, datetime

# Matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_finance as mpf

from enum import Enum

# Utility Methods
class Utility:

    @staticmethod
    def iso_to_datetime(dateString):
        return datetime.datetime(*map(int, re.split('[^\d]', dateString)[:-1]))

    # get_close_quadruple:(time, open, close, high, low) (static)
    # param quoteDict:String => A single quote dictionary returned from get_history(...)['historicals'] in Query.
    # returns A quadruple containing (time, open, close, high, low).
    @staticmethod
    def get_quote_quadruple(quoteDict):
        return (mpl.dates.date2num(Utility.iso_to_datetime(quoteDict['begins_at'])), float(quoteDict['open_price']), float(quoteDict['close_price']), float(quoteDict['high_price']), float(quoteDict['low_price']))

    # plot_historicals:Void (static)
    # param historicals:String => Raw dictionary returned from get_history(...) method in Query.
    # param isCandleStick:Boolean => If true, plots a candlestick plot. Else, plots a line plot.
    @staticmethod
    def plot_historicals(historicals, isCandleStick = True):
        quotes = list(map(lambda quote: Utility.get_quote_quadruple(quote), historicals['historicals']))

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(bottom=0.2)

        if isCandleStick:
            mpf.candlestick_ochl(ax, quotes, width=0.1, colorup="#20CE99", colordown="#F4542F")
        else:
            closes = list(map(lambda quote: quote[2], quotes))
            dates = list(map(lambda quote: quote[0], quotes))
            ax.plot(dates, closes)

        for label in ax.xaxis.get_ticklabels():

            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(10))
            ax.grid(True)

            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title(historicals['symbol'])
            plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)

            label.set_rotation(45)

        plt.show()

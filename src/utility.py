# Anthony Krivonos
# Oct 29, 2018
# src/factory.py

# Abstract: Utility methods for Quantico.

# Imports
import sys
import re, datetime
from time import sleep
import threading

# Matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_finance as mpf

# Pandas
import pandas as pd
import pandas_market_calendars as mcal

# NumPy
import numpy as np

# Enums
from enums import *

# Utility Methods
class Utility:

    # log:String
    # param message:String => Message to log.
    # NOTE: Prints a log message with time.
    @staticmethod
    def log(message):
        print(str(Utility.now_datetime64()) + ": " + message)

    # get_date_string:String
    # param date:datetime => Date to be converted into a string.
    # returns The date as a formatted string YYYY-MM-dd.
    @staticmethod
    def get_date_string(date):
        return date.strftime('%Y-%m-%d')

    # now_datetime64:datetime64
    # returns The current date as a datetime64.
    @staticmethod
    def now_datetime64():
        return np.datetime64(datetime.datetime.now())

    # today_date_string:String
    # returns The current date as a formatted string YYYY-MM-dd.
    @staticmethod
    def today_date_string():
        return Utility.get_date_string(datetime.datetime.today())

    # tomorrow_date_string:datetime
    # returns Tomorrow's date as a formatted string YYYY-MM-dd.
    @staticmethod
    def tomorrow_date_string():
        return Utility.get_date_string(datetime.date.today() + datetime.timedelta(days=1))

    # iso_to_datetime:datetime
    # param dateString:String => An ISO-formatted date string.
    # returns A datetime object correlating with the inputted dateString.
    @staticmethod
    def iso_to_datetime(dateString):
        return datetime.datetime(*map(int, re.split('[^\d]', dateString)[:-1]))

    # get_close_quadruple:(time, open, close, high, low) (static)
    # param quoteDict:String => A single quote dictionary returned from get_history(...)['historicals'] in Query.
    # returns A quintuple containing (time, open, close, high, low).
    @staticmethod
    def get_quote_quintuple(quoteDict):
        return (mpl.dates.date2num(Utility.iso_to_datetime(quoteDict['begins_at'])), float(quoteDict['open_price']), float(quoteDict['close_price']), float(quoteDict['high_price']), float(quoteDict['low_price']))

    # get_close_quadruple:(time, open, close, high, low) (static)
    # param historicals:[String:Any] => A historicals dict from the Query class.
    # returns A list of quintuples containing (time, open, close, high, low).
    @staticmethod
    def get_quintuples_from_historicals(historicals):
        return list(map(lambda quote: Utility.get_quote_quintuple(quote), historicals['historicals']))

    # d64_to_datetime:datetime (static)
    # param dt64:datetime64 => A NumPy base 64 date.
    # returns A datetime object.
    @staticmethod
    def dt64_to_datetime(dt64):
        return datetime.datetime.fromtimestamp(dt64.astype('O')/1e9)

    # plot_historicals:Void (static)
    # param historicals:String => Raw dictionary returned from get_history(...) method in Query.
    # param is_candlestick_chart:Boolean => If true, plots a candlestick plot. Else, plots a line plot.
    @staticmethod
    def plot_historicals(historicals, is_candlestick_chart = True):
        quotes = Utility.get_quintuples_from_historicals(historicals)

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.subplots_adjust(bottom=0.2)

        if is_candlestick_chart:
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

    # sleep_then_execute:Void
    # param time:String|datetime => If string, must look like "hh:mm". Otherwise, a datetime to wait until.
    # param action:lambda Function => The function to execute once the waiting period is over.
    # param sec:Integer => The number of seconds until the sleep condition is checked again.
    # returns The executed function.
    @staticmethod
    def sleep_then_execute(time, action, sec = 60):
        Utility.set_interval(sec, lambda: action(), time, None)

    # execute_between_times:Void
    # param start_time:datetime|None => The datetime for the execution to begin.
    # param stop_time:datetime|None => The datetime for the execution to end.
    # param action:lambda Function => The function to execute on the secInterval before the time is reached.
    # param sec:Integer => The number of seconds until the sleep condition is checked again.
    @staticmethod
    def execute_between_times(start_time, stop_time, action, sec = 60):
        Utility.set_interval(sec, lambda: action(), start_time, stop_time)

    # set_interval:Timer
    # param sec:Integer => Number of seconds between each execution of action.
    # param action:lambda Function => The function to execute on the secInterval before the time is reached.
    # param start_time:datetime|None => The datetime for the interval to begin.
    # param stop_time:datetime|None => The datetime for the interval to end.
    @staticmethod
    def set_interval(sec, action, start_time = None, stop_time = None):
        def call_action():
            now = datetime.datetime.today()
            if start_time is not None and stop_time is not None:
                if start_time < now and stop_time >= now:
                    Utility.set_interval(sec, action, start_time, stop_time)
                    action()
                elif start_time > now:
                    Utility.set_interval(sec, action, start_time, stop_time)
                elif stop_time < now:
                    action()
            elif start_time is None:
                if stop_time is None:
                    action()
                elif stop_time >= now:
                    Utility.set_interval(sec, action, None, stop_time)
                    action()
            else:
                if start_time > now:
                    Utility.set_interval(sec, action, start_time, None)
                else:
                    action()
        t = threading.Timer(sec, call_action)
        t.start()
        return t

    # get_next_market_hours:(datetime, datetime)
    # returns Datetime tuple with (next_market_open_datetime, next_market_close_datetime)
    @staticmethod
    def get_next_market_hours(market = "NYSE"):
        calendar = mcal.get_calendar(market)
        schedule = calendar.schedule(Utility.today_date_string(), Utility.tomorrow_date_string())
        start_times = schedule['market_open'].values
        end_times = schedule['market_close'].values

        current_date = np.datetime64(datetime.datetime.now())

        if current_date < start_times[0]:
            start_time = start_times[0]
            end_time = end_times[0]
        else:
            start_time = start_times[1]
            end_time = end_times[1]

        return (Utility.dt64_to_datetime(start_time), Utility.dt64_to_datetime(end_time))

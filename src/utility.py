# Anthony Krivonos
# Oct 29, 2018
# src/factory.py

# Imports
import sys
import re, datetime
from time import sleep, time
import threading
from termcolor import colored
import random

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

# Abstract: Utility methods for Quantico.

class Utility:

    # log:Void
    # param message:String => Message to log.
    # NOTE: Prints a log message with time.
    # returns The output string.
    @staticmethod
    def log(message):
        output = str(Utility.now_datetime64()) + "L: " + message
        print(colored(output, 'blue'))
        return output

    # error:Void
    # param message:String => Message to log as an error.
    # NOTE: Prints an error message with time.
    # returns The output string.
    @staticmethod
    def error(message):
        output = str(Utility.now_datetime64()) + "E: " + message
        print(colored(output, 'red'))
        return output

    # warning:Void
    # param message:String => Message to log as a warning.
    # NOTE: Prints a warning message with time.
    # returns The output string.
    @staticmethod
    def warning(message):
        output = str(Utility.now_datetime64()) + "W: " + message
        print(colored(output, 'yellow'))
        return output

    # get_date_string:String
    # param date:datetime => Date to be converted into a string.
    # returns The date as a formatted string YYYY-MM-dd.
    @staticmethod
    def get_date_string(date):
        return date.strftime('%Y-%m-%d')

    # get_timestamp_string:String
    # param date:Float => Float timestamp to be converted into a string.
    # returns The date as a formatted string YYYY-MM-dd.
    @staticmethod
    def get_timestamp_string(date_float):
        return Utility.get_date_string(Utility.float_to_datetime(date_float))

    # now_timestamp:String
    # returns The timestamp for current time since epoch.
    @staticmethod
    def now_timestamp():
        return Utility.now_datetime().timestamp()

    # now_datetime:datetime
    # returns The current date as a datetime.
    @staticmethod
    def now_datetime():
        return datetime.datetime.now()

    # now_datetime64:datetime64
    # returns The current date as a datetime64.
    @staticmethod
    def now_datetime64():
        return np.datetime64(Utility.now_datetime())

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

    # next_week_date_string:datetime
    # returns Next week's date as a formatted string YYYY-MM-dd.
    @staticmethod
    def next_week_date_string():
        return Utility.get_date_string(datetime.date.today() + datetime.timedelta(days=7))

    # next_month_date_string:datetime
    # returns Next month's date as a formatted string YYYY-MM-dd.
    @staticmethod
    def next_month_date_string():
        today = datetime.date.today()
        try:
            return today.replace(month=today.month+1)
        except ValueError:
            if today.month == 12:
                return today.replace(year=today.year+1, month=1)
        return Utility.get_date_string(today + datetime.timedelta(days=30))


    # iso_to_datetime:datetime
    # param dateString:String => An ISO-formatted date string.
    # returns A datetime object correlating with the inputted dateString.
    @staticmethod
    def iso_to_datetime(dateString):
        return datetime.datetime(*map(int, re.split('[^\d]', dateString)[:-1]))

    # datetime_to_float:Float
    # param date_float:Float => datetime to convert into a float timestamp.
    # returns A float timestamp for the datetime.
    def datetime_to_float(date):
        return date.timestamp()

    # float_to_datetime:datetime
    # param date_float:Float => Float to convert into datetime.
    # returns A datetime represented by the float.
    def float_to_datetime(date_float):
        return datetime.datetime.fromtimestamp(date_float)

    # get_quote_quintuple:(time, open, close, high, low) (static)
    # param quoteDict:String => A single quote dictionary returned from get_history(...)['historicals'] in Query.
    # returns A quintuple containing (time, open, close, high, low).
    @staticmethod
    def get_quote_quintuple(quoteDict):
        return (mpl.dates.date2num(Utility.iso_to_datetime(quoteDict['begins_at'])), float(quoteDict['open_price']), float(quoteDict['close_price']), float(quoteDict['high_price']), float(quoteDict['low_price']))

    # get_quintuples_from_historicals:(time, open, close, high, low) (static)
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

    # sleep_then_execute:Void
    # param time:String|datetime => If string, must look like "hh:mm". Otherwise, a datetime to wait until.
    # param action:lambda Function => The function to execute once the waiting period is over.
    # param sec:Integer => The number of seconds until the sleep condition is checked again.
    # returns The executed function.
    @staticmethod
    def sleep_then_execute(time, action, sec = 60):
        Utility.set_interval(sec, lambda: action(), time, None)

    # execute_between_times:Void
    # param action:lambda Function => The function to execute on the secInterval before the time is reached.
    # param start_time:datetime|None => The datetime for the execution to begin.
    # param stop_time:datetime|None => The datetime for the execution to end.
    # param sec:Integer => The number of seconds until the sleep condition is checked again.
    @staticmethod
    def execute_between_times(action, start_time = None, stop_time = None, sec = 60):
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

    # get_next_market_hours:(datetime?, datetime?)
    # returns Datetime tuple with (next_market_open_datetime, next_market_close_datetime)
    @staticmethod
    def get_next_market_hours(market = "NYSE"):
        calendar = mcal.get_calendar(market)

        # NOTE: Get all market days between today and next month, in case of weekends, breaks, and holidays.
        schedule = calendar.schedule(Utility.today_date_string(), Utility.next_month_date_string())

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

    # get_random_hex:String
    # returns Returns a random hexidecimal value with leading pound symbol.
    @staticmethod
    def get_random_hex():
        rand = lambda: random.randint(0,255)
        return ('#%02X%02X%02X' % (rand(), rand(), rand()))

    # merge_dicts:Dict
    # param x:Dict => Arbitrary dictionary.
    # param y:Dict => Arbitrary dictionary.
    # returns Returns a new dictionary with contents of x and y merged.
    @staticmethod
    def merge_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    # set_file_from_dict:Void
    # param file_name:String => String name of the file to access.
    # param dict:Dict => Dictionary to set into file.
    @staticmethod
    def set_file_from_dict(file_name, dict):
        open(file_name, 'w').close()
        file = open(file_name, "w")
        for key, value in dict.items():
            file.write(Utility.get_file_dict_string(key, value) + "\n")
        file.close()

    # set_in_file:Void
    # param file_name:String => String name of the file to access.
    # param key:String => Key to set in file.
    # param value:String => Value to set in file.
    @staticmethod
    def set_in_file(file_name, key, value):
        written = False
        file = open(file_name, "r")
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.find(key, 0, line.find("=")) is not -1:
                lines[i] = Utility.get_file_dict_string(key, value) + "\n"
                written = True
        file.close()
        file = open(file_name, "w")
        for line in lines:
            file.write(line)
        if not written:
            file.write(Utility.get_file_dict_string(key, value) + "\n")
        file.close()

    # get_from_file:String
    # param file_name:String => String name of the file to access.
    # param key:String => Key to get from file.
    # returns Returns the found value for the given key or None.
    @staticmethod
    def get_from_file(file_name, key):
        file = open(file_name, "r")
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.find(key, 0, line.find("=")) is not -1:
                file.close()
                return line[line.find("=") + 1:len(line)]
        file.close()
        return None

    # get_file_as_dict:Dict
    # param file_name:String => String name of the file to access.
    # param key:String => Key to get from file.
    # returns Returns the found value for the given key or None.
    @staticmethod
    def get_file_as_dict(file_name):
        file = open(file_name, "r")
        file_dict = {}
        lines = file.readlines()
        for i, line in enumerate(lines):
            key = line[0:line.find("=")]
            value = line[line.find("=") + 1:len(line) - 1]
            file_dict[key] = value
        file.close()
        return file_dict

    # get_file_dict_string:String
    # param key:String => Key to turn into string.
    # param value:String => Value to turn into string.
    # returns Returns a simple string structure for storing a key value pair in a file.
    @staticmethod
    def get_file_dict_string(key, value):
        return key + "=" + value

# Anthony Krivonos
# Oct 29, 2018
# src/query.py

# Abstract: Offers query methods that call the Robinhood API and convert the returned objects into workable models.

# Imports
import sys
sys.path.append('ext_modules')

from Robinhood import Robinhood

# Query Class
class Query:

    # __init__:Void
    # param username:String => Username of the Robinhood user.
    # param password:String => Password for the Robinhood user.
    def __init__(self, username, password):
        self.trader = Robinhood()
        self.trader.login(username=username, password=password)

    # getInstrument:Void
    # param symbol:String => String symbol of the instrument to return.
    def getQuote(self, symbol):
        self.trader.quote_data(symbol)[0] or None


    # getInstrument:Void
    # param symbol:String => String symbol of the instrument to return.
    def getInstrument(self, symbol):
        self.trader.instruments(symbol)[0] or None
        print("Got instrument " + symbol + ".")

# my_trader =
# logged_in =
# stock_instrument = my_trader.instruments("GEVO")[0]
# quote_info = my_trader.quote_data("GEVO")
# buy_order = my_trader.place_buy_order(stock_instrument, 1)
# sell_order = my_trader.place_sell_order(stock_instrument, 1)

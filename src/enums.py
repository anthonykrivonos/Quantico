# Anthony Krivonos
# Oct 29, 2018
# src/query.py

# Import Enum
from enum import Enum

# Abstract: Collection of enums for query and Utility operations.

# Bounds Enum
class Side(Enum):
    BUY = 'buy'     # buy side
    SELL = 'sell'   # sell side

# Bounds Enum
class Bounds(Enum):
    REGULAR = 'regular'     # regular bounds
    EXTENDED = 'extended'   # extended bounds

# Option Enum
class Option(Enum):
    CALL = "call" # "call" order
    PUT = "put"   # "put" order

# Time Enum
class GoodFor(Enum):
    GOOD_FOR_DAY = "GFD"        # "GFD" time
    GOOD_TIL_CANCELED = "GTC"   # "GTC" time

# Time Enum
class Span(Enum):
    FIVE_MINUTE = "5minute"   # Five minute's time
    TEN_MINUTE = "10minute"   # Ten minute's time
    DAY = "day"               # 24 hours' time
    WEEK = "week"             # 7 days' time
    YEAR = "year"             # 365 days' time

# Tag Enum
class Tag(Enum):
    TOP_MOVERS = "top-movers"
    ETF = "etf"
    MOST_POPULAR = "100-most-popular"
    MUTUAL_FUND = "mutual-fund"
    FINANCE = "finance"
    CAP_WEIGHTED = "cap-weighted"
    INVESTMENT_OR_TRUST = "investment-trust-or-fund"
    HEALTHCARE = "healthcare"
    PHARMACEUTICAL = "pharmaceutical"
    MEDICAL = "medical"
    HEALTH = "health"
    MEDICAL_DEVICES = "medical-devices"
    MANUFACTURING = "manufacturing"
    TECHNOLOGY = "technology"
    US = "us"

# Quintuple Index
class Quintuple(Enum):
    TIME = 0
    OPEN = 1
    CLOSE = 2
    HIGH = 3
    LOW = 4

# Bounds Enum
class Emotion(Enum):
    POSITIVE = 1     # positive emotion
    NEUTRAL = 0      # neutral emotion
    NEGATIVE = -1    # negative emotion

# Events for algorithms
class Event(Enum):
    ON_MARKET_WILL_OPEN = 0
    ON_MARKET_OPEN = 1
    WHILE_MARKET_OPEN = 2
    ON_MARKET_CLOSE = 3
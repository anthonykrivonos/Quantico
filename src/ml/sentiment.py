# Anthony Krivonos
# Dec 6, 2018
# src/ml/sentiment.py

# Global Imports
import numpy as np
import math

# Local Imports
from utility import *
from enums import *

# Pandas
import pandas as pd

# TextBlob
from textblob import TextBlob, Word, Blobber

# Abstract: Offers sentiment analysis for given text.

class Sentiment():

    def __init__(self, text):
        self.text = text
        sentiment = self.get_sentiment(self.text)
        self.polarity = sentiment.polarity
        self.subjectivity = sentiment.subjectivity
        self.emotion = self.get_emotion(self.polarity)

    # Static Methods

    @staticmethod
    def get_sentiment(text):
        return TextBlob(text).sentiment

    @staticmethod
    def get_emotion(polarity):
        EMOTION_THRESHOLD = 0.2
        if polarity > EMOTION_THRESHOLD:
            return Emotion.POSITIVE
        elif polarity > -EMOTION_THRESHOLD:
            return Emotion.NEUTRAL
        return Emotion.NEGATIVE

    @staticmethod
    def props_as_array():
        return ['text', 'polarity', 'subjectivity', 'emotion']

    # Class Methods

    def __str__(self):
        return str(self.as_dict())

    def as_tuple(self):
        return (self.text, self.polarity, self.subjectivity, self.emotion)

    def as_dict(self):
        props = np.array(self.props_as_array())
        vals = np.array(self.values_as_array())
        count = len(props)
        dict = {}
        for i, prop in enumerate(props):
            dict[prop] = vals[i]
        return dict

    def values_as_array(self):
        return [self.text, self.polarity, self.subjectivity, self.emotion]
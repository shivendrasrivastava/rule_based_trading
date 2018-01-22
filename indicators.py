"""Implement technical indicators"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
from util import *
from event_analyzer import output_events_as_trades, plot_events


def get_momentum(price, window=5):
    """
    Calculates momentum indicator: momentum[t] = (price[t]/price[t-window]) - 1

    Parameters:
    price: Price, typically adjusted close price, series of a symbol
    window: Number of days to look back
    
    Returns: Momentum, series of the same size as input data
    """    
    momentum = pd.Series(np.nan, index=price.index)
    momentum.iloc[window:] = price.iloc[window:] / price.values[:-window] - 1
    return momentum


def get_sma_indicator(price, rolling_mean):
    """
    Calculates simple moving average indicator, i.e. price / rolling_mean

    Parameters:
    price: Price, typically adjusted close price, series of a symbol
    rolling_mean: Rolling mean of a series

    Returns: The simple moving average indicator
    """
    return price / rolling_mean - 1


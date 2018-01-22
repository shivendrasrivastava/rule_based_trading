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


def get_bollinger_bands(rolling_mean, rolling_std, num_std=2):
    """
    Calculate upper and lower Bollinger Bands

    Parameters:
    rolling_mean: Rolling mean of a series
    rolling_meanstd: Rolling std of a series
    num_std: Number of standard deviations for the bands

    Returns: Bollinger upper band and lower band
    """
    upper_band = rolling_mean + rolling_std * num_std
    lower_band = rolling_mean - rolling_std * num_std
    return upper_band, lower_band


def compute_bollinger_value(price, rolling_mean, rolling_std):
    """
    Output a value indicating how many standard deviations a price is from the mean

    Parameters:
    price: Price, typically adjusted close price, series of a symbol
    rolling_mean: Rolling mean of a series
    rolling_std: Rolling std of a series

    Returns:
    bollinger_val: the number of standard deviations a price is from the mean
    """

    bollinger_val = (price - rolling_mean) / rolling_std
    return bollinger_val


def plot_bollinger(symbol, sym_price, upper_band, lower_band, bollinger_val, num_std=1):
    """
    Plot Bollinger bands and value for a symbol

    Parameters:
    symbol: A symbol of interest
    sym_price: Price, typically adjusted close price, series of symbol
    upper_band: Bollinger upper band
    lower_band: Bollinger lower band
    bollinger_val: The number of standard deviations a price is from the mean
    num_std: Number of standard deviations for the bands

    Returns:
    Plot two subplots, one for the Adjusted Close Price and Bollinger bands, the other 
    for the Bollinger value
    """
    
    # Create 2 subplots
    # First subplot: symbol"s adjusted close price, rolling mean and Bollinger Bands
    f, ax = plt.subplots(2, sharex=True)
    ax[0].fill_between(upper_band.index, upper_band, lower_band, color="gray", alpha=0.4, 
        linewidth=2.0, label="Region btwn Bollinger Bands")
    ax[0].plot(sym_price, label=symbol + " Adjusted Close", color="b")
    ax[0].set_title("{} Adjusted Close with Bollinger Bands (num. of std = {})".format(
        symbol, num_std))
    ax[0].set_ylabel("Adjusted Close Price")
    ax[0].legend(loc="upper center")

    # Second subplot: the bollinger value
    ax[1].axhspan(-num_std, num_std, color="gray", alpha=0.4, linewidth=2.0,
        label="Region btwn {} & {} std".format(-num_std, num_std))
    ax[1].plot(bollinger_val, label=symbol + " Bollinger Value", color="b")
    ax[1].set_title("{} Bollinger Value)".format(symbol))
    ax[1].set_xlabel("Date")
    ax[1].set_ylabel("Bollinger Value")
    ax[1].set_xlim(bollinger_val.index.min(), bollinger_val.index.max())
    ax[1].legend(loc="upper center")
    plt.show()



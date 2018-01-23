"""Implement technical indicators"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import datetime as dt
from util import get_exchange_days, get_data, normalize_data


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


def plot_momentum(sym_price, sym_mom, title="Momentum Indicator", fig_size=(12, 6)):
    """
    Plot momentum and prices for a symbol

    Parameters:
    sym_price: Price, typically adjusted close price, series of symbol
    sym_mom: Momentum of symbol
    fig_size: Width and height of the chart in inches
    
    Returns:
    Plot momentum and prices on the sample plot with two scales
    """

    # Create two subplots on the same axes with different left and right scales
    fig, ax1 = plt.subplots()

    # The first subplot with the left scale: prices
    ax1.grid(linestyle='--')
    line1 = ax1.plot(sym_price.index, sym_price, label="Adjusted Close Price", color="b")
    ax1.set_xlabel("Date")
    # Make the y-axis label, ticks and tick labels match the line color
    ax1.set_ylabel("Adjusted Close Price", color="b")
    ax1.tick_params("y", colors="b")

    # The second subplot with the right scale: momentum
    ax2 = ax1.twinx()
    line2 = ax2.plot(sym_mom.index, sym_mom, label="Momentum", color="k", alpha=0.4)
    ax2.set_ylabel("Momentum", color="k")
    ax2.tick_params("y", colors="k")

    # Align gridlines for the two scales
    align_y_axis(ax1, ax2, .1, .1)

    # Show legend with all labels on the same legend
    lines = line1 + line2
    line_labels = [l.get_label() for l in lines]
    ax1.legend(lines, line_labels, loc="upper center")

    #Set figure size
    fig = plt.gcf()
    fig.set_size_inches(fig_size)

    plt.suptitle(title)
    plt.show()


def plot_bollinger(sym_price, upper_band, lower_band, bollinger_val, 
    num_std=1, title="Bollinger Indicator", fig_size=(12, 6)):
    """
    Plot Bollinger bands and value for a symbol

    Parameters:
    sym_price: Price, typically adjusted close price, series of symbol
    upper_band: Bollinger upper band
    lower_band: Bollinger lower band
    bollinger_val: The number of standard deviations a price is from the mean
    num_std: Number of standard deviations for the bands
    fig_size: Width and height of the chart in inches

    Returns:
    Plot two subplots, one for the Adjusted Close Price and Bollinger bands, the other 
    for the Bollinger value
    """
    
    # Create 2 subplots
    # First subplot: symbol"s adjusted close price, rolling mean and Bollinger Bands
    f, ax = plt.subplots(2, sharex=True)
    ax[0].fill_between(upper_band.index, upper_band, lower_band, color="gray", alpha=0.4, 
        linewidth=2.0, label="Region btwn Bollinger Bands")
    ax[0].plot(sym_price, label="Adjusted Close Price", color="b")
    ax[0].set_ylabel("Adjusted Close Price")
    ax[0].legend(loc="upper center")

    # Second subplot: the bollinger value
    ax[1].axhspan(-num_std, num_std, color="gray", alpha=0.4, linewidth=2.0,
        label="Region btwn {} & {} std".format(-num_std, num_std))
    ax[1].plot(bollinger_val, label="Bollinger Value", color="b")
    ax[1].set_xlabel("Date")
    ax[1].set_ylabel("Bollinger Value")
    ax[1].set_xlim(bollinger_val.index.min(), bollinger_val.index.max())
    ax[1].legend(loc="upper center")

    #Set figure size
    fig = plt.gcf()
    fig.set_size_inches(fig_size)

    plt.suptitle(title)
    plt.show()


def align_y_axis(ax1, ax2, minresax1, minresax2):
    """Sets tick marks of twinx axes to line up with 7 total tick marks

    ax1 and ax2 are matplotlib axes
    Spacing between tick marks will be a factor of minresax1 and minresax2
    from https://stackoverflow.com/questions/26752464/how-do-i-align-gridlines
    -for-two-y-axis-scales-using-matplotlib
    """

    ax1ylims = ax1.get_ybound()
    ax2ylims = ax2.get_ybound()
    ax1factor = minresax1 * 6
    ax2factor = minresax2 * 6
    ax1.set_yticks(np.linspace(ax1ylims[0],
                               ax1ylims[1] + (ax1factor -
                               (ax1ylims[1] - ax1ylims[0]) % ax1factor) %
                               ax1factor, 7))
    ax2.set_yticks(np.linspace(ax2ylims[0],
                               ax2ylims[1] + (ax2factor -
                               (ax2ylims[1] - ax2ylims[0]) % ax2factor) %
                               ax2factor, 7))

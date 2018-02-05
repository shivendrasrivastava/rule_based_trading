"""Implement Rule Based Strategy class using indicators"""

import numpy as np
import pandas as pd
import datetime as dt
from util import get_data
from marketsim import market_simulator
from indicators import get_momentum, get_sma_indicator, get_bollinger_bands, \
compute_bollinger_value, plot_momentum, plot_sma_indicator, plot_bollinger


class RuleBasedStrategy(object):

    def __init__(self):
        """Initialize a RuleBasedStrategy."""
        self.df_order_signals = pd.DataFrame()
        self.df_trades = pd.DataFrame()


    def trading_strategy(self, sym_price):
        """Create a dataframe of order signals that maximizes portfolio's return.

        Parameters:
        sym_price: The price series of a stock symbol of interest

        Returns:
        df_order_signals: A series that contains 1 for buy, 0 for hold and -1 for sell
        """

        # Get SMA indicator and generate signals
        sma_indicator = get_sma_indicator(sym_price, sym_price.rolling(window=30).mean())
        sma_signal = 1 * (sma_indicator < 0.0) + -1 * (sma_indicator > 0.0)
        
        # Get momentum indicator and generate signals
        momentum = get_momentum(sym_price, 40)
        mom_signal = -1 * (momentum < -0.07) + 1 * (momentum > 0.14)
        
        # Combine individual signals
        signal = 1 * ((sma_signal == 1) & (mom_signal == 1)) \
            + -1 * ((sma_signal == -1) & (mom_signal == -1))

        # Create an order series with 0 as default values
        self.df_order_signals = signal * 0

        # Keep track of net signals which are constrained to -1, 0, and 1
        net_signals = 0
        for date in self.df_order_signals.index:
            net_signals = self.df_order_signals.loc[:date].sum()

            # If net_signals is not long and signal is to buy
            if (net_signals < 1) and (signal.loc[date] == 1):
                self.df_order_signals.loc[date] = 1

            # If net_signals is not short and signal is to sell
            elif (net_signals > -1) and (signal.loc[date] == -1):
                self.df_order_signals.loc[date] = -1

        # On the last day, close any open positions
        if self.df_order_signals.sum() == -1:
            self.df_order_signals[-1] = 1
        elif self.df_order_signals.sum() == 1:
            self.df_order_signals[-1] = -1

        return self.df_order_signals

    

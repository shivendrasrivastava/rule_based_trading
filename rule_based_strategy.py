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

    
    def test_policy(self, symbol, start_date=dt.datetime(2008,1,1), 
        end_date=dt.datetime(2009,12,31), start_val=100000):
        """Test a trading policy for a stock wthin a date range and output a trades dataframe.

        Parameters:
        symbol: The stock symbol to act on
        start_date: A datetime object that represents the start date
        end_date: A datetime object that represents the end date
        start_val: Start value of the portfolio
        
        Returns:
        df_trades: A dataframe whose values represent trades for each day: +1000 indicating a
        BUY of 1000 shares, -1000 indicating a SELL of 1000 shares, and 0 indicating NOTHING
        """
        
        # Get stock data
        df_price = get_data([symbol], pd.date_range(start_date, end_date)).dropna()
        sym_price = df_price.iloc[:, 1]

        # Get order_signals using trading_strategy
        order_signals = self.trading_strategy(sym_price)

        # Remove 0 signals to make the "for" loop below run faster
        order_signals = order_signals[order_signals!=0.0]

        # Create a list of tuples of trades to be fed into a DataFrame constructor
        trades = []
        for date in order_signals.index:
            if order_signals.loc[date] == 1:
                trades.append((date, symbol, "BUY", 1000))
            elif order_signals.loc[date] == -1:
                trades.append((date, symbol, "SELL", 1000))

        self.df_trades = pd.DataFrame(trades, columns=["Date", "Symbol", "Order", "Shares"])
        self.df_trades.set_index("Date", inplace=True)

        return self.df_trades


    def get_order_signals(self):
        """Get the ordder signals dataframe created by trading_strategy."""
        return self.df_order_signals


    def get_trades(self):
        """Get the trades dataframe created by test_policy."""
        return self.df_trades


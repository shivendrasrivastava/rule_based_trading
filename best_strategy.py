"""Implement Best Possible Strategy class. Assume that we can see the future, 
create a set of trades that represents the best a strategy could possibly do 
during a period. This is to give an idea of an upper bound on performance."""

import numpy as np
import pandas as pd
import datetime as dt
from util import get_exchange_days, get_data
from marketsim import market_simulator


class BestPossibleStrategy(object):

    def __init__(self):
        """Initializes a BestPossibleStrategy"""
        self.df_order_signals = pd.DataFrame()
        self.df_trades = pd.DataFrame()


    def trading_strategy(self, sym_price):
        """Creates a dataframe of order signals that maximizes portfolio's return

        Parameters:
        sym_price: The price series of a stock symbol of interest

        Returns:
        df_order_signals: A series that contains 1 for buy, 0 for hold and -1 for sell
        """

        # Get return for today's price relative to tomorrow's price
        # in order to decide whether to buy or sell today
        return_tday_vs_tmr = pd.Series(np.nan, index=sym_price.index)
        return_tday_vs_tmr[:-1]  = sym_price[:-1] / sym_price.values[1:] - 1 

        # Create an order signals dataframe: if today's return is negative and tomorrow 
        # is positive, buy today (order signal of 1) and vice versa (-1); if the sign of 
        # return doesn't change then hold the stock (0)
        return_signs = -1 * return_tday_vs_tmr.apply(np.sign)
        self.df_order_signals = return_signs.diff(periods=1) / 2
        self.df_order_signals[0] = return_signs[0]

        # On the last day, close any open positions
        if self.df_order_signals.sum() == -1:
            self.df_order_signals[-1] = 1
        elif self.df_order_signals.sum() == 1:
            self.df_order_signals[-1] = -1
        
        return self.df_order_signals


    
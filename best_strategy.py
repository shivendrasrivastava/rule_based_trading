"""Implement Best Possible Strategy class. Assume that we can see the future, 
create a set of trades that represents the best a strategy could possibly do 
during a period. This is to give an idea of an upper bound on performance."""

import numpy as np
import pandas as pd
import datetime as dt
from util import get_data
from marketsim import market_simulator


class BestPossibleStrategy(object):

    def __init__(self):
        """Initialize a BestPossibleStrategy."""
        self.df_order_signals = pd.DataFrame()
        self.df_trades = pd.DataFrame()


    def trading_strategy(self, sym_price):
        """Create a dataframe of order signals that maximizes portfolio's return.

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


if __name__ == "__main__":
    start_val = 100000
    symbol = "JPM"

    # In-sample or training period
    start_d = dt.datetime(2008, 1, 1)
    end_d = dt.datetime(2009, 12, 31)

    # Get benchmark data
    benchmark_prices = get_data([symbol], pd.date_range(start_d, end_d), 
        addSPY=False).dropna()

    # Create benchmark trades: buy 1000 shares of symbol, hold them till the last date
    df_benchmark_trades = pd.DataFrame(
        data=[(benchmark_prices.index.min(), symbol, "BUY", 1000), 
        (benchmark_prices.index.max(), symbol, "SELL", 1000)], 
        columns=["Date", "Symbol", "Order", "Shares"])
    df_benchmark_trades.set_index("Date", inplace=True)

    best_poss = BestPossibleStrategy()
    df_trades = best_poss.test_policy(symbol=symbol, start_date=start_d, end_date=end_d)
    
    # Retrieve performance stats via a market simulator
    print ("Performances during training period for {}".format(symbol))
    print ("Date Range: {} to {}".format(start_d, end_d))
    market_simulator(df_trades, df_benchmark_trades, start_val=start_val)


    # Out-of-sample or testing period
    start_d = dt.datetime(2010, 1, 1)
    end_d = dt.datetime(2011, 12, 31)
    best_poss = BestPossibleStrategy()
    best_poss.test_policy(symbol=symbol, start_date=start_d, end_date=end_d)

    # Retrieve performance stats via a market simulator
    print ("\nPerformances during testing period for {}".format(symbol))
    print ("Date Range: {} to {}".format(start_d, end_d))
    market_simulator(df_trades, df_benchmark_trades, start_val=start_val)
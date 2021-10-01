import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu


class SmartBetaIndex:

    def __init__(self, historic_prices, index_type, basket_size):
        self.index_type = index_type
        self.historic_prices = historic_prices
        self.basket_size = basket_size

    def calc_returns(self, time_period='M'):
        # takes in the historic prices defined at class level
        #  returns a dataframe of return by month

        price_shifted = self.historic_prices.shift(1)
        returns = (self.historic_prices - price_shifted) / price_shifted

        return returns.resample('M').sum()

    def convert_to_daily(self, df):
        # takes the weights that are calculated by month and forward fills them by day
        # this sets the weights for the next month for returns calculation

        start_date = df.index.min() - pd.DateOffset(day=1)
        end_date = df.index.max() + pd.DateOffset(day=31)
        dates = pd.date_range(start_date, end_date, freq='D')
        dates.name = 'date'
        df = df.reindex(dates, method='ffill')

        return df

    def momentum_calc(self, df):
        """
        Takes in dataframe of prices for a calculation
        Returns: dictionary of (data,stock):price

        """
        threshold = 0.00  # to force positve values
        stock_above_thresh = df.sum()[df.sum() > threshold].index

        momentum_stocks_dict = {}
        last_time_period = df.index.max()

        momentum_stocks_dict[last_time_period] = df[stock_above_thresh].sum().nlargest(
            self.basket_size).to_dict()

        # calculate weightings by momentum
        momentum_weights_df = pd.DataFrame.from_dict(momentum_stocks_dict, orient='index').apply(
            lambda x: x / x.sum(), axis=1
        )

        return momentum_weights_df.stack().to_dict()

    def volatility_calc(self, df):
        """
        Takes in dataframe of volatity for a calculation
        Returns: dictionary of (data,stock):price

        """
        low_vol_stocks_dict = {}
        last_time_period = df.index.max()

        threshold = 0.00  # to force positve values
        stock_above_thresh = df.sum()[df.sum() > threshold].index

        low_vol_stocks_dict[last_time_period] = df[stock_above_thresh].sum().nsmallest(self.basket_size).to_dict()

        # calculates weights using volatility
        volatility_weights = pd.DataFrame.from_dict(low_vol_stocks_dict, orient='index').apply(
            lambda x: x / x.sum(), axis=1
        )

        return volatility_weights.stack().to_dict()


    def get_portfolio_weights(self, look_back_period, rebalance_frequency):
        # calculates the weights for the index

        # gets the dataset if using divs we just look at historic divs not historic

        returns_df = self.historic_prices.resample('M').sum()

        all_weights_monthly = pd.DataFrame(columns=returns_df.columns, index=returns_df.index)

        for time_period in range(look_back_period, len(returns_df), rebalance_frequency):

            start_period = time_period - look_back_period

            period_returns = returns_df.iloc[start_period:time_period]

            if self.index_type == 'momentum':
                period_weights = self.momentum_calc(period_returns)

            elif self.index_type == 'volatility':
                period_weights = self.volatility_calc(period_returns)

            for date_, stock in period_weights.keys():
                formated_date = (date_).to_pydatetime().strftime("%Y-%m-%d")

                all_weights_monthly.loc[formated_date, stock] = period_weights[(date_, stock)]

        all_weights_daily = self.convert_to_daily(all_weights_monthly.fillna(0))
        all_weights_daily = all_weights_daily.fillna(0)
        # removes the weekends
        return all_weights_daily[all_weights_daily.index.dayofweek < 5]
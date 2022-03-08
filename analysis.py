from datetime import datetime
import numpy as np
import pandas as pd
import file_io as IO
import finance

class Portfolio_Analysis:

    COL_TIMESTAMP = 'timestamp'
    COL_PRICE_PREFIX = 'price_'
    COL_RETURN_PREFIX = 'return_'

    def __init__(self, portfolio = {}):
        self.portfolio = portfolio
        self.results = {}
        self.coins = []

        self.df = None
        self.df_meta = None
        self.df_correl_matrix = None
        self.df_covar_matrix = None
        self.df_return = None

        self.portfolio_mean_ret = 0
        self.portfolio_std = 0

        self.analyse()

    def analyse(self):
        # Crypto data
        self.set_crypto_results()

        # Other assets data
        # self.set_assets_results()

        # Make DataFrames
        self.set_base_df()

        # Make Metadata
        self.set_metadata_df()

        # Matrices
        self.df_correl_matrix = self.df_return.corr()
        self.df_covar_matrix = self.df_return.cov()

        # Scalar values
        self.mean_return_p = finance.mean_return_p(self.df_meta['coins_per'], self.df_meta['return_mean'])
        self.standard_deviation_p = finance.standard_deviation_p(self.df_meta['coins_per'], self.df_covar_matrix)
        self.sharper_ratio = finance.sharper_ratio(self.mean_return_p, self.standard_deviation_p)

    # Vantage finance API. origin: 2022-02-24
    def correct_asset_time(self, x):
        return int(datetime.timestamp(datetime.strptime(x[2:], '%y-%m-%d')))

    def set_crypto_results(self):
        for coin in self.portfolio['crypto']:
            data = IO.read_asset(coin)

            timestamps = [*map(lambda x: datetime.fromtimestamp(x[0]), data)]
            prices = [*map(lambda x: x[1], data)]
            ln_return = finance.ln_return(prices)

            cols = [self.COL_TIMESTAMP, self.COL_PRICE_PREFIX + coin, self.COL_RETURN_PREFIX + coin]
            self.results[coin] = pd.DataFrame(zip(timestamps, prices, ln_return), columns=cols)

    # def set_assets_results(self):
    #     for asset in self.portfolio['asset']:
    #         current_asset = IO.read_asset(asset)['Time Series (Daily)']
        
    #         timestamps = np.array([*map(self.correct_asset_time, current_asset)])
    #         prices = np.array([*map(lambda x: current_asset[x]['4. close'], current_asset)]).astype(np.float)
    #         ln_return = finance.ln_return(prices)
        
    #         self.results[asset] = pd.DataFrame(zip(timestamps, prices, ln_return), columns = self.get_df_cols(asset))

    def set_base_df(self):
        self.coins = [coin for coin in self.portfolio['crypto']]

        for asset in self.results:
            if self.df is None: 
                self.df = self.results[asset]
            else: 
                self.df = self.df.merge(self.results[asset], on=self.COL_TIMESTAMP, how='inner')

        self.df_return = self.df.filter(regex=self.COL_RETURN_PREFIX)
        self.df = self.df.join((self.df_return - self.df_return.mean()).rename(columns=dict(
            zip(self.df_return.columns, ['excess_ret_' + coin for coin in self.coins]))))

    def set_metadata_df(self):
        coins_native = [self.portfolio['crypto'][coin]['native'] for coin in self.coins]
        coins_usd = [coins_native[i] * self.df[self.COL_PRICE_PREFIX + coin][0] for i, coin in enumerate(self.coins)]
        coins_per = coins_usd / np.sum(coins_usd)
        coins_last_close = [self.df[self.COL_PRICE_PREFIX + coin][0] for coin in self.coins]

        std = self.df_return.std()
        mean = self.df_return.mean()
        # mean absolute deviation = 1/N Sum( |xi − m(X)| )
        absolute_deviation = abs(self.df.filter(regex='excess_ret_')).sum() / self.df.count()[0]

        data = [coins_native, coins_last_close, coins_usd, coins_per, std, mean, absolute_deviation]
        cols = ['coins_native', 'coins_last_close', 'coins_usd', 'coins_per', 'return_std', 'return_mean', 'absolute_deviation']
        self.df_meta = pd.DataFrame(data, cols, self.coins).T

from datetime import datetime
import numpy as np
import pandas as pd
import file_io as IO
import finance

class Portfolio_Analysis:

    COL_TIMESTAMP = 'timestamp'
    COL_PRICE_PREFIX = 'price_'
    COL_RETURN_PREFIX = 'return_'
    COL_EXCESS_RETURN_PREFIX = 'excess_ret_'

    def __init__(self, portfolio = {}):
        self.portfolio = portfolio
        self.raw_results = {}
        self.assets = []

        self.df = None
        self.df_meta = None
        self.df_correl_matrix = None
        self.df_covar_matrix = None
        self.df_return = None

        self.portfolio_mean_ret = 0
        self.portfolio_std = 0

        self.analyse()

    def analyse(self):
        # Make DataFrames
        self.set_base_df()

        # Make Metadata
        self.set_metadata_df()

        # Matrices
        self.df_correl_matrix = self.df_return.corr()
        self.df_covar_matrix = self.df_return.cov()

        # Scalar values
        self.mean_return_p = finance.mean_return_p(self.df_meta['assets_per'], self.df_meta['return_mean'])
        self.standard_deviation_p = finance.standard_deviation_p(self.df_meta['assets_per'], self.df_covar_matrix)
        self.sharper_ratio = finance.sharper_ratio(self.mean_return_p, self.standard_deviation_p)

    def set_base_df(self):
        for asset in self.portfolio:
            data = IO.read_asset(asset)
            if data is None:
                continue
            self.assets.append(asset)

            timestamps = [*map(lambda x: datetime.fromtimestamp(x[0]), data)]
            prices = [*map(lambda x: x[1], data)]
            cols = [self.COL_TIMESTAMP, self.COL_PRICE_PREFIX + asset]
            self.raw_results[asset] = pd.DataFrame(zip(timestamps, prices), columns=cols)

            print(self.df)
            if self.df is None:
                self.df = self.raw_results[asset]
            else: 
                self.df = self.df.merge(self.raw_results[asset], on=self.COL_TIMESTAMP, how='inner')

        for asset in self.assets:
            ln_return = finance.ln_return(self.df[self.COL_PRICE_PREFIX + asset])
            self.df[self.COL_RETURN_PREFIX + asset] = pd.Series(ln_return)
        
        self.df = self.df[:-1]

        self.df_return = self.df.filter(regex=self.COL_RETURN_PREFIX)
        self.df = self.df.join((self.df_return - self.df_return.mean()).rename(columns=dict(
            zip(self.df_return.columns, [self.COL_EXCESS_RETURN_PREFIX + asset for asset in self.assets]))))

    def set_metadata_df(self):
        assets_native = [self.portfolio[asset]['native'] for asset in self.assets]
        assets_last_close = [self.df[self.COL_PRICE_PREFIX + asset][0] for asset in self.assets]
        assets_usd = [assets_native[i] * assets_last_close[i] for i, _ in enumerate(self.assets)]
        assets_per = assets_usd / np.sum(assets_usd)

        std = self.df_return.std()
        mean = self.df_return.mean()
        # mean absolute deviation = Sum( |xi − m(X)| ) * 1/N
        absolute_deviation = abs(self.df.filter(regex=self.COL_EXCESS_RETURN_PREFIX)).sum() / self.df.count()[0]

        data = [assets_native, assets_last_close, assets_usd, assets_per, std, mean, absolute_deviation]
        cols = ['assets_native', 'assets_last_close', 'assets_usd', 'assets_per', 'return_std', 'return_mean', 'absolute_deviation']
        self.df_meta = pd.DataFrame(data, cols, self.assets).T

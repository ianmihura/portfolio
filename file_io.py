import json

class IO:

    PORTFOLIO = 'portfolio.json'
    DATA_ROUTE = 'data/'

    def __init__(self):
        return

    @staticmethod
    def read_portfolio():
        f = open(IO.PORTFOLIO, 'r')
        portfolio = json.load(f)
        f.close()
        return portfolio

    @staticmethod
    def read_asset(asset):
        f = open(IO.DATA_ROUTE + asset, 'r')
        current_asset = json.load(f)
        f.close()
        return current_asset

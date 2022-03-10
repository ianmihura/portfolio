import json

PORTFOLIO = 'portfolio.json'
DATA_ROUTE = './data/'

def read_portfolio():
    f = open(PORTFOLIO, 'r')
    portfolio = json.load(f)
    f.close()
    return portfolio

def save_portfolio(new_portfolio):
    f = open(PORTFOLIO, 'w')
    json.dump(new_portfolio, f)
    f.close()

def read_asset(asset):
    f = open(f'{DATA_ROUTE}{asset}.json', 'r')
    current_asset = json.load(f)
    f.close()
    return current_asset

def save_asset(asset_key, asset_data):
    f = open(f'{DATA_ROUTE}{asset_key}.json', 'w')
    json.dump(asset_data, f)
    f.close()
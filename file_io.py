import json

PORTFOLIO = 'portfolio_a.json'
DATA_ROUTE = './data/'

def read_portfolio():
    try:
        f = open(PORTFOLIO, 'r')
        portfolio = json.load(f)
        f.close()
    except:
        portfolio = None
        print(f'Error reading file {PORTFOLIO}')
    
    return portfolio

def save_portfolio(new_portfolio):
    try:
        f = open(PORTFOLIO, 'w')
        json.dump(new_portfolio, f)
        f.close()
    except:
        print(f'Error saving portfolio file')

def read_asset(asset):
    try:
        f = open(f'{DATA_ROUTE}{asset}.json', 'r')
        current_asset = json.load(f)
        f.close()
    except:
        current_asset = None
        print(f'Error reading file {asset}')

    return current_asset

def save_asset(asset_key, asset_data):
    try:
        f = open(f'{DATA_ROUTE}{asset_key}.json', 'w')
        json.dump(asset_data, f)
        f.close()
    except:
        print(f'Error saving file {asset_key}')
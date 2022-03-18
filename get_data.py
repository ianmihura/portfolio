from concurrent.futures import process
from os import environ as env
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import requests
import file_io as IO
import argparse


# APIs
def get_api_coingecko(symbol, vs_currency):
    return f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart/range?vs_currency={vs_currency}&from=1609415616&to=2590526525'

def get_api_vantage(symbol):
    return f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={env["VANTAGE_API_KEY"]}'

def get_api_polygon_financials(symbol):
    return f'https://api.polygon.io/vX/reference/financials?ticker={symbol}&apiKey={env["POLYGON_API_KEY"]}'

def get_api_polygon_tickers():
    return f'https://api.polygon.io/v3/reference/tickers?active=true&sort=ticker&order=asc&apiKey={env["POLYGON_API_KEY"]}'

def get_api_polygon_metadata(symbol):
    return f'https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={env["POLYGON_API_KEY"]}'

def get_api_yahoo_market():
    return f'https://yfapi.net/v6/finance/quote/marketSummary?lang=en&region=US'

def get_api_yahoo_recommendations(symbol):
    return f'https://yfapi.net/v6/finance/recommendationsbysymbol/{symbol}'

def get_api_yahoo_metadata(symbol):
    return f'https://yfapi.net/v11/finance/quoteSummary/{symbol}?lang=en&modules=defaultKeyStatistics%2CassetProfile%2CsummaryDetail%2CfinancialData%20%2CfundProfile'


# Formatting raw input
# Vantage finance API. origin: 2022-02-24
def correct_vantage_time(x):
    return int(datetime.timestamp(datetime.strptime(x[2:], '%y-%m-%d')))

# Coin Gecko API. origin: 1643932800000
def correct_crypto_time(x):
    return int(datetime.timestamp(datetime.fromtimestamp(x[0]/1000).replace(hour=0)))

def format_coingecko(jraw):
    data = jraw['prices']
    timestamps = [*map(correct_crypto_time, data)]
    prices = [*map(lambda x: x[1], data)]
    z_data = [*zip(timestamps, prices)]
    z_data.reverse()
    return z_data

def format_vantage(jraw):
    data = jraw['Time Series (Daily)']
    timestamps = [correct_vantage_time(x) for x in data]
    prices = [float(data[x]['4. close']) for x in data]
    z_data = [*zip(timestamps, prices)]
    return z_data


# Interface to save data
def save_market():
    try:
        api_url = get_api_yahoo_market()
        raw = requests.get(api_url, headers={"x-api-key": env['YAHOO_API_KEY']})

        IO.save_asset('market', raw.json())
        print('Market data -- Query successful')
    except:
        print('Market data -- Query fail')
        print(raw.json())

def save_asset_metadata(asset, asset_api_id):
    try:
        api_url = get_api_yahoo_metadata(asset_api_id)
        raw = requests.get(api_url, headers={"x-api-key": env['YAHOO_API_KEY']})

        IO.save_asset(f'{asset}.meta', raw.json())
        print(asset, '-- Metadata -- Query successful')
    except:
        print(asset, '-- Metadata -- Query fail')
        print(raw.json())

def save_asset_recommend(asset, asset_api_id):
    try:
        api_url = get_api_yahoo_recommendations(asset_api_id)
        raw = requests.get(api_url, headers={"x-api-key": env['YAHOO_API_KEY']})

        IO.save_asset(f'{asset}.rec', raw.json())
        print(asset, '-- Recommendations -- Query successful')
    except:
        print(asset, '-- Recommendations -- Query fail')
        print(raw.json())


def save_asset(asset, asset_api_id, type):
    try:
        if type == 'crypto':
            api_url = get_api_coingecko(asset_api_id, 'usd')
            raw = requests.get(api_url)
            data = format_coingecko(raw.json())
        elif type == 'equity':
            api_url = get_api_vantage(asset_api_id)
            raw = requests.get(api_url)
            data = format_vantage(raw.json())
            
        IO.save_asset(asset, data)
        print(asset, '-- Price -- Query successful')
    except:
        print(asset, '-- Price -- Query fail')
        print(raw.json())

def process_json(json):
    if json:
        IO.PORTFOLIO = json

    portfolio = IO.read_portfolio()
    for asset in portfolio:
        asset_data = portfolio[asset]
        save_asset(asset, asset_data['api_id'], asset_data['type'])
        save_asset_metadata(asset, asset_data['api_id'])
    save_market()

def process_asset(asset):
    
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', type=str)
    parser.add_argument('-a', '--asset', type=str)

    args = parser.parse_args()

    if args.asset:
        process_asset(args.asset)
    else:
        process_json(args.json)

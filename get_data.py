from os import environ as env
from dotenv import load_dotenv
from datetime import datetime
import requests
import file_io as IO
import json

load_dotenv()
PORTFOLIO = 'portfolio.json'

def get_api_coingecko(symbol, vs_currency):
    return f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart/range?vs_currency={vs_currency}&from=1609415616&to=2590526525'

def get_api_vantage(symbol):
    return f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={env["VANTAGE_API_KEY"]}'

def get_api_polygon_financials(symbol):
    return f'https://api.polygon.io/vX/reference/financials?ticker={symbol}&apiKey={env["POLYGON_API_KEY"]}'

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

def save_asset(asset, asset_api_id, type):
    if type == 'crypto':
        api_url = get_api_coingecko(asset_api_id, 'usd')
        raw = requests.get(api_url)
        data = format_coingecko(raw.json())
    elif type == 'equity':
        api_url = get_api_vantage(asset_api_id)
        raw = requests.get(api_url)
        data = format_vantage(raw.json())

    IO.save_asset(asset, data)
    print(asset, '-- Query successful')

def main():
    portfolio = IO.read_portfolio()
    for asset in portfolio:
        asset_data = portfolio[asset]
        save_asset(asset, asset_data['api_id'], asset_data['type'])

if __name__ == '__main__':
    main()
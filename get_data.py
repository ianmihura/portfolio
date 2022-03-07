from os import environ as env
from dotenv import load_dotenv
from datetime import datetime
import requests
import file_io as IO

load_dotenv()
PORTFOLIO = 'portfolio.json'


def get_api_coingecko(symbol, vs_currency):
    return f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart/range?vs_currency={vs_currency}&from=1609415616&to=2590526525'


def get_api_vantage(symbol):
    return f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={env["VANTAGE_API_KEY"]}'


# Vantage finance API. origin: 2022-02-24
def correct_asset_time(x):
    return int(datetime.timestamp(datetime.strptime(x[2:], '%y-%m-%d')))


# Coin Gecko API. origin: 1643932800000
def correct_crypto_time(x):
    return int(datetime.timestamp(datetime.fromtimestamp(x[0]/1000).replace(hour=0)))


def format_crypto(jraw):
    data = jraw['prices']
    timestamps = [*map(correct_crypto_time, data)]
    prices = [*map(lambda x: x[1], data)]
    return [*zip(timestamps, prices)].reverse()


def main():
    portfolio = IO.read_portfolio()

    for coin in portfolio['crypto']:
        value = portfolio['crypto'][coin]
        api_url = get_api_coingecko(value['api_id'], 'usd')
        raw = requests.get(api_url)
        data = format_crypto(raw.json())
        IO.save_asset(coin, data)
    
    # loop assets


if __name__ == '__main__':
    main()
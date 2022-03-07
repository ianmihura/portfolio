https = require('https')
fs = require('fs')
require('dotenv').config()

const PORTFOLIO = "portfolio.json"

const API_COINGECKO = (symbol, vs_currency) => `https://api.coingecko.com/api/v3/coins/${symbol}/market_chart/range?vs_currency=${vs_currency}&from=1609415616&to=2590526525`
const API_VANTAGE = symbol => `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${symbol}&outputsize=full&apikey=${process.env.VANTAGE_API_KEY}`

const http_call = function(key, api_url) {
    https.get(api_url, resp => {
        let data = ''
        resp.on('data', chunk => { data += chunk })
        resp.on('end', () => {
            fs.writeFile(`.\\data\\${key}`, data, err => {
                if (err)
                    console.log(`${key} error`, err)
                else
                    console.log(`${key} query executed successfully`)
            })
        })
    })
}

fs.readFile(PORTFOLIO, 'utf8', (err, raw) => {
    if (err) return console.log('Error reading file', err)

    const portfolio_json = JSON.parse(raw)

    // Crypto
    for (const [key, value] of Object.entries(portfolio_json.crypto))
        http_call(key, API_COINGECKO(value.api_id, 'usd'))

    // Other assets
    for (const [key, value] of Object.entries(portfolio_json.asset))
        http_call(key, API_VANTAGE(value.api_id))
        // portfolio_json.asset.forEach(key => { http_call(key, API_VANTAGE(key)) })
})

// BTCETH - calc prices faster
http_call('ethbtc', API_COINGECKO('bitcoin', 'eth'))
    // SPY
http_call('spy', API_VANTAGE('SPY'))
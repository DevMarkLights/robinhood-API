from flask import Blueprint, jsonify
import yfinance as yf
import numpy as np
import time

options = Blueprint('getOptions', __name__)

@options.route('/ticker/options/<ticker>')
def getOptions(ticker: str):
    stock = yf.Ticker(ticker)
    price = stock.fast_info.last_price
    if price is None:
        return {'error':'invalid ticker'}
    
    filterBy=0

    if price < 20:
        filterBy=4
    elif price > 20 and price < 50:
        filterBy=6
    elif price > 50 and price < 100:
        filterBy=10
    elif price > 100 and price < 200:
        filterBy=15
    else:
        filterBy=20
    
  
    expirations = stock.options
    first_expiration = expirations[0]
    
    options = stock.option_chain(first_expiration)

    calls = options.calls
    puts = options.puts

    filtered_puts = puts[puts['strike'] < price + filterBy]
    filtered_puts = filtered_puts[filtered_puts['strike'] > price - filterBy]
    putsWith2_return={}

    # get puts with a 2% return
    for index, row in filtered_puts.iterrows():
        price2 = row['strike']
        bid = row['bid']
        ret = bid/price2
        inTheMoney = row['inTheMoney']
        if ret > .02:
            ret = ret*100
            putsWith2_return[price2] = {'premium':'$'+str(bid*100),'return':'%'+str(round(ret,4)),'collateral':'$'+str(price2*100),'inTheMoney': inTheMoney}
    
    filtered_calls = calls[calls['strike'] < price+filterBy]
    filtered_calls = filtered_calls[filtered_calls['strike'] > price - filterBy]

    puts_iv = filtered_puts['impliedVolatility'].dropna()
    puts_iv = puts_iv.mean()

    calls_iv = filtered_calls['impliedVolatility'].dropna()
    calls_iv = calls_iv.mean()

    avg_iv = max(puts_iv,calls_iv)
    avg_iv = round(avg_iv,2)
    avg_iv = avg_iv * 100
    
    return jsonify({'Symbol':ticker,"current price":price,"IV":avg_iv, 'puts':putsWith2_return})

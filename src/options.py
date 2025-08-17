from flask import Blueprint, jsonify, request
import yfinance as yf
import yahooquery as yq
import numpy as np
import time
from scipy.stats import norm
from datetime import datetime

options = Blueprint('getOptions', __name__)

@options.get('/ticker/options/<ticker>')
def getOptions(ticker: str):
    stock = yf.Ticker(ticker)
    if stock.fast_info.open is None:
        return {'error':'invalid ticker'}
    
    price = stock.fast_info.last_price
    filterBy = filterOptions(price)

  
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
        strikePrice = row['strike']
        bid = row['bid']
        ret = bid/strikePrice
        inTheMoney = row['inTheMoney']
        if ret > .02:
            ret = ret*100
            putsWith2_return[strikePrice] = {'premium':'$'+str(round((bid*100),2)),'return':'%'+str(round(ret,4)),'collateral':'$'+str(strikePrice*100),'inTheMoney': inTheMoney}
    
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


@options.post('/ticker/options/<ticker>')
def postOptions(ticker: str):
    req = request.get_json()
    rot = req['rot'] / 100
    selectedExpiration = req['timestamp']

    stock = yf.Ticker(ticker)
    if stock.fast_info.open is None:
        return {'error':'invalid ticker'}
    
    price = stock.fast_info.last_price
    expirations = stock.options
    expiry = None
    options=None

    if selectedExpiration == "":
        options = stock.option_chain(expirations[0])
        expiry = datetime.strptime(expirations[0], "%Y-%m-%d")
    else:
        options = stock.option_chain(selectedExpiration)
        expiry = datetime.strptime(selectedExpiration,"%Y-%m-%d")

    # expiry = datetime.strptime(options_dates[0], "%Y-%m-%d")
    T = (expiry - datetime.today()).days / 365

    calls = options.calls
    puts = options.puts
    filterBy = filterOptions(price)

    filtered_puts = puts[puts['strike'] < price]
    filtered_puts = filtered_puts[filtered_puts['strike'] > price - filterBy]

    filtered_calls = calls[calls['strike'] < price+filterBy]
    filtered_calls = filtered_calls[filtered_calls['strike'] > price]

    putsWithRequestReturn=rotOptions(filtered_puts,rot,price,'put',T)
    callsWithRequestReturn=rotOptions(filtered_calls,rot,price,'call',T)

    puts_iv = filtered_puts['impliedVolatility'].dropna()
    puts_iv = round(puts_iv.mean()*100,3)

    calls_iv = filtered_calls['impliedVolatility'].dropna()
    calls_iv = round(calls_iv.mean()*100,3)
    avg_iv = max(puts_iv,calls_iv)
   

    return jsonify({'symbol':ticker,"avgIV":avg_iv,"currentPrice":round(price,2),"expirations":expirations,"rot":rot,"putsIV":puts_iv,"puts":putsWithRequestReturn,"callsIV":calls_iv,"calls":callsWithRequestReturn})


def filterOptions(price):
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
    
    return filterBy

def rotOptions(options,rot,price,type,T):

    optionsROT=[]
    for index, row in options.iterrows():
        strikePrice = row['strike']
        bid = row['bid']
        ret = bid/strikePrice
        inTheMoney = row['inTheMoney']
        iv = round(row['impliedVolatility']*100,2)
        if ret > rot:
            delta = round(black_scholes_delta(price,strikePrice,T,.05,row['impliedVolatility'],type),3)
            ret = ret*100
            optionsROT.append({'strike':strikePrice,'premium':'$'+str(round((bid*100),2)),'return':'%'+str(round(ret,2)),'collateral':'$'+str(strikePrice*100),'inTheMoney': inTheMoney,"iv":iv,"delta":delta})
        
        
    return optionsROT

def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
    """
    S: Current stock price
    K: Strike price
    T: Time to expiration in years
    r: Risk-free interest rate (annualized)
    sigma: Volatility (annualized)
    option_type: 'call' or 'put'
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    
    if option_type == 'call':
        return norm.cdf(d1)
    elif option_type == 'put':
        return norm.cdf(d1) - 1
    else:
        raise ValueError("option_type must be 'call' or 'put'")

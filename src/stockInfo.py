from flask import Blueprint, jsonify
import yfinance as yf
import numpy as np
import time

stockInfo = Blueprint('getStockInfo', __name__)

@stockInfo.route('/ticker/stockInfo/<ticker>')
def getStockInfo(ticker: str):
    stock = yf.Ticker(ticker)
    price = stock.fast_info.last_price
    if price is None:
        return {'error':'invalid ticker'}
    
    analyst_targets={}
    analyst_targets['high'] = stock.analyst_price_targets.get('high')
    analyst_targets['low'] = stock.analyst_price_targets.get('low')
    analyst_targets['current'] = stock.analyst_price_targets.get('current')
    analyst_targets['mean'] = stock.analyst_price_targets.get('mean')
    analyst_targets['median'] = stock.analyst_price_targets.get('median')

    earnings_estimate={}
    if len(stock.analyst_price_targets) > 0:
        earnings_estimate = stock.earnings_estimate['avg'].values.tolist()


    shortName = stock.history_metadata['shortName'] if 'shortName' in stock.history_metadata else ""
    longName = stock.history_metadata['longName'] if 'longName' in stock.history_metadata else ""

    summary={}
    summary['exchange'] = stock.fast_info.exchange
    summary['day_high'] = round(stock.fast_info.day_high,2)
    summary['day_low'] = round(stock.fast_info.day_low,2)
    summary['last_price'] = round(price)
    summary['shortName'] = shortName
    summary['longName'] = longName
    
    earnings_date=None
    if 'Earnings Date' in stock.calendar:
        earnings_date = str(stock.calendar['Earnings Date'][0])

    beta = None
    if 'beta' in stock.info and stock.info['beta'] is not None:
        beta = stock.info['beta']
    

    dividends={}
    divYield=None
    if 'yield' in stock.info:
        divYield = stock.info['yield']

    if stock.dividends.empty:
        dividends['dividends'] = 'no dividends'
    else:
        dates = stock.dividends[::-1].index
        amounts = stock.dividends[::-1].values

        for index,value in enumerate(dates):
            dividends[str(value).split(" ")[0]] = amounts[index]

    schedule = None
    if divYield is None and not dividends:
        res = round(calculateDividendYield(dividends,price),2)
        divYield = res[0]
        schedule = res[1]
    else :
        res = round(calculateDividendYield(dividends,price),2)
        schedule = res[1]
    

    json = {'symbol':ticker,
            "currentPrice":round(price,2),
            "analystTargets":analyst_targets, 
            "earningsEstimate":earnings_estimate,
            "earningsDate": earnings_date,
            "summary":summary,
            "dividends":dividends,
            "beta": beta,
            "schedule": schedule,
            "divYield":divYield}

    return jsonify(json)


def calculateDividendYield(dividends,price):
    keys = list(dividends.keys())
    
    for index,key in enumerate(keys):
        if index == 2:
            currentDivMonth = int(keys[index-2].split('-')[1])
            prevDivMonth =  int(keys[index-1].split('-')[1])
            prevPrevDivMonth = int(key.split('-')[1])

            # check if weekly dividend
            if prevPrevDivMonth == prevDivMonth or prevDivMonth == currentDivMonth:
                dividend = float(dividends[keys[0]] * 52)
                return [round(dividend / price,2),"weekly"]

            if prevDivMonth - currentDivMonth == 1: # monthly
                dividend = float(dividends[keys[0]] * 12)
                return [round(dividend / price,2),"monthly"]
            else:                                   # quarterly
                dividend = float(dividends[keys[0]] * 4)
                return [round(dividend / price,2),"quartely"]


            break
        # prevKey = key
from flask import Blueprint, jsonify
import yfinance as yf
import yahooquery as yq
import numpy as np
import time
from scipy.stats import norm
from datetime import datetime
from cachetools import TTLCache

OHLC = Blueprint('getOHLC', __name__)
cache = TTLCache(maxsize=100, ttl=300)
INTERVAL_TO_PERIOD = {
    '5m': '60d',
    '15m': '60d',
    '1h': '730d',
    '1d': '10y'
}

@OHLC.get('/ticker/ohlc/<ticker>/<timeframe>')
def getOHLC(ticker: str, timeframe: str):
    cache_key = f"{ticker}:{timeframe}"
    now = time.time()
    if cache_key in cache:
        # entry = cache[cache_key]
        # if now - entry['timestamp'] < 300:  # 5 minutes
        return jsonify(cache[cache_key])
        
    ticker = yf.Ticker(ticker)
    df = ticker.history(period=INTERVAL_TO_PERIOD[timeframe], interval=timeframe)
    
    if df.empty:
        return jsonify({'success': False, 'data': [], 'count': 0}), 404
    
    df.index = df.index.strftime('%Y-%m-%dT%H:%M:%S')
    
    candles = df[['Open', 'High', 'Low', 'Close', 'Volume']].rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }).to_dict(orient='records')
    
    
    timestamps = df.index.tolist()
    for i, candle in enumerate(candles):
        candle['timestamp'] = timestamps[i]
    
    response = {
            'success': True,
            'ticker': ticker.ticker,
            'timeframe': timeframe,
            'count': len(candles),
            'data': candles,
            'timestamp': now
        }
    cache[cache_key] = response
    return jsonify(response)

@OHLC.get('/ticker/ohlc/<ticker>/<timeframe>/<interval>')
def getOHLCWithInterval(ticker: str, timeframe: str, interval: str):
    ticker = yf.Ticker(ticker)
    df = ticker.history(period=interval, interval=timeframe)
    
    if df.empty:
        return jsonify({'success': False, 'data': [], 'count': 0}), 404
    
    df.index = df.index.strftime('%Y-%m-%dT%H:%M:%S')
    
    candles = df[['Open', 'High', 'Low', 'Close', 'Volume']].rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }).to_dict(orient='records')
    
    
    timestamps = df.index.tolist()
    for i, candle in enumerate(candles):
        candle['timestamp'] = timestamps[i]
    
    return jsonify({
        'success': True,
        'ticker': ticker.ticker,
        'timeframe': timeframe,
        'count': len(candles),
        'data': candles
    })
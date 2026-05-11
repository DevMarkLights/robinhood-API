from flask import Blueprint, jsonify
import yfinance as yf
import yahooquery as yq
import numpy as np
import time
from scipy.stats import norm
from datetime import datetime

OHLC = Blueprint('getOHLC', __name__)

INTERVAL_TO_PERIOD = {
    '5m': '5d',
    '15m': '30d',
    '1h': '60d',
    '1d': '1y'
}

@OHLC.get('/ticker/ohlc/<ticker>/<timeframe>')
def getOHLC(ticker: str, timeframe: str):
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
    
    return jsonify({
        'success': True,
        'ticker': ticker.ticker,
        'timeframe': timeframe,
        'count': len(candles),
        'data': candles
    })
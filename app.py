# app.py
from flask import Flask, request, jsonify, Response

from src.options import options 
from src.stockInfo import stockInfo
from src.stockInfoMulti import stockInfoMulti
from src.ohlc import OHLC
from src.financialStatement import financialStatement
from cachetools import TTLCache
cache = TTLCache(maxsize=100, ttl=300)

app = Flask(__name__)
app.register_blueprint(options)
app.register_blueprint(stockInfo)
app.register_blueprint(stockInfoMulti)
app.register_blueprint(OHLC)
app.register_blueprint(financialStatement)

@app.before_request
def check_cache():
    if request.method == "GET" and request.full_path in cache:
        return jsonify(cache[request.full_path])

@app.after_request
def store_cache(response):
    if request.method == "GET" and response.status_code == 200:
        cache[request.full_path] = response.get_json()
    return response

# Add this
print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule)

@app.get("/")
def hello():
    return 'hello'

    

if __name__ == '__main__':
    # app.run(port=8080,debug=True)
    app.run(host='0.0.0.0', port=8081)



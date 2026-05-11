# app.py
from flask import Flask, request, jsonify, Response

from src.options import options 
from src.stockInfo import stockInfo
from src.stockInfoMulti import stockInfoMulti
from src.ohlc import OHLC

app = Flask(__name__)
app.register_blueprint(options)
app.register_blueprint(stockInfo)
app.register_blueprint(stockInfoMulti)
app.register_blueprint(OHLC)

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



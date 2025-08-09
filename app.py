# app.py
from flask import Flask, request, jsonify, Response

from src.options import options 
from src.stockInfo import stockInfo

app = Flask(__name__)
app.register_blueprint(options)
app.register_blueprint(stockInfo)


@app.get("/")
def hello():
    return 'hello'

    

if __name__ == '__main__':
    # app.run(port=8080,debug=True)
    app.run(host='0.0.0.0', port=8080)



# app.py
from flask import Flask, request, jsonify, Response
import robin_stocks.robinhood as robin_stocks

app = Flask(__name__)

mfa_code = {}

@app.post("/profileSummary")
def stockSummary():
    re=request
    
    if request.is_json:
        body=request.get_json()
        username = body.get('username')
        password = body.get('password')
        mfa_code = body.get('mfa_code')
        print(username)
        print(password)
        if mfa_code != "":
            user = mfa_code.get(username)
            mfa_code = user.get('mfaCode')
            robin_stocks.login(username='marklights899@gmail.com',password='MA1234Lights',expiresIn=10,by_sms=True,mfa_code=mfa_code)
            holdings = robin_stocks.build_holdings(with_dividends=True)
            del mfa_code[username]
            return {'data':holdings},200
        else:
            try:
                robin_stocks.login(username='marklights899@gmail.com',password='MA1234Lights',expiresIn=60,by_sms=True)
                holdings = robin_stocks.build_holdings(with_dividends=True)
                return {'data':holdings},200
            except:
                return jsonify({'message': 'MFA code required'}),200

    response = [{'error': 'invalid mime/type'},{'mime/type': 'must be application/json'}]
    return response


@app.post("/mfaCode")
def storeMfaCode():
    if request.is_json:
        body = request.get_json()
        username = body.get('username')
        password = body.get('password')
        mfaCode = body.get('mfaCode')
        mfa_code[username] = {
            'mfaCode': mfaCode,
            'password': password
        }
        return stockSummary()

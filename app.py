from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
from iqoptionapi.stable_api import IQ_Option
from time import time
from datetime import datetime

API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()
# velas = API.get_candles('EURUSD', (1 * 60), 5, time())
print(API.check_connect())
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains



pairs=['EURUSD','GBPUSD', 'AUDUSD', 'AUDJPY','EURJPY','USDJPY','GBPJPY','GBPAUD', 'AUDCAD','USDCHF','GBPCHF','CADJPY','EURCAD','USDCAD','CHFJPY' ,'EURGBP' , 'AUDCHF' ,'EURAUD' , 'EURCHF','GBPCAD']


def calculate_candle_properties(candle):
    """Calculate wick lengths, body size, and price action strength."""
    upper_wick = candle['max'] - max(candle['open'], candle['close'])
    lower_wick = min(candle['open'], candle['close']) - candle['min']
    body_size = abs(candle['close'] - candle['open'])
    total_range = candle['max'] - candle['min'] + 1e-6  # Avoid zero division
    
    return {
        'upper_wick': upper_wick,
        'lower_wick': lower_wick,
        'body_size': body_size,
        'total_range': total_range,
        'color': 'green' if candle['close'] > candle['open'] else 'red',
        'buyer_pressure': lower_wick / total_range,
        'seller_pressure': upper_wick / total_range,
        'strength': body_size / total_range  # Measures candle dominance
    }

def analyze_volume_source(candles):
    """Determine if volume increase is due to buyers or sellers."""
    last_candle = candles[-1]
    prev_candle = candles[-2]
    
    upper_wick, lower_wick = calculate_candle_properties(last_candle)['upper_wick'], calculate_candle_properties(last_candle)['lower_wick']
    volume_increasing = last_candle['volume'] > prev_candle['volume']

    if volume_increasing:
        if upper_wick > lower_wick:  # Sellers caused the volume increase
            return "Sellers"
        elif lower_wick > upper_wick:  # Buyers caused the volume increase
            return "Buyers"
    
    return "Neutral"

def detect_momentum(candles):
    """Check if market momentum is aligning with price action."""
    recent_closes = [c['close'] for c in candles[-4:]]  # Last 4 closes
    up_trend = recent_closes[-1] > recent_closes[-2] > recent_closes[-3]
    down_trend = recent_closes[-1] < recent_closes[-2] < recent_closes[-3]
    
    return "UP" if up_trend else "DOWN" if down_trend else "NEUTRAL"

def detect_reversal(candles):
    """Identify possible reversals based on wick dominance."""
    last_candle = calculate_candle_properties(candles[-1])
    prev_candle = calculate_candle_properties(candles[-2])

    if last_candle['lower_wick'] > last_candle['body_size'] * 1.2 and prev_candle['lower_wick'] > prev_candle['body_size'] * 1.0:
        return "POSSIBLE UP REVERSAL"
    
    if last_candle['upper_wick'] > last_candle['body_size'] * 1.2 and prev_candle['upper_wick'] > prev_candle['body_size'] * 1.0:
        return "POSSIBLE DOWN REVERSAL"
    
    return "NO REVERSAL"

def predict_next_candle(candles):
    """Apply a multi-confirmation strategy for high-accuracy signals."""
    if len(candles) < 6:
        return "NO TRADE - Insufficient Data"

    last_candle = calculate_candle_properties(candles[-1])
    prev_candle = calculate_candle_properties(candles[-2])
    volume_source = analyze_volume_source(candles)
    momentum = detect_momentum(candles)
    reversal = detect_reversal(candles)

    # BUY SIGNAL (CALL)
    if (last_candle['buyer_pressure'] > last_candle['seller_pressure'] and
        prev_candle['buyer_pressure'] > prev_candle['seller_pressure'] and
        last_candle['lower_wick'] > last_candle['body_size'] * 0.6 and
        volume_source == "Buyers" and
        (momentum == "UP" or reversal == "POSSIBLE UP REVERSAL")):
        return "CALL"

    # SELL SIGNAL (PUT)
    if (last_candle['seller_pressure'] > last_candle['buyer_pressure'] and
        prev_candle['seller_pressure'] > prev_candle['buyer_pressure'] and
        last_candle['upper_wick'] > last_candle['body_size'] * 0.6 and
        volume_source == "Sellers" and
        (momentum == "DOWN" or reversal == "POSSIBLE DOWN REVERSAL")):
        return "PUT"

    return "NO TRADE"

################################################################################

def analyze_all_signals():
    API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
    API.connect()
    
    all_signals = {}
    for pair in pairs:
        # Get 100 candles for better pattern recognition
        velas = API.get_candles(pair, (1 * 60), 100, time())
        # velas5 = API.get_candles(pair, (2 * 60), 100, time())
        velas.pop() # remove last uncomplete candle data
        # velas5.pop() # remove last uncomplete candle data
        signal = predict_next_candle(velas)
        # signal5 = apply_cwrv_123_strategy(velas5)
        all_signals[pair] = signal 
        # if signal ==signal5 else 'NEUTRAL'
    
    return all_signals

@app.route("/")
def home():
    return jsonify({"message": "API is working!"})
# 
@app.route("/signal", methods=["GET"])
def get_signall():
    try:
        dir = analyze_all_signals()
        data={"signal": dir}
        return jsonify(data)
    
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

# @app.route("/candles", methods=["GET"])
# def get_candles():
#     try:
#         # Get timeframe parameter, default to 1
#         timeframe = int(request.args.get("timeframe", 1))
        
#         # Get specific pair parameter if it exists
#         specific_pair = request.args.get("pair", None)
        
#         API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
#         API.connect()
        
#         result = {}
        
#         # If specific pair is requested, return only that pair
#         if specific_pair:
#             velas = API.get_candles(specific_pair, (timeframe * 60), 100, time())
#             velas.pop()  # Remove last incomplete candle
#             result[specific_pair] = velas
#         else:
#             # Get candles for all pairs
#             for pair in pairs:
#                 velas = API.get_candles(pair, (timeframe * 60), 100, time())
#                 velas.pop()  # Remove last incomplete candle
#                 result[pair] = velas
        
#         return jsonify({"candles": result})
    
#     except Exception as e:
#         print(e)
#         return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

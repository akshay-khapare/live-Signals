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

# def predict_next_candle_direction(candles):
#     # Check if there are at least 3 candles to compare volumes
#     if len(candles) < 3:
#         return 'no_signal'
    
#     # Extract the last two candles
#     last_candle = candles[-1]  # Most recent candle
#     second_last_candle = candles[-2]  # Second-to-last candle
#     third_last_candle = candles[-3]  # Third-to-last candle for volume comparison
    
#     # Calculate wicks for the last candle
#     last_upper_wick = last_candle['max'] - max(last_candle['open'], last_candle['close'])
#     last_lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['min']
    
#     # Calculate wicks for the second-to-last candle
#     second_upper_wick = second_last_candle['max'] - max(second_last_candle['open'], second_last_candle['close'])
#     second_lower_wick = min(second_last_candle['open'], second_last_candle['close']) - second_last_candle['min']
    
#     # Determine candle directions (bullish or bearish)
#     last_is_bullish = last_candle['close'] > last_candle['open']
#     second_is_bullish = second_last_candle['close'] > second_last_candle['open']
    
#     # Check if candles are the same color
#     same_color = last_is_bullish == second_is_bullish
    
#     # Determine wick similarity
#     last_upper_dominant = last_upper_wick > last_lower_wick
#     second_upper_dominant = second_upper_wick > second_lower_wick
#     wicks_similar = (last_upper_dominant and second_upper_dominant) or \
#                     (not last_upper_dominant and not second_upper_dominant)
    
#     # Check volume validation or anomaly
#     volume_second_to_third = second_last_candle['volume'] - third_last_candle['volume']
#     volume_last_to_second = last_candle['volume'] - second_last_candle['volume']
#     # Validation: both increase or both decrease
#     validation = (volume_second_to_third > 0 and volume_last_to_second > 0) or \
#                  (volume_second_to_third < 0 and volume_last_to_second < 0)
#     # Anomaly: one increases, the other decreases
#     anomaly = (volume_second_to_third > 0 and volume_last_to_second < 0) or \
#               (volume_second_to_third < 0 and volume_last_to_second > 0)
    
#     # Apply the strategy
#     if same_color and wicks_similar:
#         if validation:
#             # Continuation: predict same direction as last candle
#             return "CALL" if last_is_bullish else "PUT"
#         elif anomaly:
#             # Reversal: predict opposite direction of last candle
#             return "PUT" if last_is_bullish else "CALL"
    
#     # If conditions are not met, return no signal
#     return 'no_signal'


# def is_bullish(candle):
#     return candle['close'] > candle['open']

# def is_bearish(candle):
#     return candle['close'] < candle['open']

# def get_upper_wick(candle):
#     return candle['max'] - max(candle['open'], candle['close'])

# def get_lower_wick(candle):
#     return min(candle['open'], candle['close']) - candle['min']

# def is_upper_wick_bigger(candle):
#     return get_upper_wick(candle) > get_lower_wick(candle)

# def is_lower_wick_bigger(candle):
#     return get_lower_wick(candle) > get_upper_wick(candle)

# def is_validation(candle1, candle2):
#     # Volume of 2nd and 3rd candle increasing or decreasing in same direction
#     return (candle2['volume'] > candle1['volume']) or (candle2['volume'] < candle1['volume'])

# def is_anomaly(candle1, candle2):
#     # Volume of 2nd and 3rd candle is abnormal (one increasing, one decreasing)
#     return not is_validation(candle1, candle2)

# def predict_next_candle_cwrv(candles):
#     if len(candles) < 3:
#         return 'NEUTRAL'  # Need at least 3 candles for most rules
    
#     candle1 = candles[-3]  # 3rd last candle
#     candle2 = candles[-2]  # 2nd last candle
#     candle3 = candles[-1]  # Last candle (most recent)

#     # # Rule 1: Concept 3 - Opposite Wicks ✅
#     # if (is_lower_wick_bigger(candle2) and is_upper_wick_bigger(candle3)) or \
#     #    (is_upper_wick_bigger(candle2) and is_lower_wick_bigger(candle3)):
#     #     if is_validation(candle2, candle3):
#     #         return "PUT" if is_bullish(candle3) else "CALL"  # Reversal
#         # elif is_anomaly(candle2, candle3):
#         #     return "CALL" if is_bullish(candle3) else "PUT"  # Continuation

#     # # Rule 1: Concept 4 - Opposite Wicks Color Change ✅
#     if ((is_lower_wick_bigger(candle2) and is_upper_wick_bigger(candle3)) or
#         (is_upper_wick_bigger(candle2) and is_lower_wick_bigger(candle3))) and \
#        (is_bullish(candle2) != is_bullish(candle3)):
#         # if is_validation(candle2, candle3):
#         #     return "CALL" if is_bullish(candle3) else "PUT"  # Continuation
#         if is_anomaly(candle2, candle3):
#             return "PUT" if is_bullish(candle3) else "CALL"  # Reversal

#     return 'NEUTRAL'  # No strategy matched



#     return '''None'''



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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

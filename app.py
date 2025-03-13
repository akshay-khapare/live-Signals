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
#             return 'CALL' if last_is_bullish else 'PUT'
#         elif anomaly:
#             # Reversal: predict opposite direction of last candle
#             return 'PUT' if last_is_bullish else 'CALL'
    
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
#     #         return 'PUT' if is_bullish(candle3) else 'CALL'  # Reversal
#         # elif is_anomaly(candle2, candle3):
#         #     return 'CALL' if is_bullish(candle3) else 'PUT'  # Continuation

#     # # Rule 1: Concept 4 - Opposite Wicks Color Change ✅
#     if ((is_lower_wick_bigger(candle2) and is_upper_wick_bigger(candle3)) or
#         (is_upper_wick_bigger(candle2) and is_lower_wick_bigger(candle3))) and \
#        (is_bullish(candle2) != is_bullish(candle3)):
#         # if is_validation(candle2, candle3):
#         #     return 'CALL' if is_bullish(candle3) else 'PUT'  # Continuation
#         if is_anomaly(candle2, candle3):
#             return 'PUT' if is_bullish(candle3) else 'CALL'  # Reversal

#     return 'NEUTRAL'  # No strategy matched



#     return None

def is_bullish(candle):
    """Checks if a candle is bullish (green)."""
    return candle['close'] > candle['open']

def is_bearish(candle):
    """Checks if a candle is bearish (red)."""
    return candle['close'] < candle['open']

def get_upper_wick_length(candle):
    """Calculates the upper wick length of a candle."""
    return candle['max'] - max(candle['open'], candle['close'])

def get_lower_wick_length(candle):
    """Calculates the lower wick length of a candle."""
    return min(candle['open'], candle['close']) - candle['min']

def get_candle_body_length(candle):
    """Calculates the body length of a candle."""
    return abs(candle['close'] - candle['open'])


def apply_cwrv_123_strategy(data):
    """
    Applies ONLY the CWRV 123 Official and Unofficial strategies as
    described in the PDF (Page 18).

    Args:
        data: A list of candle data (oldest to newest). Needs at least 3 candles.

    Returns:
        A string: "CALL", "PUT", or "NEUTRAL" indicating the predicted
                 direction of the next candle based on CWRV 123 rules.
                 Returns "NEUTRAL" if no pattern is found or insufficient data.
    """
    if len(data) < 3:
        return "NEUTRAL"

    candle_before_previous = data[-3]
    previous_candle = data[-2]
    current_candle = data[-1]

    # --- Official CWRV 123 Pattern (Marubozu) ---
    is_cwrv_123_official_pattern = False
    if is_bullish(candle_before_previous) and is_bullish(previous_candle) and is_bearish(current_candle) and current_candle['volume'] > previous_candle['volume']:  # Candle 3 volume high

        # Relaxed Marubozu check for candle 1 (less strict than before)
        is_marubozu_candle1 = (get_upper_wick_length(candle_before_previous) < get_candle_body_length(candle_before_previous) * 0.25 and
                               get_lower_wick_length(candle_before_previous) < get_candle_body_length(candle_before_previous) * 0.25) # Increased threshold to 0.25

        if is_marubozu_candle1:  # Official CWRV (Marubozu candle 1)
            is_cwrv_123_official_pattern = True
            return "CALL"  # Candle 4 will be Red (Binary option: PUT)


    # --- Unofficial CWRV 123 Pattern (Normal Candle) ---
    is_cwrv_123_unofficial_pattern = False
    if is_bearish(candle_before_previous) and is_bearish(previous_candle) and is_bullish(current_candle) and current_candle['volume'] > previous_candle['volume']:  # Candle 3 volume high

        is_normal_candle1 = get_candle_body_length(candle_before_previous) > 0  # Candle 1 is just a normal candle (has a body)

        if is_normal_candle1:  # Unofficial CWRV (Normal candle 1)
            is_cwrv_123_unofficial_pattern = True
            return "PUT"  # Candle 4 will be Green (Binary option: CALL)

    return "NEUTRAL"  # No CWRV 123 pattern found













































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
        signal = apply_cwrv_123_strategy(velas)
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

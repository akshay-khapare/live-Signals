from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
from iqoptionapi.stable_api import IQ_Option
from time import time
from datetime import datetime
import math

API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
API.connect()
# velas = API.get_candles('EURUSD', (1 * 60), 5, time())
print(API.check_connect())
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

def analyze_cwrv_strategy_high_accuracy(candles):
    """
    Analyzes candle data based on a HIGH ACCURACY CWRV strategy, focusing on perfect entries.
    Generates fewer, higher-confidence signals by applying stricter criteria based on CWRV Rules 1 and 3.

    Args:
        candles: A list of candle data dictionaries.

    Returns:
        A dictionary containing the signal, rule, volume status, and candle properties.
    """

    if len(candles) < 3:
        return {'signal': 'NEUTRAL', 'rule': 'Not enough candles'}

    current_candle = candles[-1]
    prev_candle = candles[-2]
    prev_prev_candle = candles[-3]

    current_color = 'verde' if current_candle['close'] > current_candle['open'] else 'vermelha' if current_candle['close'] < current_candle['open'] else 'doji'
    prev_color = 'verde' if prev_candle['close'] > prev_candle['open'] else 'vermelha' if prev_candle['close'] < prev_candle['open'] else 'doji'

    def calculate_wick_length(candle):
        candle_range = candle['max'] - candle['min']
        if candle_range <= 0:
            return 0, 0
        upper_wick = candle['max'] - max(candle['open'], candle['close'])
        lower_wick = min(candle['open'], candle['close']) - candle['min']
        return (upper_wick / candle_range) * 100, (lower_wick / candle_range) * 100

    current_upper_wick_perc, current_lower_wick_perc = calculate_wick_length(current_candle)
    prev_upper_wick_perc, prev_lower_wick_perc = calculate_wick_length(prev_candle)

    previous_volumes = [prev_prev_candle['volume'], prev_candle['volume']]
    avg_volume = np.mean(previous_volumes) if previous_volumes else 0
    volume_validation_threshold = 1.25 # Stricter validation: 25% above average
    volume_anomaly_threshold = 0.75  # Stricter anomaly: 25% below average

    volume_status = "neutral"
    if current_candle['volume'] > avg_volume * volume_validation_threshold:
        volume_status = "validation"
    elif current_candle['volume'] < avg_volume * volume_anomaly_threshold:
        volume_status = "anomaly"

    signal = 'NEUTRAL'
    rule_applied = 'None'

    # --- HIGH ACCURACY Rule 1:  Very Strict Similar Wicks (Concept-1 & Concept-2) ---
    if current_color == prev_color and current_color != 'doji': # Rule 1 still applies to same color (non-doji)

        if current_upper_wick_perc > 60 and prev_upper_wick_perc > 60: # VERY Long Upper Wicks (> 60% - much stricter)
            rule_applied = 'Rule 1 HA - Very Long Similar Upper Wicks'
            if volume_status == 'validation': # Volume VALIDATION is KEY for high accuracy continuation
                signal = 'PUT' if current_color == 'vermelha' else 'CALL' # Continuation
            elif volume_status == 'anomaly': # Volume ANOMALY for high accuracy reversal
                signal = 'CALL' if current_color == 'vermelha' else 'PUT' # Reversal

        elif current_lower_wick_perc > 60 and prev_lower_wick_perc > 60: # VERY Long Lower Wicks (> 60% - much stricter)
            rule_applied = 'Rule 1 HA - Very Long Similar Lower Wicks'
            if volume_status == 'validation': # Volume VALIDATION is KEY for high accuracy continuation
                signal = 'CALL' if current_color == 'verde' else 'PUT' # Continuation
            elif volume_status == 'anomaly': # Volume ANOMALY for high accuracy reversal
                signal = 'PUT' if current_color == 'verde' else 'CALL' # Reversal


    # --- HIGH ACCURACY Rule 3:  Very Strict Small Wicks with Anomaly (Concept-2 - Reversal focus) ---
    # Rule 3 is made VERY selective and focused on REVERSAL signals with VOLUME ANOMALY for high accuracy
    if signal == 'NEUTRAL':  # Apply Rule 3 ONLY if Rule 1 (High Accuracy) didn't give a signal
        if current_upper_wick_perc < 10 and current_lower_wick_perc < 10: # EXTREMELY Small wicks (< 10% - very strict)
            rule_applied = 'Rule 3 HA - Extremely Small Wicks - Anomaly Reversal'
            if volume_status == 'anomaly': # Volume ANOMALY is KEY for high accuracy REVERSAL in Rule 3
                signal = 'PUT' if current_color == 'verde' else 'CALL' # Reversal signal based on volume anomaly with small wicks
            # Validation with small wicks is intentionally ignored in this HIGH ACCURACY version to reduce signals


    return signal
    # {'signal': signal, 'rule': rule_applied, 'volume_status': volume_status,
    #         'current_color': current_color, 'prev_color': prev_color,
    #         'current_upper_wick_perc': current_upper_wick_perc, 'current_lower_wick_perc': current_lower_wick_perc,
    #         'prev_upper_wick_perc': prev_upper_wick_perc, 'prev_lower_wick_perc': prev_lower_wick_perc}

def calculate_wick_length(candle):
    candle_range = candle['max'] - candle['min']
    if candle_range <= 0:
        return 0, 0
    upper_wick = candle['max'] - max(candle['open'], candle['close'])
    lower_wick = min(candle['open'], candle['close']) - candle['min']
    return (upper_wick / candle_range) * 100, (lower_wick / candle_range) * 100

def get_volume_validation_cwrv(prev_candle, current_candle):
    """
    Implements CWRV's definition of volume validation and anomaly.

    Args:
        prev_candle: The previous candle (2nd candle).
        current_candle: The current candle (3rd candle).

    Returns:
        "validation", "anomaly", or "neutral".
    """
    if prev_candle['cor'] == 'verde':  # 2nd candle is green
        if current_candle['volume'] > prev_candle['volume'] and current_candle['cor'] == 'verde':
            return "validation"  # Increasing volume, same direction
        elif current_candle['volume'] < prev_candle['volume'] and current_candle['cor'] == 'verde':
          return "validation"
        elif current_candle['volume'] > prev_candle['volume'] and current_candle['cor'] == 'vermelha':
            return "anomaly"  # Increasing volume, opposite direction.
        elif current_candle['volume'] < prev_candle['volume'] and current_candle['cor'] == 'vermelha':
            return "anomaly"
        else:
            return "neutral" #added for high accuracy no trade condition.

    elif prev_candle['cor'] == 'vermelha':  # 2nd candle is red
        if current_candle['volume'] > prev_candle['volume'] and current_candle['cor'] == 'vermelha':
            return "validation"  # Increasing volume, same direction.
        elif current_candle['volume'] < prev_candle['volume'] and current_candle['cor'] == 'vermelha':
            return "validation"
        elif current_candle['volume'] > prev_candle['volume'] and current_candle['cor'] == 'verde':
            return "anomaly"    # Increasing volume, opposite direction.
        elif current_candle['volume'] < prev_candle['volume'] and current_candle['cor'] == 'verde':
            return "anomaly"
        else:
            return "neutral" #added for high accuracy

    else:  # 2nd candle is doji (handle as neutral or according to your preference)
        return "neutral"

def is_marubozu(candle, threshold=2):
    upper_wick_perc, lower_wick_perc = calculate_wick_length(candle)
    return upper_wick_perc <= threshold and lower_wick_perc <= threshold

def cwrv_predict_high_accuracy(data):
    """
    Predicts the next candle direction with high accuracy using CWRV rules.
    """
    if len(data) < 3:  # Need at least 3 candles for analysis
        return {'prediction': 'NEUTRAL', 'confidence': 0, 'rules_applied': ['Not enough data']}

    candles = []  # Add wick percentages and color
    for x in data:
        x.update({'cor': 'verde' if x['open'] < x['close']
                                else 'vermelha' if x['open'] > x['close'] else 'doji'})
        upper_wick, lower_wick = calculate_wick_length(x)
        x.update({'upper_wick_perc': upper_wick, 'lower_wick_perc': lower_wick})
        candles.append(x)

    current_candle = candles[-1]  # Most recent candle
    prev_candle = candles[-2]    # Second most recent candle
    prev_prev_candle = candles[-3] # Third most recent candle

    # CWRV Volume Validation/Anomaly (Corrected Implementation)
    volume_result = get_volume_validation_cwrv(prev_candle, current_candle)

    rules_applied = []
    prediction = 'NEUTRAL'
    confidence = 0.0  # Start with low confidence

    # --- High-Accuracy Rule 1: Similar Wicks (Concept 1) ---
    if prev_candle['cor'] == current_candle['cor']:
        # Strong Similar Upper Wicks
        if prev_candle['upper_wick_perc'] > 50 and current_candle['upper_wick_perc'] > 50  and prev_candle['lower_wick_perc'] < 15 and current_candle['lower_wick_perc'] < 15:
            rules_applied.append("Rule 1 - Strong Similar Upper Wicks")
            if volume_result == "validation":
                prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT'
                confidence = 0.9
            # No anomaly trade for high accuracy.

        # Strong Similar Lower Wicks
        elif prev_candle['lower_wick_perc'] > 50 and current_candle['lower_wick_perc'] > 50 and prev_candle['upper_wick_perc'] < 15 and current_candle['upper_wick_perc'] < 15:
            rules_applied.append("Rule 1 - Strong Similar Lower Wicks")
            if volume_result == "validation":
                prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT'
                confidence = 0.9
            # No anomaly trade for high accuracy

     # --- High-Accuracy Rule 1: One-Sided Wicks (Concept 2) ---
    if prediction == 'NEUTRAL': #check if already got signals from above rules
      if prev_candle['cor'] == current_candle['cor']:
        # Strong Upper Wick Only
        if prev_candle['upper_wick_perc'] > 60 and current_candle['upper_wick_perc'] > 60 and prev_candle['lower_wick_perc'] < 10 and current_candle['lower_wick_perc'] < 10:
            rules_applied.append("Rule 1 - Strong One-Sided Upper Wick")
            if volume_result == "validation":
                prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT'
                confidence = 0.9

        # Strong Lower Wick Only
        elif prev_candle['lower_wick_perc'] > 60 and current_candle['lower_wick_perc'] > 60 and prev_candle['upper_wick_perc'] < 10 and current_candle['upper_wick_perc'] < 10:
            rules_applied.append("Rule 1 - Strong One-Sided Lower Wick")
            if volume_result == "validation":
                prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT'
                confidence = 0.9


    # --- High-Accuracy Rule 1: Opposite Wicks (Concept 3) ---
    if prediction == 'NEUTRAL':
        if prev_candle['upper_wick_perc'] > 50 and current_candle['lower_wick_perc'] > 50:
            rules_applied.append("Rule 1 - Opposite Wicks (Down, Up)")
            if volume_result == "anomaly":  # Opposite logic for Opposite Wicks
                prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT'
                confidence = 0.9  # High confidence for strong anomaly
        elif prev_candle['lower_wick_perc'] > 50 and current_candle['upper_wick_perc'] > 50:
            rules_applied.append("Rule 1 - Opposite Wicks (Up, Down)")
            if volume_result == "anomaly":
                prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT'
                confidence = 0.9  # High confidence for strong anomaly

      # --- Rule 1: Opposite Wicks Colour Change ---
    if prediction == 'NEUTRAL':
        if prev_candle['cor'] != current_candle['cor']: #color change
            if prev_candle['upper_wick_perc'] > 50 and current_candle['lower_wick_perc'] > 50:
                rules_applied.append("Rule 1 - Opposite Wicks Colour Change (Down, Up)")
                if volume_result == "validation":  # Opposite logic for Opposite Wicks
                    prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT' #continue
                    confidence = 0.9

            elif prev_candle['lower_wick_perc'] > 50 and current_candle['upper_wick_perc'] > 50:
                rules_applied.append("Rule 1 - Opposite Wicks Colour Change (Up, Down)")
                if volume_result == "validation":
                    prediction = 'CALL' if current_candle['cor'] == 'verde' else 'PUT'
                    confidence = 0.9



    # --- High-Accuracy Rule 2: Color Change (Concepts 1 & 2) ---
    if prediction == 'NEUTRAL':
        if prev_prev_candle['cor'] != prev_candle['cor'] and prev_candle['cor'] != current_candle['cor']:
            rules_applied.append("Rule 2 - Strong Color Change")
            # Check for increasing volume of the *opposite* party.
            if prev_prev_candle['cor'] == 'verde': #previous candle was green
                if current_candle['volume'] > prev_candle['volume'] and current_candle['cor'] == 'vermelha':
                    prediction = 'PUT'  # Expect a red candle
                    confidence = 0.9
            elif prev_prev_candle['cor'] == 'vermelha':#previous candle was red
                if current_candle['volume'] > prev_candle['volume'] and current_candle['cor'] == 'verde':
                    prediction = 'CALL'  # Expect a green candle
                    confidence = 0.9


    # --- High-Accuracy Marubozu Followed by Confirmation ---
    if prediction == 'NEUTRAL':
      if is_marubozu(prev_candle) and not is_marubozu(current_candle): #check for prev candle
        rules_applied.append("Marubozu with Confirmation")
        if prev_candle['cor'] == 'verde': #previous candle marubozu and green
            if current_candle['cor'] == 'vermelha' and current_candle['volume'] > prev_candle['volume']:
                prediction = 'PUT'
                confidence = 0.95
        elif prev_candle['cor'] == 'vermelha':#previous candle marubozu and red
            if current_candle['cor'] == 'verde' and current_candle['volume'] > prev_candle['volume']:
                prediction = 'CALL'
                confidence = 0.95

      if is_marubozu(current_candle): #check current candle
        if current_candle['cor'] == 'verde':
            prediction = 'neutral'
            confidence = 0.8
        else:
            prediction = 'neutral'
            confidence = 0.8


    if not rules_applied:
        rules_applied.append("No High-Accuracy Rule Triggered")

    return prediction
    # {'prediction': prediction, 'confidence': confidence, 'rules_applied': rules_applied}

pairs=['EURUSD','GBPUSD', 'AUDUSD', 'AUDJPY','EURJPY','USDJPY','GBPJPY','GBPAUD', 'AUDCAD','USDCHF','GBPCHF','CADJPY','EURCAD','USDCAD','CHFJPY']
def analyze_all_signals():
    API = IQ_Option("akshaykhapare2003@gmail.com", "Akshay@2001")
    API.connect()
    
    all_signals = {}
    for pair in pairs:
        velas = API.get_candles(pair, (1 * 60), 6, time())
        signal = cwrv_predict_high_accuracy(velas)
        all_signals[pair] = signal
    
    return all_signals

@app.route("/")
def home():
    return jsonify({"message": "API is working!"})
# 
@app.route("/signal", methods=["GET"])
def get_trading_signal():
    try:
        dir = analyze_all_signals()
        data={"signal": dir}
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains
class AdvancedVolumePredictor:
    def __init__(self):
        self.trend_bias = None

    def fit(self, X, y):
        """Train the model to detect dominant trends from multiple volume indicators."""
        total_trend = sum(y)
        self.trend_bias = 1 if total_trend > 0 else -1  # Overall Market Direction

    def predict(self, X):
        """Predict next candle direction using combined volume indicators."""
        predictions = []

        for features in X:
            volume, price_change, prev_close, obv, nvi, pvi, vpt, volume_ratio = features

            # **Trend Strength Calculation**
            obv_signal = 1 if obv > 0 else -1
            vpt_signal = 1 if vpt > 0 else -1
            pvi_signal = 1 if pvi > nvi else -1
            trend_strength = obv_signal + vpt_signal + pvi_signal  # Combine strengths

            # **Neutral Condition Check**
            price_change_threshold = 0.0005 * prev_close  # 0.05% price change filter
            volume_threshold = 0.015 * volume  # 1.5% volume change filter

            if abs(price_change) < price_change_threshold and abs(vpt) < volume_threshold:
                predictions.append(0)  # NEUTRAL
            elif trend_strength >= 2 and volume_ratio > 1:
                predictions.append(1)  # CALL (Strong Uptrend)
            elif trend_strength <= -2 and volume_ratio < 1:
                predictions.append(-1)  # PUT (Strong Downtrend)
            else:
                predictions.append(self.trend_bias)  # Follow general market trend

        return predictions

def process_candles(candles, window_size=10):
    """Extracts OBV, NVI, PVI, VPT, and Volume Ratio for enhanced accuracy."""
    data = []
    obv, nvi, pvi, vpt = 0, 1000, 1000, 0  

    for i in range(len(candles) - window_size - 1, -1, -1):  # Process bottom to top
        window = candles[i:i + window_size]

        close_prices = [float(c['close']) for c in window]
        volumes = [int(c['volume']) for c in window]

        last_volume = volumes[-1]
        price_change = close_prices[-1] - close_prices[-2]
        prev_close = close_prices[-2]

        # **Calculate OBV, NVI, PVI, and VPT**
        obv = obv + last_volume if price_change > 0 else obv - last_volume
        nvi = nvi * (1 + (price_change / prev_close)) if last_volume < prev_close else nvi
        pvi = pvi * (1 + (price_change / prev_close)) if last_volume > prev_close else pvi
        vpt = vpt + (price_change / prev_close) * last_volume

        # **Volume Ratio: Compare Current Volume with Previous Average**
        avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
        volume_ratio = last_volume / avg_volume if avg_volume != 0 else 1

        # **Determine Candle Direction**
        direction = 1 if price_change > 0 else (-1 if price_change < 0 else 0)

        data.append({
            'volume': last_volume,
            'price_change': price_change,
            'prev_close': prev_close,
            'obv': obv,
            'nvi': nvi,
            'pvi': pvi,
            'vpt': vpt,
            'volume_ratio': volume_ratio,
            'direction': direction
        })

    return data[::-1]  # Reverse to keep recent candles at bottom

def predict_next_candle(candles, window_size=10):
    """Predicts next candle using a highly accurate volume-based strategy."""
    if len(candles) < window_size + 1:
        return "NEUTRAL"

    for candle in candles:
        candle['open'] = float(candle['open'])
        candle['close'] = float(candle['close'])
        candle['volume'] = int(candle['volume'])

    processed_data = process_candles(candles, window_size)

    X = [[d['volume'], d['price_change'], d['prev_close'], d['obv'], d['nvi'], d['pvi'], d['vpt'], d['volume_ratio']]
         for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    model = AdvancedVolumePredictor()
    model.fit(X, y)

    last_candle = processed_data[-1]
    last_features = [[last_candle['volume'], last_candle['price_change'], last_candle['prev_close'],
                      last_candle['obv'], last_candle['nvi'], last_candle['pvi'], last_candle['vpt'], last_candle['volume_ratio']]]

    next_direction = model.predict(last_features)[0]

    return "CALL" if next_direction == 1 else "PUT" if next_direction == -1 else "NEUTRAL"



def signal(pair):
    headers = {'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'}
    
    url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M1&count=100'
    url_hist2 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M2&count=100'
    url_hist5 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M5&count=100'

    response1 = requests.get(url_hist1, headers=headers).json()
    response2 = requests.get(url_hist2, headers=headers).json()
    response5 = requests.get(url_hist5, headers=headers).json()

    data1 = [{'time': m['time'], 'volume': m['volume'], 'open': m['mid']['o'], 
              'close': m['mid']['c'], 'max': m['mid']['h'], 'min': m['mid']['l']}
             for m in response1['candles'] if m['complete']]

    data2 = [{'time': m['time'], 'volume': m['volume'], 'open': m['mid']['o'], 
              'close': m['mid']['c'], 'max': m['mid']['h'], 'min': m['mid']['l']}
             for m in response2['candles'] if m['complete']]

    data5 = [{'time': m['time'], 'volume': m['volume'], 'open': m['mid']['o'], 
              'close': m['mid']['c'], 'max': m['mid']['h'], 'min': m['mid']['l']}
             for m in response5['candles'] if m['complete']]

    dir11 = predict_next_candle(data1, 3)
    dir12 = predict_next_candle(data1, 7)
    dir13 = predict_next_candle(data1, 14)
    dir21 = predict_next_candle(data2, 3)
    dir22 = predict_next_candle(data2, 7)
    dir23 = predict_next_candle(data2, 14)
    dir51 = predict_next_candle(data5, 3)
    dir52 = predict_next_candle(data5, 7)
    dir53 = predict_next_candle(data5, 14)

    dir = dir11 if (dir11 == dir12 == dir13 == dir21 == dir22 == dir23 == dir51 == dir52 == dir53) else "NEUTRAL"
    return dir

@app.route("/")
def home():
    return jsonify({"message": "API is working!"})

@app.route("/trading-signal", methods=["GET"])
def get_trading_signal():
    try:
        pair = request.args.get("pair")
        if not pair:
            return jsonify({"error": "Missing 'pair' parameter"}), 400
        
        dir = signal(pair)
        data={"pair": pair, "signal": dir}
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

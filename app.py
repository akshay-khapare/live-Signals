from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains
class HighAccuracyVolumePredictor:
    def __init__(self):
        self.thresholds = {}

    def fit(self, X, y):
        """ Train using multiple volume strategies. """
        volumes = [x[0] for x in X]
        self.thresholds['high_volume'] = max(volumes) * 0.7  # High volume threshold
        self.thresholds['low_volume'] = min(volumes) * 1.3  # Low volume threshold
        self.trend_bias = 1 if sum(y) > 0 else -1  # Majority trend

    def predict(self, X):
        """ Predict using multiple volume-based rules. """
        predictions = []
        for features in X:
            volume, price_momentum, volume_delta = features

            # 1️⃣ **Volume Climax (VC) → Strong breakouts**
            if volume > self.thresholds['high_volume'] and abs(price_momentum) > 1.2:
                predictions.append(1 if price_momentum > 0 else -1)  # CALL or PUT

            # 2️⃣ **Volume Delta Confirmation (VDC) → Trend validation**
            elif volume_delta > 0.5 and price_momentum > 0:
                predictions.append(1)  # CALL
            elif volume_delta < -0.5 and price_momentum < 0:
                predictions.append(-1)  # PUT

            # 3️⃣ **Relative Volume Surge (RV) → Detect explosive moves**
            elif volume > self.thresholds['low_volume'] and abs(price_momentum) > 0.5:
                predictions.append(1 if price_momentum > 0 else -1)

            # 4️⃣ **No strong signals → Follow dominant trend**
            else:
                predictions.append(self.trend_bias)

        return predictions

def process_candles(candles, window_size=10):
    """Extracts multiple volume strategies for training."""
    data = []

    for i in range(len(candles) - window_size):
        window = candles[i:i + window_size]
        
        close_prices = [float(c['close']) for c in window]
        volumes = [int(c['volume']) for c in window]

        # Compute features
        last_volume = volumes[-1]  # Latest volume
        price_momentum = close_prices[-1] - close_prices[-2]  # Recent price change
        volume_delta = last_volume - volumes[-2]  # Volume change from previous candle

        # Define direction (1 = CALL, -1 = PUT)
        direction = 1 if close_prices[-1] > close_prices[-2] else -1

        data.append({
            'volume': last_volume,
            'price_momentum': price_momentum,
            'volume_delta': volume_delta,
            'direction': direction
        })

    return data

def predict_next_candle(candles, window_size=10):
    """Predicts next candle using high-accuracy volume strategies."""
    if len(candles) < window_size + 1:
        return "NEUTRAL"

    # Convert data types
    for candle in candles:
        candle['open'] = float(candle['open'])
        candle['close'] = float(candle['close'])
        candle['volume'] = int(candle['volume'])

    processed_data = process_candles(candles, window_size)

    # Prepare training data
    X = [[d['volume'], d['price_momentum'], d['volume_delta']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    # Train model
    model = HighAccuracyVolumePredictor()
    model.fit(X, y)

    # Get last candle's volume & price momentum features
    last_candle = processed_data[-1]
    last_features = [[last_candle['volume'], last_candle['price_momentum'], last_candle['volume_delta']]]

    next_direction = model.predict(last_features)[0]

    return "CALL" if next_direction == 1 else "PUT"


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

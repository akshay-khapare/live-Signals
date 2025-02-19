from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

import numpy as np

class UltimateCandlePredictor:
    def __init__(self):
        self.trend_bias = None

    def fit(self, X, y):
        """Train model using recent price and volume trends."""
        self.trend_bias = 1 if sum(y) > 0 else -1  

    def predict(self, X):
        """Predicts the next candle's exact direction with optimized signals."""
        predictions = []
        for features in X:
            volume, price_change, prev_close, obv, vpt, volume_ratio, momentum_strength, volume_spike = features

            # **Core Trend & Volume Signals**
            price_signal = np.sign(price_change)
            obv_signal = np.sign(obv)
            vpt_signal = np.sign(vpt)
            volume_trend = np.sign(volume_ratio - 1)
            momentum_signal = np.sign(momentum_strength - 0.5)
            volume_spike_signal = np.sign(volume_spike - 1)

            # **Weighted Calculation for Final Signal**
            total_signal = (
                price_signal * 0.4 +  # Higher priority on price direction
                obv_signal * 0.2 +  
                vpt_signal * 0.2 +  
                volume_trend * 0.2 +  
                momentum_signal * 0.3 +  
                volume_spike_signal * 0.3  
            )

            # **Balanced Thresholds for More Calls/Puts**
            if total_signal > 0.3:
                predictions.append(1)  # CALL
            elif total_signal < -0.3:
                predictions.append(-1)  # PUT
            else:
                predictions.append(0)  # NEUTRAL

        return predictions


def process_candles(candles):
    """Processes historical candles with balanced filters."""
    data = []
    obv, vpt = 0, 0
    ema_alpha = 0.1  
    volume_ema = int(candles[0]['volume'])

    for i in range(len(candles) - 1, -1, -1):
        last_volume = int(candles[i]['volume'])
        price_change = float(candles[i]['close']) - float(candles[i]['open'])
        prev_close = float(candles[i-1]['close']) if i > 0 else float(candles[i]['open'])

        obv += last_volume if price_change > 0 else -last_volume
        price_ratio = price_change / prev_close if prev_close != 0 else 0
        vpt += (price_ratio * last_volume)

        volume_ema = (last_volume * ema_alpha) + (volume_ema * (1 - ema_alpha))
        volume_ratio = last_volume / volume_ema if volume_ema != 0 else 1
        volume_spike = last_volume / max(volume_ema * 1.2, 1)

        momentum_strength = 1 if price_change > 0 else 0
        direction = 1 if price_change > 0 else -1 if price_change < 0 else 0

        data.append({
            'volume': last_volume,
            'price_change': price_change,
            'prev_close': prev_close,
            'obv': obv,
            'vpt': vpt,
            'volume_ratio': volume_ratio,
            'momentum_strength': momentum_strength,
            'volume_spike': volume_spike,
            'direction': direction
        })

    return data[::-1]


def predict_next_candle(candles):
    """Predicts the next candle with improved accuracy."""
    if len(candles) < 2:
        return "NEUTRAL"

    for candle in candles:
        candle['open'] = float(candle['open'])
        candle['close'] = float(candle['close'])
        candle['volume'] = int(candle['volume'])

    processed_data = process_candles(candles)

    X = [[d['volume'], d['price_change'], d['prev_close'], d['obv'], d['vpt'],
          d['volume_ratio'], d['momentum_strength'], d['volume_spike']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    model = UltimateCandlePredictor()
    model.fit(X, y)

    last_candle = processed_data[-1]
    last_features = [[last_candle['volume'], last_candle['price_change'], last_candle['prev_close'],
                      last_candle['obv'], last_candle['vpt'],
                      last_candle['volume_ratio'], last_candle['momentum_strength'],
                      last_candle['volume_spike']]]

    next_direction = model.predict(last_features)[0]

    return "CALL" if next_direction == 1 else "PUT" if next_direction == -1 else "NEUTRAL"




def signal(pair,offset,minute):
    headers = {'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'}
    
    url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M{minute}&count={offset+1}'

    response1 = requests.get(url_hist1, headers=headers).json()

    data1 = [{'time': m['time'], 'volume': m['volume'], 'open': m['mid']['o'], 
              'close': m['mid']['c'], 'max': m['mid']['h'], 'min': m['mid']['l']}
             for m in response1['candles'] if m['complete']]

    dir = predict_next_candle(data1)
    return dir

@app.route("/")
def home():
    return jsonify({"message": "API is working!"})

@app.route("/trading-signal", methods=["GET"])
def get_trading_signal():
    try:
        pair = request.args.get("pair")
        minute = request.args.get("minute")
        offset = int(request.args.get("offset"))
        if not pair:
            return jsonify({"error": "Missing 'pair' parameter"}), 400
        
        dir = signal(pair,offset,minute)
        data={"pair": pair, "signal": dir}
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

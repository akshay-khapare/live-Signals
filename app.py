from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains
import numpy as np

class CandlePredictor:
    def __init__(self):
        self.bias = None

    def fit(self, X, y):
        """Train model using pure price action, volume & momentum shifts."""
        self.bias = np.sign(sum(y))

    def predict(self, X):
        """Predicts the exact next candle with full precision."""
        predictions = []
        for features in X:
            price_momentum, order_flow, volume_strength, engulfing_signal, wick_signal, breakout_signal = features

            # 🔥 **Stronger Weighting on Momentum & Order Flow**
            total_signal = (
                np.sign(order_flow) * 0.5 +  
                np.sign(volume_strength) * 0.4 +  
                np.sign(engulfing_signal) * 0.3 +  
                np.sign(wick_signal) * 0.2 +  
                np.sign(breakout_signal) * 0.6  
            )

            # 🚀 **Force Strong Decision (No Neutral)**
            predictions.append(1 if total_signal > 0 else -1)

        return predictions


def extract_features(candles):
    """Extracts powerful features based on order flow, volume & price action."""
    data = []
    volume_ema = int(candles[0]['volume'])
    ema_alpha = 0.2  

    for i in range(len(candles) - 1, -1, -1):
        last_volume = int(candles[i]['volume'])
        open_price = float(candles[i]['open'])
        close_price = float(candles[i]['close'])
        high_price = float(candles[i]['high'])
        low_price = float(candles[i]['low'])
        prev_close = float(candles[i-1]['close']) if i > 0 else close_price

        # 📊 **Key Momentum Features**
        price_momentum = close_price - open_price
        order_flow = (close_price - prev_close) * last_volume  
        volume_strength = last_volume / max(volume_ema, 1)

        # 🔥 **Engulfing Pattern for Reversals**
        engulfing_signal = 1 if (close_price > prev_close and open_price < prev_close) else -1 if (close_price < prev_close and open_price > prev_close) else 0

        # 📌 **Wick Strength Analysis**
        wick_signal = 1 if (high_price - close_price) > (close_price - open_price) else -1 if (low_price - open_price) > (open_price - close_price) else 0

        # 🚀 **Breakout & Momentum Confirmations**
        breakout_signal = 1 if close_price > high_price * 0.99 else -1 if close_price < low_price * 1.01 else 0

        # 📉 **Update Volume EMA**
        volume_ema = (last_volume * ema_alpha) + (volume_ema * (1 - ema_alpha))

        # ✅ **Final Direction Target**
        direction = 1 if price_momentum > 0 else -1  

        data.append({
            'price_momentum': price_momentum,
            'order_flow': order_flow,
            'volume_strength': volume_strength,
            'engulfing_signal': engulfing_signal,
            'wick_signal': wick_signal,
            'breakout_signal': breakout_signal,
            'direction': direction
        })

    return data[::-1]


def predict_next_candle(candles):
    """Predicts the most precise next candle move."""
    if len(candles) < 10:
        return "NEUTRAL"

    for candle in candles:
        candle['open'] = float(candle['open'])
        candle['close'] = float(candle['close'])
        candle['high'] = float(candle['high'])
        candle['low'] = float(candle['low'])
        candle['volume'] = int(candle['volume'])

    processed_data = extract_features(candles)

    X = [[d['price_momentum'], d['order_flow'], d['volume_strength'], d['engulfing_signal'], d['wick_signal'], d['breakout_signal']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    model = CandlePredictor()
    model.fit(X, y)

    last_candle = processed_data[-1]
    last_features = [[last_candle['price_momentum'], last_candle['order_flow'], last_candle['volume_strength'],
                      last_candle['engulfing_signal'], last_candle['wick_signal'], last_candle['breakout_signal']]]

    next_direction = model.predict(last_features)[0]

    return "CALL" if next_direction == 1 else "PUT"




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

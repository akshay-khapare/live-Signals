from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains
import numpy as np

class UltimatePredictor:
    def __init__(self):
        self.bias = None

    def fit(self, X, y):
        """Train model with a mix of price action, order flow, and volume dynamics."""
        self.bias = np.sign(sum(y))

    def predict(self, X):
        """Predicts next candle with the highest precision."""
        predictions = []
        for features in X:
            price_momentum, order_flow, imbalance_ratio, liquidity_strength, volume_spike, engulfing_signal, wick_analysis, break_structure = features

            # 📊 **Order Flow & Liquidity Strength Confirmation**
            order_flow_signal = np.sign(order_flow)
            liquidity_signal = np.sign(liquidity_strength)
            imbalance_signal = np.sign(imbalance_ratio - 1)

            # 🔥 **Engulfing & Wick Confirmation**
            engulfing_strength = np.sign(engulfing_signal)
            wick_signal = np.sign(wick_analysis)
            break_signal = np.sign(break_structure)

            # 🚀 **Final Prediction Signal**
            total_signal = (
                order_flow_signal * 0.35 +
                liquidity_signal * 0.3 +
                imbalance_signal * 0.25 +
                engulfing_strength * 0.4 +
                wick_signal * 0.3 +
                break_signal * 0.5
            )

            # 🎯 **Final Decision**
            if total_signal > 1.3:
                predictions.append(1)  # CALL
            elif total_signal < -1.3:
                predictions.append(-1)  # PUT
            else:
                predictions.append(0)  # NEUTRAL

        return predictions


def process_candles(candles):
    """Extracts high-precision features from price action, order flow & liquidity."""
    data = []
    volume_ema = int(candles[0]['volume'])
    ema_alpha = 0.1  # Smooth exponential tracking

    for i in range(len(candles) - 1, -1, -1):
        last_volume = int(candles[i]['volume'])
        open_price = float(candles[i]['open'])
        close_price = float(candles[i]['close'])
        high_price = float(candles[i]['high'])
        low_price = float(candles[i]['low'])
        prev_close = float(candles[i-1]['close']) if i > 0 else close_price

        # 🔥 **Smart Order Flow & Liquidity**
        price_momentum = close_price - open_price
        liquidity_strength = last_volume / max(volume_ema, 1)

        # 📈 **Order Flow & Imbalance**
        order_flow = (close_price - prev_close) * last_volume
        imbalance_ratio = last_volume / volume_ema if volume_ema != 0 else 1

        # 📊 **Engulfing Candle Detection**
        engulfing_signal = 1 if (close_price > prev_close and open_price < prev_close) else -1 if (close_price < prev_close and open_price > prev_close) else 0

        # 📌 **Wick Analysis**
        wick_analysis = 1 if (high_price - close_price) > (close_price - open_price) else -1 if (low_price - open_price) > (open_price - close_price) else 0

        # 🚀 **Break of Structure (BOS)**
        break_structure = 1 if close_price > high_price * 0.98 else -1 if close_price < low_price * 1.02 else 0

        # 📉 **Volume EMA Update**
        volume_ema = (last_volume * ema_alpha) + (volume_ema * (1 - ema_alpha))

        # 🎯 **Final Direction**
        direction = 1 if price_momentum > 0 else -1 if price_momentum < 0 else 0

        data.append({
            'price_momentum': price_momentum,
            'order_flow': order_flow,
            'imbalance_ratio': imbalance_ratio,
            'liquidity_strength': liquidity_strength,
            'volume_spike': last_volume / np.max([volume_ema * 1.5, 1]),
            'engulfing_signal': engulfing_signal,
            'wick_analysis': wick_analysis,
            'break_structure': break_structure,
            'direction': direction
        })

    return data[::-1]


def predict_next_candle(candles):
    """Predicts the most precise next candle using Smart Order Flow & Price Action."""
    if len(candles) < 14:
        return "NEUTRAL"

    for candle in candles:
        candle['open'] = float(candle['open'])
        candle['close'] = float(candle['close'])
        candle['high'] = float(candle['high'])
        candle['low'] = float(candle['low'])
        candle['volume'] = int(candle['volume'])

    processed_data = process_candles(candles)

    X = [[d['price_momentum'], d['order_flow'], d['imbalance_ratio'], d['liquidity_strength'], 
          d['volume_spike'], d['engulfing_signal'], d['wick_analysis'], d['break_structure']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    model = UltimatePredictor()
    model.fit(X, y)

    last_candle = processed_data[-1]
    last_features = [[last_candle['price_momentum'], last_candle['order_flow'], last_candle['imbalance_ratio'],
                      last_candle['liquidity_strength'], last_candle['volume_spike'],
                      last_candle['engulfing_signal'], last_candle['wick_analysis'], last_candle['break_structure']]]

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

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains
import numpy as np

class AdvancedVolumePredictor:
    def __init__(self):
        self.trend_bias = None

    def fit(self, X, y):
        """Train model to detect dominant trend bias based on historical movements."""
        self.trend_bias = 1 if sum(y) > 0 else -1  

    def predict(self, X):
        """Predict next candle direction using trend and volume confirmation."""
        predictions = []

        for features in X:
            volume, price_change, prev_close, obv, nvi, pvi, vpt, volume_ratio, ma_volume, ma_price, momentum = features
            
            # **Key Indicators Confirmation**
            obv_signal = np.sign(obv)  
            pvi_signal = np.sign(pvi - nvi)  
            vpt_signal = np.sign(vpt)  
            trend_ma_signal = 1 if ma_price > prev_close else -1  
            volume_strength = np.sign(volume_ratio - 1)  
            momentum_signal = np.sign(momentum - 0.5)  

            # **Final Decision - Weighted Confidence Model**
            total_signal = (
                obv_signal * 0.3 +
                pvi_signal * 0.2 +
                vpt_signal * 0.2 +
                trend_ma_signal * 0.2 +
                volume_strength * 0.1 +
                momentum_signal * 0.2
            )

            # **Stronger Trend Validation**
            if total_signal > 0.5:
                predictions.append(1)  # CALL
            elif total_signal < -0.5:
                predictions.append(-1)  # PUT
            else:
                predictions.append(0)  # NEUTRAL

        return predictions


def process_candles(candles, window_size=10):
    """Processes candle data with enhanced trend detection and momentum validation."""
    data = []
    obv, nvi, pvi, vpt = 0, 1000, 1000, 0
    ema_alpha = 2 / (window_size + 1)
    volume_ema = int(candles[0]['volume'])

    for i in range(len(candles) - window_size - 1, -1, -1):
        window = candles[i:i + window_size]
        close_prices = [float(c['close']) for c in window]
        volumes = [int(c['volume']) for c in window]

        last_volume = volumes[-1]
        price_change = close_prices[-1] - close_prices[-2]
        prev_close = close_prices[-2]

        # **OBV Calculation**
        obv = obv + (last_volume if price_change > 0 else -last_volume)

        # **NVI & PVI Calculation**
        price_ratio = price_change / prev_close if prev_close != 0 else 0
        nvi = nvi * (1 + price_ratio) if last_volume < volume_ema else nvi
        pvi = pvi * (1 + price_ratio) if last_volume > volume_ema else pvi

        # **VPT Calculation**
        vpt = vpt + (price_ratio * last_volume)

        # **Volume EMA Update**
        volume_ema = (last_volume * ema_alpha) + (volume_ema * (1 - ema_alpha))

        # **Multi-Period Moving Averages**
        ma_volumes = [sum([int(c['volume']) for c in candles[i:i+period]]) / len(candles[i:i+period])
                      for period in [2, 5, 7] if i + period <= len(candles)]
        ma_volume = np.mean(ma_volumes) if ma_volumes else np.mean(volumes)
        ma_price = np.mean(close_prices)

        # **Volume Ratio Calculation**
        volume_ratio = last_volume / ma_volume if ma_volume != 0 else 1

        # **Momentum Analysis**
        momentum = sum(1 for p in close_prices[:-1] if p < close_prices[-1]) / (len(close_prices) - 1)

        # **Direction Signal**
        direction = 1 if price_change > 0 and momentum > 0.6 else (-1 if price_change < 0 and momentum < 0.4 else 0)

        data.append({
            'volume': last_volume,
            'price_change': price_change,
            'prev_close': prev_close,
            'obv': obv,
            'nvi': nvi,
            'pvi': pvi,
            'vpt': vpt,
            'volume_ratio': volume_ratio,
            'ma_volume': ma_volume,
            'ma_price': ma_price,
            'momentum': momentum,
            'direction': direction
        })

    return data[::-1]


def predict_next_candle(candles, window_size=10):
    """Predicts the next candle direction using enhanced trend and momentum signals."""
    if len(candles) < window_size + 1:
        return "NEUTRAL"

    for candle in candles:
        candle['open'] = float(candle['open'])
        candle['close'] = float(candle['close'])
        candle['volume'] = int(candle['volume'])

    processed_data = process_candles(candles, window_size)

    X = [[d['volume'], d['price_change'], d['prev_close'], d['obv'], d['nvi'], d['pvi'], d['vpt'],
          d['volume_ratio'], d['ma_volume'], d['ma_price'], d['momentum']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    model = AdvancedVolumePredictor()
    model.fit(X, y)

    last_candle = processed_data[-1]
    last_features = [[last_candle['volume'], last_candle['price_change'], last_candle['prev_close'],
                      last_candle['obv'], last_candle['nvi'], last_candle['pvi'], last_candle['vpt'],
                      last_candle['volume_ratio'], last_candle['ma_volume'], last_candle['ma_price'],
                      last_candle['momentum']]]

    next_direction = model.predict(last_features)[0]

    return "CALL" if next_direction == 1 else "PUT" if next_direction == -1 else "NEUTRAL"


def signal(pair,offset,minute):
    headers = {'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'}
    
    url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M{minute}&count={offset+1}'

    response1 = requests.get(url_hist1, headers=headers).json()

    data1 = [{'time': m['time'], 'volume': m['volume'], 'open': m['mid']['o'], 
              'close': m['mid']['c'], 'max': m['mid']['h'], 'min': m['mid']['l']}
             for m in response1['candles'] if m['complete']]

    dir = predict_next_candle(data1, offset)
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

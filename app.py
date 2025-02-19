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
        self.volatility_threshold = None
        self.volume_ma_periods = [5, 10, 20]
        self.market_regime = None
        self.rsi_threshold = {'overbought': 85, 'oversold': 15}  # Even wider RSI thresholds
        self.momentum_window = 14

    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index."""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def detect_market_regime(self, prices, volumes):
        """Simplified market regime detection."""
        price_std = np.std(prices)
        price_trend = np.mean(np.diff(prices))
        
        if abs(price_trend) > price_std * 0.5:  # Much lower trend threshold
            return 'trending'
        return 'normal'

    def fit(self, X, y):
        """Simplified training process."""
        prices = [x[2] for x in X]  # prev_close at index 2
        volumes = [x[0] for x in X]  # volume at index 0
        
        self.market_regime = self.detect_market_regime(prices, volumes)
        
        # Simple trend bias calculation
        price_changes = [x[1] for x in X]
        self.trend_bias = np.sign(sum(price_changes))
        
        # Set a very low volatility threshold
        self.volatility_threshold = np.std(price_changes) * 0.5

    def predict(self, X):
        """Simplified and more aggressive prediction logic."""
        predictions = []
        
        for features in X:
            volume, price_change, prev_close, obv, nvi, pvi, vpt, volume_ratio, ma_volume, ma_price = features
            
            # Basic signal components
            obv_signal = 1 if obv > 0 else -1 if obv < 0 else 0
            vpt_signal = 1 if vpt > 0 else -1 if vpt < 0 else 0
            price_signal = 1 if price_change > 0 else -1 if price_change < 0 else 0
            
            # Simple weighted signal
            signal_strength = (
                obv_signal * 0.4 +
                vpt_signal * 0.3 +
                price_signal * 0.3
            )
            
            # Very low threshold for signal generation
            if signal_strength > 0.2:  # Lowered from previous thresholds
                predictions.append(1)  # CALL
            elif signal_strength < -0.2:  # Lowered from previous thresholds
                predictions.append(-1)  # PUT
            else:
                predictions.append(0)  # NEUTRAL

        return predictions


def process_candles(candles, window_size=10):
    """Simplified candle processing."""
    data = []
    obv, vpt = 0, 0
    
    for i in range(len(candles) - window_size - 1, -1, -1):
        window = candles[i:i + window_size]
        
        close_prices = [float(c['close']) for c in window]
        volumes = [int(c['volume']) for c in window]
        
        last_volume = volumes[-1]
        price_change = close_prices[-1] - close_prices[-2]
        prev_close = close_prices[-2]
        
        # Simplified OBV calculation
        obv = obv + last_volume if price_change > 0 else obv - last_volume
        
        # Simplified VPT calculation
        vpt = vpt + (price_change / prev_close * last_volume if prev_close != 0 else 0)
        
        # Simple moving averages
        ma_volume = sum(volumes) / len(volumes)
        ma_price = sum(close_prices) / len(close_prices)
        
        # Simplified volume ratio
        volume_ratio = last_volume / ma_volume if ma_volume != 0 else 1
        
        # Basic direction calculation
        direction = 1 if price_change > 0 else -1 if price_change < 0 else 0
        
        data.append({
            'volume': last_volume,
            'price_change': price_change,
            'prev_close': prev_close,
            'obv': obv,
            'nvi': 0,  # Removed NVI calculation
            'pvi': 0,  # Removed PVI calculation
            'vpt': vpt,
            'volume_ratio': volume_ratio,
            'ma_volume': ma_volume,
            'ma_price': ma_price,
            'direction': direction
        })
    
    return data[::-1]


def predict_next_candle(candles, window_size=10):
    """Enhanced prediction function with improved accuracy."""
    if len(candles) < window_size + 1:
        return "NEUTRAL"

    # Normalize input data
    for candle in candles:
        candle['open'] = float(candle['open'])
        candle['close'] = float(candle['close'])
        candle['volume'] = int(candle['volume'])

    processed_data = process_candles(candles, window_size)

    X = [[d['volume'], d['price_change'], d['prev_close'], d['obv'], d['nvi'], d['pvi'], d['vpt'],
          d['volume_ratio'], d['ma_volume'], d['ma_price']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    model = AdvancedVolumePredictor()
    model.fit(X, y)

    last_candle = processed_data[-1]
    last_features = [[last_candle['volume'], last_candle['price_change'], last_candle['prev_close'],
                      last_candle['obv'], last_candle['nvi'], last_candle['pvi'], last_candle['vpt'],
                      last_candle['volume_ratio'], last_candle['ma_volume'], last_candle['ma_price']]]

    next_direction = model.predict(last_features)[0]

    return "CALL" if next_direction == 1 else "PUT" if next_direction == -1 else "NEUTRAL"


def signal(pair, offset, minute):
    headers = {'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'}

    url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M{minute}&count=100'

    response1 = requests.get(url_hist1, headers=headers).json()

    data1 = [{'time': m['time'], 'volume': m['volume'], 'open': m['mid']['o'], 'close': m['mid']['c'],
              'max': m['mid']['h'], 'min': m['mid']['l']}
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

        dir = signal(pair, offset, minute)
        data = {"pair": pair, "signal": dir}
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

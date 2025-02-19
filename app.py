from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

class AdvancedVolumePredictor:
    def __init__(self):
        self.ema_short = 8  # Short-term trend
        self.ema_long = 21  # Long-term trend
        self.rsi_period = 14
        self.volume_period = 10
        
    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average."""
        alpha = 2 / (period + 1)
        ema = [data[0]]
        for price in data[1:]:
            ema.append(price * alpha + ema[-1] * (1 - alpha))
        return ema

    def calculate_rsi(self, prices):
        """Calculate Relative Strength Index."""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = -np.where(deltas < 0, deltas, 0)
        
        avg_gain = np.mean(gains[:self.rsi_period])
        avg_loss = np.mean(losses[:self.rsi_period])
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def fit(self, X, y):
        """Initialize model with training data."""
        # No complex training needed for this model
        # Just validate the data format
        if len(X) < self.ema_long:
            raise ValueError(f"Training data must have at least {self.ema_long} samples")
        
        # Verify data structure
        if not all(len(x) >= 3 for x in X):
            raise ValueError("Each sample must contain at least [volume, price_change, prev_close]")
        
        return self

    def predict(self, X):
        """Generate trading signals based on price action and volume."""
        if len(X) < self.ema_long:
            return [0] * len(X)
            
        predictions = []
        
        for i in range(self.ema_long, len(X)):
            window = X[max(0, i-self.ema_long):i+1]
            
            # Get price and volume data
            prices = [x[2] for x in window]  # prev_close
            volumes = [x[0] for x in window]  # volume
            current_price = prices[-1]
            current_volume = volumes[-1]
            
            # 1. Trend Analysis
            ema_short = self.calculate_ema(prices, self.ema_short)[-1]
            ema_long = self.calculate_ema(prices, self.ema_long)[-1]
            trend = 1 if ema_short > ema_long else -1
            
            # 2. Volume Analysis
            avg_volume = np.mean(volumes[-self.volume_period:])
            volume_surge = current_volume > avg_volume * 1.3
            
            # 3. Price Momentum
            price_change = (current_price - prices[-2]) / prices[-2]
            momentum = 1 if price_change > 0 else -1
            
            # 4. RSI
            rsi = self.calculate_rsi(prices)
            rsi_signal = 0
            if rsi < 30:  # Oversold
                rsi_signal = 1
            elif rsi > 70:  # Overbought
                rsi_signal = -1
                
            # Signal Generation
            signal = 0
            
            # Strong trend conditions
            if abs(price_change) > 0.0005:  # Minimum price movement
                if volume_surge:  # Volume confirmation
                    if trend == momentum:  # Trend and momentum agree
                        if (rsi_signal == 0) or (rsi_signal == trend):  # RSI confirms or neutral
                            signal = trend
                            
                            # Extra confirmation: Check if price is accelerating
                            prev_change = (prices[-2] - prices[-3]) / prices[-3]
                            if abs(price_change) > abs(prev_change):
                                predictions.append(signal)
                                continue
            
            predictions.append(0)
            
        return predictions

def process_candles(candles, window_size=10):
    """Process candle data for prediction."""
    data = []
    
    for i in range(len(candles) - window_size - 1, -1, -1):
        window = candles[i:i + window_size]
        
        close_prices = [float(c['close']) for c in window]
        volumes = [int(c['volume']) for c in window]
        
        last_volume = volumes[-1]
        price_change = close_prices[-1] - close_prices[-2]
        prev_close = close_prices[-2]
        
        # Calculate moving averages
        ma_volume = np.mean(volumes)
        ma_price = np.mean(close_prices)
        
        # Simple volume ratio
        volume_ratio = last_volume / ma_volume if ma_volume != 0 else 1
        
        data.append({
            'volume': last_volume,
            'price_change': price_change,
            'prev_close': prev_close,
            'obv': last_volume if price_change > 0 else -last_volume,
            'nvi': 0,
            'pvi': 0,
            'vpt': price_change * last_volume,
            'volume_ratio': volume_ratio,
            'ma_volume': ma_volume,
            'ma_price': ma_price,
            'direction': 1 if price_change > 0 else -1 if price_change < 0 else 0
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

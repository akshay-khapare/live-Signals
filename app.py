from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

class PureVolumeMomentumPredictor:
    def __init__(self):
        self.trend_bias = None
        self.last_signals = []
        self.volatility_threshold = 0.002

    def calculate_rsi(self, prices, period=14):
        gains = []
        losses = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period if len(gains) >= period else sum(gains) / len(gains)
        avg_loss = sum(losses[-period:]) / period if len(losses) >= period else sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, prices, fast=12, slow=26):
        if len(prices) < slow:
            return 0
        
        fast_ema = prices[-fast:] if len(prices) >= fast else prices
        slow_ema = prices[-slow:] if len(prices) >= slow else prices
        
        return sum(fast_ema)/len(fast_ema) - sum(slow_ema)/len(slow_ema)

    def fit(self, X, y):
        """Enhanced training with trend analysis"""
        recent_moves = y[-20:] if len(y) > 20 else y
        self.trend_bias = 1 if sum(recent_moves) > 0 else -1
        
        # Calculate average volatility for adaptive thresholds
        price_changes = [x[1] for x in X]
        self.volatility_threshold = sum([abs(pc) for pc in price_changes[-20:]]) / min(20, len(price_changes))

    def predict(self, X):
        """Enhanced prediction using multiple technical indicators"""
        predictions = []
        
        for features in X:
            volume, price_change, prev_close, obv, vpt, volume_ratio, momentum = features
            
            # Volume Analysis
            volume_signal = 1 if volume_ratio > 1.5 else (-1 if volume_ratio < 0.5 else 0)
            
            # Price Action
            price_signal = 1 if price_change > self.volatility_threshold else (-1 if price_change < -self.volatility_threshold else 0)
            
            # Trend Analysis
            trend_signal = np.sign(obv) * 0.5 + np.sign(vpt) * 0.5
            
            # Momentum Analysis
            momentum_threshold = 0.6
            momentum_signal = 1 if momentum > momentum_threshold else (-1 if momentum < (1-momentum_threshold) else 0)
            
            # Combined Signal with Dynamic Weighting
            total_signal = (
                volume_signal * 0.3 +
                price_signal * 0.25 +
                trend_signal * 0.25 +
                momentum_signal * 0.2 +
                self.trend_bias * 0.1
            )
            
            # Signal Smoothing with Recent History
            self.last_signals.append(total_signal)
            if len(self.last_signals) > 3:
                self.last_signals.pop(0)
            
            smoothed_signal = sum(self.last_signals) / len(self.last_signals)
            
            # Enhanced Decision Making
            if abs(smoothed_signal) > 0.8 and abs(price_change) > self.volatility_threshold:
                predictions.append(1 if smoothed_signal > 0 else -1)
            else:
                predictions.append(0)

        return predictions


def process_candles(candles):
    """Enhanced candle processing with additional technical indicators"""
    data = []
    obv, vpt = 0, 0
    ema_alpha = 0.2  # Increased sensitivity
    volume_ema = int(candles[0]['volume'])
    prices = []
    
    for i in range(len(candles) - 1, -1, -1):
        current_candle = candles[i]
        
        # Safely get candle values with defaults
        try:
            last_volume = int(current_candle.get('volume', 0))
            current_close = float(current_candle.get('close', 0))
            current_open = float(current_candle.get('open', 0))
            current_high = float(current_candle.get('close', 0))  # Use close if high not available
            current_low = float(current_candle.get('open', 0))   # Use open if low not available
            price_change = current_close - current_open
            prev_close = float(candles[i-1].get('close', current_open)) if i > 0 else current_open
        except (ValueError, TypeError, KeyError):
            continue
        
        prices.append(current_close)
        
        # Enhanced OBV calculation
        obv += last_volume * (1 if price_change > 0 else -1 if price_change < 0 else 0)
        
        # Enhanced VPT calculation
        price_ratio = price_change / prev_close if prev_close != 0 else 0
        vpt += last_volume * price_ratio
        
        # Improved Volume Analysis
        volume_ema = (last_volume * ema_alpha) + (volume_ema * (1 - ema_alpha))
        volume_ratio = last_volume / volume_ema if volume_ema != 0 else 1
        
        # Enhanced Momentum Calculation
        range_size = current_high - current_low
        close_position = (current_close - current_low) / range_size if range_size != 0 else 0.5
        momentum_strength = (close_position + (1 if price_change > 0 else 0)) / 2
        
        # Direction Signal with Price Action
        direction = 1 if price_change > 0 and momentum_strength > 0.7 else (-1 if price_change < 0 and momentum_strength < 0.3 else 0)
        
        data.append({
            'volume': last_volume,
            'price_change': price_change,
            'prev_close': prev_close,
            'obv': obv,
            'vpt': vpt,
            'volume_ratio': volume_ratio,
            'momentum_strength': momentum_strength,
            'direction': direction
        })

    return data[::-1]


def predict_next_candle(candles):
    """Enhanced prediction with confidence threshold"""
    if len(candles) < 3:  # Increased minimum candles requirement
        return "NEUTRAL"

    # Data Preparation with safe type conversion
    try:
        for candle in candles:
            candle['open'] = float(candle.get('open', 0))
            candle['close'] = float(candle.get('close', 0))
            candle['volume'] = int(candle.get('volume', 0))
    except (ValueError, TypeError):
        return "NEUTRAL"

    processed_data = process_candles(candles)
    
    if not processed_data:
        return "NEUTRAL"

    X = [[d['volume'], d['price_change'], d['prev_close'], d['obv'], d['vpt'],
          d['volume_ratio'], d['momentum_strength']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]

    if not X or not y:
        return "NEUTRAL"

    model = PureVolumeMomentumPredictor()
    model.fit(X, y)

    last_candle = processed_data[-1]
    last_features = [[last_candle['volume'], last_candle['price_change'], last_candle['prev_close'],
                      last_candle['obv'], last_candle['vpt'],
                      last_candle['volume_ratio'], last_candle['momentum_strength']]]

    prediction = model.predict(last_features)[0]
    
    # Add final confidence check
    if abs(last_candle['price_change']) < model.volatility_threshold:
        return "NEUTRAL"

    return "CALL" if prediction == 1 else "PUT" if prediction == -1 else "NEUTRAL"


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

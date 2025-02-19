from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
import math

app = Flask(__name__)
CORS(app)  

class AdvancedVolumePredictor:
    def __init__(self):
        self.trend_bias = None
        self.volatility_threshold = None
        self.volume_ma_periods = [5, 10, 20]
        self.weights = None
        
    def _normalize_features(self, X):
        """Custom lightweight feature normalization."""
        normalized_X = []
        for features in X:
            # Min-Max scaling without external libraries
            normalized_row = []
            for i, val in enumerate(features):
                if val == 0:
                    normalized_row.append(0)
                    continue
                
                # Find min and max in the column
                column = [row[i] for row in X]
                col_min, col_max = min(column), max(column)
                
                # Prevent division by zero
                if col_min == col_max:
                    normalized_row.append(0.5)
                else:
                    normalized_val = (val - col_min) / (col_max - col_min)
                    normalized_row.append(normalized_val)
            
            normalized_X.append(normalized_row)
        
        return normalized_X
    
    def _calculate_feature_importance(self, X, y):
        """Calculate feature importance using correlation and variance."""
        feature_importances = []
        
        for i in range(len(X[0])):
            column = [row[i] for row in X]
            
            # Calculate correlation with target
            column_mean = sum(column) / len(column)
            y_mean = sum(y) / len(y)
            
            numerator = sum((column[j] - column_mean) * (y[j] - y_mean) for j in range(len(y)))
            denominator = math.sqrt(
                sum((column[j] - column_mean)**2 for j in range(len(y))) *
                sum((y[j] - y_mean)**2 for j in range(len(y)))
            )
            
            correlation = numerator / denominator if denominator != 0 else 0
            variance = sum((val - column_mean)**2 for val in column) / len(column)
            
            feature_importances.append(abs(correlation) * variance)
        
        return feature_importances
    
    def fit(self, X, y):
        """Train model using custom lightweight techniques."""
        # Normalize features
        X_normalized = self._normalize_features(X)
        
        # Calculate feature importance
        feature_importances = self._calculate_feature_importance(X_normalized, y)
        
        # Initialize adaptive weights
        self.weights = [
            1.0 / (1 + math.exp(-importance)) 
            for importance in feature_importances
        ]
        
        # Calculate trend bias with weighted recent data
        weighted_trends = [y[i] * (i + 1) / len(y) for i in range(len(y))]
        self.trend_bias = 1 if sum(weighted_trends) > 0 else -1
        
        # Calculate volatility threshold
        price_changes = [x[1] for x in X]
        self.volatility_threshold = np.std(price_changes) * 1.5
    
    def _weighted_voting(self, features):
        """Custom ensemble prediction using weighted voting."""
        # Weighted feature contributions
        weighted_contributions = [
            features[i] * self.weights[i] 
            for i in range(len(features))
        ]
        
        # Aggregate weighted contributions
        total_contribution = sum(weighted_contributions)
        normalized_contribution = total_contribution / sum(self.weights)
        
        # Adaptive thresholding
        if abs(normalized_contribution) < 0.1:
            return 0  # Neutral
        elif normalized_contribution > 0.3:
            return 1  # Strong positive
        elif normalized_contribution < -0.3:
            return -1  # Strong negative
        else:
            return 0  # Neutral
    
    def predict(self, X):
        """Predict using custom lightweight ensemble method."""
        # Normalize features
        X_normalized = self._normalize_features(X)
        
        predictions = []
        for features in X_normalized:
            prediction = self._weighted_voting(features)
            predictions.append(prediction)
        
        return predictions

def process_candles(candles, window_size=10):
    """Enhanced candle processing with lightweight technical indicators."""
    data = []
    obv, nvi, pvi, vpt = 0, 1000, 1000, 0
    
    # Lightweight moving averages
    volume_ema = int(candles[0]['volume'])
    
    for i in range(len(candles) - window_size - 1, -1, -1):
        window = candles[i:i + window_size]
        
        close_prices = [float(c['close']) for c in window]
        volumes = [int(c['volume']) for c in window]
        
        last_volume = volumes[-1]
        price_change = close_prices[-1] - close_prices[-2]
        prev_close = close_prices[-2]
        
        # Simplified technical indicators
        volume_momentum = last_volume / (sum(volumes) + 1e-5)
        price_momentum = price_change / (prev_close + 1e-5)
        
        # Lightweight OBV calculation
        obv = obv + (last_volume * volume_momentum * (1 + abs(price_momentum)))
        
        # Simplified NVI and PVI
        nvi = nvi * (1 + price_momentum * (2 if last_volume < volume_ema else 1))
        pvi = pvi * (1 + price_momentum * (2 if last_volume > volume_ema else 1))
        
        # Lightweight VPT
        vpt = vpt + (price_momentum * last_volume * (1 + abs(price_momentum) * 2))
        
        # Update volume EMA
        volume_ema = int(0.7 * last_volume + 0.3 * volume_ema)
        
        # Multiple moving averages
        ma_volumes = [
            sum([int(c['volume']) for c in candles[i:i+period]]) / period 
            for period in [5, 10, 20] if i + period <= len(candles)
        ]
        
        ma_volume = sum(ma_volumes) / len(ma_volumes) if ma_volumes else sum(volumes) / len(volumes)
        ma_price = sum(close_prices) / len(close_prices)
        
        # Volume ratio
        volume_ratio = last_volume / (ma_volume + 1e-5)
        
        # Multi-factor momentum
        momentum_factors = [
            sum(1 for p in close_prices[:-1] if p < close_prices[-1]) / (len(close_prices) - 1),
            sum(1 for v in volumes[:-1] if v < volumes[-1]) / (len(volumes) - 1)
        ]
        direction = 1 if price_change > 0 and np.mean(momentum_factors) > 0.6 else \
                    (-1 if price_change < 0 and np.mean(momentum_factors) < 0.4 else 0)
        
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
            'direction': direction
        })
    
    return data[::-1]

def predict_next_candle(candles, window_size=10):
    """Enhanced prediction function with lightweight approach."""
    if len(candles) < window_size + 1:
        return "NEUTRAL"
        
    # Lightweight data validation
    try:
        for candle in candles:
            float(candle['open'])
            float(candle['close'])
            int(candle['volume'])
    except (ValueError, TypeError, KeyError) as e:
        print(f"Data validation error: {e}")
        return "NEUTRAL"
    
    processed_data = process_candles(candles, window_size)
    
    X = [[d['volume'], d['price_change'], d['prev_close'], d['obv'], d['nvi'], d['pvi'], d['vpt'], 
          d['volume_ratio'], d['ma_volume'], d['ma_price']] for d in processed_data[:-1]]
    y = [d['direction'] for d in processed_data[:-1]]
    
    # Handle insufficient training data
    if len(X) < 2 or len(set(y)) < 2:
        return "NEUTRAL"
    
    model = AdvancedVolumePredictor()
    model.fit(X, y)
    
    last_candle = processed_data[-1]
    last_features = [[last_candle['volume'], last_candle['price_change'], last_candle['prev_close'],
                      last_candle['obv'], last_candle['nvi'], last_candle['pvi'], last_candle['vpt'], 
                      last_candle['volume_ratio'], last_candle['ma_volume'], last_candle['ma_price']]]
    
    next_direction = model.predict(last_features)[0]
    
    return "CALL" if next_direction == 1 else "PUT" if next_direction == -1 else "NEUTRAL"

def signal(pair,offset,minute):
    headers = {'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'}
    
    url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M{minute}&count=100'

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

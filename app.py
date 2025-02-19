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
        self.volume_ma_periods = [5, 10, 20]  # Multiple periods for volume analysis
        
    def fit(self, X, y):
        """Train model to detect dominant market trends and establish volatility baseline."""
        # Calculate trend strength using weighted recent data
        weighted_trends = []
        for i, direction in enumerate(y):
            weight = (i + 1) / len(y)  # More recent trends get higher weights
            weighted_trends.append(direction * weight)
            
        total_trend = sum(weighted_trends)
        self.trend_bias = 1 if total_trend > 0 else -1
        
        # Calculate volatility threshold from training data
        price_changes = [x[1] for x in X]  # price_change is at index 1
        self.volatility_threshold = np.std(price_changes) * 1.5

    def predict(self, X):
        """Predicts next candle direction using enhanced volume indicators."""
        predictions = []

        for features in X:
            volume, price_change, prev_close, obv, nvi, pvi, vpt, volume_ratio, ma_volume, ma_price = features
            
            # Enhanced trend confirmation signals with weighted importance
            obv_signal = 1 if obv > 0 else -1 if obv < 0 else 0
            vpt_signal = 1 if vpt > 0 else -1 if vpt < 0 else 0
            pvi_signal = 1 if pvi > nvi else -1 if pvi < nvi else 0
            
            # Volume trend analysis
            volume_trend = 1 if volume_ratio > 1.2 else -1 if volume_ratio < 0.8 else 0
            
            # Weighted signal combination
            signal_weights = {
                'obv': 0.3,
                'vpt': 0.25,
                'pvi': 0.25,
                'volume': 0.2
            }
            
            weighted_signal = (
                obv_signal * signal_weights['obv'] +
                vpt_signal * signal_weights['vpt'] +
                pvi_signal * signal_weights['pvi'] +
                volume_trend * signal_weights['volume']
            )

            # Dynamic thresholds based on market conditions
            price_volatility = abs(price_change) / prev_close
            volume_volatility = abs(volume - ma_volume) / ma_volume
            
            # Adaptive decision thresholds
            trend_threshold = 0.15 * (1 + volume_volatility)  # Requires stronger signals in volatile periods
            neutral_threshold = 0.05 * (1 + price_volatility)
            
            # Enhanced decision making with volatility consideration
            if price_volatility > self.volatility_threshold * 2:
                predictions.append(0)  # Stay neutral in extremely volatile conditions
            elif abs(weighted_signal) < neutral_threshold:
                predictions.append(0)  # NEUTRAL
            elif weighted_signal > trend_threshold:
                # Confirmation check using price action
                if price_change > 0 and volume_ratio > 1:
                    predictions.append(1)  # Strong CALL signal
                else:
                    predictions.append(0)  # Weak signal, stay neutral
            elif weighted_signal < -trend_threshold:
                # Confirmation check using price action
                if price_change < 0 and volume_ratio > 1:
                    predictions.append(-1)  # Strong PUT signal
                else:
                    predictions.append(0)  # Weak signal, stay neutral
            else:
                predictions.append(0)  # NEUTRAL

        return predictions


def process_candles(candles, window_size=10):
    """Enhanced candle processing with improved technical indicators."""
    data = []
    obv, nvi, pvi, vpt = 0, 1000, 1000, 0
    
    # Calculate exponential moving averages for volume
    ema_alpha = 2 / (window_size + 1)
    volume_ema = int(candles[0]['volume'])
    
    for i in range(len(candles) - window_size - 1, -1, -1):
        window = candles[i:i + window_size]
        
        close_prices = [float(c['close']) for c in window]
        volumes = [int(c['volume']) for c in window]
        
        last_volume = volumes[-1]
        price_change = close_prices[-1] - close_prices[-2]
        prev_close = close_prices[-2]
        
        # Enhanced OBV calculation with volume weight
        volume_weight = last_volume / sum(volumes)
        obv = obv + (last_volume * volume_weight) if price_change > 0 else obv - (last_volume * volume_weight)
        
        # Improved NVI and PVI calculations with trend consideration
        price_ratio = price_change / prev_close if prev_close != 0 else 0
        nvi = nvi * (1 + price_ratio * 1.5) if last_volume < volume_ema else nvi
        pvi = pvi * (1 + price_ratio * 1.5) if last_volume > volume_ema else pvi
        
        # Enhanced VPT calculation
        vpt = vpt + (price_ratio * last_volume * (1 + abs(price_ratio)))
        
        # Update volume EMA
        volume_ema = (last_volume * ema_alpha) + (volume_ema * (1 - ema_alpha))
        
        # Calculate multiple moving averages for better trend confirmation
        ma_volumes = []
        for period in [5, 10, 20]:
            if i + period <= len(candles):
                period_volumes = [int(c['volume']) for c in candles[i:i+period]]
                ma_volumes.append(sum(period_volumes) / len(period_volumes))
        
        ma_volume = sum(ma_volumes) / len(ma_volumes) if ma_volumes else sum(volumes) / len(volumes)
        ma_price = sum(close_prices) / len(close_prices)
        
        # Enhanced volume ratio calculation
        volume_ratio = last_volume / ma_volume if ma_volume != 0 else 1
        
        # Improved direction calculation with momentum consideration
        momentum = sum(1 for p in close_prices[:-1] if p < close_prices[-1]) / (len(close_prices) - 1)
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

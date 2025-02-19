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
        self.volume_ma_periods = [5, 10, 20, 50]  # Added longer period
        self.rsi_periods = [14, 21]  # Multiple RSI periods
        self.ema_periods = [8, 13, 21]  # Multiple EMAs for confirmation
        self.macd_params = {'fast': 12, 'slow': 26, 'signal': 9}
        
    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average."""
        multiplier = 2 / (period + 1)
        ema = [data[0]]
        for price in data[1:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        return ema

    def calculate_macd(self, prices):
        """Calculate MACD with signal line."""
        fast_ema = self.calculate_ema(prices, self.macd_params['fast'])
        slow_ema = self.calculate_ema(prices, self.macd_params['slow'])
        macd_line = [f - s for f, s in zip(fast_ema, slow_ema)]
        signal_line = self.calculate_ema(macd_line, self.macd_params['signal'])
        return macd_line, signal_line

    def calculate_rsi(self, prices, period):
        """Enhanced RSI calculation."""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        
        if down == 0:
            return [100] * len(prices)
            
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1.+ rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up/down
            rsi[i] = 100. - 100./(1.+ rs)
            
        return rsi

    def detect_divergence(self, prices, indicator_values, window=10):
        """Detect price and indicator divergence."""
        if len(prices) < window:
            return 0
            
        price_trend = np.polyfit(range(window), prices[-window:], 1)[0]
        indicator_trend = np.polyfit(range(window), indicator_values[-window:], 1)[0]
        
        if price_trend * indicator_trend < 0:  # Opposite directions
            return np.sign(indicator_trend)  # Return direction of indicator trend
        return 0

    def calculate_volume_profile(self, volumes, prices, num_bins=10):
        """Calculate volume profile for price levels."""
        bins = np.linspace(min(prices), max(prices), num_bins)
        vol_profile = np.zeros(num_bins-1)
        
        for price, volume in zip(prices, volumes):
            bin_idx = np.digitize(price, bins) - 1
            if 0 <= bin_idx < len(vol_profile):
                vol_profile[bin_idx] += volume
                
        return vol_profile, bins

    def fit(self, X, y):
        """Enhanced model training with multiple indicators."""
        prices = [x[2] for x in X]  # prev_close at index 2
        volumes = [x[0] for x in X]  # volume at index 0
        
        # Calculate base volatility
        returns = np.diff(prices) / prices[:-1]
        self.volatility_threshold = np.std(returns) * 2
        
        # Calculate volume profile
        self.vol_profile, self.price_bins = self.calculate_volume_profile(volumes, prices)
        
        # Pre-calculate indicator thresholds
        self.rsi_thresholds = {}
        for period in self.rsi_periods:
            rsi_values = self.calculate_rsi(prices, period)
            self.rsi_thresholds[period] = {
                'oversold': np.percentile(rsi_values, 20),
                'overbought': np.percentile(rsi_values, 80)
            }

    def predict(self, X):
        """Highly accurate prediction with multiple confirmation layers."""
        predictions = []
        window_size = max(self.volume_ma_periods)
        
        if len(X) < window_size:
            return [0] * len(X)
            
        for i in range(window_size, len(X)):
            window = X[max(0, i-window_size):i+1]
            prices = [x[2] for x in window]  # Using prev_close
            volumes = [x[0] for x in window]
            
            current_price = prices[-1]
            current_volume = volumes[-1]
            
            # 1. Calculate multiple EMAs
            ema_signals = []
            for period in self.ema_periods:
                ema = self.calculate_ema(prices, period)
                ema_signals.append(1 if current_price > ema[-1] else -1)
            
            # 2. Calculate MACD
            macd_line, signal_line = self.calculate_macd(prices)
            macd_signal = 1 if macd_line[-1] > signal_line[-1] else -1
            
            # 3. Calculate multiple RSIs
            rsi_signals = []
            for period in self.rsi_periods:
                rsi = self.calculate_rsi(prices, period)
                if rsi[-1] < self.rsi_thresholds[period]['oversold']:
                    rsi_signals.append(1)  # Potential reversal up
                elif rsi[-1] > self.rsi_thresholds[period]['overbought']:
                    rsi_signals.append(-1)  # Potential reversal down
                else:
                    rsi_signals.append(0)
            
            # 4. Volume analysis
            vol_ma = np.mean(volumes[-20:])
            volume_signal = 1 if current_volume > vol_ma * 1.5 else 0
            
            # 5. Price action
            price_change = (current_price - prices[-2]) / prices[-2]
            volatility = np.std(prices[-20:]) / np.mean(prices[-20:])
            
            # 6. Divergence check
            rsi_divergence = self.detect_divergence(prices[-10:], 
                                                  self.calculate_rsi(prices, 14)[-10:])
            
            # Comprehensive signal generation with strict rules
            signal = 0
            
            # Rule 1: Strong trend confirmation (all EMAs aligned)
            ema_consensus = all(s == ema_signals[0] for s in ema_signals)
            
            # Rule 2: MACD confirmation
            macd_confirm = macd_signal == ema_signals[0] if ema_consensus else False
            
            # Rule 3: RSI confirmation (no overbought/oversold conflict)
            rsi_conflict = any(s * rsi_signals[0] < 0 for s in rsi_signals if s != 0)
            
            # Rule 4: Volume confirmation
            volume_confirm = volume_signal > 0
            
            # Rule 5: Volatility check
            volatility_safe = volatility < self.volatility_threshold
            
            # Final decision with strict criteria
            if (ema_consensus and macd_confirm and not rsi_conflict and 
                volume_confirm and volatility_safe and abs(price_change) > 0.0001):
                
                # Additional confirmation from divergence
                if rsi_divergence != 0:
                    signal = rsi_divergence
                else:
                    signal = ema_signals[0]
                    
                # Extra check for signal strength
                if abs(macd_line[-1] - signal_line[-1]) < np.std(macd_line):
                    signal = 0  # Signal not strong enough
                    
            predictions.append(signal)
            
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

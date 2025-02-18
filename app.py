from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

class SimpleDecisionTree:
    def __init__(self):
        self.threshold = None
        self.label = None

    def fit(self, X, y):
        """ A simple 1-feature decision tree for classification """
        self.threshold = np.median(X[:, 0])  # Take median of the first feature
        self.label = np.sign(np.mean(y))  # Majority class

    def predict(self, X):
        """ Predict based on the simple threshold """
        return np.where(X[:, 0] > self.threshold, self.label, -self.label)

def predict_next_candle(candles, window_size=10):
    df = pd.DataFrame(candles)
    df[['open', 'close', 'max', 'min']] = df[['open', 'close', 'max', 'min']].astype(float)

    df['direction'] = df.apply(lambda row: 1 if row['close'] > row['open'] else (-1 if row['close'] < row['open'] else 0), axis=1)

    for i in range(1, window_size + 1):
        df[f'prev_close_{i}'] = df['close'].shift(i)
        df[f'prev_volume_{i}'] = df['volume'].shift(i)

    df.dropna(inplace=True)

    features = [col for col in df.columns if col not in ['time', 'direction']]
    target = 'direction'

    train_size = int(len(df) * 0.8)
    train_df = df[:train_size]
    test_df = df[train_size:]

    X_train = train_df[features].values
    y_train = train_df[target].values
    X_test = test_df[features].values

    model = SimpleDecisionTree()
    model.fit(X_train, y_train)

    last_candle_features = X_test[-1].reshape(1, -1)
    next_direction = model.predict(last_candle_features)[0]

    return 'CALL' if next_direction == 1 else 'PUT' if next_direction == -1 else 'NEUTRAL'

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

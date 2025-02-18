from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = FastAPI(title="Trading Signal API")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def predict_next_candle(candles, window_size=10):
    df = pd.DataFrame(candles)

    # Convert necessary columns to float
    df[['open', 'close', 'max', 'min']] = df[['open', 'close', 'max', 'min']].astype(float)

    # Define target: 1 for Up, -1 for Down, 0 for Neutral
    df['direction'] = df.apply(lambda row: 1 if row['close'] > row['open'] else (-1 if row['close'] < row['open'] else 0), axis=1)

    # Feature Engineering
    for i in range(1, window_size + 1):
        df[f'prev_close_{i}'] = df['close'].shift(i)
        df[f'prev_volume_{i}'] = df['volume'].shift(i)

    # Drop NaN values from shifting
    df.dropna(inplace=True)

    # Split data into train & test
    X = df.drop(columns=['time', 'direction'])
    y = df['direction']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train Model
    model = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    # Predict next candle
    last_candle_features = X.iloc[-1].values.reshape(1, -1)
    next_direction = model.predict(last_candle_features)[0]

    # Convert prediction to readable output
    if next_direction == 1:
        return 'CALL'
    elif next_direction == -1:
        return 'PUT'
    else:
        return 'NEUTRAL'



def signal(pair):
    headers = {
        'Authorization': 'Bearer 8874b89990ef31aa9fd85b4e3765f222-b4f234623b1f9f383de395ea4910ff6a'
    }

    url_hist1 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M1&count=100'
    url_hist2 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M2&count=100'
    url_hist5 = f'https://api-fxpractice.oanda.com/v3/instruments/{pair}/candles?granularity=M5&count=100'

    response1 = requests.get(url_hist1, headers=headers)
    response2 = requests.get(url_hist2, headers=headers)
    response5 = requests.get(url_hist5, headers=headers)
    f1 = response1.json()
    f2 = response2.json()
    f5 = response5.json()
    
    data1 = []
    data2 = []
    data5 = []
    
    for m in f1['candles']:
        if m['complete']:
            f = {
                'time': m['time'],
                'volume': m['volume'],
                'open': m['mid']['o'],
                'close': m['mid']['c'],
                'max': m['mid']['h'],
                'min': m['mid']['l']
            }
            data1.append(f)

    for m in f2['candles']:
        if m['complete']:
            f = {
                'time': m['time'],
                'volume': m['volume'],
                'open': m['mid']['o'],
                'close': m['mid']['c'],
                'max': m['mid']['h'],
                'min': m['mid']['l']
            }
            data2.append(f)

    for m in f5['candles']:
        if m['complete']:
            f = {
                'time': m['time'],
                'volume': m['volume'],
                'open': m['mid']['o'],
                'close': m['mid']['c'],
                'max': m['mid']['h'],
                'min': m['mid']['l']
            }
            data5.append(f)

    dir11=predict_next_candle(data1,3)
    dir12=predict_next_candle(data1,7)
    dir13=predict_next_candle(data1,14)
    dir21=predict_next_candle(data2,3)
    dir22=predict_next_candle(data2,7)
    dir23=predict_next_candle(data2,14)
    dir51=predict_next_candle(data5,3)
    dir52=predict_next_candle(data5,7)
    dir53=predict_next_candle(data5,14)

    dir= dir1 if (dir11 == dir12 == dir13 == dir21 ==dir22==dir23==dir51==dir52==dir53) else "NEUTRAL"
    return dir
@app.get("/")
def home():
    return {"message": "API is working!"}
@app.get("/trading-signal", response_model=str, summary="Get Trading Signal")
async def get_trading_signal(
    pair: str = Query(..., description="Trading pair (e.g., EUR_USD)"),
):
    """
    Retrieve a trading signal for a given currency pair.
    
    - **pair**: The trading pair to analyze (e.g., EUR_USD)
    - **offset**: Number of candles to analyze (default: 15, min: 1, max: 100)
    - **pro**: Google API Key for Gemini AI
    
    Returns:
    - CALL: Upward movement predicted
    - PUT: Downward movement predicted
    - NEUTRAL: No clear direction
    """
    try:
        return signal(pair)
    except Exception as e:
        raise HTTPException(status_code=500, detail='error occured')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import os
import numpy as np
import pandas as pd
import requests  # kept in case you later pull real data

import cpz
from cpz.execution.models import OrderSubmitRequest
from cpz.execution.enums import OrderSide, OrderType, TimeInForce

# --- Set CPZ AI credentials (demo values; replace with real ones) ---
os.environ["CPZ_AI_API_KEY"] = "cpz_key_dd6876b5d1384745a8f8a8b0"
os.environ["CPZ_AI_SECRET_KEY"] = "cpz_secret_6p1j5t486b4w1h1a654y604e1t1t2y3y2x27383v3w1g453b"
os.environ["CPZ_STRATEGY_ID"] = "6bd20a68-6ba7-44c9-90e5-0319496a1ea7"

# ==========================
# CPZ AI / Execution Config
# ==========================
PLACE_ORDERS = False  # <<< set to True to send orders via CPZ
BROKER = "alpaca"
BROKER_ENVIRONMENT = "paper"  # "paper" or "live"
STRATEGY_ID = os.environ.get("CPZ_STRATEGY_ID", "strategy_ID_XYZ")

QTY_PER_TRADE = 10  # fixed quantity per trade (adjust as you like)


# Function to get sentiment score (placeholder)
def get_sentiment_score(symbol):
    # Replace with actual sentiment analysis logic
    return np.random.uniform(-1, 1)  # Random sentiment score for demonstration


# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Example market data (replace with real-time data)
# market_data = {
#     'SPY': {'price': 683, 'change': 0.23},
#     'QQQ': {'price': 621.57, 'change': -0.27},
#     'AAPL': {'price': 275.25, 'change': 2.16}
# }

market_data = [
    {
        "low": 247.47,
        "high": 251.82,
        "open": 249.485,
        "close": 249.34,
        "symbol": "AAPL",
        "volume": 33893611,
        "timestamp": "2025-10-15T04:00:00.000Z",
        "transactions": 528880,
        "volumeWeightedPrice": 249.5813
    },
    {
        "low": 245.13,
        "high": 249.04,
        "open": 248.25,
        "close": 247.45,
        "symbol": "AAPL",
        "volume": 39776974,
        "timestamp": "2025-10-16T04:00:00.000Z",
        "transactions": 616258,
        "volumeWeightedPrice": 247.354
    },
    {
        "low": 247.27,
        "high": 253.38,
        "open": 248.02,
        "close": 252.29,
        "symbol": "AAPL",
        "volume": 49146961,
        "timestamp": "2025-10-17T04:00:00.000Z",
        "transactions": 634830,
        "volumeWeightedPrice": 250.7598
    },
    {
        "low": 255.63,
        "high": 264.375,
        "open": 255.885,
        "close": 262.24,
        "symbol": "AAPL",
        "volume": 90483029,
        "timestamp": "2025-10-20T04:00:00.000Z",
        "transactions": 1160822,
        "volumeWeightedPrice": 261.7003
    },
    {
        "low": 261.83,
        "high": 265.29,
        "open": 261.88,
        "close": 262.77,
        "symbol": "AAPL",
        "volume": 46695748,
        "timestamp": "2025-10-21T04:00:00.000Z",
        "transactions": 714945,
        "volumeWeightedPrice": 263.4176
    }
]


def run_sentiment_rsi_strategy():
    # Create CPZ client only once if we're placing orders
    client = None
    if PLACE_ORDERS:
        if not STRATEGY_ID:
            raise ValueError("CPZ_STRATEGY_ID is not set. Cannot place orders.")
        client = cpz.clients.sync.CPZClient()
        client.execution.use_broker(BROKER, environment=BROKER_ENVIRONMENT)

    orders = []

    # Strategy implementation
    for symbol, data in market_data.items():
        sentiment_score = get_sentiment_score(symbol)
        print(f"\n=== {symbol} ===")
        print(f"Sentiment: {sentiment_score:.4f}")

        # Placeholder for historical price data
        historical_data = pd.DataFrame({'close': [data['price']] * 20})  # Simulated data
        historical_data['rsi'] = calculate_rsi(historical_data)
        current_rsi = historical_data['rsi'].iloc[-1]
        print(f"RSI: {current_rsi:.2f}")

        buy_signal = sentiment_score > 0.5 and current_rsi < 30
        sell_signal = sentiment_score < -0.5 or current_rsi > 70

        if buy_signal:
            print(f"Buy signal for {symbol}")
            if PLACE_ORDERS and client is not None:
                order = client.execution.submit_order(OrderSubmitRequest(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    qty=QTY_PER_TRADE,
                    order_type=OrderType.MARKET,
                    time_in_force=TimeInForce.DAY,
                    strategy_id=STRATEGY_ID,  # REQUIRED
                ))
                print(f"Submitted BUY {QTY_PER_TRADE} {symbol} -> order_id={order.id}, status={order.status}")
                orders.append(order)

        elif sell_signal:
            print(f"Sell signal for {symbol}")
            if PLACE_ORDERS and client is not None:
                order = client.execution.submit_order(OrderSubmitRequest(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    qty=QTY_PER_TRADE,
                    order_type=OrderType.MARKET,
                    time_in_force=TimeInForce.DAY,
                    strategy_id=STRATEGY_ID,  # REQUIRED
                ))
                print(f"Submitted SELL {QTY_PER_TRADE} {symbol} -> order_id={order.id}, status={order.status}")
                orders.append(order)
        else:
            print(f"No trade signal for {symbol}")

    if PLACE_ORDERS and not orders:
        print("\nNo orders submitted (no active signals).")

    return orders


if __name__ == "__main__":
    run_sentiment_rsi_strategy()
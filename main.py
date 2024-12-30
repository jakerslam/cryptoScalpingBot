import os
import time
from datetime import datetime
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException, BinanceOrderException
import json

# Open and read the JSON file
with open('api_key.json', 'r') as file:
    data = json.load(file)
    print(data)
apiKey = data["key"]
apiSecret = data["secret"]
# Load environment variables
API_KEY = os.getenv('BINANCE_US_API_KEY', apiKey)
API_SECRET = os.getenv('BINANCE_US_API_SECRET', apiSecret)

# Initialize Binance.US client
client = Client(API_KEY, API_SECRET, tld='us')

# Parameters
#BTC
# SYMBOL = 'BTCUSD'  # Trading pair
# TRADE_QUANTITY = 0.001  # Quantity to trade (adjust as needed)
# PROFIT_MARGIN = 0.001  # Profit margin as a fraction (e.g., 0.1% = 0.001)
# CHECK_INTERVAL = 10  # Time in seconds between checks

#XRP
SYMBOL = 'XRPUSDT'  # Trading pair
TRADE_QUANTITY = 1  # Quantity to trade (adjust as needed)
PROFIT_MARGIN = 0.001  # Profit margin as a fraction (e.g., 0.1% = 0.001)
CHECK_INTERVAL = 10  # Time in seconds between checks

# Logger function
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# Fetch current price
def get_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except BinanceAPIException as e:
        log_message(f"Binance API Exception while fetching price: {e}")
        return None

# Place an order
def place_order(symbol, side, quantity):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        log_message(f"Order placed: {order}")
        return order
    except BinanceOrderException as e:
        log_message(f"Binance Order Exception: {e}")
        return None
    except BinanceAPIException as e:
        log_message(f"Binance API Exception: {e}")
        return None

# Scalping strategy
def scalping_strategy():
    log_message("Starting scalping strategy...")
    # Get the current price
    current_price = get_price(SYMBOL)
    if current_price is None:
        return

    # Simulate buying and selling for profit
    log_message(f"Current price: {current_price}")

    # Place a buy order
    buy_order = place_order(SYMBOL, SIDE_BUY, TRADE_QUANTITY)
    if not buy_order:
        log_message("Failed to place buy order.")
        return

    # Wait for the price to increase for profit
    buy_price = current_price
    target_price = buy_price * (1 + PROFIT_MARGIN)
    log_message(f"Buy price: {buy_price}, Target price: {target_price}")

    while True:
        time.sleep(CHECK_INTERVAL)
        current_price = get_price(SYMBOL)
        if current_price is None:
            continue
        log_message(f"Current price: {current_price}")

        if current_price >= target_price:
            # Place a sell order
            sell_order = place_order(SYMBOL, SIDE_SELL, TRADE_QUANTITY)
            if sell_order:
                log_message(f"Successfully sold at {current_price}. Profit realized!")
            else:
                log_message("Failed to place sell order.")
            break

# Main loop
if __name__ == "__main__":
    log_message("Trading bot started.")
    while True:
        try:
            scalping_strategy()
        except Exception as e:
            log_message(f"Unexpected error: {e}")
        log_message("Waiting for the next round...")
        time.sleep(CHECK_INTERVAL)

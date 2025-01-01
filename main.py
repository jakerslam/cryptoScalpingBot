 import json
import logging
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Load API keys from a JSON file
with open('api_key.json', 'r') as file:
    apiData = json.load(file)

API_KEY = apiData["key"]
API_SECRET = apiData["secret"]

# Initialize Binance client
client = Client(API_KEY, API_SECRET, tld='US')

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", handlers=[
    logging.FileHandler("trading_bot.log"),
    logging.StreamHandler()
])

# Trading configuration
TRADING_PAIRS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
SMA_PERIOD = 14
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_QUANTITY = 0.01  # Adjust based on your balance and trading requirements

no_action_cycles = 0  # Track cycles with no action

# Cache for balances to avoid repeated attempts on insufficient funds
last_checked_balance = {}

def fetch_price_data(symbol):
    # Fetch historical price data for the given symbol.
    try:
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
        return [float(kline[4]) for kline in klines]  # Closing prices
    except BinanceAPIException as e:
        logging.error(f"API error fetching price data for {symbol}: {e}")
        return None

def calculate_sma(prices, period):

    # Calculate the Simple Moving Average (SMA).

    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def calculate_rsi(prices, period):

    # Calculate the Relative Strength Index (RSI).

    if len(prices) < period + 1:
        return None
    gains, losses = 0, 0
    for i in range(1, period + 1):
        change = prices[-i] - prices[-i - 1]
        if change > 0:
            gains += change
        else:
            losses -= change
    avg_gain = gains / period
    avg_loss = losses / period if losses > 0 else 1  # Avoid division by zero
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def check_balance(asset, quantity):
    # Check if there is sufficient balance to execute the trade.
    global last_checked_balance
    try:
        # Avoid repeated balance checks for the same asset
        if asset in last_checked_balance:
            balance_info = last_checked_balance[asset]
        else:
            account_info = client.get_account()
            balance_info = next((b for b in account_info['balances'] if b['asset'] == asset), None)
            if balance_info:
                last_checked_balance[asset] = balance_info

        if balance_info:
            free_balance = float(balance_info['free'])
            return free_balance >= quantity
        else:
            logging.warning(f"No balance information available for asset: {asset}")
            return False

    except BinanceAPIException as e:
        logging.error(f"Error checking balance for {asset}: {e}")
        return False

def place_order(symbol, side, quantity):
    # Place a buy or sell order, ensuring sufficient balance for buy operations.
    try:
        asset = symbol[:-4]  # Extract asset from trading pair (e.g., BTC from BTCUSDT)

        if side == "BUY" and not check_balance(asset, quantity):
            logging.warning(f"Insufficient balance to place BUY order for {symbol}")
            return False

        if side == "BUY":
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
        elif side == "SELL":
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            raise ValueError("Invalid order side")

        logging.info(f"Order placed: {order}")
        return True

    except BinanceAPIException as e:
        logging.error(f"Failed to place {side} order for {symbol}: {e}")
        return False

def trading_logic(symbol):
    # Execute trading logic for the given symbol.
    try:
        prices = fetch_price_data(symbol)
        if not prices:
            logging.warning(f"No price data for {symbol}")
            return False

        # Calculate indicators
        sma = calculate_sma(prices, SMA_PERIOD)
        rsi = calculate_rsi(prices, RSI_PERIOD)

        if sma is None or rsi is None:
            logging.warning(f"Not enough data for indicators on {symbol}")
            return False

        # Current price
        current_price = prices[-1]

        # Trading conditions
        if current_price > sma and rsi < RSI_OVERSOLD:
            logging.info(f"Placing a BUY order for {symbol} at {current_price}")
            return place_order(symbol, "BUY", TRADE_QUANTITY)
        elif current_price < sma and rsi > RSI_OVERBOUGHT:
            logging.info(f"Placing a SELL order for {symbol} at {current_price}")
            return place_order(symbol, "SELL", TRADE_QUANTITY)
        else:
            return False

    except Exception as e:
        logging.error(f"Error in trading logic for {symbol}: {e}")
        return False

def log_no_action(cycles):
    
    # Log the number of cycles with no action.
    
    if cycles == 1:
        logging.info("No action taken during this cycle.")
    elif cycles > 1:
        logging.info(f"No action taken for {cycles} consecutive cycles.")

if __name__ == "__main__":
    while True:
        action_taken = False  # Track whether any action was taken this cycle

        for pair in TRADING_PAIRS:
            if trading_logic(pair):
                action_taken = True

        if action_taken:
            if no_action_cycles > 0:
                log_no_action(no_action_cycles)  # Log skipped cycles
            no_action_cycles = 0  # Reset the counter after action is taken
        else:
            no_action_cycles += 1

        # Log if no action was taken during the cycle
        if no_action_cycles == 1:
            logging.info("No action taken during this cycle.")

        # Wait before next cycle
        time.sleep(10)  # Adjust delay as needed
 

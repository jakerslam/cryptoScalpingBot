from binance.client import Client

# Replace these with your Binance.US API key and secret
API_KEY = "JmetcaoGgUBWuVdrVg82YxTNKUCSWP09U0JHz1WlyntE2GIQVpxXHjQoIpfu6DSZ"
API_SECRET = "p6tTHsfLpD6Xy8IVZAwpADgSi2V5VYVDMRsOtgbPvYLZfLNskxqhoxfzqzicIc5r"

# Initialize Binance.US client
client = Client(API_KEY, API_SECRET, tld="us")  # Use 'us' as the top-level domain for Binance.US

# Test connection by fetching account info
try:
    account_info = client.get_account()
    print("Account Info:", account_info)
except Exception as e:
    print("Error connecting to Binance.US API:", e)

# Get current price of BTC/USDT
try:
    btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
    print("BTC Price:", btc_price)
except Exception as e:
    print("Error fetching BTC price:", e)


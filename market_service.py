import yfinance as yf
import pandas as pd
from datetime import datetime
import threading
import time

class MarketService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MarketService, cls).__new__(cls)
                    cls._instance.cache = {}
        return cls._instance

    def get_current_price(self, symbol):
        """Fetches real-time price for a symbol (e.g., '1120.SR')."""
        try:
            # Ticker format for Saudi format is .SR
            ticker_sym = symbol if symbol.endswith(".SR") else f"{symbol}.SR"
            
            # Check cache first (valid for 60 seconds)
            cached = self.cache.get(ticker_sym)
            if cached and (time.time() - cached['timestamp'] < 60):
                return cached['price']

            # Fetch live
            ticker = yf.Ticker(ticker_sym)
            data = ticker.history(period="1d")
            
            if data.empty:
                return None
                
            price = data['Close'].iloc[-1]
            
            # Update cache
            self.cache[ticker_sym] = {
                'price': price,
                'timestamp': time.time()
            }
            return price
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    def get_history(self, symbol, period="1mo", interval="1d"):
        """Fetches historical OHLCV data."""
        try:
            ticker_sym = symbol if symbol.endswith(".SR") else f"{symbol}.SR"
            ticker = yf.Ticker(ticker_sym)
            return ticker.history(period=period, interval=interval)
        except Exception:
            return pd.DataFrame()

    def get_market_status(self):
        """Checks if TASI is currently open (approximate)."""
        now = datetime.now()
        # Sunday to Thursday
        if now.weekday() in [4, 5]: # Fri, Sat
            return "CLOSED"
        # 10:00 to 15:20
        hour = now.hour
        minute = now.minute
        if (hour > 10 or (hour == 10 and minute >= 0)) and (hour < 15 or (hour == 15 and minute <= 20)):
            return "OPEN"
        return "CLOSED"

import datetime
from collections import deque
import time
import threading
from market_service import MarketService
from news_service import NewsService

class KnowledgeCenter:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(KnowledgeCenter, cls).__new__(cls)
                    cls._instance.market_data = {}
                    cls._instance.bot_signals = deque(maxlen=100)
                    cls._instance.investigator_logs = deque(maxlen=50)
                    # Real Services
                    cls._instance.market_service = MarketService()
                    cls._instance.news_service = NewsService()
                    
                    # TASI Tickers to track
                    cls._instance.tickers = ["1120", "2222", "2010", "7010", "4030", "1180"] # Rajhi, Aramco, SABIC, STC, Almarai, NCB
        return cls._instance

        # In a real scenario, this fetches from Yahoo Finance or Tadawul API
        # Here we simulate random movement for the scenario
        timestamp = datetime.datetime.now()
        snapshot = {"timestamp": timestamp, "prices": {}}
        
        if not self.market_data:
            # Initialize with dummy base prices if empty
            for sym in self.saudi_symbols:
                self.market_data[sym] = random.uniform(20.0, 150.0)
        
        for sym in self.saudi_symbols:
            # Random stick movement (-1% to +1%)
            change = random.uniform(-0.01, 0.01)
            self.market_data[sym] *= (1 + change)
            snapshot["prices"][sym] = self.market_data[sym]
            
        self.market_history.append(snapshot)
        return self.market_data

        self.market_status = "OPEN" # OPEN, CLOSED
        
    def update_market_data(self):
        """Fetches REAL data from MarketService."""
        new_data = {}
        print("[KC] Starting market data fetch...") 
        for ticker in self.tickers:
            try:
                price = self.market_service.get_current_price(ticker)
                print(f"[KC] Fetched {ticker}: {price}") 
                if price:
                    new_data[ticker] = price
            except Exception as e:
                print(f"[KC] Error fetching {ticker}: {e}") 
        
        if new_data:
            cleaned_data = {k: v for k, v in new_data.items() if v is not None}
            self.market_data.update(cleaned_data)
            print(f"[KC] Data Updated: {self.market_data}") 
        else:
            print("[KC] No data fetched in this cycle.") 
            
        return self.market_data

    def log_signal(self, bot_id, symbol, signal_type, price, reason):
        """Log a raw signal from a bot."""
        signal = {
            "id": len(self.bot_signals) + 1,
            "timestamp": datetime.datetime.now(),
            "bot_id": bot_id,
            "symbol": symbol,
            "type": signal_type,
            "price": price,
            "reason": reason,
            "status": "PENDING" # Pending Investigator review
        }
        self.bot_signals.append(signal)
        return signal

    def log_investigator_verdict(self, signal_id, verdict, message):
        """Log the investigator's decision."""
        # Find signal
        for sig in self.bot_signals:
            if sig['id'] == signal_id:
                # Update market data
                self.update_market_data()
                    
                # Simulate slight delay to respect API limits
                time.sleep(10) 
                sig['status'] = verdict # 'APPROVED' or 'REJECTED'
                log_entry = {
                    "timestamp": datetime.datetime.now(),
                    "signal_id": signal_id,
                    "verdict": verdict,
                    "message": message,
                    "bot_id": sig['bot_id']
                }
                self.investigator_logs.appendleft(log_entry)
                return log_entry
        return None

    def get_latest_logs(self, limit=10):
        return list(self.investigator_logs)[:limit]

    def get_bot_history(self, bot_id):
        """Returns all signals and investigator logs for a specific bot."""
        signals = [s for s in self.bot_signals if s['bot_id'] == bot_id]
        
        # Get related logs
        logs = [l for l in self.investigator_logs if l['bot_id'] == bot_id]
        
        return {
            "signals": signals,
            "logs": list(logs)
        }

    def get_market_snapshot(self):
        return self.market_data

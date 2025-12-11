import datetime
from knowledge_center import KnowledgeCenter

class ChallengeManager:
    def __init__(self):
        self.kc = KnowledgeCenter()
        self.start_date = None
        self.end_date = None
        self.bot_scores = {} # BotID -> {pnl: 0.0, trades: 0, wins: 0}
        self.is_active = False

    def start_new_challenge(self):
        """Starts a new weekly challenge (Sunday to Thursday)."""
        today = datetime.datetime.now()
        # Logic to align with Sunday start could go here
        self.start_date = today
        self.end_date = today + datetime.timedelta(days=5) # 5 Trading days
        self.is_active = True
        
        # Reset scores - Use actual bot IDs from strategies.py
        bot_ids = ["hunter", "analyst", "lightning", "sniper", "mastermind", 
                   "brave", "guardian", "wave", "striker", "jewel"]
        
        for bot_id in bot_ids:
            self.bot_scores[bot_id] = {"pnl": 0.0, "trades": 0, "wins": 0, "status": "ACTIVE"}
            
        print(f"Challenge Started: {self.start_date} to {self.end_date}")

    def update_score(self, bot_id, pnl):
        """Updates the score for a bot after a closed trade."""
        if not self.is_active or bot_id not in self.bot_scores:
            return
            
        stats = self.bot_scores[bot_id]
        if stats["status"] != "ACTIVE":
            return

        stats["pnl"] += pnl
        stats["trades"] += 1
        if pnl > 0:
            stats["wins"] += 1
            
    def disqualify_bot(self, bot_id, reason):
        """Investigator calls this to kick a bot out."""
        if bot_id in self.bot_scores:
            self.bot_scores[bot_id]["status"] = "DISQUALIFIED"
            print(f"BOT {bot_id} DISQUALIFIED: {reason}")

    def get_leaderboard(self):
        """Returns bots sorted by PnL."""
        # Convert dict to list
        ranking = []
        for bid, stats in self.bot_scores.items():
            ranking.append({
                "id": bid,
                "pnl": round(stats["pnl"], 2),
                "profit_pct": round((stats["pnl"] / 100000) * 100, 2), # Assuming 100k capital
                "balance": round(100000 + stats["pnl"], 2),
                "trades": stats["trades"],
                "wins": stats["wins"],
                "losses": stats["trades"] - stats["wins"],
                "win_rate": round((stats["wins"] / stats["trades"] * 100), 1) if stats["trades"] > 0 else 0,
                "status": stats["status"]
            })
        
        # Sort by PnL descending
        ranking.sort(key=lambda x: x["pnl"], reverse=True)
        return ranking

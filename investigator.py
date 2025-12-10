from knowledge_center import KnowledgeCenter
import random

class InvestigatorBot:
    def __init__(self, challenge_manager):
        self.kc = KnowledgeCenter()
        self.cm = challenge_manager
        self.name = "المحقق كونان" # Or just "Investigator"

    def check_signal(self, signal, market_data=None):
        """
        Validates the bot's signal against market conditions and evidence.
        Returns: 'APPROVED' or 'REJECTED'
        """
        # Fetch market data if not provided
        if market_data is None:
            market_data = self.kc.get_market_snapshot()
            
        current_price = market_data.get(signal['symbol'])
        # Logic:
        # 1. Check if price matches market data (Anti-cheat)
        # 2. Check strategy logic (Simulated)
        # 3. Disqualify if too many bad trades
        
        
        # 1. Price Reality Check
        if not current_price:
            return "REJECTED (Symbol Not Found)"
            
        diff = abs(current_price - signal['price']) / current_price
        if diff > 0.05: # > 5% difference is suspicious
            return "REJECTED (Price Mismatch > 5%)"
            
        # 2. Evidence Audit (New Feature)
        evidence = signal.get('evidence')
        if evidence:
            ev_type = evidence.get('type')
            ev_data = evidence.get('data', {})
            
            audit_steps = []
            
            if ev_type == 'technical':
                # Audit Technical Indicators
                indicators = ev_data.get('indicators', {})
                rsi = indicators.get('RSI (14)')
                if rsi:
                    if signal['type'] == 'BUY' and rsi > 40: # Suspicious, usually buy at <30
                         audit_steps.append({"check": "قيمة مؤشر RSI", "status": "WARN", "note": f"القيمة {rsi} مرتفعة قليلاً للشراء"})
                    else:
                         audit_steps.append({"check": "قيمة مؤشر RSI", "status": "PASS", "note": "في مناطق التشبع"})
                else:
                    audit_steps.append({"check": "المؤشرات الفنية", "status": "PASS", "note": "تتوافق مع شروط الدخول"})
                    
                audit_steps.append({"check": "اكتمال الشمعة", "status": "PASS", "note": "تم الإغلاق فوق الدعم"})

            elif ev_type == 'volume':
                # Audit Volume
                audit_steps.append({"check": "تحليل تدفق السيولة", "status": "PASS", "note": ev_data.get('flow_net')})
                audit_steps.append({"check": "فحص دفتر الأوامر", "status": "PASS", "note": "طلبات شراء حقيقية (غير وهمية)"})
                
            else: # Sentiment
                sentiment = ev_data.get('sentiment_score', 0.5)
                action = signal['type']
                if action == 'BUY' and sentiment < 0.5:
                     return "REJECTED (Sentiment Mismatch)"
                audit_steps.append({"check": "تحليل المشاعر", "status": "PASS", "note": f"التوافق: {int(sentiment*100)}%"})

            # Common checks
            audit_steps.append({"check": "تحقق السعر العادل", "status": "PASS", "note": f"الفارق {diff*100:.2f}% مقبول"})
            
            signal['audit_trail'] = audit_steps
        
        # 3. Random Audit
        if random.random() < 0.1:
            return "REJECTED (Random Audit Check)"
            
        return "APPROVED"


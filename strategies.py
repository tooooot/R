import random

class BaseStrategy:
    def __init__(self, bot_id, name, human_name, bio, risk, strategy_title, scientific_explanation):
        self.bot_id = bot_id
        self.name = name
        self.human_name = human_name
        self.bio = bio
        self.risk = risk
        self.strategy_title = strategy_title
        self.scientific_explanation = scientific_explanation
        
    
    def analyze(self, market_data):
        """
        Input: market_data (dict) -> {symbol: price}
        Output: Signal or None
        Signal: {
            "symbol": str, 
            "type": "BUY"|"SELL", 
            "price": float, 
            "reason": str,
            "evidence": dict  <-- NEW: Rich Evidence Data
        }
        """
        raise NotImplementedError

    def generate_evidence(self, symbol, action):
        """Generates simulated rich evidence based on the specific strategy type."""
        
        # Default: Social/News Evidence (for Sentiment, Random, Contrarian)
        evidence_type = "sentiment"
        data = {}
        
        # 1. Technical Strategy Evidence (RSI, MACD, Bollinger, Trend, Golden)
        if isinstance(self, (RSI_Bot, MACD_Bot, BollingerBot, TrendFollower, GoldenRatioBot)):
            evidence_type = "technical"
            
            # Simulate Indicator Values based on the Bot
            indicators = {}
            chart_points = []
            
            if isinstance(self, RSI_Bot):
                val = random.randint(20, 29) if action == "BUY" else random.randint(71, 85)
                indicators = {"RSI (14)": val, "Support": "Strong"}
                note = f"مؤشر RSI وصل مستويات {val} مما يدعم الانعكاس."
                
            elif isinstance(self, MACD_Bot):
                indicators = {"MACD": "Positive Cross", "Histogram": "+0.45"}
                note = "تقاطع إيجابي لخطوط الماكد مع تزايد الزخم."
                
            elif isinstance(self, BollingerBot):
                indicators = {"Band Width": "Squeeze", "Price": "Lower Band"}
                note = "السعر يلامس الحد السفلي للبولنجر مع انحراف معياري منخفض."
                
            else: # Trend / Golden
                indicators = {"EMA 50": "Above", "Trend": "Bullish"}
                note = "السعر يتداول بثبات فوق المتوسطات المتحركة الرئيسية."

            # Simulate simple chart data (last 10 candles)
            start_price = 100.0
            for _ in range(10):
                change = random.uniform(-1, 1)
                start_price += change
                chart_points.append(round(start_price, 2))
                
            data = {
                "indicators": indicators,
                "chart_data": chart_points,
                "technical_note": note
            }

        # 2. Volume/Scalping Evidence
        elif isinstance(self, (VolumeBot, ScalperBot)):
            evidence_type = "volume"
            
            # Simulate Order Book
            bids = [random.randint(1000, 5000) for _ in range(3)]
            asks = [random.randint(200, 800) for _ in range(3)] # Lower asks implies buying pressure
            
            data = {
                "volume_surge": f"+{random.randint(200, 600)}%",
                "flow_net": "Inflow (شرائي)",
                "order_book": {"bids": bids, "asks": asks},
                "vwap": "102.50"
            }
            
        # 3. Sentiment/Fundamental (Default Logic)
        else:
            evidence_type = "sentiment"
            tweets_count = random.randint(12, 45)
            positive_sentiment = random.uniform(0.7, 0.99) if action == "BUY" else random.uniform(0.1, 0.4)
            data = {
                "social_volume": tweets_count,
                "sentiment_score": positive_sentiment,
                "news_headlines": [
                    f"تفاؤل حول نتائج {symbol} المالية.",
                    "تقرير: قطاع {symbol} يجذب الاستثمارات."
                ]
            }
            
        return {
            "type": evidence_type,
            "data": data,
            "report_text": f"تحليل {self.strategy_title}: إشارة قوية بناءً على البيانات أعلاه."
        }

class RandomBot(BaseStrategy):
    def analyze(self, market_data):
        # 10% chance to trade
        if random.random() > 0.1:
            return None
        
        symbol = random.choice(list(market_data.keys()))
        price = market_data[symbol]
        action = random.choice(["BUY", "SELL"])
        
        return {
            "symbol": symbol,
            "type": action,
            "price": price,
            "reason": "Random gut feeling",
            "evidence": self.generate_evidence(symbol, action)
        }

class TrendFollower(BaseStrategy):
    def analyze(self, market_data):
        # Checks if price is above 50 (dummy logic for trend)
        for sym, price in market_data.items():
            if price > 50 and random.random() < 0.2:
                 return {"symbol": sym, "type": "BUY", "price": price, "reason": "Price above 50 SAR breakout", "evidence": self.generate_evidence(sym, "BUY")}
        return None

class RSI_Bot(BaseStrategy):
    def analyze(self, market_data):
        # Simulates RSI logic
        sym = random.choice(list(market_data.keys()))
        price = market_data[sym]
        return {"symbol": sym, "type": "SELL", "price": price, "reason": "RSI Overbought (>70)", "evidence": self.generate_evidence(sym, "SELL")}

class MACD_Bot(BaseStrategy):
    def analyze(self, market_data):
        sym = random.choice(list(market_data.keys()))
        price = market_data[sym]
        return {"symbol": sym, "type": "BUY", "price": price, "reason": "MACD Golden Cross", "evidence": self.generate_evidence(sym, "BUY")}

class BollingerBot(BaseStrategy):
    def analyze(self, market_data):
        sym = random.choice(list(market_data.keys()))
        price = market_data[sym]
        return {"symbol": sym, "type": "BUY", "price": price, "reason": "Lower Band Touch", "evidence": self.generate_evidence(sym, "BUY")}

class VolumeBot(BaseStrategy):
    def analyze(self, market_data):
        sym = random.choice(list(market_data.keys()))
        price = market_data[sym]
        return {"symbol": sym, "type": "BUY", "price": price, "reason": "Volume Spike Detected", "evidence": self.generate_evidence(sym, "BUY")}

class SentimentBot(BaseStrategy):
    def analyze(self, market_data):
        sym = random.choice(list(market_data.keys()))
        price = market_data[sym]
        return {"symbol": sym, "type": "BUY", "price": price, "reason": "Positive Social Sentiment", "evidence": self.generate_evidence(sym, "BUY")}

class GoldenRatioBot(BaseStrategy):
    def analyze(self, market_data):
        sym = random.choice(list(market_data.keys()))
        price = market_data[sym]
        return {"symbol": sym, "type": "SELL", "price": price, "reason": "Fibonacci Retracement 61.8%", "evidence": self.generate_evidence(sym, "SELL")}

class ScalperBot(BaseStrategy):
    def analyze(self, market_data):
        # High frequency, low change
        if random.random() < 0.5:
             sym = random.choice(list(market_data.keys()))
             price = market_data[sym]
             return {"symbol": sym, "type": "BUY", "price": price, "reason": "Micro-structure arbitrage", "evidence": self.generate_evidence(sym, "BUY")}
        return None

class ContrarianBot(BaseStrategy):
    def analyze(self, market_data):
        sym = random.choice(list(market_data.keys()))
        price = market_data[sym]
        return {
            "symbol": sym,
            "type": "SELL",
            "price": price,
            "reason": "Fading the noise",
            "evidence": self.generate_evidence(sym, "SELL")
        }

# Factory to get all bots
def get_all_bots():
    return [
        # 1. رائد - Trend Following (Hunter)
        TrendFollower("hunter", "رائد", "رائد", 
                     "رائد في اقتناص الفرص القصيرة المدى. الفرصة الذهبية تأتي مرة واحدة.", 
                     "متوسط 🟠", "استراتيجية الاختراق السريع", 
                     "تعتمد على مؤشر RSI ومتوسطات الحركة لتحديد نقاط الدخول والخروج. يبحث عن إشارات اختراق قوية مع تأكيد من حجم التداول."),
                     
        # 2. وجدان - Sentiment Analysis (Analyst)
        SentimentBot("analyst", "وجدان", "وجدان", 
                    "محللة حكيمة تعتمد على البيانات. البيانات لا تكذب، الأرقام تتحدث.", 
                    "منخفض 🟢", "التحليل الثنائي المتقدم", 
                    "تجمع بين التحليل الأساسي والفني. تستخدم نظام تصنيف متقدم لتقييم قوة الإشارة."),
                    
        # 3. بيان - Scalping (Lightning)
        ScalperBot("lightning", "بيان", "بيان", 
                  "واضحة ومباشرة في التداول اللحظي. السرعة قوة، اللحظة كل شيء.", 
                  "عالي جداً 🔴", "Scalping الذكي", 
                  "تعتمد على فروقات الأسعار الصغيرة. تدخل وتخرج في ثوانٍ معدودة بسرعة فائقة."),
                  
        # 4. ذيب - RSI Sniper (Sniper)
        RSI_Bot("sniper", "ذيب", "ذيب", 
               "ذئب صياد ينتظر الفرصة المثالية. طلقة واحدة، هدف واحد.", 
               "منخفض 🟢", "القنص الدقيق", 
               "ينتظر تكوّن الأنماط المثالية. يستخدم مستويات الدعم والمقاومة الرئيسية مع RSI."),
               
        # 5. ثامر - Strategic Planning (Mastermind)
        MACD_Bot("mastermind", "ثامر", "ثامر", 
                "مثمر ومنتج بالتخطيط الدقيق. التخطيط المحكم أساس النجاح.", 
                "متوسط 🟠", "التخطيط الاستراتيجي", 
                "يعتمد على نماذج رياضية متقدمة. يحلل الارتباطات ويبني محفظة متوازنة باستخدام MACD."),
                
        # 6. جسور - High Risk (Brave)
        RandomBot("brave", "جسور", "جسور", 
                 "جسور ومخاطر محسوب. لا مخاطرة لا مكاسب.", 
                 "عالي جداً 🔴", "المخاطرة المحسوبة", 
                 "يستهدف الأسهم المتقلبة والفرص عالية العائد. يدير المخاطر بصرامة رغم جرأته."),
                 
        # 7. رزين - Conservative Guardian
        BollingerBot("guardian", "رزين", "رزين", 
                    "رزين ومتزن. الحفاظ على رأس المال أولوية.", 
                    "منخفض 🟢", "الحماية الحكيمة", 
                    "يركز على الحفاظ على رأس المال أولاً. يستخدم Bollinger Bands مع Stop Loss ضيق."),
                    
        # 8. صامل - Trend Rider (Wave)
        TrendFollower("wave", "صامل", "صامل", 
                     "صامل وصبور. مع التيار أنجح.", 
                     "متوسط 🟠", "ركوب الأمواج", 
                     "يتبع الاتجاهات القوية. يدخل بعد تأكد الاتجاه ويخرج عند الانعكاس."),
                     
        # 9. حازم - Disciplined Volume
        VolumeBot("striker", "حازم", "حازم", 
                 "حازم وقوي في قراراته. الحزم في القرار قوة.", 
                 "متوسط 🟠", "الحزم والانضباط", 
                 "يعتمد على الانضباط الصارم. قواعد دخول وخروج محددة بدقة بناءً على حجم التداول."),
                 
        # 10. جوهرة - Selective Quality (Jewel)
        GoldenRatioBot("jewel", "جوهرة", "جوهرة", 
                      "ثمينة ونادرة في اختياراتها. الجودة أهم من الكمية.", 
                      "منخفض 🟢", "انتقاء الجواهر", 
                      "تبحث عن الفرص النادرة عالية الجودة. معايير صارمة  جداً للدخول باستخدام نسب فيبوناتشي الذهبية.")
    ]

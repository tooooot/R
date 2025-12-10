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
        RandomBot("Bot-1", "المغامر", "جسور 👨🏻", 
                 "لا أؤمن بالتحليل، أؤمن بالفوضى. السوق كازينو وأنا الرابح دائماً.", 
                 "عالي جداً 🔴", "نظرية الفوضى (Chaos Theory)", "تعتمد الاستراتيجية على مبدأ الحركة البراونية العشوائية للأسعار، حيث يفترض أن الأسواق لا تتبع نمطاً محدداً ويمكن تحقيق عوائد شاذة عبر الدخول العشوائي مع إدارة مخاطر صارمة."),
                 
        TrendFollower("Bot-2", "صياد الترند", "رائد 👨🏻", 
                     "الترند صديقي حتى ينحني. أنا لا أعاكس التيار أبداً.", 
                     "متوسط 🟠", "تتبع الاتجاه (Trend Following)", "تقوم على ملاحقة الزخم (Momentum) باستخدام المتوسطات المتحركة الأسية (EMA 50/200). يتم الشراء عند تقاطع المتوسطات للصعود، والبيع عند كسر الاتجاه."),
                     
        RSI_Bot("Bot-3", "قناص RSI", "رزين 👨🏻", 
               "الصبر مفتاح الثروة. قد أنتظر أياماً لاقتناص اللحظة المثالية.", 
               "منخفض 🟢", "الارتداد من التشبع (Mean Reversion)", "تستخدم مؤشر القوة النسبية (RSI 14) لتحديد مناطق ذروة البيع (<30) للشراء، وذروة الشراء (>70) للبيع، بناءً على فرضية أن السعر سيعود لمتوسطه الحسابي."),
               
        MACD_Bot("Bot-4", "خبير MACD", "بيان 👩🏻", 
                "الرياضيات لا تكذب. تقاطعات المتوسطات تخبرني بالمستقبل.", 
                "متوسط 🟠", "التقاطع والزخم (MACD Crossover)", "تعتمد على تقاطع خط الإشارة مع خط الماكد (12,26,9) لتوليد إشارات دخول مبكرة وتأكيد قوة الاتجاه الحالي وقياس الزخم."),
                
        BollingerBot("Bot-5", "سيد البولنجر", "حازم 👨🏻", 
                    "أحترم الحدود. عندما يبتعد السعر كثيراً، يجب أن يعود.", 
                    "منخفض 🟢", "نطاقات التقلب (Volatility Squeeze)", "تستغل الانحراف المعياري للسعر (Standard Deviation 2). عندما يلامس السعر النطاق السفلي يعتبر رخيصاً إحصائياً، والعكس عند النطاق العلوي."),
                    
        VolumeBot("Bot-6", "محلل السيولة", "ثامر 👨🏻", 
                 "اتبع المال. السعر قد يكذب، لكن السيولة لا تكذب أبداً.", 
                 "متوسط 🟠", "تحليل التدفقات النقدية (VSA)", "Volume Spread Analysis يركز على العلاقة بين حجم التداول ومدى حركة السعر لكشف تحركات كبار المستثمرين (Smart Money) قبل أن تظهر في السعر."),
                 
        SentimentBot("Bot-7", "قارئ المشاعر", "وجدان 👩🏻", 
                    "الأسواق يحركها الخوف والجشع. أنا أسمع نبض الشارع.", 
                    "عالي 🔴", "تحليل الشعور (Sentiment Analysis)", "استخدام معالجة اللغات الطبيعية (NLP) لقياس نغمة الأخبار والتغريدات. يتم الشراء عند التشاؤم المفرط (خوف) والبيع عند التفاؤل المفرط (طمع)."),
                    
        GoldenRatioBot("Bot-8", "الذهبي", "لجين 👩🏻", 
                      "الطبيعة تتبع النسبة الذهبية، والأسهم كذلك.", 
                      "متوسط 🟠", "تصحيحات فيبوناتشي (Fibonacci)", "تعتمد على النسب الرياضية المقدسة (0.618) لتحديد مستويات الدعم والمقاومة النفسية التي يميل السعر للارتداد منها خلال التصحيحات."),
                      
        ScalperBot("Bot-9", "الخاطف (Scalper)", "ذيب 👨🏻", 
                  "السرعة هي الحياة. لا أحتفظ بالأسهم، أنا أخطف الأرباح.", 
                  "عالي جداً 🔴", "المضاربة اللحظية (High Frequency)", "استغلال فروقات سعرية طفيفة جداً في أجزاء من الثانية (Micro-trends). تعتمد على السرعة الفائقة وكثرة الصفقات لتحقيق مرابح تراكمية."),
                  
        ContrarianBot("Bot-10", "المعاكس", "صامل 👨🏻", 
                     "عندما يهرب الجميع، أثبت أنا. أشتري الانهيارات.", 
                     "عالي 🔴", "الاستثمار المضاد (Contrarian Investing)", "مخالفة سلوك القطيع. الشراء عندما يصل مؤشر الخوف لأقصاه، بناءً على مقولة روتشيلد: 'اشترِ عندما تسيل الدماء في الشوارع'.")
    ]

"""
محلل المشاعر للأخبار باستخدام AraBERT
يستخدم نموذج BERT المدرب على النصوص العربية لتحليل المشاعر
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """محلل المشاعر للأخبار العربية"""
    
    def __init__(self):
        self.sentiment_pipeline = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """تحميل نموذج AraBERT"""
        try:
            from transformers import pipeline
            
            # تحميل النموذج العربي
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment"
            )
            self.model_loaded = True
            logger.info("✅ تم تحميل نموذج AraBERT بنجاح")
            
        except Exception as e:
            logger.warning(f"⚠️ فشل تحميل AraBERT: {e}. سيتم استخدام التحليل الأساسي.")
            self.model_loaded = False
    
    def analyze_text(self, text: str) -> Tuple[str, float]:
        """
        تحليل نص وإرجاع المشاعر ودرجة الثقة
        
        Returns:
            tuple: (sentiment, confidence)
            sentiment: 'positive', 'negative', 'neutral'
            confidence: 0.0 to 1.0
        """
        if not text or len(text.strip()) < 5:
            return 'neutral', 0.5
        
        # إذا كان النموذج محملاً، استخدمه
        if self.model_loaded and self.sentiment_pipeline:
            try:
                result = self.sentiment_pipeline(text[:512])[0]  # حد أقصى 512 حرف
                label = result['label'].lower()
                score = result['score']
                
                # تحويل التسميات إلى نظام موحد
                if 'pos' in label or 'إيجاب' in label:
                    return 'positive', score
                elif 'neg' in label or 'سلب' in label:
                    return 'negative', score
                else:
                    return 'neutral', score
                    
            except Exception as e:
                logger.error(f"خطأ في التحليل: {e}")
                return self._basic_sentiment_analysis(text)
        
        # التحليل الأساسي كخطة بديلة
        return self._basic_sentiment_analysis(text)
    
    def _basic_sentiment_analysis(self, text: str) -> Tuple[str, float]:
        """تحليل بسيط بناءً على كلمات مفتاحية"""
        text_lower = text.lower()
        
        positive_words = [
            'ارتفاع', 'نمو', 'ربح', 'أرباح', 'مكاسب', 'إيجابي', 'تحسن',
            'صعود', 'قوي', 'نجاح', 'تقدم', 'ازدهار', 'طفرة', 'قياسي'
        ]
        
        negative_words = [
            'انخفاض', 'هبوط', 'خسارة', 'خسائر', 'تراجع', 'سلبي', 'ضعف',
            'انهيار', 'تدهور', 'ركود', 'أزمة', 'مخاطر', 'قلق', 'تحذير'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            confidence = min(0.6 + (positive_count * 0.1), 0.95)
            return 'positive', confidence
        elif negative_count > positive_count:
            confidence = min(0.6 + (negative_count * 0.1), 0.95)
            return 'negative', confidence
        else:
            return 'neutral', 0.5
    
    def analyze_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """
        تحليل مجموعة من الأخبار
        
        Args:
            news_list: قائمة dictionary تحتوي على 'title' و 'text'
            
        Returns:
            نفس القائمة مع إضافة 'sentiment' و 'confidence'
        """
        analyzed = []
        
        for news in news_list:
            # دمج العنوان والنص للتحليل
            full_text = f"{news.get('title', '')} {news.get('text', '')}"
            sentiment, confidence = self.analyze_text(full_text)
            
            analyzed_news = news.copy()
            analyzed_news['sentiment'] = sentiment
            analyzed_news['confidence'] = confidence
            analyzed.append(analyzed_news)
        
        return analyzed
    
    def get_stock_recommendation(self, stock_news: List[Dict]) -> Dict:
        """
        إنشاء توصية لسهم بناءً على تحليل الأخبار
        
        Args:
            stock_news: قائمة الأخبار المتعلقة بالسهم (مع sentiment و confidence)
            
        Returns:
            dict: {
                'recommendation': str,  # شراء قوي، شراء، محايد، بيع، بيع قوي
                'confidence': float,
                'positive_count': int,
                'negative_count': int,
                'neutral_count': int
            }
        """
        if not stock_news:
            return {
                'recommendation': 'لا توجد بيانات كافية',
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        # حساب عدد كل نوع
        positive_count = sum(1 for n in stock_news if n.get('sentiment') == 'positive')
        negative_count = sum(1 for n in stock_news if n.get('sentiment') == 'negative')
        neutral_count = sum(1 for n in stock_news if n.get('sentiment') == 'neutral')
        
        total = len(stock_news)
        positive_ratio = positive_count / total
        negative_ratio = negative_count / total
        
        # حساب متوسط الثقة
        avg_confidence = sum(n.get('confidence', 0.5) for n in stock_news) / total
        
        # تحديد التوصية
        if positive_ratio >= 0.7 and positive_count >= 3:
            recommendation = 'شراء قوي 🟢'
        elif positive_ratio >= 0.5 and positive_count >= 2:
            recommendation = 'شراء 🟢'
        elif negative_ratio >= 0.7 and negative_count >= 3:
            recommendation = 'بيع قوي 🔴'
        elif negative_ratio >= 0.5 and negative_count >= 2:
            recommendation = 'بيع 🔴'
        else:
            recommendation = 'محايد ⚪'
        
        return {
            'recommendation': recommendation,
            'confidence': round(avg_confidence * 100, 1),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_count': total
        }


# نسخة singleton
_analyzer_instance = None

def get_analyzer() -> NewsAnalyzer:
    """الحصول على instance واحد من المحلل"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = NewsAnalyzer()
    return _analyzer_instance

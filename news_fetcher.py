"""
نظام جلب الأخبار من مصادر متعددة
يدعم التكامل مع مصادر عربية وعالمية
"""

from typing import List, Dict
from datetime import datetime, timedelta
import logging
import json
import os

logger = logging.getLogger(__name__)


class NewsFetcher:
    """جالب الأخبار من مصادر متعددة"""
    
    def __init__(self, cache_duration_minutes: int = 30):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache_file = "news_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """تحميل الكاش من الملف"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    # تحويل timestamps من string إلى datetime
                    if 'timestamp' in cache:
                        cache['timestamp'] = datetime.fromisoformat(cache['timestamp'])
                    return cache
        except Exception as e:
            logger.error(f"خطأ في تحميل الكاش: {e}")
        
        return {'timestamp': None, 'news': {}}
    
    def _save_cache(self):
        """حفظ الكاش إلى الملف"""
        try:
            cache_copy = self.cache.copy()
            if 'timestamp' in cache_copy and cache_copy['timestamp']:
                cache_copy['timestamp'] = cache_copy['timestamp'].isoformat()
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_copy, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطأ في حفظ الكاش: {e}")
    
    def _is_cache_valid(self) -> bool:
        """التحقق من صلاحية الكاش"""
        if not self.cache.get('timestamp'):
            return False
        
        age = datetime.now() - self.cache['timestamp']
        return age < self.cache_duration
    
    def fetch_all_news(self) -> Dict[str, List[Dict]]:
        """
        جلب الأخبار من جميع المصادر
        
        Returns:
            dict: {
                'argaam': [...],
                'mubasher': [...],
                'tadawul': [...],
                'general': [...]
            }
        """
        # استخدام الكاش إذا كان صالحاً
        if self._is_cache_valid():
            logger.info("📦 استخدام الأخبار من الكاش")
            return self.cache.get('news', {})
        
        logger.info("🔄 جلب أخبار جديدة...")
        
        all_news = {
            'argaam': self._fetch_argaam(),
            'mubasher': self._fetch_mubasher(),
            'tadawul': self._fetch_tadawul(),
            'general': self._fetch_general()
        }
        
        # حفظ في الكاش
        self.cache = {
            'timestamp': datetime.now(),
            'news': all_news
        }
        self._save_cache()
        
        return all_news
    
    def _fetch_argaam(self) -> List[Dict]:
        """جلب أخبار من أرقام (demo data)"""
        # في الإصدار الكامل، سيتم استخدام API حقيقي
        return self._get_demo_news('أرقام')
    
    def _fetch_mubasher(self) -> List[Dict]:
        """جلب أخبار من مباشر (demo data)"""
        return self._get_demo_news('مباشر')
    
    def _fetch_tadawul(self) -> List[Dict]:
        """جلب أخبار من تداول (demo data)"""
        return self._get_demo_news('تداول')
    
    def _fetch_general(self) -> List[Dict]:
        """جلب أخبار عامة (demo data)"""
        return self._get_demo_news('عام')
    
    def _get_demo_news(self, source: str) -> List[Dict]:
        """بيانات تجريبية للأخبار"""
        demo_news = {
            'أرقام': [
                {
                    'title': 'أرامكو السعودية تعلن عن أرباح قياسية للربع الثالث',
                    'text': 'حققت أرامكو أرباحاً صافية بلغت 32.6 مليار دولار في الربع الثالث من العام الجاري',
                    'stock': '2222',
                    'stock_name': 'أرامكو',
                    'timestamp': datetime.now() - timedelta(hours=2),
                    'source': source
                },
                {
                    'title': 'مصرف الراجحي يطلق خدمات مصرفية رقمية جديدة',
                    'text': 'أعلن مصرف الراجحي عن إطلاق مجموعة من الخدمات المصرفية الرقمية المبتكرة',
                    'stock': '1120',
                    'stock_name': 'الراجحي',
                    'timestamp': datetime.now() - timedelta(hours=5),
                    'source': source
                },
                {
                    'title': 'سابك تواجه تحديات في السوق العالمية',
                    'text': 'تواجه سابك ضغوطاً بسبب انخفاض أسعار المواد البتروكيماوية في الأسواق العالمية',
                    'stock': '2010',
                    'stock_name': 'سابك',
                    'timestamp': datetime.now() - timedelta(hours=8),
                    'source': source
                }
            ],
            'مباشر': [
                {
                    'title': 'المؤشر العام يغلق على ارتفاع بنسبة 1.2%',
                    'text': 'أغلق المؤشر العام السعودي تداولات اليوم على ارتفاع بنسبة 1.2% مدفوعاً بقطاع البنوك',
                    'stock': 'TASI',
                    'stock_name': 'المؤشر العام',
                    'timestamp': datetime.now() - timedelta(hours=1),
                    'source': source
                },
                {
                    'title': 'الاتصالات السعودية STC تحقق نمواً في عدد المشتركين',
                    'text': 'أعلنت STC عن زيادة عدد مشتركي خدمات الجيل الخامس بنسبة 15% خلال الربع الأخير',
                    'stock': '7010',
                    'stock_name': 'الاتصالات',
                    'timestamp': datetime.now() - timedelta(hours=4),
                    'source': source
                }
            ],
            'تداول': [
                {
                    'title': 'ارتفاع حجم التداولات إلى 8 مليار ريال',
                    'text': 'شهدت السوق السعودية ارتفاعاً في حجم التداولات ليصل إلى 8 مليار ريال في جلسة اليوم',
                    'stock': 'TASI',
                    'stock_name': 'المؤشر العام',
                    'timestamp': datetime.now() - timedelta(minutes=30),
                    'source': source
                }
            ],
            'عام': [
                {
                    'title': 'رؤية 2030 تدفع النمو في قطاع التقنية',
                    'text': 'تشهد شركات التقنية السعودية نمواً متسارعاً بفضل دعم مبادرات رؤية 2030',
                    'stock': 'TECH',
                    'stock_name': 'قطاع التقنية',
                    'timestamp': datetime.now() - timedelta(hours=12),
                    'source': source
                }
            ]
        }
        
        return demo_news.get(source, [])
    
    def get_news_by_stock(self, stock_symbol: str) -> List[Dict]:
        """
        جلب أخبار سهم معين من جميع المصادر
        
        Args:
            stock_symbol: رمز السهم مثل '2222'
            
        Returns:
            قائمة الأخبار المتعلقة بالسهم
        """
        all_news = self.fetch_all_news()
        stock_news = []
        
        for source_news in all_news.values():
            for news in source_news:
                if news.get('stock') == stock_symbol:
                    stock_news.append(news)
        
        # ترتيب حسب الوقت (الأحدث أولاً)
        stock_news.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        
        return stock_news
    
    def get_all_stocks_summary(self) -> Dict[str, List[Dict]]:
        """
        جلب ملخص لجميع الأسهم المتوفرة
        
        Returns:
            dict: {stock_symbol: [news_list]}
        """
        all_news = self.fetch_all_news()
        stocks_summary = {}
        
        for source_news in all_news.values():
            for news in source_news:
                stock = news.get('stock')
                if stock:
                    if stock not in stocks_summary:
                        stocks_summary[stock] = []
                    stocks_summary[stock].append(news)
        
        return stocks_summary


# نسخة singleton
_fetcher_instance = None

def get_fetcher() -> NewsFetcher:
    """الحصول على instance واحد من جالب الأخبار"""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = NewsFetcher()
    return _fetcher_instance

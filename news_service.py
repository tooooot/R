import random
from datetime import datetime

class NewsService:
    def __init__(self):
        self.headlines = [
            "السوق يشتعل! المنافسة تصل ذروتها 🔥",
            "هل يقلب القناص الطاولة اليوم؟ 🎯",
            "هدوء ما قبل العاصفة في تداول.. 🌪️",
            "المستثمر الذكي يجمع بصمت.. 🤫",
            "تحركات غريبة من ريبوت المضارب.. ماذا يخطط؟ 🤔"
        ]
        
    def get_latest_news(self, leaderboard):
        """Generates a dynamic news report based on current leaderboard."""
        if not leaderboard:
            return {
                "id": random.randint(1000, 9999),
                "type": 'SUMMARY',
                "title": "في انتظار بيانات السوق...",
                "body": "جاري تحليل البيانات ورصد تحركات الريبوتات. سنوافيكم بالتقارير حال توفرها.",
                "timestamp": datetime.now().strftime("%H:%M"),
                "author": "راصد 🤖",
                "image": "/static/images/rased.png"
            }
            
        top_bot = leaderboard[0]
        
        report_type = random.choice(['URGENT', 'MORNING', 'SUMMARY'])
        
        if report_type == 'URGENT':
            title = f"عاجل: {top_bot['name']} يتصدر المشهد!"
            body = f"يا ساتر! {top_bot['name']} جالس يقدم أداء خرافي اليوم. الجميع يتساءل: هل أحد يقدر يوقفه؟ 🚀"
        elif report_type == 'MORNING':
            title = "صباح تداول: قهوة وأرباح ☕"
            body = "صباح الخير يا رفاق! السوق اليوم شكله 'رايق'. نصيحتي لكم: راقبوا تحركات القناص، شكله ناوي على نية."
        else:
            title = "ملخص السوق: من الضحك ومن بكى؟"
            body = f"انتهى التداول اليوم. {top_bot['name']} كان النجم بلا منازع. أما البقية... محتاجين شدة حيل! 📉"
            
        return {
            "id": random.randint(1000, 9999),
            "type": report_type,
            "title": title,
            "body": body,
            "timestamp": datetime.now().strftime("%H:%M"),
            "author": "راصد 🤖",
            "image": "/static/images/rased.png"
        }

news_service = NewsService()

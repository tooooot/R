"""
OneSignal Notification Service
إرسال إشعارات ذكية للمستخدمين بناءً على نشاط التداول
"""

import requests
import json
from typing import List, Dict

class OneSignalService:
    def __init__(self, app_id: str, rest_api_key: str):
        """
        تهيئة خدمة OneSignal
        
        Args:
            app_id: OneSignal App ID
            rest_api_key: OneSignal REST API Key
        """
        self.app_id = app_id
        self.rest_api_key = rest_api_key
        self.api_url = "https://onesignal.com/api/v1/notifications"
    
    def send_notification(self, 
                         title: str, 
                         message: str, 
                         user_ids: List[str] = None,
                         data: Dict = None,
                         url: str = None):
        """
        إرسال إشعار
        
        Args:
            title: عنوان الإشعار
            message: نص الإشعار
            user_ids: قائمة Player IDs (إذا كانت فارغة، يرسل للجميع)
            data: بيانات إضافية
            url: رابط عند الضغط على الإشعار
        """
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {self.rest_api_key}"
        }
        
        payload = {
            "app_id": self.app_id,
            "headings": {"en": title},
            "contents": {"en": message},
        }
        
        # إرسال لمستخدمين محددين أو للجميع
        if user_ids and len(user_ids) > 0:
            payload["include_player_ids"] = user_ids
        else:
            payload["included_segments"] = ["All"]
        
        # بيانات إضافية
        if data:
            payload["data"] = data
        
        # رابط
        if url:
            payload["url"] = url
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                print(f"✅ تم إرسال الإشعار: {title}")
                return response.json()
            else:
                print(f"❌ خطأ في إرسال الإشعار: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في الاتصال بـ OneSignal: {e}")
            return None
    
    def notify_winning_trade(self, robot_name: str, symbol: str, profit: float):
        """إشعار بصفقة رابحة"""
        title = f"🎉 صفقة رابحة!"
        message = f"{robot_name} حقق ربح {profit:.2f} ر.س من {symbol}"
        
        return self.send_notification(
            title=title,
            message=message,
            data={
                "type": "winning_trade",
                "robot": robot_name,
                "symbol": symbol,
                "profit": profit
            }
        )
    
    def notify_robot_trade(self, robot_name: str, symbol: str, trade_type: str, price: float, user_ids: List[str]):
        """إشعار بصفقة روبوت معين (للمشتركين فقط)"""
        title = f"🤖 {robot_name}"
        emoji = "🟢" if trade_type == "BUY" else "🔴"
        message = f"{emoji} {trade_type} {symbol} عند {price:.2f} ر.س"
        
        return self.send_notification(
            title=title,
            message=message,
            user_ids=user_ids,
            data={
                "type": "robot_trade",
                "robot": robot_name,
                "symbol": symbol,
                "trade_type": trade_type,
                "price": price
            }
        )
    
    def notify_challenge_winner(self, robot_name: str, profit_pct: float):
        """إعلان الفائز في التحدي"""
        title = "👑 الفائز في التحدي!"
        message = f"{robot_name} يتصدر بأرباح {profit_pct:.1f}%"
        
        return self.send_notification(
            title=title,
            message=message,
            data={
                "type": "challenge_winner",
                "robot": robot_name,
                "profit": profit_pct
            }
        )
    
    def notify_market_opportunity(self, symbol: str, signal: str):
        """إشعار بفرصة في السوق"""
        title = "💡 فرصة استثمارية"
        message = f"إشارة {signal} على {symbol}"
        
        return self.send_notification(
            title=title,
            message=message,
            data={
                "type": "market_opportunity",
                "symbol": symbol,
                "signal": signal
            }
        )


# Singleton instance
_onesignal_service = None

def get_onesignal_service(app_id: str = None, rest_api_key: str = None):
    """الحصول على instance واحد من الخدمة"""
    global _onesignal_service
    
    if _onesignal_service is None and app_id and rest_api_key:
        _onesignal_service = OneSignalService(app_id, rest_api_key)
    
    return _onesignal_service

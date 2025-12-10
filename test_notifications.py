"""
سكريبت اختبار سريع لنظام الإشعارات
يتحقق من أن جميع المكونات موجودة وتعمل
"""

import sys
import os

def test_onesignal_service():
    """اختبار استيراد خدمة OneSignal"""
    try:
        from onesignal_service import OneSignalService, get_onesignal_service
        print("✅ تم استيراد onesignal_service بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في استيراد onesignal_service: {e}")
        return False

def test_requests_library():
    """اختبار وجود مكتبة requests"""
    try:
        import requests
        print("✅ مكتبة requests موجودة")
        return True
    except ImportError:
        print("❌ مكتبة requests غير موجودة - قم بتثبيتها: pip install requests")
        return False

def test_environment_variables():
    """اختبار متغيرات البيئة"""
    app_id = os.environ.get('ONESIGNAL_APP_ID')
    api_key = os.environ.get('ONESIGNAL_REST_API_KEY')
    
    if app_id and api_key:
        print(f"✅ متغيرات OneSignal موجودة")
        print(f"   App ID: {app_id[:15]}...")
        print(f"   API Key: {api_key[:15]}...")
        return True
    else:
        print("⚠️  متغيرات OneSignal غير موجودة")
        print("   سيتطلب ذلك إعداد OneSignal في البيئة الإنتاجية")
        print("   للاختبار المحلي، أنشئ ملف .env وأضف:")
        print("   ONESIGNAL_APP_ID=your_app_id")
        print("   ONESIGNAL_REST_API_KEY=your_api_key")
        return False

def test_notification_send():
    """اختبار إرسال إشعار تجريبي (يتطلب مفاتيح صحيحة)"""
    app_id = os.environ.get('ONESIGNAL_APP_ID')
    api_key = os.environ.get('ONESIGNAL_REST_API_KEY')
    
    if not (app_id and api_key):
        print("⏭️  تخطي اختبار الإرسال - المفاتيح غير موجودة")
        return None
    
    try:
        from onesignal_service import get_onesignal_service
        service = get_onesignal_service(app_id, api_key)
        
        # إرسال إشعار اختبار (للجميع)
        result = service.send_notification(
            title="🧪 اختبار النظام",
            message="نظام الإشعارات يعمل بنجاح!",
            data={"type": "test"}
        )
        
        if result:
            print("✅ تم إرسال إشعار اختبار بنجاح")
            print(f"   Response: {result}")
            return True
        else:
            print("❌ فشل إرسال الإشعار - راجع المفاتيح أو الإعدادات")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إرسال الإشعار: {e}")
        return False

def main():
    """تشغيل جميع الاختبارات"""
    print("=" * 50)
    print("🔍 اختبار نظام الإشعارات - OneSignal")
    print("=" * 50)
    print()
    
    results = []
    
    # الاختبارات الأساسية
    print("1️⃣ اختبار المكتبات:")
    results.append(test_requests_library())
    results.append(test_onesignal_service())
    print()
    
    print("2️⃣ اختبار الإعدادات:")
    env_ok = test_environment_variables()
    results.append(env_ok)
    print()
    
    # اختبار الإرسال (اختياري)
    if env_ok:
        print("3️⃣ اختبار الإرسال:")
        send_result = test_notification_send()
        if send_result is not None:
            results.append(send_result)
        print()
    
    # النتيجة النهائية
    print("=" * 50)
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    
    print(f"📊 النتيجة: {passed} نجح | {failed} فشل | {len(results)} إجمالي")
    
    if all(results):
        print("🎉 جميع الاختبارات نجحت! النظام جاهز للاستخدام.")
        return 0
    elif any(results):
        print("⚠️  بعض الاختبارات فشلت - راجع الرسائل أعلاه.")
        return 1
    else:
        print("❌ فشلت معظم الاختبارات - راجع الإعداد.")
        return 2

if __name__ == "__main__":
    sys.exit(main())

< !--OneSignal SDK Initialization-- >
<script src="https://cdn.onesignal.com/sdks/OneSignalSDK.js" defer></script>
<script>
  window.OneSignal = window.OneSignal || [];
  OneSignal.push(function() {
    OneSignal.init({
      appId: "YOUR_APP_ID_HERE", // استبدل هذا بالـ App ID من OneSignal
      safari_web_id: "web.onesignal.auto.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      notifyButton: {
        enable: false, // نستخدم زر مخصص
      },
      allowLocalhostAsSecureOrigin: true, // للتطوير المحلي فقط
      welcomeNotification: {
        title: "مرحباً بك!",
        message: "شكراً لتفعيل الإشعارات. سنبقيك على اطلاع بآخر الصفقات."
      }
    });

    // طلب الإذن تلقائياً عند أول زيارة
    OneSignal.showNativePrompt();

    // حفظ Player ID للمستخدم (للإشعارات المخصصة)
    OneSignal.getUserId(function(userId) {
      if (userId) {
        console.log("OneSignal User ID:", userId);
        // يمكنك حفظه في localStorage أو إرساله للسيرفر
        localStorage.setItem('onesignal_user_id', userId);
      }
    });

    // معالجة الإشعارات عند استلامها
    OneSignal.on('notificationDisplay', function(event) {
      console.log('OneSignal notification displayed:', event);
    });
  });
</script>

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'تنبيه جديد 🚨';
    const options = {
        body: data.body || 'لديك إشعار جديد من المتداول الذكي',
        icon: '/static/images/icon.png',
        badge: '/static/images/icon.png',
        data: data.url || '/app'
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data)
    );
});

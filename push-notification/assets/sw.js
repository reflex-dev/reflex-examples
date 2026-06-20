"use strict";

self.addEventListener("install", function (event) {
  event.waitUntil(self.skipWaiting()); //will install the service worker
});

self.addEventListener("activate", function (event) {
  event.waitUntil(self.clients.claim()); //will activate the serviceworker
});

// Register event listener for the 'notificationclick' event.
self.addEventListener("notificationclick", function (event) {
  event.notification.close();

  if (event.notification.data.url === undefined) {
    return;
  }

  event.waitUntil(
    clients.matchAll({ type: "window" }).then((clientsArr) => {
      // If a Window tab matching the targeted URL already exists, focus that;
      const hadWindowToFocus = clientsArr.some((windowClient) =>
        windowClient.url === event.notification.data.url
          ? (windowClient.focus(), true)
          : false
      );
      // Otherwise, open a new tab to the applicable URL and focus it.
      if (!hadWindowToFocus)
        clients
          .openWindow(event.notification.data.url)
          .then((windowClient) => (windowClient ? windowClient.focus() : null));
    })
  );
});

self.addEventListener("push", function (event) {
  event.waitUntil(
    self.registration.pushManager
      .getSubscription()
      .then(function (subscription) {
        if (!event.data) {
          return;
        }

        var payload = JSON.parse(event.data.text());
        return self.registration.showNotification(payload.title, {
          body: payload.body,
          icon: payload.icon,
          data: {
            url: payload.url,
          },
          tag: payload.url + payload.body + payload.icon + payload.title,
        });
      })
  );
});

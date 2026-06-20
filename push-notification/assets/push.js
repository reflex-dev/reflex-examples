// Public base64 to Uint
function urlBase64ToUint8Array(base64String) {
  var padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  var base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");

  var rawData = window.atob(base64);
  var outputArray = new Uint8Array(rawData.length);

  for (var i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Register a Service Worker.
function registerForPushNotifications(
  registration_endpoint,
  application_server_key,
  browser_id, 
) {
  navigator.serviceWorker
    .register("sw.js")
    .then(function (registration) {
      return navigator.serviceWorker.ready.then(function (
        serviceWorkerRegistration
      ) {
        return serviceWorkerRegistration.pushManager
          .getSubscription()
          .then(function (subscription) {
            // Existing subscription found.
            if (subscription) {
              return subscription;
            }

            // Make a new subscription.
            return serviceWorkerRegistration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: urlBase64ToUint8Array(
                application_server_key
              ),
            });
          });
      });
    })
    .then(function (subscription) {
      // Send the subscription details to the server using the Fetch API.
      fetch(registration_endpoint, {
        method: "post",
        headers: {
          "Content-type": "application/json",
          "X-Reflex-Browser-Id": browser_id,
        },
        body: JSON.stringify(subscription),
      });
    });
}

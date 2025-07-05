import httpx
from webpush import WebPush, WebPushSubscription

from .models import Notification, Subscriber

wp = WebPush(private_key="./private_key.pem", public_key="./public_key.pem")


# https://developer.apple.com/documentation/usernotifications/handling-notification-responses-from-apns
UNREGISTER_CODES = {
    400,  # Bad request, unlikely to recover, require re-register
    403,  # Bad certificate, likely registered with different instance of app
    410,  # Device token no longer active
}


def push(subscriptions: list[Subscriber], notification: Notification) -> list[str]:
    """Push a notification to the given subscriptions.
    
    Args:
        subscriptions: A list of subscriptions to push to.
        notification: The notification to push.
        
    Returns:
        A list of subscription auth keys that are no longer valid.
    """
    remove_subs = []
    for sub_json in set(s.sub for s in subscriptions if s.enabled):
        sub = WebPushSubscription.model_validate_json(sub_json)
        print("    Sending to", sub.keys.auth)
        wp_payload = wp.get(
            notification.json(),
            sub,
            subscriber="test@example.com",
        )
        req = httpx.post(
            str(sub.endpoint),
            data=wp_payload.encrypted,
            headers=wp_payload.headers,
        )
        if req.status_code in UNREGISTER_CODES:
            remove_subs.append(sub.keys.auth)
        else:
            try:
                req.raise_for_status()
            except Exception as e:
                print(f"    Failed to send to {sub.keys.auth}: {e} (future attempts may succeed)")
    return remove_subs

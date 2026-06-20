import reflex as rx


class Subscriber(rx.Model, table=True):
    """Store subscription data originating from the browser."""

    # Associated with a LocalStorage value saved in each browser.
    browser_id: str

    # The Auth key returned from the browser's subscription.
    auth_key: str

    # JSON-encoded subscription data saved from `push-register` endpoint.
    sub: str

    # Whether this browser has enabled notifications in the app.
    enabled: bool = True


class Notification(rx.Base):
    """Fields recognized by our service worker to display a notification."""

    title: str | None = None
    body: str | None = None
    icon: str | None = None
    url: str | None = None
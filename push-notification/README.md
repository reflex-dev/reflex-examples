# push-notification

Send Web Push API notifications from a Reflex app!

## Setup

```
pip install -r requirements.txt
reflex db migrate  # create database of subscribers
vapid-gen          # generate keys
```

## Code Overview

### Python

* `push_notification.py` - main entry point and UI for Reflex app
* `state.py` - Reflex state for sending notifications and interacting with the database
* `models.py` - database model for storing subscription data and notification fields
* `register.py` - backend route for receiving subscription data from frontend
* `push.py` - routines for sending push notifications from the backend

### JavaScript

* `assets/sw.js` - service worker to be registered in the browser
* `assets/push.js` - script to request permission and send subscription data to backend

## Further Reading

Did you know your server can send web push notifications to your app _for free_, without subscribing to some third party push service?

**Check out the [Web Push Book](https://web-push-book.gauntface.com) for a deep dive into the Web Push API and how it works.**

* [webpush](https://pypi.org/project/webpush/) python library used by this example code
* [MDN Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API) docs
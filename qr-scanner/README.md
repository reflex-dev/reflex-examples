# qr-scanner example

This QR code scanner wraps the
[@yudiel/react-qr-scanner](https://github.com/yudielcurbelo/react-qr-scanner)
component which seems to have the least amount of issues compared to other
react-based QR scanning components.

## Chrome and Safari

Chrome and Safari browser on desktop and mobile (iPhone) will NOT prompt for
camera permissions if the server is not secure (or localhost)!

Additionally, if your component does not have `on_error` set to a valid
EventHandler, you'll get a rather obtuse error on the frontend like:

```console
TypeError: p.current is not a function. (In 'p.current(e)', 'p.current' is undefined)
```

This is actually a Camera permission issue, but the component has no way of
reporting it, because `onError` is not defined and there is no graceful
fallback.

Accessing the scanner via a TLS connection should alleviate the issue. Firefox
does not seem to exhibit this behavior.
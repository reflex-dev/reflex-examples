# chatroom

A multi-client chat room.

NOTE: this example does NOT work in prod mode with redis!

<img src="assets/screenshot.png">

## `broadcast_event`

This function iterates through all states in the app, applying the Event payload
against each state instance. The resulting change list is passed off to
`pynecone.app.EventNamespace.emit()` directly.

Either event handlers or other out-of-band callbacks can use this API to emit
Events from the server as if they originated from the client. This preserves the
simple State and Event Handler conceptual model, while allowing server-to-client
communication and state updates at will.

## `send_message`

`broadcast_event` is used in the `send_message` event handler, which broadcasts
the `state.incoming_message` event to all connected clients, with the details of
the message. This in itself doesn't trigger any network traffic, unless the
state update creates a delta.

## `nick_change`

When the user sets or changes their nick, the event handler first updates the
local state, as usual. Then it awaits, `broadcast_nicks` which collects the full
nick list from the `State` instance of each connected client by iterating over
`app.state_manager.states` values.

The same `broadcast_event` mechanism described above is then used to pass the
nick list via the `state.set_nicks` event to all connected clients.

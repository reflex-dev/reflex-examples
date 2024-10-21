"""A simple example of a keyboard event listener in Reflex."""

import dataclasses

import reflex as rx
from reflex.utils.imports import ImportVar, ParsedImportDict, merge_imports
from reflex.vars.sequence import ArrayVar


def key_event_spec(
    ev: rx.Var[str],
) -> tuple[rx.Var[str]]:
    """Takes the event object and returns the key pressed to send to the state."""
    return (ev,)


class GlobalKeyWatcher(rx.Fragment):
    """A global key watcher that triggers an event when a key is pressed."""

    # List of keys to trigger on
    keys: rx.Var[list[str]] = ArrayVar.create([])

    # The event handler that will be called
    on_key_down: rx.EventHandler[key_event_spec]

    def _get_imports(self) -> ParsedImportDict:
        """Get the imports for the component."""
        return merge_imports(
            super()._get_imports(),
            {"react": [ImportVar(tag="useEffect")]},
        )

    def _get_hooks(self) -> str | None:
        return """
            useEffect(() => {
                const handle_key = (_ev) => {
                    let key = _ev.key;
                    if (_ev.ctrlKey) key = "Ctrl+" + key;
                    if (%s.includes(key) && _ev.altKey === false && _ev.metaKey === false)
                        %s
                }
                document.addEventListener("keydown", handle_key, false);
                return () => {
                    document.removeEventListener("keydown", handle_key, false);
                }
            })
            """ % (
            self.keys,
            str(rx.Var.create(self.event_triggers["on_key_down"])) + "(key)",
        )

    def render(self):
        """Render the component."""
        return ""  # No visual element, hooks only

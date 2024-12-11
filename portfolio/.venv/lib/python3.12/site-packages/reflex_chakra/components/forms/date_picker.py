"""A date input component."""

from reflex_chakra.components.forms.input import Input
from reflex.vars import Var


class DatePicker(Input):
    """A date input component."""

    # The type of input.
    type_: Var[str] = "date"  # type: ignore
